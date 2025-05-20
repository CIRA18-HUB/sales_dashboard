# pages/product_page.py - 完全自包含的产品分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 从config导入颜色配置
from config import COLORS, DATA_FILES, BCG_COLORS


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_product_data():
    """加载产品分析所需的所有数据"""
    try:
        # 加载销售数据
        sales_data = pd.read_excel(DATA_FILES['sales_data'])

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

        # 过滤销售订单（只保留正常产品和TT产品）
        sales_orders = sales_data[
            sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

        # 添加渠道字段
        sales_orders['渠道'] = sales_orders['订单类型'].apply(
            lambda x: 'TT' if x == '订单-TT产品' else 'MT'
        )

        # 加载产品代码列表
        try:
            with open(DATA_FILES['product_codes'], 'r', encoding='utf-8') as f:
                product_codes = [line.strip() for line in f.readlines() if line.strip()]
        except:
            product_codes = []

        # 加载促销活动数据
        try:
            promotion_data = pd.read_excel(DATA_FILES['promotion_data'])
            if '促销开始供货时间' in promotion_data.columns:
                promotion_data['促销开始供货时间'] = pd.to_datetime(promotion_data['促销开始供货时间'])
            if '促销结束供货时间' in promotion_data.columns:
                promotion_data['促销结束供货时间'] = pd.to_datetime(promotion_data['促销结束供货时间'])
        except:
            promotion_data = pd.DataFrame()

        return sales_orders, product_codes, promotion_data

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), [], pd.DataFrame()


def apply_product_filters(data):
    """应用筛选条件"""
    filtered_data = data.copy()

    # 应用全局筛选条件
    if st.session_state.get('filter_region') and st.session_state.get('filter_region') != '全部':
        if '所属区域' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['所属区域'] == st.session_state.get('filter_region')]

    if st.session_state.get('filter_person') and st.session_state.get('filter_person') != '全部':
        if '申请人' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['申请人'] == st.session_state.get('filter_person')]

    if st.session_state.get('filter_customer') and st.session_state.get('filter_customer') != '全部':
        if '客户代码' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['客户代码'] == st.session_state.get('filter_customer')]

    return filtered_data


# ==================== 2. 工具函数 ====================
def format_currency(value):
    """格式化货币显示"""
    if pd.isna(value) or value == 0:
        return "¥0"
    if value >= 100000000:
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"


def format_number(value):
    """格式化数字显示"""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


# ==================== 3. 产品分析函数 ====================
def analyze_product_data(sales_data, product_codes, promotion_data):
    """分析产品数据"""
    if sales_data.empty:
        return {}

    # 获取当前年份
    current_year = datetime.now().year
    previous_year = current_year - 1

    # 年初至今销售数据
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]

    # 只分析指定产品代码的产品
    if product_codes:
        filtered_products = ytd_sales[ytd_sales['产品代码'].isin(product_codes)]
    else:
        filtered_products = ytd_sales

    # 产品销售汇总
    product_sales = filtered_products.groupby(['产品代码', '产品简称'])['求和项:金额（元）'].sum().reset_index()
    product_sales['销售占比'] = product_sales['求和项:金额（元）'] / product_sales['求和项:金额（元）'].sum() * 100 if \
        product_sales['求和项:金额（元）'].sum() > 0 else 0

    # 产品销量汇总
    product_quantity = filtered_products.groupby(['产品代码', '产品简称'])['求和项:数量（箱）'].sum().reset_index()

    # 合并销售额和销量
    product_summary = pd.merge(product_sales, product_quantity, on=['产品代码', '产品简称'], how='left')

    # 上年同期数据
    last_year_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == previous_year]

    if not last_year_sales.empty and product_codes:
        last_year_filtered = last_year_sales[last_year_sales['产品代码'].isin(product_codes)]
        last_year_product_sales = last_year_filtered.groupby('产品代码')['求和项:金额（元）'].sum().reset_index()
        last_year_product_sales.rename(columns={'求和项:金额（元）': '去年销售额'}, inplace=True)

        # 合并今年和去年的销售数据
        product_summary = pd.merge(product_summary, last_year_product_sales, on='产品代码', how='left')
        product_summary['去年销售额'] = product_summary['去年销售额'].fillna(0)

        # 计算增长率
        product_summary['增长率'] = (product_summary['求和项:金额（元）'] - product_summary['去年销售额']) / \
                                    product_summary['去年销售额'] * 100
        product_summary['增长率'] = product_summary['增长率'].fillna(0)
        product_summary.loc[product_summary['去年销售额'] == 0, '增长率'] = 100  # 去年无销售，今年有销售的，增长率设为100%
    else:
        product_summary['去年销售额'] = 0
        product_summary['增长率'] = 0

    # 根据BCG矩阵分类产品
    product_summary['产品类型'] = product_summary.apply(
        lambda row: '明星产品' if row['销售占比'] >= 1.5 and row['增长率'] >= 20
        else '现金牛产品' if row['销售占比'] >= 1.5 and row['增长率'] < 20
        else '问号产品' if row['销售占比'] < 1.5 and row['增长率'] >= 20
        else '瘦狗产品',
        axis=1
    )

    # 计算各类产品数量和销售额
    bcg_count = product_summary.groupby('产品类型').size().reset_index(name='产品数量')
    bcg_sales = product_summary.groupby('产品类型')['求和项:金额（元）'].sum().reset_index()

    # 合并数量和销售额
    bcg_summary = pd.merge(bcg_count, bcg_sales, on='产品类型', how='left')
    bcg_summary['销售占比'] = bcg_summary['求和项:金额（元）'] / bcg_summary['求和项:金额（元）'].sum() * 100 if \
        bcg_summary['求和项:金额（元）'].sum() > 0 else 0

    # 计算目标产品结构是否健康
    cash_cow_percent = bcg_summary.loc[
        bcg_summary['产品类型'] == '现金牛产品', '销售占比'].sum() if not bcg_summary.empty else 0
    star_question_percent = bcg_summary.loc[
        bcg_summary['产品类型'].isin(['明星产品', '问号产品']), '销售占比'].sum() if not bcg_summary.empty else 0
    dog_percent = bcg_summary.loc[
        bcg_summary['产品类型'] == '瘦狗产品', '销售占比'].sum() if not bcg_summary.empty else 0

    is_healthy_mix = (
            (45 <= cash_cow_percent <= 50) and
            (40 <= star_question_percent <= 45) and
            (dog_percent <= 10)
    )

    # 月度产品趋势
    monthly_product_sales = filtered_products.groupby([
        '产品代码',
        '产品简称',
        pd.Grouper(key='发运月份', freq='M')
    ])['求和项:金额（元）'].sum().reset_index()

    monthly_product_sales['月份'] = monthly_product_sales['发运月份'].dt.month

    # 促销活动分析
    promotion_summary = None
    if not promotion_data.empty and not product_summary.empty:
        # 获取当年促销活动
        current_year_promotions = promotion_data[
            (promotion_data['促销开始供货时间'].dt.year == current_year) |
            (promotion_data['促销结束供货时间'].dt.year == current_year)
            ] if '促销开始供货时间' in promotion_data.columns and '促销结束供货时间' in promotion_data.columns else pd.DataFrame()

        if not current_year_promotions.empty:
            # 按产品统计促销活动次数
            promotion_count = current_year_promotions.groupby(['产品代码', '促销产品名称']).size().reset_index(
                name='促销活动次数')

            # 计算预计销售额
            promotion_sales = current_year_promotions.groupby(['产品代码', '促销产品名称'])[
                '预计销售额（元）'].sum().reset_index()

            # 合并促销次数和销售额
            promotion_summary = pd.merge(promotion_count, promotion_sales, on=['产品代码', '促销产品名称'], how='left')

            # 计算促销效果
            promotion_summary['促销效果'] = promotion_summary['预计销售额（元）'] / promotion_summary['促销活动次数'] if \
                promotion_summary['促销活动次数'].sum() > 0 else 0

            # 添加实际销售额
            promotion_summary = pd.merge(
                promotion_summary,
                product_summary[['产品代码', '求和项:金额（元）']],
                on='产品代码',
                how='left'
            )
            promotion_summary['实际销售额'] = promotion_summary['求和项:金额（元）']
            promotion_summary.drop('求和项:金额（元）', axis=1, inplace=True)

    # 获取产品价格信息
    price_data = filtered_products[['产品代码', '产品简称', '单价（箱）']].drop_duplicates()

    return {
        'product_summary': product_summary,
        'bcg_summary': bcg_summary,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent,
        'is_healthy_mix': is_healthy_mix,
        'monthly_product_sales': monthly_product_sales,
        'promotion_summary': promotion_summary,
        'price_data': price_data
    }


