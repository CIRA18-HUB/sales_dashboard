# pages/inventory_page.py
# 库存分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.inventory import (
    analyze_inventory_data, get_inventory_insights, 
    create_inventory_health_pie, create_risk_distribution_chart,
    create_batch_age_chart, create_inventory_forecast_comparison
)
from utils.helpers import (
    create_metric_card, create_line_chart, create_stacked_bar, generate_insight
)
from config import COLOR_THEME

def show_inventory_page(data, filters):
    """
    显示库存分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("库存分析")
    
    # 分析库存数据
    inventory_result = analyze_inventory_data(
        data['sales_orders'],
        data['inventory_data'],
        data['monthly_inventory'],
        data['forecast_data']
    )
    
    if not inventory_result['success']:
        st.error(f"库存数据分析失败: {inventory_result['message']}")
        return
    
    # 获取关键指标
    total_inventory = inventory_result['total_inventory']
    assigned_inventory = inventory_result['assigned_inventory']
    orderable_inventory = inventory_result['orderable_inventory']
    pending_inventory = inventory_result['pending_inventory']
    
    # 库存健康状况分布
    health_distribution = inventory_result['health_distribution']
    healthy_count = health_distribution.get('库存健康', 0)
    low_count = health_distribution.get('库存不足', 0)
    high_count = health_distribution.get('库存过剩', 0)
    total_count = healthy_count + low_count + high_count
    
    healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0
    
    # 积压风险分布
    risk_distribution = inventory_result['risk_distribution']
    high_risk = risk_distribution.get('高风险', 0)
    medium_risk = risk_distribution.get('中风险', 0)
    low_risk = risk_distribution.get('低风险', 0)
    total_risk = high_risk + medium_risk + low_risk
    
    high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "总库存量", 
                total_inventory, 
                None
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "健康库存占比", 
                healthy_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                "高风险库存占比", 
                high_risk_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        assigned_percentage = assigned_inventory / total_inventory * 100 if total_inventory > 0 else 0
        
        st.markdown(
            create_metric_card(
                "已分配库存占比", 
                assigned_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第二行：库存健康分布和风险分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("库存健康状况")
        
        # 创建库存健康状况饼图
        fig = create_inventory_health_pie(health_distribution)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 库存健康状况统计
        st.info(
            f"**库存健康状况统计：**\n\n"
            f"- 库存健康: **{healthy_count}个产品 ({healthy_percentage:.1f}%)**\n"
            f"- 库存不足: **{low_count}个产品 ({low_count/total_count*100:.1f}%)**\n"
            f"- 库存过剩: **{high_count}个产品 ({high_count/total_count*100:.1f}%)**"
        )
    
    with col2:
        st.subheader("库存积压风险")
        
        # 创建积压风险分布图
        fig = create_risk_distribution_chart(risk_distribution)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 库存积压风险统计
        st.info(
            f"**库存积压风险统计：**\n\n"
            f"- 低风险: **{low_risk}个产品 ({low_risk/total_risk*100:.1f}%)**\n"
            f"- 中风险: **{medium_risk}个产品 ({medium_risk/total_risk*100:.1f}%)**\n"
            f"- 高风险: **{high_risk}个产品 ({high_risk/total_risk*100:.1f}%)**"
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第三行：批次库存分析和库存预测
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("批次库存分析")
        
        batch_inventory = inventory_result['batch_inventory']
        
        if batch_inventory is not None and not batch_inventory.empty:
            # 创建批次库龄分布图
            fig = create_batch_age_chart(batch_inventory)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 计算批次库龄分布
            age_risk_counts = batch_inventory['库龄风险'].value_counts().to_dict()
            
            fresh_count = age_risk_counts.get('新鲜', 0)
            normal_count = age_risk_counts.get('正常', 0)
            aged_count = age_risk_counts.get('老化', 0)
            expired_count = age_risk_counts.get('过期风险', 0)
            
            st.info(
                f"**批次库龄分析：**\n\n"
                f"- 新鲜批次: **{fresh_count}个**\n"
                f"- 正常批次: **{normal_count}个**\n"
                f"- 老化批次: **{aged_count}个**\n"
                f"- 过期风险批次: **{expired_count}个**"
            )
            
            if expired_count > 0:
                st.warning(
                    f"**注意：**发现{expired_count}个批次有过期风险，需要立即处理！"
                )
        else:
            st.info("没有批次级库存数据，无法进行批次库存分析。")
    
    with col2:
        st.subheader("库存与预测对比")
        
        forecast_vs_inventory = inventory_result['forecast_vs_inventory']
        
        if forecast_vs_inventory is not None and not forecast_vs_inventory.empty:
            # 创建库存与预测对比图
            fig = create_inventory_forecast_comparison(forecast_vs_inventory)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 计算预测库存状态分布
            forecast_status_counts = forecast_vs_inventory['预测库存状态'].value_counts().to_dict()
            
            low_forecast = forecast_status_counts.get('库存不足', 0)
            normal_forecast = forecast_status_counts.get('库存适中', 0)
            high_forecast = forecast_status_counts.get('库存过剩', 0)
            
            st.info(
                f"**预测与库存对比：**\n\n"
                f"- 库存不足(相对预测): **{low_forecast}个产品**\n"
                f"- 库存适中(相对预测): **{normal_forecast}个产品**\n"
                f"- 库存过剩(相对预测): **{high_forecast}个产品**"
            )
            
            if low_forecast > 0:
                st.warning(
                    f"**注意：**有{low_forecast}个产品库存可能无法满足预测需求，建议及时补货！"
                )
        else:
            st.info("没有预测数据，无法进行库存与预测对比分析。")
    
    # 分隔符
    st.markdown("---")
    
    # 第四行：库存洞察
    st.subheader("库存洞察分析")
    
    inventory_insights = get_inventory_insights(inventory_result)
    st.info(inventory_insights)
    
    # 分隔符
    st.markdown("---")
    
    # 第五行：高风险产品详细分析（点击展开）
    with st.expander("高风险产品详细分析"):
        # 获取库存分析数据
        inventory_analysis = inventory_result['inventory_analysis']
        
        # 过滤高风险产品
        high_risk_products = inventory_analysis[inventory_analysis['积压风险'] == '高风险']
        
        if not high_risk_products.empty:
            # 按清库周期排序
            high_risk_products = high_risk_products.sort_values('清库周期(月)', ascending=False)
            
            # 创建清库周期条形图
            fig = px.bar(
                high_risk_products.head(20),
                y='物料',
                x='清库周期(月)',
                orientation='h',
                title='高风险产品清库周期(TOP20)',
                color='清库周期(月)',
                color_continuous_scale=px.colors.sequential.Reds,
                text_auto='.1f'
            )
            
            fig.update_layout(
                xaxis_title='清库周期 (月)',
                yaxis_title='产品代码',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 高风险产品库存价值
            high_risk_value = high_risk_products['现有库存'].sum()
            st.warning(
                f"**高风险产品库存统计：**\n\n"
                f"- 高风险产品数量: **{len(high_risk_products)}个**\n"
                f"- 高风险库存总量: **{high_risk_value:,.0f}**\n"
                f"- 平均清库周期: **{high_risk_products['清库周期(月)'].mean():.1f}个月**\n\n"
                f"建议对这些产品制定专项清库计划，如促销活动、打折销售或调整库存策略。"
            )
            
            # 显示高风险产品清单
            st.subheader("高风险产品清单")
            display_cols = ['物料', '现有库存', '月平均销量', '清库周期(月)', '库存覆盖天数']
            st.write(high_risk_products[display_cols])
        else:
            st.info("没有高风险产品，库存状况良好！")