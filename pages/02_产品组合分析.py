# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import re
from itertools import combinations
import warnings

# 新增：导入认证模块
try:
    from data_storage import storage
except ImportError:
    st.error("请确保 data_storage 模块可用")
    st.stop()

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide"
)

# 增强的CSS样式 - 统一容器设计
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局字体和背景 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        color: #1f2937;
    }

    /* 添加浮动粒子背景动画 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    /* 主容器背景 */
    .main .block-container {
        background: rgba(255,255,255,0.98);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* 确保所有文本颜色正确 */
    .stApp, .stApp * {
        color: #1f2937 !important;
    }

    /* 主标题样式 - 增强动画 */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white !important;
        border-radius: 25px;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.5s ease-out, glow 2s ease-in-out infinite alternate;
        box-shadow: 
            0 15px 35px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1),
            inset 0 1px 0 rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        transform: perspective(1000px) rotateX(0deg);
        transition: transform 0.3s ease;
    }

    .main-header * {
        color: white !important;
    }

    .main-header:hover {
        transform: perspective(1000px) rotateX(-2deg) scale(1.02);
        box-shadow: 
            0 25px 50px rgba(102, 126, 234, 0.5),
            0 10px 30px rgba(0,0,0,0.15);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
    }

    .main-header::after {
        content: '✨';
        position: absolute;
        top: 10%;
        right: 10%;
        font-size: 2rem;
        animation: sparkle 1.5s ease-in-out infinite;
    }

    /* 统一的内容容器样式 */
    .content-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        animation: containerFadeIn 1.2s ease-out;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .content-container:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.12),
            0 8px 20px rgba(0,0,0,0.06);
    }

    .content-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.02), transparent);
        animation: containerShimmer 8s linear infinite;
    }

    /* 确保容器内文本颜色正确 */
    .content-container, .content-container * {
        color: #1f2937 !important;
    }

    /* 给所有图表添加圆角 */
    .js-plotly-plot .plotly, .js-plotly-plot .plot-container {
        border-radius: 20px !important;
        overflow: hidden !important;
    }

    /* Plotly图表容器圆角 */
    .user-select-none {
        border-radius: 20px !important;
    }

    @keyframes containerFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }

    @keyframes containerShimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    @keyframes glow {
        from { box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4), 0 5px 15px rgba(0,0,0,0.1); }
        to { box-shadow: 0 20px 40px rgba(102, 126, 234, 0.6), 0 8px 20px rgba(0,0,0,0.15); }
    }

    @keyframes sparkle {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
        50% { transform: scale(1.3) rotate(180deg); opacity: 0.7; }
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    @keyframes fadeInScale {
        from { 
            opacity: 0; 
            transform: translateY(-50px) scale(0.8) rotateX(-10deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }

    /* 增强的指标卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem 1.5rem;
        border-radius: 25px;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.9);
        text-align: center;
        height: 100%;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUpStagger 1s ease-out;
        position: relative;
        overflow: visible;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        min-height: 160px;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.8s ease;
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 25px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-15px) scale(1.05) rotateY(5deg);
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.15),
            0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
        animation: pulse 1.5s infinite;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card:hover::after {
        opacity: 0.1;
    }

    @keyframes slideUpStagger {
        from { 
            opacity: 0; 
            transform: translateY(60px) scale(0.8) rotateX(-15deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.8rem;
        animation: textGradient 4s ease infinite, bounce 2s ease-in-out infinite;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-3px); }
        60% { transform: translateY(-2px); }
    }

    @keyframes textGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .metric-label {
        color: #374151 !important;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.5rem;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    .metric-sublabel {
        color: #6b7280 !important;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 500;
        font-style: italic;
    }

    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 
            inset 0 2px 4px rgba(0,0,0,0.06),
            0 4px 8px rgba(0,0,0,0.04);
        backdrop-filter: blur(10px);
    }

    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 35px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 1rem;
        color: #374151 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }

    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.15), transparent);
        transition: left 0.8s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.4);
    }

    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1);
        animation: activeTab 0.5s ease;
    }

    .stTabs [aria-selected="true"]::before {
        display: none;
    }

    @keyframes activeTab {
        0% { transform: scale(0.95); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1.02); }
    }

    /* 动画卡片延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }
    .metric-card:nth-child(9) { animation-delay: 0.9s; }
    .metric-card:nth-child(10) { animation-delay: 1.0s; }

    /* 促销活动有效率标题样式 */
    .promo-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        font-weight: 700;
        font-size: 1.5rem;
    }

    .promo-header * {
        color: white !important;
    }

    /* 添加脉动效果 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.8rem;
        }
        .metric-card {
            padding: 1.5rem 1rem;
        }
        .main-header {
            padding: 2rem 0;
        }
        .content-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }

    /* Streamlit组件样式覆盖 */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.9) !important;
        color: #1f2937 !important;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    .stSelectbox label {
        color: #374151 !important;
        font-weight: 600;
    }

    .stRadio > div {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 15px;
        padding: 1rem;
    }

    .stRadio label {
        color: #1f2937 !important;
    }

    /* 确保所有Streamlit元素的文本颜色 */
    .stMarkdown, .stText, .stCaption {
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)


# 产品名称简化函数
def simplify_product_name(name):
    """简化产品名称，去掉口力和-中国等后缀"""
    if pd.isna(name):
        return ""
    # 去掉口力
    name = name.replace('口力', '')
    # 去掉-中国等后缀
    name = re.sub(r'-中国.*$', '', name)
    # 去掉其他常见后缀
    name = re.sub(r'（.*）$', '', name)
    name = re.sub(r'\(.*\)$', '', name)
    # 限制长度
    if len(name) > 8:
        name = name[:8] + '..'
    return name.strip()
def fixed_authentication_check():
    """检查附件一的认证状态"""
    is_authenticated = (
            hasattr(st.session_state, 'authenticated') and
            st.session_state.authenticated is True and
            hasattr(st.session_state, 'username') and
            st.session_state.username != ""
    )
    return is_authenticated

def show_auth_required_page():
    """显示需要认证的提示页面"""
    st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 60vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin: 2rem 0;
    ">
        <div style="
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 400px;
        ">
            <h2 style="color: #667eea; margin-bottom: 2rem;">🔐 需要登录</h2>
            <p style="color: #666; margin-bottom: 2rem;">请先通过主页面登录系统后再访问产品组合分析</p>
            <p style="color: #999; font-size: 0.9rem;">您可以通过侧边栏返回主页面进行登录</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
def clear_promotion_cache():
    """清理促销分析缓存"""
    try:
        analyze_promotion_cached.clear()
        st.success("✅ 促销分析缓存已清理")
    except:
        st.info("缓存清理完成")
# 缓存数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 星品代码
        with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
            star_products = [line.strip() for line in f.readlines() if line.strip()]

        # 新品代码
        with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
            new_products = [line.strip() for line in f.readlines() if line.strip()]

        # 仪表盘产品代码
        with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
            dashboard_products = [line.strip() for line in f.readlines() if line.strip()]

        # 促销活动数据
        promotion_df = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')

        # 销售数据
        sales_df = pd.read_excel('24-25促销效果销售数据.xlsx')

        # 调试：检查原始数据
        print(f"原始销售数据行数: {len(sales_df)}")
        print(f"原始销售数据列名: {list(sales_df.columns)}")

        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'])
        sales_df['销售额'] = sales_df['单价'] * sales_df['箱数']

        # 调试：检查计算后的数据
        print(f"计算销售额后的数据:")
        print(f"总记录数: {len(sales_df)}")
        print(f"唯一产品数: {sales_df['产品代码'].nunique()}")

        # 获取动态时间信息
        time_info = get_dynamic_time_range(sales_df)
        current_year = time_info['current_year']

        print(f"{current_year}年记录数: {len(sales_df[sales_df['发运月份'].dt.year == current_year])}")
        print(
            f"{current_year}年总销售额: {sales_df[sales_df['发运月份'].dt.year == current_year]['销售额'].sum():,.0f}")

        # 简化产品名称
        sales_df['产品简称'] = sales_df['产品简称'].apply(simplify_product_name)
        promotion_df['促销产品名称'] = promotion_df['促销产品名称'].apply(simplify_product_name)

        return {
            'star_products': star_products,
            'new_products': new_products,
            'dashboard_products': dashboard_products,
            'promotion_df': promotion_df,
            'sales_df': sales_df,
            'time_info': time_info
        }
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        print(f"数据加载错误详情: {str(e)}")
        return None



def get_dynamic_time_range(sales_df):
    """动态获取数据的时间范围和最新月份"""
    try:
        # 获取数据中的最新月份和最早月份
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'])
        latest_month = sales_df['发运月份'].max()
        earliest_month = sales_df['发运月份'].min()

        # 获取当前年份的数据
        current_year = latest_month.year
        current_year_data = sales_df[sales_df['发运月份'].dt.year == current_year]

        if len(current_year_data) > 0:
            current_year_latest = current_year_data['发运月份'].max()
        else:
            current_year_latest = latest_month

        # 计算环比月份（上个月）
        previous_month = current_year_latest - pd.DateOffset(months=1)

        # 计算同比月份（去年同期）
        same_month_last_year = current_year_latest - pd.DateOffset(years=1)

        return {
            'latest_month': current_year_latest,
            'previous_month': previous_month,
            'same_month_last_year': same_month_last_year,
            'current_year': current_year,
            'data_range': f"{earliest_month.strftime('%Y-%m')} 至 {latest_month.strftime('%Y-%m')}"
        }
    except Exception as e:
        st.error(f"时间范围计算出错: {str(e)}")
        # 返回默认值
        return {
            'latest_month': pd.Timestamp('2025-04'),
            'previous_month': pd.Timestamp('2025-03'),
            'same_month_last_year': pd.Timestamp('2024-04'),
            'current_year': 2025,
            'data_range': "2024-01 至 2025-04"
        }
def get_dynamic_time_range(sales_df):
    """动态获取数据的时间范围和最新月份"""
    try:
        # 获取数据中的最新月份和最早月份
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'])
        latest_month = sales_df['发运月份'].max()
        earliest_month = sales_df['发运月份'].min()

        # 获取当前年份的数据
        current_year = latest_month.year
        current_year_data = sales_df[sales_df['发运月份'].dt.year == current_year]

        if len(current_year_data) > 0:
            current_year_latest = current_year_data['发运月份'].max()
        else:
            current_year_latest = latest_month

        # 计算环比月份（上个月）
        previous_month = current_year_latest - pd.DateOffset(months=1)

        # 计算同比月份（去年同期）
        same_month_last_year = current_year_latest - pd.DateOffset(years=1)

        return {
            'latest_month': current_year_latest,
            'previous_month': previous_month,
            'same_month_last_year': same_month_last_year,
            'current_year': current_year,
            'data_range': f"{earliest_month.strftime('%Y-%m')} 至 {latest_month.strftime('%Y-%m')}"
        }
    except Exception as e:
        st.error(f"时间范围计算出错: {str(e)}")
        # 返回默认值
        return {
            'latest_month': pd.Timestamp('2025-04'),
            'previous_month': pd.Timestamp('2025-03'),
            'same_month_last_year': pd.Timestamp('2024-04'),
            'current_year': 2025,
            'data_range': "2024-01 至 2025-04"
        }

# 添加缓存函数来优化BCG矩阵计算
@st.cache_data
def analyze_product_bcg_cached(sales_df, dashboard_products, time_info, region=None):
    """缓存BCG矩阵分析结果（使用动态时间）"""
    if region:
        sales_df = sales_df[sales_df['区域'] == region]
    # 当dashboard_products为None时，分析所有产品
    return analyze_product_bcg_comprehensive(sales_df, dashboard_products, time_info)


# 添加缓存函数来优化促销分析
@st.cache_data
def analyze_promotion_cached(promotion_df, sales_df, time_info):
    """缓存促销分析结果（使用动态时间）"""
    data = {
        'promotion_df': promotion_df,
        'sales_df': sales_df
    }
    return analyze_promotion_effectiveness_enhanced(data, time_info)


# 添加缓存函数来优化产品关联网络
@st.cache_data
def create_product_network_cached(sales_df, dashboard_products, star_products, new_products, promotion_df,
                                  product_filter):
    """缓存产品关联网络计算"""
    data = {
        'sales_df': sales_df,
        'dashboard_products': dashboard_products,
        'star_products': star_products,
        'new_products': new_products,
        'promotion_df': promotion_df
    }
    return create_real_product_network(data, product_filter)


# 添加缓存函数来优化有效产品分析
@st.cache_data
def analyze_effective_products_cached(sales_df, dashboard_products, dimension='national', selected_region=None):
    """缓存有效产品分析结果"""
    data = {
        'sales_df': sales_df,
        'dashboard_products': dashboard_products
    }
    return analyze_effective_products(data, dimension, selected_region)


