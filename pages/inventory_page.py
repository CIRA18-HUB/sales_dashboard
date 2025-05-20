# pages/inventory_page.py - 库存分析与预测页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import math
import calendar
import re
import warnings

warnings.filterwarnings('ignore')

# 从config导入必要的函数和配置
from config import (
    COLORS, INVENTORY_RISK_COLORS, INVENTORY_CONFIG, load_inventory_data,
    format_currency, format_percentage, format_number, format_days,
    calculate_inventory_risk_level, calculate_risk_percentage,
    setup_page, add_chart_explanation, safe_mean, calculate_unified_accuracy,
    generate_recommendation
)

# 设置页面
setup_page()

# 页面标题
st.markdown('<div class="main-header">📦 库存分析与预测</div>', unsafe_allow_html=True)

# 自定义CSS样式 - 调整字体大小和样式与预测与计划.py保持一致
st.markdown("""
<style>
    /* 确保字体大小适中 */
    .main-header {
        font-size: 2rem;  /* 与预测与计划.py一致 */
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.2rem;
    }
    .card-value {
        font-size: 1.8rem;
    }
    .sub-header {
        font-size: 1.5rem;
    }
    /* 保持与预测与计划.py一致的图表颜色 */
    .stPlotlyChart {
        background-color: white !important;
    }
    /* 补充必要的样式 */
    .page-title {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    .chart-container {
        margin: 1.2rem 0;
    }
    /* 匹配预测与计划.py的悬停样式 */
    .hover-info {
        background-color: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    /* 微调其他细节 */
    .streamlit-expanderHeader {
        font-size: 1rem;
    }
    div.stRadio > label {
        font-size: 0.9rem;
    }
    div.stSelectbox > div > div > div > div > div.st-bq {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 1. 库存专用数据加载函数 ====================
@st.cache_data
def load_and_process_inventory_data():
    """加载并处理库存分析数据"""
    try:
        with st.spinner("正在加载库存数据..."):
            data = load_inventory_data()

            if not data or 'inventory_data' not in data or data['inventory_data'].empty:
                st.warning("无法加载库存数据，将使用示例数据进行分析")
                # 创建示例数据
                data = create_sample_inventory_data()

            # 分析数据
            analysis_result = analyze_inventory_data(data)
            data['analysis_result'] = analysis_result

            return data
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        # 创建示例数据
        return create_sample_inventory_data()


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

    # 整合数据
    sample_data = {
        'inventory_data': pd.DataFrame(inventory_data),
        'batch_data': pd.DataFrame(batch_data),
        'shipping_data': pd.DataFrame(shipping_data),
        'forecast_data': pd.DataFrame(forecast_data),
        'price_data': price_data,
        'analysis_result': {}  # 将在后续分析中填充
    }

    # 确保日期字段正确格式化
    sample_data['batch_data']['生产日期'] = pd.to_datetime(sample_data['batch_data']['生产日期'])
    sample_data['shipping_data']['订单日期'] = pd.to_datetime(sample_data['shipping_data']['订单日期'])
    sample_data['forecast_data']['所属年月'] = pd.to_datetime(sample_data['forecast_data']['所属年月'])

    # 分析数据
    analysis_result = analyze_inventory_data(sample_data)
    sample_data['analysis_result'] = analysis_result

    return sample_data


# ==================== 2. 库存专用筛选器 ====================
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


# ==================== 3. 核心分析函数 ====================
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
        assigned_inventory = (inventory_data['现有库存'] - inventory_data['现有库存可订量']).sum() if all(
            col in inventory_data.columns for col in ['现有库存', '现有库存可订量']) else 0
        orderable_inventory = inventory_data[
            '现有库存可订量'].sum() if '现有库存可订量' in inventory_data.columns else 0
        pending_inventory = inventory_data['待入库量'].sum() if '待入库量' in inventory_data.columns else 0

        # 批次级别分析
        batch_analysis = None
        if not batch_data.empty:
            batch_analysis = analyze_batch_level_data(batch_data, shipping_data, forecast_data, price_data)

        # 计算健康分布
        health_distribution = {}
        risk_distribution = {}

        if batch_analysis is not None and not batch_analysis.empty:
            # 根据风险程度统计
            risk_counts = batch_analysis['风险程度'].value_counts().to_dict()
            risk_distribution = risk_counts

            # 转换为健康分布（简化）
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
            'assigned_inventory': assigned_inventory,
            'orderable_inventory': orderable_inventory,
            'pending_inventory': pending_inventory,
            'health_distribution': health_distribution,
            'risk_distribution': risk_distribution,
            'batch_analysis': batch_analysis
        }

    except Exception as e:
        st.error(f"库存分析出错: {str(e)}")
        return {}


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
                unit_price = price_data.get(product_code, 50.0)
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

                # 计算预测偏差（简化）
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

                # 责任归属分析（简化版）
                responsible_region, responsible_person = analyze_responsibility_simplified(
                    product_code, shipping_data, forecast_data
                )

                # 生成建议措施
                recommendation = generate_recommendation_for_inventory(risk_level, batch_age, days_to_clear)

                # 确定积压原因
                stocking_reasons = determine_stocking_reasons(batch_age, sales_metrics['sales_volatility'],
                                                              forecast_bias)

                # 添加到分析结果
                batch_analysis.append({
                    '产品代码': product_code,
                    '描述': description,
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


def calculate_product_sales_metrics(shipping_data):
    """计算产品销售指标"""
    if shipping_data.empty:
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

        # 计算销量波动（简化）
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
    """计算预测偏差（简化版）"""
    try:
        if forecast_data.empty or shipping_data.empty:
            return 0.0

        # 获取最近一个月的预测和实际销量
        recent_forecast = forecast_data[forecast_data['产品代码'] == product_code]['预计销售量'].sum()
        recent_sales = shipping_data[shipping_data['产品代码'] == product_code]['数量'].sum()

        if recent_forecast == 0 and recent_sales == 0:
            return 0.0
        elif recent_forecast == 0:
            return -0.5  # 无预测但有销售
        elif recent_sales == 0:
            return 0.5  # 有预测但无销售
        else:
            # 计算预测偏差
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
        if not shipping_data.empty:
            product_shipping = shipping_data[shipping_data['产品代码'] == product_code]
            if not product_shipping.empty:
                # 按申请人统计数量
                person_sales = product_shipping.groupby('申请人')['数量'].sum()
                if not person_sales.empty:
                    main_person = person_sales.idxmax()
                    # 获取该人员的区域
                    person_region = product_shipping[product_shipping['申请人'] == main_person]['所属区域'].iloc[0]
                    return person_region, main_person

        # 从预测数据中找责任人
        if not forecast_data.empty:
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


# ==================== 4. 图表创建函数 ====================
def create_inventory_overview_charts(analysis_result):
    """创建库存概览图表"""
    if not analysis_result:
        return None, None

    # 库存健康分布饼图
    health_dist = analysis_result.get('health_distribution', {})
    if health_dist:
        health_fig = px.pie(
            names=list(health_dist.keys()),
            values=list(health_dist.values()),
            title="库存健康状况分布",
            color_discrete_map={
                '库存健康': COLORS['success'],
                '库存不足': COLORS['warning'],
                '库存过剩': COLORS['danger']
            }
        )
        health_fig.update_traces(textposition='inside', textinfo='percent+label')
        health_fig.update_layout(height=400, plot_bgcolor='white')
    else:
        health_fig = None

    # 风险等级分布条形图
    risk_dist = analysis_result.get('risk_distribution', {})
    if risk_dist:
        risk_fig = px.bar(
            x=list(risk_dist.keys()),
            y=list(risk_dist.values()),
            title="风险等级分布",
            color=list(risk_dist.keys()),
            color_discrete_map=INVENTORY_RISK_COLORS
        )
        risk_fig.update_layout(height=400, showlegend=False, plot_bgcolor='white')
        risk_fig.update_traces(text=list(risk_dist.values()), textposition='outside')
    else:
        risk_fig = None

    return health_fig, risk_fig


def create_batch_risk_charts(batch_analysis):
    """创建批次风险图表"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 高风险批次库龄分布
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])].head(10)

    if not high_risk_batches.empty:
        # 添加产品显示列，使用产品简称而非代码
        high_risk_batches['产品显示'] = high_risk_batches['描述'].apply(
            lambda x: x.replace('口力', '').replace('-中国', '') if isinstance(x, str) else x
        )

        age_fig = px.bar(
            high_risk_batches,
            x='产品显示',  # 使用产品显示而非产品代码
            y='库龄',
            color='风险程度',
            title="高风险批次库龄分布（Top 10）",
            color_discrete_map=INVENTORY_RISK_COLORS,
            text='库龄'
        )
        age_fig.update_traces(textposition='outside')
        age_fig.update_layout(height=500, plot_bgcolor='white')
        age_fig.update_xaxes(tickangle=45)
    else:
        age_fig = None

    # 清库天数vs库龄散点图
    valid_batches = batch_analysis[batch_analysis['预计清库天数'] != float('inf')].head(20)

    if not valid_batches.empty:
        # 添加产品显示列，使用产品简称
        valid_batches['产品显示'] = valid_batches['描述'].apply(
            lambda x: x.replace('口力', '').replace('-中国', '') if isinstance(x, str) else x
        )

        scatter_fig = px.scatter(
            valid_batches,
            x='库龄',
            y='预计清库天数',
            size='批次价值',
            color='风险程度',
            hover_name='产品显示',  # 使用产品显示而非产品代码
            title="库龄 vs 清库天数关系",
            color_discrete_map=INVENTORY_RISK_COLORS
        )

        # 添加风险阈值线
        scatter_fig.add_shape(type="line", x0=0, x1=max(valid_batches['库龄']),
                              y0=90, y1=90, line=dict(color="red", dash="dash"))
        scatter_fig.add_shape(type="line", x0=90, x1=90,
                              y0=0, y1=max(valid_batches['预计清库天数']),
                              line=dict(color="red", dash="dash"))

        scatter_fig.update_layout(height=500, plot_bgcolor='white')
    else:
        scatter_fig = None

    return age_fig, scatter_fig


