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
class BatchLevelInventoryAnalyzer:
    """批次级别库存分析器 - 移植自附件一的核心逻辑"""

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
def load_and_process_data():
    """加载和处理所有数据 - 增强版本包含批次分析"""
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

        # 创建产品代码到名称的映射
        product_name_map = {}
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and pd.notna(row['描述']) and isinstance(row['物料'], str) and row[
                '物料'].startswith('F'):
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
            else:
                forecast_bias = 0.0

            forecast_accuracy[product_code] = {
                'forecast_bias': forecast_bias
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
                forecast_info = forecast_accuracy.get(current_material, {'forecast_bias': 0.0})

                # 计算日均出货（考虑季节性）
                daily_avg_sales = sales_metrics['daily_avg_sales']
                daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, analyzer.min_daily_sales)

                # 计算预计清库天数
                if daily_avg_sales_adjusted > 0:
                    days_to_clear = quantity / daily_avg_sales_adjusted

                    # 计算积压风险
                    one_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 30)
                    two_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 60)
                    three_month_risk = analyzer.calculate_risk_percentage(days_to_clear, age_days, 90)
                else:
                    days_to_clear = float('inf')
                    one_month_risk = 100
                    two_month_risk = 100
                    three_month_risk = 100

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

                # 确定风险等级和得分
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
                    risk_color = COLOR_SCHEME['risk_extreme']
                    risk_advice = '🚨 立即7折清库'
                elif risk_score >= 60:
                    risk_level = "高风险"
                    risk_color = COLOR_SCHEME['risk_high']
                    risk_advice = '⚠️ 建议8折促销'
                elif risk_score >= 40:
                    risk_level = "中风险"
                    risk_color = COLOR_SCHEME['risk_medium']
                    risk_advice = '📢 适度9折促销'
                elif risk_score >= 20:
                    risk_level = "低风险"
                    risk_color = COLOR_SCHEME['risk_low']
                    risk_advice = '✅ 正常销售'
                else:
                    risk_level = "极低风险"
                    risk_color = COLOR_SCHEME['risk_minimal']
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
                    expected_loss = quantity * current_price * 0.3
                elif age_days >= 90:
                    expected_loss = quantity * current_price * 0.2
                elif age_days >= 60:
                    expected_loss = quantity * current_price * 0.1
                else:
                    expected_loss = 0

                # 简化责任分析（基于出货数据的区域和申请人）
                responsible_region = analyzer.default_region
                responsible_person = analyzer.default_person

                # 查找该产品最近的出货记录
                recent_shipments = shipment_df[
                    (shipment_df['产品代码'] == current_material) &
                    (shipment_df['订单日期'].dt.date >= (datetime.now().date() - timedelta(days=90)))
                    ]

                if not recent_shipments.empty:
                    # 找出最频繁的区域和申请人
                    region_counts = recent_shipments['所属区域'].value_counts()
                    person_counts = recent_shipments['申请人'].value_counts()

                    if not region_counts.empty:
                        responsible_region = region_counts.index[0]
                    if not person_counts.empty:
                        responsible_person = person_counts.index[0]

                # 构建批次数据
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
                    '风险颜色': risk_color,
                    '处理建议': risk_advice,
                    '单价': current_price,
                    '批次价值': quantity * current_price,
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
                    '预测偏差': f"{round(forecast_info['forecast_bias'] * 100, 1)}%",
                    '责任区域': responsible_region,
                    '责任人': responsible_person,
                    '责任分析摘要': f"{responsible_person}主要责任({responsible_region}区域)",
                    '风险程度': risk_level,
                    '风险得分': risk_score,
                    '建议措施': recommendation
                })

        processed_inventory = pd.DataFrame(batch_data)

        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory)

        return processed_inventory, shipment_df, forecast_df, metrics, product_name_map

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, {}


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

        # 更新布局
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="库存风险综合分析",
            title_x=0.5,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter"
            ),
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


