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

# 增强的CSS样式 - 添加更多动画效果
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局字体 */
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
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 主标题样式 - 增强动画 */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white;
        border-radius: 25px;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.5s ease-out, glow 2s ease-in-out infinite alternate;
        box-shadow: 
            0 15px 35px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1),
            inset 0 1px 0 rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        transform: perspective(1000px) rotateX(0deg);
        transition: transform 0.3s ease;
    }

    .main-header:hover {
        transform: perspective(1000px) rotateX(-2deg) scale(1.02);
        box-shadow: 
            0 25px 50px rgba(102, 126, 234, 0.5),
            0 10px 30px rgba(0,0,0,0.15);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
    }

    .main-header::after {
        content: '✨';
        position: absolute;
        top: 10%;
        right: 10%;
        font-size: 2rem;
        animation: sparkle 1.5s ease-in-out infinite;
    }

    @keyframes glow {
        from { box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4), 0 5px 15px rgba(0,0,0,0.1); }
        to { box-shadow: 0 20px 40px rgba(102, 126, 234, 0.6), 0 8px 20px rgba(0,0,0,0.15); }
    }

    @keyframes sparkle {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
        50% { transform: scale(1.3) rotate(180deg); opacity: 0.7; }
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
            transform: translateY(-50px) scale(0.8) rotateX(-10deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }

    /* 增强的指标卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 2.5rem 2rem;
        border-radius: 25px;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.9);
        text-align: center;
        height: 100%;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUpStagger 1s ease-out;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.8s ease;
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 25px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-15px) scale(1.05) rotateY(5deg);
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.15),
            0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card:hover::after {
        opacity: 0.1;
    }

    @keyframes slideUpStagger {
        from { 
            opacity: 0; 
            transform: translateY(60px) scale(0.8) rotateX(-15deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }

    .metric-value {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: textGradient 4s ease infinite, bounce 2s ease-in-out infinite;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-3px); }
        60% { transform: translateY(-2px); }
    }

    @keyframes textGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .metric-label {
        color: #374151;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.8rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .metric-sublabel {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        font-weight: 500;
        font-style: italic;
    }

    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 
            inset 0 2px 4px rgba(0,0,0,0.06),
            0 4px 8px rgba(0,0,0,0.04);
        backdrop-filter: blur(10px);
    }

    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 35px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }

    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.15), transparent);
        transition: left 0.8s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.4);
    }

    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1);
        animation: activeTab 0.5s ease;
    }

    .stTabs [aria-selected="true"]::before {
        display: none;
    }

    @keyframes activeTab {
        0% { transform: scale(0.95); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1.02); }
    }

    /* 动画卡片延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }

    /* 图表容器样式 */
    .chart-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 25px;
        padding: 1.5rem;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            inset 0 1px 0 rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.3);
        animation: chartFadeIn 1.2s ease-out;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .chart-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.02), transparent);
        animation: chartShimmer 8s linear infinite;
    }

    @keyframes chartShimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    @keyframes chartFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }

    /* 添加脉动效果 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }

    .metric-card:hover {
        animation: pulse 1.5s infinite;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 2.5rem;
        }
        .metric-card {
            padding: 2rem 1.5rem;
        }
        .main-header {
            padding: 2rem 0;
        }
    }

    /* 添加加载动画 */
    @keyframes loading {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading {
        animation: loading 2s linear infinite;
    }

    /* 成功动画 */
    @keyframes success {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    .success {
        animation: success 0.6s ease-in-out;
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

        # 区分渠道类型 - 增加文本清理功能
        def identify_channel(order_type):
            if pd.isna(order_type):
                return 'Other'

            # 转换为字符串并清理文本
            order_type_str = str(order_type)
            # 去除前后空格、换行符、制表符等
            order_type_str = order_type_str.strip()
            # 去除所有空格（包括中间的）
            order_type_clean = order_type_str.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
            # 统一转为大写进行匹配
            order_type_upper = order_type_clean.upper()

            # 判断渠道类型
            if 'TT' in order_type_upper:
                return 'TT'
            elif 'MT' in order_type_upper or '正常' in order_type_str:
                return 'MT'
            else:
                # 调试信息：记录被归类为Other的订单类型
                if order_type_str and order_type_str != 'nan':
                    print(f"警告：无法识别的订单类型: '{order_type_str}' (长度:{len(order_type_str)})")
                return 'Other'

        sales_data['渠道类型'] = sales_data['订单类型'].apply(identify_channel)

        # 添加数据验证 - 检查渠道分类结果
        channel_counts = sales_data['渠道类型'].value_counts()
        print("渠道分类统计:")
        print(channel_counts)

        # 检查是否有大量数据被分类为Other
        if 'Other' in channel_counts and channel_counts['Other'] > 0:
            print(f"\n注意：有 {channel_counts['Other']} 条记录被分类为 'Other' 渠道")
            # 显示前5条Other类型的订单类型样本
            other_samples = sales_data[sales_data['渠道类型'] == 'Other']['订单类型'].head(5)
            print("Other渠道订单类型样本:")
            for idx, sample in enumerate(other_samples):
                print(f"  {idx + 1}. '{sample}' (类型: {type(sample)})")

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


@st.cache_data
def validate_channel_data(data):
    """验证渠道数据分类的准确性"""
    sales_data = data['sales_data']

    # 统计各渠道2025年的销售额
    current_year = 2025
    validation_results = {}

    for channel in ['TT', 'MT', 'Other']:
        channel_sales = sales_data[
            (sales_data['渠道类型'] == channel) &
            (sales_data['发运月份'].dt.year == current_year)
            ]['销售额'].sum()

        channel_count = len(sales_data[
                                (sales_data['渠道类型'] == channel) &
                                (sales_data['发运月份'].dt.year == current_year)
                                ])

        validation_results[channel] = {
            '销售额': channel_sales,
            '订单数': channel_count,
            '平均单价': channel_sales / channel_count if channel_count > 0 else 0
        }

    return validation_results
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
            '<b>MT渠道月度销售额与达成率</b>',
            '<b>MT渠道区域销售分布</b>',
            '<b>MT渠道季度对比分析</b>',
            '<b>MT渠道环比增长趋势</b>'  # 改为环比
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": False}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
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

        # 计算环比增长（与上月对比）
        if month > 1:
            last_month_start = pd.Timestamp(f'{current_year}-{month - 1:02d}-01')
            last_month_end = last_month_start + pd.offsets.MonthEnd(0)
            last_month_sales = sales_data[
                (sales_data['渠道类型'] == 'MT') &
                (sales_data['发运月份'] >= last_month_start) &
                (sales_data['发运月份'] <= last_month_end)
                ]['销售额'].sum()

            growth_rate = ((mt_month_sales - last_month_sales) / last_month_sales * 100) if last_month_sales > 0 else 0
        else:
            growth_rate = 0  # 1月份没有环比数据

        monthly_data.append({
            '月份': f'{month}月',
            '季度': f'Q{(month - 1) // 3 + 1}',
            'MT销售额': mt_month_sales,
            'MT目标额': mt_month_target,
            'MT达成率': mt_achievement,
            '环比增长': growth_rate
        })

    df_monthly = pd.DataFrame(monthly_data)

    # 添加月度销售额柱状图
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['MT销售额'],
            name='MT销售额',
            marker=dict(
                color='#764ba2',
                line=dict(color='rgba(118, 75, 162, 0.8)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in df_monthly['MT销售额']],
            textposition='inside',
            textfont=dict(color='white', size=11, family="Arial Black"),
            hovertemplate=(
                    '<b>MT渠道月度销售</b><br>' +
                    '月份: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '完成度: %{customdata[1]:.1f}%<br>' +
                    '环比增长: %{customdata[2]:+.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['MT目标额'],
                df_monthly['MT达成率'],
                df_monthly['环比增长']
            ))
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
            line=dict(color='#f59e0b', width=4, dash='dot'),
            marker=dict(
                size=10,
                color='#f59e0b',
                line=dict(color='white', width=2)
            ),
            text=[f'{v:.0f}%' for v in df_monthly['MT达成率']],
            textposition='top center',
            textfont=dict(color='#1f2937', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>MT达成率</b><br>' +
                    '月份: %{x}<br>' +
                    '达成率: %{y:.1f}%<br>' +
                    '销售额: ¥%{customdata[0]:,.0f}<br>' +
                    '目标额: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(df_monthly['MT销售额'], df_monthly['MT目标额']))
        ),
        row=1, col=1, secondary_y=True
    )

    # 添加100%参考线
    fig.add_hline(
        y=100,
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=1, secondary_y=True,
        annotation_text="目标线 100%"
    )

    # 2. 区域销售分布
    regional_data = sales_data[sales_data['渠道类型'] == 'MT'].groupby('所属区域')['销售额'].sum().sort_values(
        ascending=True)

    fig.add_trace(
        go.Bar(
            y=regional_data.index,
            x=regional_data.values,
            name='区域销售额',
            orientation='h',
            marker=dict(
                color='#764ba2',
                line=dict(color='rgba(118, 75, 162, 0.8)', width=1)
            ),
            text=[f'¥{v / 10000:.0f}万' for v in regional_data.values],
            textposition='inside',
            textfont=dict(color='white', size=11, family="Arial Black"),
            hovertemplate=(
                    '<b>MT渠道区域分析</b><br>' +
                    '区域: %{y}<br>' +
                    '销售额: ¥%{x:,.0f}<br>' +
                    '占MT总额: %{customdata[0]:.1f}%<br>' +
                    '排名: 第%{customdata[1]}名' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                [v / regional_data.sum() * 100 for v in regional_data.values],
                list(range(len(regional_data), 0, -1))
            ))
        ),
        row=1, col=2
    )

    # 3. 季度对比分析
    quarterly_data = df_monthly.groupby('季度').agg({
        'MT销售额': 'sum',
        'MT目标额': 'sum'
    }).reset_index()
    quarterly_data['达成率'] = (quarterly_data['MT销售额'] / quarterly_data['MT目标额'] * 100).fillna(0)

    fig.add_trace(
        go.Bar(
            x=quarterly_data['季度'],
            y=quarterly_data['MT销售额'],
            name='季度销售额',
            marker=dict(
                color=['#667eea', '#764ba2', '#f59e0b', '#10b981'],
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in quarterly_data['MT销售额']],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Black"),
            hovertemplate=(
                    '<b>MT季度对比</b><br>' +
                    '季度: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                quarterly_data['MT目标额'],
                quarterly_data['达成率']
            ))
        ),
        row=2, col=1
    )

    # 4. 环比增长趋势（替代同比）
    positive_growth = [max(0, v) for v in df_monthly['环比增长']]
    negative_growth = [min(0, v) for v in df_monthly['环比增长']]

    # 1月份特殊处理
    fig.add_trace(
        go.Bar(
            x=[df_monthly['月份'].iloc[0]],
            y=[0],
            name='无环比数据',
            marker=dict(
                color='#d1d5db',
                line=dict(color='rgba(209, 213, 219, 0.8)', width=1)
            ),
            text=['无环比'],
            textposition='inside',
            textfont=dict(color='#6b7280', size=10, family="Arial Black"),
            showlegend=True,
            hovertemplate=(
                    '<b>1月份</b><br>' +
                    '无上月数据对比' +
                    '<extra></extra>'
            )
        ),
        row=2, col=2
    )

    # 其他月份的环比增长
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'][1:],  # 从2月开始
            y=positive_growth[1:],
            name='正增长',
            marker=dict(
                color='#10b981',
                line=dict(color='rgba(16, 185, 129, 0.8)', width=1)
            ),
            text=[f'+{v:.0f}%' if v > 0 else '' for v in positive_growth[1:]],
            textposition='outside',
            textfont=dict(color='#10b981', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>MT环比正增长</b><br>' +
                    '月份: %{x}<br>' +
                    '增长率: +%{y:.1f}%<br>' +
                    '当月销售: ¥%{customdata[0]:,.0f}<br>' +
                    '上月销售: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['MT销售额'][1:],
                [df_monthly['MT销售额'].iloc[i - 1] for i in range(1, len(df_monthly))]
            ))
        ),
        row=2, col=2
    )

    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'][1:],  # 从2月开始
            y=negative_growth[1:],
            name='负增长',
            marker=dict(
                color='#ef4444',
                line=dict(color='rgba(239, 68, 68, 0.8)', width=1)
            ),
            text=[f'{v:.0f}%' if v < 0 else '' for v in negative_growth[1:]],
            textposition='outside',
            textfont=dict(color='#ef4444', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>MT环比负增长</b><br>' +
                    '月份: %{x}<br>' +
                    '增长率: %{y:.1f}%<br>' +
                    '当月销售: ¥%{customdata[0]:,.0f}<br>' +
                    '上月销售: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['MT销售额'][1:],
                [df_monthly['MT销售额'].iloc[i - 1] for i in range(1, len(df_monthly))]
            ))
        ),
        row=2, col=2
    )

    # 添加零线
    fig.add_hline(
        y=0,
        line=dict(color="gray", width=1),
        row=2, col=2
    )

    # 设置第4个子图的Y轴范围，确保负数部分能够完整显示
    fig.update_yaxes(
        range=[-150, 150],  # 设置Y轴范围，给负数部分留出足够空间
        row=2, col=2
    )

    # 更新布局
    fig.update_layout(
        height=800,  # 增加高度以确保显示完整
        showlegend=True,
        title={
            'text': "<b>🏪 MT渠道综合分析</b>",
            'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=11, color='#374151')
        ),
        font=dict(family="Inter, sans-serif", color='#374151'),
        margin=dict(t=80, l=60, r=60, b=80)
    )

    # 更新坐标轴
    fig.update_xaxes(
        tickangle=-45,
        row=1, col=1,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>销售额 (元)</b>",
        row=1, col=1,
        secondary_y=False,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>达成率 (%)</b>",
        row=1, col=1,
        secondary_y=True,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>环比增长率 (%)</b>",  # 改为环比
        row=2, col=2,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )

    # 更新所有坐标轴的字体
    fig.update_xaxes(tickfont=dict(size=10, color='#6b7280'))
    fig.update_yaxes(tickfont=dict(size=10, color='#6b7280'))

    return fig


