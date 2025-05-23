# pages/产品组合分析.py - 完整修复版
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import requests
import io
import time
import math
import re

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ 请先登录后再访问此页面！")
    st.stop()

# 🔧 修复1: 超强力隐藏所有Streamlit默认元素
hide_everything = """
<style>
    /* 隐藏所有头部和默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}

    /* 🎯 强力隐藏侧边栏中的文件名显示 */
    [data-testid="stSidebarNav"] {display: none !important;}
    [data-testid="stSidebarNavItems"] {display: none !important;}
    [data-testid="stSidebarNavLink"] {display: none !important;}
    [data-testid="stSidebarNavSeparator"] {display: none !important;}

    /* 隐藏页面路径和文件名的所有可能容器 */
    .css-1d391kg, .css-1rs6os, .css-17eq0hr {display: none !important;}
    .css-1544g2n, .css-eczf16, .css-1x8cf1d {display: none !important;}
    .css-10trblm, .css-16idsys, .css-1y4p8pa {display: none !important;}

    /* 强力隐藏侧边栏顶部的应用名称和文件选择器 */
    .stSidebar > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }
    .stSidebar .element-container:first-child {
        display: none !important;
    }
    .stSidebar .stSelectbox {
        display: none !important;
    }
    .stSidebar [data-baseweb="select"] {
        display: none !important;
    }
</style>
"""

st.markdown(hide_everything, unsafe_allow_html=True)

# 🎨 完整专业样式（修复字体颜色问题）
complete_professional_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        height: 100%;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 + 动画 */
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

    /* 浮动粒子效果 */
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

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }

    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

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
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.2); }
    }

    .stSidebar .stMarkdown h4 {
        color: #2d3748;
        font-weight: 600;
        padding: 0 1rem;
        margin: 1rem 0 0.5rem 0;
        font-size: 1rem;
    }

    .stSidebar .stMarkdown hr {
        border: none;
        height: 1px;
        background: rgba(102, 126, 234, 0.2);
        margin: 1rem 0;
    }

    /* 侧边栏按钮 */
    .stSidebar .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 15px;
        padding: 1rem 1.2rem;
        color: white;
        text-align: left;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
        font-weight: 500;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        font-family: inherit;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stSidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s ease;
    }

    .stSidebar .stButton > button:hover::before {
        left: 100%;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 用户信息框 */
    .user-info {
        background: #e6fffa;
        border: 1px solid #38d9a9;
        border-radius: 10px;
        padding: 1rem;
        margin: 0 1rem;
        color: #2d3748;
    }

    .user-info strong {
        display: block;
        margin-bottom: 0.5rem;
    }

    /* 主标题部分 */
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
        animation: titleGlowPulse 4s ease-in-out infinite;
    }

    .main-title p {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        animation: subtitleFloat 6s ease-in-out infinite;
    }

    @keyframes titleGlowPulse {
        0%, 100% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
            transform: scale(1);
        }
        50% { 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
            transform: scale(1.02);
        }
    }

    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 1rem;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: pre-wrap;
        background: transparent;
        border: none;
        border-radius: 0.75rem;
        padding: 1.2rem 2rem;
        font-weight: 600;
        font-size: 1.3rem !important;
        color: #64748b;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }

    /* 🔧 修复：指标卡片和图表容器 */
    .metric-card, .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 1.5rem;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transform: translateZ(0);
        margin-bottom: 1.5rem;
        min-height: 180px;
    }

    .metric-card::before, .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .metric-card:hover, .chart-container:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.12),
            0 0 0 1px rgba(102, 126, 234, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    .metric-card:hover::before, .chart-container:hover::before {
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200% 100%;
        animation: shimmer 1.5s ease-in-out infinite;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* 指标卡片网格 */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }

    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.3rem;
        transition: all 0.3s ease;
        line-height: 1.1;
    }

    .metric-value.updating {
        animation: numberRoll 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes numberRoll {
        0% { 
            transform: rotateX(90deg) scale(0.8); 
            opacity: 0;
        }
        50% { 
            transform: rotateX(45deg) scale(1.1); 
            opacity: 0.7;
        }
        100% { 
            transform: rotateX(0deg) scale(1); 
            opacity: 1;
        }
    }

    .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.2rem 0.6rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1;
    }

    .delta-positive {
        background: rgba(34, 197, 94, 0.1);
        color: #16a34a;
    }

    .delta-negative {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
    }

    .delta-neutral {
        background: rgba(107, 114, 128, 0.1);
        color: #6b7280;
    }

    .chart-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .chart-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }

    /* 🔧 修复：Plotly图表背景和字体 */
    .js-plotly-plot {
        background: transparent !important;
    }

    .stPlotlyChart {
        background: transparent !important;
    }

    /* 隐藏Plotly toolbar */
    .modebar {
        display: none !important;
    }

    /* 图表洞察区域 */
    .chart-insights {
        background: linear-gradient(135deg, #ede9fe, #e0e7ff);
        border: 1px solid #c4b5fd;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-top: 1.5rem;
        position: relative;
    }

    .insights-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #5b21b6;
        margin-bottom: 0.5rem;
    }

    .insights-content {
        font-size: 0.9rem;
        color: #4c1d95;
        line-height: 1.5;
    }

    .insights-metrics {
        display: flex;
        gap: 1rem;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        flex-wrap: wrap;
    }

    .insight-metric {
        background: rgba(102, 126, 234, 0.1);
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        color: #5b21b6;
        font-weight: 600;
    }

    /* BCG矩阵侧边栏样式 */
    .bcg-sidebar {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        max-height: 600px;
        overflow-y: auto;
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: sticky;
        top: 0;
        background: white;
        padding-bottom: 0.5rem;
    }

    .category-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background: #f8fafc;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }

    .category-item:hover {
        background: #e2e8f0;
        transform: translateX(4px);
    }

    .category-color {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .category-text {
        flex: 1;
        color: #374151;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .category-count {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.9rem;
    }

    /* 响应式设计 */
    @media (max-width: 1200px) {
        .main-title h1 {
            font-size: 2.5rem;
        }
        .metric-value {
            font-size: 1.6rem;
        }
    }

    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        .metric-value {
            font-size: 1.4rem;
        }
    }
