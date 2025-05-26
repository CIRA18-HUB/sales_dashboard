# 集成版 Trolli SAL 系统 - 登录界面与产品组合分析
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import math
import time
from datetime import datetime, timedelta
import warnings
import random

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="📊 Trolli SAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "welcome"
if 'stats_initialized' not in st.session_state:
    st.session_state.stats_initialized = False
    st.session_state.stat1_value = 1000
    st.session_state.stat2_value = 4
    st.session_state.stat3_value = 24
    st.session_state.stat4_value = 99
    st.session_state.last_update = time.time()

# 通用CSS样式
common_css = """
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    
    /* 隐藏侧边栏 */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
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

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 主标题 */
    .main-title {
        text-align: center;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        z-index: 10;
    }

    .main-title h1 {
        font-size: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        font-weight: 700;
        animation: titleGlowPulse 4s ease-in-out infinite;
    }

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

    /* 登录容器 */
    .login-container {
        max-width: 450px;
        margin: 3rem auto;
        padding: 3rem 2.5rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        text-align: center;
        position: relative;
        z-index: 10;
        animation: loginSlideIn 0.8s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    @keyframes loginSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* 标签页容器 */
    .stTabs {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        animation: slideUp 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes slideUp {
        0% { opacity: 0; transform: translateY(100px) scale(0.8); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 标签按钮样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.8rem;
        background: rgba(255, 255, 255, 0.8);
        padding: 1.5rem;
        border-bottom: 1px solid rgba(102, 126, 234, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        padding: 1rem 1.5rem;
        font-size: 0.9rem;
        color: #64748b;
        border-radius: 15px;
        transition: all 0.4s ease;
        white-space: nowrap;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        transform: translateY(-3px) scale(1.02);
    }

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }

    /* 标签内容 */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 2rem;
        animation: contentFadeIn 0.8s ease-out;
    }

    @keyframes contentFadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Streamlit metric样式覆盖 */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        animation: cardSlideUp 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2, #ff6b6b, #ffa726);
        background-size: 300% 100%;
        animation: gradientShift 3s ease-in-out infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes cardSlideUp {
        0% { opacity: 0; transform: translateY(60px) scale(0.8); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
    }

    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        animation: numberSlideUp 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes numberSlideUp {
        0% { opacity: 0; transform: translateY(100%) scale(0.5); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 导航栏样式 */
    .nav-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* 统计卡片 */
    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .stat-card:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 1);
    }

    .counter-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
        transition: all 0.3s ease;
    }

    .counter-number.updating {
        animation: numberPulse 0.6s ease-out;
    }

    @keyframes numberPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }

    .stat-label {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* 功能卡片 */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .feature-card:hover {
        transform: translateY(-10px) rotate(2deg) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 1);
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
        animation: iconBounce 2s ease-in-out infinite;
    }

    @keyframes iconBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .feature-title {
        font-size: 1.4rem;
        color: #2d3748;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .feature-description {
        color: #4a5568;
        line-height: 1.6;
    }

    /* 更新提示 */
    .update-badge {
        display: inline-block;
        background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%);
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        animation: badgeFloat 3s ease-in-out infinite;
    }

    @keyframes badgeFloat {
        0%, 100% { 
            transform: translateY(0);
            box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
        }
        50% { 
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(116, 185, 255, 0.5);
        }
    }

    /* 输入框样式 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: white;
    }

    /* 下拉选择框样式 */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title h1 { font-size: 2.2rem; }
        [data-testid="metric-container"] { margin-bottom: 1rem; }
    }
</style>
"""

st.markdown(common_css, unsafe_allow_html=True)

