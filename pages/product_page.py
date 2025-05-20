# pages/product_page.py - 完全自包含的产品分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# 导入统一配置
from config import (
    COLORS, BCG_COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, load_data_files, create_filters, add_chart_explanation,
    create_flip_card, setup_page
)

# ==================== 页面配置 ====================
setup_page()

# 检查认证
if not check_authentication():
    st.stop()

# 页面标题
st.title("📦 产品分析")

# 加载数据
data = load_data_files()
if not data:
    st.error("无法加载数据文件，请检查文件路径")
    st.stop()

# 应用筛选器
filtered_data = create_filters(data)
if not filtered_data:
    st.error("应用筛选器失败")
    st.stop()


# ==================== 工具函数 ====================
def calculate_product_metrics(sales_data, product_codes=None):
    """计算产品相关指标"""
    if sales_data.empty:
        return {}

    # 筛选符合条件的产品
    if product_codes:
        filtered_sales = sales_data[sales_data['产品代码'].isin(product_codes)].copy()
    else:
        filtered_sales = sales_data.copy()

    if filtered_sales.empty:
        return {}

    # 基础统计
    total_products = filtered_sales['产品代码'].nunique()

    # 产品销售统计
    product_sales = filtered_sales.groupby(['产品代码', '产品简称'])['销售额'].sum().reset_index()
    product_sales['销售占比'] = product_sales['销售额'] / product_sales['销售额'].sum() * 100 if product_sales[
                                                                                                     '销售额'].sum() > 0 else 0

    # 计算去年同期数据
    current_year = datetime.now().year
    last_year = current_year - 1

    last_year_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == last_year]
    if not last_year_sales.empty:
        last_year_product_sales = last_year_sales.groupby(['产品代码'])['销售额'].sum().reset_index()
        last_year_product_sales.rename(columns={'销售额': '去年销售额'}, inplace=True)

        # 合并今年和去年的销售数据
        product_sales = product_sales.merge(last_year_product_sales, on='产品代码', how='left')
        product_sales['去年销售额'] = product_sales['去年销售额'].fillna(0)

        # 计算增长率
        product_sales['增长率'] = (product_sales['销售额'] - product_sales['去年销售额']) / product_sales[
            '去年销售额'] * 100
        product_sales['增长率'] = product_sales['增长率'].fillna(0)
        product_sales.loc[product_sales['去年销售额'] == 0, '增长率'] = 100  # 去年为0，今年有销售的，增长率设为100%
    else:
        # 无去年数据时设置默认增长率
        product_sales['增长率'] = 0
        product_sales['去年销售额'] = 0

    # 根据BCG矩阵分类产品
    product_sales['BCG分类'] = product_sales.apply(
        lambda row: '明星产品' if row['销售占比'] >= 1.5 and row['增长率'] >= 20
        else '现金牛产品' if row['销售占比'] >= 1.5 and row['增长率'] < 20
        else '问号产品' if row['销售占比'] < 1.5 and row['增长率'] >= 20
        else '瘦狗产品',
        axis=1
    )

    # 计算各类产品的销售额和占比
    bcg_summary = product_sales.groupby('BCG分类')['销售额'].sum().reset_index()
    bcg_summary['销售占比'] = bcg_summary['销售额'] / bcg_summary['销售额'].sum() * 100

    # 检查产品组合健康度
    cash_cow_percent = bcg_summary.loc[bcg_summary['BCG分类'] == '现金牛产品', '销售占比'].sum() if '现金牛产品' in \
                                                                                                    bcg_summary[
                                                                                                        'BCG分类'].values else 0
    star_question_percent = bcg_summary.loc[
        bcg_summary['BCG分类'].isin(['明星产品', '问号产品']), '销售占比'].sum() if not bcg_summary.empty else 0
    dog_percent = bcg_summary.loc[bcg_summary['BCG分类'] == '瘦狗产品', '销售占比'].sum() if '瘦狗产品' in bcg_summary[
        'BCG分类'].values else 0

    # 判断是否符合健康产品组合
    is_healthy_mix = (
            (45 <= cash_cow_percent <= 50) and
            (40 <= star_question_percent <= 45) and
            (dog_percent <= 10)
    )

    # 计算健康度指标
    bcg_health_score = 100 - (
            abs(cash_cow_percent - 47.5) * 1.5 +  # 理想值47.5%的偏差
            abs(star_question_percent - 42.5) * 1.5 +  # 理想值42.5%的偏差
            max(0, dog_percent - 10) * 3  # 瘦狗产品超出10%的惩罚
    )

    bcg_health = max(0, min(100, bcg_health_score))

    # 添加产品客户覆盖率
    if '客户代码' in filtered_sales.columns:
        # 计算每个产品的购买客户数
        product_customers = filtered_sales.groupby('产品代码')['客户代码'].nunique().reset_index()
        product_customers.columns = ['产品代码', '购买客户数']

        # 计算总客户数
        total_customers = filtered_sales['客户代码'].nunique()

        # 计算覆盖率
        product_customers['客户覆盖率'] = product_customers[
                                              '购买客户数'] / total_customers * 100 if total_customers > 0 else 0

        # 合并到产品销售数据
        product_sales = product_sales.merge(product_customers, on='产品代码', how='left')

    return {
        'total_products': total_products,
        'product_sales': product_sales,
        'bcg_summary': bcg_summary,
        'is_healthy_mix': is_healthy_mix,
        'bcg_health': bcg_health,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent
    }


# ==================== 分析数据 ====================
def analyze_product_data(filtered_data):
    """分析产品数据"""
    sales_data = filtered_data.get('sales_orders', pd.DataFrame())
    product_codes = filtered_data.get('product_codes', [])

    # 获取当前年份数据
    current_year = datetime.now().year
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]

    # 计算产品指标
    product_metrics = calculate_product_metrics(ytd_sales, product_codes)

    return product_metrics