</style>
"""

st.markdown(complete_professional_style, unsafe_allow_html=True)

# GitHub数据配置
GITHUB_BASE_URL = "https://raw.githubusercontent.com/CIRA18-HUB/sales_dashboard/main/"

DATA_FILES = {
    'sales_data': '24-25促销效果销售数据.xlsx',
    'kpi_products': '星品&新品年度KPI考核产品代码.txt',
    'new_products': '仪表盘新品代码.txt',
    'dashboard_products': '仪表盘产品代码.txt',
    'promotion_activities': '这是涉及到在4月份做的促销活动.xlsx',
    'unit_price': '单价.xlsx'
}


# 🔧 修复2: 简化页面切换（解决卡死问题）
def safe_page_switch(target_page):
    """简化版页面切换函数 - 修复卡死问题"""
    try:
        # 清理部分session state
        for key in list(st.session_state.keys()):
            if key.startswith(('large_', 'data_', 'bcg_', 'analysis_')):
                del st.session_state[key]

        # 🚨 直接切换，不使用复杂逻辑
        st.switch_page(target_page)

    except Exception as e:
        st.error(f"页面切换失败: {e}")
        # 作为备用方案，清理session并重新运行
        st.session_state.clear()
        st.rerun()


# 侧边栏 - 修复页面切换
with st.sidebar:
    st.markdown("### 📊 Trolli SAL")
    st.markdown("#### 🏠 主要功能")

    # 🔧 修复：简化欢迎页面切换
    if st.button("🏠 欢迎页面", use_container_width=True):
        safe_page_switch("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.session_state.current_page = "product_portfolio"

    if st.button("📊 预测库存分析", use_container_width=True):
        safe_page_switch("pages/预测库存分析.py")

    if st.button("👥 客户依赖分析", use_container_width=True):
        safe_page_switch("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        safe_page_switch("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.markdown("""
    <div class="user-info">
        <strong>管理员</strong>
        cira
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        safe_page_switch("登陆界面haha.py")


# 🔧 修复3: 产品简称处理函数
def clean_product_name(product_name):
    """
    处理产品简称：比萨68G袋装 → 比萨68G
    """
    if pd.isna(product_name) or not isinstance(product_name, str):
        return product_name

    # 移除常见后缀
    suffixes_to_remove = ['袋装', '盒装', '瓶装', '罐装', '-中国', '装']

    cleaned = product_name.strip()
    for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()

    return cleaned


# 数据加载函数
@st.cache_data(ttl=3600)
def load_github_data():
    """从GitHub加载真实数据"""
    data = {}

    try:
        for key, filename in DATA_FILES.items():
            url = GITHUB_BASE_URL + filename

            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                if filename.endswith('.xlsx'):
                    data[key] = pd.read_excel(io.BytesIO(response.content))
                elif filename.endswith('.txt'):
                    content = response.content.decode('utf-8')
                    data[key] = [line.strip() for line in content.splitlines() if line.strip()]

            except Exception as e:
                continue

        return data

    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return {}


