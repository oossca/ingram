"""数据流"""
import hashlib
import os
import time
from queue import Queue
from threading import Lock, RLock, Thread

from loguru import logger
from gevent.pool import Pool as geventPool

from .utils import common
from .utils import timer
from .utils import net


@common.singleton
class Data:

    def __init__(self, config):
        self.config = config
        self.create_time = timer.get_time_stamp()
        self.runned_time = 0
        self.taskid = hashlib.md5((self.config.in_file + self.config.out_dir).encode('utf-8')).hexdigest()

        self.total = 0
        self.done = 0
        self.found = 0

        self.total_lock = Lock()
        self.found_lock = Lock()
        self.done_lock = Lock()
        self.vulnerable_lock = Lock()
        self.not_vulneralbe_lock = Lock()

        self.preprocess()

    def _load_state_from_disk(self):
        """加载上次运行状态"""
        # done & found & run time
        state_file = os.path.join(self.config.out_dir, f".{self.taskid}")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    if line := f.readline().strip():
                        parts = line.split(',')
                        if len(parts) >= 3:
                            _done, _found, _runned_time = parts[:3]
                            self.done = max(0, int(_done))  # 确保非负
                            self.found = max(0, int(_found))  # 确保非负
                            self.runned_time = max(0.0, float(_runned_time))  # 确保非负
                            logger.info(f"恢复状态: 已完成 {self.done} 个目标，发现 {self.found} 个漏洞")
            except (ValueError, IOError) as e:
                logger.warning(f"状态文件损坏，重新开始: {e}")
                self.done = 0
                self.found = 0
                self.runned_time = 0.0

    def _cal_total(self):
        """计算目标总数"""
        with open(self.config.in_file, 'r') as f:
            for line in f:
                if (strip_line := line.strip()) and not line.startswith('#'):
                    self.add_total(net.get_ip_seg_len(strip_line))

    def _generate_ip(self):
        skip_count = self.done
        with open(self.config.in_file, 'r') as f:
            for line in f:
                if (strip_line := line.strip()) and not line.startswith('#'):
                    line_ips = net.get_all_ip(strip_line)
                    if skip_count >= len(line_ips):
                        skip_count -= len(line_ips)
                        continue
                    else:
                        # 从当前行的剩余IP开始生成
                        for ip in line_ips[skip_count:]:
                            yield ip
                        skip_count = 0

            # 如果已经跳过了所有已处理的IP，继续生成剩余的IP
            if skip_count == 0:
                for line in f:
                    if (strip_line := line.strip()) and not line.startswith('#'):
                        for ip in net.get_all_ip(strip_line):
                            yield ip

    def preprocess(self):
        """预处理"""
        # 打开记录结果的文件
        self.vulnerable = open(os.path.join(self.config.out_dir, self.config.vulnerable), 'a')
        self.not_vulneralbe = open(os.path.join(self.config.out_dir, self.config.not_vulnerable), 'a')

        self._load_state_from_disk()

        cal_thread = Thread(target=self._cal_total)
        cal_thread.start()

        self.ip_generator = self._generate_ip()
        cal_thread.join()

    def add_total(self, item=1):
        if isinstance(item, int):
            with self.total_lock:
                self.total += item
        elif isinstance(item, list):
            with self.total_lock:
                self.total += sum(item)

    def add_found(self, item=1):
        if isinstance(item, int):
            with self.found_lock:
                self.found += item
        elif isinstance(item, list):
            with self.found_lock:
                self.found += sum(item)

    def add_done(self, item=1):
        if isinstance(item, int):
            with self.done_lock:
                self.done += item
        elif isinstance(item, list):
            with self.done_lock:
                self.done += sum(item)

    def add_vulnerable(self, item):
        with self.vulnerable_lock:
            self.vulnerable.writelines(','.join(item) + '\n')
            self.vulnerable.flush()

    def add_not_vulnerable(self, item):
        with self.not_vulneralbe_lock:
            self.not_vulneralbe.writelines(','.join(item) + '\n')
            self.not_vulneralbe.flush()

    def record_running_state(self, force=False):
        # 每隔 10 个记录一下当前运行状态，提高恢复精度
        # 或者强制保存
        if force or self.done % 10 == 0:
            with open(os.path.join(self.config.out_dir, f".{self.taskid}"), 'w') as f:
                current_runtime = self.runned_time + timer.get_time_stamp() - self.create_time
                f.write(f"{str(self.done)},{str(self.found)},{current_runtime}")

    def force_save_state(self):
        """强制保存当前状态"""
        self.record_running_state(force=True)

    def __del__(self):
        try:  # if dont use try, sys.exit() may cause error
            self.force_save_state()  # 强制保存状态
            if hasattr(self, 'vulnerable') and self.vulnerable:
                self.vulnerable.close()
            if hasattr(self, 'not_vulneralbe') and self.not_vulneralbe:
                self.not_vulneralbe.close()
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

    def cleanup(self):
        """主动清理资源"""
        self.force_save_state()
        if hasattr(self, 'vulnerable') and self.vulnerable:
            self.vulnerable.close()
        if hasattr(self, 'not_vulneralbe') and self.not_vulneralbe:
            self.not_vulneralbe.close()

    def shutdown_workers(self):
        """关闭工作线程池"""
        try:
            if hasattr(self, 'workers') and self.workers:
                self.workers.kill()
        except Exception as e:
            logger.error(f"关闭工作线程池时出错: {e}")


