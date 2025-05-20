# pages/material_page.py - 完全自包含的物料分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 从config导入颜色配置
from config import COLORS, DATA_FILES


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_material_data():
    """加载物料分析所需的所有数据"""
    try:
        # 加载销售数据
        sales_data = pd.read_excel(DATA_FILES['sales_data'])

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

        # 筛选物料订单
        material_orders = sales_data[
            (sales_data['订单类型'] == '物料') |
            (sales_data['订单类型'].str.contains('物料', na=False))
            ].copy()

        # 识别物料代码（通常以M开头）
        if '产品代码' in material_orders.columns:
            material_orders['是物料'] = material_orders['产品代码'].str.startswith('M', na=False)
        else:
            material_orders['是物料'] = False

        # 加载实时库存数据
        try:
            inventory_data = pd.read_excel(DATA_FILES['inventory_data'])
        except:
            inventory_data = pd.DataFrame()

        return material_orders, inventory_data

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


def apply_material_filters(data):
    """应用筛选条件"""
    filtered_data = data.copy()

    # 应用全局筛选条件
    if st.session_state.get('filter_region') and st.session_state.get('filter_region') != '全部':
        if '所属区域' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['所属区域'] == st.session_state.get('filter_region')]

    if st.session_state.get('filter_person') and st.session_state.get('filter_person') != '全部':
        if '申请人' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['申请人'] == st.session_state.get('filter_person')]

    if st.session_state.get('filter_customer') and st.session_state.get('filter_customer') != '全部':
        if '客户代码' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['客户代码'] == st.session_state.get('filter_customer')]

    return filtered_data


# ==================== 2. 工具函数 ====================
def format_currency(value):
    """格式化货币显示"""
    if pd.isna(value) or value == 0:
        return "¥0"
    if value >= 100000000:
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"


def format_number(value):
    """格式化数字显示"""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


# ==================== 3. 物料分析函数 ====================
def analyze_material_data(material_orders, inventory_data):
    """分析物料数据"""
    if material_orders.empty:
        return {}

    # 获取当前年份
    current_year = datetime.now().year

    # 按物料类型分组统计
    material_types = material_orders.groupby('订单类型')['求和项:金额（元）'].sum().reset_index()
    material_types = material_types.sort_values('求和项:金额（元）', ascending=False)

    # 计算物料费用总额
    total_material_cost = material_types['求和项:金额（元）'].sum()

    # 添加占比
    material_types['占比'] = material_types[
                                 '求和项:金额（元）'] / total_material_cost * 100 if total_material_cost > 0 else 0

    # 按月统计物料使用趋势
    monthly_material = material_orders.groupby(pd.Grouper(key='发运月份', freq='M'))[
        '求和项:金额（元）'].sum().reset_index()
    monthly_material['月份'] = monthly_material['发运月份'].dt.month
    monthly_material['年份'] = monthly_material['发运月份'].dt.year

    # 按客户统计物料使用情况
    customer_material = material_orders.groupby(['客户代码', '客户简称'])['求和项:金额（元）'].sum().reset_index()
    customer_material = customer_material.sort_values('求和项:金额（元）', ascending=False)

    # 添加占比
    customer_material['占比'] = customer_material[
                                    '求和项:金额（元）'] / total_material_cost * 100 if total_material_cost > 0 else 0

    # 计算物料使用效率指标
    # 从库存中筛选物料
    material_inventory = inventory_data[
        inventory_data['物料'].str.startswith('M', na=False)] if not inventory_data.empty else pd.DataFrame()

    # 计算物料库存周转率
    if not material_inventory.empty and not material_orders.empty:
        # 按物料代码汇总近6个月的使用量
        six_months_ago = pd.Timestamp(year=current_year, month=datetime.now().month, day=1) - pd.DateOffset(months=6)
        recent_material_usage = material_orders[material_orders['发运月份'] >= six_months_ago]

        if not recent_material_usage.empty:
            material_usage = recent_material_usage.groupby('产品代码')['求和项:数量（箱）'].sum().reset_index()
            material_usage['月平均使用量'] = material_usage['求和项:数量（箱）'] / 6  # 6个月平均

            # 合并库存数据
            material_efficiency = pd.merge(
                material_inventory[['物料', '现有库存']].drop_duplicates(),
                material_usage,
                left_on='物料',
                right_on='产品代码',
                how='left'
            )

            # 填充缺失的月平均使用量为很小的值(0.1)，避免除以零错误
            material_efficiency['月平均使用量'] = material_efficiency['月平均使用量'].fillna(0.1)

            # 计算周转率和覆盖天数
            material_efficiency['周转率'] = material_efficiency['月平均使用量'] / material_efficiency['现有库存']
            material_efficiency['库存覆盖天数'] = material_efficiency['现有库存'] / material_efficiency[
                '月平均使用量'] * 30

            # 计算周转等级
            material_efficiency['周转等级'] = material_efficiency.apply(
                lambda row: '优秀' if row['周转率'] > 1.5 else
                '良好' if row['周转率'] > 1 else
                '一般' if row['周转率'] > 0.5 else
                '不佳' if row['周转率'] > 0.2 else
                '很差',
                axis=1
            )

            # 计算各周转等级的数量
            turnover_rating = material_efficiency['周转等级'].value_counts().to_dict()

            # 计算平均周转率和库存覆盖天数
            avg_turnover_rate = material_efficiency['周转率'].mean()
            avg_coverage_days = material_efficiency['库存覆盖天数'].mean()
        else:
            material_efficiency = pd.DataFrame()
            turnover_rating = {}
            avg_turnover_rate = 0
            avg_coverage_days = 0
    else:
        material_efficiency = pd.DataFrame()
        turnover_rating = {}
        avg_turnover_rate = 0
        avg_coverage_days = 0

    # 计算按区域分组的物料使用
    if '所属区域' in material_orders.columns:
        region_material = material_orders.groupby('所属区域')['求和项:金额（元）'].sum().reset_index()
        region_material = region_material.sort_values('求和项:金额（元）', ascending=False)
        region_material['占比'] = region_material[
                                      '求和项:金额（元）'] / total_material_cost * 100 if total_material_cost > 0 else 0
    else:
        region_material = pd.DataFrame()

    # 分析物料供应风险（假设数据，实际应根据真实供应链数据计算）
    # 这里只是示例，实际应根据供应商交付时间、供应稳定性等计算
    supply_risk = {
        '低风险': 60,
        '中风险': 30,
        '高风险': 10
    }

    return {
        'material_types': material_types,
        'total_material_cost': total_material_cost,
        'monthly_material': monthly_material,
        'customer_material': customer_material,
        'material_efficiency': material_efficiency,
        'turnover_rating': turnover_rating,
        'avg_turnover_rate': avg_turnover_rate,
        'avg_coverage_days': avg_coverage_days,
        'region_material': region_material,
        'supply_risk': supply_risk
    }


