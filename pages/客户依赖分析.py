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

warnings.filterwarnings('ignore')

# 尝试导入 streamlit-echarts
try:
    from streamlit_echarts import st_echarts
    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False
    print("streamlit-echarts 未安装，将使用备选方案")

# 创建一个简单的 streamlit-echarts 包装器（用于没有安装时的兼容性）
if not ECHARTS_AVAILABLE:
    def st_echarts(options, height="400px", key=None):
        st.error("streamlit-echarts 组件未安装。请运行以下命令安装：")
        st.code("pip install streamlit-echarts", language="bash")
        st.info("安装后请重新启动应用。现在将显示备选图表。")
        return None

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

# 检查依赖组件
if not ECHARTS_AVAILABLE:
    with st.sidebar:
        st.warning("🔧 **提示**：安装 streamlit-echarts 可以获得更好的桑基图效果")
        st.code("pip install streamlit-echarts", language="bash")
        st.caption("安装后重启应用即可使用高级桑基图")

# 统一高级CSS样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* 浮动粒子背景 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none; z-index: -1;
    }
    
    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }
    
    /* 主容器 */
    .main .block-container {
        background: rgba(255,255,255,0.95);
        border-radius: 20px; padding: 2rem; margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* 主标题 */
    .main-header {
        text-align: center; padding: 2.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white; border-radius: 20px; margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.2s ease-out;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        position: relative; overflow: hidden;
    }
    
    .main-header::before {
        content: ''; position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
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
        from { opacity: 0; transform: translateY(-30px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    /* 统一指标卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem; border-radius: 18px; text-align: center; height: 100%;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 3px 10px rgba(0,0,0,0.03);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUp 0.8s ease-out;
        position: relative; overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .metric-card::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 10px 20px rgba(102, 126, 234, 0.15);
    }
    
    .metric-card:hover::before { left: 100%; }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    /* 指标数值样式 */
    .metric-value {
        font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1.1;
    }
    
    .big-value {
        font-size: 2.8rem; font-weight: 900; margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1;
    }
    
    @keyframes valueGlow {
        from { filter: brightness(1); }
        to { filter: brightness(1.1); }
    }
    
    .metric-label {
        color: #374151; font-size: 0.95rem; font-weight: 600;
        margin-top: 0.5rem; letter-spacing: 0.3px;
    }
    
    .metric-sublabel {
        color: #6b7280; font-size: 0.8rem; margin-top: 0.4rem;
        font-weight: 500; font-style: italic;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 0.6rem; border-radius: 12px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px; padding: 0 20px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px; border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 600; font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px); 
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* 直接对Plotly图表应用圆角样式 */
    .stPlotlyChart {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.06), 0 3px 10px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.05);
        margin: 1.5rem 0;
    }
    
    /* 确保图表内部背景为白色 */
    .js-plotly-plot {
        background: white !important;
        border-radius: 16px !important;
    }
    
    .plot-container {
        background: white !important;
        border-radius: 16px !important;
    }
    
    /* 洞察卡片 */
    .insight-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-left: 4px solid #667eea; border-radius: 12px;
        padding: 1.2rem; margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        animation: slideInLeft 0.6s ease-out;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(5px) translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.12);
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .insight-card h4 {
        color: #1f2937; margin-bottom: 0.8rem;
        font-weight: 700; font-size: 1rem;
    }
    
    .insight-card ul {
        color: #374151; line-height: 1.5; margin: 0; padding-left: 1rem;
    }
    
    .insight-card li {
        margin-bottom: 0.3rem; color: #4a5568; font-size: 0.9rem;
    }
    
    /* 动画延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }
    
    /* 响应式 */
    @media (max-width: 768px) {
        .metric-value, .big-value { font-size: 1.8rem; }
        .metric-card { padding: 1rem; margin: 0.5rem 0; }
        .main-header { padding: 1.5rem 0; }
    }
    
    /* 确保文字颜色 */
    h1, h2, h3, h4, h5, h6 { color: #1f2937 !important; }
    p, span, div { color: #374151; }
    
    /* 优化Plotly图表中文字体 */
    .plotly .gtitle {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Arial", sans-serif !important;
    }
    
    .plotly .g-gtitle {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Arial", sans-serif !important;
    }
    
    /* 图表标题容器 */
    .chart-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 200% 200%;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
        position: relative;
        overflow: hidden;
        animation: gradientFlow 6s ease infinite;
        transition: all 0.3s ease;
    }
    
    .chart-header:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
    }
    
    /* 渐变流动动画 */
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 光泽效果 */
    .chart-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent
        );
        animation: shine 3s ease-in-out infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        50%, 100% { left: 200%; }
    }
    
    /* 图表标题样式 */
    .chart-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-align: left;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
        line-height: 1.2;
        animation: fadeInSlide 0.8s ease-out;
    }
    
    .chart-subtitle {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        font-weight: 400;
        text-align: left;
        line-height: 1.4;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
        animation: fadeInSlide 1s ease-out;
    }
    
    @keyframes fadeInSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# 数据加载函数
@st.cache_data(ttl=3600)
def load_and_process_data():
    """加载并处理客户数据"""
    try:
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
        
        current_year = datetime.now().year
        metrics = calculate_metrics(customer_status, sales_data, monthly_data, current_year)
        
        return metrics, customer_status, sales_data, monthly_data
        
    except Exception as e:
        st.error(f"数据加载错误: {e}")
        return None, None, None, None

def calculate_metrics(customer_status, sales_data, monthly_data, current_year):
    """计算业务指标"""
    # 基础客户指标
    total_customers = len(customer_status)
    normal_customers = len(customer_status[customer_status['状态'] == '正常'])
    closed_customers = len(customer_status[customer_status['状态'] == '闭户'])
    normal_rate = (normal_customers / total_customers * 100) if total_customers > 0 else 0
    
    # 销售数据
    current_year_sales = sales_data[sales_data['订单日期'].dt.year == current_year]
    total_sales = current_year_sales['金额'].sum()
    
    # 同比增长
    last_year_total = monthly_data['往年同期'].sum()
    growth_rate = ((total_sales - last_year_total) / last_year_total * 100) if last_year_total > 0 else 0
    
    # 区域风险分析
    customer_region_map = monthly_data[['客户', '所属大区']].drop_duplicates()
    sales_with_region = current_year_sales.merge(
        customer_region_map, left_on='经销商名称', right_on='客户', how='left'
    )
    
    region_details = []
    max_dependency = 0
    max_dependency_region = ""
    
    if not sales_with_region.empty and '所属大区' in sales_with_region.columns:
        for region, group in sales_with_region.groupby('所属大区'):
            if pd.notna(region):
                customer_sales = group.groupby('经销商名称')['金额'].sum().sort_values(ascending=False)
                if len(customer_sales) > 0:
                    max_customer_sales = customer_sales.max()
                    total_region_sales = customer_sales.sum()
                    dependency = (max_customer_sales / total_region_sales * 100) if total_region_sales > 0 else 0
                    
                    if dependency > max_dependency:
                        max_dependency = dependency
                        max_dependency_region = region
                    
                    region_details.append({
                        '区域': region,
                        '总销售额': total_region_sales,
                        '客户数': len(customer_sales),
                        '最大客户依赖度': dependency,
                        '最大客户': customer_sales.index[0] if len(customer_sales) > 0 else '',
                        '最大客户销售额': max_customer_sales
                    })
    
    region_stats = pd.DataFrame(region_details) if region_details else pd.DataFrame()
    
    # RFM客户分析
    current_date = datetime.now()
    customer_rfm = []
    customer_actual_sales = current_year_sales.groupby('经销商名称')['金额'].sum()
    
    for customer in customer_actual_sales.index:
        customer_orders = current_year_sales[current_year_sales['经销商名称'] == customer]
        last_order_date = customer_orders['订单日期'].max()
        recency = (current_date - last_order_date).days
        frequency = len(customer_orders)
        monetary = customer_orders['金额'].sum()
        
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
            '客户': customer, 'R': recency, 'F': frequency, 'M': monetary,
            '类型': customer_type, '最近购买': last_order_date.strftime('%Y-%m-%d')
        })
    
    rfm_df = pd.DataFrame(customer_rfm) if customer_rfm else pd.DataFrame()
    
    # 客户类型统计
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
    
    # 目标达成分析
    current_year_str = str(current_year)
    current_year_targets = monthly_data[monthly_data['月份'].astype(str).str.startswith(current_year_str)]
    customer_targets = current_year_targets.groupby('客户')['月度指标'].sum()
    
    achieved_customers = 0
    total_target_customers = len(customer_targets)
    customer_achievement_details = []
    
    for customer in customer_targets.index:
        target = customer_targets[customer]
        actual = customer_actual_sales.get(customer, 0)
        if target > 0:
            achievement_rate = (actual / target * 100)
            if actual >= target * 0.8:
                achieved_customers += 1
            
            customer_achievement_details.append({
                '客户': customer, '目标': target, '实际': actual,
                '达成率': achievement_rate, '状态': '达成' if achievement_rate >= 80 else '未达成'
            })
    
    target_achievement_rate = (achieved_customers / total_target_customers * 100) if total_target_customers > 0 else 0
    
    # 客户集中度
    concentration_rate = 0
    if len(customer_actual_sales) > 0:
        sorted_sales = customer_actual_sales.sort_values(ascending=False)
        top20_count = max(1, int(len(sorted_sales) * 0.2))
        top20_sales = sorted_sales.head(top20_count).sum()
        concentration_rate = (top20_sales / total_sales * 100) if total_sales > 0 else 0
    
    return {
        'total_customers': total_customers, 'normal_customers': normal_customers, 'closed_customers': closed_customers,
        'normal_rate': normal_rate, 'total_sales': total_sales, 'growth_rate': growth_rate,
        'region_stats': region_stats, 'max_dependency': max_dependency, 'max_dependency_region': max_dependency_region,
        'target_achievement_rate': target_achievement_rate, 'achieved_customers': achieved_customers, 'total_target_customers': total_target_customers,
        'diamond_customers': diamond_customers, 'gold_customers': gold_customers, 'silver_customers': silver_customers,
        'potential_customers': potential_customers, 'risk_customers': risk_customers, 'high_value_rate': high_value_rate,
        'current_year': current_year, 'rfm_df': rfm_df, 'concentration_rate': concentration_rate,
        'customer_achievement_details': pd.DataFrame(customer_achievement_details) if customer_achievement_details else pd.DataFrame()
    }

