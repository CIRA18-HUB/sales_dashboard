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
from urllib.parse import urlencode
import random

# 设置随机种子以确保示例数据一致性
np.random.seed(42)
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售预测准确率分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局颜色变量 */
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --success-color: #4CAF50;
        --warning-color: #FFA500;
        --danger-color: #F44336;
        --info-color: #2196F3;
        --light-color: #f8f9fa;
        --dark-color: #343a40;
        --border-color: #dee2e6;
        --text-color: #212529;
        --title-color: #343a40;
    }

    /* 主标题 */
    .main-header {
        font-size: 1.8rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }

    /* 子标题 */
    .sub-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eaeaea;
    }

    /* 指标卡片 */
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 20px;
    }

    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        flex: 1;
        min-width: 200px;
        position: relative;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }

    .card-header {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--dark-color);
        margin-bottom: 10px;
    }

    .card-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 8px;
    }

    .card-change {
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }

    .card-change.positive {
        color: var(--success-color);
    }

    .card-change.negative {
        color: var(--danger-color);
    }

    .card-text {
        font-size: 0.8rem;
        color: #6c757d;
    }

    .metric-icon {
        position: absolute;
        top: 15px;
        right: 15px;
        width: 36px;
        height: 36px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 颜色标记 */
    .border-primary {
        border-left: 4px solid var(--primary-color);
    }

    .border-success {
        border-left: 4px solid var(--success-color);
    }

    .border-warning {
        border-left: 4px solid var(--warning-color);
    }

    .border-danger {
        border-left: 4px solid var(--danger-color);
    }

    .border-info {
        border-left: 4px solid var(--info-color);
    }

    /* 筛选器面板 */
    .filter-container {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    .filter-title {
        font-size: 1rem;
        font-weight: 500;
        color: var(--primary-color);
        margin-bottom: 12px;
    }

    .filter-group {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 12px;
    }

    /* 图表卡片 */
    .chart-card {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    .chart-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--primary-color);
        margin-bottom: 12px;
    }

    /* 图表说明 */
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.08);
        padding: 12px;
        border-radius: 6px;
        margin: 12px 0;
        border-left: 4px solid var(--success-color);
        font-size: 0.9rem;
    }

    /* 标记和标签 */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 8px;
    }

    .badge-success {
        background-color: rgba(76, 175, 80, 0.15);
        color: var(--success-color);
    }

    .badge-warning {
        background-color: rgba(255, 165, 0, 0.15);
        color: var(--warning-color);
    }

    .badge-danger {
        background-color: rgba(244, 67, 54, 0.15);
        color: var(--danger-color);
    }

    /* 下钻导航 */
    .breadcrumb {
        display: flex;
        align-items: center;
        font-size: 0.9rem;
        margin-bottom: 16px;
    }

    .breadcrumb-item {
        color: var(--secondary-color);
        cursor: pointer;
    }

    .breadcrumb-item.active {
        color: var(--primary-color);
        font-weight: 500;
    }

    .breadcrumb-separator {
        margin: 0 8px;
        color: #6c757d;
    }

    /* 表格样式 */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9rem;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }

    .styled-table thead tr {
        background-color: var(--primary-color);
        color: white;
        text-align: left;
    }

    .styled-table th,
    .styled-table td {
        padding: 10px 15px;
    }

    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }

    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }

    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid var(--primary-color);
    }

    /* 美化滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* 交互提示 */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: rgba(0,0,0,0.8);
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

    /* 加载指示器 */
    .loader {
        border: 5px solid #f3f3f3;
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 2s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* 动画效果 */
    .fade-in {
        animation: fadeIn 0.5s;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* 响应式调整 */
    @media screen and (max-width: 768px) {
        .metric-card {
            min-width: 100%;
        }
    }

    /* 区域切换标签 */
    .region-tabs {
        display: flex;
        margin-bottom: 16px;
        overflow-x: auto;
        padding-bottom: 5px;
    }

    .region-tab {
        padding: 8px 16px;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        white-space: nowrap;
    }

    .region-tab.active {
        border-bottom: 2px solid var(--primary-color);
        color: var(--primary-color);
        font-weight: 500;
    }

    /* 悬停卡片 */
    .hover-card {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .hover-card:hover {
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }

    /* 提示框 */
    .alert {
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }

    .alert-info {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid var(--info-color);
        color: #0c5460;
    }

    .alert-warning {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 4px solid var(--warning-color);
        color: #856404;
    }

    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--success-color);
        color: #155724;
    }

    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid var(--danger-color);
        color: #721c24;
    }

    /* 低准确率标记 */
    .low-accuracy {
        border: 2px solid var(--danger-color);
        box-shadow: 0 0 8px var(--danger-color);
    }

    /* 分页器 */
    .pagination {
        display: flex;
        justify-content: center;
        margin: 16px 0;
    }

    .pagination-btn {
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        margin: 0 4px;
        cursor: pointer;
    }

    .pagination-btn:hover {
        background-color: var(--secondary-color);
    }

    .pagination-btn:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .pagination-info {
        display: inline-block;
        padding: 6px 12px;
        margin: 0 4px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'overview'  # 默认视图为总览

if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = '全部'  # 默认选择全部区域

if 'selected_drill_down' not in st.session_state:
    st.session_state['selected_drill_down'] = None  # 默认没有下钻对象

if 'breadcrumb' not in st.session_state:
    st.session_state['breadcrumb'] = [('总览', 'overview')]  # 导航路径

if 'filter_months' not in st.session_state:
    # 获取最近3个月作为默认值
    today = datetime.now()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    two_months_ago = (last_month - timedelta(days=1)).replace(day=1)
    st.session_state['filter_months'] = [
        two_months_ago.strftime('%Y-%m'),
        last_month.strftime('%Y-%m'),
        current_month.strftime('%Y-%m')
    ]

if 'filter_regions' not in st.session_state:
    st.session_state['filter_regions'] = ['北', '南', '东', '西']  # 默认选择所有区域


# 登录界面
def show_login_screen():
    st.markdown(
        '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">销售预测准确率分析仪表盘 | 登录</div>',
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
                st.rerun()
            else:
                st.error("密码错误，请重试！")


# 数据加载和处理函数
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
        'F0110A', 'F0110B', 'F0115C', 'F0101P', 'F01K8A', 'F0183K',
        'F01C2T', 'F3421C', 'F3415C', 'F01L3N', 'F01L4H'
    ]

    # 产品名称列表
    product_names = [
        '口力比萨68克袋装-中国', '口力汉堡大袋120g-中国', '口力西瓜45G+送9G袋装-中国',
        '口力海洋动物100g-中国', '口力幻彩蜥蜴105g-中国', '口力午餐袋77g-中国',
        '口力汉堡中袋108g-中国', '口力酸恐龙108G直立袋装-中国', '口力薯条90G直立袋装-中国',
        '口力比萨XXL45G盒装-中国', '口力比萨中包80g-中国', '口力比萨大包100g-中国',
        '口力薯条65g-中国', '口力鸡块75g-中国', '口力汉堡圈85g-中国',
        '口力汉堡90G直立袋装-中国', '口力烘焙袋77G袋装-中国', '口力酸恐龙60G袋装-中国',
        '口力电竞软糖55G袋装-中国', '口力可乐瓶60G袋装-中国', '口力酸小虫60G袋装-中国',
        '口力彩蝶虫48G+送9.6G袋装-中国', '口力扭扭虫48G+送9.6G袋装-中国'
    ]

    # 产品规格
    product_specs = [
        '68g*24', '120g*24', '54g*24', '100g*24', '105g*24', '77g*24',
        '108g*24', '108g*24', '90g*24', '45g*24', '80g*24', '100g*24',
        '65g*24', '75g*24', '85g*24', '90g*24', '77g*24', '60g*24',
        '55g*24', '60g*24', '60g*24', '57.6g*24', '57.6g*24'
    ]

    # 创建DataFrame
    data = {'产品代码': product_codes,
            '产品名称': product_names,
            '产品规格': product_specs}

    df = pd.DataFrame(data)

    # 添加简化产品名称列
    df['简化产品名称'] = df.apply(lambda row: simplify_product_name(row['产品代码'], row['产品名称']), axis=1)

    return df


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


def load_sample_actual_data():
    """创建示例实际销售数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P', 'F01K8A', 'F0183K',
        'F01C2T', 'F3421C', 'F3415C', 'F01L3N', 'F01L4H'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 申请人列表 (销售员)
    applicants = ['孙杨', '李根', '张伟', '王芳', '刘涛', '陈明', '林静', '黄强', '赵敏', '钱进']

    # 生成日期范围 - 确保包含2023年数据用于同比计算
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 5, 1)  # 确保有最新月份数据
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # 创建数据
    data = []
    for date in date_range:
        # 为每天生成随机数量的记录
        num_records = np.random.randint(5, 15)

        # 根据月份和季节性适当调整销量
        month = date.month
        is_holiday = month in [1, 5, 10, 12]  # 假设这些月份是高销售季节

        # 年度趋势 - 2024和2025年逐年增加
        year_factor = 1.0
        if date.year == 2024:
            year_factor = 1.15
        elif date.year == 2025:
            year_factor = 1.25

        for _ in range(num_records):
            region = np.random.choice(regions)
            applicant = np.random.choice(applicants)

            # 给每个销售员分配主要负责的区域，使数据更合理
            if applicant in ['孙杨', '李根', '张伟']:
                region = np.random.choice(['北', '东'], p=[0.7, 0.3])
            elif applicant in ['王芳', '刘涛']:
                region = np.random.choice(['南', '西'], p=[0.7, 0.3])
            else:
                region = np.random.choice(regions)

            # 随机选择产品，但有一些规律
            if is_holiday:
                # 假日季节，特定产品更受欢迎
                product_code = np.random.choice(
                    product_codes,
                    p=[0.15, 0.12, 0.1, 0.07, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02,
                       0.01, 0.01, 0.01, 0.01, 0.01, 0.005, 0.005]
                )
            else:
                # 非假日季节，销售更加平均
                product_code = np.random.choice(product_codes)

            # 根据区域、月份和产品调整销量
            base_quantity = np.random.randint(20, 150)

            # 区域因素
            if region == '北':
                region_factor = 1.2
            elif region == '南':
                region_factor = 1.1
            elif region == '东':
                region_factor = 1.3
            else:  # 西区
                region_factor = 0.9

            # 季节因素 - 添加季节性波动
            season_factor = 1.0
            if month in [12, 1, 2]:  # 冬季
                season_factor = 0.9
            elif month in [3, 4, 5]:  # 春季
                season_factor = 1.1
            elif month in [6, 7, 8]:  # 夏季
                season_factor = 1.2
            else:  # 秋季
                season_factor = 1.0

            # 添加一些随机波动
            random_factor = np.random.uniform(0.85, 1.15)

            # 最终销量
            quantity = int(base_quantity * region_factor * season_factor * year_factor * random_factor)

            # 为了模拟真实情况，偶尔添加一些异常大订单
            if np.random.random() < 0.02:  # 2% 的概率
                quantity *= np.random.randint(2, 5)

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
    """创建示例预测数据，增加合理性和季节性波动"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P', 'F01K8A', 'F0183K',
        'F01C2T', 'F3421C', 'F3415C', 'F01L3N', 'F01L4H'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 销售员列表
    sales_people = ['孙杨', '李根', '张伟', '王芳', '刘涛', '陈明', '林静', '黄强', '赵敏', '钱进']

    # 生成月份范围
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 5, 1)
    month_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    # 创建数据
    data = []
    for month in month_range:
        month_str = month.strftime('%Y-%m')
        current_month = month.month
        current_year = month.year

        # 季节性因素
        if current_month in [12, 1, 2]:  # 冬季
            season_factor = 0.9
        elif current_month in [3, 4, 5]:  # 春季
            season_factor = 1.1
        elif current_month in [6, 7, 8]:  # 夏季
            season_factor = 1.2
        else:  # 秋季
            season_factor = 1.0

        # 年度增长因素
        year_factor = 1.0
        if current_year == 2024:
            year_factor = 1.1
        elif current_year == 2025:
            year_factor = 1.2

        for region in regions:
            # 区域因素
            if region == '北':
                region_factor = 1.2
            elif region == '南':
                region_factor = 1.1
            elif region == '东':
                region_factor = 1.3
            else:  # 西区
                region_factor = 0.9

            # 计算区域内销售员平均准确率 - 模拟不同销售员预测能力
            sales_accuracy = {
                '孙杨': 0.85,  # 高准确率
                '李根': 0.92,
                '张伟': 0.88,
                '王芳': 0.75,  # 中等准确率
                '刘涛': 0.79,
                '陈明': 0.82,
                '林静': 0.65,  # 低准确率
                '黄强': 0.60,
                '赵敏': 0.70,
                '钱进': 0.78
            }

            for sales_person in sales_people:
                # 销售员准确率因素
                accuracy = sales_accuracy.get(sales_person, 0.75)

                # 给销售员分配特定区域，使数据更合理
                if sales_person in ['孙杨', '李根', '张伟']:
                    if region not in ['北', '东'] and np.random.random() > 0.3:
                        continue  # 70%概率跳过非主要区域
                elif sales_person in ['王芳', '刘涛']:
                    if region not in ['南', '西'] and np.random.random() > 0.3:
                        continue  # 70%概率跳过非主要区域

                for product_code in product_codes:
                    # 产品季节性 - 一些产品在特定季节更受欢迎
                    product_season_factor = 1.0

                    # 为不同产品设定不同的季节性
                    if product_code in ['F0104L', 'F01E4P', 'F01E6C']:
                        if current_month in [6, 7, 8]:  # 夏季热销
                            product_season_factor = 1.3
                    elif product_code in ['F3411A', 'F0110C', 'F0101P']:
                        if current_month in [12, 1, 2]:  # 冬季热销
                            product_season_factor = 1.25

                    # 有些产品可能没有预测
                    if np.random.random() > 0.1:  # 90%的概率有预测
                        # 计算基础预测销量
                        base_forecast = np.random.normal(120, 40)

                        # 应用各种因素计算最终预测
                        forecast_mean = base_forecast * region_factor * season_factor * year_factor * product_season_factor

                        # 加入预测误差 - 基于销售员准确率
                        error_range = (1 - accuracy) * 2  # 错误范围取决于准确率
                        error_factor = np.random.uniform(1 - error_range, 1 + error_range)

                        forecast = max(0, round(forecast_mean * error_factor))

                        data.append({
                            '所属大区': region,
                            '销售员': sales_person,
                            '所属年月': month_str,
                            '产品代码': product_code,
                            '预计销售量': forecast
                        })

    # 创建DataFrame
    df = pd.DataFrame(data)
    return df


def filter_data(data, months=None, regions=None, salesperson=None, product_code=None):
    """增强的数据筛选函数，支持更多筛选条件"""
    filtered_data = data.copy()

    if months and len(months) > 0:
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months)]

    if regions and len(regions) > 0 and '全部' not in regions:
        filtered_data = filtered_data[filtered_data['所属区域'].isin(regions)]

    if salesperson and salesperson != '全部':
        if '销售员' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['销售员'] == salesperson]
        elif '申请人' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['申请人'] == salesperson]

    if product_code and product_code != '全部':
        filtered_data = filtered_data[filtered_data['产品代码'] == product_code]

    return filtered_data


def get_common_months(actual_df, forecast_df):
    """获取两个数据集共有的月份"""
    actual_months = set(actual_df['所属年月'].unique())
    forecast_months = set(forecast_df['所属年月'].unique())
    common_months = sorted(list(actual_months.intersection(forecast_months)))
    return common_months


def get_recent_months(num_months=3):
    """获取最近几个月的年月字符串，如['2025-03', '2025-04', '2025-05']"""
    today = datetime.now()
    current_month = today.replace(day=1)

    months = []
    for i in range(num_months):
        # 向前推i个月
        month_date = current_month - timedelta(days=i * 30)  # 近似
        month_date = month_date.replace(day=1)  # 确保是月初
        months.append(month_date.strftime('%Y-%m'))

    # 返回倒序排列的月份（从过去到现在）
    return sorted(months)


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
        df['数量差异率'] = np.where(
            df['求和项:数量（箱）'] > 0,
            df['数量差异'] / df['求和项:数量（箱）'] * 100,
            np.where(
                df['预计销售量'] > 0,
                -100,  # 预测有值但实际为0
                0  # 预测和实际都是0
            )
        )

        # 准确率 - 使用统一的计算公式: 1 - |差异率|/100
        df['数量准确率'] = np.where(
            (df['求和项:数量（箱）'] > 0) | (df['预计销售量'] > 0),
            np.maximum(0, 1 - np.abs(df['数量差异率']) / 100),
            1  # 预测和实际都是0时准确率为100%
        )

    # 计算总体准确率
    national_accuracy = calculate_national_accuracy(merged_monthly)
    regional_accuracy = calculate_regional_accuracy(merged_monthly)
    salesperson_accuracy = calculate_salesperson_accuracy(merged_by_salesperson)

    # 计算占比80%的SKU
    national_top_skus = calculate_top_skus(merged_monthly, by_region=False)
    regional_top_skus = calculate_top_skus(merged_monthly, by_region=True)

    # 计算预测准确率随时间变化趋势
    accuracy_trends = calculate_accuracy_trends(merged_monthly)

    # 计算预测偏差典型特征
    bias_patterns = identify_bias_patterns(merged_monthly)

    # 计算产品增长率和趋势
    product_growth = calculate_product_growth(actual_monthly)

    return {
        'actual_monthly': actual_monthly,
        'forecast_monthly': forecast_monthly,
        'merged_monthly': merged_monthly,
        'merged_by_salesperson': merged_by_salesperson,
        'national_accuracy': national_accuracy,
        'regional_accuracy': regional_accuracy,
        'salesperson_accuracy': salesperson_accuracy,
        'national_top_skus': national_top_skus,
        'regional_top_skus': regional_top_skus,
        'accuracy_trends': accuracy_trends,
        'bias_patterns': bias_patterns,
        'product_growth': product_growth
    }


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
        import numpy as np
        return np.nanmean(series)
    except (OverflowError, ValueError, TypeError, ZeroDivisionError):
        # 处理任何计算错误
        return default


def calculate_unified_accuracy(actual, forecast):
    """统一计算准确率的函数，适用于全国和区域"""
    if actual == 0 and forecast == 0:
        return 1.0  # 如果实际和预测都为0，准确率为100%

    if actual == 0:
        return 0.0  # 如果实际为0但预测不为0，准确率为0%

    # 计算差异率
    diff_rate = (actual - forecast) / actual

    # 计算准确率 (基础公式: 1 - |差异率|)
    return max(0, 1 - abs(diff_rate))


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
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算整体差异
    region_overall['数量差异'] = region_overall['求和项:数量（箱）'] - region_overall['预计销售量']
    region_overall['差异率'] = region_overall.apply(
        lambda row: (row['数量差异'] / row['求和项:数量（箱）'] * 100) if row['求和项:数量（箱）'] > 0 else 0,
        axis=1
    )

    return {
        'region_monthly': region_monthly_summary,
        'region_overall': region_overall
    }


