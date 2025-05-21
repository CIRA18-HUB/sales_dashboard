import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import os
import sys
import calendar
from dateutil.relativedelta import relativedelta

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售达成分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 - 使用新品仪表盘的样式
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
    }
    .card {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: white;
        transition: transform 0.3s;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
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
    .highlight {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 5px solid #1E88E5;
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
    .stExpander {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .chart-explanation {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 5px solid #1E88E5;
        font-size: 1rem;
        line-height: 1.5;
    }
    /* 调整图表容器的样式 */
    .st-emotion-cache-1wrcr25 {
        margin-top: 2rem !important;
        margin-bottom: 3rem !important;
        padding: 1rem !important;
    }
    /* 设置侧边栏样式 */
    .st-emotion-cache-6qob1r {
        background-color: #f5f7fa;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"]{
        background-color: #f8f9fa;
    }
    [data-testid="stSidebarNav"]{
        padding-top: 2rem;
    }
    .sidebar-header {
        font-size: 1.3rem;
        color: #0D47A1;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        letter-spacing: 0.03em;
    }
    /* 调整图表字体大小 */
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .xtick text {
        font-size: 14px !important;
        letter-spacing: 0.02em !important;
    }
    .js-plotly-plot .plotly .gtitle {
        font-size: 18px !important;
        letter-spacing: 0.03em !important;
    }
    /* 图表标签间距 */
    .js-plotly-plot .plotly text {
        letter-spacing: 0.02em !important;
    }
    /* KPI卡片样式 */
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        text-align: center;
        height: 100%;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .kpi-title {
        font-size: 1.1rem;
        color: #424242;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E88E5;
        margin: 0.5rem 0;
    }
    .kpi-subtitle {
        font-size: 0.9rem;
        color: #757575;
    }
    /* 正值和负值的颜色 */
    .positive-value {
        color: #4CAF50;
    }
    .negative-value {
        color: #F44336;
    }
    /* 图表容器 */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    /* 分析部分标题 */
    .analysis-section-title {
        font-size: 1.5rem;
        color: #1E88E5;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E3F2FD;
    }
    /* 图表标题 */
    .chart-title {
        font-size: 1.2rem;
        color: #0D47A1;
        margin-bottom: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# 文件路径配置 - 适配Streamlit Cloud
def get_file_path(filename):
    """获取文件路径，适配不同部署环境"""
    # 尝试不同的路径
    possible_paths = [
        filename,  # 当前目录
        f"./{filename}",  # 相对路径
        f"data/{filename}",  # 可能的data文件夹
        os.path.join(os.getcwd(), filename)  # 完整路径
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return filename  # 如果都不存在，返回原文件名


# 格式化数值的函数
def format_number(value):
    """格式化数量显示为逗号分隔的完整数字"""
    if pd.isna(value) or value == 0:
        return "0"
    return f"{int(value):,}"


def format_currency(value):
    """格式化金额显示"""
    if pd.isna(value) or value == 0:
        return "¥0"

    if value >= 100000000:  # 亿元级别
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:  # 万元级别
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{int(value):,}"


def format_percentage(value, include_sign=False):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0.0%"

    prefix = ""
    if include_sign and value > 0:
        prefix = "+"
    elif include_sign and value < 0:
        prefix = ""  # 负号已包含在值中

    return f"{prefix}{value:.1f}%"


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 数据加载函数
@st.cache_data
def load_raw_sales_data(file_path="仪表盘原始数据.xlsx"):
    """加载原始销售数据"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.error(f"❌ 找不到文件: {file_path}")
            st.info("请确认文件已正确上传到该目录")
            return pd.DataFrame()

        # 尝试读取Excel文件，处理编码问题
        try:
            df = pd.read_excel(actual_path, engine='openpyxl')
        except Exception as e:
            try:
                df = pd.read_excel(actual_path, engine='xlrd')
            except Exception as e2:
                st.error(f"无法读取Excel文件: {str(e)}")
                return pd.DataFrame()

        # 确保列名格式一致
        required_columns = ['发运月份', '所属区域', '客户代码', '经销商名称', '客户简称',
                            '申请人', '订单类型', '产品代码', '产品名称', '产品简称',
                            '单价（箱）', '求和项:数量（箱）', '求和项:金额（元）']

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ 销售数据文件缺少必要的列: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # 数据类型转换
        df['发运月份'] = pd.to_datetime(df['发运月份'], format='%Y-%m', errors='coerce')
        df['求和项:数量（箱）'] = pd.to_numeric(df['求和项:数量（箱）'], errors='coerce')
        df['求和项:金额（元）'] = pd.to_numeric(df['求和项:金额（元）'], errors='coerce')
        df['单价（箱）'] = pd.to_numeric(df['单价（箱）'], errors='coerce')

        # 填充缺失值
        df['求和项:数量（箱）'] = df['求和项:数量（箱）'].fillna(0)
        df['求和项:金额（元）'] = df['求和项:金额（元）'].fillna(0)

        # 删除无效日期的行
        df = df.dropna(subset=['发运月份'])

        return df

    except Exception as e:
        st.error(f"❌ 加载销售数据时出错: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_sales_targets(file_path="仪表盘销售月度指标维护.xlsx"):
    """加载销售月度指标数据"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.warning(f"⚠️ 找不到文件: {file_path}，将无法显示销售达成分析")
            return pd.DataFrame()

        try:
            df = pd.read_excel(actual_path, engine='openpyxl')
        except Exception:
            try:
                df = pd.read_excel(actual_path, engine='xlrd')
            except Exception as e:
                st.warning(f"无法读取销售指标文件: {str(e)}")
                return pd.DataFrame()

        required_columns = ['销售员', '指标年月', '月度指标', '往年同期', '省份区域', '所属大区']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.warning(f"销售指标文件缺少必要的列: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # 数据类型转换
        df['指标年月'] = pd.to_datetime(df['指标年月'], format='%Y-%m', errors='coerce')
        df['月度指标'] = pd.to_numeric(df['月度指标'], errors='coerce')
        df['往年同期'] = pd.to_numeric(df['往年同期'], errors='coerce')

        df['月度指标'] = df['月度指标'].fillna(0)
        df['往年同期'] = df['往年同期'].fillna(0)

        # 删除无效日期的行
        df = df.dropna(subset=['指标年月'])

        return df

    except Exception as e:
        st.warning(f"⚠️ 加载销售指标数据时出错: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_tt_targets(file_path="仪表盘TT产品月度指标.xlsx"):
    """加载TT产品月度指标数据"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.warning(f"⚠️ 找不到文件: {file_path}，将无法显示TT渠道达成分析")
            return pd.DataFrame()

        try:
            df = pd.read_excel(actual_path, engine='openpyxl')
        except Exception:
            try:
                df = pd.read_excel(actual_path, engine='xlrd')
            except Exception as e:
                st.warning(f"无法读取TT产品指标文件: {str(e)}")
                return pd.DataFrame()

        required_columns = ['城市', '城市类型', '指标年月', '月度指标', '往年同期', '所属大区']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.warning(f"TT产品指标文件缺少必要的列: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # 数据类型转换
        df['指标年月'] = pd.to_datetime(df['指标年月'], format='%Y-%m', errors='coerce')
        df['月度指标'] = pd.to_numeric(df['月度指标'], errors='coerce')
        df['往年同期'] = pd.to_numeric(df['往年同期'], errors='coerce')

        df['月度指标'] = df['月度指标'].fillna(0)
        df['往年同期'] = df['往年同期'].fillna(0)

        # 删除无效日期的行
        df = df.dropna(subset=['指标年月'])

        return df

    except Exception as e:
        st.warning(f"⚠️ 加载TT产品指标数据时出错: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_customer_relations(file_path="仪表盘人与客户关系表.xlsx"):
    """加载客户关系数据"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.warning(f"⚠️ 找不到文件: {file_path}，将使用所有客户数据")
            return pd.DataFrame()

        try:
            df = pd.read_excel(actual_path, engine='openpyxl')
        except Exception:
            try:
                df = pd.read_excel(actual_path, engine='xlrd')
            except Exception as e:
                st.warning(f"无法读取客户关系文件: {str(e)}")
                return pd.DataFrame()

        required_columns = ['销售员', '客户', '状态']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.warning(f"客户关系文件缺少必要的列: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # 只保留状态为'正常'的客户
        df = df[df['状态'] == '正常']

        return df

    except Exception as e:
        st.warning(f"⚠️ 加载客户关系数据时出错: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_product_codes(file_path="仪表盘产品代码.txt"):
    """加载产品代码列表"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.warning(f"⚠️ 找不到文件: {file_path}，将使用所有产品数据")
            return []

        # 尝试不同的编码方式
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']

        for encoding in encodings:
            try:
                with open(actual_path, 'r', encoding=encoding) as f:
                    product_codes = [line.strip() for line in f.readlines() if line.strip()]
                return product_codes
            except UnicodeDecodeError:
                continue

        st.warning(f"无法读取产品代码文件，编码问题")
        return []

    except Exception as e:
        st.warning(f"⚠️ 加载产品代码数据时出错: {str(e)}")
        return []


# 数据筛选和处理函数
def filter_current_year_data(df):
    """筛选当前年份的数据"""
    if df.empty:
        return df

    current_year = datetime.now().year
    filtered_df = df[df['发运月份'].dt.year == current_year]

    return filtered_df


def get_sales_by_channel(df):
    """按MT/TT渠道分组销售数据"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # MT渠道：订单-正常产品
    mt_data = df[df['订单类型'] == '订单-正常产品'].copy()

    # TT渠道：订单-TT产品
    tt_data = df[df['订单类型'] == '订单-TT产品'].copy()

    return mt_data, tt_data


def calculate_achievement_rate(actual_sales, targets):
    """计算销售达成率"""
    if targets is None or targets.empty or actual_sales.empty:
        return pd.DataFrame()

    try:
        # 按月份、销售员汇总实际销售
        actual_monthly = actual_sales.groupby(['发运月份', '申请人', '所属区域']).agg({
            '求和项:金额（元）': 'sum'
        }).reset_index()

        # 转换日期格式以便合并
        actual_monthly['指标年月'] = actual_monthly['发运月份']
        actual_monthly = actual_monthly.rename(columns={'申请人': '销售员'})

        # 合并实际销售和目标
        merged = pd.merge(
            actual_monthly,
            targets,
            on=['指标年月', '销售员'],
            how='outer'
        )

        # 填充缺失值
        merged['求和项:金额（元）'] = merged['求和项:金额（元）'].fillna(0)
        merged['月度指标'] = merged['月度指标'].fillna(0)

        # 计算达成率
        merged['达成率'] = np.where(
            merged['月度指标'] > 0,
            merged['求和项:金额（元）'] / merged['月度指标'] * 100,
            0
        )

        return merged

    except Exception as e:
        st.warning(f"计算销售达成率时出错: {str(e)}")
        return pd.DataFrame()


def calculate_growth_rate(df, period_type='month'):
    """计算成长率"""
    if df.empty:
        return pd.DataFrame()

    try:
        # 按月份汇总数据
        monthly_data = df.groupby('发运月份').agg({
            '求和项:金额（元）': 'sum',
            '求和项:数量（箱）': 'sum'
        }).reset_index()

        monthly_data = monthly_data.sort_values('发运月份')

        if len(monthly_data) < 2:
            return monthly_data

        if period_type == 'month':
            # 环比增长率（月度）
            monthly_data['销售额环比增长率'] = monthly_data['求和项:金额（元）'].pct_change() * 100
            monthly_data['销售量环比增长率'] = monthly_data['求和项:数量（箱）'].pct_change() * 100

            # 同比增长率（年度）
            monthly_data['年'] = monthly_data['发运月份'].dt.year
            monthly_data['月'] = monthly_data['发运月份'].dt.month

            # 初始化同比增长率列
            monthly_data['销售额同比增长率'] = np.nan
            monthly_data['销售量同比增长率'] = np.nan

            # 计算同比增长率
            for idx, row in monthly_data.iterrows():
                prev_year_data = monthly_data[
                    (monthly_data['年'] == row['年'] - 1) &
                    (monthly_data['月'] == row['月'])
                    ]

                if not prev_year_data.empty:
                    prev_amount = prev_year_data['求和项:金额（元）'].iloc[0]
                    prev_quantity = prev_year_data['求和项:数量（箱）'].iloc[0]

                    if prev_amount > 0:
                        monthly_data.loc[idx, '销售额同比增长率'] = (row[
                                                                         '求和项:金额（元）'] - prev_amount) / prev_amount * 100
                    if prev_quantity > 0:
                        monthly_data.loc[idx, '销售量同比增长率'] = (row[
                                                                         '求和项:数量（箱）'] - prev_quantity) / prev_quantity * 100

        return monthly_data

    except Exception as e:
        st.warning(f"计算成长率时出错: {str(e)}")
        return pd.DataFrame()


def calculate_quarterly_data(df):
    """计算季度数据"""
    if df.empty:
        return pd.DataFrame()

    # 创建季度列
    df['季度'] = df['发运月份'].dt.to_period('Q')

    # 按季度分组
    quarterly_data = df.groupby('季度').agg({
        '求和项:金额（元）': 'sum',
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 转换季度为字符串格式
    quarterly_data['季度'] = quarterly_data['季度'].astype(str)

    return quarterly_data


def calculate_quarterly_achievement(actual_sales, targets):
    """计算季度达成率"""
    if targets is None or targets.empty or actual_sales.empty:
        return pd.DataFrame()

    try:
        # 添加季度列
        actual_sales['季度'] = actual_sales['发运月份'].dt.to_period('Q')
        targets['季度'] = targets['指标年月'].dt.to_period('Q')

        # 按季度汇总销售数据
        actual_quarterly = actual_sales.groupby(['季度', '申请人', '所属区域']).agg({
            '求和项:金额（元）': 'sum'
        }).reset_index()

        # 按季度汇总目标数据
        targets_quarterly = targets.groupby(['季度', '销售员', '所属大区']).agg({
            '月度指标': 'sum'
        }).reset_index()

        # 合并数据
        actual_quarterly['销售员'] = actual_quarterly['申请人']
        merged = pd.merge(
            actual_quarterly,
            targets_quarterly,
            on=['季度', '销售员'],
            how='outer'
        )

        # 填充缺失值
        merged['求和项:金额（元）'] = merged['求和项:金额（元）'].fillna(0)
        merged['月度指标'] = merged['月度指标'].fillna(0)

        # 计算达成率
        merged['达成率'] = np.where(
            merged['月度指标'] > 0,
            merged['求和项:金额（元）'] / merged['月度指标'] * 100,
            0
        )

        # 转换季度为字符串格式
        merged['季度'] = merged['季度'].astype(str)

        return merged

    except Exception as e:
        st.warning(f"计算季度达成率时出错: {str(e)}")
        return pd.DataFrame()


def create_kpi_metrics(data, channel_name="全渠道"):
    """创建KPI指标卡片"""
    if data.empty:
        st.warning(f"⚠️ 没有{channel_name}数据可显示")
        return

    # 计算关键指标
    total_amount = data['求和项:金额（元）'].sum()
    total_quantity = data['求和项:数量（箱）'].sum()

    # 计算月度环比增长率
    growth_data = calculate_growth_rate(data)
    if not growth_data.empty and len(growth_data) > 1:
        latest_month_growth = growth_data.iloc[-1]['销售额环比增长率']
        latest_quantity_growth = growth_data.iloc[-1]['销售量环比增长率']
    else:
        latest_month_growth = 0
        latest_quantity_growth = 0

    # 计算年度指标
    current_year = datetime.now().year
    prev_year = current_year - 1
    current_year_data = data[data['发运月份'].dt.year == current_year]
    prev_year_data = data[data['发运月份'].dt.year == prev_year]

    current_year_amount = current_year_data['求和项:金额（元）'].sum()
    prev_year_amount = prev_year_data['求和项:金额（元）'].sum()

    yoy_growth = 0
    if prev_year_amount > 0:
        yoy_growth = (current_year_amount - prev_year_amount) / prev_year_amount * 100

    # 显示KPI卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">总销售额</div>
            <div class="kpi-value">{format_currency(total_amount)}</div>
            <div class="kpi-subtitle">{current_year}年累计</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">总销售量</div>
            <div class="kpi-value">{format_number(total_quantity)}箱</div>
            <div class="kpi-subtitle">{current_year}年累计</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        growth_class = "positive-value" if latest_month_growth >= 0 else "negative-value"
        growth_symbol = "+" if latest_month_growth > 0 else ""

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">月度环比增长</div>
            <div class="kpi-value {growth_class}">{growth_symbol}{format_percentage(latest_month_growth)}</div>
            <div class="kpi-subtitle">相比上月销售额</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        yoy_class = "positive-value" if yoy_growth >= 0 else "negative-value"
        yoy_symbol = "+" if yoy_growth > 0 else ""

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">年度同比增长</div>
            <div class="kpi-value {yoy_class}">{yoy_symbol}{format_percentage(yoy_growth)}</div>
            <div class="kpi-subtitle">相比去年同期</div>
        </div>
        """, unsafe_allow_html=True)


def create_regional_analysis(data, channel_name="全渠道", achievement_data=None):
    """创建区域分析图表"""
    if data.empty:
        st.warning(f"⚠️ 没有{channel_name}区域数据可分析")
        return

    st.markdown(f'<div class="analysis-section-title">📍 区域销售分析</div>', unsafe_allow_html=True)

    # 按区域汇总销售数据
    region_sales = data.groupby('所属区域').agg({
        '求和项:金额（元）': 'sum',
        '求和项:数量（箱）': 'sum',
        '客户简称': 'nunique'
    }).reset_index()

    region_sales.columns = ['所属区域', '销售额', '销售量', '客户数']
    region_sales = region_sales.sort_values('销售额', ascending=False)

    # 计算区域销售达成率
    region_achievement = pd.DataFrame()
    if achievement_data is not None and not achievement_data.empty:
        region_achievement = achievement_data.groupby('所属大区').agg({
            '达成率': 'mean',
            '月度指标': 'sum',
            '求和项:金额（元）': 'sum'
        }).reset_index()
        region_achievement = region_achievement.rename(columns={'所属大区': '所属区域'})

    # 创建图表
    col1, col2 = st.columns(2)

    with col1:
        # 区域销售额图表
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">区域销售额分布</div>', unsafe_allow_html=True)

        fig_region_sales = go.Figure()

        colors = px.colors.qualitative.Bold
        for i, row in region_sales.iterrows():
            fig_region_sales.add_trace(go.Bar(
                x=[row['所属区域']],
                y=[row['销售额']],
                name=row['所属区域'],
                text=[format_currency(row['销售额'])],
                textposition='auto',
                marker_color=colors[i % len(colors)]
            ))

        fig_region_sales.update_layout(
            showlegend=False,
            xaxis_title="区域",
            yaxis_title="销售额",
            plot_bgcolor='white',
            height=400,
            margin=dict(t=30, b=50, l=60, r=30)
        )

        fig_region_sales.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        fig_region_sales.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        st.plotly_chart(fig_region_sales, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if not region_achievement.empty:
            # 区域达成率图表
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">区域销售达成率</div>', unsafe_allow_html=True)

            fig_achievement = px.bar(
                region_achievement,
                y='所属区域',
                x='达成率',
                orientation='h',
                height=400,
                color='达成率',
                color_continuous_scale=px.colors.sequential.Blues,
                text=[f"{x:.1f}%" for x in region_achievement['达成率']]
            )

            fig_achievement.update_traces(
                textposition='auto',
                textfont=dict(size=14)
            )

            fig_achievement.update_layout(
                xaxis_title="达成率 (%)",
                yaxis_title="区域",
                plot_bgcolor='white',
                margin=dict(t=30, b=50, l=60, r=30)
            )

            # 添加100%基准线
            fig_achievement.add_vline(
                x=100,
                line_dash="dash",
                line_color="red",
                annotation_text="目标线(100%)",
                annotation_position="top"
            )

            fig_achievement.update_xaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14),
                gridcolor='#eee'
            )

            fig_achievement.update_yaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14)
            )

            st.plotly_chart(fig_achievement, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 区域销售占比饼图
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">区域销售占比</div>', unsafe_allow_html=True)

            fig_region_pie = px.pie(
                region_sales,
                values='销售额',
                names='所属区域',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=400
            )

            fig_region_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(size=14)
            )

            fig_region_pie.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=14)
                ),
                margin=dict(t=30, b=50, l=60, r=30)
            )

            st.plotly_chart(fig_region_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 区域客户数量和平均客单价
    col1, col2 = st.columns(2)

    with col1:
        # 区域客户数量
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">区域客户数量</div>', unsafe_allow_html=True)

        fig_customers = px.bar(
            region_sales,
            x='所属区域',
            y='客户数',
            color='所属区域',
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=350,
            text='客户数'
        )

        fig_customers.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_customers.update_layout(
            showlegend=False,
            xaxis_title="区域",
            yaxis_title="客户数",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=60, r=30)
        )

        fig_customers.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        fig_customers.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        st.plotly_chart(fig_customers, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 计算平均客单价
        region_sales['平均客单价'] = region_sales['销售额'] / region_sales['客户数']

        # 平均客单价图表
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">区域平均客单价</div>', unsafe_allow_html=True)

        fig_avg_sales = px.bar(
            region_sales,
            x='所属区域',
            y='平均客单价',
            color='所属区域',
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=350,
            text=[format_currency(x) for x in region_sales['平均客单价']]
        )

        fig_avg_sales.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_avg_sales.update_layout(
            showlegend=False,
            xaxis_title="区域",
            yaxis_title="平均客单价",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=60, r=30)
        )

        fig_avg_sales.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        fig_avg_sales.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        st.plotly_chart(fig_avg_sales, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 添加解释
    top_region = region_sales.iloc[0]['所属区域']
    top_region_sales = format_currency(region_sales.iloc[0]['销售额'])
    top_region_customers = region_sales.iloc[0]['客户数']

    explanation = f"""
    <b>区域分析:</b> {channel_name}中，<span style='color:#1E88E5;font-weight:bold;'>{top_region}</span>区域的销售表现最为突出，
    累计销售额达到{top_region_sales}，覆盖{top_region_customers}家客户。
    """

    if not region_achievement.empty:
        best_achieve_region = region_achievement.loc[region_achievement['达成率'].idxmax()]
        worst_achieve_region = region_achievement.loc[region_achievement['达成率'].idxmin()]

        explanation += f"""<br><b>达成率分析:</b> {best_achieve_region['所属区域']}区域达成率最高，为
        {best_achieve_region['达成率']:.1f}%；{worst_achieve_region['所属区域']}区域达成率最低，为
        {worst_achieve_region['达成率']:.1f}%。"""

    add_chart_explanation(explanation)


def create_salesperson_analysis(data, channel_name="全渠道", achievement_data=None):
    """创建销售员分析图表"""
    if data.empty:
        st.warning(f"⚠️ 没有{channel_name}销售员数据可分析")
        return

    st.markdown(f'<div class="analysis-section-title">👨‍💼 销售员业绩分析</div>', unsafe_allow_html=True)

    # 按销售员汇总数据
    salesperson_data = data.groupby('申请人').agg({
        '求和项:金额（元）': 'sum',
        '求和项:数量（箱）': 'sum',
        '客户简称': 'nunique'
    }).reset_index()

    salesperson_data.columns = ['销售员', '销售额', '销售量', '客户数']
    salesperson_data = salesperson_data.sort_values('销售额', ascending=False).head(10)

    # 销售员达成率数据
    salesperson_achievement = pd.DataFrame()
    if achievement_data is not None and not achievement_data.empty:
        salesperson_achievement = achievement_data.groupby('销售员').agg({
            '达成率': 'mean',
            '月度指标': 'sum',
            '求和项:金额（元）': 'sum'
        }).reset_index()

        # 只显示前10名销售员
        top_salespeople = salesperson_data['销售员'].tolist()
        salesperson_achievement = salesperson_achievement[salesperson_achievement['销售员'].isin(top_salespeople)]

    # 创建图表
    col1, col2 = st.columns(2)

    with col1:
        # 销售员销售额排名
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">销售员销售额排名 (前10名)</div>', unsafe_allow_html=True)

        fig_sales_ranking = px.bar(
            salesperson_data,
            y='销售员',
            x='销售额',
            orientation='h',
            color='销售额',
            color_continuous_scale=px.colors.sequential.Blues,
            height=500,
            text=[format_currency(x) for x in salesperson_data['销售额']]
        )

        fig_sales_ranking.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_sales_ranking.update_layout(
            xaxis_title="销售额",
            yaxis_title="销售员",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=100, r=30),
            yaxis={'categoryorder': 'total ascending'}
        )

        fig_sales_ranking.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        fig_sales_ranking.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        st.plotly_chart(fig_sales_ranking, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if not salesperson_achievement.empty:
            # 销售员达成率图表
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">销售员达成率 (前10名)</div>', unsafe_allow_html=True)

            fig_achieve_ranking = px.bar(
                salesperson_achievement,
                y='销售员',
                x='达成率',
                orientation='h',
                color='达成率',
                color_continuous_scale=px.colors.sequential.Greens,
                height=500,
                text=[f"{x:.1f}%" for x in salesperson_achievement['达成率']]
            )

            fig_achieve_ranking.update_traces(
                textposition='auto',
                textfont=dict(size=14)
            )

            fig_achieve_ranking.update_layout(
                xaxis_title="达成率 (%)",
                yaxis_title="销售员",
                plot_bgcolor='white',
                margin=dict(t=30, b=50, l=100, r=30)
            )

            # 添加100%基准线
            fig_achieve_ranking.add_vline(
                x=100,
                line_dash="dash",
                line_color="red",
                annotation_text="目标线(100%)",
                annotation_position="top"
            )

            fig_achieve_ranking.update_xaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14),
                gridcolor='#eee'
            )

            fig_achieve_ranking.update_yaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14)
            )

            st.plotly_chart(fig_achieve_ranking, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 销售员客户数图表
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">销售员覆盖客户数 (前10名)</div>', unsafe_allow_html=True)

            fig_customer_count = px.bar(
                salesperson_data,
                y='销售员',
                x='客户数',
                orientation='h',
                color='客户数',
                color_continuous_scale=px.colors.sequential.Greens,
                height=500,
                text='客户数'
            )

            fig_customer_count.update_traces(
                textposition='auto',
                textfont=dict(size=14)
            )

            fig_customer_count.update_layout(
                xaxis_title="客户数",
                yaxis_title="销售员",
                plot_bgcolor='white',
                margin=dict(t=30, b=50, l=100, r=30),
                yaxis={'categoryorder': 'total ascending'}
            )

            fig_customer_count.update_xaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14),
                gridcolor='#eee'
            )

            fig_customer_count.update_yaxes(
                tickfont=dict(size=14),
                title_font=dict(size=14)
            )

            st.plotly_chart(fig_customer_count, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 销售员客单价和销售趋势
    col1, col2 = st.columns(2)

    with col1:
        # 销售员平均客单价
        salesperson_data['平均客单价'] = salesperson_data['销售额'] / salesperson_data['客户数']

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">销售员平均客单价</div>', unsafe_allow_html=True)

        fig_avg_sales = px.bar(
            salesperson_data,
            y='销售员',
            x='平均客单价',
            orientation='h',
            color='平均客单价',
            color_continuous_scale=px.colors.sequential.Oranges,
            height=450,
            text=[format_currency(x) for x in salesperson_data['平均客单价']]
        )

        fig_avg_sales.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_avg_sales.update_layout(
            xaxis_title="平均客单价",
            yaxis_title="销售员",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=100, r=30),
            yaxis={'categoryorder': 'total ascending'}
        )

        fig_avg_sales.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        fig_avg_sales.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        st.plotly_chart(fig_avg_sales, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 拆分月度数据
        try:
            # 获取表现最好的销售员
            top_salesperson = salesperson_data.iloc[0]['销售员']
            top_salesperson_data = data[data['申请人'] == top_salesperson]

            # 按月分组销售数据
            monthly_data = top_salesperson_data.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
                '求和项:金额（元）': 'sum'
            }).reset_index()

            monthly_data = monthly_data.sort_values('发运月份')
            monthly_data['月份'] = monthly_data['发运月份'].dt.strftime('%Y-%m')

            if not monthly_data.empty:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="chart-title">顶级销售员 {top_salesperson} 月度业绩</div>',
                            unsafe_allow_html=True)

                fig_monthly = px.line(
                    monthly_data,
                    x='月份',
                    y='求和项:金额（元）',
                    markers=True,
                    height=450
                )

                fig_monthly.update_traces(
                    line=dict(width=3, color='#1E88E5'),
                    marker=dict(size=10, color='#0D47A1')
                )

                fig_monthly.update_layout(
                    xaxis_title="月份",
                    yaxis_title="销售额",
                    plot_bgcolor='white',
                    margin=dict(t=30, b=70, l=70, r=30)
                )

                # 添加数据标签
                for i, row in monthly_data.iterrows():
                    fig_monthly.add_annotation(
                        x=row['月份'],
                        y=row['求和项:金额（元）'],
                        text=format_currency(row['求和项:金额（元）']),
                        showarrow=False,
                        yshift=10,
                        font=dict(size=12)
                    )

                fig_monthly.update_xaxes(
                    tickfont=dict(size=14),
                    title_font=dict(size=14),
                    tickangle=45
                )

                fig_monthly.update_yaxes(
                    tickfont=dict(size=14),
                    title_font=dict(size=14),
                    gridcolor='#eee'
                )

                st.plotly_chart(fig_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"没有找到{top_salesperson}的月度数据")
        except Exception as e:
            st.warning(f"显示月度数据时出错: {str(e)}")

    # 添加解释
    top_salesperson = salesperson_data.iloc[0]['销售员']
    top_sales_amount = format_currency(salesperson_data.iloc[0]['销售额'])

    explanation = f"""
    <b>销售员分析:</b> 在{channel_name}中，<span style='color:#1E88E5;font-weight:bold;'>{top_salesperson}</span>的销售业绩最为突出，
    累计销售额达到{top_sales_amount}，排名第一。
    """

    if not salesperson_achievement.empty:
        try:
            best_achieve_salesperson = salesperson_achievement.loc[salesperson_achievement['达成率'].idxmax()]

            explanation += f"""<br><b>达成率分析:</b> {best_achieve_salesperson['销售员']}的达成率最高，为
            {best_achieve_salesperson['达成率']:.1f}%，表现优异。"""

            # 计算达成率统计
            above_target = len(salesperson_achievement[salesperson_achievement['达成率'] >= 100])
            total_salespeople = len(salesperson_achievement)

            explanation += f"<br>前10名销售员中，有{above_target}人达成或超额完成销售目标，占比{above_target / total_salespeople * 100:.1f}%。"
        except:
            pass

    add_chart_explanation(explanation)


def create_quarterly_analysis(data, channel_name="全渠道", achievement_data=None):
    """创建季度分析图表"""
    if data.empty:
        st.warning(f"⚠️ 没有{channel_name}季度数据可分析")
        return

    st.markdown(f'<div class="analysis-section-title">📅 季度销售分析</div>', unsafe_allow_html=True)

    # 计算季度数据
    quarterly_data = calculate_quarterly_data(data)

    if quarterly_data.empty:
        st.warning("季度数据计算失败")
        return

    # 计算季度达成率
    quarterly_achievement = pd.DataFrame()
    if achievement_data is not None and not achievement_data.empty:
        quarterly_achievement = calculate_quarterly_achievement(data, achievement_data)

        if not quarterly_achievement.empty:
            quarterly_achievement_summary = quarterly_achievement.groupby('季度').agg({
                '达成率': 'mean',
                '月度指标': 'sum',
                '求和项:金额（元）': 'sum'
            }).reset_index()

    # 创建图表
    col1, col2 = st.columns(2)

    with col1:
        # 季度销售额柱状图
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">季度销售额</div>', unsafe_allow_html=True)

        fig_quarterly = px.bar(
            quarterly_data,
            x='季度',
            y='求和项:金额（元）',
            color='季度',
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=400,
            text=[format_currency(x) for x in quarterly_data['求和项:金额（元）']]
        )

        fig_quarterly.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_quarterly.update_layout(
            showlegend=False,
            xaxis_title="季度",
            yaxis_title="销售额",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=60, r=30)
        )

        fig_quarterly.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        fig_quarterly.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        st.plotly_chart(fig_quarterly, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 季度销售量柱状图
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">季度销售量</div>', unsafe_allow_html=True)

        fig_quantity = px.bar(
            quarterly_data,
            x='季度',
            y='求和项:数量（箱）',
            color='季度',
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=400,
            text=[f"{format_number(x)}箱" for x in quarterly_data['求和项:数量（箱）']]
        )

        fig_quantity.update_traces(
            textposition='auto',
            textfont=dict(size=14)
        )

        fig_quantity.update_layout(
            showlegend=False,
            xaxis_title="季度",
            yaxis_title="销售量 (箱)",
            plot_bgcolor='white',
            margin=dict(t=30, b=50, l=60, r=30)
        )

        fig_quantity.update_xaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14)
        )

        fig_quantity.update_yaxes(
            tickfont=dict(size=14),
            title_font=dict(size=14),
            gridcolor='#eee'
        )

        st.plotly_chart(fig_quantity, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 季度达成率图表
    if not quarterly_achievement.empty and 'quarterly_achievement_summary' in locals():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">季度销售达成率</div>', unsafe_allow_html=True)

        fig_quarter_achievement = go.Figure()

        # 添加销售额和目标柱状图
        fig_quarter_achievement.add_trace(go.Bar(
            x=quarterly_achievement_summary['季度'],
            y=quarterly_achievement_summary['求和项:金额（元）'],
            name='实际销售额',
            marker_color='#1E88E5',
            text=[format_currency(x) for x in quarterly_achievement_summary['求和项:金额（元）']],
            textposition='auto'
        ))

        fig_quarter_achievement.add_trace(go.Bar(
            x=quarterly_achievement_summary['季度'],
            y=quarterly_achievement_summary['月度指标'],
            name='销售目标',
            marker_color='#90CAF9',
            text=[format_currency(x) for x in quarterly_achievement_summary['月度指标']],
            textposition='auto'
        ))

        # 添加达成率线
        fig_quarter_achievement.add_trace(go.Scatter(
            x=quarterly_achievement_summary['季度'],
            y=quarterly_achievement_summary['达成率'],
            mode='lines+markers+text',
            name='达成率',
            yaxis='y2',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=10),
            text=[f"{x:.1f}%" for x in quarterly_achievement_summary['达成率']],
            textposition='top center'
        ))

        # 更新布局
        fig_quarter_achievement.update_layout(
            barmode='group',
            xaxis=dict(
                title="季度",
                titlefont=dict(size=14),
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                title="销售额/目标",
                titlefont=dict(size=14),
                tickfont=dict(size=14),
                gridcolor='#eee'
            ),
            yaxis2=dict(
                title="达成率 (%)",
                titlefont=dict(size=14, color='#4CAF50'),
                tickfont=dict(size=14, color='#4CAF50'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='white',
            height=500,
            margin=dict(t=80, b=50, l=60, r=80)
        )

        # 添加100%基准线
        fig_quarter_achievement.add_hline(
            y=100,
            line_dash="dash",
            line_color="red",
            opacity=0.7,
            yref='y2',
            annotation_text="目标线(100%)",
            annotation_position="top right"
        )

        st.plotly_chart(fig_quarter_achievement, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 添加解释
    if not quarterly_data.empty:
        max_quarter = quarterly_data.loc[quarterly_data['求和项:金额（元）'].idxmax()]
        max_sales = format_currency(max_quarter['求和项:金额（元）'])
        max_q = max_quarter['季度']

        explanation = f"""
        <b>季度分析:</b> 在{channel_name}中，<span style='color:#1E88E5;font-weight:bold;'>{max_q}</span>的销售表现最为突出，
        销售额达到{max_sales}，领先于其他季度。
        """

        if not quarterly_achievement.empty and 'quarterly_achievement_summary' in locals():
            try:
                best_quarter = quarterly_achievement_summary.loc[quarterly_achievement_summary['达成率'].idxmax()]
                best_q = best_quarter['季度']
                best_rate = best_quarter['达成率']

                explanation += f"""<br><b>达成率分析:</b> {best_q}的达成率最高，为{best_rate:.1f}%，
                表现{('优秀' if best_rate >= 100 else '良好' if best_rate >= 80 else '一般')}。"""

                # 计算同比环比
                if len(quarterly_achievement_summary) > 1:
                    latest_q = quarterly_achievement_summary.iloc[-1]
                    previous_q = quarterly_achievement_summary.iloc[-2]

                    qoq_growth = (latest_q['求和项:金额（元）'] - previous_q['求和项:金额（元）']) / previous_q[
                        '求和项:金额（元）'] * 100

                    explanation += f"<br><b>环比增长:</b> 最新季度{latest_q['季度']}相比上一季度{previous_q['季度']}，"
                    explanation += f"销售额环比{'增长' if qoq_growth >= 0 else '下降'}{abs(qoq_growth):.1f}%。"
            except:
                pass

        add_chart_explanation(explanation)


def create_monthly_analysis(data, channel_name="全渠道", achievement_data=None):
    """创建月度分析图表"""
    if data.empty:
        st.warning(f"⚠️ 没有{channel_name}月度数据可分析")
        return

    st.markdown(f'<div class="analysis-section-title">📆 月度销售分析</div>', unsafe_allow_html=True)

    # 按月分组数据
    monthly_data = data.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
        '求和项:金额（元）': 'sum',
        '求和项:数量（箱）': 'sum',
        '客户简称': 'nunique'
    }).reset_index()

    monthly_data['月份'] = monthly_data['发运月份'].dt.strftime('%Y-%m')
    monthly_data = monthly_data.sort_values('发运月份')

    # 计算增长率
    if len(monthly_data) > 1:
        monthly_data['销售额环比增长率'] = monthly_data['求和项:金额（元）'].pct_change() * 100
        monthly_data['销售量环比增长率'] = monthly_data['求和项:数量（箱）'].pct_change() * 100

    # 获取月度达成率
    monthly_achievement = pd.DataFrame()
    if achievement_data is not None and not achievement_data.empty:
        monthly_achievement = achievement_data.groupby('指标年月').agg({
            '达成率': 'mean',
            '月度指标': 'sum',
            '求和项:金额（元）': 'sum'
        }).reset_index()

        monthly_achievement['月份'] = monthly_achievement['指标年月'].dt.strftime('%Y-%m')

    # 创建图表
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">月度销售趋势</div>', unsafe_allow_html=True)

    # 创建双Y轴图表
    fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加销售额柱状图
    fig_monthly.add_trace(
        go.Bar(
            x=monthly_data['月份'],
            y=monthly_data['求和项:金额（元）'],
            name='销售额',
            marker_color='#1E88E5',
            text=[format_currency(x) for x in monthly_data['求和项:金额（元）']],
            textposition='auto'
        ),
        secondary_y=False
    )

    # 添加销售量线
    fig_monthly.add_trace(
        go.Scatter(
            x=monthly_data['月份'],
            y=monthly_data['求和项:数量（箱）'],
            name='销售量',
            mode='lines+markers',
            line=dict(color='#FFA726', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )

    # 更新布局
    fig_monthly.update_layout(
        xaxis=dict(
            title="月份",
            titlefont=dict(size=14),
            tickfont=dict(size=14),
            tickangle=45
        ),
        yaxis=dict(
            title="销售额",
            titlefont=dict(size=14, color='#1E88E5'),
            tickfont=dict(size=14, color='#1E88E5'),
            gridcolor='#eee'
        ),
        yaxis2=dict(
            title="销售量(箱)",
            titlefont=dict(size=14, color='#FFA726'),
            tickfont=dict(size=14, color='#FFA726'),
            gridcolor='#eee'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='white',
        height=500,
        margin=dict(t=80, b=70, l=70, r=70)
    )

    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 月度达成率
    if not monthly_achievement.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">月度销售达成率</div>', unsafe_allow_html=True)

        fig_achievement = go.Figure()

        # 添加达成率线
        fig_achievement.add_trace(go.Scatter(
            x=monthly_achievement['月份'],
            y=monthly_achievement['达成率'],
            mode='lines+markers+text',
            name='达成率',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=10),
            text=[f"{x:.1f}%" for x in monthly_achievement['达成率']],
            textposition='top center'
        ))

        # 添加100%基准线
        fig_achievement.add_hline(
            y=100,
            line_dash="dash",
            line_color="red",
            annotation_text="目标线(100%)",
            annotation_position="top right"
        )

        # 更新布局
        fig_achievement.update_layout(
            xaxis=dict(
                title="月份",
                titlefont=dict(size=14),
                tickfont=dict(size=14),
                tickangle=45
            ),
            yaxis=dict(
                title="达成率 (%)",
                titlefont=dict(size=14),
                tickfont=dict(size=14),
                gridcolor='#eee'
            ),
            showlegend=False,
            plot_bgcolor='white',
            height=400,
            margin=dict(t=30, b=70, l=70, r=30)
        )

        st.plotly_chart(fig_achievement, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 环比增长率图表
    if len(monthly_data) > 1:
        col1, col2 = st.columns(2)

        with col1:
            # 销售额环比增长率
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">销售额环比增长率</div>', unsafe_allow_html=True)

            fig_mom_sales = go.Figure()

            fig_mom_sales.add_trace(go.Bar(
                x=monthly_data['月份'][1:],  # 跳过第一个月，因为没有环比
                y=monthly_data['销售额环比增长率'][1:],
                marker_color=np.where(monthly_data['销售额环比增长率'][1:] >= 0, '#4CAF50', '#F44336'),
                text=[f"{x:+.1f}%" for x in monthly_data['销售额环比增长率'][1:]],
                textposition='auto'
            ))

            # 添加0%基准线
            fig_mom_sales.add_hline(
                y=0,
                line_dash="dash",
                line_color="black"
            )

            fig_mom_sales.update_layout(
                xaxis=dict(
                    title="月份",
                    titlefont=dict(size=14),
                    tickfont=dict(size=14),
                    tickangle=45
                ),
                yaxis=dict(
                    title="环比增长率 (%)",
                    titlefont=dict(size=14),
                    tickfont=dict(size=14),
                    gridcolor='#eee'
                ),
                showlegend=False,
                plot_bgcolor='white',
                height=400,
                margin=dict(t=30, b=70, l=70, r=30)
            )

            st.plotly_chart(fig_mom_sales, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # 销售量环比增长率
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">销售量环比增长率</div>', unsafe_allow_html=True)

            fig_mom_quantity = go.Figure()

            fig_mom_quantity.add_trace(go.Bar(
                x=monthly_data['月份'][1:],  # 跳过第一个月，因为没有环比
                y=monthly_data['销售量环比增长率'][1:],
                marker_color=np.where(monthly_data['销售量环比增长率'][1:] >= 0, '#4CAF50', '#F44336'),
                text=[f"{x:+.1f}%" for x in monthly_data['销售量环比增长率'][1:]],
                textposition='auto'
            ))

            # 添加0%基准线
            fig_mom_quantity.add_hline(
                y=0,
                line_dash="dash",
                line_color="black"
            )

            fig_mom_quantity.update_layout(
                xaxis=dict(
                    title="月份",
                    titlefont=dict(size=14),
                    tickfont=dict(size=14),
                    tickangle=45
                ),
                yaxis=dict(
                    title="环比增长率 (%)",
                    titlefont=dict(size=14),
                    tickfont=dict(size=14),
                    gridcolor='#eee'
                ),
                showlegend=False,
                plot_bgcolor='white',
                height=400,
                margin=dict(t=30, b=70, l=70, r=30)
            )

            st.plotly_chart(fig_mom_quantity, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 添加解释
    if not monthly_data.empty:
        latest_month = monthly_data.iloc[-1]
        latest_month_str = latest_month['月份']
        latest_sales = format_currency(latest_month['求和项:金额（元）'])

        explanation = f"""
        <b>月度分析:</b> 最新月份({latest_month_str})销售额为{latest_sales}，销售量为{format_number(latest_month['求和项:数量（箱）'])}箱。
        """

        if len(monthly_data) > 1:
            latest_mom_growth = latest_month['销售额环比增长率']
            growth_desc = '增长' if latest_mom_growth >= 0 else '下降'

            explanation += f"<br><b>环比分析:</b> 最新月份销售额环比{growth_desc} {abs(latest_mom_growth):.1f}%，"

            if latest_mom_growth >= 5:
                explanation += "增长势头强劲。"
            elif latest_mom_growth >= 0:
                explanation += "保持正增长。"
            elif latest_mom_growth >= -5:
                explanation += "略有下降。"
            else:
                explanation += "下降幅度较大，需要关注。"

        if not monthly_achievement.empty:
            try:
                latest_achievement = monthly_achievement.iloc[-1]
                latest_achievement_rate = latest_achievement['达成率']

                explanation += f"<br><b>达成率分析:</b> 最新月份达成率为{latest_achievement_rate:.1f}%，"

                if latest_achievement_rate >= 100:
                    explanation += "超额完成销售目标。"
                elif latest_achievement_rate >= 90:
                    explanation += "接近完成销售目标。"
                elif latest_achievement_rate >= 80:
                    explanation += "达成情况良好。"
                else:
                    explanation += "与目标仍有差距。"

                # 计算月度达成趋势
                if len(monthly_achievement) > 1:
                    is_increasing = monthly_achievement['达成率'].iloc[-1] > monthly_achievement['达成率'].iloc[-2]

                    explanation += f" 达成率呈{'上升' if is_increasing else '下降'}趋势。"
            except:
                pass

        add_chart_explanation(explanation)


# 主程序
def main():
    # 标题
    st.markdown('<div class="main-header">销售达成分析仪表盘</div>', unsafe_allow_html=True)

    # 加载数据
    with st.spinner('🔄 正在加载数据...'):
        # 加载销售数据和目标数据
        raw_sales_data = load_raw_sales_data()
        sales_targets = load_sales_targets()
        tt_targets = load_tt_targets()
        customer_relations = load_customer_relations()
        product_codes = load_product_codes()

        # 检查数据加载情况
        if raw_sales_data.empty:
            st.error("❌ 无法加载销售数据，请检查数据文件")
            st.info("请确认文件 '仪表盘原始数据.xlsx' 存在且格式正确")
            st.stop()

        # 数据筛选和预处理
        # 筛选有效产品
        if product_codes:
            raw_sales_data = raw_sales_data[raw_sales_data['产品代码'].isin(product_codes)]

        # 筛选正常客户
        if not customer_relations.empty:
            normal_customers = customer_relations['客户'].unique()
            raw_sales_data = raw_sales_data[raw_sales_data['经销商名称'].isin(normal_customers)]

        # 只保留销售订单（MT + TT）
        sales_data = raw_sales_data[
            raw_sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

        # 筛选当年数据
        sales_data = filter_current_year_data(sales_data)

        if sales_data.empty:
            st.error("❌ 当年没有销售订单数据")
            st.info("请检查数据中是否包含当年的销售数据")
            st.stop()

        # 分离MT/TT渠道数据
        mt_data, tt_data = get_sales_by_channel(sales_data)

        # 计算销售达成率
        current_year_targets = filter_current_year_data(sales_targets) if not sales_targets.empty else pd.DataFrame()
        current_year_tt_targets = filter_current_year_data(tt_targets) if not tt_targets.empty else pd.DataFrame()

        all_achievement_data = calculate_achievement_rate(sales_data, current_year_targets)
        mt_achievement_data = calculate_achievement_rate(mt_data, current_year_targets)
        tt_achievement_data = calculate_achievement_rate(tt_data, current_year_tt_targets)

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["全渠道分析", "MT渠道分析", "TT渠道分析"])

    # 全渠道分析标签页
    with tab1:
        # 创建KPI指标卡片
        create_kpi_metrics(sales_data, "全渠道")

        # 创建区域分析
        create_regional_analysis(sales_data, "全渠道", all_achievement_data)

        # 创建销售员分析
        create_salesperson_analysis(sales_data, "全渠道", all_achievement_data)

        # 创建季度分析
        create_quarterly_analysis(sales_data, "全渠道", all_achievement_data)

        # 创建月度分析
        create_monthly_analysis(sales_data, "全渠道", all_achievement_data)

    # MT渠道分析标签页
    with tab2:
        if not mt_data.empty:
            # 创建KPI指标卡片
            create_kpi_metrics(mt_data, "MT渠道")

            # 创建区域分析
            create_regional_analysis(mt_data, "MT渠道", mt_achievement_data)

            # 创建销售员分析
            create_salesperson_analysis(mt_data, "MT渠道", mt_achievement_data)

            # 创建季度分析
            create_quarterly_analysis(mt_data, "MT渠道", mt_achievement_data)

            # 创建月度分析
            create_monthly_analysis(mt_data, "MT渠道", mt_achievement_data)
        else:
            st.warning("⚠️ 没有MT渠道数据")

    # TT渠道分析标签页
    with tab3:
        if not tt_data.empty:
            # 创建KPI指标卡片
            create_kpi_metrics(tt_data, "TT渠道")

            # 创建区域分析
            create_regional_analysis(tt_data, "TT渠道", tt_achievement_data)

            # 创建销售员分析
            create_salesperson_analysis(tt_data, "TT渠道", tt_achievement_data)

            # 创建季度分析
            create_quarterly_analysis(tt_data, "TT渠道", tt_achievement_data)

            # 创建月度分析
            create_monthly_analysis(tt_data, "TT渠道", tt_achievement_data)
        else:
            st.warning("⚠️ 没有TT渠道数据")


# 运行主程序
if __name__ == "__main__":
    main()