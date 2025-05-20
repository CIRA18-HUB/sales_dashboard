# pages/material_page.py - 完全自包含的物料分析页面
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
    COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, load_data_files, create_filters, add_chart_explanation,
    create_flip_card, setup_page
)

# ==================== 页面配置 ====================
setup_page()

# 检查认证
if not check_authentication():
    st.stop()

# 页面标题
st.title("🧰 物料分析")

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
def calculate_material_metrics(expense_orders):
    """计算物料相关指标"""
    if expense_orders.empty:
        return {}

    # 筛选物料订单
    material_orders = expense_orders[expense_orders['订单类型'] == '物料'].copy()

    # 促销费用订单（非物料订单）
    promotion_orders = expense_orders[expense_orders['订单类型'] != '物料'].copy()

    # 计算物料总费用
    if '求和项:金额（元）' in material_orders.columns:
        total_material_expense = material_orders['求和项:金额（元）'].sum()
    else:
        total_material_expense = 0

    # 计算促销总费用
    if '求和项:金额（元）' in promotion_orders.columns:
        total_promotion_expense = promotion_orders['求和项:金额（元）'].sum()
    else:
        total_promotion_expense = 0

    # 计算各类促销费用占比
    promotion_by_type = pd.DataFrame()
    if not promotion_orders.empty and '订单类型' in promotion_orders.columns:
        promotion_by_type = promotion_orders.groupby('订单类型')['求和项:金额（元）'].sum().reset_index()
        promotion_by_type['占比'] = promotion_by_type[
                                        '求和项:金额（元）'] / total_promotion_expense * 100 if total_promotion_expense > 0 else 0

    # 计算物料费用月度趋势
    material_monthly_trend = pd.DataFrame()
    if '发运月份' in material_orders.columns:
        material_orders['月份'] = pd.to_datetime(material_orders['发运月份']).dt.strftime('%Y-%m')
        material_monthly_trend = material_orders.groupby('月份')['求和项:金额（元）'].sum().reset_index()

    # 计算促销费用月度趋势
    promotion_monthly_trend = pd.DataFrame()
    if '发运月份' in promotion_orders.columns:
        promotion_orders['月份'] = pd.to_datetime(promotion_orders['发运月份']).dt.strftime('%Y-%m')
        promotion_monthly_trend = promotion_orders.groupby('月份')['求和项:金额（元）'].sum().reset_index()

    # 合并物料和促销月度趋势
    monthly_expense = pd.DataFrame()
    if not material_monthly_trend.empty or not promotion_monthly_trend.empty:
        # 获取所有月份
        all_months = set()
        if not material_monthly_trend.empty:
            all_months.update(material_monthly_trend['月份'])
        if not promotion_monthly_trend.empty:
            all_months.update(promotion_monthly_trend['月份'])

        monthly_expense = pd.DataFrame({'月份': list(all_months)})

        # 合并物料费用
        if not material_monthly_trend.empty:
            monthly_expense = monthly_expense.merge(
                material_monthly_trend,
                on='月份',
                how='left'
            )
            monthly_expense.rename(columns={'求和项:金额（元）': '物料费用'}, inplace=True)
        else:
            monthly_expense['物料费用'] = 0

        # 合并促销费用
        if not promotion_monthly_trend.empty:
            monthly_expense = monthly_expense.merge(
                promotion_monthly_trend,
                on='月份',
                how='left'
            )
            monthly_expense.rename(columns={'求和项:金额（元）': '促销费用'}, inplace=True)
        else:
            monthly_expense['促销费用'] = 0

        # 填充缺失值
        monthly_expense.fillna(0, inplace=True)

        # 按月份排序
        monthly_expense['月份_日期'] = pd.to_datetime(monthly_expense['月份'])
        monthly_expense.sort_values('月份_日期', inplace=True)
        monthly_expense.drop('月份_日期', axis=1, inplace=True)

    # 计算各区域物料费用分布
    region_material_expense = pd.DataFrame()
    if not material_orders.empty and '所属区域' in material_orders.columns:
        region_material_expense = material_orders.groupby('所属区域')['求和项:金额（元）'].sum().reset_index()
        region_material_expense['占比'] = region_material_expense[
                                              '求和项:金额（元）'] / total_material_expense * 100 if total_material_expense > 0 else 0

    # 计算物料使用率和ROI
    # 假设：物料费用与销售收入比率为衡量使用效率的指标
    material_efficiency = {}
    sales_orders = filtered_data.get('sales_orders', pd.DataFrame())
    if not sales_orders.empty and '销售额' in sales_orders.columns:
        total_sales = sales_orders['销售额'].sum()

        # 物料费用率
        material_expense_ratio = total_material_expense / total_sales * 100 if total_sales > 0 else 0

        # 促销费用率
        promotion_expense_ratio = total_promotion_expense / total_sales * 100 if total_sales > 0 else 0

        # 物料ROI（简化计算，假设销售额增长的10%归因于物料投入）
        material_roi = total_sales * 0.1 / total_material_expense if total_material_expense > 0 else 0

        # 促销ROI（简化计算，假设销售额增长的20%归因于促销活动）
        promotion_roi = total_sales * 0.2 / total_promotion_expense if total_promotion_expense > 0 else 0

        material_efficiency = {
            'material_expense_ratio': material_expense_ratio,
            'promotion_expense_ratio': promotion_expense_ratio,
            'material_roi': material_roi,
            'promotion_roi': promotion_roi,
            'total_sales': total_sales
        }

    return {
        'total_material_expense': total_material_expense,
        'total_promotion_expense': total_promotion_expense,
        'promotion_by_type': promotion_by_type,
        'monthly_expense': monthly_expense,
        'region_material_expense': region_material_expense,
        'material_efficiency': material_efficiency
    }


