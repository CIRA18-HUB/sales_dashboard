# pages/inventory_page.py - 库存分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import math
import glob
import warnings
import logging
from pathlib import Path

# 配置日志系统
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('库存分析')

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="库存分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 与预测与计划.py保持一致
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
        position: relative;
    }
    .view-details-btn {
        position: absolute;
        bottom: 5px;
        right: 10px;
        background-color: #1f3867;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 2px 8px;
        font-size: 0.7rem;
        cursor: pointer;
    }
    .view-details-btn:hover {
        background-color: #4c78a8;
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
    .time-dim-note {
        font-size: 0.85rem;
        color: #6c757d;
        font-style: italic;
        margin-top: 0.3rem;
        margin-bottom: 0.7rem;
    }
    .empty-chart-message {
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        background-color: rgba(0,0,0,0.03);
        border-radius: 10px;
        margin: 1rem 0;
        padding: 20px;
    }
    .empty-chart-message h3 {
        color: #6c757d;
        margin-bottom: 10px;
    }
    .empty-chart-message p {
        color: #6c757d;
        text-align: center;
        max-width: 80%;
    }
    .data-search-info {
        font-size: 0.85rem;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #6c757d;
    }
    .file-info {
        margin-top: 0.25rem;
        font-size: 0.8rem;
    }
    .error-box {
        background-color: rgba(244, 67, 54, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 0.5rem solid #F44336;
    }
    .success-box {
        background-color: rgba(76, 175, 80, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 0.5rem solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<div class="main-header">📦 库存分析</div>', unsafe_allow_html=True)

# 全局常量定义
COLORS = {
    'primary': '#1f3867',
    'secondary': '#4c78a8',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'gray': '#6c757d'
}

INVENTORY_RISK_COLORS = {
    '极高风险': '#8B0000',  # 深红色
    '高风险': '#FF0000',  # 红色
    '中风险': '#FFA500',  # 橙色
    '低风险': '#4CAF50',  # 绿色
    '极低风险': '#2196F3'  # 蓝色
}

# 库存配置参数
INVENTORY_CONFIG = {
    'high_stock_days': 90,  # 库存超过90天视为高风险
    'medium_stock_days': 60,  # 库存超过60天视为中风险
    'low_stock_days': 30,  # 库存超过30天视为低风险
    'min_daily_sales': 0.1,  # 最小日均销量阈值
    'annual_capital_cost': 0.12,  # 年化资金成本率 (12%)
    'stagnant_days_threshold': 60  # 超过60天的批次视为呆滞库存
}


# ==================== 1. 格式化函数 ====================
def format_currency(value):
    """格式化货币"""
    return f"¥{value:,.2f}" if pd.notna(value) else "¥0.00"


def format_percentage(value):
    """格式化百分比"""
    return f"{value:.1f}%" if pd.notna(value) else "0.0%"


def format_number(value):
    """格式化数量"""
    return f"{int(value):,}" if pd.notna(value) else "0"


def format_days(value):
    """格式化天数"""
    if pd.isna(value) or value == float('inf'):
        return "∞"
    return f"{value:.1f}天"


# ==================== 2. 库存数据加载与处理函数 - 完全重写 ====================
def find_data_files(file_patterns, search_dirs=None):
    """查找匹配的数据文件

    Args:
        file_patterns: 文件名模式列表，如['*库存*.xlsx', '*出货*.xlsx']
        search_dirs: 要搜索的目录列表，默认为当前目录和相关子目录

    Returns:
        dict: 键为模式，值为找到的第一个匹配文件路径
    """
    if search_dirs is None:
        # 默认搜索目录：当前目录、pages目录、data目录和上级目录
        base_dir = os.getcwd()
        search_dirs = [
            base_dir,
            os.path.join(base_dir, "pages"),
            os.path.join(base_dir, "data"),
            os.path.dirname(base_dir)
        ]

    found_files = {}

    # 记录搜索过的文件总数
    total_files_searched = 0

    for pattern in file_patterns:
        found_files[pattern] = None

        for directory in search_dirs:
            if not os.path.exists(directory):
                continue

            # 在每个目录中搜索
            search_path = os.path.join(directory, pattern)
            matching_files = glob.glob(search_path)
            total_files_searched += len(matching_files)

            # 如果找到匹配的文件，选择最新的一个
            if matching_files:
                newest_file = max(matching_files, key=os.path.getmtime)
                found_files[pattern] = newest_file
                break

    # 记录找到了多少文件
    found_count = sum(1 for f in found_files.values() if f is not None)

    logger.info(f"搜索了{len(search_dirs)}个目录，扫描了{total_files_searched}个文件，找到{found_count}个匹配文件")

    return found_files


@st.cache_data
def load_inventory_data(show_details=False):
    """加载库存数据 - 更灵活的文件查找和错误处理"""
    try:
        # 需要查找的文件模式
        file_patterns = [
            "*批次*库存*.xlsx",  # 库存数据
            "*出货数据*.xlsx",  # 出货数据
            "*人工预测*.xlsx",  # 预测数据
            "*单价*.xlsx"  # 单价数据
        ]

        # 查找匹配的文件
        found_files = find_data_files(file_patterns)

        # 显示数据文件信息
        if show_details:
            file_info = "<div class='data-search-info'>数据文件搜索结果：<ul>"
            for pattern, file_path in found_files.items():
                status = "✅ 已找到" if file_path else "❌ 未找到"
                file_info += f"<li>{pattern}: {status}"
                if file_path:
                    file_info += f" <span class='file-info'>({file_path}, 修改时间: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')})</span>"
                file_info += "</li>"
            file_info += "</ul></div>"
            st.markdown(file_info, unsafe_allow_html=True)

        # 检查是否找到了必要的库存数据文件
        inventory_file = found_files.get("*批次*库存*.xlsx")
        if not inventory_file:
            st.error("找不到库存数据文件，请确保文件名包含'批次'和'库存'字样，格式为Excel(.xlsx)")
            if show_details:
                st.info("提示：请检查文件是否位于应用目录、pages子目录或data子目录中")
            return None

        # 读取库存数据 - 增强的错误处理
        try:
            inventory_raw = pd.read_excel(inventory_file, header=0)
            logger.info(f"成功读取库存数据: {inventory_file}, 行数: {len(inventory_raw)}")
        except Exception as e:
            st.error(f"读取库存数据时出错: {str(e)}")
            st.info(f"请检查文件 {inventory_file} 的格式是否正确")
            return None

        # 通过分析数据结构处理数据
        # 首先检查数据结构
        if len(inventory_raw.columns) < 7:
            st.error(f"库存数据文件格式不正确: 只有{len(inventory_raw.columns)}列，至少需要7列")
            return None

        # 处理第一层数据（产品信息）- 使用更灵活的列检测
        product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
        inventory_data = product_rows.iloc[:, :7].copy()

        # 动态设置列名
        expected_cols = ['产品代码', '描述', '现有库存', '已分配量', '现有库存可订量', '待入库量', '本月剩余可订量']
        if len(inventory_data.columns) >= len(expected_cols):
            inventory_data.columns = expected_cols
        else:
            st.warning(f"库存数据列数不足，预期{len(expected_cols)}列，实际{len(inventory_data.columns)}列")
            # 尝试部分映射
            available_cols = min(len(inventory_data.columns), len(expected_cols))
            inventory_data.columns = expected_cols[:available_cols] + list(inventory_data.columns[available_cols:])

        # 处理第二层数据（批次信息）
        batch_rows = inventory_raw[inventory_raw.iloc[:, 7].notna()]
        if len(batch_rows) == 0:
            st.warning("库存数据中未找到批次信息，这将影响分析结果")
            batch_data = pd.DataFrame(columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量'])
        else:
            batch_data = batch_rows.iloc[:, 7:].copy()
            batch_cols = ['库位', '生产日期', '生产批号', '数量']
            batch_data.columns = batch_cols + list(batch_data.columns[len(batch_cols):])

            # 为批次数据添加产品代码
            product_code = None
            product_description = None
            batch_with_product = []

            for i, row in inventory_raw.iterrows():
                if pd.notna(row.iloc[0]):
                    # 这是产品行
                    product_code = row.iloc[0]
                    product_description = row.iloc[1] if len(row) > 1 else ""  # 获取产品描述
                elif pd.notna(row.iloc[7]) and product_code is not None:
                    # 这是批次行
                    batch_row = row.iloc[7:].copy()
                    batch_row_with_product = pd.Series([product_code, product_description] + batch_row.tolist())
                    batch_with_product.append(batch_row_with_product)

            if batch_with_product:
                batch_data = pd.DataFrame(batch_with_product)
                batch_cols = ['产品代码', '描述', '库位', '生产日期', '生产批号', '数量']
                batch_data.columns = batch_cols + list(batch_data.columns[len(batch_cols):])

                # 转换日期列 - 容错处理
                try:
                    batch_data['生产日期'] = pd.to_datetime(batch_data['生产日期'], errors='coerce')
                except Exception as e:
                    st.warning(f"转换生产日期时出错: {str(e)}，将使用当前日期代替")
                    batch_data['生产日期'] = datetime.now()
            else:
                batch_data = pd.DataFrame(columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量'])
                st.warning("无法提取批次信息，请检查数据格式")

        # 加载出货数据
        shipping_data = None
        shipping_file = found_files.get("*出货数据*.xlsx")
        if shipping_file:
            try:
                shipping_data = pd.read_excel(shipping_file)

                # 尝试自动检测列名
                if '产品代码' in shipping_data.columns and '数量' in shipping_data.columns:
                    required_cols = ['订单日期', '所属区域', '申请人', '产品代码', '数量']
                    missing_cols = [col for col in required_cols if col not in shipping_data.columns]

                    if missing_cols:
                        st.warning(f"出货数据缺少列: {', '.join(missing_cols)}，分析结果可能不准确")
                else:
                    # 假设标准格式
                    shipping_data.columns = ['订单日期', '所属区域', '申请人', '产品代码', '数量']

                shipping_data['订单日期'] = pd.to_datetime(shipping_data['订单日期'], errors='coerce')
                logger.info(f"成功读取出货数据: {shipping_file}, 行数: {len(shipping_data)}")
            except Exception as e:
                st.warning(f"读取出货数据时出错: {str(e)}，将影响销售分析结果")
                shipping_data = None

        # 加载预测数据
        forecast_data = None
        forecast_file = found_files.get("*人工预测*.xlsx")
        if forecast_file:
            try:
                forecast_data = pd.read_excel(forecast_file)

                # 尝试自动检测列名
                if '产品代码' in forecast_data.columns and '预计销售量' in forecast_data.columns:
                    # 使用现有列名
                    pass
                else:
                    # 假设标准格式
                    forecast_data.columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']

                # 尝试转换日期列
                try:
                    forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'], errors='coerce')
                except:
                    st.warning("转换预测数据日期时出错，将影响预测分析结果")

                logger.info(f"成功读取预测数据: {forecast_file}, 行数: {len(forecast_data)}")
            except Exception as e:
                st.warning(f"读取预测数据时出错: {str(e)}，将影响预测分析结果")
                forecast_data = None

        # 加载单价数据
        price_data = {}
        price_file = found_files.get("*单价*.xlsx")
        if price_file:
            try:
                price_df = pd.read_excel(price_file)

                # 检测列名
                if '产品代码' in price_df.columns and '单价' in price_df.columns:
                    for _, row in price_df.iterrows():
                        price_data[row['产品代码']] = row['单价']
                else:
                    # 尝试使用前两列
                    for _, row in price_df.iterrows():
                        if len(row) >= 2:
                            price_data[str(row.iloc[0])] = float(row.iloc[1])

                logger.info(f"成功读取单价数据: {price_file}, 产品数: {len(price_data)}")
            except Exception as e:
                st.warning(f"读取单价数据时出错: {str(e)}，将使用默认单价")
                price_data = {}

        # 如果未找到价格数据，使用默认价格
        if not price_data:
            # 从库存数据中，提取所有产品代码，设置默认价格
            for code in inventory_data['产品代码']:
                if code not in price_data:
                    price_data[code] = 150.0  # 默认价格

        return {
            'inventory_data': inventory_data,
            'batch_data': batch_data,
            'shipping_data': shipping_data,
            'forecast_data': forecast_data,
            'price_data': price_data
        }

    except Exception as e:
        logger.exception("加载库存数据时发生异常")
        st.error(f"数据加载过程中发生错误: {str(e)}")
        return None


@st.cache_data
def load_and_process_inventory_data(show_details=False):
    """加载并处理库存分析数据 - 不再使用示例数据"""
    try:
        with st.spinner("正在加载库存数据..."):
            data = load_inventory_data(show_details)

            if not data:
                st.error("无法加载库存数据，请检查数据文件路径和格式")
                return None

            if 'inventory_data' not in data or data['inventory_data'].empty:
                st.error("库存数据为空，请检查数据文件")
                return None

            # 分析数据
            with st.spinner("正在分析库存数据..."):
                analysis_result = analyze_inventory_data(data)
                data['analysis_result'] = analysis_result

            if not analysis_result:
                st.warning("数据分析结果为空，请检查数据质量")

            return data

    except Exception as e:
        logger.exception("处理库存数据时发生异常")
        st.error(f"数据处理失败: {str(e)}")
        return None


# ==================== 3. 库存筛选器 ====================
def create_inventory_filters(data):
    """创建库存页面专用筛选器"""
    if not data:
        return data

    # 初始化筛选状态
    if 'inv_filter_product' not in st.session_state:
        st.session_state.inv_filter_product = '全部'
    if 'inv_filter_risk' not in st.session_state:
        st.session_state.inv_filter_risk = '全部'
    if 'inv_filter_region' not in st.session_state:
        st.session_state.inv_filter_region = '全部'
    if 'inv_filter_person' not in st.session_state:
        st.session_state.inv_filter_person = '全部'

    with st.sidebar:
        st.markdown("## 🔍 库存筛选")
        st.markdown("---")

        # 产品代码筛选
        if 'batch_data' in data and not data['batch_data'].empty:
            all_products = ['全部'] + sorted(data['batch_data']['产品代码'].unique().tolist())
            selected_product = st.selectbox(
                "选择产品代码", all_products,
                index=all_products.index(
                    st.session_state.inv_filter_product) if st.session_state.inv_filter_product in all_products else 0,
                key="inv_product_filter"
            )
            st.session_state.inv_filter_product = selected_product

        # 风险等级筛选
        risk_levels = ['全部', '极高风险', '高风险', '中风险', '低风险', '极低风险']
        selected_risk = st.selectbox(
            "选择风险等级", risk_levels,
            index=risk_levels.index(
                st.session_state.inv_filter_risk) if st.session_state.inv_filter_risk in risk_levels else 0,
            key="inv_risk_filter"
        )
        st.session_state.inv_filter_risk = selected_risk

        # 责任区域筛选
        if 'shipping_data' in data and data['shipping_data'] is not None and not data['shipping_data'].empty:
            all_regions = ['全部'] + sorted(data['shipping_data']['所属区域'].unique().tolist())
            selected_region = st.selectbox(
                "选择责任区域", all_regions,
                index=all_regions.index(
                    st.session_state.inv_filter_region) if st.session_state.inv_filter_region in all_regions else 0,
                key="inv_region_filter"
            )
            st.session_state.inv_filter_region = selected_region

        # 责任人筛选
        if 'shipping_data' in data and data['shipping_data'] is not None and not data['shipping_data'].empty:
            all_persons = ['全部'] + sorted(data['shipping_data']['申请人'].unique().tolist())
            selected_person = st.selectbox(
                "选择责任人", all_persons,
                index=all_persons.index(
                    st.session_state.inv_filter_person) if st.session_state.inv_filter_person in all_persons else 0,
                key="inv_person_filter"
            )
            st.session_state.inv_filter_person = selected_person

        # 重置按钮
        if st.button("重置筛选条件", key="inv_reset_filters"):
            st.session_state.inv_filter_product = '全部'
            st.session_state.inv_filter_risk = '全部'
            st.session_state.inv_filter_region = '全部'
            st.session_state.inv_filter_person = '全部'
            st.rerun()

    return apply_inventory_filters(data)


def apply_inventory_filters(data):
    """应用库存筛选条件"""
    if not data or 'analysis_result' not in data:
        return data

    filtered_data = data.copy()

    # 应用筛选到批次分析结果
    if 'batch_analysis' in data['analysis_result']:
        batch_analysis = data['analysis_result']['batch_analysis'].copy()

        # 产品筛选
        if st.session_state.inv_filter_product != '全部':
            batch_analysis = batch_analysis[batch_analysis['产品代码'] == st.session_state.inv_filter_product]

        # 风险等级筛选
        if st.session_state.inv_filter_risk != '全部':
            batch_analysis = batch_analysis[batch_analysis['风险程度'] == st.session_state.inv_filter_risk]

        # 责任区域筛选
        if st.session_state.inv_filter_region != '全部':
            batch_analysis = batch_analysis[batch_analysis['责任区域'] == st.session_state.inv_filter_region]

        # 责任人筛选
        if st.session_state.inv_filter_person != '全部':
            batch_analysis = batch_analysis[batch_analysis['责任人'] == st.session_state.inv_filter_person]

        # 更新筛选后的数据
        filtered_data['analysis_result']['batch_analysis'] = batch_analysis

    return filtered_data


# ==================== 4. 辅助函数 ====================
def get_simplified_product_name(product_code, full_name):
    """将产品完整名称简化为更简短的格式"""
    if not full_name or not isinstance(full_name, str):
        return product_code

    # 如果符合"口力X-中国"格式，则简化
    if "口力" in full_name and "-中国" in full_name:
        # 去除"口力"前缀和"-中国"后缀
        return full_name.replace("口力", "").replace("-中国", "").strip()

    # 否则返回原始名称
    return full_name


def calculate_risk_percentage(days_to_clear, batch_age, target_days):
    """
    计算库存风险百分比

    参数:
    days_to_clear (float): 预计清库天数
    batch_age (int): 批次库龄（天数）
    target_days (int): 目标清库天数（30/60/90天）

    返回:
    float: 风险百分比，范围0-100
    """
    # 库龄已经超过目标天数，风险直接为100%
    if batch_age >= target_days:
        return 100.0

    # 无法清库情况
    if days_to_clear == float('inf'):
        return 100.0

    # 清库天数超过目标的3倍，风险为100%
    if days_to_clear >= 3 * target_days:
        return 100.0

    # 计算基于清库天数的风险
    clearance_ratio = days_to_clear / target_days
    clearance_risk = 100 / (1 + math.exp(-4 * (clearance_ratio - 1)))

    # 计算基于库龄的风险
    age_risk = 100 * batch_age / target_days

    # 组合风险 - 加权平均，更强调高风险因素
    combined_risk = 0.8 * max(clearance_risk, age_risk) + 0.2 * min(clearance_risk, age_risk)

    # 清库天数超过目标，风险至少为80%
    if days_to_clear > target_days:
        combined_risk = max(combined_risk, 80)

    # 清库天数超过目标的2倍，风险至少为90%
    if days_to_clear >= 2 * target_days:
        combined_risk = max(combined_risk, 90)

    # 库龄超过目标的75%，风险至少为75%
    if batch_age >= 0.75 * target_days:
        combined_risk = max(combined_risk, 75)

    return min(100, round(combined_risk, 1))


def calculate_inventory_risk_level(batch_age, days_to_clear, sales_volatility, forecast_bias):
    """
    计算库存风险等级

    参数:
    batch_age (int): 批次库龄（天数）
    days_to_clear (float): 预计清库天数
    sales_volatility (float): 销量波动系数
    forecast_bias (float): 预测偏差

    返回:
    str: 风险等级（极高风险/高风险/中风险/低风险/极低风险）
    """
    risk_score = 0

    # 库龄因素 (0-40分)
    if batch_age > 90:
        risk_score += 40
    elif batch_age > 60:
        risk_score += 30
    elif batch_age > 30:
        risk_score += 20
    else:
        risk_score += 10

    # 清库天数因素 (0-40分)
    if days_to_clear == float('inf'):
        risk_score += 40
    elif days_to_clear > 180:  # 半年以上
        risk_score += 35
    elif days_to_clear > 90:  # 3个月以上
        risk_score += 30
    elif days_to_clear > 60:  # 2个月以上
        risk_score += 20
    elif days_to_clear > 30:  # 1个月以上
        risk_score += 10

    # 销量波动系数 (0-10分)
    if sales_volatility > 2.0:
        risk_score += 10
    elif sales_volatility > 1.0:
        risk_score += 5

    # 预测偏差 (0-10分) - 使用绝对值评估偏差大小
    if abs(forecast_bias) > 0.5:  # 50%以上偏差
        risk_score += 10
    elif abs(forecast_bias) > 0.3:  # 30%以上偏差
        risk_score += 8
    elif abs(forecast_bias) > 0.15:  # 15%以上偏差
        risk_score += 5

    # 根据总分确定风险等级
    if risk_score >= 80:
        return "极高风险"
    elif risk_score >= 60:
        return "高风险"
    elif risk_score >= 40:
        return "中风险"
    elif risk_score >= 20:
        return "低风险"
    else:
        return "极低风险"


def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


def display_empty_chart_message(title, message):
    """显示空图表提示信息"""
    st.markdown(
        f'''
        <div class="empty-chart-message">
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
        ''',
        unsafe_allow_html=True
    )


# ==================== 5. 核心分析函数 ====================
def analyze_inventory_data(data):
    """分析库存数据，实现完整的业务逻辑"""
    try:
        if not data or 'inventory_data' not in data or data['inventory_data'].empty:
            return {}

        # 获取数据
        inventory_data = data['inventory_data']
        batch_data = data.get('batch_data', pd.DataFrame())
        shipping_data = data.get('shipping_data', pd.DataFrame())
        forecast_data = data.get('forecast_data', pd.DataFrame())
        price_data = data.get('price_data', {})

        # 计算基础指标
        total_inventory = inventory_data['现有库存'].sum() if '现有库存' in inventory_data.columns else 0

        # 计算库存总价值
        total_inventory_value = 0
        for _, row in inventory_data.iterrows():
            code = row['产品代码']
            qty = row['现有库存']
            price = price_data.get(code, 150.0)  # 默认价格
            total_inventory_value += qty * price

        # 批次级别分析
        batch_analysis = None
        if not batch_data.empty:
            batch_analysis = analyze_batch_level_data(batch_data, shipping_data, forecast_data, price_data)

        # 计算库存周转率和周转天数
        inventory_turnover, inventory_turnover_days = calculate_inventory_turnover(
            inventory_data, shipping_data, 90, price_data  # 使用90天的销售数据
        )

        # 计算呆滞库存比例
        stagnant_ratio, stagnant_value = calculate_stagnant_inventory(batch_analysis, price_data, total_inventory_value)

        # 计算库存资金占用成本
        annual_rate = INVENTORY_CONFIG['annual_capital_cost']  # 年化资金成本率
        daily_rate = annual_rate / 365
        capital_cost = total_inventory_value * annual_rate / 12  # 月化成本

        # 计算健康分布
        health_distribution = {}
        risk_distribution = {}

        if batch_analysis is not None and not batch_analysis.empty:
            # 根据风险程度统计
            risk_counts = batch_analysis['风险程度'].value_counts().to_dict()
            risk_distribution = risk_counts

            # 转换为健康分布
            extreme_high = risk_counts.get('极高风险', 0)
            high = risk_counts.get('高风险', 0)
            medium = risk_counts.get('中风险', 0)
            low = risk_counts.get('低风险', 0)
            extreme_low = risk_counts.get('极低风险', 0)

            health_distribution = {
                '库存过剩': extreme_high + high,
                '库存健康': medium + low,
                '库存不足': extreme_low
            }

        return {
            'total_inventory': total_inventory,
            'total_inventory_value': total_inventory_value,
            'inventory_turnover': inventory_turnover,
            'inventory_turnover_days': inventory_turnover_days,
            'stagnant_ratio': stagnant_ratio,
            'stagnant_value': stagnant_value,
            'capital_cost': capital_cost,
            'health_distribution': health_distribution,
            'risk_distribution': risk_distribution,
            'batch_analysis': batch_analysis
        }

    except Exception as e:
        logger.exception("库存分析出错")
        st.error(f"库存分析出错: {str(e)}")
        return {}


def calculate_inventory_turnover(inventory_data, shipping_data, days_period, price_data):
    """计算库存周转率和周转天数"""
    try:
        # 库存周转率 = 一段时间内的销售成本 / 平均库存价值
        # 这里简化为：周期内销售量 / 当前库存量

        if inventory_data.empty or shipping_data is None or shipping_data.empty:
            return 0.0, float('inf')

        # 计算当前库存总价值
        current_inventory_value = 0
        for _, row in inventory_data.iterrows():
            code = row['产品代码']
            qty = row['现有库存']
            price = price_data.get(code, 150.0)  # 默认价格
            current_inventory_value += qty * price

        if current_inventory_value == 0:
            return 0.0, float('inf')

        # 计算周期内的销售总价值
        today = datetime.now().date()
        period_start = today - timedelta(days=days_period)

        period_sales_value = 0
        period_shipping = shipping_data[shipping_data['订单日期'].dt.date >= period_start]

        for _, row in period_shipping.iterrows():
            code = row['产品代码']
            qty = row['数量']
            price = price_data.get(code, 150.0)  # 默认价格
            period_sales_value += qty * price

        # 年化周转率 = (周期销售额 / 周期天数) * 365 / 当前库存值
        annual_turnover = (period_sales_value / days_period) * 365 / current_inventory_value

        # 周转天数 = 365 / 周转率
        turnover_days = 365 / annual_turnover if annual_turnover > 0 else float('inf')

        return annual_turnover, turnover_days

    except Exception as e:
        logger.exception("计算库存周转出错")
        print(f"计算库存周转出错: {str(e)}")
        return 0.0, float('inf')


def calculate_stagnant_inventory(batch_analysis, price_data, total_inventory_value):
    """计算呆滞库存比例和价值"""
    try:
        if batch_analysis is None or batch_analysis.empty or total_inventory_value == 0:
            return 0.0, 0.0

        # 定义呆滞库存：库龄超过60天的批次
        stagnant_days = INVENTORY_CONFIG['stagnant_days_threshold']
        stagnant_batches = batch_analysis[batch_analysis['库龄'] > stagnant_days]

        if stagnant_batches.empty:
            return 0.0, 0.0

        # 计算呆滞库存价值
        stagnant_value = stagnant_batches['批次价值'].sum()

        # 计算呆滞比例
        stagnant_ratio = stagnant_value / total_inventory_value if total_inventory_value > 0 else 0.0

        return stagnant_ratio, stagnant_value

    except Exception as e:
        logger.exception("计算呆滞库存出错")
        print(f"计算呆滞库存出错: {str(e)}")
        return 0.0, 0.0


def analyze_batch_level_data(batch_data, shipping_data, forecast_data, price_data):
    """批次级别详细分析"""
    try:
        if batch_data.empty:
            return pd.DataFrame()

        batch_analysis = []
        today = datetime.now().date()

        # 计算产品销售指标
        product_sales_metrics = calculate_product_sales_metrics(shipping_data)

        # 处理每个批次
        for _, batch in batch_data.iterrows():
            try:
                product_code = batch['产品代码']
                description = batch['描述']
                batch_date = pd.to_datetime(batch['生产日期']).date() if pd.notna(batch['生产日期']) else today
                batch_qty = float(batch['数量']) if pd.notna(batch['数量']) else 0

                # 计算库龄
                batch_age = (today - batch_date).days

                # 获取产品单价
                unit_price = price_data.get(product_code, 150.0)
                batch_value = batch_qty * unit_price

                # 获取销售指标
                sales_metrics = product_sales_metrics.get(product_code, {
                    'daily_avg_sales': 0.1,
                    'sales_volatility': 0,
                    'total_sales': 0
                })

                # 计算清库天数
                daily_sales = max(sales_metrics['daily_avg_sales'], INVENTORY_CONFIG['min_daily_sales'])
                days_to_clear = batch_qty / daily_sales if daily_sales > 0 else float('inf')

                # 计算预测偏差
                forecast_bias = calculate_forecast_bias(product_code, forecast_data, shipping_data)

                # 计算风险积压百分比
                one_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 30)
                two_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 60)
                three_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 90)

                # 计算风险等级
                risk_level = calculate_inventory_risk_level(
                    batch_age, days_to_clear,
                    sales_metrics['sales_volatility'],
                    forecast_bias
                )

                # 责任归属分析
                responsible_region, responsible_person = analyze_responsibility_simplified(
                    product_code, shipping_data, forecast_data
                )

                # 生成建议措施
                recommendation = generate_recommendation_for_inventory(risk_level, batch_age, days_to_clear)

                # 确定积压原因
                stocking_reasons = determine_stocking_reasons(batch_age, sales_metrics['sales_volatility'],
                                                              forecast_bias)

                # 获取产品简化名称
                simplified_name = get_simplified_product_name(product_code, description)

                # 添加到分析结果
                batch_analysis.append({
                    '产品代码': product_code,
                    '描述': description,
                    '产品简化名称': simplified_name,
                    '批次日期': batch_date,
                    '批次库存': batch_qty,
                    '库龄': batch_age,
                    '批次价值': batch_value,
                    '日均出货': round(sales_metrics['daily_avg_sales'], 2),
                    '出货波动系数': round(sales_metrics['sales_volatility'], 2),
                    '预计清库天数': days_to_clear if days_to_clear != float('inf') else float('inf'),
                    '一个月积压风险': f"{one_month_risk:.1f}%",
                    '两个月积压风险': f"{two_month_risk:.1f}%",
                    '三个月积压风险': f"{three_month_risk:.1f}%",
                    '积压原因': stocking_reasons,
                    '责任区域': responsible_region,
                    '责任人': responsible_person,
                    '风险程度': risk_level,
                    '风险得分': calculate_risk_score(batch_age, days_to_clear, sales_metrics['sales_volatility'],
                                                     forecast_bias),
                    '建议措施': recommendation,
                    '预测偏差': f"{forecast_bias * 100:.1f}%" if abs(forecast_bias) < 10 else "异常"
                })

            except Exception as e:
                logger.exception(f"处理批次数据时出错: {str(e)}")
                continue

        # 转换为DataFrame并排序
        if batch_analysis:
            df = pd.DataFrame(batch_analysis)
            risk_order = {"极高风险": 0, "高风险": 1, "中风险": 2, "低风险": 3, "极低风险": 4}
            df['风险排序'] = df['风险程度'].map(risk_order)
            df = df.sort_values(['风险排序', '库龄'], ascending=[True, False])
            df = df.drop(columns=['风险排序'])
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        logger.exception("批次分析出错")
        st.error(f"批次分析出错: {str(e)}")
        return pd.DataFrame()


def calculate_risk_score(batch_age, days_to_clear, sales_volatility, forecast_bias):
    """计算批次风险得分"""
    risk_score = 0

    # 库龄因素 (0-40分)
    if batch_age > 90:
        risk_score += 40
    elif batch_age > 60:
        risk_score += 30
    elif batch_age > 30:
        risk_score += 20
    else:
        risk_score += 10

    # 清库天数因素 (0-40分)
    if days_to_clear == float('inf'):
        risk_score += 40
    elif days_to_clear > 180:  # 半年以上
        risk_score += 35
    elif days_to_clear > 90:  # 3个月以上
        risk_score += 30
    elif days_to_clear > 60:  # 2个月以上
        risk_score += 20
    elif days_to_clear > 30:  # 1个月以上
        risk_score += 10

    # 销量波动系数 (0-10分)
    if sales_volatility > 2.0:
        risk_score += 10
    elif sales_volatility > 1.0:
        risk_score += 5

    # 预测偏差 (0-10分) - 使用绝对值评估偏差大小
    if abs(forecast_bias) > 0.5:  # 50%以上偏差
        risk_score += 10
    elif abs(forecast_bias) > 0.3:  # 30%以上偏差
        risk_score += 8
    elif abs(forecast_bias) > 0.15:  # 15%以上偏差
        risk_score += 5

    return risk_score


def calculate_product_sales_metrics(shipping_data):
    """计算产品销售指标"""
    if shipping_data is None or shipping_data.empty:
        return {}

    metrics = {}
    today = datetime.now().date()

    for product_code in shipping_data['产品代码'].unique():
        product_sales = shipping_data[shipping_data['产品代码'] == product_code]

        if product_sales.empty:
            metrics[product_code] = {
                'daily_avg_sales': 0.1,
                'sales_volatility': 0,
                'total_sales': 0
            }
            continue

        # 计算总销量
        total_sales = product_sales['数量'].sum()

        # 计算日期范围
        min_date = product_sales['订单日期'].min().date()
        days_range = (today - min_date).days + 1

        # 日均销量
        daily_avg_sales = total_sales / days_range if days_range > 0 else 0.1

        # 计算销量波动
        daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['数量'].sum()
        sales_volatility = daily_sales.std() / daily_sales.mean() if len(
            daily_sales) > 1 and daily_sales.mean() > 0 else 0

        metrics[product_code] = {
            'daily_avg_sales': max(daily_avg_sales, 0.1),
            'sales_volatility': sales_volatility,
            'total_sales': total_sales
        }

    return metrics


def calculate_forecast_bias(product_code, forecast_data, shipping_data):
    """计算预测偏差"""
    try:
        if forecast_data is None or forecast_data.empty or shipping_data is None or shipping_data.empty:
            return 0.0

        # 获取最近一个月的预测和实际销量
        recent_forecast = forecast_data[forecast_data['产品代码'] == product_code]['预计销售量'].sum()

        # 获取最近30天的实际销量
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        recent_sales_data = shipping_data[
            (shipping_data['产品代码'] == product_code) &
            (shipping_data['订单日期'].dt.date >= thirty_days_ago)
            ]
        recent_sales = recent_sales_data['数量'].sum() if not recent_sales_data.empty else 0

        if recent_forecast == 0 and recent_sales == 0:
            return 0.0
        elif recent_forecast == 0:
            return -1.0  # 无预测但有销售
        elif recent_sales == 0:
            return 1.0  # 有预测但无销售
        else:
            # 计算预测偏差 - 对称平均绝对百分比误差(SMAPE)变体
            bias = (recent_forecast - recent_sales) / ((recent_forecast + recent_sales) / 2)
            return max(-1.0, min(1.0, bias))  # 限制在-1到1之间

    except Exception:
        logger.exception("计算预测偏差出错")
        return 0.0


def analyze_responsibility_simplified(product_code, shipping_data, forecast_data):
    """简化的责任归属分析"""
    try:
        # 默认责任人和区域
        default_region = "未知区域"
        default_person = "系统管理员"

        # 从出货数据中找最主要的责任人
        if shipping_data is not None and not shipping_data.empty:
            product_shipping = shipping_data[shipping_data['产品代码'] == product_code]
            if not product_shipping.empty:
                # 按申请人统计数量
                person_sales = product_shipping.groupby('申请人')['数量'].sum()
                if not person_sales.empty:
                    main_person = person_sales.idxmax()
                    # 获取该人员的区域
                    person_region_data = product_shipping[product_shipping['申请人'] == main_person]['所属区域']
                    if not person_region_data.empty:
                        person_region = person_region_data.iloc[0]
                        return person_region, main_person

        # 从预测数据中找责任人
        if forecast_data is not None and not forecast_data.empty:
            product_forecast = forecast_data[forecast_data['产品代码'] == product_code]
            if not product_forecast.empty:
                forecast_person = product_forecast['销售员'].iloc[0]
                forecast_region = product_forecast['所属大区'].iloc[0]
                return forecast_region, forecast_person

        return default_region, default_person

    except Exception:
        logger.exception("分析责任归属时出错")
        return "未知区域", "系统管理员"


def generate_recommendation_for_inventory(risk_level, batch_age, days_to_clear):
    """生成库存建议措施"""
    if risk_level == "极高风险":
        return "紧急清理：考虑折价促销或转仓"
    elif risk_level == "高风险":
        return "优先处理：促销或加大营销力度"
    elif risk_level == "中风险":
        return "密切监控：调整采购计划"
    elif risk_level == "低风险":
        return "常规管理：定期检查库存状态"
    else:
        return "维持现状：正常库存水平"


def determine_stocking_reasons(batch_age, volatility, forecast_bias):
    """确定积压原因"""
    reasons = []
    if batch_age > 60:
        reasons.append("库龄过长")
    if volatility > 1.0:
        reasons.append("销量波动大")
    if abs(forecast_bias) > 0.3:
        reasons.append("预测偏差大")
    if not reasons:
        reasons.append("正常库存")
    return "，".join(reasons)


# ==================== 6. 图表创建函数 - 优化重组版 ====================
def create_risk_overview_chart(analysis_result):
    """创建风险概览图表 - 将库存健康和风险分布整合为一个图"""
    if not analysis_result:
        return None

    # 风险等级分布
    risk_dist = analysis_result.get('risk_distribution', {})

    if not risk_dist:
        return None

    # 确保按风险等级排序
    risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
    ordered_risk = {k: risk_dist.get(k, 0) for k in risk_order if k in risk_dist}

    # 创建饼图
    risk_fig = go.Figure()

    # 添加风险环形图
    risk_fig.add_trace(go.Pie(
        labels=list(ordered_risk.keys()),
        values=list(ordered_risk.values()),
        marker_colors=[INVENTORY_RISK_COLORS.get(level, COLORS['gray']) for level in ordered_risk.keys()],
        textposition='inside',
        textinfo='percent+label',
        hole=0.6,
        hovertemplate='<b>%{label}</b><br>批次数量: %{value}<br>占比: %{percent}<extra></extra>',
        domain={'x': [0, 1], 'y': [0, 1]},
        sort=False  # 保持自定义排序
    ))

    # 在中心添加总批次数量
    total_batches = sum(ordered_risk.values())
    high_risk_count = ordered_risk.get('极高风险', 0) + ordered_risk.get('高风险', 0)
    high_risk_pct = high_risk_count / total_batches * 100 if total_batches > 0 else 0

    risk_fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>总批次: {total_batches}</b><br>高风险: {format_percentage(high_risk_pct)}",
        font=dict(size=14, color=COLORS['primary']),
        showarrow=False
    )

    risk_fig.update_layout(
        title={
            'text': "<b>库存风险分布</b><br><span style='font-size:12px;font-weight:normal'>按风险等级划分的批次数量</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=400,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5
        )
    )

    return risk_fig


def create_combined_risk_chart(batch_analysis):
    """创建综合风险分析图表 - 整合库龄和价值分析"""
    if batch_analysis is None or batch_analysis.empty:
        return None

    # 选取高风险和极高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        return None

    # 按库龄排序，选择前15个最老批次
    top_batches = high_risk_batches.sort_values('库龄', ascending=False).head(15)

    # 创建图表 - 使用散点图，大小表示批次价值，颜色表示风险等级
    risk_fig = go.Figure()

    # 为每个风险等级分别添加散点
    for risk_level in ['极高风险', '高风险']:
        risk_data = top_batches[top_batches['风险程度'] == risk_level]
        if not risk_data.empty:
            # 计算散点大小 - 基于批次价值的正规化
            if risk_data['批次价值'].max() > 0:
                size_scale = risk_data['批次价值'] / risk_data['批次价值'].max() * 40 + 10
            else:
                size_scale = 15

            risk_fig.add_trace(go.Scatter(
                x=risk_data['库龄'],
                y=risk_data['预计清库天数'],
                mode='markers',
                marker=dict(
                    size=size_scale,
                    color=INVENTORY_RISK_COLORS.get(risk_level),
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                name=risk_level,
                text=risk_data['产品简化名称'],
                customdata=risk_data[['批次价值', '责任人', '建议措施']],
                hovertemplate='<b>%{text}</b><br>库龄: %{x}天<br>清库天数: %{y}天<br>批次价值: ¥%{customdata[0]:.2f}<br>责任人: %{customdata[1]}<br>建议: %{customdata[2]}<extra></extra>'
            ))

    # 添加参考线
    risk_fig.add_shape(
        type="line", x0=90, x1=90, y0=0, y1=top_batches['预计清库天数'].max() * 1.1,
        line=dict(color=COLORS['danger'], dash="dash", width=2)
    )
    risk_fig.add_shape(
        type="line", x0=60, x1=60, y0=0, y1=top_batches['预计清库天数'].max() * 1.1,
        line=dict(color=COLORS['warning'], dash="dash", width=1.5)
    )

    # 添加参考线说明
    risk_fig.add_annotation(
        x=90, y=top_batches['预计清库天数'].max() * 1.05,
        text="高风险库龄(90天)",
        showarrow=False,
        font=dict(size=10, color=COLORS['danger']),
        xanchor="center",
        yanchor="bottom"
    )

    risk_fig.add_annotation(
        x=60, y=top_batches['预计清库天数'].max() * 1.05,
        text="中风险库龄(60天)",
        showarrow=False,
        font=dict(size=10, color=COLORS['warning']),
        xanchor="center",
        yanchor="bottom"
    )

    # 添加图表说明
    risk_fig.update_layout(
        title={
            'text': "<b>高风险批次分析</b><br><span style='font-size:12px;font-weight:normal'>库龄 vs 清库天数，气泡大小表示批次价值</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=500,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="批次库龄（天）",
        yaxis_title="预计清库天数（天）",
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=100, b=80)
    )

    return risk_fig


def create_responsibility_tree_chart(batch_analysis):
    """创建责任归属树状图 - 替代分离的责任图表"""
    if batch_analysis is None or batch_analysis.empty:
        return None

    # 整合数据 - 按区域、责任人和风险程度统计批次价值
    aggregated_data = batch_analysis.groupby(['责任区域', '责任人', '风险程度'])['批次价值'].sum().reset_index()

    # 确保有区域信息 - 过滤掉未知区域
    aggregated_data = aggregated_data[
        (aggregated_data['责任区域'].notna()) &
        (aggregated_data['责任区域'] != '未知区域') &
        (aggregated_data['责任人'].notna()) &
        (aggregated_data['责任人'] != '系统管理员')
        ]

    if aggregated_data.empty:
        return None

    # 创建树状图数据
    risk_order = ["极高风险", "高风险", "中风险", "低风险", "极低风险"]

    # 添加所有层级
    labels = ['全部批次']
    parents = ['']
    values = [aggregated_data['批次价值'].sum()]
    colors = ['#FFFFFF']  # 根节点颜色

    # 添加区域层级
    for region, group in aggregated_data.groupby('责任区域'):
        labels.append(region)
        parents.append('全部批次')
        values.append(group['批次价值'].sum())
        colors.append(COLORS['primary'])

        # 添加责任人层级
        for person, person_group in group.groupby('责任人'):
            person_id = f"{region} - {person}"
            labels.append(person_id)
            parents.append(region)
            values.append(person_group['批次价值'].sum())
            colors.append(COLORS['secondary'])

            # 添加风险等级层级
            for risk in risk_order:
                risk_rows = person_group[person_group['风险程度'] == risk]
                if not risk_rows.empty:
                    risk_id = f"{person_id} - {risk}"
                    labels.append(risk_id)
                    parents.append(person_id)
                    values.append(risk_rows['批次价值'].sum())
                    colors.append(INVENTORY_RISK_COLORS.get(risk, COLORS['gray']))

    # 创建树状图
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colors=colors,
            line=dict(width=1, color='white')
        ),
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>批次价值: ¥%{value:,.2f}<br>占比: %{percentParent:.1%}<br>占总体: %{percentRoot:.1%}<extra></extra>',
        branchvalues="total"
    ))

    fig.update_layout(
        title={
            'text': "<b>责任归属分析</b><br><span style='font-size:12px;font-weight:normal'>按区域、责任人和风险等级的批次价值分布</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=600,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig


def create_forecast_impact_chart(batch_analysis):
    """创建预测影响综合图表 - 整合清库预测和预测偏差分析"""
    if batch_analysis is None or batch_analysis.empty:
        return None

    # 处理预测偏差数据
    batch_analysis_copy = batch_analysis.copy()
    batch_analysis_copy['预测偏差值'] = batch_analysis_copy['预测偏差'].apply(
        lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) and '%' in x and x != '异常' else 0
    )

    # 筛选有效数据
    valid_forecast = batch_analysis_copy[
        (abs(batch_analysis_copy['预测偏差值']) <= 1.0) &
        (batch_analysis_copy['预计清库天数'] != float('inf'))
        ]

    if valid_forecast.empty or len(valid_forecast) < 3:
        return None

    # 选择预测偏差较大的批次
    significant_bias = valid_forecast.sort_values('预测偏差值', key=abs, ascending=False).head(20)

    # 创建图表
    fig = go.Figure()

    # 创建散点图，使用条件颜色映射
    fig.add_trace(go.Scatter(
        x=significant_bias['预测偏差值'] * 100,  # 转为百分比显示
        y=significant_bias['预计清库天数'],
        mode='markers',
        marker=dict(
            size=significant_bias['批次价值'] / significant_bias['批次价值'].max() * 30 + 10,
            color=significant_bias['预测偏差值'] * 100,
            colorscale=[
                [0.0, '#1565C0'],  # 深蓝色 - 预测不足
                [0.5, '#FFFFFF'],  # 白色 - 预测准确
                [1.0, '#C62828']  # 深红色 - 预测过高
            ],
            colorbar=dict(
                title="预测偏差 (%)",
                titleside="right",
                tickmode="array",
                tickvals=[-100, -50, 0, 50, 100],
                ticktext=["-100%", "-50%", "0%", "50%", "100%"],
                ticks="outside"
            ),
            line=dict(width=1, color='white')
        ),
        text=significant_bias['产品简化名称'],
        customdata=significant_bias[['批次价值', '责任人', '风险程度', '库龄']],
        hovertemplate='<b>%{text}</b><br>预测偏差: %{x:.1f}%<br>清库天数: %{y:.1f}天<br>批次价值: ¥%{customdata[0]:.2f}<br>责任人: %{customdata[1]}<br>风险程度: %{customdata[2]}<br>库龄: %{customdata[3]}天<extra></extra>'
    ))

    # 添加参考线
    fig.add_shape(
        type="line", x0=0, x1=0,
        y0=0, y1=significant_bias['预计清库天数'].max() * 1.1,
        line=dict(color=COLORS['gray'], dash="dash", width=1)
    )

    fig.add_shape(
        type="line", x0=significant_bias['预测偏差值'].min() * 100 * 1.1,
        x1=significant_bias['预测偏差值'].max() * 100 * 1.1,
        y0=90, y1=90,
        line=dict(color=COLORS['danger'], dash="dash", width=1)
    )

    # 添加区域标注
    fig.add_annotation(
        x=50,
        y=significant_bias['预计清库天数'].max() * 0.75,
        text="预测过高<br>库存积压风险",
        showarrow=False,
        font=dict(size=12, color=COLORS['danger']),
        align="center",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=COLORS['danger'],
        borderwidth=1,
        borderpad=4
    )

    fig.add_annotation(
        x=-50,
        y=significant_bias['预计清库天数'].max() * 0.75,
        text="预测过低<br>缺货风险",
        showarrow=False,
        font=dict(size=12, color=COLORS['primary']),
        align="center",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=COLORS['primary'],
        borderwidth=1,
        borderpad=4
    )

    # 优化图表布局
    fig.update_layout(
        title={
            'text': "<b>预测偏差对库存的影响</b><br><span style='font-size:12px;font-weight:normal'>气泡大小表示批次价值，颜色表示预测偏差</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=550,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="预测偏差 (%)",
        yaxis_title="预计清库天数",
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            title_font=dict(size=12),
            tickfont=dict(size=10),
            range=[significant_bias['预测偏差值'].min() * 100 * 1.1,
                   significant_bias['预测偏差值'].max() * 100 * 1.1]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=100, b=50)
    )

    return fig


def create_batch_risk_heatmap(data):
    """创建批次风险热力图，用于替代详细数据表 - 优化版"""
    if data is None or data.empty:
        return None

    # 准备热力图数据
    risk_order = ["极高风险", "高风险", "中风险", "低风险", "极低风险"]

    # 按产品和风险程度分组
    grouped_data = data.groupby(['产品简化名称', '风险程度']).agg({
        '批次价值': 'sum',
        '批次库存': 'sum',
        '库龄': 'mean',
        '预计清库天数': 'mean'
    }).reset_index()

    # 创建热力图
    pivot_data = pd.pivot_table(
        grouped_data,
        values='批次价值',
        index='产品简化名称',
        columns='风险程度',
        aggfunc='sum',
        fill_value=0
    )

    # 确保所有风险级别的列都存在
    for risk in risk_order:
        if risk not in pivot_data.columns:
            pivot_data[risk] = 0

    # 按照风险顺序排列列
    for col in risk_order:
        if col not in pivot_data.columns:
            pivot_data[col] = 0
    pivot_data = pivot_data[risk_order]

    # 计算每行(产品)的总和，并按总和排序
    pivot_data['总价值'] = pivot_data.sum(axis=1)
    pivot_data = pivot_data.sort_values('总价值', ascending=False)
    pivot_data = pivot_data.drop('总价值', axis=1)

    # 限制显示前15个产品
    pivot_data = pivot_data.head(15)

    # 确保数据不为空
    if pivot_data.empty or pivot_data.sum().sum() == 0:
        return None

    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=[
            [0, 'rgb(247, 251, 255)'],  # 接近白色
            [0.1, 'rgb(198, 219, 239)'],
            [0.3, 'rgb(107, 174, 214)'],
            [0.5, 'rgb(33, 113, 181)'],
            [0.8, 'rgb(8, 48, 107)'],
            [1, 'rgb(8, 29, 88)']  # 深蓝色
        ],
        showscale=True,
        colorbar=dict(title="批次价值"),
        text=[[format_currency(val) for val in row] for row in pivot_data.values],
        hovertemplate='<b>产品: %{y}</b><br>风险等级: %{x}<br>批次价值: %{text}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': "<b>批次风险分布热力图</b><br><span style='font-size:12px;font-weight:normal'>各产品在不同风险等级下的批次价值分布</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=600,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="风险等级",
        yaxis_title="产品",
        xaxis=dict(
            tickangle=-30,
            categoryorder='array',
            categoryarray=risk_order,
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=100, b=50)
    )

    return fig


