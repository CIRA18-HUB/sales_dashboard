# modules/material.py
# 物料使用效率分析模块

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import create_line_chart, create_stacked_bar
from utils.constants import INVENTORY_TURNOVER_RATINGS
from config import COLOR_THEME

def analyze_material_efficiency(sales_data, inventory_data):
    """
    分析物料使用效率
    
    参数:
        sales_data (DataFrame): 销售数据
        inventory_data (DataFrame): 库存数据
    
    返回:
        dict: 包含物料使用效率分析结果的字典
    """
    # 确保包含所需列
    if not {'产品代码', '求和项:数量（箱）', '发运月份'}.issubset(sales_data.columns) or \
       not {'物料', '现有库存'}.issubset(inventory_data.columns):
        return {
            'success': False,
            'message': '数据结构不符合要求，缺少必要列'
        }
    
    try:
        # 按产品代码和月份分组计算销售量
        monthly_sales = sales_data.groupby([
            '产品代码', pd.Grouper(key='发运月份', freq='M')
        ])['求和项:数量（箱）'].sum().reset_index()
        
        # 计算每个产品的月平均销售量
        avg_monthly_sales = monthly_sales.groupby('产品代码')['求和项:数量（箱）'].mean().reset_index()
        avg_monthly_sales.rename(columns={'求和项:数量（箱）': '月平均销量'}, inplace=True)
        
        # 库存数据处理（简化处理：直接使用物料作为产品代码）
        # 在实际应用中，应该使用产品代码和物料代码的映射关系
        inventory_summary = inventory_data.groupby('物料').agg({
            '现有库存': 'sum',
            '已分配量': 'sum',
            '现有库存可订量': 'sum',
            '待入库量': 'sum'
        }).reset_index()
        
        # 将物料当作产品代码（简化处理）
        inventory_summary.rename(columns={'物料': '产品代码'}, inplace=True)
        
        # 合并销售和库存数据
        efficiency_data = pd.merge(
            inventory_summary,
            avg_monthly_sales,
            on='产品代码',
            how='left'
        )
        
        # 处理缺失值（没有销售记录的产品）
        efficiency_data['月平均销量'].fillna(0, inplace=True)
        
        # 计算库存周转率（月平均销量/现有库存）
        # 避免除以零
        efficiency_data['库存周转率'] = np.where(
            efficiency_data['现有库存'] > 0,
            efficiency_data['月平均销量'] / efficiency_data['现有库存'],
            0
        )
        
        # 计算库存覆盖天数（现有库存/(月平均销量/30)）
        # 避免除以零
        efficiency_data['库存覆盖天数'] = np.where(
            efficiency_data['月平均销量'] > 0,
            efficiency_data['现有库存'] / (efficiency_data['月平均销量'] / 30),
            float('inf')  # 如果没有销售，则覆盖天数为无穷大
        )
        
        # 添加产品名称
        product_names = sales_data[['产品代码', '产品名称', '产品简称']].drop_duplicates()
        efficiency_data = pd.merge(
            efficiency_data,
            product_names,
            on='产品代码',
            how='left'
        )
        
        # 计算周转率评级
        def get_turnover_rating(rate):
            if rate >= 2.0:
                return INVENTORY_TURNOVER_RATINGS['EXCELLENT']
            elif rate >= 1.5:
                return INVENTORY_TURNOVER_RATINGS['GOOD']
            elif rate >= 1.0:
                return INVENTORY_TURNOVER_RATINGS['NORMAL']
            elif rate >= 0.5:
                return INVENTORY_TURNOVER_RATINGS['POOR']
            else:
                return INVENTORY_TURNOVER_RATINGS['VERY_POOR']
        
        efficiency_data['周转率评级'] = efficiency_data['库存周转率'].apply(get_turnover_rating)
        
        # 计算总体指标
        overall_metrics = {
            'avg_turnover_rate': efficiency_data['库存周转率'].mean(),
            'avg_coverage_days': efficiency_data['库存覆盖天数'].replace([np.inf, -np.inf], np.nan).mean(),
            'low_turnover_products': len(efficiency_data[efficiency_data['库存周转率'] < 0.5]),
            'high_turnover_products': len(efficiency_data[efficiency_data['库存周转率'] > 2.0]),
            'total_products': len(efficiency_data)
        }
        
        # 按周转率评级分组统计
        rating_counts = efficiency_data['周转率评级'].value_counts().to_dict()
        
        # 返回结果
        return {
            'success': True,
            'efficiency_data': efficiency_data,
            'overall_metrics': overall_metrics,
            'rating_counts': rating_counts
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'分析过程中出错: {str(e)}'
        }

