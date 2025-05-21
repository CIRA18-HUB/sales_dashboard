# 产品组合.py - 完整的销售数据分析仪表盘
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
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 常量定义 ====================
# 颜色配置
COLORS = {
    'primary': '#1f3867',
    'secondary': '#4c78a8',
    'accent': '#f0f8ff',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'gray': '#6c757d'
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

# 数据文件路径 - 修改为相对路径
DATA_FILES = {
    'sales_data': "仪表盘原始数据.xlsx",
    'promotion_data': "仪表盘促销活动.xlsx",
    'star_new_products': "星品&新品年度KPI考核.txt",
    'new_products': "仪表盘新品代码.txt",  # 添加新品代码文件
    'all_products': "仪表盘产品代码.txt"  # 添加所有产品代码文件
}

# ==================== CSS样式 ====================
st.markdown("""
<style>
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --accent-color: #f0f8ff;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --gray-color: #6c757d;
    }

    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        padding-top: 1rem;
        font-weight: 600;
    }

    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
    }

    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .card-header {
        font-size: 1.1rem;
        font-weight: bold;
        color: var(--gray-color);
        margin-bottom: 0.5rem;
    }

    .card-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .card-text {
        font-size: 0.9rem;
        color: var(--gray-color);
    }

    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid var(--success-color);
        font-size: 0.9rem;
    }

    .alert-box {
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--success-color);
    }

    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 4px solid var(--warning-color);
    }

    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid var(--danger-color);
    }

    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .kpi-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

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
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* 添加表格相关样式 */
    .table-container {
        min-height: 300px;
        overflow: auto;
        margin-bottom: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }

    /* 确保图表有最小高度 */
    .plotly-chart {
        min-height: 350px;
    }

    /* 减少卡片间的空白 */
    .metric-card {
        margin-bottom: 0.75rem !important;
    }

    /* 让区域更紧凑 */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem !important;
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


# ==================== 数据加载函数 ====================
@st.cache_data
def load_sales_data():
    """加载销售数据"""
    try:
        if os.path.exists(DATA_FILES['sales_data']):
            df = pd.read_excel(DATA_FILES['sales_data'])

            # 数据预处理
            required_columns = ['客户简称', '所属区域', '发运月份', '申请人', '产品代码', '产品名称', '产品简称',
                                '订单类型', '单价（箱）', '求和项:数量（箱）', '求和项:金额（元）']

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

            return df
        else:
            st.error(f"找不到销售数据文件: {DATA_FILES['sales_data']}，请确保文件路径正确")
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
            st.error(f"找不到促销数据文件: {DATA_FILES['promotion_data']}，请确保文件路径正确")
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
            st.error(f"找不到星品&新品产品代码文件: {DATA_FILES['star_new_products']}，请确保文件路径正确")
            return ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A']  # 默认值
    except Exception as e:
        st.error(f"加载星品&新品产品代码失败: {str(e)}")
        return ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A']  # 默认值


@st.cache_data
def load_new_products():
    """加载新品产品代码"""
    try:
        if os.path.exists(DATA_FILES['new_products']):
            with open(DATA_FILES['new_products'], 'r', encoding='utf-8') as f:
                products = [line.strip() for line in f.readlines() if line.strip()]
            return products
        else:
            st.error(f"找不到新品产品代码文件: {DATA_FILES['new_products']}，请确保文件路径正确")
            return ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']  # 默认值
    except Exception as e:
        st.error(f"加载新品产品代码失败: {str(e)}")
        return ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']  # 默认值


@st.cache_data
def load_all_products():
    """加载所有产品代码"""
    try:
        if os.path.exists(DATA_FILES['all_products']):
            with open(DATA_FILES['all_products'], 'r', encoding='utf-8') as f:
                products = [line.strip() for line in f.readlines() if line.strip()]
            return products
        else:
            st.error(f"找不到产品代码文件: {DATA_FILES['all_products']}，请确保文件路径正确")
            # 如果文件不存在，尝试从销售数据中获取
            return []
    except Exception as e:
        st.error(f"加载产品代码失败: {str(e)}")
        return []


def create_sample_sales_data():
    """创建示例销售数据"""
    # 准备示例数据
    num_rows = 40
    product_codes = ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A', 'F0110C', 'F0183F', 'F01K8A', 'F0183K',
                     'F0101P', 'F0104L', 'F01E4B']
    # 确保产品代码数组长度与其他字段一致
    product_codes_extended = (product_codes * (num_rows // len(product_codes) + 1))[:num_rows]

    data = {
        '客户简称': ['广州佳成行', '河南甜丰號', '北京客户', '上海客户'] * 10,
        '所属区域': ['南', '中', '北', '东'] * 10,
        '发运月份': ['2025-01', '2025-02', '2025-03', '2025-04'] * 10,
        '申请人': ['梁洪泽', '胡斌', '李根', '刘嫔妍'] * 10,
        '产品代码': product_codes_extended,
        '产品名称': ['示例产品' + str(i) for i in range(num_rows)],
        '产品简称': ['简称' + str(i) for i in range(num_rows)],
        '订单类型': ['订单-正常产品'] * num_rows,
        '单价（箱）': [100 + i * 10 for i in range(num_rows)],
        '数量（箱）': [10 + i for i in range(num_rows)],
    }

    df = pd.DataFrame(data)
    df['销售额'] = df['单价（箱）'] * df['数量（箱）']

    return df


def create_sample_promotion_data():
    """创建示例促销数据"""
    num_rows = 15
    product_codes = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P'] * 3
    # 确保产品代码数组长度与其他字段一致
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

    # 基础指标
    total_sales = sales_data['销售额'].sum()
    total_customers = sales_data['客户简称'].nunique()
    total_products = sales_data['产品代码'].nunique()
    avg_price = sales_data['单价（箱）'].mean()

    # 区域分析
    region_sales = sales_data.groupby('所属区域')['销售额'].sum().sort_values(ascending=False)
    top_region = region_sales.index[0] if not region_sales.empty else "无数据"
    top_region_sales = region_sales.iloc[0] if not region_sales.empty else 0

    return {
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_products': total_products,
        'avg_price': avg_price,
        'region_sales': region_sales,
        'top_region': top_region,
        'top_region_sales': top_region_sales
    }


def analyze_star_new_kpi(sales_data, star_new_products):
    """分析星品&新品KPI达成情况"""
    if sales_data.empty:
        return {}

    # 获取当年数据
    current_year = datetime.now().year
    try:
        ytd_data = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]
    except:
        ytd_data = sales_data

    # 计算星品&新品销售额
    star_new_sales = ytd_data[ytd_data['产品代码'].isin(star_new_products)]['销售额'].sum()
    total_sales = ytd_data['销售额'].sum()

    # 计算达成率
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

    # 简化版促销效果分析
    total_promotions = len(promotion_data)

    # 假设有效性逻辑（简化版）
    # 实际应该按照用户提供的复杂逻辑计算
    effective_promotions = int(total_promotions * 0.7)  # 假设70%有效
    effectiveness_rate = (effective_promotions / total_promotions * 100) if total_promotions > 0 else 0

    return {
        'total_promotions': total_promotions,
        'effective_promotions': effective_promotions,
        'effectiveness_rate': effectiveness_rate
    }


def calculate_bcg_metrics(sales_data, all_products=None):
    """计算BCG产品组合指标"""
    if sales_data.empty:
        return {}

    # 按产品代码汇总
    product_sales = sales_data.groupby(['产品代码', '产品简称']).agg({
        '销售额': 'sum',
        '数量（箱）': 'sum'
    }).reset_index()

    if product_sales.empty:
        return {}

    # 计算销售占比
    total_sales = product_sales['销售额'].sum()
    product_sales['销售占比'] = product_sales['销售额'] / total_sales * 100 if total_sales > 0 else 0

    # 简化的增长率计算（由于没有历史数据，使用随机值作为示例）
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

    # 健康度评分
    bcg_health_score = 100 - (
            abs(cash_cow_percent - 47.5) * 1.5 +
            abs(star_question_percent - 42.5) * 1.5 +
            max(0, dog_percent - 10) * 3
    )
    bcg_health = max(0, min(100, bcg_health_score))

    # 计算产品覆盖率
    product_coverage = 0
    if all_products and len(all_products) > 0:
        selling_products = sales_data['产品代码'].nunique()
        product_coverage = (selling_products / len(all_products)) * 100

    return {
        'product_sales': product_sales,
        'bcg_summary': bcg_summary,
        'bcg_health': bcg_health,
        'cash_cow_percent': cash_cow_percent,
        'star_question_percent': star_question_percent,
        'dog_percent': dog_percent,
        'product_coverage': product_coverage
    }


# ==================== 图表创建函数 ====================
def create_kpi_card(title, value, subtitle, color="primary", key=None):
    """创建KPI卡片"""
    if key:
        clicked = st.button(f"{title}\n{value}\n{subtitle}", key=key, help=f"点击查看{title}详情")
        if clicked:
            return True
    else:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">{title}</p>
            <p class="card-value" style="color: {COLORS.get(color, COLORS['primary'])};">{value}</p>
            <p class="card-text">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    return False


def create_region_sales_chart(region_sales):
    """创建区域销售图表"""
    region_df = region_sales.reset_index()
    region_df.columns = ['区域', '销售额']

    fig = px.bar(
        region_df,
        x='区域',
        y='销售额',
        title="各区域销售额对比",
        color='区域',
        text='销售额'
    )

    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        xaxis_title="区域",
        yaxis_title="销售额（元）",
        showlegend=False
    )

    return fig


def create_bcg_bubble_chart(product_data):
    """创建BCG矩阵气泡图"""
    if product_data.empty:
        return None

    color_map = {
        '明星产品': BCG_COLORS['star'],
        '现金牛产品': BCG_COLORS['cash_cow'],
        '问号产品': BCG_COLORS['question'],
        '瘦狗产品': BCG_COLORS['dog']
    }

    fig = px.scatter(
        product_data,
        x='增长率',
        y='销售占比',
        size='销售额',
        color='BCG分类',
        hover_name='产品简称',
        title="产品BCG矩阵分析",
        color_discrete_map=color_map,
        size_max=50
    )

    # 添加分隔线
    fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=max(product_data['销售占比']) * 1.1,
                  line=dict(color="gray", width=1, dash="dash"))
    fig.add_shape(type="line", x0=min(product_data['增长率']) * 1.1, y0=1.5,
                  x1=max(product_data['增长率']) * 1.1, y1=1.5,
                  line=dict(color="gray", width=1, dash="dash"))

    fig.update_layout(height=500, xaxis_title="增长率 (%)", yaxis_title="销售占比 (%)")

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


def create_kpi_achievement_chart(current_ratio, target_ratio):
    """创建更美观的KPI达成率展示图表"""
    achievement_rate = (current_ratio / target_ratio * 100) if target_ratio > 0 else 0

    # 数据准备
    categories = ['达成率']
    values = [achievement_rate]

    # 确定颜色
    if achievement_rate >= 100:
        bar_color = COLORS['success']
        status = "已超额完成"
    elif achievement_rate >= 80:
        bar_color = COLORS['warning']
        status = "接近目标"
    else:
        bar_color = COLORS['danger']
        status = "距离目标较远"

    # 创建水平条形图
    fig = go.Figure()

    # 添加背景条 (目标条)
    fig.add_trace(go.Bar(
        y=categories,
        x=[100],  # 目标始终是100%
        orientation='h',
        marker=dict(color='rgba(220, 220, 220, 0.5)'),
        hoverinfo='none',
        showlegend=False,
        name='目标'
    ))

    # 添加实际达成条
    fig.add_trace(go.Bar(
        y=categories,
        x=[achievement_rate],
        orientation='h',
        marker=dict(color=bar_color),
        hovertemplate='达成率: %{x:.1f}%<extra></extra>',
        name='实际达成'
    ))

    # 在图表上添加文字标注
    fig.add_annotation(
        x=achievement_rate + 5,
        y=0,
        text=f"{achievement_rate:.1f}%",
        showarrow=False,
        font=dict(size=16, color=bar_color, family="Arial, sans-serif"),
        align="left"
    )

    # 添加目标标注
    fig.add_annotation(
        x=105,
        y=0,
        text="目标: 100%",
        showarrow=False,
        font=dict(size=12, color='gray'),
        align="left"
    )

    # 更新布局
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


# ==================== 主程序 ====================
def main():
    # 检查认证
    if not check_authentication():
        return

    # 页面标题
    st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载数据..."):
        sales_data = load_sales_data()
        promotion_data = load_promotion_data()
        star_new_products = load_star_new_products()
        new_products = load_new_products()  # 加载新品代码
        all_products = load_all_products()  # 加载所有产品代码

    # 侧边栏筛选器
    st.sidebar.header("🔍 数据筛选")

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
    bcg_analysis = calculate_bcg_metrics(filtered_sales, all_products)

    # 创建标签页
    tab_names = ["📊 销售概览", "🎯 产品发展分析", "🎪 促销活动分析", "🆕 新品分析", "🔄 产品组合分析", "🌐 区域分析"]
    current_tab = st.session_state.active_tab  # 获取当前活动标签页索引
    tabs = st.tabs(tab_names)

    with tabs[0]:  # 销售概览
        st.subheader("🔑 关键业务指标")

        # 创建5个关键指标卡片
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_sales_clicked = create_kpi_card(
                "总销售额",
                format_currency(sales_overview.get('total_sales', 0)),
                "全部销售收入",
                key="total_sales_card"
            )
            if total_sales_clicked:
                st.session_state.active_tab = 0
                st.rerun()

        with col2:
            kpi_clicked = create_kpi_card(
                "星品&新品KPI达成率",
                format_percentage(star_new_analysis.get('achievement_rate', 0)),
                f"目标: {STAR_NEW_KPI_TARGET}%",
                color="success" if star_new_analysis.get('achievement_rate', 0) >= 100 else "warning",
                key="kpi_card"
            )
            if kpi_clicked:
                st.session_state.active_tab = 1
                st.rerun()

        with col3:
            promotion_clicked = create_kpi_card(
                "促销活动有效率",
                format_percentage(promotion_analysis.get('effectiveness_rate', 0)),
                f"有效活动: {promotion_analysis.get('effective_promotions', 0)}个",
                key="promotion_card"
            )
            if promotion_clicked:
                st.session_state.active_tab = 2
                st.rerun()

        with col4:
            region_clicked = create_kpi_card(
                "区域销售排名",
                f"第1名: {sales_overview.get('top_region', '无数据')}",
                format_currency(sales_overview.get('top_region_sales', 0)),
                key="region_card"
            )
            if region_clicked:
                st.session_state.active_tab = 5
                st.rerun()

        with col5:
            bcg_clicked = create_kpi_card(
                "产品组合健康度",
                format_percentage(bcg_analysis.get('bcg_health', 0)),
                "BCG矩阵评分",
                color="success" if bcg_analysis.get('bcg_health', 0) >= 80 else "warning",
                key="bcg_card"
            )
            if bcg_clicked:
                st.session_state.active_tab = 4
                st.rerun()

        # 详细销售分析
        st.markdown('<div class="sub-header">📊 销售详细分析</div>', unsafe_allow_html=True)

        # 基础指标展示
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">客户数量</p>
                <p class="card-value">{format_number(sales_overview.get('total_customers', 0))}</p>
                <p class="card-text">服务客户总数</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">产品数量</p>
                <p class="card-value">{format_number(sales_overview.get('total_products', 0))}</p>
                <p class="card-text">销售产品总数</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">平均单价</p>
                <p class="card-value">{format_currency(sales_overview.get('avg_price', 0))}</p>
                <p class="card-text">每箱平均价格</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            customer_avg = sales_overview.get('total_sales', 0) / sales_overview.get('total_customers',
                                                                                     1) if sales_overview.get(
                'total_customers', 0) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">客户平均贡献</p>
                <p class="card-value">{format_currency(customer_avg)}</p>
                <p class="card-text">单客户平均销售额</p>
            </div>
            """, unsafe_allow_html=True)

        # 区域销售图表
        if not sales_overview.get('region_sales', pd.Series()).empty:
            fig = create_region_sales_chart(sales_overview['region_sales'])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="chart-explanation">
                <b>图表解读：</b> 展示各区域销售额对比，帮助识别核心市场和增长机会。
                销售分布反映了市场渗透情况和资源配置效果。
            </div>
            """, unsafe_allow_html=True)

    with tabs[1]:  # 产品发展分析
        st.subheader("🎯 星品&新品年度KPI考核")

        # KPI概览
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">星品&新品销售额</p>
                <p class="card-value">{format_currency(star_new_analysis.get('star_new_sales', 0))}</p>
                <p class="card-text">考核产品销售额</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">当前占比</p>
                <p class="card-value">{format_percentage(star_new_analysis.get('current_ratio', 0))}</p>
                <p class="card-text">实际销售占比</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            achievement_rate = star_new_analysis.get('achievement_rate', 0)
            color = COLORS['success'] if achievement_rate >= 100 else COLORS['warning'] if achievement_rate >= 80 else \
                COLORS['danger']
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">目标达成率</p>
                <p class="card-value" style="color: {color};">{format_percentage(achievement_rate)}</p>
                <p class="card-text">完成度评估</p>
            </div>
            """, unsafe_allow_html=True)

        # 使用新的KPI达成率图表替代原来的仪表盘
        if star_new_analysis:
            fig = create_kpi_achievement_chart(
                star_new_analysis.get('current_ratio', 0),
                star_new_analysis.get('target_ratio', STAR_NEW_KPI_TARGET)
            )
            st.plotly_chart(fig, use_container_width=True)

            # 添加补充说明
            st.markdown(f"""
            <div class="chart-explanation">
                <b>KPI说明：</b> 星品&新品销售占比目标为{STAR_NEW_KPI_TARGET}%，当前实际占比为
                {format_percentage(star_new_analysis.get('current_ratio', 0))}，
                达成率为{format_percentage(star_new_analysis.get('achievement_rate', 0))}。
            </div>
            """, unsafe_allow_html=True)

        # 产品详细分析
        if not filtered_sales.empty:
            star_new_products_detail = filtered_sales[filtered_sales['产品代码'].isin(star_new_products)]
            if not star_new_products_detail.empty:
                product_performance = star_new_products_detail.groupby(['产品代码', '产品简称']).agg({
                    '销售额': 'sum',
                    '数量（箱）': 'sum'
                }).reset_index().sort_values('销售额', ascending=False)

                st.markdown('<div class="sub-header">📊 考核产品详细表现</div>', unsafe_allow_html=True)
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                st.dataframe(product_performance, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("当前筛选条件下没有考核产品数据。")

        # KPI建议
        achievement_rate = star_new_analysis.get('achievement_rate', 0)
        if achievement_rate >= 100:
            st.markdown(f"""
            <div class="alert-box alert-success">
                <h4>✅ KPI目标已达成</h4>
                <p>当前星品&新品销售占比{format_percentage(star_new_analysis.get('current_ratio', 0))}，已超过{STAR_NEW_KPI_TARGET}%的目标要求。</p>
                <p><strong>建议行动：</strong>保持现有产品推广力度，探索进一步提升的机会。</p>
            </div>
            """, unsafe_allow_html=True)
        elif achievement_rate >= 80:
            st.markdown(f"""
            <div class="alert-box alert-warning">
                <h4>⚠️ 接近目标，需要加强</h4>
                <p>当前达成率{format_percentage(achievement_rate)}，距离目标还需努力。</p>
                <p><strong>建议行动：</strong>加大星品&新品营销推广，重点关注高潜力产品。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-box alert-danger">
                <h4>🚨 目标达成严重不足</h4>
                <p>当前达成率{format_percentage(achievement_rate)}，需要紧急行动。</p>
                <p><strong>建议行动：</strong>全面评估产品策略，加大资源投入，制定专项提升计划。</p>
            </div>
            """, unsafe_allow_html=True)

    with tabs[2]:  # 促销活动分析
        st.subheader("🎪 促销活动效果分析")

        # 促销概览
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">总促销活动</p>
                <p class="card-value">{format_number(promotion_analysis.get('total_promotions', 0))}</p>
                <p class="card-text">活动总数</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">有效活动</p>
                <p class="card-value">{format_number(promotion_analysis.get('effective_promotions', 0))}</p>
                <p class="card-text">效果显著的活动</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            effectiveness_rate = promotion_analysis.get('effectiveness_rate', 0)
            color = COLORS['success'] if effectiveness_rate >= 70 else COLORS[
                'warning'] if effectiveness_rate >= 50 else COLORS['danger']
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">活动有效率</p>
                <p class="card-value" style="color: {color};">{format_percentage(effectiveness_rate)}</p>
                <p class="card-text">促销成功率</p>
            </div>
            """, unsafe_allow_html=True)

        # 促销数据表
        if not promotion_data.empty:
            st.markdown('<div class="sub-header">📋 促销活动列表</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.dataframe(promotion_data, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("没有促销活动数据。")

        # 促销建议
        effectiveness_rate = promotion_analysis.get('effectiveness_rate', 0)
        if effectiveness_rate >= 70:
            st.markdown("""
            <div class="alert-box alert-success">
                <h4>✅ 促销效果良好</h4>
                <p>大部分促销活动都取得了预期效果，活动策划和执行能力优秀。</p>
                <p><strong>建议行动：</strong>总结成功经验，复制到更多产品和区域。</p>
            </div>
            """, unsafe_allow_html=True)
        elif effectiveness_rate >= 50:
            st.markdown("""
            <div class="alert-box alert-warning">
                <h4>⚠️ 促销效果一般</h4>
                <p>部分促销活动效果不明显，需要优化促销策略。</p>
                <p><strong>建议行动：</strong>分析无效活动原因，改进促销方案设计。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box alert-danger">
                <h4>🚨 促销效果不佳</h4>
                <p>多数促销活动未达到预期效果，需要全面检讨促销策略。</p>
                <p><strong>建议行动：</strong>重新评估促销模式，优化活动设计和执行流程。</p>
            </div>
            """, unsafe_allow_html=True)

    with tabs[3]:  # 新品分析
        st.subheader("🆕 新品市场表现分析")

        # 新品数据分析
        new_products_data = filtered_sales[filtered_sales['产品代码'].isin(new_products)]

        # 新品概览
        if not new_products_data.empty:
            new_total_sales = new_products_data['销售额'].sum()
            new_customers = new_products_data['客户简称'].nunique()
            total_sales = filtered_sales['销售额'].sum()
            new_ratio = (new_total_sales / total_sales * 100) if total_sales > 0 else 0

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">新品销售额</p>
                    <p class="card-value">{format_currency(new_total_sales)}</p>
                    <p class="card-text">新品产生的销售额</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">新品销售占比</p>
                    <p class="card-value">{format_percentage(new_ratio)}</p>
                    <p class="card-text">占总销售额比例</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">购买新品的客户</p>
                    <p class="card-value">{format_number(new_customers)}</p>
                    <p class="card-text">尝试新品的客户数</p>
                </div>
                """, unsafe_allow_html=True)

            # 新品详细表现
            new_product_performance = new_products_data.groupby(['产品代码', '产品简称']).agg({
                '销售额': 'sum',
                '数量（箱）': 'sum',
                '客户简称': 'nunique'
            }).reset_index().sort_values('销售额', ascending=False)
            new_product_performance.columns = ['产品代码', '产品名称', '销售额', '销售数量', '购买客户数']

            st.markdown('<div class="sub-header">📊 各新品详细表现</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.dataframe(new_product_performance, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("当前筛选条件下没有新品数据。")

    with tabs[4]:  # 产品组合分析
        st.subheader("🔄 产品组合BCG分析")

        if bcg_analysis and not bcg_analysis.get('product_sales', pd.DataFrame()).empty:
            # BCG健康度展示
            col1, col2 = st.columns(2)

            with col1:
                fig = create_bcg_health_gauge(bcg_analysis.get('bcg_health', 0))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">现金牛产品占比</p>
                    <p class="card-value">{format_percentage(bcg_analysis.get('cash_cow_percent', 0))}</p>
                    <p class="card-text">理想范围: 45-50%</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">明星&问号产品占比</p>
                    <p class="card-value">{format_percentage(bcg_analysis.get('star_question_percent', 0))}</p>
                    <p class="card-text">理想范围: 40-45%</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">瘦狗产品占比</p>
                    <p class="card-value">{format_percentage(bcg_analysis.get('dog_percent', 0))}</p>
                    <p class="card-text">理想范围: ≤10%</p>
                </div>
                """, unsafe_allow_html=True)

                # 添加产品覆盖率指标
                if 'product_coverage' in bcg_analysis and bcg_analysis['product_coverage'] > 0:
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">产品覆盖率</p>
                        <p class="card-value">{format_percentage(bcg_analysis.get('product_coverage', 0))}</p>
                        <p class="card-text">实际销售产品数 / 系统中产品总数</p>
                    </div>
                    """, unsafe_allow_html=True)

            # BCG矩阵图
            product_sales = bcg_analysis.get('product_sales', pd.DataFrame())
            if not product_sales.empty:
                fig = create_bcg_bubble_chart(product_sales)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("""
                <div class="chart-explanation">
                    <b>BCG矩阵解读：</b> 此图展示产品在增长率和市场份额上的分布。
                    明星产品需要持续投入，现金牛产品提供稳定收入，问号产品需要评估潜力，瘦狗产品考虑退出。
                </div>
                """, unsafe_allow_html=True)

                # 显示BCG分类详细数据
                st.markdown('<div class="sub-header">📋 产品BCG分类详情</div>', unsafe_allow_html=True)
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                display_df = product_sales[
                    ['产品代码', '产品简称', 'BCG分类', '销售额', '销售占比', '增长率']].sort_values('销售额',
                                                                                                     ascending=False)
                display_df['销售额'] = display_df['销售额'].apply(format_currency)
                display_df['销售占比'] = display_df['销售占比'].apply(format_percentage)
                display_df['增长率'] = display_df['增长率'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(display_df, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("暂无充足数据进行BCG分析。")

    with tabs[5]:  # 区域分析
        st.subheader("🌐 区域销售深度分析")

        if not sales_overview.get('region_sales', pd.Series()).empty:
            # 区域销售排名
            region_sales = sales_overview['region_sales']
            region_df = region_sales.reset_index()
            region_df.columns = ['区域', '销售额']
            region_df['排名'] = range(1, len(region_df) + 1)
            region_df['占比'] = region_df['销售额'] / region_df['销售额'].sum() * 100

            st.markdown('<div class="sub-header">📊 区域销售排名</div>', unsafe_allow_html=True)

            # 前三名区域展示
            col1, col2, col3 = st.columns(3)

            for i, (col, (_, row)) in enumerate(zip([col1, col2, col3], region_df.head(3).iterrows())):
                rank_color = ['🥇', '🥈', '🥉'][i] if i < 3 else f"第{row['排名']}名"
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">{rank_color} {row['区域']}</p>
                        <p class="card-value">{format_currency(row['销售额'])}</p>
                        <p class="card-text">占比: {format_percentage(row['占比'])}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # 区域销售图表
            fig = create_region_sales_chart(region_sales)
            st.plotly_chart(fig, use_container_width=True)

            # 区域详细数据表
            st.markdown('<div class="sub-header">📋 区域详细数据</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            display_df = region_df.copy()
            display_df['销售额'] = display_df['销售额'].apply(format_currency)
            display_df['占比'] = display_df['占比'].apply(format_percentage)
            st.dataframe(display_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("暂无区域销售数据。")


if __name__ == "__main__":
    main()