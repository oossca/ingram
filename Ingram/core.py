import os
import gc
import psutil
from collections import defaultdict
from threading import Thread

import gevent
from loguru import logger
from gevent.pool import Pool as geventPool

from .data import Data, SnapshotPipeline
from .pocs import get_poc_dict
from .utils import color
from .utils import common
from .utils import fingerprint
from .utils import port_scan
from .utils import status_bar
from .utils import timer


@common.singleton
class Core:

    def __init__(self, config):
        self.config = config
        self.data = Data(config)
        self.snapshot_pipeline = SnapshotPipeline(config)
        self.poc_dict = get_poc_dict(self.config)

    def finish(self):
        # 检查是否所有任务完成
        all_done = self.data.done >= self.data.total
        # 检查快照任务是否完成（队列为空且任务数为0）
        snapshots_done = self.snapshot_pipeline.empty() and self.snapshot_pipeline.task_count <= 0
        return all_done and snapshots_done

    def _get_memory_usage(self):
        """获取内存使用情况"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0

    def _monitor_performance(self):
        """性能监控"""
        memory_mb = self._get_memory_usage()
        queue_size = self.snapshot_pipeline.task_count if hasattr(self.snapshot_pipeline, 'task_count') else 0
        
        if memory_mb > 500:  # 内存超过500MB时警告
            logger.warning(f"内存使用较高: {memory_mb:.1f}MB")
            
        if queue_size > 100:  # 队列积压超过100时警告
            logger.warning(f"快照队列积压: {queue_size}个任务")
            
        # 定期垃圾回收
        if self.data.done % 100 == 0:
            gc.collect()

    def report(self):
        """report the results"""
        # 输出性能统计
        memory_mb = self._get_memory_usage()
        logger.info(f"扫描完成，峰值内存使用: {memory_mb:.1f}MB")
        
        results_file = os.path.join(self.config.out_dir, self.config.vulnerable)
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                items = [l.strip().split(',') for l in f if l.strip()]

            if items:
                results = defaultdict(lambda: defaultdict(lambda: 0))
                for i in items:
                    dev, vul = i[2].split('-')[0], i[-1]
                    results[dev][vul] += 1
                results_sum = len(items)
                results_max = max([val for vul in results.values() for val in vul.values()])
                
                print('\n')
                print('-' * 19, 'REPORT', '-' * 19)
                for dev in results:
                    vuls = [(vul_name, vul_count) for vul_name, vul_count in results[dev].items()]
                    dev_sum = sum([i[1] for i in vuls])
                    print(color.red(f"{dev} {dev_sum}", 'bright'))
                    for vul_name, vul_count in vuls:
                        block_num = int(vul_count / results_max * 25)
                        print(color.green(f"{vul_name:>18} | {'▥' * block_num} {vul_count}"))
                print(color.yellow(f"{'sum: ' + str(results_sum):>46}", 'bright'), flush=True)
                print('-' * 46)
                print('\n')

    def _scan(self, target):
        """
        params:
        - target: 有两种形式, 即 ip 或 ip:port
        """
        import gevent
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        items = target.split(':')
        ip = items[0]
        ports = [items[1], ] if len(items) > 1 else self.config.ports

        # 存活检测 (是否有必要)

        # 端口扫描
        for port in ports:
            try:
                if port_scan(ip, port, self.config.timeout):
                    logger.info(f"{ip} port {port} is open")
                    # 指纹
                    if product := fingerprint(ip, port, self.config):
                        logger.info(f"{ip}:{port} is {product}")
                        verified = False
                        # poc verify & exploit
                        for poc in self.poc_dict[product]:
                            try:
                                if results := poc.verify(ip, port):
                                    verified = True
                                    # found 加 1
                                    self.data.add_found()
                                    # 将验证成功的 poc 记录到 config.vulnerable 中
                                    self.data.add_vulnerable(results[:6])
                                    # snapshot
                                    if not self.config.disable_snapshot:
                                        self.snapshot_pipeline.put((poc.exploit, results))
                            except Exception as e:
                                logger.debug(f"POC验证异常 {ip}:{port} - {e}")
                                # 继续尝试下一个POC
                                continue
                            
                            # 添加短暂休眠，防止请求过快
                            gevent.sleep(0.01)
                        
                        if not verified:
                            self.data.add_not_vulnerable([ip, str(port), product])
                else:
                    logger.debug(f"{ip} port {port} is closed")
                    
            except Exception as e:
                logger.debug(f"扫描异常 {ip}:{port} - {e}")
                # 继续下一个端口
                continue
                
            # 端口间短暂休眠
            gevent.sleep(0.001)
            
        self.data.add_done()
        self.data.record_running_state()
        
        # 性能监控
        if self.data.done % 50 == 0:
            self._monitor_performance()

    def run(self):
        logger.info(f"running at {timer.get_time_formatted()}")
        logger.info(f"config is {self.config}")

        try:
            # 状态栏
            self.status_bar_thread = Thread(target=status_bar, args=[self, ], daemon=True)
            self.status_bar_thread.start()
            # snapshot
            if not self.config.disable_snapshot:
                self.snapshot_pipeline_thread = Thread(target=self.snapshot_pipeline.process, args=[self, ], daemon=True)
                self.snapshot_pipeline_thread.start()
            # 扫描
            # 使用更稳定的gevent池处理方式
            scan_pool = geventPool(self.config.th_num)
            jobs = []
            
            # 批量提交任务
            for ip in self.data.ip_generator:
                if len(jobs) >= self.config.th_num * 2:  # 控制队列长度
                    # 等待部分任务完成
                    scan_pool.join()
                    jobs = [job for job in jobs if not job.ready()]
                
                job = scan_pool.spawn(self._scan, ip)
                jobs.append(job)
            
            # 等待所有任务完成，设置超时
            try:
                gevent.with_timeout(300, scan_pool.join)  # 5分钟超时
            except:
                logger.warning("扫描任务等待超时，强制继续")
                # 强制停止剩余任务
                scan_pool.kill()

            # self.snapshot_pipeline_thread.join()
            self.status_bar_thread.join()

            self.report()

        except KeyboardInterrupt:
            logger.warning('程序被用户中断，正在保存状态...')
            self.data.cleanup()
            self.snapshot_pipeline.stop()
            logger.info('状态已保存，程序退出')

        except Exception as e:
            logger.error(f"程序运行出错: {e}")
            self.data.cleanup()
            self.snapshot_pipeline.stop()