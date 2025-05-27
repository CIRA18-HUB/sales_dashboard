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
    
    /* 响应式 */
    @media (max-width: 768px) {
        .metric-value, .big-value { font-size: 1.8rem; }
        .metric-card { padding: 1rem; margin: 0.5rem 0; }
        .main-header { padding: 1.5rem 0; }
    }
    
    /* 确保文字颜色 */
    h1, h2, h3, h4, h5, h6 { color: #1f2937 !important; }
    p, span, div { color: #374151; }
    
    /* 图表标题样式 */
    .chart-title {
        color: #1f2937;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .chart-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        text-align: center;
        line-height: 1.4;
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
            title=dict(text="区域客户依赖风险矩阵", font=dict(size=16)),
            xaxis=dict(title="客户数量", gridcolor='rgba(200,200,200,0.3)', showgrid=True),
            yaxis=dict(title="最大客户依赖度(%)", gridcolor='rgba(200,200,200,0.3)', showgrid=True,
                      range=[0, max(100, metrics['region_stats']['最大客户依赖度'].max() * 1.1)]),
            height=500, showlegend=False, 
            plot_bgcolor='white', 
            paper_bgcolor='white',
            margin=dict(t=80, b=60, l=60, r=60)
        )
        charts['risk_matrix'] = fig_risk
    
    # 4. 价值分层桑基图
    if not metrics['rfm_df'].empty:
        try:
            source, target, value, labels, colors = [], [], [], ['全部客户'], ['#f0f0f0']
            customer_types = [('钻石客户', '#ff6b6b'), ('黄金客户', '#ffd93d'), ('白银客户', '#c0c0c0'), 
                            ('潜力客户', '#4ecdc4'), ('流失风险', '#a8a8a8')]
            
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
            
            if source:
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(pad=15, thickness=20, line=dict(color="white", width=1),
                             label=labels, color=colors),
                    link=dict(source=source, target=target, value=value,
                             color='rgba(180, 180, 180, 0.3)')
                )])
                fig_sankey.update_layout(
                    height=500, 
                    margin=dict(t=60, b=60, l=60, r=60),
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                )
                charts['sankey'] = fig_sankey
        except Exception as e:
            print(f"桑基图创建失败: {e}")
    
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
    
    # Tab 2: 健康诊断
    with tabs[1]:
        if 'health_radar' in charts:
            st.markdown('<div class="chart-title">客户健康状态综合评估</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-subtitle">多维度评估客户群体整体健康状况</div>', unsafe_allow_html=True)
            st.plotly_chart(charts['health_radar'], use_container_width=True, key="health_radar")
        
        # 健康度评分
        health_score = (metrics['normal_rate'] * 0.4 + metrics['target_achievement_rate'] * 0.3 + metrics['high_value_rate'] * 0.3)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="metric-card" style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem;'>
                <h1 style='font-size: 3rem; margin: 0; color: white !important;'>{health_score:.1f}</h1>
                <p style='font-size: 1.2rem; margin: 0.5rem 0 0 0; color: white !important;'>综合健康度评分</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: 风险评估
    with tabs[2]:
        # Top20客户分析
        st.markdown('<div class="chart-title">Top 20 客户贡献度分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">展示前20大客户的销售额分布和累计贡献度</div>', unsafe_allow_html=True)
        
        if 'top20' in charts:
            st.plotly_chart(charts['top20'], use_container_width=True, key="top20_chart")
        
        # 区域风险矩阵  
        st.markdown('<div class="chart-title">区域客户依赖风险矩阵</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">评估各区域的客户集中度风险</div>', unsafe_allow_html=True)
        
        if 'risk_matrix' in charts:
            st.plotly_chart(charts['risk_matrix'], use_container_width=True, key="risk_matrix_chart")
    
    # Tab 4: 价值分层
    with tabs[3]:
        st.markdown('<div class="chart-title">客户价值流动分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">展示客户在不同价值层级间的分布</div>', unsafe_allow_html=True)
        
        if 'sankey' in charts:
            st.plotly_chart(charts['sankey'], use_container_width=True, key="sankey_chart")
    
    # Tab 5: 目标追踪
    with tabs[4]:
        st.markdown('<div class="chart-title">客户目标达成分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">评估各客户的销售目标完成情况</div>', unsafe_allow_html=True)
        
        if 'target_scatter' in charts:
            st.plotly_chart(charts['target_scatter'], use_container_width=True, key="target_scatter_chart")
    
    # Tab 6: 趋势分析
    with tabs[5]:
        st.markdown('<div class="chart-title">销售趋势分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">追踪销售额和订单数的月度变化趋势</div>', unsafe_allow_html=True)
        
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
