import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import re
import warnings

warnings.filterwarnings('ignore')

# 自定义CSS样式 - 与sales_dashboard.py保持一致
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #444444;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f3867;
    }
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0.5rem 2rem 0 rgba(58, 59, 69, 0.2);
    }
    .card-text {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
    }
    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
    }
    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f3867;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 0.9rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border-left: 0.5rem solid #4CAF50;
    }
    .flip-card-container {
        width: 100%;
        height: auto;
        perspective: 1000px;
        margin-bottom: 20px;
    }
    .flip-card {
        position: relative;
        width: 100%;
        height: 100%;
        cursor: pointer;
    }
    .flip-card-front, .flip-card-back, .flip-card-deep {
        position: relative;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        transition: transform 0.6s ease;
    }
    .back-button {
        background-color: #f0f0f0;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .back-button:hover {
        background-color: #e0e0e0;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f3867;
        padding: 10px;
        margin-top: 15px;
        border-radius: 0 4px 4px 0;
    }
    .insight-title {
        font-weight: 600;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 颜色配置
COLORS = {
    "primary": "#1f3867",  # 主要颜色
    "secondary": "#484848",  # 次要颜色
    "background": "#F7F7F7",  # 背景色
    "text": "#484848",  # 文本颜色
    "accent1": "#FFB400",  # 强调色1
    "accent2": "#00A699",  # 强调色2
    "accent3": "#FF385C",  # 强调色3
    "accent4": "#007A87",  # 强调色4
    "grey_light": "#DDDDDD",  # 浅灰色
}

CHART_COLORS = [
    COLORS["primary"],
    COLORS["accent1"],
    COLORS["accent2"],
    COLORS["accent3"],
    COLORS["accent4"],
]

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 对于翻卡交互，我们需要以下状态变量
if 'card_states' not in st.session_state:
    st.session_state.card_states = {
        'sales': 'front',
        'penetration': 'front',
        'ranking': 'front'
    }


# 格式化数值的函数
def format_yuan(value):
    """格式化金额显示"""
    if value >= 100000000:  # 亿元级别
        return f"{value / 100000000:.2f}亿元"
    elif value >= 10000:  # 万元级别
        return f"{value / 10000:.2f}万元"
    else:
        return f"{value:.2f}元"


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 1. 数据加载函数
@st.cache_data
def load_raw_data():
    """加载原始销售数据"""
    try:
        df = pd.read_excel("仪表盘原始数据.xlsx")
        return df
    except Exception as e:
        st.error(f"加载仪表盘原始数据失败: {e}")
        return pd.DataFrame()


@st.cache_data
def load_new_products():
    """加载新品代码列表"""
    try:
        with open("仪表盘新品代码.txt", "r") as file:
            new_products = [line.strip() for line in file.readlines() if line.strip()]
        return new_products
    except Exception as e:
        st.error(f"加载新品代码列表失败: {e}")
        return []


@st.cache_data
def load_promotion_data():
    """加载促销活动数据"""
    try:
        df = pd.read_excel("仪表盘促销活动.xlsx")
        return df
    except Exception as e:
        st.error(f"加载促销活动数据失败: {e}")
        return pd.DataFrame()


@st.cache_data
def load_customer_sales_relation():
    """加载人与客户关系表"""
    try:
        df = pd.read_excel("仪表盘人与客户关系表.xlsx")
        # 只保留状态为"正常"的客户
        df = df[df["状态"] == "正常"]
        return df
    except Exception as e:
        st.error(f"加载人与客户关系表失败: {e}")
        return pd.DataFrame()


def prepare_new_product_data():
    """准备新品分析数据"""
    raw_data = load_raw_data()
    new_products = load_new_products()
    promotion_data = load_promotion_data()
    customer_relation = load_customer_sales_relation()

    if raw_data.empty or not new_products:
        st.warning("没有找到新品数据或销售数据")
        return pd.DataFrame(), pd.DataFrame(), []

    # 筛选新品销售数据
    # 只保留订单类型为'订单-TT产品'或'订单-正常产品'的记录
    sales_data = raw_data[raw_data["订单类型"].isin(["订单-TT产品", "订单-正常产品"])]

    # 处理销售额列名差异（根据原始数据中的列名）
    if "求和项:金额（元）" in sales_data.columns and "销售额" not in sales_data.columns:
        sales_data["销售额"] = sales_data["求和项:金额（元）"]

    # 筛选新品数据
    new_product_sales = sales_data[sales_data["产品代码"].isin(new_products)]

    # 筛选新品促销数据
    new_product_promotion = promotion_data[promotion_data["产品代码"].isin(new_products)]

    # 有效客户列表
    valid_customers = customer_relation["客户"].unique().tolist()

    return new_product_sales, new_product_promotion, valid_customers


# 2. 数据分析函数
def analyze_new_product_performance(new_product_data, all_sales_data):
    """分析新品表现"""
    if new_product_data.empty or all_sales_data.empty:
        return {
            "total_sales": 0,
            "total_volume": 0,
            "avg_price": 0,
            "customer_count": 0,
            "sales_percentage": 0,
            "region_sales": pd.DataFrame(),
            "monthly_trend": pd.DataFrame(),
            "product_ranking": pd.DataFrame(),
        }

    # 确保销售额列存在
    sales_column = "销售额" if "销售额" in new_product_data.columns else "求和项:金额（元）"
    quantity_column = "数量（箱）" if "数量（箱）" in new_product_data.columns else "求和项:数量（箱）"

    # 新品总销售额
    total_sales = new_product_data[sales_column].sum()

    # 全部销售额
    all_sales = all_sales_data[sales_column].sum()

    # 新品销售占比
    sales_percentage = (total_sales / all_sales * 100) if all_sales > 0 else 0

    # 新品总销量
    total_volume = new_product_data[quantity_column].sum()

    # 平均单价
    avg_price = total_sales / total_volume if total_volume > 0 else 0

    # 客户覆盖数
    customer_count = new_product_data["客户简称"].nunique()

    # 区域销售分布
    region_sales = new_product_data.groupby("所属区域")[sales_column].sum().reset_index()
    region_sales = region_sales.sort_values(sales_column, ascending=False)

    # 月度销售趋势
    new_product_data["发运月份"] = pd.to_datetime(new_product_data["发运月份"], format="%Y-%m")
    monthly_trend = new_product_data.groupby("发运月份")[sales_column].sum().reset_index()
    monthly_trend = monthly_trend.sort_values("发运月份")

    # 产品排名
    product_ranking = new_product_data.groupby(["产品代码", "产品简称"])[sales_column].sum().reset_index()
    product_ranking = product_ranking.sort_values(sales_column, ascending=False)

    return {
        "total_sales": total_sales,
        "total_volume": total_volume,
        "avg_price": avg_price,
        "customer_count": customer_count,
        "sales_percentage": sales_percentage,
        "region_sales": region_sales,
        "monthly_trend": monthly_trend,
        "product_ranking": product_ranking,
    }


def analyze_promotion_impact(promotion_data, sales_data):
    """分析促销活动对新品销售的影响"""
    if promotion_data.empty or sales_data.empty:
        return {
            "promotion_count": 0,
            "promotion_sales_forecast": 0,
            "promotion_products": [],
        }

    # 促销活动数量
    promotion_count = promotion_data["流程编号："].nunique()

    # 促销销售预测
    promotion_sales_forecast = promotion_data["预计销售额（元）"].sum()

    # 促销产品列表
    promotion_products = promotion_data["产品代码"].unique().tolist()

    return {
        "promotion_count": promotion_count,
        "promotion_sales_forecast": promotion_sales_forecast,
        "promotion_products": promotion_products,
    }


def calculate_penetration_rate(new_product_data, all_customers):
    """计算新品渗透率"""
    if new_product_data.empty or not all_customers:
        return {
            "total_customers": 0,
            "new_product_customers": 0,
            "penetration_rate": 0,
            "region_penetration": pd.DataFrame()
        }

    # 购买新品的客户
    new_product_customers = new_product_data["客户简称"].unique()

    # 新品客户数量
    new_product_customer_count = len(new_product_customers)

    # 总客户数量
    total_customer_count = len(all_customers)

    # 渗透率
    penetration_rate = (new_product_customer_count / total_customer_count * 100) if total_customer_count > 0 else 0

    # 按区域计算渗透率
    region_customers = new_product_data.groupby("所属区域")["客户简称"].nunique().reset_index()
    region_customers.columns = ["所属区域", "新品客户数"]

    return {
        "total_customers": total_customer_count,
        "new_product_customers": new_product_customer_count,
        "penetration_rate": penetration_rate,
        "region_penetration": region_customers
    }


# 3. 图表函数
def create_monthly_trend_chart(monthly_data, title="新品月度销售趋势"):
    """创建月度趋势图表"""
    if monthly_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="月份",
            yaxis_title="销售额（元）",
            height=400,
        )
        return fig

    # 确定销售额列名
    sales_column = "销售额" if "销售额" in monthly_data.columns else "求和项:金额（元）"

    fig = px.line(
        monthly_data,
        x="发运月份",
        y=sales_column,
        markers=True,
        title=title,
    )

    fig.update_layout(
        xaxis_title="月份",
        yaxis_title="销售额（元）",
        height=400,
        plot_bgcolor="white",
        font=dict(size=12),
    )

    fig.update_traces(
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=8, color=COLORS["primary"]),
    )

    return fig


