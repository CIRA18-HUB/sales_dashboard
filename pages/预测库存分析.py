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
    
    /* Plotly图表圆角样式 - 重要修改 */
    .js-plotly-plot .plotly .modebar {
        border-top-right-radius: 20px !important;
    }
    
    .js-plotly-plot .plotly {
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Plotly图表容器样式 */
    div[data-testid="stPlotlyChart"] {
        border-radius: 20px !important;
        overflow: hidden !important;
        margin-bottom: 2rem !important;
        background: rgba(255,255,255,0.98) !important;
        padding: 1rem !important;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03) !important;
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
    .risk-extreme { border-left-color: #ff4757 !important; }
    .risk-high { border-left-color: #ff6348 !important; }
    .risk-medium { border-left-color: #ffa502 !important; }
    .risk-low { border-left-color: #2ed573 !important; }
    .risk-minimal { border-left-color: #5352ed !important; }
    
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
            rgba(255, 71, 87, 0.15) 0%,
            rgba(255, 71, 87, 0.08) 50%,
            rgba(255, 71, 87, 0.15) 100%) !important;
        border-left: 8px solid #ff4757 !important;
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
        background: linear-gradient(90deg, transparent, rgba(255, 71, 87, 0.1), transparent);
        animation: riskScanline 2s linear infinite;
        pointer-events: none;
    }
    
    .stDataFrame tbody tr:has(td:contains("极高风险")):hover {
        background: linear-gradient(90deg, 
            rgba(255, 71, 87, 0.25) 0%,
            rgba(255, 71, 87, 0.15) 50%,
            rgba(255, 71, 87, 0.25) 100%) !important;
        transform: scale(1.03) translateX(15px) !important;
        box-shadow: 
            0 20px 50px rgba(255, 71, 87, 0.4),
            -10px 0 30px rgba(255, 71, 87, 0.3),
            inset 0 0 30px rgba(255, 71, 87, 0.1) !important;
        border-left-width: 12px !important;
    }
    
    /* 风险等级样式 - 高风险 (增强版) */
    .stDataFrame tbody tr:has(td:contains("高风险")):not(:has(td:contains("极高风险"))) {
        background: linear-gradient(90deg, 
            rgba(255, 99, 72, 0.12) 0%,
            rgba(255, 99, 72, 0.06) 50%,
            rgba(255, 99, 72, 0.12) 100%) !important;
        border-left: 6px solid #ff6348 !important;
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
            rgba(255, 99, 72, 0.2) 0%,
            rgba(255, 99, 72, 0.12) 50%,
            rgba(255, 99, 72, 0.2) 100%) !important;
        transform: scale(1.025) translateX(12px) !important;
        box-shadow: 
            0 15px 40px rgba(255, 99, 72, 0.35),
            -8px 0 25px rgba(255, 99, 72, 0.25),
            inset 0 0 20px rgba(255, 99, 72, 0.08) !important;
        border-left-width: 10px !important;
    }
    
    /* 风险等级样式 - 中风险 */
    .stDataFrame tbody tr:has(td:contains("中风险")) {
        background: linear-gradient(90deg, rgba(255, 165, 2, 0.08), rgba(255, 165, 2, 0.04)) !important;
        border-left: 4px solid #ffa502 !important;
        animation: mediumRiskPulse 3s ease-in-out infinite !important;
    }
    
    .stDataFrame tbody tr:has(td:contains("中风险")):hover {
        background: linear-gradient(90deg, rgba(255, 165, 2, 0.15), rgba(255, 165, 2, 0.08)) !important;
        transform: scale(1.015) translateX(8px) !important;
        box-shadow: 0 10px 30px rgba(255, 165, 2, 0.2) !important;
    }
    
    /* 风险等级样式 - 低风险 */
    .stDataFrame tbody tr:has(td:contains("低风险")) {
        background: linear-gradient(90deg, rgba(46, 213, 115, 0.06), rgba(46, 213, 115, 0.03)) !important;
        border-left: 3px solid #2ed573 !important;
    }
    
    /* 风险等级样式 - 极低风险 */
    .stDataFrame tbody tr:has(td:contains("极低风险")) {
        background: linear-gradient(90deg, rgba(83, 82, 237, 0.06), rgba(83, 82, 237, 0.03)) !important;
        border-left: 3px solid #5352ed !important;
    }
    
    /* 动画效果定义 */
    @keyframes extremeRiskPulse {
        0%, 100% {
            box-shadow: 
                0 0 0 0 rgba(255, 71, 87, 0.8),
                0 10px 25px rgba(255, 71, 87, 0.3),
                inset 0 0 20px rgba(255, 71, 87, 0.05);
        }
        50% {
            box-shadow: 
                0 0 0 15px rgba(255, 71, 87, 0),
                0 15px 40px rgba(255, 71, 87, 0.5),
                inset 0 0 30px rgba(255, 71, 87, 0.1);
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
                0 0 10px rgba(255, 99, 72, 0.4),
                0 5px 15px rgba(255, 99, 72, 0.2);
        }
        50% {
            box-shadow: 
                0 0 25px rgba(255, 99, 72, 0.6),
                0 10px 30px rgba(255, 99, 72, 0.3);
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
        background: linear-gradient(135deg, #ff4757 0%, #ff3838 50%, #ff2525 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        padding: 1rem 1.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        animation: extremeRiskTextPulse 1s ease-in-out infinite !important;
        box-shadow: 
            0 4px 10px rgba(255, 71, 87, 0.4),
            inset 0 2px 4px rgba(255,255,255,0.2),
            inset 0 -2px 4px rgba(0,0,0,0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="stDataFrameResizable"] td:contains("高风险") {
        background: linear-gradient(135deg, #ff6348 0%, #ff5733 50%, #ff4520 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.4rem !important;
        text-shadow: 0 2px 3px rgba(0,0,0,0.3) !important;
        animation: highRiskTextGlow 2s ease-in-out infinite !important;
        box-shadow: 
            0 3px 8px rgba(255, 99, 72, 0.3),
            inset 0 1px 3px rgba(255,255,255,0.2) !important;
    }
    
    @keyframes extremeRiskTextPulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 
                0 4px 10px rgba(255, 71, 87, 0.4),
                inset 0 2px 4px rgba(255,255,255,0.2),
                inset 0 -2px 4px rgba(0,0,0,0.2);
        }
        50% { 
            transform: scale(1.05);
            box-shadow: 
                0 6px 20px rgba(255, 71, 87, 0.6),
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
        color: #2ed573 !important;
        text-shadow: 0 1px 2px rgba(46, 213, 115, 0.2) !important;
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
            background: radial-gradient(circle at 50% 50%, rgba(255, 71, 87, 0.3) 0%, transparent 50%);
            opacity: 0;
        }
        50% {
            opacity: 1;
        }
        100% {
            background: radial-gradient(circle at 50% 50%, rgba(255, 71, 87, 0) 0%, transparent 80%);
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
    'risk_extreme': '#ff4757',
    'risk_high': '#ff6348',
    'risk_medium': '#ffa502',
    'risk_low': '#2ed573',
    'risk_minimal': '#5352ed',
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
@st.cache_data
def load_and_process_data():
    """加载和处理所有数据"""
    try:
        # 读取数据文件
        shipment_df = pd.read_excel('2409~250224出货数据.xlsx')
        forecast_df = pd.read_excel('2409~2502人工预测.xlsx') 
        inventory_df = pd.read_excel('含批次库存0221(2).xlsx')
        price_df = pd.read_excel('单价.xlsx')
        
        # 处理日期
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])
        forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'], format='%Y-%m')
        
        # 创建产品代码到名称的映射
        product_name_map = {}
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and pd.notna(row['描述']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                simplified_name = simplify_product_name(row['描述'])
                product_name_map[row['物料']] = simplified_name
        
        # 处理库存数据
        batch_data = []
        current_material = None
        current_desc = None
        current_price = 0
        
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                current_material = row['物料']
                current_desc = simplify_product_name(row['描述'])
                # 获取单价
                price_match = price_df[price_df['产品代码'] == current_material]
                current_price = price_match['单价'].iloc[0] if len(price_match) > 0 else 100
            elif pd.notna(row['生产日期']) and current_material:
                # 这是批次信息行
                prod_date = pd.to_datetime(row['生产日期'])
                quantity = row['数量'] if pd.notna(row['数量']) else 0
                batch_no = row['生产批号'] if pd.notna(row['生产批号']) else ''
                
                # 计算库龄
                age_days = (datetime.now() - prod_date).days
                
                # 确定风险等级
                if age_days >= 120:
                    risk_level = '极高风险'
                    risk_color = COLOR_SCHEME['risk_extreme']
                    risk_advice = '🚨 立即7折清库'
                elif age_days >= 90:
                    risk_level = '高风险'
                    risk_color = COLOR_SCHEME['risk_high'] 
                    risk_advice = '⚠️ 建议8折促销'
                elif age_days >= 60:
                    risk_level = '中风险'
                    risk_color = COLOR_SCHEME['risk_medium']
                    risk_advice = '📢 适度9折促销'
                elif age_days >= 30:
                    risk_level = '低风险'
                    risk_color = COLOR_SCHEME['risk_low']
                    risk_advice = '✅ 正常销售'
                else:
                    risk_level = '极低风险'
                    risk_color = COLOR_SCHEME['risk_minimal']
                    risk_advice = '🌟 新鲜库存'
                
                # 计算预期损失
                if age_days >= 120:
                    expected_loss = quantity * current_price * 0.3
                elif age_days >= 90:
                    expected_loss = quantity * current_price * 0.2
                elif age_days >= 60:
                    expected_loss = quantity * current_price * 0.1
                else:
                    expected_loss = 0
                
                batch_data.append({
                    '物料': current_material,
                    '产品名称': current_desc,
                    '生产日期': prod_date,
                    '生产批号': batch_no,
                    '数量': quantity,
                    '库龄': age_days,
                    '风险等级': risk_level,
                    '风险颜色': risk_color,
                    '处理建议': risk_advice,
                    '单价': current_price,
                    '批次价值': quantity * current_price,
                    '预期损失': expected_loss
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
    high_risk_value_ratio = (high_risk_value / processed_inventory['批次价值'].sum() * 100) if processed_inventory['批次价值'].sum() > 0 else 0
    
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
        shipment_current_year['产品名称'] = shipment_current_year['产品代码'].map(product_name_map).fillna(shipment_current_year['产品代码'])
        forecast_current_year['产品名称'] = forecast_current_year['产品代码'].map(product_name_map).fillna(forecast_current_year['产品代码'])
        
        # 按月份和产品汇总实际销量
        shipment_monthly = shipment_current_year.groupby([
            shipment_current_year['订单日期'].dt.to_period('M'),
            '产品代码',
            '产品名称',
            '所属区域'
        ]).agg({
            '求和项:数量（箱）': 'sum'
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
        
        # 计算准确率和差异
        merged_data['实际销量'] = merged_data['求和项:数量（箱）']
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
        
        colors = [
            COLOR_SCHEME['risk_extreme'],
            COLOR_SCHEME['risk_high'],
            COLOR_SCHEME['risk_medium'], 
            COLOR_SCHEME['risk_low'],
            COLOR_SCHEME['risk_minimal']
        ]
        
        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("风险等级分布", "各风险等级价值分布", "库存批次库龄分布", "高风险批次优先级分析"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )
        
        # 1. 风险等级分布饼图 - 增强悬停
        fig.add_trace(go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            hole=.4,
            marker_colors=colors[:len(risk_counts)],
            textinfo='label+percent',
            name="风险分布",
            hovertemplate="<b>%{label}</b><br>" +
                         "批次数量: %{value}个<br>" +
                         "占比: %{percent}<br>" +
                         "<extra></extra>"
        ), row=1, col=1)
        
        # 2. 风险等级价值分布 - 增强悬停
        fig.add_trace(go.Bar(
            x=risk_value.index,
            y=risk_value.values,
            marker_color=colors[:len(risk_value)],
            name="价值分布",
            text=[f'¥{v:.1f}M' for v in risk_value.values],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>" +
                         "总价值: ¥%{y:.1f}M<br>" +
                         "批次数: " + risk_value.index.map(lambda x: str(risk_counts.get(x, 0))) + "个<br>" +
                         "平均批次价值: ¥%{y:.1f}K<br>" +
                         "<extra></extra>"
        ), row=1, col=2)
        
        # 3. 库龄分布直方图 - 增强悬停
        fig.add_trace(go.Histogram(
            x=processed_inventory['库龄'],
            nbinsx=20,
            marker_color=COLOR_SCHEME['primary'],
            opacity=0.7,
            name="库龄分布",
            hovertemplate="库龄范围: %{x}天<br>" +
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
                    size=np.minimum(high_risk_data['数量']/20, 50),
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
            )
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
        
        # 在左上角添加重点SKU统计
        key_sku_text = f"🎯 <b>重点SKU统计</b><br>数量: {len(key_products_data)}个<br>占销售额: 80%<br>平均准确率: {key_products_data['准确率'].mean():.1%}"
        fig.add_annotation(
            x=0.02,
            y=0.98,
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
        
        # 更新布局
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
                y=0.02,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter"
            )
        )
        
        return fig
    
    except Exception as e:
        st.error(f"预测分析图表创建失败: {str(e)}")
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
        risk_class = "risk-extreme" if metrics['high_risk_ratio'] > 25 else "risk-high" if metrics['high_risk_ratio'] > 15 else "risk-medium"
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
with tab2:
    st.markdown("### 🎯 库存风险分布全景分析")
    
    # 直接显示图表，不使用容器
    integrated_fig = create_integrated_risk_analysis(processed_inventory)
    st.plotly_chart(integrated_fig, use_container_width=True)
    
    # 风险分析洞察
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">📊 综合风险分析洞察</div>
        <div class="insight-content">
            • 极高风险: {metrics['risk_counts']['extreme']}个批次 ({metrics['risk_counts']['extreme']/max(metrics['total_batches'], 1)*100:.1f}%)<br>
            • 高风险: {metrics['risk_counts']['high']}个批次 ({metrics['risk_counts']['high']/max(metrics['total_batches'], 1)*100:.1f}%)<br>
            • 高风险批次价值占比: {metrics['high_risk_value_ratio']:.1f}%<br>
            • 建议优先处理极高风险和高风险批次，通过促销可回收资金: ¥{metrics['high_risk_value']*0.8:.1f}M
        </div>
    </div>
    """, unsafe_allow_html=True)

# 标签3：销售预测准确性综合分析 - 无表格版本
with tab3:
    st.markdown(f"### 📈 销售预测准确性综合分析 - {datetime.now().year}年数据")
    
    if merged_data is not None and not merged_data.empty:
        # 直接显示超级整合图表，不使用容器
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
                • <b>整体表现:</b> 预测准确率{overall_acc:.1f}%，{'已达到优秀水平' if overall_acc >= 85 else '距离85%目标还有' + f'{85-overall_acc:.1f}%提升空间'}<br>
                • <b>重点SKU:</b> {key_products_count}个产品贡献80%销售额，是预测精度提升的关键focus<br>
                • <b>预测偏差:</b> 整体{'预测偏高' if diff_rate < 0 else '预测偏低' if diff_rate > 0 else '预测相对准确'}，差异率{abs(diff_rate):.1f}%<br>
                • <b>改进方向:</b> 重点关注图中大气泡低准确率(红色)产品，优化其预测模型和参数<br>
                • <b>区域差异:</b> 各区域预测能力存在差异，建议针对性培训和经验分享
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning(f"暂无{datetime.now().year}年的预测数据，请检查数据文件是否包含当年数据。")

# 标签4：库存积压预警详情
with tab4:
    st.markdown("### 📋 库存积压预警详情")
    
    if not processed_inventory.empty:
        # 筛选控件
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox(
                "选择风险等级",
                options=['全部'] + list(processed_inventory['风险等级'].unique()),
                index=0
            )
        
        with col2:
            min_value = st.number_input(
                "最小批次价值",
                min_value=0,
                max_value=int(processed_inventory['批次价值'].max()),
                value=0
            )
        
        with col3:
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
        
        filtered_data = filtered_data[
            (filtered_data['批次价值'] >= min_value) &
            (filtered_data['库龄'] <= max_age)
        ]
        
        # 显示高级数据表格
        if not filtered_data.empty:
            # 使用容器包裹表格
            with st.container():
                st.markdown('<div class="advanced-table">', unsafe_allow_html=True)
                
                # 重新排序列并格式化
                display_columns = ['物料', '产品名称', '生产日期', '生产批号', '数量', '库龄', '风险等级', '批次价值', '处理建议']
                display_data = filtered_data[display_columns].copy()
                
                # 格式化数值
                display_data['批次价值'] = display_data['批次价值'].apply(lambda x: f"¥{x:,.0f}")
                display_data['生产日期'] = display_data['生产日期'].dt.strftime('%Y-%m-%d')
                display_data['库龄'] = display_data['库龄'].apply(lambda x: f"{x}天")
                
                # 按风险等级和价值排序
                risk_order = {'极高风险': 0, '高风险': 1, '中风险': 2, '低风险': 3, '极低风险': 4}
                display_data['风险排序'] = display_data['风险等级'].map(risk_order)
                display_data = display_data.sort_values(['风险排序', '库龄'], ascending=[True, False])
                display_data = display_data.drop('风险排序', axis=1)
                
                # 显示增强表格
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    height=500,
                    hide_index=False
                )
                
                # 下载按钮
                csv = display_data.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载筛选结果",
                    data=csv,
                    file_name=f"库存积压预警_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; 
                        background: linear-gradient(135deg, rgba(255, 165, 2, 0.1), rgba(255, 165, 2, 0.05));
                        border-radius: 20px; border: 2px dashed #ffa502;">
                <div style="font-size: 3rem; color: #ffa502; margin-bottom: 1rem;">📭</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ffa502; margin-bottom: 0.5rem;">暂无符合条件的数据</div>
                <div style="color: #666; font-size: 1rem;">请调整筛选条件重新查询</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; 
                    background: linear-gradient(135deg, rgba(255, 71, 87, 0.1), rgba(255, 71, 87, 0.05));
                    border-radius: 20px; border: 2px dashed #ff4757;">
            <div style="font-size: 3rem; color: #ff4757; margin-bottom: 1rem;">📦</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #ff4757; margin-bottom: 0.5rem;">暂无库存数据</div>
            <div style="color: #666; font-size: 1rem;">请检查数据文件是否正确加载</div>
        </div>
        """, unsafe_allow_html=True)

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