def create_ultra_integrated_forecast_chart(merged_data):
    """创建超级整合的预测分析图表 - 增强版本带高级悬停和交互"""
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

        # 创建超级整合图表 - 使用1个大图显示所有信息
        fig = go.Figure()

        # 重点SKU
        key_products_data = product_analysis[product_analysis['是否重点SKU']]
        if not key_products_data.empty:
            fig.add_trace(go.Scatter(
                x=key_products_data['实际销量'],
                y=key_products_data['预测销量'],
                mode='markers',
                marker=dict(
                    size=key_products_data['销售占比'] * 2,  # 按销售占比调整大小
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
                    key_products_data['实际销量'],
                    key_products_data['预测销量'],
                    key_products_data['差异量'],
                    key_products_data['差异率'],
                    key_products_data['销售占比'],
                    key_products_data['准确率'] * 100,
                    key_products_data['改进建议'],
                    key_products_data['产品代码']
                )),
                hovertemplate="""
                <b>🎯 重点SKU: %{customdata[0]}</b><br>
                <b>产品代码: %{customdata[8]}</b><br>
                <br>
                <b>📊 销量对比</b><br>
                实际销量: <b>%{customdata[1]:,.0f}</b>箱<br>
                预测销量: <b>%{customdata[2]:,.0f}</b>箱<br>
                差异量: <span style="color: %{customdata[3]:+.0f < 0 ? 'red' : 'green'};">%{customdata[3]:+,.0f}箱</span><br>
                <br>
                <b>📈 准确性分析</b><br>
                预测准确率: <b style="color: %{customdata[6]:.1f > 85 ? 'green' : customdata[6]:.1f > 75 ? 'orange' : 'red'};">%{customdata[6]:.1f}%</b><br>
                预测差异率: %{customdata[4]:+.1f}%<br>
                销售占比: <b>%{customdata[5]:.1f}%</b><br>
                <br>
                <b>💡 改进建议</b><br>
                %{customdata[7]}<br>
                <extra></extra>
                """,
                name="重点SKU (占销售额80%)",
                legendgroup="key"
            ))

        # 其他产品
        other_products_data = product_analysis[~product_analysis['是否重点SKU']].head(20)  # 只显示前20个其他产品
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
                    other_products_data['实际销量'],
                    other_products_data['预测销量'],
                    other_products_data['差异量'],
                    other_products_data['差异率'],
                    other_products_data['销售占比'],
                    other_products_data['准确率'] * 100,
                    other_products_data['改进建议']
                )),
                hovertemplate="""
                <b>📦 产品: %{customdata[0]}</b><br>
                <br>
                <b>📊 销量对比</b><br>
                实际销量: %{customdata[1]:,.0f}箱<br>
                预测销量: %{customdata[2]:,.0f}箱<br>
                差异量: %{customdata[3]:+,.0f}箱<br>
                <br>
                <b>📈 准确性分析</b><br>
                预测准确率: <b>%{customdata[6]:.1f}%</b><br>
                预测差异率: %{customdata[4]:+.1f}%<br>
                销售占比: %{customdata[5]:.1f}%<br>
                <br>
                <b>💡 建议</b><br>
                %{customdata[7]}<br>
                <extra></extra>
                """,
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

        # 在图表右侧添加区域准确率排名的注释
        region_text = "🌍 <b>区域准确率排行</b><br>"
        for i, row in region_analysis.iterrows():
            color = "🟢" if row['准确率'] > 0.85 else "🟡" if row['准确率'] > 0.75 else "🔴"
            region_text += f"{color} {row['所属区域']}: {row['准确率']:.1%}<br>"

        fig.add_annotation(
            x=0.98,
            y=0.02,
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

        # 在左上角添加重点SKU统计 - 调整位置避免遮挡
        key_sku_text = f"🎯 <b>重点SKU统计</b><br>数量: {len(key_products_data)}个<br>占销售额: 80%<br>平均准确率: {key_products_data['准确率'].mean():.1%}"
        fig.add_annotation(
            x=0.02,
            y=0.95,  # 从0.98调整到0.95，稍微往下移
            xref='paper',
            yref='paper',
            text=key_sku_text,
            showarrow=False,
            align='left',
            bgcolor='rgba(102, 126, 234, 0.1)',
            bordercolor=COLOR_SCHEME['primary'],
            borderwidth=2,
            font=dict(size=11, color=COLOR_SCHEME['primary'])
        )

        # 更新布局 - 调整图例位置避免遮挡
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
                y=0.15,  # 从0.02调整到0.15，往上移避免遮挡坐标轴
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
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
def create_key_sku_ranking_chart(merged_data, product_name_map, selected_region='全国'):
    """创建重点SKU准确率排行图表 - 支持区域筛选"""
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
                title=f"重点SKU准确率排行榜{title_suffix}<br><sub>暂无数据</sub>",
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

        # 添加准确率条形
        fig.add_trace(go.Bar(
            y=key_skus['产品名称'],
            x=key_skus['准确率'],
            orientation='h',
            marker=dict(
                color=key_skus['准确率'],
                colorscale='RdYlGn',
                cmin=60,
                cmax=100,
                colorbar=dict(
                    title="准确率(%)",
                    x=1.02
                )
            ),
            text=key_skus.apply(lambda x: f"{x['准确率']:.1f}%<br>销量:{x['实际销量']:,.0f}", axis=1),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>" +
                          "准确率: %{x:.1f}%<br>" +
                          "实际销量: %{customdata[0]:,.0f}箱<br>" +
                          "预测销量: %{customdata[1]:,.0f}箱<br>" +
                          "销售占比: %{customdata[2]:.2f}%<br>" +
                          "差异量: %{customdata[3]:+,.0f}箱<br>" +
                          "差异率: %{customdata[4]:+.1f}%<br>" +
                          "区域: " + selected_region + "<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                key_skus['实际销量'],
                key_skus['预测销量'],
                key_skus['销售额占比'],
                key_skus['差异量'],
                key_skus['差异率']
            ))
        ))

        # 添加参考线
        fig.add_vline(x=85, line_dash="dash", line_color="gray", annotation_text="目标线:85%")

        # 计算关键统计信息
        total_skus = len(key_skus)
        avg_accuracy = key_skus['准确率'].mean()

        fig.update_layout(
            title=f"重点SKU预测准确率排行榜{title_suffix}<br><sub>销售额占比80%的核心产品 (共{total_skus}个，平均准确率{avg_accuracy:.1f}%)</sub>",
            xaxis_title="预测准确率 (%)",
            yaxis_title="产品名称",
            height=max(400, len(key_skus) * 40),  # 动态调整高度
            margin=dict(l=200, r=100, t=100, b=50),
            showlegend=False
        )

        return fig

    except Exception as e:
        st.error(f"重点SKU排行图表创建失败: {str(e)}")
        return go.Figure()