def create_region_distribution_chart(region_data, title="新品区域销售分布"):
    """创建区域分布图表"""
    if region_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="区域",
            yaxis_title="销售额（元）",
            height=400,
        )
        return fig

    # 确定销售额列名
    sales_column = "销售额" if "销售额" in region_data.columns else "求和项:金额（元）"

    fig = px.bar(
        region_data,
        x="所属区域",
        y=sales_column,
        title=title,
        color_discrete_sequence=[COLORS["primary"]],
    )

    fig.update_layout(
        xaxis_title="区域",
        yaxis_title="销售额（元）",
        height=400,
        plot_bgcolor="white",
        font=dict(size=12),
    )

    return fig


def create_product_ranking_chart(product_data, title="新品销售排名"):
    """创建产品排名图表"""
    if product_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="产品",
            yaxis_title="销售额（元）",
            height=400,
        )
        return fig

    # 确定销售额列名
    sales_column = "销售额" if "销售额" in product_data.columns else "求和项:金额（元）"

    # 只显示前10名产品
    top_products = product_data.head(10).copy()

    fig = px.bar(
        top_products,
        x="产品简称",
        y=sales_column,
        title=title,
        color_discrete_sequence=[COLORS["accent1"]],
    )

    fig.update_layout(
        xaxis_title="产品",
        yaxis_title="销售额（元）",
        height=400,
        plot_bgcolor="white",
        font=dict(size=12),
    )

    return fig


