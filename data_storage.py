# data_storage.py - 数据存储模块（增强版）
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
        
        # 初始化用户阅读状态文件
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
                "processor": None,
                "process_note": ""
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
    
    def process_request(self, request_id: str, processor: str = "管理员", process_note: str = "") -> bool:
        """处理需求/问题"""
        try:
            requests = self.get_all_requests()
            for request in requests:
                if request['id'] == request_id:
                    request['status'] = '已处理'
                    request['process_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    request['processor'] = processor
                    request['process_note'] = process_note
                    break
            
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def delete_request(self, request_id: str) -> bool:
        """删除需求/问题"""
        try:
            requests = self.get_all_requests()
            requests = [r for r in requests if r['id'] != request_id]
            
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
                "publisher": publisher,
                "is_important": False
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
                updates = json.load(f)
                # 按发布时间倒序排列
                return sorted(updates, key=lambda x: x['publish_time'], reverse=True)
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
    
    def get_user_read_status(self, username: str = "cira") -> Dict:
        """获取用户的阅读状态"""
        try:
            with open(self.user_read_status_file, 'r', encoding='utf-8') as f:
                all_status = json.load(f)
                return all_status.get(username, {})
        except:
            return {}
    
    def mark_update_as_read(self, update_id: str, username: str = "cira") -> bool:
        """标记更新为已读"""
        try:
            with open(self.user_read_status_file, 'r', encoding='utf-8') as f:
                all_status = json.load(f)
            
            if username not in all_status:
                all_status[username] = {}
            
            all_status[username][update_id] = {
                "read_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_read": True
            }
            
            with open(self.user_read_status_file, 'w', encoding='utf-8') as f:
                json.dump(all_status, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_unread_updates_count(self, username: str = "cira") -> int:
        """获取未读更新数量"""
        try:
            all_updates = self.get_all_updates()
            user_read_status = self.get_user_read_status(username)
            
            unread_count = 0
            for update in all_updates:
                update_id = update['id']
                if update_id not in user_read_status or not user_read_status[update_id].get('is_read', False):
                    unread_count += 1
            
            return unread_count
        except:
            return 0
    
    def has_unread_updates(self, username: str = "cira") -> bool:
        """检查是否有未读更新"""
        return self.get_unread_updates_count(username) > 0
    
    def get_latest_update(self) -> Optional[Dict]:
        """获取最新的系统更新"""
        updates = self.get_all_updates()
        return updates[0] if updates else None
    
    def mark_all_updates_as_read(self, username: str = "cira") -> bool:
        """标记所有更新为已读"""
        try:
            all_updates = self.get_all_updates()
            
            with open(self.user_read_status_file, 'r', encoding='utf-8') as f:
                all_status = json.load(f)
            
            if username not in all_status:
                all_status[username] = {}
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for update in all_updates:
                all_status[username][update['id']] = {
                    "read_time": current_time,
                    "is_read": True
                }
            
            with open(self.user_read_status_file, 'w', encoding='utf-8') as f:
                json.dump(all_status, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

# 创建全局实例
storage = DataStorage()
