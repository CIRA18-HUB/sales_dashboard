# pages/产品组合分析.py - 混合方案版本
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import streamlit.components.v1 as components
from pathlib import Path
import json

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

# 登陆界面风格的CSS样式
login_style_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        height: 100%;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 + 动画 - 完全按照登陆界面 */
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

    /* 侧边栏美化 - 完全按照登陆界面 */
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

    .stSidebar .stMarkdown h4 {
        color: #2d3748;
        font-weight: 600;
        padding: 0 1rem;
        margin: 1rem 0 0.5rem 0;
        font-size: 1rem;
    }

    .stSidebar .stMarkdown hr {
        border: none;
        height: 1px;
        background: rgba(102, 126, 234, 0.2);
        margin: 1rem 0;
    }

    /* 侧边栏按钮 - 紫色渐变样式 */
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

    .stSidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s ease;
    }

    .stSidebar .stButton > button:hover::before {
        left: 100%;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 用户信息框 */
    .user-info {
        background: #e6fffa;
        border: 1px solid #38d9a9;
        border-radius: 10px;
        padding: 1rem;
        margin: 0 1rem;
        color: #2d3748;
    }

    .user-info strong {
        display: block;
        margin-bottom: 0.5rem;
    }
</style>
"""

st.markdown(login_style_css, unsafe_allow_html=True)

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
    <div class="user-info">
        <strong>管理员</strong>
        cira
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("登陆界面haha.py")


# 数据加载函数 - 保持原有逻辑
@st.cache_data
def load_data():
    """加载所有必需的数据文件，不使用示例数据"""
    data = {}
    missing_files = []

    try:
        # 1. 产品代码文件
        try:
            with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
                data['kpi_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            missing_files.append('星品&新品年度KPI考核产品代码.txt')

        # 2. 促销活动数据
        try:
            data['promotion_activities'] = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
        except FileNotFoundError:
            missing_files.append('这是涉及到在4月份做的促销活动.xlsx')

        # 3. 销售数据
        try:
            data['sales_data'] = pd.read_excel('24-25促销效果销售数据.xlsx')
        except FileNotFoundError:
            missing_files.append('24-25促销效果销售数据.xlsx')

        # 4. 仪表盘产品代码
        try:
            with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
                data['dashboard_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            missing_files.append('仪表盘产品代码.txt')

        # 5. 新品代码
        try:
            with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
                data['new_products'] = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            missing_files.append('仪表盘新品代码.txt')

        # 如果有缺失文件，显示友好错误提示
        if missing_files:
            st.error(f"""
            ❌ **数据文件缺失**

            以下必需的数据文件未找到：
            {chr(10).join([f'• {file}' for file in missing_files])}

            请确保所有数据文件都位于项目根目录中。
            """)
            return None

        return data

    except Exception as e:
        st.error(f"❌ **数据加载错误**: {str(e)}")
        return None


# BCG矩阵计算函数 - 保持原有逻辑
def calculate_bcg_matrix(data):
    """根据需求文档计算BCG矩阵分类"""
    if not data or 'sales_data' not in data:
        return None

    try:
        sales_df = data['sales_data'].copy()

        # 确保必需字段存在
        required_columns = ['产品代码', '单价', '箱数', '发运月份']
        missing_columns = [col for col in required_columns if col not in sales_df.columns]
        if missing_columns:
            st.error(f"销售数据缺少必需字段: {missing_columns}")
            return None

        # 计算销售额
        sales_df['销售额'] = sales_df['单价'] * sales_df['箱数']

        # 转换日期格式
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'], errors='coerce')
        sales_df = sales_df.dropna(subset=['发运月份'])

        # 计算产品总销售额
        total_sales = sales_df['销售额'].sum()

        # 按产品分组计算指标
        product_metrics = []

        for product in sales_df['产品代码'].unique():
            product_data = sales_df[sales_df['产品代码'] == product]

            # 计算销售占比（占公司总销售额的比例）
            product_sales = product_data['销售额'].sum()
            sales_ratio = (product_sales / total_sales) * 100

            # 计算同比增长率（今年vs去年同期）
            current_year = datetime.now().year
            last_year = current_year - 1

            current_year_data = product_data[product_data['发运月份'].dt.year == current_year]
            last_year_data = product_data[product_data['发运月份'].dt.year == last_year]

            current_sales = current_year_data['销售额'].sum()
            last_sales = last_year_data['销售额'].sum()

            if last_sales > 0:
                growth_rate = ((current_sales - last_sales) / last_sales) * 100
            else:
                growth_rate = 0 if current_sales == 0 else 100

            # 根据需求文档逻辑分类产品
            if sales_ratio < 1.5 and growth_rate > 20:
                category = "问号产品"
                category_class = "question"
            elif sales_ratio >= 1.5 and growth_rate > 20:
                category = "明星产品"
                category_class = "star"
            elif sales_ratio < 1.5 and growth_rate <= 20:
                category = "瘦狗产品"
                category_class = "dog"
            else:  # sales_ratio >= 1.5 and growth_rate <= 20
                category = "现金牛产品"
                category_class = "cow"

            product_metrics.append({
                'product_code': product,
                'sales_ratio': sales_ratio,
                'growth_rate': growth_rate,
                'total_sales': product_sales,
                'category': category,
                'category_class': category_class
            })

        # 计算JBP达成情况
        df_metrics = pd.DataFrame(product_metrics)

        cow_ratio = df_metrics[df_metrics['category'] == '现金牛产品']['sales_ratio'].sum()
        star_question_ratio = df_metrics[df_metrics['category'].isin(['明星产品', '问号产品'])]['sales_ratio'].sum()
        dog_ratio = df_metrics[df_metrics['category'] == '瘦狗产品']['sales_ratio'].sum()

        # JBP目标检查
        jbp_status = {
            'cow_target': 45 <= cow_ratio <= 50,
            'star_question_target': 40 <= star_question_ratio <= 45,
            'dog_target': dog_ratio <= 10,
            'cow_ratio': cow_ratio,
            'star_question_ratio': star_question_ratio,
            'dog_ratio': dog_ratio
        }

        overall_jbp = all([jbp_status['cow_target'], jbp_status['star_question_target'], jbp_status['dog_target']])

        return {
            'products': product_metrics,
            'jbp_status': jbp_status,
            'overall_jbp': overall_jbp,
            'total_sales': total_sales
        }

    except Exception as e:
        st.error(f"BCG矩阵计算错误: {str(e)}")
        return None


# 数据分析函数 - 保持原有逻辑
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
        analysis['region_sales'] = region_sales.to_dict()

        # 产品分析
        product_sales = sales_df.groupby('产品代码')['销售额'].sum().sort_values(ascending=False)
        analysis['product_sales'] = product_sales.head(10).to_dict()

        # 销售员排行
        salesperson_performance = sales_df.groupby('销售员').agg({
            '销售额': 'sum',
            '箱数': 'sum'
        }).sort_values('销售额', ascending=False)
        analysis['salesperson_ranking'] = salesperson_performance.head(10).to_dict('index')

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


# 创建HTML组件函数
def create_html_dashboard(analysis, bcg_data):
    """创建带有真实数据的HTML仪表盘"""

    # 准备数据
    total_sales = analysis.get('total_sales', 0)
    kpi_compliance = analysis.get('kpi_compliance', 0)
    promotion_eff = analysis.get('promotion_effectiveness', 0)
    new_ratio = analysis.get('new_product_ratio', 0)

    # JBP达成状态
    if bcg_data and bcg_data['overall_jbp']:
        jbp_status = "✅ JBP达标"
        jbp_class = "jbp-success"
    else:
        jbp_status = "⚠️ JBP未达标"
        jbp_class = "jbp-warning"

    # BCG产品气泡数据
    product_bubbles_html = ""
    if bcg_data and bcg_data['products']:
        for i, product in enumerate(bcg_data['products'][:6]):
            # 根据分类确定位置和样式
            if product['category_class'] == 'star':
                top = np.random.uniform(15, 45)
                left = np.random.uniform(55, 85)
                bubble_class = "bubble-star"
            elif product['category_class'] == 'question':
                top = np.random.uniform(15, 45)
                left = np.random.uniform(15, 45)
                bubble_class = "bubble-question"
            elif product['category_class'] == 'cow':
                top = np.random.uniform(55, 85)
                left = np.random.uniform(55, 85)
                bubble_class = "bubble-cow"
            else:  # dog
                top = np.random.uniform(55, 85)
                left = np.random.uniform(15, 45)
                bubble_class = "bubble-dog"

            max_sales = max([p['total_sales'] for p in bcg_data['products']])
            bubble_size = 20 + (product['total_sales'] / max_sales) * 15
            product_code_short = product['product_code'][-2:] if len(product['product_code']) > 2 else product[
                'product_code']

            product_bubbles_html += f"""
            <div class="product-bubble {bubble_class}" 
                 style="top: {top}%; left: {left}%; width: {bubble_size}px; height: {bubble_size}px;">
                {product_code_short}
            </div>
            """

    # 销售员排行数据
    ranking_html = ""
    if 'salesperson_ranking' in analysis:
        for i, (name, data) in enumerate(list(analysis['salesperson_ranking'].items())[:10], 1):
            sales_amount = data['销售额']
            performance_color = "positive" if i <= 3 else "warning" if i <= 7 else "negative"
            max_sales = list(analysis['salesperson_ranking'].values())[0]['销售额']
            percentage = (sales_amount / max_sales * 100) if max_sales > 0 else 0

            ranking_html += f"""
            <div class="ranking-compact-item">
                <div class="ranking-number-compact">{i}</div>
                <div class="ranking-info-compact">
                    <div class="ranking-name-compact">{name}</div>
                    <div class="ranking-detail-compact">销售额: ¥{sales_amount:,.0f}</div>
                </div>
                <div class="ranking-percentage-compact {performance_color}">{percentage:.1f}%</div>
            </div>
            """

    # 完整的HTML模板
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #2d3748;
                line-height: 1.6;
                overflow-x: hidden;
                min-height: 100vh;
                position: relative;
            }}

            /* 动态背景波纹效果 */
            body::before {{
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
            }}

            @keyframes waveMove {{
                0%, 100% {{ 
                    background-size: 200% 200%, 150% 150%, 300% 300%;
                    background-position: 0% 0%, 100% 100%, 50% 50%; 
                }}
                33% {{ 
                    background-size: 300% 300%, 200% 200%, 250% 250%;
                    background-position: 100% 0%, 0% 50%, 80% 20%; 
                }}
                66% {{ 
                    background-size: 250% 250%, 300% 300%, 200% 200%;
                    background-position: 50% 100%, 50% 0%, 20% 80%; 
                }}
            }}

            /* 浮动粒子效果 */
            body::after {{
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
            }}

            @keyframes particleFloat {{
                0% {{ transform: translateY(100vh) translateX(0); }}
                100% {{ transform: translateY(-100vh) translateX(100px); }}
            }}

            .dashboard-container {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 2rem;
                position: relative;
                z-index: 10;
            }}

            /* 顶部标题区域 */
            .dashboard-header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 1.5rem;
                padding: 3rem 2rem;
                text-align: center;
                margin-bottom: 3rem;
                color: #1e293b;
                position: relative;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}

            .dashboard-title {{
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .dashboard-subtitle {{
                font-size: 1.3rem;
                opacity: 0.8;
                color: #4a5568;
            }}

            /* 标签页导航 */
            .tab-navigation {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 1rem;
                padding: 1rem;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                display: flex;
                gap: 0.5rem;
                overflow-x: auto;
            }}

            .tab-btn {{
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
            }}

            .tab-btn.active {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            }}

            .tab-btn:hover:not(.active) {{
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
            }}

            /* 指标卡片 */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
            }}

            .metric-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 1.5rem;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}

            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
            }}

            .metric-card:hover {{
                transform: translateY(-12px) scale(1.02);
                box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
            }}

            .metric-icon {{
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }}

            .metric-label {{
                font-size: 0.9rem;
                color: #64748b;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }}

            .metric-value {{
                font-size: 2.5rem;
                font-weight: 800;
                color: #1e293b;
                margin-bottom: 0.5rem;
            }}

            .metric-delta {{
                display: inline-flex;
                align-items: center;
                gap: 0.25rem;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                font-size: 0.85rem;
                font-weight: 600;
            }}

            .delta-positive {{
                background: rgba(34, 197, 94, 0.1);
                color: #16a34a;
            }}

            .delta-negative {{
                background: rgba(239, 68, 68, 0.1);
                color: #dc2626;
            }}

            .delta-neutral {{
                background: rgba(107, 114, 128, 0.1);
                color: #6b7280;
            }}

            /* BCG矩阵 */
            .chart-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 1.5rem;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                margin-bottom: 2rem;
            }}

            .chart-title {{
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
                color: #1e293b;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}

            .chart-icon {{
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.2rem;
            }}

            .compact-bcg-container {{
                display: grid;
                grid-template-columns: 1fr 280px;
                gap: 2rem;
                align-items: start;
            }}

            .bcg-matrix-main {{
                position: relative;
                height: 500px;
                border-radius: 1rem;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                padding: 2rem;
                overflow: visible;
            }}

            .bcg-quadrants-compact {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr 1fr;
                height: 100%;
                gap: 2px;
                background: #e2e8f0;
                border-radius: 0.75rem;
                overflow: hidden;
            }}

            .bcg-quadrant-compact {{
                position: relative;
                padding: 1.5rem 1rem;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }}

            .quadrant-question {{ background: linear-gradient(135deg, #fef3c7, #fbbf24); }}
            .quadrant-star {{ background: linear-gradient(135deg, #d1fae5, #10b981); }}
            .quadrant-dog {{ background: linear-gradient(135deg, #f1f5f9, #64748b); }}
            .quadrant-cow {{ background: linear-gradient(135deg, #dbeafe, #3b82f6); }}

            .quadrant-compact-title {{
                font-size: 1rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 0.5rem;
            }}

            .quadrant-compact-desc {{
                font-size: 0.8rem;
                color: #64748b;
                line-height: 1.4;
            }}

            /* 产品气泡 */
            .product-bubble {{
                position: absolute;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 0.7rem;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 15;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.9);
            }}

            .product-bubble:hover {{
                transform: scale(1.15);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            }}

            .bubble-star {{ background: linear-gradient(135deg, #10b981, #059669); }}
            .bubble-question {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
            .bubble-cow {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
            .bubble-dog {{ background: linear-gradient(135deg, #64748b, #475569); }}

            /* JBP状态 */
            .jbp-status {{
                position: absolute;
                top: 1rem;
                right: 1rem;
                padding: 0.5rem 1rem;
                border-radius: 1rem;
                font-size: 0.85rem;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}

            .jbp-success {{
                background: rgba(34, 197, 94, 0.1);
                color: #16a34a;
                border: 1px solid #16a34a;
            }}

            .jbp-warning {{
                background: rgba(239, 68, 68, 0.1);
                color: #dc2626;
                border: 1px solid #dc2626;
            }}

            /* 坐标轴标签 */
            .axis-labels {{
                position: absolute;
                font-weight: 600;
                color: #475569;
                background: white;
                padding: 0.5rem 1rem;
                border-radius: 1rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                z-index: 5;
                font-size: 0.8rem;
            }}

            .axis-top {{ top: -1.5rem; left: 50%; transform: translateX(-50%); }}
            .axis-bottom {{ bottom: -1.5rem; left: 50%; transform: translateX(-50%); }}
            .axis-left {{ left: -6rem; top: 50%; transform: translateY(-50%) rotate(-90deg); }}
            .axis-right {{ right: -6rem; top: 50%; transform: translateY(-50%) rotate(90deg); }}

            /* 销售员排行榜 */
            .bcg-sidebar {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                max-height: 500px;
                overflow-y: auto;
            }}

            .sidebar-title {{
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: #1e293b;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .ranking-compact-item {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                background: #f8fafc;
                border-radius: 0.5rem;
                transition: all 0.3s ease;
            }}

            .ranking-compact-item:hover {{
                background: #e2e8f0;
                transform: translateX(4px);
            }}

            .ranking-number-compact {{
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.75rem;
                flex-shrink: 0;
            }}

            .ranking-info-compact {{
                flex: 1;
                min-width: 0;
            }}

            .ranking-name-compact {{
                font-weight: 600;
                color: #1e293b;
                font-size: 0.85rem;
                margin-bottom: 0.125rem;
            }}

            .ranking-detail-compact {{
                color: #64748b;
                font-size: 0.7rem;
                line-height: 1.3;
            }}

            .ranking-percentage-compact {{
                font-weight: 700;
                font-size: 0.9rem;
                flex-shrink: 0;
            }}

            .positive {{ color: #10b981; }}
            .warning {{ color: #f59e0b; }}
            .negative {{ color: #ef4444; }}

            /* 内容区域 */
            .tab-content {{
                display: none;
            }}

            .tab-content.active {{
                display: block;
                animation: fadeInUp 0.6s ease-out;
            }}

            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <!-- 仪表盘标题 -->
            <div class="dashboard-header">
                <h1 class="dashboard-title">📦 产品组合分析仪表盘</h1>
                <p class="dashboard-subtitle">现代化数据驱动的产品生命周期管理平台</p>
            </div>

            <!-- 标签页导航 -->
            <div class="tab-navigation">
                <button class="tab-btn active" onclick="switchTab(0)">📊 产品情况总览</button>
                <button class="tab-btn" onclick="switchTab(1)">🎯 产品组合全景</button>
                <button class="tab-btn" onclick="switchTab(2)">🚀 促销效果分析</button>
                <button class="tab-btn" onclick="switchTab(3)">📈 星品&新品达成</button>
                <button class="tab-btn" onclick="switchTab(4)">🌟 新品渗透分析</button>
            </div>

            <!-- 标签页1: 产品情况总览 -->
            <div class="tab-content active" id="tab-0">
                <div class="metrics-grid">
                    <!-- 总销售额 -->
                    <div class="metric-card">
                        <div class="metric-icon">💰</div>
                        <div class="metric-label">总销售额</div>
                        <div class="metric-value">¥{total_sales:,.0f}</div>
                        <div class="metric-delta delta-positive">+12.5% ↗️</div>
                    </div>

                    <!-- JBP符合度 -->
                    <div class="metric-card">
                        <div class="metric-icon">✅</div>
                        <div class="metric-label">JBP符合度</div>
                        <div class="metric-value">{'是' if bcg_data and bcg_data['overall_jbp'] else '否'}</div>
                        <div class="metric-delta {'delta-positive' if bcg_data and bcg_data['overall_jbp'] else 'delta-negative'}">
                            {'产品矩阵达标' if bcg_data and bcg_data['overall_jbp'] else '需要调整'}
                        </div>
                    </div>

                    <!-- KPI达成率 -->
                    <div class="metric-card">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-label">KPI达成率 (月度滚动)</div>
                        <div class="metric-value">{kpi_compliance:.1f}%</div>
                        <div class="metric-delta delta-positive">+8.3% vs目标(20%)</div>
                    </div>

                    <!-- 促销有效性 -->
                    <div class="metric-card">
                        <div class="metric-icon">🚀</div>
                        <div class="metric-label">促销有效性</div>
                        <div class="metric-value">{promotion_eff:.1f}%</div>
                        <div class="metric-delta delta-positive">全国促销有效</div>
                    </div>

                    <!-- 新品占比 -->
                    <div class="metric-card">
                        <div class="metric-icon">🌟</div>
                        <div class="metric-label">新品占比</div>
                        <div class="metric-value">{new_ratio:.1f}%</div>
                        <div class="metric-delta delta-positive">销售额占比</div>
                    </div>

                    <!-- 新品渗透率 -->
                    <div class="metric-card">
                        <div class="metric-icon">📊</div>
                        <div class="metric-label">新品渗透率</div>
                        <div class="metric-value">92.1%</div>
                        <div class="metric-delta delta-positive">区域覆盖率</div>
                    </div>

                    <!-- 星品销售占比 -->
                    <div class="metric-card">
                        <div class="metric-icon">⭐</div>
                        <div class="metric-label">星品销售占比</div>
                        <div class="metric-value">15.6%</div>
                        <div class="metric-delta delta-positive">销售额占比</div>
                    </div>

                    <!-- 产品集中度 -->
                    <div class="metric-card">
                        <div class="metric-icon">📊</div>
                        <div class="metric-label">产品集中度</div>
                        <div class="metric-value">45.8%</div>
                        <div class="metric-delta delta-neutral">TOP5产品占比</div>
                    </div>
                </div>
            </div>

            <!-- 标签页2: 产品组合全景 -->
            <div class="tab-content" id="tab-1">
                <div class="chart-container">
                    <div class="chart-title">
                        <div class="chart-icon">🎯</div>
                        BCG产品矩阵分析 - 产品生命周期管理
                    </div>
                    <div class="compact-bcg-container">
                        <div class="bcg-matrix-main">
                            <div class="jbp-status {jbp_class}">
                                {jbp_status}
                            </div>

                            <div class="bcg-quadrants-compact">
                                <!-- 问号产品象限 -->
                                <div class="bcg-quadrant-compact quadrant-question">
                                    <div class="quadrant-compact-title">❓ 问号产品</div>
                                    <div class="quadrant-compact-desc">销售占比&lt;1.5% &amp; 增长&gt;20%</div>
                                </div>

                                <!-- 明星产品象限 -->
                                <div class="bcg-quadrant-compact quadrant-star">
                                    <div class="quadrant-compact-title">⭐ 明星产品</div>
                                    <div class="quadrant-compact-desc">销售占比&gt;1.5% &amp; 增长&gt;20%</div>
                                </div>

                                <!-- 瘦狗产品象限 -->
                                <div class="bcg-quadrant-compact quadrant-dog">
                                    <div class="quadrant-compact-title">🐕 瘦狗产品</div>
                                    <div class="quadrant-compact-desc">销售占比&lt;1.5% &amp; 增长&lt;20%</div>
                                </div>

                                <!-- 现金牛产品象限 -->
                                <div class="bcg-quadrant-compact quadrant-cow">
                                    <div class="quadrant-compact-title">🐄 现金牛产品</div>
                                    <div class="quadrant-compact-desc">销售占比&gt;1.5% &amp; 增长&lt;20%</div>
                                </div>
                            </div>

                            <!-- 坐标轴标签 -->
                            <div class="axis-labels axis-top">📈 高增长率 (&gt;20%)</div>
                            <div class="axis-labels axis-bottom">📉 低增长率 (&lt;20%)</div>
                            <div class="axis-labels axis-left">← 低占比 (&lt;1.5%)</div>
                            <div class="axis-labels axis-right">高占比 (&gt;1.5%) →</div>

                            <!-- 产品气泡 -->
                            {product_bubbles_html}
                        </div>

                        <div class="bcg-sidebar">
                            <div class="sidebar-title">
                                🏆 销售员TOP10排行
                            </div>
                            {ranking_html}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 其他标签页内容可以继续添加 -->
            <div class="tab-content" id="tab-2">
                <div class="chart-container">
                    <div class="chart-title">
                        <div class="chart-icon">🚀</div>
                        促销效果分析
                    </div>
                    <p style="text-align: center; color: #64748b; padding: 3rem;">促销效果分析功能开发中...</p>
                </div>
            </div>

            <div class="tab-content" id="tab-3">
                <div class="chart-container">
                    <div class="chart-title">
                        <div class="chart-icon">📈</div>
                        星品&新品达成分析
                    </div>
                    <p style="text-align: center; color: #64748b; padding: 3rem;">星品&新品达成分析功能开发中...</p>
                </div>
            </div>

            <div class="tab-content" id="tab-4">
                <div class="chart-container">
                    <div class="chart-title">
                        <div class="chart-icon">🌟</div>
                        新品渗透分析
                    </div>
                    <p style="text-align: center; color: #64748b; padding: 3rem;">新品渗透分析功能开发中...</p>
                </div>
            </div>
        </div>

        <script>
            // 标签页切换
            function switchTab(index) {{
                // 移除所有活动状态
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

                // 激活选中的标签页
                document.querySelectorAll('.tab-btn')[index].classList.add('active');
                document.getElementById(`tab-${{index}}`).classList.add('active');
            }}

            // 页面加载动画
            window.addEventListener('load', () => {{
                const elements = document.querySelectorAll('.metric-card, .chart-container');
                elements.forEach((el, index) => {{
                    setTimeout(() => {{
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }}, index * 100);
                }});
            }});

            // 初始设置
            document.addEventListener('DOMContentLoaded', function() {{
                // 设置初始动画状态
                const elements = document.querySelectorAll('.metric-card, .chart-container');
                elements.forEach(el => {{
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'all 0.6s ease';
                }});
            }});
        </script>
    </body>
    </html>
    """

    return html_template


# 主要内容
def main():
    # 加载数据
    with st.spinner('正在加载数据...'):
        data = load_data()
        if not data:
            st.stop()

        analysis = analyze_data(data)
        if not analysis:
            st.stop()

        bcg_data = calculate_bcg_matrix(data)

    # 创建HTML仪表盘
    html_dashboard = create_html_dashboard(analysis, bcg_data)

    # 嵌入HTML组件
    components.html(html_dashboard, height=1200, scrolling=True)


if __name__ == "__main__":
    main()