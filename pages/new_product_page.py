# pages/new_product_page.py
# 新品分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.new_product import (
    analyze_new_product_data, get_new_product_insights,
    create_new_product_trend_chart, create_new_product_performance_chart,
    create_new_product_region_chart, create_new_product_growth_chart
)
from utils.helpers import (
    create_metric_card, create_pie_chart, create_stacked_bar, generate_insight
)
from config import COLOR_THEME

def show_new_product_page(data, filters):
    """
    显示新品分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("新品分析")
    
    # 分析新品数据
    new_product_result = analyze_new_product_data(
        data['sales_orders'],
        data['new_product_codes'],
        data['promotion_data']
    )
    
    if not new_product_result['success']:
        st.error(f"新品数据分析失败: {new_product_result['message']}")
        return
    
    # 获取关键指标
    new_product_total_sales = new_product_result['new_product_total_sales']
    new_product_percentage = new_product_result['new_product_percentage']
    product_summary = new_product_result['product_summary']
    total_new_products = len(product_summary)
    
    # 计算最近一个月的增长率
    monthly_sales = new_product_result['monthly_sales']
    if len(monthly_sales) >= 2:
        latest_month = monthly_sales.iloc[-1]
        growth_rate = latest_month['环比增长率'] * 100 if not pd.isna(latest_month['环比增长率']) else 0
    else:
        growth_rate = 0
    
    # 渠道分析
    channel_sales = new_product_result['channel_sales']
    mt_percentage = channel_sales[channel_sales['渠道'] == 'MT渠道']['销售占比'].values[0] if not channel_sales.empty else 0
    tt_percentage = channel_sales[channel_sales['渠道'] == 'TT渠道']['销售占比'].values[0] if not channel_sales.empty else 0
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "新品销售总额", 
                new_product_total_sales, 
                None, 
                is_currency=True
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "新品销售占比", 
                new_product_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                "新品数量", 
                total_new_products, 
                None
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            create_metric_card(
                "月环比增长", 
                growth_rate, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第二行：新品销售趋势和新品性能
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新品销售趋势")
        
        # 创建新品销售趋势图
        fig = create_new_product_trend_chart(monthly_sales)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 新品销售趋势洞察
        if len(monthly_sales) >= 2:
            latest_month = monthly_sales.iloc[-1]
            previous_month = monthly_sales.iloc[-2]
            latest_sales = latest_month['求和项:金额（元）']
            previous_sales = previous_month['求和项:金额（元）']
            sales_change = latest_sales - previous_sales
            change_percentage = (sales_change / previous_sales) * 100 if previous_sales > 0 else 0
            
            trend_insight = generate_insight(
                monthly_sales,
                "新品月度销售额",
                latest_sales,
                sales_change,
                None
            )
            
            st.info(trend_insight)
    
    with col2:
        st.subheader("新品销售表现")
        
        # 创建新品性能对比图
        fig = create_new_product_performance_chart(product_summary)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # TOP3新品表现分析
        if not product_summary.empty:
            top3 = product_summary.head(3)
            
            top3_html = ""
            for i, (_, row) in enumerate(top3.iterrows()):
                top3_html += f"{i+1}. **{row['产品简称']}**: ¥{row['求和项:金额（元）']:,.2f} ({row['占新品销售比例']:.1f}%)<br>"
            
            st.markdown(
                f"**TOP3新品表现：**<br>{top3_html}",
                unsafe_allow_html=True
            )
    
    # 分隔符
    st.markdown("---")
    
    # 第三行：新品区域分布和渠道分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新品区域分布")
        
        # 创建新品区域分布图
        fig = create_new_product_region_chart(new_product_result['region_sales'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 区域分布分析
        region_sales = new_product_result['region_sales']
        
        if not region_sales.empty:
            top_region = region_sales.iloc[0]
            top_region_percentage = top_region['求和项:金额（元）'] / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
            
            st.info(
                f"**区域分布分析：**\n\n"
                f"- 销售额最高的区域: **{top_region['所属区域']}**\n"
                f"- 占新品总销售额: **{top_region_percentage:.1f}%**\n"
                f"- 区域销售额: **¥{top_region['求和项:金额（元）']:,.2f}**"
            )
    
    with col2:
        st.subheader("新品渠道分布")
        
        # 创建渠道分布饼图
        fig = create_pie_chart(
            channel_sales,
            '渠道',
            '销售额',
            '新品渠道销售分布'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 渠道分布分析
        st.info(
            f"**渠道分布分析：**\n\n"
            f"- MT渠道占比: **{mt_percentage:.1f}%**\n"
            f"- TT渠道占比: **{tt_percentage:.1f}%**\n"
            f"- 主要销售渠道: **{'MT渠道' if mt_percentage > tt_percentage else 'TT渠道'}**"
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第四行：新品增长曲线和客户分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新品增长曲线")
        
        # 创建新品增长曲线图
        fig = create_new_product_growth_chart(new_product_result['monthly_product_sales'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 新品上市时间分析
        new_product_age = new_product_result.get('new_product_age', {})
        
        if new_product_age:
            avg_age = sum(new_product_age.values()) / len(new_product_age)
            newest_product = min(new_product_age.items(), key=lambda x: x[1])
            oldest_product = max(new_product_age.items(), key=lambda x: x[1])
            
            st.info(
                f"**新品上市时间分析：**\n\n"
                f"- 平均上市时间: **{avg_age:.0f}天**\n"
                f"- 最新上市产品: **{newest_product[0]}** ({newest_product[1]}天)\n"
                f"- 上市最长产品: **{oldest_product[0]}** ({oldest_product[1]}天)"
            )
    
    with col2:
        st.subheader("新品客户分布")
        
        # 客户分布分析
        customer_sales = new_product_result['customer_sales']
        
        if not customer_sales.empty:
            # 创建TOP10客户条形图
            fig = px.bar(
                customer_sales.head(10),
                y='客户简称',
                x='求和项:金额（元）',
                orientation='h',
                title='新品TOP10客户',
                color='求和项:金额（元）',
                color_continuous_scale=px.colors.sequential.Blues,
                text_auto='.2s'
            )
            
            fig.update_layout(
                xaxis_title='销售额 (元)',
                yaxis_title='客户',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # TOP客户分析
            top_customer = customer_sales.iloc[0]
            top_customer_percentage = top_customer['求和项:金额（元）'] / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
            
            st.info(
                f"**TOP客户分析：**\n\n"
                f"- 销售额最高的客户: **{top_customer['客户简称']}**\n"
                f"- 占新品总销售额: **{top_customer_percentage:.1f}%**\n"
                f"- 客户销售额: **¥{top_customer['求和项:金额（元）']:,.2f}**"
            )
        else:
            st.info("没有新品客户数据。")
    
    # 分隔符
    st.markdown("---")
    
    # 第五行：新品洞察
    st.subheader("新品洞察分析")
    
    new_product_insights = get_new_product_insights(new_product_result)
    st.info(new_product_insights)
    
    # 分隔符
    st.markdown("---")
    
    # 第六行：新品促销分析（点击展开）
    with st.expander("新品促销分析"):
        promotion_analysis = new_product_result.get('promotion_analysis')
        
        if promotion_analysis is not None and not promotion_analysis.empty:
            # 创建促销效果条形图
            fig = px.bar(
                promotion_analysis.head(10),
                y='产品名称',
                x='促销效果',
                orientation='h',
                title='新品促销效果TOP10',
                color='促销效果',
                color_continuous_scale=px.colors.sequential.Blues,
                text_auto='.2s'
            )
            
            fig.update_layout(
                xaxis_title='促销效果 (平均每次促销带来的销售额)',
                yaxis_title='产品',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 促销活动统计
            total_promotions = promotion_analysis['促销活动次数'].sum()
            total_expected_sales = promotion_analysis['预计销售额（元）'].sum()
            avg_effect = total_expected_sales / total_promotions if total_promotions > 0 else 0
            
            st.info(
                f"**促销活动统计：**\n\n"
                f"- 总促销活动次数: **{total_promotions}**\n"
                f"- 预计总促销销售额: **¥{total_expected_sales:,.2f}**\n"
                f"- 平均促销效果: **¥{avg_effect:,.2f}**"
            )
            
            # 促销建议
            st.success(
                "**新品促销建议：**\n\n"
                "1. 加大促销效果好的新品推广力度\n"
                "2. 考虑多渠道推广，提高新品知名度\n"
                "3. 结合区域特点，制定差异化促销策略\n"
                "4. 收集客户反馈，及时调整产品和促销方式"
            )
        else:
            st.info("没有新品促销活动数据。")