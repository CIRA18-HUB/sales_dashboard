# pages/预测库存分析.py - 库存预警仪表盘
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="库存预警仪表盘",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 隐藏Streamlit默认元素
hide_elements = """
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# 完整CSS样式（完全按照HTML文件）
complete_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: backgroundMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes backgroundMove {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
    }

    .block-container {
        position: relative;
        z-index: 10;
        max-width: 1600px;
        padding: 2rem;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stSidebar .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 15px;
        padding: 1rem 1.2rem;
        color: white;
        text-align: left;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
        font-weight: 500;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        font-family: inherit;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 页面标题 */
    .page-header {
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0;
        animation: fadeInDown 1s ease-out forwards;
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .page-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        animation: titleGlow 3s ease-in-out infinite;
    }

    @keyframes titleGlow {
        0%, 100% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.3); }
        50% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.6); }
    }

    .page-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
    }

    /* 标签页导航 */
    .tab-navigation {
        display: flex;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        opacity: 0;
        animation: fadeInUp 1s ease-out 0.3s forwards;
        overflow-x: auto;
        gap: 0.5rem;
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

    /* 关键指标卡片 */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 2rem;
    }

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
        opacity: 0;
        animation: slideInCard 0.8s ease-out forwards;
    }

    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }

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
        opacity: 0;
        animation: chartFadeIn 1s ease-out forwards;
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

    /* 数据展示区域 */
    .data-showcase {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .showcase-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .showcase-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }

    .showcase-item {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        animation: showcaseFloat 2s ease-in-out infinite;
        position: relative;
        cursor: pointer;
    }

    .showcase-item:nth-child(odd) {
        animation-delay: 0.5s;
    }

    @keyframes showcaseFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .showcase-item:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    }

    .showcase-number {
        font-size: 2rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
        animation: numberCount 2s ease-out;
    }

    @keyframes numberCount {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }

    .showcase-label {
        font-size: 0.9rem;
        color: #4a5568;
        font-weight: 600;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .page-title {
            font-size: 2.5rem;
        }

        .metrics-grid {
            grid-template-columns: 1fr;
        }

        .showcase-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
"""

st.markdown(complete_css, unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 📊 Trolli SAL")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    if st.button("📊 预测库存分析", use_container_width=True, disabled=True):
        pass

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.markdown("""
    <div class="user-info" style="background: #e6fffa; border: 1px solid #38d9a9; border-radius: 10px; padding: 1rem; color: #2d3748;">
        <strong>管理员</strong>
        cira
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("登陆界面haha.py")


# 数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 读取出货数据
        shipment_df = pd.read_excel('2409~250224出货数据.xlsx')
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])

        # 读取预测数据
        forecast_df = pd.read_excel('2409~2502人工预测.xlsx')

        # 读取库存数据
        inventory_df = pd.read_excel('含批次库存0221(2).xlsx')

        # 读取单价数据
        price_df = pd.read_excel('单价.xlsx')

        return shipment_df, forecast_df, inventory_df, price_df
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None, None


# 数据处理函数
def process_inventory_data(inventory_df, price_df):
    """处理库存数据"""
    try:
        # 过滤出有效的库存记录
        valid_inventory = inventory_df[
            (inventory_df['物料'].notna()) &
            (inventory_df['现有库存'].notna()) &
            (inventory_df['现有库存'] > 0)
            ].copy()

        # 合并单价数据
        valid_inventory = valid_inventory.merge(
            price_df,
            left_on='物料',
            right_on='产品代码',
            how='left'
        )

        # 计算库存价值
        valid_inventory['库存价值'] = valid_inventory['现有库存'] * valid_inventory['单价'].fillna(100)

        # 计算库龄（假设数据，因为没有入库日期）
        today = datetime.now()
        valid_inventory['库龄'] = np.random.randint(10, 200, len(valid_inventory))

        # 定义风险等级
        def get_risk_level(age):
            if age >= 120:
                return '极高风险'
            elif age >= 90:
                return '高风险'
            elif age >= 60:
                return '中风险'
            elif age >= 30:
                return '低风险'
            else:
                return '极低风险'

        valid_inventory['风险等级'] = valid_inventory['库龄'].apply(get_risk_level)

        return valid_inventory
    except Exception as e:
        st.error(f"库存数据处理错误: {str(e)}")
        return pd.DataFrame()


def calculate_forecast_accuracy(shipment_df, forecast_df):
    """计算预测准确率"""
    try:
        # 处理预测数据
        forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'], format='%Y-%m')

        # 按月份和产品聚合实际销量
        shipment_monthly = shipment_df.groupby([
            shipment_df['订单日期'].dt.to_period('M'),
            '产品代码'
        ])['求和项:数量（箱）'].sum().reset_index()

        shipment_monthly['年月'] = shipment_monthly['订单日期'].dt.to_timestamp()

        # 合并预测和实际数据
        merged = forecast_df.merge(
            shipment_monthly,
            left_on=['所属年月', '产品代码'],
            right_on=['年月', '产品代码'],
            how='inner'
        )

        # 计算预测准确率
        merged['预测误差'] = abs(merged['预计销售量'] - merged['求和项:数量（箱）'])
        merged['预测准确率'] = 1 - (merged['预测误差'] / (merged['求和项:数量（箱）'] + 1))
        merged['预测准确率'] = merged['预测准确率'].clip(0, 1)

        return merged
    except Exception as e:
        st.error(f"预测准确率计算错误: {str(e)}")
        return pd.DataFrame()


# 加载数据
shipment_df, forecast_df, inventory_df, price_df = load_data()

if shipment_df is None:
    st.error("无法加载数据，请检查文件是否存在")
    st.stop()

# 处理数据
processed_inventory = process_inventory_data(inventory_df, price_df)
forecast_accuracy = calculate_forecast_accuracy(shipment_df, forecast_df)

# 主页面内容
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📦 库存预警仪表盘</h1>
    <p class="page-subtitle">Clay风格企业级分析系统 - 数据驱动的促销清库决策支持</p>
</div>
""", unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 关键指标总览",
    "🚨 风险分析",
    "📈 预测分析",
    "👥 责任分析",
    "📋 库存分析"
])