# 添加缓存函数来优化新品渗透率分析
def create_regional_penetration_analysis(data):
    """创建区域新品渗透率分析"""
    sales_df = data['sales_df']
    new_products = data['new_products']

    # 2025年数据
    sales_2025 = sales_df[sales_df['发运月份'].dt.year == 2025]

    regional_stats = []
    regions = sales_2025['区域'].unique()

    for region in regions:
        region_data = sales_2025[sales_2025['区域'] == region]

        # 总客户数
        total_customers = region_data['客户名称'].nunique()

        # 购买新品的客户数
        new_product_customers = region_data[region_data['产品代码'].isin(new_products)]['客户名称'].nunique()

        # 新品销售额
        new_product_sales = region_data[region_data['产品代码'].isin(new_products)]['销售额'].sum()
        total_sales = region_data['销售额'].sum()

        # 新品数量
        new_products_sold = region_data[region_data['产品代码'].isin(new_products)]['产品代码'].nunique()

        penetration_rate = (new_product_customers / total_customers * 100) if total_customers > 0 else 0
        sales_ratio = (new_product_sales / total_sales * 100) if total_sales > 0 else 0

        regional_stats.append({
            'region': region,
            'penetration_rate': penetration_rate,
            'total_customers': total_customers,
            'new_product_customers': new_product_customers,
            'new_product_sales': new_product_sales,
            'total_sales': total_sales,
            'sales_ratio': sales_ratio,
            'new_products_count': new_products_sold
        })

    df = pd.DataFrame(regional_stats).sort_values('penetration_rate', ascending=True)  # 改为升序，使东区在左边

    # 创建图表
    fig = go.Figure()

    # 添加渗透率柱状图
    fig.add_trace(go.Bar(
        name='新品渗透率',
        x=df['region'],
        y=df['penetration_rate'],
        text=[f"{rate:.1f}%" for rate in df['penetration_rate']],
        textposition='auto',  # 改为auto防止重影
        marker=dict(color='#4CAF50'),
        yaxis='y',
        offsetgroup=1,
        hovertemplate="""<b>%{x}区域</b><br>
新品渗透率: %{y:.1f}%<br>
购买新品客户: %{customdata[0]}个<br>
总客户数: %{customdata[1]}个<br>
新品数量: %{customdata[2]}个<br>
<extra></extra>""",
        customdata=df[['new_product_customers', 'total_customers', 'new_products_count']].values
    ))

    # 添加销售占比折线图
    fig.add_trace(go.Scatter(
        name='新品销售占比',
        x=df['region'],
        y=df['sales_ratio'],
        mode='lines+markers',
        marker=dict(size=10, color='#FF5722'),
        line=dict(width=3, color='#FF5722'),
        yaxis='y2',
        hovertemplate="""<b>%{x}区域</b><br>
新品销售占比: %{y:.1f}%<br>
新品销售额: ¥%{customdata[0]:,.0f}<br>
总销售额: ¥%{customdata[1]:,.0f}<br>
<extra></extra>""",
        customdata=df[['new_product_sales', 'total_sales']].values
    ))

    # 计算全国平均渗透率
    total_customers_all = sales_2025['客户名称'].nunique()
    new_customers_all = sales_2025[sales_2025['产品代码'].isin(new_products)]['客户名称'].nunique()
    national_avg_penetration = (new_customers_all / total_customers_all * 100) if total_customers_all > 0 else 0

    # 添加全国平均线（红色虚线）
    fig.add_hline(y=national_avg_penetration, line_dash="dash", line_color="red",
                  annotation_text=f"全国渗透率: {national_avg_penetration:.1f}%",
                  annotation_position="top left",
                  annotation_textangle=0)

    fig.update_layout(
        title=dict(text="<b>区域新品渗透率分析</b>", font=dict(size=20)),
        xaxis=dict(title="销售区域"),
        yaxis=dict(
            title="新品渗透率 (%)",
            side='left',
            range=[0, max(df['penetration_rate'].max() * 1.2, national_avg_penetration * 1.3)]  # 确保标注不被遮挡
        ),
        yaxis2=dict(title="新品销售占比 (%)", overlaying='y', side='right'),
        height=600,
        hovermode='x unified',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        ),
        plot_bgcolor='white',
        margin=dict(t=100)  # 增加顶部边距，避免标注被遮挡
    )

    return fig, df


@st.cache_data
def analyze_growth_rates_cached(sales_df, dashboard_products, time_info):
    """缓存增长率分析结果（使用动态时间）"""
    data = {
        'sales_df': sales_df,
        'dashboard_products': dashboard_products
    }
    return analyze_product_growth_rates(data, time_info)


# 计算总体指标（基于后续所有分析）- 添加缓存
# 计算总体指标（基于后续所有分析）- 添加缓存
# 计算总体指标（基于后续所有分析）- 修改缓存键强制刷新
# 计算总体指标（基于后续所有分析）- 添加缓存
@st.cache_data
def calculate_comprehensive_metrics(sales_df, star_products, new_products, dashboard_products, promotion_df, time_info):
    """计算产品情况总览的各项指标（使用动态时间范围）"""
    current_year = time_info['current_year']

    # 当前年份数据
    sales_current_year = sales_df[sales_df['发运月份'].dt.year == current_year]

    # 总销售额 - 计算所有产品并四舍五入
    total_sales = round(sales_current_year['销售额'].sum())

    # 星品和新品销售额 - 在所有产品中查找星品和新品
    star_sales = sales_current_year[sales_current_year['产品代码'].isin(star_products)]['销售额'].sum()
    new_sales = sales_current_year[sales_current_year['产品代码'].isin(new_products)]['销售额'].sum()

    # 占比计算 - 基于所有产品的总销售额
    star_ratio = (star_sales / total_sales * 100) if total_sales > 0 else 0
    new_ratio = (new_sales / total_sales * 100) if total_sales > 0 else 0
    total_ratio = star_ratio + new_ratio

    # 新品渗透率 - 基于所有客户
    total_customers = sales_current_year['客户名称'].nunique()
    new_customers = sales_current_year[sales_current_year['产品代码'].isin(new_products)]['客户名称'].nunique()
    penetration_rate = (new_customers / total_customers * 100) if total_customers > 0 else 0

    # BCG分析 - 改为分析所有产品
    product_analysis = analyze_product_bcg_comprehensive(sales_df, None, time_info)  # 传入None表示分析所有产品

    total_bcg_sales = product_analysis['sales'].sum() if len(product_analysis) > 0 else 0
    cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum() if len(
        product_analysis) > 0 else 0
    star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])][
        'sales'].sum() if len(product_analysis) > 0 else 0

    cow_ratio = cow_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0
    star_question_ratio = star_question_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0

    jbp_status = 'YES' if (45 <= cow_ratio <= 50 and 40 <= star_question_ratio <= 45) else 'NO'

    # 促销有效性
    data = {
        'promotion_df': promotion_df,
        'sales_df': sales_df
    }
    promo_results = analyze_promotion_effectiveness_enhanced(data, time_info)
    promo_effectiveness = (promo_results['is_effective'].sum() / len(promo_results) * 100) if len(
        promo_results) > 0 else 0

    # 有效产品分析 - 只分析仪表盘产品
    effective_rate_all = calculate_effective_products_rate(sales_current_year, dashboard_products)

    # 计算有效产品详细数据 - 只分析仪表盘产品
    data = {
        'sales_df': sales_df,
        'dashboard_products': dashboard_products
    }
    product_analysis_eff = analyze_effective_products(data, 'national')
    effective_products = product_analysis_eff[product_analysis_eff['is_effective'] == True]
    effective_count = len(effective_products)

    if len(effective_products) > 0:
        avg_effective_sales = effective_products['monthly_avg_boxes'].mean()
    else:
        avg_effective_sales = 0

    return {
        'total_sales': total_sales,  # 所有产品的销售额（已四舍五入）
        'star_ratio': star_ratio,
        'new_ratio': new_ratio,
        'total_ratio': total_ratio,
        'penetration_rate': penetration_rate,
        'jbp_status': jbp_status,
        'promo_effectiveness': promo_effectiveness,
        'effective_products_rate': effective_rate_all,
        'effective_products_count': effective_count,
        'avg_effective_sales': avg_effective_sales,
        'current_year': current_year,
        'data_range': time_info['data_range']
    }

def analyze_product_bcg_comprehensive(sales_df, dashboard_products, time_info):
    """分析产品BCG矩阵数据，使用动态时间范围"""
    if len(sales_df) == 0:
        return pd.DataFrame()

    current_year = time_info['current_year']
    current_data = sales_df[sales_df['发运月份'].dt.year == current_year]
    prev_data = sales_df[sales_df['发运月份'].dt.year == current_year - 1]

    # 如果dashboard_products为None，则分析所有产品
    if dashboard_products is None:
        products_to_analyze = current_data['产品代码'].unique().tolist()
        # 添加去年有但今年没有的产品
        prev_year_products = prev_data['产品代码'].unique()
        for p in prev_year_products:
            if p not in products_to_analyze:
                products_to_analyze.append(p)
    else:
        products_to_analyze = dashboard_products

    product_stats = []
    total_sales = current_data['销售额'].sum()

    for product in products_to_analyze:
        current_product_data = current_data[current_data['产品代码'] == product]
        prev_product_data = prev_data[prev_data['产品代码'] == product]

        current_sales = current_product_data['销售额'].sum()
        prev_sales = prev_product_data['销售额'].sum()

        # 获取产品名称
        if len(current_product_data) > 0:
            product_name = current_product_data['产品简称'].iloc[0]
        elif len(prev_product_data) > 0:
            product_name = prev_product_data['产品简称'].iloc[0]
        else:
            all_product_data = sales_df[sales_df['产品代码'] == product]
            if len(all_product_data) > 0:
                product_name = all_product_data['产品简称'].iloc[0]
            else:
                product_name = product

        # 只处理有销售数据的产品
        if current_sales > 0 or prev_sales > 0:
            market_share = (current_sales / total_sales * 100) if total_sales > 0 else 0

            # 计算增长率，限制在合理范围内
            if prev_sales > 0:
                growth_rate = ((current_sales - prev_sales) / prev_sales * 100)
            elif current_sales > 0:
                growth_rate = 100
            else:
                growth_rate = 0

            # 存储真实增长率用于显示
            real_growth_rate = growth_rate
            # 限制显示范围用于图表
            display_growth_rate = max(-50, min(growth_rate, 100))

            # 分类逻辑
            if market_share >= 1.5 and growth_rate > 20:
                category = 'star'
                reason = f"市场份额高({market_share:.1f}%≥1.5%)且增长快({growth_rate:.1f}%>20%)"
            elif market_share < 1.5 and growth_rate > 20:
                category = 'question'
                reason = f"市场份额低({market_share:.1f}%<1.5%)但增长快({growth_rate:.1f}%>20%)"
            elif market_share >= 1.5 and growth_rate <= 20:
                category = 'cow'
                reason = f"市场份额高({market_share:.1f}%≥1.5%)但增长慢({growth_rate:.1f}%≤20%)"
            else:
                category = 'dog'
                reason = f"市场份额低({market_share:.1f}%<1.5%)且增长慢({growth_rate:.1f}%≤20%)"

            product_stats.append({
                'product': product,
                'name': product_name,
                'market_share': market_share,
                'growth_rate': display_growth_rate,
                'real_growth_rate': real_growth_rate,
                'sales': current_sales,
                'prev_sales': prev_sales,
                'category': category,
                'category_reason': reason,
                'calculation_detail': f"当前销售额: ¥{current_sales:,.0f}\n去年销售额: ¥{prev_sales:,.0f}\n市场份额: {market_share:.2f}%\n真实增长率: {real_growth_rate:.1f}%"
            })

    return pd.DataFrame(product_stats)

def create_bcg_matrix(data, dimension='national', selected_region=None):
    """创建BCG矩阵分析"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']

    # 确保只分析仪表盘产品
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(dashboard_products)]

    if dimension == 'national':
        product_analysis = analyze_product_bcg_comprehensive(sales_df_filtered, dashboard_products)
        return product_analysis
    else:
        if selected_region:
            region_data = sales_df_filtered[sales_df_filtered['区域'] == selected_region]
            region_analysis = analyze_product_bcg_comprehensive(region_data, dashboard_products)
            return region_analysis
        return pd.DataFrame()


def plot_bcg_matrix(product_df, title="BCG产品矩阵"):
    """绘制简化的BCG矩阵图"""
    if len(product_df) == 0:
        return go.Figure()

    fig = go.Figure()

    # 定义象限颜色和产品颜色
    quadrant_colors = {
        'star': 'rgba(255, 235, 153, 0.3)',
        'question': 'rgba(255, 153, 153, 0.3)',
        'cow': 'rgba(204, 235, 255, 0.3)',
        'dog': 'rgba(230, 230, 230, 0.3)'
    }

    bubble_colors = {
        'star': '#FFC107',
        'question': '#F44336',
        'cow': '#2196F3',
        'dog': '#9E9E9E'
    }

    category_names = {
        'star': '⭐ 明星产品',
        'question': '❓ 问号产品',
        'cow': '🐄 现金牛产品',
        'dog': '🐕 瘦狗产品'
    }

    # 添加象限背景
    fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=100,
                  fillcolor=quadrant_colors['question'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=1.5, y0=20, x1=10, y1=100,
                  fillcolor=quadrant_colors['star'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0, y0=-50, x1=1.5, y1=20,
                  fillcolor=quadrant_colors['dog'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=1.5, y0=-50, x1=10, y1=20,
                  fillcolor=quadrant_colors['cow'], line=dict(width=0), layer="below")

    # 绘制产品气泡
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            # 优化位置分布
            positions = optimize_smart_grid_positions(cat_data, category)

            # 设置气泡大小
            sizes = cat_data['sales'].apply(lambda x: max(min(np.sqrt(x) / 20, 60), 25))

            # 创建hover文本
            hover_texts = []
            for _, row in cat_data.iterrows():
                category_name = category_names.get(category, category)
                hover_text = f"""<b>{row['name']} ({row['product']})</b><br>
