# app.py - 欢迎页
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

# 自定义CSS样式 - 更现代化的设计
st.markdown("""
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --accent-color: #f0f8ff;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --gray-color: #6c757d;
    }

    /* 主标题 */
    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2.5rem;
        padding-top: 2rem;
        font-weight: 600;
    }

    /* 欢迎卡片 */
    .welcome-card {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }

    /* 更新提示框 */
    .update-info {
        background-color: var(--accent-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid var(--primary-color);
        margin: 2.5rem 0;
        text-align: center;
        font-size: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* 导航提示卡片 */
    .nav-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .nav-title {
        font-size: 1.3rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
        font-weight: 600;
    }

    .nav-item {
        padding: 0.8rem 0;
        border-bottom: 1px solid #f5f5f5;
    }

    /* 页脚 */
    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eee;
        text-align: center;
        color: var(--gray-color);
        font-size: 0.9rem;
    }

    /* 登录框样式 */
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .login-header {
        text-align: center;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 600;
    }

    .login-btn {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        width: 100%;
        margin-top: 1rem;
        transition: background-color 0.3s;
    }

    .login-btn:hover {
        background-color: var(--secondary-color);
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="login-container">
            <h2 class="login-header">欢迎登录</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("请输入访问密码", type="password")

        # 登录按钮
        login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
        with login_col2:
            login_button = st.button("登 录", key="login_button")

        # 验证密码
        if login_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()

# 欢迎页面内容
st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

# 欢迎卡片
st.markdown("""
<div class="welcome-card">
    <h2 style="color: #1f3867; margin-bottom: 1rem;">欢迎使用销售数据分析仪表盘</h2>
    <p style="font-size: 1.1rem; color: #555;">本仪表盘提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>
""", unsafe_allow_html=True)

# 更新信息提示
st.markdown("""
<div class="update-info">
    <h3 style="margin-bottom: 0.5rem;">⏰ 数据每周一17:00更新</h3>
</div>
""", unsafe_allow_html=True)

# 导航指南
st.markdown("""
<div class="nav-card">
    <h3 class="nav-title">导航指南</h3>
    <div class="nav-item">
        <strong>销售总览</strong> - 查看销售业绩总体情况，包括销售趋势、区域分布等
    </div>
    <div class="nav-item">
        <strong>客户分析</strong> - 了解客户分布、贡献度、忠诚度等关键指标
    </div>
    <div class="nav-item">
        <strong>产品分析</strong> - 分析产品销售表现，包括BCG矩阵分析
    </div>
    <div class="nav-item">
        <strong>库存分析</strong> - 监控库存状况、周转率，优化库存管理
    </div>
    <div class="nav-item">
        <strong>物料分析</strong> - 分析物料使用效率和费用控制
    </div>
    <div class="nav-item">
        <strong>新品分析</strong> - 追踪新产品市场表现和渗透率
    </div>
</div>
<p style="text-align: center; margin-top: 1rem; color: #666;">请使用左侧导航栏访问各分析页面</p>
""", unsafe_allow_html=True)

# 页脚
st.markdown("""
<div class="footer">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)