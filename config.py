# config.py - 统一配置和共享函数
import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import math
from datetime import datetime, timedelta

# ================ 获取路径 ================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # 项目根目录

# ================ 颜色主题 ================
COLORS = {
    'primary': '#1f3867',  # 主题色
    'secondary': '#4c78a8',  # 次要颜色
    'success': '#4CAF50',  # 成功/积极
    'warning': '#FF9800',  # 警告/提示
    'danger': '#F44336',  # 危险/错误
    'gray': '#6c757d',  # 中性灰
    'info': '#2196F3'  # 信息蓝
}

# BCG矩阵颜色
BCG_COLORS = {
    'star': '#FFD700',  # 明星产品 - 金色
    'cash_cow': '#4CAF50',  # 现金牛 - 绿色
    'question': '#2196F3',  # 问号产品 - 蓝色
    'dog': '#F44336'  # 瘦狗产品 - 红色
}

# 库存风险颜色 - 调整为与预测与计划.py一致的配色
INVENTORY_RISK_COLORS = {
    '极高风险': '#F44336',  # 红色
    '高风险': '#FF9800',  # 橙色
    '中风险': '#FFC107',  # 黄色
    '低风险': '#4CAF50',  # 绿色
    '极低风险': '#2196F3'  # 蓝色
}

# ================ 数据文件路径 ================
DATA_FILES = {
    'sales_data': os.path.join(ROOT_DIR, "仪表盘原始数据.xlsx"),  # 销售原始数据
    'sales_target': os.path.join(ROOT_DIR, "仪表盘销售月度指标维护.xlsx"),  # 销售目标
    'customer_target': os.path.join(ROOT_DIR, "仪表盘客户月度指标维护.xlsx"),  # 客户指标
    'tt_product_target': os.path.join(ROOT_DIR, "仪表盘TT产品月度指标.xlsx"),  # TT产品指标
    'promotion': os.path.join(ROOT_DIR, "仪表盘促销活动.xlsx"),  # 促销活动
    'inventory': os.path.join(ROOT_DIR, "仪表盘实时库存.xlsx"),  # 实时库存
    'month_end_inventory': os.path.join(ROOT_DIR, "仪表盘月终月末库存.xlsx"),  # 月末库存
    'forecast': os.path.join(ROOT_DIR, "仪表盘人工预测.xlsx"),  # 人工预测
    'product_codes': os.path.join(ROOT_DIR, "仪表盘产品代码.txt"),  # 产品代码列表
    'new_product_codes': os.path.join(ROOT_DIR, "仪表盘新品代码.txt"),  # 新品产品代码
    'customer_relation': os.path.join(ROOT_DIR, "仪表盘人与客户关系表.xlsx"),  # 客户关系表

    # 库存分析专用文件 - 修复文件名
    'batch_inventory': os.path.join(ROOT_DIR, "含批次库存0221(2).xlsx"),  # 批次库存数据
    'shipping_data': os.path.join(ROOT_DIR, "2409~250224出货数据.xlsx"),  # 出货数据
    'inventory_forecast': os.path.join(ROOT_DIR, "2409~2502人工预测.xlsx"),  # 库存预测数据
    'price_data': os.path.join(ROOT_DIR, "单价.xlsx")  # 产品单价
}


# 安全文件加载函数
def safe_load_file(file_key, default_creator=None):
    """安全地加载数据文件，如果文件不存在或加载失败，则使用默认创建函数"""
    file_path = DATA_FILES.get(file_key)

    try:
        if file_path and os.path.exists(file_path):
            # 根据文件类型选择加载方法
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                return pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]

        # 文件不存在或无法识别格式，使用默认创建函数
        if default_creator and callable(default_creator):
            return default_creator()
        return None

    except Exception as e:
        print(f"加载文件 {file_key} 失败: {str(e)}")
        if default_creator and callable(default_creator):
            return default_creator()
        return None


