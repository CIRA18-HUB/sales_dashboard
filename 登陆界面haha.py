# app.py - 修复版 Streamlit 应用
import streamlit as st
from datetime import datetime
import time
import random
import math

# 设置页面配置
st.set_page_config(
    page_title="Trolli SAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # 确保侧边栏展开
)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'stats_initialized' not in st.session_state:
    st.session_state.stats_initialized = False
    st.session_state.stat1_value = 1000
    st.session_state.stat2_value = 4
    st.session_state.stat3_value = 24
    st.session_state.stat4_value = 99
    st.session_state.last_update = time.time()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "welcome"

# 隐藏Streamlit默认元素 - 修复版
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
    
    /* 确保侧边栏可见 - 移除可能隐藏侧边栏的CSS */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 主要CSS样式 - 增强版
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
    
    /* 侧边栏样式 - 确保可见性 */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
        z-index: 10;
    }
    
    /* 侧边栏按钮样式 */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        color: white;
        text-align: left;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        margin-bottom: 0.3rem;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateX(5px) scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 标题样式 */
    .sidebar-title {
        color: #2d3748;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.3rem;
    }
    
    .sidebar-section {
        color: #2d3748;
        font-weight: 600;
        padding: 0 1rem;
        margin: 1rem 0 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* 用户信息框 */
    .user-info {
        background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
        border: 1px solid #38d9a9;
        border-radius: 10px;
        padding: 1rem;
        margin: 0 1rem;
        color: #2d3748;
        box-shadow: 0 2px 5px rgba(56, 217, 169, 0.2);
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
    
    /* 成功/错误消息样式 */
    .stSuccess, .stError {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
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
                st.success("🎉 登录成功！正在进入仪表盘...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")
        
        # 更新提示
        st.markdown("""
        <div style="text-align: center; margin: 3rem auto;">
            <div class="update-badge">
                🔄 每周四17:00刷新数据
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# 主页面 - 侧边栏（确保在登录后显示）
with st.sidebar:
    st.markdown('<h3 class="sidebar-title">📊 Trolli SAL</h3>', unsafe_allow_html=True)
    st.markdown('<h4 class="sidebar-section">🏠 主要功能</h4>', unsafe_allow_html=True)
    
    if st.button("🏠 欢迎页面", use_container_width=True):
        st.session_state.current_page = "welcome"
        st.rerun()
    
    st.markdown("---")
    st.markdown('<h4 class="sidebar-section">📈 分析模块</h4>', unsafe_allow_html=True)
    
    # 模拟页面跳转（在实际部署中使用 st.switch_page）
    if st.button("📦 产品组合分析", use_container_width=True):
        st.session_state.current_page = "product_analysis"
        st.info("📦 产品组合分析页面（演示版本）")
    
    if st.button("📊 预测库存分析", use_container_width=True):
        st.session_state.current_page = "inventory_forecast"
        st.info("📊 预测库存分析页面（演示版本）")
    
    if st.button("👥 客户依赖分析", use_container_width=True):
        st.session_state.current_page = "customer_analysis"
        st.info("👥 客户依赖分析页面（演示版本）")
    
    if st.button("🎯 销售达成分析", use_container_width=True):
        st.session_state.current_page = "sales_achievement"
        st.info("🎯 销售达成分析页面（演示版本）")
    
    st.markdown("---")
    st.markdown('<h4 class="sidebar-section">👤 用户信息</h4>', unsafe_allow_html=True)
    st.markdown("""
    <div class="user-info">
        <strong>管理员</strong><br>
        cira<br>
        <small>登录时间: {}</small>
    </div>
    """.format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
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
        st.session_state.stat2_value = 4  # 固定值
        st.session_state.stat3_value = 24  # 固定值
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

# 功能模块介绍
st.markdown("<br><br>", unsafe_allow_html=True)

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">👥</span>
        <h3 class="feature-title">客户依赖分析</h3>
        <p class="feature-description">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🎯</span>
        <h3 class="feature-title">销售达成分析</h3>
        <p class="feature-description">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
    """, unsafe_allow_html=True)

# 更新提示和导航
st.markdown("""
<div style="text-align: center; margin: 3rem auto;">
    <div class="update-badge">
        🔄 每周四17:00刷新数据
    </div>
</div>

<div class="navigation-hint">
    👈 请使用左侧导航栏访问各分析页面
</div>

<div class="footer">
    <p>Trolli SAL | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周四17:00刷新数据 | 将枯燥数据变好看</p>
</div>
""", unsafe_allow_html=True)

# 页面状态显示（调试用）
if st.session_state.get('current_page') != 'welcome':
    st.info(f"当前页面: {st.session_state.get('current_page', 'welcome')}")

# 自动刷新机制（可选，可能导致性能问题）
# if st.session_state.authenticated:
#     # 每3秒刷新一次数据
#     time.sleep(0.1)
#     if is_updated:
#         st.rerun()
