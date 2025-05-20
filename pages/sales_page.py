# pages/sales_page.py - 完全自包含的销售分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 从config导入颜色配置
from config import COLORS, DATA_FILES


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_sales_data():
    """加载销售分析所需的所有数据"""
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

        # 加载销售指标
        try:
            sales_target = pd.read_excel(DATA_FILES['sales_target'])
            if '指标年月' in sales_target.columns:
                sales_target['指标年月'] = pd.to_datetime(sales_target['指标年月'])
        except:
            sales_target = pd.DataFrame()

        # 加载TT产品指标
        try:
            tt_target = pd.read_excel(DATA_FILES['tt_product_target'])
            if '指标年月' in tt_target.columns:
                tt_target['指标年月'] = pd.to_datetime(tt_target['指标年月'])
        except:
            tt_target = pd.DataFrame()

        return sales_orders, sales_target, tt_target

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def apply_sales_filters(data):
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


# ==================== 3. 销售分析函数 ====================
def analyze_sales_data(sales_data, sales_target, tt_target):
    """分析销售数据"""
    if sales_data.empty:
        return {}

    # 获取当前年份和月份
    current_year = datetime.now().year
    current_month = datetime.now().month
    previous_year = current_year - 1

    # 年初至今销售数据
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]
    ytd_sales_amount = ytd_sales['求和项:金额（元）'].sum()

    # 上年度同期销售数据
    last_ytd_sales = sales_data[
        (pd.to_datetime(sales_data['发运月份']).dt.year == previous_year) &
        (pd.to_datetime(sales_data['发运月份']).dt.month <= current_month)
        ]
    last_ytd_sales_amount = last_ytd_sales['求和项:金额（元）'].sum()

    # 计算同比增长率
    yoy_growth = (
                             ytd_sales_amount - last_ytd_sales_amount) / last_ytd_sales_amount * 100 if last_ytd_sales_amount > 0 else 0

    # 计算年度销售目标和达成率
    if not sales_target.empty:
        current_year_targets = sales_target[pd.to_datetime(sales_target['指标年月']).dt.year == current_year]
        annual_target = current_year_targets['月度指标'].sum() if not current_year_targets.empty else 0
        achievement_rate = ytd_sales_amount / annual_target * 100 if annual_target > 0 else 0
    else:
        annual_target = 0
        achievement_rate = 0

    # 按渠道分析
    channel_data = ytd_sales.groupby('渠道')['求和项:金额（元）'].sum().reset_index()
    channel_data['占比'] = channel_data['求和项:金额（元）'] / ytd_sales_amount * 100 if ytd_sales_amount > 0 else 0

    # MT和TT渠道销售额
    mt_sales = channel_data.loc[channel_data['渠道'] == 'MT', '求和项:金额（元）'].sum() if not channel_data.empty else 0
    tt_sales = channel_data.loc[channel_data['渠道'] == 'TT', '求和项:金额（元）'].sum() if not channel_data.empty else 0

    # 月度销售趋势
    monthly_sales = ytd_sales.groupby(pd.Grouper(key='发运月份', freq='M'))['求和项:金额（元）'].sum().reset_index()
    monthly_sales['月份'] = monthly_sales['发运月份'].dt.month

    # 季度销售趋势
    quarterly_sales = ytd_sales.groupby(pd.Grouper(key='发运月份', freq='Q'))['求和项:金额（元）'].sum().reset_index()
    quarterly_sales['季度'] = quarterly_sales['发运月份'].dt.quarter

    # 销售人员分析
    if '申请人' in ytd_sales.columns:
        salesperson_sales = ytd_sales.groupby('申请人')['求和项:金额（元）'].sum().reset_index()
        salesperson_sales = salesperson_sales.sort_values('求和项:金额（元）', ascending=False)
    else:
        salesperson_sales = pd.DataFrame()

    # TT产品达成率分析
    tt_achievement = {}
    if not tt_target.empty and '订单-TT产品' in sales_data['订单类型'].values:
        tt_sales_data = sales_data[sales_data['订单类型'] == '订单-TT产品']
        tt_sales_by_city = tt_sales_data.groupby('城市')['求和项:金额（元）'].sum().reset_index()

        # 合并TT销售和目标数据
        if not tt_sales_by_city.empty and '城市' in tt_target.columns:
            tt_current_year = tt_target[pd.to_datetime(tt_target['指标年月']).dt.year == current_year]
            if not tt_current_year.empty:
                tt_achievement['有目标城市数'] = len(tt_current_year['城市'].unique())
                tt_achievement['有销售城市数'] = len(tt_sales_by_city['城市'].unique())

                # C60城市达成率
                c60_target = tt_current_year[tt_current_year['城市类型'] == 'C60']
                c60_sales = tt_sales_by_city[tt_sales_by_city['城市'].isin(c60_target['城市'])]

                tt_achievement['C60目标总额'] = c60_target['月度指标'].sum()
                tt_achievement['C60销售总额'] = c60_sales['求和项:金额（元）'].sum()
                tt_achievement['C60达成率'] = tt_achievement['C60销售总额'] / tt_achievement['C60目标总额'] * 100 if \
                tt_achievement['C60目标总额'] > 0 else 0

                # 非C60城市达成率
                non_c60_target = tt_current_year[tt_current_year['城市类型'] != 'C60']
                non_c60_sales = tt_sales_by_city[~tt_sales_by_city['城市'].isin(c60_target['城市'])]

                tt_achievement['非C60目标总额'] = non_c60_target['月度指标'].sum()
                tt_achievement['非C60销售总额'] = non_c60_sales['求和项:金额（元）'].sum()
                tt_achievement['非C60达成率'] = tt_achievement['非C60销售总额'] / tt_achievement[
                    '非C60目标总额'] * 100 if tt_achievement['非C60目标总额'] > 0 else 0

    return {
        'ytd_sales': ytd_sales_amount,
        'last_ytd_sales': last_ytd_sales_amount,
        'yoy_growth': yoy_growth,
        'annual_target': annual_target,
        'achievement_rate': achievement_rate,
        'channel_data': channel_data,
        'mt_sales': mt_sales,
        'tt_sales': tt_sales,
        'monthly_sales': monthly_sales,
        'quarterly_sales': quarterly_sales,
        'salesperson_sales': salesperson_sales,
        'tt_achievement': tt_achievement
    }


