import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import os
import re
import calendar

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售预测准确率分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'overview'  # 默认视图

if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = None

if 'selected_salesperson' not in st.session_state:
    st.session_state['selected_salesperson'] = None

if 'selected_product' not in st.session_state:
    st.session_state['selected_product'] = None

if 'filter_months' not in st.session_state:
    st.session_state['filter_months'] = []

if 'filter_regions' not in st.session_state:
    st.session_state['filter_regions'] = []

# 自定义CSS样式 - 现代化界面
st.markdown("""
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --accent-color: #f0f8ff;
        --success-color: #4CAF50;
        --warning-color: #FB8C00;
        --danger-color: #F44336;
        --info-color: #2196F3;
        --light-color: #f8f9fa;
        --dark-color: #343a40;
        --gray-color: #6c757d;
    }

    /* 主标题 */
    .main-header {
        font-size: 1.8rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1rem;
    }

    /* 二级标题 */
    .sub-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }

    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
        transition: transform 0.3s;
        cursor: pointer;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0.5rem 2rem 0 rgba(58, 59, 69, 0.2);
    }

    /* 卡片内部样式 */
    .card-header {
        font-size: 1rem;
        font-weight: bold;
        color: var(--gray-color);
        margin-bottom: 0.5rem;
    }

    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--primary-color);
    }

    .card-trend {
        display: inline-block;
        font-size: 0.9rem;
        margin-left: 0.5rem;
    }

    .trend-up {
        color: var(--success-color);
    }

    .trend-down {
        color: var(--danger-color);
    }

    .card-text {
        font-size: 0.9rem;
        color: var(--gray-color);
        margin-top: 0.5rem;
    }

    /* 筛选器样式 */
    .filter-container {
        background-color: var(--light-color);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0.1rem 0.5rem rgba(0,0,0,0.05);
    }

    .filter-title {
        font-weight: bold;
        color: var(--dark-color);
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }

    /* 返回按钮 */
    .back-button {
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }

    /* 图表说明 */
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 0.9rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border-left: 0.5rem solid #4CAF50;
        font-size: 0.9rem;
    }

    /* 问题指标 */
    .low-accuracy {
        border: 2px solid var(--danger-color);
        box-shadow: 0 0 8px var(--danger-color);
    }

    /* 分析洞察面板 */
    .insight-panel {
        background-color: #f8f9fa;
        border-left: 4px solid var(--info-color);
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }

    .insight-title {
        font-weight: bold;
        color: var(--info-color);
        margin-bottom: 0.5rem;
    }

    /* Tab样式 */
    .custom-tabs {
        margin-top: 1rem;
    }

    /* 热力图图例 */
    .heatmap-legend {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0;
    }

    .legend-item {
        margin: 0 0.5rem;
        font-size: 0.8rem;
    }

    .legend-color {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border-radius: 0.2rem;
        margin-right: 0.3rem;
        vertical-align: middle;
    }

    /* 下钻指示器 */
    .drill-indicator {
        font-size: 0.8rem;
        color: var(--gray-color);
        margin-bottom: 0.5rem;
    }

    /* 表格样式 */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        font-size: 0.9em;
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }

    .styled-table thead tr {
        background-color: var(--primary-color);
        color: white;
        text-align: left;
    }

    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
    }

    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }

    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }

    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid var(--primary-color);
    }

    /* 加载动画 */
    .loading-spinner {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }

    /* 工具提示 */
    .tooltip {
        position: relative;
        display: inline-block;
        margin-left: 0.3rem;
        cursor: help;
    }

    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    /* 导航痕迹 */
    .breadcrumb {
        display: flex;
        flex-wrap: wrap;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        list-style: none;
        background-color: #e9ecef;
        border-radius: 0.25rem;
        font-size: 0.9rem;
    }

    .breadcrumb-item {
        display: inline-block;
        margin-right: 0.5rem;
    }

    .breadcrumb-item:not(:last-child):after {
        content: ">";
        margin-left: 0.5rem;
        color: var(--gray-color);
    }

    .breadcrumb-link {
        color: var(--primary-color);
        text-decoration: none;
        cursor: pointer;
    }

    .breadcrumb-current {
        color: var(--gray-color);
    }
</style>
""", unsafe_allow_html=True)

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div class="main-header">销售预测准确率分析仪表盘 | 登录</div>',
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
            if password == 'SAL':  # 简易密码，实际应用中应更安全
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


# 添加Logo到右上角
def add_logo():
    st.markdown(
        """
        <div style="position: absolute; top: 0.5rem; right: 1rem; z-index: 1000;">
            <img src="https://www.example.com/logo.png" height="40">
        </div>
        """,
        unsafe_allow_html=True
    )


# 统一格式化函数
def format_number(value, precision=0):
    """格式化数值显示"""
    if pd.isna(value) or value is None:
        return "N/A"

    if isinstance(value, (int, float)):
        if abs(value) >= 10000:
            return f"{value / 10000:.{precision}f}万"
        return f"{value:,.{precision}f}"

    return str(value)


def format_percent(value, precision=1):
    """格式化百分比显示"""
    if pd.isna(value) or value is None:
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}%"

    return str(value)


# 安全计算函数
def safe_mean(series, default=0):
    """安全地计算Series的均值，处理空值和异常"""
    if series is None or len(series) == 0 or (hasattr(series, 'empty') and series.empty) or (
            hasattr(series, 'isna') and series.isna().all()):
        return default

    try:
        # 尝试使用pandas内置mean方法
        if hasattr(series, 'mean'):
            return series.mean()

        # 如果不是pandas Series，尝试使用numpy
        return np.nanmean(series)
    except (OverflowError, ValueError, TypeError, ZeroDivisionError):
        # 处理任何计算错误
        return default


# 修改产品名称简化函数
def simplify_product_name(code, full_name):
    """将产品完整名称简化为更简短的格式"""
    # 检查输入有效性
    if not full_name or not isinstance(full_name, str):
        return full_name

    # 如果符合"口力X-中国"格式，则简化
    if "口力" in full_name and "-中国" in full_name:
        # 去除"口力"前缀和"-中国"后缀
        return full_name.replace("口力", "").replace("-中国", "").strip()

    # 否则返回原始名称
    return full_name


# 统一准确率计算函数
def calculate_unified_accuracy(actual, forecast):
    """统一计算准确率的函数，适用于全国和区域"""
    # 处理边缘情况
    if pd.isna(actual) or pd.isna(forecast):
        return 0.0

    # 如果实际和预测都为0，准确率为100%
    if actual == 0 and forecast == 0:
        return 1.0

    # 如果实际为0但预测不为0，准确率为0%
    if actual == 0:
        return 0.0

    # 计算差异率
    diff_rate = (actual - forecast) / actual

    # 计算准确率 (基础公式: 1 - |差异率|)
    # 限制最小值为0，确保不会出现负数准确率
    return max(0, 1 - abs(diff_rate))


# 备货建议生成函数
def generate_recommendation(growth_rate):
    """基于增长率生成备货建议"""
    if pd.isna(growth_rate):
        return {
            "建议": "数据不足",
            "调整比例": 0,
            "颜色": "#9E9E9E",  # 灰色
            "样式类": "recommendation-neutral",
            "图标": "?"
        }

    # 基于增长率生成建议
    if growth_rate > 15:
        return {
            "建议": "增加备货",
            "调整比例": round(growth_rate),
            "颜色": "#4CAF50",  # 绿色
            "样式类": "recommendation-increase",
            "图标": "↑"
        }
    elif growth_rate > 0:
        return {
            "建议": "小幅增加",
            "调整比例": round(growth_rate / 2),
            "颜色": "#8BC34A",  # 浅绿色
            "样式类": "recommendation-increase",
            "图标": "↗"
        }
    elif growth_rate > -10:
        return {
            "建议": "维持现状",
            "调整比例": 0,
            "颜色": "#FFC107",  # 黄色
            "样式类": "recommendation-maintain",
            "图标": "→"
        }
    else:
        adjust = abs(round(growth_rate / 2))
        return {
            "建议": "减少备货",
            "调整比例": adjust,
            "颜色": "#F44336",  # 红色
            "样式类": "recommendation-decrease",
            "图标": "↓"
        }


# 获取最近3个月的函数
def get_last_three_months():
    today = datetime.now()
    current_month = today.replace(day=1)

    last_month = current_month - timedelta(days=1)
    last_month = last_month.replace(day=1)

    two_months_ago = last_month - timedelta(days=1)
    two_months_ago = two_months_ago.replace(day=1)

    months = []
    for dt in [two_months_ago, last_month, current_month]:
        months.append(dt.strftime('%Y-%m'))

    return months


# 数据加载函数 - 增强错误处理和数据验证
@st.cache_data
def load_product_info(file_path=None):
    """加载产品信息数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return create_sample_product_info()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['产品代码', '产品名称']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"产品信息文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return create_sample_product_info()

        # 确保数据类型正确
        df['产品代码'] = df['产品代码'].astype(str)
        df['产品名称'] = df['产品名称'].astype(str)

        # 添加简化产品名称列
        df['简化产品名称'] = df.apply(lambda row: simplify_product_name(row['产品代码'], row['产品名称']), axis=1)

        return df

    except Exception as e:
        st.error(f"加载产品信息数据时出错: {str(e)}。使用示例数据进行演示。")
        return create_sample_product_info()


def create_sample_product_info():
    """创建示例产品信息数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 产品名称列表
    product_names = [
        '口力比萨68克袋装-中国', '口力汉堡大袋120g-中国', '口力汉堡中袋108g-中国',
        '口力海洋动物100g-中国', '口力幻彩蜥蜴105g-中国', '口力午餐袋77g-中国',
        '口力汉堡137g-中国', '口力热狗120g-中国', '口力奶酪90g-中国',
        '口力比萨小包60g-中国', '口力比萨中包80g-中国', '口力比萨大包100g-中国',
        '口力薯条65g-中国', '口力鸡块75g-中国', '口力汉堡圈85g-中国',
        '口力德果汉堡108g-中国'
    ]

    # 产品规格
    product_specs = [
        '68g*24', '120g*24', '108g*24', '100g*24', '105g*24', '77g*24',
        '137g*24', '120g*24', '90g*24', '60g*24', '80g*24', '100g*24',
        '65g*24', '75g*24', '85g*24', '108g*24'
    ]

    # 创建DataFrame
    data = {'产品代码': product_codes,
            '产品名称': product_names,
            '产品规格': product_specs}

    df = pd.DataFrame(data)

    # 添加简化产品名称列
    df['简化产品名称'] = df.apply(lambda row: simplify_product_name(row['产品代码'], row['产品名称']), axis=1)

    return df


# 优化的产品代码映射函数
def format_product_code(code, product_info_df, include_name=True):
    """格式化产品代码显示"""
    if product_info_df is None or code not in product_info_df['产品代码'].values:
        return code

    if include_name:
        # 优先使用简化名称
        filtered_df = product_info_df[product_info_df['产品代码'] == code]
        if not filtered_df.empty and '简化产品名称' in filtered_df.columns:
            simplified_name = filtered_df['简化产品名称'].iloc[0]
            if not pd.isna(simplified_name) and simplified_name:
                return simplified_name

        # 回退到产品名称
        product_name = filtered_df['产品名称'].iloc[0] if not filtered_df.empty else code
        return product_name
    else:
        return code


@st.cache_data
def load_actual_data(file_path=None):
    """加载实际销售数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return load_sample_actual_data()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['订单日期', '所属区域', '申请人', '产品代码', '求和项:数量（箱）']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"实际销售数据文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return load_sample_actual_data()

        # 确保数据类型正确
        df['订单日期'] = pd.to_datetime(df['订单日期'])
        df['所属区域'] = df['所属区域'].astype(str)
        df['申请人'] = df['申请人'].astype(str)
        df['产品代码'] = df['产品代码'].astype(str)
        df['求和项:数量（箱）'] = df['求和项:数量（箱）'].astype(float)

        # 创建年月字段，用于与预测数据对齐
        df['所属年月'] = df['订单日期'].dt.strftime('%Y-%m')

        return df

    except Exception as e:
        st.error(f"加载实际销售数据时出错: {str(e)}。使用示例数据进行演示。")
        return load_sample_actual_data()


@st.cache_data
def load_forecast_data(file_path=None):
    """加载预测数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return load_sample_forecast_data()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"预测数据文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return load_sample_forecast_data()

        # 确保数据类型正确
        df['所属大区'] = df['所属大区'].astype(str)
        df['销售员'] = df['销售员'].astype(str)
        df['所属年月'] = pd.to_datetime(df['所属年月']).dt.strftime('%Y-%m')
        df['产品代码'] = df['产品代码'].astype(str)
        df['预计销售量'] = df['预计销售量'].astype(float)

        # 为了保持一致，将'所属大区'列重命名为'所属区域'
        df = df.rename(columns={'所属大区': '所属区域'})

        return df

    except Exception as e:
        st.error(f"加载预测数据时出错: {str(e)}。使用示例数据进行演示。")
        return load_sample_forecast_data()


# 示例数据创建函数
def load_sample_actual_data():
    """创建示例实际销售数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 申请人列表
    applicants = ['孙杨', '李根', '张伟', '王芳', '刘涛', '陈明']

    # 生成日期范围
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2025, 2, 24)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # 创建数据
    data = []
    for date in date_range:
        # 为每天生成随机数量的记录
        num_records = np.random.randint(3, 10)

        for _ in range(num_records):
            region = np.random.choice(regions)
            applicant = np.random.choice(applicants)
            product_code = np.random.choice(product_codes)
            quantity = np.random.randint(5, 300)

            data.append({
                '订单日期': date,
                '所属区域': region,
                '申请人': applicant,
                '产品代码': product_code,
                '求和项:数量（箱）': quantity
            })

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 添加年月字段
    df['所属年月'] = df['订单日期'].dt.strftime('%Y-%m')

    return df


def load_sample_forecast_data():
    """创建示例预测数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 销售员列表
    sales_people = ['李根', '张伟', '王芳', '刘涛', '陈明', '孙杨']

    # 生成月份范围
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2025, 2, 1)
    month_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    # 创建数据
    data = []
    for month in month_range:
        month_str = month.strftime('%Y-%m')

        for region in regions:
            for sales_person in sales_people:
                for product_code in product_codes:
                    # 使用正态分布生成预测值，使其变化更自然
                    forecast = max(0, np.random.normal(150, 50))

                    # 有些产品可能没有预测
                    if np.random.random() > 0.1:  # 90%的概率有预测
                        data.append({
                            '所属大区': region,
                            '销售员': sales_person,
                            '所属年月': month_str,
                            '产品代码': product_code,
                            '预计销售量': round(forecast)
                        })

    # 创建DataFrame
    df = pd.DataFrame(data)
    # 重命名列
    df = df.rename(columns={'所属大区': '所属区域'})
    return df


# 获取共有月份函数
def get_common_months(actual_df, forecast_df):
    """获取两个数据集共有的月份"""
    actual_months = set(actual_df['所属年月'].unique())
    forecast_months = set(forecast_df['所属年月'].unique())
    common_months = sorted(list(actual_months.intersection(forecast_months)))
    return common_months


# 优化的数据筛选函数
def filter_data(data, months=None, regions=None, products=None, salespersons=None):
    """统一的数据筛选函数 - 支持更多维度筛选"""
    if data is None or data.empty:
        return pd.DataFrame()

    filtered_data = data.copy()

    # 月份筛选
    if months and len(months) > 0:
        # 确保月份格式一致
        if '所属年月' in filtered_data.columns:
            if isinstance(filtered_data['所属年月'].iloc[0], str):
                months_str = [m if isinstance(m, str) else m.strftime('%Y-%m') for m in months]
                filtered_data = filtered_data[filtered_data['所属年月'].isin(months_str)]
            else:
                # 如果是datetime格式，转换筛选条件
                months_dt = [pd.to_datetime(m) for m in months]
                filtered_data = filtered_data[filtered_data['所属年月'].isin(months_dt)]

    # 区域筛选
    if regions and len(regions) > 0:
        if '所属区域' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['所属区域'].isin(regions)]

    # 产品筛选
    if products and len(products) > 0:
        if '产品代码' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['产品代码'].isin(products)]

    # 销售员筛选
    if salespersons and len(salespersons) > 0:
        if '销售员' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['销售员'].isin(salespersons)]
        elif '申请人' in filtered_data.columns:  # 实际数据中可能用"申请人"表示销售员
            filtered_data = filtered_data[filtered_data['申请人'].isin(salespersons)]

    return filtered_data


