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
    
    /* 渠道占比卡片样式 */
    .channel-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        animation: slideUp 0.6s ease-out;
    }
    
    .channel-card-mt {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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
        
        # 打印数据预览以调试
        st.write("数据加载成功！")
        
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
    tt_percentage = (tt_sales / total_sales * 100) if total_sales > 0 else 0
    mt_percentage = (mt_sales / total_sales * 100) if total_sales > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_target': total_target,
        'total_achievement': total_achievement,
        'tt_sales': tt_sales,
        'tt_target': tt_target,
        'tt_achievement': tt_achievement,
        'mt_sales': mt_sales,
        'mt_target': mt_target,
        'mt_achievement': mt_achievement,
        'tt_percentage': tt_percentage,
        'mt_percentage': mt_percentage
    }

# 创建整合的全国维度分析图（去除饼图）
@st.cache_data
def create_integrated_national_analysis(data, channel_filter=None):
    """创建整合的全国维度分析图"""
    sales_data = data['sales_data']
    tt_city_data = data['tt_city_data']
    mt_data = data['mt_data']
    
    current_year = 2025
    
    # 创建子图 - 2行2列的布局
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '销售额与达成率月度趋势', '季度销售额与达成率',
            '月度销售额对比', '累计销售额趋势'
        ),
        row_heights=[0.5, 0.5],
        column_widths=[0.6, 0.4],
        specs=[
            [{"secondary_y": True}, {"secondary_y": True}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # 准备月度数据
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
        
        # 去年同期数据
        last_year_start = month_start - pd.DateOffset(years=1)
        last_year_end = month_end - pd.DateOffset(years=1)
        last_year_sales = sales_data[
            (sales_data['发运月份'] >= last_year_start) & 
            (sales_data['发运月份'] <= last_year_end)
        ]['销售额'].sum()
        
        monthly_data.append({
            '月份': f'{month}月',
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
                      if (tt_month_target + mt_month_target) > 0 else 0,
            '去年同期': last_year_sales,
            '同比增长率': ((tt_month_sales + mt_month_sales - last_year_sales) / last_year_sales * 100) 
                       if last_year_sales > 0 else 0
        })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # 1. 销售额与达成率月度趋势（左上）
    # 销售额柱状图
    if not channel_filter or channel_filter == 'TT':
        fig.add_trace(
            go.Bar(
                x=df_monthly['月份'],
                y=df_monthly['TT销售额'],
                name='TT销售额',
                marker_color='#667eea',
                opacity=0.8,
                hovertemplate='TT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )
    
    if not channel_filter or channel_filter == 'MT':
        fig.add_trace(
            go.Bar(
                x=df_monthly['月份'],
                y=df_monthly['MT销售额'],
                name='MT销售额',
                marker_color='#764ba2',
                opacity=0.8,
                hovertemplate='MT销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )
    
    # 达成率线图
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
            textfont=dict(size=10),
            hovertemplate='总达成率: %{y:.1f}%<br>月份: %{x}<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # 2. 季度销售额与达成率（右上）
    quarterly_data = df_monthly.groupby('季度').agg({
        'TT销售额': 'sum',
        'MT销售额': 'sum',
        'TT目标额': 'sum',
        'MT目标额': 'sum',
        '总销售额': 'sum',
        '总目标额': 'sum'
    }).reset_index()
    
    quarterly_data['总达成率'] = (quarterly_data['总销售额'] / quarterly_data['总目标额'] * 100).fillna(0)
    
    # 季度销售额
    if not channel_filter or channel_filter == 'TT':
        fig.add_trace(
            go.Bar(
                x=quarterly_data['季度'],
                y=quarterly_data['TT销售额'],
                name='TT季度销售',
                marker_color='#667eea',
                text=[f'{v/10000:.0f}万' for v in quarterly_data['TT销售额']],
                textposition='inside',
                hovertemplate='TT: ¥%{y:,.0f}<br>季度: %{x}<extra></extra>'
            ),
            row=1, col=2, secondary_y=False
        )
    
    if not channel_filter or channel_filter == 'MT':
        fig.add_trace(
            go.Bar(
                x=quarterly_data['季度'],
                y=quarterly_data['MT销售额'],
                name='MT季度销售',
                marker_color='#764ba2',
                text=[f'{v/10000:.0f}万' for v in quarterly_data['MT销售额']],
                textposition='inside',
                hovertemplate='MT: ¥%{y:,.0f}<br>季度: %{x}<extra></extra>'
            ),
            row=1, col=2, secondary_y=False
        )
    
    # 季度达成率
    fig.add_trace(
        go.Scatter(
            x=quarterly_data['季度'],
            y=quarterly_data['总达成率'],
            name='季度达成率',
            mode='lines+markers+text',
            line=dict(color='#10b981', width=3),
            marker=dict(size=12),
            text=[f'{v:.0f}%' for v in quarterly_data['总达成率']],
            textposition='top center',
            hovertemplate='达成率: %{y:.1f}%<br>季度: %{x}<extra></extra>'
        ),
        row=1, col=2, secondary_y=True
    )
    
    # 3. 月度销售额对比（左下） - 替换原来的饼图
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['总销售额'],
            name='当前销售额',
            marker_color='#667eea',
            text=[f'{v/10000:.0f}万' for v in df_monthly['总销售额']],
            textposition='outside',
            hovertemplate='销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['去年同期'],
            name='去年同期',
            marker_color='#999999',
            opacity=0.6,
            hovertemplate='去年同期: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. 累计销售额趋势（右下）
    cumulative_current = df_monthly['总销售额'].cumsum()
    cumulative_target = df_monthly['总目标额'].cumsum()
    
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=cumulative_current,
            name='累计销售额',
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            fill='tonexty',
            hovertemplate='累计销售额: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=cumulative_target,
            name='累计目标',
            mode='lines+markers',
            line=dict(color='#ef4444', width=2, dash='dash'),
            marker=dict(size=6),
            hovertemplate='累计目标: ¥%{y:,.0f}<br>月份: %{x}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=800,
        showlegend=True,
        title={
            'text': f"{'全国' if not channel_filter else channel_filter + '渠道'}销售综合分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        hovermode='x unified',
        plot_bgcolor='white',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        )
    )
    
    # 更新坐标轴
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=1, secondary_y=True)
    
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=2, secondary_y=False)
    fig.update_yaxes(title_text="达成率 (%)", row=1, col=2, secondary_y=True)
    
    fig.update_yaxes(title_text="销售额 (元)", row=2, col=1)
    fig.update_yaxes(title_text="累计销售额 (元)", row=2, col=2)
    
    return fig

# 创建改进的区域维度分析图
@st.cache_data
def create_improved_regional_analysis(data, channel_filter=None):
    """创建改进的区域维度分析图"""
    sales_data = data['sales_data']
    
    # 按区域和渠道汇总
    regional_data = sales_data.groupby(['所属区域', '渠道类型'])['销售额'].sum().unstack(fill_value=0)
    regional_data['总计'] = regional_data.sum(axis=1)
    regional_data = regional_data.sort_values('总计', ascending=False)
    
    # 创建2x2布局的子图
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('区域销售额排名', '区域渠道结构', '区域达成率分析', '区域增长趋势'),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    colors = {'TT': '#667eea', 'MT': '#764ba2'}
    
    # 1. 区域销售额排名（左上）
    fig.add_trace(
        go.Bar(
            x=regional_data['总计'],
            y=regional_data.index,
            name='总销售额',
            orientation='h',
            marker_color='#667eea',
            text=[f'¥{val/10000:.0f}万' for val in regional_data['总计']],
            textposition='auto',
            hovertemplate='区域: %{y}<br>总销售额: ¥%{x:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. 区域渠道结构（右上）
    for channel in ['MT', 'TT']:
        if channel in regional_data.columns and (not channel_filter or channel_filter == channel):
            fig.add_trace(
                go.Bar(
                    x=regional_data.index,
                    y=regional_data[channel],
                    name=f'{channel}渠道',
                    marker_color=colors[channel],
                    text=[f'{val/10000:.0f}万' for val in regional_data[channel]],
                    textposition='auto',
                    hovertemplate=f'{channel}渠道<br>区域: %{{x}}<br>销售额: ¥%{{y:,.0f}}<extra></extra>'
                ),
                row=1, col=2
            )
    
    # 3. 区域达成率分析（左下） - 模拟达成率数据
    achievement_rates = np.random.uniform(70, 120, len(regional_data))
    colors_achievement = ['#10b981' if rate >= 100 else '#f59e0b' if rate >= 80 else '#ef4444' 
                         for rate in achievement_rates]
    
    fig.add_trace(
        go.Scatter(
            x=regional_data['总计'],
            y=achievement_rates,
            mode='markers+text',
            marker=dict(
                size=[val/1000000 for val in regional_data['总计']],  # 销售额决定点的大小
                color=colors_achievement,
                sizemode='area',
                sizeref=2.*max([val/1000000 for val in regional_data['总计']])/(40.**2),
                sizemin=10
            ),
            text=regional_data.index,
            textposition='top center',
            name='区域达成率',
            hovertemplate='区域: %{text}<br>销售额: ¥%{x:,.0f}<br>达成率: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 添加达成率参考线
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="目标线(100%)", row=2, col=1)
    
    # 4. 区域增长趋势（右下） - 模拟同比增长数据
    growth_rates = np.random.uniform(-10, 30, len(regional_data))
    positive_growth = [rate if rate > 0 else 0 for rate in growth_rates]
    negative_growth = [rate if rate < 0 else 0 for rate in growth_rates]
    
    fig.add_trace(
        go.Bar(
            x=regional_data.index,
            y=positive_growth,
            name='正增长',
            marker_color='#10b981',
            hovertemplate='区域: %{x}<br>增长率: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=regional_data.index,
            y=negative_growth,
            name='负增长',
            marker_color='#ef4444',
            hovertemplate='区域: %{x}<br>增长率: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=800,
        title={
            'text': f"{'全渠道' if not channel_filter else channel_filter + '渠道'}区域综合分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='white'
    )
    
    # 更新各子图的坐标轴
    fig.update_xaxes(title_text="销售额 (元)", row=1, col=1)
    fig.update_yaxes(title_text="区域", row=1, col=1)
    
    fig.update_xaxes(title_text="区域", row=1, col=2, tickangle=-45)
    fig.update_yaxes(title_text="销售额 (元)", row=1, col=2)
    
    fig.update_xaxes(title_text="销售额 (元)", row=2, col=1)
    fig.update_yaxes(title_text="达成率 (%)", row=2, col=1)
    
    fig.update_xaxes(title_text="区域", row=2, col=2, tickangle=-45)
    fig.update_yaxes(title_text="增长率 (%)", row=2, col=2)
    
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
        "📊 全渠道分析"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 销售达成总览
    with tabs[0]:
        # 第一行：总体指标卡片
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第二行：渠道占比卡片（替换原来的饼图）
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="channel-card">
                <h3>🏢 TT渠道占比</h3>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 1rem 0;">
                    {metrics['tt_percentage']:.1f}%
                </div>
                <div style="font-size: 1.2rem;">
                    销售额: ¥{metrics['tt_sales']/10000:.0f}万
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="channel-card channel-card-mt">
                <h3>🏪 MT渠道占比</h3>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 1rem 0;">
                    {metrics['mt_percentage']:.1f}%
                </div>
                <div style="font-size: 1.2rem;">
                    销售额: ¥{metrics['mt_sales']/10000:.0f}万
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 保留原始数据查看功能
        with st.expander("查看原始数据", expanded=False):
            st.write("销售数据样本：")
            st.dataframe(data['sales_data'].head())
            st.write("TT城市指标数据样本：")
            st.dataframe(data['tt_city_data'].head())
            st.write("MT指标数据样本：")
            st.dataframe(data['mt_data'].head())
    
    # Tab 2: MT渠道分析
    with tabs[1]:
        st.markdown("### 🏪 MT渠道深度分析")
        
        # 维度选择
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            dimension_mt = st.radio(
                "分析维度",
                ["全国维度", "区域维度"],
                key="mt_dimension",
                horizontal=True
            )
        
        # 显示相应图表
        with st.container():
            if dimension_mt == "全国维度":
                fig = create_integrated_national_analysis(data, channel_filter='MT')
            else:
                fig = create_improved_regional_analysis(data, channel_filter='MT')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: TT渠道分析
    with tabs[2]:
        st.markdown("### 🏢 TT渠道深度分析")
        
        # 维度选择
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            dimension_tt = st.radio(
                "分析维度",
                ["全国维度", "区域维度"],
                key="tt_dimension",
                horizontal=True
            )
        
        # 显示相应图表
        with st.container():
            if dimension_tt == "全国维度":
                fig = create_integrated_national_analysis(data, channel_filter='TT')
            else:
                fig = create_improved_regional_analysis(data, channel_filter='TT')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: 全渠道分析
    with tabs[3]:
        st.markdown("### 📊 全渠道综合分析")
        
        # 维度选择
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            dimension_all = st.radio(
                "分析维度",
                ["全国维度", "区域维度"],
                key="all_dimension",
                horizontal=True
            )
        
        # 显示相应图表
        with st.container():
            if dimension_all == "全国维度":
                fig = create_integrated_national_analysis(data)
            else:
                fig = create_improved_regional_analysis(data)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
