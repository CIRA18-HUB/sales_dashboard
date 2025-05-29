# pages/预测库存分析.py - 智能库存预警分析系统
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time


# 在 import 部分后面新增这个类
# 在 import 部分后面新增这个完整的类
class BatchLevelInventoryAnalyzer:
    """批次级别库存分析器 - 完整移植自积压超详细.py"""

    def __init__(self):
        # 风险参数设置
        self.high_stock_days = 90
        self.medium_stock_days = 60
        self.low_stock_days = 30
        self.high_volatility_threshold = 1.0
        self.medium_volatility_threshold = 0.8
        self.high_forecast_bias_threshold = 0.3
        self.medium_forecast_bias_threshold = 0.15
        self.high_clearance_days = 90
        self.medium_clearance_days = 60
        self.low_clearance_days = 30
        self.min_daily_sales = 0.5
        self.min_seasonal_index = 0.3

        # 默认区域和责任人
        self.default_regions = ['东', '南', '西', '北', '中']
        self.default_region = '东'
        self.default_person = '系统管理员'

        # 责任归属分析权重参数
        self.forecast_accuracy_weight = 0.25
        self.recent_sales_weight = 0.30
        self.ordering_history_weight = 0.25
        self.market_performance_weight = 0.20

    def calculate_risk_percentage(self, days_to_clear, batch_age, target_days):
        """计算风险百分比"""
        import math

        if batch_age >= target_days:
            return 100.0

        if days_to_clear == float('inf'):
            return 100.0

        if days_to_clear >= 3 * target_days:
            return 100.0

        # 计算基于清库天数的风险
        clearance_ratio = days_to_clear / target_days
        clearance_risk = 100 / (1 + math.exp(-4 * (clearance_ratio - 1)))

        # 计算基于库龄的风险
        age_risk = 100 * batch_age / target_days

        # 组合风险
        combined_risk = 0.8 * max(clearance_risk, age_risk) + 0.2 * min(clearance_risk, age_risk)

        if days_to_clear > target_days:
            combined_risk = max(combined_risk, 80)

        if days_to_clear >= 2 * target_days:
            combined_risk = max(combined_risk, 90)

        if batch_age >= 0.75 * target_days:
            combined_risk = max(combined_risk, 75)

        return min(100, round(combined_risk, 1))

    def calculate_forecast_bias(self, forecast_quantity, actual_sales):
        """计算预测偏差"""
        import math

        if actual_sales == 0 and forecast_quantity == 0:
            return 0.0
        elif actual_sales == 0:
            return min(math.sqrt(forecast_quantity) / max(forecast_quantity, 1), 1.0)
        elif forecast_quantity == 0:
            return -min(math.sqrt(actual_sales) / max(actual_sales, 1), 1.0)
        else:
            if forecast_quantity > actual_sales:
                normalized_error = (forecast_quantity - actual_sales) / actual_sales
                return min(math.tanh(normalized_error), 1.0)
            else:
                normalized_error = (actual_sales - forecast_quantity) / forecast_quantity
                return -min(math.tanh(normalized_error), 1.0)

    def analyze_responsibility_collaborative(self, product_code, batch_date, product_sales_metrics,
                                             forecast_info, orders_history, batch_qty=0,
                                             sales_person_region_mapping=None):
        """改进的责任归属分析 - 完整移植"""
        today = datetime.now().date()
        batch_date = batch_date.date() if hasattr(batch_date, 'date') else batch_date

        # 默认责任映射
        default_mapping = {"region": self.default_region, "person": self.default_person}

        if sales_person_region_mapping is None:
            sales_person_region_mapping = {}

        # 1. 获取批次生产前后的预测记录
        forecast_start_date = batch_date - timedelta(days=90)
        forecast_end_date = batch_date + timedelta(days=30)

        # 2. 初始化责任评分系统
        person_scores = {}
        region_scores = {}
        responsibility_details = {}

        # 3. 预测与实际销售差异分析 (60%)
        forecast_sales_discrepancy_weight = 0.60
        forecast_responsibility_details = {}

        # 模拟预测数据（实际应用中从forecast_info获取）
        if forecast_info and 'person_forecast' in forecast_info:
            person_forecast_totals = forecast_info['person_forecast']
            total_forecast = sum(person_forecast_totals.values())

            # 模拟实际销售数据
            person_sales = {}
            for person in person_forecast_totals.keys():
                # 基于历史数据模拟实际销售
                forecast_qty = person_forecast_totals[person]
                # 模拟履行率在20%-80%之间
                fulfillment_rate = np.random.uniform(0.2, 0.8)
                actual_sales = forecast_qty * fulfillment_rate
                person_sales[person] = actual_sales

            overall_fulfillment_rate = sum(person_sales.values()) / total_forecast if total_forecast > 0 else 1.0

            responsibility_details["overall_analysis"] = {
                "total_forecast": total_forecast,
                "total_sales": sum(person_sales.values()),
                "fulfillment_rate": overall_fulfillment_rate
            }

            if overall_fulfillment_rate < 0.8:
                for person, forecast_qty in person_forecast_totals.items():
                    forecast_proportion = forecast_qty / total_forecast
                    actual_sales = person_sales.get(person, 0)
                    fulfillment_rate = actual_sales / forecast_qty if forecast_qty > 0 else 1.0

                    base_score = (1 - fulfillment_rate) * forecast_proportion

                    if forecast_proportion > 0.5:
                        adjusted_score = base_score * (2.0 if fulfillment_rate < 0.6 else 1.5)
                    elif forecast_proportion > 0.2:
                        adjusted_score = base_score * (1.5 if fulfillment_rate < 0.6 else 1.2)
                    else:
                        adjusted_score = base_score * 1.0

                    final_score = adjusted_score * forecast_sales_discrepancy_weight
                    person_scores[person] = person_scores.get(person, 0) + final_score

                    person_region = sales_person_region_mapping.get(person, default_mapping["region"])
                    region_scores[person_region] = region_scores.get(person_region, 0) + (final_score * 0.8)

                    forecast_responsibility_details[person] = {
                        "forecast_quantity": forecast_qty,
                        "forecast_proportion": forecast_proportion,
                        "actual_sales": actual_sales,
                        "fulfillment_rate": fulfillment_rate,
                        "responsibility_score": final_score
                    }

        responsibility_details["forecast_responsibility"] = forecast_responsibility_details

        # 4. 库存责任分配机制
        person_allocations = {}
        if forecast_responsibility_details and batch_qty > 0:
            forecast_deltas = {}
            total_delta = 0

            for person, details in forecast_responsibility_details.items():
                forecast_qty = details.get("forecast_quantity", 0)
                actual_sales = details.get("actual_sales", 0)
                delta = max(0, forecast_qty - actual_sales)

                if delta > 0:
                    forecast_deltas[person] = delta
                    total_delta += delta

            if total_delta > 0:
                allocated_total = 0
                for person, delta in forecast_deltas.items():
                    proportion = delta / total_delta
                    allocation = int(batch_qty * proportion)
                    allocation = max(1, allocation)
                    allocation = min(allocation, batch_qty - allocated_total)

                    person_allocations[person] = allocation
                    allocated_total += allocation

                remaining_qty = batch_qty - allocated_total
                if remaining_qty > 0 and forecast_deltas:
                    sorted_forecast_persons = sorted(forecast_deltas.items(), key=lambda x: x[1], reverse=True)
                    person_allocations[sorted_forecast_persons[0][0]] += remaining_qty
            else:
                person_allocations[default_mapping["person"]] = batch_qty
        else:
            person_allocations[default_mapping["person"]] = batch_qty

        # 5. 确定责任人
        if person_allocations:
            responsible_person = max(person_allocations.items(), key=lambda x: x[1])[0]
            if responsible_person in sales_person_region_mapping:
                responsible_region = sales_person_region_mapping[responsible_person]
            else:
                responsible_region = default_mapping["region"]
        else:
            responsible_person = default_mapping["person"]
            responsible_region = default_mapping["region"]

        # 如果是系统管理员，区域为空
        if responsible_person == self.default_person:
            responsible_region = ""

        responsible_persons = list(person_allocations.keys())
        secondary_persons = [p for p in responsible_persons if p != responsible_person]

        # 构建责任分析详情
        responsibility_analysis = {
            "responsible_person": responsible_person,
            "responsible_region": responsible_region,
            "responsible_persons": responsible_persons,
            "secondary_persons": secondary_persons,
            "person_scores": person_scores,
            "region_scores": region_scores,
            "responsibility_details": responsibility_details,
            "quantity_allocation": {
                "batch_qty": batch_qty,
                "person_allocations": person_allocations,
                "allocation_logic": "责任库存严格基于预测未兑现量分配"
            },
            "batch_info": {
                "batch_date": batch_date,
                "batch_age": (today - batch_date).days,
                "batch_qty": batch_qty
            }
        }

        return (responsible_region, responsible_person, responsibility_analysis)

    def generate_responsibility_summary_collaborative(self, responsibility_analysis):
        """生成责任分析摘要 - 完整移植"""
        if not responsibility_analysis:
            return "无法确定责任"

        responsible_person = responsibility_analysis.get("responsible_person", self.default_person)
        secondary_persons = responsibility_analysis.get("secondary_persons", [])
        responsibility_details = responsibility_analysis.get("responsibility_details", {})

        batch_info = responsibility_analysis.get("batch_info", {})
        batch_qty = batch_info.get("batch_qty", 0)

        quantity_allocation = responsibility_analysis.get("quantity_allocation", {})
        person_allocations = quantity_allocation.get("person_allocations", {})

        forecast_responsibility = responsibility_details.get("forecast_responsibility", {})

        # 构建主要责任人的责任原因
        main_person_reasons = []

        if responsible_person in forecast_responsibility:
            person_forecast = forecast_responsibility[responsible_person]
            forecast_qty = person_forecast.get("forecast_quantity", 0)
            actual_sales = person_forecast.get("actual_sales", 0)
            fulfillment = person_forecast.get("fulfillment_rate", 1.0) * 100
            unfulfilled = max(0, forecast_qty - actual_sales)

            if forecast_qty > 0:
                main_person_reasons.append(
                    f"预测{forecast_qty:.0f}件但仅销售{actual_sales:.0f}件(履行率{fulfillment:.0f}%)")

            if unfulfilled > 0:
                main_person_reasons.append(f"未兑现预测{unfulfilled:.0f}件")

        if not main_person_reasons:
            main_person_reasons.append("综合预测与销售因素")

        # 构建其他责任人的摘要
        other_persons_data = []
        for person in secondary_persons:
            if person != responsible_person:
                allocated_qty = person_allocations.get(person, 0)
                reason = ""

                if person in forecast_responsibility:
                    forecast_info = forecast_responsibility[person]
                    forecast_qty = forecast_info.get("forecast_quantity", 0)
                    actual_sales = forecast_info.get("actual_sales", 0)
                    unfulfilled = max(0, forecast_qty - actual_sales)

                    if unfulfilled > 0:
                        reason = f"未兑现预测{unfulfilled:.0f}件"
                    else:
                        reason = "责任共担"
                else:
                    reason = "责任共担"

                other_persons_data.append((person, reason, allocated_qty))

        # 按库存数量降序排序
        other_persons_data.sort(key=lambda x: x[2], reverse=True)
        other_persons_summary = [f"{person}({reason}，承担{qty}件)" for person, reason, qty in other_persons_data]

        # 生成最终摘要
        main_reason = "、".join(main_person_reasons)

        if responsible_person in person_allocations and person_allocations[responsible_person] > 0:
            main_responsibility_qty = person_allocations[responsible_person]
            main_person_with_qty = f"{responsible_person}主要责任({main_reason}，承担{main_responsibility_qty}件)"
        else:
            main_person_with_qty = f"{responsible_person}主要责任({main_reason}，承担0件)"

        if other_persons_summary:
            others_text = "，".join(other_persons_summary)
            summary = f"{main_person_with_qty}，共同责任：{others_text}"
        else:
            summary = main_person_with_qty

        return summary

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="智能库存预警系统",
    page_icon="📦",
    layout="wide"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 统一的增强CSS样式 - 添加高级动画和修复文字截断
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 全局字体和背景 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* 添加浮动粒子背景动画 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    /* 主容器背景 */
    .main .block-container {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 页面标题样式 */
    .page-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white;
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.5s ease-out;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }

    .page-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    @keyframes fadeInScale {
        from { 
            opacity: 0; 
            transform: translateY(-50px) scale(0.8); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }

    .page-title {
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        line-height: 1.1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .page-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* 统一的卡片容器样式 */
    .metric-card, .content-container, .chart-container, .insight-box {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 25px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03);
        border: 1px solid rgba(255,255,255,0.3);
        animation: slideUpStagger 1s ease-out;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }

    /* Plotly 图表圆角样式 */
    .js-plotly-plot {
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
    }

    /* Plotly 图表容器圆角 */
    [data-testid="stPlotlyChart"] {
        border-radius: 20px !important;
        overflow: hidden !important;
    }

    /* Plotly iframe 圆角 */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 20px !important;
        overflow: hidden !important;
    }

    [data-testid="stPlotlyChart"] iframe {
        border-radius: 20px !important;
    }

    /* 指标卡片增强样式 - 修复文字截断 */
    .metric-card {
        text-align: center;
        height: 100%;
        padding: 2.5rem 2rem;
        position: relative;
        overflow: visible !important; /* 修复文字截断 */
        perspective: 1000px;
        animation: cardEntrance 1s ease-out;
        transform-style: preserve-3d;
    }

    /* 3D翻转效果 */
    .metric-card-inner {
        width: 100%;
        height: 100%;
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }

    .metric-card:hover .metric-card-inner {
        transform: rotateY(5deg) rotateX(-5deg);
    }

    /* 波纹效果 */
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.2) 0%, transparent 70%);
        transform: translate(-50%, -50%) scale(0);
        animation: ripple 3s infinite;
        opacity: 0;
        pointer-events: none;
    }

    @keyframes ripple {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        100% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0;
        }
    }

    @keyframes cardEntrance {
        0% {
            opacity: 0;
            transform: translateY(50px) rotateX(-30deg);
        }
        50% {
            opacity: 0.5;
            transform: translateY(25px) rotateX(-15deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) rotateX(0);
        }
    }

    .metric-card:hover, .content-container:hover, .chart-container:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.12);
    }

    @keyframes slideUpStagger {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }

    /* 数值样式 - 修复截断并添加滚动动画 */
    .metric-value {
        font-size: 2.8rem !important; /* 略微减小以防止截断 */
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: visible !important;
        display: inline-block;
        min-width: 100%;
        animation: numberCount 2s ease-out;
    }

    /* 数字滚动动画 */
    @keyframes numberCount {
        0% {
            opacity: 0;
            transform: translateY(50px) scale(0.5);
            filter: blur(10px);
        }
        50% {
            opacity: 0.5;
            filter: blur(5px);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }

    .metric-label {
        color: #374151 !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        animation: labelFade 1.5s ease-out 0.5s both;
    }

    @keyframes labelFade {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .metric-description {
        color: #6b7280 !important;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        font-weight: 500;
        font-style: italic;
        animation: labelFade 1.5s ease-out 0.7s both;
    }

    /* 图表标题样式 */
    .chart-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #333 !important;
        margin-bottom: 1.5rem;
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 洞察框样式 */
    .insight-box {
        border-left: 4px solid #667eea;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .insight-title {
        font-weight: 700;
        color: #333 !important;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }

    .insight-content {
        color: #666 !important;
        line-height: 1.6;
        font-size: 1rem;
    }

    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(248, 250, 252, 0.95) !important;
        padding: 1rem;
        border-radius: 20px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 35px;
        background: rgba(255,255,255,0.95) !important;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        color: #333 !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }

    /* 特殊风险等级颜色 */
    .risk-extreme { border-left-color: #8B0000 !important; }
    .risk-high { border-left-color: #FF0000 !important; }
    .risk-medium { border-left-color: #FFA500 !important; }
    .risk-low { border-left-color: #90EE90 !important; }
    .risk-minimal { border-left-color: #006400 !important; }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value { font-size: 2.2rem !important; }
        .metric-card { padding: 2rem 1.5rem; }
        .page-header { padding: 2rem 1rem; }
        .page-title { font-size: 2.5rem; }
    }

    /* 高级表格样式 - 增强版 */
    .advanced-table {
        background: linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.98)) !important;
        border-radius: 30px !important;
        overflow: visible !important;
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.12),
            0 15px 30px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.04),
            inset 0 2px 4px rgba(255,255,255,0.9) !important;
        border: 2px solid transparent !important;
        background-image: 
            linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.98)),
            linear-gradient(135deg, #667eea, #764ba2) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        margin: 2rem 0 !important;
        position: relative !important;
        animation: tableContainerEntrance 1.5s ease-out !important;
    }

    @keyframes tableContainerEntrance {
        from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .stDataFrame > div {
        border-radius: 25px !important;
        overflow: hidden !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 表格头部样式 - 增强版 */
    .stDataFrame thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        padding: 2rem 1.2rem !important;
        text-align: center !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }

    .stDataFrame thead th::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: tableHeaderShimmer 2s ease-in-out infinite;
    }

    .stDataFrame thead th::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
        animation: tableHeaderUnderline 3s ease-in-out infinite;
    }

    @keyframes tableHeaderShimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    @keyframes tableHeaderUnderline {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
    }

    /* 表格行样式 - 增强版 */
    .stDataFrame tbody tr {
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border-bottom: 1px solid rgba(0,0,0,0.03) !important;
        position: relative !important;
    }

    .stDataFrame tbody tr:nth-child(even) {
        background: rgba(102, 126, 234, 0.02) !important;
    }

    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.05)) !important;
        transform: scale(1.02) translateX(5px) !important;
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.15),
            -5px 0 20px rgba(102, 126, 234, 0.1) !important;
        z-index: 10 !important;
    }

    .stDataFrame tbody td {
        padding: 1.5rem 1.2rem !important;
        border: none !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        vertical-align: middle !important;
        position: relative !important;
    }

    /* 风险等级样式 - 极高风险 (超级增强版) */
    .stDataFrame tbody tr:has(td:contains("极高风险")) {
        background: linear-gradient(90deg, 
            rgba(139, 0, 0, 0.15) 0%,
            rgba(139, 0, 0, 0.08) 50%,
            rgba(139, 0, 0, 0.15) 100%) !important;
        border-left: 8px solid #8B0000 !important;
        animation: 
            extremeRiskPulse 1.5s ease-in-out infinite,
            extremeRiskWave 3s linear infinite,
            extremeRiskShake 10s ease-in-out infinite !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stDataFrame tbody tr:has(td:contains("极高风险"))::before {
        content: '⚠️';
        position: absolute;
        left: -30px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        animation: warningBlink 1s ease-in-out infinite;
    }

    .stDataFrame tbody tr:has(td:contains("极高风险"))::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(139, 0, 0, 0.1), transparent);
        animation: riskScanline 2s linear infinite;
        pointer-events: none;
    }

    .stDataFrame tbody tr:has(td:contains("极高风险")):hover {
        background: linear-gradient(90deg, 
            rgba(139, 0, 0, 0.25) 0%,
            rgba(139, 0, 0, 0.15) 50%,
            rgba(139, 0, 0, 0.25) 100%) !important;
        transform: scale(1.03) translateX(15px) !important;
        box-shadow: 
            0 20px 50px rgba(139, 0, 0, 0.4),
            -10px 0 30px rgba(139, 0, 0, 0.3),
            inset 0 0 30px rgba(139, 0, 0, 0.1) !important;
        border-left-width: 12px !important;
    }

    /* 风险等级样式 - 高风险 (增强版) */
    .stDataFrame tbody tr:has(td:contains("高风险")):not(:has(td:contains("极高风险"))) {
        background: linear-gradient(90deg, 
            rgba(255, 0, 0, 0.12) 0%,
            rgba(255, 0, 0, 0.06) 50%,
            rgba(255, 0, 0, 0.12) 100%) !important;
        border-left: 6px solid #FF0000 !important;
        animation: 
            highRiskGlow 2s ease-in-out infinite,
            highRiskBreath 4s ease-in-out infinite !important;
        position: relative !important;
    }

    .stDataFrame tbody tr:has(td:contains("高风险")):not(:has(td:contains("极高风险")))::before {
        content: '⚡';
        position: absolute;
        left: -25px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.2rem;
        animation: warningFloat 2s ease-in-out infinite;
    }

    .stDataFrame tbody tr:has(td:contains("高风险")):not(:has(td:contains("极高风险"))):hover {
        background: linear-gradient(90deg, 
            rgba(255, 0, 0, 0.2) 0%,
            rgba(255, 0, 0, 0.12) 50%,
            rgba(255, 0, 0, 0.2) 100%) !important;
        transform: scale(1.025) translateX(12px) !important;
        box-shadow: 
            0 15px 40px rgba(255, 0, 0, 0.35),
            -8px 0 25px rgba(255, 0, 0, 0.25),
            inset 0 0 20px rgba(255, 0, 0, 0.08) !important;
        border-left-width: 10px !important;
    }

    /* 风险等级样式 - 中风险 */
    .stDataFrame tbody tr:has(td:contains("中风险")) {
        background: linear-gradient(90deg, rgba(255, 165, 0, 0.08), rgba(255, 165, 0, 0.04)) !important;
        border-left: 4px solid #FFA500 !important;
        animation: mediumRiskPulse 3s ease-in-out infinite !important;
    }

    .stDataFrame tbody tr:has(td:contains("中风险")):hover {
        background: linear-gradient(90deg, rgba(255, 165, 0, 0.15), rgba(255, 165, 0, 0.08)) !important;
        transform: scale(1.015) translateX(8px) !important;
        box-shadow: 0 10px 30px rgba(255, 165, 0, 0.2) !important;
    }

    /* 风险等级样式 - 低风险 */
    .stDataFrame tbody tr:has(td:contains("低风险")) {
        background: linear-gradient(90deg, rgba(144, 238, 144, 0.06), rgba(144, 238, 144, 0.03)) !important;
        border-left: 3px solid #90EE90 !important;
    }

    /* 风险等级样式 - 极低风险 */
    .stDataFrame tbody tr:has(td:contains("极低风险")) {
        background: linear-gradient(90deg, rgba(0, 100, 0, 0.06), rgba(0, 100, 0, 0.03)) !important;
        border-left: 3px solid #006400 !important;
    }

    /* 动画效果定义 */
    @keyframes extremeRiskPulse {
        0%, 100% {
            box-shadow: 
                0 0 0 0 rgba(139, 0, 0, 0.8),
                0 10px 25px rgba(139, 0, 0, 0.3),
                inset 0 0 20px rgba(139, 0, 0, 0.05);
        }
        50% {
            box-shadow: 
                0 0 0 15px rgba(139, 0, 0, 0),
                0 15px 40px rgba(139, 0, 0, 0.5),
                inset 0 0 30px rgba(139, 0, 0, 0.1);
        }
    }

    @keyframes extremeRiskWave {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes extremeRiskShake {
        0%, 90%, 100% { transform: translateX(0); }
        91%, 93%, 95%, 97%, 99% { transform: translateX(-2px); }
        92%, 94%, 96%, 98% { transform: translateX(2px); }
    }

    @keyframes highRiskGlow {
        0%, 100% {
            box-shadow: 
                0 0 10px rgba(255, 0, 0, 0.4),
                0 5px 15px rgba(255, 0, 0, 0.2);
        }
        50% {
            box-shadow: 
                0 0 25px rgba(255, 0, 0, 0.6),
                0 10px 30px rgba(255, 0, 0, 0.3);
        }
    }

    @keyframes highRiskBreath {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.005); }
    }

    @keyframes mediumRiskPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.95; }
    }

    @keyframes warningBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    @keyframes warningFloat {
        0%, 100% { transform: translateY(-50%); }
        50% { transform: translateY(-60%); }
    }

    @keyframes riskScanline {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* 风险等级单元格特殊样式 - 超级增强版 */
    [data-testid="stDataFrameResizable"] td:contains("极高风险") {
        background: linear-gradient(135deg, #8B0000 0%, #660000 50%, #4B0000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        padding: 1rem 1.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        animation: extremeRiskTextPulse 1s ease-in-out infinite !important;
        box-shadow: 
            0 4px 10px rgba(139, 0, 0, 0.4),
            inset 0 2px 4px rgba(255,255,255,0.2),
            inset 0 -2px 4px rgba(0,0,0,0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    [data-testid="stDataFrameResizable"] td:contains("高风险") {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 50%, #990000 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.4rem !important;
        text-shadow: 0 2px 3px rgba(0,0,0,0.3) !important;
        animation: highRiskTextGlow 2s ease-in-out infinite !important;
        box-shadow: 
            0 3px 8px rgba(255, 0, 0, 0.3),
            inset 0 1px 3px rgba(255,255,255,0.2) !important;
    }

    @keyframes extremeRiskTextPulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 
                0 4px 10px rgba(139, 0, 0, 0.4),
                inset 0 2px 4px rgba(255,255,255,0.2),
                inset 0 -2px 4px rgba(0,0,0,0.2);
        }
        50% { 
            transform: scale(1.05);
            box-shadow: 
                0 6px 20px rgba(139, 0, 0, 0.6),
                inset 0 2px 4px rgba(255,255,255,0.3),
                inset 0 -2px 4px rgba(0,0,0,0.3);
        }
    }

    @keyframes highRiskTextGlow {
        0%, 100% { 
            filter: brightness(1) saturate(1); 
        }
        50% { 
            filter: brightness(1.2) saturate(1.2); 
        }
    }

    /* 表格行号样式 - 增强版 */
    .stDataFrame tbody tr td:first-child {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(102, 126, 234, 0.08)) !important;
        font-weight: 800 !important;
        color: #667eea !important;
        text-shadow: 0 1px 2px rgba(102, 126, 234, 0.2) !important;
        border-right: 2px solid rgba(102, 126, 234, 0.2) !important;
    }

    /* 数值列特殊格式 - 增强版 */
    .stDataFrame tbody td:contains("¥") {
        font-weight: 800 !important;
        color: #228B22 !important;
        text-shadow: 0 1px 2px rgba(34, 139, 34, 0.2) !important;
        font-size: 1.05rem !important;
    }

    .stDataFrame tbody td:contains("天") {
        font-weight: 700 !important;
        color: #667eea !important;
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }

    /* 表格容器增强 */
    .stDataFrame {
        background: transparent !important;
        border: none !important;
        position: relative !important;
    }

    .stDataFrame > div > div {
        border-radius: 25px !important;
        overflow: hidden !important;
        position: relative !important;
    }

    /* 滚动条美化 - 增强版 */
    .stDataFrame ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .stDataFrame ::-webkit-scrollbar-track {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
        border-radius: 10px;
        margin: 10px;
    }

    .stDataFrame ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        box-shadow: inset 0 0 6px rgba(0,0,0,0.1);
    }

    .stDataFrame ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6b419e);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
    }

    /* 特殊效果：聚光灯效果 */
    .stDataFrame tbody tr:has(td:contains("极高风险")):hover::after {
        animation: riskSpotlight 1s ease-in-out;
    }

    @keyframes riskSpotlight {
        0% {
            background: radial-gradient(circle at 50% 50%, rgba(139, 0, 0, 0.3) 0%, transparent 50%);
            opacity: 0;
        }
        50% {
            opacity: 1;
        }
        100% {
            background: radial-gradient(circle at 50% 50%, rgba(139, 0, 0, 0) 0%, transparent 80%);
            opacity: 0;
        }
    }

    /* 添加渐进式加载动画 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }

    /* 加载动画初始状态 */
    .metric-card {
        opacity: 0;
        animation: cardLoadIn 0.8s ease-out forwards;
    }

    @keyframes cardLoadIn {
        0% {
            opacity: 0;
            transform: translateY(50px) scale(0.8);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
</style>
""", unsafe_allow_html=True)

# 配色方案
COLOR_SCHEME = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'risk_extreme': '#8B0000',  # 深红色
    'risk_high': '#FF0000',  # 红色
    'risk_medium': '#FFA500',  # 橙色
    'risk_low': '#90EE90',  # 浅绿色
    'risk_minimal': '#006400',  # 深绿色
    'chart_colors': ['#667eea', '#ff6b9d', '#c44569', '#ffc75f', '#f8b500', '#845ec2', '#4e8397', '#00c9a7']
}


def create_integrated_risk_analysis_optimized(processed_inventory):
    """创建优化的整合风险分析图表 - 修复箱数格式和悬停遮挡问题"""
    try:
        if processed_inventory.empty:
            fig = go.Figure()
            fig.update_layout(
                title="风险分析 (无数据)",
                annotations=[
                    dict(
                        text="暂无库存数据",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        xanchor='center', yanchor='middle',
                        font=dict(size=20, color="gray")
                    )
                ]
            )
            return fig

        # 风险分布数据
        risk_counts = processed_inventory['风险等级'].value_counts()
        risk_value = processed_inventory.groupby('风险等级')['批次价值'].sum() / 1000000

        # 创建颜色映射字典
        risk_color_map = {
            '极高风险': '#8B0000',
            '高风险': '#FF0000',
            '中风险': '#FFA500',
            '低风险': '#90EE90',
            '极低风险': '#006400'
        }

        # 按风险等级顺序排列
        risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        ordered_risks = [risk for risk in risk_order if risk in risk_counts.index]
        colors = [risk_color_map[risk] for risk in ordered_risks]

        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("风险等级分布", "各风险等级价值分布", "库存批次库龄分布", "高风险批次优先级分析"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )

        # 为饼图准备详细信息
        risk_details = {}
        for risk in ordered_risks:
            risk_products = processed_inventory[processed_inventory['风险等级'] == risk]
            risk_details[risk] = {
                'count': len(risk_products),
                'value': risk_products['批次价值'].sum() / 1000000,
                'avg_stock': int(risk_products['数量'].mean()) if '数量' in processed_inventory.columns else int(
                    risk_products['批次库存'].mean()) if '批次库存' in processed_inventory.columns else 0,
                'products': risk_products.groupby('产品名称').agg({
                    '数量': 'count' if '数量' in processed_inventory.columns else lambda x: 0,
                    '批次价值': 'sum'
                }).head(5).to_dict()
            }

        # 1. 风险等级分布饼图 - 修复悬停格式
        fig.add_trace(go.Pie(
            labels=ordered_risks,
            values=[risk_counts[risk] for risk in ordered_risks],
            hole=.4,
            marker_colors=colors,
            textinfo='label+percent',
            name="风险分布",
            customdata=[[risk_details[risk]['count'],
                         risk_details[risk]['value'],
                         risk_details[risk]['avg_stock']] for risk in ordered_risks],
            hovertemplate="<b>%{label}</b><br>" +
                          "批次数: %{value}个<br>" +
                          "占比: %{percent}<br>" +
                          "总价值: ¥%{customdata[1]:.1f}M<br>" +
                          "平均库存: %{customdata[2]:,}箱<br>" +  # 整数显示
                          "<extra></extra>"
        ), row=1, col=1)

        # 2. 风险等级价值分布 - 修复悬停格式
        fig.add_trace(go.Bar(
            x=ordered_risks,
            y=[risk_value.get(risk, 0) for risk in ordered_risks],
            marker_color=colors,
            name="价值分布",
            text=[f'¥{risk_value.get(risk, 0):.1f}M' for risk in ordered_risks],
            textposition='auto',
            customdata=[[risk_counts.get(risk, 0),
                         int(processed_inventory[processed_inventory['风险等级'] == risk][
                                 '数量'].sum()) if '数量' in processed_inventory.columns else int(
                             processed_inventory[processed_inventory['风险等级'] == risk][
                                 '批次库存'].sum()) if '批次库存' in processed_inventory.columns else 0] for risk in
                        ordered_risks],
            hovertemplate="<b>%{x}</b><br>" +
                          "总价值: ¥%{y:.1f}M<br>" +
                          "批次数: %{customdata[0]}个<br>" +
                          "总库存: %{customdata[1]:,}箱<br>" +  # 整数显示
                          "<extra></extra>"
        ), row=1, col=2)

        # 3. 库龄分布直方图 - 修复悬停格式
        stock_col = '数量' if '数量' in processed_inventory.columns else '批次库存'
        fig.add_trace(go.Histogram(
            x=processed_inventory['库龄'],
            nbinsx=20,
            marker_color=COLOR_SCHEME['primary'],
            opacity=0.7,
            name="库龄分布",
            customdata=processed_inventory[[stock_col]],
            hovertemplate="库龄: %{x}天<br>" +
                          "批次数: %{y}个<br>" +
                          "<extra></extra>"
        ), row=2, col=1)

        # 4. 高风险批次分析 - 修复悬停格式
        high_risk_data = processed_inventory[
            processed_inventory['风险等级'].isin(['极高风险', '高风险'])
        ].head(15)

        if not high_risk_data.empty:
            # 计算建议处理优先级
            high_risk_data = high_risk_data.copy()
            high_risk_data['优先级分数'] = (
                    high_risk_data['库龄'] * 0.4 +
                    high_risk_data['批次价值'] / high_risk_data['批次价值'].max() * 100 * 0.6
            )

            stock_col = '数量' if '数量' in high_risk_data.columns else '批次库存'

            fig.add_trace(go.Scatter(
                x=high_risk_data['库龄'],
                y=high_risk_data['批次价值'],
                mode='markers',
                marker=dict(
                    size=np.minimum(high_risk_data[stock_col] / 20, 50),
                    color=high_risk_data['风险等级'].map({
                        '极高风险': COLOR_SCHEME['risk_extreme'],
                        '高风险': COLOR_SCHEME['risk_high']
                    }),
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=high_risk_data['产品名称'],
                customdata=np.column_stack((
                    high_risk_data['产品名称'],
                    high_risk_data['生产批号'] if '生产批号' in high_risk_data.columns else ['未知'] * len(
                        high_risk_data),
                    high_risk_data[stock_col].astype(int),  # 转换为整数
                    high_risk_data['库龄'],
                    high_risk_data['风险等级'],
                    high_risk_data['批次价值'],
                    high_risk_data['预期损失'] if '预期损失' in high_risk_data.columns else [0] * len(high_risk_data),
                    high_risk_data['处理建议'] if '处理建议' in high_risk_data.columns else ['需处理'] * len(
                        high_risk_data),
                    high_risk_data['优先级分数']
                )),
                hovertemplate="<b>🚨 高风险批次: %{customdata[0]}</b><br>" +
                              "<b>批号:</b> %{customdata[1]}<br>" +
                              "<b>数量:</b> %{customdata[2]:,} 箱<br>" +  # 整数显示
                              "<b>库龄:</b> %{customdata[3]} 天<br>" +
                              "<b>风险等级:</b> %{customdata[4]}<br>" +
                              "<b>批次价值:</b> ¥%{customdata[5]:,.0f}<br>" +
                              "<b>预期损失:</b> ¥%{customdata[6]:,.0f}<br>" +
                              "<b>处理建议:</b> %{customdata[7]}<br>" +
                              "<b>处理优先级:</b> %{customdata[8]:.1f}分<br>" +
                              "<extra></extra>",
                name="高风险批次"
            ), row=2, col=2)

        # 优化布局 - 解决悬停遮挡问题
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="库存风险综合分析",
            title_x=0.5,
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.95)",
                font_size=12,
                font_family="Inter",
                bordercolor="rgba(0,0,0,0.1)",
                align="left"
            ),
            hovermode='closest',
            paper_bgcolor='rgba(255,255,255,0.98)',
            plot_bgcolor='rgba(255,255,255,0.98)',
            margin=dict(l=20, r=20, t=80, b=20)
        )

        # 更新子图标题样式
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=16, family='Inter', weight=700)

        return fig

    except Exception as e:
        st.error(f"风险分析图表创建失败: {str(e)}")
        return go.Figure()


def create_region_analysis_fixed_final(region_stats, region_risk_details):
    """创建最终修复版的区域分析图表 - 修复箱数格式"""
    try:
        col1, col2 = st.columns(2)

        with col1:
            # 区域价值分布饼图
            if '批次价值' in region_stats.columns:
                fig_region_pie = go.Figure(data=[go.Pie(
                    labels=region_stats.index,
                    values=region_stats['批次价值'],
                    hole=.4,
                    marker_colors=COLOR_SCHEME['chart_colors'][:len(region_stats)],
                    hovertemplate="<b>🌍 %{label}区域</b><br>" +
                                  "库存价值: ¥%{value:,.2f}<br>" +
                                  "价值占比: %{percent}<br>" +
                                  "<extra></extra>"
                )])
                fig_region_pie.update_layout(
                    title="区域库存价值分布",
                    height=450,
                    hoverlabel=dict(
                        bgcolor="rgba(255,255,255,0.95)",
                        font_size=12,
                        bordercolor="rgba(0,0,0,0.1)"
                    )
                )
                st.plotly_chart(fig_region_pie, use_container_width=True)

        with col2:
            # 区域风险得分对比 - 修复箱数格式
            if '风险得分' in region_stats.columns:
                hover_data = []
                for region in region_stats.index:
                    score = region_stats.loc[region, '风险得分']
                    batch_stock = int(region_stats.loc[region, '批次库存']) if '批次库存' in region_stats.columns else 0
                    avg_age = int(region_stats.loc[region, '库龄']) if '库龄' in region_stats.columns else 0

                    if score > 70:
                        risk_level = "🔴 极高风险区域"
                        suggestion = "立即制定应急清库方案"
                    elif score > 60:
                        risk_level = "🟠 高风险区域"
                        suggestion = "加强监控，优化库存结构"
                    elif score > 40:
                        risk_level = "🟡 中风险区域"
                        suggestion = "定期审查，预防风险升级"
                    else:
                        risk_level = "🟢 低风险区域"
                        suggestion = "维持现状，正常管理"

                    hover_data.append([risk_level, suggestion, score, batch_stock, avg_age])

                region_colors = region_stats['风险得分'].apply(
                    lambda x: '#8B0000' if x > 70 else '#FF0000' if x > 60 else '#FFA500' if x > 40 else '#90EE90'
                )

                fig_region_risk = go.Figure(data=[go.Bar(
                    x=region_stats.index,
                    y=region_stats['风险得分'],
                    marker_color=region_colors,
                    text=region_stats['风险得分'].apply(lambda x: f"{x:.0f}分"),
                    textposition='outside',
                    textfont=dict(size=11),
                    customdata=hover_data,
                    hovertemplate="<b>🎯 %{x}区域</b><br>" +
                                  "风险得分: %{y:.0f}分<br>" +
                                  "风险等级: <b>%{customdata[0]}</b><br>" +
                                  "管理建议: %{customdata[1]}<br>" +
                                  "库存量: %{customdata[3]:,}箱<br>" +  # 整数显示
                                  "平均库龄: %{customdata[4]:,}天<br>" +  # 整数显示
                                  "<br><b>📊 评分逻辑</b><br>" +
                                  "• >70分: 极高风险<br>" +
                                  "• 60-70分: 高风险<br>" +
                                  "• 40-60分: 中风险<br>" +
                                  "• <40分: 低风险<br>" +
                                  "<extra></extra>"
                )])

                # 添加风险等级参考线
                fig_region_risk.add_hline(y=70, line_dash="dash", line_color="#8B0000",
                                          annotation=dict(text="极高风险线",
                                                          x=0.02, xanchor="left",
                                                          bgcolor="rgba(255,255,255,0.9)",
                                                          bordercolor="#8B0000"))
                fig_region_risk.add_hline(y=60, line_dash="dash", line_color="red",
                                          annotation=dict(text="高风险线",
                                                          x=0.02, xanchor="left", y=62,
                                                          bgcolor="rgba(255,255,255,0.9)",
                                                          bordercolor="red"))
                fig_region_risk.add_hline(y=40, line_dash="dash", line_color="orange",
                                          annotation=dict(text="中风险线",
                                                          x=0.02, xanchor="left", y=42,
                                                          bgcolor="rgba(255,255,255,0.9)",
                                                          bordercolor="orange"))

                fig_region_risk.update_layout(
                    title="区域风险得分与判断标准",
                    height=450,
                    yaxis_title="风险得分",
                    hoverlabel=dict(
                        bgcolor="rgba(255,255,255,0.95)",
                        font_size=11,
                        bordercolor="rgba(0,0,0,0.1)"
                    )
                )
                st.plotly_chart(fig_region_risk, use_container_width=True)

        return True

    except Exception as e:
        st.error(f"区域分析失败: {str(e)}")
        return False

def create_product_analysis_fixed_final(product_stats):
    """创建最终修复版的产品分析图表 - 修复箱数格式"""
    try:
        # 创建新的布局：2行，第一行2列，第二行1列占满
        fig_product = make_subplots(
            rows=2, cols=2,
            subplot_titles=("产品库存价值TOP15 (含周转率)", "产品库龄vs风险得分矩阵"),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter", "colspan": 2}, None]],
            row_heights=[0.4, 0.6],
            horizontal_spacing=0.12,
            vertical_spacing=0.15
        )

        # 1. TOP15产品价值 + 周转率信息 - 修复箱数格式
        top15_products = product_stats.head(15)

        risk_colors = {
            '极高风险': '#8B0000',
            '高风险': '#FF0000',
            '中风险': '#FFA500',
            '低风险': '#90EE90',
            '极低风险': '#006400',
            '未知': '#808080'
        }

        if '批次价值' in top15_products.columns:
            # 构建完整的悬停数据，修复数值格式
            hover_data = []
            for idx, row in top15_products.iterrows():
                risk_level = row.get('风险等级', '未知')
                turnover_rate = row.get('库存周转率', 0)
                batch_stock = int(row.get('批次库存', 0))  # 转换为整数
                avg_age = int(row.get('库龄', 0))  # 转换为整数
                risk_score = row.get('风险得分', 0)

                turnover_rating = (
                    '优秀(>6次/年)' if turnover_rate > 6 else
                    '良好(4-6次/年)' if turnover_rate > 4 else
                    '一般(2-4次/年)' if turnover_rate > 2 else
                    '需改进(<2次/年)'
                )

                hover_data.append([
                    risk_level, turnover_rate, turnover_rating,
                    batch_stock, avg_age, risk_score
                ])

            fig_product.add_trace(
                go.Bar(
                    x=top15_products.index,
                    y=top15_products['批次价值'],
                    marker_color=[risk_colors.get(data[0], '#808080') for data in hover_data],
                    text=top15_products['批次价值'].apply(lambda x: f"¥{x / 10000:.1f}万"),
                    textposition='auto',
                    textfont=dict(size=10),
                    customdata=hover_data,
                    hovertemplate="<b>%{x}</b><br>" +
                                  "库存价值: ¥%{y:,.2f}<br>" +
                                  "风险等级: <b>%{customdata[0]}</b><br>" +
                                  "风险得分: %{customdata[5]:.0f}分<br>" +
                                  "<br><b>📈 周转分析</b><br>" +
                                  "年周转率: %{customdata[1]:.1f}次<br>" +
                                  "周转评级: %{customdata[2]}<br>" +
                                  "<br><b>📊 基础数据</b><br>" +
                                  "库存量: %{customdata[3]:,}箱<br>" +  # 整数显示
                                  "平均库龄: %{customdata[4]:,}天<br>" +  # 整数显示
                                  "<extra></extra>",
                    name="产品价值分析"
                ),
                row=1, col=1
            )

        # 2. 产品库龄vs风险得分矩阵
        if all(col in product_stats.columns for col in ['库龄', '风险得分', '批次价值']):
            fig_product.add_trace(
                go.Scatter(
                    x=product_stats['库龄'],
                    y=product_stats['风险得分'],
                    mode='markers',
                    marker=dict(
                        size=np.log1p(product_stats['批次价值']) * 2.5,
                        color=product_stats.get('预计清库天数', [30] * len(product_stats)).replace([np.inf, -np.inf],
                                                                                                   365),
                        colorscale='RdYlGn_r',
                        cmin=0,
                        cmax=180,
                        showscale=True,
                        colorbar=dict(
                            title="清库天数",
                            x=1.02,
                            len=0.35
                        ),
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=product_stats.index,
                    hovertemplate="<b>%{text}</b><br>" +
                                  "库龄: %{x:.0f}天<br>" +
                                  "风险得分: %{y:.0f}分<br>" +
                                  "清库天数: %{marker.color:.0f}天<br>" +
                                  "<extra></extra>",
                    name="风险矩阵"
                ),
                row=1, col=2
            )

        # 3. 产品价值vs清库天数风险象限 - 修复气泡重叠和箱数格式
        if all(col in product_stats.columns for col in ['批次价值', '预计清库天数']):
            clearance_data = product_stats['预计清库天数'].replace([np.inf, -np.inf], 365)

            value_median = product_stats['批次价值'].median()
            象限分类 = np.where((product_stats['批次价值'] > value_median) &
                                (clearance_data > 90), '🔴高价值高风险',
                                np.where((product_stats['批次价值'] > value_median) &
                                         (clearance_data <= 90), '🟢高价值低风险',
                                         np.where((product_stats['批次价值'] <= value_median) &
                                                  (clearance_data > 90), '🟠低价值高风险', '🟡低价值低风险')))

            fig_product.add_trace(
                go.Scatter(
                    x=product_stats['批次价值'],
                    y=clearance_data,
                    mode='markers',
                    marker=dict(
                        size=product_stats.get('库龄', [30] * len(product_stats)) / 3.5,
                        color=[risk_colors.get(risk, '#808080') for risk in
                               product_stats.get('风险等级', ['未知'] * len(product_stats))],
                        opacity=0.7,
                        line=dict(width=1.5, color='white')
                    ),
                    text=product_stats.index,
                    customdata=np.column_stack((
                        象限分类,
                        product_stats.get('批次库存', [0] * len(product_stats)).astype(int),  # 转换为整数
                        product_stats.get('库龄', [0] * len(product_stats)).astype(int)  # 转换为整数
                    )),
                    hovertemplate="<b>%{text}</b><br>" +
                                  "库存价值: ¥%{x:,.2f}<br>" +
                                  "预计清库: %{y:.0f}天<br>" +
                                  "象限分类: <b>%{customdata[0]}</b><br>" +
                                  "库存量: %{customdata[1]:,}箱<br>" +  # 整数显示
                                  "库龄: %{customdata[2]:,}天<br>" +  # 整数显示
                                  "<extra></extra>",
                    name="价值风险象限"
                ),
                row=2, col=1
            )

            # 添加象限参考线
            fig_product.add_hline(y=90, line_dash="dash", line_color="red",
                                  annotation=dict(text="⚠️ 90天清库风险线",
                                                  xref="x3", yref="y3",
                                                  x=product_stats['批次价值'].max() * 0.8,
                                                  bgcolor="rgba(255,255,255,0.9)",
                                                  bordercolor="red"),
                                  row=2, col=1)

            fig_product.add_vline(x=value_median, line_dash="dash", line_color="blue",
                                  annotation=dict(text="💰 价值中位线",
                                                  xref="x3", yref="paper",
                                                  y=0.65, yanchor="bottom",
                                                  bgcolor="rgba(255,255,255,0.9)",
                                                  bordercolor="blue"),
                                  row=2, col=1)

        # 优化布局
        fig_product.update_layout(
            height=1000,
            showlegend=False,
            title_text="产品维度库存风险深度分析",
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.95)",
                font_size=11,
                font_family="Inter",
                bordercolor="rgba(0,0,0,0.1)",
                align="left"
            ),
            hovermode='closest',
            paper_bgcolor='rgba(255,255,255,0.98)',
            plot_bgcolor='rgba(255,255,255,0.98)',
            margin=dict(l=20, r=100, t=100, b=20)
        )

        # 调整坐标轴
        fig_product.update_xaxes(tickangle=-45, row=1, col=1)
        fig_product.update_xaxes(title_text="库存价值 (元)", row=2, col=1)
        fig_product.update_yaxes(title_text="预计清库天数 (天)", row=2, col=1)

        return fig_product

    except Exception as e:
        st.error(f"产品分析图表创建失败: {str(e)}")
        return go.Figure()


def create_region_analysis_optimized(region_stats, region_risk_details):
    """创建优化的区域分析图表 - 解决悬停遮挡问题"""
    try:
        col1, col2 = st.columns(2)

        with col1:
            # 区域价值分布饼图 - 优化悬停
            if '批次价值' in region_stats.columns:
                fig_region_pie = go.Figure(data=[go.Pie(
                    labels=region_stats.index,
                    values=region_stats['批次价值'],
                    hole=.4,
                    marker_colors=COLOR_SCHEME['chart_colors'][:len(region_stats)],
                    hovertemplate="<b>%{label}</b><br>" +
                                  "价值: ¥%{value:,.0f}<br>" +
                                  "占比: %{percent}<br>" +
                                  "<extra></extra>"
                )])
                fig_region_pie.update_layout(
                    title="区域库存价值分布",
                    height=450,
                    hoverlabel=dict(
                        bgcolor="rgba(255,255,255,0.95)",
                        font_size=12,
                        bordercolor="rgba(0,0,0,0.1)"
                    )
                )
                st.plotly_chart(fig_region_pie, use_container_width=True)

        with col2:
            # 区域风险得分对比 - 优化悬停
            if '风险得分' in region_stats.columns:
                region_colors = region_stats['风险得分'].apply(
                    lambda x: '#8B0000' if x > 70 else '#FF0000' if x > 60 else '#FFA500' if x > 40 else '#90EE90'
                )

                fig_region_risk = go.Figure(data=[go.Bar(
                    x=region_stats.index,
                    y=region_stats['风险得分'],
                    marker_color=region_colors,
                    text=region_stats['风险得分'].apply(lambda x: f"{x:.0f}"),
                    textposition='outside',
                    textfont=dict(size=11),
                    hovertemplate="<b>%{x}</b><br>" +
                                  "风险得分: %{y:.0f}分<br>" +
                                  "<extra></extra>"
                )])

                fig_region_risk.update_layout(
                    title="区域平均风险得分",
                    height=450,
                    yaxis_title="风险得分",
                    hoverlabel=dict(
                        bgcolor="rgba(255,255,255,0.95)",
                        font_size=12,
                        bordercolor="rgba(0,0,0,0.1)"
                    )
                )
                st.plotly_chart(fig_region_risk, use_container_width=True)

        return True

    except Exception as e:
        st.error(f"区域分析失败: {str(e)}")
        return False
def simplify_product_name(product_name):
    """简化产品名称：去掉'口力'和'-中国'"""
    if pd.isna(product_name):
        return product_name

    simplified = str(product_name)
    # 去掉"口力"
    simplified = simplified.replace('口力', '')
    # 去掉"-中国"
    simplified = simplified.replace('-中国', '')
    # 去掉开头的空格
    simplified = simplified.strip()

    return simplified


# 数据加载函数
# 替换原有的 load_and_process_data 函数
@st.cache_data
@st.cache_data
def load_and_process_data():
    """加载和处理所有数据 - 完整移植积压超详细.py的逻辑"""
    try:
        # 读取数据文件
        shipment_df = pd.read_excel('2409~250224出货数据.xlsx')
        forecast_df = pd.read_excel('2409~2502人工预测.xlsx')
        inventory_df = pd.read_excel('含批次库存0221(2).xlsx')
        price_df = pd.read_excel('单价.xlsx')

        # 处理日期
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])
        shipment_df.columns = ['订单日期', '所属区域', '申请人', '产品代码', '数量']

        forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'])
        forecast_df.columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']

        # 创建分析器实例
        analyzer = BatchLevelInventoryAnalyzer()

        # 创建销售人员-区域映射
        sales_person_region_mapping = {}
        person_region_data = shipment_df[['申请人', '所属区域']].drop_duplicates()
        person_region_counts = shipment_df.groupby(['申请人', '所属区域']).size().unstack(fill_value=0)

        for person in shipment_df['申请人'].unique():
            if person == analyzer.default_person:
                sales_person_region_mapping[person] = ""
            elif person in person_region_counts.index:
                most_common_region = person_region_counts.loc[person].idxmax()
                sales_person_region_mapping[person] = most_common_region
            else:
                sales_person_region_mapping[person] = analyzer.default_region

        # 对预测数据中的销售员也添加区域映射
        for person in forecast_df['销售员'].unique():
            if person == analyzer.default_person:
                continue
            if person not in sales_person_region_mapping:
                person_regions = forecast_df[forecast_df['销售员'] == person]['所属大区'].unique()
                if len(person_regions) > 0:
                    sales_person_region_mapping[person] = person_regions[0]
                else:
                    sales_person_region_mapping[person] = analyzer.default_region

        # 确保系统管理员的区域为空字符串
        sales_person_region_mapping[analyzer.default_person] = ""

        # 创建产品代码到名称的映射
        product_name_map = {}
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and pd.notna(row['描述']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                simplified_name = simplify_product_name(row['描述'])
                product_name_map[row['物料']] = simplified_name

        # 计算产品销售指标
        product_sales_metrics = {}
        today = datetime.now().date()

        for product_code in product_name_map.keys():
            product_sales = shipment_df[shipment_df['产品代码'] == product_code]

            if len(product_sales) == 0:
                product_sales_metrics[product_code] = {
                    'daily_avg_sales': 0,
                    'sales_std': 0,
                    'coefficient_of_variation': float('inf'),
                    'total_sales': 0,
                    'last_90_days_sales': 0
                }
            else:
                total_sales = product_sales['数量'].sum()
                ninety_days_ago = today - timedelta(days=90)
                recent_sales = product_sales[product_sales['订单日期'].dt.date >= ninety_days_ago]
                recent_sales_total = recent_sales['数量'].sum() if len(recent_sales) > 0 else 0

                days_range = (today - product_sales['订单日期'].min().date()).days + 1
                daily_avg_sales = total_sales / days_range if days_range > 0 else 0

                daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['数量'].sum()
                sales_std = daily_sales.std() if len(daily_sales) > 1 else 0

                coefficient_of_variation = sales_std / daily_avg_sales if daily_avg_sales > 0 else float('inf')

                product_sales_metrics[product_code] = {
                    'daily_avg_sales': daily_avg_sales,
                    'sales_std': sales_std,
                    'coefficient_of_variation': coefficient_of_variation,
                    'total_sales': total_sales,
                    'last_90_days_sales': recent_sales_total
                }

        # 计算季节性指数
        seasonal_indices = {}
        for product_code in product_name_map.keys():
            product_sales = shipment_df[shipment_df['产品代码'] == product_code]

            if len(product_sales) > 0:
                product_sales['月份'] = product_sales['订单日期'].dt.month
                monthly_sales = product_sales.groupby('月份')['数量'].sum()

                if len(monthly_sales) > 1:
                    avg_monthly_sales = monthly_sales.mean()
                    current_month = today.month
                    if current_month in monthly_sales.index:
                        seasonal_index = monthly_sales[current_month] / avg_monthly_sales
                    else:
                        seasonal_index = 1.0
                else:
                    seasonal_index = 1.0
            else:
                seasonal_index = 1.0

            seasonal_index = max(seasonal_index, analyzer.min_seasonal_index)
            seasonal_indices[product_code] = seasonal_index

        # 计算预测准确度
        forecast_accuracy = {}
        for product_code in product_name_map.keys():
            product_forecast = forecast_df[forecast_df['产品代码'] == product_code]

            if len(product_forecast) > 0:
                forecast_quantity = product_forecast['预计销售量'].sum()

                one_month_ago = today - timedelta(days=30)
                product_recent_sales = shipment_df[
                    (shipment_df['产品代码'] == product_code) &
                    (shipment_df['订单日期'].dt.date >= one_month_ago)
                ]

                actual_sales = product_recent_sales['数量'].sum() if not product_recent_sales.empty else 0

                forecast_bias = analyzer.calculate_forecast_bias(forecast_quantity, actual_sales)

                # 按销售员分组的预测
                person_forecast = product_forecast.groupby('销售员')['预计销售量'].sum().to_dict()
            else:
                forecast_bias = 0.0
                person_forecast = {}

            forecast_accuracy[product_code] = {
                'forecast_bias': forecast_bias,
                'person_forecast': person_forecast
            }

        # 处理批次数据并进行完整分析
        batch_data = []
        current_material = None
        current_desc = None
        current_price = 0

        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                current_material = row['物料']
                current_desc = simplify_product_name(row['描述'])
                price_match = price_df[price_df['产品代码'] == current_material]
                current_price = price_match['单价'].iloc[0] if len(price_match) > 0 else 100
            elif pd.notna(row['生产日期']) and current_material:
                prod_date = pd.to_datetime(row['生产日期'])
                quantity = row['数量'] if pd.notna(row['数量']) else 0
                batch_no = row['生产批号'] if pd.notna(row['生产批号']) else ''

                # 计算库龄
                age_days = (datetime.now() - prod_date).days

                # 获取销售指标
                sales_metrics = product_sales_metrics.get(current_material, {
                    'daily_avg_sales': 0,
                    'sales_std': 0,
                    'coefficient_of_variation': float('inf'),
                    'total_sales': 0,
                    'last_90_days_sales': 0
                })

                # 获取季节性指数
                seasonal_index = seasonal_indices.get(current_material, 1.0)

                # 获取预测准确度
                forecast_info = forecast_accuracy.get(current_material, {
                    'forecast_bias': 0.0,
                    'person_forecast': {}
                })

                # 获取产品单价并计算批次价值
                unit_price = current_price
                batch_value = quantity * unit_price

                # 计算预计清库天数
                daily_avg_sales = sales_metrics['daily_avg_sales']
                daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, analyzer.min_daily_sales)

                if daily_avg_sales_adjusted > 0:
                    days_to_clear = quantity / daily_avg_sales_adjusted
                    one_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 30)
                    two_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 60)
                    three_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 90)
                else:
                    days_to_clear = float('inf')
                    one_month_risk = 100
                    two_month_risk = 100
                    three_month_risk = 100

                # 使用完整的责任归属分析
                responsible_region, responsible_person, responsibility_details = analyzer.analyze_responsibility_collaborative(
                    current_material, prod_date, sales_metrics, forecast_info, None, quantity, sales_person_region_mapping
                )

                # 确定积压原因
                stocking_reasons = []
                if age_days > 60:
                    stocking_reasons.append("库龄过长")
                if sales_metrics['coefficient_of_variation'] > analyzer.high_volatility_threshold:
                    stocking_reasons.append("销量波动大")
                if seasonal_index < 0.8:
                    stocking_reasons.append("季节性影响")
                if abs(forecast_info['forecast_bias']) > analyzer.high_forecast_bias_threshold:
                    stocking_reasons.append("预测偏差大")
                if not stocking_reasons:
                    stocking_reasons.append("正常库存")

                # 风险等级评估
                risk_score = 0

                # 库龄因素
                if age_days > 90:
                    risk_score += 40
                elif age_days > 60:
                    risk_score += 30
                elif age_days > 30:
                    risk_score += 20
                else:
                    risk_score += 10

                # 清库天数因素
                if days_to_clear == float('inf'):
                    risk_score += 40
                elif days_to_clear > 180:
                    risk_score += 35
                elif days_to_clear > 90:
                    risk_score += 30
                elif days_to_clear > 60:
                    risk_score += 20
                elif days_to_clear > 30:
                    risk_score += 10

                # 销量波动系数
                if sales_metrics['coefficient_of_variation'] > 2.0:
                    risk_score += 10
                elif sales_metrics['coefficient_of_variation'] > 1.0:
                    risk_score += 5

                # 预测偏差
                if abs(forecast_info['forecast_bias']) > 0.5:
                    risk_score += 10
                elif abs(forecast_info['forecast_bias']) > 0.3:
                    risk_score += 8
                elif abs(forecast_info['forecast_bias']) > 0.15:
                    risk_score += 5

                # 根据总分确定风险等级
                if risk_score >= 80:
                    risk_level = "极高风险"
                    risk_advice = '🚨 立即7折清库'
                elif risk_score >= 60:
                    risk_level = "高风险"
                    risk_advice = '⚠️ 建议8折促销'
                elif risk_score >= 40:
                    risk_level = "中风险"
                    risk_advice = '📢 适度9折促销'
                elif risk_score >= 20:
                    risk_level = "低风险"
                    risk_advice = '✅ 正常销售'
                else:
                    risk_level = "极低风险"
                    risk_advice = '🌟 新鲜库存'

                # 生成建议措施
                if risk_level == "极高风险":
                    recommendation = "紧急清理：考虑折价促销"
                elif risk_level == "高风险":
                    recommendation = "优先处理：降价促销或转仓调配"
                elif risk_level == "中风险":
                    recommendation = "密切监控：调整采购计划"
                elif risk_level == "低风险":
                    recommendation = "常规管理：定期审查库存周转"
                else:
                    recommendation = "维持现状：正常库存水平"

                # 预期损失计算
                if age_days >= 120:
                    expected_loss = quantity * unit_price * 0.3
                elif age_days >= 90:
                    expected_loss = quantity * unit_price * 0.2
                elif age_days >= 60:
                    expected_loss = quantity * unit_price * 0.1
                else:
                    expected_loss = 0

                # 格式化预测偏差为百分比
                forecast_bias_value = forecast_info['forecast_bias']
                if forecast_bias_value == float('inf'):
                    forecast_bias_pct = "无穷大"
                elif forecast_bias_value == 0:
                    forecast_bias_pct = "0%"
                else:
                    forecast_bias_pct = f"{round(forecast_bias_value * 100, 1)}%"

                # 生成责任分析摘要
                responsibility_summary = analyzer.generate_responsibility_summary_collaborative(responsibility_details)

                # 将分析结果添加到列表
                batch_data.append({
                    '物料': current_material,
                    '产品名称': current_desc,
                    '描述': current_desc,
                    '生产日期': prod_date,
                    '生产批号': batch_no,
                    '批次日期': prod_date.date(),
                    '数量': quantity,
                    '批次库存': quantity,
                    '库龄': age_days,
                    '风险等级': risk_level,
                    '风险颜色': '',  # 将在显示时设置
                    '处理建议': risk_advice,
                    '单价': unit_price,
                    '批次价值': batch_value,
                    '预期损失': expected_loss,
                    '日均出货': round(daily_avg_sales, 2),
                    '出货标准差': round(sales_metrics['sales_std'], 2),
                    '出货波动系数': round(sales_metrics['coefficient_of_variation'], 2),
                    '预计清库天数': days_to_clear if days_to_clear != float('inf') else float('inf'),
                    '一个月积压风险': f"{round(one_month_risk, 1)}%",
                    '两个月积压风险': f"{round(two_month_risk, 1)}%",
                    '三个月积压风险': f"{round(three_month_risk, 1)}%",
                    '积压原因': '，'.join(stocking_reasons),
                    '季节性指数': round(seasonal_index, 2),
                    '预测偏差': forecast_bias_pct,
                    '责任区域': responsible_region,
                    '责任人': responsible_person,
                    '责任详情': responsibility_details,
                    '责任分析摘要': responsibility_summary,
                    '风险程度': risk_level,
                    '风险得分': risk_score,
                    '建议措施': recommendation
                })

        processed_inventory = pd.DataFrame(batch_data)

        # 按照风险程度和库龄排序
        risk_order = {
            "极高风险": 0,
            "高风险": 1,
            "中风险": 2,
            "低风险": 3,
            "极低风险": 4
        }
        processed_inventory['风险排序'] = processed_inventory['风险程度'].map(risk_order)
        processed_inventory = processed_inventory.sort_values(by=['风险排序', '库龄'], ascending=[True, False])
        processed_inventory = processed_inventory.drop(columns=['风险排序'])

        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory)

        return processed_inventory, shipment_df, forecast_df, metrics, product_name_map

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, {}


def create_enhanced_region_forecast_chart(merged_data):
    """创建升级版区域预测准确率图表 - 修复标签遮挡问题，移动到图表外部"""
    try:
        if merged_data is None or merged_data.empty:
            fig = go.Figure()
            fig.update_layout(
                title="区域预测准确率分析 (无数据)",
                annotations=[
                    dict(
                        text="暂无预测数据",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        xanchor='center', yanchor='middle',
                        font=dict(size=20, color="gray")
                    )
                ]
            )
            return fig, pd.DataFrame()

        # 区域汇总数据
        region_comparison = merged_data.groupby('所属区域').agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index()

        region_comparison['准确率'] = region_comparison['准确率'] * 100
        region_comparison['销量占比'] = (region_comparison['实际销量'] / region_comparison['实际销量'].sum() * 100)
        region_comparison['差异量'] = region_comparison['实际销量'] - region_comparison['预测销量']
        region_comparison['差异率'] = (region_comparison['差异量'] / region_comparison['实际销量']).fillna(0) * 100

        # 按准确率排序
        region_comparison = region_comparison.sort_values('准确率', ascending=True)

        # 计算全国平均准确率
        national_average = region_comparison['准确率'].mean()

        # 创建现代化的水平条形图
        fig = go.Figure()

        # 根据准确率设置渐变色
        colors = []
        for accuracy in region_comparison['准确率']:
            if accuracy >= 85:
                colors.append('#2E8B57')  # 海绿色 - 优秀
            elif accuracy >= 75:
                colors.append('#32CD32')  # 酸橙绿 - 良好
            elif accuracy >= 65:
                colors.append('#FFD700')  # 金色 - 一般
            elif accuracy >= 55:
                colors.append('#FF8C00')  # 深橙色 - 需改进
            else:
                colors.append('#DC143C')  # 深红色 - 差

        # 获取最佳和最差区域信息
        best_region = region_comparison.iloc[-1]
        worst_region = region_comparison.iloc[0]

        # 准备悬停信息
        hover_data = []
        for idx, row in region_comparison.iterrows():
            hover_info = (
                f"<b>🌏 {row['所属区域']}区域预测表现</b><br>"
                f"<b>预测准确率:</b> {row['准确率']:.1f}%<br>"
                f"<br><b>📊 销量数据</b><br>"
                f"实际销量: {int(row['实际销量']):,}箱<br>"
                f"预测销量: {int(row['预测销量']):,}箱<br>"
                f"销量占比: {row['销量占比']:.1f}%<br>"
                f"<br><b>📈 预测偏差</b><br>"
                f"差异量: {int(row['差异量']):+,}箱<br>"
                f"差异率: {row['差异率']:+.1f}%<br>"
                f"<br><b>📋 全国对比</b><br>"
                f"🥇 最佳区域: {best_region['所属区域']} ({best_region['准确率']:.1f}%)<br>"
                f"🎯 待改进区域: {worst_region['所属区域']} ({worst_region['准确率']:.1f}%)<br>"
                f"📊 全国平均: {national_average:.1f}%<br>"
                f"<br><b>🎨 颜色说明</b><br>"
                f"🟢 绿色 = 优秀 (≥85%)<br>"
                f"🟡 黄色 = 一般 (65-85%)<br>"
                f"🔴 红色 = 需改进 (<65%)"
            )
            hover_data.append(hover_info)

        # 主要条形图
        fig.add_trace(go.Bar(
            y=region_comparison['所属区域'],
            x=region_comparison['准确率'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.8)', width=2),
                # 添加渐变效果
                opacity=0.9
            ),
            text=[f"{acc:.1f}%" for acc in region_comparison['准确率']],
            textposition='outside',
            textfont=dict(size=14, color='black', family='Inter'),
            name="预测准确率",
            customdata=hover_data,
            hovertemplate="%{customdata}<extra></extra>"
        ))

        # 计算图表顶部位置（用于所有标注的统一y坐标）
        top_position = len(region_comparison) + 0.8

        # 添加全国平均线（垂直虚线）
        fig.add_vline(
            x=national_average, 
            line_dash="dash", 
            line_color="#4169E1", 
            line_width=3
        )

        # 添加全国平均线标注 - 精简样式，放在线的正上方
        fig.add_annotation(
            x=national_average,
            y=top_position,
            text=f"全国平均<br>{national_average:.1f}%",
            showarrow=False,
            bgcolor="rgba(65,105,225,0.85)",
            bordercolor="#4169E1",
            borderwidth=1,
            font=dict(color="white", size=10, family="Inter"),
            xanchor="center",
            yanchor="bottom",
            borderpad=3
        )

        # 添加优秀标准参考线
        fig.add_vline(x=85, line_dash="dash", line_color="#2E8B57", line_width=2)
        fig.add_annotation(
            x=85,
            y=top_position,
            text="优秀标准<br>85%",
            showarrow=False,
            bgcolor="rgba(46,139,87,0.85)",
            bordercolor="#2E8B57",
            borderwidth=1,
            font=dict(color="white", size=10, family="Inter"),
            xanchor="center",
            yanchor="bottom",
            borderpad=3
        )

        # 添加良好标准参考线
        fig.add_vline(x=75, line_dash="dot", line_color="#FFD700", line_width=2)
        fig.add_annotation(
            x=75,
            y=top_position,
            text="良好标准<br>75%",
            showarrow=False,
            bgcolor="rgba(255,215,0,0.9)",
            bordercolor="#FFD700",
            borderwidth=1,
            font=dict(color="black", size=10, family="Inter"),
            xanchor="center",
            yanchor="bottom",
            borderpad=3
        )

        # 添加及格标准参考线
        fig.add_vline(x=65, line_dash="dot", line_color="#FF8C00", line_width=2)
        fig.add_annotation(
            x=65,
            y=top_position,
            text="及格标准<br>65%",
            showarrow=False,
            bgcolor="rgba(255,140,0,0.85)",
            bordercolor="#FF8C00",
            borderwidth=1,
            font=dict(color="white", size=10, family="Inter"),
            xanchor="center",
            yanchor="bottom",
            borderpad=3
        )

        # 现代化布局设计 - 优化比例和空间利用
        fig.update_layout(
            title=dict(
                text="<b>区域预测准确率综合分析</b><br><sub>基于实际销量与预测销量对比 | 彩色编码显示表现等级 | 悬停查看详细分析</sub>",
                x=0.5,
                xanchor='center',
                font=dict(size=18, family='Inter')
            ),
            xaxis=dict(
                title=dict(
                    text="<b>预测准确率 (%)</b>",
                    font=dict(size=14, family='Inter')
                ),
                range=[0, max(region_comparison['准确率'].max() + 5, 90)],
                ticksuffix="%",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                gridwidth=1,
                tickfont=dict(size=12, family='Inter')
            ),
            yaxis=dict(
                title=dict(
                    text="<b>销售区域</b>",
                    font=dict(size=14, family='Inter')
                ),
                tickfont=dict(size=13, family='Inter'),
                categoryorder='array',
                categoryarray=region_comparison['所属区域'].tolist(),
                range=[-0.5, len(region_comparison) + 1.2]  # 为顶部标注预留空间
            ),
            height=max(450, len(region_comparison) * 70 + 120),  # 优化高度，为标注预留空间
            margin=dict(l=80, r=40, t=120, b=80),  # 优化边距，减少右侧空白
            showlegend=False,
            plot_bgcolor='rgba(248,250,252,0.8)',
            paper_bgcolor='rgba(255,255,255,0.95)',
            font=dict(family='Inter'),
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.98)",
                font_size=13,
                font_family="Inter",
                bordercolor="rgba(0,0,0,0.1)",
                align="left"
            ),
            # 添加动画效果
            transition=dict(duration=500, easing="cubic-in-out")
        )

        return fig, region_comparison

    except Exception as e:
        st.error(f"区域预测准确率图表创建失败: {str(e)}")
        return go.Figure(), pd.DataFrame()
def calculate_key_metrics(processed_inventory):
    """计算关键指标"""
    if processed_inventory.empty:
        return {
            'total_batches': 0,
            'high_risk_batches': 0,
            'high_risk_ratio': 0,
            'total_inventory_value': 0,
            'high_risk_value_ratio': 0,
            'avg_age': 0,
            'high_risk_value': 0,
            'risk_counts': {
                'extreme': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'minimal': 0
            }
        }

    total_batches = len(processed_inventory)
    high_risk_batches = len(processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])])
    high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0

    total_inventory_value = processed_inventory['批次价值'].sum() / 1000000
    high_risk_value = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险'])
    ]['批次价值'].sum()
    high_risk_value_ratio = (high_risk_value / processed_inventory['批次价值'].sum() * 100) if processed_inventory[
                                                                                                   '批次价值'].sum() > 0 else 0

    avg_age = processed_inventory['库龄'].mean()

    # 风险分布统计
    risk_counts = processed_inventory['风险等级'].value_counts().to_dict()

    return {
        'total_batches': int(total_batches),
        'high_risk_batches': int(high_risk_batches),
        'high_risk_ratio': round(high_risk_ratio, 1),
        'total_inventory_value': round(total_inventory_value, 2),
        'high_risk_value_ratio': round(high_risk_value_ratio, 1),
        'avg_age': round(avg_age, 0),
        'high_risk_value': round(high_risk_value / 1000000, 1),
        'risk_counts': {
            'extreme': risk_counts.get('极高风险', 0),
            'high': risk_counts.get('高风险', 0),
            'medium': risk_counts.get('中风险', 0),
            'low': risk_counts.get('低风险', 0),
            'minimal': risk_counts.get('极低风险', 0)
        }
    }


def process_forecast_analysis(shipment_df, forecast_df, product_name_map):
    """处理预测分析数据 - 只使用当年数据"""
    try:
        current_year = datetime.now().year

        # 筛选当年数据
        shipment_current_year = shipment_df[shipment_df['订单日期'].dt.year == current_year].copy()
        forecast_current_year = forecast_df[forecast_df['所属年月'].dt.year == current_year].copy()

        if shipment_current_year.empty or forecast_current_year.empty:
            return None, {}

        # 添加产品名称映射
        shipment_current_year['产品名称'] = shipment_current_year['产品代码'].map(product_name_map).fillna(
            shipment_current_year['产品代码'])
        forecast_current_year['产品名称'] = forecast_current_year['产品代码'].map(product_name_map).fillna(
            forecast_current_year['产品代码'])

        # 按月份和产品汇总实际销量 - 修正列名
        shipment_monthly = shipment_current_year.groupby([
            shipment_current_year['订单日期'].dt.to_period('M'),
            '产品代码',
            '产品名称',
            '所属区域'
        ]).agg({
            '数量': 'sum'  # 修正：从 '求和项:数量（箱）' 改为 '数量'
        }).reset_index()
        shipment_monthly['年月'] = shipment_monthly['订单日期'].dt.to_timestamp()

        # 按月份和产品汇总预测销量
        forecast_monthly = forecast_current_year.groupby([
            forecast_current_year['所属年月'].dt.to_period('M'),
            '产品代码',
            '产品名称',
            '所属大区'
        ]).agg({
            '预计销售量': 'sum'
        }).reset_index()
        forecast_monthly['年月'] = forecast_monthly['所属年月'].dt.to_timestamp()

        # 统一区域名称
        forecast_monthly = forecast_monthly.rename(columns={'所属大区': '所属区域'})

        # 合并数据
        merged_data = pd.merge(
            shipment_monthly,
            forecast_monthly,
            on=['年月', '产品代码', '产品名称', '所属区域'],
            how='outer'
        ).fillna(0)

        # 计算准确率和差异 - 修正列名
        merged_data['实际销量'] = merged_data['数量']  # 修正：从 '求和项:数量（箱）' 改为 '数量'
        merged_data['预测销量'] = merged_data['预计销售量']
        merged_data['差异量'] = merged_data['实际销量'] - merged_data['预测销量']

        # 计算准确率
        merged_data['准确率'] = merged_data.apply(
            lambda row: 1 - abs(row['差异量']) / max(row['实际销量'], 1) if row['实际销量'] > 0 else
            (1 if row['预测销量'] == 0 else 0),
            axis=1
        )
        merged_data['准确率'] = merged_data['准确率'].clip(0, 1)

        # 计算关键指标
        key_metrics = {
            'total_actual_sales': merged_data['实际销量'].sum(),
            'total_forecast_sales': merged_data['预测销量'].sum(),
            'overall_accuracy': merged_data['准确率'].mean() * 100,
            'overall_diff_rate': ((merged_data['实际销量'].sum() - merged_data['预测销量'].sum()) /
                                  merged_data['实际销量'].sum()) * 100 if merged_data['实际销量'].sum() > 0 else 0
        }

        return merged_data, key_metrics

    except Exception as e:
        st.error(f"预测分析处理失败: {str(e)}")
        return None, {}


def create_integrated_risk_analysis(processed_inventory):
    """创建整合的风险分析图表 - 增强版本带高级悬停"""
    try:
        if processed_inventory.empty:
            fig = go.Figure()
            fig.update_layout(
                title="风险分析 (无数据)",
                annotations=[
                    dict(
                        text="暂无库存数据",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        xanchor='center', yanchor='middle',
                        font=dict(size=20, color="gray")
                    )
                ]
            )
            return fig

        # 风险分布数据
        risk_counts = processed_inventory['风险等级'].value_counts()
        risk_value = processed_inventory.groupby('风险等级')['批次价值'].sum() / 1000000

        # 创建颜色映射字典
        risk_color_map = {
            '极高风险': '#8B0000',  # 深红色
            '高风险': '#FF0000',  # 红色
            '中风险': '#FFA500',  # 橙色
            '低风险': '#90EE90',  # 浅绿色
            '极低风险': '#006400'  # 深绿色
        }

        # 按风险等级顺序排列
        risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        ordered_risks = [risk for risk in risk_order if risk in risk_counts.index]
        colors = [risk_color_map[risk] for risk in ordered_risks]

        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("风险等级分布", "各风险等级价值分布", "库存批次库龄分布", "高风险批次优先级分析"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )

        # 为饼图准备详细信息
        risk_details = {}
        for risk in ordered_risks:
            risk_products = processed_inventory[processed_inventory['风险等级'] == risk]
            risk_details[risk] = {
                'count': len(risk_products),
                'value': risk_products['批次价值'].sum() / 1000000,
                'products': risk_products.groupby('产品名称').agg({
                    '数量': 'count',
                    '批次价值': 'sum'
                }).head(5).to_dict()
            }

        # 1. 风险等级分布饼图 - 增强悬停
        fig.add_trace(go.Pie(
            labels=ordered_risks,
            values=[risk_counts[risk] for risk in ordered_risks],
            hole=.4,
            marker_colors=colors,
            textinfo='label+percent',
            name="风险分布",
            customdata=[[risk_details[risk]['count'],
                         risk_details[risk]['value'],
                         ', '.join(list(risk_details[risk]['products']['数量'].keys())[:3])] for risk in ordered_risks],
            hovertemplate="<b>%{label}</b><br>" +
                          "批次数量: %{value}个<br>" +
                          "占比: %{percent}<br>" +
                          "总价值: ¥%{customdata[1]:.1f}M<br>" +
                          "主要产品: %{customdata[2]}<br>" +
                          "<extra></extra>"
        ), row=1, col=1)

        # 2. 风险等级价值分布 - 增强悬停
        fig.add_trace(go.Bar(
            x=ordered_risks,
            y=[risk_value.get(risk, 0) for risk in ordered_risks],
            marker_color=colors,
            name="价值分布",
            text=[f'¥{risk_value.get(risk, 0):.1f}M' for risk in ordered_risks],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>" +
                          "总价值: ¥%{y:.1f}M<br>" +
                          "批次数: " + ", ".join(
                [f"{risk}: {risk_counts.get(risk, 0)}个" for risk in ordered_risks]) + "<br>" +
                          "<extra></extra>"
        ), row=1, col=2)

        # 3. 库龄分布直方图 - 增强悬停显示产品信息
        # 创建库龄区间的产品信息
        age_bins = pd.cut(processed_inventory['库龄'], bins=20)
        age_product_info = processed_inventory.groupby([age_bins, '产品名称']).size().reset_index(name='批次数')

        fig.add_trace(go.Histogram(
            x=processed_inventory['库龄'],
            nbinsx=20,
            marker_color=COLOR_SCHEME['primary'],
            opacity=0.7,
            name="库龄分布",
            customdata=processed_inventory[['产品名称', '库龄', '生产批号']],
            hovertemplate="库龄: %{x}天<br>" +
                          "批次数量: %{y}个<br>" +
                          "<extra></extra>"
        ), row=2, col=1)

        # 4. 高风险批次分析 - 增强悬停
        high_risk_data = processed_inventory[
            processed_inventory['风险等级'].isin(['极高风险', '高风险'])
        ].head(15)

        if not high_risk_data.empty:
            # 计算建议处理优先级
            high_risk_data['优先级分数'] = (
                    high_risk_data['库龄'] * 0.4 +
                    high_risk_data['批次价值'] / high_risk_data['批次价值'].max() * 100 * 0.6
            )

            fig.add_trace(go.Scatter(
                x=high_risk_data['库龄'],
                y=high_risk_data['批次价值'],
                mode='markers',
                marker=dict(
                    size=np.minimum(high_risk_data['数量'] / 20, 50),
                    color=high_risk_data['风险等级'].map({
                        '极高风险': COLOR_SCHEME['risk_extreme'],
                        '高风险': COLOR_SCHEME['risk_high']
                    }),
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=high_risk_data['产品名称'],
                customdata=np.column_stack((
                    high_risk_data['产品名称'],
                    high_risk_data['生产批号'],
                    high_risk_data['数量'],
                    high_risk_data['库龄'],
                    high_risk_data['风险等级'],
                    high_risk_data['批次价值'],
                    high_risk_data['预期损失'],
                    high_risk_data['处理建议'],
                    high_risk_data['优先级分数']
                )),
                hovertemplate="""
                <b>🚨 高风险批次详情</b><br><br>
                <b>产品:</b> %{customdata[0]}<br>
                <b>批号:</b> %{customdata[1]}<br>
                <b>数量:</b> %{customdata[2]:,.0f} 箱<br>
                <b>库龄:</b> %{customdata[3]} 天<br>
                <b>风险等级:</b> <span style="color: red;">%{customdata[4]}</span><br>
                <b>批次价值:</b> ¥%{customdata[5]:,.0f}<br>
                <b>预期损失:</b> ¥%{customdata[6]:,.0f}<br>
                <b>处理建议:</b> %{customdata[7]}<br>
                <b>处理优先级:</b> %{customdata[8]:.1f}分<br>
                <extra></extra>
                """,
                name="高风险批次"
            ), row=2, col=2)

        # 更新布局 - 优化悬停体验
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="库存风险综合分析",
            title_x=0.5,
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.95)",
                font_size=13,
                font_family="Inter",
                align="left",
                namelength=-1
            ),
            hovermode='closest',
            hoverdistance=20,
            paper_bgcolor='rgba(255,255,255,0.98)',
            plot_bgcolor='rgba(255,255,255,0.98)',
            margin=dict(l=50, r=50, t=100, b=50)
        )

        # 为不同类型的图表设置悬停对齐
        fig.update_traces(
            hoverlabel_align='auto',
            selector=dict(type='pie')
        )
        fig.update_traces(
            hoverlabel_align='right',
            selector=dict(type='bar')
        )
        fig.update_traces(
            hoverlabel_align='auto',
            selector=dict(type='histogram')
        )
        fig.update_traces(
            hoverlabel_align='left',
            selector=dict(type='scatter')
        )

        # 更新子图标题样式
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=16, family='Inter', weight=700)

        return fig

    except Exception as e:
        st.error(f"风险分析图表创建失败: {str(e)}")
        return go.Figure()


def create_ultra_integrated_forecast_chart(merged_data):
    """创建超级整合的预测分析图表 - 修复图例位置和箱数格式"""
    try:
        if merged_data is None or merged_data.empty:
            fig = go.Figure()
            fig.update_layout(
                title="预测分析 (无数据)",
                annotations=[
                    dict(
                        text="暂无预测数据",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        xanchor='center', yanchor='middle',
                        font=dict(size=20, color="gray")
                    )
                ]
            )
            return fig

        # 1. 分析重点SKU (销售额占比80%的产品)
        total_sales_by_product = merged_data.groupby(['产品代码', '产品名称'])['实际销量'].sum().reset_index()
        total_sales_by_product = total_sales_by_product.sort_values('实际销量', ascending=False)
        total_sales = total_sales_by_product['实际销量'].sum()
        total_sales_by_product['累计占比'] = total_sales_by_product['实际销量'].cumsum() / total_sales
        key_products_df = total_sales_by_product[total_sales_by_product['累计占比'] <= 0.8]
        key_products = key_products_df['产品代码'].tolist()

        # 2. 产品级别汇总分析
        product_analysis = merged_data.groupby(['产品代码', '产品名称']).agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index()

        # 计算差异
        product_analysis['差异量'] = product_analysis['实际销量'] - product_analysis['预测销量']
        product_analysis['差异率'] = (product_analysis['差异量'] / product_analysis['实际销量']).fillna(0) * 100
        product_analysis['销售占比'] = product_analysis['实际销量'] / product_analysis['实际销量'].sum() * 100
        product_analysis['是否重点SKU'] = product_analysis['产品代码'].isin(key_products)

        # 计算预测改进建议
        product_analysis['改进建议'] = product_analysis.apply(
            lambda row: "🟢 预测优秀，保持现状" if row['准确率'] > 0.9 else
            "🟡 预测良好，微调即可" if row['准确率'] > 0.8 else
            "🟠 需改进预测模型" if row['准确率'] > 0.7 else
            "🔴 紧急优化预测方法",
            axis=1
        )

        # 3. 区域分析
        region_analysis = merged_data.groupby('所属区域').agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index().sort_values('准确率', ascending=False)

        # 创建超级整合图表
        fig = go.Figure()

        # 重点SKU - 修复箱数格式为整数
        key_products_data = product_analysis[product_analysis['是否重点SKU']]
        if not key_products_data.empty:
            fig.add_trace(go.Scatter(
                x=key_products_data['实际销量'],
                y=key_products_data['预测销量'],
                mode='markers',
                marker=dict(
                    size=key_products_data['销售占比'] * 2,
                    sizemin=15,
                    color=key_products_data['准确率'],
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=1,
                    opacity=0.8,
                    line=dict(width=2, color='white'),
                    colorbar=dict(
                        title=dict(text="预测准确率", side="right"),
                        tickmode="linear",
                        tick0=0,
                        dtick=0.2,
                        tickformat=".0%",
                        x=1.02
                    )
                ),
                text=key_products_data['产品名称'],
                customdata=np.column_stack((
                    key_products_data['产品名称'],
                    key_products_data['实际销量'].astype(int),  # 转换为整数
                    key_products_data['预测销量'].astype(int),  # 转换为整数
                    key_products_data['差异量'].astype(int),   # 转换为整数
                    key_products_data['差异率'],
                    key_products_data['销售占比'],
                    key_products_data['准确率'] * 100,
                    key_products_data['改进建议'],
                    key_products_data['产品代码']
                )),
                hovertemplate="<b>🎯 重点SKU: %{customdata[0]}</b><br>" +
                              "<b>代码: %{customdata[8]}</b><br>" +
                              "<br><b>📊 销量对比</b><br>" +
                              "实际销量: <b>%{customdata[1]:,}</b>箱<br>" +  # 整数显示
                              "预测销量: <b>%{customdata[2]:,}</b>箱<br>" +  # 整数显示
                              "差异量: %{customdata[3]:+,}箱<br>" +  # 整数显示
                              "<br><b>📈 准确性分析</b><br>" +
                              "预测准确率: <b>%{customdata[6]:.1f}%</b><br>" +
                              "销售占比: <b>%{customdata[5]:.1f}%</b><br>" +
                              "<br><b>💡 改进建议</b><br>" +
                              "%{customdata[7]}<br>" +
                              "<extra></extra>",
                name="重点SKU (占销售额80%)",
                legendgroup="key"
            ))

        # 其他产品 - 修复箱数格式为整数
        other_products_data = product_analysis[~product_analysis['是否重点SKU']].head(20)
        if not other_products_data.empty:
            fig.add_trace(go.Scatter(
                x=other_products_data['实际销量'],
                y=other_products_data['预测销量'],
                mode='markers',
                marker=dict(
                    size=other_products_data['销售占比'] * 2,
                    sizemin=8,
                    color=other_products_data['准确率'],
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=1,
                    opacity=0.5,
                    line=dict(width=1, color='gray'),
                    showscale=False
                ),
                text=other_products_data['产品名称'],
                customdata=np.column_stack((
                    other_products_data['产品名称'],
                    other_products_data['实际销量'].astype(int),  # 转换为整数
                    other_products_data['预测销量'].astype(int),  # 转换为整数
                    other_products_data['差异量'].astype(int),   # 转换为整数
                    other_products_data['差异率'],
                    other_products_data['销售占比'],
                    other_products_data['准确率'] * 100,
                    other_products_data['改进建议']
                )),
                hovertemplate="<b>📦 %{customdata[0]}</b><br>" +
                              "实际: %{customdata[1]:,}箱<br>" +  # 整数显示
                              "预测: %{customdata[2]:,}箱<br>" +  # 整数显示
                              "准确率: %{customdata[6]:.1f}%<br>" +
                              "<extra></extra>",
                name="其他产品",
                legendgroup="other"
            ))

        # 添加完美预测线 (y=x)
        max_val = max(product_analysis['实际销量'].max(), product_analysis['预测销量'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(dash='dash', color='gray', width=2),
            name='完美预测线',
            hoverinfo='skip',
            showlegend=True
        ))

        # 在图表右侧添加区域准确率排名的注释 - 保持原位置
        region_text = "<b>🌍 区域准确率排行</b><br>"
        for i, row in region_analysis.iterrows():
            color = "🟢" if row['准确率'] > 0.85 else "🟡" if row['准确率'] > 0.75 else "🔴"
            region_text += f"{color} {row['所属区域']}: {row['准确率']:.1%}<br>"

        fig.add_annotation(
            x=0.98,
            y=0.25,
            xref='paper',
            yref='paper',
            text=region_text,
            showarrow=False,
            align='left',
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11)
        )

        # 更新布局 - 调整图例到左上角
        fig.update_layout(
            title=dict(
                text=f"销售预测准确性全景分析 - {datetime.now().year}年数据<br><sub>气泡大小=销售占比 | 颜色=准确率 | 重点SKU(占销售额80%)突出显示</sub>",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="实际销量 (箱)",
            yaxis_title="预测销量 (箱)",
            height=700,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,  # 移动到左上角
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='gray',
                borderwidth=1,
                font=dict(size=10)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter"
            ),
            paper_bgcolor='rgba(255,255,255,0.98)',
            plot_bgcolor='rgba(255,255,255,0.98)',
            margin=dict(l=20, r=20, t=100, b=20)
        )

        return fig

    except Exception as e:
        st.error(f"预测分析图表创建失败: {str(e)}")
        return go.Figure()


# 替换原有的 create_key_sku_ranking_chart 函数
# 替换原有的 create_key_sku_ranking_chart 函数
def create_key_sku_ranking_chart(merged_data, product_name_map, selected_region='全国'):
    """创建重点SKU准确率排行图表 - 修复箱数格式"""
    try:
        # 根据选择的区域筛选数据
        if selected_region != '全国':
            filtered_data = merged_data[merged_data['所属区域'] == selected_region]
            title_suffix = f" - {selected_region}区域"
        else:
            filtered_data = merged_data
            title_suffix = " - 全国"

        if filtered_data.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"重点SKU预测准确率排行榜{title_suffix}<br><sub>暂无数据</sub>",
                annotations=[
                    dict(
                        text="该区域暂无数据",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        xanchor='center', yanchor='middle',
                        font=dict(size=20, color="gray")
                    )
                ]
            )
            return fig

        # 产品级别分析
        product_sales = filtered_data.groupby(['产品代码', '产品名称']).agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index()

        product_sales['销售额占比'] = (product_sales['实际销量'] / product_sales['实际销量'].sum() * 100)
        product_sales = product_sales.sort_values('实际销量', ascending=False)
        product_sales['累计占比'] = product_sales['销售额占比'].cumsum()

        # 筛选出占比80%的重点SKU
        key_skus = product_sales[product_sales['累计占比'] <= 80.0].copy()
        key_skus['准确率'] = key_skus['准确率'] * 100
        key_skus['差异量'] = key_skus['实际销量'] - key_skus['预测销量']
        key_skus['差异率'] = (key_skus['差异量'] / key_skus['实际销量'].fillna(1)) * 100
        key_skus = key_skus.sort_values('准确率', ascending=True)

        # 创建水平条形图
        fig = go.Figure()

        # 根据准确率设置颜色
        colors = key_skus['准确率'].apply(
            lambda x: '#006400' if x >= 90 else '#90EE90' if x >= 85 else '#FFA500' if x >= 75 else '#FF6B6B'
        )

        # 添加准确率条形
        fig.add_trace(go.Bar(
            y=key_skus['产品名称'],
            x=key_skus['准确率'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            ),
            text=key_skus.apply(lambda x: f"{x['准确率']:.1f}%", axis=1),
            textposition='outside',
            textfont=dict(size=11, color='black'),
            hovertemplate="<b>%{y}</b><br>" +
                          "准确率: %{x:.1f}%<br>" +
                          "实际销量: %{customdata[0]:,}箱<br>" +  # 整数显示
                          "预测销量: %{customdata[1]:,}箱<br>" +  # 整数显示
                          "销售占比: %{customdata[2]:.2f}%<br>" +
                          "差异量: %{customdata[3]:+,}箱<br>" +  # 整数显示
                          "差异率: %{customdata[4]:+.1f}%<br>" +
                          "区域: " + selected_region + "<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                key_skus['实际销量'].astype(int),  # 转换为整数
                key_skus['预测销量'].astype(int),  # 转换为整数
                key_skus['销售额占比'],
                key_skus['差异量'].astype(int),  # 转换为整数
                key_skus['差异率']
            ))
        ))

        # 添加参考线但不加注释（注释会在图外添加）
        fig.add_vline(x=85, line_dash="dash", line_color="red", line_width=2)
        fig.add_vline(x=90, line_dash="dot", line_color="green", line_width=2)

        # 计算关键统计信息
        total_skus = len(key_skus)
        avg_accuracy = key_skus['准确率'].mean()
        excellent_count = len(key_skus[key_skus['准确率'] >= 90])
        good_count = len(key_skus[key_skus['准确率'] >= 85])
        poor_count = len(key_skus[key_skus['准确率'] < 75])

        # 创建详细的标题和副标题
        subtitle_text = (f"核心产品占销售额80% (共{total_skus}个) | "
                         f"平均准确率{avg_accuracy:.1f}% | "
                         f"优秀({excellent_count}个) 良好({good_count}个) 待改进({poor_count}个)")

        fig.update_layout(
            title=dict(
                text=f"重点SKU预测准确率排行榜{title_suffix}<br><sub>{subtitle_text}</sub>",
                x=0.5,
                xanchor='center',
                font=dict(size=16)
            ),
            xaxis=dict(
                title="预测准确率 (%)",
                range=[0, max(100, key_skus['准确率'].max() + 15)],
                ticksuffix="%",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)"
            ),
            yaxis=dict(
                title="产品名称",
                automargin=True,
                tickfont=dict(size=10)
            ),
            height=max(500, len(key_skus) * 35),
            margin=dict(l=250, r=220, t=120, b=60),
            showlegend=False,
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='rgba(255,255,255,0.95)',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter"
            )
        )

        # 在图的右侧外部添加区间标记 - 红色文字+线条
        chart_right = max(100, key_skus['准确率'].max() + 5)

        # 添加右侧外部的区间标记文字
        fig.add_annotation(
            x=chart_right + 8,
            y=len(key_skus) * 0.8,
            xref='x',
            yref='y',
            text="<b style='color: #006400;'>🟢 优秀区间</b><br><span style='color: #006400;'>(≥90%)</span>",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#006400',
            arrowwidth=2,
            ax=-20,
            ay=0,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor='#006400',
            borderwidth=1,
            font=dict(size=11, color='#006400')
        )

        fig.add_annotation(
            x=chart_right + 8,
            y=len(key_skus) * 0.6,
            xref='x',
            yref='y',
            text="<b style='color: #228B22;'>🟡 良好区间</b><br><span style='color: #228B22;'>(85-90%)</span>",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#228B22',
            arrowwidth=2,
            ax=-20,
            ay=0,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor='#228B22',
            borderwidth=1,
            font=dict(size=11, color='#228B22')
        )

        fig.add_annotation(
            x=chart_right + 8,
            y=len(key_skus) * 0.4,
            xref='x',
            yref='y',
            text="<b style='color: #FF8C00;'>🟠 需改进</b><br><span style='color: #FF8C00;'>(75-85%)</span>",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#FF8C00',
            arrowwidth=2,
            ax=-20,
            ay=0,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor='#FF8C00',
            borderwidth=1,
            font=dict(size=11, color='#FF8C00')
        )

        fig.add_annotation(
            x=chart_right + 8,
            y=len(key_skus) * 0.2,
            xref='x',
            yref='y',
            text="<b style='color: #DC143C;'>🔴 待优化</b><br><span style='color: #DC143C;'>(<75%)</span>",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#DC143C',
            arrowwidth=2,
            ax=-20,
            ay=0,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor='#DC143C',
            borderwidth=1,
            font=dict(size=11, color='#DC143C')
        )

        return fig

    except Exception as e:
        st.error(f"重点SKU排行图表创建失败: {str(e)}")
        return go.Figure()


def create_product_analysis_chart(merged_data):
    """创建产品预测分析图表 - 修复箱数格式"""
    try:
        # 准备完整的产品分析数据
        all_products = merged_data.groupby(['产品代码', '产品名称']).agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index()

        all_products['准确率'] = all_products['准确率'] * 100
        all_products['差异率'] = (
                    (all_products['实际销量'] - all_products['预测销量']) / all_products['实际销量'] * 100).fillna(0)

        # 创建散点图
        fig = go.Figure()

        # 按准确率分组着色
        all_products['颜色组'] = pd.cut(all_products['准确率'],
                                        bins=[0, 70, 80, 90, 100],
                                        labels=['需改进', '一般', '良好', '优秀'])

        colors = {'需改进': '#FF0000', '一般': '#FFA500', '良好': '#FFFF00', '优秀': '#00FF00'}

        for group, color in colors.items():
            group_data = all_products[all_products['颜色组'] == group]
            if not group_data.empty:
                fig.add_trace(go.Scatter(
                    x=group_data['准确率'],
                    y=group_data['差异率'],
                    mode='markers',
                    name=group,
                    marker=dict(
                        size=np.log1p(group_data['实际销量']) * 2,
                        color=color,
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=group_data['产品名称'],
                    hovertemplate="<b>%{text}</b><br>" +
                                  "准确率: %{x:.1f}%<br>" +
                                  "差异率: %{y:+.1f}%<br>" +
                                  "实际销量: %{customdata[0]:,}箱<br>" +  # 整数显示
                                  "预测销量: %{customdata[1]:,}箱<br>" +  # 整数显示
                                  "<extra></extra>",
                    customdata=np.column_stack((
                        group_data['实际销量'].astype(int),  # 转换为整数
                        group_data['预测销量'].astype(int)   # 转换为整数
                    ))
                ))

        # 添加参考线
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="预测准确")
        fig.add_vline(x=85, line_dash="dash", line_color="gray", annotation_text="目标准确率")

        fig.update_layout(
            title="产品预测准确率与差异率分布<br><sub>气泡大小表示销量规模</sub>",
            xaxis_title="预测准确率 (%)",
            yaxis_title="预测差异率 (%)",
            height=600,
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.95)",
                font_size=12,
                font_family="Inter"
            )
        )

        return fig

    except Exception as e:
        st.error(f"产品分析图表创建失败: {str(e)}")
        return go.Figure()


def create_region_analysis_chart(merged_data):
    """创建区域维度分析图表 - 修复箱数格式"""
    try:
        # 区域汇总
        region_comparison = merged_data.groupby('所属区域').agg({
            '实际销量': 'sum',
            '预测销量': 'sum',
            '准确率': 'mean'
        }).reset_index()

        region_comparison['准确率'] = region_comparison['准确率'] * 100
        region_comparison['销量占比'] = (region_comparison['实际销量'] / region_comparison['实际销量'].sum() * 100)

        # 创建组合图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("区域准确率对比", "区域销量与准确率关系"),
            specs=[[{"type": "bar"}, {"type": "scatter"}]]
        )

        # 1. 条形图 - 修复悬停格式
        region_comparison_sorted = region_comparison.sort_values('准确率', ascending=True)
        fig.add_trace(go.Bar(
            y=region_comparison_sorted['所属区域'],
            x=region_comparison_sorted['准确率'],
            orientation='h',
            marker=dict(
                color=region_comparison_sorted['准确率'],
                colorscale='RdYlGn',
                cmin=70,
                cmax=100
            ),
            text=region_comparison_sorted['准确率'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            customdata=np.column_stack((
                region_comparison_sorted['实际销量'].astype(int),  # 转换为整数
                region_comparison_sorted['预测销量'].astype(int)   # 转换为整数
            )),
            hovertemplate="<b>%{y}</b><br>" +
                          "准确率: %{x:.1f}%<br>" +
                          "实际销量: %{customdata[0]:,}箱<br>" +  # 整数显示
                          "预测销量: %{customdata[1]:,}箱<br>" +  # 整数显示
                          "<extra></extra>"
        ), row=1, col=1)

        # 2. 散点图 - 修复悬停格式
        fig.add_trace(go.Scatter(
            x=region_comparison['实际销量'],
            y=region_comparison['准确率'],
            mode='markers+text',
            marker=dict(
                size=region_comparison['销量占比'] * 3,
                color=region_comparison['准确率'],
                colorscale='RdYlGn',
                cmin=70,
                cmax=100,
                showscale=False
            ),
            text=region_comparison['所属区域'],
            textposition="top center",
            customdata=np.column_stack((
                region_comparison['实际销量'].astype(int),  # 转换为整数
                region_comparison['预测销量'].astype(int),  # 转换为整数
                region_comparison['销量占比']
            )),
            hovertemplate="<b>%{text}</b><br>" +
                          "销量: %{customdata[0]:,}箱<br>" +  # 整数显示
                          "准确率: %{y:.1f}%<br>" +
                          "销量占比: %{customdata[2]:.1f}%<br>" +
                          "预测销量: %{customdata[1]:,}箱<br>" +  # 整数显示
                          "<extra></extra>"
        ), row=1, col=2)

        fig.update_xaxes(title_text="预测准确率 (%)", row=1, col=1)
        fig.update_xaxes(title_text="实际销量 (箱)", row=1, col=2)
        fig.update_yaxes(title_text="准确率 (%)", row=1, col=2)

        fig.update_layout(
            height=500,
            showlegend=False,
            title_text="区域预测表现综合分析",
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.95)",
                font_size=12,
                font_family="Inter"
            )
        )

        return fig

    except Exception as e:
        st.error(f"区域分析图表创建失败: {str(e)}")
        return go.Figure()


# 动画数值显示函数
def animate_metric_value(value, prefix="", suffix="", duration=2000):
    """创建动画数值显示"""
    metric_id = f"metric_{np.random.randint(10000, 99999)}"
    return f"""
    <div class="metric-value" id="{metric_id}">0</div>
    <script>
        (function() {{
            let start = 0;
            let end = {value};
            let duration = {duration};
            let startTime = null;
            let element = document.getElementById('{metric_id}');

            function animateValue(timestamp) {{
                if (!startTime) startTime = timestamp;
                const progress = Math.min((timestamp - startTime) / duration, 1);
                const currentValue = Math.floor(progress * (end - start) + start);
                element.textContent = '{prefix}' + currentValue.toLocaleString() + '{suffix}';

                if (progress < 1) {{
                    requestAnimationFrame(animateValue);
                }}
            }}

            requestAnimationFrame(animateValue);
        }})();
    </script>
    """


# 加载数据
with st.spinner('🔄 正在加载数据...'):
    processed_inventory, shipment_df, forecast_df, metrics, product_name_map = load_and_process_data()

# 页面标题
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📦 智能库存预警分析系统</h1>
    <p class="page-subtitle">数据驱动的库存风险管理与预测分析决策支持平台</p>
</div>
""", unsafe_allow_html=True)

# 处理预测数据
merged_data, forecast_key_metrics = process_forecast_analysis(shipment_df, forecast_df, product_name_map)

# 创建标签页
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 核心指标总览",
    "🎯 风险分布分析",
    "📈 销售预测准确性综合分析",
    "📋 库存积压预警详情"
])

