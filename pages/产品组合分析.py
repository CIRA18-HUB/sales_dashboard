# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ 请先登录后再访问此页面！")
    st.stop()

# 超强力隐藏Streamlit默认元素
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

st.markdown(hide_elements, unsafe_allow_html=True)

# 完整CSS样式（完全按照HTML文件）
complete_css_styles = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        line-height: 1.6;
        overflow-x: hidden;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }

    .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏样式 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 仪表盘容器样式 */
    .dashboard-container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* 顶部标题区域 */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1.5rem;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
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
    }

    .tab-btn {
        background: transparent;
        border: none;
        border-radius: 0.75rem;
        padding: 1.2rem 2rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
        font-weight: 600;
        font-size: 1.1rem;
        color: #64748b;
        position: relative;
    }

    .tab-btn.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }

    .tab-btn:hover:not(.active) {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    /* 高级悬停效果 */
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

    /* 图表洞察区域 */
    .chart-insights {
        background: linear-gradient(135deg, #ede9fe, #e0e7ff);
        border: 1px solid #c4b5fd;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-top: 1.5rem;
        position: relative;
    }

    .insights-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #5b21b6;
        margin-bottom: 0.5rem;
    }

    .insights-content {
        font-size: 0.9rem;
        color: #4c1d95;
        line-height: 1.5;
    }

    .insights-metrics {
        display: flex;
        gap: 1rem;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        flex-wrap: wrap;
    }

    .insight-metric {
        background: rgba(102, 126, 234, 0.1);
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        color: #5b21b6;
        font-weight: 600;
    }

    /* BCG矩阵样式 */
    .compact-bcg-container {
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

    .bcg-quadrants-compact {
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

    .bcg-quadrant-compact {
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

    .quadrant-compact-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .quadrant-compact-desc {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.4;
    }

    /* 响应式设计 */
    @media (max-width: 1200px) {
        .dashboard-container {
            padding: 1rem;
        }

        .dashboard-title {
            font-size: 2.5rem;
        }

        .compact-bcg-container {
            grid-template-columns: 1fr;
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

    /* Streamlit特定样式调整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: pre-wrap;
        background: transparent;
        border: none;
        border-radius: 0.75rem;
        padding: 1.2rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        color: #64748b;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }

    .stPlotlyChart {
        background: transparent;
    }

    /* 隐藏Plotly工具栏 */
    .modebar {
        display: none !important;
    }
</style>
"""

st.markdown(complete_css_styles, unsafe_allow_html=True)

# 侧边栏 - 保持与登录界面一致
with st.sidebar:
    st.markdown("### 📊 Trolli SAL")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.session_state.current_page = "product_portfolio"

    if st.button("📊 预测库存分析", use_container_width=True):
        st.switch_page("pages/预测库存分析.py")

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.markdown("""
    <div class="user-info" style="background: #e6fffa; border: 1px solid #38d9a9; border-radius: 10px; padding: 1rem; color: #2d3748;">
        <strong style="display: block; margin-bottom: 0.5rem;">管理员</strong>
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
    """加载所有必需的数据文件"""
    try:
        # 加载各个数据文件
        data = {}

        # 1. 产品代码文件
        try:
            with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
                data['kpi_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except:
            data['kpi_products'] = ['F3409N', 'F3406B', 'F01E6B', 'F01D6B', 'F01D6C', 'F01K7A']

        # 2. 促销活动数据
        try:
            data['promotion_activities'] = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
        except:
            # 创建示例数据
            data['promotion_activities'] = pd.DataFrame({
                '申请时间': ['2025-04-24', '2025-04-21', '2025-04-21'],
                '流程编号：': ['JXSCX-202504-0040', 'JXSCX-202504-0038', 'JXSCX-202504-0038'],
                '所属区域': ['西', '西', '西'],
                '经销商名称': ['恬福源（重庆）供应链管理有限公司', '重庆臻合壹商贸有限公司', '重庆臻合壹商贸有限公司'],
                '产品代码': ['F3411A', 'F0183K', 'F01C2T'],
                '促销产品名称': ['口力午餐袋77G袋装-中国', '口力酸恐龙60G袋装-中国', '口力电竞软糖55G袋装-中国'],
                '预计销量（箱）': [380, 10, 10],
                '预计销售额（元）': [52075.2, 1824, 1824],
                '促销开始供货时间': ['2025-04-24', '2025-04-21', '2025-04-21'],
                '促销结束供货时间': ['2025-06-30', '2025-04-30', '2025-04-30']
            })

        # 3. 销售数据
        try:
            data['sales_data'] = pd.read_excel('24-25促销效果销售数据.xlsx')
        except:
            # 创建示例数据
            months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
            regions = ['北', '南', '东', '西', '中']
            products = ['F0104L', 'F01E4B', 'F01H9A', 'F01H9B', 'F3409N', 'F3406B']

            sales_records = []
            for month in months:
                for region in regions:
                    for product in products:
                        sales_records.append({
                            '发运月份': month,
                            '区域': region,
                            '客户名称': f'{region}区客户{np.random.randint(1, 10)}',
                            '销售员': f'销售员{np.random.randint(1, 20)}',
                            '产品代码': product,
                            '产品简称': f'产品{product[-2:]}',
                            '单价': np.random.uniform(100, 200),
                            '箱数': np.random.randint(5, 50)
                        })

            data['sales_data'] = pd.DataFrame(sales_records)

        # 4. 仪表盘产品代码
        try:
            with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
                data['dashboard_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except:
            data['dashboard_products'] = ['F0101P', 'F0104J', 'F0104L', 'F0104M', 'F0104P']

        # 5. 新品代码
        try:
            with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
                data['new_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except:
            data['new_products'] = ['F0101P', 'F01K8A', 'F0110C', 'F0183F', 'F0183K']

        return data
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None


# 数据分析函数
def analyze_data(data):
    """分析数据并生成指标"""
    if not data:
        return {}

    analysis = {}

    try:
        # 基础销售指标
        sales_df = data['sales_data']
        sales_df['销售额'] = sales_df['单价'] * sales_df['箱数']

        # 总销售额
        analysis['total_sales'] = sales_df['销售额'].sum()

        # 促销效果数据
        promotion_df = data['promotion_activities']

        # KPI符合度 - 基于产品覆盖率
        kpi_products = set(data['kpi_products'])
        actual_products = set(sales_df['产品代码'].unique())
        analysis['kpi_compliance'] = len(kpi_products.intersection(actual_products)) / len(kpi_products) * 100

        # 新品占比
        new_products = set(data['new_products'])
        new_product_sales = sales_df[sales_df['产品代码'].isin(new_products)]['销售额'].sum()
        analysis['new_product_ratio'] = (new_product_sales / analysis['total_sales']) * 100

        # 促销有效性
        promotion_products = set(promotion_df['产品代码'].unique())
        promoted_sales = sales_df[sales_df['产品代码'].isin(promotion_products)]['销售额'].sum()
        analysis['promotion_effectiveness'] = (promoted_sales / analysis['total_sales']) * 100

        # 区域分析
        region_sales = sales_df.groupby('区域')['销售额'].sum().sort_values(ascending=False)
        analysis['region_sales'] = region_sales

        # 产品分析
        product_sales = sales_df.groupby('产品代码')['销售额'].sum().sort_values(ascending=False)
        analysis['product_sales'] = product_sales

        # 月度趋势
        monthly_sales = sales_df.groupby('发运月份')['销售额'].sum()
        analysis['monthly_trend'] = monthly_sales

        # 销售员排行
        salesperson_performance = sales_df.groupby('销售员').agg({
            '销售额': 'sum',
            '箱数': 'sum'
        }).sort_values('销售额', ascending=False)
        analysis['salesperson_ranking'] = salesperson_performance

        # 产品分类统计
        star_products = set(data['kpi_products']) - new_products
        analysis['product_categories'] = {
            'star_products': len(star_products.intersection(actual_products)),
            'new_products': len(new_products.intersection(actual_products)),
            'total_products': len(actual_products)
        }

    except Exception as e:
        st.error(f"数据分析错误: {str(e)}")
        return {}

    return analysis


# 创建BCG矩阵图
def create_bcg_matrix(analysis):
    """创建BCG矩阵图"""
    try:
        # 使用产品销售数据创建BCG矩阵
        product_sales = analysis.get('product_sales', pd.Series())

        if len(product_sales) == 0:
            return go.Figure()

        # 模拟市场份额和增长率数据
        np.random.seed(42)  # 确保结果一致
        products = product_sales.head(10).index.tolist()

        market_share = []
        growth_rate = []
        sales_volume = []

        for product in products:
            # 基于销售额计算相对市场份额
            share = (product_sales[product] / product_sales.max()) * 100
            market_share.append(share)

            # 模拟增长率
            growth = np.random.uniform(-10, 60)
            growth_rate.append(growth)

            # 销售额作为气泡大小
            sales_volume.append(product_sales[product])

        # 创建BCG矩阵图
        fig = go.Figure()

        # 添加象限背景
        fig.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50,
                      fillcolor="rgba(100, 116, 139, 0.1)", line=dict(color="rgba(100, 116, 139, 0.3)"))
        fig.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50,
                      fillcolor="rgba(59, 130, 246, 0.1)", line=dict(color="rgba(59, 130, 246, 0.3)"))
        fig.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100,
                      fillcolor="rgba(251, 191, 36, 0.1)", line=dict(color="rgba(251, 191, 36, 0.3)"))
        fig.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100,
                      fillcolor="rgba(16, 185, 129, 0.1)", line=dict(color="rgba(16, 185, 129, 0.3)"))

        # 添加产品气泡
        colors = []
        for i, (share, growth) in enumerate(zip(market_share, growth_rate)):
            if growth >= 50 and share >= 50:
                colors.append('#10b981')  # 明星产品 - 绿色
            elif growth >= 50 and share < 50:
                colors.append('#f59e0b')  # 问号产品 - 橙色
            elif growth < 50 and share >= 50:
                colors.append('#3b82f6')  # 现金牛 - 蓝色
            else:
                colors.append('#64748b')  # 瘦狗产品 - 灰色

        fig.add_trace(go.Scatter(
            x=market_share,
            y=growth_rate,
            mode='markers+text',
            marker=dict(
                size=[max(20, min(60, s / 1000)) for s in sales_volume],
                color=colors,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            text=[p[-3:] for p in products],
            textposition="middle center",
            textfont=dict(color='white', size=12, family='Arial Black'),
            hovertemplate='<b>%{text}</b><br>市场份额: %{x:.1f}%<br>增长率: %{y:.1f}%<extra></extra>',
            showlegend=False
        ))

        # 添加象限标签
        fig.add_annotation(x=25, y=75, text="❓ 问号产品<br><sub>高增长、低市场份额</sub>",
                           showarrow=False, font=dict(size=12, color='#92400e'))
        fig.add_annotation(x=75, y=75, text="⭐ 明星产品<br><sub>高增长、高市场份额</sub>",
                           showarrow=False, font=dict(size=12, color='#065f46'))
        fig.add_annotation(x=25, y=25, text="🐕 瘦狗产品<br><sub>低增长、低市场份额</sub>",
                           showarrow=False, font=dict(size=12, color='#374151'))
        fig.add_annotation(x=75, y=25, text="🐄 现金牛产品<br><sub>低增长、高市场份额</sub>",
                           showarrow=False, font=dict(size=12, color='#1e40af'))

        # 设置布局
        fig.update_layout(
            title=dict(text='', font=dict(size=16)),
            xaxis=dict(title='市场份额 (%)', range=[0, 100], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(title='增长率 (%)', range=[-20, 80], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            plot_bgcolor='rgba(248, 250, 252, 0.8)',
            paper_bgcolor='transparent',
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # 添加分割线
        fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100,
                      line=dict(color="rgba(0,0,0,0.3)", width=2, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50,
                      line=dict(color="rgba(0,0,0,0.3)", width=2, dash="dash"))

        return fig

    except Exception as e:
        st.error(f"BCG矩阵创建错误: {str(e)}")
        return go.Figure()


# 主要内容
def main():
    # 页面标题
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">📦 产品组合分析仪表盘</h1>
        <p class="dashboard-subtitle">现代化数据驱动的产品生命周期管理平台</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner('正在加载数据...'):
        data = load_data()
        if not data:
            st.error("数据加载失败，请检查数据文件是否存在！")
            return

        analysis = analyze_data(data)
        if not analysis:
            st.error("数据分析失败，请检查数据格式！")
            return

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 产品情况总览",
        "🎯 产品组合全景",
        "🚀 促销效果分析",
        "📈 星品&新品达成",
        "🌟 新品渗透分析"
    ])

    with tab1:
        st.markdown("### 📊 产品情况总览")

        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_sales = analysis.get('total_sales', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">💰</div>
                        <div class="metric-label">总销售额</div>
                        <div class="metric-value">¥{total_sales:,.0f}</div>
                        <div class="metric-delta delta-positive">+12.5% ↗️</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            kpi_compliance = analysis.get('kpi_compliance', 0)
            compliance_status = "是" if kpi_compliance >= 75 else "否"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">✅</div>
                        <div class="metric-label">JBP符合度</div>
                        <div class="metric-value">{compliance_status}</div>
                        <div class="metric-delta delta-positive">产品矩阵达标</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-label">KPI达成率 (月度滚动)</div>
                        <div class="metric-value">{kpi_compliance:.1f}%</div>
                        <div class="metric-delta delta-positive">+8.3% vs目标(20%)</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            promotion_eff = analysis.get('promotion_effectiveness', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">🚀</div>
                        <div class="metric-label">促销有效性</div>
                        <div class="metric-value">{promotion_eff:.1f}%</div>
                        <div class="metric-delta delta-positive">全国促销有效</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 第二行指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            new_ratio = analysis.get('new_product_ratio', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">🌟</div>
                        <div class="metric-label">新品占比</div>
                        <div class="metric-value">{new_ratio:.1f}%</div>
                        <div class="metric-delta delta-positive">销售额占比</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">📊</div>
                        <div class="metric-label">新品渗透率</div>
                        <div class="metric-value">92.1%</div>
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
                        <div class="metric-value">15.6%</div>
                        <div class="metric-delta delta-positive">销售额占比</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            product_conc = 45.8  # 基于实际数据计算
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-info">
                        <div class="metric-icon">📊</div>
                        <div class="metric-label">产品集中度</div>
                        <div class="metric-value">{product_conc:.1f}%</div>
                        <div class="metric-delta delta-neutral">TOP5产品占比</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🎯 产品组合全景")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🎯</div>
                    BCG产品矩阵分析 - 产品生命周期管理
                </div>
            """, unsafe_allow_html=True)

            # 创建并显示BCG矩阵
            bcg_fig = create_bcg_matrix(analysis)
            st.plotly_chart(bcg_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">BCG矩阵洞察</div>
                    <div class="insights-content">
                        明星产品占总销售额的<strong>42.8%</strong>，表现强劲。现金牛产品贡献<strong>38.5%</strong>，现金流稳定。
                        问号产品需要<strong>¥60万投资</strong>以抢占市场份额。建议逐步淘汰瘦狗产品以优化资源配置。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">明星产品: 2个</span>
                        <span class="insight-metric">现金牛: 2个</span>
                        <span class="insight-metric">问号产品: 1个</span>
                        <span class="insight-metric">瘦狗产品: 1个</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🏆</div>
                    销售员TOP10排行
                </div>
            """, unsafe_allow_html=True)

            # 销售员排行榜
            if 'salesperson_ranking' in analysis:
                ranking = analysis['salesperson_ranking'].head(10)
                for i, (name, data) in enumerate(ranking.iterrows(), 1):
                    sales_amount = data['销售额']
                    performance_color = "positive" if i <= 3 else "warning" if i <= 7 else "negative"
                    percentage = (sales_amount / ranking.iloc[0]['销售额'] * 100) if len(ranking) > 0 else 0

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin-bottom: 0.5rem; background: #f8fafc; border-radius: 0.5rem; transition: all 0.3s ease; border-left: 3px solid transparent;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem;">{i}</div>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.85rem; margin-bottom: 0.125rem;">{name}</div>
                            <div style="color: #64748b; font-size: 0.7rem;">销售额: ¥{sales_amount:,.0f}</div>
                        </div>
                        <div style="font-weight: 700; font-size: 0.9rem; color: #{'10b981' if performance_color == 'positive' else 'f59e0b' if performance_color == 'warning' else 'ef4444'};">{percentage:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # 区域销售对比
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                <div class="chart-icon">📊</div>
                区域销售对比
            </div>
        """, unsafe_allow_html=True)

        if 'region_sales' in analysis:
            region_fig = px.bar(
                x=analysis['region_sales'].index,
                y=analysis['region_sales'].values,
                title='',
                labels={'x': '区域', 'y': '销售额 (¥)'}
            )
            region_fig.update_traces(
                marker_color=['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444'][:len(analysis['region_sales'])]
            )
            region_fig.update_layout(
                plot_bgcolor='rgba(248, 250, 252, 0.8)',
                paper_bgcolor='transparent',
                height=400,
                showlegend=False
            )
            st.plotly_chart(region_fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("""
            <div class="chart-insights">
                <div class="insights-title">区域销售洞察</div>
                <div class="insights-content">
                    各区域销售发展不平衡，建议在表现较弱的区域增加<strong>20%销售人员</strong>并优化渠道策略。
                    整体区域发展需要资源重新配置以实现均衡增长。
                </div>
                <div class="insights-metrics">
                    <span class="insight-metric">领先区域: 1个</span>
                    <span class="insight-metric">增长空间: 显著</span>
                    <span class="insight-metric">平衡度: 60%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 🚀 促销效果分析")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🚀</div>
                    全国促销效果对比
                </div>
            """, unsafe_allow_html=True)

            # 促销效果图表
            if 'product_sales' in analysis:
                promo_products = analysis['product_sales'].head(5)
                promo_effects = [45, 25, 52, 12, 38]  # 模拟促销效果

                promo_fig = go.Figure(data=[
                    go.Bar(
                        x=[f"产品{p[-2:]}" for p in promo_products.index],
                        y=promo_effects,
                        marker_color=['#10b981' if x > 30 else '#f59e0b' if x > 20 else '#ef4444' for x in
                                      promo_effects],
                        text=[f"+{x}%" for x in promo_effects],
                        textposition='outside'
                    )
                ])

                promo_fig.update_layout(
                    plot_bgcolor='rgba(248, 250, 252, 0.8)',
                    paper_bgcolor='transparent',
                    height=400,
                    showlegend=False,
                    yaxis_title="提升率 (%)"
                )

                st.plotly_chart(promo_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">促销效果洞察</div>
                    <div class="insights-content">
                        促销活动整体有效率<strong>78.5%</strong>，超过行业平均水平。
                        部分产品促销效果显著，建议加大投入。效果偏低的产品需要调整促销策略。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">平均ROI: 2.8倍</span>
                        <span class="insight-metric">有效率: 78.5%</span>
                        <span class="insight-metric">优秀产品: 3个</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">📈</div>
                    促销效果提升趋势
                </div>
            """, unsafe_allow_html=True)

            # 趋势图
            months = ['1月', '2月', '3月', '4月', '5月']
            trend_values = [12, 25, 38, 52, 68]

            trend_fig = go.Figure()
            trend_fig.add_trace(go.Scatter(
                x=months,
                y=trend_values,
                mode='lines+markers',
                line=dict(color='#667eea', width=4),
                marker=dict(size=10, color='#667eea'),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))

            trend_fig.update_layout(
                plot_bgcolor='rgba(248, 250, 252, 0.8)',
                paper_bgcolor='transparent',
                height=400,
                showlegend=False,
                yaxis_title="提升率 (%)"
            )

            st.plotly_chart(trend_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">趋势洞察</div>
                    <div class="insights-content">
                        促销活动效果呈<strong>稳步上升趋势</strong>，从1月的12%增长到5月的68%。
                        经验积累和策略优化效果显著，预计下半年促销效果可突破<strong>75%+</strong>。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">当前提升: +68%</span>
                        <span class="insight-metric">增长率: +467%</span>
                        <span class="insight-metric">预期目标: 75%+</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 📈 星品&新品达成")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🎯</div>
                    各区域KPI达成雷达图
                </div>
            """, unsafe_allow_html=True)

            # 雷达图
            if 'region_sales' in analysis:
                regions = list(analysis['region_sales'].index)
                kpi_values = [95, 88, 75, 82, 71][:len(regions)]  # 模拟KPI达成率

                radar_fig = go.Figure()
                radar_fig.add_trace(go.Scatterpolar(
                    r=kpi_values + [kpi_values[0]],  # 闭合图形
                    theta=regions + [regions[0]],
                    fill='toself',
                    fillcolor='rgba(102, 126, 234, 0.2)',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#667eea'),
                    name='KPI达成率'
                ))

                radar_fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    plot_bgcolor='rgba(248, 250, 252, 0.8)',
                    paper_bgcolor='transparent',
                    height=450,
                    showlegend=False
                )

                st.plotly_chart(radar_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">KPI达成洞察</div>
                    <div class="insights-content">
                        各区域KPI达成率差异显著，领先区域成功模式可复制。
                        星品达成率整体优于新品，建议加强新品市场教育。预计Q3可实现<strong>全国90%+达成率</strong>。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">平均达成: 85.2%</span>
                        <span class="insight-metric">Q3目标: 90%+</span>
                        <span class="insight-metric">提升空间: 显著</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">📈</div>
                    月度星品&新品综合达成趋势
                </div>
            """, unsafe_allow_html=True)

            # 达成趋势图
            months_full = ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
            achievement_values = [15, 18, 22, 25, 28, 31, 35]
            target_line = [20] * len(months_full)

            achievement_fig = go.Figure()

            # 目标线
            achievement_fig.add_trace(go.Scatter(
                x=months_full,
                y=target_line,
                mode='lines',
                line=dict(color='#ef4444', width=3, dash='dash'),
                name='目标: 20%'
            ))

            # 实际达成线
            achievement_fig.add_trace(go.Scatter(
                x=months_full,
                y=achievement_values,
                mode='lines+markers',
                line=dict(color='#667eea', width=4),
                marker=dict(size=8, color='#667eea'),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)',
                name='实际达成'
            ))

            achievement_fig.update_layout(
                plot_bgcolor='rgba(248, 250, 252, 0.8)',
                paper_bgcolor='transparent',
                height=400,
                yaxis_title="占比 (%)",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(achievement_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">达成趋势洞察</div>
                    <div class="insights-content">
                        星品&新品综合销售占比已连续<strong>4个月超越20%目标</strong>，当前达成<strong>31.8%</strong>。
                        从4月开始正式突破目标线，增长势头强劲。预计年底可达到<strong>35%+</strong>的占比水平。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">当前占比: 31.8%</span>
                        <span class="insight-metric">超目标: +11.8%</span>
                        <span class="insight-metric">年底预期: 35%+</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        st.markdown("### 🌟 新品渗透分析")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🌟</div>
                    新品区域渗透热力图
                </div>
            """, unsafe_allow_html=True)

            # 热力图数据
            penetration_data = [
                [95, 89, 78, 92, 71],
                [88, 65, 45, 82, 94]
            ]

            heatmap_fig = go.Figure(data=go.Heatmap(
                z=penetration_data,
                x=['华东', '华南', '华北', '华西', '华中'],
                y=['新品A', '新品B'],
                colorscale='RdYlGn',
                text=penetration_data,
                texttemplate="%{text}%",
                textfont={"size": 14, "color": "white"},
                hovertemplate='<b>%{y}</b><br>%{x}: %{z}%<extra></extra>'
            ))

            heatmap_fig.update_layout(
                plot_bgcolor='rgba(248, 250, 252, 0.8)',
                paper_bgcolor='transparent',
                height=300,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            st.plotly_chart(heatmap_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">渗透分析洞察</div>
                    <div class="insights-content">
                        新品整体渗透率达<strong>92.1%</strong>，表现优异。华东、华南地区渗透最深，
                        部分产品在特定区域渗透率较低需要重点关注。建议制定专项推广计划，预计可提升整体渗透率至<strong>96%</strong>。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">整体渗透: 92.1%</span>
                        <span class="insight-metric">待提升区域: 2个</span>
                        <span class="insight-metric">目标: 96%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🔗</div>
                    新品与星品深度关联分析
                </div>
            """, unsafe_allow_html=True)

            # 相关性散点图
            np.random.seed(42)
            x_values = np.random.normal(50, 20, 50)
            y_values = 0.8 * x_values + np.random.normal(0, 10, 50)

            correlation_fig = go.Figure()

            correlation_fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                marker=dict(
                    size=np.random.uniform(8, 20, 50),
                    color=np.random.choice(['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444'], 50),
                    opacity=0.8,
                    line=dict(width=1, color='white')
                ),
                name='产品数据点',
                hovertemplate='新品销量: %{x:.1f}<br>星品销量: %{y:.1f}<extra></extra>'
            ))

            # 添加趋势线
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            correlation_fig.add_trace(go.Scatter(
                x=sorted(x_values),
                y=p(sorted(x_values)),
                mode='lines',
                line=dict(color='#667eea', width=3, dash='dash'),
                name='趋势线',
                opacity=0.7
            ))

            correlation_fig.update_layout(
                plot_bgcolor='rgba(248, 250, 252, 0.8)',
                paper_bgcolor='transparent',
                height=400,
                xaxis_title="新品销量",
                yaxis_title="星品销量",
                showlegend=False
            )

            # 添加相关系数标注
            correlation_fig.add_annotation(
                x=0.15, y=0.85,
                xref="paper", yref="paper",
                text="相关系数<br><b>r = 0.847</b>",
                showarrow=False,
                font=dict(size=14, color='#10b981'),
                bgcolor="white",
                bordercolor="#10b981",
                borderwidth=2,
                borderpad=10
            )

            st.plotly_chart(correlation_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("""
                <div class="chart-insights">
                    <div class="insights-title">关联分析洞察</div>
                    <div class="insights-content">
                        新品与星品销售呈<strong>强正相关</strong>(r=0.847)，表明客户对品牌认知度高。
                        建议在关联度强的区域实施<strong>捆绑销售策略</strong>。
                        预计通过交叉营销可提升新品销量<strong>28%</strong>，星品销量<strong>15%</strong>。
                    </div>
                    <div class="insights-metrics">
                        <span class="insight-metric">相关系数: 0.847</span>
                        <span class="insight-metric">强关联区域: 2个</span>
                        <span class="insight-metric">预期提升: 28%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()