# ==================== 图表创建函数 ====================
def create_bcg_bubble_chart(product_data, title="产品BCG矩阵分析"):
    """创建BCG矩阵气泡图"""
    if product_data.empty:
        return None

    # 设置BCG矩阵的颜色映射
    color_map = {
        '明星产品': BCG_COLORS['star'],
        '现金牛产品': BCG_COLORS['cash_cow'],
        '问号产品': BCG_COLORS['question'],
        '瘦狗产品': BCG_COLORS['dog']
    }

    # 创建气泡图
    fig = px.scatter(
        product_data,
        x='增长率',
        y='销售占比',
        size='销售额',
        color='BCG分类',
        hover_name='产品简称',
        text='产品简称',
        size_max=50,
        title=title,
        color_discrete_map=color_map
    )

    # 添加分隔线
    fig.add_shape(
        type="line",
        x0=20, y0=0,
        x1=20, y1=max(product_data['销售占比']) * 1.1,
        line=dict(color="gray", width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=min(product_data['增长率']) * 1.1, y0=1.5,
        x1=max(product_data['增长率']) * 1.1, y1=1.5,
        line=dict(color="gray", width=1, dash="dash")
    )

    # 添加象限标签
    annotations = [
        dict(
            x=50, y=4,
            text="明星产品",
            showarrow=False,
            font=dict(size=12, color=BCG_COLORS['star'])
        ),
        dict(
            x=10, y=4,
            text="现金牛产品",
            showarrow=False,
            font=dict(size=12, color=BCG_COLORS['cash_cow'])
        ),
        dict(
            x=50, y=0.5,
            text="问号产品",
            showarrow=False,
            font=dict(size=12, color=BCG_COLORS['question'])
        ),
        dict(
            x=10, y=0.5,
            text="瘦狗产品",
            showarrow=False,
            font=dict(size=12, color=BCG_COLORS['dog'])
        )
    ]

    fig.update_layout(
        annotations=annotations,
        height=500,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="增长率 (%)",
        yaxis_title="销售占比 (%)",
        legend_title="产品分类"
    )

    # 添加悬浮信息
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>销售占比: %{y:.2f}%<br>增长率: %{x:.2f}%<br>销售额: %{marker.size:,.0f}元<extra></extra>'
    )

    return fig


def create_bcg_pie_chart(bcg_data, title="产品组合健康度"):
    """创建BCG分类占比饼图"""
    if bcg_data.empty:
        return None

    # 设置BCG矩阵的颜色映射
    color_map = {
        '明星产品': BCG_COLORS['star'],
        '现金牛产品': BCG_COLORS['cash_cow'],
        '问号产品': BCG_COLORS['question'],
        '瘦狗产品': BCG_COLORS['dog']
    }

    fig = px.pie(
        bcg_data,
        names='BCG分类',
        values='销售占比',
        title=title,
        color='BCG分类',
        color_discrete_map=color_map,
        hole=0.3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def create_top_products_chart(product_data, title="TOP10热销产品"):
    """创建热销产品柱状图"""
    if product_data.empty:
        return None

    # 只取前10名产品
    top_products = product_data.sort_values('销售额', ascending=False).head(10).copy()

    fig = px.bar(
        top_products,
        x='产品简称',
        y='销售额',
        title=title,
        color='BCG分类',
        color_discrete_map={
            '明星产品': BCG_COLORS['star'],
            '现金牛产品': BCG_COLORS['cash_cow'],
            '问号产品': BCG_COLORS['question'],
            '瘦狗产品': BCG_COLORS['dog']
        },
        text='销售额'
    )

    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="产品",
        yaxis_title="销售额（元）",
        xaxis={'categoryorder': 'total descending'}
    )

    return fig


def create_growth_products_chart(product_data, title="TOP10增长最快产品"):
    """创建增长最快产品柱状图"""
    if product_data.empty:
        return None

    # 筛选有效产品（去年销售额不为0的产品）
    valid_products = product_data[product_data['去年销售额'] > 0].copy()

    if valid_products.empty:
        return None

    # 只取前10名增长最快的产品
    top_growth = valid_products.sort_values('增长率', ascending=False).head(10).copy()

    fig = px.bar(
        top_growth,
        x='产品简称',
        y='增长率',
        title=title,
        color='BCG分类',
        color_discrete_map={
            '明星产品': BCG_COLORS['star'],
            '现金牛产品': BCG_COLORS['cash_cow'],
            '问号产品': BCG_COLORS['question'],
            '瘦狗产品': BCG_COLORS['dog']
        },
        text='增长率'
    )

    fig.update_traces(
        texttemplate='%{y:.1f}%',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="产品",
        yaxis_title="增长率（%）",
        xaxis={'categoryorder': 'total descending'}
    )

    return fig


