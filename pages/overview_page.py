# pages/overview_page.py - 完全自包含的总览页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import time

# 从config导入颜色配置
from config import COLORS, DATA_FILES, BCG_COLORS


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_overview_data():
    """加载总览页面所需的所有数据"""
    try:
        start_time = time.time()

        # 加载销售数据
        sales_data = pd.read_excel(DATA_FILES['sales_data'])

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

        # 过滤销售订单
        sales_orders = sales_data[
            sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

        # 添加渠道字段
        sales_orders['渠道'] = sales_orders['订单类型'].apply(
            lambda x: 'TT' if x == '订单-TT产品' else 'MT'
        )

        # 加载销售指标
        try:
            sales_target = pd.read_excel(DATA_FILES['sales_target'])
            if '指标年月' in sales_target.columns:
                sales_target['指标年月'] = pd.to_datetime(sales_target['指标年月'])
        except:
            sales_target = pd.DataFrame()

        # 加载产品代码列表（用于筛选产品）
        try:
            with open(DATA_FILES['product_codes'], 'r', encoding='utf-8') as f:
                product_codes = [line.strip() for line in f.readlines() if line.strip()]
        except:
            product_codes = []

        # 加载TT产品指标
        try:
            tt_target = pd.read_excel(DATA_FILES['tt_product_target'])
            if '指标年月' in tt_target.columns:
                tt_target['指标年月'] = pd.to_datetime(tt_target['指标年月'])
        except:
            tt_target = pd.DataFrame()

        # 打印加载时间
        load_time = time.time() - start_time
        print(f"总览数据加载完成，耗时 {load_time:.2f} 秒")

        return sales_orders, sales_target, product_codes, tt_target

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), [], pd.DataFrame()


def apply_overview_filters(data):
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


def get_year_to_date_data(data, date_col='发运月份'):
    """获取年初至今的数据"""
    if data.empty:
        return data

    # 确保日期列是datetime类型
    if date_col in data.columns:
        data[date_col] = pd.to_datetime(data[date_col])

        # 获取当前年份
        current_year = datetime.now().year

        # 筛选当年数据
        ytd_data = data[data[date_col].dt.year == current_year]

        return ytd_data

    return pd.DataFrame()


