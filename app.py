# app.py - 修复版本
import streamlit as st
from datetime import datetime
import os

# 设置页面配置 - 关键是这里要隐藏默认标题
st.set_page_config(
    page_title="销售数据分析仪表盘",
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

    /* 隐藏顶部应用标题 */
    .stAppHeader {display: none;}

    /* 隐藏Deploy按钮 */
    .stDeployButton {display: none;}

    /* 隐藏右上角菜单 */
    .stToolbar {display: none;}

    /* 移除顶部边距 */
    .main > div:first-child {
        padding-top: 0rem;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 主要CSS样式
main_css = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式重置 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 动态背景效果 */
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
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stSidebar > div:first-child {
        background: transparent;
        padding-top: 1rem;
    }

    /* 侧边栏标题 */
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
    }

    .stSidebar .stMarkdown h4 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.8rem;
        padding: 0.5rem 0;
    }

    /* 侧边栏按钮 */
    .stSidebar .stButton > button {
        width: 100%;
        background: transparent;
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        color: #4a5568;
        text-align: left;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: #667eea;
        color: #667eea;
        transform: translateX(5px);
    }

    /* 登录容器 */
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
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
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
</style>
"""
st.markdown(main_css, unsafe_allow_html=True)

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
            <div style="font-size: 3rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; animation: pulse 2s infinite;">📊</div>
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
            <div style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem; box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); animation: updateBadgeGlow 2s ease-in-out infinite alternate;">
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
    <h1 style="font-size: 3rem; color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); margin-bottom: 1rem; font-weight: 700; animation: titleGlow 3s ease-in-out infinite alternate;">
        📊 销售数据分析仪表盘
    </h1>
    <p style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 2rem; animation: subtitleWave 3s ease-in-out infinite;">欢迎使用销售数据分析仪表盘，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>

<style>
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

@keyframes subtitleWave {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}
</style>
"""
st.markdown(welcome_content, unsafe_allow_html=True)

# 数据统计展示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; animation: cardSlideUp 0.8s ease-out 0.1s both;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">1000+</span>
        <div style="color: #4a5568; font-size: 0.9rem;">数据分析</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; animation: cardSlideUp 0.8s ease-out 0.2s both;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">4</span>
        <div style="color: #4a5568; font-size: 0.9rem;">分析模块</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; animation: cardSlideUp 0.8s ease-out 0.3s both;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">24</span>
        <div style="color: #4a5568; font-size: 0.9rem;">小时监控</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; animation: cardSlideUp 0.8s ease-out 0.4s both;">
        <span style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">99%</span>
        <div style="color: #4a5568; font-size: 0.9rem;">准确率</div>
    </div>
    """, unsafe_allow_html=True)

# 功能模块介绍
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideIn 0.8s ease-out 0.2s both; position: relative; overflow: hidden; margin-bottom: 2rem;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconGradient 3s ease-in-out infinite; display: block;">📦</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">产品组合分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideIn 0.8s ease-out 0.6s both; position: relative; overflow: hidden;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconGradient 3s ease-in-out infinite; display: block;">👥</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">客户依赖分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideIn 0.8s ease-out 0.4s both; position: relative; overflow: hidden; margin-bottom: 2rem;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconGradient 3s ease-in-out infinite; display: block;">📊</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">预测库存分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideIn 0.8s ease-out 0.8s both; position: relative; overflow: hidden;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconGradient 3s ease-in-out infinite; display: block;">🎯</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">销售达成分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
    """, unsafe_allow_html=True)

# 更新提示和导航指引
st.markdown("""
<div style="text-align: center; margin: 3rem auto; max-width: 600px;">
    <div style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem; box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); animation: updateBadgeGlow 2s ease-in-out infinite alternate;">
        🔄 数据每周一 17:00 自动更新
    </div>
</div>

<div style="text-align: center; color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; margin-top: 2rem; animation: bounce 2s ease-in-out infinite;">
    👈 请使用左侧导航栏访问各分析页面
</div>

<div style="text-align: center; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据 | 为您提供专业的数据洞察服务</p>
</div>

<style>
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

@keyframes iconGradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes updateBadgeGlow {
    from { 
        box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); 
    }
    to { 
        box-shadow: 0 5px 30px rgba(116, 185, 255, 0.6); 
    }
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}
</style>
""", unsafe_allow_html=True)