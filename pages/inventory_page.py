# pages/inventory_page.py - 库存分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import math
import warnings

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="库存分析仪表盘",
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


# ==================== 2. 库存数据加载与处理函数 ====================
@st.cache_data
def load_inventory_data():
    """加载库存数据 - 使用相对路径"""
    try:
        # 尝试查找文件的位置
        inventory_file_paths = [
            "含批次库存0221(2).xlsx",  # 仓库根目录
            os.path.join("pages", "含批次库存0221(2).xlsx")  # pages文件夹
        ]

        inventory_file = None
        for path in inventory_file_paths:
            if os.path.exists(path):
                inventory_file = path
                break

        if not inventory_file:
            return None

        # 读取库存数据
        inventory_raw = pd.read_excel(inventory_file, header=0)

        # 处理第一层数据（产品信息）
        product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
        inventory_data = product_rows.iloc[:, :7].copy()
        inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                  '现有库存可订量', '待入库量', '本月剩余可订量']

        # 处理第二层数据（批次信息）
        batch_rows = inventory_raw[inventory_raw.iloc[:, 7].notna()]
        batch_data = batch_rows.iloc[:, 7:].copy()
        batch_data.columns = ['库位', '生产日期', '生产批号', '数量']

        # 为批次数据添加产品代码
        product_code = None
        product_description = None
        batch_with_product = []

        for i, row in inventory_raw.iterrows():
            if pd.notna(row.iloc[0]):
                # 这是产品行
                product_code = row.iloc[0]
                product_description = row.iloc[1]  # 获取产品描述
            elif pd.notna(row.iloc[7]):
                # 这是批次行
                batch_row = row.iloc[7:].copy()
                batch_row_with_product = pd.Series([product_code, product_description] + batch_row.tolist())
                batch_with_product.append(batch_row_with_product)

        batch_data = pd.DataFrame(batch_with_product)
        batch_data.columns = ['产品代码', '描述', '库位', '生产日期', '生产批号', '数量']

        # 转换日期列
        batch_data['生产日期'] = pd.to_datetime(batch_data['生产日期'])

        # 加载出货数据
        shipping_file_paths = [
            "2409~250224出货数据.xlsx",  # 仓库根目录
            os.path.join("pages", "2409~250224出货数据.xlsx")  # pages文件夹
        ]

        shipping_file = None
        for path in shipping_file_paths:
            if os.path.exists(path):
                shipping_file = path
                break

        shipping_data = None
        if shipping_file:
            shipping_data = pd.read_excel(shipping_file)
            shipping_data.columns = ['订单日期', '所属区域', '申请人', '产品代码', '数量']
            shipping_data['订单日期'] = pd.to_datetime(shipping_data['订单日期'])

        # 加载预测数据
        forecast_file_paths = [
            "2409~2502人工预测.xlsx",  # 仓库根目录
            os.path.join("pages", "2409~2502人工预测.xlsx")  # pages文件夹
        ]

        forecast_file = None
        for path in forecast_file_paths:
            if os.path.exists(path):
                forecast_file = path
                break

        forecast_data = None
        if forecast_file:
            forecast_data = pd.read_excel(forecast_file)
            forecast_data.columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']
            forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])

        # 加载单价数据
        price_file_paths = [
            "单价.xlsx",  # 仓库根目录
            os.path.join("pages", "单价.xlsx")  # pages文件夹
        ]

        price_data = {}
        price_file = None
        for path in price_file_paths:
            if os.path.exists(path):
                price_file = path
                break

        if price_file:
            price_df = pd.read_excel(price_file)
            for _, row in price_df.iterrows():
                price_data[row['产品代码']] = row['单价']
        else:
            # 使用固定价格作为备用
            price_data = {
                'F01E4B': 137.04,
                'F3411A': 137.04,
                'F0104L': 126.72,
                'F3406B': 129.36,
                'F01C5D': 153.6,
                'F01L3A': 182.4,
                'F01L6A': 307.2,
                'F01A3C': 175.5,
                'F01H2B': 307.2,
                'F01L4A': 182.4,
                'F0104J': 216.96
            }

        # 如果没有找到价格，设置默认价格
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
        st.error(f"数据加载错误: {str(e)}")
        return None


