# pages/销售达成分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="销售达成分析 - Trolli SAL",
    page_icon="🎯",
    layout="wide"
)

# 增强的CSS样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
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
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
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
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .metric-sublabel {
        color: #999;
        font-size: 0.8rem;
        margin-top: 0.3rem;
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
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    /* 动画卡片延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
</style>
""", unsafe_allow_html=True)

# 缓存数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 从GitHub根目录加载文件
        tt_city_data = pd.read_excel("TT渠道-城市月度指标.xlsx")
        sales_data = pd.read_excel("TT与MT销售数据.xlsx")
        mt_data = pd.read_excel("MT渠道月度指标.xlsx")
        
        # 数据预处理
        # TT城市数据
        tt_city_data['指标年月'] = pd.to_datetime(tt_city_data['指标年月'])
        tt_city_data['月度指标'] = pd.to_numeric(tt_city_data['月度指标'], errors='coerce').fillna(0)
        tt_city_data['往年同期'] = pd.to_numeric(tt_city_data['往年同期'], errors='coerce').fillna(0)
        
        # 销售数据
        sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])
        sales_data['单价（箱）'] = pd.to_numeric(sales_data['单价（箱）'], errors='coerce').fillna(0)
        sales_data['求和项:数量（箱）'] = pd.to_numeric(sales_data['求和项:数量（箱）'], errors='coerce').fillna(0)
        sales_data['销售额'] = sales_data['单价（箱）'] * sales_data['求和项:数量（箱）']
        
        # 区分渠道类型
        def identify_channel(order_type):
            if pd.isna(order_type):
                return 'Other'
            order_type_str = str(order_type)
            if 'TT' in order_type_str or 'tt' in order_type_str:
                return 'TT'
            elif 'MT' in order_type_str or 'mt' in order_type_str or '正常' in order_type_str:
                return 'MT'
            else:
                return 'Other'
        
        sales_data['渠道类型'] = sales_data['订单类型'].apply(identify_channel)
        
        # MT数据
        mt_data['月份'] = pd.to_datetime(mt_data['月份'])
        mt_data['月度指标'] = pd.to_numeric(mt_data['月度指标'], errors='coerce').fillna(0)
        mt_data['往年同期'] = pd.to_numeric(mt_data['往年同期'], errors='coerce').fillna(0)
        
        return {
            'tt_city_data': tt_city_data,
            'sales_data': sales_data,
            'mt_data': mt_data
        }
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None

# 计算总体指标
def calculate_overview_metrics(data):
    """计算销售达成总览的各项指标"""
    tt_city_data = data['tt_city_data']
    sales_data = data['sales_data']
    mt_data = data['mt_data']
    
    current_year = 2025
    
    # 计算TT渠道指标
    tt_sales = sales_data[
        (sales_data['渠道类型'] == 'TT') & 
        (sales_data['发运月份'].dt.year == current_year)
    ]['销售额'].sum()
    
    tt_target = tt_city_data[
        tt_city_data['指标年月'].dt.year == current_year
    ]['月度指标'].sum()
    
    tt_achievement = (tt_sales / tt_target * 100) if tt_target > 0 else 0
    
    # 计算MT渠道指标
    mt_sales = sales_data[
        (sales_data['渠道类型'] == 'MT') & 
        (sales_data['发运月份'].dt.year == current_year)
    ]['销售额'].sum()
    
    mt_target = mt_data[
        mt_data['月份'].dt.year == current_year
    ]['月度指标'].sum()
    
    mt_achievement = (mt_sales / mt_target * 100) if mt_target > 0 else 0
    
    # 计算总体指标
    total_sales = tt_sales + mt_sales
    total_target = tt_target + mt_target
    total_achievement = (total_sales / total_target * 100) if total_target > 0 else 0
    
    # 计算同比增长
    last_year_sales = sales_data[
        sales_data['发运月份'].dt.year == current_year - 1
    ]['销售额'].sum()
    
    growth_rate = ((total_sales - last_year_sales) / last_year_sales * 100) if last_year_sales > 0 else 0
    
    # 计算城市达成率
    city_achieved = tt_city_data[
        (tt_city_data['指标年月'].dt.year == current_year) &
        (tt_city_data['月度指标'] > 0)
    ].groupby('城市').first()
    
    total_cities = len(city_achieved)
    achieved_cities = len(city_achieved[city_achieved['月度指标'] > 0])
    city_achievement_rate = (achieved_cities / total_cities * 100) if total_cities > 0 else 0
    
    # 计算区域数据
    regions = sales_data['所属区域'].nunique()
    
    return {
        'total_sales': total_sales,
        'total_target': total_target,
        'total_achievement': total_achievement,
        'growth_rate': growth_rate,
        'tt_sales': tt_sales,
        'tt_achievement': tt_achievement,
        'mt_sales': mt_sales,
        'mt_achievement': mt_achievement,
        'city_achievement_rate': city_achievement_rate,
        'regions': regions
    }

# 创建区域销售对比图
def create_regional_comparison_chart(data):
    """创建区域销售额对比图"""
    sales_data = data['sales_data']
    
    # 按区域和渠道汇总
    regional_sales = sales_data.groupby(['所属区域', '渠道类型'])['销售额'].sum().unstack(fill_value=0)
    
    # 计算总销售额并排序
    regional_sales['总计'] = regional_sales.sum(axis=1)
    regional_sales = regional_sales.sort_values('总计', ascending=True)
    
    fig = go.Figure()
    
    # 为每个渠道添加条形图
    colors = {'TT': '#667eea', 'MT': '#764ba2', 'Other': '#999999'}
    
    for channel in ['MT', 'TT']:
        if channel in regional_sales.columns:
            fig.add_trace(go.Bar(
                name=f"{channel}渠道",
                y=regional_sales.index,
                x=regional_sales[channel],
                orientation='h',
                marker_color=colors.get(channel, '#999999'),
                text=[f"¥{val/10000:.0f}万" for val in regional_sales[channel]],
                textposition='inside',
                textfont=dict(color='white', size=12, weight='bold'),
                hovertemplate=f'<b>{channel}渠道</b><br>' +
                             '区域: %{y}<br>' +
                             '销售额: ¥%{x:,.0f}<br>' +
                             '<extra></extra>'
            ))
    
    # 添加总销售额标注
    for idx, (region, total) in enumerate(zip(regional_sales.index, regional_sales['总计'])):
        fig.add_annotation(
            x=total,
            y=idx,
            text=f"¥{total/10000:.0f}万",
            xanchor='left',
            xshift=10,
            font=dict(size=14, weight='bold', color='#333'),
            showarrow=False
        )
    
    fig.update_layout(
        title={
            'text': "各区域渠道销售额构成分析",
            'font': {'size': 20, 'weight': 'bold'}
        },
        xaxis_title="销售额",
        yaxis_title="",
        barmode='stack',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            tickformat=',.0f'
        ),
        yaxis=dict(
            showgrid=False
        ),
        plot_bgcolor='white',
        hovermode='y unified'
    )
    
    return fig

# 创建月度趋势分析图
def create_monthly_trend_analysis(data):
    """创建月度销售趋势分析图"""
    sales_data = data['sales_data']
    tt_city_data = data['tt_city_data']
    mt_data = data['mt_data']
    
    # 计算实际销售趋势
    monthly_sales = sales_data.groupby([
        sales_data['发运月份'].dt.to_period('M'),
        '渠道类型'
    ])['销售额'].sum().reset_index()
    
    monthly_sales['发运月份'] = monthly_sales['发运月份'].astype(str)
    
    # 计算目标趋势
    tt_monthly_target = tt_city_data.groupby(
        tt_city_data['指标年月'].dt.to_period('M')
    )['月度指标'].sum().reset_index()
    tt_monthly_target['指标年月'] = tt_monthly_target['指标年月'].astype(str)
    
    mt_monthly_target = mt_data.groupby(
        mt_data['月份'].dt.to_period('M')
    )['月度指标'].sum().reset_index()
    mt_monthly_target['月份'] = mt_monthly_target['月份'].astype(str)
    
    fig = go.Figure()
    
    # 添加实际销售趋势线
    for channel, color in [('TT', '#667eea'), ('MT', '#764ba2')]:
        channel_data = monthly_sales[monthly_sales['渠道类型'] == channel]
        
        fig.add_trace(go.Scatter(
            x=channel_data['发运月份'],
            y=channel_data['销售额'],
            name=f"{channel}实际",
            mode='lines+markers',
            line=dict(width=3, color=color),
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '月份: %{x}<br>' +
                         '销售额: ¥%{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
    
    # 添加目标线
    fig.add_trace(go.Scatter(
        x=tt_monthly_target['指标年月'],
        y=tt_monthly_target['月度指标'],
        name='TT目标',
        mode='lines',
        line=dict(width=2, color='#667eea', dash='dash'),
        opacity=0.6,
        hovertemplate='<b>TT目标</b><br>' +
                     '月份: %{x}<br>' +
                     '目标额: ¥%{y:,.0f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=mt_monthly_target['月份'],
        y=mt_monthly_target['月度指标'],
        name='MT目标',
        mode='lines',
        line=dict(width=2, color='#764ba2', dash='dash'),
        opacity=0.6,
        hovertemplate='<b>MT目标</b><br>' +
                     '月份: %{x}<br>' +
                     '目标额: ¥%{y:,.0f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "销售额月度趋势对比分析",
            'font': {'size': 20, 'weight': 'bold'}
        },
        xaxis_title="月份",
        yaxis_title="销售额",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            tickformat=',.0f'
        ),
        plot_bgcolor='white'
    )
    
    return fig

# 创建客户贡献分析
def create_customer_contribution_analysis(data):
    """创建客户贡献分析图表"""
    sales_data = data['sales_data']
    
    # 计算客户销售额
    customer_sales = sales_data.groupby('客户简称')['销售额'].sum().sort_values(ascending=False)
    
    # 计算累计贡献率
    total_sales = customer_sales.sum()
    customer_contribution = pd.DataFrame({
        '客户': customer_sales.index,
        '销售额': customer_sales.values,
        '贡献率': (customer_sales.values / total_sales * 100)
    })
    customer_contribution['累计贡献率'] = customer_contribution['贡献率'].cumsum()
    
    # 找出80%贡献的客户数
    customers_80 = len(customer_contribution[customer_contribution['累计贡献率'] <= 80])
    
    # 只显示前20个客户
    top_customers = customer_contribution.head(20)
    
    fig = go.Figure()
    
    # 添加柱状图
    fig.add_trace(go.Bar(
        x=top_customers['客户'],
        y=top_customers['销售额'],
        name='销售额',
        marker_color='#667eea',
        yaxis='y',
        text=[f"¥{val/10000:.0f}万" for val in top_customers['销售额']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                     '销售额: ¥%{y:,.0f}<br>' +
                     '贡献率: %{customdata:.1f}%<br>' +
                     '<extra></extra>',
        customdata=top_customers['贡献率']
    ))
    
    # 添加累计贡献率曲线
    fig.add_trace(go.Scatter(
        x=top_customers['客户'],
        y=top_customers['累计贡献率'],
        name='累计贡献率',
        mode='lines+markers',
        line=dict(color='#f59e0b', width=3),
        marker=dict(size=8),
        yaxis='y2',
        hovertemplate='<b>累计贡献率</b><br>' +
                     '客户: %{x}<br>' +
                     '累计贡献: %{y:.1f}%<br>' +
                     '<extra></extra>'
    ))
    
    # 添加80%贡献线
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="red",
        yref='y2',
        annotation_text=f"80%贡献线 (前{customers_80}个客户)",
        annotation_position="left"
    )
    
    fig.update_layout(
        title={
            'text': f"客户贡献度分析 (Top 20) - 前{customers_80}个客户贡献80%销售额",
            'font': {'size': 20, 'weight': 'bold'}
        },
        xaxis_title="客户名称",
        yaxis=dict(
            title="销售额",
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            tickformat=',.0f'
        ),
        yaxis2=dict(
            title="累计贡献率 (%)",
            overlaying='y',
            side='right',
            range=[0, 100],
            showgrid=False
        ),
        height=600,
        hovermode='x unified',
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        bargap=0.2
    )
    
    return fig, customers_80, len(customer_sales)

# 创建渠道达成分析仪表盘
def create_channel_achievement_dashboard(data):
    """创建渠道达成分析仪表盘"""
    metrics = calculate_overview_metrics(data)
    
    # 创建仪表盘
    fig = go.Figure()
    
    # TT渠道仪表盘
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['tt_achievement'],
        domain={'x': [0, 0.45], 'y': [0, 1]},
        title={'text': "TT渠道达成率", 'font': {'size': 20}},
        delta={'reference': 100, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 150], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 80], 'color': '#fff3e0'},
                {'range': [80, 100], 'color': '#e8f5e9'},
                {'range': [100, 150], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    # MT渠道仪表盘
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['mt_achievement'],
        domain={'x': [0.55, 1], 'y': [0, 1]},
        title={'text': "MT渠道达成率", 'font': {'size': 20}},
        delta={'reference': 100, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 150], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#764ba2"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 80], 'color': '#fff3e0'},
                {'range': [80, 100], 'color': '#e8f5e9'},
                {'range': [100, 150], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# 主页面
def main():
    # 检查认证状态
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("🚫 请先登录系统")
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-weight: 800;">
                📊 Trolli SAL
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 主要功能
        st.markdown("#### 🏠 主要功能")
        
        if st.button("🏠 欢迎页面", use_container_width=True):
            st.switch_page("登陆界面haha.py")
        
        st.markdown("---")
        
        # 分析模块
        st.markdown("#### 📈 分析模块")
        
        if st.button("📦 产品组合分析", use_container_width=True):
            st.switch_page("pages/产品组合分析.py")
        
        if st.button("📊 预测库存分析", use_container_width=True):
            st.switch_page("pages/预测库存分析.py")
        
        if st.button("👥 客户依赖分析", use_container_width=True):
            st.switch_page("pages/客户依赖分析.py")
        
        if st.button("🎯 销售达成分析", use_container_width=True, type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # 用户信息
        st.markdown("#### 👤 用户信息")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                    border: 1px solid rgba(102,126,234,0.3); 
                    border-radius: 10px; 
                    padding: 1rem; 
                    margin: 0.5rem 0;">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.3rem;">当前用户</div>
            <div style="font-size: 1.1rem; font-weight: bold; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;">
                管理员 cira
            </div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">
                ✅ 已认证
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 退出登录按钮
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.switch_page("登陆界面haha.py")
    
    # 主页面内容
    st.markdown("""
    <div class="main-header">
        <h1>🎯 销售达成分析</h1>
        <p>全渠道销售业绩综合分析系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    data = load_data()
    if data is None:
        return
    
    # 计算总体指标
    metrics = calculate_overview_metrics(data)
    
    # 创建标签页
    tab_names = [
        "📊 销售达成总览",
        "🏪 MT渠道分析",
        "🏢 TT渠道分析",
        "📊 全渠道分析",
        "📈 趋势洞察",
        "👥 客户贡献分析"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 销售达成总览 - 只显示指标卡片
    with tabs[0]:
        # 第一行指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['total_sales']/10000:.0f}万</div>
                <div class="metric-label">💰 2025年总销售额</div>
                <div class="metric-sublabel">MT+TT全渠道</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            achievement_color = "#10b981" if metrics['total_achievement'] >= 100 else "#f59e0b"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {achievement_color}">{metrics['total_achievement']:.1f}%</div>
                <div class="metric-label">🎯 总体达成率</div>
                <div class="metric-sublabel">目标: ¥{metrics['total_target']/10000:.0f}万</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            growth_color = "#10b981" if metrics['growth_rate'] > 0 else "#ef4444"
            growth_icon = "↗" if metrics['growth_rate'] > 0 else "↘"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {growth_color}">{growth_icon} {abs(metrics['growth_rate']):.1f}%</div>
                <div class="metric-label">📈 同比增长率</div>
                <div class="metric-sublabel">vs 2024年</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['city_achievement_rate']:.1f}%</div>
                <div class="metric-label">🏙️ 城市达成率</div>
                <div class="metric-sublabel">TT渠道覆盖</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第二行指标卡片
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['tt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏢 TT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['tt_achievement']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['mt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏪 MT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['mt_achievement']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            tt_ratio = (metrics['tt_sales'] / metrics['total_sales'] * 100) if metrics['total_sales'] > 0 else 0
            mt_ratio = 100 - tt_ratio
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{tt_ratio:.1f}% / {mt_ratio:.1f}%</div>
                <div class="metric-label">📊 渠道销售占比</div>
                <div class="metric-sublabel">TT / MT</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['regions']}</div>
                <div class="metric-label">🗺️ 覆盖区域数</div>
                <div class="metric-sublabel">全国布局</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 2: MT渠道分析
    with tabs[1]:
        st.markdown("### 🏪 MT渠道深度分析")
        
        # MT渠道达成率仪表盘
        gauge_fig = create_channel_achievement_dashboard(data)
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # 只显示MT部分的仪表盘
            mt_gauge = go.Figure()
            mt_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['mt_achievement'],
                title={'text': "MT渠道达成率", 'font': {'size': 24}},
                delta={'reference': 100, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 150], 'tickwidth': 1},
                    'bar': {'color': "#764ba2"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 80], 'color': '#fff3e0'},
                        {'range': [80, 100], 'color': '#e8f5e9'},
                        {'range': [100, 150], 'color': '#c8e6c9'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            mt_gauge.update_layout(height=300)
            st.plotly_chart(mt_gauge, use_container_width=True)
        
        with col2:
            # MT渠道关键指标
            st.info(f"""
            **MT渠道关键指标**
            - 销售额: ¥{metrics['mt_sales']/10000:.0f}万
            - 目标额: ¥{metrics['mt_target']/10000:.0f}万  
            - 达成率: {metrics['mt_achievement']:.1f}%
            - 渠道占比: {(metrics['mt_sales'] / metrics['total_sales'] * 100):.1f}%
            
            **分析洞察**
            - {'✅ 超额完成目标' if metrics['mt_achievement'] >= 100 else '⚠️ 未达成目标'}
            - {'📈 渠道表现优秀' if metrics['mt_achievement'] >= 120 else '📊 渠道表现正常' if metrics['mt_achievement'] >= 80 else '📉 需要改进'}
            """)
    
    # Tab 3: TT渠道分析
    with tabs[2]:
        st.markdown("### 🏢 TT渠道深度分析")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # TT渠道达成率仪表盘
            tt_gauge = go.Figure()
            tt_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['tt_achievement'],
                title={'text': "TT渠道达成率", 'font': {'size': 24}},
                delta={'reference': 100, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 150], 'tickwidth': 1},
                    'bar': {'color': "#667eea"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 80], 'color': '#fff3e0'},
                        {'range': [80, 100], 'color': '#e8f5e9'},
                        {'range': [100, 150], 'color': '#c8e6c9'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            tt_gauge.update_layout(height=300)
            st.plotly_chart(tt_gauge, use_container_width=True)
        
        with col2:
            # TT渠道关键指标
            st.info(f"""
            **TT渠道关键指标**
            - 销售额: ¥{metrics['tt_sales']/10000:.0f}万
            - 目标额: ¥{metrics['tt_target']/10000:.0f}万  
            - 达成率: {metrics['tt_achievement']:.1f}%
            - 渠道占比: {(metrics['tt_sales'] / metrics['total_sales'] * 100):.1f}%
            
            **分析洞察**
            - {'✅ 超额完成目标' if metrics['tt_achievement'] >= 100 else '⚠️ 未达成目标'}
            - {'📈 渠道表现优秀' if metrics['tt_achievement'] >= 120 else '📊 渠道表现正常' if metrics['tt_achievement'] >= 80 else '📉 需要改进'}
            """)
    
    # Tab 4: 全渠道分析
    with tabs[3]:
        st.markdown("### 📊 全渠道综合分析")
        
        # 区域销售对比图
        regional_fig = create_regional_comparison_chart(data)
        st.plotly_chart(regional_fig, use_container_width=True)
        
        # 渠道对比洞察
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("""
            **🏆 表现最佳区域**
            - 基于总销售额排名
            - 识别重点市场
            - 资源分配参考
            """)
        
        with col2:
            st.info("""
            **📊 渠道结构分析**
            - MT/TT渠道占比
            - 区域渠道偏好
            - 发展机会识别
            """)
        
        with col3:
            st.warning("""
            **🎯 改进建议**
            - 低销售区域关注
            - 渠道平衡优化
            - 资源调配建议
            """)
    
    # Tab 5: 趋势洞察
    with tabs[4]:
        st.markdown("### 📈 销售趋势洞察分析")
        
        # 月度趋势图
        monthly_trend_fig = create_monthly_trend_analysis(data)
        st.plotly_chart(monthly_trend_fig, use_container_width=True)
        
        # 趋势分析洞察
        st.markdown("### 📊 趋势分析关键发现")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📈 增长趋势**
            - 实线：实际销售额
            - 虚线：目标销售额
            - 对比分析达成情况
            """)
        
        with col2:
            st.success("""
            **🎯 目标达成**
            - 月度达成率追踪
            - 渠道表现对比
            - 趋势预测参考
            """)
    
    # Tab 6: 客户贡献分析
    with tabs[5]:
        st.markdown("### 👥 客户贡献分析")
        
        # 客户贡献分析图
        customer_fig, customers_80, total_customers = create_customer_contribution_analysis(data)
        st.plotly_chart(customer_fig, use_container_width=True)
        
        # 客户分析洞察
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "贡献80%销售的客户数",
                f"{customers_80}个",
                f"占比 {customers_80/total_customers*100:.1f}%"
            )
        
        with col2:
            st.metric(
                "总客户数",
                f"{total_customers}个",
                "活跃客户"
            )
        
        with col3:
            concentration = customers_80/total_customers*100
            risk_level = "高" if concentration < 20 else "中" if concentration < 40 else "低"
            risk_color = "#ef4444" if risk_level == "高" else "#f59e0b" if risk_level == "中" else "#10b981"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.8); border-radius: 10px;">
                <h3 style="margin: 0; color: {risk_color};">客户集中度风险</h3>
                <h1 style="margin: 0.5rem 0; color: {risk_color};">{risk_level}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # 客户管理建议
        st.markdown("### 🎯 客户管理策略建议")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **核心客户维护**
            - 定期拜访Top 20客户
            - 制定专属服务方案
            - 建立长期合作关系
            - 优先保障供货
            """)
        
        with col2:
            st.info("""
            **客户开发策略**
            - 降低客户集中度风险
            - 开发潜力客户
            - 区域市场拓展
            - 新渠道客户开发
            """)

if __name__ == "__main__":
    main()
