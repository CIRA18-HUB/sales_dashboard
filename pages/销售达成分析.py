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

# 增强的CSS样式 - 参考产品组合分析的样式
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
    
    /* 增强的动画效果 */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 区域卡片动画 */
    .region-card {
        animation: float 3s ease-in-out infinite;
        animation-delay: calc(var(--i) * 0.2s);
    }
    
    /* 成就卡片特效 */
    .achievement-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: slideInRight 0.8s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* 渠道分析卡片 */
    .channel-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border-top: 4px solid transparent;
        border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
    }
    
    .channel-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* 趋势图卡片 */
    .trend-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        animation: fadeInUp 1s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 目标线动画 */
    .target-line {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* 数据点动画 */
    .data-point {
        animation: float 3s ease-in-out infinite;
    }
    
    /* 强调文本 */
    .highlight-text {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* 成功指标 */
    .success-metric {
        color: #10b981;
        font-weight: bold;
    }
    
    /* 警告指标 */
    .warning-metric {
        color: #f59e0b;
        font-weight: bold;
    }
    
    /* 危险指标 */
    .danger-metric {
        color: #ef4444;
        font-weight: bold;
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
        sales_data['渠道类型'] = sales_data['订单类型'].apply(
            lambda x: 'TT' if 'TT' in str(x) else ('MT' if 'MT' in str(x) else 'Other')
        )
        
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
    regions = sales_data['所属区域'].unique()
    
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
        'regions': len(regions)
    }

# 创建增强的区域分析图表
def create_regional_analysis_chart(data, channel='ALL'):
    """创建区域分析图表"""
    sales_data = data['sales_data']
    
    # 根据渠道筛选数据
    if channel == 'TT':
        filtered_data = sales_data[sales_data['渠道类型'] == 'TT']
    elif channel == 'MT':
        filtered_data = sales_data[sales_data['渠道类型'] == 'MT']
    else:
        filtered_data = sales_data
    
    # 按区域汇总
    regional_stats = filtered_data.groupby('所属区域').agg({
        '销售额': 'sum'
    }).reset_index()
    
    # 创建图表
    fig = go.Figure()
    
    # 添加柱状图
    fig.add_trace(go.Bar(
        x=regional_stats['所属区域'],
        y=regional_stats['销售额'],
        marker=dict(
            color=regional_stats['销售额'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="销售额")
        ),
        text=[f"¥{val:,.0f}" for val in regional_stats['销售额']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{channel}渠道各区域销售额分析" if channel != 'ALL' else "全渠道各区域销售额分析",
        xaxis_title="销售区域",
        yaxis_title="销售额 (¥)",
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig

# 创建月度趋势分析图
def create_monthly_trend_chart(data):
    """创建月度趋势分析图"""
    sales_data = data['sales_data']
    
    # 按月份和渠道汇总
    monthly_stats = sales_data.groupby([
        sales_data['发运月份'].dt.to_period('M'),
        '渠道类型'
    ])['销售额'].sum().reset_index()
    
    monthly_stats['发运月份'] = monthly_stats['发运月份'].astype(str)
    
    fig = go.Figure()
    
    # 为每个渠道添加趋势线
    for channel in ['TT', 'MT']:
        channel_data = monthly_stats[monthly_stats['渠道类型'] == channel]
        
        fig.add_trace(go.Scatter(
            x=channel_data['发运月份'],
            y=channel_data['销售额'],
            name=f"{channel}渠道",
            mode='lines+markers',
            line=dict(width=3, shape='spline'),
            marker=dict(size=10),
            hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="销售额月度趋势分析",
        xaxis_title="月份",
        yaxis_title="销售额 (¥)",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# 创建城市达成率热力图
def create_city_achievement_heatmap(data):
    """创建城市达成率热力图"""
    tt_city_data = data['tt_city_data']
    sales_data = data['sales_data']
    
    # 计算各城市达成率
    city_achievement = []
    
    cities = tt_city_data['城市'].unique()
    for city in cities[:20]:  # 限制显示前20个城市
        city_target = tt_city_data[
            (tt_city_data['城市'] == city) &
            (tt_city_data['指标年月'].dt.year == 2025)
        ]['月度指标'].sum()
        
        city_sales = sales_data[
            (sales_data['城市'] == city) &
            (sales_data['发运月份'].dt.year == 2025) &
            (sales_data['渠道类型'] == 'TT')
        ]['销售额'].sum()
        
        if city_target > 0:
            achievement = (city_sales / city_target * 100)
            city_achievement.append({
                'city': city,
                'achievement': achievement,
                'sales': city_sales,
                'target': city_target
            })
    
    # 创建热力图数据
    achievement_df = pd.DataFrame(city_achievement)
    achievement_df = achievement_df.sort_values('achievement', ascending=False)
    
    # 创建图表
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=achievement_df['city'],
        y=achievement_df['achievement'],
        marker=dict(
            color=achievement_df['achievement'],
            colorscale=[
                [0, '#ef4444'],      # 红色 - 低达成率
                [0.5, '#f59e0b'],    # 橙色 - 中等达成率
                [0.8, '#10b981'],    # 绿色 - 高达成率
                [1, '#059669']       # 深绿色 - 超额达成
            ],
            cmin=0,
            cmax=150,
            showscale=True,
            colorbar=dict(title="达成率(%)")
        ),
        text=[f"{val:.1f}%" for val in achievement_df['achievement']],
        textposition='outside',
        hovertemplate="""<b>%{x}</b><br>
达成率: %{y:.1f}%<br>
销售额: ¥%{customdata[0]:,.0f}<br>
目标额: ¥%{customdata[1]:,.0f}<extra></extra>""",
        customdata=achievement_df[['sales', 'target']].values
    ))
    
    # 添加目标线
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="目标线 100%", annotation_position="right")
    
    fig.update_layout(
        title="TT渠道城市达成率排名 (Top 20)",
        xaxis_title="城市",
        yaxis_title="达成率 (%)",
        height=600,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

# 主页面
def main():
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
        "🗺️ 区域表现分析",
        "📈 趋势洞察",
        "🏆 城市达成排名"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 销售达成总览 - 只显示指标卡片
    with tabs[0]:
        # 第一行指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['total_sales']:,.0f}</div>
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
                <div class="metric-sublabel">目标: ¥{metrics['total_target']:,.0f}</div>
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
                <div class="metric-value">¥{metrics['tt_sales']:,.0f}</div>
                <div class="metric-label">🏢 TT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['tt_achievement']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['mt_sales']:,.0f}</div>
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
        
        # 增加一些视觉效果
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 成就展示
        achievements = []
        if metrics['total_achievement'] >= 100:
            achievements.append("🏆 销售目标达成")
        if metrics['growth_rate'] > 20:
            achievements.append("🚀 高速增长")
        if metrics['city_achievement_rate'] > 80:
            achievements.append("🌟 城市覆盖优秀")
        
        if achievements:
            st.markdown("### 🎖️ 成就达成")
            cols = st.columns(len(achievements))
            for idx, achievement in enumerate(achievements):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="achievement-card">
                        <h4>{achievement}</h4>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tab 2: MT渠道分析
    with tabs[1]:
        st.markdown("### 🏪 MT渠道深度分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # MT渠道区域分析图
            mt_regional_fig = create_regional_analysis_chart(data, 'MT')
            st.plotly_chart(mt_regional_fig, use_container_width=True)
        
        with col2:
            # MT渠道关键指标
            mt_metrics = {
                '总销售额': f"¥{metrics['mt_sales']:,.0f}",
                '达成率': f"{metrics['mt_achievement']:.1f}%",
                '占比': f"{(metrics['mt_sales'] / metrics['total_sales'] * 100):.1f}%"
            }
            
            for label, value in mt_metrics.items():
                st.markdown(f"""
                <div class="channel-card">
                    <h4>{label}</h4>
                    <h2 class="highlight-text">{value}</h2>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 3: TT渠道分析
    with tabs[2]:
        st.markdown("### 🏢 TT渠道深度分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # TT渠道区域分析图
            tt_regional_fig = create_regional_analysis_chart(data, 'TT')
            st.plotly_chart(tt_regional_fig, use_container_width=True)
        
        with col2:
            # TT渠道关键指标
            tt_metrics = {
                '总销售额': f"¥{metrics['tt_sales']:,.0f}",
                '达成率': f"{metrics['tt_achievement']:.1f}%",
                '占比': f"{(metrics['tt_sales'] / metrics['total_sales'] * 100):.1f}%"
            }
            
            for label, value in tt_metrics.items():
                st.markdown(f"""
                <div class="channel-card">
                    <h4>{label}</h4>
                    <h2 class="highlight-text">{value}</h2>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 4: 区域表现分析
    with tabs[3]:
        st.markdown("### 🗺️ 全渠道区域表现分析")
        
        # 全渠道区域分析
        all_regional_fig = create_regional_analysis_chart(data, 'ALL')
        st.plotly_chart(all_regional_fig, use_container_width=True)
        
        # 区域对比分析
        sales_data = data['sales_data']
        regional_comparison = sales_data.groupby(['所属区域', '渠道类型'])['销售额'].sum().unstack(fill_value=0)
        
        if not regional_comparison.empty:
            fig = go.Figure()
            
            for channel in regional_comparison.columns:
                fig.add_trace(go.Bar(
                    name=f"{channel}渠道",
                    x=regional_comparison.index,
                    y=regional_comparison[channel],
                    text=[f"¥{val:,.0f}" for val in regional_comparison[channel]],
                    textposition='auto',
                    hovertemplate='<b>%{x} - %{fullData.name}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
                ))
            
            fig.update_layout(
                title="各区域渠道销售额对比",
                xaxis_title="销售区域",
                yaxis_title="销售额 (¥)",
                barmode='group',
                height=500,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: 趋势洞察
    with tabs[4]:
        st.markdown("### 📈 销售趋势洞察分析")
        
        # 月度趋势图
        monthly_trend_fig = create_monthly_trend_chart(data)
        st.plotly_chart(monthly_trend_fig, use_container_width=True)
        
        # 季度分析
        sales_data = data['sales_data']
        sales_data['季度'] = sales_data['发运月份'].dt.quarter
        sales_data['年份'] = sales_data['发运月份'].dt.year
        
        quarterly_stats = sales_data.groupby(['年份', '季度', '渠道类型'])['销售额'].sum().reset_index()
        
        fig = go.Figure()
        
        for channel in ['TT', 'MT']:
            channel_data = quarterly_stats[quarterly_stats['渠道类型'] == channel]
            channel_data['季度标签'] = channel_data['年份'].astype(str) + 'Q' + channel_data['季度'].astype(str)
            
            fig.add_trace(go.Bar(
                name=f"{channel}渠道",
                x=channel_data['季度标签'],
                y=channel_data['销售额'],
                text=[f"¥{val:,.0f}" for val in channel_data['销售额']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title="季度销售额对比",
            xaxis_title="季度",
            yaxis_title="销售额 (¥)",
            barmode='group',
            height=500,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 6: 城市达成排名
    with tabs[5]:
        st.markdown("### 🏆 TT渠道城市达成率排名")
        
        # 城市达成率热力图
        city_heatmap_fig = create_city_achievement_heatmap(data)
        st.plotly_chart(city_heatmap_fig, use_container_width=True)
        
        # 城市分类统计
        tt_city_data = data['tt_city_data']
        city_types = tt_city_data[tt_city_data['指标年月'].dt.year == 2025].groupby('城市类型')['城市'].nunique()
        
        if not city_types.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**C60城市数量**: {city_types.get('C60', 0)}个")
            
            with col2:
                st.info(f"**非C60城市数量**: {city_types.get('非C60', 0)}个")
            
            with col3:
                total_cities = city_types.sum()
                st.info(f"**城市总数**: {total_cities}个")

if __name__ == "__main__":
    main()
