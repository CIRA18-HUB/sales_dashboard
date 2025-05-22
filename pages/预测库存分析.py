# pages/预测库存分析.py - 完整版本（包含所有样式和动画效果）
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="预测库存分析 - 销售数据仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ 请先登录系统")
    st.stop()

# 超强力隐藏Streamlit默认元素
hide_elements = """
<style>
    /* 隐藏所有可能的Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}

    /* 强力隐藏侧边栏中的应用名称 */
    .stSidebar > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }

    /* 隐藏侧边栏顶部的应用标题 */
    .stSidebar .element-container:first-child {
        display: none !important;
    }

    /* 通过多种方式隐藏应用标题 */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 如果以上都无效，至少让它不可见 */
    .stSidebar > div:first-child {
        background: transparent !important;
        border: none !important;
    }

    .stSidebar .stSelectbox {
        display: none !important;
    }
</style>
"""

st.markdown(hide_elements, unsafe_allow_html=True)

# 完整CSS样式（继承登录界面样式）
complete_css_with_animations = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 + 动画 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景波纹效果 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 60%);
        animation: waveMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes waveMove {
        0%, 100% { 
            background-size: 200% 200%, 150% 150%, 300% 300%;
            background-position: 0% 0%, 100% 100%, 50% 50%; 
        }
        33% { 
            background-size: 300% 300%, 200% 200%, 250% 250%;
            background-position: 100% 0%, 0% 50%, 80% 20%; 
        }
        66% { 
            background-size: 250% 250%, 300% 300%, 200% 200%;
            background-position: 50% 100%, 50% 0%, 20% 80%; 
        }
    }

    /* 浮动粒子效果 */
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.2), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.3), transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: particleFloat 20s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes particleFloat {
        0% { transform: translateY(100vh) translateX(0); }
        100% { transform: translateY(-100vh) translateX(100px); }
    }

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }

    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .stSidebar > div:first-child {
        background: transparent;
        padding-top: 1rem;
    }

    /* 侧边栏标题 */
    .stSidebar .stMarkdown h3 {
        color: #2d3748;
        font-weight: 600;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titlePulse 3s ease-in-out infinite;
    }

    @keyframes titlePulse {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.2); }
    }

    /* 侧边栏按钮 */
    .stSidebar .stButton > button {
        width: 100%;
        background: transparent;
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        color: #4a5568;
        text-align: left;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.9rem;
        position: relative;
        overflow: hidden;
    }

    .stSidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s ease;
    }

    .stSidebar .stButton > button:hover::before {
        left: 100%;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: #667eea;
        color: #667eea;
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    /* 标签页样式 */
    .tab-navigation {
        display: flex;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 1s ease-out 0.3s both;
        overflow-x: auto;
        gap: 0.5rem;
        position: relative;
        z-index: 10;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .tab-button {
        flex: 1;
        min-width: 180px;
        padding: 1rem 1.5rem;
        border: none;
        background: transparent;
        border-radius: 15px;
        cursor: pointer;
        font-family: inherit;
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        transition: all 0.3s ease;
        text-align: center;
        white-space: nowrap;
        position: relative;
        overflow: hidden;
    }

    .tab-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s ease;
    }

    .tab-button:hover::before {
        left: 100%;
    }

    .tab-button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        color: #667eea;
        transform: translateY(-2px);
    }

    .tab-button.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }

    /* 卡片样式 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        animation: slideInCard 0.8s ease-out both;
        margin-bottom: 2rem;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #81ecec);
        background-size: 200% 100%;
        animation: gradientFlow 3s ease-in-out infinite;
    }

    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes slideInCard {
        from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .metric-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
    }

    .metric-icon {
        font-size: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        display: block;
        animation: iconBounce 2s ease-in-out infinite;
    }

    @keyframes iconBounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .metric-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1;
        animation: numberGlow 2s ease-out;
    }

    @keyframes numberGlow {
        0% { filter: drop-shadow(0 0 0 transparent); }
        50% { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.6)); }
        100% { filter: drop-shadow(0 0 0 transparent); }
    }

    .metric-description {
        color: #718096;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .metric-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        animation: statusPulse 3s ease-in-out infinite;
    }

    @keyframes statusPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .status-healthy {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }

    .status-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }

    .status-danger {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }

    /* 图表容器 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        animation: chartFadeIn 1s ease-out both;
        position: relative;
        overflow: hidden;
    }

    @keyframes chartFadeIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #81ecec, #74b9ff);
        background-size: 300% 100%;
        animation: rainbowShift 4s ease-in-out infinite;
    }

    @keyframes rainbowShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .chart-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1.5rem;
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 洞察汇总区域 */
    .insight-summary {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border-left: 4px solid #667eea;
        position: relative;
    }

    .insight-summary::before {
        content: '💡';
        position: absolute;
        top: 1rem;
        left: 1rem;
        font-size: 1.5rem;
    }

    .insight-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0 0 0.5rem 2.5rem;
    }

    .insight-content {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-left: 2.5rem;
    }

    .insight-metrics {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }

    .insight-metric {
        background: rgba(255, 255, 255, 0.7);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #2d3748;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .tab-navigation {
            flex-direction: column;
        }

        .tab-button {
            min-width: auto;
            margin-bottom: 0.5rem;
        }
    }
