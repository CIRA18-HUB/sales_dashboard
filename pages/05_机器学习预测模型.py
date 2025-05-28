# 机器学习模型预测.py - 智能预测分析系统
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="智能预测分析系统",
    page_icon="🤖",
    layout="wide"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 统一的增强CSS样式 - 基于附件一的样式并进行优化
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 全局字体和背景 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* 添加浮动粒子背景动画 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    /* 主容器背景 */
    .main .block-container {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 页面标题样式 */
    .page-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white;
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.5s ease-out;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }

    .page-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
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
        from { 
            opacity: 0; 
            transform: translateY(-50px) scale(0.8); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }

    .page-title {
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        line-height: 1.1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .page-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* 统一的卡片容器样式 */
    .metric-card, .content-container, .chart-container, .insight-box {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 25px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03);
        border: 1px solid rgba(255,255,255,0.3);
        animation: slideUpStagger 1s ease-out;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }

    /* 指标卡片增强样式 */
    .metric-card {
        text-align: center;
        height: 100%;
        padding: 2.5rem 2rem;
        position: relative;
        overflow: visible !important;
        perspective: 1000px;
        animation: cardEntrance 1s ease-out;
        transform-style: preserve-3d;
    }

    /* 3D翻转效果 */
    .metric-card-inner {
        width: 100%;
        height: 100%;
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }

    .metric-card:hover .metric-card-inner {
        transform: rotateY(5deg) rotateX(-5deg);
    }

    /* 波纹效果 */
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.2) 0%, transparent 70%);
        transform: translate(-50%, -50%) scale(0);
        animation: ripple 3s infinite;
        opacity: 0;
        pointer-events: none;
    }

    @keyframes ripple {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        100% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0;
        }
    }

    @keyframes cardEntrance {
        0% {
            opacity: 0;
            transform: translateY(50px) rotateX(-30deg);
        }
        50% {
            opacity: 0.5;
            transform: translateY(25px) rotateX(-15deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) rotateX(0);
        }
    }

    .metric-card:hover, .content-container:hover, .chart-container:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.12);
    }

    /* 数值样式 */
    .metric-value {
        font-size: 2.8rem !important;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: visible !important;
        display: inline-block;
        min-width: 100%;
        animation: numberCount 2s ease-out;
    }

    /* 数字滚动动画 */
    @keyframes numberCount {
        0% {
            opacity: 0;
            transform: translateY(50px) scale(0.5);
            filter: blur(10px);
        }
        50% {
            opacity: 0.5;
            filter: blur(5px);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }

    .metric-label {
        color: #374151 !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        animation: labelFade 1.5s ease-out 0.5s both;
    }

    @keyframes labelFade {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .metric-description {
        color: #6b7280 !important;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        font-weight: 500;
        font-style: italic;
        animation: labelFade 1.5s ease-out 0.7s both;
    }

    /* 图表标题样式 */
    .chart-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #333 !important;
        margin-bottom: 1.5rem;
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 洞察框样式 */
    .insight-box {
        border-left: 4px solid #667eea;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .insight-title {
        font-weight: 700;
        color: #333 !important;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }

    .insight-content {
        color: #666 !important;
        line-height: 1.6;
        font-size: 1rem;
    }

    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(248, 250, 252, 0.95) !important;
        padding: 1rem;
        border-radius: 20px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 35px;
        background: rgba(255,255,255,0.95) !important;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        color: #333 !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }

    /* Plotly 图表圆角样式 */
    .js-plotly-plot {
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
    }

    /* 准确率等级颜色 */
    .accuracy-excellent { border-left-color: #00FF00 !important; }
    .accuracy-good { border-left-color: #90EE90 !important; }
    .accuracy-medium { border-left-color: #FFA500 !important; }
    .accuracy-low { border-left-color: #FF6347 !important; }
    .accuracy-poor { border-left-color: #FF0000 !important; }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value { font-size: 2.2rem !important; }
        .metric-card { padding: 2rem 1.5rem; }
        .page-header { padding: 2rem 1rem; }
        .page-title { font-size: 2.5rem; }
    }

    /* 加载动画初始状态 */
    .metric-card {
        opacity: 0;
        animation: cardLoadIn 0.8s ease-out forwards;
    }

    @keyframes cardLoadIn {
        0% {
            opacity: 0;
            transform: translateY(50px) scale(0.8);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* 渐进式加载动画 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)

# 配色方案
COLOR_SCHEME = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'excellent': '#00FF00',
    'good': '#90EE90',
    'medium': '#FFA500',
    'low': '#FF6347',
    'poor': '#FF0000',
    'chart_colors': ['#667eea', '#ff6b9d', '#c44569', '#ffc75f', '#f8b500', '#845ec2', '#4e8397', '#00c9a7']
}

# 数据加载函数
@st.cache_data
def load_and_process_data():
    """加载和处理预测数据"""
    try:
        # 读取数据文件
        df = pd.read_excel('预测与销量记录数据仪表盘.xlsx')
        
        # 转换月份为日期格式
        df['月份'] = pd.to_datetime(df['月份'])
        
        # 计算准确率
        df['准确率'] = 1 - np.abs(df['预测销量'] - df['实际销量']) / np.maximum(df['实际销量'], 1)
        df['准确率'] = df['准确率'].clip(0, 1)
        
        # 计算加权准确率（近期数据权重更高）
        df['权重'] = 1.0
        max_date = df['月份'].max()
        for i in range(6):
            date_threshold = max_date - pd.DateOffset(months=i)
            df.loc[df['月份'] >= date_threshold, '权重'] = 1 + (5-i) * 0.2
        
        return df
        
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame()

def calculate_accuracy_metrics(df, product=None, recent_months=None):
    """计算准确率指标"""
    if df.empty:
        return {
            'avg_accuracy': 0,
            'weighted_accuracy': 0,
            'trend': 0,
            'product_count': 0
        }
    
    # 筛选数据
    filtered_df = df.copy()
    if product:
        filtered_df = filtered_df[filtered_df['产品简称'] == product]
    if recent_months:
        max_date = df['月份'].max()
        date_threshold = max_date - pd.DateOffset(months=recent_months)
        filtered_df = filtered_df[filtered_df['月份'] >= date_threshold]
    
    if filtered_df.empty:
        return {
            'avg_accuracy': 0,
            'weighted_accuracy': 0,
            'trend': 0,
            'product_count': 0
        }
    
    # 计算平均准确率
    avg_accuracy = filtered_df['准确率'].mean()
    
    # 计算加权准确率
    weighted_accuracy = np.average(filtered_df['准确率'], weights=filtered_df['权重'])
    
    # 计算趋势
    if len(filtered_df) > 1:
        # 使用最近3个月和之前3个月对比
        sorted_df = filtered_df.sort_values('月份')
        mid_point = len(sorted_df) // 2
        recent_acc = sorted_df.iloc[mid_point:]['准确率'].mean()
        past_acc = sorted_df.iloc[:mid_point]['准确率'].mean()
        trend = recent_acc - past_acc
    else:
        trend = 0
    
    return {
        'avg_accuracy': avg_accuracy,
        'weighted_accuracy': weighted_accuracy,
        'trend': trend,
        'product_count': filtered_df['产品简称'].nunique()
    }

def create_accuracy_overview_chart(df):
    """创建准确率总览图表"""
    try:
        # 按月份计算整体准确率
        monthly_accuracy = df.groupby('月份').apply(
            lambda x: pd.Series({
                '平均准确率': x['准确率'].mean(),
                '加权准确率': np.average(x['准确率'], weights=x['权重'])
            })
        ).reset_index()
        
        # 创建图表
        fig = go.Figure()
        
        # 添加平均准确率线
        fig.add_trace(go.Scatter(
            x=monthly_accuracy['月份'],
            y=monthly_accuracy['平均准确率'] * 100,
            mode='lines+markers',
            name='平均准确率',
            line=dict(color=COLOR_SCHEME['primary'], width=3),
            marker=dict(size=10),
            hovertemplate="<b>%{x|%Y-%m}</b><br>" +
                          "平均准确率: %{y:.1f}%<br>" +
                          "<extra></extra>"
        ))
        
        # 添加加权准确率线
        fig.add_trace(go.Scatter(
            x=monthly_accuracy['月份'],
            y=monthly_accuracy['加权准确率'] * 100,
            mode='lines+markers',
            name='加权准确率',
            line=dict(color=COLOR_SCHEME['secondary'], width=3, dash='dash'),
            marker=dict(size=10),
            hovertemplate="<b>%{x|%Y-%m}</b><br>" +
                          "加权准确率: %{y:.1f}%<br>" +
                          "<extra></extra>"
        ))
        
        # 添加85%目标线
        fig.add_hline(
            y=85, 
            line_dash="dot", 
            line_color="gray",
            annotation_text="目标准确率: 85%",
            annotation_position="right"
        )
        
        # 添加注释说明两种准确率的区别
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref='paper',
            yref='paper',
            text="""
            <b>📊 准确率说明</b><br>
            <b>平均准确率</b>: 所有预测的简单算术平均<br>
            <b>加权准确率</b>: 近期数据权重更高，更能反映当前预测水平
            """,
            showarrow=False,
            align='left',
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11)
        )
        
        fig.update_layout(
            title="预测准确率趋势分析",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            height=500,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"准确率总览图表创建失败: {str(e)}")
        return go.Figure()

def create_product_accuracy_chart(df):
    """创建产品准确率对比图表"""
    try:
        # 计算每个产品的准确率指标
        product_metrics = []
        for product in df['产品简称'].unique():
            metrics = calculate_accuracy_metrics(df, product=product)
            product_metrics.append({
                '产品简称': product,
                '平均准确率': metrics['avg_accuracy'] * 100,
                '加权准确率': metrics['weighted_accuracy'] * 100,
                '趋势': metrics['trend'] * 100
            })
        
        product_df = pd.DataFrame(product_metrics)
        product_df = product_df.sort_values('加权准确率', ascending=False)
        
        # 创建图表
        fig = go.Figure()
        
        # 添加加权准确率条形图
        fig.add_trace(go.Bar(
            x=product_df['产品简称'],
            y=product_df['加权准确率'],
            name='加权准确率',
            marker=dict(
                color=product_df['加权准确率'],
                colorscale='RdYlGn',
                cmin=60,
                cmax=100,
                colorbar=dict(
                    title="准确率(%)",
                    x=1.02
                )
            ),
            text=product_df['加权准确率'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>" +
                          "加权准确率: %{y:.1f}%<br>" +
                          "平均准确率: %{customdata[0]:.1f}%<br>" +
                          "趋势: %{customdata[1]:+.1f}%<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                product_df['平均准确率'],
                product_df['趋势']
            ))
        ))
        
        # 添加趋势指示器
        for i, row in product_df.iterrows():
            if abs(row['趋势']) > 0.1:
                fig.add_annotation(
                    x=row['产品简称'],
                    y=row['加权准确率'] + 2,
                    text='📈' if row['趋势'] > 0 else '📉',
                    showarrow=False,
                    font=dict(size=20)
                )
        
        fig.update_layout(
            title="产品预测准确率排行榜<br><sub>加权准确率 = 近期预测权重更高</sub>",
            xaxis_title="产品",
            yaxis_title="准确率 (%)",
            height=600,
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig
        
    except Exception as e:
        st.error(f"产品准确率图表创建失败: {str(e)}")
        return go.Figure()

def create_accuracy_distribution_chart(df):
    """创建准确率分布图表"""
    try:
        # 计算每个产品的平均准确率
        product_accuracy = df.groupby('产品简称')['准确率'].mean() * 100
        
        # 定义准确率区间
        bins = [0, 70, 80, 85, 90, 95, 100]
        labels = ['<70%', '70-80%', '80-85%', '85-90%', '90-95%', '>95%']
        
        # 统计各区间产品数量
        accuracy_dist = pd.cut(product_accuracy, bins=bins, labels=labels, include_lowest=True)
        dist_counts = accuracy_dist.value_counts().sort_index()
        
        # 计算累计百分比
        total_products = len(product_accuracy)
        cumulative_pct = (dist_counts.cumsum() / total_products * 100).round(1)
        
        # 创建组合图
        fig = make_subplots(
            specs=[[{"secondary_y": True}]]
        )
        
        # 添加柱状图
        fig.add_trace(
            go.Bar(
                x=dist_counts.index,
                y=dist_counts.values,
                name='产品数量',
                marker=dict(
                    color=['#FF0000', '#FF6347', '#FFA500', '#90EE90', '#00FF00', '#006400'],
                    opacity=0.8
                ),
                text=dist_counts.values,
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>" +
                              "产品数量: %{y}个<br>" +
                              "占比: %{customdata:.1f}%<br>" +
                              "<extra></extra>",
                customdata=dist_counts.values / total_products * 100
            ),
            secondary_y=False
        )
        
        # 添加累计百分比线
        fig.add_trace(
            go.Scatter(
                x=cumulative_pct.index,
                y=cumulative_pct.values,
                mode='lines+markers+text',
                name='累计占比',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10),
                text=[f"{x:.1f}%" for x in cumulative_pct.values],
                textposition='top center',
                hovertemplate="<b>%{x}</b><br>" +
                              "累计占比: %{y:.1f}%<br>" +
                              "<extra></extra>"
            ),
            secondary_y=True
        )
        
        # 计算准确率>85%的产品占比
        high_accuracy_count = dist_counts[['85-90%', '90-95%', '>95%']].sum()
        high_accuracy_pct = high_accuracy_count / total_products * 100
        
        # 添加统计信息
        fig.add_annotation(
            x=0.98,
            y=0.98,
            xref='paper',
            yref='paper',
            text=f"""
            <b>📊 统计汇总</b><br>
            总产品数: {total_products}个<br>
            准确率>85%: {high_accuracy_count}个<br>
            占比: <b style="color: {'green' if high_accuracy_pct > 50 else 'orange'};">{high_accuracy_pct:.1f}%</b>
            """,
            showarrow=False,
            align='right',
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=12)
        )
        
        fig.update_xaxes(title_text="准确率区间")
        fig.update_yaxes(title_text="产品数量", secondary_y=False)
        fig.update_yaxes(title_text="累计占比 (%)", secondary_y=True)
        
        fig.update_layout(
            title="产品预测准确率分布<br><sub>各准确率区间的产品数量统计</sub>",
            height=500,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"准确率分布图表创建失败: {str(e)}")
        return go.Figure()

def create_model_performance_chart(df):
    """创建模型性能趋势图表"""
    try:
        # 获取所有产品列表
        products = df['产品简称'].unique()
        
        # 创建子图
        rows = (len(products) + 2) // 3
        fig = make_subplots(
            rows=rows, 
            cols=3,
            subplot_titles=products,
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # 为每个产品创建趋势图
        for idx, product in enumerate(products):
            row = idx // 3 + 1
            col = idx % 3 + 1
            
            product_data = df[df['产品简称'] == product].sort_values('月份')
            
            # 添加准确率趋势线
            fig.add_trace(
                go.Scatter(
                    x=product_data['月份'],
                    y=product_data['准确率'] * 100,
                    mode='lines+markers',
                    name=product,
                    line=dict(width=2),
                    marker=dict(size=8),
                    showlegend=False,
                    hovertemplate="<b>%{x|%Y-%m}</b><br>" +
                                  "准确率: %{y:.1f}%<br>" +
                                  "实际: %{customdata[0]}<br>" +
                                  "预测: %{customdata[1]}<br>" +
                                  "模型: %{customdata[2]}<br>" +
                                  "<extra></extra>",
                    customdata=np.column_stack((
                        product_data['实际销量'],
                        product_data['预测销量'],
                        product_data['选择模型']
                    ))
                ),
                row=row, col=col
            )
            
            # 添加85%目标线
            fig.add_hline(
                y=85, 
                line_dash="dot", 
                line_color="gray",
                opacity=0.5,
                row=row, col=col
            )
            
            # 计算趋势
            if len(product_data) > 1:
                recent_acc = product_data.tail(3)['准确率'].mean() * 100
                past_acc = product_data.head(3)['准确率'].mean() * 100
                trend = recent_acc - past_acc
                
                # 添加趋势标记
                fig.add_annotation(
                    x=product_data['月份'].iloc[-1],
                    y=product_data['准确率'].iloc[-1] * 100 + 5,
                    text='📈' if trend > 5 else '📉' if trend < -5 else '➡️',
                    showarrow=False,
                    font=dict(size=16),
                    row=row, col=col
                )
        
        fig.update_layout(
            title="产品预测准确率趋势变化<br><sub>各产品历史准确率走势及趋势</sub>",
            height=300 * rows,
            showlegend=False,
            hovermode='closest'
        )
        
        # 更新所有子图的y轴范围
        fig.update_yaxes(range=[0, 105])
        
        return fig
        
    except Exception as e:
        st.error(f"模型性能图表创建失败: {str(e)}")
        return go.Figure()

def create_model_selection_analysis(df):
    """创建模型选择分析图表"""
    try:
        # 统计各模型被选择的次数和准确率
        model_stats = df.groupby('选择模型').agg({
            '准确率': ['mean', 'count']
        }).reset_index()
        model_stats.columns = ['模型', '平均准确率', '选择次数']
        model_stats['平均准确率'] = model_stats['平均准确率'] * 100
        model_stats = model_stats.sort_values('选择次数', ascending=False)
        
        # 创建图表
        fig = go.Figure()
        
        # 添加散点图
        fig.add_trace(go.Scatter(
            x=model_stats['选择次数'],
            y=model_stats['平均准确率'],
            mode='markers+text',
            marker=dict(
                size=model_stats['选择次数'] * 2,
                color=model_stats['平均准确率'],
                colorscale='RdYlGn',
                cmin=70,
                cmax=90,
                showscale=True,
                colorbar=dict(title="平均准确率(%)")
            ),
            text=model_stats['模型'],
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>" +
                          "选择次数: %{x}<br>" +
                          "平均准确率: %{y:.1f}%<br>" +
                          "<extra></extra>"
        ))
        
        # 添加参考线
        fig.add_hline(y=85, line_dash="dash", line_color="gray", 
                      annotation_text="目标准确率: 85%")
        
        fig.update_layout(
            title="模型选择频率与准确率分析<br><sub>气泡大小表示选择频率</sub>",
            xaxis_title="被选择次数",
            yaxis_title="平均准确率 (%)",
            height=600,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"模型选择分析图表创建失败: {str(e)}")
        return go.Figure()

# 加载数据
with st.spinner('🔄 正在加载数据...'):
    df = load_and_process_data()

# 页面标题
st.markdown("""
<div class="page-header">
    <h1 class="page-title">🤖 智能预测分析系统</h1>
    <p class="page-subtitle">基于机器学习的销售预测准确性分析与优化平台</p>
</div>
""", unsafe_allow_html=True)

# 计算关键指标
if not df.empty:
    # 整体指标
    overall_metrics = calculate_accuracy_metrics(df)
    
    # 最近一个月指标
    recent_metrics = calculate_accuracy_metrics(df, recent_months=1)
    
    # 准确率>85%的产品统计
    product_accuracy = df.groupby('产品简称')['准确率'].mean()
    high_accuracy_products = (product_accuracy > 0.85).sum()
    high_accuracy_ratio = high_accuracy_products / len(product_accuracy) * 100
else:
    overall_metrics = {'avg_accuracy': 0, 'weighted_accuracy': 0, 'trend': 0, 'product_count': 0}
    recent_metrics = {'avg_accuracy': 0, 'weighted_accuracy': 0, 'trend': 0, 'product_count': 0}
    high_accuracy_products = 0
    high_accuracy_ratio = 0

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 核心指标总览",
    "📈 准确率趋势分析", 
    "🎯 产品准确率对比",
    "📊 准确率分布统计",
    "🔬 模型性能分析"
])

# 标签1：核心指标总览
with tab1:
    st.markdown("### 🎯 预测准确性核心指标")
    
    # 第一行：整体指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        accuracy_class = "accuracy-excellent" if overall_metrics['avg_accuracy'] > 0.85 else \
                        "accuracy-good" if overall_metrics['avg_accuracy'] > 0.8 else \
                        "accuracy-medium" if overall_metrics['avg_accuracy'] > 0.7 else "accuracy-low"
        st.markdown(f"""
        <div class="metric-card {accuracy_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{overall_metrics['avg_accuracy']*100:.1f}%</div>
                <div class="metric-label">📊 整体平均准确率</div>
                <div class="metric-description">所有预测的算术平均</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card {accuracy_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{overall_metrics['weighted_accuracy']*100:.1f}%</div>
                <div class="metric-label">⚖️ 整体加权准确率</div>
                <div class="metric-description">近期数据权重更高</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{overall_metrics['product_count']}</div>
                <div class="metric-label">📦 产品总数</div>
                <div class="metric-description">参与预测的产品数量</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ratio_class = "accuracy-excellent" if high_accuracy_ratio > 60 else \
                     "accuracy-good" if high_accuracy_ratio > 40 else \
                     "accuracy-medium" if high_accuracy_ratio > 20 else "accuracy-low"
        st.markdown(f"""
        <div class="metric-card {ratio_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{high_accuracy_ratio:.1f}%</div>
                <div class="metric-label">🎯 高准确率产品占比</div>
                <div class="metric-description">准确率>85%的产品</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 第二行：最近一个月指标
    st.markdown("### 📅 最近一个月预测表现")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        recent_class = "accuracy-excellent" if recent_metrics['avg_accuracy'] > 0.85 else \
                      "accuracy-good" if recent_metrics['avg_accuracy'] > 0.8 else \
                      "accuracy-medium" if recent_metrics['avg_accuracy'] > 0.7 else "accuracy-low"
        st.markdown(f"""
        <div class="metric-card {recent_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{recent_metrics['avg_accuracy']*100:.1f}%</div>
                <div class="metric-label">📊 近期平均准确率</div>
                <div class="metric-description">最近一个月表现</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="metric-card {recent_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{recent_metrics['weighted_accuracy']*100:.1f}%</div>
                <div class="metric-label">⚖️ 近期加权准确率</div>
                <div class="metric-description">最近一个月加权</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        trend = overall_metrics['trend'] * 100
        trend_class = "accuracy-excellent" if trend > 5 else \
                     "accuracy-good" if trend > 0 else \
                     "accuracy-medium" if trend > -5 else "accuracy-low"
        trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
        st.markdown(f"""
        <div class="metric-card {trend_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{trend:+.1f}%</div>
                <div class="metric-label">{trend_icon} 准确率趋势</div>
                <div class="metric-description">{'改善中' if trend > 0 else '下降中' if trend < 0 else '持平'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        # 计算最常用的模型
        if not df.empty:
            most_used_model = df['选择模型'].value_counts().index[0]
            model_count = df['选择模型'].value_counts().iloc[0]
        else:
            most_used_model = "无数据"
            model_count = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value" style="font-size: 1.8rem !important;">{most_used_model}</div>
                <div class="metric-label">🏆 最常用模型</div>
                <div class="metric-description">使用{model_count}次</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 洞察总结
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 智能洞察与建议</div>
        <div class="insight-content">
            • <b>整体表现:</b> 预测系统整体准确率{overall_metrics['avg_accuracy']*100:.1f}%，
            {'已达到优秀水平(>85%)' if overall_metrics['avg_accuracy'] > 0.85 else 
             '达到良好水平(>80%)' if overall_metrics['avg_accuracy'] > 0.8 else
             '有待提升'}<br>
            • <b>加权vs平均:</b> 加权准确率
            {'高于' if overall_metrics['weighted_accuracy'] > overall_metrics['avg_accuracy'] else '低于'}
            平均准确率{abs(overall_metrics['weighted_accuracy'] - overall_metrics['avg_accuracy'])*100:.1f}%，
            说明近期预测{'有所改善' if overall_metrics['weighted_accuracy'] > overall_metrics['avg_accuracy'] else '有所下降'}<br>
            • <b>产品覆盖:</b> {high_accuracy_products}个产品达到85%以上准确率，占比{high_accuracy_ratio:.1f}%<br>
            • <b>趋势分析:</b> 整体准确率趋势{trend:+.1f}%，
            {'持续改善中' if trend > 5 else '基本稳定' if abs(trend) <= 5 else '需要关注下降趋势'}<br>
            • <b>改进建议:</b> 
            {'继续保持当前预测策略' if overall_metrics['avg_accuracy'] > 0.85 else
             '重点关注低准确率产品，优化预测模型' if overall_metrics['avg_accuracy'] > 0.75 else
             '建议全面审查预测方法，考虑引入新的预测模型'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 标签2：准确率趋势分析
with tab2:
    st.markdown("### 📈 预测准确率趋势分析")
    
    if not df.empty:
        # 创建准确率总览图表
        overview_fig = create_accuracy_overview_chart(df)
        st.plotly_chart(overview_fig, use_container_width=True)
        
        # 月度统计
        st.markdown("#### 📊 月度准确率统计")
        monthly_stats = df.groupby(df['月份'].dt.to_period('M')).agg({
            '准确率': ['mean', 'std', 'count']
        }).round(3)
        monthly_stats.columns = ['平均准确率', '标准差', '预测数量']
        monthly_stats['平均准确率'] = (monthly_stats['平均准确率'] * 100).round(1)
        monthly_stats['标准差'] = (monthly_stats['标准差'] * 100).round(1)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(
                monthly_stats.tail(6),
                use_container_width=True
            )
        with col2:
            latest_month = monthly_stats.index[-1]
            st.metric(
                "最新月份",
                str(latest_month),
                f"{monthly_stats.iloc[-1]['平均准确率']}%"
            )
            st.metric(
                "月度最佳",
                str(monthly_stats['平均准确率'].idxmax()),
                f"{monthly_stats['平均准确率'].max()}%"
            )
    else:
        st.warning("暂无数据可供分析")

# 标签3：产品准确率对比
with tab3:
    st.markdown("### 🎯 产品预测准确率对比分析")
    
    if not df.empty:
        # 创建产品准确率图表
        product_fig = create_product_accuracy_chart(df)
        st.plotly_chart(product_fig, use_container_width=True)
        
        # 产品详细统计表
        st.markdown("#### 📋 产品准确率详细统计")
        
        product_stats = []
        for product in df['产品简称'].unique():
            metrics = calculate_accuracy_metrics(df, product=product)
            recent_metrics = calculate_accuracy_metrics(df, product=product, recent_months=3)
            
            product_stats.append({
                '产品简称': product,
                '历史平均准确率': f"{metrics['avg_accuracy']*100:.1f}%",
                '历史加权准确率': f"{metrics['weighted_accuracy']*100:.1f}%",
                '近3月平均准确率': f"{recent_metrics['avg_accuracy']*100:.1f}%",
                '近3月加权准确率': f"{recent_metrics['weighted_accuracy']*100:.1f}%",
                '准确率趋势': '📈' if metrics['trend'] > 0.05 else '📉' if metrics['trend'] < -0.05 else '➡️',
                '预测次数': df[df['产品简称'] == product].shape[0]
            })
        
        product_stats_df = pd.DataFrame(product_stats)
        product_stats_df = product_stats_df.sort_values('历史加权准确率', ascending=False)
        
        st.dataframe(
            product_stats_df,
            use_container_width=True,
            height=400
        )
        
        # 下载按钮
        csv = product_stats_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载产品准确率统计",
            data=csv,
            file_name=f"产品准确率统计_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无数据可供分析")

# 标签4：准确率分布统计
with tab4:
    st.markdown("### 📊 准确率分布统计分析")
    
    if not df.empty:
        # 创建准确率分布图表
        dist_fig = create_accuracy_distribution_chart(df)
        st.plotly_chart(dist_fig, use_container_width=True)
        
        # 详细分布统计
        st.markdown("#### 📈 准确率分布详情")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card accuracy-excellent">
                <div class="metric-card-inner">
                    <div class="metric-value">{:.1f}%</div>
                    <div class="metric-label">🎯 优秀(>90%)</div>
                    <div class="metric-description">预测非常准确</div>
                </div>
            </div>
            """.format((product_accuracy > 0.9).sum() / len(product_accuracy) * 100), 
            unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card accuracy-good">
                <div class="metric-card-inner">
                    <div class="metric-value">{:.1f}%</div>
                    <div class="metric-label">✅ 良好(80-90%)</div>
                    <div class="metric-description">预测较为准确</div>
                </div>
            </div>
            """.format(((product_accuracy >= 0.8) & (product_accuracy <= 0.9)).sum() / len(product_accuracy) * 100), 
            unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card accuracy-low">
                <div class="metric-card-inner">
                    <div class="metric-value">{:.1f}%</div>
                    <div class="metric-label">⚠️ 待改进(<80%)</div>
                    <div class="metric-description">需要优化模型</div>
                </div>
            </div>
            """.format((product_accuracy < 0.8).sum() / len(product_accuracy) * 100), 
            unsafe_allow_html=True)
        
        # 准确率分位数统计
        st.markdown("#### 📊 准确率分位数统计")
        quantiles = product_accuracy.quantile([0.25, 0.5, 0.75]).round(3)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("最低准确率", f"{product_accuracy.min()*100:.1f}%")
        with col2:
            st.metric("25%分位数", f"{quantiles[0.25]*100:.1f}%")
        with col3:
            st.metric("中位数", f"{quantiles[0.5]*100:.1f}%")
        with col4:
            st.metric("75%分位数", f"{quantiles[0.75]*100:.1f}%")
    else:
        st.warning("暂无数据可供分析")

# 标签5：模型性能分析
with tab5:
    st.markdown("### 🔬 模型性能深度分析")
    
    if not df.empty:
        # 创建模型性能趋势图
        st.markdown("#### 📈 产品准确率趋势变化")
        performance_fig = create_model_performance_chart(df)
        st.plotly_chart(performance_fig, use_container_width=True)
        
        # 模型选择分析
        st.markdown("#### 🎯 模型选择与性能分析")
        model_fig = create_model_selection_analysis(df)
        st.plotly_chart(model_fig, use_container_width=True)
        
        # 模型性能对比表
        st.markdown("#### 📊 各模型性能对比")
        
        model_performance = df.groupby('选择模型').agg({
            '准确率': ['mean', 'std', 'count'],
            '产品简称': 'nunique'
        }).round(3)
        
        model_performance.columns = ['平均准确率', '准确率标准差', '使用次数', '覆盖产品数']
        model_performance['平均准确率'] = (model_performance['平均准确率'] * 100).round(1)
        model_performance['准确率标准差'] = (model_performance['准确率标准差'] * 100).round(1)
        model_performance = model_performance.sort_values('平均准确率', ascending=False)
        
        st.dataframe(
            model_performance,
            use_container_width=True
        )
        
        # 模型选择洞察
        best_model = model_performance.index[0]
        best_accuracy = model_performance.iloc[0]['平均准确率']
        most_used_model = model_performance.sort_values('使用次数', ascending=False).index[0]
        
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">🔍 模型选择洞察</div>
            <div class="insight-content">
                • <b>最佳性能模型:</b> {best_model}，平均准确率{best_accuracy}%<br>
                • <b>最常使用模型:</b> {most_used_model}，使用{model_performance.loc[most_used_model, '使用次数']}次<br>
                • <b>模型多样性:</b> 系统共使用{len(model_performance)}种不同模型进行预测<br>
                • <b>优化建议:</b> 
                {'当前模型选择策略良好' if best_model == most_used_model else 
                 f'考虑更多使用{best_model}模型以提升整体准确率'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("暂无数据可供分析")

# 页脚
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: rgba(102, 126, 234, 0.8); font-family: 'Inter', sans-serif; font-size: 0.9rem; margin-top: 2rem; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
        🤖 Powered by Machine Learning & Streamlit | 智能预测分析平台 | 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """,
    unsafe_allow_html=True
)