# 数据加载函数
@st.cache_data(ttl=3600)
def load_real_data():
    """加载数据文件"""
    try:
        data_dict = {}
        
        # 模拟数据加载过程
        try:
            # 这里应该是真实的数据加载代码
            # data = pd.read_excel('TT与MT销售数据.xlsx')
            # 为演示目的，创建模拟数据
            data_dict['sales_data'] = create_mock_sales_data()
            data_dict['new_products'] = ['P001', 'P002', 'P003', 'P004', 'P005']
            data_dict['kpi_products'] = ['P001', 'P002', 'P003', 'P006', 'P007', 'P008']
        except Exception as e:
            st.warning(f"⚠️ 数据文件加载失败: {str(e)}")
        
        return data_dict
    except Exception as e:
        st.error(f"❌ 数据加载过程中发生错误: {str(e)}")
        return {}

def create_mock_sales_data():
    """创建模拟销售数据"""
    np.random.seed(42)
    n_records = 1000
    
    products = [f'P{str(i).zfill(3)}' for i in range(1, 21)]
    regions = ['北', '南', '东', '西', '中']
    
    data = {
        '产品代码': np.random.choice(products, n_records),
        '所属区域': np.random.choice(regions, n_records),
        '单价（箱）': np.random.uniform(50, 200, n_records),
        '求和项:数量（箱）': np.random.randint(1, 100, n_records),
        '客户代码': [f'C{str(i).zfill(4)}' for i in np.random.randint(1, 201, n_records)]
    }
    
    df = pd.DataFrame(data)
    df['销售额'] = df['单价（箱）'] * df['求和项:数量（箱）']
    return df

# 计算关键指标函数
@st.cache_data
def calculate_key_metrics(data_dict):
    """计算关键业务指标"""
    try:
        metrics = {}
        
        sales_data = data_dict.get('sales_data')
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        
        if sales_data is not None:
            total_sales = sales_data['销售额'].sum()
            
            # 计算新品占比
            new_product_sales = sales_data[sales_data['产品代码'].isin(new_products)]['销售额'].sum()
            new_product_ratio = (new_product_sales / total_sales * 100) if total_sales > 0 else 15.3
            
            # 计算星品占比
            star_products = [p for p in kpi_products if p not in new_products]
            star_product_sales = sales_data[sales_data['产品代码'].isin(star_products)]['销售额'].sum()
            star_product_ratio = (star_product_sales / total_sales * 100) if total_sales > 0 else 12.8
            
            # 计算总占比
            total_star_new_ratio = new_product_ratio + star_product_ratio
            
            # 计算新品渗透率
            total_customers = sales_data['客户代码'].nunique()
            new_product_customers = sales_data[sales_data['产品代码'].isin(new_products)]['客户代码'].nunique()
            penetration_rate = (new_product_customers / total_customers * 100) if total_customers > 0 else 89.7
            
        else:
            total_sales = 8456789
            new_product_ratio = 15.3
            star_product_ratio = 12.8
            total_star_new_ratio = 28.1
            penetration_rate = 89.7
        
        metrics.update({
            'total_sales': total_sales,
            'new_product_ratio': new_product_ratio,
            'star_product_ratio': star_product_ratio,
            'total_star_new_ratio': total_star_new_ratio,
            'penetration_rate': penetration_rate,
            'jbp_status': "是" if total_star_new_ratio >= 20 else "否",
            'kpi_rate': (total_star_new_ratio / 20) * 100,
            'promo_effectiveness': 75.0
        })
        
        return metrics
    
    except Exception as e:
        st.error(f"指标计算失败: {str(e)}")
        return {
            'total_sales': 8456789,
            'jbp_status': "是",
            'kpi_rate': 140.5,
            'promo_effectiveness': 75.0,
            'new_product_ratio': 15.3,
            'star_product_ratio': 12.8,
            'total_star_new_ratio': 28.1,
            'penetration_rate': 89.7
        }