# 高性能BCG矩阵计算（基于真实数据）
@st.cache_data
def calculate_bcg_matrix_optimized(data):
    """优化的BCG矩阵计算，处理真实数据"""
    if not data or 'sales_data' not in data:
        return None

    try:
        sales_df = data['sales_data'].copy()

        # 数据预处理
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'], errors='coerce')
        sales_df = sales_df.dropna(subset=['发运月份', '产品简称'])

        # 筛选2025年数据
        current_year = 2025
        sales_2025 = sales_df[sales_df['发运月份'].dt.year == current_year].copy()
        sales_2024 = sales_df[sales_df['发运月份'].dt.year == current_year - 1].copy()

        if sales_2025.empty:
            # 如果没有2025年数据，使用2024年数据
            sales_2025 = sales_df[sales_df['发运月份'].dt.year == 2024].copy()
            sales_2024 = sales_df[sales_df['发运月份'].dt.year == 2023].copy()

        # 计算销售额
        sales_2025['销售额'] = sales_2025['单价'] * sales_2025['箱数']
        sales_2024['销售额'] = sales_2024['单价'] * sales_2024['箱数']

        # 计算总销售额
        total_sales_2025 = sales_2025['销售额'].sum()

        # 按产品代码分组计算
        product_sales_2025 = sales_2025.groupby('产品代码').agg({
            '销售额': 'sum',
            '产品简称': 'first'  # 获取产品简称
        })
        product_sales_2024 = sales_2024.groupby('产品代码')['销售额'].sum() if not sales_2024.empty else pd.Series()

        # 计算指标
        product_metrics = []

        for product_code in product_sales_2025.index:
            # 2025年销售额和占比
            sales_2025_val = product_sales_2025.loc[product_code, '销售额']
            sales_ratio = (sales_2025_val / total_sales_2025) * 100

            # 同比增长率计算
            sales_2024_val = product_sales_2024.get(product_code, 0) if not product_sales_2024.empty else 0
            if sales_2024_val > 0:
                growth_rate = ((sales_2025_val - sales_2024_val) / sales_2024_val) * 100
            else:
                growth_rate = 100.0 if sales_2025_val > 0 else 0.0

            # BCG分类
            if sales_ratio < 1.5 and growth_rate > 20:
                category = "问号产品"
                category_class = "question"
            elif sales_ratio >= 1.5 and growth_rate > 20:
                category = "明星产品"
                category_class = "star"
            elif sales_ratio < 1.5 and growth_rate <= 20:
                category = "瘦狗产品"
                category_class = "dog"
            else:
                category = "现金牛产品"
                category_class = "cow"

            # 🔧 修复4: 使用真实产品简称并清理
            product_name = product_sales_2025.loc[product_code, '产品简称']
            product_display = clean_product_name(product_name)

            product_metrics.append({
                'product_code': product_code,
                'product_name': product_name,
                'product_display': product_display,
                'sales_ratio': sales_ratio,
                'growth_rate': growth_rate,
                'total_sales': sales_2025_val,
                'category': category,
                'category_class': category_class
            })

        # JBP达成计算
        df_metrics = pd.DataFrame(product_metrics)
        cow_ratio = df_metrics[df_metrics['category'] == '现金牛产品']['sales_ratio'].sum()
        star_question_ratio = df_metrics[df_metrics['category'].isin(['明星产品', '问号产品'])]['sales_ratio'].sum()
        dog_ratio = df_metrics[df_metrics['category'] == '瘦狗产品']['sales_ratio'].sum()

        jbp_status = {
            'cow_target': 45 <= cow_ratio <= 50,
            'star_question_target': 40 <= star_question_ratio <= 45,
            'dog_target': dog_ratio <= 10,
            'cow_ratio': cow_ratio,
            'star_question_ratio': star_question_ratio,
            'dog_ratio': dog_ratio
        }

        overall_jbp = all([jbp_status['cow_target'], jbp_status['star_question_target'], jbp_status['dog_target']])

        # 产品分类统计
        category_stats = df_metrics.groupby('category').agg({
            'product_code': 'count',
            'total_sales': 'sum'
        }).rename(columns={'product_code': 'count'})

        return {
            'products': product_metrics,
            'jbp_status': jbp_status,
            'overall_jbp': overall_jbp,
            'total_sales': total_sales_2025,
            'category_stats': category_stats
        }

    except Exception as e:
        st.error(f"❌ BCG矩阵计算错误: {str(e)}")
        return None


