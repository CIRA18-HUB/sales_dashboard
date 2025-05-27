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
    
    /* 分析卡片样式 */
    .analysis-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .analysis-card h4 {
        margin-top: 0;
        color: #333;
    }
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
        'tt_target': tt_target,
        'tt_achievement': tt_achievement,
        'mt_sales': mt_sales,
        'mt_target': mt_target,
        'mt_achievement': mt_achievement,
        'city_achievement_rate': city_achievement_rate,
        'regions': regions
    }

# 创建综合销售指标分析图（添加渠道参数）
def create_comprehensive_sales_analysis(data, focus_channel=None):
    """创建综合销售指标分析图（季度和月度）"""
    sales_data = data['sales_data']
    tt_city_data = data['tt_city_data']
    mt_data = data['mt_data']
    
    # 准备数据
    current_year = 2025
    
    # 计算月度数据
    monthly_data = []
    
    for month in range(1, 13):
        month_start = pd.Timestamp(f'{current_year}-{month:02d}-01')
        month_end = month_start + pd.offsets.MonthEnd(0)
        
        # 计算TT渠道月度数据
        tt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'TT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        tt_month_target = tt_city_data[
            (tt_city_data['指标年月'] >= month_start) & 
            (tt_city_data['指标年月'] <= month_end)
        ]['月度指标'].sum()
        
        # 计算MT渠道月度数据
        mt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'MT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        mt_month_target = mt_data[
            (mt_data['月份'] >= month_start) & 
            (mt_data['月份'] <= month_end)
        ]['月度指标'].sum()
        
        monthly_data.append({
            '时间': f'{current_year}-{month:02d}',
            '季度': f'Q{(month-1)//3 + 1}',
            'TT销售额': tt_month_sales,
            'TT目标额': tt_month_target,
            'TT达成率': (tt_month_sales / tt_month_target * 100) if tt_month_target > 0 else 0,
            'MT销售额': mt_month_sales,
            'MT目标额': mt_month_target,
            'MT达成率': (mt_month_sales / mt_month_target * 100) if mt_month_target > 0 else 0,
            '总销售额': tt_month_sales + mt_month_sales,
            '总目标额': tt_month_target + mt_month_target,
            '总达成率': ((tt_month_sales + mt_month_sales) / (tt_month_target + mt_month_target) * 100) 
                      if (tt_month_target + mt_month_target) > 0 else 0
        })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # 创建子图
    from plotly.subplots import make_subplots
    
    # 根据聚焦渠道调整标题
    if focus_channel == 'MT':
        main_title = "MT渠道销售指标综合分析仪表板"
    elif focus_channel == 'TT':
        main_title = "TT渠道销售指标综合分析仪表板"
    else:
        main_title = "销售指标综合分析仪表板"
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('销售额月度趋势', '达成率月度趋势', 
                       '季度销售额对比', '季度达成率分析'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 1. 销售额月度趋势（左上）
    if focus_channel != 'TT':
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['MT销售额'],
                name='MT销售额',
                mode='lines+markers',
                line=dict(color='#764ba2', width=3),
                marker=dict(size=8),
                hovertemplate='%{y:,.0f}万<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )
    
    if focus_channel != 'MT':
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['TT销售额'],
                name='TT销售额',
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                hovertemplate='%{y:,.0f}万<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )
    
    if not focus_channel:
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['总销售额'],
                name='总销售额',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=4, dash='dash'),
                marker=dict(size=10),
                hovertemplate='%{y:,.0f}万<extra></extra>'
            ),
            row=1, col=1, secondary_y=True
        )
    
    # 2. 达成率月度趋势（右上）
    if focus_channel != 'TT':
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['MT达成率'],
                name='MT达成率',
                mode='lines+markers+text',
                line=dict(color='#764ba2', width=3),
                marker=dict(size=10),
                text=[f'{v:.0f}%' for v in df_monthly['MT达成率']],
                textposition='bottom center',
                textfont=dict(size=10),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
    
    if focus_channel != 'MT':
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['TT达成率'],
                name='TT达成率',
                mode='lines+markers+text',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10),
                text=[f'{v:.0f}%' for v in df_monthly['TT达成率']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
    
    if not focus_channel:
        fig.add_trace(
            go.Scatter(
                x=df_monthly['时间'],
                y=df_monthly['总达成率'],
                name='总达成率',
                mode='lines+markers',
                line=dict(color='#10b981', width=4),
                marker=dict(size=12, symbol='diamond'),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
    
    # 添加100%参考线
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="目标线", row=1, col=2)
    
    # 3. 季度销售额对比（左下）
    quarterly_data = df_monthly.groupby('季度').agg({
        'TT销售额': 'sum',
        'MT销售额': 'sum',
        '总销售额': 'sum'
    }).reset_index()
    
    if focus_channel != 'TT':
        fig.add_trace(
            go.Bar(
                x=quarterly_data['季度'],
                y=quarterly_data['MT销售额'],
                name='MT销售额',
                marker_color='#764ba2',
                text=[f'{v/10000:.0f}万' for v in quarterly_data['MT销售额']],
                textposition='inside',
                hovertemplate='%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    if focus_channel != 'MT':
        fig.add_trace(
            go.Bar(
                x=quarterly_data['季度'],
                y=quarterly_data['TT销售额'],
                name='TT销售额',
                marker_color='#667eea',
                text=[f'{v/10000:.0f}万' for v in quarterly_data['TT销售额']],
                textposition='inside',
                hovertemplate='%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 4. 季度达成率分析（右下）
    quarterly_achievement = df_monthly.groupby('季度').agg({
        'TT销售额': 'sum',
        'TT目标额': 'sum',
        'MT销售额': 'sum',
        'MT目标额': 'sum',
        '总销售额': 'sum',
        '总目标额': 'sum'
    })
    
    quarterly_achievement['TT达成率'] = (quarterly_achievement['TT销售额'] / 
                                       quarterly_achievement['TT目标额'] * 100)
    quarterly_achievement['MT达成率'] = (quarterly_achievement['MT销售额'] / 
                                       quarterly_achievement['MT目标额'] * 100)
    quarterly_achievement['总达成率'] = (quarterly_achievement['总销售额'] / 
                                      quarterly_achievement['总目标额'] * 100)
    
    if focus_channel != 'TT':
        fig.add_trace(
            go.Scatter(
                x=quarterly_achievement.index,
                y=quarterly_achievement['MT达成率'],
                name='MT达成率',
                mode='lines+markers+text',
                line=dict(color='#764ba2', width=4),
                marker=dict(size=15),
                text=[f'{v:.0f}%' for v in quarterly_achievement['MT达成率']],
                textposition='bottom center',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=2, col=2
        )
    
    if focus_channel != 'MT':
        fig.add_trace(
            go.Scatter(
                x=quarterly_achievement.index,
                y=quarterly_achievement['TT达成率'],
                name='TT达成率',
                mode='lines+markers+text',
                line=dict(color='#667eea', width=4),
                marker=dict(size=15),
                text=[f'{v:.0f}%' for v in quarterly_achievement['TT达成率']],
                textposition='top center',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=2, col=2
        )
    
    if not focus_channel:
        fig.add_trace(
            go.Scatter(
                x=quarterly_achievement.index,
                y=quarterly_achievement['总达成率'],
                name='总达成率',
                mode='lines+markers+text',
                line=dict(color='#10b981', width=5),
                marker=dict(size=20, symbol='star'),
                text=[f'{v:.0f}%' for v in quarterly_achievement['总达成率']],
                textposition='middle right',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ),
            row=2, col=2
        )
    
    # 添加100%参考线
    fig.add_hline(y=100, line_dash="dash", line_color="red", row=2, col=2)
    
    # 更新布局
    fig.update_xaxes(title_text="月份", row=1, col=1)
    fig.update_xaxes(title_text="月份", row=1, col=2)
    fig.update_xaxes(title_text="季度", row=2, col=1)
    fig.update_xaxes(title_text="季度", row=2, col=2)
    
    fig.update_yaxes(title_text="销售额", row=1, col=1, secondary_y=False)
    if not focus_channel:
        fig.update_yaxes(title_text="总销售额", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=2)
    fig.update_yaxes(title_text="销售额", row=2, col=1)
    fig.update_yaxes(title_text="达成率 (%)", row=2, col=2)
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title={
            'text': main_title,
            'font': {'size': 24, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        hovermode='x unified',
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5
        )
    )
    
    # 添加动画效果
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='white')
        ),
        selector=dict(type='bar')
    )
    
    return fig

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

# 主页面
def main():
    # 检查认证状态
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("🚫 请先登录系统")
        st.stop()
    
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
        "📊 全渠道分析"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 销售达成总览 - 只保留前4个指标卡片
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
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['tt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏢 TT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['tt_achievement']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['mt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏪 MT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['mt_achievement']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 2: MT渠道分析
    with tabs[1]:
        st.markdown("### 🏪 MT渠道深度分析")
        
        # 创建MT渠道专属的综合销售指标分析图
        mt_comprehensive_fig = create_comprehensive_sales_analysis(data, focus_channel='MT')
        st.plotly_chart(mt_comprehensive_fig, use_container_width=True)
    
    # Tab 3: TT渠道分析
    with tabs[2]:
        st.markdown("### 🏢 TT渠道深度分析")
        
        # 创建TT渠道专属的综合销售指标分析图
        tt_comprehensive_fig = create_comprehensive_sales_analysis(data, focus_channel='TT')
        st.plotly_chart(tt_comprehensive_fig, use_container_width=True)
    
    # Tab 4: 全渠道分析
    with tabs[3]:
        st.markdown("### 📊 全渠道综合分析")
        
        # 区域销售对比图
        regional_fig = create_regional_comparison_chart(data)
        st.plotly_chart(regional_fig, use_container_width=True)
        
        # 分析洞察卡片（整合原来图5的内容）
        st.markdown("### 📈 关键业务洞察")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="analysis-card">
                <h4>🏆 表现最佳区域</h4>
                <ul>
                    <li>基于总销售额排名</li>
                    <li>识别重点市场</li>
                    <li>资源分配参考</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="analysis-card">
                <h4>📊 渠道结构分析</h4>
                <ul>
                    <li>MT/TT渠道占比</li>
                    <li>区域渠道偏好</li>
                    <li>发展机会识别</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="analysis-card">
                <h4>🎯 改进建议</h4>
                <ul>
                    <li>低销售区域关注</li>
                    <li>渠道平衡优化</li>
                    <li>资源调配建议</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