# 标签1：核心指标总览 - 增强动画效果
# 标签1：核心指标总览 - 修复数值格式
with tab1:
    st.markdown("### 🎯 库存管理关键指标")

    # 第一行指标 - 库存相关
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{metrics['total_batches']:,}</div>
                <div class="metric-label">📦 总批次数</div>
                <div class="metric-description">当前库存批次总数</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        health_score = 100 - metrics['high_risk_ratio']
        health_class = "risk-low" if health_score > 80 else "risk-medium" if health_score > 60 else "risk-high"
        st.markdown(f"""
        <div class="metric-card {health_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{health_score:.1f}%</div>
                <div class="metric-label">💚 库存健康度</div>
                <div class="metric-description">{'健康' if health_score > 80 else '需关注' if health_score > 60 else '风险'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">¥{metrics['total_inventory_value']:.1f}M</div>
                <div class="metric-label">💰 库存总价值</div>
                <div class="metric-description">全部库存价值统计</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        risk_class = "risk-extreme" if metrics['high_risk_ratio'] > 25 else "risk-high" if metrics[
                                                                                               'high_risk_ratio'] > 15 else "risk-medium"
        st.markdown(f"""
        <div class="metric-card {risk_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{metrics['high_risk_ratio']:.1f}%</div>
                <div class="metric-label">⚠️ 高风险占比</div>
                <div class="metric-description">需要紧急处理的批次</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 第二行指标 - 预测准确性相关（修复箱数格式）
    st.markdown("### 🎯 预测准确性关键指标")
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        actual_sales = int(forecast_key_metrics.get('total_actual_sales', 0))  # 转换为整数
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{actual_sales:,}</div>
                <div class="metric-label">📊 实际销量</div>
                <div class="metric-description">{datetime.now().year}年总销量(箱)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        forecast_sales = int(forecast_key_metrics.get('total_forecast_sales', 0))  # 转换为整数
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{forecast_sales:,}</div>
                <div class="metric-label">🎯 预测销量</div>
                <div class="metric-description">{datetime.now().year}年总预测(箱)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        overall_acc = forecast_key_metrics.get('overall_accuracy', 0)
        accuracy_class = "risk-low" if overall_acc > 85 else "risk-medium" if overall_acc > 75 else "risk-high"
        st.markdown(f"""
        <div class="metric-card {accuracy_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{overall_acc:.1f}%</div>
                <div class="metric-label">🎯 整体准确率</div>
                <div class="metric-description">全国预测精度</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        diff_rate = forecast_key_metrics.get('overall_diff_rate', 0)
        diff_class = "risk-low" if abs(diff_rate) < 5 else "risk-medium" if abs(diff_rate) < 15 else "risk-high"
        st.markdown(f"""
        <div class="metric-card {diff_class}">
            <div class="metric-card-inner">
                <div class="metric-value">{diff_rate:+.1f}%</div>
                <div class="metric-label">📊 整体差异率</div>
                <div class="metric-description">{'预测偏高' if diff_rate < 0 else '预测偏低' if diff_rate > 0 else '预测准确'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 标签2：风险分布分析
# 标签2：风险分布分析
# 标签2：风险分布分析 - 整合统计分析
# 标签2：风险分布分析 - 修复版本
# 标签2：风险分布分析 - 重构版本使用子标签
# 标签2：风险分布分析 - 修复版本，删除深度统计洞察子标签
# 标签2：风险分布分析 - 修复函数调用错误
with tab2:
    st.markdown("### 🎯 库存风险分布综合分析")

    # 创建子标签页进行分类展示 - 只保留3个子标签
    risk_tab1, risk_tab2, risk_tab3 = st.tabs([
        "📊 风险分布全景",
        "📦 产品维度分析",
        "🌍 区域维度分析"
    ])

    # 子标签1：风险分布全景
    with risk_tab1:
        st.markdown("#### 🎯 库存风险分布全景分析")

        # 原有的风险分析图表 - 优化悬停
        integrated_fig = create_integrated_risk_analysis_optimized(processed_inventory)
        st.plotly_chart(integrated_fig, use_container_width=True)

        # 风险分析洞察
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">📊 综合风险分析洞察</div>
            <div class="insight-content">
                • 极高风险: {metrics['risk_counts']['extreme']}个批次 ({metrics['risk_counts']['extreme'] / max(metrics['total_batches'], 1) * 100:.1f}%)<br>
                • 高风险: {metrics['risk_counts']['high']}个批次 ({metrics['risk_counts']['high'] / max(metrics['total_batches'], 1) * 100:.1f}%)<br>
                • 高风险批次价值占比: {metrics['high_risk_value_ratio']:.1f}%<br>
                • 建议优先处理极高风险和高风险批次，通过促销可回收资金: ¥{metrics['high_risk_value'] * 0.8:.1f}M
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 子标签2：产品维度分析
    with risk_tab2:
        st.markdown("#### 📦 产品维度风险分析")

        if not processed_inventory.empty:
            # 检查实际存在的列名
            available_columns = processed_inventory.columns.tolist()

            # 使用实际存在的列名进行聚合
            agg_dict = {}
            if '数量' in available_columns:
                agg_dict['数量'] = 'sum'
            elif '批次库存' in available_columns:
                agg_dict['批次库存'] = 'sum'

            if '批次价值' in available_columns:
                agg_dict['批次价值'] = 'sum'

            if '库龄' in available_columns:
                agg_dict['库龄'] = 'mean'

            if '风险得分' in available_columns:
                agg_dict['风险得分'] = 'mean'

            if '日均出货' in available_columns:
                agg_dict['日均出货'] = 'mean'

            if '风险等级' in available_columns:
                agg_dict['风险等级'] = lambda x: x.mode()[0] if not x.empty else '未知'

            if '积压原因' in available_columns:
                agg_dict['积压原因'] = lambda x: '，'.join(x.unique()[:3])

            if '责任区域' in available_columns:
                agg_dict['责任区域'] = lambda x: x.mode()[0] if not x.empty else '未知'

            if '物料' in available_columns:
                agg_dict['物料'] = 'first'
            elif '产品代码' in available_columns:
                agg_dict['产品代码'] = 'first'

            # 执行聚合操作
            try:
                product_stats = processed_inventory.groupby('产品名称').agg(agg_dict).round(2)

                # 统一列名处理
                if '数量' in product_stats.columns:
                    product_stats = product_stats.rename(columns={'数量': '批次库存'})
                if '物料' in product_stats.columns:
                    product_stats = product_stats.rename(columns={'物料': '产品代码'})

                # 计算衍生指标
                if '批次库存' in product_stats.columns and '日均出货' in product_stats.columns:
                    product_stats['预计清库天数'] = product_stats['批次库存'] / product_stats['日均出货'].replace(0,
                                                                                                                  0.1)
                    product_stats['库存周转率'] = 365 / product_stats['预计清库天数'].replace([np.inf, -np.inf], 365)

                if '批次价值' in product_stats.columns:
                    product_stats['价值占比'] = product_stats['批次价值'] / product_stats['批次价值'].sum() * 100
                    product_stats = product_stats.sort_values('批次价值', ascending=False)

                # 创建优化的产品分析图表
                fig_product = create_product_analysis_fixed_final(product_stats)
                st.plotly_chart(fig_product, use_container_width=True)

            except Exception as e:
                st.error(f"产品统计分析失败: {str(e)}")
                st.info("正在显示基础统计信息...")
                st.write("可用列名:", processed_inventory.columns.tolist())

        else:
            st.info("暂无产品数据进行分析")

    # 子标签3：区域维度分析
    with risk_tab3:
        st.markdown("#### 🌍 区域库存风险分析")

        if not processed_inventory.empty and '责任区域' in processed_inventory.columns:
            # 使用实际存在的列名进行区域分析
            region_agg_dict = {}
            if '数量' in processed_inventory.columns:
                region_agg_dict['数量'] = 'sum'
            elif '批次库存' in processed_inventory.columns:
                region_agg_dict['批次库存'] = 'sum'

            if '批次价值' in processed_inventory.columns:
                region_agg_dict['批次价值'] = 'sum'
            if '库龄' in processed_inventory.columns:
                region_agg_dict['库龄'] = 'mean'
            if '风险得分' in processed_inventory.columns:
                region_agg_dict['风险得分'] = 'mean'
            if '产品名称' in processed_inventory.columns:
                region_agg_dict['产品名称'] = 'nunique'
            if '日均出货' in processed_inventory.columns:
                region_agg_dict['日均出货'] = 'mean'
            if '积压原因' in processed_inventory.columns:
                region_agg_dict['积压原因'] = lambda x: '，'.join(pd.Series(x).value_counts().head(3).index)

            try:
                region_stats = processed_inventory.groupby('责任区域').agg(region_agg_dict).round(2)

                # 统一列名
                if '数量' in region_stats.columns:
                    region_stats = region_stats.rename(columns={'数量': '批次库存'})

                # 计算每个区域的风险等级分布
                region_risk_details = {}
                for region in region_stats.index:
                    region_data = processed_inventory[processed_inventory['责任区域'] == region]
                    if '风险等级' in processed_inventory.columns:
                        risk_counts = region_data['风险等级'].value_counts().to_dict()
                    else:
                        risk_counts = {}
                    region_risk_details[region] = risk_counts

                # 创建区域分析图表 - 修复函数名
                create_region_analysis_fixed_final(region_stats, region_risk_details)

            except Exception as e:
                st.error(f"区域分析失败: {str(e)}")

        else:
            st.info("暂无区域数据或责任区域列不存在")

# 标签3：销售预测准确性综合分析 - 纯图表版本
# 标签3：销售预测准确性综合分析 - 删除统计卡片和表格
with tab3:
    st.markdown(f"### 📈 销售预测准确性综合分析 - {datetime.now().year}年数据")

    if merged_data is not None and not merged_data.empty:
        # 创建子标签页进行多维度分析
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
            "🎯 预测准确性全景图",
            "🏆 重点SKU准确率排行",
            "📊 产品预测详细分析",
            "🌍 区域维度深度分析"
        ])

        # 子标签1：预测准确性全景图
        with sub_tab1:
            # 直接显示超级整合图表
            ultra_fig = create_ultra_integrated_forecast_chart(merged_data)
            st.plotly_chart(ultra_fig, use_container_width=True)

            # 改进建议
            overall_acc = forecast_key_metrics.get('overall_accuracy', 0)
            diff_rate = forecast_key_metrics.get('overall_diff_rate', 0)

            # 计算重点SKU数量
            total_sales_by_product = merged_data.groupby(['产品代码', '产品名称'])['实际销量'].sum().reset_index()
            total_sales_by_product = total_sales_by_product.sort_values('实际销量', ascending=False)
            total_sales = total_sales_by_product['实际销量'].sum()
            total_sales_by_product['累计占比'] = total_sales_by_product['实际销量'].cumsum() / total_sales
            key_products_count = len(total_sales_by_product[total_sales_by_product['累计占比'] <= 0.8])

            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">💡 预测准确性深度洞察</div>
                <div class="insight-content">
                    • <b>整体表现:</b> 预测准确率{overall_acc:.1f}%，{'已达到优秀水平' if overall_acc >= 85 else '距离85%目标还有' + f'{85 - overall_acc:.1f}%提升空间'}<br>
                    • <b>重点SKU:</b> {key_products_count}个产品贡献80%销售额，是预测精度提升的关键focus<br>
                    • <b>预测偏差:</b> 整体{'预测偏高' if diff_rate < 0 else '预测偏低' if diff_rate > 0 else '预测相对准确'}，差异率{abs(diff_rate):.1f}%<br>
                    • <b>改进方向:</b> 重点关注图中大气泡低准确率(红色)产品，优化其预测模型和参数<br>
                    • <b>区域差异:</b> 各区域预测能力存在差异，建议针对性培训和经验分享
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 子标签2：重点SKU准确率排行 - 修复雷达图中的箱数格式
            with sub_tab2:
                st.markdown("#### 🏆 销售额占比80%的重点SKU准确率排行")

                # 创建区域筛选器
                col1, col2 = st.columns([2, 8])
                with col1:
                    all_regions = ['全国'] + list(merged_data['所属区域'].unique())
                    selected_region_sku = st.selectbox(
                        "选择区域",
                        options=all_regions,
                        index=0,
                        key="sku_region_filter"
                    )

                # 创建重点SKU排行图表
                key_sku_fig = create_key_sku_ranking_chart(merged_data, product_name_map, selected_region_sku)
                st.plotly_chart(key_sku_fig, use_container_width=True)

                # 区域对比视图
                st.markdown("##### 🌍 各区域重点SKU对比")

                # 创建区域选择器
                regions = merged_data['所属区域'].unique()
                selected_regions = st.multiselect("选择要对比的区域", options=regions, default=list(regions[:3]))

                if selected_regions:
                    # 创建区域对比雷达图 - 修复箱数格式
                    fig_radar = go.Figure()

                    for region in selected_regions:
                        region_data = merged_data[merged_data['所属区域'] == region]
                        region_products = region_data.groupby(['产品代码', '产品名称']).agg({
                            '实际销量': 'sum',
                            '预测销量': 'sum',
                            '准确率': 'mean'
                        }).reset_index()

                        region_products['销售额占比'] = (
                                region_products['实际销量'] / region_products['实际销量'].sum() * 100)
                        region_products = region_products.sort_values('实际销量', ascending=False)
                        region_products['累计占比'] = region_products['销售额占比'].cumsum()

                        # 获取该区域的重点SKU
                        key_skus = region_products[region_products['累计占比'] <= 80.0]

                        # 计算各项指标
                        metrics = {
                            '平均准确率': key_skus['准确率'].mean() * 100,
                            'SKU数量': len(key_skus),
                            '销量集中度': 80 / len(key_skus) if len(key_skus) > 0 else 0,
                            '预测稳定性': (1 - key_skus['准确率'].std()) * 100 if len(key_skus) > 1 else 100
                        }

                        # 计算额外的统计数据 - 修复箱数格式
                        total_actual = int(key_skus['实际销量'].sum())  # 转换为整数
                        total_forecast = int(key_skus['预测销量'].sum())  # 转换为整数
                        top3_skus = key_skus.head(3)['产品名称'].tolist()
                        accuracy_range = f"{key_skus['准确率'].min() * 100:.1f}% - {key_skus['准确率'].max() * 100:.1f}%"

                        # 创建自定义悬停文本 - 修复箱数格式
                        hover_text = [
                            f"<b>{region} - 平均准确率</b><br>值: {metrics['平均准确率']:.1f}%<br>范围: {accuracy_range}<br>TOP3 SKU: {', '.join(top3_skus[:3])}",
                            f"<b>{region} - SKU多样性</b><br>重点SKU数: {len(key_skus)}<br>总SKU数: {len(region_products)}<br>占比: {len(key_skus) / len(region_products) * 100:.1f}%",
                            f"<b>{region} - 销量集中度</b><br>值: {metrics['销量集中度']:.1f}<br>说明: 平均每个SKU贡献{metrics['销量集中度']:.1f}%销售额<br>实际总销量: {total_actual:,}箱",
                            # 整数显示
                            f"<b>{region} - 预测稳定性</b><br>值: {metrics['预测稳定性']:.1f}%<br>说明: 预测准确率的一致性程度<br>预测总量: {total_forecast:,}箱"
                            # 整数显示
                        ]

                        fig_radar.add_trace(go.Scatterpolar(
                            r=[metrics['平均准确率'], metrics['SKU数量'] * 2,
                               metrics['销量集中度'], metrics['预测稳定性']],
                            theta=['平均准确率', 'SKU多样性', '销量集中度', '预测稳定性'],
                            fill='toself',
                            name=region,
                            hovertext=hover_text,
                            hoverinfo="text"
                        ))

                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=True,
                        title="区域重点SKU综合表现对比<br><sub>悬停查看详细计算结果</sub>",
                        height=500
                    )

                    st.plotly_chart(fig_radar, use_container_width=True)

        # 子标签3：产品预测详细分析 - 使用图表
        with sub_tab3:
            st.markdown("#### 📊 全国产品预测表现分析")

            # 创建产品分析图表
            product_fig = create_product_analysis_chart(merged_data)
            st.plotly_chart(product_fig, use_container_width=True)

            # 产品表现分布统计
            all_products = merged_data.groupby(['产品代码', '产品名称']).agg({
                '实际销量': 'sum',
                '预测销量': 'sum',
                '准确率': 'mean'
            }).reset_index()

            all_products['准确率'] = all_products['准确率'] * 100

            # 创建准确率分布直方图
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=all_products['准确率'],
                nbinsx=20,
                marker_color='rgba(102, 126, 234, 0.7)',
                name='产品数量'
            ))

            fig_hist.add_vline(x=85, line_dash="dash", line_color="red",
                               annotation_text="目标准确率:85%")
            fig_hist.add_vline(x=all_products['准确率'].mean(), line_dash="dash",
                               line_color="green", annotation_text=f"平均准确率:{all_products['准确率'].mean():.1f}%")

            fig_hist.update_layout(
                title="产品预测准确率分布",
                xaxis_title="准确率 (%)",
                yaxis_title="产品数量",
                height=400,
                bargap=0.1
            )

            st.plotly_chart(fig_hist, use_container_width=True)

        # 子标签4：区域维度深度分析 - 使用图表
            # 子标签4：区域维度深度分析 - 使用图表
            # 子标签4：区域维度深度分析 - 使用图表
            # 子标签4：区域维度深度分析 - 使用图表
            # 子标签4：区域维度深度分析 - 使用图表
            with sub_tab4:
                st.markdown("#### 🌍 区域维度预测准确性深度分析")

                # 创建升级版区域分析图表 - 总结信息已移至悬停中
                enhanced_region_fig, region_comparison_data = create_enhanced_region_forecast_chart(merged_data)

                # 全宽显示图表（移除了右侧总结框）
                st.plotly_chart(enhanced_region_fig, use_container_width=True)

                # 区域表现热力图
                if not merged_data.empty:
                    # 准备数据
                    region_product_matrix = merged_data.pivot_table(
                        values='准确率',
                        index='所属区域',
                        columns='产品名称',
                        aggfunc='mean'
                    ) * 100

                    # 选择前10个产品显示
                    top_products = merged_data.groupby('产品名称')['实际销量'].sum().nlargest(10).index
                    region_product_matrix = region_product_matrix[top_products]

                    # 创建热力图
                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=region_product_matrix.values,
                        x=region_product_matrix.columns,
                        y=region_product_matrix.index,
                        colorscale='RdYlGn',
                        zmid=85,
                        text=region_product_matrix.values.round(1),
                        texttemplate='%{text}%',
                        textfont={"size": 10},
                        hovertemplate="<b>%{y} - %{x}</b><br>准确率: %{z:.1f}%<br><extra></extra>"
                    ))

                    fig_heatmap.update_layout(
                        title="区域-产品预测准确率热力图<br><sub>显示销量前10产品</sub>",
                        xaxis_title="产品名称",
                        yaxis_title="区域",
                        height=500
                    )

                    st.plotly_chart(fig_heatmap, use_container_width=True)


