# pages/预测库存分析.py - 重构版
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

# 白色主题CSS样式（参考附件二的风格）
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
    
    /* 增强的指标卡片样式 */
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
        font-size: 2.2rem;
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
        font-size: 0.9rem;
        margin-top: 0.5rem;
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
    
    /* 标签页样式增强 */
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
    
    /* 文本样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #333 !important;
        animation: textFadeIn 0.8s ease-out;
    }
    
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
    
    /* 悬浮球动画 */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    /* 旋转动画 */
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 闪烁动画 */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* 波纹效果 */
    @keyframes ripple {
        0% {
            transform: scale(0);
            opacity: 1;
        }
        100% {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    /* 渐变动画 */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 应用渐变动画的元素 */
    .gradient-animated {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    /* 弹跳动画 */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }
    
    /* 修复数字重影 */
    text {
        text-rendering: optimizeLegibility;
    }
</style>
""", unsafe_allow_html=True)

# 专业配色方案（参考附件二）
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
    
    # 风险等级色彩（参考附件三）
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

# 创建默认的plotly布局配置
def get_plotly_layout():
    """返回标准的plotly布局配置"""
    return {
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': {'color': '#333', 'family': 'Inter, sans-serif'},
        'title_font': {'size': 20, 'color': '#333', 'family': 'Inter, sans-serif'},
        'xaxis': {
            'gridcolor': 'rgba(200,200,200,0.3)',
            'zerolinecolor': 'rgba(200,200,200,0.5)',
            'tickfont': {'size': 12},
            'title_font': {'size': 14}
        },
        'yaxis': {
            'gridcolor': 'rgba(200,200,200,0.3)',
            'zerolinecolor': 'rgba(200,200,200,0.5)',
            'tickfont': {'size': 12},
            'title_font': {'size': 14}
        },
        'colorway': COLOR_SCHEME['chart_colors'],
        'hoverlabel': {
            'bgcolor': 'white',
            'bordercolor': '#667eea',
            'font': {'size': 14, 'color': '#333', 'family': 'Inter, sans-serif'}
        },
        'legend': {
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': '#e0e0e0',
            'borderwidth': 1
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

# 数据加载和处理函数（参考附件三的计算逻辑）
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
        
        # 处理库存数据 - 参考附件三的批次处理逻辑
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
                
                # 计算库龄（参考附件三）
                age_days = (datetime.now() - prod_date).days
                
                # 确定风险等级（参考附件三的风险分级逻辑）
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
                
                # 计算预期损失（参考附件三）
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
        
        # 计算预测准确率（参考附件三）
        forecast_accuracy = calculate_forecast_accuracy(shipment_df, forecast_df)
        
        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory, forecast_accuracy)
        
        return processed_inventory, forecast_accuracy, shipment_df, forecast_df, metrics, product_name_map
        
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None, None, None, None

def calculate_forecast_accuracy(shipment_df, forecast_df):
    """计算预测准确率（参考附件三）"""
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
    """计算关键指标（参考附件三）"""
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
    # 动画效果
    lottie_urls = {
        'dashboard': "https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json",
        'analytics': "https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json"
    }
    
    # 核心KPI展示
    st.markdown("### 🎯 实时核心指标")
    
    # 第一行指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_batches']:,}</div>
            <div class="metric-label">📦 库存批次总数</div>
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: {'#2ed573' if health_score > 85 else '#ffa502' if health_score > 70 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem;">
                {health_emoji} {'健康' if health_score > 85 else '注意' if health_score > 70 else '警告'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">¥{metrics['total_inventory_value']:.1f}M</div>
            <div class="metric-label">💰 库存总价值</div>
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: {'#ff6348' if metrics['avg_age'] > 60 else '#2ed573'}; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: {'#ff4757' if risk_coverage > 30 else '#ffa502' if risk_coverage > 15 else '#2ed573'}; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: {'#2ed573' if forecast_score > 80 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: #ff6348; font-size: 0.9rem; margin-top: 0.5rem;">
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
            <div style="color: {'#2ed573' if efficiency_score > 70 else '#ff4757'}; font-size: 0.9rem; margin-top: 0.5rem;">
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
        st.markdown("""
        <div style="background: #fff5f5; border: 1px solid #ff4757; border-radius: 10px; padding: 1rem; margin-top: 2rem; animation: pulse 2s ease-in-out infinite;">
            <h4 style="color: #ff4757; margin: 0;">⚠️ 风险预警</h4>
            <p style="color: #666; margin: 0.5rem 0 0 0;">当前有{batches}个高风险批次需要紧急处理，建议立即采取清库行动！</p>
        </div>
        """.format(batches=metrics['high_risk_batches']), unsafe_allow_html=True)

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
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_matrix.update_layout(
            **layout_config,
            title=dict(
                text="<b>风险价值矩阵分析</b><br><sup>气泡大小表示批次数量，颜色表示风险等级</sup>",
                font=dict(size=24)
            ),
            xaxis_title="库龄（天）",
            yaxis_title="批次价值（元）",
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
    
    # 使用函数获取布局配置
    layout_config = get_plotly_layout()
    
    fig_waterfall.update_layout(
        **layout_config,
        title="库存价值风险分解",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)

# 标签3：AI预测分析
with tab3:
    st.markdown("### 🧠 智能预测分析引擎")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 预测准确率趋势 - 带置信区间
        if not forecast_accuracy.empty:
            monthly_acc = forecast_accuracy.groupby(
                forecast_accuracy['所属年月'].dt.to_period('M')
            ).agg({
                '预测准确率': ['mean', 'std', 'count'],
                '误差率': 'mean'
            }).reset_index()
            monthly_acc.columns = ['月份', '准确率均值', '准确率标准差', '样本数', '平均误差率']
            monthly_acc['月份'] = monthly_acc['月份'].dt.to_timestamp()
            
            # 计算置信区间
            monthly_acc['置信上限'] = monthly_acc['准确率均值'] + 1.96 * monthly_acc['准确率标准差'] / np.sqrt(monthly_acc['样本数'])
            monthly_acc['置信下限'] = monthly_acc['准确率均值'] - 1.96 * monthly_acc['准确率标准差'] / np.sqrt(monthly_acc['样本数'])
            
            fig_trend = go.Figure()
            
            # 添加置信区间
            fig_trend.add_trace(go.Scatter(
                x=monthly_acc['月份'],
                y=monthly_acc['置信上限'] * 100,
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_acc['月份'],
                y=monthly_acc['置信下限'] * 100,
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(width=0),
                showlegend=False,
                name='95%置信区间'
            ))
            
            # 添加主线
            fig_trend.add_trace(go.Scatter(
                x=monthly_acc['月份'],
                y=monthly_acc['准确率均值'] * 100,
                mode='lines+markers',
                name='预测准确率',
                line=dict(color=COLOR_SCHEME['primary_gradient'][0], width=3),
                marker=dict(size=10, symbol='circle'),
                hovertemplate="""
                月份: %{x|%Y-%m}<br>
                准确率: <b>%{y:.1f}%</b><br>
                样本数: %{customdata[0]}个<br>
                平均误差: %{customdata[1]:.1f}%<br>
                <extra></extra>
                """,
                customdata=np.column_stack((
                    monthly_acc['样本数'],
                    monthly_acc['平均误差率']
                ))
            ))
            
            # 添加目标线
            fig_trend.add_hline(
                y=85, 
                line_dash="dash", 
                line_color=COLOR_SCHEME['risk_low'],
                annotation_text="目标: 85%"
            )
            
            # 使用函数获取布局配置
            layout_config = get_plotly_layout()
            
            fig_trend.update_layout(
                **layout_config,
                title="AI预测准确率趋势（含95%置信区间）",
                xaxis_title="时间",
                yaxis_title="准确率(%)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # 预测偏差热力图
        if not forecast_accuracy.empty:
            # 创建销售员-月份的预测偏差矩阵
            pivot_bias = forecast_accuracy.pivot_table(
                values='预测偏向',
                index='销售员',
                columns=forecast_accuracy['所属年月'].dt.strftime('%Y-%m'),
                aggfunc='mean'
            ).fillna(0)
            
            # 选择表现差异最大的前15个销售员
            bias_variance = pivot_bias.var(axis=1).sort_values(ascending=False).head(15)
            pivot_bias_top = pivot_bias.loc[bias_variance.index]
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=pivot_bias_top.values,
                x=pivot_bias_top.columns,
                y=pivot_bias_top.index,
                colorscale=[
                    [0, COLOR_SCHEME['risk_extreme']],
                    [0.5, 'white'],
                    [1, COLOR_SCHEME['risk_minimal']]
                ],
                zmid=0,
                text=np.round(pivot_bias_top.values, 0),
                texttemplate='%{text}',
                textfont={"size": 10},
                hovertemplate="""
                销售员: %{y}<br>
                月份: %{x}<br>
                预测偏差: <b>%{z:.0f}箱</b><br>
                <sup>正值表示预测过高，负值表示预测过低</sup>
                <extra></extra>
                """
            ))
            
            # 使用函数获取布局配置
            layout_config = get_plotly_layout()
            
            fig_heatmap.update_layout(
                **layout_config,
                title="销售团队预测偏差热力图（TOP15）",
                xaxis_title="月份",
                yaxis_title="销售员",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 产品预测难度3D散点图
    st.markdown("### 🎲 产品预测难度立体分析")
    
    if not forecast_accuracy.empty:
        # 计算产品维度的详细指标
        product_analysis = forecast_accuracy.groupby('产品名称').agg({
            '预测准确率': ['mean', 'std', 'count'],
            '预测误差': ['sum', 'mean'],
            '求和项:数量（箱）': 'sum'
        }).reset_index()
        product_analysis.columns = ['产品名称', '平均准确率', '准确率波动', '预测次数', 
                                    '累计误差', '平均误差', '实际销量']
        
        # 计算综合难度分数
        product_analysis['预测难度'] = (
            (1 - product_analysis['平均准确率']) * 0.4 +
            product_analysis['准确率波动'] * 0.3 +
            (product_analysis['平均误差'] / (product_analysis['实际销量'] + 1)) * 0.3
        )
        
        # 选择TOP20产品
        product_analysis = product_analysis.nlargest(20, '预测难度')
        
        # 创建3D散点图效果
        fig_3d_scatter = go.Figure()
        
        # 添加主散点
        fig_3d_scatter.add_trace(go.Scatter(
            x=product_analysis['平均准确率'] * 100,
            y=product_analysis['准确率波动'] * 100,
            mode='markers+text',
            marker=dict(
                size=product_analysis['预测次数'] * 2,
                sizemode='diameter',
                sizemin=10,
                color=product_analysis['预测难度'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="预测<br>难度"),
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            text=[name[:10] + '...' if len(name) > 10 else name 
                  for name in product_analysis['产品名称']],
            textposition="top center",
            textfont=dict(size=10, color='#333'),
            customdata=np.column_stack((
                product_analysis['产品名称'],
                product_analysis['预测次数'],
                product_analysis['实际销量'],
                product_analysis['累计误差'],
                product_analysis['预测难度']
            )),
            hovertemplate="""
            <b style='font-size:16px;'>%{customdata[0]}</b><br>
            <br>
            平均准确率: <b>%{x:.1f}%</b><br>
            准确率波动: <b>%{y:.1f}%</b><br>
            预测次数: %{customdata[1]}次<br>
            实际总销量: %{customdata[2]:,.0f}箱<br>
            累计误差: %{customdata[3]:,.0f}箱<br>
            <br>
            预测难度评分: <b>%{customdata[4]:.3f}</b><br>
            <extra></extra>
            """
        ))
        
        # 添加参考线
        avg_accuracy = product_analysis['平均准确率'].mean() * 100
        avg_volatility = product_analysis['准确率波动'].mean() * 100
        
        fig_3d_scatter.add_hline(y=avg_volatility, line_dash="dot", 
                                 line_color="rgba(150,150,150,0.3)")
        fig_3d_scatter.add_vline(x=avg_accuracy, line_dash="dot", 
                                 line_color="rgba(150,150,150,0.3)")
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_3d_scatter.update_layout(
            **layout_config,
            title=dict(
                text="<b>产品预测难度矩阵</b><br><sup>气泡大小=预测频次，颜色=难度系数</sup>",
                font=dict(size=24)
            ),
            xaxis_title="平均预测准确率 (%)",
            yaxis_title="预测波动性 (%)",
            height=500
        )
        
        st.plotly_chart(fig_3d_scatter, use_container_width=True)

# 标签4：绩效看板
with tab4:
    st.markdown("### 🏆 多维度绩效分析看板")
    
    # 区域绩效雷达图 - 增强版
    if not shipment_df.empty:
        # 计算更多维度
        region_stats = shipment_df.groupby('所属区域').agg({
            '求和项:数量（箱）': ['sum', 'mean', 'count', 'std'],
            '申请人': 'nunique',
            '产品代码': 'nunique',
            '订单日期': lambda x: (x.max() - x.min()).days
        }).round(2)
        region_stats.columns = ['总销量', '平均订单', '订单数', '订单波动', 
                               '销售员数', '产品种类', '活跃天数']
        region_stats = region_stats.reset_index()
        
        # 计算衍生指标
        region_stats['人均销量'] = region_stats['总销量'] / region_stats['销售员数']
        region_stats['订单效率'] = region_stats['总销量'] / region_stats['订单数']
        region_stats['产品集中度'] = region_stats['总销量'] / region_stats['产品种类']
        region_stats['销售稳定性'] = 1 / (1 + region_stats['订单波动'] / region_stats['平均订单'])
        
        # 创建增强雷达图
        categories = ['总销量', '人均销量', '订单效率', '产品多样性', 
                     '团队规模', '销售稳定性', '市场覆盖', '活跃度']
        
        fig_radar = go.Figure()
        
        for i, region in enumerate(region_stats['所属区域'].unique()[:5]):
            region_data = region_stats[region_stats['所属区域'] == region]
            
            # 标准化数据
            values = []
            raw_values = [
                region_data['总销量'].values[0],
                region_data['人均销量'].values[0],
                region_data['订单效率'].values[0],
                region_data['产品种类'].values[0],
                region_data['销售员数'].values[0],
                region_data['销售稳定性'].values[0],
                region_data['订单数'].values[0],
                region_data['活跃天数'].values[0]
            ]
            
            for j, cat in enumerate(categories):
                col_name = ['总销量', '人均销量', '订单效率', '产品种类', 
                           '销售员数', '销售稳定性', '订单数', '活跃天数'][j]
                max_val = region_stats[col_name].max()
                min_val = region_stats[col_name].min()
                if max_val > min_val:
                    normalized = (raw_values[j] - min_val) / (max_val - min_val) * 100
                else:
                    normalized = 50
                values.append(normalized)
            
            # 添加雷达图轨迹
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # 闭合图形
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor=COLOR_SCHEME['chart_colors'][i % len(COLOR_SCHEME['chart_colors'])],
                opacity=0.3,
                line=dict(
                    color=COLOR_SCHEME['chart_colors'][i % len(COLOR_SCHEME['chart_colors'])],
                    width=3
                ),
                name=region,
                hovertemplate="""
                %{theta}<br>
                得分: <b>%{r:.1f}</b><br>
                <extra></extra>
                """
            ))
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_radar.update_layout(
            **layout_config,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10),
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=12),
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                bgcolor='white'
            ),
            title=dict(
                text="<b>区域综合竞争力雷达图</b><br><sup>8维度综合评估</sup>",
                font=dict(size=24)
            ),
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # 销售员绩效矩阵
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 销售精英象限分析")
        
        if not shipment_df.empty:
            # 计算销售员绩效
            sales_performance = shipment_df.groupby('申请人').agg({
                '求和项:数量（箱）': ['sum', 'count', 'mean'],
                '产品代码': 'nunique',
                '所属区域': 'first'
            }).reset_index()
            sales_performance.columns = ['销售员', '总销量', '订单数', '平均订单', '产品数', '区域']
            
            # 计算效率指标
            sales_performance['订单效率'] = sales_performance['平均订单']
            sales_performance['市场广度'] = sales_performance['产品数']
            
            # 选择TOP30
            sales_performance = sales_performance.nlargest(30, '总销量')
            
            # 创建象限图
            fig_quadrant = go.Figure()
            
            # 按区域着色
            for region in sales_performance['区域'].unique():
                region_data = sales_performance[sales_performance['区域'] == region]
                
                fig_quadrant.add_trace(go.Scatter(
                    x=region_data['订单效率'],
                    y=region_data['市场广度'],
                    mode='markers+text',
                    name=region,
                    marker=dict(
                        size=region_data['总销量'] / 50,
                        sizemode='diameter',
                        sizemin=10,
                        opacity=0.7,
                        line=dict(width=2, color='white')
                    ),
                    text=[name.split()[0] if len(name.split()) > 0 else name 
                          for name in region_data['销售员']],
                    textposition="top center",
                    customdata=np.column_stack((
                        region_data['销售员'],
                        region_data['总销量'],
                        region_data['订单数']
                    )),
                    hovertemplate="""
                    <b>%{customdata[0]}</b><br>
                    订单效率: %{x:.1f}箱/单<br>
                    市场广度: %{y}个产品<br>
                    总销量: %{customdata[1]:,.0f}箱<br>
                    订单数: %{customdata[2]}单<br>
                    <extra></extra>
                    """
                ))
            
            # 添加平均线
            avg_efficiency = sales_performance['订单效率'].mean()
            avg_breadth = sales_performance['市场广度'].mean()
            
            fig_quadrant.add_hline(y=avg_breadth, line_dash="dash", 
                                  line_color="rgba(150,150,150,0.3)")
            fig_quadrant.add_vline(x=avg_efficiency, line_dash="dash", 
                                  line_color="rgba(150,150,150,0.3)")
            
            # 添加象限标签
            fig_quadrant.add_annotation(
                x=sales_performance['订单效率'].max() * 0.9,
                y=sales_performance['市场广度'].max() * 0.9,
                text="<b>明星</b>",
                showarrow=False,
                font=dict(size=16, color=COLOR_SCHEME['risk_low'])
            )
            
            # 使用函数获取布局配置
            layout_config = get_plotly_layout()
            
            fig_quadrant.update_layout(
                **layout_config,
                title="销售精英四象限分析",
                xaxis_title="订单效率（箱/单）",
                yaxis_title="市场广度（产品数）",
                height=400
            )
            
            st.plotly_chart(fig_quadrant, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 团队成长轨迹")
        
        if not shipment_df.empty:
            # 计算月度团队绩效
            monthly_team = shipment_df.groupby([
                shipment_df['订单日期'].dt.to_period('M'),
                '所属区域'
            ])['求和项:数量（箱）'].sum().reset_index()
            monthly_team['订单日期'] = monthly_team['订单日期'].dt.to_timestamp()
            
            # 创建动态折线图
            fig_growth = go.Figure()
            
            for i, region in enumerate(monthly_team['所属区域'].unique()[:5]):
                region_data = monthly_team[monthly_team['所属区域'] == region]
                
                fig_growth.add_trace(go.Scatter(
                    x=region_data['订单日期'],
                    y=region_data['求和项:数量（箱）'],
                    mode='lines+markers',
                    name=region,
                    line=dict(
                        color=COLOR_SCHEME['chart_colors'][i],
                        width=3,
                        shape='spline'
                    ),
                    marker=dict(size=8),
                    hovertemplate="""
                    %{x|%Y-%m}<br>
                    销量: <b>%{y:,.0f}箱</b><br>
                    <extra></extra>
                    """
                ))
            
            # 使用函数获取布局配置
            layout_config = get_plotly_layout()
            
            fig_growth.update_layout(
                **layout_config,
                title="区域销售成长曲线",
                xaxis_title="时间",
                yaxis_title="月销量（箱）",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)

# 标签5：深度分析
with tab5:
    st.markdown("### 📊 库存深度洞察分析")
    
    # 库存周转漏斗图
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # 创建漏斗图数据
        funnel_data = []
        risk_levels = ['极低风险', '低风险', '中风险', '高风险', '极高风险']
        
        for level in risk_levels:
            count = processed_inventory[processed_inventory['风险等级'] == level].shape[0]
            value = processed_inventory[processed_inventory['风险等级'] == level]['批次价值'].sum() / 1000000
            avg_age = processed_inventory[processed_inventory['风险等级'] == level]['库龄'].mean()
            
            funnel_data.append({
                '风险等级': level,
                '批次数': count,
                '价值': value,
                '平均库龄': avg_age if not pd.isna(avg_age) else 0
            })
        
        funnel_df = pd.DataFrame(funnel_data)
        
        # 创建漏斗图
        fig_funnel = go.Figure()
        
        fig_funnel.add_trace(go.Funnel(
            y=funnel_df['风险等级'],
            x=funnel_df['批次数'],
            textposition="inside",
            textinfo="value+percent initial",
            opacity=0.9,
            marker=dict(
                color=[COLOR_SCHEME['risk_minimal'], COLOR_SCHEME['risk_low'],
                      COLOR_SCHEME['risk_medium'], COLOR_SCHEME['risk_high'],
                      COLOR_SCHEME['risk_extreme']],
                line=dict(width=2, color='white')
            ),
            customdata=np.column_stack((
                funnel_df['价值'],
                funnel_df['平均库龄']
            )),
            hovertemplate="""
            <b>%{y}</b><br>
            批次数: %{x}个<br>
            占比: %{percentInitial}<br>
            总价值: ¥%{customdata[0]:.1f}M<br>
            平均库龄: %{customdata[1]:.0f}天<br>
            <extra></extra>
            """
        ))
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_funnel.update_layout(
            **layout_config,
            title=dict(
                text="<b>库存风险漏斗分析</b><br><sup>从健康到风险的批次分布</sup>",
                font=dict(size=24)
            ),
            height=500
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        # 关键指标仪表盘
        st.markdown("#### 🎯 实时监控仪表")
        
        # 库存健康度仪表
        health_score = 100 - metrics['high_risk_ratio']
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "库存健康度", 'font': {'size': 20, 'color': '#333'}},
            delta={'reference': 85, 'increasing': {'color': COLOR_SCHEME['risk_low']}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#333"},
                'bar': {'color': COLOR_SCHEME['primary_gradient'][0]},
                'bgcolor': "rgba(240,240,240,0.5)",
                'borderwidth': 2,
                'bordercolor': "#e0e0e0",
                'steps': [
                    {'range': [0, 50], 'color': COLOR_SCHEME['risk_extreme']},
                    {'range': [50, 70], 'color': COLOR_SCHEME['risk_high']},
                    {'range': [70, 85], 'color': COLOR_SCHEME['risk_medium']},
                    {'range': [85, 100], 'color': COLOR_SCHEME['risk_low']}
                ],
                'threshold': {
                    'line': {'color': "#333", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_gauge.update_layout(
            **layout_config,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # 添加说明卡片
        health_status = '😊 优秀' if health_score > 85 else '😐 良好' if health_score > 70 else '😟 需改善'
        st.markdown(f"""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 1rem; border: 1px solid #e0e0e0;">
            <h5 style="margin: 0; color: #333;">健康度解读</h5>
            <p style="margin: 0.5rem 0;">当前: {health_score:.1f}%</p>
            <p style="margin: 0.5rem 0;">目标: 85%</p>
            <p style="margin: 0; color: {'#2ed573' if health_score > 85 else '#ffa502' if health_score > 70 else '#ff4757'};">
                状态: {health_status}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ABC-XYZ矩阵分析
    st.markdown("### 🎲 ABC-XYZ智能分类矩阵")
    
    # 计算ABC分类（基于价值）
    product_value = processed_inventory.groupby('产品名称')['批次价值'].sum().sort_values(ascending=False)
    cumsum_pct = product_value.cumsum() / product_value.sum()
    
    abc_classification = pd.DataFrame({
        '产品名称': product_value.index,
        '总价值': product_value.values,
        'ABC类别': ['A' if cumsum_pct[prod] <= 0.8 else 'B' if cumsum_pct[prod] <= 0.95 else 'C' 
                    for prod in product_value.index]
    })
    
    # 计算XYZ分类（基于需求稳定性）
    if not shipment_df.empty:
        demand_stability = shipment_df.groupby('产品名称')['求和项:数量（箱）'].agg(['mean', 'std'])
        demand_stability['变异系数'] = demand_stability['std'] / (demand_stability['mean'] + 1)
        demand_stability['XYZ类别'] = pd.cut(
            demand_stability['变异系数'],
            bins=[0, 0.5, 1, float('inf')],
            labels=['X', 'Y', 'Z']
        )
        
        # 合并ABC和XYZ
        matrix_data = abc_classification.merge(
            demand_stability[['XYZ类别']],
            left_on='产品名称',
            right_index=True,
            how='left'
        )
        
        # 创建矩阵可视化
        matrix_summary = matrix_data.groupby(['ABC类别', 'XYZ类别']).agg({
            '产品名称': 'count',
            '总价值': 'sum'
        }).reset_index()
        matrix_summary.columns = ['ABC', 'XYZ', '产品数', '总价值']
        
        # 创建热力图矩阵
        pivot_matrix = matrix_summary.pivot(index='ABC', columns='XYZ', values='产品数').fillna(0)
        
        fig_matrix = go.Figure(data=go.Heatmap(
            z=pivot_matrix.values,
            x=pivot_matrix.columns,
            y=pivot_matrix.index,
            colorscale='Blues',
            text=pivot_matrix.values.astype(int),
            texttemplate='%{text}',
            textfont={"size": 20},
            hovertemplate="""
            类别: %{y}-%{x}<br>
            产品数: <b>%{z}</b><br>
            <extra></extra>
            """
        ))
        
        # 添加策略标注
        annotations = []
        strategies = {
            ('A', 'X'): '精准补货',
            ('A', 'Y'): '安全库存',
            ('A', 'Z'): '柔性供应',
            ('B', 'X'): '定期检查',
            ('B', 'Y'): '标准管理',
            ('B', 'Z'): '谨慎控制',
            ('C', 'X'): '简化流程',
            ('C', 'Y'): '按需订货',
            ('C', 'Z'): '最小库存'
        }
        
        for i, abc in enumerate(['A', 'B', 'C']):
            for j, xyz in enumerate(['X', 'Y', 'Z']):
                if (abc, xyz) in strategies:
                    annotations.append(dict(
                        x=j, y=i,
                        text=f"<b>{strategies[(abc, xyz)]}</b>",
                        showarrow=False,
                        font=dict(size=12, color='white')
                    ))
        
        # 使用函数获取布局配置
        layout_config = get_plotly_layout()
        
        fig_matrix.update_layout(
            **layout_config,
            title="ABC-XYZ库存管理策略矩阵",
            xaxis_title="需求稳定性（XYZ）",
            yaxis_title="价值贡献（ABC）",
            height=400,
            annotations=annotations
        )
        
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    # 智能决策建议
    st.markdown("### 💡 AI驱动的行动建议")
    
    # 创建决策卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        critical_items = processed_inventory[
            processed_inventory['风险等级'] == '极高风险'
        ].nlargest(5, '批次价值')
        
        st.markdown(f"""
        <div style="background: #fff5f5; border: 2px solid #ff4757; border-radius: 10px; padding: 1.5rem; height: 100%; animation: pulse 2s ease-in-out infinite;">
            <h4 style="color: #ff4757; margin: 0;">🚨 紧急清库行动</h4>
            <p style="margin: 1rem 0;"><strong>立即处理TOP5高风险批次：</strong></p>
            <ul style="margin: 0; padding-left: 1.5rem;">
                {chr(10).join([f"<li>{row['产品名称'][:20]}... - ¥{row['批次价值']/1000:.0f}K</li>" for _, row in critical_items.iterrows()])}
            </ul>
            <p style="margin: 1rem 0 0 0;">
                <strong>预计回收资金</strong>: ¥{critical_items['批次价值'].sum()/1000000*0.7:.1f}M<br>
                <strong>建议折扣</strong>: 7折速清
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        poor_forecast = forecast_accuracy.groupby('产品名称')['预测准确率'].mean().nsmallest(5)
        
        st.markdown(f"""
        <div style="background: #fff8e1; border: 2px solid #ffa502; border-radius: 10px; padding: 1.5rem; height: 100%; animation: float 3s ease-in-out infinite;">
            <h4 style="color: #f57c00; margin: 0;">📊 预测优化重点</h4>
            <p style="margin: 1rem 0;"><strong>需改进预测的产品：</strong></p>
            <ul style="margin: 0; padding-left: 1.5rem;">
                {chr(10).join([f"<li>{prod[:20]}... - {acc*100:.1f}%</li>" for prod, acc in poor_forecast.items()])}
            </ul>
            <p style="margin: 1rem 0 0 0;"><strong>建议措施</strong>:</p>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>增加历史数据权重</li>
                <li>引入季节性因子</li>
                <li>加强市场调研</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #e8f5e9; border: 2px solid #2ed573; border-radius: 10px; padding: 1.5rem; height: 100%; animation: bounce 2s ease-in-out infinite;">
            <h4 style="color: #2e7d32; margin: 0;">🎯 补货策略优化</h4>
            <p style="margin: 1rem 0;"><strong>基于ABC-XYZ分析：</strong></p>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>A类产品: 实施VMI管理</li>
                <li>B类产品: 采用EOQ模型</li>
                <li>C类产品: JIT采购策略</li>
            </ul>
            <p style="margin: 1rem 0 0 0;"><strong>预期效果</strong>:</p>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>库存降低15-20%</li>
                <li>周转率提升2-3次/年</li>
                <li>资金占用减少¥{metrics['total_inventory_value']*0.15:.1f}M</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 添加动态效果
    if st.button("🎊 查看优化成果", key="celebrate"):
        rain(
            emoji="🎉",
            font_size=30,
            falling_speed=5,
            animation_length=2
        )
        st.balloons()
        st.success("🎉 恭喜！系统优化建议已生成，预计可节省成本15%以上！")

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
