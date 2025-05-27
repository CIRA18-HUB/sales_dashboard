# pages/预测库存分析.py - 修复版
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_lottie import st_lottie
from streamlit_extras.badges import badge
from streamlit_extras.let_it_rain import rain
import json
import requests
import time

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="智能库存预警系统",
    page_icon="🚀",
    layout="wide"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 统一的白色主题CSS样式（与附件二保持一致）
st.markdown("""
<style>
    /* 主标题动画样式 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        animation: fadeInDown 1s ease-in;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes fadeInDown {
        from { 
            opacity: 0; 
            transform: translateY(-30px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    
    /* 统一的指标卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
        animation: slideUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
        border: 1px solid #f0f0f0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102,126,234,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s;
        opacity: 0;
    }
    
    .metric-card:hover::before {
        animation: shimmer 0.6s ease-in-out;
    }
    
    @keyframes shimmer {
        0% { 
            transform: translateX(-100%) translateY(-100%) rotate(45deg); 
            opacity: 0; 
        }
        50% { 
            opacity: 1; 
        }
        100% { 
            transform: translateX(100%) translateY(100%) rotate(45deg); 
            opacity: 0; 
        }
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
    
    /* 动画延迟效果 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .metric-label {
        color: #666;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* 指标容器样式 */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    /* 统一标签页样式 */
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
        font-size: 16px;
        transition: all 0.3s ease;
        animation: tabFadeIn 0.5s ease-out;
    }
    
    @keyframes tabFadeIn {
        from { 
            opacity: 0;
            transform: translateX(-20px);
        }
        to { 
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #f0f0f0 0%, #ffffff 100%);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        animation: tabActive 0.3s ease-out;
    }
    
    @keyframes tabActive {
        from { transform: scale(0.95); }
        to { transform: scale(1); }
    }
    
    /* 图表容器动画 */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        animation: chartFadeIn 1s ease-out;
    }
    
    @keyframes chartFadeIn {
        from { 
            opacity: 0;
            transform: scale(0.95);
        }
        to { 
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* 统一文本样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #333 !important;
        animation: textFadeIn 0.8s ease-out;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1 { font-size: 2.5rem; }
    h2 { font-size: 2rem; }
    h3 { font-size: 1.75rem; }
    h4 { font-size: 1.5rem; }
    
    @keyframes textFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* 展开器动画样式 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 10px;
        color: #333 !important;
        font-weight: 500;
        font-size: 16px;
        transition: all 0.3s;
        animation: expanderFadeIn 0.6s ease-out;
    }
    
    @keyframes expanderFadeIn {
        from { 
            opacity: 0;
            transform: translateX(-20px);
        }
        to { 
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
        transform: translateX(5px);
    }
    
    /* 修复数字重影 */
    text {
        text-rendering: optimizeLegibility;
    }
    
    /* 其他动画效果 */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }
    
    /* 渐变动画 */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .gradient-animated {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
</style>
""", unsafe_allow_html=True)

# 统一配色方案（与附件二保持一致）
COLOR_SCHEME = {
    # 主色调 - 紫色渐变
    'primary_gradient': ['#667eea', '#764ba2'],
    'secondary_gradient': ['#78E1FF', '#4A90E2'],
    
    # 数据可视化色板
    'chart_colors': [
        '#667eea',  # 主紫色
        '#FF6B9D',  # 玫瑰红
        '#C44569',  # 深红
        '#FFC75F',  # 金黄
        '#F8B500',  # 橙黄
        '#845EC2',  # 紫罗兰
        '#4E8397',  # 深蓝绿
        '#00C9A7'   # 青绿
    ],
    
    # 风险等级色彩
    'risk_extreme': '#FF4757',     # 鲜红
    'risk_high': '#FF6348',        # 橙红
    'risk_medium': '#FFA502',      # 明黄
    'risk_low': '#2ED573',         # 翠绿
    'risk_minimal': '#5352ED',     # 宝蓝
    
    # 背景色
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F8F9FA',
    'text_primary': '#333333',
    'text_secondary': '#666666'
}