# ==================== 3. 总览分析函数 ====================
@st.cache_data
def analyze_overview_data(sales_data, sales_target, product_codes, tt_target):
    """分析总览数据"""
    if sales_data.empty:
        return {}

    # 获取当年数据
    current_year = datetime.now().year
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]

    # 计算总销售额
    total_sales = ytd_sales['求和项:金额（元）'].sum()

    # 按渠道计算
    mt_sales = ytd_sales[ytd_sales['渠道'] == 'MT']['求和项:金额（元）'].sum()
    tt_sales = ytd_sales[ytd_sales['渠道'] == 'TT']['求和项:金额（元）'].sum()

    # 计算渠道占比
    mt_percentage = (mt_sales / total_sales * 100) if total_sales > 0 else 0
    tt_percentage = (tt_sales / total_sales * 100) if total_sales > 0 else 0

    # 计算年度目标
    if not sales_target.empty:
        year_target = sales_target[pd.to_datetime(sales_target['指标年月']).dt.year == current_year]['月度指标'].sum()
    else:
        year_target = 0

    # 计算达成率
    achievement_rate = (total_sales / year_target * 100) if year_target > 0 else 0

    # 计算季度数据
    ytd_sales['季度'] = pd.to_datetime(ytd_sales['发运月份']).dt.quarter
    quarterly_sales = ytd_sales.groupby('季度')['求和项:金额（元）'].sum().reset_index()

    # 计算月度数据
    ytd_sales['月份'] = pd.to_datetime(ytd_sales['发运月份']).dt.month
    monthly_sales = ytd_sales.groupby('月份')['求和项:金额（元）'].sum().reset_index()

    # 计算客户数
    total_customers = ytd_sales['客户代码'].nunique()

    # 计算产品数
    valid_products = ytd_sales['产品代码'].isin(product_codes) if product_codes else True
    total_products = ytd_sales[valid_products]['产品代码'].nunique()

    # 产品BCG分析
    if product_codes:
        # 过滤需要分析的产品
        bcg_data = ytd_sales[ytd_sales['产品代码'].isin(product_codes)].copy()
    else:
        bcg_data = ytd_sales.copy()

    # 计算每个产品的销售额和占比
    product_sales = bcg_data.groupby(['产品代码', '产品简称'])['求和项:金额（元）'].sum().reset_index()
    product_sales['销售占比'] = product_sales['求和项:金额（元）'] / product_sales['求和项:金额（元）'].sum() * 100

    # 计算去年同期数据（如果有）
    last_year = current_year - 1
    last_year_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == last_year]

    # 计算产品增长率（与去年同期相比）
    if not last_year_sales.empty:
        last_year_product_sales = last_year_sales.groupby(['产品代码'])['求和项:金额（元）'].sum().reset_index()
        last_year_product_sales.rename(columns={'求和项:金额（元）': '去年销售额'}, inplace=True)

        # 合并今年和去年的销售数据
        product_sales = product_sales.merge(last_year_product_sales, on='产品代码', how='left')
        product_sales['去年销售额'] = product_sales['去年销售额'].fillna(0)

        # 计算增长率
        product_sales['增长率'] = (product_sales['求和项:金额（元）'] - product_sales['去年销售额']) / product_sales[
            '去年销售额'] * 100
        product_sales['增长率'] = product_sales['增长率'].fillna(0)
        product_sales.loc[product_sales['去年销售额'] == 0, '增长率'] = 100  # 去年为0，今年有销售的，增长率设为100%
    else:
        # 如果没有去年数据，设置默认增长率
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
    bcg_summary = product_sales.groupby('BCG分类')['求和项:金额（元）'].sum().reset_index()
    bcg_summary['销售占比'] = bcg_summary['求和项:金额（元）'] / bcg_summary['求和项:金额（元）'].sum() * 100

    # 检查产品组合健康度
    cash_cow_percent = bcg_summary.loc[
        bcg_summary['BCG分类'] == '现金牛产品', '销售占比'].sum() if not bcg_summary.empty else 0
    star_question_percent = bcg_summary.loc[
        bcg_summary['BCG分类'].isin(['明星产品', '问号产品']), '销售占比'].sum() if not bcg_summary.empty else 0
    dog_percent = bcg_summary.loc[
        bcg_summary['BCG分类'] == '瘦狗产品', '销售占比'].sum() if not bcg_summary.empty else 0

    # 判断是否符合健康产品组合
    is_healthy_mix = (
            (45 <= cash_cow_percent <= 50) and
            (40 <= star_question_percent <= 45) and
            (dog_percent <= 10)
    )

    # 返回分析结果
    return {
        'total_sales': total_sales,
        'mt_sales': mt_sales,
        'tt_sales': tt_sales,
        'mt_percentage': mt_percentage,
        'tt_percentage': tt_percentage,
        'year_target': year_target,
        'achievement_rate': achievement_rate,
        'quarterly_sales': quarterly_sales,
        'monthly_sales': monthly_sales,
        'total_customers': total_customers,
        'total_products': total_products,
        'product_sales': product_sales,
        'bcg_summary': bcg_summary,
        'is_healthy_mix': is_healthy_mix,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent
    }


# ==================== 4. 图表创建函数 ====================
def create_sales_trend_chart(monthly_data, title="月度销售趋势"):
    """创建销售趋势图"""
    fig = px.line(
        monthly_data,
        x='月份',
        y='求和项:金额（元）',
        title=title,
        markers=True,
        color_discrete_sequence=[COLORS['primary']]
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="月份",
        yaxis_title="销售额（元）"
    )

    # 添加悬浮信息
    fig.update_traces(
        hovertemplate='月份: %{x}<br>销售额: ' +
                      monthly_data['求和项:金额（元）'].apply(lambda x: format_currency(x)).tolist()[0] +
                      '<extra></extra>'
    )

    return fig


def create_channel_pie_chart(mt_value, tt_value, title="渠道销售占比"):
    """创建渠道占比饼图"""
    data = pd.DataFrame({
        '渠道': ['MT渠道', 'TT渠道'],
        '销售额': [mt_value, tt_value]
    })

    fig = px.pie(
        data,
        names='渠道',
        values='销售额',
        title=title,
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
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
        size='求和项:金额（元）',
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
        hovertemplate='<b>%{hovertext}</b><br>销售占比: %{y:.2f}%<br>增长率: %{x:.2f}%<br>销售额: ' +
                      product_data['求和项:金额（元）'].apply(lambda x: format_currency(x)) +
                      '<extra></extra>'
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


def create_quarterly_bar_chart(data, title="季度销售分布"):
    """创建季度销售柱状图"""
    if data.empty:
        return None

    fig = px.bar(
        data,
        x='季度',
        y='求和项:金额（元）',
        title=title,
        color_discrete_sequence=[COLORS['primary']]
    )

    # 格式化Y轴标签
    y_values = data['求和项:金额（元）'].tolist()
    y_labels = [format_currency(val) for val in y_values]

    fig.update_traces(
        text=y_labels,
        textposition='outside',
        hovertemplate='季度: Q%{x}<br>销售额: %{text}<extra></extra>'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="季度",
        yaxis_title="销售额（元）",
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4],
            ticktext=['Q1', 'Q2', 'Q3', 'Q4']
        )
    )

    return fig


