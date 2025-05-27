# pages/客户依赖分析.py
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
import matplotlib.colors as mcolors

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
    from streamlit_extras.add_vertical_space import add_vertical_space
    from streamlit_card import card
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

# 与销售达成分析完全一致的CSS样式
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 全局字体 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
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
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* 主标题样式 - 增强动画 */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white;
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
        padding: 2.5rem 2rem;
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
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
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
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
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
        color: #374151;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.8rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .metric-sublabel {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.8rem;
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
        color: white;
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
    
    /* 图表容器样式 */
    .chart-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 25px;
        padding: 1.5rem;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            inset 0 1px 0 rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.3);
        animation: chartFadeIn 1.2s ease-out;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .chart-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.02), transparent);
        animation: chartShimmer 8s linear infinite;
    }
    
    @keyframes chartShimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @keyframes chartFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    /* 添加脉动效果 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    .metric-card:hover {
        animation: pulse 1.5s infinite;
    }
    
    /* 洞察卡片 - 动画增强 */
    .insight-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: insightSlide 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(10px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    @keyframes insightSlide {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 2.5rem;
        }
        .metric-card {
            padding: 2rem 1.5rem;
        }
        .main-header {
            padding: 2rem 0;
        }
    }
    
    /* 添加加载动画 */
    @keyframes loading {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading {
        animation: loading 2s linear infinite;
    }
    
    /* 成功动画 */
    @keyframes success {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .success {
        animation: success 0.6s ease-in-out;
    }
    
    /* 新增的客户价值卡片动画 */
    .value-card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .value-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .value-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    .value-card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: iconFloat 3s ease-in-out infinite;
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .value-card-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #2d3748;
    }
    
    .value-card-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.3rem;
    }
    
    .value-card-desc {
        font-size: 0.9rem;
        color: #718096;
    }
    
    /* 图表说明悬停提示 */
    .chart-info {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 24px;
        height: 24px;
        background: #667eea;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: help;
        font-size: 14px;
        font-weight: bold;
        transition: all 0.3s ease;
        z-index: 10;
    }
    
    .chart-info:hover {
        transform: scale(1.2);
        background: #5a67d8;
    }
    
    .chart-info-tooltip {
        position: absolute;
        top: 40px;
        right: 0;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        width: 300px;
        font-size: 0.9rem;
        line-height: 1.5;
        display: none;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .chart-info:hover + .chart-info-tooltip {
        display: block;
        animation: tooltipFadeIn 0.3s ease;
    }
    
    @keyframes tooltipFadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 数据加载和处理函数
@st.cache_data(ttl=3600)
def load_and_process_data():
    """加载并处理客户数据"""
    try:
        # 模拟加载动画
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-animation">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 加载数据
        customer_status = pd.read_excel("客户状态.xlsx")
        customer_status.columns = ['客户名称', '状态']
        
        sales_data = pd.read_excel("客户月度销售达成.xlsx")
        sales_data.columns = ['订单日期', '发运月份', '经销商名称', '金额']
        
        sales_data['金额'] = pd.to_numeric(
            sales_data['金额'].astype(str).str.replace(',', '').str.replace('，', ''),
            errors='coerce'
        ).fillna(0)
        
        sales_data['订单日期'] = pd.to_datetime(sales_data['订单日期'])
        
        monthly_data = pd.read_excel("客户月度指标.xlsx")
        monthly_data.columns = ['客户', '月度指标', '月份', '往年同期', '所属大区']
        
        loading_placeholder.empty()
        
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
    
    # 2. 当年销售数据
    current_year_sales = sales_data[sales_data['订单日期'].dt.year == current_year]
    total_sales = current_year_sales['金额'].sum()
    avg_customer_contribution = total_sales / normal_customers if normal_customers > 0 else 0
    
    # 3. 同比增长率
    last_year_total = monthly_data['往年同期'].sum()
    growth_rate = ((total_sales - last_year_total) / last_year_total * 100) if last_year_total > 0 else 0
    
    # 4. 区域风险分析
    customer_region_map = monthly_data[['客户', '所属大区']].drop_duplicates()
    sales_with_region = current_year_sales.merge(
        customer_region_map, 
        left_on='经销商名称', 
        right_on='客户', 
        how='left'
    )
    
    # 计算每个大区的依赖度
    region_details = []
    max_dependency = 0
    max_dependency_region = ""
    
    if not sales_with_region.empty and '所属大区' in sales_with_region.columns:
        region_groups = sales_with_region.groupby('所属大区')
        
        for region, group in region_groups:
            if pd.notna(region):
                customer_sales = group.groupby('经销商名称')['金额'].sum().sort_values(ascending=False)
                max_customer_sales = customer_sales.max()
                total_region_sales = customer_sales.sum()
                customer_count = customer_sales.count()
                
                if total_region_sales > 0:
                    dependency = (max_customer_sales / total_region_sales * 100)
                    if dependency > max_dependency:
                        max_dependency = dependency
                        max_dependency_region = region
                    
                    top3_customers = customer_sales.head(3)
                    top3_info = [
                        {
                            'name': name,
                            'sales': sales,
                            'percentage': sales / total_region_sales * 100
                        }
                        for name, sales in top3_customers.items()
                    ]
                    
                    region_details.append({
                        '区域': region,
                        '总销售额': total_region_sales,
                        '客户数': customer_count,
                        '平均销售额': total_region_sales / customer_count if customer_count > 0 else 0,
                        '最大客户依赖度': dependency,
                        '最大客户': customer_sales.index[0],
                        '最大客户销售额': max_customer_sales,
                        'TOP3客户': top3_info
                    })
        
        if region_details:
            region_stats = pd.DataFrame(region_details)
        else:
            region_stats = pd.DataFrame()
    else:
        region_stats = pd.DataFrame()
    
    # 5. RFM客户价值分析
    current_date = datetime.now()
    customer_rfm = []
    
    customer_actual_sales = current_year_sales.groupby('经销商名称')['金额'].sum()
    
    for customer in customer_actual_sales.index:
        customer_orders = current_year_sales[current_year_sales['经销商名称'] == customer]
        
        last_order_date = customer_orders['订单日期'].max()
        recency = (current_date - last_order_date).days
        frequency = len(customer_orders)
        monetary = customer_orders['金额'].sum()
        
        # 确定客户类型
        if recency <= 30 and frequency >= 12 and monetary >= 1000000:
            customer_type = '钻石客户'
        elif recency <= 60 and frequency >= 8 and monetary >= 500000:
            customer_type = '黄金客户'
        elif recency <= 90 and frequency >= 6 and monetary >= 200000:
            customer_type = '白银客户'
        elif recency > 180 or frequency < 3:
            customer_type = '流失风险'
        else:
            customer_type = '潜力客户'
        
        customer_rfm.append({
            '客户': customer,
            'R': recency,
            'F': frequency,
            'M': monetary,
            '类型': customer_type,
            '最近购买': last_order_date.strftime('%Y-%m-%d')
        })
    
    rfm_df = pd.DataFrame(customer_rfm) if customer_rfm else pd.DataFrame()
    
    # 统计各类客户数量
    if not rfm_df.empty:
        customer_type_counts = rfm_df['类型'].value_counts()
        diamond_customers = customer_type_counts.get('钻石客户', 0)
        gold_customers = customer_type_counts.get('黄金客户', 0)
        silver_customers = customer_type_counts.get('白银客户', 0)
        risk_customers = customer_type_counts.get('流失风险', 0)
        potential_customers = customer_type_counts.get('潜力客户', 0)
    else:
        diamond_customers = gold_customers = silver_customers = risk_customers = potential_customers = 0
    
    high_value_rate = ((diamond_customers + gold_customers) / normal_customers * 100) if normal_customers > 0 else 0
    
    # 6. 目标达成分析
    current_year_str = str(current_year)
    current_year_targets = monthly_data[monthly_data['月份'].astype(str).str.startswith(current_year_str)]
    
    customer_targets = current_year_targets.groupby('客户')['月度指标'].sum()
    
    achieved_customers = 0
    total_target_customers = 0
    customer_achievement_details = []
    
    for customer in customer_targets.index:
        target = customer_targets[customer]
        actual = customer_actual_sales.get(customer, 0)
        if target > 0:
            total_target_customers += 1
            achievement_rate = (actual / target * 100)
            if actual >= target * 0.8:
                achieved_customers += 1
            
            customer_achievement_details.append({
                '客户': customer,
                '目标': target,
                '实际': actual,
                '达成率': achievement_rate,
                '状态': '达成' if achievement_rate >= 80 else '未达成'
            })
    
    target_achievement_rate = (achieved_customers / total_target_customers * 100) if total_target_customers > 0 else 0
    
    # 7. 额外计算一些指标
    # 客户集中度（前20%客户贡献）
    concentration_rate = 0  # 默认值
    try:
        if len(customer_actual_sales) > 0:
            sorted_sales = customer_actual_sales.sort_values(ascending=False)
            top20_count = max(1, int(len(sorted_sales) * 0.2))
            top20_sales = sorted_sales.head(top20_count).sum()
            concentration_rate = (top20_sales / total_sales * 100) if total_sales > 0 else 0
    except:
        concentration_rate = 0
    
    return {
        'total_customers': total_customers,
        'normal_customers': normal_customers,
        'closed_customers': closed_customers,
        'normal_rate': normal_rate,
        'total_sales': total_sales,
        'avg_customer_contribution': avg_customer_contribution,
        'region_stats': region_stats,
        'max_dependency': max_dependency,
        'max_dependency_region': max_dependency_region,
        'risk_threshold': 30.0,
        'target_achievement_rate': target_achievement_rate,
        'achieved_customers': achieved_customers,
        'total_target_customers': total_target_customers,
        'diamond_customers': diamond_customers,
        'gold_customers': gold_customers,
        'silver_customers': silver_customers,
        'potential_customers': potential_customers,
        'risk_customers': risk_customers,
        'high_value_rate': high_value_rate,
        'growth_rate': growth_rate,
        'current_year': current_year,
        'rfm_df': rfm_df,
        'customer_achievement_details': pd.DataFrame(customer_achievement_details) if customer_achievement_details else pd.DataFrame(),
        'concentration_rate': concentration_rate
    }

# 添加数据验证函数
def validate_metrics_data(metrics):
    """验证指标数据的有效性"""
    try:
        # 确保基本指标都是有效数值
        for key in ['normal_rate', 'target_achievement_rate', 'high_value_rate', 'max_dependency']:
            if key in metrics:
                if pd.isna(metrics[key]) or not isinstance(metrics[key], (int, float)):
                    metrics[key] = 0
                else:
                    metrics[key] = max(0, min(100, metrics[key]))  # 限制在0-100范围内
        
        # 确保客户数量都是非负整数
        for key in ['total_customers', 'normal_customers', 'risk_customers']:
            if key in metrics:
                if pd.isna(metrics[key]) or metrics[key] < 0:
                    metrics[key] = 0
                else:
                    metrics[key] = int(metrics[key])
        
        # 验证DataFrame
        if 'rfm_df' in metrics and not isinstance(metrics['rfm_df'], pd.DataFrame):
            metrics['rfm_df'] = pd.DataFrame()
            
        if 'customer_achievement_details' in metrics and not isinstance(metrics['customer_achievement_details'], pd.DataFrame):
            metrics['customer_achievement_details'] = pd.DataFrame()
        
        return metrics
    except Exception as e:
        print(f"数据验证出错: {e}")
        return metrics

# 创建高级可视化图表
def create_advanced_charts(metrics, sales_data, monthly_data):
    """创建高级交互式图表 - 修复版"""
    charts = {}
    
    # 1. 增强版客户健康状态雷达图
    categories = ['健康度', '目标达成', '价值贡献', '活跃度', '稳定性']
    
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics['normal_customers'] > 0 else 0,
        (100 - metrics['max_dependency'])
    ]
    
    # 对应的详细说明
    descriptions = {
        '健康度': f"正常运营客户占比 {metrics['normal_rate']:.1f}%\n越高说明客户群体越稳定",
        '目标达成': f"销售目标达成率 {metrics['target_achievement_rate']:.1f}%\n反映整体销售执行力",
        '价值贡献': f"高价值客户占比 {metrics['high_value_rate']:.1f}%\n钻石+黄金客户比例",
        '活跃度': f"活跃客户占比 {((metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics['normal_customers'] > 0 else 0):.1f}%\n近期有交易的客户比例",
        '稳定性': f"风险分散度 {(100 - metrics['max_dependency']):.1f}%\n100-最大客户依赖度"
    }
    
    fig_radar = go.Figure()
    
    # 添加当前状态
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='当前状态',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        customdata=[[desc] for desc in descriptions.values()],
        hovertemplate='<b>%{theta}</b><br>%{customdata[0]}<extra></extra>',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.9)",
            font_size=12,
            font_family="Arial"
        )
    ))
    
    # 添加基准线
    fig_radar.add_trace(go.Scatterpolar(
        r=[85, 80, 70, 85, 70],
        theta=categories,
        fill='toself',
        name='目标基准',
        fillcolor='rgba(255, 99, 71, 0.1)',
        line=dict(color='#ff6347', width=2, dash='dash'),
        hovertemplate='%{theta} 目标: %{r:.1f}%<extra></extra>'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                tickfont=dict(size=12)
            ),
            angularaxis=dict(
                tickfont=dict(size=14, weight='bold')
            )
        ),
        showlegend=True,
        height=500,
        margin=dict(t=40, b=40, l=40, r=40),
        font=dict(size=14)
    )
    
    charts['health_radar'] = fig_radar
    
    # 2. 客户价值流动桑基图（安全版本）
    if not metrics['rfm_df'].empty:
        try:
            # 准备桑基图数据
            source = []
            target = []
            value = []
            labels = ['全部客户']
            colors = ['#f0f0f0']
            
            # 客户类型及其对应的颜色
            customer_types = [
                ('钻石客户', '#ff6b6b'),
                ('黄金客户', '#ffd93d'),
                ('白银客户', '#c0c0c0'),
                ('潜力客户', '#4ecdc4'),
                ('流失风险', '#a8a8a8')
            ]
            
            node_idx = 1
            for ct, color in customer_types:
                count = len(metrics['rfm_df'][metrics['rfm_df']['类型'] == ct])
                if count > 0:
                    labels.append(f"{ct}\n{count}家")
                    colors.append(color)
                    source.append(0)
                    target.append(node_idx)
                    value.append(count)
                    node_idx += 1
            
            if len(source) > 0:  # 确保有数据
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=20,
                        thickness=25,
                        line=dict(color="white", width=2),
                        label=labels,
                        color=colors
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=value,
                        color='rgba(180, 180, 180, 0.3)'
                    )
                )])
                
                fig_sankey.update_layout(
                    height=700,
                    margin=dict(t=60, b=60, l=60, r=60),
                    font=dict(size=14)
                )
                
                charts['sankey'] = fig_sankey
        except Exception as e:
            print(f"桑基图创建失败: {e}")
    
    # 3. 客户贡献度旭日图（安全版本）
    if not metrics['rfm_df'].empty:
        try:
            # 准备旭日图数据
            sunburst_data = []
            total_value = metrics['rfm_df']['M'].sum()
            
            if total_value > 0:
                sunburst_data.append({
                    'labels': '全部客户',
                    'parents': '',
                    'values': total_value
                })
                
                # 按客户类型分组
                for customer_type in ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']:
                    type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
                    if not type_customers.empty:
                        type_total = type_customers['M'].sum()
                        sunburst_data.append({
                            'labels': f"{customer_type}\n({len(type_customers)}家)",
                            'parents': '全部客户',
                            'values': type_total
                        })
                
                if len(sunburst_data) > 1:
                    df_sunburst = pd.DataFrame(sunburst_data)
                    
                    fig_sunburst = go.Figure(go.Sunburst(
                        labels=df_sunburst['labels'],
                        parents=df_sunburst['parents'],
                        values=df_sunburst['values'],
                        branchvalues="total"
                    ))
                    
                    fig_sunburst.update_layout(
                        height=700,
                        margin=dict(t=40, b=40, l=40, r=40)
                    )
                    
                    charts['sunburst'] = fig_sunburst
        except Exception as e:
            print(f"旭日图创建失败: {e}")
    
    # 4. 动态月度趋势面积图
    if not sales_data.empty:
        try:
            # 按月汇总销售数据
            sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
            monthly_sales = sales_data.groupby('年月')['金额'].agg(['sum', 'count']).reset_index()
            monthly_sales['年月'] = monthly_sales['年月'].astype(str)
            
            # 创建双轴图
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 销售额面积图
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_sales['年月'],
                    y=monthly_sales['sum'],
                    mode='lines+markers',
                    name='销售额',
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.2)',
                    line=dict(color='#667eea', width=3)
                ),
                secondary_y=False
            )
            
            # 订单数量线
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_sales['年月'],
                    y=monthly_sales['count'],
                    mode='lines+markers',
                    name='订单数',
                    line=dict(color='#ff6b6b', width=2)
                ),
                secondary_y=True
            )
            
            fig_trend.update_xaxes(title_text="月份")
            fig_trend.update_yaxes(title_text="销售额", secondary_y=False)
            fig_trend.update_yaxes(title_text="订单数", secondary_y=True)
            
            fig_trend.update_layout(
                height=500,
                hovermode='x unified',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            
            charts['trend'] = fig_trend
        except Exception as e:
            print(f"趋势图创建失败: {e}")
    
    # 5. 目标达成散点图（修复版本）
    if not metrics['customer_achievement_details'].empty:
        try:
            achievement_df = metrics['customer_achievement_details'].copy()
            
            # 数据清理和验证
            achievement_df = achievement_df.dropna(subset=['目标', '实际', '达成率'])
            achievement_df = achievement_df[achievement_df['目标'] > 0]
            achievement_df = achievement_df[achievement_df['实际'] >= 0]
            
            if not achievement_df.empty:
                fig_scatter = go.Figure()
                
                # 安全的颜色和大小计算
                colors = []
                sizes = []
                for rate in achievement_df['达成率']:
                    rate = max(0, min(500, rate))  # 限制范围
                    
                    if rate >= 100:
                        colors.append('#48bb78')
                        sizes.append(max(20, min(80, rate / 2)))
                    elif rate >= 80:
                        colors.append('#ffd93d')
                        sizes.append(max(15, min(60, rate / 2.5)))
                    else:
                        colors.append('#ff6b6b')
                        sizes.append(max(10, min(40, rate / 3)))
                
                # 添加散点
                fig_scatter.add_trace(go.Scatter(
                    x=achievement_df['目标'],
                    y=achievement_df['实际'],
                    mode='markers',
                    marker=dict(
                        size=sizes,
                        color=colors,
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    text=achievement_df['客户'],
                    name='客户达成情况',
                    hovertemplate='<b>%{text}</b><br>目标: ¥%{x:,.0f}<br>实际: ¥%{y:,.0f}<extra></extra>'
                ))
                
                # 安全计算最大值
                max_target = achievement_df['目标'].max()
                max_actual = achievement_df['实际'].max()
                max_val = max(max_target, max_actual, 1000000) * 1.1
                
                # 添加参考线
                if max_val > 0 and pd.notna(max_val):
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val],
                        y=[0, max_val],
                        mode='lines',
                        name='目标线(100%)',
                        line=dict(color='#e74c3c', width=3, dash='dash')
                    ))
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val],
                        y=[0, max_val * 0.8],
                        mode='lines',
                        name='达成线(80%)',
                        line=dict(color='#f39c12', width=2, dash='dot')
                    ))
                
                # 安全的布局更新
                fig_scatter.update_layout(
                    title="客户目标达成分析",
                    xaxis_title="目标金额",
                    yaxis_title="实际金额",
                    height=800,
                    hovermode='closest',
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                charts['target_scatter'] = fig_scatter
            else:
                # 空数据的处理
                fig_empty = go.Figure()
                fig_empty.add_annotation(
                    text="暂无有效的目标达成数据",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=20, color="gray")
                )
                fig_empty.update_layout(height=400, plot_bgcolor='white')
                charts['target_scatter'] = fig_empty
                
        except Exception as e:
            print(f"目标达成散点图创建失败: {e}")
            # 创建错误提示图
            fig_error = go.Figure()
            fig_error.add_annotation(
                text=f"图表创建出错: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig_error.update_layout(height=400, plot_bgcolor='white')
            charts['target_scatter'] = fig_error
    
    return charts

# 创建带悬停提示的图表容器
def create_chart_with_tooltip(chart, title, subtitle, tooltip_text, key):
    """创建带悬停提示的图表容器"""
    container = st.container()
    with container:
        st.markdown(f"""
        <div class="chart-container">
            <div class="chart-info">?</div>
            <div class="chart-info-tooltip">
                <strong>图表说明</strong><br>
                {tooltip_text}
            </div>
            <div style="margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #1f2937; font-size: 1.2rem; font-weight: 700;">{title}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.9rem;">{subtitle}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(chart, use_container_width=True, key=key)

# 主应用逻辑
def main():
    
    # 标题
    st.markdown("""
    <div class="main-header">
        <h1>👥 客户依赖分析</h1>
        <p>深入洞察客户关系，识别业务风险，优化客户组合策略</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('正在加载数据...'):
        metrics, customer_status, sales_data, monthly_data = load_and_process_data()
    
    if metrics is None:
        st.error("❌ 数据加载失败，请检查数据文件是否存在。")
        return
    
    # 验证数据
    metrics = validate_metrics_data(metrics)
    
    # 创建高级图表
    charts = create_advanced_charts(metrics, sales_data, monthly_data)
    
    # 创建标签页
    tabs = st.tabs([
        "📊 关键指标总览", 
        "🎯 客户健康诊断", 
        "⚠️ 大客户依赖风险评估", 
        "💎 价值分层管理", 
        "📈 目标达成追踪",
        "📉 趋势洞察分析"
    ])
    
    # Tab 1: 关键指标总览 - 优化后的指标卡片
    with tabs[0]:
        # 第一行：核心业务指标
        st.markdown("### 核心业务指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['total_sales']/100000000:.2f}亿</div>
                <div class="metric-label">💰 年度销售总额</div>
                <div class="metric-sublabel">同比 <span style="color: {'#48bb78' if metrics['growth_rate'] > 0 else '#f56565'};">{'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['normal_rate']:.1f}%</div>
                <div class="metric-label">❤️ 客户健康度</div>
                <div class="metric-sublabel">正常客户 {metrics['normal_customers']} 家</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#f56565' if metrics['max_dependency'] > 30 else '#667eea'};">
                    {metrics['max_dependency']:.1f}%
                </div>
                <div class="metric-label">⚠️ 最高区域风险</div>
                <div class="metric-sublabel">{metrics['max_dependency_region']} 区域</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['target_achievement_rate']:.1f}%</div>
                <div class="metric-label">🎯 目标达成率</div>
                <div class="metric-sublabel">{metrics['achieved_customers']}/{metrics['total_target_customers']} 家达成</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 第二行：客户分布指标
        st.markdown("### 客户分布指标")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="height: 160px;">
                <div class="value-card-icon">💎</div>
                <div class="value-card-number">{metrics['diamond_customers']}</div>
                <div class="value-card-label">钻石客户</div>
                <div class="value-card-desc">核心战略客户</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="height: 160px;">
                <div class="value-card-icon">🏆</div>
                <div class="value-card-number">{metrics['gold_customers']}</div>
                <div class="value-card-label">黄金客户</div>
                <div class="value-card-desc">重要价值客户</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="height: 160px;">
                <div class="value-card-icon">🥈</div>
                <div class="value-card-number">{metrics['silver_customers']}</div>
                <div class="value-card-label">白银客户</div>
                <div class="value-card-desc">基础稳定客户</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="height: 160px;">
                <div class="value-card-icon">🌟</div>
                <div class="value-card-number">{metrics['potential_customers']}</div>
                <div class="value-card-label">潜力客户</div>
                <div class="value-card-desc">待开发客户</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card" style="height: 160px;">
                <div class="value-card-icon">⚠️</div>
                <div class="value-card-number" style="color: #f56565;">{metrics['risk_customers']}</div>
                <div class="value-card-label">流失风险</div>
                <div class="value-card-desc">需要挽回</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 第三行：客户状态统计
        st.markdown("### 客户状态统计")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="height: 140px;">
                <div class="metric-label">📊 总客户数</div>
                <div class="metric-value">{metrics['total_customers']}</div>
                <div class="metric-sublabel">全部注册客户</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="height: 140px;">
                <div class="metric-label">✅ 正常客户</div>
                <div class="metric-value" style="color: #48bb78;">{metrics['normal_customers']}</div>
                <div class="metric-sublabel">占比 {metrics['normal_rate']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="height: 140px;">
                <div class="metric-label">❌ 闭户客户</div>
                <div class="metric-value" style="color: #f56565;">{metrics['closed_customers']}</div>
                <div class="metric-sublabel">占比 {(100 - metrics['normal_rate']):.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 核心洞察总结
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='insight-card'>
                <h4>💡 业务健康状况</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>{0}年销售额达¥{1:,.2f}，同比{2}</li>
                    <li>客户群体整体健康，但存在{3}家流失风险客户需要重点关注</li>
                    <li>高价值客户群体贡献了约{4:.1f}%的销售额</li>
                    <li>前20%客户贡献{5:.1f}%销售额，集中度{6}</li>
                </ul>
            </div>
            """.format(
                metrics['current_year'],
                metrics['total_sales'],
                f"增长{metrics['growth_rate']:.1f}%" if metrics['growth_rate'] > 0 else f"下降{abs(metrics['growth_rate']):.1f}%",
                metrics['risk_customers'],
                metrics['high_value_rate'] * 1.5,  # 估算值
                metrics.get('concentration_rate', 0),
                '偏高' if metrics.get('concentration_rate', 0) > 80 else '合理'
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='insight-card'>
                <h4>🎯 管理建议</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>立即启动{0}家流失风险客户的挽回计划</li>
                    <li>重点监控{1}区域的大客户依赖风险</li>
                    <li>培育{2}家潜力客户，提升整体客户价值</li>
                    <li>优化产品组合，提高客户满意度和粘性</li>
                </ul>
            </div>
            """.format(
                metrics['risk_customers'],
                metrics['max_dependency_region'],
                metrics['potential_customers']
            ), unsafe_allow_html=True)
    
    # Tab 2: 客户健康诊断
    with tabs[1]:
        # 增强版雷达图
        if 'health_radar' in charts:
            create_chart_with_tooltip(
                charts['health_radar'],
                "客户健康状态综合评估",
                "多维度评估客户群体的整体健康状况（悬停查看详情）",
                "• <b>使用说明</b>：将鼠标悬停在雷达图的各个维度上查看详细信息<br>" +
                "• <b>维度说明</b>：<br>" +
                "  - 健康度：正常运营客户占比<br>" +
                "  - 目标达成：完成销售目标的客户比例<br>" +
                "  - 价值贡献：高价值客户占比<br>" +
                "  - 活跃度：近期有交易的客户比例<br>" +
                "  - 稳定性：区域依赖度的反向指标<br>" +
                "• <b>解读方法</b>：蓝色区域越大越好，红色虚线为目标基准<br>" +
                "• <b>管理建议</b>：重点关注低于基准线的维度，制定改善计划",
                "health_radar_chart"
            )
        
        # 健康度评分卡
        health_score = (metrics['normal_rate'] * 0.4 + 
                      metrics['target_achievement_rate'] * 0.3 + 
                      metrics['high_value_rate'] * 0.3)
        
        st.markdown("### 综合健康度评分")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style='background: linear-gradient(135deg, #667eea, #764ba2); 
                      color: white; padding: 3rem; border-radius: 20px; 
                      text-align: center; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);'>
                <h1 style='font-size: 4rem; margin: 0; font-weight: 800;'>{health_score:.1f}</h1>
                <p style='font-size: 1.5rem; margin: 1rem 0 0 0; font-weight: 600;'>综合健康度评分</p>
                <hr style='border-color: rgba(255,255,255,0.3); margin: 2rem 0;'>
                <div style='display: flex; justify-content: space-around; text-align: center;'>
                    <div>
                        <p style='margin: 0; font-size: 1.8rem; font-weight: 700;'>{metrics['normal_rate']:.1f}%</p>
                        <p style='margin: 0.3rem 0 0 0; opacity: 0.9;'>正常率</p>
                    </div>
                    <div>
                        <p style='margin: 0; font-size: 1.8rem; font-weight: 700;'>{metrics['target_achievement_rate']:.1f}%</p>
                        <p style='margin: 0.3rem 0 0 0; opacity: 0.9;'>达成率</p>
                    </div>
                    <div>
                        <p style='margin: 0; font-size: 1.8rem; font-weight: 700;'>{metrics['high_value_rate']:.1f}%</p>
                        <p style='margin: 0.3rem 0 0 0; opacity: 0.9;'>价值率</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: 大客户依赖风险评估
    with tabs[2]:
        # 添加客户贡献度分析 (Top 20)
        st.markdown("### 📊 客户贡献度分析 (Top 20)")
        
        # 计算Top 20客户贡献度
        if not metrics['rfm_df'].empty:
            # 获取销售额排名前20的客户
            top20_customers = metrics['rfm_df'].nlargest(20, 'M')
            total_sales = metrics['rfm_df']['M'].sum()
            
            # 计算累计百分比
            top20_customers['销售额占比'] = (top20_customers['M'] / total_sales * 100).round(2)
            top20_customers['累计占比'] = top20_customers['销售额占比'].cumsum()
            
            # 创建双轴图
            fig_top20 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 添加柱状图 - 销售额
            fig_top20.add_trace(
                go.Bar(
                    x=top20_customers['客户'],
                    y=top20_customers['M'],
                    name='销售额',
                    marker=dict(
                        color='#667eea',
                        line=dict(color='white', width=2),
                        opacity=0.9
                    ),
                    text=[f"¥{val/10000:.0f}万" for val in top20_customers['M']],
                    textposition='outside',
                    textfont=dict(size=12, color='#667eea', family='Arial Black'),
                    hovertemplate='<b style="font-size: 16px;">%{x}</b><br><br>' +
                                 '<b>销售额:</b> ¥%{y:,.0f}<br>' +
                                 '<b>占比:</b> %{customdata:.1f}%<extra></extra>',
                    customdata=top20_customers['销售额占比'],
                ),
                secondary_y=False,
            )
            
            # 添加折线图 - 累计占比
            fig_top20.add_trace(
                go.Scatter(
                    x=top20_customers['客户'],
                    y=top20_customers['累计占比'],
                    name='累计占比',
                    mode='lines+markers+text',
                    line=dict(color='#ff8800', width=4, shape='spline'),
                    marker=dict(size=10, color='#ff8800', line=dict(width=2, color='white')),
                    text=[f"{val:.0f}%" if i % 3 == 0 else "" for i, val in enumerate(top20_customers['累计占比'])],
                    textposition='top center',
                    textfont=dict(size=12, color='#ff8800', family='Arial Black'),
                    hovertemplate='<b>%{x}</b><br>累计占比: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=True,
            )
            
            # 添加80%参考线
            fig_top20.add_hline(
                y=80, 
                line_dash="dash", 
                line_color="#e74c3c",
                line_width=3,
                annotation_text="贡献80%销售额线", 
                annotation_position="right",
                annotation_font=dict(size=14, color="#e74c3c"),
                secondary_y=True
            )
            
            # 更新布局
            fig_top20.update_xaxes(
                title_text="客户名称", 
                tickangle=-45,
                tickfont=dict(size=12),
                titlefont=dict(size=16)
            )
            fig_top20.update_yaxes(
                title_text="销售额", 
                secondary_y=False,
                tickfont=dict(size=12),
                titlefont=dict(size=16)
            )
            fig_top20.update_yaxes(
                title_text="累计占比 (%)", 
                range=[0, 105], 
                secondary_y=True,
                tickfont=dict(size=12),
                titlefont=dict(size=16)
            )
            
            fig_top20.update_layout(
                height=600,
                hovermode='x unified',
                margin=dict(t=60, b=120, l=60, r=60),
                showlegend=True,
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.1)',
                    borderwidth=1,
                    font=dict(size=14)
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                bargap=0.15,
                font=dict(family='Arial', size=14)
            )
            
            # 显示图表
            create_chart_with_tooltip(
                fig_top20,
                "客户贡献度分析 (Top 20)",
                "展示前20大客户的销售额分布和累计贡献度",
                "• <b>图表说明</b>：蓝色柱状图表示各客户销售额，橙色折线表示累计占比<br>" +
                "• <b>关注重点</b>：红色虚线表示贡献80%销售额的分界线<br>" +
                "• <b>风险评估</b>：如果少数客户贡献过多销售额，说明客户集中度过高<br>" +
                "• <b>管理建议</b>：平衡客户结构，避免过度依赖少数大客户",
                "top20_chart"
            )
            
            # 显示关键指标
            st.markdown("#### 🎯 关键风险指标")
            col1, col2, col3 = st.columns(3)
            
            # 计算贡献80%销售额的客户数
            customers_for_80 = len(top20_customers[top20_customers['累计占比'] <= 80]) + 1
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{customers_for_80}</div>
                    <div class="metric-label">贡献80%销售的客户数</div>
                    <div class="metric-sublabel">占比 {customers_for_80/len(metrics['rfm_df'])*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(metrics['rfm_df'])}</div>
                    <div class="metric-label">总活跃客户数</div>
                    <div class="metric-sublabel">本年度有交易</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # 客户集中度风险评估
                risk_level = "高" if customers_for_80 <= 5 else "中" if customers_for_80 <= 10 else "低"
                risk_color = "#e74c3c" if risk_level == "高" else "#f39c12" if risk_level == "中" else "#27ae60"
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {risk_color};">{risk_level}风险</div>
                    <div class="metric-label">客户集中度评估</div>
                    <div class="metric-sublabel">Top20占比 {top20_customers['销售额占比'].sum():.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><hr style='border: 1px solid #e0e0e0; margin: 2rem 0;'><br>", unsafe_allow_html=True)
        
        # 区域风险分析
        st.markdown("### 🗺️ 区域客户依赖风险评估")
        
        if not metrics['region_stats'].empty:
            # 创建两列布局
            col_chart, col_details = st.columns([3, 2])
            
            with col_chart:
                # 创建风险评估矩阵
                fig_risk_matrix = go.Figure()
                
                # 添加风险区域背景
                fig_risk_matrix.add_shape(
                    type="rect", x0=0, y0=30, x1=100, y1=100,
                    fillcolor="rgba(231, 76, 60, 0.1)", layer="below",
                    line=dict(width=0)
                )
                fig_risk_matrix.add_shape(
                    type="rect", x0=0, y0=15, x1=100, y1=30,
                    fillcolor="rgba(243, 156, 18, 0.1)", layer="below",
                    line=dict(width=0)
                )
                fig_risk_matrix.add_shape(
                    type="rect", x0=0, y0=0, x1=100, y1=15,
                    fillcolor="rgba(39, 174, 96, 0.1)", layer="below",
                    line=dict(width=0)
                )
                
                # 添加散点
                for _, region in metrics['region_stats'].iterrows():
                    color = '#e74c3c' if region['最大客户依赖度'] > 30 else '#f39c12' if region['最大客户依赖度'] > 15 else '#27ae60'
                    fig_risk_matrix.add_trace(go.Scatter(
                        x=[region['客户数']],
                        y=[region['最大客户依赖度']],
                        mode='markers+text',
                        marker=dict(
                            size=max(20, min(80, region['总销售额']/50000)),
                            color=color,
                            line=dict(color='white', width=3),
                            opacity=0.8
                        ),
                        text=region['区域'],
                        textposition="top center",
                        textfont=dict(size=14, family='Arial Black', color='black'),
                        name=region['区域'],
                        hovertemplate=f"<b style='font-size: 18px;'>{region['区域']}</b><br><br>" +
                                     f"<b>客户数:</b> {region['客户数']}家<br>" +
                                     f"<b>依赖度:</b> <span style='color: {color}; font-weight: bold;'>{region['最大客户依赖度']:.1f}%</span><br>" +
                                     f"<b>总销售:</b> ¥{region['总销售额']/10000:.1f}万<br>" +
                                     f"<b>最大客户:</b> {region['最大客户']}<extra></extra>",
                    ))
                
                # 添加风险线
                fig_risk_matrix.add_hline(
                    y=30, line_dash="dash", line_color="#e74c3c", line_width=3,
                    annotation_text="高风险线(30%)", annotation_position="right",
                    annotation_font=dict(size=14, color="#e74c3c", family='Arial Black')
                )
                fig_risk_matrix.add_hline(
                    y=15, line_dash="dash", line_color="#f39c12", line_width=2,
                    annotation_text="中风险线(15%)", annotation_position="right",
                    annotation_font=dict(size=14, color="#f39c12", family='Arial Black')
                )
                
                fig_risk_matrix.update_layout(
                    title=dict(
                        text="区域客户依赖风险矩阵",
                        font=dict(size=20, family='Arial Black')
                    ),
                    xaxis=dict(
                        title="客户数量",
                        titlefont=dict(size=16),
                        tickfont=dict(size=14),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True
                    ),
                    yaxis=dict(
                        title="最大客户依赖度(%)",
                        titlefont=dict(size=16),
                        tickfont=dict(size=14),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True,
                        range=[0, max(100, metrics['region_stats']['最大客户依赖度'].max() * 1.1)]
                    ),
                    height=600,
                    showlegend=False,
                    hovermode='closest',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=80, b=60, l=60, r=60)
                )
                
                st.plotly_chart(fig_risk_matrix, use_container_width=True)
            
            with col_details:
                # 显示风险详情
                st.markdown("#### 🔍 区域风险详情")
                
                # 按风险等级分组显示
                high_risk = metrics['region_stats'][metrics['region_stats']['最大客户依赖度'] > 30]
                medium_risk = metrics['region_stats'][(metrics['region_stats']['最大客户依赖度'] > 15) & 
                                                     (metrics['region_stats']['最大客户依赖度'] <= 30)]
                low_risk = metrics['region_stats'][metrics['region_stats']['最大客户依赖度'] <= 15]
                
                if not high_risk.empty:
                    st.markdown("##### 🔴 高风险区域")
                    for _, region in high_risk.iterrows():
                        st.markdown(f"""
                        <div class="metric-card" style='background: rgba(231, 76, 60, 0.1); 
                                  border-left: 4px solid #e74c3c; height: auto;'>
                            <div class="metric-label" style="color: #e74c3c;">{region['区域']}</div>
                            <div class="metric-sublabel">依赖度: {region['最大客户依赖度']:.1f}% | 
                            最大客户: {region['最大客户'][:20]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if not medium_risk.empty:
                    st.markdown("##### 🟡 中风险区域")
                    for _, region in medium_risk.iterrows():
                        st.markdown(f"""
                        <div class="metric-card" style='background: rgba(243, 156, 18, 0.1); 
                                  border-left: 4px solid #f39c12; height: auto;'>
                            <div class="metric-label" style="color: #f39c12;">{region['区域']}</div>
                            <div class="metric-sublabel">依赖度: {region['最大客户依赖度']:.1f}% | 
                            最大客户: {region['最大客户'][:20]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if not low_risk.empty:
                    st.markdown("##### 🟢 低风险区域")
                    for _, region in low_risk.iterrows():
                        st.markdown(f"""
                        <div class="metric-card" style='background: rgba(39, 174, 96, 0.1); 
                                  border-left: 4px solid #27ae60; height: auto;'>
                            <div class="metric-label" style="color: #27ae60;">{region['区域']}</div>
                            <div class="metric-sublabel">依赖度: {region['最大客户依赖度']:.1f}% | 
                            客户数: {region['客户数']}家</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Tab 4: 价值分层管理
    with tabs[3]:
        # 客户价值分层
        if 'sankey' in charts:
            create_chart_with_tooltip(
                charts['sankey'],
                "客户价值流动分析",
                "展示客户在不同价值层级间的分布与流动",
                """• <b>图表说明</b>：桑基图展示客户价值分层流动<br>
                • <b>分层标准</b>：<br>
                  - 钻石客户：R≤30天, F≥12次, M≥100万<br>
                  - 黄金客户：R≤60天, F≥8次, M≥50万<br>
                  - 白银客户：R≤90天, F≥6次, M≥20万<br>
                  - 流失风险：R>180天或F<3次<br>
                • <b>二级分层</b>：根据销售额中位数分为高/低贡献<br>
                • <b>管理策略</b>：针对不同层级客户制定差异化策略""",
                "sankey_chart"
            )
        
        # 客户价值旭日图
        if 'sunburst' in charts:
            create_chart_with_tooltip(
                charts['sunburst'],
                "客户贡献度层次分析",
                "深入了解各类客户的销售贡献结构",
                """• <b>使用方法</b>：点击扇形区域可以下钻查看详情<br>
                • <b>颜色含义</b>：<br>
                  - 红色：钻石客户（最高价值）<br>
                  - 橙色：黄金客户（高价值）<br>
                  - 灰色：白银客户（中等价值）<br>
                  - 蓝色：潜力客户（待开发）<br>
                  - 紫色：流失风险（需挽回）<br>
                • <b>数据解读</b>：扇形大小代表销售额贡献""",
                "sunburst_chart"
            )
    
    # Tab 5: 目标达成追踪
    with tabs[4]:
        if 'target_scatter' in charts:
            create_chart_with_tooltip(
                charts['target_scatter'],
                "客户目标达成分析",
                "评估各客户的销售目标完成情况",
                """• <b>图表解读</b>：<br>
                  - 红色虚线：100%目标线<br>
                  - 橙色虚线：80%达成线<br>
                  - 气泡大小：代表达成率<br>
                  - 气泡颜色：绿色(达成)、黄色(接近)、红色(未达成)<br>
                • <b>分析要点</b>：<br>
                  - 线上方：超额完成<br>
                  - 线附近：基本达成<br>
                  - 线下方：未达成<br>
                • <b>管理建议</b>：重点关注红色气泡客户""",
                "target_scatter_chart"
            )
    
    # Tab 6: 趋势洞察分析
    with tabs[5]:
        if 'trend' in charts:
            create_chart_with_tooltip(
                charts['trend'],
                "销售趋势分析",
                "追踪销售额和订单数的月度变化趋势",
                """• <b>双轴图表</b>：<br>
                  - 蓝色面积：月度销售额（左轴）<br>
                  - 红色虚线：月度订单数（右轴）<br>
                • <b>分析维度</b>：<br>
                  - 销售额趋势：业务规模变化<br>
                  - 订单数趋势：交易活跃度<br>
                  - 两者关系：客单价变化<br>
                • <b>洞察价值</b>：识别季节性规律和异常波动""",
                "trend_chart"
            )
        
        # 趋势洞察总结
        st.markdown("""
        <div class='insight-card'>
            <h4>📊 趋势洞察要点</h4>
            <ul style='margin: 0; padding-left: 20px;'>
                <li>销售额呈现明显的季节性波动，需要提前做好库存和产能规划</li>
                <li>订单数量与销售额的增长不同步，说明客单价在发生变化</li>
                <li>建议分析高峰期和低谷期的原因，制定针对性的营销策略</li>
                <li>关注异常波动月份，深入分析背后的业务原因</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 运行主应用
if __name__ == "__main__":
    main()
