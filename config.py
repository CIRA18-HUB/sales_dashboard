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
        .stButton > button {
            background-color: #1f3867;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #4c78a8;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
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
        # 检查所有文件是否存在
        for key, filepath in DATA_FILES.items():
            if not os.path.exists(filepath):
                st.error(f"数据文件不存在: {filepath}")
                return None

        # 加载销售数据
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

        # 计算销售额
        if '单价（箱）' in sales_orders.columns and '求和项:数量（箱）' in sales_orders.columns:
            sales_orders['销售额'] = sales_orders['单价（箱）'] * sales_orders['求和项:数量（箱）']
        elif '求和项:金额（元）' in sales_orders.columns:
            sales_orders['销售额'] = sales_orders['求和项:金额（元）']

        # 加载促销活动
        promotion_data = pd.read_excel(DATA_FILES['promotion'])
        if '促销开始供货时间' in promotion_data.columns:
            promotion_data['促销开始供货时间'] = pd.to_datetime(promotion_data['促销开始供货时间'])
        if '促销结束供货时间' in promotion_data.columns:
            promotion_data['促销结束供货时间'] = pd.to_datetime(promotion_data['促销结束供货时间'])

        # 加载销售指标
        sales_target = pd.read_excel(DATA_FILES['sales_target'])
        if '指标年月' in sales_target.columns:
            sales_target['指标年月'] = pd.to_datetime(sales_target['指标年月'])

        # 加载客户指标
        customer_target = pd.read_excel(DATA_FILES['customer_target'])
        if '月份' in customer_target.columns:
            customer_target['月份'] = pd.to_datetime(customer_target['月份'])

        # 加载TT产品指标
        tt_target = pd.read_excel(DATA_FILES['tt_product_target'])
        if '指标年月' in tt_target.columns:
            tt_target['指标年月'] = pd.to_datetime(tt_target['指标年月'])

        # 加载库存数据
        inventory_data = pd.read_excel(DATA_FILES['inventory'])

        # 加载月末库存
        month_end_inventory = pd.read_excel(DATA_FILES['month_end_inventory'])
        if '所属年月' in month_end_inventory.columns:
            month_end_inventory['所属年月'] = pd.to_datetime(month_end_inventory['所属年月'])

        # 加载预测数据
        forecast_data = pd.read_excel(DATA_FILES['forecast'])
        if '所属年月' in forecast_data.columns:
            forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])

        # 加载产品代码
        with open(DATA_FILES['product_codes'], 'r', encoding='utf-8') as f:
            product_codes = [line.strip() for line in f if line.strip()]

        # 加载新品代码
        with open(DATA_FILES['new_product_codes'], 'r', encoding='utf-8') as f:
            new_product_codes = [line.strip() for line in f if line.strip()]

        # 加载客户关系
        customer_relation = pd.read_excel(DATA_FILES['customer_relation'])
        # 筛选正常状态的客户
        active_customers = customer_relation[customer_relation['状态'] == '正常']

        # 添加简化产品名称和包装类型
        if '产品名称' in sales_orders.columns and '产品代码' in sales_orders.columns:
            sales_orders['简化产品名称'] = sales_orders.apply(
                lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
                axis=1
            )
            sales_orders['包装类型'] = sales_orders['产品名称'].apply(extract_packaging)

        # 将所有数据存入字典
        data_dict = {
            'sales_orders': sales_orders,
            'expense_orders': expense_orders,
            'promotion_data': promotion_data,
            'sales_target': sales_target,
            'customer_target': customer_target,
            'tt_target': tt_target,
            'inventory_data': inventory_data,
            'month_end_inventory': month_end_inventory,
            'forecast_data': forecast_data,
            'product_codes': product_codes,
            'new_product_codes': new_product_codes,
            'active_customers': active_customers,
            'customer_relation': customer_relation
        }

        return data_dict

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None


