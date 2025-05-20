# config.py - 统一配置和共享函数
import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

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

# ================ 数据文件路径 ================
DATA_FILES = {
    'sales_data': "仪表盘原始数据.xlsx",  # 销售原始数据
    'sales_target': "仪表盘销售月度指标维护.xlsx",  # 销售目标
    'customer_target': "仪表盘客户月度指标维护.xlsx",  # 客户指标
    'tt_product_target': "仪表盘TT产品月度指标.xlsx",  # TT产品指标
    'promotion': "仪表盘促销活动.xlsx",  # 促销活动
    'inventory': "仪表盘实时库存.xlsx",  # 实时库存
    'month_end_inventory': "仪表盘月终月末库存.xlsx",  # 月末库存
    'forecast': "仪表盘人工预测.xlsx",  # 人工预测
    'product_codes': "仪表盘产品代码.txt",  # 产品代码列表
    'new_product_codes': "仪表盘新品代码.txt",  # 新品产品代码
    'customer_relation': "仪表盘人与客户关系表.xlsx"  # 客户关系表
}


# ================ 统一CSS样式 ================
def load_css():
    """加载统一CSS样式"""
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

        /* 主要头部样式 */
        .main-header {
            font-size: 2rem;
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }

        /* 卡片样式 */
        .card-header {
            font-size: 1.2rem;
            font-weight: 600;
            color: #444444;
            margin-bottom: 0.5rem;
        }

        .card-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .metric-card {
            background-color: white;
            border-radius: 8px;
            padding: 1.2rem;
            box-shadow: 0 0.15rem 1.2rem 0 rgba(58, 59, 69, 0.15);
            margin-bottom: 1.2rem;
            transition: transform 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-3px);
        }

        .card-text {
            font-size: 0.9rem;
            color: var(--gray-color);
        }

        /* 提示框样式 */
        .alert-box {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .alert-success {
            background-color: rgba(76, 175, 80, 0.1);
            border-left: 0.5rem solid var(--success-color);
        }

        .alert-warning {
            background-color: rgba(255, 152, 0, 0.1);
            border-left: 0.5rem solid var(--warning-color);
        }

        .alert-danger {
            background-color: rgba(244, 67, 54, 0.1);
            border-left: 0.5rem solid var(--danger-color);
        }

        /* 子标题样式 */
        .sub-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--accent-color);
        }

        /* 图表解释框 */
        .chart-explanation {
            background-color: rgba(76, 175, 80, 0.1);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 0.5rem solid var(--success-color);
        }

        /* 按钮样式 */
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color);
            box-shadow: 0 0.15rem 1rem 0 rgba(58, 59, 69, 0.15);
        }

        /* 加载器样式 */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
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
    """格式化数字显示"""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


# ================ 数据处理函数 ================
def extract_packaging(product_name):
    """从产品名称中提取包装类型"""
    try:
        # 确保输入是字符串
        if not isinstance(product_name, str):
            return "其他"

        # 检查组合类型（优先级最高）
        if re.search(r'分享装袋装', product_name):
            return '分享装袋装'
        elif re.search(r'分享装盒装', product_name):
            return '分享装盒装'

        # 按包装大小分类（从大到小）
        elif re.search(r'随手包', product_name):
            return '随手包'
        elif re.search(r'迷你包', product_name):
            return '迷你包'
        elif re.search(r'分享装', product_name):
            return '分享装'

        # 按包装形式分类
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

        # 默认分类
        return '其他'
    except Exception as e:
        print(f"提取包装类型时出错: {str(e)}, 产品名称: {product_name}")
        return '其他'  # 捕获任何异常并返回默认值


