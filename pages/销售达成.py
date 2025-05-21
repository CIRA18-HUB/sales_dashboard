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

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售总览分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
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
        transition: all 0.3s ease;
        cursor: pointer;
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
    .low-accuracy {
        border: 2px solid #F44336;
        box-shadow: 0 0 8px #F44336;
    }
    .logo-container {
        position: absolute;
        top: 0.5rem;
        right: 1rem;
        z-index: 1000;
    }
    .logo-img {
        height: 40px;
    }
    .pagination-btn {
        background-color: #1f3867;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
        margin: 5px;
        cursor: pointer;
    }
    .pagination-btn:hover {
        background-color: #2c4f8f;
    }
    .pagination-info {
        display: inline-block;
        padding: 5px;
        margin: 5px;
    }
    .hover-info {
        background-color: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .slider-container {
        padding: 10px 0;
    }
    .highlight-product {
        font-weight: bold;
        background-color: #ffeb3b;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .recommendation-tag {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 5px;
    }
    .recommendation-increase {
        background-color: #4CAF50;
        color: white;
    }
    .recommendation-maintain {
        background-color: #FFC107;
        color: black;
    }
    .recommendation-decrease {
        background-color: #F44336;
        color: white;
    }
    .view-details-btn {
        background-color: #1f3867;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 5px 10px;
        font-size: 0.8rem;
        cursor: pointer;
        margin-top: 5px;
        width: 100%;
        text-align: center;
    }
    .view-details-btn:hover {
        background-color: #2c4f8f;
    }
    .tab-content {
        padding: 1rem 0;
    }
    /* 标签页内容区域样式 */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    /* 图表容器样式 */
    .chart-container {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态 - 用于标签页切换
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0


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
    return f"¥{int(value):,}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0.0%"
    return f"{value:.1f}%"


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 创建可点击卡片
def create_clickable_card(title, value, subtitle, target_tab, key_prefix):
    """创建可点击的卡片，点击后跳转到指定标签页"""

    # 使用st.container创建卡片容器
    container = st.container()

    with container:
        # 卡片内容
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">{title}</p>
            <p class="card-value">{value}</p>
            <p class="card-text">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

        # 隐藏在卡片底部的按钮
        if st.button(f"查看详情", key=f"btn_{key_prefix}_{target_tab}"):
            st.session_state.active_tab = target_tab
            st.experimental_rerun()


# 数据加载函数 - 修改为隐藏成功消息
@st.cache_data
def load_raw_sales_data(file_path="仪表盘原始数据.xlsx"):
    """加载原始销售数据"""
    try:
        actual_path = get_file_path(file_path)

        if not os.path.exists(actual_path):
            st.error(f"❌ 找不到文件: {file_path}")
            st.info("请确认文件已正确上传到GitHub仓库根目录")
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
            st.info(f"现有列: {', '.join(df.columns.tolist())}")
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

        # 不显示成功消息
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

        # 不显示成功消息
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

        # 不显示成功消息
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

        # 不显示成功消息
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
                # 不显示成功消息
                return product_codes
            except UnicodeDecodeError:
                continue

        st.warning(f"无法读取产品代码文件，编码问题")
        return []

    except Exception as e:
        st.warning(f"⚠️ 加载产品代码数据时出错: {str(e)}")
        return []


# 数据筛选和处理函数
def filter_sales_data(df, months=None, regions=None, products=None, customers=None, salespeople=None):
    """筛选销售数据"""
    if df.empty:
        return df

    filtered_df = df.copy()

    if months and len(months) > 0:
        try:
            month_dates = [pd.to_datetime(m, format='%Y-%m') for m in months]
            filtered_df = filtered_df[filtered_df['发运月份'].isin(month_dates)]
        except Exception as e:
            st.warning(f"月份筛选出错: {str(e)}")

    if regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df['所属区域'].isin(regions)]

    if products and len(products) > 0:
        filtered_df = filtered_df[filtered_df['产品代码'].isin(products)]

    if customers and len(customers) > 0:
        filtered_df = filtered_df[filtered_df['客户简称'].isin(customers)]

    if salespeople and len(salespeople) > 0:
        filtered_df = filtered_df[filtered_df['申请人'].isin(salespeople)]

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


# 创建概览页KPI卡片
def create_overview_cards(df, mt_data, tt_data, achievement_data=None, growth_data=None):
    """创建概览页的KPI卡片"""
    if df.empty:
        st.warning("❌ 没有数据可显示KPI")
        return

    try:
        # 计算总体KPI
        total_amount = df['求和项:金额（元）'].sum()
        total_quantity = df['求和项:数量（箱）'].sum()

        # 客户数和产品数
        unique_customers = df['客户简称'].nunique()
        unique_products = df['产品代码'].nunique()

        # 平均达成率
        avg_achievement = 0
        if achievement_data is not None and not achievement_data.empty:
            avg_achievement = achievement_data['达成率'].mean()

        # MT/TT渠道数据
        mt_amount = mt_data['求和项:金额（元）'].sum() if not mt_data.empty else 0
        mt_quantity = mt_data['求和项:数量（箱）'].sum() if not mt_data.empty else 0
        tt_amount = tt_data['求和项:金额（元）'].sum() if not tt_data.empty else 0
        tt_quantity = tt_data['求和项:数量（箱）'].sum() if not tt_data.empty else 0

        # 计算MT/TT渠道达成率
        mt_achievement = 0
        tt_achievement = 0
        if achievement_data is not None and not achievement_data.empty:
            mt_data_with_achievement = pd.merge(
                mt_data,
                achievement_data,
                left_on=['发运月份', '申请人'],
                right_on=['指标年月', '销售员'],
                how='inner'
            )
            if not mt_data_with_achievement.empty:
                mt_achievement = mt_data_with_achievement['达成率'].mean()

            tt_data_with_achievement = pd.merge(
                tt_data,
                achievement_data,
                left_on=['发运月份', '申请人'],
                right_on=['指标年月', '销售员'],
                how='inner'
            )
            if not tt_data_with_achievement.empty:
                tt_achievement = tt_data_with_achievement['达成率'].mean()

        # 获取成长率
        latest_mom_amount = 0
        latest_mom_quantity = 0
        latest_yoy_amount = 0

        if growth_data is not None and not growth_data.empty and len(growth_data) > 0:
            latest_data = growth_data.iloc[-1]
            latest_mom_amount = latest_data.get('销售额环比增长率', 0)
            latest_mom_quantity = latest_data.get('销售量环比增长率', 0)
            latest_yoy_amount = latest_data.get('销售额同比增长率', 0)

        # 第一行：销售总量和达成率
        st.markdown("### 总体销售业绩")
        col1, col2, col3 = st.columns(3)

        with col1:
            create_clickable_card(
                "总销售额",
                format_currency(total_amount),
                "本期累计销售",
                1,  # 跳转到第二个标签页（销售达成分析）
                "sales_total"
            )

        with col2:
            create_clickable_card(
                "总销售量",
                f"{format_number(total_quantity)}箱",
                "本期累计销量",
                1,
                "quantity_total"
            )

        with col3:
            create_clickable_card(
                "平均达成率",
                format_percentage(avg_achievement),
                "销售目标完成度",
                1,
                "achievement_total"
            )

        # 第二行：渠道分析
        st.markdown("### 渠道销售分析")
        col1, col2 = st.columns(2)

        with col1:
            create_clickable_card(
                "MT渠道达成率",
                format_percentage(mt_achievement),
                f"MT渠道销售额: {format_currency(mt_amount)}",
                2,  # 跳转到第三个标签页（渠道分析）
                "mt_achievement"
            )

        with col2:
            create_clickable_card(
                "TT渠道达成率",
                format_percentage(tt_achievement),
                f"TT渠道销售额: {format_currency(tt_amount)}",
                2,
                "tt_achievement"
            )

        # 第三行：成长分析
        st.markdown("### 销售成长分析")
        col1, col2, col3 = st.columns(3)

        with col1:
            create_clickable_card(
                "销售额环比增长",
                format_percentage(latest_mom_amount),
                "相比上月变化",
                3,  # 跳转到第四个标签页（成长分析）
                "mom_amount"
            )

        with col2:
            create_clickable_card(
                "销售量环比增长",
                format_percentage(latest_mom_quantity),
                "相比上月变化",
                3,
                "mom_quantity"
            )

        with col3:
            create_clickable_card(
                "销售额同比增长",
                format_percentage(latest_yoy_amount),
                "相比去年同期",
                3,
                "yoy_amount"
            )

    except Exception as e:
        st.error(f"❌ 创建概览KPI卡片时出错: {str(e)}")


def create_achievement_analysis(achievement_data):
    """创建销售达成分析图表"""
    if achievement_data is None or achievement_data.empty:
        st.warning("⚠️ 没有销售达成数据可显示")
        return

    try:
        st.markdown('<div class="sub-header">📊 销售达成分析</div>', unsafe_allow_html=True)

        # 按月度显示达成率趋势
        monthly_achievement = achievement_data.groupby('指标年月').agg({
            '达成率': 'mean',
            '求和项:金额（元）': 'sum',
            '月度指标': 'sum'
        }).reset_index()

        if monthly_achievement.empty:
            st.warning("没有月度达成数据")
            return

        col1, col2 = st.columns([2, 1])

        with col1:
            # 月度销售达成率趋势图
            fig = go.Figure()

            # 添加达成率线
            fig.add_trace(go.Scatter(
                x=monthly_achievement['指标年月'],
                y=monthly_achievement['达成率'],
                mode='lines+markers',
                name='月度达成率',
                line=dict(color='#1f3867', width=3),
                marker=dict(size=8)
            ))

            # 添加100%基准线
            fig.add_hline(y=100, line_dash="dash", line_color="red",
                          annotation_text="目标线(100%)")

            fig.update_layout(
                title='月度销售达成率趋势',
                xaxis_title='月份',
                yaxis_title='达成率 (%)',
                plot_bgcolor='white',
                hovermode='x',
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 实际销售额与目标对比
            fig_target = go.Figure()

            fig_target.add_trace(go.Bar(
                x=monthly_achievement['指标年月'],
                y=monthly_achievement['求和项:金额（元）'],
                name='实际销售额',
                marker_color='#1f3867'
            ))

            fig_target.add_trace(go.Bar(
                x=monthly_achievement['指标年月'],
                y=monthly_achievement['月度指标'],
                name='销售目标',
                marker_color='#2c4f8f'
            ))

            fig_target.update_layout(
                title='实际销售额与目标对比',
                xaxis_title='月份',
                yaxis_title='销售额 (元)',
                barmode='group',
                plot_bgcolor='white',
                height=450
            )

            st.plotly_chart(fig_target, use_container_width=True)

        # 按区域显示达成率
        if '所属大区' in achievement_data.columns:
            regional_achievement = achievement_data.groupby('所属大区').agg({
                '达成率': 'mean'
            }).reset_index().sort_values('达成率', ascending=True)

            if not regional_achievement.empty:
                fig_region = px.bar(
                    regional_achievement,
                    x='达成率',
                    y='所属大区',
                    orientation='h',
                    title='各区域销售达成率',
                    color='达成率',
                    color_continuous_scale='Blues',
                    height=400
                )

                fig_region.update_layout(
                    plot_bgcolor='white',
                    xaxis_title='达成率 (%)'
                )

                # 添加100%基准线
                fig_region.add_vline(x=100, line_dash="dash", line_color="red")

                st.plotly_chart(fig_region, use_container_width=True)

        # 动态解读
        avg_achievement = monthly_achievement['达成率'].mean()
        best_month = monthly_achievement.loc[monthly_achievement['达成率'].idxmax()]
        worst_month = monthly_achievement.loc[monthly_achievement['达成率'].idxmin()]

        explanation = f"""
        <b>图表解读：</b> 月度销售达成率平均为{avg_achievement:.1f}%。
        最佳表现月份为{best_month['指标年月'].strftime('%Y年%m月')}，达成率{best_month['达成率']:.1f}%；
        最低表现月份为{worst_month['指标年月'].strftime('%Y年%m月')}，达成率{worst_month['达成率']:.1f}%。
        """

        if avg_achievement >= 100:
            explanation += "<br><b>业绩表现：</b> 整体达成情况良好，继续保持。"
        elif avg_achievement >= 80:
            explanation += "<br><b>业绩表现：</b> 达成情况基本符合预期，仍有提升空间。"
        else:
            explanation += "<br><b>业绩表现：</b> 达成率偏低，需要加强销售推进力度。"

        add_chart_explanation(explanation)

    except Exception as e:
        st.error(f"❌ 创建销售达成分析时出错: {str(e)}")


def create_channel_analysis(mt_data, tt_data, achievement_data=None, growth_data=None):
    """创建MT/TT渠道对比分析"""
    try:
        st.markdown('<div class="sub-header">🔄 MT/TT渠道对比分析</div>', unsafe_allow_html=True)

        # 计算渠道汇总数据
        mt_amount = mt_data['求和项:金额（元）'].sum() if not mt_data.empty else 0
        mt_quantity = mt_data['求和项:数量（箱）'].sum() if not mt_data.empty else 0
        tt_amount = tt_data['求和项:金额（元）'].sum() if not tt_data.empty else 0
        tt_quantity = tt_data['求和项:数量（箱）'].sum() if not tt_data.empty else 0

        # 检查是否有数据
        if mt_amount == 0 and tt_amount == 0:
            st.warning("⚠️ 没有MT/TT渠道销售数据")
            return

        # 第一行：渠道占比分析
        st.markdown("#### 渠道分布")
        col1, col2 = st.columns(2)

        # 渠道占比饼图
        channel_data = pd.DataFrame({
            '渠道': ['MT渠道', 'TT渠道'],
            '销售额': [mt_amount, tt_amount],
            '销售量': [mt_quantity, tt_quantity]
        })

        with col1:
            if mt_amount > 0 or tt_amount > 0:
                fig_amount = px.pie(
                    channel_data,
                    values='销售额',
                    names='渠道',
                    title='销售额渠道分布',
                    color_discrete_map={'MT渠道': '#1f3867', 'TT渠道': '#4c78a8'},
                    height=350
                )
                fig_amount.update_layout(plot_bgcolor='white')
                st.plotly_chart(fig_amount, use_container_width=True)
            else:
                st.info("没有销售额数据")

        with col2:
            if mt_quantity > 0 or tt_quantity > 0:
                fig_quantity = px.pie(
                    channel_data,
                    values='销售量',
                    names='渠道',
                    title='销售量渠道分布',
                    color_discrete_map={'MT渠道': '#1f3867', 'TT渠道': '#4c78a8'},
                    height=350
                )
                fig_quantity.update_layout(plot_bgcolor='white')
                st.plotly_chart(fig_quantity, use_container_width=True)
            else:
                st.info("没有销售量数据")

        # 第二行：月度趋势对比
        st.markdown("#### 月度趋势")

        combined_monthly = pd.DataFrame()

        if not mt_data.empty:
            mt_monthly = mt_data.groupby('发运月份').agg({
                '求和项:金额（元）': 'sum'
            }).reset_index()
            mt_monthly['渠道'] = 'MT渠道'
            combined_monthly = pd.concat([combined_monthly, mt_monthly])

        if not tt_data.empty:
            tt_monthly = tt_data.groupby('发运月份').agg({
                '求和项:金额（元）': 'sum'
            }).reset_index()
            tt_monthly['渠道'] = 'TT渠道'
            combined_monthly = pd.concat([combined_monthly, tt_monthly])

        if not combined_monthly.empty:
            # 渠道月度趋势
            fig_trend = px.line(
                combined_monthly,
                x='发运月份',
                y='求和项:金额（元）',
                color='渠道',
                title='MT/TT渠道月度销售趋势',
                color_discrete_map={'MT渠道': '#1f3867', 'TT渠道': '#4c78a8'},
                height=400
            )
            fig_trend.update_layout(
                plot_bgcolor='white',
                xaxis_title='月份',
                yaxis_title='销售额 (元)'
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # 如果有成长率数据，添加渠道环比增长对比
            if growth_data is not None and not growth_data.empty:
                col1, col2 = st.columns(2)

                # MT渠道增长率
                mt_growth = calculate_growth_rate(mt_data)
                if not mt_growth.empty and len(mt_growth) > 1:
                    with col1:
                        fig_mt_growth = px.line(
                            mt_growth,
                            x='发运月份',
                            y='销售额环比增长率',
                            title='MT渠道销售额环比增长',
                            line_shape='linear',
                            height=350
                        )
                        fig_mt_growth.update_layout(
                            plot_bgcolor='white',
                            yaxis_title='环比增长率 (%)'
                        )
                        fig_mt_growth.add_hline(y=0, line_dash="dash", line_color="gray")
                        st.plotly_chart(fig_mt_growth, use_container_width=True)

                # TT渠道增长率
                tt_growth = calculate_growth_rate(tt_data)
                if not tt_growth.empty and len(tt_growth) > 1:
                    with col2:
                        fig_tt_growth = px.line(
                            tt_growth,
                            x='发运月份',
                            y='销售额环比增长率',
                            title='TT渠道销售额环比增长',
                            line_shape='linear',
                            height=350
                        )
                        fig_tt_growth.update_layout(
                            plot_bgcolor='white',
                            yaxis_title='环比增长率 (%)'
                        )
                        fig_tt_growth.add_hline(y=0, line_dash="dash", line_color="gray")
                        st.plotly_chart(fig_tt_growth, use_container_width=True)

        # 动态解读
        total_amount = mt_amount + tt_amount
        if total_amount > 0:
            mt_percentage = (mt_amount / total_amount * 100)
            tt_percentage = (tt_amount / total_amount * 100)

            explanation = f"""
            <b>图表解读：</b> MT渠道贡献销售额{format_currency(mt_amount)}，占比{mt_percentage:.1f}%；
            TT渠道贡献销售额{format_currency(tt_amount)}，占比{tt_percentage:.1f}%。
            """

            if mt_percentage > 70:
                explanation += "<br><b>渠道建议：</b> MT渠道为主导，建议强化TT渠道发展以平衡渠道结构。"
            elif tt_percentage > 70:
                explanation += "<br><b>渠道建议：</b> TT渠道为主导，建议加强MT渠道布局以扩大市场覆盖。"
            else:
                explanation += "<br><b>渠道建议：</b> 双渠道发展相对均衡，继续保持协调发展策略。"

            add_chart_explanation(explanation)

    except Exception as e:
        st.error(f"❌ 创建渠道分析时出错: {str(e)}")


def create_growth_analysis(growth_data):
    """创建成长分析图表"""
    if growth_data.empty:
        st.warning("⚠️ 没有足够的历史数据进行成长分析")
        return

    try:
        st.markdown('<div class="sub-header">📈 销售成长分析</div>', unsafe_allow_html=True)

        # 环比增长率图表
        st.markdown("#### 环比增长分析")

        if '销售额环比增长率' in growth_data.columns:
            # 使用两列布局
            col1, col2 = st.columns(2)

            with col1:
                # 销售额环比增长率
                valid_growth_data = growth_data.dropna(subset=['销售额环比增长率'])
                if not valid_growth_data.empty:
                    fig_mom_sales = px.line(
                        valid_growth_data,
                        x='发运月份',
                        y='销售额环比增长率',
                        title='销售额环比增长率趋势',
                        markers=True,
                        color_discrete_sequence=['#1f3867'],
                        height=350
                    )
                    fig_mom_sales.update_layout(
                        plot_bgcolor='white',
                        yaxis_title='环比增长率 (%)'
                    )
                    fig_mom_sales.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig_mom_sales, use_container_width=True)

            with col2:
                # 销售量环比增长率
                valid_quantity_data = growth_data.dropna(subset=['销售量环比增长率'])
                if not valid_quantity_data.empty:
                    fig_mom_quantity = px.line(
                        valid_quantity_data,
                        x='发运月份',
                        y='销售量环比增长率',
                        title='销售量环比增长率趋势',
                        markers=True,
                        color_discrete_sequence=['#4c78a8'],
                        height=350
                    )
                    fig_mom_quantity.update_layout(
                        plot_bgcolor='white',
                        yaxis_title='环比增长率 (%)'
                    )
                    fig_mom_quantity.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig_mom_quantity, use_container_width=True)

        # 同比增长率图表（如果有数据）
        if '销售额同比增长率' in growth_data.columns:
            st.markdown("#### 同比增长分析")

            col1, col2 = st.columns(2)

            with col1:
                # 销售额同比增长率
                yoy_data = growth_data.dropna(subset=['销售额同比增长率'])
                if not yoy_data.empty:
                    fig_yoy_sales = px.line(
                        yoy_data,
                        x='发运月份',
                        y='销售额同比增长率',
                        title='销售额同比增长率趋势',
                        markers=True,
                        color_discrete_sequence=['#2E8B57'],
                        height=350
                    )
                    fig_yoy_sales.update_layout(
                        plot_bgcolor='white',
                        yaxis_title='同比增长率 (%)'
                    )
                    fig_yoy_sales.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig_yoy_sales, use_container_width=True)

            with col2:
                # 销售量同比增长率
                yoy_quantity_data = growth_data.dropna(subset=['销售量同比增长率'])
                if not yoy_quantity_data.empty:
                    fig_yoy_quantity = px.line(
                        yoy_quantity_data,
                        x='发运月份',
                        y='销售量同比增长率',
                        title='销售量同比增长率趋势',
                        markers=True,
                        color_discrete_sequence=['#FF6347'],
                        height=350
                    )
                    fig_yoy_quantity.update_layout(
                        plot_bgcolor='white',
                        yaxis_title='同比增长率 (%)'
                    )
                    fig_yoy_quantity.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig_yoy_quantity, use_container_width=True)

        # 月度销售趋势
        st.markdown("#### 销售额和销售量趋势")

        # 创建双Y轴图表
        fig_trends = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加销售额线
        fig_trends.add_trace(
            go.Scatter(
                x=growth_data['发运月份'],
                y=growth_data['求和项:金额（元）'],
                name='销售额',
                line=dict(color='#1f3867', width=3)
            ),
            secondary_y=False
        )

        # 添加销售量线
        fig_trends.add_trace(
            go.Scatter(
                x=growth_data['发运月份'],
                y=growth_data['求和项:数量（箱）'],
                name='销售量(箱)',
                line=dict(color='#FF6347', width=3)
            ),
            secondary_y=True
        )

        # 更新布局
        fig_trends.update_layout(
            title='月度销售额与销售量趋势',
            plot_bgcolor='white',
            hovermode='x',
            height=400
        )

        # 更新X轴
        fig_trends.update_xaxes(title_text='月份')

        # 更新Y轴
        fig_trends.update_yaxes(title_text='销售额 (元)', secondary_y=False)
        fig_trends.update_yaxes(title_text='销售量 (箱)', secondary_y=True)

        st.plotly_chart(fig_trends, use_container_width=True)

        # 动态解读
        if len(growth_data) > 0:
            latest_data = growth_data.iloc[-1]
            explanation = f"""
            <b>图表解读：</b> 最新月份({latest_data['发运月份'].strftime('%Y年%m月')})
            销售额环比增长{latest_data.get('销售额环比增长率', 0):.1f}%，
            销售量环比增长{latest_data.get('销售量环比增长率', 0):.1f}%。
            """

            growth_rate = latest_data.get('销售额环比增长率', 0)
            if pd.notna(growth_rate):
                if growth_rate > 5:
                    explanation += "<br><b>增长趋势：</b> 销售额增长强劲，业务发展势头良好。"
                elif growth_rate > 0:
                    explanation += "<br><b>增长趋势：</b> 销售额保持正增长，发展稳健。"
                else:
                    explanation += "<br><b>增长趋势：</b> 销售额出现下降，需要关注市场变化。"

            add_chart_explanation(explanation)

    except Exception as e:
        st.error(f"❌ 创建成长分析时出错: {str(e)}")