def create_sample_inventory_data():
    """创建示例库存数据用于演示"""
    # 创建产品数据
    products = ['F0104L', 'F01E4B', 'F3411A', 'F01C5G', 'F01L4H', 'F01L3N', 'F01E4A', 'F01C5C', 'F0101P', 'F01K8A']
    descriptions = [
        '口力比萨68克袋装-中国', '口力汉堡108G袋装-中国', '口力午餐袋77G袋装-中国',
        '口力儿童节85G袋装-中国', '口力扭扭虫48G+送9.6G袋装-中国', '口力彩蝶虫48G+送9.6G袋装-中国',
        '口力汉堡540G盒装-中国', '口力欢乐派对400G袋装-中国', '口力汉堡90G直立袋装-中国', '口力烘焙袋77G袋装-中国'
    ]

    # 创建库存数据
    inventory_data = []
    for i, (code, desc) in enumerate(zip(products, descriptions)):
        inventory = np.random.randint(500, 5000)
        allocated = np.random.randint(0, inventory // 10)
        orderable = inventory - allocated
        pending = np.random.randint(0, 1000)

        inventory_data.append({
            '产品代码': code,
            '描述': desc,
            '现有库存': inventory,
            '已分配量': allocated,
            '现有库存可订量': orderable,
            '待入库量': pending,
            '本月剩余可订量': orderable + pending
        })

    # 创建批次数据
    batch_data = []
    today = datetime.now().date()

    for i, (code, desc) in enumerate(zip(products, descriptions)):
        inventory = inventory_data[i]['现有库存']
        batches = np.random.randint(1, 5)  # 每个产品1-4个批次

        for j in range(batches):
            # 生成随机的批次日期，从今天向前推1-180天
            days_ago = np.random.randint(1, 180)
            batch_date = today - timedelta(days=days_ago)

            # 生成批次号
            batch_number = f"{batch_date.strftime('%Y%m%d')}L:{np.random.randint(70000, 80000)}"

            # 分配库存到批次
            if j == batches - 1:  # 最后一个批次
                quantity = inventory
            else:
                quantity = np.random.randint(50, inventory // 2)
                inventory -= quantity

            batch_data.append({
                '产品代码': code,
                '描述': desc,
                '库位': 'DC-000',
                '生产日期': batch_date,
                '生产批号': batch_number,
                '数量': quantity
            })

    # 创建出货数据
    shipping_data = []
    start_date = today - timedelta(days=365)  # 去年今天

    regions = ['东', '南', '西', '北', '中']
    applicants = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']

    for i in range(500):  # 500条出货记录
        product_index = np.random.randint(0, len(products))
        product_code = products[product_index]

        # 随机日期，从一年前到今天
        days_offset = np.random.randint(0, 365)
        order_date = start_date + timedelta(days=days_offset)

        # 随机区域和申请人
        region = np.random.choice(regions)
        applicant = np.random.choice(applicants)

        # 随机数量，有一定波动性
        quantity = np.random.randint(5, 200)
        if np.random.random() < 0.1:  # 10%的概率有大单
            quantity *= np.random.randint(3, 10)

        shipping_data.append({
            '订单日期': order_date,
            '所属区域': region,
            '申请人': applicant,
            '产品代码': product_code,
            '数量': quantity
        })

    # 创建预测数据
    forecast_data = []
    next_month = today.replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)  # 下个月1号

    for region in regions:
        for applicant in applicants:
            for product_code in products:
                # 70%的概率有预测
                if np.random.random() < 0.7:
                    # 预测值，基于历史平均值加一些随机波动
                    product_shipping = [item for item in shipping_data
                                        if item['产品代码'] == product_code and
                                        item['所属区域'] == region and
                                        item['申请人'] == applicant]

                    if product_shipping:
                        avg_quantity = sum(item['数量'] for item in product_shipping) / len(product_shipping)
                        forecast = avg_quantity * (0.8 + 0.4 * np.random.random())  # 80%-120%的平均值
                    else:
                        forecast = np.random.randint(20, 100)  # 随机值

                    forecast_data.append({
                        '所属大区': region,
                        '销售员': applicant,
                        '所属年月': next_month,
                        '产品代码': product_code,
                        '预计销售量': round(forecast)
                    })

    # 创建价格数据
    price_data = {}
    for code in products:
        price_data[code] = np.random.randint(100, 300)

    # 确保日期字段正确格式化
    batch_df = pd.DataFrame(batch_data)
    batch_df['生产日期'] = pd.to_datetime(batch_df['生产日期'])

    shipping_df = pd.DataFrame(shipping_data)
    shipping_df['订单日期'] = pd.to_datetime(shipping_df['订单日期'])

    forecast_df = pd.DataFrame(forecast_data)
    forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'])

    # 整合数据
    sample_data = {
        'inventory_data': pd.DataFrame(inventory_data),
        'batch_data': batch_df,
        'shipping_data': shipping_df,
        'forecast_data': forecast_df,
        'price_data': price_data
    }

    return sample_data


@st.cache_data
def load_and_process_inventory_data():
    """加载并处理库存分析数据，如果没有真实数据则使用示例数据"""
    try:
        with st.spinner("正在加载库存数据..."):
            data = load_inventory_data()

            if not data or 'inventory_data' not in data or data['inventory_data'].empty:
                st.warning("无法加载真实库存数据，将使用示例数据进行分析")
                # 创建示例数据
                data = create_sample_inventory_data()

            # 分析数据
            analysis_result = analyze_inventory_data(data)
            data['analysis_result'] = analysis_result

            return data
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        # 创建示例数据
        data = create_sample_inventory_data()
        analysis_result = analyze_inventory_data(data)
        data['analysis_result'] = analysis_result
        return data


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
        if 'shipping_data' in data and not data['shipping_data'].empty:
            all_regions = ['全部'] + sorted(data['shipping_data']['所属区域'].unique().tolist())
            selected_region = st.selectbox(
                "选择责任区域", all_regions,
                index=all_regions.index(
                    st.session_state.inv_filter_region) if st.session_state.inv_filter_region in all_regions else 0,
                key="inv_region_filter"
            )
            st.session_state.inv_filter_region = selected_region

        # 责任人筛选
        if 'shipping_data' in data and not data['shipping_data'].empty:
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
                print(f"处理批次数据时出错: {str(e)}")
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


# ==================== 6. 图表创建函数 ====================
def create_inventory_overview_charts(analysis_result):
    """创建库存概览图表 - 使用与预测与计划.py一致的样式"""
    if not analysis_result:
        return None, None

    # 库存健康分布饼图
    health_dist = analysis_result.get('health_distribution', {})
    if health_dist:
        health_fig = go.Figure(data=[go.Pie(
            labels=list(health_dist.keys()),
            values=list(health_dist.values()),
            marker_colors=[COLORS['danger'], COLORS['success'], COLORS['warning']],
            textposition='inside',
            textinfo='percent+label',
            hole=0.4,
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
        )])

        health_fig.update_layout(
            title="库存健康状况分布",
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary'])
        )
    else:
        health_fig = None

    # 风险等级分布条形图
    risk_dist = analysis_result.get('risk_distribution', {})
    if risk_dist:
        # 确保按风险等级排序
        risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        ordered_risk = {k: risk_dist.get(k, 0) for k in risk_order if k in risk_dist}

        risk_fig = go.Figure(data=[go.Bar(
            y=list(ordered_risk.keys()),
            x=list(ordered_risk.values()),
            orientation='h',
            marker_color=[INVENTORY_RISK_COLORS.get(level, COLORS['gray']) for level in ordered_risk.keys()],
            text=list(ordered_risk.values()),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>批次数量: %{x}<extra></extra>'
        )])

        risk_fig.update_layout(
            title="风险等级分布",
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="批次数量",
            yaxis_title="风险等级"
        )
    else:
        risk_fig = None

    return health_fig, risk_fig


def create_batch_risk_charts(batch_analysis):
    """创建批次风险图表 - 调整图表类型和样式"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 高风险批次库龄分布 - 使用水平条形图
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if not high_risk_batches.empty:
        # 按库龄排序，显示前10个最老批次
        top_batches = high_risk_batches.sort_values('库龄', ascending=False).head(10)

        age_fig = go.Figure(data=[go.Bar(
            y=top_batches['产品简化名称'],  # 使用简化名称
            x=top_batches['库龄'],
            orientation='h',
            marker_color=[INVENTORY_RISK_COLORS.get(risk, COLORS['gray']) for risk in top_batches['风险程度']],
            text=top_batches['库龄'],
            textposition='outside',
            customdata=top_batches[['风险程度', '批次价值', '建议措施', '责任人']],
            hovertemplate='<b>%{y}</b><br>库龄: %{x}天<br>风险程度: %{customdata[0]}<br>批次价值: ¥%{customdata[1]:.2f}<br>建议: %{customdata[2]}<br>责任人: %{customdata[3]}<extra></extra>'
        )])

        # 添加风险阈值参考线
        age_fig.add_shape(
            type="line", x0=90, x1=90, y0=-0.5, y1=len(top_batches) - 0.5,
            line=dict(color=COLORS['danger'], dash="dash", width=2)
        )
        age_fig.add_shape(
            type="line", x0=60, x1=60, y0=-0.5, y1=len(top_batches) - 0.5,
            line=dict(color=COLORS['warning'], dash="dash", width=1.5)
        )

        age_fig.update_layout(
            title="高风险批次库龄分布（Top 10）",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="库龄（天）",
            yaxis_title="产品",
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(autorange="reversed")  # 从大到小显示
        )

        # 添加图例说明
        age_fig.add_annotation(
            x=90, y=len(top_batches),
            text="高风险阈值(90天)",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color=COLORS['danger'])
        )
    else:
        age_fig = None

    # 批次价值vs库龄关系散点图
    valid_batches = batch_analysis.head(20)  # 限制数量以提高可读性

    if not valid_batches.empty:
        scatter_fig = go.Figure()

        # 按风险程度分组绘制散点
        for risk_level in ['极高风险', '高风险', '中风险', '低风险', '极低风险']:
            risk_data = valid_batches[valid_batches['风险程度'] == risk_level]
            if not risk_data.empty:
                scatter_fig.add_trace(go.Scatter(
                    x=risk_data['库龄'],
                    y=risk_data['批次价值'],
                    mode='markers',
                    name=risk_level,
                    marker=dict(
                        size=risk_data['批次库存'] / risk_data['批次库存'].max() * 25 + 5,  # 动态调整大小
                        color=INVENTORY_RISK_COLORS.get(risk_level, COLORS['gray']),
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=risk_data['产品简化名称'],
                    hovertemplate='<b>%{text}</b><br>库龄: %{x}天<br>价值: ¥%{y:.2f}<br>库存: %{marker.size:.0f}箱<br>风险: ' + risk_level + '<br>责任人: %{customdata}<extra></extra>',
                    customdata=risk_data['责任人']
                ))

        # 添加风险阈值线
        scatter_fig.add_shape(
            type="line", x0=90, x1=90, y0=0, y1=valid_batches['批次价值'].max() * 1.1,
            line=dict(color=COLORS['danger'], dash="dash", width=2)
        )
        scatter_fig.add_shape(
            type="line", x0=60, x1=60, y0=0, y1=valid_batches['批次价值'].max() * 1.1,
            line=dict(color=COLORS['warning'], dash="dash", width=1.5)
        )

        scatter_fig.update_layout(
            title="批次价值 vs 库龄关系",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="库龄（天）",
            yaxis_title="批次价值（元）",
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
    else:
        scatter_fig = None

    return age_fig, scatter_fig


def create_responsibility_charts(batch_analysis):
    """创建责任归属图表 - 优化图表样式"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 区域责任分布 - 饼图，更简单清晰
    region_analysis = batch_analysis.groupby('责任区域').agg({
        '批次库存': 'sum',
        '批次价值': 'sum',
        '产品代码': 'count'
    }).reset_index()
    region_analysis.columns = ['责任区域', '总库存量', '总价值', '批次数量']

    # 移除空值或异常值区域
    region_analysis = region_analysis[
        (region_analysis['责任区域'].notna()) &
        (region_analysis['责任区域'] != '未知区域')
        ]

    if not region_analysis.empty:
        colors = px.colors.qualitative.Set2[:len(region_analysis)]

        region_fig = go.Figure(data=[go.Pie(
            labels=region_analysis['责任区域'],
            values=region_analysis['总价值'],
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>总价值: ¥%{value:,.2f}<br>占比: %{percent}<br>批次数量: %{customdata[0]}<br>总库存量: %{customdata[1]:,}箱<extra></extra>',
            customdata=region_analysis[['批次数量', '总库存量']]
        )])

        region_fig.update_layout(
            title="各区域责任库存分布",
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary'])
        )
    else:
        region_fig = None

    # 责任人TOP10堆叠柱状图
    person_risk = batch_analysis.groupby(['责任人', '风险程度']).size().unstack(fill_value=0)

    if not person_risk.empty:
        # 选择前10个责任人
        person_totals = person_risk.sum(axis=1).sort_values(ascending=False).head(10)
        top_persons = person_risk.loc[person_totals.index]

        # 确保风险顺序正确
        risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        for risk in risk_order:
            if risk not in top_persons.columns:
                top_persons[risk] = 0
        top_persons = top_persons[risk_order]

        # 使用堆叠条形图
        person_fig = go.Figure()

        # 添加各风险等级的条形
        for i, risk in enumerate(risk_order):
            if risk in top_persons.columns:
                person_fig.add_trace(go.Bar(
                    x=top_persons.index,
                    y=top_persons[risk],
                    name=risk,
                    marker_color=INVENTORY_RISK_COLORS.get(risk, COLORS['gray']),
                    hovertemplate='<b>%{x}</b><br>%{y} 个批次: ' + risk + '<extra></extra>'
                ))

        person_fig.update_layout(
            title="责任人风险分布（Top 10）",
            barmode='stack',
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="责任人",
            yaxis_title="批次数量",
            xaxis=dict(tickangle=45),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    else:
        person_fig = None

    return region_fig, person_fig


def create_clearance_prediction_charts(batch_analysis):
    """创建清库预测图表 - 优化图表设计"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 创建高风险批次清库预测图 - 水平条形图
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if not high_risk_batches.empty:
        # 预处理数据 - 替换无穷大
        valid_clearance = high_risk_batches.copy()
        valid_clearance['清库天数'] = valid_clearance['预计清库天数'].apply(
            lambda x: 365 if x == float('inf') else x
        )

        # 按清库天数排序，取前10个
        top_clearance = valid_clearance.sort_values('清库天数', ascending=False).head(10)

        # 创建条形图
        hist_fig = go.Figure()

        # 添加清库天数条形
        hist_fig.add_trace(go.Bar(
            y=top_clearance['产品简化名称'],
            x=top_clearance['清库天数'],
            orientation='h',
            name='预计清库天数',
            marker_color=COLORS['danger'],
            opacity=0.7,
            text=[f"{x:.0f}天" if x < 365 else "∞" for x in top_clearance['清库天数']],
            textposition='outside',
            customdata=top_clearance[['风险程度', '批次价值', '责任人']],
            hovertemplate='<b>%{y}</b><br>预计清库天数: %{text}<br>风险程度: %{customdata[0]}<br>批次价值: ¥%{customdata[1]:.2f}<br>责任人: %{customdata[2]}<extra></extra>'
        ))

        # 添加库龄条形
        hist_fig.add_trace(go.Bar(
            y=top_clearance['产品简化名称'],
            x=top_clearance['库龄'],
            orientation='h',
            name='当前库龄',
            marker_color=COLORS['primary'],
            opacity=0.7,
            text=top_clearance['库龄'],
            textposition='outside',
            customdata=top_clearance[['风险程度', '批次价值', '责任人']],
            hovertemplate='<b>%{y}</b><br>当前库龄: %{x}天<br>风险程度: %{customdata[0]}<br>批次价值: ¥%{customdata[1]:.2f}<br>责任人: %{customdata[2]}<extra></extra>'
        ))

        # 添加风险阈值线
        hist_fig.add_shape(
            type="line", x0=90, x1=90, y0=-0.5, y1=len(top_clearance) - 0.5,
            line=dict(color=COLORS['danger'], dash="dash", width=2)
        )

        hist_fig.update_layout(
            title="高风险批次清库预测",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="天数",
            yaxis_title="产品",
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(autorange="reversed"),  # 从大到小显示
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    else:
        hist_fig = None

    # 预测偏差对库存的影响图表 - 气泡图
    batch_analysis_copy = batch_analysis.copy()
    batch_analysis_copy['预测偏差值'] = batch_analysis_copy['预测偏差'].apply(
        lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) and '%' in x and x != '异常' else 0
    )

    valid_forecast = batch_analysis_copy[
        (abs(batch_analysis_copy['预测偏差值']) <= 1.0) &
        (batch_analysis_copy['预计清库天数'] != float('inf'))
        ]

    if not valid_forecast.empty:
        # 选择最显著的预测偏差批次
        significant_bias = valid_forecast.sort_values('预测偏差值', key=abs, ascending=False).head(15)

        forecast_fig = go.Figure()

        # 创建气泡图
        forecast_fig.add_trace(go.Scatter(
            x=significant_bias['预测偏差值'] * 100,  # 转为百分比
            y=significant_bias['预计清库天数'],
            mode='markers',
            marker=dict(
                size=significant_bias['批次价值'] / significant_bias['批次价值'].max() * 30 + 10,  # 动态调整大小
                color=significant_bias['预测偏差值'] * 100,
                colorscale='RdBu_r',  # 红蓝色标，红色表示预测过高，蓝色表示预测过低
                colorbar=dict(title="预测偏差 (%)"),
                line=dict(width=1, color='white')
            ),
            text=significant_bias['产品简化名称'],
            customdata=significant_bias[['批次价值', '责任人', '风险程度']],
            hovertemplate='<b>%{text}</b><br>预测偏差: %{x:.1f}%<br>清库天数: %{y:.1f}天<br>批次价值: ¥%{customdata[0]:.2f}<br>责任人: %{customdata[1]}<br>风险程度: %{customdata[2]}<extra></extra>'
        ))

        # 添加参考线
        forecast_fig.add_shape(
            type="line", x0=0, x1=0,
            y0=0, y1=significant_bias['预计清库天数'].max() * 1.1,
            line=dict(color=COLORS['gray'], dash="dash", width=1)
        )

        forecast_fig.add_shape(
            type="line", x0=significant_bias['预测偏差值'].min() * 100 * 1.1,
            x1=significant_bias['预测偏差值'].max() * 100 * 1.1,
            y0=90, y1=90,
            line=dict(color=COLORS['danger'], dash="dash", width=1)
        )

        forecast_fig.update_layout(
            title="预测偏差对库存的影响",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="预测偏差 (%)",
            yaxis_title="预计清库天数",
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            )
        )

        # 添加象限标记
        forecast_fig.add_annotation(
            x=50, y=significant_bias['预计清库天数'].max() * 0.75,
            text="预测过高<br>库存积压风险",
            showarrow=False,
            font=dict(size=10, color=COLORS['danger'])
        )

        forecast_fig.add_annotation(
            x=-50, y=significant_bias['预计清库天数'].max() * 0.75,
            text="预测过低<br>缺货风险",
            showarrow=False,
            font=dict(size=10, color=COLORS['primary'])
        )
    else:
        forecast_fig = None

    return hist_fig, forecast_fig


# 新增：创建批次风险热力图函数
def create_batch_risk_heatmap(data):
    """创建批次风险热力图，用于替代详细数据表"""
    if data is None or data.empty:
        return None

    # 准备热力图数据
    risk_order = {"极高风险": 0, "高风险": 1, "中风险": 2, "低风险": 3, "极低风险": 4}

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
    for risk in ["极高风险", "高风险", "中风险", "低风险", "极低风险"]:
        if risk not in pivot_data.columns:
            pivot_data[risk] = 0

    # 按照风险顺序排列列
    pivot_data = pivot_data[["极高风险", "高风险", "中风险", "低风险", "极低风险"]]

    # 计算每行(产品)的总和，并按总和排序
    pivot_data['总价值'] = pivot_data.sum(axis=1)
    pivot_data = pivot_data.sort_values('总价值', ascending=False)
    pivot_data = pivot_data.drop('总价值', axis=1)

    # 限制显示前15个产品
    pivot_data = pivot_data.head(15)

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
        title="批次风险热力图",
        height=600,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="风险等级",
        yaxis_title="产品",
        xaxis=dict(
            tickangle=-45,
            categoryorder='array',
            categoryarray=["极高风险", "高风险", "中风险", "低风险", "极低风险"]
        )
    )

    return fig


# 新增：创建批次价值条形图函数
def create_batch_value_chart(data):
    """创建批次价值条形图，用于替代详细数据表"""
    if data is None or data.empty:
        return None

    # 按产品分组计算批次价值总和
    product_values = data.groupby('产品简化名称').agg({
        '批次价值': 'sum',
        '风险程度': lambda x: ', '.join(sorted(x.unique())),
        '责任人': lambda x: ', '.join(sorted(x.unique())),
        '批次库存': 'sum',
        '库龄': 'mean'
    }).reset_index()

    # 按批次价值排序并限制数量
    top_products = product_values.sort_values('批次价值', ascending=False).head(15)

    # 确定主要风险颜色 - 选择最严重的风险
    risk_order = {
        "极高风险": 0,
        "高风险": 1,
        "中风险": 2,
        "低风险": 3,
        "极低风险": 4
    }

    # 函数：获取最严重的风险
    def get_worst_risk(risk_str):
        risks = risk_str.split(', ')
        worst_risk = min(risks, key=lambda x: risk_order.get(x, 5) if x in risk_order else 5)
        return worst_risk

    top_products['主要风险'] = top_products['风险程度'].apply(get_worst_risk)

    # 创建条形图
    fig = go.Figure()

    # 按风险分组添加条形
    for risk in ["极高风险", "高风险", "中风险", "低风险", "极低风险"]:
        risk_data = top_products[top_products['主要风险'] == risk]
        if not risk_data.empty:
            fig.add_trace(go.Bar(
                x=risk_data['产品简化名称'],
                y=risk_data['批次价值'],
                name=risk,
                marker_color=INVENTORY_RISK_COLORS.get(risk, COLORS['gray']),
                text=risk_data['批次价值'].apply(format_currency),
                textposition='outside',
                customdata=risk_data[['风险程度', '责任人', '批次库存', '库龄']],
                hovertemplate='<b>%{x}</b><br>批次价值: %{text}<br>风险情况: %{customdata[0]}<br>责任人: %{customdata[1]}<br>库存量: %{customdata[2]:.0f}箱<br>平均库龄: %{customdata[3]:.1f}天<extra></extra>'
            ))

    fig.update_layout(
        title="批次价值分布",
        height=600,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="产品",
        yaxis_title="批次价值（元）",
        xaxis=dict(tickangle=-45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


# ==================== 7. 主页面逻辑 ====================
def main():
    """主页面函数"""
    # 检查用户是否已登录
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("请先登录系统")
        st.stop()

    # 加载库存数据
    data = load_and_process_inventory_data()

    if data is None:
        st.error("无法加载库存数据，请检查数据文件")
        return

    # 应用筛选
    filtered_data = create_inventory_filters(data)

    if 'analysis_result' not in filtered_data:
        st.error("数据分析失败")
        return

    analysis_result = filtered_data['analysis_result']

    # 创建标签页 - 保持与预测与计划.py一致的结构
    tabs = st.tabs([
        "📊 总览与关键指标",
        "⚠️ 风险批次分析",
        "👥 责任归属分析",
        "📈 清库预测分析",
        "📋 批次分析可视化"
    ])

    with tabs[0]:  # 总览与关键指标
        st.markdown('<div class="sub-header">📊 库存关键指标</div>', unsafe_allow_html=True)

        # 关键指标行 - 新增库存周转天数和呆滞库存比例
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # 库存周转天数 - 新增核心指标
            turnover_days = analysis_result.get('inventory_turnover_days', float('inf'))
            turnover_days_display = format_days(turnover_days)
            turnover_color = COLORS['success'] if turnover_days < 60 else (
                COLORS['warning'] if turnover_days < 90 else COLORS['danger'])

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">库存周转天数</p>
                <p class="card-value" style="color:{turnover_color};">{turnover_days_display}</p>
                <p class="card-text">库存流转速度核心指标</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 呆滞库存比例 - 新增核心指标
            stagnant_ratio = analysis_result.get('stagnant_ratio', 0.0)
            stagnant_ratio_display = format_percentage(stagnant_ratio * 100)
            stagnant_color = COLORS['success'] if stagnant_ratio < 0.1 else (
                COLORS['warning'] if stagnant_ratio < 0.3 else COLORS['danger'])

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">呆滞库存比例</p>
                <p class="card-value" style="color:{stagnant_color};">{stagnant_ratio_display}</p>
                <p class="card-text">超过60天的库存占比</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # 库存总量 - 保留基础指标
            total_inv = analysis_result.get('total_inventory', 0)
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">库存总量</p>
                <p class="card-value">{format_number(total_inv)}</p>
                <p class="card-text">当前总库存数量</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # 库存资金占用成本 - 新增核心指标
            capital_cost = analysis_result.get('capital_cost', 0.0)
            capital_cost_display = format_currency(capital_cost)

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">月均资金占用成本</p>
                <p class="card-value">{capital_cost_display}</p>
                <p class="card-text">基于年化{INVENTORY_CONFIG['annual_capital_cost'] * 100}%资金成本</p>
            </div>
            """, unsafe_allow_html=True)

        # 次要指标 - 高风险和呆滞库存详情
        st.markdown('<div class="sub-header">库存风险指标</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
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

        with col2:
            # 呆滞库存价值
            stagnant_value = analysis_result.get('stagnant_value', 0.0)
            stagnant_value_display = format_currency(stagnant_value)
            total_value = analysis_result.get('total_inventory_value', 0.0)
            stagnant_pct = (stagnant_value / total_value * 100) if total_value > 0 else 0

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">呆滞库存价值</p>
                <p class="card-value" style="color:{COLORS['warning']};">{stagnant_value_display}</p>
                <p class="card-text">占总库存价值{format_percentage(stagnant_pct)}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # 库存总价值
            total_value = analysis_result.get('total_inventory_value', 0.0)
            total_value_display = format_currency(total_value)

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">库存总价值</p>
                <p class="card-value">{total_value_display}</p>
                <p class="card-text">所有产品库存总价值</p>
            </div>
            """, unsafe_allow_html=True)

        # 概览图表
        st.markdown('<div class="sub-header">库存状况概览</div>', unsafe_allow_html=True)

        health_fig, risk_fig = create_inventory_overview_charts(analysis_result)

        col1, col2 = st.columns(2)

        with col1:
            if health_fig:
                st.plotly_chart(health_fig, use_container_width=True)
            else:
                st.info("暂无库存健康分布数据")

        with col2:
            if risk_fig:
                st.plotly_chart(risk_fig, use_container_width=True)
            else:
                st.info("暂无风险分布数据")

        # 添加图表解释
        if health_fig or risk_fig:
            add_chart_explanation("""
            <b>图表解读：</b> 左图展示库存健康状况分布，绿色表示健康库存，红色表示过剩库存（可能存在积压风险），橙色表示库存不足。
            右图显示各风险等级的批次数量分布，从极高风险到极低风险逐级递减，帮助识别亟需处理的库存。
            <br><b>行动建议：</b> 重点关注高风险和极高风险批次，优先制定清库方案。对于库存周转天数过高的产品，
            考虑调整采购策略并执行针对性促销活动，降低呆滞库存比例。建立健全的库存预警机制，定期监控风险等级变化趋势。
            """)

    with tabs[1]:  # 风险批次分析
        st.markdown('<div class="sub-header">⚠️ 批次风险分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 风险统计 - 使用与预测与计划.py一致的卡片样式
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

            # 风险图表
            age_fig, scatter_fig = create_batch_risk_charts(batch_analysis)

            if age_fig:
                st.plotly_chart(age_fig, use_container_width=True)
            else:
                st.info("暂无高风险批次库龄数据")

            if scatter_fig:
                st.plotly_chart(scatter_fig, use_container_width=True)
            else:
                st.info("暂无批次价值关系数据")

            # 添加图表解释
            if age_fig or scatter_fig:
                # 提取关键洞察
                high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
                oldest_batch = batch_analysis.iloc[
                    batch_analysis['库龄'].idxmax()] if not batch_analysis.empty else None
                high_value_old_batch = high_risk_batches.iloc[
                    high_risk_batches['批次价值'].idxmax()] if not high_risk_batches.empty else None

                insight_text = "<b>图表解读：</b> 上图显示高风险批次的库龄分布，红色虚线标记90天高风险阈值。"
                if oldest_batch is not None:
                    insight_text += f" 最老批次为{oldest_batch['产品简化名称']}，库龄{oldest_batch['库龄']}天。"

                insight_text += "下图展示库龄与批次价值的关系，气泡大小代表库存量，颜色表示风险等级。"
                if high_value_old_batch is not None:
                    insight_text += f" 价值最高的高风险批次为{high_value_old_batch['产品简化名称']}，价值{format_currency(high_value_old_batch['批次价值'])}。"

                insight_text += "<br><b>行动建议：</b> 优先处理库龄超过90天且价值高的批次，制定分级清库策略：对极高风险批次考虑折价促销，"
                insight_text += "对高风险批次加强营销推广力度。建立定期批次审查机制，对接近60天的批次提前干预，防止形成呆滞库存。"

                add_chart_explanation(insight_text)
        else:
            st.info("当前筛选条件下暂无批次数据")

    with tabs[2]:  # 责任归属分析
        st.markdown('<div class="sub-header">👥 责任归属分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

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

            # 责任图表
            region_fig, person_fig = create_responsibility_charts(batch_analysis)

            if region_fig:
                st.plotly_chart(region_fig, use_container_width=True)
            else:
                st.info("暂无责任区域分布数据")

            if person_fig:
                st.plotly_chart(person_fig, use_container_width=True)
            else:
                st.info("暂无责任人分布数据")

            # 添加图表解释
            if region_fig or person_fig:
                # 提取关键洞察
                top_region_name = region_stats.index[0] if len(region_stats) > 0 else "无"
                top_person_name = person_stats.index[0] if len(person_stats) > 0 else "无"

                # 查找风险最高的区域
                region_risk_counts = batch_analysis.groupby('责任区域')['风险程度'].apply(
                    lambda x: sum(x.isin(['极高风险', '高风险'])) / len(x) if len(x) > 0 else 0
                ).sort_values(ascending=False)

                highest_risk_region = region_risk_counts.index[0] if len(region_risk_counts) > 0 else "无"
                highest_risk_pct = region_risk_counts.iloc[0] * 100 if len(region_risk_counts) > 0 else 0

                insight_text = "<b>图表解读：</b> 上图展示各责任区域的库存价值分布，饼图大小反映了各区域管理库存的相对规模。"
                if top_region_name != "无":
                    insight_text += f" {top_region_name}区域负责最大库存价值，占总库存的{region_stats.iloc[0] / region_stats.sum() * 100:.1f}%。"

                insight_text += " 下图显示责任人的风险批次分布，堆叠柱状图清晰展示各风险等级的构成情况。"
                if top_person_name != "无":
                    insight_text += f" {top_person_name}是主要责任人，负责{len(batch_analysis[batch_analysis['责任人'] == top_person_name])}个批次。"

                insight_text += "<br><b>行动建议：</b> "

                if highest_risk_region != "无" and highest_risk_pct > 30:
                    insight_text += f"对{highest_risk_region}区域（高风险批次占比{format_percentage(highest_risk_pct)}）进行重点库存管理培训，"
                else:
                    insight_text += "对库存价值高的区域加强库存管理培训，"

                insight_text += "建立清晰的责任制考核体系；优化预测准确性，提高销售与采购的协调效率；"
                insight_text += "建立跨区域库存调拨机制，平衡区域间库存分布差异。"

                add_chart_explanation(insight_text)
        else:
            st.info("当前筛选条件下暂无责任归属数据")

    with tabs[3]:  # 清库预测分析
        st.markdown('<div class="sub-header">📈 清库预测分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

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

            # 清库预测图表
            hist_fig, forecast_fig = create_clearance_prediction_charts(batch_analysis)

            if hist_fig:
                st.plotly_chart(hist_fig, use_container_width=True)
            else:
                st.info("暂无清库预测数据")

            if forecast_fig:
                st.plotly_chart(forecast_fig, use_container_width=True)
            else:
                st.info("暂无预测偏差对库存影响数据")

            # 添加图表解释
            if hist_fig or forecast_fig:
                # 提取关键洞察
                no_sales_products = batch_analysis[batch_analysis['预计清库天数'] == float('inf')][
                    '产品简化名称'].tolist()
                most_overestimated = batch_analysis.sort_values('预测偏差值', ascending=False).head(1)
                most_underestimated = batch_analysis.sort_values('预测偏差值', ascending=True).head(1)

                insight_text = "<b>图表解读：</b> 上图对比展示了高风险批次的预计清库天数(红色)和当前库龄(蓝色)，红色虚线标记90天高风险阈值。"

                if not no_sales_products:
                    insight_text += " 所有批次都有销售记录，但部分批次清库周期过长。"
                elif len(no_sales_products) <= 3:
                    insight_text += f" 产品{', '.join(no_sales_products[:3])}因无销量导致清库天数为无穷大，需要特别关注。"
                else:
                    insight_text += f" 有{infinite_batches}个批次因无销量导致清库天数为无穷大，需要特别干预措施。"

                insight_text += " 下图展示预测偏差与清库天数的关系，气泡大小代表批次价值。"

                if not most_overestimated.empty:
                    product = most_overestimated['产品简化名称'].iloc[0]
                    bias = float(most_overestimated['预测偏差'].iloc[0].rstrip('%')) if isinstance(
                        most_overestimated['预测偏差'].iloc[0], str) else 0
                    insight_text += f" 预测偏差最大的产品是{product}，预测过高{abs(bias):.1f}%。"

                insight_text += "<br><b>行动建议：</b> 对长期积压批次制定专项清库行动计划，考虑捆绑销售或限时促销；"
                insight_text += "改善预测模型准确性，减少偏差导致的库存积压；建立动态定价机制，根据库龄调整价格策略；"
                insight_text += "对无销量的产品考虑替代性营销策略或转移到其他销售渠道。"

                add_chart_explanation(insight_text)
        else:
            st.info("当前筛选条件下暂无清库预测数据")

    with tabs[4]:  # 批次分析可视化 (替代原来的详细数据表)
        st.markdown('<div class="sub-header">📋 批次详细分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 筛选选项
            col1, col2, col3 = st.columns(3)

            with col1:
                show_count = st.selectbox("显示数量", [10, 20, 50, 100, "全部"], index=1)

            with col2:
                sort_by = st.selectbox("排序依据", ["风险程度", "库龄", "批次价值", "预计清库天数"])

            with col3:
                ascending = st.selectbox("排序方式", ["降序", "升序"]) == "升序"

            # 数据处理
            display_data = batch_analysis.copy()

            # 排序
            if sort_by == "风险程度":
                risk_order = {"极高风险": 0, "高风险": 1, "中风险": 2, "低风险": 3, "极低风险": 4}
                display_data['排序值'] = display_data['风险程度'].map(risk_order)
                display_data = display_data.sort_values('排序值', ascending=ascending)
                display_data = display_data.drop('排序值', axis=1)
            else:
                # 处理无穷大值和特殊排序
                if sort_by == "预计清库天数":
                    # 对于无穷大值的处理，确保它们始终排在最前面或最后面
                    is_inf = display_data['预计清库天数'] == float('inf')
                    if ascending:
                        # 升序时，无穷大值应该排在最后
                        not_inf_data = display_data[~is_inf].sort_values(sort_by, ascending=True)
                        inf_data = display_data[is_inf]
                        display_data = pd.concat([not_inf_data, inf_data])
                    else:
                        # 降序时，无穷大值应该排在最前面
                        not_inf_data = display_data[~is_inf].sort_values(sort_by, ascending=False)
                        inf_data = display_data[is_inf]
                        display_data = pd.concat([inf_data, not_inf_data])
                else:
                    display_data = display_data.sort_values(sort_by, ascending=ascending)

            # 限制显示数量
            if show_count != "全部":
                display_data = display_data.head(int(show_count))

            # 创建可视化图表替代表格
            if not display_data.empty:
                # 风险热力图
                risk_heatmap = create_batch_risk_heatmap(display_data)
                if risk_heatmap:
                    st.plotly_chart(risk_heatmap, use_container_width=True)

                # 批次价值条形图
                value_chart = create_batch_value_chart(display_data)
                if value_chart:
                    st.plotly_chart(value_chart, use_container_width=True)

                # 数据洞察
                st.markdown('<div class="sub-header">数据洞察</div>', unsafe_allow_html=True)

                extreme_high_count = len(display_data[display_data['风险程度'] == '极高风险'])
                high_count = len(display_data[display_data['风险程度'] == '高风险'])
                total_value = display_data['批次价值'].sum()
                avg_age = display_data['库龄'].mean()

                # 提取主要积压原因
                if '积压原因' in display_data.columns:
                    # 分解复合原因
                    all_reasons = []
                    for reasons in display_data['积压原因']:
                        if pd.notna(reasons):
                            for reason in reasons.split('，'):
                                all_reasons.append(reason)

                    # 统计频率
                    if all_reasons:
                        from collections import Counter
                        reason_counts = Counter(all_reasons)
                        top_reason = reason_counts.most_common(1)[0][0]
                    else:
                        top_reason = "未知"
                else:
                    top_reason = "未知"

                insight_text = f"""
                **当前筛选结果概况：**
                - 显示 {len(display_data)} 个批次，总价值 {format_currency(total_value)}
                - 极高风险批次 {extreme_high_count} 个，高风险批次 {high_count} 个
                - 平均库龄 {avg_age:.1f} 天
                - 主要积压原因：{top_reason}

                **优化建议：**
                - 立即制定极高风险和高风险批次的紧急清库行动计划
                - 加强预测准确性培训，建立预测责任制考核机制
                - 优化库存周转策略，建立动态补货和清库预警系统
                - 定期评估库存健康度，建立跨部门协作的快速响应机制
                """

                st.markdown(insight_text)

            else:
                st.info("当前筛选和排序条件下无数据显示")
        else:
            st.info("暂无详细分析数据")


# 执行主函数
if __name__ == "__main__":
    main()