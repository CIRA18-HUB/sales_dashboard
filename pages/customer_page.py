# pages/customer_page.py - 客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import warnings
from config import load_css, format_currency, format_percentage, format_number, DATA_FILES, COLORS

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载统一CSS样式
load_css()

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">销售数据分析仪表盘 | 登录</div>', unsafe_allow_html=True)

    # 创建居中的登录框
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
            <h2 style="text-align: center; color: #1f3867; margin-bottom: 20px;">请输入密码</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("密码", type="password", key="password_input")

        # 登录按钮
        login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
        with login_col2:
            login_button = st.button("登录", key="login_button")

        # 验证密码
        if login_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()

# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">👥 客户分析</h1>', unsafe_allow_html=True)

# ==================== 模拟数据加载 ====================
@st.cache_data
def load_example_data():
    """加载示例数据"""
    # 客户数据
    customer_data = pd.DataFrame({
        '客户代码': [f'CU{i:04d}' for i in range(1, 21)],
        '客户简称': [f'客户{i}' for i in range(1, 21)],
        '所属区域': np.random.choice(['东', '南', '西', '北', '中'], 20),
        '销售额': np.random.randint(10000, 500000, 20),
        '购买产品种类': np.random.randint(1, 15, 20),
        '申请人': np.random.choice(['李明', '张伟', '王芳', '赵敏', '刘强'], 20)
    })

    # 模拟销售订单数据
    orders = []
    for i in range(50):
        customer_idx = np.random.randint(0, len(customer_data))
        customer_row = customer_data.iloc[customer_idx]

        for j in range(np.random.randint(1, 5)):  # 每个客户1-4个订单
            product_code = f'F{np.random.randint(1000, 9999)}'
            product_name = f'口力{np.random.choice(["汉堡", "薯条", "汽水", "披萨", "糖果"])}{np.random.randint(50, 200)}G袋装-中国'

            orders.append({
                '发运月份': f'2025-{np.random.randint(1, 6):02d}',
                '所属区域': customer_row['所属区域'],
                '客户代码': customer_row['客户代码'],
                '客户简称': customer_row['客户简称'],
                '申请人': customer_row['申请人'],
                '订单类型': '订单-正常产品',
                '产品代码': product_code,
                '产品名称': product_name,
                '单价（箱）': np.random.randint(100, 300),
                '数量（箱）': np.random.randint(10, 100)
            })

    orders_df = pd.DataFrame(orders)
    orders_df['销售额'] = orders_df['单价（箱）'] * orders_df['数量（箱）']
    orders_df['发运月份'] = pd.to_datetime(orders_df['发运月份'])

    return orders_df

# 加载示例数据
sales_data = load_example_data()

# ==================== 侧边栏筛选器 ====================
st.sidebar.header("🔍 数据筛选")

# 初始化筛选器状态
if "customer_filter_region" not in st.session_state:
    st.session_state.customer_filter_region = "全部"
if "customer_filter_salesperson" not in st.session_state:
    st.session_state.customer_filter_salesperson = "全部"
if "customer_filter_customer" not in st.session_state:
    st.session_state.customer_filter_customer = "全部"
if "customer_filter_date_range" not in st.session_state:
    st.session_state.customer_filter_date_range = (
        sales_data['发运月份'].min().date(),
        sales_data['发运月份'].max().date()
    )

# 筛选说明
st.sidebar.markdown('<p style="color: #666; font-size: 0.9rem;">选择区域、销售员或客户进行数据筛选</p>',
                    unsafe_allow_html=True)

# 区域筛选器
all_regions = sorted(['全部'] + list(sales_data['所属区域'].unique()))
selected_region = st.sidebar.selectbox(
    "选择区域",
    all_regions,
    index=0,
    key="customer_sidebar_region"
)
st.session_state.customer_filter_region = selected_region

# 销售员筛选器
all_salespersons = sorted(['全部'] + list(sales_data['申请人'].unique()))
selected_salesperson = st.sidebar.selectbox(
    "选择销售员",
    all_salespersons,
    index=0,
    key="customer_sidebar_salesperson"
)
st.session_state.customer_filter_salesperson = selected_salesperson

# 客户筛选器
all_customers = sorted(['全部'] + list(sales_data['客户简称'].unique()))
selected_customer = st.sidebar.selectbox(
    "选择客户",
    all_customers,
    index=0,
    key="customer_sidebar_customer"
)
st.session_state.customer_filter_customer = selected_customer

# 日期范围筛选器
st.sidebar.markdown("### 日期范围")
start_date = st.sidebar.date_input(
    "开始日期",
    value=sales_data['发运月份'].min().date(),
    min_value=sales_data['发运月份'].min().date(),
    max_value=sales_data['发运月份'].max().date(),
    key="customer_sidebar_start_date"
)
end_date = st.sidebar.date_input(
    "结束日期",
    value=sales_data['发运月份'].max().date(),
    min_value=sales_data['发运月份'].min().date(),
    max_value=sales_data['发运月份'].max().date(),
    key="customer_sidebar_end_date"
)

if end_date < start_date:
    end_date = start_date
    st.sidebar.warning("结束日期不能早于开始日期，已自动调整。")

st.session_state.customer_filter_date_range = (start_date, end_date)

# 重置筛选按钮
if st.sidebar.button("重置筛选条件", key="customer_reset_filters"):
    st.session_state.customer_filter_region = "全部"
    st.session_state.customer_filter_salesperson = "全部"
    st.session_state.customer_filter_customer = "全部"
    st.session_state.customer_filter_date_range = (
        sales_data['发运月份'].min().date(),
        sales_data['发运月份'].max().date()
    )
    st.rerun()

# 应用筛选条件
filtered_data = sales_data.copy()