# ================ 库存分析配置 ================
INVENTORY_CONFIG = {
    # 风险评估阈值
    'high_stock_days': 90,  # 库存超过90天视为高风险
    'medium_stock_days': 60,  # 库存超过60天视为中风险
    'low_stock_days': 30,  # 库存超过30天视为低风险

    # 波动性阈值
    'high_volatility_threshold': 1.0,  # 出货波动系数超过1.0视为高波动
    'medium_volatility_threshold': 0.8,  # 出货波动系数超过0.8视为中等波动

    # 预测偏差阈值
    'high_forecast_bias_threshold': 0.3,  # 预测偏差超过30%视为高偏差
    'medium_forecast_bias_threshold': 0.15,  # 预测偏差超过15%视为中等偏差
    'max_forecast_bias': 1.0,  # 预测偏差最大值

    # 清库天数阈值
    'high_clearance_days': 90,  # 预计清库天数超过90天视为高风险
    'medium_clearance_days': 60,  # 预计清库天数超过60天视为中风险
    'low_clearance_days': 30,  # 预计清库天数超过30天视为低风险

    # 最小值设置
    'min_daily_sales': 0.5,  # 最小日均销量阈值
    'min_seasonal_index': 0.3,  # 季节性指数下限

    # 责任归属权重
    'forecast_accuracy_weight': 0.60,  # 预测准确性权重（提高到60%）
    'sales_response_weight': 0.25,  # 销售响应及时性权重
    'ordering_history_weight': 0.15,  # 订单历史关联权重
}


# ================ 统一CSS样式 - 与预测与计划.py完全一致 ================
def load_css():
    """加载统一CSS样式 - 完全复刻预测与计划.py"""
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
    </style>
    """, unsafe_allow_html=True)


# ================ 格式化函数 ================
def format_currency(value):
    """格式化货币显示"""
    if pd.isna(value) or value == 0:
        return "¥0"
    if value >= 100000000:  # 亿元级别
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:  # 万元级别
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"


def format_number(value):
    """格式化数字显示 - 与预测与计划.py一致，显示箱数"""
    if pd.isna(value):
        return "0 箱"
    if value == float('inf'):
        return "∞"
    return f"{value:,.0f} 箱"


def format_days(value):
    """格式化天数显示"""
    if pd.isna(value):
        return "0天"
    if value == float('inf'):
        return "∞"
    return f"{value:.0f}天"


# ================ 数据处理函数 ================
def extract_packaging(product_name):
    """从产品名称中提取包装类型"""
    try:
        if not isinstance(product_name, str):
            return "其他"

        # 检查组合类型（优先级最高）
        if re.search(r'分享装袋装', product_name):
            return '分享装袋装'
        elif re.search(r'分享装盒装', product_name):
            return '分享装盒装'
        elif re.search(r'随手包', product_name):
            return '随手包'
        elif re.search(r'迷你包', product_name):
            return '迷你包'
        elif re.search(r'分享装', product_name):
            return '分享装'
        elif re.search(r'袋装', product_name):
            return '袋装'
        elif re.search(r'盒装', product_name):
            return '盒装'
        elif re.search(r'瓶装', product_name):
            return '瓶装'

        # 处理特殊规格
        kg_match = re.search(r'(\d+(?:\.\d+)?)\s*KG', product_name, re.IGNORECASE)
        if kg_match:
            weight = float(kg_match.group(1))
            if weight >= 1.5:
                return '大包装'
            return '散装'

        g_match = re.search(r'(\d+(?:\.\d+)?)\s*G', product_name)
        if g_match:
            weight = float(g_match.group(1))
            if weight <= 50:
                return '小包装'
            elif weight <= 100:
                return '中包装'
            else:
                return '大包装'

        return '其他'
    except Exception as e:
        print(f"提取包装类型时出错: {str(e)}, 产品名称: {product_name}")
        return '其他'


def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称 - 去掉"口力"和"-中国" """
    try:
        if not isinstance(product_name, str):
            return str(product_code)

        # 应用简化规则：去掉"口力"和"-中国"
        simplified = product_name.replace('口力', '').replace('-中国', '').strip()

        if simplified:
            return simplified
        else:
            return str(product_code)

    except Exception as e:
        print(f"简化产品名称时出错: {e}，产品代码: {product_code}")
        return str(product_code)


