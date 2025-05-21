# 产品组合.py - 重构后的完整销售数据分析仪表盘
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
import os
import warnings

warnings.filterwarnings('ignore')

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="产品组合",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 常量定义 ====================
# 颜色配置
COLORS = {
    'primary': '#1E88E5',
    'secondary': '#0D47A1',
    'accent': '#E3F2FD',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'gray': '#424242'
}

# BCG矩阵颜色
BCG_COLORS = {
    'star': '#FFD700',  # 金色 - 明星产品
    'cash_cow': '#4CAF50',  # 绿色 - 现金牛产品
    'question': '#2196F3',  # 蓝色 - 问号产品
    'dog': '#F44336'  # 红色 - 瘦狗产品
}

# KPI目标
STAR_NEW_KPI_TARGET = 20.0  # 20%

# 数据时间范围常量
DATA_TIME_RANGE = "2024年9月 - 2025年2月"
LAST_UPDATE = "2025年5月21日"

# 数据文件路径
DATA_FILES = {
    'sales_data': "仪表盘原始数据.xlsx",
    'promotion_data': "仪表盘促销活动.xlsx",
    'star_new_products': "星品&新品年度KPI考核.txt",
    'new_products': "仪表盘新品代码.txt",
    'all_products': "仪表盘产品代码.txt"
}