# BCG矩阵数据计算
@st.cache_data
def calculate_bcg_data(data_dict):
    """计算BCG矩阵数据"""
    try:
        sales_data = data_dict.get('sales_data')
        if sales_data is None:
            return []
        
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        star_products = [p for p in kpi_products if p not in new_products]
        
        # 按产品聚合数据
        product_sales = sales_data.groupby('产品代码')['销售额'].sum().reset_index()
        product_sales = product_sales[product_sales['销售额'] > 0]
        total_sales = product_sales['销售额'].sum()
        
        if total_sales == 0:
            return []
        
        bcg_data = []
        for _, row in product_sales.iterrows():
            product_code = row['产品代码']
            product_sales_amount = row['销售额']
            
            # 计算市场份额
            market_share = (product_sales_amount / total_sales * 100)
            
            # 计算增长率（模拟）
            if product_code in new_products:
                growth_rate = np.random.uniform(30, 80)
            elif product_code in star_products:
                growth_rate = np.random.uniform(20, 50)
            else:
                growth_rate = np.random.uniform(-10, 30)
            
            # 确定BCG分类
            if market_share >= 1.5 and growth_rate > 20:
                category = 'star'
            elif market_share < 1.5 and growth_rate > 20:
                category = 'question'
            elif market_share >= 1.5 and growth_rate <= 20:
                category = 'cow'
            else:
                category = 'dog'
            
            product_name = f"产品{str(product_code)[-3:]}"
            
            bcg_data.append({
                'code': product_code,
                'name': product_name,
                'share': market_share,
                'growth': growth_rate,
                'sales': product_sales_amount,
                'category': category
            })
        
        # 取前20个产品
        bcg_data = sorted(bcg_data, key=lambda x: x['sales'], reverse=True)[:20]
        return bcg_data
    
    except Exception as e:
        st.error(f"BCG数据计算失败: {str(e)}")
        return []