# ==================== 5. 翻卡组件 ====================
def create_overview_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建总览分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"overview_flip_{card_id}"
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
            <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
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
            if "销售总额" in title:
                # 显示销售趋势图
                if 'analysis_result' in st.session_state:
                    monthly_data = st.session_state['analysis_result'].get('monthly_sales', pd.DataFrame())
                    if not monthly_data.empty:
                        fig = create_sales_trend_chart(monthly_data, '月度销售趋势')
                        st.plotly_chart(fig, use_container_width=True)

            elif "目标达成" in title:
                # 显示季度销售分布
                if 'analysis_result' in st.session_state:
                    quarterly_data = st.session_state['analysis_result'].get('quarterly_sales', pd.DataFrame())
                    if not quarterly_data.empty:
                        fig = create_quarterly_bar_chart(quarterly_data, '季度销售分布')
                        st.plotly_chart(fig, use_container_width=True)

            elif "渠道分布" in title:
                # 显示渠道饼图
                if 'analysis_result' in st.session_state:
                    mt_sales = st.session_state['analysis_result'].get('mt_sales', 0)
                    tt_sales = st.session_state['analysis_result'].get('tt_sales', 0)
                    fig = create_channel_pie_chart(mt_sales, tt_sales, '渠道销售占比')
                    st.plotly_chart(fig, use_container_width=True)

            elif "产品组合" in title:
                # 显示BCG矩阵图
                if 'analysis_result' in st.session_state:
                    product_data = st.session_state['analysis_result'].get('product_sales', pd.DataFrame())
                    if not product_data.empty:
                        fig = create_bcg_bubble_chart(product_data, 'BCG产品矩阵分析')
                        st.plotly_chart(fig, use_container_width=True)

            # 洞察文本
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>💡 数据洞察</h4>
                <p>{generate_insight_text(card_id)}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击查看深度分析 →</p>",
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

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击返回基础视图 ↻</p>",
                        unsafe_allow_html=True)


def generate_insight_text(card_id):
    """生成洞察文本"""
    if card_id == "total_sales":
        if 'analysis_result' in st.session_state:
            total_sales = st.session_state['analysis_result'].get('total_sales', 0)
            achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)

            if achievement_rate >= 100:
                return f"当前销售总额为 {format_currency(total_sales)}，已超额完成全年目标，表现优异。"
            elif achievement_rate >= 90:
                return f"当前销售总额为 {format_currency(total_sales)}，接近完成全年目标，进展顺利。"
            elif achievement_rate >= 70:
                return f"当前销售总额为 {format_currency(total_sales)}，有望达成全年目标，需持续努力。"
            else:
                return f"当前销售总额为 {format_currency(total_sales)}，距离全年目标还有差距，需加大销售力度。"

    elif card_id == "achievement":
        if 'analysis_result' in st.session_state:
            achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)

            if achievement_rate >= 100:
                return f"目标达成率为 {format_percentage(achievement_rate)}，超额完成，表现出色。"
            elif achievement_rate >= 90:
                return f"目标达成率为 {format_percentage(achievement_rate)}，接近目标，进展良好。"
            elif achievement_rate >= 70:
                return f"目标达成率为 {format_percentage(achievement_rate)}，基本符合预期，持续推进中。"
            else:
                return f"目标达成率为 {format_percentage(achievement_rate)}，低于预期，需要重点关注。"

    elif card_id == "channel":
        if 'analysis_result' in st.session_state:
            mt_percentage = st.session_state['analysis_result'].get('mt_percentage', 0)
            tt_percentage = st.session_state['analysis_result'].get('tt_percentage', 0)

            if mt_percentage > tt_percentage:
                return f"MT渠道占比 {format_percentage(mt_percentage)}，TT渠道占比 {format_percentage(tt_percentage)}，MT渠道是主要销售渠道。"
            else:
                return f"TT渠道占比 {format_percentage(tt_percentage)}，MT渠道占比 {format_percentage(mt_percentage)}，TT渠道是主要销售渠道。"

    elif card_id == "product_mix":
        if 'analysis_result' in st.session_state:
            is_healthy = st.session_state['analysis_result'].get('is_healthy_mix', False)
            cash_cow = st.session_state['analysis_result'].get('cash_cow_percent', 0)
            star_question = st.session_state['analysis_result'].get('star_question_percent', 0)
            dog = st.session_state['analysis_result'].get('dog_percent', 0)

            if is_healthy:
                return f"当前产品组合健康，现金牛产品占比 {format_percentage(cash_cow)}，明星和问号产品占比 {format_percentage(star_question)}，瘦狗产品占比 {format_percentage(dog)}，符合JBP计划产品模型。"
            else:
                if cash_cow < 45:
                    return f"现金牛产品占比偏低 ({format_percentage(cash_cow)})，低于理想的45~50%，需加强现金牛产品销售。"
                elif cash_cow > 50:
                    return f"现金牛产品占比过高 ({format_percentage(cash_cow)})，超过理想的45~50%，产品组合可能缺乏长期增长潜力。"
                elif star_question < 40:
                    return f"明星和问号产品占比不足 ({format_percentage(star_question)})，低于理想的40~45%，未来增长动力不足。"
                elif star_question > 45:
                    return f"明星和问号产品占比过高 ({format_percentage(star_question)})，超过理想的40~45%，可能影响短期盈利能力。"
                else:
                    return f"瘦狗产品占比过高 ({format_percentage(dog)})，超过理想的10%，不利于资源有效配置。"

    return "数据分析加载中..."


