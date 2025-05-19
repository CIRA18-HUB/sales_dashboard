# pages/product_page.py
# 产品分析页面

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块和工具
from modules.product import (
    analyze_product_data, get_product_insights, 
    create_product_treemap, create_product_growth_chart,
    create_promotion_effectiveness_chart
)
from utils.helpers import (
    create_metric_card, create_bcg_matrix, create_pie_chart, 
    create_stacked_bar, generate_insight
)
from utils.constants import BCG_QUADRANTS
from config import COLOR_THEME, BCG_CONFIG

def show_product_page(data, filters):
    """
    显示产品分析页面
    
    参数:
        data (dict): 所有数据字典
        filters (dict): 筛选条件
    """
    st.title("产品分析")
    
    # 分析产品数据
    product_result = analyze_product_data(
        data['sales_orders'],
        data['product_codes'],
        data['promotion_data']
    )
    
    if not product_result['success']:
        st.error(f"产品数据分析失败: {product_result['message']}")
        return
    
    # 获取关键指标
    product_summary = product_result['product_summary']
    total_products = len(product_summary)
    bcg_summary = product_result['bcg_summary']
    
    # 计算各象限产品数量和销售占比
    bcg_counts = {}
    bcg_sales_percentage = {}
    
    for _, row in bcg_summary.iterrows():
        bcg_counts[row['产品类型']] = row['产品数量']
        bcg_sales_percentage[row['产品类型']] = row['销售占比'] * 100
    
    # 现金牛产品占比
    cash_cow_count = bcg_counts.get('现金牛产品', 0)
    cash_cow_percentage = bcg_sales_percentage.get('现金牛产品', 0)
    
    # 明星产品占比
    star_count = bcg_counts.get('明星产品', 0)
    star_percentage = bcg_sales_percentage.get('明星产品', 0)
    
    # 问号产品占比
    question_count = bcg_counts.get('问号产品', 0)
    question_percentage = bcg_sales_percentage.get('问号产品', 0)
    
    # 瘦狗产品占比
    dog_count = bcg_counts.get('瘦狗产品', 0)
    dog_percentage = bcg_sales_percentage.get('瘦狗产品', 0)
    
    # 合并明星和问号产品占比
    star_question_percentage = star_percentage + question_percentage
    
    # 第一行：关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card(
                "产品总数", 
                total_products, 
                None
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                "现金牛产品占比", 
                cash_cow_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                "明星和问号产品占比", 
                star_question_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            create_metric_card(
                "瘦狗产品占比", 
                dog_percentage, 
                None, 
                is_percentage=True
            ), 
            unsafe_allow_html=True
        )
    
    # 分隔符
    st.markdown("---")
    
    # 第二行：BCG矩阵和产品销售分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("BCG矩阵分析")
        
        # 创建BCG矩阵
        fig = create_bcg_matrix(product_result['product_bcg'], 'BCG产品组合分析')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # JBP计划产品模型目标评估
        jbp_insights = "**JBP计划产品模型目标评估**:\n"
        
        # 评估现金牛产品占比
        if 45 <= cash_cow_percentage <= 50:
            jbp_insights += f"- 现金牛产品占比: **{cash_cow_percentage:.1f}%** (达标，目标: 45%-50%)\n"
        elif cash_cow_percentage < 45:
            jbp_insights += f"- 现金牛产品占比: **{cash_cow_percentage:.1f}%** (低于目标，目标: 45%-50%)\n"
        else:
            jbp_insights += f"- 现金牛产品占比: **{cash_cow_percentage:.1f}%** (高于目标，目标: 45%-50%)\n"
        
        # 评估明星和问号产品占比
        if 40 <= star_question_percentage <= 45:
            jbp_insights += f"- 明星和问号产品占比: **{star_question_percentage:.1f}%** (达标，目标: 40%-45%)\n"
        elif star_question_percentage < 40:
            jbp_insights += f"- 明星和问号产品占比: **{star_question_percentage:.1f}%** (低于目标，目标: 40%-45%)\n"
        else:
            jbp_insights += f"- 明星和问号产品占比: **{star_question_percentage:.1f}%** (高于目标，目标: 40%-45%)\n"
        
        # 评估瘦狗产品占比
        if dog_percentage <= 10:
            jbp_insights += f"- 瘦狗产品占比: **{dog_percentage:.1f}%** (达标，目标: ≤10%)"
        else:
            jbp_insights += f"- 瘦狗产品占比: **{dog_percentage:.1f}%** (高于目标，目标: ≤10%)"
        
        st.info(jbp_insights)
    
    with col2:
        st.subheader("产品销售分布")
        
        # 创建产品树图
        fig = create_product_treemap(product_summary)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 创建象限产品数量条形图
        bcg_count_data = pd.DataFrame({
            '象限': list(bcg_counts.keys()),
            '产品数量': list(bcg_counts.values())
        })
        
        fig = px.bar(
            bcg_count_data,
            x='象限',
            y='产品数量',
            title='各象限产品数量分布',
            color='象限',
            color_discrete_map={
                '现金牛产品': BCG_CONFIG['cash_cow_color'],
                '明星产品': BCG_CONFIG['star_color'],
                '问号产品': BCG_CONFIG['question_mark_color'],
                '瘦狗产品': BCG_CONFIG['dog_color']
            },
            text_auto=True
        )
        
        fig.update_layout(
            xaxis_title='产品象限',
            yaxis_title='产品数量',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 分隔符
    st.markdown("---")
    
    # 第三行：产品销售趋势和促销效果分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("产品销售趋势")
        
        # 创建产品增长趋势图
        fig = create_product_growth_chart(product_result['monthly_product_sales'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # TOP10产品销售额条形图
        top_products = product_summary.head(10)
        
        fig = px.bar(
            top_products,
            y='产品简称',
            x='求和项:金额（元）',
            orientation='h',
            title='TOP10产品销售额',
            color='产品类型',
            color_discrete_map={
                '现金牛产品': BCG_CONFIG['cash_cow_color'],
                '明星产品': BCG_CONFIG['star_color'],
                '问号产品': BCG_CONFIG['question_mark_color'],
                '瘦狗产品': BCG_CONFIG['dog_color']
            },
            text_auto='.2s'
        )
        
        fig.update_layout(
            xaxis_title='销售额 (元)',
            yaxis_title='产品',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("促销效果分析")
        
        # 促销活动分析
        promotion_analysis = product_result['promotion_analysis']
        
        if promotion_analysis is not None and not promotion_analysis.empty:
            # 创建促销效果对比图
            fig = create_promotion_effectiveness_chart(promotion_analysis)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 计算促销活动统计信息
            total_promotions = promotion_analysis['促销活动次数'].sum()
            total_promotion_sales = promotion_analysis['预计销售额（元）'].sum()
            avg_promotion_effect = total_promotion_sales / total_promotions if total_promotions > 0 else 0
            
            st.info(
                f"**促销活动统计：**\n\n"
                f"- 总促销活动次数: **{total_promotions}**\n"
                f"- 预计总促销销售额: **¥{total_promotion_sales:,.2f}**\n"
                f"- 平均每次促销效果: **¥{avg_promotion_effect:,.2f}**"
            )
        else:
            st.info("没有促销活动数据，无法进行促销效果分析。")
        
        # 价格分布分析
        price_distribution = product_result['price_distribution']
        
        if not price_distribution.empty:
            # 创建价格分布直方图
            fig = px.histogram(
                price_distribution,
                x='单价（箱）',
                title='产品价格分布',
                nbins=20,
                color_discrete_sequence=[COLOR_THEME['primary']]
            )
            
            fig.update_layout(
                xaxis_title='单价 (元/箱)',
                yaxis_title='产品数量',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 价格统计信息
            min_price = price_distribution['单价（箱）'].min()
            max_price = price_distribution['单价（箱）'].max()
            avg_price = price_distribution['单价（箱）'].mean()
            
            st.info(
                f"**价格分析：**\n\n"
                f"- 最低单价: **¥{min_price:.2f}/箱**\n"
                f"- 最高单价: **¥{max_price:.2f}/箱**\n"
                f"- 平均单价: **¥{avg_price:.2f}/箱**"
            )
    
    # 分隔符
    st.markdown("---")
    
    # 第四行：产品洞察
    st.subheader("产品洞察分析")
    
    product_insights = get_product_insights(product_result)
    st.info(product_insights)
    
    # 分隔符
    st.markdown("---")
    
    # 第五行：产品象限详细分析（点击展开）
    with st.expander("产品象限详细分析"):
        # 选择要查看的象限
        quadrant = st.selectbox(
            "选择要分析的产品象限",
            ['现金牛产品', '明星产品', '问号产品', '瘦狗产品']
        )
        
        # 过滤选定象限的产品
        quadrant_products = product_summary[product_summary['产品类型'] == quadrant]
        
        if not quadrant_products.empty:
            # 创建象限产品销售额条形图
            fig = px.bar(
                quadrant_products,
                y='产品简称',
                x='求和项:金额（元）',
                orientation='h',
                title=f'{quadrant}销售额',
                color='求和项:金额（元）',
                color_continuous_scale=px.colors.sequential.Blues,
                text_auto='.2s'
            )
            
            fig.update_layout(
                xaxis_title='销售额 (元)',
                yaxis_title='产品',
                height=min(len(quadrant_products) * 30 + 200, 800)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 计算象限产品统计信息
            quadrant_sales = quadrant_products['求和项:金额（元）'].sum()
            quadrant_quantity = quadrant_products['求和项:数量（箱）'].sum()
            avg_price = quadrant_sales / quadrant_quantity if quadrant_quantity > 0 else 0
            
            st.info(
                f"**{quadrant}统计：**\n\n"
                f"- 产品数量: **{len(quadrant_products)}**\n"
                f"- 总销售额: **¥{quadrant_sales:,.2f}**\n"
                f"- 总销售量: **{quadrant_quantity:,.0f}箱**\n"
                f"- 平均单价: **¥{avg_price:.2f}/箱**"
            )
            
            # 根据象限类型提供建议
            if quadrant == '现金牛产品':
                st.success(
                    "**现金牛产品优化建议：**\n\n"
                    "1. 保持稳定的市场份额，控制成本\n"
                    "2. 利用这些产品产生的现金流支持其他产品的发展\n"
                    "3. 定期评估产品生命周期，预测可能的衰退"
                )
            elif quadrant == '明星产品':
                st.success(
                    "**明星产品优化建议：**\n\n"
                    "1. 继续加大营销投入，扩大市场份额\n"
                    "2. 关注产品质量和客户体验，维持高增长率\n"
                    "3. 开发配套产品，延长产品生命周期"
                )
            elif quadrant == '问号产品':
                st.success(
                    "**问号产品优化建议：**\n\n"
                    "1. 评估各产品的发展潜力，对有潜力的产品加大投入\n"
                    "2. 对缺乏竞争力的产品考虑逐步淘汰\n"
                    "3. 关注市场反馈，及时调整产品定位"
                )
            elif quadrant == '瘦狗产品':
                st.success(
                    "**瘦狗产品优化建议：**\n\n"
                    "1. 评估是否有特殊市场需求或战略意义\n"
                    "2. 考虑逐步淘汰或减少资源投入\n"
                    "3. 对有价值的产品进行重新定位或升级改造"
                )
        else:
            st.info(f"没有{quadrant}类型的产品。")