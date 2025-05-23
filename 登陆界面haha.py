# app.py - Trolli SAL 浅色系高观赏性版本
import streamlit as st
from datetime import datetime
import time
import random
import math

# 设置页面配置
st.set_page_config(
    page_title="Trolli SAL - 智能数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏Streamlit默认元素
hide_streamlit_style = """
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* 隐藏侧边栏的Streamlit branding */
    .css-1y4p8pa {padding-top: 0rem;}
    [data-testid="stSidebarNav"] {display: none;}

    /* 调整主容器的padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 初始化session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'
if 'animation_key' not in st.session_state:
    st.session_state.animation_key = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# 动态数据初始化
if 'dynamic_stats' not in st.session_state:
    st.session_state.dynamic_stats = {
        'sales': 2345678,
        'analysis': 1234,
        'accuracy': 98.5,
        'login_stats': {
            'data_analysis': 1234,
            'modules': 4,
            'monitoring': 24,
            'accuracy': 99
        }
    }

# 完整的CSS样式
complete_css = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* 登录页面背景 */
    .stApp[data-page="login"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 25%, #ffeef8 50%, #fff0e8 75%, #f0f4ff 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 主页面背景 */
    .stApp[data-page="main"] {
        background: #f8fafc;
    }

    /* 浮动几何图形 */
    .floating-shapes {
        position: fixed;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: 1;
        pointer-events: none;
    }

    .shape {
        position: absolute;
        background: linear-gradient(45deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        backdrop-filter: blur(5px);
        animation: float 20s infinite ease-in-out;
    }

    .shape:nth-child(1) {
        width: 300px;
        height: 300px;
        border-radius: 63% 37% 54% 46% / 55% 48% 52% 45%;
        top: 10%;
        left: 10%;
        animation-duration: 25s;
    }

    .shape:nth-child(2) {
        width: 200px;
        height: 200px;
        border-radius: 73% 27% 26% 74% / 54% 32% 68% 46%;
        top: 60%;
        right: 10%;
        animation-duration: 20s;
        animation-delay: -5s;
    }

    .shape:nth-child(3) {
        width: 250px;
        height: 250px;
        border-radius: 43% 57% 61% 39% / 44% 68% 32% 56%;
        bottom: 10%;
        left: 30%;
        animation-duration: 30s;
        animation-delay: -10s;
    }

    @keyframes float {
        0%, 100% {
            transform: translate(0, 0) rotate(0deg) scale(1);
        }
        33% {
            transform: translate(30px, -30px) rotate(120deg) scale(1.1);
        }
        66% {
            transform: translate(-20px, 20px) rotate(240deg) scale(0.9);
        }
    }

    /* 登录卡片 */
    .login-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        max-width: 450px;
        margin: 3rem auto;
        box-shadow: 
            0 20px 40px rgba(99, 102, 241, 0.08),
            0 0 0 1px rgba(99, 102, 241, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        animation: cardEntry 1s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
    }

    @keyframes cardEntry {
        0% {
            opacity: 0;
            transform: translateY(30px) scale(0.9);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Logo动画 */
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }

    .logo {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        margin: 0 auto 1rem;
        animation: logoBounce 2s ease-in-out infinite;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }

    @keyframes logoBounce {
        0%, 100% { 
            transform: translateY(0) rotate(0deg);
        }
        50% { 
            transform: translateY(-10px) rotate(5deg);
        }
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* 登录页统计卡片 */
    .login-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 2.5rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(168, 85, 247, 0.05));
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }

    .login-stat-item {
        text-align: center;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .login-stat-item:hover {
        transform: scale(1.05);
        background: rgba(255, 255, 255, 0.9);
    }

    .login-stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
        animation: countUp 2s ease-out;
    }

    @keyframes countUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* 装饰点点 */
    .decorative-dots {
        position: absolute;
        width: 100px;
        height: 100px;
        top: -30px;
        right: -30px;
        background-image: 
            radial-gradient(circle, rgba(99, 102, 241, 0.3) 2px, transparent 2px),
            radial-gradient(circle, rgba(168, 85, 247, 0.3) 2px, transparent 2px);
        background-size: 20px 20px, 30px 30px;
        background-position: 0 0, 15px 15px;
        animation: dotsRotate 60s linear infinite;
    }

    @keyframes dotsRotate {
        100% { transform: rotate(360deg); }
    }

    /* Streamlit输入框美化 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.8);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        background: white;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
    }

    /* 登录按钮 */
    .stButton > button {
        width: 100%;
        padding: 1.25rem;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }

    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }

    /* 更新徽章 */
    .update-badge {
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 2rem auto 0;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3);
        text-align: center;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    /* 侧边栏样式 */
    .stSidebar {
        background: white;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.05);
    }

    .stSidebar > div:first-child {
        background: white;
        padding-top: 0;
    }

    /* 侧边栏头部 */
    .sidebar-header {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        padding: 2rem 1.5rem;
        margin: -1rem -1rem 1rem -1rem;
        text-align: center;
    }

    .sidebar-logo-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }

    .sidebar-logo {
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    /* 侧边栏按钮 */
    .stSidebar .stButton > button {
        background: #f8fafc;
        color: #334155;
        padding: 0.875rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 10px;
        font-weight: 500;
        text-align: left;
        transition: all 0.2s ease;
    }

    .stSidebar .stButton > button:hover {
        background: #f1f5f9;
        transform: translateX(4px);
        box-shadow: none;
    }

    .stSidebar .stButton > button.active-page {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
    }

    /* 用户信息卡片 */
    .user-info-card {
        background: linear-gradient(135deg, #f0f4ff, #ffeef8);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* 主页面标题 */
    .welcome-header {
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeInUp 0.8s ease;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .welcome-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.75rem;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        height: 100%;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899, #f59e0b);
        background-size: 300% 100%;
        animation: gradientMove 3s ease infinite;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    }

    .stat-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .stat-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }

    .stat-value.updating {
        animation: numberPulse 0.6s ease;
    }

    @keyframes numberPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); color: #6366f1; }
    }

    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
    }

    .stat-trend {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        color: #10b981;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* 功能卡片 */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        height: 100%;
    }

    .feature-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
        transform: scale(0);
        transition: transform 0.6s ease;
    }

    .feature-card:hover::after {
        transform: scale(1);
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    }

    .feature-icon-wrapper {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.3);
    }

    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.75rem;
    }

    .feature-description {
        color: #64748b;
        line-height: 1.6;
    }

    /* 导航提示 */
    .nav-hint {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-top: 2rem;
    }

    .nav-hint-icon {
        display: inline-block;
        animation: bounce 2s ease-in-out infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(-10px); }
    }

    /* 更新徽章（大） */
    .update-badge-large {
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 600;
        display: inline-block;
        animation: floatBadge 3s ease-in-out infinite;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        text-align: center;
        margin: 3rem auto;
    }

    @keyframes floatBadge {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* 动画类 */
    .animate-in {
        animation: slideIn 0.6s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
"""


# 更新动态数据
def update_dynamic_stats():
    current_time = time.time()
    if current_time - st.session_state.last_update > 5:  # 每5秒更新一次
        # 销售额随机波动
        st.session_state.dynamic_stats['sales'] = 2345678 + random.randint(-50000, 100000)
        # 分析次数递增
        st.session_state.dynamic_stats['analysis'] = 1234 + random.randint(-25, 50)
        # 准确率小幅波动
        st.session_state.dynamic_stats['accuracy'] = round(98.5 + random.uniform(-1, 2), 1)

        # 登录页统计数据
        st.session_state.dynamic_stats['login_stats']['data_analysis'] = 1234 + random.randint(-50, 100)
        st.session_state.dynamic_stats['login_stats']['accuracy'] = 99 + random.randint(-4, 0)

        st.session_state.last_update = current_time
        st.session_state.animation_key += 1


# 如果未登录，显示登录页面
if not st.session_state.authenticated:
    # 应用CSS
    st.markdown(complete_css, unsafe_allow_html=True)

    # 添加页面标识
    st.markdown('<div class="stApp" data-page="login"></div>', unsafe_allow_html=True)

    # 浮动几何图形
    st.markdown("""
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    """, unsafe_allow_html=True)

    # 登录卡片
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="decorative-dots"></div>

            <div class="logo-container">
                <div class="logo">📊</div>
                <h1 class="app-title">Trolli SAL</h1>
                <p style="color: #64748b; font-size: 0.95rem; line-height: 1.6; text-align: center;">
                    智能销售数据分析平台<br>洞察业务趋势 · 发现增长机会
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 数据统计展示
        st.markdown(f"""
        <div class="login-stats animate-in" key="{st.session_state.animation_key}">
            <div class="login-stat-item">
                <span class="login-stat-number">{st.session_state.dynamic_stats['login_stats']['data_analysis']}+</span>
                <span style="color: #64748b; font-size: 0.85rem;">数据分析</span>
            </div>
            <div class="login-stat-item">
                <span class="login-stat-number">{st.session_state.dynamic_stats['login_stats']['modules']}</span>
                <span style="color: #64748b; font-size: 0.85rem;">分析模块</span>
            </div>
            <div class="login-stat-item">
                <span class="login-stat-number">{st.session_state.dynamic_stats['login_stats']['monitoring']}/7</span>
                <span style="color: #64748b; font-size: 0.85rem;">实时监控</span>
            </div>
            <div class="login-stat-item">
                <span class="login-stat-number">{st.session_state.dynamic_stats['login_stats']['accuracy']}%</span>
                <span style="color: #64748b; font-size: 0.85rem;">准确率</span>
            </div>
        </div>
        """, unsafe_allow_html=True, help="数据实时更新中")

        # 登录表单
        with st.form("login_form"):
            st.markdown("#### 🔐 访问密码")
            password = st.text_input("", type="password", placeholder="请输入访问密码", label_visibility="collapsed")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.form_submit_button("登 录", use_container_width=True)

        if submit_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("🎉 登录成功！正在进入仪表盘...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")

        # 更新提示
        st.markdown("""
        <div style="text-align: center;">
            <div class="update-badge">🔄 每周四17:00刷新数据</div>
        </div>
        """, unsafe_allow_html=True)

    # 更新动态数据
    update_dynamic_stats()

    # 自动刷新
    time.sleep(5)
    st.rerun()

else:
    # 已登录 - 显示主页面
    st.markdown(complete_css, unsafe_allow_html=True)
    st.markdown('<div class="stApp" data-page="main"></div>', unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        # 侧边栏头部
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo-wrapper">
                <div class="sidebar-logo">📊</div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700;">Trolli SAL</div>
                    <div style="font-size: 0.85rem; opacity: 0.9;">数据分析平台</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🏠 主要功能")

        # 欢迎页面按钮
        if st.button("🏠 欢迎页面", use_container_width=True, key="welcome_btn"):
            st.session_state.current_page = 'welcome'

        st.markdown("---")
        st.markdown("##### 📈 分析模块")

        # 分析模块按钮
        if st.button("📦 产品组合分析", use_container_width=True):
            st.switch_page("pages/产品组合分析.py")

        if st.button("📊 预测库存分析", use_container_width=True):
            st.switch_page("pages/预测库存分析.py")

        if st.button("👥 客户依赖分析", use_container_width=True):
            st.switch_page("pages/客户依赖分析.py")

        if st.button("🎯 销售达成分析", use_container_width=True):
            st.switch_page("pages/销售达成分析.py")

        st.markdown("---")
        st.markdown("##### 👤 用户信息")

        st.markdown("""
        <div class="user-info-card">
            <strong style="color: #1e293b;">🎭 管理员</strong>
            <span style="color: #64748b; font-size: 0.9rem;">cira</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_page = 'welcome'
            st.rerun()

    # 主内容区 - 欢迎页面
    if st.session_state.current_page == 'welcome':
        # 欢迎标题
        st.markdown("""
        <div class="welcome-header">
            <h1 class="welcome-title">📊 欢迎使用 Trolli SAL</h1>
            <p style="font-size: 1.25rem; color: #64748b; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                您的智能销售数据分析助手，提供多维度的业务洞察，帮助您发现增长机会，优化销售策略
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 更新动态数据
        update_dynamic_stats()

        # 数据统计卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="stat-card animate-in" key="stat1-{st.session_state.animation_key}">
                <div class="stat-trend">+12.5%</div>
                <div class="stat-icon">💰</div>
                <div class="stat-value {'updating' if st.session_state.animation_key % 2 == 0 else ''}">
                    ¥{st.session_state.dynamic_stats['sales']:,}
                </div>
                <div class="stat-label">年度销售额</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-card animate-in" key="stat2-{st.session_state.animation_key}">
                <div class="stat-trend">+8.3%</div>
                <div class="stat-icon">📈</div>
                <div class="stat-value {'updating' if st.session_state.animation_key % 2 == 0 else ''}">
                    {st.session_state.dynamic_stats['analysis']}
                </div>
                <div class="stat-label">数据分析次数</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="stat-card animate-in">
                <div class="stat-trend">稳定</div>
                <div class="stat-icon">⏰</div>
                <div class="stat-value">24/7</div>
                <div class="stat-label">实时监控</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="stat-card animate-in" key="stat4-{st.session_state.animation_key}">
                <div class="stat-trend">+2.1%</div>
                <div class="stat-icon">🎯</div>
                <div class="stat-value {'updating' if st.session_state.animation_key % 2 == 0 else ''}">
                    {st.session_state.dynamic_stats['accuracy']}%
                </div>
                <div class="stat-label">预测准确率</div>
            </div>
            """, unsafe_allow_html=True)

        # 功能模块介绍
        st.markdown("""
        <h2 style="font-size: 1.75rem; font-weight: 700; color: #1e293b; margin: 3rem 0 2rem; text-align: center;">
            🚀 核心分析功能
        </h2>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="feature-card animate-in">
                <div class="feature-icon-wrapper">📦</div>
                <h3 class="feature-title">产品组合分析</h3>
                <p class="feature-description">
                    深度分析产品销售表现，通过BCG矩阵识别明星产品和问题产品，优化产品组合策略，提升整体盈利能力
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="feature-card animate-in" style="margin-top: 2rem;">
                <div class="feature-icon-wrapper">👥</div>
                <h3 class="feature-title">客户依赖分析</h3>
                <p class="feature-description">
                    评估客户依赖度和风险等级，识别关键客户群体，制定个性化维护策略，降低客户流失风险
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-card animate-in">
                <div class="feature-icon-wrapper">📊</div>
                <h3 class="feature-title">预测库存分析</h3>
                <p class="feature-description">
                    基于AI算法和历史数据，精准预测未来库存需求，优化库存管理，降低运营成本，提高资金使用效率
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="feature-card animate-in" style="margin-top: 2rem;">
                <div class="feature-icon-wrapper">🎯</div>
                <h3 class="feature-title">销售达成分析</h3>
                <p class="feature-description">
                    实时监控销售目标达成情况，分析业绩趋势，识别销售瓶颈，为策略调整提供数据支持
                </p>
            </div>
            """, unsafe_allow_html=True)

        # 更新提示和导航指引
        st.markdown("""
        <div style="text-align: center;">
            <div class="update-badge-large">
                🔄 数据每周四17:00自动更新
            </div>
            <div class="nav-hint">
                <span class="nav-hint-icon">👈</span> 
                使用左侧导航栏访问各个分析模块
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 自动刷新实现动态效果
        time.sleep(5)
        st.rerun()