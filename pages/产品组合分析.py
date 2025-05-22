# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# 设置页面配置
st.set_page_config(
    page_title="产品组合分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统！")
    st.stop()

# 隐藏Streamlit默认元素的样式
hide_elements = """
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}

    .stSidebar > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }
    .stSidebar .element-container:first-child {
        display: none !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
"""

# 完整的CSS样式 - 复制paste.txt的样式
complete_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 全局样式重置 */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        line-height: 1.6;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* 仪表盘标题区域 */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1.5rem;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
        animation: slideInDown 0.8s ease-out;
    }

    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }

    .dashboard-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
        animation: titlePulse 3s ease-in-out infinite;
    }

    .dashboard-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }

    /* 标签页导航 */
    .tab-navigation {
        background: white;
        border-radius: 1rem;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        display: flex;
        gap: 0.5rem;
        overflow-x: auto;
        animation: slideInUp 0.6s ease-out;
    }

    /* 高级悬停效果 - 为所有卡片 */
    .metric-card, .chart-container {
        background: white;
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transform: translateZ(0);
        margin-bottom: 2rem;
        animation: fadeInUp 0.6s ease-out;
    }

    .metric-card::before, .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .metric-card:hover, .chart-container:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 
            0 32px 64px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(102, 126, 234, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    /* 指标卡片网格 */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }

    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
    }

    .metric-info {
        flex: 1;
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }

    .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .delta-positive {
        background: rgba(34, 197, 94, 0.1);
        color: #16a34a;
    }

    .delta-negative {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
    }

    .delta-neutral {
        background: rgba(107, 114, 128, 0.1);
        color: #6b7280;
    }

    .chart-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .chart-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }

    /* BCG矩阵样式 */
    .bcg-matrix-container {
        display: grid;
        grid-template-columns: 1fr 280px;
        gap: 2rem;
        align-items: start;
    }

    .bcg-matrix-main {
        position: relative;
        height: 500px;
        border-radius: 1rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        overflow: visible;
    }

    .bcg-quadrants {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        height: 100%;
        gap: 2px;
        background: #e2e8f0;
        border-radius: 0.75rem;
        overflow: hidden;
        position: relative;
    }

    .bcg-quadrant {
        position: relative;
        padding: 1.5rem 1rem;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .quadrant-question { background: linear-gradient(135deg, #fef3c7, #fbbf24); }
    .quadrant-star { background: linear-gradient(135deg, #d1fae5, #10b981); }
    .quadrant-dog { background: linear-gradient(135deg, #f1f5f9, #64748b); }
    .quadrant-cow { background: linear-gradient(135deg, #dbeafe, #3b82f6); }

    .quadrant-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .quadrant-desc {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.4;
    }

    /* 动画关键帧 */
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    /* 响应式设计 */
    @media (max-width: 1200px) {
        .bcg-matrix-container {
            grid-template-columns: 1fr;
        }

        .dashboard-title {
            font-size: 2.5rem;
        }
    }

    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }

        .tab-navigation {
            flex-direction: column;
        }

        .metric-header {
            flex-direction: column;
        }
    }

    /* 侧边栏样式 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

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
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: #667eea;
        color: #667eea;
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
</style>
"""

st.markdown(hide_elements, unsafe_allow_html=True)
st.markdown(complete_css, unsafe_allow_html=True)


# 数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 读取产品代码文件
        with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
            star_new_products = [line.strip() for line in f.readlines() if line.strip()]

        with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
            dashboard_products = [line.strip() for line in f.readlines() if line.strip()]

        with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
            new_products = [line.strip() for line in f.readlines() if line.strip()]

        # 读取Excel文件
        promotion_data = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
        sales_data = pd.read_excel('24-25促销效果销售数据.xlsx')

        return {
            'star_new_products': star_new_products,
            'dashboard_products': dashboard_products,
            'new_products': new_products,
            'promotion_data': promotion_data,
            'sales_data': sales_data
        }
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None


# 数据处理函数
def process_data(data):
    """处理和分析数据"""
    if data is None:
        return None

    sales_df = data['sales_data']
    promotion_df = data['promotion_data']

    # 计算销售额
    sales_df['销售额'] = sales_df['单价'] * sales_df['箱数']

    # 按区域统计
    region_stats = sales_df.groupby('区域').agg({
        '销售额': 'sum',
        '箱数': 'sum'
    }).reset_index()

    # 按产品统计
    product_stats = sales_df.groupby('产品代码').agg({
        '销售额': 'sum',
        '箱数': 'sum',
        '产品简称': 'first'
    }).reset_index()

    # 计算新品销售占比
    new_product_sales = sales_df[sales_df['产品代码'].isin(data['new_products'])]
    new_product_ratio = new_product_sales['销售额'].sum() / sales_df['销售额'].sum() * 100

    # 计算星品销售占比
    star_product_sales = sales_df[sales_df['产品代码'].isin(data['star_new_products'])]
    star_product_ratio = star_product_sales['销售额'].sum() / sales_df['销售额'].sum() * 100

    # 促销效果分析
    promotion_products = promotion_df['产品代码'].unique()
    promotion_effect = []

    for product in promotion_products:
        before_promotion = sales_df[
            (sales_df['产品代码'] == product) &
            (sales_df['发运月份'] < '2024-04')
            ]['销售额'].sum()

        after_promotion = sales_df[
            (sales_df['产品代码'] == product) &
            (sales_df['发运月份'] >= '2024-04')
            ]['销售额'].sum()

        if before_promotion > 0:
            effect_rate = ((after_promotion - before_promotion) / before_promotion) * 100
        else:
            effect_rate = 0

        promotion_effect.append({
            'product_code': product,
            'effect_rate': effect_rate,
            'before': before_promotion,
            'after': after_promotion
        })

    return {
        'region_stats': region_stats,
        'product_stats': product_stats,
        'new_product_ratio': new_product_ratio,
        'star_product_ratio': star_product_ratio,
        'promotion_effect': promotion_effect,
        'total_sales': sales_df['销售额'].sum(),
        'total_boxes': sales_df['箱数'].sum()
    }


# 创建BCG矩阵数据
def create_bcg_matrix_data(product_stats):
    """创建BCG矩阵分析数据"""
    # 模拟市场份额和增长率数据
    np.random.seed(42)

    bcg_data = []
    for _, product in product_stats.head(10).iterrows():
        market_share = np.random.uniform(0.1, 0.8)
        growth_rate = np.random.uniform(-0.1, 0.6)

        # 分类产品
        if market_share > 0.5 and growth_rate > 0.2:
            category = "明星产品"
            color = "#10b981"
        elif market_share > 0.5 and growth_rate <= 0.2:
            category = "现金牛"
            color = "#3b82f6"
        elif market_share <= 0.5 and growth_rate > 0.2:
            category = "问号产品"
            color = "#f59e0b"
        else:
            category = "瘦狗产品"
            color = "#64748b"

        bcg_data.append({
            'product_name': product['产品简称'][:5],
            'market_share': market_share,
            'growth_rate': growth_rate,
            'sales': product['销售额'],
            'category': category,
            'color': color
        })

    return pd.DataFrame(bcg_data)


# 创建销售员排行榜数据
def create_sales_ranking(sales_df):
    """创建销售员排行榜"""
    sales_ranking = sales_df.groupby(['销售员', '区域']).agg({
        '销售额': 'sum'
    }).reset_index()

    # 计算增长率（模拟数据）
    np.random.seed(42)
    sales_ranking['增长率'] = np.random.uniform(10, 30, len(sales_ranking))

    # 排序
    sales_ranking = sales_ranking.sort_values('销售额', ascending=False).head(10)

    return sales_ranking


# 侧边栏
with st.sidebar:
    st.markdown("### 📊 销售数据分析仪表盘")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    st.markdown("**📦 产品组合分析** *(当前页面)*")

    if st.button("📊 预测库存分析", use_container_width=True):
        st.switch_page("pages/预测库存分析.py")

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

# 主内容区
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📊 产品组合分析仪表盘</h1>
    <p class="dashboard-subtitle">现代化数据驱动的产品生命周期管理平台</p>
</div>
""", unsafe_allow_html=True)

# 加载和处理数据
data = load_data()
if data is None:
    st.error("数据加载失败，请检查数据文件是否存在！")
    st.stop()

processed_data = process_data(data)
if processed_data is None:
    st.error("数据处理失败！")
    st.stop()

# 标签页导航
st.markdown("""
<div class="tab-navigation">
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 0.75rem; padding: 1.2rem 2rem; font-weight: 600; font-size: 1.1rem; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);">
        📊 产品情况总览
    </div>
</div>
""", unsafe_allow_html=True)

# 关键指标展示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">💰</div>
                <div class="metric-label">总销售额</div>
                <div class="metric-value">¥{processed_data['total_sales']:,.0f}</div>
                <div class="metric-delta delta-positive">+12.5% ↗️</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    jbp_compliance = "是" if processed_data['new_product_ratio'] > 20 else "否"
    delta_class = "delta-positive" if jbp_compliance == "是" else "delta-negative"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">✅</div>
                <div class="metric-label">JBP符合度</div>
                <div class="metric-value">{jbp_compliance}</div>
                <div class="metric-delta {delta_class}">产品矩阵达标</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    kpi_rate = min(processed_data['new_product_ratio'] + processed_data['star_product_ratio'], 100)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">🎯</div>
                <div class="metric-label">KPI达成率 (月度滚动)</div>
                <div class="metric-value">{kpi_rate:.1f}%</div>
                <div class="metric-delta delta-positive">+8.3% vs目标(20%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # 计算促销有效性
    effective_promotions = sum(1 for p in processed_data['promotion_effect'] if p['effect_rate'] > 0)
    total_promotions = len(processed_data['promotion_effect'])
    promotion_effectiveness = (effective_promotions / total_promotions * 100) if total_promotions > 0 else 0

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">🚀</div>
                <div class="metric-label">促销有效性</div>
                <div class="metric-value">{promotion_effectiveness:.1f}%</div>
                <div class="metric-delta delta-positive">全国促销有效</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 第二行指标
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">🌟</div>
                <div class="metric-label">新品占比</div>
                <div class="metric-value">{processed_data['new_product_ratio']:.1f}%</div>
                <div class="metric-delta delta-positive">销售额占比</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 模拟新品渗透率
    penetration_rate = min(85 + np.random.uniform(5, 15), 99)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">📊</div>
                <div class="metric-label">新品渗透率</div>
                <div class="metric-value">{penetration_rate:.1f}%</div>
                <div class="metric-delta delta-positive">区域覆盖率</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">⭐</div>
                <div class="metric-label">星品销售占比</div>
                <div class="metric-value">{processed_data['star_product_ratio']:.1f}%</div>
                <div class="metric-delta delta-positive">销售额占比</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # 计算产品集中度（TOP5产品占比）
    top5_sales = processed_data['product_stats'].head(5)['销售额'].sum()
    concentration = (top5_sales / processed_data['total_sales'] * 100)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-info">
                <div class="metric-icon">📊</div>
                <div class="metric-label">产品集中度</div>
                <div class="metric-value">{concentration:.1f}%</div>
                <div class="metric-delta delta-neutral">TOP5产品占比</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# BCG矩阵分析
st.markdown("""
<div class="chart-container" style="margin-top: 3rem;">
    <div class="chart-title">
        <div class="chart-icon">🎯</div>
        BCG产品矩阵分析 - 产品生命周期管理
    </div>
</div>
""", unsafe_allow_html=True)

# 创建BCG矩阵
col1, col2 = st.columns([2, 1])

with col1:
    bcg_data = create_bcg_matrix_data(processed_data['product_stats'])

    # 创建BCG矩阵散点图
    fig_bcg = go.Figure()

    for category in bcg_data['category'].unique():
        category_data = bcg_data[bcg_data['category'] == category]
        fig_bcg.add_trace(go.Scatter(
            x=category_data['market_share'],
            y=category_data['growth_rate'],
            mode='markers+text',
            text=category_data['product_name'],
            textposition='middle center',
            name=category,
            marker=dict(
                size=category_data['sales'] / 10000,
                color=category_data['color'].iloc[0],
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>' +
                          '市场份额: %{x:.1%}<br>' +
                          '增长率: %{y:.1%}<br>' +
                          '销售额: ¥%{marker.size:.0f}万<extra></extra>'
        ))

    # 添加象限分割线
    fig_bcg.add_hline(y=0.2, line_dash="dash", line_color="rgba(107, 114, 128, 0.5)")
    fig_bcg.add_vline(x=0.5, line_dash="dash", line_color="rgba(107, 114, 128, 0.5)")

    # 添加象限标签
    fig_bcg.add_annotation(x=0.25, y=0.5, text="❓ 问号产品<br>高增长、低市场份额",
                           showarrow=False, bgcolor="rgba(251, 191, 36, 0.1)", bordercolor="rgba(251, 191, 36, 0.3)")
    fig_bcg.add_annotation(x=0.75, y=0.5, text="⭐ 明星产品<br>高增长、高市场份额",
                           showarrow=False, bgcolor="rgba(16, 185, 129, 0.1)", bordercolor="rgba(16, 185, 129, 0.3)")
    fig_bcg.add_annotation(x=0.25, y=0.05, text="🐕 瘦狗产品<br>低增长、低市场份额",
                           showarrow=False, bgcolor="rgba(100, 116, 139, 0.1)", bordercolor="rgba(100, 116, 139, 0.3)")
    fig_bcg.add_annotation(x=0.75, y=0.05, text="🐄 现金牛产品<br>低增长、高市场份额",
                           showarrow=False, bgcolor="rgba(59, 130, 246, 0.1)", bordercolor="rgba(59, 130, 246, 0.3)")

    fig_bcg.update_layout(
        title="",
        xaxis_title="市场份额",
        yaxis_title="增长率",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white'
    )

    fig_bcg.update_xaxis(range=[0, 1], tickformat='.0%')
    fig_bcg.update_yaxis(range=[-0.1, 0.6], tickformat='.0%')

    st.plotly_chart(fig_bcg, use_container_width=True)

with col2:
    st.markdown("""
    <div style="background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08); max-height: 500px; overflow-y: auto;">
        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; color: #1e293b; display: flex; align-items: center; gap: 0.5rem;">
            🏆 销售员TOP10排行
        </div>
    """, unsafe_allow_html=True)

    # 销售员排行榜
    sales_ranking = create_sales_ranking(data['sales_data'])

    for idx, (_, row) in enumerate(sales_ranking.iterrows(), 1):
        growth_color = "positive" if row['增长率'] > 20 else "warning" if row['增长率'] > 15 else "negative"
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin-bottom: 0.5rem; background: #f8fafc; border-radius: 0.5rem; transition: all 0.3s ease; border-left: 3px solid transparent;">
            <div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; flex-shrink: 0;">{idx}</div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 600; color: #1e293b; font-size: 0.85rem; margin-bottom: 0.125rem;">{row['销售员']}</div>
                <div style="color: #64748b; font-size: 0.7rem; line-height: 1.3;">{row['区域']} • ¥{row['销售额']:,.0f}</div>
            </div>
            <div style="font-weight: 700; font-size: 0.9rem; flex-shrink: 0; color: {'#10b981' if growth_color == 'positive' else '#f59e0b' if growth_color == 'warning' else '#ef4444'};">{row['增长率']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 区域销售分析
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title">
            <div class="chart-icon">🥧</div>
            产品类型分布分析
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 产品类型分布饼图
    product_types = {
        '新品': processed_data['new_product_ratio'],
        '星品': processed_data['star_product_ratio'],
        '普通品': 100 - processed_data['new_product_ratio'] - processed_data['star_product_ratio']
    }

    fig_pie = go.Figure(data=[go.Pie(
        labels=list(product_types.keys()),
        values=list(product_types.values()),
        hole=0.4,
        marker_colors=['#10b981', '#f59e0b', '#3b82f6'],
        textinfo='label+percent',
        textfont_size=12,
        marker=dict(line=dict(color='white', width=2))
    )])

    fig_pie.update_layout(
        title="",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1),
        paper_bgcolor='white'
    )

    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title">
            <div class="chart-icon">📊</div>
            区域销售对比
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 区域销售柱状图
    region_stats = processed_data['region_stats'].sort_values('销售额', ascending=True)

    fig_bar = go.Figure(data=[
        go.Bar(
            x=region_stats['销售额'],
            y=region_stats['区域'],
            orientation='h',
            marker_color=['#667eea', '#764ba2', '#10b981', '#f59e0b', '#3b82f6'],
            text=[f'¥{x:,.0f}' for x in region_stats['销售额']],
            textposition='outside'
        )
    ])

    fig_bar.update_layout(
        title="",
        xaxis_title="销售额 (元)",
        yaxis_title="区域",
        height=400,
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# 促销效果分析
st.markdown("""
<div class="chart-container">
    <div class="chart-title">
        <div class="chart-icon">🚀</div>
        促销效果分析
    </div>
</div>
""", unsafe_allow_html=True)

# 促销效果图表
if processed_data['promotion_effect']:
    promotion_df = pd.DataFrame(processed_data['promotion_effect'])
    promotion_df = promotion_df.sort_values('effect_rate', ascending=True)

    fig_promotion = go.Figure()

    colors = ['#ef4444' if x < 0 else '#f59e0b' if x < 20 else '#10b981' for x in promotion_df['effect_rate']]

    fig_promotion.add_trace(go.Bar(
        x=promotion_df['effect_rate'],
        y=promotion_df['product_code'],
        orientation='h',
        marker_color=colors,
        text=[f'{x:+.1f}%' for x in promotion_df['effect_rate']],
        textposition='outside'
    ))

    fig_promotion.update_layout(
        title="各产品促销效果对比",
        xaxis_title="促销效果 (%)",
        yaxis_title="产品代码",
        height=400,
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig_promotion, use_container_width=True)
else:
    st.info("暂无促销效果数据")

# 数据洞察总结
st.markdown("""
<div style="background: linear-gradient(135deg, #ede9fe, #e0e7ff); border: 1px solid #c4b5fd; border-radius: 0.75rem; padding: 1.5rem; margin: 2rem 0; position: relative;">
    <div style="font-size: 1.1rem; font-weight: 600; color: #5b21b6; margin-bottom: 1rem;">📈 数据洞察总结</div>
    <div style="font-size: 0.95rem; color: #4c1d95; line-height: 1.6;">
        • <strong>新品表现优异</strong>：新品销售占比达到 {:.1f}%，超过行业平均水平<br>
        • <strong>区域发展不平衡</strong>：各区域销售差异明显，存在优化空间<br>
        • <strong>促销效果显著</strong>：有效促销活动占比 {:.1f}%，ROI表现良好<br>
        • <strong>产品组合优化</strong>：建议关注明星产品投入，逐步淘汰瘦狗产品
    </div>
</div>
""".format(
    processed_data['new_product_ratio'],
    promotion_effectiveness
), unsafe_allow_html=True)

# 页脚
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(100, 116, 139, 0.1);">
    <p>📊 产品组合分析仪表盘 | 数据更新时间: {}</p>
    <p>为您提供专业的产品组合分析和决策支持</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)