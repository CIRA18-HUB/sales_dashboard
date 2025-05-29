# app.py - 修复版 Streamlit 应用
import streamlit as st
from datetime import datetime
import time
import random
import math
from data_storage import storage

# 设置页面配置
st.set_page_config(
    page_title="Trolli SAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None  # 'admin' 或 'user'
if 'stats_initialized' not in st.session_state:
    st.session_state.stats_initialized = False
    st.session_state.stat1_value = 1000
    st.session_state.stat2_value = 4
    st.session_state.stat3_value = 24
    st.session_state.stat4_value = 99
    st.session_state.last_update = time.time()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "welcome"
if 'show_request_form' not in st.session_state:
    st.session_state.show_request_form = False

# 隐藏Streamlit默认元素 - 修复版（不隐藏侧边栏）
hide_streamlit_style = """
<style>
    /* 隐藏Streamlit默认元素，但保留侧边栏 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 移除顶部空白 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* 确保主内容区占满宽度 */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 主要CSS样式 - 增强版（包含新增的需求提交和展示样式）
main_css = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 全局样式 */
    html, body {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* 主背景渐变 - 确保生效 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
    }
    
    /* 动态背景波纹 - 简化版确保兼容性 */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: waveMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes waveMove {
        0%, 100% { 
            background-position: 0% 0%, 100% 100%;
            opacity: 0.8;
        }
        50% { 
            background-position: 100% 100%, 0% 0%;
            opacity: 1;
        }
    }
    
    /* 确保内容在背景之上 */
    .main .block-container {
        position: relative;
        z-index: 1;
        background: transparent !important;
    }
    
    /* 主标题 */
    .main-title {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
        z-index: 10;
    }
    
    .main-title h1 {
        font-size: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        font-weight: 700;
        animation: titleGlow 3s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 15px rgba(255, 255, 255, 0.4);
            transform: scale(1);
        }
        50% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 25px rgba(255, 255, 255, 0.8);
            transform: scale(1.02);
        }
    }
    
    .main-title p {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* 统计卡片 */
    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 1);
    }
    
    .counter-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
        transition: all 0.3s ease;
    }
    
    .counter-number.updating {
        animation: numberPulse 0.6s ease-out;
    }
    
    @keyframes numberPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }
    
    .stat-label {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .feature-card:hover {
        transform: translateY(-10px) rotate(2deg) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 1);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .feature-title {
        font-size: 1.4rem;
        color: #2d3748;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .feature-description {
        color: #4a5568;
        line-height: 1.6;
    }
    
    /* 更新提示 */
    .update-badge {
        display: inline-block;
        background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%);
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        animation: badgeFloat 3s ease-in-out infinite;
    }
    
    @keyframes badgeFloat {
        0%, 100% { 
            transform: translateY(0);
            box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        }
        50% { 
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(116, 185, 255, 0.5);
        }
    }
    
    .navigation-hint {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 2rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        animation: hintPulse 4s ease-in-out infinite;
    }
    
    @keyframes hintPulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* 登录容器 */
    .login-container {
        max-width: 450px;
        margin: 3rem auto;
        padding: 3rem 2.5rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        text-align: center;
        position: relative;
        z-index: 10;
        animation: loginSlideIn 0.8s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    @keyframes loginSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* 登录按钮特殊样式 */
    .login-form .stButton > button {
        width: 100%;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .login-form .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* 导航按钮特殊样式 */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        margin-top: 1rem !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 顶部按钮和导航按钮区分 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 下拉选择框样式 */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
    }
    
    /* 成功/错误消息样式 */
    .stSuccess, .stError {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 需求提交表单容器 */
    .request-form-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: formFadeIn 0.5s ease-out;
    }
    
    @keyframes formFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 需求展示区域 */
    .request-display-area {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 需求卡片 */
    .request-card {
        background: rgba(248, 249, 250, 0.9);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .request-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 标签样式 */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-processed {
        background: #d1fae5;
        color: #065f46;
    }
    
    .type-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .type-requirement {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .type-issue {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Tabs样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 文本域样式 */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* 日期输入样式 */
    .stDateInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
</style>
"""

st.markdown(main_css, unsafe_allow_html=True)

# 登录界面
if not st.session_state.authenticated:
    # 创建登录界面布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h2 style="font-size: 1.8rem; color: #2d3748; margin-bottom: 0.5rem; font-weight: 600;">Trolli SAL</h2>
            <p style="color: #718096; font-size: 0.9rem; margin-bottom: 2rem;">欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 登录表单
        with st.container():
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("#### 🔐 请输入访问密码")
                password = st.text_input("密码", type="password", placeholder="请输入访问密码", label_visibility="collapsed")
                submit_button = st.form_submit_button("登 录", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if submit_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.session_state.user_role = 'user'
                st.success("🎉 登录成功！正在进入仪表盘...")
                time.sleep(1)
                st.rerun()
            elif password == 'cira18':
                st.session_state.authenticated = True
                st.session_state.user_role = 'admin'
                st.success("🎉 管理员登录成功！正在进入仪表盘...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")
        
        # 需求提交区域
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 提交需求按钮
        if st.button("📝 我要提交需求/问题", use_container_width=True):
            st.session_state.show_request_form = not st.session_state.show_request_form
        
        # 需求提交表单
        if st.session_state.show_request_form:
            with st.container():
                st.markdown('<div class="request-form-container">', unsafe_allow_html=True)
                st.markdown("### 📋 提交需求/问题")
                
                with st.form("request_form"):
                    col_type, col_date = st.columns(2)
                    with col_type:
                        request_type = st.selectbox("类型", ["需求", "问题"])
                    with col_date:
                        requirement_date = st.date_input("需求时间", value=datetime.now())
                    
                    title = st.text_input("标题", placeholder="请简要描述您的需求或问题")
                    content = st.text_area("详细描述", placeholder="请详细说明您的需求或遇到的问题", height=150)
                    submitter = st.text_input("提交人（选填）", placeholder="您的姓名或部门")
                    
                    submit_request = st.form_submit_button("提交", use_container_width=True)
                    
                    if submit_request:
                        if title and content:
                            if storage.add_request(
                                request_type=request_type,
                                title=title,
                                content=content,
                                submitter=submitter,
                                requirement_date=str(requirement_date)
                            ):
                                st.success("✅ 提交成功！我们会尽快处理您的需求。")
                                st.session_state.show_request_form = False
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.error("❌ 请填写标题和详细描述！")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 更新提示
        st.markdown("""
        <div style="text-align: center; margin: 3rem auto;">
            <div class="update-badge">
                🔄 每周四17:00刷新数据
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# 主页面

# 侧边栏
with st.sidebar:
    st.markdown(f"### 👤 当前用户")
    if st.session_state.user_role == 'admin':
        st.markdown("🔐 **管理员**")
    else:
        st.markdown("👤 **普通用户**")
    
    st.markdown("---")
    
    # 管理员功能
    if st.session_state.user_role == 'admin':
        st.markdown("### 🛠️ 管理员功能")
        
        # 发布系统更新
        with st.expander("📢 发布系统更新"):
            with st.form("update_form"):
                update_title = st.text_input("更新标题", placeholder="例如：新增销售报表功能")
                update_content = st.text_area("更新内容", placeholder="详细说明更新内容", height=100)
                
                if st.form_submit_button("发布更新", use_container_width=True):
                    if update_title and update_content:
                        if storage.add_update(update_title, update_content):
                            st.success("✅ 更新发布成功！")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ 请填写完整信息！")
        
        st.markdown("---")
    
    # 退出登录按钮
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.current_page = "welcome"
        st.rerun()

# 主内容区
st.markdown("""
<div class="main-title">
    <h1>📊 Trolli SAL</h1>
    <p>欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>
""", unsafe_allow_html=True)

# 动态更新统计数据
def update_stats():
    current_time = time.time()
    if current_time - st.session_state.last_update >= 3:
        st.session_state.stat1_value = 1000 + random.randint(0, 200) + int(math.sin(current_time * 0.1) * 100)
        st.session_state.stat2_value = 4
        st.session_state.stat3_value = 24
        st.session_state.stat4_value = 95 + random.randint(0, 4) + int(math.sin(current_time * 0.15) * 3)
        st.session_state.last_update = current_time
        return True
    return False

# 更新统计数据
is_updated = update_stats()
update_class = "updating" if is_updated else ""

# 统计卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <span class="counter-number {update_class}">{st.session_state.stat1_value}+</span>
        <div class="stat-label">数据分析</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <span class="counter-number {update_class}">{st.session_state.stat2_value}</span>
        <div class="stat-label">分析模块</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <span class="counter-number {update_class}">{st.session_state.stat3_value}</span>
        <div class="stat-label">小时监控</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <span class="counter-number {update_class}">{st.session_state.stat4_value}%</span>
        <div class="stat-label">准确率</div>
    </div>
    """, unsafe_allow_html=True)

# 需求和更新展示区域
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="request-display-area">', unsafe_allow_html=True)

# 使用标签页展示
tab1, tab2, tab3 = st.tabs(["📋 待处理需求", "📢 系统更新", "✅ 处理记录"])

with tab1:
    pending_requests = storage.get_pending_requests()
    if pending_requests:
        st.markdown(f"### 共有 {len(pending_requests)} 个待处理项目")
        
        # 倒序显示，最新的在前
        for request in reversed(pending_requests):
            with st.container():
                col1, col2 = st.columns([10, 2])
                
                with col1:
                    # 类型和状态标签
                    type_class = "type-requirement" if request['type'] == "需求" else "type-issue"
                    st.markdown(f"""
                    <div class="request-card">
                        <div style="margin-bottom: 0.5rem;">
                            <span class="type-badge {type_class}">{request['type']}</span>
                            <span class="status-badge status-pending">待处理</span>
                            <span style="color: #6b7280; font-size: 0.85rem;">
                                {request['submit_time']} | {request['submitter']}
                            </span>
                        </div>
                        <h4 style="margin: 0.5rem 0; color: #1f2937;">{request['title']}</h4>
                        <p style="color: #4b5563; margin: 0.5rem 0;">{request['content']}</p>
                        <p style="color: #9ca3af; font-size: 0.85rem; margin-top: 0.5rem;">
                            需求时间：{request['requirement_date']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.session_state.user_role == 'admin':
                        if st.button("标记已处理", key=f"process_{request['id']}"):
                            if storage.process_request(request['id']):
                                st.success("✅ 已标记为处理完成")
                                time.sleep(1)
                                st.rerun()
    else:
        st.info("👍 当前没有待处理的需求")

with tab2:
    updates = storage.get_all_updates()
    if updates:
        st.markdown(f"### 系统更新通知")
        
        # 倒序显示，最新的在前
        for update in reversed(updates):
            with st.container():
                col1, col2 = st.columns([10, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="request-card" style="border-left-color: #10b981;">
                        <div style="margin-bottom: 0.5rem;">
                            <span style="color: #6b7280; font-size: 0.85rem;">
                                {update['publish_time']} | {update['publisher']}
                            </span>
                        </div>
                        <h4 style="margin: 0.5rem 0; color: #1f2937;">📢 {update['title']}</h4>
                        <p style="color: #4b5563; margin: 0.5rem 0;">{update['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.session_state.user_role == 'admin':
                        if st.button("删除", key=f"delete_{update['id']}"):
                            if storage.delete_update(update['id']):
                                st.success("✅ 已删除")
                                time.sleep(1)
                                st.rerun()
    else:
        st.info("📭 暂无系统更新")

with tab3:
    processed_requests = storage.get_processed_requests()
    if processed_requests:
        st.markdown(f"### 已处理 {len(processed_requests)} 个项目")
        
        # 倒序显示，最新处理的在前
        for request in reversed(processed_requests):
            type_class = "type-requirement" if request['type'] == "需求" else "type-issue"
            st.markdown(f"""
            <div class="request-card" style="opacity: 0.8;">
                <div style="margin-bottom: 0.5rem;">
                    <span class="type-badge {type_class}">{request['type']}</span>
                    <span class="status-badge status-processed">已处理</span>
                    <span style="color: #6b7280; font-size: 0.85rem;">
                        提交：{request['submit_time']} | {request['submitter']}
                    </span>
                </div>
                <h4 style="margin: 0.5rem 0; color: #1f2937;">{request['title']}</h4>
                <p style="color: #4b5563; margin: 0.5rem 0;">{request['content']}</p>
                <p style="color: #9ca3af; font-size: 0.85rem; margin-top: 0.5rem;">
                    处理时间：{request['process_time']} | 处理人：{request['processor']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 暂无处理记录")

st.markdown('</div>', unsafe_allow_html=True)

# 功能模块介绍
st.markdown("<br><br>", unsafe_allow_html=True)

# 添加导航提示
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h3 style="color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); font-size: 1.5rem;">
        💡 点击下方按钮进入对应分析页面
    </h3>
</div>
""", unsafe_allow_html=True)

# 第一行：产品组合分析 和 预测库存分析
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📦</span>
        <h3 class="feature-title">产品组合分析</h3>
        <p class="feature-description">
            分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 进入产品组合分析", key="product_nav", use_container_width=True):
        try:
            st.switch_page("pages/产品组合分析.py")
        except:
            st.info("📦 正在跳转到产品组合分析页面...")

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <h3 class="feature-title">预测库存分析</h3>
        <p class="feature-description">
            基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 进入预测库存分析", key="inventory_nav", use_container_width=True):
        try:
            st.switch_page("pages/预测库存分析.py")
        except:
            st.info("📊 正在跳转到预测库存分析页面...")

st.markdown("<br>", unsafe_allow_html=True)

# 第二行：客户依赖分析 和 销售达成分析  
col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">👥</span>
        <h3 class="feature-title">客户依赖分析</h3>
        <p class="feature-description">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 进入客户依赖分析", key="customer_nav", use_container_width=True):
        try:
            st.switch_page("pages/客户依赖分析.py")
        except:
            st.info("👥 正在跳转到客户依赖分析页面...")

with col4:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🎯</span>
        <h3 class="feature-title">销售达成分析</h3>
        <p class="feature-description">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 进入销售达成分析", key="sales_nav", use_container_width=True):
        try:
            st.switch_page("pages/销售达成分析.py")
        except:
            st.info("🎯 正在跳转到销售达成分析页面...")

# 更新提示和导航
st.markdown("""
<div style="text-align: center; margin: 3rem auto;">
    <div class="update-badge">
        🔄 每周四17:00刷新数据
    </div>
</div>

<div class="navigation-hint">
    ✨ 享受简洁优雅的数据分析体验
</div>

<div class="footer">
    <p>Trolli SAL | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周四17:00刷新数据 | 将枯燥数据变好看</p>
</div>
""", unsafe_allow_html=True)

# 自动刷新机制
if st.session_state.authenticated:
    time.sleep(0.1)
    if is_updated:
        st.rerun()
