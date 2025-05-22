# 产品组合分析页面 - Clay.com风格设计（更新版v7.0）
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clay.com风格CSS样式 - 鲜艳蓝色主题
st.markdown("""
<style>
    /* Clay.com风格主题 - 鲜艳蓝色版本 */
    :root {
        --primary-bg: linear-gradient(135deg, #1E90FF 0%, #4169E1 100%);
        --secondary-bg: linear-gradient(135deg, #4682B4 0%, #5A9FD4 100%);
        --accent-blue: #ffffff;
        --accent-gold: #FFD700;
        --text-primary: #1e40af;
        --text-secondary: #1e3a8a;
        --text-muted: #475569;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --glass-bg: rgba(255, 255, 255, 0.9);
        --glass-border: rgba(255, 255, 255, 0.3);
    }

    /* 全局背景 */
    .stApp {
        background: var(--primary-bg);
        color: var(--text-primary);
    }

    /* 主容器 */
    .main-container {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid var(--glass-border);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: slideUp 0.6s ease-out;
    }

    /* 动画定义 */
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

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 0 30px rgba(255, 215, 0, 0.6); }
    }

    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }

    /* 关键指标卡片 */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid var(--glass-border);
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(255, 215, 0, 0.2);
        border-color: var(--accent-gold);
        cursor: pointer;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,215,0,0.1), transparent);
        transition: left 0.5s;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.5rem 0;
        animation: countUp 1s ease-out;
    }

    .metric-label {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .metric-change {
        font-size: 0.9rem;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        margin-top: 0.5rem;
        display: inline-block;
    }

    .change-positive {
        background: rgba(34, 197, 94, 0.2);
        color: var(--success);
        border: 1px solid var(--success);
    }

    .change-negative {
        background: rgba(239, 68, 68, 0.2);
        color: var(--danger);
        border: 1px solid var(--danger);
    }

    .change-neutral {
        background: rgba(71, 85, 105, 0.2);
        color: var(--text-muted);
        border: 1px solid var(--text-muted);
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 0.5rem;
        border: 1px solid var(--glass-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 0.8rem 1.5rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 215, 0, 0.1);
        color: var(--text-primary);
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-gold), #FFA500);
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }

    /* 筛选器样式 */
    .filter-container {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid var(--glass-border);
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    /* 自定义选择框 */
    .stSelectbox > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        color: var(--text-primary);
        backdrop-filter: blur(10px);
    }

    .stSelectbox > div > div:hover {
        border-color: var(--accent-gold);
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }

    /* 图表容器 */
    .chart-container {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid var(--glass-border);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .chart-container:hover {
        border-color: var(--accent-gold);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.15);
    }

    /* 图表标题 */
    .chart-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        text-align: center;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }

    .status-good { background: var(--success); }
    .status-warning { background: var(--warning); }
    .status-danger { background: var(--danger); }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* 达成率卡片样式 */
    .achievement-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid var(--glass-border);
        padding: 2rem;
        margin: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
    }

    .achievement-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.2);
        border-color: var(--accent-gold);
    }

    .achievement-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }

    .achievement-value {
        font-size: 3rem;
        font-weight: 700;
        margin: 1rem 0;
        animation: countUp 1.2s ease-out;
    }

    .achievement-target {
        font-size: 1rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }

    .achievement-status {
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin-top: 1rem;
        display: inline-block;
        font-weight: 500;
    }

    /* 侧边栏样式 */
    .css-1d391kg {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-card, .achievement-card {
            margin: 0.5rem 0;
        }

        .metric-value, .achievement-value {
            font-size: 2rem;
        }

        .main-container {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }

    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--glass-bg);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--text-primary), var(--accent-gold));
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--accent-gold), var(--text-primary));
    }
</style>
""", unsafe_allow_html=True)


# 数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 加载产品代码文件
        with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
            star_new_products = [line.strip() for line in f.readlines() if line.strip()]

        with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
            new_products = [line.strip() for line in f.readlines() if line.strip()]

        with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
            dashboard_products = [line.strip() for line in f.readlines() if line.strip()]

        # 加载Excel文件
        promotion_data = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
        sales_data = pd.read_excel('24-25促销效果销售数据.xlsx')

        # 数据预处理
        sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
        sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'], format='%Y-%m')
        sales_data['年份'] = sales_data['发运月份'].dt.year
        sales_data['月份'] = sales_data['发运月份'].dt.month

        # 产品分类
        sales_data['产品类型'] = sales_data['产品代码'].apply(
            lambda x: '新品' if x in new_products else (
                '星品' if x in star_new_products and x not in new_products else '普通品')
        )

        return {
            'sales_data': sales_data,
            'promotion_data': promotion_data,
            'star_new_products': star_new_products,
            'new_products': new_products,
            'dashboard_products': dashboard_products
        }
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None