# 应用区域筛选
if st.session_state.customer_filter_region != "全部":
    filtered_data = filtered_data[filtered_data['所属区域'] == st.session_state.customer_filter_region]

# 应用销售员筛选
if st.session_state.customer_filter_salesperson != "全部":
    filtered_data = filtered_data[filtered_data['申请人'] == st.session_state.customer_filter_salesperson]

# 应用客户筛选
if st.session_state.customer_filter_customer != "全部":
    filtered_data = filtered_data[filtered_data['客户简称'] == st.session_state.customer_filter_customer]

# 应用日期筛选
start_date, end_date = st.session_state.customer_filter_date_range
filtered_data = filtered_data[
    (filtered_data['发运月份'].dt.date >= start_date) &
    (filtered_data['发运月份'].dt.date <= end_date)
]

# ==================== 分析数据 ====================
def analyze_customer_data(data):
    """分析客户数据"""
    if data.empty:
        return {
            'total_customers': 0,
            'top5_concentration': 0,
            'top10_concentration': 0,
            'avg_customer_value': 0,
            'dependency_risk_score': 0,
            'customer_sales': pd.DataFrame(),
            'region_stats': pd.DataFrame()
        }

    # 客户总数
    total_customers = data['客户代码'].nunique()

    # 客户销售额统计
    customer_sales = data.groupby(['客户代码', '客户简称']).agg({
        '销售额': 'sum',
        '产品代码': 'nunique',
        '申请人': lambda x: x.value_counts().index[0] if not x.empty else "未知"
    }).reset_index()

    customer_sales.columns = ['客户代码', '客户简称', '销售额', '购买产品种类', '主要销售员']
    customer_sales = customer_sales.sort_values('销售额', ascending=False)

    # 计算TOP5、TOP10客户销售额
    total_sales = customer_sales['销售额'].sum()

    if len(customer_sales) >= 5:
        top5_sales = customer_sales.head(5)['销售额'].sum()
    else:
        top5_sales = total_sales

    if len(customer_sales) >= 10:
        top10_sales = customer_sales.head(10)['销售额'].sum()
    else:
        top10_sales = total_sales

    # 计算集中度
    top5_concentration = (top5_sales / total_sales * 100) if total_sales > 0 else 0
    top10_concentration = (top10_sales / total_sales * 100) if total_sales > 0 else 0

    # 计算平均客户价值
    avg_customer_value = total_sales / total_customers if total_customers > 0 else 0

    # 计算客户依赖度风险
    dependency_risk_score = top5_concentration  # 简单起见，直接用TOP5集中度作为依赖风险

    # 按区域统计客户
    region_stats = data.groupby('所属区域').agg({
        '客户代码': lambda x: len(set(x)),
        '销售额': 'sum'
    }).reset_index()

    region_stats.columns = ['所属区域', '客户数量', '销售额']
    region_stats['平均客户价值'] = region_stats['销售额'] / region_stats['客户数量']

    # 添加客户价值分类
    if not customer_sales.empty:
        avg_value = customer_sales['销售额'].mean()
        avg_variety = customer_sales['购买产品种类'].mean()

        customer_sales['客户类型'] = customer_sales.apply(
            lambda row: '高价值核心客户' if row['销售额'] > avg_value and row['购买产品种类'] > avg_variety
            else '高价值单一客户' if row['销售额'] > avg_value and row['购买产品种类'] <= avg_variety
            else '低价值多样客户' if row['销售额'] <= avg_value and row['购买产品种类'] > avg_variety
            else '低价值边缘客户',
            axis=1
        )

    return {
        'total_customers': total_customers,
        'top5_concentration': top5_concentration,
        'top10_concentration': top10_concentration,
        'avg_customer_value': avg_customer_value,
        'dependency_risk_score': dependency_risk_score,
        'customer_sales': customer_sales,
        'region_stats': region_stats
    }

# 分析数据
customer_analysis = analyze_customer_data(filtered_data)

# ==================== 图表创建函数 ====================
def create_concentration_gauge(concentration, title="客户集中度"):
    """创建客户集中度仪表盘"""
    # 确定颜色和状态
    if concentration <= 50:
        color = COLORS['success']
        status = "健康"
    elif concentration <= 70:
        color = COLORS['warning']
        status = "警示"
    else:
        color = COLORS['danger']
        status = "风险"

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=concentration,
        title={
            'text': f"{title}<br><span style='font-size:0.8em;color:{color}'>{status}</span>",
            'font': {'size': 24, 'family': "Arial"}
        },
        number={
            'suffix': "%",
            'font': {'size': 26, 'color': color, 'family': "Arial"}
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS['primary']},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': f"rgba(76, 175, 80, 0.3)"},
                {'range': [50, 70], 'color': f"rgba(255, 152, 0, 0.3)"},
                {'range': [70, 100], 'color': f"rgba(244, 67, 54, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor="white",
        font={'color': COLORS['primary'], 'family': "Arial"}
    )

    return fig


def create_customer_bar_chart(customer_data, title="客户销售额分布"):
    """创建客户销售额柱状图"""
    if customer_data.empty:
        return None

    # 只取前10名客户
    top_customers = customer_data.head(10).copy()

    fig = px.bar(
        top_customers,
        x='客户简称',
        y='销售额',
        title=title,
        color='销售额',
        color_continuous_scale=px.colors.sequential.Blues,
        text='销售额'
    )

    fig.update_traces(
        texttemplate='¥%{y:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="客户",
        yaxis_title="销售额（元）",
        xaxis={'categoryorder': 'total descending', 'tickangle': -45},
        coloraxis_showscale=False,
        font={'family': "Arial"}
    )

    return fig