def calculate_salesperson_accuracy(merged_by_salesperson):
    """计算销售员预测准确率"""
    # 按销售员汇总
    salesperson_summary = merged_by_salesperson.groupby(['销售员', '所属区域']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异和准确率
    salesperson_summary['数量差异'] = salesperson_summary['求和项:数量（箱）'] - salesperson_summary['预计销售量']
    salesperson_summary['数量准确率'] = salesperson_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按销售员计算总体准确率
    sales_overall = salesperson_summary.groupby('销售员').agg({
        '数量准确率': lambda x: safe_mean(x, 0),
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 按区域计算销售员准确率
    sales_by_region = salesperson_summary.copy()

    return {
        'sales_summary': salesperson_summary,
        'sales_overall': sales_overall,
        'sales_by_region': sales_by_region
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


def calculate_accuracy_trends(merged_df):
    """计算准确率随时间的变化趋势"""
    # 按月份汇总
    monthly_trend = merged_df.groupby('所属年月').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算准确率
    monthly_trend['数量准确率'] = monthly_trend.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按区域和月份汇总
    region_monthly_trend = merged_df.groupby(['所属区域', '所属年月']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算区域准确率
    region_monthly_trend['数量准确率'] = region_monthly_trend.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按产品和月份汇总
    product_monthly_trend = merged_df.groupby(['产品代码', '所属年月']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算产品准确率
    product_monthly_trend['数量准确率'] = product_monthly_trend.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按销售员和月份汇总 (需要使用merged_by_salesperson)
    salesperson_monthly_trend = merged_df.groupby(['所属年月']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算销售员准确率
    salesperson_monthly_trend['数量准确率'] = salesperson_monthly_trend.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    return {
        'monthly': monthly_trend.sort_values('所属年月'),
        'region_monthly': region_monthly_trend,
        'product_monthly': product_monthly_trend,
        'salesperson_monthly': salesperson_monthly_trend
    }


def identify_bias_patterns(merged_df):
    """识别预测偏差的典型模式"""
    # 计算总体偏差
    overall_bias = (merged_df['求和项:数量（箱）'].sum() - merged_df['预计销售量'].sum()) / merged_df[
        '求和项:数量（箱）'].sum() if merged_df['求和项:数量（箱）'].sum() > 0 else 0

    # 按区域计算预测偏差
    region_bias = merged_df.groupby('所属区域').apply(
        lambda x: (x['求和项:数量（箱）'].sum() - x['预计销售量'].sum()) / x['求和项:数量（箱）'].sum() if x[
                                                                                                           '求和项:数量（箱）'].sum() > 0 else 0
    ).reset_index()
    region_bias.columns = ['所属区域', '偏差率']

    # 按月份计算预测偏差
    monthly_bias = merged_df.groupby('所属年月').apply(
        lambda x: (x['求和项:数量（箱）'].sum() - x['预计销售量'].sum()) / x['求和项:数量（箱）'].sum() if x[
                                                                                                           '求和项:数量（箱）'].sum() > 0 else 0
    ).reset_index()
    monthly_bias.columns = ['所属年月', '偏差率']

    # 过度预测和预测不足的产品
    product_bias = merged_df.groupby('产品代码').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    product_bias['偏差率'] = product_bias.apply(
        lambda row: (row['求和项:数量（箱）'] - row['预计销售量']) / row['求和项:数量（箱）'] if row[
                                                                                                 '求和项:数量（箱）'] > 0 else 0,
        axis=1
    )

    # 过度预测产品 (偏差率 < -0.1)
    over_forecast_products = product_bias[product_bias['偏差率'] < -0.1].sort_values('偏差率')

    # 预测不足产品 (偏差率 > 0.1)
    under_forecast_products = product_bias[product_bias['偏差率'] > 0.1].sort_values('偏差率', ascending=False)

    return {
        'overall_bias': overall_bias,
        'region_bias': region_bias,
        'monthly_bias': monthly_bias,
        'over_forecast_products': over_forecast_products,
        'under_forecast_products': under_forecast_products
    }


def calculate_product_growth(actual_monthly, regions=None, months=None, growth_min=-100, growth_max=500):
    """
    计算产品销量增长率，用于生成备货建议

    计算逻辑：
    1. 优先计算同比增长率：当前月与去年同月比较
    2. 若无同比数据，则计算环比增长率：当前月与上月比较
    3. 根据增长率给出备货建议

    参数:
    - actual_monthly: 实际销售数据
    - regions: 区域筛选
    - months: 月份筛选
    - growth_min/max: 增长率异常值截断范围

    返回:
    - all_growth: 所有产品增长率数据
    - latest_growth: 最新月份的增长率数据，包含趋势与备货建议
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


def generate_recommendation(growth_rate):
    """优化的备货建议生成函数"""
    # 基于增长率生成建议
    if growth_rate > 15:
        return {
            "建议": "增加备货",
            "调整比例": round(growth_rate),
            "颜色": "#4CAF50",
            "样式类": "recommendation-increase",
            "图标": "↑"
        }
    elif growth_rate > 0:
        return {
            "建议": "小幅增加",
            "调整比例": round(growth_rate / 2),
            "颜色": "#8BC34A",
            "样式类": "recommendation-increase",
            "图标": "↗"
        }
    elif growth_rate > -10:
        return {
            "建议": "维持现状",
            "调整比例": 0,
            "颜色": "#FFC107",
            "样式类": "recommendation-maintain",
            "图标": "→"
        }
    else:
        adjust = abs(round(growth_rate / 2))
        return {
            "建议": "减少备货",
            "调整比例": adjust,
            "颜色": "#F44336",
            "样式类": "recommendation-decrease",
            "图标": "↓"
        }


def format_product_code(code, product_info_df, include_name=True):
    """将产品代码格式化为只显示简化名称，不显示代码"""
    if product_info_df is None or code not in product_info_df['产品代码'].values:
        return code

    if include_name:
        # 仅使用简化名称，不包含代码
        filtered_df = product_info_df[product_info_df['产品代码'] == code]
        if not filtered_df.empty and '简化产品名称' in filtered_df.columns:
            simplified_name = filtered_df['简化产品名称'].iloc[0]
            if not pd.isna(simplified_name) and simplified_name:
                # 移除代码部分，只保留简化产品名称部分
                return simplified_name.replace(code, "").strip()

        # 回退到只显示产品名称，不显示代码
        product_name = filtered_df['产品名称'].iloc[0]
        return product_name
    else:
        return code


def format_number(value):
    """格式化数量显示为逗号分隔的完整数字"""
    return f"{int(value):,}"


# UI组件和显示函数
def display_metric_card(title, value, change=None, change_text=None, color="primary", icon=None,
                        description=None, suffix=None, on_click=None, key=None):
    """显示指标卡片组件"""
    # 处理百分比变化
    change_html = ""
    if change is not None:
        change_class = "positive" if change >= 0 else "negative"
        change_icon = "↑" if change >= 0 else "↓"
        change_html = f"""
        <div class="card-change {change_class}">
            {change_icon} {abs(change):.1f}% {change_text if change_text else ''}
        </div>
        """

    # 处理图标
    icon_html = ""
    if icon:
        icon_html = f"""
        <div class="metric-icon" style="background-color: rgba(0,0,0,0.05);">
            {icon}
        </div>
        """

    # 处理描述
    description_html = ""
    if description:
        description_html = f'<p class="card-text">{description}</p>'

    # 处理后缀
    suffix_html = suffix if suffix else ""

    # 生成唯一键
    card_key = key if key else f"metric_card_{title}_{random.randint(1000, 9999)}"

    # 组装HTML
    html = f"""
    <div id="{card_key}" class="metric-card border-{color}" onclick="{on_click if on_click else ''}">
        {icon_html}
        <p class="card-header">{title}</p>
        <p class="card-value">{value}{suffix_html}</p>
        {change_html}
        {description_html}
    </div>
    """

    return st.markdown(html, unsafe_allow_html=True)


def display_filter_panel():
    """显示改进的筛选面板"""
    with st.container():
        st.markdown('<div class="filter-title">📊 分析筛选</div>', unsafe_allow_html=True)

        # 使用列布局优化空间
        col1, col2 = st.columns(2)

        with col1:
            # 时间筛选区
            st.markdown('<div style="font-size: 0.9rem; margin-bottom: 0.5rem;">📅 时间范围</div>',
                        unsafe_allow_html=True)

            # 获取所有可能的月份
            all_months = []
            if 'processed_data' in st.session_state and 'merged_monthly' in st.session_state['processed_data']:
                all_months = sorted(st.session_state['processed_data']['merged_monthly']['所属年月'].unique())

            # 默认选择最近3个月或所有月份中最新的3个
            default_months = st.session_state.get('filter_months', [])
            if not default_months and all_months:
                default_months = all_months[-3:] if len(all_months) >= 3 else all_months

            selected_months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=default_months,
                key="filter_months_select"
            )

            # 更新会话状态
            st.session_state['filter_months'] = selected_months

        with col2:
            # 区域筛选区
            st.markdown('<div style="font-size: 0.9rem; margin-bottom: 0.5rem;">🌏 区域选择</div>',
                        unsafe_allow_html=True)

            # 获取所有可能的区域
            all_regions = []
            if 'processed_data' in st.session_state and 'merged_monthly' in st.session_state['processed_data']:
                all_regions = sorted(st.session_state['processed_data']['merged_monthly']['所属区域'].unique())

            # 默认选择所有区域
            default_regions = st.session_state.get('filter_regions', [])
            if not default_regions and all_regions:
                default_regions = all_regions

            selected_regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=default_regions,
                key="filter_regions_select"
            )

            # 更新会话状态
            st.session_state['filter_regions'] = selected_regions

    # 返回筛选结果
    return selected_months, selected_regions


def create_accuracy_change_chart(accuracy_trends, regions=None):
    """创建准确率变化趋势图"""
    if not accuracy_trends or accuracy_trends['monthly'].empty:
        return None

    # 准备数据
    trend_data = accuracy_trends['monthly'].copy()
    trend_data['数量准确率'] = trend_data['数量准确率'] * 100  # 转换为百分比

    # 创建图表
    fig = go.Figure()

    # 添加全国准确率线
    fig.add_trace(go.Scatter(
        x=trend_data['所属年月'],
        y=trend_data['数量准确率'],
        mode='lines+markers',
        name='全国准确率',
        line=dict(color='#1f3867', width=3),
        marker=dict(size=8)
    ))

    # 如果有选定区域，添加区域准确率线
    if regions and '全部' not in regions:
        region_data = accuracy_trends['region_monthly'].copy()
        region_data = region_data[region_data['所属区域'].isin(regions)]
        region_data['数量准确率'] = region_data['数量准确率'] * 100  # 转换为百分比

        # 为每个区域添加一条线
        for region in regions:
            region_trend = region_data[region_data['所属区域'] == region]
            if not region_trend.empty:
                fig.add_trace(go.Scatter(
                    x=region_trend['所属年月'],
                    y=region_trend['数量准确率'],
                    mode='lines+markers',
                    name=f'{region}区域',
                    marker=dict(size=6)
                ))

    # 添加基准线
    fig.add_shape(
        type="line",
        x0=trend_data['所属年月'].min(),
        x1=trend_data['所属年月'].max(),
        y0=80,
        y1=80,
        line=dict(color="green", width=1, dash="dash"),
        name="良好准确率基准"
    )

    # 更新布局
    fig.update_layout(
        title="预测准确率月度趋势",
        xaxis_title="月份",
        yaxis_title="准确率 (%)",
        yaxis=dict(range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='white',
        height=400
    )

    # 添加悬停信息
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>准确率: %{y:.1f}%<extra>%{name}</extra>'
    )

    return fig


def create_region_accuracy_heatmap(regional_accuracy, selected_months):
    """创建区域准确率热力图"""
    if not regional_accuracy or regional_accuracy['region_monthly'].empty:
        return None

    # 筛选数据
    region_data = regional_accuracy['region_monthly'].copy()
    if selected_months and len(selected_months) > 0:
        region_data = region_data[region_data['所属年月'].isin(selected_months)]

    # 准备热力图数据
    region_data['数量准确率'] = region_data['数量准确率'] * 100  # 转换为百分比

    # 数据透视表
    pivot_data = region_data.pivot_table(
        values='数量准确率',
        index='所属区域',
        columns='所属年月',
        aggfunc='mean'
    ).round(1)

    # 创建热力图
    fig = px.imshow(
        pivot_data,
        text_auto='.1f',
        color_continuous_scale=[
            [0, "rgb(220, 53, 69)"],  # 红色 - 低准确率
            [0.25, "rgb(255, 193, 7)"],  # 黄色 - 一般准确率
            [0.5, "rgb(255, 153, 51)"],  # 浅橙色 - 中等准确率
            [0.75, "rgb(40, 167, 69)"],  # 浅绿色 - 高等准确率
            [1, "rgb(0, 123, 255)"]  # 蓝色 - 最高准确率
        ],
        labels=dict(x="月份", y="区域", color="准确率 (%)"),
        range_color=[0, 100],
        aspect="auto"
    )

    # 更新布局
    fig.update_layout(
        title="区域月度预测准确率热力图",
        xaxis_title="月份",
        yaxis_title="区域",
        coloraxis_colorbar=dict(title="准确率 (%)"),
        plot_bgcolor='white',
        height=350
    )

    # 自定义悬停信息
    hovertemplate = '<b>%{y} 区域</b><br>%{x} 月份<br>准确率: %{z:.1f}%<extra></extra>'
    for i in range(len(fig.data)):
        fig.data[i].update(hovertemplate=hovertemplate)

    return fig


def create_forecast_bias_chart(bias_patterns):
    """创建预测偏差分析图"""
    if not bias_patterns or bias_patterns['monthly_bias'].empty:
        return None

    # 准备数据
    monthly_bias = bias_patterns['monthly_bias'].copy()
    monthly_bias['偏差率'] = monthly_bias['偏差率'] * 100  # 转换为百分比

    # 创建图表
    fig = go.Figure()

    # 添加偏差率柱状图
    fig.add_trace(go.Bar(
        x=monthly_bias['所属年月'],
        y=monthly_bias['偏差率'],
        marker_color=monthly_bias['偏差率'].apply(
            lambda x: '#4CAF50' if x > 0 else '#F44336'  # 绿色为低估，红色为高估
        ),
        name='预测偏差率',
        text=monthly_bias['偏差率'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))

    # 添加零线
    fig.add_shape(
        type="line",
        x0=monthly_bias['所属年月'].min(),
        x1=monthly_bias['所属年月'].max(),
        y0=0,
        y1=0,
        line=dict(color="black", width=1)
    )

    # 更新布局
    fig.update_layout(
        title="月度预测偏差趋势",
        xaxis_title="月份",
        yaxis_title="偏差率 (%)",
        yaxis=dict(
            tickformat='.1f',
            zeroline=False
        ),
        plot_bgcolor='white',
        height=350,
        margin=dict(t=50, b=50)
    )

    # 自定义悬停信息
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>偏差率: %{y:.1f}%<br>%{text}<extra></extra>'
    )

    # 添加说明标签
    fig.add_annotation(
        x=0.02,
        y=0.95,
        xref="paper",
        yref="paper",
        text="正值表示预测低估，负值表示预测高估",
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#1f3867",
        borderwidth=1,
        borderpad=4,
        font=dict(size=10)
    )

    return fig


def create_salesperson_accuracy_radar(salesperson_accuracy, selected_regions):
    """创建销售员准确率雷达图"""
    if not salesperson_accuracy or salesperson_accuracy['sales_overall'].empty:
        return None

    # 准备数据
    sales_data = salesperson_accuracy['sales_summary'].copy()

    # 筛选区域
    if selected_regions and len(selected_regions) > 0 and '全部' not in selected_regions:
        sales_data = sales_data[sales_data['所属区域'].isin(selected_regions)]

    # 计算每个销售员在各区域的准确率
    sales_data['数量准确率'] = sales_data['数量准确率'] * 100  # 转换为百分比

    # 按销售员分组
    top_salespersons = sales_data.groupby('销售员')['求和项:数量（箱）'].sum().nlargest(5).index.tolist()

    if not top_salespersons:
        return None

    # 创建雷达图
    fig = go.Figure()

    # 获取所有区域
    all_regions = sorted(sales_data['所属区域'].unique())

    # 为每个销售员添加一条雷达线
    for salesperson in top_salespersons:
        # 获取该销售员在各区域的准确率
        person_data = sales_data[sales_data['销售员'] == salesperson]

        # 准备雷达图数据
        radar_data = []
        for region in all_regions:
            region_accuracy = person_data[person_data['所属区域'] == region]['数量准确率'].mean()
            if np.isnan(region_accuracy):
                region_accuracy = 0
            radar_data.append(region_accuracy)

        # 如果只有1个区域，雷达图需要至少3个点，添加虚拟点
        if len(all_regions) < 3:
            for i in range(3 - len(all_regions)):
                all_regions.append(f"其他区域{i + 1}")
                radar_data.append(0)

        # 添加雷达线
        fig.add_trace(go.Scatterpolar(
            r=radar_data,
            theta=all_regions,
            fill='toself',
            name=salesperson
        ))

    # 更新布局
    fig.update_layout(
        title="销售员预测准确率分布",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=400
    )

    return fig


def create_product_accuracy_scatter(skus_data, product_info):
    """创建产品预测准确率与销量散点图"""
    if skus_data.empty:
        return None

    # 准备数据
    scatter_data = skus_data.copy()
    scatter_data['数量准确率'] = scatter_data['数量准确率'] * 100  # 转换为百分比

    # 添加产品显示名称
    scatter_data['产品显示'] = scatter_data['产品代码'].apply(
        lambda x: format_product_code(x, product_info, include_name=True)
    )

    # 创建散点图
    fig = px.scatter(
        scatter_data,
        x='求和项:数量（箱）',
        y='数量准确率',
        size='求和项:数量（箱）',
        color='数量准确率',
        hover_name='产品显示',
        text='产品显示',
        color_continuous_scale=[
            [0, "red"],
            [0.5, "yellow"],
            [0.8, "green"],
            [1, "blue"]
        ],
        size_max=40,
        range_color=[0, 100]
    )

    # 更新布局
    fig.update_layout(
        title="产品销量与预测准确率关系",
        xaxis_title="销量 (箱)",
        yaxis_title="准确率 (%)",
        yaxis=dict(range=[0, 100]),
        coloraxis_colorbar=dict(title="准确率 (%)"),
        plot_bgcolor='white',
        height=450
    )

    # 添加准确率基准线
    fig.add_shape(
        type="line",
        x0=scatter_data['求和项:数量（箱）'].min(),
        x1=scatter_data['求和项:数量（箱）'].max(),
        y0=80,
        y1=80,
        line=dict(color="green", width=1, dash="dash"),
        name="准确率基准"
    )

    # 更改悬停信息
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>销量: %{x:,.0f}箱<br>准确率: %{y:.1f}%<br>累计占比: %{customdata:.2f}%<extra></extra>',
        customdata=scatter_data['累计占比']
    )

    # 显示文本
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10)
    )

    return fig


def display_top_skus_analysis(top_skus, product_info, product_growth, title="重点SKU准确率分析"):
    """显示重点SKU分析内容"""
    if top_skus.empty:
        st.warning("没有足够的数据来分析重点SKU。")
        return

    # 添加产品名称
    top_skus['产品名称'] = top_skus['产品代码'].apply(
        lambda x: format_product_code(x, product_info, include_name=True)
    )

    # 计算统计数据
    accuracy_stats = {
        '高准确率(>80%)': len(top_skus[top_skus['数量准确率'] > 0.8]),
        '中等准确率(60-80%)': len(top_skus[(top_skus['数量准确率'] > 0.6) & (top_skus['数量准确率'] <= 0.8)]),
        '低准确率(<60%)': len(top_skus[top_skus['数量准确率'] <= 0.6])
    }

    # 创建图表
    col1, col2 = st.columns([2, 1])

    with col1:
        # 创建条形图
        fig_bar = go.Figure()

        # 转换百分比
        top_skus['数量准确率_pct'] = top_skus['数量准确率'] * 100

        # 添加条形图
        fig_bar.add_trace(go.Bar(
            y=top_skus['产品名称'],
            x=top_skus['求和项:数量（箱）'],
            name='销售量',
            orientation='h',
            marker=dict(
                color=top_skus['数量准确率_pct'],
                colorscale=[
                    [0, "red"],
                    [0.6, "yellow"],
                    [0.8, "green"],
                    [1, "blue"]
                ],
                colorbar=dict(
                    title="准确率(%)"
                )
            )
        ))

        # 更新布局
        fig_bar.update_layout(
            title=title,
            xaxis_title="销售量 (箱)",
            yaxis_title="产品",
            yaxis=dict(autorange="reversed"),  # 从上到下按销量排序
            plot_bgcolor='white',
            height=max(350, len(top_skus) * 30)
        )

        # 添加准确率标签
        for i, row in enumerate(top_skus.itertuples()):
            fig_bar.add_annotation(
                y=row.产品名称,
                x=row.求和项: 数量（箱） *1.02,
            text = f"{row.数量准确率_pct:.0f}%",
            showarrow = False,
            font = dict(
                color="black" if row.数量准确率 > 0.6 else "red",
                size=10
            )
            )

            # 悬停信息
            fig_bar.update_traces(
                hovertemplate='<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata:.2f}%<extra></extra>',
                customdata=top_skus['累计占比']
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # 显示准确率分布
            st.markdown("### 准确率分布")

            # 创建准确率分布饼图
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(accuracy_stats.keys()),
                values=list(accuracy_stats.values()),
                hole=.3,
                marker_colors=['#4CAF50', '#FFC107', '#F44336']
            )])

            fig_pie.update_layout(
                title="重点SKU准确率分布",
                height=300
            )

            st.plotly_chart(fig_pie, use_container_width=True)

            # 显示准确率最低的产品
            if len(top_skus) > 0:
                lowest_accuracy = top_skus.loc[top_skus['数量准确率'].idxmin()]
                st.markdown(f"""
            <div class="alert alert-warning">
                <strong>准确率最低产品:</strong> {lowest_accuracy['产品名称']}<br>
                准确率: {lowest_accuracy['数量准确率'] * 100:.1f}%<br>
                销量: {format_number(lowest_accuracy['求和项:数量（箱）'])}箱
            </div>
            """, unsafe_allow_html=True)

                # 添加行动建议
                if accuracy_stats['低准确率(<60%)'] > 0:
                    st.markdown(f"""
                <div class="alert alert-danger">
                    <strong>行动建议:</strong><br>
                    发现{accuracy_stats['低准确率(<60%)']}个重点SKU准确率低于60%，建议优先改进这些产品的预测方法。
                </div>
                """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                <div class="alert alert-success">
                    <strong>行动建议:</strong><br>
                    重点SKU预测准确率整体良好，建议保持当前预测方法。
                </div>
                """, unsafe_allow_html=True)

    def display_breadcrumb():
        """显示导航面包屑"""
        if 'breadcrumb' not in st.session_state:
            st.session_state['breadcrumb'] = [('总览', 'overview')]

        breadcrumb_html = '<div class="breadcrumb">'

        for i, (name, view) in enumerate(st.session_state['breadcrumb']):
            is_active = i == len(st.session_state['breadcrumb']) - 1
            class_name = "breadcrumb-item active" if is_active else "breadcrumb-item"

            if is_active:
                breadcrumb_html += f'<span class="{class_name}">{name}</span>'
            else:
                breadcrumb_html += f'<span class="{class_name}" onclick="breadcrumb_click_{i}()">{name}</span>'

            if i < len(st.session_state['breadcrumb']) - 1:
                breadcrumb_html += '<span class="breadcrumb-separator">/</span>'

        breadcrumb_html += '</div>'

        st.markdown(breadcrumb_html, unsafe_allow_html=True)

        # 添加JavaScript函数处理点击
        for i, (name, view) in enumerate(st.session_state['breadcrumb']):
            if i < len(st.session_state['breadcrumb']) - 1:
                st.markdown(f"""
            <script>
            function breadcrumb_click_{i}() {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{ view: '{view}', index: {i} }},
                    dataType: 'json'
                }}, '*');
            }}
            </script>
            """, unsafe_allow_html=True)

    def display_overview_page(processed_data, product_info, filter_months, filter_regions):
        """显示仪表盘总览页面"""
        # 显示标题和面包屑
        st.markdown('<h1 class="main-header">销售预测准确率分析仪表盘</h1>', unsafe_allow_html=True)

        # 更新导航路径
        st.session_state['breadcrumb'] = [('总览', 'overview')]
        display_breadcrumb()

        # 筛选数据
        filtered_data = {
            'merged_monthly': filter_data(processed_data['merged_monthly'], filter_months, filter_regions),
            'merged_by_salesperson': filter_data(processed_data['merged_by_salesperson'], filter_months,
                                                 filter_regions),
        }

        # 重新计算关键指标
        national_accuracy = calculate_national_accuracy(filtered_data['merged_monthly'])
        regional_accuracy = calculate_regional_accuracy(filtered_data['merged_monthly'])
        salesperson_accuracy = calculate_salesperson_accuracy(filtered_data['merged_by_salesperson'])
        accuracy_trends = calculate_accuracy_trends(filtered_data['merged_monthly'])

        # 总销售量和预测量
        total_actual = filtered_data['merged_monthly']['求和项:数量（箱）'].sum()
        total_forecast = filtered_data['merged_monthly']['预计销售量'].sum()

        # 计算环比变化
        latest_months = sorted(filtered_data['merged_monthly']['所属年月'].unique())
        if len(latest_months) >= 2:
            latest_month = latest_months[-1]
            prev_month = latest_months[-2]

            latest_data = filtered_data['merged_monthly'][filtered_data['merged_monthly']['所属年月'] == latest_month]
            prev_data = filtered_data['merged_monthly'][filtered_data['merged_monthly']['所属年月'] == prev_month]

            latest_accuracy = calculate_unified_accuracy(
                latest_data['求和项:数量（箱）'].sum(), latest_data['预计销售量'].sum()) * 100
            prev_accuracy = calculate_unified_accuracy(
                prev_data['求和项:数量（箱）'].sum(), prev_data['预计销售量'].sum()) * 100

            accuracy_change = latest_accuracy - prev_accuracy
        else:
            accuracy_change = 0

        # 计算区域准确率排名
        region_ranking = regional_accuracy['region_overall'].sort_values('数量准确率', ascending=False)
        region_ranking['数量准确率'] = region_ranking['数量准确率'] * 100  # 转换为百分比

        # 计算销售员准确率排名
        sales_ranking = salesperson_accuracy['sales_overall'].sort_values('数量准确率', ascending=False)
        sales_ranking['数量准确率'] = sales_ranking['数量准确率'] * 100  # 转换为百分比

        # 指标卡片行
        st.markdown('<div class="sub-header">📊 关键绩效指标</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        # 全国预测准确率
        with col1:
            national_accuracy_value = national_accuracy['overall']['数量准确率'] * 100
            display_metric_card(
                "全国预测准确率",
                f"{national_accuracy_value:.2f}%",
                change=accuracy_change,
                change_text="环比上月",
                color="primary",
                icon="📊",
                description="整体预测精度",
                key="card_national_accuracy",
                on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'accuracy', detail: 'national'}, dataType: 'json'}, '*')"
            )

        # 最高准确率区域
        with col2:
            if not region_ranking.empty:
                best_region = region_ranking.iloc[0]
                display_metric_card(
                    "最高准确率区域",
                    f"{best_region['所属区域']} ({best_region['数量准确率']:.2f}%)",
                    color="success",
                    icon="🏆",
                    description="预测最准确的区域",
                    key="card_best_region",
                    on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'accuracy', detail: 'region'}, dataType: 'json'}, '*')"
                )
            else:
                display_metric_card("最高准确率区域", "暂无数据", color="primary", icon="🏆")

        # 总实际销量
        with col3:
            display_metric_card(
                "总实际销量",
                format_number(total_actual),
                suffix=" 箱",
                color="info",
                icon="📦",
                description="选定期间内总销量",
                key="card_total_sales",
                on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'sales', detail: 'total'}, dataType: 'json'}, '*')"
            )

        # 预测偏差
        with col4:
            diff_percent = ((total_actual - total_forecast) / total_actual * 100) if total_actual > 0 else 0
            bias_type = "低估" if diff_percent > 0 else "高估"
            display_metric_card(
                "预测偏差",
                f"{abs(diff_percent):.2f}%",
                color="warning",
                icon="⚠️",
                description=f"整体{bias_type}程度",
                key="card_forecast_bias",
                on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'bias', detail: 'overall'}, dataType: 'json'}, '*')"
            )

        # 第二行指标卡
        col1, col2, col3, col4 = st.columns(4)

        # 最低准确率区域
        with col1:
            if len(region_ranking) > 1:
                worst_region = region_ranking.iloc[-1]
                display_metric_card(
                    "最低准确率区域",
                    f"{worst_region['所属区域']} ({worst_region['数量准确率']:.2f}%)",
                    color="danger",
                    icon="⚠️",
                    description="需要改进的区域",
                    key="card_worst_region",
                    on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'accuracy', detail: 'worst_region'}, dataType: 'json'}, '*')"
                )
            else:
                display_metric_card("最低准确率区域", "暂无数据", color="danger", icon="⚠️")

        # 预测准确率最高的销售员
        with col2:
            if not sales_ranking.empty:
                best_salesperson = sales_ranking.iloc[0]
                display_metric_card(
                    "最佳预测销售员",
                    f"{best_salesperson['销售员']} ({best_salesperson['数量准确率']:.2f}%)",
                    color="success",
                    icon="👑",
                    description="预测最准确的销售员",
                    key="card_best_salesperson",
                    on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'accuracy', detail: 'salesperson'}, dataType: 'json'}, '*')"
                )
            else:
                display_metric_card("最佳预测销售员", "暂无数据", color="success", icon="👑")

        # 高估产品占比
        with col3:
            overforecast_count = len(processed_data['bias_patterns']['over_forecast_products'])
            total_products = len(processed_data['merged_monthly']['产品代码'].unique())
            overforecast_pct = (overforecast_count / total_products * 100) if total_products > 0 else 0

            display_metric_card(
                "高估产品占比",
                f"{overforecast_pct:.2f}%",
                color="info",
                icon="📉",
                description=f"{overforecast_count}个产品预测过高",
                key="card_overforecast",
                on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'bias', detail: 'over'}, dataType: 'json'}, '*')"
            )

        # 低估产品占比
        with col4:
            underforecast_count = len(processed_data['bias_patterns']['under_forecast_products'])
            underforecast_pct = (underforecast_count / total_products * 100) if total_products > 0 else 0

            display_metric_card(
                "低估产品占比",
                f"{underforecast_pct:.2f}%",
                color="warning",
                icon="📈",
                description=f"{underforecast_count}个产品预测过低",
                key="card_underforecast",
                on_click="parent.postMessage({type: 'streamlit:setComponentValue', value: {view: 'bias', detail: 'under'}, dataType: 'json'}, '*')"
            )

        # 准确率趋势和区域分析
        st.markdown('<div class="sub-header">📈 预测准确率分析</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 创建准确率变化趋势图
            accuracy_chart = create_accuracy_change_chart(accuracy_trends, filter_regions)
            if accuracy_chart:
                st.plotly_chart(accuracy_chart, use_container_width=True)
            else:
                st.warning("没有足够的数据来生成准确率趋势图。")

        with col2:
            # 创建区域热力图
            heatmap_chart = create_region_accuracy_heatmap(regional_accuracy, filter_months)
            if heatmap_chart:
                st.plotly_chart(heatmap_chart, use_container_width=True)
            else:
                st.warning("没有足够的数据来生成区域准确率热力图。")

        # 预测偏差分析
        st.markdown('<div class="sub-header">🔍 预测偏差分析</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 创建预测偏差分析图
            bias_chart = create_forecast_bias_chart(processed_data['bias_patterns'])
            if bias_chart:
                st.plotly_chart(bias_chart, use_container_width=True)
            else:
                st.warning("没有足够的数据来生成预测偏差分析图。")

        with col2:
            # 创建销售员准确率雷达图
            radar_chart = create_salesperson_accuracy_radar(salesperson_accuracy, filter_regions)
            if radar_chart:
                st.plotly_chart(radar_chart, use_container_width=True)
            else:
                st.warning("没有足够的数据来生成销售员准确率雷达图。")

        # 重点SKU分析
        st.markdown('<div class="sub-header">🏆 重点SKU分析</div>', unsafe_allow_html=True)

        # 计算当前筛选条件下的重点SKU
        filtered_top_skus = calculate_top_skus(filtered_data['merged_monthly'], by_region=False)

        if not filtered_top_skus.empty:
            # 准备SKU散点图
            col1, col2 = st.columns([2, 1])

            with col1:
                # 创建产品预测准确率与销量散点图
                scatter_chart = create_product_accuracy_scatter(filtered_top_skus, product_info)
                if scatter_chart:
                    st.plotly_chart(scatter_chart, use_container_width=True)
                else:
                    st.warning("没有足够的数据来生成产品准确率分析图。")

            with col2:
                # 显示重点SKU列表
                st.markdown("### 重点SKU列表")
                top_skus_display = filtered_top_skus.copy()
                top_skus_display['产品名称'] = top_skus_display['产品代码'].apply(
                    lambda x: format_product_code(x, product_info, include_name=True)
                )
                top_skus_display['准确率'] = (top_skus_display['数量准确率'] * 100).round(1).astype(str) + '%'

                # 只显示部分列
                display_cols = ['产品名称', '求和项:数量（箱）', '准确率', '累计占比']
                st.dataframe(
                    top_skus_display[display_cols].rename(columns={
                        '求和项:数量（箱）': '销量',
                        '累计占比': '累计占比(%)'
                    }),
                    hide_index=True,
                    use_container_width=True
                )

                # 添加查看更多的链接
                st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <button id="view_more_skus" style="background-color: #1f3867; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer;">
                    查看更多SKU分析 ▶
                </button>
            </div>
            <script>
            document.getElementById('view_more_skus').onclick = function() {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: { view: 'sku_analysis', detail: 'national' },
                    dataType: 'json'
                }, '*');
            }
            </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的数据来进行重点SKU分析。")

        # 导航到详细分析
        st.markdown('<div class="sub-header">🔍 深入分析</div>', unsafe_allow_html=True)

        # 创建导航卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
        <div class="hover-card" id="nav_accuracy" style="cursor: pointer;">
            <h3 style="color: #1f3867;">📊 准确率分析</h3>
            <p>深入分析预测准确率，按区域、销售员、产品等维度查看详细数据。</p>
            <p style="text-align: right; color: #1f3867;">查看详情 ▶</p>
        </div>
        <script>
        document.getElementById('nav_accuracy').onclick = function() {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: { view: 'accuracy', detail: 'all' },
                dataType: 'json'
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
        <div class="hover-card" id="nav_bias" style="cursor: pointer;">
            <h3 style="color: #1f3867;">🔍 偏差分析</h3>
            <p>识别预测偏差模式，找出系统性高估或低估的产品和区域。</p>
            <p style="text-align: right; color: #1f3867;">查看详情 ▶</p>
        </div>
        <script>
        document.getElementById('nav_bias').onclick = function() {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: { view: 'bias', detail: 'all' },
                dataType: 'json'
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
        <div class="hover-card" id="nav_sku" style="cursor: pointer;">
            <h3 style="color: #1f3867;">🏆 重点SKU分析</h3>
            <p>分析销量占比80%的重点SKU预测准确率，优化库存管理。</p>
            <p style="text-align: right; color: #1f3867;">查看详情 ▶</p>
        </div>
        <script>
        document.getElementById('nav_sku').onclick = function() {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: { view: 'sku_analysis', detail: 'all' },
                dataType: 'json'
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
        <div class="hover-card" id="nav_trend" style="cursor: pointer;">
            <h3 style="color: #1f3867;">📈 趋势分析</h3>
            <p>分析预测准确率随时间的变化趋势，识别季节性模式。</p>
            <p style="text-align: right; color: #1f3867;">查看详情 ▶</p>
        </div>
        <script>
        document.getElementById('nav_trend').onclick = function() {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: { view: 'trend', detail: 'all' },
                dataType: 'json'
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)

    def display_accuracy_analysis_page(processed_data, product_info, filter_months, filter_regions, detail='all'):
        """显示准确率分析页面"""
        # 显示标题和面包屑
        st.markdown('<h1 class="main-header">预测准确率分析</h1>', unsafe_allow_html=True)

        # 更新导航路径
        st.session_state['breadcrumb'] = [('总览', 'overview'), ('准确率分析', 'accuracy')]
        display_breadcrumb()

        # 筛选数据
        filtered_data = {
            'merged_monthly': filter_data(processed_data['merged_monthly'], filter_months, filter_regions),
            'merged_by_salesperson': filter_data(processed_data['merged_by_salesperson'], filter_months,
                                                 filter_regions),
        }

        # 重新计算关键指标
        national_accuracy = calculate_national_accuracy(filtered_data['merged_monthly'])
        regional_accuracy = calculate_regional_accuracy(filtered_data['merged_monthly'])
        salesperson_accuracy = calculate_salesperson_accuracy(filtered_data['merged_by_salesperson'])

        # 区域标签页
        region_tabs = ["全国"] + (filter_regions if filter_regions else [])

        # 创建选项卡集
        st.markdown('<div class="region-tabs">', unsafe_allow_html=True)
        for i, tab in enumerate(region_tabs):
            active_class = " active" if (detail == 'national' and tab == '全国') or (detail == tab) else ""
            st.markdown(f"""
        <div class="region-tab{active_class}" id="tab_{i}" onclick="select_tab('{tab}')">
            {tab}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 添加JavaScript处理选项卡点击
        st.markdown("""
    <script>
    function select_tab(tab) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: { view: 'accuracy', detail: tab },
            dataType: 'json'
        }, '*');
    }
    </script>
    """, unsafe_allow_html=True)

        # 显示选定区域的数据
        if detail == 'national' or detail == 'all':
            display_national_accuracy(national_accuracy, regional_accuracy)
        elif detail == 'region':
            display_regional_accuracy(regional_accuracy)
        elif detail == 'salesperson':
            display_salesperson_accuracy(salesperson_accuracy, filter_regions)
        elif detail in filter_regions:
            display_region_specific_accuracy(detail, processed_data, filter_months)
        else:
            display_national_accuracy(national_accuracy, regional_accuracy)

        # 添加区域下钻分析说明
        if detail != 'salesperson':
            st.markdown("""
            <div class="chart-explanation">
                <strong>提示：</strong> 点击区域名称可以下钻查看该区域的详细分析。点击销售员名称可以查看该销售员的预测准确率详情。
            </div>
            """, unsafe_allow_html=True)


def display_national_accuracy(national_accuracy, regional_accuracy):
    """显示全国预测准确率分析"""
    # 准备数据
    monthly_data = national_accuracy['monthly'].copy()
    monthly_data['数量准确率'] = monthly_data['数量准确率'] * 100  # 转换为百分比

    region_data = regional_accuracy['region_overall'].copy()
    region_data['数量准确率'] = region_data['数量准确率'] * 100  # 转换为百分比

    # 计算全国总体指标
    overall_accuracy = national_accuracy['overall']['数量准确率'] * 100

    # 指标卡片
    st.markdown("### 全国预测准确率概览")

    col1, col2, col3 = st.columns(3)

    with col1:
        display_metric_card(
            "全国平均准确率",
            f"{overall_accuracy:.2f}%",
            color="primary",
            icon="📊",
            description="所选期间内平均准确率"
        )

    with col2:
        if not monthly_data.empty:
            best_month = monthly_data.loc[monthly_data['数量准确率'].idxmax()]
            display_metric_card(
                "最高准确率月份",
                f"{best_month['所属年月']} ({best_month['数量准确率']:.2f}%)",
                color="success",
                icon="🏆",
                description="预测最准确的月份"
            )
        else:
            display_metric_card("最高准确率月份", "暂无数据", color="success", icon="🏆")

    with col3:
        if not monthly_data.empty:
            worst_month = monthly_data.loc[monthly_data['数量准确率'].idxmin()]
            display_metric_card(
                "最低准确率月份",
                f"{worst_month['所属年月']} ({worst_month['数量准确率']:.2f}%)",
                color="danger",
                icon="⚠️",
                description="预测最不准确的月份"
            )
        else:
            display_metric_card("最低准确率月份", "暂无数据", color="danger", icon="⚠️")

    # 月度准确率趋势图
    st.markdown("### 全国月度准确率趋势")

    if not monthly_data.empty:
        fig = go.Figure()

        # 添加准确率线
        fig.add_trace(go.Scatter(
            x=monthly_data['所属年月'],
            y=monthly_data['数量准确率'],
            mode='lines+markers',
            name='准确率',
            line=dict(color='#1f3867', width=2),
            marker=dict(size=8)
        ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=monthly_data['所属年月'].min(),
            x1=monthly_data['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            plot_bgcolor='white',
            height=400,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>准确率: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        if len(monthly_data) > 1:
            trend = "上升" if monthly_data['数量准确率'].iloc[-1] > monthly_data['数量准确率'].iloc[-2] else "下降"
            trend_value = abs(monthly_data['数量准确率'].iloc[-1] - monthly_data['数量准确率'].iloc[-2])

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 近期全国预测准确率呈{trend}趋势，最近一个月相比上月{trend}了{trend_value:.2f}个百分点。
                月度平均准确率为{monthly_data['数量准确率'].mean():.2f}%。
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成全国月度准确率趋势图。")

    # 区域准确率对比
    st.markdown("### 各区域准确率对比")

    if not region_data.empty:
        # 按准确率排序
        region_data = region_data.sort_values('数量准确率', ascending=False)

        fig = go.Figure()

        # 添加条形图
        fig.add_trace(go.Bar(
            y=region_data['所属区域'],
            x=region_data['数量准确率'],
            orientation='h',
            marker=dict(
                color=region_data['数量准确率'],
                colorscale='Viridis',
                colorbar=dict(title='准确率 (%)'),
                cmin=0,
                cmax=100
            ),
            text=region_data['数量准确率'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto'
        ))

        # 更新布局
        fig.update_layout(
            xaxis_title="准确率 (%)",
            yaxis_title="区域",
            xaxis=dict(range=[0, 100]),
            plot_bgcolor='white',
            height=400
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>准确率: %{x:.2f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        best_region = region_data.iloc[0]
        worst_region = region_data.iloc[-1]
        avg_accuracy = region_data['数量准确率'].mean()

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> {best_region['所属区域']}区域预测准确率最高，为{best_region['数量准确率']:.2f}%；
            {worst_region['所属区域']}区域预测准确率最低，为{worst_region['数量准确率']:.2f}%。
            各区域平均准确率为{avg_accuracy:.2f}%。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域准确率对比图。")


def display_regional_accuracy(regional_accuracy):
    """显示区域预测准确率分析"""
    # 准备数据
    region_data = regional_accuracy['region_overall'].copy()
    region_data['数量准确率'] = region_data['数量准确率'] * 100  # 转换为百分比

    # 显示标题
    st.markdown("### 区域预测准确率详细分析")

    # 详细区域数据表格
    if not region_data.empty:
        # 添加差异率
        region_data['差异率%'] = region_data['差异率'].round(2)

        # 格式化数据
        display_df = region_data.copy()
        display_df['数量准确率'] = display_df['数量准确率'].round(2).astype(str) + '%'
        display_df['差异率'] = display_df['差异率'].round(2).astype(str) + '%'
        display_df = display_df.rename(columns={
            '求和项:数量（箱）': '实际销量',
            '预计销售量': '预测销量',
            '数量差异': '差异',
            '数量准确率': '准确率'
        })

        # 显示表格
        st.dataframe(
            display_df[['所属区域', '实际销量', '预测销量', '差异', '准确率', '差异率']],
            use_container_width=True,
            column_config={
                "所属区域": st.column_config.Column("区域", width="small"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "差异": st.column_config.NumberColumn("差异", format="%d"),
                "准确率": st.column_config.TextColumn("准确率"),
                "差异率": st.column_config.TextColumn("差异率", help="正值表示低估，负值表示高估")
            },
            hide_index=True
        )
    else:
        st.warning("没有足够的区域数据进行分析。")

    # 区域准确率热力图
    st.markdown("### 区域月度准确率热力图")

    region_monthly = regional_accuracy['region_monthly'].copy()
    if not region_monthly.empty:
        region_monthly['数量准确率'] = region_monthly['数量准确率'] * 100  # 转换为百分比

        # 数据透视表
        pivot_data = region_monthly.pivot_table(
            values='数量准确率',
            index='所属区域',
            columns='所属年月',
            aggfunc='mean'
        ).round(1)

        # 创建热力图
        fig = px.imshow(
            pivot_data,
            text_auto='.1f',
            color_continuous_scale=[
                [0, "rgb(220, 53, 69)"],  # 红色 - 低准确率
                [0.5, "rgb(255, 193, 7)"],  # 黄色 - 中等准确率
                [0.8, "rgb(40, 167, 69)"],  # 绿色 - 高准确率
                [1, "rgb(0, 123, 255)"]  # 蓝色 - 最高准确率
            ],
            labels=dict(x="月份", y="区域", color="准确率 (%)"),
            range_color=[0, 100],
            aspect="auto"
        )

        # 更新布局
        fig.update_layout(
            title="区域月度预测准确率热力图",
            xaxis_title="月份",
            yaxis_title="区域",
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        st.markdown("""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 此热力图展示了各区域在不同月份的预测准确率，颜色越深表示准确率越高。
            通过观察热力图，可以识别出区域预测准确率的季节性模式和变化趋势。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域月度准确率热力图。")

    # 区域差异率分析
    st.markdown("### 区域预测偏差分析")

    if not region_data.empty:
        # 创建区域差异率图
        fig = go.Figure()

        # 按差异率绝对值降序排序
        region_data = region_data.sort_values('差异率', key=abs, ascending=False)

        # 添加条形图
        fig.add_trace(go.Bar(
            y=region_data['所属区域'],
            x=region_data['差异率'],
            orientation='h',
            marker=dict(
                color=region_data['差异率'].apply(
                    lambda x: '#4CAF50' if x > 0 else '#F44336'  # 绿色为低估，红色为高估
                )
            ),
            text=region_data['差异率'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto'
        ))

        # 添加零线
        fig.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=-0.5,
            y1=len(region_data) - 0.5,
            line=dict(color="black", width=1)
        )

        # 更新布局
        fig.update_layout(
            title="区域预测偏差分析",
            xaxis_title="偏差率 (%)",
            yaxis_title="区域",
            plot_bgcolor='white',
            height=400
        )

        # 添加图例说明
        fig.add_annotation(
            x=-region_data['差异率'].abs().max() * 0.9,
            y=len(region_data) - 0.5,
            text="高估",
            showarrow=False,
            font=dict(color="#F44336")
        )

        fig.add_annotation(
            x=region_data['差异率'].abs().max() * 0.9,
            y=len(region_data) - 0.5,
            text="低估",
            showarrow=False,
            font=dict(color="#4CAF50")
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        most_underestimated = region_data[region_data['差异率'] > 0].iloc[0] if len(
            region_data[region_data['差异率'] > 0]) > 0 else None
        most_overestimated = region_data[region_data['差异率'] < 0].iloc[0] if len(
            region_data[region_data['差异率'] < 0]) > 0 else None

        explanation = "<strong>图表解释：</strong> 此图展示了各区域的预测偏差率，正值表示预测低估（实际销量高于预测），负值表示预测高估（实际销量低于预测）。"

        if most_underestimated is not None:
            explanation += f" {most_underestimated['所属区域']}区域预测最为低估，偏差率为{most_underestimated['差异率']:.2f}%。"

        if most_overestimated is not None:
            explanation += f" {most_overestimated['所属区域']}区域预测最为高估，偏差率为{most_overestimated['差异率']:.2f}%。"

        st.markdown(f"""
        <div class="chart-explanation">
            {explanation}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域预测偏差分析图。")


def display_salesperson_accuracy(salesperson_accuracy, selected_regions):
    """显示销售员预测准确率分析"""
    # 准备数据
    sales_overall = salesperson_accuracy['sales_overall'].copy()
    sales_overall['数量准确率'] = sales_overall['数量准确率'] * 100  # 转换为百分比

    sales_by_region = salesperson_accuracy['sales_by_region'].copy()
    sales_by_region['数量准确率'] = sales_by_region['数量准确率'] * 100  # 转换为百分比

    # 显示标题
    st.markdown("### 销售员预测准确率分析")

    # 销售员准确率排名
    if not sales_overall.empty:
        # 按准确率排序
        sales_overall = sales_overall.sort_values('数量准确率', ascending=False)

        fig = go.Figure()

        # 添加条形图
        fig.add_trace(go.Bar(
            y=sales_overall['销售员'],
            x=sales_overall['数量准确率'],
            orientation='h',
            marker=dict(
                color=sales_overall['数量准确率'],
                colorscale='Viridis',
                colorbar=dict(title='准确率 (%)'),
                cmin=0,
                cmax=100
            ),
            text=sales_overall['数量准确率'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto'
        ))

        # 更新布局
        fig.update_layout(
            title="销售员预测准确率排名",
            xaxis_title="准确率 (%)",
            yaxis_title="销售员",
            xaxis=dict(range=[0, 100]),
            plot_bgcolor='white',
            height=max(400, len(sales_overall) * 30)
        )

        # 添加准确率基准线
        fig.add_shape(
            type="line",
            x0=80,
            x1=80,
            y0=-0.5,
            y1=len(sales_overall) - 0.5,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        best_salesperson = sales_overall.iloc[0]
        worst_salesperson = sales_overall.iloc[-1]
        avg_accuracy = sales_overall['数量准确率'].mean()

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> {best_salesperson['销售员']}的预测准确率最高，为{best_salesperson['数量准确率']:.2f}%；
            {worst_salesperson['销售员']}的预测准确率最低，为{worst_salesperson['数量准确率']:.2f}%。
            销售员平均准确率为{avg_accuracy:.2f}%。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成销售员准确率排名图。")

    # 区域内销售员准确率对比
    if selected_regions and len(selected_regions) > 0 and not sales_by_region.empty:
        st.markdown("### 各区域销售员准确率对比")

        # 筛选选定区域的数据
        if '全部' not in selected_regions:
            region_sales = sales_by_region[sales_by_region['所属区域'].isin(selected_regions)]
        else:
            region_sales = sales_by_region

        if not region_sales.empty:
            # 创建热力图
            pivot_data = region_sales.pivot_table(
                values='数量准确率',
                index='销售员',
                columns='所属区域',
                aggfunc='mean'
            ).round(1)

            fig = px.imshow(
                pivot_data,
                text_auto='.1f',
                color_continuous_scale=[
                    [0, "rgb(220, 53, 69)"],  # 红色 - 低准确率
                    [0.5, "rgb(255, 193, 7)"],  # 黄色 - 中等准确率
                    [0.8, "rgb(40, 167, 69)"],  # 绿色 - 高准确率
                    [1, "rgb(0, 123, 255)"]  # 蓝色 - 最高准确率
                ],
                labels=dict(x="区域", y="销售员", color="准确率 (%)"),
                range_color=[0, 100],
                aspect="auto"
            )

            # 更新布局
            fig.update_layout(
                title="各区域销售员准确率热力图",
                xaxis_title="区域",
                yaxis_title="销售员",
                coloraxis_colorbar=dict(title="准确率 (%)"),
                plot_bgcolor='white',
                height=max(400, len(pivot_data) * 30)
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解释
            st.markdown("""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 此热力图展示了销售员在不同区域的预测准确率，颜色越深表示准确率越高。
                这有助于识别销售员在不同区域的表现差异，从而有针对性地改进预测能力。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("所选区域没有足够的销售员数据。")

    # 销售员准确率雷达图
    st.markdown("### 销售员预测准确率雷达图")

    if not sales_by_region.empty and len(sales_overall) > 0:
        # 选择前5名销售员进行对比
        top_salespersons = sales_overall.nlargest(5, '数量准确率')['销售员'].tolist()

        # 获取所有区域
        all_regions = sorted(sales_by_region['所属区域'].unique())

        if len(all_regions) > 0:
            # 创建雷达图
            fig = go.Figure()

            # 为每个销售员添加一条雷达线
            for salesperson in top_salespersons:
                # 获取该销售员在各区域的准确率
                person_data = sales_by_region[sales_by_region['销售员'] == salesperson]

                # 准备雷达图数据
                radar_data = []
                for region in all_regions:
                    region_accuracy = person_data[person_data['所属区域'] == region]['数量准确率'].mean()
                    if np.isnan(region_accuracy):
                        region_accuracy = 0
                    radar_data.append(region_accuracy)

                # 如果只有1个区域，雷达图需要至少3个点，添加虚拟点
                if len(all_regions) < 3:
                    for i in range(3 - len(all_regions)):
                        all_regions.append(f"虚拟区域{i + 1}")
                        radar_data.append(0)

                # 添加雷达线
                fig.add_trace(go.Scatterpolar(
                    r=radar_data,
                    theta=all_regions,
                    fill='toself',
                    name=salesperson
                ))

            # 更新布局
            fig.update_layout(
                title="销售员各区域预测准确率雷达图",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解释
            st.markdown(f"""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 此雷达图展示了预测准确率前5名销售员在各区域的表现。
                通过对比雷达线的形状，可以识别销售员在不同区域的预测能力差异。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("没有足够的区域数据来生成雷达图。")
    else:
        st.warning("没有足够的销售员数据来生成雷达图。")


def display_region_specific_accuracy(region, processed_data, filter_months):
    """显示特定区域的准确率分析"""
    # 筛选区域数据
    region_data = filter_data(processed_data['merged_monthly'], filter_months, [region])
    region_salesperson_data = filter_data(processed_data['merged_by_salesperson'], filter_months, [region])

    # 显示标题
    st.markdown(f"### {region}区域预测准确率分析")

    # 计算关键指标
    region_accuracy = calculate_national_accuracy(region_data)  # 复用函数计算区域整体准确率
    salesperson_in_region = calculate_salesperson_accuracy(region_salesperson_data)

    # 区域总体准确率
    overall_accuracy = region_accuracy['overall']['数量准确率'] * 100

    # 显示指标卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        display_metric_card(
            f"{region}区域平均准确率",
            f"{overall_accuracy:.2f}%",
            color="primary",
            icon="📊",
            description="所选期间内平均准确率"
        )

    with col2:
        monthly_data = region_accuracy['monthly'].copy()
        if not monthly_data.empty:
            monthly_data['数量准确率'] = monthly_data['数量准确率'] * 100
            best_month = monthly_data.loc[monthly_data['数量准确率'].idxmax()]
            display_metric_card(
                "最高准确率月份",
                f"{best_month['所属年月']} ({best_month['数量准确率']:.2f}%)",
                color="success",
                icon="🏆",
                description="预测最准确的月份"
            )
        else:
            display_metric_card("最高准确率月份", "暂无数据", color="success", icon="🏆")

    with col3:
        if not salesperson_in_region['sales_overall'].empty:
            salesperson_in_region['sales_overall']['数量准确率'] = salesperson_in_region['sales_overall'][
                                                                       '数量准确率'] * 100
            best_salesperson = salesperson_in_region['sales_overall'].loc[
                salesperson_in_region['sales_overall']['数量准确率'].idxmax()]
            display_metric_card(
                "最佳预测销售员",
                f"{best_salesperson['销售员']} ({best_salesperson['数量准确率']:.2f}%)",
                color="info",
                icon="👑",
                description="区域内预测最准确的销售员"
            )
        else:
            display_metric_card("最佳预测销售员", "暂无数据", color="info", icon="👑")

    # 月度准确率趋势图
    st.markdown(f"### {region}区域月度准确率趋势")

    if not monthly_data.empty:
        fig = go.Figure()

        # 添加准确率线
        fig.add_trace(go.Scatter(
            x=monthly_data['所属年月'],
            y=monthly_data['数量准确率'],
            mode='lines+markers',
            name='准确率',
            line=dict(color='#1f3867', width=2),
            marker=dict(size=8)
        ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=monthly_data['所属年月'].min(),
            x1=monthly_data['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            plot_bgcolor='white',
            height=400,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>准确率: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        if len(monthly_data) > 1:
            trend = "上升" if monthly_data['数量准确率'].iloc[-1] > monthly_data['数量准确率'].iloc[-2] else "下降"
            trend_value = abs(monthly_data['数量准确率'].iloc[-1] - monthly_data['数量准确率'].iloc[-2])

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 近期{region}区域预测准确率呈{trend}趋势，最近一个月相比上月{trend}了{trend_value:.2f}个百分点。
                区域月度平均准确率为{monthly_data['数量准确率'].mean():.2f}%。
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"没有足够的数据来生成{region}区域月度准确率趋势图。")

    # 区域内销售员准确率分析
    st.markdown(f"### {region}区域销售员准确率分析")

    sales_summary = salesperson_in_region['sales_summary'].copy()
    if not sales_summary.empty:
        # 按销售员分组并计算平均准确率
        sales_avg = sales_summary.groupby('销售员').agg({
            '数量准确率': 'mean',
            '求和项:数量（箱）': 'sum'
        }).reset_index()

        sales_avg['数量准确率'] = sales_avg['数量准确率'] * 100  # 转换为百分比

        # 按准确率排序
        sales_avg = sales_avg.sort_values('数量准确率', ascending=False)

        fig = go.Figure()

        # 添加条形图
        fig.add_trace(go.Bar(
            y=sales_avg['销售员'],
            x=sales_avg['数量准确率'],
            orientation='h',
            marker=dict(
                color=sales_avg['数量准确率'],
                colorscale='Viridis',
                colorbar=dict(title='准确率 (%)'),
                cmin=0,
                cmax=100
            ),
            text=sales_avg['数量准确率'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto'
        ))

        # 更新布局
        fig.update_layout(
            title=f"{region}区域销售员预测准确率排名",
            xaxis_title="准确率 (%)",
            yaxis_title="销售员",
            xaxis=dict(range=[0, 100]),
            plot_bgcolor='white',
            height=max(400, len(sales_avg) * 30)
        )

        # 添加准确率基准线
        fig.add_shape(
            type="line",
            x0=80,
            x1=80,
            y0=-0.5,
            y1=len(sales_avg) - 0.5,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>准确率: %{x:.2f}%<br>销售量: %{customdata:,} 箱<extra></extra>',
            customdata=sales_avg['求和项:数量（箱）']
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        best_salesperson = sales_avg.iloc[0]
        worst_salesperson = sales_avg.iloc[-1]
        avg_accuracy = sales_avg['数量准确率'].mean()

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> {region}区域内，{best_salesperson['销售员']}的预测准确率最高，为{best_salesperson['数量准确率']:.2f}%；
            {worst_salesperson['销售员']}的预测准确率最低，为{worst_salesperson['数量准确率']:.2f}%。
            区域内销售员平均准确率为{avg_accuracy:.2f}%。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"没有足够的数据来分析{region}区域内销售员准确率。")

    # 区域产品准确率分析
    st.markdown(f"### {region}区域产品预测准确率分析")

    # 按产品分组
    product_accuracy = region_data.groupby('产品代码').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算准确率
    product_accuracy['数量准确率'] = product_accuracy.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    ) * 100

    # 筛选销量较大的产品（前10个）
    top_products = product_accuracy.nlargest(10, '求和项:数量（箱）')

    if not top_products.empty:
        # 创建散点图
        fig = px.scatter(
            top_products,
            x='求和项:数量（箱）',
            y='数量准确率',
            size='求和项:数量（箱）',
            color='数量准确率',
            hover_name='产品代码',
            color_continuous_scale=[
                [0, "red"],
                [0.5, "yellow"],
                [0.8, "green"],
                [1, "blue"]
            ],
            size_max=40,
            range_color=[0, 100]
        )

        # 更新布局
        fig.update_layout(
            title=f"{region}区域主要产品销量与预测准确率关系",
            xaxis_title="销量 (箱)",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=500
        )

        # 添加准确率基准线
        fig.add_shape(
            type="line",
            x0=top_products['求和项:数量（箱）'].min(),
            x1=top_products['求和项:数量（箱）'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="准确率基准"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解释
        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 此散点图展示了{region}区域内销量最高的10个产品的预测准确率。
            点的大小表示销量，颜色表示准确率（颜色越深表示准确率越高）。
            通过观察图中的散点分布，可以识别销量大但准确率低的产品，优先改进这些产品的预测方法。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"没有足够的数据来分析{region}区域产品预测准确率。")


def display_bias_analysis_page(processed_data, product_info, filter_months, filter_regions, detail='all'):
    """显示预测偏差分析页面"""
    # 显示标题和面包屑
    st.markdown('<h1 class="main-header">预测偏差分析</h1>', unsafe_allow_html=True)

    # 更新导航路径
    st.session_state['breadcrumb'] = [('总览', 'overview'), ('偏差分析', 'bias')]
    display_breadcrumb()

    # 筛选数据
    filtered_data = {
        'merged_monthly': filter_data(processed_data['merged_monthly'], filter_months, filter_regions),
    }

    # 重新计算偏差模式
    bias_patterns = identify_bias_patterns(filtered_data['merged_monthly'])

    # 创建选项卡
    tabs = st.tabs(["总体偏差", "区域偏差", "产品偏差", "月度偏差"])

    with tabs[0]:  # 总体偏差
        display_overall_bias(bias_patterns, filtered_data)

    with tabs[1]:  # 区域偏差
        display_region_bias(bias_patterns, filtered_data)

    with tabs[2]:  # 产品偏差
        display_product_bias(bias_patterns, product_info)

    with tabs[3]:  # 月度偏差
        display_monthly_bias(bias_patterns, filtered_data)


def display_overall_bias(bias_patterns, filtered_data):
    """显示总体偏差分析"""
    # 计算总体偏差
    total_actual = filtered_data['merged_monthly']['求和项:数量（箱）'].sum()
    total_forecast = filtered_data['merged_monthly']['预计销售量'].sum()
    overall_bias = (total_actual - total_forecast) / total_actual if total_actual > 0 else 0
    overall_bias_pct = overall_bias * 100

    # 偏差类型
    bias_type = "低估" if overall_bias > 0 else "高估"
    bias_color = "#4CAF50" if overall_bias > 0 else "#F44336"

    # 显示总体偏差指标
    st.markdown("### 总体预测偏差分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        display_metric_card(
            "总体偏差率",
            f"{abs(overall_bias_pct):.2f}%",
            color="primary",
            icon="📊",
            description=f"整体{bias_type}程度"
        )

    with col2:
        display_metric_card(
            "实际销量",
            format_number(total_actual),
            suffix=" 箱",
            color="success",
            icon="📦",
            description="筛选范围内实际销量"
        )

    with col3:
        display_metric_card(
            "预测销量",
            format_number(total_forecast),
            suffix=" 箱",
            color="info",
            icon="📋",
            description="筛选范围内预测销量"
        )

    # 显示偏差仪表盘
    st.markdown("### 预测偏差程度")

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=100 + overall_bias_pct,
        delta={"reference": 100, "valueformat": ".1f"},
        title={"text": "预测准确度"},
        gauge={
            "axis": {"range": [0, 200], "tickwidth": 1, "tickcolor": "darkblue"},
            "bar": {"color": "rgba(0,0,0,0)"},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 80], "color": "#F44336"},  # 严重高估
                {"range": [80, 95], "color": "#FF9800"},  # 中度高估
                {"range": [95, 105], "color": "#4CAF50"},  # 准确
                {"range": [105, 120], "color": "#FF9800"},  # 中度低估
                {"range": [120, 200], "color": "#F44336"},  # 严重低估
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": 100 + overall_bias_pct
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # 添加箭头指示当前值
    fig.add_annotation(
        x=0.5,
        y=0.25,
        text="当前值",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )

    st.plotly_chart(fig, use_container_width=True)

    # 图表解释
    st.markdown(f"""
    <div class="chart-explanation">
        <strong>图表解释：</strong> 当前预测整体{bias_type}了{abs(overall_bias_pct):.2f}%，处于
        {"准确" if abs(overall_bias_pct) <= 5 else "中度" + bias_type if abs(overall_bias_pct) <= 20 else "严重" + bias_type}范围内。

        <strong>解释说明：</strong>
        <ul>
            <li>值为100表示预测完全准确</li>
            <li>小于100表示预测高估（预测值大于实际值）</li>
            <li>大于100表示预测低估（预测值小于实际值）</li>
            <li>合理范围为95-105（±5%偏差）</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 显示高估和低估统计
    st.markdown("### 产品预测偏差统计")

    over_count = len(bias_patterns['over_forecast_products'])
    under_count = len(bias_patterns['under_forecast_products'])
    total_products = over_count + under_count + len(
        filtered_data['merged_monthly'].groupby('产品代码').filter(
            lambda x: abs((x['求和项:数量（箱）'].sum() - x['预计销售量'].sum()) / x['求和项:数量（箱）'].sum() if x[
                                                                                                                   '求和项:数量（箱）'].sum() > 0 else 0) <= 0.1
        )['产品代码'].unique()
    )

    # 创建偏差分布饼图
    fig = go.Figure(data=[go.Pie(
        labels=['准确预测', '预测高估', '预测低估'],
        values=[total_products - over_count - under_count, over_count, under_count],
        hole=.3,
        marker_colors=['#4CAF50', '#F44336', '#2196F3']
    )])

    fig.update_layout(
        title="产品预测偏差分布",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 图表解释
    over_pct = over_count / total_products * 100 if total_products > 0 else 0
    under_pct = under_count / total_products * 100 if total_products > 0 else 0
    accurate_pct = 100 - over_pct - under_pct

    st.markdown(f"""
    <div class="chart-explanation">
        <strong>图表解释：</strong> 在总共{total_products}个产品中，有{over_count}个产品({over_pct:.1f}%)预测高估，
        {under_count}个产品({under_pct:.1f}%)预测低估，剩余{accurate_pct:.1f}%的产品预测准确（偏差在±10%以内）。

        <strong>行动建议：</strong>
        {"应着重关注预测高估的产品，降低预测量，避免库存积压。" if over_pct > under_pct + 10 else ""}
        {"应着重关注预测低估的产品，提高预测量，避免断货风险。" if under_pct > over_pct + 10 else ""}
        {"预测偏差分布相对均衡，建议保持当前预测方法，重点关注偏差较大的个别产品。" if abs(over_pct - under_pct) <= 10 else ""}
    </div>
    """, unsafe_allow_html=True)

    # 月度偏差趋势
    st.markdown("### 月度偏差趋势")

    monthly_bias = bias_patterns['monthly_bias'].copy()
    if not monthly_bias.empty:
        monthly_bias['偏差率'] = monthly_bias['偏差率'] * 100  # 转换为百分比

        # 创建图表
        fig = go.Figure()

        # 添加偏差率柱状图
        fig.add_trace(go.Bar(
            x=monthly_bias['所属年月'],
            y=monthly_bias['偏差率'],
            marker_color=monthly_bias['偏差率'].apply(
                lambda x: '#4CAF50' if x > 0 else '#F44336'  # 绿色为低估，红色为高估
            ),
            name='预测偏差率',
            text=monthly_bias['偏差率'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))

        # 添加零线
        fig.add_shape(
            type="line",
            x0=monthly_bias['所属年月'].min(),
            x1=monthly_bias['所属年月'].max(),
            y0=0,
            y1=0,
            line=dict(color="black", width=1)
        )

        # 更新布局
        fig.update_layout(
            title="月度预测偏差趋势",
            xaxis_title="月份",
            yaxis_title="偏差率 (%)",
            yaxis=dict(
                tickformat='.1f',
                zeroline=False
            ),
            plot_bgcolor='white',
            height=400,
            margin=dict(t=50, b=50)
        )

        # 自定义悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>偏差率: %{y:.1f}%<br>%{text}<extra></extra>'
        )

        # 添加说明标签
        fig.add_annotation(
            x=0.02,
            y=0.95,
            xref="paper",
            yref="paper",
            text="正值表示预测低估，负值表示预测高估",
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#1f3867",
            borderwidth=1,
            borderpad=4,
            font=dict(size=10)
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        last_bias = monthly_bias.iloc[-1]['偏差率'] if len(monthly_bias) > 0 else 0
        last_bias_type = "低估" if last_bias > 0 else "高估"

        # 偏差趋势分析
        if len(monthly_bias) > 1:
            # 计算偏差率变化率
            bias_changes = monthly_bias['偏差率'].diff().dropna()
            trend = "增加" if bias_changes.mean() > 0 else "减少"
            consistency = "持续" if all(b > 0 for b in bias_changes) or all(b < 0 for b in bias_changes) else "波动"
        else:
            trend = "未知"
            consistency = "未知"

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 最近一个月预测{last_bias_type}了{abs(last_bias):.1f}%。
            从趋势来看，预测偏差呈{consistency}{trend}趋势。

            <strong>行动建议：</strong>
            {f"注意调整预测方法，降低{last_bias_type}趋势。" if abs(last_bias) > 10 else "继续保持当前预测准确度。"}
            {f"建议分析{last_bias_type}原因，可能与季节性因素有关。" if abs(last_bias) > 15 else ""}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成月度偏差趋势图。")


def display_region_bias(bias_patterns, filtered_data):
    """显示区域预测偏差分析"""
    # 准备数据
    region_bias = bias_patterns['region_bias'].copy()
    region_bias['偏差率'] = region_bias['偏差率'] * 100  # 转换为百分比

    # 计算各区域实际与预测销量
    region_sales = filtered_data['merged_monthly'].groupby('所属区域').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 显示标题
    st.markdown("### 区域预测偏差分析")

    # 区域预测偏差条形图
    if not region_bias.empty:
        # 按偏差率绝对值降序排序
        region_bias = region_bias.sort_values('偏差率', key=abs, ascending=False)

        fig = go.Figure()

        # 添加条形图
        fig.add_trace(go.Bar(
            y=region_bias['所属区域'],
            x=region_bias['偏差率'],
            orientation='h',
            marker_color=region_bias['偏差率'].apply(
                lambda x: '#4CAF50' if x > 0 else '#F44336'  # 绿色为低估，红色为高估
            ),
            text=region_bias['偏差率'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ))

        # 添加零线
        fig.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=-0.5,
            y1=len(region_bias) - 0.5,
            line=dict(color="black", width=1)
        )

        # 更新布局
        fig.update_layout(
            title="区域预测偏差率",
            xaxis_title="偏差率 (%)",
            yaxis_title="区域",
            plot_bgcolor='white',
            height=400
        )

        # 添加图例说明
        fig.add_annotation(
            x=-region_bias['偏差率'].abs().max() * 0.9,
            y=len(region_bias) - 0.5,
            text="高估",
            showarrow=False,
            font=dict(color="#F44336")
        )

        fig.add_annotation(
            x=region_bias['偏差率'].abs().max() * 0.9,
            y=len(region_bias) - 0.5,
            text="低估",
            showarrow=False,
            font=dict(color="#4CAF50")
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>偏差率: %{x:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        most_underestimated = region_bias[region_bias['偏差率'] > 0].iloc[0] if len(
            region_bias[region_bias['偏差率'] > 0]) > 0 else None
        most_overestimated = region_bias[region_bias['偏差率'] < 0].iloc[0] if len(
            region_bias[region_bias['偏差率'] < 0]) > 0 else None

        explanation = "<strong>图表解释：</strong> 此图展示了各区域的预测偏差率，正值表示预测低估（实际销量高于预测），负值表示预测高估（实际销量低于预测）。"

        if most_underestimated is not None:
            explanation += f" {most_underestimated['所属区域']}区域预测最为低估，偏差率为{most_underestimated['偏差率']:.1f}%。"

        if most_overestimated is not None:
            explanation += f" {most_overestimated['所属区域']}区域预测最为高估，偏差率为{most_overestimated['偏差率']:.1f}%。"

        st.markdown(f"""
        <div class="chart-explanation">
            {explanation}

            <strong>行动建议：</strong>
            {f"建议提高{most_underestimated['所属区域']}区域的预测量约{abs(most_underestimated['偏差率']):.0f}%，以避免断货风险。" if most_underestimated is not None and abs(most_underestimated['偏差率']) > 10 else ""}
            {f"建议降低{most_overestimated['所属区域']}区域的预测量约{abs(most_overestimated['偏差率']):.0f}%，以避免库存积压。" if most_overestimated is not None and abs(most_overestimated['偏差率']) > 10 else ""}
            {"区域预测偏差相对较小，当前预测准确度良好。" if (most_underestimated is None or abs(most_underestimated['偏差率']) <= 10) and (most_overestimated is None or abs(most_overestimated['偏差率']) <= 10) else ""}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域预测偏差图。")

    # 区域实际vs预测销量对比
    st.markdown("### 区域实际vs预测销量对比")

    if not region_sales.empty:
        fig = go.Figure()

        # 添加实际销量柱
        fig.add_trace(go.Bar(
            y=region_sales['所属区域'],
            x=region_sales['求和项:数量（箱）'],
            name='实际销量',
            marker_color='royalblue',
            orientation='h',
            offsetgroup=0
        ))

        # 添加预测销量柱
        fig.add_trace(go.Bar(
            y=region_sales['所属区域'],
            x=region_sales['预计销售量'],
            name='预测销量',
            marker_color='lightcoral',
            orientation='h',
            offsetgroup=1
        ))

        # 计算偏差百分比
        region_sales['偏差百分比'] = (region_sales['求和项:数量（箱）'] - region_sales['预计销售量']) / region_sales[
            '求和项:数量（箱）'] * 100

        # 更新布局
        fig.update_layout(
            title="区域实际vs预测销量对比",
            xaxis_title="销量 (箱)",
            yaxis_title="区域",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            barmode='group',
            plot_bgcolor='white',
            height=400
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>%{name}: %{x:,} 箱<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        largest_region = region_sales.loc[region_sales['求和项:数量（箱）'].idxmax()]
        largest_diff = region_sales.loc[region_sales['偏差百分比'].abs().idxmax()]

        diff_type = "低估" if largest_diff['偏差百分比'] > 0 else "高估"

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> {largest_region['所属区域']}区域的销量最大，为{format_number(largest_region['求和项:数量（箱）'])}箱。
            {largest_diff['所属区域']}区域的预测偏差最大，偏差率为{abs(largest_diff['偏差百分比']):.1f}%，属于预测{diff_type}。

            <strong>行动建议：</strong>
            针对销量大且偏差大的区域，应优先调整预测方法，特别是对于{largest_diff['所属区域']}区域，建议
            {f"提高预测量约{abs(largest_diff['偏差百分比']):.0f}%" if diff_type == "低估" else f"降低预测量约{abs(largest_diff['偏差百分比']):.0f}%"}。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域销量对比图。")

    # 区域月度偏差热力图
    st.markdown("### 区域月度偏差热力图")

    # 按区域和月份计算偏差率
    region_monthly = filtered_data['merged_monthly'].groupby(['所属区域', '所属年月']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    region_monthly['偏差率'] = (region_monthly['求和项:数量（箱）'] - region_monthly['预计销售量']) / region_monthly[
        '求和项:数量（箱）'] * 100

    if not region_monthly.empty:
        # 数据透视表
        pivot_data = region_monthly.pivot_table(
            values='偏差率',
            index='所属区域',
            columns='所属年月',
            aggfunc='mean'
        ).round(1)

        # 创建热力图
        fig = px.imshow(
            pivot_data,
            text_auto='.1f',
            color_continuous_scale=[
                [0, "rgb(178, 34, 34)"],  # 深红色 - 严重高估
                [0.4, "rgb(255, 127, 80)"],  # 浅红色 - 轻微高估
                [0.5, "rgb(255, 255, 255)"],  # 白色 - 准确
                [0.6, "rgb(144, 238, 144)"],  # 浅绿色 - 轻微低估
                [1, "rgb(0, 100, 0)"]  # 深绿色 - 严重低估
            ],
            labels=dict(x="月份", y="区域", color="偏差率 (%)"),
            color_continuous_midpoint=0,
            aspect="auto"
        )

        # 更新布局
        fig.update_layout(
            title="区域月度预测偏差热力图",
            xaxis_title="月份",
            yaxis_title="区域",
            coloraxis_colorbar=dict(
                title="偏差率 (%)",
                tickvals=[-50, -25, 0, 25, 50],
                ticktext=["高估 50%", "高估 25%", "准确", "低估 25%", "低估 50%"]
            ),
            plot_bgcolor='white',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        st.markdown("""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 此热力图展示了各区域在不同月份的预测偏差率，颜色表示偏差程度和方向：
            <ul>
                <li>红色表示预测高估（预测值大于实际值）</li>
                <li>绿色表示预测低估（预测值小于实际值）</li>
                <li>白色表示预测准确（偏差接近0）</li>
            </ul>

            通过观察热力图，可以识别区域预测偏差的季节性模式和变化趋势，以便有针对性地改进预测方法。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成区域月度偏差热力图。")


def display_product_bias(bias_patterns, product_info):
    """显示产品预测偏差分析"""
    # 准备数据
    over_forecast = bias_patterns['over_forecast_products'].copy()
    under_forecast = bias_patterns['under_forecast_products'].copy()

    # 添加产品名称
    if not over_forecast.empty:
        over_forecast['偏差率'] = over_forecast['偏差率'] * 100  # 转换为百分比
        over_forecast['产品名称'] = over_forecast['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

    if not under_forecast.empty:
        under_forecast['偏差率'] = under_forecast['偏差率'] * 100  # 转换为百分比
        under_forecast['产品名称'] = under_forecast['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

    # 显示标题
    st.markdown("### 产品预测偏差分析")

    # 创建偏差散点图
    st.markdown("#### 预测偏差散点图")

    # 合并过度预测和预测不足的产品
    all_products = pd.concat([over_forecast, under_forecast])

    if not all_products.empty:
        # 按偏差率绝对值排序
        all_products = all_products.sort_values('偏差率', key=abs, ascending=False)

        # 创建散点图
        fig = px.scatter(
            all_products,
            y='产品名称',
            x='偏差率',
            size='求和项:数量（箱）',
            color='偏差率',
            hover_name='产品代码',
            color_continuous_scale=[
                [0, "rgb(178, 34, 34)"],  # 深红色 - 严重高估
                [0.4, "rgb(255, 127, 80)"],  # 浅红色 - 轻微高估
                [0.5, "rgb(255, 255, 255)"],  # 白色 - 准确
                [0.6, "rgb(144, 238, 144)"],  # 浅绿色 - 轻微低估
                [1, "rgb(0, 100, 0)"]  # 深绿色 - 严重低估
            ],
            color_continuous_midpoint=0,
            size_max=40
        )

        # 更新布局
        fig.update_layout(
            title="产品预测偏差散点图（点大小表示销量）",
            xaxis_title="偏差率 (%)",
            yaxis_title="产品",
            coloraxis_colorbar=dict(
                title="偏差率 (%)",
                tickvals=[-50, -25, 0, 25, 50],
                ticktext=["高估 50%", "高估 25%", "准确", "低估 25%", "低估 50%"]
            ),
            plot_bgcolor='white',
            height=max(600, len(all_products) * 20)
        )

        # 添加零线
        fig.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=-0.5,
            y1=len(all_products) - 0.5,
            line=dict(color="black", width=1)
        )

        # 添加高估和低估区域标记
        fig.add_annotation(
            x=-25,
            y=len(all_products) * 0.9,
            text="高估区域",
            showarrow=False,
            font=dict(color="#F44336")
        )

        fig.add_annotation(
            x=25,
            y=len(all_products) * 0.9,
            text="低估区域",
            showarrow=False,
            font=dict(color="#4CAF50")
        )

        # 更新悬停提示
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>偏差率: %{x:.1f}%<br>销量: %{marker.size:,} 箱<br>预测量: %{customdata:,} 箱<extra></extra>',
            customdata=all_products['预计销售量']
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        st.markdown("""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 此散点图展示了产品的预测偏差情况，点的位置表示偏差率，大小表示销量，颜色表示偏差程度：
            <ul>
                <li>红色区域表示预测高估（预测值大于实际值）</li>
                <li>绿色区域表示预测低估（预测值小于实际值）</li>
            </ul>

            应优先关注销量大（点大）且偏差率高（远离中心线）的产品，这些产品的预测误差对整体业绩影响最大。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成产品预测偏差散点图。")

    # 高估产品列表
    st.markdown("#### 预测高估产品（Top 10）")

    if not over_forecast.empty:
        # 按偏差率绝对值排序，取前10个
        top_over = over_forecast.nlargest(10, '偏差率', key=abs)

        # 调整列名和格式
        display_df = top_over.copy()
        display_df['偏差率'] = display_df['偏差率'].round(1).astype(str) + '%'
        display_df['实际销量'] = display_df['求和项:数量（箱）']
        display_df['预测销量'] = display_df['预计销售量']

        # 显示表格
        st.dataframe(
            display_df[['产品名称', '实际销量', '预测销量', '偏差率']],
            use_container_width=True,
            column_config={
                "产品名称": st.column_config.Column("产品名称", width="medium"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "偏差率": st.column_config.TextColumn("偏差率")
            },
            hide_index=True
        )

        # 添加建议
        st.markdown(f"""
        <div class="alert alert-danger">
            <strong>行动建议：</strong> 以上产品预测量明显高于实际销量，建议降低这些产品的预测量约{abs(top_over['偏差率'].mean()):.0f}%，
            尤其是{top_over.iloc[0]['产品名称']}，其预测高估了{abs(top_over.iloc[0]['偏差率']):.1f}%。这些高估可能导致库存积压，增加库存成本。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("没有发现明显预测高估的产品。")

    # 低估产品列表
    st.markdown("#### 预测低估产品（Top 10）")

    if not under_forecast.empty:
        # 按偏差率排序，取前10个
        top_under = under_forecast.nlargest(10, '偏差率')

        # 调整列名和格式
        display_df = top_under.copy()
        display_df['偏差率'] = display_df['偏差率'].round(1).astype(str) + '%'
        display_df['实际销量'] = display_df['求和项:数量（箱）']
        display_df['预测销量'] = display_df['预计销售量']

        # 显示表格
        st.dataframe(
            display_df[['产品名称', '实际销量', '预测销量', '偏差率']],
            use_container_width=True,
            column_config={
                "产品名称": st.column_config.Column("产品名称", width="medium"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "偏差率": st.column_config.TextColumn("偏差率")
            },
            hide_index=True
        )

        # 添加建议
        st.markdown(f"""
        <div class="alert alert-warning">
            <strong>行动建议：</strong> 以上产品预测量明显低于实际销量，建议提高这些产品的预测量约{top_under['偏差率'].mean():.0f}%，
            尤其是{top_under.iloc[0]['产品名称']}，其预测低估了{top_under.iloc[0]['偏差率']:.1f}%。这些低估可能导致缺货风险，影响销售和客户满意度。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("没有发现明显预测低估的产品。")

    # 准确预测产品
    st.markdown("#### 预测最准确的产品")

    # 合并过度预测和预测不足的产品
    if not all_products.empty:
        # 按偏差率绝对值排序，取前10个最准确的
        accurate_products = all_products.nsmallest(10, '偏差率', key=abs)

        # 调整列名和格式
        display_df = accurate_products.copy()
        display_df['偏差率'] = display_df['偏差率'].round(1).astype(str) + '%'
        display_df['实际销量'] = display_df['求和项:数量（箱）']
        display_df['预测销量'] = display_df['预计销售量']

        # 显示表格
        st.dataframe(
            display_df[['产品名称', '实际销量', '预测销量', '偏差率']],
            use_container_width=True,
            column_config={
                "产品名称": st.column_config.Column("产品名称", width="medium"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "偏差率": st.column_config.TextColumn("偏差率")
            },
            hide_index=True
        )

        # 添加建议
        st.markdown(f"""
        <div class="alert alert-success">
            <strong>最佳实践：</strong> 以上产品预测最为准确，偏差率控制在±{accurate_products['偏差率'].abs().max():.1f}%以内。
            建议分析这些产品预测准确的原因和方法，将最佳实践推广到其他产品的预测中。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("没有足够的数据来分析预测准确的产品。")


def display_monthly_bias(bias_patterns, filtered_data):
    """显示月度预测偏差分析"""
    # 准备数据
    monthly_bias = bias_patterns['monthly_bias'].copy()
    monthly_bias['偏差率'] = monthly_bias['偏差率'] * 100  # 转换为百分比

    # 按月份汇总实际与预测销量
    monthly_sales = filtered_data['merged_monthly'].groupby('所属年月').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算月度差异
    monthly_sales['差异'] = monthly_sales['求和项:数量（箱）'] - monthly_sales['预计销售量']
    monthly_sales['偏差率'] = monthly_sales['差异'] / monthly_sales['求和项:数量（箱）'] * 100

    # 显示标题
    st.markdown("### 月度预测偏差分析")

    # 月度偏差趋势图
    if not monthly_bias.empty:
        fig = go.Figure()

        # 添加偏差率柱状图
        fig.add_trace(go.Bar(
            x=monthly_bias['所属年月'],
            y=monthly_bias['偏差率'],
            marker_color=monthly_bias['偏差率'].apply(
                lambda x: '#4CAF50' if x > 0 else '#F44336'  # 绿色为低估，红色为高估
            ),
            name='预测偏差率',
            text=monthly_bias['偏差率'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))

        # 添加零线
        fig.add_shape(
            type="line",
            x0=monthly_bias['所属年月'].min(),
            x1=monthly_bias['所属年月'].max(),
            y0=0,
            y1=0,
            line=dict(color="black", width=1)
        )

        # 更新布局
        fig.update_layout(
            title="月度预测偏差趋势",
            xaxis_title="月份",
            yaxis_title="偏差率 (%)",
            yaxis=dict(
                tickformat='.1f',
                zeroline=False
            ),
            plot_bgcolor='white',
            height=400,
            margin=dict(t=50, b=50)
        )

        # 自定义悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>偏差率: %{y:.1f}%<br>%{text}<extra></extra>'
        )

        # 添加说明标签
        fig.add_annotation(
            x=0.02,
            y=0.95,
            xref="paper",
            yref="paper",
            text="正值表示预测低估，负值表示预测高估",
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#1f3867",
            borderwidth=1,
            borderpad=4,
            font=dict(size=10)
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        if len(monthly_bias) > 1:
            # 计算偏差趋势
            recent_biases = monthly_bias.tail(3)
            trend = "上升" if recent_biases['偏差率'].iloc[-1] > recent_biases['偏差率'].iloc[0] else "下降"

            # 季节性分析
            month_numbers = [int(m.split('-')[1]) for m in monthly_bias['所属年月']]
            quarters = [(n - 1) // 3 + 1 for n in month_numbers]

            # 计算季度平均偏差
            quarterly_bias = {}
            for i, q in enumerate(quarters):
                if q not in quarterly_bias:
                    quarterly_bias[q] = []
                quarterly_bias[q].append(monthly_bias['偏差率'].iloc[i])

            quarterly_avg = {q: sum(biases) / len(biases) for q, biases in quarterly_bias.items()}

            # 找出偏差最大的季度
            if quarterly_avg:
                max_q = max(quarterly_avg.items(), key=lambda x: abs(x[1]))
                q_bias_type = "低估" if max_q[1] > 0 else "高估"

                q_names = {1: "一季度(1-3月)", 2: "二季度(4-6月)", 3: "三季度(7-9月)", 4: "四季度(10-12月)"}
                q_name = q_names.get(max_q[0], f"Q{max_q[0]}")
            else:
                max_q = (0, 0)
                q_bias_type = "未知"
                q_name = "未知"

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 近期预测偏差率呈{trend}趋势。根据历史数据分析，
                {q_name}的预测偏差最大，平均偏差率为{abs(max_q[1]):.1f}%，属于预测{q_bias_type}。

                <strong>季节性因素：</strong> 根据月度偏差趋势，可以发现预测准确性存在明显的季节性波动，
                特别是在{q_name}期间，预测偏差率较大。这可能与季节性销售波动、促销活动或市场因素有关。

                <strong>行动建议：</strong>
                {f"针对{q_name}的预测方法需要调整，建议在该季度{'提高' if q_bias_type == '低估' else '降低'}预测量约{abs(max_q[1]):.0f}%。" if abs(max_q[1]) > 10 else ""}
                {"建议分析季节性因素对预测准确性的影响，针对性地优化各季度的预测方法。" if len(quarterly_avg) >= 2 else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成月度偏差趋势图。")

    # 月度实际vs预测销量对比
    st.markdown("### 月度实际vs预测销量对比")

    if not monthly_sales.empty:
        fig = go.Figure()

        # 添加实际销量线
        fig.add_trace(go.Scatter(
            x=monthly_sales['所属年月'],
            y=monthly_sales['求和项:数量（箱）'],
            mode='lines+markers',
            name='实际销量',
            line=dict(color='royalblue', width=3),
            marker=dict(size=8)
        ))

        # 添加预测销量线
        fig.add_trace(go.Scatter(
            x=monthly_sales['所属年月'],
            y=monthly_sales['预计销售量'],
            mode='lines+markers',
            name='预测销量',
            line=dict(color='lightcoral', width=3, dash='dot'),
            marker=dict(size=8)
        ))

        # 更新布局
        fig.update_layout(
            title="月度实际vs预测销量趋势",
            xaxis_title="月份",
            yaxis_title="销量 (箱)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=400
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:,} 箱<br>偏差率: %{customdata:.1f}%<extra></extra>',
            customdata=monthly_sales['偏差率']
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        if len(monthly_sales) > 1:
            # 分析销量趋势
            sales_trend = "上升" if monthly_sales['求和项:数量（箱）'].iloc[-1] > monthly_sales['求和项:数量（箱）'].iloc[
                -2] else "下降"
            forecast_trend = "上升" if monthly_sales['预计销售量'].iloc[-1] > monthly_sales['预计销售量'].iloc[
                -2] else "下降"

            # 找出预测最准确和最不准确的月份
            monthly_sales['偏差绝对值'] = monthly_sales['偏差率'].abs()
            best_month = monthly_sales.loc[monthly_sales['偏差绝对值'].idxmin()]
            worst_month = monthly_sales.loc[monthly_sales['偏差绝对值'].idxmax()]

            worst_type = "低估" if worst_month['偏差率'] > 0 else "高估"

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>图表解释：</strong> 最近一个月的销量呈{sales_trend}趋势，而预测销量呈{forecast_trend}趋势。
                {best_month['所属年月']}月的预测最为准确，偏差率仅为{abs(best_month['偏差率']):.1f}%；
                {worst_month['所属年月']}月的预测最不准确，偏差率高达{abs(worst_month['偏差率']):.1f}%，属于预测{worst_type}。

                <strong>行动建议：</strong>
                分析{worst_month['所属年月']}月预测偏差较大的原因，可能是由于特殊事件、市场变化或季节性因素导致。
                建议参考{best_month['所属年月']}月的预测方法，提高整体预测准确性。
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成月度销量对比图。")

    # 月度偏差分布直方图
    st.markdown("### 月度偏差分布")

    if not monthly_sales.empty:
        fig = go.Figure()

        # 添加偏差率直方图
        fig.add_trace(go.Histogram(
            x=monthly_sales['偏差率'],
            nbinsx=10,
            marker_color='#1f3867',
            opacity=0.7
        ))

        # 添加零线
        fig.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=0,
            y1=len(monthly_sales),
            line=dict(color="red", width=2, dash="dash")
        )

        # 更新布局
        fig.update_layout(
            title="月度偏差率分布",
            xaxis_title="偏差率 (%)",
            yaxis_title="月份数量",
            plot_bgcolor='white',
            height=400
        )

        # 添加说明标签
        fig.add_annotation(
            x=-20,
            y=len(monthly_sales) * 0.8,
            text="高估",
            showarrow=False,
            font=dict(color="#F44336")
        )

        fig.add_annotation(
            x=20,
            y=len(monthly_sales) * 0.8,
            text="低估",
            showarrow=False,
            font=dict(color="#4CAF50")
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解释
        over_months = len(monthly_sales[monthly_sales['偏差率'] < 0])
        under_months = len(monthly_sales[monthly_sales['偏差率'] > 0])
        accurate_months = len(monthly_sales[abs(monthly_sales['偏差率']) <= 5])

        bias_tendency = "高估" if over_months > under_months else "低估" if under_months > over_months else "平衡"

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 在分析的{len(monthly_sales)}个月中，有{over_months}个月预测高估，
            {under_months}个月预测低估，{accurate_months}个月预测较为准确（偏差率在±5%以内）。

            整体预测趋势显示为{bias_tendency}倾向，这可能反映了预测方法中的系统性偏差。

            <strong>行动建议：</strong>
            {f"调整预测方法，降低{'高估' if bias_tendency == '高估' else '低估'}倾向，使预测更加平衡。" if bias_tendency != '平衡' else ""}
            {"提高预测准确性，争取将更多月份的偏差率控制在±5%以内。" if accurate_months < len(monthly_sales) / 2 else ""}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来生成月度偏差分布图。")


def display_sku_analysis_page(processed_data, product_info, filter_months, filter_regions, detail='all'):
    """显示重点SKU分析页面"""
    # 显示标题和面包屑
    st.markdown('<h1 class="main-header">重点SKU分析</h1>', unsafe_allow_html=True)

    # 更新导航路径
    st.session_state['breadcrumb'] = [('总览', 'overview'), ('重点SKU分析', 'sku_analysis')]
    display_breadcrumb()

    # 筛选数据
    filtered_data = {
        'merged_monthly': filter_data(processed_data['merged_monthly'], filter_months, filter_regions),
    }

    # 计算当前筛选条件下的重点SKU
    filtered_top_skus = calculate_top_skus(filtered_data['merged_monthly'], by_region=False)
    filtered_regional_top_skus = calculate_top_skus(filtered_data['merged_monthly'], by_region=True)

    # 区域标签页
    region_tabs = ["全国"] + (filter_regions if filter_regions else [])

    # 创建选项卡集
    st.markdown('<div class="region-tabs">', unsafe_allow_html=True)
    for i, tab in enumerate(region_tabs):
        active_class = " active" if (detail == 'national' and tab == '全国') or (detail == tab) else ""
        st.markdown(f"""
        <div class="region-tab{active_class}" id="tab_{i}" onclick="select_tab('{tab}')">
            {tab}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 添加JavaScript处理选项卡点击
    st.markdown("""
    <script>
    function select_tab(tab) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: { view: 'sku_analysis', detail: tab },
            dataType: 'json'
        }, '*');
    }
    </script>
    """, unsafe_allow_html=True)

    # 显示选定区域的数据
    if detail == 'national' or detail == 'all':
        display_national_sku_analysis(filtered_top_skus, product_info, processed_data['product_growth'])
    elif detail in filter_regions:
        if detail in filtered_regional_top_skus:
            display_region_specific_sku_analysis(detail, filtered_regional_top_skus[detail], product_info,
                                                 processed_data['product_growth'])
        else:
            st.warning(f"没有足够的数据来分析{detail}区域的重点SKU。")
    else:
        display_national_sku_analysis(filtered_top_skus, product_info, processed_data['product_growth'])


def display_national_sku_analysis(top_skus, product_info, product_growth):
    """显示全国重点SKU分析"""
    if top_skus.empty:
        st.warning("没有足够的数据来分析重点SKU。")
        return

    # 添加产品名称
    top_skus['产品名称'] = top_skus['产品代码'].apply(
        lambda x: format_product_code(x, product_info, include_name=True)
    )

    # 计算统计数据
    accuracy_stats = {
        '高准确率(>80%)': len(top_skus[top_skus['数量准确率'] > 0.8]),
        '中等准确率(60-80%)': len(top_skus[(top_skus['数量准确率'] > 0.6) & (top_skus['数量准确率'] <= 0.8)]),
        '低准确率(<60%)': len(top_skus[top_skus['数量准确率'] <= 0.6])
    }

    # 显示标题和摘要
    st.markdown("### 全国重点SKU分析")

    st.markdown(f"""
    <div class="alert alert-info">
        <strong>摘要：</strong> 本分析基于销售量累计占比80%的重点SKU，共计{len(top_skus)}个产品。
        准确率分布：{accuracy_stats['高准确率(>80%)']}个高准确率产品、
        {accuracy_stats['中等准确率(60-80%)']}个中等准确率产品、
        {accuracy_stats['低准确率(<60%)']}个低准确率产品。
    </div>
    """, unsafe_allow_html=True)

    # 显示图表
    col1, col2 = st.columns([2, 1])

    with col1:
        # 创建条形图
        fig_bar = go.Figure()

        # 转换百分比
        top_skus['数量准确率_pct'] = top_skus['数量准确率'] * 100

        # 添加条形图
        fig_bar.add_trace(go.Bar(
            y=top_skus['产品名称'],
            x=top_skus['求和项:数量（箱）'],
            name='销售量',
            orientation='h',
            marker=dict(
                color=top_skus['数量准确率_pct'],
                colorscale=[
                    [0, "red"],
                    [0.6, "yellow"],
                    [0.8, "green"],
                    [1, "blue"]
                ],
                colorbar=dict(
                    title="准确率(%)"
                )
            )
        ))

        # 更新布局
        fig_bar.update_layout(
            title="重点SKU销量及准确率",
            xaxis_title="销售量 (箱)",
            yaxis_title="产品",
            yaxis=dict(autorange="reversed"),  # 从上到下按销量排序
            plot_bgcolor='white',
            height=max(500, len(top_skus) * 30)
        )

        # 添加准确率标签
        for i, row in enumerate(top_skus.itertuples()):
            fig_bar.add_annotation(
                y=row.产品名称,
                x=row.求和项: 数量（箱） *1.02,
            text = f"{row.数量准确率_pct:.0f}%",
            showarrow = False,
            font = dict(
                color="black" if row.数量准确率 > 0.6 else "red",
                size=10
            )
            )

            # 悬停信息
            fig_bar.update_traces(
                hovertemplate='<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata:.2f}%<extra></extra>',
                customdata=top_skus['累计占比']
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # 显示准确率分布
            st.markdown("#### 准确率分布")

            # 创建准确率分布饼图
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(accuracy_stats.keys()),
                values=list(accuracy_stats.values()),
                hole=.3,
                marker_colors=['#4CAF50', '#FFC107', '#F44336']
            )])

            fig_pie.update_layout(
                title="重点SKU准确率分布",
                height=300
            )

            st.plotly_chart(fig_pie, use_container_width=True)

            # 显示准确率最低的产品
            if len(top_skus) > 0:
                lowest_accuracy = top_skus.loc[top_skus['数量准确率'].idxmin()]
                st.markdown(f"""
            <div class="alert alert-warning">
                <strong>准确率最低产品:</strong> {lowest_accuracy['产品名称']}<br>
                准确率: {lowest_accuracy['数量准确率'] * 100:.1f}%<br>
                销量: {format_number(lowest_accuracy['求和项:数量（箱）'])}箱
            </div>
            """, unsafe_allow_html=True)

                # 添加行动建议
                if accuracy_stats['低准确率(<60%)'] > 0:
                    st.markdown(f"""
                <div class="alert alert-danger">
                    <strong>行动建议:</strong><br>
                    发现{accuracy_stats['低准确率(<60%)']}个重点SKU准确率低于60%，建议优先改进这些产品的预测方法。
                </div>
                """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                <div class="alert alert-success">
                    <strong>行动建议:</strong><br>
                    重点SKU预测准确率整体良好，建议保持当前预测方法。
                </div>
                """, unsafe_allow_html=True)

        # SKU准确率与销量关系散点图
        st.markdown("### 重点SKU准确率与销量关系")

        # 创建散点图
        fig_scatter = px.scatter(
            top_skus,
            x='求和项:数量（箱）',
            y='数量准确率_pct',
            size='求和项:数量（箱）',
            color='数量准确率_pct',
            hover_name='产品名称',
            text='产品名称',
            color_continuous_scale=[
                [0, "red"],
                [0.6, "yellow"],
                [0.8, "green"],
                [1, "blue"]
            ],
            size_max=40,
            range_color=[0, 100]
        )

        # 更新布局
        fig_scatter.update_layout(
            title="SKU销量与预测准确率关系",
            xaxis_title="销量 (箱)",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=500
        )

        # 添加准确率基准线
        fig_scatter.add_shape(
            type="line",
            x0=top_skus['求和项:数量（箱）'].min(),
            x1=top_skus['求和项:数量（箱）'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="准确率基准"
        )

        # 更改悬停信息
        fig_scatter.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>销量: %{x:,.0f}箱<br>准确率: %{y:.1f}%<br>累计占比: %{customdata:.2f}%<extra></extra>',
            customdata=top_skus['累计占比']
        )

        # 显示文本
        fig_scatter.update_traces(
            textposition='top center',
            textfont=dict(size=10)
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        # 添加图表解释
        st.markdown("""
    <div class="chart-explanation">
        <strong>图表解释：</strong> 此散点图展示了重点SKU的销量与预测准确率的关系。点的大小表示销量，颜色表示准确率（颜色越深表示准确率越高）。
        通过观察散点分布，可以识别销量大但准确率低的产品，这些产品应优先改进预测方法。
    </div>
    """, unsafe_allow_html=True)

        # 合并产品增长率数据
        st.markdown("### 重点SKU销量增长趋势与备货建议")

        # 从产品增长数据中提取重点SKU的数据
        if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
            growth_data = product_growth['latest_growth']

            # 筛选重点SKU
            sku_growth = growth_data[growth_data['产品代码'].isin(top_skus['产品代码'])]

            if not sku_growth.empty:
                # 添加产品名称
                sku_growth['产品名称'] = sku_growth['产品代码'].apply(
                    lambda x: format_product_code(x, product_info, include_name=True)
                )

                # 按增长率降序排序
                sku_growth = sku_growth.sort_values('销量增长率', ascending=False)

                # 创建条形图
                fig_growth = go.Figure()

                # 添加条形图
                fig_growth.add_trace(go.Bar(
                    y=sku_growth['产品名称'],
                    x=sku_growth['销量增长率'],
                    orientation='h',
                    marker_color=sku_growth['销量增长率'].apply(
                        lambda x: '#4CAF50' if x > 10 else '#FFC107' if x > 0 else '#FF9800' if x > -10 else '#F44336'
                    ),
                    text=sku_growth.apply(
                        lambda row: f"{row['销量增长率']:.1f}% {row['建议图标']}",
                        axis=1
                    ),
                    textposition='auto'
                ))

                # 添加零线
                fig_growth.add_shape(
                    type="line",
                    x0=0,
                    x1=0,
                    y0=-0.5,
                    y1=len(sku_growth) - 0.5,
                    line=dict(color="black", width=1)
                )

                # 更新布局
                fig_growth.update_layout(
                    title="重点SKU销量增长率与备货建议",
                    xaxis_title="增长率 (%)",
                    yaxis_title="产品",
                    plot_bgcolor='white',
                    height=max(400, len(sku_growth) * 30)
                )

                # 悬停信息
                fig_growth.update_traces(
                    hovertemplate='<b>%{y}</b><br>增长率: %{x:.1f}%<br>备货建议: %{customdata[0]}<br>调整比例: %{customdata[1]}%<extra></extra>',
                    customdata=sku_growth[['备货建议', '调整比例']]
                )

                st.plotly_chart(fig_growth, use_container_width=True)

                # 添加图表解释
                growth_counts = {
                    '强劲增长': len(sku_growth[sku_growth['趋势'] == '强劲增长']),
                    '增长': len(sku_growth[sku_growth['趋势'] == '增长']),
                    '轻微下降': len(sku_growth[sku_growth['趋势'] == '轻微下降']),
                    '显著下降': len(sku_growth[sku_growth['趋势'] == '显著下降'])
                }

                explanation = f"""
            <strong>图表解释：</strong> 在{len(sku_growth)}个重点SKU中，
            {growth_counts['强劲增长']}个产品呈强劲增长（>10%），
            {growth_counts['增长']}个产品呈增长（0-10%），
            {growth_counts['轻微下降']}个产品呈轻微下降（-10%-0），
            {growth_counts['显著下降']}个产品呈显著下降（<-10%）。
            """

                if growth_counts['强劲增长'] > 0:
                    top_growth = sku_growth[sku_growth['趋势'] == '强劲增长'].iloc[0]
                    explanation += f"<br><strong>增长最快产品：</strong> {top_growth['产品名称']}，增长率达{top_growth['销量增长率']:.1f}%，建议{top_growth['备货建议']}，调整比例{top_growth['调整比例']}%。"

                if growth_counts['显著下降'] > 0:
                    top_decline = sku_growth[sku_growth['趋势'] == '显著下降'].iloc[0]
                    explanation += f"<br><strong>下降最快产品：</strong> {top_decline['产品名称']}，下降率达{abs(top_decline['销量增长率']):.1f}%，建议{top_decline['备货建议']}，调整比例{top_decline['调整比例']}%。"

                # 综合建议
                if growth_counts['强劲增长'] + growth_counts['增长'] > growth_counts['轻微下降'] + growth_counts[
                    '显著下降']:
                    explanation += "<br><strong>综合建议：</strong> 总体呈增长趋势，建议适当增加库存，重点关注强劲增长的产品。"
                elif growth_counts['强劲增长'] + growth_counts['增长'] < growth_counts['轻微下降'] + growth_counts[
                    '显著下降']:
                    explanation += "<br><strong>综合建议：</strong> 总体呈下降趋势，建议控制库存，降低显著下降产品的备货量。"
                else:
                    explanation += "<br><strong>综合建议：</strong> 总体趋势平稳，建议保持当前库存水平，针对个别产品进行调整。"

                st.markdown(f"""
            <div class="chart-explanation">
                {explanation}
            </div>
            """, unsafe_allow_html=True)
            else:
                st.warning("没有足够的数据来分析重点SKU的增长趋势。")
        else:
            st.warning("没有足够的历史数据来计算增长率。")

        # 显示重点SKU详细数据表格
        st.markdown("### 重点SKU详细数据")

        # 准备表格数据
        display_df = top_skus.copy()
        display_df['准确率'] = (display_df['数量准确率'] * 100).round(1).astype(str) + '%'
        display_df['实际销量'] = display_df['求和项:数量（箱）']
        display_df['预测销量'] = display_df['预计销售量']
        display_df['累计占比'] = display_df['累计占比'].round(2).astype(str) + '%'

        # 显示表格
        st.dataframe(
            display_df[['产品名称', '实际销量', '预测销量', '准确率', '累计占比']],
            use_container_width=True,
            column_config={
                "产品名称": st.column_config.Column("产品名称", width="medium"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "准确率": st.column_config.TextColumn("准确率"),
                "累计占比": st.column_config.TextColumn("累计占比")
            },
            hide_index=True
        )

    def display_region_specific_sku_analysis(region, region_top_skus, product_info, product_growth):
        """显示特定区域的重点SKU分析"""
        if region_top_skus.empty:
            st.warning(f"没有足够的数据来分析{region}区域的重点SKU。")
            return

        # 添加产品名称
        region_top_skus['产品名称'] = region_top_skus['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 计算统计数据
        accuracy_stats = {
            '高准确率(>80%)': len(region_top_skus[region_top_skus['数量准确率'] > 0.8]),
            '中等准确率(60-80%)': len(
                region_top_skus[(region_top_skus['数量准确率'] > 0.6) & (region_top_skus['数量准确率'] <= 0.8)]),
            '低准确率(<60%)': len(region_top_skus[region_top_skus['数量准确率'] <= 0.6])
        }

        # 显示标题和摘要
        st.markdown(f"### {region}区域重点SKU分析")

        st.markdown(f"""
    <div class="alert alert-info">
        <strong>摘要：</strong> 本分析基于{region}区域销售量累计占比80%的重点SKU，共计{len(region_top_skus)}个产品。
        准确率分布：{accuracy_stats['高准确率(>80%)']}个高准确率产品、
        {accuracy_stats['中等准确率(60-80%)']}个中等准确率产品、
        {accuracy_stats['低准确率(<60%)']}个低准确率产品。
    </div>
    """, unsafe_allow_html=True)

        # 显示图表
        col1, col2 = st.columns([2, 1])

        with col1:
            # 创建条形图
            fig_bar = go.Figure()

            # 转换百分比
            region_top_skus['数量准确率_pct'] = region_top_skus['数量准确率'] * 100

            # 添加条形图
            fig_bar.add_trace(go.Bar(
                y=region_top_skus['产品名称'],
                x=region_top_skus['求和项:数量（箱）'],
                name='销售量',
                orientation='h',
                marker=dict(
                    color=region_top_skus['数量准确率_pct'],
                    colorscale=[
                        [0, "red"],
                        [0.6, "yellow"],
                        [0.8, "green"],
                        [1, "blue"]
                    ],
                    colorbar=dict(
                        title="准确率(%)"
                    )
                )
            ))

            # 更新布局
            fig_bar.update_layout(
                title=f"{region}区域重点SKU销量及准确率",
                xaxis_title="销售量 (箱)",
                yaxis_title="产品",
                yaxis=dict(autorange="reversed"),  # 从上到下按销量排序
                plot_bgcolor='white',
                height=max(500, len(region_top_skus) * 30)
            )

            # 添加准确率标签
            for i, row in enumerate(region_top_skus.itertuples()):
                fig_bar.add_annotation(
                    y=row.产品名称,
                    x=row.求和项: 数量（箱） *1.02,
                text = f"{row.数量准确率_pct:.0f}%",
                showarrow = False,
                font = dict(
                    color="black" if row.数量准确率 > 0.6 else "red",
                    size=10
                )
                )

                # 悬停信息
                fig_bar.update_traces(
                    hovertemplate='<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata:.2f}%<extra></extra>',
                    customdata=region_top_skus['累计占比']
                )

                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                # 显示准确率分布
                st.markdown("#### 准确率分布")

                # 创建准确率分布饼图
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(accuracy_stats.keys()),
                    values=list(accuracy_stats.values()),
                    hole=.3,
                    marker_colors=['#4CAF50', '#FFC107', '#F44336']
                )])

                fig_pie.update_layout(
                    title=f"{region}区域重点SKU准确率分布",
                    height=300
                )

                st.plotly_chart(fig_pie, use_container_width=True)

                # 显示准确率最低的产品
                if len(region_top_skus) > 0:
                    lowest_accuracy = region_top_skus.loc[region_top_skus['数量准确率'].idxmin()]
                    st.markdown(f"""
            <div class="alert alert-warning">
                <strong>准确率最低产品:</strong> {lowest_accuracy['产品名称']}<br>
                准确率: {lowest_accuracy['数量准确率'] * 100:.1f}%<br>
                销量: {format_number(lowest_accuracy['求和项:数量（箱）'])}箱
            </div>
            """, unsafe_allow_html=True)

                    # 添加行动建议
                    if accuracy_stats['低准确率(<60%)'] > 0:
                        st.markdown(f"""
                <div class="alert alert-danger">
                    <strong>{region}区域行动建议:</strong><br>
                    发现{accuracy_stats['低准确率(<60%)']}个重点SKU准确率低于60%，建议{region}区域优先改进这些产品的预测方法。
                </div>
                """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                <div class="alert alert-success">
                    <strong>{region}区域行动建议:</strong><br>
                    {region}区域重点SKU预测准确率整体良好，建议保持当前预测方法。
                </div>
                """, unsafe_allow_html=True)

            # 区域vs全国SKU对比
            st.markdown(f"### {region}区域与全国重点SKU对比")

            # 获取全国重点SKU
            national_top_skus = calculate_top_skus(processed_data['merged_monthly'], by_region=False)

            if not national_top_skus.empty:
                # 获取区域和全国的SKU代码
                region_skus = set(region_top_skus['产品代码'])
                national_skus = set(national_top_skus['产品代码'])

                # 计算共有和特有SKU
                common_skus = region_skus.intersection(national_skus)
                region_unique_skus = region_skus - national_skus
                national_unique_skus = national_skus - region_skus

                # 创建饼图
                fig_comparison = go.Figure()

                # 添加区域特有SKU占比
                fig_comparison.add_trace(go.Pie(
                    labels=['区域与全国共有SKU', '区域特有SKU', '全国重点但区域非重点SKU'],
                    values=[len(common_skus), len(region_unique_skus), len(national_unique_skus)],
                    hole=.3,
                    marker_colors=['#4CAF50', '#2196F3', '#F44336']
                ))

                fig_comparison.update_layout(
                    title=f"{region}区域与全国重点SKU对比",
                    plot_bgcolor='white',
                    height=400
                )

                # 获取常见的SKU名称用于悬停信息
                common_sku_names = [format_product_code(code, product_info, include_name=True) for code in common_skus]
                region_unique_sku_names = [format_product_code(code, product_info, include_name=True) for code in
                                           region_unique_skus]
                national_unique_sku_names = [format_product_code(code, product_info, include_name=True) for code in
                                             national_unique_skus]

                # 准备悬停文本
                hover_texts = [
                    f"共有SKU ({len(common_skus)}个):<br>" +
                    '<br>- '.join([''] + common_sku_names[:10] + (['...更多'] if len(common_sku_names) > 10 else [])),

                    f"区域特有SKU ({len(region_unique_skus)}个):<br>" +
                    '<br>- '.join([''] + region_unique_sku_names[:10] + (
                        ['...更多'] if len(region_unique_sku_names) > 10 else [])),

                    f"全国重点非区域SKU ({len(national_unique_skus)}个):<br>" +
                    '<br>- '.join([''] + national_unique_sku_names[:10] + (
                        ['...更多'] if len(national_unique_sku_names) > 10 else []))
                ]

                # 更新悬停信息
                fig_comparison.update_traces(
                    hovertemplate='%{label}: %{percent}<br><br>%{customdata}<extra></extra>',
                    customdata=hover_texts
                )

                st.plotly_chart(fig_comparison, use_container_width=True)

                # 添加图表解释
                st.markdown(f"""
        <div class="chart-explanation">
            <strong>图表解释：</strong> 此饼图展示了{region}区域重点SKU与全国重点SKU的对比情况。
            <ul>
                <li>绿色部分：同时是{region}区域和全国重点的产品（{len(common_skus)}个）</li>
<li>蓝色部分：只在{region}区域是重点的产品（{len(region_unique_skus)}个）</li>
                <li>红色部分：在全国范围内是重点但在{region}区域不是重点的产品（{len(national_unique_skus)}个）</li>
            </ul>
            
            <strong>分析建议：</strong>
            <ul>
                <li>区域特有SKU（蓝色）表明{region}区域有独特的市场偏好，这些产品应针对{region}区域特别关注</li>
                <li>全国重点但区域非重点SKU（红色）可能在{region}区域存在开发空间，可考虑针对性营销</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 显示详细数据表格
        st.markdown("#### 区域特有SKU列表")
        if len(region_unique_skus) > 0:
            # 获取区域特有SKU的详细数据
            region_unique_data = region_top_skus[region_top_skus['产品代码'].isin(region_unique_skus)]

            # 准备表格数据
            display_df = region_unique_data.copy()
            display_df['准确率'] = (display_df['数量准确率'] * 100).round(1).astype(str) + '%'
            display_df['实际销量'] = display_df['求和项:数量（箱）']
            display_df['预测销量'] = display_df['预计销售量']

            # 显示表格
            st.dataframe(
                display_df[['产品名称', '实际销量', '预测销量', '准确率']],
                use_container_width=True,
                column_config={
                    "产品名称": st.column_config.Column("产品名称", width="medium"),
                    "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                    "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                    "准确率": st.column_config.TextColumn("准确率")
                },
                hide_index=True
            )
        else:
            st.info(f"{region}区域没有特有的重点SKU。")
    else:
        st.warning("没有足够的数据来进行区域与全国的SKU对比分析。")

    # 从产品增长数据中提取该区域重点SKU的数据
    st.markdown(f"### {region}区域重点SKU销量增长趋势")

    if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
        growth_data = product_growth['latest_growth']

        # 筛选重点SKU
        sku_growth = growth_data[growth_data['产品代码'].isin(region_top_skus['产品代码'])]

        if not sku_growth.empty:
            # 添加产品名称
            sku_growth['产品名称'] = sku_growth['产品代码'].apply(
                lambda x: format_product_code(x, product_info, include_name=True)
            )

            # 按增长率降序排序
            sku_growth = sku_growth.sort_values('销量增长率', ascending=False)

            # 创建条形图
            fig_growth = go.Figure()

            # 添加条形图
            fig_growth.add_trace(go.Bar(
                y=sku_growth['产品名称'],
                x=sku_growth['销量增长率'],
                orientation='h',
                marker_color=sku_growth['销量增长率'].apply(
                    lambda x: '#4CAF50' if x > 10 else '#FFC107' if x > 0 else '#FF9800' if x > -10 else '#F44336'
                ),
                text=sku_growth.apply(
                    lambda row: f"{row['销量增长率']:.1f}% {row['建议图标']}",
                    axis=1
                ),
                textposition='auto'
            ))

            # 添加零线
            fig_growth.add_shape(
                type="line",
                x0=0,
                x1=0,
                y0=-0.5,
                y1=len(sku_growth) - 0.5,
                line=dict(color="black", width=1)
            )

            # 更新布局
            fig_growth.update_layout(
                title=f"{region}区域重点SKU销量增长率与备货建议",
                xaxis_title="增长率 (%)",
                yaxis_title="产品",
                plot_bgcolor='white',
                height=max(400, len(sku_growth) * 30)
            )

            # 悬停信息
            fig_growth.update_traces(
                hovertemplate='<b>%{y}</b><br>增长率: %{x:.1f}%<br>备货建议: %{customdata[0]}<br>调整比例: %{customdata[1]}%<extra></extra>',
                customdata=sku_growth[['备货建议', '调整比例']]
            )

            st.plotly_chart(fig_growth, use_container_width=True)

            # 添加区域特有产品的增长建议
            region_unique_growth = sku_growth[sku_growth['产品代码'].isin(region_unique_skus)]

            if not region_unique_growth.empty:
                st.markdown(f"""
                <div class="alert alert-info">
                    <strong>区域特有产品增长分析：</strong><br>
                    在{region}区域特有的重点SKU中，
                    {len(region_unique_growth[region_unique_growth['销量增长率'] > 10])}个产品呈强劲增长，
                    {len(region_unique_growth[region_unique_growth['销量增长率'] < -10])}个产品呈显著下降。
                    
                    建议重点关注以下产品：<br>
                    {region_unique_growth.iloc[0]['产品名称']} - 增长率{region_unique_growth.iloc[0]['销量增长率']:.1f}%，建议{region_unique_growth.iloc[0]['备货建议']}
                    {f"<br>{region_unique_growth.iloc[-1]['产品名称']} - 增长率{region_unique_growth.iloc[-1]['销量增长率']:.1f}%，建议{region_unique_growth.iloc[-1]['备货建议']}" if len(region_unique_growth) > 1 else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"没有足够的数据来分析{region}区域重点SKU的增长趋势。")
    else:
        st.warning("没有足够的历史数据来计算增长率。")

    # 显示详细数据表格
    st.markdown(f"### {region}区域重点SKU详细数据")

    # 准备表格数据
    display_df = region_top_skus.copy()
    display_df['准确率'] = (display_df['数量准确率'] * 100).round(1).astype(str) + '%'
    display_df['实际销量'] = display_df['求和项:数量（箱）']
    display_df['预测销量'] = display_df['预计销售量']
    display_df['累计占比'] = display_df['累计占比'].round(2).astype(str) + '%'

    # 显示表格
    st.dataframe(
        display_df[['产品名称', '实际销量', '预测销量', '准确率', '累计占比']],
        use_container_width=True,
        column_config={
            "产品名称": st.column_config.Column("产品名称", width="medium"),
            "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
            "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
            "准确率": st.column_config.TextColumn("准确率"),
            "累计占比": st.column_config.TextColumn("累计占比")
        },
        hide_index=True
    )

def display_trend_analysis_page(processed_data, product_info, filter_months, filter_regions):
    """显示趋势分析页面"""
    # 显示标题和面包屑
    st.markdown('<h1 class="main-header">预测准确率趋势分析</h1>', unsafe_allow_html=True)

    # 更新导航路径
    st.session_state['breadcrumb'] = [('总览', 'overview'), ('趋势分析', 'trend')]
    display_breadcrumb()

    # 筛选数据
    filtered_data = {
        'merged_monthly': filter_data(processed_data['merged_monthly'], filter_months, filter_regions),
    }

    # 检查数据是否足够
    if filtered_data['merged_monthly'].empty or len(filtered_data['merged_monthly']['所属年月'].unique()) < 2:
        st.warning("没有足够的数据来进行趋势分析。至少需要两个月的数据才能分析趋势。")
        return

    # 计算趋势数据
    accuracy_trends = calculate_accuracy_trends(filtered_data['merged_monthly'])

    # 创建选项卡
    tabs = st.tabs(["整体趋势", "区域趋势", "销售员趋势", "产品趋势"])

    with tabs[0]:  # 整体趋势
        display_overall_accuracy_trend(accuracy_trends)

    with tabs[1]:  # 区域趋势
        display_region_accuracy_trend(accuracy_trends, filter_regions)

    with tabs[2]:  # 销售员趋势
        display_salesperson_accuracy_trend(processed_data, filter_months, filter_regions)

    with tabs[3]:  # 产品趋势
        display_product_accuracy_trend(accuracy_trends, product_info, filter_months)

def display_overall_accuracy_trend(accuracy_trends):
    """显示整体准确率趋势分析"""
    # 准备数据
    monthly_trend = accuracy_trends['monthly'].copy()
    monthly_trend['数量准确率'] = monthly_trend['数量准确率'] * 100  # 转换为百分比

    # 显示标题
    st.markdown("### 全国预测准确率月度趋势")

    if not monthly_trend.empty:
        # 创建趋势图
        fig = go.Figure()

        # 添加准确率线
        fig.add_trace(go.Scatter(
            x=monthly_trend['所属年月'],
            y=monthly_trend['数量准确率'],
            mode='lines+markers',
            name='准确率',
            line=dict(color='#1f3867', width=3),
            marker=dict(size=8)
        ))

        # 添加趋势线 (移动平均)
        window_size = min(3, len(monthly_trend))
        if window_size > 1:
            monthly_trend['移动平均'] = monthly_trend['数量准确率'].rolling(window=window_size, min_periods=1).mean()

            fig.add_trace(go.Scatter(
                x=monthly_trend['所属年月'],
                y=monthly_trend['移动平均'],
                mode='lines',
                name=f'{window_size}月移动平均',
                line=dict(color='#FF9800', width=2, dash='dash')
            ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=monthly_trend['所属年月'].min(),
            x1=monthly_trend['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            title="全国月度预测准确率趋势",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=500,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 趋势分析
        if len(monthly_trend) >= 3:
            # 计算趋势
            recent_months = monthly_trend.tail(3)
            trend_direction = "上升" if recent_months['数量准确率'].iloc[-1] > recent_months['数量准确率'].iloc[0] else "下降"
            trend_magnitude = abs(recent_months['数量准确率'].iloc[-1] - recent_months['数量准确率'].iloc[0])

            # 识别季节性模式
            month_numbers = [int(m.split('-')[1]) for m in monthly_trend['所属年月']]
            quarters = [(n-1)//3 + 1 for n in month_numbers]

            # 计算季度平均准确率
            quarterly_accuracy = {}
            for i, q in enumerate(quarters):
                if q not in quarterly_accuracy:
                    quarterly_accuracy[q] = []
                quarterly_accuracy[q].append(monthly_trend['数量准确率'].iloc[i])

            quarterly_avg = {q: sum(accuracies)/len(accuracies) for q, accuracies in quarterly_accuracy.items()}

            # 找出准确率最高和最低的季度
            if quarterly_avg:
                best_q = max(quarterly_avg.items(), key=lambda x: x[1])
                worst_q = min(quarterly_avg.items(), key=lambda x: x[1])

                q_names = {1: "一季度(1-3月)", 2: "二季度(4-6月)", 3: "三季度(7-9月)", 4: "四季度(10-12月)"}
                best_q_name = q_names.get(best_q[0], f"Q{best_q[0]}")
                worst_q_name = q_names.get(worst_q[0], f"Q{worst_q[0]}")
            else:
                best_q = (0, 0)
                worst_q = (0, 0)
                best_q_name = "未知"
                worst_q_name = "未知"

            # 准确率突变点
            change_points = []
            for i in range(1, len(monthly_trend)):
                change = abs(monthly_trend['数量准确率'].iloc[i] - monthly_trend['数量准确率'].iloc[i-1])
                if change > 15:  # 超过15个百分点的变化视为突变
                    change_points.append((
                        monthly_trend['所属年月'].iloc[i],
                        monthly_trend['数量准确率'].iloc[i-1],
                        monthly_trend['数量准确率'].iloc[i],
                        change
                    ))

            change_text = ""
            if change_points:
                change_text = "发现准确率突变点：<br>"
                for cp in change_points:
                    direction = "上升" if cp[2] > cp[1] else "下降"
                    change_text += f"· {cp[0]}月准确率{direction}了{cp[3]:.1f}个百分点<br>"

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>趋势分析：</strong><br>
                · 近3个月准确率呈{trend_direction}趋势，变化幅度为{trend_magnitude:.1f}个百分点<br>
                · {best_q_name}的平均准确率最高，为{best_q[1]:.1f}%<br>
                · {worst_q_name}的平均准确率最低，为{worst_q[1]:.1f}%<br>
                {change_text}
                
                <strong>季节性分析：</strong><br>
                预测准确率存在明显的季节性波动，这可能与以下因素有关：<br>
                · 销售旺季/淡季的预测难度差异<br>
                · 节假日或促销活动对销售预测的影响<br>
                · 新品上市或产品生命周期变化
                
                <strong>行动建议：</strong><br>
                {'针对准确率下降趋势，建议检查近期预测方法的变化，及时调整预测模型。' if trend_direction == '下降' and trend_magnitude > 5 else ''}
                {'针对准确率的季节性波动，建议对' + worst_q_name + '的预测方法进行优化，增加季节性因素的考量。' if abs(best_q[1] - worst_q[1]) > 10 else ''}
                {'当前预测准确率整体表现良好，建议保持现有预测方法。' if trend_direction == '上升' or trend_magnitude <= 5 else ''}
            </div>
            """, unsafe_allow_html=True)

        # 显示具体月份准确率数据
        st.markdown("#### 月度准确率详细数据")

        # 准备表格数据
        display_df = monthly_trend.copy()
        display_df['准确率'] = display_df['数量准确率'].round(1).astype(str) + '%'
        display_df['实际销量'] = display_df['求和项:数量（箱）']
        display_df['预测销量'] = display_df['预计销售量']
        display_df['差异'] = display_df['实际销量'] - display_df['预测销量']

        # 格式化日期列
        display_df['月份'] = display_df['所属年月']

        # 显示表格
        st.dataframe(
            display_df[['月份', '实际销量', '预测销量', '差异', '准确率']],
            use_container_width=True,
            column_config={
                "月份": st.column_config.Column("月份", width="small"),
                "实际销量": st.column_config.NumberColumn("实际销量", format="%d"),
                "预测销量": st.column_config.NumberColumn("预测销量", format="%d"),
                "差异": st.column_config.NumberColumn("差异", format="%d"),
                "准确率": st.column_config.TextColumn("准确率")
            },
            hide_index=True
        )
    else:
        st.warning("没有足够的数据来分析整体准确率趋势。")

    # 显示年度准确率对比（如果有多年数据）
    if not monthly_trend.empty:
        # 提取年份
        monthly_trend['年份'] = monthly_trend['所属年月'].apply(lambda x: x.split('-')[0])
        monthly_trend['月'] = monthly_trend['所属年月'].apply(lambda x: x.split('-')[1])

        # 检查是否有多个年份的数据
        years = monthly_trend['年份'].unique()

        if len(years) > 1:
            st.markdown("### 年度准确率对比")

            # 创建年度对比图
            fig = go.Figure()

            # 为每年添加一条线
            for year in years:
                year_data = monthly_trend[monthly_trend['年份'] == year]

                fig.add_trace(go.Scatter(
                    x=year_data['月'],
                    y=year_data['数量准确率'],
                    mode='lines+markers',
                    name=f'{year}年',
                    marker=dict(size=8)
                ))

            # 添加准确率目标线
            fig.add_shape(
                type="line",
                x0=monthly_trend['月'].min(),
                x1=monthly_trend['月'].max(),
                y0=80,
                y1=80,
                line=dict(color="green", width=1, dash="dash"),
                name="良好准确率基准"
            )

            # 更新布局
            fig.update_layout(
                title="年度准确率月度对比",
                xaxis_title="月份",
                yaxis_title="准确率 (%)",
                yaxis=dict(range=[0, 100]),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='white',
                height=500
            )

            # 添加悬停信息
            fig.update_traces(
                hovertemplate='<b>%{x}月</b><br>%{name}: %{y:.1f}%<extra></extra>'
            )

            st.plotly_chart(fig, use_container_width=True)

            # 计算年度平均准确率
            year_avg = monthly_trend.groupby('年份')['数量准确率'].mean().reset_index()

            # 创建年度平均准确率条形图
            fig_avg = go.Figure()

            fig_avg.add_trace(go.Bar(
                x=year_avg['年份'],
                y=year_avg['数量准确率'],
                marker_color='#1f3867',
                text=year_avg['数量准确率'].apply(lambda x: f"{x:.1f}%"),
                textposition='auto'
            ))

            # 更新布局
            fig_avg.update_layout(
                title="年度平均准确率对比",
                xaxis_title="年份",
                yaxis_title="平均准确率 (%)",
                yaxis=dict(range=[0, 100]),
                plot_bgcolor='white',
                height=400
            )

            st.plotly_chart(fig_avg, use_container_width=True)

            # 图表解释
            improvement = year_avg['数量准确率'].iloc[-1] - year_avg['数量准确率'].iloc[0]
            improved = improvement > 0

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>年度对比分析：</strong><br>
                从{years[0]}年到{years[-1]}年，预测准确率{'提高' if improved else '下降'}了{abs(improvement):.1f}个百分点。
                
                <strong>季节性模式：</strong><br>
                {'各年的准确率变化趋势存在相似的季节性模式，表明销售的季节性特征对预测准确率有显著影响。' if len(monthly_trend) > 6 else '数据量不足，无法确定明确的季节性模式。'}
                
                <strong>改进建议：</strong><br>
                {'持续优化预测方法，保持准确率提升趋势。' if improved else '分析准确率下降原因，调整预测模型和方法。'}
                {'建议进一步优化季节性因素在预测模型中的权重，提高旺季和淡季的预测准确性。' if len(monthly_trend) > 6 else ''}
            </div>
            """, unsafe_allow_html=True)

def display_region_accuracy_trend(accuracy_trends, filter_regions):
    """显示区域准确率趋势分析"""
    # 准备数据
    region_monthly = accuracy_trends['region_monthly'].copy()
    region_monthly['数量准确率'] = region_monthly['数量准确率'] * 100  # 转换为百分比

    # 筛选选定区域
    if filter_regions and len(filter_regions) > 0:
        region_monthly = region_monthly[region_monthly['所属区域'].isin(filter_regions)]

    # 显示标题
    st.markdown("### 区域预测准确率月度趋势")

    if not region_monthly.empty:
        # 创建区域趋势图
        fig = go.Figure()

        # 为每个区域添加一条线
        for region in region_monthly['所属区域'].unique():
            region_data = region_monthly[region_monthly['所属区域'] == region]

            fig.add_trace(go.Scatter(
                x=region_data['所属年月'],
                y=region_data['数量准确率'],
                mode='lines+markers',
                name=f'{region}区域',
                marker=dict(size=8)
            ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=region_monthly['所属年月'].min(),
            x1=region_monthly['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            title="区域月度准确率趋势",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=500,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 区域月度准确率热力图
        st.markdown("### 区域月度准确率热力图")

        # 数据透视表
        pivot_data = region_monthly.pivot_table(
            values='数量准确率',
            index='所属区域',
            columns='所属年月',
            aggfunc='mean'
        ).round(1)

        # 创建热力图
        fig_heatmap = px.imshow(
            pivot_data,
            text_auto='.1f',
            color_continuous_scale=[
                [0, "rgb(220, 53, 69)"],      # 红色 - 低准确率
                [0.5, "rgb(255, 193, 7)"],    # 黄色 - 中等准确率
                [0.8, "rgb(40, 167, 69)"],    # 绿色 - 高准确率
                [1, "rgb(0, 123, 255)"]       # 蓝色 - 最高准确率
            ],
            labels=dict(x="月份", y="区域", color="准确率 (%)"),
            range_color=[0, 100],
            aspect="auto"
        )

        # 更新布局
        fig_heatmap.update_layout(
            title="区域月度准确率热力图",
            xaxis_title="月份",
            yaxis_title="区域",
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=400
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # 区域季节性分析
        st.markdown("### 区域准确率季节性分析")

        # 添加季度信息
        region_monthly['月'] = region_monthly['所属年月'].apply(lambda x: int(x.split('-')[1]))
        region_monthly['季度'] = region_monthly['月'].apply(lambda x: (x-1)//3 + 1)

        # 按区域和季度汇总
        quarterly_data = region_monthly.groupby(['所属区域', '季度'])['数量准确率'].mean().reset_index()

        # 数据透视表
        pivot_quarterly = quarterly_data.pivot_table(
            values='数量准确率',
            index='所属区域',
            columns='季度',
            aggfunc='mean'
        ).round(1)

        # 创建热力图
        fig_quarterly = px.imshow(
            pivot_quarterly,
            text_auto='.1f',
            color_continuous_scale=[
                [0, "rgb(220, 53, 69)"],      # 红色 - 低准确率
                [0.5, "rgb(255, 193, 7)"],    # 黄色 - 中等准确率
                [0.8, "rgb(40, 167, 69)"],    # 绿色 - 高准确率
                [1, "rgb(0, 123, 255)"]       # 蓝色 - 最高准确率
            ],
            labels=dict(x="季度", y="区域", color="准确率 (%)"),
            range_color=[0, 100],
            aspect="auto"
        )

        # 更新布局
        fig_quarterly.update_layout(
            title="区域季度准确率热力图",
            xaxis_title="季度",
            yaxis_title="区域",
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=400
        )

        # 替换x轴标签
        fig_quarterly.update_xaxes(
            ticktext=["Q1(1-3月)", "Q2(4-6月)", "Q3(7-9月)", "Q4(10-12月)"],
            tickvals=[1, 2, 3, 4]
        )

        st.plotly_chart(fig_quarterly, use_container_width=True)

        # 区域特征分析
        st.markdown("### 区域准确率特征分析")

        # 计算各区域的统计特征
        region_stats = region_monthly.groupby('所属区域')['数量准确率'].agg([
            ('平均值', 'mean'),
            ('最大值', 'max'),
            ('最小值', 'min'),
            ('标准差', 'std')
        ]).reset_index()

        # 按平均准确率排序
        region_stats = region_stats.sort_values('平均值', ascending=False)

        # 创建特征雷达图
        # 为每个区域创建一个雷达图
        fig_radar = go.Figure()

        for _, row in region_stats.iterrows():
            region = row['所属区域']

            # 获取该区域在每个季度的准确率
            region_quarterly = quarterly_data[quarterly_data['所属区域'] == region]

            # 准备雷达图数据
            radar_data = []
            q_names = ["Q1(1-3月)", "Q2(4-6月)", "Q3(7-9月)", "Q4(10-12月)"]

            for q in range(1, 5):
                q_acc = region_quarterly[region_quarterly['季度'] == q]['数量准确率'].mean() if q in region_quarterly['季度'].values else 0
                radar_data.append(q_acc)

            # 添加雷达线
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_data,
                theta=q_names,
                fill='toself',
                name=region
            ))

        # 更新布局
        fig_radar.update_layout(
            title="区域季度准确率雷达图",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        # 图表解释
        best_region = region_stats.iloc[0]['所属区域']
        worst_region = region_stats.iloc[-1]['所属区域']
        most_stable = region_stats.loc[region_stats['标准差'].idxmin()]['所属区域']

        # 找出每个区域最好和最差的季度
        best_quarters = {}
        worst_quarters = {}

        for region in region_monthly['所属区域'].unique():
            region_q_data = quarterly_data[quarterly_data['所属区域'] == region]
            if not region_q_data.empty:
                best_q = region_q_data.loc[region_q_data['数量准确率'].idxmax()]
                worst_q = region_q_data.loc[region_q_data['数量准确率'].idxmin()]

                best_quarters[region] = (int(best_q['季度']), best_q['数量准确率'])
                worst_quarters[region] = (int(worst_q['季度']), worst_q['数量准确率'])

        # 准备区域特征说明
        region_features = ""
        for region in region_monthly['所属区域'].unique():
            if region in best_quarters and region in worst_quarters:
                best_q = best_quarters[region]
                worst_q = worst_quarters[region]

                q_names = {1: "Q1(1-3月)", 2: "Q2(4-6月)", 3: "Q3(7-9月)", 4: "Q4(10-12月)"}

                region_features += f"· {region}区域：平均准确率{region_stats[region_stats['所属区域'] == region]['平均值'].values[0]:.1f}%，"
                region_features += f"最佳季度为{q_names[best_q[0]]}({best_q[1]:.1f}%)，"
                region_features += f"最差季度为{q_names[worst_q[0]]}({worst_q[1]:.1f}%)<br>"

        st.markdown(f"""
        <div class="chart-explanation">
            <strong>区域分析：</strong><br>
            · {best_region}区域的平均准确率最高，为{region_stats[region_stats['所属区域'] == best_region]['平均值'].values[0]:.1f}%<br>
            · {worst_region}区域的平均准确率最低，为{region_stats[region_stats['所属区域'] == worst_region]['平均值'].values[0]:.1f}%<br>
            · {most_stable}区域的准确率最稳定，波动最小<br>
            
            <strong>季节性特征：</strong><br>
            {region_features}
            
            <strong>改进建议：</strong><br>
            1. 分享{best_region}区域的预测最佳实践，提升其他区域的预测能力<br>
            2. 重点改进{worst_region}区域的预测方法，特别是在其最差季度的预测<br>
            3. 研究各区域准确率的季节性波动，针对性地调整不同季度的预测策略
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来分析区域准确率趋势。")

def display_salesperson_accuracy_trend(processed_data, filter_months, filter_regions):
    """显示销售员准确率趋势分析"""
    # 筛选数据
    filtered_data = {
        'merged_by_salesperson': filter_data(processed_data['merged_by_salesperson'], filter_months, filter_regions),
    }

    # 检查数据是否足够
    if filtered_data['merged_by_salesperson'].empty:
        st.warning("没有足够的数据来分析销售员准确率趋势。")
        return

    # 按月份和销售员统计
    monthly_salesperson = filtered_data['merged_by_salesperson'].groupby(['所属年月', '销售员']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算准确率
    monthly_salesperson['数量准确率'] = monthly_salesperson.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']) * 100,
        axis=1
    )

    # 显示标题
    st.markdown("### 销售员预测准确率趋势")

    if not monthly_salesperson.empty:
        # 计算每个销售员的平均准确率
        salesperson_avg = monthly_salesperson.groupby('销售员')['数量准确率'].mean().reset_index()

        # 筛选前10名销售员
        top_salespersons = salesperson_avg.nlargest(10, '数量准确率')['销售员'].tolist()

        # 创建销售员准确率趋势图
        fig = go.Figure()

        # 为每个销售员添加一条线
        for salesperson in top_salespersons:
            salesperson_data = monthly_salesperson[monthly_salesperson['销售员'] == salesperson]

            fig.add_trace(go.Scatter(
                x=salesperson_data['所属年月'],
                y=salesperson_data['数量准确率'],
                mode='lines+markers',
                name=salesperson,
                marker=dict(size=6)
            ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=monthly_salesperson['所属年月'].min(),
            x1=monthly_salesperson['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            title="销售员月度准确率趋势（Top 10）",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=500,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 销售员准确率热力图
        st.markdown("### 销售员月度准确率热力图")

        # 数据透视表 - 选择每个销售员最新3个月
        all_months = sorted(monthly_salesperson['所属年月'].unique())
        recent_months = all_months[-min(3, len(all_months)):]

        recent_data = monthly_salesperson[monthly_salesperson['所属年月'].isin(recent_months)]

        # 按准确率排序，选择前15名销售员
        top_15_salespersons = salesperson_avg.nlargest(15, '数量准确率')['销售员'].tolist()
        recent_data = recent_data[recent_data['销售员'].isin(top_15_salespersons)]

        if not recent_data.empty:
            pivot_data = recent_data.pivot_table(
                values='数量准确率',
                index='销售员',
                columns='所属年月',
                aggfunc='mean'
            ).round(1)

            # 创建热力图
            fig_heatmap = px.imshow(
                pivot_data,
                text_auto='.1f',
                color_continuous_scale=[
                    [0, "rgb(220, 53, 69)"],      # 红色 - 低准确率
                    [0.5, "rgb(255, 193, 7)"],    # 黄色 - 中等准确率
                    [0.8, "rgb(40, 167, 69)"],    # 绿色 - 高准确率
                    [1, "rgb(0, 123, 255)"]       # 蓝色 - 最高准确率
                ],
                labels=dict(x="月份", y="销售员", color="准确率 (%)"),
                range_color=[0, 100],
                aspect="auto"
            )

            # 更新布局
            fig_heatmap.update_layout(
                title="销售员最近月度准确率热力图（Top 15）",
                xaxis_title="月份",
                yaxis_title="销售员",
                coloraxis_colorbar=dict(title="准确率 (%)"),
                plot_bgcolor='white',
                height=max(400, len(top_15_salespersons) * 25)
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("最近几个月没有足够的销售员数据来生成热力图。")

        # 销售员准确率稳定性分析
        st.markdown("### 销售员准确率稳定性分析")

        # 计算销售员准确率的均值和标准差
        salesperson_stats = monthly_salesperson.groupby('销售员')['数量准确率'].agg([
            ('平均值', 'mean'),
            ('标准差', 'std'),
            ('最大值', 'max'),
            ('最小值', 'min')
        ]).reset_index()

        # 处理标准差为NaN的情况（只有一个月的数据）
        salesperson_stats['标准差'] = salesperson_stats['标准差'].fillna(0)

        # 选择有足够数据的销售员（至少3个月）
        salesperson_counts = monthly_salesperson.groupby('销售员').size().reset_index(name='count')
        valid_salespersons = salesperson_counts[salesperson_counts['count'] >= 3]['销售员'].tolist()

        salesperson_stats = salesperson_stats[salesperson_stats['销售员'].isin(valid_salespersons)]

        if not salesperson_stats.empty:
            # 创建散点图
            fig_scatter = px.scatter(
                salesperson_stats,
                x='平均值',
                y='标准差',
                hover_name='销售员',
                size='最大值',
                color='平均值',
                color_continuous_scale=[
                    [0, "red"],
                    [0.6, "yellow"],
                    [0.8, "green"],
                    [1, "blue"]
                ],
                range_color=[0, 100],
                size_max=15
            )

            # 添加四象限线
            fig_scatter.add_shape(
                type="line",
                x0=salesperson_stats['平均值'].mean(),
                x1=salesperson_stats['平均值'].mean(),
                y0=0,
                y1=salesperson_stats['标准差'].max() * 1.1,
                line=dict(color="black", width=1, dash="dash")
            )

            fig_scatter.add_shape(
                type="line",
                x0=0,
                x1=100,
                y0=salesperson_stats['标准差'].mean(),
                y1=salesperson_stats['标准差'].mean(),
                line=dict(color="black", width=1, dash="dash")
            )

            # 添加象限标注
            fig_scatter.add_annotation(
                x=salesperson_stats['平均值'].mean() * 0.5,
                y=salesperson_stats['标准差'].mean() * 0.5,
                text="低准确率<br>高稳定性",
                showarrow=False,
                font=dict(size=10)
            )

            fig_scatter.add_annotation(
                x=salesperson_stats['平均值'].mean() * 1.5,
                y=salesperson_stats['标准差'].mean() * 0.5,
                text="高准确率<br>高稳定性",
                showarrow=False,
                font=dict(size=10)
            )

            fig_scatter.add_annotation(
                x=salesperson_stats['平均值'].mean() * 0.5,
                y=salesperson_stats['标准差'].mean() * 1.5,
                text="低准确率<br>低稳定性",
                showarrow=False,
                font=dict(size=10)
            )

            fig_scatter.add_annotation(
                x=salesperson_stats['平均值'].mean() * 1.5,
                y=salesperson_stats['标准差'].mean() * 1.5,
                text="高准确率<br>低稳定性",
                showarrow=False,
                font=dict(size=10)
            )

            # 更新布局
            fig_scatter.update_layout(
                title="销售员准确率与稳定性分析",
                xaxis_title="平均准确率 (%)",
                yaxis_title="准确率标准差 (%)",
                plot_bgcolor='white',
                height=500
            )

            # 添加悬停信息
            fig_scatter.update_traces(
                hovertemplate='<b>%{hovertext}</b><br>平均准确率: %{x:.1f}%<br>标准差: %{y:.1f}%<br>最高准确率: %{marker.size:.1f}%<extra></extra>'
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

            # 图表解释
            best_avg = salesperson_stats.loc[salesperson_stats['平均值'].idxmax()]
            most_stable = salesperson_stats.loc[salesperson_stats['标准差'].idxmin()]

            # 定义理想销售员（高准确率，高稳定性）
            ideal_salespersons = salesperson_stats[
                (salesperson_stats['平均值'] > salesperson_stats['平均值'].mean()) &
                (salesperson_stats['标准差'] < salesperson_stats['标准差'].mean())
            ]

            # 需要重点培训的销售员（低准确率，低稳定性）
            train_salespersons = salesperson_stats[
                (salesperson_stats['平均值'] < salesperson_stats['平均值'].mean()) &
                (salesperson_stats['标准差'] > salesperson_stats['标准差'].mean())
            ]

            st.markdown(f"""
            <div class="chart-explanation">
                <strong>销售员准确率分析：</strong><br>
                · {best_avg['销售员']}的平均准确率最高，为{best_avg['平均值']:.1f}%<br>
                · {most_stable['销售员']}的准确率最稳定，标准差仅为{most_stable['标准差']:.1f}%<br>
                · 有{len(ideal_salespersons)}名销售员位于理想象限（高准确率，高稳定性）<br>
                · 有{len(train_salespersons)}名销售员位于待改进象限（低准确率，低稳定性）<br>
                
                <strong>行动建议：</strong><br>
                1. 分享优秀销售员（{", ".join(ideal_salespersons['销售员'].head(3).tolist() if len(ideal_salespersons) >= 3 else ideal_salespersons['销售员'].tolist())}）的预测方法，形成最佳实践<br>
                2. 对准确率低且波动大的销售员（{", ".join(train_salespersons['销售员'].head(3).tolist() if len(train_salespersons) >= 3 else train_salespersons['销售员'].tolist())}）进行重点培训<br>
                3. 建立销售员预测准确率评估机制，将准确率作为绩效考核的一部分
            </div>
            """, unsafe_allow_html=True)

            # 显示销售员准确率详细数据
            st.markdown("#### 销售员准确率详细数据")

            # 准备表格数据
            display_df = salesperson_stats.copy()
            display_df['平均准确率'] = display_df['平均值'].round(1).astype(str) + '%'
            display_df['波动范围'] = display_df.apply(
                lambda row: f"{row['最小值']:.1f}% - {row['最大值']:.1f}%",
                axis=1
            )

            # 计算每个销售员的销量
            salesperson_volume = filtered_data['merged_by_salesperson'].groupby('销售员')['求和项:数量（箱）'].sum().reset_index()
            display_df = pd.merge(display_df, salesperson_volume, on='销售员', how='left')

            # 按平均准确率排序
            display_df = display_df.sort_values('平均值', ascending=False)

            # 显示表格
            st.dataframe(
                display_df[['销售员', '平均准确率', '波动范围', '标准差', '求和项:数量（箱）']],
                use_container_width=True,
                column_config={
                    "销售员": st.column_config.Column("销售员", width="medium"),
                    "平均准确率": st.column_config.TextColumn("平均准确率"),
                    "波动范围": st.column_config.TextColumn("波动范围"),
                    "标准差": st.column_config.NumberColumn("标准差", format="%.2f"),
                    "求和项:数量（箱）": st.column_config.NumberColumn("销售量", format="%d")
                },
                hide_index=True
            )
        else:
            st.warning("没有足够的销售员数据来进行稳定性分析。")
    else:
        st.warning("没有足够的数据来分析销售员准确率趋势。")

def display_product_accuracy_trend(accuracy_trends, product_info, filter_months):
    """显示产品准确率趋势分析"""
    # 准备数据
    product_monthly = accuracy_trends['product_monthly'].copy()
    product_monthly['数量准确率'] = product_monthly['数量准确率'] * 100  # 转换为百分比

    # 筛选月份
    if filter_months and len(filter_months) > 0:
        product_monthly = product_monthly[product_monthly['所属年月'].isin(filter_months)]

    # 显示标题
    st.markdown("### 产品准确率趋势分析")

    if not product_monthly.empty:
        # 计算每个产品的平均准确率
        product_avg = product_monthly.groupby('产品代码')['数量准确率'].mean().reset_index()

        # 计算每个产品的销量
        product_volume = product_monthly.groupby('产品代码')['求和项:数量（箱）'].sum().reset_index()

        # 合并准确率和销量数据
        product_stats = pd.merge(product_avg, product_volume, on='产品代码', how='inner')

        # 筛选销量最大的10个产品
        top_products = product_stats.nlargest(10, '求和项:数量（箱）')['产品代码'].tolist()

        # 添加产品名称
        top_products_data = product_monthly[product_monthly['产品代码'].isin(top_products)]
        top_products_data['产品名称'] = top_products_data['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 创建产品准确率趋势图
        fig = go.Figure()

        # 为每个产品添加一条线
        for product in top_products:
            product_data = top_products_data[top_products_data['产品代码'] == product]
            product_name = product_data['产品名称'].iloc[0] if not product_data.empty else product

            fig.add_trace(go.Scatter(
                x=product_data['所属年月'],
                y=product_data['数量准确率'],
                mode='lines+markers',
                name=product_name,
                marker=dict(size=6)
            ))

        # 添加准确率目标线
        fig.add_shape(
            type="line",
            x0=top_products_data['所属年月'].min(),
            x1=top_products_data['所属年月'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="良好准确率基准"
        )

        # 更新布局
        fig.update_layout(
            title="主要产品准确率趋势（Top 10销量）",
            xaxis_title="月份",
            yaxis_title="准确率 (%)",
            yaxis=dict(range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=500,
            hovermode="x unified"
        )

        # 添加悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 产品准确率与销量散点图
        st.markdown("### 产品准确率与销量分析")

        # 合并产品信息和准确率数据
        product_info_df = product_stats.copy()
        product_info_df['产品名称'] = product_info_df['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 创建散点图
        fig_scatter = px.scatter(
            product_info_df,
            x='求和项:数量（箱）',
            y='数量准确率',
            hover_name='产品名称',
            size='求和项:数量（箱）',
            color='数量准确率',
            color_continuous_scale=[
                [0, "red"],
                [0.6, "yellow"],
                [0.8, "green"],
                [1, "blue"]
            ],
            range_color=[0, 100],
            size_max=40
        )

        # 添加准确率基准线
        fig_scatter.add_shape(
            type="line",
            x0=product_info_df['求和项:数量（箱）'].min(),
            x1=product_info_df['求和项:数量（箱）'].max(),
            y0=80,
            y1=80,
            line=dict(color="green", width=1, dash="dash"),
            name="准确率基准"
        )

        # 更新布局
        fig_scatter.update_layout(
            title="产品准确率与销量关系图",
            xaxis_title="销量 (箱)",
            yaxis_title="准确率 (%)",
            plot_bgcolor='white',
            height=600
        )

        # 添加悬停信息
        fig_scatter.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>销量: %{x:,.0f}箱<br>准确率: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        # 产品准确率热力图
        st.markdown("### 主要产品月度准确率热力图")

        # 筛选销量前20的产品
        top20_products = product_stats.nlargest(20, '求和项:数量（箱）')['产品代码'].tolist()

        # 筛选这些产品的数据
        top_products_data = product_monthly[product_monthly['产品代码'].isin(top20_products)]

        # 添加产品名称
        top_products_data['产品名称'] = top_products_data['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 数据透视表
        pivot_data = top_products_data.pivot_table(
            values='数量准确率',
            index='产品名称',
            columns='所属年月',
            aggfunc='mean'
        ).round(1)

        # 创建热力图
        fig_heatmap = px.imshow(
            pivot_data,
            text_auto='.1f',
            color_continuous_scale=[
                [0, "rgb(220, 53, 69)"],      # 红色 - 低准确率
                [0.5, "rgb(255, 193, 7)"],    # 黄色 - 中等准确率
                [0.8, "rgb(40, 167, 69)"],    # 绿色 - 高准确率
                [1, "rgb(0, 123, 255)"]       # 蓝色 - 最高准确率
            ],
            labels=dict(x="月份", y="产品", color="准确率 (%)"),
            range_color=[0, 100],
            aspect="auto"
        )

        # 更新布局
        fig_heatmap.update_layout(
            title="主要产品月度准确率热力图",
            xaxis_title="月份",
            yaxis_title="产品",
            coloraxis_colorbar=dict(title="准确率 (%)"),
            plot_bgcolor='white',
            height=max(500, len(top20_products) * 25)
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # 产品准确率详细数据
        st.markdown("### 产品准确率排名（Top 20）")

        # 筛选销量前50的产品
        top50_products = product_stats.nlargest(50, '求和项:数量（箱）')

        # 添加产品名称
        top50_products['产品名称'] = top50_products['产品代码'].apply(
            lambda x: format_product_code(x, product_info, include_name=True)
        )

        # 计算准确率稳定性
        product_stability = product_monthly.groupby('产品代码')['数量准确率'].std().reset_index()
        product_stability.columns = ['产品代码', '标准差']

        # 合并数据
        top50_products = pd.merge(top50_products, product_stability, on='产品代码', how='left')

        # 按准确率排序
        top50_products = top50_products.sort_values('数量准确率', ascending=False)

        # 显示前20个
        top50_products = top50_products.head(20)

        # 准备表格数据
        display_df = top50_products.copy()
        display_df['准确率'] = display_df['数量准确率'].round(1).astype(str) + '%'
        display_df['波动'] = display_df['标准差'].round(2)
        display_df['销量'] = display_df['求和项:数量（箱）']

        # 显示表格
        st.dataframe(
            display_df[['产品名称', '准确率', '波动', '销量']],
            use_container_width=True,
            column_config={
                "产品名称": st.column_config.Column("产品名称", width="medium"),
                "准确率": st.column_config.TextColumn("平均准确率"),
                "波动": st.column_config.NumberColumn("准确率波动", format="%.2f"),
                "销量": st.column_config.NumberColumn("销售量", format="%d")
            },
            hide_index=True
        )

        # 产品准确率分布分析
        st.markdown("### 产品准确率分布分析")

        # 计算准确率分布
        accuracy_bins = [0, 60, 80, 90, 100]
        accuracy_labels = ['低(0-60%)', '中(60-80%)', '高(80-90%)', '极高(90-100%)']

        product_stats['准确率区间'] = pd.cut(product_stats['数量准确率'], bins=accuracy_bins, labels=accuracy_labels, right=True)

        # 分布计数
        dist_counts = product_stats['准确率区间'].value_counts().reset_index()
        dist_counts.columns = ['准确率区间', '产品数量']

        # 按区间顺序排序
        dist_counts['区间顺序'] = dist_counts['准确率区间'].apply(lambda x: accuracy_labels.index(x))
        dist_counts = dist_counts.sort_values('区间顺序')

        # 创建条形图
        fig_dist = px.bar(
            dist_counts,
            x='准确率区间',
            y='产品数量',
            color='准确率区间',
            color_discrete_map={
                '低(0-60%)': '#F44336',
                '中(60-80%)': '#FFC107',
                '高(80-90%)': '#4CAF50',
                '极高(90-100%)': '#2196F3'
            },
            text='产品数量'
        )

        # 更新布局
        fig_dist.update_layout(
            title="产品准确率分布",
            xaxis_title="准确率区间",
            yaxis_title="产品数量",
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )

        # 添加文本标签
        fig_dist.update_traces(
            textposition='outside',
            texttemplate='%{text}个产品'
        )

        st.plotly_chart(fig_dist, use_container_width=True)

        # 图表解释
        st.markdown(f"""
        <div class="chart-explanation">
            <strong>产品准确率分析：</strong><br>
            · 销量最大的10个产品中，{len(top_products_data[top_products_data['数量准确率'] >= 80])/len(top_products_data)*100:.1f}%的月份达到了良好准确率（>=80%）<br>
            · 所有产品中，{len(product_stats[product_stats['数量准确率'] >= 80])/len(product_stats)*100:.1f}%的产品具有良好的平均准确率<br>
            · 高销量产品的准确率{("普遍更高" if product_stats[product_stats['求和项:数量（箱）'] > product_stats['求和项:数量（箱）'].median()]['数量准确率'].mean() > product_stats[product_stats['求和项:数量（箱）'] <= product_stats['求和项:数量（箱）'].median()]['数量准确率'].mean() else "并未显著高于")}低销量产品<br>
            
            <strong>行动建议：</strong><br>
            1. 重点关注销量大但准确率低的产品，优先改进其预测方法<br>
            2. 分析准确率波动较大的产品，识别影响准确率的关键因素<br>
            3. 对于类似产品，采用相似的预测方法，提高整体预测准确性
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("没有足够的数据来分析产品准确率趋势。")

# 主程序
def main():
    # 如果需要登录但未认证，显示登录屏幕
    if not st.session_state['authenticated']:
        show_login_screen()
        return

    # 加载数据
    actual_data = load_actual_data()
    forecast_data = load_forecast_data()
    product_info = load_product_info()

    # 筛选共有月份数据
    common_months = get_common_months(actual_data, forecast_data)
    actual_data = actual_data[actual_data['所属年月'].isin(common_months)]
    forecast_data = forecast_data[forecast_data['所属年月'].isin(common_months)]

    # 处理数据并缓存结果
    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = process_data(actual_data, forecast_data, product_info)

    # 显示筛选面板
    filter_months, filter_regions = display_filter_panel()

    # 根据当前视图显示相应内容
    if 'current_view' not in st.session_state:
        st.session_state['current_view'] = 'overview'

    # 检查是否有详细信息
    detail = None
    if 'selected_drill_down' in st.session_state:
        detail = st.session_state['selected_drill_down']

    # 显示相应页面
    if st.session_state['current_view'] == 'overview':
        display_overview_page(st.session_state['processed_data'], product_info, filter_months, filter_regions)
    elif st.session_state['current_view'] == 'accuracy':
        display_accuracy_analysis_page(st.session_state['processed_data'], product_info, filter_months, filter_regions, detail)
    elif st.session_state['current_view'] == 'bias':
        display_bias_analysis_page(st.session_state['processed_data'], product_info, filter_months, filter_regions, detail)
    elif st.session_state['current_view'] == 'sku_analysis':
        display_sku_analysis_page(st.session_state['processed_data'], product_info, filter_months, filter_regions, detail)
    elif st.session_state['current_view'] == 'trend':
        display_trend_analysis_page(st.session_state['processed_data'], product_info, filter_months, filter_regions)
    else:
        display_overview_page(st.session_state['processed_data'], product_info, filter_months, filter_regions)

    # 处理导航点击
    if 'streamlit:componentOutput' in st.query_params:
        output_data = st.query_params['streamlit:componentOutput']
        if 'view' in output_data:
            st.session_state['current_view'] = output_data['view']
            if 'detail' in output_data:
                st.session_state['selected_drill_down'] = output_data['detail']
            if 'index' in output_data:
                # 截断面包屑
                st.session_state['breadcrumb'] = st.session_state['breadcrumb'][:output_data['index'] + 1]
            st.rerun()

if __name__ == "__main__":
    main()