def format_amount(amount):
    """格式化金额"""
    if amount >= 100000000:
        return f"¥{amount/100000000:.1f}亿"
    elif amount >= 10000:
        return f"¥{amount/10000:.0f}万"
    else:
        return f"¥{amount:,.0f}"

def calculate_customer_cycles(sales_data, current_year):
    """计算客户下单周期和异常行为"""
    # 获取最近12个月的数据
    end_date = sales_data['订单日期'].max()
    start_date = end_date - timedelta(days=365)
    recent_data = sales_data[sales_data['订单日期'] >= start_date].copy()
    
    # 计算每个客户的订单间隔
    customer_cycles = []
    
    for customer in recent_data['经销商名称'].unique():
        customer_orders = recent_data[recent_data['经销商名称'] == customer].sort_values('订单日期')
        
        if len(customer_orders) < 2:
            continue
            
        # 计算订单间隔
        order_dates = customer_orders['订单日期'].tolist()
        intervals = []
        order_details = []
        
        for i in range(1, len(order_dates)):
            interval = (order_dates[i] - order_dates[i-1]).days
            intervals.append(interval)
            
            order_details.append({
                '日期': order_dates[i-1],
                '下一单日期': order_dates[i],
                '间隔天数': interval,
                '金额': customer_orders.iloc[i-1]['金额']
            })
        
        # 添加最后一个订单
        last_order = customer_orders.iloc[-1]
        days_since_last = (end_date - order_dates[-1]).days
        order_details.append({
            '日期': order_dates[-1],
            '下一单日期': None,
            '间隔天数': days_since_last,
            '金额': last_order['金额'],
            '距今天数': days_since_last
        })
        
        if intervals:
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 0
            
            # 预测下次订单时间
            predicted_date = order_dates[-1] + timedelta(days=int(avg_interval))
            
            customer_cycles.append({
                '客户': customer,
                '总销售额': customer_orders['金额'].sum(),
                '订单次数': len(customer_orders),
                '平均间隔': avg_interval,
                '间隔标准差': std_interval,
                '最后订单日期': order_dates[-1],
                '距今天数': days_since_last,
                '预测下单日期': predicted_date,
                '订单详情': order_details,
                '异常状态': '正常' if days_since_last <= avg_interval * 1.5 else 
                           '轻度异常' if days_since_last <= avg_interval * 2 else '严重异常'
            })
    
    # 按总销售额排序，获取Top 20
    cycles_df = pd.DataFrame(customer_cycles)
    if not cycles_df.empty:
        cycles_df = cycles_df.nlargest(20, '总销售额')  # 保持Top 20
    
    return cycles_df

def calculate_risk_prediction(sales_data, current_date=None):
    """计算客户风险预测模型"""
    if current_date is None:
        current_date = datetime.now()
    
    # 获取最近12个月的数据用于建模
    model_end_date = sales_data['订单日期'].max()
    model_start_date = model_end_date - timedelta(days=365)
    model_data = sales_data[sales_data['订单日期'] >= model_start_date].copy()
    
    risk_predictions = []
    
    for customer in model_data['经销商名称'].unique():
        customer_orders = model_data[model_data['经销商名称'] == customer].sort_values('订单日期')
        
        if len(customer_orders) < 3:  # 需要至少3个订单才能建模
            continue
        
        # 计算历史特征
        order_dates = customer_orders['订单日期'].tolist()
        order_amounts = customer_orders['金额'].tolist()
        
        # 计算间隔
        intervals = []
        for i in range(1, len(order_dates)):
            intervals.append((order_dates[i] - order_dates[i-1]).days)
        
        # 基础统计
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals) if len(intervals) > 1 else avg_interval * 0.2
        avg_amount = np.mean(order_amounts)
        std_amount = np.std(order_amounts) if len(order_amounts) > 1 else avg_amount * 0.2
        
        # 计算趋势
        if len(intervals) >= 3:
            # 间隔趋势（是否在拉长）
            recent_intervals = intervals[-3:]
            interval_trend = (recent_intervals[-1] - recent_intervals[0]) / max(recent_intervals[0], 1)
        else:
            interval_trend = 0
        
        if len(order_amounts) >= 3:
            # 金额趋势（是否在下降）
            recent_amounts = order_amounts[-3:]
            amount_trend = (recent_amounts[-1] - recent_amounts[0]) / max(recent_amounts[0], 1)
        else:
            amount_trend = 0
        
        # 当前状态
        last_order_date = order_dates[-1]
        days_since_last = (current_date - last_order_date).days
        last_amount = order_amounts[-1]
        
        # 风险评分计算
        # 1. 断单风险
        if days_since_last > avg_interval:
            # 使用正态分布计算超期概率
            z_score = (days_since_last - avg_interval) / max(std_interval, 1)
            # 基础断单概率
            disconnect_risk_base = min(0.99, 1 / (1 + np.exp(-z_score)))
            # 考虑趋势调整
            disconnect_risk = disconnect_risk_base * (1 + interval_trend * 0.3)
        else:
            # 预测未来30天的断单风险
            future_days = days_since_last + 30
            z_score = (future_days - avg_interval) / max(std_interval, 1)
            disconnect_risk = min(0.99, 1 / (1 + np.exp(-z_score + 1)))
        
        # 2. 减量风险
        if last_amount < avg_amount * 0.7:
            amount_z_score = (avg_amount - last_amount) / max(std_amount, 1)
            reduction_risk_base = min(0.99, 1 / (1 + np.exp(-amount_z_score)))
            reduction_risk = reduction_risk_base * (1 - amount_trend * 0.3)
        else:
            reduction_risk = max(0.1, 0.3 + amount_trend * 0.5) if amount_trend < 0 else 0.1
        
        # 3. 综合流失风险
        # 权重：断单风险60%，减量风险40%
        churn_risk = disconnect_risk * 0.6 + reduction_risk * 0.4
        
        # 调整因子
        # 如果是老客户（订单数>10），降低风险
        if len(customer_orders) > 10:
            churn_risk *= 0.8
        
        # 如果最近有大额订单，降低风险
        if last_amount > avg_amount * 1.5:
            churn_risk *= 0.7
        
        # 确定风险等级
        if churn_risk >= 0.8:
            risk_level = '高风险'
            risk_color = '#e74c3c'
        elif churn_risk >= 0.5:
            risk_level = '中风险'
            risk_color = '#f39c12'
        elif churn_risk >= 0.2:
            risk_level = '低风险'
            risk_color = '#f1c40f'
        else:
            risk_level = '安全'
            risk_color = '#27ae60'
        
        # 确定主要风险类型
        if disconnect_risk > reduction_risk * 1.5:
            main_risk_type = '断单风险'
        elif reduction_risk > disconnect_risk * 1.5:
            main_risk_type = '减量风险'
        else:
            main_risk_type = '综合风险'
        
        # 生成行动建议
        if churn_risk >= 0.8:
            if days_since_last > avg_interval * 1.5:
                action = '立即电话联系，了解是否有问题'
            else:
                action = '密切关注，准备主动联系'
        elif churn_risk >= 0.5:
            action = '定期回访，了解需求变化'
        else:
            action = '常规维护'
        
        # 预测下次订单
        predicted_next_order = last_order_date + timedelta(days=int(avg_interval))
        predicted_amount = avg_amount * (1 + amount_trend * 0.2)
        
        # 计算置信区间
        confidence_interval = std_interval / max(avg_interval, 1) * 100
        
        risk_predictions.append({
            '客户': customer,
            '流失风险概率': churn_risk * 100,
            '断单风险': disconnect_risk * 100,
            '减量风险': reduction_risk * 100,
            '置信区间': min(20, confidence_interval),
            '风险等级': risk_level,
            '风险颜色': risk_color,
            '主要风险': main_risk_type,
            '最后订单日期': last_order_date,
            '距今天数': days_since_last,
            '平均周期': avg_interval,
            '平均金额': avg_amount,
            '最后金额': last_amount,
            '建议行动': action,
            '预测下单日期': predicted_next_order,
            '预测金额': predicted_amount,
            '历史订单数': len(customer_orders),
            '金额趋势': '下降' if amount_trend < -0.1 else '上升' if amount_trend > 0.1 else '稳定',
            '周期趋势': '延长' if interval_trend > 0.1 else '缩短' if interval_trend < -0.1 else '稳定'
        })
    
    # 转换为DataFrame并排序
    risk_df = pd.DataFrame(risk_predictions)
    if not risk_df.empty:
        risk_df = risk_df.sort_values('流失风险概率', ascending=False)
    
    return risk_df

