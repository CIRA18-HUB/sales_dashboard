# pages/overview.py
# 总览页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入工具函数
from utils.helpers import (
    create_metric_card, create_heatmap, create_pie_chart, 
    create_stacked_bar, create_line_chart, generate_insight
)
from utils.data_loader import categorize_products
from utils.constants import BCG_QUADRANTS, CHANNEL_TYPES, GLOSSARY
from config import COLOR_THEME


def show_overview_page(data, filters):
    """
    显示总览页面

    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("销售数据总览")

    # 获取当前日期
    current_year = datetime.now().year
    current_month = datetime.now().month

    # 检查sales_orders是否存在，如果不存在但sales_data存在，则创建sales_orders
    if 'sales_orders' not in data and 'sales_data' in data and not data['sales_data'].empty:
        # 过滤销售数据（只包括订单-正常产品和订单-TT产品）
        data['sales_orders'] = data['sales_data'][
            data['sales_data']['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

    # 如果sales_orders仍不存在，显示消息并返回
    if 'sales_orders' not in data:
        st.info("请先在侧边栏中点击「加载筛选数据」按钮加载基础数据")
        return

    # 过滤销售数据（只包括订单-正常产品和订单-TT产品）
    sales_data = data['sales_orders']

    # 根据筛选条件过滤数据
    if filters.get('region'):
        sales_data = sales_data[sales_data['所属区域'] == filters['region']]

    if filters.get('sales_person'):
        sales_data = sales_data[sales_data['申请人'] == filters['sales_person']]

    if filters.get('customer'):
        # 先尝试匹配客户代码
        customer_match = sales_data['客户代码'] == filters['customer']
        # 再尝试匹配客户简称或经销商名称
        if customer_match.sum() == 0:
            customer_match = (
                    (sales_data['客户简称'] == filters['customer']) |
                    (sales_data['经销商名称'] == filters['customer'])
            )
        sales_data = sales_data[customer_match]

    if filters.get('product'):
        # 先尝试匹配产品代码
        product_match = sales_data['产品代码'] == filters['product']
        # 再尝试匹配产品简称或产品名称
        if product_match.sum() == 0:
            product_match = (
                    (sales_data['产品简称'] == filters['product']) |
                    (sales_data['产品名称'] == filters['product'])
            )
        sales_data = sales_data[product_match]

    if filters.get('date_range') and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        sales_data = sales_data[
            (sales_data['发运月份'] >= pd.Timestamp(start_date)) &
            (sales_data['发运月份'] <= pd.Timestamp(end_date))
            ]

    # 计算关键指标
    total_sales = sales_data['求和项:金额（元）'].sum()
    total_quantity = sales_data['求和项:数量（箱）'].sum()

    # 计算MT和TT渠道销售额
    mt_sales = sales_data[sales_data['订单类型'] == '订单-正常产品']['求和项:金额（元）'].sum()
    tt_sales = sales_data[sales_data['订单类型'] == '订单-TT产品']['求和项:金额（元）'].sum()

    # 计算目标达成率（这里使用模拟数据）
    # 在实际应用中，应从目标数据中获取相应的目标值
    sales_target = 10000000  # 示例目标值
    achievement_rate = total_sales / sales_target if sales_target > 0 else 0

    # 增长计算（假设前一期间的销售额）
    # 在实际应用中，应计算与上年同期的对比
    prev_period_sales = total_sales * 0.9  # 示例前一期间销售额
    sales_growth = (total_sales - prev_period_sales) / prev_period_sales if prev_period_sales > 0 else 0

    # 创建第一行卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            create_metric_card(
                "销售总额",
                total_sales,
                sales_growth * 100,
                is_currency=True
            ),
            unsafe_allow_html=True
        )

        if st.button("深入分析销售总额", key="sales_total_analysis"):
            st.session_state.selected_tab = 1  # 跳转到销售分析页
            st.experimental_rerun()

    with col2:
        st.markdown(
            create_metric_card(
                "目标达成率",
                achievement_rate * 100,
                None,
                is_percentage=True
            ),
            unsafe_allow_html=True
        )

        if st.button("深入分析目标达成", key="target_achievement_analysis"):
            st.session_state.selected_tab = 1  # 跳转到销售分析页
            st.experimental_rerun()

    with col3:
        st.markdown(
            create_metric_card(
                "总销售数量",
                total_quantity,
                None
            ),
            unsafe_allow_html=True
        )

    with col4:
        mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
        tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0

        st.markdown(
            create_metric_card(
                "MT/TT渠道占比",
                mt_percentage,
                None,
                is_percentage=True,
                suffix="/TT" + f"{tt_percentage:.1f}%"
            ),
            unsafe_allow_html=True
        )

        if st.button("深入分析渠道占比", key="channel_analysis"):
            st.session_state.selected_tab = 2  # 跳转到客户分析页
            st.experimental_rerun()

    # 分隔符
    st.markdown("---")

    # 第二行：BCG矩阵和TOP客户
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("产品BCG矩阵分析")

        # 计算产品BCG象限
        product_bcg = categorize_products(sales_data, data['product_codes'])

        # 计算每个象限的产品数量
        bcg_counts = product_bcg['产品类型'].value_counts().reset_index()
        bcg_counts.columns = ['象限', '产品数量']

        # 计算每个象限的销售额
        bcg_sales = product_bcg.groupby('产品类型')['求和项:金额（元）'].sum().reset_index()
        bcg_sales.columns = ['象限', '销售额']

        # 合并数量和销售额
        bcg_summary = pd.merge(bcg_counts, bcg_sales, on='象限')

        # 计算销售占比
        bcg_summary['销售占比'] = bcg_summary['销售额'] / bcg_summary['销售额'].sum()

        # 创建饼图
        fig = create_pie_chart(
            bcg_summary,
            '象限',
            '销售额',
            'BCG产品组合销售占比',
            {
                '现金牛产品': COLOR_THEME['success'],
                '明星产品': COLOR_THEME['primary'],
                '问号产品': COLOR_THEME['secondary'],
                '瘦狗产品': COLOR_THEME['warning']
            }
        )

        st.plotly_chart(fig, use_container_width=True)

        # BCG矩阵目标达成评估
        cash_cow_percentage = bcg_summary[bcg_summary['象限'] == '现金牛产品']['销售占比'].sum() * 100
        star_question_percentage = bcg_summary[
                                       bcg_summary['象限'].isin(['明星产品', '问号产品'])
                                   ]['销售占比'].sum() * 100
        dog_percentage = bcg_summary[bcg_summary['象限'] == '瘦狗产品']['销售占比'].sum() * 100

        st.info(
            f"**JBP计划产品模型目标评估：**\n\n"
            f"- 现金牛产品占比: **{cash_cow_percentage:.1f}%** (目标: 45%-50%)\n"
            f"- 明星和问号产品占比: **{star_question_percentage:.1f}%** (目标: 40%-45%)\n"
            f"- 瘦狗产品占比: **{dog_percentage:.1f}%** (目标: ≤10%)"
        )

        # 添加按钮，点击跳转到产品分析页面
        if st.button("深入分析产品组合", key="product_mix_analysis"):
            st.session_state.selected_tab = 3  # 跳转到产品分析页
            st.experimental_rerun()

    with col2:
        st.subheader("TOP10客户分析")

        # 计算每个客户的销售额
        customer_sales = sales_data.groupby(['客户代码', '客户简称', '经销商名称'])[
            '求和项:金额（元）'].sum().reset_index()
        customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False).head(10)

        # 计算TOP10客户占总销售额的比例
        top10_sales = customer_sales['求和项:金额（元）'].sum()
        top10_percentage = top10_sales / total_sales * 100 if total_sales > 0 else 0

        # 创建水平条形图
        fig = px.bar(
            customer_sales,
            y='客户简称',
            x='求和项:金额（元）',
            orientation='h',
            title=f'TOP10客户销售额 (占总销售额的{top10_percentage:.1f}%)',
            color='求和项:金额（元）',
            color_continuous_scale=px.colors.sequential.Blues,
            text_auto='.2s'
        )

        fig.update_layout(
            xaxis_title="销售额 (元)",
            yaxis_title="客户",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 客户依赖度分析
        top1_percentage = customer_sales.iloc[0]['求和项:金额（元）'] / total_sales * 100 if total_sales > 0 else 0
        top5_percentage = customer_sales.head(5)['求和项:金额（元）'].sum() / total_sales * 100 if total_sales > 0 else 0

        dependency_level = "高" if top5_percentage > 50 else "中" if top5_percentage > 30 else "低"

        st.info(
            f"**客户依赖度分析：**\n\n"
            f"- 第一大客户占比: **{top1_percentage:.1f}%**\n"
            f"- TOP5客户占比: **{top5_percentage:.1f}%**\n"
            f"- 客户依赖度: **{dependency_level}**"
        )

        # 添加按钮，点击跳转到客户分析页面
        if st.button("深入分析客户结构", key="customer_structure_analysis"):
            st.session_state.selected_tab = 2  # 跳转到客户分析页
            st.experimental_rerun()

    # 分隔符
    st.markdown("---")

    # 第三行：销售趋势和库存预警
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("销售趋势分析")

        # 按月分组计算销售额
        monthly_sales = sales_data.groupby(pd.Grouper(key='发运月份', freq='M'))['求和项:金额（元）'].sum().reset_index()

        # 区分MT和TT渠道的月度销售额
        mt_monthly_sales = sales_data[sales_data['订单类型'] == '订单-正常产品'].groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        mt_monthly_sales['渠道'] = 'MT'

        tt_monthly_sales = sales_data[sales_data['订单类型'] == '订单-TT产品'].groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        tt_monthly_sales['渠道'] = 'TT'

        # 合并MT和TT渠道数据
        channel_monthly_sales = pd.concat([mt_monthly_sales, tt_monthly_sales])

        # 创建折线图
        fig = create_line_chart(
            channel_monthly_sales,
            '发运月份',
            '求和项:金额（元）',
            '渠道',
            '月度销售趋势(按渠道)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 销售趋势洞察
        if len(monthly_sales) >= 2:
            latest_month_sales = monthly_sales.iloc[-1]['求和项:金额（元）']
            previous_month_sales = monthly_sales.iloc[-2]['求和项:金额（元）']
            mom_change = (
                                     latest_month_sales - previous_month_sales) / previous_month_sales if previous_month_sales > 0 else 0

            trend_insight = generate_insight(
                monthly_sales,
                "最新月销售额",
                latest_month_sales,
                latest_month_sales - previous_month_sales,
                previous_month_sales
            )

            st.info(trend_insight)

        # 添加按钮，点击跳转到销售分析页面
        if st.button("深入分析销售趋势", key="sales_trend_analysis"):
            st.session_state.selected_tab = 1  # 跳转到销售分析页
            st.experimental_rerun()

    with col2:
        st.subheader("物料使用效率")

        # 使用物料使用效率数据
        # 这里使用简化的数据，实际应用中应使用物料使用效率分析结果
        # 创建模拟数据
        np.random.seed(42)

        # 从sales_data中随机选择5个产品
        if len(sales_data) > 0:
            sample_products = sales_data[['产品代码', '产品简称']].drop_duplicates().sample(
                min(5, len(sales_data[['产品代码', '产品简称']].drop_duplicates()))
            )

            product_codes = sample_products['产品代码'].tolist()
            product_names = sample_products['产品简称'].tolist()

            efficiency_data = pd.DataFrame({
                '产品代码': product_codes,
                '产品简称': product_names,
                '库存周转率': np.random.uniform(0.5, 2.5, len(product_codes)),
                '库存覆盖天数': np.random.uniform(30, 180, len(product_codes))
            })

            # 创建水平条形图
            fig = px.bar(
                efficiency_data,
                y='产品简称',
                x='库存周转率',
                orientation='h',
                title='产品库存周转率',
                color='库存周转率',
                color_continuous_scale=px.colors.sequential.Blues,
                text_auto='.2f'
            )

            fig.update_layout(
                xaxis_title="库存周转率",
                yaxis_title="产品",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # 库存效率洞察
            avg_turnover = efficiency_data['库存周转率'].mean()
            avg_coverage = efficiency_data['库存覆盖天数'].mean()

            st.info(
                f"**物料使用效率分析：**\n\n"
                f"- 平均库存周转率: **{avg_turnover:.2f}**\n"
                f"- 平均库存覆盖天数: **{avg_coverage:.0f}天**\n"
                f"- 建议: {get_turnover_advice(avg_turnover)}"
            )
        else:
            st.warning("没有足够的数据进行物料使用效率分析。")

        # 添加按钮，点击跳转到物料分析页面
        if st.button("深入分析物料效率", key="material_efficiency_analysis"):
            st.session_state.selected_tab = 5  # 跳转到物料分析页
            st.experimental_rerun()

    # 名词解释部分
    with st.expander("名词解释"):
        for term, explanation in GLOSSARY.items():
            st.markdown(f"**{term}**: {explanation}")

def get_turnover_advice(turnover_rate):
    """根据周转率生成建议"""
    if turnover_rate < 0.8:
        return "库存周转率偏低，建议优化库存策略，加强销售力度或减少采购量。"
    elif turnover_rate < 1.2:
        return "库存周转率一般，可考虑针对低周转产品制定专项销售计划。"
    else:
        return "库存周转率良好，继续保持当前库存管理策略。"