<br><b>分类：{category_name}</b><br>
<br><b>分类原因：</b><br>{row['category_reason']}<br>
<br><b>详细信息：</b><br>{row['calculation_detail']}<br>
<br><b>策略建议：</b><br>{get_strategy_suggestion(category)}"""
                hover_texts.append(hover_text)

            fig.add_trace(go.Scatter(
                x=positions['x'],
                y=positions['y'],
                mode='markers+text',
                marker=dict(
                    size=sizes,
                    color=bubble_colors[category],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=cat_data['name'].apply(lambda x: x[:6] + '..' if len(x) > 6 else x),
                textposition='middle center',
                textfont=dict(size=8, color='white', weight='bold'),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts,
                showlegend=False,
                name=category_name
            ))

    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", opacity=0.5, line_width=2)
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", opacity=0.5, line_width=2)

    # 添加象限标注
    annotations = [
        dict(x=0.75, y=60, text="<b>❓ 问号产品</b><br>低份额·高增长",
             showarrow=False, font=dict(size=12, color="#F44336"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#F44336", borderwidth=2),
        dict(x=5.5, y=60, text="<b>⭐ 明星产品</b><br>高份额·高增长",
             showarrow=False, font=dict(size=12, color="#FFC107"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#FFC107", borderwidth=2),
        dict(x=0.75, y=-15, text="<b>🐕 瘦狗产品</b><br>低份额·低增长",
             showarrow=False, font=dict(size=12, color="#9E9E9E"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#9E9E9E", borderwidth=2),
        dict(x=5.5, y=-15, text="<b>🐄 现金牛产品</b><br>高份额·低增长",
             showarrow=False, font=dict(size=12, color="#2196F3"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#2196F3", borderwidth=2)
    ]

    for ann in annotations:
        fig.add_annotation(**ann)

    # 添加产品统计
    total_products = len(product_df)
    fig.add_annotation(
        x=0.5, y=95,
        text=f"<b>共分析 {total_products} 个产品</b>",
        showarrow=False,
        font=dict(size=14, color='black'),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black',
        borderwidth=1
    )

    # 更新布局
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=20), x=0.5),
        xaxis_title="市场份额 (%)",
        yaxis_title="市场增长率 (%)",
        height=700,
        showlegend=False,
        template="plotly_white",
        xaxis=dict(range=[-0.5, 10.5], showgrid=True, gridcolor='rgba(200,200,200,0.3)'),
        yaxis=dict(range=[-50, 100], showgrid=True, gridcolor='rgba(200,200,200,0.3)'),
        hovermode='closest',
        plot_bgcolor='white'
    )

    return fig


def create_regional_sales_structure(data):
    """创建区域产品销售结构分析（TOP10产品）"""
    sales_df = data['sales_df']

    # 获取当前年份数据
    current_year = pd.Timestamp.now().year
    sales_current = sales_df[sales_df['发运月份'].dt.year == current_year]

    regions = sales_current['区域'].unique()

    # 创建子图
    fig = make_subplots(
        rows=len(regions),
        cols=1,
        subplot_titles=[f"{region}区域 TOP10 产品" for region in regions],
        vertical_spacing=0.1,
        specs=[[{'type': 'bar'}] for _ in regions]
    )

    # 为每个区域创建TOP10产品图表
    for idx, region in enumerate(regions, 1):
        region_data = sales_current[sales_current['区域'] == region]

        # 计算各产品销售额并排序
        product_sales = region_data.groupby(['产品代码', '产品简称'])['销售额'].sum().reset_index()
        product_sales = product_sales.sort_values('销售额', ascending=False).head(10)

        # 添加柱状图
        fig.add_trace(
            go.Bar(
                x=product_sales['销售额'],
                y=product_sales['产品简称'],
                orientation='h',
                text=[f"¥{val / 10000:.1f}万" for val in product_sales['销售额']],
                textposition='auto',
                marker_color='rgba(102, 126, 234, 0.8)',
                hovertemplate='<b>%{y}</b><br>销售额: ¥%{x:,.0f}<extra></extra>'
            ),
            row=idx, col=1
        )

        # 更新子图布局
        fig.update_xaxes(title_text="销售额", row=idx, col=1)
        fig.update_yaxes(tickfont=dict(size=10), row=idx, col=1)

    # 更新整体布局
    fig.update_layout(
        title=dict(text=f"<b>区域产品销售结构分析（{current_year}年）</b>", font=dict(size=20)),
        height=300 * len(regions),
        showlegend=False,
        template="plotly_white"
    )

    return fig
def optimize_smart_grid_positions(data, category):
    """智能网格布局优化"""
    # 定义每个象限的范围
    ranges = {
        'star': {'x': (1.5, 10), 'y': (20, 100)},
        'question': {'x': (0, 1.5), 'y': (20, 100)},
        'cow': {'x': (1.5, 10), 'y': (-50, 20)},
        'dog': {'x': (0, 1.5), 'y': (-50, 20)}
    }

    x_range = ranges[category]['x']
    y_range = ranges[category]['y']

    # 基于真实市场份额和增长率的位置
    x_positions = data['market_share'].values.copy()
    y_positions = data['growth_rate'].values.copy()

    # 如果产品太多且位置相近，使用网格分布
    n = len(data)
    if n > 10:  # 当产品多于10个时使用网格
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))

        x_step = (x_range[1] - x_range[0]) / (cols + 1)
        y_step = (y_range[1] - y_range[0]) / (rows + 1)

        for i, (idx, row) in enumerate(data.iterrows()):
            grid_row = i // cols
            grid_col = i % cols

            # 网格位置加上轻微随机偏移
            x_grid = x_range[0] + (grid_col + 1) * x_step
            y_grid = y_range[0] + (grid_row + 1) * y_step

            # 添加随机偏移但保持在合理范围内
            x_offset = np.random.uniform(-x_step * 0.3, x_step * 0.3)
            y_offset = np.random.uniform(-y_step * 0.3, y_step * 0.3)

            x_positions[i] = max(x_range[0], min(x_range[1], x_grid + x_offset))
            y_positions[i] = max(y_range[0], min(y_range[1], y_grid + y_offset))
    else:
        # 产品较少时，使用力导向算法优化位置
        for _ in range(30):
            for i in range(len(x_positions)):
                for j in range(i + 1, len(x_positions)):
                    dx = x_positions[i] - x_positions[j]
                    dy = y_positions[i] - y_positions[j]
                    dist = np.sqrt(dx ** 2 + dy ** 2)

                    if dist < 0.8:  # 最小距离
                        force = (0.8 - dist) / 3
                        angle = np.arctan2(dy, dx)
                        x_positions[i] += force * np.cos(angle)
                        y_positions[i] += force * np.sin(angle)
                        x_positions[j] -= force * np.cos(angle)
                        y_positions[j] -= force * np.sin(angle)

                        # 确保不超出象限边界
                        x_positions[i] = max(x_range[0], min(x_range[1], x_positions[i]))
                        y_positions[i] = max(y_range[0], min(y_range[1], y_positions[i]))
                        x_positions[j] = max(x_range[0], min(x_range[1], x_positions[j]))
                        y_positions[j] = max(y_range[0], min(y_range[1], y_positions[j]))

    return {'x': x_positions, 'y': y_positions}


def get_strategy_suggestion(category):
    """获取策略建议"""
    strategies = {
        'star': '继续加大投入，保持市场领导地位，扩大竞争优势',
        'question': '选择性投资，识别潜力产品，加快市场渗透',
        'cow': '维持现有投入，最大化利润贡献，为其他产品提供资金',
        'dog': '控制成本，考虑产品升级或逐步退出'
    }
    return strategies.get(category, '')


# 修改促销活动有效性分析函数
# 修改促销活动有效性分析函数
# 修改促销活动有效性分析函数
# 修改促销活动有效性分析函数
# 修改促销活动有效性分析函数
def analyze_promotion_effectiveness_enhanced(data, time_info):
    """基于实际促销周期的有效性分析（使用动态时间）"""
    promotion_df = data['promotion_df']
    sales_df = data['sales_df']

    # 只分析全国促销活动，去除重复
    national_promotions = promotion_df[promotion_df['所属区域'] == '全国'].drop_duplicates(
        subset=['产品代码', '促销开始供货时间', '促销结束供货时间'])

    effectiveness_results = []

    for _, promo in national_promotions.iterrows():
        product_code = promo['产品代码']

        # 解析促销时间
        try:
            promo_start = pd.to_datetime(promo['促销开始供货时间'])
            promo_end = pd.to_datetime(promo['促销结束供货时间'])
        except:
            # 如果时间解析失败，跳过该促销
            print(f"时间解析失败，跳过产品 {product_code}")
            continue

        # 计算促销期间长度（天数）
        promo_duration = (promo_end - promo_start).days + 1

        # 计算促销期间的销售数据
        promo_period_sales = sales_df[
            (sales_df['发运月份'] >= promo_start) &
            (sales_df['发运月份'] <= promo_end) &
            (sales_df['产品代码'] == product_code)
            ]['销售额'].sum()

        promo_period_boxes = sales_df[
            (sales_df['发运月份'] >= promo_start) &
            (sales_df['发运月份'] <= promo_end) &
            (sales_df['产品代码'] == product_code)
            ]['箱数'].sum()

        # 计算日均销售额
        daily_avg_sales = promo_period_sales / promo_duration if promo_duration > 0 else 0
        daily_avg_boxes = promo_period_boxes / promo_duration if promo_duration > 0 else 0

        # 计算促销前同等长度时间段的销售数据（用于环比）
        pre_promo_start = promo_start - pd.Timedelta(days=promo_duration)
        pre_promo_end = promo_start - pd.Timedelta(days=1)

        pre_promo_sales = sales_df[
            (sales_df['发运月份'] >= pre_promo_start) &
            (sales_df['发运月份'] <= pre_promo_end) &
            (sales_df['产品代码'] == product_code)
            ]['销售额'].sum()

        pre_daily_avg_sales = pre_promo_sales / promo_duration if promo_duration > 0 else 0

        # 计算去年同期数据（用于同比）
        last_year_start = promo_start - pd.DateOffset(years=1)
        last_year_end = promo_end - pd.DateOffset(years=1)

        last_year_sales = sales_df[
            (sales_df['发运月份'] >= last_year_start) &
            (sales_df['发运月份'] <= last_year_end) &
            (sales_df['产品代码'] == product_code)
            ]['销售额'].sum()

        last_year_daily_avg = last_year_sales / promo_duration if promo_duration > 0 else 0

        # 计算过去6个月该产品的日均销售额（历史平均）
        history_start = promo_start - pd.DateOffset(months=6)
        history_end = promo_start - pd.Timedelta(days=1)

        history_data = sales_df[
            (sales_df['发运月份'] >= history_start) &
            (sales_df['发运月份'] <= history_end) &
            (sales_df['产品代码'] == product_code)
            ]

        if len(history_data) > 0:
            history_days = (history_end - history_start).days + 1
            history_total_sales = history_data['销售额'].sum()
            history_daily_avg = history_total_sales / history_days
        else:
            history_daily_avg = 0

        # 计算增长率（基于日均销售额）
        # 环比增长率
        if pre_daily_avg_sales > 0:
            mom_growth = ((daily_avg_sales - pre_daily_avg_sales) / pre_daily_avg_sales * 100)
        elif daily_avg_sales > 0:
            mom_growth = 100
        else:
            mom_growth = 0

        # 同比增长率
        if last_year_daily_avg > 0:
            yoy_growth = ((daily_avg_sales - last_year_daily_avg) / last_year_daily_avg * 100)
        elif daily_avg_sales > 0:
            yoy_growth = 100
        else:
            yoy_growth = 0

        # 较历史平均增长率
        if history_daily_avg > 0:
            avg_growth = ((daily_avg_sales - history_daily_avg) / history_daily_avg * 100)
        elif daily_avg_sales > 0:
            avg_growth = 100
        else:
            avg_growth = 0

        # 判断是否为新品（去年同期无销售数据）
        is_new_product = last_year_sales < 1

        # 获取产品名称
        product_name = promo['促销产品名称']

        # 判断促销类型（短期/长期）
        is_short_term = promo_duration <= 15

        # 判断有效性 - 分层标准
        if is_new_product:
            # 新品：日均环比增长 ≥ 15%
            is_effective = mom_growth >= 15
            threshold = "15%"
            if is_effective:
                effectiveness_reason = f"✅ 有效（新品，日均环比增长{mom_growth:.1f}%≥{threshold}）"
            else:
                effectiveness_reason = f"❌ 无效（新品，日均环比增长{mom_growth:.1f}%<{threshold}）"
            positive_count = None
        else:
            # 成熟品：根据促销时长设置不同标准
            if is_short_term:
                # 短期促销：三指标中至少2个 ≥ 10%
                threshold = 10
                positive_indicators = [mom_growth >= threshold, yoy_growth >= threshold, avg_growth >= threshold]
                positive_count = sum(positive_indicators)
                is_effective = positive_count >= 2
                effectiveness_reason = f"{'✅ 有效' if is_effective else '❌ 无效'}（短期促销，{positive_count}/3项≥{threshold}%）"
            else:
                # 长期促销：三指标中至少2个 ≥ 5%
                threshold = 5
                positive_indicators = [mom_growth >= threshold, yoy_growth >= threshold, avg_growth >= threshold]
                positive_count = sum(positive_indicators)
                is_effective = positive_count >= 2
                effectiveness_reason = f"{'✅ 有效' if is_effective else '❌ 无效'}（长期促销，{positive_count}/3项≥{threshold}%）"

        effectiveness_results.append({
            'product': product_name,
            'product_code': product_code,
            'sales': promo_period_sales,  # 总销售额
            'daily_avg_sales': daily_avg_sales,  # 日均销售额
            'boxes': promo_period_boxes,
            'daily_avg_boxes': daily_avg_boxes,  # 日均箱数
            'is_effective': is_effective,
            'mom_growth': mom_growth,
            'yoy_growth': yoy_growth,
            'avg_growth': avg_growth,
            'positive_count': positive_count,
            'effectiveness_reason': effectiveness_reason,
            'pre_promo_sales': pre_promo_sales,
            'pre_daily_avg_sales': pre_daily_avg_sales,
            'last_year_sales': last_year_sales,
            'last_year_daily_avg': last_year_daily_avg,
            'history_daily_avg': history_daily_avg,
            'is_new_product': is_new_product,
            'is_short_term': is_short_term,
            'promo_start': promo_start.strftime('%Y-%m-%d'),
            'promo_end': promo_end.strftime('%Y-%m-%d'),
            'promo_duration': promo_duration,
            # 保持兼容性的字段名
            'march_sales': pre_promo_sales,
            'april_2024_sales': last_year_sales,
            'avg_2024_sales': history_daily_avg * promo_duration,  # 换算成总期望销售额
            'promotion_start_date': promo_start.strftime('%Y-%m-%d'),
            'promotion_end_date': promo_end.strftime('%Y-%m-%d'),
            'promotion_duration_days': promo_duration,
            'has_time_data': True
        })

    return pd.DataFrame(effectiveness_results)


# 修改区域覆盖率分析 - 使用不同颜色并加强悬停功能
def create_regional_coverage_analysis(data):
    """创建更易读的区域产品覆盖率分析（包含漏铺产品分析）"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']

    regional_stats = []
    regions = sales_df['区域'].unique()

    for region in regions:
        region_data = sales_df[sales_df['区域'] == region]
        products_sold = region_data[region_data['产品代码'].isin(dashboard_products)]['产品代码'].unique()
        total_products = len(dashboard_products)
        coverage_rate = (len(products_sold) / total_products * 100) if total_products > 0 else 0

        # 找出漏铺的产品
        missing_products = [p for p in dashboard_products if p not in products_sold]

        # 分析漏铺产品在其他区域的表现
        missing_product_analysis = []
        for product_code in missing_products[:10]:  # 只分析前10个漏铺产品
            # 获取产品名称
            product_info = sales_df[sales_df['产品代码'] == product_code]
            if len(product_info) > 0:
                product_name = product_info['产品简称'].iloc[0]
            else:
                product_name = f"产品{product_code}"

            # 计算在其他区域的平均销售额
            other_regions_data = sales_df[(sales_df['产品代码'] == product_code) & (sales_df['区域'] != region)]
            if len(other_regions_data) > 0:
                avg_sales_other = other_regions_data.groupby('区域')['销售额'].sum().mean()
                regions_count = other_regions_data['区域'].nunique()
            else:
                avg_sales_other = 0
                regions_count = 0

            missing_product_analysis.append({
                'name': product_name,
                'avg_sales': avg_sales_other,
                'regions': regions_count
            })

        # 按其他区域平均销售额排序
        missing_product_analysis.sort(key=lambda x: x['avg_sales'], reverse=True)

        # 创建漏铺产品详细文本
        missing_products_detail = ""
        if len(missing_product_analysis) > 0:
            missing_products_detail = "<b>漏铺产品潜力分析（TOP 10）：</b><br>"
            for i, prod in enumerate(missing_product_analysis):
                missing_products_detail += f"{i + 1}. {prod['name']}: 其他{prod['regions']}个区域平均¥{prod['avg_sales']:,.0f}<br>"

            if len(missing_products) > 10:
                missing_products_detail += f"<br>...等共{len(missing_products)}个漏铺产品"

        total_sales = region_data['销售额'].sum()
        dashboard_sales = region_data[region_data['产品代码'].isin(dashboard_products)]['销售额'].sum()

        regional_stats.append({
            'region': region,
            'coverage_rate': coverage_rate,
            'products_sold': len(products_sold),
            'total_products': total_products,
            'total_sales': total_sales,
            'dashboard_sales': dashboard_sales,
            'gap': max(0, 80 - coverage_rate),
            'missing_products': missing_products,
            'missing_count': len(missing_products),
            'missing_products_detail': missing_products_detail
        })

    df = pd.DataFrame(regional_stats).sort_values('coverage_rate', ascending=True)

    fig = go.Figure()

    # 为每个区域设置不同的颜色
    region_colors = {
        '东区': '#FF6B6B',
        '南区': '#4ECDC4',
        '西区': '#FFA500',
        '北区': '#1E90FF',
        '中区': '#9370DB'
    }

    # 获取每个区域的颜色
    colors = [region_colors.get(region, '#10b981') for region in df['region']]

    # 创建自定义hover数据
    customdata = []
    for _, row in df.iterrows():
        customdata.append([
            row['products_sold'],
            row['total_products'],
            row['missing_count'],
            row['total_sales'],
            row['dashboard_sales'],
            row['missing_products_detail']
        ])

    fig.add_trace(go.Bar(
        y=df['region'],
        x=df['coverage_rate'],
        orientation='h',
        name='覆盖率',
        marker=dict(
            color=colors,
            line=dict(width=2, color='white')
        ),
        text=[f"{rate:.1f}% ({sold}/{total}产品)" for rate, sold, total in
              zip(df['coverage_rate'], df['products_sold'], df['total_products'])],
        textposition='inside',
        textfont=dict(color='white', size=12, weight='bold'),
        hovertemplate="""<b>%{y}区域</b><br>
覆盖率: %{x:.1f}%<br>
已覆盖产品: %{customdata[0]}个<br>
总产品数: %{customdata[1]}个<br>
漏铺产品数: %{customdata[2]}个<br>
总销售额: ¥%{customdata[3]:,.0f}<br>
仪表盘产品销售额: ¥%{customdata[4]:,.0f}<br>
<br>%{customdata[5]}<br>
<extra></extra>""",
        customdata=customdata
    ))

    fig.add_vline(x=80, line_dash="dash", line_color="red",
                  annotation_text="目标: 80%", annotation_position="top")

    fig.update_layout(
        title=dict(text="<b>区域产品覆盖率分析</b>", font=dict(size=20)),
        xaxis=dict(title="覆盖率 (%)", range=[0, 105]),
        yaxis=dict(title=""),
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        bargap=0.2
    )

    return fig, df


