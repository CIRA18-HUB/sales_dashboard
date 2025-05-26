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
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# 自定义CSS样式
st.markdown("""
<style>
    /* 主背景渐变 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 度量卡片样式 */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
        background: rgba(255, 255, 255, 1);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.9);
        padding: 0.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        background: transparent;
        color: #4a5568;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 容器样式 */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 图表容器 */
    .plot-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .plot-container:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* 洞察卡片 */
    .insight-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: slideInLeft 0.8s ease-out;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 增强按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8, #6b4f9a);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 信息提示样式 */
    .info-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #667eea;
        font-weight: 600;
    }
    
    .info-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        font-size: 0.85rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        animation: tooltipFadeIn 0.3s ease;
    }
    
    @keyframes tooltipFadeIn {
        from { opacity: 0; transform: translateX(-50%) translateY(10px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 数据加载和处理函数
@st.cache_data(ttl=3600)  # 缓存1小时
def load_and_process_data():
    """加载并处理客户数据"""
    try:
        # 使用相对路径加载数据文件（适配GitHub部署）
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
    
    # 4. 区域风险分析
    customer_region_map = monthly_data[['客户', '所属大区']].drop_duplicates()
    sales_with_region = current_year_sales.merge(
        customer_region_map, 
        left_on='经销商名称', 
        right_on='客户', 
        how='left'
    )
    
    # 计算每个大区的依赖度
    region_stats = pd.DataFrame()
    max_dependency = 0
    max_dependency_region = ""
    region_details = []
    
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
                    
                    # 获取TOP3客户信息
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
    
    # 5. 目标达成分析
    current_year_str = str(current_year)
    current_year_targets = monthly_data[monthly_data['月份'].astype(str).str.startswith(current_year_str)]
    
    customer_actual_sales = current_year_sales.groupby('经销商名称')['金额'].sum()
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
    
    # 6. RFM客户价值分析
    current_date = datetime.now()
    customer_rfm = []
    
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
    
    return {
        'total_customers': total_customers,
        'normal_customers': normal_customers,
        'closed_customers': closed_customers,
        'normal_rate': normal_rate,
        'closed_rate': closed_rate,
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
        'customer_achievement_details': pd.DataFrame(customer_achievement_details) if customer_achievement_details else pd.DataFrame()
    }

# 创建高级可视化图表
def create_advanced_charts(metrics, sales_data, monthly_data):
    """创建高级交互式图表"""
    charts = {}
    
    # 1. 客户健康度仪表盘
    fig_health = go.Figure()
    
    # 添加半圆仪表
    fig_health.add_trace(go.Indicator(
        mode = "gauge+number+delta",
        value = metrics['normal_rate'],
        domain = {'x': [0, 0.5], 'y': [0, 1]},
        title = {'text': "客户健康度", 'font': {'size': 20}},
        delta = {'reference': 85, 'relative': False},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ff4444'},
                {'range': [50, 85], 'color': '#ffaa00'},
                {'range': [85, 100], 'color': '#00aa00'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    
    # 添加客户状态饼图
    fig_health.add_trace(go.Pie(
        values=[metrics['normal_customers'], metrics['closed_customers']],
        labels=['正常客户', '闭户客户'],
        domain={'x': [0.6, 1], 'y': [0, 1]},
        marker=dict(colors=['#667eea', '#ff4444']),
        textfont=dict(size=14, color='white'),
        textposition='inside',
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
    ))
    
    fig_health.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    charts['health'] = fig_health
    
    # 2. 区域风险热力图
    if not metrics['region_stats'].empty:
        fig_risk = go.Figure()
        
        # 创建树状图显示区域风险
        regions = metrics['region_stats']['区域'].tolist()
        dependencies = metrics['region_stats']['最大客户依赖度'].tolist()
        sales = metrics['region_stats']['总销售额'].tolist()
        customers = metrics['region_stats']['客户数'].tolist()
        
        # 计算颜色（根据依赖度）
        colors = ['#00aa00' if d < 30 else '#ffaa00' if d < 40 else '#ff4444' for d in dependencies]
        
        fig_risk.add_trace(go.Treemap(
            labels=[f"{r}<br>依赖度: {d:.1f}%<br>销售额: {s/10000:.1f}万<br>客户数: {c}" 
                   for r, d, s, c in zip(regions, dependencies, sales, customers)],
            values=sales,
            parents=[""] * len(regions),
            marker=dict(
                colorscale='RdYlGn_r',
                cmid=30,
                colorbar=dict(title="依赖度%"),
                line=dict(width=2, color='white')
            ),
            text=[f"{d:.1f}%" for d in dependencies],
            textfont=dict(size=16, color='white'),
            hovertemplate='<b>%{label}</b><br>销售额占比: %{percentRoot}<extra></extra>'
        ))
        
        fig_risk.update_layout(
            height=500,
            title={
                'text': '区域风险分布图（面积=销售额，颜色=依赖度）',
                'x': 0.5,
                'xanchor': 'center'
            },
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        charts['risk'] = fig_risk
    
    # 3. 目标达成瀑布图
    if not metrics['customer_achievement_details'].empty:
        achievement_df = metrics['customer_achievement_details'].sort_values('达成率', ascending=False).head(20)
        
        fig_target = go.Figure()
        
        # 创建瀑布图
        fig_target.add_trace(go.Waterfall(
            x=achievement_df['客户'],
            y=achievement_df['实际'] - achievement_df['目标'],
            measure=['relative'] * len(achievement_df),
            text=[f"{r:.0f}%" for r in achievement_df['达成率']],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#00aa00"}},
            decreasing={"marker": {"color": "#ff4444"}},
            hovertemplate='<b>%{x}</b><br>差额: %{y:,.0f}<br>达成率: %{text}<extra></extra>'
        ))
        
        fig_target.update_layout(
            height=500,
            title="TOP20客户目标达成情况（绿色=超额，红色=未达成）",
            xaxis_title="客户",
            yaxis_title="实际vs目标差额",
            showlegend=False,
            xaxis={'tickangle': -45}
        )
        
        charts['target'] = fig_target
    
    # 4. RFM客户价值3D散点图
    if not metrics['rfm_df'].empty:
        rfm = metrics['rfm_df']
        
        # 创建3D散点图
        fig_rfm = go.Figure()
        
        # 为每种客户类型创建不同的散点
        type_colors = {
            '钻石客户': '#e74c3c',
            '黄金客户': '#f39c12',
            '白银客户': '#95a5a6',
            '潜力客户': '#3498db',
            '流失风险': '#9b59b6'
        }
        
        for customer_type, color in type_colors.items():
            df_type = rfm[rfm['类型'] == customer_type]
            if not df_type.empty:
                fig_rfm.add_trace(go.Scatter3d(
                    x=df_type['R'],
                    y=df_type['F'],
                    z=df_type['M'],
                    mode='markers',
                    name=customer_type,
                    marker=dict(
                        size=8,
                        color=color,
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=df_type['客户'],
                    hovertemplate='<b>%{text}</b><br>' +
                                 'R (最近购买): %{x}天前<br>' +
                                 'F (购买频次): %{y}次<br>' +
                                 'M (购买金额): ¥%{z:,.0f}<extra></extra>'
                ))
        
        fig_rfm.update_layout(
            height=600,
            title="RFM客户价值分布（3D视图）",
            scene=dict(
                xaxis_title="R - 最近购买（天）",
                yaxis_title="F - 购买频次（次）",
                zaxis_title="M - 购买金额（元）",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        charts['rfm'] = fig_rfm
    
    # 5. 销售趋势动态图
    if not sales_data.empty:
        # 按月汇总销售数据
        sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
        monthly_sales = sales_data.groupby('年月')['金额'].sum().reset_index()
        monthly_sales['年月'] = monthly_sales['年月'].astype(str)
        
        fig_trend = go.Figure()
        
        # 添加面积图
        fig_trend.add_trace(go.Scatter(
            x=monthly_sales['年月'],
            y=monthly_sales['金额'],
            mode='lines+markers',
            name='月度销售额',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea', line=dict(width=2, color='white')),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
        ))
        
        # 添加趋势线
        if len(monthly_sales) > 1:
            z = np.polyfit(range(len(monthly_sales)), monthly_sales['金额'], 1)
            p = np.poly1d(z)
            fig_trend.add_trace(go.Scatter(
                x=monthly_sales['年月'],
                y=p(range(len(monthly_sales))),
                mode='lines',
                name='趋势线',
                line=dict(color='#ff6b6b', width=2, dash='dash')
            ))
        
        fig_trend.update_layout(
            height=400,
            title="月度销售趋势",
            xaxis_title="月份",
            yaxis_title="销售额",
            hovermode='x unified',
            showlegend=True
        )
        
        charts['trend'] = fig_trend
    
    return charts

# 主应用逻辑
def main():
    # 标题和动画
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                👥 客户依赖分析
            </h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">
                深入洞察客户关系，识别业务风险，优化客户组合策略
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 加载Lottie动画
        if LOTTIE_AVAILABLE:
            lottie_url = "https://assets5.lottiefiles.com/packages/lf20_qp1q7mct.json"
            lottie_json = load_lottie_url(lottie_url)
            if lottie_json:
                st_lottie(lottie_json, height=200, key="customer_analysis")
    
    # 加载数据
    with st.spinner('正在加载数据...'):
        metrics, customer_status, sales_data, monthly_data = load_and_process_data()
    
    if metrics is None:
        st.error("数据加载失败，请检查数据文件是否存在。")
        return
    
    # 创建高级图表
    charts = create_advanced_charts(metrics, sales_data, monthly_data)
    
    # 关键指标展示
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 使用metric cards展示关键指标
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="客户健康度 ❤️",
            value=f"{metrics['normal_rate']:.1f}%",
            delta=f"{metrics['normal_rate']-85:.1f}%",
            delta_color="normal" if metrics['normal_rate'] > 85 else "inverse",
            help=f"正常客户{metrics['normal_customers']}家，闭户{metrics['closed_customers']}家"
        )
    
    with col2:
        st.metric(
            label="区域最高风险 ⚠️",
            value=f"{metrics['max_dependency']:.1f}%",
            delta=f"{metrics['max_dependency']-30:.1f}%",
            delta_color="inverse",
            help=f"{metrics['max_dependency_region']}区域单一客户依赖度过高"
        )
    
    with col3:
        st.metric(
            label="目标达成率 🎯",
            value=f"{metrics['target_achievement_rate']:.1f}%",
            delta=f"{metrics['achieved_customers']}/{metrics['total_target_customers']}家",
            help=f"共{metrics['achieved_customers']}家客户达成80%以上目标"
        )
    
    with col4:
        st.metric(
            label="高价值客户占比 💎",
            value=f"{metrics['high_value_rate']:.1f}%",
            delta=f"{metrics['diamond_customers']+metrics['gold_customers']}家",
            help=f"钻石{metrics['diamond_customers']}+黄金{metrics['gold_customers']}客户"
        )
    
    with col5:
        st.metric(
            label="同比增长 📈",
            value=f"{'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%",
            delta=f"¥{(metrics['total_sales']-monthly_data['往年同期'].sum())/10000:.1f}万",
            delta_color="normal" if metrics['growth_rate'] > 0 else "inverse",
            help=f"总销售额{metrics['total_sales']/100000000:.2f}亿元"
        )
    
    # 美化metric cards
    if EXTRAS_AVAILABLE:
        style_metric_cards(
            background_color="#FFFFFF",
            border_left_color="#667eea",
            border_size_px=3,
            box_shadow=True
        )
    
    # 标签页内容
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 总览仪表盘", 
        "❤️ 客户健康分析", 
        "⚠️ 区域风险分析", 
        "🎯 目标达成分析", 
        "💎 客户价值分析"
    ])
    
    with tab1:
        # 总览仪表盘
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        
        # 核心洞察
        st.markdown("""
        <div class='insight-card'>
            <h3>💡 核心洞察</h3>
            <ul style='margin: 0; padding-left: 20px;'>
                <li>客户健康度{0}，{1}的客户保持正常运营状态</li>
                <li>{2}区域存在高度客户依赖风险，需要重点关注</li>
                <li>高价值客户群体贡献了约78.6%的销售额</li>
                <li>建议开发{3}家潜力客户，预防{4}家流失风险客户</li>
            </ul>
        </div>
        """.format(
            '良好' if metrics['normal_rate'] > 85 else '一般',
            f"{metrics['normal_rate']:.1f}%",
            metrics['max_dependency_region'],
            metrics['potential_customers'],
            metrics['risk_customers']
        ), unsafe_allow_html=True)
        
        # 显示关键图表
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(charts['health'], use_container_width=True)
        with col2:
            if 'trend' in charts:
                st.plotly_chart(charts['trend'], use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # 客户健康分析
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        
        if EXTRAS_AVAILABLE:
            colored_header(
                label="客户健康状况分析",
                description="评估客户整体健康度，识别风险客户群体",
                color_name="blue-70"
            )
        
        # 显示健康度仪表盘
        st.plotly_chart(charts['health'], use_container_width=True)
        
        # 客户状态明细
        if st.checkbox("显示客户状态明细"):
            status_summary = customer_status['状态'].value_counts()
            
            fig_status = go.Figure()
            fig_status.add_trace(go.Bar(
                x=status_summary.index,
                y=status_summary.values,
                text=status_summary.values,
                textposition='auto',
                marker_color=['#667eea', '#ff4444']
            ))
            
            fig_status.update_layout(
                title="客户状态分布",
                xaxis_title="状态",
                yaxis_title="客户数量",
                showlegend=False
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        # 区域风险分析
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        
        if EXTRAS_AVAILABLE:
            colored_header(
                label="区域风险集中度分析",
                description="识别高风险区域，制定风险分散策略",
                color_name="orange-70"
            )
        
        if 'risk' in charts:
            st.plotly_chart(charts['risk'], use_container_width=True)
            
            # 显示风险区域详情
            if st.checkbox("显示区域风险详情"):
                risk_regions = metrics['region_stats'][
                    metrics['region_stats']['最大客户依赖度'] > 30
                ].sort_values('最大客户依赖度', ascending=False)
                
                if not risk_regions.empty:
                    st.warning(f"⚠️ 发现{len(risk_regions)}个高风险区域（依赖度>30%）")
                    
                    for _, region in risk_regions.iterrows():
                        with st.expander(f"{region['区域']}区域 - 依赖度{region['最大客户依赖度']:.1f}%"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("最大客户", region['最大客户'])
                            with col2:
                                st.metric("依赖度", f"{region['最大客户依赖度']:.1f}%")
                            with col3:
                                st.metric("客户数", f"{region['客户数']}家")
                            
                            # TOP3客户信息
                            if 'TOP3客户' in region:
                                st.markdown("**TOP3客户贡献：**")
                                for i, customer in enumerate(region['TOP3客户']):
                                    st.markdown(f"{i+1}. {customer['name']}: ¥{customer['sales']/10000:.1f}万 ({customer['percentage']:.1f}%)")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        # 目标达成分析
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        
        if EXTRAS_AVAILABLE:
            colored_header(
                label="目标达成情况分析",
                description="监控客户目标完成进度，识别需要支持的客户",
                color_name="green-70"
            )
        
        if 'target' in charts:
            st.plotly_chart(charts['target'], use_container_width=True)
            
            # 达成率分布
            achievement_df = metrics['customer_achievement_details']
            if not achievement_df.empty:
                # 创建达成率分布直方图
                fig_dist = go.Figure()
                fig_dist.add_trace(go.Histogram(
                    x=achievement_df['达成率'],
                    nbinsx=20,
                    name='客户数',
                    marker_color='#667eea',
                    hovertemplate='达成率: %{x:.0f}%<br>客户数: %{y}<extra></extra>'
                ))
                
                fig_dist.add_vline(x=80, line_dash="dash", line_color="red", 
                                  annotation_text="达成线(80%)")
                fig_dist.add_vline(x=100, line_dash="dash", line_color="green", 
                                  annotation_text="目标线(100%)")
                
                fig_dist.update_layout(
                    title="客户目标达成率分布",
                    xaxis_title="达成率(%)",
                    yaxis_title="客户数量",
                    showlegend=False
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab5:
        # 客户价值分析
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        
        if EXTRAS_AVAILABLE:
            colored_header(
                label="RFM客户价值分析",
                description="基于RFM模型的客户价值分层和策略建议",
                color_name="violet-70"
            )
        
        # 客户价值分布
        col1, col2, col3, col4, col5 = st.columns(5)
        
        value_metrics = [
            ("💎 钻石客户", metrics['diamond_customers'], "#e74c3c"),
            ("🥇 黄金客户", metrics['gold_customers'], "#f39c12"),
            ("🥈 白银客户", metrics['silver_customers'], "#95a5a6"),
            ("🌟 潜力客户", metrics['potential_customers'], "#3498db"),
            ("⚠️ 流失风险", metrics['risk_customers'], "#9b59b6")
        ]
        
        for col, (label, value, color) in zip([col1, col2, col3, col4, col5], value_metrics):
            with col:
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: {color}20; border-radius: 10px; border: 2px solid {color};'>
                    <h2 style='color: {color}; margin: 0;'>{value}</h2>
                    <p style='margin: 0; font-weight: 600;'>{label}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 显示RFM 3D散点图
        if 'rfm' in charts:
            st.plotly_chart(charts['rfm'], use_container_width=True)
        
        # 客户策略建议
        st.markdown("""
        <div class='insight-card'>
            <h3>🎯 客户策略建议</h3>
            <ul style='margin: 0; padding-left: 20px;'>
                <li><b>钻石客户：</b>提供VIP服务，建立战略合作关系</li>
                <li><b>黄金客户：</b>增加互动频次，提升为钻石客户</li>
                <li><b>白银客户：</b>定期关怀，推荐新产品提升客单价</li>
                <li><b>潜力客户：</b>精准营销，激发购买潜力</li>
                <li><b>流失风险：</b>立即启动挽回计划，了解流失原因</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.8); margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p>Trolli SAL | 客户依赖分析 | 数据更新时间: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)

# 运行主应用
if __name__ == "__main__":
    main()