# 产品简称映射函数
@st.cache_data
def create_product_mapping(sales_data, promotion_data):
    """创建产品代码到简称的映射"""
    mapping = {}

    # 从销售数据提取映射
    if '产品简称' in sales_data.columns:
        sales_mapping = sales_data[['产品代码', '产品简称']].drop_duplicates()
        for _, row in sales_mapping.iterrows():
            if pd.notna(row['产品简称']):
                mapping[row['产品代码']] = row['产品简称']

    # 从促销数据提取映射（补充）
    if '促销产品名称' in promotion_data.columns:
        promo_mapping = promotion_data[['产品代码', '促销产品名称']].drop_duplicates()
        for _, row in promo_mapping.iterrows():
            if row['产品代码'] not in mapping and pd.notna(row['促销产品名称']):
                mapping[row['产品代码']] = row['促销产品名称']

    return mapping


def get_product_display_name(product_code, mapping):
    """获取产品显示名称（优先使用简称）"""
    return mapping.get(product_code, product_code)


# 计算关键指标
def calculate_key_metrics(data, selected_region):
    """计算六大关键指标"""
    sales_df = data['sales_data'].copy()

    # 区域筛选
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    # 时间筛选：2025年1-5月 vs 2024年1-5月
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]
    last_year_data = sales_df[(sales_df['年份'] == 2024) & (sales_df['月份'] <= 5)]

    # 1. 总销售额/销量
    current_sales = current_year_data['销售额'].sum()
    current_volume = current_year_data['箱数'].sum()
    last_sales = last_year_data['销售额'].sum()
    last_volume = last_year_data['箱数'].sum()

    # 计算同比增长率
    sales_growth = ((current_sales - last_sales) / last_sales * 100) if last_sales > 0 else 0
    volume_growth = ((current_volume - last_volume) / last_volume * 100) if last_volume > 0 else 0

    # 2. 产品矩阵占比
    # 计算每个产品的销售占比和成长率
    product_metrics = []
    total_sales = current_year_data['销售额'].sum()

    for product in current_year_data['产品代码'].unique():
        # 当前年度该产品销售
        product_current = current_year_data[current_year_data['产品代码'] == product]['销售额'].sum()
        # 去年同期该产品销售
        product_last = last_year_data[last_year_data['产品代码'] == product]['销售额'].sum()

        product_share = (product_current / total_sales * 100) if total_sales > 0 else 0
        growth_rate = ((product_current - product_last) / product_last * 100) if product_last > 0 else 0

        # BCG分类
        if product_share < 1.5 and growth_rate > 20:
            category = '问号产品'
        elif product_share >= 1.5 and growth_rate > 20:
            category = '明星产品'
        elif product_share < 1.5 and growth_rate <= 20:
            category = '瘦狗产品'
        else:
            category = '现金牛产品'

        product_metrics.append({
            '产品代码': product,
            '销售占比': product_share,
            '成长率': growth_rate,
            '类别': category,
            '销售额': product_current
        })

    product_df = pd.DataFrame(product_metrics)

    # 计算各类别占比
    category_stats = product_df.groupby('类别')['销售占比'].sum() if len(product_df) > 0 else pd.Series()

    # 3. 星品&新品KPI达成率
    star_new_sales = current_year_data[current_year_data['产品代码'].isin(data['star_new_products'])]['销售额'].sum()
    kpi_achievement = (star_new_sales / current_sales * 100) if current_sales > 0 else 0

    # 分别计算星品和新品达成率
    new_sales = current_year_data[current_year_data['产品代码'].isin(data['new_products'])]['销售额'].sum()
    star_sales = star_new_sales - new_sales  # 星品销售额（星品&新品 - 新品）

    star_achievement = (star_sales / current_sales * 100) if current_sales > 0 else 0
    new_achievement = (new_sales / current_sales * 100) if current_sales > 0 else 0

    # 4. 促销活动效果
    promotion_products = data['promotion_data']['产品代码'].unique()
    promotion_sales = current_year_data[current_year_data['产品代码'].isin(promotion_products)]['销售额'].sum()
    promotion_effect = (promotion_sales / current_sales * 100) if current_sales > 0 else 0

    # 5. 新品占比
    new_product_ratio = (new_sales / current_sales * 100) if current_sales > 0 else 0

    # 6. 新品渗透率
    if selected_region == '全部':
        total_regions = sales_df['区域'].nunique()
        new_product_regions = sales_df[sales_df['产品代码'].isin(data['new_products'])]['区域'].nunique()
    else:
        total_regions = 1
        new_product_regions = 1 if len(
            current_year_data[current_year_data['产品代码'].isin(data['new_products'])]) > 0 else 0

    penetration_rate = (new_product_regions / total_regions * 100) if total_regions > 0 else 0

    return {
        'total_sales': current_sales,
        'total_volume': current_volume,
        'sales_growth': sales_growth,
        'volume_growth': volume_growth,
        'category_stats': category_stats,
        'kpi_achievement': kpi_achievement,
        'star_achievement': star_achievement,
        'new_achievement': new_achievement,
        'promotion_effect': promotion_effect,
        'new_product_ratio': new_product_ratio,
        'penetration_rate': penetration_rate,
        'product_df': product_df
    }


# 关键指标总览标签页
def render_key_metrics_tab(metrics):
    """渲染关键指标总览标签页"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # 标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #1e40af, #FFD700); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   margin-bottom: 0.5rem;">关键指标总览</h1>
        <p style="color: #475569; font-size: 1.1rem;">数据驱动的产品组合洞察</p>
    </div>
    """, unsafe_allow_html=True)

    # 创建两行三列布局
    col1, col2, col3 = st.columns(3)

    with col1:
        # 总销售额指标
        sales_status = "良好" if metrics['sales_growth'] > 0 else "需关注"
        status_class = "status-good" if metrics['sales_growth'] > 0 else "status-danger"
        change_class = "change-positive" if metrics['sales_growth'] > 0 else "change-negative"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='sales'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                总销售额
            </div>
            <div class="metric-value">¥{metrics['total_sales']:,.0f}</div>
            <div class="metric-change {change_class}">
                {metrics['sales_growth']:+.1f}% 同比
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {sales_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 产品矩阵占比
        cash_cow_ratio = metrics['category_stats'].get('现金牛产品', 0)
        matrix_status = "达标" if 45 <= cash_cow_ratio <= 50 else "偏离目标"
        status_class = "status-good" if 45 <= cash_cow_ratio <= 50 else "status-warning"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='matrix'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                现金牛产品占比
            </div>
            <div class="metric-value">{cash_cow_ratio:.1f}%</div>
            <div class="metric-change change-neutral">
                目标: 45%-50%
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {matrix_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # KPI达成率
        kpi_status = "已达成" if metrics['kpi_achievement'] >= 20 else "进行中"
        status_class = "status-good" if metrics['kpi_achievement'] >= 20 else "status-warning"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='kpi'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                星品&新品KPI达成率
            </div>
            <div class="metric-value">{metrics['kpi_achievement']:.1f}%</div>
            <div class="metric-change change-neutral">
                目标: 20%
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {kpi_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 第二行
    col4, col5, col6 = st.columns(3)

    with col4:
        # 促销活动效果
        promotion_status = "有效" if metrics['promotion_effect'] > 5 else "一般"
        status_class = "status-good" if metrics['promotion_effect'] > 5 else "status-warning"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='promotion'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                促销活动效果
            </div>
            <div class="metric-value">{metrics['promotion_effect']:.1f}%</div>
            <div class="metric-change change-neutral">
                销售额占比
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {promotion_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        # 新品占比
        new_status = "良好" if metrics['new_product_ratio'] > 15 else "需提升"
        status_class = "status-good" if metrics['new_product_ratio'] > 15 else "status-warning"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='newproduct'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                新品占比
            </div>
            <div class="metric-value">{metrics['new_product_ratio']:.1f}%</div>
            <div class="metric-change change-neutral">
                销售额占比
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {new_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        # 新品渗透率
        penetration_status = "优秀" if metrics['penetration_rate'] > 80 else "良好" if metrics[
                                                                                           'penetration_rate'] > 60 else "需改善"
        status_class = "status-good" if metrics['penetration_rate'] > 80 else "status-warning" if metrics[
                                                                                                      'penetration_rate'] > 60 else "status-danger"

        st.markdown(f"""
        <div class="metric-card" onclick="window.location.hash='penetration'">
            <div class="metric-label">
                <span class="status-indicator {status_class}"></span>
                新品渗透率
            </div>
            <div class="metric-value">{metrics['penetration_rate']:.1f}%</div>
            <div class="metric-change change-neutral">
                区域覆盖率
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #475569;">
                状态: {penetration_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 总结信息
    st.markdown("""
    <div class="main-container" style="margin-top: 2rem;">
        <h3 style="color: #1e40af; margin-bottom: 1rem;">📊 总体评估</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <h4 style="color: #22c55e;">✅ 表现良好</h4>
                <ul style="color: #1e3a8a; line-height: 1.8;">
                    <li>新品渗透率覆盖较广</li>
                    <li>产品组合结构基本合理</li>
                </ul>
            </div>
            <div>
                <h4 style="color: #f59e0b;">⚠️ 需要关注</h4>
                <ul style="color: #1e3a8a; line-height: 1.8;">
                    <li>持续监控KPI达成进度</li>
                    <li>优化促销活动效果</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# BCG矩阵分析图
def render_bcg_matrix(data, selected_region, product_mapping):
    """渲染BCG产品矩阵分析图"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">产品组合全景分析 - BCG矩阵</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    # 时间筛选：2025年1-5月 vs 2024年1-5月
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]
    last_year_data = sales_df[(sales_df['年份'] == 2024) & (sales_df['月份'] <= 5)]

    # 计算产品指标
    total_sales = current_year_data['销售额'].sum()
    product_metrics = []

    for product in current_year_data['产品代码'].unique():
        # 当前年度该产品销售
        product_current = current_year_data[current_year_data['产品代码'] == product]['销售额'].sum()
        # 去年同期该产品销售
        product_last = last_year_data[last_year_data['产品代码'] == product]['销售额'].sum()

        product_share = (product_current / total_sales * 100) if total_sales > 0 else 0
        growth_rate = ((product_current - product_last) / product_last * 100) if product_last > 0 else 0

        # 产品类型
        if product in data['new_products']:
            product_type = '新品'
        elif product in data['star_new_products']:
            product_type = '星品'
        else:
            product_type = '普通品'

        # BCG分类
        if product_share < 1.5 and growth_rate > 20:
            category = '问号产品'
        elif product_share >= 1.5 and growth_rate > 20:
            category = '明星产品'
        elif product_share < 1.5 and growth_rate <= 20:
            category = '瘦狗产品'
        else:
            category = '现金牛产品'

        # 获取产品显示名称
        display_name = get_product_display_name(product, product_mapping)

        product_metrics.append({
            '产品代码': product,
            '产品简称': display_name,
            '销售占比': product_share,
            '成长率': growth_rate,
            '类别': category,
            '销售额': product_current,
            '产品类型': product_type
        })

    df = pd.DataFrame(product_metrics)

    if len(df) == 0:
        st.warning("没有找到符合条件的产品数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 创建BCG矩阵散点图
    fig = go.Figure()

    # 不同类别的颜色
    colors = {
        '问号产品': '#f59e0b',
        '明星产品': '#22c55e',
        '瘦狗产品': '#ef4444',
        '现金牛产品': '#3b82f6'
    }

    # 不同产品类型的形状
    symbols = {
        '新品': 'circle',
        '星品': 'diamond',
        '普通品': 'square'
    }

    for category in df['类别'].unique():
        category_data = df[df['类别'] == category]

        for product_type in category_data['产品类型'].unique():
            type_data = category_data[category_data['产品类型'] == product_type]

            fig.add_trace(go.Scatter(
                x=type_data['销售占比'],
                y=type_data['成长率'],
                mode='markers',
                marker=dict(
                    size=np.maximum(type_data['销售额'] / 50000, 10),  # 调整气泡大小，最小10
                    color=colors[category],
                    symbol=symbols[product_type],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                name=f'{category}-{product_type}',
                text=type_data['产品简称'],
                customdata=type_data[['产品代码', '销售额']],
                hovertemplate=(
                        '<b>%{text}</b><br>' +
                        '产品代码: %{customdata[0]}<br>' +
                        '销售占比: %{x:.2f}%<br>' +
                        '成长率: %{y:.2f}%<br>' +
                        '销售额: ¥%{customdata[1]:,.0f}<br>' +
                        f'类别: {category}<br>' +
                        f'类型: {product_type}<extra></extra>'
                )
            ))

    # 添加象限分割线
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(30, 64, 175, 0.5)", line_width=2)
    fig.add_vline(x=1.5, line_dash="dash", line_color="rgba(30, 64, 175, 0.5)", line_width=2)

    # 添加象限标签
    max_x = df['销售占比'].max() if len(df) > 0 else 5
    max_y = df['成长率'].max() if len(df) > 0 else 50

    fig.add_annotation(x=0.7, y=max_y * 0.8, text="问号产品", showarrow=False,
                       font=dict(size=14, color="#f59e0b", weight="bold"))
    fig.add_annotation(x=max_x * 0.7, y=max_y * 0.8, text="明星产品", showarrow=False,
                       font=dict(size=14, color="#22c55e", weight="bold"))
    fig.add_annotation(x=0.7, y=10, text="瘦狗产品", showarrow=False,
                       font=dict(size=14, color="#ef4444", weight="bold"))
    fig.add_annotation(x=max_x * 0.7, y=10, text="现金牛产品", showarrow=False,
                       font=dict(size=14, color="#3b82f6", weight="bold"))

    # 添加JBP目标区域
    fig.add_shape(
        type="rect",
        x0=1.5, y0=-20, x1=max_x, y1=20,
        fillcolor="rgba(59, 130, 246, 0.1)",
        line=dict(width=0),
    )
    fig.add_annotation(x=max_x * 0.5, y=0, text="现金牛目标区域<br>(45%-50%)",
                       showarrow=False, font=dict(size=12, color="#3b82f6"))

    # 更新布局
    fig.update_layout(
        title=dict(
            text="BCG产品矩阵 - 产品生命周期全景",
            x=0.5,
            font=dict(size=20, color="#1e40af")
        ),
        xaxis=dict(
            title="销售占比 (%)",
            gridcolor="rgba(30, 64, 175, 0.1)",
            tickfont=dict(color="#1e3a8a")
        ),
        yaxis=dict(
            title="成长率 (%)",
            gridcolor="rgba(30, 64, 175, 0.1)",
            tickfont=dict(color="#1e3a8a")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e40af"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(30, 64, 175, 0.3)",
            borderwidth=1
        ),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # JBP计划达成度分析
    col1, col2 = st.columns(2)

    with col1:
        # 当前占比 vs 目标占比
        current_ratios = df.groupby('类别')['销售占比'].sum()

        fig_target = go.Figure()

        categories = ['现金牛产品', '明星产品', '问号产品', '瘦狗产品']
        current_values = [current_ratios.get(cat, 0) for cat in categories]
        target_values = [47.5, 22.5, 22.5, 10]  # JBP目标中位数

        fig_target.add_trace(go.Bar(
            x=categories,
            y=current_values,
            name='当前占比',
            marker_color='#1e40af',
            opacity=0.8
        ))

        fig_target.add_trace(go.Bar(
            x=categories,
            y=target_values,
            name='目标占比',
            marker_color='#FFD700',
            opacity=0.6
        ))

        fig_target.update_layout(
            title="JBP计划达成度对比",
            xaxis_title="产品类别",
            yaxis_title="占比 (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e40af"),
            legend=dict(bgcolor="rgba(255,255,255,0.8)"),
            height=400
        )

        st.plotly_chart(fig_target, use_container_width=True)

    with col2:
        # 产品类型分布
        type_distribution = df.groupby('产品类型')['销售额'].sum()

        fig_pie = go.Figure(data=[go.Pie(
            labels=type_distribution.index,
            values=type_distribution.values,
            hole=0.4,
            marker=dict(
                colors=['#22c55e', '#1e40af', '#FFD700'],
                line=dict(color='#ffffff', width=2)
            ),
            textfont=dict(color="#1e40af")
        )])

        fig_pie.update_layout(
            title="产品类型销售额分布",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e40af"),
            height=400
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 促销效果分析图
def render_promotion_analysis(data, selected_region, product_mapping):
    """渲染促销效果综合分析图"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">促销效果综合分析</h2>', unsafe_allow_html=True)

    # 数据准备
    sales_df = data['sales_data'].copy()
    promotion_df = data['promotion_data'].copy()

    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]
        promotion_df = promotion_df[promotion_df['所属区域'] == selected_region]

    # 促销产品分析
    promotion_products = promotion_df['产品代码'].unique()

    # 计算促销前后效果
    promotion_effects = []

    for product in promotion_products:
        product_sales = sales_df[sales_df['产品代码'] == product]

        # 促销前基准（2024年同期1-5月）
        baseline_sales = product_sales[(product_sales['年份'] == 2024) & (product_sales['月份'] <= 5)]['箱数'].sum()

        # 促销期间销售（2025年1-5月）
        promo_sales = product_sales[(product_sales['年份'] == 2025) & (product_sales['月份'] <= 5)]['箱数'].sum()

        # 预期销量
        expected_sales = promotion_df[promotion_df['产品代码'] == product]['预计销量（箱）'].sum()

        # 效果计算
        if baseline_sales > 0:
            effect_rate = ((promo_sales - baseline_sales) / baseline_sales * 100)
        else:
            effect_rate = 0

        achievement_rate = (promo_sales / expected_sales * 100) if expected_sales > 0 else 0

        # 获取产品显示名称
        display_name = get_product_display_name(product, product_mapping)

        promotion_effects.append({
            '产品代码': product,
            '产品名称': display_name,
            '基准销量': baseline_sales,
            '实际销量': promo_sales,
            '预期销量': expected_sales,
            '提升效果': effect_rate,
            '达成率': achievement_rate
        })

    effect_df = pd.DataFrame(promotion_effects)

    if len(effect_df) == 0:
        st.warning("没有找到促销产品数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 创建组合图表
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('促销效果对比', '达成率分析', '区域促销表现', '时间趋势分析'),
        specs=[[{"secondary_y": True}, {"type": "bar"}],
               [{"type": "bar"}, {"secondary_y": True}]]
    )

    # 第一个子图：促销效果对比
    fig.add_trace(
        go.Bar(
            x=effect_df['产品名称'],
            y=effect_df['基准销量'],
            name='基准销量',
            marker_color='rgba(148, 163, 184, 0.7)',
            opacity=0.7
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=effect_df['产品名称'],
            y=effect_df['实际销量'],
            name='实际销量',
            marker_color='#1e40af',
            opacity=0.8
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=effect_df['产品名称'],
            y=effect_df['提升效果'],
            mode='lines+markers',
            name='提升效果(%)',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1, secondary_y=True
    )

    # 第二个子图：达成率分析
    colors = ['#22c55e' if x >= 100 else '#f59e0b' if x >= 80 else '#ef4444' for x in effect_df['达成率']]

    fig.add_trace(
        go.Bar(
            x=effect_df['产品名称'],
            y=effect_df['达成率'],
            name='达成率',
            marker_color=colors,
            opacity=0.8
        ),
        row=1, col=2
    )

    # 第三个子图：区域促销表现
    if selected_region == '全部':
        region_performance = promotion_df.groupby('所属区域').agg({
            '预计销量（箱）': 'sum',
            '预计销售额（元）': 'sum'
        }).reset_index()

        fig.add_trace(
            go.Bar(
                x=region_performance['所属区域'],
                y=region_performance['预计销量（箱）'],
                name='预计销量',
                marker_color='#FFD700',
                opacity=0.8
            ),
            row=2, col=1
        )

    # 第四个子图：时间趋势分析
    monthly_sales = sales_df[sales_df['产品代码'].isin(promotion_products)].groupby(['年份', '月份']).agg({
        '箱数': 'sum',
        '销售额': 'sum'
    }).reset_index()

    monthly_sales['时间'] = monthly_sales['年份'].astype(str) + '-' + monthly_sales['月份'].astype(str).str.zfill(2)

    fig.add_trace(
        go.Scatter(
            x=monthly_sales['时间'],
            y=monthly_sales['箱数'],
            mode='lines+markers',
            name='销量趋势',
            line=dict(color='#1e40af', width=3),
            marker=dict(size=6)
        ),
        row=2, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_sales['时间'],
            y=monthly_sales['销售额'],
            mode='lines+markers',
            name='销售额趋势',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=6),
            yaxis='y2'
        ),
        row=2, col=2, secondary_y=True
    )

    # 更新布局
    fig.update_layout(
        height=800,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e40af"),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(30, 64, 175, 0.3)",
            borderwidth=1
        )
    )

    # 更新坐标轴
    fig.update_xaxes(tickfont=dict(color="#1e3a8a"), gridcolor="rgba(30, 64, 175, 0.1)")
    fig.update_yaxes(tickfont=dict(color="#1e3a8a"), gridcolor="rgba(30, 64, 175, 0.1)")

    st.plotly_chart(fig, use_container_width=True)

    # 促销效果总结
    avg_effect = effect_df['提升效果'].mean()
    avg_achievement = effect_df['达成率'].mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">平均提升效果</div>
            <div class="metric-value" style="color: {'#22c55e' if avg_effect > 0 else '#ef4444'};">
                {avg_effect:+.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">平均达成率</div>
            <div class="metric-value" style="color: {'#22c55e' if avg_achievement >= 100 else '#f59e0b' if avg_achievement >= 80 else '#ef4444'};">
                {avg_achievement:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">促销产品数量</div>
            <div class="metric-value" style="color: #1e40af;">
                {len(promotion_products)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# KPI达成仪表板 - 改为卡片显示
def render_kpi_dashboard(data, selected_region, metrics):
    """渲染KPI达成仪表板 - 使用卡片替代仪表盘"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">星品&新品KPI达成仪表板</h2>', unsafe_allow_html=True)

    # 三张独立达成率卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        # 星品达成率卡片
        star_status = "已达成" if metrics['star_achievement'] >= 20 else "进行中" if metrics[
                                                                                         'star_achievement'] >= 15 else "需关注"
        star_color = "#22c55e" if metrics['star_achievement'] >= 20 else "#f59e0b" if metrics[
                                                                                          'star_achievement'] >= 15 else "#ef4444"
        star_status_class = "change-positive" if metrics['star_achievement'] >= 20 else "change-neutral" if metrics[
                                                                                                                'star_achievement'] >= 15 else "change-negative"

        st.markdown(f"""
        <div class="achievement-card">
            <div class="achievement-title">星品达成率</div>
            <div class="achievement-value" style="color: {star_color};">{metrics['star_achievement']:.1f}%</div>
            <div class="achievement-target">目标: 20% | 差距: {20 - metrics['star_achievement']:+.1f}%</div>
            <div class="achievement-status {star_status_class}">{star_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 新品达成率卡片
        new_status = "已达成" if metrics['new_achievement'] >= 20 else "进行中" if metrics[
                                                                                       'new_achievement'] >= 15 else "需关注"
        new_color = "#22c55e" if metrics['new_achievement'] >= 20 else "#f59e0b" if metrics[
                                                                                        'new_achievement'] >= 15 else "#ef4444"
        new_status_class = "change-positive" if metrics['new_achievement'] >= 20 else "change-neutral" if metrics[
                                                                                                              'new_achievement'] >= 15 else "change-negative"

        st.markdown(f"""
        <div class="achievement-card">
            <div class="achievement-title">新品达成率</div>
            <div class="achievement-value" style="color: {new_color};">{metrics['new_achievement']:.1f}%</div>
            <div class="achievement-target">目标: 20% | 差距: {20 - metrics['new_achievement']:+.1f}%</div>
            <div class="achievement-status {new_status_class}">{new_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # 综合达成率卡片
        total_status = "已达成" if metrics['kpi_achievement'] >= 20 else "进行中" if metrics[
                                                                                         'kpi_achievement'] >= 15 else "需关注"
        total_color = "#22c55e" if metrics['kpi_achievement'] >= 20 else "#f59e0b" if metrics[
                                                                                          'kpi_achievement'] >= 15 else "#ef4444"
        total_status_class = "change-positive" if metrics['kpi_achievement'] >= 20 else "change-neutral" if metrics[
                                                                                                                'kpi_achievement'] >= 15 else "change-negative"

        st.markdown(f"""
        <div class="achievement-card">
            <div class="achievement-title">综合达成率</div>
            <div class="achievement-value" style="color: {total_color};">{metrics['kpi_achievement']:.1f}%</div>
            <div class="achievement-target">目标: 20% | 差距: {20 - metrics['kpi_achievement']:+.1f}%</div>
            <div class="achievement-status {total_status_class}">{total_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # 各区域KPI表现雷达图
    sales_df = data['sales_data'].copy()
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    # 时间筛选：2025年1-5月
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]

    if selected_region == '全部':
        st.markdown("#### 各区域KPI表现")

        region_kpi = []
        for region in current_year_data['区域'].unique():
            region_data = current_year_data[current_year_data['区域'] == region]
            region_total = region_data['销售额'].sum()
            region_star_new = region_data[region_data['产品代码'].isin(data['star_new_products'])]['销售额'].sum()
            region_kpi_rate = (region_star_new / region_total * 100) if region_total > 0 else 0

            region_kpi.append({
                '区域': region,
                'KPI达成率': region_kpi_rate
            })

        region_df = pd.DataFrame(region_kpi)

        if len(region_df) > 0:
            fig_radar = go.Figure()

            fig_radar.add_trace(go.Scatterpolar(
                r=region_df['KPI达成率'],
                theta=region_df['区域'],
                fill='toself',
                name='KPI达成率',
                marker=dict(color='#1e40af'),
                line=dict(color='#1e40af', width=2)
            ))

            # 添加目标线
            fig_radar.add_trace(go.Scatterpolar(
                r=[20] * len(region_df),
                theta=region_df['区域'],
                mode='lines',
                name='目标线 (20%)',
                line=dict(color='#22c55e', width=2, dash='dash')
            ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(region_df['KPI达成率'].max(), 25)],
                        color="#1e3a8a"
                    ),
                    angularaxis=dict(color="#1e3a8a")
                ),
                title="各区域KPI达成率对比",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1e40af"),
                height=400
            )

            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 新品渗透分析
def render_penetration_analysis(data, selected_region, product_mapping):
    """渲染新品市场渗透分析"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">新品市场渗透动态分析</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    # 时间筛选：2025年1-5月
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]

    # 新品数据
    new_product_sales = current_year_data[current_year_data['产品代码'].isin(data['new_products'])]

    # 区域渗透率分析
    region_penetration = []
    for region in current_year_data['区域'].unique():
        region_data = current_year_data[current_year_data['区域'] == region]
        region_new_data = new_product_sales[new_product_sales['区域'] == region]

        total_customers = region_data['客户名称'].nunique()
        new_customers = region_new_data['客户名称'].nunique()
        penetration_rate = (new_customers / total_customers * 100) if total_customers > 0 else 0

        region_penetration.append({
            '区域': region,
            '渗透率': penetration_rate,
            '总客户数': total_customers,
            '新品客户数': new_customers,
            '新品销售额': region_new_data['销售额'].sum()
        })

    penetration_df = pd.DataFrame(region_penetration)

    if len(penetration_df) == 0:
        st.warning("没有找到新品数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('区域渗透率', '客户渗透散点图', '新品销量趋势', '新品排行榜'),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"secondary_y": True}, {"type": "bar"}]]
    )

    # 第一个子图：区域渗透率
    colors = ['#22c55e' if x > 80 else '#f59e0b' if x > 60 else '#ef4444' for x in penetration_df['渗透率']]

    fig.add_trace(
        go.Bar(
            x=penetration_df['区域'],
            y=penetration_df['渗透率'],
            name='渗透率',
            marker=dict(color=colors, opacity=0.8),
            text=[f'{x:.1f}%' for x in penetration_df['渗透率']],
            textposition='outside'
        ),
        row=1, col=1
    )

    # 第二个子图：客户渗透散点图
    fig.add_trace(
        go.Scatter(
            x=penetration_df['总客户数'],
            y=penetration_df['新品客户数'],
            mode='markers',
            marker=dict(
                size=np.maximum(penetration_df['新品销售额'] / 20000, 10),
                color=penetration_df['渗透率'],
                colorscale='Viridis',
                showscale=True,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            name='客户渗透',
            text=penetration_df['区域'],
            hovertemplate=(
                    '<b>%{text}</b><br>' +
                    '总客户数: %{x}<br>' +
                    '新品客户数: %{y}<br>' +
                    '渗透率: %{marker.color:.1f}%<br>' +
                    '新品销售额: ¥%{marker.size:,.0f}<extra></extra>'
            )
        ),
        row=1, col=2
    )

    # 第三个子图：新品销量趋势
    if len(new_product_sales) > 0:
        monthly_new_sales = new_product_sales.groupby(['年份', '月份']).agg({
            '箱数': 'sum',
            '销售额': 'sum'
        }).reset_index()

        if len(monthly_new_sales) > 0:
            monthly_new_sales['时间'] = monthly_new_sales['年份'].astype(str) + '-' + monthly_new_sales['月份'].astype(
                str).str.zfill(2)

            fig.add_trace(
                go.Scatter(
                    x=monthly_new_sales['时间'],
                    y=monthly_new_sales['箱数'],
                    mode='lines+markers',
                    name='新品销量',
                    line=dict(color='#1e40af', width=3),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=monthly_new_sales['时间'],
                    y=monthly_new_sales['销售额'],
                    mode='lines+markers',
                    name='新品销售额',
                    line=dict(color='#22c55e', width=3),
                    marker=dict(size=6),
                    yaxis='y2'
                ),
                row=2, col=1, secondary_y=True
            )

    # 第四个子图：新品排行榜
    if len(new_product_sales) > 0:
        new_product_ranking = new_product_sales.groupby('产品代码')['销售额'].sum().sort_values(ascending=False).head(
            10)

        # 获取产品显示名称
        ranking_names = [get_product_display_name(code, product_mapping) for code in new_product_ranking.index]

        fig.add_trace(
            go.Bar(
                x=new_product_ranking.values,
                y=ranking_names,
                orientation='h',
                name='新品销售额',
                marker=dict(
                    color=new_product_ranking.values,
                    colorscale='Plasma',
                    opacity=0.8
                ),
                text=[f'¥{x:,.0f}' for x in new_product_ranking.values],
                textposition='inside'
            ),
            row=2, col=2
        )

    # 更新布局
    fig.update_layout(
        height=800,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e40af"),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(30, 64, 175, 0.3)",
            borderwidth=1
        )
    )

    # 更新坐标轴
    fig.update_xaxes(tickfont=dict(color="#1e3a8a"), gridcolor="rgba(30, 64, 175, 0.1)")
    fig.update_yaxes(tickfont=dict(color="#1e3a8a"), gridcolor="rgba(30, 64, 175, 0.1)")

    st.plotly_chart(fig, use_container_width=True)

    # 渗透率总结指标
    avg_penetration = penetration_df['渗透率'].mean()
    max_penetration = penetration_df['渗透率'].max()
    min_penetration = penetration_df['渗透率'].min()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">平均渗透率</div>
            <div class="metric-value" style="color: {'#22c55e' if avg_penetration > 70 else '#f59e0b' if avg_penetration > 50 else '#ef4444'};">
                {avg_penetration:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">最高渗透率</div>
            <div class="metric-value" style="color: #22c55e;">
                {max_penetration:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">最低渗透率</div>
            <div class="metric-value" style="color: #ef4444;">
                {min_penetration:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">新品数量</div>
            <div class="metric-value" style="color: #1e40af;">
                {len(data['new_products'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; background: linear-gradient(135deg, #1e40af, #FFD700); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            🎯 产品组合分析
        </h1>
        <p style="color: #475569; font-size: 1.2rem; margin-bottom: 2rem;">
            Clay.com风格的高级数据可视化分析平台
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner('正在加载数据...'):
        data = load_data()

    if data is None:
        st.error("数据加载失败，请检查数据文件是否存在。")
        return

    # 创建产品简称映射
    product_mapping = create_product_mapping(data['sales_data'], data['promotion_data'])

    # 侧边栏筛选器
    st.sidebar.markdown("""
    <div class="filter-container">
        <h3 style="color: #1e40af; margin-bottom: 1rem;">🔍 筛选器</h3>
    </div>
    """, unsafe_allow_html=True)

    regions = ['全部'] + list(data['sales_data']['区域'].unique())
    selected_region = st.sidebar.selectbox('选择区域', regions, index=0)

    # 计算关键指标
    metrics = calculate_key_metrics(data, selected_region)

    # 标签页
    tabs = st.tabs([
        "📊 关键指标总览",
        "🎯 产品组合全景",
        "🚀 促销效果分析",
        "📈 KPI达成仪表板",
        "🌟 新品渗透分析"
    ])

    with tabs[0]:
        render_key_metrics_tab(metrics)

    with tabs[1]:
        render_bcg_matrix(data, selected_region, product_mapping)

    with tabs[2]:
        render_promotion_analysis(data, selected_region, product_mapping)

    with tabs[3]:
        render_kpi_dashboard(data, selected_region, metrics)

    with tabs[4]:
        render_penetration_analysis(data, selected_region, product_mapping)

    # 页脚
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; border-top: 1px solid rgba(30, 64, 175, 0.2); margin-top: 3rem;">
        <p style="color: #475569; font-size: 0.9rem;">
            产品组合分析仪表盘 | 版本 7.0.0 | 基于Clay.com设计风格
        </p>
        <p style="color: #64748b; font-size: 0.8rem;">
            数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()