def get_material_efficiency_insights(analysis_result):
    """
    生成物料使用效率洞察
    
    参数:
        analysis_result (dict): 物料使用效率分析结果
        
    返回:
        str: 洞察文本
    """
    if not analysis_result['success']:
        return f"无法生成洞察: {analysis_result['message']}"
    
    metrics = analysis_result['overall_metrics']
    
    # 生成洞察文本
    insights = []
    
    # 总体周转率评价
    avg_turnover = metrics['avg_turnover_rate']
    if avg_turnover >= 2.0:
        insights.append("**总体库存周转率表现优异**，说明库存管理效率很高。")
    elif avg_turnover >= 1.5:
        insights.append("**总体库存周转率表现良好**，库存管理整体有效。")
    elif avg_turnover >= 1.0:
        insights.append("**总体库存周转率表现一般**，有改进空间。")
    elif avg_turnover >= 0.5:
        insights.append("**总体库存周转率较低**，需要改进库存管理策略。")
    else:
        insights.append("**总体库存周转率很低**，库存积压严重，亟需优化库存策略。")
    
    # 覆盖天数分析
    avg_coverage = metrics['avg_coverage_days']
    if avg_coverage <= 30:
        insights.append(f"平均库存覆盖天数为**{avg_coverage:.0f}天**，较短，存在缺货风险。")
    elif avg_coverage <= 60:
        insights.append(f"平均库存覆盖天数为**{avg_coverage:.0f}天**，合理。")
    elif avg_coverage <= 90:
        insights.append(f"平均库存覆盖天数为**{avg_coverage:.0f}天**，略长，但可接受。")
    else:
        insights.append(f"平均库存覆盖天数为**{avg_coverage:.0f}天**，过长，资金占用较多。")
    
    # 产品周转率分布
    low_percentage = metrics['low_turnover_products'] / metrics['total_products'] * 100
    high_percentage = metrics['high_turnover_products'] / metrics['total_products'] * 100
    
    if low_percentage > 30:
        insights.append(f"**{low_percentage:.1f}%的产品周转率低于0.5**，建议重点关注这些产品的库存优化。")
    
    if high_percentage > 30:
        insights.append(f"**{high_percentage:.1f}%的产品周转率高于2.0**，这些产品的库存管理效率很高。")
    
    # 建议措施
    if avg_turnover < 1.0:
        insights.append("\n**建议措施**：\n"
                       "1. 对低周转产品制定专项销售计划\n"
                       "2. 调整库存策略，减少低周转产品的采购量\n"
                       "3. 考虑促销活动清理库存\n"
                       "4. 优化产品结构，逐步淘汰持续低周转的产品")
    elif low_percentage > 20:
        insights.append("\n**建议措施**：\n"
                       f"1. 重点关注{metrics['low_turnover_products']}个低周转产品\n"
                       "2. 针对不同产品类别制定差异化的库存策略\n"
                       "3. 加强销售预测准确性，提高库存管理精度")
    else:
        insights.append("\n**建议措施**：\n"
                       "1. 保持当前的库存管理策略\n"
                       "2. 持续监控库存周转率变化趋势\n"
                       "3. 季度性评估产品组合的库存效率")
    
    return "\n\n".join(insights)