# 修改产品关联网络图函数
def create_real_product_network(data, product_filter='all'):
    """基于真实销售数据创建产品关联网络图（显示全部仪表盘产品）"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    star_products = data['star_products']
    new_products = data['new_products']
    promotion_df = data['promotion_df']

    # 获取促销产品列表（只保留在仪表盘产品中的促销产品）
    promo_products = promotion_df[promotion_df['所属区域'] == '全国']['产品代码'].unique().tolist()
    promo_products = [p for p in promo_products if p in dashboard_products]

    # 根据筛选条件过滤产品（确保都是仪表盘产品）
    if product_filter == 'star':
        filtered_products = [p for p in dashboard_products if p in star_products]
        filter_title = "星品"
    elif product_filter == 'new':
        filtered_products = [p for p in dashboard_products if p in new_products]
        filter_title = "新品"
    elif product_filter == 'promo':
        filtered_products = [p for p in dashboard_products if p in promo_products]
        filter_title = "促销品"
    else:
        # 确保使用dashboard_products列表
        filtered_products = list(dashboard_products)  # 创建副本避免修改原列表
        filter_title = "全部仪表盘产品"

    # 如果没有产品，返回空图
    if len(filtered_products) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text=f"<b>{filter_title}产品关联网络分析</b><br><i style='font-size:14px'>暂无满足条件的产品</i>",
                font=dict(size=20)),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=700,
            plot_bgcolor='rgba(248,249,250,0.5)'
        )
        return fig

    # 严格过滤销售数据，确保只包含筛选后的产品
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(filtered_products)].copy()

    # 创建产品代码到产品名称的映射（确保唯一性）
    product_name_map = {}
    # 创建产品代码到客户集合的映射，优化性能
    product_customers_map = {}

    # 确保每个filtered_products中的产品都有映射
    for product in filtered_products:
        product_data = sales_df_filtered[sales_df_filtered['产品代码'] == product]
        if len(product_data) > 0:
            # 使用第一个出现的产品简称
            product_name = product_data['产品简称'].iloc[0]
            # 缓存客户集合
            product_customers_map[product] = set(product_data['客户名称'].unique())
        else:
            # 如果在过滤后的销售数据中找不到，尝试在所有销售数据中查找
            all_product_data = sales_df[sales_df['产品代码'] == product]
            if len(all_product_data) > 0:
                product_name = all_product_data['产品简称'].iloc[0]
            else:
                product_name = f"产品{product}"  # 使用产品代码作为名称
            product_customers_map[product] = set()
        product_name_map[product] = product_name

    product_pairs = []

    # 降低关联度门槛以显示更多连接，使用filtered_products确保只处理仪表盘产品
    for i, prod1 in enumerate(filtered_products):
        for j in range(i + 1, len(filtered_products)):
            prod2 = filtered_products[j]

            customers_prod1 = product_customers_map.get(prod1, set())
            customers_prod2 = product_customers_map.get(prod2, set())

            common_customers = customers_prod1.intersection(customers_prod2)
            total_customers = customers_prod1.union(customers_prod2)

            if len(total_customers) > 0:
                correlation = len(common_customers) / len(total_customers)

                # 降低门槛到0.2以显示更多关联
                if correlation > 0.2:
                    name1 = product_name_map[prod1]
                    name2 = product_name_map[prod2]

                    product_pairs.append((name1, name2, correlation, len(common_customers), prod1, prod2))

    # 使用产品代码作为节点（确保唯一性），但显示产品名称
    nodes = filtered_products

    # 如果没有节点，返回空图
    if len(nodes) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text=f"<b>{filter_title}产品关联网络分析</b><br><i style='font-size:14px'>暂无满足条件的产品</i>",
                font=dict(size=20)),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=700,
            plot_bgcolor='rgba(248,249,250,0.5)'
        )
        return fig

    # 使用圆形布局，适应更多节点
    pos = {}
    angle_step = 2 * np.pi / len(nodes)
    for i, node in enumerate(nodes):
        angle = i * angle_step
        # 增大圆的半径以容纳更多节点
        radius = min(1.5, 0.8 + len(nodes) * 0.02)
        pos[node] = (radius * np.cos(angle), radius * np.sin(angle))

    fig = go.Figure()

    # 添加边（降低线条粗细）
    for pair in product_pairs:
        prod1_code = pair[4]
        prod2_code = pair[5]
        x0, y0 = pos[prod1_code]
        x1, y1 = pos[prod2_code]

        color_intensity = int(255 * pair[2])
        color = f'rgba({color_intensity}, {100}, {255 - color_intensity}, {pair[2] * 0.7})'

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=pair[2] * 10, color=color),  # 降低线条粗细
            hoverinfo='text',
            text=f"""<b>产品关联分析</b><br>
产品1: {pair[0]}<br>
产品2: {pair[1]}<br>
关联度: {pair[2]:.1%}<br>
共同客户数: {pair[3]}<br>
<br><b>营销洞察:</b><br>
- 这两个产品有{pair[2]:.0%}的客户重叠<br>
- 适合捆绑销售，预计可提升{pair[2] * 30:.0f}%销量<br>
- 建议在促销时同时推广<br>
- 可设计组合套装，提高客单价""",
            showlegend=False
        ))

    # 添加节点
    node_x = [pos[node][0] for node in nodes]
    node_y = [pos[node][1] for node in nodes]

    node_sizes = []
    node_details = []
    node_colors = []
    node_texts = []  # 显示的文本

    for node in nodes:
        # node 是产品代码
        product_code = node
        product_name = product_name_map[product_code]

        # 计算连接数
        connections = sum(1 for pair in product_pairs if product_code in [pair[4], pair[5]])
        total_correlation = sum(pair[2] for pair in product_pairs if product_code in [pair[4], pair[5]])
        # 调整节点大小
        node_sizes.append(15 + min(connections * 5, 30))  # 限制最大节点尺寸

        product_data = sales_df_filtered[sales_df_filtered['产品代码'] == product_code]
        if len(product_data) > 0:
            total_sales = product_data['销售额'].sum()
            customer_count = product_data['客户名称'].nunique()
        else:
            total_sales = 0
            customer_count = 0

        # 判断产品类型并设置颜色
        product_types = []
        if product_code in star_products:
            product_types.append("星品")
        if product_code in new_products:
            product_types.append("新品")
        if product_code in promo_products:
            product_types.append("促销品")

        # 设置颜色优先级：促销品 > 新品 > 星品 > 常规品
        if product_code in promo_products:
            node_color = '#FF5722'  # 橙红色
        elif product_code in new_products:
            node_color = '#4CAF50'  # 绿色
        elif product_code in star_products:
            node_color = '#FFC107'  # 金色
        else:
            node_color = '#667eea'  # 默认紫色

        if not product_types:
            product_types.append("常规品")

        node_colors.append(node_color)
        node_texts.append(product_name)  # 显示产品名称
        product_type_text = "、".join(product_types) if product_types else "常规品"

        detail = f"""<b>{product_name} ({product_code})</b><br>