# ==================== 分析数据 ====================
def analyze_material_data(filtered_data):
    """分析物料数据"""
    expense_orders = filtered_data.get('expense_orders', pd.DataFrame())
    sales_orders = filtered_data.get('sales_orders', pd.DataFrame())

    # 计算物料指标
    material_metrics = calculate_material_metrics(expense_orders)

    # 分析促销活动效果
    promotion_data = filtered_data.get('promotion_data', pd.DataFrame())
    if not promotion_data.empty and not sales_orders.empty:
        # 获取促销活动期间的销售数据
        promotion_sales = pd.DataFrame()

        if '促销开始供货时间' in promotion_data.columns and '促销结束供货时间' in promotion_data.columns:
            # 筛选有效的促销活动
            valid_promotions = promotion_data.dropna(subset=['促销开始供货时间', '促销结束供货时间'])

            # 合并所有促销活动期间的销售数据
            promotion_period_sales = []

            for _, promotion in valid_promotions.iterrows():
                start_date = promotion['促销开始供货时间']
                end_date = promotion['促销结束供货时间']

                # 筛选促销期间的销售数据
                period_sales = sales_orders[
                    (sales_orders['发运月份'] >= start_date) &
                    (sales_orders['发运月份'] <= end_date)
                    ]

                # 添加促销活动信息
                if not period_sales.empty:
                    period_sales[
                        '促销活动'] = f"{promotion.get('流程编号：', '')} ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})"
                    period_sales['促销类型'] = "促销期间销售"
                    promotion_period_sales.append(period_sales)

            # 合并所有促销期间的销售数据
            if promotion_period_sales:
                promotion_sales = pd.concat(promotion_period_sales)

        # 计算促销效果指标
        promotion_effect = {}

        if not promotion_sales.empty:
            # 促销期间总销售额
            promotion_total_sales = promotion_sales['销售额'].sum()

            # 计算非促销期间的销售数据
            non_promotion_sales = sales_orders[~sales_orders.index.isin(promotion_sales.index)]
            non_promotion_total_sales = non_promotion_sales['销售额'].sum()

            # 计算促销期间和非促销期间的天数
            if '发运月份' in promotion_sales.columns and '发运月份' in non_promotion_sales.columns:
                promotion_days = (promotion_sales['发运月份'].max() - promotion_sales['发运月份'].min()).days + 1
                non_promotion_days = (non_promotion_sales['发运月份'].max() - non_promotion_sales[
                    '发运月份'].min()).days + 1

                # 计算日均销售额
                promotion_daily_sales = promotion_total_sales / promotion_days if promotion_days > 0 else 0
                non_promotion_daily_sales = non_promotion_total_sales / non_promotion_days if non_promotion_days > 0 else 0

                # 计算促销增长率
                promotion_growth = (
                                               promotion_daily_sales - non_promotion_daily_sales) / non_promotion_daily_sales * 100 if non_promotion_daily_sales > 0 else 0

                promotion_effect = {
                    'promotion_total_sales': promotion_total_sales,
                    'non_promotion_total_sales': non_promotion_total_sales,
                    'promotion_days': promotion_days,
                    'non_promotion_days': non_promotion_days,
                    'promotion_daily_sales': promotion_daily_sales,
                    'non_promotion_daily_sales': non_promotion_daily_sales,
                    'promotion_growth': promotion_growth
                }

        material_metrics['promotion_effect'] = promotion_effect

    return material_metrics