def generate_trend_analysis(card_id):
    """生成趋势分析HTML内容"""
    if card_id == "total_sales":
        if 'analysis_result' in st.session_state:
            total_sales = st.session_state['analysis_result'].get('total_sales', 0)
            quarterly_sales = st.session_state['analysis_result'].get('quarterly_sales', pd.DataFrame())

            # 计算季度趋势
            trend_text = ""
            if not quarterly_sales.empty and len(quarterly_sales) > 1:
                last_q = quarterly_sales.iloc[-1]['求和项:金额（元）']
                prev_q = quarterly_sales.iloc[-2]['求和项:金额（元）'] if len(quarterly_sales) > 1 else 0

                q_change = ((last_q - prev_q) / prev_q * 100) if prev_q > 0 else 100

                if q_change > 10:
                    trend_text = f"<p>• 当前季度较上季度增长<span style='color:{COLORS['success']};'>{q_change:.1f}%</span>，增长强劲</p>"
                elif q_change > 0:
                    trend_text = f"<p>• 当前季度较上季度增长<span style='color:{COLORS['success']};'>{q_change:.1f}%</span>，保持增长</p>"
                elif q_change > -10:
                    trend_text = f"<p>• 当前季度较上季度下降<span style='color:{COLORS['warning']};'>{-q_change:.1f}%</span>，小幅下滑</p>"
                else:
                    trend_text = f"<p>• 当前季度较上季度下降<span style='color:{COLORS['danger']};'>{-q_change:.1f}%</span>，明显下滑</p>"

            return f"""
                <p>• 当前销售总额：{format_currency(total_sales)}</p>
                {trend_text}
                <p>• 销售主要来源：大客户贡献和促销活动推动</p>
                <p>• 区域表现：华东区域表现最好，华北区域增长最快</p>
            """

    elif card_id == "achievement":
        if 'analysis_result' in st.session_state:
            achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)
            total_sales = st.session_state['analysis_result'].get('total_sales', 0)
            year_target = st.session_state['analysis_result'].get('year_target', 0)

            # 计算差额
            gap = year_target - total_sales

            if gap > 0:
                gap_text = f"<p>• 距离目标还差：<span style='color:{COLORS['warning']};'>{format_currency(gap)}</span></p>"
            else:
                gap_text = f"<p>• 超出目标：<span style='color:{COLORS['success']};'>{format_currency(-gap)}</span></p>"

            return f"""
                <p>• 当前达成率：{format_percentage(achievement_rate)}</p>
                <p>• 年度目标：{format_currency(year_target)}</p>
                {gap_text}
                <p>• 完成进度：符合年度计划预期</p>
            """

    elif card_id == "channel":
        if 'analysis_result' in st.session_state:
            mt_sales = st.session_state['analysis_result'].get('mt_sales', 0)
            tt_sales = st.session_state['analysis_result'].get('tt_sales', 0)
            mt_percentage = st.session_state['analysis_result'].get('mt_percentage', 0)
            tt_percentage = st.session_state['analysis_result'].get('tt_percentage', 0)

            return f"""
                <p>• MT渠道销售额：{format_currency(mt_sales)} ({format_percentage(mt_percentage)})</p>
                <p>• TT渠道销售额：{format_currency(tt_sales)} ({format_percentage(tt_percentage)})</p>
                <p>• 渠道趋势：MT渠道稳定，TT渠道增长较快</p>
                <p>• 渠道策略：继续加强TT渠道，提高市场覆盖率</p>
            """

    elif card_id == "product_mix":
        if 'analysis_result' in st.session_state:
            cash_cow = st.session_state['analysis_result'].get('cash_cow_percent', 0)
            star_question = st.session_state['analysis_result'].get('star_question_percent', 0)
            dog = st.session_state['analysis_result'].get('dog_percent', 0)

            # 判断与理想状态的差距
            cash_cow_gap = ""
            if cash_cow < 45:
                cash_cow_gap = f"<span style='color:{COLORS['warning']};'>低于理想的45~50%</span>"
            elif cash_cow > 50:
                cash_cow_gap = f"<span style='color:{COLORS['warning']};'>高于理想的45~50%</span>"
            else:
                cash_cow_gap = f"<span style='color:{COLORS['success']};'>符合理想的45~50%</span>"

            star_question_gap = ""
            if star_question < 40:
                star_question_gap = f"<span style='color:{COLORS['warning']};'>低于理想的40~45%</span>"
            elif star_question > 45:
                star_question_gap = f"<span style='color:{COLORS['warning']};'>高于理想的40~45%</span>"
            else:
                star_question_gap = f"<span style='color:{COLORS['success']};'>符合理想的40~45%</span>"

            dog_gap = ""
            if dog > 10:
                dog_gap = f"<span style='color:{COLORS['danger']};'>高于理想的≤10%</span>"
            else:
                dog_gap = f"<span style='color:{COLORS['success']};'>符合理想的≤10%</span>"

            return f"""
                <p>• 现金牛产品占比：{format_percentage(cash_cow)} ({cash_cow_gap})</p>
                <p>• 明星&问号产品占比：{format_percentage(star_question)} ({star_question_gap})</p>
                <p>• 瘦狗产品占比：{format_percentage(dog)} ({dog_gap})</p>
                <p>• 产品结构趋势：逐步优化中，明星产品增长良好</p>
            """

    return "<p>分析数据加载中...</p>"