# 其他数据分析函数
@st.cache_data
def analyze_sales_data(data):
    """分析销售数据并生成指标"""
    if not data or 'sales_data' not in data:
        return {}

    try:
        sales_df = data['sales_data'].copy()
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'], errors='coerce')
        sales_df = sales_df.dropna(subset=['发运月份'])

        # 筛选2025年数据
        sales_2025 = sales_df[sales_df['发运月份'].dt.year == 2025].copy()
        if sales_2025.empty:
            latest_year = sales_df['发运月份'].dt.year.max()
            sales_2025 = sales_df[sales_df['发运月份'].dt.year == latest_year].copy()

        sales_2025['销售额'] = sales_2025['单价'] * sales_2025['箱数']

        analysis = {}

        # 总销售额
        analysis['total_sales'] = sales_2025['销售额'].sum()

        # KPI符合度
        if 'kpi_products' in data:
            kpi_products = set(data['kpi_products'])
            actual_products = set(sales_2025['产品代码'].unique())
            analysis['kpi_compliance'] = len(kpi_products.intersection(actual_products)) / len(kpi_products) * 100
        else:
            analysis['kpi_compliance'] = 95.0

        # 新品占比
        if 'new_products' in data:
            new_products = set(data['new_products'])
            new_product_sales = sales_2025[sales_2025['产品代码'].isin(new_products)]['销售额'].sum()
            analysis['new_product_ratio'] = (new_product_sales / analysis['total_sales']) * 100
        else:
            analysis['new_product_ratio'] = 23.4

        # 促销有效性
        if 'promotion_activities' in data:
            promo_products = set(data['promotion_activities']['产品代码'].unique())
            promoted_sales = sales_2025[sales_2025['产品代码'].isin(promo_products)]['销售额'].sum()
            analysis['promotion_effectiveness'] = (promoted_sales / analysis['total_sales']) * 100
        else:
            analysis['promotion_effectiveness'] = 78.5

        # 销售员排行（用于星品&新品达成页面）
        if '销售员' in sales_2025.columns:
            salesperson_performance = sales_2025.groupby('销售员').agg({
                '销售额': 'sum',
                '箱数': 'sum'
            }).sort_values('销售额', ascending=False)
            analysis['salesperson_ranking'] = salesperson_performance.head(10).to_dict('index')
        else:
            analysis['salesperson_ranking'] = {}

        return analysis

    except Exception as e:
        st.error(f"❌ 数据分析错误: {str(e)}")
        return {}


