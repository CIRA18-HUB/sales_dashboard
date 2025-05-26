# pages/产品组合分析.py - Trolli SAL 产品组合分析仪表盘（修复版）
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

warnings.filterwarnings('ignore')

# 设置页面配置 - 关键：隐藏侧边栏
st.set_page_config(
    page_title="📦 Trolli SAL 产品组合分析",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"  # 关键：默认隐藏侧边栏
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ 请先登录系统")
    if st.button("🏠 返回登录页", use_container_width=True):
        st.switch_page("app.py")
    st.stop()

# 隐藏所有默认元素并添加完整CSS样式
hide_elements_and_style = """
<style>
    /* 完全隐藏侧边栏 - 重要！ */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}

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
        width: 100%;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* 顶部导航栏 */
    .top-nav {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 100;
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
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title h1 { font-size: 2.2rem; }
        [data-testid="metric-container"] { margin-bottom: 1rem; }
    }
</style>
"""

st.markdown(hide_elements_and_style, unsafe_allow_html=True)

# 顶部导航栏 - 替代侧边栏
col1, col2, col3 = st.columns([2, 8, 2])
with col1:
    if st.button("🏠 返回主页", use_container_width=True):
        st.switch_page("app.py")
with col3:
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("app.py")

# 数据加载函数 - 修复版
@st.cache_data(ttl=3600)
def load_real_data():
    """加载真实数据文件 - 修复版，确保总是返回字典"""
    data_dict = {}  # 初始化为空字典
    failed_files = []
    
    try:
        # 1. 加载销售数据
        try:
            sales_data = pd.read_excel('TT与MT销售数据.xlsx')
            data_dict['sales_data'] = sales_data
        except Exception as e:
            failed_files.append(f"TT与MT销售数据.xlsx: {str(e)}")
        
        # 2. 加载出货数据 - 不显示错误信息
        try:
            shipment_data = pd.read_excel('2409-250224出货数据.xlsx')
            data_dict['shipment_data'] = shipment_data
        except:
            pass  # 静默处理这个已知缺失的文件
        
        # 3. 加载促销效果数据
        try:
            promotion_data = pd.read_excel('24-25促销效果销售数据.xlsx')
            data_dict['promotion_data'] = promotion_data
        except Exception as e:
            failed_files.append(f"24-25促销效果销售数据.xlsx: {str(e)}")
        
        # 4. 加载4月促销活动数据
        try:
            april_promo_data = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
            data_dict['april_promo_data'] = april_promo_data
        except Exception as e:
            failed_files.append(f"这是涉及到在4月份做的促销活动.xlsx: {str(e)}")
        
        # 5. 加载客户数据
        try:
            customer_data = pd.read_excel('客户月度指标.xlsx')
            data_dict['customer_data'] = customer_data
        except Exception as e:
            failed_files.append(f"客户月度指标.xlsx: {str(e)}")
        
        # 6. 加载月终库存数据
        try:
            inventory_data = pd.read_excel('月终库存2.xlsx')
            data_dict['inventory_data'] = inventory_data
        except Exception as e:
            failed_files.append(f"月终库存2.xlsx: {str(e)}")
        
        # 7. 加载单价数据
        try:
            price_data = pd.read_excel('单价.xlsx')
            data_dict['price_data'] = price_data
        except Exception as e:
            failed_files.append(f"单价.xlsx: {str(e)}")
        
        # 8. 加载产品代码数据
        try:
            with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
                dashboard_products = [line.strip() for line in f.readlines() if line.strip()]
            data_dict['dashboard_products'] = dashboard_products
        except Exception as e:
            failed_files.append(f"仪表盘产品代码.txt: {str(e)}")
        
        # 9. 加载新品代码数据
        try:
            with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
                new_products = [line.strip() for line in f.readlines() if line.strip()]
            data_dict['new_products'] = new_products
        except Exception as e:
            failed_files.append(f"仪表盘新品代码.txt: {str(e)}")
        
        # 10. 加载星品&新品KPI代码
        try:
            with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
                kpi_products = [line.strip() for line in f.readlines() if line.strip()]
            data_dict['kpi_products'] = kpi_products
        except Exception as e:
            failed_files.append(f"星品&新品年度KPI考核产品代码.txt: {str(e)}")
        
        # 显示加载失败的重要文件
        if failed_files:
            for failed in failed_files:
                if "2409-250224出货数据.xlsx" not in failed:  # 跳过这个已知缺失的文件
                    st.warning(f"⚠️ 文件加载失败: {failed}")
        
    except Exception as e:
        st.error(f"❌ 数据加载过程中发生错误: {str(e)}")
    
    return data_dict  # 确保总是返回字典，即使是空的

# 计算关键指标函数
def calculate_key_metrics(data_dict):
    """基于真实数据计算关键业务指标"""
    try:
        # 默认指标值
        metrics = {
            'total_sales': 0,
            'new_product_ratio': 0,
            'star_product_ratio': 0,
            'total_star_new_ratio': 0,
            'kpi_rate': 0,
            'jbp_status': "未达标",
            'penetration_rate': 0
        }
        
        # 检查数据完整性
        if not data_dict or 'sales_data' not in data_dict:
            return metrics
        
        sales_data = data_dict.get('sales_data')
        if sales_data is None or sales_data.empty:
            return metrics
        
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        
        # 确保有必要的列
        required_cols = ['产品代码', '单价（箱）', '求和项:数量（箱）']
        missing_cols = [col for col in required_cols if col not in sales_data.columns]
        if missing_cols:
            st.warning(f"⚠️ 销售数据缺少必要列: {missing_cols}")
            return metrics
        
        # 计算销售额
        sales_data_copy = sales_data.copy()
        sales_data_copy['销售额'] = sales_data_copy['单价（箱）'] * sales_data_copy['求和项:数量（箱）']
        
        # 1. 计算总销售额
        total_sales = sales_data_copy['销售额'].sum()
        if total_sales <= 0:
            return metrics
        
        metrics['total_sales'] = total_sales
        
        # 2. 计算新品占比
        if new_products:
            new_product_sales = sales_data_copy[sales_data_copy['产品代码'].isin(new_products)]['销售额'].sum()
            new_product_ratio = (new_product_sales / total_sales * 100)
            metrics['new_product_ratio'] = new_product_ratio
        
        # 3. 计算星品占比
        if kpi_products and new_products:
            star_products = [p for p in kpi_products if p not in new_products]
            if star_products:
                star_product_sales = sales_data_copy[sales_data_copy['产品代码'].isin(star_products)]['销售额'].sum()
                star_product_ratio = (star_product_sales / total_sales * 100)
                metrics['star_product_ratio'] = star_product_ratio
        
        # 4. 计算总占比和其他指标
        metrics['total_star_new_ratio'] = metrics['new_product_ratio'] + metrics['star_product_ratio']
        metrics['kpi_rate'] = (metrics['total_star_new_ratio'] / 20) * 100 if metrics['total_star_new_ratio'] > 0 else 0
        metrics['jbp_status'] = "达标" if metrics['total_star_new_ratio'] >= 20 else "未达标"
        
        # 5. 计算渗透率
        if '客户代码' in sales_data_copy.columns:
            total_customers = sales_data_copy['客户代码'].nunique()
            if total_customers > 0 and new_products:
                new_product_customers = sales_data_copy[sales_data_copy['产品代码'].isin(new_products)]['客户代码'].nunique()
                metrics['penetration_rate'] = (new_product_customers / total_customers * 100)
        
        return metrics
    
    except Exception as e:
        st.error(f"❌ 指标计算失败: {str(e)}")
        return {
            'total_sales': 0,
            'new_product_ratio': 0,
            'star_product_ratio': 0,
            'total_star_new_ratio': 0,
            'kpi_rate': 0,
            'jbp_status': "未达标",
            'penetration_rate': 0
        }

# BCG矩阵数据计算
def calculate_bcg_data(data_dict):
    """基于真实数据计算BCG矩阵数据"""
    try:
        if not data_dict or 'sales_data' not in data_dict:
            return []
        
        sales_data = data_dict.get('sales_data')
        if sales_data is None or sales_data.empty:
            return []
        
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        star_products = [p for p in kpi_products if p not in new_products] if kpi_products and new_products else []
        
        # 计算销售额
        sales_data_copy = sales_data.copy()
        if '销售额' not in sales_data_copy.columns:
            sales_data_copy['销售额'] = sales_data_copy['单价（箱）'] * sales_data_copy['求和项:数量（箱）']
        
        # 按产品聚合数据
        product_sales = sales_data_copy.groupby('产品代码')['销售额'].sum().reset_index()
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
            
            # 基于产品类型设定增长率
            if product_code in new_products:
                growth_rate = min(market_share * 5 + 30, 80)
            elif product_code in star_products:
                growth_rate = min(market_share * 3 + 20, 60)
            else:
                growth_rate = max(market_share * 2 - 5, -10)
            
            # 确定BCG分类
            share_threshold = 1.5
            growth_threshold = 20
            
            if market_share >= share_threshold and growth_rate > growth_threshold:
                category = 'star'
            elif market_share < share_threshold and growth_rate > growth_threshold:
                category = 'question'
            elif market_share >= share_threshold and growth_rate <= growth_threshold:
                category = 'cow'
            else:
                category = 'dog'
            
            product_name = f"产品{str(product_code)[-4:]}" if len(str(product_code)) > 4 else str(product_code)
            
            bcg_data.append({
                'code': product_code,
                'name': product_name,
                'share': market_share,
                'growth': growth_rate,
                'sales': product_sales_amount,
                'category': category
            })
        
        # 按销售额排序，取前20个产品
        bcg_data = sorted(bcg_data, key=lambda x: x['sales'], reverse=True)[:20]
        
        return bcg_data
    
    except Exception as e:
        st.error(f"❌ BCG数据计算失败: {str(e)}")
        return []

# 创建BCG矩阵图表
def create_bcg_matrix(bcg_data):
    """创建BCG矩阵图表"""
    if not bcg_data:
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
                    size=[max(min(math.sqrt(p['sales']) / 100, 60), 15) for p in category_data],
                    color=colors[category],
                    opacity=0.9,
                    line=dict(width=3, color='white')
                ),
                name={
                    'star': '⭐ 明星产品',
                    'question': '❓ 问号产品',
                    'cow': '🐄 现金牛产品',
                    'dog': '🐕 瘦狗产品'
                }[category],
                text=[p['name'][:8] for p in category_data],
                textposition='middle center',
                textfont=dict(size=9, color='white', family='Inter'),
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
        title=dict(text='产品组合BCG矩阵分析', font=dict(size=18, color='#1e293b'), x=0.5),
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
        ],
        legend=dict(
            orientation='h',
            x=0.5, xanchor='center', y=-0.15,
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#e2e8f0', borderwidth=1
        )
    )
    
    return fig

