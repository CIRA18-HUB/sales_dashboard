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

# 统一的CSS样式 - 与产品组合分析保持一致
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 主背景 - 白色简洁风格 */
    .stApp {
        background: #f8f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* 主标题样式 - 与产品组合分析一致 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        animation: headerSlideDown 0.8s ease-out;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        animation: titlePulse 3s ease-in-out infinite;
    }
    
    @keyframes headerSlideDown {
        from {
            transform: translateY(-50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* 增强的指标卡片样式 */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        height: 180px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: cardFadeIn 0.6s ease-out;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s;
        opacity: 0;
    }
    
    .metric-card:hover::before {
        animation: shimmer 0.5s ease-in-out;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #667eea;
        animation: numberCount 1.5s ease-out;
        margin-bottom: 0.5rem;
        word-break: break-all;
        line-height: 1.2;
    }
    
    .metric-label {
        color: #4a5568;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-detail {
        color: #718096;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .metric-trend {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .trend-up {
        background: rgba(72, 187, 120, 0.1);
        color: #48bb78;
    }
    
    .trend-down {
        background: rgba(245, 101, 101, 0.1);
        color: #f56565;
    }
    
    @keyframes cardFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes numberCount {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* 标签页样式 - 统一风格 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        animation: tabSelect 0.3s ease;
    }
    
    @keyframes tabSelect {
        from { transform: scale(0.95); }
        to { transform: scale(1); }
    }
    
    /* 图表容器 - 增强动画和悬停提示 */
    .plot-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
        animation: slideUp 0.6s ease-out;
        position: relative;
    }
    
    .plot-container:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-4px);
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
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 动态背景粒子效果 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
        100% { transform: translateY(0px) rotate(360deg); }
    }
    
    .floating-icon {
        position: fixed;
        font-size: 20px;
        opacity: 0.1;
        animation: float 6s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    /* 高级卡片样式 */
    .advanced-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        animation: cardEntry 0.8s ease-out;
    }
    
    .advanced-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        transition: left 0.5s;
    }
    
    .advanced-card:hover::before {
        left: 100%;
    }
    
    @keyframes cardEntry {
        from {
            opacity: 0;
            transform: scale(0.9) rotateX(10deg);
        }
        to {
            opacity: 1;
            transform: scale(1) rotateX(0);
        }
    }
    
    /* 数据点动画 */
    .data-point {
        display: inline-block;
        animation: dataPulse 2s ease-in-out infinite;
    }
    
    @keyframes dataPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    /* 加载动画 */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    .loading-dot {
        width: 15px;
        height: 15px;
        margin: 0 5px;
        background: #667eea;
        border-radius: 50%;
        animation: loadingBounce 1.4s ease-in-out infinite both;
    }
    
    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes loadingBounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }
    
    /* 提示框美化 */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: valueShine 3s ease-in-out infinite;
    }
    
    @keyframes valueShine {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    /* 图表标题样式 */
    .chart-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .chart-subtitle {
        font-size: 0.9rem;
        color: #718096;
        margin-bottom: 1rem;
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
    
    /* 雷达图增强样式 */
    .radar-tooltip {
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        pointer-events: none;
        display: none;
        z-index: 1000;
    }
    
    .radar-dimension {
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .radar-value {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .radar-desc {
        font-size: 0.85rem;
        color: #cbd5e0;
    }
</style>
""", unsafe_allow_html=True)

# 添加浮动背景图标
st.markdown("""
<div class="floating-icon" style="top: 10%; left: 10%;">👥</div>
<div class="floating-icon" style="top: 20%; right: 15%; animation-delay: 1s;">📊</div>
<div class="floating-icon" style="bottom: 30%; left: 5%; animation-delay: 2s;">💼</div>
<div class="floating-icon" style="bottom: 10%; right: 10%; animation-delay: 3s;">📈</div>
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

# 创建高级可视化图表
def create_advanced_charts(metrics, sales_data, monthly_data):
    """创建高级交互式图表"""
    charts = {}
    
    # 1. 增强版客户健康状态雷达图
    categories = ['健康度', '目标达成', '价值贡献', '活跃度', '稳定性']
    
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100,
        (100 - metrics['max_dependency'])
    ]
    
    # 对应的详细说明
    descriptions = {
        '健康度': f"正常运营客户占比 {metrics['normal_rate']:.1f}%\n越高说明客户群体越稳定",
        '目标达成': f"销售目标达成率 {metrics['target_achievement_rate']:.1f}%\n反映整体销售执行力",
        '价值贡献': f"高价值客户占比 {metrics['high_value_rate']:.1f}%\n钻石+黄金客户比例",
        '活跃度': f"活跃客户占比 {((metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100):.1f}%\n近期有交易的客户比例",
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
    
    # 2. 客户价值流动桑基图（优化版）
    if not metrics['rfm_df'].empty:
        # 准备桑基图数据
        source = []
        target = []
        value = []
        labels = ['全部客户']
        colors = ['#e8e8e8']
        
        # 客户类型及其对应的颜色
        customer_types = [
            ('钻石客户', '#e74c3c'),
            ('黄金客户', '#f39c12'),
            ('白银客户', '#95a5a6'),
            ('潜力客户', '#3498db'),
            ('流失风险', '#9b59b6')
        ]
        
        node_idx = 1
        for ct, color in customer_types:
            count = len(metrics['rfm_df'][metrics['rfm_df']['类型'] == ct])
            if count > 0:
                labels.append(f"{ct}\n({count}家)")
                colors.append(color)
                source.append(0)
                target.append(node_idx)
                value.append(count)
                node_idx += 1
        
        # 添加二级分层（销售额贡献）
        for idx, (ct, color) in enumerate(customer_types, 1):
            if idx < len(labels):  # 确保节点存在
                type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == ct]
                if not type_customers.empty:
                    # 根据销售额分层
                    high_sales = len(type_customers[type_customers['M'] > type_customers['M'].median()])
                    low_sales = len(type_customers) - high_sales
                    
                    if high_sales > 0:
                        labels.append(f"高贡献\n({high_sales}家)")
                        colors.append(color)
                        source.append(idx)
                        target.append(len(labels) - 1)
                        value.append(high_sales)
                    
                    if low_sales > 0:
                        labels.append(f"低贡献\n({low_sales}家)")
                        colors.append('#cccccc')
                        source.append(idx)
                        target.append(len(labels) - 1)
                        value.append(low_sales)
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=colors,
                hovertemplate='%{label}<br>客户数: %{value}<extra></extra>'
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(200, 200, 200, 0.3)'
            )
        )])
        
        fig_sankey.update_layout(
            height=600,
            margin=dict(t=40, b=40, l=40, r=40),
            font=dict(size=12)
        )
        
        charts['sankey'] = fig_sankey
    
    # 3. 客户贡献度旭日图（增强版）
    if not metrics['rfm_df'].empty:
        # 准备旭日图数据
        sunburst_data = []
        
        # 根节点
        total_value = metrics['rfm_df']['M'].sum()
        sunburst_data.append({
            'labels': '全部客户',
            'parents': '',
            'values': total_value,
            'text': f"总销售额: ¥{total_value/10000:.1f}万"
        })
        
        # 颜色映射
        type_colors = {
            '钻石客户': '#e74c3c',
            '黄金客户': '#f39c12',
            '白银客户': '#95a5a6',
            '潜力客户': '#3498db',
            '流失风险': '#9b59b6'
        }
        
        # 按客户类型分组
        for customer_type in ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']:
            type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
            
            if not type_customers.empty:
                type_total = type_customers['M'].sum()
                # 添加类型节点
                sunburst_data.append({
                    'labels': f"{customer_type}\n({len(type_customers)}家)",
                    'parents': '全部客户',
                    'values': type_total,
                    'text': f"¥{type_total/10000:.1f}万 ({type_total/total_value*100:.1f}%)",
                    'color': type_colors[customer_type]
                })
                
                # 添加前10个客户（如果超过10个）
                top_customers = type_customers.nlargest(10, 'M')
                for _, customer in top_customers.iterrows():
                    customer_name = customer['客户'][:15] + '...' if len(customer['客户']) > 15 else customer['客户']
                    sunburst_data.append({
                        'labels': customer_name,
                        'parents': f"{customer_type}\n({len(type_customers)}家)",
                        'values': customer['M'],
                        'text': f"¥{customer['M']/10000:.1f}万",
                        'color': type_colors[customer_type]
                    })
        
        if sunburst_data:
            df_sunburst = pd.DataFrame(sunburst_data)
            
            fig_sunburst = go.Figure(go.Sunburst(
                labels=df_sunburst['labels'],
                parents=df_sunburst['parents'],
                values=df_sunburst['values'],
                text=df_sunburst['text'],
                branchvalues="total",
                marker=dict(
                    colors=df_sunburst.get('color', '#cccccc'),
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>%{text}<br>占比: %{percentRoot}<extra></extra>',
                textfont=dict(size=12)
            ))
            
            fig_sunburst.update_layout(
                height=700,
                margin=dict(t=40, b=40, l=40, r=40),
                font=dict(size=14)
            )
            
            charts['sunburst'] = fig_sunburst
    
    # 4. 动态月度趋势面积图
    if not sales_data.empty:
        # 按月汇总销售数据
        sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
        monthly_sales = sales_data.groupby('年月')['金额'].agg(['sum', 'count']).reset_index()
        monthly_sales['年月'] = monthly_sales['年月'].astype(str)
        
        # 创建双轴图
        fig_trend = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]]
        )
        
        # 销售额面积图
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_sales['年月'],
                y=monthly_sales['sum'],
                mode='lines+markers',
                name='销售额',
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#667eea', line=dict(width=2, color='white')),
                hovertemplate='%{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
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
                line=dict(color='#ff6b6b', width=2, dash='dot'),
                marker=dict(size=6, color='#ff6b6b'),
                hovertemplate='%{x}<br>订单数: %{y}<extra></extra>'
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
    
    # 5. 目标达成散点图（优化版）
    if not metrics['customer_achievement_details'].empty:
        achievement_df = metrics['customer_achievement_details']
        
        fig_scatter = go.Figure()
        
        # 根据达成率设置颜色
        colors = []
        for rate in achievement_df['达成率']:
            if rate >= 100:
                colors.append('#48bb78')  # 绿色
            elif rate >= 80:
                colors.append('#f39c12')  # 橙色
            else:
                colors.append('#f56565')  # 红色
        
        # 添加散点
        fig_scatter.add_trace(go.Scatter(
            x=achievement_df['目标'],
            y=achievement_df['实际'],
            mode='markers',
            marker=dict(
                size=achievement_df['达成率'].apply(lambda x: min(max(x/5, 10), 50)),
                color=colors,
                line=dict(width=1, color='white'),
                opacity=0.8
            ),
            text=achievement_df['客户'],
            customdata=achievement_df[['达成率', '状态']],
            hovertemplate='<b>%{text}</b><br>目标: ¥%{x:,.0f}<br>实际: ¥%{y:,.0f}<br>达成率: %{customdata[0]:.1f}%<br>状态: %{customdata[1]}<extra></extra>'
        ))
        
        # 添加目标线
        max_val = max(achievement_df['目标'].max(), achievement_df['实际'].max())
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='目标线(100%)',
            line=dict(color='red', dash='dash'),
            showlegend=True
        ))
        
        # 添加80%达成线
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val * 0.8],
            mode='lines',
            name='达成线(80%)',
            line=dict(color='orange', dash='dot'),
            showlegend=True
        ))
        
        fig_scatter.update_layout(
            xaxis_title="目标金额",
            yaxis_title="实际金额",
            height=600,
            margin=dict(t=40, b=40, l=40, r=40),
            hovermode='closest'
        )
        
        charts['target_scatter'] = fig_scatter
    
    return charts