# ==================== 4. 图表创建函数 ====================
def create_material_type_chart(data, title="物料类型分布"):
    """创建物料类型分布饼图"""
    if data.empty:
        return None

    fig = px.pie(
        data,
        names='订单类型',
        values='求和项:金额（元）',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_material_trend_chart(data, title="月度物料使用趋势"):
    """创建物料使用趋势图"""
    if data.empty:
        return None

    # 筛选当前年度数据
    current_year = datetime.now().year
    current_data = data[data['年份'] == current_year]

    fig = px.line(
        current_data,
        x='月份',
        y='求和项:金额（元）',
        title=title,
        markers=True,
        color_discrete_sequence=[COLORS['primary']]
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="月份",
        yaxis_title="物料费用（元）",
        hovermode="x unified"
    )

    # 添加数值标签
    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='top center'
    )

    return fig


def create_customer_material_chart(data, title="客户物料使用TOP10"):
    """创建客户物料使用条形图"""
    if data.empty:
        return None

    # 取TOP10客户
    top_data = data.head(10)

    fig = px.bar(
        top_data,
        y='客户简称',
        x='求和项:金额（元）',
        orientation='h',
        title=title,
        color='求和项:金额（元）',
        color_continuous_scale=px.colors.sequential.Blues,
        text_auto='.2s'
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="物料费用（元）",
        yaxis_title="客户"
    )

    return fig