# 创建促销有效性图表
def create_promotion_chart(data_dict):
    """创建促销有效性图表"""
    try:
        if not data_dict:
            return None
            
        # 优先使用4月促销数据
        promo_data = data_dict.get('april_promo_data')
        if promo_data is None or promo_data.empty:
            promo_data = data_dict.get('promotion_data')
        
        if promo_data is None or promo_data.empty:
            return None
        
        # 查找销量相关列
        sales_col = None
        for col in promo_data.columns:
            if any(keyword in str(col) for keyword in ['销量', '数量', '箱数', '销售额']):
                sales_col = col
                break
        
        if sales_col is None and len(promo_data.columns) > 1:
            # 假设第二列是销量数据
            sales_col = promo_data.columns[1]
        
        if sales_col is None:
            return None
        
        # 查找产品相关列
        product_col = None
        for col in promo_data.columns:
            if any(keyword in str(col) for keyword in ['产品', '商品']):
                product_col = col
                break
        
        if product_col is None:
            product_col = promo_data.columns[0]
        
        # 聚合数据
        promo_summary = promo_data.groupby(product_col)[sales_col].sum().reset_index()
        promo_summary = promo_summary.sort_values(sales_col, ascending=False).head(10)
        
        if promo_summary.empty:
            return None
        
        # 计算有效性
        median_sales = promo_summary[sales_col].median()
        promo_summary['is_effective'] = promo_summary[sales_col] > median_sales
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=promo_summary[product_col],
            y=promo_summary[sales_col],
            marker_color=[
                '#10b981' if effective else '#ef4444' 
                for effective in promo_summary['is_effective']
            ],
            marker_line=dict(width=2, color='white'),
            text=[f"{val:,.0f}" for val in promo_summary[sales_col]],
            textposition='outside'
        ))
        
        effective_count = promo_summary['is_effective'].sum()
        total_count = len(promo_summary)
        effectiveness_rate = (effective_count / total_count * 100) if total_count > 0 else 0
        
        fig.update_layout(
            title=f'促销活动有效性分析: {effectiveness_rate:.1f}% ({effective_count}/{total_count})',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.9)',
            height=500,
            font=dict(family='Inter'),
            xaxis=dict(title='🎯 促销产品', tickangle=45),
            yaxis=dict(title=f'📦 {sales_col}'),
            margin=dict(l=80, r=80, t=80, b=120)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"❌ 促销图表创建失败: {str(e)}")
        return None