# ==================== 图表创建函数 ====================
def create_expense_pie_chart(expense_by_type, title="费用类型占比"):
    """创建费用类型占比饼图"""
    if expense_by_type.empty:
        return None

    fig = px.pie(
        expense_by_type,
        names='订单类型',
        values='求和项:金额（元）',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel,
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


def create_expense_trend_chart(monthly_expense, title="费用月度趋势"):
    """创建费用月度趋势图"""
    if monthly_expense.empty:
        return None

    fig = go.Figure()

    # 添加物料费用线
    if '物料费用' in monthly_expense.columns:
        fig.add_trace(go.Scatter(
            x=monthly_expense['月份'],
            y=monthly_expense['物料费用'],
            mode='lines+markers',
            name='物料费用',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=8)
        ))

    # 添加促销费用线
    if '促销费用' in monthly_expense.columns:
        fig.add_trace(go.Scatter(
            x=monthly_expense['月份'],
            y=monthly_expense['促销费用'],
            mode='lines+markers',
            name='促销费用',
            line=dict(color=COLORS['secondary'], width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=title,
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="月份",
        yaxis_title="费用金额（元）",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_region_expense_chart(region_expense, title="区域费用分布"):
    """创建区域费用分布图"""
    if region_expense.empty:
        return None

    # 按费用降序排序
    region_expense = region_expense.sort_values('求和项:金额（元）', ascending=False)

    fig = px.bar(
        region_expense,
        x='所属区域',
        y='求和项:金额（元）',
        title=title,
        color='所属区域',
        text='求和项:金额（元）'
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
        xaxis_title="区域",
        yaxis_title="费用金额（元）",
        showlegend=False
    )

    return fig


def create_efficiency_gauge(value, title, max_value=10, target=5):
    """创建效率指标仪表盘"""
    if value > max_value:
        value = max_value

    # 确定颜色
    if value >= target:
        color = COLORS['success']
    elif value >= target / 2:
        color = COLORS['warning']
    else:
        color = COLORS['danger']

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        number={'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, target / 2], 'color': 'rgba(255, 67, 54, 0.3)'},
                {'range': [target / 2, target], 'color': 'rgba(255, 144, 14, 0.3)'},
                {'range': [target, max_value], 'color': 'rgba(50, 205, 50, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
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


def create_expense_ratio_chart(material_ratio, promotion_ratio, title="费用占比分析"):
    """创建费用占比柱状图"""
    # 创建数据
    data = pd.DataFrame({
        '费用类型': ['物料费用率', '促销费用率'],
        '占销售比例': [material_ratio, promotion_ratio]
    })

    # 设置颜色
    colors = [COLORS['primary'], COLORS['secondary']]

    fig = px.bar(
        data,
        x='费用类型',
        y='占销售比例',
        title=title,
        color='费用类型',
        color_discrete_sequence=colors,
        text='占销售比例'
    )

    fig.update_traces(
        texttemplate='%{y:.2f}%',
        textposition='outside'
    )

    fig.update_layout(
        height=350,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="费用类型",
        yaxis_title="占销售比例（%）",
        showlegend=False
    )

    return fig


def create_promotion_effect_chart(promotion_effect, title="促销效果分析"):
    """创建促销效果对比图"""
    if not promotion_effect:
        return None

    promotion_daily_sales = promotion_effect.get('promotion_daily_sales', 0)
    non_promotion_daily_sales = promotion_effect.get('non_promotion_daily_sales', 0)

    # 创建数据
    data = pd.DataFrame({
        '销售状态': ['非促销期间', '促销期间'],
        '日均销售额': [non_promotion_daily_sales, promotion_daily_sales]
    })

    # 设置颜色
    colors = [COLORS['gray'], COLORS['success']]

    fig = px.bar(
        data,
        x='销售状态',
        y='日均销售额',
        title=title,
        color='销售状态',
        color_discrete_sequence=colors,
        text='日均销售额'
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
        xaxis_title="销售状态",
        yaxis_title="日均销售额（元）",
        showlegend=False
    )

    # 添加增长率标注
    growth = promotion_effect.get('promotion_growth', 0)
    fig.add_annotation(
        x=1,
        y=promotion_daily_sales * 1.1,
        text=f"增长率: {format_percentage(growth)}",
        showarrow=False,
        font=dict(
            size=14,
            color="green" if growth > 0 else "red"
        ),
        bgcolor="white",
        bordercolor="green" if growth > 0 else "red",
        borderwidth=1,
        borderpad=4
    )

    return fig


# ==================== 主页面 ====================
# 分析数据
material_analysis = analyze_material_data(filtered_data)

# 创建标签页
tabs = st.tabs(["📊 费用概览", "🔍 物料分析", "🚀 促销效果", "💲 ROI分析"])

with tabs[0]:  # 费用概览
    # 费用总览指标行
    st.subheader("🔑 关键费用指标")
    col1, col2, col3, col4 = st.columns(4)

    # 物料总费用
    total_material_expense = material_analysis.get('total_material_expense', 0)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">物料总费用</p>
            <p class="card-value">{format_currency(total_material_expense)}</p>
            <p class="card-text">物料投入总金额</p>
        </div>
        """, unsafe_allow_html=True)

    # 促销总费用
    total_promotion_expense = material_analysis.get('total_promotion_expense', 0)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">促销总费用</p>
            <p class="card-value">{format_currency(total_promotion_expense)}</p>
            <p class="card-text">促销活动总投入</p>
        </div>
        """, unsafe_allow_html=True)

    # 物料费用率
    material_efficiency = material_analysis.get('material_efficiency', {})
    material_expense_ratio = material_efficiency.get('material_expense_ratio', 0)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">物料费用率</p>
            <p class="card-value">{format_percentage(material_expense_ratio)}</p>
            <p class="card-text">物料费用占销售比例</p>
        </div>
        """, unsafe_allow_html=True)

    # 促销费用率
    promotion_expense_ratio = material_efficiency.get('promotion_expense_ratio', 0)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">促销费用率</p>
            <p class="card-value">{format_percentage(promotion_expense_ratio)}</p>
            <p class="card-text">促销费用占销售比例</p>
        </div>
        """, unsafe_allow_html=True)

    # 费用分布分析
    st.markdown('<div class="sub-header">📊 费用分布分析</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        # 促销费用类型占比饼图
        promotion_by_type = material_analysis.get('promotion_by_type', pd.DataFrame())
        if not promotion_by_type.empty:
            fig = create_expense_pie_chart(promotion_by_type, "促销费用类型占比")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            top_type = promotion_by_type.sort_values('求和项:金额（元）', ascending=False).iloc[0]
            top_type_name = top_type['订单类型']
            top_type_amount = top_type['求和项:金额（元）']
            top_type_percentage = top_type['占比']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> 最主要的促销费用类型是{top_type_name}，金额{format_currency(top_type_amount)}，占促销总费用的{format_percentage(top_type_percentage)}。
                {'费用集中在少数类型，投入结构相对集中。' if top_type_percentage > 50 else '费用分布相对均衡，各类型投入较为平衡。'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无促销费用类型数据")

    with cols[1]:
        # 区域费用分布图
        region_material_expense = material_analysis.get('region_material_expense', pd.DataFrame())
        if not region_material_expense.empty:
            fig = create_region_expense_chart(region_material_expense, "区域物料费用分布")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            top_region = region_material_expense.sort_values('求和项:金额（元）', ascending=False).iloc[0]
            top_region_name = top_region['所属区域']
            top_region_amount = top_region['求和项:金额（元）']
            top_region_percentage = top_region['占比']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> 物料费用最高的区域是{top_region_name}，金额{format_currency(top_region_amount)}，占总物料费用的{format_percentage(top_region_percentage)}。
                {'区域间物料投入差异较大，投入集中在少数区域。' if top_region_percentage > 30 else '区域间物料投入相对均衡，资源分配较为平均。'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无区域物料费用数据")

    # 费用趋势分析
    st.markdown('<div class="sub-header">📊 费用趋势分析</div>', unsafe_allow_html=True)

    # 月度费用趋势图
    monthly_expense = material_analysis.get('monthly_expense', pd.DataFrame())
    if not monthly_expense.empty:
        fig = create_expense_trend_chart(monthly_expense, "物料和促销费用月度趋势")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        trend_analysis = ""

        if '物料费用' in monthly_expense.columns and len(monthly_expense) > 1:
            latest_material = monthly_expense.iloc[-1]['物料费用']
            previous_material = monthly_expense.iloc[-2]['物料费用']
            material_mom_change = (
                                              latest_material - previous_material) / previous_material * 100 if previous_material > 0 else 0

            trend_analysis += f"最近月物料费用{format_currency(latest_material)}，环比{'增长' if material_mom_change >= 0 else '下降'}{format_percentage(abs(material_mom_change))}。"

        if '促销费用' in monthly_expense.columns and len(monthly_expense) > 1:
            latest_promotion = monthly_expense.iloc[-1]['促销费用']
            previous_promotion = monthly_expense.iloc[-2]['促销费用']
            promotion_mom_change = (
                                               latest_promotion - previous_promotion) / previous_promotion * 100 if previous_promotion > 0 else 0

            trend_analysis += f"最近月促销费用{format_currency(latest_promotion)}，环比{'增长' if promotion_mom_change >= 0 else '下降'}{format_percentage(abs(promotion_mom_change))}。"

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> {trend_analysis}
            {'物料和促销费用呈现季节性波动，可能与促销活动周期相关。' if len(monthly_expense) >= 3 else '费用趋势数据较少，无法判断长期趋势。'}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("暂无月度费用趋势数据")

    # 费用占比分析
    if material_efficiency:
        fig = create_expense_ratio_chart(material_expense_ratio, promotion_expense_ratio, "物料和促销费用占销售比例")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        total_ratio = material_expense_ratio + promotion_expense_ratio

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 物料费用占销售额的{format_percentage(material_expense_ratio)}，促销费用占销售额的{format_percentage(promotion_expense_ratio)}，合计占比{format_percentage(total_ratio)}。
            {'总体费用率处于合理范围，投入产出比良好。' if total_ratio < 10 else '总体费用率较高，需关注投入产出效率。'}
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:  # 物料分析
    st.subheader("🔍 物料费用分析")

    # 物料费用率仪表盘
    cols = st.columns(2)
    with cols[0]:
        if material_efficiency:
            material_expense_ratio = material_efficiency.get('material_expense_ratio', 0)
            fig = create_efficiency_gauge(material_expense_ratio / 10, "物料费用率指数", max_value=1, target=0.5)
            st.plotly_chart(fig, use_container_width=True)

            # 合理范围解释
            if material_expense_ratio < 5:
                ratio_status = "良好，处于行业低位水平"
                ratio_color = COLORS['success']
            elif material_expense_ratio < 8:
                ratio_status = "一般，处于行业中等水平"
                ratio_color = COLORS['warning']
            else:
                ratio_status = "偏高，高于行业平均水平"
                ratio_color = COLORS['danger']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>指标解读：</b> 物料费用率{format_percentage(material_expense_ratio)}，<span style="color: {ratio_color};">{ratio_status}</span>。
                物料费用率是物料费用占销售额的比例，反映了物料投入的效率。{'费用控制良好，成本效益显著。' if material_expense_ratio < 5 else '费用控制一般，仍有优化空间。' if material_expense_ratio < 8 else '费用控制不佳，需要改进成本管理。'}
            </div>
            """, unsafe_allow_html=True)

    with cols[1]:
        if material_efficiency:
            material_roi = material_efficiency.get('material_roi', 0)
            fig = create_efficiency_gauge(material_roi, "物料投入ROI", max_value=10, target=5)
            st.plotly_chart(fig, use_container_width=True)

            # ROI解释
            if material_roi >= 5:
                roi_status = "优秀，投资回报显著"
                roi_color = COLORS['success']
            elif material_roi >= 3:
                roi_status = "良好，投资回报一般"
                roi_color = COLORS['warning']
            else:
                roi_status = "欠佳，投资回报率低"
                roi_color = COLORS['danger']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>指标解读：</b> 物料投入ROI为{material_roi:.2f}，<span style="color: {roi_color};">{roi_status}</span>。
                ROI (Return on Investment) 表示每投入1元物料费用产生的销售回报。{'投入产出效率高，物料使用效果显著。' if material_roi >= 5 else '投入产出效率一般，物料使用效果可接受。' if material_roi >= 3 else '投入产出效率低，物料使用效果不理想，需要改进。'}
            </div>
            """, unsafe_allow_html=True)

    # 物料区域分布分析
    st.markdown('<div class="sub-header">📊 物料区域分布分析</div>', unsafe_allow_html=True)

    region_material_expense = material_analysis.get('region_material_expense', pd.DataFrame())
    if not region_material_expense.empty:
        # 创建条形图
        fig = create_region_expense_chart(region_material_expense, "区域物料费用分布")
        st.plotly_chart(fig, use_container_width=True)

        # 进一步分析区域物料使用效率
        # 假设我们可以获取各区域的销售数据
        sales_data = filtered_data.get('sales_orders', pd.DataFrame())
        if not sales_data.empty and '所属区域' in sales_data.columns:
            region_sales = sales_data.groupby('所属区域')['销售额'].sum().reset_index()

            # 合并区域销售额和物料费用
            region_efficiency = region_material_expense.merge(
                region_sales,
                on='所属区域',
                how='inner'
            )

            if not region_efficiency.empty:
                # 计算区域物料费用率
                region_efficiency['物料费用率'] = region_efficiency['求和项:金额（元）'] / region_efficiency[
                    '销售额'] * 100
                region_efficiency.sort_values('物料费用率', ascending=True, inplace=True)

                # 创建区域物料费用率条形图
                fig = px.bar(
                    region_efficiency,
                    x='所属区域',
                    y='物料费用率',
                    title="区域物料费用率对比",
                    color='物料费用率',
                    color_continuous_scale=px.colors.sequential.Blues_r,
                    text='物料费用率'
                )

                fig.update_traces(
                    texttemplate='%{y:.2f}%',
                    textposition='outside'
                )

                fig.update_layout(
                    height=400,
                    margin=dict(l=50, r=50, t=60, b=50),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_title="区域",
                    yaxis_title="物料费用率（%）"
                )

                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                best_region = region_efficiency.iloc[0]['所属区域']
                best_ratio = region_efficiency.iloc[0]['物料费用率']
                worst_region = region_efficiency.iloc[-1]['所属区域']
                worst_ratio = region_efficiency.iloc[-1]['物料费用率']

                st.markdown(f"""
                <div class="chart-explanation">
                    <b>图表解读：</b> 物料费用率最低的区域是{best_region}，为{format_percentage(best_ratio)}；最高的区域是{worst_region}，为{format_percentage(worst_ratio)}。
                    区域间物料使用效率差异明显，可从{best_region}区域借鉴经验，提升{worst_region}等高费用率区域的使用效率。
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无区域物料费用数据")

    # 物料管理建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

    if material_efficiency:
        material_expense_ratio = material_efficiency.get('material_expense_ratio', 0)
        material_roi = material_efficiency.get('material_roi', 0)

        if material_expense_ratio > 8:
            st.markdown("""
            <h4>⚠️ 物料费用控制需改进</h4>
            <p>当前物料费用率较高，投入产出效率有待提升。</p>
            <p><strong>改进建议：</strong></p>
            <ul>
                <li>审查物料采购流程，优化采购策略</li>
                <li>精细化物料使用管理，减少浪费</li>
                <li>评估各类物料的实际促销效果，优化物料结构</li>
                <li>建立物料使用监控体系，强化费用控制</li>
            </ul>
            """, unsafe_allow_html=True)
        elif material_roi < 3:
            st.markdown("""
            <h4>⚠️ 物料投入回报率低</h4>
            <p>当前物料投入产出比不理想，需要提高物料使用效率。</p>
            <p><strong>改进建议：</strong></p>
            <ul>
                <li>分析高效物料类型，优化物料投放结构</li>
                <li>改进物料投放方式，提高转化率</li>
                <li>针对不同客户和区域，制定差异化的物料策略</li>
                <li>建立物料投入效果评估机制，持续优化</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <h4>✅ 物料管理良好</h4>
            <p>当前物料费用控制和使用效率较好，建议持续优化。</p>
            <p><strong>维持建议：</strong></p>
            <ul>
                <li>保持现有物料管理方式，定期评估物料效果</li>
                <li>关注物料投入结构，优化资源配置</li>
                <li>建立物料使用最佳实践，在区域间推广</li>
                <li>持续监控物料使用效率，确保良好投入产出比</li>
            </ul>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无足够数据提供物料管理建议")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:  # 促销效果
    st.subheader("🚀 促销活动效果分析")

    # 促销费用率和ROI分析
    cols = st.columns(2)
    with cols[0]:
        if material_efficiency:
            promotion_expense_ratio = material_efficiency.get('promotion_expense_ratio', 0)
            fig = create_efficiency_gauge(promotion_expense_ratio / 10, "促销费用率指数", max_value=1, target=0.5)
            st.plotly_chart(fig, use_container_width=True)

            # 合理范围解释
            if promotion_expense_ratio < 5:
                ratio_status = "良好，处于行业低位水平"
                ratio_color = COLORS['success']
            elif promotion_expense_ratio < 10:
                ratio_status = "一般，处于行业中等水平"
                ratio_color = COLORS['warning']
            else:
                ratio_status = "偏高，高于行业平均水平"
                ratio_color = COLORS['danger']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>指标解读：</b> 促销费用率{format_percentage(promotion_expense_ratio)}，<span style="color: {ratio_color};">{ratio_status}</span>。
                促销费用率是促销费用占销售额的比例，反映了促销投入的强度。{'促销投入控制良好，成本效益平衡。' if promotion_expense_ratio < 5 else '促销投入适中，仍有优化空间。' if promotion_expense_ratio < 10 else '促销投入较高，需评估促销效果。'}
            </div>
            """, unsafe_allow_html=True)

    with cols[1]:
        if material_efficiency:
            promotion_roi = material_efficiency.get('promotion_roi', 0)
            fig = create_efficiency_gauge(promotion_roi, "促销活动ROI", max_value=10, target=5)
            st.plotly_chart(fig, use_container_width=True)

            # ROI解释
            if promotion_roi >= 5:
                roi_status = "优秀，投资回报显著"
                roi_color = COLORS['success']
            elif promotion_roi >= 3:
                roi_status = "良好，投资回报一般"
                roi_color = COLORS['warning']
            else:
                roi_status = "欠佳，投资回报率低"
                roi_color = COLORS['danger']

            st.markdown(f"""
            <div class="chart-explanation">
                <b>指标解读：</b> 促销投入ROI为{promotion_roi:.2f}，<span style="color: {roi_color};">{roi_status}</span>。
                ROI (Return on Investment) 表示每投入1元促销费用产生的销售回报。{'促销效果显著，投入产出效率高。' if promotion_roi >= 5 else '促销效果一般，投入产出可接受。' if promotion_roi >= 3 else '促销效果不理想，需要改进促销策略。'}
            </div>
            """, unsafe_allow_html=True)

    # 促销效果对比分析
    st.markdown('<div class="sub-header">📊 促销效果对比分析</div>', unsafe_allow_html=True)

    promotion_effect = material_analysis.get('promotion_effect', {})
    if promotion_effect:
        # 创建促销效果对比图
        fig = create_promotion_effect_chart(promotion_effect, "促销期间vs非促销期间销售对比")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        promotion_growth = promotion_effect.get('promotion_growth', 0)
        promotion_days = promotion_effect.get('promotion_days', 0)
        non_promotion_days = promotion_effect.get('non_promotion_days', 0)

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 促销期间（{promotion_days}天）日均销售额比非促销期间（{non_promotion_days}天）{'增长' if promotion_growth >= 0 else '下降'}{format_percentage(abs(promotion_growth))}。
            {'促销活动效果显著，有效提升了销售业绩。' if promotion_growth > 20 else '促销活动效果一般，销售提升空间有限。' if promotion_growth > 0 else '促销活动效果不佳，未能有效提升销售。'}
        </div>
        """, unsafe_allow_html=True)

        # 促销活动详细分析
        promotion_data = filtered_data.get('promotion_data', pd.DataFrame())
        if not promotion_data.empty:
            st.markdown('<div class="sub-header">📊 促销活动详情分析</div>', unsafe_allow_html=True)

            # 按区域统计促销活动数量
            if '所属区域' in promotion_data.columns:
                region_promotion_count = promotion_data.groupby('所属区域').size().reset_index(name='活动数量')

                # 创建区域促销活动数量柱状图
                fig = px.bar(
                    region_promotion_count,
                    x='所属区域',
                    y='活动数量',
                    title="区域促销活动分布",
                    color='所属区域',
                    text='活动数量'
                )

                fig.update_traces(
                    textposition='outside'
                )

                fig.update_layout(
                    height=400,
                    margin=dict(l=50, r=50, t=60, b=50),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_title="区域",
                    yaxis_title="促销活动数量",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                most_active_region = region_promotion_count.sort_values('活动数量', ascending=False).iloc[0]
                most_region_name = most_active_region['所属区域']
                most_region_count = most_active_region['活动数量']

                st.markdown(f"""
                <div class="chart-explanation">
                    <b>图表解读：</b> 促销活动最多的区域是{most_region_name}，共{most_region_count}个活动。
                    {'区域间促销活动分布不均，资源集中在少数区域。' if region_promotion_count['活动数量'].std() / region_promotion_count['活动数量'].mean() > 0.5 else '区域间促销活动分布相对均衡。'}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无促销效果对比数据")

    # 促销策略建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

    if promotion_effect:
        promotion_growth = promotion_effect.get('promotion_growth', 0)

        if promotion_growth < 0:
            st.markdown("""
            <h4>🚨 促销效果不佳警告</h4>
            <p>当前促销活动未能有效提升销售，需要全面改进促销策略。</p>
            <p><strong>改进建议：</strong></p>
            <ul>
                <li>全面评估促销活动设计，找出低效环节</li>
                <li>调整促销形式和力度，提高吸引力</li>
                <li>重新定位促销目标客户群，提高针对性</li>
                <li>改进促销时机选择，避开淡季和不利因素</li>
                <li>强化促销执行管理，确保活动落地效果</li>
            </ul>
            """, unsafe_allow_html=True)
        elif promotion_growth < 20:
            st.markdown("""
            <h4>⚠️ 促销效果有限提示</h4>
            <p>当前促销活动效果一般，销售提升空间有限，需要优化促销策略。</p>
            <p><strong>优化建议：</strong></p>
            <ul>
                <li>分析高效促销活动特点，总结成功经验</li>
                <li>优化促销品类选择，聚焦高增长潜力产品</li>
                <li>调整促销力度和形式，提高性价比</li>
                <li>加强促销宣传和推广，扩大影响范围</li>
                <li>建立促销效果评估机制，持续改进</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <h4>✅ 促销效果显著</h4>
            <p>当前促销活动效果显著，有效提升了销售业绩，建议持续优化。</p>
            <p><strong>持续优化建议：</strong></p>
            <ul>
                <li>维持现有成功促销策略，持续复制推广</li>
                <li>精细化活动规划，进一步提高投入产出比</li>
                <li>尝试创新促销形式，保持市场新鲜感</li>
                <li>加强促销与其他营销活动的协同，形成合力</li>
                <li>建立促销效果预测模型，指导未来活动规划</li>
            </ul>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无足够数据提供促销策略建议")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:  # ROI分析
    st.subheader("💲 投入产出分析")

    # 物料和促销投入产出比较
    if material_efficiency:
        material_roi = material_efficiency.get('material_roi', 0)
        promotion_roi = material_efficiency.get('promotion_roi', 0)

        # 创建ROI对比柱状图
        roi_data = pd.DataFrame({
            '投入类型': ['物料投入', '促销活动'],
            'ROI': [material_roi, promotion_roi]
        })

        fig = px.bar(
            roi_data,
            x='投入类型',
            y='ROI',
            title="物料vs促销投入ROI对比",
            color='投入类型',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
            text='ROI'
        )

        fig.update_traces(
            texttemplate='%{y:.2f}',
            textposition='outside'
        )

        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="投入类型",
            yaxis_title="投入回报率(ROI)",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        roi_diff = material_roi - promotion_roi
        better_type = "物料投入" if roi_diff > 0 else "促销活动"

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 物料投入ROI为{material_roi:.2f}，促销活动ROI为{promotion_roi:.2f}，{'二者差异不大。' if abs(roi_diff) < 1 else f'{better_type}的投入产出效率更高。'}
            {'总体投入产出效率良好，资源配置合理。' if min(material_roi, promotion_roi) >= 3 else '部分投入效率不高，需要优化资源配置。'}
        </div>
        """, unsafe_allow_html=True)

        # 费用与销售对比分析
        st.markdown('<div class="sub-header">📊 费用与销售关系分析</div>', unsafe_allow_html=True)

        # 创建费用与销售关系散点图
        monthly_expense = material_analysis.get('monthly_expense', pd.DataFrame())

        if not monthly_expense.empty:
            # 获取月度销售数据
            sales_data = filtered_data.get('sales_orders', pd.DataFrame())
            monthly_sales = pd.DataFrame()

            if not sales_data.empty and '发运月份' in sales_data.columns and '销售额' in sales_data.columns:
                sales_data['月份'] = pd.to_datetime(sales_data['发运月份']).dt.strftime('%Y-%m')
                monthly_sales = sales_data.groupby('月份')['销售额'].sum().reset_index()

            if not monthly_sales.empty:
                # 合并费用和销售数据
                expense_sales = monthly_expense.merge(
                    monthly_sales,
                    on='月份',
                    how='inner'
                )

                if not expense_sales.empty:
                    # 计算总费用
                    if '物料费用' in expense_sales.columns and '促销费用' in expense_sales.columns:
                        expense_sales['总费用'] = expense_sales['物料费用'] + expense_sales['促销费用']

                    # 创建费用与销售散点图
                    fig = px.scatter(
                        expense_sales,
                        x='总费用',
                        y='销售额',
                        title="费用投入与销售关系",
                        text='月份',
                        size='总费用',
                        color='月份',
                        trendline='ols'
                    )

                    fig.update_traces(
                        textposition='top center'
                    )

                    fig.update_layout(
                        height=500,
                        margin=dict(l=50, r=50, t=60, b=50),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        xaxis_title="总费用投入（元）",
                        yaxis_title="销售额（元）"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 计算相关系数
                    correlation = expense_sales['总费用'].corr(expense_sales['销售额'])

                    # 图表解读
                    corr_strength = "强" if abs(correlation) > 0.7 else "中等" if abs(correlation) > 0.4 else "弱"
                    corr_direction = "正相关" if correlation > 0 else "负相关"

                    st.markdown(f"""
                    <div class="chart-explanation">
                        <b>图表解读：</b> 费用投入与销售额呈{corr_strength}{corr_direction}关系（相关系数{correlation:.2f}）。
                        {'费用投入对销售有显著促进作用，投入产出效率良好。' if correlation > 0.7 else '费用投入对销售有一定促进作用，但并非唯一决定因素。' if correlation > 0 else '费用投入与销售关系不明显，需要重新评估费用投入策略。'}
                    </div>
                    """, unsafe_allow_html=True)

        # 投入产出优化建议
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

        if material_roi < 3 and promotion_roi < 3:
            st.markdown("""
            <h4>🚨 投入产出效率低警告</h4>
            <p>当前物料和促销投入产出效率均较低，需要全面改进资源配置策略。</p>
            <p><strong>优化建议：</strong></p>
            <ul>
                <li>全面评估投入结构，重点分析低效环节</li>
                <li>建立投入产出评估机制，淘汰低效投入项目</li>
                <li>优化投入时机和力度，提高针对性和协同性</li>
                <li>精细化资源分配，向高效区域和客户倾斜</li>
                <li>加强费用管控，降低无效投入</li>
            </ul>
            """, unsafe_allow_html=True)
        elif material_roi > promotion_roi:
            st.markdown(f"""
            <h4>⚠️ 投入结构调整建议</h4>
            <p>物料投入ROI({material_roi:.2f})高于促销活动ROI({promotion_roi:.2f})，建议优化投入结构。</p>
            <p><strong>调整建议：</strong></p>
            <ul>
                <li>适当增加物料投入比例，优化投入结构</li>
                <li>改进促销活动策划和执行，提高促销效率</li>
                <li>分析高效物料类型，重点投入高回报物料</li>
                <li>建立物料与促销协同机制，形成营销合力</li>
                <li>持续跟踪投入效果，动态调整资源配置</li>
            </ul>
            """, unsafe_allow_html=True)
        elif promotion_roi > material_roi:
            st.markdown(f"""
            <h4>⚠️ 投入结构调整建议</h4>
            <p>促销活动ROI({promotion_roi:.2f})高于物料投入ROI({material_roi:.2f})，建议优化投入结构。</p>
            <p><strong>调整建议：</strong></p>
            <ul>
                <li>适当增加促销活动投入比例，优化投入结构</li>
                <li>改进物料投放策略，提高物料使用效率</li>
                <li>分析高效促销类型，重点投入高回报促销活动</li>
                <li>建立物料与促销协同机制，形成营销合力</li>
                <li>持续跟踪投入效果，动态调整资源配置</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <h4>✅ 投入产出效率良好</h4>
            <p>物料投入ROI({material_roi:.2f})和促销活动ROI({promotion_roi:.2f})均处于良好水平，投入结构较为合理。</p>
            <p><strong>持续优化建议：</strong></p>
            <ul>
                <li>保持现有投入结构，持续优化细节</li>
                <li>定期评估投入效果，及时调整资源配置</li>
                <li>尝试创新投入方式，进一步提高效率</li>
                <li>建立投入产出预测模型，指导未来投入决策</li>
                <li>完善投入绩效评估体系，激励高效投入</li>
            </ul>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无投入产出分析数据")

# 物料洞察总结
st.subheader("💡 物料与促销洞察总结")

# 生成洞察内容
total_material_expense = material_analysis.get('total_material_expense', 0)
total_promotion_expense = material_analysis.get('total_promotion_expense', 0)
material_efficiency = material_analysis.get('material_efficiency', {})
material_expense_ratio = material_efficiency.get('material_expense_ratio', 0)
promotion_expense_ratio = material_efficiency.get('promotion_expense_ratio', 0)
material_roi = material_efficiency.get('material_roi', 0)
promotion_roi = material_efficiency.get('promotion_roi', 0)
promotion_effect = material_analysis.get('promotion_effect', {})
promotion_growth = promotion_effect.get('promotion_growth', 0) if promotion_effect else 0

# 综合评估
if (material_roi >= 5 and promotion_roi >= 5) or (promotion_growth > 20):
    efficiency = "优秀"
    efficiency_color = COLORS['success']
    efficiency_advice = "保持现有物料和促销策略，持续优化细节以提升效率"
elif (material_roi >= 3 and promotion_roi >= 3) or (promotion_growth > 0):
    efficiency = "良好"
    efficiency_color = COLORS['success']
    efficiency_advice = "整体策略有效，可在细节上进一步优化以提高投入产出比"
elif (material_roi >= 1 and promotion_roi >= 1) or (promotion_growth > -10):
    efficiency = "一般"
    efficiency_color = COLORS['warning']
    efficiency_advice = "投入产出效率中等，需改进费用结构和使用策略以提高回报"
else:
    efficiency = "欠佳"
    efficiency_color = COLORS['danger']
    efficiency_advice = "投入产出效率低，需重新评估物料和促销策略，优化资源配置"

st.markdown(f"""
<div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
            padding: 1rem; border-radius: 0.5rem;">
    <h4>📋 物料与促销分析总结</h4>
    <p><strong>费用规模：</strong>物料总费用{format_currency(total_material_expense)}，促销总费用{format_currency(total_promotion_expense)}，合计{format_currency(total_material_expense + total_promotion_expense)}。</p>
    <p><strong>费用比例：</strong>物料费用率{format_percentage(material_expense_ratio)}，促销费用率{format_percentage(promotion_expense_ratio)}，合计占销售比例{format_percentage(material_expense_ratio + promotion_expense_ratio)}。</p>
    <p><strong>投入产出：</strong>物料投入ROI为{material_roi:.2f}，促销活动ROI为{promotion_roi:.2f}，{'物料投入效率更高' if material_roi > promotion_roi else '促销活动效率更高' if promotion_roi > material_roi else '二者效率相当'}。</p>
    <p><strong>促销效果：</strong>{'促销期间销售{'增长' if promotion_growth >= 0 else '下降'}{format_percentage(abs(promotion_growth))}' if promotion_growth != 0 else '无法评估促销效果'}。</p>
    <p><strong>综合评价：</strong><span style="color: {efficiency_color};">{efficiency}</span>。{efficiency_advice}。</p>
</div>
""", unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)