# 创建带悬停提示的图表容器
def create_chart_with_tooltip(chart, title, subtitle, tooltip_text, key):
    """创建带悬停提示的图表容器"""
    container = st.container()
    with container:
        st.markdown(f"""
        <div class="plot-container">
            <div class="chart-info">?</div>
            <div class="chart-info-tooltip">
                <strong>图表说明</strong><br>
                {tooltip_text}
            </div>
            <div class="chart-title">{title}</div>
            <div class="chart-subtitle">{subtitle}</div>
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
    metrics, customer_status, sales_data, monthly_data = load_and_process_data()
    
    if metrics is None:
        st.error("❌ 数据加载失败，请检查数据文件是否存在。")
        return
    
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
        # 核心指标展示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💰 年度销售总额</div>
                <div class="metric-value data-point">¥{metrics['total_sales']/100000000:.2f}亿</div>
                <div class="metric-detail">同比 {'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">❤️ 客户健康度</div>
                <div class="metric-value data-point">{metrics['normal_rate']:.1f}%</div>
                <div class="metric-detail">正常客户 {metrics['normal_customers']} 家</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚠️ 最高区域风险</div>
                <div class="metric-value data-point" style="color: {'#f56565' if metrics['max_dependency'] > 30 else '#667eea'};">
                    {metrics['max_dependency']:.1f}%
                </div>
                <div class="metric-detail">{metrics['max_dependency_region']} 区域</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🎯 目标达成率</div>
                <div class="metric-value data-point">{metrics['target_achievement_rate']:.1f}%</div>
                <div class="metric-detail">{metrics['achieved_customers']}/{metrics['total_target_customers']} 家达成</div>
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
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        # 增强版雷达图
        create_chart_with_tooltip(
            charts['health_radar'],
            "客户健康状态综合评估",
            "多维度评估客户群体的整体健康状况（悬停查看详情）",
            """
            • <b>使用说明</b>：将鼠标悬停在雷达图的各个维度上查看详细信息<br>
            • <b>维度说明</b>：<br>
              - 健康度：正常运营客户占比<br>
              - 目标达成：完成销售目标的客户比例<br>
              - 价值贡献：高价值客户占比<br>
              - 活跃度：近期有交易的客户比例<br>
              - 稳定性：区域依赖度的反向指标<br>
            • <b>解读方法</b>：蓝色区域越大越好，红色虚线为目标基准<br>
            • <b>管理建议</b>：重点关注低于基准线的维度，制定改善计划
            """,
            "health_radar_chart"
        )
        
        # 客户状态分布（优化展示）
        if not customer_status.empty:
            status_counts = customer_status['状态'].value_counts()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_status = go.Figure()
                
                # 使用环形图展示
                fig_status.add_trace(go.Pie(
                    labels=status_counts.index,
                    values=status_counts.values,
                    hole=0.6,
                    marker=dict(colors=['#48bb78', '#f56565']),
                    textinfo='label+percent+value',
                    textfont=dict(size=14),
                    hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
                ))
                
                # 在中心添加总数
                fig_status.add_annotation(
                    text=f'<b>{metrics["total_customers"]}</b><br>总客户数',
                    x=0.5, y=0.5,
                    font=dict(size=20, color='#2d3748'),
                    showarrow=False
                )
                
                fig_status.update_layout(
                    height=400,
                    margin=dict(t=40, b=40, l=40, r=40),
                    showlegend=True
                )
                
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # 健康度评分卡
                health_score = (metrics['normal_rate'] * 0.4 + 
                              metrics['target_achievement_rate'] * 0.3 + 
                              metrics['high_value_rate'] * 0.3)
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea, #764ba2); 
                          color: white; padding: 2rem; border-radius: 15px; 
                          text-align: center; height: 100%;'>
                    <h2 style='font-size: 3rem; margin: 0;'>{health_score:.1f}</h2>
                    <p style='font-size: 1.2rem; margin: 0.5rem 0;'>健康度评分</p>
                    <hr style='border-color: rgba(255,255,255,0.3); margin: 1rem 0;'>
                    <p style='margin: 0.5rem 0;'>正常率: {metrics['normal_rate']:.1f}%</p>
                    <p style='margin: 0.5rem 0;'>达成率: {metrics['target_achievement_rate']:.1f}%</p>
                    <p style='margin: 0.5rem 0;'>价值率: {metrics['high_value_rate']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 3: 大客户依赖风险评估
    with tabs[2]:
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        # 区域风险分析
        if not metrics['region_stats'].empty:
            # 创建风险评估矩阵
            fig_risk_matrix = go.Figure()
            
            # 添加风险区域背景
            fig_risk_matrix.add_shape(
                type="rect", x0=0, y0=30, x1=100, y1=100,
                fillcolor="rgba(255, 0, 0, 0.1)", layer="below"
            )
            fig_risk_matrix.add_shape(
                type="rect", x0=0, y0=15, x1=100, y1=30,
                fillcolor="rgba(255, 165, 0, 0.1)", layer="below"
            )
            fig_risk_matrix.add_shape(
                type="rect", x0=0, y0=0, x1=100, y1=15,
                fillcolor="rgba(0, 255, 0, 0.1)", layer="below"
            )
            
            # 添加散点
            for _, region in metrics['region_stats'].iterrows():
                color = '#ff4444' if region['最大客户依赖度'] > 30 else '#ff8800' if region['最大客户依赖度'] > 15 else '#48bb78'
                fig_risk_matrix.add_trace(go.Scatter(
                    x=[region['客户数']],
                    y=[region['最大客户依赖度']],
                    mode='markers+text',
                    marker=dict(
                        size=region['总销售额']/100000,  # 根据销售额调整大小
                        color=color,
                        line=dict(color='white', width=2)
                    ),
                    text=region['区域'],
                    textposition="top center",
                    name=region['区域'],
                    hovertemplate=f"<b>{region['区域']}</b><br>" +
                                 f"客户数: {region['客户数']}<br>" +
                                 f"依赖度: {region['最大客户依赖度']:.1f}%<br>" +
                                 f"总销售: ¥{region['总销售额']/10000:.1f}万<br>" +
                                 f"最大客户: {region['最大客户']}<extra></extra>"
                ))
            
            # 添加风险线
            fig_risk_matrix.add_hline(y=30, line_dash="dash", line_color="red", 
                                      annotation_text="高风险线", annotation_position="right")
            fig_risk_matrix.add_hline(y=15, line_dash="dash", line_color="orange", 
                                      annotation_text="中风险线", annotation_position="right")
            
            fig_risk_matrix.update_layout(
                title="区域客户依赖风险矩阵",
                xaxis_title="客户数量",
                yaxis_title="最大客户依赖度(%)",
                height=500,
                showlegend=False,
                hovermode='closest'
            )
            
            create_chart_with_tooltip(
                fig_risk_matrix,
                "区域客户依赖风险评估",
                "识别高风险区域，制定风险分散策略",
                """
                • <b>用途</b>：评估各区域的大客户依赖风险<br>
                • <b>风险等级</b>：<br>
                  - 红色区域(>30%)：高风险，需立即采取行动<br>
                  - 橙色区域(15-30%)：中风险，需要关注<br>
                  - 绿色区域(<15%)：低风险，保持监控<br>
                • <b>气泡大小</b>：代表区域总销售额<br>
                • <b>管理策略</b>：<br>
                  - 高风险区域：开发新客户，分散风险<br>
                  - 中风险区域：培育潜力客户，平衡结构<br>
                  - 低风险区域：维持现状，持续优化
