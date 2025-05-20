# pages/customer_page.py - 完全自包含的客户分析页面
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
def load_customer_data():
    """加载客户分析所需的所有数据"""
    try:
        # 加载销售数据
        sales_data = pd.read_excel(DATA_FILES['sales_data'])

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

        # 过滤销售订单（只保留正常产品和TT产品）
        sales_orders = sales_data[
            sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

        # 添加渠道字段
        sales_orders['渠道'] = sales_orders['订单类型'].apply(
            lambda x: 'TT' if x == '订单-TT产品' else 'MT'
        )

        # 加载客户关系数据
        try:
            customer_relations = pd.read_excel(DATA_FILES['customer_relations'])
        except:
            customer_relations = pd.DataFrame()

        return sales_orders, customer_relations

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


def apply_customer_filters(data):
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


# ==================== 3. 客户分析函数 ====================
def analyze_customer_data(sales_data):
    """分析客户数据"""
    if sales_data.empty:
        return {}

    # 计算总销售额
    total_sales = sales_data['求和项:金额（元）'].sum()

    # 按客户计算销售额
    customer_sales = sales_data.groupby(['客户代码', '客户简称'])['求和项:金额（元）'].sum().reset_index()
    customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False)

    # 计算客户数量
    total_customers = len(customer_sales)

    # 计算TOP客户占比
    if not customer_sales.empty:
        top5_sales = customer_sales.head(5)['求和项:金额（元）'].sum()
        top5_percentage = (top5_sales / total_sales * 100) if total_sales > 0 else 0

        top10_sales = customer_sales.head(10)['求和项:金额（元）'].sum()
        top10_percentage = (top10_sales / total_sales * 100) if total_sales > 0 else 0
    else:
        top5_percentage = 0
        top10_percentage = 0

    # 按渠道分析客户
    mt_customers = sales_data[sales_data['渠道'] == 'MT']['客户代码'].nunique()
    tt_customers = sales_data[sales_data['渠道'] == 'TT']['客户代码'].nunique()

    # 按月份分析客户数量变化
    monthly_customers = sales_data.groupby(
        pd.Grouper(key='发运月份', freq='M')
    )['客户代码'].nunique().reset_index()
    monthly_customers.rename(columns={'客户代码': '客户数量'}, inplace=True)

    return {
        'total_sales': total_sales,
        'total_customers': total_customers,
        'customer_sales': customer_sales,
        'top5_percentage': top5_percentage,
        'top10_percentage': top10_percentage,
        'mt_customers': mt_customers,
        'tt_customers': tt_customers,
        'monthly_customers': monthly_customers
    }


# ==================== 4. 图表创建函数 ====================
def create_customer_pie_chart(data, names_col, values_col, title):
    """创建客户分析饼图"""
    fig = px.pie(
        data,
        names=names_col,
        values=values_col,
        title=title,
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['success'],
                                 COLORS['warning'], COLORS['info']],
        hole=0.3
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
        paper_bgcolor='white'
    )

    return fig


def create_customer_bar_chart(data, x_col, y_col, title, top_n=10):
    """创建客户销售额柱状图"""
    plot_data = data.head(top_n)

    fig = px.bar(
        plot_data,
        x=y_col,
        y=x_col,
        orientation='h',
        title=title,
        color=y_col,
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=500,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def create_customer_trend_chart(data, x_col, y_col, title):
    """创建客户趋势图"""
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
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
        paper_bgcolor='white'
    )

    return fig


