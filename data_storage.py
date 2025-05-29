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
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.read_status_file = os.path.join(self.data_dir, "read_status.json")
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
        
        # 初始化用户文件
        if not os.path.exists(self.users_file):
            default_users = [
                {
                    "username": "admin",
                    "password": "SAL!2025",
                    "role": "管理员",
                    "display_name": "管理员"
                },
                {
                    "username": "user",
                    "password": "user123",
                    "role": "普通用户", 
                    "display_name": "普通用户"
                }
            ]
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, ensure_ascii=False, indent=2)
        
        # 初始化已读状态文件
        if not os.path.exists(self.read_status_file):
            with open(self.read_status_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
    
    def authenticate_user(self, password: str) -> Dict:
        """验证用户身份"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            for user in users:
                if user['password'] == password:
                    return {
                        'authenticated': True,
                        'username': user['username'],
                        'role': user['role'],
                        'display_name': user['display_name']
                    }
            
            return {'authenticated': False}
        except:
            return {'authenticated': False}
    
    def is_admin(self, username: str) -> bool:
        """检查用户是否为管理员"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            for user in users:
                if user['username'] == username:
                    return user['role'] == '管理员'
            return False
        except:
            return False
    
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
            
            # 获取用户已读状态
            with open(self.read_status_file, 'r', encoding='utf-8') as f:
                read_status = json.load(f)
            
            user_read_updates = read_status.get(username, [])
            
            # 检查是否有新更新
            for update in updates:
                if update['id'] not in user_read_updates:
                    return True
            
            return False
        except:
            return False
    
    def mark_updates_as_read(self, username: str) -> bool:
        """标记所有更新为已读"""
        try:
            updates = self.get_all_updates()
            update_ids = [update['id'] for update in updates]
            
            # 读取当前已读状态
            try:
                with open(self.read_status_file, 'r', encoding='utf-8') as f:
                    read_status = json.load(f)
            except:
                read_status = {}
            
            # 更新用户已读状态
            read_status[username] = update_ids
            
            # 保存已读状态
            with open(self.read_status_file, 'w', encoding='utf-8') as f:
                json.dump(read_status, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False
    
    def get_unread_updates(self, username: str) -> List[Dict]:
        """获取用户未读的更新"""
        try:
            updates = self.get_all_updates()
            
            # 获取用户已读状态
            with open(self.read_status_file, 'r', encoding='utf-8') as f:
                read_status = json.load(f)
            
            user_read_updates = read_status.get(username, [])
            
            # 返回未读更新
            unread_updates = [update for update in updates if update['id'] not in user_read_updates]
            return sorted(unread_updates, key=lambda x: x['publish_time'], reverse=True)
        except:
            return self.get_all_updates()

# 创建全局实例
storage = DataStorage()
