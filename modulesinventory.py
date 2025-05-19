# modules/inventory.py
# 库存分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_line_chart, create_stacked_bar
from config import COLOR_THEME

def analyze_inventory_data(sales_data, inventory_data, monthly_inventory=None, forecast_data=None):
    """
    分析库存数据
    
    参数:
        sales_data (DataFrame): 销售数据
        inventory_data (DataFrame): 实时库存数据
        monthly_inventory (DataFrame): 月终月末库存数据，可选
        forecast_data (DataFrame): 预测数据，可选
        
    返回:
        dict: 包含库存分析结果的字典
    """
    # 确保包含所需列
    if not {'产品代码', '求和项:数量（箱）', '发运月份'}.issubset(sales_data.columns) or \
       not {'物料', '现有库存', '已分配量', '现有库存可订量'}.issubset(inventory_data.columns):
        return {
            'success': False,
            'message': '数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 产品级库存分析
        product_inventory = inventory_data.groupby('物料').agg({
            '现有库存': 'sum',
            '已分配量': 'sum',
            '现有库存可订量': 'sum',
            '待入库量': 'sum'
        }).reset_index()
        
        # 月度销售量统计
        monthly_sales_volume = sales_data.groupby([
            '产品代码', pd.Grouper(key='发运月份', freq='M')
        ])['求和项:数量（箱）'].sum().reset_index()
        
        # 计算每个产品的平均月销量
        avg_monthly_sales = monthly_sales_volume.groupby('产品代码')['求和项:数量（箱）'].mean().reset_index()
        avg_monthly_sales.rename(columns={'求和项:数量（箱）': '月平均销量'}, inplace=True)
        
        # 合并产品库存和销售数据（假设产品代码与物料代码相同）
        inventory_analysis = pd.merge(
            product_inventory,
            avg_monthly_sales,
            left_on='物料',
            right_on='产品代码',
            how='left'
        )
        
        # 处理缺失值
        inventory_analysis['月平均销量'].fillna(0, inplace=True)
        
        # 计算库存覆盖天数（现有库存/(月平均销量/30)）
        inventory_analysis['库存覆盖天数'] = np.where(
            inventory_analysis['月平均销量'] > 0,
            inventory_analysis['现有库存'] / (inventory_analysis['月平均销量'] / 30),
            float('inf')  # 如果没有销售，则覆盖天数为无穷大
        )
        
        # 计算清库周期（月）
        inventory_analysis['清库周期(月)'] = np.where(
            inventory_analysis['月平均销量'] > 0,
            inventory_analysis['现有库存'] / inventory_analysis['月平均销量'],
            float('inf')  # 如果没有销售，则清库周期为无穷大
        )
        
        # 计算库存健康指数
        # 1. 过低库存（覆盖天数<15天）: 风险
        # 2. 正常库存（15天<=覆盖天数<=60天）: 健康
        # 3. 高库存（覆盖天数>60天）: 风险
        def get_inventory_health(days):
            if days < 15:
                return '库存不足'
            elif days <= 60:
                return '库存健康'
            else:
                return '库存过剩'
        
        inventory_analysis['库存健康状态'] = inventory_analysis['库存覆盖天数'].apply(get_inventory_health)
        
        # 计算库存积压风险
        # 1. 低风险（清库周期<=1个月）
        # 2. 中风险（1个月<清库周期<=3个月）
        # 3. 高风险（清库周期>3个月）
        def get_inventory_risk(months):
            if months <= 1:
                return '低风险'
            elif months <= 3:
                return '中风险'
            else:
                return '高风险'
        
        inventory_analysis['积压风险'] = inventory_analysis['清库周期(月)'].apply(get_inventory_risk)
        
        # 批次级库存分析
        batch_inventory = None
        if '生产日期' in inventory_data.columns and '生产批号' in inventory_data.columns:
            # 计算批次库龄
            today = datetime.now()
            
            batch_inventory = inventory_data[inventory_data['生产日期'].notna()].copy()
            batch_inventory['生产日期'] = pd.to_datetime(batch_inventory['生产日期'])
            batch_inventory['库龄(天)'] = (today - batch_inventory['生产日期']).dt.days
            
            # 计算批次价值
            batch_inventory['批次价值'] = batch_inventory['数量']  # 假设这里有单价信息，可以计算实际价值
            
            # 计算库龄风险
            def get_age_risk(age):
                if age <= 30:
                    return '新鲜'
                elif age <= 90:
                    return '正常'
                elif age <= 180:
                    return '老化'
                else:
                    return '过期风险'
            
            batch_inventory['库龄风险'] = batch_inventory['库龄(天)'].apply(get_age_risk)
        
        # 月终月末库存分析
        monthly_inventory_trend = None
        if monthly_inventory is not None and not monthly_inventory.empty:
            # 确保有所需列
            if {'产品名称', '产品代码', '所属年月', '每月1日初库存', '每月末库存'}.issubset(monthly_inventory.columns):
                # 计算月度库存变化
                monthly_inventory_trend = monthly_inventory.copy()
                
                # 处理缺失的月末库存（当月还未到月底）
                current_month = pd.Timestamp(datetime.now().year, datetime.now().month, 1)
                monthly_inventory_trend.loc[
                    monthly_inventory_trend['所属年月'] == current_month,
                    '每月末库存'
                ] = None
                
                # 计算库存变化率
                monthly_inventory_trend['库存变化量'] = monthly_inventory_trend['每月末库存'] - monthly_inventory_trend['每月1日初库存']
                monthly_inventory_trend['库存变化率'] = monthly_inventory_trend['库存变化量'] / monthly_inventory_trend['每月1日初库存']
        
        # 销售预测与库存对比分析
        forecast_vs_inventory = None
        if forecast_data is not None and not forecast_data.empty:
            # 确保有所需列
            if {'所属年月', '产品代码', '预计销售量'}.issubset(forecast_data.columns):
                # 按产品和月份汇总预测销售量
                forecast_summary = forecast_data.groupby(['产品代码', '所属年月'])['预计销售量'].sum().reset_index()
                
                # 合并当前库存数据和预测数据
                forecast_vs_inventory = pd.merge(
                    product_inventory[['物料', '现有库存']],
                    forecast_summary,
                    left_on='物料',
                    right_on='产品代码',
                    how='inner'
                )
                
                # 计算预测覆盖率
                forecast_vs_inventory['预测覆盖率'] = forecast_vs_inventory['现有库存'] / forecast_vs_inventory['预计销售量']
                
                # 根据预测覆盖率添加状态
                def get_forecast_status(ratio):
                    if ratio < 0.5:
                        return '库存不足'
                    elif ratio <= 1.5:
                        return '库存适中'
                    else:
                        return '库存过剩'
                
                forecast_vs_inventory['预测库存状态'] = forecast_vs_inventory['预测覆盖率'].apply(get_forecast_status)
        
        # 库存整体统计指标
        total_inventory = product_inventory['现有库存'].sum()
        assigned_inventory = product_inventory['已分配量'].sum()
        orderable_inventory = product_inventory['现有库存可订量'].sum()
        pending_inventory = product_inventory['待入库量'].sum()
        
        # 库存健康状况分布
        health_distribution = inventory_analysis['库存健康状态'].value_counts().to_dict()
        
        # 积压风险分布
        risk_distribution = inventory_analysis['积压风险'].value_counts().to_dict()
        
        # 返回结果
        return {
            'success': True,
            'total_inventory': total_inventory,
            'assigned_inventory': assigned_inventory,
            'orderable_inventory': orderable_inventory,
            'pending_inventory': pending_inventory,
            'product_inventory': product_inventory,
            'inventory_analysis': inventory_analysis,
            'batch_inventory': batch_inventory,
            'monthly_inventory_trend': monthly_inventory_trend,
            'forecast_vs_inventory': forecast_vs_inventory,
            'health_distribution': health_distribution,
            'risk_distribution': risk_distribution
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_inventory_insights(analysis_result):
    """
    生成库存洞察
    
    参数:
        analysis_result (dict): 库存分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    insights = []
    
    # 库存总量洞察
    total_inventory = analysis_result['total_inventory']
    assigned_inventory = analysis_result['assigned_inventory']
    orderable_inventory = analysis_result['orderable_inventory']
    pending_inventory = analysis_result['pending_inventory']
    
    assigned_percentage = assigned_inventory / total_inventory * 100 if total_inventory > 0 else 0
    
    insights.append(f"**库存总览**:\n"
                   f"- 总库存量: **{total_inventory:,.0f}**\n"
                   f"- 已分配量: **{assigned_inventory:,.0f}** ({assigned_percentage:.1f}%)\n"
                   f"- 可订量: **{orderable_inventory:,.0f}**\n"
                   f"- 待入库量: **{pending_inventory:,.0f}**")
    
    # 库存健康状况洞察
    health_distribution = analysis_result['health_distribution']
    
    healthy_count = health_distribution.get('库存健康', 0)
    low_count = health_distribution.get('库存不足', 0)
    high_count = health_distribution.get('库存过剩', 0)
    total_count = healthy_count + low_count + high_count
    
    healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0
    low_percentage = low_count / total_count * 100 if total_count > 0 else 0
    high_percentage = high_count / total_count * 100 if total_count > 0 else 0
    
    insights.append(f"**库存健康状况**:\n"
                   f"- 库存健康: **{healthy_count}个产品 ({healthy_percentage:.1f}%)**\n"
                   f"- 库存不足: **{low_count}个产品 ({low_percentage:.1f}%)**\n"
                   f"- 库存过剩: **{high_count}个产品 ({high_percentage:.1f}%)**")
    
    # 积压风险洞察
    risk_distribution = analysis_result['risk_distribution']
    
    low_risk = risk_distribution.get('低风险', 0)
    medium_risk = risk_distribution.get('中风险', 0)
    high_risk = risk_distribution.get('高风险', 0)
    total_risk = low_risk + medium_risk + high_risk
    
    low_risk_percentage = low_risk / total_risk * 100 if total_risk > 0 else 0
    medium_risk_percentage = medium_risk / total_risk * 100 if total_risk > 0 else 0
    high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0
    
    insights.append(f"**积压风险分析**:\n"
                   f"- 低风险: **{low_risk}个产品 ({low_risk_percentage:.1f}%)**\n"
                   f"- 中风险: **{medium_risk}个产品 ({medium_risk_percentage:.1f}%)**\n"
                   f"- 高风险: **{high_risk}个产品 ({high_risk_percentage:.1f}%)**")
    
    # 批次库存洞察
    batch_inventory = analysis_result.get('batch_inventory')
    
    if batch_inventory is not None and not batch_inventory.empty:
        # 计算批次库龄分布
        age_risk_counts = batch_inventory['库龄风险'].value_counts().to_dict()
        
        fresh_count = age_risk_counts.get('新鲜', 0)
        normal_count = age_risk_counts.get('正常', 0)
        aged_count = age_risk_counts.get('老化', 0)
        expired_count = age_risk_counts.get('过期风险', 0)
        
        insights.append(f"**批次库龄分析**:\n"
                       f"- 新鲜批次: **{fresh_count}个**\n"
                       f"- 正常批次: **{normal_count}个**\n"
                       f"- 老化批次: **{aged_count}个**\n"
                       f"- 过期风险批次: **{expired_count}个**")
    
    # 预测与库存对比洞察
    forecast_vs_inventory = analysis_result.get('forecast_vs_inventory')
    
    if forecast_vs_inventory is not None and not forecast_vs_inventory.empty:
        # 计算预测库存状态分布
        forecast_status_counts = forecast_vs_inventory['预测库存状态'].value_counts().to_dict()
        
        low_forecast = forecast_status_counts.get('库存不足', 0)
        normal_forecast = forecast_status_counts.get('库存适中', 0)
        high_forecast = forecast_status_counts.get('库存过剩', 0)
        
        insights.append(f"**预测与库存对比**:\n"
                       f"- 库存不足(相对预测): **{low_forecast}个产品**\n"
                       f"- 库存适中(相对预测): **{normal_forecast}个产品**\n"
                       f"- 库存过剩(相对预测): **{high_forecast}个产品**")
    
    # 月度库存趋势洞察
    monthly_inventory_trend = analysis_result.get('monthly_inventory_trend')
    
    if monthly_inventory_trend is not None and not monthly_inventory_trend.empty:
        # 计算最近月份的库存变化
        latest_month_data = monthly_inventory_trend.sort_values('所属年月', ascending=False).iloc[0]
        if not pd.isna(latest_month_data['库存变化率']):
            change_rate = latest_month_data['库存变化率'] * 100
            change_description = "增长" if change_rate > 0 else "下降"
            
            insights.append(f"**最近月度库存变化**:\n"
                           f"- 初库存: **{latest_month_data['每月1日初库存']:,.0f}**\n"
                           f"- 月末库存: **{latest_month_data['每月末库存']:,.0f}**\n"
                           f"- 库存{change_description}: **{abs(change_rate):.1f}%**")
    
    # 库存优化建议
    suggestions = []
    
    if high_percentage > 30:
        suggestions.append("关注库存过剩产品，考虑促销或调整采购计划")
    
    if low_percentage > 20:
        suggestions.append("关注库存不足产品，及时补充库存")
    
    if high_risk_percentage > 20:
        suggestions.append("重点处理高积压风险产品，制定清库计划")
    
    if batch_inventory is not None and not batch_inventory.empty:
        if expired_count > 0:
            suggestions.append(f"紧急处理{expired_count}个过期风险批次")
        
        if aged_count > 0:
            suggestions.append(f"优先销售{aged_count}个老化批次")
    
    if suggestions:
        insights.append("**库存优化建议**:\n- " + "\n- ".join(suggestions))
    
    return "\n\n".join(insights)

def create_inventory_health_pie(health_distribution):
    """
    创建库存健康状况饼图
    
    参数:
        health_distribution (dict): 库存健康状况分布
        
    返回:
        plotly.graph_objects.Figure: 饼图对象
    """
    # 准备数据
    labels = []
    values = []
    colors = []
    
    for status, count in health_distribution.items():
        labels.append(status)
        values.append(count)
        
        if status == '库存健康':
            colors.append(COLOR_THEME['success'])
        elif status == '库存不足':
            colors.append(COLOR_THEME['warning'])
        else:  # 库存过剩
            colors.append(COLOR_THEME['secondary'])
    
    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4
    )])
    
    fig.update_layout(
        title='库存健康状况分布',
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

def create_risk_distribution_chart(risk_distribution):
    """
    创建积压风险分布图
    
    参数:
        risk_distribution (dict): 积压风险分布
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    # 准备数据
    categories = []
    values = []
    colors = []
    
    for risk, count in risk_distribution.items():
        categories.append(risk)
        values.append(count)
        
        if risk == '低风险':
            colors.append(COLOR_THEME['success'])
        elif risk == '中风险':
            colors.append(COLOR_THEME['secondary'])
        else:  # 高风险
            colors.append(COLOR_THEME['warning'])
    
    # 创建柱状图
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=colors
    )])
    
    fig.update_layout(
        title='库存积压风险分布',
        xaxis=dict(title='风险等级'),
        yaxis=dict(title='产品数量'),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 添加数据标签
    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )
    
    return fig