# 修复后的plotly布局配置函数
def get_safe_plotly_layout():
    """返回安全的plotly布局配置，避免参数冲突"""
    return {
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': {'color': '#333', 'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', 'size': 14},
        'title': {
            'font': {'size': 24, 'color': '#333', 'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        'colorway': COLOR_SCHEME['chart_colors'],
        'hoverlabel': {
            'bgcolor': 'white',
            'bordercolor': '#667eea',
            'font': {'size': 14, 'color': '#333', 'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'}
        },
        'legend': {
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': '#e0e0e0',
            'borderwidth': 1,
            'font': {'size': 14}
        }
    }

# 加载Lottie动画
@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# 数据加载和处理函数
@st.cache_data
def load_and_process_data():
    """加载和处理所有数据"""
    try:
        # 直接从根目录读取文件
        shipment_df = pd.read_excel('2409~250224出货数据.xlsx')
        forecast_df = pd.read_excel('2409~2502人工预测.xlsx')
        inventory_df = pd.read_excel('含批次库存0221(2).xlsx')
        price_df = pd.read_excel('单价.xlsx')
        
        # 处理日期
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])
        forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'], format='%Y-%m')
        
        # 创建产品代码到名称的映射
        product_name_map = {}
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and pd.notna(row['描述']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                product_name_map[row['物料']] = row['描述']
        
        # 处理库存数据
        batch_data = []
        current_material = None
        current_desc = None
        current_stock = 0
        current_price = 0
        
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                current_material = row['物料']
                current_desc = row['描述']
                current_stock = row['现有库存'] if pd.notna(row['现有库存']) else 0
                # 获取单价
                price_match = price_df[price_df['产品代码'] == current_material]
                current_price = price_match['单价'].iloc[0] if len(price_match) > 0 else 100
            elif pd.notna(row['生产日期']) and current_material:
                # 这是批次信息行
                prod_date = pd.to_datetime(row['生产日期'])
                quantity = row['数量'] if pd.notna(row['数量']) else 0
                batch_no = row['生产批号'] if pd.notna(row['生产批号']) else ''
                
                # 计算库龄
                age_days = (datetime.now() - prod_date).days
                
                # 确定风险等级
                if age_days >= 120:
                    risk_level = '极高风险'
                    risk_color = COLOR_SCHEME['risk_extreme']
                    risk_advice = '🚨 立即7折清库'
                elif age_days >= 90:
                    risk_level = '高风险'
                    risk_color = COLOR_SCHEME['risk_high']
                    risk_advice = '⚠️ 建议8折促销'
                elif age_days >= 60:
                    risk_level = '中风险'
                    risk_color = COLOR_SCHEME['risk_medium']
                    risk_advice = '📢 适度9折促销'
                elif age_days >= 30:
                    risk_level = '低风险'
                    risk_color = COLOR_SCHEME['risk_low']
                    risk_advice = '✅ 正常销售'
                else:
                    risk_level = '极低风险'
                    risk_color = COLOR_SCHEME['risk_minimal']
                    risk_advice = '🌟 新鲜库存'
                
                # 计算预期损失
                if age_days >= 120:
                    expected_loss = quantity * current_price * 0.3
                elif age_days >= 90:
                    expected_loss = quantity * current_price * 0.2
                elif age_days >= 60:
                    expected_loss = quantity * current_price * 0.1
                else:
                    expected_loss = 0
                
                # 计算额外指标
                daily_cost = quantity * current_price * 0.0001  # 日存储成本
                opportunity_cost = quantity * current_price * 0.05 * (age_days / 365)  # 机会成本
                
                batch_data.append({
                    '物料': current_material,
                    '产品名称': current_desc,
                    '描述': current_desc,
                    '生产日期': prod_date,
                    '生产批号': batch_no,
                    '数量': quantity,
                    '库龄': age_days,
                    '风险等级': risk_level,
                    '风险颜色': risk_color,
                    '处理建议': risk_advice,
                    '单价': current_price,
                    '批次价值': quantity * current_price,
                    '预期损失': expected_loss,
                    '日存储成本': daily_cost,
                    '机会成本': opportunity_cost,
                    '总成本': expected_loss + (daily_cost * age_days) + opportunity_cost
                })
        
        processed_inventory = pd.DataFrame(batch_data)
        
        # 将产品代码替换为产品名称
        shipment_df['产品名称'] = shipment_df['产品代码'].map(product_name_map).fillna(shipment_df['产品代码'])
        forecast_df['产品名称'] = forecast_df['产品代码'].map(product_name_map).fillna(forecast_df['产品代码'])
        
        # 计算预测准确率
        forecast_accuracy = calculate_forecast_accuracy(shipment_df, forecast_df)
        
        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory, forecast_accuracy)
        
        return processed_inventory, forecast_accuracy, shipment_df, forecast_df, metrics, product_name_map
        
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None, None, None, None