def create_responsibility_charts(batch_analysis):
    """创建责任归属图表"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 区域责任分布
    region_analysis = batch_analysis.groupby('责任区域').agg({
        '批次库存': 'sum',
        '批次价值': 'sum',
        '产品代码': 'count'
    }).reset_index()
    region_analysis.columns = ['责任区域', '总库存量', '总价值', '批次数量']

    region_fig = px.bar(
        region_analysis,
        x='责任区域',
        y='总价值',
        color='总库存量',
        title="各区域责任库存价值分布",
        text='批次数量',
        color_continuous_scale='Reds'
    )
    region_fig.update_traces(textposition='outside')
    region_fig.update_layout(height=400, plot_bgcolor='white')

    # 责任人风险分布
    person_risk = batch_analysis.groupby(['责任人', '风险程度']).size().unstack(fill_value=0)

    if not person_risk.empty:
        # 确保所有风险等级列都存在
        all_risk_levels = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        for risk in all_risk_levels:
            if risk not in person_risk.columns:
                person_risk[risk] = 0

        # 选择前10个责任人
        person_totals = person_risk.sum(axis=1).sort_values(ascending=False).head(10)
        top_persons = person_risk.loc[person_totals.index]

        # 使用更安全的go.Figure方式创建图表
        person_fig = go.Figure()

        for risk in all_risk_levels:
            if risk in top_persons.columns:  # 确保该风险级别存在于数据中
                person_fig.add_trace(go.Bar(
                    x=top_persons.index,
                    y=top_persons[risk],
                    name=risk,
                    marker_color=INVENTORY_RISK_COLORS.get(risk, '#CCCCCC')
                ))

        person_fig.update_layout(
            title="责任人风险分布（Top 10）",
            barmode='stack',
            height=400,
            xaxis_title="责任人",
            yaxis_title="批次数量",
            xaxis=dict(tickangle=45),
            plot_bgcolor='white'
        )
    else:
        person_fig = None

    return region_fig, person_fig


def create_clearance_prediction_charts(batch_analysis):
    """创建清库预测图表"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 清库天数分布直方图
    valid_clearance = batch_analysis[
        (batch_analysis['预计清库天数'] != float('inf')) &
        (batch_analysis['预计清库天数'] <= 365)
        ]

    if not valid_clearance.empty:
        hist_fig = px.histogram(
            valid_clearance,
            x='预计清库天数',
            nbins=20,
            title="清库天数分布",
            color_discrete_sequence=[COLORS['primary']]
        )
        hist_fig.add_vline(x=90, line_dash="dash", line_color="red",
                           annotation_text="90天风险线")
        hist_fig.update_layout(height=400, plot_bgcolor='white')
    else:
        hist_fig = None

    # 预测偏差分析
    # 将预测偏差转换为数值
    batch_analysis['预测偏差值'] = batch_analysis['预测偏差'].apply(
        lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) and '%' in x and x != '异常' else 0
    )

    forecast_analysis = batch_analysis[abs(batch_analysis['预测偏差值']) <= 1.0].head(20)

    if not forecast_analysis.empty:
        # 添加产品显示列，使用产品简称
        forecast_analysis['产品显示'] = forecast_analysis['描述'].apply(
            lambda x: x.replace('口力', '').replace('-中国', '') if isinstance(x, str) else x
        )

        forecast_fig = px.scatter(
            forecast_analysis,
            x='预测偏差值',
            y='预计清库天数',
            size='批次价值',
            color='风险程度',
            hover_name='产品显示',  # 使用产品显示而非代码
            title="预测偏差 vs 清库天数",
            color_discrete_map=INVENTORY_RISK_COLORS
        )
        forecast_fig.add_vline(x=0, line_dash="dash", line_color="gray",
                               annotation_text="预测准确线")
        forecast_fig.update_layout(height=400, plot_bgcolor='white')
    else:
        forecast_fig = None

    return hist_fig, forecast_fig


# ==================== 5. 预测准确率分析函数 ====================
# 预测数据加载函数
@st.cache_data
def load_product_info():
    """加载产品信息数据"""
    try:
        # 创建示例数据
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
    except Exception as e:
        st.error(f"加载产品信息数据时出错: {str(e)}")
        return pd.DataFrame()


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
def load_actual_data():
    """加载实际销售数据"""
    try:
        # 创建示例数据
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
    except Exception as e:
        st.error(f"加载实际销售数据时出错: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_forecast_data():
    """加载预测数据"""
    try:
        # 创建示例数据
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

        # 重命名所属大区为所属区域以统一列名
        df = df.rename(columns={'所属大区': '所属区域'})

        return df
    except Exception as e:
        st.error(f"加载预测数据时出错: {str(e)}")
        return pd.DataFrame()


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


# 统一的数据筛选函数
def filter_data(data, months=None, regions=None):
    """统一的数据筛选函数"""
    filtered_data = data.copy()

    if months and len(months) > 0:
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months)]

    if regions and len(regions) > 0:
        filtered_data = filtered_data[filtered_data['所属区域'].isin(regions)]

    return filtered_data


# 数据处理和分析函数
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

        # 准确率
        df['数量准确率'] = np.where(
            (df['求和项:数量（箱）'] > 0) | (df['预计销售量'] > 0),
            np.maximum(0, 100 - np.abs(df['数量差异率'])) / 100,
            1  # 预测和实际都是0时准确率为100%
        )

    # 计算总体准确率
    national_accuracy = calculate_national_accuracy(merged_monthly)
    regional_accuracy = calculate_regional_accuracy(merged_monthly)

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
        '数量准确率': lambda x: safe_mean(x, 0)
    }).reset_index()

    return {
        'region_monthly': region_monthly_summary,
        'region_overall': region_overall
    }


# 计算产品增长率函数
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


def calculate_top_skus(merged_df, by_region=False):
    """计算占销售量80%的SKU及其准确率"""
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


# 格式化产品代码函数
def format_product_code(code, product_info_df, include_name=True):
    """将产品代码格式化为只显示简化名称，不显示代码"""
    if product_info_df is None or product_info_df.empty or code not in product_info_df['产品代码'].values:
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


