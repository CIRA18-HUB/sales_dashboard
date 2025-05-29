# pages/_管理员_系统更新发布.py - 管理员专用系统更新发布页面
import streamlit as st
from datetime import datetime
import sys
import os
import time

# 添加主目录到路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_storage import storage

# 页面配置
st.set_page_config(
    page_title="系统更新发布 | Trolli SAL",
    page_icon="🔄",
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

# 🛡️ 管理员权限检查
if not storage.is_admin(st.session_state.username):
    st.error("❌ 您没有权限访问此页面")
    st.markdown("""
    <div style="text-align: center; margin: 2rem; background: rgba(231, 76, 60, 0.1); padding: 2rem; border-radius: 10px; border-left: 4px solid #e74c3c;">
        <h3 style="color: #e74c3c; margin-bottom: 1rem;">🚫 访问被拒绝</h3>
        <p style="color: #c0392b; margin-bottom: 1.5rem;">此页面仅限管理员访问。</p>
        <p style="color: #7f8c8d;">如果您认为这是个错误，请联系系统管理员。</p>
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

    /* 更新项目样式 */
    .update-item {
        background: rgba(248, 250, 252, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #00b894;
        transition: all 0.3s ease;
        position: relative;
    }

    .update-item:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .update-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }

    .update-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0;
        flex: 1;
    }

    .update-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .update-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #718096;
        flex-wrap: wrap;
    }

    .update-content {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
        white-space: pre-line;
    }

    /* 删除按钮样式 */
    .delete-btn {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.8rem !important;
    }

    /* 标记已读按钮样式 */
    .mark-read-btn {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%) !important;
        padding: 0.8rem 2rem !important;
        font-size: 1rem !important;
        margin: 1rem 0 !important;
    }

    /* 新更新提示 */
    .new-update-badge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: linear-gradient(135deg, #ff6b6b 0%, #e74c3c 100%);
        color: white;
        font-size: 0.7rem;
        font-weight: bold;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
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

    /* 管理员标识 */
    .admin-badge {
        background: linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 1rem;
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
        .update-header {
            flex-direction: column;
            gap: 1rem;
        }
        .update-actions {
            align-self: flex-start;
        }
        .update-meta {
            flex-direction: column;
            gap: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 显示用户信息和管理员标识
st.markdown(f"""
<div class="user-info">
    👤 {st.session_state.display_name} ({st.session_state.user_role}) | 管理员专用页面
</div>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="page-title">🔄 系统更新发布</h1>', unsafe_allow_html=True)
st.markdown('<div class="admin-badge">👨‍💼 管理员专用</div>', unsafe_allow_html=True)

# 创建选项卡
tab1, tab2 = st.tabs(["📝 发布更新", "📋 更新记录"])

# Tab 1: 发布更新
with tab1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown("### 📝 发布系统更新")
    st.markdown("发布新的系统更新通知，用户在系统中会看到更新提示。")
    
    with st.form("publish_update_form", clear_on_submit=True):
        title = st.text_input(
            "更新标题",
            placeholder="例如：系统功能优化更新 v1.2.0",
            help="简洁明了的更新标题"
        )
        
        content = st.text_area(
            "更新内容",
            placeholder="详细描述此次更新的内容，包括：\n1. 新增功能\n2. 优化改进\n3. 问题修复\n4. 注意事项",
            height=200,
            help="详细的更新说明，支持换行"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            publish_btn = st.form_submit_button("🚀 发布更新", use_container_width=True)
    
    if publish_btn:
        if not title.strip():
            st.error("❌ 请输入更新标题")
        elif not content.strip():
            st.error("❌ 请输入更新内容")
        else:
            success = storage.add_update(
                title=title.strip(),
                content=content.strip(),
                publisher=st.session_state.display_name
            )
            
            if success:
                st.success("🎉 系统更新发布成功！用户将看到更新提示。")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 发布失败，请重试")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: 更新记录
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📋 已发布的更新")
    with col2:
        if st.button("🔍 标记全部已读", use_container_width=True, key="mark_all_read"):
            if storage.mark_updates_as_read(st.session_state.username):
                st.success("✅ 已标记全部更新为已读")
                time.sleep(0.5)
                st.rerun()
    with col3:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    # 获取所有更新和未读更新
    all_updates = storage.get_all_updates()
    unread_updates = storage.get_unread_updates(st.session_state.username)
    unread_ids = [update['id'] for update in unread_updates]
    
    if not all_updates:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔄</div>
            <h3>暂无更新记录</h3>
            <p>还没有发布任何系统更新。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 按发布时间倒序显示
        sorted_updates = sorted(all_updates, key=lambda x: x['publish_time'], reverse=True)
        
        for update in sorted_updates:
            is_unread = update['id'] in unread_ids
            
            with st.container():
                st.markdown(f"""
                <div class="update-item">
                    {f'<div class="new-update-badge">新</div>' if is_unread else ''}
                    <div class="update-header">
                        <h4 class="update-title">{update['title']}</h4>
                        <div class="update-actions">
                        </div>
                    </div>
                    <div class="update-meta">
                        <span>👨‍💼 发布人：{update['publisher']}</span>
                        <span>📅 发布时间：{update['publish_time']}</span>
                        {f'<span style="color: #e53e3e; font-weight: bold;">🔴 未读</span>' if is_unread else '<span style="color: #00b894; font-weight: bold;">✅ 已读</span>'}
                    </div>
                    <div class="update-content">
                        {update['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 删除按钮（只有管理员可以删除）
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button(f"🗑️ 删除", key=f"delete_{update['id']}", use_container_width=True):
                        if storage.delete_update(update['id']):
                            st.success("✅ 更新已删除")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ 删除失败，请重试")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 统计信息
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("### 📊 统计信息")

col1, col2, col3 = st.columns(3)

with col1:
    total_updates = len(storage.get_all_updates())
    st.metric("总更新数", total_updates, help="已发布的更新总数")

with col2:
    unread_count = len(storage.get_unread_updates(st.session_state.username))
    st.metric("未读更新", unread_count, help="您未读的更新数量")

with col3:
    read_count = total_updates - unread_count
    st.metric("已读更新", read_count, help="您已读的更新数量")

st.markdown('</div>', unsafe_allow_html=True)