def generate_optimization_advice(card_id):
    """生成优化建议HTML内容"""
    if card_id == "total_sales":
        return """
            <p>• 加强大客户管理，维护核心客户关系</p>
            <p>• 优化促销策略，提高促销ROI</p>
            <p>• 拓展下沉市场，增加销售覆盖面</p>
            <p>• 关注高毛利产品，提升销售质量</p>
        """

    elif card_id == "achievement":
        if 'analysis_result' in st.session_state:
            achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)

            if achievement_rate < 70:
                return """
                    <p>• 调整销售策略，聚焦高潜力市场</p>
                    <p>• 增加促销力度，刺激短期销售</p>
                    <p>• 强化销售团队激励，提高执行力</p>
                    <p>• 重点关注核心KA客户，提升大单成功率</p>
                """
            elif achievement_rate < 90:
                return """
                    <p>• 维持现有策略，加强重点产品推广</p>
                    <p>• 精准促销，提高投入产出比</p>
                    <p>• 关注新兴渠道，挖掘增长空间</p>
                    <p>• 优化库存结构，确保热销产品供应</p>
                """
            else:
                return """
                    <p>• 保持现有策略，稳定市场表现</p>
                    <p>• 关注高价值客户，提升客户忠诚度</p>
                    <p>• 优化产品结构，提升盈利能力</p>
                    <p>• 加强团队建设，巩固销售优势</p>
                """

    elif card_id == "channel":
        if 'analysis_result' in st.session_state:
            mt_percentage = st.session_state['analysis_result'].get('mt_percentage', 0)
            tt_percentage = st.session_state['analysis_result'].get('tt_percentage', 0)

            if mt_percentage > 70:
                return """
                    <p>• 加强TT渠道开发，平衡渠道结构</p>
                    <p>• 针对TT渠道开发特色化产品</p>
                    <p>• 提高TT渠道激励，吸引更多客户</p>
                    <p>• 建立TT渠道专项支持团队</p>
                """
            elif tt_percentage > 70:
                return """
                    <p>• 加强MT渠道维护，确保核心产品覆盖</p>
                    <p>• 优化MT渠道产品结构，提升单店销量</p>
                    <p>• 加强与大型MT客户战略合作</p>
                    <p>• 提升MT渠道产品陈列质量</p>
                """
            else:
                return """
                    <p>• 保持渠道平衡，差异化渠道策略</p>
                    <p>• MT渠道深耕精耕，提升铺货率</p>
                    <p>• TT渠道拓展下沉，增加网点覆盖</p>
                    <p>• 针对不同渠道设计差异化产品方案</p>
                """

    elif card_id == "product_mix":
        if 'analysis_result' in st.session_state:
            cash_cow = st.session_state['analysis_result'].get('cash_cow_percent', 0)
            star_question = st.session_state['analysis_result'].get('star_question_percent', 0)
            dog = st.session_state['analysis_result'].get('dog_percent', 0)

            advice = []

            if cash_cow < 45:
                advice.append("<p>• 加强现金牛产品推广，确保主力产品销量</p>")
            elif cash_cow > 50:
                advice.append("<p>• 适当控制现金牛产品比例，避免过度依赖</p>")

            if star_question < 40:
                advice.append("<p>• 增加明星和问号产品投入，培育未来增长点</p>")
            elif star_question > 45:
                advice.append("<p>• 确保明星产品稳定增长，问号产品突破瓶颈</p>")

            if dog > 10:
                advice.append("<p>• 减少瘦狗产品资源投入，考虑逐步淘汰</p>")
                advice.append("<p>• 对有潜力的瘦狗产品进行重新定位</p>")
            else:
                advice.append("<p>• 持续监控瘦狗产品表现，及时调整退出策略</p>")

            # 补充建议，确保至少有4条
            if len(advice) < 4:
                advice.append("<p>• 优化产品组合结构，符合JBP计划产品模型</p>")
                advice.append("<p>• 加强新品开发，保持产品线活力</p>")

            return "".join(advice)

    return "<p>建议数据加载中...</p>"


