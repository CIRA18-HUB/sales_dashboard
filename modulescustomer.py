# modules/customer.py
# 客户分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_pie_chart, create_stacked_bar
from config import COLOR_THEME

def analyze_customer_data(sales_data, customer_relations=None, customer_target=None):
    """
    分析客户数据
    
    参数:
        sales_data (DataFrame): 销售数据
        customer_relations (DataFrame): 客户关系数据，可选
        customer_target (DataFrame): 客户目标数据，可选
        
    返回:
        dict: 包含客户分析结果的字典
    """
    # 确保包含所需列
    if not {'客户代码', '客户简称', '经销商名称', '求和项:金额（元）', '发运月份', '订单类型'}.issubset(sales_data.columns):
        return {
            'success': False,
            'message': '销售数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 计算总销售额
        total_sales = sales_data['求和项:金额（元）'].sum()
        
        # 按客户计算销售额
        customer_sales = sales_data.groupby(['客户代码', '客户简称', '经销商名称'])['求和项:金额（元）'].sum().reset_index()
        customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 计算客户数量
        total_customers = len(customer_sales)
        
        # 计算TOP客户销售额和占比
        top10_sales = customer_sales.head(10)['求和项:金额（元）'].sum()
        top10_percentage = top10_sales / total_sales * 100 if total_sales > 0 else 0
        
        top5_sales = customer_sales.head(5)['求和项:金额（元）'].sum()
        top5_percentage = top5_sales / total_sales * 100 if total_sales > 0 else 0
        
        top1_sales = customer_sales.iloc[0]['求和项:金额（元）'] if not customer_sales.empty else 0
        top1_percentage = top1_sales / total_sales * 100 if total_sales > 0 else 0
        
        # 计算客户的MT和TT渠道销售额
        mt_customer_sales = sales_data[sales_data['订单类型'] == '订单-正常产品'].groupby(
            ['客户代码', '客户简称', '经销商名称']
        )['求和项:金额（元）'].sum().reset_index()
        mt_customer_sales['渠道'] = 'MT'
        
        tt_customer_sales = sales_data[sales_data['订单类型'] == '订单-TT产品'].groupby(
            ['客户代码', '客户简称', '经销商名称']
        )['求和项:金额（元）'].sum().reset_index()
        tt_customer_sales['渠道'] = 'TT'
        
        # 合并MT和TT渠道数据
        channel_customer_sales = pd.concat([mt_customer_sales, tt_customer_sales])
        
        # 按月分析客户数量变化
        monthly_customer_count = sales_data.groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['客户代码'].nunique().reset_index()
        monthly_customer_count.columns = ['月份', '客户数量']
        
        # 客户关系状态分析
        customer_status = None
        if customer_relations is not None and not customer_relations.empty:
            customer_status = customer_relations.groupby('状态').size().reset_index()
            customer_status.columns = ['状态', '客户数量']
        
        # 客户目标达成分析
        customer_achievement = None
        if customer_target is not None and not customer_target.empty:
            # 按客户和月份分组计算销售额
            sales_by_customer_month = sales_data.groupby([
                '客户简称', pd.Grouper(key='发运月份', freq='M')
            ])['求和项:金额（元）'].sum().reset_index()
            
            # 将月份格式调整为与目标数据相同
            sales_by_customer_month['月份'] = sales_by_customer_month['发运月份'].dt.to_period('M').dt.to_timestamp()
            
            # 合并销售数据和目标数据
            customer_achievement = pd.merge(
                sales_by_customer_month,
                customer_target[['客户', '月份', '月度指标']],
                left_on=['客户简称', '月份'],
                right_on=['客户', '月份'],
                how='left'
            )
            
            # 计算达成率
            customer_achievement['达成率'] = customer_achievement['求和项:金额（元）'] / customer_achievement['月度指标']
        
        # 计算客户产品多样性
        customer_product_diversity = sales_data.groupby('客户简称')['产品代码'].nunique().reset_index()
        customer_product_diversity.columns = ['客户简称', '产品数量']
        customer_product_diversity = customer_product_diversity.sort_values('产品数量', ascending=False)
        
        # 计算客户忠诚度（购买月份数）
        customer_loyalty = sales_data.groupby('客户简称')['发运月份'].apply(
            lambda x: x.dt.to_period('M').nunique()
        ).reset_index()
        customer_loyalty.columns = ['客户简称', '购买月份数']
        customer_loyalty = customer_loyalty.sort_values('购买月份数', ascending=False)
        
        # 返回结果
        return {
            'success': True,
            'total_sales': total_sales,
            'total_customers': total_customers,
            'customer_sales': customer_sales,
            'top10_sales': top10_sales,
            'top10_percentage': top10_percentage,
            'top5_sales': top5_sales,
            'top5_percentage': top5_percentage,
            'top1_sales': top1_sales,
            'top1_percentage': top1_percentage,
            'channel_customer_sales': channel_customer_sales,
            'monthly_customer_count': monthly_customer_count,
            'customer_status': customer_status,
            'customer_achievement': customer_achievement,
            'customer_product_diversity': customer_product_diversity,
            'customer_loyalty': customer_loyalty
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_customer_dependency_level(top1_percentage, top5_percentage):
    """
    评估客户依赖程度
    
    参数:
        top1_percentage (float): 第一大客户销售占比
        top5_percentage (float): 前5大客户销售占比
        
    返回:
        tuple: (依赖级别, 描述)
    """
    if top1_percentage > 30 or top5_percentage > 60:
        return ("高", "客户集中度过高，存在较大依赖风险")
    elif top1_percentage > 20 or top5_percentage > 40:
        return ("中", "客户集中度一般，有一定依赖风险")
    else:
        return ("低", "客户分散度良好，依赖风险较低")

def get_customer_insights(analysis_result):
    """
    生成客户洞察
    
    参数:
        analysis_result (dict): 客户分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    insights = []
    
    # 客户数量洞察
    total_customers = analysis_result['total_customers']
    insights.append(f"共有 **{total_customers}** 个活跃客户。")
    
    # 客户依赖度洞察
    top1_percentage = analysis_result['top1_percentage']
    top5_percentage = analysis_result['top5_percentage']
    top10_percentage = analysis_result['top10_percentage']
    
    dependency_level, dependency_desc = get_customer_dependency_level(top1_percentage, top5_percentage)
    
    insights.append(f"**客户依赖度: {dependency_level}**\n"
                   f"- 第一大客户占比: **{top1_percentage:.1f}%**\n"
                   f"- TOP5客户占比: **{top5_percentage:.1f}%**\n"
                   f"- TOP10客户占比: **{top10_percentage:.1f}%**\n"
                   f"{dependency_desc}")
    
    # 客户渠道洞察
    channel_data = analysis_result['channel_customer_sales']
    if not channel_data.empty:
        mt_sales = channel_data[channel_data['渠道'] == 'MT']['求和项:金额（元）'].sum()
        tt_sales = channel_data[channel_data['渠道'] == 'TT']['求和项:金额（元）'].sum()
        total_sales = mt_sales + tt_sales
        
        mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
        tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0
        
        insights.append(f"**渠道占比**:\n"
                       f"- MT渠道: **{mt_percentage:.1f}%**\n"
                       f"- TT渠道: **{tt_percentage:.1f}%**")
    
    # 客户月份变化洞察
    monthly_count = analysis_result['monthly_customer_count']
    if len(monthly_count) >= 2:
        latest_count = monthly_count.iloc[-1]['客户数量']
        previous_count = monthly_count.iloc[-2]['客户数量']
        count_change = latest_count - previous_count
        
        if count_change > 0:
            insights.append(f"最近一个月客户数量**增加了 {count_change} 个**，客户拓展良好。")
        elif count_change < 0:
            insights.append(f"最近一个月客户数量**减少了 {abs(count_change)} 个**，需关注客户流失情况。")
        else:
            insights.append("最近一个月客户数量保持稳定。")
    
    # 客户产品多样性洞察
    diversity = analysis_result['customer_product_diversity']
    if not diversity.empty:
        avg_products = diversity['产品数量'].mean()
        high_diversity_count = len(diversity[diversity['产品数量'] > avg_products])
        high_diversity_percentage = high_diversity_count / len(diversity) * 100
        
        insights.append(f"客户平均购买 **{avg_products:.1f}** 种产品，**{high_diversity_percentage:.1f}%** 的客户购买产品种类高于平均水平。")
    
    # 客户忠诚度洞察
    loyalty = analysis_result['customer_loyalty']
    if not loyalty.empty:
        avg_months = loyalty['购买月份数'].mean()
        high_loyalty_count = len(loyalty[loyalty['购买月份数'] >= 6])  # 购买超过半年
        high_loyalty_percentage = high_loyalty_count / len(loyalty) * 100
        
        insights.append(f"客户平均活跃 **{avg_months:.1f}** 个月，**{high_loyalty_percentage:.1f}%** 的客户活跃超过半年，属于忠诚客户。")
    
    return "\n\n".join(insights)

def create_customer_pareto_chart(customer_sales):
    """
    创建客户帕累托图
    
    参数:
        customer_sales (DataFrame): 客户销售数据
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if customer_sales.empty:
        return None
    
    # 计算累计销售额和占比
    customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False).reset_index(drop=True)
    customer_sales['累计销售额'] = customer_sales['求和项:金额（元）'].cumsum()
    customer_sales['累计占比'] = customer_sales['累计销售额'] / customer_sales['求和项:金额（元）'].sum()
    
    # 限制显示前20个客户
    display_customers = min(20, len(customer_sales))
    plot_data = customer_sales.head(display_customers)
    
    # 创建图表
    fig = go.Figure()
    
    # 添加销售额柱状图
    fig.add_trace(go.Bar(
        x=plot_data.index,
        y=plot_data['求和项:金额（元）'],
        name='销售额',
        marker_color=COLOR_THEME['primary']
    ))
    
    # 添加累计占比线
    fig.add_trace(go.Scatter(
        x=plot_data.index,
        y=plot_data['累计占比'],
        name='累计占比',
        mode='lines+markers',
        line=dict(color=COLOR_THEME['secondary'], width=2),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # 更新布局
    fig.update_layout(
        title=f'客户销售额帕累托图 (前{display_customers}名)',
        xaxis=dict(
            title='客户排名',
            tickmode='array',
            tickvals=plot_data.index,
            ticktext=[f"{i+1}" for i in plot_data.index]
        ),
        yaxis=dict(title='销售额 (元)'),
        yaxis2=dict(
            title='累计占比',
            titlefont=dict(color=COLOR_THEME['secondary']),
            tickfont=dict(color=COLOR_THEME['secondary']),
            overlaying='y',
            side='right',
            showgrid=False,
            tickformat='.0%',
            range=[0, 1]
        ),
        legend=dict(
            x=0,
            y=1.1,
            orientation='h'
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 添加标注线
    fig.add_shape(
        type="line",
        x0=-1, y0=0.8, x1=display_customers, y1=0.8,
        yref="y2",
        line=dict(color="red", width=2, dash="dash")
    )
    
    fig.add_annotation(
        x=display_customers-1,
        y=0.8,
        yref="y2",
        text="80%",
        showarrow=False,
        font=dict(color="red")
    )
    
    return fig

def create_customer_bubble_chart(analysis_result):
    """
    创建客户气泡图（销售额、产品多样性、忠诚度）
    
    参数:
        analysis_result (dict): 客户分析结果
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if not analysis_result['success']:
        return None
    
    # 合并客户销售、产品多样性和忠诚度数据
    customer_sales = analysis_result['customer_sales']
    product_diversity = analysis_result['customer_product_diversity']
    loyalty = analysis_result['customer_loyalty']
    
    # 只保留客户简称列，方便合并
    customer_sales = customer_sales[['客户简称', '求和项:金额（元）']]
    
    # 合并数据
    merged_data = pd.merge(customer_sales, product_diversity, on='客户简称', how='left')
    merged_data = pd.merge(merged_data, loyalty, on='客户简称', how='left')
    
    # 填充缺失值
    merged_data['产品数量'].fillna(1, inplace=True)
    merged_data['购买月份数'].fillna(1, inplace=True)
    
    # 仅显示前50个客户
    top_customers = min(50, len(merged_data))
    plot_data = merged_data.nlargest(top_customers, '求和项:金额（元）')
    
    # 创建气泡图
    fig = px.scatter(
        plot_data,
        x='产品数量',
        y='购买月份数',
        size='求和项:金额（元）',
        color='求和项:金额（元）',
        hover_name='客户简称',
        text='客户简称',
        size_max=50,
        color_continuous_scale=px.colors.sequential.Blues,
        title=f'客户价值矩阵 (TOP {top_customers})'
    )
    
    # 更新布局
    fig.update_layout(
        xaxis=dict(title='产品多样性 (购买产品数量)'),
        yaxis=dict(title='客户忠诚度 (活跃月份数)'),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 更新文本
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=8)
    )
    
    # 添加四象限分隔线
    avg_products = plot_data['产品数量'].mean()
    avg_months = plot_data['购买月份数'].mean()
    
    fig.add_shape(
        type="line", x0=avg_products, y0=0, x1=avg_products, y1=plot_data['购买月份数'].max() * 1.1,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    fig.add_shape(
        type="line", x0=0, y0=avg_months, x1=plot_data['产品数量'].max() * 1.1, y1=avg_months,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # 添加象限标签
    fig.add_annotation(
        x=avg_products/2, y=avg_months + avg_months*0.2,
        text="低多样性<br>高忠诚度",
        showarrow=False,
        font=dict(size=10)
    )
    
    fig.add_annotation(
        x=avg_products + avg_products*0.3, y=avg_months + avg_months*0.2,
        text="高多样性<br>高忠诚度<br>(核心客户)",
        showarrow=False,
        font=dict(size=10)
    )
    
    fig.add_annotation(
        x=avg_products/2, y=avg_months*0.5,
        text="低多样性<br>低忠诚度<br>(风险客户)",
        showarrow=False,
        font=dict(size=10)
    )
    
    fig.add_annotation(
        x=avg_products + avg_products*0.3, y=avg_months*0.5,
        text="高多样性<br>低忠诚度",
        showarrow=False,
        font=dict(size=10)
    )
    
    return fig