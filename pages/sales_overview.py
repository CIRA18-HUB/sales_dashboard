# pages/sales_overview.py - 完全自包含的销售总览页面(合并overview+sales)
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
st.title("📈 销售总览")

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
def analyze_monthly_distribution(monthly_data):
    """分析月度销售分布"""
    if monthly_data.empty or len(monthly_data) < 3:
        return "数据不足，无法分析"

    # 计算变异系数(标准差/均值)
    mean = monthly_data['销售额'].mean()
    std = monthly_data['销售额'].std()
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
    sales = monthly_data['销售额'].tolist()
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


def analyze_quarterly_distribution(quarterly_data):
    """分析季度销售分布"""
    if quarterly_data.empty or len(quarterly_data) < 2:
        return "数据不足，无法分析"

    sales = quarterly_data['销售额'].tolist()

    max_quarter = quarterly_data.loc[quarterly_data['销售额'].idxmax(), '季度']
    min_quarter = quarterly_data.loc[quarterly_data['销售额'].idxmin(), '季度']

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


def analyze_channel_distribution(mt_percentage, tt_percentage):
    """分析渠道分布情况"""
    balance = abs(mt_percentage - tt_percentage)

    if balance < 20:
        return "较为均衡，双渠道发展良好"
    elif balance < 40:
        return "存在一定偏向性，但整体可接受"
    elif balance < 60:
        return "明显不均衡，存在渠道依赖风险"
    else:
        return "高度不均衡，严重依赖单一渠道，建议加强弱势渠道建设"


def analyze_team_distribution(salesperson_data):
    """分析销售团队分布"""
    if salesperson_data.empty or len(salesperson_data) < 3:
        return "数据不足，无法分析"

    # 计算前20%销售员的销售占比（帕累托原则）
    total_sales = salesperson_data['销售额'].sum()
    top_count = max(1, round(len(salesperson_data) * 0.2))
    top_sales = salesperson_data.head(top_count)['销售额'].sum()
    top_percentage = top_sales / total_sales * 100 if total_sales > 0 else 0

    if top_percentage > 80:
        return f"高度依赖核心销售人员，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，存在团队结构风险"
    elif top_percentage > 60:
        return f"较为依赖核心销售人员，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，团队结构有待优化"
    else:
        return f"团队结构相对均衡，前{top_count}名销售贡献了{top_percentage:.1f}%的业绩，团队整体实力较强"


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