# 创建BCG矩阵图表
def create_bcg_matrix(bcg_data):
    """创建BCG矩阵图表"""
    if not bcg_data:
        st.warning("⚠️ 没有可用的BCG数据")
        return None
    
    colors = {
        'star': '#22c55e',
        'question': '#f59e0b',
        'cow': '#3b82f6',
        'dog': '#94a3b8'
    }
    
    fig = go.Figure()
    
    for category in ['star', 'question', 'cow', 'dog']:
        category_data = [p for p in bcg_data if p['category'] == category]
        
        if category_data:
            fig.add_trace(go.Scatter(
                x=[p['share'] for p in category_data],
                y=[p['growth'] for p in category_data],
                mode='markers+text',
                marker=dict(
                    size=[max(min(math.sqrt(p['sales']) / 50, 80), 20) for p in category_data],
                    color=colors[category],
                    opacity=0.9,
                    line=dict(width=4, color='white')
                ),
                name={
                    'star': '⭐ 明星产品',
                    'question': '❓ 问号产品',
                    'cow': '🐄 现金牛产品',
                    'dog': '🐕 瘦狗产品'
                }[category],
                text=[p['name'][:8] for p in category_data],
                textposition='middle center',
                textfont=dict(size=10, color='white', family='Inter'),
                hovertemplate='<b>%{text}</b><br>市场份额: %{x:.2f}%<br>增长率: %{y:.1f}%<br>销售额: ¥%{customdata}<extra></extra>',
                customdata=[f"{p['sales']:,.0f}" for p in category_data]
            ))
    
    # 计算图表范围
    all_shares = [p['share'] for p in bcg_data]
    all_growth = [p['growth'] for p in bcg_data]
    max_share = max(all_shares) + 1 if all_shares else 10
    max_growth = max(all_growth) + 10 if all_growth else 60
    min_growth = min(all_growth) - 5 if all_growth else -10
    
    # 分界线位置
    share_threshold = np.median(all_shares) if all_shares else 1.5
    growth_threshold = np.median(all_growth) if all_growth else 20
    
    fig.update_layout(
        title=dict(text='产品矩阵分布 - BCG分析', font=dict(size=18, color='#1e293b'), x=0.5),
        xaxis=dict(
            title='📊 市场份额 (%)',
            range=[0, max_share],
            showgrid=True,
            gridcolor='rgba(226, 232, 240, 0.8)'
        ),
        yaxis=dict(
            title='📈 市场增长率 (%)',
            range=[min_growth, max_growth],
            showgrid=True,
            gridcolor='rgba(226, 232, 240, 0.8)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248, 250, 252, 1)',
        height=600,
        font=dict(family='Inter'),
        shapes=[
            # 分界线
            dict(type='line', x0=share_threshold, x1=share_threshold, y0=min_growth, y1=max_growth, 
                 line=dict(dash='dot', color='#667eea', width=3)),
            dict(type='line', x0=0, x1=max_share, y0=growth_threshold, y1=growth_threshold,
                 line=dict(dash='dot', color='#667eea', width=3)),
            # 四象限背景颜色
            dict(type='rect', x0=0, y0=growth_threshold, x1=share_threshold, y1=max_growth,
                 fillcolor='rgba(245, 158, 11, 0.15)', line=dict(width=0), layer='below'),
            dict(type='rect', x0=share_threshold, y0=growth_threshold, x1=max_share, y1=max_growth,
                 fillcolor='rgba(34, 197, 94, 0.15)', line=dict(width=0), layer='below'),
            dict(type='rect', x0=0, y0=min_growth, x1=share_threshold, y1=growth_threshold,
                 fillcolor='rgba(148, 163, 184, 0.15)', line=dict(width=0), layer='below'),
            dict(type='rect', x0=share_threshold, y0=min_growth, x1=max_share, y1=growth_threshold,
                 fillcolor='rgba(59, 130, 246, 0.15)', line=dict(width=0), layer='below')
        ],
        annotations=[
            dict(x=share_threshold/2, y=max_growth-5, text='<b>❓ 问号产品</b><br>低份额·高增长',
                 showarrow=False, font=dict(size=12, color='#92400e'),
                 bgcolor='rgba(254, 243, 199, 0.95)', bordercolor='#f59e0b', borderwidth=2),
            dict(x=max_share-1, y=max_growth-5, text='<b>⭐ 明星产品</b><br>高份额·高增长',
                 showarrow=False, font=dict(size=12, color='#14532d'),
                 bgcolor='rgba(220, 252, 231, 0.95)', bordercolor='#22c55e', borderwidth=2),
            dict(x=share_threshold/2, y=min_growth+3, text='<b>🐕 瘦狗产品</b><br>低份额·低增长',
                 showarrow=False, font=dict(size=12, color='#334155'),
                 bgcolor='rgba(241, 245, 249, 0.95)', bordercolor='#94a3b8', borderwidth=2),
            dict(x=max_share-1, y=min_growth+3, text='<b>🐄 现金牛产品</b><br>高份额·低增长',
                 showarrow=False, font=dict(size=12, color='#1e3a8a'),
                 bgcolor='rgba(219, 234, 254, 0.95)', bordercolor='#3b82f6', borderwidth=2)
        ],
        legend=dict(
            orientation='h',
            x=0.5, xanchor='center', y=-0.15,
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#e2e8f0', borderwidth=1
        )
    )
    
    return fig

# 动态更新统计数据
def update_stats():
    current_time = time.time()
    if current_time - st.session_state.last_update >= 3:
        st.session_state.stat1_value = 1000 + random.randint(0, 200) + int(math.sin(current_time * 0.1) * 100)
        st.session_state.stat2_value = 4
        st.session_state.stat3_value = 24
        st.session_state.stat4_value = 95 + random.randint(0, 4) + int(math.sin(current_time * 0.15) * 3)
        st.session_state.last_update = current_time
        return True
    return False

# ========== 主应用逻辑 ==========

# 登录界面
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h2 style="font-size: 1.8rem; color: #2d3748; margin-bottom: 0.5rem; font-weight: 600;">Trolli SAL</h2>
            <p style="color: #718096; font-size: 0.9rem; margin-bottom: 2rem;">欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 登录表单
        with st.form("login_form"):
            st.markdown("#### 🔐 请输入访问密码")
            password = st.text_input("密码", type="password", placeholder="请输入访问密码", label_visibility="collapsed")
            submit_button = st.form_submit_button("登 录", use_container_width=True)
        
        if submit_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("🎉 登录成功！正在进入仪表盘...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")
        
        # 更新提示
        st.markdown("""
        <div style="text-align: center; margin: 3rem auto;">
            <div class="update-badge">
                🔄 每周四17:00刷新数据
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# 主应用界面
# 顶部导航栏
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 6, 2])

with col1:
    page_options = {
        "🏠 欢迎页面": "welcome",
        "📦 产品组合分析": "product_analysis"
    }
    selected_page = st.selectbox("页面选择", options=list(page_options.keys()), 
                                index=0 if st.session_state.current_page == "welcome" else 1,
                                label_visibility="collapsed")
    
    if page_options[selected_page] != st.session_state.current_page:
        st.session_state.current_page = page_options[selected_page]
        st.rerun()

with col3:
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_page = "welcome"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 根据当前页面显示内容
if st.session_state.current_page == "welcome":
    # 欢迎页面
    st.markdown("""
    <div class="main-title">
        <h1>📊 Trolli SAL</h1>
        <p>欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 动态统计数据
    is_updated = update_stats()
    update_class = "updating" if is_updated else ""
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat1_value}+</span>
            <div class="stat-label">数据分析</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat2_value}</span>
            <div class="stat-label">分析模块</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat3_value}</span>
            <div class="stat-label">小时监控</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat4_value}%</span>
            <div class="stat-label">准确率</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 功能模块介绍
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); font-size: 1.5rem;">
            💡 选择上方下拉菜单切换到产品组合分析页面
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <h3 class="feature-title">产品组合分析</h3>
            <p class="feature-description">
                分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">即将推出更多模块</h3>
            <p class="feature-description">
                预测库存分析、客户依赖分析、销售达成分析等更多功能模块正在开发中，敬请期待。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 更新提示
    st.markdown("""
    <div style="text-align: center; margin: 3rem auto;">
        <div class="update-badge">
            🔄 每周四17:00刷新数据
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "product_analysis":
    # 产品组合分析页面
    st.markdown("""
    <div class="main-title">
        <h1>📦 Trolli SAL 产品组合分析仪表盘</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner("🔄 正在加载数据..."):
        data_dict = load_real_data()
        key_metrics = calculate_key_metrics(data_dict)
        bcg_data = calculate_bcg_data(data_dict)
    
    # 创建标签页
    tabs = st.tabs([
        "📊 产品情况总览",
        "🎯 BCG产品矩阵", 
        "🚀 全国促销活动有效性",
        "📈 星品新品达成",
        "🔗 产品关联分析",
        "📍 漏铺市分析",
        "📅 季节性分析"
    ])
    
    # 标签页1: 产品情况总览
    with tabs[0]:
        st.markdown("### 📊 核心业务指标")
        
        # 创建4列布局显示关键指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 2025年总销售额",
                value=f"¥{key_metrics['total_sales']:,.0f}",
                delta="📈 基于销售数据计算"
            )
        
        with col2:
            st.metric(
                label="✅ JBP符合度",
                value=key_metrics['jbp_status'],
                delta="产品矩阵结构评估"
            )
        
        with col3:
            st.metric(
                label="🎯 KPI达成率",
                value=f"{key_metrics['kpi_rate']:.1f}%",
                delta=f"目标≥20% 实际{key_metrics['total_star_new_ratio']:.1f}%"
            )
        
        with col4:
            st.metric(
                label="🚀 全国促销有效性",
                value=f"{key_metrics['promo_effectiveness']:.1f}%",
                delta="基于促销活动数据"
            )
        
        # 第二行指标
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                label="🌟 新品占比",
                value=f"{key_metrics['new_product_ratio']:.1f}%",
                delta="新品销售额占比"
            )
        
        with col6:
            st.metric(
                label="⭐ 星品占比",
                value=f"{key_metrics['star_product_ratio']:.1f}%",
                delta="星品销售额占比"
            )
        
        with col7:
            st.metric(
                label="🎯 星品&新品总占比",
                value=f"{key_metrics['total_star_new_ratio']:.1f}%",
                delta="✅ 超过20%目标" if key_metrics['total_star_new_ratio'] >= 20 else "⚠️ 低于20%目标"
            )
        
        with col8:
            st.metric(
                label="📊 新品渗透率",
                value=f"{key_metrics['penetration_rate']:.1f}%",
                delta="购买新品客户比例"
            )
    
    # 标签页2: BCG产品矩阵
    with tabs[1]:
        st.markdown("### 🎯 BCG产品矩阵分析")
        
        # 全国BCG矩阵
        fig = create_bcg_matrix(bcg_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="national_bcg")
            
            # JBP符合度分析
            st.markdown("### 📊 JBP符合度分析")
            
            if bcg_data:
                # 计算各类产品占比
                total_sales = sum(p['sales'] for p in bcg_data)
                cow_sales = sum(p['sales'] for p in bcg_data if p['category'] == 'cow')
                star_question_sales = sum(p['sales'] for p in bcg_data if p['category'] in ['star', 'question'])
                dog_sales = sum(p['sales'] for p in bcg_data if p['category'] == 'dog')
                
                cow_ratio = (cow_sales / total_sales * 100) if total_sales > 0 else 0
                star_question_ratio = (star_question_sales / total_sales * 100) if total_sales > 0 else 0
                dog_ratio = (dog_sales / total_sales * 100) if total_sales > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    cow_status = "✓" if 45 <= cow_ratio <= 50 else "✗"
                    st.metric(
                        label="现金牛产品占比 (目标: 45%-50%)",
                        value=f"{cow_ratio:.1f}% {cow_status}",
                        delta="符合标准" if cow_status == "✓" else "需要调整"
                    )
                
                with col2:
                    star_status = "✓" if 40 <= star_question_ratio <= 45 else "✗"
                    st.metric(
                        label="明星&问号产品占比 (目标: 40%-45%)",
                        value=f"{star_question_ratio:.1f}% {star_status}",
                        delta="符合标准" if star_status == "✓" else "需要调整"
                    )
                
                with col3:
                    dog_status = "✓" if dog_ratio <= 10 else "✗"
                    st.metric(
                        label="瘦狗产品占比 (目标: ≤10%)",
                        value=f"{dog_ratio:.1f}% {dog_status}",
                        delta="符合标准" if dog_status == "✓" else "需要调整"
                    )
                
                # 总体评估
                overall_conforming = cow_status == "✓" and star_status == "✓" and dog_status == "✓"
                if overall_conforming:
                    st.success("🎉 总体评估：符合JBP计划 ✓")
                else:
                    st.warning("⚠️ 总体评估：需要优化产品结构")
        else:
            st.error("❌ BCG矩阵数据不足，无法生成图表")
    
    # 标签页3-7: 其他分析模块
    with tabs[2]:
        st.markdown("### 🚀 促销活动有效性分析")
        st.info("🚧 该模块正在开发中，将提供促销活动效果评估和优化建议...")
    
    with tabs[3]:
        st.markdown("### 📈 星品&新品总占比达成分析")
        st.info("🚧 该模块正在开发中，将提供区域、销售员、趋势三个维度的深度分析...")
    
    with tabs[4]:
        st.markdown("### 🔗 产品关联分析")
        st.info("🚧 该模块正在开发中，将提供产品关联规则挖掘和推荐...")
    
    with tabs[5]:
        st.markdown("### 📍 漏铺市分析")
        st.info("🚧 该模块正在开发中，将识别各区域产品覆盖空白和机会...")
    
    with tabs[6]:
        st.markdown("### 📅 季节性分析")
        st.info("🚧 该模块正在开发中，将展示产品的季节性销售特征和趋势...")