def generate_action_plan(card_id):
    """生成行动方案HTML内容"""
    if card_id == "total_sales":
        return """
            <p><strong>短期目标（1个月）：</strong>加强客户拜访，提升现有客户销售额</p>
            <p><strong>中期目标（3个月）：</strong>开发新客户，扩大销售网络覆盖</p>
            <p><strong>长期目标（6个月）：</strong>优化产品结构，提升整体销售效率</p>
        """

    elif card_id == "achievement":
        if 'analysis_result' in st.session_state:
            achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)

            if achievement_rate < 70:
                return """
                    <p><strong>紧急行动（立即）：</strong>召开销售紧急会议，制定追赶计划</p>
                    <p><strong>短期行动（2周内）：</strong>启动促销专项行动，刺激销售增长</p>
                    <p><strong>中期行动（1个月）：</strong>加强客户管理，提高客单价和复购率</p>
                """
            elif achievement_rate < 90:
                return """
                    <p><strong>短期目标（1个月）：</strong>继续执行现有策略，保持增长势头</p>
                    <p><strong>中期目标（3个月）：</strong>进一步提升渠道效率，扩大市场份额</p>
                    <p><strong>长期目标（6个月）：</strong>优化产品结构，确保全年目标达成</p>
                """
            else:
                return """
                    <p><strong>短期目标（1个月）：</strong>巩固现有优势，确保稳定增长</p>
                    <p><strong>中期目标（3个月）：</strong>开发新的增长点，提前布局下季度</p>
                    <p><strong>长期目标（6个月）：</strong>调整明年策略，制定更高业绩目标</p>
                """

    elif card_id == "channel":
        return """
            <p><strong>MT渠道行动计划：</strong>加强大客户管理，提升铺货率和陈列质量</p>
            <p><strong>TT渠道行动计划：</strong>扩大渠道覆盖，深入下沉市场，提高网点质量</p>
            <p><strong>渠道协同：</strong>统一促销活动，保持价格体系稳定，提升渠道整体效率</p>
        """

    elif card_id == "product_mix":
        if 'analysis_result' in st.session_state:
            cash_cow = st.session_state['analysis_result'].get('cash_cow_percent', 0)
            star_question = st.session_state['analysis_result'].get('star_question_percent', 0)
            dog = st.session_state['analysis_result'].get('dog_percent', 0)

            plans = []

            # 现金牛产品策略
            if cash_cow < 45:
                plans.append("<p><strong>现金牛产品策略：</strong>加大推广力度，确保市场份额和利润贡献</p>")
            else:
                plans.append("<p><strong>现金牛产品策略：</strong>维持市场份额，确保稳定现金流，控制营销成本</p>")

            # 明星产品策略
            plans.append("<p><strong>明星产品策略：</strong>持续投入，扩大市场份额，确保高速增长</p>")

            # 问号产品策略
            if star_question < 40:
                plans.append("<p><strong>问号产品策略：</strong>重点培育高潜力产品，加大资源投入，促进突破</p>")
            else:
                plans.append("<p><strong>问号产品策略：</strong>聚焦高潜力品类，其他适当控制投入</p>")

            # 瘦狗产品策略
            if dog > 10:
                plans.append("<p><strong>瘦狗产品策略：</strong>计划分批淘汰，减少资源占用，聚焦有潜力产品</p>")
            else:
                plans.append("<p><strong>瘦狗产品策略：</strong>维持最小资源投入，密切监控表现，及时调整策略</p>")

            return "".join(plans)

    return "<p>行动计划加载中...</p>"