# ==================== 分析数据 ====================
def analyze_sales_overview(filtered_data):
    """分析销售总览数据"""
    sales_data = filtered_data.get('sales_orders', pd.DataFrame())
    sales_target = filtered_data.get('sales_target', pd.DataFrame())
    tt_target = filtered_data.get('tt_target', pd.DataFrame())

    if sales_data.empty:
        return {}

    # 获取当前年份和月份
    current_year = datetime.now().year
    current_month = datetime.now().month
    previous_year = current_year - 1

    # 年初至今销售数据
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]
    ytd_sales_amount = ytd_sales['销售额'].sum()

    # 上年度同期销售数据
    last_ytd_sales = sales_data[
        (pd.to_datetime(sales_data['发运月份']).dt.year == previous_year) &
        (pd.to_datetime(sales_data['发运月份']).dt.month <= current_month)
        ]
    last_ytd_sales_amount = last_ytd_sales['销售额'].sum()

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
    channel_data = ytd_sales.groupby('渠道')['销售额'].sum().reset_index()
    if not channel_data.empty:
        channel_data['占比'] = channel_data['销售额'] / ytd_sales_amount * 100 if ytd_sales_amount > 0 else 0

    # MT和TT渠道销售额
    mt_sales = channel_data.loc[channel_data['渠道'] == 'MT', '销售额'].sum() if 'MT' in channel_data[
        '渠道'].values else 0
    tt_sales = channel_data.loc[channel_data['渠道'] == 'TT', '销售额'].sum() if 'TT' in channel_data[
        '渠道'].values else 0

    # 计算渠道占比
    mt_percentage = (mt_sales / ytd_sales_amount * 100) if ytd_sales_amount > 0 else 0
    tt_percentage = (tt_sales / ytd_sales_amount * 100) if ytd_sales_amount > 0 else 0

    # 月度销售趋势
    ytd_sales['月份'] = pd.to_datetime(ytd_sales['发运月份']).dt.month
    monthly_sales = ytd_sales.groupby('月份')['销售额'].sum().reset_index()

    # 季度销售趋势
    ytd_sales['季度'] = (pd.to_datetime(ytd_sales['发运月份']).dt.month - 1) // 3 + 1
    quarterly_sales = ytd_sales.groupby('季度')['销售额'].sum().reset_index()

    # 销售人员分析
    if '申请人' in ytd_sales.columns:
        salesperson_sales = ytd_sales.groupby('申请人')['销售额'].sum().reset_index()
        salesperson_sales = salesperson_sales.sort_values('销售额', ascending=False)
    else:
        salesperson_sales = pd.DataFrame()

    # TT产品达成率分析
    tt_achievement = {}
    if not tt_target.empty and 'TT' in sales_data['渠道'].values:
        tt_sales_data = sales_data[sales_data['渠道'] == 'TT']

        # 合并TT销售和目标数据
        if not tt_sales_data.empty and '城市' in tt_target.columns:
            tt_current_year = tt_target[pd.to_datetime(tt_target['指标年月']).dt.year == current_year]
            if not tt_current_year.empty:
                # 如果TT销售数据中没有城市信息，尝试从销售数据中获取城市信息
                if '城市' not in tt_sales_data.columns and '所属区域' in tt_sales_data.columns:
                    # 这里假设区域对应城市，实际应根据真实数据结构调整
                    tt_sales_by_region = tt_sales_data.groupby('所属区域')['销售额'].sum().reset_index()
                    tt_sales_by_region.columns = ['城市', '销售额']

                    # 城市类型映射
                    c60_cities = tt_current_year[tt_current_year['城市类型'] == 'C60']['城市'].unique()

                    # 计算C60城市销售额
                    c60_sales = tt_sales_by_region[tt_sales_by_region['城市'].isin(c60_cities)]
                    non_c60_sales = tt_sales_by_region[~tt_sales_by_region['城市'].isin(c60_cities)]

                    tt_achievement['C60目标总额'] = tt_current_year[tt_current_year['城市类型'] == 'C60'][
                        '月度指标'].sum()
                    tt_achievement['C60销售总额'] = c60_sales['销售额'].sum()
                    tt_achievement['C60达成率'] = tt_achievement['C60销售总额'] / tt_achievement['C60目标总额'] * 100 if \
                    tt_achievement['C60目标总额'] > 0 else 0

                    tt_achievement['非C60目标总额'] = tt_current_year[tt_current_year['城市类型'] != 'C60'][
                        '月度指标'].sum()
                    tt_achievement['非C60销售总额'] = non_c60_sales['销售额'].sum()
                    tt_achievement['非C60达成率'] = tt_achievement['非C60销售总额'] / tt_achievement[
                        '非C60目标总额'] * 100 if tt_achievement['非C60目标总额'] > 0 else 0

    # 产品BCG分析
    product_codes = filtered_data.get('product_codes', [])
    if product_codes:
        # 过滤需要分析的产品
        bcg_data = ytd_sales[ytd_sales['产品代码'].isin(product_codes)].copy()

        # 计算每个产品的销售额和占比
        product_sales = bcg_data.groupby(['产品代码', '产品简称'])['销售额'].sum().reset_index()
        product_sales['销售占比'] = product_sales['销售额'] / product_sales['销售额'].sum() * 100 if product_sales[
                                                                                                         '销售额'].sum() > 0 else 0

        # 计算去年同期数据
        last_year_product_sales = last_ytd_sales.groupby(['产品代码'])['销售额'].sum().reset_index()
        last_year_product_sales.rename(columns={'销售额': '去年销售额'}, inplace=True)

        # 合并今年和去年的销售数据
        product_sales = product_sales.merge(last_year_product_sales, on='产品代码', how='left')
        product_sales['去年销售额'] = product_sales['去年销售额'].fillna(0)

        # 计算增长率
        product_sales['增长率'] = (product_sales['销售额'] - product_sales['去年销售额']) / product_sales[
            '去年销售额'] * 100
        product_sales['增长率'] = product_sales['增长率'].fillna(0)
        product_sales.loc[product_sales['去年销售额'] == 0, '增长率'] = 100  # 去年为0，今年有销售的，增长率设为100%

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
        dog_percent = bcg_summary.loc[bcg_summary['BCG分类'] == '瘦狗产品', '销售占比'].sum() if '瘦狗产品' in \
                                                                                                 bcg_summary[
                                                                                                     'BCG分类'].values else 0

        # 判断是否符合健康产品组合
        is_healthy_mix = (
                (45 <= cash_cow_percent <= 50) and
                (40 <= star_question_percent <= 45) and
                (dog_percent <= 10)
        )
    else:
        product_sales = pd.DataFrame()
        bcg_summary = pd.DataFrame()
        is_healthy_mix = False
        cash_cow_percent = 0
        star_question_percent = 0
        dog_percent = 0

    return {
        'ytd_sales': ytd_sales_amount,
        'last_ytd_sales': last_ytd_sales_amount,
        'yoy_growth': yoy_growth,
        'annual_target': annual_target,
        'achievement_rate': achievement_rate,
        'channel_data': channel_data,
        'mt_sales': mt_sales,
        'tt_sales': tt_sales,
        'mt_percentage': mt_percentage,
        'tt_percentage': tt_percentage,
        'monthly_sales': monthly_sales,
        'quarterly_sales': quarterly_sales,
        'salesperson_sales': salesperson_sales,
        'tt_achievement': tt_achievement,
        'product_sales': product_sales,
        'bcg_summary': bcg_summary,
        'is_healthy_mix': is_healthy_mix,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent
    }