def create_product_analysis_chart(merged_data):
    """创建产品预测分析图表"""
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
                                  "实际销量: %{customdata[0]:,.0f}箱<br>" +
                                  "预测销量: %{customdata[1]:,.0f}箱<br>" +
                                  "<extra></extra>",
                    customdata=np.column_stack((
                        group_data['实际销量'],
                        group_data['预测销量']
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
            hovermode='closest'
        )

        return fig

    except Exception as e:
        st.error(f"产品分析图表创建失败: {str(e)}")
        return go.Figure()


def create_region_analysis_chart(merged_data):
    """创建区域维度分析图表"""
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

        # 1. 条形图
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
            hovertemplate="<b>%{y}</b><br>准确率: %{x:.1f}%<br><extra></extra>"
        ), row=1, col=1)

        # 2. 散点图
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
            hovertemplate="<b>%{text}</b><br>" +
                          "销量: %{x:,.0f}箱<br>" +
                          "准确率: %{y:.1f}%<br>" +
                          "销量占比: %{customdata:.1f}%<br>" +
                          "<extra></extra>",
            customdata=region_comparison['销量占比']
        ), row=1, col=2)

        fig.update_xaxes(title_text="预测准确率 (%)", row=1, col=1)
        fig.update_xaxes(title_text="实际销量 (箱)", row=1, col=2)
        fig.update_yaxes(title_text="准确率 (%)", row=1, col=2)

        fig.update_layout(
            height=500,
            showlegend=False,
            title_text="区域预测表现综合分析"
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

    # 第二行指标 - 预测准确性相关
    st.markdown("### 🎯 预测准确性关键指标")
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{forecast_key_metrics.get('total_actual_sales', 0):,}</div>
                <div class="metric-label">📊 实际销量</div>
                <div class="metric-description">{datetime.now().year}年总销量(箱)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-inner">
                <div class="metric-value">{forecast_key_metrics.get('total_forecast_sales', 0):,}</div>
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
with tab2:
    st.markdown("### 🎯 库存风险分布全景分析")

    # 原有的风险分析图表
    integrated_fig = create_integrated_risk_analysis(processed_inventory)
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

    # 新增：统计分析部分（从原tab4的子标签2移动过来）
    st.markdown("---")
    st.markdown("### 📊 库存积压统计分析")

    # 按产品统计
    product_stats = processed_inventory.groupby('产品名称').agg({
        '批次库存': 'sum',
        '批次价值': 'sum',
        '库龄': 'mean',
        '风险得分': 'mean',
        '日均出货': 'mean'
    }).round(2)

    product_stats['预计清库天数'] = product_stats['批次库存'] / product_stats['日均出货'].replace(0, 0.1)
    product_stats = product_stats.sort_values('批次价值', ascending=False)

    # 创建产品分析图表 - 增强悬停信息
    fig_product = make_subplots(
        rows=2, cols=2,
        subplot_titles=("产品库存价值TOP10", "产品平均库龄分布",
                        "产品风险得分分布", "产品预计清库天数"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )

    # TOP10产品价值 - 增强悬停
    top10_products = product_stats.head(10)
    fig_product.add_trace(
        go.Bar(
            x=top10_products.index,
            y=top10_products['批次价值'],
            marker_color='#667eea',
            text=top10_products['批次价值'].apply(lambda x: f"¥{x / 10000:.1f}万"),
            textposition='auto',
            hovertemplate="<b>产品: %{x}</b><br>" +
                          "库存价值: ¥%{y:,.0f}<br>" +
                          "占总价值比例: %{customdata[0]:.1f}%<br>" +
                          "库存量: %{customdata[1]:,.0f}箱<br>" +
                          "平均库龄: %{customdata[2]:.0f}天<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                top10_products['批次价值'] / product_stats['批次价值'].sum() * 100,
                top10_products['批次库存'],
                top10_products['库龄']
            ))
        ),
        row=1, col=1
    )

    # 产品平均库龄 - 增强悬停
    fig_product.add_trace(
        go.Bar(
            x=top10_products.index,
            y=top10_products['库龄'],
            marker_color=top10_products['库龄'].apply(
                lambda x: '#FF0000' if x > 90 else '#FFA500' if x > 60 else '#90EE90'
            ),
            text=top10_products['库龄'].apply(lambda x: f"{x:.0f}天"),
            textposition='auto',
            hovertemplate="<b>产品: %{x}</b><br>" +
                          "平均库龄: %{y:.0f}天<br>" +
                          "风险判断: %{customdata[0]}<br>" +
                          "建议措施: %{customdata[1]}<br>" +
                          "日均出货: %{customdata[2]:.2f}箱<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                top10_products['库龄'].apply(
                    lambda x: '极高风险' if x > 90 else '高风险' if x > 60 else '正常'
                ),
                top10_products['库龄'].apply(
                    lambda x: '立即7折清库' if x > 90 else '建议8折促销' if x > 60 else '正常销售'
                ),
                top10_products['日均出货']
            ))
        ),
        row=1, col=2
    )

    # 风险得分散点图 - 增强悬停
    fig_product.add_trace(
        go.Scatter(
            x=product_stats['批次价值'],
            y=product_stats['风险得分'],
            mode='markers',
            marker=dict(
                size=product_stats['批次库存'] / product_stats['批次库存'].max() * 50,
                color=product_stats['风险得分'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(
                    title="风险得分",
                    x=1.02
                )
            ),
            text=product_stats.index,
            hovertemplate="<b>产品: %{text}</b><br>" +
                          "库存价值: ¥%{x:,.0f}<br>" +
                          "风险得分: %{y:.0f}<br>" +
                          "风险等级: %{customdata[0]}<br>" +
                          "库存量: %{customdata[1]:,.0f}箱<br>" +
                          "预计清库天数: %{customdata[2]}<br>" +
                          "处理建议: %{customdata[3]}<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                product_stats['风险得分'].apply(
                    lambda x: '极高风险' if x >= 80 else '高风险' if x >= 60 else '中风险' if x >= 40 else '低风险'
                ),
                product_stats['批次库存'],
                product_stats['预计清库天数'].apply(
                    lambda x: '∞' if x > 365 else f'{x:.0f}天'
                ),
                product_stats['风险得分'].apply(
                    lambda x: '紧急清理' if x >= 80 else '优先处理' if x >= 60 else '密切监控' if x >= 40 else '常规管理'
                )
            ))
        ),
        row=2, col=1
    )

    # 预计清库天数 - 增强悬停
    clearance_data = top10_products['预计清库天数'].replace([np.inf, -np.inf], 365)
    fig_product.add_trace(
        go.Bar(
            x=top10_products.index,
            y=clearance_data,
            marker_color=clearance_data.apply(
                lambda x: '#8B0000' if x > 180 else '#FF0000' if x > 90 else '#FFA500' if x > 60 else '#90EE90'
            ),
            text=clearance_data.apply(lambda x: "∞" if x >= 365 else f"{x:.0f}天"),
            textposition='auto',
            hovertemplate="<b>产品: %{x}</b><br>" +
                          "预计清库天数: %{text}<br>" +
                          "计算依据: 库存量÷日均出货<br>" +
                          "库存量: %{customdata[0]:,.0f}箱<br>" +
                          "日均出货: %{customdata[1]:.2f}箱<br>" +
                          "风险判断: %{customdata[2]}<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                top10_products['批次库存'],
                top10_products['日均出货'],
                clearance_data.apply(
                    lambda x: '极度积压' if x > 180 else '严重积压' if x > 90 else '中度积压' if x > 60 else '轻度积压'
                )
            ))
        ),
        row=2, col=2
    )

    fig_product.update_layout(
        height=800,
        showlegend=False,
        title_text="产品维度库存风险深度分析",
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter"
        )
    )
    fig_product.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_product, use_container_width=True)

    # 区域统计
    st.markdown("#### 🌍 区域库存分析")

    region_stats = processed_inventory.groupby('责任区域').agg({
        '批次库存': 'sum',
        '批次价值': 'sum',
        '库龄': 'mean',
        '风险得分': 'mean'
    }).round(2)

    col1, col2 = st.columns(2)

    with col1:
        # 区域价值分布饼图 - 增强悬停
        fig_region_pie = go.Figure(data=[go.Pie(
            labels=region_stats.index,
            values=region_stats['批次价值'],
            hole=.4,
            marker_colors=COLOR_SCHEME['chart_colors'][:len(region_stats)],
            hovertemplate="<b>区域: %{label}</b><br>" +
                          "库存价值: ¥%{value:,.0f}<br>" +
                          "占比: %{percent}<br>" +
                          "库存量: %{customdata[0]:,.0f}箱<br>" +
                          "平均库龄: %{customdata[1]:.0f}天<br>" +
                          "平均风险得分: %{customdata[2]:.0f}<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                region_stats['批次库存'],
                region_stats['库龄'],
                region_stats['风险得分']
            ))
        )])
        fig_region_pie.update_layout(
            title="区域库存价值分布",
            height=400
        )
        st.plotly_chart(fig_region_pie, use_container_width=True)

    with col2:
        # 区域风险得分对比 - 增强悬停
        fig_region_risk = go.Figure(data=[go.Bar(
            x=region_stats.index,
            y=region_stats['风险得分'],
            marker_color=region_stats['风险得分'].apply(
                lambda x: '#FF0000' if x > 60 else '#FFA500' if x > 40 else '#90EE90'
            ),
            text=region_stats['风险得分'].apply(lambda x: f"{x:.0f}"),
            textposition='auto',
            hovertemplate="<b>区域: %{x}</b><br>" +
                          "平均风险得分: %{y:.0f}<br>" +
                          "风险等级: %{customdata[0]}<br>" +
                          "库存价值: ¥%{customdata[1]:,.0f}<br>" +
                          "平均库龄: %{customdata[2]:.0f}天<br>" +
                          "管理建议: %{customdata[3]}<br>" +
                          "<extra></extra>",
            customdata=np.column_stack((
                region_stats['风险得分'].apply(
                    lambda x: '高风险' if x > 60 else '中风险' if x > 40 else '低风险'
                ),
                region_stats['批次价值'],
                region_stats['库龄'],
                region_stats['风险得分'].apply(
                    lambda x: '需要重点关注和整改' if x > 60 else '加强监控和预防' if x > 40 else '保持现有管理水平'
                )
            ))
        )])
        fig_region_risk.update_layout(
            title="区域平均风险得分",
            height=400
        )
        st.plotly_chart(fig_region_risk, use_container_width=True)

