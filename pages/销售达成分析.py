# pages/销售达成分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
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
    
    # 计算渠道占比
    tt_ratio = (tt_sales / total_sales * 100) if total_sales > 0 else 0
    mt_ratio = (mt_sales / total_sales * 100) if total_sales > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_target': total_target,
        'total_achievement': total_achievement,
        'tt_sales': tt_sales,
        'tt_target': tt_target,
        'tt_achievement': tt_achievement,
        'tt_ratio': tt_ratio,
        'mt_sales': mt_sales,
        'mt_target': mt_target,
        'mt_achievement': mt_achievement,
        'mt_ratio': mt_ratio
    }

# 创建综合分析图 - MT渠道
@st.cache_data
def create_mt_comprehensive_analysis(data):
    """创建MT渠道综合分析图"""
    sales_data = data['sales_data']
    mt_data = data['mt_data']
    
    current_year = 2025
    
    # 创建2x2子图布局
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'MT渠道月度销售额与达成率', 'MT渠道区域销售分布',
            'MT渠道季度对比分析', 'MT渠道同比增长趋势'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": False}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. 月度销售额与达成率
    monthly_data = []
    for month in range(1, 13):
        month_start = pd.Timestamp(f'{current_year}-{month:02d}-01')
        month_end = month_start + pd.offsets.MonthEnd(0)
        
        mt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'MT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        mt_month_target = mt_data[
            (mt_data['月份'] >= month_start) & 
            (mt_data['月份'] <= month_end)
        ]['月度指标'].sum()
        
        mt_achievement = (mt_month_sales / mt_month_target * 100) if mt_month_target > 0 else 0
        
        # 去年同期数据
        last_year_start = month_start - pd.DateOffset(years=1)
        last_year_end = month_end - pd.DateOffset(years=1)
        last_year_sales = sales_data[
            (sales_data['渠道类型'] == 'MT') & 
            (sales_data['发运月份'] >= last_year_start) & 
            (sales_data['发运月份'] <= last_year_end)
        ]['销售额'].sum()
        
        growth_rate = ((mt_month_sales - last_year_sales) / last_year_sales * 100) if last_year_sales > 0 else 0
        
        monthly_data.append({
            '月份': f'{month}月',
            '季度': f'Q{(month-1)//3 + 1}',
            'MT销售额': mt_month_sales,
            'MT达成率': mt_achievement,
            '同比增长': growth_rate
        })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # 添加月度销售额柱状图
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['MT销售额'],
            name='MT销售额',
            marker_color='#764ba2',
            text=[f'{v/10000:.0f}万' for v in df_monthly['MT销售额']],
            textposition='inside',
            hovertemplate='MT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=False
    )
    
    # 添加达成率线图
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=df_monthly['MT达成率'],
            name='MT达成率',
            mode='lines+markers+text',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8),
            text=[f'{v:.0f}%' for v in df_monthly['MT达成率']],
            textposition='top center',
            hovertemplate='MT达成率: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # 2. 区域销售分布
    regional_data = sales_data[sales_data['渠道类型'] == 'MT'].groupby('所属区域')['销售额'].sum().sort_values(ascending=True)
    
    fig.add_trace(
        go.Bar(
            y=regional_data.index,
            x=regional_data.values,
            name='区域销售额',
            orientation='h',
            marker_color='#764ba2',
            text=[f'¥{v/10000:.0f}万' for v in regional_data.values],
            textposition='inside',
            hovertemplate='区域: %{y}<br>销售额: ¥%{x:,.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. 季度对比分析
    quarterly_data = df_monthly.groupby('季度')['MT销售额'].sum()
    
    fig.add_trace(
        go.Bar(
            x=quarterly_data.index,
            y=quarterly_data.values,
            name='季度销售额',
            marker_color='#667eea',
            text=[f'{v/10000:.0f}万' for v in quarterly_data.values],
            textposition='inside',
            hovertemplate='季度: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. 同比增长趋势
    positive_growth = [max(0, v) for v in df_monthly['同比增长']]
    negative_growth = [min(0, v) for v in df_monthly['同比增长']]
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=positive_growth,
            name='正增长',
            marker_color='#10b981',
            hovertemplate='同比增长: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=negative_growth,
            name='负增长',
            marker_color='#ef4444',
            hovertemplate='同比下降: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=700,
        showlegend=True,
        title={
            'text': "🏪 MT渠道综合分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # 更新坐标轴
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="增长率 (%)", row=2, col=2)
    
    return fig

# 创建综合分析图 - TT渠道
@st.cache_data
def create_tt_comprehensive_analysis(data):
    """创建TT渠道综合分析图"""
    sales_data = data['sales_data']
    tt_city_data = data['tt_city_data']
    
    current_year = 2025
    
    # 创建2x2子图布局
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'TT渠道月度销售额与达成率', 'TT渠道区域销售分布',
            'TT渠道季度对比分析', 'TT渠道同比增长趋势'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": False}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. 月度销售额与达成率
    monthly_data = []
    for month in range(1, 13):
        month_start = pd.Timestamp(f'{current_year}-{month:02d}-01')
        month_end = month_start + pd.offsets.MonthEnd(0)
        
        tt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'TT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        tt_month_target = tt_city_data[
            (tt_city_data['指标年月'] >= month_start) & 
            (tt_city_data['指标年月'] <= month_end)
        ]['月度指标'].sum()
        
        tt_achievement = (tt_month_sales / tt_month_target * 100) if tt_month_target > 0 else 0
        
        # 去年同期数据
        last_year_start = month_start - pd.DateOffset(years=1)
        last_year_end = month_end - pd.DateOffset(years=1)
        last_year_sales = sales_data[
            (sales_data['渠道类型'] == 'TT') & 
            (sales_data['发运月份'] >= last_year_start) & 
            (sales_data['发运月份'] <= last_year_end)
        ]['销售额'].sum()
        
        growth_rate = ((tt_month_sales - last_year_sales) / last_year_sales * 100) if last_year_sales > 0 else 0
        
        monthly_data.append({
            '月份': f'{month}月',
            '季度': f'Q{(month-1)//3 + 1}',
            'TT销售额': tt_month_sales,
            'TT达成率': tt_achievement,
            '同比增长': growth_rate
        })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # 添加月度销售额柱状图
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['TT销售额'],
            name='TT销售额',
            marker_color='#667eea',
            text=[f'{v/10000:.0f}万' for v in df_monthly['TT销售额']],
            textposition='inside',
            hovertemplate='TT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=False
    )
    
    # 添加达成率线图
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=df_monthly['TT达成率'],
            name='TT达成率',
            mode='lines+markers+text',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8),
            text=[f'{v:.0f}%' for v in df_monthly['TT达成率']],
            textposition='top center',
            hovertemplate='TT达成率: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # 2. 区域销售分布
    regional_data = sales_data[sales_data['渠道类型'] == 'TT'].groupby('所属区域')['销售额'].sum().sort_values(ascending=True)
    
    fig.add_trace(
        go.Bar(
            y=regional_data.index,
            x=regional_data.values,
            name='区域销售额',
            orientation='h',
            marker_color='#667eea',
            text=[f'¥{v/10000:.0f}万' for v in regional_data.values],
            textposition='inside',
            hovertemplate='区域: %{y}<br>销售额: ¥%{x:,.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. 季度对比分析
    quarterly_data = df_monthly.groupby('季度')['TT销售额'].sum()
    
    fig.add_trace(
        go.Bar(
            x=quarterly_data.index,
            y=quarterly_data.values,
            name='季度销售额',
            marker_color='#764ba2',
            text=[f'{v/10000:.0f}万' for v in quarterly_data.values],
            textposition='inside',
            hovertemplate='季度: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. 同比增长趋势
    positive_growth = [max(0, v) for v in df_monthly['同比增长']]
    negative_growth = [min(0, v) for v in df_monthly['同比增长']]
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=positive_growth,
            name='正增长',
            marker_color='#10b981',
            hovertemplate='同比增长: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=negative_growth,
            name='负增长',
            marker_color='#ef4444',
            hovertemplate='同比下降: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=700,
        showlegend=True,
        title={
            'text': "🏢 TT渠道综合分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # 更新坐标轴
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="增长率 (%)", row=2, col=2)
    
    return fig

# 创建全渠道综合分析图
@st.cache_data
def create_all_channel_comprehensive_analysis(data):
    """创建全渠道综合分析图"""
    sales_data = data['sales_data']
    tt_city_data = data['tt_city_data']
    mt_data = data['mt_data']
    
    current_year = 2025
    
    # 创建2x2子图布局
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '全渠道月度销售额与达成率对比', '渠道销售额季度对比',
            '区域渠道销售分布热力图', '全年销售趋势与预测'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": True}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. 月度销售额与达成率
    monthly_data = []
    for month in range(1, 13):
        month_start = pd.Timestamp(f'{current_year}-{month:02d}-01')
        month_end = month_start + pd.offsets.MonthEnd(0)
        
        # TT渠道数据
        tt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'TT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        tt_month_target = tt_city_data[
            (tt_city_data['指标年月'] >= month_start) & 
            (tt_city_data['指标年月'] <= month_end)
        ]['月度指标'].sum()
        
        # MT渠道数据
        mt_month_sales = sales_data[
            (sales_data['渠道类型'] == 'MT') & 
            (sales_data['发运月份'] >= month_start) & 
            (sales_data['发运月份'] <= month_end)
        ]['销售额'].sum()
        
        mt_month_target = mt_data[
            (mt_data['月份'] >= month_start) & 
            (mt_data['月份'] <= month_end)
        ]['月度指标'].sum()
        
        total_sales = tt_month_sales + mt_month_sales
        total_target = tt_month_target + mt_month_target
        total_achievement = (total_sales / total_target * 100) if total_target > 0 else 0
        
        monthly_data.append({
            '月份': f'{month}月',
            '季度': f'Q{(month-1)//3 + 1}',
            'TT销售额': tt_month_sales,
            'MT销售额': mt_month_sales,
            '总销售额': total_sales,
            '总达成率': total_achievement
        })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # 添加TT和MT销售额
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['TT销售额'],
            name='TT销售额',
            marker_color='#667eea',
            hovertemplate='TT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['MT销售额'],
            name='MT销售额',
            marker_color='#764ba2',
            hovertemplate='MT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=False
    )
    
    # 添加总达成率线图
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=df_monthly['总达成率'],
            name='总达成率',
            mode='lines+markers+text',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8),
            text=[f'{v:.0f}%' for v in df_monthly['总达成率']],
            textposition='top center',
            hovertemplate='总达成率: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # 2. 季度对比
    quarterly_tt = df_monthly.groupby('季度')['TT销售额'].sum()
    quarterly_mt = df_monthly.groupby('季度')['MT销售额'].sum()
    
    fig.add_trace(
        go.Bar(
            x=quarterly_tt.index,
            y=quarterly_tt.values,
            name='TT季度销售',
            marker_color='#667eea',
            text=[f'{v/10000:.0f}万' for v in quarterly_tt.values],
            textposition='inside',
            hovertemplate='TT: ¥%{y:,.0f}<br>季度: %{x}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=quarterly_mt.index,
            y=quarterly_mt.values,
            name='MT季度销售',
            marker_color='#764ba2',
            text=[f'{v/10000:.0f}万' for v in quarterly_mt.values],
            textposition='inside',
            hovertemplate='MT: ¥%{y:,.0f}<br>季度: %{x}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. 区域渠道分布
    regional_channel = sales_data.groupby(['所属区域', '渠道类型'])['销售额'].sum().unstack(fill_value=0)
    if 'TT' in regional_channel.columns:
        fig.add_trace(
            go.Bar(
                y=regional_channel.index,
                x=regional_channel['TT'],
                name='TT区域销售',
                orientation='h',
                marker_color='#667eea',
                hovertemplate='TT区域: %{y}<br>销售额: ¥%{x:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    if 'MT' in regional_channel.columns:
        fig.add_trace(
            go.Bar(
                y=regional_channel.index,
                x=regional_channel['MT'],
                name='MT区域销售',
                orientation='h',
                marker_color='#764ba2',
                hovertemplate='MT区域: %{y}<br>销售额: ¥%{x:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 4. 累计销售趋势
    cumulative_sales = df_monthly['总销售额'].cumsum()
    
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=cumulative_sales,
            name='累计销售额',
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            fill='tonexty',
            hovertemplate='累计销售: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2, secondary_y=False
    )
    
    # 更新布局
    fig.update_layout(
        height=700,
        showlegend=True,
        title={
            'text': "📊 全渠道综合分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='white',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # 更新坐标轴
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="累计销售额 (元)", row=2, col=2)
    
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
    with st.spinner('正在加载数据...'):
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
        "📊 全渠道对比"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 销售达成总览
    with tabs[0]:
        # 增强的指标卡片布局 - 2行3列
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['total_sales']/10000:.0f}万</div>
                <div class="metric-label">💰 2025年总销售额</div>
                <div class="metric-sublabel">目标: ¥{metrics['total_target']/10000:.0f}万</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            achievement_color = "#10b981" if metrics['total_achievement'] >= 100 else "#f59e0b" if metrics['total_achievement'] >= 80 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {achievement_color}">{metrics['total_achievement']:.1f}%</div>
                <div class="metric-label">🎯 总体达成率</div>
                <div class="metric-sublabel">{'✅ 超额完成' if metrics['total_achievement'] >= 100 else '⚠️ 需要努力' if metrics['total_achievement'] >= 80 else '🚨 严重不足'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            gap = metrics['total_target'] - metrics['total_sales']
            gap_color = "#10b981" if gap <= 0 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {gap_color}">¥{abs(gap)/10000:.0f}万</div>
                <div class="metric-label">📈 {'超额完成' if gap <= 0 else '目标缺口'}</div>
                <div class="metric-sublabel">{'🎉 恭喜达标' if gap <= 0 else '💪 继续加油'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第二行 - 渠道对比卡片
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['tt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏢 TT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['tt_achievement']:.1f}% | 占比: {metrics['tt_ratio']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['mt_sales']/10000:.0f}万</div>
                <div class="metric-label">🏪 MT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['mt_achievement']:.1f}% | 占比: {metrics['mt_ratio']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            better_channel = "TT" if metrics['tt_achievement'] > metrics['mt_achievement'] else "MT"
            better_color = "#667eea" if better_channel == "TT" else "#764ba2"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {better_color}">{better_channel}</div>
                <div class="metric-label">🏆 表现更优渠道</div>
                <div class="metric-sublabel">{better_channel}渠道达成率更高</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 添加数据预览
        with st.expander("查看原始数据", expanded=False):
            tab1, tab2, tab3 = st.tabs(["销售数据", "TT指标数据", "MT指标数据"])
            with tab1:
                st.dataframe(data['sales_data'].head())
            with tab2:
                st.dataframe(data['tt_city_data'].head())
            with tab3:
                st.dataframe(data['mt_data'].head())
    
    # Tab 2: MT渠道分析
    with tabs[1]:
        fig = create_mt_comprehensive_analysis(data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: TT渠道分析
    with tabs[2]:
        fig = create_tt_comprehensive_analysis(data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: 全渠道对比
    with tabs[3]:
        fig = create_all_channel_comprehensive_analysis(data)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