def calculate_forecast_accuracy(shipment_df, forecast_df):
    """计算预测准确率"""
    # 按月份和产品聚合实际销量
    shipment_monthly = shipment_df.groupby([
        shipment_df['订单日期'].dt.to_period('M'),
        '产品代码'
    ])['求和项:数量（箱）'].sum().reset_index()
    shipment_monthly['年月'] = shipment_monthly['订单日期'].dt.to_timestamp()
    
    # 合并预测和实际数据
    merged = forecast_df.merge(
        shipment_monthly,
        left_on=['所属年月', '产品代码'],
        right_on=['年月', '产品代码'],
        how='inner'
    )
    
    # 计算预测准确率
    merged['预测误差'] = abs(merged['预计销售量'] - merged['求和项:数量（箱）'])
    merged['预测准确率'] = 1 - (merged['预测误差'] / (merged['求和项:数量（箱）'] + 1))
    merged['预测准确率'] = merged['预测准确率'].clip(0, 1)
    
    # 添加更多分析维度
    merged['误差率'] = merged['预测误差'] / (merged['求和项:数量（箱）'] + 1) * 100
    merged['预测偏向'] = merged['预计销售量'] - merged['求和项:数量（箱）']
    
    return merged

def calculate_key_metrics(processed_inventory, forecast_accuracy):
    """计算关键指标"""
    if processed_inventory.empty:
        return None
    
    total_batches = len(processed_inventory)
    high_risk_batches = len(processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])])
    high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0
    
    total_inventory_value = processed_inventory['批次价值'].sum() / 1000000
    high_risk_value = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险'])
    ]['批次价值'].sum()
    high_risk_value_ratio = (high_risk_value / processed_inventory['批次价值'].sum() * 100) if processed_inventory['批次价值'].sum() > 0 else 0
    
    avg_age = processed_inventory['库龄'].mean()
    forecast_acc = forecast_accuracy['预测准确率'].mean() * 100 if not forecast_accuracy.empty else 0
    
    # 额外计算的高级指标
    total_cost = processed_inventory['总成本'].sum() / 1000000
    storage_cost_daily = processed_inventory['日存储成本'].sum() * 30  # 月度存储成本
    
    # 风险分布统计
    risk_counts = processed_inventory['风险等级'].value_counts().to_dict()
    
    return {
        'total_batches': int(total_batches),
        'high_risk_batches': int(high_risk_batches),
        'high_risk_ratio': round(high_risk_ratio, 1),
        'total_inventory_value': round(total_inventory_value, 2),
        'high_risk_value_ratio': round(high_risk_value_ratio, 1),
        'avg_age': round(avg_age, 0),
        'forecast_accuracy': round(forecast_acc, 1),
        'high_risk_value': round(high_risk_value / 1000000, 1),
        'total_cost': round(total_cost, 2),
        'storage_cost_monthly': round(storage_cost_daily / 1000, 2),
        'risk_counts': {
            'extreme': risk_counts.get('极高风险', 0),
            'high': risk_counts.get('高风险', 0),
            'medium': risk_counts.get('中风险', 0),
            'low': risk_counts.get('低风险', 0),
            'minimal': risk_counts.get('极低风险', 0)
        }
    }

