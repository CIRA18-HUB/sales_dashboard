# app.py - 完整版本（包含动画和强力隐藏）
import streamlit as st
from datetime import datetime
import os

# 设置页面配置
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 强力隐藏Streamlit默认元素 + 完整动画CSS
complete_css = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 强力隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}

    /* 尝试隐藏应用标题的多种方法 */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .main > div:first-child {padding-top: 0rem !important;}

    /* 如果上面都不行，至少让它透明 */
    .stApp > div:first-child {
        background: transparent !important;
        backdrop-filter: blur(0px) !important;
    }

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 + 动画 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景粒子效果 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120, 119, 198, 0.2) 0%, transparent 60%);
        animation: backgroundMove 10s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes backgroundMove {
        0%, 100% { 
            background-position: 0% 0%, 100% 100%, 50% 50%; 
            background-size: 200% 200%, 150% 150%, 300% 300%;
        }
        33% { 
            background-position: 100% 0%, 0% 50%, 80% 20%; 
            background-size: 300% 300%, 200% 200%, 250% 250%;
        }
        66% { 
            background-position: 50% 100%, 50% 0%, 20% 80%; 
            background-size: 250% 250%, 300% 300%, 200% 200%;
        }
    }

    /* 添加浮动粒子 */
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.2), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.3), transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: particleFloat 20s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes particleFloat {
        0% { transform: translateY(100vh) translateX(0); }
        100% { transform: translateY(-100vh) translateX(100px); }
    }

    /* Streamlit容器样式 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        border-radius: 0;
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏美化 + 动画 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }

    @keyframes slideInLeft {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .stSidebar > div:first-child {
        background: transparent;
        padding-top: 1rem;
    }

    /* 侧边栏标题动画 */
    .stSidebar .stMarkdown h3 {
        color: #2d3748;
        font-weight: 600;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titlePulse 3s ease-in-out infinite;
    }

    @keyframes titlePulse {
        0%, 100% { 
            transform: scale(1);
            filter: brightness(1);
        }
        50% { 
            transform: scale(1.05);
            filter: brightness(1.2);
        }
    }

    .stSidebar .stMarkdown h4 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.8rem;
        padding: 0.5rem 0;
        animation: fadeInUp 0.6s ease-out both;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* 侧边栏按钮动画 */
    .stSidebar .stButton > button {
        width: 100%;
        background: transparent;
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        color: #4a5568;
        text-align: left;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.9rem;
        position: relative;
        overflow: hidden;
    }

    .stSidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s ease;
    }

    .stSidebar .stButton > button:hover::before {
        left: 100%;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: #667eea;
        color: #667eea;
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    /* 登录容器动画 */
    .login-container {
        max-width: 450px;
        margin: 3rem auto;
        padding: 3rem 2.5rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        text-align: center;
        animation: slideUpBounce 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
        overflow: hidden;
    }

    @keyframes slideUpBounce {
        0% {
            opacity: 0;
            transform: translateY(100px) scale(0.8) rotateX(30deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-10px) scale(1.05) rotateX(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    /* 登录表单动画 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        transform: translateY(-3px) scale(1.02);
        background: rgba(255, 255, 255, 1);
    }

    /* 登录按钮动画 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transition: width 0.6s, height 0.6s, top 0.6s, left 0.6s;
        transform: translate(-50%, -50%);
    }

    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
    }

    /* 欢迎页面标题动画 */
    .welcome-title {
        animation: titleGlowPulse 4s ease-in-out infinite;
    }

    @keyframes titleGlowPulse {
        0%, 100% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
            transform: scale(1);
        }
        25% {
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 30px rgba(255, 255, 255, 0.7);
            transform: scale(1.01);
        }
        50% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
            transform: scale(1.02);
        }
        75% {
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 30px rgba(255, 255, 255, 0.7);
            transform: scale(1.01);
        }
    }

    .welcome-subtitle {
        animation: subtitleFloat 6s ease-in-out infinite;
    }

    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-5px) rotate(0.5deg); }
        50% { transform: translateY(-8px) rotate(0deg); }
        75% { transform: translateY(-3px) rotate(-0.5deg); }
    }

    /* 统计卡片动画 */
    .stat-card {
        animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) both;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stat-card:hover {
        transform: translateY(-15px) scale(1.05) rotateY(5deg);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    }

    @keyframes cardSlideUpStagger {
        0% {
            opacity: 0;
            transform: translateY(60px) scale(0.8) rotateX(30deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-10px) scale(1.05) rotateX(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    /* 功能卡片动画 */
    .feature-card {
        animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) both;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 1s ease;
    }

    .feature-card:hover::before {
        left: 100%;
    }

    .feature-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: cardRotateHover 8s linear infinite paused;
        pointer-events: none;
    }

    .feature-card:hover::after {
        animation-play-state: running;
    }

    @keyframes cardRotateHover {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .feature-card:hover {
        transform: translateY(-20px) scale(1.05) rotateX(5deg) rotateY(5deg);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.25);
    }

    @keyframes featureCardFloat {
        0% {
            opacity: 0;
            transform: translateY(80px) scale(0.8) rotateX(45deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-15px) scale(1.05) rotateX(-10deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    /* 图标动画 */
    .feature-icon {
        animation: iconColorShift 4s ease-in-out infinite, iconFloat 6s ease-in-out infinite;
    }

    @keyframes iconColorShift {
        0%, 100% { 
            background-position: 0% 50%;
            filter: hue-rotate(0deg);
        }
        25% { 
            background-position: 50% 50%;
            filter: hue-rotate(90deg);
        }
        50% { 
            background-position: 100% 50%;
            filter: hue-rotate(180deg);
        }
        75% { 
            background-position: 50% 50%;
            filter: hue-rotate(270deg);
        }
    }

    @keyframes iconFloat {
        0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
        25% { transform: translateY(-8px) rotate(3deg) scale(1.1); }
        50% { transform: translateY(-5px) rotate(0deg) scale(1.05); }
        75% { transform: translateY(-3px) rotate(-2deg) scale(1.08); }
    }

    /* 更新徽章动画 */
    .update-badge {
        animation: badgeGlowPulse 3s ease-in-out infinite, badgeFloat 5s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }

    .update-badge::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: badgeSweep 4s ease-in-out infinite;
    }

    @keyframes badgeSweep {
        0%, 100% { left: -100%; }
        50% { left: 100%; }
    }

    @keyframes badgeGlowPulse {
        0%, 100% { 
            box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        }
        50% { 
            box-shadow: 0 10px 40px rgba(116, 185, 255, 0.8);
        }
    }

    @keyframes badgeFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        33% { transform: translateY(-8px) rotate(1deg); }
        66% { transform: translateY(-12px) rotate(-1deg); }
    }

    .update-badge:hover {
        transform: scale(1.1) rotate(3deg);
        animation-duration: 1s;
    }

    /* 导航提示动画 */
    .navigation-hint {
        animation: bounceArrow 3s ease-in-out infinite;
    }

    @keyframes bounceArrow {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0) translateX(0); }
        10% { transform: translateY(-8px) translateX(-5px); }
        30% { transform: translateY(-5px) translateX(-8px); }
        40% { transform: translateY(-12px) translateX(-3px); }
        60% { transform: translateY(-8px) translateX(-6px); }
    }

    /* 成功/错误消息动画 */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        animation: alertSlideIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes alertSlideIn {
        0% {
            opacity: 0;
            transform: translateY(-30px) scale(0.8);
        }
        60% {
            opacity: 1;
            transform: translateY(5px) scale(1.05);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
    }

    .stError {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }

    /* 响应式动画调整 */
    @media (max-width: 768px) {
        .welcome-title {
            animation-duration: 6s;
        }

        .feature-card:hover {
            transform: translateY(-10px) scale(1.02);
        }

        .stat-card:hover {
            transform: translateY(-8px) scale(1.02);
        }
    }
</style>
"""

st.markdown(complete_css, unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    # 登录页面布局
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 3rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; animation: titlePulse 2s infinite;">📊</div>
            <h2 style="font-size: 1.8rem; color: #2d3748; margin-bottom: 0.5rem; font-weight: 600;">销售数据分析仪表盘</h2>
            <p style="color: #718096; font-size: 0.9rem; margin-bottom: 2rem;">洞察业务趋势，发现增长机会</p>
        </div>
        """, unsafe_allow_html=True)

        # 登录表单
        with st.form("login_form"):
            st.markdown("#### 🔐 请输入访问密码")
            password = st.text_input("密码", type="password", placeholder="请输入访问密码")
            submit_button = st.form_submit_button("登 录", use_container_width=True)

        if submit_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("🎉 登录成功！正在进入仪表盘...")
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")

        # 更新提示
        st.markdown("""
        <div style="text-align: center; margin: 3rem auto; max-width: 600px;">
            <div class="update-badge" style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem;">
                🕐 数据每周一 17:00 自动更新
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# 认证成功后的主页面
# 侧边栏导航
with st.sidebar:
    st.markdown("### 📊 销售数据分析仪表盘")

    # 主要功能
    st.markdown("#### 🏠 主要功能")

    # 导航菜单
    if st.button("🏠 欢迎页面", use_container_width=True):
        st.session_state.current_page = "welcome"

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    # 分析页面链接
    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    if st.button("📊 预测库存分析", use_container_width=True):
        st.switch_page("pages/预测库存分析.py")

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")

    # 用户信息
    st.markdown("#### 👤 用户信息")
    st.info("**管理员**  \n系统管理员")

    # 登出按钮
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# 主内容区 - 欢迎页面
welcome_content = """
<div style="text-align: center; margin-bottom: 3rem; position: relative; z-index: 10;">
    <h1 class="welcome-title" style="font-size: 3rem; color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); margin-bottom: 1rem; font-weight: 700;">
        📊 销售数据分析仪表盘
    </h1>
    <p class="welcome-subtitle" style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 2rem;">欢迎使用销售数据分析仪表盘，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>
"""
st.markdown(welcome_content, unsafe_allow_html=True)

# 数据统计展示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.1s;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">1000+</span>
        <div style="color: #4a5568; font-size: 0.9rem;">数据分析</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.2s;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">4</span>
        <div style="color: #4a5568; font-size: 0.9rem;">分析模块</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.3s;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">24</span>
        <div style="color: #4a5568; font-size: 0.9rem;">小时监控</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.4s;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">99%</span>
        <div style="color: #4a5568; font-size: 0.9rem;">准确率</div>
    </div>
    """, unsafe_allow_html=True)

# 功能模块介绍
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin-bottom: 2rem; animation-delay: 0.2s; position: relative; overflow: hidden;">
        <span class="feature-icon" style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; display: block;">📦</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">产品组合分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.6s; position: relative; overflow: hidden;">
        <span class="feature-icon" style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; display: block;">👥</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">客户依赖分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin-bottom: 2rem; animation-delay: 0.4s; position: relative; overflow: hidden;">
        <span class="feature-icon" style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; display: block;">📊</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">预测库存分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation-delay: 0.8s; position: relative; overflow: hidden;">
        <span class="feature-icon" style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; display: block;">🎯</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">销售达成分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
    """, unsafe_allow_html=True)

# 更新提示和导航指引
st.markdown("""
<div style="text-align: center; margin: 3rem auto; max-width: 600px;">
    <div class="update-badge" style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem; position: relative; overflow: hidden;">
        🔄 数据每周一 17:00 自动更新
    </div>
</div>

<div class="navigation-hint" style="text-align: center; color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; margin-top: 2rem;">
    👈 请使用左侧导航栏访问各分析页面
</div>

<div style="text-align: center; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据 | 为您提供专业的数据洞察服务</p>
</div>
""", unsafe_allow_html=True)