<b>产品类型:</b> {product_type_text}<br>
<br><b>网络分析:</b><br>
- 关联产品数: {connections}<br>
- 平均关联度: {total_correlation / connections if connections > 0 else 0:.1%}<br>
- 总销售额: ¥{total_sales:,.0f}<br>
- 客户数: {customer_count}<br>
<br><b>产品定位:</b><br>
{'• 核心产品，适合作为引流主打' if connections >= 5 else
        '• 重要连接点，适合交叉销售' if connections >= 3 else
        '• 特色产品，可独立推广'}<br>
<br><b>策略建议:</b><br>
{'• 作为促销活动的核心产品<br>• 与多个产品组合销售<br>• 重点培养忠实客户' if connections >= 5 else
        '• 选择2-3个关联产品捆绑<br>• 开发组合套装<br>• 提升客户粘性' if connections >= 3 else
        '• 挖掘独特卖点<br>• 寻找目标客户群<br>• 差异化营销'}"""

        node_details.append(detail)

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        ),
        text=node_texts,  # 使用产品名称
        textposition='top center',
        textfont=dict(size=8, weight='bold'),
        hoverinfo='text',
        hovertext=node_details,
        showlegend=False
    ))

    # 添加图例
    if product_filter == 'all':
        legend_items = [
            ('星品', '#FFC107'),
            ('新品', '#4CAF50'),
            ('促销品', '#FF5722'),
            ('常规品', '#667eea')
        ]
        for i, (label, color) in enumerate(legend_items):
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=12, color=color),
                name=label,
                showlegend=True
            ))

    # 调整布局以适应更多节点
    fig.update_layout(
        title=dict(
            text=f"<b>{filter_title}产品关联网络分析</b><br><i style='font-size:14px'>共{len(nodes)}个产品（仪表盘产品）</i>",
            font=dict(size=20)),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-2, 2]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-2, 2]),
        height=800,  # 增加高度
        plot_bgcolor='rgba(248,249,250,0.5)',
        hovermode='closest',
        showlegend=product_filter == 'all',
        legend=dict(
            x=1.05,
            y=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        )
    )

    return fig


# 促销活动柱状图
# 促销活动柱状图
def create_optimized_promotion_chart(promo_results, time_info):
    """创建基于日均销售额的促销活动有效性柱状图（显示动态时间范围）"""
    if len(promo_results) == 0:
        return None

    # 检查必需的字段是否存在，如果不存在则添加默认值
    required_fields = ['is_short_term', 'is_new_product', 'daily_avg_sales', 'promo_start', 'promo_end',
                       'promo_duration']
    for field in required_fields:
        if field not in promo_results.columns:
            if field == 'is_short_term':
                promo_results[field] = True  # 默认短期促销
            elif field == 'is_new_product':
                promo_results[field] = False  # 默认非新品
            elif field == 'daily_avg_sales':
                promo_results[field] = promo_results.get('sales', 0) / 30  # 估算日均
            elif field in ['promo_start', 'promo_end']:
                promo_results[field] = time_info['latest_month'].strftime('%Y-%m-01')  # 使用动态日期
            elif field == 'promo_duration':
                promo_results[field] = 30  # 默认30天

    fig = go.Figure()

    colors = ['#10b981' if is_eff else '#ef4444' for is_eff in promo_results['is_effective']]

    hover_texts = []
    for _, row in promo_results.iterrows():
        arrow_up = '↑'
        arrow_down = '↓'

        # 安全获取字段值
        is_new_product = row.get('is_new_product', False)
        is_short_term = row.get('is_short_term', True)
        daily_avg_sales = row.get('daily_avg_sales', 0)
        promo_start = row.get('promo_start', time_info['latest_month'].strftime('%Y-%m-01'))
        promo_end = row.get('promo_end', time_info['latest_month'].strftime('%Y-%m-30'))
        promo_duration = row.get('promo_duration', 30)

        # 根据是否为新品调整hover文本
        if is_new_product:
            hover_text = f"""<b>{row['product']}</b><br>
<b>产品类型:</b> 🌟 新品<br>
<b>促销时间:</b> {promo_start} 至 {promo_end} ({promo_duration}天)<br>
<b>促销期总销售额:</b> ¥{row['sales']:,.0f}<br>
<b>促销期日均销售额:</b> ¥{daily_avg_sales:,.0f}<br>
<b>有效性判断:</b> {row.get('effectiveness_reason', '分析中...')}<br>
<br><b>详细分析（基于日均销售额）:</b><br>
- 促销前日均: ¥{row.get('pre_daily_avg_sales', 0):,.0f}<br>
- 日均环比: {arrow_up if row.get('mom_growth', 0) > 0 else arrow_down}{abs(row.get('mom_growth', 0)):.1f}%<br>
- 去年同期无销售数据（新品）<br>
- 历史日均: ¥{row.get('history_daily_avg', 0):,.0f}<br>
<br><b>营销建议:</b><br>
{'继续加大推广力度，新品表现优秀' if row['is_effective'] else '需要调整新品推广策略，提升日均销售表现'}"""
        else:
            promo_type = "短期促销" if is_short_term else "长期促销"
            hover_text = f"""<b>{row['product']}</b><br>
<b>促销类型:</b> {promo_type}<br>
<b>促销时间:</b> {promo_start} 至 {promo_end} ({promo_duration}天)<br>
<b>促销期总销售额:</b> ¥{row['sales']:,.0f}<br>
<b>促销期日均销售额:</b> ¥{daily_avg_sales:,.0f}<br>
<b>有效性判断:</b> {row.get('effectiveness_reason', '分析中...')}<br>
<br><b>详细分析（基于日均销售额）:</b><br>
- 促销前日均: ¥{row.get('pre_daily_avg_sales', 0):,.0f}<br>
- 日均环比: {arrow_up if row.get('mom_growth', 0) > 0 else arrow_down}{abs(row.get('mom_growth', 0)):.1f}%<br>
- 去年同期日均: ¥{row.get('last_year_daily_avg', 0):,.0f}<br>
- 日均同比: {arrow_up if row.get('yoy_growth', 0) > 0 else arrow_down}{abs(row.get('yoy_growth', 0)):.1f}%<br>
- 历史日均: ¥{row.get('history_daily_avg', 0):,.0f}<br>
- 较历史平均: {arrow_up if row.get('avg_growth', 0) > 0 else arrow_down}{abs(row.get('avg_growth', 0)):.1f}%<br>
<br><b>营销建议:</b><br>
{'继续优化促销策略，扩大市场影响' if row['is_effective'] else '需要重新评估促销策略，优化投入产出比'}"""
        hover_texts.append(hover_text)

    # 使用日均销售额作为Y轴数据
    y_values = promo_results['daily_avg_sales'].fillna(0).values
    x_labels = promo_results['product'].values

    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"¥{val:,.0f}/天" for val in y_values],
        textposition='auto',  # 改为auto防止重影
        textfont=dict(size=11, weight='bold'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        width=0.6
    ))

    effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
    max_sales = y_values.max() if len(y_values) > 0 and y_values.max() > 0 else 1000

    # 计算促销时间范围 - 使用动态时间
    try:
        all_start_dates = pd.to_datetime(promo_results['promo_start'])
        all_end_dates = pd.to_datetime(promo_results['promo_end'])
        time_range = f"{all_start_dates.min().strftime('%Y-%m-%d')} 至 {all_end_dates.max().strftime('%Y-%m-%d')}"
    except:
        time_range = time_info['data_range']

    # 统计促销类型
    short_term_count = promo_results.get('is_short_term', pd.Series([True] * len(promo_results))).sum()
    long_term_count = len(promo_results) - short_term_count
    new_product_count = promo_results.get('is_new_product', pd.Series([False] * len(promo_results))).sum()

    title_text = f"<b>全国促销活动有效性分析（基于日均销售额）</b><br>有效率: {effectiveness_rate:.1f}% ({promo_results['is_effective'].sum()}/{len(promo_results)})"

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title="促销产品", tickangle=-30 if len(x_labels) > 6 else 0),
        yaxis=dict(title="日均销售额 (¥)", range=[0, max_sales * 1.3]),
        height=600,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        bargap=0.3
    )

    # 添加日均销售额平均线
    if len(y_values) > 0 and y_values.mean() > 0:
        avg_daily_sales = y_values.mean()
        fig.add_hline(
            y=avg_daily_sales,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"日均平均: ¥{avg_daily_sales:,.0f}",
            annotation_position="right"
        )

    return fig



def calculate_effective_products_rate(sales_df, dashboard_products):
    """计算有效产品率（月均销售≥15箱）"""
    # 过滤仪表盘产品
    df = sales_df[sales_df['产品代码'].isin(dashboard_products)]

    # 计算每个产品的月均销售箱数
    product_monthly = df.groupby('产品代码').agg({
        '箱数': 'sum',
        '发运月份': 'nunique'
    })

    product_monthly['月均箱数'] = product_monthly['箱数'] / product_monthly['发运月份']

    # 计算有效产品数
    effective_products = (product_monthly['月均箱数'] >= 15).sum()
    total_products = len(product_monthly)

    return (effective_products / total_products * 100) if total_products > 0 else 0


# 新增：有效产品详细分析
def analyze_effective_products(data, dimension='national', selected_region=None):
    """分析有效产品（月均销售≥15箱）"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']

    # 根据维度过滤数据
    if dimension == 'regional' and selected_region:
        df = sales_df[(sales_df['产品代码'].isin(dashboard_products)) &
                      (sales_df['区域'] == selected_region)]
    else:
        df = sales_df[sales_df['产品代码'].isin(dashboard_products)]

    # 计算每个产品的月均销售
    product_stats = []
    for product in dashboard_products:
        product_data = df[df['产品代码'] == product]

        if len(product_data) > 0:
            total_boxes = product_data['箱数'].sum()
            total_sales = product_data['销售额'].sum()
            months_sold = product_data['发运月份'].nunique()

            monthly_avg_boxes = total_boxes / months_sold if months_sold > 0 else 0
            is_effective = monthly_avg_boxes >= 15

            # 获取产品名称
            product_name = product_data['产品简称'].iloc[0]

            product_stats.append({
                'product_code': product,
                'product_name': product_name,
                'total_boxes': total_boxes,
                'total_sales': total_sales,
                'months_sold': months_sold,
                'monthly_avg_boxes': monthly_avg_boxes,
                'is_effective': is_effective,
                'effectiveness_gap': max(0, 15 - monthly_avg_boxes)
            })

    return pd.DataFrame(product_stats)


# 新增：创建有效产品分析图表
def create_effective_products_chart(product_df, title="有效产品分析"):
    """创建有效产品分析图表"""
    if len(product_df) == 0:
        return go.Figure(), 0

    # 排序：有效产品在前，按月均箱数降序
    product_df = product_df.sort_values(['is_effective', 'monthly_avg_boxes'],
                                        ascending=[False, False])

    # 显示所有产品
    display_df = product_df

    colors = ['#10b981' if eff else '#ef4444' for eff in display_df['is_effective']]

    fig = go.Figure()

    hover_texts = []
    for _, row in display_df.iterrows():
        status = "✅ 有效" if row['is_effective'] else "❌ 无效"
        gap_text = f"距离标准还差: {row['effectiveness_gap']:.1f}箱" if not row[
            'is_effective'] else "超出标准: {row['monthly_avg_boxes']-15:.1f}箱"

        hover_text = f"""<b>{row['product_name']} ({row['product_code']})</b><br>
<b>月均销售:</b> {row['monthly_avg_boxes']:.1f}箱<br>
<b>有效性:</b> {status}<br>
<b>{gap_text}</b><br>
<br><b>详细数据:</b><br>
- 总销售箱数: {row['total_boxes']:,.0f}箱<br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 销售月数: {row['months_sold']}个月<br>
<br><b>策略建议:</b><br>
{'继续保持良好势头，可作为主推产品' if row['is_effective'] else '需要加强市场推广，提升销售表现'}"""
        hover_texts.append(hover_text)

    fig.add_trace(go.Bar(
        x=display_df['product_name'],
        y=display_df['monthly_avg_boxes'],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{val:.1f}" for val in display_df['monthly_avg_boxes']],
        textposition='auto',  # 改为auto防止重影
        textfont=dict(size=10),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts
    ))

    # 添加有效产品线
    fig.add_hline(y=15, line_dash="dash", line_color="red",
                  annotation_text="有效产品标准: 15箱/月",
                  annotation_position="right")

    # 计算统计信息
    total_products = len(product_df)
    effective_count = product_df['is_effective'].sum()
    effectiveness_rate = (effective_count / total_products * 100) if total_products > 0 else 0

    # 根据产品数量调整图表高度
    chart_height = max(600, 400 + len(display_df) * 15)

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br>有效产品率: {effectiveness_rate:.1f}% ({effective_count}/{total_products})",
            font=dict(size=20),
            x=0.5
        ),
        xaxis=dict(title="产品名称", tickangle=-45),
        yaxis=dict(title="月均销售 (箱)", range=[0, max(display_df['monthly_avg_boxes'].max() * 1.2, 20)]),
        height=chart_height,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        bargap=0.2
    )

    return fig, effectiveness_rate