def create_sales_percentage_chart(new_sales, total_sales, title="新品销售占比"):
    """创建新品销售占比图表"""
    labels = ["新品", "非新品"]
    values = [new_sales, total_sales - new_sales]

    fig = px.pie(
        values=values,
        names=labels,
        title=title,
        color_discrete_sequence=[COLORS["primary"], COLORS["accent1"]],
    )

    fig.update_traces(
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        textfont_size=14,
    )

    fig.update_layout(
        height=400,
        font=dict(size=12),
    )

    return fig


def create_penetration_gauge(penetration_rate, title="新品市场渗透率"):
    """创建渗透率仪表盘图表"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=penetration_rate,
        title={"text": title, "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": COLORS["accent2"]},
            "steps": [
                {"range": [0, 30], "color": "#FF9999"},
                {"range": [30, 70], "color": "#FFCC99"},
                {"range": [70, 100], "color": "#99CC99"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 50
            }
        },
        number={"suffix": "%", "font": {"size": 24}},
    ))

    fig.update_layout(
        height=300,
        font=dict(size=12),
    )

    return fig


def create_region_penetration_chart(region_data, title="各区域新品渗透率"):
    """创建区域渗透率图表"""
    if region_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="区域",
            yaxis_title="新品客户数",
            height=400,
        )
        return fig

    fig = px.bar(
        region_data,
        x="所属区域",
        y="新品客户数",
        title=title,
        color_discrete_sequence=[COLORS["accent2"]],
    )

    fig.update_layout(
        xaxis_title="区域",
        yaxis_title="新品客户数",
        height=400,
        plot_bgcolor="white",
        font=dict(size=12),
    )

    return fig


# 4. 翻卡组件
def create_flip_card(id, title, value, level2_content, level3_content):
    """创建三层翻卡交互组件"""
    # 使用会话状态跟踪卡片状态
    if id not in st.session_state.card_states:
        st.session_state.card_states[id] = "front"

    container = st.container()

    with container:
        if st.session_state.card_states[id] == "front":
            # 显示第一层（指标卡片）
            front_card = st.container()
            with front_card:
                st.markdown(f"""
                <div class="metric-card" id="card_{id}_front">
                    <p class="card-header">{title}</p>
                    <p class="card-value">{value}</p>
                    <p class="card-text">点击查看详情</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"查看分析", key=f"btn_{id}_to_second"):
                    st.session_state.card_states[id] = "second"
                    st.rerun()

        elif st.session_state.card_states[id] == "second":
            # 显示第二层（图表分析）
            second_card = st.container()
            with second_card:
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("返回", key=f"btn_{id}_to_front"):
                        st.session_state.card_states[id] = "front"
                        st.rerun()
                with col2:
                    st.markdown(f"""<p class="card-header">{title} - 详细分析</p>""", unsafe_allow_html=True)

                st.markdown(level2_content, unsafe_allow_html=True)

                if st.button("深入分析", key=f"btn_{id}_to_third"):
                    st.session_state.card_states[id] = "third"
                    st.rerun()

        elif st.session_state.card_states[id] == "third":
            # 显示第三层（深度分析）
            third_card = st.container()
            with third_card:
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("返回", key=f"btn_{id}_to_second"):
                        st.session_state.card_states[id] = "second"
                        st.rerun()
                with col2:
                    st.markdown(f"""<p class="card-header">{title} - 深度分析</p>""", unsafe_allow_html=True)

                st.markdown(level3_content, unsafe_allow_html=True)