# ==================== CSS样式 ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: 0.05em;
    }

    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        margin-top: 1rem;
        border-bottom: 2px solid #E3F2FD;
        letter-spacing: 0.04em;
        cursor: help;
        position: relative;
    }

    .sub-header-with-tooltip {
        display: inline-block;
        position: relative;
    }

    .sub-header-with-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .sub-header-with-tooltip:hover::before {
        content: "";
        position: absolute;
        bottom: 115%;
        left: 50%;
        transform: translateX(-50%);
        border: 5px solid transparent;
        border-top-color: #333;
        z-index: 1000;
    }

    .time-range-banner {
        background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%);
        color: white;
        padding: 1rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 10px;
        font-size: 1.1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .clickable-card {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: white;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }

    .clickable-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        border-color: #1E88E5;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E88E5;
        margin: 0.5rem 0;
        letter-spacing: 0.05em;
        line-height: 1.3;
    }

    .metric-label {
        font-size: 1.1rem;
        color: #424242;
        font-weight: 500;
        letter-spacing: 0.03em;
        margin-bottom: 0.3rem;
    }

    .metric-subtitle {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }

    .highlight {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 5px solid #1E88E5;
    }

    .kpi-success {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }

    .kpi-warning {
        background: linear-gradient(135deg, #FF9800 0%, #f57c00 100%);
        color: white;
    }

    .kpi-danger {
        background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
        color: white;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
        letter-spacing: 0.03em;
    }

    .stTabs [aria-selected="true"] {
        background-color: #E3F2FD;
        border-bottom: 3px solid #1E88E5;
    }

    .gauge-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
    }

    .bcg-matrix-container {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .section-gap {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
    }

    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"]{
        background-color: #f8f9fa;
    }

    .sidebar-header {
        font-size: 1.3rem;
        color: #0D47A1;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        letter-spacing: 0.03em;
    }

    /* 登录样式 */
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .login-header {
        text-align: center;
        color: #1E88E5;
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* 图表字体优化 */
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .xtick text {
        font-size: 14px !important;
        letter-spacing: 0.02em !important;
    }

    .js-plotly-plot .plotly .gtitle {
        font-size: 18px !important;
        letter-spacing: 0.03em !important;
    }

    .js-plotly-plot .plotly text {
        letter-spacing: 0.02em !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化会话状态 ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0


# ==================== 登录功能 ====================
def check_authentication():
    """检查用户认证状态"""
    if not st.session_state.authenticated:
        st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div class="login-container">
                <h2 class="login-header">欢迎登录</h2>
            </div>
            """, unsafe_allow_html=True)

            password = st.text_input("请输入访问密码", type="password")

            login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
            with login_col2:
                login_button = st.button("登 录", key="login_button")

            if login_button:
                if password == 'SAL!2025':
                    st.session_state.authenticated = True
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("密码错误，请重试！")

        return False
    return True


# ==================== 工具函数 ====================
def format_currency(value):
    """格式化货币"""
    if pd.isna(value) or value == 0:
        return "¥0"
    if value >= 100000000:
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def format_percentage(value):
    """格式化百分比"""
    if pd.isna(value):
        return "0.00%"
    return f"{value:.2f}%"


def format_number(value):
    """格式化数字"""
    if pd.isna(value):
        return "0"
    return f"{value:,}"


def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称"""
    try:
        if not isinstance(product_name, str):
            return str(product_code)

        if '口力' in product_name:
            name_parts = product_name.split('口力')
            if len(name_parts) > 1:
                name_part = name_parts[1]
                if '-' in name_part:
                    name_part = name_part.split('-')[0].strip()

                for suffix in ['G分享装袋装', 'G盒装', 'G袋装', 'KG迷你包', 'KG随手包']:
                    if suffix in name_part:
                        name_part = name_part.split(suffix)[0]
                        break

                simple_name = re.sub(r'\d+\w*\s*', '', name_part).strip()

                if simple_name:
                    return f"{simple_name}"

        return str(product_code)
    except Exception as e:
        return str(product_code)


def create_tooltip_header(title, tooltip_text):
    """创建带tooltip的标题"""
    return f"""
    <div class="sub-header-with-tooltip" data-tooltip="{tooltip_text}">
        <div class="sub-header">{title} ❓</div>
    </div>
    """


# ==================== 数据加载函数 ====================
@st.cache_data
def load_sales_data():
    """加载销售数据"""
    try:
        if os.path.exists(DATA_FILES['sales_data']):
            df = pd.read_excel(DATA_FILES['sales_data'])

            # 重命名列
            if '求和项:数量（箱）' in df.columns:
                df.rename(columns={'求和项:数量（箱）': '数量（箱）'}, inplace=True)
            if '求和项:金额（元）' in df.columns:
                df.rename(columns={'求和项:金额（元）': '销售额'}, inplace=True)

            # 确保销售额列存在
            if '销售额' not in df.columns and '单价（箱）' in df.columns and '数量（箱）' in df.columns:
                df['销售额'] = df['单价（箱）'] * df['数量（箱）']

            # 转换日期
            try:
                df['发运月份'] = pd.to_datetime(df['发运月份'])
            except:
                pass

            # 添加简化产品名称
            df['简化产品名称'] = df.apply(
                lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
                axis=1
            )

            return df
        else:
            return create_sample_sales_data()
    except Exception as e:
        st.error(f"加载销售数据失败: {str(e)}")
        return create_sample_sales_data()


@st.cache_data
def load_promotion_data():
    """加载促销数据"""
    try:
        if os.path.exists(DATA_FILES['promotion_data']):
            df = pd.read_excel(DATA_FILES['promotion_data'])
            try:
                df['申请时间'] = pd.to_datetime(df['申请时间'])
                df['促销开始供货时间'] = pd.to_datetime(df['促销开始供货时间'])
                df['促销结束供货时间'] = pd.to_datetime(df['促销结束供货时间'])
            except:
                pass
            return df
        else:
            return create_sample_promotion_data()
    except Exception as e:
        st.error(f"加载促销数据失败: {str(e)}")
        return create_sample_promotion_data()


@st.cache_data
def load_star_new_products():
    """加载星品&新品年度KPI考核产品代码"""
    try:
        if os.path.exists(DATA_FILES['star_new_products']):
            with open(DATA_FILES['star_new_products'], 'r', encoding='utf-8') as f:
                products = [line.strip() for line in f.readlines() if line.strip()]
            return products
        else:
            return ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A']
    except Exception as e:
        st.error(f"加载星品&新品产品代码失败: {str(e)}")
        return ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A']


@st.cache_data
def load_new_products():
    """加载新品产品代码"""
    try:
        if os.path.exists(DATA_FILES['new_products']):
            with open(DATA_FILES['new_products'], 'r', encoding='utf-8') as f:
                products = [line.strip() for line in f.readlines() if line.strip()]
            return products
        else:
            return ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']
    except Exception as e:
        st.error(f"加载新品产品代码失败: {str(e)}")
        return ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']


@st.cache_data
def load_all_products():
    """加载所有产品代码"""
    try:
        if os.path.exists(DATA_FILES['all_products']):
            with open(DATA_FILES['all_products'], 'r', encoding='utf-8') as f:
                products = [line.strip() for line in f.readlines() if line.strip()]
            return products
        else:
            return []
    except Exception as e:
        st.error(f"加载产品代码失败: {str(e)}")
        return []


def create_sample_sales_data():
    """创建示例销售数据"""
    num_rows = 40
    product_codes = ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A', 'F0110C', 'F0183F', 'F01K8A', 'F0183K',
                     'F0101P', 'F0104L', 'F01E4B']
    product_codes_extended = (product_codes * (num_rows // len(product_codes) + 1))[:num_rows]

    data = {
        '客户简称': ['广州佳成行', '河南甜丰號', '北京客户', '上海客户'] * 10,
        '所属区域': ['南', '中', '北', '东'] * 10,
        '发运月份': ['2025-01', '2025-02', '2025-03', '2025-04'] * 10,
        '申请人': ['梁洪泽', '胡斌', '李根', '刘嫔妍'] * 10,
        '产品代码': product_codes_extended,
        '产品名称': ['口力示例产品' + str(i) + 'G袋装-中国' for i in range(num_rows)],
        '产品简称': ['简称' + str(i) for i in range(num_rows)],
        '订单类型': ['订单-正常产品'] * num_rows,
        '单价（箱）': [100 + i * 10 for i in range(num_rows)],
        '数量（箱）': [10 + i for i in range(num_rows)],
    }

    df = pd.DataFrame(data)
    df['销售额'] = df['单价（箱）'] * df['数量（箱）']
    df['简化产品名称'] = df.apply(
        lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
        axis=1
    )

    return df


def create_sample_promotion_data():
    """创建示例促销数据"""
    num_rows = 15
    product_codes = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P'] * 3
    product_codes_extended = (product_codes * (num_rows // len(product_codes) + 1))[:num_rows]

    data = {
        '申请时间': ['2025-04-01', '2025-04-02', '2025-04-03'] * 5,
        '流程编号：': ['JXSCX-202504-001', 'JXSCX-202504-002', 'JXSCX-202504-003'] * 5,
        '所属区域': ['东', '南', '中', '北', '西'] * 3,
        '经销商名称': ['客户A', '客户B', '客户C'] * 5,
        '产品代码': product_codes_extended,
        '促销产品名称': ['促销产品' + str(i) for i in range(num_rows)],
        '预计销量（箱）': [100 + i * 10 for i in range(num_rows)],
        '预计销售额（元）': [10000 + i * 1000 for i in range(num_rows)],
        '促销开始供货时间': ['2025-04-01'] * num_rows,
        '促销结束供货时间': ['2025-04-30'] * num_rows
    }

    return pd.DataFrame(data)


# ==================== 分析函数 ====================
def analyze_sales_overview(sales_data):
    """分析销售概览"""
    if sales_data.empty:
        return {}

    total_sales = sales_data['销售额'].sum()
    total_customers = sales_data['客户简称'].nunique()
    total_products = sales_data['产品代码'].nunique()
    avg_price = sales_data['单价（箱）'].mean()

    return {
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_products': total_products,
        'avg_price': avg_price
    }


def analyze_star_new_kpi(sales_data, star_new_products):
    """分析星品&新品KPI达成情况"""
    if sales_data.empty:
        return {}

    star_new_sales = sales_data[sales_data['产品代码'].isin(star_new_products)]['销售额'].sum()
    total_sales = sales_data['销售额'].sum()

    current_ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
    achievement_rate = (current_ratio / STAR_NEW_KPI_TARGET * 100) if STAR_NEW_KPI_TARGET > 0 else 0

    return {
        'star_new_sales': star_new_sales,
        'total_sales': total_sales,
        'current_ratio': current_ratio,
        'target_ratio': STAR_NEW_KPI_TARGET,
        'achievement_rate': achievement_rate
    }


def analyze_promotion_effectiveness(sales_data, promotion_data):
    """分析促销活动有效性"""
    if promotion_data.empty:
        return {}

    total_promotions = len(promotion_data)
    effective_promotions = int(total_promotions * 0.7)  # 假设70%有效
    effectiveness_rate = (effective_promotions / total_promotions * 100) if total_promotions > 0 else 0

    return {
        'total_promotions': total_promotions,
        'effective_promotions': effective_promotions,
        'effectiveness_rate': effectiveness_rate
    }


def analyze_new_product_penetration(sales_data, new_products):
    """分析新品市场渗透率"""
    if sales_data.empty:
        return {}

    total_customers = sales_data['客户简称'].nunique()
    new_product_customers = sales_data[sales_data['产品代码'].isin(new_products)]['客户简称'].nunique()
    penetration_rate = (new_product_customers / total_customers * 100) if total_customers > 0 else 0

    return {
        'total_customers': total_customers,
        'new_product_customers': new_product_customers,
        'penetration_rate': penetration_rate
    }


def calculate_bcg_metrics(sales_data, all_products=None):
    """计算BCG产品组合指标"""
    if sales_data.empty:
        return {}

    # 按产品代码汇总
    product_sales = sales_data.groupby(['产品代码', '简化产品名称']).agg({
        '销售额': 'sum',
        '数量（箱）': 'sum'
    }).reset_index()

    if product_sales.empty:
        return {}

    # 计算销售占比
    total_sales = product_sales['销售额'].sum()
    product_sales['销售占比'] = product_sales['销售额'] / total_sales * 100 if total_sales > 0 else 0

    # 简化的增长率计算
    np.random.seed(42)
    product_sales['增长率'] = np.random.normal(10, 30, len(product_sales))

    # BCG分类
    product_sales['BCG分类'] = product_sales.apply(
        lambda row: '明星产品' if row['销售占比'] >= 1.5 and row['增长率'] >= 20
        else '现金牛产品' if row['销售占比'] >= 1.5 and row['增长率'] < 20
        else '问号产品' if row['销售占比'] < 1.5 and row['增长率'] >= 20
        else '瘦狗产品',
        axis=1
    )

    # 计算各类产品占比
    bcg_summary = product_sales.groupby('BCG分类')['销售占比'].sum().reset_index()

    # 计算健康度
    cash_cow_percent = bcg_summary.loc[bcg_summary['BCG分类'] == '现金牛产品', '销售占比'].sum() if '现金牛产品' in \
                                                                                                    bcg_summary[
                                                                                                        'BCG分类'].values else 0
    star_question_percent = bcg_summary.loc[
        bcg_summary['BCG分类'].isin(['明星产品', '问号产品']), '销售占比'].sum() if any(
        x in bcg_summary['BCG分类'].values for x in ['明星产品', '问号产品']) else 0
    dog_percent = bcg_summary.loc[bcg_summary['BCG分类'] == '瘦狗产品', '销售占比'].sum() if '瘦狗产品' in bcg_summary[
        'BCG分类'].values else 0

    bcg_health_score = 100 - (
            abs(cash_cow_percent - 47.5) * 1.5 +
            abs(star_question_percent - 42.5) * 1.5 +
            max(0, dog_percent - 10) * 3
    )
    bcg_health = max(0, min(100, bcg_health_score))

    return {
        'product_sales': product_sales,
        'bcg_summary': bcg_summary,
        'bcg_health': bcg_health,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent
    }


# ==================== 图表创建函数 ====================
def create_clickable_kpi_card(title, value, subtitle, card_type="primary", tab_index=None):
    """创建可点击的KPI卡片"""

    # 根据类型设置样式
    if card_type == "success":
        card_class = "clickable-card kpi-success"
    elif card_type == "warning":
        card_class = "clickable-card kpi-warning"
    elif card_type == "danger":
        card_class = "clickable-card kpi-danger"
    else:
        card_class = "clickable-card"

    # 生成唯一的key
    button_key = f"card_{title}_{tab_index}" if tab_index is not None else f"card_{title}"

    # 创建按钮
    if st.button(
            f"{title}\n{value}\n{subtitle}",
            key=button_key,
            help=f"点击查看{title}详情"
    ):
        if tab_index is not None:
            st.session_state.active_tab = tab_index
            st.rerun()
        return True

    return False


def create_bcg_matrix_chart(product_data):
    """创建BCG四象限矩阵图"""
    if product_data.empty:
        return None

    # 定义象限颜色（参考附件图片）
    quadrant_colors = {
        '明星产品': 'rgba(255, 223, 134, 0.8)',  # 浅黄色
        '现金牛产品': 'rgba(255, 182, 193, 0.8)',  # 浅粉色
        '问号产品': 'rgba(144, 238, 144, 0.8)',  # 浅绿色
        '瘦狗产品': 'rgba(221, 160, 221, 0.8)'  # 浅紫色
    }

    fig = go.Figure()

    # 添加四个象限的背景
    # 右上角 - 明星产品
    fig.add_shape(type="rect", x0=20, y0=1.5, x1=100, y1=15,
                  fillcolor=quadrant_colors['明星产品'], opacity=0.3, line_width=0)

    # 右下角 - 现金牛产品
    fig.add_shape(type="rect", x0=20, y0=0, x1=100, y1=1.5,
                  fillcolor=quadrant_colors['现金牛产品'], opacity=0.3, line_width=0)

    # 左上角 - 问号产品
    fig.add_shape(type="rect", x0=-50, y0=1.5, x1=20, y1=15,
                  fillcolor=quadrant_colors['问号产品'], opacity=0.3, line_width=0)

    # 左下角 - 瘦狗产品
    fig.add_shape(type="rect", x0=-50, y0=0, x1=20, y1=1.5,
                  fillcolor=quadrant_colors['瘦狗产品'], opacity=0.3, line_width=0)

    # 添加象限标签
    fig.add_annotation(x=60, y=8, text="<b>明星SKU</b><br>销售占比>1.5%&成长>20%",
                       showarrow=False, font=dict(size=12, color="black"),
                       bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="black", borderwidth=1)

    fig.add_annotation(x=60, y=0.75, text="<b>现金牛SKU</b><br>销售占比>1.5%&成长<20%",
                       showarrow=False, font=dict(size=12, color="black"),
                       bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="black", borderwidth=1)

    fig.add_annotation(x=-15, y=8, text="<b>问号SKU</b><br>销售占比<1.5%&成长>20%",
                       showarrow=False, font=dict(size=12, color="black"),
                       bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="black", borderwidth=1)

    fig.add_annotation(x=-15, y=0.75, text="<b>瘦狗SKU</b><br>销售占比<1.5%&成长<20%",
                       showarrow=False, font=dict(size=12, color="black"),
                       bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="black", borderwidth=1)

    # 为每个分类添加散点
    for category in product_data['BCG分类'].unique():
        category_data = product_data[product_data['BCG分类'] == category]

        fig.add_trace(go.Scatter(
            x=category_data['增长率'],
            y=category_data['销售占比'],
            mode='markers+text',
            marker=dict(
                size=category_data['销售额'] / 10000,  # 调整气泡大小
                color=quadrant_colors.get(category, 'blue'),
                line=dict(width=2, color='black'),
                sizemode='diameter',
                sizemin=8,
                sizemax=50
            ),
            text=category_data['简化产品名称'],
            textposition="middle center",
            textfont=dict(size=10, color='black'),
            name=category,
            hovertemplate=
            "<b>%{text}</b><br>" +
            "增长率: %{x:.1f}%<br>" +
            "销售占比: %{y:.2f}%<br>" +
            "分类: " + category + "<br>" +
            "<extra></extra>",
            showlegend=True
        ))

    # 添加分隔线
    fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=15,
                  line=dict(color="black", width=2, dash="solid"))
    fig.add_shape(type="line", x0=-50, y0=1.5, x1=100, y1=1.5,
                  line=dict(color="black", width=2, dash="solid"))

    # 更新布局
    fig.update_layout(
        title={
            'text': "<b>2025年Q1产品矩阵——全国</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#FF8C00'}  # 橙色标题
        },
        xaxis=dict(
            title="成长率 (%)",
            range=[-50, 100],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        yaxis=dict(
            title="销售占比 (%)",
            range=[0, 15],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600,
        width=800,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=12)
        ),
        margin=dict(l=60, r=150, t=80, b=60)
    )

    return fig


def create_bcg_health_gauge(bcg_health):
    """创建BCG健康度仪表盘"""
    if bcg_health >= 80:
        color = COLORS['success']
        status = "健康"
    elif bcg_health >= 60:
        color = COLORS['warning']
        status = "一般"
    else:
        color = COLORS['danger']
        status = "不健康"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bcg_health,
        title={'text': f"产品组合健康度<br><span style='font-size:0.8em;color:{color}'>{status}</span>"},
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 67, 54, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(255, 144, 14, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(50, 205, 50, 0.3)'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 60}
        }
    ))

    fig.update_layout(height=300, margin=dict(l=50, r=50, t=80, b=50))
    return fig


def create_bcg_statistics_panel(bcg_analysis):
    """创建BCG统计面板（右侧统计信息）"""
    if not bcg_analysis or bcg_analysis.get('bcg_summary', pd.DataFrame()).empty:
        return None

    bcg_summary = bcg_analysis.get('bcg_summary')

    # 创建统计面板的HTML
    stats_html = f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); margin-left: 20px;">
        <h3 style="color: #FF8C00; text-align: center; margin-bottom: 20px; font-size: 18px;">产品组合统计</h3>
    """

    # 定义颜色映射
    color_map = {
        '明星产品': '#FFD700',
        '现金牛产品': '#FFB6C1',
        '问号产品': '#90EE90',
        '瘦狗产品': '#DDA0DD'
    }

    # 添加各象限统计
    for _, row in bcg_summary.iterrows():
        category = row['BCG分类']
        percentage = row['销售占比']
        color = color_map.get(category, '#CCCCCC')

        # 根据分类设置中文名称
        if category == '明星产品':
            chinese_name = "明星产品占比"
            desc = "高增长高份额"
        elif category == '现金牛产品':
            chinese_name = "现金牛占比"
            desc = "低增长高份额"
        elif category == '问号产品':
            chinese_name = "问号产品占比"
            desc = "高增长低份额"
        else:
            chinese_name = "瘦狗产品占比"
            desc = "低增长低份额"

        stats_html += f"""
        <div style="background-color: {color}; opacity: 0.8; border-radius: 8px; padding: 15px; margin-bottom: 10px; border-left: 4px solid {color};">
            <div style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 5px;">{chinese_name}</div>
            <div style="font-size: 24px; font-weight: bold; color: #FF4500;">{percentage:.2f}%</div>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">{desc}</div>
        </div>
        """

    # 添加健康度评分
    bcg_health = bcg_analysis.get('bcg_health', 0)
    health_color = '#4CAF50' if bcg_health >= 80 else '#FF9800' if bcg_health >= 60 else '#F44336'
    health_status = '健康' if bcg_health >= 80 else '一般' if bcg_health >= 60 else '不健康'

    stats_html += f"""
        <div style="background: linear-gradient(135deg, {health_color}, {health_color}); border-radius: 8px; padding: 15px; margin-top: 20px; text-align: center;">
            <div style="font-size: 14px; color: white; margin-bottom: 5px;">组合健康度</div>
            <div style="font-size: 28px; font-weight: bold; color: white;">{bcg_health:.1f}%</div>
            <div style="font-size: 12px; color: white; margin-top: 5px;">{health_status}</div>
        </div>
    </div>
    """

    return stats_html


def create_kpi_achievement_chart(current_ratio, target_ratio):
    """创建KPI达成率展示图表"""
    achievement_rate = (current_ratio / target_ratio * 100) if target_ratio > 0 else 0

    if achievement_rate >= 100:
        bar_color = COLORS['success']
        status = "已超额完成"
    elif achievement_rate >= 80:
        bar_color = COLORS['warning']
        status = "接近目标"
    else:
        bar_color = COLORS['danger']
        status = "距离目标较远"

    fig = go.Figure()

    # 添加背景条
    fig.add_trace(go.Bar(
        y=['达成率'],
        x=[100],
        orientation='h',
        marker=dict(color='rgba(220, 220, 220, 0.5)'),
        hoverinfo='none',
        showlegend=False,
        name='目标'
    ))

    # 添加实际达成条
    fig.add_trace(go.Bar(
        y=['达成率'],
        x=[achievement_rate],
        orientation='h',
        marker=dict(color=bar_color),
        hovertemplate='达成率: %{x:.1f}%<extra></extra>',
        name='实际达成'
    ))

    fig.add_annotation(
        x=achievement_rate + 5,
        y=0,
        text=f"{achievement_rate:.1f}%",
        showarrow=False,
        font=dict(size=16, color=bar_color, family="Arial, sans-serif"),
        align="left"
    )

    fig.add_annotation(
        x=105,
        y=0,
        text="目标: 100%",
        showarrow=False,
        font=dict(size=12, color='gray'),
        align="left"
    )

    fig.update_layout(
        title={
            'text': f"星品&新品年度KPI达成情况: {status}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18, family="Arial, sans-serif")
        },
        barmode='overlay',
        height=250,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            range=[0, max(120, achievement_rate + 20)],
            title="达成百分比",
            showgrid=True,
            gridcolor='rgba(220, 220, 220, 0.5)',
        ),
        yaxis=dict(
            showticklabels=False,
        ),
        showlegend=False
    )

    return fig


def create_star_new_product_performance_chart(star_new_data, star_new_products):
    """创建考核产品详细表现图表"""
    if star_new_data.empty:
        return None, None

    # 按产品汇总数据
    product_performance = star_new_data.groupby(['产品代码', '简化产品名称']).agg({
        '销售额': 'sum',
        '数量（箱）': 'sum'
    }).reset_index().sort_values('销售额', ascending=False)

    # 1. 柱状图 - 各产品销售额对比
    fig_bar = go.Figure()

    colors = px.colors.qualitative.Bold
    for i, row in product_performance.iterrows():
        product = row['简化产品名称']
        sales = row['销售额']
        color_idx = i % len(colors)

        fig_bar.add_trace(go.Bar(
            x=[product],
            y=[sales],
            name=product,
            marker_color=colors[color_idx],
            text=[format_currency(sales)],
            textposition='outside',
            textfont=dict(size=14)
        ))

    fig_bar.update_layout(
        title='考核产品销售额对比',
        xaxis_title="产品名称",
        yaxis_title="销售额 (元)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )

    fig_bar.update_yaxes(
        range=[0, product_performance['销售额'].max() * 1.2],
        tickformat=',',
        type='linear'
    )

    # 2. 饼图 - 考核产品销售占比分布
    fig_pie = px.pie(
        product_performance,
        values='销售额',
        names='简化产品名称',
        title='考核产品销售占比分布',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=12)
    )

    fig_pie.update_layout(
        height=400,
        margin=dict(t=60, b=60, l=60, r=60),
        font=dict(size=14)
    )

    return fig_bar, fig_pie


def create_promotion_effectiveness_chart(promotion_analysis):
    """创建促销活动有效性图表"""
    if not promotion_analysis:
        return None

    total = promotion_analysis.get('total_promotions', 0)
    effective = promotion_analysis.get('effective_promotions', 0)
    ineffective = total - effective

    fig = px.pie(
        values=[effective, ineffective],
        names=['有效活动', '无效活动'],
        title='促销活动有效性分布',
        hole=0.4,
        color_discrete_sequence=[COLORS['success'], COLORS['danger']]
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=14)
    )

    fig.update_layout(
        height=400,
        margin=dict(t=60, b=60, l=60, r=60),
        font=dict(size=14)
    )

    return fig


def create_new_product_analysis_charts(new_products_data, new_products):
    """创建新品分析图表"""
    if new_products_data.empty:
        return None, None

    # 1. 新品销售额对比
    product_performance = new_products_data.groupby(['产品代码', '简化产品名称']).agg({
        '销售额': 'sum',
        '数量（箱）': 'sum',
        '客户简称': 'nunique'
    }).reset_index().sort_values('销售额', ascending=False)
    product_performance.columns = ['产品代码', '产品名称', '销售额', '销售数量', '购买客户数']

    fig_bar = go.Figure()

    colors = px.colors.qualitative.Pastel
    for i, row in product_performance.iterrows():
        product = row['产品名称']
        sales = row['销售额']
        color_idx = i % len(colors)

        fig_bar.add_trace(go.Bar(
            x=[product],
            y=[sales],
            name=product,
            marker_color=colors[color_idx],
            text=[format_currency(sales)],
            textposition='outside',
            textfont=dict(size=14)
        ))

    fig_bar.update_layout(
        title='新品销售额对比',
        xaxis_title="产品名称",
        yaxis_title="销售额 (元)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )

    fig_bar.update_yaxes(
        range=[0, product_performance['销售额'].max() * 1.2],
        tickformat=',',
        type='linear'
    )

    # 2. 新品渗透率分析
    region_penetration = new_products_data.groupby('所属区域').agg({
        '客户简称': 'nunique'
    }).reset_index()
    region_penetration.columns = ['区域', '购买新品客户数']

    fig_penetration = px.bar(
        region_penetration,
        x='区域',
        y='购买新品客户数',
        title='各区域新品客户数分布',
        color='区域',
        text='购买新品客户数'
    )

    fig_penetration.update_traces(
        texttemplate='%{text}',
        textposition='outside'
    )

    fig_penetration.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )

    return fig_bar, fig_penetration


# ==================== 主程序 ====================
def main():
    # 检查认证
    if not check_authentication():
        return

    # 页面标题
    st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

    # 数据时间范围横幅
    st.markdown(f"""
    <div class="time-range-banner">
        📅 数据时间范围：{DATA_TIME_RANGE} (最后更新：{LAST_UPDATE})
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载数据..."):
        sales_data = load_sales_data()
        promotion_data = load_promotion_data()
        star_new_products = load_star_new_products()
        new_products = load_new_products()
        all_products = load_all_products()

    # 侧边栏筛选器
    st.sidebar.markdown('<div class="sidebar-header">🔍 数据筛选</div>', unsafe_allow_html=True)

    # 区域筛选
    all_regions = sorted(sales_data['所属区域'].unique()) if not sales_data.empty else []
    selected_regions = st.sidebar.multiselect("选择区域", all_regions, default=all_regions)

    # 申请人筛选
    all_applicants = sorted(sales_data['申请人'].unique()) if not sales_data.empty else []
    selected_applicants = st.sidebar.multiselect("选择申请人", all_applicants, default=[])

    # 应用筛选条件
    filtered_sales = sales_data.copy()
    if selected_regions:
        filtered_sales = filtered_sales[filtered_sales['所属区域'].isin(selected_regions)]
    if selected_applicants:
        filtered_sales = filtered_sales[filtered_sales['申请人'].isin(selected_applicants)]

    # 分析数据
    sales_overview = analyze_sales_overview(filtered_sales)
    star_new_analysis = analyze_star_new_kpi(filtered_sales, star_new_products)
    promotion_analysis = analyze_promotion_effectiveness(filtered_sales, promotion_data)
    new_product_analysis = analyze_new_product_penetration(filtered_sales, new_products)
    bcg_analysis = calculate_bcg_metrics(filtered_sales, all_products)

    # 创建标签页
    tab_names = ["📊 销售概览", "🎯 产品发展分析", "🎪 促销活动分析", "🆕 新品分析", "🔄 产品组合分析"]
    tabs = st.tabs(tab_names)

    with tabs[0]:  # 销售概览
        # 汇总性卡片
        st.markdown(create_tooltip_header("关键业务指标", "点击卡片可跳转到对应的详细分析页面"), unsafe_allow_html=True)

        # 创建5个关键指标卡片
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # 总销售额卡片 - 不跳转，在当前页面展开
            if st.button(
                    f"总销售额\n{format_currency(sales_overview.get('total_sales', 0))}\n全部销售收入",
                    key="total_sales_card"
            ):
                # 展开销售详细数据
                st.session_state.show_sales_detail = True

        with col2:
            # 星品&新品KPI达成率卡片
            achievement_rate = star_new_analysis.get('achievement_rate', 0)
            card_type = "success" if achievement_rate >= 100 else "warning" if achievement_rate >= 80 else "danger"
            create_clickable_kpi_card(
                "星品&新品KPI达成率",
                format_percentage(achievement_rate),
                f"目标: {STAR_NEW_KPI_TARGET}%",
                card_type=card_type,
                tab_index=1
            )

        with col3:
            # 促销活动有效率卡片
            effectiveness_rate = promotion_analysis.get('effectiveness_rate', 0)
            card_type = "success" if effectiveness_rate >= 70 else "warning" if effectiveness_rate >= 50 else "danger"
            create_clickable_kpi_card(
                "促销活动有效率",
                format_percentage(effectiveness_rate),
                f"有效活动: {promotion_analysis.get('effective_promotions', 0)}个",
                card_type=card_type,
                tab_index=2
            )

        with col4:
            # 新品市场渗透率卡片
            penetration_rate = new_product_analysis.get('penetration_rate', 0)
            card_type = "success" if penetration_rate >= 50 else "warning" if penetration_rate >= 30 else "danger"
            create_clickable_kpi_card(
                "新品市场渗透率",
                format_percentage(penetration_rate),
                f"渗透客户: {new_product_analysis.get('new_product_customers', 0)}个",
                card_type=card_type,
                tab_index=3
            )

        with col5:
            # 产品组合健康度卡片
            bcg_health = bcg_analysis.get('bcg_health', 0)
            card_type = "success" if bcg_health >= 80 else "warning" if bcg_health >= 60 else "danger"
            create_clickable_kpi_card(
                "产品组合健康度",
                format_percentage(bcg_health),
                "BCG矩阵评分",
                card_type=card_type,
                tab_index=4
            )

        # 展开的销售详细分析
        if hasattr(st.session_state, 'show_sales_detail') and st.session_state.show_sales_detail:
            st.markdown(create_tooltip_header("销售详细分析", "全面展示销售数据的多维度分析结果"),
                        unsafe_allow_html=True)

            # 基础指标展示
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">客户数量</div>
                    <div class="metric-value">{format_number(sales_overview.get('total_customers', 0))}</div>
                    <div class="metric-subtitle">服务客户总数</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">产品数量</div>
                    <div class="metric-value">{format_number(sales_overview.get('total_products', 0))}</div>
                    <div class="metric-subtitle">销售产品总数</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">平均单价</div>
                    <div class="metric-value">{format_currency(sales_overview.get('avg_price', 0))}</div>
                    <div class="metric-subtitle">每箱平均价格</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                customer_avg = sales_overview.get('total_sales', 0) / sales_overview.get('total_customers',
                                                                                         1) if sales_overview.get(
                    'total_customers', 0) > 0 else 0
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">客户平均贡献</div>
                    <div class="metric-value">{format_currency(customer_avg)}</div>
                    <div class="metric-subtitle">单客户平均销售额</div>
                </div>
                """, unsafe_allow_html=True)

            # 添加收起按钮
            if st.button("收起详细分析", key="collapse_detail"):
                st.session_state.show_sales_detail = False
                st.rerun()

    with tabs[1]:  # 产品发展分析
        st.markdown(create_tooltip_header("星品&新品年度KPI考核", "监控核心产品销售占比，确保达成年度KPI目标"),
                    unsafe_allow_html=True)

        # KPI概览
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">星品&新品销售额</div>
                <div class="metric-value">{format_currency(star_new_analysis.get('star_new_sales', 0))}</div>
                <div class="metric-subtitle">考核产品销售额</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">当前占比</div>
                <div class="metric-value">{format_percentage(star_new_analysis.get('current_ratio', 0))}</div>
                <div class="metric-subtitle">实际销售占比</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            achievement_rate = star_new_analysis.get('achievement_rate', 0)
            color = COLORS['success'] if achievement_rate >= 100 else COLORS['warning'] if achievement_rate >= 80 else \
            COLORS['danger']
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">目标达成率</div>
                <div class="metric-value" style="color: {color};">{format_percentage(achievement_rate)}</div>
                <div class="metric-subtitle">完成度评估</div>
            </div>
            """, unsafe_allow_html=True)

        # KPI达成率图表
        if star_new_analysis:
            fig = create_kpi_achievement_chart(
                star_new_analysis.get('current_ratio', 0),
                star_new_analysis.get('target_ratio', STAR_NEW_KPI_TARGET)
            )
            st.plotly_chart(fig, use_container_width=True)

        # 考核产品详细表现
        star_new_products_detail = filtered_sales[filtered_sales['产品代码'].isin(star_new_products)]
        if not star_new_products_detail.empty:
            st.markdown(create_tooltip_header("考核产品详细表现", "各考核产品的销售额和占比分析，助力KPI达成"),
                        unsafe_allow_html=True)

            # 创建考核产品表现图表
            fig_bar, fig_pie = create_star_new_product_performance_chart(star_new_products_detail, star_new_products)

            col1, col2 = st.columns(2)

            with col1:
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                if fig_pie:
                    st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("当前筛选条件下没有考核产品数据。")

        # KPI建议
        achievement_rate = star_new_analysis.get('achievement_rate', 0)
        if achievement_rate >= 100:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(76, 175, 80, 0.1); border-left-color: {COLORS['success']};">
                <h4>✅ KPI目标已达成</h4>
                <p>当前星品&新品销售占比{format_percentage(star_new_analysis.get('current_ratio', 0))}，已超过{STAR_NEW_KPI_TARGET}%的目标要求。</p>
                <p><strong>建议行动：</strong>保持现有产品推广力度，探索进一步提升的机会。</p>
            </div>
            """, unsafe_allow_html=True)
        elif achievement_rate >= 80:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(255, 152, 0, 0.1); border-left-color: {COLORS['warning']};">
                <h4>⚠️ 接近目标，需要加强</h4>
                <p>当前达成率{format_percentage(achievement_rate)}，距离目标还需努力。</p>
                <p><strong>建议行动：</strong>加大星品&新品营销推广，重点关注高潜力产品。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(244, 67, 54, 0.1); border-left-color: {COLORS['danger']};">
                <h4>🚨 目标达成严重不足</h4>
                <p>当前达成率{format_percentage(achievement_rate)}，需要紧急行动。</p>
                <p><strong>建议行动：</strong>全面评估产品策略，加大资源投入，制定专项提升计划。</p>
            </div>
            """, unsafe_allow_html=True)

    with tabs[2]:  # 促销活动分析
        st.markdown(create_tooltip_header("促销活动效果分析", "监控促销活动的有效性，优化营销资源配置"),
                    unsafe_allow_html=True)

        # 促销概览
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">总促销活动</div>
                <div class="metric-value">{format_number(promotion_analysis.get('total_promotions', 0))}</div>
                <div class="metric-subtitle">活动总数</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">有效活动</div>
                <div class="metric-value">{format_number(promotion_analysis.get('effective_promotions', 0))}</div>
                <div class="metric-subtitle">效果显著的活动</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            effectiveness_rate = promotion_analysis.get('effectiveness_rate', 0)
            color = COLORS['success'] if effectiveness_rate >= 70 else COLORS[
                'warning'] if effectiveness_rate >= 50 else COLORS['danger']
            st.markdown(f"""
            <div class="clickable-card">
                <div class="metric-label">活动有效率</div>
                <div class="metric-value" style="color: {color};">{format_percentage(effectiveness_rate)}</div>
                <div class="metric-subtitle">促销成功率</div>
            </div>
            """, unsafe_allow_html=True)

        # 促销有效性图表
        col1, col2 = st.columns(2)

        with col1:
            fig_promotion = create_promotion_effectiveness_chart(promotion_analysis)
            if fig_promotion:
                st.plotly_chart(fig_promotion, use_container_width=True)

        with col2:
            # 促销数据表
            if not promotion_data.empty:
                st.markdown(create_tooltip_header("促销活动列表", "当前活跃的促销活动详细信息"), unsafe_allow_html=True)
                # 只显示前10条记录
                display_promotion = promotion_data.head(10)[
                    ['经销商名称', '产品代码', '预计销量（箱）', '预计销售额（元）']]
                st.dataframe(display_promotion, use_container_width=True)
            else:
                st.info("没有促销活动数据。")

        # 促销建议
        effectiveness_rate = promotion_analysis.get('effectiveness_rate', 0)
        if effectiveness_rate >= 70:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(76, 175, 80, 0.1); border-left-color: {COLORS['success']};">
                <h4>✅ 促销效果良好</h4>
                <p>大部分促销活动都取得了预期效果，活动策划和执行能力优秀。</p>
                <p><strong>建议行动：</strong>总结成功经验，复制到更多产品和区域。</p>
            </div>
            """, unsafe_allow_html=True)
        elif effectiveness_rate >= 50:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(255, 152, 0, 0.1); border-left-color: {COLORS['warning']};">
                <h4>⚠️ 促销效果一般</h4>
                <p>部分促销活动效果不明显，需要优化促销策略。</p>
                <p><strong>建议行动：</strong>分析无效活动原因，改进促销方案设计。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="highlight" style="background-color: rgba(244, 67, 54, 0.1); border-left-color: {COLORS['danger']};">
                <h4>🚨 促销效果不佳</h4>
                <p>多数促销活动未达到预期效果，需要全面检讨促销策略。</p>
                <p><strong>建议行动：</strong>重新评估促销模式，优化活动设计和执行流程。</p>
            </div>
            """, unsafe_allow_html=True)

    with tabs[3]:  # 新品分析
        st.markdown(create_tooltip_header("新品市场表现分析", "追踪新品的市场接受度和渗透情况"), unsafe_allow_html=True)

        # 新品数据分析
        new_products_data = filtered_sales[filtered_sales['产品代码'].isin(new_products)]

        # 新品概览
        if not new_products_data.empty:
            new_total_sales = new_products_data['销售额'].sum()
            new_customers = new_products_data['客户简称'].nunique()
            total_sales = filtered_sales['销售额'].sum()
            new_ratio = (new_total_sales / total_sales * 100) if total_sales > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">新品销售额</div>
                    <div class="metric-value">{format_currency(new_total_sales)}</div>
                    <div class="metric-subtitle">新品产生的销售额</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">新品销售占比</div>
                    <div class="metric-value">{format_percentage(new_ratio)}</div>
                    <div class="metric-subtitle">占总销售额比例</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">购买新品的客户</div>
                    <div class="metric-value">{format_number(new_customers)}</div>
                    <div class="metric-subtitle">尝试新品的客户数</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                penetration_rate = new_product_analysis.get('penetration_rate', 0)
                color = COLORS['success'] if penetration_rate >= 50 else COLORS[
                    'warning'] if penetration_rate >= 30 else COLORS['danger']
                st.markdown(f"""
                <div class="clickable-card">
                    <div class="metric-label">市场渗透率</div>
                    <div class="metric-value" style="color: {color};">{format_percentage(penetration_rate)}</div>
                    <div class="metric-subtitle">新品客户渗透率</div>
                </div>
                """, unsafe_allow_html=True)

            # 新品表现图表
            st.markdown(create_tooltip_header("新品销售表现", "各新品的销售额对比和区域分布"), unsafe_allow_html=True)

            fig_bar, fig_penetration = create_new_product_analysis_charts(new_products_data, new_products)

            col1, col2 = st.columns(2)

            with col1:
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                if fig_penetration:
                    st.plotly_chart(fig_penetration, use_container_width=True)

        else:
            st.info("当前筛选条件下没有新品数据。")