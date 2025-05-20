# utils/helpers.py
# 辅助函数

# utils/helpers.py
# 辅助函数

import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os  # 添加这一行导入os模块
from config import COLOR_THEME, METRIC_CARD_STYLE

# 创建指标卡
def create_metric_card(title, value, change=None, is_percentage=False, prefix="", suffix="", is_currency=False):
    """
    创建一个漂亮的指标卡
    
    参数:
        title (str): 指标标题
        value (float/int): 指标值
        change (float, optional): 变化量
        is_percentage (bool): 是否为百分比
        prefix (str): 前缀
        suffix (str): 后缀
        is_currency (bool): 是否为货币
        
    返回:
        str: HTML格式的指标卡
    """
    # 格式化值
    if is_percentage:
        formatted_value = f"{value:.1f}%"
    elif is_currency:
        formatted_value = f"¥{value:,.2f}"
    else:
        formatted_value = f"{prefix}{value:,.0f}{suffix}"
    
    # 格式化变化量
    change_html = ""
    if change is not None:
        change_class = "positive-change" if change >= 0 else "negative-change"
        change_prefix = "+" if change > 0 else ""
        if is_percentage:
            formatted_change = f"{change_prefix}{change:.1f}%"
        else:
            formatted_change = f"{change_prefix}{change:,.0f}"
        
        change_html = f'<div class="metric-change {change_class}">{formatted_change}</div>'
    
    # 创建HTML卡片
    card_html = f"""
    {METRIC_CARD_STYLE}
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{formatted_value}</div>
        {change_html}
    </div>
    """
    
    return card_html

# 获取当前日期信息
def get_current_date_info():
    """
    获取当前日期信息
    
    返回:
        tuple: (年份, 月份, 是否年末)
    """
    now = datetime.now()
    return now.year, now.month, now.month == 12

# 创建条件格式热力图
def create_heatmap(data, x, y, values, title, color_scale=None, annotation_format=".1%"):
    """
    创建条件格式热力图
    
    参数:
        data (DataFrame): 数据
        x (str): x轴列名
        y (str): y轴列名
        values (str): 值列名
        title (str): 图表标题
        color_scale (list): 颜色刻度
        annotation_format (str): 注释格式
        
    返回:
        plotly.graph_objects.Figure: 热力图对象
    """
    if color_scale is None:
        color_scale = [
            [0, 'red'],
            [0.7, 'yellow'],
            [0.9, 'lightgreen'],
            [1, 'green']
        ]
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=data[values],
        x=data[x],
        y=data[y],
        colorscale=color_scale,
        showscale=True,
        text=data[values],
        texttemplate=annotation_format if '%' in annotation_format else '{text:' + annotation_format + '}',
        textfont={"size": 10},
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(title=x),
        yaxis=dict(title=y),
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
    )
    
    return fig

