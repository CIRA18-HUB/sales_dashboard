# pages/inventory_page.py - 库存分析页面（移除预测功能）
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math
import warnings

warnings.filterwarnings('ignore')

# 从config导入必要的函数和配置
from config import (
    COLORS, INVENTORY_RISK_COLORS, INVENTORY_CONFIG, load_inventory_data,
    format_currency, format_percentage, format_number, format_days,
    calculate_inventory_risk_level, calculate_risk_percentage,
    setup_page, add_chart_explanation
)

# 设置页面
setup_page()

# 页面标题
st.markdown('<div class="main-header">📦 库存分析</div>', unsafe_allow_html=True)

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


# ==================== 5. 主页面逻辑 ====================
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

    # 创建标签页 - 移除预测相关标签
    tabs = st.tabs([
        "📊 库存概览",
        "⚠️ 批次风险",
        "👥 责任归属",
        "📈 清库预测",
        "📋 详细分析"
    ])

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


# 执行主函数
if __name__ == "__main__":
    main()