</style>
"""

st.markdown(complete_css_with_animations, unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 📊 销售数据分析仪表盘")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    st.button("📊 预测库存分析", use_container_width=True, disabled=True)

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.info("**管理员**  \n系统管理员")

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("登陆界面haha.py")


# 数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 加载出货数据
        shipment_df = pd.read_excel("2409~250224出货数据.xlsx")
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])

        # 加载预测数据
        forecast_df = pd.read_excel("2409~2502人工预测.xlsx")

        # 加载库存数据（需要特殊处理分层级结构）
        inventory_df = pd.read_excel("含批次库存0221(2).xlsx")

        # 加载单价数据
        price_df = pd.read_excel("单价.xlsx")

        return shipment_df, forecast_df, inventory_df, price_df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None, None, None, None


# 处理库存数据的分层级结构
def process_inventory_data(inventory_df):
    """处理分层级的库存数据"""
    if inventory_df is None:
        return pd.DataFrame()

    # 创建处理后的数据列表
    processed_data = []
    current_product = None

    for idx, row in inventory_df.iterrows():
        if pd.notna(row['物料']) and row['物料'].strip():
            # 这是主产品行
            current_product = {
                '产品代码': row['物料'],
                '产品描述': row['描述'],
                '现有库存': row['现有库存'],
                '已分配量': row['已分配量'],
                '可订量': row['现有库存可订量'],
                '待入库量': row['待入库量'],
                '本月剩余可订量': row['本月剩余可订量']
            }
        elif current_product and pd.notna(row['生产日期']):
            # 这是批次详情行
            batch_data = current_product.copy()
            batch_data.update({
                '库位': row['库位'],
                '生产日期': row['生产日期'],
                '生产批号': row['生产批号'],
                '批次数量': row['数量']
            })
            processed_data.append(batch_data)

    return pd.DataFrame(processed_data)


# 页面标题
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem; position: relative; z-index: 10;">
    <h1 style="font-size: 3.5rem; color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); margin-bottom: 1rem; font-weight: 800; animation: titleGlowPulse 4s ease-in-out infinite;">
        📊 预测库存分析仪表盘
    </h1>
    <p style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 2rem; animation: subtitleFloat 6s ease-in-out infinite;">Clay风格企业级分析系统 - 数据驱动的库存预测与管理优化</p>
</div>

<style>
@keyframes titleGlowPulse {
    0%, 100% { 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
        transform: scale(1);
    }
    50% { 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
        transform: scale(1.02);
    }
}

@keyframes subtitleFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
</style>
""", unsafe_allow_html=True)

# 标签页导航
tabs = ["📊 关键指标总览", "🚨 风险分析", "📈 预测分析", "👥 责任分析", "📋 库存分析"]
selected_tab = st.selectbox("", tabs, label_visibility="collapsed")

