# pages/material_page.py
# 物料使用效率分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.material import (
    analyze_material_efficiency, get_material_efficiency_insights,
    get_top_low_turnover_products, create_turnover_histogram,
    create_turnover_rating_pie
)
from utils.helpers import (
    create_metric_card, create_gauge, generate_insight
)
from config import COLOR_THEME

def show_material_page(data, filters):
    """
    显示物料使用效率分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("物料使用效率分析")
    
    # 分析物料使用效率
    analysis_result = analyze_material_efficiency(
        data['sales_orders'],
        data['inventory_data']
    )
    
    if not analysis_result['success']:
        st.error(f"物料使用效率分析失败: {analysis_result['message']}")
        return
    
    # 获取分析结果
    efficiency_data = analysis_result['efficiency_data']
    overall_metrics = analysis_result['overall_metrics']
    rating_counts = analysis_result['rating_counts']
    
    # 提取关键指标
    avg_turnover_rate = overall_metrics['avg_turnover_rate']
    avg_coverage_days = overall_metrics['avg_coverage_days']
    low_turnover_products = overall_metrics['low_turnover_products']
    high_turnover_products = overall_metrics['high_turnover_products']
    total_products = overall_metrics['total_products']
    
    # 计算周转率评级分布百分比
    excellent_percentage = rating_counts.get('优秀', 0) / total_products * 100 if total_products > 0 else 0
    good_percentage = rating_counts.get('良好', 0) / total_products * 100 if total_products > 0 else 0
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "平均库存周转率", 
                avg_turnover_rate, 
                None
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "平均库存覆盖天数", 
                avg_coverage_days, 
                None,
                suffix="天"
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                "高效率产品占比", 
                excellent_percentage + good_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        low_percentage = low_turnover_products / total_products * 100 if total_products > 0 else 0
        
        st.markdown(
            create_metric_card(
                "低周转产品占比", 
                low_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第二行：周转率分布和周转率评级
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("库存周转率分布")
        
        # 创建周转率分布直方图
        fig = create_turnover_histogram(analysis_result)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 周转率分布统计
        st.info(
            f"**周转率分布统计：**\n\n"
            f"- 高周转率(>1.5): **{len(efficiency_data[efficiency_data['库存周转率'] > 1.5])}个产品 "
            f"({len(efficiency_data[efficiency_data['库存周转率'] > 1.5])/len(efficiency_data)*100:.1f}%)**\n"
            f"- 中周转率(0.5-1.5): **{len(efficiency_data[(efficiency_data['库存周转率'] <= 1.5) & (efficiency_data['库存周转率'] > 0.5)])}个产品 "
            f"({len(efficiency_data[(efficiency_data['库存周转率'] <= 1.5) & (efficiency_data['库存周转率'] > 0.5)])/len(efficiency_data)*100:.1f}%)**\n"
            f"- 低周转率(<0.5): **{len(efficiency_data[efficiency_data['库存周转率'] <= 0.5])}个产品 "
            f"({len(efficiency_data[efficiency_data['库存周转率'] <= 0.5])/len(efficiency_data)*100:.1f}%)**"
        )
    
    with col2:
        st.subheader("周转率评级分布")
        
        # 创建周转率评级饼图
        fig = create_turnover_rating_pie(analysis_result)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 周转率评级统计
        st.info(
            f"**周转率评级统计：**\n\n"
            f"- 优秀: **{rating_counts.get('优秀', 0)}个产品 ({excellent_percentage:.1f}%)**\n"
            f"- 良好: **{rating_counts.get('良好', 0)}个产品 ({good_percentage:.1f}%)**\n"
            f"- 一般: **{rating_counts.get('一般', 0)}个产品 "
            f"({rating_counts.get('一般', 0)/total_products*100:.1f}%)**\n"
            f"- 不佳: **{rating_counts.get('不佳', 0)}个产品 "
            f"({rating_counts.get('不佳', 0)/total_products*100:.1f}%)**\n"
            f"- 很差: **{rating_counts.get('很差', 0)}个产品 "
            f"({rating_counts.get('很差', 0)/total_products*100:.1f}%)**"
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第三行：周转率排名
    st.subheader("产品周转率排名")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("周转率最高的产品")
        
        # 按周转率排序
        high_turnover = efficiency_data.sort_values('库存周转率', ascending=False).head(10)
        
        # 创建高周转率条形图
        fig = px.bar(
            high_turnover,
            y='产品简称',
            x='库存周转率',
            orientation='h',
            title='周转率最高的10个产品',
            color='库存周转率',
            color_continuous_scale=px.colors.sequential.Blues,
            text_auto='.2f'
        )
        
        fig.update_layout(
            xaxis_title='库存周转率',
            yaxis_title='产品',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("周转率最低的产品")
        
        # 按周转率排序
        low_turnover = efficiency_data.sort_values('库存周转率').head(10)
        
        # 创建低周转率条形图
        fig = px.bar(
            low_turnover,
            y='产品简称',
            x='库存周转率',
            orientation='h',
            title='周转率最低的10个产品',
            color='库存周转率',
            color_continuous_scale=px.colors.sequential.Reds_r,
            text_auto='.2f'
        )
        
        fig.update_layout(
            xaxis_title='库存周转率',
            yaxis_title='产品',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 第四行：低周转率产品分析
    st.subheader("低周转率产品分析")
    
    # 获取周转率最低的产品
    low_turnover_detail = get_top_low_turnover_products(analysis_result)
    
    if not low_turnover_detail.empty:
        # 创建覆盖天数条形图
        fig = px.bar(
            low_turnover_detail,
            y='产品简称',
            x='库存覆盖天数',
            orientation='h',
            title='低周转产品库存覆盖天数',
            color='库存覆盖天数',
            color_continuous_scale=px.colors.sequential.Reds,
            text_auto='.0f'
        )
        
        fig.update_layout(
            xaxis_title='库存覆盖天数',
            yaxis_title='产品',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 低周转产品建议
        st.warning(
            "**低周转产品优化建议：**\n\n"
            "1. 考虑促销活动，加速清理库存\n"
            "2. 调整采购计划，减少低周转产品的采购量\n"
            "3. 评估产品未来需求，考虑是否逐步淘汰\n"
            "4. 制定特定的库存控制策略，如最低库存量或及时补货点的调整"
        )
    else:
        st.info("没有低周转率产品，物料使用效率良好！")
    
    # 分隔符
    st.markdown("---")
    
    # 第五行：物料使用效率洞察
    st.subheader("物料使用效率洞察")
    
    efficiency_insights = get_material_efficiency_insights(analysis_result)
    st.info(efficiency_insights)