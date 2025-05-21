# customer_page.py - 客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import re
import os

# 忽略警告
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="客户分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 更现代化的设计
st.markdown("""
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --accent-color: #f0f8ff;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --gray-color: #6c757d;
    }

    /* 主标题 */
    .main-header {
        font-size: 2rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }

    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
        cursor: pointer;
        border-left: 5px solid var(--primary-color);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.15);
    }

    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .card-text {
        font-size: 0.9rem;
        color: var(--gray-color);
    }

    .card-trend {
        margin-top: 0.5rem;
        font-weight: 500;
    }

    .trend-up {
        color: var(--success-color);
    }

    .trend-down {
        color: var(--danger-color);
    }

    /* 图表容器 */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* 图表解释框 */
    .chart-explanation {
        background-color: var(--accent-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 5px solid var(--primary-color);
        font-size: 0.95rem;
    }

    /* 章节标题 */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }

    /* 提示框 */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 5px solid var(--success-color);
    }

    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 5px solid var(--warning-color);
    }

    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 5px solid var(--danger-color);
    }

    /* 标签样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    /* 登录框样式 */
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
    }

    .login-header {
        text-align: center;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* 客户分级标签 */
    .customer-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }

    .tag-large {
        background-color: #4CAF50;
        color: white;
    }

    .tag-medium {
        background-color: #2196F3;
        color: white;
    }

    .tag-small {
        background-color: #9E9E9E;
        color: white;
    }

    /* 悬浮效果 */
    .hover-info {
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 添加活动标签跟踪（用于卡片点击跳转）
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0  # 默认显示第一个标签

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div style="font-size: 1.8rem; color: #1f3867; text-align: center; margin-bottom: 1.5rem; font-weight: 600;">客户分析仪表盘 | 登录</div>',
        unsafe_allow_html=True)

    # 创建居中的登录框
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <h2 class="login-header">请输入密码</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("密码", type="password", key="password_input")

        # 登录按钮
        login_button = st.button("登录")

        # 验证密码
        if login_button:
            if password == 'SAL!2025':  # 使用与app.py相同的密码
                st.session_state['authenticated'] = True
                st.success("登录成功！")
                try:
                    st.rerun()  # 使用新版本方法
                except AttributeError:
                    try:
                        st.experimental_rerun()  # 尝试使用旧版本方法
                    except:
                        st.error("请刷新页面以查看更改")
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()


# ====== 实用工具函数（替代config.py） ======

# 格式化货币
def format_currency(value):
    """将数值格式化为货币形式"""
    if pd.isna(value) or value is None:
        return "¥0"

    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except:
            return value

    if abs(value) >= 1_000_000:
        return f"¥{value / 1_000_000:.2f}M"
    elif abs(value) >= 1000:
        return f"¥{value / 1000:.1f}K"
    else:
        return f"¥{value:.0f}"


# 格式化数字
def format_number(value):
    """格式化数字，大数使用K/M表示"""
    if pd.isna(value) or value is None:
        return "0"

    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except:
            return value

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs(value) >= 1000:
        return f"{value / 1000:.1f}K"
    else:
        return f"{value:.0f}"


# 格式化百分比
def format_percentage(value):
    """将数值格式化为百分比形式"""
    if pd.isna(value) or value is None:
        return "0%"

    if isinstance(value, str):
        try:
            value = float(value.replace('%', '').replace(',', ''))
        except:
            return value

    return f"{value:.1f}%"


# 加载数据文件
def load_data_files():
    """加载所需的数据文件"""
    data = {}

    try:
        # 定义可能的数据文件路径
        base_paths = [
            "./data/",  # 当前目录下的data文件夹
            "../data/",  # 上级目录的data文件夹
            "./",  # 当前目录
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/"),  # 相对于脚本的路径
        ]

        # 尝试找到销售订单数据
        sales_orders_found = False
        for base_path in base_paths:
            for filename in [
                "仪表盘原始数据.xlsx",
                "sales_orders.xlsx",
                "sales_data.xlsx",
                "订单数据.xlsx"
            ]:
                file_path = os.path.join(base_path, filename)
                if os.path.exists(file_path):
                    st.sidebar.info(f"从 {file_path} 加载销售订单数据")
                    data['sales_orders'] = pd.read_excel(file_path)
                    sales_orders_found = True
                    break
            if sales_orders_found:
                break

        # 如果没有找到销售订单数据，创建模拟数据
        if not sales_orders_found:
            st.sidebar.warning("未找到销售订单数据，使用模拟数据进行演示")
            # 创建模拟数据
            months = pd.date_range(start='2023-01-01', end='2025-05-01', freq='MS')
            regions = ['北', '南', '东', '西']
            customers = [f'客户{i}' for i in range(1, 51)]
            products = [f'产品{i}' for i in range(1, 30)]

            # 生成随机数据
            np.random.seed(42)
            n_rows = 2000

            mock_data = {
                '发运月份': np.random.choice(months, n_rows),
                '所属区域': np.random.choice(regions, n_rows),
                '客户代码': np.random.choice([f'CU{i:04d}' for i in range(1, 101)], n_rows),
                '经销商名称': np.random.choice([f'{region}区客户{i}' for region in regions for i in range(1, 26)],
                                               n_rows),
                '客户简称': np.random.choice([f'{region}客户{i}' for region in regions for i in range(1, 26)], n_rows),
                '申请人': np.random.choice([f'销售员{i}' for i in range(1, 11)], n_rows),
                '产品代码': np.random.choice([f'F{i:04d}' for i in range(1, 101)], n_rows),
                '产品名称': np.random.choice([f'口力{product}' for product in products], n_rows),
                '产品简称': np.random.choice(products, n_rows),
                '单价（箱）': np.random.uniform(80, 300, n_rows).round(2),
                '求和项:数量（箱）': np.random.randint(1, 100, n_rows),
            }

            # 计算金额
            mock_data['求和项:金额（元）'] = mock_data['单价（箱）'] * mock_data['求和项:数量（箱）']

            data['sales_orders'] = pd.DataFrame(mock_data)

        # 尝试加载客户关系表
        for base_path in base_paths:
            file_path = os.path.join(base_path, "仪表盘人与客户关系表.xlsx")
            if os.path.exists(file_path):
                data['customer_relation'] = pd.read_excel(file_path)
                break

        # 尝试加载客户目标数据
        for base_path in base_paths:
            file_path = os.path.join(base_path, "仪表盘客户月度指标维护.xlsx")
            if os.path.exists(file_path):
                data['customer_target'] = pd.read_excel(file_path)
                break

        return data

    except Exception as e:
        st.error(f"加载数据文件时出错: {str(e)}")
        return {'sales_orders': pd.DataFrame()}


# 图表解释函数
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 客户专用筛选器
def create_customer_filters(data):
    """创建客户分析专用的筛选器"""
    # 初始化筛选结果
    filtered_data = data.copy()

    # 确保数据加载成功
    if not data or 'sales_orders' not in data or data['sales_orders'].empty:
        st.sidebar.warning("无法加载客户数据，请检查数据源")
        return filtered_data

    orders = data['sales_orders']
    customer_relation = data.get('customer_relation', pd.DataFrame())

    with st.sidebar:
        st.markdown("## 🔍 客户筛选")
        st.markdown("---")

        # 1. 区域筛选
        if '所属区域' in orders.columns:
            all_regions = sorted(['全部'] + list(orders['所属区域'].unique()))
            selected_region = st.sidebar.selectbox(
                "选择区域", all_regions, index=0, key="customer_region_filter"
            )
            if selected_region != '全部':
                orders = orders[orders['所属区域'] == selected_region]

        # 2. 客户状态筛选（基于客户关系表）
        if not customer_relation.empty and '状态' in customer_relation.columns:
            status_options = ['全部', '正常', '闭户']
            selected_status = st.sidebar.selectbox(
                "客户状态", status_options, index=0, key="customer_status_filter"
            )
            if selected_status != '全部':
                # 根据状态过滤客户关系表
                filtered_customers = customer_relation[customer_relation['状态'] == selected_status]

                # 找出客户列
                customer_col = None
                for col in ['客户', '客户简称', '经销商名称', '客户代码']:
                    if col in customer_relation.columns:
                        customer_col = col
                        break

                if customer_col:
                    # 获取符合状态的客户列表
                    valid_customers = filtered_customers[customer_col].unique()

                    # 查找订单表中对应客户列
                    order_customer_col = None
                    for col in ['客户代码', '经销商名称', '客户简称']:
                        if col in orders.columns:
                            order_customer_col = col
                            break

                    if order_customer_col:
                        # 根据状态过滤订单
                        orders = orders[orders[order_customer_col].isin(valid_customers)]

        # 3. 销售员筛选
        if '申请人' in orders.columns:
            all_sales = sorted(['全部'] + list(orders['申请人'].unique()))
            selected_sales = st.sidebar.selectbox(
                "销售员", all_sales, index=0, key="customer_salesperson_filter"
            )
            if selected_sales != '全部':
                orders = orders[orders['申请人'] == selected_sales]

        # 4. 客户类型或层级筛选 (基于销售额分层)
        if '销售额' in orders.columns or ('求和项:金额（元）' in orders.columns and '销售额' not in orders.columns):
            # 如果没有销售额列但有金额列，创建销售额列
            if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
                orders['销售额'] = orders['求和项:金额（元）']

            # 按客户汇总销售额
            customer_col = None
            for col in ['客户代码', '经销商名称', '客户简称']:
                if col in orders.columns:
                    customer_col = col
                    break

            if customer_col:
                customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
                # 使用qcut对客户按销售额分层
                customer_sales['层级'] = pd.qcut(
                    customer_sales['销售额'],
                    q=[0, 0.5, 0.8, 1.0],
                    labels=['小客户', '中等客户', '大客户']
                )

                # 计算每个层级的客户数量
                tier_counts = customer_sales['层级'].value_counts()

                tier_options = ['全部', '大客户', '中等客户', '小客户']
                selected_tier = st.sidebar.selectbox(
                    "客户层级", tier_options, index=0,
                    help=f"大客户: 销售额前20%的客户 ({tier_counts.get('大客户', 0)}家)\n"
                         f"中等客户: 销售额前21-50%的客户 ({tier_counts.get('中等客户', 0)}家)\n"
                         f"小客户: 销售额占比低于50%的客户 ({tier_counts.get('小客户', 0)}家)",
                    key="customer_tier_filter"
                )

                if selected_tier != '全部':
                    tier_customers = customer_sales[customer_sales['层级'] == selected_tier][customer_col].tolist()
                    orders = orders[orders[customer_col].isin(tier_customers)]

        # 5. 日期范围筛选
        if '发运月份' in orders.columns:
            try:
                # 确保发运月份是日期类型
                if not pd.api.types.is_datetime64_any_dtype(orders['发运月份']):
                    orders['发运月份'] = pd.to_datetime(orders['发运月份'])

                min_date = orders['发运月份'].min()
                max_date = orders['发运月份'].max()

                # 转换为日期以供date_input使用
                min_date = min_date.date() if hasattr(min_date, 'date') else min_date
                max_date = max_date.date() if hasattr(max_date, 'date') else max_date

                st.sidebar.markdown("### 日期范围")
                # 默认显示最近6个月
                default_start = (pd.to_datetime(max_date) - pd.Timedelta(days=180)).date()
                default_start = max(default_start, min_date)

                start_date = st.sidebar.date_input(
                    "开始日期", value=default_start, min_value=min_date, max_value=max_date,
                    key="customer_start_date"
                )
                end_date = st.sidebar.date_input(
                    "结束日期", value=max_date, min_value=min_date, max_value=max_date,
                    key="customer_end_date"
                )

                if end_date < start_date:
                    st.sidebar.warning("结束日期不能早于开始日期，已自动调整")
                    end_date = start_date

                # 转换为datetime格式以便比较
                start_datetime = pd.Timestamp(start_date)
                end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

                # 应用日期筛选
                orders = orders[(orders['发运月份'] >= start_datetime) &
                                (orders['发运月份'] <= end_datetime)]
            except Exception as e:
                st.sidebar.warning(f"日期筛选器初始化失败: {e}")

        # 筛选器重置按钮
        if st.sidebar.button("重置筛选条件", key="reset_customer_filters"):
            try:
                st.rerun()  # 使用新版本方法
            except AttributeError:
                try:
                    st.experimental_rerun()  # 尝试使用旧版本方法
                except:
                    st.warning("请手动刷新页面重置筛选条件")

    # 更新筛选后的数据
    filtered_data['sales_orders'] = orders
    return filtered_data


# 计算客户关键指标
def calculate_customer_kpis(data):
    """计算客户分析的关键指标"""
    kpis = {}

    try:
        orders = data.get('sales_orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty:
            return kpis

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 找出客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return kpis

        # 1. 总客户数量
        kpis['total_customers'] = orders[customer_col].nunique()

        # 2. 客户平均销售额
        if '销售额' in orders.columns:
            total_sales = orders['销售额'].sum()
            kpis['total_sales'] = total_sales
            kpis['avg_customer_sales'] = total_sales / kpis['total_customers'] if kpis['total_customers'] > 0 else 0

            # 计算top客户贡献
            customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
            customer_sales = customer_sales.sort_values('销售额', ascending=False)

            # 计算TOP 20%客户销售额占比
            top_count = max(1, int(kpis['total_customers'] * 0.2))  # 至少1个客户
            top_sales = customer_sales.head(top_count)['销售额'].sum()
            kpis['top_customers_contribution'] = top_sales / total_sales if total_sales > 0 else 0
            kpis['top_customers_count'] = top_count

            # 计算上个周期（如上月）同比增长
            if '发运月份' in orders.columns:
                # 确保是日期类型
                if not pd.api.types.is_datetime64_any_dtype(orders['发运月份']):
                    orders['发运月份'] = pd.to_datetime(orders['发运月份'])

                # 计算当前月和上月
                current_month = orders['发运月份'].max().to_period('M')
                previous_month = (current_month.to_timestamp() - pd.Timedelta(days=30)).to_period('M')

                # 当月销售额
                current_month_sales = orders[orders['发运月份'].dt.to_period('M') == current_month]['销售额'].sum()

                # 上月销售额
                previous_month_sales = orders[orders['发运月份'].dt.to_period('M') == previous_month]['销售额'].sum()

                # 环比增长率
                if previous_month_sales > 0:
                    kpis['sales_growth'] = (current_month_sales - previous_month_sales) / previous_month_sales
                else:
                    kpis['sales_growth'] = 0 if current_month_sales == 0 else 1  # 避免除零错误

                # 当月和上月的客户数
                current_month_customers = orders[orders['发运月份'].dt.to_period('M') == current_month][
                    customer_col].nunique()
                previous_month_customers = orders[orders['发运月份'].dt.to_period('M') == previous_month][
                    customer_col].nunique()

                # 客户数环比增长率
                if previous_month_customers > 0:
                    kpis['customer_count_growth'] = (
                                                            current_month_customers - previous_month_customers) / previous_month_customers
                else:
                    kpis['customer_count_growth'] = 0 if current_month_customers == 0 else 1

        # 3. 客户订单频次和客单价
        orders_count = orders.groupby(customer_col).size().reset_index(name='订单数')
        kpis['avg_order_frequency'] = orders_count['订单数'].mean()

        if '销售额' in orders.columns:
            # 计算平均客单价
            total_orders = len(orders)
            kpis['avg_order_value'] = total_sales / total_orders if total_orders > 0 else 0

        # 4. 目标达成率
        if not customer_target.empty and '月度指标' in customer_target.columns:
            common_cols = set(customer_target.columns) & set(orders.columns)
            if customer_col in common_cols and '月份' in customer_target.columns and '发运月份' in orders.columns:
                # 准备订单月份
                if not pd.api.types.is_datetime64_any_dtype(orders['发运月份']):
                    orders['发运月份'] = pd.to_datetime(orders['发运月份'])

                orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()

                # 合并订单和目标
                # 为每个客户和月份创建销售汇总
                sales_monthly = orders.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

                # 合并目标数据
                merged = pd.merge(sales_monthly, customer_target, on=[customer_col, '月份'], how='inner')

                if not merged.empty:
                    # 计算达成率
                    merged['达成率'] = merged['销售额'] / merged['月度指标'] * 100
                    kpis['target_achievement'] = merged['达成率'].mean()
                    kpis['target_achievement_count'] = sum(merged['达成率'] >= 100)
                    kpis['target_total_count'] = len(merged)
                    kpis['target_achievement_rate'] = (
                        kpis['target_achievement_count'] / kpis['target_total_count'] * 100
                        if kpis['target_total_count'] > 0 else 0)

        return kpis

    except Exception as e:
        st.error(f"计算客户KPI时出错: {str(e)}")
        return {}


# 创建客户销售额排行图表 - 改进版
def create_top_customers_chart(data, top_n=10):
    """创建客户销售额排行图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty or len(orders) < 5:
            st.warning("数据不足，无法创建客户销售额排行图表")
            return None

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return None

        # 按客户汇总销售额
        if '销售额' in orders.columns:
            customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
            customer_sales = customer_sales.sort_values('销售额', ascending=False).head(top_n)

            # 如果有客户简称列，使用简称；否则使用代码
            display_col = customer_col
            if '客户简称' in orders.columns and customer_col != '客户简称':
                # 尝试获取客户简称
                customer_name_map = {}
                for _, row in orders.drop_duplicates([customer_col, '客户简称']).iterrows():
                    customer_name_map[row[customer_col]] = row['客户简称']

                if customer_name_map:
                    customer_sales['客户简称'] = customer_sales[customer_col].map(
                        lambda x: customer_name_map.get(x, x))
                    display_col = '客户简称'

            # 计算累计销售额和占比
            total_sales = customer_sales['销售额'].sum()
            customer_sales['累计销售额'] = customer_sales['销售额'].cumsum()
            customer_sales['累计占比'] = customer_sales['累计销售额'] / total_sales * 100

            # 创建水平条形图
            fig = go.Figure()

            # 定义渐变颜色
            colorscale = px.colors.sequential.Blues
            colors = [colorscale[int((i / (len(customer_sales) - 1 if len(customer_sales) > 1 else 1)) * (
                    len(colorscale) - 1))]
                      for i in range(len(customer_sales))]

            # 添加销售额水平条形图
            fig.add_trace(go.Bar(
                y=customer_sales[display_col],
                x=customer_sales['销售额'],
                marker_color=colors,
                orientation='h',
                name='销售额',
                text=customer_sales['销售额'].apply(lambda x: f"{x:,.0f}"),
                textposition='auto',
                textfont=dict(size=12)
            ))

            # 添加累计占比线
            fig.add_trace(go.Scatter(
                y=customer_sales[display_col],
                x=customer_sales['累计占比'].apply(lambda x: x * customer_sales['销售额'].max() / 100),
                mode='lines+markers',
                name='累计占比',
                line=dict(color='firebrick', width=3),
                marker=dict(size=8),
                yaxis='y',
                xaxis='x2'
            ))

            # 更新布局
            fig.update_layout(
                title="客户销售额排行TOP" + str(top_n),
                xaxis=dict(
                    title="销售额 (元)",
                    tickformat=",",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
                ),
                xaxis2=dict(
                    title="累计占比 (%)",
                    overlaying='x',
                    side='top',
                    range=[0, customer_sales['销售额'].max()],
                    showticklabels=False,
                    showgrid=False
                ),
                yaxis=dict(
                    title="客户",
                    autorange="reversed"  # 从上到下按销售额降序排列
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=120, r=60, t=80, b=60),
                plot_bgcolor='white',
                barmode='group',
                height=500
            )

            # 添加累计占比标签
            for i, row in customer_sales.iterrows():
                fig.add_annotation(
                    x=row['销售额'] * 1.05,
                    y=row[display_col],
                    text=f"{row['累计占比']:.1f}%",
                    showarrow=False,
                    font=dict(color='firebrick', size=10)
                )

            # 添加悬停信息
            hover_data = []
            for i, row in customer_sales.iterrows():
                order_count = orders[orders[customer_col] == row[customer_col]].shape[0]
                avg_order_value = row['销售额'] / order_count if order_count > 0 else 0

                # 收集该客户的产品信息
                customer_orders = orders[orders[customer_col] == row[customer_col]]
                top_products = []
                if '产品代码' in customer_orders.columns:
                    # 优先使用产品简称
                    product_name_col = '产品简称' if '产品简称' in customer_orders.columns else '产品名称' if '产品名称' in customer_orders.columns else '产品代码'

                    product_sales = customer_orders.groupby(['产品代码', product_name_col])[
                        '销售额'].sum().reset_index()
                    product_sales = product_sales.sort_values('销售额', ascending=False).head(3)
                    for _, prod in product_sales.iterrows():
                        top_products.append(f"{prod[product_name_col]}: {format_currency(prod['销售额'])}")

                info = (
                    f"销售额: {format_currency(row['销售额'])}<br>"
                    f"订单数: {order_count}<br>"
                    f"平均订单金额: {format_currency(avg_order_value)}<br>"
                    f"累计占比: {row['累计占比']:.1f}%<br>"
                )

                if top_products:
                    info += "<br><b>主要产品:</b><br>" + "<br>".join(top_products)

                hover_data.append(info)

            # 添加悬停模板
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>%{customdata}<extra></extra>',
                customdata=hover_data,
                selector=dict(type='bar')
            )

            return fig

        else:
            st.warning("找不到销售额列，无法创建客户销售额排行图表")
            return None

    except Exception as e:
        st.error(f"创建客户销售额排行图表时出错: {str(e)}")
        return None


