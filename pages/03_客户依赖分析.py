# pages/客户依赖分析.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import json
import time

warnings.filterwarnings('ignore')

# 尝试导入 streamlit-echarts
try:
    from streamlit_echarts import st_echarts

    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False
    print("streamlit-echarts 未安装，将使用备选方案")

# 创建一个简单的 streamlit-echarts 包装器（用于没有安装时的兼容性）
if not ECHARTS_AVAILABLE:
    def st_echarts(options, height="400px", key=None):
        st.error("streamlit-echarts 组件未安装。请运行以下命令安装：")
        st.code("pip install streamlit-echarts", language="bash")
        st.info("安装后请重新启动应用。现在将显示备选图表。")
        return None

# 设置页面配置
st.set_page_config(
    page_title="客户依赖分析 - Trolli SAL",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录！")
    st.switch_page("app.py")
    st.stop()

# 统一高级CSS样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* 浮动粒子背景 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none; z-index: -1;
    }

    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    /* 主容器 */
    .main .block-container {
        background: rgba(255,255,255,0.95);
        border-radius: 20px; padding: 2rem; margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 主标题 */
    .main-header {
        text-align: center; padding: 2.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white; border-radius: 20px; margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.2s ease-out;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        position: relative; overflow: hidden;
    }

    .main-header::before {
        content: ''; position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
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
        from { opacity: 0; transform: translateY(-30px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* === 关键修复：统一指标卡片样式 === */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
        padding: 1.5rem !important; 
        border-radius: 18px !important; 
        text-align: center !important; 
        height: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 3px 10px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        animation: slideUp 0.8s ease-out !important;
        backdrop-filter: blur(10px) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
        overflow: hidden !important;
        margin-bottom: 1rem !important;
    }

    .metric-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent) !important;
        transition: left 0.6s ease !important;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 10px 20px rgba(102, 126, 234, 0.15) !important;
    }

    .metric-card:hover::before { left: 100% !important; }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 指标数值样式 */
    .metric-value {
        font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1.1;
    }

    .big-value {
        font-size: 2.8rem; font-weight: 900; margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1;
    }

    @keyframes valueGlow {
        from { filter: brightness(1); }
        to { filter: brightness(1.1); }
    }

    .metric-label {
        color: #374151; font-size: 0.95rem; font-weight: 600;
        margin-top: 0.5rem; letter-spacing: 0.3px;
    }

    .metric-sublabel {
        color: #6b7280; font-size: 0.8rem; margin-top: 0.4rem;
        font-weight: 500; font-style: italic;
    }

    /* === 新增：目标达成率卡片专用样式 === */
    .target-achievement-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
        padding: 1.2rem !important; 
        border-radius: 18px !important; 
        text-align: center !important; 
        height: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 3px 10px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        animation: slideUp 0.8s ease-out !important;
        backdrop-filter: blur(10px) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
        overflow: hidden !important;
        margin-bottom: 1rem !important;
    }

    .target-achievement-card:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 10px 20px rgba(102, 126, 234, 0.15) !important;
    }

    .target-calculation-logic {
        font-size: 0.7rem !important;
        color: #6b7280 !important;
        margin-top: 0.3rem !important;
        line-height: 1.2 !important;
        font-weight: 500 !important;
        text-align: center !important;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 0.6rem; border-radius: 12px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px; padding: 0 20px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px; border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 600; font-size: 0.85rem;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px); 
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }

    /* === 修复：直接对Plotly图表应用圆角样式并禁用全屏 === */
    .stPlotlyChart {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.06), 0 3px 10px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.05);
        margin: 1.5rem 0;
    }

    .stPlotlyChart .js-plotly-plot {
        background: white !important;
        border-radius: 16px !important;
    }

    .stPlotlyChart .plot-container {
        background: white !important;
        border-radius: 16px !important;
    }

    /* === 新增：禁用Plotly全屏按钮 === */
    .stPlotlyChart .modebar-btn[data-title="zoom"],
    .stPlotlyChart .modebar-btn[data-title="Zoom"],
    .stPlotlyChart .modebar-btn[data-title*="zoom"],
    .stPlotlyChart .modebar-btn[data-title*="full"],
    .stPlotlyChart .modebar-btn[data-title*="Full"],
    .stPlotlyChart .modebar-btn[data-title="Toggle Spike Lines"],
    .stPlotlyChart .modebar-btn[data-title="Show closest data on hover"],
    .stPlotlyChart .modebar-btn[data-title="Compare data on hover"] {
        display: none !important;
    }

    /* 洞察卡片 */
    .insight-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-left: 4px solid #667eea; border-radius: 12px;
        padding: 1.2rem; margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        animation: slideInLeft 0.6s ease-out;
        transition: all 0.3s ease;
    }

    .insight-card:hover {
        transform: translateX(5px) translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.12);
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .insight-card h4 {
        color: #1f2937; margin-bottom: 0.8rem;
        font-weight: 700; font-size: 1rem;
    }

    .insight-card ul {
        color: #374151; line-height: 1.5; margin: 0; padding-left: 1rem;
    }

    .insight-card li {
        margin-bottom: 0.3rem; color: #4a5568; font-size: 0.9rem;
    }

    /* 动画延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }

    /* 响应式 */
    @media (max-width: 768px) {
        .metric-value, .big-value { font-size: 1.8rem; }
        .metric-card { padding: 1rem; margin: 0.5rem 0; height: 140px !important; }
        .target-achievement-card { padding: 1rem; margin: 0.5rem 0; height: 140px !important; }
        .main-header { padding: 1.5rem 0; }
    }

    /* 确保文字颜色 */
    h1, h2, h3, h4, h5, h6 { color: #1f2937 !important; }
    p, span, div { color: #374151; }

    /* 优化Plotly图表中文字体 */
    .plotly .gtitle {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Arial", sans-serif !important;
    }

    .plotly .g-gtitle {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Arial", sans-serif !important;
    }

    /* 图表标题容器 */
    .chart-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 200% 200%;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
        position: relative;
        overflow: hidden;
        animation: gradientFlow 6s ease infinite;
        transition: all 0.3s ease;
    }

    .chart-header:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
    }

    /* 渐变流动动画 */
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 光泽效果 */
    .chart-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent
        );
        animation: shine 3s ease-in-out infinite;
    }

    @keyframes shine {
        0% { left: -100%; }
        50%, 100% { left: 200%; }
    }

    /* 图表标题样式 */
    .chart-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-align: left;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
        line-height: 1.2;
        animation: fadeInSlide 0.8s ease-out;
    }

    .chart-subtitle {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        font-weight: 400;
        text-align: left;
        line-height: 1.4;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
        animation: fadeInSlide 1s ease-out;
    }

    @keyframes fadeInSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* ===== 新增的现代化样式 ===== */

    /* 现代化图表容器样式 */
    .stPlotlyChart > div {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%);
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15), 
                    0 1px 8px rgba(0,0,0,0.05) !important;
        padding: 15px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .stPlotlyChart > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2), 
                    0 5px 15px rgba(0,0,0,0.08) !important;
    }

    /* 优化下拉选择框样式 */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
    }

    /* 趋势分析特殊样式 */
    .trend-analysis-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e9ecef 100%);
        border-radius: 24px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }

    /* 增强的图表悬停效果 */
    .js-plotly-plot .plotly:hover {
        cursor: pointer;
    }

    /* 美化滚动条 */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46a1 100%);
    }