def create_risk_dashboard(risk_df):
    """创建风险仪表盘"""
    # 1. 风险分布图（增强悬停信息）
    fig_dist = go.Figure()
    
    # 按风险等级分组
    risk_levels = ['高风险', '中风险', '低风险', '安全']
    colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60']
    
    for level, color in zip(risk_levels, colors):
        level_data = risk_df[risk_df['风险等级'] == level]
        if not level_data.empty:
            # 准备悬停信息
            hover_customers = level_data.head(10)  # 显示前10个客户
            hover_text = f"<b>{level}</b><br>客户数: {len(level_data)}<br><br><b>客户列表：</b><br>"
            for _, customer in hover_customers.iterrows():
                hover_text += f"• {customer['客户']} (风险:{customer['流失风险概率']:.0f}%)<br>"
            if len(level_data) > 10:
                hover_text += f"... 还有{len(level_data)-10}个客户"
            
            fig_dist.add_trace(go.Bar(
                name=level,
                x=[level],
                y=[len(level_data)],
                marker_color=color,
                text=len(level_data),
                textposition='auto',
                hovertemplate=hover_text + '<extra></extra>'
            ))
    
    fig_dist.update_layout(
        title='客户风险等级分布',
        xaxis_title='风险等级',
        yaxis_title='客户数量',
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # 2. 风险概率分布直方图（增强悬停信息）
    fig_hist = go.Figure()
    
    # 创建直方图数据
    hist_data = np.histogram(risk_df['流失风险概率'], bins=20, range=(0, 100))
    bin_centers = (hist_data[1][:-1] + hist_data[1][1:]) / 2
    
    # 为每个bin准备客户列表
    hover_texts = []
    for i in range(len(hist_data[0])):
        bin_min = hist_data[1][i]
        bin_max = hist_data[1][i+1]
        bin_customers = risk_df[(risk_df['流失风险概率'] >= bin_min) & (risk_df['流失风险概率'] < bin_max)]
        
        hover_text = f"<b>风险区间: {bin_min:.0f}%-{bin_max:.0f}%</b><br>"
        hover_text += f"客户数: {len(bin_customers)}<br><br>"
        
        if len(bin_customers) > 0:
            hover_text += "<b>客户列表：</b><br>"
            for _, customer in bin_customers.head(5).iterrows():
                hover_text += f"• {customer['客户']} ({customer['流失风险概率']:.1f}%)<br>"
            if len(bin_customers) > 5:
                hover_text += f"... 还有{len(bin_customers)-5}个客户"
        
        hover_texts.append(hover_text)
    
    fig_hist.add_trace(go.Bar(
        x=bin_centers,
        y=hist_data[0],
        marker_color='#667eea',
        opacity=0.7,
        name='客户分布',
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=hover_texts
    ))
    
    # 添加风险区间标注
    fig_hist.add_vrect(x0=80, x1=100, fillcolor="#e74c3c", opacity=0.1, 
                      annotation_text="高风险区", annotation_position="top")
    fig_hist.add_vrect(x0=50, x1=80, fillcolor="#f39c12", opacity=0.1,
                      annotation_text="中风险区", annotation_position="top")
    fig_hist.add_vrect(x0=20, x1=50, fillcolor="#f1c40f", opacity=0.1,
                      annotation_text="低风险区", annotation_position="top")
    fig_hist.add_vrect(x0=0, x1=20, fillcolor="#27ae60", opacity=0.1,
                      annotation_text="安全区", annotation_position="top")
    
    fig_hist.update_layout(
        title='客户流失风险概率分布',
        xaxis_title='流失风险概率 (%)',
        yaxis_title='客户数量',
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # 3. 风险矩阵散点图（优化显示）
    fig_matrix = go.Figure()
    
    # 为每个客户创建散点
    for _, customer in risk_df.iterrows():
        hover_text = f"<b style='font-size:14px;'>{customer['客户']}</b><br><br>" + \
                    f"<b>📊 风险评估结果：</b><br>" + \
                    f"• 综合流失风险: <b style='color:{customer['风险颜色']}'>{customer['流失风险概率']:.1f}%</b><br>" + \
                    f"• 断单风险: {customer['断单风险']:.1f}%<br>" + \
                    f"• 减量风险: {customer['减量风险']:.1f}%<br>" + \
                    f"• 风险等级: <b>{customer['风险等级']}</b><br><br>" + \
                    f"<b>📈 业务指标：</b><br>" + \
                    f"• 最后订单: {customer['最后订单日期'].strftime('%Y-%m-%d')} ({customer['距今天数']}天前)<br>" + \
                    f"• 平均下单周期: {customer['平均周期']:.0f}天<br>" + \
                    f"• 平均订单金额: {format_amount(customer['平均金额'])}<br>" + \
                    f"• 最后订单金额: {format_amount(customer['最后金额'])}<br><br>" + \
                    f"<b>📋 趋势分析：</b><br>" + \
                    f"• 金额趋势: {customer['金额趋势']}<br>" + \
                    f"• 周期趋势: {customer['周期趋势']}<br><br>" + \
                    f"<b>🎯 建议行动：</b><br>" + \
                    f"<span style='color:{customer['风险颜色']}'>{customer['建议行动']}</span>"
        
        # 只为高风险客户显示标签
        show_text = customer['流失风险概率'] >= 70
        
        fig_matrix.add_trace(go.Scatter(
            x=[customer['断单风险']],
            y=[customer['减量风险']],
            mode='markers+text' if show_text else 'markers',
            marker=dict(
                size=12,
                color=customer['风险颜色'],
                line=dict(color='white', width=2),
                opacity=0.8
            ),
            text=customer['客户'][:8] + '...' if len(customer['客户']) > 8 and show_text else '',
            textposition='top center',
            textfont=dict(size=9),
            name=customer['风险等级'],
            hovertemplate=hover_text + '<extra></extra>',
            showlegend=False
        ))
    
    # 添加风险区域
    fig_matrix.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100,
                        fillcolor="rgba(231, 76, 60, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100,
                        fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50,
                        fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50,
                        fillcolor="rgba(39, 174, 96, 0.1)", layer="below", line=dict(width=0))
    
    # 添加区域标签
    fig_matrix.add_annotation(x=75, y=75, text="高风险区", showarrow=False,
                             font=dict(size=14, color='#e74c3c'), opacity=0.7)
    fig_matrix.add_annotation(x=25, y=75, text="断单风险", showarrow=False,
                             font=dict(size=12, color='#f39c12'), opacity=0.7)
    fig_matrix.add_annotation(x=75, y=25, text="减量风险", showarrow=False,
                             font=dict(size=12, color='#f39c12'), opacity=0.7)
    fig_matrix.add_annotation(x=25, y=25, text="低风险区", showarrow=False,
                             font=dict(size=14, color='#27ae60'), opacity=0.7)
    
    # 添加对角线
    fig_matrix.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode='lines',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_matrix.update_layout(
        title=dict(
            text='客户风险矩阵 - 断单风险 vs 减量风险',
            font=dict(size=16, color='#2d3748')
        ),
        xaxis=dict(title='断单风险 (%)', range=[-5, 105]),
        yaxis=dict(title='减量风险 (%)', range=[-5, 105]),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    return fig_dist, fig_hist, fig_matrix

def create_timeline_chart(cycles_df):
    """创建美化的客户下单时间轴图表"""
    fig = go.Figure()
    
    # 设置颜色方案
    color_scale = {
        '正常': '#48bb78',
        '轻度异常': '#ed8936', 
        '严重异常': '#e53e3e'
    }
    
    # 为每个客户创建一条时间轴（增加间距）
    for idx, customer_data in cycles_df.iterrows():
        y_position = idx * 1.3  # 适度的行间距
        orders = customer_data['订单详情']
        
        # 收集所有订单数据用于绘制
        dates = []
        amounts = []
        colors = []
        sizes = []
        hover_texts = []
        
        for i, order in enumerate(orders):
            dates.append(order['日期'])
            amounts.append(order['金额'])
            
            # 确定颜色和大小
            if order.get('距今天数'):
                # 最后一个订单
                color = color_scale.get(customer_data['异常状态'], '#667eea')
                size = 18 if customer_data['异常状态'] == '严重异常' else 13  # 调整大小差异
            else:
                # 历史订单
                interval = order['间隔天数']
                avg_interval = customer_data['平均间隔']
                if interval > avg_interval * 1.5:
                    color = color_scale['轻度异常']
                    size = 13
                else:
                    color = color_scale['正常']
                    size = 10
            
            colors.append(color)
            sizes.append(size)
            
            # 构建悬停文本
            hover_text = f"<b>{customer_data['客户']}</b><br>"
            hover_text += f"订单日期: {order['日期'].strftime('%Y-%m-%d')}<br>"
            hover_text += f"订单金额: <b>{format_amount(order['金额'])}</b><br>"
            if order.get('下一单日期'):
                hover_text += f"间隔天数: {order['间隔天数']}天"
            else:
                hover_text += f"距今天数: <b>{order['间隔天数']}天</b><br>"
                hover_text += f"状态: <b>{customer_data['异常状态']}</b>"
            
            hover_texts.append(hover_text)
        
        # 绘制订单连线（渐变效果）
        fig.add_trace(go.Scatter(
            x=dates,
            y=[y_position] * len(dates),
            mode='lines',
            line=dict(
                color='rgba(150, 150, 150, 0.25)',  # 降低透明度
                width=2,  # 减小线宽
                shape='spline'
            ),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # 绘制订单点（根据金额大小调整）
        normalized_amounts = np.array(amounts) / max(amounts) * 15 + 8  # 减小标记大小
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=[y_position] * len(dates),
            mode='markers',
            marker=dict(
                size=normalized_amounts,
                color=colors,
                line=dict(color='white', width=1.5),  # 减小边框宽度
                opacity=0.9
            ),
            text=[f"¥{amount/10000:.0f}万" if amount >= 10000 else f"¥{amount:.0f}" 
                  for amount in amounts],
            textposition='top center',
            textfont=dict(size=8, color='#666'),  # 减小字体大小
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_texts,
            showlegend=False
        ))
        
        # 添加客户名称
        fig.add_annotation(
            x=dates[0] - timedelta(days=5),
            y=y_position,
            text=customer_data['客户'][:10] + '...' if len(customer_data['客户']) > 10 else customer_data['客户'],
            xanchor='right',
            showarrow=False,
            font=dict(size=10, color='#2d3748')  # 稍微减小字体
        )
        
        # 添加平均周期基准（虚线）
        avg_interval_days = customer_data['平均间隔']
        reference_dates = []
        ref_date = dates[0]
        while ref_date <= dates[-1] + timedelta(days=30):
            reference_dates.append(ref_date)
            ref_date += timedelta(days=avg_interval_days)
        
        fig.add_trace(go.Scatter(
            x=reference_dates,
            y=[y_position - 0.25] * len(reference_dates),  # 调整位置以匹配新的间距
            mode='markers',
            marker=dict(
                symbol='line-ns',
                size=6,  # 减小参考线标记大小
                color='rgba(102, 126, 234, 0.25)'  # 降低透明度
            ),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # 添加预测点
        if customer_data['预测下单日期'] > datetime.now():
            fig.add_trace(go.Scatter(
                x=[customer_data['预测下单日期']],
                y=[y_position],
                mode='markers+text',
                marker=dict(
                    size=12,  # 减小预测点大小
                    color='rgba(102, 126, 234, 0.5)',
                    symbol='circle-open',
                    line=dict(width=2.5)  # 稍微减小线宽
                ),
                text='预测',
                textposition='top center',
                textfont=dict(size=8, color='#667eea'),  # 减小字体
                hovertemplate=f"预测下单日期: {customer_data['预测下单日期'].strftime('%Y-%m-%d')}<extra></extra>",
                showlegend=False
            ))
    
    # 添加交替背景（提高可读性）
    for i in range(0, len(cycles_df), 2):
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="y",
            x0=0,
            x1=1,
            y0=i * 1.3 - 0.4,
            y1=min((i + 1) * 1.3 - 0.4, len(cycles_df) * 1.3 - 0.5),
            fillcolor="rgba(240, 240, 240, 0.3)",
            layer="below",
            line=dict(width=0)
        )
    
    # 添加渐变背景区域（表示时间流逝）
    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=datetime.now() - timedelta(days=30),
        x1=datetime.now() + timedelta(days=30),
        y0=0,
        y1=1,
        fillcolor="rgba(102, 126, 234, 0.05)",
        layer="below",
        line=dict(width=0)
    )
    
    # 添加今日标记线
    current_date = datetime.now()
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(
            color="rgba(102, 126, 234, 0.5)",
            width=2,
            dash="dash"
        )
    )
    
    # 添加今日标注
    fig.add_annotation(
        x=current_date,
        y=1.02,
        yref="paper",
        text="今日",
        showarrow=False,
        font=dict(size=12, color="rgba(102, 126, 234, 0.8)"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(102, 126, 234, 0.5)",
        borderwidth=1,
        borderpad=4
    )
    
    # 更新布局
    fig.update_layout(
        height=max(800, len(cycles_df) * 60),  # 调整高度以适应20个客户
        xaxis=dict(
            title="时间轴",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.05)',
            type='date',
            tickformat='%Y-%m',
            dtick='M1'
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            range=[-0.5, len(cycles_df) * 1.3 - 0.5],  # 调整范围以匹配新的y位置
            autorange='reversed'
        ),
        hovermode='closest',
        paper_bgcolor='white',
        plot_bgcolor='rgba(250, 250, 250, 0.8)',
        margin=dict(l=150, r=50, t=60, b=60),  # 增加左边距以容纳客户名称
        dragmode='pan'
    )
    
    # 添加图例
    legend_elements = [
        ('正常', '#48bb78', 'circle'),
        ('轻度异常', '#ed8936', 'circle'),
        ('严重异常', '#e53e3e', 'circle'),
        ('预测', 'rgba(102, 126, 234, 0.5)', 'circle-open')
    ]
    
    for i, (name, color, symbol) in enumerate(legend_elements):
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol=symbol, line=dict(width=1.5, color='white')),  # 调整图例标记大小
            showlegend=True,
            name=name
        ))
    
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        )
    )
    
    return fig

