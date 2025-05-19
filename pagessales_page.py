# pages/sales_page.py
# 销售分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.sales import (
    analyze_sales_data, get_sales_insights, 
    create_achievement_heatmap, create_sales_comparison_chart
)
from utils.helpers import (
    create_metric_card, create_line_chart, create_stacked_bar,
    create_pie_chart, create_gauge, generate_insight
)
from config import COLOR_THEME, ACHIEVEMENT_THRESHOLDS

def show_sales_page(data, filters):
    """
    显示销售分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("销售金额分析")
    
    # 分析销售数据
    sales_result = analyze_sales_data(
        data['sales_orders'],
        data['sales_target']
    )
    
    if not sales_result['success']:
        st.error(f"销售数据分析失败: {sales_result['message']}")
        return
    
    # 获取关键指标
    total_sales = sales_result['total_sales']
    
    # 目标达成分析
    achievement_data = sales_result['achievement_data']
    if achievement_data is not None:
        avg_achievement = achievement_data['达成率'].mean() * 100
    else:
        avg_achievement = 0
    
    # 渠道分析
    channel_sales = sales_result['channel_sales']
    mt_sales = channel_sales[channel_sales['渠道'] == 'MT渠道']['销售额'].values[0]
    tt_sales = channel_sales[channel_sales['渠道'] == 'TT渠道']['销售额'].values[0]
    
    mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
    tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0
    
    # 销售趋势分析
    monthly_sales = sales_result['monthly_sales']
    if len(monthly_sales) >= 2:
        latest_month_sales = monthly_sales.iloc[-1]['求和项:金额（元）']
        previous_month_sales = monthly_sales.iloc[-2]['求和项:金额（元）']
        mom_change = (latest_month_sales - previous_month_sales) / previous_month_sales if previous_month_sales > 0 else 0
        mom_change_percentage = mom_change * 100
    else:
        mom_change_percentage = 0
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "销售总额", 
                total_sales, 
                None, 
                is_currency=True
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "目标达成率", 
                avg_achievement, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                "MT渠道占比", 
                mt_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            create_metric_card(
                "环比增长", 
                mom_change_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第二行：销售趋势和渠道占比
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("销售趋势分析")
        
        # 创建月度销售趋势图
        fig = create_line_chart(
            monthly_sales,
            '发运月份',
            '求和项:金额（元）',
            title='月度销售趋势'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 生成趋势洞察
        trend_insight = generate_insight(
            monthly_sales,
            "月度销售额",
            latest_month_sales,
            latest_month_sales - previous_month_sales if len(monthly_sales) >= 2 else None,
            None
        )
        
        st.info(trend_insight)
    
    with col2:
        st.subheader("渠道销售分析")
        
        # 创建渠道占比饼图
        fig = create_pie_chart(
            channel_sales,
            '渠道',
            '销售额',
            'MT/TT渠道销售占比'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 创建月度渠道销售趋势
        channel_monthly_sales = sales_result['channel_monthly_sales']
        
        fig = create_line_chart(
            channel_monthly_sales,
            '发运月份',
            '求和项:金额（元）',
            '渠道',
            '月度渠道销售趋势'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 分隔符
    st.markdown("---")
    
    # 第三行：目标达成和区域分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("目标达成分析")
        
        if achievement_data is not None:
            # 创建目标达成热力图
            fig = create_achievement_heatmap(achievement_data)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 创建销售与目标对比图
            fig = create_sales_comparison_chart(sales_result)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("没有目标数据，无法进行目标达成分析。")
    
    with col2:
        st.subheader("区域销售分析")
        
        # 创建区域销售条形图
        region_sales = sales_result['region_sales']
        
        fig = px.bar(
            region_sales,
            x='所属区域',
            y='求和项:金额（元）',
            title='区域销售分布',
            color='求和项:金额（元）',
            color_continuous_scale=px.colors.sequential.Blues,
            text_auto='.2s'
        )
        
        fig.update_layout(
            xaxis_title='区域',
            yaxis_title='销售额 (元)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 区域达成率分析
        region_achievement = sales_result['region_achievement']
        
        if region_achievement is not None:
            # 处理可能的缺失值
            region_achievement['达成率'].fillna(0, inplace=True)
            
            # 创建区域达成率图表
            fig = px.bar(
                region_achievement,
                x='所属区域',
                y='达成率',
                color='达成率',
                title='区域销售目标达成率',
                color_continuous_scale=[
                    [0, 'red'],
                    [0.7, 'yellow'],
                    [0.9, 'lightgreen'],
                    [1, 'green']
                ],
                text_auto='.0%'
            )
            
            fig.update_layout(
                xaxis_title='区域',
                yaxis_title='达成率',
                height=400,
                yaxis=dict(
                    tickformat='.0%'
                )
            )
            
            # 添加100%基准线
            fig.add_shape(
                type="line",
                x0=-0.5, y0=1, x1=len(region_achievement['所属区域'].unique())-0.5, y1=1,
                line=dict(color="red", width=2, dash="dash")
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 分隔符
    st.markdown("---")
    
    # 第四行：销售洞察
    st.subheader("销售洞察分析")
    
    sales_insights = get_sales_insights(sales_result)
    st.info(sales_insights)
    
    # 分隔符
    st.markdown("---")
    
    # 第五行：销售人员分析（点击展开）
    with st.expander("销售人员分析"):
        salesperson_sales = sales_result['salesperson_sales']
        
        # 创建销售人员销售额条形图
        fig = px.bar(
            salesperson_sales.head(10),
            y='申请人',
            x='求和项:金额（元）',
            orientation='h',
            title='TOP10销售人员销售额',
            color='求和项:金额（元）',
            color_continuous_scale=px.colors.sequential.Blues,
            text_auto='.2s'
        )
        
        fig.update_layout(
            xaxis_title='销售额 (元)',
            yaxis_title='销售人员',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 销售人员目标达成分析
        if achievement_data is not None:
            # 计算每个销售人员的平均达成率
            person_achievement = achievement_data.groupby('申请人')['达成率'].mean().reset_index()
            person_achievement = person_achievement.sort_values('达成率', ascending=False)
            
            # 创建销售人员达成率条形图
            fig = px.bar(
                person_achievement,
                y='申请人',
                x='达成率',
                orientation='h',
                title='销售人员目标达成率',
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
                yaxis_title='销售人员',
                height=500,
                xaxis=dict(
                    tickformat='.0%'
                )
            )
            
            # 添加100%基准线
            fig.add_shape(
                type="line",
                x0=1, y0=-0.5, x1=1, y1=len(person_achievement)-0.5,
                line=dict(color="red", width=2, dash="dash")
            )
            
            st.plotly_chart(fig, use_container_width=True)