# 加载数据
shipment_df, forecast_df, inventory_df, price_df = load_data()

if any(df is None for df in [shipment_df, forecast_df, inventory_df, price_df]):
    st.error("数据加载失败，请检查数据文件")
    st.stop()

# 处理库存数据
processed_inventory = process_inventory_data(inventory_df)


# 数据预处理
def preprocess_data():
    """数据预处理和计算"""
    # 计算库龄
    if not processed_inventory.empty:
        processed_inventory['生产日期'] = pd.to_datetime(processed_inventory['生产日期'], errors='coerce')
        processed_inventory['库龄'] = (datetime.now() - processed_inventory['生产日期']).dt.days

    # 合并单价数据
    merged_inventory = processed_inventory.merge(price_df, left_on='产品代码', right_on='产品代码', how='left')
    merged_inventory['批次价值'] = merged_inventory['批次数量'] * merged_inventory['单价']

    # 计算预测准确率
    forecast_analysis = calculate_forecast_accuracy()

    return merged_inventory, forecast_analysis


def calculate_forecast_accuracy():
    """计算预测准确率"""
    # 按月汇总实际销售数据
    shipment_monthly = shipment_df.groupby([
        shipment_df['订单日期'].dt.to_period('M'),
        '产品代码'
    ])['求和项:数量（箱）'].sum().reset_index()
    shipment_monthly['所属年月'] = shipment_monthly['订单日期'].astype(str)

    # 合并预测和实际数据
    merged = forecast_df.merge(
        shipment_monthly,
        on=['所属年月', '产品代码'],
        how='inner'
    )

    # 计算准确率
    merged['预测偏差'] = abs(merged['预计销售量'] - merged['求和项:数量（箱）']) / (merged['求和项:数量（箱）'] + 1)
    merged['准确率'] = 1 - merged['预测偏差']
    merged['准确率'] = merged['准确率'].clip(0, 1)

    return merged


# 数据预处理
merged_inventory, forecast_analysis = preprocess_data()


# 计算关键指标
def calculate_key_metrics():
    """计算关键指标"""
    # 总批次数量
    total_batches = len(merged_inventory) if not merged_inventory.empty else 0

    # 高风险批次（库龄>90天）
    high_risk_batches = len(merged_inventory[merged_inventory['库龄'] > 90]) if not merged_inventory.empty else 0
    high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0

    # 库存总价值
    total_value = merged_inventory['批次价值'].sum() if not merged_inventory.empty else 0

    # 高风险价值占比
    high_risk_value = merged_inventory[merged_inventory['库龄'] > 90][
        '批次价值'].sum() if not merged_inventory.empty else 0
    high_risk_value_ratio = (high_risk_value / total_value * 100) if total_value > 0 else 0

    # 平均库龄
    avg_age = merged_inventory['库龄'].mean() if not merged_inventory.empty else 0

    # 预测准确率
    avg_accuracy = forecast_analysis['准确率'].mean() * 100 if not forecast_analysis.empty else 0

    return {
        'total_batches': total_batches,
        'high_risk_ratio': high_risk_ratio,
        'total_value': total_value / 1000000,  # 转换为百万
        'high_risk_value_ratio': high_risk_value_ratio,
        'avg_age': avg_age,
        'avg_accuracy': avg_accuracy
    }


metrics = calculate_key_metrics()