# ================ 库存分析专用函数 ================
def calculate_inventory_risk_level(batch_age, clearance_days, volatility, forecast_bias):
    """计算库存风险等级"""
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
    if clearance_days == float('inf'):
        risk_score += 40
    elif clearance_days > 180:
        risk_score += 35
    elif clearance_days > 90:
        risk_score += 30
    elif clearance_days > 60:
        risk_score += 20
    elif clearance_days > 30:
        risk_score += 10

    # 销量波动系数 (0-10分)
    if volatility > 2.0:
        risk_score += 10
    elif volatility > 1.0:
        risk_score += 5

    # 预测偏差 (0-10分)
    if abs(forecast_bias) > 0.5:
        risk_score += 10
    elif abs(forecast_bias) > 0.3:
        risk_score += 8
    elif abs(forecast_bias) > 0.15:
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


def calculate_risk_percentage(days_to_clear, batch_age, target_days):
    """计算积压风险百分比"""
    if batch_age >= target_days:
        return 100.0

    if days_to_clear == float('inf'):
        return 100.0

    if days_to_clear >= 3 * target_days:
        return 100.0

    clearance_ratio = days_to_clear / target_days
    clearance_risk = 100 / (1 + math.exp(-4 * (clearance_ratio - 1)))

    age_risk = 100 * batch_age / target_days

    combined_risk = 0.8 * max(clearance_risk, age_risk) + 0.2 * min(clearance_risk, age_risk)

    if days_to_clear > target_days:
        combined_risk = max(combined_risk, 80)

    if days_to_clear >= 2 * target_days:
        combined_risk = max(combined_risk, 90)

    if batch_age >= 0.75 * target_days:
        combined_risk = max(combined_risk, 75)

    return min(100, round(combined_risk, 1))


# ================ 通用加载数据函数 ================
@st.cache_data
def load_data_files():
    """加载所有数据文件，返回字典格式"""
    data_dict = {}

    try:
        # 加载销售数据
        try:
            file_path = DATA_FILES['sales_data']
            if os.path.exists(file_path):
                sales_data = pd.read_excel(file_path)

                if '发运月份' in sales_data.columns:
                    sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

                sales_orders = sales_data[sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])].copy()
                sales_orders['渠道'] = sales_orders['订单类型'].apply(
                    lambda x: 'TT' if x == '订单-TT产品' else 'MT'
                )

                expense_orders = sales_data[sales_data['订单类型'].isin([
                    '陈列激励明细-F1', '促销补差支持-F1', '促销搭赠支持-F1',
                    '门店运维激励费用-F3', '全国旧日期库存处理-F3', '物料'
                ])].copy()

                if '单价（箱）' in sales_orders.columns and '求和项:数量（箱）' in sales_orders.columns:
                    sales_orders['销售额'] = sales_orders['单价（箱）'] * sales_orders['求和项:数量（箱）']
                elif '求和项:金额（元）' in sales_orders.columns:
                    sales_orders['销售额'] = sales_orders['求和项:金额（元）']
                else:
                    sales_orders['销售额'] = 0

                data_dict['sales_orders'] = sales_orders
                data_dict['expense_orders'] = expense_orders
            else:
                st.warning(f"销售数据文件不存在: {file_path}")
                data_dict['sales_orders'] = pd.DataFrame()
                data_dict['expense_orders'] = pd.DataFrame()
        except Exception as e:
            st.error(f"处理销售数据时出错: {str(e)}")
            data_dict['sales_orders'] = pd.DataFrame()
            data_dict['expense_orders'] = pd.DataFrame()

        # 加载其他通用数据文件
        for file_key in ['customer_relation', 'promotion', 'sales_target', 'customer_target',
                         'tt_product_target', 'inventory', 'month_end_inventory', 'forecast']:
            if file_key in DATA_FILES:
                file_path = DATA_FILES[file_key]
                if os.path.exists(file_path):
                    try:
                        df = pd.read_excel(file_path)
                        # 处理日期列
                        date_columns = ['指标年月', '所属年月', '月份', '促销开始供货时间', '促销结束供货时间']
                        for date_col in date_columns:
                            if date_col in df.columns:
                                df[date_col] = pd.to_datetime(df[date_col])
                        data_dict[file_key] = df
                    except Exception as e:
                        st.warning(f"处理{file_key}数据时出错: {str(e)}")
                        data_dict[file_key] = pd.DataFrame()
                else:
                    st.warning(f"文件不存在: {file_path}")
                    data_dict[file_key] = pd.DataFrame()

        # 加载产品代码列表
        for file_key in ['product_codes', 'new_product_codes']:
            if file_key in DATA_FILES:
                file_path = DATA_FILES[file_key]
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            codes = [line.strip() for line in f if line.strip()]
                        data_dict[file_key] = codes
                    except Exception as e:
                        st.warning(f"处理{file_key}时出错: {str(e)}")
                        data_dict[file_key] = []
                else:
                    st.warning(f"文件不存在: {file_path}")
                    data_dict[file_key] = []

        return data_dict

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return {}


