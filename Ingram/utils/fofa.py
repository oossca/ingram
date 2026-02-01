"""FOFA API接口模块"""
import base64
import json
import time
from urllib.parse import quote

import requests
from loguru import logger


class FofaAPI:
    """FOFA API接口封装"""
    
    def __init__(self, email, key, base_url="https://fofa.info/api/v1/search/all"):
        self.email = email
        self.key = key
        self.base_url = base_url
        self.size = 100  # 每页最大结果数
        self.max_pages = 50  # 最大页数，防止请求过多
        self.request_delay = 1  # 请求间隔（秒）
    
    def _make_request(self, query, page=1, size=None):
        """发送FOFA API请求"""
        if size is None:
            size = self.size
            
        # 构造请求参数
        params = {
            "email": self.email,
            "key": self.key,
            "qbase64": base64.b64encode(query.encode('utf-8')).decode('utf-8'),
            "page": page,
            "size": min(size, 100),  # FOFA API限制最大100
            "fields": "host,ip,port,protocol,country,header,domain,server"  # 返回字段
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error"):
                logger.error(f"FOFA API错误: {data['errmsg']}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FOFA请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"FOFA响应解析失败: {e}")
            return None
    
    def search(self, query, max_results=1000):
        """
        搜索FOFA并返回结果
        
        Args:
            query (str): FOFA搜索语法
            max_results (int): 最大返回结果数
            
        Returns:
            list: 搜索结果列表，每个元素为包含目标信息的字典
        """
        logger.info(f"开始FOFA搜索: {query}")
        results = []
        page = 1
        
        while len(results) < max_results and page <= self.max_pages:
            if page > 1:
                time.sleep(self.request_delay)  # 请求间隔
                
            data = self._make_request(query, page)
            
            if not data:
                break
                
            if data.get("size") == 0:
                logger.info("FOFA搜索无更多结果")
                break
                
            # 处理结果
            page_results = []
            for item in data.get("results", []):
                target_info = {
                    "host": item[0] if len(item) > 0 else "",
                    "ip": item[1] if len(item) > 1 else "",
                    "port": item[2] if len(item) > 2 else "",
                    "protocol": item[3] if len(item) > 3 else "",
                    "country": item[4] if len(item) > 4 else "",
                    "header": item[5] if len(item) > 5 else "",
                    "domain": item[6] if len(item) > 6 else "",
                    "server": item[7] if len(item) > 7 else ""
                }
                page_results.append(target_info)
            
            results.extend(page_results)
            logger.info(f"FOFA第{page}页获取到{len(page_results)}个结果，总计{len(results)}个")
            
            # 检查是否还有更多结果
            if len(page_results) < self.size:
                break
                
            page += 1
            
            if len(results) >= max_results:
                logger.info(f"已达到最大结果数限制: {max_results}")
                break
        
        logger.info(f"FOFA搜索完成，共获取{len(results)}个目标")
        return results
    
    def search_cameras(self, query="camera", max_results=1000):
        """
        搜索摄像头相关目标
        
        Args:
            query (str): 搜索关键词，默认为camera
            max_results (int): 最大返回结果数
            
        Returns:
            list: 摄像头目标列表
        """
        # 常见的摄像头搜索语法
        camera_queries = [
            query,
            f'title="摄像头"',
            f'body="摄像头"',
            'app="Hikvision-Web"',
            'app="Dahua-Web"',
            'app="AXIS-Web"',
            'app="Vivotek-Web"',
            'app="Foscam-Web"',
            'banner="Camera"',
            'banner="webcam"',
            'banner="DVR"'
        ]
        
        all_results = []
        for camera_query in camera_queries[:3]:  # 限制查询数量
            results = self.search(camera_query, max_results // len(camera_queries))
            all_results.extend(results)
        
        # 去重（基于host）
        seen_hosts = set()
        unique_results = []
        for item in all_results:
            host = item.get("host", "")
            if host and host not in seen_hosts:
                seen_hosts.add(host)
                unique_results.append(item)
        
        return unique_results[:max_results]
    
    def save_to_file(self, results, output_file):
        """
        将FOFA结果保存到文件
        
        Args:
            results (list): FOFA搜索结果
            output_file (str): 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# FOFA搜索结果\n")
                f.write(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# 格式: ip:port 或 host\n\n")
                
                for item in results:
                    host = item.get("host", "")
                    ip = item.get("ip", "")
                    port = item.get("port", "")
                    
                    if host:
                        f.write(f"{host}\n")
                    elif ip and port:
                        f.write(f"{ip}:{port}\n")
            
            logger.info(f"FOFA结果已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存FOFA结果失败: {e}")
            return False


def create_fofa_targets(email, key, query="camera", output_file="fofa_targets.txt", max_results=1000):
    """
    创建FOFA目标文件
    
    Args:
        email (str): FOFA邮箱
        key (str): FOFA API密钥
        query (str): 搜索查询
        output_file (str): 输出文件路径
        max_results (int): 最大结果数
        
    Returns:
        bool: 是否成功
    """
    api = FofaAPI(email, key)
    
    if query.lower() == "camera" or "摄像头" in query:
        results = api.search_cameras(query, max_results)
    else:
        results = api.search(query, max_results)
    
    if results:
        return api.save_to_file(results, output_file)
    else:
        logger.error("未获取到FOFA结果")
        return False


if __name__ == "__main__":
    # 测试代码
    email = "your_email@example.com"
    key = "your_fofa_key"
    
    api = FofaAPI(email, key)
    results = api.search_cameras(max_results=50)
    
    if results:
        api.save_to_file(results, "test_fofa.txt")