# 标签3：销售预测准确性综合分析 - 纯图表版本
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

            # 在标签3的子标签2部分，替换整个 with sub_tab2 块的内容
            # 子标签2：重点SKU准确率排行 - 增加区域筛选器
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
                    # 创建区域对比雷达图 - 增强悬停信息
                    fig_radar = go.Figure()

                    # 存储每个区域的详细数据用于悬停显示
                    region_hover_data = {}

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

                        # 计算额外的统计数据
                        total_actual = key_skus['实际销量'].sum()
                        total_forecast = key_skus['预测销量'].sum()
                        top3_skus = key_skus.head(3)['产品名称'].tolist()
                        accuracy_range = f"{key_skus['准确率'].min() * 100:.1f}% - {key_skus['准确率'].max() * 100:.1f}%"

                        # 存储悬停数据
                        region_hover_data[region] = {
                            'metrics': metrics,
                            'total_actual': total_actual,
                            'total_forecast': total_forecast,
                            'top3_skus': top3_skus,
                            'accuracy_range': accuracy_range,
                            'sku_count': len(key_skus),
                            'total_skus': len(region_products)
                        }

                        # 创建自定义悬停文本
                        hover_text = [
                            f"<b>{region} - 平均准确率</b><br>值: {metrics['平均准确率']:.1f}%<br>范围: {accuracy_range}<br>TOP3 SKU: {', '.join(top3_skus[:3])}",
                            f"<b>{region} - SKU多样性</b><br>重点SKU数: {len(key_skus)}<br>总SKU数: {len(region_products)}<br>占比: {len(key_skus) / len(region_products) * 100:.1f}%",
                            f"<b>{region} - 销量集中度</b><br>值: {metrics['销量集中度']:.1f}<br>说明: 平均每个SKU贡献{metrics['销量集中度']:.1f}%销售额<br>实际总销量: {total_actual:,.0f}箱",
                            f"<b>{region} - 预测稳定性</b><br>值: {metrics['预测稳定性']:.1f}%<br>说明: 预测准确率的一致性程度<br>预测总量: {total_forecast:,.0f}箱"
                        ]

                        fig_radar.add_trace(go.Scatterpolar(
                            r=[metrics['平均准确率'], metrics['SKU数量'] * 2,
                               metrics['销量集中度'], metrics['预测稳定性']],
                            theta=['平均准确率', 'SKU多样性', '销量集中度', '预测稳定性'],
                            fill='toself',
                            name=region,
                            hovertext=hover_text,
                            hoverinfo="text",
                            customdata=[[total_actual, total_forecast, len(key_skus), accuracy_range]] * 4
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

                    # 添加区域对比表格
                    st.markdown("##### 📊 区域重点SKU关键指标对比表")

                    comparison_data = []
                    for region in selected_regions:
                        data = region_hover_data[region]
                        comparison_data.append({
                            '区域': region,
                            '重点SKU数量': data['sku_count'],
                            '平均准确率': f"{data['metrics']['平均准确率']:.1f}%",
                            '准确率范围': data['accuracy_range'],
                            '实际销量': f"{data['total_actual']:,.0f}",
                            '预测销量': f"{data['total_forecast']:,.0f}",
                            '销量集中度': f"{data['metrics']['销量集中度']:.1f}",
                            '预测稳定性': f"{data['metrics']['预测稳定性']:.1f}%"
                        })

                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

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

            # 统计信息卡片
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("产品总数", len(all_products))
            with col2:
                excellent_count = len(all_products[all_products['准确率'] >= 90])
                st.metric("优秀预测产品", f"{excellent_count} ({excellent_count / len(all_products) * 100:.1f}%)")
            with col3:
                poor_count = len(all_products[all_products['准确率'] < 70])
                st.metric("需改进产品", f"{poor_count} ({poor_count / len(all_products) * 100:.1f}%)")
            with col4:
                avg_accuracy = all_products['准确率'].mean()
                st.metric("平均准确率", f"{avg_accuracy:.1f}%")

        # 子标签4：区域维度深度分析 - 使用图表
        with sub_tab4:
            st.markdown("#### 🌍 区域维度预测准确性深度分析")

            # 创建区域分析图表
            region_fig = create_region_analysis_chart(merged_data)
            st.plotly_chart(region_fig, use_container_width=True)

            # 区域表现热力图
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

    else:
        st.warning(f"暂无{datetime.now().year}年的预测数据，请检查数据文件是否包含当年数据。")

# 替换整个 with tab4 块的内容
# 标签4：库存积压预警详情 - 完整移植附件一的报告格式
# 标签4：库存积压预警详情 - 简化版，只保留批次分析明细
# 标签4：库存积压预警详情 - 修改后版本
with tab4:
    st.markdown("### 📋 库存积压预警详情分析")

    if not processed_inventory.empty:
        # 创建子标签页
        detail_tab1, detail_tab2, detail_tab3 = st.tabs([
            "📊 批次分析明细",
            "📈 统计分析",
            "💡 改进建议"
        ])

        # 子标签1：批次分析明细 - 修改后版本
        with detail_tab1:
            # 筛选控件
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

            # 删除了原来的风险等级分布统计指标卡片

            # 显示筛选结果统计信息
            if not filtered_data.empty:
                st.markdown(f"#### 📋 批次分析明细表 (共{len(filtered_data)}条记录)")

                # 准备显示的列 - 风险程度字段排在第一列
                display_columns = [
                    '风险程度',  # 移至第一列
                    '物料', '描述', '批次日期', '批次库存', '库龄', '批次价值',
                    '日均出货', '出货波动系数', '预计清库天数',
                    '一个月积压风险', '两个月积压风险', '三个月积压风险',
                    '积压原因', '季节性指数', '预测偏差',
                    '责任区域', '责任人', '责任分析摘要',
                    '风险得分', '建议措施'
                ]

                # 格式化显示数据
                display_data = filtered_data[display_columns].copy()

                # 格式化数值列
                display_data['批次价值'] = display_data['批次价值'].apply(lambda x: f"¥{x:,.0f}")
                display_data['批次日期'] = display_data['批次日期'].astype(str)
                display_data['库龄'] = display_data['库龄'].apply(lambda x: f"{x}天")
                display_data['日均出货'] = display_data['日均出货'].apply(lambda x: f"{x:.2f}")
                display_data['出货波动系数'] = display_data['出货波动系数'].apply(lambda x: f"{x:.2f}")
                display_data['预计清库天数'] = display_data['预计清库天数'].apply(
                    lambda x: "∞" if x == float('inf') else f"{x:.1f}天"
                )
                display_data['季节性指数'] = display_data['季节性指数'].apply(lambda x: f"{x:.2f}")

                # 美化积压风险字段 - 添加警告图标
                display_data['一个月积压风险'] = display_data['一个月积压风险'].apply(
                    lambda x: f"🔴 {x}" if '100.0%' in str(x) or float(str(x).replace('%', '')) > 90 else
                    f"🟠 {x}" if float(str(x).replace('%', '')) > 70 else
                    f"🟡 {x}" if float(str(x).replace('%', '')) > 50 else
                    f"🟢 {x}"
                )

                display_data['两个月积压风险'] = display_data['两个月积压风险'].apply(
                    lambda x: f"🔴 {x}" if '100.0%' in str(x) or float(str(x).replace('%', '')) > 90 else
                    f"🟠 {x}" if float(str(x).replace('%', '')) > 70 else
                    f"🟡 {x}" if float(str(x).replace('%', '')) > 50 else
                    f"🟢 {x}"
                )

                display_data['三个月积压风险'] = display_data['三个月积压风险'].apply(
                    lambda x: f"🔴 {x}" if '100.0%' in str(x) or float(str(x).replace('%', '')) > 90 else
                    f"🟠 {x}" if float(str(x).replace('%', '')) > 70 else
                    f"🟡 {x}" if float(str(x).replace('%', '')) > 50 else
                    f"🟢 {x}"
                )

                # 使用增强样式显示表格，添加专门的风险等级样式
                with st.container():
                    st.markdown("""
                    <style>
                    /* 风险等级第一列特殊样式 - 极高风险动画 */
                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("极高风险")) {
                        background: linear-gradient(90deg, 
                            rgba(139, 0, 0, 0.25) 0%,
                            rgba(139, 0, 0, 0.15) 50%,
                            rgba(139, 0, 0, 0.25) 100%) !important;
                        border-left: 8px solid #8B0000 !important;
                        animation: 
                            extremeRiskRowPulse 1.5s ease-in-out infinite,
                            extremeRiskRowShake 5s ease-in-out infinite !important;
                        position: relative !important;
                        overflow: hidden !important;
                    }

                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("极高风险"))::before {
                        content: '🚨';
                        position: absolute;
                        left: -35px;
                        top: 50%;
                        transform: translateY(-50%);
                        font-size: 1.5rem;
                        animation: warningIconBlink 1s ease-in-out infinite;
                        z-index: 10;
                    }

                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("极高风险"))::after {
                        content: '';
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(139, 0, 0, 0.1), transparent);
                        animation: riskRowScanline 2s linear infinite;
                        pointer-events: none;
                        z-index: 1;
                    }

                    /* 高风险行样式 - 动画效果 */
                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("高风险")):not(:has(td:nth-child(1):contains("极高风险"))) {
                        background: linear-gradient(90deg, 
                            rgba(255, 0, 0, 0.18) 0%,
                            rgba(255, 0, 0, 0.10) 50%,
                            rgba(255, 0, 0, 0.18) 100%) !important;
                        border-left: 6px solid #FF0000 !important;
                        animation: 
                            highRiskRowGlow 2s ease-in-out infinite,
                            highRiskRowPulse 3s ease-in-out infinite !important;
                        position: relative !important;
                    }

                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("高风险")):not(:has(td:nth-child(1):contains("极高风险")))::before {
                        content: '⚡';
                        position: absolute;
                        left: -30px;
                        top: 50%;
                        transform: translateY(-50%);
                        font-size: 1.3rem;
                        animation: warningIconFloat 2s ease-in-out infinite;
                        z-index: 10;
                    }

                    /* 中风险行样式 */
                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("中风险")) {
                        background: linear-gradient(90deg, rgba(255, 165, 0, 0.12), rgba(255, 165, 0, 0.06)) !important;
                        border-left: 4px solid #FFA500 !important;
                        animation: mediumRiskRowPulse 4s ease-in-out infinite !important;
                    }

                    /* 低风险行样式 */
                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("低风险")) {
                        background: linear-gradient(90deg, rgba(144, 238, 144, 0.08), rgba(144, 238, 144, 0.04)) !important;
                        border-left: 3px solid #90EE90 !important;
                    }

                    /* 极低风险行样式 */
                    [data-testid="stDataFrame"] tbody tr:has(td:nth-child(1):contains("极低风险")) {
                        background: linear-gradient(90deg, rgba(0, 100, 0, 0.08), rgba(0, 100, 0, 0.04)) !important;
                        border-left: 3px solid #006400 !important;
                    }

                    /* 风险等级第一列单元格样式 - 超级增强版 */
                    [data-testid="stDataFrame"] tbody td:nth-child(1):contains("极高风险") {
                        background: linear-gradient(135deg, #8B0000 0%, #660000 50%, #4B0000 100%) !important;
                        color: white !important;
                        font-weight: 900 !important;
                        border-radius: 15px !important;
                        padding: 1rem 1.5rem !important;
                        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
                        animation: extremeRiskCellPulse 1s ease-in-out infinite !important;
                        box-shadow: 
                            0 4px 15px rgba(139, 0, 0, 0.5),
                            inset 0 2px 4px rgba(255,255,255,0.2),
                            inset 0 -2px 4px rgba(0,0,0,0.2) !important;
                        position: relative !important;
                        overflow: hidden !important;
                        text-transform: uppercase !important;
                        letter-spacing: 1px !important;
                        border: 2px solid rgba(255,255,255,0.3) !important;
                    }

                    [data-testid="stDataFrame"] tbody td:nth-child(1):contains("高风险"):not(:contains("极高风险")) {
                        background: linear-gradient(135deg, #FF0000 0%, #CC0000 50%, #990000 100%) !important;
                        color: white !important;
                        font-weight: 800 !important;
                        border-radius: 12px !important;
                        padding: 0.9rem 1.4rem !important;
                        text-shadow: 0 2px 3px rgba(0,0,0,0.3) !important;
                        animation: highRiskCellGlow 2s ease-in-out infinite !important;
                        box-shadow: 
                            0 3px 10px rgba(255, 0, 0, 0.4),
                            inset 0 1px 3px rgba(255,255,255,0.2) !important;
                        text-transform: uppercase !important;
                        letter-spacing: 0.5px !important;
                    }

                    [data-testid="stDataFrame"] tbody td:nth-child(1):contains("中风险") {
                        background: linear-gradient(135deg, #FFA500 0%, #FF8C00 50%, #FF7F00 100%) !important;
                        color: white !important;
                        font-weight: 700 !important;
                        border-radius: 10px !important;
                        padding: 0.8rem 1.2rem !important;
                        text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
                        box-shadow: 0 2px 8px rgba(255, 165, 0, 0.3) !important;
                    }

                    [data-testid="stDataFrame"] tbody td:nth-child(1):contains("低风险") {
                        background: linear-gradient(135deg, #90EE90 0%, #98FB98 50%, #90EE90 100%) !important;
                        color: #006400 !important;
                        font-weight: 600 !important;
                        border-radius: 8px !important;
                        padding: 0.7rem 1rem !important;
                        box-shadow: 0 2px 6px rgba(144, 238, 144, 0.3) !important;
                    }

                    [data-testid="stDataFrame"] tbody td:nth-child(1):contains("极低风险") {
                        background: linear-gradient(135deg, #006400 0%, #228B22 50%, #006400 100%) !important;
                        color: white !important;
                        font-weight: 600 !important;
                        border-radius: 8px !important;
                        padding: 0.7rem 1rem !important;
                        box-shadow: 0 2px 6px rgba(0, 100, 0, 0.3) !important;
                    }

                    /* 动画效果定义 */
                    @keyframes extremeRiskRowPulse {
                        0%, 100% {
                            box-shadow: 
                                0 0 0 0 rgba(139, 0, 0, 0.8),
                                0 10px 30px rgba(139, 0, 0, 0.3),
                                inset 0 0 20px rgba(139, 0, 0, 0.05);
                        }
                        50% {
                            box-shadow: 
                                0 0 0 20px rgba(139, 0, 0, 0),
                                0 15px 50px rgba(139, 0, 0, 0.5),
                                inset 0 0 40px rgba(139, 0, 0, 0.1);
                        }
                    }

                    @keyframes extremeRiskRowShake {
                        0%, 85%, 100% { transform: translateX(0); }
                        86%, 88%, 90%, 92%, 94% { transform: translateX(-3px); }
                        87%, 89%, 91%, 93%, 95% { transform: translateX(3px); }
                    }

                    @keyframes highRiskRowGlow {
                        0%, 100% {
                            box-shadow: 
                                0 0 15px rgba(255, 0, 0, 0.4),
                                0 5px 20px rgba(255, 0, 0, 0.2);
                        }
                        50% {
                            box-shadow: 
                                0 0 30px rgba(255, 0, 0, 0.6),
                                0 10px 40px rgba(255, 0, 0, 0.3);
                        }
                    }

                    @keyframes highRiskRowPulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.008); }
                    }

                    @keyframes mediumRiskRowPulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.95; }
                    }

                    @keyframes warningIconBlink {
                        0%, 100% { opacity: 1; transform: translateY(-50%) scale(1); }
                        50% { opacity: 0.3; transform: translateY(-50%) scale(1.1); }
                    }

                    @keyframes warningIconFloat {
                        0%, 100% { transform: translateY(-50%); }
                        50% { transform: translateY(-65%); }
                    }

                    @keyframes riskRowScanline {
                        0% { transform: translateX(-100%); }
                        100% { transform: translateX(100%); }
                    }

                    @keyframes extremeRiskCellPulse {
                        0%, 100% { 
                            transform: scale(1);
                            box-shadow: 
                                0 4px 15px rgba(139, 0, 0, 0.5),
                                inset 0 2px 4px rgba(255,255,255,0.2),
                                inset 0 -2px 4px rgba(0,0,0,0.2);
                        }
                        50% { 
                            transform: scale(1.05);
                            box-shadow: 
                                0 6px 25px rgba(139, 0, 0, 0.7),
                                inset 0 2px 4px rgba(255,255,255,0.3),
                                inset 0 -2px 4px rgba(0,0,0,0.3);
                        }
                    }

                    @keyframes highRiskCellGlow {
                        0%, 100% { 
                            filter: brightness(1) saturate(1); 
                            transform: scale(1);
                        }
                        50% { 
                            filter: brightness(1.15) saturate(1.2); 
                            transform: scale(1.03);
                        }
                    }

                    /* 积压风险列样式美化 */
                    [data-testid="stDataFrame"] tbody td:contains("🔴") {
                        animation: riskIndicatorPulse 2s ease-in-out infinite;
                        font-weight: 700 !important;
                    }

                    [data-testid="stDataFrame"] tbody td:contains("🟠") {
                        animation: riskIndicatorGlow 3s ease-in-out infinite;
                        font-weight: 600 !important;
                    }

                    @keyframes riskIndicatorPulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                    }

                    @keyframes riskIndicatorGlow {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.8; }
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="advanced-table">', unsafe_allow_html=True)

                    # 显示数据表格
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

            else:
                st.info("暂无符合筛选条件的数据")

        # 子标签2：统计分析
        with detail_tab2:
            st.markdown("#### 📊 库存积压统计分析")

            # 按产品统计
            product_stats = processed_inventory.groupby('产品名称').agg({
                '批次库存': 'sum',
                '批次价值': 'sum',
                '库龄': 'mean',
                '风险得分': 'mean',
                '日均出货': 'mean'
            }).round(2)

            product_stats['预计清库天数'] = product_stats['批次库存'] / product_stats['日均出货'].replace(0, 0.1)
            product_stats = product_stats.sort_values('批次价值', ascending=False)

            # 创建产品分析图表
            fig_product = make_subplots(
                rows=2, cols=2,
                subplot_titles=("产品库存价值TOP10", "产品平均库龄分布",
                                "产品风险得分分布", "产品预计清库天数"),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}]]
            )

            # TOP10产品价值
            top10_products = product_stats.head(10)
            fig_product.add_trace(
                go.Bar(
                    x=top10_products.index,
                    y=top10_products['批次价值'],
                    marker_color='#667eea',
                    text=top10_products['批次价值'].apply(lambda x: f"¥{x / 10000:.1f}万"),
                    textposition='auto'
                ),
                row=1, col=1
            )

            # 产品平均库龄
            fig_product.add_trace(
                go.Bar(
                    x=top10_products.index,
                    y=top10_products['库龄'],
                    marker_color=top10_products['库龄'].apply(
                        lambda x: '#FF0000' if x > 90 else '#FFA500' if x > 60 else '#90EE90'
                    ),
                    text=top10_products['库龄'].apply(lambda x: f"{x:.0f}天"),
                    textposition='auto'
                ),
                row=1, col=2
            )

            # 风险得分散点图
            fig_product.add_trace(
                go.Scatter(
                    x=product_stats['批次价值'],
                    y=product_stats['风险得分'],
                    mode='markers',
                    marker=dict(
                        size=product_stats['批次库存'] / product_stats['批次库存'].max() * 50,
                        color=product_stats['风险得分'],
                        colorscale='RdYlGn_r',
                        showscale=True
                    ),
                    text=product_stats.index,
                    hovertemplate="<b>%{text}</b><br>" +
                                  "价值: ¥%{x:,.0f}<br>" +
                                  "风险得分: %{y:.0f}<br>" +
                                  "<extra></extra>"
                ),
                row=2, col=1
            )

            # 预计清库天数
            clearance_data = top10_products['预计清库天数'].replace([np.inf, -np.inf], 365)
            fig_product.add_trace(
                go.Bar(
                    x=top10_products.index,
                    y=clearance_data,
                    marker_color=clearance_data.apply(
                        lambda x: '#8B0000' if x > 180 else '#FF0000' if x > 90 else '#FFA500' if x > 60 else '#90EE90'
                    ),
                    text=clearance_data.apply(lambda x: "∞" if x >= 365 else f"{x:.0f}天"),
                    textposition='auto'
                ),
                row=2, col=2
            )

            fig_product.update_layout(height=800, showlegend=False)
            fig_product.update_xaxes(tickangle=-45)

            st.plotly_chart(fig_product, use_container_width=True)

            # 区域统计
            st.markdown("#### 🌍 区域库存分析")

            region_stats = processed_inventory.groupby('责任区域').agg({
                '批次库存': 'sum',
                '批次价值': 'sum',
                '库龄': 'mean',
                '风险得分': 'mean'
            }).round(2)

            col1, col2 = st.columns(2)

            with col1:
                # 区域价值分布饼图
                fig_region_pie = go.Figure(data=[go.Pie(
                    labels=region_stats.index,
                    values=region_stats['批次价值'],
                    hole=.4,
                    marker_colors=COLOR_SCHEME['chart_colors'][:len(region_stats)]
                )])
                fig_region_pie.update_layout(
                    title="区域库存价值分布",
                    height=400
                )
                st.plotly_chart(fig_region_pie, use_container_width=True)

            with col2:
                # 区域风险得分对比
                fig_region_risk = go.Figure(data=[go.Bar(
                    x=region_stats.index,
                    y=region_stats['风险得分'],
                    marker_color=region_stats['风险得分'].apply(
                        lambda x: '#FF0000' if x > 60 else '#FFA500' if x > 40 else '#90EE90'
                    ),
                    text=region_stats['风险得分'].apply(lambda x: f"{x:.0f}"),
                    textposition='auto'
                )])
                fig_region_risk.update_layout(
                    title="区域平均风险得分",
                    height=400
                )
                st.plotly_chart(fig_region_risk, use_container_width=True)

        # 子标签3：改进建议
        with detail_tab3:
            st.markdown("#### 💡 库存优化改进建议")

            # 计算关键洞察
            high_risk_items = processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])]
            total_risk_value = high_risk_items['批次价值'].sum()
            potential_recovery = total_risk_value * 0.7  # 假设7折处理

            # 重点问题产品
            problem_products = processed_inventory.groupby('产品名称').agg({
                '批次价值': 'sum',
                '风险得分': 'mean'
            }).sort_values('风险得分', ascending=False).head(5)

            # 建议卡片
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">🎯 核心改进目标</div>
                <div class="insight-content">
                    • 高风险库存总价值：¥{total_risk_value:,.0f}<br>
                    • 预计可回收资金：¥{potential_recovery:,.0f} (7折清理)<br>
                    • 需重点处理批次：{len(high_risk_items)}个<br>
                    • 建议处理周期：30天内完成高风险批次清理
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 分级改进措施
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class="content-container">
                    <h5>🚨 紧急措施（7天内）</h5>
                    <ul>
                        <li>立即对极高风险批次实施7折清仓</li>
                        <li>联系各区域负责人制定清库计划</li>
                        <li>启动跨区域库存调配机制</li>
                        <li>开展特价促销活动</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="content-container">
                    <h5>📊 中期优化（30天内）</h5>
                    <ul>
                        <li>优化销售预测模型，提高准确率</li>
                        <li>建立库存预警自动化系统</li>
                        <li>完善区域间协同机制</li>
                        <li>制定分级库存管理策略</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="content-container">
                    <h5>⚡ 短期行动（14天内）</h5>
                    <ul>
                        <li>评估高风险批次处理进度</li>
                        <li>调整采购计划，避免新增积压</li>
                        <li>强化销售团队库存意识培训</li>
                        <li>建立每周库存审查机制</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="content-container">
                    <h5>🎯 长期战略（90天内）</h5>
                    <ul>
                        <li>实施S&OP流程优化</li>
                        <li>引入AI预测系统</li>
                        <li>建立供应链柔性机制</li>
                        <li>完善绩效考核体系</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 重点关注产品清单
            st.markdown("#### 🔍 重点关注产品")

            problem_display = problem_products.copy()
            problem_display['批次价值'] = problem_display['批次价值'].apply(lambda x: f"¥{x:,.0f}")
            problem_display['风险得分'] = problem_display['风险得分'].apply(lambda x: f"{x:.0f}")
            problem_display['处理优先级'] = ['🔴 极高', '🟠 高', '🟡 中', '🟢 一般', '🔵 低'][:len(problem_display)]

            st.dataframe(
                problem_display[['批次价值', '风险得分', '处理优先级']],
                use_container_width=True
            )

            # 责任人行动计划
            st.markdown("#### 👥 责任人行动计划")

            responsible_stats = processed_inventory[
                processed_inventory['风险等级'].isin(['极高风险', '高风险'])
            ].groupby('责任人').agg({
                '批次库存': 'sum',
                '批次价值': 'sum',
                '产品名称': 'count'
            }).sort_values('批次价值', ascending=False).head(10)

            responsible_stats.columns = ['负责库存量', '负责价值', '批次数']
            responsible_stats['行动要求'] = responsible_stats.apply(
                lambda x: f"30天内清理{x['批次数']}个批次，价值¥{x['负责价值']:,.0f}",
                axis=1
            )

            st.dataframe(
                responsible_stats[['负责库存量', '负责价值', '批次数', '行动要求']],
                use_container_width=True
            )

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