# 新增：产品环比同比分析函数
def analyze_product_growth_rates(data, time_info):
    """分析所有仪表盘产品的环比同比增长率（使用动态时间）"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']

    # 使用动态时间
    latest_month = time_info['latest_month']
    previous_month = time_info['previous_month']
    same_month_last_year = time_info['same_month_last_year']

    product_growth_stats = []

    for product in dashboard_products:
        # 当期数据
        current_sales = sales_df[(sales_df['发运月份'] == latest_month) &
                                 (sales_df['产品代码'] == product)]['销售额'].sum()

        current_boxes = sales_df[(sales_df['发运月份'] == latest_month) &
                                 (sales_df['产品代码'] == product)]['箱数'].sum()

        # 上期数据
        previous_sales = sales_df[(sales_df['发运月份'] == previous_month) &
                                  (sales_df['产品代码'] == product)]['销售额'].sum()

        previous_boxes = sales_df[(sales_df['发运月份'] == previous_month) &
                                  (sales_df['产品代码'] == product)]['箱数'].sum()

        # 去年同期数据
        last_year_sales = sales_df[(sales_df['发运月份'] == same_month_last_year) &
                                   (sales_df['产品代码'] == product)]['销售额'].sum()

        last_year_boxes = sales_df[(sales_df['发运月份'] == same_month_last_year) &
                                   (sales_df['产品代码'] == product)]['箱数'].sum()

        # 获取产品名称
        product_data = sales_df[sales_df['产品代码'] == product]
        if len(product_data) > 0:
            product_name = product_data['产品简称'].iloc[0]
        else:
            product_name = product

        # 计算环比增长率
        if previous_sales > 0:
            mom_sales_growth = ((current_sales - previous_sales) / previous_sales * 100)
        elif current_sales > 0:
            mom_sales_growth = 100
        else:
            mom_sales_growth = 0

        if previous_boxes > 0:
            mom_boxes_growth = ((current_boxes - previous_boxes) / previous_boxes * 100)
        elif current_boxes > 0:
            mom_boxes_growth = 100
        else:
            mom_boxes_growth = 0

        # 计算同比增长率
        if last_year_sales > 0:
            yoy_sales_growth = ((current_sales - last_year_sales) / last_year_sales * 100)
        elif current_sales > 0:
            yoy_sales_growth = 100
        else:
            yoy_sales_growth = 0

        if last_year_boxes > 0:
            yoy_boxes_growth = ((current_boxes - last_year_boxes) / last_year_boxes * 100)
        elif current_boxes > 0:
            yoy_boxes_growth = 100
        else:
            yoy_boxes_growth = 0

        # 判断是否为新品
        is_new_product = last_year_sales == 0 and last_year_boxes == 0

        product_growth_stats.append({
            'product_code': product,
            'product_name': product_name,
            'current_sales': current_sales,
            'current_boxes': current_boxes,
            'previous_sales': previous_sales,
            'previous_boxes': previous_boxes,
            'last_year_sales': last_year_sales,
            'last_year_boxes': last_year_boxes,
            'mom_sales_growth': mom_sales_growth,
            'mom_boxes_growth': mom_boxes_growth,
            'yoy_sales_growth': yoy_sales_growth,
            'yoy_boxes_growth': yoy_boxes_growth,
            'is_new_product': is_new_product,
            'has_current_sales': current_sales > 0 or current_boxes > 0
        })

    return pd.DataFrame(product_growth_stats)


# 新增：创建环比同比分析图表
def create_growth_rate_charts(growth_df, time_info):
    """创建环比同比分析图表（显示动态时间信息）"""
    # 只显示有当前销售数据的产品
    active_products = growth_df[growth_df['has_current_sales'] == True].copy()

    if len(active_products) == 0:
        return None, None

    # 按销售额排序
    active_products = active_products.sort_values('current_sales', ascending=False)

    # 环比分析图
    fig_mom = go.Figure()

    # 颜色根据环比增长率
    mom_colors = ['#10b981' if growth > 0 else '#ef4444' for growth in active_products['mom_sales_growth']]

    hover_texts_mom = []
    for _, row in active_products.iterrows():
        arrow_up = '↑'
        arrow_down = '↓'

        # 使用动态时间信息
        current_month = time_info['latest_month'].strftime('%Y-%m')
        previous_month = time_info['previous_month'].strftime('%Y-%m')

        hover_text = f"""<b>{row['product_name']} ({row['product_code']})</b><br>
<br><b>环比分析（{current_month} vs {previous_month}）:</b><br>
- 当月销售额: ¥{row['current_sales']:,.0f}<br>
- 上月销售额: ¥{row['previous_sales']:,.0f}<br>
- 销售额环比: {arrow_up if row['mom_sales_growth'] > 0 else arrow_down}{abs(row['mom_sales_growth']):.1f}%<br>
- 当月箱数: {row['current_boxes']:,.0f}箱<br>
- 上月箱数: {row['previous_boxes']:,.0f}箱<br>
- 箱数环比: {arrow_up if row['mom_boxes_growth'] > 0 else arrow_down}{abs(row['mom_boxes_growth']):.1f}%<br>
<br><b>分析结论:</b><br>
{'销售表现良好，继续保持' if row['mom_sales_growth'] > 0 else '销售下滑，需要关注'}"""
        hover_texts_mom.append(hover_text)

    fig_mom.add_trace(go.Bar(
        x=active_products['product_name'],
        y=active_products['mom_sales_growth'],
        marker=dict(color=mom_colors, line=dict(width=0)),
        text=[f"{val:.1f}%" for val in active_products['mom_sales_growth']],
        textposition='auto',  # 改为auto防止重影
        textfont=dict(size=10),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts_mom,
        name='环比增长率'
    ))

    fig_mom.add_hline(y=0, line_dash="solid", line_color="gray", line_width=2)

    positive_count_mom = (active_products['mom_sales_growth'] > 0).sum()
    total_count = len(active_products)

    # 使用动态时间信息更新标题
    current_month = time_info['latest_month'].strftime('%Y年%m月')
    previous_month = time_info['previous_month'].strftime('%Y年%m月')

    fig_mom.update_layout(
        title=dict(
            text=f"<b>产品环比增长率分析（{current_month} vs {previous_month}）</b><br>正增长产品: {positive_count_mom}/{total_count} ({positive_count_mom / total_count * 100:.1f}%)",
            font=dict(size=20),
            x=0.5
        ),
        xaxis=dict(title="产品名称", tickangle=-45),
        yaxis=dict(title="环比增长率 (%)", range=[active_products['mom_sales_growth'].min() * 1.2,
                                                  active_products['mom_sales_growth'].max() * 1.2]),
        height=600,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white'
    )

    # 同比分析图
    fig_yoy = go.Figure()

    # 颜色根据同比增长率（新品用特殊颜色）
    yoy_colors = []
    for _, row in active_products.iterrows():
        if row['is_new_product']:
            yoy_colors.append('#FFC107')  # 新品用金色
        elif row['yoy_sales_growth'] > 0:
            yoy_colors.append('#10b981')  # 正增长用绿色
        else:
            yoy_colors.append('#ef4444')  # 负增长用红色

    hover_texts_yoy = []
    for _, row in active_products.iterrows():
        arrow_up = '↑'
        arrow_down = '↓'

        # 使用动态时间信息
        current_month = time_info['latest_month'].strftime('%Y-%m')
        last_year_month = time_info['same_month_last_year'].strftime('%Y-%m')

        if row['is_new_product']:
            hover_text = f"""<b>{row['product_name']} ({row['product_code']})</b><br>
<b>产品类型:</b> 🌟 新品<br>
<br><b>同比分析（{current_month} vs {last_year_month}）:</b><br>
- 当期销售额: ¥{row['current_sales']:,.0f}<br>
- 去年同期: 无数据（新品）<br>
- 当期箱数: {row['current_boxes']:,.0f}箱<br>
<br><b>分析结论:</b><br>
新品上市，需要重点关注市场反馈"""
        else:
            hover_text = f"""<b>{row['product_name']} ({row['product_code']})</b><br>