# ==================== 图表创建函数 ====================
def create_sales_trend_chart(data, title="月度销售趋势"):
    """创建销售趋势图"""
    if data.empty:
        return None

    fig = px.line(
        data,
        x='月份',
        y='销售额',
        title=title,
        markers=True,
        color_discrete_sequence=[COLORS['primary']]
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        texttemplate='%{y:,.0f}',
        textposition='top center'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="月份",
        yaxis_title="销售额（元）",
        hovermode="x unified"
    )

    return fig


def create_channel_pie_chart(data, title="渠道销售占比"):
    """创建渠道占比饼图"""
    if data.empty:
        return None

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


def create_sales_bar_chart(data, x_col, y_col, title, color_col=None):
    """创建销售柱状图表"""
    if data.empty:
        return None

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


def create_quarterly_bar_chart(data, title="季度销售分布"):
    """创建季度销售柱状图"""
    if data.empty:
        return None

    fig = px.bar(
        data,
        x='季度',
        y='销售额',
        title=title,
        color_discrete_sequence=[COLORS['primary']]
    )

    # 格式化Y轴标签
    y_values = data['销售额'].tolist()
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
        x='销售额',
        y='申请人',
        orientation='h',
        title=title,
        color='销售额',
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


# ==================== 主页面 ====================
# 分析数据
analysis_result = analyze_sales_overview(filtered_data)

# 创建标签页
tabs = st.tabs(["📊 销售概览", "🎯 目标达成", "🔄 渠道分析", "👨‍💼 销售人员", "🔵 BCG产品矩阵"])