# 根据选择的标签页显示内容
if selected_tab == "📊 关键指标总览":
    # 关键指标卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📦</span>
            <h3 class="metric-title">总批次数量</h3>
            <div class="metric-value">{metrics['total_batches']}</div>
            <p class="metric-description">
                库存批次总数{metrics['total_batches']}个，其中高风险批次需要制定促销清库策略进行风险控制。
            </p>
            <span class="metric-status {'status-warning' if metrics['high_risk_ratio'] > 15 else 'status-healthy'}">
                {'需要关注' if metrics['high_risk_ratio'] > 15 else '状态良好'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⚠️</span>
            <h3 class="metric-title">高风险批次占比</h3>
            <div class="metric-value">{metrics['high_risk_ratio']:.1f}%</div>
            <p class="metric-description">
                {metrics['high_risk_ratio']:.1f}%的批次处于高风险状态。主要集中在库龄超过90天的产品，需要紧急促销清库。
            </p>
            <span class="metric-status {'status-danger' if metrics['high_risk_ratio'] > 15 else 'status-warning' if metrics['high_risk_ratio'] > 10 else 'status-healthy'}">
                {'风险预警' if metrics['high_risk_ratio'] > 15 else '需要关注' if metrics['high_risk_ratio'] > 10 else '状态良好'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">💎</span>
            <h3 class="metric-title">库存总价值</h3>
            <div class="metric-value">{metrics['total_value']:.2f}M</div>
            <p class="metric-description">
                库存总价值{metrics['total_value']:.2f}百万元。需要重点关注高价值产品的库存周转效率。
            </p>
            <span class="metric-status status-healthy">稳定管理</span>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🚨</span>
            <h3 class="metric-title">高风险价值占比</h3>
            <div class="metric-value">{metrics['high_risk_value_ratio']:.1f}%</div>
            <p class="metric-description">
                {metrics['high_risk_value_ratio']:.1f}%的高价值库存需要促销清库，严重影响现金流周转。
            </p>
            <span class="metric-status {'status-danger' if metrics['high_risk_value_ratio'] > 30 else 'status-warning' if metrics['high_risk_value_ratio'] > 20 else 'status-healthy'}">
                {'紧急处理' if metrics['high_risk_value_ratio'] > 30 else '需要关注' if metrics['high_risk_value_ratio'] > 20 else '状态良好'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⏰</span>
            <h3 class="metric-title">平均库龄</h3>
            <div class="metric-value">{metrics['avg_age']:.0f}天</div>
            <p class="metric-description">
                平均库龄{metrics['avg_age']:.0f}天。建议优化进货计划和预测准确率。
            </p>
            <span class="metric-status {'status-warning' if metrics['avg_age'] > 60 else 'status-healthy'}">
                {'需要优化' if metrics['avg_age'] > 60 else '状态良好'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🎯</span>
            <h3 class="metric-title">预测准确率</h3>
            <div class="metric-value">{metrics['avg_accuracy']:.1f}%</div>
            <p class="metric-description">
                整体预测准确率{metrics['avg_accuracy']:.1f}%，持续改善中。
            </p>
            <span class="metric-status {'status-healthy' if metrics['avg_accuracy'] > 75 else 'status-warning'}">
                {'持续改善' if metrics['avg_accuracy'] > 75 else '需要提升'}
            </span>
        </div>
        """, unsafe_allow_html=True)

elif selected_tab == "🚨 风险分析":
    # 风险分析页面
    if not merged_inventory.empty:
        # 风险等级分布
        def get_risk_level(age):
            if age > 120:
                return '极高风险'
            elif age > 90:
                return '高风险'
            elif age > 60:
                return '中风险'
            elif age > 30:
                return '低风险'
            else:
                return '极低风险'


        merged_inventory['风险等级'] = merged_inventory['库龄'].apply(get_risk_level)
        risk_distribution = merged_inventory['风险等级'].value_counts()

        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">🎯 风险等级分布分析</h3>
        </div>
        """, unsafe_allow_html=True)

        # 创建风险分布饼图
        fig_risk = px.pie(
            values=risk_distribution.values,
            names=risk_distribution.index,
            title="库存风险等级分布",
            color_discrete_map={
                '极高风险': '#ef4444',
                '高风险': '#f59e0b',
                '中风险': '#eab308',
                '低风险': '#22c55e',
                '极低风险': '#06b6d4'
            }
        )
        fig_risk.update_layout(
            font=dict(family="Inter", size=12),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        # 高风险产品详情
        high_risk_products = merged_inventory[merged_inventory['库龄'] > 90].nlargest(10, '批次价值')

        if not high_risk_products.empty:
            st.markdown("""
            <div class="chart-container">
                <h3 class="chart-title">🔥 高风险批次优先级分析</h3>
            </div>
            """, unsafe_allow_html=True)

            # 创建气泡图
            fig_bubble = px.scatter(
                high_risk_products,
                x='库龄',
                y='批次价值',
                size='批次数量',
                color='风险等级',
                hover_data=['产品代码', '产品描述'],
                title="高风险批次气泡图（气泡大小=批次数量）",
                color_discrete_map={
                    '极高风险': '#ef4444',
                    '高风险': '#f59e0b'
                }
            )
            fig_bubble.update_layout(
                font=dict(family="Inter", size=12),
                height=400,
                xaxis_title="库龄 (天)",
                yaxis_title="批次价值 (元)"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

elif selected_tab == "📈 预测分析":
    # 预测分析页面
    if not forecast_analysis.empty:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">📈 预测准确率趋势分析</h3>
        </div>
        """, unsafe_allow_html=True)

        # 按月计算平均准确率
        monthly_accuracy = forecast_analysis.groupby('所属年月')['准确率'].mean().reset_index()
        monthly_accuracy['准确率_百分比'] = monthly_accuracy['准确率'] * 100

        # 创建时间趋势图
        fig_trend = px.line(
            monthly_accuracy,
            x='所属年月',
            y='准确率_百分比',
            title="月度预测准确率趋势",
            markers=True
        )
        fig_trend.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            yaxis_title="预测准确率 (%)"
        )
        fig_trend.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="目标线 (80%)")
        st.plotly_chart(fig_trend, use_container_width=True)

        # 产品预测表现散点图
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">🎯 产品预测表现分析</h3>
        </div>
        """, unsafe_allow_html=True)

        # 创建预测vs实际散点图
        fig_scatter = px.scatter(
            forecast_analysis,
            x='预计销售量',
            y='求和项:数量（箱）',
            color='准确率',
            hover_data=['产品代码', '所属年月'],
            title="预测销量 vs 实际销量",
            color_continuous_scale='RdYlGn'
        )
        # 添加完美预测线
        max_val = max(forecast_analysis[['预计销售量', '求和项:数量（箱）']].max())
        fig_scatter.add_shape(
            type="line",
            x0=0, y0=0, x1=max_val, y1=max_val,
            line=dict(color="red", width=2, dash="dash")
        )
        fig_scatter.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            xaxis_title="预测销量 (箱)",
            yaxis_title="实际销量 (箱)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

elif selected_tab == "👥 责任分析":
    # 责任分析页面
    if not forecast_analysis.empty:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">👥 区域预测表现对比</h3>
        </div>
        """, unsafe_allow_html=True)

        # 按区域汇总表现
        region_performance = forecast_analysis.groupby('所属大区').agg({
            '准确率': 'mean',
            '预计销售量': 'sum',
            '求和项:数量（箱）': 'sum'
        }).reset_index()
        region_performance['准确率_百分比'] = region_performance['准确率'] * 100

        # 创建区域对比柱状图
        fig_region = px.bar(
            region_performance,
            x='所属大区',
            y='准确率_百分比',
            title="区域预测准确率对比",
            color='准确率_百分比',
            color_continuous_scale='RdYlGn'
        )
        fig_region.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            yaxis_title="预测准确率 (%)"
        )
        st.plotly_chart(fig_region, use_container_width=True)

        # 销售员表现分析
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">🏆 销售员绩效排名</h3>
        </div>
        """, unsafe_allow_html=True)

        # 按销售员汇总表现
        salesperson_performance = forecast_analysis.groupby('销售员').agg({
            '准确率': 'mean',
            '预计销售量': 'sum',
            '求和项:数量（箱）': 'sum'
        }).reset_index()
        salesperson_performance['准确率_百分比'] = salesperson_performance['准确率'] * 100
        salesperson_performance = salesperson_performance.sort_values('准确率_百分比', ascending=True)

        # 创建销售员排名图
        fig_salesperson = px.bar(
            salesperson_performance.tail(10),  # 显示前10名
            x='准确率_百分比',
            y='销售员',
            orientation='h',
            title="销售员预测准确率排名 (Top 10)",
            color='准确率_百分比',
            color_continuous_scale='RdYlGn'
        )
        fig_salesperson.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            xaxis_title="预测准确率 (%)"
        )
        st.plotly_chart(fig_salesperson, use_container_width=True)

elif selected_tab == "📋 库存分析":
    # 库存分析页面
    if not merged_inventory.empty:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">📈 库存分析概览</h3>
        </div>
        """, unsafe_allow_html=True)

        # 库龄分布直方图
        fig_age_dist = px.histogram(
            merged_inventory,
            x='库龄',
            nbins=20,
            title="库龄分布直方图",
            color_discrete_sequence=['#667eea']
        )
        fig_age_dist.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            xaxis_title="库龄 (天)",
            yaxis_title="批次数量"
        )
        st.plotly_chart(fig_age_dist, use_container_width=True)

        # 价值分布分析
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">💰 库存价值分布分析</h3>
        </div>
        """, unsafe_allow_html=True)

        # 按产品代码汇总价值
        product_value = merged_inventory.groupby('产品代码').agg({
            '批次价值': 'sum',
            '批次数量': 'sum',
            '库龄': 'mean'
        }).reset_index()
        product_value = product_value.nlargest(15, '批次价值')

        # 创建价值分布图
        fig_value = px.bar(
            product_value,
            x='产品代码',
            y='批次价值',
            title="产品库存价值分布 (Top 15)",
            color='库龄',
            color_continuous_scale='RdYlBu_r'
        )
        fig_value.update_layout(
            font=dict(family="Inter", size=12),
            height=400,
            xaxis_title="产品代码",
            yaxis_title="库存价值 (元)",
            xaxis={'tickangle': 45}
        )
        st.plotly_chart(fig_value, use_container_width=True)

# 洞察汇总
st.markdown("""
<div class="insight-summary">
    <div class="insight-title">💡 核心洞察与建议</div>
    <div class="insight-content">
        基于当前数据分析，建议重点关注以下几个方面：<br>
        1. 高风险批次管理：制定差异化的促销清库策略<br>
        2. 预测模型优化：提升预测准确率，特别是节假日期间<br>
        3. 区域协调发展：加强区域间最佳实践交流<br>
        4. 库存结构优化：重点管理高价值、长库龄产品
    </div>
    <div class="insight-metrics">
        <span class="insight-metric">风险控制目标：高风险占比<15%</span>
        <span class="insight-metric">预测提升目标：准确率>85%</span>
        <span class="insight-metric">库存优化目标：平均库龄<45天</span>
        <span class="insight-metric">价值管控目标：高风险价值<20%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript动画效果
javascript_animations = """
<script>
// 数字滚动动画函数
function animateCounters() {
    const counters = document.querySelectorAll('.metric-value');

    counters.forEach(counter => {
        const text = counter.textContent;
        const numbers = text.match(/[\d.]+/);
        if (numbers) {
            const target = parseFloat(numbers[0]);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.innerHTML = text;
                    clearInterval(timer);
                } else {
                    if (target >= 10) {
                        counter.innerHTML = text.replace(/[\d.]+/, Math.ceil(current));
                    } else {
                        counter.innerHTML = text.replace(/[\d.]+/, current.toFixed(1));
                    }
                }
            }, 40);
        }
    });
}

// 页面加载后执行动画
setTimeout(() => {
    animateCounters();
}, 1000);

// 添加鼠标跟随效果
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

function animateCursor() {
    cursorX += (mouseX - cursorX) * 0.1;
    cursorY += (mouseY - cursorY) * 0.1;

    // 更新背景渐变跟随鼠标
    const main = document.querySelector('.main');
    if (main) {
        const xPercent = (cursorX / window.innerWidth) * 100;
        const yPercent = (cursorY / window.innerHeight) * 100;

        main.style.background = `
            radial-gradient(circle at ${xPercent}% ${yPercent}%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            linear-gradient(135deg, #667eea 0%, #764ba2 100%)
        `;
    }

    requestAnimationFrame(animateCursor);
}

animateCursor();
</script>
"""

st.markdown(javascript_animations, unsafe_allow_html=True)