<br><b>同比分析（{current_month} vs {last_year_month}）:</b><br>
- 当期销售额: ¥{row['current_sales']:,.0f}<br>
- 去年同期: ¥{row['last_year_sales']:,.0f}<br>
- 销售额同比: {arrow_up if row['yoy_sales_growth'] > 0 else arrow_down}{abs(row['yoy_sales_growth']):.1f}%<br>
- 当期箱数: {row['current_boxes']:,.0f}箱<br>
- 去年箱数: {row['last_year_boxes']:,.0f}箱<br>
- 箱数同比: {arrow_up if row['yoy_boxes_growth'] > 0 else arrow_down}{abs(row['yoy_boxes_growth']):.1f}%<br>
<br><b>分析结论:</b><br>
{'同比增长良好，产品生命力强' if row['yoy_sales_growth'] > 0 else '同比下滑，需要产品升级或调整'}"""
        hover_texts_yoy.append(hover_text)

    fig_yoy.add_trace(go.Bar(
        x=active_products['product_name'],
        y=active_products['yoy_sales_growth'],
        marker=dict(color=yoy_colors, line=dict(width=0)),
        text=[f"{row['yoy_sales_growth']:.1f}%" if not row['is_new_product'] else "新品"
              for _, row in active_products.iterrows()],
        textposition='auto',  # 改为auto防止重影
        textfont=dict(size=10),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts_yoy,
        name='同比增长率'
    ))

    fig_yoy.add_hline(y=0, line_dash="solid", line_color="gray", line_width=2)

    # 添加图例
    fig_yoy.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='#10b981'),
        name='正增长',
        showlegend=True
    ))

    fig_yoy.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='#ef4444'),
        name='负增长',
        showlegend=True
    ))

    fig_yoy.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='#FFC107'),
        name='新品',
        showlegend=True
    ))

    positive_count_yoy = ((active_products['yoy_sales_growth'] > 0) & (~active_products['is_new_product'])).sum()
    new_count = active_products['is_new_product'].sum()
    non_new_count = total_count - new_count

    # 使用动态时间信息更新标题
    current_year = time_info['current_year']
    last_year = current_year - 1

    fig_yoy.update_layout(
        title=dict(
            text=f"<b>产品同比增长率分析（{current_year} vs {last_year}）</b><br>正增长: {positive_count_yoy}/{non_new_count}个老品 | 新品: {new_count}个",
            font=dict(size=20),
            x=0.5
        ),
        xaxis=dict(title="产品名称", tickangle=-45),
        yaxis=dict(title="同比增长率 (%)", range=[active_products['yoy_sales_growth'].min() * 1.2,
                                                  active_products['yoy_sales_growth'].max() * 1.2]),
        height=600,
        hovermode='closest',
        plot_bgcolor='white',
        legend=dict(
            x=1.02,
            y=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        )
    )

    return fig_mom, fig_yoy


# 主页面
# 主页面
def main():
    # 检查认证状态 - 使用附件一的认证系统
    if not fixed_authentication_check():
        show_auth_required_page()
        st.stop()

    st.markdown("""
    <div class="main-header">
        <h1>📦 产品组合分析</h1>
        <p>基于真实销售数据的智能分析系统</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    data = load_data()
    if data is None:
        return

    # 获取时间信息
    time_info = data['time_info']

    # 创建标签页
    tab_names = [
        "📊 产品情况总览",
        "🎯 BCG产品矩阵",
        "🚀 全国促销活动有效性",
        "📈 星品新品达成",
        "🔗 市场网络与覆盖分析"
    ]

    tabs = st.tabs(tab_names)

    # Tab 1: 产品情况总览 - 只保留指标卡片
    with tabs[0]:
        metrics = calculate_comprehensive_metrics(
            data['sales_df'],
            data['star_products'],
            data['new_products'],
            data['dashboard_products'],
            data['promotion_df'],
            time_info
        )

        # 第一行：4个卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # 将销售额转换为更简洁的格式（四舍五入）
            sales_display = round(metrics['total_sales'])  # 四舍五入到整数
            if sales_display >= 10000:
                sales_text = f"¥{sales_display / 10000:.0f}万"
            else:
                sales_text = f"¥{sales_display:.0f}"

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{sales_text}</div>
                <div class="metric-label">💰 {metrics['current_year']}总销售额</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#10b981' if metrics['jbp_status'] == 'YES' else '#ef4444'}">
                    {metrics['jbp_status']}
                </div>
                <div class="metric-label">✅ JBP符合度</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['penetration_rate']:.0f}%</div>
                <div class="metric-label">📊 新品渗透率</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['promo_effectiveness']:.0f}%</div>
                <div class="metric-label" style="font-size: 0.95rem;">🚀 促销有效性</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 第二行：4个卡片
        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['new_ratio']:.0f}%</div>
                <div class="metric-label">🌟 新品占比</div>
            </div>
            """, unsafe_allow_html=True)

        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['star_ratio']:.0f}%</div>
                <div class="metric-label">⭐ 星品占比</div>
            </div>
            """, unsafe_allow_html=True)

        with col7:
            status_color = '#10b981' if metrics['total_ratio'] >= 20 else '#ef4444'
            status_text = "✅ 达标" if metrics['total_ratio'] >= 20 else "❌ 未达标"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_ratio']:.0f}%</div>
                <div class="metric-label" style="font-size: 0.95rem;">🎯 星品&新品占比</div>
                <div style="color: {status_color}; font-size: 0.85rem; margin-top: 0.5rem;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with col8:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['effective_products_rate']:.0f}%</div>
                <div class="metric-label">📦 有效产品率</div>
                <div class="metric-sublabel">月均≥15箱</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 第三行：有效产品相关指标（居中显示2个）
        col_empty1, col9, col10, col_empty2 = st.columns([1, 2, 2, 1])

        with col9:
            st.markdown(f"""
            <div class="metric-card" style="animation-delay: 0.9s;">
                <div class="metric-value">{metrics['effective_products_count']}</div>
                <div class="metric-label">✅ 有效产品数</div>
                <div class="metric-sublabel">月均≥15箱</div>
            </div>
            """, unsafe_allow_html=True)

        with col10:
            st.markdown(f"""
            <div class="metric-card" style="animation-delay: 1.0s;">
                <div class="metric-value">{metrics['avg_effective_sales']:.0f}箱</div>
                <div class="metric-label">📈 月均销售量</div>
                <div class="metric-sublabel">有效产品平均</div>
            </div>
            """, unsafe_allow_html=True)

    # Tab 2: BCG产品矩阵
    with tabs[1]:
        # 选择维度控件
        bcg_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True, key="bcg_dimension")

        # 获取分析数据 - 分析所有产品
        if bcg_dimension == "🌏 全国维度":
            product_analysis = analyze_product_bcg_cached(
                data['sales_df'],
                None,  # 传入None表示分析所有产品
                time_info
            )
            title = "BCG产品矩阵（全产品）"
            selected_region = None
        else:
            regions = data['sales_df']['区域'].unique()
            selected_region = st.selectbox("🗺️ 选择区域", regions)
            product_analysis = analyze_product_bcg_cached(
                data['sales_df'],
                None,  # 传入None表示分析所有产品
                time_info,
                selected_region
            )
            title = f"{selected_region}区域 BCG产品矩阵（全产品）"

        # 显示BCG矩阵图表
        if len(product_analysis) > 0:
            with st.spinner('正在生成BCG矩阵图...'):
                fig = plot_bcg_matrix(product_analysis, title=title)
            st.plotly_chart(fig, use_container_width=True)

            # JBP符合度分析
            total_sales = product_analysis['sales'].sum()
            cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
            star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])][
                'sales'].sum()
            dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()

            cow_ratio = cow_sales / total_sales * 100 if total_sales > 0 else 0
            star_question_ratio = star_question_sales / total_sales * 100 if total_sales > 0 else 0
            dog_ratio = dog_sales / total_sales * 100 if total_sales > 0 else 0

            region_prefix = f"{selected_region}区域 " if bcg_dimension == "🗺️ 分区域维度" else ""

            with st.expander(f"📊 {region_prefix}JBP符合度分析", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("现金牛产品占比", f"{cow_ratio:.1f}%",
                              "✅ 符合" if 45 <= cow_ratio <= 50 else "❌ 不符合",
                              delta_color="normal" if 45 <= cow_ratio <= 50 else "inverse")
                    st.caption("目标: 45%-50%")

                with col2:
                    st.metric("明星&问号产品占比", f"{star_question_ratio:.1f}%",
                              "✅ 符合" if 40 <= star_question_ratio <= 45 else "❌ 不符合",
                              delta_color="normal" if 40 <= star_question_ratio <= 45 else "inverse")
                    st.caption("目标: 40%-45%")

                with col3:
                    st.metric("瘦狗产品占比", f"{dog_ratio:.1f}%",
                              "✅ 符合" if dog_ratio <= 10 else "❌ 不符合",
                              delta_color="normal" if dog_ratio <= 10 else "inverse")
                    st.caption("目标: ≤10%")
        else:
            st.warning("该区域暂无产品数据")

    # Tab 3: 全国促销活动有效性
    with tabs[2]:
        # 添加缓存清理按钮
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("🔄 刷新数据", key="clear_promo_cache"):
                clear_promotion_cache()
                st.rerun()

        try:
            promo_results = analyze_promotion_cached(data['promotion_df'], data['sales_df'], time_info)

            if len(promo_results) > 0:
                # 计算有效率并显示在标题中
                effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100

                # 促销活动效果图表
                st.markdown(f"""
                <div class="promo-header">
                    <h2>🚀 全国促销活动有效性分析</h2>
                    <h3>基于实际促销周期和日均销售额的精确分析 | 总体有效率: {effectiveness_rate:.1f}% ({promo_results['is_effective'].sum()}/{len(promo_results)})</h3>
                </div>
                """, unsafe_allow_html=True)

                fig = create_optimized_promotion_chart(promo_results, time_info)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                # 促销洞察分析（简化版）
                with st.expander("💡 促销活动深度洞察（基于日均销售额分析）", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        effective_products = promo_results[promo_results['is_effective'] == True]
                        ineffective_products = promo_results[promo_results['is_effective'] == False]

                        # 有效产品统计
                        avg_daily_sales_effective = effective_products.get('daily_avg_sales',
                                                                           pd.Series([0])).mean() if len(
                            effective_products) > 0 else 0
                        avg_duration_effective = effective_products.get('promo_duration',
                                                                        pd.Series([30])).mean() if len(
                            effective_products) > 0 else 0
                        avg_mom_effective = effective_products.get('mom_growth', pd.Series([0])).mean() if len(
                            effective_products) > 0 else 0

                        effective_text = f"""**🎯 有效促销产品特征**
- 有效产品数: {len(effective_products)}个
- 平均日均销售额: ¥{avg_daily_sales_effective:,.0f}
- 平均促销时长: {avg_duration_effective:.1f}天
- 平均日均环比增长: {avg_mom_effective:.1f}%
- 平均总销售额: ¥{effective_products['sales'].mean() if len(effective_products) > 0 else 0:,.0f}"""

                        st.info(effective_text)

                    with col2:
                        # 无效产品统计
                        avg_daily_sales_ineffective = ineffective_products.get('daily_avg_sales',
                                                                               pd.Series([0])).mean() if len(
                            ineffective_products) > 0 else 0
                        avg_duration_ineffective = ineffective_products.get('promo_duration',
                                                                            pd.Series([30])).mean() if len(
                            ineffective_products) > 0 else 0
                        avg_mom_ineffective = ineffective_products.get('mom_growth', pd.Series([0])).mean() if len(
                            ineffective_products) > 0 else 0

                        ineffective_text = f"""**⚠️ 无效促销产品分析**
- 无效产品数: {len(ineffective_products)}个
- 平均日均销售额: ¥{avg_daily_sales_ineffective:,.0f}
- 平均促销时长: {avg_duration_ineffective:.1f}天
- 平均日均环比增长: {avg_mom_ineffective:.1f}%
- 平均总销售额: ¥{ineffective_products['sales'].mean() if len(ineffective_products) > 0 else 0:,.0f}"""

                        st.warning(ineffective_text)

                    # 新品促销分析
                    new_products_promo = promo_results[promo_results.get('is_new_product', False) == True]
                    if len(new_products_promo) > 0:
                        new_effective = new_products_promo['is_effective'].sum()
                        new_avg_daily = new_products_promo.get('daily_avg_sales', pd.Series([0])).mean()
                        new_avg_growth = new_products_promo.get('mom_growth', pd.Series([0])).mean()

                        new_promo_text = f"""**🌟 新品促销分析**
- 新品促销数: {len(new_products_promo)}个
- 有效新品数: {new_effective}个
- 新品有效率: {new_effective / len(new_products_promo) * 100:.1f}%
- 新品平均日均销售额: ¥{new_avg_daily:,.0f}
- 新品平均日均环比增长: {new_avg_growth:.1f}%
- 判断标准: 新品需日均环比增长≥15%"""

                        st.success(new_promo_text)
            else:
                st.info("暂无全国促销活动数据")
        except Exception as e:
            st.error(f"数据分析出现问题，请点击'🔄 刷新数据'按钮重新加载。错误信息：{str(e)}")
            if st.button("🔄 立即刷新", key="immediate_refresh"):
                clear_promotion_cache()
                st.rerun()

    # Tab 4: 星品新品达成
    with tabs[3]:
        # 选择控件
        view_type = st.radio("选择分析视角", ["按区域", "按销售员", "趋势分析"], horizontal=True, key="star_new_view")

        sales_df = data['sales_df']
        star_products = data['star_products']
        new_products = data['new_products']
        star_new_products = list(set(star_products + new_products))
        current_year = time_info['current_year']

        if view_type == "按区域":
            # 区域分析 - 使用当前年份数据
            region_stats = []
            current_year_data = sales_df[sales_df['发运月份'].dt.year == current_year]

            for region in current_year_data['区域'].unique():
                region_data = current_year_data[current_year_data['区域'] == region]
                total_sales = region_data['销售额'].sum()
                star_new_sales = region_data[region_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0

                total_customers = region_data['客户名称'].nunique()
                star_new_customers = region_data[region_data['产品代码'].isin(star_new_products)]['客户名称'].nunique()

                region_stats.append({
                    'region': region,
                    'ratio': ratio,
                    'achieved': ratio >= 20,
                    'total_sales': total_sales,
                    'star_new_sales': star_new_sales,
                    'customers': f"{star_new_customers}/{total_customers}",
                    'penetration': star_new_customers / total_customers * 100 if total_customers > 0 else 0
                })

            region_df = pd.DataFrame(region_stats)

            fig = go.Figure()

            colors = ['#10b981' if ach else '#f59e0b' for ach in region_df['achieved']]

            hover_texts = []
            for _, row in region_df.iterrows():
                hover_text = f"""<b>{row['region']}</b><br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>达成情况:</b> {'✅ 已达标' if row['achieved'] else '❌ 未达标'}<br>
<br><b>销售分析:</b><br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
- 覆盖客户: {row['customers']}<br>
- 客户渗透率: {row['penetration']:.1f}%<br>
<br><b>行动建议:</b><br>
{'继续保持，可作为其他区域标杆' if row['achieved'] else f"距离目标还差{20 - row['ratio']:.1f}%，需重点提升"}"""
                hover_texts.append(hover_text)

            fig.add_trace(go.Bar(
                x=region_df['region'],
                y=region_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in region_df['ratio']],
                textposition='auto',  # 改为auto防止重影
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))

            fig.add_hline(y=20, line_dash="dash", line_color="red",
                          annotation_text="目标线 20%", annotation_position="right")

            fig.update_layout(
                title=f"各区域星品&新品占比达成情况（{current_year}年）",
                xaxis_title="销售区域",
                yaxis_title="占比 (%)",
                height=500,
                showlegend=False,
                hovermode='closest'
            )

            st.plotly_chart(fig, use_container_width=True)

        elif view_type == "按销售员":
            # 销售员分析 - 使用当前年份数据
            salesperson_stats = []
            current_year_data = sales_df[sales_df['发运月份'].dt.year == current_year]

            for person in current_year_data['销售员'].unique():
                person_data = current_year_data[current_year_data['销售员'] == person]
                total_sales = person_data['销售额'].sum()
                star_new_sales = person_data[person_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0

                total_customers = person_data['客户名称'].nunique()
                star_new_customers = person_data[person_data['产品代码'].isin(star_new_products)]['客户名称'].nunique()

                salesperson_stats.append({
                    'salesperson': person,
                    'ratio': ratio,
                    'achieved': ratio >= 20,
                    'total_sales': total_sales,
                    'star_new_sales': star_new_sales,
                    'customers': f"{star_new_customers}/{total_customers}",
                    'region': person_data['区域'].mode().iloc[0] if len(person_data) > 0 else ''
                })

            person_df = pd.DataFrame(salesperson_stats).sort_values('ratio', ascending=False)

            fig = go.Figure()

            colors = ['#10b981' if ach else '#f59e0b' for ach in person_df['achieved']]

            hover_texts = []
            for _, row in person_df.iterrows():
                hover_text = f"""<b>{row['salesperson']}</b><br>
<b>所属区域:</b> {row['region']}<br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>达成情况:</b> {'✅ 已达标' if row['achieved'] else '❌ 未达标'}<br>
<br><b>销售分析:</b><br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
- 覆盖客户: {row['customers']}<br>
<br><b>绩效建议:</b><br>
{'优秀销售员，可分享经验' if row['achieved'] else '需要培训和支持，提升产品知识'}"""
                hover_texts.append(hover_text)

            fig.add_trace(go.Bar(
                x=person_df['salesperson'],
                y=person_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in person_df['ratio']],
                textposition='auto',  # 改为auto防止重影
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))

            fig.add_hline(y=20, line_dash="dash", line_color="red",
                          annotation_text="目标线 20%", annotation_position="right")

            fig.update_layout(
                title=f"全部销售员星品&新品占比达成情况（{current_year}年，共{len(person_df)}人）",
                xaxis_title="销售员",
                yaxis_title="占比 (%)",
                height=600,
                showlegend=False,
                hovermode='closest',
                xaxis={'tickangle': -45}
            )

            st.plotly_chart(fig, use_container_width=True)

            achieved_count = person_df['achieved'].sum()
            st.info(
                f"📊 达成率统计：{achieved_count}/{len(person_df)}人达标（{achieved_count / len(person_df) * 100:.1f}%）")

        else:  # 趋势分析
            # 趋势分析 - 动态时间范围
            monthly_stats = []

            # 动态生成月份范围
            latest_month = time_info['latest_month']
            start_month = latest_month - pd.DateOffset(months=12)  # 显示最近12个月

            for month in pd.date_range(start=start_month, end=latest_month, freq='M'):
                month_data = sales_df[
                    (sales_df['发运月份'].dt.year == month.year) &
                    (sales_df['发运月份'].dt.month == month.month)
                    ]

                if len(month_data) > 0:
                    total_sales = month_data['销售额'].sum()
                    star_new_sales = month_data[month_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                    ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0

                    monthly_stats.append({
                        'month': month.strftime('%Y-%m'),
                        'ratio': ratio,
                        'total_sales': total_sales,
                        'star_new_sales': star_new_sales
                    })

            trend_df = pd.DataFrame(monthly_stats)

            fig = go.Figure()

            hover_texts = []
            for _, row in trend_df.iterrows():
                hover_text = f"""<b>{row['month']}</b><br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>总销售额:</b> ¥{row['total_sales']:,.0f}<br>
<b>星品新品销售额:</b> ¥{row['star_new_sales']:,.0f}<br>
<br><b>趋势分析:</b><br>
{'保持良好势头' if row['ratio'] >= 20 else '需要加强推广'}"""
                hover_texts.append(hover_text)

            fig.add_trace(go.Scatter(
                x=trend_df['month'],
                y=trend_df['ratio'],
                mode='lines+markers',
                name='星品&新品占比',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))

            fig.add_hline(y=20, line_dash="dash", line_color="red",
                          annotation_text="目标线 20%", annotation_position="right")

            fig.update_layout(
                title=f"星品&新品占比月度趋势（最近12个月至{latest_month.strftime('%Y-%m')}）",
                xaxis_title="月份",
                yaxis_title="占比 (%)",
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

    # Tab 5: 市场网络与覆盖分析
    with tabs[4]:
        # 选择控件
        analysis_type = st.radio("选择分析类型",
                                 ["🔗 产品关联网络", "📍 区域销售结构", "🌟 新品渗透率",
                                  "✅ 有效产品分析", "📊 环比同比分析"],
                                 horizontal=True, key="market_analysis_type")

        if analysis_type == "🔗 产品关联网络":
            # 产品关联网络
            st.subheader("产品关联网络分析")

            # 添加产品筛选器
            col1, col2 = st.columns([1, 3])
            with col1:
                product_filter = st.selectbox(
                    "🎯 筛选产品类型",
                    options=['all', 'star', 'new', 'promo'],
                    format_func=lambda x: {
                        'all': '全部仪表盘产品',
                        'star': '⭐ 星品',
                        'new': '🌟 新品',
                        'promo': '🚀 促销品'
                    }[x],
                    key="network_filter"
                )

            with col2:
                if product_filter == 'all':
                    st.info("💡 **节点颜色说明**: 🟡 星品 | 🟢 新品 | 🟠 促销品 | 🟣 常规品")
                elif product_filter == 'star':
                    st.info("⭐ **星品关联网络**: 展示仪表盘产品中所有星品之间的客户关联关系")
                elif product_filter == 'new':
                    st.info("🌟 **新品关联网络**: 展示仪表盘产品中所有新品之间的客户关联关系")
                else:
                    st.info("🚀 **促销品关联网络**: 展示仪表盘产品中所有促销产品之间的客户关联关系")

            # 创建基于真实数据的2D网络图 - 使用缓存版本
            with st.spinner('正在生成产品关联网络图...'):
                network_fig = create_product_network_cached(
                    data['sales_df'],
                    data['dashboard_products'],
                    data['star_products'],
                    data['new_products'],
                    data['promotion_df'],
                    product_filter
                )
            st.plotly_chart(network_fig, use_container_width=True)

            # 关联分析洞察
            with st.expander("💡 产品关联营销策略", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.info("""
                    **🎯 关联分析价值**
                    - 识别经常一起购买的产品组合
                    - 发现交叉销售机会
                    - 优化产品组合策略
                    - 提升客户购买体验
                    """)

                with col2:
                    st.success("""
                    **📈 应用建议**
                    - 将高关联产品打包销售
                    - 在促销时同时推广关联产品
                    - 基于关联度设计货架陈列
                    - 开发新的组合套装产品
                    """)

        elif analysis_type == "📍 区域销售结构":
            # 区域销售结构分析（替代原来的覆盖率分析）
            st.subheader("区域产品销售结构分析")

            # 导入必要的模块
            from plotly.subplots import make_subplots

            fig = create_regional_sales_structure(data)
            st.plotly_chart(fig, use_container_width=True)

            # 分析洞察
            with st.expander("💡 区域销售结构洞察", expanded=True):
                st.info("""
                **📊 分析价值**
                - 了解各区域热销产品TOP10
                - 发现区域产品偏好差异
                - 指导区域个性化营销
                - 优化区域产品配置

                **🎯 应用建议**
                - 根据区域偏好制定差异化策略
                - 在表现好的区域推广更多产品
                - 学习成功区域的产品组合经验
                """)

        elif analysis_type == "🌟 新品渗透率":
            st.subheader("区域新品渗透率分析")

            # 生成新品渗透率分析 - 使用缓存版本
            with st.spinner('正在分析新品渗透率...'):
                fig, penetration_df = create_regional_penetration_analysis_cached(
                    data['sales_df'],
                    data['new_products']
                )
            st.plotly_chart(fig, use_container_width=True)

            # 分析洞察
            with st.expander("💡 新品渗透策略建议", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    avg_penetration = penetration_df['penetration_rate'].mean()
                    st.metric("平均渗透率", f"{avg_penetration:.1f}%",
                              f"{'高于' if avg_penetration > 50 else '低于'}行业平均")

                with col2:
                    top_region = penetration_df.iloc[-1]  # 因为是升序排列，最后一个是最高的
                    st.success(f"""
                                    **🏆 最佳区域**
                                    {top_region['region']}: {top_region['penetration_rate']:.1f}%
                                    客户: {top_region['new_product_customers']}/{top_region['total_customers']}
                                    """)

                with col3:
                    bottom_region = penetration_df.iloc[0]  # 第一个是最低的
                    st.warning(f"""
                                    **⚠️ 待提升区域**
                                    {bottom_region['region']}: {bottom_region['penetration_rate']:.1f}%
                                    潜力: {bottom_region['total_customers'] - bottom_region['new_product_customers']}个客户
                                    """)

            # 详细数据表
            with st.expander("📋 查看各区域新品渗透详情", expanded=False):
                display_df = penetration_df.copy()
                display_df = display_df[['region', 'penetration_rate', 'new_product_customers',
                                         'total_customers', 'sales_ratio', 'new_product_sales']]
                display_df.columns = ['区域', '渗透率(%)', '新品客户数', '总客户数', '销售占比(%)', '新品销售额']
                display_df['渗透率(%)'] = display_df['渗透率(%)'].apply(lambda x: f"{x:.1f}%")
                display_df['销售占比(%)'] = display_df['销售占比(%)'].apply(lambda x: f"{x:.1f}%")
                display_df['新品销售额'] = display_df['新品销售额'].apply(lambda x: f"¥{x:,.0f}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        elif analysis_type == "✅ 有效产品分析":
            st.subheader("有效产品分析（月均销售≥15箱）")

            # 选择维度
            eff_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True,
                                     key="eff_dimension")

            if eff_dimension == "🌏 全国维度":
                product_analysis = analyze_effective_products_cached(
                    data['sales_df'],
                    data['dashboard_products'],
                    'national'
                )
                title = "全国有效产品分析"
            else:
                regions = data['sales_df']['区域'].unique()
                selected_region = st.selectbox("选择区域", regions)
                product_analysis = analyze_effective_products_cached(
                    data['sales_df'],
                    data['dashboard_products'],
                    'regional',
                    selected_region
                )
                title = f"{selected_region}区域有效产品分析"

            if len(product_analysis) > 0:
                fig, effectiveness_rate = create_effective_products_chart(product_analysis, title)
                st.plotly_chart(fig, use_container_width=True)

                # 策略建议
                with st.expander("💡 有效产品策略建议", expanded=True):
                    effective_products = product_analysis[product_analysis['is_effective'] == True]
                    ineffective_products = product_analysis[product_analysis['is_effective'] == False]

                    st.info(f"""
                                    **📋 策略建议**
                                    - 有效产品（{len(effective_products)}个）：继续保持良好销售势头，可作为主推产品
                                    - 接近标准产品：月均销售10-15箱的产品，稍加推广即可达标
                                    - 低效产品：月均销售低于10箱的产品，需要重新评估市场定位
                                    - 区域差异：不同区域的有效产品可能不同，需因地制宜
                                    """)
            else:
                st.warning("暂无产品数据")

        else:  # 环比同比分析
            st.subheader(f"📊 仪表盘产品环比同比分析（{time_info['latest_month'].strftime('%Y-%m')}）")

            # 分析产品增长率 - 使用缓存版本和动态时间
            growth_df = analyze_growth_rates_cached(
                data['sales_df'],
                data['dashboard_products'],
                time_info
            )

            if len(growth_df) > 0:
                # 创建环比同比图表
                fig_mom, fig_yoy = create_growth_rate_charts(growth_df, time_info)

                if fig_mom and fig_yoy:
                    # 显示环比分析
                    st.plotly_chart(fig_mom, use_container_width=True)

                    # 显示同比分析
                    st.plotly_chart(fig_yoy, use_container_width=True)

                    # 增长率分析洞察
                    with st.expander("💡 增长率分析洞察", expanded=True):
                        active_products = growth_df[growth_df['has_current_sales'] == True]

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            mom_positive = (active_products['mom_sales_growth'] > 0).sum()
                            mom_negative = (active_products['mom_sales_growth'] <= 0).sum()
                            avg_mom = active_products['mom_sales_growth'].mean()

                            current_month = time_info['latest_month'].strftime('%Y年%m月')
                            previous_month = time_info['previous_month'].strftime('%Y年%m月')

                            st.info(f"""
                                            **📈 环比分析（{current_month} vs {previous_month}）**
                                            - 正增长产品: {mom_positive}个
                                            - 负增长产品: {mom_negative}个
                                            - 平均增长率: {avg_mom:.1f}%
                                            - 最高增长: {active_products['mom_sales_growth'].max():.1f}%
                                            - 最大下滑: {active_products['mom_sales_growth'].min():.1f}%
                                            """)

                        with col2:
                            non_new_products = active_products[active_products['is_new_product'] == False]
                            yoy_positive = (non_new_products['yoy_sales_growth'] > 0).sum()
                            yoy_negative = (non_new_products['yoy_sales_growth'] <= 0).sum()
                            avg_yoy = non_new_products['yoy_sales_growth'].mean()

                            current_year = time_info['current_year']
                            last_year = current_year - 1

                            st.success(f"""
                                            **📊 同比分析（{current_year} vs {last_year}）**
                                            - 正增长产品: {yoy_positive}个
                                            - 负增长产品: {yoy_negative}个
                                            - 平均增长率: {avg_yoy:.1f}%
                                            - 新品数量: {active_products['is_new_product'].sum()}个
                                            - 最高增长: {non_new_products['yoy_sales_growth'].max():.1f}%
                                            """)

                        with col3:
                            # 双增长产品（环比同比都增长）
                            double_growth = active_products[
                                (active_products['mom_sales_growth'] > 0) &
                                (active_products['yoy_sales_growth'] > 0) &
                                (~active_products['is_new_product'])
                                ]

                            st.warning(f"""
                                            **⭐ 明星增长产品**
                                            - 双增长产品: {len(double_growth)}个
                                            - 占老品比例: {len(double_growth) / (len(active_products) - active_products['is_new_product'].sum()) * 100:.1f}%
                                            - 建议: 重点关注和推广
                                            - 策略: 可作为主打产品
                                            """)

                    # 产品增长明细表
                    with st.expander("📋 产品增长率明细表", expanded=False):
                        # 准备显示数据
                        display_df = growth_df[growth_df['has_current_sales'] == True].copy()
                        display_df = display_df.sort_values('current_sales', ascending=False)

                        # 格式化显示
                        display_df['环比增长'] = display_df['mom_sales_growth'].apply(lambda x: f"{x:+.1f}%")
                        display_df['同比增长'] = display_df.apply(
                            lambda row: "新品" if row['is_new_product'] else f"{row['yoy_sales_growth']:+.1f}%",
                            axis=1
                        )
                        display_df['当期销售额'] = display_df['current_sales'].apply(lambda x: f"¥{x:,.0f}")
                        display_df['产品类型'] = display_df['is_new_product'].apply(lambda x: "🌟新品" if x else "老品")

                        # 选择显示列
                        st.dataframe(
                            display_df[['product_name', '产品类型', '当期销售额', '环比增长', '同比增长']],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.warning("暂无足够的数据进行环比同比分析")
            else:
                st.warning("暂无产品数据")


if __name__ == "__main__":
    main()