# ==================== 4. 图表创建函数 ====================
def create_sales_trend_chart(data, x_col, y_col, title):
    """创建销售趋势图表"""
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
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
        xaxis_title=x_col,
        yaxis_title="销售额（元）",
        hovermode="x unified"
    )

    # 添加数值标签
    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='top center'
    )

    return fig


def create_sales_bar_chart(data, x_col, y_col, title, color_col=None):
    """创建销售柱状图表"""
    if color_col:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']]
        )
    else:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=[COLORS['primary']]
        )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode="x unified"
    )

    # 添加数值标签
    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )

    return fig


def create_channel_pie_chart(data, title):
    """创建渠道占比饼图"""
    if data.empty:
        return None

    fig = px.pie(
        data,
        names='渠道',
        values='求和项:金额（元）',
        title=title,
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
        hole=0.4
    )

    fig.update_traces(
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_achievement_gauge(achievement_rate, title="年度目标达成率"):
    """创建目标达成率仪表盘"""
    # 确定颜色
    if achievement_rate >= 100:
        color = COLORS['success']
    elif achievement_rate >= 80:
        color = COLORS['warning']
    else:
        color = COLORS['danger']

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=achievement_rate,
        title={'text': title, 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 120], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 67, 54, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(255, 144, 14, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(255, 255, 0, 0.3)'},
                {'range': [100, 120], 'color': 'rgba(50, 205, 50, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )

    return fig


def create_salesperson_chart(data, title):
    """创建销售人员柱状图"""
    if data.empty:
        return None

    # 只保留前10名销售人员
    top_data = data.head(10)

    fig = px.bar(
        top_data,
        x='求和项:金额（元）',
        y='申请人',
        orientation='h',
        title=title,
        color='求和项:金额（元）',
        color_continuous_scale=px.colors.sequential.Blues
    )

    fig.update_layout(
        height=500,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="销售额（元）",
        yaxis_title="销售人员",
        yaxis={'categoryorder': 'total ascending'}
    )

    # 添加数值标签
    fig.update_traces(
        texttemplate='%{x:,.0f}',
        textposition='outside'
    )

    return fig


# ==================== 5. 翻卡组件 ====================
def create_sales_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建销售分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"sales_flip_{card_id}"
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
                # 显示月度销售趋势
                if 'analysis_result' in st.session_state:
                    monthly_data = st.session_state['analysis_result'].get('monthly_sales', pd.DataFrame())
                    if not monthly_data.empty:
                        fig = create_sales_trend_chart(monthly_data, '月份', '求和项:金额（元）', '月度销售趋势')
                        st.plotly_chart(fig, use_container_width=True)

            elif "增长率" in title:
                # 显示同比销售对比
                if 'analysis_result' in st.session_state:
                    monthly_data = st.session_state['analysis_result'].get('monthly_sales', pd.DataFrame())
                    last_year_monthly = st.session_state['analysis_result'].get('last_ytd_sales', 0)
                    if not monthly_data.empty and last_year_monthly > 0:
                        # 创建同比增长率图表
                        current_year = datetime.now().year
                        previous_year = current_year - 1

                        # 创建简单的同比数据表
                        compare_data = pd.DataFrame({
                            '年份': [str(previous_year), str(current_year)],
                            '销售额': [last_year_monthly, st.session_state['analysis_result'].get('ytd_sales', 0)]
                        })

                        fig = create_sales_bar_chart(compare_data, '年份', '销售额', '同比销售对比')
                        st.plotly_chart(fig, use_container_width=True)

            elif "达成率" in title:
                # 显示目标达成率仪表盘
                if 'analysis_result' in st.session_state:
                    achievement_rate = st.session_state['analysis_result'].get('achievement_rate', 0)
                    fig = create_achievement_gauge(achievement_rate)
                    st.plotly_chart(fig, use_container_width=True)

            elif "渠道分布" in title:
                # 显示渠道分布饼图
                if 'analysis_result' in st.session_state:
                    channel_data = st.session_state['analysis_result'].get('channel_data', pd.DataFrame())
                    if not channel_data.empty:
                        fig = create_channel_pie_chart(channel_data, '销售渠道分布')
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
    if 'analysis_result' not in st.session_state:
        return "数据分析加载中..."

    analysis = st.session_state['analysis_result']

    if card_id == "total_sales":
        ytd_sales = analysis.get('ytd_sales', 0)
        achievement_rate = analysis.get('achievement_rate', 0)
        annual_target = analysis.get('annual_target', 0)

        if achievement_rate >= 100:
            return f"销售总额 {format_currency(ytd_sales)}，已超额完成年度目标 {format_currency(annual_target)}，表现优异。持续加强销售策略，有望创造更高业绩。"
        elif achievement_rate >= 80:
            return f"销售总额 {format_currency(ytd_sales)}，完成年度目标的 {format_percentage(achievement_rate)}，进展良好。距离目标 {format_currency(annual_target)} 还有一定差距，需保持稳定增长。"
        elif achievement_rate >= 60:
            return f"销售总额 {format_currency(ytd_sales)}，完成年度目标的 {format_percentage(achievement_rate)}，进展一般。距离目标 {format_currency(annual_target)} 还有较大差距，需加强销售活动。"
        else:
            return f"销售总额 {format_currency(ytd_sales)}，仅完成年度目标的 {format_percentage(achievement_rate)}，进展缓慢。需要紧急调整销售策略，以达成年度目标 {format_currency(annual_target)}。"

    elif card_id == "yoy_growth":
        yoy_growth = analysis.get('yoy_growth', 0)
        ytd_sales = analysis.get('ytd_sales', 0)
        last_ytd_sales = analysis.get('last_ytd_sales', 0)

        if yoy_growth > 20:
            return f"同比增长 {format_percentage(yoy_growth)}，表现非常强劲。相比去年同期 {format_currency(last_ytd_sales)}，今年销售额 {format_currency(ytd_sales)} 有显著提升。"
        elif yoy_growth > 0:
            return f"同比增长 {format_percentage(yoy_growth)}，保持正向增长。相比去年同期 {format_currency(last_ytd_sales)}，今年销售额 {format_currency(ytd_sales)} 有所提升。"
        elif yoy_growth > -10:
            return f"同比下降 {format_percentage(-yoy_growth)}，较去年略有下滑。相比去年同期 {format_currency(last_ytd_sales)}，今年销售额 {format_currency(ytd_sales)} 有小幅度降低。"
        else:
            return f"同比下降 {format_percentage(-yoy_growth)}，表现不佳。相比去年同期 {format_currency(last_ytd_sales)}，今年销售额 {format_currency(ytd_sales)} 有显著下降，需警惕销售趋势。"

    elif card_id == "achievement_rate":
        achievement_rate = analysis.get('achievement_rate', 0)
        annual_target = analysis.get('annual_target', 0)

        current_month = datetime.now().month
        expected_rate = (current_month / 12) * 100  # 简单线性目标

        if achievement_rate >= 100:
            return f"目标达成率 {format_percentage(achievement_rate)}，已超额完成年度目标 {format_currency(annual_target)}。表现优异，考虑调高未来目标。"
        elif achievement_rate >= expected_rate:
            return f"目标达成率 {format_percentage(achievement_rate)}，高于预期进度({format_percentage(expected_rate)})。年度目标 {format_currency(annual_target)} 有望提前完成。"
        elif achievement_rate >= expected_rate * 0.8:
            return f"目标达成率 {format_percentage(achievement_rate)}，略低于预期进度({format_percentage(expected_rate)})。需要加快销售节奏，确保完成年度目标 {format_currency(annual_target)}。"
        else:
            return f"目标达成率 {format_percentage(achievement_rate)}，显著低于预期进度({format_percentage(expected_rate)})。需要制定补救措施，否则年度目标 {format_currency(annual_target)} 难以达成。"

    elif card_id == "channel_distribution":
        mt_sales = analysis.get('mt_sales', 0)
        tt_sales = analysis.get('tt_sales', 0)
        total_sales = mt_sales + tt_sales

        mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
        tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0

        if mt_percentage > 70:
            return f"MT渠道占比 {format_percentage(mt_percentage)}，TT渠道占比 {format_percentage(tt_percentage)}。渠道分布严重偏向MT渠道，存在渠道依赖风险，建议加强TT渠道开发。"
        elif tt_percentage > 70:
            return f"MT渠道占比 {format_percentage(mt_percentage)}，TT渠道占比 {format_percentage(tt_percentage)}。渠道分布严重偏向TT渠道，存在渠道依赖风险，建议加强MT渠道维护。"
        elif abs(mt_percentage - tt_percentage) < 20:
            return f"MT渠道占比 {format_percentage(mt_percentage)}，TT渠道占比 {format_percentage(tt_percentage)}。渠道分布相对均衡，降低了渠道依赖风险，建议继续保持多渠道发展策略。"
        else:
            major_channel = "MT" if mt_percentage > tt_percentage else "TT"
            major_percentage = max(mt_percentage, tt_percentage)
            minor_percentage = min(mt_percentage, tt_percentage)
            return f"{major_channel}渠道占比 {format_percentage(major_percentage)}，是主要销售渠道。另一渠道占比 {format_percentage(minor_percentage)}，建议适当平衡渠道发展。"

    return "数据分析加载中..."


def generate_trend_analysis(card_id):
    """生成趋势分析HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>分析数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_sales":
        ytd_sales = analysis.get('ytd_sales', 0)
        monthly_sales = analysis.get('monthly_sales', pd.DataFrame())

        # 分析月度趋势
        if not monthly_sales.empty and len(monthly_sales) > 1:
            last_month = monthly_sales.iloc[-1]['求和项:金额（元）']
            prev_month = monthly_sales.iloc[-2]['求和项:金额（元）']

            mom_change = ((last_month - prev_month) / prev_month * 100) if prev_month > 0 else 0

            # 计算3个月环比平均增长率
            if len(monthly_sales) >= 4:
                growth_rates = []
                for i in range(len(monthly_sales) - 3, len(monthly_sales)):
                    if i > 0:
                        current = monthly_sales.iloc[i]['求和项:金额（元）']
                        previous = monthly_sales.iloc[i - 1]['求和项:金额（元）']
                        if previous > 0:
                            growth_rates.append((current - previous) / previous * 100)

                avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

                trend_text = f"<p>• 近三个月平均环比增长率：<span style='color:{COLORS['success'] if avg_growth > 0 else COLORS['danger']};'>{avg_growth:.1f}%</span></p>"
            else:
                trend_text = ""

            mom_color = COLORS['success'] if mom_change > 0 else COLORS['danger']

            return f"""
                <p>• 当前销售总额：{format_currency(ytd_sales)}</p>
                <p>• 最近月环比变化：<span style='color:{mom_color};'>{mom_change:.1f}%</span></p>
                {trend_text}
                <p>• 销售集中度：{analyze_monthly_distribution(monthly_sales)}</p>
                <p>• 销售趋势：{analyze_sales_trend(monthly_sales)}</p>
            """
        else:
            return f"""
                <p>• 当前销售总额：{format_currency(ytd_sales)}</p>
                <p>• 数据不足，无法分析月度趋势</p>
            """

    elif card_id == "yoy_growth":
        yoy_growth = analysis.get('yoy_growth', 0)
        ytd_sales = analysis.get('ytd_sales', 0)
        last_ytd_sales = analysis.get('last_ytd_sales', 0)

        return f"""
            <p>• 当前同比增长率：<span style='color:{COLORS['success'] if yoy_growth > 0 else COLORS['danger']};'>{yoy_growth:.1f}%</span></p>
            <p>• 今年销售总额：{format_currency(ytd_sales)}</p>
            <p>• 去年同期销售额：{format_currency(last_ytd_sales)}</p>
            <p>• 销售差额：{format_currency(ytd_sales - last_ytd_sales)}</p>
            <p>• 增长表现：{'优于行业平均水平' if yoy_growth > 10 else '符合行业平均水平' if yoy_growth > 0 else '低于行业平均水平'}</p>
        """

    elif card_id == "achievement_rate":
        achievement_rate = analysis.get('achievement_rate', 0)
        ytd_sales = analysis.get('ytd_sales', 0)
        annual_target = analysis.get('annual_target', 0)

        current_month = datetime.now().month
        expected_rate = (current_month / 12) * 100

        gap = annual_target - ytd_sales

        return f"""
            <p>• 目标达成率：<span style='color:{COLORS['success'] if achievement_rate >= expected_rate else COLORS['danger']};'>{achievement_rate:.1f}%</span></p>
            <p>• 年度目标：{format_currency(annual_target)}</p>
            <p>• 当前销售额：{format_currency(ytd_sales)}</p>
            <p>• 差距：{format_currency(abs(gap))} {'(已超额完成)' if gap < 0 else ''}</p>
            <p>• 达成进度：{'领先于时间进度' if achievement_rate > expected_rate else '落后于时间进度'} (当前应达到{expected_rate:.1f}%)</p>
        """

    elif card_id == "channel_distribution":
        mt_sales = analysis.get('mt_sales', 0)
        tt_sales = analysis.get('tt_sales', 0)
        total_sales = mt_sales + tt_sales

        mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
        tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0

        channel_balance = abs(mt_percentage - tt_percentage)

        return f"""
            <p>• MT渠道销售额：{format_currency(mt_sales)} ({format_percentage(mt_percentage)})</p>
            <p>• TT渠道销售额：{format_currency(tt_sales)} ({format_percentage(tt_percentage)})</p>
            <p>• 主导渠道：{'MT渠道' if mt_sales > tt_sales else 'TT渠道'}</p>
            <p>• 渠道平衡度：{'高度不平衡' if channel_balance > 50 else '中度不平衡' if channel_balance > 30 else '相对平衡'}</p>
            <p>• 渠道战略：{'需要加强弱势渠道' if channel_balance > 30 else '继续保持多渠道发展'}</p>
        """

    return "<p>分析数据加载中...</p>"


def analyze_monthly_distribution(monthly_data):
    """分析月度销售分布"""
    if monthly_data.empty or len(monthly_data) < 3:
        return "数据不足，无法分析"

    # 计算变异系数(标准差/均值)
    mean = monthly_data['求和项:金额（元）'].mean()
    std = monthly_data['求和项:金额（元）'].std()
    cv = std / mean if mean > 0 else 0

    if cv < 0.1:
        return "销售非常稳定，月度波动很小"
    elif cv < 0.2:
        return "销售较为稳定，月度波动适中"
    elif cv < 0.3:
        return "销售波动明显，存在一定季节性"
    else:
        return "销售波动较大，季节性特征显著"


def analyze_sales_trend(monthly_data):
    """分析销售趋势"""
    if monthly_data.empty or len(monthly_data) < 3:
        return "数据不足，无法分析"

    # 简单趋势分析
    sales = monthly_data['求和项:金额（元）'].tolist()
    n = len(sales)

    # 计算最近三个月的趋势
    recent = sales[-3:] if n >= 3 else sales

    if all(recent[i] > recent[i - 1] for i in range(1, len(recent))):
        return "持续上升趋势，销售表现强劲"
    elif all(recent[i] < recent[i - 1] for i in range(1, len(recent))):
        return "持续下降趋势，需要警惕销售下滑"

    # 计算整体趋势（简单线性回归）
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(sales) / n

    numerator = sum((x[i] - mean_x) * (sales[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0

    if slope > 0.05 * mean_y:
        return "总体呈现上升趋势，但存在波动"
    elif slope < -0.05 * mean_y:
        return "总体呈现下降趋势，但存在波动"
    else:
        return "总体趋势平稳，波动在正常范围内"


def generate_optimization_advice(card_id):
    """生成优化建议HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>建议数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_sales":
        ytd_sales = analysis.get('ytd_sales', 0)
        achievement_rate = analysis.get('achievement_rate', 0)

        if achievement_rate >= 100:
            return """
                <p>• 保持当前销售策略，继续扩大市场份额</p>
                <p>• 考虑提高销售目标，激励团队创造更好业绩</p>
                <p>• 关注高毛利产品，提升整体盈利能力</p>
                <p>• 加强客户关系管理，提高客户忠诚度</p>
            """
        elif achievement_rate >= 80:
            return """
                <p>• 分析高绩效区域和渠道，复制成功经验</p>
                <p>• 加强团队激励，冲刺年度销售目标</p>
                <p>• 聚焦核心客户，提高单客户销售额</p>
                <p>• 优化产品组合，提升销售效率</p>
            """
        elif achievement_rate >= 60:
            return """
                <p>• 重点关注销售表现较弱的区域和渠道</p>
                <p>• 加强促销活动，刺激短期销售增长</p>
                <p>• 强化销售团队培训，提高销售技能</p>
                <p>• 优化库存和物流，确保产品供应</p>
            """
        else:
            return """
                <p>• 紧急评估销售策略，找出表现不佳原因</p>
                <p>• 制定专项行动计划，加速销售增长</p>
                <p>• 考虑调整产品定价策略，提高市场竞争力</p>
                <p>• 加强与大客户的沟通，争取大单支持</p>
            """

    elif card_id == "yoy_growth":
        yoy_growth = analysis.get('yoy_growth', 0)

        if yoy_growth > 20:
            return """
                <p>• 深入分析高增长驱动因素，巩固优势</p>
                <p>• 考虑适度扩大产能，满足增长需求</p>
                <p>• 加强市场预测，提前规划资源配置</p>
                <p>• 关注可持续性，避免短期增长透支未来</p>
            """
        elif yoy_growth > 0:
            return """
                <p>• 分析增长点，加大资源投入</p>
                <p>• 关注低增长或负增长的产品线</p>
                <p>• 加强市场竞争分析，找出差距</p>
                <p>• 优化营销策略，提高市场反应速度</p>
            """
        elif yoy_growth > -10:
            return """
                <p>• 分析下滑原因，制定针对性措施</p>
                <p>• 加强市场调研，了解客户需求变化</p>
                <p>• 优化产品结构，淘汰低效产品</p>
                <p>• 强化销售团队激励，提高销售积极性</p>
            """
        else:
            return """
                <p>• 紧急分析严重下滑原因，可能涉及市场、产品或渠道问题</p>
                <p>• 考虑产品创新或升级，提高竞争力</p>
                <p>• 重新评估目标客户群体，调整市场定位</p>
                <p>• 加强内部管理，降低运营成本</p>
            """

    elif card_id == "achievement_rate":
        achievement_rate = analysis.get('achievement_rate', 0)
        current_month = datetime.now().month
        expected_rate = (current_month / 12) * 100

        if achievement_rate >= expected_rate * 1.1:
            return """
                <p>• 考虑提高年度目标，保持团队动力</p>
                <p>• 分析超额完成原因，形成最佳实践</p>
                <p>• 关注团队可持续发展，避免倦怠</p>
                <p>• 加强长期客户关系建设，确保未来业绩</p>
            """
        elif achievement_rate >= expected_rate:
            return """
                <p>• 保持当前节奏，确保目标达成</p>
                <p>• 加强数据分析，把握市场机会</p>
                <p>• 优化资源配置，提高销售效率</p>
                <p>• 加强团队建设，培养核心骨干</p>
            """
        elif achievement_rate >= expected_rate * 0.8:
            return """
                <p>• 评估销售漏斗，找出转化率低的环节</p>
                <p>• 加强短期促销活动，提升销售业绩</p>
                <p>• 强化客户管理，提高成交率</p>
                <p>• 重点关注高潜力区域和产品</p>
            """
        else:
            return """
                <p>• 重新评估年度目标的合理性</p>
                <p>• 制定销售追赶计划，明确责任分工</p>
                <p>• 加强销售监控，建立预警机制</p>
                <p>• 考虑调整销售策略或产品定位</p>
            """

    elif card_id == "channel_distribution":
        mt_sales = analysis.get('mt_sales', 0)
        tt_sales = analysis.get('tt_sales', 0)

        if mt_sales > tt_sales * 3:
            return """
                <p>• 加强TT渠道建设，降低对MT渠道依赖</p>
                <p>• 开发TT渠道专属产品，提升竞争力</p>
                <p>• 优化TT渠道激励政策，吸引更多客户</p>
                <p>• 加强TT渠道培训和支持</p>
            """
        elif tt_sales > mt_sales * 3:
            return """
                <p>• 加强MT渠道维护，确保核心产品覆盖</p>
                <p>• 优化MT渠道产品结构，提升单店销量</p>
                <p>• 加强与大型MT客户战略合作</p>
                <p>• 提升MT渠道产品陈列质量</p>
            """
        else:
            return """
                <p>• 持续优化双渠道策略，扬长避短</p>
                <p>• 差异化产品定位，满足不同渠道需求</p>
                <p>• 建立健全渠道考核体系，促进良性竞争</p>
                <p>• 加强跨渠道协同，提高整体效率</p>
            """

    return "<p>建议数据加载中...</p>"


def generate_action_plan(card_id):
    """生成行动方案HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>行动计划加载中...</p>"

    if card_id == "total_sales":
        return """
            <p><strong>近期行动（1个月）：</strong>分析当前销售数据，找出增长点和问题点，制定针对性计划</p>
            <p><strong>中期行动（3个月）：</strong>优化产品组合和渠道策略，提高销售效率</p>
            <p><strong>长期行动（6个月）：</strong>加强团队建设和客户关系管理，确保销售增长可持续性</p>
        """

    elif card_id == "yoy_growth":
        return """
            <p><strong>近期行动（1个月）：</strong>对比竞争对手增长数据，分析差距，找出改进点</p>
            <p><strong>中期行动（3个月）：</strong>调整产品结构和营销策略，优化增长曲线</p>
            <p><strong>长期行动（6个月）：</strong>建立增长预测模型，提前应对市场变化</p>
        """

    elif card_id == "achievement_rate":
        return """
            <p><strong>近期行动（1个月）：</strong>对标进度，调整月度销售计划，确保目标达成节奏</p>
            <p><strong>中期行动（3个月）：</strong>评估年度目标完成情况，必要时调整策略和资源分配</p>
            <p><strong>长期行动（6个月）：</strong>优化目标设定和考核机制，提高目标管理有效性</p>
        """

    elif card_id == "channel_distribution":
        return """
            <p><strong>近期行动（1个月）：</strong>分析各渠道客户特点和购买行为，优化渠道策略</p>
            <p><strong>中期行动（3个月）：</strong>加强薄弱渠道建设，平衡渠道发展</p>
            <p><strong>长期行动（6个月）：</strong>构建全渠道营销体系，提升整体市场覆盖和竞争力</p>
        """

    return "<p>行动计划加载中...</p>"


# ==================== 6. 主页面函数 ====================
def show_sales_analysis():
    """显示销售分析页面"""
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
    st.title("📈 销售分析")

    # 加载数据
    with st.spinner("正在加载销售数据..."):
        sales_data, sales_target, tt_target = load_sales_data()

    if sales_data.empty:
        st.error("无法加载销售数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_data = apply_sales_filters(sales_data)

    # 分析数据
    analysis_result = analyze_sales_data(filtered_data, sales_target, tt_target)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("没有符合筛选条件的数据")
        return

    # 显示关键指标卡片
    st.subheader("📊 销售概览")

    col1, col2 = st.columns(2)

    with col1:
        create_sales_flip_card(
            "total_sales",
            "销售总额",
            analysis_result['ytd_sales'],
            "年初至今总销售额",
            is_currency=True
        )

    with col2:
        create_sales_flip_card(
            "yoy_growth",
            "同比增长率",
            analysis_result['yoy_growth'],
            "与去年同期比较",
            is_percentage=True
        )

    col3, col4 = st.columns(2)

    with col3:
        create_sales_flip_card(
            "achievement_rate",
            "目标达成率",
            analysis_result['achievement_rate'],
            f"年度目标: {format_currency(analysis_result['annual_target'])}",
            is_percentage=True
        )

    with col4:
        create_sales_flip_card(
            "channel_distribution",
            "渠道分布",
            f"MT: {analysis_result['mt_sales'] / analysis_result['ytd_sales'] * 100:.1f}% / TT: {analysis_result['tt_sales'] / analysis_result['ytd_sales'] * 100:.1f}%" if
            analysis_result['ytd_sales'] > 0 else "暂无数据",
            "销售渠道占比分析"
        )

    # 销售趋势分析
    st.subheader("📈 销售趋势分析")

    col1, col2 = st.columns(2)

    with col1:
        # 月度销售趋势
        monthly_data = analysis_result.get('monthly_sales', pd.DataFrame())
        if not monthly_data.empty:
            fig = create_sales_trend_chart(monthly_data, '月份', '求和项:金额（元）', '月度销售趋势')
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>月度销售趋势{analyze_sales_trend(monthly_data)}。{analyze_monthly_distribution(monthly_data)}。</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # 季度销售趋势
        quarterly_data = analysis_result.get('quarterly_sales', pd.DataFrame())
        if not quarterly_data.empty:
            fig = create_sales_bar_chart(quarterly_data, '季度', '求和项:金额（元）', '季度销售分布')
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            current_quarter = (datetime.now().month - 1) // 3 + 1
            q_data = quarterly_data[quarterly_data['季度'] == current_quarter]
            q_sales = q_data['求和项:金额（元）'].iloc[0] if not q_data.empty else 0

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>当前第{current_quarter}季度销售额为{format_currency(q_sales)}。季度销售分布显示{analyze_quarterly_distribution(quarterly_data)}。</p>
            </div>
            """, unsafe_allow_html=True)

    # 渠道分析
    st.subheader("🔄 销售渠道分析")

    # 渠道数据
    channel_data = analysis_result.get('channel_data', pd.DataFrame())
    if not channel_data.empty:
        # 渠道占比饼图
        fig = create_channel_pie_chart(channel_data, '销售渠道占比')
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>📊 图表解读</h4>
            <p>MT渠道贡献{format_currency(analysis_result['mt_sales'])}销售额，占比{format_percentage(channel_data.loc[channel_data['渠道'] == 'MT', '占比'].iloc[0] if 'MT' in channel_data['渠道'].values else 0)}。
            TT渠道贡献{format_currency(analysis_result['tt_sales'])}销售额，占比{format_percentage(channel_data.loc[channel_data['渠道'] == 'TT', '占比'].iloc[0] if 'TT' in channel_data['渠道'].values else 0)}。
            {'MT渠道是主要销售渠道' if analysis_result['mt_sales'] > analysis_result['tt_sales'] else 'TT渠道是主要销售渠道'}。</p>
        </div>
        """, unsafe_allow_html=True)

    # TT产品达成情况
    tt_achievement = analysis_result.get('tt_achievement', {})
    if tt_achievement:
        st.subheader("🎯 TT产品目标达成情况")

        col1, col2 = st.columns(2)

        with col1:
            c60_achievement = tt_achievement.get('C60达成率', 0)
            fig = create_achievement_gauge(c60_achievement, "C60城市达成率")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            non_c60_achievement = tt_achievement.get('非C60达成率', 0)
            fig = create_achievement_gauge(non_c60_achievement, "非C60城市达成率")
            st.plotly_chart(fig, use_container_width=True)

        # TT产品解读
        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>📊 TT产品分析</h4>
            <p><strong>C60城市：</strong> 目标{format_currency(tt_achievement.get('C60目标总额', 0))}，已完成{format_currency(tt_achievement.get('C60销售总额', 0))}，
            达成率{format_percentage(tt_achievement.get('C60达成率', 0))}，{get_achievement_comment(tt_achievement.get('C60达成率', 0))}</p>
            <p><strong>非C60城市：</strong> 目标{format_currency(tt_achievement.get('非C60目标总额', 0))}，已完成{format_currency(tt_achievement.get('非C60销售总额', 0))}，
            达成率{format_percentage(tt_achievement.get('非C60达成率', 0))}，{get_achievement_comment(tt_achievement.get('非C60达成率', 0))}</p>
        </div>
        """, unsafe_allow_html=True)

    # 销售人员分析
    salesperson_data = analysis_result.get('salesperson_sales', pd.DataFrame())
    if not salesperson_data.empty:
        st.subheader("👨‍💼 销售人员分析")

        fig = create_salesperson_chart(salesperson_data, 'TOP10销售人员业绩')
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_salesperson = salesperson_data.iloc[0]['申请人'] if not salesperson_data.empty else ""
        top_sales = salesperson_data.iloc[0]['求和项:金额（元）'] if not salesperson_data.empty else 0

        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4>📊 图表解读</h4>
            <p>TOP1销售人员{top_salesperson}贡献{format_currency(top_sales)}销售额，表现优异。
            销售团队整体表现{analyze_team_distribution(salesperson_data)}。</p>
        </div>
        """, unsafe_allow_html=True)

    # 销售洞察总结
    st.subheader("💡 销售洞察总结")

    achievement_rate = analysis_result.get('achievement_rate', 0)
    yoy_growth = analysis_result.get('yoy_growth', 0)

    # 生成综合洞察
    if achievement_rate >= 100 and yoy_growth > 0:
        performance = "优异"
        performance_color = COLORS['success']
        comment = "销售业绩表现强势，同比增长，达成率高，建议保持现有策略并扩大优势"
    elif achievement_rate >= 80 and yoy_growth > 0:
        performance = "良好"
        performance_color = COLORS['success']
        comment = "销售业绩良好，同比有增长，达成率接近目标，需继续保持增长势头"
    elif achievement_rate >= 60 or yoy_growth > 0:
        performance = "一般"
        performance_color = COLORS['warning']
        comment = "销售业绩一般，目标达成或同比增长有所欠缺，需加强销售策略"
    else:
        performance = "欠佳"
        performance_color = COLORS['danger']
        comment = "销售业绩欠佳，同比下降且目标达成率低，需重点关注并采取补救措施"

    st.markdown(f"""
    <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0.5rem;">
        <h4>📋 销售表现总结</h4>
        <p><strong>整体表现：</strong><span style="color: {performance_color};">{performance}</span></p>
        <p><strong>目标达成情况：</strong>年初至今达成率 {format_percentage(achievement_rate)}，{get_achievement_comment(achievement_rate)}</p>
        <p><strong>同比增长情况：</strong>同比{format_percentage(yoy_growth)} {'增长' if yoy_growth >= 0 else '下降'}</p>
        <p><strong>渠道表现：</strong>{'MT渠道占主导' if analysis_result['mt_sales'] > analysis_result['tt_sales'] else 'TT渠道占主导'}，渠道分布{analyze_channel_distribution(analysis_result)}</p>
        <p><strong>综合评价：</strong>{comment}</p>
    </div>
    """, unsafe_allow_html=True)


def analyze_quarterly_distribution(quarterly_data):
    """分析季度销售分布"""
    if quarterly_data.empty or len(quarterly_data) < 2:
        return "数据不足，无法分析"

    sales = quarterly_data['求和项:金额（元）'].tolist()

    max_quarter = quarterly_data.loc[quarterly_data['求和项:金额（元）'].idxmax(), '季度']
    min_quarter = quarterly_data.loc[quarterly_data['求和项:金额（元）'].idxmin(), '季度']

    # 计算变异系数
    mean = sum(sales) / len(sales)
    variance = sum((x - mean) ** 2 for x in sales) / len(sales)
    std = variance ** 0.5
    cv = std / mean if mean > 0 else 0

    if cv < 0.1:
        return f"季度销售非常平均，显示业务稳定性强"
    elif cv < 0.2:
        return f"季度间有一定差异，第{max_quarter}季度表现最佳，第{min_quarter}季度相对较弱"
    else:
        return f"季度销售存在显著差异，表现出明显的季节性，第{max_quarter}季度是销售旺季，第{min_quarter}季度是销售淡季"


def analyze_team_distribution(salesperson_data):
    """分析销售团队分布"""
    if salesperson_data.empty or len(salesperson_data) < 3:
        return "数据不足，无法分析"

    # 计算前20%销售员的销售占比（帕累托原则）
    total_sales = salesperson_data['求和项:金额（元）'].sum()
    top_count = max(1, round(len(salesperson_data) * 0.2))
    top_sales = salesperson_data.head(top_count)['求和项:金额（元）'].sum()
    top_percentage = top_sales / total_sales * 100 if total_sales > 0 else 0

    if top_percentage > 80:
        return f"高度依赖核心销售人员，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，存在团队结构风险"
    elif top_percentage > 60:
        return f"较为依赖核心销售人员，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，团队结构有待优化"
    else:
        return f"团队结构相对均衡，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，团队整体实力较强"


def analyze_channel_distribution(analysis):
    """分析渠道分布情况"""
    mt_sales = analysis.get('mt_sales', 0)
    tt_sales = analysis.get('tt_sales', 0)
    total_sales = mt_sales + tt_sales

    if total_sales == 0:
        return "数据不足，无法分析"

    mt_percentage = mt_sales / total_sales * 100
    tt_percentage = tt_sales / total_sales * 100

    balance = abs(mt_percentage - tt_percentage)

    if balance < 20:
        return "较为均衡，双渠道发展良好"
    elif balance < 40:
        return "存在一定偏向性，但整体可接受"
    elif balance < 60:
        return "明显不均衡，存在渠道依赖风险"
    else:
        return "高度不均衡，严重依赖单一渠道，建议加强弱势渠道建设"


def get_achievement_comment(rate):
    """根据达成率生成评价文本"""
    if rate >= 100:
        return "已超额完成目标"
    elif rate >= 90:
        return "接近完成目标，进展良好"
    elif rate >= 80:
        return "略有差距，但基本符合预期"
    elif rate >= 60:
        return "有较大差距，需加强销售力度"
    else:
        return "差距显著，需要重点关注"


if __name__ == "__main__":
    show_sales_analysis()