# 创建客户目标达成率图表 - 改进版
def create_target_achievement_chart(data):
    """创建客户目标达成率图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty or customer_target.empty:
            st.warning("数据不足，无法创建客户目标达成率图表")
            return None

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称', '客户']:
            if col in orders.columns and col in customer_target.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return None

        # 准备月份数据
        if '发运月份' in orders.columns and '月份' in customer_target.columns:
            # 准备订单月份
            if not pd.api.types.is_datetime64_any_dtype(orders['发运月份']):
                orders['发运月份'] = pd.to_datetime(orders['发运月份'])

            orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()

            # 确保月份格式一致
            if not pd.api.types.is_datetime64_any_dtype(customer_target['月份']):
                customer_target['月份'] = pd.to_datetime(customer_target['月份'])

            # 汇总订单销售额
            if '销售额' in orders.columns:
                sales_monthly = orders.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

                # 合并目标数据
                merged = pd.merge(sales_monthly, customer_target, on=[customer_col, '月份'], how='inner')

                if not merged.empty and '月度指标' in merged.columns:
                    # 计算达成率
                    merged['达成率'] = (merged['销售额'] / merged['月度指标'] * 100).fillna(0)

                    # 标记达成状态
                    merged['达成状态'] = merged['达成率'].apply(
                        lambda x: '已达成' if x >= 100 else '未达成'
                    )

                    # 按月份和客户排序
                    merged = merged.sort_values(['月份', customer_col])

                    # 使用客户简称替代代码
                    if '客户简称' in orders.columns and customer_col != '客户简称':
                        customer_name_map = {}
                        for _, row in orders.drop_duplicates([customer_col, '客户简称']).iterrows():
                            customer_name_map[row[customer_col]] = row['客户简称']

                        if customer_name_map:
                            merged['客户简称'] = merged[customer_col].map(
                                lambda x: customer_name_map.get(x, x))
                            display_col = '客户简称'
                        else:
                            display_col = customer_col
                    else:
                        display_col = customer_col

                    # 准备透视表数据
                    pivot_data = merged.pivot_table(
                        values='达成率',
                        index='月份',
                        columns=display_col,
                        aggfunc='mean'
                    ).fillna(0)

                    # 限制客户数量，避免图表过于拥挤
                    max_customers = 15
                    if pivot_data.shape[1] > max_customers:
                        # 按平均达成率排序，选取最高和最低的客户
                        customer_avg = pivot_data.mean().sort_values(ascending=False)
                        top_customers = customer_avg.head(max_customers // 2).index
                        bottom_customers = customer_avg.tail(max_customers // 2).index
                        selected_customers = list(top_customers) + list(bottom_customers)
                        pivot_data = pivot_data[selected_customers]

                    # 创建改进的热力图
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_data.values,
                        x=pivot_data.columns,
                        y=[d.strftime('%Y-%m') for d in pivot_data.index],
                        colorscale=[
                            [0, 'rgb(165,0,38)'],  # 深红色 (0%)
                            [0.25, 'rgb(244,109,67)'],  # 浅红色 (25%)
                            [0.5, 'rgb(255,255,191)'],  # 黄色 (50%)
                            [0.75, 'rgb(116,173,209)'],  # 浅绿色 (75%)
                            [0.9, 'rgb(49,104,142)'],  # 深绿色 (90%)
                            [1, 'rgb(0,68,27)']  # 更深绿色 (100%+)
                        ],
                        colorbar=dict(
                            title="达成率 (%)",
                            titleside="right",
                            tickvals=[0, 25, 50, 75, 100, 150, 200],
                            ticktext=["0%", "25%", "50%", "75%", "100%", "150%", "200%+"],
                            ticks="outside",
                            thickness=15,
                            len=0.9
                        ),
                        hovertemplate='客户: %{x}<br>月份: %{y}<br>达成率: %{z:.1f}%<extra></extra>',
                        zauto=False,
                        zmin=0,
                        zmax=200,  # 限制最大值，避免极端值影响色彩显示
                    ))

                    # 更新布局
                    fig.update_layout(
                        title={
                            'text': '客户月度指标达成率分析',
                            'font': {'size': 20, 'color': '#1f3867'}
                        },
                        xaxis=dict(
                            title="客户",
                            tickangle=45,
                            tickfont={'size': 11},
                            gridcolor='lightgray'
                        ),
                        yaxis=dict(
                            title="月份",
                            tickfont={'size': 11},
                            gridcolor='lightgray',
                            autorange="reversed"  # 最新月份在上方
                        ),
                        margin=dict(l=80, r=80, t=80, b=120),
                        height=max(500, 400 + (pivot_data.shape[0] * 30)),  # 动态调整高度
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )

                    # 为热力图值添加文本注释
                    for i, month in enumerate(pivot_data.index):
                        for j, customer in enumerate(pivot_data.columns):
                            value = pivot_data.iloc[i, j]
                            # 为不同达成率使用不同颜色的文字
                            text_color = 'white' if value < 70 or value > 130 else 'black'

                            if not pd.isna(value):  # 确保值不是NaN
                                fig.add_annotation(
                                    x=customer,
                                    y=month.strftime('%Y-%m'),
                                    text=f"{value:.0f}%",
                                    showarrow=False,
                                    font=dict(size=9, color=text_color)
                                )

                    return fig

        st.warning("数据不足，无法创建客户目标达成率图表")
        return None

    except Exception as e:
        st.error(f"创建客户目标达成率图表时出错: {str(e)}")
        return None


# 创建客户趋势分析图 - 改进版
def create_customer_trend_chart(data):
    """创建客户趋势分析图"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            st.warning("数据不足，无法创建客户趋势分析图")
            return None

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '发运月份' not in orders.columns or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 确保发运月份是日期类型
        if not pd.api.types.is_datetime64_any_dtype(orders['发运月份']):
            orders['发运月份'] = pd.to_datetime(orders['发运月份'])

        # 按月份汇总客户数和销售额
        orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()
        monthly_stats = orders.groupby('月份').agg(
            客户数量=pd.NamedAgg(column=customer_col, aggfunc='nunique'),
            销售额=pd.NamedAgg(column='销售额', aggfunc='sum'),
            订单数=pd.NamedAgg(column=customer_col, aggfunc='count')
        ).reset_index()

        # 计算环比增长率
        monthly_stats['客户环比'] = monthly_stats['客户数量'].pct_change() * 100
        monthly_stats['销售额环比'] = monthly_stats['销售额'].pct_change() * 100
        monthly_stats['订单数环比'] = monthly_stats['订单数'].pct_change() * 100

        # 计算3月移动平均 - 如果有足够数据
        if len(monthly_stats) >= 3:
            monthly_stats['客户数量_MA3'] = monthly_stats['客户数量'].rolling(window=3).mean()
            monthly_stats['销售额_MA3'] = monthly_stats['销售额'].rolling(window=3).mean()

        # 创建更现代的图表
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加销售额面积图
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['销售额'],
                mode='lines',
                name='销售额',
                line=dict(width=0),
                fill='tozeroy',
                fillcolor='rgba(231, 107, 124, 0.2)',
                stackgroup='one',
                hovertemplate='销售额: %{y:,.0f}元<br>环比: %{text:.1f}%<extra></extra>',
                text=monthly_stats['销售额环比']
            ),
            secondary_y=True
        )

        # 添加销售额线
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['销售额'],
                mode='lines+markers',
                name='销售额',
                line=dict(color='rgba(231, 107, 124, 1)', width=3),
                marker=dict(size=8, color='rgba(231, 107, 124, 1)'),
                hovertemplate='销售额: %{y:,.0f}元<br>环比: %{text:.1f}%<extra></extra>',
                text=monthly_stats['销售额环比'],
                visible=True
            ),
            secondary_y=True
        )

        # 添加客户数量线
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['客户数量'],
                mode='lines+markers',
                name='客户数量',
                line=dict(color='rgba(58, 134, 255, 1)', width=3),
                marker=dict(size=8),
                hovertemplate='客户数量: %{y}<br>环比: %{text:.1f}%<extra></extra>',
                text=monthly_stats['客户环比']
            ),
            secondary_y=False
        )

        # 如果有足够数据，添加移动平均线
        if len(monthly_stats) >= 3:
            fig.add_trace(
                go.Scatter(
                    x=monthly_stats['月份'],
                    y=monthly_stats['客户数量_MA3'],
                    mode='lines',
                    name='客户数量(3月移动平均)',
                    line=dict(color='rgba(58, 134, 255, 0.5)', width=2, dash='dash'),
                    hovertemplate='3月移动平均: %{y:.1f}<extra></extra>'
                ),
                secondary_y=False
            )

            fig.add_trace(
                go.Scatter(
                    x=monthly_stats['月份'],
                    y=monthly_stats['销售额_MA3'],
                    mode='lines',
                    name='销售额(3月移动平均)',
                    line=dict(color='rgba(231, 107, 124, 0.5)', width=2, dash='dash'),
                    hovertemplate='3月移动平均: %{y:,.0f}元<extra></extra>'
                ),
                secondary_y=True
            )

        # 添加环比增长注释 - 仅在数据点不太密集时添加
        if len(monthly_stats) <= 12:  # 如果数据点少于或等于12个
            for i, row in monthly_stats.iterrows():
                if i > 0:  # 跳过第一个月，因为没有环比数据
                    # 客户环比标注
                    color = 'green' if row['客户环比'] >= 0 else 'red'
                    symbol = '▲' if row['客户环比'] >= 0 else '▼'
                    fig.add_annotation(
                        x=row['月份'],
                        y=row['客户数量'],
                        text=f"{symbol} {abs(row['客户环比']):.1f}%",
                        showarrow=False,
                        yshift=15,
                        font=dict(color=color, size=10)
                    )

                    # 销售额环比标注
                    color = 'green' if row['销售额环比'] >= 0 else 'red'
                    symbol = '▲' if row['销售额环比'] >= 0 else '▼'
                    fig.add_annotation(
                        x=row['月份'],
                        y=row['销售额'],
                        text=f"{symbol} {abs(row['销售额环比']):.1f}%",
                        showarrow=False,
                        yshift=15,
                        font=dict(color=color, size=10)
                    )

        # 更新轴标题和范围
        fig.update_xaxes(
            title_text="月份",
            tickangle=0,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray'
        )
        fig.update_yaxes(
            title_text="客户数量",
            secondary_y=False,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray'
        )
        fig.update_yaxes(
            title_text="销售额 (元)",
            tickformat=",",
            secondary_y=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray'
        )

        # 更新布局
        fig.update_layout(
            title={
                'text': "客户数量与销售额月度趋势",
                'font': {'size': 20, 'color': '#1f3867'}
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=60, t=80, b=60),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            height=550
        )

        return fig

    except Exception as e:
        st.error(f"创建客户趋势分析图表时出错: {str(e)}")
        return None


