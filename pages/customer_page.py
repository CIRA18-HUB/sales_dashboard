# pages/customer_page.py - 完全自包含的客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# 从config导入配置
from config import COLORS, DATA_FILES, BUSINESS_CONFIG, FORMAT_CONFIG, CHART_CONFIG


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_customer_data():
    """加载客户分析所需的所有数据"""
    try:
        # 加载销售数据
        if os.path.exists(DATA_FILES['sales_data']):
            sales_data = pd.read_excel(DATA_FILES['sales_data'])
        else:
            st.error(f"销售数据文件不存在：{DATA_FILES['sales_data']}")
            return pd.DataFrame(), pd.DataFrame()

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'], errors='coerce')

        # 过滤销售订单（只保留正常产品和TT产品）
        valid_order_types = ['订单-正常产品', '订单-TT产品']
        sales_orders = sales_data[
            sales_data['订单类型'].isin(valid_order_types)
        ].copy()

        # 添加渠道字段
        sales_orders['渠道'] = sales_orders['订单类型'].apply(
            lambda x: 'TT' if x == '订单-TT产品' else 'MT'
        )

        # 确保数据完整性
        required_columns = ['客户代码', '客户简称', '求和项:金额（元）', '所属区域', '申请人']
        missing_columns = [col for col in required_columns if col not in sales_orders.columns]
        if missing_columns:
            st.warning(f"销售数据缺少必要的列: {', '.join(missing_columns)}")

        # 加载客户关系数据
        customer_relations = pd.DataFrame()
        if os.path.exists(DATA_FILES['customer_relations']):
            try:
                customer_relations = pd.read_excel(DATA_FILES['customer_relations'])
            except Exception as e:
                st.warning(f"客户关系数据加载失败: {str(e)}")

        return sales_orders, customer_relations

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


# ==================== 2. 数据处理函数 ====================
def create_sample_data():
    """创建示例数据用于演示"""
    sample_data = pd.DataFrame({
        '客户代码': ['CU0001', 'CU0002', 'CU0003', 'CU0004', 'CU0005'],
        '客户简称': ['示例客户A', '示例客户B', '示例客户C', '示例客户D', '示例客户E'],
        '求和项:金额（元）': [150000, 120000, 80000, 60000, 40000],
        '所属区域': ['东', '南', '中', '北', '西'],
        '申请人': ['销售员A', '销售员B', '销售员C', '销售员D', '销售员E'],
        '渠道': ['MT', 'TT', 'MT', 'TT', 'MT'],
        '发运月份': pd.to_datetime(['2025-01-01', '2025-02-01', '2025-03-01', '2025-04-01', '2025-05-01'])
    })
    return sample_data


def apply_filters(data):
    """应用页面筛选条件"""
    filtered_data = data.copy()

    # 区域筛选
    if hasattr(st.session_state, 'customer_region_filter') and st.session_state.customer_region_filter != '全部':
        filtered_data = filtered_data[
            filtered_data['所属区域'] == st.session_state.customer_region_filter
            ]

    # 申请人筛选
    if hasattr(st.session_state, 'customer_person_filter') and st.session_state.customer_person_filter != '全部':
        filtered_data = filtered_data[
            filtered_data['申请人'] == st.session_state.customer_person_filter
            ]

    # 渠道筛选
    if hasattr(st.session_state, 'customer_channel_filter') and st.session_state.customer_channel_filter != '全部':
        filtered_data = filtered_data[
            filtered_data['渠道'] == st.session_state.customer_channel_filter
            ]

    return filtered_data


# ==================== 3. 工具函数 ====================
def format_currency(value):
    """格式化货币显示"""
    if pd.isna(value) or value == 0:
        return "¥0"

    if value >= FORMAT_CONFIG['currency_unit_threshold']['billion']:
        return f"¥{value / FORMAT_CONFIG['currency_unit_threshold']['billion']:.{FORMAT_CONFIG['decimal_places']['currency']}f}亿"
    elif value >= FORMAT_CONFIG['currency_unit_threshold']['million']:
        return f"¥{value / FORMAT_CONFIG['currency_unit_threshold']['million']:.{FORMAT_CONFIG['decimal_places']['currency']}f}万"
    else:
        return f"¥{value:,.{FORMAT_CONFIG['decimal_places']['currency']}f}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0%"
    return f"{value:.{FORMAT_CONFIG['decimal_places']['percentage']}f}%"