# 数据处理和分析函数 - 修复准确率计算问题
def process_data(actual_df, forecast_df, product_info_df):
    """处理数据并计算关键指标"""
    # 按月份、区域、产品码汇总数据
    actual_monthly = actual_df.groupby(['所属年月', '所属区域', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    forecast_monthly = forecast_df.groupby(['所属年月', '所属区域', '产品代码']).agg({
        '预计销售量': 'sum'
    }).reset_index()

    # 按销售员细分的预测数据
    forecast_by_salesperson = forecast_df.groupby(['所属年月', '所属区域', '销售员', '产品代码']).agg({
        '预计销售量': 'sum'
    }).reset_index()

    # 实际按销售员细分的数据
    actual_by_salesperson = actual_df.groupby(['所属年月', '所属区域', '申请人', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 重命名列，使合并更容易
    actual_by_salesperson = actual_by_salesperson.rename(columns={'申请人': '销售员'})

    # 合并预测和实际数据
    # 按区域和产品级别
    merged_monthly = pd.merge(
        actual_monthly,
        forecast_monthly,
        on=['所属年月', '所属区域', '产品代码'],
        how='outer'
    )

    # 按销售员级别
    merged_by_salesperson = pd.merge(
        actual_by_salesperson,
        forecast_by_salesperson,
        on=['所属年月', '所属区域', '销售员', '产品代码'],
        how='outer'
    )

    # 填充缺失值为0
    for df in [merged_monthly, merged_by_salesperson]:
        df['求和项:数量（箱）'] = df['求和项:数量（箱）'].fillna(0)
        df['预计销售量'] = df['预计销售量'].fillna(0)

    # 计算差异和准确率
    for df in [merged_monthly, merged_by_salesperson]:
        # 差异
        df['数量差异'] = df['求和项:数量（箱）'] - df['预计销售量']

        # 差异率 (避免除以零)
        df['数量差异率'] = df.apply(
            lambda row: ((row['求和项:数量（箱）'] - row['预计销售量']) / row['求和项:数量（箱）'] * 100)
            if row['求和项:数量（箱）'] > 0 else
            (-100 if row['预计销售量'] > 0 else 0),
            axis=1
        )

        # 使用统一准确率计算函数
        df['数量准确率'] = df.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )

    # 计算总体准确率
    national_accuracy = calculate_national_accuracy(merged_monthly)
    regional_accuracy = calculate_regional_accuracy(merged_monthly)

    # 计算销售员准确率
    salesperson_accuracy = calculate_salesperson_accuracy(merged_by_salesperson)

    # 计算占比80%的SKU
    national_top_skus = calculate_top_skus(merged_monthly, by_region=False)
    regional_top_skus = calculate_top_skus(merged_monthly, by_region=True)

    return {
        'actual_monthly': actual_monthly,
        'forecast_monthly': forecast_monthly,
        'merged_monthly': merged_monthly,
        'merged_by_salesperson': merged_by_salesperson,
        'national_accuracy': national_accuracy,
        'regional_accuracy': regional_accuracy,
        'salesperson_accuracy': salesperson_accuracy,
        'national_top_skus': national_top_skus,
        'regional_top_skus': regional_top_skus
    }


def calculate_national_accuracy(merged_df):
    """计算全国的预测准确率"""
    # 按月份汇总
    monthly_summary = merged_df.groupby('所属年月').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异
    monthly_summary['数量差异'] = monthly_summary['求和项:数量（箱）'] - monthly_summary['预计销售量']

    # 使用统一函数计算准确率
    monthly_summary['数量准确率'] = monthly_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 计算整体平均准确率 (使用安全均值计算)
    overall = {
        '数量准确率': safe_mean(monthly_summary['数量准确率'], 0)
    }

    return {
        'monthly': monthly_summary,
        'overall': overall
    }


def calculate_regional_accuracy(merged_df):
    """计算各区域的预测准确率"""
    # 按月份和区域汇总
    region_monthly_summary = merged_df.groupby(['所属年月', '所属区域']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异
    region_monthly_summary['数量差异'] = region_monthly_summary['求和项:数量（箱）'] - region_monthly_summary[
        '预计销售量']

    # 使用统一函数计算准确率
    region_monthly_summary['数量准确率'] = region_monthly_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按区域计算平均准确率 (使用安全均值计算)
    region_overall = region_monthly_summary.groupby('所属区域').agg({
        '数量准确率': lambda x: safe_mean(x, 0),
        '求和项:数量（箱）': 'sum',  # 添加总销量以便排序
        '预计销售量': 'sum'  # 添加总预测量
    }).reset_index()

    # 添加区域份额
    total_sales = region_overall['求和项:数量（箱）'].sum()
    if total_sales > 0:
        region_overall['销量占比'] = region_overall['求和项:数量（箱）'] / total_sales
    else:
        region_overall['销量占比'] = 0

    return {
        'region_monthly': region_monthly_summary,
        'region_overall': region_overall
    }


def calculate_salesperson_accuracy(merged_df):
    """计算销售员预测准确率"""
    # 按销售员汇总
    salesperson_summary = merged_df.groupby(['销售员', '所属区域']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异和准确率
    salesperson_summary['数量差异'] = salesperson_summary['求和项:数量（箱）'] - salesperson_summary['预计销售量']
    salesperson_summary['数量准确率'] = salesperson_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 添加销量份额
    total_sales = salesperson_summary['求和项:数量（箱）'].sum()
    if total_sales > 0:
        salesperson_summary['销量占比'] = salesperson_summary['求和项:数量（箱）'] / total_sales
    else:
        salesperson_summary['销量占比'] = 0

    # 按区域汇总销售员数据
    region_salesperson = salesperson_summary.groupby('所属区域').agg({
        '数量准确率': lambda x: safe_mean(x, 0),
        '销售员': 'count'
    }).reset_index().rename(columns={'销售员': '销售员数量'})

    return {
        'salesperson_summary': salesperson_summary,
        'region_salesperson': region_salesperson
    }


def calculate_product_growth(actual_monthly, regions=None, months=None, growth_min=-100, growth_max=500):
    """
    计算产品销量增长率，用于生成备货建议
    """
    # 确保数据按时间排序
    actual_monthly['所属年月'] = pd.to_datetime(actual_monthly['所属年月'])
    actual_monthly = actual_monthly.sort_values('所属年月')

    # 应用区域筛选
    if regions and len(regions) > 0:
        filtered_data = actual_monthly[actual_monthly['所属区域'].isin(regions)]
    else:
        filtered_data = actual_monthly  # 如果没有区域筛选，使用全部数据

    # 应用月份筛选
    if months and len(months) > 0:
        months_datetime = pd.to_datetime(months)
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months_datetime)]

    # 按产品和月份汇总筛选后的区域销量
    filtered_monthly_sales = filtered_data.groupby(['所属年月', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 创建年和月字段
    filtered_monthly_sales['年'] = filtered_monthly_sales['所属年月'].dt.year
    filtered_monthly_sales['月'] = filtered_monthly_sales['所属年月'].dt.month

    # 准备用于计算增长率的数据结构
    growth_data = []

    # 获取所有产品的唯一列表
    products = filtered_monthly_sales['产品代码'].unique()

    # 获取所有年份和月份
    years = filtered_monthly_sales['年'].unique()
    years.sort()

    # 检查是否有足够的数据进行增长率计算
    if len(filtered_monthly_sales) > 0:
        # 为每个产品计算月度增长率
        for product in products:
            product_data = filtered_monthly_sales[filtered_monthly_sales['产品代码'] == product]

            # 按年月对产品销量进行排序
            product_data = product_data.sort_values(['年', '月'])

            # 如果产品有多个月的数据，计算环比增长率（与上月相比）
            if len(product_data) > 1:
                for i in range(1, len(product_data)):
                    current_row = product_data.iloc[i]
                    prev_row = product_data.iloc[i - 1]

                    # 计算当前月环比增长率
                    current_sales = current_row['求和项:数量（箱）']
                    prev_sales = prev_row['求和项:数量（箱）']

                    if prev_sales > 0:
                        growth_rate = (current_sales - prev_sales) / prev_sales * 100
                        # 限制异常值
                        growth_rate = max(min(growth_rate, growth_max), growth_min)
                    else:
                        growth_rate = 0 if current_sales == 0 else 100

                    # 记录环比增长率数据
                    growth_data.append({
                        '产品代码': product,
                        '年': current_row['年'],
                        '月': current_row['月'],
                        '当月销量': current_sales,
                        '上月销量': prev_sales,
                        '销量增长率': growth_rate,
                        '计算方式': '环比'  # 标记为环比计算
                    })

            # 尝试计算同期同比增长率（如果有前一年的数据）- 优先使用同比数据
            if len(years) > 1:
                for year in years[1:]:  # 从第二年开始
                    prev_year = year - 1

                    # 获取当前年和前一年的数据
                    current_year_data = product_data[product_data['年'] == year]
                    prev_year_data = product_data[product_data['年'] == prev_year]

                    # 为每个月计算同比增长率
                    for _, curr_row in current_year_data.iterrows():
                        curr_month = curr_row['月']
                        curr_sales = curr_row['求和项:数量（箱）']

                        # 寻找前一年同月数据
                        prev_month_data = prev_year_data[prev_year_data['月'] == curr_month]

                        if not prev_month_data.empty:
                            prev_sales = prev_month_data.iloc[0]['求和项:数量（箱）']

                            if prev_sales > 0:
                                yoy_growth_rate = (curr_sales - prev_sales) / prev_sales * 100
                                # 限制异常值
                                yoy_growth_rate = max(min(yoy_growth_rate, growth_max), growth_min)
                            else:
                                yoy_growth_rate = 0 if curr_sales == 0 else 100

                            # 记录同比增长率
                            # 优先使用同比数据（替换之前的环比数据，如果存在）
                            existing_entry = next((item for item in growth_data if
                                                   item['产品代码'] == product and
                                                   item['年'] == year and
                                                   item['月'] == curr_month), None)

                            if existing_entry:
                                existing_entry['销量增长率'] = yoy_growth_rate
                                existing_entry['同比上年销量'] = prev_sales
                                existing_entry['计算方式'] = '同比'  # 更新为同比计算
                            else:
                                growth_data.append({
                                    '产品代码': product,
                                    '年': year,
                                    '月': curr_month,
                                    '当月销量': curr_sales,
                                    '同比上年销量': prev_sales,
                                    '销量增长率': yoy_growth_rate,
                                    '计算方式': '同比'  # 标记为同比计算
                                })

    # 创建增长率DataFrame
    growth_df = pd.DataFrame(growth_data)

    # 如果有增长数据，添加趋势判断和备货建议
    if not growth_df.empty:
        try:
            # 取最近一个月的增长率
            latest_growth = growth_df.sort_values(['年', '月'], ascending=False).groupby(
                '产品代码').first().reset_index()

            # 过滤无效增长率值
            latest_growth = latest_growth[latest_growth['销量增长率'].notna()]
            latest_growth = latest_growth[np.isfinite(latest_growth['销量增长率'])]

            if not latest_growth.empty:
                # 添加趋势判断
                latest_growth['趋势'] = np.where(
                    latest_growth['销量增长率'] > 10, '强劲增长',
                    np.where(
                        latest_growth['销量增长率'] > 0, '增长',
                        np.where(
                            latest_growth['销量增长率'] > -10, '轻微下降',
                            '显著下降'
                        )
                    )
                )

                # 添加备货建议
                latest_growth['备货建议对象'] = latest_growth['销量增长率'].apply(generate_recommendation)
                latest_growth['备货建议'] = latest_growth['备货建议对象'].apply(lambda x: x['建议'])
                latest_growth['调整比例'] = latest_growth['备货建议对象'].apply(lambda x: x['调整比例'])
                latest_growth['建议颜色'] = latest_growth['备货建议对象'].apply(lambda x: x['颜色'])
                latest_growth['建议样式类'] = latest_growth['备货建议对象'].apply(lambda x: x['样式类'])
                latest_growth['建议图标'] = latest_growth['备货建议对象'].apply(lambda x: x['图标'])
            else:
                # 创建空的结果框架
                latest_growth = pd.DataFrame(columns=growth_df.columns)
        except Exception as e:
            # 记录错误但继续执行
            print(f"处理增长率数据时出错: {str(e)}")
            latest_growth = pd.DataFrame(columns=growth_df.columns)

        return {
            'all_growth': growth_df,
            'latest_growth': latest_growth
        }
    else:
        return {
            'all_growth': pd.DataFrame(),
            'latest_growth': pd.DataFrame()
        }


def calculate_top_skus(merged_df, by_region=False):
    """计算占销售量80%的SKU及其准确率 - 修复空区域问题"""
    if merged_df.empty:
        return {} if by_region else pd.DataFrame()

    if by_region:
        # 按区域、产品汇总
        grouped = merged_df.groupby(['所属区域', '产品代码']).agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算准确率
        grouped['数量准确率'] = grouped.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )

        # 计算各区域的占比80%SKU
        results = {}
        for region in grouped['所属区域'].unique():
            if pd.isna(region) or region is None or region == 'None':
                continue  # 跳过空区域

            region_data = grouped[grouped['所属区域'] == region].copy()
            if region_data.empty:
                continue  # 跳过没有数据的区域

            total_sales = region_data['求和项:数量（箱）'].sum()
            if total_sales <= 0:
                continue  # 跳过销售量为0的区域

            # 按销售量降序排序
            region_data = region_data.sort_values('求和项:数量（箱）', ascending=False)

            # 计算累计销售量和占比
            region_data['累计销售量'] = region_data['求和项:数量（箱）'].cumsum()
            region_data['累计占比'] = region_data['累计销售量'] / total_sales * 100

            # 筛选占比80%的SKU
            top_skus = region_data[region_data['累计占比'] <= 80].copy()

            # 如果没有SKU达到80%阈值，至少取前3个SKU
            if top_skus.empty:
                top_skus = region_data.head(min(3, len(region_data)))

            results[region] = top_skus

        return results
    else:
        # 全国汇总
        grouped = merged_df.groupby('产品代码').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算准确率
        grouped['数量准确率'] = grouped.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )

        total_sales = grouped['求和项:数量（箱）'].sum()
        if total_sales <= 0:
            return pd.DataFrame(columns=grouped.columns)  # 返回空DataFrame但保持列结构

        # 按销售量降序排序
        grouped = grouped.sort_values('求和项:数量（箱）', ascending=False)

        # 计算累计销售量和占比
        grouped['累计销售量'] = grouped['求和项:数量（箱）'].cumsum()
        grouped['累计占比'] = grouped['累计销售量'] / total_sales * 100

        # 筛选占比80%的SKU
        top_skus = grouped[grouped['累计占比'] <= 80].copy()

        # 如果没有SKU达到80%阈值，至少取前5个SKU
        if top_skus.empty:
            top_skus = grouped.head(min(5, len(grouped)))

        return top_skus


# 创建热力图
def create_heatmap(data, index, columns, values, title, colorscale='RdYlGn', reverse_scale=False):
    """创建热力图"""
    # 数据透视
    pivot_data = data.pivot_table(index=index, columns=columns, values=values, aggfunc='mean')

    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=colorscale,
        reversescale=reverse_scale,
        colorbar=dict(title=values),
        hovertemplate=f"{index}: %{{y}}<br>{columns}: %{{x}}<br>{values}: %{{z:.2f}}<extra></extra>"
    ))

    fig.update_layout(
        title=title,
        xaxis_title=columns,
        yaxis_title=index,
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=80, b=50)
    )

    return fig


# 创建树状图
def create_treemap(data, path, values, title, color=None, color_scale='RdYlGn'):
    """创建树状图"""
    if color:
        fig = px.treemap(
            data,
            path=path,
            values=values,
            color=color,
            color_continuous_scale=color_scale,
            title=title
        )
    else:
        fig = px.treemap(
            data,
            path=path,
            values=values,
            title=title
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='white'
    )

    return fig


# 创建气泡图
def create_bubble_chart(data, x, y, size, color, hover_name, title, color_discrete_map=None):
    """创建气泡图"""

    # 计算最佳气泡大小范围
    if data[size].max() > 0:
        size_max = min(50, max(20, 50 * data[size].quantile(0.9) / data[size].max()))
    else:
        size_max = 20

    fig = px.scatter(
        data,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        size_max=size_max,
        title=title,
        color_discrete_map=color_discrete_map
    )

    fig.update_layout(
        xaxis=dict(
            title=x,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(220,220,220,0.8)',
            tickformat=",",
            showexponent="none"
        ),
        yaxis=dict(
            title=y,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(220,220,220,0.8)'
        ),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=50)
    )

    # 添加零线
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)

    return fig