def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称"""
    try:
        # 确保输入是字符串类型
        if not isinstance(product_name, str):
            return str(product_code)  # 返回产品代码作为备选

        if '口力' in product_name:
            # 提取"口力"之后的产品类型
            name_parts = product_name.split('口力')
            if len(name_parts) > 1:
                name_part = name_parts[1]
                if '-' in name_part:
                    name_part = name_part.split('-')[0].strip()

                # 进一步简化，只保留主要部分（去掉规格和包装形式）
                for suffix in ['G分享装袋装', 'G盒装', 'G袋装', 'KG迷你包', 'KG随手包']:
                    if suffix in name_part:
                        name_part = name_part.split(suffix)[0]
                        break

                # 去掉可能的数字和单位
                simple_name = re.sub(r'\d+\w*\s*', '', name_part).strip()

                if simple_name:  # 确保简化名称不为空
                    return f"{simple_name} ({product_code})"

        # 如果无法提取或处理中出现错误，则返回产品代码
        return str(product_code)
    except Exception as e:
        # 捕获任何异常，确保函数始终返回一个字符串
        print(f"简化产品名称时出错: {e}，产品代码: {product_code}")
        return str(product_code)


# ================ 通用加载数据函数 ================
@st.cache_data
def load_data_files():
    """加载所有数据文件，返回字典格式"""
    data_dict = {}

    try:
        # 检查必要的文件是否存在
        missing_files = [file for file, path in DATA_FILES.items()
                         if not os.path.exists(path) and file in ['sales_data']]
        if missing_files:
            st.error(f"缺少关键数据文件: {', '.join(missing_files)}")
            return None

        # 加载销售数据
        try:
            sales_data = pd.read_excel(DATA_FILES['sales_data'])
            # 处理日期列
            if '发运月份' in sales_data.columns:
                sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

            # 过滤销售订单
            sales_orders = sales_data[sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])].copy()

            # 添加渠道字段
            sales_orders['渠道'] = sales_orders['订单类型'].apply(
                lambda x: 'TT' if x == '订单-TT产品' else 'MT'
            )

            # 过滤费用订单
            expense_orders = sales_data[sales_data['订单类型'].isin([
                '陈列激励明细-F1', '促销补差支持-F1', '促销搭赠支持-F1',
                '门店运维激励费用-F3', '全国旧日期库存处理-F3', '物料'
            ])].copy()

            # 计算销售额 - 灵活处理列名
            if '单价（箱）' in sales_orders.columns and '求和项:数量（箱）' in sales_orders.columns:
                sales_orders['销售额'] = sales_orders['单价（箱）'] * sales_orders['求和项:数量（箱）']
            elif '单价（箱）' in sales_orders.columns and '数量（箱）' in sales_orders.columns:
                sales_orders['销售额'] = sales_orders['单价（箱）'] * sales_orders['数量（箱）']
            elif '求和项:金额（元）' in sales_orders.columns:
                sales_orders['销售额'] = sales_orders['求和项:金额（元）']
            else:
                # 尝试查找任何可能表示金额的列
                possible_amount_columns = [col for col in sales_orders.columns
                                           if '金额' in col or '销售额' in col]
                if possible_amount_columns:
                    sales_orders['销售额'] = sales_orders[possible_amount_columns[0]]
                else:
                    st.warning("无法确定销售额列，请检查数据格式。")
                    sales_orders['销售额'] = 0

            data_dict['sales_orders'] = sales_orders
            data_dict['expense_orders'] = expense_orders
        except Exception as e:
            st.error(f"处理销售数据时出错: {str(e)}")
            # 创建最小化的数据集以避免完全失败
            data_dict['sales_orders'] = pd.DataFrame(columns=['客户简称', '所属区域', '发运月份',
                                                              '申请人', '产品代码', '销售额'])
            data_dict['expense_orders'] = pd.DataFrame()

        # 加载客户关系表 - 更加健壮的加载方式
        try:
            customer_relation = pd.read_excel(DATA_FILES['customer_relation'])
            # 检查是否存在客户代码列，如果没有则尝试创建映射
            if '客户代码' not in customer_relation.columns:
                st.warning("客户关系表中未找到'客户代码'列，将尝试创建映射。")

                # 从销售数据中提取客户代码和客户名称的对应关系
                if 'sales_orders' in data_dict and not data_dict['sales_orders'].empty:
                    sales_orders = data_dict['sales_orders']
                    # 查找可能的客户列
                    customer_name_cols = [col for col in sales_orders.columns
                                          if '客户' in col or '经销商' in col]
                    customer_code_cols = [col for col in sales_orders.columns
                                          if '客户代码' in col or 'client_id' in col]

                    if customer_name_cols and customer_code_cols:
                        # 创建客户名称到代码的映射
                        customer_mapping = sales_orders[
                            [customer_code_cols[0], customer_name_cols[0]]].drop_duplicates()

                        # 为客户关系表添加客户代码列
                        if '客户' in customer_relation.columns:
                            customer_relation = customer_relation.merge(
                                customer_mapping,
                                left_on='客户',
                                right_on=customer_name_cols[0],
                                how='left'
                            )
                            # 重命名映射的列为客户代码
                            customer_relation.rename(columns={customer_code_cols[0]: '客户代码'}, inplace=True)
                        else:
                            # 如果连"客户"列都没有，使用"销售员"列进行关联
                            if '销售员' in customer_relation.columns:
                                # 为每个销售员分配一个唯一标识作为客户代码
                                customer_relation['客户代码'] = 'C' + customer_relation.index.astype(str)
                                st.warning("客户关系表中无法确定客户列，已使用销售员创建临时映射。")

            # 筛选正常状态的客户
            if '状态' in customer_relation.columns:
                active_customers = customer_relation[customer_relation['状态'] == '正常']
            else:
                active_customers = customer_relation.copy()
                active_customers['状态'] = '正常'  # 为所有客户添加"正常"状态
                st.warning("客户关系表中没有状态列，已假设所有客户为'正常'状态。")

            data_dict['customer_relation'] = customer_relation
            data_dict['active_customers'] = active_customers
        except Exception as e:
            st.error(f"处理客户关系表时出错: {str(e)}")
            # 创建最小化的客户关系数据
            data_dict['customer_relation'] = pd.DataFrame(columns=['销售员', '客户', '状态', '客户代码'])
            data_dict['active_customers'] = pd.DataFrame(columns=['销售员', '客户', '状态', '客户代码'])

        # 加载促销活动数据
        try:
            if os.path.exists(DATA_FILES['promotion']):
                promotion_data = pd.read_excel(DATA_FILES['promotion'])
                if '促销开始供货时间' in promotion_data.columns:
                    promotion_data['促销开始供货时间'] = pd.to_datetime(promotion_data['促销开始供货时间'])
                if '促销结束供货时间' in promotion_data.columns:
                    promotion_data['促销结束供货时间'] = pd.to_datetime(promotion_data['促销结束供货时间'])
                data_dict['promotion_data'] = promotion_data
        except Exception as e:
            st.warning(f"处理促销活动数据时出错: {str(e)}")
            data_dict['promotion_data'] = pd.DataFrame()

        # 加载销售指标数据
        try:
            if os.path.exists(DATA_FILES['sales_target']):
                sales_target = pd.read_excel(DATA_FILES['sales_target'])
                if '指标年月' in sales_target.columns:
                    sales_target['指标年月'] = pd.to_datetime(sales_target['指标年月'])
                data_dict['sales_target'] = sales_target
        except Exception as e:
            st.warning(f"处理销售指标数据时出错: {str(e)}")
            data_dict['sales_target'] = pd.DataFrame()

        # 加载客户指标数据
        try:
            if os.path.exists(DATA_FILES['customer_target']):
                customer_target = pd.read_excel(DATA_FILES['customer_target'])
                if '月份' in customer_target.columns:
                    customer_target['月份'] = pd.to_datetime(customer_target['月份'])
                data_dict['customer_target'] = customer_target
        except Exception as e:
            st.warning(f"处理客户指标数据时出错: {str(e)}")
            data_dict['customer_target'] = pd.DataFrame()

        # 加载TT产品指标数据
        try:
            if os.path.exists(DATA_FILES['tt_product_target']):
                tt_target = pd.read_excel(DATA_FILES['tt_product_target'])
                if '指标年月' in tt_target.columns:
                    tt_target['指标年月'] = pd.to_datetime(tt_target['指标年月'])
                data_dict['tt_target'] = tt_target
        except Exception as e:
            st.warning(f"处理TT产品指标数据时出错: {str(e)}")
            data_dict['tt_target'] = pd.DataFrame()

        # 加载库存数据
        try:
            if os.path.exists(DATA_FILES['inventory']):
                inventory_data = pd.read_excel(DATA_FILES['inventory'])
                data_dict['inventory_data'] = inventory_data
        except Exception as e:
            st.warning(f"处理实时库存数据时出错: {str(e)}，将使用简化的库存数据")
            data_dict['inventory_data'] = pd.DataFrame(columns=['物料', '描述', '现有库存'])

        # 加载月末库存数据
        try:
            if os.path.exists(DATA_FILES['month_end_inventory']):
                month_end_inventory = pd.read_excel(DATA_FILES['month_end_inventory'])
                if '所属年月' in month_end_inventory.columns:
                    month_end_inventory['所属年月'] = pd.to_datetime(month_end_inventory['所属年月'])
                data_dict['month_end_inventory'] = month_end_inventory
        except Exception as e:
            st.warning(f"处理月末库存数据时出错: {str(e)}")
            data_dict['month_end_inventory'] = pd.DataFrame()

        # 加载预测数据
        try:
            if os.path.exists(DATA_FILES['forecast']):
                forecast_data = pd.read_excel(DATA_FILES['forecast'])
                if '所属年月' in forecast_data.columns:
                    forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])
                data_dict['forecast_data'] = forecast_data
        except Exception as e:
            st.warning(f"处理预测数据时出错: {str(e)}")
            data_dict['forecast_data'] = pd.DataFrame()

        # 加载产品代码列表
        try:
            if os.path.exists(DATA_FILES['product_codes']):
                with open(DATA_FILES['product_codes'], 'r', encoding='utf-8') as f:
                    product_codes = [line.strip() for line in f if line.strip()]
                data_dict['product_codes'] = product_codes
            else:
                # 如果文件不存在，从销售数据中提取产品代码
                if 'sales_orders' in data_dict and '产品代码' in data_dict['sales_orders'].columns:
                    product_codes = data_dict['sales_orders']['产品代码'].unique().tolist()
                    data_dict['product_codes'] = product_codes
                else:
                    data_dict['product_codes'] = []
        except Exception as e:
            st.warning(f"处理产品代码列表时出错: {str(e)}")
            data_dict['product_codes'] = []

        # 加载新品代码列表
        try:
            if os.path.exists(DATA_FILES['new_product_codes']):
                with open(DATA_FILES['new_product_codes'], 'r', encoding='utf-8') as f:
                    new_product_codes = [line.strip() for line in f if line.strip()]
                data_dict['new_product_codes'] = new_product_codes
            else:
                data_dict['new_product_codes'] = []
        except Exception as e:
            st.warning(f"处理新品代码列表时出错: {str(e)}")
            data_dict['new_product_codes'] = []

        # 添加简化产品名称和包装类型
        try:
            if 'sales_orders' in data_dict and not data_dict['sales_orders'].empty:
                sales_orders = data_dict['sales_orders']
                if '产品名称' in sales_orders.columns and '产品代码' in sales_orders.columns:
                    sales_orders['简化产品名称'] = sales_orders.apply(
                        lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
                        axis=1
                    )
                    sales_orders['包装类型'] = sales_orders['产品名称'].apply(extract_packaging)
                    data_dict['sales_orders'] = sales_orders
        except Exception as e:
            st.warning(f"处理产品名称和包装类型时出错: {str(e)}")

        return data_dict

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None


# ================ 筛选器函数 - 增强版 ================
def create_filters(data, page_name=None):
    """创建统一筛选器，每个页面独立状态"""
    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        st.warning("无法加载筛选器，数据不完整")
        return data

    # 为每个页面创建独立的session状态键
    region_key = f"{page_name}_filter_region" if page_name else "filter_region"
    person_key = f"{page_name}_filter_person" if page_name else "filter_person"
    customer_key = f"{page_name}_filter_customer" if page_name else "filter_customer"
    date_key = f"{page_name}_filter_date_range" if page_name else "filter_date_range"

    # 初始化筛选状态
    if region_key not in st.session_state:
        st.session_state[region_key] = '全部'
    if person_key not in st.session_state:
        st.session_state[person_key] = '全部'
    if customer_key not in st.session_state:
        st.session_state[customer_key] = '全部'
    if date_key not in st.session_state:
        # 默认显示当年数据
        current_year = datetime.now().year
        st.session_state[date_key] = (
            datetime(current_year, 1, 1),
            datetime(current_year, 12, 31)
        )

    sales_data = data['sales_orders']

    with st.sidebar:
        st.markdown("## 🔍 数据筛选")
        st.markdown("---")

        # 区域筛选器
        if '所属区域' in sales_data.columns:
            all_regions = sorted(['全部'] + list(sales_data['所属区域'].unique()))
            selected_region = st.sidebar.selectbox(
                "选择区域", all_regions, index=0, key=f"{page_name}_sidebar_region"
            )
            st.session_state[region_key] = selected_region

        # 销售员筛选器
        if '申请人' in sales_data.columns:
            all_persons = sorted(['全部'] + list(sales_data['申请人'].unique()))
            selected_person = st.sidebar.selectbox(
                "选择销售员", all_persons, index=0, key=f"{page_name}_sidebar_person"
            )
            st.session_state[person_key] = selected_person

        # 客户筛选器 - 更健壮的实现
        customer_relation = data.get('customer_relation', pd.DataFrame())

        # 检查客户关系表
        customer_col = None
        for col in ['客户', '客户简称', '经销商名称']:
            if col in customer_relation.columns:
                customer_col = col
                break

        if customer_col and not customer_relation.empty:
            # 筛选状态为"正常"的客户
            if '状态' in customer_relation.columns:
                active_customers = customer_relation[customer_relation['状态'] == '正常']
            else:
                active_customers = customer_relation

            all_customers = sorted(['全部'] + list(active_customers[customer_col].unique()))
            selected_customer = st.sidebar.selectbox(
                "选择客户", all_customers, index=0, key=f"{page_name}_sidebar_customer"
            )
            st.session_state[customer_key] = selected_customer

        # 日期范围筛选器
        if '发运月份' in sales_data.columns:
            try:
                # 确保日期列是日期时间类型
                sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

                min_date = sales_data['发运月份'].min().date()
                max_date = sales_data['发运月份'].max().date()

                # 获取当前的日期范围值
                current_start, current_end = st.session_state[date_key]

                # 确保是日期对象
                current_start = current_start.date() if hasattr(current_start, 'date') else current_start
                current_end = current_end.date() if hasattr(current_end, 'date') else current_end

                # 确保当前选择的日期在有效范围内
                current_start = max(current_start, min_date)
                current_end = min(current_end, max_date)

                st.sidebar.markdown("### 日期范围")
                # 日期选择器
                start_date = st.sidebar.date_input(
                    "开始日期",
                    value=current_start,
                    min_value=min_date,
                    max_value=max_date,
                    key=f"{page_name}_sidebar_start_date"
                )

                end_date = st.sidebar.date_input(
                    "结束日期",
                    value=current_end,
                    min_value=min_date,
                    max_value=max_date,
                    key=f"{page_name}_sidebar_end_date"
                )

                # 确保结束日期不早于开始日期
                if end_date < start_date:
                    end_date = start_date
                    st.sidebar.warning("结束日期不能早于开始日期，已自动调整。")

                # 更新会话状态
                st.session_state[date_key] = (start_date, end_date)

            except Exception as e:
                st.sidebar.warning(f"日期筛选器初始化失败: {e}")

        # 添加重置筛选器按钮
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

    # 返回筛选后的数据
    return apply_filters(data, page_name)


def apply_filters(data, page_name=None):
    """应用筛选条件到数据 - 更健壮的实现"""
    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        return data

    # 获取页面特定的筛选器键
    region_key = f"{page_name}_filter_region" if page_name else "filter_region"
    person_key = f"{page_name}_filter_person" if page_name else "filter_person"
    customer_key = f"{page_name}_filter_customer" if page_name else "filter_customer"
    date_key = f"{page_name}_filter_date_range" if page_name else "filter_date_range"

    filtered_data = data.copy()
    sales_data = filtered_data['sales_orders'].copy()

    # 应用区域筛选
    if region_key in st.session_state and st.session_state[region_key] != '全部' and '所属区域' in sales_data.columns:
        sales_data = sales_data[sales_data['所属区域'] == st.session_state[region_key]]

    # 应用销售员筛选
    if person_key in st.session_state and st.session_state[person_key] != '全部':
        person_col = None
        for col in ['申请人', '销售员']:
            if col in sales_data.columns:
                person_col = col
                break

        if person_col:
            sales_data = sales_data[sales_data[person_col] == st.session_state[person_key]]

    # 应用客户筛选 - 更健壮的实现
    if customer_key in st.session_state and st.session_state[customer_key] != '全部':
        try:
            # 1. 直接在销售数据中查找客户
            customer_cols = [col for col in sales_data.columns if '客户' in col or '经销商' in col]
            found = False

            for col in customer_cols:
                if st.session_state[customer_key] in sales_data[col].values:
                    sales_data = sales_data[sales_data[col] == st.session_state[customer_key]]
                    found = True
                    break

            # 2. 如果直接查找失败，尝试通过客户关系表进行匹配
            if not found and 'customer_relation' in filtered_data:
                customer_relation = filtered_data['customer_relation']
                # 查找匹配的客户列
                cr_customer_col = None
                for col in ['客户', '客户简称', '经销商名称']:
                    if col in customer_relation.columns and st.session_state[customer_key] in customer_relation[
                        col].values:
                        cr_customer_col = col
                        break

                if cr_customer_col:
                    # 查找客户对应的代码列
                    cr_code_col = None
                    for col in ['客户代码', 'client_id']:
                        if col in customer_relation.columns:
                            cr_code_col = col
                            break

                    if cr_code_col:
                        # 获取客户代码
                        customer_codes = \
                        customer_relation[customer_relation[cr_customer_col] == st.session_state[customer_key]][
                            cr_code_col].tolist()

                        # 在销售数据中查找匹配的客户代码列
                        sales_code_col = None
                        for col in ['客户代码', 'client_id']:
                            if col in sales_data.columns:
                                sales_code_col = col
                                break

                        if sales_code_col and customer_codes:
                            sales_data = sales_data[sales_data[sales_code_col].isin(customer_codes)]
                            found = True

            # 3. 如果仍未找到匹配，尝试模糊匹配
            if not found:
                for col in customer_cols:
                    mask = sales_data[col].astype(str).str.contains(st.session_state[customer_key], case=False,
                                                                    na=False)
                    if mask.any():
                        sales_data = sales_data[mask]
                        found = True
                        break

            if not found:
                st.sidebar.warning(f"未找到匹配的客户: {st.session_state[customer_key]}")

        except Exception as e:
            st.sidebar.warning(f"客户筛选应用失败: {e}")

    # 应用日期范围筛选
    if date_key in st.session_state and '发运月份' in sales_data.columns:
        try:
            start_date, end_date = st.session_state[date_key]

            # 确保日期类型一致
            start_date = pd.to_datetime(start_date) if not isinstance(start_date, pd.Timestamp) else start_date
            end_date = pd.to_datetime(end_date) if not isinstance(end_date, pd.Timestamp) else end_date

            # 确保销售数据日期列是日期时间类型
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

            # 应用日期筛选 - 使用整天范围
            sales_data = sales_data[
                (sales_data['发运月份'] >= pd.Timestamp(start_date.year, start_date.month, start_date.day, 0, 0, 0)) &
                (sales_data['发运月份'] <= pd.Timestamp(end_date.year, end_date.month, end_date.day, 23, 59, 59))
                ]
        except Exception as e:
            st.sidebar.warning(f"日期筛选应用失败: {e}")

    # 更新过滤后的销售数据
    filtered_data['sales_orders'] = sales_data

    return filtered_data


# ================ 图表解释函数 ================
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# ================ 认证函数 ================
def check_authentication():
    """检查用户认证"""
    # 初始化认证状态
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown(
            '<div style="font-size: 1.8rem; color: #1f3867; text-align: center; margin-bottom: 2rem; font-weight: 600;">销售数据分析仪表盘 | 登录</div>',
            unsafe_allow_html=True)

        # 创建居中的登录框
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("""
            <div style="padding: 2rem; border-radius: 10px; border: 1px solid #ddd; box-shadow: 0 0.25rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
                <h2 style="text-align: center; color: #1f3867; margin-bottom: 1.5rem; font-weight: 600;">请输入密码</h2>
            </div>
            """, unsafe_allow_html=True)

            # 密码输入框
            password = st.text_input("密码", type="password", key="password_input")

            # 登录按钮
            login_button = st.button("登录", key="login_button")

            # 验证密码
            if login_button:
                if password == 'SAL!2025':
                    st.session_state.authenticated = True
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("密码错误，请重试！")

        # 如果未认证，不显示后续内容
        return False

    return True


# ================ 翻卡组件函数 ================
def create_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False, is_number=False):
    """创建统一的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"flip_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = 0

    # 格式化值
    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    elif is_number:
        formatted_value = format_number(value)
    else:
        formatted_value = str(value)

    # 创建卡片容器
    card_container = st.container()

    with card_container:
        # 点击按钮
        if st.button(f"查看{title}详情", key=f"btn_{card_id}", help=f"点击查看{title}的详细分析"):
            st.session_state[flip_key] = (st.session_state[flip_key] + 1) % 3

        current_layer = st.session_state[flip_key]

        if current_layer == 0:
            # 第一层：基础指标
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

    # 加载CSS样式
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
        # 替换非数值数据为默认值
        df[column] = pd.to_numeric(df[column], errors='coerce').fillna(default_value)
    return df