# ================ 筛选器函数 ================
def create_filters(data, filter_type="normal"):
    """创建统一筛选器"""
    # 初始化筛选状态
    if 'filter_region' not in st.session_state:
        st.session_state.filter_region = '全部'
    if 'filter_person' not in st.session_state:
        st.session_state.filter_person = '全部'
    if 'filter_customer' not in st.session_state:
        st.session_state.filter_customer = '全部'
    if 'filter_date_range' not in st.session_state:
        # 默认显示当年数据
        current_year = datetime.now().year
        st.session_state.filter_date_range = (
            datetime(current_year, 1, 1),
            datetime(current_year, 12, 31)
        )

    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        st.warning("无法加载筛选器，数据不完整")
        return

    sales_data = data['sales_orders']

    # 区域筛选器
    if '所属区域' in sales_data.columns:
        all_regions = sorted(['全部'] + list(sales_data['所属区域'].unique()))
        selected_region = st.sidebar.selectbox(
            "选择区域", all_regions, index=0, key="sidebar_region"
        )
        st.session_state.filter_region = selected_region

    # 销售员筛选器
    if '申请人' in sales_data.columns:
        all_persons = sorted(['全部'] + list(sales_data['申请人'].unique()))
        selected_person = st.sidebar.selectbox(
            "选择销售员", all_persons, index=0, key="sidebar_person"
        )
        st.session_state.filter_person = selected_person

    # 客户筛选器
    active_customers = data.get('active_customers', pd.DataFrame())

    if not active_customers.empty and '客户' in active_customers.columns:
        all_customers = sorted(['全部'] + list(active_customers['客户'].unique()))
        selected_customer = st.sidebar.selectbox(
            "选择客户", all_customers, index=0, key="sidebar_customer"
        )
        st.session_state.filter_customer = selected_customer

    # 日期范围筛选器
    if '发运月份' in sales_data.columns:
        min_date = sales_data['发运月份'].min().date()
        max_date = sales_data['发运月份'].max().date()

        date_range = st.sidebar.date_input(
            "选择日期范围",
            value=st.session_state.filter_date_range,
            min_value=min_date,
            max_value=max_date,
            key="sidebar_date_range"
        )

        # 确保date_range是元组且有两个元素
        if isinstance(date_range, tuple) and len(date_range) == 2:
            st.session_state.filter_date_range = date_range
        elif hasattr(date_range, '__iter__') and len(date_range) >= 2:
            st.session_state.filter_date_range = (date_range[0], date_range[-1])

    # 返回筛选后的数据
    return apply_filters(data)


def apply_filters(data):
    """应用筛选条件到数据"""
    if not data or not isinstance(data, dict) or 'sales_orders' not in data:
        return data

    filtered_data = data.copy()
    sales_data = filtered_data['sales_orders'].copy()

    # 应用区域筛选
    if st.session_state.filter_region != '全部' and '所属区域' in sales_data.columns:
        sales_data = sales_data[sales_data['所属区域'] == st.session_state.filter_region]

    # 应用销售员筛选
    if st.session_state.filter_person != '全部' and '申请人' in sales_data.columns:
        sales_data = sales_data[sales_data['申请人'] == st.session_state.filter_person]

    # 应用客户筛选
    if st.session_state.filter_customer != '全部':
        customer_relation = filtered_data.get('customer_relation', pd.DataFrame())
        if not customer_relation.empty and st.session_state.filter_customer in customer_relation['客户'].values:
            # 通过客户关系表查找客户代码
            customer_codes = customer_relation[customer_relation['客户'] == st.session_state.filter_customer][
                '客户代码'].tolist()
            if customer_codes and '客户代码' in sales_data.columns:
                sales_data = sales_data[sales_data['客户代码'].isin(customer_codes)]

    # 应用日期范围筛选
    if '发运月份' in sales_data.columns and hasattr(st.session_state.filter_date_range, '__iter__') and len(
            st.session_state.filter_date_range) >= 2:
        start_date, end_date = st.session_state.filter_date_range
        sales_data = sales_data[
            (sales_data['发运月份'].dt.date >= start_date) &
            (sales_data['发运月份'].dt.date <= end_date)
            ]

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
            '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">销售数据分析仪表盘 | 登录</div>',
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
            <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); 
                        text-align: center; min-height: 200px; display: flex; 
                        flex-direction: column; justify-content: center;">
                <h3 style="color: {COLORS['primary']}; margin-bottom: 1rem;">{title}</h3>
                <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">{formatted_value}</h1>
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