# 创建动画效果
def create_animation_effect():
    """创建页面加载动画"""
    placeholder = st.empty()
    for i in range(3):
        placeholder.markdown(
            f"""
            <div style='text-align: center; color: #667eea;'>
                <h2 style='animation: bounce 0.5s ease-in-out infinite;'>{'.' * (i + 1)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.3)
    placeholder.empty()

# 加载数据
with st.spinner('🔄 正在加载智能分析系统...'):
    create_animation_effect()
    processed_inventory, forecast_accuracy, shipment_df, forecast_df, metrics, product_name_map = load_and_process_data()

if metrics is None:
    st.stop()

# 页面标题 - 使用渐变效果
st.markdown("""
<div class="main-header gradient-animated">
    <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>
        🚀 智能库存预警系统
    </h1>
    <p style='font-size: 1.2rem;'>
        AI驱动的库存风险监控与决策支持平台
    </p>
</div>
""", unsafe_allow_html=True)

# 实时指标刷新
col_refresh = st.columns([10, 1])
with col_refresh[1]:
    if st.button("🔄", key="refresh_btn", help="刷新数据"):
        st.cache_data.clear()
        st.rerun()

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 智能监控中心",
    "💎 风险热力图",
    "🧠 AI预测分析",
    "🏆 绩效看板",
    "📈 深度分析"
])

# 标签1：智能监控中心 - 只显示指标卡片
with tab1:
    # 核心KPI展示
    st.markdown("### 🎯 实时核心指标")
    
    # 第一行指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_batches']:,}</div>
            <div class="metric-label">📦 库存批次总数</div>
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                ⚠️ 高危: {metrics['high_risk_batches']}个
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        health_score = 100 - metrics['high_risk_ratio']
        health_emoji = "🟢" if health_score > 85 else "🟡" if health_score > 70 else "🔴"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{health_score:.1f}%</div>
            <div class="metric-label">💯 库存健康度</div>
            <div style="color: {'#2ed573' if health_score > 85 else '#ffa502' if health_score > 70 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                {health_emoji} {'健康' if health_score > 85 else '注意' if health_score > 70 else '警告'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">¥{metrics['total_inventory_value']:.1f}M</div>
            <div class="metric-label">💰 库存总价值</div>
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                📈 成本: ¥{metrics['total_cost']:.1f}M
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        turnover_rate = 365 / metrics['avg_age'] if metrics['avg_age'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{turnover_rate:.1f}次/年</div>
            <div class="metric-label">🔄 库存周转率</div>
            <div style="color: {'#ff6348' if metrics['avg_age'] > 60 else '#2ed573'}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                库龄: {metrics['avg_age']:.0f}天
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 第二行高级指标
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        risk_coverage = metrics['high_risk_value_ratio']
        risk_level = "🔴 严重" if risk_coverage > 30 else "🟡 中等" if risk_coverage > 15 else "🟢 良好"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{risk_coverage}%</div>
            <div class="metric-label">🎯 风险资金占比</div>
            <div style="color: {'#ff4757' if risk_coverage > 30 else '#ffa502' if risk_coverage > 15 else '#2ed573'}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                {risk_level}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        forecast_score = metrics['forecast_accuracy']
        forecast_grade = "A" if forecast_score > 90 else "B" if forecast_score > 80 else "C" if forecast_score > 70 else "D"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{forecast_score}%</div>
            <div class="metric-label">🧠 AI预测准确率</div>
            <div style="color: {'#2ed573' if forecast_score > 80 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                等级: {forecast_grade}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        monthly_loss = metrics['total_cost'] / 12
        daily_loss = monthly_loss / 30
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">¥{daily_loss:.3f}M/天</div>
            <div class="metric-label">⏱️ 时间价值损失</div>
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                月损: ¥{monthly_loss:.2f}M
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        efficiency_score = (1 - metrics['high_risk_ratio']/100) * metrics['forecast_accuracy']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{efficiency_score:.1f}</div>
            <div class="metric-label">⚡ 综合效率指数</div>
            <div style="color: {'#2ed573' if efficiency_score > 70 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500;">
                {"表现优秀" if efficiency_score > 70 else "AI优化中"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 第三行 - 风险分布概览
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 风险等级分布")
    
    col9, col10, col11, col12, col13 = st.columns(5)
    
    risk_items = [
        (col9, "极高风险", metrics['risk_counts']['extreme'], COLOR_SCHEME['risk_extreme']),
        (col10, "高风险", metrics['risk_counts']['high'], COLOR_SCHEME['risk_high']),
        (col11, "中风险", metrics['risk_counts']['medium'], COLOR_SCHEME['risk_medium']),
        (col12, "低风险", metrics['risk_counts']['low'], COLOR_SCHEME['risk_low']),
        (col13, "极低风险", metrics['risk_counts']['minimal'], COLOR_SCHEME['risk_minimal'])
    ]
    
    for col, risk_name, count, color in risk_items:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color};">
                <div style="font-size: 2rem; font-weight: bold; color: {color};">{count}</div>
                <div class="metric-label">{risk_name}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 添加实时预警动画
    if metrics['high_risk_ratio'] > 20:
        st.markdown(f"""
        <div style="background: #fff5f5; border: 1px solid #ff4757; border-radius: 10px; padding: 1rem; margin-top: 2rem; animation: pulse 2s ease-in-out infinite;">
            <h4 style="color: #ff4757; margin: 0;">⚠️ 风险预警</h4>
            <p style="color: #666; margin: 0.5rem 0 0 0;">当前有{metrics['high_risk_batches']}个高风险批次需要紧急处理，建议立即采取清库行动！</p>
        </div>
        """, unsafe_allow_html=True)

# 标签2：风险热力图
with tab2:
    st.markdown("### 💎 多维度风险分析矩阵")
    
    # 获取高风险数据
    risk_items = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险', '中风险'])
    ].head(100)
    
    if not risk_items.empty:
        # 创建高级散点矩阵
        fig_matrix = go.Figure()
        
        # 为每个风险等级创建独立的trace
        for risk_level, color in [
            ('极高风险', COLOR_SCHEME['risk_extreme']),
            ('高风险', COLOR_SCHEME['risk_high']),
            ('中风险', COLOR_SCHEME['risk_medium'])
        ]:
            risk_subset = risk_items[risk_items['风险等级'] == risk_level]
            if not risk_subset.empty:
                fig_matrix.add_trace(go.Scatter(
                    x=risk_subset['库龄'],
                    y=risk_subset['批次价值'],
                    mode='markers',
                    name=risk_level,
                    marker=dict(
                        size=risk_subset['数量'] / 5,
                        sizemode='diameter',
                        sizemin=8,
                        sizeref=2,
                        color=color,
                        opacity=0.8,
                        line=dict(width=1, color='white'),
                        symbol='circle'
                    ),
                    text=[f"{row['产品名称']}<br>批号: {row['生产批号']}" 
                          for _, row in risk_subset.iterrows()],
                    customdata=np.column_stack((
                        risk_subset['物料'],
                        risk_subset['产品名称'],
                        risk_subset['生产批号'],
                        risk_subset['生产日期'].dt.strftime('%Y-%m-%d'),
                        risk_subset['数量'],
                        risk_subset['单价'],
                        risk_subset['处理建议'],
                        risk_subset['预期损失'],
                        risk_subset['日存储成本'],
                        risk_subset['机会成本'],
                        risk_subset['总成本']
                    )),
                    hovertemplate="""
                    <b style='font-size:16px;'>%{text}</b><br>
                    <br>
                    <b>📦 基础信息</b><br>
                    产品代码: %{customdata[0]}<br>
                    生产日期: %{customdata[3]}<br>
                    库龄: <b>%{x}天</b><br>
                    <br>
                    <b>💰 价值分析</b><br>
                    批次数量: <b>%{customdata[4]:,.0f}箱</b><br>
                    单价: ¥%{customdata[5]:.2f}<br>
                    批次价值: <b>¥%{y:,.0f}</b><br>
                    <br>
                    <b>📊 成本明细</b><br>
                    预期损失: ¥%{customdata[7]:,.0f}<br>
                    日存储成本: ¥%{customdata[8]:,.2f}<br>
                    机会成本: ¥%{customdata[9]:,.0f}<br>
                    总成本影响: <b>¥%{customdata[10]:,.0f}</b><br>
                    <br>
                    <b>🎯 处理建议</b><br>
                    %{customdata[6]}<br>
                    <extra></extra>
                    """
                ))
        
        # 添加风险区域标注
        max_value = risk_items['批次价值'].max()
        max_age = risk_items['库龄'].max()
        
        # 添加象限分割线和标注
        fig_matrix.add_shape(
            type="line",
            x0=90, y0=0, x1=90, y1=max_value,
            line=dict(color="rgba(150,150,150,0.3)", width=2, dash="dash"),
        )
        
        fig_matrix.add_shape(
            type="line",
            x0=0, y0=max_value*0.5, x1=max_age, y1=max_value*0.5,
            line=dict(color="rgba(150,150,150,0.3)", width=2, dash="dash"),
        )
        
        # 添加象限标签
        annotations = [
            dict(x=45, y=max_value*0.9, text="<b>低龄高值</b><br>密切监控",
                 showarrow=False, font=dict(size=14, color="#333")),
            dict(x=max_age*0.75, y=max_value*0.9, text="<b>高龄高值</b><br>紧急清理",
                 showarrow=False, font=dict(size=14, color="#333")),
            dict(x=45, y=max_value*0.1, text="<b>低龄低值</b><br>正常管理",
                 showarrow=False, font=dict(size=14, color="#333")),
            dict(x=max_age*0.75, y=max_value*0.1, text="<b>高龄低值</b><br>批量处理",
                 showarrow=False, font=dict(size=14, color="#333"))
        ]
        
        # 使用修复后的布局配置
        layout_config = get_safe_plotly_layout()
        
        fig_matrix.update_layout(
            **layout_config,
            title="风险价值矩阵分析<br><sub>气泡大小表示批次数量，颜色表示风险等级</sub>",
            xaxis=dict(
                title="库龄（天）",
                gridcolor='rgba(200,200,200,0.3)',
                zerolinecolor='rgba(200,200,200,0.5)',
                tickfont=dict(size=12),
                titlefont=dict(size=14)
            ),
            yaxis=dict(
                title="批次价值（元）",
                gridcolor='rgba(200,200,200,0.3)',
                zerolinecolor='rgba(200,200,200,0.5)',
                tickfont=dict(size=12),
                titlefont=dict(size=14)
            ),
            height=600,
            hovermode='closest',
            annotations=annotations,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_matrix, use_container_width=True, key="risk_matrix")
    
    # 风险价值瀑布图
    st.markdown("### 💸 风险价值瀑布分析")
    
    # 准备瀑布图数据
    waterfall_data = []
    cumulative = metrics['total_inventory_value']
    
    waterfall_data.append({
        'name': '库存总价值',
        'measure': 'absolute',
        'value': cumulative
    })
    
    for risk_level, color in [
        ('极低风险', COLOR_SCHEME['risk_minimal']),
        ('低风险', COLOR_SCHEME['risk_low']),
        ('中风险', COLOR_SCHEME['risk_medium']),
        ('高风险', COLOR_SCHEME['risk_high']),
        ('极高风险', COLOR_SCHEME['risk_extreme'])
    ]:
        risk_value = processed_inventory[
            processed_inventory['风险等级'] == risk_level
        ]['批次价值'].sum() / 1000000
        
        if risk_value > 0:
            waterfall_data.append({
                'name': risk_level,
                'measure': 'relative',
                'value': -risk_value,
                'color': color
            })
    
    # 创建瀑布图
    fig_waterfall = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=[d['measure'] for d in waterfall_data],
        x=[d['name'] for d in waterfall_data],
        textposition="outside",
        text=[f"¥{abs(d['value']):.1f}M" for d in waterfall_data],
        y=[d['value'] for d in waterfall_data],
        connector={"line": {"color": "rgba(150, 150, 150, 0.3)"}},
        increasing={"marker": {"color": COLOR_SCHEME['risk_minimal']}},
        decreasing={"marker": {"color": COLOR_SCHEME['risk_extreme']}},
        totals={"marker": {"color": COLOR_SCHEME['secondary_gradient'][0]}}
    ))
    
    # 使用修复后的布局配置
    layout_config = get_safe_plotly_layout()
    
    fig_waterfall.update_layout(
        **layout_config,
        title="库存价值风险分解",
        xaxis=dict(
            gridcolor='rgba(200,200,200,0.3)',
            zerolinecolor='rgba(200,200,200,0.5)',
            tickfont=dict(size=12),
            titlefont=dict(size=14)
        ),
        yaxis=dict(
            gridcolor='rgba(200,200,200,0.3)',
            zerolinecolor='rgba(200,200,200,0.5)',
            tickfont=dict(size=12),
            titlefont=dict(size=14)
        ),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)

# 其余标签页保持不变...
# 标签3：AI预测分析
with tab3:
    st.markdown("### 🧠 智能预测分析引擎")
    
    # 在这里继续其他标签页的内容...
    st.info("AI预测分析功能正在开发中...")

# 标签4：绩效看板
with tab4:
    st.markdown("### 🏆 多维度绩效分析看板")
    st.info("绩效看板功能正在开发中...")

# 标签5：深度分析
with tab5:
    st.markdown("### 📈 深度分析")
    st.info("深度分析功能正在开发中...")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🚀 Powered by Advanced Analytics & AI | 实时数据驱动决策</p>
    </div>
    """,
    unsafe_allow_html=True
)