# 创建客户区域分布图 - 改进版
def create_customer_region_chart(data):
    """创建客户区域分布图"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty or '所属区域' not in orders.columns:
            st.warning("数据不足，无法创建客户区域分布图")
            return None

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 按区域统计客户数量和销售额
        region_stats = orders.groupby('所属区域').agg(
            客户数量=pd.NamedAgg(column=customer_col, aggfunc='nunique'),
            销售额=pd.NamedAgg(column='销售额', aggfunc='sum'),
            订单数=pd.NamedAgg(column=customer_col, aggfunc='count')
        ).reset_index()

        # 计算客户均销售额、客户均订单数等指标
        region_stats['客户均销售额'] = region_stats['销售额'] / region_stats['客户数量']
        region_stats['客户均订单数'] = region_stats['订单数'] / region_stats['客户数量']
        region_stats['订单均销售额'] = region_stats['销售额'] / region_stats['订单数']

        # 计算总销售额和总客户数
        total_sales = region_stats['销售额'].sum()
        total_customers = region_stats['客户数量'].sum()

        # 计算区域占比
        region_stats['销售额占比'] = region_stats['销售额'] / total_sales * 100
        region_stats['客户数占比'] = region_stats['客户数量'] / total_customers * 100

        # 按客户数量降序排序
        region_stats = region_stats.sort_values('客户数量', ascending=False)

        # 创建图表 - 使用现代化树形图和高级条形图
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "domain"}, {"type": "xy"}]],
            subplot_titles=("客户区域分布", "区域客户绩效对比"),
            column_widths=[0.4, 0.6]
        )

        # 添加树形图 - 客户区域分布
        fig.add_trace(
            go.Treemap(
                labels=region_stats['所属区域'],
                parents=[""] * len(region_stats),
                values=region_stats['客户数量'],
                hovertemplate='<b>%{label}</b><br>客户数量: %{value}<br>占比: %{percentRoot:.1f}%<extra></extra>',
                marker=dict(
                    colors=px.colors.qualitative.Pastel,
                    line=dict(width=1.5, color='white')
                ),
                textinfo="label+value",
                insidetextfont=dict(size=14)
            ),
            row=1, col=1
        )

        # 准备悬停信息
        hover_text = []
        for _, row in region_stats.iterrows():
            hover_text.append(
                f"区域: {row['所属区域']}<br>" +
                f"客户数量: {row['客户数量']} ({row['客户数占比']:.1f}%)<br>" +
                f"销售额: {format_currency(row['销售额'])} ({row['销售额占比']:.1f}%)<br>" +
                f"客户均销售额: {format_currency(row['客户均销售额'])}<br>" +
                f"客户均订单数: {row['客户均订单数']:.1f}<br>" +
                f"订单均销售额: {format_currency(row['订单均销售额'])}"
            )

        # 添加客户均销售额柱状图 - 带渐变色
        max_value = region_stats['客户均销售额'].max() * 1.1  # 留出10%的空间

        # 创建颜色渐变
        colors = px.colors.sequential.Viridis
        color_values = [colors[int(i / (len(region_stats) - 1 if len(region_stats) > 1 else 1) * (len(colors) - 1))]
                        for i in range(len(region_stats))]

        # 添加柱状图
        fig.add_trace(
            go.Bar(
                x=region_stats['所属区域'],
                y=region_stats['客户均销售额'],
                name="客户均销售额",
                marker_color=color_values,
                opacity=0.85,
                hovertext=hover_text,
                hovertemplate='%{hovertext}<extra></extra>',
                text=region_stats['客户均销售额'].apply(lambda x: f"{x:,.0f}"),
                textposition='auto',
                textfont=dict(size=11)
            ),
            row=1, col=2
        )

        # 添加客户数量点
        fig.add_trace(
            go.Scatter(
                x=region_stats['所属区域'],
                y=[max_value * 0.05] * len(region_stats),  # 放在底部作为点的位置
                mode='markers',
                name='客户数量',
                marker=dict(
                    symbol='circle',
                    size=region_stats['客户数量'] / region_stats['客户数量'].max() * 40 + 10,  # 根据客户数量调整大小
                    color='rgba(50, 171, 96, 0.7)',
                    line=dict(color='rgba(50, 171, 96, 1.0)', width=1)
                ),
                hovertext=hover_text,
                hovertemplate='%{hovertext}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )

        # 为每个气泡添加客户数量标签
        for i, row in region_stats.iterrows():
            fig.add_annotation(
                x=row['所属区域'],
                y=max_value * 0.05,  # 放在底部作为点的位置
                text=str(row['客户数量']),
                showarrow=False,
                font=dict(size=10, color="white"),
                row=1, col=2
            )

        # 更新布局
        fig.update_layout(
            title={
                'text': "客户区域分布与绩效分析",
                'font': {'size': 20, 'color': '#1f3867'}
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=80, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=600,
            showlegend=True
        )

        # 更新坐标轴
        fig.update_xaxes(
            title_text="区域",
            tickangle=0,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray',
            row=1, col=2
        )
        fig.update_yaxes(
            title_text="客户均销售额 (元)",
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray',
            row=1, col=2
        )

        return fig

    except Exception as e:
        st.error(f"创建客户区域分布图表时出错: {str(e)}")
        return None


# 创建客户产品偏好分析图 - 改进版
def create_customer_product_preference(data):
    """创建客户产品偏好分析图"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            st.warning("数据不足，无法创建客户产品偏好分析图")
            return None

        # 确保销售额列存在
        if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
            orders['销售额'] = orders['求和项:金额（元）']

        # 确定必要列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '产品代码' not in orders.columns or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 获取客户销售额排名
        customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
        customer_sales = customer_sales.sort_values('销售额', ascending=False)

        # 选取销售额前5的客户
        top_customers = customer_sales.head(5)[customer_col].tolist()

        # 为每个客户找出销售额前5的产品
        filtered_orders = orders[orders[customer_col].isin(top_customers)]

        # 使用客户简称显示（如果有）
        display_col = customer_col
        if '客户简称' in orders.columns and customer_col != '客户简称':
            customer_name_map = {}
            for _, row in orders.drop_duplicates([customer_col, '客户简称']).iterrows():
                customer_name_map[row[customer_col]] = row['客户简称']

            if customer_name_map:
                filtered_orders['显示名称'] = filtered_orders[customer_col].map(
                    lambda x: customer_name_map.get(x, x))
                display_col = '显示名称'

        # 创建产品偏好图
        # 优先使用产品简称显示
        product_col = '产品简称' if '产品简称' in filtered_orders.columns else '产品名称' if '产品名称' in filtered_orders.columns else '产品代码'

        # 客户-产品销售额透视表
        pivot_data = filtered_orders.pivot_table(
            values='销售额',
            index=display_col,
            columns=product_col,
            aggfunc='sum'
        ).fillna(0)

        # 如果产品太多，只保留每个客户销售额最高的5个产品
        if pivot_data.shape[1] > 15:  # 如果产品超过15个
            top_products_per_customer = {}
            for customer in pivot_data.index:
                customer_products = pivot_data.loc[customer].nlargest(5)
                for product in customer_products.index:
                    top_products_per_customer[product] = True

            # 只保留这些产品
            pivot_data = pivot_data[list(top_products_per_customer.keys())]

        # 计算每个客户的总销售额
        pivot_data['总销售额'] = pivot_data.sum(axis=1)

        # 按总销售额排序
        pivot_data = pivot_data.sort_values('总销售额', ascending=False)

        # 移除总销售额列
        pivot_data = pivot_data.drop(columns=['总销售额'])

        # 转换为百分比
        pivot_pct = pivot_data.copy()
        for customer in pivot_pct.index:
            total = pivot_pct.loc[customer].sum()
            pivot_pct.loc[customer] = pivot_pct.loc[customer] / total * 100 if total > 0 else 0

        # 准备热力图悬停文本
        hover_text = []
        for i, customer in enumerate(pivot_pct.index):
            customer_hover = []
            for j, product in enumerate(pivot_pct.columns):
                pct_value = pivot_pct.iloc[i, j]
                actual_value = pivot_data.iloc[i, j]

                if pct_value > 0:
                    customer_hover.append(
                        f"客户: {customer}<br>" +
                        f"产品: {product}<br>" +
                        f"销售额: {format_currency(actual_value)}<br>" +
                        f"占比: {pct_value:.1f}%"
                    )
                else:
                    customer_hover.append("")
            hover_text.append(customer_hover)

        # 为热力图准备自定义文本
        text_annotations = []
        for i, customer in enumerate(pivot_pct.index):
            for j, product in enumerate(pivot_pct.columns):
                pct_value = pivot_pct.iloc[i, j]
                if pct_value > 1:  # 只显示占比超过1%的值
                    text_annotations.append(f"{pct_value:.1f}%")
                else:
                    text_annotations.append("")

        # 重塑文本注释数组
        text_matrix = []
        for i in range(len(pivot_pct.index)):
            row = []
            for j in range(len(pivot_pct.columns)):
                idx = i * len(pivot_pct.columns) + j
                row.append(text_annotations[idx])
            text_matrix.append(row)

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=pivot_pct.values,
            x=pivot_pct.columns,
            y=pivot_pct.index,
            colorscale=[
                [0, 'rgb(255,255,255)'],  # 白色 (0%)
                [0.01, 'rgb(240,240,255)'],  # 极浅蓝 (1%)
                [0.1, 'rgb(200,200,255)'],  # 浅蓝 (10%)
                [0.3, 'rgb(130,130,255)'],  # 中蓝 (30%)
                [0.5, 'rgb(60,60,220)'],  # 深蓝 (50%)
                [0.7, 'rgb(0,0,180)'],  # 更深蓝 (70%)
                [1, 'rgb(0,0,120)']  # 深深蓝 (100%)
            ],
            colorbar=dict(
                title="销售占比 (%)",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0%", "25%", "50%", "75%", "100%"]
            ),
            hoverinfo="text",
            text=hover_text,
            zauto=True,
        ))

        # 添加占比文本标签
        for i, customer in enumerate(pivot_pct.index):
            for j, product in enumerate(pivot_pct.columns):
                pct_value = pivot_pct.iloc[i, j]
                if pct_value > 5:  # 只显示主要占比
                    text_color = 'white' if pct_value > 25 else 'black'
                    fig.add_annotation(
                        x=product,
                        y=customer,
                        text=f"{pct_value:.1f}%",
                        showarrow=False,
                        font=dict(color=text_color, size=10)
                    )

        # 更新布局
        fig.update_layout(
            title={
                'text': '主要客户产品偏好分析（销售额占比）',
                'font': {'size': 20, 'color': '#1f3867'}
            },
            xaxis=dict(
                title="产品",
                tickangle=45
            ),
            yaxis=dict(
                title="客户"
            ),
            margin=dict(l=100, r=50, t=80, b=120),
            height=500,  # 固定高度
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        return fig

    except Exception as e:
        st.error(f"创建客户产品偏好分析图表时出错: {str(e)}")
        return None


# 创建可点击卡片
def create_clickable_metric_card(header, value, description, trend=None, trend_value=None, card_id=None,
                                 target_tab=None):
    """创建可点击的指标卡片，点击后跳转到指定标签页"""
    # 确定趋势类型和标签
    trend_class = ""
    trend_symbol = ""

    if trend:
        if trend == "up":
            trend_class = "trend-up"
            trend_symbol = "▲"
        elif trend == "down":
            trend_class = "trend-down"
            trend_symbol = "▼"

    # 构建趋势文本
    trend_html = ""
    if trend and trend_value is not None:
        trend_html = f'<p class="card-trend {trend_class}">{trend_symbol} {abs(trend_value):.1f}%</p>'

    # 构建点击事件
    onclick = ""
    if card_id and target_tab is not None:
        onclick = f"onclick=\"storeActiveTab('{card_id}', {target_tab})\""

    # 构建卡片HTML
    card_html = f"""
    <div class="metric-card" id="{card_id}" {onclick}>
        <p class="card-header">{header}</p>
        <p class="card-value">{value}</p>
        <p class="card-text">{description}</p>
        {trend_html}
    </div>
    """

    return card_html


# 主程序部分
# 加载数据 - 使用自定义函数
data = load_data_files()

# 确保所有必要的数据都已加载
if 'sales_orders' not in data or data['sales_orders'].empty:
    st.error("无法加载销售订单数据，请检查数据源")
    st.stop()

# 确保销售额列存在
if '销售额' not in data['sales_orders'].columns and '求和项:金额（元）' in data['sales_orders'].columns:
    data['sales_orders']['销售额'] = data['sales_orders']['求和项:金额（元）']

# 应用筛选器 - 使用专用筛选器
filtered_data = create_customer_filters(data)

# 用于标签页导航的JavaScript
st.markdown("""
<script>
function storeActiveTab(cardId, tabIndex) {
    // 将选中的标签索引存储到localStorage
    localStorage.setItem('activeTab', tabIndex);
    // 提交表单以触发页面刷新
    window.location.href = window.location.pathname + '?tab=' + tabIndex;
}

// 页面加载时检查URL参数或localStorage中的标签索引
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    let tabIndex = urlParams.get('tab');

    if (!tabIndex && localStorage.getItem('activeTab')) {
        tabIndex = localStorage.getItem('activeTab');
    }

    if (tabIndex !== null) {
        // 找到所有标签按钮
        const tabButtons = document.querySelectorAll('[data-baseweb="tab"]');
        if (tabButtons.length > tabIndex) {
            // 点击对应的标签按钮
            tabButtons[tabIndex].click();
        }
    }
});
</script>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-header">客户分析仪表盘</div>', unsafe_allow_html=True)

# 计算关键指标
kpis = calculate_customer_kpis(filtered_data)

# 创建标签页
tab_names = ["📊 客户概览", "🔍 客户详情分析", "📈 客户趋势", "🌐 区域分析"]
tabs = st.tabs(tab_names)

# 从URL或会话状态获取活动标签索引
active_tab = st.session_state.get('active_tab', 0)

# 客户概览标签
with tabs[0]:
    # 核心指标卡片行
    st.markdown('<div class="section-header">🔑 核心客户指标</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # 客户总数
        st.markdown(
            create_clickable_metric_card(
                header="客户总数",
                value=format_number(kpis.get('total_customers', 0)),
                description="活跃交易客户数量",
                trend="up" if kpis.get('customer_count_growth', 0) > 0 else "down" if kpis.get('customer_count_growth',
                                                                                               0) < 0 else None,
                trend_value=kpis.get('customer_count_growth', 0) * 100 if kpis.get(
                    'customer_count_growth') is not None else None,
                card_id="total_customers_card",
                target_tab=2  # 点击后跳转到"客户趋势"标签
            ),
            unsafe_allow_html=True
        )

    with col2:
        # TOP客户贡献
        top_count = kpis.get('top_customers_count', 0)
        top_contribution = kpis.get('top_customers_contribution', 0) * 100
        st.markdown(
            create_clickable_metric_card(
                header="TOP客户贡献",
                value=f"{top_contribution:.1f}%",
                description=f"TOP {top_count} 客户销售占比",
                card_id="top_customers_card",
                target_tab=1  # 点击后跳转到"客户详情分析"标签
            ),
            unsafe_allow_html=True
        )

    with col3:
        # 客户目标达成率
        st.markdown(
            create_clickable_metric_card(
                header="目标达成率",
                value=format_percentage(kpis.get('target_achievement_rate', 0)),
                description=f"{kpis.get('target_achievement_count', 0)}/{kpis.get('target_total_count', 0)} 客户达成目标",
                card_id="target_achievement_card",
                target_tab=1  # 点击后跳转到"客户详情分析"标签
            ),
            unsafe_allow_html=True
        )

    with col4:
        # 客户均销售额
        st.markdown(
            create_clickable_metric_card(
                header="客户均销售额",
                value=format_currency(kpis.get('avg_customer_sales', 0)),
                description="平均每客户贡献",
                trend="up" if kpis.get('sales_growth', 0) > 0 else "down" if kpis.get('sales_growth', 0) < 0 else None,
                trend_value=kpis.get('sales_growth', 0) * 100 if kpis.get('sales_growth') is not None else None,
                card_id="avg_customer_sales_card",
                target_tab=3  # 点击后跳转到"区域分析"标签
            ),
            unsafe_allow_html=True
        )

    # 客户销售额排行
    st.markdown('<div class="section-header">📊 客户销售贡献分析</div>', unsafe_allow_html=True)
    top_customers_fig = create_top_customers_chart(filtered_data)
    if top_customers_fig:
        st.plotly_chart(top_customers_fig, use_container_width=True)

        # 添加图表解释
        top_customers_explanation = """
        <b>图表解读：</b> 此图展示了销售额最高的客户排名及其累计销售占比。条形图长度表示每个客户的销售额，颜色深浅也与销售额相关。
        右侧红色百分比展示每个客户的累计销售贡献，可快速识别关键客户所占销售比例。悬停查看客户详情包括订单数、平均订单金额和主要产品。
        通过此图可识别核心客户群体，优化客户关系管理策略，合理分配销售资源。
        """
        add_chart_explanation(top_customers_explanation)
    else:
        st.warning("无法生成客户销售额排行图表，请检查数据或筛选条件。")

    # 客户区域分布简要概览
    st.markdown('<div class="section-header">🌐 客户区域分布概览</div>', unsafe_allow_html=True)
    region_fig = create_customer_region_chart(filtered_data)
    if region_fig:
        st.plotly_chart(region_fig, use_container_width=True)

        # 添加图表解释
        region_explanation = """
        <b>图表解读：</b> 左侧树形图直观展示不同区域的客户数量分布，方块大小表示客户数量。右侧图表对比各区域的客户均销售额(柱状图)
        和客户数量(圆圈大小)，从而展示不同区域的客户价值和密度。通过对比可发现高价值区域与高密度区域是否一致，
        辅助制定区域市场策略和资源分配。悬停在区域上可查看详细指标数据。
        """
        add_chart_explanation(region_explanation)
    else:
        st.warning("无法生成客户区域分布图表，请检查数据或筛选条件。")

# 客户详情分析标签
with tabs[1]:
    # 客户目标达成率热力图
    st.markdown('<div class="section-header">📊 客户目标达成分析</div>', unsafe_allow_html=True)
    target_achievement_fig = create_target_achievement_chart(filtered_data)
    if target_achievement_fig:
        st.plotly_chart(target_achievement_fig, use_container_width=True)

        # 添加图表解释
        target_explanation = """
        <b>图表解读：</b> 此热力图展示了各客户月度销售目标的达成情况。颜色从红色(低达成率)到蓝色再到绿色(高达成率)，直观展示客户业绩表现。
        深绿色区域表示目标超额完成的客户和月份，深红色区域表示亟需关注的客户和时期。通过分析热力图模式，可识别客户的季节性表现差异、
        稳定性强弱，以及整体目标设置的合理性。数字标签显示具体达成百分比，便于精准评估。
        """
        add_chart_explanation(target_explanation)
    else:
        st.info("无法生成客户目标达成率图表，可能是因为缺少客户目标数据或当前筛选条件下没有匹配的数据。")

    # 客户产品偏好分析
    st.markdown('<div class="section-header">🛒 客户产品偏好分析</div>', unsafe_allow_html=True)
    preference_fig = create_customer_product_preference(filtered_data)
    if preference_fig:
        st.plotly_chart(preference_fig, use_container_width=True)

        # 添加图表解释
        preference_explanation = """
        <b>图表解读：</b> 此热力图展示了主要客户对不同产品的偏好程度，颜色深浅和数字标签表示产品销售额在该客户总购买中的占比。
        横向查看可分析单个客户的产品购买结构和集中度，纵向查看可比较不同客户对同一产品的偏好差异。
        深蓝色区域表示客户高度依赖的核心产品，可用于识别客户购买模式、评估产品组合策略有效性，并针对不同客户特性制定差异化的产品推荐和促销方案。
        """
        add_chart_explanation(preference_explanation)
    else:
        st.warning("无法生成客户产品偏好分析图表，请检查数据或筛选条件。")

# 客户趋势标签
with tabs[2]:
    # 客户趋势分析
    st.markdown('<div class="section-header">📈 客户趋势分析</div>', unsafe_allow_html=True)
    trend_fig = create_customer_trend_chart(filtered_data)
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)

        # 添加图表解释
        trend_explanation = """
        <b>图表解读：</b> 此图展示了客户数量(蓝线)和销售额(红区域)的月度变化趋势。虚线表示3个月移动平均值，平滑短期波动，
        便于观察长期趋势。环比增长率标注在每个数据点上，绿色箭头表示增长，红色箭头表示下降。
        通过分析客户数与销售额的相关性和时间变化模式，可评估客户开发与销售策略的有效性，识别季节性因素影响，
        并预测未来趋势，为销售和市场策略调整提供依据。
        """
        add_chart_explanation(trend_explanation)
    else:
        st.warning("无法生成客户趋势分析图表，请检查数据或筛选条件。")

# 区域分析标签
with tabs[3]:
    # 客户区域分布
    st.markdown('<div class="section-header">🗺️ 客户区域分布详细分析</div>', unsafe_allow_html=True)
    region_fig = create_customer_region_chart(filtered_data)
    if region_fig:
        st.plotly_chart(region_fig, use_container_width=True)

        # 添加图表解释
        region_explanation = """
        <b>图表解读：</b> 左侧树形图展示各区域客户数量分布及占比，区块大小直观反映客户集中度。
        右侧图表对比各区域的客户均销售额(柱状图)和客户数量(圆圈大小)，颜色渐变表示客户价值高低。
        通过区域客户密度与客户价值的对比分析，可发现高价值区域与客户密集区域的匹配情况，为区域资源分配、
        市场开发策略和销售团队部署提供决策依据。悬停可查看各区域的详细指标，包括销售占比、订单数等关键数据。
        """
        add_chart_explanation(region_explanation)
    else:
        st.warning("无法生成客户区域分布图表，请检查数据或筛选条件。")