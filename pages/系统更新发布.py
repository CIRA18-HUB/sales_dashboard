# pages/系统更新发布.py - 系统更新发布页面
import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_storage import storage

# 设置页面配置
st.set_page_config(
    page_title="系统更新发布 - Trolli SAL",
    page_icon="🔔",
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

    /* 更新卡片 */
    .update-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
        position: relative;
    }

    .update-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
    }

    .update-card.unread {
        border-left-color: #ff416c;
        background: linear-gradient(135deg, rgba(255, 65, 108, 0.05) 0%, rgba(255, 255, 255, 0.95) 50%);
    }

    .update-card.unread::before {
        content: '新';
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #ff416c 0%, #ff4757 100%);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        animation: newBadgePulse 2s ease-in-out infinite;
    }

    @keyframes newBadgePulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 2px 8px rgba(255, 65, 108, 0.4);
        }
        50% { 
            transform: scale(1.1);
            box-shadow: 0 4px 16px rgba(255, 65, 108, 0.8);
        }
    }

    .update-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .update-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0;
    }

    .update-publisher {
        background: linear-gradient(135degrees, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .update-content {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
        white-space: pre-wrap;
    }

    .update-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        color: #718096;
    }

    .update-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }

    /* 按钮样式 */
    .btn-read {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }

    .btn-read:hover {
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
    .stTextArea > div > div > textarea {
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

    /* 全部标记已读按钮 */
    .mark-all-read-btn {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 500;
        transition: all 0.3s ease;
        display: inline-block;
        margin-bottom: 1rem;
    }

    .mark-all-read-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(116, 185, 255, 0.4);
    }

    /* 空状态样式 */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #4a5568;
    }

    .empty-state h3 {
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }

    .empty-state p {
        color: #718096;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="page-title">🔔 系统更新发布</h1>', unsafe_allow_html=True)

# 创建标签页
tab1, tab2 = st.tabs(["📢 发布更新", "📋 更新记录"])

with tab1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("### 发布系统更新")
    st.markdown("---")
    
    with st.form("publish_update_form"):
        title = st.text_input(
            "更新标题",
            placeholder="请输入更新标题...",
            help="简要描述本次更新的主要内容"
        )
        
        content = st.text_area(
            "更新内容",
            placeholder="请输入详细的更新内容...\n\n可以包括：\n- 新增功能\n- 修复的问题\n- 性能优化\n- 注意事项等",
            height=200,
            help="详细描述本次更新的内容"
        )
        
        publisher = st.text_input(
            "发布人",
            value="管理员",
            help="发布人姓名"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 发布更新", use_container_width=True)
        
        if submit_button:
            if title and content:
                success = storage.add_update(
                    title=title,
                    content=content,
                    publisher=publisher
                )
                
                if success:
                    st.success("✅ 系统更新发布成功！")
                    st.balloons()
                else:
                    st.error("❌ 发布失败，请重试！")
            else:
                st.warning("⚠️ 请填写完整的更新标题和内容！")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### 📋 系统更新记录")
    st.markdown("---")
    
    all_updates = storage.get_all_updates()
    user_read_status = storage.get_user_read_status("cira")
    unread_count = storage.get_unread_updates_count("cira")
    
    if all_updates:
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(all_updates)}</div>
                <div class="stats-label">总更新数</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number" style="color: #ff416c;">{unread_count}</div>
                <div class="stats-label">未读更新</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            read_count = len(all_updates) - unread_count
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number" style="color: #00b894;">{read_count}</div>
                <div class="stats-label">已读更新</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            latest_update = storage.get_latest_update()
            if latest_update:
                days_ago = (datetime.now() - datetime.strptime(latest_update['publish_time'], "%Y-%m-%d %H:%M:%S")).days
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{days_ago}</div>
                    <div class="stats-label">最新更新(天前)</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 全部标记已读按钮
        if unread_count > 0:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📖 全部标记已读", use_container_width=True):
                    if storage.mark_all_updates_as_read("cira"):
                        st.success("✅ 已将所有更新标记为已读！")
                        st.rerun()
                    else:
                        st.error("❌ 操作失败！")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 显示更新列表
        for i, update in enumerate(all_updates):
            update_id = update['id']
            is_read = user_read_status.get(update_id, {}).get('is_read', False)
            card_class = "update-card" if is_read else "update-card unread"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="update-header">
                    <h3 class="update-title">{update['title']}</h3>
                    <span class="update-publisher">{update['publisher']}</span>
                </div>
                <div class="update-content">{update['content']}</div>
                <div class="update-meta">
                    <div><strong>发布时间：</strong>{update['publish_time']}</div>
                    <div><strong>状态：</strong>{'已读' if is_read else '未读'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 操作按钮
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            if not is_read:
                with col2:
                    if st.button(f"✅ 标记已读", key=f"read_{i}"):
                        if storage.mark_update_as_read(update_id, "cira"):
                            st.success("✅ 已标记为已读！")
                            st.rerun()
                        else:
                            st.error("❌ 操作失败！")
            
            with col3:
                if st.button(f"🗑️ 删除更新", key=f"delete_{i}"):
                    if storage.delete_update(update_id):
                        st.success("✅ 更新已删除！")
                        st.rerun()
                    else:
                        st.error("❌ 删除失败！")
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="update-card">
            <div class="empty-state">
                <h3>📭 暂无系统更新</h3>
                <p>当前没有发布任何系统更新，您可以在"发布更新"标签页添加新的系统更新。</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 返回主页按钮
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🏠 返回主页", use_container_width=True):
        st.switch_page("登陆界面haha.py")
