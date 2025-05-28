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

# 统一的增强CSS样式 - 修复版
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

    /* 主容器背景 - 确保不透明 */
    .main .block-container {
        background: rgba(255,255,255,1) !important;
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

    /* 统一的卡片容器样式 - 确保背景不透明 */
    .metric-card, .content-container, .chart-container, .insight-box {
        background: white !important;
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
        overflow: hidden !important;
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

    /* 数值样式 - 调整字体大小避免溢出 */
    .metric-value {
        font-size: 2.2rem !important;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden !important;
        text-overflow: ellipsis;
        display: inline-block;
        max-width: 100%;
        padding: 0 0.5rem;
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

    /* 洞察框样式 - 确保背景不透明 */
    .insight-box {
        background: white !important;
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

    /* 标签页样式增强 - 修复布局问题 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(248, 250, 252, 1) !important;
        padding: 0.8rem;
        border-radius: 20px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
    }

    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 0 25px;
        background: white !important;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        color: #333 !important;
        white-space: nowrap;
        flex: 0 1 auto;
        margin-bottom: 0.5rem;
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
        background: white !important;
    }

    /* 准确率等级颜色 */
    .accuracy-excellent { border-left-color: #00FF00 !important; }
    .accuracy-good { border-left-color: #90EE90 !important; }
    .accuracy-medium { border-left-color: #FFA500 !important; }
    .accuracy-low { border-left-color: #FF6347 !important; }
    .accuracy-poor { border-left-color: #FF0000 !important; }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value { font-size: 1.8rem !important; }
        .metric-card { padding: 1.5rem 1rem; }
        .page-header { padding: 2rem 1rem; }
        .page-title { font-size: 2.2rem; }
        .stTabs [data-baseweb="tab"] { 
            padding: 0 15px; 
            font-size: 0.85rem;
            height: 45px;
        }
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

    /* 确保所有文字在白色背景上清晰可见 */
    div[class*="metric"] {
        background: white !important;
    }
    
    /* 修复注释框背景 */
    div[class*="annotation"] {
        background: rgba(255,255,255,0.98) !important;
    }
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
        
        # 过滤掉实际销量为0或空的记录
        df_valid = df[(df['实际销量'].notna()) & (df['实际销量'] > 0)].copy()
        
        # 计算单月准确率
        df_valid['准确率'] = 1 - np.abs(df_valid['预测销量'] - df_valid['实际销量']) / df_valid['实际销量']
        df_valid['准确率'] = df_valid['准确率'].clip(0, 1)
        
        # 添加准确率计算详情
        df_valid['计算详情'] = df_valid.apply(lambda row: 
            f"准确率 = 1 - |预测({row['预测销量']:.0f}) - 实际({row['实际销量']:.0f})| / 实际({row['实际销量']:.0f}) = {row['准确率']:.2%}",
            axis=1
        )
        
        return df, df_valid
        
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def calculate_metrics(df_valid):
    """计算所有关键指标 - 修正版"""
    if df_valid.empty:
        return {
            'overall_avg_accuracy': 0,
            'overall_weighted_accuracy': 0,
            'recent_accuracy': 0,
            'recent_month': None,
            'total_products': 0,
            'high_accuracy_products': 0,
            'high_accuracy_ratio': 0,
            'most_used_model': 'N/A',
            'model_count': 0,
            'product_metrics': pd.DataFrame(),
            'products_with_records': 0,
            'high_accuracy_count': 0,
            'medium_accuracy_count': 0,
            'low_accuracy_count': 0,
            'trend': 0
        }
    
    try:
        # 1. 整体平均准确率：每个产品的历史平均，再求平均
        product_avg_accuracy = df_valid.groupby('产品简称')['准确率'].mean()
        overall_avg_accuracy = product_avg_accuracy.mean()
        
        # 2. 加权整体准确率：只考虑最近3个月，基于销量加权
        recent_3months = df_valid['月份'].max() - pd.DateOffset(months=2)
        df_recent_3months = df_valid[df_valid['月份'] >= recent_3months]
        
        if not df_recent_3months.empty:
            # 先计算每个产品在最近3个月的平均准确率和平均销量
            product_recent = df_recent_3months.groupby('产品简称').agg({
                '准确率': 'mean',
                '实际销量': 'mean'
            }).reset_index()
            
            # 计算加权平均
            total_weighted = np.sum(product_recent['准确率'] * product_recent['实际销量'])
            total_sales = product_recent['实际销量'].sum()
            overall_weighted_accuracy = total_weighted / total_sales if total_sales > 0 else 0
        else:
            overall_weighted_accuracy = 0
        
        # 3. 最近准确率：每个产品最近一次的预测
        latest_records = df_valid.sort_values('月份').groupby('产品简称').last()
        recent_accuracy = latest_records['准确率'].mean()
        recent_month = df_valid['月份'].max()
        
        # 4. 产品统计
        total_products = len(product_avg_accuracy)
        products_with_records = total_products
        
        # 5. 准确率分布统计（基于产品的历史平均）
        high_accuracy_count = (product_avg_accuracy > 0.8).sum()
        medium_accuracy_count = ((product_avg_accuracy >= 0.6) & (product_avg_accuracy <= 0.8)).sum()
        low_accuracy_count = (product_avg_accuracy < 0.6).sum()
        
        # 6. 高准确率产品占比 (>85%)
        high_accuracy_products = (product_avg_accuracy > 0.85).sum()
        high_accuracy_ratio = high_accuracy_products / total_products * 100 if total_products > 0 else 0
        
        # 7. 最常用模型
        model_counts = df_valid['选择模型'].value_counts()
        most_used_model = model_counts.index[0] if len(model_counts) > 0 else 'N/A'
        model_count = model_counts.iloc[0] if len(model_counts) > 0 else 0
        
        # 8. 准确率趋势
        trend = (recent_accuracy - overall_avg_accuracy) * 100
        
        # 9. 创建产品指标汇总
        product_metrics = pd.DataFrame({
            '产品简称': product_avg_accuracy.index,
            '平均准确率': product_avg_accuracy.values,
            '平均销量': df_valid.groupby('产品简称')['实际销量'].mean().values,
            '常用模型': df_valid.groupby('产品简称')['选择模型'].agg(lambda x: x.mode()[0] if len(x) > 0 else 'N/A').values
        })
        
        # 添加加权准确率
        product_weighted = df_valid.groupby('产品简称').apply(
            lambda x: np.average(x['准确率'], weights=x['实际销量'])
        ).reset_index(name='加权准确率')
        product_metrics = product_metrics.merge(product_weighted, on='产品简称')
        
        return {
            'overall_avg_accuracy': overall_avg_accuracy,
            'overall_weighted_accuracy': overall_weighted_accuracy,
            'recent_accuracy': recent_accuracy,
            'recent_month': recent_month,
            'total_products': total_products,
            'high_accuracy_products': high_accuracy_products,
            'high_accuracy_ratio': high_accuracy_ratio,
            'most_used_model': most_used_model,
            'model_count': model_count,
            'product_metrics': product_metrics,
            'products_with_records': products_with_records,
            'high_accuracy_count': high_accuracy_count,
            'medium_accuracy_count': medium_accuracy_count,
            'low_accuracy_count': low_accuracy_count,
            'trend': trend
        }
    except Exception as e:
        st.error(f"指标计算失败: {str(e)}")
        return {
            'overall_avg_accuracy': 0,
            'overall_weighted_accuracy': 0,
            'recent_accuracy': 0,
            'recent_month': None,
            'total_products': 0,
            'high_accuracy_products': 0,
            'high_accuracy_ratio': 0,
            'most_used_model': 'N/A',
            'model_count': 0,
            'product_metrics': pd.DataFrame(),
            'products_with_records': 0,
            'high_accuracy_count': 0,
            'medium_accuracy_count': 0,
            'low_accuracy_count': 0,
            'trend': 0
        }

def create_accuracy_trend_chart(df_valid):
    """创建准确率趋势图表"""
    try:
        # 按月份计算准确率
        monthly_stats = df_valid.groupby('月份').agg({
            '准确率': 'mean',
            '实际销量': 'sum',
            '预测销量': 'sum'
        }).reset_index()
        
        # 计算加权准确率
        monthly_product_stats = df_valid.groupby(['月份', '产品简称']).agg({
            '准确率': 'mean',
            '实际销量': 'mean',
            '预测销量': 'mean'
        }).reset_index()
        
        monthly_weighted = monthly_product_stats.groupby('月份').apply(
            lambda x: np.average(x['准确率'], weights=x['实际销量'])
        ).reset_index(name='加权准确率')
        
        monthly_stats = monthly_stats.merge(monthly_weighted, on='月份')
        
        # 创建图表
        fig = go.Figure()
        
        # 平均准确率线
        fig.add_trace(go.Scatter(
            x=monthly_stats['月份'],
            y=monthly_stats['准确率'] * 100,
            mode='lines+markers',
            name='平均准确率',
            line=dict(color=COLOR_SCHEME['primary'], width=3),
            marker=dict(size=10),
            customdata=np.column_stack((
                monthly_stats['实际销量'],
                monthly_stats['预测销量'],
                monthly_stats['准确率'] * 100
            )),
            hovertemplate="<b>%{x|%Y-%m}</b><br>" +
                          "平均准确率: %{y:.1f}%<br>" +
                          "总实际销量: %{customdata[0]:.0f}箱<br>" +
                          "总预测销量: %{customdata[1]:.0f}箱<br>" +
                          "计算: 所有产品准确率的算术平均<br>" +
                          "<extra></extra>"
        ))
        
        # 加权准确率线
        fig.add_trace(go.Scatter(
            x=monthly_stats['月份'],
            y=monthly_stats['加权准确率'] * 100,
            mode='lines+markers',
            name='加权准确率',
            line=dict(color=COLOR_SCHEME['secondary'], width=3, dash='dash'),
            marker=dict(size=10),
            customdata=np.column_stack((
                monthly_stats['实际销量'],
                monthly_stats['预测销量'],
                monthly_stats['加权准确率'] * 100
            )),
            hovertemplate="<b>%{x|%Y-%m}</b><br>" +
                          "加权准确率: %{y:.1f}%<br>" +
                          "总实际销量: %{customdata[0]:.0f}箱<br>" +
                          "总预测销量: %{customdata[1]:.0f}箱<br>" +
                          "计算: 基于销量加权的准确率<br>" +
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
        
        # 添加说明 - 确保背景不透明
        fig.add_annotation(
            x=0.02, y=0.98,
            xref='paper', yref='paper',
            text="""<b>📊 准确率说明</b><br>
<b>平均准确率</b>: 所有产品的简单平均<br>
<b>加权准确率</b>: 基于销量加权，销量大的产品影响更大""",
            showarrow=False,
            align='left',
            bgcolor='white',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11, color='black')
        )
        
        fig.update_layout(
            title="预测准确率趋势分析",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            height=600,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.98,
                bgcolor='white',
                bordercolor='gray',
                borderwidth=1
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(255,255,255,0.9)',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
        
    except Exception as e:
        st.error(f"准确率趋势图表创建失败: {str(e)}")
        return go.Figure()

def create_all_products_trend_chart(df_valid):
    """创建全部产品准确率趋势图 - 可滚动版本"""
    try:
        # 获取所有产品列表
        all_products = df_valid['产品简称'].unique()
        
        # 创建图表
        fig = go.Figure()
        
        # 为每个产品添加趋势线
        for i, product in enumerate(all_products):
            product_data = df_valid[df_valid['产品简称'] == product].sort_values('月份')
            
            fig.add_trace(
                go.Scatter(
                    x=product_data['月份'],
                    y=product_data['准确率'] * 100,
                    mode='lines+markers',
                    name=product,
                    line=dict(width=2, color=COLOR_SCHEME['chart_colors'][i % len(COLOR_SCHEME['chart_colors'])]),
                    marker=dict(size=6),
                    customdata=np.column_stack((
                        product_data['实际销量'],
                        product_data['预测销量'],
                        product_data['选择模型'],
                        product_data['计算详情']
                    )),
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                  "月份: %{x|%Y-%m}<br>" +
                                  "准确率: %{y:.1f}%<br>" +
                                  "实际销量: %{customdata[0]:.0f}箱<br>" +
                                  "预测销量: %{customdata[1]:.0f}箱<br>" +
                                  "使用模型: %{customdata[2]}<br>" +
                                  "%{customdata[3]}<br>" +
                                  "<extra></extra>",
                    visible='legendonly' if i >= 10 else True  # 默认只显示前10个产品
                )
            )
        
        # 添加85%参考线
        fig.add_hline(
            y=85, 
            line_dash="dot", 
            line_color="gray",
            annotation_text="目标: 85%"
        )
        
        fig.update_layout(
            title=f"全部产品准确率趋势分析（共{len(all_products)}个产品）<br><sub>点击图例可显示/隐藏产品，默认显示前10个产品</sub>",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            height=800,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                bgcolor='white',
                bordercolor='gray',
                borderwidth=1,
                itemsizing='constant'
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(255,255,255,0.9)',
            margin=dict(l=50, r=250, t=100, b=50),
            font=dict(color='black')
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(range=[0, 105], showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
        
    except Exception as e:
        st.error(f"全部产品趋势图表创建失败: {str(e)}")
        return go.Figure()

def create_product_ranking_chart(df_valid, metrics):
    """创建产品准确率排行榜 - 显示所有产品"""
    try:
        product_metrics = metrics['product_metrics']
        
        # 按平均准确率排序
        product_metrics = product_metrics.sort_values('平均准确率', ascending=True)
        
        # 创建图表
        fig = go.Figure()
        
        # 添加平均准确率条形图
        fig.add_trace(go.Bar(
            y=product_metrics['产品简称'],
            x=product_metrics['平均准确率'] * 100,
            orientation='h',
            name='平均准确率',
            marker=dict(
                color=product_metrics['平均准确率'] * 100,
                colorscale='RdYlGn',
                cmin=60,
                cmax=100,
                colorbar=dict(
                    title="准确率(%)",
                    x=1.15
                )
            ),
            text=product_metrics['平均准确率'].apply(lambda x: f"{x*100:.1f}%"),
            textposition='outside',
            customdata=np.column_stack((
                product_metrics['平均销量'],
                product_metrics['加权准确率'],
                product_metrics['常用模型']
            )),
            hovertemplate="<b>%{y}</b><br>" +
                          "平均准确率: %{x:.1f}%<br>" +
                          "加权准确率: %{customdata[1]:.1f}%<br>" +
                          "平均销量: %{customdata[0]:.0f}箱<br>" +
                          "常用模型: %{customdata[2]}<br>" +
                          "计算方法: 历史所有月份准确率的平均值<br>" +
                          "<extra></extra>"
        ))
        
        # 添加加权准确率散点图
        fig.add_trace(go.Scatter(
            y=product_metrics['产品简称'],
            x=product_metrics['加权准确率'] * 100,
            mode='markers',
            name='加权准确率',
            marker=dict(
                size=10,
                color='#764ba2',
                symbol='diamond'
            ),
            hovertemplate="<b>%{y}</b><br>" +
                          "加权准确率: %{x:.1f}%<br>" +
                          "计算方法: 基于销量加权的准确率<br>" +
                          "<extra></extra>"
        ))
        
        # 添加85%参考线
        fig.add_vline(x=85, line_dash="dash", line_color="gray", annotation_text="目标: 85%")
        
        # 计算需要的高度
        height = max(800, len(product_metrics) * 25)
        
        fig.update_layout(
            title=f"产品预测准确率排行榜（全部{len(product_metrics)}个产品）<br><sub>显示平均准确率和加权准确率</sub>",
            xaxis_title="预测准确率 (%)",
            yaxis_title="",
            height=height,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.02,
                bgcolor='white',
                bordercolor='gray',
                borderwidth=1
            ),
            margin=dict(l=200, r=150, t=100, b=50),
            paper_bgcolor='white',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(color='black')
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
        
    except Exception as e:
        st.error(f"产品排行榜创建失败: {str(e)}")
        return go.Figure()

def create_accuracy_distribution_chart(df_valid):
    """创建准确率分布图表 - 基于原始数据计算"""
    try:
        # 定义准确率区间
        bins = [0, 0.6, 0.8, 0.85, 0.9, 0.95, 1.0]
        labels = ['<60%', '60-80%', '80-85%', '85-90%', '90-95%', '>95%']
        
        # 基于所有记录计算分布（不是按产品平均）
        df_valid['区间'] = pd.cut(df_valid['准确率'], bins=bins, labels=labels, include_lowest=True)
        dist_counts = df_valid['区间'].value_counts().sort_index()
        
        # 计算占比
        total_records = len(df_valid)
        dist_percentages = (dist_counts / total_records * 100).round(1)
        
        # 计算累计百分比
        cumulative_pct = (dist_counts.cumsum() / total_records * 100).round(1)
        
        # 创建组合图
        fig = make_subplots(
            specs=[[{"secondary_y": True}]]
        )
        
        # 添加柱状图
        fig.add_trace(
            go.Bar(
                x=dist_counts.index,
                y=dist_counts.values,
                name='记录数量',
                marker=dict(
                    color=['#FF0000', '#FF6347', '#FFA500', '#90EE90', '#00FF00', '#006400'],
                    opacity=0.8,
                    line=dict(color='white', width=2)
                ),
                text=[f"{v}<br>({p:.1f}%)" for v, p in zip(dist_counts.values, dist_percentages.values)],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>" +
                              "记录数量: %{y}条<br>" +
                              "占比: %{customdata:.1f}%<br>" +
                              "<extra></extra>",
                customdata=dist_percentages.values
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
        
        # 添加统计信息 - 调整位置避免遮挡
        high_accuracy_count = dist_counts[['85-90%', '90-95%', '>95%']].sum()
        high_accuracy_pct = high_accuracy_count / total_records * 100
        
        # 按产品统计
        product_stats = df_valid.groupby('产品简称')['准确率'].mean()
        products_above_85 = (product_stats > 0.85).sum()
        total_products = len(product_stats)
        
        fig.add_annotation(
            x=0.02, y=0.98,  # 改为左上角
            xref='paper', yref='paper',
            text=f"""<b>📊 统计汇总</b><br>
总记录数: {total_records}条<br>
总产品数: {total_products}个<br>
准确率>85%的记录: {high_accuracy_count}条({high_accuracy_pct:.1f}%)<br>
准确率>85%的产品: {products_above_85}个({products_above_85/total_products*100:.1f}%)""",
            showarrow=False,
            align='left',  # 改为左对齐
            bgcolor='white',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=12, color='black')
        )
        
        fig.update_xaxes(title_text="准确率区间")
        fig.update_yaxes(title_text="记录数量", secondary_y=False, showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(title_text="累计占比 (%)", secondary_y=True)
        
        fig.update_layout(
            title="预测准确率分布<br><sub>基于所有预测记录的分布统计</sub>",
            height=600,
            hovermode='x unified',
            paper_bgcolor='white',
            plot_bgcolor='rgba(255,255,255,0.9)',
            margin=dict(l=50, r=100, t=100, b=50),
            font=dict(color='black')
        )
        
        return fig
        
    except Exception as e:
        st.error(f"准确率分布图表创建失败: {str(e)}")
        return go.Figure()

def create_model_analysis_charts(df_valid):
    """创建模型分析图表 - 将饼图改为条形图"""
    try:
        # 模型使用频率统计
        model_counts = df_valid['选择模型'].value_counts()
        
        # 模型准确率统计
        model_accuracy = df_valid.groupby('选择模型')['准确率'].agg(['mean', 'count']).reset_index()
        model_accuracy.columns = ['模型', '平均准确率', '使用次数']
        model_accuracy = model_accuracy.sort_values('使用次数', ascending=False)
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("模型使用频率", "模型准确率vs使用频率"),
            specs=[[{"type": "bar"}, {"type": "scatter"}]],
            horizontal_spacing=0.15
        )
        
        # 1. 条形图 - 模型使用频率（替换饼图）
        fig.add_trace(go.Bar(
            x=model_counts.index[:8],  # 只显示前8个
            y=model_counts.values[:8],
            marker_color=COLOR_SCHEME['chart_colors'][:8],
            text=model_counts.values[:8],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>" +
                          "使用次数: %{y}<br>" +
                          "占比: %{text}<br>" +
                          "<extra></extra>"
        ), row=1, col=1)
        
        # 2. 散点图 - 模型准确率vs使用频率
        fig.add_trace(go.Scatter(
            x=model_accuracy['使用次数'],
            y=model_accuracy['平均准确率'] * 100,
            mode='markers+text',
            marker=dict(
                size=model_accuracy['使用次数'] / 5,
                sizemin=10,
                color=model_accuracy['平均准确率'] * 100,
                colorscale='RdYlGn',
                cmin=70,
                cmax=100,
                showscale=True,
                colorbar=dict(title="准确率(%)", x=1.15)
            ),
            text=model_accuracy['模型'],
            textposition="top center",
            customdata=model_accuracy['模型'],
            hovertemplate="<b>%{customdata}</b><br>" +
                          "使用次数: %{x}<br>" +
                          "平均准确率: %{y:.1f}%<br>" +
                          "说明: 该模型在所有使用记录中的平均表现<br>" +
                          "<extra></extra>"
        ), row=1, col=2)
        
        # 添加85%参考线（只对散点图）
        fig.add_hline(y=85, line_dash="dash", line_color="gray", 
                      annotation_text="目标: 85%", row=1, col=2)
        
        # 设置坐标轴
        fig.update_xaxes(title_text="模型名称", row=1, col=1)
        fig.update_yaxes(title_text="使用次数", row=1, col=1)
        fig.update_xaxes(title_text="使用次数", row=1, col=2, showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(title_text="平均准确率 (%)", row=1, col=2, showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        fig.update_layout(
            title="机器学习模型使用分析",
            height=600,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=50, r=150, t=100, b=50),
            font=dict(color='black')
        )
        
        return fig
        
    except Exception as e:
        st.error(f"模型分析图表创建失败: {str(e)}")
        return go.Figure()

# 加载数据
with st.spinner('🔄 正在加载数据...'):
    df_all, df_valid = load_and_process_data()
    metrics = calculate_metrics(df_valid)

# 页面标题
st.markdown("""
<div class="page-header">
    <h1 class="page-title">🤖 智能预测分析系统</h1>
    <p class="page-subtitle">基于机器学习的销售预测准确性分析与优化平台</p>
</div>
""", unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 预测准确性核心指标",
    "📈 准确率趋势分析", 
    "🏆 产品准确率排行",
    "📊 准确率分布统计",
    "🔬 模型性能分析"
])

# 标签1：核心指标总览
with tab1:
    if not df_valid.empty and metrics['total_products'] > 0:
        # 第一行：整体指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            accuracy_class = "accuracy-excellent" if metrics['overall_avg_accuracy'] > 0.85 else \
                            "accuracy-good" if metrics['overall_avg_accuracy'] > 0.8 else \
                            "accuracy-medium" if metrics['overall_avg_accuracy'] > 0.7 else "accuracy-low"
            st.markdown(f"""
            <div class="metric-card {accuracy_class}">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['overall_avg_accuracy']*100:.1f}%</div>
                    <div class="metric-label">📊 整体平均准确率</div>
                    <div class="metric-description">所有产品的算术平均</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card {accuracy_class}">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['overall_weighted_accuracy']*100:.1f}%</div>
                    <div class="metric-label">⚖️ 加权整体准确率</div>
                    <div class="metric-description">最近3个月销量加权</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['total_products']}</div>
                    <div class="metric-label">📦 产品总数</div>
                    <div class="metric-description">参与预测的产品数量</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            ratio_class = "accuracy-excellent" if metrics['high_accuracy_ratio'] > 60 else \
                         "accuracy-good" if metrics['high_accuracy_ratio'] > 40 else \
                         "accuracy-medium" if metrics['high_accuracy_ratio'] > 20 else "accuracy-low"
            st.markdown(f"""
            <div class="metric-card {ratio_class}">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['high_accuracy_ratio']:.1f}%</div>
                    <div class="metric-label">🎯 高准确率产品占比</div>
                    <div class="metric-description">准确率>85%的产品</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 第二行：最近一个月指标
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            recent_class = "accuracy-excellent" if metrics['recent_accuracy'] > 0.85 else \
                          "accuracy-good" if metrics['recent_accuracy'] > 0.8 else \
                          "accuracy-medium" if metrics['recent_accuracy'] > 0.7 else "accuracy-low"
            st.markdown(f"""
            <div class="metric-card {recent_class}">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['recent_accuracy']*100:.1f}%</div>
                    <div class="metric-label">📊 最近准确率</div>
                    <div class="metric-description">每个产品最近一次</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['recent_month'].strftime('%Y-%m') if metrics['recent_month'] else 'N/A'}</div>
                    <div class="metric-label">📅 最新数据月份</div>
                    <div class="metric-description">数据更新时间</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            # 计算准确率趋势
            trend = metrics['trend']
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
            # 缩短模型名称以避免溢出
            model_name = metrics['most_used_model']
            if len(model_name) > 15:
                model_name = model_name[:12] + '...'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-inner">
                    <div class="metric-value" style="font-size: 1.5rem !important;">{model_name}</div>
                    <div class="metric-label">🏆 最常用模型</div>
                    <div class="metric-description">使用{metrics['model_count']}次</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 第三部分：准确率分布统计
        st.markdown("### 📊 准确率分布统计")
        col9, col10, col11, col12, col13 = st.columns(5)
        
        with col9:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['total_products']}</div>
                    <div class="metric-label">📊 总产品数</div>
                    <div class="metric-description">系统中的产品总数</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col10:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['products_with_records']}</div>
                    <div class="metric-label">📝 有记录产品数</div>
                    <div class="metric-description">有准确率记录的产品</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col11:
            st.markdown(f"""
            <div class="metric-card accuracy-excellent">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['high_accuracy_count']}</div>
                    <div class="metric-label">🟢 高准确率产品</div>
                    <div class="metric-description">>80%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col12:
            st.markdown(f"""
            <div class="metric-card accuracy-medium">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['medium_accuracy_count']}</div>
                    <div class="metric-label">🟡 中等准确率产品</div>
                    <div class="metric-description">60%-80%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col13:
            st.markdown(f"""
            <div class="metric-card accuracy-low">
                <div class="metric-card-inner">
                    <div class="metric-value">{metrics['low_accuracy_count']}</div>
                    <div class="metric-label">🔴 低准确率产品</div>
                    <div class="metric-description"><60%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 显示数据概览
        st.markdown("### 📊 数据概览")
        st.info(f"数据时间范围：{df_valid['月份'].min().strftime('%Y-%m')} 至 {df_valid['月份'].max().strftime('%Y-%m')}")
        st.info(f"总记录数：{len(df_valid)} 条")
    else:
        st.warning("暂无有效数据可供分析")

# 标签2：准确率趋势分析
with tab2:
    if not df_valid.empty:
        # 创建准确率趋势图表
        trend_fig = create_accuracy_trend_chart(df_valid)
        st.plotly_chart(trend_fig, use_container_width=True, key="trend_chart")
        
        # 全部产品准确率趋势
        st.markdown("### 📈 全部产品准确率趋势")
        all_products_fig = create_all_products_trend_chart(df_valid)
        st.plotly_chart(all_products_fig, use_container_width=True, key="all_products_chart")
        
        # 洞察分析
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">💡 趋势分析洞察</div>
            <div class="insight-content">
                • <b>整体表现:</b> 预测系统整体平均准确率{metrics['overall_avg_accuracy']*100:.1f}%，
                {'已达到优秀水平(>85%)' if metrics['overall_avg_accuracy'] > 0.85 else 
                 '达到良好水平(>80%)' if metrics['overall_avg_accuracy'] > 0.8 else
                 '有待提升'}<br>
                • <b>加权vs平均:</b> 加权准确率（最近3个月）
                {'高于' if metrics['overall_weighted_accuracy'] > metrics['overall_avg_accuracy'] else '低于'}
                整体平均{abs(metrics['overall_weighted_accuracy'] - metrics['overall_avg_accuracy'])*100:.1f}%，
                说明{'最近销量大的产品预测更准确' if metrics['overall_weighted_accuracy'] > metrics['overall_avg_accuracy'] else '最近销量大的产品预测有待改进'}<br>
                • <b>最新表现:</b> 最近准确率为{metrics['recent_accuracy']*100:.1f}%，
                {'持续改善' if metrics['recent_accuracy'] > metrics['overall_avg_accuracy'] else '需要关注'}<br>
                • <b>改进建议:</b> 
                {'保持当前预测策略，继续优化' if metrics['overall_avg_accuracy'] > 0.85 else
                 '重点关注销量大但准确率低的产品' if metrics['overall_weighted_accuracy'] < metrics['overall_avg_accuracy'] else
                 '全面审查预测模型，提升整体准确率'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("暂无有效数据可供分析")

# 标签3：产品准确率排行
with tab3:
    if not df_valid.empty:
        # 创建产品排行榜 - 显示所有产品
        ranking_fig = create_product_ranking_chart(df_valid, metrics)
        st.plotly_chart(ranking_fig, use_container_width=True, key="ranking_chart")
        
        # 重点产品分析
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">🏆 重点产品分析</div>
            <div class="insight-content">
                • <b>优秀产品:</b> 共有{metrics['high_accuracy_products']}个产品准确率超过85%，占比{metrics['high_accuracy_ratio']:.1f}%<br>
                • <b>提升空间:</b> {metrics['total_products'] - metrics['high_accuracy_products']}个产品准确率低于85%，需要重点优化<br>
                • <b>销量权重:</b> 排行榜同时展示了平均准确率和加权准确率，便于综合评估<br>
                • <b>优化建议:</b> 优先改进销量大但准确率低的产品，可带来更大的整体提升
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("暂无有效数据可供分析")

# 标签4：准确率分布统计
with tab4:
    if not df_valid.empty:
        # 创建分布图表
        dist_fig = create_accuracy_distribution_chart(df_valid)
        st.plotly_chart(dist_fig, use_container_width=True, key="distribution_chart")
        
        # 分布洞察
        product_metrics = metrics['product_metrics']
        if not product_metrics.empty:
            excellent_count = (product_metrics['平均准确率'] > 0.9).sum()
            poor_count = (product_metrics['平均准确率'] < 0.6).sum()
        else:
            excellent_count = 0
            poor_count = 0
        
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">📊 准确率分布洞察</div>
            <div class="insight-content">
                • <b>优秀表现(>90%):</b> {excellent_count}个产品，占比{excellent_count/metrics['total_products']*100:.1f}%<br>
                • <b>需要改进(<60%):</b> {poor_count}个产品，占比{poor_count/metrics['total_products']*100:.1f}%<br>
                • <b>分布特征:</b> {'大部分产品表现优秀' if metrics['high_accuracy_ratio'] > 50 else 
                                '准确率分布较为分散' if metrics['high_accuracy_ratio'] > 20 else
                                '多数产品需要优化'}<br>
                • <b>行动建议:</b> {'继续保持，关注个别低准确率产品' if poor_count < 5 else
                                '建立专项小组，优化低准确率产品的预测模型'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("暂无有效数据可供分析")

# 标签5：模型性能分析
with tab5:
    if not df_valid.empty:
        # 创建模型分析图表
        model_fig = create_model_analysis_charts(df_valid)
        st.plotly_chart(model_fig, use_container_width=True, key="model_chart")
        
        # 模型洞察
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">🔬 模型使用洞察</div>
            <div class="insight-content">
                • <b>最常用模型:</b> {metrics['most_used_model']}，使用{metrics['model_count']}次<br>
                • <b>模型多样性:</b> 系统使用了多种模型进行预测，体现了智能选择策略<br>
                • <b>性能vs使用:</b> 使用频率高的模型不一定准确率最高，需要平衡考虑<br>
                • <b>优化方向:</b> 分析高准确率但使用少的模型，考虑扩大其应用范围
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("暂无有效数据可供分析")

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
