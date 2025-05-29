# data_storage.py - 数据存储模块
import json
import os
from datetime import datetime
import streamlit as st
from typing import List, Dict, Optional
import uuid

class DataStorage:
    """数据存储管理类"""
    
    def __init__(self):
        self.data_dir = "data"
        self.requests_file = os.path.join(self.data_dir, "requests.json")
        self.updates_file = os.path.join(self.data_dir, "updates.json")
        self.user_read_status_file = os.path.join(self.data_dir, "user_read_status.json")
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """确保数据文件存在"""
        # 创建数据目录
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 初始化请求文件
        if not os.path.exists(self.requests_file):
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        
        # 初始化更新文件
        if not os.path.exists(self.updates_file):
            with open(self.updates_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        
        # 初始化用户已读状态文件
        if not os.path.exists(self.user_read_status_file):
            with open(self.user_read_status_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
    
    def add_request(self, request_type: str, title: str, content: str, 
                   submitter: str, requirement_date: str) -> bool:
        """添加新的需求/问题"""
        try:
            requests = self.get_all_requests()
            new_request = {
                "id": str(uuid.uuid4()),
                "type": request_type,
                "title": title,
                "content": content,
                "submitter": submitter if submitter else "匿名",
                "requirement_date": requirement_date,
                "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "待处理",
                "process_time": None,
                "processor": None
            }
            requests.append(new_request)
            
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"保存失败：{str(e)}")
            return False
    
    def get_all_requests(self) -> List[Dict]:
        """获取所有需求/问题"""
        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def get_pending_requests(self) -> List[Dict]:
        """获取待处理的需求/问题"""
        requests = self.get_all_requests()
        return [r for r in requests if r['status'] == '待处理']
    
    def get_processed_requests(self) -> List[Dict]:
        """获取已处理的需求/问题"""
        requests = self.get_all_requests()
        return [r for r in requests if r['status'] == '已处理']
    
    def process_request(self, request_id: str, processor: str = "管理员") -> bool:
        """处理需求/问题"""
        try:
            requests = self.get_all_requests()
            for request in requests:
                if request['id'] == request_id:
                    request['status'] = '已处理'
                    request['process_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    request['processor'] = processor
                    break
            
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def add_update(self, title: str, content: str, publisher: str = "管理员") -> bool:
        """添加系统更新"""
        try:
            updates = self.get_all_updates()
            new_update = {
                "id": str(uuid.uuid4()),
                "title": title,
                "content": content,
                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "publisher": publisher
            }
            updates.append(new_update)
            
            with open(self.updates_file, 'w', encoding='utf-8') as f:
                json.dump(updates, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_all_updates(self) -> List[Dict]:
        """获取所有系统更新"""
        try:
            with open(self.updates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def delete_update(self, update_id: str) -> bool:
        """删除系统更新"""
        try:
            updates = self.get_all_updates()
            updates = [u for u in updates if u['id'] != update_id]
            
            with open(self.updates_file, 'w', encoding='utf-8') as f:
                json.dump(updates, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def has_unread_updates(self, username: str) -> bool:
        """检查用户是否有未读更新"""
        try:
            updates = self.get_all_updates()
            if not updates:
                return False
            
            # 获取最新更新的时间
            latest_update_time = max(update['publish_time'] for update in updates)
            
            # 获取用户已读状态
            with open(self.user_read_status_file, 'r', encoding='utf-8') as f:
                read_status = json.load(f)
            
            user_last_read = read_status.get(username, "1900-01-01 00:00:00")
            
            return latest_update_time > user_last_read
        except:
            return False
    
    def mark_updates_as_read(self, username: str) -> bool:
        """标记用户已读所有更新"""
        try:
            with open(self.user_read_status_file, 'r', encoding='utf-8') as f:
                read_status = json.load(f)
            
            read_status[username] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.user_read_status_file, 'w', encoding='utf-8') as f:
                json.dump(read_status, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_user_role(self, username: str) -> str:
        """获取用户角色（简单实现）"""
        # 这里可以根据实际需求扩展用户权限系统
        admin_users = ["cira", "管理员", "admin"]
        return "管理员" if username in admin_users else "普通用户"

# 创建全局实例
storage = DataStorage()