def format_number(value):
    """格式化数字显示"""
    if pd.isna(value):
        return "0"
    return f"{value:,.{FORMAT_CONFIG['decimal_places']['quantity']}f}"


def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# ==================== 4. 客户分析函数 ====================
def analyze_customer_data(sales_data):
    """分析客户数据"""
    if sales_data.empty:
        return {}

    # 基础统计
    total_sales = sales_data['求和项:金额（元）'].sum()
    total_customers = sales_data['客户代码'].nunique()

    # 按客户计算销售额
    customer_sales = sales_data.groupby(['客户代码', '客户简称']).agg({
        '求和项:金额（元）': 'sum',
        '渠道': 'first',
        '所属区域': 'first'
    }).reset_index()
    customer_sales = customer_sales.sort_values('求和项:金额（元）', ascending=False)

    # 计算客户集中度
    top5_sales = customer_sales.head(BUSINESS_CONFIG['top_customer_count'])['求和项:金额（元）'].sum()
    top5_percentage = (top5_sales / total_sales * 100) if total_sales > 0 else 0

    top10_sales = customer_sales.head(10)['求和项:金额（元）'].sum()
    top10_percentage = (top10_sales / total_sales * 100) if total_sales > 0 else 0

    # 渠道分析
    channel_analysis = sales_data.groupby('渠道').agg({
        '客户代码': 'nunique',
        '求和项:金额（元）': 'sum'
    }).reset_index()
    channel_analysis.columns = ['渠道', '客户数量', '销售额']

    # 月度趋势分析
    monthly_customers = pd.DataFrame()
    if '发运月份' in sales_data.columns:
        monthly_customers = sales_data.groupby(
            pd.Grouper(key='发运月份', freq='M')
        )['客户代码'].nunique().reset_index()
        monthly_customers.rename(columns={'客户代码': '客户数量'}, inplace=True)

    # 区域分析
    region_analysis = sales_data.groupby('所属区域').agg({
        '客户代码': 'nunique',
        '求和项:金额（元）': 'sum'
    }).reset_index()
    region_analysis.columns = ['所属区域', '客户数量', '销售额']
    region_analysis = region_analysis.sort_values('销售额', ascending=False)

    return {
        'total_sales': total_sales,
        'total_customers': total_customers,
        'customer_sales': customer_sales,
        'top5_percentage': top5_percentage,
        'top10_percentage': top10_percentage,
        'channel_analysis': channel_analysis,
        'monthly_customers': monthly_customers,
        'region_analysis': region_analysis
    }


# ==================== 5. 图表创建函数 ====================
def create_metric_card(title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建指标卡片"""
    # 格式化值
    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)

    st.markdown(f"""
    <div class="metric-card">
        <p class="card-header">{title}</p>
        <p class="card-value">{formatted_value}</p>
        <p class="card-text">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


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
        color_continuous_scale='Blues',
        text=y_col
    )

    # 格式化文本
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=CHART_CONFIG['height']['large'],
        margin=CHART_CONFIG['margins']['medium'],
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="销售额 (元)",
        yaxis_title="客户",
        coloraxis_showscale=False
    )

    return fig


def create_customer_pie_chart(data, names_col, values_col, title):
    """创建客户分析饼图"""
    fig = px.pie(
        data,
        names=names_col,
        values=values_col,
        title=title,
        color_discrete_sequence=CHART_CONFIG['color_sequences']['primary'],
        hole=0.3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value:,.0f} (%{percent})<extra></extra>'
    )

    fig.update_layout(
        height=CHART_CONFIG['height']['medium'],
        margin=CHART_CONFIG['margins']['small'],
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def create_trend_chart(data, x_col, y_col, title):
    """创建趋势图"""
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20, color=COLORS['gray'])
        )
    else:
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
        height=CHART_CONFIG['height']['medium'],
        margin=CHART_CONFIG['margins']['medium'],
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