def create_bcg_health_gauge(bcg_health, title="产品组合健康度"):
    """创建产品组合健康度仪表盘"""
    # 确定颜色
    if bcg_health >= 80:
        color = COLORS['success']
        status = "健康"
    elif bcg_health >= 60:
        color = COLORS['warning']
        status = "一般"
    else:
        color = COLORS['danger']
        status = "不健康"

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bcg_health,
        title={'text': f"{title}<br><span style='font-size:0.8em;color:{color}'>{status}</span>", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 67, 54, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(255, 144, 14, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(50, 205, 50, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )

    return fig


def create_customer_coverage_chart(product_data, title="产品客户覆盖率"):
    """创建产品客户覆盖率图"""
    if product_data.empty or '客户覆盖率' not in product_data.columns:
        return None

    # 获取TOP10热销产品
    top_products = product_data.sort_values('销售额', ascending=False).head(10).copy()

    fig = px.bar(
        top_products,
        x='产品简称',
        y='客户覆盖率',
        title=title,
        color='BCG分类',
        color_discrete_map={
            '明星产品': BCG_COLORS['star'],
            '现金牛产品': BCG_COLORS['cash_cow'],
            '问号产品': BCG_COLORS['question'],
            '瘦狗产品': BCG_COLORS['dog']
        },
        text='客户覆盖率'
    )

    fig.update_traces(
        texttemplate='%{y:.1f}%',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="产品",
        yaxis_title="客户覆盖率（%）",
        xaxis={'categoryorder': 'total descending'}
    )

    return fig


# ==================== 主页面 ====================
# 分析数据
product_analysis = analyze_product_data(filtered_data)

# 创建标签页
tabs = st.tabs(["📊 产品概览", "🔄 BCG矩阵", "🚀 产品增长", "👥 客户覆盖"])

with tabs[0]:  # 产品概览
    # KPI指标行
    st.subheader("🔑 关键产品指标")
    col1, col2, col3, col4 = st.columns(4)

    # 产品总数
    total_products = product_analysis.get('total_products', 0)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">产品总数</p>
            <p class="card-value">{format_number(total_products)}</p>
            <p class="card-text">在售产品数量</p>
        </div>
        """, unsafe_allow_html=True)

    # 现金牛产品占比
    cash_cow_percent = product_analysis.get('cash_cow_percent', 0)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">现金牛产品占比</p>
            <p class="card-value" style="color: {'#4CAF50' if 45 <= cash_cow_percent <= 50 else '#FF9800'};">{format_percentage(cash_cow_percent)}</p>
            <p class="card-text">理想比例: 45-50%</p>
        </div>
        """, unsafe_allow_html=True)

    # 明星和问号产品占比
    star_question_percent = product_analysis.get('star_question_percent', 0)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">明星&问号产品占比</p>
            <p class="card-value" style="color: {'#4CAF50' if 40 <= star_question_percent <= 45 else '#FF9800'};">{format_percentage(star_question_percent)}</p>
            <p class="card-text">理想比例: 40-45%</p>
        </div>
        """, unsafe_allow_html=True)

    # 瘦狗产品占比
    dog_percent = product_analysis.get('dog_percent', 0)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">瘦狗产品占比</p>
            <p class="card-value" style="color: {'#4CAF50' if dog_percent <= 10 else '#F44336'};">{format_percentage(dog_percent)}</p>
            <p class="card-text">理想比例: ≤10%</p>
        </div>
        """, unsafe_allow_html=True)

    # 产品组合健康度
    st.markdown('<div class="sub-header">📊 产品组合健康度</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        # BCG健康度仪表盘
        bcg_health = product_analysis.get('bcg_health', 0)
        fig = create_bcg_health_gauge(bcg_health, "产品组合健康度")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        is_healthy_mix = product_analysis.get('is_healthy_mix', False)

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 产品组合健康度为{format_percentage(bcg_health)}，{'符合' if is_healthy_mix else '不符合'}理想的BCG产品组合模型。
            {'当前产品组合结构健康，各类产品占比平衡。' if is_healthy_mix else '当前产品组合结构需要优化，存在一定的不平衡。'}
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        # BCG分类饼图
        bcg_summary = product_analysis.get('bcg_summary', pd.DataFrame())
        if not bcg_summary.empty:
            fig = create_bcg_pie_chart(bcg_summary, "产品类型占比")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> 此图展示了各类产品的销售占比。理想的产品组合为：现金牛产品45-50%，明星和问号产品40-45%，瘦狗产品≤10%。
                当前现金牛产品{format_percentage(cash_cow_percent)}，明星&问号产品{format_percentage(star_question_percent)}，瘦狗产品{format_percentage(dog_percent)}。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无产品BCG分类数据")

    # 热销产品分析
    st.markdown('<div class="sub-header">📊 热销产品分析</div>', unsafe_allow_html=True)

    product_sales = product_analysis.get('product_sales', pd.DataFrame())
    if not product_sales.empty:
        # TOP10热销产品柱状图
        fig = create_top_products_chart(product_sales, "TOP10热销产品")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_product = product_sales.sort_values('销售额', ascending=False).iloc[0] if not product_sales.empty else None
        top_product_name = top_product['产品简称'] if top_product is not None and '产品简称' in top_product else "未知"
        top_product_sales = top_product['销售额'] if top_product is not None else 0
        top_product_percentage = top_product['销售占比'] if top_product is not None else 0

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> {top_product_name}是销售额最高的产品，销售额{format_currency(top_product_sales)}，占总销售额的{format_percentage(top_product_percentage)}。
            TOP10产品中，{'现金牛产品占主导' if sum(1 for p in product_sales.sort_values('销售额', ascending=False).head(10)['BCG分类'] if p == '现金牛产品') > 5 else '明星产品表现强劲' if sum(1 for p in product_sales.sort_values('销售额', ascending=False).head(10)['BCG分类'] if p == '明星产品') > 3 else '产品类型分布相对均衡'}。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("暂无产品销售数据")

    # 产品组合建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

    if product_analysis.get('is_healthy_mix', False):
        st.markdown(f"""
        <h4>✅ 产品组合健康</h4>
        <p>当前产品组合结构健康，符合BCG产品组合模型要求（现金牛45-50%，明星&问号40-45%，瘦狗≤10%）。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>维持现有产品组合结构，持续关注各类产品表现</li>
            <li>关注明星产品向现金牛产品的顺利转化</li>
            <li>加大对有潜力的问号产品的投入，培育新的明星产品</li>
            <li>定期评估并淘汰表现不佳的瘦狗产品，优化资源配置</li>
        </ul>
        """, unsafe_allow_html=True)
    elif product_analysis.get('cash_cow_percent', 0) < 45:
        st.markdown(f"""
        <h4>⚠️ 现金牛产品比例不足</h4>
        <p>当前现金牛产品占比{format_percentage(product_analysis.get('cash_cow_percent', 0))}，低于理想的45-50%，可能影响稳定现金流。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>加强现金牛产品营销，提高市场份额</li>
            <li>加速优质明星产品向现金牛产品转化</li>
            <li>扩大现金牛产品的渠道覆盖</li>
            <li>控制现金牛产品成本，提高利润率</li>
        </ul>
        """, unsafe_allow_html=True)
    elif product_analysis.get('cash_cow_percent', 0) > 50:
        st.markdown(f"""
        <h4>⚠️ 现金牛产品比例过高</h4>
        <p>当前现金牛产品占比{format_percentage(product_analysis.get('cash_cow_percent', 0))}，高于理想的45-50%，可能缺乏长期增长动力。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>增加明星和问号产品的投入，培育未来增长点</li>
            <li>开发创新产品，丰富产品线</li>
            <li>评估现金牛产品生命周期，适时淘汰老化产品</li>
            <li>建立产品创新机制，保持产品活力</li>
        </ul>
        """, unsafe_allow_html=True)
    elif product_analysis.get('star_question_percent', 0) < 40:
        st.markdown(f"""
        <h4>⚠️ 明星和问号产品比例不足</h4>
        <p>当前明星和问号产品占比{format_percentage(product_analysis.get('star_question_percent', 0))}，低于理想的40-45%，未来增长动力不足。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>加大研发投入，开发创新产品</li>
            <li>增加明星产品的营销支持，扩大市场份额</li>
            <li>评估问号产品潜力，对高潜力产品加大投入</li>
            <li>建立产品创新孵化机制，持续培育新品</li>
        </ul>
        """, unsafe_allow_html=True)
    elif product_analysis.get('dog_percent', 0) > 10:
        st.markdown(f"""
        <h4>⚠️ 瘦狗产品比例过高</h4>
        <p>当前瘦狗产品占比{format_percentage(product_analysis.get('dog_percent', 0))}，高于理想的10%以下，资源配置效率不高。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>制定瘦狗产品淘汰计划，释放资源</li>
            <li>评估瘦狗产品潜力，有潜力的尝试重新定位</li>
            <li>无潜力的产品逐步减少投入，最终退出</li>
            <li>建立产品生命周期管理机制，及时处理低效产品</li>
        </ul>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:  # BCG矩阵
    st.subheader("🔄 BCG产品矩阵分析")

    # 产品BCG矩阵
    product_sales = product_analysis.get('product_sales', pd.DataFrame())
    if not product_sales.empty:
        # BCG矩阵气泡图
        fig = create_bcg_bubble_chart(product_sales, "产品BCG矩阵分析")
        st.plotly_chart(fig, use_container_width=True)

        # BCG矩阵解释
        st.markdown("""
        <div class="chart-explanation">
            <b>BCG矩阵解读：</b>
            <ul>
                <li><b>明星产品</b>（销售占比≥1.5% & 增长率≥20%）：高增长、高市场份额的产品，需要持续投入以保持增长</li>
                <li><b>现金牛产品</b>（销售占比≥1.5% & 增长率<20%）：低增长、高市场份额的产品，产生稳定现金流</li>
                <li><b>问号产品</b>（销售占比<1.5% & 增长率≥20%）：高增长、低市场份额的产品，需要评估是否增加投入</li>
                <li><b>瘦狗产品</b>（销售占比<1.5% & 增长率<20%）：低增长、低市场份额的产品，考虑是否退出</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 产品类型详细分析
        st.markdown('<div class="sub-header">📊 产品类型详细分析</div>', unsafe_allow_html=True)

        # 创建产品类型分析展示框
        col1, col2 = st.columns(2)

        with col1:
            # 现金牛产品分析
            cash_cow_products = product_sales[product_sales['BCG分类'] == '现金牛产品'].sort_values('销售额', ascending=False)

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {BCG_COLORS['cash_cow']}; 
                        padding: 1.5rem; border-radius: 0.5rem;">
                <h4>🐄 现金牛产品分析</h4>
                <p><b>产品数量：</b> {len(cash_cow_products)} 个</p>
                <p><b>销售占比：</b> {format_percentage(product_analysis.get('cash_cow_percent', 0))}</p>
                <p><b>TOP3现金牛产品：</b></p>
                <ul>
            """, unsafe_allow_html=True)

            for i, row in cash_cow_products.head(3).iterrows():
                st.markdown(f"""
                    <li>{row['产品简称']} - 销售额：{format_currency(row['销售额'])}，销售占比：{format_percentage(row['销售占比'])}，增长率：{format_percentage(row['增长率'])}</li>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                </ul>
                <p><b>现金牛产品策略建议：</b></p>
                <ul>
                    <li>{'增加现金牛产品比例，扩大稳定收入来源' if product_analysis.get('cash_cow_percent', 0) < 45 else '保持现金牛产品稳定' if product_analysis.get('cash_cow_percent', 0) <= 50 else '适当控制现金牛产品比例，避免过度依赖'}</li>
                    <li>控制营销成本，保持较高利润率</li>
                    <li>定期创新包装或口味，延长产品生命周期</li>
                    <li>利用规模优势，优化供应链成本</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # 问号产品分析
            question_products = product_sales[product_sales['BCG分类'] == '问号产品'].sort_values('销售额', ascending=False)

            st.markdown(f"""
            <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid {BCG_COLORS['question']}; 
                        padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem;">
                <h4>❓ 问号产品分析</h4>
                <p><b>产品数量：</b> {len(question_products)} 个</p>
                <p><b>销售占比：</b> {format_percentage(question_products['销售占比'].sum() if not question_products.empty else 0)}</p>
                <p><b>TOP3问号产品：</b></p>
                <ul>
            """, unsafe_allow_html=True)

            for i, row in question_products.head(3).iterrows():
                st.markdown(f"""
                    <li>{row['产品简称']} - 销售额：{format_currency(row['销售额'])}，销售占比：{format_percentage(row['销售占比'])}，增长率：{format_percentage(row['增长率'])}</li>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                </ul>
                <p><b>问号产品策略建议：</b></p>
                <ul>
                    <li>评估产品潜力，识别有望成为明星产品的问号产品</li>
                    <li>对高潜力问号产品加大营销投入</li>
                    <li>扩大渠道覆盖，提高市场份额</li>
                    <li>对低潜力问号产品考虑退出策略</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 明星产品分析
            star_products = product_sales[product_sales['BCG分类'] == '明星产品'].sort_values('销售额', ascending=False)

            st.markdown(f"""
            <div style="background-color: rgba(255, 215, 0, 0.1); border-left: 4px solid {BCG_COLORS['star']}; 
                        padding: 1.5rem; border-radius: 0.5rem;">
                <h4>⭐ 明星产品分析</h4>
                <p><b>产品数量：</b> {len(star_products)} 个</p>
                <p><b>销售占比：</b> {format_percentage(star_products['销售占比'].sum() if not star_products.empty else 0)}</p>
                <p><b>TOP3明星产品：</b></p>
                <ul>
            """, unsafe_allow_html=True)

            for i, row in star_products.head(3).iterrows():
                st.markdown(f"""
                    <li>{row['产品简称']} - 销售额：{format_currency(row['销售额'])}，销售占比：{format_percentage(row['销售占比'])}，增长率：{format_percentage(row['增长率'])}</li>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                </ul>
                <p><b>明星产品策略建议：</b></p>
                <ul>
                    <li>持续高投入，保持增长势头</li>
                    <li>扩大渠道覆盖，提高市场份额</li>
                    <li>建立品牌忠诚度，为转化为现金牛产品做准备</li>
                    <li>关注产品生命周期，及时管理转型</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # 瘦狗产品分析
            dog_products = product_sales[product_sales['BCG分类'] == '瘦狗产品'].sort_values('销售额', ascending=False)

            st.markdown(f"""
            <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid {BCG_COLORS['dog']}; 
                        padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem;">
                <h4>🐕 瘦狗产品分析</h4>
                <p><b>产品数量：</b> {len(dog_products)} 个</p>
                <p><b>销售占比：</b> {format_percentage(product_analysis.get('dog_percent', 0))}</p>
                <p><b>TOP3瘦狗产品：</b></p>
                <ul>
            """, unsafe_allow_html=True)

            for i, row in dog_products.head(3).iterrows():
                st.markdown(f"""
                    <li>{row['产品简称']} - 销售额：{format_currency(row['销售额'])}，销售占比：{format_percentage(row['销售占比'])}，增长率：{format_percentage(row['增长率'])}</li>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                </ul>
                <p><b>瘦狗产品策略建议：</b></p>
                <ul>
                    <li>{'减少瘦狗产品比例，释放资源' if product_analysis.get('dog_percent', 0) > 10 else '维持瘦狗产品适度比例，避免资源浪费'}</li>
                    <li>评估重新定位可能性，对有潜力产品尝试转型</li>
                    <li>制定产品退出计划，逐步淘汰低效产品</li>
                    <li>从瘦狗产品尝试中总结经验，指导未来产品开发</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 产品矩阵总结
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
        st.markdown(f"""
        <h4>🔄 BCG产品矩阵总结</h4>
        <p>BCG产品矩阵分析是评估产品组合健康度的重要工具。当前产品组合中：</p>
        <ul>
            <li>现金牛产品占比{format_percentage(product_analysis.get('cash_cow_percent', 0))}，{'符合' if 45 <= product_analysis.get('cash_cow_percent', 0) <= 50 else '不符合'}理想的45-50%比例</li>
            <li>明星和问号产品占比{format_percentage(product_analysis.get('star_question_percent', 0))}，{'符合' if 40 <= product_analysis.get('star_question_percent', 0) <= 45 else '不符合'}理想的40-45%比例</li>
            <li>瘦狗产品占比{format_percentage(product_analysis.get('dog_percent', 0))}，{'符合' if product_analysis.get('dog_percent', 0) <= 10 else '不符合'}理想的≤10%比例</li>
        </ul>
        <p><strong>矩阵管理策略：</strong></p>
        <ul>
            <li>实施产品生命周期管理，关注产品在矩阵中的动态变化</li>
            <li>资源向高价值象限倾斜，优化投资回报</li>
            <li>建立明确的产品升级和退出机制，保持产品结构活力</li>
            <li>定期评估产品组合健康度，及时调整产品策略</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 产品矩阵表格
        with st.expander("查看产品BCG分类详细数据"):
            # 创建标签页
            product_tabs = st.tabs(["现金牛产品", "明星产品", "问号产品", "瘦狗产品"])

            with product_tabs[0]:
                if not cash_cow_products.empty:
                    # 显示列
                    display_cols = ['产品代码', '产品简称', '销售额', '销售占比', '增长率', '客户覆盖率'] if '客户覆盖率' in cash_cow_products.columns else ['产品代码', '产品简称', '销售额', '销售占比', '增长率']
                    st.dataframe(cash_cow_products[display_cols], use_container_width=True)
                else:
                    st.info("暂无现金牛产品")

            with product_tabs[1]:
                if not star_products.empty:
                    # 显示列
                    display_cols = ['产品代码', '产品简称', '销售额', '销售占比', '增长率', '客户覆盖率'] if '客户覆盖率' in star_products.columns else ['产品代码', '产品简称', '销售额', '销售占比', '增长率']
                    st.dataframe(star_products[display_cols], use_container_width=True)
                else:
                    st.info("暂无明星产品")

            with product_tabs[2]:
                if not question_products.empty:
                    # 显示列
                    display_cols = ['产品代码', '产品简称', '销售额', '销售占比', '增长率', '客户覆盖率'] if '客户覆盖率' in question_products.columns else ['产品代码', '产品简称', '销售额', '销售占比', '增长率']
                    st.dataframe(question_products[display_cols], use_container_width=True)
                else:
                    st.info("暂无问号产品")

            with product_tabs[3]:
                if not dog_products.empty:
                    # 显示列
                    display_cols = ['产品代码', '产品简称', '销售额', '销售占比', '增长率', '客户覆盖率'] if '客户覆盖率' in dog_products.columns else ['产品代码', '产品简称', '销售额', '销售占比', '增长率']
                    st.dataframe(dog_products[display_cols], use_container_width=True)
                else:
                    st.info("暂无瘦狗产品")
    else:
        st.info("暂无产品BCG分析数据")

with tabs[2]:  # 产品增长
    st.subheader("🚀 产品增长分析")

    # 产品增长分析
    product_sales = product_analysis.get('product_sales', pd.DataFrame())
    if not product_sales.empty:
        # 增长率分布
        valid_products = product_sales[product_sales['去年销售额'] > 0].copy()

        if not valid_products.empty:
            # 创建增长率分布直方图
            growth_ranges = [-100, -50, -20, 0, 20, 50, 100, float('inf')]
            growth_labels = ['<-50%', '-50% ~ -20%', '-20% ~ 0%', '0% ~ 20%', '20% ~ 50%', '50% ~ 100%', '>100%']

            valid_products['增长区间'] = pd.cut(valid_products['增长率'], bins=growth_ranges, labels=growth_labels)
            growth_distribution = valid_products.groupby('增长区间').size().reset_index(name='产品数量')

            fig = px.bar(
                growth_distribution,
                x='增长区间',
                y='产品数量',
                title="产品增长率分布",
                color='增长区间',
                text='产品数量',
                color_discrete_sequence=px.colors.sequential.Blues
            )

            fig.update_traces(
                textposition='outside'
            )

            fig.update_layout(
                height=400,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="增长率区间",
                yaxis_title="产品数量",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            growth_counts = growth_distribution.set_index('增长区间')['产品数量'].to_dict()
            positive_growth_count = sum(growth_counts.get(label, 0) for label in ['0% ~ 20%', '20% ~ 50%', '50% ~ 100%', '>100%'])
            negative_growth_count = sum(growth_counts.get(label, 0) for label in ['<-50%', '-50% ~ -20%', '-20% ~ 0%'])
            high_growth_count = sum(growth_counts.get(label, 0) for label in ['20% ~ 50%', '50% ~ 100%', '>100%'])

            total_valid = positive_growth_count + negative_growth_count
            positive_percentage = (positive_growth_count / total_valid * 100) if total_valid > 0 else 0
            high_growth_percentage = (high_growth_count / total_valid * 100) if total_valid > 0 else 0

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> {positive_growth_count}个产品实现正增长，占比{format_percentage(positive_percentage)}；{high_growth_count}个产品增长率超过20%，占比{format_percentage(high_growth_percentage)}。
                {'产品整体增长势头良好，多数产品保持正增长。' if positive_percentage > 70 else '产品增长分化明显，部分产品表现优异，部分产品需要关注。' if positive_percentage > 50 else '产品整体增长乏力，负增长产品占比较高，需要重点关注。'}
            </div>
            """, unsafe_allow_html=True)

            # 增长最快产品分析
            st.markdown('<div class="sub-header">📊 增长最快产品分析</div>', unsafe_allow_html=True)

            # TOP10增长最快产品柱状图
            fig = create_growth_products_chart(valid_products, "TOP10增长最快产品")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            top_growth_product = valid_products.sort_values('增长率', ascending=False).iloc[0] if not valid_products.empty else None
            top_growth_name = top_growth_product['产品简称'] if top_growth_product is not None and '产品简称' in top_growth_product else "未知"
            top_growth_rate = top_growth_product['增长率'] if top_growth_product is not None else 0
            top_growth_sales = top_growth_product['销售额'] if top_growth_product is not None else 0

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> {top_growth_name}是增长最快的产品，增长率{format_percentage(top_growth_rate)}，销售额{format_currency(top_growth_sales)}。
                TOP10增长产品中，{'主要是明星产品' if sum(1 for p in valid_products.sort_values('增长率', ascending=False).head(10)['BCG分类'] if p == '明星产品') > 5 else '主要是问号产品' if sum(1 for p in valid_products.sort_values('增长率', ascending=False).head(10)['BCG分类'] if p == '问号产品') > 5 else '产品类型分布多样'}。这些产品是未来增长的重要驱动力。
            </div>
            """, unsafe_allow_html=True)

            # 增长产品策略建议
            st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

            # 确定增长建议类型
            if positive_percentage > 70:
                growth_advice = "增长势头良好"
            elif positive_percentage > 50:
                growth_advice = "增长分化明显"
            else:
                growth_advice = "整体增长乏力"

            if growth_advice == "增长势头良好":
                st.markdown("""
                <h4>🚀 产品增长表现良好</h4>
                <p>大多数产品都保持正增长，产品组合整体发展健康。</p>
                <p><strong>增长策略建议：</strong></p>
                <ul>
                    <li>保持对高增长产品的投入，继续扩大市场份额</li>
                    <li>分析高增长产品成功因素，复制到其他产品</li>
                    <li>关注市场趋势变化，提前布局新增长点</li>
                    <li>持续优化产品结构，淘汰负增长产品</li>
                </ul>
                """, unsafe_allow_html=True)
            elif growth_advice == "增长分化明显":
                st.markdown("""
                <h4>⚠️ 产品增长分化明显</h4>
                <p>部分产品表现优异，部分产品增长乏力，需要有针对性的策略。</p>
                <p><strong>增长策略建议：</strong></p>
                <ul>
                    <li>重点支持高增长产品，扩大成功产品比例</li>
                    <li>分析低增长和负增长产品原因，制定改进计划</li>
                    <li>优化产品结构，减少负增长产品比例</li>
                    <li>加强产品创新，持续培育新增长点</li>
                </ul>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <h4>🚨 产品整体增长乏力</h4>
                <p>负增长产品占比较高，需要重点关注产品策略调整。</p>
                <p><strong>增长策略建议：</strong></p>
                <ul>
                    <li>全面评估产品组合，找出增长瓶颈</li>
                    <li>加大产品创新力度，开发更符合市场需求的产品</li>
                    <li>优化营销策略，提升产品竞争力</li>
                    <li>大胆淘汰长期负增长产品，释放资源</li>
                </ul>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # 增长潜力产品
            st.markdown('<div class="sub-header">📊 增长潜力产品分析</div>', unsafe_allow_html=True)

            # 筛选问号产品中增长率最高的产品
            high_potential = product_sales[product_sales['BCG分类'] == '问号产品'].sort_values('增长率', ascending=False).head(5)

            if not high_potential.empty:
                # 创建高潜力产品表格
                st.markdown("""
                <p>以下问号产品增长率高，但市场份额仍低，具有较大增长潜力，值得重点关注。</p>
                """, unsafe_allow_html=True)

                for i, row in high_potential.iterrows():
                    product_name = row['产品简称']
                    growth_rate = row['增长率']
                    market_share = row['销售占比']
                    sales_amount = row['销售额']

                    st.markdown(f"""
                    <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; 
                                box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: {COLORS['primary']};">{product_name}</h4>
                                <p style="margin: 0.2rem 0;">产品代码: {row['产品代码']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="margin: 0; font-weight: bold; color: #4CAF50;">增长率: {format_percentage(growth_rate)}</p>
                                <p style="margin: 0;">销售占比: {format_percentage(market_share)}</p>
                                <p style="margin: 0;">销售额: {format_currency(sales_amount)}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # 潜力产品建议
                st.markdown("""
                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; 
                            padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;">
                    <h4>💡 潜力产品发展建议</h4>
                    <ul>
                        <li>增加营销投入，提高品牌认知度</li>
                        <li>扩大渠道覆盖，提升市场渗透率</li>
                        <li>加强客户教育，推动产品试用</li>
                        <li>建立专项跟踪机制，定期评估发展进度</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("暂无高增长潜力产品")
        else:
            st.info("暂无有效的产品增长率数据（需要去年销售额大于0）")
    else:
        st.info("暂无产品销售数据")

with tabs[3]:  # 客户覆盖
    st.subheader("👥 产品客户覆盖分析")

    # 产品客户覆盖分析
    product_sales = product_analysis.get('product_sales', pd.DataFrame())
    if not product_sales.empty and '客户覆盖率' in product_sales.columns:
        # 产品客户覆盖率图表
        fig = create_customer_coverage_chart(product_sales, "TOP10热销产品客户覆盖率")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_coverage_product = product_sales.sort_values('客户覆盖率', ascending=False).iloc[0] if not product_sales.empty else None
        top_coverage_name = top_coverage_product['产品简称'] if top_coverage_product is not None and '产品简称' in top_coverage_product else "未知"
        top_coverage_rate = top_coverage_product['客户覆盖率'] if top_coverage_product is not None else 0

        top_sales_coverage = product_sales.sort_values('销售额', ascending=False).head(10)['客户覆盖率'].mean()

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> {top_coverage_name}的客户覆盖率最高，达到{format_percentage(top_coverage_rate)}，是渗透率最高的产品。
            TOP10热销产品的平均客户覆盖率为{format_percentage(top_sales_coverage)}，{'说明热销产品普遍有较好的市场渗透度' if top_sales_coverage > 50 else '说明即使是热销产品，市场渗透度仍有提升空间'}。
        </div>
        """, unsafe_allow_html=True)

        # 客户覆盖分析
        st.markdown('<div class="sub-header">📊 客户覆盖率分布</div>', unsafe_allow_html=True)

        # 创建客户覆盖率分布统计
        coverage_ranges = [0, 10, 30, 50, 70, 90, 100]
        coverage_labels = ['<10%', '10% ~ 30%', '30% ~ 50%', '50% ~ 70%', '70% ~ 90%', '>90%']

        product_sales['覆盖率区间'] = pd.cut(product_sales['客户覆盖率'], bins=coverage_ranges, labels=coverage_labels)
        coverage_distribution = product_sales.groupby('覆盖率区间').size().reset_index(name='产品数量')

        fig = px.bar(
            coverage_distribution,
            x='覆盖率区间',
            y='产品数量',
            title="产品客户覆盖率分布",
            color='覆盖率区间',
            text='产品数量',
            color_discrete_sequence=px.colors.sequential.Reds
        )

        fig.update_traces(
            textposition='outside'
        )

        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="客户覆盖率区间",
            yaxis_title="产品数量",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        coverage_counts = coverage_distribution.set_index('覆盖率区间')['产品数量'].to_dict()
        low_coverage_count = sum(coverage_counts.get(label, 0) for label in ['<10%', '10% ~ 30%'])
        medium_coverage_count = sum(coverage_counts.get(label, 0) for label in ['30% ~ 50%', '50% ~ 70%'])
        high_coverage_count = sum(coverage_counts.get(label, 0) for label in ['70% ~ 90%', '>90%'])

        total_products = low_coverage_count + medium_coverage_count + high_coverage_count
        low_percentage = (low_coverage_count / total_products * 100) if total_products > 0 else 0
        medium_percentage = (medium_coverage_count / total_products * 100) if total_products > 0 else 0
        high_percentage = (high_coverage_count / total_products * 100) if total_products > 0 else 0

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> {low_coverage_count}个产品客户覆盖率低于30%，占比{format_percentage(low_percentage)}；{medium_coverage_count}个产品客户覆盖率在30%-70%之间，占比{format_percentage(medium_percentage)}；{high_coverage_count}个产品客户覆盖率高于70%，占比{format_percentage(high_percentage)}。
            {'多数产品客户覆盖率较低，市场渗透有较大提升空间。' if low_percentage > 50 else '产品客户覆盖率分布相对均衡，部分产品渗透良好，部分产品需要提升。' if medium_percentage > 40 else '多数产品客户覆盖率较高，市场渗透度良好。'}
        </div>
        """, unsafe_allow_html=True)

        # 客户覆盖与销售关系分析
        st.markdown('<div class="sub-header">📊 客户覆盖与销售关系分析</div>', unsafe_allow_html=True)

        # 创建客户覆盖率与销售额散点图
        fig = px.scatter(
            product_sales,
            x='客户覆盖率',
            y='销售额',
            size='销售额',
            color='BCG分类',
            hover_name='产品简称',
            title="客户覆盖率与销售额关系",
            color_discrete_map={
                '明星产品': BCG_COLORS['star'],
                '现金牛产品': BCG_COLORS['cash_cow'],
                '问号产品': BCG_COLORS['question'],
                '瘦狗产品': BCG_COLORS['dog']
            },
            size_max=50
        )

        fig.update_layout(
            height=500,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="客户覆盖率 (%)",
            yaxis_title="销售额 (元)"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        # 计算相关系数
        correlation = product_sales['客户覆盖率'].corr(product_sales['销售额'])

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 客户覆盖率与销售额的相关系数为{correlation:.2f}，{'显示两者有较强的正相关关系，提高客户覆盖率通常会带来销售额增长。' if correlation > 0.5 else '显示两者有一定的正相关关系，但也有其他因素影响销售额。' if correlation > 0 else '显示两者相关性较弱，销售额可能更多受到单客户采购量等其他因素影响。'}
            在图中可以看到，{'现金牛产品和明星产品通常具有较高的客户覆盖率，同时销售额也较高。' if product_sales[product_sales['BCG分类'].isin(['现金牛产品', '明星产品'])]['客户覆盖率'].mean() > 50 else '即使是现金牛产品和明星产品，客户覆盖率也有很大提升空间。'}
        </div>
        """, unsafe_allow_html=True)

        # 客户覆盖策略建议
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

        if low_percentage > 50:
            st.markdown("""
            <h4>⚠️ 提高产品客户覆盖率策略</h4>
            <p>多数产品客户覆盖率较低，市场渗透有较大提升空间。</p>
            <p><strong>覆盖率提升策略：</strong></p>
            <ul>
                <li>针对低覆盖率产品，实施客户扩展计划</li>
                <li>加强销售团队培训，提高产品推广能力</li>
                <li>开展产品试用活动，降低客户尝试门槛</li>
                <li>优化产品定位，提高产品与客户需求的匹配度</li>
                <li>建立产品渗透率指标，纳入销售考核体系</li>
            </ul>
            """, unsafe_allow_html=True)
        elif medium_percentage > 40:
            st.markdown("""
            <h4>🔄 优化产品客户覆盖策略</h4>
            <p>产品客户覆盖率分布相对均衡，部分产品渗透良好，部分产品需要提升。</p>
            <p><strong>覆盖率优化策略：</strong></p>
            <ul>
                <li>分析高覆盖率产品成功因素，在低覆盖率产品中复制</li>
                <li>重点提升核心产品的覆盖率，扩大市场份额</li>
                <li>针对不同渠道，设计差异化的产品覆盖策略</li>
                <li>优化产品组合推广，提高产品渗透协同效应</li>
                <li>定期评估覆盖率提升成效，持续优化策略</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <h4>✅ 巩固产品客户覆盖优势</h4>
            <p>多数产品客户覆盖率较高，市场渗透度良好。</p>
            <p><strong>覆盖率巩固策略：</strong></p>
            <ul>
                <li>保持高覆盖率产品的市场优势，提高单客户销售额</li>
                <li>针对低覆盖率产品，制定针对性提升计划</li>
                <li>关注客户满意度，防止客户流失降低覆盖率</li>
                <li>探索产品交叉销售机会，提高产品组合渗透率</li>
                <li>持续优化产品性能，巩固市场竞争力</li>
            </ul>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无产品客户覆盖率数据")

# 产品洞察总结
st.subheader("💡 产品洞察总结")

# 生成洞察内容
total_products = product_analysis.get('total_products', 0)
bcg_health = product_analysis.get('bcg_health', 0)
is_healthy_mix = product_analysis.get('is_healthy_mix', False)

# 综合评估
if bcg_health >= 80:
    product_structure = "产品组合健康"
    structure_color = COLORS['success']
    structure_advice = "继续保持良好的产品结构，关注产品生命周期管理"
elif bcg_health >= 60:
    product_structure = "产品组合一般"
    structure_color = COLORS['warning']
    structure_advice = "优化产品组合结构，调整各类产品占比，提高组合健康度"
else:
    product_structure = "产品组合不健康"
    structure_color = COLORS['danger']
    structure_advice = "全面重构产品组合，制定产品升级和退出计划，重建健康产品结构"

st.markdown(f"""
<div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
            padding: 1rem; border-radius: 0.5rem;">
    <h4>📋 产品分析总结</h4>
    <p><strong>产品基础：</strong>当前共有{format_number(total_products)}个在售产品，BCG健康度{format_percentage(bcg_health)}。</p>
    <p><strong>产品结构：</strong><span style="color: {structure_color};">{product_structure}</span>，现金牛产品占比{format_percentage(product_analysis.get('cash_cow_percent', 0))}，明星&问号产品占比{format_percentage(product_analysis.get('star_question_percent', 0))}，瘦狗产品占比{format_percentage(product_analysis.get('dog_percent', 0))}。</p>
    <p><strong>增长状况：</strong>{'产品整体增长势头良好，多数产品保持正增长' if product_analysis.get('product_sales', pd.DataFrame()).empty or len(product_analysis.get('product_sales', pd.DataFrame())[product_analysis.get('product_sales', pd.DataFrame())['增长率'] > 0]) / len(product_analysis.get('product_sales', pd.DataFrame())) > 0.7 else '产品增长分化明显，部分产品表现优异，部分产品增长乏力' if product_analysis.get('product_sales', pd.DataFrame()).empty or len(product_analysis.get('product_sales', pd.DataFrame())[product_analysis.get('product_sales', pd.DataFrame())['增长率'] > 0]) / len(product_analysis.get('product_sales', pd.DataFrame())) > 0.5 else '产品整体增长乏力，负增长产品占比较高'}。</p>
    <p><strong>客户覆盖：</strong>{'产品客户覆盖率整体较高，市场渗透度良好' if product_analysis.get('product_sales', pd.DataFrame()).empty or '客户覆盖率' not in product_analysis.get('product_sales', pd.DataFrame()).columns or product_analysis.get('product_sales', pd.DataFrame())['客户覆盖率'].mean() > 50 else '产品客户覆盖率一般，部分产品需要提升渗透率' if product_analysis.get('product_sales', pd.DataFrame()).empty or '客户覆盖率' not in product_analysis.get('product_sales', pd.DataFrame()).columns or product_analysis.get('product_sales', pd.DataFrame())['客户覆盖率'].mean() > 30 else '产品客户覆盖率整体较低，市场渗透有较大提升空间'}。</p>
    <p><strong>发展建议：</strong>{structure_advice}；加强产品创新，培育未来增长点；持续优化产品结构，提高产品竞争力；建立完善的产品生命周期管理机制。</p>
</div>
""", unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)