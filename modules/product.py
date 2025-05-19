# modules/product.py
# 产品分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_bcg_matrix, create_pie_chart, create_stacked_bar
from utils.data_loader import categorize_products
from utils.constants import BCG_QUADRANTS
from config import COLOR_THEME, BCG_CONFIG

def analyze_product_data(sales_data, product_codes, promotion_data=None):
    """
    分析产品数据
    
    参数:
        sales_data (DataFrame): 销售数据
        product_codes (list): 产品代码列表
        promotion_data (DataFrame): 促销活动数据，可选
        
    返回:
        dict: 包含产品分析结果的字典
    """
    # 确保包含所需列
    if not {'产品代码', '产品简称', '产品名称', '求和项:金额（元）', '发运月份'}.issubset(sales_data.columns):
        return {
            'success': False,
            'message': '销售数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 过滤只包含指定产品代码的销售数据
        filtered_sales = sales_data[sales_data['产品代码'].isin(product_codes)].copy()
        
        # 计算总销售额
        total_sales = filtered_sales['求和项:金额（元）'].sum()
        
        # 按产品计算销售额
        product_sales = filtered_sales.groupby(['产品代码', '产品简称', '产品名称'])['求和项:金额（元）'].sum().reset_index()
        product_sales = product_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 计算销售数量
        product_quantity = filtered_sales.groupby(['产品代码', '产品简称', '产品名称'])['求和项:数量（箱）'].sum().reset_index()
        
        # 合并销售额和销售数量
        product_summary = pd.merge(product_sales, product_quantity, on=['产品代码', '产品简称', '产品名称'])
        
        # 计算销售占比
        product_summary['销售占比'] = product_summary['求和项:金额（元）'] / total_sales
        
        # 按月份分析产品销售趋势
        monthly_product_sales = filtered_sales.groupby([
            '产品代码', '产品简称', pd.Grouper(key='发运月份', freq='M')
        ])['求和项:金额（元）'].sum().reset_index()
        
        # 计算产品BCG象限
        product_bcg = categorize_products(filtered_sales, product_codes)
        
        # 合并BCG象限信息
        product_summary = pd.merge(
            product_summary,
            product_bcg[['产品代码', '产品类型', '增长率']],
            on='产品代码',
            how='left'
        )
        
        # 计算每个象限的产品数量和销售额
        bcg_summary = product_summary.groupby('产品类型').agg({
            '产品代码': 'count',
            '求和项:金额（元）': 'sum'
        }).reset_index()
        bcg_summary.columns = ['产品类型', '产品数量', '销售额']
        bcg_summary['销售占比'] = bcg_summary['销售额'] / total_sales
        
        # 促销活动分析
        promotion_analysis = None
        if promotion_data is not None and not promotion_data.empty:
            # 计算每个产品的促销活动数量
            promotion_count = promotion_data.groupby(['产品代码', '促销产品名称']).size().reset_index()
            promotion_count.columns = ['产品代码', '产品名称', '促销活动次数']
            
            # 计算促销期间的预计销售额
            promotion_sales = promotion_data.groupby(['产品代码', '促销产品名称']).agg({
                '预计销量（箱）': 'sum',
                '预计销售额（元）': 'sum'
            }).reset_index()
            
            # 合并促销次数和销售额
            promotion_analysis = pd.merge(
                promotion_count,
                promotion_sales,
                on=['产品代码', '产品名称'],
                how='left'
            )
            
            # 计算促销效果（预计销售额/促销活动次数）
            promotion_analysis['促销效果'] = promotion_analysis['预计销售额（元）'] / promotion_analysis['促销活动次数']
            
            # 按促销效果排序
            promotion_analysis = promotion_analysis.sort_values('促销效果', ascending=False)
        
        # 计算产品价格分布
        price_data = filtered_sales.drop_duplicates(['产品代码', '单价（箱）'])
        price_distribution = price_data.groupby(['产品代码', '产品简称'])['单价（箱）'].mean().reset_index()
        price_distribution = price_distribution.sort_values('单价（箱）', ascending=False)
        
        # 返回结果
        return {
            'success': True,
            'total_sales': total_sales,
            'product_summary': product_summary,
            'monthly_product_sales': monthly_product_sales,
            'product_bcg': product_bcg,
            'bcg_summary': bcg_summary,
            'promotion_analysis': promotion_analysis,
            'price_distribution': price_distribution
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_product_insights(analysis_result):
    """
    生成产品洞察
    
    参数:
        analysis_result (dict): 产品分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    insights = []
    
    # 产品总览洞察
    product_summary = analysis_result['product_summary']
    total_products = len(product_summary)
    top_product = product_summary.iloc[0] if not product_summary.empty else None
    
    insights.append(f"共有 **{total_products}** 个活跃产品。")
    
    if top_product is not None:
        top_product_percentage = top_product['销售占比'] * 100
        insights.append(f"销售额最高的产品是 **{top_product['产品简称']}**，占总销售额的 **{top_product_percentage:.1f}%**。")
    
    # BCG矩阵洞察
    bcg_summary = analysis_result['bcg_summary']
    
    if not bcg_summary.empty:
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
        
        insights.append(f"**BCG产品组合分析**:\n"
                       f"- 现金牛产品: **{cash_cow_count}个 ({cash_cow_percentage:.1f}%)**\n"
                       f"- 明星产品: **{star_count}个 ({star_percentage:.1f}%)**\n"
                       f"- 问号产品: **{question_count}个 ({question_percentage:.1f}%)**\n"
                       f"- 瘦狗产品: **{dog_count}个 ({dog_percentage:.1f}%)**")
        
        # JBP计划产品模型评估
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
        
        insights.append(jbp_insights)
    
    # 促销活动洞察
    promotion_analysis = analysis_result.get('promotion_analysis')
    
    if promotion_analysis is not None and not promotion_analysis.empty:
        total_promotions = promotion_analysis['促销活动次数'].sum()
        total_promotion_sales = promotion_analysis['预计销售额（元）'].sum()
        
        insights.append(f"**促销活动分析**:\n"
                       f"- 总促销活动次数: **{total_promotions}**\n"
                       f"- 预计促销销售额: **¥{total_promotion_sales:,.2f}**")
        
        # 最佳促销效果产品
        top_promotion = promotion_analysis.iloc[0]
        insights.append(f"促销效果最好的产品是 **{top_promotion['产品名称']}**，"
                       f"平均每次促销活动带来 **¥{top_promotion['促销效果']:,.2f}** 的销售额。")
    
    # 价格分布洞察
    price_distribution = analysis_result.get('price_distribution')
    
    if price_distribution is not None and not price_distribution.empty:
        avg_price = price_distribution['单价（箱）'].mean()
        max_price = price_distribution['单价（箱）'].max()
        min_price = price_distribution['单价（箱）'].min()
        
        insights.append(f"**产品价格分析**:\n"
                       f"- 平均单价: **¥{avg_price:.2f}/箱**\n"
                       f"- 最高单价: **¥{max_price:.2f}/箱**\n"
                       f"- 最低单价: **¥{min_price:.2f}/箱**")
    
    # 产品优化建议
    suggestions = []
    
    if 'bcg_summary' in analysis_result and not bcg_summary.empty:
        # 现金牛产品建议
        if cash_cow_percentage < 45:
            suggestions.append("增加现金牛产品的营销投入，提高其销售占比")
        elif cash_cow_percentage > 50:
            suggestions.append("适当调整现金牛产品的营销资源，分配更多资源给明星和问号产品")
        
        # 明星和问号产品建议
        if star_question_percentage < 40:
            suggestions.append("加大对明星和问号产品的投入，提高其销售占比")
        
        # 瘦狗产品建议
        if dog_percentage > 10:
            suggestions.append("考虑淘汰或改进部分瘦狗产品，降低其销售占比")
    
    if suggestions:
        insights.append("**产品优化建议**:\n- " + "\n- ".join(suggestions))
    
    return "\n\n".join(insights)

def create_product_treemap(product_summary):
    """
    创建产品树图
    
    参数:
        product_summary (DataFrame): 产品摘要数据
        
    返回:
        plotly.graph_objects.Figure: 树图对象
    """
    if product_summary.empty:
        return None
    
    # 创建树图
    fig = px.treemap(
        product_summary,
        path=['产品类型', '产品简称'],
        values='求和项:金额（元）',
        color='产品类型',
        color_discrete_map={
            '现金牛产品': BCG_CONFIG['cash_cow_color'],
            '明星产品': BCG_CONFIG['star_color'],
            '问号产品': BCG_CONFIG['question_mark_color'],
            '瘦狗产品': BCG_CONFIG['dog_color']
        },
        hover_data=['产品代码', '求和项:数量（箱）', '销售占比'],
        title='产品销售分布树图 (按BCG象限分组)'
    )
    
    # 自定义悬停信息
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.2f}<br>销售占比: %{customdata[2]:.1%}<br>销售数量: %{customdata[1]:,} 箱<br>产品代码: %{customdata[0]}'
    )
    
    # 更新布局
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=600
    )
    
    return fig

def create_product_growth_chart(monthly_product_sales, top_n=10):
    """
    创建产品增长趋势图
    
    参数:
        monthly_product_sales (DataFrame): 月度产品销售数据
        top_n (int): 显示的产品数量
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if monthly_product_sales.empty:
        return None
    
    # 计算每个产品的总销售额
    product_total = monthly_product_sales.groupby(['产品代码', '产品简称'])['求和项:金额（元）'].sum().reset_index()
    
    # 选择销售额最高的N个产品
    top_products = product_total.nlargest(top_n, '求和项:金额（元）')['产品代码'].tolist()
    
    # 过滤数据
    plot_data = monthly_product_sales[monthly_product_sales['产品代码'].isin(top_products)]
    
    # 创建折线图
    fig = px.line(
        plot_data,
        x='发运月份',
        y='求和项:金额（元）',
        color='产品简称',
        markers=True,
        title=f'TOP {top_n} 产品销售趋势'
    )
    
    # 更新布局
    fig.update_layout(
        xaxis_title='月份',
        yaxis_title='销售额 (元)',
        legend_title='产品',
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_promotion_effectiveness_chart(promotion_analysis, top_n=10):
    """
    创建促销效果对比图
    
    参数:
        promotion_analysis (DataFrame): 促销分析数据
        top_n (int): 显示的产品数量
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if promotion_analysis is None or promotion_analysis.empty:
        return None
    
    # 选择促销效果最好的N个产品
    plot_data = promotion_analysis.nlargest(top_n, '促销效果')
    
    # 创建水平条形图
    fig = px.bar(
        plot_data,
        y='产品名称',
        x='促销效果',
        orientation='h',
        color='促销效果',
        color_continuous_scale=px.colors.sequential.Blues,
        title=f'TOP {top_n} 促销效果产品对比',
        text='促销效果'
    )
    
    # 更新布局
    fig.update_layout(
        xaxis_title='促销效果 (平均每次促销带来的销售额)',
        yaxis_title='产品',
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 更新文本
    fig.update_traces(
        texttemplate='¥%{x:,.2f}',
        textposition='outside'
    )
    
    return fig