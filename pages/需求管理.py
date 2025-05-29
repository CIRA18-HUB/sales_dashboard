# pages/需求管理.py - 需求管理页面（移除自定义导航版本）
import streamlit as st
from datetime import datetime, date
import sys
import os
import time

# 添加主目录到路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_storage import storage

# 页面配置
st.set_page_config(
    page_title="需求管理 | Trolli SAL",
    page_icon="📋",
    layout="wide"
)

# 🔐 登录状态检查
if not st.session_state.get('authenticated', False):
    st.error("❌ 请先登录系统")
    st.markdown("""
    <div style="text-align: center; margin: 2rem;">
        <p>您需要先登录才能访问此页面</p>
        <a href="/" style="color: #667eea; text-decoration: none; font-weight: 500;">👈 返回登录页面</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 应用完整CSS样式（包含紫色背景）
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 主容器背景 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景波纹效果 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 60%);
        animation: waveMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes waveMove {
        0%, 100% { 
            background-size: 200% 200%, 150% 150%, 300% 300%;
            background-position: 0% 0%, 100% 100%, 50% 50%; 
        }
        33% { 
            background-size: 300% 300%, 200% 200%, 250% 250%;
            background-position: 100% 0%, 0% 50%, 80% 20%; 
        }
        66% { 
            background-size: 250% 250%, 300% 300%, 200% 200%;
            background-position: 50% 100%, 50% 0%, 20% 80%; 
        }
    }

    /* 主容器 */
    .main .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
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
        0%, 100% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); }
        50% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5); }
    }

    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }

    /* 卡片样式 */
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: cardSlideUp 0.8s ease-out;
    }

    @keyframes cardSlideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 表单样式 */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 2px solid rgba(229, 232, 240, 0.8);
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .stDateInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem;
    }

    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 需求项目样式 */
    .request-item {
        background: rgba(248, 250, 252, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .request-item:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .request-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .request-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0;
    }

    .request-status {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-pending {
        background: linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%);
        color: white;
    }

    .status-processed {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
    }

    .request-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #718096;
    }

    .request-content {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* 空状态样式 */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #718096;
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    /* 用户信息样式 */
    .user-info {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .page-title {
            font-size: 2rem;
        }
        .content-card {
            padding: 1.5rem;
        }
        .request-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .request-meta {
            flex-direction: column;
            gap: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 显示用户信息
st.markdown(f"""
<div class="user-info">
    👤 欢迎，{st.session_state.display_name} ({st.session_state.user_role})
</div>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="page-title">📋 需求管理</h1>', unsafe_allow_html=True)

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["📝 提交需求", "⏳ 待处理需求", "✅ 处理记录"])

# Tab 1: 提交需求
with tab1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown("### 📝 提交新需求")
    st.markdown("请详细描述您的需求或遇到的问题，我们会尽快处理。")
    
    with st.form("submit_request_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            request_type = st.selectbox(
                "需求类型",
                ["功能需求", "问题反馈", "数据问题", "界面优化", "其他"],
                help="请选择最符合的需求类型"
            )
        
        with col2:
            requirement_date = st.date_input(
                "期望完成日期",
                value=date.today(),
                help="您希望此需求完成的日期"
            )
        
        title = st.text_input(
            "需求标题",
            placeholder="请输入简明的需求标题...",
            help="用一句话概括您的需求"
        )
        
        content = st.text_area(
            "详细描述",
            placeholder="请详细描述您的需求或问题，包括具体的场景、期望的效果等...",
            height=120,
            help="详细的描述有助于我们更好地理解和处理您的需求"
        )
        
        submitter = st.text_input(
            "提交人",
            value=st.session_state.get('display_name', ''),
            help="您的姓名或昵称"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_btn = st.form_submit_button("🚀 提交需求", use_container_width=True)
    
    if submit_btn:
        if not title.strip():
            st.error("❌ 请输入需求标题")
        elif not content.strip():
            st.error("❌ 请输入详细描述")
        else:
            success = storage.add_request(
                request_type=request_type,
                title=title.strip(),
                content=content.strip(),
                submitter=submitter.strip() if submitter.strip() else "匿名",
                requirement_date=requirement_date.strftime("%Y-%m-%d")
            )
            
            if success:
                st.success("🎉 需求提交成功！我们会尽快处理您的需求。")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 提交失败，请重试")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: 待处理需求
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### ⏳ 待处理需求")
    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    pending_requests = storage.get_pending_requests()
    
    if not pending_requests:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3>当前没有待处理的需求</h3>
            <p>所有需求都已处理完成，或者还没有新的需求提交。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for request in pending_requests:
            with st.container():
                st.markdown(f"""
                <div class="request-item">
                    <div class="request-header">
                        <h4 class="request-title">{request['title']}</h4>
                        <span class="request-status status-pending">待处理</span>
                    </div>
                    <div class="request-meta">
                        <span>📋 类型：{request['type']}</span>
                        <span>👤 提交人：{request['submitter']}</span>
                        <span>📅 提交时间：{request['submit_time']}</span>
                        <span>⏰ 期望完成：{request['requirement_date']}</span>
                    </div>
                    <div class="request-content">
                        {request['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 管理员可以处理需求
                if storage.is_admin(st.session_state.username):
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button(f"✅ 处理", key=f"process_{request['id']}", use_container_width=True):
                            if storage.process_request(request['id'], st.session_state.display_name):
                                st.success("✅ 需求已标记为已处理")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ 处理失败，请重试")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: 处理记录
with tab3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### ✅ 处理记录")
    with col2:
        if st.button("🔄 刷新记录", use_container_width=True):
            st.rerun()
    
    processed_requests = storage.get_processed_requests()
    
    if not processed_requests:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <h3>暂无处理记录</h3>
            <p>还没有已处理的需求记录。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for request in processed_requests:
            st.markdown(f"""
            <div class="request-item">
                <div class="request-header">
                    <h4 class="request-title">{request['title']}</h4>
                    <span class="request-status status-processed">已处理</span>
                </div>
                <div class="request-meta">
                    <span>📋 类型：{request['type']}</span>
                    <span>👤 提交人：{request['submitter']}</span>
                    <span>📅 提交时间：{request['submit_time']}</span>
                    <span>⏰ 期望完成：{request['requirement_date']}</span>
                    <span>✅ 处理时间：{request['process_time']}</span>
                    <span>👨‍💼 处理人：{request['processor']}</span>
                </div>
                <div class="request-content">
                    {request['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 统计信息
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("### 📊 需求统计")

col1, col2, col3 = st.columns(3)

with col1:
    total_requests = len(storage.get_all_requests())
    st.metric("总需求数", total_requests, help="系统中的需求总数")

with col2:
    pending_count = len(storage.get_pending_requests())
    st.metric("待处理", pending_count, help="等待处理的需求数量")

with col3:
    processed_count = len(storage.get_processed_requests())
    st.metric("已处理", processed_count, help="已完成处理的需求数量")

st.markdown('</div>', unsafe_allow_html=True)
