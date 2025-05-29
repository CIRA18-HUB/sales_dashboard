# pages/需求管理.py - 需求管理页面
import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_storage import storage

# 设置页面配置
st.set_page_config(
    page_title="需求管理 - Trolli SAL",
    page_icon="📝",
    layout="wide"
)

# 应用CSS样式
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 主容器 */
    .block-container {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* 页面标题 */
    .page-title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        animation: titleGlow 3s ease-in-out infinite;
    }

    @keyframes titleGlow {
        0%, 100% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
        }
        50% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
        }
    }

    /* 表单容器 */
    .form-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: slideInUp 0.8s ease-out;
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* 需求卡片 */
    .request-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }

    .request-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
    }

    .request-card.processed {
        border-left-color: #00b894;
        opacity: 0.8;
    }

    .request-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .request-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0;
    }

    .request-type {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .request-status {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .status-pending {
        background: linear-gradient(135deg, #ffa726 0%, #ff7043 100%);
        color: white;
    }

    .status-processed {
        background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
        color: white;
    }

    .request-content {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .request-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        color: #718096;
    }

    .request-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }

    /* 按钮样式 */
    .btn-process {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }

    .btn-process:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 184, 148, 0.3);
    }

    .btn-delete {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }

    .btn-delete:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
    }

    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        padding: 1rem 2rem;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }

    /* 输入框样式 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* 提交按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }

    /* 统计卡片 */
    .stats-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stats-label {
        color: #4a5568;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="page-title">📝 需求管理</h1>', unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3 = st.tabs(["📝 提交需求", "⏳ 待处理需求", "✅ 处理记录"])

with tab1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("### 提交新需求")
    st.markdown("---")
    
    with st.form("submit_request_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            request_type = st.selectbox(
                "需求类型",
                ["功能需求", "问题反馈", "系统优化", "数据请求", "其他"],
                help="请选择您的需求类型"
            )
            
            submitter = st.text_input(
                "提交人",
                value="cira",
                help="请输入您的姓名"
            )
        
        with col2:
            title = st.text_input(
                "需求标题",
                placeholder="请简要描述您的需求",
                help="请用一句话概括您的需求"
            )
            
            requirement_date = st.date_input(
                "期望完成日期",
                value=datetime.now().date(),
                help="请选择您期望的完成日期"
            )
        
        content = st.text_area(
            "需求描述",
            placeholder="请详细描述您的需求...",
            height=150,
            help="请详细描述您的需求，包括背景、期望结果等"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 提交需求", use_container_width=True)
        
        if submit_button:
            if title and content:
                success = storage.add_request(
                    request_type=request_type,
                    title=title,
                    content=content,
                    submitter=submitter,
                    requirement_date=requirement_date.strftime("%Y-%m-%d")
                )
                
                if success:
                    st.success("✅ 需求提交成功！您的需求已进入待处理队列。")
                    st.balloons()
                else:
                    st.error("❌ 提交失败，请重试！")
            else:
                st.warning("⚠️ 请填写完整的需求标题和描述！")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### ⏳ 待处理需求")
    st.markdown("---")
    
    pending_requests = storage.get_pending_requests()
    
    if pending_requests:
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(pending_requests)}</div>
                <div class="stats-label">待处理</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            types = [req['type'] for req in pending_requests]
            most_common = max(set(types), key=types.count) if types else "无"
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number" style="font-size: 1.2rem;">{most_common}</div>
                <div class="stats-label">最多类型</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_days = sum([int((datetime.now() - datetime.strptime(req['submit_time'], "%Y-%m-%d %H:%M:%S")).days) for req in pending_requests]) / len(pending_requests)
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{avg_days:.1f}</div>
                <div class="stats-label">平均等待天数</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 显示需求列表
        for i, request in enumerate(pending_requests):
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">
                    <h3 class="request-title">{request['title']}</h3>
                    <div>
                        <span class="request-type">{request['type']}</span>
                        <span class="request-status status-pending">待处理</span>
                    </div>
                </div>
                <div class="request-content">{request['content']}</div>
                <div class="request-meta">
                    <div>
                        <strong>提交人：</strong>{request['submitter']} | 
                        <strong>期望完成：</strong>{request['requirement_date']} | 
                        <strong>提交时间：</strong>{request['submit_time']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 管理员操作按钮
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col2:
                if st.button(f"✅ 标记已处理", key=f"process_{i}"):
                    if storage.process_request(request['id'], "管理员"):
                        st.success("✅ 需求已标记为已处理！")
                        st.rerun()
                    else:
                        st.error("❌ 操作失败！")
            
            with col3:
                if st.button(f"🗑️ 删除需求", key=f"delete_{i}"):
                    if storage.delete_request(request['id']):
                        st.success("✅ 需求已删除！")
                        st.rerun()
                    else:
                        st.error("❌ 删除失败！")
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="request-card" style="text-align: center; padding: 3rem;">
            <h3 style="color: #4a5568; margin-bottom: 1rem;">🎉 暂无待处理需求</h3>
            <p style="color: #718096;">当前没有待处理的需求，您可以在"提交需求"标签页添加新需求。</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### ✅ 处理记录")
    st.markdown("---")
    
    processed_requests = storage.get_processed_requests()
    
    if processed_requests:
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(processed_requests)}</div>
                <div class="stats-label">已处理</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # 计算平均处理时间
            total_hours = 0
            valid_count = 0
            for req in processed_requests:
                if req.get('process_time') and req.get('submit_time'):
                    submit_time = datetime.strptime(req['submit_time'], "%Y-%m-%d %H:%M:%S")
                    process_time = datetime.strptime(req['process_time'], "%Y-%m-%d %H:%M:%S")
                    hours = (process_time - submit_time).total_seconds() / 3600
                    total_hours += hours
                    valid_count += 1
            
            avg_process_hours = total_hours / valid_count if valid_count > 0 else 0
            if avg_process_hours < 24:
                display_time = f"{avg_process_hours:.1f}h"
            else:
                display_time = f"{avg_process_hours/24:.1f}d"
            
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number" style="font-size: 1.2rem;">{display_time}</div>
                <div class="stats-label">平均处理时间</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            types = [req['type'] for req in processed_requests]
            most_common = max(set(types), key=types.count) if types else "无"
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number" style="font-size: 1.2rem;">{most_common}</div>
                <div class="stats-label">处理最多类型</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 显示已处理需求列表
        for request in processed_requests:
            st.markdown(f"""
            <div class="request-card processed">
                <div class="request-header">
                    <h3 class="request-title">{request['title']}</h3>
                    <div>
                        <span class="request-type">{request['type']}</span>
                        <span class="request-status status-processed">已处理</span>
                    </div>
                </div>
                <div class="request-content">{request['content']}</div>
                <div class="request-meta">
                    <div>
                        <strong>提交人：</strong>{request['submitter']} | 
                        <strong>期望完成：</strong>{request['requirement_date']} | 
                        <strong>提交时间：</strong>{request['submit_time']}
                    </div>
                    <div>
                        <strong>处理人：</strong>{request.get('processor', '未知')} | 
                        <strong>处理时间：</strong>{request.get('process_time', '未知')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="request-card" style="text-align: center; padding: 3rem;">
            <h3 style="color: #4a5568; margin-bottom: 1rem;">📋 暂无处理记录</h3>
            <p style="color: #718096;">当前没有已处理的需求记录。</p>
        </div>
        """, unsafe_allow_html=True)

# 返回主页按钮
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🏠 返回主页", use_container_width=True):
        st.switch_page("登陆界面haha.py")