# ==================== 4. 图表创建函数 ====================
def create_bcg_matrix(data, title):
    """创建BCG矩阵散点图"""
    if data.empty:
        return None

    # 创建气泡图
    fig = px.scatter(
        data,
        x='增长率',
        y='销售占比',
        size='求和项:金额（元）',
        color='产品类型',
        hover_name='产品简称',
        text='产品简称',
        size_max=50,
        title=title,
        color_discrete_map=BCG_COLORS,
        height=500
    )

    # 添加分隔线
    fig.add_shape(
        type="line",
        x0=20, y0=0,
        x1=20, y1=max(data['销售占比']) * 1.1,
        line=dict(color=COLORS['gray'], width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=min(data['增长率']) * 1.1, y0=1.5,
        x1=max(data['增长率']) * 1.1, y1=1.5,
        line=dict(color=COLORS['gray'], width=1, dash="dash")
    )

    # 添加象限标签
    annotations = [
        dict(
            x=50, y=4,
            text="明星产品",
            showarrow=False,
            font=dict(size=14, color=BCG_COLORS['star'])
        ),
        dict(
            x=10, y=4,
            text="现金牛产品",
            showarrow=False,
            font=dict(size=14, color=BCG_COLORS['cash_cow'])
        ),
        dict(
            x=50, y=0.5,
            text="问号产品",
            showarrow=False,
            font=dict(size=14, color=BCG_COLORS['question'])
        ),
        dict(
            x=10, y=0.5,
            text="瘦狗产品",
            showarrow=False,
            font=dict(size=14, color=BCG_COLORS['dog'])
        )
    ]

    fig.update_layout(
        annotations=annotations,
        height=600,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        xaxis_title="增长率 (%)",
        yaxis_title="销售占比 (%)",
        legend_title="产品类型"
    )

    # 更新点的外观
    fig.update_traces(
        marker=dict(opacity=0.7, line=dict(width=1, color=COLORS['white'])),
        textposition='middle right',
        hovertemplate='<b>%{hovertext}</b><br>销售占比: %{y:.2f}%<br>增长率: %{x:.2f}%<br>销售额: %{marker.size:,.2f}元<extra></extra>'
    )

    return fig


def create_product_treemap(data, title="产品销售分布"):
    """创建产品销售树图"""
    if data.empty:
        return None

    # 构建树图数据
    fig = px.treemap(
        data,
        path=['产品类型', '产品简称'],
        values='求和项:金额（元）',
        color='产品类型',
        color_discrete_map=BCG_COLORS,
        title=title,
        height=600
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor=COLORS['white']
    )

    # 更新悬停信息
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.2f}<br>占比: %{percentParent:.1%}<extra></extra>'
    )

    return fig