# ==================== 6. 主页面函数 ====================
def show_customer_analysis():
    """显示客户分析页面"""
    # 页面标题
    st.markdown('<div class="main-header">👥 客户分析</div>', unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载客户数据..."):
        sales_data, customer_relations = load_customer_data()

    # 如果主数据为空，使用示例数据
    if sales_data.empty:
        st.warning("无法加载真实数据，正在使用示例数据进行演示")
        sales_data = create_sample_data()

    # 侧边栏筛选器
    with st.sidebar:
        st.markdown("### 🔍 客户分析筛选")

        # 区域筛选
        regions = ['全部'] + sorted(sales_data['所属区域'].unique().tolist())
        selected_region = st.selectbox(
            "区域",
            regions,
            key="customer_region_filter"
        )

        # 申请人筛选
        persons = ['全部'] + sorted(sales_data['申请人'].unique().tolist())
        selected_person = st.selectbox(
            "申请人",
            persons,
            key="customer_person_filter"
        )

        # 渠道筛选
        channels = ['全部'] + sorted(sales_data['渠道'].unique().tolist())
        selected_channel = st.selectbox(
            "渠道",
            channels,
            key="customer_channel_filter"
        )

    # 应用筛选
    filtered_data = apply_filters(sales_data)

    if filtered_data.empty:
        st.warning("筛选条件下没有数据，请调整筛选条件")
        return

    # 分析数据
    analysis_result = analyze_customer_data(filtered_data)

    if not analysis_result:
        st.error("数据分析失败")
        return

    # 第一层：关键指标概览
    st.markdown('<div class="sub-header">📊 关键指标概览</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card(
            "客户总数",
            analysis_result['total_customers'],
            "活跃交易客户"
        )

    with col2:
        create_metric_card(
            "销售总额",
            analysis_result['total_sales'],
            "所有客户贡献",
            is_currency=True
        )

    with col3:
        create_metric_card(
            "TOP5客户集中度",
            analysis_result['top5_percentage'],
            "前5名客户销售占比",
            is_percentage=True
        )

    with col4:
        avg_customer_value = analysis_result['total_sales'] / analysis_result['total_customers'] if analysis_result[
                                                                                                        'total_customers'] > 0 else 0
        create_metric_card(
            "平均客户价值",
            avg_customer_value,
            "每客户平均销售额",
            is_currency=True
        )

    # 第二层：图表分析（使用expander）
    with st.expander("📊 客户排行分析", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 TOP10客户销售排行")
            customer_sales = analysis_result.get('customer_sales', pd.DataFrame())
            if not customer_sales.empty:
                fig = create_customer_bar_chart(
                    customer_sales,
                    '客户简称',
                    '求和项:金额（元）',
                    'TOP10客户销售额排行'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无客户销售数据")

        with col2:
            st.markdown("#### 🔄 渠道客户分布")
            channel_analysis = analysis_result.get('channel_analysis', pd.DataFrame())
            if not channel_analysis.empty:
                fig = create_customer_pie_chart(
                    channel_analysis,
                    '渠道',
                    '客户数量',
                    '不同渠道客户数量分布'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无渠道分析数据")

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 左图展示了销售额最高的10个客户排行，帮助识别核心客户；右图显示不同渠道的客户分布情况。
        通过客户排行可以看出销售的集中度，通过渠道分布可以了解业务结构的均衡性。
        <b>行动建议：</b> 重点维护TOP客户关系，同时关注渠道平衡发展。
        """)

    with st.expander("📈 客户趋势与区域分析", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📅 月度客户数量趋势")
            monthly_customers = analysis_result.get('monthly_customers', pd.DataFrame())
            fig = create_trend_chart(
                monthly_customers,
                '发运月份',
                '客户数量',
                '月度活跃客户数量变化'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🌍 区域客户分析")
            region_analysis = analysis_result.get('region_analysis', pd.DataFrame())
            if not region_analysis.empty:
                fig = create_customer_pie_chart(
                    region_analysis,
                    '所属区域',
                    '销售额',
                    '各区域销售额分布'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无区域分析数据")

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 左图显示月度客户数量的变化趋势，反映业务发展的持续性；右图展示各区域的销售贡献分布。
        客户数量趋势有助于评估业务增长的健康度，区域分布有助于资源配置优化。
        <b>行动建议：</b> 关注客户数量下降的月份，分析原因并采取措施；平衡区域发展，避免过度依赖单一区域。
        """)

    # 第三层：深度分析（使用expander）
    with st.expander("🔍 客户深度分析与洞察", expanded=False):
        # 客户依赖度分析
        st.markdown("#### 🎯 客户依赖度风险评估")

        dependency_level = "高风险" if analysis_result['top5_percentage'] > BUSINESS_CONFIG[
            'dependency_threshold'] else "中等风险" if analysis_result['top5_percentage'] > 40 else "低风险"
        dependency_color = COLORS['danger'] if analysis_result['top5_percentage'] > BUSINESS_CONFIG[
            'dependency_threshold'] else COLORS['warning'] if analysis_result['top5_percentage'] > 40 else COLORS[
            'success']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="alert-box alert-info">
                <h4>🔍 风险评估结果</h4>
                <p><strong>TOP5客户占比：</strong>{format_percentage(analysis_result['top5_percentage'])}</p>
                <p><strong>风险等级：</strong><span style="color: {dependency_color};">{dependency_level}</span></p>
                <p><strong>评估标准：</strong>超过{format_percentage(BUSINESS_CONFIG['dependency_threshold'])}为高风险</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="alert-box alert-{'danger' if analysis_result['top5_percentage'] > BUSINESS_CONFIG['dependency_threshold'] else 'warning' if analysis_result['top5_percentage'] > 40 else 'success'}">
                <h4>💡 风险缓解建议</h4>
                {'<p>• 立即制定客户分散策略<br>• 开发新客户降低依赖<br>• 建立客户流失预警机制</p>' if analysis_result['top5_percentage'] > BUSINESS_CONFIG['dependency_threshold'] else
            '<p>• 继续维护核心客户关系<br>• 适度开发新客户<br>• 定期评估客户集中度</p>' if analysis_result['top5_percentage'] > 40 else
            '<p>• 保持良好的客户结构<br>• 深化客户价值挖掘<br>• 持续优化客户组合</p>'}
            </div>
            """, unsafe_allow_html=True)

        # 详细数据表格
        st.markdown("#### 📋 客户详细数据表")

        customer_sales = analysis_result.get('customer_sales', pd.DataFrame())
        if not customer_sales.empty:
            # 添加排名和占比
            customer_display = customer_sales.copy()
            customer_display['排名'] = range(1, len(customer_display) + 1)
            customer_display['销售占比'] = (
                    customer_display['求和项:金额（元）'] / analysis_result['total_sales'] * 100
            ).round(FORMAT_CONFIG['decimal_places']['percentage'])
            customer_display['累计占比'] = customer_display['销售占比'].cumsum()

            # 格式化显示列
            display_columns = ['排名', '客户代码', '客户简称', '渠道', '所属区域']
            customer_display['销售额(格式化)'] = customer_display['求和项:金额（元）'].apply(format_currency)
            customer_display['销售占比(格式化)'] = customer_display['销售占比'].apply(lambda x: f"{x}%")
            customer_display['累计占比(格式化)'] = customer_display['累计占比'].apply(lambda x: f"{x}%")

            display_columns.extend(['销售额(格式化)', '销售占比(格式化)', '累计占比(格式化)'])

            st.dataframe(
                customer_display[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.info("暂无客户详细数据")

    # 总结洞察
    st.markdown("#### 💡 客户分析总结洞察")

    # 生成智能洞察
    total_customers = analysis_result['total_customers']
    top5_percentage = analysis_result['top5_percentage']

    insight_color = COLORS['danger'] if top5_percentage > BUSINESS_CONFIG['dependency_threshold'] else COLORS[
        'warning'] if top5_percentage > 40 else COLORS['success']

    st.markdown(f"""
    <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0.5rem;">
        <h4>📊 核心发现</h4>
        <p><strong>客户规模：</strong>当前共服务 {total_customers} 个活跃客户，销售总额 {format_currency(analysis_result['total_sales'])}</p>
        <p><strong>集中度评估：</strong><span style="color: {insight_color};">TOP5客户贡献 {format_percentage(top5_percentage)} 的销售额</span></p>
        <p><strong>渠道分布：</strong>{'多渠道均衡发展' if len(analysis_result.get('channel_analysis', pd.DataFrame())) > 1 else '单一渠道为主'}</p>

        <h4>🎯 战略建议</h4>
        <p><strong>短期行动：</strong>{'优化客户结构，降低集中度风险' if top5_percentage > 50 else '深化客户价值，提升服务质量'}</p>
        <p><strong>中期规划：</strong>建立客户分层管理体系，制定差异化服务策略</p>
        <p><strong>长期目标：</strong>构建稳定多元的客户生态，实现可持续增长</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show_customer_analysis()