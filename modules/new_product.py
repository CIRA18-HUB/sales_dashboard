# modules/new_product.py
# 新品分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_line_chart, create_stacked_bar
from config import COLOR_THEME

def analyze_new_product_data(sales_data, new_product_codes, promotion_data=None):
    """
    分析新品数据
    
    参数:
        sales_data (DataFrame): 销售数据
        new_product_codes (list): 新品产品代码列表
        promotion_data (DataFrame): 促销活动数据，可选
        
    返回:
        dict: 包含新品分析结果的字典
    """
    # 确保包含所需列
    if not {'产品代码', '产品简称', '产品名称', '求和项:金额（元）', '发运月份'}.issubset(sales_data.columns):
        return {
            'success': False,
            'message': '销售数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 过滤只包含新品产品代码的销售数据
        new_product_sales = sales_data[sales_data['产品代码'].isin(new_product_codes)].copy()
        
        # 计算新品总销售额
        new_product_total_sales = new_product_sales['求和项:金额（元）'].sum()
        
        # 计算新品占总销售额的比例
        total_sales = sales_data['求和项:金额（元）'].sum()
        new_product_percentage = new_product_total_sales / total_sales * 100 if total_sales > 0 else 0
        
        # 按新品计算销售额
        product_sales = new_product_sales.groupby(['产品代码', '产品简称', '产品名称'])['求和项:金额（元）'].sum().reset_index()
        product_sales = product_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 计算新品销售数量
        product_quantity = new_product_sales.groupby(['产品代码', '产品简称', '产品名称'])['求和项:数量（箱）'].sum().reset_index()
        
        # 合并销售额和销售数量
        product_summary = pd.merge(product_sales, product_quantity, on=['产品代码', '产品简称', '产品名称'])
        
        # 计算各新品占新品总销售额的比例
        product_summary['占新品销售比例'] = product_summary['求和项:金额（元）'] / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        
        # 按月份分析新品销售趋势
        monthly_sales = new_product_sales.groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        
        # 计算月环比增长率
        monthly_sales['环比增长率'] = monthly_sales['求和项:金额（元）'].pct_change()
        
        # 计算每个新品的月度销售额
        monthly_product_sales = new_product_sales.groupby([
            '产品代码', '产品简称', pd.Grouper(key='发运月份', freq='M')
        ])['求和项:金额（元）'].sum().reset_index()
        
        # 计算新品的区域分布
        region_sales = new_product_sales.groupby('所属区域')['求和项:金额（元）'].sum().reset_index()
        region_sales = region_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 计算新品的渠道分布（MT/TT）
        channel_sales = pd.DataFrame()
        channel_sales['渠道'] = ['MT渠道', 'TT渠道']
        channel_sales['销售额'] = [
            new_product_sales[new_product_sales['订单类型'] == '订单-正常产品']['求和项:金额（元）'].sum(),
            new_product_sales[new_product_sales['订单类型'] == '订单-TT产品']['求和项:金额（元）'].sum()
        ]
        
        channel_sales['销售占比'] = channel_sales['销售额'] / channel_sales['销售额'].sum() * 100 if channel_sales['销售额'].sum() > 0 else 0
        
        # 计算新品客户分布
        customer_sales = new_product_sales.groupby(['客户代码', '客户简称', '经销商名称'])['求和项:金额（元）'].sum().reset_index()
        customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 新品促销活动分析
        promotion_analysis = None
        if promotion_data is not None and not promotion_data.empty:
            # 过滤只包含新品的促销活动
            new_product_promotions = promotion_data[promotion_data['产品代码'].isin(new_product_codes)].copy()
            
            if not new_product_promotions.empty:
                # 按产品统计促销活动
                promotion_count = new_product_promotions.groupby(['产品代码', '促销产品名称']).size().reset_index()
                promotion_count.columns = ['产品代码', '产品名称', '促销活动次数']
                
                # 计算促销期间的预计销售额
                promotion_sales = new_product_promotions.groupby(['产品代码', '促销产品名称']).agg({
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
        
        # 计算新品上市后的天数
        new_product_age = {}
        for code in new_product_codes:
            product_data = sales_data[sales_data['产品代码'] == code]
            if not product_data.empty:
                first_sale_date = product_data['发运月份'].min()
                today = datetime.now()
                age_days = (today - first_sale_date).days
                new_product_age[code] = age_days
        
        # 返回结果
        return {
            'success': True,
            'new_product_total_sales': new_product_total_sales,
            'new_product_percentage': new_product_percentage,
            'product_summary': product_summary,
            'monthly_sales': monthly_sales,
            'monthly_product_sales': monthly_product_sales,
            'region_sales': region_sales,
            'channel_sales': channel_sales,
            'customer_sales': customer_sales,
            'promotion_analysis': promotion_analysis,
            'new_product_age': new_product_age
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_new_product_insights(analysis_result):
    """
    生成新品洞察
    
    参数:
        analysis_result (dict): 新品分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    insights = []
    
    # 新品总体表现洞察
    new_product_total_sales = analysis_result['new_product_total_sales']
    new_product_percentage = analysis_result['new_product_percentage']
    
    insights.append(f"新品总销售额为 **¥{new_product_total_sales:,.2f}**，占总销售额的 **{new_product_percentage:.1f}%**。")
    
    # 新品销售趋势洞察
    monthly_sales = analysis_result['monthly_sales']
    
    if len(monthly_sales) >= 2:
        latest_month = monthly_sales.iloc[-1]
        previous_month = monthly_sales.iloc[-2]
        
        if not pd.isna(latest_month['环比增长率']):
            growth_rate = latest_month['环比增长率'] * 100
            growth_description = "增长" if growth_rate > 0 else "下降"
            
            insights.append(f"最近一个月新品销售额环比**{growth_description} {abs(growth_rate):.1f}%**。")
    
    # 新品区域分布洞察
    region_sales = analysis_result['region_sales']
    
    if not region_sales.empty:
        top_region = region_sales.iloc[0]
        top_region_percentage = top_region['求和项:金额（元）'] / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        
        insights.append(f"**{top_region['所属区域']}**区域是新品销售最好的区域，占新品总销售额的 **{top_region_percentage:.1f}%**。")
    
    # 新品渠道分布洞察
    channel_sales = analysis_result['channel_sales']
    
    if not channel_sales.empty:
        mt_sales = channel_sales[channel_sales['渠道'] == 'MT渠道']['销售额'].values[0]
        tt_sales = channel_sales[channel_sales['渠道'] == 'TT渠道']['销售额'].values[0]
        
        mt_percentage = mt_sales / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        tt_percentage = tt_sales / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        
        insights.append(f"新品在MT渠道占比 **{mt_percentage:.1f}%**，在TT渠道占比 **{tt_percentage:.1f}%**。")
    
    # 新品客户分布洞察
    customer_sales = analysis_result['customer_sales']
    
    if not customer_sales.empty:
        top_customer = customer_sales.iloc[0]
        top_customer_percentage = top_customer['求和项:金额（元）'] / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        
        insights.append(f"**{top_customer['客户简称']}**是购买新品最多的客户，占新品总销售额的 **{top_customer_percentage:.1f}%**。")
    
    # 新品促销活动洞察
    promotion_analysis = analysis_result.get('promotion_analysis')
    
    if promotion_analysis is not None and not promotion_analysis.empty:
        total_promotions = promotion_analysis['促销活动次数'].sum()
        total_expected_sales = promotion_analysis['预计销售额（元）'].sum()
        
        promotion_sales_percentage = total_expected_sales / new_product_total_sales * 100 if new_product_total_sales > 0 else 0
        
        insights.append(f"新品共进行了 **{total_promotions}** 次促销活动，预计销售额 **¥{total_expected_sales:,.2f}**，"
                       f"占新品总销售额的 **{promotion_sales_percentage:.1f}%**。")
    
    # 新品上市时间洞察
    new_product_age = analysis_result.get('new_product_age', {})
    
    if new_product_age:
        avg_age = sum(new_product_age.values()) / len(new_product_age)
        newest_product = min(new_product_age.items(), key=lambda x: x[1])
        oldest_product = max(new_product_age.items(), key=lambda x: x[1])
        
        insights.append(f"新品平均上市 **{avg_age:.0f}天**，最新上市的产品为 **{newest_product[0]}** ({newest_product[1]}天)，"
                       f"上市时间最长的产品为 **{oldest_product[0]}** ({oldest_product[1]}天)。")
    
    # 新品优化建议
    product_summary = analysis_result['product_summary']
    
    suggestions = []
    
    if not product_summary.empty:
        # 销售表现好的新品
        top_performers = product_summary.head(3)['产品简称'].tolist()
        top_performers_str = "、".join(top_performers)
        
        # 销售表现差的新品
        poor_performers = product_summary.tail(3)['产品简称'].tolist()
        poor_performers_str = "、".join(poor_performers)
        
        suggestions.append(f"重点关注表现优异的新品：{top_performers_str}，扩大其市场份额")
        suggestions.append(f"评估表现不佳的新品：{poor_performers_str}，考虑调整营销策略或产品定位")
    
    if new_product_percentage < 10:
        suggestions.append("整体新品销售占比较低，建议加大新品推广力度")
    
    if promotion_analysis is not None and not promotion_analysis.empty:
        top_promotion = promotion_analysis.sort_values('预计销售额（元）', ascending=False).iloc[0]
        suggestions.append(f"重点推广促销效果好的新品：{top_promotion['产品名称']}")
    
    if suggestions:
        insights.append("**新品优化建议**:\n- " + "\n- ".join(suggestions))
    
    return "\n\n".join(insights)

def create_new_product_trend_chart(monthly_sales):
    """
    创建新品销售趋势图
    
    参数:
        monthly_sales (DataFrame): 月度销售数据
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if monthly_sales.empty:
        return None
    
    # 创建复合图表
    fig = go.Figure()
    
    # 添加销售额柱状图
    fig.add_trace(go.Bar(
        x=monthly_sales['发运月份'],
        y=monthly_sales['求和项:金额（元）'],
        name='销售额',
        marker_color=COLOR_THEME['primary']
    ))
    
    # 添加环比增长率线
    fig.add_trace(go.Scatter(
        x=monthly_sales['发运月份'],
        y=monthly_sales['环比增长率'],
        name='环比增长率',
        mode='lines+markers',
        line=dict(color=COLOR_THEME['secondary'], width=2),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # 更新布局
    fig.update_layout(
        title='新品月度销售趋势',
        xaxis=dict(title='月份'),
        yaxis=dict(title='销售额 (元)'),
        yaxis2=dict(
            title='环比增长率',
            titlefont=dict(color=COLOR_THEME['secondary']),
            tickfont=dict(color=COLOR_THEME['secondary']),
            overlaying='y',
            side='right',
            showgrid=False,
            tickformat='.0%',
            range=[-0.5, 0.5]
        ),
        legend=dict(
            x=0,
            y=1.1,
            orientation='h'
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig

def create_new_product_performance_chart(product_summary, top_n=10):
    """
    创建新品销售表现对比图
    
    参数:
        product_summary (DataFrame): 产品摘要数据
        top_n (int): 显示的产品数量
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if product_summary.empty:
        return None
    
    # 选择前N个产品
    plot_data = product_summary.head(top_n)
    
    # 创建水平条形图
    fig = px.bar(
        plot_data,
        y='产品简称',
        x='求和项:金额（元）',
        orientation='h',
        color='求和项:金额（元）',
        color_continuous_scale=px.colors.sequential.Blues,
        title=f'TOP {top_n} 新品销售表现对比',
        text='求和项:金额（元）'
    )
    
    # 更新布局
    fig.update_layout(
        xaxis=dict(title='销售额 (元)'),
        yaxis=dict(title='产品'),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 更新文本
    fig.update_traces(
        texttemplate='¥%{x:,.2f}',
        textposition='outside'
    )
    
    return fig

def create_new_product_region_chart(region_sales):
    """
    创建新品区域分布图
    
    参数:
        region_sales (DataFrame): 区域销售数据
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if region_sales.empty:
        return None
    
    # 创建饼图
    fig = px.pie(
        region_sales,
        names='所属区域',
        values='求和项:金额（元）',
        title='新品销售区域分布',
        color_discrete_sequence=px.colors.sequential.Blues
    )
    
    # 更新布局
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=80, b=20),
    )
    
    # 更新文本
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    return fig

def create_new_product_growth_chart(monthly_product_sales, top_n=5):
    """
    创建新品增长曲线图
    
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
        title=f'TOP {top_n} 新品增长曲线'
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