def create_bcg_pie_chart(data, title="产品类型分布"):
    """创建BCG分类占比饼图"""
    if data.empty:
        return None

    fig = px.pie(
        data,
        names='产品类型',
        values='求和项:金额（元）',
        title=title,
        color='产品类型',
        color_discrete_map=BCG_COLORS,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.2f}<br>占比: %{percent:.1%}<extra></extra>'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor=COLORS['white'],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_product_trend_chart(data, product_count=10, title="产品销售趋势"):
    """创建产品销售趋势图"""
    if data.empty:
        return None

    # 获取销售额最高的N个产品
    top_products = data.groupby(['产品代码', '产品简称'])['求和项:金额（元）'].sum().nlargest(product_count).reset_index()

    # 过滤数据，只保留这些产品
    filtered_data = data[data['产品简称'].isin(top_products['产品简称'])]

    # 创建折线图
    fig = px.line(
        filtered_data,
        x='月份',
        y='求和项:金额（元）',
        color='产品简称',
        title=title,
        markers=True,
        height=500,
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['info'],
                                 COLORS['warning'], COLORS['success'], COLORS['danger']] * 10
    )

    fig.update_layout(
        xaxis_title="月份",
        yaxis_title="销售额（元）",
        legend_title="产品",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white']
    )

    # 更新线条样式
    fig.update_traces(
        line=dict(width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{fullData.name}</b><br>月份: %{x}<br>销售额: ¥%{y:,.2f}<extra></extra>'
    )

    return fig


def create_promotion_chart(data, title="促销活动效果"):
    """创建促销活动效果图"""
    if data is None or data.empty:
        return None

    # 获取促销效果最好的产品
    top_promotions = data.sort_values('促销效果', ascending=False).head(10)

    # 创建横向柱状图
    fig = px.bar(
        top_promotions,
        y='促销产品名称',
        x='促销效果',
        orientation='h',
        title=title,
        color_discrete_sequence=[COLORS['primary']],
        text_auto='.2s'
    )

    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        xaxis_title='促销效果（元/次）',
        yaxis_title='产品'
    )

    # 添加促销活动次数标注
    for i, row in enumerate(top_promotions.itertuples()):
        fig.add_annotation(
            x=row.促销效果 + max(top_promotions['促销效果']) * 0.05,
            y=i,
            text=f"活动次数: {row.促销活动次数}",
            showarrow=False,
            font=dict(size=10, color=COLORS['gray'])
        )

    return fig


