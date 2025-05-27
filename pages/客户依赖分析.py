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
    
    /* 指标卡片样式 - 统一风格 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: cardFadeIn 0.6s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        animation: numberCount 1.5s ease-out;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
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
    
    /* 图表容器 - 增强动画 */
    .plot-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
        animation: slideUp 0.6s ease-out;
    }
    
    .plot-container:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
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
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
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
        font-size: 2.5rem;
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
        'customer_achievement_details': pd.DataFrame(customer_achievement_details) if customer_achievement_details else pd.DataFrame()
    }

# 创建高级可视化图表
def create_advanced_charts(metrics, sales_data, monthly_data):
    """创建高级交互式图表"""
    charts = {}
    
    # 1. 客户健康状态雷达图（替代仪表盘）
    categories = ['健康度', '目标达成', '价值贡献', '活跃度', '稳定性']
    
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100,
        (100 - metrics['max_dependency'])
    ]
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='当前状态',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2),
        hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
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
                ticksuffix='%'
            )
        ),
        showlegend=True,
        title="客户健康状态综合评估",
        height=450
    )
    
    charts['health_radar'] = fig_radar
    
    # 2. 3D区域风险热力图
    if not metrics['region_stats'].empty:
        regions = metrics['region_stats']['区域'].tolist()
        dependencies = metrics['region_stats']['最大客户依赖度'].tolist()
        sales = metrics['region_stats']['总销售额'].tolist()
        customers = metrics['region_stats']['客户数'].tolist()
        
        # 创建3D散点图
        fig_3d = go.Figure()
        
        fig_3d.add_trace(go.Scatter3d(
            x=customers,
            y=[s/10000 for s in sales],
            z=dependencies,
            mode='markers+text',
            text=regions,
            marker=dict(
                size=[d/2 for d in dependencies],
                color=dependencies,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="依赖度%", x=1.02),
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>' +
                         '客户数: %{x}<br>' +
                         '销售额: %{y:.1f}万<br>' +
                         '依赖度: %{z:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        fig_3d.update_layout(
            scene=dict(
                xaxis_title="客户数量",
                yaxis_title="销售额（万元）",
                zaxis_title="客户依赖度（%）",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            title="区域风险三维分布图",
            height=600
        )
        
        charts['risk_3d'] = fig_3d
    
    # 3. 客户价值流动桑基图
    if not metrics['rfm_df'].empty:
        # 准备桑基图数据
        source = []
        target = []
        value = []
        labels = ['所有客户', '钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']
        
        # 客户类型分布
        customer_types = ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']
        for i, ct in enumerate(customer_types):
            count = len(metrics['rfm_df'][metrics['rfm_df']['类型'] == ct])
            if count > 0:
                source.append(0)
                target.append(i + 1)
                value.append(count)
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=["#667eea", "#e74c3c", "#f39c12", "#95a5a6", "#3498db", "#9b59b6"],
                hovertemplate='%{label}<br>客户数: %{value}<extra></extra>'
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(102, 126, 234, 0.3)'
            )
        )])
        
        fig_sankey.update_layout(
            title="客户价值流向分析",
            height=400
        )
        
        charts['sankey'] = fig_sankey
    
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
            title="销售趋势双轴分析",
            height=400,
            hovermode='x unified'
        )
        
        charts['trend'] = fig_trend
    
    # 5. 客户贡献度旭日图
    if not metrics['rfm_df'].empty:
        # 准备旭日图数据
        sunburst_data = []
        
        # 按客户类型分组
        for customer_type in ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']:
            type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
            
            if not type_customers.empty:
                # 添加类型节点
                sunburst_data.append({
                    'labels': customer_type,
                    'parents': '',
                    'values': type_customers['M'].sum()
                })
                
                # 添加前5个客户
                top_customers = type_customers.nlargest(5, 'M')
                for _, customer in top_customers.iterrows():
                    sunburst_data.append({
                        'labels': customer['客户'][:10],
                        'parents': customer_type,
                        'values': customer['M']
                    })
        
        if sunburst_data:
            df_sunburst = pd.DataFrame(sunburst_data)
            
            fig_sunburst = go.Figure(go.Sunburst(
                labels=df_sunburst['labels'],
                parents=df_sunburst['parents'],
                values=df_sunburst['values'],
                branchvalues="total",
                marker=dict(
                    colorscale='Viridis',
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.0f}<br>占比: %{percentRoot}<extra></extra>'
            ))
            
            fig_sunburst.update_layout(
                title="客户贡献度层级分析",
                height=500
            )
            
            charts['sunburst'] = fig_sunburst
    
    return charts