with tabs[0]:  # 销售概览
    # KPI指标行
    st.subheader("🔑 关键绩效指标")
    col1, col2, col3, col4 = st.columns(4)

    # 总销售额
    total_sales = analysis_result.get('ytd_sales', 0)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总销售额</p>
            <p class="card-value">{format_currency(total_sales)}</p>
            <p class="card-text">年初至今销售收入</p>
        </div>
        """, unsafe_allow_html=True)

    # 同比增长率
    yoy_growth = analysis_result.get('yoy_growth', 0)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">同比增长率</p>
            <p class="card-value" style="color: {'#4CAF50' if yoy_growth >= 0 else '#F44336'};">{format_percentage(yoy_growth)}</p>
            <p class="card-text">与去年同期比较</p>
        </div>
        """, unsafe_allow_html=True)

    # 目标达成率
    achievement_rate = analysis_result.get('achievement_rate', 0)
    annual_target = analysis_result.get('annual_target', 0)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">目标达成率</p>
            <p class="card-value" style="color: {'#4CAF50' if achievement_rate >= 80 else '#FF9800' if achievement_rate >= 60 else '#F44336'};">{format_percentage(achievement_rate)}</p>
            <p class="card-text">年度目标: {format_currency(annual_target)}</p>
        </div>
        """, unsafe_allow_html=True)

    # 渠道分布
    mt_percentage = analysis_result.get('mt_percentage', 0)
    tt_percentage = analysis_result.get('tt_percentage', 0)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">渠道分布</p>
            <p class="card-value">MT: {format_percentage(mt_percentage)} / TT: {format_percentage(tt_percentage)}</p>
            <p class="card-text">销售渠道占比</p>
        </div>
        """, unsafe_allow_html=True)

    # 销售趋势分析
    st.markdown('<div class="sub-header">📈 销售趋势分析</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        # 月度销售趋势
        monthly_data = analysis_result.get('monthly_sales', pd.DataFrame())
        if not monthly_data.empty:
            fig = create_sales_trend_chart(monthly_data, "月度销售趋势")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> 月度销售趋势{analyze_sales_trend(monthly_data)}。{analyze_monthly_distribution(monthly_data)}。
            </div>
            """, unsafe_allow_html=True)

    with cols[1]:
        # 季度销售趋势
        quarterly_data = analysis_result.get('quarterly_sales', pd.DataFrame())
        if not quarterly_data.empty:
            fig = create_quarterly_bar_chart(quarterly_data, "季度销售分布")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            current_quarter = (datetime.now().month - 1) // 3 + 1
            q_data = quarterly_data[quarterly_data['季度'] == current_quarter]
            q_sales = q_data['销售额'].iloc[0] if not q_data.empty else 0

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> 当前第{current_quarter}季度销售额为{format_currency(q_sales)}。季度销售分布显示{analyze_quarterly_distribution(quarterly_data)}。
            </div>
            """, unsafe_allow_html=True)

    # 销售同比分析
    st.markdown('<div class="sub-header">📊 销售同比分析</div>', unsafe_allow_html=True)

    # 创建同比数据
    current_year = datetime.now().year
    previous_year = current_year - 1
    compare_data = pd.DataFrame({
        '年份': [str(previous_year), str(current_year)],
        '销售额': [analysis_result.get('last_ytd_sales', 0), analysis_result.get('ytd_sales', 0)]
    })

    fig = create_sales_bar_chart(compare_data, '年份', '销售额', '同比销售对比')
    st.plotly_chart(fig, use_container_width=True)

    # 图表解读
    last_ytd_sales = analysis_result.get('last_ytd_sales', 0)
    ytd_sales = analysis_result.get('ytd_sales', 0)

    if yoy_growth > 0:
        growth_comment = f"同比增长{format_percentage(yoy_growth)}，增长势头良好。分析主要增长来源，继续复制成功经验。"
    else:
        growth_comment = f"同比下降{format_percentage(-yoy_growth)}，需要重点关注。分析下滑原因，制定针对性措施。"

    st.markdown(f"""
    <div class="chart-explanation">
        <b>图表解读：</b> 今年销售额{format_currency(ytd_sales)}，去年同期销售额{format_currency(last_ytd_sales)}。{growth_comment}
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:  # 目标达成
    st.subheader("🎯 销售目标达成情况")

    # 目标达成率仪表盘
    col1, col2 = st.columns(2)

    with col1:
        fig = create_achievement_gauge(achievement_rate, "年度目标达成率")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        achievement_comment = get_achievement_comment(achievement_rate)
        current_month = datetime.now().month
        expected_rate = (current_month / 12) * 100  # 简单线性目标

        if achievement_rate >= expected_rate:
            progress_comment = f"目前进度超前，高于预期进度({format_percentage(expected_rate)})。"
        else:
            progress_comment = f"目前进度滞后，低于预期进度({format_percentage(expected_rate)})。"

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 当前目标达成率为{format_percentage(achievement_rate)}，{achievement_comment}。年度销售目标{format_currency(annual_target)}，已完成{format_currency(total_sales)}。{progress_comment}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # TT产品达成情况
        tt_achievement = analysis_result.get('tt_achievement', {})
        if tt_achievement:
            c60_achievement = tt_achievement.get('C60达成率', 0)
            non_c60_achievement = tt_achievement.get('非C60达成率', 0)

            # 创建TT产品目标达成率数据
            tt_achievement_data = pd.DataFrame({
                '城市类型': ['C60城市', '非C60城市'],
                '达成率': [c60_achievement, non_c60_achievement]
            })

            fig = px.bar(
                tt_achievement_data,
                x='城市类型',
                y='达成率',
                title="TT产品目标达成率",
                color='城市类型',
                text='达成率'
            )

            fig.update_traces(
                texttemplate='%{y:.1f}%',
                textposition='outside'
            )

            fig.update_layout(
                height=350,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="城市类型",
                yaxis_title="达成率 (%)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> C60城市达成率{format_percentage(c60_achievement)}，{get_achievement_comment(c60_achievement)}。非C60城市达成率{format_percentage(non_c60_achievement)}，{get_achievement_comment(non_c60_achievement)}。
                {'C60城市表现更好，继续保持优势。' if c60_achievement > non_c60_achievement else '非C60城市表现更好，可复制经验到C60城市。'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无TT产品目标数据")

    # 目标达成分析
    st.markdown('<div class="sub-header">📊 目标达成分析</div>', unsafe_allow_html=True)

    # 创建目标缺口分析
    gap = annual_target - total_sales
    gap_percentage = (gap / annual_target * 100) if annual_target > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        # 目标缺口指标卡
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">目标缺口</p>
            <p class="card-value" style="color: {'#4CAF50' if gap <= 0 else '#F44336'};">{format_currency(abs(gap))}</p>
            <p class="card-text">{'已超额完成' if gap <= 0 else '距离目标还差'}</p>
        </div>
        """, unsafe_allow_html=True)

        # 剩余时间指标卡
        current_month = datetime.now().month
        remaining_months = 12 - current_month

        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">剩余时间</p>
            <p class="card-value">{remaining_months}个月</p>
            <p class="card-text">完成年度目标的剩余时间</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 月均销售额指标卡
        monthly_avg = total_sales / current_month if current_month > 0 else 0

        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">月均销售额</p>
            <p class="card-value">{format_currency(monthly_avg)}</p>
            <p class="card-text">当前平均月销售额</p>
        </div>
        """, unsafe_allow_html=True)

        # 月需销售额指标卡
        required_monthly = gap / remaining_months if remaining_months > 0 else 0

        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">月需销售额</p>
            <p class="card-value" style="color: {'#4CAF50' if required_monthly <= monthly_avg else '#F44336'};">{format_currency(required_monthly)}</p>
            <p class="card-text">剩余月份每月需完成的销售额</p>
        </div>
        """, unsafe_allow_html=True)

    # 目标达成建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
    if gap <= 0:
        st.markdown(f"""
        <h4>🎉 目标达成建议</h4>
        <p>恭喜！您已经超额完成了年度销售目标 {format_percentage(abs(gap_percentage))}。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>继续保持当前销售策略，争取更高业绩</li>
            <li>关注高毛利产品，提升整体盈利能力</li>
            <li>加强团队激励，保持销售动力</li>
            <li>考虑调高下一阶段销售目标</li>
        </ul>
        """, unsafe_allow_html=True)
    elif achievement_rate >= 80:
        st.markdown(f"""
        <h4>📈 目标达成建议</h4>
        <p>目前达成率良好，距离目标还差 {format_currency(gap)}（{format_percentage(gap_percentage)}）。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>聚焦核心客户，提高客单价和复购率</li>
            <li>加强新客户开发，扩大销售基础</li>
            <li>制定冲刺计划，确保全年达成</li>
            <li>关注季节性因素，调整Q4销售策略</li>
        </ul>
        """, unsafe_allow_html=True)
    elif achievement_rate >= 60:
        st.markdown(f"""
        <h4>⚠️ 目标达成建议</h4>
        <p>目前达成率一般，距离目标还差 {format_currency(gap)}（{format_percentage(gap_percentage)}）。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>分析销售漏斗，找出转化率低的环节</li>
            <li>加强促销活动，刺激短期销售增长</li>
            <li>强化销售团队培训，提升销售技能</li>
            <li>优化产品组合，聚焦高增长产品</li>
        </ul>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <h4>🚨 目标达成建议</h4>
        <p>目前达成率较低，距离目标还差 {format_currency(gap)}（{format_percentage(gap_percentage)}）。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>召开销售紧急会议，制定追赶计划</li>
            <li>重点关注大客户，争取大单支持</li>
            <li>考虑调整产品价格策略，提高竞争力</li>
            <li>重新评估年度目标合理性，必要时调整</li>
        </ul>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:  # 渠道分析
    st.subheader("🔄 销售渠道分析")

    # MT和TT渠道销售额和占比
    mt_sales = analysis_result.get('mt_sales', 0)
    tt_sales = analysis_result.get('tt_sales', 0)
    channel_data = analysis_result.get('channel_data', pd.DataFrame())

    # 渠道占比饼图和柱状图
    col1, col2 = st.columns(2)

    with col1:
        if not channel_data.empty:
            fig = create_channel_pie_chart(channel_data, "渠道销售占比")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            channel_balance = analyze_channel_distribution(mt_percentage, tt_percentage)

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> MT渠道销售额{format_currency(mt_sales)}，占比{format_percentage(mt_percentage)}；
                TT渠道销售额{format_currency(tt_sales)}，占比{format_percentage(tt_percentage)}。
                渠道分布{channel_balance}。
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if not channel_data.empty:
            # 创建渠道销售额柱状图
            fig = px.bar(
                channel_data,
                x='渠道',
                y='销售额',
                title="渠道销售额对比",
                color='渠道',
                text='销售额',
                color_discrete_sequence=[COLORS['primary'], COLORS['secondary']]
            )

            fig.update_traces(
                texttemplate='%{y:,.0f}',
                textposition='outside'
            )

            fig.update_layout(
                height=350,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="渠道",
                yaxis_title="销售额（元）",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            dominant_channel = "MT" if mt_sales > tt_sales else "TT"

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> {dominant_channel}渠道是主要销售渠道，贡献了较大部分的销售额。
                {'建议维持多渠道发展策略，避免过度依赖单一渠道。' if abs(mt_percentage - tt_percentage) < 30 else f'建议加强{("TT" if mt_percentage > tt_percentage else "MT")}渠道开发，降低渠道依赖风险。'}
            </div>
            """, unsafe_allow_html=True)

    # 渠道战略分析
    st.markdown('<div class="sub-header">📊 渠道战略分析</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # MT渠道分析卡片
        st.markdown(f"""
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
            <h3 style="color: {COLORS['primary']};">MT渠道分析</h3>
            <p><strong>销售额：</strong> {format_currency(mt_sales)}</p>
            <p><strong>渠道占比：</strong> {format_percentage(mt_percentage)}</p>
            <p><strong>渠道优势：</strong> 稳定的销售渠道，品牌展示效果好</p>
            <p><strong>渠道挑战：</strong> 竞争激烈，渠道费用高</p>
            <hr>
            <h4>策略建议</h4>
            <ul>
                <li>深耕KA客户，提高单店效率</li>
                <li>优化陈列布局，突出新品展示</li>
                <li>加强与采购方关系，争取资源倾斜</li>
                <li>季节性调整产品组合，提高周转率</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # TT渠道分析卡片
        st.markdown(f"""
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
            <h3 style="color: {COLORS['secondary']};">TT渠道分析</h3>
            <p><strong>销售额：</strong> {format_currency(tt_sales)}</p>
            <p><strong>渠道占比：</strong> {format_percentage(tt_percentage)}</p>
            <p><strong>渠道优势：</strong> 广泛的市场覆盖，渗透下沉市场</p>
            <p><strong>渠道挑战：</strong> 管理难度大，单店效率低</p>
            <hr>
            <h4>策略建议</h4>
            <ul>
                <li>扩大网点覆盖，下沉至三四线市场</li>
                <li>差异化产品策略，针对性开发TT专用产品</li>
                <li>优化渠道激励政策，提升客户积极性</li>
                <li>建立渠道关键指标体系，提高管理效率</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 渠道发展建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
    if abs(mt_percentage - tt_percentage) < 20:
        st.markdown(f"""
        <h4>🎯 渠道平衡策略</h4>
        <p>当前渠道结构较为均衡，MT占比{format_percentage(mt_percentage)}，TT占比{format_percentage(tt_percentage)}。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>保持双渠道均衡发展策略，降低渠道风险</li>
            <li>MT渠道深耕精耕，提升单店销售效率</li>
            <li>TT渠道广覆盖，扩大市场渗透率</li>
            <li>加强渠道协同，确保价格体系稳定</li>
        </ul>
        """, unsafe_allow_html=True)
    elif mt_percentage > tt_percentage:
        st.markdown(f"""
        <h4>🔔 MT渠道占比过高提示</h4>
        <p>当前MT渠道占比{format_percentage(mt_percentage)}，明显高于TT渠道占比{format_percentage(tt_percentage)}。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>加强TT渠道开发，平衡渠道结构</li>
            <li>开发TT渠道专属产品，提升竞争力</li>
            <li>优化TT渠道激励政策，吸引更多客户</li>
            <li>加强TT渠道培训和支持</li>
        </ul>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <h4>🔔 TT渠道占比过高提示</h4>
        <p>当前TT渠道占比{format_percentage(tt_percentage)}，明显高于MT渠道占比{format_percentage(mt_percentage)}。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>加强MT渠道维护，确保核心产品覆盖</li>
            <li>优化MT渠道产品结构，提升单店销量</li>
            <li>加强与大型MT客户战略合作</li>
            <li>提升MT渠道产品陈列质量</li>
        </ul>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:  # 销售人员
    st.subheader("👨‍💼 销售人员分析")

    # 销售人员业绩
    salesperson_sales = analysis_result.get('salesperson_sales', pd.DataFrame())

    if not salesperson_sales.empty:
        # TOP10销售人员业绩
        fig = create_salesperson_chart(salesperson_sales, "TOP10销售人员业绩")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_salesperson = salesperson_sales.iloc[0]['申请人'] if not salesperson_sales.empty else ""
        top_sales = salesperson_sales.iloc[0]['销售额'] if not salesperson_sales.empty else 0

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> TOP1销售人员{top_salesperson}贡献{format_currency(top_sales)}销售额，表现优异。
            销售团队整体表现{analyze_team_distribution(salesperson_sales)}。
        </div>
        """, unsafe_allow_html=True)

        # 销售人员数据分析
        st.markdown('<div class="sub-header">📊 销售人员数据分析</div>', unsafe_allow_html=True)

        # 计算销售人员相关指标
        salesperson_count = len(salesperson_sales)
        avg_sales_per_person = salesperson_sales['销售额'].mean()
        median_sales = salesperson_sales['销售额'].median()
        sales_std = salesperson_sales['销售额'].std()
        cv = (sales_std / avg_sales_per_person * 100) if avg_sales_per_person > 0 else 0

        # 显示指标卡片
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">销售人员数量</p>
                <p class="card-value">{salesperson_count}</p>
                <p class="card-text">当前活跃销售人员</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">人均销售额</p>
                <p class="card-value">{format_currency(avg_sales_per_person)}</p>
                <p class="card-text">销售团队平均水平</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">业绩变异系数</p>
                <p class="card-value">{format_percentage(cv)}</p>
                <p class="card-text">团队均衡性指标</p>
            </div>
            """, unsafe_allow_html=True)

        # 销售人员分布分析
        col1, col2 = st.columns(2)

        with col1:
            # 计算区域销售人员分布
            if '所属区域' in filtered_data['sales_orders'].columns and '申请人' in filtered_data['sales_orders'].columns:
                region_salesperson = filtered_data['sales_orders'].groupby(['所属区域', '申请人'])['销售额'].sum().reset_index()
                region_salesperson_count = region_salesperson.groupby('所属区域')['申请人'].nunique().reset_index()
                region_salesperson_count.columns = ['所属区域', '销售人员数量']

                # 创建区域销售人员分布图
                fig = px.bar(
                    region_salesperson_count,
                    x='所属区域',
                    y='销售人员数量',
                    title="区域销售人员分布",
                    color='所属区域',
                    text='销售人员数量'
                )

                fig.update_traces(
                    textposition='outside'
                )

                fig.update_layout(
                    height=350,
                    margin=dict(l=50, r=50, t=60, b=50),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_title="区域",
                    yaxis_title="销售人员数量",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 计算销售人员业绩分布
            sales_distribution = pd.cut(
                salesperson_sales['销售额'],
                bins=[0, 100000, 500000, 1000000, float('inf')],
                labels=['10万以下', '10-50万', '50-100万', '100万以上']
            )

            sales_distribution = pd.DataFrame({
                '销售额区间': sales_distribution,
                '人数': 1
            }).groupby('销售额区间').count().reset_index()

            fig = px.pie(
                sales_distribution,
                names='销售额区间',
                values='人数',
                title="销售人员业绩分布",
                color_discrete_sequence=px.colors.qualitative.Set3
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

            st.plotly_chart(fig, use_container_width=True)

        # 销售团队建议
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
        if cv > 50:
            st.markdown(f"""
            <h4>🚨 团队均衡性警报</h4>
            <p>当前团队业绩差异较大（变异系数{format_percentage(cv)}），存在明显的业绩不平衡现象。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>分析高绩效销售人员的成功经验，总结最佳实践</li>
                <li>对低绩效销售人员进行针对性辅导和培训</li>
                <li>优化销售区域和客户分配，提高资源配置效率</li>
                <li>调整团队激励机制，促进团队整体绩效提升</li>
            </ul>
            """, unsafe_allow_html=True)
        elif cv > 30:
            st.markdown(f"""
            <h4>⚠️ 团队均衡性提示</h4>
            <p>当前团队业绩差异中等（变异系数{format_percentage(cv)}），仍有优化空间。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>加强团队内部经验分享，促进相互学习</li>
                <li>针对中等绩效销售人员提供针对性指导</li>
                <li>定期开展销售技能培训，提升团队整体能力</li>
                <li>建立销售辅导机制，帮助成员突破瓶颈</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <h4>✅ 团队均衡性良好</h4>
            <p>当前团队业绩比较均衡（变异系数{format_percentage(cv)}），整体表现稳定。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>保持当前团队管理方式，继续培养团队凝聚力</li>
                <li>建立长效激励机制，维持团队稳定性</li>
                <li>挖掘团队增长潜力，尝试突破业绩天花板</li>
                <li>加强团队核心能力建设，应对市场变化</li>
            </ul>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无销售人员数据")

with tabs[4]:  # BCG产品矩阵
    st.subheader("🔵 BCG产品组合分析")

    # 产品BCG分析
    product_sales = analysis_result.get('product_sales', pd.DataFrame())
    bcg_summary = analysis_result.get('bcg_summary', pd.DataFrame())

    if not product_sales.empty and not bcg_summary.empty:
        # 产品BCG矩阵图和产品组合饼图
        col1, col2 = st.columns(2)

        with col1:
            # BCG矩阵气泡图
            fig = create_bcg_bubble_chart(product_sales, "产品BCG矩阵分析")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown("""
            <div class="chart-explanation">
                <b>BCG矩阵解读：</b>
                <ul>
                    <li><b>明星产品</b> - 高增长、高市场份额，需要持续投入来保持增长</li>
                    <li><b>现金牛产品</b> - 低增长、高市场份额，产生稳定现金流</li>
                    <li><b>问号产品</b> - 高增长、低市场份额，需要评估是否增加投入</li>
                    <li><b>瘦狗产品</b> - 低增长、低市场份额，考虑是否退出</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # BCG分类饼图
            fig = create_bcg_pie_chart(bcg_summary, "产品组合健康度")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            cash_cow_percent = analysis_result.get('cash_cow_percent', 0)
            star_question_percent = analysis_result.get('star_question_percent', 0)
            dog_percent = analysis_result.get('dog_percent', 0)
            is_healthy_mix = analysis_result.get('is_healthy_mix', False)

            st.markdown(f"""
            <div class="chart-explanation">
                <b>产品组合解读：</b> {'当前产品组合结构健康' if is_healthy_mix else '当前产品组合结构需要优化'}。
                现金牛产品占比{format_percentage(cash_cow_percent)}（理想：45-50%），
                明星&问号产品占比{format_percentage(star_question_percent)}（理想：40-45%），
                瘦狗产品占比{format_percentage(dog_percent)}（理想：≤10%）。
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
                <p><b>销售占比：</b> {format_percentage(cash_cow_percent)}</p>
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
                    <li>{'增加现金牛产品比例，扩大稳定收入来源' if cash_cow_percent < 45 else '保持现金牛产品稳定' if cash_cow_percent <= 50 else '适当控制现金牛产品比例，避免过度依赖'}</li>
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
                    <li>重点评估高增长问号产品，制定突破计划</li>
                    <li>增加营销投入，提升市场知名度</li>
                    <li>针对高潜力产品，扩大渠道覆盖</li>
                    <li>建立专项追踪机制，定期评估投入产出比</li>
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
                    <li>持续投入，保持增长势头</li>
                    <li>扩大渠道覆盖，占领更多市场份额</li>
                    <li>加强品牌建设，提高客户忠诚度</li>
                    <li>建立完整产品线，打造产品生态</li>
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
                <p><b>销售占比：</b> {format_percentage(dog_percent)}</p>
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
                    <li>{'减少瘦狗产品比例，释放资源' if dog_percent > 10 else '维持瘦狗产品适度比例，避免资源浪费'}</li>
                    <li>重新评估产品定位，尝试转型或升级</li>
                    <li>计划性淘汰无潜力产品，集中资源</li>
                    <li>设定清晰退出机制，降低退出成本</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 产品组合优化建议
        is_healthy_mix = analysis_result.get('is_healthy_mix', False)
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
        if is_healthy_mix:
            st.markdown(f"""
            <h4>✅ 产品组合健康</h4>
            <p>当前产品组合结构健康，符合JBP计划产品模型要求（现金牛45-50%，明星&问号40-45%，瘦狗≤10%）。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>保持现有产品组合结构，继续监控各类产品表现</li>
                <li>关注明星产品向现金牛产品的转化，确保持续稳定的现金流</li>
                <li>培育问号产品，为未来增长做准备</li>
                <li>定期淘汰瘦狗产品，优化资源配置</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            if cash_cow_percent < 45:
                st.markdown(f"""
                <h4>⚠️ 现金牛产品比例不足</h4>
                <p>当前现金牛产品占比{format_percentage(cash_cow_percent)}，低于理想的45-50%，可能影响稳定现金流。</p>
                <p><strong>建议行动：</strong></p>
                <ul>
                    <li>加强现金牛产品营销，提高市场份额</li>
                    <li>加速优质明星产品向现金牛产品转化</li>
                    <li>扩大现金牛产品的渠道覆盖</li>
                    <li>控制现金牛产品成本，提高利润率</li>
                </ul>
                """, unsafe_allow_html=True)
            elif cash_cow_percent > 50:
                st.markdown(f"""
                <h4>⚠️ 现金牛产品比例过高</h4>
                <p>当前现金牛产品占比{format_percentage(cash_cow_percent)}，高于理想的45-50%，可能缺乏长期增长动力。</p>
                <p><strong>建议行动：</strong></p>
                <ul>
                    <li>增加明星和问号产品的投入，培育未来增长点</li>
                    <li>开发创新产品，丰富产品线</li>
                    <li>评估现金牛产品生命周期，适时淘汰老化产品</li>
                    <li>建立产品创新机制，保持产品活力</li>
                </ul>
                """, unsafe_allow_html=True)
            elif star_question_percent < 40:
                st.markdown(f"""
                <h4>⚠️ 明星和问号产品比例不足</h4>
                <p>当前明星和问号产品占比{format_percentage(star_question_percent)}，低于理想的40-45%，未来增长动力不足。</p>
                <p><strong>建议行动：</strong></p>
                <ul>
                    <li>加大研发投入，开发创新产品</li>
                    <li>增加明星产品的营销支持，扩大市场份额</li>
                    <li>评估问号产品潜力，对高潜力产品加大投入</li>
                    <li>建立产品创新孵化机制，持续培育新品</li>
                </ul>
                """, unsafe_allow_html=True)
            elif dog_percent > 10:
                st.markdown(f"""
                <h4>⚠️ 瘦狗产品比例过高</h4>
                <p>当前瘦狗产品占比{format_percentage(dog_percent)}，高于理想的10%以下，资源配置效率不高。</p>
                <p><strong>建议行动：</strong></p>
                <ul>
                    <li>制定瘦狗产品淘汰计划，释放资源</li>
                    <li>评估瘦狗产品潜力，有潜力的尝试重新定位</li>
                    <li>无潜力的产品逐步减少投入，最终退出</li>
                    <li>建立产品生命周期管理机制，及时处理低效产品</li>
                </ul>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无产品BCG分析数据")

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
    <p><strong>渠道表现：</strong>{'MT渠道占主导' if analysis_result.get('mt_sales', 0) > analysis_result.get('tt_sales', 0) else 'TT渠道占主导'}，渠道分布{analyze_channel_distribution(analysis_result.get('mt_percentage', 0), analysis_result.get('tt_percentage', 0))}</p>
    <p><strong>综合评价：</strong>{comment}</p>
</div>
""", unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)