# ================ 库存专用数据加载函数 ================
@st.cache_data
def load_inventory_data():
    """加载库存分析专用数据"""
    try:
        data_dict = {}

        # 加载批次库存数据
        batch_inventory_path = DATA_FILES['batch_inventory']
        if os.path.exists(batch_inventory_path):
            try:
                inventory_raw = pd.read_excel(batch_inventory_path)

                # 处理嵌套结构的库存数据
                product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
                inventory_data = product_rows.iloc[:, :7].copy()

                if len(inventory_data.columns) >= 7:
                    inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                              '现有库存可订量', '待入库量', '本月剩余可订量']

                # 处理批次级别数据
                batch_data = []
                current_product_code = None
                current_product_desc = None

                for i, row in inventory_raw.iterrows():
                    if pd.notna(row.iloc[0]):  # 产品行
                        current_product_code = row.iloc[0]
                        current_product_desc = row.iloc[1] if len(row) > 1 else ""
                    elif len(row) > 7 and pd.notna(row.iloc[7]):  # 批次行
                        batch_row = row.iloc[7:].copy()
                        if len(batch_row) >= 4:
                            batch_info = {
                                '产品代码': current_product_code,
                                '描述': current_product_desc,
                                '库位': batch_row.iloc[0],
                                '生产日期': batch_row.iloc[1],
                                '生产批号': batch_row.iloc[2],
                                '数量': batch_row.iloc[3]
                            }
                            batch_data.append(batch_info)

                batch_df = pd.DataFrame(batch_data)
                if not batch_df.empty and '生产日期' in batch_df.columns:
                    batch_df['生产日期'] = pd.to_datetime(batch_df['生产日期'], errors='coerce')

                data_dict['inventory_data'] = inventory_data
                data_dict['batch_data'] = batch_df
            except Exception as e:
                st.error(f"处理批次库存数据时出错: {str(e)}")
                data_dict['inventory_data'] = pd.DataFrame(columns=['产品代码', '描述', '现有库存', '已分配量',
                                                                    '现有库存可订量', '待入库量', '本月剩余可订量'])
                data_dict['batch_data'] = pd.DataFrame(
                    columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量'])
        else:
            st.warning(f"库存批次数据文件不存在: {batch_inventory_path}")
            # 创建空的 DataFrame 避免后续处理错误
            data_dict['inventory_data'] = pd.DataFrame(columns=['产品代码', '描述', '现有库存', '已分配量',
                                                                '现有库存可订量', '待入库量', '本月剩余可订量'])
            data_dict['batch_data'] = pd.DataFrame(columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量'])

        # 加载出货数据 - 修复列名映射
        shipping_data_path = DATA_FILES['shipping_data']
        if os.path.exists(shipping_data_path):
            try:
                shipping_data = pd.read_excel(shipping_data_path)

                # 检查并重命名列名
                if '求和项:数量（箱）' in shipping_data.columns:
                    shipping_data = shipping_data.rename(columns={'求和项:数量（箱）': '数量'})

                # 标准化处理
                shipping_data['订单日期'] = pd.to_datetime(shipping_data['订单日期'])
                shipping_data['数量'] = pd.to_numeric(shipping_data['数量'], errors='coerce')
                shipping_data = shipping_data.dropna(subset=['数量'])

                data_dict['shipping_data'] = shipping_data
            except Exception as e:
                st.error(f"处理出货数据时出错: {str(e)}")
                data_dict['shipping_data'] = pd.DataFrame(
                    columns=['订单日期', '所属区域', '申请人', '产品代码', '数量'])
        else:
            st.warning(f"出货数据文件不存在: {shipping_data_path}")
            data_dict['shipping_data'] = pd.DataFrame(columns=['订单日期', '所属区域', '申请人', '产品代码', '数量'])

        # 加载预测数据
        forecast_data_path = DATA_FILES['inventory_forecast']
        if os.path.exists(forecast_data_path):
            try:
                forecast_data = pd.read_excel(forecast_data_path)

                # 标准化处理
                forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])
                forecast_data['预计销售量'] = pd.to_numeric(forecast_data['预计销售量'], errors='coerce')
                forecast_data = forecast_data.dropna(subset=['预计销售量'])

                data_dict['forecast_data'] = forecast_data
            except Exception as e:
                st.error(f"处理预测数据时出错: {str(e)}")
                data_dict['forecast_data'] = pd.DataFrame(
                    columns=['所属大区', '销售员', '所属年月', '产品代码', '预计销售量'])
        else:
            st.warning(f"预测数据文件不存在: {forecast_data_path}")
            data_dict['forecast_data'] = pd.DataFrame(
                columns=['所属大区', '销售员', '所属年月', '产品代码', '预计销售量'])

        # 加载单价数据
        price_data_path = DATA_FILES['price_data']
        if os.path.exists(price_data_path):
            try:
                price_df = pd.read_excel(price_data_path)
                price_dict = {}
                for _, row in price_df.iterrows():
                    price_dict[row['产品代码']] = row['单价']
                data_dict['price_data'] = price_dict
            except Exception as e:
                st.error(f"处理单价数据时出错: {str(e)}")
                # 默认单价数据
                data_dict['price_data'] = {
                    'F01E4B': 137.04, 'F3411A': 137.04, 'F0104L': 126.72,
                    'F3406B': 129.36, 'F01C5D': 153.6, 'F01L3A': 182.4
                }
        else:
            st.warning(f"单价数据文件不存在: {price_data_path}")
            # 默认单价数据
            data_dict['price_data'] = {
                'F01E4B': 137.04, 'F3411A': 137.04, 'F0104L': 126.72,
                'F3406B': 129.36, 'F01C5D': 153.6, 'F01L3A': 182.4
            }

        return data_dict

    except Exception as e:
        st.error(f"库存数据加载失败: {str(e)}")
        return {}