# 主应用逻辑
def main():
    # 侧边栏返回按钮
    with st.sidebar:
        if st.button("🏠 返回主页", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.switch_page("app.py")
    
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
    
    # 关键指标展示 - 使用metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value data-point">{metrics['normal_rate']:.1f}%</div>
            <div class="metric-label">❤️ 客户健康度</div>
            <small style="color: #888;">正常客户 {metrics['normal_customers']} 家</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value data-point" style="color: {'#ff6b6b' if metrics['max_dependency'] > 30 else '#667eea'};">
                {metrics['max_dependency']:.1f}%
            </div>
            <div class="metric-label">⚠️ 最高依赖风险</div>
            <small style="color: #888;">{metrics['max_dependency_region']} 区域</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value data-point">{metrics['target_achievement_rate']:.1f}%</div>
            <div class="metric-label">🎯 目标达成率</div>
            <small style="color: #888;">达成 {metrics['achieved_customers']} 家</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value data-point">{metrics['high_value_rate']:.1f}%</div>
            <div class="metric-label">💎 高价值客户</div>
            <small style="color: #888;">钻石+黄金 {metrics['diamond_customers']+metrics['gold_customers']} 家</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 创建标签页
    tabs = st.tabs([
        "📊 总览分析", 
        "⚠️ 风险评估", 
        "💎 价值分层", 
        "🎯 目标跟踪",
        "📈 趋势洞察"
    ])
    
    with tabs[0]:
        # 总览分析
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        # 雷达图
        st.plotly_chart(charts['health_radar'], use_container_width=True, key="overview_radar")
        
        # 核心洞察
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='insight-card'>
                <h4>💡 健康诊断</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>客户健康度{0}，{1}%的客户保持正常运营</li>
                    <li>同比增长{2}%，业务发展{3}</li>
                    <li>平均客户贡献¥{4:.0f}</li>
                </ul>
            </div>
            """.format(
                '良好' if metrics['normal_rate'] > 85 else '一般',
                metrics['normal_rate'],
                f"{metrics['growth_rate']:+.1f}",
                '稳健' if metrics['growth_rate'] > 0 else '需关注',
                metrics['avg_customer_contribution']
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='insight-card'>
                <h4>🎯 行动建议</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>重点关注{0}区域的客户集中度风险</li>
                    <li>激活{1}家潜力客户，提升客户价值</li>
                    <li>及时干预{2}家流失风险客户</li>
                </ul>
            </div>
            """.format(
                metrics['max_dependency_region'],
                metrics['potential_customers'],
                metrics['risk_customers']
            ), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[1]:
        # 风险评估
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        if 'risk_3d' in charts:
            st.plotly_chart(charts['risk_3d'], use_container_width=True, key="risk_3d_chart")
            
            # 风险详情
            if not metrics['region_stats'].empty:
                risk_regions = metrics['region_stats'][
                    metrics['region_stats']['最大客户依赖度'] > 30
                ].sort_values('最大客户依赖度', ascending=False)
                
                if not risk_regions.empty:
                    st.warning(f"⚠️ 发现 {len(risk_regions)} 个高风险区域")
                    
                    for _, region in risk_regions.iterrows():
                        with st.expander(f"🔍 {region['区域']}区域 - 依赖度 {region['最大客户依赖度']:.1f}%"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("最大客户", region['最大客户'])
                            with col2:
                                st.metric("客户贡献", f"¥{region['最大客户销售额']/10000:.1f}万")
                            with col3:
                                st.metric("区域客户数", f"{region['客户数']}家")
                            
                            # TOP3客户贡献图
                            if 'TOP3客户' in region and region['TOP3客户']:
                                top3_names = [c['name'] for c in region['TOP3客户']]
                                top3_values = [c['percentage'] for c in region['TOP3客户']]
                                
                                fig_top3 = go.Figure(go.Bar(
                                    x=top3_values,
                                    y=top3_names,
                                    orientation='h',
                                    marker_color='#667eea',
                                    text=[f"{v:.1f}%" for v in top3_values],
                                    textposition='outside'
                                ))
                                
                                fig_top3.update_layout(
                                    title="TOP3客户贡献占比",
                                    xaxis_title="占比(%)",
                                    height=200,
                                    margin=dict(l=0, r=0, t=30, b=0)
                                )
                                
                                st.plotly_chart(fig_top3, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[2]:
        # 价值分层
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        # 客户价值分布
        col1, col2, col3, col4, col5 = st.columns(5)
        
        value_cards = [
            (col1, "💎 钻石", metrics['diamond_customers'], "#e74c3c"),
            (col2, "🥇 黄金", metrics['gold_customers'], "#f39c12"),
            (col3, "🥈 白银", metrics['silver_customers'], "#95a5a6"),
            (col4, "🌟 潜力", metrics['potential_customers'], "#3498db"),
            (col5, "⚠️ 流失", metrics['risk_customers'], "#9b59b6")
        ]
        
        for col, label, value, color in value_cards:
            with col:
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: {color}; color: white; border-radius: 10px;'>
                    <h2 style='margin: 0;'>{value}</h2>
                    <p style='margin: 0;'>{label}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 桑基图和旭日图
        if 'sankey' in charts:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.plotly_chart(charts['sankey'], use_container_width=True, key="value_sankey")
            
            with col2:
                if 'sunburst' in charts:
                    st.plotly_chart(charts['sunburst'], use_container_width=True, key="value_sunburst")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[3]:
        # 目标跟踪
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        if not metrics['customer_achievement_details'].empty:
            # 创建目标达成散点图
            achievement_df = metrics['customer_achievement_details']
            
            fig_scatter = go.Figure()
            
            # 添加散点
            fig_scatter.add_trace(go.Scatter(
                x=achievement_df['目标'],
                y=achievement_df['实际'],
                mode='markers',
                marker=dict(
                    size=achievement_df['达成率'].apply(lambda x: min(max(x/5, 10), 50)),
                    color=achievement_df['达成率'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="达成率%"),
                    line=dict(width=1, color='white')
                ),
                text=achievement_df['客户'],
                hovertemplate='<b>%{text}</b><br>目标: ¥%{x:,.0f}<br>实际: ¥%{y:,.0f}<br><extra></extra>'
            ))
            
            # 添加目标线
            max_val = max(achievement_df['目标'].max(), achievement_df['实际'].max())
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='目标线',
                line=dict(color='red', dash='dash'),
                showlegend=True
            ))
            
            # 添加80%达成线
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val * 0.8],
                mode='lines',
                name='80%达成线',
                line=dict(color='orange', dash='dot'),
                showlegend=True
            ))
            
            fig_scatter.update_layout(
                title="客户目标达成分布",
                xaxis_title="目标金额",
                yaxis_title="实际金额",
                height=500
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True, key="target_scatter")
            
            # 达成率分布
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(
                    x=achievement_df['达成率'],
                    nbinsx=20,
                    marker_color='#667eea',
                    name='客户数'
                ))
                
                fig_hist.add_vline(x=80, line_dash="dash", line_color="red", 
                                  annotation_text="达成线")
                fig_hist.add_vline(x=100, line_dash="dash", line_color="green", 
                                  annotation_text="目标线")
                
                fig_hist.update_layout(
                    title="达成率分布直方图",
                    xaxis_title="达成率(%)",
                    yaxis_title="客户数量",
                    height=300
                )
                
                st.plotly_chart(fig_hist, use_container_width=True, key="achievement_hist")
            
            with col2:
                # 达成情况统计
                achieved = len(achievement_df[achievement_df['达成率'] >= 80])
                excellent = len(achievement_df[achievement_df['达成率'] >= 100])
                poor = len(achievement_df[achievement_df['达成率'] < 50])
                
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px;'>
                    <h4>📊 达成统计</h4>
                    <p>✅ 达成(≥80%): <b>{achieved}</b>家</p>
                    <p>🌟 超额(≥100%): <b>{excellent}</b>家</p>
                    <p>⚠️ 落后(<50%): <b>{poor}</b>家</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[4]:
        # 趋势洞察
        st.markdown("<div class='advanced-card'>", unsafe_allow_html=True)
        
        if 'trend' in charts:
            st.plotly_chart(charts['trend'], use_container_width=True, key="trend_analysis")
        
        # 趋势预测和洞察
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='insight-card'>
                <h4>📊 趋势特征</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>销售额月度波动呈现季节性特征</li>
                    <li>Q2通常为销售高峰期</li>
                    <li>年末存在冲刺效应</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='insight-card'>
                <h4>🔮 预测建议</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>提前为旺季储备库存</li>
                    <li>淡季加强客户维护</li>
                    <li>制定差异化季节策略</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #e0e0e0;'>
        <p>Trolli SAL | 客户依赖分析 | 数据更新时间: {}</p>
        <p style='font-size: 0.9rem; opacity: 0.8;'>让数据洞察更有价值</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)

# 运行主应用
if __name__ == "__main__":
    main()