# 创建综合分析图 - TT渠道 (修复版本)
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
            '<b>TT渠道月度销售额与达成率</b>',
            '<b>TT渠道区域销售分布</b>',
            '<b>TT渠道季度对比分析</b>',
            '<b>TT渠道环比增长趋势</b>'  # 改为环比
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": False}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
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

        # 计算环比增长（与上月对比）
        if month > 1:
            last_month_start = pd.Timestamp(f'{current_year}-{month - 1:02d}-01')
            last_month_end = last_month_start + pd.offsets.MonthEnd(0)
            last_month_sales = sales_data[
                (sales_data['渠道类型'] == 'TT') &
                (sales_data['发运月份'] >= last_month_start) &
                (sales_data['发运月份'] <= last_month_end)
                ]['销售额'].sum()

            growth_rate = ((tt_month_sales - last_month_sales) / last_month_sales * 100) if last_month_sales > 0 else 0
        else:
            growth_rate = 0  # 1月份没有环比数据

        monthly_data.append({
            '月份': f'{month}月',
            '季度': f'Q{(month - 1) // 3 + 1}',
            'TT销售额': tt_month_sales,
            'TT目标额': tt_month_target,
            'TT达成率': tt_achievement,
            '环比增长': growth_rate
        })

    df_monthly = pd.DataFrame(monthly_data)

    # 添加月度销售额柱状图
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['TT销售额'],
            name='TT销售额',
            marker=dict(
                color='#667eea',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in df_monthly['TT销售额']],
            textposition='inside',
            textfont=dict(color='white', size=11, family="Arial Black"),
            hovertemplate=(
                    '<b>TT渠道月度销售</b><br>' +
                    '月份: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '完成度: %{customdata[1]:.1f}%<br>' +
                    '环比增长: %{customdata[2]:+.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['TT目标额'],
                df_monthly['TT达成率'],
                df_monthly['环比增长']
            ))
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
            line=dict(color='#f59e0b', width=4, dash='dot'),
            marker=dict(
                size=10,
                color='#f59e0b',
                line=dict(color='white', width=2)
            ),
            text=[f'{v:.0f}%' for v in df_monthly['TT达成率']],
            textposition='top center',
            textfont=dict(color='#1f2937', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>TT达成率</b><br>' +
                    '月份: %{x}<br>' +
                    '达成率: %{y:.1f}%<br>' +
                    '销售额: ¥%{customdata[0]:,.0f}<br>' +
                    '目标额: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(df_monthly['TT销售额'], df_monthly['TT目标额']))
        ),
        row=1, col=1, secondary_y=True
    )

    # 添加100%参考线
    fig.add_hline(
        y=100,
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=1, secondary_y=True,
        annotation_text="目标线 100%"
    )

    # 2. 区域销售分布
    regional_data = sales_data[sales_data['渠道类型'] == 'TT'].groupby('所属区域')['销售额'].sum().sort_values(
        ascending=True)

    fig.add_trace(
        go.Bar(
            y=regional_data.index,
            x=regional_data.values,
            name='区域销售额',
            orientation='h',
            marker=dict(
                color='#667eea',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1)
            ),
            text=[f'¥{v / 10000:.0f}万' for v in regional_data.values],
            textposition='inside',
            textfont=dict(color='white', size=11, family="Arial Black"),
            hovertemplate=(
                    '<b>TT渠道区域分析</b><br>' +
                    '区域: %{y}<br>' +
                    '销售额: ¥%{x:,.0f}<br>' +
                    '占TT总额: %{customdata[0]:.1f}%<br>' +
                    '排名: 第%{customdata[1]}名' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                [v / regional_data.sum() * 100 for v in regional_data.values],
                list(range(len(regional_data), 0, -1))
            ))
        ),
        row=1, col=2
    )

    # 3. 季度对比分析
    quarterly_data = df_monthly.groupby('季度').agg({
        'TT销售额': 'sum',
        'TT目标额': 'sum'
    }).reset_index()
    quarterly_data['达成率'] = (quarterly_data['TT销售额'] / quarterly_data['TT目标额'] * 100).fillna(0)

    fig.add_trace(
        go.Bar(
            x=quarterly_data['季度'],
            y=quarterly_data['TT销售额'],
            name='季度销售额',
            marker=dict(
                color=['#667eea', '#764ba2', '#f59e0b', '#10b981'],
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in quarterly_data['TT销售额']],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Black"),
            hovertemplate=(
                    '<b>TT季度对比</b><br>' +
                    '季度: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                quarterly_data['TT目标额'],
                quarterly_data['达成率']
            ))
        ),
        row=2, col=1
    )

    # 4. 环比增长趋势（替代同比）
    positive_growth = [max(0, v) for v in df_monthly['环比增长']]
    negative_growth = [min(0, v) for v in df_monthly['环比增长']]

    # 1月份特殊处理 - 显示新渠道标识
    fig.add_trace(
        go.Bar(
            x=[df_monthly['月份'].iloc[0]],
            y=[0],
            name='新增渠道',
            marker=dict(
                color='#9333ea',
                line=dict(color='rgba(147, 51, 234, 0.8)', width=1)
            ),
            text=['新渠道'],
            textposition='inside',
            textfont=dict(color='white', size=10, family="Arial Black"),
            showlegend=True,
            hovertemplate=(
                    '<b>TT渠道1月份</b><br>' +
                    '新增渠道，无环比数据<br>' +
                    '销售额: ¥%{customdata[0]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=[[df_monthly['TT销售额'].iloc[0]]]
        ),
        row=2, col=2
    )

    # 其他月份的环比增长
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'][1:],  # 从2月开始
            y=positive_growth[1:],
            name='正增长',
            marker=dict(
                color='#10b981',
                line=dict(color='rgba(16, 185, 129, 0.8)', width=1)
            ),
            text=[f'+{v:.0f}%' if v > 0 else '' for v in positive_growth[1:]],
            textposition='outside',
            textfont=dict(color='#10b981', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>TT环比正增长</b><br>' +
                    '月份: %{x}<br>' +
                    '增长率: +%{y:.1f}%<br>' +
                    '当月销售: ¥%{customdata[0]:,.0f}<br>' +
                    '上月销售: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['TT销售额'][1:],
                [df_monthly['TT销售额'].iloc[i - 1] for i in range(1, len(df_monthly))]
            ))
        ),
        row=2, col=2
    )

    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'][1:],  # 从2月开始
            y=negative_growth[1:],
            name='负增长',
            marker=dict(
                color='#ef4444',
                line=dict(color='rgba(239, 68, 68, 0.8)', width=1)
            ),
            text=[f'{v:.0f}%' if v < 0 else '' for v in negative_growth[1:]],
            textposition='outside',
            textfont=dict(color='#ef4444', size=10, family="Arial Black"),
            hovertemplate=(
                    '<b>TT环比负增长</b><br>' +
                    '月份: %{x}<br>' +
                    '增长率: %{y:.1f}%<br>' +
                    '当月销售: ¥%{customdata[0]:,.0f}<br>' +
                    '上月销售: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['TT销售额'][1:],
                [df_monthly['TT销售额'].iloc[i - 1] for i in range(1, len(df_monthly))]
            ))
        ),
        row=2, col=2
    )

    # 添加零线
    fig.add_hline(
        y=0,
        line=dict(color="gray", width=1),
        row=2, col=2
    )

    # 添加新渠道说明
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="x domain",
        yref="y domain",
        text="<b>注：TT为2025年新增渠道</b>",
        showarrow=False,
        font=dict(size=11, color='#9333ea'),
        row=2, col=2
    )

    # 设置第4个子图的Y轴范围，确保负数部分能够完整显示
    fig.update_yaxes(
        range=[-150, 150],  # 设置Y轴范围，给负数部分留出足够空间
        row=2, col=2
    )

    # 更新布局
    fig.update_layout(
        height=800,  # 增加高度以确保显示完整
        showlegend=True,
        title={
            'text': "<b>🏢 TT渠道综合分析</b>",
            'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=11, color='#374151')
        ),
        font=dict(family="Inter, sans-serif", color='#374151'),
        margin=dict(t=80, l=60, r=60, b=80)
    )

    # 更新坐标轴
    fig.update_xaxes(
        tickangle=-45,
        row=1, col=1,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>销售额 (元)</b>",
        row=1, col=1,
        secondary_y=False,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>达成率 (%)</b>",
        row=1, col=1,
        secondary_y=True,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>环比增长率 (%)</b>",  # 改为环比
        row=2, col=2,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )

    # 更新所有坐标轴的字体
    fig.update_xaxes(tickfont=dict(size=10, color='#6b7280'))
    fig.update_yaxes(tickfont=dict(size=10, color='#6b7280'))

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
            '<b>全渠道月度销售额与达成率对比</b>',
            '<b>渠道销售额季度对比</b>',
            '<b>区域渠道销售分布热力图</b>',
            '<b>全年销售趋势与预测</b>'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "bar"}],
            [{"type": "bar"}, {"secondary_y": True}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
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
            '季度': f'Q{(month - 1) // 3 + 1}',
            'TT销售额': tt_month_sales,
            'TT目标额': tt_month_target,
            'MT销售额': mt_month_sales,
            'MT目标额': mt_month_target,
            '总销售额': total_sales,
            '总目标额': total_target,
            '总达成率': total_achievement
        })

    df_monthly = pd.DataFrame(monthly_data)

    # 添加TT和MT销售额
    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['TT销售额'],
            name='TT销售额',
            marker=dict(
                color='#667eea',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1)
            ),
            hovertemplate=(
                    '<b>TT渠道</b><br>' +
                    '月份: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['TT目标额'],
                df_monthly['TT销售额'] / df_monthly['TT目标额'] * 100
            ))
        ),
        row=1, col=1, secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=df_monthly['月份'],
            y=df_monthly['MT销售额'],
            name='MT销售额',
            marker=dict(
                color='#764ba2',
                line=dict(color='rgba(118, 75, 162, 0.8)', width=1)
            ),
            hovertemplate=(
                    '<b>MT渠道</b><br>' +
                    '月份: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                df_monthly['MT目标额'],
                df_monthly['MT销售额'] / df_monthly['MT目标额'] * 100
            ))
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
            line=dict(color='#f59e0b', width=4),
            marker=dict(
                size=12,
                color='#f59e0b',
                line=dict(color='white', width=2)
            ),
            text=[f'{v:.0f}%' for v in df_monthly['总达成率']],
            textposition='top center',
            textfont=dict(color='#1f2937', size=11, family="Arial Black"),
            hovertemplate=(
                    '<b>总体达成率</b><br>' +
                    '月份: %{x}<br>' +
                    '达成率: %{y:.1f}%<br>' +
                    '总销售: ¥%{customdata[0]:,.0f}<br>' +
                    '总目标: ¥%{customdata[1]:,.0f}' +
                    '<extra></extra>'
            ),
            customdata=list(zip(df_monthly['总销售额'], df_monthly['总目标额']))
        ),
        row=1, col=1, secondary_y=True
    )

    # 添加100%参考线
    fig.add_hline(
        y=100,
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=1, secondary_y=True,
        annotation_text="目标线 100%"
    )

    # 2. 季度对比
    quarterly_tt = df_monthly.groupby('季度')['TT销售额'].sum()
    quarterly_mt = df_monthly.groupby('季度')['MT销售额'].sum()
    quarterly_tt_target = df_monthly.groupby('季度')['TT目标额'].sum()
    quarterly_mt_target = df_monthly.groupby('季度')['MT目标额'].sum()

    fig.add_trace(
        go.Bar(
            x=quarterly_tt.index,
            y=quarterly_tt.values,
            name='TT季度销售',
            marker=dict(
                color='#667eea',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in quarterly_tt.values],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Black"),
            hovertemplate=(
                    '<b>TT季度销售</b><br>' +
                    '季度: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                quarterly_tt_target.values,
                quarterly_tt.values / quarterly_tt_target.values * 100
            ))
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            x=quarterly_mt.index,
            y=quarterly_mt.values,
            name='MT季度销售',
            marker=dict(
                color='#764ba2',
                line=dict(color='rgba(118, 75, 162, 0.8)', width=1)
            ),
            text=[f'{v / 10000:.0f}万' for v in quarterly_mt.values],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Black"),
            hovertemplate=(
                    '<b>MT季度销售</b><br>' +
                    '季度: %{x}<br>' +
                    '销售额: ¥%{y:,.0f}<br>' +
                    '目标额: ¥%{customdata[0]:,.0f}<br>' +
                    '达成率: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                quarterly_mt_target.values,
                quarterly_mt.values / quarterly_mt_target.values * 100
            ))
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
                marker=dict(
                    color='#667eea',
                    line=dict(color='rgba(102, 126, 234, 0.8)', width=1)
                ),
                hovertemplate=(
                        '<b>TT区域销售</b><br>' +
                        '区域: %{y}<br>' +
                        '销售额: ¥%{x:,.0f}<br>' +
                        '占TT总额: %{customdata:.1f}%' +
                        '<extra></extra>'
                ),
                customdata=[v / regional_channel['TT'].sum() * 100 for v in regional_channel['TT']]
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
                marker=dict(
                    color='#764ba2',
                    line=dict(color='rgba(118, 75, 162, 0.8)', width=1)
                ),
                hovertemplate=(
                        '<b>MT区域销售</b><br>' +
                        '区域: %{y}<br>' +
                        '销售额: ¥%{x:,.0f}<br>' +
                        '占MT总额: %{customdata:.1f}%' +
                        '<extra></extra>'
                ),
                customdata=[v / regional_channel['MT'].sum() * 100 for v in regional_channel['MT']]
            ),
            row=2, col=1
        )

    # 4. 累计销售趋势
    cumulative_sales = df_monthly['总销售额'].cumsum()
    cumulative_target = df_monthly['总目标额'].cumsum()

    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=cumulative_sales,
            name='累计销售额',
            mode='lines+markers',
            line=dict(color='#10b981', width=4),
            marker=dict(size=10, color='#10b981'),
            fill='tonexty',
            hovertemplate=(
                    '<b>累计销售趋势</b><br>' +
                    '月份: %{x}<br>' +
                    '累计销售: ¥%{y:,.0f}<br>' +
                    '累计目标: ¥%{customdata[0]:,.0f}<br>' +
                    '累计达成: %{customdata[1]:.1f}%' +
                    '<extra></extra>'
            ),
            customdata=list(zip(
                cumulative_target,
                cumulative_sales / cumulative_target * 100
            ))
        ),
        row=2, col=2, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_monthly['月份'],
            y=cumulative_target,
            name='累计目标额',
            mode='lines+markers',
            line=dict(color='#ef4444', width=3, dash='dash'),
            marker=dict(size=8, color='#ef4444'),
            hovertemplate=(
                    '<b>累计目标</b><br>' +
                    '月份: %{x}<br>' +
                    '累计目标: ¥%{y:,.0f}' +
                    '<extra></extra>'
            )
        ),
        row=2, col=2, secondary_y=False
    )

    # 更新布局
    fig.update_layout(
        height=750,
        showlegend=True,
        title={
            'text': "<b>📊 全渠道综合对比分析</b>",
            'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=11, color='#374151')
        ),
        font=dict(family="Inter, sans-serif", color='#374151'),
        margin=dict(t=80, l=60, r=60, b=80)
    )

    # 更新坐标轴
    fig.update_xaxes(
        tickangle=-45,
        row=1, col=1,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>销售额 (元)</b>",
        row=1, col=1,
        secondary_y=False,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>达成率 (%)</b>",
        row=1, col=1,
        secondary_y=True,
        title_font=dict(size=12, color='#6b7280')
    )
    fig.update_yaxes(
        title_text="<b>累计销售额 (元)</b>",
        row=2, col=2,
        gridcolor='rgba(0,0,0,0.1)',
        gridwidth=1,
        title_font=dict(size=12, color='#6b7280')
    )

    # 更新所有坐标轴的字体
    fig.update_xaxes(tickfont=dict(size=10, color='#6b7280'))
    fig.update_yaxes(tickfont=dict(size=10, color='#6b7280'))

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

        # 加载数据
        with st.spinner('正在加载数据...'):
            data = load_data()

        if data is None:
            return

        # 新增：数据验证（仅在开发模式下显示）
        if st.sidebar.checkbox('显示数据验证信息', value=False):
            st.sidebar.subheader('渠道数据验证')
            validation = validate_channel_data(data)

            for channel, info in validation.items():
                st.sidebar.write(f"**{channel}渠道**")
                st.sidebar.write(f"- 销售额: ¥{info['销售额'] / 10000:.1f}万")
                st.sidebar.write(f"- 订单数: {info['订单数']}")
                st.sidebar.write(f"- 平均单价: ¥{info['平均单价']:.2f}")
                st.sidebar.write("---")

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
                <div class="metric-value">¥{metrics['total_sales'] / 10000:.0f}万</div>
                <div class="metric-label">💰 2025年总销售额</div>
                <div class="metric-sublabel">目标: ¥{metrics['total_target'] / 10000:.0f}万</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            achievement_color = "#10b981" if metrics['total_achievement'] >= 100 else "#f59e0b" if metrics[
                                                                                                       'total_achievement'] >= 80 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="background: linear-gradient(135deg, {achievement_color} 0%, {achievement_color} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{metrics['total_achievement']:.1f}%</div>
                <div class="metric-label">🎯 总体达成率</div>
                <div class="metric-sublabel">{'✅ 超额完成' if metrics['total_achievement'] >= 100 else '⚠️ 需要努力' if metrics['total_achievement'] >= 80 else '🚨 严重不足'}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            gap = metrics['total_target'] - metrics['total_sales']
            gap_color = "#10b981" if gap <= 0 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="background: linear-gradient(135deg, {gap_color} 0%, {gap_color} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">¥{abs(gap) / 10000:.0f}万</div>
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
                <div class="metric-value">¥{metrics['tt_sales'] / 10000:.0f}万</div>
                <div class="metric-label">🏢 TT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['tt_achievement']:.1f}% | 占比: {metrics['tt_ratio']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['mt_sales'] / 10000:.0f}万</div>
                <div class="metric-label">🏪 MT渠道销售额</div>
                <div class="metric-sublabel">达成率: {metrics['mt_achievement']:.1f}% | 占比: {metrics['mt_ratio']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col6:
            better_channel = "TT" if metrics['tt_achievement'] > metrics['mt_achievement'] else "MT"
            better_color = "#667eea" if better_channel == "TT" else "#764ba2"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="background: linear-gradient(135deg, {better_color} 0%, {better_color} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{better_channel}</div>
                <div class="metric-label">🏆 表现更优渠道</div>
                <div class="metric-sublabel">{better_channel}渠道达成率更高</div>
            </div>
            """, unsafe_allow_html=True)

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
