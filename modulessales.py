# modules/sales.py
# 销售金额分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_line_chart, create_heatmap, create_stacked_bar
from utils.constants import ACHIEVEMENT_RATINGS
from config import COLOR_THEME

def analyze_sales_data(sales_data, target_data=None, period='monthly'):
    """
    分析销售数据
    
    参数:
        sales_data (DataFrame): 销售数据
        target_data (DataFrame): 目标数据，可选
        period (str): 分析周期，可以是'monthly', 'quarterly', 'yearly'
        
    返回:
        dict: 包含销售分析结果的字典
    """
    # 确保包含所需列
    if not {'产品代码', '求和项:金额（元）', '发运月份', '订单类型', '所属区域', '申请人'}.issubset(sales_data.columns):
        return {
            'success': False,
            'message': '销售数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 计算总销售额
        total_sales = sales_data['求和项:金额（元）'].sum()
        
        # 按月份分组计算销售额
        monthly_sales = sales_data.groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        
        # 按订单类型计算销售额
        order_type_sales = sales_data.groupby('订单类型')['求和项:金额（元）'].sum().reset_index()
        
        # 创建渠道销售数据
        channel_sales = pd.DataFrame()
        channel_sales['渠道'] = ['MT渠道', 'TT渠道']
        channel_sales['销售额'] = [
            sales_data[sales_data['订单类型'] == '订单-正常产品']['求和项:金额（元）'].sum(),
            sales_data[sales_data['订单类型'] == '订单-TT产品']['求和项:金额（元）'].sum()
        ]
        
        # 按区域分组计算销售额
        region_sales = sales_data.groupby('所属区域')['求和项:金额（元）'].sum().reset_index()
        
        # 按销售人员分组计算销售额
        salesperson_sales = sales_data.groupby('申请人')['求和项:金额（元）'].sum().reset_index()
        salesperson_sales = salesperson_sales.sort_values('求和项:金额（元）', ascending=False)
        
        # 计算每个月的MT和TT渠道销售额
        mt_monthly = sales_data[sales_data['订单类型'] == '订单-正常产品'].groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        mt_monthly['渠道'] = 'MT渠道'
        
        tt_monthly = sales_data[sales_data['订单类型'] == '订单-TT产品'].groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['求和项:金额（元）'].sum().reset_index()
        tt_monthly['渠道'] = 'TT渠道'
        
        channel_monthly_sales = pd.concat([mt_monthly, tt_monthly])
        
        # 目标达成分析
        achievement_data = None
        if target_data is not None and not target_data.empty:
            # 按月份和销售人员分组计算销售额
            sales_by_person_month = sales_data.groupby([
                pd.Grouper(key='发运月份', freq='M'), '申请人'
            ])['求和项:金额（元）'].sum().reset_index()
            
            # 将月份格式调整为与目标数据相同
            sales_by_person_month['月份'] = sales_by_person_month['发运月份'].dt.to_period('M').dt.to_timestamp()
            
            # 将目标数据的月份格式调整
            if '指标年月' in target_data.columns:
                target_data['月份'] = pd.to_datetime(target_data['指标年月'])
            
            # 合并销售数据和目标数据
            achievement_data = pd.merge(
                sales_by_person_month,
                target_data[['月份', '申请人', '月度指标']],
                on=['月份', '申请人'],
                how='left'
            )
            
            # 计算达成率
            achievement_data['达成率'] = achievement_data['求和项:金额（元）'] / achievement_data['月度指标']
            
            # 按区域和月份计算达成率
            region_achievement = sales_data.groupby([
                '所属区域', pd.Grouper(key='发运月份', freq='M')
            ])['求和项:金额（元）'].sum().reset_index()
            
            # 将月份格式调整
            region_achievement['月份'] = region_achievement['发运月份'].dt.to_period('M').dt.to_timestamp()
            
            # 按区域和月份汇总目标
            region_target = target_data.groupby(['所属大区', '月份'])['月度指标'].sum().reset_index()
            region_target.rename(columns={'所属大区': '所属区域'}, inplace=True)
            
            # 合并区域销售和目标数据
            region_achievement = pd.merge(
                region_achievement,
                region_target,
                on=['所属区域', '月份'],
                how='left'
            )
            
            # 计算区域达成率
            region_achievement['达成率'] = region_achievement['求和项:金额（元）'] / region_achievement['月度指标']
        
        # 计算季度和年度数据
        quarterly_sales = monthly_sales.copy()
        quarterly_sales['季度'] = quarterly_sales['发运月份'].dt.to_period('Q').dt.to_timestamp()
        quarterly_sales = quarterly_sales.groupby('季度')['求和项:金额（元）'].sum().reset_index()
        
        yearly_sales = monthly_sales.copy()
        yearly_sales['年份'] = yearly_sales['发运月份'].dt.to_period('Y').dt.to_timestamp()
        yearly_sales = yearly_sales.groupby('年份')['求和项:金额（元）'].sum().reset_index()
        
        # 返回结果
        return {
            'success': True,
            'total_sales': total_sales,
            'monthly_sales': monthly_sales,
            'quarterly_sales': quarterly_sales,
            'yearly_sales': yearly_sales,
            'order_type_sales': order_type_sales,
            'channel_sales': channel_sales,
            'channel_monthly_sales': channel_monthly_sales,
            'region_sales': region_sales,
            'salesperson_sales': salesperson_sales,
            'achievement_data': achievement_data,
            'region_achievement': region_achievement if 'region_achievement' in locals() else None
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_sales_growth(monthly_sales, compare_months=3):
    """
    计算销售增长率
    
    参数:
        monthly_sales (DataFrame): 月度销售数据
        compare_months (int): 比较的月数
        
    返回:
        float: 增长率
    """
    if len(monthly_sales) < compare_months + 1:
        return 0.0
    
    # 获取最近N个月和前N个月的销售额
    recent_sales = monthly_sales.iloc[-compare_months:]['求和项:金额（元）'].sum()
    previous_sales = monthly_sales.iloc[-(compare_months*2):-compare_months]['求和项:金额（元）'].sum()
    
    # 计算增长率
    if previous_sales > 0:
        return (recent_sales - previous_sales) / previous_sales
    else:
        return 0.0

def get_sales_insights(analysis_result):
    """
    生成销售洞察
    
    参数:
        analysis_result (dict): 销售分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    insights = []
    
    # 总销售额洞察
    total_sales = analysis_result['total_sales']
    insights.append(f"总销售额为 **¥{total_sales:,.2f}**。")
    
    # 渠道分析洞察
    channel_sales = analysis_result['channel_sales']
    mt_sales = channel_sales[channel_sales['渠道'] == 'MT渠道']['销售额'].values[0]
    tt_sales = channel_sales[channel_sales['渠道'] == 'TT渠道']['销售额'].values[0]
    
    mt_percentage = mt_sales / total_sales * 100 if total_sales > 0 else 0
    tt_percentage = tt_sales / total_sales * 100 if total_sales > 0 else 0
    
    insights.append(f"MT渠道占比 **{mt_percentage:.1f}%**，TT渠道占比 **{tt_percentage:.1f}%**。")
    
    # 销售趋势洞察
    monthly_sales = analysis_result['monthly_sales']
    if len(monthly_sales) >= 2:
        latest_month_sales = monthly_sales.iloc[-1]['求和项:金额（元）']
        previous_month_sales = monthly_sales.iloc[-2]['求和项:金额（元）']
        mom_change = (latest_month_sales - previous_month_sales) / previous_month_sales if previous_month_sales > 0 else 0
        
        if mom_change > 0:
            insights.append(f"最新月销售额环比增长 **{mom_change:.1%}**，呈上升趋势。")
        elif mom_change < 0:
            insights.append(f"最新月销售额环比下降 **{abs(mom_change):.1%}**，需关注原因。")
        else:
            insights.append("最新月销售额与上月持平。")
    
    # 计算3个月销售增长率
    sales_growth = get_sales_growth(monthly_sales)
    if sales_growth > 0:
        insights.append(f"近3个月销售同比增长 **{sales_growth:.1%}**。")
    elif sales_growth < 0:
        insights.append(f"近3个月销售同比下降 **{abs(sales_growth):.1%}**。")
    
    # 销售达成洞察
    if analysis_result['achievement_data'] is not None:
        achievement_data = analysis_result['achievement_data']
        avg_achievement = achievement_data['达成率'].mean()
        
        if avg_achievement >= 1.0:
            insights.append(f"整体目标达成率为 **{avg_achievement:.1%}**，表现优秀。")
        elif avg_achievement >= 0.9:
            insights.append(f"整体目标达成率为 **{avg_achievement:.1%}**，接近目标。")
        elif avg_achievement >= 0.8:
            insights.append(f"整体目标达成率为 **{avg_achievement:.1%}**，仍有差距。")
        else:
            insights.append(f"整体目标达成率为 **{avg_achievement:.1%}**，差距较大，需重点关注。")
    
    # 区域洞察
    region_sales = analysis_result['region_sales']
    top_region = region_sales.sort_values('求和项:金额（元）', ascending=False).iloc[0]
    
    top_region_percentage = top_region['求和项:金额（元）'] / total_sales * 100 if total_sales > 0 else 0
    
    insights.append(f"**{top_region['所属区域']}**区域销售额最高，占总销售额的 **{top_region_percentage:.1f}%**。")
    
    # 销售人员洞察
    salesperson_sales = analysis_result['salesperson_sales']
    if not salesperson_sales.empty:
        top_salesperson = salesperson_sales.iloc[0]
        top_salesperson_percentage = top_salesperson['求和项:金额（元）'] / total_sales * 100 if total_sales > 0 else 0
        
        insights.append(f"**{top_salesperson['申请人']}**销售额最高，占总销售额的 **{top_salesperson_percentage:.1f}%**。")
    
    return "\n\n".join(insights)

def create_achievement_heatmap(achievement_data):
    """
    创建达成率热力图
    
    参数:
        achievement_data (DataFrame): 达成率数据
        
    返回:
        plotly.graph_objects.Figure: 热力图对象
    """
    if achievement_data is None or achievement_data.empty:
        return None
    
    # 透视表转换数据格式
    pivot_data = achievement_data.pivot(
        index='申请人',
        columns='月份',
        values='达成率'
    ).reset_index()
    
    # 填充缺失值
    pivot_data = pivot_data.fillna(0)
    
    # 获取月份列表
    months = sorted([col for col in pivot_data.columns if isinstance(col, pd.Timestamp)])
    
    # 创建热力图数据
    z_data = []
    y_data = []
    
    for _, row in pivot_data.iterrows():
        y_data.append(row['申请人'])
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
        title='销售达成率热力图 (按销售人员和月份)',
        xaxis=dict(title='月份'),
        yaxis=dict(title='销售人员'),
        margin=dict(l=50, r=50, t=80, b=50),
        height=500,
    )
    
    return fig

def create_sales_comparison_chart(analysis_result):
    """
    创建销售对比图（实际销售额与目标）
    
    参数:
        analysis_result (dict): 销售分析结果
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if not analysis_result['success'] or analysis_result['achievement_data'] is None:
        return None
    
    # 按月份汇总实际销售额和目标
    achievement_data = analysis_result['achievement_data']
    monthly_summary = achievement_data.groupby('月份').agg({
        '求和项:金额（元）': 'sum',
        '月度指标': 'sum'
    }).reset_index()
    
    # 计算达成率
    monthly_summary['达成率'] = monthly_summary['求和项:金额（元）'] / monthly_summary['月度指标']
    
    # 创建图表
    fig = go.Figure()
    
    # 添加实际销售额柱状图
    fig.add_trace(go.Bar(
        x=monthly_summary['月份'],
        y=monthly_summary['求和项:金额（元）'],
        name='实际销售额',
        marker_color=COLOR_THEME['primary']
    ))
    
    # 添加目标销售额柱状图
    fig.add_trace(go.Bar(
        x=monthly_summary['月份'],
        y=monthly_summary['月度指标'],
        name='目标销售额',
        marker_color=COLOR_THEME['secondary'],
        opacity=0.7
    ))
    
    # 添加达成率线
    fig.add_trace(go.Scatter(
        x=monthly_summary['月份'],
        y=monthly_summary['达成率'],
        name='达成率',
        mode='lines+markers',
        line=dict(color=COLOR_THEME['success'], width=2),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # 更新布局
    fig.update_layout(
        title='月度销售额与目标对比',
        xaxis=dict(title='月份'),
        yaxis=dict(title='销售额 (元)'),
        yaxis2=dict(
            title='达成率',
            titlefont=dict(color=COLOR_THEME['success']),
            tickfont=dict(color=COLOR_THEME['success']),
            overlaying='y',
            side='right',
            showgrid=False,
            tickformat='.0%',
            range=[0, max(monthly_summary['达成率']) * 1.1]
        ),
        barmode='group',
        legend=dict(
            x=0,
            y=1.1,
            orientation='h'
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig