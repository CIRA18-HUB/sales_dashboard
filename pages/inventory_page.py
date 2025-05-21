# pages/inventory_page.py - 库存分析页面
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
    setup_page, add_chart_explanation, get_simplified_product_name
)

# 设置页面
setup_page()

# 页面标题
st.markdown('<div class="main-header">📦 库存分析</div>', unsafe_allow_html=True)


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

                # 获取产品简化名称
                simplified_name = get_simplified_product_name(product_code, description)

                # 添加到分析结果
                batch_analysis.append({
                    '产品代码': product_code,
                    '描述': description,
                    '产品简化名称': simplified_name,  # 新增简化名称列
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


# ==================== 4. 图表创建函数 - 调整为与预测与计划.py一致的风格 ====================
def create_inventory_overview_charts(analysis_result):
    """创建库存概览图表 - 使用与预测与计划.py一致的样式"""
    if not analysis_result:
        return None, None

    # 库存健康分布饼图 - 使用一致的颜色配方
    health_dist = analysis_result.get('health_distribution', {})
    if health_dist:
        health_fig = go.Figure(data=[go.Pie(
            labels=list(health_dist.keys()),
            values=list(health_dist.values()),
            marker_colors=[COLORS['danger'], COLORS['success'], COLORS['warning']],
            textposition='inside',
            textinfo='percent+label'
        )])

        health_fig.update_layout(
            title="库存健康状况分布",
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary'])
        )
    else:
        health_fig = None

    # 风险等级分布条形图 - 调整为水平条形图，更加清晰
    risk_dist = analysis_result.get('risk_distribution', {})
    if risk_dist:
        risk_fig = go.Figure(data=[go.Bar(
            y=list(risk_dist.keys()),
            x=list(risk_dist.values()),
            orientation='h',
            marker_color=[INVENTORY_RISK_COLORS.get(level, COLORS['gray']) for level in risk_dist.keys()],
            text=list(risk_dist.values()),
            textposition='outside'
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
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])].head(10)

    if not high_risk_batches.empty:
        age_fig = go.Figure(data=[go.Bar(
            y=high_risk_batches['产品简化名称'],  # 使用简化名称
            x=high_risk_batches['库龄'],
            orientation='h',
            marker_color=[INVENTORY_RISK_COLORS.get(risk, COLORS['gray']) for risk in high_risk_batches['风险程度']],
            text=high_risk_batches['库龄'],
            textposition='outside',
            customdata=high_risk_batches[['风险程度', '批次价值', '建议措施']],
            hovertemplate='<b>%{y}</b><br>库龄: %{x}天<br>风险程度: %{customdata[0]}<br>批次价值: %{customdata[1]:.2f}元<br>建议: %{customdata[2]}<extra></extra>'
        )])

        age_fig.update_layout(
            title="高风险批次库龄分布（Top 10）",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="库龄（天）",
            yaxis_title="产品"
        )
    else:
        age_fig = None

    # 批次价值vs风险程度散点图 - 新的图表类型
    valid_batches = batch_analysis.head(20)

    if not valid_batches.empty:
        scatter_fig = go.Figure()

        # 按风险程度分组绘制散点
        for risk_level in valid_batches['风险程度'].unique():
            risk_data = valid_batches[valid_batches['风险程度'] == risk_level]

            scatter_fig.add_trace(go.Scatter(
                x=risk_data['库龄'],
                y=risk_data['批次价值'],
                mode='markers',
                name=risk_level,
                marker=dict(
                    size=10,
                    color=INVENTORY_RISK_COLORS.get(risk_level, COLORS['gray']),
                    opacity=0.7
                ),
                text=risk_data['产品简化名称'],
                hovertemplate='<b>%{text}</b><br>库龄: %{x}天<br>价值: %{y:.2f}元<br>风险: ' + risk_level + '<extra></extra>'
            ))

        # 添加风险阈值线
        max_age = valid_batches['库龄'].max()
        scatter_fig.add_shape(type="line", x0=90, x1=90, y0=0, y1=valid_batches['批次价值'].max(),
                              line=dict(color=COLORS['danger'], dash="dash", width=2),
                              name="高风险线")

        scatter_fig.update_layout(
            title="批次价值 vs 库龄关系",
            height=500,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="库龄（天）",
            yaxis_title="批次价值（元）",
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

    # 区域责任分布 - 气泡图
    region_analysis = batch_analysis.groupby('责任区域').agg({
        '批次库存': 'sum',
        '批次价值': 'sum',
        '产品代码': 'count'
    }).reset_index()
    region_analysis.columns = ['责任区域', '总库存量', '总价值', '批次数量']

    region_fig = go.Figure(data=[go.Scatter(
        x=region_analysis['总库存量'],
        y=region_analysis['总价值'],
        mode='markers+text',
        marker=dict(
            size=region_analysis['批次数量'],
            sizemode='diameter',
            sizeref=2. * max(region_analysis['批次数量']) / (40. ** 2),
            sizemin=4,
            color=region_analysis['总价值'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="总价值（元）")
        ),
        text=region_analysis['责任区域'],
        textposition="middle center",
        hovertemplate='<b>%{text}</b><br>总库存量: %{x:,.0f}箱<br>总价值: %{y:,.2f}元<br>批次数量: %{marker.size}<extra></extra>'
    )])

    region_fig.update_layout(
        title="各区域责任库存分布",
        height=400,
        plot_bgcolor='white',
        title_font=dict(size=16, color=COLORS['primary']),
        xaxis_title="总库存量（箱）",
        yaxis_title="总价值（元）"
    )

    # 责任人TOP10堆叠柱状图
    person_risk = batch_analysis.groupby(['责任人', '风险程度']).size().unstack(fill_value=0)

    if not person_risk.empty:
        # 选择前10个责任人
        person_totals = person_risk.sum(axis=1).sort_values(ascending=False).head(10)
        top_persons = person_risk.loc[person_totals.index]

        person_fig = go.Figure()

        all_risk_levels = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        for risk in all_risk_levels:
            if risk in top_persons.columns:
                person_fig.add_trace(go.Bar(
                    x=top_persons.index,
                    y=top_persons[risk],
                    name=risk,
                    marker_color=INVENTORY_RISK_COLORS.get(risk, COLORS['gray'])
                ))

        person_fig.update_layout(
            title="责任人风险分布（Top 10）",
            barmode='stack',
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="责任人",
            yaxis_title="批次数量",
            xaxis=dict(tickangle=45)
        )
    else:
        person_fig = None

    return region_fig, person_fig


def create_clearance_prediction_charts(batch_analysis):
    """创建清库预测图表 - 优化图表设计"""
    if batch_analysis is None or batch_analysis.empty:
        return None, None

    # 清库天数分布箱线图
    valid_clearance = batch_analysis[
        (batch_analysis['预计清库天数'] != float('inf')) &
        (batch_analysis['预计清库天数'] <= 365)
        ]

    if not valid_clearance.empty:
        # 按风险等级分组的箱线图
        hist_fig = go.Figure()

        for risk_level in ['极高风险', '高风险', '中风险', '低风险', '极低风险']:
            risk_data = valid_clearance[valid_clearance['风险程度'] == risk_level]
            if not risk_data.empty:
                hist_fig.add_trace(go.Box(
                    y=risk_data['预计清库天数'],
                    name=risk_level,
                    marker_color=INVENTORY_RISK_COLORS.get(risk_level, COLORS['gray']),
                    boxpoints='outliers'
                ))

        # 添加风险阈值线
        hist_fig.add_shape(type="line", x0=-0.5, x1=4.5, y0=90, y1=90,
                           line=dict(color=COLORS['danger'], dash="dash", width=2))

        hist_fig.update_layout(
            title="清库天数分布（按风险等级）",
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            yaxis_title="清库天数",
            xaxis_title="风险等级"
        )
    else:
        hist_fig = None

    # 预测偏差趋势图
    batch_analysis_copy = batch_analysis.copy()
    batch_analysis_copy['预测偏差值'] = batch_analysis_copy['预测偏差'].apply(
        lambda x: float(x.rstrip('%')) / 100 if isinstance(x, str) and '%' in x and x != '异常' else 0
    )

    forecast_analysis = batch_analysis_copy[
        (abs(batch_analysis_copy['预测偏差值']) <= 1.0) &
        (batch_analysis_copy['预计清库天数'] != float('inf'))
        ].head(20)

    if not forecast_analysis.empty:
        forecast_fig = go.Figure()

        # 按风险程度分组的散点图
        for risk_level in forecast_analysis['风险程度'].unique():
            risk_data = forecast_analysis[forecast_analysis['风险程度'] == risk_level]

            forecast_fig.add_trace(go.Scatter(
                x=risk_data['预测偏差值'] * 100,  # 转为百分比
                y=risk_data['预计清库天数'],
                mode='markers',
                name=risk_level,
                marker=dict(
                    size=10,
                    color=INVENTORY_RISK_COLORS.get(risk_level, COLORS['gray']),
                    opacity=0.7
                ),
                text=risk_data['产品简化名称'],
                hovertemplate='<b>%{text}</b><br>预测偏差: %{x:.1f}%<br>清库天数: %{y:.1f}天<br>风险: ' + risk_level + '<extra></extra>'
            ))

        # 添加参考线
        forecast_fig.add_shape(type="line", x0=0, x1=0,
                               y0=0, y1=forecast_analysis['预计清库天数'].max(),
                               line=dict(color=COLORS['gray'], dash="dash", width=1))

        forecast_fig.update_layout(
            title="预测偏差 vs 清库天数",
            height=400,
            plot_bgcolor='white',
            title_font=dict(size=16, color=COLORS['primary']),
            xaxis_title="预测偏差 (%)",
            yaxis_title="清库天数",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
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

    # 创建标签页 - 与预测与计划.py类似的标签页结构
    tabs = st.tabs([
        "📊 总览与关键指标",
        "⚠️ 风险批次分析",
        "👥 责任归属分析",
        "📈 清库预测分析",
        "📋 详细数据表"
    ])

    with tabs[0]:  # 总览与关键指标
        st.markdown('<div class="sub-header">📊 库存关键指标</div>', unsafe_allow_html=True)

        # KPI指标行 - 使用与预测与计划.py一致的样式
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

        # 添加图表解释 - 使用与预测与计划.py一致的样式
        if health_fig or risk_fig:
            add_chart_explanation("""
            <b>图表解读：</b> 左图展示库存健康状况分布，绿色表示健康库存，橙色表示库存不足，红色表示库存过剩。
            右图显示各风险等级的批次数量分布，颜色从蓝色到红色表示风险程度递增。库存过剩批次需要重点关注清库计划。
            <br><b>行动建议：</b> 重点关注红色区域（高风险/库存过剩），制定专项清库方案；橙色区域需要及时补货计划；
            建立库存预警机制，定期监控风险等级变化趋势。
            """)

    with tabs[1]:  # 风险批次分析
        st.markdown('<div class="sub-header">⚠️ 批次风险分析</div>', unsafe_allow_html=True)

        batch_analysis = analysis_result.get('batch_analysis')

        if batch_analysis is not None and not batch_analysis.empty:
            # 风险统计 - 使用与预测与计划.py一致的卡片样式
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
                <b>图表解读：</b> 上图显示高风险批次的库龄分布，颜色深浅表示风险等级，展示了需要优先处理的产品批次。
                下图展示库龄与批次价值的关系，更大的气泡表示更高的价值，90天虚线标记风险阈值。
                <br><b>行动建议：</b> 优先处理库龄长且价值高的批次，避免资金积压；制定分类清库策略：
                极高风险批次需要紧急促销，高风险批次加强营销推广，建立批次轮动机制确保库存新鲜度。
                """)
        else:
            st.info("当前筛选条件下暂无批次数据")

    with tabs[2]:  # 责任归属分析
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
                <b>图表解读：</b> 上图通过气泡大小和颜色展示各区域的库存数量和价值分布，便于识别重点关注区域。
                下图显示主要责任人的风险批次分布，堆叠柱状图清晰展示各风险等级的构成情况。
                <br><b>行动建议：</b> 对库存价值高的区域和责任人加强管理培训，建立清晰的责任制考核体系；
                优化预测准确性培训，提高销售与采购的协调效率；建立跨区域库存调拨机制，优化资源配置。
                """)
        else:
            st.info("当前筛选条件下暂无责任归属数据")

    with tabs[3]:  # 清库预测分析
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
                <b>图表解读：</b> 上图按风险等级展示清库天数分布，箱线图显示了不同风险等级的清库周期差异。
                下图展示预测偏差与清库天数的关系，帮助识别预测准确性对库存周转的影响。
                <br><b>行动建议：</b> 对长期积压批次制定专项清库行动计划，考虑捆绑销售或限时促销；
                改善预测模型准确性，减少偏差导致的库存积压；建立动态定价机制，根据库龄调整价格策略。
                """)
        else:
            st.info("当前筛选条件下暂无清库预测数据")

    with tabs[4]:  # 详细数据表
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
                # 格式化显示列 - 使用产品简化名称
                display_columns = [
                    '产品代码', '产品简化名称', '批次日期', '批次库存', '库龄', '批次价值',
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
                            help="批次风险等级评估，基于库龄、清库天数、销量波动等因素综合计算"
                        ),
                        "批次价值": st.column_config.TextColumn(
                            "批次价值",
                            help="批次总价值（数量×单价），反映资金占用情况"
                        ),
                        "建议措施": st.column_config.TextColumn(
                            "建议措施",
                            help="针对该批次风险等级的具体处理建议"
                        ),
                        "产品简化名称": st.column_config.TextColumn(
                            "产品简化名称",
                            help="产品的简化显示名称，便于快速识别"
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
                **当前筛选结果概况：**
                - 显示 {len(display_data)} 个批次，总价值 {format_currency(total_value)}
                - 极高风险批次 {extreme_high_count} 个，高风险批次 {high_count} 个
                - 平均库龄 {avg_age:.1f} 天
                - 主要积压原因：{display_data['积压原因'].mode().iloc[0] if not display_data['积压原因'].mode().empty else '混合因素'}

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