# ================ 筛选器函数 ================
def create_filters(data, page_name=None):
    """创建统一筛选器，每个页面独立状态"""
    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        st.warning("无法加载筛选器，数据不完整")
        return data

    region_key = f"{page_name}_filter_region" if page_name else "filter_region"
    person_key = f"{page_name}_filter_person" if page_name else "filter_person"
    customer_key = f"{page_name}_filter_customer" if page_name else "filter_customer"
    date_key = f"{page_name}_filter_date_range" if page_name else "filter_date_range"

    if region_key not in st.session_state:
        st.session_state[region_key] = '全部'
    if person_key not in st.session_state:
        st.session_state[person_key] = '全部'
    if customer_key not in st.session_state:
        st.session_state[customer_key] = '全部'
    if date_key not in st.session_state:
        current_year = datetime.now().year
        st.session_state[date_key] = (
            datetime(current_year, 1, 1),
            datetime(current_year, 12, 31)
        )

    sales_data = data['sales_orders']

    with st.sidebar:
        st.markdown("## 🔍 数据筛选")
        st.markdown("---")

        if '所属区域' in sales_data.columns:
            all_regions = sorted(['全部'] + list(sales_data['所属区域'].unique()))
            selected_region = st.sidebar.selectbox(
                "选择区域", all_regions, index=0, key=f"{page_name}_sidebar_region"
            )
            st.session_state[region_key] = selected_region

        if '申请人' in sales_data.columns:
            all_persons = sorted(['全部'] + list(sales_data['申请人'].unique()))
            selected_person = st.sidebar.selectbox(
                "选择销售员", all_persons, index=0, key=f"{page_name}_sidebar_person"
            )
            st.session_state[person_key] = selected_person

        customer_relation = data.get('customer_relation', pd.DataFrame())
        customer_col = None
        for col in ['客户', '客户简称', '经销商名称']:
            if col in customer_relation.columns:
                customer_col = col
                break

        if customer_col and not customer_relation.empty:
            if '状态' in customer_relation.columns:
                active_customers = customer_relation[customer_relation['状态'] == '正常']
            else:
                active_customers = customer_relation

            all_customers = sorted(['全部'] + list(active_customers[customer_col].unique()))
            selected_customer = st.sidebar.selectbox(
                "选择客户", all_customers, index=0, key=f"{page_name}_sidebar_customer"
            )
            st.session_state[customer_key] = selected_customer

        if '发运月份' in sales_data.columns:
            try:
                sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])
                min_date = sales_data['发运月份'].min().date()
                max_date = sales_data['发运月份'].max().date()

                current_start, current_end = st.session_state[date_key]
                current_start = current_start.date() if hasattr(current_start, 'date') else current_start
                current_end = current_end.date() if hasattr(current_end, 'date') else current_end

                current_start = max(current_start, min_date)
                current_end = min(current_end, max_date)

                st.sidebar.markdown("### 日期范围")
                start_date = st.sidebar.date_input(
                    "开始日期", value=current_start, min_value=min_date, max_value=max_date,
                    key=f"{page_name}_sidebar_start_date"
                )
                end_date = st.sidebar.date_input(
                    "结束日期", value=current_end, min_value=min_date, max_value=max_date,
                    key=f"{page_name}_sidebar_end_date"
                )

                if end_date < start_date:
                    end_date = start_date
                    st.sidebar.warning("结束日期不能早于开始日期，已自动调整。")

                st.session_state[date_key] = (start_date, end_date)

            except Exception as e:
                st.sidebar.warning(f"日期筛选器初始化失败: {e}")

        if st.sidebar.button("重置筛选条件", key=f"{page_name}_reset_filters"):
            st.session_state[region_key] = '全部'
            st.session_state[person_key] = '全部'
            st.session_state[customer_key] = '全部'
            current_year = datetime.now().year
            st.session_state[date_key] = (
                datetime(current_year, 1, 1),
                datetime(current_year, 12, 31)
            )
            st.rerun()

    return apply_filters(data, page_name)