def create_batch_age_chart(batch_inventory):
    """
    创建批次库龄分布图
    
    参数:
        batch_inventory (DataFrame): 批次库存数据
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if batch_inventory is None or batch_inventory.empty:
        return None
    
    # 计算库龄分布
    age_bins = [0, 30, 90, 180, 365, float('inf')]
    age_labels = ['0-30天', '31-90天', '91-180天', '181-365天', '>365天']
    
    batch_inventory['库龄分组'] = pd.cut(batch_inventory['库龄(天)'], bins=age_bins, labels=age_labels)
    age_distribution = batch_inventory.groupby('库龄分组').size().reset_index()
    age_distribution.columns = ['库龄分组', '批次数量']
    
    # 颜色映射
    color_scale = [
        COLOR_THEME['success'],  # 0-30天
        COLOR_THEME['primary'],  # 31-90天
        COLOR_THEME['secondary'],  # 91-180天
        COLOR_THEME['warning'],  # 181-365天
        'red'  # >365天
    ]
    
    # 创建柱状图
    fig = go.Figure(data=[go.Bar(
        x=age_distribution['库龄分组'],
        y=age_distribution['批次数量'],
        marker_color=color_scale[:len(age_distribution)]
    )])
    
    fig.update_layout(
        title='批次库龄分布',
        xaxis=dict(title='库龄'),
        yaxis=dict(title='批次数量'),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 添加数据标签
    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )
    
    return fig

def create_inventory_forecast_comparison(forecast_vs_inventory):
    """
    创建库存与预测对比图
    
    参数:
        forecast_vs_inventory (DataFrame): 库存与预测对比数据
        
    返回:
        plotly.graph_objects.Figure: 图表对象
    """
    if forecast_vs_inventory is None or forecast_vs_inventory.empty:
        return None
    
    # 准备数据
    plot_data = forecast_vs_inventory.copy()
    
    # 排序
    plot_data = plot_data.sort_values('预测覆盖率')
    
    # 选择最高和最低的10个产品
    low_coverage = plot_data.head(5)
    high_coverage = plot_data.tail(5)
    
    # 合并数据
    display_data = pd.concat([low_coverage, high_coverage])
    
    # 创建条形图
    fig = px.bar(
        display_data,
        y='产品代码',
        x='预测覆盖率',
        color='预测库存状态',
        orientation='h',
        title='库存预测覆盖率 (最高和最低5个产品)',
        color_discrete_map={
            '库存不足': COLOR_THEME['warning'],
            '库存适中': COLOR_THEME['success'],
            '库存过剩': COLOR_THEME['secondary']
        },
        text='预测覆盖率'
    )
    
    # 更新布局
    fig.update_layout(
        xaxis=dict(title='库存/预测销量'),
        yaxis=dict(title='产品代码'),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # 更新文本
    fig.update_traces(
        texttemplate='%{x:.1f}',
        textposition='outside'
    )
    
    # 添加基准线
    fig.add_shape(
        type="line",
        x0=1, y0=-1, x1=1, y1=len(display_data),
        line=dict(color="red", width=2, dash="dash")
    )
    
    fig.add_annotation(
        x=1,
        y=len(display_data),
        text="库存=预测",
        showarrow=False,
        font=dict(color="red")
    )
    
    return fig