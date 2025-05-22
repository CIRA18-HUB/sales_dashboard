# 产品组合分析页面 - Tableau风格设计 v9.0
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
from scipy.stats import pearsonr

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tableau风格CSS样式
st.markdown("""
<style>
    /* Tableau经典配色方案 */
    :root {
        --tableau-bg: linear-gradient(135deg, #f7f9fc 0%, #e8f1f8 100%);
        --tableau-card-bg: #ffffff;
        --tableau-border: #d1d9e0;
        --tableau-text-primary: #2c3e50;
        --tableau-text-secondary: #5a6c7d;
        --tableau-text-title: #1f4e79;

        /* Tableau经典10色数据色板 */
        --tableau-blue: #1f77b4;
        --tableau-orange: #ff7f0e;
        --tableau-green: #2ca02c;
        --tableau-red: #d62728;
        --tableau-purple: #9467bd;
        --tableau-brown: #8c564b;
        --tableau-pink: #e377c2;
        --tableau-gray: #7f7f7f;
        --tableau-olive: #bcbd22;
        --tableau-cyan: #17becf;
    }

    /* 全局样式 */
    .stApp {
        background: var(--tableau-bg);
        color: var(--tableau-text-primary);
    }

    /* 主容器 */
    .main-container {
        background: var(--tableau-card-bg);
        border: 1px solid var(--tableau-border);
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(31, 78, 121, 0.1);
        transition: all 0.3s ease;
    }

    .main-container:hover {
        box-shadow: 0 8px 25px rgba(31, 78, 121, 0.15);
    }

    /* 指标卡片样式 */
    .metric-card {
        background: var(--tableau-card-bg);
        border: 1px solid var(--tableau-border);
        border-radius: 8px;
        padding: 24px;
        margin: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(31, 78, 121, 0.1);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--tableau-blue), var(--tableau-orange));
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(31, 78, 121, 0.15);
        border-color: var(--tableau-blue);
    }

    .metric-title {
        color: var(--tableau-text-title);
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 8px 0;
        animation: countUp 1s ease-out;
    }

    .metric-change {
        font-size: 0.9rem;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 8px;
    }

    .change-positive {
        color: var(--tableau-green);
        background: rgba(44, 160, 44, 0.1);
    }

    .change-negative {
        color: var(--tableau-red);
        background: rgba(214, 39, 40, 0.1);
    }

    .change-neutral {
        color: var(--tableau-text-secondary);
        background: rgba(90, 108, 125, 0.1);
    }

    /* 不同指标的主色调 */
    .sales .metric-value { color: var(--tableau-blue); }
    .jbp .metric-value { color: var(--tableau-green); }
    .kpi .metric-value { color: var(--tableau-orange); }
    .promotion .metric-value { color: var(--tableau-purple); }
    .newproduct .metric-value { color: var(--tableau-red); }
    .penetration .metric-value { color: var(--tableau-cyan); }
    .star .metric-value { color: var(--tableau-brown); }
    .concentration .metric-value { color: var(--tableau-pink); }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--tableau-card-bg);
        border-radius: 8px;
        padding: 8px;
        border: 1px solid var(--tableau-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 6px;
        color: var(--tableau-text-secondary);
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 12px 20px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(31, 119, 180, 0.1);
        color: var(--tableau-blue);
    }

    .stTabs [aria-selected="true"] {
        background: var(--tableau-blue);
        color: white !important;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.3);
    }

    /* 图表容器 */
    .chart-container {
        background: var(--tableau-card-bg);
        border: 1px solid var(--tableau-border);
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(31, 78, 121, 0.1);
    }

    .chart-title {
        color: var(--tableau-text-title);
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 20px 0;
        border-bottom: 2px solid var(--tableau-border);
        padding-bottom: 10px;
    }

    /* 筛选器样式 */
    .filter-container {
        background: var(--tableau-card-bg);
        border: 1px solid var(--tableau-border);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(31, 78, 121, 0.1);
    }

    /* 动画效果 */
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-card {
            margin: 8px 0;
        }
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# 数据加载和验证函数
@st.cache_data
def load_data():
    """加载所有数据文件并进行验证"""
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

        # 数据验证
        if len(sales_data) == 0:
            st.error("❌ 销售数据为空")
            return None

        if len(promotion_data) == 0:
            st.error("❌ 促销数据为空")
            return None

        return {
            'sales_data': sales_data,
            'promotion_data': promotion_data,
            'star_new_products': star_new_products,
            'new_products': new_products,
            'dashboard_products': dashboard_products
        }
    except Exception as e:
        st.error(f"❌ 数据加载错误: {str(e)}")
        return None


def safe_render_chart(data, chart_func, chart_title, *args, **kwargs):
    """安全渲染图表，确保不显示空白"""
    try:
        if data is None or len(data) == 0:
            st.warning(f"⚠️ {chart_title}：暂无数据显示")
            st.info("💡 可能原因：当前筛选条件下没有匹配的数据，请调整筛选器")
            return False

        # 检查是否有数值型数据
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) == 0 and 'BCG' not in chart_title:
            st.warning(f"⚠️ {chart_title}：缺少数值型数据")
            return False

        # 渲染图表
        chart_func(data, *args, **kwargs)
        return True

    except Exception as e:
        st.error(f"❌ {chart_title}渲染失败：{str(e)}")
        st.info("🔧 请检查数据格式或联系技术支持")
        return False


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
    """计算8个关键指标"""
    sales_df = data['sales_data'].copy()

    # 区域筛选
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    # 时间筛选：2025年1-5月 vs 2024年1-5月
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]
    last_year_data = sales_df[(sales_df['年份'] == 2024) & (sales_df['月份'] <= 5)]

    if len(current_year_data) == 0:
        st.warning("⚠️ 当前筛选条件下没有2025年数据")
        return None

    # 1. 总销售额
    current_sales = current_year_data['销售额'].sum()
    last_sales = last_year_data['销售额'].sum()
    sales_growth = ((current_sales - last_sales) / last_sales * 100) if last_sales > 0 else 0

    # 2. BCG矩阵分析
    product_metrics = []
    total_sales = current_year_data['销售额'].sum()

    for product in current_year_data['产品代码'].unique():
        product_current = current_year_data[current_year_data['产品代码'] == product]['销售额'].sum()
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
    category_stats = product_df.groupby('类别')['销售占比'].sum() if len(product_df) > 0 else pd.Series()

    # 3. JBP符合度
    cash_cow_ratio = category_stats.get('现金牛产品', 0)
    star_question_ratio = category_stats.get('明星产品', 0) + category_stats.get('问号产品', 0)
    dog_ratio = category_stats.get('瘦狗产品', 0)

    jbp_compliant = (45 <= cash_cow_ratio <= 50 and 40 <= star_question_ratio <= 45 and dog_ratio <= 10)

    # 4. KPI达成率
    star_new_sales = current_year_data[current_year_data['产品代码'].isin(data['star_new_products'])]['销售额'].sum()
    kpi_achievement = (star_new_sales / current_sales * 100) if current_sales > 0 else 0

    # 5. 星品销售占比
    new_sales = current_year_data[current_year_data['产品代码'].isin(data['new_products'])]['销售额'].sum()
    star_sales = star_new_sales - new_sales
    star_ratio = (star_sales / current_sales * 100) if current_sales > 0 else 0

    # 6. 新品占比
    new_ratio = (new_sales / current_sales * 100) if current_sales > 0 else 0

    # 7. 新品渗透率
    if selected_region == '全部':
        total_regions = sales_df['区域'].nunique()
        new_product_regions = sales_df[sales_df['产品代码'].isin(data['new_products'])]['区域'].nunique()
    else:
        total_regions = 1
        new_product_regions = 1 if len(
            current_year_data[current_year_data['产品代码'].isin(data['new_products'])]) > 0 else 0

    penetration_rate = (new_product_regions / total_regions * 100) if total_regions > 0 else 0

    # 8. 产品集中度
    product_sales = current_year_data.groupby('产品代码')['销售额'].sum().sort_values(ascending=False)
    top5_sales = product_sales.head(5).sum()
    concentration = (top5_sales / current_sales * 100) if current_sales > 0 else 0

    # 9. 促销有效性（全国促销）
    national_promotions = data['promotion_data'][data['promotion_data']['所属区域'] == '全国']
    promotion_effectiveness = calculate_promotion_effectiveness(data, national_promotions)

    return {
        'total_sales': current_sales,
        'sales_growth': sales_growth,
        'jbp_compliant': jbp_compliant,
        'kpi_achievement': kpi_achievement,
        'star_ratio': star_ratio,
        'new_ratio': new_ratio,
        'penetration_rate': penetration_rate,
        'concentration': concentration,
        'promotion_effectiveness': promotion_effectiveness,
        'category_stats': category_stats,
        'product_df': product_df
    }


def calculate_promotion_effectiveness(data, national_promotions):
    """计算全国促销活动有效性"""
    if len(national_promotions) == 0:
        return 0

    sales_df = data['sales_data']
    effective_count = 0

    for _, promo in national_promotions.iterrows():
        product_code = promo['产品代码']

        # 获取该产品的销售数据
        product_sales = sales_df[sales_df['产品代码'] == product_code]

        # 4月销量
        april_2025 = product_sales[(product_sales['年份'] == 2025) & (product_sales['月份'] == 4)]['箱数'].sum()
        # 3月销量
        march_2025 = product_sales[(product_sales['年份'] == 2025) & (product_sales['月份'] == 3)]['箱数'].sum()
        # 去年4月销量
        april_2024 = product_sales[(product_sales['年份'] == 2024) & (product_sales['月份'] == 4)]['箱数'].sum()
        # 2024年平均月销量
        avg_2024 = product_sales[product_sales['年份'] == 2024]['箱数'].mean()

        # 三个基准
        base1 = april_2025 > march_2025
        base2 = april_2025 > april_2024
        base3 = april_2025 > avg_2024

        # 至少两个基准有效
        if sum([base1, base2, base3]) >= 2:
            effective_count += 1

    return (effective_count / len(national_promotions) * 100)


# 渲染指标卡片
def render_metric_card(title, value, change, change_type, card_class, emoji):
    """渲染单个指标卡片"""
    change_class = f"change-{change_type}"

    return f"""
    <div class="metric-card {card_class}" onclick="handleMetricClick('{title}')">
        <div class="metric-title">
            <span style="margin-right: 8px; font-size: 1.2rem;">{emoji}</span>
            {title}
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-change {change_class}">{change}</div>
    </div>
    """


# 第一标签页：关键指标总览
def render_key_metrics_tab(metrics):
    """渲染关键指标总览标签页"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #1f4e79; font-size: 2.5rem; margin-bottom: 0.5rem;">📊 产品情况总览</h1>
        <p style="color: #5a6c7d; font-size: 1.1rem;">基于Tableau风格的专业数据分析驾驶舱</p>
    </div>
    """, unsafe_allow_html=True)

    # 8个指标卡片（4行2列）
    col1, col2 = st.columns(2)

    with col1:
        # 总销售额
        change_type = "positive" if metrics['sales_growth'] > 0 else "negative"
        st.markdown(render_metric_card(
            "总销售额",
            f"¥{metrics['total_sales']:,.0f}",
            f"{metrics['sales_growth']:+.1f}% ↗️" if metrics[
                                                         'sales_growth'] > 0 else f"{metrics['sales_growth']:+.1f}% ↘️",
            change_type,
            "sales",
            "💰"
        ), unsafe_allow_html=True)

        # KPI达成率
        st.markdown(render_metric_card(
            "KPI达成率",
            f"{metrics['kpi_achievement']:.1f}%",
            "目标: 20%",
            "positive" if metrics['kpi_achievement'] >= 20 else "neutral",
            "kpi",
            "🎯"
        ), unsafe_allow_html=True)

        # 新品占比
        st.markdown(render_metric_card(
            "新品占比",
            f"{metrics['new_ratio']:.1f}%",
            "销售额占比",
            "neutral",
            "newproduct",
            "🌟"
        ), unsafe_allow_html=True)

        # 星品销售占比
        st.markdown(render_metric_card(
            "星品销售占比",
            f"{metrics['star_ratio']:.1f}%",
            "销售额占比",
            "neutral",
            "star",
            "⭐"
        ), unsafe_allow_html=True)

    with col2:
        # JBP符合度
        st.markdown(render_metric_card(
            "JBP符合度",
            "是" if metrics['jbp_compliant'] else "否",
            "产品矩阵目标",
            "positive" if metrics['jbp_compliant'] else "negative",
            "jbp",
            "✅"
        ), unsafe_allow_html=True)

        # 促销有效性
        st.markdown(render_metric_card(
            "促销有效性",
            f"{metrics['promotion_effectiveness']:.1f}%",
            "全国促销活动有效",
            "positive" if metrics['promotion_effectiveness'] > 70 else "neutral",
            "promotion",
            "🚀"
        ), unsafe_allow_html=True)

        # 新品渗透率
        st.markdown(render_metric_card(
            "新品渗透率",
            f"{metrics['penetration_rate']:.1f}%",
            "区域覆盖率",
            "positive" if metrics['penetration_rate'] > 80 else "neutral",
            "penetration",
            "📊"
        ), unsafe_allow_html=True)

        # 产品集中度
        st.markdown(render_metric_card(
            "产品集中度",
            f"{metrics['concentration']:.1f}%",
            "TOP5产品占比",
            "neutral",
            "concentration",
            "📊"
        ), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 添加点击跳转的JavaScript
    st.markdown("""
    <script>
    function handleMetricClick(title) {
        // 这里可以添加跳转逻辑
        console.log('点击了指标：', title);
    }
    </script>
    """, unsafe_allow_html=True)


# BCG矩阵分析图
def render_bcg_matrix(data, selected_region, product_mapping):
    """渲染BCG产品矩阵分析图"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">🎯 BCG产品矩阵分析</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()
    if selected_region != '全部':
        sales_df = sales_df[sales_df['区域'] == selected_region]

    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]
    last_year_data = sales_df[(sales_df['年份'] == 2024) & (sales_df['月份'] <= 5)]

    if len(current_year_data) == 0:
        st.warning("⚠️ 没有找到符合条件的数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 计算产品指标
    total_sales = current_year_data['销售额'].sum()
    product_metrics = []

    for product in current_year_data['产品代码'].unique():
        product_current = current_year_data[current_year_data['产品代码'] == product]['销售额'].sum()
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

    # 创建BCG矩阵散点图
    fig = go.Figure()

    # Tableau色彩映射
    colors = {
        '问号产品': '#ff7f0e',  # 橙色
        '明星产品': '#2ca02c',  # 绿色
        '瘦狗产品': '#d62728',  # 红色
        '现金牛产品': '#1f77b4'  # 蓝色
    }

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
                    size=np.maximum(type_data['销售额'] / 50000, 10),
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
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(31, 78, 121, 0.5)", line_width=2)
    fig.add_vline(x=1.5, line_dash="dash", line_color="rgba(31, 78, 121, 0.5)", line_width=2)

    # 更新布局
    fig.update_layout(
        title=dict(
            text="BCG产品矩阵 - 产品生命周期全景",
            x=0.5,
            font=dict(size=20, color="#1f4e79")
        ),
        xaxis=dict(
            title="销售占比 (%)",
            gridcolor="rgba(209, 217, 224, 0.5)",
            tickfont=dict(color="#2c3e50")
        ),
        yaxis=dict(
            title="成长率 (%)",
            gridcolor="rgba(209, 217, 224, 0.5)",
            tickfont=dict(color="#2c3e50")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(209, 217, 224, 0.8)",
            borderwidth=1
        ),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# 铺市机会分析
def render_market_opportunity_analysis(data, selected_region, product_mapping):
    """渲染铺市机会分析"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">🏪 铺市机会分析</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()

    # 计算各产品在各区域的铺市指数
    regions = sales_df['区域'].unique()
    products = sales_df['产品代码'].unique()

    opportunity_data = []

    for product in products:
        product_sales_by_region = sales_df[sales_df['产品代码'] == product].groupby('区域')['销售额'].sum()
        national_avg = product_sales_by_region.mean()

        for region in regions:
            region_sales = product_sales_by_region.get(region, 0)
            market_index = (region_sales / national_avg) if national_avg > 0 else 0

            if market_index < 0.6:
                opportunity_level = "高潜力"
                color_value = 3
            elif market_index < 0.8:
                opportunity_level = "有机会"
                color_value = 2
            else:
                opportunity_level = "饱和"
                color_value = 1

            display_name = get_product_display_name(product, product_mapping)

            opportunity_data.append({
                '产品代码': product,
                '产品简称': display_name,
                '区域': region,
                '铺市指数': market_index,
                '机会等级': opportunity_level,
                '颜色值': color_value,
                '销售额': region_sales
            })

    opportunity_df = pd.DataFrame(opportunity_data)

    if len(opportunity_df) > 0:
        # 创建热力图
        pivot_data = opportunity_df.pivot(index='产品简称', columns='区域', values='颜色值')

        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale=[[0, '#2ca02c'], [0.5, '#ff7f0e'], [1, '#d62728']],
            showscale=True,
            colorbar=dict(
                title="机会等级",
                tickvals=[1, 2, 3],
                ticktext=["饱和", "有机会", "高潜力"]
            )
        ))

        fig.update_layout(
            title="各产品区域铺市机会热力图",
            xaxis_title="区域",
            yaxis_title="产品",
            font=dict(color="#2c3e50"),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # TOP10铺市机会排行
        top_opportunities = opportunity_df[opportunity_df['机会等级'].isin(['高潜力', '有机会'])].nsmallest(10,
                                                                                                            '铺市指数')

        if len(top_opportunities) > 0:
            st.subheader("🎯 TOP10铺市机会排行")

            for _, row in top_opportunities.iterrows():
                st.write(f"**{row['产品简称']}** - {row['区域']} - {row['机会等级']} (指数: {row['铺市指数']:.2f})")

    st.markdown('</div>', unsafe_allow_html=True)


# 促销效果分析
def render_promotion_analysis(data, selected_region, product_mapping):
    """渲染促销效果分析"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">🚀 全国促销效果分析</h2>', unsafe_allow_html=True)

    # 筛选全国促销活动
    national_promotions = data['promotion_data'][data['promotion_data']['所属区域'] == '全国']

    if len(national_promotions) == 0:
        st.warning("⚠️ 没有找到全国促销活动数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    sales_df = data['sales_data']
    promotion_effects = []

    for _, promo in national_promotions.iterrows():
        product_code = promo['产品代码']
        product_sales = sales_df[sales_df['产品代码'] == product_code]

        # 计算各月销量
        april_2025 = product_sales[(product_sales['年份'] == 2025) & (product_sales['月份'] == 4)]['箱数'].sum()
        march_2025 = product_sales[(product_sales['年份'] == 2025) & (product_sales['月份'] == 3)]['箱数'].sum()
        april_2024 = product_sales[(product_sales['年份'] == 2024) & (product_sales['月份'] == 4)]['箱数'].sum()

        display_name = get_product_display_name(product_code, product_mapping)

        promotion_effects.append({
            '产品代码': product_code,
            '产品简称': display_name,
            '3月销量': march_2025,
            '4月销量': april_2025,
            '去年4月': april_2024,
            '环比增长': april_2025 - march_2025,
            '同比增长': april_2025 - april_2024
        })

    effect_df = pd.DataFrame(promotion_effects)

    if len(effect_df) > 0:
        # 创建促销效果对比图
        fig = make_subplots(rows=1, cols=2, subplot_titles=('月度销量对比', '增长效果分析'))

        # 左图：销量对比
        fig.add_trace(
            go.Bar(x=effect_df['产品简称'], y=effect_df['3月销量'], name='3月销量', marker_color='#1f77b4'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=effect_df['产品简称'], y=effect_df['4月销量'], name='4月销量', marker_color='#ff7f0e'),
            row=1, col=2
        )

        # 右图：增长效果
        fig.add_trace(
            go.Bar(x=effect_df['产品简称'], y=effect_df['环比增长'], name='环比增长', marker_color='#2ca02c'),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=effect_df['产品简称'], y=effect_df['同比增长'], name='同比增长', marker_color='#d62728'),
            row=1, col=2
        )

        fig.update_layout(
            title="全国促销活动效果分析",
            height=500,
            font=dict(color="#2c3e50")
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 星品&新品达成分析
def render_kpi_achievement_analysis(data, selected_region):
    """渲染KPI达成分析"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">📈 星品&新品达成分析</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]

    if len(current_year_data) == 0:
        st.warning("⚠️ 没有找到2025年数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 各区域KPI达成情况
    if selected_region == '全部':
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
            # 雷达图
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=region_df['KPI达成率'],
                theta=region_df['区域'],
                fill='toself',
                name='KPI达成率',
                marker=dict(color='#1f77b4'),
                line=dict(color='#1f77b4', width=2)
            ))

            # 添加目标线
            fig.add_trace(go.Scatterpolar(
                r=[20] * len(region_df),
                theta=region_df['区域'],
                mode='lines',
                name='目标线 (20%)',
                line=dict(color='#2ca02c', width=2, dash='dash')
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(region_df['KPI达成率'].max(), 25)]
                    )
                ),
                title="各区域KPI达成率雷达图",
                font=dict(color="#2c3e50"),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

    # 月度达成趋势
    monthly_trend = []
    for month in range(1, 6):
        month_data = current_year_data[current_year_data['月份'] == month]
        month_total = month_data['销售额'].sum()
        month_star_new = month_data[month_data['产品代码'].isin(data['star_new_products'])]['销售额'].sum()
        month_kpi_rate = (month_star_new / month_total * 100) if month_total > 0 else 0

        monthly_trend.append({
            '月份': f"2025-{month:02d}",
            'KPI达成率': month_kpi_rate
        })

    trend_df = pd.DataFrame(monthly_trend)

    if len(trend_df) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_df['月份'],
            y=trend_df['KPI达成率'],
            mode='lines+markers',
            name='KPI达成率',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8)
        ))

        fig.add_hline(y=20, line_dash="dash", line_color="#2ca02c", annotation_text="目标线 20%")

        fig.update_layout(
            title="月度KPI达成趋势",
            xaxis_title="月份",
            yaxis_title="KPI达成率 (%)",
            font=dict(color="#2c3e50"),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 新品渗透分析
def render_penetration_analysis(data, selected_region, product_mapping):
    """渲染新品渗透分析"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="chart-title">🌟 新品渗透分析</h2>', unsafe_allow_html=True)

    sales_df = data['sales_data'].copy()
    current_year_data = sales_df[(sales_df['年份'] == 2025) & (sales_df['月份'] <= 5)]
    new_product_sales = current_year_data[current_year_data['产品代码'].isin(data['new_products'])]

    if len(new_product_sales) == 0:
        st.warning("⚠️ 没有找到新品销售数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 区域渗透热力图
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
            '新品销售额': region_new_data['销售额'].sum()
        })

    penetration_df = pd.DataFrame(region_penetration)

    if len(penetration_df) > 0:
        # 区域渗透柱状图
        fig = go.Figure()
        colors = ['#2ca02c' if x > 80 else '#ff7f0e' if x > 60 else '#d62728' for x in penetration_df['渗透率']]

        fig.add_trace(go.Bar(
            x=penetration_df['区域'],
            y=penetration_df['渗透率'],
            name='渗透率',
            marker=dict(color=colors),
            text=[f'{x:.1f}%' for x in penetration_df['渗透率']],
            textposition='outside'
        ))

        fig.update_layout(
            title="各区域新品渗透率",
            xaxis_title="区域",
            yaxis_title="渗透率 (%)",
            font=dict(color="#2c3e50"),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # 新品与星品关联分析
    st.subheader("🔗 新品与星品关联分析")

    correlation_data = []
    for region in current_year_data['区域'].unique():
        region_data = current_year_data[current_year_data['区域'] == region]

        new_product_sales_region = region_data[region_data['产品代码'].isin(data['new_products'])]['销售额'].sum()
        star_product_sales_region = region_data[region_data['产品代码'].isin(data['star_new_products'])]['销售额'].sum()

        correlation_data.append({
            '区域': region,
            '新品销售额': new_product_sales_region,
            '星品销售额': star_product_sales_region
        })

    corr_df = pd.DataFrame(correlation_data)

    if len(corr_df) > 0 and corr_df['新品销售额'].sum() > 0 and corr_df['星品销售额'].sum() > 0:
        # 计算相关性
        correlation, p_value = pearsonr(corr_df['新品销售额'], corr_df['星品销售额'])

        # 散点图
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=corr_df['星品销售额'],
            y=corr_df['新品销售额'],
            mode='markers',
            marker=dict(
                size=12,
                color='#1f77b4',
                opacity=0.7
            ),
            text=corr_df['区域'],
            hovertemplate='<b>%{text}</b><br>星品销售额: ¥%{x:,.0f}<br>新品销售额: ¥%{y:,.0f}<extra></extra>'
        ))

        fig.update_layout(
            title=f"新品与星品销售关联分析 (相关系数: {correlation:.3f})",
            xaxis_title="星品销售额 (¥)",
            yaxis_title="新品销售额 (¥)",
            font=dict(color="#2c3e50"),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 关联度分析结果
        if correlation > 0.7:
            st.success("🔥 **强关联** - 建议与热销星品捆绑推广新品")
        elif correlation > 0.3:
            st.info("📈 **中等关联** - 可在星品客户中交叉推广新品")
        else:
            st.warning("🎯 **独立销售** - 新品需要独立的营销策略")

    st.markdown('</div>', unsafe_allow_html=True)


# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; color: #1f4e79; margin-bottom: 0.5rem;">
            📊 产品组合分析仪表盘
        </h1>
        <p style="color: #5a6c7d; font-size: 1.2rem; margin-bottom: 2rem;">
            基于Tableau风格的专业数据分析平台
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner('🔄 正在加载数据...'):
        data = load_data()

    if data is None:
        st.error("❌ 数据加载失败，请检查数据文件是否存在。")
        return

    # 创建产品简称映射
    product_mapping = create_product_mapping(data['sales_data'], data['promotion_data'])

    # 侧边栏筛选器
    st.sidebar.markdown("""
    <div class="filter-container">
        <h3 style="color: #1f4e79; margin-bottom: 1rem;">🔍 数据筛选器</h3>
    </div>
    """, unsafe_allow_html=True)

    regions = ['全部'] + list(data['sales_data']['区域'].unique())
    selected_region = st.sidebar.selectbox('选择区域', regions, index=0)

    # 计算关键指标
    metrics = calculate_key_metrics(data, selected_region)

    if metrics is None:
        st.error("❌ 指标计算失败")
        return

    # 标签页
    tabs = st.tabs([
        "📊 产品情况总览",
        "🎯 产品组合全景",
        "🚀 促销效果分析",
        "📈 星品&新品达成",
        "🌟 新品渗透分析"
    ])

    with tabs[0]:
        render_key_metrics_tab(metrics)

    with tabs[1]:
        safe_render_chart(
            data['sales_data'],
            render_bcg_matrix,
            "BCG产品矩阵",
            data, selected_region, product_mapping
        )
        safe_render_chart(
            data['sales_data'],
            render_market_opportunity_analysis,
            "铺市机会分析",
            data, selected_region, product_mapping
        )

    with tabs[2]:
        safe_render_chart(
            data['promotion_data'],
            render_promotion_analysis,
            "促销效果分析",
            data, selected_region, product_mapping
        )

    with tabs[3]:
        safe_render_chart(
            data['sales_data'],
            render_kpi_achievement_analysis,
            "KPI达成分析",
            data, selected_region
        )

    with tabs[4]:
        safe_render_chart(
            data['sales_data'],
            render_penetration_analysis,
            "新品渗透分析",
            data, selected_region, product_mapping
        )

    # 页脚
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; border-top: 1px solid #d1d9e0; margin-top: 3rem;">
        <p style="color: #5a6c7d; font-size: 0.9rem;">
            产品组合分析仪表盘 | 版本 9.0 | 基于Tableau设计风格
        </p>
        <p style="color: #5a6c7d; font-size: 0.8rem;">
            数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()