@common.singleton
class SnapshotPipeline:

    def __init__(self, config):
        self.config = config
        self.var_lock = RLock()
        # 限制队列大小，防止内存积压
        self.pipeline = Queue(min(config.th_num, 100))  # 限制最大队列长度
        self.workers = geventPool(min(config.th_num, 50))  # 限制最大工作线程数
        self.snapshots_dir = os.path.join(self.config.out_dir, self.config.snapshots)
        # 确保目录存在
        os.makedirs(self.snapshots_dir, exist_ok=True)
        # 如果目录不存在，done设为0
        if os.path.exists(self.snapshots_dir):
            self.done = len([f for f in os.listdir(self.snapshots_dir) if os.path.isfile(os.path.join(self.snapshots_dir, f))])
        else:
            self.done = 0
        self.task_count = 0
        self.task_count_lock = Lock()
        self.running = True
        self.processed_count = 0  # 处理计数器

    def put(self, msg):
        """放入一条消息
        params:
        - msg: (poc.exploit, results)
        """
        try:
            # 使用非阻塞方式，避免卡住
            self.pipeline.put_nowait(msg)
            with self.task_count_lock:
                self.task_count += 1
        except:
            # 队列满时，丢弃旧任务或跳过
            logger.debug("快照队列已满，跳过当前快照任务")
            pass

    def empty(self):
        try:
            return self.pipeline.empty()
        except:
            # 如果gevent队列不支持empty，返回True表示可能为空
            return True

    def get(self):
        """获取队列中的项目"""
        return self.pipeline.get()

    def get_nowait(self):
        """非阻塞获取队列中的项目"""
        try:
            return self.pipeline.get_nowait()
        except:
            raise

    def get_done(self):
        with self.var_lock:
            return self.done

    def add_done(self, num=1):
        with self.var_lock:
            self.done += num

    def _snapshot(self, exploit_func, results):
        """利用 poc 的 exploit 方法获取 results 处的资源
        params:
        - exploit_func: pocs 路径下每个 poc 的 exploit 方法
        - results: poc 的 verify 验证为真时的返回结果
        """
        if res := exploit_func(results):
            self.add_done(res)
        with self.task_count_lock:
            self.task_count -= 1

    def process(self, core):
        import gevent
        
        consecutive_empty = 0  # 连续空队列计数
        max_consecutive_empty = 50  # 最大连续空次数
        
        while self.running and not core.finish():
            try:
                # 使用gevent的队列非阻塞获取
                result = self.pipeline.get_nowait()
                exploit_func, results = result
                self.workers.spawn(self._snapshot, exploit_func, results)
                with self.task_count_lock:
                    self.processed_count += 1
                consecutive_empty = 0  # 重置计数器
            except:
                # 如果队列为空，短暂休眠
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    # 连续多次队列为空，检查是否应该退出
                    gevent.sleep(0.5)
                else:
                    gevent.sleep(0.1)
                continue
        
        # 处理剩余的队列任务
        remaining_tasks = 0
        while not self.empty():
            try:
                result = self.pipeline.get_nowait()
                if result:
                    exploit_func, results = result
                    self.workers.spawn(self._snapshot, exploit_func, results)
                    remaining_tasks += 1
            except:
                break
        
        if remaining_tasks > 0:
            logger.info(f"处理剩余快照任务: {remaining_tasks}个")
            # 等待所有任务完成，但设置超时
            try:
                gevent.with_timeout(30, self.workers.join)  # 30秒超时
            except:
                logger.warning("快照任务等待超时，强制退出")
        
        logger.info(f"快照处理完成，共处理 {self.processed_count} 个任务")
        self.workers.join()

    def stop(self):
        """停止处理"""
        self.running = False

    def shutdown(self):
        """关闭快照管道"""
        self.stop()
        try:
            if hasattr(self, 'workers') and self.workers:
                self.workers.kill()
        except Exception as e:
            logger.error(f"关闭快照管道时出错: {e}")