# 创建BCG矩阵
def create_bcg_matrix(data, title):
    """
    创建BCG矩阵（波士顿矩阵）
    
    参数:
        data (DataFrame): 数据，需要包含'销售占比', '增长率', '产品类型', '产品代码'和'求和项:金额（元）'列
        title (str): 图表标题
        
    返回:
        plotly.graph_objects.Figure: BCG矩阵图对象
    """
    # 设置象限边界
    x_boundary = 0.015  # 1.5%销售占比边界
    y_boundary = 0.2    # 20%增长率边界
    
    # 设置颜色映射
    color_map = {
        '现金牛产品': COLOR_THEME['success'],
        '明星产品': COLOR_THEME['primary'],
        '问号产品': COLOR_THEME['secondary'],
        '瘦狗产品': COLOR_THEME['warning']
    }
    
    # 创建气泡图
    fig = px.scatter(
        data,
        x='销售占比',
        y='增长率',
        size='求和项:金额（元）',
        color='产品类型',
        text='产品代码',
        color_discrete_map=color_map,
        hover_name='产品代码',
        hover_data={
            '销售占比': ':.1%',
            '增长率': ':.1%',
            '求和项:金额（元）': ':,.0f'
        },
        size_max=60
    )
    
    # 添加象限分隔线
    fig.add_shape(
        type="line", x0=x_boundary, y0=-0.5, x1=x_boundary, y1=1.0,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    fig.add_shape(
        type="line", x0=0, y0=y_boundary, x1=0.1, y1=y_boundary,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # 添加象限标签
    fig.add_annotation(
        x=x_boundary/2, y=y_boundary + 0.1,
        text="问号产品",
        showarrow=False,
        font=dict(size=14)
    )
    
    fig.add_annotation(
        x=x_boundary + 0.02, y=y_boundary + 0.1,
        text="明星产品",
        showarrow=False,
        font=dict(size=14)
    )
    
    fig.add_annotation(
        x=x_boundary/2, y=y_boundary - 0.1,
        text="瘦狗产品",
        showarrow=False,
        font=dict(size=14)
    )
    
    fig.add_annotation(
        x=x_boundary + 0.02, y=y_boundary - 0.1,
        text="现金牛产品",
        showarrow=False,
        font=dict(size=14)
    )
    
    # 更新布局
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="销售占比",
            tickformat='.1%',
            range=[0, max(data['销售占比']) * 1.1]
        ),
        yaxis=dict(
            title="增长率",
            tickformat='.0%',
            range=[-0.3, 0.7]
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# 创建饼图
def create_pie_chart(data, names, values, title, color_discrete_map=None):
    """
    创建饼图
    
    参数:
        data (DataFrame): 数据
        names (str): 名称列
        values (str): 值列
        title (str): 图表标题
        color_discrete_map (dict): 颜色映射
        
    返回:
        plotly.graph_objects.Figure: 饼图对象
    """
    fig = px.pie(
        data,
        names=names,
        values=values,
        title=title,
        color=names,
        color_discrete_map=color_discrete_map,
        hole=0.3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

# 创建堆叠柱状图
def create_stacked_bar(data, x, y, color, title, barmode='stack', orientation='v'):
    """
    创建堆叠柱状图
    
    参数:
        data (DataFrame): 数据
        x (str): x轴列名
        y (str): y轴列名
        color (str): 颜色分组列名
        title (str): 图表标题
        barmode (str): 柱形模式，'stack'为堆叠，'group'为分组
        orientation (str): 方向，'v'为垂直，'h'为水平
        
    返回:
        plotly.graph_objects.Figure: 柱状图对象
    """
    fig = px.bar(
        data,
        x=x if orientation == 'v' else y,
        y=y if orientation == 'v' else x,
        color=color,
        title=title,
        barmode=barmode,
        orientation=orientation,
        text_auto='.2s' if orientation == 'v' else True,
    )
    
    fig.update_traces(
        textposition='auto',
        textangle=0 if orientation == 'h' else -90,
        textfont_size=10
    )
    
    fig.update_layout(
        margin=dict(l=50, r=50, t=80, b=100 if orientation == 'v' else 50),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(title=x if orientation == 'v' else y),
        yaxis=dict(title=y if orientation == 'v' else x)
    )
    
    return fig

# 创建折线图
def create_line_chart(data, x, y, color=None, title='', mode='lines+markers'):
    """
    创建折线图
    
    参数:
        data (DataFrame): 数据
        x (str): x轴列名
        y (str): y轴列名或列名列表
        color (str): 颜色分组列名
        title (str): 图表标题
        mode (str): 线型模式
        
    返回:
        plotly.graph_objects.Figure: 折线图对象
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        markers=True if 'markers' in mode else False
    )
    
    fig.update_traces(
        mode=mode,
        marker=dict(size=8),
        line=dict(width=2)
    )
    
    fig.update_layout(
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(title=x),
        yaxis=dict(title=y if isinstance(y, str) else 'Value')
    )
    
    return fig

# 创建仪表盘
def create_gauge(value, title, min_value=0, max_value=100, threshold_values=[50, 70, 90]):
    """
    创建仪表盘
    
    参数:
        value (float): 仪表盘值
        title (str): 图表标题
        min_value (float): 最小值
        max_value (float): 最大值
        threshold_values (list): 阈值列表，用于颜色分段
        
    返回:
        plotly.graph_objects.Figure: 仪表盘对象
    """
    # 设置颜色刻度
    if len(threshold_values) == 3:
        color_scale = [
            [0, COLOR_THEME['warning']],
            [threshold_values[0]/100, COLOR_THEME['warning']],
            [threshold_values[1]/100, COLOR_THEME['secondary']],
            [threshold_values[2]/100, COLOR_THEME['primary']],
            [1, COLOR_THEME['success']]
        ]
    else:
        color_scale = [
            [0, COLOR_THEME['warning']],
            [0.5, COLOR_THEME['secondary']],
            [0.8, COLOR_THEME['primary']],
            [1, COLOR_THEME['success']]
        ]
    
    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_value, threshold_values[0]], 'color': COLOR_THEME['warning']},
                {'range': [threshold_values[0], threshold_values[1]], 'color': COLOR_THEME['secondary']},
                {'range': [threshold_values[1], threshold_values[2]], 'color': COLOR_THEME['primary']},
                {'range': [threshold_values[2], max_value], 'color': COLOR_THEME['success']}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=300
    )
    
    return fig

# 生成洞察解读
def generate_insight(data, metric_name, value, change=None, benchmark=None):
    """
    生成洞察性解读文本
    
    参数:
        data: 用于生成洞察的数据
        metric_name: 指标名称
        value: 当前值
        change: 变化量
        benchmark: 基准值
        
    返回:
        str: 洞察解读文本
    """
    # 根据指标和变化情况生成洞察
    insight = f"**{metric_name}** 当前值为 **{value:,.0f}**. "
    
    if change is not None:
        if change > 0:
            insight += f"相比上期增长了 **{abs(change):,.0f}** ({abs(change/value)*100:.1f}%). "
            insight += "这是一个积极的信号，表明业务正在增长。"
        elif change < 0:
            insight += f"相比上期下降了 **{abs(change):,.0f}** ({abs(change/value)*100:.1f}%). "
            insight += "这需要关注，可能是季节性波动或市场变化导致的。"
        else:
            insight += "相比上期保持稳定。"
    
    if benchmark is not None:
        achievement = value / benchmark
        if achievement >= 1:
            insight += f"\n\n相对于基准值 **{benchmark:,.0f}**，当前达成率为 **{achievement:.1%}**，表现优异。"
        elif achievement >= 0.9:
            insight += f"\n\n相对于基准值 **{benchmark:,.0f}**，当前达成率为 **{achievement:.1%}**，接近目标。"
        elif achievement >= 0.8:
            insight += f"\n\n相对于基准值 **{benchmark:,.0f}**，当前达成率为 **{achievement:.1%}**，需要努力提升。"
        else:
            insight += f"\n\n相对于基准值 **{benchmark:,.0f}**，当前达成率为 **{achievement:.1%}**，存在明显差距，建议制定改进计划。"
    
    return insight


# 新增以下函数到utils/helpers.py文件末尾

# 将Excel文件转换为parquet格式以提高加载速度
def convert_to_parquet(excel_path, output_path=None):
    """
    将Excel文件转换为parquet格式，提高加载速度

    参数:
        excel_path (str): Excel文件路径
        output_path (str, optional): 输出文件路径，如果为None则自动生成

    返回:
        str: 输出文件路径
    """
    if output_path is None:
        output_path = excel_path.replace('.xlsx', '.parquet')

    # 读取Excel
    df = pd.read_excel(excel_path)

    # 保存为parquet
    df.to_parquet(output_path)

    return output_path


# 处理会话状态初始化
def initialize_session_state(key, default_value=None):
    """
    初始化或获取会话状态变量

    参数:
        key (str): 会话状态键名
        default_value: 默认值

    返回:
        会话状态值
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]


# 批量转换Excel文件为parquet格式
# 在utils/helpers.py中替换convert_all_excel_to_parquet函数
def convert_all_excel_to_parquet(data_paths):
    """
    将所有Excel文件转换为parquet格式以提高加载速度

    参数:
        data_paths (dict): 包含数据文件路径的字典

    返回:
        dict: 更新后的数据文件路径字典
    """
    updated_paths = data_paths.copy()

    # 创建进度条以显示转换进度
    excel_files = [path for path, file_path in data_paths.items() if file_path.endswith('.xlsx')]

    for data_type in excel_files:
        file_path = data_paths[data_type]
        parquet_path = file_path.replace('.xlsx', '.parquet')

        # 检查parquet文件是否存在，如果不存在或Excel文件更新过，则转换
        if not os.path.exists(parquet_path) or (
                os.path.exists(file_path) and
                os.path.getmtime(file_path) > os.path.getmtime(parquet_path)
        ):
            try:
                # 转换前输出日志
                print(f"正在转换 {file_path} 为 {parquet_path}...")

                # 读取Excel
                df = pd.read_excel(file_path)

                # 保存为parquet
                df.to_parquet(parquet_path)

                # 更新路径为parquet文件
                updated_paths[data_type] = parquet_path
                print(f"已完成转换 {file_path} 为 {parquet_path}")
            except Exception as e:
                print(f"转换 {file_path} 失败: {str(e)}")
        else:
            # 如果parquet文件已存在且是最新的，更新路径
            updated_paths[data_type] = parquet_path
            print(f"使用已有的parquet文件: {parquet_path}")

    return updated_paths