</style>
""", unsafe_allow_html=True)


# 数据加载函数
@st.cache_data(ttl=3600)
def load_and_process_data():
    """加载并处理客户数据 - 调试版本"""
    try:
        customer_status = pd.read_excel("客户状态.xlsx")
        customer_status.columns = ['客户名称', '状态']

        sales_data = pd.read_excel("客户月度销售达成.xlsx")
        sales_data.columns = ['订单日期', '发运月份', '经销商名称', '金额']

        # 添加详细调试信息
        print(f"=== 原始数据调试信息 ===")
        print(f"数据总行数: {len(sales_data)}")
        print(f"数据字段: {sales_data.columns.tolist()}")
        print(f"前5行数据:")
        print(sales_data.head())
        print(f"发运月份字段类型: {sales_data['发运月份'].dtype}")
        print(f"发运月份样例: {sales_data['发运月份'].head()}")
        print(f"金额字段类型: {sales_data['金额'].dtype}")
        print(f"金额样例: {sales_data['金额'].head()}")

        # 处理金额字段 - 更严格的清理
        print(f"=== 处理金额字段 ===")
        # 先转换为字符串，移除所有可能的分隔符
        sales_data['金额_原始'] = sales_data['金额'].copy()  # 保存原始值用于调试
        sales_data['金额'] = sales_data['金额'].astype(str).str.replace(',', '').str.replace('，', '').str.replace(' ',
                                                                                                                  '')

        # 转换为数值类型
        sales_data['金额'] = pd.to_numeric(sales_data['金额'], errors='coerce')

        # 检查转换结果
        print(f"金额转换后的空值数量: {sales_data['金额'].isna().sum()}")
        print(f"金额转换后的总和: {sales_data['金额'].sum():,.0f}")

        # 填充空值为0
        sales_data['金额'] = sales_data['金额'].fillna(0)

        # 处理日期字段
        print(f"=== 处理日期字段 ===")
        sales_data['订单日期'] = pd.to_datetime(sales_data['订单日期'], errors='coerce')

        # 关键修复：更严格的发运月份处理
        if sales_data['发运月份'].dtype == 'object':
            # 如果是字符串类型，先尝试解析
            print("发运月份是字符串类型，尝试解析...")
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'], errors='coerce')
        else:
            # 如果已经是datetime类型，直接使用
            print("发运月份已是datetime类型")
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'], errors='coerce')

        print(f"发运月份处理后的空值数量: {sales_data['发运月份'].isna().sum()}")
        print(f"发运月份范围: {sales_data['发运月份'].min()} 到 {sales_data['发运月份'].max()}")

        # 检查数据完整性
        valid_data = sales_data.dropna(subset=['发运月份', '金额'])
        print(f"有效数据行数: {len(valid_data)}")
        print(f"有效数据金额总和: {valid_data['金额'].sum():,.0f}")

        # 按年份分组查看数据分布
        print(f"=== 按发运年份统计 ===")
        sales_data['发运年份'] = sales_data['发运月份'].dt.year
        yearly_stats = sales_data.groupby('发运年份')['金额'].agg(['count', 'sum']).reset_index()
        print("年份分布:")
        print(yearly_stats)

        monthly_data = pd.read_excel("客户月度指标.xlsx")
        monthly_data.columns = ['客户', '月度指标', '月份', '往年同期', '所属大区']

        current_year = datetime.now().year
        print(f"当前年份: {current_year}")

        metrics = calculate_metrics(customer_status, sales_data, monthly_data, current_year)

        return metrics, customer_status, sales_data, monthly_data

    except Exception as e:
        st.error(f"数据加载错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return None, None, None, None


def create_integrated_trend_analysis(sales_data, monthly_data, selected_region='全国'):
    """创建整合的趋势分析图表 - 修改为按发运月份统计"""
    # 获取区域数据
    if selected_region == '全国':
        region_sales = sales_data.copy()
    else:
        customer_region_map = monthly_data[['客户', '所属大区']].drop_duplicates()
        sales_with_region = sales_data.merge(
            customer_region_map, left_on='经销商名称', right_on='客户', how='left'
        )
        region_sales = sales_with_region[sales_with_region['所属大区'] == selected_region]

    if region_sales.empty:
        return None

    # 计算基础指标
    total_sales = region_sales['金额'].sum()
    total_orders = len(region_sales)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    # 关键修改：按发运月份统计月度趋势数据
    region_sales['年月'] = region_sales['发运月份'].dt.to_period('M')
    monthly_trend = region_sales.groupby('年月').agg({
        '金额': ['sum', 'count', 'mean', 'std']
    }).reset_index()
    monthly_trend.columns = ['年月', '销售额', '订单数', '平均客单价', '标准差']

    # 转换日期格式为中文
    monthly_trend['年月_str'] = monthly_trend['年月'].apply(lambda x: f"{x.year}年{x.month}月")

    # 计算同比和环比
    monthly_trend['环比增长'] = monthly_trend['销售额'].pct_change() * 100
    monthly_trend['订单环比'] = monthly_trend['订单数'].pct_change() * 100

    # 订单金额分布分析
    bins = [0, 10000, 20000, 40000, float('inf')]
    labels = ['<1万', '1-2万', '2-4万', '>4万']
    region_sales['金额区间'] = pd.cut(region_sales['金额'], bins=bins, labels=labels)

    distribution = region_sales.groupby('金额区间').agg({
        '金额': ['count', 'sum', 'mean']
    }).reset_index()
    distribution.columns = ['金额区间', '订单数', '销售额', '平均金额']

    # 客户分析 - 按发运月份
    customer_monthly = region_sales.groupby(['年月', '经销商名称'])['金额'].sum().reset_index()
    active_customers = customer_monthly.groupby('年月')['经销商名称'].nunique().reset_index()
    active_customers.columns = ['年月', '活跃客户数']

    # 合并数据
    monthly_trend = monthly_trend.merge(active_customers, on='年月', how='left')

    # 创建2x2布局 - 增加高度和间距
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],  # 均等行高
        column_widths=[0.6, 0.4],  # 左列更宽
        subplot_titles=(
            '', '', '', ''  # 不使用内置标题
        ),
        specs=[
            [{"secondary_y": True}, {"type": "pie"}],
            [{"secondary_y": True}, {"secondary_y": False}]
        ],
        vertical_spacing=0.2,  # 增加垂直间距
        horizontal_spacing=0.18  # 增加水平间距
    )

    # 定义配色方案
    primary_color = '#667eea'
    primary_light = 'rgba(102, 126, 234, 0.1)'
    secondary_color = '#ff6b6b'
    tertiary_color = '#9b59b6'
    accent_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']

    # 1. 主趋势图（左上）
    fig.add_trace(
        go.Scatter(
            x=monthly_trend['年月_str'],
            y=monthly_trend['销售额'],
            mode='lines',
            name='销售额',
            line=dict(color=primary_color, width=3, shape='spline'),
            fill='tozeroy',
            fillcolor=primary_light,
            hovertemplate='%{x}<br>销售额: ¥%{y:,.0f}<br>环比: %{customdata:.1f}%<extra></extra>',
            customdata=monthly_trend['环比增长'].fillna(0)
        ),
        row=1, col=1, secondary_y=False
    )

    # 订单数折线图
    fig.add_trace(
        go.Scatter(
            x=monthly_trend['年月_str'],
            y=monthly_trend['订单数'],
            mode='lines+markers',
            name='订单数',
            line=dict(color=secondary_color, width=2.5, dash='dot'),
            marker=dict(size=6, color=secondary_color),
            hovertemplate='%{x}<br>订单数: %{y}笔<extra></extra>'
        ),
        row=1, col=1, secondary_y=True
    )

    # 2. 金额区间贡献饼图（右上）
    fig.add_trace(
        go.Pie(
            labels=distribution['金额区间'],
            values=distribution['销售额'],
            hole=0.45,
            marker=dict(
                colors=accent_colors,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=12),
            hovertemplate='%{label}<br>销售额: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>',
            pull=[0.05 if i == distribution['销售额'].idxmax() else 0 for i in range(len(distribution))]
        ),
        row=1, col=2
    )

    # 饼图中心文字
    fig.add_annotation(
        x=1.15, y=0.77,
        text=f"<b>总计</b><br>{format_amount(total_sales)}",
        showarrow=False,
        font=dict(size=13, color='#2d3748'),
        xref="paper", yref="paper"
    )

    # 3. 客单价与客户数合并图（左下）
    fig.add_trace(
        go.Bar(
            x=monthly_trend['年月_str'],
            y=monthly_trend['平均客单价'],
            name='平均客单价',
            marker=dict(
                color=tertiary_color,
                opacity=0.7
            ),
            hovertemplate='%{x}<br>客单价: ¥%{y:,.0f}<extra></extra>',
            yaxis='y3'
        ),
        row=2, col=1, secondary_y=False
    )

    # 活跃客户数折线图
    fig.add_trace(
        go.Scatter(
            x=monthly_trend['年月_str'],
            y=monthly_trend['活跃客户数'],
            mode='lines+markers+text',
            name='活跃客户数',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8, color='#e74c3c'),
            text=[f'{y}' for y in monthly_trend['活跃客户数']],
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='%{x}<br>活跃客户: %{y}家<extra></extra>',
            yaxis='y4'
        ),
        row=2, col=1, secondary_y=True
    )

    # 4. 环比增长率（右下）
    colors_bar = ['#2ecc71' if x > 0 else '#e74c3c' for x in monthly_trend['环比增长'].fillna(0)]

    fig.add_trace(
        go.Bar(
            x=monthly_trend['年月_str'],
            y=monthly_trend['环比增长'].fillna(0),
            name='销售额环比',
            marker=dict(color=colors_bar),
            text=[f'{x:.1f}%' if pd.notna(x) else '0%' for x in monthly_trend['环比增长']],
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate='%{x}<br>环比: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )

    # 添加零线
    fig.add_shape(
        type="line",
        x0=0, x1=1,
        y0=0, y1=0,
        xref="x4 domain", yref="y5",
        line=dict(color="#95a5a6", width=1, dash="dash"),
        opacity=0.5
    )

    # 添加优化的标题（位置调整，避免重叠）
    titles = [
        (0.3, 0.98, "销售额与订单数趋势(按发运月份)", 15),
        (0.8, 0.98, "金额区间贡献", 14),
        (0.3, 0.48, "平均客单价与活跃客户数", 14),
        (0.8, 0.48, "环比增长率", 14)
    ]

    for x, y, text, size in titles:
        fig.add_annotation(
            x=x, y=y,
            xref="paper", yref="paper",
            text=f"<b>{text}</b>",
            showarrow=False,
            font=dict(size=size, color='#2d3748'),
            align="center"
        )

    # 右下角动态指标
    if len(monthly_trend) > 1:
        latest_growth = monthly_trend['环比增长'].iloc[-1]
        growth_text = f"{'↑' if latest_growth > 0 else '↓'} {abs(latest_growth):.1f}%"
        fig.add_annotation(
            x=0.98, y=0.02,
            xref="paper", yref="paper",
            text=f"最新: {growth_text}",
            showarrow=False,
            font=dict(size=11, color=primary_color),
            bgcolor="rgba(240, 240, 240, 0.8)",
            borderpad=4
        )

    # 更新轴标签
    fig.update_xaxes(tickangle=-45, showgrid=False, tickfont=dict(size=9))
    fig.update_yaxes(title_text="销售额", row=1, col=1, secondary_y=False, showgrid=True, tickfont=dict(size=9))
    fig.update_yaxes(title_text="订单数", row=1, col=1, secondary_y=True, showgrid=False, tickfont=dict(size=9))
    fig.update_yaxes(title_text="客单价", row=2, col=1, secondary_y=False, showgrid=True, tickfont=dict(size=9))
    fig.update_yaxes(title_text="客户数", row=2, col=1, secondary_y=True, showgrid=False, tickfont=dict(size=9))
    fig.update_yaxes(title_text="(%)", row=2, col=2, showgrid=True, tickfont=dict(size=9))

    # 总体布局设置 - 增加高度
    fig.update_layout(
        height=1200,  # 增加到1200px
        showlegend=True,
        hovermode='closest',  # 使用closest模式，自动优化位置
        hoverdistance=20,  # 设置悬停距离
        plot_bgcolor='white',
        paper_bgcolor='white',
        # 删除title部分，不显示主标题
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
            itemsizing='constant'
        ),
        margin=dict(t=50, b=100, l=80, r=80),  # 减小顶部边距，因为没有标题了
        font=dict(family="Microsoft YaHei, Arial", size=10)
    )

    # 设置Plotly内置的悬停标签优化
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Microsoft YaHei"
        )
    )

    # 网格线样式
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')

    return fig


def calculate_metrics(customer_status, sales_data, monthly_data, current_year):
    """计算业务指标 - 彻底修复目标达成率计算逻辑"""

    print(f"=== calculate_metrics 调试信息 ===")
    print(f"输入参数 - current_year: {current_year}")
    print(f"销售数据总记录数: {len(sales_data)}")

    # 基础客户指标
    total_customers = len(customer_status)
    normal_customers = len(customer_status[customer_status['状态'] == '正常'])
    closed_customers = len(customer_status[customer_status['状态'] == '闭户'])
    normal_rate = (normal_customers / total_customers * 100) if total_customers > 0 else 0

    # 按发运月份筛选当前年度销售数据
    print(f"=== 筛选当前年度数据 ===")

    # 确保发运月份是datetime类型
    if sales_data['发运月份'].dtype != 'datetime64[ns]':
        sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'], errors='coerce')

    # 移除发运月份为空的行
    sales_data_clean = sales_data.dropna(subset=['发运月份']).copy()
    print(f"清理后数据行数: {len(sales_data_clean)}")

    # 按发运月份筛选当前年度销售数据
    current_year_sales = sales_data_clean[sales_data_clean['发运月份'].dt.year == current_year].copy()
    print(f"{current_year}年发运销售记录数: {len(current_year_sales)}")

    if len(current_year_sales) == 0:
        print(f"警告：{current_year}年没有发运数据")
        all_years = sales_data_clean['发运月份'].dt.year.unique()
        print(f"数据中包含的年份: {sorted(all_years)}")

        if len(all_years) > 0:
            latest_year = max(all_years)
            print(f"使用最新年份 {latest_year} 的数据")
            current_year_sales = sales_data_clean[sales_data_clean['发运月份'].dt.year == latest_year].copy()
            current_year = latest_year

    # 确保金额字段正确处理
    if '金额' in current_year_sales.columns:
        current_year_sales['金额'] = pd.to_numeric(
            current_year_sales['金额'].astype(str).str.replace(',', '').str.replace('，', ''),
            errors='coerce'
        ).fillna(0)

    total_sales = current_year_sales['金额'].sum()
    print(f"按发运月份计算的{current_year}年总销售额: {total_sales:,.0f}")

    # 同比增长
    last_year_total = monthly_data['往年同期'].sum() if '往年同期' in monthly_data.columns else 0
    growth_rate = ((total_sales - last_year_total) / last_year_total * 100) if last_year_total > 0 else 0

    # 计算时间进度（仅用于显示）
    from datetime import datetime, date
    current_date = datetime.now().date()
    year_start = date(current_year, 1, 1)
    year_end = date(current_year, 12, 31)
    total_days_in_year = (year_end - year_start).days + 1
    days_passed = (current_date - year_start).days + 1
    time_progress = min(days_passed / total_days_in_year, 1.0)

    print(f"年度进度: {days_passed}/{total_days_in_year}天 ({time_progress * 100:.1f}%)")

    # ===== 关键修复：目标达成分析 - 严格按年度目标计算 =====
    target_growth_factor = 1.1
    customer_region_map = monthly_data[
        ['客户', '所属大区']].drop_duplicates() if '所属大区' in monthly_data.columns else pd.DataFrame()
    customer_actual_sales = current_year_sales.groupby('经销商名称')['金额'].sum()

    # 计算年度目标
    customer_annual_targets = {}
    total_historical_target = monthly_data['月度指标'].sum() if '月度指标' in monthly_data.columns else 0

    for customer in customer_actual_sales.index:
        historical_sales = 0
        if '往年同期' in monthly_data.columns:
            historical_sales = monthly_data[monthly_data['客户'] == customer]['往年同期'].sum()

        if historical_sales > 0:
            estimated_annual_target = historical_sales * target_growth_factor
        else:
            avg_target = total_historical_target / len(monthly_data['客户'].unique()) if len(
                monthly_data['客户'].unique()) > 0 else 500000
            estimated_annual_target = avg_target * target_growth_factor

        customer_annual_targets[customer] = estimated_annual_target

    # ===== 彻底修复：目标达成分析 - 严格按年度目标计算，不考虑时间进度 =====
    achieved_customers = 0
    total_target_customers = len(customer_annual_targets)
    customer_achievement_details = []

    print(f"=== 目标达成分析（严格按年度目标）===")
    print(f"需要评估的客户数: {total_target_customers}")

    for customer, annual_target in customer_annual_targets.items():
        actual_sales = customer_actual_sales.get(customer, 0)

        if annual_target > 0:
            # 关键修复：严格按年度目标计算达成率，完全不考虑时间进度
            achievement_rate = (actual_sales / annual_target * 100)

            # 达成标准：实际销售额达到年度目标的80%即视为达成
            is_achieved = actual_sales >= (annual_target * 0.8)
            if is_achieved:
                achieved_customers += 1

            # 关键修复：确保存储的是基于年度目标的正确达成率
            customer_achievement_details.append({
                '客户': customer,
                '年度目标': annual_target,  # 存储年度目标
                '实际': actual_sales,  # 存储实际销售额
                '达成率': achievement_rate,  # 关键：这里存储的是基于年度目标的达成率
                '状态': '达成' if is_achieved else '未达成',
                '时间进度': time_progress * 100  # 仅用于显示，不影响计算
            })

    target_achievement_rate = (achieved_customers / total_target_customers * 100) if total_target_customers > 0 else 0

    print(f"目标达成客户数: {achieved_customers}/{total_target_customers}")
    print(f"目标达成率: {target_achievement_rate:.1f}%")

    # 验证达成率计算
    if customer_achievement_details:
        print(f"=== 验证达成率计算 ===")
        for i in range(min(3, len(customer_achievement_details))):
            detail = customer_achievement_details[i]
            manual_rate = (detail['实际'] / detail['年度目标'] * 100)
            print(f"客户: {detail['客户']}")
            print(f"  年度目标: {detail['年度目标']:,.0f}")
            print(f"  实际销售: {detail['实际']:,.0f}")
            print(f"  存储达成率: {detail['达成率']:.1f}%")
            print(f"  手工计算: {manual_rate:.1f}%")
            print(f"  计算正确: {abs(detail['达成率'] - manual_rate) < 0.01}")

    # 区域风险分析
    sales_with_region = pd.DataFrame()
    if not customer_region_map.empty:
        sales_with_region = current_year_sales.merge(
            customer_region_map, left_on='经销商名称', right_on='客户', how='left'
        )

    region_details = []
    max_dependency = 0
    max_dependency_region = ""

    if not sales_with_region.empty and '所属大区' in sales_with_region.columns:
        for region, group in sales_with_region.groupby('所属大区'):
            if pd.notna(region):
                customer_sales = group.groupby('经销商名称')['金额'].sum().sort_values(ascending=False)
                if len(customer_sales) > 0:
                    max_customer_sales = customer_sales.max()
                    total_region_sales = customer_sales.sum()
                    dependency = (max_customer_sales / total_region_sales * 100) if total_region_sales > 0 else 0

                    if dependency > max_dependency:
                        max_dependency = dependency
                        max_dependency_region = region

                    region_details.append({
                        '区域': region,
                        '总销售额': total_region_sales,
                        '客户数': len(customer_sales),
                        '最大客户依赖度': dependency,
                        '最大客户': customer_sales.index[0] if len(customer_sales) > 0 else '',
                        '最大客户销售额': max_customer_sales
                    })

    region_stats = pd.DataFrame(region_details) if region_details else pd.DataFrame()

    # RFM客户分析
    current_date_dt = datetime.now()
    customer_rfm = []

    for customer in customer_actual_sales.index:
        customer_orders = current_year_sales[current_year_sales['经销商名称'] == customer]
        if len(customer_orders) > 0:
            last_order_date = customer_orders['发运月份'].max()
            recency = (current_date_dt - last_order_date).days
            frequency = len(customer_orders)
            monetary = customer_orders['金额'].sum()

            if recency <= 30 and frequency >= 12 and monetary >= 1000000:
                customer_type = '钻石客户'
            elif recency <= 60 and frequency >= 8 and monetary >= 500000:
                customer_type = '黄金客户'
            elif recency <= 90 and frequency >= 6 and monetary >= 200000:
                customer_type = '白银客户'
            elif recency > 180 or frequency < 3:
                customer_type = '流失风险'
            else:
                customer_type = '潜力客户'

            customer_rfm.append({
                '客户': customer, 'R': recency, 'F': frequency, 'M': monetary,
                '类型': customer_type, '最近购买': last_order_date.strftime('%Y-%m-%d')
            })

    rfm_df = pd.DataFrame(customer_rfm) if customer_rfm else pd.DataFrame()

    # 客户类型统计
    if not rfm_df.empty:
        customer_type_counts = rfm_df['类型'].value_counts()
        diamond_customers = customer_type_counts.get('钻石客户', 0)
        gold_customers = customer_type_counts.get('黄金客户', 0)
        silver_customers = customer_type_counts.get('白银客户', 0)
        risk_customers = customer_type_counts.get('流失风险', 0)
        potential_customers = customer_type_counts.get('潜力客户', 0)
    else:
        diamond_customers = gold_customers = silver_customers = risk_customers = potential_customers = 0

    high_value_rate = ((diamond_customers + gold_customers) / normal_customers * 100) if normal_customers > 0 else 0

    # 客户集中度
    concentration_rate = 0
    if len(customer_actual_sales) > 0:
        sorted_sales = customer_actual_sales.sort_values(ascending=False)
        top20_count = max(1, int(len(sorted_sales) * 0.2))
        top20_sales = sorted_sales.head(top20_count).sum()
        concentration_rate = (top20_sales / total_sales * 100) if total_sales > 0 else 0

    print(f"=== 最终计算结果 ===")
    print(f"总销售额: {total_sales:,.0f}")
    print(f"正常客户数: {normal_customers}")
    print(f"目标达成率: {target_achievement_rate:.1f}%")

    return {
        'total_sales': total_sales, 'normal_customers': normal_customers, 'closed_customers': closed_customers,
        'normal_rate': normal_rate, 'growth_rate': growth_rate,
        'region_stats': region_stats, 'max_dependency': max_dependency, 'max_dependency_region': max_dependency_region,
        'target_achievement_rate': target_achievement_rate, 'achieved_customers': achieved_customers,
        'total_target_customers': total_target_customers,
        'diamond_customers': diamond_customers, 'gold_customers': gold_customers, 'silver_customers': silver_customers,
        'potential_customers': potential_customers, 'risk_customers': risk_customers,
        'high_value_rate': high_value_rate,
        'current_year': current_year, 'rfm_df': rfm_df, 'concentration_rate': concentration_rate,
        'customer_achievement_details': pd.DataFrame(
            customer_achievement_details) if customer_achievement_details else pd.DataFrame(),
        'sales_with_region': sales_with_region,
        'total_customers': total_customers,
        'time_progress': time_progress * 100,
        'days_passed': days_passed,
        'total_days_in_year': total_days_in_year,
        'target_calculation_method': '严格按年度目标计算，不考虑时间进度'
    }


def format_amount(amount):
    """格式化金额"""
    if amount >= 100000000:
        return f"¥{amount / 100000000:.1f}亿"
    elif amount >= 10000:
        return f"¥{amount / 10000:.0f}万"
    else:
        return f"¥{amount:,.0f}"


def calculate_customer_cycles(sales_data, current_year):
    """计算客户下单周期和异常行为"""
    # 获取最近12个月的数据
    end_date = sales_data['订单日期'].max()
    start_date = end_date - timedelta(days=365)
    recent_data = sales_data[sales_data['订单日期'] >= start_date].copy()

    # 计算每个客户的订单间隔
    customer_cycles = []

    for customer in recent_data['经销商名称'].unique():
        customer_orders = recent_data[recent_data['经销商名称'] == customer].sort_values('订单日期')

        if len(customer_orders) < 2:
            continue

        # 计算订单间隔
        order_dates = customer_orders['订单日期'].tolist()
        intervals = []
        order_details = []

        for i in range(1, len(order_dates)):
            interval = (order_dates[i] - order_dates[i - 1]).days
            intervals.append(interval)

            order_details.append({
                '日期': order_dates[i - 1],
                '下一单日期': order_dates[i],
                '间隔天数': interval,
                '金额': customer_orders.iloc[i - 1]['金额']
            })

        # 添加最后一个订单
        last_order = customer_orders.iloc[-1]
        days_since_last = (end_date - order_dates[-1]).days
        order_details.append({
            '日期': order_dates[-1],
            '下一单日期': None,
            '间隔天数': days_since_last,
            '金额': last_order['金额'],
            '距今天数': days_since_last
        })

        if intervals:
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 0

            # 预测下次订单时间
            predicted_date = order_dates[-1] + timedelta(days=int(avg_interval))

            customer_cycles.append({
                '客户': customer,
                '总销售额': customer_orders['金额'].sum(),
                '订单次数': len(customer_orders),
                '平均间隔': avg_interval,
                '间隔标准差': std_interval,
                '最后订单日期': order_dates[-1],
                '距今天数': days_since_last,
                '预测下单日期': predicted_date,
                '订单详情': order_details,
                '异常状态': '正常' if days_since_last <= avg_interval * 1.5 else
                '轻度异常' if days_since_last <= avg_interval * 2 else '严重异常'
            })

    # 按总销售额排序，获取Top 20
    cycles_df = pd.DataFrame(customer_cycles)
    if not cycles_df.empty:
        cycles_df = cycles_df.nlargest(20, '总销售额')  # 保持Top 20

    return cycles_df


def calculate_risk_prediction(sales_data, current_date=None):
    """计算客户风险预测模型"""
    if current_date is None:
        current_date = datetime.now()

    # 获取最近12个月的数据用于建模
    model_end_date = sales_data['订单日期'].max()
    model_start_date = model_end_date - timedelta(days=365)
    model_data = sales_data[sales_data['订单日期'] >= model_start_date].copy()

    risk_predictions = []

    for customer in model_data['经销商名称'].unique():
        customer_orders = model_data[model_data['经销商名称'] == customer].sort_values('订单日期')

        if len(customer_orders) < 3:  # 需要至少3个订单才能建模
            continue

        # 计算历史特征
        order_dates = customer_orders['订单日期'].tolist()
        order_amounts = customer_orders['金额'].tolist()

        # 计算间隔
        intervals = []
        for i in range(1, len(order_dates)):
            intervals.append((order_dates[i] - order_dates[i - 1]).days)

        # 基础统计
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals) if len(intervals) > 1 else avg_interval * 0.2
        avg_amount = np.mean(order_amounts)
        std_amount = np.std(order_amounts) if len(order_amounts) > 1 else avg_amount * 0.2

        # 计算趋势
        if len(intervals) >= 3:
            # 间隔趋势（是否在拉长）
            recent_intervals = intervals[-3:]
            interval_trend = (recent_intervals[-1] - recent_intervals[0]) / max(recent_intervals[0], 1)
        else:
            interval_trend = 0

        if len(order_amounts) >= 3:
            # 金额趋势（是否在下降）
            recent_amounts = order_amounts[-3:]
            amount_trend = (recent_amounts[-1] - recent_amounts[0]) / max(recent_amounts[0], 1)
        else:
            amount_trend = 0

        # 当前状态
        last_order_date = order_dates[-1]
        days_since_last = (current_date - last_order_date).days
        last_amount = order_amounts[-1]

        # 风险评分计算
        # 1. 断单风险
        if days_since_last > avg_interval:
            # 使用正态分布计算超期概率
            z_score = (days_since_last - avg_interval) / max(std_interval, 1)
            # 基础断单概率
            disconnect_risk_base = min(0.99, 1 / (1 + np.exp(-z_score)))
            # 考虑趋势调整
            disconnect_risk = disconnect_risk_base * (1 + interval_trend * 0.3)
        else:
            # 预测未来30天的断单风险
            future_days = days_since_last + 30
            z_score = (future_days - avg_interval) / max(std_interval, 1)
            disconnect_risk = min(0.99, 1 / (1 + np.exp(-z_score + 1)))

        # 2. 减量风险
        if last_amount < avg_amount * 0.7:
            amount_z_score = (avg_amount - last_amount) / max(std_amount, 1)
            reduction_risk_base = min(0.99, 1 / (1 + np.exp(-amount_z_score)))
            reduction_risk = reduction_risk_base * (1 - amount_trend * 0.3)
        else:
            reduction_risk = max(0.1, 0.3 + amount_trend * 0.5) if amount_trend < 0 else 0.1

        # 3. 综合流失风险
        # 权重：断单风险60%，减量风险40%
        churn_risk = disconnect_risk * 0.6 + reduction_risk * 0.4

        # 调整因子
        # 如果是老客户（订单数>10），降低风险
        if len(customer_orders) > 10:
            churn_risk *= 0.8

        # 如果最近有大额订单，降低风险
        if last_amount > avg_amount * 1.5:
            churn_risk *= 0.7

        # 确定风险等级
        if churn_risk >= 0.8:
            risk_level = '高风险'
            risk_color = '#e74c3c'
        elif churn_risk >= 0.5:
            risk_level = '中风险'
            risk_color = '#f39c12'
        elif churn_risk >= 0.2:
            risk_level = '低风险'
            risk_color = '#f1c40f'
        else:
            risk_level = '安全'
            risk_color = '#27ae60'

        # 确定主要风险类型
        if disconnect_risk > reduction_risk * 1.5:
            main_risk_type = '断单风险'
        elif reduction_risk > disconnect_risk * 1.5:
            main_risk_type = '减量风险'
        else:
            main_risk_type = '综合风险'

        # 生成行动建议
        if churn_risk >= 0.8:
            if days_since_last > avg_interval * 1.5:
                action = '立即电话联系，了解是否有问题'
            else:
                action = '密切关注，准备主动联系'
        elif churn_risk >= 0.5:
            action = '定期回访，了解需求变化'
        else:
            action = '常规维护'

        # 预测下次订单
        predicted_next_order = last_order_date + timedelta(days=int(avg_interval))
        predicted_amount = avg_amount * (1 + amount_trend * 0.2)

        # 计算置信区间
        confidence_interval = std_interval / max(avg_interval, 1) * 100

        risk_predictions.append({
            '客户': customer,
            '流失风险概率': churn_risk * 100,
            '断单风险': disconnect_risk * 100,
            '减量风险': reduction_risk * 100,
            '置信区间': min(20, confidence_interval),
            '风险等级': risk_level,
            '风险颜色': risk_color,
            '主要风险': main_risk_type,
            '最后订单日期': last_order_date,
            '距今天数': days_since_last,
            '平均周期': avg_interval,
            '平均金额': avg_amount,
            '最后金额': last_amount,
            '建议行动': action,
            '预测下单日期': predicted_next_order,
            '预测金额': predicted_amount,
            '历史订单数': len(customer_orders),
            '金额趋势': '下降' if amount_trend < -0.1 else '上升' if amount_trend > 0.1 else '稳定',
            '周期趋势': '延长' if interval_trend > 0.1 else '缩短' if interval_trend < -0.1 else '稳定'
        })

    # 转换为DataFrame并排序
    risk_df = pd.DataFrame(risk_predictions)
    if not risk_df.empty:
        risk_df = risk_df.sort_values('流失风险概率', ascending=False)

    return risk_df


def create_risk_dashboard(risk_df):
    """创建风险仪表盘"""
    # 1. 风险分布图（增强悬停信息）
    fig_dist = go.Figure()

    # 按风险等级分组
    risk_levels = ['高风险', '中风险', '低风险', '安全']
    colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60']

    for level, color in zip(risk_levels, colors):
        level_data = risk_df[risk_df['风险等级'] == level]
        if not level_data.empty:
            # 准备悬停信息
            hover_customers = level_data.head(10)  # 显示前10个客户
            hover_text = f"<b>{level}</b><br>客户数: {len(level_data)}<br><br><b>客户列表：</b><br>"
            for _, customer in hover_customers.iterrows():
                hover_text += f"• {customer['客户']} (风险:{customer['流失风险概率']:.0f}%)<br>"
            if len(level_data) > 10:
                hover_text += f"... 还有{len(level_data) - 10}个客户"

            fig_dist.add_trace(go.Bar(
                name=level,
                x=[level],
                y=[len(level_data)],
                marker_color=color,
                text=len(level_data),
                textposition='auto',
                hovertemplate=hover_text + '<extra></extra>'
            ))

    fig_dist.update_layout(
        title='客户风险等级分布',
        xaxis_title='风险等级',
        yaxis_title='客户数量',
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # 2. 风险概率分布直方图（增强悬停信息）
    fig_hist = go.Figure()

    # 创建直方图数据
    hist_data = np.histogram(risk_df['流失风险概率'], bins=20, range=(0, 100))
    bin_centers = (hist_data[1][:-1] + hist_data[1][1:]) / 2

    # 为每个bin准备客户列表
    hover_texts = []
    for i in range(len(hist_data[0])):
        bin_min = hist_data[1][i]
        bin_max = hist_data[1][i + 1]
        bin_customers = risk_df[(risk_df['流失风险概率'] >= bin_min) & (risk_df['流失风险概率'] < bin_max)]

        hover_text = f"<b>风险区间: {bin_min:.0f}%-{bin_max:.0f}%</b><br>"
        hover_text += f"客户数: {len(bin_customers)}<br><br>"

        if len(bin_customers) > 0:
            hover_text += "<b>客户列表：</b><br>"
            for _, customer in bin_customers.head(5).iterrows():
                hover_text += f"• {customer['客户']} ({customer['流失风险概率']:.1f}%)<br>"
            if len(bin_customers) > 5:
                hover_text += f"... 还有{len(bin_customers) - 5}个客户"

        hover_texts.append(hover_text)

    fig_hist.add_trace(go.Bar(
        x=bin_centers,
        y=hist_data[0],
        marker_color='#667eea',
        opacity=0.7,
        name='客户分布',
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=hover_texts
    ))

    # 添加风险区间标注
    fig_hist.add_vrect(x0=80, x1=100, fillcolor="#e74c3c", opacity=0.1,
                       annotation_text="高风险区", annotation_position="top")
    fig_hist.add_vrect(x0=50, x1=80, fillcolor="#f39c12", opacity=0.1,
                       annotation_text="中风险区", annotation_position="top")
    fig_hist.add_vrect(x0=20, x1=50, fillcolor="#f1c40f", opacity=0.1,
                       annotation_text="低风险区", annotation_position="top")
    fig_hist.add_vrect(x0=0, x1=20, fillcolor="#27ae60", opacity=0.1,
                       annotation_text="安全区", annotation_position="top")

    fig_hist.update_layout(
        title='客户流失风险概率分布',
        xaxis_title='流失风险概率 (%)',
        yaxis_title='客户数量',
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # 3. 风险矩阵散点图（优化显示）
    fig_matrix = go.Figure()

    # 为每个客户创建散点
    for _, customer in risk_df.iterrows():
        hover_text = f"<b style='font-size:14px;'>{customer['客户']}</b><br><br>" + \
                     f"<b>📊 风险评估结果：</b><br>" + \
                     f"• 综合流失风险: <b style='color:{customer['风险颜色']}'>{customer['流失风险概率']:.1f}%</b><br>" + \
                     f"• 断单风险: {customer['断单风险']:.1f}%<br>" + \
                     f"• 减量风险: {customer['减量风险']:.1f}%<br>" + \
                     f"• 风险等级: <b>{customer['风险等级']}</b><br><br>" + \
                     f"<b>📈 业务指标：</b><br>" + \
                     f"• 最后订单: {customer['最后订单日期'].strftime('%Y-%m-%d')} ({customer['距今天数']}天前)<br>" + \
                     f"• 平均下单周期: {customer['平均周期']:.0f}天<br>" + \
                     f"• 平均订单金额: {format_amount(customer['平均金额'])}<br>" + \
                     f"• 最后订单金额: {format_amount(customer['最后金额'])}<br><br>" + \
                     f"<b>📋 趋势分析：</b><br>" + \
                     f"• 金额趋势: {customer['金额趋势']}<br>" + \
                     f"• 周期趋势: {customer['周期趋势']}<br><br>" + \
                     f"<b>🎯 建议行动：</b><br>" + \
                     f"<span style='color:{customer['风险颜色']}'>{customer['建议行动']}</span>"

        # 只为高风险客户显示标签
        show_text = customer['流失风险概率'] >= 70

        fig_matrix.add_trace(go.Scatter(
            x=[customer['断单风险']],
            y=[customer['减量风险']],
            mode='markers+text' if show_text else 'markers',
            marker=dict(
                size=12,
                color=customer['风险颜色'],
                line=dict(color='white', width=2),
                opacity=0.8
            ),
            text=customer['客户'][:8] + '...' if len(customer['客户']) > 8 and show_text else '',
            textposition='top center',
            textfont=dict(size=9),
            name=customer['风险等级'],
            hovertemplate=hover_text + '<extra></extra>',
            showlegend=False
        ))

    # 添加风险区域
    fig_matrix.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100,
                         fillcolor="rgba(231, 76, 60, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100,
                         fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50,
                         fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50,
                         fillcolor="rgba(39, 174, 96, 0.1)", layer="below", line=dict(width=0))

    # 添加区域标签
    fig_matrix.add_annotation(x=75, y=75, text="高风险区", showarrow=False,
                              font=dict(size=14, color='#e74c3c'), opacity=0.7)
    fig_matrix.add_annotation(x=25, y=75, text="断单风险", showarrow=False,
                              font=dict(size=12, color='#f39c12'), opacity=0.7)
    fig_matrix.add_annotation(x=75, y=25, text="减量风险", showarrow=False,
                              font=dict(size=12, color='#f39c12'), opacity=0.7)
    fig_matrix.add_annotation(x=25, y=25, text="低风险区", showarrow=False,
                              font=dict(size=14, color='#27ae60'), opacity=0.7)

    # 添加对角线
    fig_matrix.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode='lines',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig_matrix.update_layout(
        title=dict(
            text='客户风险矩阵 - 断单风险 vs 减量风险',
            font=dict(size=16, color='#2d3748')
        ),
        xaxis=dict(title='断单风险 (%)', range=[-5, 105]),
        yaxis=dict(title='减量风险 (%)', range=[-5, 105]),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    return fig_dist, fig_hist, fig_matrix


def create_timeline_chart(cycles_df):
    """创建美化的客户下单时间轴图表"""
    fig = go.Figure()

    # 设置颜色方案
    color_scale = {
        '正常': '#48bb78',
        '轻度异常': '#ed8936',
        '严重异常': '#e53e3e'
    }

    # 为每个客户创建一条时间轴（增加间距）
    for idx, customer_data in cycles_df.iterrows():
        y_position = idx * 1.3  # 适度的行间距
        orders = customer_data['订单详情']

        # 收集所有订单数据用于绘制
        dates = []
        amounts = []
        colors = []
        sizes = []
        hover_texts = []

        for i, order in enumerate(orders):
            dates.append(order['日期'])
            amounts.append(order['金额'])

            # 确定颜色和大小
            if order.get('距今天数'):
                # 最后一个订单
                color = color_scale.get(customer_data['异常状态'], '#667eea')
                size = 18 if customer_data['异常状态'] == '严重异常' else 13  # 调整大小差异
            else:
                # 历史订单
                interval = order['间隔天数']
                avg_interval = customer_data['平均间隔']
                if interval > avg_interval * 1.5:
                    color = color_scale['轻度异常']
                    size = 13
                else:
                    color = color_scale['正常']
                    size = 10

            colors.append(color)
            sizes.append(size)

            # 构建悬停文本
            hover_text = f"<b>{customer_data['客户']}</b><br>"
            hover_text += f"订单日期: {order['日期'].strftime('%Y-%m-%d')}<br>"
            hover_text += f"订单金额: <b>{format_amount(order['金额'])}</b><br>"
            if order.get('下一单日期'):
                hover_text += f"间隔天数: {order['间隔天数']}天"
            else:
                hover_text += f"距今天数: <b>{order['间隔天数']}天</b><br>"
                hover_text += f"状态: <b>{customer_data['异常状态']}</b>"

            hover_texts.append(hover_text)

        # 绘制订单连线（渐变效果）
        fig.add_trace(go.Scatter(
            x=dates,
            y=[y_position] * len(dates),
            mode='lines',
            line=dict(
                color='rgba(150, 150, 150, 0.25)',  # 降低透明度
                width=2,  # 减小线宽
                shape='spline'
            ),
            hoverinfo='skip',
            showlegend=False
        ))

        # 绘制订单点（根据金额大小调整）
        normalized_amounts = np.array(amounts) / max(amounts) * 15 + 8  # 减小标记大小

        fig.add_trace(go.Scatter(
            x=dates,
            y=[y_position] * len(dates),
            mode='markers',
            marker=dict(
                size=normalized_amounts,
                color=colors,
                line=dict(color='white', width=1.5),  # 减小边框宽度
                opacity=0.9
            ),
            text=[f"¥{amount / 10000:.0f}万" if amount >= 10000 else f"¥{amount:.0f}"
                  for amount in amounts],
            textposition='top center',
            textfont=dict(size=8, color='#666'),  # 减小字体大小
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_texts,
            showlegend=False
        ))

        # 添加客户名称
        fig.add_annotation(
            x=dates[0] - timedelta(days=5),
            y=y_position,
            text=customer_data['客户'][:10] + '...' if len(customer_data['客户']) > 10 else customer_data['客户'],
            xanchor='right',
            showarrow=False,
            font=dict(size=10, color='#2d3748')  # 稍微减小字体
        )

        # 添加平均周期基准（虚线）
        avg_interval_days = customer_data['平均间隔']
        reference_dates = []
        ref_date = dates[0]
        while ref_date <= dates[-1] + timedelta(days=30):
            reference_dates.append(ref_date)
            ref_date += timedelta(days=avg_interval_days)

        fig.add_trace(go.Scatter(
            x=reference_dates,
            y=[y_position - 0.25] * len(reference_dates),  # 调整位置以匹配新的间距
            mode='markers',
            marker=dict(
                symbol='line-ns',
                size=6,  # 减小参考线标记大小
                color='rgba(102, 126, 234, 0.25)'  # 降低透明度
            ),
            hoverinfo='skip',
            showlegend=False
        ))

        # 添加预测点
        if customer_data['预测下单日期'] > datetime.now():
            fig.add_trace(go.Scatter(
                x=[customer_data['预测下单日期']],
                y=[y_position],
                mode='markers+text',
                marker=dict(
                    size=12,  # 减小预测点大小
                    color='rgba(102, 126, 234, 0.5)',
                    symbol='circle-open',
                    line=dict(width=2.5)  # 稍微减小线宽
                ),
                text='预测',
                textposition='top center',
                textfont=dict(size=8, color='#667eea'),  # 减小字体
                hovertemplate=f"预测下单日期: {customer_data['预测下单日期'].strftime('%Y-%m-%d')}<extra></extra>",
                showlegend=False
            ))

    # 添加交替背景（提高可读性）
    for i in range(0, len(cycles_df), 2):
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="y",
            x0=0,
            x1=1,
            y0=i * 1.3 - 0.4,
            y1=min((i + 1) * 1.3 - 0.4, len(cycles_df) * 1.3 - 0.5),
            fillcolor="rgba(240, 240, 240, 0.3)",
            layer="below",
            line=dict(width=0)
        )

    # 添加渐变背景区域（表示时间流逝）
    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=datetime.now() - timedelta(days=30),
        x1=datetime.now() + timedelta(days=30),
        y0=0,
        y1=1,
        fillcolor="rgba(102, 126, 234, 0.05)",
        layer="below",
        line=dict(width=0)
    )

    # 添加今日标记线
    current_date = datetime.now()
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(
            color="rgba(102, 126, 234, 0.5)",
            width=2,
            dash="dash"
        )
    )

    # 添加今日标注
    fig.add_annotation(
        x=current_date,
        y=1.02,
        yref="paper",
        text="今日",
        showarrow=False,
        font=dict(size=12, color="rgba(102, 126, 234, 0.8)"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(102, 126, 234, 0.5)",
        borderwidth=1,
        borderpad=4
    )

    # 更新布局
    fig.update_layout(
        height=max(800, len(cycles_df) * 60),  # 调整高度以适应20个客户
        xaxis=dict(
            title="时间轴",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.05)',
            type='date',
            tickformat='%Y-%m',
            dtick='M1'
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            range=[-0.5, len(cycles_df) * 1.3 - 0.5],  # 调整范围以匹配新的y位置
            autorange='reversed'
        ),
        hovermode='closest',
        paper_bgcolor='white',
        plot_bgcolor='rgba(250, 250, 250, 0.8)',
        margin=dict(l=150, r=50, t=60, b=60),  # 增加左边距以容纳客户名称
        dragmode='pan'
    )

    # 添加图例
    legend_elements = [
        ('正常', '#48bb78', 'circle'),
        ('轻度异常', '#ed8936', 'circle'),
        ('严重异常', '#e53e3e', 'circle'),
        ('预测', 'rgba(102, 126, 234, 0.5)', 'circle-open')
    ]

    for i, (name, color, symbol) in enumerate(legend_elements):
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol=symbol, line=dict(width=1.5, color='white')),  # 调整图例标记大小
            showlegend=True,
            name=name
        ))

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        )
    )

    return fig


def create_enhanced_charts(metrics, sales_data, monthly_data):
    """创建增强图表 - 修复目标达成散点图"""
    global ECHARTS_AVAILABLE  # 声明使用全局变量
    charts = {}

    # 1. 客户健康雷达图
    categories = ['客户健康度', '目标达成率', '价值贡献度', '客户活跃度', '风险分散度']
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics[
                                                                                                             'normal_customers'] > 0 else 0,
        100 - metrics['max_dependency']
    ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', name='当前状态',
        fillcolor='rgba(102, 126, 234, 0.3)', line=dict(color='#667eea', width=3),
        hovertemplate='<b>%{theta}</b><br>数值: %{r:.1f}%<br><extra></extra>'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=[85, 80, 70, 85, 70], theta=categories, fill='toself', name='目标基准',
        fillcolor='rgba(255, 99, 71, 0.1)', line=dict(color='#ff6347', width=2, dash='dash')
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%'),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=True, height=450,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    charts['health_radar'] = fig_radar

    # 2. Top20客户贡献分析
    if not metrics['rfm_df'].empty:
        top20_customers = metrics['rfm_df'].nlargest(20, 'M')
        total_sales = metrics['rfm_df']['M'].sum()

        top20_customers['销售额占比'] = (top20_customers['M'] / total_sales * 100).round(2)
        top20_customers['累计占比'] = top20_customers['销售额占比'].cumsum()

        fig_top20 = make_subplots(specs=[[{"secondary_y": True}]])

        fig_top20.add_trace(go.Bar(
            x=top20_customers['客户'], y=top20_customers['M'], name='销售额',
            marker=dict(color='#667eea', opacity=0.8),
            hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.0f}<br>占比: %{customdata:.1f}%<extra></extra>',
            customdata=top20_customers['销售额占比']
        ), secondary_y=False)

        fig_top20.add_trace(go.Scatter(
            x=top20_customers['客户'], y=top20_customers['累计占比'], name='累计占比',
            mode='lines+markers', line=dict(color='#ff8800', width=3),
            marker=dict(size=8, color='#ff8800'),
            hovertemplate='<b>%{x}</b><br>累计占比: %{y:.1f}%<extra></extra>'
        ), secondary_y=True)

        fig_top20.add_hline(y=80, line_dash="dash", line_color="#e74c3c",
                            annotation_text="80%贡献线", secondary_y=True)

        fig_top20.update_xaxes(title_text="客户名称", tickangle=-45, showgrid=True, gridwidth=1,
                               gridcolor='rgba(0,0,0,0.05)')
        fig_top20.update_yaxes(title_text="销售额", secondary_y=False, showgrid=True, gridwidth=1,
                               gridcolor='rgba(0,0,0,0.05)')
        fig_top20.update_yaxes(title_text="累计占比 (%)", range=[0, 105], secondary_y=True)

        fig_top20.update_layout(
            height=500, hovermode='x unified',
            margin=dict(t=60, b=100, l=60, r=60),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=True
        )
        charts['top20'] = fig_top20

    # 3. 区域风险矩阵
    if not metrics['region_stats'].empty:
        fig_risk = go.Figure()

        # 添加背景区域
        fig_risk.add_shape(type="rect", x0=0, y0=30, x1=100, y1=100,
                           fillcolor="rgba(231, 76, 60, 0.1)", layer="below", line=dict(width=0))
        fig_risk.add_shape(type="rect", x0=0, y0=15, x1=100, y1=30,
                           fillcolor="rgba(243, 156, 18, 0.1)", layer="below", line=dict(width=0))
        fig_risk.add_shape(type="rect", x0=0, y0=0, x1=100, y1=15,
                           fillcolor="rgba(39, 174, 96, 0.1)", layer="below", line=dict(width=0))

        for _, region in metrics['region_stats'].iterrows():
            color = '#e74c3c' if region['最大客户依赖度'] > 30 else '#f39c12' if region[
                                                                                     '最大客户依赖度'] > 15 else '#27ae60'
            fig_risk.add_trace(go.Scatter(
                x=[region['客户数']], y=[region['最大客户依赖度']], mode='markers+text',
                marker=dict(size=max(15, min(60, region['总销售额'] / 100000)), color=color,
                            line=dict(color='white', width=2), opacity=0.8),
                text=region['区域'], textposition="top center", name=region['区域'],
                hovertemplate=f"<b>{region['区域']}</b><br>客户数: {region['客户数']}家<br>" +
                              f"依赖度: {region['最大客户依赖度']:.1f}%<br>" +
                              f"总销售: {format_amount(region['总销售额'])}<extra></extra>"
            ))

        fig_risk.add_hline(y=30, line_dash="dash", line_color="#e74c3c",
                           annotation_text="高风险线(30%)")
        fig_risk.add_hline(y=15, line_dash="dash", line_color="#f39c12",
                           annotation_text="中风险线(15%)")

        fig_risk.update_layout(
            xaxis=dict(title="客户数量", gridcolor='rgba(200,200,200,0.3)', showgrid=True),
            yaxis=dict(title="最大客户依赖度(%)", gridcolor='rgba(200,200,200,0.3)', showgrid=True,
                       range=[0, max(100, metrics['region_stats']['最大客户依赖度'].max() * 1.1)]),
            height=500, showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=20, b=60, l=60, r=60)
        )
        charts['risk_matrix'] = fig_risk

    # 4. 优化的价值分层图（使用Plotly树状图）
    if not metrics['rfm_df'].empty:
        # 使用更鲜明的配色方案
        customer_types = [
            ('钻石客户', '#e74c3c', '💎'),  # 鲜红色 - 最高价值
            ('黄金客户', '#f39c12', '🏆'),  # 金橙色 - 高价值
            ('白银客户', '#3498db', '🥈'),  # 天蓝色 - 中等价值
            ('潜力客户', '#2ecc71', '🌟'),  # 翠绿色 - 有潜力
            ('流失风险', '#95a5a6', '⚠️')  # 灰色 - 风险客户
        ]

        # 统计总客户数
        total_count = len(metrics['rfm_df'])

        # 准备数据
        data_for_treemap = []

        # 添加根节点
        data_for_treemap.append({
            'labels': '全部客户',
            'parents': '',
            'values': total_count,
            'text': f'全部客户<br>{total_count}家',
            'color': '#9b59b6'
        })

        # 为每个客户类型准备悬停信息
        for customer_type, color, emoji in customer_types:
            type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
            count = len(type_customers)

            if count > 0:
                percentage = count / total_count * 100

                # 获取Top 10客户用于悬停显示
                top_customers = type_customers.nlargest(10, 'M')

                # 构建悬停文本 - 包含客户列表
                hover_lines = []
                hover_lines.append(f"<b>{emoji} {customer_type}</b>")
                hover_lines.append(f"客户数: {count}家 ({percentage:.1f}%)")
                hover_lines.append("")
                hover_lines.append("<b>Top 10客户：</b>")

                for idx, (_, cust) in enumerate(top_customers.iterrows(), 1):
                    customer_name = cust['客户']
                    if len(customer_name) > 15:
                        customer_name = customer_name[:15] + "..."
                    hover_lines.append(f"{idx}. {customer_name} ({format_amount(cust['M'])})")

                if len(type_customers) > 10:
                    hover_lines.append(f"... 还有{len(type_customers) - 10}个客户")

                hover_text = "<br>".join(hover_lines)

                data_for_treemap.append({
                    'labels': f"{emoji} {customer_type}",
                    'parents': '全部客户',
                    'values': count,
                    'text': f"{emoji} {customer_type}<br>{count}家",  # 简化显示文本
                    'color': color,
                    'hover_text': hover_text,
                    'percentage': percentage
                })

        # 创建数据框
        df_treemap = pd.DataFrame(data_for_treemap)

        # 创建树状图
        fig_treemap = go.Figure(go.Treemap(
            labels=df_treemap['labels'],
            parents=df_treemap['parents'],
            values=df_treemap['values'],
            text=df_treemap['text'],
            textinfo="text",
            customdata=df_treemap[['hover_text', 'percentage']].values if 'hover_text' in df_treemap.columns else None,
            hovertemplate='%{customdata[0]}<extra></extra>' if 'hover_text' in df_treemap.columns else '%{label}<br>%{value}家<extra></extra>',
            marker=dict(
                colors=df_treemap['color'],
                line=dict(width=3, color='white')
            ),
            textfont=dict(size=16, family="Microsoft YaHei")
        ))

        fig_treemap.update_layout(
            title=dict(
                text="客户价值分层流向分析",
                font=dict(size=20, color='#2d3748', family="Microsoft YaHei"),
                x=0.5,
                xanchor='center'
            ),
            height=600,
            margin=dict(t=80, b=20, l=20, r=20),
            paper_bgcolor='#f8f9fa',
            plot_bgcolor='white'
        )

        charts['sankey'] = fig_treemap

    # 5. 月度趋势图
    if not sales_data.empty:
        try:
            sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
            monthly_sales = sales_data.groupby('年月')['金额'].agg(['sum', 'count']).reset_index()
            monthly_sales['年月'] = monthly_sales['年月'].astype(str)

            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

            fig_trend.add_trace(go.Scatter(
                x=monthly_sales['年月'], y=monthly_sales['sum'], mode='lines+markers',
                name='销售额', fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color='#667eea', width=3),
                hovertemplate='月份: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
            ), secondary_y=False)

            fig_trend.add_trace(go.Scatter(
                x=monthly_sales['年月'], y=monthly_sales['count'], mode='lines+markers',
                name='订单数', line=dict(color='#ff6b6b', width=2),
                hovertemplate='月份: %{x}<br>订单数: %{y}笔<extra></extra>'
            ), secondary_y=True)

            fig_trend.update_xaxes(title_text="月份", showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
            fig_trend.update_yaxes(title_text="销售额", secondary_y=False, showgrid=True, gridwidth=1,
                                   gridcolor='rgba(0,0,0,0.05)')
            fig_trend.update_yaxes(title_text="订单数", secondary_y=True)
            fig_trend.update_layout(
                height=450, hovermode='x unified',
                margin=dict(t=60, b=60, l=60, r=60),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            charts['trend'] = fig_trend
        except Exception as e:
            print(f"趋势图创建失败: {e}")

    # 6. 彻底修复：目标达成散点图
    try:
        print(f"=== 创建目标达成散点图 ===")
        if not metrics['customer_achievement_details'].empty:
            achievement_df = metrics['customer_achievement_details'].copy()
            print(f"原始数据行数: {len(achievement_df)}")
            print(f"数据字段: {achievement_df.columns.tolist()}")

            # 数据验证和清理
            required_columns = ['年度目标', '实际', '达成率', '客户']
            missing_columns = [col for col in required_columns if col not in achievement_df.columns]
            if missing_columns:
                print(f"缺少必要字段: {missing_columns}")
                charts['target_scatter'] = None
            else:
                # 确保数据类型正确
                achievement_df = achievement_df.dropna(subset=['年度目标', '实际'])
                achievement_df = achievement_df[achievement_df['年度目标'] > 0]
                achievement_df = achievement_df[achievement_df['实际'] >= 0]

                print(f"清理后数据行数: {len(achievement_df)}")

                if not achievement_df.empty and len(achievement_df) > 0:
                    # ===== 关键修复：重新验证并修正达成率 =====
                    print(f"=== 重新验证达成率计算 ===")

                    # 重新计算达成率，确保正确
                    achievement_df['达成率_验证'] = (achievement_df['实际'] / achievement_df['年度目标'] * 100)

                    # 检查是否有差异
                    for i in range(min(3, len(achievement_df))):
                        row = achievement_df.iloc[i]
                        original_rate = row['达成率']
                        verified_rate = row['达成率_验证']
                        print(f"客户: {row['客户']}")
                        print(f"  年度目标: {row['年度目标']:,.0f}")
                        print(f"  实际销售: {row['实际']:,.0f}")
                        print(f"  原始达成率: {original_rate:.1f}%")
                        print(f"  验证达成率: {verified_rate:.1f}%")
                        print(f"  是否一致: {abs(original_rate - verified_rate) < 0.1}")

                    # 使用验证后的达成率
                    achievement_df['达成率'] = achievement_df['达成率_验证']

                    # 计算颜色和大小
                    colors = ['#48bb78' if rate >= 100 else '#ffd93d' if rate >= 80 else '#ff6b6b'
                              for rate in achievement_df['达成率']]
                    sizes = [max(8, min(40, rate / 5)) for rate in achievement_df['达成率']]

                    fig_scatter = go.Figure()

                    # 添加散点 - 确保使用正确的数据
                    fig_scatter.add_trace(go.Scatter(
                        x=achievement_df['年度目标'],  # X轴：年度目标
                        y=achievement_df['实际'],  # Y轴：实际销售额
                        mode='markers',
                        marker=dict(
                            size=sizes,
                            color=colors,
                            line=dict(width=2, color='white'),
                            opacity=0.8
                        ),
                        text=achievement_df['客户'],
                        name='客户达成情况',
                        # 关键修复：悬停信息使用验证后的达成率
                        hovertemplate='<b>%{text}</b><br>' +
                                      '年度目标: ¥%{x:,.0f}<br>' +
                                      '实际销售: ¥%{y:,.0f}<br>' +
                                      '达成率: %{customdata:.1f}%<extra></extra>',
                        customdata=achievement_df['达成率']  # 使用验证后的达成率
                    ))

                    # 添加参考线
                    max_val = max(achievement_df['年度目标'].max(), achievement_df['实际'].max()) * 1.1

                    # 100%达成线 (y = x)
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val], y=[0, max_val], mode='lines', name='目标线(100%)',
                        line=dict(color='#e74c3c', width=3, dash='dash'),
                        hoverinfo='skip'
                    ))

                    # 80%达成线 (y = 0.8x)
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val], y=[0, max_val * 0.8], mode='lines', name='达成线(80%)',
                        line=dict(color='#f39c12', width=2, dash='dot'),
                        hoverinfo='skip'
                    ))

                    fig_scatter.update_layout(
                        title="客户年度目标 vs 实际销售额",
                        xaxis_title="年度目标 (¥)",
                        yaxis_title="实际销售额 (¥)",
                        height=500,
                        hovermode='closest',
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(t=60, b=60, l=60, r=60),
                        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)'),
                        showlegend=True
                    )

                    charts['target_scatter'] = fig_scatter
                    print(f"目标散点图创建成功，数据点数量: {len(achievement_df)}")

                    # 最终验证：输出修正后的达成率示例
                    if len(achievement_df) > 0:
                        sample = achievement_df.iloc[0]
                        print(f"=== 最终验证 ===")
                        print(f"示例客户: {sample['客户']}")
                        print(f"年度目标: {sample['年度目标']:,.0f}")
                        print(f"实际销售: {sample['实际']:,.0f}")
                        print(f"最终达成率: {sample['达成率']:.1f}%")
                        print(f"数学验证: {sample['实际'] / sample['年度目标'] * 100:.1f}%")
                else:
                    print("目标达成数据为空或无效")
                    charts['target_scatter'] = None
        else:
            print("没有客户目标达成数据")
            charts['target_scatter'] = None
    except Exception as e:
        print(f"目标散点图创建失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        charts['target_scatter'] = None

    return charts


def create_enhanced_trend_analysis(sales_data, monthly_data, selected_region='全国'):
    """创建增强的趋势分析图表"""
    # 获取区域数据
    if selected_region == '全国':
        # 全国数据
        region_sales = sales_data.copy()
    else:
        # 特定区域数据
        customer_region_map = monthly_data[['客户', '所属大区']].drop_duplicates()
        sales_with_region = sales_data.merge(
            customer_region_map, left_on='经销商名称', right_on='客户', how='left'
        )
        region_sales = sales_with_region[sales_with_region['所属大区'] == selected_region]

    if region_sales.empty:
        return None, None, None, None

    # 计算基础指标
    total_sales = region_sales['金额'].sum()
    total_orders = len(region_sales)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    # 订单金额分布分析
    bins = [0, 10000, 20000, 40000, float('inf')]
    labels = ['<1万', '1-2万', '2-4万', '>4万']
    region_sales['金额区间'] = pd.cut(region_sales['金额'], bins=bins, labels=labels)

    # 计算各区间的订单数和金额
    distribution = region_sales.groupby('金额区间').agg({
        '金额': ['count', 'sum']
    }).reset_index()
    distribution.columns = ['金额区间', '订单数', '销售额']

    # 月度趋势数据
    region_sales['年月'] = region_sales['订单日期'].dt.to_period('M')
    monthly_trend = region_sales.groupby('年月').agg({
        '金额': ['sum', 'count', 'mean']
    }).reset_index()
    monthly_trend.columns = ['年月', '销售额', '订单数', '平均客单价']
    monthly_trend['年月'] = monthly_trend['年月'].astype(str)

    # 创建综合分析图表
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.3, 0.7],
        column_widths=[0.5, 0.5],
        subplot_titles=('月度销售趋势', '月度订单数趋势', '订单金额分布', '金额区间贡献度'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True, "colspan": 2}, None]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 1. 销售额趋势（左上）
    fig.add_trace(
        go.Scatter(
            x=monthly_trend['年月'],
            y=monthly_trend['销售额'],
            mode='lines+markers',
            name='销售额',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            hovertemplate='月份: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

    # 2. 订单数趋势（右上）
    fig.add_trace(
        go.Scatter(
            x=monthly_trend['年月'],
            y=monthly_trend['订单数'],
            mode='lines+markers',
            name='订单数',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8),
            hovertemplate='月份: %{x}<br>订单数: %{y}笔<extra></extra>'
        ),
        row=1, col=2
    )

    # 3. 订单金额分布（下方左侧）
    fig.add_trace(
        go.Bar(
            x=distribution['金额区间'],
            y=distribution['订单数'],
            name='订单数',
            marker_color='#667eea',
            opacity=0.7,
            yaxis='y3',
            hovertemplate='%{x}<br>订单数: %{y}笔<extra></extra>'
        ),
        row=2, col=1
    )

    # 4. 金额贡献（下方右侧）
    fig.add_trace(
        go.Bar(
            x=distribution['金额区间'],
            y=distribution['销售额'],
            name='销售额',
            marker_color='#ff8800',
            opacity=0.7,
            yaxis='y4',
            hovertemplate='%{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1, secondary_y=True
    )

    # 更新布局
    fig.update_xaxes(title_text="月份", row=1, col=1, tickangle=-45)
    fig.update_xaxes(title_text="月份", row=1, col=2, tickangle=-45)
    fig.update_xaxes(title_text="金额区间", row=2, col=1)

    fig.update_yaxes(title_text="销售额", row=1, col=1)
    fig.update_yaxes(title_text="订单数", row=1, col=2)
    fig.update_yaxes(title_text="订单数", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="销售额", row=2, col=1, secondary_y=True)

    fig.update_layout(
        height=800,
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        title=dict(
            text=f"{selected_region} - 销售综合分析仪表板",
            font=dict(size=24, color='#2d3748'),
            x=0.5,
            xanchor='center'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )

    return fig, total_sales, total_orders, avg_order_value


def main():
    global ECHARTS_AVAILABLE  # 声明使用全局变量

    # 初始化session_state来保存标签状态
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    if 'risk_subtab' not in st.session_state:
        st.session_state.risk_subtab = 0

    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>👥 客户依赖分析</h1>
        <p>深入洞察客户关系，识别业务风险，优化客户组合策略</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner('正在加载数据...'):
        metrics, customer_status, sales_data, monthly_data = load_and_process_data()

    if metrics is None:
        st.error("❌ 数据加载失败，请检查数据文件。")
        return

    # 创建图表
    charts = create_enhanced_charts(metrics, sales_data, monthly_data)

    # 标签页
    tab_list = [
        "📊 核心指标", "🎯 健康诊断", "⚠️ 风险评估",
        "💎 价值分层", "📈 目标追踪", "📉 趋势分析"
    ]

    tabs = st.tabs(tab_list)

    # Tab 1: 核心指标
    with tabs[0]:
        # 关键修复：为目标达成率卡片添加完全一致的CSS样式
        st.markdown("""
        <style>
        /* 确保所有指标卡片使用相同的基础样式 */
        .metric-card {
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
            padding: 1.5rem !important; 
            border-radius: 18px !important; 
            text-align: center !important; 
            height: 140px !important;
            min-height: 140px !important;
            max-height: 140px !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 3px 10px rgba(0,0,0,0.03) !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            animation: slideUp 0.8s ease-out !important;
            backdrop-filter: blur(10px) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            position: relative !important;
            overflow: hidden !important;
        }

        .metric-card:hover {
            transform: translateY(-8px) scale(1.02) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 10px 20px rgba(102, 126, 234, 0.15) !important;
        }

        .metric-card::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 100% !important;
            height: 100% !important;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent) !important;
            transition: left 0.6s ease !important;
        }

        .metric-card:hover::before {
            left: 100% !important;
        }

        /* 目标达成率特殊样式 - 与其他卡片完全一致 */
        .info-icon {
            position: absolute !important;
            bottom: 8px !important;
            right: 8px !important;
            width: 20px !important;
            height: 20px !important;
            background: #667eea !important;
            color: white !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 14px !important;
            cursor: pointer !important;
            z-index: 10 !important;
            font-weight: bold !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        .info-icon:hover {
            background: #5a67d8 !important;
            transform: scale(1.1) !important;
        }

        .tooltip {
            visibility: hidden !important;
            position: absolute !important;
            bottom: 30px !important;
            right: 0 !important;
            background: rgba(0,0,0,0.92) !important;
            color: white !important;
            text-align: left !important;
            border-radius: 10px !important;
            padding: 16px !important;
            z-index: 1000 !important;
            opacity: 0 !important;
            transition: all 0.3s ease !important;
            width: 280px !important;
            font-size: 13px !important;
            line-height: 1.6 !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }

        .info-icon:hover .tooltip {
            visibility: visible !important;
            opacity: 1 !important;
            transform: translateY(-5px) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 核心业务指标
        st.markdown("### 💰 核心业务指标")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                        <div class="metric-card">
                            <div class="big-value">{format_amount(metrics['total_sales'])}</div>
                            <div class="metric-label">年度销售总额</div>
                            <div class="metric-sublabel">同比 {'+' if metrics['growth_rate'] > 0 else ''}{metrics['growth_rate']:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{metrics['normal_rate']:.1f}%</div>
                            <div class="metric-label">客户健康度</div>
                            <div class="metric-sublabel">正常客户 {metrics['normal_customers']} 家</div>
                        </div>
                        """, unsafe_allow_html=True)

        with col3:
            risk_color = '#e74c3c' if metrics['max_dependency'] > 30 else '#667eea'
            st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value" style="color: {risk_color} !important;">
                                {metrics['max_dependency']:.1f}%
                            </div>
                            <div class="metric-label">最高区域风险</div>
                            <div class="metric-sublabel">{metrics['max_dependency_region']} 区域</div>
                        </div>
                        """, unsafe_allow_html=True)

        # === 关键修复：目标达成率卡片 - 移除悬停框，直接显示计算逻辑 ===
        with col4:
            st.markdown(f"""
                        <div class="target-achievement-card">
                            <div class="metric-value">{metrics['target_achievement_rate']:.1f}%</div>
                            <div class="metric-label">目标达成率</div>
                            <div class="metric-sublabel">{metrics['achieved_customers']}/{metrics['total_target_customers']} 家达成</div>
                            <div class="target-calculation-logic">
                                计算逻辑：实际销售额÷年度目标×100%<br>
                                统计口径：按发运月份不考虑时间进度
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        # 客户分布指标
        st.markdown("### 👥 客户分布指标")
        col1, col2, col3, col4, col5 = st.columns(5)

        customer_types = [
            (col1, "💎", metrics['diamond_customers'], "钻石客户"),
            (col2, "🏆", metrics['gold_customers'], "黄金客户"),
            (col3, "🥈", metrics['silver_customers'], "白银客户"),
            (col4, "🌟", metrics['potential_customers'], "潜力客户"),
            (col5, "⚠️", metrics['risk_customers'], "流失风险")
        ]

        for col, icon, count, label in customer_types:
            color = '#e74c3c' if label == "流失风险" else '#667eea'
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 1.8rem; margin-bottom: 0.3rem;">{icon}</div>
                        <div class="metric-value" style="color: {color} !important;">{count}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 客户状态统计
        st.markdown("### 📈 客户状态统计")
        col1, col2, col3 = st.columns(3)

        status_data = [
            (col1, metrics['total_customers'], "总客户数", "#667eea"),
            (col2, metrics['normal_customers'], "正常客户", "#48bb78"),
            (col3, metrics['closed_customers'], "闭户客户", "#e74c3c")
        ]

        for col, count, label, color in status_data:
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: {color} !important;">{count}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 价值分层关键指标
        if not metrics['rfm_df'].empty:
            st.markdown("### 💎 价值分层关键指标")
            col1, col2, col3 = st.columns(3)

            total_revenue = metrics['rfm_df']['M'].sum()
            top_revenue = metrics['rfm_df'][metrics['rfm_df']['类型'].isin(['钻石客户', '黄金客户'])]['M'].sum()
            risk_revenue = metrics['rfm_df'][metrics['rfm_df']['类型'] == '流失风险']['M'].sum()

            with col1:
                top_percentage = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{top_percentage:.1f}%</div>
                        <div class="metric-label">高价值客户贡献度</div>
                        <div class="metric-sublabel">钻石+黄金客户</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                risk_percentage = (risk_revenue / total_revenue * 100) if total_revenue > 0 else 0
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #e74c3c !important;">{risk_percentage:.1f}%</div>
                        <div class="metric-label">风险客户价值占比</div>
                        <div class="metric-sublabel">需要立即关注</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col3:
                # 计算订单相关指标
                total_orders_all = len(sales_data) if not sales_data.empty else 0
                avg_order_value_all = total_revenue / total_orders_all if total_orders_all > 0 else 0

                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_orders_all:,}</div>
                        <div class="metric-label">年度总订单数</div>
                        <div class="metric-sublabel">平均客单价: {format_amount(avg_order_value_all)}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Tab 2: 健康诊断
    with tabs[1]:
        if 'health_radar' in charts:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户健康状态综合评估</div>
                <div class="chart-subtitle">多维度评估客户群体整体健康状况</div>
            </div>
            ''', unsafe_allow_html=True)
            st.plotly_chart(charts['health_radar'], use_container_width=True, key="health_radar")

    # Tab 3: 风险评估
    with tabs[2]:
        # 创建子标签页
        risk_subtab_list = ["📊 客户贡献分析", "🕐 下单周期监测", "🎯 风险预警模型"]
        risk_subtabs = st.tabs(risk_subtab_list)

        with risk_subtabs[0]:
            # Top20客户分析
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">Top 20 客户贡献度分析</div>
                <div class="chart-subtitle">展示前20大客户的销售额分布和累计贡献度</div>
            </div>
            ''', unsafe_allow_html=True)

            if 'top20' in charts:
                st.plotly_chart(charts['top20'], use_container_width=True, key="top20_chart")

            # 区域风险矩阵
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">区域客户依赖风险矩阵</div>
                <div class="chart-subtitle">评估各区域的客户集中度风险</div>
            </div>
            ''', unsafe_allow_html=True)

            if 'risk_matrix' in charts:
                st.plotly_chart(charts['risk_matrix'], use_container_width=True, key="risk_matrix_chart")

        with risk_subtabs[1]:
            # 下单周期监测
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户下单周期监测</div>
                <div class="chart-subtitle">追踪Top 20客户的下单规律，识别异常行为</div>
            </div>
            ''', unsafe_allow_html=True)

            # 计算客户周期数据
            if sales_data is not None and not sales_data.empty:
                cycles_df = calculate_customer_cycles(sales_data, metrics['current_year'])

                if not cycles_df.empty:
                    # 显示时间轴图表
                    timeline_fig = create_timeline_chart(cycles_df)
                    st.plotly_chart(timeline_fig, use_container_width=True, key="timeline_chart")

                    # 添加提示信息
                    st.info("💡 提示：可以拖动图表查看更多细节，鼠标悬停查看详细信息")
                else:
                    st.info("暂无足够的订单数据进行周期分析")
            else:
                st.info("暂无订单数据")

        with risk_subtabs[2]:
            # 风险预警模型
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">客户风险预警模型</div>
                <div class="chart-subtitle">基于机器学习的30天流失风险预测</div>
            </div>
            ''', unsafe_allow_html=True)

            if sales_data is not None and not sales_data.empty:
                # 计算风险预测
                risk_df = calculate_risk_prediction(sales_data)

                if not risk_df.empty:
                    # 创建风险仪表盘
                    fig_dist, fig_hist, fig_matrix = create_risk_dashboard(risk_df)

                    # 显示图表
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(fig_dist, use_container_width=True, key="risk_dist")
                    with col2:
                        st.plotly_chart(fig_hist, use_container_width=True, key="risk_hist")

                    st.plotly_chart(fig_matrix, use_container_width=True, key="risk_matrix_scatter")

                    # 高风险客户详细列表
                    st.markdown('''
                    <div class="chart-header">
                        <div class="chart-title">高风险客户详细分析</div>
                        <div class="chart-subtitle">需要重点关注的客户列表</div>
                    </div>
                    ''', unsafe_allow_html=True)

                    # 筛选高风险客户
                    high_risk_customers = risk_df[risk_df['流失风险概率'] >= 50].head(10)

                    if not high_risk_customers.empty:
                        for _, customer in high_risk_customers.iterrows():
                            risk_icon = '🔴' if customer['风险等级'] == '高风险' else '🟠'

                            # 风险说明
                            risk_factors = []
                            if customer['断单风险'] > 70:
                                risk_factors.append(f"断单风险高达 {customer['断单风险']:.0f}%")
                            if customer['减量风险'] > 70:
                                risk_factors.append(f"减量风险达 {customer['减量风险']:.0f}%")
                            if customer['周期趋势'] == '延长':
                                risk_factors.append("下单周期正在延长")
                            if customer['金额趋势'] == '下降':
                                risk_factors.append("订单金额持续下降")

                            st.markdown(f"""
                            <div class="insight-card" style="border-left-color: {customer['风险颜色']};">
                                <h4>{risk_icon} {customer['客户']}</h4>
                                <ul>
                                    <li><strong>流失概率：</strong>{customer['流失风险概率']:.1f}% (±{customer['置信区间']:.0f}%)</li>
                                    <li><strong>风险类型：</strong>{customer['主要风险']}</li>
                                    <li><strong>最后订单：</strong>{customer['最后订单日期'].strftime('%Y-%m-%d')} ({customer['距今天数']}天前)</li>
                                    <li><strong>平均周期：</strong>{customer['平均周期']:.0f}天 | 平均金额：{format_amount(customer['平均金额'])}</li>
                                    <li><strong>风险因素：</strong>{' | '.join(risk_factors)}</li>
                                    <li><strong>预测下单：</strong>{customer['预测下单日期'].strftime('%Y-%m-%d')} | 预测金额：{format_amount(customer['预测金额'])}</li>
                                    <li><strong>建议行动：</strong><span style="color: {customer['风险颜色']}; font-weight: bold;">{customer['建议行动']}</span></li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)

                        # 导出风险报告
                        if st.button("📥 导出风险预警报告", key="export_risk_report"):
                            export_cols = ['客户', '流失风险概率', '风险等级', '主要风险',
                                           '最后订单日期', '距今天数', '平均周期', '平均金额',
                                           '建议行动', '金额趋势', '周期趋势']
                            export_df = risk_df[export_cols].copy()
                            export_df['流失风险概率'] = export_df['流失风险概率'].round(1)
                            csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="下载CSV文件",
                                data=csv,
                                file_name=f"客户风险预警报告_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.success("✅ 暂无高风险客户，业务状况良好！")
                else:
                    st.info("需要更多历史数据才能进行风险预测")
            else:
                st.info("暂无订单数据")

    # Tab 4: 价值分层
    with tabs[3]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">客户价值流动分析</div>
            <div class="chart-subtitle">展示客户在不同价值层级间的分布，悬停查看详细客户名单</div>
        </div>
        ''', unsafe_allow_html=True)

        if 'sankey' in charts and charts['sankey'] is not None:
            st.plotly_chart(charts['sankey'], use_container_width=True, key="sankey_chart")

            # 添加价值分层说明
            st.markdown("""
            <div class='insight-card'>
                <h4>💡 价值分层说明</h4>
                <ul>
                    <li><span style='color: #e74c3c; font-size: 1.2em;'>●</span> <strong>💎 钻石客户</strong>：近期活跃、高频率、高金额的核心客户</li>
                    <li><span style='color: #f39c12; font-size: 1.2em;'>●</span> <strong>🏆 黄金客户</strong>：表现良好、贡献稳定的重要客户</li>
                    <li><span style='color: #3498db; font-size: 1.2em;'>●</span> <strong>🥈 白银客户</strong>：有一定贡献但仍有提升空间的客户</li>
                    <li><span style='color: #2ecc71; font-size: 1.2em;'>●</span> <strong>🌟 潜力客户</strong>：需要培育和激活的客户群体</li>
                    <li><span style='color: #95a5a6; font-size: 1.2em;'>●</span> <strong>⚠️ 流失风险</strong>：长期未下单或订单减少的风险客户</li>
                </ul>
                <p style="margin-top: 1rem; color: #667eea; font-weight: 600;">💡 提示：将鼠标悬停在图表上可查看每个分类的Top 10客户名单</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 暂无客户价值分层数据。请确保已加载客户销售数据。")

    # Tab 5: 目标追踪（修复图表显示问题）
    with tabs[4]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">客户目标达成分析</div>
            <div class="chart-subtitle">评估当前年度（{0}年）各客户的销售目标完成情况</div>
        </div>
        '''.format(metrics['current_year']), unsafe_allow_html=True)

        # 修复目标散点图显示问题
        if 'target_scatter' in charts and charts['target_scatter'] is not None:
            st.plotly_chart(charts['target_scatter'], use_container_width=True, key="target_scatter_chart")
        else:
            # 如果没有图表，显示详细的目标达成数据表格
            if not metrics['customer_achievement_details'].empty:
                st.markdown("### 📊 客户目标达成详细数据")

                achievement_df = metrics['customer_achievement_details'].copy()
                achievement_df = achievement_df.sort_values('达成率', ascending=False)

                # 添加达成状态的颜色标识
                def get_status_color(row):
                    if row['达成率'] >= 100:
                        return "🟢"
                    elif row['达成率'] >= 80:
                        return "🟡"
                    else:
                        return "🔴"

                achievement_df['状态图标'] = achievement_df.apply(get_status_color, axis=1)

                # 显示前20个客户的目标达成情况
                top_customers = achievement_df.head(20)

                for _, customer in top_customers.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        st.markdown(f"**{customer['状态图标']} {customer['客户']}**")

                    with col2:
                        st.markdown(f"目标: {format_amount(customer['年度目标'])}")

                    with col3:
                        st.markdown(f"实际: {format_amount(customer['实际'])}")

                    with col4:
                        color = '#48bb78' if customer['达成率'] >= 100 else '#ffd93d' if customer[
                                                                                             '达成率'] >= 80 else '#ff6b6b'
                        st.markdown(
                            f"<span style='color: {color}; font-weight: bold;'>{customer['达成率']:.1f}%</span>",
                            unsafe_allow_html=True)

                # 总结统计
                total_customers = len(achievement_df)
                achieved_100 = len(achievement_df[achievement_df['达成率'] >= 100])
                achieved_80 = len(achievement_df[achievement_df['达成率'] >= 80])

                st.markdown(f"""
                <div class='insight-card'>
                    <h4>📈 目标达成总结</h4>
                    <ul>
                        <li>🟢 <strong>完全达成（≥100%）：</strong>{achieved_100}家客户 ({achieved_100 / total_customers * 100:.1f}%)</li>
                        <li>🟡 <strong>基本达成（≥80%）：</strong>{achieved_80}家客户 ({achieved_80 / total_customers * 100:.1f}%)</li>
                        <li>🔴 <strong>未达成（<80%）：</strong>{total_customers - achieved_80}家客户 ({(total_customers - achieved_80) / total_customers * 100:.1f}%)</li>
                        <li>📊 <strong>平均达成率：</strong>{achievement_df['达成率'].mean():.1f}%</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("暂无目标达成数据")

    # Tab 6: 趋势分析
    with tabs[5]:
        st.markdown('''
        <div class="chart-header">
            <div class="chart-title">销售趋势综合分析</div>
            <div class="chart-subtitle">多维度展示销售数据的时间序列变化和分布特征</div>
        </div>
        ''', unsafe_allow_html=True)

        # 区域选择器
        if not monthly_data.empty and '所属大区' in monthly_data.columns:
            regions = ['全国'] + sorted(monthly_data['所属大区'].dropna().unique().tolist())

            # 初始化session state
            if 'selected_region' not in st.session_state:
                st.session_state.selected_region = '全国'

            # 区域选择器
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                selected_region = st.selectbox(
                    '选择区域',
                    regions,
                    index=regions.index(
                        st.session_state.selected_region) if st.session_state.selected_region in regions else 0,
                    key='region_selector'
                )
                st.session_state.selected_region = selected_region
        else:
            selected_region = '全国'

        # 创建增强的趋势分析（单一综合图表）
        with st.spinner(f'正在加载{selected_region}数据...'):
            trend_fig = create_integrated_trend_analysis(sales_data, monthly_data, selected_region)

        if trend_fig:
            # 显示综合图表
            st.plotly_chart(trend_fig, use_container_width=True, key=f"integrated_trend_chart_{selected_region}")

            # 趋势洞察
            st.markdown(f"""
            <div class='insight-card'>
                <h4>📊 {selected_region} 关键洞察</h4>
                <ul>
                    <li>销售额呈现季节性波动，需提前规划产能</li>
                    <li>小额订单（<1万）占比较高，可考虑提升客单价策略</li>
                    <li>大额订单（>4万）贡献了主要收入，需重点维护</li>
                    <li>建议深入分析高峰低谷期原因，优化销售策略</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"暂无{selected_region}的销售数据")


if __name__ == "__main__":
    main()