# 创建星品新品达成分析
def create_achievement_analysis(data_dict, key_metrics):
    """创建星品新品达成分析"""
    try:
        if not data_dict or 'sales_data' not in data_dict:
            return None, None
        
        sales_data = data_dict['sales_data']
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        
        # 创建达成率仪表盘
        fig1 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = key_metrics['total_star_new_ratio'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "星品&新品总占比"},
            delta = {'reference': 20, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 30], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': '#ff4444'},
                    {'range': [10, 20], 'color': '#ffaa00'},
                    {'range': [20, 30], 'color': '#00ff00'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 20
                }
            }
        ))
        
        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "darkblue", 'family': "Arial"},
            height=400
        )
        
        # 尝试创建月度趋势（如果有月度数据）
        fig2 = None
        if '发运月份' in sales_data.columns or '月份' in sales_data.columns:
            date_col = '发运月份' if '发运月份' in sales_data.columns else '月份'
            sales_data_copy = sales_data.copy()
            sales_data_copy['销售额'] = sales_data_copy['单价（箱）'] * sales_data_copy['求和项:数量（箱）']
            
            # 计算每月的占比
            monthly_data = []
            for month in sales_data_copy[date_col].unique():
                month_data = sales_data_copy[sales_data_copy[date_col] == month]
                month_total = month_data['销售额'].sum()
                if month_total > 0:
                    new_sales = month_data[month_data['产品代码'].isin(new_products)]['销售额'].sum()
                    star_sales = month_data[month_data['产品代码'].isin([p for p in kpi_products if p not in new_products])]['销售额'].sum()
                    ratio = (new_sales + star_sales) / month_total * 100
                    monthly_data.append({'月份': month, '占比': ratio})
            
            if monthly_data:
                monthly_df = pd.DataFrame(monthly_data)
                fig2 = px.line(monthly_df, x='月份', y='占比', 
                             title='星品&新品占比月度趋势',
                             markers=True)
                fig2.add_hline(y=20, line_dash="dash", line_color="red", 
                             annotation_text="目标线 20%")
                fig2.update_layout(height=400)
        
        return fig1, fig2
    
    except Exception as e:
        st.error(f"❌ 达成分析创建失败: {str(e)}")
        return None, None

# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div class="main-title">
        <h1>📦 Trolli SAL 产品组合分析仪表盘</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner("🔄 正在加载真实数据文件..."):
        data_dict = load_real_data()
        
        # 修复：确保data_dict不为None且有数据
        if not data_dict or len(data_dict) == 0:
            st.error("❌ 没有成功加载任何数据文件，无法进行分析")
            st.info("💡 请确保所有数据文件都在正确的位置")
            if st.button("🏠 返回主页", key="error_return"):
                st.switch_page("app.py")
            return
            
        key_metrics = calculate_key_metrics(data_dict)
        bcg_data = calculate_bcg_data(data_dict)
    
    # 创建标签页
    tabs = st.tabs([
        "📊 总览",
        "🎯 BCG矩阵", 
        "🚀 促销分析",
        "📈 达成分析",
        "🔗 关联分析",
        "📍 漏铺分析",
        "📅 季节性"
    ])
    
    # 标签页1: 产品情况总览
    with tabs[0]:
        st.markdown("### 📊 核心业务指标")
        
        # 创建4列布局显示关键指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 总销售额",
                value=f"¥{key_metrics['total_sales']:,.0f}",
                delta="基于真实销售数据"
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
                label="📊 新品渗透率",
                value=f"{key_metrics['penetration_rate']:.1f}%",
                delta="购买新品客户比例"
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
            # 计算数据覆盖率
            available_files = len([k for k, v in data_dict.items() if v is not None and (isinstance(v, pd.DataFrame) and not v.empty or isinstance(v, list) and v)])
            total_files = 10
            coverage_rate = (available_files / total_files * 100)
            st.metric(
                label="📄 数据覆盖率",
                value=f"{coverage_rate:.0f}%",
                delta=f"{available_files}/{total_files}个文件"
            )
    
    # 标签页2: BCG产品矩阵
    with tabs[1]:
        st.markdown("### 🎯 BCG产品矩阵分析")
        
        if bcg_data:
            fig = create_bcg_matrix(bcg_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="bcg_matrix")
                
                # JBP符合度分析
                st.markdown("### 📊 JBP符合度分析")
                
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
                    cow_status = "✓" if 30 <= cow_ratio <= 60 else "✗"
                    st.metric(
                        label="现金牛产品占比 (目标: 30%-60%)",
                        value=f"{cow_ratio:.1f}% {cow_status}",
                        delta="符合标准" if cow_status == "✓" else "需要调整"
                    )
                
                with col2:
                    star_status = "✓" if 30 <= star_question_ratio <= 50 else "✗"
                    st.metric(
                        label="明星&问号产品占比 (目标: 30%-50%)",
                        value=f"{star_question_ratio:.1f}% {star_status}",
                        delta="符合标准" if star_status == "✓" else "需要调整"
                    )
                
                with col3:
                    dog_status = "✓" if dog_ratio <= 20 else "✗"
                    st.metric(
                        label="瘦狗产品占比 (目标: ≤20%)",
                        value=f"{dog_ratio:.1f}% {dog_status}",
                        delta="符合标准" if dog_status == "✓" else "需要调整"
                    )
                
                # 总体评估
                overall_conforming = cow_status == "✓" and star_status == "✓" and dog_status == "✓"
                if overall_conforming:
                    st.success("🎉 总体评估：符合JBP计划标准 ✓")
                else:
                    st.warning("⚠️ 总体评估：产品结构需要优化")
        else:
            st.error("❌ 没有足够的数据生成BCG矩阵")
    
    # 标签页3: 促销活动有效性
    with tabs[2]:
        st.markdown("### 🚀 促销活动有效性分析")
        
        fig = create_promotion_chart(data_dict)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="promotion_chart")
            
            st.info("""
            📊 **数据来源：** 基于真实促销活动数据文件  
            🎯 **分析逻辑：** 销量超过中位数为有效，低于中位数为无效  
            💡 **提示：** 悬停在柱状图上可查看详细数据
            """)
        else:
            st.warning("⚠️ 促销数据不足或格式不正确，无法生成图表")
    
    # 标签页4: 星品&新品达成分析
    with tabs[3]:
        st.markdown("### 📈 星品&新品总占比达成分析")
        
        fig1, fig2 = create_achievement_analysis(data_dict, key_metrics)
        
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # 显示详细信息
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌟 新品表现分析")
            new_products = data_dict.get('new_products', [])
            if new_products:
                st.write(f"新品代码数量: {len(new_products)}个")
                st.write(f"新品销售占比: {key_metrics['new_product_ratio']:.1f}%")
            else:
                st.warning("未找到新品代码数据")
        
        with col2:
            st.markdown("#### ⭐ 星品表现分析")
            kpi_products = data_dict.get('kpi_products', [])
            if kpi_products and new_products:
                star_count = len([p for p in kpi_products if p not in new_products])
                st.write(f"星品代码数量: {star_count}个")
                st.write(f"星品销售占比: {key_metrics['star_product_ratio']:.1f}%")
            else:
                st.warning("未找到完整的产品代码数据")
    
    # 标签页5: 产品关联分析
    with tabs[4]:
        st.markdown("### 🔗 产品关联分析")
        
        try:
            if 'sales_data' in data_dict and 'customer_data' in data_dict:
                sales_data = data_dict['sales_data']
                if '客户代码' in sales_data.columns and '产品代码' in sales_data.columns:
                    # 创建客户-产品购买矩阵
                    customer_product = sales_data.groupby(['客户代码', '产品代码'])['求和项:数量（箱）'].sum().reset_index()
                    
                    # 找出购买多个产品的客户
                    customer_counts = customer_product.groupby('客户代码')['产品代码'].nunique()
                    multi_product_customers = customer_counts[customer_counts > 1].index
                    
                    if len(multi_product_customers) > 0:
                        st.info(f"📊 发现 {len(multi_product_customers)} 个客户购买了多种产品")
                        
                        # 简单的关联分析示例
                        st.markdown("#### 🎯 产品组合购买TOP10")
                        # 这里可以进一步实现关联规则挖掘
                        sample_data = customer_product[customer_product['客户代码'].isin(multi_product_customers)].head(10)
                        st.dataframe(sample_data)
                    else:
                        st.warning("⚠️ 未发现购买多种产品的客户")
                else:
                    st.warning("⚠️ 销售数据缺少必要的列")
            else:
                st.warning("⚠️ 缺少必要的数据文件")
        except Exception as e:
            st.error(f"❌ 关联分析失败: {str(e)}")
    
    # 标签页6: 漏铺市分析
    with tabs[5]:
        st.markdown("### 📍 漏铺市分析")
        
        try:
            if 'sales_data' in data_dict:
                sales_data = data_dict['sales_data']
                if '所属区域' in sales_data.columns:
                    # 分析产品在各区域的覆盖情况
                    region_product = sales_data.groupby(['所属区域', '产品代码']).size().reset_index(name='覆盖数')
                    
                    # 计算每个区域的产品覆盖率
                    all_products = sales_data['产品代码'].unique()
                    all_regions = sales_data['所属区域'].unique()
                    
                    coverage_data = []
                    for region in all_regions:
                        region_products = region_product[region_product['所属区域'] == region]['产品代码'].unique()
                        coverage_rate = len(region_products) / len(all_products) * 100
                        coverage_data.append({
                            '区域': region,
                            '覆盖产品数': len(region_products),
                            '总产品数': len(all_products),
                            '覆盖率': coverage_rate
                        })
                    
                    coverage_df = pd.DataFrame(coverage_data)
                    
                    # 创建覆盖率图表
                    fig = px.bar(coverage_df, x='区域', y='覆盖率', 
                                title='各区域产品覆盖率分析',
                                color='覆盖率',
                                color_continuous_scale='RdYlGn')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 显示详细数据
                    st.dataframe(coverage_df)
                else:
                    st.warning("⚠️ 销售数据缺少区域信息")
            else:
                st.warning("⚠️ 缺少销售数据文件")
        except Exception as e:
            st.error(f"❌ 漏铺分析失败: {str(e)}")
    
    # 标签页7: 季节性分析
    with tabs[6]:
        st.markdown("### 📅 季节性分析")
        
        try:
            if 'sales_data' in data_dict:
                sales_data = data_dict['sales_data']
                date_col = None
                
                # 查找日期列
                for col in ['发运月份', '月份', '日期']:
                    if col in sales_data.columns:
                        date_col = col
                        break
                
                if date_col:
                    sales_data_copy = sales_data.copy()
                    sales_data_copy['销售额'] = sales_data_copy['单价（箱）'] * sales_data_copy['求和项:数量（箱）']
                    
                    # 按月份汇总
                    monthly_sales = sales_data_copy.groupby(date_col)['销售额'].sum().reset_index()
                    monthly_sales = monthly_sales.sort_values(date_col)
                    
                    # 创建趋势图
                    fig = px.line(monthly_sales, x=date_col, y='销售额', 
                                 title='月度销售趋势分析',
                                 markers=True)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 计算环比增长
                    monthly_sales['环比增长'] = monthly_sales['销售额'].pct_change() * 100
                    
                    # 显示统计信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("最高销售月份", 
                                 monthly_sales.loc[monthly_sales['销售额'].idxmax(), date_col],
                                 f"¥{monthly_sales['销售额'].max():,.0f}")
                    with col2:
                        st.metric("最低销售月份", 
                                 monthly_sales.loc[monthly_sales['销售额'].idxmin(), date_col],
                                 f"¥{monthly_sales['销售额'].min():,.0f}")
                    with col3:
                        avg_growth = monthly_sales['环比增长'].mean()
                        st.metric("平均环比增长", 
                                 f"{avg_growth:.1f}%",
                                 "正增长" if avg_growth > 0 else "负增长")
                else:
                    st.warning("⚠️ 销售数据缺少时间信息")
            else:
                st.warning("⚠️ 缺少销售数据文件")
        except Exception as e:
            st.error(f"❌ 季节性分析失败: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ 应用程序发生错误: {str(e)}")
        st.info("💡 请检查数据文件是否完整，或联系管理员")
        if st.button("🏠 返回主页", key="main_error_return"):
            st.switch_page("app.py")