# 5. 主页面函数
def show():
    """显示新品分析页面"""
    st.title("新品销售分析")

    # 认证检查
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # 显示密码输入区域
        password_container = st.empty()
        st.markdown(
            '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">2025新品销售数据分析 | 登录</div>',
            unsafe_allow_html=True)

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
            login_button = st.button("登录")

            # 验证密码
            if login_button:
                if password == 'SAL!2025':  # 注意这里密码是SAL!2025
                    st.session_state.authenticated = True
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("密码错误，请重试！")

        # 如果未认证，停止执行后续代码
        if not st.session_state.authenticated:
            return

    # 加载数据
    with st.spinner("正在加载新品数据..."):
        new_product_sales, new_product_promotion, valid_customers = prepare_new_product_data()
        all_sales_data = load_raw_data()

    # 确保数据加载成功
    if new_product_sales.empty:
        st.warning("没有找到新品销售数据，请检查数据文件。")
        return

    # 计算主要指标
    performance_metrics = analyze_new_product_performance(new_product_sales, all_sales_data)
    promotion_metrics = analyze_promotion_impact(new_product_promotion, new_product_sales)
    penetration_metrics = calculate_penetration_rate(new_product_sales, valid_customers)

    # 销售额数据列名
    sales_column = "销售额" if "销售额" in new_product_sales.columns else "求和项:金额（元）"

    # 显示数据时间范围
    try:
        date_range = f"数据范围: {new_product_sales['发运月份'].min().strftime('%Y-%m')} 至 {new_product_sales['发运月份'].max().strftime('%Y-%m')}"
        st.markdown(f"<p style='color:gray; font-size:14px;'>{date_range}</p>", unsafe_allow_html=True)
    except:
        pass

    # 创建KPI卡片及图表
    col1, col2, col3 = st.columns(3)

    # 准备销售趋势图
    trend_chart = create_monthly_trend_chart(performance_metrics["monthly_trend"])
    trend_chart_html = trend_chart.to_html(full_html=False, include_plotlyjs='cdn')

    # 销售趋势洞察
    trend_insight = """
    <div class="insight-box">
        <div class="insight-title">洞察:</div>
        <p>新品销售呈现逐月增长趋势，建议关注季节性波动并及时调整营销策略。销售高峰期可能与促销活动和市场推广力度相关。</p>
    </div>
    """
    trend_level2 = f"{trend_chart_html}{trend_insight}"

    # 销售深度分析
    sales_deep_analysis = f"""
    <h4>新品销售表现深度分析</h4>
    <p>总销售额: <strong>¥{performance_metrics['total_sales']:,.2f}</strong></p>
    <p>销售占比: <strong>{performance_metrics['sales_percentage']:.2f}%</strong></p>
    <p>平均单价: <strong>¥{performance_metrics['avg_price']:,.2f}</strong></p>

    <div class="insight-box">
        <div class="insight-title">销售策略建议:</div>
        <ul>
            <li>根据月度销售趋势，建议在销售高峰期前1-2个月增加促销力度</li>
            <li>关注单价变化趋势，避免过度降价促销影响品牌形象</li>
            <li>针对表现优秀的新品，考虑扩大产品线或开发衍生产品</li>
            <li>对于增长速度放缓的新品，研究竞品情况并调整营销策略</li>
        </ul>
    </div>

    <div class="insight-box">
        <div class="insight-title">关键行动计划:</div>
        <ol>
            <li>每月定期回顾新品销售表现，及时调整促销和生产计划</li>
            <li>建立新品销售预警机制，对于表现不达预期的产品快速响应</li>
            <li>发现表现突出的新品后及时增加库存和营销资源投入</li>
        </ol>
    </div>
    """

    # 渗透率图表
    penetration_gauge = create_penetration_gauge(penetration_metrics["penetration_rate"])
    penetration_gauge_html = penetration_gauge.to_html(full_html=False, include_plotlyjs='cdn')

    # 区域渗透图表
    region_penetration_chart = create_region_penetration_chart(penetration_metrics["region_penetration"])
    region_penetration_html = region_penetration_chart.to_html(full_html=False, include_plotlyjs='cdn')

    # 渗透率洞察
    penetration_insight = f"""
    <div class="insight-box">
        <div class="insight-title">洞察:</div>
        <p>当前新品渗透率为{penetration_metrics['penetration_rate']:.2f}%，在{penetration_metrics['total_customers']}个有效客户中，有{penetration_metrics['new_product_customers']}个客户购买了新品。</p>
        <p>不同区域渗透率存在显著差异，这可能与区域市场成熟度、销售团队执行力和客户结构有关。</p>
    </div>
    """
    penetration_level2 = f"{penetration_gauge_html}{region_penetration_html}{penetration_insight}"

    # 渗透率深度分析
    penetration_deep_analysis = f"""
    <h4>新品市场渗透深度分析</h4>
    <p>总客户数: <strong>{penetration_metrics['total_customers']}</strong></p>
    <p>购买新品客户数: <strong>{penetration_metrics['new_product_customers']}</strong></p>
    <p>市场渗透率: <strong>{penetration_metrics['penetration_rate']:.2f}%</strong></p>

    <div class="insight-box">
        <div class="insight-title">渗透策略建议:</div>
        <ul>
            <li>针对尚未尝试新品的客户，开发专门的首单优惠方案</li>
            <li>对已购买新品的客户，提供回购奖励增强忠诚度</li>
            <li>针对渗透率低的区域，加强销售团队培训和资源投入</li>
            <li>将客户按渗透状态分组，制定差异化的营销策略</li>
        </ul>
    </div>

    <div class="insight-box">
        <div class="insight-title">渗透目标计划:</div>
        <ol>
            <li>短期目标：在3个月内将渗透率提升至{min(100, penetration_metrics['penetration_rate'] * 1.2):.2f}%</li>
            <li>中期目标：在6个月内实现区域间渗透率差异减少50%</li>
            <li>长期目标：建立稳定的新品推广渠道和流程，确保新品快速进入市场</li>
        </ol>
    </div>
    """

    # 产品排名图表
    product_chart = create_product_ranking_chart(performance_metrics["product_ranking"])
    product_chart_html = product_chart.to_html(full_html=False, include_plotlyjs='cdn')

    # 产品排名洞察
    product_insight = """
    <div class="insight-box">
        <div class="insight-title">洞察:</div>
        <p>新品表现存在明显差异，头部产品贡献了主要销售额。了解表现最好的新品成功因素，可以为后续新品开发和推广提供经验。</p>
    </div>
    """
    product_level2 = f"{product_chart_html}{product_insight}"

    # 产品深度分析
    product_deep_analysis = """
    <h4>新品产品组合深度分析</h4>

    <div class="insight-box">
        <div class="insight-title">产品表现分层:</div>
        <p><strong>明星新品:</strong> 销售表现突出，已成为重要收入来源的新品</p>
        <p><strong>潜力新品:</strong> 增长速度快但基数较小，需要加大推广力度的新品</p>
        <p><strong>问题新品:</strong> 表现不及预期，需要调整策略或重新定位的新品</p>
    </div>

    <div class="insight-box">
        <div class="insight-title">产品策略建议:</div>
        <ul>
            <li>明星新品：确保供应稳定，扩大渠道覆盖，考虑开发衍生产品</li>
            <li>潜力新品：增加营销投入，提高市场曝光，优化定价策略</li>
            <li>问题新品：深入分析原因（定价、包装、口味等），调整或淘汰</li>
        </ul>
    </div>

    <div class="insight-box">
        <div class="insight-title">产品组合优化:</div>
        <p>根据BCG矩阵模型，新品应逐步向"明星"和"现金牛"方向发展。建议定期评估新品生命周期阶段，及时调整资源分配。</p>
    </div>
    """

    # 卡片1：销售额
    with col1:
        create_flip_card(
            "sales",
            "新品销售额",
            format_yuan(performance_metrics["total_sales"]),
            trend_level2,
            sales_deep_analysis
        )

    # 卡片2：市场渗透率
    with col2:
        create_flip_card(
            "penetration",
            "新品市场渗透率",
            f"{penetration_metrics['penetration_rate']:.2f}%",
            penetration_level2,
            penetration_deep_analysis
        )

    # 卡片3：产品表现
    with col3:
        create_flip_card(
            "ranking",
            "新品数量",
            f"{len(performance_metrics['product_ranking'])}个",
            product_level2,
            product_deep_analysis
        )

    # 第二行：销售占比分析
    st.markdown('<div class="sub-header">新品销售占比分析</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 占比饼图
        percentage_chart = create_sales_percentage_chart(
            performance_metrics["total_sales"],
            all_sales_data[sales_column].sum()
        )
        st.plotly_chart(percentage_chart, use_container_width=True)

        # 图表解读
        add_chart_explanation(f"""
        <b>图表解读：</b> 此饼图显示了新品销售额在总销售额中的占比。当前新品占比为<b>{performance_metrics['sales_percentage']:.2f}%</b>，
        反映了新品对整体业务的贡献程度。理想的新品占比应根据公司战略和产品生命周期管理策略确定，通常在15-30%之间是合理的范围。
        """)

    with col2:
        # 区域新品分布
        region_chart = create_region_distribution_chart(performance_metrics["region_sales"])
        st.plotly_chart(region_chart, use_container_width=True)

        # 图表解读
        add_chart_explanation("""
        <b>图表解读：</b> 此柱状图展示了新品在不同区域的销售分布。区域间的差异可能反映了市场接受度、渠道覆盖或销售团队执行力的差异。
        表现最好的区域可能有成功经验值得推广，而表现较弱的区域则需要额外支持或资源投入。
        """)

    # 第三行：趋势和表现分析
    st.markdown('<div class="sub-header">新品趋势与表现分析</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 月度趋势图
        st.plotly_chart(trend_chart, use_container_width=True)

        # 图表解读
        add_chart_explanation("""
        <b>图表解读：</b> 此折线图展示了新品销售额的月度变化趋势。通过观察趋势变化，可以识别销售旺季和淡季，评估营销活动效果，
        并为库存管理提供依据。持续上升的趋势表明市场接受度良好，而下降趋势则可能需要调整策略或产品改进。
        """)

    with col2:
        # 产品排名图
        st.plotly_chart(product_chart, use_container_width=True)

        # 图表解读
        add_chart_explanation("""
        <b>图表解读：</b> 此柱状图展示了销售额排名前10的新品。销售集中度是评估新品组合健康度的重要指标。
        过高的集中度（如前3名贡献超过80%销售额）表明对少数产品依赖过重，应考虑拓宽新品组合；而过低的集中度则可能意味着缺乏明星产品牵引。
        """)

    # 促销分析区域
    st.markdown('<div class="sub-header">新品促销活动分析</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 促销活动指标
        promotion_metrics_display = {
            "促销活动数量": f"{promotion_metrics['promotion_count']}个",
            "促销预测销售额": f"¥{promotion_metrics['promotion_sales_forecast']:,.2f}",
            "促销产品种类": f"{len(promotion_metrics['promotion_products'])}种",
        }

        for metric, value in promotion_metrics_display.items():
            st.metric(metric, value)

        # 促销解读
        add_chart_explanation("""
        <b>促销活动分析：</b> 促销活动是新品市场导入的重要手段。通过分析促销活动数量、预计销售额和实际效果，
        可以评估不同促销策略的ROI，优化资源分配，并为后续促销决策提供依据。建议关注促销覆盖率（促销新品占比）和促销效率（销售提升倍数）。
        """)

    with col2:
        # 促销产品列表
        if promotion_metrics["promotion_products"]:
            promotion_product_data = new_product_promotion.drop_duplicates(subset=["产品代码"])
            st.markdown("### 促销新品列表")

            # 创建表格
            product_table = pd.DataFrame({
                "产品代码": promotion_product_data["产品代码"],
                "产品名称": promotion_product_data["促销产品名称"],
                "预计销售额": promotion_product_data["预计销售额（元）"].apply(lambda x: f"¥{x:,.2f}")
            })

            st.dataframe(product_table, use_container_width=True)
        else:
            st.info("暂无促销新品数据")

    # 页面说明
    with st.expander("页面说明"):
        st.markdown("""
        ### 新品分析页面说明

        本页面提供新品销售表现的全面分析，帮助业务人员了解新品市场表现，并为新品推广和销售策略提供数据支持。

        **主要指标说明**:
        - **新品销售额**: 新品产生的总销售额
        - **新品市场渗透率**: 购买新品的客户占总客户的比例
        - **新品数量**: 当前正在销售的新品数量

        **如何使用**:
        1. 点击指标卡片查看详细分析图表
        2. 点击"深入分析"按钮获取更多洞察和建议
        3. 查看各区域图表了解区域间差异

        **数据更新**: 数据每周一17:00更新。
        """)

    # 页脚
    st.markdown("""
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
        <p>新品销售分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
        <p>使用Streamlit和Plotly构建 | 数据更新频率: 每周</p>
    </div>
    """, unsafe_allow_html=True)


# 主函数
if __name__ == "__main__":
    # 不再使用set_page_config，改为使用config中的setup_page()函数
    # 显示页面
    show()