def get_top_low_turnover_products(analysis_result, top_n=5):
    """
    获取周转率最低的前N个产品
    
    参数:
        analysis_result (dict): 物料使用效率分析结果
        top_n (int): 返回的产品数量
        
    返回:
        DataFrame: 周转率最低的产品
    """
    if not analysis_result['success']:
        return pd.DataFrame()
    
    efficiency_data = analysis_result['efficiency_data']
    
    # 按库存周转率升序排序
    low_turnover = efficiency_data.sort_values('库存周转率').head(top_n)
    
    return low_turnover[['产品代码', '产品简称', '现有库存', '月平均销量', '库存周转率', '库存覆盖天数']]

def create_turnover_histogram(analysis_result, bin_size=0.2):
    """
    创建库存周转率分布直方图
    
    参数:
        analysis_result (dict): 物料使用效率分析结果
        bin_size (float): 直方图箱宽
        
    返回:
        plotly.graph_objects.Figure: 直方图对象
    """
    if not analysis_result['success']:
        return None
    
    efficiency_data = analysis_result['efficiency_data']
    
    # 创建直方图
    fig = px.histogram(
        efficiency_data, 
        x='库存周转率',
        nbins=int(max(efficiency_data['库存周转率']) / bin_size) + 1,
        title='库存周转率分布',
        color_discrete_sequence=[COLOR_THEME['primary']]
    )
    
    fig.update_layout(
        xaxis_title='库存周转率',
        yaxis_title='产品数量',
        bargap=0.1,
        xaxis=dict(
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
            ticktext=['0.5', '1.0', '1.5', '2.0', '2.5', '3.0+']
        )
    )
    
    # 添加垂直线表示评级边界
    boundaries = [0.5, 1.0, 1.5, 2.0]
    colors = [COLOR_THEME['warning'], COLOR_THEME['secondary'], COLOR_THEME['primary'], COLOR_THEME['success']]
    labels = ['不佳', '一般', '良好', '优秀']
    
    for boundary, color, label in zip(boundaries, colors, labels):
        fig.add_shape(
            type="line",
            x0=boundary, y0=0, x1=boundary, y1=1,
            yref="paper",
            line=dict(color=color, width=2, dash="dash")
        )
        
        fig.add_annotation(
            x=boundary,
            y=1,
            yref="paper",
            text=label,
            showarrow=False,
            textangle=-90,
            xanchor="center",
            yanchor="top",
            font=dict(size=10, color=color)
        )
    
    return fig

def create_turnover_rating_pie(analysis_result):
    """
    创建周转率评级饼图
    
    参数:
        analysis_result (dict): 物料使用效率分析结果
        
    返回:
        plotly.graph_objects.Figure: 饼图对象
    """
    if not analysis_result['success']:
        return None
    
    efficiency_data = analysis_result['efficiency_data']
    
    # 计算每个评级的产品数量
    rating_counts = efficiency_data['周转率评级'].value_counts().reset_index()
    rating_counts.columns = ['评级', '产品数量']
    
    # 设置颜色映射
    color_map = {
        INVENTORY_TURNOVER_RATINGS['EXCELLENT']: COLOR_THEME['success'],
        INVENTORY_TURNOVER_RATINGS['GOOD']: COLOR_THEME['primary'],
        INVENTORY_TURNOVER_RATINGS['NORMAL']: COLOR_THEME['secondary'],
        INVENTORY_TURNOVER_RATINGS['POOR']: COLOR_THEME['warning'],
        INVENTORY_TURNOVER_RATINGS['VERY_POOR']: COLOR_THEME['warning']
    }
    
    # 创建饼图
    fig = px.pie(
        rating_counts,
        names='评级',
        values='产品数量',
        title='库存周转率评级分布',
        color='评级',
        color_discrete_map=color_map,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    return fig