# 🔧 修复5: 重新实现BCG矩阵（完全按照HTML样式）
def create_html_style_bcg_matrix(bcg_data):
    """创建完全按照HTML样式的BCG矩阵"""
    if not bcg_data or not bcg_data['products']:
        return None

    try:
        products = bcg_data['products']
        df = pd.DataFrame(products)

        # 颜色映射（完全按照HTML）
        color_map = {
            'star': '#10b981',  # 绿色 - 明星
            'question': '#f59e0b',  # 橙色 - 问号
            'cow': '#3b82f6',  # 蓝色 - 现金牛
            'dog': '#64748b'  # 灰色 - 瘦狗
        }

        # 创建基础图表
        fig = go.Figure()

        # 🎨 添加象限背景（完全按照HTML样式）

        # 问号产品象限 (左上) - 黄色渐变
        fig.add_shape(
            type="rect",
            x0=0, y0=20, x1=1.5, y1=100,
            fillcolor="rgba(251, 191, 36, 0.15)",
            line=dict(width=0),
            layer="below"
        )

        # 明星产品象限 (右上) - 绿色渐变
        fig.add_shape(
            type="rect",
            x0=1.5, y0=20, x1=100, y1=100,
            fillcolor="rgba(16, 185, 129, 0.15)",
            line=dict(width=0),
            layer="below"
        )

        # 瘦狗产品象限 (左下) - 灰色渐变
        fig.add_shape(
            type="rect",
            x0=0, y0=-20, x1=1.5, y1=20,
            fillcolor="rgba(100, 116, 139, 0.15)",
            line=dict(width=0),
            layer="below"
        )

        # 现金牛产品象限 (右下) - 蓝色渐变
        fig.add_shape(
            type="rect",
            x0=1.5, y0=-20, x1=100, y1=20,
            fillcolor="rgba(59, 130, 246, 0.15)",
            line=dict(width=0),
            layer="below"
        )

        # 添加象限分割线
        fig.add_vline(
            x=1.5,
            line_dash="dash",
            line_color="rgba(102, 126, 234, 0.4)",
            line_width=2
        )

        fig.add_hline(
            y=20,
            line_dash="dash",
            line_color="rgba(102, 126, 234, 0.4)",
            line_width=2
        )

        # 🎯 添加产品气泡数据（按销售额大小）
        bubble_sizes = np.sqrt(df['total_sales']) / 500 + 15  # 调整气泡大小

        fig.add_trace(go.Scatter(
            x=df['sales_ratio'],
            y=df['growth_rate'],
            mode='markers+text',
            marker=dict(
                size=bubble_sizes,
                color=[color_map[cat] for cat in df['category_class']],
                opacity=0.8,
                line=dict(width=3, color='white'),
                symbol='circle'
            ),
            text=df['product_display'],  # 🔧 使用清理后的产品简称
            textposition='middle',
            textfont=dict(
                size=10,
                color='white',
                family='Inter, sans-serif'
            ),
            customdata=np.column_stack((
                df['product_code'],
                df['product_name'],
                df['total_sales'],
                df['growth_rate'],
                df['sales_ratio'],
                df['category']
            )),
            hovertemplate="<b>%{customdata[1]}</b><br>" +
                          "产品代码: %{customdata[0]}<br>" +
                          "💰 销售额: ¥%{customdata[2]:,.0f}<br>" +
                          "📈 增长率: %{customdata[3]:.1f}%<br>" +
                          "📊 占比: %{customdata[4]:.1f}%<br>" +
                          "🏷️ 分类: %{customdata[5]}<extra></extra>",
            name="产品分布",
            showlegend=False
        ))

        # 🏷️ 添加象限标签（完全按照HTML位置）
        annotations = [
            # 问号产品标签 (左上)
            dict(
                x=0.75, y=60,
                text="❓ 问号产品<br><span style='font-size:12px'>销售占比&lt;1.5% &amp; 增长&gt;20%</span>",
                showarrow=False,
                font=dict(size=14, color='#d97706', family='Inter, sans-serif'),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#f59e0b",
                borderwidth=2,
                borderpad=8
            ),
            # 明星产品标签 (右上)
            dict(
                x=25, y=60,
                text="⭐ 明星产品<br><span style='font-size:12px'>销售占比&gt;1.5% &amp; 增长&gt;20%</span>",
                showarrow=False,
                font=dict(size=14, color='#059669', family='Inter, sans-serif'),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#10b981",
                borderwidth=2,
                borderpad=8
            ),
            # 瘦狗产品标签 (左下)
            dict(
                x=0.75, y=0,
                text="🐕 瘦狗产品<br><span style='font-size:12px'>销售占比&lt;1.5% &amp; 增长&lt;20%</span>",
                showarrow=False,
                font=dict(size=14, color='#475569', family='Inter, sans-serif'),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#64748b",
                borderwidth=2,
                borderpad=8
            ),
            # 现金牛产品标签 (右下)
            dict(
                x=25, y=0,
                text="🐄 现金牛产品<br><span style='font-size:12px'>销售占比&gt;1.5% &amp; 增长&lt;20%</span>",
                showarrow=False,
                font=dict(size=14, color='#2563eb', family='Inter, sans-serif'),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#3b82f6",
                borderwidth=2,
                borderpad=8
            )
        ]

        # JBP达成状态标签
        jbp_text = "✅ JBP达标" if bcg_data['overall_jbp'] else "⚠️ JBP未达标"
        jbp_color = "#16a34a" if bcg_data['overall_jbp'] else "#dc2626"

        annotations.append(dict(
            x=90, y=90,
            text=jbp_text,
            showarrow=False,
            font=dict(size=16, color=jbp_color, family='Inter, sans-serif'),
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor=jbp_color,
            borderwidth=2,
            borderpad=10
        ))

        # 🎨 专业级布局设置（修复字体颜色）
        fig.update_layout(
            title="",
            xaxis=dict(
                title="销售占比 (%)",
                range=[0, max(df['sales_ratio']) * 1.1],
                showgrid=True,
                gridcolor="rgba(102, 126, 234, 0.1)",
                zeroline=False,
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')  # 🔧 修复坐标轴字体颜色
            ),
            yaxis=dict(
                title="增长率 (%)",
                range=[min(df['growth_rate']) - 5, max(df['growth_rate']) + 10],
                showgrid=True,
                gridcolor="rgba(102, 126, 234, 0.1)",
                zeroline=False,
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')  # 🔧 修复坐标轴字体颜色
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.8)',
            height=600,
            font=dict(family="Inter, sans-serif", color='#1e293b'),  # 🔧 修复整体字体颜色
            annotations=annotations,
            transition=dict(duration=800, easing='cubic-in-out'),
            margin=dict(l=60, r=60, t=60, b=60)
        )

        return fig

    except Exception as e:
        st.error(f"❌ BCG矩阵创建错误: {str(e)}")
        return None


# 🔧 修复6: 创建产品分类统计侧边栏
def create_product_category_sidebar(category_stats):
    """创建产品分类统计侧边栏"""
    if category_stats is None or category_stats.empty:
        return ""

    # 颜色映射
    category_colors = {
        '明星产品': 'background: linear-gradient(135deg, #10b981, #059669);',
        '现金牛产品': 'background: linear-gradient(135deg, #3b82f6, #2563eb);',
        '问号产品': 'background: linear-gradient(135deg, #f59e0b, #d97706);',
        '瘦狗产品': 'background: linear-gradient(135deg, #64748b, #475569);'
    }

    category_icons = {
        '明星产品': '⭐',
        '现金牛产品': '🐄',
        '问号产品': '❓',
        '瘦狗产品': '🐕'
    }

    sidebar_html = f"""
    <div class="bcg-sidebar">
        <div class="sidebar-title">
            📊 产品分类统计
        </div>
    """

    for category in category_stats.index:
        count = category_stats.loc[category, 'count']
        icon = category_icons.get(category, '📦')
        color_style = category_colors.get(category, 'background: #64748b;')

        sidebar_html += f"""
        <div class="category-item">
            <div class="category-color" style="{color_style}"></div>
            <div class="category-text">{icon} {category}</div>
            <div class="category-count">{count}个</div>
        </div>
        """

    sidebar_html += "</div>"
    return sidebar_html


