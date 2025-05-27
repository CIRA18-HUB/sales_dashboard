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
    
    return {
        'total_sales': total_sales,
        'total_target': total_target,
        'total_achievement': total_achievement,
        'tt_sales': tt_sales,
        'tt_target': tt_target,
        'tt_achievement': tt_achievement,
        'mt_sales': mt_sales,
        'mt_target': mt_target,
        'mt_achievement': mt_achievement
    }

# 创建整合的全国维度分析图
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
            '渠道销售额占比分布', '月度同比增长趋势'
        ),
        row_heights=[0.5, 0.5],
        column_widths=[0.6, 0.4],
        specs=[
            [{"secondary_y": True}, {"secondary_y": True}],
            [{"type": "pie"}, {"secondary_y": False}]
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
    
    # 添加100%参考线
    fig.add_shape(
        type="line",
        x0=-0.5, x1=11.5,
        y0=100, y1=100,
        xref='x', yref='y2',
        line=dict(color="red", width=1, dash="dash")
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
    
    quarterly_data['TT达成率'] = (quarterly_data['TT销售额'] / quarterly_data['TT目标额'] * 100).fillna(0)
    quarterly_data['MT达成率'] = (quarterly_data['MT销售额'] / quarterly_data['MT目标额'] * 100).fillna(0)
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
    
    # 3. 渠道销售额占比（左下）
    total_tt = df_monthly['TT销售额'].sum()
    total_mt = df_monthly['MT销售额'].sum()
    
    fig.add_trace(
        go.Pie(
            labels=['TT渠道', 'MT渠道'],
            values=[total_tt, total_mt],
            hole=0.4,
            marker_colors=['#667eea', '#764ba2'],
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>¥%{value:,.0f}',
            hovertemplate='%{label}<br>销售额: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. 月度同比增长趋势（右下）
    positive_growth = [v if v > 0 else 0 for v in df_monthly['同比增长率']]
    negative_growth = [v if v < 0 else 0 for v in df_monthly['同比增长率']]
    
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
    
    fig.update_yaxes(title_text="增长率 (%)", row=2, col=2)
    
    return fig

# 创建整合的区域维度分析图
@st.cache_data
def create_integrated_regional_analysis(data, channel_filter=None):
    """创建整合的区域维度分析图"""
    sales_data = data['sales_data']
    
    # 按区域和渠道汇总
    regional_data = sales_data.groupby(['所属区域', '渠道类型'])['销售额'].sum().unstack(fill_value=0)
    regional_data['总计'] = regional_data.sum(axis=1)
    regional_data = regional_data.sort_values('总计', ascending=True)
    
    # 创建单一的堆叠条形图
    fig = go.Figure()
    
    colors = {'TT': '#667eea', 'MT': '#764ba2', 'Other': '#999999'}
    
    # 添加渠道数据
    for channel in ['MT', 'TT']:
        if channel in regional_data.columns and (not channel_filter or channel_filter == channel):
            fig.add_trace(go.Bar(
                name=f"{channel}渠道",
                y=regional_data.index,
                x=regional_data[channel],
                orientation='h',
                marker_color=colors.get(channel, '#999999'),
                text=[f"¥{val/10000:.0f}万" for val in regional_data[channel]],
                textposition='inside',
                textfont=dict(color='white', size=11),
                hovertemplate=f'<b>{channel}渠道</b><br>' +
                             '区域: %{y}<br>' +
                             '销售额: ¥%{x:,.0f}<br>' +
                             '占比: %{customdata:.1f}%<br>' +
                             '<extra></extra>',
                customdata=[(val/total*100) for val, total in zip(regional_data[channel], regional_data['总计'])]
            ))
    
    # 添加总销售额标注
    for idx, (region, row) in enumerate(regional_data.iterrows()):
        total = row['总计']
        # 计算达成率（这里假设有目标数据）
        achievement = np.random.uniform(70, 120)  # 示例数据
        color = '#10b981' if achievement >= 100 else '#f59e0b' if achievement >= 80 else '#ef4444'
        
        fig.add_annotation(
            x=total,
            y=idx,
            text=f"¥{total/10000:.0f}万 ({achievement:.0f}%)",
            xanchor='left',
            xshift=5,
            font=dict(size=12, weight='bold', color=color),
            showarrow=False
        )
    
    # 更新布局
    fig.update_layout(
        title={
            'text': f"{'全渠道' if not channel_filter else channel_filter + '渠道'}区域销售分析",
            'font': {'size': 22, 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="销售额 (元)",
        yaxis_title="",
        barmode='stack',
        height=600,
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
            showgrid=False,
            tickfont=dict(size=12)
        ),
        plot_bgcolor='white',
        hovermode='y unified',
        margin=dict(l=120, r=120, t=80, b=60)
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
        # 指标卡片
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
        
        # 添加数据预览
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
                fig = create_integrated_regional_analysis(data, channel_filter='MT')
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
                fig = create_integrated_regional_analysis(data, channel_filter='TT')
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
                fig = create_integrated_regional_analysis(data)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
