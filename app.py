# app.py - 重写的美化版本
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

# 自定义CSS样式 - 完整美化版本
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式重置 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主容器背景 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
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
        }
        50% { 
            background-position: 100% 0%, 0% 100%, 80% 20%; 
        }
    }

    /* Streamlit容器样式 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        border-radius: 0;
        padding-top: 2rem;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stSidebar > div:first-child {
        background: transparent;
    }

    /* 侧边栏标题 */
    .stSidebar .element-container h3 {
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
    }

    /* 侧边栏选择框 */
    .stSidebar .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.8);
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    .stSidebar .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* 登录界面样式 */
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
        animation: slideUp 0.8s ease-out;
        position: relative;
        z-index: 100;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .login-header {
        margin-bottom: 2rem;
    }

    .logo-icon {
        font-size: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .login-title {
        font-size: 1.8rem;
        color: #2d3748;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .login-subtitle {
        color: #718096;
        font-size: 0.9rem;
    }

    /* 登录输入框 */
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
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }

    /* 登录按钮 */
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
        margin-top: 1rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* 欢迎页面样式 */
    .welcome-header {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
        z-index: 10;
    }

    .main-title {
        font-size: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        font-weight: 700;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        from { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5); 
            transform: scale(1);
        }
        to { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.8); 
            transform: scale(1.02);
        }
    }

    .welcome-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        animation: subtitleWave 3s ease-in-out infinite;
    }

    @keyframes subtitleWave {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    /* 统计卡片 */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: cardSlideUp 0.8s ease-out both;
    }

    .stat-card:nth-child(1) { animation-delay: 0.1s; }
    .stat-card:nth-child(2) { animation-delay: 0.2s; }
    .stat-card:nth-child(3) { animation-delay: 0.3s; }
    .stat-card:nth-child(4) { animation-delay: 0.4s; }

    @keyframes cardSlideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stat-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
    }

    .stat-label {
        color: #4a5568;
        font-size: 0.9rem;
    }

    /* 功能卡片 */
    .features-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        animation: cardSlideIn 0.8s ease-out both;
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
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.8s ease;
    }

    .feature-card:hover::before {
        left: 100%;
    }

    .feature-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    }

    .feature-card:nth-child(1) { animation-delay: 0.2s; }
    .feature-card:nth-child(2) { animation-delay: 0.4s; }
    .feature-card:nth-child(3) { animation-delay: 0.6s; }
    .feature-card:nth-child(4) { animation-delay: 0.8s; }

    @keyframes cardSlideIn {
        from {
            opacity: 0;
            transform: translateY(50px) rotateX(20deg);
        }
        to {
            opacity: 1;
            transform: translateY(0) rotateX(0deg);
        }
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #667eea, #764ba2, #81ecec);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: iconGradient 3s ease-in-out infinite;
        display: block;
    }

    @keyframes iconGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
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
    .update-notice {
        text-align: center;
        margin: 3rem auto;
        max-width: 600px;
    }

    .update-badge {
        display: inline-block;
        background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%);
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        animation: updateBadgeGlow 2s ease-in-out infinite alternate;
        transition: all 0.3s ease;
    }

    @keyframes updateBadgeGlow {
        from { 
            box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); 
        }
        to { 
            box-shadow: 0 5px 30px rgba(116, 185, 255, 0.6); 
        }
    }

    .update-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 30px rgba(116, 185, 255, 0.6);
    }

    /* 导航提示 */
    .navigation-hint {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
        margin-top: 2rem;
        animation: bounce 2s ease-in-out infinite;
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }

    /* 页脚 */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 成功/错误消息 */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
    }

    .stError {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }

        .stats-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        .features-container {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        .login-container {
            margin: 1rem;
            padding: 2rem 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    # 使用HTML创建美化的登录界面
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div class="logo-icon">📊</div>
            <h2 class="login-title">销售数据分析仪表盘</h2>
            <p class="login-subtitle">洞察业务趋势，发现增长机会</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 创建登录表单
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
    <div class="update-notice">
        <div class="update-badge">
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

    # 分析页面链接（对应您的pages目录中的文件）
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
st.markdown("""
<div class="welcome-header">
    <h1 class="main-title">
        📊 销售数据分析仪表盘
    </h1>
    <p class="welcome-subtitle">欢迎使用销售数据分析仪表盘，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>
""", unsafe_allow_html=True)

# 数据统计展示
st.markdown("""
<div class="stats-container">
    <div class="stat-card">
        <span class="stat-number">1000+</span>
        <div class="stat-label">数据分析</div>
    </div>
    <div class="stat-card">
        <span class="stat-number">4</span>
        <div class="stat-label">分析模块</div>
    </div>
    <div class="stat-card">
        <span class="stat-number">24</span>
        <div class="stat-label">小时监控</div>
    </div>
    <div class="stat-card">
        <span class="stat-number">99%</span>
        <div class="stat-label">准确率</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 功能模块介绍
st.markdown("""
<div class="features-container">
    <div class="feature-card">
        <span class="feature-icon">📦</span>
        <h3 class="feature-title">产品组合分析</h3>
        <p class="feature-description">
            分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
        </p>
    </div>

    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <h3 class="feature-title">预测库存分析</h3>
        <p class="feature-description">
            基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
        </p>
    </div>

    <div class="feature-card">
        <span class="feature-icon">👥</span>
        <h3 class="feature-title">客户依赖分析</h3>
        <p class="feature-description">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>

    <div class="feature-card">
        <span class="feature-icon">🎯</span>
        <h3 class="feature-title">销售达成分析</h3>
        <p class="feature-description">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# 更新提示和导航指引
st.markdown("""
<div class="update-notice">
    <div class="update-badge">
        🔄 数据每周一 17:00 自动更新
    </div>
</div>

<div class="navigation-hint">
    👈 请使用左侧导航栏访问各分析页面
</div>

<div class="footer">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据 | 为您提供专业的数据洞察服务</p>
</div>
""", unsafe_allow_html=True)