# 创建统一导航栏函数
def render_navigation():
    """渲染导航栏和面包屑"""
    # 获取当前视图路径
    current_view = st.session_state.get('current_view', 'overview')
    region = st.session_state.get('selected_region', None)
    salesperson = st.session_state.get('selected_salesperson', None)
    product = st.session_state.get('selected_product', None)

    # 创建面包屑导航
    breadcrumb = '<div class="breadcrumb">'

    # 首页链接
    breadcrumb += '<span class="breadcrumb-item"><a class="breadcrumb-link" onclick="parent.postMessage({\'type\': \'streamlit:setSessionState\', \'state\': {\'current_view\': \'overview\', \'selected_region\': null, \'selected_salesperson\': null, \'selected_product\': null}}, \'*\')">首页</a></span>'

    # 区域链接
    if region:
        breadcrumb += f'<span class="breadcrumb-item"><a class="breadcrumb-link" onclick="parent.postMessage({{"type": "streamlit:setSessionState", "state": {{"current_view": "region", "selected_region": "{region}", "selected_salesperson": null, "selected_product": null}}}}, \'*\')">{region}区域</a></span>'

    # 销售员链接
    if salesperson:
        breadcrumb += f'<span class="breadcrumb-item"><a class="breadcrumb-link" onclick="parent.postMessage({{"type": "streamlit:setSessionState", "state": {{"current_view": "salesperson", "selected_region": "{region}", "selected_salesperson": "{salesperson}", "selected_product": null}}}}, \'*\')">{salesperson}</a></span>'

    # 产品链接
    if product:
        breadcrumb += f'<span class="breadcrumb-item"><span class="breadcrumb-current">{product}</span></span>'
    elif current_view == 'region':
        breadcrumb += f'<span class="breadcrumb-item"><span class="breadcrumb-current">{region}区域分析</span></span>'
    elif current_view == 'salesperson':
        breadcrumb += f'<span class="breadcrumb-item"><span class="breadcrumb-current">{salesperson}销售分析</span></span>'
    elif current_view == 'products':
        breadcrumb += f'<span class="breadcrumb-item"><span class="breadcrumb-current">产品分析</span></span>'
    else:
        breadcrumb += f'<span class="breadcrumb-item"><span class="breadcrumb-current">销售预测总览</span></span>'

    breadcrumb += '</div>'

    st.markdown(breadcrumb, unsafe_allow_html=True)

    return current_view


# 创建统一筛选器函数
def render_filters(all_months, all_regions, default_months=None, default_regions=None):
    """渲染统一的筛选面板"""
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

        with col1:
            # 默认选择最近3个月
            if default_months is None:
                last_three = get_last_three_months()
                valid_last_months = [m for m in last_three if m in all_months]
                default_months = valid_last_months if valid_last_months else ([all_months[-1]] if all_months else [])

            months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=default_months,
                key="filter_months"
            )

        with col2:
            # 默认选择所有区域
            if default_regions is None:
                default_regions = all_regions

            regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=default_regions,
                key="filter_regions"
            )

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("应用筛选", use_container_width=True):
                # 更新session状态
                st.session_state['filter_months'] = months
                st.session_state['filter_regions'] = regions
                st.rerun()

        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("重置筛选", use_container_width=True):
                # 重置为默认值
                st.session_state['filter_months'] = default_months
                st.session_state['filter_regions'] = default_regions
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 如果没有选择月份或区域，显示警告
    if not months or not regions:
        st.warning("请选择至少一个月份和一个区域进行分析。")
        return None, None

    return months, regions


# 主仪表板函数
def render_dashboard():
    """渲染主仪表板"""
    # 添加Logo
    add_logo()

    # 标题
    st.markdown('<div class="main-header">销售预测准确率分析仪表盘</div>', unsafe_allow_html=True)

    # 渲染导航
    current_view = render_navigation()

    # 主数据加载 - 默认使用示例数据
    DEFAULT_ACTUAL_FILE = "2409~250224出货数据.xlsx"
    DEFAULT_FORECAST_FILE = "2409~2502人工预测.xlsx"
    DEFAULT_PRODUCT_FILE = "产品信息.xlsx"

    # 侧边栏控制 - 数据加载
    with st.sidebar:
        st.header("📂 数据源设置")
        use_default_files = st.checkbox("使用默认文件", value=True, help="使用指定的默认文件路径")

        if use_default_files:
            actual_data = load_actual_data(DEFAULT_ACTUAL_FILE)
            forecast_data = load_forecast_data(DEFAULT_FORECAST_FILE)
            product_info = load_product_info(DEFAULT_PRODUCT_FILE)

            if os.path.exists(DEFAULT_ACTUAL_FILE):
                st.success(f"已成功加载默认出货数据文件")
            else:
                st.warning(f"默认出货数据文件不存在，使用示例数据")

            if os.path.exists(DEFAULT_FORECAST_FILE):
                st.success(f"已成功加载默认预测数据文件")
            else:
                st.warning(f"默认预测数据文件不存在，使用示例数据")

            if os.path.exists(DEFAULT_PRODUCT_FILE):
                st.success(f"已成功加载默认产品信息文件")
            else:
                st.warning(f"默认产品信息文件不存在，使用示例数据")
        else:
            actual_file = st.file_uploader("上传出货数据文件", type=["xlsx", "xls"])
            forecast_file = st.file_uploader("上传预测数据文件", type=["xlsx", "xls"])
            product_file = st.file_uploader("上传产品信息文件", type=["xlsx", "xls"])

            actual_data = load_actual_data(actual_file if actual_file else None)
            forecast_data = load_forecast_data(forecast_file if forecast_file else None)
            product_info = load_product_info(product_file if product_file else None)

    # 获取所有月份和区域
    common_months = get_common_months(actual_data, forecast_data)
    all_regions = sorted(list(set(actual_data['所属区域'].unique()) | set(forecast_data['所属区域'].unique())))

    # 筛选共有月份数据
    actual_data_filtered = actual_data[actual_data['所属年月'].isin(common_months)]
    forecast_data_filtered = forecast_data[forecast_data['所属年月'].isin(common_months)]

    # 根据当前视图渲染对应内容
    if current_view == 'overview':
        render_overview(actual_data_filtered, forecast_data_filtered, product_info, common_months, all_regions)
    elif current_view == 'region':
        render_region_view(actual_data_filtered, forecast_data_filtered, product_info, common_months, all_regions)
    elif current_view == 'salesperson':
        render_salesperson_view(actual_data_filtered, forecast_data_filtered, product_info, common_months, all_regions)
    elif current_view == 'product':
        render_product_view(actual_data_filtered, forecast_data_filtered, product_info, common_months, all_regions)
    else:
        # 默认视图 - 通过标签页选择
        render_tabs_view(actual_data_filtered, forecast_data_filtered, product_info, common_months, all_regions)