def display_recommendations_table(latest_growth, product_info_df):
    """显示产品增长率和备货建议的图表"""
    if latest_growth.empty:
        st.warning("没有足够的数据来生成备货建议图表。")
        return

    # 确保数据中包含必要的列
    if '产品代码' not in latest_growth.columns:
        st.error("数据中缺少产品代码列。")
        return

    # 创建一个副本以避免修改原始数据
    display_data = latest_growth.copy()

    # 添加产品显示名称（如果尚未存在）
    if '产品显示' not in display_data.columns:
        display_data['产品显示'] = display_data.apply(
            lambda row: format_product_code(row['产品代码'], product_info_df, include_name=True),
            axis=1
        )

    # 按增长率降序排序
    display_data = display_data.sort_values('销量增长率', ascending=False)

    # 显示图表标题和说明
    st.markdown("### 产品备货建议一览")
    st.markdown("""
    <div style="margin-bottom: 1rem; padding: 0.9rem; background-color: rgba(76, 175, 80, 0.1); border-radius: 0.5rem; border-left: 0.5rem solid #4CAF50;">
        <p style="margin: 0; font-size: 0.9rem;">
            <b>图表说明</b>：展示了产品销量的增长趋势与备货建议。计算方法：优先使用同比增长率（当前月份与去年同期相比），如无同期数据则使用环比增长率（与前一月相比）。
            颜色区分了不同趋势：深蓝色表示强劲增长(>10%)，绿色表示增长(0-10%)，橙色表示轻微下降(-10-0%)，红色表示显著下降(<-10%)。
            悬停可查看详细的备货建议和调整幅度。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 创建趋势的颜色映射
    color_map = {
        '强劲增长': '#1E88E5',  # 深蓝色
        '增长': '#43A047',  # 绿色
        '轻微下降': '#FB8C00',  # 橙色
        '显著下降': '#E53935'  # 红色
    }

    # 准备自定义数据用于悬停提示
    custom_data = []
    for _, row in display_data.iterrows():
        # 将所有数值转为字符串，避免格式问题
        # 使用'当月销量'替代'3个月滚动销量'
        sales_value = "0"
        if '当月销量' in row and pd.notna(row['当月销量']):
            sales_value = str(int(row['当月销量']))

        trend = str(row['趋势']) if pd.notna(row['趋势']) else ""
        recommendation = str(row['备货建议']) if pd.notna(row['备货建议']) else ""
        adjust_pct = str(int(row['调整比例'])) + "%" if pd.notna(row['调整比例']) else "0%"
        icon = str(row.get('建议图标', '')) if pd.notna(row.get('建议图标', '')) else ""

        custom_data.append([sales_value, trend, recommendation, adjust_pct, icon])

    # 创建水平条形图
    fig = go.Figure()

    # 添加条形图
    fig.add_trace(go.Bar(
        y=display_data['产品显示'],
        x=display_data['销量增长率'],
        orientation='h',
        marker=dict(
            color=[color_map.get(trend, '#1f3867') for trend in display_data['趋势']],
            line=dict(width=0)
        ),
        customdata=custom_data,
        hovertemplate='<b>%{y}</b><br>' +
                      '增长率: %{x:.1f}%<br>' +
                      '当前销量: %{customdata[0]}箱<br>' +
                      '趋势: %{customdata[1]}<br>' +
                      '备货建议: %{customdata[2]} %{customdata[4]}<br>' +
                      '调整幅度: %{customdata[3]}<extra></extra>'
    ))

    # 添加零线
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=-0.5,
        y1=len(display_data) - 0.5,
        line=dict(color="black", width=1, dash="dash")
    )

    # 更新布局
    fig.update_layout(
        title="产品销量增长率与备货建议",
        xaxis=dict(
            title="增长率 (%)",
            zeroline=False
        ),
        yaxis=dict(
            title="产品",
            autorange="reversed"  # 将最高增长率的产品放在顶部
        ),
        height=max(500, len(display_data) * 30),  # 动态调整高度以适应产品数量
        margin=dict(l=10, r=10, t=100, b=10),  # 增加上边距为图例留出空间
        plot_bgcolor='white'
    )

    # 添加标注 - 在条形旁边显示增长率
    for i, row in enumerate(display_data.itertuples()):
        fig.add_annotation(
            x=row.销量增长率,
            y=row.产品显示,
            text=f"{row.销量增长率:.1f}% {row.建议图标 if hasattr(row, '建议图标') and pd.notna(row.建议图标) else ''}",
            showarrow=False,
            xshift=10 if row.销量增长率 >= 0 else -10,
            align="left" if row.销量增长率 >= 0 else "right",
            font=dict(
                color="#43A047" if row.销量增长率 >= 0 else "#E53935",
                size=10
            )
        )

    # 添加图例解释不同颜色的含义
    legend_items = [
        {"name": "强劲增长", "color": "#1E88E5", "description": "> 10%"},
        {"name": "增长", "color": "#43A047", "description": "0% ~ 10%"},
        {"name": "轻微下降", "color": "#FB8C00", "description": "-10% ~ 0%"},
        {"name": "显著下降", "color": "#E53935", "description": "< -10%"}
    ]

    # 在图表上方添加图例
    legend_annotations = []
    for i, item in enumerate(legend_items):
        # 计算x位置，平均分布在图表宽度上
        x_pos = 0.05 + (i * 0.25)
        legend_annotations.append(
            dict(
                x=x_pos,
                y=1.08,  # 放在图表上方
                xref="paper",
                yref="paper",
                text=f"<span style='color:{item['color']};'>■</span> {item['name']} ({item['description']})",
                showarrow=False,
                font=dict(size=10),
                align="left"
            )
        )

    fig.update_layout(annotations=legend_annotations)

    # 显示图表
    st.plotly_chart(fig, use_container_width=True)


# ==================== 6. 主页面逻辑 ====================
def main():
    """主页面函数"""
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

    # 加载预测准确率分析数据
    product_info = load_product_info()
    actual_df = load_actual_data()
    forecast_df = load_forecast_data()

    # 获取共有月份数据
    common_months = sorted(set(actual_df['所属年月'].unique()) & set(forecast_df['所属年月'].unique()))
    actual_df = actual_df[actual_df['所属年月'].isin(common_months)]
    forecast_df = forecast_df[forecast_df['所属年月'].isin(common_months)]

    # 处理预测数据
    processed_data = process_data(actual_df, forecast_df, product_info)

    # 获取所有月份
    all_months = sorted(processed_data['merged_monthly']['所属年月'].unique())
    # 获取最近3个月
    latest_months = get_last_three_months()
    valid_latest_months = [month for month in latest_months if month in all_months]

    # 创建标签页 - 整合两个页面的标签
    tabs = st.tabs([
        "📊 库存概览",
        "⚠️ 批次风险",
        "👥 责任归属",
        "📈 清库预测",
        "📋 详细分析",
        "📊 预测总览",
        "🔍 预测差异分析",
        "📈 产品趋势",
        "🔍 重点SKU分析"
    ])

    # === 库存分析部分 ===
    with tabs[0]:  # 库存概览
        st.markdown('<div class="sub-header">📊 库存关键指标</div>', unsafe_allow_html=True)

        # KPI指标行
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_inv = analysis_result.get('total_inventory', 0)
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">总库存量</p>
                <p class="card-value">{format_number(total_inv)}</p>
                <p class="card-text">当前总库存数量</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            assigned_inv = analysis_result.get('assigned_inventory', 0)
            assigned_pct = (assigned_inv / total_inv * 100) if total_inv > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">已分配库存占比</p>
                <p class="card-value">{format_percentage(assigned_pct)}</p>
                <p class="card-text">已分配给订单的库存</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            risk_dist = analysis_result.get('risk_distribution', {})
            high_risk_count = risk_dist.get('极高风险', 0) + risk_dist.get('高风险', 0)
            total_batches = sum(risk_dist.values()) if risk_dist else 0
            high_risk_pct = (high_risk_count / total_batches * 100) if total_batches > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">高风险批次占比</p>
                <p class="card-value">{format_percentage(high_risk_pct)}</p>
                <p class="card-text">需要重点关注的批次</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            pending_inv = analysis_result.get('pending_inventory', 0)
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">待入库量</p>
                <p class="card-value">{format_number(pending_inv)}</p>
                <p class="card-text">即将到货的库存</p>
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
            <b>图表解读：</b> 左图展示库存健康状况分布，绿色表示健康库存，橙色表示库存不足，红色表示库存过剩。
            右图显示各风险等级的批次数量分布，颜色从蓝色到红色表示风险程度递增。
            <b>行动建议：</b> 重点关注红色区域（高风险/库存过剩），制定清库计划；橙色区域需要及时补货；绿色区域保持当前策略。
            """)

    with tabs[1]:  # 批次风险
        st.markdown('<div class="sub-header">⚠️ 批次风险分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 风险统计
            col1, col2, col3 = st.columns(3)

            with col1:
                extreme_high = len(batch_analysis[batch_analysis['风险程度'] == '极高风险'])
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">极高风险批次</p>
                    <p class="card-value" style="color: {INVENTORY_RISK_COLORS['极高风险']};">{extreme_high}</p>
                    <p class="card-text">需要紧急处理</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                high_risk = len(batch_analysis[batch_analysis['风险程度'] == '高风险'])
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">高风险批次</p>
                    <p class="card-value" style="color: {INVENTORY_RISK_COLORS['高风险']};">{high_risk}</p>
                    <p class="card-text">优先关注处理</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                avg_age = batch_analysis['库龄'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">平均库龄</p>
                    <p class="card-value">{format_days(avg_age)}</p>
                    <p class="card-text">所有批次平均库龄</p>
                </div>
                """, unsafe_allow_html=True)

            # 风险图表
            age_fig, scatter_fig = create_batch_risk_charts(batch_analysis)

            if age_fig:
                st.plotly_chart(age_fig, use_container_width=True)

            if scatter_fig:
                st.plotly_chart(scatter_fig, use_container_width=True)

            # 添加图表解释
            if age_fig or scatter_fig:
                add_chart_explanation("""
                <b>图表解读：</b> 上图显示高风险批次的库龄分布，颜色区分风险等级。下图展示库龄与清库天数的关系，气泡大小表示批次价值。
                红色虚线标记90天风险阈值，右上角象限为最高风险区域。
                <b>行动建议：</b> 优先处理库龄长且清库天数多的批次；对高价值风险批次制定专项清库方案；建立批次预警机制。
                """)
        else:
            st.info("当前筛选条件下暂无批次数据")

    with tabs[2]:  # 责任归属
        st.markdown('<div class="sub-header">👥 责任归属分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 责任统计
            region_stats = batch_analysis.groupby('责任区域')['批次价值'].sum().sort_values(ascending=False)
            person_stats = batch_analysis.groupby('责任人')['批次价值'].sum().sort_values(ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                top_region = region_stats.index[0] if len(region_stats) > 0 else "无"
                top_region_value = region_stats.iloc[0] if len(region_stats) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">最大责任区域</p>
                    <p class="card-value">{top_region}</p>
                    <p class="card-text">责任价值: {format_currency(top_region_value)}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                top_person = person_stats.index[0] if len(person_stats) > 0 else "无"
                top_person_value = person_stats.iloc[0] if len(person_stats) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">最大责任人</p>
                    <p class="card-value">{top_person}</p>
                    <p class="card-text">责任价值: {format_currency(top_person_value)}</p>
                </div>
                """, unsafe_allow_html=True)

            # 责任图表
            region_fig, person_fig = create_responsibility_charts(batch_analysis)

            if region_fig:
                st.plotly_chart(region_fig, use_container_width=True)

            if person_fig:
                st.plotly_chart(person_fig, use_container_width=True)

            # 添加图表解释
            if region_fig or person_fig:
                add_chart_explanation("""
                <b>图表解读：</b> 上图显示各区域的责任库存价值分布，条高表示价值，颜色深浅表示库存量。
                下图展示主要责任人的风险批次分布，堆叠柱状图显示各风险等级的批次数量。
                <b>行动建议：</b> 对责任价值高的区域和人员进行重点培训；建立责任制考核机制；优化预测和销售协同流程。
                """)
        else:
            st.info("当前筛选条件下暂无责任归属数据")

    with tabs[3]:  # 清库预测
        st.markdown('<div class="sub-header">📈 清库预测分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 清库统计
            infinite_batches = len(batch_analysis[batch_analysis['预计清库天数'] == float('inf')])
            long_clearance = len(batch_analysis[
                                     (batch_analysis['预计清库天数'] != float('inf')) &
                                     (batch_analysis['预计清库天数'] > 180)
                                     ])
            avg_clearance = batch_analysis[batch_analysis['预计清库天数'] != float('inf')]['预计清库天数'].mean()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">无法清库批次</p>
                    <p class="card-value" style="color: {COLORS['danger']};">{infinite_batches}</p>
                    <p class="card-text">需要特殊处理</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">长期积压批次</p>
                    <p class="card-value" style="color: {COLORS['warning']};">{long_clearance}</p>
                    <p class="card-text">清库超过180天</p>
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

            if forecast_fig:
                st.plotly_chart(forecast_fig, use_container_width=True)

            # 添加图表解释
            if hist_fig or forecast_fig:
                add_chart_explanation("""
                <b>图表解读：</b> 上图显示清库天数的分布情况，红线标记90天风险阈值。下图展示预测偏差与清库天数的关系。
                预测偏差为正值表示预测过高，负值表示预测过低，气泡大小表示批次价值。
                <b>行动建议：</b> 对超过180天的长期积压制定专项清库计划；改善预测准确性，减少预测偏差；建立动态清库监控机制。
                """)
        else:
            st.info("当前筛选条件下暂无清库预测数据")

    with tabs[4]:  # 详细分析
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
                # 处理无穷大值
                if sort_by == "预计清库天数":
                    display_data = display_data[display_data['预计清库天数'] != float('inf')]
                display_data = display_data.sort_values(sort_by, ascending=ascending)

            # 限制显示数量
            if show_count != "全部":
                display_data = display_data.head(int(show_count))

            # 显示数据表
            if not display_data.empty:
                # 格式化显示列
                display_columns = [
                    '产品代码', '描述', '批次日期', '批次库存', '库龄', '批次价值',
                    '预计清库天数', '风险程度', '积压原因', '责任区域', '责任人', '建议措施'
                ]

                display_df = display_data[display_columns].copy()

                # 格式化数值
                display_df['批次价值'] = display_df['批次价值'].apply(lambda x: format_currency(x))
                display_df['预计清库天数'] = display_df['预计清库天数'].apply(
                    lambda x: "∞" if x == float('inf') else f"{x:.1f}天"
                )

                # 设置索引
                display_df.index = range(1, len(display_df) + 1)

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=600,
                    column_config={
                        "风险程度": st.column_config.TextColumn(
                            "风险程度",
                            help="批次风险等级评估"
                        ),
                        "批次价值": st.column_config.TextColumn(
                            "批次价值",
                            help="批次总价值（数量×单价）"
                        ),
                        "建议措施": st.column_config.TextColumn(
                            "建议措施",
                            help="针对该批次的处理建议"
                        )
                    }
                )

                # 数据洞察
                st.markdown('<div class="sub-header">数据洞察</div>', unsafe_allow_html=True)

                extreme_high_count = len(display_data[display_data['风险程度'] == '极高风险'])
                high_count = len(display_data[display_data['风险程度'] == '高风险'])
                total_value = display_data['批次价值'].sum()
                avg_age = display_data['库龄'].mean()

                insight_text = f"""
                **当前筛选结果洞察：**
                - 显示 {len(display_data)} 个批次，总价值 {format_currency(total_value)}
                - 极高风险批次 {extreme_high_count} 个，高风险批次 {high_count} 个
                - 平均库龄 {avg_age:.1f} 天
                - 主要积压原因：{display_data['积压原因'].mode().iloc[0] if not display_data['积压原因'].mode().empty else '混合因素'}

                **改进建议：**
                - 对极高风险和高风险批次制定紧急清库计划
                - 优化预测准确性，减少预测偏差导致的积压
                - 建立跨部门协作机制，提高销售响应速度
                - 定期审查库存健康状况，建立预警机制
                """

                st.markdown(insight_text)

            else:
                st.info("当前筛选和排序条件下无数据显示")
        else:
            st.info("暂无详细分析数据")

    # === 预测准确率分析部分 ===
    with tabs[5]:  # 预测总览
        # 在标签页内添加筛选器
        st.markdown("### 📊 分析筛选")
        with st.expander("筛选条件", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                overview_selected_months = st.multiselect(
                    "选择分析月份",
                    options=all_months,
                    default=valid_latest_months if valid_latest_months else ([all_months[-1]] if all_months else []),
                    key="overview_months"
                )

            with col2:
                all_regions = sorted(processed_data['merged_monthly']['所属区域'].unique())
                overview_selected_regions = st.multiselect(
                    "选择区域",
                    options=all_regions,
                    default=all_regions,
                    key="overview_regions"
                )

        # 根据筛选条件过滤数据
        overview_filtered_monthly = filter_data(processed_data['merged_monthly'], overview_selected_months,
                                                overview_selected_regions)
        overview_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], overview_selected_months,
                                                    overview_selected_regions)

        # 检查选定月份和区域是否为空
        if not overview_selected_months or not overview_selected_regions:
            st.warning("请选择至少一个月份和一个区域进行分析。")
        else:
            # 计算总览KPI
            total_actual_qty = overview_filtered_monthly['求和项:数量（箱）'].sum()
            total_forecast_qty = overview_filtered_monthly['预计销售量'].sum()
            total_diff = total_actual_qty - total_forecast_qty
            total_diff_percent = (total_diff / total_actual_qty * 100) if total_actual_qty > 0 else 0

            # 根据筛选条件计算准确率
            filtered_national_accuracy = calculate_national_accuracy(overview_filtered_monthly)
            national_qty_accuracy = filtered_national_accuracy['overall']['数量准确率'] * 100

            # 计算区域准确率
            filtered_regional_accuracy = calculate_regional_accuracy(overview_filtered_monthly)
            selected_regions_accuracy = filtered_regional_accuracy['region_overall']
            selected_regions_qty_accuracy = selected_regions_accuracy['数量准确率'].mean() * 100

            # 指标卡行
            st.markdown("### 🔑 关键绩效指标")
            col1, col2, col3, col4 = st.columns(4)

            # 总销售量
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">实际销售量</p>
                    <p class="card-value">{format_number(total_actual_qty)}</p>
                    <p class="card-text">选定期间内</p>
                </div>
                """, unsafe_allow_html=True)

            # 总预测销售量
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">预测销售量</p>
                    <p class="card-value">{format_number(total_forecast_qty)}</p>
                    <p class="card-text">选定期间内</p>
                </div>
                """, unsafe_allow_html=True)

            # 全国准确率
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">全国销售量准确率</p>
                    <p class="card-value">{national_qty_accuracy:.2f}%</p>
                    <p class="card-text">整体预测精度</p>
                    <p class="card-text" style="font-style: italic; font-size: 0.8rem;">计算逻辑：1-|实际销量-预测销量|/实际销量</p>
                </div>
                """, unsafe_allow_html=True)

            # 选定区域准确率
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">选定区域准确率</p>
                    <p class="card-value">{selected_regions_qty_accuracy:.2f}%</p>
                    <p class="card-text">选定区域预测精度</p>
                    <p class="card-text" style="font-style: italic; font-size: 0.8rem;">计算逻辑：各区域准确率的平均值</p>
                </div>
                """, unsafe_allow_html=True)

            # 区域销售分析
            st.markdown('<div class="sub-header">📊 区域销售分析</div>', unsafe_allow_html=True)

            # 计算每个区域的销售量和预测量
            region_sales_comparison = overview_filtered_monthly.groupby('所属区域').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 计算差异
            region_sales_comparison['差异'] = region_sales_comparison['求和项:数量（箱）'] - region_sales_comparison[
                '预计销售量']
            region_sales_comparison['差异率'] = region_sales_comparison['差异'] / region_sales_comparison[
                '求和项:数量（箱）'] * 100

            # 创建水平堆叠柱状图
            fig_sales_comparison = go.Figure()

            # 添加实际销售量柱
            fig_sales_comparison.add_trace(go.Bar(
                y=region_sales_comparison['所属区域'],
                x=region_sales_comparison['求和项:数量（箱）'],
                name='实际销售量',
                marker_color='royalblue',
                orientation='h'
            ))

            # 添加预测销售量柱
            fig_sales_comparison.add_trace(go.Bar(
                y=region_sales_comparison['所属区域'],
                x=region_sales_comparison['预计销售量'],
                name='预测销售量',
                marker_color='lightcoral',
                orientation='h'
            ))

            # 添加差异率点
            fig_sales_comparison.add_trace(go.Scatter(
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
            fig_sales_comparison.update_layout(
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

            # 准备区域详细信息
            region_details = []
            for _, region_row in region_sales_comparison.iterrows():
                region = region_row['所属区域']
                # 获取该区域数据
                region_data = overview_filtered_monthly[overview_filtered_monthly['所属区域'] == region]

                if not region_data.empty:
                    # 找出差异最大的产品
                    product_diff = region_data.groupby('产品代码').agg({
                        '求和项:数量（箱）': 'sum',
                        '预计销售量': 'sum'
                    })
                    product_diff['差异'] = product_diff['求和项:数量（箱）'] - product_diff['预计销售量']
                    product_diff['差异率'] = product_diff.apply(
                        lambda row: (row['差异'] / row['求和项:数量（箱）'] * 100) if row['求和项:数量（箱）'] > 0 else 0,
                        axis=1
                    )

                    if not product_diff.empty:
                        # 找出差异率最大的产品
                        max_diff_idx = product_diff['差异率'].abs().idxmax()
                        product_code = max_diff_idx
                        product_name = format_product_code(product_code, product_info, include_name=True)
                        actual = product_diff.loc[max_diff_idx, '求和项:数量（箱）']
                        forecast = product_diff.loc[max_diff_idx, '预计销售量']
                        diff_rate = product_diff.loc[max_diff_idx, '差异率']

                        # 找该产品的主要销售员
                        product_sales = overview_filtered_salesperson[
                            (overview_filtered_salesperson['所属区域'] == region) &
                            (overview_filtered_salesperson['产品代码'] == product_code)
                            ]

                        if not product_sales.empty:
                            sales_by_person = product_sales.groupby('销售员').agg({
                                '求和项:数量（箱）': 'sum'
                            })
                            top_salesperson = sales_by_person[
                                '求和项:数量（箱）'].idxmax() if not sales_by_person.empty else "未知"
                        else:
                            top_salesperson = "未知"

                        detail = f"最大差异产品: {product_name}<br>"
                        detail += f"实际销量: {actual:.0f}箱<br>"
                        detail += f"预测销量: {forecast:.0f}箱<br>"
                        detail += f"差异率: {diff_rate:.1f}%<br>"
                        detail += f"主要销售员: {top_salesperson}"
                    else:
                        detail = "无产品差异数据"
                else:
                    detail = "无区域数据"

                region_details.append(detail)

            # 更新悬停模板
            fig_sales_comparison.update_traces(
                hovertemplate='<b>%{y}区域</b><br>%{x:,.0f}箱<br><br><b>差异详情:</b><br>%{customdata}<extra>%{name}</extra>',
                customdata=region_details,
                selector=dict(type='bar')
            )

            st.plotly_chart(fig_sales_comparison, use_container_width=True)

            # 生成动态解读
            diff_explanation = f"""
            <b>图表解读：</b> 此图展示了各区域的实际销售量(蓝色)与预测销售量(红色)对比，绿色点表示正差异率(低估)，红色点表示负差异率(高估)。
            差异率越高(绝对值越大)，表明预测偏离实际的程度越大。
            """

            # 添加具体分析
            if not region_sales_comparison.empty:
                # 找出差异最大的项目
                high_diff_regions = region_sales_comparison[abs(region_sales_comparison['差异率']) > 15]
                if not high_diff_regions.empty:
                    diff_explanation += "<br><b>需关注区域：</b> "
                    for _, row in high_diff_regions.iterrows():
                        if row['差异率'] > 0:
                            diff_explanation += f"{row['所属区域']}区域低估了{row['差异率']:.1f}%，"
                        else:
                            diff_explanation += f"{row['所属区域']}区域高估了{abs(row['差异率']):.1f}%，"

                diff_explanation += f"<br><b>行动建议：</b> "

                # 添加具体建议
                if not high_diff_regions.empty:
                    for _, row in high_diff_regions.iterrows():
                        if row['差异率'] > 0:
                            adjust = abs(round(row['差异率']))
                            diff_explanation += f"建议{row['所属区域']}区域提高预测量{adjust}%以满足实际需求；"
                        else:
                            adjust = abs(round(row['差异率']))
                            diff_explanation += f"建议{row['所属区域']}区域降低预测量{adjust}%以避免库存积压；"
                else:
                    diff_explanation += "各区域预测与实际销售较为匹配，建议维持当前预测方法。"

            add_chart_explanation(diff_explanation)

            # 添加历史趋势分析部分
            st.markdown('<div class="sub-header">📊 销售与预测历史趋势</div>', unsafe_allow_html=True)

            # 准备历史趋势数据
            monthly_trend = overview_filtered_monthly.groupby(['所属年月', '所属区域']).agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            # 使用全国数据
            # 计算全国趋势
            national_trend = monthly_trend.groupby('所属年月').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            trend_data = national_trend

            # 创建销售与预测趋势图
            fig_trend = go.Figure()

            # 添加实际销售线
            fig_trend.add_trace(go.Scatter(
                x=trend_data['所属年月'],
                y=trend_data['求和项:数量（箱）'],
                mode='lines+markers',
                name='实际销售量',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8)
            ))

            # 添加预测销售线
            fig_trend.add_trace(go.Scatter(
                x=trend_data['所属年月'],
                y=trend_data['预计销售量'],
                mode='lines+markers',
                name='预测销售量',
                line=dict(color='lightcoral', width=3, dash='dot'),
                marker=dict(size=8)
            ))

            # 计算差异率
            trend_data['差异率'] = (trend_data['求和项:数量（箱）'] - trend_data['预计销售量']) / trend_data[
                '求和项:数量（箱）'] * 100

            # 添加差异率线
            fig_trend.add_trace(go.Scatter(
                x=trend_data['所属年月'],
                y=trend_data['差异率'],
                mode='lines+markers+text',
                name='差异率 (%)',
                yaxis='y2',
                line=dict(color='green', width=2),
                marker=dict(size=8),
                text=[f"{x:.1f}%" for x in trend_data['差异率']],
                textposition='top center'
            ))

            # 更新布局
            title = f"销售与预测历史趋势分析"
            fig_trend.update_layout(
                title=title,
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

            # 添加悬停提示
            fig_trend.update_traces(
                hovertemplate='<b>%{x}</b><br>%{name}: %{y:,.0f}箱<extra></extra>',
                selector=dict(name=['实际销售量', '预测销售量'])
            )

            fig_trend.update_traces(
                hovertemplate='<b>%{x}</b><br>%{name}: %{y:.2f}%<extra></extra>',
                selector=dict(name='差异率 (%)')
            )

            # 强调选定月份
            if overview_selected_months:
                for month in overview_selected_months:
                    if month in trend_data['所属年月'].values:
                        fig_trend.add_shape(
                            type="rect",
                            x0=month,
                            x1=month,
                            y0=0,
                            y1=trend_data['求和项:数量（箱）'].max() * 1.1,
                            fillcolor="rgba(144, 238, 144, 0.2)",
                            line=dict(width=0)
                        )

            st.plotly_chart(fig_trend, use_container_width=True)

            # 生成动态解读
            trend_explanation = f"""
            <b>图表解读：</b> 此图展示了全国历史销售量(蓝线)与预测销售量(红线)趋势，以及月度差异率(绿线)。
            通过观察趋势可以发现销售的季节性波动、预测与实际的一致性以及差异率的变化趋势。
            """

            # 添加具体分析
            if not trend_data.empty and len(trend_data) > 1:
                # 计算整体趋势
                sales_trend = np.polyfit(range(len(trend_data)), trend_data['求和项:数量（箱）'], 1)[0]
                sales_trend_direction = "上升" if sales_trend > 0 else "下降"

                # 找出差异率最大和最小的月份
                max_diff_month = trend_data.loc[trend_data['差异率'].abs().idxmax()]

                # 计算准确率均值
                accuracy_mean = (100 - abs(trend_data['差异率'])).mean()

                trend_explanation += f"<br><b>趋势分析：</b> "

                trend_explanation += f"全国销售量整体呈{sales_trend_direction}趋势，"
                trend_explanation += f"历史准确率平均为{accuracy_mean:.1f}%，"
                trend_explanation += f"{max_diff_month['所属年月']}月差异率最大，达{max_diff_month['差异率']:.1f}%。"

                # 生成建议
                trend_explanation += f"<br><b>行动建议：</b> "

                # 根据趋势分析生成建议
                if abs(trend_data['差异率']).mean() > 10:
                    trend_explanation += f"针对全国的销售预测仍有提升空间，建议分析差异率较大月份的原因；"

                    # 检查是否有季节性模式
                    month_numbers = [int(m.split('-')[1]) for m in trend_data['所属年月']]
                    if len(month_numbers) >= 12:
                        spring_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[345]$')]['差异率']).mean()
                        summer_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[678]$')]['差异率']).mean()
                        autumn_diff = abs(
                            trend_data[trend_data['所属年月'].str.contains(r'-0[9]$|10|11$')]['差异率']).mean()
                        winter_diff = abs(
                            trend_data[trend_data['所属年月'].str.contains(r'-12$|-0[12]$')]['差异率']).mean()

                        seasons = [('春季', spring_diff), ('夏季', summer_diff), ('秋季', autumn_diff),
                                   ('冬季', winter_diff)]
                        worst_season = max(seasons, key=lambda x: x[1])

                        trend_explanation += f"特别注意{worst_season[0]}月份的预测，历史上这些月份差异率较大({worst_season[1]:.1f}%)；"

                    trend_explanation += "考虑在预测模型中增加季节性因素，提高季节性预测的准确性。"
                else:
                    trend_explanation += f"全国的销售预测整体表现良好，建议保持当前预测方法，"
                    trend_explanation += "持续监控销售趋势变化，及时调整预测模型。"

            add_chart_explanation(trend_explanation)

            with tabs[6]:  # 预测差异分析
                # 在标签页内添加筛选器
                st.markdown("### 📊 预测差异分析筛选")
                with st.expander("筛选条件", expanded=True):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        diff_selected_months = st.multiselect(
                            "选择分析月份",
                            options=all_months,
                            default=valid_latest_months if valid_latest_months else (
                                [all_months[-1]] if all_months else []),
                            key="diff_months"
                        )

                    with col2:
                        diff_selected_regions = st.multiselect(
                            "选择区域",
                            options=all_regions,
                            default=all_regions,
                            key="diff_regions"
                        )

                    with col3:
                        analysis_dimension = st.selectbox(
                            "选择分析维度",
                            options=['产品', '销售员'],
                            key="dimension_select"
                        )

                # 筛选数据
                diff_filtered_monthly = filter_data(processed_data['merged_monthly'], diff_selected_months,
                                                    diff_selected_regions)
                diff_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], diff_selected_months,
                                                        diff_selected_regions)

                # 检查筛选条件是否有效
                if not diff_selected_months or not diff_selected_regions:
                    st.warning("请选择至少一个月份和一个区域进行分析。")
                else:
                    st.markdown("### 预测差异详细分析")

                    # 使用全国数据
                    # 准备数据
                    # 全国数据，按选定维度汇总
                    if analysis_dimension == '产品':
                        diff_data = diff_filtered_monthly.groupby(['产品代码', '所属区域']).agg({
                            '求和项:数量（箱）': 'sum',
                            '预计销售量': 'sum',
                        }).reset_index()

                        # 合并销售员信息(按区域和产品分组)
                        sales_info = diff_filtered_salesperson.groupby(['所属区域', '产品代码', '销售员']).agg({
                            '求和项:数量（箱）': 'sum'
                        }).reset_index()

                        # 对每个产品找出主要销售员(销量最大的)
                        top_sales = sales_info.loc[
                            sales_info.groupby(['所属区域', '产品代码'])['求和项:数量（箱）'].idxmax()]
                        top_sales = top_sales[['所属区域', '产品代码', '销售员']]

                        # 将销售员信息合并到差异数据中
                        diff_data = pd.merge(diff_data, top_sales, on=['所属区域', '产品代码'], how='left')

                        # 汇总到产品级别
                        diff_summary = diff_data.groupby('产品代码').agg({
                            '求和项:数量（箱）': 'sum',
                            '预计销售量': 'sum'
                        }).reset_index()

                    else:  # 销售员维度
                        diff_data = diff_filtered_salesperson.groupby(['销售员', '所属区域', '产品代码']).agg({
                            '求和项:数量（箱）': 'sum',
                            '预计销售量': 'sum'
                        }).reset_index()

                        # 对每个销售员找出主要产品(销量最大的)
                        top_products = diff_data.loc[
                            diff_data.groupby(['销售员', '所属区域'])['求和项:数量（箱）'].idxmax()]
                        top_products = top_products[['销售员', '所属区域', '产品代码']]

                        # 汇总到销售员级别
                        diff_summary = diff_data.groupby('销售员').agg({
                            '求和项:数量（箱）': 'sum',
                            '预计销售量': 'sum'
                        }).reset_index()

                    # 计算差异和差异率
                    diff_summary['数量差异'] = diff_summary['求和项:数量（箱）'] - diff_summary['预计销售量']
                    diff_summary['数量差异率'] = diff_summary['数量差异'] / diff_summary['求和项:数量（箱）'] * 100

                    # 处理产品名称显示
                    if analysis_dimension == '产品':
                        diff_summary['产品名称'] = diff_summary['产品代码'].apply(
                            lambda x: format_product_code(x, product_info, include_name=True))
                        diff_summary['产品显示'] = diff_summary['产品名称']
                        dimension_column = '产品显示'
                    else:
                        dimension_column = '销售员'

                    # 按差异率绝对值降序排序（差异最大的排在前面）
                    diff_summary = diff_summary.sort_values('数量差异率', key=abs, ascending=False)

                    # 显示所有数据，不再限制数量
                    top_diff_items = diff_summary

                    # 准备详细信息用于悬停显示
                    hover_data = []
                    for idx, row in top_diff_items.iterrows():
                        if analysis_dimension == '产品':
                            # 找到该产品的详细信息
                            # 查找该产品在所有选定月份的数据
                            product_details = diff_filtered_monthly[
                                diff_filtered_monthly['产品代码'] == row['产品代码']]
                            product_details = product_details.sort_values('所属年月')

                            # 按月份汇总
                            monthly_info = []
                            for month, month_data in product_details.groupby('所属年月'):
                                actual = month_data['求和项:数量（箱）'].sum()
                                forecast = month_data['预计销售量'].sum()
                                diff_rate = (actual - forecast) / actual * 100 if actual > 0 else 0
                                monthly_info.append(
                                    f"{month}月: 实际 {actual:.0f}箱, 预测 {forecast:.0f}箱, 差异 {diff_rate:.1f}%"
                                )

                            # 分析区域和销售员
                            region_info = []
                            for region, region_data in product_details.groupby('所属区域'):
                                region_actual = region_data['求和项:数量（箱）'].sum()
                                region_forecast = region_data['预计销售量'].sum()
                                region_diff = (
                                                      region_actual - region_forecast) / region_actual * 100 if region_actual > 0 else 0

                                # 找出该区域主要销售员
                                region_salesperson = diff_filtered_salesperson[
                                    (diff_filtered_salesperson['产品代码'] == row['产品代码']) &
                                    (diff_filtered_salesperson['所属区域'] == region)
                                    ]

                                if not region_salesperson.empty:
                                    top_salesperson = region_salesperson.groupby('销售员')[
                                        '求和项:数量（箱）'].sum().idxmax()
                                    region_info.append(
                                        f"{region}区域: 差异 {region_diff:.1f}%, 主要销售员: {top_salesperson}"
                                    )

                            # 备货建议
                            recent_sales = product_details.sort_values('所属年月', ascending=False)
                            recent_trend = 0
                            if len(recent_sales) >= 2:
                                recent_values = recent_sales.groupby('所属年月')['求和项:数量（箱）'].sum()
                                if len(recent_values) >= 2:
                                    latest_values = recent_values.iloc[:2].values
                                    if latest_values[1] > 0:  # 避免除以零
                                        recent_trend = (latest_values[0] - latest_values[1]) / latest_values[1] * 100

                            recommendation = "<b>备货建议:</b><br>"
                            if recent_trend > 15:
                                recommendation += f"销量呈上升趋势(+{recent_trend:.1f}%)，建议增加备货{min(50, round(abs(recent_trend)))}%"
                            elif recent_trend < -15:
                                recommendation += f"销量呈下降趋势({recent_trend:.1f}%)，建议减少备货{min(30, abs(round(recent_trend)))}%"
                            else:
                                recommendation += "销量较稳定，建议维持当前备货水平，关注区域差异"

                            # 合并所有信息
                            hover_info = "<br>".join(monthly_info) + "<br><br>" + "<br>".join(
                                region_info) + "<br><br>" + recommendation

                        else:  # 销售员维度
                            # 查找该销售员的所有产品差异
                            salesperson_products = diff_data[diff_data['销售员'] == row['销售员']]

                            # 按产品分组并计算差异
                            product_grouped = salesperson_products.groupby('产品代码').agg({
                                '求和项:数量（箱）': 'sum',
                                '预计销售量': 'sum'
                            })
                            product_grouped['数量差异'] = product_grouped['求和项:数量（箱）'] - product_grouped[
                                '预计销售量']
                            product_grouped['数量差异率'] = product_grouped.apply(
                                lambda x: (x['数量差异'] / x['求和项:数量（箱）'] * 100) if x[
                                                                                              '求和项:数量（箱）'] > 0 else 0,
                                axis=1
                            )
                            # 按差异率绝对值排序
                            product_grouped = product_grouped.sort_values(by='数量差异率', key=abs, ascending=False)

                            # 构建产品详情（最多显示10个）
                            products_info = []
                            for product_code, detail in product_grouped.head(10).iterrows():
                                product_name = format_product_code(product_code, product_info, include_name=True)
                                products_info.append(
                                    f"{product_name}: 差异率 {detail['数量差异率']:.1f}%, "
                                    f"实际 {detail['求和项:数量（箱）']:.0f}箱, 预测 {detail['预计销售量']:.0f}箱"
                                )

                            # 生成备货建议
                            recommendation = "<b>备货建议:</b><br>"
                            overestimated = product_grouped[product_grouped['数量差异率'] < -10]
                            underestimated = product_grouped[product_grouped['数量差异率'] > 10]

                            if len(product_grouped) > 0:
                                if len(overestimated) > len(underestimated) * 1.5:
                                    recommendation += f"该销售员整体高估趋势，建议下调预测10-15%<br>"
                                elif len(underestimated) > len(overestimated) * 1.5:
                                    recommendation += f"该销售员整体低估趋势，建议上调预测10-15%<br>"
                                else:
                                    recommendation += "需针对具体产品调整:<br>"

                                # 添加最需要调整的3个产品建议
                                top_products = 0
                                for product_code, detail in product_grouped.head(5).iterrows():
                                    if abs(detail['数量差异率']) > 10 and top_products < 3:
                                        product_name = format_product_code(product_code, product_info,
                                                                           include_name=True)
                                        adjustment = min(50, abs(round(detail['数量差异率'])))

                                        if detail['数量差异率'] > 10:
                                            recommendation += f"· {product_name}: 上调预测{adjustment}%<br>"
                                        else:
                                            recommendation += f"· {product_name}: 下调预测{adjustment}%<br>"

                                        top_products += 1
                            else:
                                recommendation += "数据不足，无法提供建议"

                            hover_info = "<br>".join(products_info) + "<br><br>" + recommendation

                        hover_data.append(hover_info)

                    # 创建水平堆叠柱状图
                    fig_diff = go.Figure()

                    # 添加实际销售量柱
                    fig_diff.add_trace(go.Bar(
                        y=top_diff_items[dimension_column],
                        x=top_diff_items['求和项:数量（箱）'],
                        name='实际销售量',
                        marker_color='royalblue',
                        orientation='h',
                        customdata=hover_data,
                        hovertemplate='<b>%{y}</b><br>实际销售量: %{x:,.0f}箱<br><br><b>详细差异来源:</b><br>%{customdata}<extra></extra>'
                    ))

                    # 添加预测销售量柱
                    fig_diff.add_trace(go.Bar(
                        y=top_diff_items[dimension_column],
                        x=top_diff_items['预计销售量'],
                        name='预测销售量',
                        marker_color='lightcoral',
                        orientation='h',
                        hovertemplate='<b>%{y}</b><br>预测销售量: %{x:,.0f}箱<extra></extra>'
                    ))

                    # 添加差异率点
                    fig_diff.add_trace(go.Scatter(
                        y=top_diff_items[dimension_column],
                        x=[top_diff_items['求和项:数量（箱）'].max() * 1.05] * len(top_diff_items),  # 放在右侧
                        mode='markers+text',
                        marker=dict(
                            color=top_diff_items['数量差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                            size=10
                        ),
                        text=[f"{x:.1f}%" for x in top_diff_items['数量差异率']],
                        textposition='middle right',
                        name='差异率 (%)',
                        hovertemplate='<b>%{y}</b><br>差异率: %{text}<extra></extra>'
                    ))

                    # 更新布局
                    title = f"全国预测与实际销售对比 (按{analysis_dimension}维度，差异率降序)"
                    fig_diff.update_layout(
                        title=title,
                        xaxis=dict(
                            title="销售量 (箱)",
                            tickformat=",",
                            showexponent="none"
                        ),
                        yaxis=dict(title=analysis_dimension),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        barmode='group',
                        plot_bgcolor='white',
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=12
                        ),
                        height=max(600, len(top_diff_items) * 25)  # 动态调整高度以适应数据量
                    )

                    st.plotly_chart(fig_diff, use_container_width=True)

                    # 生成动态解读
                    diff_explanation = f"""
                                    <b>图表解读：</b> 此图展示全国的{analysis_dimension}维度预测差异情况，蓝色代表实际销售量，红色代表预测销售量，点的颜色表示差异率(绿色为低估，红色为高估)。
                                    悬停在"实际销售量"条形上，可以查看详细的差异来源，包括区域、销售员或产品的具体信息。这有助于精确定位预测不准确的具体原因。
                                    """

                    # 添加数据钻取分析建议
                    diff_explanation += f"<br><b>差异分析建议：</b> "

                    if analysis_dimension == '产品':
                        diff_explanation += "对于差异较大的产品，建议分析产品在不同区域和销售员间的表现差异，识别特定产品预测准确性的影响因素；"
                        diff_explanation += "可切换到销售员维度，分析销售员对产品预测的准确程度。"
                    else:  # 销售员维度
                        diff_explanation += "对于差异较大的销售员，建议分析其销售的产品组合和区域分布，识别特定销售员预测准确性的影响因素；"
                        diff_explanation += "可切换到产品维度，分析产品的销售员层面差异。"

                    add_chart_explanation(diff_explanation)

            with tabs[7]:  # 产品趋势
                # 在标签页内添加筛选器
                st.markdown("### 📊 分析筛选")
                with st.expander("筛选条件", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        trend_selected_months = st.multiselect(
                            "选择分析月份",
                            options=all_months,
                            default=valid_latest_months if valid_latest_months else (
                                [all_months[-1]] if all_months else []),
                            key="trend_months"
                        )

                    with col2:
                        trend_selected_regions = st.multiselect(
                            "选择区域",
                            options=all_regions,
                            default=all_regions,
                            key="trend_regions"
                        )

                # 筛选数据
                trend_filtered_monthly = filter_data(processed_data['merged_monthly'], trend_selected_months,
                                                     trend_selected_regions)

                # 检查筛选条件是否有效
                if not trend_selected_months or not trend_selected_regions:
                    st.warning("请选择至少一个月份和一个区域进行分析。")
                else:
                    st.markdown("### 产品销售趋势分析")

                    # 动态计算所选区域的产品增长率
                    product_growth = calculate_product_growth(actual_monthly=actual_df, regions=trend_selected_regions,
                                                              months=trend_selected_months)

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

                        # 显示备货建议表格
                        display_recommendations_table(latest_growth, product_info)

                    else:
                        st.warning(
                            "没有足够的历史数据来计算产品增长率。需要至少两个月的销售数据才能计算环比增长，或者至少两年的销售数据才能计算同比增长。")

            with tabs[8]:  # 重点SKU分析
                # 添加筛选器
                st.markdown("### 📊 分析筛选")
                with st.expander("筛选条件", expanded=True):
                    col1, col2 = st.columns(2)

                    # 获取当前系统月份作为默认值
                    current_month = datetime.now().strftime('%Y-%m')
                    current_month_in_data = False

                    # 检查当前月份是否在数据集中
                    if current_month in all_months:
                        current_month_in_data = True
                        default_month = [current_month]
                    else:
                        # 如果当前月份不在数据中，使用数据中的最新月份
                        default_month = [all_months[-1]] if all_months else []

                    with col1:
                        sku_selected_months = st.multiselect(
                            "选择分析月份",
                            options=all_months,
                            default=default_month,
                            key="sku_months"
                        )
                    with col2:
                        sku_selected_regions = st.multiselect(
                            "选择区域",
                            options=all_regions,
                            default=all_regions,
                            key="sku_regions"
                        )

                # 筛选数据
                sku_filtered_monthly = filter_data(processed_data['merged_monthly'], sku_selected_months,
                                                   sku_selected_regions)
                sku_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], sku_selected_months,
                                                       sku_selected_regions)

                # 重新计算重点SKU
                filtered_national_top_skus = calculate_top_skus(sku_filtered_monthly, by_region=False)
                filtered_regional_top_skus = calculate_top_skus(sku_filtered_monthly, by_region=True)

                # 使用新计算的结果
                national_top_skus = filtered_national_top_skus
                regional_top_skus = filtered_regional_top_skus

                # 检查筛选条件是否有效
                if not sku_selected_months or not sku_selected_regions:
                    st.warning("请选择至少一个月份和一个区域进行分析。")
                else:
                    st.markdown("### 销售量占比80%重点SKU分析")

                    # 显示全国重点SKU分析
                    if not national_top_skus.empty:
                        # 格式化准确率为百分比
                        national_top_skus['数量准确率'] = national_top_skus['数量准确率'] * 100

                        # 添加产品名称
                        national_top_skus['产品名称'] = national_top_skus['产品代码'].apply(
                            lambda x: format_product_code(x, product_info, include_name=True)
                        )
                        national_top_skus['产品显示'] = national_top_skus['产品名称']

                        # 合并增长率数据和备货建议
                        try:
                            # 使用当前选择的区域和月份计算增长率
                            product_growth_data = calculate_product_growth(
                                actual_monthly=actual_df,
                                regions=sku_selected_regions,
                                months=sku_selected_months
                            ).get('latest_growth', pd.DataFrame())

                            if not product_growth_data.empty:
                                national_top_skus = pd.merge(
                                    national_top_skus,
                                    product_growth_data[
                                        ['产品代码', '销量增长率', '趋势', '备货建议', '调整比例', '建议样式类',
                                         '建议图标']],
                                    on='产品代码',
                                    how='left'
                                )
                        except Exception as e:
                            print(f"合并备货建议数据时出错: {str(e)}")

                        # 创建水平条形图
                        fig_top_skus = go.Figure()

                        # 添加销售量条
                        fig_top_skus.add_trace(go.Bar(
                            y=national_top_skus['产品显示'],
                            x=national_top_skus['求和项:数量（箱）'],
                            name='销售量',
                            marker=dict(
                                color=national_top_skus['数量准确率'],
                                colorscale='RdYlGn',
                                cmin=0,
                                cmax=100,
                                colorbar=dict(
                                    title='准确率 (%)',
                                    x=1.05
                                )
                            ),
                            orientation='h'
                        ))

                        # 添加准确率和备货建议标记
                        for i, row in national_top_skus.iterrows():
                            accuracy_text = f"{row['数量准确率']:.0f}%"

                            # 如果有备货建议，添加到文本
                            if '备货建议' in row and pd.notna(row['备货建议']):
                                if pd.notna(row['建议图标']):
                                    accuracy_text += f" {row['建议图标']}"

                            fig_top_skus.add_annotation(
                                y=row['产品显示'],
                                x=row['求和项:数量（箱）'] * 1.05,
                                text=accuracy_text,
                                showarrow=False,
                                font=dict(
                                    color="black" if row['数量准确率'] > 70 else "red",
                                    size=10
                                )
                            )

                        # 更新布局
                        fig_top_skus.update_layout(
                            title=f"重点SKU及其准确率",
                            xaxis=dict(
                                title="销售量 (箱)",
                                tickformat=",",
                                showexponent="none"
                            ),
                            yaxis=dict(title="产品"),
                            showlegend=False,
                            plot_bgcolor='white',
                            height=max(700, len(national_top_skus) * 40),  # 增加高度
                            margin=dict(l=20, r=40, t=60, b=30)  # 增加边距
                        )

                        # 添加悬停提示
                        hover_template = '<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata[0]:.2f}%'

                        # 如果有备货建议数据，添加到悬停提示
                        if '备货建议' in national_top_skus.columns:
                            hover_template += '<br>建议: %{customdata[1]}'
                            customdata = national_top_skus[['累计占比', '备货建议']].fillna('未知').values
                        else:
                            customdata = national_top_skus[['累计占比']].values

                        fig_top_skus.update_traces(
                            hovertemplate=hover_template + '<extra></extra>',
                            customdata=customdata,
                            selector=dict(type='bar')
                        )

                        # 突出显示准确率低的产品
                        low_accuracy_products = national_top_skus[national_top_skus['数量准确率'] < 70]
                        if not low_accuracy_products.empty:
                            for product in low_accuracy_products['产品显示']:
                                fig_top_skus.add_shape(
                                    type="rect",
                                    y0=list(national_top_skus['产品显示']).index(product) - 0.45,
                                    y1=list(national_top_skus['产品显示']).index(product) + 0.45,
                                    x0=0,
                                    x1=national_top_skus['求和项:数量（箱）'].max() * 1.05,
                                    line=dict(color="#F44336", width=2),
                                    fillcolor="rgba(244, 67, 54, 0.1)"
                                )

                        st.plotly_chart(fig_top_skus, use_container_width=True)

                        # 生成动态解读
                        explanation = """
                                        <b>图表解读：</b> 此图展示了销售量累计占比达到80%的重点SKU及其准确率，条形长度表示销售量，颜色深浅表示准确率(深绿色表示高准确率，红色表示低准确率)。
                                        框线标记的产品准确率低于70%，需要特别关注。
                                        """

                        # 添加具体产品建议
                        if not national_top_skus.empty:
                            top_product = national_top_skus.iloc[0]
                            lowest_accuracy_product = national_top_skus.loc[national_top_skus['数量准确率'].idxmin()]

                            explanation += f"<br><b>产品分析：</b> "
                            explanation += f"{top_product['产品显示']}是销售量最高的产品({format_number(top_product['求和项:数量（箱）'])})，累计占比{top_product['累计占比']:.2f}%，准确率{top_product['数量准确率']:.1f}%；"

                            if lowest_accuracy_product['数量准确率'] < 80:
                                explanation += f"{lowest_accuracy_product['产品显示']}准确率最低，仅为{lowest_accuracy_product['数量准确率']:.1f}%。"

                            # 生成预测建议
                            explanation += "<br><b>行动建议：</b> "

                            low_accuracy = national_top_skus[national_top_skus['数量准确率'] < 70]
                            if not low_accuracy.empty:
                                if len(low_accuracy) <= 3:
                                    for _, product in low_accuracy.iterrows():
                                        explanation += f"重点关注{product['产品显示']}的预测准确性，目前准确率仅为{product['数量准确率']:.1f}%；"
                                else:
                                    explanation += f"共有{len(low_accuracy)}个重点SKU准确率低于70%，需安排专项预测改进计划；"
                            else:
                                explanation += "重点SKU预测准确率良好，建议保持当前预测方法；"

                            # 添加备货建议
                            if '备货建议' in national_top_skus.columns:
                                growth_products = national_top_skus[national_top_skus['销量增长率'] > 10]
                                if not growth_products.empty:
                                    top_growth = growth_products.iloc[0]
                                    explanation += f"增加{top_growth['产品显示']}的备货量{top_growth['调整比例']}%，其增长率达{top_growth['销量增长率']:.1f}%。"

                        add_chart_explanation(explanation)
                    else:
                        st.warning("没有足够的数据来计算全国重点SKU。")

                    # 计算各区域重点SKU对比
                    if regional_top_skus:
                        st.markdown("### 区域重点SKU分析")

                        # 选择显示哪些区域
                        regions_list = list(regional_top_skus.keys())
                        if len(regions_list) > 0:
                            selected_region = st.selectbox(
                                "选择区域查看详情",
                                options=regions_list,
                                key="region_sku_select"
                            )

                            # 显示所选区域的重点SKU
                            if selected_region in regional_top_skus and not regional_top_skus[selected_region].empty:
                                region_top = regional_top_skus[selected_region].copy()

                                # 显示区域和全国重点SKU的重叠分析
                                if not national_top_skus.empty:
                                    region_skus = set(region_top['产品代码'])
                                    national_skus = set(national_top_skus['产品代码'])

                                    # 计算共有和特有SKU
                                    common_skus = region_skus.intersection(national_skus)
                                    region_unique_skus = region_skus - national_skus
                                    national_unique_skus = national_skus - region_skus

                                    # 创建区域和全国重点SKU的名称映射
                                    common_sku_names = [format_product_code(code, product_info, include_name=True) for
                                                        code in
                                                        common_skus]
                                    region_unique_sku_names = [
                                        format_product_code(code, product_info, include_name=True) for
                                        code in region_unique_skus]
                                    national_unique_sku_names = [
                                        format_product_code(code, product_info, include_name=True) for
                                        code in national_unique_skus]

                                    # 完整显示所有SKU，不限制数量
                                    hover_texts = [
                                        f"共有SKU ({len(common_skus)}个):<br>" +
                                        '<br>- '.join(
                                            [''] + [format_product_code(code, product_info, include_name=True) for code
                                                    in
                                                    common_skus]),

                                        f"区域特有SKU ({len(region_unique_skus)}个):<br>" +
                                        '<br>- '.join(
                                            [''] + [format_product_code(code, product_info, include_name=True) for code
                                                    in
                                                    region_unique_skus]),

                                        f"全国重点非区域SKU ({len(national_unique_skus)}个):<br>" +
                                        '<br>- '.join(
                                            [''] + [format_product_code(code, product_info, include_name=True) for code
                                                    in
                                                    national_unique_skus])
                                    ]

                                    # 创建饼图
                                    fig_sku_comparison = go.Figure()

                                    # 添加区域特有SKU占比
                                    fig_sku_comparison.add_trace(go.Pie(
                                        labels=['区域与全国共有SKU', '区域特有SKU', '全国重点但区域非重点SKU'],
                                        values=[len(common_skus), len(region_unique_skus), len(national_unique_skus)],
                                        hole=.3,
                                        marker_colors=['#4CAF50', '#2196F3', '#F44336'],
                                        textinfo='label+percent',
                                        hoverinfo='text',
                                        hovertext=hover_texts,
                                        customdata=[common_sku_names, region_unique_sku_names,
                                                    national_unique_sku_names]
                                    ))

                                    fig_sku_comparison.update_layout(
                                        title=f"{selected_region}区域与全国重点SKU对比",
                                        plot_bgcolor='white',
                                        hoverlabel=dict(
                                            bgcolor="white",
                                            font_size=12,
                                            font_family="Arial"
                                        )
                                    )

                                    st.plotly_chart(fig_sku_comparison, use_container_width=True)

                                    # 修改图表解读，删除SKU详情部分
                                    sku_comparison_explanation = f"""
                                                    <b>图表解读：</b> 此饼图展示了{selected_region}区域重点SKU与全国重点SKU的对比情况。共有SKU(绿色)表示同时是区域和全国重点的产品；区域特有SKU(蓝色)表示只在该区域是重点的产品；全国重点但区域非重点SKU(红色)表示在全国范围内是重点但在该区域不是重点的产品。
                                                    <br><b>建议：</b> 关注区域特有SKU表明区域市场特性；注意全国重点但区域非重点的SKU可能有开发空间。
                                                    """

                                    add_chart_explanation(sku_comparison_explanation)
                            else:
                                st.warning(f"无法显示{selected_region}区域的重点SKU信息。")
                        else:
                            st.info("没有足够的区域数据来进行重点SKU分析。")

# 执行主函数
if __name__ == "__main__":
    main()