def apply_filters(data, page_name=None):
    """应用筛选条件到数据"""
    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        return data

    region_key = f"{page_name}_filter_region" if page_name else "filter_region"
    person_key = f"{page_name}_filter_person" if page_name else "filter_person"
    customer_key = f"{page_name}_filter_customer" if page_name else "filter_customer"
    date_key = f"{page_name}_filter_date_range" if page_name else "filter_date_range"

    filtered_data = data.copy()
    sales_data = filtered_data['sales_orders'].copy()

    if region_key in st.session_state and st.session_state[region_key] != '全部' and '所属区域' in sales_data.columns:
        sales_data = sales_data[sales_data['所属区域'] == st.session_state[region_key]]

    if person_key in st.session_state and st.session_state[person_key] != '全部':
        person_col = None
        for col in ['申请人', '销售员']:
            if col in sales_data.columns:
                person_col = col
                break
        if person_col:
            sales_data = sales_data[sales_data[person_col] == st.session_state[person_key]]

    if customer_key in st.session_state and st.session_state[customer_key] != '全部':
        try:
            customer_cols = [col for col in sales_data.columns if '客户' in col or '经销商' in col]
            found = False
            for col in customer_cols:
                if st.session_state[customer_key] in sales_data[col].values:
                    sales_data = sales_data[sales_data[col] == st.session_state[customer_key]]
                    found = True
                    break
            if not found:
                for col in customer_cols:
                    mask = sales_data[col].astype(str).str.contains(st.session_state[customer_key], case=False,
                                                                    na=False)
                    if mask.any():
                        sales_data = sales_data[mask]
                        break
        except Exception as e:
            st.sidebar.warning(f"客户筛选应用失败: {e}")

    if date_key in st.session_state and '发运月份' in sales_data.columns:
        try:
            start_date, end_date = st.session_state[date_key]
            start_date = pd.to_datetime(start_date) if not isinstance(start_date, pd.Timestamp) else start_date
            end_date = pd.to_datetime(end_date) if not isinstance(end_date, pd.Timestamp) else end_date
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])
            sales_data = sales_data[
                (sales_data['发运月份'] >= pd.Timestamp(start_date.year, start_date.month, start_date.day, 0, 0, 0)) &
                (sales_data['发运月份'] <= pd.Timestamp(end_date.year, end_date.month, end_date.day, 23, 59, 59))
                ]
        except Exception as e:
            st.sidebar.warning(f"日期筛选应用失败: {e}")

    filtered_data['sales_orders'] = sales_data
    return filtered_data