def create_enhanced_charts(metrics, sales_data, monthly_data):
    """创建增强图表"""
    charts = {}
    
    # 1. 客户健康雷达图
    categories = ['客户健康度', '目标达成率', '价值贡献度', '客户活跃度', '风险分散度']
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics['normal_customers'] > 0 else 0,
        100 - metrics['max_dependency']
    ]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', name='当前状态',
        fillcolor='rgba(102, 126, 234, 0.3)', line=dict(color='#667eea', width=3),
        hovertemplate='<b>%{theta}</b><br>数值: %{r:.1f}%<br><extra></extra>'
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[85, 80, 70, 85, 70], theta=categories, fill='toself', name='目标基准',
        fillcolor='rgba(255, 99, 71, 0.1)', line=dict(color='#ff6347', width=2, dash='dash')
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%'),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=True, height=450, 
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    charts['health_radar'] = fig_radar
    
    # 2. Top20客户贡献分析
    if not metrics['rfm_df'].empty:
        top20_customers = metrics['rfm_df'].nlargest(20, 'M')
        total_sales = metrics['rfm_df']['M'].sum()
        
        top20_customers['销售额占比'] = (top20_customers['M'] / total_sales * 100).round(2)
        top20_customers['累计占比'] = top20_customers['销售额占比'].cumsum()
        
        fig_top20 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_top20.add_trace(go.Bar(
            x=top20_customers['客户'], y=top20_customers['M'], name='销售额',
            marker=dict(color='#667eea', opacity=0.8),
            hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<br>占比: %{customdata:.1f}%<extra></extra>',
            customdata=top20_customers['销售额占比']
        ), secondary_y=False)
        
        fig_top20.add_trace(go.Scatter(
            x=top20_customers['客户'], y=top20_customers['累计占比'], name='累计占比',
            mode='lines+markers', line=dict(color='#ff8800', width=3),
            marker=dict(size=8, color='#ff8800'),
            hovertemplate='<b>%{x}</b><br>累计占比: %{y:.1f}%<extra></extra>'
        ), secondary_y=True)
        
        fig_top20.add_hline(y=80, line_dash="dash", line_color="#e74c3c", 
                           annotation_text="80%贡献线", secondary_y=True)
        
        fig_top20.update_xaxes(title_text="客户名称", tickangle=-45, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        fig_top20.update_yaxes(title_text="销售额", secondary_y=False, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        fig_top20.update_yaxes(title_text="累计占比 (%)", range=[0, 105], secondary_y=True)
        
        fig_top20.update_layout(
            height=500, hovermode='x unified', 
            margin=dict(t=60, b=100, l=60, r=60),
            plot_bgcolor='white', 
            paper_bgcolor='white',
            showlegend=True
        )
        charts['top20'] = fig_top20
    
    # 3. 区域风险矩阵
    if not metrics['region_stats'].empty:
        fig_risk = go.Figure()
        
        # 添加背景区域
        fig_risk.add_shape(type="rect", x0=0, y0=30, x1=100, y1=100,
                          fillcolor="rgba(231, 76, 60, 0.1)", layer="below", line=dict(width=0))
        fig_risk.add_shape(type="rect", x0=0, y0=15, x1=100, y1=30,
                          fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
        fig_risk.add_shape(type="rect", x0=0, y0=0, x1=100, y1=15,
                          fillcolor="rgba(39, 174, 96, 0.1)", layer="below", line=dict(width=0))
        
        for _, region in metrics['region_stats'].iterrows():
            color = '#e74c3c' if region['最大客户依赖度'] > 30 else '#f39c12' if region['最大客户依赖度'] > 15 else '#27ae60'
            fig_risk.add_trace(go.Scatter(
                x=[region['客户数']], y=[region['最大客户依赖度']], mode='markers+text',
                marker=dict(size=max(15, min(60, region['总销售额']/100000)), color=color,
                           line=dict(color='white', width=2), opacity=0.8),
                text=region['区域'], textposition="top center", name=region['区域'],
                hovertemplate=f"<b>{region['区域']}</b><br>客户数: {region['客户数']}家<br>" +
                             f"依赖度: {region['最大客户依赖度']:.1f}%<br>" +
                             f"总销售: {format_amount(region['总销售额'])}<extra></extra>"
            ))
        
        fig_risk.add_hline(y=30, line_dash="dash", line_color="#e74c3c", 
                          annotation_text="高风险线(30%)")
        fig_risk.add_hline(y=15, line_dash="dash", line_color="#f39c12", 
                          annotation_text="中风险线(15%)")
        
        fig_risk.update_layout(
            xaxis=dict(title="客户数量", gridcolor='rgba(200,200,200,0.3)', showgrid=True),
            yaxis=dict(title="最大客户依赖度(%)", gridcolor='rgba(200,200,200,0.3)', showgrid=True,
                      range=[0, max(100, metrics['region_stats']['最大客户依赖度'].max() * 1.1)]),
            height=500, showlegend=False, 
            plot_bgcolor='white', 
            paper_bgcolor='white',
            margin=dict(t=20, b=60, l=60, r=60)
        )
        charts['risk_matrix'] = fig_risk
    
    # 4. 价值分层桑基图（使用ECharts或备选方案）
    if not metrics['rfm_df'].empty:
        # 使用更鲜明的配色方案
        customer_types = [
            ('钻石客户', '#e74c3c', '💎'),  # 鲜红色 - 最高价值
            ('黄金客户', '#f39c12', '🏆'),  # 金橙色 - 高价值
            ('白银客户', '#3498db', '🥈'),  # 天蓝色 - 中等价值
            ('潜力客户', '#2ecc71', '🌟'),  # 翠绿色 - 有潜力
            ('流失风险', '#95a5a6', '⚠️')   # 灰色 - 风险客户
        ]
        
        # 统计总客户数
        total_count = len(metrics['rfm_df'])
        
        if ECHARTS_AVAILABLE:
            # 使用 ECharts 创建桑基图
            try:
                # 准备节点数据
                nodes = [{
                    "name": f"全部客户\n{total_count}家",
                    "itemStyle": {"color": "#9b59b6"}
                }]
                links = []
                
                for customer_type, color, emoji in customer_types:
                    type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
                    count = len(type_customers)
                    
                    if count > 0:
                        percentage = count / total_count * 100
                        node_name = f"{emoji} {customer_type}\n{count}家 ({percentage:.1f}%)"
                        
                        # 节点数据
                        nodes.append({
                            "name": node_name,
                            "itemStyle": {"color": color}
                        })
                        
                        # 获取客户名单
                        customer_names = type_customers.nlargest(10, 'M')['客户'].tolist()
                        customer_sales = type_customers.nlargest(10, 'M')['M'].tolist()
                        
                        # 构建简化的tooltip文本
                        tooltip_text = f"{emoji} {customer_type}: {count}家 ({percentage:.1f}%)"
                        
                        links.append({
                            "source": f"全部客户\n{total_count}家",
                            "target": node_name,
                            "value": count
                        })
                
                # ECharts 配置
                option = {
                    "title": {
                        "text": "客户价值分层流向分析",
                        "left": "center",
                        "top": 20,
                        "textStyle": {
                            "fontSize": 20,
                            "fontWeight": "bold",
                            "color": "#2d3748"
                        }
                    },
                    "tooltip": {
                        "trigger": "item",
                        "triggerOn": "mousemove",
                        "backgroundColor": "rgba(255,255,255,0.98)",
                        "borderColor": "#667eea",
                        "borderWidth": 2,
                        "borderRadius": 8,
                        "padding": [10, 15],
                        "textStyle": {
                            "fontSize": 13,
                            "color": "#2d3748",
                            "lineHeight": 20
                        },
                        "extraCssText": "box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);"
                    },
                    "series": [{
                        "type": "sankey",
                        "layout": "none",
                        "emphasis": {
                            "focus": "adjacency",
                            "itemStyle": {
                                "shadowBlur": 20,
                                "shadowColor": "rgba(102, 126, 234, 0.5)"
                            }
                        },
                        "data": nodes,
                        "links": links,
                        "lineStyle": {
                            "color": "gradient",
                            "curveness": 0.5,
                            "opacity": 0.6
                        },
                        "label": {
                            "position": "right",
                            "fontSize": 14,
                            "fontWeight": "bold",
                            "color": "#374151"
                        },
                        "itemStyle": {
                            "borderWidth": 2,
                            "borderColor": "#fff",
                            "borderRadius": 4
                        },
                        "animationDuration": 1500,
                        "animationEasing": "cubicOut"
                    }],
                    "color": ['#9b59b6', '#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#95a5a6'],
                    "backgroundColor": "#f8f9fa"
                }
                
                # 创建一个占位符用于渲染 ECharts
                charts['sankey'] = ('echarts', option)
                print("✅ ECharts 桑基图配置创建成功")
                
            except Exception as e:
                print(f"ECharts 桑基图创建失败: {e}")
                ECHARTS_AVAILABLE = False
        
        if not ECHARTS_AVAILABLE:
            # 使用 Plotly 树状图作为更稳定的备选方案
            try:
                import plotly.express as px
                
                # 准备数据
                data_for_treemap = []
                
                # 添加根节点
                data_for_treemap.append({
                    'labels': '全部客户',
                    'parents': '',
                    'values': total_count,
                    'text': f'全部客户<br>{total_count}家',
                    'color': '#9b59b6'
                })
                
                # 添加各类型客户
                for customer_type, color, emoji in customer_types:
                    type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
                    count = len(type_customers)
                    
                    if count > 0:
                        percentage = count / total_count * 100
                        
                        # 获取客户名单用于悬停显示
                        top_customers = type_customers.nlargest(10, 'M')
                        hover_text = f"{emoji} {customer_type}<br>"
                        hover_text += f"客户数: {count}家<br>"
                        hover_text += f"占比: {percentage:.1f}%<br><br>"
                        hover_text += "Top 10客户：<br>"
                        for _, cust in top_customers.iterrows():
                            hover_text += f"• {cust['客户'][:15]}... ({format_amount(cust['M'])})<br>"
                        if len(type_customers) > 10:
                            hover_text += f"... 还有{len(type_customers)-10}个客户"
                        
                        data_for_treemap.append({
                            'labels': f"{emoji} {customer_type}",
                            'parents': '全部客户',
                            'values': count,
                            'text': f"{emoji} {customer_type}<br>{count}家 ({percentage:.1f}%)",
                            'color': color,
                            'hover_text': hover_text
                        })
                
                # 创建数据框
                df_treemap = pd.DataFrame(data_for_treemap)
                
                # 创建树状图
                fig_treemap = go.Figure(go.Treemap(
                    labels=df_treemap['labels'],
                    parents=df_treemap['parents'],
                    values=df_treemap['values'],
                    text=df_treemap['text'],
                    textinfo="text",
                    hovertext=df_treemap.get('hover_text', df_treemap['text']),
                    hovertemplate='%{hovertext}<extra></extra>',
                    marker=dict(
                        colors=df_treemap['color'],
                        line=dict(width=3, color='white')
                    ),
                    textfont=dict(size=16, family="Microsoft YaHei")
                ))
                
                fig_treemap.update_layout(
                    title=dict(
                        text="客户价值分层分布",
                        font=dict(size=20, color='#2d3748', family="Microsoft YaHei"),
                        x=0.5,
                        xanchor='center'
                    ),
                    height=550,
                    margin=dict(t=100, b=20, l=20, r=20),
                    paper_bgcolor='#f8f9fa',
                    plot_bgcolor='white'
                )
                
                charts['sankey'] = fig_treemap
                print("✅ 使用树状图作为桑基图的替代方案")
                
            except Exception as e:
                print(f"树状图创建也失败: {e}")
                # 最后的备选方案：堆叠条形图
                try:
                    # 创建堆叠条形图的代码...（保持原有的备选方案）
                    customer_type_counts = metrics['rfm_df']['类型'].value_counts()
                    
                    fig_bar = go.Figure()
                    
                    # 按价值从高到低排序
                    ordered_types = ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']
                    
                    for customer_type in ordered_types:
                        if customer_type in customer_type_counts.index:
                            count = customer_type_counts[customer_type]
                            percentage = count / len(metrics['rfm_df']) * 100
                            
                            # 查找对应的颜色和emoji
                            for ct, color, emoji in customer_types:
                                if ct == customer_type:
                                    break
                            
                            # 获取该类型的客户列表
                            type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
                            top_customers = type_customers.nlargest(10, 'M')
                            
                            # 构建悬停文本
                            hover_text = f"<b>{emoji} {customer_type}</b><br>"
                            hover_text += f"客户数: {count}家<br>"
                            hover_text += f"占比: {percentage:.1f}%<br><br>"
                            hover_text += "<b>Top 10客户：</b><br>"
                            for _, cust in top_customers.iterrows():
                                hover_text += f"• {cust['客户']} ({format_amount(cust['M'])})<br>"
                            if len(type_customers) > 10:
                                hover_text += f"... 还有{len(type_customers)-10}个客户"
                            
                            fig_bar.add_trace(go.Bar(
                                y=[customer_type],
                                x=[count],
                                name=f"{emoji} {customer_type}",
                                orientation='h',
                                marker=dict(
                                    color=color,
                                    line=dict(color='white', width=2)
                                ),
                                text=f"{count}家 ({percentage:.1f}%)",
                                textposition='inside',
                                textfont=dict(size=14, color='white', family='Microsoft YaHei'),
                                hovertemplate=hover_text + '<extra></extra>',
                                showlegend=True
                            ))
                    
                    fig_bar.update_layout(
                        title=dict(
                            text="客户价值分层分布",
                            font=dict(size=20, color='#2d3748', family="Microsoft YaHei"),
                            x=0.5,
                            xanchor='center'
                        ),
                        xaxis=dict(
                            title="客户数量",
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(0,0,0,0.05)'
                        ),
                        yaxis=dict(
                            title="",
                            showgrid=False,
                            categoryorder='array',
                            categoryarray=['流失风险', '潜力客户', '白银客户', '黄金客户', '钻石客户']
                        ),
                        height=500,
                        plot_bgcolor='white',
                        paper_bgcolor='#f8f9fa',
                        margin=dict(t=100, b=80, l=150, r=80),
                        barmode='relative',
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=12,
                            font_family="Microsoft YaHei"
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    
                    charts['sankey'] = fig_bar
                    print("✅ 使用堆叠条形图作为最终备选方案")
                    
                except Exception as e3:
                    print(f"所有备选方案都失败: {e3}")
                    charts['sankey'] = None
    
    # 5. 月度趋势图
    if not sales_data.empty:
        try:
            sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
            monthly_sales = sales_data.groupby('年月')['金额'].agg(['sum', 'count']).reset_index()
            monthly_sales['年月'] = monthly_sales['年月'].astype(str)
            
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_sales['年月'], y=monthly_sales['sum'], mode='lines+markers',
                name='销售额', fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color='#667eea', width=3),
                hovertemplate='月份: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
            ), secondary_y=False)
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_sales['年月'], y=monthly_sales['count'], mode='lines+markers',
                name='订单数', line=dict(color='#ff6b6b', width=2),
                hovertemplate='月份: %{x}<br>订单数: %{y}笔<extra></extra>'
            ), secondary_y=True)
            
            fig_trend.update_xaxes(title_text="月份", showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
            fig_trend.update_yaxes(title_text="销售额", secondary_y=False, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
            fig_trend.update_yaxes(title_text="订单数", secondary_y=True)
            fig_trend.update_layout(
                height=450, hovermode='x unified',
                margin=dict(t=60, b=60, l=60, r=60),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            charts['trend'] = fig_trend
        except Exception as e:
            print(f"趋势图创建失败: {e}")
    
    # 6. 目标达成散点图
    if not metrics['customer_achievement_details'].empty:
        try:
            achievement_df = metrics['customer_achievement_details'].copy()
            achievement_df = achievement_df.dropna(subset=['目标', '实际'])
            achievement_df = achievement_df[achievement_df['目标'] > 0]
            
            if not achievement_df.empty:
                colors = ['#48bb78' if rate >= 100 else '#ffd93d' if rate >= 80 else '#ff6b6b' 
                         for rate in achievement_df['达成率']]
                sizes = [max(10, min(50, rate/3)) for rate in achievement_df['达成率']]
                
                fig_scatter = go.Figure()
                fig_scatter.add_trace(go.Scatter(
                    x=achievement_df['目标'], y=achievement_df['实际'], mode='markers',
                    marker=dict(size=sizes, color=colors, line=dict(width=2, color='white'), opacity=0.8),
                    text=achievement_df['客户'], name='客户达成情况',
                    hovertemplate='<b>%{text}</b><br>目标: ¥%{x:,.0f}<br>实际: ¥%{y:,.0f}<br>达成率: %{customdata:.1f}%<extra></extra>',
                    customdata=achievement_df['达成率']
                ))
                
                max_val = max(achievement_df['目标'].max(), achievement_df['实际'].max()) * 1.1
                fig_scatter.add_trace(go.Scatter(
                    x=[0, max_val], y=[0, max_val], mode='lines', name='目标线(100%)',
                    line=dict(color='#e74c3c', width=3, dash='dash')
                ))
                fig_scatter.add_trace(go.Scatter(
                    x=[0, max_val], y=[0, max_val * 0.8], mode='lines', name='达成线(80%)',
                    line=dict(color='#f39c12', width=2, dash='dot')
                ))
                
                fig_scatter.update_layout(
                    xaxis_title="目标金额", yaxis_title="实际金额", height=500,
                    hovermode='closest', 
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=60, b=60, l=60, r=60),
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                )
                charts['target_scatter'] = fig_scatter
        except Exception as e:
            print(f"散点图创建失败: {e}")
    
    return charts

def main():
    # 主标题
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
        st.error("❌ 数据加载失败，请检查数据文件。")
        return
    
    # 创建图表
    charts = create_enhanced_charts(metrics, sales_data, monthly_data)
    
    # 标签页
    tabs = st.tabs([
        "📊 核心指标", "🎯 健康诊断", "⚠️ 风险评估", 
        "💎 价值分层", "📈 目标追踪", "📉 趋势分析"
    ])
    
    # Tab 1: 核心指标
    with tabs[0]:
        # 核心业务指标
        st.markdown("### 💰 核心业务指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-value">{format_amount(metrics['total_sales'])}</div>
                <div class="metric-label">年度销售总额</div>
                <div class="metric-sublabel">同比 {'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['normal_rate']:.1f}%</div>
                <div class="metric-label">客户健康度</div>
                <div class="metric-sublabel">正常客户 {metrics['normal_customers']} 家</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            risk_color = '#e74c3c' if metrics['max_dependency'] > 30 else '#667eea'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {risk_color} !important;">
                    {metrics['max_dependency']:.1f}%
                </div>
                <div class="metric-label">最高区域风险</div>
                <div class="metric-sublabel">{metrics['max_dependency_region']} 区域</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['target_achievement_rate']:.1f}%</div>
                <div class="metric-label">目标达成率</div>
                <div class="metric-sublabel">{metrics['achieved_customers']}/{metrics['total_target_customers']} 家达成</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 客户分布指标
        st.markdown("### 👥 客户分布指标")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        customer_types = [
            (col1, "💎", metrics['diamond_customers'], "钻石客户"),
            (col2, "🏆", metrics['gold_customers'], "黄金客户"),
            (col3, "🥈", metrics['silver_customers'], "白银客户"),
            (col4, "🌟", metrics['potential_customers'], "潜力客户"),
            (col5, "⚠️", metrics['risk_customers'], "流失风险")
        ]
        
        for col, icon, count, label in customer_types:
            color = '#e74c3c' if label == "流失风险" else '#667eea'
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.8rem; margin-bottom: 0.3rem;">{icon}</div>
                    <div class="metric-value" style="color: {color} !important;">{count}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 客户状态统计
        st.markdown("### 📈 客户状态统计")
        col1, col2, col3 = st.columns(3)
        
        status_data = [
            (col1, metrics['total_customers'], "总客户数", "#667eea"),
            (col2, metrics['normal_customers'], "正常客户", "#48bb78"),
            (col3, metrics['closed_customers'], "闭户客户", "#e74c3c")
        ]
        
        for col, count, label, color in status_data:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {color} !important;">{count}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 价值分层关键指标
        if not metrics['rfm_df'].empty:
            st.markdown("### 💎 价值分层关键指标")
            col1, col2, col3, col4 = st.columns(4)
            
            total_revenue = metrics['rfm_df']['M'].sum()
            top_revenue = metrics['rfm_df'][metrics['rfm_df']['类型'].isin(['钻石客户', '黄金客户'])]['M'].sum()
            risk_revenue = metrics['rfm_df'][metrics['rfm_df']['类型'] == '流失风险']['M'].sum()
            avg_customer_value = total_revenue / len(metrics['rfm_df']) if len(metrics['rfm_df']) > 0 else 0
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-value">{format_amount(total_revenue)}</div>
                    <div class="metric-label">总客户价值</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                top_percentage = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{top_percentage:.1f}%</div>
                    <div class="metric-label">高价值客户贡献度</div>
                    <div class="metric-sublabel">钻石+黄金客户</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                risk_percentage = (risk_revenue / total_revenue * 100) if total_revenue > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #e74c3c !important;">{risk_percentage:.1f}%</div>
                    <div class="metric-label">风险客户价值占比</div>
                    <div class="metric-sublabel">需要立即关注</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{format_amount(avg_customer_value)}</div>
                    <div class="metric-label">平均客户价值</div>
                    <div class="metric-sublabel">年度平均</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 2: 健康诊断
    with tabs[1]:
        if 'health_radar' in charts:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户健康状态综合评估</div>
                <div class="chart-subtitle">多维度评估客户群体整体健康状况</div>
            </div>
            ''', unsafe_allow_html=True)
            st.plotly_chart(charts['health_radar'], use_container_width=True, key="health_radar")
    
    # Tab 3: 风险评估
    with tabs[2]:
        # 创建子标签页
        risk_subtabs = st.tabs(["📊 客户贡献分析", "🕐 下单周期监测", "🎯 风险预警模型"])
        
        with risk_subtabs[0]:
            # Top20客户分析
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">Top 20 客户贡献度分析</div>
                <div class="chart-subtitle">展示前20大客户的销售额分布和累计贡献度</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if 'top20' in charts:
                st.plotly_chart(charts['top20'], use_container_width=True, key="top20_chart")
            
            # 区域风险矩阵  
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">区域客户依赖风险矩阵</div>
                <div class="chart-subtitle">评估各区域的客户集中度风险</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if 'risk_matrix' in charts:
                st.plotly_chart(charts['risk_matrix'], use_container_width=True, key="risk_matrix_chart")
        
        with risk_subtabs[1]:
            # 下单周期监测
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户下单周期监测</div>
                <div class="chart-subtitle">追踪Top 20客户的下单规律，识别异常行为</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # 计算客户周期数据
            if sales_data is not None and not sales_data.empty:
                cycles_df = calculate_customer_cycles(sales_data, metrics['current_year'])
                
                if not cycles_df.empty:
                    # 显示时间轴图表
                    timeline_fig = create_timeline_chart(cycles_df)
                    st.plotly_chart(timeline_fig, use_container_width=True, key="timeline_chart")
                    
                    # 添加提示信息
                    st.info("💡 提示：可以拖动图表查看更多细节，鼠标悬停查看详细信息")
                else:
                    st.info("暂无足够的订单数据进行周期分析")
            else:
                st.info("暂无订单数据")
        
        with risk_subtabs[2]:
            # 风险预警模型
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户风险预警模型</div>
                <div class="chart-subtitle">基于机器学习的30天流失风险预测</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if sales_data is not None and not sales_data.empty:
                # 计算风险预测
                risk_df = calculate_risk_prediction(sales_data)
                
                if not risk_df.empty:
                    # 创建风险仪表盘
                    fig_dist, fig_hist, fig_matrix = create_risk_dashboard(risk_df)
                    
                    # 显示图表
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(fig_dist, use_container_width=True, key="risk_dist")
                    with col2:
                        st.plotly_chart(fig_hist, use_container_width=True, key="risk_hist")
                    
                    st.plotly_chart(fig_matrix, use_container_width=True, key="risk_matrix_scatter")
                    
                    # 高风险客户详细列表
                    st.markdown('''
                    <div class="chart-header">
                        <div class="chart-title">高风险客户详细分析</div>
                        <div class="chart-subtitle">需要重点关注的客户列表</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # 筛选高风险客户
                    high_risk_customers = risk_df[risk_df['流失风险概率'] >= 50].head(10)
                    
                    if not high_risk_customers.empty:
                        for _, customer in high_risk_customers.iterrows():
                            risk_icon = '🔴' if customer['风险等级'] == '高风险' else '🟠'
                            
                            # 风险说明
                            risk_factors = []
                            if customer['断单风险'] > 70:
                                risk_factors.append(f"断单风险高达 {customer['断单风险']:.0f}%")
                            if customer['减量风险'] > 70:
                                risk_factors.append(f"减量风险达 {customer['减量风险']:.0f}%")
                            if customer['周期趋势'] == '延长':
                                risk_factors.append("下单周期正在延长")
                            if customer['金额趋势'] == '下降':
                                risk_factors.append("订单金额持续下降")
                            
                            st.markdown(f"""
                            <div class="insight-card" style="border-left-color: {customer['风险颜色']};">
                                <h4>{risk_icon} {customer['客户']}</h4>
                                <ul>
                                    <li><strong>流失概率：</strong>{customer['流失风险概率']:.1f}% (±{customer['置信区间']:.0f}%)</li>
                                    <li><strong>风险类型：</strong>{customer['主要风险']}</li>
                                    <li><strong>最后订单：</strong>{customer['最后订单日期'].strftime('%Y-%m-%d')} ({customer['距今天数']}天前)</li>
                                    <li><strong>平均周期：</strong>{customer['平均周期']:.0f}天 | 平均金额：{format_amount(customer['平均金额'])}</li>
                                    <li><strong>风险因素：</strong>{' | '.join(risk_factors)}</li>
                                    <li><strong>预测下单：</strong>{customer['预测下单日期'].strftime('%Y-%m-%d')} | 预测金额：{format_amount(customer['预测金额'])}</li>
                                    <li><strong>建议行动：</strong><span style="color: {customer['风险颜色']}; font-weight: bold;">{customer['建议行动']}</span></li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 导出风险报告
                        if st.button("📥 导出风险预警报告", key="export_risk_report"):
                            export_cols = ['客户', '流失风险概率', '风险等级', '主要风险', 
                                         '最后订单日期', '距今天数', '平均周期', '平均金额',
                                         '建议行动', '金额趋势', '周期趋势']
                            export_df = risk_df[export_cols].copy()
                            export_df['流失风险概率'] = export_df['流失风险概率'].round(1)
                            csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="下载CSV文件",
                                data=csv,
                                file_name=f"客户风险预警报告_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.success("✅ 暂无高风险客户，业务状况良好！")
                else:
                    st.info("需要更多历史数据才能进行风险预测")
            else:
                st.info("暂无订单数据")
    
    # Tab 4: 价值分层
    with tabs[3]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">客户价值流动分析</div>
            <div class="chart-subtitle">展示客户在不同价值层级间的分布</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if 'sankey' in charts and charts['sankey'] is not None:
            # 检查是否是 ECharts 配置
            if isinstance(charts['sankey'], tuple) and charts['sankey'][0] == 'echarts':
                if ECHARTS_AVAILABLE:
                    # 使用 streamlit-echarts 渲染
                    st_echarts(
                        options=charts['sankey'][1],
                        height="550px",
                        key="sankey_echarts"
                    )
                else:
                    st.error("需要安装 streamlit-echarts 组件来显示桑基图。请运行：pip install streamlit-echarts")
            else:
                # 显示 Plotly 图表
                st.plotly_chart(charts['sankey'], use_container_width=True, key="sankey_chart")
                
                # 如果可以安装streamlit-echarts，显示提示
                if not ECHARTS_AVAILABLE:
                    with st.expander("💡 想要更好的桑基图效果？"):
                        st.markdown("""
                        当前使用的是备选图表。安装 `streamlit-echarts` 可以获得更好的桑基图效果：
                        
                        ```bash
                        pip install streamlit-echarts
                        ```
                        
                        安装后重启应用即可看到增强的桑基图，支持：
                        - 🎯 更流畅的动画效果
                        - 📊 更好的交互体验
                        - 👁️ 悬停查看详细客户名单
                        """)
            
            # 添加价值分层说明
            st.markdown("""
            <div class='insight-card'>
                <h4>💡 价值分层说明</h4>
                <ul>
                    <li><span style='color: #e74c3c; font-size: 1.2em;'>●</span> <strong>💎 钻石客户</strong>：近期活跃、高频率、高金额的核心客户</li>
                    <li><span style='color: #f39c12; font-size: 1.2em;'>●</span> <strong>🏆 黄金客户</strong>：表现良好、贡献稳定的重要客户</li>
                    <li><span style='color: #3498db; font-size: 1.2em;'>●</span> <strong>🥈 白银客户</strong>：有一定贡献但仍有提升空间的客户</li>
                    <li><span style='color: #2ecc71; font-size: 1.2em;'>●</span> <strong>🌟 潜力客户</strong>：需要培育和激活的客户群体</li>
                    <li><span style='color: #95a5a6; font-size: 1.2em;'>●</span> <strong>⚠️ 流失风险</strong>：长期未下单或订单减少的风险客户</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 暂无客户价值分层数据。请确保已加载客户销售数据。")
    
    # Tab 5: 目标追踪
    with tabs[4]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">客户目标达成分析</div>
            <div class="chart-subtitle">评估当前年度（{0}年）各客户的销售目标完成情况</div>
        </div>
        '''.format(metrics['current_year']), unsafe_allow_html=True)
        
        if 'target_scatter' in charts:
            st.plotly_chart(charts['target_scatter'], use_container_width=True, key="target_scatter_chart")
    
    # Tab 6: 趋势分析
    with tabs[5]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">销售趋势分析</div>
            <div class="chart-subtitle">追踪销售额和订单数的月度变化趋势</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if 'trend' in charts:
            st.plotly_chart(charts['trend'], use_container_width=True, key="trend_chart")
        
        # 趋势洞察
        st.markdown("""
        <div class='insight-card'>
            <h4>📊 关键洞察</h4>
            <ul>
                <li>销售额呈现季节性波动，需提前规划产能</li>
                <li>订单数与销售额增长不同步，客单价在变化</li>
                <li>建议深入分析高峰低谷期原因</li>
                <li>关注异常波动月份的业务驱动因素</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