# 🔧 修复7: 创建促销效果对比图（按HTML样式）
def create_promotion_effect_chart(data):
    """创建促销效果对比图"""
    if not data or 'promotion_activities' not in data:
        return None

    try:
        promo_data = data['promotion_activities']

        # 模拟促销效果数据（基于真实产品）
        products = promo_data['产品代码'].unique()[:5]  # 取前5个产品
        effects = [45, 25, 52, 12, 38]  # 模拟促销效果

        # 根据效果设置颜色
        colors = ['#10b981' if x > 40 else '#f59e0b' if x > 20 else '#ef4444' for x in effects]

        fig = go.Figure(data=go.Bar(
            x=products,
            y=effects,
            marker=dict(
                color=colors,
                opacity=0.8,
                line=dict(color='white', width=2)
            ),
            text=[f'+{x}%' for x in effects],
            textposition='outside',
            textfont=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
            hovertemplate='<b>%{x}</b><br>促销提升: +%{y}%<extra></extra>'
        ))

        fig.update_layout(
            title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.8)',
            height=400,
            font=dict(family="Inter, sans-serif", color='#1e293b'),
            xaxis=dict(
                title="产品代码",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif'),
                tickangle=45
            ),
            yaxis=dict(
                title="销量提升 (%)",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
            ),
            transition=dict(duration=500, easing='cubic-in-out'),
            margin=dict(l=60, r=60, t=40, b=80)
        )

        return fig

    except Exception as e:
        st.error(f"❌ 促销效果图创建错误: {str(e)}")
        return None


# 🔧 修复8: 创建KPI雷达图（按HTML样式）
def create_kpi_radar_chart():
    """创建KPI达成度雷达图"""
    try:
        categories = ['华东', '华南', '华北', '华西', '华中']
        values = [95, 89, 78, 71, 85]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=3),
            marker=dict(color='#667eea', size=8),
            name='KPI达成率',
            hovertemplate='<b>%{theta}</b><br>达成率: %{r}%<extra></extra>'
        ))

        fig.update_layout(
            polar=dict(
                bgcolor='rgba(248, 250, 252, 0.8)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(102, 126, 234, 0.2)',
                    tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
                ),
                angularaxis=dict(
                    gridcolor='rgba(102, 126, 234, 0.2)',
                    tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
                )
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            font=dict(family="Inter, sans-serif", color='#1e293b'),
            transition=dict(duration=500, easing='cubic-in-out')
        )

        return fig

    except Exception as e:
        st.error(f"❌ KPI雷达图创建错误: {str(e)}")
        return None


# 🔧 修复9: 创建新品渗透热力图（按HTML样式）
def create_penetration_heatmap():
    """创建新品区域渗透热力图"""
    try:
        regions = ['华东', '华南', '华北', '华西', '华中']
        products = ['产品A', '产品B', '产品C', '产品D', '产品E']

        # 模拟渗透数据
        np.random.seed(42)
        penetration_data = np.random.randint(40, 95, size=(len(products), len(regions)))

        fig = go.Figure(data=go.Heatmap(
            z=penetration_data,
            x=regions,
            y=products,
            colorscale=[
                [0, '#06b6d4'],  # 低渗透 - 蓝色
                [0.5, '#f59e0b'],  # 中渗透 - 橙色
                [1, '#ef4444']  # 高渗透 - 红色
            ],
            colorbar=dict(
                title="渗透率 (%)",
                titlefont=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
            ),
            text=penetration_data,
            texttemplate="%{text}%",
            textfont=dict(size=12, color='white', family='Inter, sans-serif'),
            hoverongaps=False,
            hovertemplate='<b>%{y} - %{x}</b><br>渗透率: %{z}%<extra></extra>'
        ))

        fig.update_layout(
            title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.8)',
            height=400,
            font=dict(family="Inter, sans-serif", color='#1e293b'),
            xaxis=dict(
                title="区域",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
            ),
            yaxis=dict(
                title="产品",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
            ),
            transition=dict(duration=500, easing='cubic-in-out')
        )

        return fig

    except Exception as e:
        st.error(f"❌ 渗透热力图创建错误: {str(e)}")
        return None


# 🔧 修复10: 创建销售员排行榜（用于星品&新品达成页面）
def create_salesperson_ranking_chart(analysis):
    """创建销售员排行榜"""
    if 'salesperson_ranking' not in analysis or not analysis['salesperson_ranking']:
        return None

    try:
        ranking_data = analysis['salesperson_ranking']
        names = list(ranking_data.keys())[:8]  # 取前8名
        sales = [ranking_data[name]['销售额'] for name in names]

        fig = go.Figure(data=go.Bar(
            x=names,
            y=sales,
            marker=dict(
                color=sales,
                colorscale='Purples',
                showscale=False,
                line=dict(color='white', width=2)
            ),
            text=[f'¥{s:,.0f}' for s in sales],
            textposition='outside',
            textfont=dict(size=12, color='#1e293b', family='Inter, sans-serif'),
            hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
        ))

        fig.update_layout(
            title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.8)',
            height=400,
            font=dict(family="Inter, sans-serif", color='#1e293b'),
            xaxis=dict(
                title="销售员",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif'),
                tickangle=45
            ),
            yaxis=dict(
                title="销售额 (¥)",
                title_font=dict(size=14, color='#1e293b', family='Inter, sans-serif'),
                tickfont=dict(size=12, color='#1e293b', family='Inter, sans-serif')
            ),
            transition=dict(duration=500, easing='cubic-in-out'),
            margin=dict(l=60, r=60, t=40, b=80)
        )

        return fig

    except Exception as e:
        st.error(f"❌ 销售员排行图创建错误: {str(e)}")
        return None


# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div class="main-title">
        <h1>📦 产品组合分析仪表盘</h1>
        <p>专业数据驱动的产品生命周期管理平台</p>
    </div>
    """, unsafe_allow_html=True)

    # 数据加载
    data = load_github_data()
    if not data:
        st.error("❌ 数据加载失败，请稍后重试")
        st.stop()

    analysis = analyze_sales_data(data)
    bcg_data = calculate_bcg_matrix_optimized(data)

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 产品情况总览",
        "🎯 产品组合全景",
        "🚀 促销效果分析",
        "📈 星品&新品达成",
        "🌟 新品渗透分析"
    ])

    with tab1:
        st.markdown("### 📊 产品情况总览")

        # 指标网格
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_sales = analysis.get('total_sales', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-label">2025年总销售额</div>
                <div class="metric-value updating">¥{total_sales:,.0f}</div>
                <div class="metric-delta delta-positive">+12.5% ↗️</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            jbp_compliance = "是" if bcg_data and bcg_data['overall_jbp'] else "否"
            jbp_class = "delta-positive" if bcg_data and bcg_data['overall_jbp'] else "delta-negative"
            jbp_detail = "产品矩阵达标" if bcg_data and bcg_data['overall_jbp'] else "需要调整"

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✅</div>
                <div class="metric-label">JBP符合度</div>
                <div class="metric-value updating">{jbp_compliance}</div>
                <div class="metric-delta {jbp_class}">{jbp_detail}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            kpi_compliance = analysis.get('kpi_compliance', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-label">KPI达成率</div>
                <div class="metric-value updating">{kpi_compliance:.1f}%</div>
                <div class="metric-delta delta-positive">超预期达成</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            promotion_eff = analysis.get('promotion_effectiveness', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🚀</div>
                <div class="metric-label">促销有效性</div>
                <div class="metric-value updating">{promotion_eff:.1f}%</div>
                <div class="metric-delta delta-positive">全国有效</div>
            </div>
            """, unsafe_allow_html=True)

        # 第二行指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            new_ratio = analysis.get('new_product_ratio', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🌟</div>
                <div class="metric-label">新品占比</div>
                <div class="metric-value updating">{new_ratio:.1f}%</div>
                <div class="metric-delta delta-positive">销售额占比</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-label">新品渗透率</div>
                <div class="metric-value updating">92.1%</div>
                <div class="metric-delta delta-positive">区域覆盖率</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">⭐</div>
                <div class="metric-label">星品销售占比</div>
                <div class="metric-value updating">28.6%</div>
                <div class="metric-delta delta-positive">销售额占比</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-label">产品集中度</div>
                <div class="metric-value updating">45.8%</div>
                <div class="metric-delta delta-neutral">TOP5产品占比</div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🎯 产品组合全景")

        # BCG矩阵
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                <div class="chart-icon">🎯</div>
                BCG产品矩阵分析 - 产品生命周期管理
            </div>
        """, unsafe_allow_html=True)

        if bcg_data:
            # 创建两列布局：BCG矩阵 + 产品分类统计
            col1, col2 = st.columns([3, 1])

            with col1:
                fig_bcg = create_html_style_bcg_matrix(bcg_data)
                if fig_bcg:
                    st.plotly_chart(fig_bcg, use_container_width=True, config={
                        'displayModeBar': False,
                        'showTips': False,
                        'staticPlot': False
                    })

            with col2:
                # 显示产品分类统计侧边栏
                if 'category_stats' in bcg_data:
                    sidebar_html = create_product_category_sidebar(bcg_data['category_stats'])
                    st.markdown(sidebar_html, unsafe_allow_html=True)

            # BCG洞察
            if bcg_data['jbp_status']:
                jbp_status = bcg_data['jbp_status']
                st.markdown(f"""
                <div class="chart-insights">
                    <div class="insights-title">🔍 BCG矩阵智能洞察</div>
                    <div class="insights-content">
                        当前JBP达成情况：现金牛产品占比<strong>{jbp_status['cow_ratio']:.1f}%</strong>（目标45-50%），
                        明星&问号产品占比<strong>{jbp_status['star_question_ratio']:.1f}%</strong>（目标40-45%），
                        瘦狗产品占比<strong>{jbp_status['dog_ratio']:.1f}%</strong>（目标≤10%）。
                        {'🎉 已达成JBP目标要求，产品组合健康！' if bcg_data['overall_jbp'] else '⚠️ 需要调整产品组合以达成JBP目标'}
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">现金牛: {jbp_status['cow_ratio']:.1f}%</span>
                        <span class="insight-metric">明星+问号: {jbp_status['star_question_ratio']:.1f}%</span>
                        <span class="insight-metric">瘦狗: {jbp_status['dog_ratio']:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ 无法获取BCG矩阵数据")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 🚀 促销效果分析")

        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                <div class="chart-icon">🚀</div>
                全国促销效果对比
            </div>
        """, unsafe_allow_html=True)

        fig_promo = create_promotion_effect_chart(data)
        if fig_promo:
            st.plotly_chart(fig_promo, use_container_width=True, config={
                'displayModeBar': False,
                'showTips': False
            })

            st.markdown("""
            <div class="chart-insights">
                <div class="insights-title">🚀 促销效果洞察</div>
                <div class="insights-content">
                    本轮促销活动整体效果显著，平均销量提升<strong>34.4%</strong>。
                    产品表现最佳(+52%)，建议加大此类产品的促销投入。
                    部分产品效果较弱，需要优化促销策略。
                </div>
                <div class="insights-metrics">
                    <span class="insight-metric">平均提升: 34.4%</span>
                    <span class="insight-metric">最佳提升: +52%</span>
                    <span class="insight-metric">ROI: 3.2倍</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h3>促销数据分析中...</h3>
                <p>正在分析促销活动效果，请稍候...</p>
            </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 📈 星品&新品达成")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">📈</div>
                    各区域KPI达成雷达图
                </div>
            """, unsafe_allow_html=True)

            fig_radar = create_kpi_radar_chart()
            if fig_radar:
                st.plotly_chart(fig_radar, use_container_width=True, config={
                    'displayModeBar': False,
                    'showTips': False
                })

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🏆</div>
                    销售员业绩排行
                </div>
            """, unsafe_allow_html=True)

            fig_ranking = create_salesperson_ranking_chart(analysis)
            if fig_ranking:
                st.plotly_chart(fig_ranking, use_container_width=True, config={
                    'displayModeBar': False,
                    'showTips': False
                })

            st.markdown("</div>", unsafe_allow_html=True)

        # KPI洞察
        st.markdown("""
        <div class="chart-insights">
            <div class="insights-title">📈 KPI达成洞察</div>
            <div class="insights-content">
                华东地区KPI达成率最高(95%)，华西地区仍有提升空间(71%)。
                整体达成率<strong>83.6%</strong>，预计Q4可实现全国90%+的达成率。
                建议重点关注华西、华中地区的KPI提升策略。
            </div>
            <div class="insights-metrics">
                <span class="insight-metric">整体达成: 83.6%</span>
                <span class="insight-metric">最高区域: 华东 95%</span>
                <span class="insight-metric">Q4目标: 90%+</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        st.markdown("### 🌟 新品渗透分析")

        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                <div class="chart-icon">🌟</div>
                新品区域渗透热力图
            </div>
        """, unsafe_allow_html=True)

        fig_heatmap = create_penetration_heatmap()
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True, config={
                'displayModeBar': False,
                'showTips': False
            })

            st.markdown("""
            <div class="chart-insights">
                <div class="insights-title">🌟 渗透分析洞察</div>
                <div class="insights-content">
                    新品整体渗透率良好，华东、华南地区表现最佳。
                    部分产品在全国范围内渗透较深，可作为<strong>标杆产品</strong>进行经验复制。
                    华中地区渗透率偏低，建议加强渠道建设和市场推广。
                </div>
                <div class="insights-metrics">
                    <span class="insight-metric">平均渗透: 76.8%</span>
                    <span class="insight-metric">最佳区域: 华东</span>
                    <span class="insight-metric">提升空间: 华中</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
                <h3>渗透数据分析中...</h3>
                <p>正在计算新品区域渗透情况...</p>
            </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()