# ================ 图表解释函数 ================
def add_chart_explanation(explanation_text):
    """添加图表解释 - 与预测与计划.py一致的样式"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# ================ 翻卡组件函数 ================
def create_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False, is_number=False):
    """创建统一的翻卡组件"""
    flip_key = f"flip_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = 0

    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    elif is_number:
        formatted_value = format_number(value)
    else:
        formatted_value = str(value)

    card_container = st.container()

    with card_container:
        if st.button(f"查看{title}详情", key=f"btn_{card_id}", help=f"点击查看{title}的详细分析"):
            st.session_state[flip_key] = (st.session_state[flip_key] + 1) % 3

        current_layer = st.session_state[flip_key]

        if current_layer == 0:
            st.markdown(f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 10px; 
                        box-shadow: 0 0.25rem 1.25rem 0 rgba(58, 59, 69, 0.15); 
                        text-align: center; min-height: 200px; display: flex; 
                        flex-direction: column; justify-content: center; transition: transform 0.3s ease;">
                <h3 style="color: {COLORS['primary']}; margin-bottom: 1rem; font-weight: 600;">{title}</h3>
                <h1 style="color: {COLORS['primary']}; margin-bottom: 0.8rem; font-weight: 700;">{formatted_value}</h1>
                <p style="color: {COLORS['gray']}; margin-bottom: 1rem;">{subtitle}</p>
                <p style="color: {COLORS['secondary']}; font-size: 0.9rem;">点击查看分析 →</p>
            </div>
            """, unsafe_allow_html=True)

        return current_layer


# ================ 全局页面设置 ================
def setup_page():
    """设置页面配置"""
    st.set_page_config(
        page_title="销售数据分析仪表盘",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_css()


# ================ 辅助函数 ================
def get_safe_column(df, possible_names, default=None):
    """安全地获取数据框中的列，通过检查多个可能的列名"""
    for name in possible_names:
        if name in df.columns:
            return name
    return default


def sanitize_data(df, column, default_value=0):
    """清理和验证数据列的值"""
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').fillna(default_value)
    return df


# 预测准确率分析新增函数
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


# 优化备货建议生成函数
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