# 首页总览视图
def render_overview(actual_data, forecast_data, product_info, all_months, all_regions):
    """渲染首页总览"""
    # 渲染筛选器
    selected_months, selected_regions = render_filters(all_months, all_regions)
    if not selected_months or not selected_regions:
        return

    # 筛选数据
    filtered_actual = filter_data(actual_data, selected_months, selected_regions)
    filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

    # 处理数据
    processed_data = process_data(filtered_actual, filtered_forecast, product_info)

    # 布局 - 关键指标区
    st.markdown('<div class="sub-header">🔍 预测准确率关键指标</div>', unsafe_allow_html=True)

    # 获取关键指标
    national_accuracy = processed_data['national_accuracy']['overall']['数量准确率'] * 100
    regional_accuracy = processed_data['regional_accuracy']['region_overall']

    # 创建指标卡
    col1, col2, col3, col4 = st.columns(4)

    # 全国准确率
    with col1:
        accuracy_color = "green" if national_accuracy >= 80 else "orange" if national_accuracy >= 60 else "red"
        st.markdown(f"""
        <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'tab_accuracy'}}}}, '*')">
            <p class="card-header">全国预测准确率</p>
            <p class="card-value" style="color:{accuracy_color};">{national_accuracy:.2f}%</p>
            <p class="card-text">整体预测精度</p>
        </div>
        """, unsafe_allow_html=True)

    # 最高准确率区域
    with col2:
        if not regional_accuracy.empty:
            best_region = regional_accuracy.loc[regional_accuracy['数量准确率'].idxmax()]
            best_accuracy = best_region['数量准确率'] * 100
            best_color = "green" if best_accuracy >= 80 else "orange" if best_accuracy >= 60 else "red"

            st.markdown(f"""
            <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'region', 'selected_region': '{best_region['所属区域']}'}}}}, '*')">
                <p class="card-header">最高准确率区域</p>
                <p class="card-value" style="color:{best_color};">{best_region['所属区域']} ({best_accuracy:.2f}%)</p>
                <p class="card-text">点击查看详情</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">最高准确率区域</p>
                <p class="card-value">暂无数据</p>
                <p class="card-text">请检查数据</p>
            </div>
            """, unsafe_allow_html=True)

    # 最低准确率区域
    with col3:
        if not regional_accuracy.empty:
            worst_region = regional_accuracy.loc[regional_accuracy['数量准确率'].idxmin()]
            worst_accuracy = worst_region['数量准确率'] * 100
            worst_color = "green" if worst_accuracy >= 80 else "orange" if worst_accuracy >= 60 else "red"

            st.markdown(f"""
            <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'region', 'selected_region': '{worst_region['所属区域']}'}}}}, '*')">
                <p class="card-header">最低准确率区域</p>
                <p class="card-value" style="color:{worst_color};">{worst_region['所属区域']} ({worst_accuracy:.2f}%)</p>
                <p class="card-text">点击查看详情</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">最低准确率区域</p>
                <p class="card-value">暂无数据</p>
                <p class="card-text">请检查数据</p>
            </div>
            """, unsafe_allow_html=True)

    # 重点SKU准确率
    with col4:
        if 'national_top_skus' in processed_data and not processed_data['national_top_skus'].empty:
            top_skus_accuracy = safe_mean(processed_data['national_top_skus']['数量准确率']) * 100
            top_skus_color = "green" if top_skus_accuracy >= 80 else "orange" if top_skus_accuracy >= 60 else "red"
            top_skus_count = len(processed_data['national_top_skus'])

            st.markdown(f"""
            <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'product'}}}}, '*')">
                <p class="card-header">重点SKU准确率</p>
                <p class="card-value" style="color:{top_skus_color};">{top_skus_accuracy:.2f}%</p>
                <p class="card-text">占销量80%的{top_skus_count}个SKU</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">重点SKU准确率</p>
                <p class="card-value">暂无数据</p>
                <p class="card-text">请检查数据</p>
            </div>
            """, unsafe_allow_html=True)

    # 区域热力图
    st.markdown('<div class="sub-header">🌐 区域预测准确率热力图</div>', unsafe_allow_html=True)

    if not processed_data['regional_accuracy']['region_monthly'].empty:
        # 准备热力图数据
        heatmap_data = processed_data['regional_accuracy']['region_monthly']

        # 绘制热力图
        heatmap_fig = create_heatmap(
            data=heatmap_data,
            index='所属区域',
            columns='所属年月',
            values='数量准确率',
            title="各区域月度预测准确率热力图",
            colorscale='RdYlGn',
            reverse_scale=False
        )

        # 显示图表
        st.plotly_chart(heatmap_fig, use_container_width=True)

        # 添加图表说明
        st.markdown("""
        <div class="chart-explanation">
            <b>图表说明:</b> 热力图显示了各区域在不同月份的预测准确率，颜色从红色到绿色表示准确率从低到高。
            您可以通过点击图表中的区域名称快速跳转到区域详细分析页面。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域热力图。")

    # 销售员准确率分布
    st.markdown('<div class="sub-header">👥 销售员预测准确率分布</div>', unsafe_allow_html=True)

    if 'salesperson_accuracy' in processed_data and not processed_data['salesperson_accuracy'][
        'salesperson_summary'].empty:
        # 准备数据
        salesperson_data = processed_data['salesperson_accuracy']['salesperson_summary']

        # 按准确率降序排序
        salesperson_data = salesperson_data.sort_values('数量准确率', ascending=False)

        # 选择前10名和后10名销售员
        if len(salesperson_data) > 20:
            top10 = salesperson_data.head(10)
            bottom10 = salesperson_data.tail(10)
            display_data = pd.concat([top10, bottom10])
        else:
            display_data = salesperson_data

        # 转换准确率为百分比显示
        display_data['数量准确率_百分比'] = display_data['数量准确率'] * 100

        # 创建气泡图 - 销售员准确率与销量关系
        fig = create_bubble_chart(
            data=display_data,
            x='求和项:数量（箱）',
            y='数量准确率_百分比',
            size='求和项:数量（箱）',
            color='所属区域',
            hover_name='销售员',
            title="销售员准确率与销量关系"
        )

        # 显示图表
        st.plotly_chart(fig, use_container_width=True)

        # 添加图表说明
        st.markdown("""
        <div class="chart-explanation">
            <b>图表说明:</b> 气泡图展示了销售员的预测准确率与销量关系，气泡大小表示销量大小，颜色区分所属区域。
            点击气泡可以查看该销售员的详细预测情况。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成销售员准确率分布图。")

    # 获取产品增长率数据
    product_growth = calculate_product_growth(actual_monthly=actual_data, regions=selected_regions,
                                              months=selected_months)

    # 产品增长与准确率
    st.markdown('<div class="sub-header">📈 产品增长与准确率分析</div>', unsafe_allow_html=True)

    if 'latest_growth' in product_growth and not product_growth[
        'latest_growth'].empty and 'national_top_skus' in processed_data:
        try:
            # 合并产品增长率和准确率数据
            growth_data = product_growth['latest_growth']
            accuracy_data = processed_data['national_top_skus']

            # 确保有产品代码列
            if '产品代码' in growth_data.columns and '产品代码' in accuracy_data.columns:
                # 合并数据
                merged_product_data = pd.merge(
                    growth_data,
                    accuracy_data[['产品代码', '数量准确率', '求和项:数量（箱）']],
                    on='产品代码',
                    how='inner'
                )

                # 确保有足够的数据
                if not merged_product_data.empty:
                    # 转换准确率为百分比
                    merged_product_data['数量准确率_百分比'] = merged_product_data['数量准确率'] * 100

                    # 添加产品名称
                    merged_product_data['产品名称'] = merged_product_data['产品代码'].apply(
                        lambda x: format_product_code(x, product_info, include_name=True)
                    )

                    # 创建四象限散点图
                    fig = go.Figure()

                    # 添加散点
                    fig.add_trace(go.Scatter(
                        x=merged_product_data['求和项:数量（箱）'],
                        y=merged_product_data['销量增长率'],
                        mode='markers',
                        marker=dict(
                            size=merged_product_data['数量准确率_百分比'] / 2 + 10,  # 调整大小
                            color=merged_product_data['数量准确率_百分比'],
                            colorscale='RdYlGn',
                            colorbar=dict(title='准确率 (%)'),
                            cmin=0,
                            cmax=100,
                            line=dict(width=1, color='white')
                        ),
                        text=merged_product_data['产品名称'],
                        hovertemplate='<b>%{text}</b><br>销量: %{x:,.0f}箱<br>增长率: %{y:.2f}%<br>准确率: %{marker.color:.2f}%<extra></extra>'
                    ))

                    # 添加四象限分割线
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    fig.add_vline(x=merged_product_data['求和项:数量（箱）'].median(), line_dash="dash",
                                  line_color="gray", line_width=1)

                    # 添加象限标签
                    median_x = merged_product_data['求和项:数量（箱）'].median()
                    max_x = merged_product_data['求和项:数量（箱）'].max()
                    max_y = merged_product_data['销量增长率'].max()
                    min_y = merged_product_data['销量增长率'].min()

                    fig.add_annotation(
                        x=median_x * 1.5,
                        y=max_y * 0.8,
                        text="高销量 + 高增长<br>(重点关注)",
                        showarrow=False,
                        font=dict(size=10, color="green")
                    )

                    fig.add_annotation(
                        x=median_x * 0.5,
                        y=max_y * 0.8,
                        text="低销量 + 高增长<br>(潜力产品)",
                        showarrow=False,
                        font=dict(size=10, color="blue")
                    )

                    fig.add_annotation(
                        x=median_x * 1.5,
                        y=min_y * 0.8,
                        text="高销量 + 负增长<br>(需警惕)",
                        showarrow=False,
                        font=dict(size=10, color="red")
                    )

                    fig.add_annotation(
                        x=median_x * 0.5,
                        y=min_y * 0.8,
                        text="低销量 + 负增长<br>(考虑调整)",
                        showarrow=False,
                        font=dict(size=10, color="orange")
                    )

                    # 更新布局
                    fig.update_layout(
                        title="产品销量-增长率-准确率分析",
                        xaxis=dict(
                            title="销量 (箱)",
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(220,220,220,0.8)',
                            tickformat=",",
                            showexponent="none"
                        ),
                        yaxis=dict(
                            title="销量增长率 (%)",
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(220,220,220,0.8)'
                        ),
                        plot_bgcolor='white',
                        margin=dict(l=20, r=20, t=50, b=50)
                    )

                    # 显示图表
                    st.plotly_chart(fig, use_container_width=True)

                    # 添加图表说明
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>图表说明:</b> 此图展示了产品的销量、增长率和准确率三个维度，气泡大小和颜色表示预测准确率（越大越绿表示准确率越高）。
                        四个象限代表不同的产品状态：右上角为核心产品（高销量高增长），左上角为潜力产品（低销量高增长），
                        右下角为需关注产品（高销量负增长），左下角为待调整产品（低销量负增长）。
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("没有足够的匹配数据来生成产品增长与准确率分析图。")
            else:
                st.warning("数据缺少必要的'产品代码'列。")
        except Exception as e:
            st.error(f"生成产品增长与准确率分析图时出错: {str(e)}")
    else:
        st.warning("没有足够的数据来生成产品增长与准确率分析图。")

    # 添加下钻引导区域
    st.markdown('<div class="sub-header">🔍 深入分析</div>', unsafe_allow_html=True)

    # 创建三个卡片用于引导下钻
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card" onclick="parent.postMessage({'type': 'streamlit:setSessionState', 'state': {'current_view': 'region'}}, '*')">
            <p class="card-header">区域准确率分析</p>
            <p class="card-value" style="font-size: 1.3rem;">点击查看 →</p>
            <p class="card-text">深入了解各区域预测准确率情况</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" onclick="parent.postMessage({'type': 'streamlit:setSessionState', 'state': {'current_view': 'salesperson'}}, '*')">
            <p class="card-header">销售员准确率分析</p>
            <p class="card-value" style="font-size: 1.3rem;">点击查看 →</p>
            <p class="card-text">分析销售员预测能力和差异</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" onclick="parent.postMessage({'type': 'streamlit:setSessionState', 'state': {'current_view': 'product'}}, '*')">
            <p class="card-header">产品预测分析</p>
            <p class="card-value" style="font-size: 1.3rem;">点击查看 →</p>
            <p class="card-text">重点SKU预测准确率和备货建议</p>
        </div>
        """, unsafe_allow_html=True)


# 区域视图
# 替换 render_region_view 函数中的错误代码
def render_region_view(actual_data, forecast_data, product_info, all_months, all_regions):
    """渲染区域分析视图"""
    # 获取选中的区域
    selected_region = st.session_state.get('selected_region')

    if not selected_region:
        # 如果没有选中区域，显示区域选择界面
        st.markdown('<div class="sub-header">🌐 区域预测准确率分析</div>', unsafe_allow_html=True)

        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions)
        if not selected_months or not selected_regions:
            return

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 显示区域准确率热力图
        if not processed_data['regional_accuracy']['region_monthly'].empty:
            # 准备热力图数据
            heatmap_data = processed_data['regional_accuracy']['region_monthly']

            # 绘制热力图
            heatmap_fig = create_heatmap(
                data=heatmap_data,
                index='所属区域',
                columns='所属年月',
                values='数量准确率',
                title="各区域月度预测准确率热力图",
                colorscale='RdYlGn',
                reverse_scale=False
            )

            # 显示图表
            st.plotly_chart(heatmap_fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 热力图显示了各区域在不同月份的预测准确率，颜色从红色到绿色表示准确率从低到高。
                点击图表上的区域名称可以查看该区域的详细分析。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成区域热力图。")

        # 显示区域准确率排名
        st.markdown('<div class="sub-header">🏆 区域预测准确率排名</div>', unsafe_allow_html=True)

        if not processed_data['regional_accuracy']['region_overall'].empty:
            # 准备数据
            region_data = processed_data['regional_accuracy']['region_overall'].copy()

            # 转换准确率为百分比
            region_data['数量准确率_百分比'] = region_data['数量准确率'] * 100

            # 按准确率降序排序
            region_data = region_data.sort_values('数量准确率', ascending=False)

            # 创建条形图
            fig = px.bar(
                region_data,
                y='所属区域',
                x='数量准确率_百分比',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                text=region_data['数量准确率_百分比'].apply(lambda x: f"{x:.2f}%"),
                hover_data={
                    '求和项:数量（箱）': ':,.0f',
                    '预计销售量': ':,.0f',
                    '销量占比': ':.2%'
                },
                labels={
                    '所属区域': '区域',
                    '数量准确率_百分比': '准确率(%)',
                    '求和项:数量（箱）': '实际销量(箱)',
                    '预计销售量': '预测销量(箱)',
                    '销量占比': '销量占比'
                },
                title="区域预测准确率排名"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100]
                ),
                yaxis=dict(title="区域"),
                coloraxis_showscale=False,
                plot_bgcolor='white'
            )

            # 添加平均线
            mean_accuracy = region_data['数量准确率_百分比'].mean()
            fig.add_vline(
                x=mean_accuracy,
                line_dash="dash",
                line_color="black",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 创建可点击的区域卡片
            st.markdown('<div class="sub-header">🔍 选择区域进行详细分析</div>', unsafe_allow_html=True)

            # 每行显示3个卡片
            cols = st.columns(3)
            for i, (_, row) in enumerate(region_data.iterrows()):
                region = row['所属区域']
                accuracy = row['数量准确率_百分比']
                accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"

                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'region', 'selected_region': '{region}'}}}}, '*')">
                        <p class="card-header">{region}区域</p>
                        <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                        <p class="card-text">销量占比: {row['销量占比']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成区域准确率排名。")
    else:
        # 显示指定区域的详细分析
        st.markdown(f'<div class="sub-header">🌐 {selected_region}区域预测准确率分析</div>', unsafe_allow_html=True)

        # 返回按钮
        if st.button("◀ 返回区域列表", key="back_to_regions"):
            st.session_state['selected_region'] = None
            st.rerun()

        # 渲染筛选器
        selected_months, _ = render_filters(all_months, all_regions, default_regions=[selected_region])
        if not selected_months:
            return

        # 筛选数据 - 只筛选选定区域
        filtered_actual = filter_data(actual_data, selected_months, [selected_region])
        filtered_forecast = filter_data(forecast_data, selected_months, [selected_region])

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 关键指标
        region_accuracy = processed_data['regional_accuracy']['region_overall']
        region_monthly = processed_data['regional_accuracy']['region_monthly']

        if not region_accuracy.empty:
            region_data = region_accuracy[region_accuracy['所属区域'] == selected_region]
            if not region_data.empty:
                accuracy = region_data['数量准确率'].iloc[0] * 100

                # 关键指标卡
                col1, col2, col3 = st.columns(3)

                with col1:
                    accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">区域准确率</p>
                        <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                        <p class="card-text">整体预测精度</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">实际销量</p>
                        <p class="card-value">{format_number(region_data['求和项:数量（箱）'].iloc[0])}箱</p>
                        <p class="card-text">选定期间内</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    diff = region_data['求和项:数量（箱）'].iloc[0] - region_data['预计销售量'].iloc[0]
                    diff_percent = (diff / region_data['求和项:数量（箱）'].iloc[0] * 100) if \
                    region_data['求和项:数量（箱）'].iloc[0] > 0 else 0
                    diff_text = "高估" if diff_percent < 0 else "低估"
                    diff_color = "red" if diff_percent < 0 else "green"

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">预测偏差</p>
                        <p class="card-value" style="color:{diff_color};">{abs(diff_percent):.2f}% {diff_text}</p>
                        <p class="card-text">预测{diff_text}{format_number(abs(diff))}箱</p>
                    </div>
                    """, unsafe_allow_html=True)

                # 月度准确率趋势
                if not region_monthly.empty:
                    region_trend = region_monthly[region_monthly['所属区域'] == selected_region].sort_values('所属年月')

                    if not region_trend.empty:
                        # 添加百分比列
                        region_trend['数量准确率_百分比'] = region_trend['数量准确率'] * 100

                        # 创建趋势图
                        fig = px.line(
                            region_trend,
                            x='所属年月',
                            y='数量准确率_百分比',
                            markers=True,
                            line_shape='linear',
                            labels={
                                '所属年月': '月份',
                                '数量准确率_百分比': '准确率(%)'
                            },
                            title=f"{selected_region}区域月度预测准确率趋势"
                        )

                        # 添加实际销量柱状图
                        fig.add_bar(
                            x=region_trend['所属年月'],
                            y=region_trend['求和项:数量（箱）'],
                            name='实际销量',
                            yaxis='y2',
                            marker_color='rgba(0, 123, 255, 0.3)',
                            hovertemplate='%{x}<br>实际销量: %{y:,.0f}箱<extra></extra>'
                        )

                        # 更新布局
                        fig.update_layout(
                            yaxis=dict(
                                title="准确率 (%)",
                                range=[0, 100],
                                tickformat='.2f',
                                side='left'
                            ),
                            yaxis2=dict(
                                title="销量 (箱)",
                                overlaying='y',
                                side='right',
                                showgrid=False,
                                tickformat=',',
                                rangemode='tozero'
                            ),
                            legend=dict(
                                orientation='h',
                                yanchor='bottom',
                                y=1.02,
                                xanchor='right',
                                x=1
                            ),
                            hovermode='x unified',
                            plot_bgcolor='white'
                        )

                        # 添加平均线
                        mean_accuracy = region_trend['数量准确率_百分比'].mean()
                        fig.add_hline(
                            y=mean_accuracy,
                            line_dash="dash",
                            line_color="red",
                            annotation_text=f"平均: {mean_accuracy:.2f}%",
                            annotation_position="top left"
                        )

                        # 显示图表
                        st.plotly_chart(fig, use_container_width=True)

                # 销售员准确率排名
                if 'salesperson_accuracy' in processed_data and not processed_data['salesperson_accuracy'][
                    'salesperson_summary'].empty:
                    st.markdown(f'<div class="sub-header">👥 {selected_region}区域销售员准确率分析</div>',
                                unsafe_allow_html=True)

                    # 筛选该区域销售员数据
                    region_salespersons = processed_data['salesperson_accuracy']['salesperson_summary']
                    region_salespersons = region_salespersons[region_salespersons['所属区域'] == selected_region]

                    if not region_salespersons.empty:
                        # 转换准确率为百分比
                        region_salespersons['数量准确率_百分比'] = region_salespersons['数量准确率'] * 100

                        # 按准确率降序排序
                        region_salespersons = region_salespersons.sort_values('数量准确率', ascending=False)

                        # 创建条形图
                        fig = px.bar(
                            region_salespersons,
                            y='销售员',
                            x='数量准确率_百分比',
                            color='数量准确率_百分比',
                            color_continuous_scale='RdYlGn',
                            range_color=[0, 100],
                            text=region_salespersons['数量准确率_百分比'].apply(lambda x: f"{x:.2f}%"),
                            hover_data={
                                '求和项:数量（箱）': ':,.0f',
                                '预计销售量': ':,.0f',
                                '销量占比': ':.2%'
                            },
                            labels={
                                '销售员': '销售员',
                                '数量准确率_百分比': '准确率(%)',
                                '求和项:数量（箱）': '实际销量(箱)',
                                '预计销售量': '预测销量(箱)',
                                '销量占比': '销量占比'
                            },
                            title=f"{selected_region}区域销售员预测准确率排名"
                        )

                        # 更新布局
                        fig.update_layout(
                            xaxis=dict(
                                title="准确率 (%)",
                                range=[0, 100]
                            ),
                            yaxis=dict(title="销售员"),
                            coloraxis_showscale=False,
                            plot_bgcolor='white',
                            height=max(400, len(region_salespersons) * 30)  # 动态调整高度
                        )

                        # 添加平均线
                        mean_accuracy = region_salespersons['数量准确率_百分比'].mean()
                        fig.add_vline(
                            x=mean_accuracy,
                            line_dash="dash",
                            line_color="black",
                            annotation_text=f"平均: {mean_accuracy:.2f}%",
                            annotation_position="top"
                        )

                        # 显示图表
                        st.plotly_chart(fig, use_container_width=True)

                        # 创建销售员点击卡片
                        st.markdown('<div class="sub-header">🔍 选择销售员进行详细分析</div>', unsafe_allow_html=True)

                        # 每行显示3个卡片
                        cols = st.columns(3)
                        for i, (_, row) in enumerate(region_salespersons.iterrows()):
                            salesperson = row['销售员']
                            accuracy = row['数量准确率_百分比']
                            accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"

                            with cols[i % 3]:
                                st.markdown(f"""
                                <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'salesperson', 'selected_region': '{selected_region}', 'selected_salesperson': '{salesperson}'}}}}, '*')">
                                    <p class="card-header">{salesperson}</p>
                                    <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                                    <p class="card-text">销量: {format_number(row['求和项:数量（箱）'])}箱</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning(f"没有找到{selected_region}区域的销售员数据。")

                # 产品准确率分析
                if 'regional_top_skus' in processed_data and selected_region in processed_data['regional_top_skus']:
                    st.markdown(f'<div class="sub-header">🛍️ {selected_region}区域重点SKU分析</div>',
                                unsafe_allow_html=True)

                    # 获取区域重点SKU
                    region_skus = processed_data['regional_top_skus'][selected_region].copy()

                    if not region_skus.empty:
                        # 转换准确率为百分比
                        region_skus['数量准确率_百分比'] = region_skus['数量准确率'] * 100

                        # 添加产品名称
                        region_skus['产品名称'] = region_skus['产品代码'].apply(
                            lambda x: format_product_code(x, product_info, include_name=True)
                        )

                        # 创建条形图
                        fig = px.bar(
                            region_skus,
                            y='产品名称',
                            x='求和项:数量（箱）',
                            color='数量准确率_百分比',
                            color_continuous_scale='RdYlGn',
                            range_color=[0, 100],
                            hover_data={
                                '数量准确率_百分比': ':.2f',
                                '预计销售量': ':,.0f',
                                '累计占比': ':.2f'
                            },
                            labels={
                                '产品名称': '产品',
                                '求和项:数量（箱）': '销量(箱)',
                                '数量准确率_百分比': '准确率(%)',
                                '预计销售量': '预测销量(箱)',
                                '累计占比': '累计占比(%)'
                            },
                            title=f"{selected_region}区域重点SKU销量与准确率"
                        )

                        # 更新布局
                        fig.update_layout(
                            xaxis=dict(
                                title="销量 (箱)",
                                tickformat=",",
                                showexponent="none"
                            ),
                            yaxis=dict(title="产品"),
                            coloraxis=dict(
                                colorbar=dict(
                                    title="准确率 (%)",
                                    tickformat=".2f"
                                )
                            ),
                            plot_bgcolor='white',
                            height=max(400, len(region_skus) * 30)  # 动态调整高度
                        )

                        # 显示图表
                        st.plotly_chart(fig, use_container_width=True)

                        # 添加图表说明
                        st.markdown("""
                        <div class="chart-explanation">
                            <b>图表说明:</b> 条形图展示了该区域销量累计占比达到80%的重点SKU及其准确率，条形长度表示销量，颜色表示准确率(绿色为高准确率，红色为低准确率)。
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"没有找到{selected_region}区域的重点SKU数据。")
            else:
                st.warning(f"没有找到{selected_region}区域的汇总数据。")
        else:
            st.warning("区域准确率数据为空，请检查数据。")


