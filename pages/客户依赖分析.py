# pages/客户依赖分析.py - 增强版本
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import json
import time
import random

# 导入高级组件
try:
    from streamlit_lottie import st_lottie
    import requests
    LOTTIE_AVAILABLE = True
except:
    LOTTIE_AVAILABLE = False

try:
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.let_it_rain import rain
    from streamlit_extras.badges import badge
    EXTRAS_AVAILABLE = True
except:
    EXTRAS_AVAILABLE = False

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="客户依赖分析 - Trolli SAL",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录！")
    st.switch_page("app.py")
    st.stop()

# 加载Lottie动画
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# 增强版CSS样式 - 采用产品组合分析的风格
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 主背景渐变 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        position: relative;
        overflow-x: hidden;
    }
    
    /* 动态背景粒子效果 */
    @keyframes float {
        0% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0.8; }
        25% { transform: translateY(-20px) translateX(10px) rotate(90deg); opacity: 1; }
        50% { transform: translateY(10px) translateX(-10px) rotate(180deg); opacity: 0.6; }
        75% { transform: translateY(-10px) translateX(5px) rotate(270deg); opacity: 0.9; }
        100% { transform: translateY(0px) translateX(0px) rotate(360deg); opacity: 0.8; }
    }
    
    /* 浮动元素背景 */
    .stApp::before {
        content: '';
        position: fixed;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        top: 10%;
        left: 5%;
        animation: float 12s ease-in-out infinite;
        z-index: 0;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        bottom: 20%;
        right: 10%;
        animation: float 15s ease-in-out infinite reverse;
        z-index: 0;
    }
    
    /* 主标题样式 - 增强动画 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        color: #2d3748;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        animation: slideDown 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes slideDown {
        from { 
            opacity: 0; 
            transform: translateY(-50px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(0deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(180deg); }
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes glow {
        0%, 100% { filter: brightness(1) drop-shadow(0 0 10px rgba(102, 126, 234, 0.5)); }
        50% { filter: brightness(1.1) drop-shadow(0 0 20px rgba(102, 126, 234, 0.8)); }
    }
    
    /* 指标卡片样式 - 增强版 */
    .metric-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 100%;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInScale 0.6s ease-out backwards;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8) translateY(20px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* 度量值样式 */
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.2); }
    }
    
    .metric-label {
        color: #4a5568;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .metric-delta.positive {
        color: #00aa00;
    }
    
    .metric-delta.negative {
        color: #ff4444;
    }
    
    /* 标签页样式 - 增强版 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.95);
        padding: 0.8rem;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 30px;
        background: white;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
        z-index: -1;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        width: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: transparent;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transform: translateY(-3px);
    }
    
    /* 图表容器动画增强 */
    .plot-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .plot-container:hover {
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15);
        transform: translateY(-5px) scale(1.01);
    }
    
    .plot-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(135deg, #667eea, #764ba2, #667eea);
        border-radius: 20px;
        opacity: 0;
        z-index: -1;
        transition: opacity 0.4s ease;
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .plot-container:hover::before {
        opacity: 0.3;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* 洞察卡片 - 增强动画 */
    .insight-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        backdrop-filter: blur(10px);
        border-left: 5px solid transparent;
        background-clip: padding-box;
        border-image: linear-gradient(135deg, #667eea, #764ba2) 1;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        animation: slideInLeft 0.8s ease-out;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    }
    
    .insight-card h3 {
        color: #667eea;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 增强按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
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
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }
    
    /* 数据点动画 */
    .data-point {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        margin: 0.25rem;
        font-weight: 600;
        animation: bounce 2s ease-in-out infinite;
        animation-delay: calc(var(--i) * 0.1s);
        transition: all 0.3s ease;
    }
    
    .data-point:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* 特殊效果容器 */
    .special-container {
        position: relative;
        padding: 2rem;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    
    .special-container::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: conic-gradient(from 0deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: rotate 10s linear infinite;
    }
    
    /* 加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 3px solid rgba(102, 126, 234, 0.1);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 悬停信息增强 */
    .hover-info {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .hover-info:hover .tooltip {
        opacity: 1;
        visibility: visible;
        transform: translateY(-10px);
    }
    
    .tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-size: 0.9rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* 响应式优化 */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0 15px;
            height: 50px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 数据加载和处理函数
@st.cache_data(ttl=3600)
def load_and_process_data():
    """加载并处理客户数据"""
    try:
        # 使用相对路径加载数据文件
        customer_status = pd.read_excel("客户状态.xlsx")
        customer_status.columns = ['客户名称', '状态']
        
        sales_data = pd.read_excel("客户月度销售达成.xlsx")
        sales_data.columns = ['订单日期', '发运月份', '经销商名称', '金额']
        
        # 处理金额字段
        sales_data['金额'] = pd.to_numeric(
            sales_data['金额'].astype(str).str.replace(',', '').str.replace('，', ''),
            errors='coerce'
        ).fillna(0)
        
        sales_data['订单日期'] = pd.to_datetime(sales_data['订单日期'])
        
        monthly_data = pd.read_excel("客户月度指标.xlsx")
        monthly_data.columns = ['客户', '月度指标', '月份', '往年同期', '所属大区']
        
        # 计算所有指标
        current_year = datetime.now().year
        metrics = calculate_metrics(customer_status, sales_data, monthly_data, current_year)
        
        return metrics, customer_status, sales_data, monthly_data
        
    except Exception as e:
        st.error(f"数据加载错误: {e}")
        return None, None, None, None

def calculate_metrics(customer_status, sales_data, monthly_data, current_year):
    """计算所有业务指标"""
    # 1. 客户健康指标
    total_customers = len(customer_status)
    normal_customers = len(customer_status[customer_status['状态'] == '正常'])
    closed_customers = len(customer_status[customer_status['状态'] == '闭户'])
    normal_rate = (normal_customers / total_customers * 100) if total_customers > 0 else 0
    closed_rate = (closed_customers / total_customers * 100) if total_customers > 0 else 0
    
    # 2. 当年销售数据
    current_year_sales = sales_data[sales_data['订单日期'].dt.year == current_year]
    total_sales = current_year_sales['金额'].sum()
    avg_customer_contribution = total_sales / normal_customers if normal_customers > 0 else 0
    
    # 3. 同比增长率
    last_year_total = monthly_data['往年同期'].sum()
    growth_rate = ((total_sales - last_year_total) / last_year_total * 100) if last_year_total > 0 else 0
    
    # 4. 集中度分析（帕累托分析）
    customer_sales = current_year_sales.groupby('经销商名称')['金额'].sum().sort_values(ascending=False)
    customer_sales_cum = customer_sales.cumsum()
    total_customer_sales = customer_sales.sum()
    
    # 计算贡献度
    top_20_percent_count = int(len(customer_sales) * 0.2)
    top_20_sales = customer_sales.head(top_20_percent_count).sum()
    pareto_ratio = (top_20_sales / total_customer_sales * 100) if total_customer_sales > 0 else 0
    
    # 找到贡献80%销售额的客户数量
    customers_for_80_percent = (customer_sales_cum <= total_customer_sales * 0.8).sum() + 1
    concentration_ratio = (customers_for_80_percent / len(customer_sales) * 100) if len(customer_sales) > 0 else 0
    
    # 5. 客户层级分析
    customer_tiers = []
    for idx, (customer, sales) in enumerate(customer_sales.items()):
        contribution = (sales / total_customer_sales * 100) if total_customer_sales > 0 else 0
        cumulative_contribution = (customer_sales_cum.iloc[idx] / total_customer_sales * 100) if total_customer_sales > 0 else 0
        
        # 确定客户层级
        if idx < 3:
            tier = 'S级战略客户'
            tier_color = '#e74c3c'
        elif contribution >= 2:
            tier = 'A级核心客户'
            tier_color = '#f39c12'
        elif contribution >= 1:
            tier = 'B级重要客户'
            tier_color = '#3498db'
        elif contribution >= 0.5:
            tier = 'C级普通客户'
            tier_color = '#2ecc71'
        else:
            tier = 'D级长尾客户'
            tier_color = '#95a5a6'
        
        customer_tiers.append({
            '客户': customer,
            '销售额': sales,
            '贡献度': contribution,
            '累计贡献': cumulative_contribution,
            '层级': tier,
            '颜色': tier_color,
            '排名': idx + 1
        })
    
    tiers_df = pd.DataFrame(customer_tiers)
    
    # 6. 客户活跃度分析
    customer_activity = []
    current_month = datetime.now().month
    
    for customer in customer_sales.index:
        customer_orders = current_year_sales[current_year_sales['经销商名称'] == customer]
        monthly_orders = customer_orders.groupby(customer_orders['订单日期'].dt.month)['金额'].sum()
        
        # 计算活跃月份数
        active_months = len(monthly_orders)
        avg_monthly_sales = customer_orders['金额'].sum() / current_month
        
        # 计算订单频率趋势
        if len(monthly_orders) >= 3:
            recent_3_months = monthly_orders.tail(3).mean()
            early_months = monthly_orders.head(3).mean()
            trend = ((recent_3_months - early_months) / early_months * 100) if early_months > 0 else 0
        else:
            trend = 0
        
        # 活跃度评分
        activity_score = (active_months / current_month * 40 + 
                         min(avg_monthly_sales / 500000 * 30, 30) +
                         min(trend / 100 * 30, 30))
        
        if activity_score >= 80:
            activity_level = '高度活跃'
            risk_level = '低风险'
        elif activity_score >= 60:
            activity_level = '中度活跃'
            risk_level = '中风险'
        elif activity_score >= 40:
            activity_level = '低度活跃'
            risk_level = '高风险'
        else:
            activity_level = '濒临流失'
            risk_level = '极高风险'
        
        customer_activity.append({
            '客户': customer,
            '活跃月份': active_months,
            '月均销售': avg_monthly_sales,
            '趋势': trend,
            '活跃度评分': activity_score,
            '活跃度': activity_level,
            '风险等级': risk_level
        })
    
    activity_df = pd.DataFrame(customer_activity)
    
    # 7. 区域集中度分析
    region_concentration = []
    for region in monthly_data['所属大区'].unique():
        if pd.notna(region):
            region_customers = monthly_data[monthly_data['所属大区'] == region]['客户'].unique()
            region_sales = current_year_sales[current_year_sales['经销商名称'].isin(region_customers)]
            
            if len(region_sales) > 0:
                region_total = region_sales['金额'].sum()
                region_customer_sales = region_sales.groupby('经销商名称')['金额'].sum().sort_values(ascending=False)
                
                # 计算HHI指数（赫芬达尔指数）
                market_shares = (region_customer_sales / region_total * 100)
                hhi = (market_shares ** 2).sum()
                
                # 计算CR3（前3大客户集中度）
                cr3 = market_shares.head(3).sum()
                
                # 判断集中度类型
                if hhi > 2500:
                    concentration_type = '高度集中'
                    risk_type = '高风险'
                elif hhi > 1500:
                    concentration_type = '中度集中'
                    risk_type = '中风险'
                else:
                    concentration_type = '分散型'
                    risk_type = '低风险'
                
                region_concentration.append({
                    '区域': region,
                    'HHI指数': hhi,
                    'CR3': cr3,
                    '客户数': len(region_customer_sales),
                    '总销售额': region_total,
                    '集中度类型': concentration_type,
                    '风险类型': risk_type,
                    '最大客户': region_customer_sales.index[0] if len(region_customer_sales) > 0 else '',
                    '最大客户占比': market_shares.iloc[0] if len(market_shares) > 0 else 0
                })
    
    concentration_df = pd.DataFrame(region_concentration)
    
    return {
        'total_customers': total_customers,
        'normal_customers': normal_customers,
        'closed_customers': closed_customers,
        'normal_rate': normal_rate,
        'closed_rate': closed_rate,
        'total_sales': total_sales,
        'avg_customer_contribution': avg_customer_contribution,
        'growth_rate': growth_rate,
        'pareto_ratio': pareto_ratio,
        'concentration_ratio': concentration_ratio,
        'customers_for_80_percent': customers_for_80_percent,
        'current_year': current_year,
        'tiers_df': tiers_df,
        'activity_df': activity_df,
        'concentration_df': concentration_df,
        'customer_sales': customer_sales
    }

# 创建高级可视化图表
def create_advanced_visualizations(metrics, sales_data, monthly_data):
    """创建高级交互式可视化"""
    charts = {}
    
    # 1. 客户层级分布太阳图
    tiers_df = metrics['tiers_df']
    
    # 准备太阳图数据
    tier_groups = tiers_df.groupby('层级').agg({
        '销售额': 'sum',
        '客户': 'count'
    }).reset_index()
    tier_groups.columns = ['层级', '销售额', '客户数']
    
    # 创建太阳图
    fig_sunburst = go.Figure()
    
    # 为每个层级创建客户数据
    labels = ['全部客户']
    parents = ['']
    values = [metrics['total_sales']]
    colors = ['#667eea']
    hover_text = [f"总销售额: ¥{metrics['total_sales']:,.0f}<br>客户总数: {len(tiers_df)}"]
    
    tier_colors = {
        'S级战略客户': '#e74c3c',
        'A级核心客户': '#f39c12',
        'B级重要客户': '#3498db',
        'C级普通客户': '#2ecc71',
        'D级长尾客户': '#95a5a6'
    }
    
    for tier in ['S级战略客户', 'A级核心客户', 'B级重要客户', 'C级普通客户', 'D级长尾客户']:
        tier_data = tiers_df[tiers_df['层级'] == tier]
        if len(tier_data) > 0:
            labels.append(tier)
            parents.append('全部客户')
            values.append(tier_data['销售额'].sum())
            colors.append(tier_colors[tier])
            hover_text.append(
                f"{tier}<br>销售额: ¥{tier_data['销售额'].sum():,.0f}<br>"
                f"客户数: {len(tier_data)}<br>"
                f"平均贡献: ¥{tier_data['销售额'].mean():,.0f}"
            )
            
            # 添加具体客户（限制每个层级显示前5个）
            for _, customer in tier_data.head(5).iterrows():
                labels.append(customer['客户'])
                parents.append(tier)
                values.append(customer['销售额'])
                colors.append(tier_colors[tier])
                hover_text.append(
                    f"{customer['客户']}<br>"
                    f"销售额: ¥{customer['销售额']:,.0f}<br>"
                    f"贡献度: {customer['贡献度']:.2f}%<br>"
                    f"排名: 第{customer['排名']}位"
                )
    
    fig_sunburst.add_trace(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        hovertext=hover_text,
        hoverinfo="text",
        textfont=dict(size=14, color="white"),
        insidetextorientation='radial'
    ))
    
    fig_sunburst.update_layout(
        title={
            'text': '客户层级价值分布图',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=600,
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    charts['sunburst'] = fig_sunburst
    
    # 2. 帕累托曲线图（增强版）
    customer_sales = metrics['customer_sales']
    
    # 计算累计百分比
    cum_sales = customer_sales.cumsum()
    cum_sales_pct = (cum_sales / customer_sales.sum() * 100)
    customer_pct = np.arange(1, len(customer_sales) + 1) / len(customer_sales) * 100
    
    fig_pareto = go.Figure()
    
    # 添加柱状图（销售额）
    fig_pareto.add_trace(go.Bar(
        x=list(range(len(customer_sales))),
        y=customer_sales.values,
        name='客户销售额',
        marker_color='rgba(102, 126, 234, 0.6)',
        yaxis='y',
        hovertemplate='<b>%{text}</b><br>销售额: ¥%{y:,.0f}<br>排名: 第%{x}位<extra></extra>',
        text=[f"{name[:10]}..." if len(name) > 10 else name for name in customer_sales.index]
    ))
    
    # 添加累计曲线
    fig_pareto.add_trace(go.Scatter(
        x=list(range(len(customer_sales))),
        y=cum_sales_pct.values,
        name='累计贡献率',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='累计贡献: %{y:.1f}%<extra></extra>'
    ))
    
    # 添加80/20参考线
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", 
                        yref='y2', annotation_text="80%线", 
                        annotation_position="right")
    
    # 找到80%的位置
    idx_80 = np.where(cum_sales_pct >= 80)[0][0]
    fig_pareto.add_vline(x=idx_80, line_dash="dash", line_color="green",
                        annotation_text=f"{idx_80+1}家客户贡献80%",
                        annotation_position="top")
    
    fig_pareto.update_layout(
        title={
            'text': f'客户贡献度帕累托分析 (前{idx_80+1}家客户贡献80%销售额)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis=dict(title='客户排名', showticklabels=False),
        yaxis=dict(title='销售额', side='left'),
        yaxis2=dict(
            title='累计贡献率 (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        height=500,
        hovermode='x unified',
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    charts['pareto'] = fig_pareto
    
    # 3. 客户活跃度矩阵
    activity_df = metrics['activity_df']
    
    # 创建散点图矩阵
    fig_matrix = go.Figure()
    
    # 为不同风险等级设置颜色和大小
    risk_colors = {
        '低风险': '#2ecc71',
        '中风险': '#f39c12',
        '高风险': '#e67e22',
        '极高风险': '#e74c3c'
    }
    
    for risk in ['低风险', '中风险', '高风险', '极高风险']:
        risk_data = activity_df[activity_df['风险等级'] == risk]
        if len(risk_data) > 0:
            fig_matrix.add_trace(go.Scatter(
                x=risk_data['活跃月份'],
                y=risk_data['月均销售'],
                mode='markers+text',
                name=risk,
                marker=dict(
                    size=risk_data['活跃度评分'] / 2,
                    color=risk_colors[risk],
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=[name[:8] + '...' if len(name) > 8 else name for name in risk_data['客户']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='<b>%{text}</b><br>' +
                            '活跃月份: %{x}<br>' +
                            '月均销售: ¥%{y:,.0f}<br>' +
                            '活跃度评分: %{marker.size:.1f}<br>' +
                            '<extra></extra>'
            ))
    
    # 添加象限分割线
    avg_months = activity_df['活跃月份'].mean()
    avg_sales = activity_df['月均销售'].mean()
    
    fig_matrix.add_hline(y=avg_sales, line_dash="dot", line_color="gray", opacity=0.5)
    fig_matrix.add_vline(x=avg_months, line_dash="dot", line_color="gray", opacity=0.5)
    
    # 添加象限标注
    fig_matrix.add_annotation(x=2, y=avg_sales*2, text="高价值<br>低频客户", showarrow=False,
                             font=dict(size=12, color="gray"))
    fig_matrix.add_annotation(x=avg_months*1.5, y=avg_sales*2, text="明星客户", showarrow=False,
                             font=dict(size=12, color="gray"))
    fig_matrix.add_annotation(x=2, y=avg_sales*0.3, text="问题客户", showarrow=False,
                             font=dict(size=12, color="gray"))
    fig_matrix.add_annotation(x=avg_months*1.5, y=avg_sales*0.3, text="潜力客户", showarrow=False,
                             font=dict(size=12, color="gray"))
    
    fig_matrix.update_layout(
        title='客户活跃度风险矩阵（气泡大小=活跃度评分）',
        xaxis_title='活跃月份数',
        yaxis_title='月均销售额',
        height=600,
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    charts['matrix'] = fig_matrix
    
    # 4. 区域集中度雷达图
    concentration_df = metrics['concentration_df']
    
    if not concentration_df.empty:
        # 创建雷达图
        fig_radar = go.Figure()
        
        # 准备数据
        categories = ['HHI指数', 'CR3', '客户数', '风险指数', '平均贡献']
        
        # 归一化处理
        max_hhi = concentration_df['HHI指数'].max()
        max_cr3 = 100
        max_customers = concentration_df['客户数'].max()
        
        for _, region in concentration_df.iterrows():
            # 计算风险指数（基于HHI）
            risk_index = min(region['HHI指数'] / 50, 100)
            
            # 计算平均贡献
            avg_contribution = region['总销售额'] / region['客户数'] / 10000  # 万元
            max_avg_contribution = concentration_df['总销售额'].max() / concentration_df['客户数'].min() / 10000
            
            values = [
                region['HHI指数'] / max_hhi * 100,
                region['CR3'],
                region['客户数'] / max_customers * 100,
                risk_index,
                avg_contribution / max_avg_contribution * 100
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=region['区域'],
                opacity=0.6,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                            '%{theta}: %{r:.1f}<br>' +
                            '<extra></extra>'
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=12)
                )
            ),
            title='区域客户集中度多维分析',
            height=500,
            showlegend=True
        )
        
        charts['radar'] = fig_radar
    
    # 5. 销售趋势河流图
    # 按月份和客户层级汇总数据
    sales_data_copy = sales_data.copy()
    sales_data_copy['年月'] = sales_data_copy['订单日期'].dt.to_period('M')
    
    # 合并客户层级信息
    tier_mapping = dict(zip(tiers_df['客户'], tiers_df['层级']))
    sales_data_copy['层级'] = sales_data_copy['经销商名称'].map(tier_mapping).fillna('其他')
    
    # 按月份和层级汇总
    monthly_tier_sales = sales_data_copy.groupby(['年月', '层级'])['金额'].sum().reset_index()
    monthly_tier_sales['年月'] = monthly_tier_sales['年月'].astype(str)
    
    # 创建河流图
    fig_stream = go.Figure()
    
    tier_order = ['S级战略客户', 'A级核心客户', 'B级重要客户', 'C级普通客户', 'D级长尾客户']
    
    for tier in tier_order:
        tier_data = monthly_tier_sales[monthly_tier_sales['层级'] == tier]
        if len(tier_data) > 0:
            fig_stream.add_trace(go.Scatter(
                x=tier_data['年月'],
                y=tier_data['金额'],
                name=tier,
                mode='lines',
                stackgroup='one',
                fillcolor=tier_colors.get(tier, '#95a5a6'),
                line=dict(width=0.5, color=tier_colors.get(tier, '#95a5a6')),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                            '月份: %{x}<br>' +
                            '销售额: ¥%{y:,.0f}<br>' +
                            '<extra></extra>'
            ))
    
    fig_stream.update_layout(
        title='客户分层销售趋势流图',
        xaxis_title='月份',
        yaxis_title='销售额',
        height=500,
        hovermode='x unified',
        showlegend=True,
        legend=dict(x=1.01, y=0.5)
    )
    
    charts['stream'] = fig_stream
    
    return charts

# 主应用逻辑
def main():
    # 侧边栏
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3 style='color: white;'>🎯 快速导航</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 返回主页", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.switch_page("app.py")
        
        # 添加一些统计信息
        st.markdown("---")
        st.markdown("""
        <div style='color: white; padding: 1rem;'>
            <h4>📊 数据概览</h4>
            <p>• 数据更新: 实时</p>
            <p>• 分析维度: 5个</p>
            <p>• 可视化图表: 8种</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 主标题动画
    st.markdown("""
    <div class="main-header">
        <h1>👥 客户依赖分析</h1>
        <p style="font-size: 1.2rem; opacity: 0.8;">
            智能识别客户价值 · 精准评估业务风险 · 优化客户组合策略
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('🔄 正在加载数据...'):
        time.sleep(0.5)  # 添加轻微延迟以显示加载动画
        metrics, customer_status, sales_data, monthly_data = load_and_process_data()
    
    if metrics is None:
        st.error("❌ 数据加载失败，请检查数据文件是否存在。")
        return
    
    # 创建可视化
    charts = create_advanced_visualizations(metrics, sales_data, monthly_data)
    
    # 如果安装了extras，添加庆祝效果
    if EXTRAS_AVAILABLE and random.random() < 0.1:  # 10%概率显示
        rain(
            emoji="💎",
            font_size=30,
            falling_speed=3,
            animation_length=2
        )
    
    # 关键指标卡片
    st.markdown("<br>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    
    # 指标数据
    metric_data = [
        {
            'label': '客户健康度',
            'value': f"{metrics['normal_rate']:.1f}%",
            'delta': f"{metrics['normal_rate']-85:.1f}%",
            'delta_color': 'positive' if metrics['normal_rate'] > 85 else 'negative',
            'help': f"正常客户{metrics['normal_customers']}家，闭户{metrics['closed_customers']}家",
            'icon': '❤️'
        },
        {
            'label': '帕累托系数',
            'value': f"{metrics['pareto_ratio']:.1f}%",
            'delta': f"前20%客户贡献",
            'delta_color': 'positive' if metrics['pareto_ratio'] > 70 else 'negative',
            'help': f"前{int(len(metrics['customer_sales'])*0.2)}家客户贡献{metrics['pareto_ratio']:.1f}%销售额",
            'icon': '📊'
        },
        {
            'label': '集中度指标',
            'value': f"{metrics['concentration_ratio']:.1f}%",
            'delta': f"{metrics['customers_for_80_percent']}家贡献80%",
            'delta_color': 'negative' if metrics['concentration_ratio'] < 30 else 'positive',
            'help': "客户集中度越低，风险越分散",
            'icon': '🎯'
        },
        {
            'label': '人均贡献',
            'value': f"¥{metrics['avg_customer_contribution']/10000:.1f}万",
            'delta': f"平均每家客户",
            'delta_color': 'positive',
            'help': f"总销售额{metrics['total_sales']/100000000:.2f}亿元",
            'icon': '💰'
        },
        {
            'label': '同比增长',
            'value': f"{'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%",
            'delta': f"较去年同期",
            'delta_color': 'positive' if metrics['growth_rate'] > 0 else 'negative',
            'help': f"增长额{(metrics['total_sales']-monthly_data['往年同期'].sum())/10000:.1f}万",
            'icon': '📈'
        }
    ]
    
    # 显示指标卡片
    for col, data in zip(cols, metric_data):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{data['icon']}</div>
                <div class="metric-value">{data['value']}</div>
                <div class="metric-label">{data['label']}</div>
                <div class="metric-delta {data['delta_color']}">{data['delta']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 价值分层洞察", 
        "📊 集中度分析", 
        "⚡ 活跃度矩阵", 
        "🗺️ 区域风险雷达", 
        "📈 动态趋势"
    ])
    
    with tab1:
        # 价值分层分析
        st.markdown("""
        <div class='insight-card'>
            <h3>💡 核心洞察</h3>
            <p>基于客户贡献度的智能分层，识别不同价值客户群体的特征与机会</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示太阳图
        with st.container():
            st.plotly_chart(charts['sunburst'], use_container_width=True, key="sunburst_chart")
        
        # 客户层级统计
        tiers_df = metrics['tiers_df']
        tier_stats = tiers_df.groupby('层级').agg({
            '销售额': ['sum', 'mean', 'count']
        }).round(0)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # 创建层级分布饼图
            tier_summary = tiers_df.groupby('层级')['销售额'].sum()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=tier_summary.index,
                values=tier_summary.values,
                hole=0.4,
                marker_colors=['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#95a5a6'],
                textfont=dict(size=14, color='white'),
                textposition='inside',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title='客户价值分布',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_pie, use_container_width=True, key="tier_pie_chart")
        
        with col2:
            # 显示关键客户信息
            st.markdown("### 🏆 TOP 5 战略客户")
            top_customers = tiers_df.head(5)
            for idx, customer in top_customers.iterrows():
                st.markdown(f"""
                <div class='data-point' style='--i: {idx};'>
                    #{customer['排名']} {customer['客户'][:12]}...
                    <br>¥{customer['销售额']/10000:.1f}万 ({customer['贡献度']:.1f}%)
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        # 集中度分析
        st.markdown("""
        <div class='insight-card'>
            <h3>📊 帕累托法则验证</h3>
            <p>深度分析客户贡献集中度，评估业务风险分布</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示帕累托图
        st.plotly_chart(charts['pareto'], use_container_width=True, key="pareto_chart")
        
        # 集中度指标展示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 创建集中度仪表
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = metrics['concentration_ratio'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "客户集中度风险"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "#2ecc71"},
                        {'range': [30, 50], 'color': "#f39c12"},
                        {'range': [50, 100], 'color': "#e74c3c"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 30
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True, key="concentration_gauge")
        
        with col2:
            st.markdown(f"""
            <div class='special-container'>
                <h4>📈 20/80法则</h4>
                <p>前20%客户贡献<br><span style='font-size: 2rem; color: #667eea;'>{metrics['pareto_ratio']:.1f}%</span><br>的销售额</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='special-container'>
                <h4>🎯 核心客户群</h4>
                <p>仅需<br><span style='font-size: 2rem; color: #764ba2;'>{metrics['customers_for_80_percent']}</span>家<br>贡献80%销售</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # 活跃度分析
        st.markdown("""
        <div class='insight-card'>
            <h3>⚡ 客户活跃度健康诊断</h3>
            <p>多维度评估客户活跃状态，提前预警流失风险</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示活跃度矩阵
        st.plotly_chart(charts['matrix'], use_container_width=True, key="activity_matrix")
        
        # 风险分布统计
        activity_df = metrics['activity_df']
        risk_summary = activity_df['风险等级'].value_counts()
        
        # 创建风险分布条形图
        fig_risk = go.Figure(data=[
            go.Bar(
                x=risk_summary.index,
                y=risk_summary.values,
                marker_color=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c'],
                text=risk_summary.values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>客户数: %{y}<extra></extra>'
            )
        ])
        
        fig_risk.update_layout(
            title='客户风险等级分布',
            xaxis_title='风险等级',
            yaxis_title='客户数量',
            height=400,
            showlegend=False
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig_risk, use_container_width=True, key="risk_distribution")
        
        with col2:
            # 显示预警客户
            high_risk = activity_df[activity_df['风险等级'].isin(['高风险', '极高风险'])]
            st.markdown("### ⚠️ 重点关注客户")
            
            for idx, customer in high_risk.head(5).iterrows():
                badge_color = "red" if customer['风险等级'] == '极高风险' else "orange"
                st.markdown(f"""
                <div style='margin: 0.5rem 0; padding: 0.5rem; background: rgba(255,255,255,0.1); border-radius: 10px;'>
                    <span style='color: {badge_color}; font-weight: bold;'>●</span> {customer['客户'][:15]}...
                    <br><small>活跃度: {customer['活跃度评分']:.1f} | 趋势: {customer['趋势']:+.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        # 区域风险分析
        st.markdown("""
        <div class='insight-card'>
            <h3>🗺️ 区域集中度风险评估</h3>
            <p>多维度分析各区域客户结构，识别高风险区域</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'radar' in charts:
            st.plotly_chart(charts['radar'], use_container_width=True, key="region_radar")
            
            # 区域风险详情
            concentration_df = metrics['concentration_df']
            
            # 创建HHI指数分布图
            fig_hhi = go.Figure()
            
            # 按风险类型分组
            for risk_type in ['低风险', '中风险', '高风险']:
                risk_data = concentration_df[concentration_df['风险类型'] == risk_type]
                if len(risk_data) > 0:
                    color_map = {'低风险': '#2ecc71', '中风险': '#f39c12', '高风险': '#e74c3c'}
                    fig_hhi.add_trace(go.Bar(
                        x=risk_data['区域'],
                        y=risk_data['HHI指数'],
                        name=risk_type,
                        marker_color=color_map[risk_type],
                        hovertemplate='<b>%{x}</b><br>HHI指数: %{y:.0f}<br>%{fullData.name}<extra></extra>'
                    ))
            
            fig_hhi.update_layout(
                title='区域HHI指数分布（赫芬达尔-赫希曼指数）',
                xaxis_title='区域',
                yaxis_title='HHI指数',
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(fig_hhi, use_container_width=True, key="hhi_distribution")
            
            # 高风险区域预警
            high_risk_regions = concentration_df[concentration_df['风险类型'] == '高风险']
            if len(high_risk_regions) > 0:
                st.warning(f"⚠️ 发现{len(high_risk_regions)}个高风险区域需要重点关注")
                
                for _, region in high_risk_regions.iterrows():
                    with st.expander(f"{region['区域']} - HHI: {region['HHI指数']:.0f}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("最大客户", region['最大客户'][:15] + "...")
                        with col2:
                            st.metric("依赖度", f"{region['最大客户占比']:.1f}%")
                        with col3:
                            st.metric("CR3指数", f"{region['CR3']:.1f}%")
        else:
            st.info("暂无区域数据")
    
    with tab5:
        # 动态趋势分析
        st.markdown("""
        <div class='insight-card'>
            <h3>📈 客户分层动态演进</h3>
            <p>追踪不同价值层级客户的销售贡献变化趋势</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'stream' in charts:
            st.plotly_chart(charts['stream'], use_container_width=True, key="stream_chart")
            
            # 趋势洞察
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class='special-container'>
                    <h4>📊 趋势洞察</h4>
                    <ul style='margin: 0; padding-left: 20px;'>
                        <li>S级客户贡献稳定，是业务基石</li>
                        <li>A级客户增长明显，潜力巨大</li>
                        <li>D级客户占比下降，客户质量提升</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='special-container'>
                    <h4>🎯 行动建议</h4>
                    <ul style='margin: 0; padding-left: 20px;'>
                        <li>维护S级客户的战略伙伴关系</li>
                        <li>加大A级客户的资源投入</li>
                        <li>优化D级客户的服务模式</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 20px;'>
        <p style='color: white; font-size: 1.1rem;'>
            Trolli SAL | 客户依赖分析 | 数据更新时间: {}
        </p>
        <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem;'>
            Powered by Advanced Analytics · Making Data Beautiful
        </p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)

# 运行主应用
if __name__ == "__main__":
    main()