def create_turnover_histogram(data, title="物料周转率分布"):
    """创建物料周转率分布直方图"""
    if data is None or data.empty:
        return None

    material_efficiency = data.get('material_efficiency', pd.DataFrame())

    if material_efficiency.empty:
        return None

    fig = px.histogram(
        material_efficiency,
        x='周转率',
        nbins=20,
        title=title,
        color_discrete_sequence=[COLORS['primary']]
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="周转率",
        yaxis_title="物料数量",
        bargap=0.1
    )

    # 添加垂直线标识不同周转率区间
    fig.add_shape(
        type="line",
        x0=0.2, y0=0,
        x1=0.2, y1=material_efficiency['周转率'].value_counts().max() * 1.1,
        line=dict(color="red", width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=0.5, y0=0,
        x1=0.5, y1=material_efficiency['周转率'].value_counts().max() * 1.1,
        line=dict(color="orange", width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=1.0, y0=0,
        x1=1.0, y1=material_efficiency['周转率'].value_counts().max() * 1.1,
        line=dict(color="green", width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=1.5, y0=0,
        x1=1.5, y1=material_efficiency['周转率'].value_counts().max() * 1.1,
        line=dict(color="blue", width=1, dash="dash")
    )

    # 添加区间标签
    fig.add_annotation(
        x=0.1, y=material_efficiency['周转率'].value_counts().max() * 0.9,
        text="很差",
        showarrow=False,
        font=dict(color="red")
    )

    fig.add_annotation(
        x=0.35, y=material_efficiency['周转率'].value_counts().max() * 0.9,
        text="不佳",
        showarrow=False,
        font=dict(color="orange")
    )

    fig.add_annotation(
        x=0.75, y=material_efficiency['周转率'].value_counts().max() * 0.9,
        text="一般",
        showarrow=False,
        font=dict(color="green")
    )

    fig.add_annotation(
        x=1.25, y=material_efficiency['周转率'].value_counts().max() * 0.9,
        text="良好",
        showarrow=False,
        font=dict(color="blue")
    )

    fig.add_annotation(
        x=1.75, y=material_efficiency['周转率'].value_counts().max() * 0.9,
        text="优秀",
        showarrow=False,
        font=dict(color="darkblue")
    )

    return fig


def create_turnover_rating_pie(data, title="周转率评级分布"):
    """创建周转率评级饼图"""
    turnover_rating = data.get('turnover_rating', {})

    if not turnover_rating:
        return None

    # 转换为DataFrame
    rating_df = pd.DataFrame({
        '评级': list(turnover_rating.keys()),
        '物料数量': list(turnover_rating.values())
    })

    # 设置评级顺序
    rating_order = ['优秀', '良好', '一般', '不佳', '很差']
    rating_df['评级'] = pd.Categorical(rating_df['评级'], categories=rating_order, ordered=True)
    rating_df = rating_df.sort_values('评级')

    # 设置颜色映射
    color_map = {
        '优秀': COLORS['success'],
        '良好': COLORS['info'],
        '一般': COLORS['warning'],
        '不佳': COLORS['warning'],
        '很差': COLORS['danger']
    }

    fig = px.pie(
        rating_df,
        names='评级',
        values='物料数量',
        title=title,
        color='评级',
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_supply_risk_chart(risk_data, title="物料供应风险分布"):
    """创建物料供应风险饼图"""
    if not risk_data:
        return None

    # 转换为DataFrame
    risk_df = pd.DataFrame({
        '风险等级': list(risk_data.keys()),
        '物料占比': list(risk_data.values())
    })

    # 设置颜色映射
    color_map = {
        '低风险': COLORS['success'],
        '中风险': COLORS['warning'],
        '高风险': COLORS['danger']
    }

    fig = px.pie(
        risk_df,
        names='风险等级',
        values='物料占比',
        title=title,
        color='风险等级',
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_region_material_chart(data, title="区域物料使用分布"):
    """创建区域物料使用饼图"""
    if data.empty:
        return None

    fig = px.pie(
        data,
        names='所属区域',
        values='求和项:金额（元）',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

    # ==================== 5. 翻卡组件 ====================


def create_material_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建物料分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"material_flip_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = 0

    # 格式化值
    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)

    # 创建卡片容器
    card_container = st.container()

    with card_container:
        # 点击按钮
        if st.button(f"查看{title}详情", key=f"btn_{card_id}", help=f"点击查看{title}的详细分析"):
            st.session_state[flip_key] = (st.session_state[flip_key] + 1) % 3

        current_layer = st.session_state[flip_key]

        if current_layer == 0:
            # 第一层：基础指标
            st.markdown(f"""
                    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                                box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); 
                                text-align: center; min-height: 200px; display: flex; 
                                flex-direction: column; justify-content: center;">
                        <h3 style="color: {COLORS['primary']}; margin-bottom: 1rem;">{title}</h3>
                        <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">{formatted_value}</h1>
                        <p style="color: {COLORS['gray']}; margin-bottom: 1rem;">{subtitle}</p>
                        <p style="color: {COLORS['secondary']}; font-size: 0.9rem;">点击查看分析 →</p>
                    </div>
                    """, unsafe_allow_html=True)

        elif current_layer == 1:
            # 第二层：图表分析
            st.markdown(f"### 📊 {title} - 图表分析")

            # 根据不同的指标显示不同的图表
            if "物料费用总额" in title:
                # 显示物料类型分布
                if 'analysis_result' in st.session_state:
                    material_types = st.session_state['analysis_result'].get('material_types', pd.DataFrame())
                    if not material_types.empty:
                        fig = create_material_type_chart(material_types, "物料类型分布")
                        st.plotly_chart(fig, use_container_width=True)

            elif "物料周转率" in title:
                # 显示周转率分布
                if 'analysis_result' in st.session_state:
                    fig = create_turnover_histogram(st.session_state['analysis_result'], "物料周转率分布")
                    st.plotly_chart(fig, use_container_width=True)

            elif "库存覆盖天数" in title:
                # 显示周转等级分布
                if 'analysis_result' in st.session_state:
                    fig = create_turnover_rating_pie(st.session_state['analysis_result'], "周转率评级分布")
                    st.plotly_chart(fig, use_container_width=True)

            elif "物料供应风险" in title:
                # 显示供应风险分布
                if 'analysis_result' in st.session_state:
                    supply_risk = st.session_state['analysis_result'].get('supply_risk', {})
                    if supply_risk:
                        fig = create_supply_risk_chart(supply_risk, "物料供应风险分布")
                        st.plotly_chart(fig, use_container_width=True)

            # 洞察文本
            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>💡 数据洞察</h4>
                        <p>{generate_insight_text(card_id)}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击查看深度分析 →</p>",
                        unsafe_allow_html=True)

        else:
            # 第三层：深度分析
            st.markdown(f"### 🔍 {title} - 深度分析")

            # 深度分析内容
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                        <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid {COLORS['info']}; 
                                    padding: 1rem; border-radius: 0.5rem;">
                            <h4>📈 趋势分析</h4>
                            {generate_trend_analysis(card_id)}
                        </div>
                        """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                        <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid {COLORS['warning']}; 
                                    padding: 1rem; border-radius: 0.5rem;">
                            <h4>🎯 优化建议</h4>
                            {generate_optimization_advice(card_id)}
                        </div>
                        """, unsafe_allow_html=True)

            # 行动方案
            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                                padding: 1rem; margin-top: 1rem; border-radius: 0.5rem;">
                        <h4>📋 行动方案</h4>
                        {generate_action_plan(card_id)}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击返回基础视图 ↻</p>",
                        unsafe_allow_html=True)


def generate_insight_text(card_id):
    """生成洞察文本"""
    if 'analysis_result' not in st.session_state:
        return "数据分析加载中..."

    analysis = st.session_state['analysis_result']

    if card_id == "total_cost":
        total_cost = analysis.get('total_material_cost', 0)
        material_types = analysis.get('material_types', pd.DataFrame())

        if not material_types.empty and len(material_types) > 0:
            top_type = material_types.iloc[0]
            top_type_percentage = top_type['占比']

            return f"物料费用总额为 {format_currency(total_cost)}，主要用于{top_type['订单类型']}，占比{format_percentage(top_type_percentage)}。{'物料费用集中度较高，可能存在优化空间。' if top_type_percentage > 60 else '物料费用分布相对均衡。'}"
        else:
            return f"物料费用总额为 {format_currency(total_cost)}，暂无详细分类数据。"

    elif card_id == "turnover_rate":
        avg_turnover = analysis.get('avg_turnover_rate', 0)
        turnover_rating = analysis.get('turnover_rating', {})

        if turnover_rating:
            excellent_count = turnover_rating.get('优秀', 0)
            good_count = turnover_rating.get('良好', 0)
            poor_count = turnover_rating.get('不佳', 0) + turnover_rating.get('很差', 0)
            total_count = sum(turnover_rating.values())

            excellent_percentage = excellent_count / total_count * 100 if total_count > 0 else 0
            good_percentage = good_count / total_count * 100 if total_count > 0 else 0
            poor_percentage = poor_count / total_count * 100 if total_count > 0 else 0

            if avg_turnover > 1:
                return f"平均物料周转率为 {avg_turnover:.2f}，整体周转良好。优秀周转率物料占比{format_percentage(excellent_percentage)}，良好周转率物料占比{format_percentage(good_percentage)}，差劣周转率物料占比{format_percentage(poor_percentage)}。"
            else:
                return f"平均物料周转率为 {avg_turnover:.2f}，整体周转有待提高。优秀周转率物料占比{format_percentage(excellent_percentage)}，良好周转率物料占比{format_percentage(good_percentage)}，差劣周转率物料占比{format_percentage(poor_percentage)}。"
        else:
            return f"平均物料周转率为 {avg_turnover:.2f}，暂无详细周转评级数据。"

    elif card_id == "coverage_days":
        avg_coverage = analysis.get('avg_coverage_days', 0)

        if avg_coverage > 90:
            return f"平均库存覆盖天数为 {avg_coverage:.1f}天，物料库存过高，资金占用较多，建议优化库存管理，提高周转效率。"
        elif avg_coverage > 60:
            return f"平均库存覆盖天数为 {avg_coverage:.1f}天，物料库存略高，但仍在合理范围内，可以适当优化。"
        elif avg_coverage > 30:
            return f"平均库存覆盖天数为 {avg_coverage:.1f}天，物料库存处于合理水平，供应链运作良好。"
        elif avg_coverage > 15:
            return f"平均库存覆盖天数为 {avg_coverage:.1f}天，物料库存偏低，需要关注补货及时性，避免断料风险。"
        else:
            return f"平均库存覆盖天数仅为 {avg_coverage:.1f}天，物料库存严重不足，存在高断料风险，需要紧急补充库存。"

    elif card_id == "supply_risk":
        supply_risk = analysis.get('supply_risk', {})

        if supply_risk:
            high_risk = supply_risk.get('高风险', 0)
            medium_risk = supply_risk.get('中风险', 0)
            low_risk = supply_risk.get('低风险', 0)

            if high_risk > 20:
                return f"物料供应高风险占比{format_percentage(high_risk)}，中风险占比{format_percentage(medium_risk)}，低风险占比{format_percentage(low_risk)}。供应链风险较高，需要加强供应商管理和备选方案准备。"
            elif high_risk > 10:
                return f"物料供应高风险占比{format_percentage(high_risk)}，中风险占比{format_percentage(medium_risk)}，低风险占比{format_percentage(low_risk)}。供应链风险中等，需要关注高风险物料的供应稳定性。"
            else:
                return f"物料供应高风险占比{format_percentage(high_risk)}，中风险占比{format_percentage(medium_risk)}，低风险占比{format_percentage(low_risk)}。供应链风险较低，物料供应相对稳定。"
        else:
            return "暂无物料供应风险数据。"

    return "数据分析加载中..."


def generate_trend_analysis(card_id):
    """生成趋势分析HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>分析数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_cost":
        monthly_material = analysis.get('monthly_material', pd.DataFrame())

        if not monthly_material.empty and len(monthly_material) > 1:
            # 计算月度变化趋势
            current_month_data = monthly_material.iloc[-1]
            previous_month_data = monthly_material.iloc[-2]

            current_cost = current_month_data['求和项:金额（元）']
            previous_cost = previous_month_data['求和项:金额（元）']

            mom_change = ((current_cost - previous_cost) / previous_cost * 100) if previous_cost > 0 else 0

            # 计算季度趋势
            if len(monthly_material) >= 3:
                q_current = current_cost
                q_previous = monthly_material.iloc[-3:-1]['求和项:金额（元）'].sum() / 2

                q_change = ((q_current - q_previous) / q_previous * 100) if q_previous > 0 else 0

                trend_text = f"<p>• 环比季度趋势：<span style='color:{COLORS['success'] if q_change > 0 else COLORS['danger']};'>{q_change:+.1f}%</span></p>"
            else:
                trend_text = ""

            # 获取TOP物料类型
            material_types = analysis.get('material_types', pd.DataFrame())

            type_text = ""
            if not material_types.empty:
                top_type = material_types.iloc[0]
                type_text = f"<p>• 主要物料类型：{top_type['订单类型']} ({format_percentage(top_type['占比'])})</p>"

            return f"""
                        <p>• 当前物料费用：{format_currency(analysis.get('total_material_cost', 0))}</p>
                        <p>• 环比月度变化：<span style='color:{COLORS['success'] if mom_change > 0 else COLORS['danger']};'>{mom_change:+.1f}%</span></p>
                        {trend_text}
                        {type_text}
                        <p>• 物料费用趋势：{'呈上升趋势，需关注成本控制' if mom_change > 5 else '呈下降趋势，成本管控有效' if mom_change < -5 else '相对稳定，波动在合理范围'}</p>
                    """
        else:
            return f"""
                        <p>• 当前物料费用：{format_currency(analysis.get('total_material_cost', 0))}</p>
                        <p>• 暂无足够的历史数据进行趋势分析</p>
                    """

    elif card_id == "turnover_rate":
        avg_turnover = analysis.get('avg_turnover_rate', 0)
        turnover_rating = analysis.get('turnover_rating', {})
        material_efficiency = analysis.get('material_efficiency', pd.DataFrame())

        if turnover_rating and not material_efficiency.empty:
            # 计算各等级占比
            total_count = sum(turnover_rating.values())

            excellent_count = turnover_rating.get('优秀', 0)
            good_count = turnover_rating.get('良好', 0)
            average_count = turnover_rating.get('一般', 0)
            poor_count = turnover_rating.get('不佳', 0)
            very_poor_count = turnover_rating.get('很差', 0)

            excellent_percentage = excellent_count / total_count * 100 if total_count > 0 else 0
            good_percentage = good_count / total_count * 100 if total_count > 0 else 0
            average_percentage = average_count / total_count * 100 if total_count > 0 else 0
            poor_percentage = poor_count / total_count * 100 if total_count > 0 else 0
            very_poor_percentage = very_poor_count / total_count * 100 if total_count > 0 else 0

            # 找出周转率最高和最低的物料
            if len(material_efficiency) > 0:
                top_turnover = material_efficiency.nlargest(1, '周转率')
                bottom_turnover = material_efficiency.nsmallest(1, '周转率')

                top_material = top_turnover.iloc[0]['物料'] if not top_turnover.empty else "无数据"
                top_rate = top_turnover.iloc[0]['周转率'] if not top_turnover.empty else 0

                bottom_material = bottom_turnover.iloc[0]['物料'] if not bottom_turnover.empty else "无数据"
                bottom_rate = bottom_turnover.iloc[0]['周转率'] if not bottom_turnover.empty else 0

                return f"""
                            <p>• 平均周转率：{avg_turnover:.2f}</p>
                            <p>• 周转率分布：优秀 {format_percentage(excellent_percentage)}，良好 {format_percentage(good_percentage)}，一般 {format_percentage(average_percentage)}，不佳 {format_percentage(poor_percentage)}，很差 {format_percentage(very_poor_percentage)}</p>
                            <p>• 最高周转率物料：{top_material} ({top_rate:.2f})</p>
                            <p>• 最低周转率物料：{bottom_material} ({bottom_rate:.2f})</p>
                            <p>• 整体评价：{'周转效率良好，资金占用合理' if avg_turnover > 1 else '周转效率一般，有优化空间' if avg_turnover > 0.5 else '周转效率较低，资金占用过多'}</p>
                        """
            else:
                return f"""
                            <p>• 平均周转率：{avg_turnover:.2f}</p>
                            <p>• 周转率分布：优秀 {format_percentage(excellent_percentage)}，良好 {format_percentage(good_percentage)}，一般 {format_percentage(average_percentage)}，不佳 {format_percentage(poor_percentage)}，很差 {format_percentage(very_poor_percentage)}</p>
                            <p>• 整体评价：{'周转效率良好，资金占用合理' if avg_turnover > 1 else '周转效率一般，有优化空间' if avg_turnover > 0.5 else '周转效率较低，资金占用过多'}</p>
                        """
        else:
            return f"""
                        <p>• 平均周转率：{avg_turnover:.2f}</p>
                        <p>• 暂无详细的周转率分布数据</p>
                    """

    elif card_id == "coverage_days":
        avg_coverage = analysis.get('avg_coverage_days', 0)
        material_efficiency = analysis.get('material_efficiency', pd.DataFrame())

        if not material_efficiency.empty:
            # 计算库存覆盖天数分布
            low_coverage = len(material_efficiency[material_efficiency['库存覆盖天数'] < 15])
            normal_coverage = len(material_efficiency[(material_efficiency['库存覆盖天数'] >= 15) & (
                        material_efficiency['库存覆盖天数'] <= 90)])
            high_coverage = len(material_efficiency[material_efficiency['库存覆盖天数'] > 90])

            total_count = len(material_efficiency)

            low_percentage = low_coverage / total_count * 100 if total_count > 0 else 0
            normal_percentage = normal_coverage / total_count * 100 if total_count > 0 else 0
            high_percentage = high_coverage / total_count * 100 if total_count > 0 else 0

            # 找出覆盖天数最高和最低的物料
            top_coverage = material_efficiency.nlargest(1, '库存覆盖天数')
            bottom_coverage = material_efficiency.nsmallest(1, '库存覆盖天数')

            top_material = top_coverage.iloc[0]['物料'] if not top_coverage.empty else "无数据"
            top_days = top_coverage.iloc[0]['库存覆盖天数'] if not top_coverage.empty else 0

            bottom_material = bottom_coverage.iloc[0]['物料'] if not bottom_coverage.empty else "无数据"
            bottom_days = bottom_coverage.iloc[0]['库存覆盖天数'] if not bottom_coverage.empty else 0

            return f"""
                        <p>• 平均库存覆盖天数：{avg_coverage:.1f}天</p>
                        <p>• 覆盖天数分布：不足 (<15天) {format_percentage(low_percentage)}，合理 (15-90天) {format_percentage(normal_percentage)}，过高 (>90天) {format_percentage(high_percentage)}</p>
                        <p>• 覆盖天数最高物料：{top_material} ({top_days:.1f}天)</p>
                        <p>• 覆盖天数最低物料：{bottom_material} ({bottom_days:.1f}天)</p>
                        <p>• 整体评价：{'库存水平合理，供应链运作良好' if 30 <= avg_coverage <= 60 else '库存水平偏高，资金占用较多' if avg_coverage > 60 else '库存水平偏低，存在断料风险'}</p>
                    """
        else:
            return f"""
                        <p>• 平均库存覆盖天数：{avg_coverage:.1f}天</p>
                        <p>• 暂无详细的库存覆盖天数分布数据</p>
                    """

    elif card_id == "supply_risk":
        supply_risk = analysis.get('supply_risk', {})

        if supply_risk:
            high_risk = supply_risk.get('高风险', 0)
            medium_risk = supply_risk.get('中风险', 0)
            low_risk = supply_risk.get('低风险', 0)

            # 风险评分（加权平均）
            risk_score = (high_risk * 3 + medium_risk * 2 + low_risk * 1) / (high_risk + medium_risk + low_risk) if (
                                                                                                                                high_risk + medium_risk + low_risk) > 0 else 0

            # 风险趋势（这里是假设数据，实际应从历史数据计算）
            # 假设风险较上月下降了0.2分
            risk_trend = -0.2

            return f"""
                        <p>• 供应风险分布：高风险 {format_percentage(high_risk)}，中风险 {format_percentage(medium_risk)}，低风险 {format_percentage(low_risk)}</p>
                        <p>• 综合风险评分：{risk_score:.1f}/3.0 ({risk_score / 3 * 100:.1f}%)</p>
                        <p>• 风险变化趋势：<span style='color:{COLORS['success']};'>{risk_trend:+.1f}</span></p>
                        <p>• 主要风险因素：{'供应商集中度高' if high_risk > 20 else '供应商交付不稳定' if high_risk > 10 else '供应链整体稳定'}</p>
                        <p>• 风险等级：{'高' if risk_score > 2 else '中' if risk_score > 1.5 else '低'}</p>
                    """
        else:
            return """
                        <p>• 暂无详细的供应风险分布数据</p>
                        <p>• 建议建立供应商风险评估体系，定期监控供应风险</p>
                    """

    return "<p>分析数据加载中...</p>"


def generate_optimization_advice(card_id):
    """生成优化建议HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>建议数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_cost":
        total_cost = analysis.get('total_material_cost', 0)
        material_types = analysis.get('material_types', pd.DataFrame())

        if not material_types.empty and len(material_types) > 0:
            top_type = material_types.iloc[0]
            top_type_percentage = top_type['占比']

            if top_type_percentage > 70:
                return """
                            <p>• 分析主要物料类型成本结构，找出优化空间</p>
                            <p>• 评估不同供应商报价，寻找性价比更高的选择</p>
                            <p>• 考虑物料替代方案，降低对单一物料的依赖</p>
                            <p>• 优化物料使用流程，减少浪费和报废</p>
                        """
            elif top_type_percentage > 50:
                return """
                            <p>• 加强主要物料类型的成本控制，提高使用效率</p>
                            <p>• 集中采购，争取更优惠的供应条件</p>
                            <p>• 优化物料规格和品质要求，避免过度规格</p>
                            <p>• 改进物料管理流程，减少非增值环节</p>
                        """
            else:
                return """
                            <p>• 全面评估各类物料使用情况，优化整体成本结构</p>
                            <p>• 实施标准化管理，减少物料种类和规格</p>
                            <p>• 建立物料成本趋势监控机制，及时应对价格波动</p>
                            <p>• 加强物料回收和循环利用，降低整体成本</p>
                        """
        else:
            return """
                        <p>• 建立物料成本分类统计体系，明确成本结构</p>
                        <p>• 进行物料成本基准比较，找出优化空间</p>
                        <p>• 设定物料成本控制目标，定期监控执行情况</p>
                        <p>• 加强采购和使用环节的成本意识</p>
                    """

    elif card_id == "turnover_rate":
        avg_turnover = analysis.get('avg_turnover_rate', 0)
        turnover_rating = analysis.get('turnover_rating', {})

        if turnover_rating:
            poor_count = turnover_rating.get('不佳', 0) + turnover_rating.get('很差', 0)
            total_count = sum(turnover_rating.values())

            poor_percentage = poor_count / total_count * 100 if total_count > 0 else 0

            if avg_turnover < 0.5 or poor_percentage > 30:
                return """
                            <p>• 全面评估低周转物料，制定分类处理方案</p>
                            <p>• 优化采购计划，减少低周转物料的采购量</p>
                            <p>• 改进物料需求预测方法，提高准确性</p>
                            <p>• 考虑物料寄售模式，减少自有库存</p>
                            <p>• 建立物料周转率绩效考核制度</p>
                        """
            elif avg_turnover < 1:
                return """
                            <p>• 针对周转率不佳的物料制定改进计划</p>
                            <p>• 优化安全库存水平，避免过度库存</p>
                            <p>• 加强物料需求计划与生产计划的协同</p>
                            <p>• 实施定期库存评估机制，及时调整</p>
                        """
            else:
                return """
                            <p>• 保持当前物料管理策略，继续优化细节</p>
                            <p>• 关注物料市场变化，及时调整采购策略</p>
                            <p>• 定期评估物料周转情况，防止恶化</p>
                            <p>• 分享高周转物料的管理经验，推广到其他物料</p>
                        """
        else:
            return """
                        <p>• 建立物料周转率监控体系，定期评估</p>
                        <p>• 设定物料周转目标，推动持续改进</p>
                        <p>• 优化物料采购和使用流程，提高效率</p>
                        <p>• 加强物料库存管理，减少资金占用</p>
                    """

    elif card_id == "coverage_days":
        avg_coverage = analysis.get('avg_coverage_days', 0)

        if avg_coverage > 90:
            return """
                        <p>• 针对高库存物料制定消化计划，降低库存水平</p>
                        <p>• 调整安全库存参数，避免过度库存</p>
                        <p>• 优化物料需求预测方法，提高准确性</p>
                        <p>• 加强物料寿命管理，避免过期报废</p>
                        <p>• 建立库存预警机制，及时处理异常</p>
                    """
        elif avg_coverage > 60:
            return """
                        <p>• 评估高库存物料，有针对性地降低库存</p>
                        <p>• 优化补货策略，平衡库存水平</p>
                        <p>• 加强需求预测与采购计划的协同</p>
                        <p>• 定期评估库存结构，确保资源合理配置</p>
                    """
        elif avg_coverage > 30:
            return """
                        <p>• 保持当前库存管理策略，维持库存平衡</p>
                        <p>• 关注物料需求变化，及时调整库存水平</p>
                        <p>• 优化物料库存结构，提高整体效率</p>
                        <p>• 定期评估库存健康状况，防止恶化</p>
                    """
        elif avg_coverage > 15:
            return """
                        <p>• 评估低库存物料，适当提高安全库存</p>
                        <p>• 加强与供应商的协作，缩短补货周期</p>
                        <p>• 优化物料需求预警机制，提前应对变化</p>
                        <p>• 建立库存应急预案，降低断料风险</p>
                    """
        else:
            return """
                        <p>• 立即评估关键物料库存，补充不足项</p>
                        <p>• 重新设定安全库存水平，确保基本供应</p>
                        <p>• 加强供应商管理，确保及时交付</p>
                        <p>• 建立物料库存日常监控机制</p>
                        <p>• 优化需求预测方法，提高准确性</p>
                    """

    elif card_id == "supply_risk":
        supply_risk = analysis.get('supply_risk', {})

        if supply_risk:
            high_risk = supply_risk.get('高风险', 0)

            if high_risk > 20:
                return """
                            <p>• 全面评估高风险物料，制定风险缓解计划</p>
                            <p>• 发展备选供应商，降低单一依赖风险</p>
                            <p>• 建立关键物料战略库存，应对突发情况</p>
                            <p>• 加强与核心供应商的合作关系，提高稳定性</p>
                            <p>• 考虑物料替代方案，降低特定物料依赖</p>
                        """
            elif high_risk > 10:
                return """
                            <p>• 针对高风险物料制定风险管理计划</p>
                            <p>• 优化供应商评估体系，提前识别风险</p>
                            <p>• 加强供应市场监控，及时应对变化</p>
                            <p>• 适当提高关键物料安全库存，降低风险</p>
                        """
            else:
                return """
                            <p>• 保持当前供应风险管理策略，继续监控</p>
                            <p>• 定期评估供应商表现，维持良好合作</p>
                            <p>• 关注市场变化，预判可能的供应风险</p>
                            <p>• 优化供应链结构，提高整体稳定性</p>
                        """
        else:
            return """
                        <p>• 建立物料供应风险评估体系，定期监控</p>
                        <p>• 评估关键物料供应链，识别潜在风险</p>
                        <p>• 制定物料供应应急预案，提高应对能力</p>
                        <p>• 加强与核心供应商的战略合作，提高稳定性</p>
                    """

    return "<p>建议数据加载中...</p>"


def generate_action_plan(card_id):
    """生成行动方案HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>行动计划加载中...</p>"

    if card_id == "total_cost":
        total_cost = st.session_state['analysis_result'].get('total_material_cost', 0)
        material_types = st.session_state['analysis_result'].get('material_types', pd.DataFrame())

        if not material_types.empty and len(material_types) > 0:
            top_type = material_types.iloc[0]
            top_type_percentage = top_type['占比']

            if top_type_percentage > 60:
                return """
                            <p><strong>近期行动（1个月）：</strong>详细分析主要物料类型成本构成，识别优化机会</p>
                            <p><strong>中期行动（3个月）：</strong>启动主要物料成本优化项目，设定明确目标</p>
                            <p><strong>长期行动（6个月）：</strong>建立物料成本长效管理机制，推动持续改进</p>
                        """
            else:
                return """
                            <p><strong>近期行动（1个月）：</strong>全面评估各类物料成本结构，确定优化重点</p>
                            <p><strong>中期行动（3个月）：</strong>实施物料成本优化举措，如优化采购策略、减少浪费等</p>
                            <p><strong>长期行动（6个月）：</strong>建立物料成本管理体系，确保持续优化</p>
                        """
        else:
            return """
                        <p><strong>近期行动（1个月）：</strong>收集物料成本详细数据，建立成本结构分析</p>
                        <p><strong>中期行动（3个月）：</strong>基于成本分析结果，制定优化计划</p>
                        <p><strong>长期行动（6个月）：</strong>实施物料成本管理体系，推动持续改进</p>
                    """

    elif card_id == "turnover_rate":
        avg_turnover = st.session_state['analysis_result'].get('avg_turnover_rate', 0)

        if avg_turnover < 0.5:
            return """
                        <p><strong>紧急行动（2周内）：</strong>评估周转率最低的物料，制定清理计划</p>
                        <p><strong>近期行动（1个月）：</strong>全面调整采购计划，减少低周转物料的采购量</p>
                        <p><strong>中期行动（3个月）：</strong>优化物料管理流程，提高整体周转效率</p>
                    """
        elif avg_turnover < 1:
            return """
                        <p><strong>近期行动（1个月）：</strong>分析周转率不佳的物料，制定改进方案</p>
                        <p><strong>中期行动（3个月）：</strong>优化物料需求预测和采购策略，提高周转率</p>
                        <p><strong>长期行动（6个月）：</strong>建立物料周转率管理体系，确保持续优化</p>
                    """
        else:
            return """
                        <p><strong>近期行动（1个月）：</strong>维持当前物料管理策略，关注周转率变化</p>
                        <p><strong>中期行动（3个月）：</strong>优化物料周转效率，进一步提升表现</p>
                        <p><strong>长期行动（6个月）：</strong>建立物料周转率最佳实践，推广成功经验</p>
                    """

    elif card_id == "coverage_days":
        avg_coverage = st.session_state['analysis_result'].get('avg_coverage_days', 0)

        if avg_coverage > 90:
            return """
                        <p><strong>近期行动（1个月）：</strong>针对库存覆盖天数最高的物料制定消化计划</p>
                        <p><strong>中期行动（3个月）：</strong>优化物料采购策略和安全库存水平，降低整体库存</p>
                        <p><strong>长期行动（6个月）：</strong>建立库存优化长效机制，保持合理库存水平</p>
                    """
        elif avg_coverage < 15:
            return """
                        <p><strong>紧急行动（1周内）：</strong>评估关键物料库存，立即补充不足项</p>
                        <p><strong>近期行动（1个月）：</strong>重新评估安全库存水平，优化补货策略</p>
                        <p><strong>中期行动（3个月）：</strong>加强供应商管理，提高供应稳定性</p>
                    """
        else:
            return """
                        <p><strong>近期行动（1个月）：</strong>评估库存结构，针对性优化不同物料的库存水平</p>
                        <p><strong>中期行动（3个月）：</strong>优化物料需求预测和补货策略，提高准确性</p>
                        <p><strong>长期行动（6个月）：</strong>建立库存健康管理体系，保持最佳库存水平</p>
                    """

    elif card_id == "supply_risk":
        supply_risk = st.session_state['analysis_result'].get('supply_risk', {})

        if supply_risk:
            high_risk = supply_risk.get('高风险', 0)

            if high_risk > 20:
                return """
                            <p><strong>近期行动（1个月）：</strong>评估高风险物料，制定风险缓解计划</p>
                            <p><strong>中期行动（3个月）：</strong>发展备选供应商，建立战略库存</p>
                            <p><strong>长期行动（6个月）：</strong>优化供应链结构，降低整体风险</p>
                        """
            else:
                return """
                            <p><strong>近期行动（1个月）：</strong>监控供应风险变化，关注高风险物料</p>
                            <p><strong>中期行动（3个月）：</strong>优化供应商管理体系，提高供应稳定性</p>
                            <p><strong>长期行动（6个月）：</strong>建立供应风险管理长效机制，提高韧性</p>
                        """
        else:
            return """
                        <p><strong>近期行动（1个月）：</strong>开展物料供应风险评估，识别潜在风险</p>
                        <p><strong>中期行动（3个月）：</strong>制定关键物料供应保障策略</p>
                        <p><strong>长期行动（6个月）：</strong>建立供应风险管理体系，提高供应链韧性</p>
                    """

    return "<p>行动计划加载中...</p>"

    # ==================== 6. 主页面函数 ====================


def show_material_analysis():
    """显示物料分析页面"""
    # 页面样式
    st.markdown("""
            <style>
            .main { background-color: #f8f9fa; }
            .stButton > button {
                background-color: #1f3867;
                color: white;
                border: none;
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                font-weight: bold;
                transition: all 0.3s;
            }
            .stButton > button:hover {
                background-color: #4c78a8;
                box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
            }
            </style>
            """, unsafe_allow_html=True)

    # 页面标题
    st.title("🧰 物料分析")

    # 加载数据
    with st.spinner("正在加载物料数据..."):
        material_orders, inventory_data = load_material_data()

    if material_orders.empty:
        st.error("无法加载物料数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_materials = apply_material_filters(material_orders)

    # 分析数据
    analysis_result = analyze_material_data(filtered_materials, inventory_data)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("无法分析物料数据，请检查数据格式")
        return

    # 获取关键指标
    total_material_cost = analysis_result.get('total_material_cost', 0)
    avg_turnover_rate = analysis_result.get('avg_turnover_rate', 0)
    avg_coverage_days = analysis_result.get('avg_coverage_days', 0)

    # 计算供应风险得分（加权平均）
    supply_risk = analysis_result.get('supply_risk', {})
    if supply_risk:
        high_risk = supply_risk.get('高风险', 0)
        medium_risk = supply_risk.get('中风险', 0)
        low_risk = supply_risk.get('低风险', 0)

        risk_score = (high_risk * 3 + medium_risk * 2 + low_risk * 1) / (high_risk + medium_risk + low_risk) if (
                                                                                                                            high_risk + medium_risk + low_risk) > 0 else 0
    else:
        risk_score = 0

    # 显示关键指标卡片
    st.subheader("📊 物料概览")

    col1, col2 = st.columns(2)

    with col1:
        create_material_flip_card(
            "total_cost",
            "物料费用总额",
            total_material_cost,
            "当前累计物料费用",
            is_currency=True
        )

    with col2:
        create_material_flip_card(
            "turnover_rate",
            "物料周转率",
            avg_turnover_rate,
            "高周转>1.5，低周转<0.5"
        )

    col3, col4 = st.columns(2)

    with col3:
        create_material_flip_card(
            "coverage_days",
            "库存覆盖天数",
            avg_coverage_days,
            "最佳范围30-60天"
        )

    with col4:
        create_material_flip_card(
            "supply_risk",
            "物料供应风险",
            risk_score,
            "满分3分，越低越好"
        )

    # 物料使用趋势
    st.subheader("📊 物料使用趋势")

    monthly_material = analysis_result.get('monthly_material', pd.DataFrame())
    if not monthly_material.empty:
        # 月度物料使用趋势
        fig = create_material_trend_chart(monthly_material, "月度物料使用趋势")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        current_month_data = monthly_material.iloc[-1] if len(monthly_material) > 0 else None
        previous_month_data = monthly_material.iloc[-2] if len(monthly_material) > 1 else None

        if current_month_data is not None and previous_month_data is not None:
            current_cost = current_month_data['求和项:金额（元）']
            previous_cost = previous_month_data['求和项:金额（元）']

            mom_change = ((current_cost - previous_cost) / previous_cost * 100) if previous_cost > 0 else 0

            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>📊 图表解读</h4>
                        <p>当月物料使用费用为 {format_currency(current_cost)}，环比{previous_month_data['月份']}月{'增长' if mom_change > 0 else '下降'}{format_percentage(abs(mom_change))}。
                        {'物料使用呈上升趋势，需关注成本控制。' if mom_change > 5 else '物料使用呈下降趋势，成本管控有效。' if mom_change < -5 else '物料使用相对稳定，波动在合理范围内。'}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # 物料类型分布
    st.subheader("📊 物料类型分布")

    material_types = analysis_result.get('material_types', pd.DataFrame())
    if not material_types.empty:
        # 物料类型分布饼图
        fig = create_material_type_chart(material_types, "物料类型分布")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_type = material_types.iloc[0] if len(material_types) > 0 else None

        if top_type is not None:
            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>📊 图表解读</h4>
                        <p>主要物料类型为 {top_type['订单类型']}，占比{format_percentage(top_type['占比'])}，费用{format_currency(top_type['求和项:金额（元）'])}。
                        {'物料费用集中度较高，存在优化空间。' if top_type['占比'] > 60 else '物料费用分布相对均衡。'}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # 客户物料使用分析
    st.subheader("📊 客户物料使用分析")

    customer_material = analysis_result.get('customer_material', pd.DataFrame())
    if not customer_material.empty:
        # 客户物料使用TOP10
        fig = create_customer_material_chart(customer_material, "客户物料使用TOP10")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_customer = customer_material.iloc[0] if len(customer_material) > 0 else None

        if top_customer is not None:
            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>📊 图表解读</h4>
                        <p>物料使用最多的客户为 {top_customer['客户简称']}，使用物料费用{format_currency(top_customer['求和项:金额（元）'])}，占比{format_percentage(top_customer['占比'])}。
                        {'客户物料使用集中度较高，需关注依赖风险。' if top_customer['占比'] > 30 else '客户物料使用分布相对均衡。'}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # 物料周转分析
    st.subheader("📊 物料周转分析")

    material_efficiency = analysis_result.get('material_efficiency', pd.DataFrame())
    if not material_efficiency.empty:
        col1, col2 = st.columns(2)

        with col1:
            # 周转率分布直方图
            fig = create_turnover_histogram(analysis_result, "物料周转率分布")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 周转率评级饼图
            fig = create_turnover_rating_pie(analysis_result, "周转率评级分布")
            st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        turnover_rating = analysis_result.get('turnover_rating', {})

        if turnover_rating:
            excellent_count = turnover_rating.get('优秀', 0)
            good_count = turnover_rating.get('良好', 0)
            poor_count = turnover_rating.get('不佳', 0) + turnover_rating.get('很差', 0)
            total_count = sum(turnover_rating.values())

            excellent_percentage = excellent_count / total_count * 100 if total_count > 0 else 0
            good_percentage = good_count / total_count * 100 if total_count > 0 else 0
            poor_percentage = poor_count / total_count * 100 if total_count > 0 else 0

            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>📊 图表解读</h4>
                        <p>平均物料周转率为 {avg_turnover_rate:.2f}，{'整体周转良好' if avg_turnover_rate > 1 else '整体周转一般' if avg_turnover_rate > 0.5 else '整体周转不佳'}。
                        优秀周转率物料占比{format_percentage(excellent_percentage)}，良好周转率物料占比{format_percentage(good_percentage)}，
                        差劣周转率物料占比{format_percentage(poor_percentage)}。
                        {'周转效率良好，资金占用合理。' if avg_turnover_rate > 1 else '周转效率有优化空间，建议改进物料管理。' if avg_turnover_rate > 0.5 else '周转效率较低，资金占用过多，需要重点优化。'}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # 低周转率物料TOP10
        st.subheader("📊 低周转率物料TOP10")

        low_turnover = material_efficiency.sort_values('周转率').head(10)

        if not low_turnover.empty:
            fig = px.bar(
                low_turnover,
                y='物料',
                x='周转率',
                orientation='h',
                title="周转率最低物料TOP10",
                color='周转率',
                color_continuous_scale=px.colors.sequential.Reds_r,
                text_auto='.2f'
            )

            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=60, b=20),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="周转率",
                yaxis_title="物料代码"
            )

            st.plotly_chart(fig, use_container_width=True)

            # 低周转物料建议
            st.markdown(f"""
                    <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid {COLORS['danger']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>⚠️ 低周转物料警告</h4>
                        <p><strong>低周转物料优化建议：</strong></p>
                        <p>• 评估低周转物料的使用必要性，考虑淘汰或替代</p>
                        <p>• 调整采购计划，减少低周转物料的采购量</p>
                        <p>• 实施物料清理行动，加速消化现有库存</p>
                        <p>• 优化物料管理流程，提高使用效率</p>
                        <p>• 加强物料需求预测，避免过度采购</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("暂无物料周转率数据，无法进行周转分析")

    # 区域物料使用分析
    region_material = analysis_result.get('region_material', pd.DataFrame())
    if not region_material.empty:
        st.subheader("📊 区域物料使用分析")

        # 区域物料使用分布
        fig = create_region_material_chart(region_material, "区域物料使用分布")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top_region = region_material.iloc[0] if len(region_material) > 0 else None

        if top_region is not None:
            st.markdown(f"""
                    <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>📊 图表解读</h4>
                        <p>物料使用最多的区域为 {top_region['所属区域']}，使用物料费用{format_currency(top_region['求和项:金额（元）'])}，占比{format_percentage(top_region['占比'])}。
                        {'区域物料使用集中度较高，可能与区域销售规模相关。' if top_region['占比'] > 40 else '区域物料使用分布相对均衡。'}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # 物料供应风险地图
    supply_risk = analysis_result.get('supply_risk', {})
    if supply_risk:
        st.subheader("📊 物料供应风险分析")

        # 物料供应风险分布
        fig = create_supply_risk_chart(supply_risk, "物料供应风险分布")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        high_risk = supply_risk.get('高风险', 0)
        medium_risk = supply_risk.get('中风险', 0)
        low_risk = supply_risk.get('低风险', 0)

        st.markdown(f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                    <h4>📊 图表解读</h4>
                    <p>物料供应风险分布：高风险{format_percentage(high_risk)}，中风险{format_percentage(medium_risk)}，低风险{format_percentage(low_risk)}。
                    综合风险评分{risk_score:.1f}/3.0。
                    {'供应链风险较高，需加强供应商管理和风险控制。' if risk_score > 2 else '供应链风险中等，需关注高风险物料的供应保障。' if risk_score > 1.5 else '供应链风险较低，物料供应相对稳定。'}</p>
                </div>
                """, unsafe_allow_html=True)

    # 物料管理洞察总结
    st.subheader("💡 物料管理洞察总结")

    # 生成洞察总结
    turnover_status = "良好" if avg_turnover_rate > 1 else "一般" if avg_turnover_rate > 0.5 else "不佳"
    turnover_color = COLORS['success'] if avg_turnover_rate > 1 else COLORS['warning'] if avg_turnover_rate > 0.5 else \
    COLORS['danger']

    coverage_status = "过高" if avg_coverage_days > 90 else "适中" if avg_coverage_days > 30 else "不足"
    coverage_color = COLORS['warning'] if avg_coverage_days > 90 else COLORS['success'] if avg_coverage_days > 30 else \
    COLORS['danger']

    risk_status = "高" if risk_score > 2 else "中" if risk_score > 1.5 else "低"
    risk_color = COLORS['danger'] if risk_score > 2 else COLORS['warning'] if risk_score > 1.5 else COLORS['success']

    if avg_turnover_rate > 1 and avg_coverage_days > 30 and avg_coverage_days < 90 and risk_score < 1.5:
        overall_status = "优秀"
        overall_color = COLORS['success']
        comment = "物料管理表现优异，周转良好，库存适中，供应风险低。"
    elif avg_turnover_rate > 0.5 and avg_coverage_days > 15 and risk_score < 2:
        overall_status = "良好"
        overall_color = COLORS['success']
        comment = "物料管理总体良好，部分指标有优化空间。"
    elif avg_turnover_rate > 0.3 and avg_coverage_days > 10 and risk_score < 2.5:
        overall_status = "一般"
        overall_color = COLORS['warning']
        comment = "物料管理存在一定问题，需要改进优化。"
    else:
        overall_status = "欠佳"
        overall_color = COLORS['danger']
        comment = "物料管理问题明显，亟需全面优化。"

    st.markdown(f"""
            <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; border-radius: 0.5rem;">
                <h4>📋 物料管理总评</h4>
                <p><strong>总体状况：</strong><span style="color: {overall_color};">{overall_status}</span></p>
                <p><strong>周转效率：</strong><span style="color: {turnover_color};">{turnover_status}</span> (周转率 {avg_turnover_rate:.2f})</p>
                <p><strong>库存水平：</strong><span style="color: {coverage_color};">{coverage_status}</span> (覆盖天数 {avg_coverage_days:.1f}天)</p>
                <p><strong>供应风险：</strong><span style="color: {risk_color};">{risk_status}</span> (风险评分 {risk_score:.1f}/3.0)</p>
                <p><strong>物料费用：</strong>{format_currency(total_material_cost)}</p>
                <p><strong>综合评价：</strong>{comment}</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    show_material_analysis()