def create_top_high_risk_product_chart(data):
    """创建高风险产品Top图表"""
    if data is None or data.empty:
        return None

    # 选择高风险和极高风险批次
    high_risk_data = data[data['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_data.empty:
        return None

    # 按产品分组计算总价值和平均库龄
    product_summary = high_risk_data.groupby('产品简化名称').agg({
        '批次价值': 'sum',
        '库龄': 'mean',
        '批次库存': 'sum',
        '风险程度': lambda x: '极高风险' if '极高风险' in x.values else '高风险'
    }).reset_index()

    # 取价值最高的10个产品
    top_products = product_summary.sort_values('批次价值', ascending=False).head(10)

    if top_products.empty:
        return None

    # 创建条形图
    fig = go.Figure()

    # 按风险程度分别添加条形
    for risk in ['极高风险', '高风险']:
        risk_products = top_products[top_products['风险程度'] == risk]
        if not risk_products.empty:
            fig.add_trace(go.Bar(
                y=risk_products['产品简化名称'],
                x=risk_products['批次价值'],
                orientation='h',
                name=risk,
                marker_color=INVENTORY_RISK_COLORS.get(risk),
                text=risk_products['批次价值'].apply(format_currency),
                textposition='outside',
                customdata=risk_products[['库龄', '批次库存']],
                hovertemplate='<b>%{y}</b><br>批次价值: %{text}<br>平均库龄: %{customdata[0]:.1f}天<br>库存量: %{customdata[1]:.0f}箱<br>风险级别: ' + risk + '<extra></extra>'
            ))

    # 优化图表布局
    fig.update_layout(
        title={
            'text': "<b>高风险产品Top10</b><br><span style='font-size:12px;font-weight:normal'>按批次价值排序的高风险/极高风险产品</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=500,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="批次价值（元）",
        yaxis_title="产品",
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            autorange="reversed",  # 从大到小显示
            title_font=dict(size=12),
            tickfont=dict(size=10),
            categoryorder='total ascending'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=100, b=50)
    )

    return fig


# ==================== 7. 追加跳转到标签页的辅助函数 - 优化版 ====================
def navigate_to_tab(tab_index):
    """跳转到指定的标签页"""
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    st.session_state.active_tab = tab_index


# ==================== 8. 主页面逻辑 - 优化重组版 ====================
def main():
    """主页面函数"""
    # 检查用户是否已登录
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("请先登录系统")
        st.stop()

    # 数据文件搜索开关
    if 'show_data_search' not in st.session_state:
        st.session_state.show_data_search = False

    # 显示数据文件搜索详情
    show_data_search = st.sidebar.checkbox("显示数据文件搜索详情", value=st.session_state.show_data_search)
    if show_data_search != st.session_state.show_data_search:
        st.session_state.show_data_search = show_data_search
        st.rerun()

    # 加载库存数据
    data = load_and_process_inventory_data(show_details=st.session_state.show_data_search)

    if data is None:
        st.error("无法加载库存数据，请检查数据文件")
        st.markdown("""
        <div class="error-box">
            <h3>数据加载失败</h3>
            <p>请确保以下数据文件存在且格式正确：</p>
            <ul>
                <li>含批次库存文件 (Excel格式)</li>
                <li>出货数据文件 (Excel格式)</li>
                <li>预测数据文件 (Excel格式)</li>
                <li>单价数据文件 (Excel格式)</li>
            </ul>
            <p>文件应位于应用目录、pages子目录或data子目录中。</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 应用筛选
    filtered_data = create_inventory_filters(data)

    if 'analysis_result' not in filtered_data:
        st.error("数据分析失败")
        return

    analysis_result = filtered_data['analysis_result']
    batch_analysis = analysis_result.get('batch_analysis')

    # 初始化活动标签页
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

    # 创建标签页 - 优化版（减少为4个标签页）
    tab_titles = [
        "📊 库存总览与风险",
        "⚠️ 高风险批次分析",
        "👥 责任归属分析",
        "📈 预测与清库分析"
    ]

    tabs = st.tabs(tab_titles)

    # 添加时间维度说明
    time_dimensions = {
        "库龄": "基于批次生产日期到当前日期计算",
        "库存周转率": "基于过去90天的销售数据计算",
        "预测偏差": "基于最近30天的销售数据与预测比较",
        "呆滞库存": f"库龄超过{INVENTORY_CONFIG['stagnant_days_threshold']}天的批次",
    }

    # 显示活动标签页
    active_tab_index = min(st.session_state.active_tab, len(tabs) - 1)

    with tabs[0]:  # 总览与关键指标
        if active_tab_index == 0:
            st.markdown('<div class="sub-header">📊 库存关键指标</div>', unsafe_allow_html=True)

            # 添加时间维度说明
            st.markdown(f'''
            <div class="time-dim-note">
            📅 <b>时间维度说明</b>: {time_dimensions["库龄"]}；{time_dimensions["库存周转率"]}；
            {time_dimensions["预测偏差"]}；{time_dimensions["呆滞库存"]}
            </div>
            ''', unsafe_allow_html=True)

            # 关键指标行 - 新增库存周转天数和呆滞库存比例
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                # 库存周转天数 - 核心指标
                turnover_days = analysis_result.get('inventory_turnover_days', float('inf'))
                turnover_days_display = format_days(turnover_days)
                turnover_color = COLORS['success'] if turnover_days < 60 else (
                    COLORS['warning'] if turnover_days < 90 else COLORS['danger'])

                # 添加跳转到清库预测分析的按钮 - 使用改进的方式
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">库存周转天数</p>
                    <p class="card-value" style="color:{turnover_color};">{turnover_days_display}</p>
                    <p class="card-text">库存流转速度核心指标</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("查看清库分析", key="view_turnover_details"):
                    st.session_state.active_tab = 3  # 预测与清库分析标签页
                    st.rerun()

            with col2:
                # 呆滞库存比例 - 新增核心指标
                stagnant_ratio = analysis_result.get('stagnant_ratio', 0.0)
                stagnant_ratio_display = format_percentage(stagnant_ratio * 100)
                stagnant_color = COLORS['success'] if stagnant_ratio < 0.1 else (
                    COLORS['warning'] if stagnant_ratio < 0.3 else COLORS['danger'])

                # 添加跳转到风险批次分析的按钮
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">呆滞库存比例</p>
                    <p class="card-value" style="color:{stagnant_color};">{stagnant_ratio_display}</p>
                    <p class="card-text">超过60天的库存占比</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("查看风险分析", key="view_stagnant_details"):
                    st.session_state.active_tab = 1  # 风险批次分析标签页
                    st.rerun()

            with col3:
                # 高风险批次数量
                risk_dist = analysis_result.get('risk_distribution', {})
                high_risk_count = risk_dist.get('极高风险', 0) + risk_dist.get('高风险', 0)
                total_batches = sum(risk_dist.values()) if risk_dist else 0
                high_risk_pct = (high_risk_count / total_batches * 100) if total_batches > 0 else 0

                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">高风险批次数量</p>
                    <p class="card-value" style="color:{COLORS['danger']};">{high_risk_count}</p>
                    <p class="card-text">占总批次{format_percentage(high_risk_pct)}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("查看高风险批次", key="view_high_risk_details"):
                    st.session_state.active_tab = 1  # 风险批次分析标签页
                    st.rerun()

            with col4:
                # 库存资金占用成本 - 核心指标
                capital_cost = analysis_result.get('capital_cost', 0.0)
                total_value = analysis_result.get('total_inventory_value', 0.0)
                capital_cost_display = format_currency(capital_cost)

                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">月均资金占用成本</p>
                    <p class="card-value">{capital_cost_display}</p>
                    <p class="card-text">总价值: {format_currency(total_value)}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("查看责任分析", key="view_capital_cost_details"):
                    st.session_state.active_tab = 2  # 责任归属分析标签页
                    st.rerun()

            # 风险概览图表
            st.markdown('<div class="sub-header">库存风险概览</div>', unsafe_allow_html=True)

            # 创建整合后的风险概览图
            risk_overview_fig = create_risk_overview_chart(analysis_result)

            if risk_overview_fig:
                st.plotly_chart(risk_overview_fig, use_container_width=True)
            else:
                display_empty_chart_message(
                    "暂无风险分布数据",
                    "当前筛选条件下无法生成风险分布图表。请尝试调整筛选条件或检查数据源。"
                )

            # 高风险产品Top图表
            if batch_analysis is not None and not batch_analysis.empty:
                high_risk_products_fig = create_top_high_risk_product_chart(batch_analysis)

                if high_risk_products_fig:
                    st.plotly_chart(high_risk_products_fig, use_container_width=True)

                    # 添加数据洞察
                    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
                    if not high_risk_batches.empty:
                        # 获取主要积压原因
                        stocking_reasons = []
                        for reason in high_risk_batches['积压原因']:
                            if pd.notna(reason):
                                for r in reason.split('，'):
                                    stocking_reasons.append(r)

                        from collections import Counter
                        reason_counts = Counter(stocking_reasons)
                        top_reasons = reason_counts.most_common(2)
                        reasons_text = f"{top_reasons[0][0]} ({top_reasons[0][1]}次)"
                        if len(top_reasons) > 1:
                            reasons_text += f" 和 {top_reasons[1][0]} ({top_reasons[1][1]}次)"

                        # 获取责任人和区域信息
                        top_region = high_risk_batches['责任区域'].value_counts().index[0] if len(
                            high_risk_batches['责任区域'].value_counts()) > 0 else "未知"
                        top_person = high_risk_batches['责任人'].value_counts().index[0] if len(
                            high_risk_batches['责任人'].value_counts()) > 0 else "未知"

                        # 构建洞察文本
                        insight_text = f"<b>风险洞察：</b> 主要积压原因为{reasons_text}。"
                        insight_text += f" {top_region}区域和{top_person}是高风险批次的主要责任人。"
                        insight_text += f" 当前共有{len(high_risk_batches)}个高风险批次，价值{format_currency(high_risk_batches['批次价值'].sum())}。"
                        insight_text += "<br><b>建议措施：</b> 针对高风险批次实施清库计划，重点关注库龄超过90天的批次；改进需求预测准确性，减少库存积压。"

                        add_chart_explanation(insight_text)

            else:
                display_empty_chart_message(
                    "暂无高风险产品数据",
                    "当前筛选条件下无法生成高风险产品图表。请尝试调整筛选条件或检查数据源。"
                )

    with tabs[1]:  # 高风险批次分析
        if active_tab_index == 1:
            st.markdown('<div class="sub-header">⚠️ 高风险批次分析</div>', unsafe_allow_html=True)

            # 添加时间维度说明
            st.markdown(f'''
            <div class="time-dim-note">
            📅 <b>时间维度说明</b>: {time_dimensions["库龄"]}；风险评估基于当前库龄、销售趋势和预测偏差综合计算
            </div>
            ''', unsafe_allow_html=True)

            if batch_analysis is not None and not batch_analysis.empty:
                # 风险统计 - 使用卡片样式
                col1, col2, col3 = st.columns(3)

                with col1:
                    extreme_high = len(batch_analysis[batch_analysis['风险程度'] == '极高风险'])
                    extreme_high_value = batch_analysis[batch_analysis['风险程度'] == '极高风险']['批次价值'].sum()

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">极高风险批次</p>
                        <p class="card-value" style="color: {INVENTORY_RISK_COLORS['极高风险']};">{extreme_high}</p>
                        <p class="card-text">价值: {format_currency(extreme_high_value)}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    high_risk = len(batch_analysis[batch_analysis['风险程度'] == '高风险'])
                    high_risk_value = batch_analysis[batch_analysis['风险程度'] == '高风险']['批次价值'].sum()

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">高风险批次</p>
                        <p class="card-value" style="color: {INVENTORY_RISK_COLORS['高风险']};">{high_risk}</p>
                        <p class="card-text">价值: {format_currency(high_risk_value)}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    avg_age = batch_analysis['库龄'].mean()
                    max_age = batch_analysis['库龄'].max()

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">库龄统计</p>
                        <p class="card-value">{format_days(avg_age)}</p>
                        <p class="card-text">最长库龄: {format_days(max_age)}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # 整合后的风险批次图
                risk_fig = create_combined_risk_chart(batch_analysis)

                if risk_fig:
                    st.plotly_chart(risk_fig, use_container_width=True)
                else:
                    display_empty_chart_message(
                        "暂无高风险批次数据",
                        "当前筛选条件下未找到高风险批次，请尝试调整风险等级筛选条件查看更多批次信息。"
                    )

                # 批次风险热力图
                heatmap_fig = create_batch_risk_heatmap(batch_analysis)

                if heatmap_fig:
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    display_empty_chart_message(
                        "暂无批次风险热力图数据",
                        "当前筛选条件下无法生成批次风险热力图。请尝试减少筛选条件。"
                    )

                # 添加图表解释
                if risk_fig or heatmap_fig:
                    # 提取关键洞察
                    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
                    oldest_batch = None
                    high_value_old_batch = None

                    # 安全地找出最老批次
                    if not batch_analysis.empty and '库龄' in batch_analysis.columns and batch_analysis[
                        '库龄'].notna().any():
                        oldest_batch = batch_analysis.loc[batch_analysis['库龄'].idxmax()]

                    # 安全地找出价值最高的高风险批次
                    if not high_risk_batches.empty and '批次价值' in high_risk_batches.columns and high_risk_batches[
                        '批次价值'].notna().any():
                        high_value_old_batch = high_risk_batches.loc[high_risk_batches['批次价值'].idxmax()]

                    insight_text = "<b>风险分析洞察：</b> 上图展示了高风险批次的库龄与清库时间关系，气泡大小表示批次价值。"
                    if oldest_batch is not None:
                        insight_text += f" 最老批次为{oldest_batch['产品简化名称']}，库龄{oldest_batch['库龄']}天。"

                    insight_text += " 热力图显示了各产品在不同风险等级下的批次价值分布，深色区域表示高价值批次。"
                    if high_value_old_batch is not None:
                        insight_text += f" 价值最高的高风险批次为{high_value_old_batch['产品简化名称']}，价值{format_currency(high_value_old_batch['批次价值'])}。"

                    insight_text += "<br><b>行动建议：</b> 优先处理库龄超过90天且价值高的批次，制定分级清库策略：对极高风险批次考虑折价促销，"
                    insight_text += "对高风险批次加强营销推广力度。建立定期批次审查机制，对接近60天的批次提前干预，防止形成呆滞库存。"

                    add_chart_explanation(insight_text)
            else:
                display_empty_chart_message(
                    "当前筛选条件下暂无批次数据",
                    "请尝试调整筛选条件，减少限制条件以查看更多数据。确保数据源包含有效的批次信息。"
                )

    with tabs[2]:  # 责任归属分析
        if active_tab_index == 2:
            st.markdown('<div class="sub-header">👥 责任归属分析</div>', unsafe_allow_html=True)

            # 添加时间维度说明
            st.markdown(f'''
            <div class="time-dim-note">
            📅 <b>时间维度说明</b>: 责任归属基于历史销售记录和预测数据分析，显示当前批次的主要责任人和区域
            </div>
            ''', unsafe_allow_html=True)

            if batch_analysis is not None and not batch_analysis.empty:
                # 责任统计
                region_stats = batch_analysis.groupby('责任区域')['批次价值'].sum().sort_values(ascending=False)
                person_stats = batch_analysis.groupby('责任人')['批次价值'].sum().sort_values(ascending=False)

                # 过滤掉空或异常的责任区域
                region_stats = region_stats[
                    region_stats.index.notna() & (region_stats.index != '') & (region_stats.index != '未知区域')]
                person_stats = person_stats[
                    person_stats.index.notna() & (person_stats.index != '') & (person_stats.index != '系统管理员')]

                col1, col2 = st.columns(2)

                with col1:
                    top_region = region_stats.index[0] if len(region_stats) > 0 else "无"
                    top_region_value = region_stats.iloc[0] if len(region_stats) > 0 else 0

                    # 获取这个区域的高风险批次比例
                    if top_region != "无":
                        region_batches = batch_analysis[batch_analysis['责任区域'] == top_region]
                        region_high_risk = len(region_batches[region_batches['风险程度'].isin(['极高风险', '高风险'])])
                        region_risk_pct = region_high_risk / len(region_batches) * 100 if len(region_batches) > 0 else 0
                        region_detail = f"高风险比例: {format_percentage(region_risk_pct)}"
                    else:
                        region_detail = "无详细数据"

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">最大责任区域</p>
                        <p class="card-value">{top_region}</p>
                        <p class="card-text">责任价值: {format_currency(top_region_value)}<br>{region_detail}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    top_person = person_stats.index[0] if len(person_stats) > 0 else "无"
                    top_person_value = person_stats.iloc[0] if len(person_stats) > 0 else 0

                    # 获取这个责任人的高风险批次比例
                    if top_person != "无":
                        person_batches = batch_analysis[batch_analysis['责任人'] == top_person]
                        person_high_risk = len(person_batches[person_batches['风险程度'].isin(['极高风险', '高风险'])])
                        person_risk_pct = person_high_risk / len(person_batches) * 100 if len(person_batches) > 0 else 0
                        person_detail = f"高风险比例: {format_percentage(person_risk_pct)}"
                    else:
                        person_detail = "无详细数据"

                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="card-header">最大责任人</p>
                        <p class="card-value">{top_person}</p>
                        <p class="card-text">责任价值: {format_currency(top_person_value)}<br>{person_detail}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # 责任树状图 - 替代原来的两个图表
                responsibility_tree = create_responsibility_tree_chart(batch_analysis)

                if responsibility_tree:
                    st.plotly_chart(responsibility_tree, use_container_width=True)

                    # 添加图表解释
                    insight_text = "<b>责任归属洞察：</b> 树状图展示了批次价值按区域、责任人和风险等级的分层分布。"

                    if top_region != "无":
                        insight_text += f" {top_region}区域是主要责任区域，占总批次价值的{region_stats.iloc[0] / region_stats.sum() * 100:.1f}%。"

                    if top_person != "无":
                        insight_text += f" {top_person}是主要责任人，管理的批次价值占{person_stats.iloc[0] / person_stats.sum() * 100:.1f}%。"

                    # 查找风险最高的区域
                    region_risk_counts = batch_analysis.groupby('责任区域')['风险程度'].apply(
                        lambda x: sum(x.isin(['极高风险', '高风险'])) / len(x) if len(x) > 0 else 0
                    ).sort_values(ascending=False)

                    highest_risk_region = region_risk_counts.index[0] if len(region_risk_counts) > 0 else "无"
                    highest_risk_pct = region_risk_counts.iloc[0] * 100 if len(region_risk_counts) > 0 else 0

                    if highest_risk_region != "无" and highest_risk_region != top_region:
                        insight_text += f" 值得注意的是，{highest_risk_region}区域的高风险批次比例最高，达到{format_percentage(highest_risk_pct)}。"

                    insight_text += "<br><b>行动建议：</b> "

                    if highest_risk_region != "无" and highest_risk_pct > 30:
                        insight_text += f"对{highest_risk_region}区域（高风险批次占比{format_percentage(highest_risk_pct)}）进行重点库存管理培训，"
                    else:
                        insight_text += "对库存价值高的区域加强库存管理培训，"

                    insight_text += "建立清晰的责任制考核体系；优化预测准确性，提高销售与采购的协调效率；"
                    insight_text += "建立跨区域库存调拨机制，平衡区域间库存分布差异。"

                    add_chart_explanation(insight_text)

                else:
                    display_empty_chart_message(
                        "暂无责任归属数据",
                        "当前筛选条件下无法生成责任归属分析图表。请尝试调整筛选条件或检查数据源。"
                    )
            else:
                display_empty_chart_message(
                    "当前筛选条件下暂无责任归属数据",
                    "请尝试调整筛选条件，减少限制条件以查看更多数据。确保数据源包含有效的责任人和区域信息。"
                )

    with tabs[3]:  # 预测与清库分析
        if active_tab_index == 3:
            st.markdown('<div class="sub-header">📈 预测与清库分析</div>', unsafe_allow_html=True)

            # 添加时间维度说明
            st.markdown(f'''
            <div class="time-dim-note">
            📅 <b>时间维度说明</b>: 清库预测基于过去销售数据计算日均销量，并根据当前库存预估清库所需天数；预测偏差分析基于最近30天数据
            </div>
            ''', unsafe_allow_html=True)

            if batch_analysis is not None and not batch_analysis.empty:
                # 清库统计
                infinite_batches = len(batch_analysis[batch_analysis['预计清库天数'] == float('inf')])
                infinite_value = batch_analysis[batch_analysis['预计清库天数'] == float('inf')]['批次价值'].sum()

                long_clearance = len(batch_analysis[
                                         (batch_analysis['预计清库天数'] != float('inf')) &
                                         (batch_analysis['预计清库天数'] > 180)
                                         ])
                long_clearance_value = batch_analysis[
                    (batch_analysis['预计清库天数'] != float('inf')) &
                    (batch_analysis['预计清库天数'] > 180)
                    ]['批次价值'].sum()

                avg_clearance = batch_analysis[batch_analysis['预计清库天数'] != float('inf')]['预计清库天数'].mean()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                                <div class="metric-card">
                                    <p class="card-header">无法清库批次</p>
                                    <p class="card-value" style="color: {COLORS['danger']};">{infinite_batches}</p>
                                    <p class="card-text">价值: {format_currency(infinite_value)}</p>
                                </div>
                                """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                                <div class="metric-card">
                                    <p class="card-header">长期积压批次</p>
                                    <p class="card-value" style="color: {COLORS['warning']};">{long_clearance}</p>
                                    <p class="card-text">价值: {format_currency(long_clearance_value)}</p>
                                </div>
                                """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                                <div class="metric-card">
                                    <p class="card-header">平均清库周期</p>
                                    <p class="card-value">{format_days(avg_clearance)}</p>
                                    <p class="card-text">可清库批次平均值</p>
                                </div>
                                """, unsafe_allow_html=True)

                # 预测偏差分析图表 - 整合图
                forecast_impact_fig = create_forecast_impact_chart(batch_analysis)

                if forecast_impact_fig:
                    st.plotly_chart(forecast_impact_fig, use_container_width=True)
                else:
                    display_empty_chart_message(
                        "暂无预测偏差分析数据",
                        "当前筛选条件下无法生成预测偏差分析图表。可能是因为筛选后的数据量不足或预测数据缺失。"
                    )

                # 添加图表解释
                if forecast_impact_fig:
                    # 提取关键洞察
                    no_sales_products = batch_analysis[batch_analysis['预计清库天数'] == float('inf')][
                        '产品简化名称'].tolist()

                    # 安全处理预测偏差分析
                    batch_analysis_copy = batch_analysis.copy()
                    batch_analysis_copy['预测偏差值'] = batch_analysis_copy['预测偏差'].apply(
                        lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) and '%' in x and x != '异常' else 0
                    )

                    most_overestimated = pd.DataFrame()
                    most_underestimated = pd.DataFrame()

                    # 安全地找出预测偏差最大的产品
                    valid_forecast = batch_analysis_copy[
                        (abs(batch_analysis_copy['预测偏差值']) <= 1.0) &
                        (batch_analysis_copy['预计清库天数'] != float('inf'))
                        ]

                    if not valid_forecast.empty:
                        sorted_bias = valid_forecast.sort_values('预测偏差值', ascending=False)
                        if not sorted_bias.empty:
                            most_overestimated = sorted_bias.iloc[0:1]

                        sorted_bias_under = valid_forecast.sort_values('预测偏差值', ascending=True)
                        if not sorted_bias_under.empty:
                            most_underestimated = sorted_bias_under.iloc[0:1]

                    insight_text = "<b>预测与清库洞察：</b> 图表展示了预测偏差与清库天数之间的关系，气泡大小表示批次价值，颜色代表预测偏差。"

                    if not no_sales_products:
                        insight_text += " 所有批次都有销售记录，但部分批次清库周期过长。"
                    elif len(no_sales_products) <= 3:
                        insight_text += f" 产品{', '.join(no_sales_products[:3])}因无销量导致清库天数为无穷大，需要特别关注。"
                    else:
                        insight_text += f" 有{infinite_batches}个批次因无销量导致清库天数为无穷大，需要特别干预措施。"

                    if not most_overestimated.empty:
                        product = most_overestimated['产品简化名称'].iloc[0]
                        bias = float(most_overestimated['预测偏差'].iloc[0].rstrip('%')) if isinstance(
                            most_overestimated['预测偏差'].iloc[0], str) else 0
                        insight_text += f" 预测偏差最大的产品是{product}，预测过高{abs(bias):.1f}%。"

                    if not most_underestimated.empty:
                        product = most_underestimated['产品简化名称'].iloc[0]
                        bias = float(most_underestimated['预测偏差'].iloc[0].rstrip('%')) if isinstance(
                            most_underestimated['预测偏差'].iloc[0], str) else 0
                        insight_text += f" 预测不足最严重的产品是{product}，预测低于实际销量{abs(bias):.1f}%。"

                    insight_text += "<br><b>行动建议：</b> 对长期积压批次制定专项清库行动计划，考虑捆绑销售或限时促销；"
                    insight_text += "改善预测模型准确性，减少偏差导致的库存积压；建立动态定价机制，根据库龄调整价格策略；"
                    insight_text += "对无销量的产品考虑替代性营销策略或转移到其他销售渠道。"

                    add_chart_explanation(insight_text)
            else:
                display_empty_chart_message(
                    "当前筛选条件下暂无清库预测数据",
                    "请尝试调整筛选条件，减少限制条件以查看更多数据。确保数据源包含有效的销售和库存信息。"
                )


# 执行主函数
if __name__ == "__main__":
    main()