# ==================== 5. 翻卡组件 ====================
def create_product_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建产品分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"product_flip_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = 0

    # 格式化值
    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)

    # 创建卡片容器
    card_container = st.container()

    with card_container:
        # 点击按钮
        if st.button(f"查看{title}详情", key=f"btn_{card_id}", help=f"点击查看{title}的详细分析"):
            st.session_state[flip_key] = (st.session_state[flip_key] + 1) % 3

        current_layer = st.session_state[flip_key]

        if current_layer == 0:
            # 第一层：基础指标
            st.markdown(f"""
            <div style="background-color: {COLORS['white']}; padding: 1.5rem; border-radius: 0.5rem; 
                        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); 
                        text-align: center; min-height: 200px; display: flex; 
                        flex-direction: column; justify-content: center;">
                <h3 style="color: {COLORS['primary']}; margin-bottom: 1rem;">{title}</h3>
                <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">{formatted_value}</h1>
                <p style="color: {COLORS['gray']}; margin-bottom: 1rem;">{subtitle}</p>
                <p style="color: {COLORS['secondary']}; font-size: 0.9rem;">点击查看分析 →</p>
            </div>
            """, unsafe_allow_html=True)

        elif current_layer == 1:
            # 第二层：图表分析
            st.markdown(f"### 📊 {title} - 图表分析")

            # 根据不同的指标显示不同的图表
            if "产品总数" in title:
                # 显示产品分布图表
                if 'analysis_result' in st.session_state:
                    product_summary = st.session_state['analysis_result'].get('product_summary', pd.DataFrame())
                    if not product_summary.empty:
                        # 按产品类型统计产品数
                        product_types = product_summary.groupby('产品类型').size().reset_index(name='产品数量')

                        # 创建柱状图
                        fig = px.bar(
                            product_types,
                            x='产品类型',
                            y='产品数量',
                            color='产品类型',
                            title='产品类型分布',
                            color_discrete_map=BCG_COLORS
                        )

                        fig.update_layout(
                            plot_bgcolor=COLORS['white'],
                            paper_bgcolor=COLORS['white']
                        )

                        st.plotly_chart(fig, use_container_width=True)

            elif "现金牛产品占比" in title:
                # 显示BCG矩阵
                if 'analysis_result' in st.session_state:
                    bcg_summary = st.session_state['analysis_result'].get('bcg_summary', pd.DataFrame())
                    if not bcg_summary.empty:
                        fig = create_bcg_pie_chart(bcg_summary, '产品类型销售占比')
                        st.plotly_chart(fig, use_container_width=True)

            elif "明星和问号产品占比" in title:
                # 显示产品趋势
                if 'analysis_result' in st.session_state:
                    product_sales = st.session_state['analysis_result'].get('monthly_product_sales', pd.DataFrame())
                    if not product_sales.empty:
                        fig = create_product_trend_chart(product_sales, 5, 'TOP5产品月度销售趋势')
                        st.plotly_chart(fig, use_container_width=True)

            elif "瘦狗产品占比" in title:
                # 显示促销效果
                if 'analysis_result' in st.session_state:
                    promotion_data = st.session_state['analysis_result'].get('promotion_summary', None)
                    if promotion_data is not None and not promotion_data.empty:
                        fig = create_promotion_chart(promotion_data, '促销活动效果TOP10')
                        st.plotly_chart(fig, use_container_width=True)

            # 洞察文本
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>💡 数据洞察</h4>
                <p>{generate_insight_text(card_id)}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='text-align: center; color: {COLORS['secondary']};'>再次点击查看深度分析 →</p>",
                        unsafe_allow_html=True)

        else:
            # 第三层：深度分析
            st.markdown(f"### 🔍 {title} - 深度分析")

            # 深度分析内容
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid {COLORS['info']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>📈 趋势分析</h4>
                    {generate_trend_analysis(card_id)}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid {COLORS['warning']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>🎯 优化建议</h4>
                    {generate_optimization_advice(card_id)}
                </div>
                """, unsafe_allow_html=True)

            # 行动方案
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin-top: 1rem; border-radius: 0.5rem;">
                <h4>📋 行动方案</h4>
                {generate_action_plan(card_id)}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='text-align: center; color: {COLORS['secondary']};'>再次点击返回基础视图 ↻</p>",
                        unsafe_allow_html=True)


def generate_insight_text(card_id):
    """生成洞察文本"""
    if 'analysis_result' not in st.session_state:
        return "数据分析加载中..."

    analysis = st.session_state['analysis_result']

    if card_id == "product_count":
        product_count = len(analysis.get('product_summary', pd.DataFrame()))
        product_types = analysis.get('product_summary', pd.DataFrame()).groupby('产品类型').size()

        if not product_types.empty:
            cash_cow_count = product_types.get('现金牛产品', 0)
            star_count = product_types.get('明星产品', 0)
            question_count = product_types.get('问号产品', 0)
            dog_count = product_types.get('瘦狗产品', 0)

            cash_cow_pct = cash_cow_count / product_count * 100 if product_count > 0 else 0
            star_pct = star_count / product_count * 100 if product_count > 0 else 0
            question_pct = question_count / product_count * 100 if product_count > 0 else 0
            dog_pct = dog_count / product_count * 100 if product_count > 0 else 0

            return f"当前共有 {product_count} 个产品，其中现金牛产品 {cash_cow_count} 个({format_percentage(cash_cow_pct)})，明星产品 {star_count} 个({format_percentage(star_pct)})，问号产品 {question_count} 个({format_percentage(question_pct)})，瘦狗产品 {dog_count} 个({format_percentage(dog_pct)})。产品组合{'健康' if analysis.get('is_healthy_mix', False) else '需要优化'}。"
        else:
            return f"当前共有 {product_count} 个产品，无法获取产品类型分布信息。"

    elif card_id == "cash_cow":
        cash_cow_percent = analysis.get('cash_cow_percent', 0)

        if 45 <= cash_cow_percent <= 50:
            return f"当前现金牛产品销售占比 {format_percentage(cash_cow_percent)}，完全符合JBP计划产品模型(目标45%-50%)，可以保持现有产品策略，确保稳定现金流。"
        elif cash_cow_percent < 45:
            return f"当前现金牛产品销售占比 {format_percentage(cash_cow_percent)}，低于JBP计划产品模型的理想范围(45%-50%)，需要加强现金牛产品推广，增加销售占比。"
        else:
            return f"当前现金牛产品销售占比 {format_percentage(cash_cow_percent)}，高于JBP计划产品模型的理想范围(45%-50%)，过度依赖现金牛产品，需要培育更多明星和问号产品，确保未来增长。"

    elif card_id == "star_question":
        star_question_percent = analysis.get('star_question_percent', 0)

        if 40 <= star_question_percent <= 45:
            return f"当前明星和问号产品销售占比 {format_percentage(star_question_percent)}，完全符合JBP计划产品模型(目标40%-45%)，可以持续投入，确保未来增长潜力。"
        elif star_question_percent < 40:
            return f"当前明星和问号产品销售占比 {format_percentage(star_question_percent)}，低于JBP计划产品模型的理想范围(40%-45%)，需要加强创新和新品推广，培育更多增长型产品。"
        else:
            return f"当前明星和问号产品销售占比 {format_percentage(star_question_percent)}，高于JBP计划产品模型的理想范围(40%-45%)，投入较多资源于高增长产品，需注意平衡短期利润和长期增长。"

    elif card_id == "dog":
        dog_percent = analysis.get('dog_percent', 0)

        if dog_percent <= 10:
            return f"当前瘦狗产品销售占比 {format_percentage(dog_percent)}，符合JBP计划产品模型要求(≤10%)，产品组合相对健康，建议继续监控瘦狗产品表现，适时优化。"
        else:
            return f"当前瘦狗产品销售占比 {format_percentage(dog_percent)}，超过JBP计划产品模型要求(≤10%)，产品组合效率较低，建议评估并考虑淘汰部分表现不佳的产品，优化资源配置。"

    return "数据分析加载中..."


def generate_trend_analysis(card_id):
    """生成趋势分析HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>分析数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "product_count":
        product_summary = analysis.get('product_summary', pd.DataFrame())

        if not product_summary.empty:
            # 按销售额排序
            top_products = product_summary.nlargest(5, '求和项:金额（元）')
            top_products_html = ""
            for i, (_, row) in enumerate(top_products.iterrows()):
                top_products_html += f"<p>• {i + 1}. {row['产品简称']} - {format_currency(row['求和项:金额（元）'])} ({format_percentage(row['销售占比'])})</p>"

            # 按增长率排序
            fastest_growing = product_summary.nlargest(3, '增长率')
            growth_html = ""
            for i, (_, row) in enumerate(fastest_growing.iterrows()):
                growth_html += f"<p>• {row['产品简称']} - 增长率 {format_percentage(row['增长率'])}</p>"

            return f"""
                <p><strong>产品结构分析：</strong></p>
                <p>• 现金牛产品：{format_percentage(analysis.get('cash_cow_percent', 0))}</p>
                <p>• 明星和问号产品：{format_percentage(analysis.get('star_question_percent', 0))}</p>
                <p>• 瘦狗产品：{format_percentage(analysis.get('dog_percent', 0))}</p>
                <p><strong>TOP5销售产品：</strong></p>
                {top_products_html}
                <p><strong>增长最快的产品：</strong></p>
                {growth_html}
            """
        else:
            return "<p>无足够产品数据进行分析</p>"

    elif card_id == "cash_cow":
        bcg_summary = analysis.get('bcg_summary', pd.DataFrame())
        product_summary = analysis.get('product_summary', pd.DataFrame())

        if not bcg_summary.empty and not product_summary.empty:
            # 筛选现金牛产品
            cash_cow_products = product_summary[product_summary['产品类型'] == '现金牛产品']

            # 获取TOP3现金牛产品
            top_cash_cows = cash_cow_products.nlargest(3, '求和项:金额（元）')

            top_products_html = ""
            for i, (_, row) in enumerate(top_cash_cows.iterrows()):
                top_products_html += f"<p>• {i + 1}. {row['产品简称']} - {format_currency(row['求和项:金额（元）'])} ({format_percentage(row['销售占比'])})</p>"

            # 计算现金牛产品的平均增长率
            avg_growth = cash_cow_products['增长率'].mean() if len(cash_cow_products) > 0 else 0

            return f"""
                <p><strong>现金牛产品概览：</strong></p>
                <p>• 现金牛产品数量：{len(cash_cow_products)}个</p>
                <p>• 销售占比：{format_percentage(analysis.get('cash_cow_percent', 0))}</p>
                <p>• 平均增长率：{format_percentage(avg_growth)}</p>
                <p><strong>TOP3现金牛产品：</strong></p>
                {top_products_html}
                <p><strong>产品成熟度：</strong>{'较高，产品处于生命周期成熟期' if avg_growth < 10 else '中等，部分产品仍有一定增长空间'}</p>
            """
        else:
            return "<p>无足够产品数据进行分析</p>"

    elif card_id == "star_question":
        product_summary = analysis.get('product_summary', pd.DataFrame())

        if not product_summary.empty:
            # 筛选明星产品和问号产品
            star_products = product_summary[product_summary['产品类型'] == '明星产品']
            question_products = product_summary[product_summary['产品类型'] == '问号产品']

            # 获取TOP2明星产品
            top_stars = star_products.nlargest(2, '求和项:金额（元）')

            top_stars_html = ""
            for i, (_, row) in enumerate(top_stars.iterrows()):
                top_stars_html += f"<p>• {i + 1}. {row['产品简称']} - 增长率 {format_percentage(row['增长率'])}</p>"

            # 获取TOP2问号产品
            top_questions = question_products.nlargest(2, '增长率')

            top_questions_html = ""
            for i, (_, row) in enumerate(top_questions.iterrows()):
                top_questions_html += f"<p>• {i + 1}. {row['产品简称']} - 增长率 {format_percentage(row['增长率'])}</p>"

            # 计算平均增长率
            star_avg_growth = star_products['增长率'].mean() if len(star_products) > 0 else 0
            question_avg_growth = question_products['增长率'].mean() if len(question_products) > 0 else 0

            return f"""
                <p><strong>明星产品概览：</strong></p>
                <p>• 明星产品数量：{len(star_products)}个</p>
                <p>• 销售占比：{format_percentage(star_products['销售占比'].sum() if len(star_products) > 0 else 0)}</p>
                <p>• 平均增长率：{format_percentage(star_avg_growth)}</p>
                <p><strong>TOP明星产品：</strong></p>
                {top_stars_html}
                <p><strong>问号产品概览：</strong></p>
                <p>• 问号产品数量：{len(question_products)}个</p>
                <p>• 销售占比：{format_percentage(question_products['销售占比'].sum() if len(question_products) > 0 else 0)}</p>
                <p>• 平均增长率：{format_percentage(question_avg_growth)}</p>
                <p><strong>潜力问号产品：</strong></p>
                {top_questions_html}
            """
        else:
            return "<p>无足够产品数据进行分析</p>"

    elif card_id == "dog":
        product_summary = analysis.get('product_summary', pd.DataFrame())

        if not product_summary.empty:
            # 筛选瘦狗产品
            dog_products = product_summary[product_summary['产品类型'] == '瘦狗产品']

            # 计算瘦狗产品平均数据
            avg_growth = dog_products['增长率'].mean() if len(dog_products) > 0 else 0
            avg_share = dog_products['销售占比'].mean() if len(dog_products) > 0 else 0

            # 筛选表现最差的产品
            worst_dogs = dog_products.nsmallest(3, '增长率')

            worst_dogs_html = ""
            for i, (_, row) in enumerate(worst_dogs.iterrows()):
                worst_dogs_html += f"<p>• {row['产品简称']} - 增长率 {format_percentage(row['增长率'])}</p>"

            # 找出有潜力改造的瘦狗产品（增长率接近于0或略有增长）
            potential_dogs = dog_products[(dog_products['增长率'] > -5) & (dog_products['增长率'] < 10)]

            potential_dogs_html = ""
            if len(potential_dogs) > 0:
                for i, (_, row) in enumerate(potential_dogs.head(2).iterrows()):
                    potential_dogs_html += f"<p>• {row['产品简称']} - 增长率 {format_percentage(row['增长率'])}</p>"
            else:
                potential_dogs_html = "<p>• 无明显改造潜力的瘦狗产品</p>"

            return f"""
                <p><strong>瘦狗产品概览：</strong></p>
                <p>• 瘦狗产品数量：{len(dog_products)}个</p>
                <p>• 销售占比：{format_percentage(analysis.get('dog_percent', 0))}</p>
                <p>• 平均增长率：{format_percentage(avg_growth)}</p>
                <p>• 平均销售占比：{format_percentage(avg_share)}</p>
                <p><strong>表现最差的产品：</strong></p>
                {worst_dogs_html}
                <p><strong>有改造潜力的产品：</strong></p>
                {potential_dogs_html}
            """
        else:
            return "<p>无足够产品数据进行分析</p>"

    return "<p>分析数据加载中...</p>"


def generate_optimization_advice(card_id):
    """生成优化建议HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>建议数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "product_count":
        is_healthy = analysis.get('is_healthy_mix', False)
        cash_cow_percent = analysis.get('cash_cow_percent', 0)
        star_question_percent = analysis.get('star_question_percent', 0)
        dog_percent = analysis.get('dog_percent', 0)

        if is_healthy:
            return """
                <p>• 保持现有的产品组合结构，维持健康平衡</p>
                <p>• 持续监控各类型产品的销售趋势</p>
                <p>• 优化产品生命周期管理，确保稳定过渡</p>
                <p>• 继续开发新品，补充产品管线</p>
            """
        else:
            advice = []

            if cash_cow_percent < 45:
                advice.append("<p>• 加强现金牛产品推广力度，提高销售占比至45%-50%</p>")
            elif cash_cow_percent > 50:
                advice.append("<p>• 适当控制现金牛产品比重，降低至45%-50%的理想范围</p>")

            if star_question_percent < 40:
                advice.append("<p>• 增加明星和问号产品投入，提高销售占比至40%-45%</p>")
            elif star_question_percent > 45:
                advice.append("<p>• 控制明星和问号产品比重，确保资源合理分配</p>")

            if dog_percent > 10:
                advice.append("<p>• 评估并淘汰表现不佳的瘦狗产品，降低销售占比至10%以下</p>")

            # 补充建议，确保至少有4条
            if len(advice) < 4:
                advice.append("<p>• 优化产品生命周期管理，确保各类产品平衡发展</p>")
                advice.append("<p>• 加强产品创新，培育更多高增长潜力产品</p>")

            return "".join(advice)

    elif card_id == "cash_cow":
        cash_cow_percent = analysis.get('cash_cow_percent', 0)

        if cash_cow_percent < 45:
            return """
                <p>• 加强现金牛产品市场推广，提高销售占比</p>
                <p>• 优化现金牛产品定价策略，提升利润贡献</p>
                <p>• 增强现金牛产品渠道覆盖，拓展销售网络</p>
                <p>• 加强库存管理，确保现金牛产品供应稳定</p>
            """
        elif cash_cow_percent > 50:
            return """
                <p>• 减少对现金牛产品的过度依赖，调整产品结构</p>
                <p>• 将部分现金牛产品的资源转向明星产品培育</p>
                <p>• 评估现金牛产品生命周期，预判未来下滑风险</p>
                <p>• 加强新品开发，为未来增长储备动力</p>
            """
        else:
            return """
                <p>• 保持现金牛产品稳定增长，维持合理占比</p>
                <p>• 密切监控市场变化，及时调整促销策略</p>
                <p>• 优化产品成本结构，提高利润贡献</p>
                <p>• 强化品牌忠诚度，稳固市场地位</p>
            """

    elif card_id == "star_question":
        star_question_percent = analysis.get('star_question_percent', 0)
        product_summary = analysis.get('product_summary', pd.DataFrame())

        if star_question_percent < 40:
            return """
                <p>• 增加明星产品和问号产品的营销投入</p>
                <p>• 扩大渠道覆盖，提升市场占有率</p>
                <p>• 加强新品开发，培育更多高增长产品</p>
                <p>• 考虑产品升级或创新，注入新的增长动力</p>
            """
        elif star_question_percent > 45:
            return """
                <p>• 关注投资回报率，避免过度投入高增长产品</p>
                <p>• 评估部分高占比明星产品转为现金牛产品的可能</p>
                <p>• 优先扶持真正有长期潜力的明星和问号产品</p>
                <p>• 平衡短期增长和长期盈利能力</p>
            """
        else:
            # 找出增长最快的问号产品
            question_products = product_summary[
                product_summary['产品类型'] == '问号产品'] if not product_summary.empty else pd.DataFrame()
            has_high_potential = len(
                question_products[question_products['增长率'] > 50]) > 0 if not question_products.empty else False

            if has_high_potential:
                return """
                    <p>• 重点关注高增长问号产品，加大资源投入</p>
                    <p>• 推动问号产品向明星产品转化</p>
                    <p>• 持续监控明星产品表现，确保增长持续性</p>
                    <p>• 关注市场趋势变化，及时调整产品策略</p>
                """
            else:
                return """
                    <p>• 平衡发展明星和问号产品，维持合理结构</p>
                    <p>• 针对性提升问号产品的市场占有率</p>
                    <p>• 加强明星产品品牌建设，巩固竞争优势</p>
                    <p>• 持续创新，保持产品活力</p>
                """

    elif card_id == "dog":
        dog_percent = analysis.get('dog_percent', 0)

        if dog_percent <= 5:
            return """
                <p>• 保持瘦狗产品的低比例结构，避免资源浪费</p>
                <p>• 继续监控现有瘦狗产品表现，及时淘汰</p>
                <p>• 制定严格的新品退出机制，避免新增瘦狗产品</p>
                <p>• 优化产品生命周期管理，做好产品转型</p>
            """
        elif dog_percent <= 10:
            return """
                <p>• 评估现有瘦狗产品，筛选可能有转机的产品</p>
                <p>• 对无转机产品制定退市计划，逐步淘汰</p>
                <p>• 控制瘦狗产品的资源投入，最小化维护成本</p>
                <p>• 分析瘦狗产品形成原因，避免重复失误</p>
            """
        else:
            return """
                <p>• 立即评估所有瘦狗产品，分类处理</p>
                <p>• 制定分批淘汰计划，优先清理最差产品</p>
                <p>• 考虑部分产品重新定位或升级改造</p>
                <p>• 严格控制瘦狗产品营销费用，避免资源浪费</p>
                <p>• 优化新品开发流程，减少瘦狗产品产生</p>
            """

    return "<p>建议数据加载中...</p>"


def generate_action_plan(card_id):
    """生成行动方案HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>行动计划加载中...</p>"

    if card_id == "product_count":
        is_healthy = st.session_state['analysis_result'].get('is_healthy_mix', False)

        if is_healthy:
            return """
                <p><strong>短期行动（1个月）：</strong>细化产品表现监控，建立产品健康度仪表盘</p>
                <p><strong>中期行动（3个月）：</strong>优化各类产品的资源分配和营销策略</p>
                <p><strong>长期行动（6个月）：</strong>完善产品生命周期管理机制，保持产品组合健康</p>
            """
        else:
            return """
                <p><strong>短期行动（1个月）：</strong>分析产品结构不平衡原因，制定调整计划</p>
                <p><strong>中期行动（3个月）：</strong>重点扶持战略性产品，调整产品组合结构</p>
                <p><strong>长期行动（6个月）：</strong>建立产品组合优化机制，定期评估和调整</p>
            """

    elif card_id == "cash_cow":
        cash_cow_percent = st.session_state['analysis_result'].get('cash_cow_percent', 0)

        if cash_cow_percent < 40:
            return """
                <p><strong>紧急行动（1个月）：</strong>增加现金牛产品促销力度，提高销量</p>
                <p><strong>中期行动（3个月）：</strong>优化渠道覆盖，加强核心终端表现</p>
                <p><strong>长期行动（6个月）：</strong>培育更多现金牛产品，提高产品结构稳定性</p>
            """
        elif cash_cow_percent > 55:
            return """
                <p><strong>短期行动（1个月）：</strong>评估现金牛产品过度依赖风险，优化资源分配</p>
                <p><strong>中期行动（3个月）：</strong>加强明星产品培育，分散产品结构风险</p>
                <p><strong>长期行动（6个月）：</strong>建立产品生命周期预警机制，提前应对增长放缓</p>
            """
        else:
            return """
                <p><strong>短期行动（1个月）：</strong>维持现金牛产品稳定增长，精细化营销策略</p>
                <p><strong>中期行动（3个月）：</strong>优化产品成本结构，提高利润贡献</p>
                <p><strong>长期行动（6个月）：</strong>建立现金牛产品品牌资产，增强市场竞争力</p>
            """

    elif card_id == "star_question":
        star_question_percent = st.session_state['analysis_result'].get('star_question_percent', 0)

        if star_question_percent < 35:
            return """
                <p><strong>短期行动（1个月）：</strong>确定高潜力明星和问号产品，加大投入</p>
                <p><strong>中期行动（3个月）：</strong>开展针对性市场活动，提升销售占比</p>
                <p><strong>长期行动（6个月）：</strong>优化新品开发流程，提高成功率</p>
            """
        elif star_question_percent > 50:
            return """
                <p><strong>短期行动（1个月）：</strong>评估高增长产品投资回报率，优化资源分配</p>
                <p><strong>中期行动（3个月）：</strong>关注部分明星产品向现金牛转化的时机</p>
                <p><strong>长期行动（6个月）：</strong>建立产品均衡发展机制，避免结构失衡</p>
            """
        else:
            return """
                <p><strong>短期行动（1个月）：</strong>分析明星和问号产品增长驱动因素，复制成功经验</p>
                <p><strong>中期行动（3个月）：</strong>重点培育1-2个问号产品，促进向明星产品转化</p>
                <p><strong>长期行动（6个月）：</strong>持续优化产品创新机制，保持产品活力</p>
            """

    elif card_id == "dog":
        dog_percent = st.session_state['analysis_result'].get('dog_percent', 0)

        if dog_percent <= 10:
            return """
                <p><strong>短期行动（1个月）：</strong>评估现有瘦狗产品，制定分类处理方案</p>
                <p><strong>中期行动（3个月）：</strong>逐步淘汰表现最差产品，减少资源占用</p>
                <p><strong>长期行动（6个月）：</strong>完善产品退出机制，保持产品组合高效率</p>
            """
        else:
            return """
                <p><strong>紧急行动（1个月）：</strong>立即评估所有瘦狗产品，确定淘汰和保留名单</p>
                <p><strong>近期行动（3个月）：</strong>实施瘦狗产品淘汰计划，第一批减少30%</p>
                <p><strong>中期行动（6个月）：</strong>优化产品评估体系，建立早期干预机制</p>
            """

    return "<p>行动计划加载中...</p>"


# ==================== 6. 主页面函数 ====================
def show_product_analysis():
    """显示产品分析页面"""
    # 页面样式 - 与sales_dashboard.py统一
    st.markdown(f"""
    <style>
        .main {{
            background-color: {COLORS['light']};
        }}
        .main-header {{
            font-size: 2rem;
            color: {COLORS['primary']};
            text-align: center;
            margin-bottom: 1rem;
        }}
        .card-header {{
            font-size: 1.2rem;
            font-weight: bold;
            color: #444444;
        }}
        .card-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: {COLORS['primary']};
        }}
        .metric-card {{
            background-color: {COLORS['white']};
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
            margin-bottom: 1rem;
        }}
        .card-text {{
            font-size: 0.9rem;
            color: {COLORS['gray']};
        }}
        .alert-box {{
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }}
        .alert-success {{
            background-color: rgba(76, 175, 80, 0.1);
            border-left: 0.5rem solid {COLORS['success']};
        }}
        .alert-warning {{
            background-color: rgba(255, 152, 0, 0.1);
            border-left: 0.5rem solid {COLORS['warning']};
        }}
        .alert-danger {{
            background-color: rgba(244, 67, 54, 0.1);
            border-left: 0.5rem solid {COLORS['danger']};
        }}
        .sub-header {{
            font-size: 1.5rem;
            font-weight: bold;
            color: {COLORS['primary']};
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        .chart-explanation {{
            background-color: rgba(76, 175, 80, 0.1);
            padding: 0.9rem;
            border-radius: 0.5rem;
            margin: 0.8rem 0;
            border-left: 0.5rem solid {COLORS['success']};
        }}
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .stButton > button:hover {{
            background-color: {COLORS['secondary']};
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        }}
    </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.markdown('<div class="main-header">📦 产品分析</div>', unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载产品数据..."):
        sales_data, product_codes, promotion_data = load_product_data()

    if sales_data.empty:
        st.error("无法加载销售数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_data = apply_product_filters(sales_data)

    # 分析数据
    analysis_result = analyze_product_data(filtered_data, product_codes, promotion_data)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("没有符合筛选条件的数据")
        return

    # 获取关键指标
    product_summary = analysis_result.get('product_summary', pd.DataFrame())
    total_products = len(product_summary) if not product_summary.empty else 0
    cash_cow_percent = analysis_result.get('cash_cow_percent', 0)
    star_question_percent = analysis_result.get('star_question_percent', 0)
    dog_percent = analysis_result.get('dog_percent', 0)

    # 显示关键指标卡片
    st.markdown('<div class="sub-header">📊 产品组合概览</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        create_product_flip_card(
            "product_count",
            "产品总数",
            total_products,
            "当前活跃产品数量"
        )

    with col2:
        create_product_flip_card(
            "cash_cow",
            "现金牛产品占比",
            cash_cow_percent,
            "目标范围: 45%-50%",
            is_percentage=True
        )

    col3, col4 = st.columns(2)

    with col3:
        create_product_flip_card(
            "star_question",
            "明星和问号产品占比",
            star_question_percent,
            "目标范围: 40%-45%",
            is_percentage=True
        )

    with col4:
        create_product_flip_card(
            "dog",
            "瘦狗产品占比",
            dog_percent,
            "目标范围: ≤10%",
            is_percentage=True
        )

    # BCG矩阵分析
    st.markdown('<div class="sub-header">📊 BCG矩阵分析</div>', unsafe_allow_html=True)

    if not product_summary.empty:
        col1, col2 = st.columns(2)

        with col1:
            # BCG矩阵散点图
            fig = create_bcg_matrix(product_summary, "产品BCG矩阵分析")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div class="chart-explanation">
                <h4>📊 图表解读</h4>
                <p><strong>BCG矩阵四象限含义：</strong></p>
                <p>• <span style="color:{BCG_COLORS['star']}">明星产品</span>：高销售占比(≥1.5%)、高增长率(≥20%)，需继续投入资源提升市场份额</p>
                <p>• <span style="color:{BCG_COLORS['cash_cow']}">现金牛产品</span>：高销售占比(≥1.5%)、低增长率(<20%)，主要利润来源，需维持市场地位</p>
                <p>• <span style="color:{BCG_COLORS['question']}">问号产品</span>：低销售占比(<1.5%)、高增长率(≥20%)，潜力产品，需评估是否加大投入</p>
                <p>• <span style="color:{BCG_COLORS['dog']}">瘦狗产品</span>：低销售占比(<1.5%)、低增长率(<20%)，表现不佳，需考虑淘汰或重新定位</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 产品组合健康度
            bcg_summary = analysis_result.get('bcg_summary', pd.DataFrame())
            if not bcg_summary.empty:
                # 销售额占比饼图
                fig = create_bcg_pie_chart(bcg_summary, "产品类型销售占比")
                st.plotly_chart(fig, use_container_width=True)

                # 产品数量分布
                product_count_by_type = product_summary.groupby('产品类型').size().reset_index(name='产品数量')
                fig = px.bar(
                    product_count_by_type,
                    x='产品类型',
                    y='产品数量',
                    color='产品类型',
                    title="产品类型数量分布",
                    color_discrete_map=BCG_COLORS
                )

                fig.update_layout(
                    plot_bgcolor=COLORS['white'],
                    paper_bgcolor=COLORS['white']
                )

                st.plotly_chart(fig, use_container_width=True)

    # 产品销售趋势
    st.markdown('<div class="sub-header">📈 产品销售趋势</div>', unsafe_allow_html=True)

    monthly_product_sales = analysis_result.get('monthly_product_sales', pd.DataFrame())
    if not monthly_product_sales.empty:
        # TOP10产品月度销售趋势
        fig = create_product_trend_chart(monthly_product_sales, 10, "TOP10产品月度销售趋势")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        st.markdown(f"""
        <div class="chart-explanation">
            <h4>📊 图表解读</h4>
            <p>上图展示了销售额TOP10产品的月度销售趋势。从图中可以看出哪些产品持续增长，哪些产品表现波动，以及可能存在的季节性因素。可以据此优化产品策略和资源配置。</p>
        </div>
        """, unsafe_allow_html=True)

    # 促销活动分析
    promotion_summary = analysis_result.get('promotion_summary', None)
    if promotion_summary is not None and not promotion_summary.empty:
        st.markdown('<div class="sub-header">🔍 促销活动分析</div>', unsafe_allow_html=True)

        # 促销效果图表
        fig = create_promotion_chart(promotion_summary, "促销活动效果TOP10")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        total_promotions = promotion_summary['促销活动次数'].sum()
        total_expected_sales = promotion_summary['预计销售额（元）'].sum()
        avg_promotion_effect = total_expected_sales / total_promotions if total_promotions > 0 else 0

        st.markdown(f"""
        <div class="chart-explanation">
            <h4>📊 图表解读</h4>
            <p>促销活动总览：共{total_promotions}次促销活动，预计总销售额{format_currency(total_expected_sales)}，平均每次促销效果{format_currency(avg_promotion_effect)}。</p>
            <p>从图表可以看出哪些产品促销效果最好，未来促销资源应优先考虑这些产品，以提高营销投入产出比。</p>
        </div>
        """, unsafe_allow_html=True)

    # 产品组合健康度评估
    st.markdown('<div class="sub-header">📋 产品组合健康度评估</div>', unsafe_allow_html=True)

    is_healthy = analysis_result.get('is_healthy_mix', False)
    health_color = COLORS['success'] if is_healthy else COLORS['warning']
    health_text = "健康" if is_healthy else "需要优化"

    st.markdown(f"""
    <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0.5rem;">
        <h4>📋 产品组合健康度评估</h4>
        <p><strong>当前状态：</strong><span style="color: {health_color};">{health_text}</span></p>
        <p><strong>JBP计划产品模型目标：</strong></p>
        <ul>
            <li>现金牛产品：45%~50%（当前：<span style="color: {COLORS['success'] if 45 <= cash_cow_percent <= 50 else COLORS['warning']};">{format_percentage(cash_cow_percent)}</span>）</li>
            <li>明星&问号产品：40%~45%（当前：<span style="color: {COLORS['success'] if 40 <= star_question_percent <= 45 else COLORS['warning']};">{format_percentage(star_question_percent)}</span>）</li>
            <li>瘦狗产品：≤10%（当前：<span style="color: {COLORS['success'] if dog_percent <= 10 else COLORS['danger']};">{format_percentage(dog_percent)}</span>）</li>
        </ul>
        <p><strong>评估结论：</strong>{get_health_conclusion(cash_cow_percent, star_question_percent, dog_percent)}</p>
    </div>
    """, unsafe_allow_html=True)


def get_health_conclusion(cash_cow, star_question, dog):
    """根据产品组合指标生成健康度结论"""
    issues = []

    if cash_cow < 45:
        issues.append("现金牛产品占比过低，需加强推广")
    elif cash_cow > 50:
        issues.append("现金牛产品占比过高，存在依赖风险")

    if star_question < 40:
        issues.append("明星和问号产品占比不足，未来增长动力不足")
    elif star_question > 45:
        issues.append("明星和问号产品占比过高，短期利润承压")

    if dog > 10:
        issues.append("瘦狗产品占比过高，资源分配效率低")

    if not issues:
        return "产品组合结构健康，符合JBP计划产品模型要求，保持现有策略即可。"
    else:
        return "产品组合存在以下问题：" + "；".join(issues) + "。建议调整产品策略，优化产品组合结构。"


if __name__ == "__main__":
    show_product_analysis()