# 主程序开始
def main():
    """主程序"""
    try:
        # 标题
        st.markdown('<div class="main-header">销售总览分析仪表盘</div>', unsafe_allow_html=True)

        # 数据加载 - 静默加载，不显示成功消息
        with st.spinner('🔄 正在加载数据...'):
            # 加载所有必需数据
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

        if sales_data.empty:
            st.error("❌ 筛选后没有销售订单数据")
            st.info("请检查数据中是否包含 '订单-正常产品' 或 '订单-TT产品' 类型的订单")
            st.stop()

        # 侧边栏筛选器 - 应用到所有标签页
        st.sidebar.header("📊 数据筛选")

        # 获取可用的筛选选项
        current_year = datetime.now().year
        available_months = sorted(sales_data['发运月份'].dt.strftime('%Y-%m').unique())
        available_regions = sorted(sales_data['所属区域'].unique())
        available_products = sorted(sales_data['产品简称'].unique())
        available_customers = sorted(sales_data['客户简称'].unique())
        available_salespeople = sorted(sales_data['申请人'].unique())

        # 默认选择当年数据
        default_months = [m for m in available_months if m.startswith(str(current_year))]

        with st.sidebar.expander("筛选条件", expanded=True):
            selected_months = st.multiselect(
                "选择月份",
                options=available_months,
                default=default_months if default_months else available_months[-6:],
                key="sales_months"
            )

            selected_regions = st.multiselect(
                "选择区域",
                options=available_regions,
                default=available_regions,
                key="sales_regions"
            )

            selected_products = st.multiselect(
                "选择产品",
                options=available_products,
                default=[],
                key="sales_products"
            )

            selected_customers = st.multiselect(
                "选择客户",
                options=available_customers,
                default=[],
                key="sales_customers"
            )

            selected_salespeople = st.multiselect(
                "选择销售员",
                options=available_salespeople,
                default=[],
                key="sales_salespeople"
            )

        # 应用筛选条件
        filtered_sales_data = filter_sales_data(
            sales_data,
            months=selected_months,
            regions=selected_regions,
            products=selected_products if selected_products else None,
            customers=selected_customers if selected_customers else None,
            salespeople=selected_salespeople if selected_salespeople else None
        )

        # 检查筛选后是否有数据
        if filtered_sales_data.empty:
            st.warning("⚠️ 根据当前筛选条件没有找到数据，请调整筛选条件")
            st.stop()

        # 分离MT/TT渠道数据
        mt_data, tt_data = get_sales_by_channel(filtered_sales_data)

        # 计算销售达成率
        achievement_data = calculate_achievement_rate(filtered_sales_data, sales_targets)

        # 计算成长率
        growth_data = calculate_growth_rate(filtered_sales_data)

        # 创建标签页
        tab_names = ["销售概览", "销售达成分析", "渠道分析", "成长分析"]
        tabs = st.tabs(tab_names)

        # 处理标签页切换
        if 'active_tab' in st.session_state:
            active_tab = st.session_state.active_tab
        else:
            active_tab = 0

        # 销售概览标签页
        with tabs[0]:
            if active_tab == 0:
                create_overview_cards(filtered_sales_data, mt_data, tt_data, achievement_data, growth_data)

        # 销售达成分析标签页
        with tabs[1]:
            if active_tab == 1:
                if not achievement_data.empty:
                    create_achievement_analysis(achievement_data)
                else:
                    st.info("ℹ️ 暂无销售目标数据，无法显示达成分析")

        # 渠道分析标签页
        with tabs[2]:
            if active_tab == 2:
                create_channel_analysis(mt_data, tt_data, achievement_data, growth_data)

        # 成长分析标签页
        with tabs[3]:
            if active_tab == 3:
                create_growth_analysis(growth_data)

        # 根据激活的标签自动点击相应的标签页
        if active_tab > 0:
            js = f"""
            <script>
                var tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                if (tabs.length >= {active_tab + 1}) {{
                    tabs[{active_tab}].click();
                }}
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
            # 重置标签页索引，避免循环点击
            st.session_state.active_tab = active_tab

        # 页脚信息
        st.markdown("---")
        st.markdown(f"**数据更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(
            "**数据说明：** 本报告基于销售订单数据生成，包含MT渠道（订单-正常产品）和TT渠道（订单-TT产品）的销售情况。")

    except Exception as e:
        st.error(f"❌ 应用运行出错: {str(e)}")
        st.info("请检查数据文件是否存在且格式正确")


# 运行主程序
if __name__ == "__main__":
    main()