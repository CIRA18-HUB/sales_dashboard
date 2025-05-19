# pages/customer_page.py
# 客户分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.customer import (
    analyze_customer_data, get_customer_insights, 
    get_customer_dependency_level, create_customer_pareto_chart,
    create_customer_bubble_chart
)
from utils.helpers import (
    create_metric_card, create_pie_chart, create_stacked_bar, generate_insight
)
from config import COLOR_THEME

def show_customer_page(data, filters):
    """
    显示客户分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("客户分析")
    
    # 分析客户数据
    customer_result = analyze_customer_data(
        data['sales_orders'],
        data['customer_relations'],
        data['customer_target']
    )
    
    if not customer_result['success']:
        st.error(f"客户数据分析失败: {customer_result['message']}")
        return
    
    # 获取关键指标
    total_customers = customer_result['total_customers']
    top1_percentage = customer_result['top1_percentage']
    top5_percentage = customer_result['top5_percentage']
    top10_percentage = customer_result['top10_percentage']
    
    # 计算客户依赖程度
    dependency_level, dependency_desc = get_customer_dependency_level(top1_percentage, top5_percentage)
    
    # 渠道分析
    channel_data = customer_result['channel_customer_sales']
    mt_sales = channel_data[channel_data['渠道'] == 'MT']['求和项:金额（元）'].sum()
    tt_sales = channel_data[channel_data['渠道'] == 'TT']['求和项:金额（元）'].sum()
    total_sales = mt_sales + tt_sales
    
    mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
    tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0
    
    # 客户月度变化分析
    monthly_customer_count = customer_result['monthly_customer_count']
    if len(monthly_customer_count) >= 2:
        latest_count = monthly_customer_count.iloc[-1]['客户数量']
        previous_count = monthly_customer_count.iloc[-2]['客户数量']
        count_change = latest_count - previous_count
    else:
        count_change = 0
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "活跃客户数", 
                total_customers, 
                count_change
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "客户依赖度", 
                None, 
                None, 
                is_percentage=False,
                prefix=dependency_level
            ), 
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            create_metric_card(
                "TOP5客户占比",
                top5_percentage,
                None,
                is_percentage=True
            ),
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            create_metric_card(
                "MT/TT占比",
                mt_percentage,
                None,
                is_percentage=True,
                suffix="/TT" + f"{tt_percentage:.1f}%"
            ),
            unsafe_allow_html=True
        )

    # 分隔符
    st.markdown("---")

    # 第二行：客户帕累托图和客户价值矩阵
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("客户销售帕累托分析")

        # 创建客户帕累托图
        fig = create_customer_pareto_chart(customer_result['customer_sales'])

        st.plotly_chart(fig, use_container_width=True)

        # 大客户依赖度分析
        st.info(
            f"**客户依赖度分析：**\n\n"
            f"- 依赖级别: **{dependency_level}**\n"
            f"- 第一大客户占比: **{top1_percentage:.1f}%**\n"
            f"- TOP5客户占比: **{top5_percentage:.1f}%**\n"
            f"- TOP10客户占比: **{top10_percentage:.1f}%**\n\n"
            f"{dependency_desc}"
        )

    with col2:
        st.subheader("客户价值矩阵")

        # 创建客户价值矩阵（气泡图）
        fig = create_customer_bubble_chart(customer_result)

        st.plotly_chart(fig, use_container_width=True)

        # 客户多样性和忠诚度分析
        product_diversity = customer_result['customer_product_diversity']
        loyalty = customer_result['customer_loyalty']

        if not product_diversity.empty and not loyalty.empty:
            avg_products = product_diversity['产品数量'].mean()
            avg_months = loyalty['购买月份数'].mean()

            st.info(
                f"**客户价值分析：**\n\n"
                f"- 平均购买产品种类: **{avg_products:.1f}种**\n"
                f"- 平均购买月份数: **{avg_months:.1f}个月**\n"
                f"- 高价值客户特征: 购买产品多样化且长期活跃"
            )

    # 分隔符
    st.markdown("---")

    # 第三行：客户渠道分析和客户月度变化
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("客户渠道分析")

        # 创建渠道占比饼图
        channel_summary = pd.DataFrame({
            '渠道': ['MT渠道', 'TT渠道'],
            '销售额': [mt_sales, tt_sales]
        })

        fig = create_pie_chart(
            channel_summary,
            '渠道',
            '销售额',
            '客户渠道销售占比'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 计算各渠道的客户数量
        mt_customers = channel_data[channel_data['渠道'] == 'MT']['客户代码'].nunique()
        tt_customers = channel_data[channel_data['渠道'] == 'TT']['客户代码'].nunique()

        # 创建渠道客户数量条形图
        channel_customers = pd.DataFrame({
            '渠道': ['MT渠道', 'TT渠道'],
            '客户数量': [mt_customers, tt_customers]
        })

        fig = px.bar(
            channel_customers,
            x='渠道',
            y='客户数量',
            title='各渠道客户数量',
            color='渠道',
            color_discrete_map={
                'MT渠道': COLOR_THEME['primary'],
                'TT渠道': COLOR_THEME['secondary']
            },
            text_auto=True
        )

        fig.update_layout(
            xaxis_title='渠道',
            yaxis_title='客户数量',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("客户月度变化")

        # 创建客户数量变化趋势图
        fig = px.line(
            monthly_customer_count,
            x='月份',
            y='客户数量',
            markers=True,
            title='月度活跃客户数变化趋势'
        )

        fig.update_layout(
            xaxis_title='月份',
            yaxis_title='客户数量',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 客户状态分析
        customer_status = customer_result['customer_status']

        if customer_status is not None and not customer_status.empty:
            # 创建客户状态饼图
            fig = create_pie_chart(
                customer_status,
                '状态',
                '客户数量',
                '客户状态分布'
            )

            st.plotly_chart(fig, use_container_width=True)

    # 分隔符
    st.markdown("---")

    # 第四行：客户洞察
    st.subheader("客户洞察分析")

    customer_insights = get_customer_insights(customer_result)
    st.info(customer_insights)

    # 分隔符
    st.markdown("---")

    # 第五行：客户目标达成分析（点击展开）
    with st.expander("客户目标达成分析"):
        customer_achievement = customer_result['customer_achievement']

        if customer_achievement is not None and not customer_achievement.empty:
            # 处理可能的缺失值
            customer_achievement['达成率'].fillna(0, inplace=True)

            # 计算每个客户的平均达成率
            customer_avg_achievement = customer_achievement.groupby('客户')['达成率'].mean().reset_index()
            customer_avg_achievement = customer_avg_achievement.sort_values('达成率', ascending=False)

            # 创建客户达成率条形图
            fig = px.bar(
                customer_avg_achievement.head(20),
                y='客户',
                x='达成率',
                orientation='h',
                title='TOP20客户目标达成率',
                color='达成率',
                color_continuous_scale=[
                    [0, 'red'],
                    [0.7, 'yellow'],
                    [0.9, 'lightgreen'],
                    [1, 'green']
                ],
                text_auto='.0%'
            )

            fig.update_layout(
                xaxis_title='达成率',
                yaxis_title='客户',
                height=600,
                xaxis=dict(
                    tickformat='.0%'
                )
            )

            # 添加100%基准线
            fig.add_shape(
                type="line",
                x0=1, y0=-0.5, x1=1, y1=len(customer_avg_achievement.head(20)) - 0.5,
                line=dict(color="red", width=2, dash="dash")
            )

            st.plotly_chart(fig, use_container_width=True)

            # 客户月度达成率热力图
            # 透视表转换数据格式
            pivot_data = customer_achievement.pivot(
                index='客户',
                columns='月份',
                values='达成率'
            ).reset_index()

            # 选择TOP10客户
            top_customers = customer_result['customer_sales'].head(10)['客户简称'].tolist()
            pivot_data = pivot_data[pivot_data['客户'].isin(top_customers)]

            # 获取月份列表
            months = sorted([col for col in pivot_data.columns if isinstance(col, pd.Timestamp)])

            # 创建热力图数据
            z_data = []
            y_data = []

            for _, row in pivot_data.iterrows():
                y_data.append(row['客户'])
                row_data = []
                for month in months:
                    row_data.append(row[month])
                z_data.append(row_data)

            # 创建热力图
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=[month.strftime('%Y-%m') for month in months],
                y=y_data,
                colorscale=[
                    [0, 'red'],
                    [0.7, 'yellow'],
                    [0.9, 'lightgreen'],
                    [1, 'green']
                ],
                showscale=True,
                text=z_data,
                texttemplate="%{text:.0%}",
                textfont={"size": 10},
            ))

            fig.update_layout(
                title='TOP10客户月度达成率热力图',
                xaxis=dict(title='月份'),
                yaxis=dict(title='客户'),
                margin=dict(l=50, r=50, t=80, b=50),
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("没有客户目标数据，无法进行客户目标达成分析。")