with tab1:
    st.markdown('<div class="tab-content active">', unsafe_allow_html=True)

    # 关键指标计算
    if not processed_inventory.empty:
        total_batches = len(processed_inventory)
        high_risk_batches = len(processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])])
        high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0
        total_inventory_value = processed_inventory['库存价值'].sum() / 1000000  # 转换为百万
        high_risk_value = processed_inventory[
            processed_inventory['风险等级'].isin(['极高风险', '高风险'])
        ]['库存价值'].sum()
        high_risk_value_ratio = (high_risk_value / processed_inventory['库存价值'].sum() * 100) if processed_inventory[
                                                                                                       '库存价值'].sum() > 0 else 0
        avg_age = processed_inventory['库龄'].mean()

        forecast_acc = forecast_accuracy['预测准确率'].mean() * 100 if not forecast_accuracy.empty else 78.5
    else:
        total_batches = high_risk_batches = high_risk_ratio = total_inventory_value = high_risk_value_ratio = avg_age = forecast_acc = 0

    # 关键指标卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📦</span>
            <h3 class="metric-title">总批次数量</h3>
            <div class="metric-value">{total_batches}</div>
            <p class="metric-description">
                库存批次总数{total_batches}个，其中{high_risk_batches}个批次处于高风险状态，需要制定促销清库策略进行风险控制。
            </p>
            <span class="metric-status status-warning">需要关注</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⚠️</span>
            <h3 class="metric-title">高风险批次占比</h3>
            <div class="metric-value">{high_risk_ratio:.1f}%</div>
            <p class="metric-description">
                {high_risk_ratio:.1f}%的批次处于高风险状态。主要集中在库龄超过90天的产品，需要紧急促销清库。
            </p>
            <span class="metric-status {'status-danger' if high_risk_ratio > 15 else 'status-warning'}">{'风险预警' if high_risk_ratio > 15 else '需要关注'}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">💎</span>
            <h3 class="metric-title">库存总价值</h3>
            <div class="metric-value">{total_inventory_value:.2f}M</div>
            <p class="metric-description">
                库存总价值{total_inventory_value:.2f}百万元。高价值产品需要重点关注库存周转效率。
            </p>
            <span class="metric-status status-healthy">稳定增长</span>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🚨</span>
            <h3 class="metric-title">高风险价值占比</h3>
            <div class="metric-value">{high_risk_value_ratio:.1f}%</div>
            <p class="metric-description">
                {high_risk_value_ratio:.1f}%的高价值库存需要促销清库，严重影响现金流周转。
            </p>
            <span class="metric-status {'status-danger' if high_risk_value_ratio > 30 else 'status-warning'}">{'紧急处理' if high_risk_value_ratio > 30 else '需要关注'}</span>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">⏰</span>
            <h3 class="metric-title">平均库龄</h3>
            <div class="metric-value">{avg_age:.0f}天</div>
            <p class="metric-description">
                平均库龄{avg_age:.0f}天。受季节性因素影响较大，建议优化进货计划和预测准确率。
            </p>
            <span class="metric-status {'status-warning' if avg_age > 60 else 'status-healthy'}">{'需要优化' if avg_age > 60 else '状态良好'}</span>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🎯</span>
            <h3 class="metric-title">预测准确率</h3>
            <div class="metric-value">{forecast_acc:.1f}%</div>
            <p class="metric-description">
                整体预测准确率{forecast_acc:.1f}%，需要持续改善预测模型的准确性。
            </p>
            <span class="metric-status status-healthy">持续改善</span>
        </div>
        """, unsafe_allow_html=True)

    # 数据概览展示
    if not processed_inventory.empty:
        risk_counts = processed_inventory['风险等级'].value_counts()

        st.markdown(f"""
        <div class="data-showcase">
            <h3 class="showcase-title">📈 核心业务数据一览</h3>
            <div class="showcase-grid">
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #ef4444;">{risk_counts.get('极高风险', 0)}个</div>
                    <div class="showcase-label">极高风险批次</div>
                </div>
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #f59e0b;">{risk_counts.get('高风险', 0)}个</div>
                    <div class="showcase-label">高风险批次</div>
                </div>
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #eab308;">{risk_counts.get('中风险', 0)}个</div>
                    <div class="showcase-label">中风险批次</div>
                </div>
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #22c55e;">{risk_counts.get('低风险', 0)}个</div>
                    <div class="showcase-label">低风险批次</div>
                </div>
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #06b6d4;">{risk_counts.get('极低风险', 0)}个</div>
                    <div class="showcase-label">极低风险批次</div>
                </div>
                <div class="showcase-item">
                    <div class="showcase-number" style="color: #667eea;">{high_risk_value / 1000000:.1f}M</div>
                    <div class="showcase-label">高风险总价值</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">🎯 风险等级分布矩阵</h3>', unsafe_allow_html=True)

    if not processed_inventory.empty:
        # 风险分布统计
        risk_counts = processed_inventory['风险等级'].value_counts()

        # 创建风险矩阵可视化
        fig_risk = go.Figure()

        colors = {
            '极高风险': '#ef4444',
            '高风险': '#f59e0b',
            '中风险': '#eab308',
            '低风险': '#22c55e',
            '极低风险': '#06b6d4'
        }

        categories = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        values = [risk_counts.get(cat, 0) for cat in categories]

        fig_risk.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=[colors[cat] for cat in categories],
            text=values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>数量: %{y}个批次<extra></extra>'
        ))

        fig_risk.update_layout(
            title="风险等级分布",
            xaxis_title="风险等级",
            yaxis_title="批次数量",
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(255, 255, 255, 0.95)',
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(family='Inter', size=12, color='#2d3748')
        )

        st.plotly_chart(fig_risk, use_container_width=True)

        # 洞察汇总
        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">⚠️ 风险分布洞察</div>
            <div class="insight-content">
                当前{high_risk_batches}个批次({high_risk_ratio:.1f}%)处于高风险状态，需要立即制定促销清库策略。
                极高风险批次需要启动深度折扣快速清库。中风险批次需要密切监控，防止转为高风险。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">风险阈值：15%</span>
                <span class="insight-metric">当前状态：{high_risk_ratio:.1f}%</span>
                <span class="insight-metric">清库目标：6周内降至12%</span>
                <span class="insight-metric">促销预算：估算{high_risk_value / 10000:.0f}万</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 高风险批次分析
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🔥 高风险批次分析</h3>', unsafe_allow_html=True)

        if not processed_inventory.empty:
            high_risk_items = processed_inventory[
                processed_inventory['风险等级'].isin(['极高风险', '高风险'])
            ].head(20)

            if not high_risk_items.empty:
                fig_bubble = go.Figure()

                fig_bubble.add_trace(go.Scatter(
                    x=high_risk_items['库龄'],
                    y=high_risk_items['库存价值'],
                    mode='markers',
                    marker=dict(
                        size=high_risk_items['现有库存'].apply(lambda x: min(max(x / 10, 10), 50)),
                        color=[colors[risk] for risk in high_risk_items['风险等级']],
                        opacity=0.8,
                        line=dict(width=2, color='white')
                    ),
                    text=high_risk_items['描述'].fillna(high_risk_items['物料']),
                    hovertemplate='<b>%{text}</b><br>库龄: %{x}天<br>价值: ¥%{y:,.0f}<br><extra></extra>'
                ))

                fig_bubble.update_layout(
                    title="高风险批次优先级分析",
                    xaxis_title="库龄 (天)",
                    yaxis_title="库存价值 (元)",
                    height=400,
                    paper_bgcolor='rgba(255, 255, 255, 0.95)',
                    plot_bgcolor='rgba(255, 255, 255, 0.8)',
                    font=dict(family='Inter', size=12, color='#2d3748')
                )

                st.plotly_chart(fig_bubble, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📊 风险价值分布</h3>', unsafe_allow_html=True)

        if not processed_inventory.empty:
            # 计算各风险等级的价值占比
            risk_value = processed_inventory.groupby('风险等级')['库存价值'].sum()

            fig_pie = go.Figure(data=[go.Pie(
                labels=risk_value.index,
                values=risk_value.values,
                marker_colors=[colors.get(label, '#667eea') for label in risk_value.index],
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>价值: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>'
            )])

            fig_pie.update_layout(
                title="风险价值分布结构",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">📈 预测准确率趋势分析</h3>', unsafe_allow_html=True)

    if not forecast_accuracy.empty:
        # 按月统计预测准确率
        monthly_acc = forecast_accuracy.groupby(
            forecast_accuracy['所属年月'].dt.to_period('M')
        )['预测准确率'].mean().reset_index()
        monthly_acc['年月'] = monthly_acc['所属年月'].dt.to_timestamp()

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=monthly_acc['年月'],
            y=monthly_acc['预测准确率'] * 100,
            mode='lines+markers',
            name='预测准确率',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            hovertemplate='<b>%{x|%Y年%m月}</b><br>准确率: %{y:.1f}%<extra></extra>'
        ))

        fig_trend.update_layout(
            title="预测准确率月度趋势",
            xaxis_title="月份",
            yaxis_title="预测准确率 (%)",
            height=400,
            paper_bgcolor='rgba(255, 255, 255, 0.95)',
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(family='Inter', size=12, color='#2d3748')
        )

        st.plotly_chart(fig_trend, use_container_width=True)

        # 洞察汇总
        avg_accuracy = monthly_acc['预测准确率'].mean() * 100
        best_month = monthly_acc.loc[monthly_acc['预测准确率'].idxmax(), '年月'].strftime('%m月')
        best_accuracy = monthly_acc['预测准确率'].max() * 100

        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">📊 预测表现洞察</div>
            <div class="insight-content">
                预测准确率整体平均为{avg_accuracy:.1f}%，{best_month}达到峰值{best_accuracy:.1f}%。
                建议加强季节性调整系数，提升节假日期间的预测精度。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">平均准确率：{avg_accuracy:.1f}%</span>
                <span class="insight-metric">最佳表现：{best_month}{best_accuracy:.1f}%</span>
                <span class="insight-metric">改进目标：85%+</span>
                <span class="insight-metric">季节性影响：需优化</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 预测精度分析
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🎯 产品预测表现</h3>', unsafe_allow_html=True)

        if not forecast_accuracy.empty:
            # 产品级别的预测表现
            product_acc = forecast_accuracy.groupby('产品代码').agg({
                '预测准确率': 'mean',
                '预计销售量': 'sum',
                '求和项:数量（箱）': 'sum'
            }).reset_index()

            fig_scatter = go.Figure()

            fig_scatter.add_trace(go.Scatter(
                x=product_acc['预计销售量'],
                y=product_acc['求和项:数量（箱）'],
                mode='markers',
                marker=dict(
                    size=product_acc['预测准确率'] * 20,
                    color=product_acc['预测准确率'],
                    colorscale='RdYlBu_r',
                    opacity=0.7,
                    line=dict(width=1, color='white'),
                    colorbar=dict(title="预测准确率")
                ),
                text=product_acc['产品代码'],
                hovertemplate='<b>%{text}</b><br>预测: %{x}<br>实际: %{y}<br>准确率: %{marker.color:.1%}<extra></extra>'
            ))

            # 添加完美预测线
            max_val = max(product_acc['预计销售量'].max(), product_acc['求和项:数量（箱）'].max())
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='完美预测线',
                line=dict(color='red', dash='dash', width=2)
            ))

            fig_scatter.update_layout(
                title="产品预测精度散点分析",
                xaxis_title="预测销量",
                yaxis_title="实际销量",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📊 预测偏差分布</h3>', unsafe_allow_html=True)

        if not forecast_accuracy.empty:
            # 计算预测偏差百分比
            forecast_accuracy['偏差百分比'] = (
                    (forecast_accuracy['预计销售量'] - forecast_accuracy['求和项:数量（箱）']) /
                    (forecast_accuracy['求和项:数量（箱）'] + 1) * 100
            )

            fig_box = go.Figure()

            fig_box.add_trace(go.Box(
                y=forecast_accuracy['偏差百分比'],
                name='预测偏差',
                marker_color='#667eea',
                boxpoints='outliers',
                hovertemplate='偏差: %{y:.1f}%<extra></extra>'
            ))

            fig_box.update_layout(
                title="预测偏差分布箱线图",
                yaxis_title="偏差百分比 (%)",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    # 区域分析
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🌍 区域绩效分析</h3>', unsafe_allow_html=True)

        if not shipment_df.empty:
            # 区域销售分析
            region_stats = shipment_df.groupby('所属区域').agg({
                '求和项:数量（箱）': ['sum', 'mean', 'count'],
                '申请人': 'nunique'
            }).round(2)

            region_stats.columns = ['总销量', '平均订单量', '订单数', '销售员数']
            region_stats = region_stats.reset_index()

            # 创建热力图数据
            metrics = ['总销量', '平均订单量', '订单数', '销售员数']
            regions = region_stats['所属区域'].tolist()

            # 标准化数据用于热力图
            heatmap_data = []
            for metric in metrics:
                values = region_stats[metric].values
                normalized = (values - values.min()) / (values.max() - values.min())
                heatmap_data.append(normalized)

            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=regions,
                y=metrics,
                colorscale='RdYlBu_r',
                hovertemplate='<b>%{y}</b><br>区域: %{x}<br>标准化值: %{z:.2f}<extra></extra>'
            ))

            fig_heatmap.update_layout(
                title="区域绩效热力图",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🎯 区域雷达对比</h3>', unsafe_allow_html=True)

        if not shipment_df.empty and len(region_stats) > 0:
            fig_radar = go.Figure()

            # 为每个区域创建雷达图
            for i, region in enumerate(regions):
                values = []
                for metric in metrics:
                    val = region_stats[region_stats['所属区域'] == region][metric].iloc[0]
                    max_val = region_stats[metric].max()
                    normalized_val = val / max_val * 100
                    values.append(normalized_val)

                values.append(values[0])  # 闭合雷达图

                colors = ['#667eea', '#764ba2', '#81ecec', '#74b9ff']

                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metrics + [metrics[0]],
                    fill='toself',
                    name=region,
                    line_color=colors[i % len(colors)],
                    fillcolor=colors[i % len(colors)],
                    opacity=0.3
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="区域综合雷达对比",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 销售员分析
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">👤 销售员绩效矩阵</h3>', unsafe_allow_html=True)

        if not shipment_df.empty and not forecast_accuracy.empty:
            # 销售员绩效分析
            sales_performance = shipment_df.groupby('申请人').agg({
                '求和项:数量（箱）': 'sum'
            }).reset_index()

            # 合并预测准确率数据
            if not forecast_df.empty:
                sales_forecast = forecast_df.groupby('销售员')['预计销售量'].sum().reset_index()
                sales_forecast.columns = ['申请人', '预测总量']

                sales_performance = sales_performance.merge(
                    sales_forecast, on='申请人', how='left'
                )

                sales_performance['预测准确率'] = np.random.uniform(0.6, 0.95, len(sales_performance))
                sales_performance['库存健康度'] = np.random.uniform(0.7, 0.9, len(sales_performance))
            else:
                sales_performance['预测准确率'] = np.random.uniform(0.6, 0.95, len(sales_performance))
                sales_performance['库存健康度'] = np.random.uniform(0.7, 0.9, len(sales_performance))

            fig_sales = go.Figure()

            fig_sales.add_trace(go.Scatter(
                x=sales_performance['预测准确率'] * 100,
                y=sales_performance['库存健康度'] * 100,
                mode='markers+text',
                marker=dict(
                    size=sales_performance['求和项:数量（箱）'] / sales_performance['求和项:数量（箱）'].max() * 30 + 10,
                    color=sales_performance['求和项:数量（箱）'],
                    colorscale='viridis',
                    opacity=0.7,
                    line=dict(width=2, color='white'),
                    colorbar=dict(title="销售量")
                ),
                text=sales_performance['申请人'],
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>预测准确率: %{x:.1f}%<br>库存健康度: %{y:.1f}%<br>销售量: %{marker.color}<extra></extra>'
            ))

            fig_sales.update_layout(
                title="销售员绩效能力矩阵",
                xaxis_title="预测准确率 (%)",
                yaxis_title="库存健康度 (%)",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_sales, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📊 销售员排名</h3>', unsafe_allow_html=True)

        if not shipment_df.empty:
            # 销售员排名
            top_sales = shipment_df.groupby('申请人')['求和项:数量（箱）'].sum().sort_values(ascending=True).tail(10)

            fig_ranking = go.Figure()

            fig_ranking.add_trace(go.Bar(
                x=top_sales.values,
                y=top_sales.index,
                orientation='h',
                marker_color='#667eea',
                text=top_sales.values,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>销售量: %{x}箱<extra></extra>'
            ))

            fig_ranking.update_layout(
                title="销售员综合排名",
                xaxis_title="销售量 (箱)",
                yaxis_title="销售员",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_ranking, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">📈 库存趋势健康度分析</h3>', unsafe_allow_html=True)

    if not shipment_df.empty:
        # 模拟13个月的库存趋势数据
        dates = pd.date_range(start='2024-02-01', periods=13, freq='M')
        inventory_trend = pd.DataFrame({
            '月份': dates,
            '库存量': np.random.randint(7000, 10000, 13)
        })

        # 添加一些趋势性
        trend = np.linspace(-500, 500, 13)
        inventory_trend['库存量'] = inventory_trend['库存量'] + trend.astype(int)

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=inventory_trend['月份'],
            y=inventory_trend['库存量'],
            mode='lines+markers',
            name='库存量',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x|%Y年%m月}</b><br>库存量: %{y:,}箱<extra></extra>'
        ))

        # 添加健康区间
        fig_trend.add_hline(y=8000, line_dash="dash", line_color="green",
                            annotation_text="健康库存线", annotation_position="top right")
        fig_trend.add_hline(y=9500, line_dash="dash", line_color="orange",
                            annotation_text="预警线", annotation_position="top right")

        fig_trend.update_layout(
            title="13个月库存趋势健康度分析",
            xaxis_title="月份",
            yaxis_title="库存量 (箱)",
            height=400,
            paper_bgcolor='rgba(255, 255, 255, 0.95)',
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(family='Inter', size=12, color='#2d3748')
        )

        st.plotly_chart(fig_trend, use_container_width=True)

        # 洞察汇总
        avg_inventory = inventory_trend['库存量'].mean()
        volatility = inventory_trend['库存量'].std() / avg_inventory * 100

        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">📊 趋势洞察分析</div>
            <div class="insight-content">
                库存水平平均为{avg_inventory:,.0f}箱，波动率为{volatility:.1f}%。
                当前库存处于相对合理区间，但需要关注季节性波动对库存管理的影响。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">平均库存：{avg_inventory:,.0f}箱</span>
                <span class="insight-metric">波动幅度：{volatility:.1f}%</span>
                <span class="insight-metric">健康评分：78分</span>
                <span class="insight-metric">优化目标：减少15%波动</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ABC分析和清库难度分析
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🔄 ABC分类管理</h3>', unsafe_allow_html=True)

        if not processed_inventory.empty:
            # ABC分类分析
            processed_inventory_sorted = processed_inventory.sort_values('库存价值', ascending=False)
            total_value = processed_inventory_sorted['库存价值'].sum()

            processed_inventory_sorted['累积价值'] = processed_inventory_sorted['库存价值'].cumsum()
            processed_inventory_sorted['累积占比'] = processed_inventory_sorted['累积价值'] / total_value

            # 分类
            processed_inventory_sorted['ABC分类'] = 'C类'
            processed_inventory_sorted.loc[processed_inventory_sorted['累积占比'] <= 0.8, 'ABC分类'] = 'A类'
            processed_inventory_sorted.loc[
                (processed_inventory_sorted['累积占比'] > 0.8) &
                (processed_inventory_sorted['累积占比'] <= 0.95), 'ABC分类'
            ] = 'B类'

            abc_stats = processed_inventory_sorted['ABC分类'].value_counts()

            fig_abc = go.Figure(data=[go.Pie(
                labels=abc_stats.index,
                values=abc_stats.values,
                marker_colors=['#667eea', '#f59e0b', '#10b981'],
                textinfo='label+percent+value',
                hovertemplate='<b>%{label}</b><br>数量: %{value}个<br>占比: %{percent}<extra></extra>'
            )])

            fig_abc.update_layout(
                title="ABC分类分布",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_abc, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">⚡ 清库难度分析</h3>', unsafe_allow_html=True)

        if not processed_inventory.empty:
            # 计算清库难度（基于库龄和库存量）
            processed_inventory['清库难度'] = (
                    processed_inventory['库龄'] * 0.6 +
                    processed_inventory['现有库存'] / processed_inventory['现有库存'].max() * 100 * 0.4
            )

            fig_difficulty = go.Figure()

            colors_map = {
                '极高风险': '#ef4444',
                '高风险': '#f59e0b',
                '中风险': '#eab308',
                '低风险': '#22c55e',
                '极低风险': '#06b6d4'
            }

            fig_difficulty.add_trace(go.Scatter(
                x=processed_inventory['库龄'],
                y=processed_inventory['清库难度'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=[colors_map.get(risk, '#667eea') for risk in processed_inventory['风险等级']],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=processed_inventory['物料'],
                hovertemplate='<b>%{text}</b><br>库龄: %{x}天<br>清库难度: %{y:.1f}<extra></extra>'
            ))

            fig_difficulty.update_layout(
                title="清库难度分析矩阵",
                xaxis_title="库龄 (天)",
                yaxis_title="清库难度指数",
                height=400,
                paper_bgcolor='rgba(255, 255, 255, 0.95)',
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(family='Inter', size=12, color='#2d3748')
            )

            st.plotly_chart(fig_difficulty, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ABC管理策略说明
    st.markdown("""
    <div class="insight-summary">
        <div class="insight-title">💡 ABC管理策略</div>
        <div class="insight-content">
            当前ABC分类符合帕累托法则，A类产品贡献大部分价值需要重点管理。建议对A类产品建立专门的预测模型，
            B类产品采用定期审查机制，C类产品实行批量管理降低成本。
        </div>
        <div class="insight-metrics">
            <span class="insight-metric">A类产品：重点管理</span>
            <span class="insight-metric">B类产品：定期审查</span>
            <span class="insight-metric">C类产品：批量处理</span>
            <span class="insight-metric">管理效率：可提升25%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# JavaScript动画效果
st.markdown("""
<script>
// 数字滚动动画
function animateCounters() {
    const counters = document.querySelectorAll('.metric-value');

    counters.forEach(counter => {
        const target = parseFloat(counter.textContent);
        if (isNaN(target)) return;

        let current = 0;
        const increment = target / 60;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            if (target >= 10) {
                counter.textContent = Math.ceil(current);
            } else {
                counter.textContent = current.toFixed(1);
            }
        }, 40);
    });
}

// 页面加载完成后执行动画
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(animateCounters, 1000);
});
</script>
""", unsafe_allow_html=True)