def create_region_bars(region_data, value_col='客户数量', title="区域客户分布"):
    """创建区域柱状图"""
    if region_data.empty:
        return None

    # 按值排序
    sorted_data = region_data.sort_values(value_col, ascending=False)

    fig = px.bar(
        sorted_data,
        x='所属区域',
        y=value_col,
        title=title,
        color='所属区域',
        text=value_col,
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    # 调整文本显示格式
    if value_col == '平均客户价值':
        fig.update_traces(texttemplate='¥%{y:,.0f}', textposition='outside')
    else:
        fig.update_traces(textposition='outside')

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="区域",
        yaxis_title=value_col,
        showlegend=False,
        font={'family': "Arial"}
    )

    return fig


def create_customer_scatter(customer_data, title="客户价值与产品多样性分布"):
    """创建客户散点图"""
    if customer_data.empty:
        return None

    fig = px.scatter(
        customer_data,
        x='购买产品种类',
        y='销售额',
        size='销售额',
        color='主要销售员',
        hover_name='客户简称',
        title=title,
        size_max=50
    )

    # 添加平均线
    avg_value = customer_data['销售额'].mean()
    fig.add_shape(
        type="line",
        x0=0,
        x1=customer_data['购买产品种类'].max() * 1.1,
        y0=avg_value,
        y1=avg_value,
        line=dict(color="red", width=1, dash="dash")
    )

    fig.add_annotation(
        x=customer_data['购买产品种类'].max() * 0.9,
        y=avg_value * 1.1,
        text="平均客户价值",
        showarrow=False,
        font=dict(color="red")
    )

    fig.update_layout(
        height=450,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="购买产品种类",
        yaxis_title="销售额（元）",
        font={'family': "Arial"}
    )

    return fig


def create_customer_pie(customer_data, title="客户价值分类占比"):
    """创建客户价值分类饼图"""
    if customer_data.empty or '客户类型' not in customer_data.columns:
        return None

    # 统计各类客户数量
    segments = customer_data.groupby('客户类型').size().reset_index(name='客户数量')

    # 颜色映射
    color_map = {
        '高价值核心客户': COLORS['success'],
        '高价值单一客户': COLORS['info'],
        '低价值多样客户': COLORS['warning'],
        '低价值边缘客户': COLORS['danger']
    }

    fig = px.pie(
        segments,
        names='客户类型',
        values='客户数量',
        title=title,
        color='客户类型',
        color_discrete_map=color_map
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value}个客户<br>占比: %{percent}'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        font={'family': "Arial"}
    )

    return fig


# ==================== 主页面 ====================
# 检查是否有数据
if filtered_data.empty:
    st.warning("当前筛选条件下没有数据，请调整筛选条件。")