with tab4:
    st.markdown("### 📋 库存积压预警详情分析")

    if not processed_inventory.empty:
        # 筛选控件 - 与积压超详细.py保持一致
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            risk_filter = st.selectbox(
                "风险等级",
                options=['全部'] + list(processed_inventory['风险等级'].unique()),
                index=0
            )

        with col2:
            product_filter = st.selectbox(
                "产品",
                options=['全部'] + list(processed_inventory['产品名称'].unique()),
                index=0
            )

        with col3:
            min_value = st.number_input(
                "最小批次价值",
                min_value=0,
                max_value=int(processed_inventory['批次价值'].max()),
                value=0
            )

        with col4:
            max_age = st.number_input(
                "最大库龄(天)",
                min_value=0,
                max_value=int(processed_inventory['库龄'].max()),
                value=int(processed_inventory['库龄'].max())
            )

        # 应用筛选
        filtered_data = processed_inventory.copy()

        if risk_filter != '全部':
            filtered_data = filtered_data[filtered_data['风险等级'] == risk_filter]

        if product_filter != '全部':
            filtered_data = filtered_data[filtered_data['产品名称'] == product_filter]

        filtered_data = filtered_data[
            (filtered_data['批次价值'] >= min_value) &
            (filtered_data['库龄'] <= max_age)
            ]

        # 显示筛选结果统计信息
        if not filtered_data.empty:
            st.markdown(f"#### 📋 批次分析明细表 (共{len(filtered_data)}条记录)")

            # 风险程度排序：极高风险排第一，以此类推
            risk_order = {
                '极高风险': 1,
                '高风险': 2,
                '中风险': 3,
                '低风险': 4,
                '极低风险': 5
            }
            filtered_data['风险排序'] = filtered_data['风险程度'].map(risk_order)
            filtered_data = filtered_data.sort_values('风险排序')

            # 准备显示的列 - 完全按照积压超详细.py的字段顺序
            display_columns = [
                '风险程度',  # 第一列
                '一个月积压风险', '两个月积压风险', '三个月积压风险',  # 积压风险字段
                '物料', '描述', '批次日期', '批次库存', '库龄', '批次价值',
                '日均出货', '出货波动系数', '预计清库天数',
                '积压原因', '季节性指数', '预测偏差',
                '责任区域', '责任人', '责任分析摘要',
                '风险得分', '建议措施'
            ]

            # 格式化显示数据
            display_data = filtered_data[display_columns].copy()

            # 删除临时的风险排序列
            if '风险排序' in display_data.columns:
                display_data = display_data.drop('风险排序', axis=1)

            # 格式化数值列 - 与积压超详细.py保持一致
            display_data['批次价值'] = display_data['批次价值'].apply(lambda x: f"¥{x:,.0f}")
            display_data['批次日期'] = display_data['批次日期'].astype(str)
            display_data['库龄'] = display_data['库龄'].apply(lambda x: f"{x}天")
            display_data['日均出货'] = display_data['日均出货'].apply(lambda x: f"{x:.2f}")
            display_data['出货波动系数'] = display_data['出货波动系数'].apply(lambda x: f"{x:.2f}")
            display_data['预计清库天数'] = display_data['预计清库天数'].apply(
                lambda x: "∞" if x == float('inf') else f"{x:.1f}天"
            )
            display_data['季节性指数'] = display_data['季节性指数'].apply(lambda x: f"{x:.2f}")
            display_data['批次库存'] = display_data['批次库存'].apply(lambda x: f"{int(x):,}")

            # 美化积压风险字段 - 添加警告图标
            for risk_col in ['一个月积压风险', '两个月积压风险', '三个月积压风险']:
                display_data[risk_col] = display_data[risk_col].apply(
                    lambda x: f"🔴 {x}" if '100.0%' in str(x) or (
                                isinstance(x, str) and float(x.replace('%', '')) > 90) else
                    f"🟠 {x}" if isinstance(x, str) and float(x.replace('%', '')) > 70 else
                    f"🟡 {x}" if isinstance(x, str) and float(x.replace('%', '')) > 50 else
                    f"🟢 {x}"
                )

            # 使用增强样式显示表格
            with st.container():
                st.markdown("""
                <style>
                /* 完整的表格样式 - 与积压超详细.py的Excel输出保持一致 */
                .advanced-table {
                    background: linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.98)) !important;
                    border-radius: 30px !important;
                    overflow: visible !important;
                    box-shadow: 
                        0 30px 60px rgba(0,0,0,0.12),
                        0 15px 30px rgba(0,0,0,0.08),
                        0 5px 15px rgba(0,0,0,0.04),
                        inset 0 2px 4px rgba(255,255,255,0.9) !important;
                    border: 2px solid transparent !important;
                    background-image: 
                        linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.98)),
                        linear-gradient(135deg, #667eea, #764ba2) !important;
                    background-origin: border-box !important;
                    background-clip: padding-box, border-box !important;
                    margin: 2rem 0 !important;
                    position: relative !important;
                }

                /* 风险等级行样式 - 极高风险动画 */
                [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("极高风险")) {
                    background: linear-gradient(90deg, 
                        rgba(139, 0, 0, 0.25) 0%,
                        rgba(139, 0, 0, 0.15) 50%,
                        rgba(139, 0, 0, 0.25) 100%) !important;
                    border-left: 8px solid #8B0000 !important;
                    animation: extremeRiskRowPulse 1.5s ease-in-out infinite !important;
                }

                [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("高风险")):not(:has(td:nth-child(1):contains("极高风险"))) {
                    background: linear-gradient(90deg, 
                        rgba(255, 0, 0, 0.18) 0%,
                        rgba(255, 0, 0, 0.10) 50%,
                        rgba(255, 0, 0, 0.18) 100%) !important;
                    border-left: 6px solid #FF0000 !important;
                    animation: highRiskRowGlow 2s ease-in-out infinite !important;
                }

                [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("中风险")) {
                    background: linear-gradient(90deg, rgba(255, 165, 0, 0.12), rgba(255, 165, 0, 0.06)) !important;
                    border-left: 4px solid #FFA500 !important;
                }

                /* 风险等级单元格样式 */
                [data-testid="stDataFrame"] tbody td:nth-child(1):contains("极高风险") {
                    background: linear-gradient(135deg, #8B0000 0%, #660000 50%, #4B0000 100%) !important;
                    color: white !important;
                    font-weight: 900 !important;
                    border-radius: 15px !important;
                    padding: 1rem 1.5rem !important;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
                    text-transform: uppercase !important;
                    letter-spacing: 1px !important;
                }

                [data-testid="stDataFrame"] tbody td:nth-child(1):contains("高风险"):not(:contains("极高风险")) {
                    background: linear-gradient(135deg, #FF0000 0%, #CC0000 50%, #990000 100%) !important;
                    color: white !important;
                    font-weight: 800 !important;
                    border-radius: 12px !important;
                    padding: 0.9rem 1.4rem !important;
                    text-shadow: 0 2px 3px rgba(0,0,0,0.3) !important;
                    text-transform: uppercase !important;
                }

                [data-testid="stDataFrame"] tbody td:nth-child(1):contains("中风险") {
                    background: linear-gradient(135deg, #FFA500 0%, #FF8C00 50%, #FF7F00 100%) !important;
                    color: white !important;
                    font-weight: 700 !important;
                    border-radius: 10px !important;
                    padding: 0.8rem 1.2rem !important;
                }

                /* 积压风险列样式 */
                [data-testid="stDataFrame"] tbody td:nth-child(2):contains("🔴"),
                [data-testid="stDataFrame"] tbody td:nth-child(3):contains("🔴"),
                [data-testid="stDataFrame"] tbody td:nth-child(4):contains("🔴") {
                    animation: riskIndicatorPulse 2s ease-in-out infinite;
                    font-weight: 700 !important;
                    background: rgba(220, 20, 60, 0.1) !important;
                    border-radius: 8px;
                }

                @keyframes extremeRiskRowPulse {
                    0%, 100% {
                        box-shadow: 0 0 0 0 rgba(139, 0, 0, 0.8);
                    }
                    50% {
                        box-shadow: 0 0 0 20px rgba(139, 0, 0, 0);
                    }
                }

                @keyframes highRiskRowGlow {
                    0%, 100% {
                        box-shadow: 0 0 15px rgba(255, 0, 0, 0.4);
                    }
                    50% {
                        box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
                    }
                }

                @keyframes riskIndicatorPulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown('<div class="advanced-table">', unsafe_allow_html=True)

                # 显示数据表格 - 与积压超详细.py的输出格式完全一致
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    height=600,
                    hide_index=False
                )

                # 下载按钮
                csv = display_data.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 导出完整报告",
                    data=csv,
                    file_name=f"批次库存积压预警报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                st.markdown('</div>', unsafe_allow_html=True)

            # 显示统计汇总信息 - 与积压超详细.py保持一致
            st.markdown("#### 📊 批次风险统计汇总")

            col1, col2, col3, col4 = st.columns(4)

            risk_stats = filtered_data['风险程度'].value_counts()
            total_value = filtered_data['批次价值'].sum()

            with col1:
                extreme_count = risk_stats.get('极高风险', 0)
                st.metric(
                    label="🔴 极高风险批次",
                    value=f"{extreme_count}个",
                    delta=f"{extreme_count / len(filtered_data) * 100:.1f}%" if len(filtered_data) > 0 else "0%"
                )

            with col2:
                high_count = risk_stats.get('高风险', 0)
                st.metric(
                    label="🟠 高风险批次",
                    value=f"{high_count}个",
                    delta=f"{high_count / len(filtered_data) * 100:.1f}%" if len(filtered_data) > 0 else "0%"
                )

            with col3:
                high_risk_value = filtered_data[
                    filtered_data['风险程度'].isin(['极高风险', '高风险'])
                ]['批次价值'].sum()
                st.metric(
                    label="💰 高风险批次价值",
                    value=f"¥{high_risk_value / 10000:.1f}万",
                    delta=f"{high_risk_value / total_value * 100:.1f}%" if total_value > 0 else "0%"
                )

            with col4:
                avg_age = filtered_data['库龄'].mean()
                st.metric(
                    label="📅 平均库龄",
                    value=f"{avg_age:.0f}天",
                    delta="需关注" if avg_age > 60 else "正常"
                )

        else:
            st.info("暂无符合筛选条件的数据")

    else:
        st.info("暂无库存数据")

# 页脚
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: rgba(102, 126, 234, 0.8); font-family: 'Inter', sans-serif; font-size: 0.9rem; margin-top: 2rem; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
        🚀 Powered by Streamlit & Plotly | 智能数据分析平台 | 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """,
    unsafe_allow_html=True
)
