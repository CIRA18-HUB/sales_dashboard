# pages/customer_page.py - 完全自包含的客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# 导入统一配置
from config import (
    COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, load_data_files, create_filters, add_chart_explanation,
    create_flip_card, setup_page, get_safe_column, sanitize_data
)

# 定义页面名称 - 确保筛选器状态独立
PAGE_NAME = "customer_page"

# ==================== 页面配置 ====================
# 设置页面配置
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 使用与sales_dashboard.py相同的样式
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

    /* 筛选器样式优化 */
    .sidebar .sidebar-content {
        background-color: #f8f9fc;
    }

    .sidebar .sidebar-content .block-container {
        padding-top: 2rem;
    }

    /* 按钮样式美化 */
    .stButton > button {
        background-color: #1f3867;
        color: white;
        font-weight: 500;
        border-radius: 0.3rem;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: #2c4f99;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* 选择框美化 */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 0.3rem;
        border: 1px solid #ddd;
    }

    /* 标签页美化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0 1rem;
        background-color: #f8f9fc;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f3867;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 检查认证
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">销售数据分析仪表盘 | 登录</div>', unsafe_allow_html=True)

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
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()

# 页面标题
st.markdown('<h1 class="main-header">👥 客户分析</h1>', unsafe_allow_html=True)

# 加载数据
with st.spinner("正在加载数据..."):
    try:
        data = load_data_files()
        if not data:
            st.error("无法加载数据文件，请检查文件路径")
            st.stop()
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        st.stop()

# ==================== 侧边栏筛选器 ====================
st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem; border-bottom: 1px solid #eee;">
        <h3 style="color: #1f3867; margin-bottom: 0.5rem;">🔍 数据筛选</h3>
        <p style="color: #666; font-size: 0.9rem;">选择区域、销售员或客户进行数据筛选</p>
    </div>
""", unsafe_allow_html=True)

# 初始化筛选器状态
if f"{PAGE_NAME}_region" not in st.session_state:
    st.session_state[f"{PAGE_NAME}_region"] = "全部"
if f"{PAGE_NAME}_salesperson" not in st.session_state:
    st.session_state[f"{PAGE_NAME}_salesperson"] = "全部"
if f"{PAGE_NAME}_customer" not in st.session_state:
    st.session_state[f"{PAGE_NAME}_customer"] = "全部"
if f"{PAGE_NAME}_date_range" not in st.session_state:
    current_year = datetime.now().year
    st.session_state[f"{PAGE_NAME}_date_range"] = (
        datetime(current_year, 1, 1),
        datetime(current_year, 12, 31)
    )

# 从数据中提取筛选选项
sales_data = data.get('sales_orders', pd.DataFrame())

# 区域筛选器
if '所属区域' in sales_data.columns:
    all_regions = sorted(['全部'] + list(sales_data['所属区域'].unique()))
    selected_region = st.sidebar.selectbox(
        "选择区域",
        all_regions,
        index=0,
        key=f"{PAGE_NAME}_sidebar_region"
    )
    st.session_state[f"{PAGE_NAME}_region"] = selected_region

# 销售员筛选器
if '申请人' in sales_data.columns:
    all_salespersons = sorted(['全部'] + list(sales_data['申请人'].unique()))
    selected_salesperson = st.sidebar.selectbox(
        "选择销售员",
        all_salespersons,
        index=0,
        key=f"{PAGE_NAME}_sidebar_salesperson"
    )
    st.session_state[f"{PAGE_NAME}_salesperson"] = selected_salesperson

# 客户筛选器
customer_col = None
for col in ['客户简称', '经销商名称', '客户']:
    if col in sales_data.columns:
        customer_col = col
        break

if customer_col:
    all_customers = sorted(['全部'] + list(sales_data[customer_col].unique()))
    selected_customer = st.sidebar.selectbox(
        "选择客户",
        all_customers,
        index=0,
        key=f"{PAGE_NAME}_sidebar_customer"
    )
    st.session_state[f"{PAGE_NAME}_customer"] = selected_customer

# 日期范围筛选器
if '发运月份' in sales_data.columns:
    try:
        sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])
        min_date = sales_data['发运月份'].min().date()
        max_date = sales_data['发运月份'].max().date()

        st.sidebar.markdown("### 日期范围")
        start_date = st.sidebar.date_input(
            "开始日期",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{PAGE_NAME}_sidebar_start_date"
        )
        end_date = st.sidebar.date_input(
            "结束日期",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{PAGE_NAME}_sidebar_end_date"
        )

        if end_date < start_date:
            end_date = start_date
            st.sidebar.warning("结束日期不能早于开始日期，已自动调整。")

        st.session_state[f"{PAGE_NAME}_date_range"] = (start_date, end_date)
    except Exception as e:
        st.sidebar.warning(f"日期筛选器初始化失败: {e}")

# 重置筛选按钮
if st.sidebar.button("重置筛选条件", key=f"{PAGE_NAME}_reset_filters"):
    st.session_state[f"{PAGE_NAME}_region"] = "全部"
    st.session_state[f"{PAGE_NAME}_salesperson"] = "全部"
    st.session_state[f"{PAGE_NAME}_customer"] = "全部"
    current_year = datetime.now().year
    st.session_state[f"{PAGE_NAME}_date_range"] = (
        datetime(current_year, 1, 1),
        datetime(current_year, 12, 31)
    )
    st.rerun()

# 应用筛选条件
filtered_data = data.copy()
filtered_sales_data = sales_data.copy()

# 应用区域筛选
if st.session_state[f"{PAGE_NAME}_region"] != "全部" and '所属区域' in filtered_sales_data.columns:
    filtered_sales_data = filtered_sales_data[filtered_sales_data['所属区域'] == st.session_state[f"{PAGE_NAME}_region"]]

# 应用销售员筛选
if st.session_state[f"{PAGE_NAME}_salesperson"] != "全部" and '申请人' in filtered_sales_data.columns:
    filtered_sales_data = filtered_sales_data[filtered_sales_data['申请人'] == st.session_state[f"{PAGE_NAME}_salesperson"]]

# 应用客户筛选
if st.session_state[f"{PAGE_NAME}_customer"] != "全部" and customer_col and customer_col in filtered_sales_data.columns:
    filtered_sales_data = filtered_sales_data[filtered_sales_data[customer_col] == st.session_state[f"{PAGE_NAME}_customer"]]

# 应用日期筛选
if '发运月份' in filtered_sales_data.columns:
    try:
        start_date, end_date = st.session_state[f"{PAGE_NAME}_date_range"]
        filtered_sales_data['发运月份'] = pd.to_datetime(filtered_sales_data['发运月份'])
        filtered_sales_data = filtered_sales_data[
            (filtered_sales_data['发运月份'] >= pd.Timestamp(start_date)) &
            (filtered_sales_data['发运月份'] <= pd.Timestamp(end_date))
            ]
    except Exception as e:
        st.warning(f"应用日期筛选时出错: {e}")

filtered_data['sales_orders'] = filtered_sales_data

# ==================== 工具函数 ====================
def calculate_customer_metrics(sales_data, customer_relation=None):
    """计算客户相关指标 - 增强版"""
    try:
        if sales_data.empty:
            return {
                'total_customers': 0,
                'top5_concentration': 0,
                'top10_concentration': 0,
                'avg_customer_value': 0,
                'dependency_risk_score': 0,
                'customer_sales': pd.DataFrame(),
                'region_stats': pd.DataFrame(),
                'customer_person': pd.DataFrame()
            }

        # 查找客户ID列 - 更灵活的列名匹配
        customer_id_col = None
        for col in ['客户代码', '客户简称', '经销商名称', '客户', 'customer_id']:
            if col in sales_data.columns:
                customer_id_col = col
                break

        if not customer_id_col:
            st.warning("数据中未找到客户标识列")
            return {}

        # 筛选活跃客户
        active_customers = pd.DataFrame()
        if customer_relation is not None and not customer_relation.empty:
            # 确认状态列存在
            status_col = None
            for col in ['状态', 'status']:
                if col in customer_relation.columns:
                    status_col = col
                    break

            customer_code_col = None
            for col in ['客户代码', '客户', 'client_id']:
                if col in customer_relation.columns:
                    customer_code_col = col
                    break

            if status_col and customer_code_col:
                active_customers = customer_relation[customer_relation[status_col] == '正常']
                if not active_customers.empty:
                    active_customer_ids = active_customers[customer_code_col].unique()
                    if len(active_customer_ids) > 0 and customer_id_col in sales_data.columns:
                        sales_data = sales_data[sales_data[customer_id_col].isin(active_customer_ids)]

        # 客户总数
        total_customers = sales_data[customer_id_col].nunique() if customer_id_col in sales_data.columns else 0

        # 客户销售额统计
        sales_col = None
        for col in ['销售额', '求和项:金额（元）', '金额', 'sales_amount']:
            if col in sales_data.columns:
                sales_col = col
                break

        if not sales_col:
            # 如果没有销售额列，尝试计算
            price_col = None
            for col in ['单价（箱）', '单价', 'unit_price']:
                if col in sales_data.columns:
                    price_col = col
                    break

            qty_col = None
            for col in ['求和项:数量（箱）', '数量（箱）', '数量', 'quantity']:
                if col in sales_data.columns:
                    qty_col = col
                    break

            if price_col and qty_col:
                sales_data['销售额'] = sales_data[price_col] * sales_data[qty_col]
                sales_col = '销售额'
            else:
                st.warning("无法确定销售额列或计算销售额，将使用默认值0")
                sales_data['销售额'] = 0
                sales_col = '销售额'

        # 清理销售额数据
        sales_data[sales_col] = pd.to_numeric(sales_data[sales_col], errors='coerce').fillna(0)

        # 安全地计算客户销售额
        if customer_id_col in sales_data.columns and sales_col in sales_data.columns:
            customer_sales = sales_data.groupby(customer_id_col)[sales_col].sum().reset_index()
            customer_sales = customer_sales.sort_values(sales_col, ascending=False)
        else:
            customer_sales = pd.DataFrame(columns=[customer_id_col, sales_col])

        # 计算TOP5、TOP10客户销售额
        total_sales = customer_sales[sales_col].sum() if not customer_sales.empty else 0

        if len(customer_sales) >= 5:
            top5_sales = customer_sales.head(5)[sales_col].sum()
        else:
            top5_sales = total_sales

        if len(customer_sales) >= 10:
            top10_sales = customer_sales.head(10)[sales_col].sum()
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
        region_stats = pd.DataFrame()
        region_col = None
        for col in ['所属区域', '区域', 'region']:
            if col in sales_data.columns:
                region_col = col
                break

        if region_col and customer_id_col in sales_data.columns and sales_col in sales_data.columns:
            try:
                region_customers = sales_data.groupby(region_col)[customer_id_col].nunique().reset_index()
                region_customers.columns = [region_col, '客户数量']

                region_sales = sales_data.groupby(region_col)[sales_col].sum().reset_index()

                region_stats = pd.merge(region_customers, region_sales, on=region_col, how='left')
                region_stats['平均客户价值'] = region_stats[sales_col] / region_stats['客户数量'].apply(lambda x: max(x, 1))
            except Exception as e:
                st.warning(f"计算区域统计信息时出错: {str(e)}")

        # 添加客户销售员关系
        customer_person = pd.DataFrame()
        person_col = None
        for col in ['申请人', '销售员', 'salesperson']:
            if col in sales_data.columns:
                person_col = col
                break

        if person_col and customer_id_col in sales_data.columns and sales_col in sales_data.columns:
            try:
                customer_person = sales_data.groupby([customer_id_col, person_col])[sales_col].sum().reset_index()
                customer_person = customer_person.sort_values([customer_id_col, sales_col], ascending=[True, False])

                # 找出每个客户的主要销售员
                main_person = customer_person.loc[customer_person.groupby(customer_id_col)[sales_col].idxmax()]
                if not customer_sales.empty and not main_person.empty:
                    customer_sales = pd.merge(
                        customer_sales,
                        main_person[[customer_id_col, person_col]],
                        on=customer_id_col,
                        how='left'
                    )
            except Exception as e:
                st.warning(f"计算客户销售员关系时出错: {str(e)}")

        # 添加客户产品多样性
        product_col = None
        for col in ['产品代码', '产品ID', 'product_code']:
            if col in sales_data.columns:
                product_col = col
                break

        if product_col and customer_id_col in sales_data.columns:
            try:
                product_diversity = sales_data.groupby(customer_id_col)[product_col].nunique().reset_index()
                product_diversity.columns = [customer_id_col, '购买产品种类']
                if not customer_sales.empty and not product_diversity.empty:
                    customer_sales = pd.merge(
                        customer_sales,
                        product_diversity,
                        on=customer_id_col,
                        how='left'
                    )
            except Exception as e:
                st.warning(f"计算产品多样性时出错: {str(e)}")

        # 添加客户简称或名称
        customer_name_col = None
        for col in ['客户简称', '经销商名称', '客户名称', 'customer_name']:
            if col in sales_data.columns and col != customer_id_col:
                customer_name_col = col
                break

        if customer_name_col and customer_id_col in sales_data.columns:
            try:
                customer_names = sales_data.groupby(customer_id_col)[customer_name_col].first().reset_index()
                if not customer_sales.empty and not customer_names.empty:
                    customer_sales = pd.merge(
                        customer_sales,
                        customer_names,
                        on=customer_id_col,
                        how='left'
                    )
            except Exception as e:
                st.warning(f"添加客户名称时出错: {str(e)}")

        return {
            'total_customers': total_customers,
            'top5_concentration': top5_concentration,
            'top10_concentration': top10_concentration,
            'avg_customer_value': avg_customer_value,
            'dependency_risk_score': dependency_risk_score,
            'customer_sales': customer_sales,
            'region_stats': region_stats,
            'customer_person': customer_person,
            'sales_column': sales_col,
            'customer_id_column': customer_id_col,
            'customer_name_column': customer_name_col,
            'person_column': person_col,
            'product_column': product_col,
            'region_column': region_col
        }
    except Exception as e:
        st.error(f"计算客户指标时出错: {str(e)}")
        return {
            'total_customers': 0,
            'top5_concentration': 0,
            'top10_concentration': 0,
            'avg_customer_value': 0,
            'dependency_risk_score': 0,
            'customer_sales': pd.DataFrame(),
            'region_stats': pd.DataFrame(),
            'customer_person': pd.DataFrame()
        }


# ==================== 分析数据 ====================
def analyze_customer_data(filtered_data):
    """分析客户数据 - 增强版"""
    try:
        sales_data = filtered_data.get('sales_orders', pd.DataFrame())
        customer_relation = filtered_data.get('customer_relation', pd.DataFrame())

        if sales_data.empty:
            st.warning("筛选后的销售数据为空，无法进行客户分析")
            return {}

        # 获取当前年份数据
        date_col = None
        for col in ['发运月份', '月份', '日期', 'date']:
            if col in sales_data.columns:
                date_col = col
                break

        if date_col:
            try:
                sales_data[date_col] = pd.to_datetime(sales_data[date_col], errors='coerce')
                current_year = datetime.now().year
                ytd_sales = sales_data[pd.to_datetime(sales_data[date_col]).dt.year == current_year]
                if ytd_sales.empty:
                    ytd_sales = sales_data  # 如果当年没有数据，使用全部数据
            except Exception as e:
                st.warning(f"日期筛选出错: {str(e)}，将使用全部数据")
                ytd_sales = sales_data
        else:
            ytd_sales = sales_data

        # 计算客户指标
        customer_metrics = calculate_customer_metrics(ytd_sales, customer_relation)

        # 添加新品购买客户分析
        new_product_codes = filtered_data.get('new_product_codes', [])
        if new_product_codes:
            product_col = customer_metrics.get('product_column')
            customer_id_col = customer_metrics.get('customer_id_column')

            if product_col and customer_id_col and product_col in ytd_sales.columns and customer_id_col in ytd_sales.columns:
                try:
                    new_product_sales = ytd_sales[ytd_sales[product_col].isin(new_product_codes)]
                    new_product_customers = new_product_sales[customer_id_col].nunique()
                    customer_metrics['new_product_customers'] = new_product_customers

                    # 计算新品客户渗透率
                    customer_metrics['new_product_penetration'] = (
                            new_product_customers / customer_metrics['total_customers'] * 100) if customer_metrics[
                                                                                                      'total_customers'] > 0 else 0
                except Exception as e:
                    st.warning(f"新品客户分析出错: {str(e)}")

        return customer_metrics
    except Exception as e:
        st.error(f"客户数据分析出错: {str(e)}")
        return {}


# ==================== 图表创建函数 ====================
def create_customer_concentration_chart(customer_sales, title="客户销售额分布", customer_name_col=None, sales_col=None):
    """创建客户销售额分布图 - 增强版"""
    try:
        if customer_sales.empty or not sales_col or sales_col not in customer_sales.columns:
            return None

        # 只取前10名客户
        top_customers = customer_sales.head(10).copy()

        # 确定客户名称列
        display_name_col = 'display_name'
        if customer_name_col and customer_name_col in top_customers.columns:
            top_customers[display_name_col] = top_customers[customer_name_col]
        else:
            # 尝试找到任何可能的客户名称列
            found = False
            for col in top_customers.columns:
                if '客户' in col or '经销商' in col:
                    top_customers[display_name_col] = top_customers[col]
                    found = True
                    break

            if not found:
                # 如果没有找到，使用索引作为名称
                top_customers[display_name_col] = [f"客户{i + 1}" for i in range(len(top_customers))]

        fig = px.bar(
            top_customers,
            x=display_name_col,
            y=sales_col,
            title=title,
            color=sales_col,
            color_continuous_scale=px.colors.sequential.Blues,
            text=sales_col
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        return fig
    except Exception as e:
        st.error(f"创建客户销售额分布图出错: {str(e)}")
        return None


def create_concentration_gauge(concentration, title="客户集中度"):
    """创建客户集中度仪表盘"""
    try:
        # 确定颜色
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
            title={'text': f"{title}<br><span style='font-size:0.8em;color:{color}'>{status}</span>",
                   'font': {'size': 24}},
            number={'suffix': "%", 'font': {'size': 26, 'color': color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(50, 205, 50, 0.3)'},
                    {'range': [50, 70], 'color': 'rgba(255, 144, 14, 0.3)'},
                    {'range': [70, 100], 'color': 'rgba(255, 67, 54, 0.3)'}
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
            font={'color': "darkblue", 'family': "Arial"}
        )

        return fig
    except Exception as e:
        st.error(f"创建客户集中度仪表盘出错: {str(e)}")
        return None


def create_region_customers_chart(region_data, title="区域客户分布", region_col=None):
    """创建区域客户分布图 - 增强版"""
    try:
        if region_data.empty:
            return None

        # 确定区域列
        region_column = None
        if region_col and region_col in region_data.columns:
            region_column = region_col
        else:
            for col in ['所属区域', '区域', 'region']:
                if col in region_data.columns:
                    region_column = col
                    break

        if not region_column and len(region_data.columns) > 0:
            region_column = region_data.columns[0]  # 默认使用第一列

        if not region_column:
            return None

        # 按客户数量排序
        sorted_data = region_data.copy()
        if '客户数量' in sorted_data.columns:
            sorted_data = sorted_data.sort_values('客户数量', ascending=False)

        fig = px.bar(
            sorted_data,
            x=region_column,
            y='客户数量',
            title=title,
            color=region_column,
            text='客户数量',
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        fig.update_traces(
            textposition='outside'
        )

        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="区域",
            yaxis_title="客户数量",
            showlegend=False,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        return fig
    except Exception as e:
        st.error(f"创建区域客户分布图出错: {str(e)}")
        return None


def create_avg_value_bar(region_data, title="区域平均客户价值", region_col=None, value_col='平均客户价值'):
    """创建区域平均客户价值图 - 增强版"""
    try:
        if region_data.empty:
            return None

        # 确定区域列
        region_column = None
        if region_col and region_col in region_data.columns:
            region_column = region_col
        else:
            for col in ['所属区域', '区域', 'region']:
                if col in region_data.columns:
                    region_column = col
                    break

        if not region_column and len(region_data.columns) > 0:
            region_column = region_data.columns[0]  # 默认使用第一列

        if not region_column:
            return None

        # 确定值列
        value_column = None
        if value_col in region_data.columns:
            value_column = value_col
        else:
            for col in ['平均客户价值', 'avg_value']:
                if col in region_data.columns:
                    value_column = col
                    break

        if not value_column:
            # 尝试计算平均客户价值
            if '销售额' in region_data.columns and '客户数量' in region_data.columns:
                region_data['平均客户价值'] = region_data['销售额'] / region_data['客户数量'].apply(lambda x: max(x, 1))
                value_column = '平均客户价值'
            else:
                st.warning("无法确定或计算平均客户价值")
                return None

        # 按平均客户价值排序
        sorted_data = region_data.copy()
        if value_column in sorted_data.columns:
            sorted_data = sorted_data.sort_values(value_column, ascending=False)

        fig = px.bar(
            sorted_data,
            x=region_column,
            y=value_column,
            title=title,
            color=region_column,
            text=value_column,
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        fig.update_traces(
            texttemplate='¥%{y:,.0f}',
            textposition='outside'
        )

        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="区域",
            yaxis_title="平均客户价值（元）",
            showlegend=False,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        return fig
    except Exception as e:
        st.error(f"创建区域平均客户价值图出错: {str(e)}")
        return None


def create_customer_scatter(customer_data, title="客户价值与产品多样性", sales_col=None, person_col=None, name_col=None, product_col='购买产品种类'):
    """创建客户散点图 - 增强版"""
    try:
        if customer_data.empty:
            return None

        # 确认必要的列存在
        product_column = None
        if product_col in customer_data.columns:
            product_column = product_col
        else:
            for col in ['购买产品种类', '产品种类数']:
                if col in customer_data.columns:
                    product_column = col
                    break

        if not product_column:
            st.warning("缺少产品种类列，无法创建客户散点图")
            return None

        # 确认销售额列
        sales_column = None
        if sales_col and sales_col in customer_data.columns:
            sales_column = sales_col
        else:
            for col in ['销售额', '求和项:金额（元）', '金额', 'sales_amount']:
                if col in customer_data.columns:
                    sales_column = col
                    break

        if not sales_column:
            st.warning("缺少销售额列，无法创建客户散点图")
            return None

        # 确定人员列
        person_column = None
        if person_col and person_col in customer_data.columns:
            person_column = person_col
        else:
            for col in ['申请人', '销售员', 'salesperson']:
                if col in customer_data.columns:
                    person_column = col
                    break

        # 确定客户名称列
        hover_name = None
        if name_col and name_col in customer_data.columns:
            hover_name = name_col
        else:
            for col in ['客户简称', '经销商名称', '客户', 'customer_name']:
                if col in customer_data.columns:
                    hover_name = col
                    break

        if not hover_name and len(customer_data.columns) > 0:
            hover_name = customer_data.columns[0]  # 默认使用第一列

        # 创建散点图参数
        scatter_params = {
            'x': product_column,
            'y': sales_column,
            'size': sales_column,
            'title': title,
            'size_max': 50,
            'hover_name': hover_name if hover_name else None
        }

        # 添加颜色分组（如果有销售员列）
        if person_column:
            scatter_params['color'] = person_column

        # 创建散点图
        fig = px.scatter(
            customer_data,
            **scatter_params
        )

        fig.update_layout(
            height=450,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="购买产品种类",
            yaxis_title="销售额（元）",
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        # 添加客户价值分类线
        if sales_column in customer_data.columns:
            avg_value = customer_data[sales_column].mean()
            fig.add_shape(
                type="line",
                x0=0,
                x1=customer_data[product_column].max() * 1.1 if len(customer_data) > 0 else 10,
                y0=avg_value,
                y1=avg_value,
                line=dict(color="red", width=1, dash="dash")
            )

            fig.add_annotation(
                x=customer_data[product_column].max() * 0.9 if len(customer_data) > 0 else 9,
                y=avg_value * 1.1,
                text="平均客户价值",
                showarrow=False,
                font=dict(color="red")
            )

        return fig
    except Exception as e:
        st.error(f"创建客户散点图出错: {str(e)}")
        return None


def create_customer_segments_chart(customer_data, title="客户价值分类", sales_col=None, product_col=None):
    """创建客户价值分类图 - 增强版"""
    try:
        if customer_data.empty:
            return None

        # 确定销售额列
        sales_column = None
        if sales_col and sales_col in customer_data.columns:
            sales_column = sales_col
        else:
            for col in ['销售额', '求和项:金额（元）', '金额', 'sales_amount']:
                if col in customer_data.columns:
                    sales_column = col
                    break

        if not sales_column:
            st.warning("缺少销售额列，无法创建客户价值分类图")
            return None

        # 确定产品多样性列
        product_diversity_col = None
        if product_col and product_col in customer_data.columns:
            product_diversity_col = product_col
        else:
            for col in ['购买产品种类', '产品种类数']:
                if col in customer_data.columns:
                    product_diversity_col = col
                    break

        # 计算价值分布
        avg_value = customer_data[sales_column].mean() if sales_column in customer_data.columns else 0

        # 客户价值分类
        classified_data = customer_data.copy()  # 避免修改原始DataFrame
        if product_diversity_col and product_diversity_col in classified_data.columns:
            avg_variety = classified_data[product_diversity_col].mean()

            # 添加客户类型列
            classified_data['客户类型'] = classified_data.apply(
                lambda row: '高价值核心客户' if row[sales_column] > avg_value and row[product_diversity_col] > avg_variety
                else '高价值单一客户' if row[sales_column] > avg_value and row[product_diversity_col] <= avg_variety
                else '低价值多样客户' if row[sales_column] <= avg_value and row[product_diversity_col] > avg_variety
                else '低价值边缘客户',
                axis=1
            )
        else:
            # 如果没有产品多样性列，简化分类
            classified_data['客户类型'] = classified_data.apply(
                lambda row: '高价值客户' if row[sales_column] > avg_value else '低价值客户',
                axis=1
            )

        # 统计各类型客户数量
        segments = classified_data.groupby('客户类型').size().reset_index(name='客户数量')

        # 为每个类型分配颜色
        color_map = {
            '高价值核心客户': '#4CAF50',
            '高价值单一客户': '#2196F3',
            '低价值多样客户': '#FF9800',
            '低价值边缘客户': '#F44336',
            '高价值客户': '#4CAF50',
            '低价值客户': '#F44336'
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
            hoverinfo='label+percent+value',
            hovertemplate='%{label}: %{value}个客户<br>占比: %{percent}'
        )

        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        return fig, classified_data
    except Exception as e:
        st.error(f"创建客户价值分类图出错: {str(e)}")
        return None, None


# ==================== 主页面 ====================
try:
    # 分析数据
    with st.spinner("正在进行客户分析..."):
        customer_analysis = analyze_customer_data(filtered_data)

    if not customer_analysis:
        st.warning("无法进行客户分析，请检查数据")
        st.stop()

    # 创建标签页
    tabs = st.tabs(["📊 客户概览", "👑 TOP客户分析", "🌐 区域客户分析", "🔍 客户价值分析"])

    with tabs[0]:  # 客户概览
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
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">TOP5客户集中度</p>
                <p class="card-value" style="color: {'#4CAF50' if top5_concentration <= 50 else '#FF9800' if top5_concentration <= 70 else '#F44336'};">{format_percentage(top5_concentration)}</p>
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
            risk_color = "#4CAF50" if dependency_risk <= 50 else "#FF9800" if dependency_risk <= 70 else "#F44336"

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">客户依赖度风险</p>
                <p class="card-value" style="color: {risk_color};">{risk_level}</p>
                <p class="card-text">客户集中风险评估</p>
            </div>
            """, unsafe_allow_html=True)

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

                st.markdown(f"""
                <div class="chart-explanation">
                    <b>图表解读：</b> TOP5客户集中度为{format_percentage(top5_concentration)}，处于<span style="color: {'#4CAF50' if top5_concentration <= 50 else '#FF9800' if top5_concentration <= 70 else '#F44336'};">{concentration_status}</span>状态。
                    {'客户分布较为均衡，业务风险较低。' if top5_concentration <= 50 else '客户较为集中，存在一定依赖风险。' if top5_concentration <= 70 else '客户高度集中，存在严重依赖风险，需要积极开发新客户。'}
                </div>
                """, unsafe_allow_html=True)

        with cols[1]:
            # TOP10客户集中度
            top10_concentration = customer_analysis.get('top10_concentration', 0)
            fig = create_concentration_gauge(top10_concentration, "TOP10客户集中度")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                concentration_status = "健康" if top10_concentration <= 60 else "警示" if top10_concentration <= 80 else "风险"

                st.markdown(f"""
                <div class="chart-explanation">
                    <b>图表解读：</b> TOP10客户集中度为{format_percentage(top10_concentration)}，处于<span style="color: {'#4CAF50' if top10_concentration <= 60 else '#FF9800' if top10_concentration <= 80 else '#F44336'};">{concentration_status}</span>状态。
                    {'客户基础广泛，业务发展稳健。' if top10_concentration <= 60 else '客户基础略显集中，需关注客户开发。' if top10_concentration <= 80 else '客户严重集中，客户基础薄弱，急需拓展新客户。'}
                </div>
                """, unsafe_allow_html=True)

        # 客户价值分类
        st.markdown('<div class="sub-header">📊 客户价值分类</div>', unsafe_allow_html=True)

        # 客户价值散点图和分类图
        customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())
        sales_col = customer_analysis.get('sales_column')
        customer_name_col = customer_analysis.get('customer_name_column')
        person_col = customer_analysis.get('person_column')
        product_col = None
        for col in ['购买产品种类', '产品种类数']:
            if col in customer_sales.columns:
                product_col = col
                break

        cols = st.columns(2)
        with cols[0]:
            fig = create_customer_scatter(
                customer_sales,
                "客户价值分布",
                sales_col=sales_col,
                person_col=person_col,
                name_col=customer_name_col,
                product_col=product_col
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                st.markdown("""
                <div class="chart-explanation">
                    <b>图表解读：</b> 散点图显示了客户销售额与产品多样性的关系。图中右上方的客户是高价值核心客户，不仅销售额高，而且产品采购多样；右下方的客户是高价值单一客户，销售额高但集中在少数产品；左上方的客户是低价值多样客户，虽采购多样但总额不高；左下方的客户是低价值边缘客户，销售额低且产品单一。
                </div>
                """, unsafe_allow_html=True)

        with cols[1]:
            fig_result, classified_data = create_customer_segments_chart(
                customer_sales,
                "客户价值分类占比",
                sales_col=sales_col,
                product_col=product_col
            )
            if fig_result:
                st.plotly_chart(fig_result, use_container_width=True)

                # 图表解读
                st.markdown("""
                <div class="chart-explanation">
                    <b>图表解读：</b> 此图展示了不同价值类型客户的分布占比。高价值核心客户具有战略意义，需重点维护；高价值单一客户有扩展潜力，可增加品类渗透；低价值多样客户适合深耕，提升单品渗透率；低价值边缘客户则需评估投入产出比，进行分级管理。
                </div>
                """, unsafe_allow_html=True)

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
        sales_col = customer_analysis.get('sales_column')
        customer_name_col = customer_analysis.get('customer_name_column')

        if not customer_sales.empty and len(customer_sales) > 0:
            # TOP10客户销售额柱状图
            fig = create_customer_concentration_chart(
                customer_sales,
                "TOP10客户销售额",
                customer_name_col=customer_name_col,
                sales_col=sales_col
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # 图表解读
                top1_name = "TOP1客户"
                top1_sales = 0

                if len(customer_sales) > 0:
                    top1_row = customer_sales.iloc[0]
                    if customer_name_col and customer_name_col in top1_row:
                        top1_name = str(top1_row[customer_name_col])
                    if sales_col and sales_col in top1_row:
                        top1_sales = top1_row[sales_col]

                total_sales = customer_sales[sales_col].sum() if sales_col in customer_sales.columns else 0
                top1_percentage = (top1_sales / total_sales * 100) if total_sales > 0 else 0

                st.markdown(f"""
                <div class="chart-explanation">
                    <b>图表解读：</b> {top1_name}是最大客户，销售额{format_currency(top1_sales)}，占总销售额的{format_percentage(top1_percentage)}。
                    TOP10客户总体占比{format_percentage(customer_analysis.get('top10_concentration', 0))}，{'客户分布较为均衡。' if customer_analysis.get('top10_concentration', 0) <= 60 else '客户较为集中。'}
                </div>
                """, unsafe_allow_html=True)

            # TOP客户详细分析
            st.markdown('<div class="sub-header">🔍 TOP5客户详细分析</div>', unsafe_allow_html=True)

            # 获取TOP5客户
            top5_customers = customer_sales.head(5) if len(customer_sales) >= 5 else customer_sales

            # 创建TOP5客户卡片
            for i, row in top5_customers.iterrows():
                # 客户名称
                customer_name = "客户" + str(i + 1)
                if customer_name_col and customer_name_col in row:
                    customer_name = str(row[customer_name_col])

                # 销售额
                customer_sales_value = row[sales_col] if sales_col in row else 0

                # 销售占比
                customer_percentage = (customer_sales_value / total_sales * 100) if total_sales > 0 else 0

                # 产品种类
                customer_products = 0
                if product_col and product_col in row:
                    customer_products = row[product_col]

                # 销售员
                customer_sales_person = "未知"
                if person_col and person_col in row:
                    customer_sales_person = str(row[person_col])

                # 高价值判定
                is_high_value = customer_sales_value > avg_customer_value
                is_diverse = (isinstance(customer_products, (int, float)) and customer_products > 5)

                # 客户类型和建议
                if is_high_value and is_diverse:
                    customer_type = "高价值核心客户"
                    recommendation = "维护核心关系，深化战略合作"
                elif is_high_value:
                    customer_type = "高价值单一客户"
                    recommendation = "扩大产品覆盖，增加品类渗透"
                elif is_diverse:
                    customer_type = "低价值多样客户"
                    recommendation = "提高单品渗透率，增加客单价"
                else:
                    customer_type = "低价值边缘客户"
                    recommendation = "评估维护成本，考虑客户升级"

                st.markdown(f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); margin-bottom: 1rem;">
                    <h3 style="color: {COLORS['primary']};">{i + 1}. {customer_name}</h3>
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
            st.info("筛选条件下没有客户销售数据，请调整筛选条件。")

    with tabs[2]:  # 区域客户分析
        st.markdown('<div class="sub-header">🌐 区域客户分析</div>', unsafe_allow_html=True)

        # 区域客户分布
        region_stats = customer_analysis.get('region_stats', pd.DataFrame())
        region_col = customer_analysis.get('region_column')

        if not region_stats.empty:
            # 区域客户数量和平均客户价值
            cols = st.columns(2)
            with cols[0]:
                fig = create_region_customers_chart(region_stats, "区域客户分布", region_col=region_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读
                    most_region = None
                    most_customers = 0

                    if region_col and region_col in region_stats.columns and '客户数量' in region_stats.columns:
                        most_idx = region_stats['客户数量'].idxmax() if not region_stats.empty else None
                        if most_idx is not None and most_idx < len(region_stats):
                            most_region = region_stats.loc[most_idx, region_col]
                            most_customers = region_stats.loc[most_idx, '客户数量']

                    # 计算客户分布均衡度
                    is_balanced = False
                    if '客户数量' in region_stats.columns and len(region_stats) > 1:
                        customer_std = region_stats['客户数量'].std()
                        customer_mean = region_stats['客户数量'].mean()
                        is_balanced = (customer_std / customer_mean < 0.3) if customer_mean > 0 else False

                    st.markdown(f"""
                    <div class="chart-explanation">
                        <b>图表解读：</b> {f"{most_region}区域客户数量最多，有{most_customers}个客户，市场覆盖最广。" if most_region else ""}
                        {'客户分布较为均衡，市场覆盖全面。' if is_balanced else '客户分布不均，区域发展不平衡，需关注薄弱区域。'}
                    </div>
                    """, unsafe_allow_html=True)

            with cols[1]:
                fig = create_avg_value_bar(
                    region_stats,
                    "区域平均客户价值",
                    region_col=region_col,
                    value_col='平均客户价值'
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读 - 更健壮的实现
                    highest_value_region = None
                    highest_avg_value = 0
                    lowest_value_region = None
                    value_gap = 0

                    if region_col and region_col in region_stats.columns and '平均客户价值' in region_stats.columns:
                        if not region_stats.empty:
                            max_idx = region_stats['平均客户价值'].idxmax()
                            min_idx = region_stats['平均客户价值'].idxmin()

                            if max_idx is not None and max_idx < len(region_stats):
                                highest_value_region = region_stats.loc[max_idx, region_col]
                                highest_avg_value = region_stats.loc[max_idx, '平均客户价值']

                            if min_idx is not None and min_idx < len(region_stats):
                                lowest_value_region = region_stats.loc[min_idx, region_col]
                                min_value = region_stats.loc[min_idx, '平均客户价值']
                                value_gap = highest_avg_value / min_value if min_value > 0 else 0

                    st.markdown(f"""
                    <div class="chart-explanation">
                        <b>图表解读：</b> {f"{highest_value_region}区域平均客户价值最高，为{format_currency(highest_avg_value)}。" if highest_value_region else ""}
                        {f"{highest_value_region}与{lowest_value_region}区域的平均客户价值差距{value_gap:.1f}倍，{'区域客户价值差异显著' if value_gap > 2 else '区域客户价值较为均衡'}。" if highest_value_region and lowest_value_region and value_gap > 0 else ""}
                    </div>
                    """, unsafe_allow_html=True)

            # 区域客户价值矩阵
            st.markdown('<div class="sub-header">📊 区域客户价值矩阵</div>', unsafe_allow_html=True)

            try:
                # 创建区域客户价值矩阵
                region_matrix = region_stats.copy()
                if '客户数量' in region_matrix.columns:
                    total_customers = region_matrix['客户数量'].sum()
                    region_matrix['客户密度'] = region_matrix[
                                                    '客户数量'] / total_customers * 100 if total_customers > 0 else 0

                    # 计算全局平均值
                    avg_density = region_matrix['客户密度'].mean()
                    avg_value = region_matrix['平均客户价值'].mean() if '平均客户价值' in region_matrix.columns else 0

                    # 添加区域类型
                    region_matrix['区域类型'] = region_matrix.apply(
                        lambda row: '核心区域' if row['客户密度'] > avg_density and row['平均客户价值'] > avg_value
                        else '价值区域' if row['客户密度'] <= avg_density and row['平均客户价值'] > avg_value
                        else '数量区域' if row['客户密度'] > avg_density and row['平均客户价值'] <= avg_value
                        else '发展区域',
                        axis=1
                    )

                    # 创建区域客户价值散点图
                    fig = px.scatter(
                        region_matrix,
                        x='客户密度',
                        y='平均客户价值',
                        size='销售额' if '销售额' in region_matrix.columns else None,
                        color='区域类型',
                        hover_name=region_col if region_col else None,
                        text=region_col if region_col else None,
                        title="区域客户价值矩阵",
                        size_max=50,
                        color_discrete_map={
                            '核心区域': '#4CAF50',
                            '价值区域': '#2196F3',
                            '数量区域': '#FF9800',
                            '发展区域': '#F44336'
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
                            font=dict(size=12, color='#4CAF50')
                        ),
                        dict(
                            x=avg_density * 0.5,
                            y=avg_value * 1.5,
                            text="价值区域",
                            showarrow=False,
                            font=dict(size=12, color='#2196F3')
                        ),
                        dict(
                            x=avg_density * 1.5,
                            y=avg_value * 0.5,
                            text="数量区域",
                            showarrow=False,
                            font=dict(size=12, color='#FF9800')
                        ),
                        dict(
                            x=avg_density * 0.5,
                            y=avg_value * 0.5,
                            text="发展区域",
                            showarrow=False,
                            font=dict(size=12, color='#F44336')
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
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Arial"
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>图表解读：</b> 区域客户价值矩阵将区域按客户密度和平均客户价值分为四类：
                        <ul>
                            <li><b>核心区域</b> - 客户数量多且价值高，是业务核心区域，需维护优势</li>
                            <li><b>价值区域</b> - 客户数量少但价值高，适合精耕细作，提升客户覆盖</li>
                            <li><b>数量区域</b> - 客户数量多但价值低，需提升客户价值，加强产品渗透</li>
                            <li><b>发展区域</b> - 客户数量少且价值低，需评估发展潜力，针对性培育</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                    # 区域客户策略建议
                    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

                    # 获取各类型区域
                    core_regions = region_matrix[region_matrix['区域类型'] == '核心区域'][
                        region_col].tolist() if region_col else []
                    value_regions = region_matrix[region_matrix['区域类型'] == '价值区域'][
                        region_col].tolist() if region_col else []
                    quantity_regions = region_matrix[region_matrix['区域类型'] == '数量区域'][
                        region_col].tolist() if region_col else []
                    develop_regions = region_matrix[region_matrix['区域类型'] == '发展区域'][
                        region_col].tolist() if region_col else []

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
                    st.warning("区域数据缺少必要的'客户数量'列，无法创建价值矩阵")
            except Exception as e:
                st.error(f"创建区域客户价值矩阵时出错: {str(e)}")
        else:
            st.info("当前筛选条件下没有区域客户分析数据。请调整筛选条件。")

    with tabs[3]:  # 客户价值分析
        st.markdown('<div class="sub-header">🔍 客户价值分析</div>', unsafe_allow_html=True)

        # 客户价值分析
        customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())
        sales_col = customer_analysis.get('sales_column')
        customer_name_col = customer_analysis.get('customer_name_column')
        product_diversity_col = None
        for col in ['购买产品种类', '产品种类数']:
            if col in customer_sales.columns:
                product_diversity_col = col
                break

        if not customer_sales.empty and sales_col and sales_col in customer_sales.columns:
            if product_diversity_col and product_diversity_col in customer_sales.columns:
                # 创建客户价值分布散点图
                fig = create_customer_scatter(
                    customer_sales,
                    "客户价值与产品多样性分布",
                    sales_col=sales_col,
                    person_col=customer_analysis.get('person_column'),
                    name_col=customer_name_col,
                    product_col=product_diversity_col
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 图表解读
                    avg_value = customer_sales[sales_col].mean() if sales_col in customer_sales.columns else 0
                    avg_variety = customer_sales[
                        product_diversity_col].mean() if product_diversity_col in customer_sales.columns else 0

                    st.markdown(f"""
                    <div class="chart-explanation">
                        <b>图表解读：</b> 此图展示了客户销售额与产品多样性的关系。平均客户价值为{format_currency(avg_value)}，平均购买产品种类为{avg_variety:.1f}种。
                        客户主要分为四类：右上方的高价值核心客户，右下方的高价值单一客户，左上方的低价值多样客户，左下方的低价值边缘客户。不同类型的客户需要不同的经营策略。
                    </div>
                    """, unsafe_allow_html=True)

                # 客户价值分析详情
                st.markdown('<div class="sub-header">📊 客户价值分类详情</div>', unsafe_allow_html=True)

                # 创建客户价值分类图
                fig_result, classified_data = create_customer_segments_chart(
                    customer_sales,
                    "客户价值分类占比",
                    sales_col=sales_col,
                    product_col=product_diversity_col
                )

                if fig_result and classified_data is not None:
                    st.plotly_chart(fig_result, use_container_width=True)

                    # 获取客户分类数据
                    if '客户类型' in classified_data.columns:
                        # 统计各类型客户数量和销售额
                        segment_stats = classified_data.groupby('客户类型').agg({
                            sales_col: 'sum',
                            classified_data.index.name if classified_data.index.name else '客户代码': 'count'
                        }).reset_index()

                        if segment_stats.empty:
                            segment_stats = pd.DataFrame(columns=['客户类型', '销售额', '客户数量'])
                        else:
                            segment_stats.columns = ['客户类型', '销售额', '客户数量']

                        # 客户类型卡片
                        col1, col2 = st.columns(2)

                        with col1:
                            # 高价值核心客户
                            core_stats = segment_stats[segment_stats['客户类型'] == '高价值核心客户'] if '客户类型' in segment_stats.columns else pd.DataFrame()
                            if not core_stats.empty:
                                core_count = core_stats.iloc[0]['客户数量'] if '客户数量' in core_stats.columns else 0
                                core_sales = core_stats.iloc[0]['销售额'] if '销售额' in core_stats.columns else 0
                                core_percentage = core_stats.iloc[0]['客户数量'] / segment_stats['客户数量'].sum() * 100 if '客户数量' in segment_stats.columns and segment_stats['客户数量'].sum() > 0 else 0
                                core_sales_percentage = core_stats.iloc[0]['销售额'] / segment_stats['销售额'].sum() * 100 if '销售额' in segment_stats.columns and segment_stats['销售额'].sum() > 0 else 0
                                core_products = classified_data[classified_data['客户类型'] == '高价值核心客户'][product_diversity_col].mean() if product_diversity_col in classified_data.columns else 0

                                st.markdown(f"""
                                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; 
                                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="color: #4CAF50;">💎 高价值核心客户</h4>
                                    <p><b>客户数量：</b> {format_number(core_count)} ({format_percentage(core_percentage)})</p>
                                    <p><b>销售贡献：</b> {format_currency(core_sales)} ({format_percentage(core_sales_percentage)})</p>
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
                            diverse_stats = segment_stats[segment_stats['客户类型'] == '低价值多样客户'] if '客户类型' in segment_stats.columns else pd.DataFrame()
                            if not diverse_stats.empty:
                                diverse_count = diverse_stats.iloc[0]['客户数量'] if '客户数量' in diverse_stats.columns else 0
                                diverse_sales = diverse_stats.iloc[0]['销售额'] if '销售额' in diverse_stats.columns else 0
                                diverse_percentage = diverse_stats.iloc[0]['客户数量'] / segment_stats['客户数量'].sum() * 100 if '客户数量' in segment_stats.columns and segment_stats['客户数量'].sum() > 0 else 0
                                diverse_sales_percentage = diverse_stats.iloc[0]['销售额'] / segment_stats['销售额'].sum() * 100 if '销售额' in segment_stats.columns and segment_stats['销售额'].sum() > 0 else 0
                                diverse_products = classified_data[classified_data['客户类型'] == '低价值多样客户'][product_diversity_col].mean() if product_diversity_col in classified_data.columns else 0

                                st.markdown(f"""
                                <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; 
                                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="color: #FF9800;">🌱 低价值多样客户</h4>
                                    <p><b>客户数量：</b> {format_number(diverse_count)} ({format_percentage(diverse_percentage)})</p>
                                    <p><b>销售贡献：</b> {format_currency(diverse_sales)} ({format_percentage(diverse_sales_percentage)})</p>
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
                            single_stats = segment_stats[segment_stats['客户类型'] == '高价值单一客户'] if '客户类型' in segment_stats.columns else pd.DataFrame()
                            if not single_stats.empty:
                                single_count = single_stats.iloc[0]['客户数量'] if '客户数量' in single_stats.columns else 0
                                single_sales = single_stats.iloc[0]['销售额'] if '销售额' in single_stats.columns else 0
                                single_percentage = single_stats.iloc[0]['客户数量'] / segment_stats['客户数量'].sum() * 100 if '客户数量' in segment_stats.columns and segment_stats['客户数量'].sum() > 0 else 0
                                single_sales_percentage = single_stats.iloc[0]['销售额'] / segment_stats['销售额'].sum() * 100 if '销售额' in segment_stats.columns and segment_stats['销售额'].sum() > 0 else 0
                                single_products = classified_data[classified_data['客户类型'] == '高价值单一客户'][product_diversity_col].mean() if product_diversity_col in classified_data.columns else 0

                                st.markdown(f"""
                                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; 
                                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="color: #2196F3;">💰 高价值单一客户</h4>
                                    <p><b>客户数量：</b> {format_number(single_count)} ({format_percentage(single_percentage)})</p>
                                    <p><b>销售贡献：</b> {format_currency(single_sales)} ({format_percentage(single_sales_percentage)})</p>
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
                            marginal_stats = segment_stats[segment_stats['客户类型'] == '低价值边缘客户'] if '客户类型' in segment_stats.columns else pd.DataFrame()
                            if not marginal_stats.empty:
                                marginal_count = marginal_stats.iloc[0]['客户数量'] if '客户数量' in marginal_stats.columns else 0
                                marginal_sales = marginal_stats.iloc[0]['销售额'] if '销售额' in marginal_stats.columns else 0
                                marginal_percentage = marginal_stats.iloc[0]['客户数量'] / segment_stats['客户数量'].sum() * 100 if '客户数量' in segment_stats.columns and segment_stats['客户数量'].sum() > 0 else 0
                                marginal_sales_percentage = marginal_stats.iloc[0]['销售额'] / segment_stats['销售额'].sum() * 100 if '销售额' in segment_stats.columns and segment_stats['销售额'].sum() > 0 else 0
                                marginal_products = classified_data[classified_data['客户类型'] == '低价值边缘客户'][product_diversity_col].mean() if product_diversity_col in classified_data.columns else 0

                                st.markdown(f"""
                                <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; 
                                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <h4 style="color: #F44336;">⚠️ 低价值边缘客户</h4>
                                    <p><b>客户数量：</b> {format_number(marginal_count)} ({format_percentage(marginal_percentage)})</p>
                                    <p><b>销售贡献：</b> {format_currency(marginal_sales)} ({format_percentage(marginal_sales_percentage)})</p>
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
                        high_value_customers = classified_data[classified_data['客户类型'].isin(['高价值核心客户', '高价值单一客户'])] if '客户类型' in classified_data.columns else pd.DataFrame()
                        high_value_count = len(high_value_customers)
                        high_value_percentage = (high_value_count / len(classified_data) * 100) if len(classified_data) > 0 else 0
                        high_value_sales = high_value_customers[sales_col].sum() if sales_col in high_value_customers.columns else 0
                        high_value_sales_percentage = (high_value_sales / classified_data[sales_col].sum() * 100) if sales_col in classified_data.columns and classified_data[sales_col].sum() > 0 else 0

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

                        # 客户价值矩阵表格
                        with st.expander("查看客户价值分类详细数据"):
                            try:
                                # 按客户类型筛选客户
                                core_customers = classified_data[classified_data['客户类型'] == '高价值核心客户'].copy() if '客户类型' in classified_data.columns else pd.DataFrame()
                                single_customers = classified_data[classified_data['客户类型'] == '高价值单一客户'].copy() if '客户类型' in classified_data.columns else pd.DataFrame()
                                diverse_customers = classified_data[classified_data['客户类型'] == '低价值多样客户'].copy() if '客户类型' in classified_data.columns else pd.DataFrame()
                                marginal_customers = classified_data[classified_data['客户类型'] == '低价值边缘客户'].copy() if '客户类型' in classified_data.columns else pd.DataFrame()

                                # 对各类型客户按销售额排序
                                if sales_col in core_customers.columns:
                                    core_customers = core_customers.sort_values(sales_col, ascending=False)
                                if sales_col in single_customers.columns:
                                    single_customers = single_customers.sort_values(sales_col, ascending=False)
                                if sales_col in diverse_customers.columns:
                                    diverse_customers = diverse_customers.sort_values(sales_col, ascending=False)
                                if sales_col in marginal_customers.columns:
                                    marginal_customers = marginal_customers.sort_values(sales_col, ascending=False)

                                # 创建标签页
                                customer_tabs = st.tabs(
                                    ["高价值核心客户", "高价值单一客户", "低价值多样客户", "低价值边缘客户"])

                                # 确定要显示的列
                                customer_id_col = customer_analysis.get('customer_id_column')
                                person_col = customer_analysis.get('person_column')

                                display_cols = []
                                if customer_id_col and customer_id_col in classified_data.columns:
                                    display_cols.append(customer_id_col)
                                if customer_name_col and customer_name_col in classified_data.columns:
                                    display_cols.append(customer_name_col)
                                if sales_col and sales_col in classified_data.columns:
                                    display_cols.append(sales_col)
                                if product_diversity_col and product_diversity_col in classified_data.columns:
                                    display_cols.append(product_diversity_col)
                                if person_col and person_col in classified_data.columns:
                                    display_cols.append(person_col)

                                # 如果没有找到任何列，使用所有列
                                if not display_cols:
                                    display_cols = [col for col in classified_data.columns if col != '客户类型']

                                with customer_tabs[0]:
                                    if not core_customers.empty:
                                        valid_cols = [col for col in display_cols if col in core_customers.columns]
                                        if valid_cols:
                                            st.dataframe(core_customers[valid_cols], use_container_width=True)
                                        else:
                                            st.info("无法显示数据，列名不匹配")
                                    else:
                                        st.info("暂无高价值核心客户")

                                with customer_tabs[1]:
                                    if not single_customers.empty:
                                        valid_cols = [col for col in display_cols if col in single_customers.columns]
                                        if valid_cols:
                                            st.dataframe(single_customers[valid_cols], use_container_width=True)
                                        else:
                                            st.info("无法显示数据，列名不匹配")
                                    else:
                                        st.info("暂无高价值单一客户")

                                with customer_tabs[2]:
                                    if not diverse_customers.empty:
                                        valid_cols = [col for col in display_cols if col in diverse_customers.columns]
                                        if valid_cols:
                                            st.dataframe(diverse_customers[valid_cols], use_container_width=True)
                                        else:
                                            st.info("无法显示数据，列名不匹配")
                                    else:
                                        st.info("暂无低价值多样客户")

                                with customer_tabs[3]:
                                    if not marginal_customers.empty:
                                        valid_cols = [col for col in display_cols if col in marginal_customers.columns]
                                        if valid_cols:
                                            st.dataframe(marginal_customers[valid_cols], use_container_width=True)
                                        else:
                                            st.info("无法显示数据，列名不匹配")
                                    else:
                                        st.info("暂无低价值边缘客户")
                            except Exception as e:
                                st.error(f"显示客户价值分类详细数据时出错: {str(e)}")
                    else:
                        st.warning("创建客户价值分类图出错，无法获取分类数据")
                else:
                    st.warning("数据中缺少产品多样性列，无法进行完整的客户价值分析")
            else:
                st.warning("数据中缺少必要的列，无法进行客户价值分析")
        else:
            st.info("当前筛选条件下没有客户价值分析数据。请调整筛选条件。")

    # 客户洞察总结
    st.markdown('<div class="sub-header">💡 客户洞察总结</div>', unsafe_allow_html=True)

    # 生成洞察内容
    total_customers = customer_analysis.get('total_customers', 0)
    top5_concentration = customer_analysis.get('top5_concentration', 0)
    avg_customer_value = customer_analysis.get('avg_customer_value', 0)

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
    sales_col = customer_analysis.get('sales_column')
    if not customer_sales.empty and sales_col and sales_col in customer_sales.columns:
        # 检查客户价值分布均衡度
        sales_std = customer_sales[sales_col].std()
        sales_mean = customer_sales[sales_col].mean()
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
except Exception as e:
    st.error(f"页面渲染过程中发生错误: {str(e)}")