else:
    # KPI指标行
    st.markdown('<div class="sub-header">🔑 关键客户指标</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # 客户总数
    total_customers = customer_analysis.get('total_customers', 0)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">客户总数</p>
            <p class="card-value">{format_number(total_customers)}</p>
            <p class="card-text">活跃客户数量</p>
        </div>
        """, unsafe_allow_html=True)

    # TOP5客户集中度
    top5_concentration = customer_analysis.get('top5_concentration', 0)
    with col2:
        concentration_color = COLORS['success'] if top5_concentration <= 50 else COLORS['warning'] if top5_concentration <= 70 else COLORS['danger']
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">TOP5客户集中度</p>
            <p class="card-value" style="color: {concentration_color};">{format_percentage(top5_concentration)}</p>
            <p class="card-text">TOP5客户占比</p>
        </div>
        """, unsafe_allow_html=True)

    # 平均客户价值
    avg_customer_value = customer_analysis.get('avg_customer_value', 0)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均客户价值</p>
            <p class="card-value">{format_currency(avg_customer_value)}</p>
            <p class="card-text">客户均值</p>
        </div>
        """, unsafe_allow_html=True)

    # 客户依赖度风险
    dependency_risk = customer_analysis.get('dependency_risk_score', 0)
    with col4:
        risk_level = "低" if dependency_risk <= 50 else "中" if dependency_risk <= 70 else "高"
        risk_color = COLORS['success'] if dependency_risk <= 50 else COLORS['warning'] if dependency_risk <= 70 else COLORS['danger']

        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">客户依赖度风险</p>
            <p class="card-value" style="color: {risk_color};">{risk_level}</p>
            <p class="card-text">客户集中风险评估</p>
        </div>
        """, unsafe_allow_html=True)

    # 创建标签页
    tabs = st.tabs(["📊 客户概览", "👑 TOP客户分析", "🌐 区域客户分析", "🔍 客户价值分析"])

    with tabs[0]:  # 客户概览
        # 客户概览分析
        st.markdown('<div class="sub-header">📊 客户概览分析</div>', unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            # 客户集中度仪表盘
            fig = create_concentration_gauge(top5_concentration, "TOP5客户集中度")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                concentration_status = "健康" if top5_concentration <= 50 else "警示" if top5_concentration <= 70 else "风险"

                add_chart_explanation(f"""
                <b>图表解读：</b> TOP5客户集中度为{format_percentage(top5_concentration)}，处于<span style="color: {'#4CAF50' if top5_concentration <= 50 else '#FF9800' if top5_concentration <= 70 else '#F44336'};">{concentration_status}</span>状态。
                {'客户分布较为均衡，业务风险较低。' if top5_concentration <= 50 else '客户较为集中，存在一定依赖风险。' if top5_concentration <= 70 else '客户高度集中，存在严重依赖风险，需要积极开发新客户。'}
                """)

        with cols[1]:
            # TOP10客户集中度
            top10_concentration = customer_analysis.get('top10_concentration', 0)
            fig = create_concentration_gauge(top10_concentration, "TOP10客户集中度")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                concentration_status = "健康" if top10_concentration <= 60 else "警示" if top10_concentration <= 80 else "风险"

                add_chart_explanation(f"""
                <b>图表解读：</b> TOP10客户集中度为{format_percentage(top10_concentration)}，处于<span style="color: {'#4CAF50' if top10_concentration <= 60 else '#FF9800' if top10_concentration <= 80 else '#F44336'};">{concentration_status}</span>状态。
                {'客户基础广泛，业务发展稳健。' if top10_concentration <= 60 else '客户基础略显集中，需关注客户开发。' if top10_concentration <= 80 else '客户严重集中，客户基础薄弱，急需拓展新客户。'}
                """)

        # 客户价值分类
        st.markdown('<div class="sub-header">📊 客户价值分类</div>', unsafe_allow_html=True)

        # 客户价值散点图和分类图
        customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

        cols = st.columns(2)
        with cols[0]:
            fig = create_customer_scatter(customer_sales)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                add_chart_explanation("""
                <b>图表解读：</b> 散点图显示了客户销售额与产品多样性的关系。图中右上方的客户是高价值核心客户，不仅销售额高，而且产品采购多样；右下方的客户是高价值单一客户，销售额高但集中在少数产品；左上方的客户是低价值多样客户，虽采购多样但总额不高；左下方的客户是低价值边缘客户，销售额低且产品单一。
                """)

        with cols[1]:
            fig = create_customer_pie(customer_sales)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                add_chart_explanation("""
                <b>图表解读：</b> 此图展示了不同价值类型客户的分布占比。高价值核心客户具有战略意义，需重点维护；高价值单一客户有扩展潜力，可增加品类渗透；低价值多样客户适合深耕，提升单品渗透率；低价值边缘客户则需评估投入产出比，进行分级管理。
                """)

        # 客户管理建议
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

        if top5_concentration > 70:
            st.markdown("""
            <h4>⚠️ 客户集中度过高警告</h4>
            <p>当前TOP5客户集中度过高，业务过度依赖少数大客户，存在较高经营风险。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>制定客户多元化战略，积极开发新客户</li>
                <li>建立客户风险评估机制，为大客户制定应急预案</li>
                <li>深化与现有客户的合作，但避免过度依赖</li>
                <li>加强销售团队建设，提高获客能力</li>
            </ul>
            """, unsafe_allow_html=True)
        elif top5_concentration > 50:
            st.markdown("""
            <h4>🔔 客户结构优化提示</h4>
            <p>客户集中度处于警戒线附近，需关注客户结构优化。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>积极开发中型客户，培育成长性客户</li>
                <li>深化大客户合作同时，扩大客户基础</li>
                <li>优化客户管理体系，建立分级管理机制</li>
                <li>定期评估客户结构健康度，调整资源配置</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <h4>✅ 客户结构健康</h4>
            <p>当前客户集中度处于健康水平，客户结构相对均衡。</p>
            <p><strong>建议行动：</strong></p>
            <ul>
                <li>维持现有客户开发策略，保持客户结构健康</li>
                <li>关注大客户需求变化，加强服务质量</li>
                <li>挖掘中小客户增长潜力，培育战略客户</li>
                <li>建立客户成长激励机制，提高客户黏性</li>
            </ul>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:  # TOP客户分析
        st.markdown('<div class="sub-header">👑 TOP客户分析</div>', unsafe_allow_html=True)

        # TOP客户销售额分析
        customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

        if not customer_sales.empty:
            # TOP10客户销售额柱状图
            fig = create_customer_bar_chart(customer_sales, "TOP10客户销售额")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                if len(customer_sales) > 0:
                    top1_name = customer_sales.iloc[0]['客户简称']
                    top1_sales = customer_sales.iloc[0]['销售额']
                    total_sales = customer_sales['销售额'].sum()
                    top1_percentage = (top1_sales / total_sales * 100) if total_sales > 0 else 0

                    add_chart_explanation(f"""
                    <b>图表解读：</b> {top1_name}是最大客户，销售额{format_currency(top1_sales)}，占总销售额的{format_percentage(top1_percentage)}。
                    TOP10客户总体占比{format_percentage(customer_analysis.get('top10_concentration', 0))}，{'客户分布较为均衡。' if customer_analysis.get('top10_concentration', 0) <= 60 else '客户较为集中。'}
                    """)

            # TOP客户详细分析
            st.markdown('<div class="sub-header">🔍 TOP5客户详细分析</div>', unsafe_allow_html=True)

            # 获取TOP5客户
            top5_customers = customer_sales.head(5) if len(customer_sales) >= 5 else customer_sales

            # 创建TOP5客户卡片
            for i, row in top5_customers.iterrows():
                customer_name = row['客户简称']
                customer_sales_value = row['销售额']
                customer_percentage = (customer_sales_value / customer_sales['销售额'].sum() * 100) if customer_sales['销售额'].sum() > 0 else 0
                customer_products = row['购买产品种类']
                customer_sales_person = row['主要销售员']
                customer_type = row['客户类型'] if '客户类型' in row else "未分类"

                # 根据客户类型设置建议
                if customer_type == '高价值核心客户':
                    recommendation = "维护核心关系，深化战略合作"
                elif customer_type == '高价值单一客户':
                    recommendation = "扩大产品覆盖，增加品类渗透"
                elif customer_type == '低价值多样客户':
                    recommendation = "提高单品渗透率，增加客单价"
                else:
                    recommendation = "评估维护成本，考虑客户升级"

                st.markdown(f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); margin-bottom: 1rem;">
                    <h3 style="color: #1f3867;">{i + 1}. {customer_name}</h3>
                    <div style="display: flex; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px; margin-right: 1rem;">
                            <p><strong>销售额：</strong> {format_currency(customer_sales_value)}</p>
                            <p><strong>占比：</strong> {format_percentage(customer_percentage)}</p>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <p><strong>购买产品种类：</strong> {customer_products}</p>
                            <p><strong>主要销售员：</strong> {customer_sales_person}</p>
                        </div>
                    </div>
                    <hr>
                    <h4>客户价值分析</h4>
                    <p><strong>价值类型：</strong> {customer_type}</p>
                    <p><strong>发展建议：</strong> {recommendation}</p>
                </div>
                """, unsafe_allow_html=True)

            # TOP客户管理策略
            st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
            st.markdown("""
            <h4>👑 TOP客户管理策略</h4>
            <p>TOP客户是业务的核心支柱，需要精细化管理和差异化策略。</p>
            <p><strong>策略建议：</strong></p>
            <ul>
                <li><strong>战略协同：</strong> 与TOP客户建立战略合作关系，深入了解其业务需求和发展方向</li>
                <li><strong>专属服务：</strong> 为TOP客户提供专属客户经理和服务团队，提升服务质量</li>
                <li><strong>产品定制：</strong> 根据TOP客户需求提供定制化产品和解决方案</li>
                <li><strong>深度合作：</strong> 探索营销协同、供应链优化等多维度合作机会</li>
                <li><strong>风险管控：</strong> 建立客户关系健康度评估机制，及时识别并应对风险</li>
            </ul>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("当前筛选条件下没有客户销售数据。请调整筛选条件。")

    with tabs[2]:  # 区域客户分析
        st.markdown('<div class="sub-header">🌐 区域客户分析</div>', unsafe_allow_html=True)

        # 区域客户分布
        region_stats = customer_analysis.get('region_stats', pd.DataFrame())

        if not region_stats.empty:
            # 区域客户数量和平均客户价值
            cols = st.columns(2)
            with cols[0]:
                fig = create_region_bars(region_stats, '客户数量', "区域客户分布")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读
                    if len(region_stats) > 0:
                        most_region = region_stats.loc[region_stats['客户数量'].idxmax(), '所属区域']
                        most_customers = region_stats.loc[region_stats['客户数量'].idxmax(), '客户数量']

                        # 计算客户分布均衡度
                        is_balanced = False
                        if len(region_stats) > 1:
                            customer_std = region_stats['客户数量'].std()
                            customer_mean = region_stats['客户数量'].mean()
                            is_balanced = (customer_std / customer_mean < 0.3) if customer_mean > 0 else False

                        add_chart_explanation(f"""
                        <b>图表解读：</b> {most_region}区域客户数量最多，有{most_customers}个客户，市场覆盖最广。
                        {'客户分布较为均衡，市场覆盖全面。' if is_balanced else '客户分布不均，区域发展不平衡，需关注薄弱区域。'}
                        """)

            with cols[1]:
                fig = create_region_bars(region_stats, '平均客户价值', "区域平均客户价值")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读
                    if len(region_stats) > 0:
                        highest_value_region = region_stats.loc[region_stats['平均客户价值'].idxmax(), '所属区域']
                        highest_avg_value = region_stats.loc[region_stats['平均客户价值'].idxmax(), '平均客户价值']

                        lowest_value_region = region_stats.loc[region_stats['平均客户价值'].idxmin(), '所属区域']
                        lowest_avg_value = region_stats.loc[region_stats['平均客户价值'].idxmin(), '平均客户价值']

                        value_gap = highest_avg_value / lowest_avg_value if lowest_avg_value > 0 else 0

                        add_chart_explanation(f"""
                        <b>图表解读：</b> {highest_value_region}区域平均客户价值最高，为{format_currency(highest_avg_value)}。
                        {highest_value_region}与{lowest_value_region}区域的平均客户价值差距{value_gap:.1f}倍，{'区域客户价值差异显著' if value_gap > 2 else '区域客户价值较为均衡'}。
                        """)

            # 区域客户价值矩阵
            st.markdown('<div class="sub-header">📊 区域客户价值矩阵</div>', unsafe_allow_html=True)

            # 添加客户密度列
            region_matrix = region_stats.copy()
            total_customers = region_matrix['客户数量'].sum()
            region_matrix['客户密度'] = region_matrix['客户数量'] / total_customers * 100 if total_customers > 0 else 0

            # 计算全局平均值
            avg_density = region_matrix['客户密度'].mean()
            avg_value = region_matrix['平均客户价值'].mean()

            # 添加区域类型
            region_matrix['区域类型'] = region_matrix.apply(
                lambda row: '核心区域' if row['客户密度'] > avg_density and row['平均客户价值'] > avg_value
                else '价值区域' if row['客户密度'] <= avg_density and row['平均客户价值'] > avg_value
                else '数量区域' if row['客户密度'] > avg_density and row['平均客户价值'] <= avg_value
                else '发展区域',
                axis=1
            )

            # 创建散点图
            fig = px.scatter(
                region_matrix,
                x='客户密度',
                y='平均客户价值',
                size='销售额',
                color='区域类型',
                hover_name='所属区域',
                text='所属区域',
                title="区域客户价值矩阵",
                size_max=50,
                color_discrete_map={
                    '核心区域': COLORS['success'],
                    '价值区域': COLORS['info'],
                    '数量区域': COLORS['warning'],
                    '发展区域': COLORS['danger']
                }
            )

            # 添加四象限分隔线
            fig.add_shape(
                type="line",
                x0=avg_density,
                x1=avg_density,
                y0=0,
                y1=region_matrix['平均客户价值'].max() * 1.1 if not region_matrix.empty else 0,
                line=dict(color="gray", width=1, dash="dash")
            )

            fig.add_shape(
                type="line",
                x0=0,
                x1=region_matrix['客户密度'].max() * 1.1 if not region_matrix.empty else 0,
                y0=avg_value,
                y1=avg_value,
                line=dict(color="gray", width=1, dash="dash")
            )

            # 添加象限标签
            annotations = [
                dict(
                    x=avg_density * 1.5,
                    y=avg_value * 1.5,
                    text="核心区域",
                    showarrow=False,
                    font=dict(size=12, color=COLORS['success'])
                ),
                dict(
                    x=avg_density * 0.5,
                    y=avg_value * 1.5,
                    text="价值区域",
                    showarrow=False,
                    font=dict(size=12, color=COLORS['info'])
                ),
                dict(
                    x=avg_density * 1.5,
                    y=avg_value * 0.5,
                    text="数量区域",
                    showarrow=False,
                    font=dict(size=12, color=COLORS['warning'])
                ),
                dict(
                    x=avg_density * 0.5,
                    y=avg_value * 0.5,
                    text="发展区域",
                    showarrow=False,
                    font=dict(size=12, color=COLORS['danger'])
                )
            ]

            fig.update_layout(
                annotations=annotations,
                height=500,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="客户密度 (%)",
                yaxis_title="平均客户价值 (元)",
                font={'family': "Arial"}
            )

            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            add_chart_explanation("""
            <b>图表解读：</b> 区域客户价值矩阵将区域按客户密度和平均客户价值分为四类：
            <ul>
                <li><b>核心区域</b> - 客户数量多且价值高，是业务核心区域，需维护优势</li>
                <li><b>价值区域</b> - 客户数量少但价值高，适合精耕细作，提升客户覆盖</li>
                <li><b>数量区域</b> - 客户数量多但价值低，需提升客户价值，加强产品渗透</li>
                <li><b>发展区域</b> - 客户数量少且价值低，需评估发展潜力，针对性培育</li>
            </ul>
            """)

            # 区域客户策略建议
            st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

            # 获取各类型区域
            core_regions = region_matrix[region_matrix['区域类型'] == '核心区域']['所属区域'].tolist()
            value_regions = region_matrix[region_matrix['区域类型'] == '价值区域']['所属区域'].tolist()
            quantity_regions = region_matrix[region_matrix['区域类型'] == '数量区域']['所属区域'].tolist()
            develop_regions = region_matrix[region_matrix['区域类型'] == '发展区域']['所属区域'].tolist()

            st.markdown(f"""
            <h4>🗺️ 区域客户发展策略</h4>
            <p>不同类型区域需要差异化的客户发展策略。</p>
            <p><strong>区域细分策略：</strong></p>
            <ul>
                <li><strong>核心区域</strong> ({', '.join(core_regions) if core_regions else '无'})：
                    <ul>
                        <li>维护核心客户关系，提高客户忠诚度</li>
                        <li>扩大产品覆盖面，提升单客销售额</li>
                        <li>建立区域标杆客户，辐射带动其他客户</li>
                    </ul>
                </li>
                <li><strong>价值区域</strong> ({', '.join(value_regions) if value_regions else '无'})：
                    <ul>
                        <li>扩大客户覆盖，获取更多高价值客户</li>
                        <li>深化现有客户合作，提高渗透率</li>
                        <li>寻找区域扩张的关键突破点</li>
                    </ul>
                </li>
                <li><strong>数量区域</strong> ({', '.join(quantity_regions) if quantity_regions else '无'})：
                    <ul>
                        <li>提升客户价值，增加高价值产品渗透</li>
                        <li>客户分级管理，重点提升高潜客户</li>
                        <li>优化客户结构，减少低效客户</li>
                    </ul>
                </li>
                <li><strong>发展区域</strong> ({', '.join(develop_regions) if develop_regions else '无'})：
                    <ul>
                        <li>评估区域发展潜力，制定针对性拓展计划</li>
                        <li>聚焦关键客户和渠道，建立区域据点</li>
                        <li>适度资源投入，控制发展风险</li>
                    </ul>
                </li>
            </ul>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("当前筛选条件下没有区域客户分析数据。请调整筛选条件。")

    with tabs[3]:  # 客户价值分析
        st.markdown('<div class="sub-header">🔍 客户价值分析</div>', unsafe_allow_html=True)

        # 客户价值分析
        customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

        if not customer_sales.empty:
            # 客户价值分布散点图
            fig = create_customer_scatter(customer_sales, "客户价值与产品多样性分布")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                avg_value = customer_sales['销售额'].mean()
                avg_variety = customer_sales['购买产品种类'].mean()

                add_chart_explanation(f"""
                <b>图表解读：</b> 此图展示了客户销售额与产品多样性的关系。平均客户价值为{format_currency(avg_value)}，平均购买产品种类为{avg_variety:.1f}种。
                客户主要分为四类：右上方的高价值核心客户，右下方的高价值单一客户，左上方的低价值多样客户，左下方的低价值边缘客户。不同类型的客户需要不同的经营策略。
                """)

            # 客户价值分析详情
            st.markdown('<div class="sub-header">📊 客户价值分类详情</div>', unsafe_allow_html=True)

            # 客户价值分类图
            fig = create_customer_pie(customer_sales)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # 客户类型分析
            if '客户类型' in customer_sales.columns:
                # 统计各类客户及销售贡献
                # 修复bug: 使用size()方法而不是自定义列名
                customer_segments = customer_sales.groupby('客户类型').agg({
                    '销售额': 'sum'
                }).reset_index()

                # 添加客户数量列
                customer_count_series = customer_sales.groupby('客户类型').size()
                customer_segments['客户数量'] = customer_segments['客户类型'].map(
                    customer_count_series)

                # 计算百分比
                customer_segments['客户占比'] = customer_segments['客户数量'] / customer_segments[
                    '客户数量'].sum() * 100
                customer_segments['销售额占比'] = customer_segments['销售额'] / customer_segments['销售额'].sum() * 100

                # 创建客户类型卡片
                col1, col2 = st.columns(2)

                # 获取各类型客户数据
                core_data = customer_segments[customer_segments['客户类型'] == '高价值核心客户'] if '高价值核心客户' in \
                                                                                                    customer_segments[
                                                                                                        '客户类型'].values else pd.DataFrame(
                    {'客户数量': [0], '销售额': [0], '客户占比': [0], '销售额占比': [0]})
                single_data = customer_segments[
                    customer_segments['客户类型'] == '高价值单一客户'] if '高价值单一客户' in customer_segments[
                    '客户类型'].values else pd.DataFrame(
                    {'客户数量': [0], '销售额': [0], '客户占比': [0], '销售额占比': [0]})
                diverse_data = customer_segments[
                    customer_segments['客户类型'] == '低价值多样客户'] if '低价值多样客户' in customer_segments[
                    '客户类型'].values else pd.DataFrame(
                    {'客户数量': [0], '销售额': [0], '客户占比': [0], '销售额占比': [0]})
                marginal_data = customer_segments[
                    customer_segments['客户类型'] == '低价值边缘客户'] if '低价值边缘客户' in customer_segments[
                    '客户类型'].values else pd.DataFrame(
                    {'客户数量': [0], '销售额': [0], '客户占比': [0], '销售额占比': [0]})

                # 高价值客户卡片
                with col1:
                    # 高价值核心客户
                    if not core_data.empty:
                        core_count = core_data.iloc[0]['客户数量'] if '客户数量' in core_data.columns else 0
                        core_sales = core_data.iloc[0]['销售额'] if '销售额' in core_data.columns else 0
                        core_count_pct = core_data.iloc[0]['客户占比'] if '客户占比' in core_data.columns else 0
                        core_sales_pct = core_data.iloc[0]['销售额占比'] if '销售额占比' in core_data.columns else 0
                        core_products = customer_sales[customer_sales['客户类型'] == '高价值核心客户'][
                            '购买产品种类'].mean() if '购买产品种类' in customer_sales.columns else 0

                        st.markdown(f"""
                        <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                                    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <h4 style="color: {COLORS['success']};">💎 高价值核心客户</h4>
                            <p><b>客户数量：</b> {format_number(core_count)} ({format_percentage(core_count_pct)})</p>
                            <p><b>销售贡献：</b> {format_currency(core_sales)} ({format_percentage(core_sales_pct)})</p>
                            <p><b>平均购买产品种类：</b> {core_products:.1f}</p>
                            <hr>
                            <h5>策略建议</h5>
                            <ul>
                                <li>建立战略合作关系，成为客户首选供应商</li>
                                <li>提供定制化产品和服务，满足特殊需求</li>
                                <li>分配专属客户经理，提供VIP服务</li>
                                <li>定期高层拜访，加强战略协同</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

                    # 低价值多样客户
                    if not diverse_data.empty:
                        diverse_count = diverse_data.iloc[0]['客户数量'] if '客户数量' in diverse_data.columns else 0
                        diverse_sales = diverse_data.iloc[0]['销售额'] if '销售额' in diverse_data.columns else 0
                        diverse_count_pct = diverse_data.iloc[0][
                            '客户占比'] if '客户占比' in diverse_data.columns else 0
                        diverse_sales_pct = diverse_data.iloc[0][
                            '销售额占比'] if '销售额占比' in diverse_data.columns else 0
                        diverse_products = customer_sales[customer_sales['客户类型'] == '低价值多样客户'][
                            '购买产品种类'].mean() if '购买产品种类' in customer_sales.columns else 0

                        st.markdown(f"""
                        <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid {COLORS['warning']}; 
                                    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <h4 style="color: {COLORS['warning']};">🌱 低价值多样客户</h4>
                            <p><b>客户数量：</b> {format_number(diverse_count)} ({format_percentage(diverse_count_pct)})</p>
                            <p><b>销售贡献：</b> {format_currency(diverse_sales)} ({format_percentage(diverse_sales_pct)})</p>
                            <p><b>平均购买产品种类：</b> {diverse_products:.1f}</p>
                            <hr>
                            <h5>策略建议</h5>
                            <ul>
                                <li>提高单品渗透率，增加客户采购量</li>
                                <li>挖掘客户需求，提供整体解决方案</li>
                                <li>设计数量激励，提高复购频率</li>
                                <li>分析购买行为，找出提升价值点</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    # 高价值单一客户
                    if not single_data.empty:
                        single_count = single_data.iloc[0]['客户数量'] if '客户数量' in single_data.columns else 0
                        single_sales = single_data.iloc[0]['销售额'] if '销售额' in single_data.columns else 0
                        single_count_pct = single_data.iloc[0]['客户占比'] if '客户占比' in single_data.columns else 0
                        single_sales_pct = single_data.iloc[0][
                            '销售额占比'] if '销售额占比' in single_data.columns else 0
                        single_products = customer_sales[customer_sales['客户类型'] == '高价值单一客户'][
                            '购买产品种类'].mean() if '购买产品种类' in customer_sales.columns else 0

                        st.markdown(f"""
                        <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid {COLORS['info']}; 
                                    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <h4 style="color: {COLORS['info']};">💰 高价值单一客户</h4>
                            <p><b>客户数量：</b> {format_number(single_count)} ({format_percentage(single_count_pct)})</p>
                            <p><b>销售贡献：</b> {format_currency(single_sales)} ({format_percentage(single_sales_pct)})</p>
                            <p><b>平均购买产品种类：</b> {single_products:.1f}</p>
                            <hr>
                            <h5>策略建议</h5>
                            <ul>
                                <li>增加品类渗透，扩大产品覆盖</li>
                                <li>交叉销售相关产品，增加客户价值</li>
                                <li>开展产品体验活动，促进新品尝试</li>
                                <li>深入了解客户需求，匹配更多产品</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

                    # 低价值边缘客户
                    if not marginal_data.empty:
                        marginal_count = marginal_data.iloc[0]['客户数量'] if '客户数量' in marginal_data.columns else 0
                        marginal_sales = marginal_data.iloc[0]['销售额'] if '销售额' in marginal_data.columns else 0
                        marginal_count_pct = marginal_data.iloc[0][
                            '客户占比'] if '客户占比' in marginal_data.columns else 0
                        marginal_sales_pct = marginal_data.iloc[0][
                            '销售额占比'] if '销售额占比' in marginal_data.columns else 0
                        marginal_products = customer_sales[customer_sales['客户类型'] == '低价值边缘客户'][
                            '购买产品种类'].mean() if '购买产品种类' in customer_sales.columns else 0

                        st.markdown(f"""
                        <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid {COLORS['danger']}; 
                                    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <h4 style="color: {COLORS['danger']};">⚠️ 低价值边缘客户</h4>
                            <p><b>客户数量：</b> {format_number(marginal_count)} ({format_percentage(marginal_count_pct)})</p>
                            <p><b>销售贡献：</b> {format_currency(marginal_sales)} ({format_percentage(marginal_sales_pct)})</p>
                            <p><b>平均购买产品种类：</b> {marginal_products:.1f}</p>
                            <hr>
                            <h5>策略建议</h5>
                            <ul>
                                <li>评估客户潜力，进行分类管理</li>
                                <li>针对高潜力客户制定发展计划</li>
                                <li>优化服务成本，提高客户效率</li>
                                <li>考虑逐步淘汰长期低价值客户</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

                # 客户价值总结
                st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

                # 计算高价值客户占比
                high_value_customers = customer_sales[
                    customer_sales['客户类型'].isin(['高价值核心客户', '高价值单一客户'])]
                high_value_count = len(high_value_customers)
                high_value_percentage = (high_value_count / len(customer_sales) * 100) if len(customer_sales) > 0 else 0
                high_value_sales = high_value_customers['销售额'].sum()
                high_value_sales_percentage = (high_value_sales / customer_sales['销售额'].sum() * 100) if \
                customer_sales['销售额'].sum() > 0 else 0

                st.markdown(f"""
                <h4>📊 客户价值构成分析</h4>
                <p>高价值客户（{format_number(high_value_count)}个，占比{format_percentage(high_value_percentage)}）贡献了{format_percentage(high_value_sales_percentage)}的销售额。</p>
                <p><strong>客户策略建议：</strong></p>
                <ul>
                    <li><strong>差异化服务策略：</strong> 根据客户价值分级，提供差异化服务</li>
                    <li><strong>高价值客户维护：</strong> 重点资源配置给高价值客户，提高忠诚度</li>
                    <li><strong>产品渗透提升：</strong> 针对单一产品客户，增加品类渗透</li>
                    <li><strong>客户价值提升：</strong> 对低价值客户进行筛选，重点培育高潜力客户</li>
                    <li><strong>建立价值评估体系：</strong> 定期评估客户价值和潜力，动态调整客户策略</li>
                </ul>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("客户价值分类数据不完整，无法显示详细分析。")
        else:
            st.info("当前筛选条件下没有客户价值分析数据。请调整筛选条件。")

    # 客户洞察总结
    st.markdown('<div class="sub-header">💡 客户洞察总结</div>', unsafe_allow_html=True)

    # 综合评估
    if top5_concentration > 70:
        customer_structure = "存在较高客户集中风险"
        structure_color = COLORS['danger']
        structure_advice = "急需开发新客户，降低对大客户的依赖"
    elif top5_concentration > 50:
        customer_structure = "客户集中度中等"
        structure_color = COLORS['warning']
        structure_advice = "需要关注客户结构优化，加强中小客户开发"
    else:
        customer_structure = "客户结构健康"
        structure_color = COLORS['success']
        structure_advice = "保持现有客户开发策略，继续维护客户结构健康"

    # 区域分布评估
    region_stats = customer_analysis.get('region_stats', pd.DataFrame())
    if not region_stats.empty and '客户数量' in region_stats.columns and len(region_stats) > 1:
        # 检查区域分布均衡度
        customer_std = region_stats['客户数量'].std()
        customer_mean = region_stats['客户数量'].mean()
        is_balanced = (customer_std / customer_mean < 0.3) if customer_mean > 0 else False
        region_distribution = "区域客户分布均衡，市场覆盖全面" if is_balanced else "区域客户分布不均衡，需关注薄弱区域发展"
    else:
        region_distribution = "无法评估区域客户分布"

    # 客户价值分布评估
    customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())
    if not customer_sales.empty and '销售额' in customer_sales.columns:
        # 检查客户价值分布均衡度
        sales_std = customer_sales['销售额'].std()
        sales_mean = customer_sales['销售额'].mean()
        value_is_balanced = (sales_std / sales_mean < 1) if sales_mean > 0 else False
        value_distribution = "客户价值分布相对均衡，整体质量良好" if value_is_balanced else "客户价值分布差异大，需分级管理"
    else:
        value_distribution = "无法评估客户价值分布"

    st.markdown(f"""
    <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0.5rem;">
        <h4>📋 客户分析总结</h4>
        <p><strong>客户基础：</strong>当前共有{format_number(total_customers)}个活跃客户，平均客户价值{format_currency(avg_customer_value)}。</p>
        <p><strong>客户结构：</strong><span style="color: {structure_color};">{customer_structure}</span>，TOP5客户集中度{format_percentage(top5_concentration)}。</p>
        <p><strong>区域分布：</strong>{region_distribution}。</p>
        <p><strong>客户价值：</strong>{value_distribution}。</p>
        <p><strong>发展建议：</strong>{structure_advice}；完善客户分级管理体系；针对不同价值客户制定差异化策略；加强客户关系管理，提高客户忠诚度。</p>
    </div>
    """, unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)