# ==================== 5. 翻卡组件 ====================
def create_customer_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建客户分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"customer_flip_{card_id}"
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
            if "客户数量" in title:
                # 显示客户分布图表
                if 'analysis_result' in st.session_state:
                    monthly_data = st.session_state['analysis_result'].get('monthly_customers', pd.DataFrame())
                    if not monthly_data.empty:
                        fig = create_customer_trend_chart(monthly_data, '发运月份', '客户数量', '月度客户数量变化')
                        st.plotly_chart(fig, use_container_width=True)

            elif "销售额" in title:
                # 显示客户销售排行
                if 'analysis_result' in st.session_state:
                    customer_sales = st.session_state['analysis_result'].get('customer_sales', pd.DataFrame())
                    if not customer_sales.empty:
                        fig = create_customer_bar_chart(customer_sales, '客户简称', '求和项:金额（元）',
                                                        'TOP10客户销售额排行')
                        st.plotly_chart(fig, use_container_width=True)

            # 洞察文本
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>💡 数据洞察</h4>
                <p>当前{title}表现良好，建议继续保持并优化相关策略。</p>
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
                    <p>• 当前指标值：{formatted_value}</p>
                    <p>• 发展趋势：稳步上升</p>
                    <p>• 影响因素：市场环境、产品策略、销售执行</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid {COLORS['warning']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>🎯 优化建议</h4>
                    <p>• 继续维护现有优势</p>
                    <p>• 关注潜在改进空间</p>
                    <p>• 制定针对性提升方案</p>
                </div>
                """, unsafe_allow_html=True)

            # 行动方案
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin-top: 1rem; border-radius: 0.5rem;">
                <h4>📋 行动方案</h4>
                <p><strong>短期目标（1个月）：</strong>深入分析当前{title}表现，识别关键成功因素</p>
                <p><strong>中期目标（3个月）：</strong>制定并实施优化策略，提升整体表现</p>
                <p><strong>长期目标（6个月）：</strong>建立持续改进机制，确保长期稳定增长</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击返回基础视图 ↻</p>",
                        unsafe_allow_html=True)


# ==================== 6. 主页面函数 ====================
def show_customer_analysis():
    """显示客户分析页面"""
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
    st.title("🏢 客户分析")

    # 加载数据
    with st.spinner("正在加载客户数据..."):
        sales_data, customer_relations = load_customer_data()

    if sales_data.empty:
        st.error("无法加载销售数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_data = apply_customer_filters(sales_data)

    # 分析数据
    analysis_result = analyze_customer_data(filtered_data)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("没有符合筛选条件的数据")
        return

    # 显示关键指标卡片
    st.subheader("📊 客户概览")

    col1, col2, col3 = st.columns(3)

    with col1:
        create_customer_flip_card(
            "total_customers",
            "客户数量",
            analysis_result['total_customers'],
            "活跃交易客户"
        )

    with col2:
        create_customer_flip_card(
            "total_sales",
            "客户销售总额",
            analysis_result['total_sales'],
            "所有客户贡献",
            is_currency=True
        )

    with col3:
        create_customer_flip_card(
            "top5_concentration",
            "TOP5客户集中度",
            analysis_result['top5_percentage'],
            "前5名客户销售占比",
            is_percentage=True
        )

    # 详细分析
    st.subheader("📈 客户详细分析")

    # 两列布局
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 客户销售排行")
        customer_sales = analysis_result.get('customer_sales', pd.DataFrame())
        if not customer_sales.empty:
            fig = create_customer_bar_chart(customer_sales, '客户简称', '求和项:金额（元）', 'TOP10客户销售额')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无客户销售数据")

    with col2:
        st.markdown("#### 客户数量趋势")
        monthly_customers = analysis_result.get('monthly_customers', pd.DataFrame())
        if not monthly_customers.empty:
            fig = create_customer_trend_chart(monthly_customers, '发运月份', '客户数量', '月度客户数量变化')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无客户趋势数据")

    # 渠道分析
    st.subheader("🔄 渠道客户分析")

    channel_data = pd.DataFrame({
        '渠道': ['MT渠道', 'TT渠道'],
        '客户数量': [analysis_result.get('mt_customers', 0), analysis_result.get('tt_customers', 0)]
    })

    if channel_data['客户数量'].sum() > 0:
        fig = create_customer_pie_chart(channel_data, '渠道', '客户数量', '渠道客户分布')
        st.plotly_chart(fig, use_container_width=True)

    # 客户洞察总结
    st.subheader("💡 客户洞察总结")

    total_customers = analysis_result['total_customers']
    top5_percentage = analysis_result['top5_percentage']

    # 生成洞察
    if top5_percentage > 60:
        dependency_level = "高"
        dependency_desc = "客户集中度过高，存在较大依赖风险"
        dependency_color = COLORS['danger']
    elif top5_percentage > 40:
        dependency_level = "中"
        dependency_desc = "客户集中度适中，风险可控"
        dependency_color = COLORS['warning']
    else:
        dependency_level = "低"
        dependency_desc = "客户分布较为均衡，风险较低"
        dependency_color = COLORS['success']

    st.markdown(f"""
    <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0.5rem;">
        <h4>📋 客户分析总结</h4>
        <p><strong>客户规模：</strong>共有 {total_customers} 个活跃客户</p>
        <p><strong>客户依赖度：</strong><span style="color: {dependency_color};">{dependency_level}</span> - {dependency_desc}</p>
        <p><strong>TOP5客户占比：</strong>{format_percentage(top5_percentage)}</p>
        <p><strong>建议措施：</strong>{'分散客户风险，开发新客户' if top5_percentage > 50 else '维持良好的客户结构'}</p>
    </div>
    """, unsafe_allow_html=True)

    # 数据表格（可选展开）
    with st.expander("📊 客户销售明细表"):
        if not customer_sales.empty:
            # 添加排名和占比
            customer_display = customer_sales.copy()
            customer_display['排名'] = range(1, len(customer_display) + 1)
            customer_display['销售占比'] = (
                        customer_display['求和项:金额（元）'] / analysis_result['total_sales'] * 100).round(2)
            customer_display['销售额(格式化)'] = customer_display['求和项:金额（元）'].apply(format_currency)
            customer_display['销售占比(格式化)'] = customer_display['销售占比'].apply(lambda x: f"{x}%")

            # 选择显示的列
            display_columns = ['排名', '客户代码', '客户简称', '销售额(格式化)', '销售占比(格式化)']
            st.dataframe(
                customer_display[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.info("暂无客户数据")


if __name__ == "__main__":
    show_customer_analysis()