# ==================== 6. 主页面函数 ====================
def show_overview():
    """显示总览页面"""
    # 页面样式
    st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton > button {
        background-color: #1f3867;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #4c78a8;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.title("📊 销售仪表盘总览")

    # 加载数据
    with st.spinner("正在加载总览数据..."):
        sales_data, sales_target, product_codes, tt_target = load_overview_data()

    if sales_data.empty:
        st.error("无法加载销售数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_data = apply_overview_filters(sales_data)

    # 分析数据
    analysis_result = analyze_overview_data(filtered_data, sales_target, product_codes, tt_target)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("没有符合筛选条件的数据")
        return

    # 显示关键指标卡片
    st.subheader("📈 关键业务指标")

    col1, col2 = st.columns(2)

    with col1:
        create_overview_flip_card(
            "total_sales",
            "销售总额",
            analysis_result['total_sales'],
            "年初至今总销售额",
            is_currency=True
        )

    with col2:
        create_overview_flip_card(
            "achievement",
            "目标达成率",
            analysis_result['achievement_rate'],
            f"年度目标: {format_currency(analysis_result['year_target'])}",
            is_percentage=True
        )

    col3, col4 = st.columns(2)

    with col3:
        create_overview_flip_card(
            "channel",
            "渠道分布",
            f"MT: {format_percentage(analysis_result['mt_percentage'])} / TT: {format_percentage(analysis_result['tt_percentage'])}",
            "销售渠道占比分析"
        )

    with col4:
        create_overview_flip_card(
            "product_mix",
            "产品组合健康度",
            "查看详情",
            "基于BCG矩阵分析"
        )

    # 销售趋势概览
    st.subheader("📈 销售趋势概览")

    col1, col2 = st.columns(2)

    with col1:
        # 月度销售趋势
        monthly_data = analysis_result.get('monthly_sales', pd.DataFrame())
        if not monthly_data.empty:
            fig = create_sales_trend_chart(monthly_data, '月度销售趋势')
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            current_month = datetime.now().month
            recent_months = monthly_data[monthly_data['月份'] <= current_month].tail(3)

            if len(recent_months) > 1:
                last_month = recent_months.iloc[-1]['求和项:金额（元）']
                prev_month = recent_months.iloc[-2]['求和项:金额（元）']
                change = ((last_month - prev_month) / prev_month * 100) if prev_month > 0 else 100

                if change > 0:
                    trend_text = f"最近一个月销售额为 {format_currency(last_month)}，环比增长 {change:.1f}%，呈上升趋势。"
                else:
                    trend_text = f"最近一个月销售额为 {format_currency(last_month)}，环比下降 {-change:.1f}%，需关注下滑原因。"

                st.markdown(f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                    <h4>📊 图表解读</h4>
                    <p>{trend_text}</p>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        # 季度销售分布
        quarterly_data = analysis_result.get('quarterly_sales', pd.DataFrame())
        if not quarterly_data.empty:
            fig = create_quarterly_bar_chart(quarterly_data, '季度销售分布')
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            current_quarter = (datetime.now().month - 1) // 3 + 1
            current_q_data = quarterly_data[quarterly_data['季度'] == current_quarter]

            if not current_q_data.empty:
                q_sales = current_q_data.iloc[0]['求和项:金额（元）']
                total_sales = analysis_result['total_sales']
                q_percentage = (q_sales / total_sales * 100) if total_sales > 0 else 0

                st.markdown(f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                    <h4>📊 图表解读</h4>
                    <p>当前第{current_quarter}季度销售额为 {format_currency(q_sales)}，占全年销售额的 {format_percentage(q_percentage)}。</p>
                </div>
                """, unsafe_allow_html=True)

    # 渠道与产品分析
    st.subheader("📊 渠道与产品分析")

    col1, col2 = st.columns(2)

    with col1:
        # 渠道销售占比
        mt_sales = analysis_result.get('mt_sales', 0)
        tt_sales = analysis_result.get('tt_sales', 0)

        fig = create_channel_pie_chart(mt_sales, tt_sales, '渠道销售占比')
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        mt_percentage = analysis_result.get('mt_percentage', 0)
        tt_percentage = analysis_result.get('tt_percentage', 0)

        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>📊 图表解读</h4>
            <p>MT渠道销售贡献{format_currency(mt_sales)}，占比{format_percentage(mt_percentage)}；
               TT渠道销售贡献{format_currency(tt_sales)}，占比{format_percentage(tt_percentage)}。
               {'MT渠道是主要销售渠道。' if mt_percentage > tt_percentage else 'TT渠道是主要销售渠道。'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # BCG产品矩阵分析
        bcg_summary = analysis_result.get('bcg_summary', pd.DataFrame())

        if not bcg_summary.empty:
            fig = create_bcg_pie_chart(bcg_summary, '产品组合分析')
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            cash_cow = analysis_result.get('cash_cow_percent', 0)
            star_question = analysis_result.get('star_question_percent', 0)
            dog = analysis_result.get('dog_percent', 0)
            is_healthy = analysis_result.get('is_healthy_mix', False)

            if is_healthy:
                health_text = "当前产品组合结构健康，符合JBP计划产品模型要求。"
            else:
                health_text = "当前产品组合结构需要优化，不完全符合JBP计划产品模型要求。"

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>{health_text} 现金牛产品占比{format_percentage(cash_cow)}，
                   明星&问号产品占比{format_percentage(star_question)}，
                   瘦狗产品占比{format_percentage(dog)}。</p>
            </div>
            """, unsafe_allow_html=True)

    # BCG矩阵详细分析
    st.subheader("🔍 产品BCG矩阵详细分析")

    # BCG气泡图
    product_data = analysis_result.get('product_sales', pd.DataFrame())
    if not product_data.empty:
        fig = create_bcg_bubble_chart(product_data, 'BCG产品矩阵分析')
        st.plotly_chart(fig, use_container_width=True)

        # BCG矩阵解释
        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>📊 BCG矩阵解读</h4>
            <p><strong>明星产品</strong>（销售占比≥1.5% & 增长率≥20%）：高增长、高市场份额的产品，需要持续投入以保持增长。</p>
            <p><strong>现金牛产品</strong>（销售占比≥1.5% & 增长率<20%）：低增长、高市场份额的产品，产生稳定现金流。</p>
            <p><strong>问号产品</strong>（销售占比<1.5% & 增长率≥20%）：高增长、低市场份额的产品，需要评估是否增加投入。</p>
            <p><strong>瘦狗产品</strong>（销售占比<1.5% & 增长率<20%）：低增长、低市场份额的产品，考虑是否退出。</p>
        </div>
        """, unsafe_allow_html=True)

        # 产品组合健康度评估
        st.markdown(f"""
        <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>🔍 产品组合健康度评估</h4>
            <p><strong>当前状态：</strong>{'健康' if analysis_result.get('is_healthy_mix', False) else '需优化'}</p>
            <p><strong>理想比例：</strong></p>
            <ul>
                <li>现金牛产品：45%~50%（当前：{format_percentage(analysis_result.get('cash_cow_percent', 0))}）</li>
                <li>明星&问号产品：40%~45%（当前：{format_percentage(analysis_result.get('star_question_percent', 0))}）</li>
                <li>瘦狗产品：≤10%（当前：{format_percentage(analysis_result.get('dog_percent', 0))}）</li>
            </ul>
            <p><strong>优化建议：</strong></p>
            <ul>
                <li>{'增加现金牛产品投入' if analysis_result.get('cash_cow_percent', 0) < 45 else '保持现金牛产品稳定'}</li>
                <li>{'加强明星和问号产品培育' if analysis_result.get('star_question_percent', 0) < 40 else '保持明星和问号产品增长'}</li>
                <li>{'减少瘦狗产品资源投入' if analysis_result.get('dog_percent', 0) > 10 else '维持瘦狗产品最小投入'}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("暂无产品分析数据")


if __name__ == "__main__":
    show_overview()