# 销售员视图
# 替换 render_salesperson_view 函数中的错误代码
def render_salesperson_view(actual_data, forecast_data, product_info, all_months, all_regions):
    """渲染销售员分析视图"""
    # 获取选中的区域和销售员
    selected_region = st.session_state.get('selected_region')
    selected_salesperson = st.session_state.get('selected_salesperson')

    if not selected_region and not selected_salesperson:
        # 销售员总览视图
        st.markdown('<div class="sub-header">👥 销售员预测准确率分析</div>', unsafe_allow_html=True)

        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions)
        if not selected_months or not selected_regions:
            return

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 销售员准确率总览
        if 'salesperson_accuracy' in processed_data and not processed_data['salesperson_accuracy'][
            'salesperson_summary'].empty:
            # 准备数据
            salesperson_data = processed_data['salesperson_accuracy']['salesperson_summary']

            # 转换准确率为百分比
            salesperson_data['数量准确率_百分比'] = salesperson_data['数量准确率'] * 100

            # 创建销售员准确率与销量关系图
            st.markdown('<div class="sub-header">🔍 销售员准确率分布</div>', unsafe_allow_html=True)

            # 创建气泡图
            fig = create_bubble_chart(
                data=salesperson_data,
                x='求和项:数量（箱）',
                y='数量准确率_百分比',
                size='求和项:数量（箱）',
                color='所属区域',
                hover_name='销售员',
                title="销售员准确率与销量关系"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 气泡图展示了销售员的预测准确率与销量关系，气泡大小表示销量大小，颜色区分所属区域。
                点击气泡可以查看该销售员的详细预测情况。理想情况下，重点销售员(大气泡)应该具有较高的准确率(位于图表上部)。
            </div>
            """, unsafe_allow_html=True)

            # 销售员准确率排名
            st.markdown('<div class="sub-header">🏆 销售员准确率排名</div>', unsafe_allow_html=True)

            # 按准确率降序排序
            top_salespersons = salesperson_data.sort_values('数量准确率', ascending=False)

            # 选择前10名和后10名
            if len(top_salespersons) > 20:
                display_salespersons = pd.concat([top_salespersons.head(10), top_salespersons.tail(10)])
            else:
                display_salespersons = top_salespersons

            # 创建条形图
            fig = px.bar(
                display_salespersons,
                y='销售员',
                x='数量准确率_百分比',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                text=display_salespersons['数量准确率_百分比'].apply(lambda x: f"{x:.2f}%"),
                hover_data={
                    '所属区域': True,
                    '求和项:数量（箱）': ':,.0f',
                    '预计销售量': ':,.0f'
                },
                labels={
                    '销售员': '销售员',
                    '数量准确率_百分比': '准确率(%)',
                    '所属区域': '区域',
                    '求和项:数量（箱）': '实际销量(箱)',
                    '预计销售量': '预测销量(箱)'
                },
                title="销售员预测准确率排名"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100]
                ),
                yaxis=dict(title="销售员"),
                coloraxis_showscale=False,
                plot_bgcolor='white',
                height=max(500, len(display_salespersons) * 25)  # 动态调整高度
            )

            # 添加平均线
            mean_accuracy = salesperson_data['数量准确率_百分比'].mean()
            fig.add_vline(
                x=mean_accuracy,
                line_dash="dash",
                line_color="black",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 按区域分组
            region_groups = salesperson_data.groupby('所属区域')

            # 创建区域选项卡
            region_tabs = st.tabs(list(region_groups.groups.keys()))

            for i, (region, group) in enumerate(region_groups):
                with region_tabs[i]:
                    # 按准确率排序
                    region_salespersons = group.sort_values('数量准确率', ascending=False)

                    # 创建销售员卡片
                    cols = st.columns(3)
                    for j, (_, row) in enumerate(region_salespersons.iterrows()):
                        salesperson = row['销售员']
                        accuracy = row['数量准确率_百分比']
                        accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"

                        with cols[j % 3]:
                            st.markdown(f"""
                            <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'salesperson', 'selected_region': '{region}', 'selected_salesperson': '{salesperson}'}}}}, '*')">
                                <p class="card-header">{salesperson}</p>
                                <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                                <p class="card-text">销量: {format_number(row['求和项:数量（箱）'])}箱</p>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成销售员分析。")

    elif selected_region and selected_salesperson:
        # 销售员详细视图
        st.markdown(f'<div class="sub-header">👤 {selected_region}区域 {selected_salesperson} 预测分析</div>',
                    unsafe_allow_html=True)

        # 返回按钮
        if st.button("◀ 返回销售员列表", key="back_to_salespersons"):
            st.session_state['selected_salesperson'] = None
            st.rerun()

        # 渲染筛选器 - 只选择特定区域和销售员
        selected_months, _ = render_filters(all_months, [selected_region], default_regions=[selected_region])
        if not selected_months:
            return

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, [selected_region])
        filtered_forecast = filter_data(forecast_data, selected_months, [selected_region])

        # 特定销售员筛选 - 实际数据中销售员可能是"申请人"
        filtered_actual = filtered_actual[filtered_actual['申请人'] == selected_salesperson]
        filtered_forecast = filtered_forecast[filtered_forecast['销售员'] == selected_salesperson]

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 检查是否有数据
        if processed_data['merged_by_salesperson'].empty:
            st.warning(f"没有找到{selected_region}区域{selected_salesperson}的预测数据。")
            return

        # 计算销售员整体指标
        salesperson_data = processed_data['merged_by_salesperson']

        total_actual = salesperson_data['求和项:数量（箱）'].sum()
        total_forecast = salesperson_data['预计销售量'].sum()
        accuracy = safe_mean(salesperson_data['数量准确率']) * 100

        # 显示关键指标
        col1, col2, col3 = st.columns(3)

        with col1:
            accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">预测准确率</p>
                <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                <p class="card-text">整体预测精度</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">实际销量</p>
                <p class="card-value">{format_number(total_actual)}箱</p>
                <p class="card-text">选定期间内</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            diff = total_actual - total_forecast
            diff_percent = (diff / total_actual * 100) if total_actual > 0 else 0
            diff_text = "高估" if diff_percent < 0 else "低估"
            diff_color = "red" if diff_percent < 0 else "green"

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">预测偏差</p>
                <p class="card-value" style="color:{diff_color};">{abs(diff_percent):.2f}% {diff_text}</p>
                <p class="card-text">预测{diff_text}{format_number(abs(diff))}箱</p>
            </div>
            """, unsafe_allow_html=True)

        # 月度准确率趋势
        st.markdown('<div class="sub-header">📈 月度预测准确率趋势</div>', unsafe_allow_html=True)

        # 按月汇总
        monthly_data = salesperson_data.groupby('所属年月').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算月度准确率
        monthly_data['数量准确率'] = monthly_data.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )
        monthly_data['数量准确率_百分比'] = monthly_data['数量准确率'] * 100

        # 创建趋势图
        if not monthly_data.empty:
            fig = px.line(
                monthly_data,
                x='所属年月',
                y='数量准确率_百分比',
                markers=True,
                line_shape='linear',
                labels={
                    '所属年月': '月份',
                    '数量准确率_百分比': '准确率(%)'
                },
                title=f"{selected_salesperson}月度预测准确率趋势"
            )

            # 添加实际销量柱状图
            fig.add_bar(
                x=monthly_data['所属年月'],
                y=monthly_data['求和项:数量（箱）'],
                name='实际销量',
                yaxis='y2',
                marker_color='rgba(0, 123, 255, 0.3)',
                hovertemplate='%{x}<br>实际销量: %{y:,.0f}箱<extra></extra>'
            )

            # 更新布局
            fig.update_layout(
                yaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100],
                    tickformat='.2f',
                    side='left'
                ),
                yaxis2=dict(
                    title="销量 (箱)",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    tickformat=',',
                    rangemode='tozero'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified',
                plot_bgcolor='white'
            )

            # 添加平均线
            mean_accuracy = monthly_data['数量准确率_百分比'].mean()
            fig.add_hline(
                y=mean_accuracy,
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top left"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("没有足够的月度数据来生成趋势图。")

        # 产品准确率分析
        st.markdown('<div class="sub-header">🛍️ 产品预测准确率分析</div>', unsafe_allow_html=True)

        # 按产品汇总
        product_data = salesperson_data.groupby('产品代码').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算产品准确率
        product_data['数量准确率'] = product_data.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )
        product_data['数量准确率_百分比'] = product_data['数量准确率'] * 100

        # 添加产品名称
        product_data['产品名称'] = product_data['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 按销量降序排序
        product_data = product_data.sort_values('求和项:数量（箱）', ascending=False)

        # 创建条形图
        if not product_data.empty:
            fig = px.bar(
                product_data,
                y='产品名称',
                x='求和项:数量（箱）',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                hover_data={
                    '数量准确率_百分比': ':.2f',
                    '预计销售量': ':,.0f'
                },
                labels={
                    '产品名称': '产品',
                    '求和项:数量（箱）': '销量(箱)',
                    '数量准确率_百分比': '准确率(%)',
                    '预计销售量': '预测销量(箱)'
                },
                title=f"{selected_salesperson}产品销量与准确率"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="销量 (箱)",
                    tickformat=",",
                    showexponent="none"
                ),
                yaxis=dict(title="产品"),
                coloraxis=dict(
                    colorbar=dict(
                        title="准确率 (%)",
                        tickformat=".2f"
                    )
                ),
                plot_bgcolor='white',
                height=max(400, len(product_data) * 30)  # 动态调整高度
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了该销售员所有产品的销量和准确率，条形长度表示销量，颜色表示准确率(绿色为高准确率，红色为低准确率)。
                重点关注销量大但准确率低的产品，这些产品对整体准确率影响最大。
            </div>
            """, unsafe_allow_html=True)

            # 准确率排名表格
            st.markdown('<div class="sub-header">📊 产品准确率排名</div>', unsafe_allow_html=True)

            # 按准确率排序
            accuracy_ranking = product_data.sort_values('数量准确率', ascending=False)

            # 显示为表格
            accuracy_ranking = accuracy_ranking[['产品名称', '数量准确率_百分比', '求和项:数量（箱）', '预计销售量']]
            accuracy_ranking.columns = ['产品', '准确率(%)', '实际销量(箱)', '预测销量(箱)']

            # 格式化
            accuracy_ranking['准确率(%)'] = accuracy_ranking['准确率(%)'].apply(lambda x: f"{x:.2f}%")
            accuracy_ranking['实际销量(箱)'] = accuracy_ranking['实际销量(箱)'].apply(lambda x: f"{int(x):,}")
            accuracy_ranking['预测销量(箱)'] = accuracy_ranking['预测销量(箱)'].apply(lambda x: f"{int(x):,}")

            st.dataframe(accuracy_ranking, use_container_width=True)

            # 识别问题产品
            low_accuracy_products = product_data[product_data['数量准确率_百分比'] < 60].sort_values('求和项:数量（箱）', ascending=False)

            if not low_accuracy_products.empty:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown('<div class="insight-title">需要改进的产品预测</div>', unsafe_allow_html=True)

                for _, row in low_accuracy_products.iterrows():
                    product_name = row['产品名称']
                    accuracy = row['数量准确率_百分比']
                    sales = row['求和项:数量（箱）']
                    forecast = row['预计销售量']
                    diff = sales - forecast
                    diff_text = "高估" if diff < 0 else "低估"

                    st.markdown(f"""
                    • <b>{product_name}</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                      销量 {format_number(sales)}箱，预测 {format_number(forecast)}箱，
                      <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("没有足够的产品数据来生成分析图表。")
    else:
        # 如果只有区域没有销售员，则重定向到区域视图
        st.session_state['current_view'] = 'region'
        st.rerun()

# 产品视图
def render_product_view(actual_data, forecast_data, product_info, all_months, all_regions):
    """渲染产品分析视图"""
    # 获取选中的产品
    selected_product = st.session_state.get('selected_product')

    if not selected_product:
        # 产品总览视图
        st.markdown('<div class="sub-header">🛍️ 产品预测准确率分析</div>', unsafe_allow_html=True)

        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions)
        if not selected_months or not selected_regions:
            return

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 重点SKU分析
        st.markdown('<div class="sub-header">💎 重点SKU分析</div>', unsafe_allow_html=True)

        if 'national_top_skus' in processed_data and not processed_data['national_top_skus'].empty:
            # 准备数据
            top_skus = processed_data['national_top_skus'].copy()

            # 转换准确率为百分比
            top_skus['数量准确率_百分比'] = top_skus['数量准确率'] * 100

            # 添加产品名称
            top_skus['产品名称'] = top_skus['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 创建热力图
            fig = px.bar(
                top_skus,
                y='产品名称',
                x='求和项:数量（箱）',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                hover_data={
                    '数量准确率_百分比': ':.2f',
                    '预计销售量': ':,.0f',
                    '累计占比': ':.2f'
                },
                labels={
                    '产品名称': '产品',
                    '求和项:数量（箱）': '销量(箱)',
                    '数量准确率_百分比': '准确率(%)',
                    '预计销售量': '预测销量(箱)',
                    '累计占比': '累计占比(%)'
                },
                title="重点SKU销量与准确率"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="销量 (箱)",
                    tickformat=",",
                    showexponent="none"
                ),
                yaxis=dict(title="产品"),
                coloraxis=dict(
                    colorbar=dict(
                        title="准确率 (%)",
                        tickformat=".2f"
                    )
                ),
                plot_bgcolor='white',
                height=max(500, len(top_skus) * 30)  # 动态调整高度
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了销量累计占比达到80%的重点SKU及其准确率，条形长度表示销量，颜色表示准确率(绿色为高准确率，红色为低准确率)。
                这些产品对整体预测准确率有最大影响，应重点关注准确率较低的重点产品。
            </div>
            """, unsafe_allow_html=True)

            # 产品点击卡片
            st.markdown('<div class="sub-header">🔍 选择产品进行详细分析</div>', unsafe_allow_html=True)

            # 每行显示3个卡片
            cols = st.columns(3)
            for i, (_, row) in enumerate(top_skus.iterrows()):
                product_code = row['产品代码']
                product_name = row['产品名称']
                accuracy = row['数量准确率_百分比']
                accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"

                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="metric-card" onclick="parent.postMessage({{'type': 'streamlit:setSessionState', 'state': {{'current_view': 'product', 'selected_product': '{product_code}'}}}}, '*')">
                        <p class="card-header">{product_name}</p>
                        <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                        <p class="card-text">销量: {format_number(row['求和项:数量（箱）'])}箱 ({row['累计占比']:.2f}%)</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成重点SKU分析。")

        # 产品增长率分析
        st.markdown('<div class="sub-header">📈 产品增长率分析</div>', unsafe_allow_html=True)

        # 计算产品增长率
        product_growth = calculate_product_growth(actual_monthly=actual_data, regions=selected_regions, months=selected_months)

        if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
            # 准备数据
            growth_data = product_growth['latest_growth'].copy()

            # 添加产品名称
            growth_data['产品名称'] = growth_data['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 创建增长率图
            fig = px.bar(
                growth_data,
                y='产品名称',
                x='销量增长率',
                color='趋势',
                orientation='h',
                color_discrete_map={
                    '强劲增长': '#1E88E5',  # 深蓝色
                    '增长': '#43A047',  # 绿色
                    '轻微下降': '#FB8C00',  # 橙色
                    '显著下降': '#E53935'  # 红色
                },
                hover_data={
                    '当月销量': ':,.0f',
                    '备货建议': True,
                    '调整比例': True
                },
                labels={
                    '产品名称': '产品',
                    '销量增长率': '增长率(%)',
                    '当月销量': '当月销量(箱)',
                    '备货建议': '备货建议',
                    '调整比例': '调整比例(%)'
                },
                title="产品销量增长率与备货建议"
            )

            # 添加零线
            fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=1)

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="增长率 (%)",
                    zeroline=False
                ),
                yaxis=dict(
                    title="产品",
                    autorange="reversed"  # 将最高增长率的产品放在顶部
                ),
                height=max(500, len(growth_data) * 30),  # 动态调整高度
                margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                plot_bgcolor='white'
            )

            # 添加标注 - 在条形旁边显示增长率
            for i, row in enumerate(growth_data.itertuples()):
                fig.add_annotation(
                    x=row.销量增长率,
                    y=row.产品名称,
                    text=f"{row.销量增长率:.1f}% {row.建议图标 if hasattr(row, '建议图标') and pd.notna(row.建议图标) else ''}",
                    showarrow=False,
                    xshift=10 if row.销量增长率 >= 0 else -10,
                    align="left" if row.销量增长率 >= 0 else "right",
                    font=dict(
                        color="#43A047" if row.销量增长率 >= 0 else "#E53935",
                        size=10
                    )
                )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了产品的销量增长率和对应的备货建议。颜色区分了不同的增长趋势：
                蓝色表示强劲增长(>10%)，绿色表示增长(0-10%)，橙色表示轻微下降(-10-0%)，红色表示显著下降(<-10%)。
                悬停可查看详细的备货建议和调整比例。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成产品增长率分析。")

        # 产品准确率排名
        st.markdown('<div class="sub-header">📊 产品准确率排名</div>', unsafe_allow_html=True)

        if 'merged_monthly' in processed_data and not processed_data['merged_monthly'].empty:
            # 按产品汇总
            product_accuracy = processed_data['merged_monthly'].groupby('产品代码').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 计算准确率
            product_accuracy['数量准确率'] = product_accuracy.apply(
                lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
                axis=1
            )
            product_accuracy['数量准确率_百分比'] = product_accuracy['数量准确率'] * 100

            # 添加产品名称
            product_accuracy['产品名称'] = product_accuracy['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 按准确率排序
            product_accuracy = product_accuracy.sort_values('数量准确率', ascending=False)

            # 创建散点图 - 销量与准确率关系
            fig = px.scatter(
                product_accuracy,
                x='求和项:数量（箱）',
                y='数量准确率_百分比',
                size='求和项:数量（箱）',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                hover_name='产品名称',
                size_max=50,
                opacity=0.8,
                labels={
                    '求和项:数量（箱）': '销量(箱)',
                    '数量准确率_百分比': '准确率(%)'
                },
                title="产品销量与准确率关系"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="销量 (箱)",
                    type='log',  # 使用对数刻度更好地显示不同销量范围
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                yaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                coloraxis_showscale=False,
                plot_bgcolor='white'
            )

            # 添加平均准确率线
            mean_accuracy = product_accuracy['数量准确率_百分比'].mean()
            fig.add_hline(
                y=mean_accuracy,
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top left"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 散点图展示了所有产品的销量与准确率关系，气泡大小表示销量大小，颜色表示准确率。
                重点关注位于图表右下区域的产品(高销量但低准确率)，这些产品对整体准确率影响最大。
            </div>
            """, unsafe_allow_html=True)

            # 分析和建议
            low_accuracy_high_sales = product_accuracy[(product_accuracy['数量准确率_百分比'] < 60) &
                                                      (product_accuracy['求和项:数量（箱）'] > product_accuracy['求和项:数量（箱）'].median())]

            if not low_accuracy_high_sales.empty:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown('<div class="insight-title">需要优先改进的产品</div>', unsafe_allow_html=True)

                st.markdown("以下产品销量高但准确率低，建议优先改进预测方法：", unsafe_allow_html=True)

                for _, row in low_accuracy_high_sales.head(5).iterrows():
                    product_name = row['产品名称']
                    accuracy = row['数量准确率_百分比']
                    sales = row['求和项:数量（箱）']
                    forecast = row['预计销售量']
                    diff = sales - forecast
                    diff_text = "高估" if diff < 0 else "低估"

                    st.markdown(f"""
                    • <b>{product_name}</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                      销量 {format_number(sales)}箱，预测 {format_number(forecast)}箱，
                      <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成产品准确率排名。")
    else:
        # 产品详细视图
        product_name = format_product_code(selected_product, product_info, include_name=True)
        st.markdown(f'<div class="sub-header">🏷️ {product_name} 预测分析</div>', unsafe_allow_html=True)

        # 返回按钮
        if st.button("◀ 返回产品列表", key="back_to_products"):
            st.session_state['selected_product'] = None
            st.rerun()

        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions)
        if not selected_months or not selected_regions:
            return

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 产品筛选
        filtered_actual = filtered_actual[filtered_actual['产品代码'] == selected_product]
        filtered_forecast = filtered_forecast[filtered_forecast['产品代码'] == selected_product]

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 检查是否有数据
        if processed_data['merged_monthly'].empty:
            st.warning(f"没有找到产品 {product_name} 的预测数据。")
            return

        # 计算产品整体指标
        product_data = processed_data['merged_monthly']

        total_actual = product_data['求和项:数量（箱）'].sum()
        total_forecast = product_data['预计销售量'].sum()
        accuracy = safe_mean(product_data['数量准确率']) * 100

        # 显示关键指标
        col1, col2, col3 = st.columns(3)

        with col1:
            accuracy_color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">预测准确率</p>
                <p class="card-value" style="color:{accuracy_color};">{accuracy:.2f}%</p>
                <p class="card-text">整体预测精度</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">实际销量</p>
                <p class="card-value">{format_number(total_actual)}箱</p>
                <p class="card-text">选定期间内</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            diff = total_actual - total_forecast
            diff_percent = (diff / total_actual * 100) if total_actual > 0 else 0
            diff_text = "高估" if diff_percent < 0 else "低估"
            diff_color = "red" if diff_percent < 0 else "green"

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">预测偏差</p>
                <p class="card-value" style="color:{diff_color};">{abs(diff_percent):.2f}% {diff_text}</p>
                <p class="card-text">预测{diff_text}{format_number(abs(diff))}箱</p>
            </div>
            """, unsafe_allow_html=True)

        # 月度准确率趋势
        st.markdown('<div class="sub-header">📈 月度预测准确率趋势</div>', unsafe_allow_html=True)

        # 按月汇总
        monthly_data = product_data.groupby('所属年月').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算月度准确率
        monthly_data['数量准确率'] = monthly_data.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )
        monthly_data['数量准确率_百分比'] = monthly_data['数量准确率'] * 100
        monthly_data['差异率'] = monthly_data.apply(
            lambda row: ((row['求和项:数量（箱）'] - row['预计销售量']) / row['求和项:数量（箱）'] * 100)
                         if row['求和项:数量（箱）'] > 0 else 0,
            axis=1
        )

        # 创建趋势图
        if not monthly_data.empty:
            # 销量与预测对比图
            fig1 = go.Figure()

            # 实际销量柱状图
            fig1.add_trace(go.Bar(
                x=monthly_data['所属年月'],
                y=monthly_data['求和项:数量（箱）'],
                name='实际销量',
                marker_color='royalblue'
            ))

            # 预测销量柱状图
            fig1.add_trace(go.Bar(
                x=monthly_data['所属年月'],
                y=monthly_data['预计销售量'],
                name='预测销量',
                marker_color='lightcoral'
            ))

            # 更新布局
            fig1.update_layout(
                title=f"{product_name} 月度销量与预测对比",
                xaxis=dict(title="月份"),
                yaxis=dict(
                    title="销量 (箱)",
                    tickformat=",",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                barmode='group',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified',
                plot_bgcolor='white'
            )

            # 显示图表
            st.plotly_chart(fig1, use_container_width=True)

            # 准确率趋势图
            fig2 = go.Figure()

            # 准确率线
            fig2.add_trace(go.Scatter(
                x=monthly_data['所属年月'],
                y=monthly_data['数量准确率_百分比'],
                mode='lines+markers',
                name='准确率',
                line=dict(color='green', width=2),
                marker=dict(size=8)
            ))

            # 差异率线
            fig2.add_trace(go.Scatter(
                x=monthly_data['所属年月'],
                y=monthly_data['差异率'],
                mode='lines+markers',
                name='差异率',
                line=dict(color='orange', width=2, dash='dash'),
                marker=dict(size=8)
            ))

            # 添加零线
            fig2.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

            # 更新布局
            fig2.update_layout(
                title=f"{product_name} 月度准确率与差异率趋势",
                xaxis=dict(title="月份"),
                yaxis=dict(
                    title="百分比 (%)",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified',
                plot_bgcolor='white'
            )

            # 显示图表
            st.plotly_chart(fig2, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 上图展示了产品的月度销量与预测对比，蓝色柱表示实际销量，红色柱表示预测销量。
                下图展示了产品的月度准确率（绿线）和差异率（橙线）趋势。差异率为正表示预测低估，为负表示预测高估。
                通过对比这两个图表，可以分析产品预测的准确性随时间的变化以及潜在的季节性因素。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的月度数据来生成趋势图。")

        # 区域准确率分析
        st.markdown('<div class="sub-header">🌐 区域准确率分析</div>', unsafe_allow_html=True)

        # 按区域汇总
        region_data = product_data.groupby('所属区域').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算区域准确率
        region_data['数量准确率'] = region_data.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )
        region_data['数量准确率_百分比'] = region_data['数量准确率'] * 100
        region_data['差异率'] = region_data.apply(
            lambda row: ((row['求和项:数量（箱）'] - row['预计销售量']) / row['求和项:数量（箱）'] * 100)
                         if row['求和项:数量（箱）'] > 0 else 0,
            axis=1
        )

        # 创建区域准确率图
        if not region_data.empty:
            # 排序
            region_data = region_data.sort_values('数量准确率', ascending=False)

            # 创建条形图
            fig = go.Figure()

            # 准确率条
            fig.add_trace(go.Bar(
                y=region_data['所属区域'],
                x=region_data['数量准确率_百分比'],
                name='准确率',
                marker_color='green',
                orientation='h'
            ))

            # 添加销量文本
            for i, row in enumerate(region_data.itertuples()):
                fig.add_annotation(
                    y=row.所属区域,
                    x=row.数量准确率_百分比 + 5,  # 位置稍微偏移
                    text=f"销量: {format_number(row['求和项:数量（箱）'])}箱",
                    showarrow=False,
                    font=dict(size=10),
                    align="left"
                )

            # 更新布局
            fig.update_layout(
                title=f"{product_name} 各区域准确率",
                xaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                yaxis=dict(title="区域"),
                showlegend=False,
                plot_bgcolor='white'
            )

            # 添加平均线
            mean_accuracy = region_data['数量准确率_百分比'].mean()
            fig.add_vline(
                x=mean_accuracy,
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了产品在各区域的预测准确率，颜色深浅表示准确率高低。
                右侧标注显示了各区域产品的销量。通过对比可以发现哪些区域对该产品的预测最准确/最不准确。
            </div>
            """, unsafe_allow_html=True)

            # 分析和建议
            low_accuracy_regions = region_data[region_data['数量准确率_百分比'] < 60].sort_values('求和项:数量（箱）', ascending=False)

            if not low_accuracy_regions.empty:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown('<div class="insight-title">需要改进的区域预测</div>', unsafe_allow_html=True)

                for _, row in low_accuracy_regions.iterrows():
                    region = row['所属区域']
                    accuracy = row['数量准确率_百分比']
                    sales = row['求和项:数量（箱）']
                    forecast = row['预计销售量']
                    diff = sales - forecast
                    diff_text = "高估" if diff < 0 else "低估"

                    st.markdown(f"""
                    • <b>{region}区域</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                      销量 {format_number(sales)}箱，预测 {format_number(forecast)}箱，
                      <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("没有足够的区域数据来生成分析图表。")

        # 销售员准确率分析
        st.markdown('<div class="sub-header">👥 销售员准确率分析</div>', unsafe_allow_html=True)

        # 获取销售员数据
        salesperson_data = processed_data['merged_by_salesperson']

        if not salesperson_data.empty:
            # 按销售员汇总
            sp_summary = salesperson_data.groupby(['销售员', '所属区域']).agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 计算准确率
            sp_summary['数量准确率'] = sp_summary.apply(
                lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
                axis=1
            )
            sp_summary['数量准确率_百分比'] = sp_summary['数量准确率'] * 100

            # 排序
            sp_summary = sp_summary.sort_values('数量准确率', ascending=False)

            # 选择前10名销售员
            display_data = sp_summary.head(10) if len(sp_summary) > 10 else sp_summary

            # 创建条形图
            fig = px.bar(
                display_data,
                y='销售员',
                x='数量准确率_百分比',
                color='所属区域',
                hover_data={
                    '求和项:数量（箱）': ':,.0f',
                    '预计销售量': ':,.0f'
                },
                labels={
                    '销售员': '销售员',
                    '数量准确率_百分比': '准确率(%)',
                    '所属区域': '区域',
                    '求和项:数量（箱）': '实际销量(箱)',
                    '预计销售量': '预测销量(箱)'
                },
                title=f"{product_name} 销售员准确率排名"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="准确率 (%)",
                    range=[0, 100],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(220,220,220,0.8)'
                ),
                yaxis=dict(title="销售员"),
                plot_bgcolor='white',
                height=max(400, len(display_data) * 30)  # 动态调整高度
            )

            # 添加平均线
            mean_accuracy = sp_summary['数量准确率_百分比'].mean()
            fig.add_vline(
                x=mean_accuracy,
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均: {mean_accuracy:.2f}%",
                annotation_position="top"
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了销售员对该产品的预测准确率排名，颜色区分了销售员所属区域。
                可以分析哪些销售员对该产品预测最准确/最不准确，以及不同区域销售员的预测差异。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的销售员数据来生成分析图表。")

# 标签页视图 - 保留支持传统标签页模式
def render_tabs_view(actual_data, forecast_data, product_info, all_months, all_regions):
    """渲染传统标签页视图"""

    # 创建标签页
    tabs = st.tabs(["📊 总览与历史", "🔍 预测差异分析", "📈 产品趋势", "🔍 重点SKU分析"])

    # 获取预设的筛选条件
    default_months = st.session_state.get('filter_months', [])
    default_regions = st.session_state.get('filter_regions', [])

    # 如果没有默认值，设置为最近3个月和所有区域
    if not default_months:
        last_three = get_last_three_months()
        valid_last_months = [m for m in last_three if m in all_months]
        default_months = valid_last_months if valid_last_months else ([all_months[-1]] if all_months else [])

    if not default_regions:
        default_regions = all_regions

    # 标签页1: 总览与历史
    with tabs[0]:
        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions, default_months, default_regions)
        if not selected_months or not selected_regions:
            return

        # 更新session状态
        st.session_state['filter_months'] = selected_months
        st.session_state['filter_regions'] = selected_regions

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 总览仪表盘
        st.markdown('<div class="sub-header">🔑 关键绩效指标</div>', unsafe_allow_html=True)

        # 计算总览KPI
        total_actual_qty = filtered_actual['求和项:数量（箱）'].sum()
        total_forecast_qty = filtered_forecast['预计销售量'].sum()

        national_accuracy = processed_data['national_accuracy']['overall']['数量准确率'] * 100

        regional_accuracy = processed_data['regional_accuracy']['region_overall']
        selected_regions_accuracy = regional_accuracy['数量准确率'].mean() * 100 if not regional_accuracy.empty else 0

        # 指标卡行
        col1, col2, col3, col4 = st.columns(4)

        # 总销售量
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">实际销售量</p>
                <p class="card-value">{format_number(total_actual_qty)}箱</p>
                <p class="card-text">选定期间内</p>
            </div>
            """, unsafe_allow_html=True)

        # 总预测销售量
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">预测销售量</p>
                <p class="card-value">{format_number(total_forecast_qty)}箱</p>
                <p class="card-text">选定期间内</p>
            </div>
            """, unsafe_allow_html=True)

        # 全国准确率
        with col3:
            accuracy_color = "green" if national_accuracy >= 80 else "orange" if national_accuracy >= 60 else "red"
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">全国销售量准确率</p>
                <p class="card-value" style="color:{accuracy_color};">{national_accuracy:.2f}%</p>
                <p class="card-text">整体预测精度</p>
            </div>
            """, unsafe_allow_html=True)

        # 选定区域准确率
        with col4:
            region_accuracy_color = "green" if selected_regions_accuracy >= 80 else "orange" if selected_regions_accuracy >= 60 else "red"
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">选定区域准确率</p>
                <p class="card-value" style="color:{region_accuracy_color};">{selected_regions_accuracy:.2f}%</p>
                <p class="card-text">选定区域预测精度</p>
            </div>
            """, unsafe_allow_html=True)

        # 区域销售分析
        st.markdown('<div class="sub-header">📊 区域销售分析</div>', unsafe_allow_html=True)

        if not processed_data['merged_monthly'].empty:
            # 计算每个区域的销售量和预测量
            region_sales_comparison = processed_data['merged_monthly'].groupby('所属区域').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 计算差异
            region_sales_comparison['差异'] = region_sales_comparison['求和项:数量（箱）'] - region_sales_comparison['预计销售量']
            region_sales_comparison['差异率'] = (region_sales_comparison['差异'] / region_sales_comparison['求和项:数量（箱）'] * 100).fillna(0)

            # 创建水平堆叠柱状图
            fig = go.Figure()

            # 添加实际销售量柱
            fig.add_trace(go.Bar(
                y=region_sales_comparison['所属区域'],
                x=region_sales_comparison['求和项:数量（箱）'],
                name='实际销售量',
                marker_color='royalblue',
                orientation='h'
            ))

            # 添加预测销售量柱
            fig.add_trace(go.Bar(
                y=region_sales_comparison['所属区域'],
                x=region_sales_comparison['预计销售量'],
                name='预测销售量',
                marker_color='lightcoral',
                orientation='h'
            ))

            # 添加差异率点
            fig.add_trace(go.Scatter(
                y=region_sales_comparison['所属区域'],
                x=[region_sales_comparison['求和项:数量（箱）'].max() * 1.05] * len(region_sales_comparison),  # 放在右侧
                mode='markers+text',
                marker=dict(
                    color=region_sales_comparison['差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                    size=10
                ),
                text=[f"{x:.1f}%" for x in region_sales_comparison['差异率']],
                textposition='middle right',
                name='差异率 (%)'
            ))

            # 更新布局
            fig.update_layout(
                title="各区域预测与实际销售对比",
                barmode='group',
                xaxis=dict(
                    title="销售量 (箱)",
                    tickformat=",",
                    showexponent="none"
                ),
                yaxis=dict(title="区域"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white'
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加解读
            st.markdown("""
            <div class="chart-explanation">
                <b>图表解读：</b> 此图展示了各区域的实际销售量(蓝色)与预测销售量(红色)对比，右侧数字表示差异率。
                绿色点表示实际销量高于预测（低估），红色点表示实际销量低于预测（高估）。
                差异率越高(绝对值越大)，表明预测偏离实际的程度越大。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成区域销售分析图表。")

        # 历史趋势分析
        st.markdown('<div class="sub-header">📊 销售与预测历史趋势</div>', unsafe_allow_html=True)

        if not processed_data['merged_monthly'].empty:
            # 按月份汇总
            monthly_trend = processed_data['merged_monthly'].groupby('所属年月').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 计算差异率
            monthly_trend['差异率'] = ((monthly_trend['求和项:数量（箱）'] - monthly_trend['预计销售量']) / monthly_trend['求和项:数量（箱）'] * 100).fillna(0)

            # 创建销售与预测趋势图
            fig = go.Figure()

            # 添加实际销售线
            fig.add_trace(go.Scatter(
                x=monthly_trend['所属年月'],
                y=monthly_trend['求和项:数量（箱）'],
                mode='lines+markers',
                name='实际销售量',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8)
            ))

            # 添加预测销售线
            fig.add_trace(go.Scatter(
                x=monthly_trend['所属年月'],
                y=monthly_trend['预计销售量'],
                mode='lines+markers',
                name='预测销售量',
                line=dict(color='lightcoral', width=3, dash='dot'),
                marker=dict(size=8)
            ))

            # 添加差异率线
            fig.add_trace(go.Scatter(
                x=monthly_trend['所属年月'],
                y=monthly_trend['差异率'],
                mode='lines+markers+text',
                name='差异率 (%)',
                yaxis='y2',
                line=dict(color='green', width=2),
                marker=dict(size=8),
                text=[f"{x:.1f}%" for x in monthly_trend['差异率']],
                textposition='top center'
            ))

            # 更新布局
            fig.update_layout(
                title="销售与预测历史趋势分析",
                xaxis_title="月份",
                yaxis=dict(
                    title="销售量 (箱)",
                    tickformat=",",
                    showexponent="none"
                ),
                yaxis2=dict(
                    title="差异率 (%)",
                    overlaying='y',
                    side='right'
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white'
            )

            # 强调选定月份
            for month in selected_months:
                if month in monthly_trend['所属年月'].values:
                    fig.add_shape(
                        type="rect",
                        x0=month,
                        x1=month,
                        y0=0,
                        y1=monthly_trend['求和项:数量（箱）'].max() * 1.1,
                        fillcolor="rgba(144, 238, 144, 0.2)",
                        line=dict(width=0)
                    )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加解读
            st.markdown("""
            <div class="chart-explanation">
                <b>图表解读：</b> 此图展示了历史销售量(蓝线)与预测销售量(红线)趋势，以及月度差异率(绿线)。
                通过观察趋势可以发现销售的季节性波动、预测与实际的一致性以及差异率的变化趋势。
                分析峰值和谷值时期的预测差异，可以发现预测模型在特定时期的弱点。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来生成历史趋势分析图表。")

    # 标签页2: 预测差异分析
    with tabs[1]:
        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions, default_months, default_regions)
        if not selected_months or not selected_regions:
            return

        # 更新session状态
        st.session_state['filter_months'] = selected_months
        st.session_state['filter_regions'] = selected_regions

        # 选择分析维度
        analysis_dimension = st.selectbox(
            "选择分析维度",
            options=['产品', '销售员'],
            key="dimension_select"
        )

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        st.markdown('<div class="sub-header">🔍 预测差异详细分析</div>', unsafe_allow_html=True)

        if analysis_dimension == '产品':
            # 按产品分析差异
            if 'merged_monthly' in processed_data and not processed_data['merged_monthly'].empty:
                # 按产品汇总
                product_diff = processed_data['merged_monthly'].groupby('产品代码').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 计算差异和准确率
                product_diff['数量差异'] = product_diff['求和项:数量（箱）'] - product_diff['预计销售量']
                product_diff['数量差异率'] = (product_diff['数量差异'] / product_diff['求和项:数量（箱）'] * 100).fillna(0)
                product_diff['数量准确率'] = product_diff.apply(
                    lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
                    axis=1
                )
                product_diff['数量准确率_百分比'] = product_diff['数量准确率'] * 100

                # 添加产品名称
                product_diff['产品名称'] = product_diff['产品代码'].apply(
                    lambda x: format_product_code(x, product_info, include_name=True)
                )

                # 按差异率绝对值排序
                product_diff = product_diff.sort_values('数量差异率', key=abs, ascending=False)

                # 创建水平条形图
                fig = go.Figure()

                # 添加实际销售量柱
                fig.add_trace(go.Bar(
                    y=product_diff['产品名称'],
                    x=product_diff['求和项:数量（箱）'],
                    name='实际销售量',
                    marker_color='royalblue',
                    orientation='h'
                ))

                # 添加预测销售量柱
                fig.add_trace(go.Bar(
                    y=product_diff['产品名称'],
                    x=product_diff['预计销售量'],
                    name='预测销售量',
                    marker_color='lightcoral',
                    orientation='h'
                ))

                # 添加差异率点
                fig.add_trace(go.Scatter(
                    y=product_diff['产品名称'],
                    x=[product_diff['求和项:数量（箱）'].max() * 1.05] * len(product_diff),  # 放在右侧
                    mode='markers+text',
                    marker=dict(
                        color=product_diff['数量差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                        size=10
                    ),
                    text=[f"{x:.1f}%" for x in product_diff['数量差异率']],
                    textposition='middle right',
                    name='差异率 (%)'
                ))

                # 更新布局
                fig.update_layout(
                    title="产品预测与实际销售对比",
                    xaxis=dict(
                        title="销售量 (箱)",
                        tickformat=",",
                        showexponent="none"
                    ),
                    yaxis=dict(title="产品"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    barmode='group',
                    plot_bgcolor='white',
                    height=max(600, len(product_diff) * 25)  # 动态调整高度
                )

                # 显示图表
                st.plotly_chart(fig, use_container_width=True)

                # 添加解读
                st.markdown("""
                <div class="chart-explanation">
                    <b>图表解读：</b> 此图展示了产品维度的预测差异，蓝色代表实际销售量，红色代表预测销售量，点的颜色表示差异率(绿色为低估，红色为高估)。
                    差异率越高(绝对值越大)，表明预测偏离实际的程度越大。重点关注销量大且差异率高的产品，这些产品对整体准确率影响最大。
                </div>
                """, unsafe_allow_html=True)

                # 产品准确率散点图
                st.markdown('<div class="sub-header">📊 产品准确率与销量关系</div>', unsafe_allow_html=True)

                # 创建散点图
                fig = px.scatter(
                    product_diff,
                    x='求和项:数量（箱）',
                    y='数量准确率_百分比',
                    size='求和项:数量（箱）',
                    color='数量准确率_百分比',
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 100],
                    hover_name='产品名称',
                    labels={
                        '求和项:数量（箱）': '销量(箱)',
                        '数量准确率_百分比': '准确率(%)'
                    },
                    title="产品销量与准确率关系"
                )

                # 更新布局
                fig.update_layout(
                    xaxis=dict(
                        title="销量 (箱)",
                        type='log',  # 使用对数刻度更好地显示不同销量范围
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(220,220,220,0.8)'
                    ),
                    yaxis=dict(
                        title="准确率 (%)",
                        range=[0, 100],
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(220,220,220,0.8)'
                    ),
                    plot_bgcolor='white'
                )

                # 添加平均准确率线
                mean_accuracy = product_diff['数量准确率_百分比'].mean()
                fig.add_hline(
                    y=mean_accuracy,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"平均: {mean_accuracy:.2f}%",
                    annotation_position="top left"
                )

                # 显示图表
                st.plotly_chart(fig, use_container_width=True)

                # 识别问题产品
                low_accuracy_high_sales = product_diff[(product_diff['数量准确率_百分比'] < 60) &
                                                       (product_diff['求和项:数量（箱）'] > product_diff['求和项:数量（箱）'].median())]

                if not low_accuracy_high_sales.empty:
                    st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                    st.markdown('<div class="insight-title">需要优先改进的产品</div>', unsafe_allow_html=True)

                    st.markdown("以下产品销量高但准确率低，建议优先改进预测方法：", unsafe_allow_html=True)

                    for _, row in low_accuracy_high_sales.head(5).iterrows():
                        product_name = row['产品名称']
                        accuracy = row['数量准确率_百分比']
                        sales = row['求和项:数量（箱）']
                        forecast = row['预计销售量']
                        diff = sales - forecast
                        diff_text = "高估" if diff < 0 else "低估"

                        st.markdown(f"""
                        • <b>{product_name}</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                          销量 {format_number(sales)}箱，预测 {format_number(forecast)}箱，
                          <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                        """, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("没有足够的数据来生成产品差异分析。")
        else:  # 销售员维度
            # 按销售员分析差异
            if 'merged_by_salesperson' in processed_data and not processed_data['merged_by_salesperson'].empty:
                # 按销售员汇总
                salesperson_diff = processed_data['merged_by_salesperson'].groupby(['销售员', '所属区域']).agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 计算差异和准确率
                salesperson_diff['数量差异'] = salesperson_diff['求和项:数量（箱）'] - salesperson_diff['预计销售量']
                salesperson_diff['数量差异率'] = (salesperson_diff['数量差异'] / salesperson_diff['求和项:数量（箱）'] * 100).fillna(0)
                salesperson_diff['数量准确率'] = salesperson_diff.apply(
                    lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
                    axis=1
                )
                salesperson_diff['数量准确率_百分比'] = salesperson_diff['数量准确率'] * 100

                # 按差异率绝对值排序
                salesperson_diff = salesperson_diff.sort_values('数量差异率', key=abs, ascending=False)

                # 创建水平条形图
                fig = go.Figure()

                # 添加实际销售量柱
                fig.add_trace(go.Bar(
                    y=salesperson_diff['销售员'],
                    x=salesperson_diff['求和项:数量（箱）'],
                    name='实际销售量',
                    marker_color='royalblue',
                    orientation='h'
                ))

                # 添加预测销售量柱
                fig.add_trace(go.Bar(
                    y=salesperson_diff['销售员'],
                    x=salesperson_diff['预计销售量'],
                    name='预测销售量',
                    marker_color='lightcoral',
                    orientation='h'
                ))

                # 添加差异率点
                fig.add_trace(go.Scatter(
                    y=salesperson_diff['销售员'],
                    x=[salesperson_diff['求和项:数量（箱）'].max() * 1.05] * len(salesperson_diff),  # 放在右侧
                    mode='markers+text',
                    marker=dict(
                        color=salesperson_diff['数量差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                        size=10
                    ),
                    text=[f"{x:.1f}%" for x in salesperson_diff['数量差异率']],
                    textposition='middle right',
                    name='差异率 (%)'
                ))

                # 更新布局
                fig.update_layout(
                    title="销售员预测与实际销售对比",
                    xaxis=dict(
                        title="销售量 (箱)",
                        tickformat=",",
                        showexponent="none"
                    ),
                    yaxis=dict(title="销售员"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    barmode='group',
                    plot_bgcolor='white',
                    height=max(600, len(salesperson_diff) * 25)  # 动态调整高度
                )

                # 显示图表
                st.plotly_chart(fig, use_container_width=True)

                # 添加解读
                st.markdown("""
                <div class="chart-explanation">
                    <b>图表解读：</b> 此图展示了销售员维度的预测差异，蓝色代表实际销售量，红色代表预测销售量，点的颜色表示差异率(绿色为低估，红色为高估)。
                    差异率越高(绝对值越大)，表明销售员的预测偏离实际的程度越大。重点关注销量大且差异率高的销售员，这些销售员对整体准确率影响最大。
                </div>
                """, unsafe_allow_html=True)

                # 销售员准确率散点图
                st.markdown('<div class="sub-header">📊 销售员准确率与区域分布</div>', unsafe_allow_html=True)

                # 创建散点图
                fig = px.scatter(
                    salesperson_diff,
                    x='求和项:数量（箱）',
                    y='数量准确率_百分比',
                    size='求和项:数量（箱）',
                    color='所属区域',
                    hover_name='销售员',
                    labels={
                        '求和项:数量（箱）': '销量(箱)',
                        '数量准确率_百分比': '准确率(%)',
                        '所属区域': '区域'
                    },
                    title="销售员销量与准确率关系"
                )

                # 更新布局
                fig.update_layout(
                    xaxis=dict(
                        title="销量 (箱)",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(220,220,220,0.8)',
                        tickformat=",",
                        showexponent="none"
                    ),
                    yaxis=dict(
                        title="准确率 (%)",
                        range=[0, 100],
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(220,220,220,0.8)'
                    ),
                    plot_bgcolor='white'
                )

                # 添加平均准确率线
                mean_accuracy = salesperson_diff['数量准确率_百分比'].mean()
                fig.add_hline(
                    y=mean_accuracy,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"平均: {mean_accuracy:.2f}%",
                    annotation_position="top left"
                )

                # 显示图表
                st.plotly_chart(fig, use_container_width=True)

                # 识别问题销售员
                low_accuracy_high_sales = salesperson_diff[(salesperson_diff['数量准确率_百分比'] < 60) &
                                                         (salesperson_diff['求和项:数量（箱）'] > salesperson_diff['求和项:数量（箱）'].median())]

                if not low_accuracy_high_sales.empty:
                    st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                    st.markdown('<div class="insight-title">需要优先改进的销售员</div>', unsafe_allow_html=True)

                    st.markdown("以下销售员销量高但准确率低，建议优先改进预测方法：", unsafe_allow_html=True)

                    for _, row in low_accuracy_high_sales.head(5).iterrows():
                        salesperson = row['销售员']
                        region = row['所属区域']
                        accuracy = row['数量准确率_百分比']
                        sales = row['求和项:数量（箱）']
                        forecast = row['预计销售量']
                        diff = sales - forecast
                        diff_text = "高估" if diff < 0 else "低估"

                        st.markdown(f"""
                        • <b>{salesperson}（{region}区域）</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                          销量 {format_number(sales)}箱，预测 {format_number(forecast)}箱，
                          <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                        """, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("没有足够的数据来生成销售员差异分析。")

    # 标签页3: 产品趋势
    with tabs[2]:
        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions, default_months, default_regions)
        if not selected_months or not selected_regions:
            return

        # 更新session状态
        st.session_state['filter_months'] = selected_months
        st.session_state['filter_regions'] = selected_regions

        # 计算产品增长率
        product_growth = calculate_product_growth(actual_monthly=actual_data, regions=selected_regions, months=selected_months)

        if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
            # 简要统计
            latest_growth = product_growth['latest_growth']
            growth_stats = {
                '强劲增长': len(latest_growth[latest_growth['趋势'] == '强劲增长']),
                '增长': len(latest_growth[latest_growth['趋势'] == '增长']),
                '轻微下降': len(latest_growth[latest_growth['趋势'] == '轻微下降']),
                '显著下降': len(latest_growth[latest_growth['趋势'] == '显著下降'])
            }

            # 统计指标卡
            st.markdown('<div class="sub-header">📊 产品增长趋势统计</div>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 0.5rem solid #2E8B57;">
                    <p class="card-header">强劲增长产品</p>
                    <p class="card-value">{growth_stats['强劲增长']}</p>
                    <p class="card-text">增长率 > 10%</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 0.5rem solid #4CAF50;">
                    <p class="card-header">增长产品</p>
                    <p class="card-value">{growth_stats['增长']}</p>
                    <p class="card-text">增长率 0% ~ 10%</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 0.5rem solid #FFA500;">
                    <p class="card-header">轻微下降产品</p>
                    <p class="card-value">{growth_stats['轻微下降']}</p>
                    <p class="card-text">增长率 -10% ~ 0%</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 0.5rem solid #F44336;">
                    <p class="card-header">显著下降产品</p>
                    <p class="card-value">{growth_stats['显著下降']}</p>
                    <p class="card-text">增长率 < -10%</p>
                </div>
                """, unsafe_allow_html=True)

            # 产品增长率图表
            st.markdown('<div class="sub-header">📈 产品增长率与备货建议</div>', unsafe_allow_html=True)

            # 准备数据
            growth_data = latest_growth.copy()

            # 添加产品名称
            growth_data['产品名称'] = growth_data['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 创建增长率图
            fig = px.bar(
                growth_data,
                y='产品名称',
                x='销量增长率',
                color='趋势',
                orientation='h',
                color_discrete_map={
                    '强劲增长': '#1E88E5',  # 深蓝色
                    '增长': '#43A047',  # 绿色
                    '轻微下降': '#FB8C00',  # 橙色
                    '显著下降': '#E53935'  # 红色
                },
                hover_data={
                    '当月销量': ':,.0f',
                    '备货建议': True,
                    '调整比例': True
                },
                labels={
                    '产品名称': '产品',
                    '销量增长率': '增长率(%)',
                    '当月销量': '当月销量(箱)',
                    '备货建议': '备货建议',
                    '调整比例': '调整比例(%)'
                },
                title="产品销量增长率与备货建议"
            )

            # 添加零线
            fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=1)

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="增长率 (%)",
                    zeroline=False
                ),
                yaxis=dict(
                    title="产品",
                    autorange="reversed"  # 将最高增长率的产品放在顶部
                ),
                height=max(500, len(growth_data) * 30),  # 动态调整高度
                margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                plot_bgcolor='white'
            )

            # 添加标注 - 在条形旁边显示增长率
            for i, row in enumerate(growth_data.itertuples()):
                fig.add_annotation(
                    x=row.销量增长率,
                    y=row.产品名称,
                    text=f"{row.销量增长率:.1f}% {row.建议图标 if hasattr(row, '建议图标') and pd.notna(row.建议图标) else ''}",
                    showarrow=False,
                    xshift=10 if row.销量增长率 >= 0 else -10,
                    align="left" if row.销量增长率 >= 0 else "right",
                    font=dict(
                        color="#43A047" if row.销量增长率 >= 0 else "#E53935",
                        size=10
                    )
                )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 条形图展示了产品的销量增长率和对应的备货建议。颜色区分了不同的增长趋势：
                蓝色表示强劲增长(>10%)，绿色表示增长(0-10%)，橙色表示轻微下降(-10-0%)，红色表示显著下降(<-10%)。
                悬停可查看详细的备货建议和调整比例。
            </div>
            """, unsafe_allow_html=True)

            # 销量-增长率-准确率三维分析
            st.markdown('<div class="sub-header">🔍 产品销量-增长率-准确率分析</div>', unsafe_allow_html=True)

            # 合并销量增长率和准确率数据
            if 'merged_monthly' in processed_data and not processed_data['merged_monthly'].empty:
                # 按产品汇总准确率数据
                product_accuracy = processed_data['merged_monthly'].groupby('产品代码').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 计算准确率
                product_accuracy['数量准确率'] = product_accuracy.apply(
                    lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
                    axis=1
                )
                product_accuracy['数量准确率_百分比'] = product_accuracy['数量准确率'] * 100

                # 合并数据
                merged_analysis = pd.merge(
                    growth_data,
                    product_accuracy[['产品代码', '数量准确率_百分比', '求和项:数量（箱）']],
                    on='产品代码',
                    how='inner'
                )

                # 创建四象限散点图
                if not merged_analysis.empty:
                    fig = go.Figure()

                    # 添加散点
                    fig.add_trace(go.Scatter(
                        x=merged_analysis['求和项:数量（箱）'],
                        y=merged_analysis['销量增长率'],
                        mode='markers',
                        marker=dict(
                            size=merged_analysis['数量准确率_百分比'] / 2 + 10,  # 调整大小
                            color=merged_analysis['数量准确率_百分比'],
                            colorscale='RdYlGn',
                            colorbar=dict(title='准确率 (%)'),
                            cmin=0,
                            cmax=100,
                            line=dict(width=1, color='white')
                        ),
                        text=merged_analysis['产品名称'],
                        hovertemplate='<b>%{text}</b><br>销量: %{x:,.0f}箱<br>增长率: %{y:.2f}%<br>准确率: %{marker.color:.2f}%<extra></extra>'
                    ))

                    # 添加四象限分割线
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    fig.add_vline(x=merged_analysis['求和项:数量（箱）'].median(), line_dash="dash", line_color="gray", line_width=1)

                    # 添加象限标签
                    median_x = merged_analysis['求和项:数量（箱）'].median()
                    max_x = merged_analysis['求和项:数量（箱）'].max()
                    max_y = merged_analysis['销量增长率'].max()
                    min_y = merged_analysis['销量增长率'].min()

                    fig.add_annotation(
                        x=median_x * 1.5,
                        y=max_y * 0.8,
                        text="高销量 + 高增长<br>(重点关注)",
                        showarrow=False,
                        font=dict(size=10, color="green")
                    )

                    fig.add_annotation(
                        x=median_x * 0.5,
                        y=max_y * 0.8,
                        text="低销量 + 高增长<br>(潜力产品)",
                        showarrow=False,
                        font=dict(size=10, color="blue")
                    )

                    fig.add_annotation(
                        x=median_x * 1.5,
                        y=min_y * 0.8,
                        text="高销量 + 负增长<br>(需警惕)",
                        showarrow=False,
                        font=dict(size=10, color="red")
                    )

                    fig.add_annotation(
                        x=median_x * 0.5,
                        y=min_y * 0.8,
                        text="低销量 + 负增长<br>(考虑调整)",
                        showarrow=False,
                        font=dict(size=10, color="orange")
                    )

                    # 更新布局
                    fig.update_layout(
                        title="产品销量-增长率-准确率分析",
                        xaxis=dict(
                            title="销量 (箱)",
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(220,220,220,0.8)',
                            tickformat=",",
                            showexponent="none"
                        ),
                        yaxis=dict(
                            title="销量增长率 (%)",
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(220,220,220,0.8)'
                        ),
                        plot_bgcolor='white',
                        margin=dict(l=20, r=20, t=50, b=50)
                    )

                    # 显示图表
                    st.plotly_chart(fig, use_container_width=True)

                    # 添加图表说明
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>图表说明:</b> 此图展示了产品的销量、增长率和准确率三个维度，气泡大小和颜色表示预测准确率（越大越绿表示准确率越高）。
                        四个象限代表不同的产品状态：右上角为核心产品（高销量高增长），左上角为潜力产品（低销量高增长），
                        右下角为需关注产品（高销量负增长），左下角为待调整产品（低销量负增长）。
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("没有足够的匹配数据来生成产品销量-增长率-准确率分析图。")
            else:
                st.warning("没有足够的准确率数据来生成产品销量-增长率-准确率分析图。")
        else:
            st.warning("没有足够的数据来计算产品增长率。")

    # 标签页4: 重点SKU分析
    with tabs[3]:
        # 渲染筛选器
        selected_months, selected_regions = render_filters(all_months, all_regions, default_months, default_regions)
        if not selected_months or not selected_regions:
            return

        # 更新session状态
        st.session_state['filter_months'] = selected_months
        st.session_state['filter_regions'] = selected_regions

        # 筛选数据
        filtered_actual = filter_data(actual_data, selected_months, selected_regions)
        filtered_forecast = filter_data(forecast_data, selected_months, selected_regions)

        # 处理数据
        processed_data = process_data(filtered_actual, filtered_forecast, product_info)

        # 重点SKU分析
        st.markdown('<div class="sub-header">💎 销售量占比80%重点SKU分析</div>', unsafe_allow_html=True)

        if 'national_top_skus' in processed_data and not processed_data['national_top_skus'].empty:
            # 格式化准确率为百分比
            national_top_skus = processed_data['national_top_skus'].copy()
            national_top_skus['数量准确率_百分比'] = national_top_skus['数量准确率'] * 100

            # 添加产品名称
            national_top_skus['产品名称'] = national_top_skus['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 创建条形图
            fig = px.bar(
                national_top_skus,
                y='产品名称',
                x='求和项:数量（箱）',
                color='数量准确率_百分比',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                text=national_top_skus['数量准确率_百分比'].apply(lambda x: f"{x:.2f}%"),
                hover_data={
                    '数量准确率_百分比': ':.2f',
                    '预计销售量': ':,.0f',
                    '累计占比': ':.2f'
                },
                labels={
                    '产品名称': '产品',
                    '求和项:数量（箱）': '销量(箱)',
                    '数量准确率_百分比': '准确率(%)',
                    '预计销售量': '预测销量(箱)',
                    '累计占比': '累计占比(%)'
                },
                title=f"重点SKU及其准确率"
            )

            # 更新布局
            fig.update_layout(
                xaxis=dict(
                    title="销售量 (箱)",
                    tickformat=",",
                    showexponent="none"
                ),
                yaxis=dict(title="产品"),
                coloraxis=dict(
                    colorbar=dict(
                        title="准确率 (%)",
                        tickformat=".2f"
                    )
                ),
                plot_bgcolor='white',
                height=max(700, len(national_top_skus) * 40),  # 增加高度
                margin=dict(l=20, r=40, t=60, b=30)  # 增加边距
            )

            # 突出显示准确率低的产品
            low_accuracy_products = national_top_skus[national_top_skus['数量准确率_百分比'] < 70]
            if not low_accuracy_products.empty:
                for product in low_accuracy_products['产品名称']:
                    idx = list(national_top_skus['产品名称']).index(product)
                    fig.add_shape(
                        type="rect",
                        y0=idx - 0.45,
                        y1=idx + 0.45,
                        x0=0,
                        x1=national_top_skus['求和项:数量（箱）'].max() * 1.05,
                        line=dict(color="#F44336", width=2),
                        fillcolor="rgba(244, 67, 54, 0.1)"
                    )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表说明
            st.markdown("""
            <div class="chart-explanation">
                <b>图表说明:</b> 此图展示了销售量累计占比达到80%的重点SKU及其准确率，条形长度表示销量，颜色表示准确率(绿色为高准确率，红色为低准确率)。
                红框标记的产品准确率低于70%，需要特别关注。这些产品对整体预测准确率有最大影响，应重点关注准确率较低的重点产品。
            </div>
            """, unsafe_allow_html=True)

            # 识别问题产品
            low_accuracy_high_share = national_top_skus[(national_top_skus['数量准确率_百分比'] < 70) & (national_top_skus['累计占比'] < 50)]

            if not low_accuracy_high_share.empty:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown('<div class="insight-title">需要改进的重点SKU</div>', unsafe_allow_html=True)

                for _, row in low_accuracy_high_share.iterrows():
                    product_name = row['产品名称']
                    accuracy = row['数量准确率_百分比']
                    sales = row['求和项:数量（箱）']
                    forecast = row['预计销售量']
                    diff = sales - forecast
                    diff_text = "高估" if diff < 0 else "低估"
                    share = row['累计占比']

                    st.markdown(f"""
                    • <b>{product_name}</b>: 准确率仅 <span style="color:red">{accuracy:.2f}%</span>，
                      销量 {format_number(sales)}箱 (占比{share:.2f}%)，预测 {format_number(forecast)}箱，
                      <b>{diff_text} {format_number(abs(diff))}箱 ({abs(diff/sales*100 if sales > 0 else 0):.2f}%)</b>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            # 区域重点SKU比较
            st.markdown('<div class="sub-header">🌐 各区域重点SKU对比</div>', unsafe_allow_html=True)

            if 'regional_top_skus' in processed_data and processed_data['regional_top_skus']:
                # 创建区域选项卡
                region_tabs = st.tabs(sorted(list(processed_data['regional_top_skus'].keys())))

                for i, region in enumerate(sorted(list(processed_data['regional_top_skus'].keys()))):
                    with region_tabs[i]:
                        region_top = processed_data['regional_top_skus'][region].copy()

                        if not region_top.empty:
                            # 格式化准确率为百分比
                            region_top['数量准确率_百分比'] = region_top['数量准确率'] * 100

                            # 添加产品名称
                            region_top['产品名称'] = region_top['产品代码'].apply(
                                lambda x: format_product_code(x, product_info, include_name=True)
                            )

                            # 创建条形图
                            fig = px.bar(
                                region_top,
                                y='产品名称',
                                x='求和项:数量（箱）',
                                color='数量准确率_百分比',
                                color_continuous_scale='RdYlGn',
                                range_color=[0, 100],
                                text=region_top['数量准确率_百分比'].apply(lambda x: f"{x:.2f}%"),
                                hover_data={
                                    '数量准确率_百分比': ':.2f',
                                    '预计销售量': ':,.0f',
                                    '累计占比': ':.2f'
                                },
                                labels={
                                    '产品名称': '产品',
                                    '求和项:数量（箱）': '销量(箱)',
                                    '数量准确率_百分比': '准确率(%)',
                                    '预计销售量': '预测销量(箱)',
                                    '累计占比': '累计占比(%)'
                                },
                                title=f"{region}区域重点SKU及其准确率"
                            )

                            # 更新布局
                            fig.update_layout(
                                xaxis=dict(
                                    title="销售量 (箱)",
                                    tickformat=",",
                                    showexponent="none"
                                ),
                                yaxis=dict(title="产品"),
                                coloraxis=dict(
                                    colorbar=dict(
                                        title="准确率 (%)",
                                        tickformat=".2f"
                                    )
                                ),
                                plot_bgcolor='white',
                                height=max(400, len(region_top) * 40)  # 增加高度
                            )

                            # 显示图表
                            st.plotly_chart(fig, use_container_width=True)

                            # 区域与全国重点SKU对比
                            try:
                                # 获取区域和全国的SKU列表
                                region_skus = set(region_top['产品代码'])
                                national_skus = set(national_top_skus['产品代码'])

                                # 计算共有和特有SKU
                                common_skus = region_skus.intersection(national_skus)
                                region_unique_skus = region_skus - national_skus
                                national_unique_skus = national_skus - region_skus

                                # 创建饼图
                                fig = go.Figure()

                                # 添加区域特有SKU占比
                                fig.add_trace(go.Pie(
                                    labels=['区域与全国共有SKU', '区域特有SKU', '全国重点但区域非重点SKU'],
                                    values=[len(common_skus), len(region_unique_skus), len(national_unique_skus)],
                                    hole=.3,
                                    marker_colors=['#4CAF50', '#2196F3', '#F44336']
                                ))

                                fig.update_layout(
                                    title=f"{region}区域与全国重点SKU对比",
                                    plot_bgcolor='white'
                                )

                                # 显示图表
                                st.plotly_chart(fig, use_container_width=True)

                                # 添加图表说明
                                st.markdown(f"""
                                <div class="chart-explanation">
                                    <b>图表说明:</b> 此饼图展示了{region}区域重点SKU与全国重点SKU的对比情况。
                                    绿色部分表示同时是区域和全国重点的产品；
                                    蓝色部分表示只在该区域是重点的产品；
                                    红色部分表示在全国范围内是重点但在该区域不是重点的产品。
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"生成区域比较图时出错: {str(e)}")
                        else:
                            st.warning(f"没有足够的数据来生成{region}区域的重点SKU分析。")
            else:
                st.warning("没有足够的数据来生成区域重点SKU比较。")
        else:
            st.warning("没有足够的数据来生成重点SKU分析。")

# 主函数
def main():
    """主程序"""
    render_dashboard()

if __name__ == "__main__":
    main()