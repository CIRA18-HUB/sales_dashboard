# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
import time
import re
from itertools import combinations
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide"
)

# 增强的CSS样式 - 统一容器设计
st.markdown("""
<style>
    /* 导入Google字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 全局字体和背景 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        color: #1f2937;
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
        background: rgba(255,255,255,0.98);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* 确保所有文本颜色正确 */
    .stApp, .stApp * {
        color: #1f2937 !important;
    }
    
    /* 主标题样式 - 增强动画 */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white !important;
        border-radius: 25px;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.5s ease-out, glow 2s ease-in-out infinite alternate;
        box-shadow: 
            0 15px 35px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1),
            inset 0 1px 0 rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        transform: perspective(1000px) rotateX(0deg);
        transition: transform 0.3s ease;
    }
    
    .main-header * {
        color: white !important;
    }
    
    .main-header:hover {
        transform: perspective(1000px) rotateX(-2deg) scale(1.02);
        box-shadow: 
            0 25px 50px rgba(102, 126, 234, 0.5),
            0 10px 30px rgba(0,0,0,0.15);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
    }
    
    .main-header::after {
        content: '✨';
        position: absolute;
        top: 10%;
        right: 10%;
        font-size: 2rem;
        animation: sparkle 1.5s ease-in-out infinite;
    }
    
    /* 统一的内容容器样式 */
    .content-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        animation: containerFadeIn 1.2s ease-out;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .content-container:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.12),
            0 8px 20px rgba(0,0,0,0.06);
    }
    
    .content-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.02), transparent);
        animation: containerShimmer 8s linear infinite;
    }
    
    /* 确保容器内文本颜色正确 */
    .content-container, .content-container * {
        color: #1f2937 !important;
    }
    
    /* 给所有图表添加圆角 */
    .js-plotly-plot .plotly, .js-plotly-plot .plot-container {
        border-radius: 20px !important;
        overflow: hidden !important;
    }
    
    /* Plotly图表容器圆角 */
    .user-select-none {
        border-radius: 20px !important;
    }
    
    @keyframes containerFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    @keyframes containerShimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @keyframes glow {
        from { box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4), 0 5px 15px rgba(0,0,0,0.1); }
        to { box-shadow: 0 20px 40px rgba(102, 126, 234, 0.6), 0 8px 20px rgba(0,0,0,0.15); }
    }
    
    @keyframes sparkle {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
        50% { transform: scale(1.3) rotate(180deg); opacity: 0.7; }
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
            transform: translateY(-50px) scale(0.8) rotateX(-10deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }
    
    /* 增强的指标卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem 1.5rem;
        border-radius: 25px;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.08),
            0 5px 15px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.9);
        text-align: center;
        height: 100%;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUpStagger 1s ease-out;
        position: relative;
        overflow: visible;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        min-height: 160px;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.8s ease;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 25px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-15px) scale(1.05) rotateY(5deg);
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.15),
            0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
        animation: pulse 1.5s infinite;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover::after {
        opacity: 0.1;
    }
    
    @keyframes slideUpStagger {
        from { 
            opacity: 0; 
            transform: translateY(60px) scale(0.8) rotateX(-15deg); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1) rotateX(0deg); 
        }
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.8rem;
        animation: textGradient 4s ease infinite, bounce 2s ease-in-out infinite;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-3px); }
        60% { transform: translateY(-2px); }
    }
    
    @keyframes textGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-label {
        color: #374151 !important;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.5rem;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    
    .metric-sublabel {
        color: #6b7280 !important;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 500;
        font-style: italic;
    }
    
    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 
            inset 0 2px 4px rgba(0,0,0,0.06),
            0 4px 8px rgba(0,0,0,0.04);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 35px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 700;
        font-size: 1rem;
        color: #374151 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.15), transparent);
        transition: left 0.8s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.4),
            0 5px 15px rgba(0,0,0,0.1);
        animation: activeTab 0.5s ease;
    }
    
    .stTabs [aria-selected="true"]::before {
        display: none;
    }
    
    @keyframes activeTab {
        0% { transform: scale(0.95); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1.02); }
    }
    
    /* 动画卡片延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }
    .metric-card:nth-child(9) { animation-delay: 0.9s; }
    .metric-card:nth-child(10) { animation-delay: 1.0s; }
    
    /* 促销活动有效率标题样式 */
    .promo-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    .promo-header * {
        color: white !important;
    }
    
    /* 添加脉动效果 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.8rem;
        }
        .metric-card {
            padding: 1.5rem 1rem;
        }
        .main-header {
            padding: 2rem 0;
        }
        .content-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
    
    /* Streamlit组件样式覆盖 */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.9) !important;
        color: #1f2937 !important;
    }
    
    .stRadio > div {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 15px;
        padding: 1rem;
    }
    
    .stRadio label {
        color: #1f2937 !important;
    }
    
    /* 确保所有Streamlit元素的文本颜色 */
    .stMarkdown, .stText, .stCaption {
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)

# 产品名称简化函数
def simplify_product_name(name):
    """简化产品名称，去掉口力和-中国等后缀"""
    if pd.isna(name):
        return ""
    # 去掉口力
    name = name.replace('口力', '')
    # 去掉-中国等后缀
    name = re.sub(r'-中国.*$', '', name)
    # 去掉其他常见后缀
    name = re.sub(r'（.*）$', '', name)
    name = re.sub(r'\(.*\)$', '', name)
    # 限制长度
    if len(name) > 8:
        name = name[:8] + '..'
    return name.strip()

# 缓存数据加载函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    try:
        # 星品代码
        with open('星品&新品年度KPI考核产品代码.txt', 'r', encoding='utf-8') as f:
            star_products = [line.strip() for line in f.readlines() if line.strip()]
        
        # 新品代码
        with open('仪表盘新品代码.txt', 'r', encoding='utf-8') as f:
            new_products = [line.strip() for line in f.readlines() if line.strip()]
        
        # 仪表盘产品代码
        with open('仪表盘产品代码.txt', 'r', encoding='utf-8') as f:
            dashboard_products = [line.strip() for line in f.readlines() if line.strip()]
        
        # 促销活动数据
        promotion_df = pd.read_excel('这是涉及到在4月份做的促销活动.xlsx')
        
        # 销售数据
        sales_df = pd.read_excel('24-25促销效果销售数据.xlsx')
        sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'])
        sales_df['销售额'] = sales_df['单价'] * sales_df['箱数']
        
        # 简化产品名称
        sales_df['产品简称'] = sales_df['产品简称'].apply(simplify_product_name)
        promotion_df['促销产品名称'] = promotion_df['促销产品名称'].apply(simplify_product_name)
        
        return {
            'star_products': star_products,
            'new_products': new_products,
            'dashboard_products': dashboard_products,
            'promotion_df': promotion_df,
            'sales_df': sales_df
        }
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None

# 计算总体指标（基于后续所有分析）
def calculate_comprehensive_metrics(data):
    """计算产品情况总览的各项指标（基于所有分析）"""
    sales_df = data['sales_df']
    star_products = data['star_products']
    new_products = data['new_products']
    dashboard_products = data['dashboard_products']
    
    # 2025年数据
    sales_2025 = sales_df[sales_df['发运月份'].dt.year == 2025]
    
    # 总销售额
    total_sales = sales_2025['销售额'].sum()
    
    # 星品和新品销售额
    star_sales = sales_2025[sales_2025['产品代码'].isin(star_products)]['销售额'].sum()
    new_sales = sales_2025[sales_2025['产品代码'].isin(new_products)]['销售额'].sum()
    
    # 占比计算
    star_ratio = (star_sales / total_sales * 100) if total_sales > 0 else 0
    new_ratio = (new_sales / total_sales * 100) if total_sales > 0 else 0
    total_ratio = star_ratio + new_ratio
    
    # 新品渗透率
    total_customers = sales_2025['客户名称'].nunique()
    new_customers = sales_2025[sales_2025['产品代码'].isin(new_products)]['客户名称'].nunique()
    penetration_rate = (new_customers / total_customers * 100) if total_customers > 0 else 0
    
    # BCG分析 - 计算JBP符合度
    product_analysis = analyze_product_bcg_comprehensive(sales_df[sales_df['产品代码'].isin(dashboard_products)], dashboard_products)
    
    total_bcg_sales = product_analysis['sales'].sum()
    cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
    star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
    
    cow_ratio = cow_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0
    star_question_ratio = star_question_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0
    
    jbp_status = 'YES' if (45 <= cow_ratio <= 50 and 40 <= star_question_ratio <= 45) else 'NO'
    
    # 促销有效性
    promo_results = analyze_promotion_effectiveness_enhanced(data)
    promo_effectiveness = (promo_results['is_effective'].sum() / len(promo_results) * 100) if len(promo_results) > 0 else 0
    
    # 有效产品分析
    effective_rate_all = calculate_effective_products_rate(sales_2025, data['dashboard_products'])
    
    # 计算有效产品详细数据
    product_analysis_eff = analyze_effective_products(data, 'national')
    effective_products = product_analysis_eff[product_analysis_eff['is_effective'] == True]
    effective_count = len(effective_products)
    
    if len(effective_products) > 0:
        avg_effective_sales = effective_products['monthly_avg_boxes'].mean()
    else:
        avg_effective_sales = 0
    
    return {
        'total_sales': total_sales,
        'star_ratio': star_ratio,
        'new_ratio': new_ratio,
        'total_ratio': total_ratio,
        'penetration_rate': penetration_rate,
        'jbp_status': jbp_status,
        'promo_effectiveness': promo_effectiveness,
        'effective_products_rate': effective_rate_all,
        'effective_products_count': effective_count,
        'avg_effective_sales': avg_effective_sales
    }

def analyze_product_bcg_comprehensive(sales_df, dashboard_products):
    """分析产品BCG矩阵数据，包括所有仪表盘产品"""
    if len(sales_df) == 0:
        return pd.DataFrame()
    
    current_year = 2025
    current_data = sales_df[sales_df['发运月份'].dt.year == current_year]
    prev_data = sales_df[sales_df['发运月份'].dt.year == current_year - 1]
    
    product_stats = []
    total_sales = current_data['销售额'].sum()
    
    for product in dashboard_products:
        current_product_data = current_data[current_data['产品代码'] == product]
        prev_product_data = prev_data[prev_data['产品代码'] == product]
        
        current_sales = current_product_data['销售额'].sum()
        prev_sales = prev_product_data['销售额'].sum()
        
        # 获取产品名称
        if len(current_product_data) > 0:
            product_name = current_product_data['产品简称'].iloc[0]
        elif len(prev_product_data) > 0:
            product_name = prev_product_data['产品简称'].iloc[0]
        else:
            all_product_data = sales_df[sales_df['产品代码'] == product]
            if len(all_product_data) > 0:
                product_name = all_product_data['产品简称'].iloc[0]
            else:
                product_name = product
        
        # 只处理有销售数据的产品
        if current_sales > 0 or prev_sales > 0:
            market_share = (current_sales / total_sales * 100) if total_sales > 0 else 0
            
            # 计算增长率，限制在合理范围内
            if prev_sales > 0:
                growth_rate = ((current_sales - prev_sales) / prev_sales * 100)
            elif current_sales > 0:
                growth_rate = 100
            else:
                growth_rate = 0
            
            # 存储真实增长率用于显示
            real_growth_rate = growth_rate
            # 限制显示范围用于图表
            display_growth_rate = max(-50, min(growth_rate, 100))
            
            # 分类逻辑
            if market_share >= 1.5 and growth_rate > 20:
                category = 'star'
                reason = f"市场份额高({market_share:.1f}%≥1.5%)且增长快({growth_rate:.1f}%>20%)"
            elif market_share < 1.5 and growth_rate > 20:
                category = 'question'
                reason = f"市场份额低({market_share:.1f}%<1.5%)但增长快({growth_rate:.1f}%>20%)"
            elif market_share >= 1.5 and growth_rate <= 20:
                category = 'cow'
                reason = f"市场份额高({market_share:.1f}%≥1.5%)但增长慢({growth_rate:.1f}%≤20%)"
            else:
                category = 'dog'
                reason = f"市场份额低({market_share:.1f}%<1.5%)且增长慢({growth_rate:.1f}%≤20%)"
            
            product_stats.append({
                'product': product,
                'name': product_name,
                'market_share': market_share,
                'growth_rate': display_growth_rate,
                'real_growth_rate': real_growth_rate,
                'sales': current_sales,
                'prev_sales': prev_sales,
                'category': category,
                'category_reason': reason,
                'calculation_detail': f"当前销售额: ¥{current_sales:,.0f}\n去年销售额: ¥{prev_sales:,.0f}\n市场份额: {market_share:.2f}%\n真实增长率: {real_growth_rate:.1f}%"
            })
    
    return pd.DataFrame(product_stats)

def create_bcg_matrix(data, dimension='national', selected_region=None):
    """创建BCG矩阵分析"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    # 确保只分析仪表盘产品
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    
    if dimension == 'national':
        product_analysis = analyze_product_bcg_comprehensive(sales_df_filtered, dashboard_products)
        return product_analysis
    else:
        if selected_region:
            region_data = sales_df_filtered[sales_df_filtered['区域'] == selected_region]
            region_analysis = analyze_product_bcg_comprehensive(region_data, dashboard_products)
            return region_analysis
        return pd.DataFrame()

def plot_bcg_matrix(product_df, title="BCG产品矩阵"):
    """绘制简化的BCG矩阵图"""
    if len(product_df) == 0:
        return go.Figure()
    
    fig = go.Figure()
    
    # 定义象限颜色和产品颜色
    quadrant_colors = {
        'star': 'rgba(255, 235, 153, 0.3)',
        'question': 'rgba(255, 153, 153, 0.3)',
        'cow': 'rgba(204, 235, 255, 0.3)',
        'dog': 'rgba(230, 230, 230, 0.3)'
    }
    
    bubble_colors = {
        'star': '#FFC107',
        'question': '#F44336',
        'cow': '#2196F3',
        'dog': '#9E9E9E'
    }
    
    category_names = {
        'star': '⭐ 明星产品',
        'question': '❓ 问号产品',
        'cow': '🐄 现金牛产品',
        'dog': '🐕 瘦狗产品'
    }
    
    # 添加象限背景
    fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=100,
                  fillcolor=quadrant_colors['question'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=1.5, y0=20, x1=10, y1=100,
                  fillcolor=quadrant_colors['star'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0, y0=-50, x1=1.5, y1=20,
                  fillcolor=quadrant_colors['dog'], line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=1.5, y0=-50, x1=10, y1=20,
                  fillcolor=quadrant_colors['cow'], line=dict(width=0), layer="below")
    
    # 绘制产品气泡
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            # 优化位置分布
            positions = optimize_smart_grid_positions(cat_data, category)
            
            # 设置气泡大小
            sizes = cat_data['sales'].apply(lambda x: max(min(np.sqrt(x)/20, 60), 25))
            
            # 创建hover文本
            hover_texts = []
            for _, row in cat_data.iterrows():
                category_name = category_names.get(category, category)
                hover_text = f"""<b>{row['name']} ({row['product']})</b><br>
<br><b>分类：{category_name}</b><br>
<br><b>分类原因：</b><br>{row['category_reason']}<br>
<br><b>详细信息：</b><br>{row['calculation_detail']}<br>
<br><b>策略建议：</b><br>{get_strategy_suggestion(category)}"""
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=positions['x'],
                y=positions['y'],
                mode='markers+text',
                marker=dict(
                    size=sizes,
                    color=bubble_colors[category],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=cat_data['name'].apply(lambda x: x[:6] + '..' if len(x) > 6 else x),
                textposition='middle center',
                textfont=dict(size=8, color='white', weight='bold'),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts,
                showlegend=False,
                name=category_name
            ))
    
    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", opacity=0.5, line_width=2)
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", opacity=0.5, line_width=2)
    
    # 添加象限标注
    annotations = [
        dict(x=0.75, y=60, text="<b>❓ 问号产品</b><br>低份额·高增长", 
             showarrow=False, font=dict(size=12, color="#F44336"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#F44336", borderwidth=2),
        dict(x=5.5, y=60, text="<b>⭐ 明星产品</b><br>高份额·高增长", 
             showarrow=False, font=dict(size=12, color="#FFC107"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#FFC107", borderwidth=2),
        dict(x=0.75, y=-15, text="<b>🐕 瘦狗产品</b><br>低份额·低增长", 
             showarrow=False, font=dict(size=12, color="#9E9E9E"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#9E9E9E", borderwidth=2),
        dict(x=5.5, y=-15, text="<b>🐄 现金牛产品</b><br>高份额·低增长", 
             showarrow=False, font=dict(size=12, color="#2196F3"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#2196F3", borderwidth=2)
    ]
    
    for ann in annotations:
        fig.add_annotation(**ann)
    
    # 添加产品统计
    total_products = len(product_df)
    fig.add_annotation(
        x=0.5, y=95,
        text=f"<b>共分析 {total_products} 个仪表盘产品</b>",
        showarrow=False,
        font=dict(size=14, color='black'),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black',
        borderwidth=1
    )
    
    # 更新布局
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=20), x=0.5),
        xaxis_title="市场份额 (%)",
        yaxis_title="市场增长率 (%)",
        height=700,
        showlegend=False,
        template="plotly_white",
        xaxis=dict(range=[-0.5, 10.5], showgrid=True, gridcolor='rgba(200,200,200,0.3)'),
        yaxis=dict(range=[-50, 100], showgrid=True, gridcolor='rgba(200,200,200,0.3)'),
        hovermode='closest',
        plot_bgcolor='white'
    )
    
    return fig

def optimize_smart_grid_positions(data, category):
    """智能网格布局优化"""
    # 定义每个象限的范围
    ranges = {
        'star': {'x': (1.5, 10), 'y': (20, 100)},
        'question': {'x': (0, 1.5), 'y': (20, 100)},
        'cow': {'x': (1.5, 10), 'y': (-50, 20)},
        'dog': {'x': (0, 1.5), 'y': (-50, 20)}
    }
    
    x_range = ranges[category]['x']
    y_range = ranges[category]['y']
    
    # 基于真实市场份额和增长率的位置
    x_positions = data['market_share'].values.copy()
    y_positions = data['growth_rate'].values.copy()
    
    # 如果产品太多且位置相近，使用网格分布
    n = len(data)
    if n > 10:  # 当产品多于10个时使用网格
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        
        x_step = (x_range[1] - x_range[0]) / (cols + 1)
        y_step = (y_range[1] - y_range[0]) / (rows + 1)
        
        for i, (idx, row) in enumerate(data.iterrows()):
            grid_row = i // cols
            grid_col = i % cols
            
            # 网格位置加上轻微随机偏移
            x_grid = x_range[0] + (grid_col + 1) * x_step
            y_grid = y_range[0] + (grid_row + 1) * y_step
            
            # 添加随机偏移但保持在合理范围内
            x_offset = np.random.uniform(-x_step*0.3, x_step*0.3)
            y_offset = np.random.uniform(-y_step*0.3, y_step*0.3)
            
            x_positions[i] = max(x_range[0], min(x_range[1], x_grid + x_offset))
            y_positions[i] = max(y_range[0], min(y_range[1], y_grid + y_offset))
    else:
        # 产品较少时，使用力导向算法优化位置
        for _ in range(30):
            for i in range(len(x_positions)):
                for j in range(i+1, len(x_positions)):
                    dx = x_positions[i] - x_positions[j]
                    dy = y_positions[i] - y_positions[j]
                    dist = np.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.8:  # 最小距离
                        force = (0.8 - dist) / 3
                        angle = np.arctan2(dy, dx)
                        x_positions[i] += force * np.cos(angle)
                        y_positions[i] += force * np.sin(angle)
                        x_positions[j] -= force * np.cos(angle)
                        y_positions[j] -= force * np.sin(angle)
                        
                        # 确保不超出象限边界
                        x_positions[i] = max(x_range[0], min(x_range[1], x_positions[i]))
                        y_positions[i] = max(y_range[0], min(y_range[1], y_positions[i]))
                        x_positions[j] = max(x_range[0], min(x_range[1], x_positions[j]))
                        y_positions[j] = max(y_range[0], min(y_range[1], y_positions[j]))
    
    return {'x': x_positions, 'y': y_positions}

def get_strategy_suggestion(category):
    """获取策略建议"""
    strategies = {
        'star': '继续加大投入，保持市场领导地位，扩大竞争优势',
        'question': '选择性投资，识别潜力产品，加快市场渗透',
        'cow': '维持现有投入，最大化利润贡献，为其他产品提供资金',
        'dog': '控制成本，考虑产品升级或逐步退出'
    }
    return strategies.get(category, '')

# 促销活动有效性分析
def analyze_promotion_effectiveness_enhanced(data):
    """增强的促销活动有效性分析"""
    promotion_df = data['promotion_df']
    sales_df = data['sales_df']
    
    # 只分析全国促销活动，去除重复
    national_promotions = promotion_df[promotion_df['所属区域'] == '全国'].drop_duplicates(subset=['产品代码'])
    
    effectiveness_results = []
    
    for _, promo in national_promotions.iterrows():
        product_code = promo['产品代码']
        
        # 计算各个时期的销售数据
        april_2025 = sales_df[(sales_df['发运月份'].dt.year == 2025) & 
                             (sales_df['发运月份'].dt.month == 4) &
                             (sales_df['产品代码'] == product_code)]['销售额'].sum()
        
        march_2025 = sales_df[(sales_df['发运月份'].dt.year == 2025) & 
                             (sales_df['发运月份'].dt.month == 3) &
                             (sales_df['产品代码'] == product_code)]['销售额'].sum()
        
        april_2024 = sales_df[(sales_df['发运月份'].dt.year == 2024) & 
                             (sales_df['发运月份'].dt.month == 4) &
                             (sales_df['产品代码'] == product_code)]['销售额'].sum()
        
        avg_2024 = sales_df[(sales_df['发运月份'].dt.year == 2024) &
                           (sales_df['产品代码'] == product_code)].groupby(
                               sales_df['发运月份'].dt.month)['销售额'].sum().mean()
        
        # 计算增长率
        mom_growth = ((april_2025 - march_2025) / march_2025 * 100) if march_2025 > 0 else 0
        yoy_growth = ((april_2025 - april_2024) / april_2024 * 100) if april_2024 > 0 else 0
        avg_growth = ((april_2025 - avg_2024) / avg_2024 * 100) if avg_2024 > 0 else 0
        
        # 判断有效性
        positive_count = sum([mom_growth > 0, yoy_growth > 0, avg_growth > 0])
        is_effective = positive_count >= 2
        
        effectiveness_results.append({
            'product': promo['促销产品名称'],
            'product_code': product_code,
            'sales': april_2025,
            'is_effective': is_effective,
            'mom_growth': mom_growth,
            'yoy_growth': yoy_growth,
            'avg_growth': avg_growth,
            'positive_count': positive_count,
            'effectiveness_reason': f"{'✅ 有效' if is_effective else '❌ 无效'}（{positive_count}/3项正增长）",
            'march_sales': march_2025,
            'april_2024_sales': april_2024,
            'avg_2024_sales': avg_2024
        })
    
    return pd.DataFrame(effectiveness_results)

# 区域覆盖率分析
def create_regional_coverage_analysis(data):
    """创建更易读的区域产品覆盖率分析"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    regional_stats = []
    regions = sales_df['区域'].unique()
    
    for region in regions:
        region_data = sales_df[sales_df['区域'] == region]
        products_sold = region_data[region_data['产品代码'].isin(dashboard_products)]['产品代码'].nunique()
        total_products = len(dashboard_products)
        coverage_rate = (products_sold / total_products * 100) if total_products > 0 else 0
        
        total_sales = region_data['销售额'].sum()
        dashboard_sales = region_data[region_data['产品代码'].isin(dashboard_products)]['销售额'].sum()
        
        regional_stats.append({
            'region': region,
            'coverage_rate': coverage_rate,
            'products_sold': products_sold,
            'total_products': total_products,
            'total_sales': total_sales,
            'dashboard_sales': dashboard_sales,
            'gap': max(0, 80 - coverage_rate)
        })
    
    df = pd.DataFrame(regional_stats).sort_values('coverage_rate', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['region'],
        x=df['coverage_rate'],
        orientation='h',
        name='覆盖率',
        marker=dict(
            color=df['coverage_rate'].apply(lambda x: '#10b981' if x >= 80 else '#f59e0b' if x >= 60 else '#ef4444'),
            line=dict(width=0)
        ),
        text=[f"{rate:.1f}% ({sold}/{total}产品)" for rate, sold, total in 
              zip(df['coverage_rate'], df['products_sold'], df['total_products'])],
        textposition='inside',
        textfont=dict(color='white', size=12, weight='bold'),
        hovertemplate="""<b>%{y}区域</b><br>
覆盖率: %{x:.1f}%<br>
已覆盖产品: %{customdata[0]}个<br>
总产品数: %{customdata[1]}个<br>
总销售额: ¥%{customdata[2]:,.0f}<br>
仪表盘产品销售额: ¥%{customdata[3]:,.0f}<br>
<extra></extra>""",
        customdata=df[['products_sold', 'total_products', 'total_sales', 'dashboard_sales']].values
    ))
    
    fig.add_vline(x=80, line_dash="dash", line_color="red", 
                 annotation_text="目标: 80%", annotation_position="top")
    
    fig.update_layout(
        title=dict(text="<b>区域产品覆盖率分析</b>", font=dict(size=20)),
        xaxis=dict(title="覆盖率 (%)", range=[0, 105]),
        yaxis=dict(title=""),
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        bargap=0.2
    )
    
    return fig, df

# 产品关联网络图
def create_real_product_network(data):
    """基于真实销售数据创建产品关联网络图"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    product_pairs = []
    
    for prod1, prod2 in combinations(dashboard_products[:20], 2):
        customers_prod1 = set(sales_df_filtered[sales_df_filtered['产品代码'] == prod1]['客户名称'].unique())
        customers_prod2 = set(sales_df_filtered[sales_df_filtered['产品代码'] == prod2]['客户名称'].unique())
        
        common_customers = customers_prod1.intersection(customers_prod2)
        total_customers = customers_prod1.union(customers_prod2)
        
        if len(total_customers) > 0:
            correlation = len(common_customers) / len(total_customers)
            
            if correlation > 0.3:
                name1 = sales_df_filtered[sales_df_filtered['产品代码'] == prod1]['产品简称'].iloc[0] if len(sales_df_filtered[sales_df_filtered['产品代码'] == prod1]) > 0 else prod1
                name2 = sales_df_filtered[sales_df_filtered['产品代码'] == prod2]['产品简称'].iloc[0] if len(sales_df_filtered[sales_df_filtered['产品代码'] == prod2]) > 0 else prod2
                
                product_pairs.append((name1, name2, correlation, len(common_customers)))
    
    nodes = set()
    for pair in product_pairs:
        nodes.add(pair[0])
        nodes.add(pair[1])
    
    nodes = list(nodes)
    
    pos = {}
    angle_step = 2 * np.pi / len(nodes)
    for i, node in enumerate(nodes):
        angle = i * angle_step
        pos[node] = (np.cos(angle), np.sin(angle))
    
    fig = go.Figure()
    
    # 添加边
    for pair in product_pairs:
        x0, y0 = pos[pair[0]]
        x1, y1 = pos[pair[1]]
        
        color_intensity = int(255 * pair[2])
        color = f'rgba({color_intensity}, {100}, {255-color_intensity}, {pair[2]})'
        
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=pair[2]*15, color=color),
            hoverinfo='text',
            text=f"""<b>产品关联分析</b><br>
产品1: {pair[0]}<br>
产品2: {pair[1]}<br>
关联度: {pair[2]:.1%}<br>
共同客户数: {pair[3]}<br>
<br><b>营销洞察:</b><br>
- 这两个产品有{pair[2]:.0%}的客户重叠<br>
- 适合捆绑销售，预计可提升{pair[2]*30:.0f}%销量<br>
- 建议在促销时同时推广<br>
- 可设计组合套装，提高客单价""",
            showlegend=False
        ))
    
    # 添加节点
    node_x = [pos[node][0] for node in nodes]
    node_y = [pos[node][1] for node in nodes]
    
    node_sizes = []
    node_details = []
    for node in nodes:
        connections = sum(1 for pair in product_pairs if node in pair[:2])
        total_correlation = sum(pair[2] for pair in product_pairs if node in pair[:2])
        node_sizes.append(20 + connections * 10)
        
        product_data = sales_df_filtered[sales_df_filtered['产品简称'] == node]
        if len(product_data) > 0:
            total_sales = product_data['销售额'].sum()
            customer_count = product_data['客户名称'].nunique()
        else:
            total_sales = 0
            customer_count = 0
        
        detail = f"""<b>{node}</b><br>
<br><b>网络分析:</b><br>
- 关联产品数: {connections}<br>
- 平均关联度: {total_correlation/connections if connections > 0 else 0:.1%}<br>
- 总销售额: ¥{total_sales:,.0f}<br>
- 客户数: {customer_count}<br>
<br><b>产品定位:</b><br>
{'• 核心产品，适合作为引流主打' if connections >= 5 else 
'• 重要连接点，适合交叉销售' if connections >= 3 else 
'• 特色产品，可独立推广'}<br>
<br><b>策略建议:</b><br>
{'• 作为促销活动的核心产品<br>• 与多个产品组合销售<br>• 重点培养忠实客户' if connections >= 5 else
'• 选择2-3个关联产品捆绑<br>• 开发组合套装<br>• 提升客户粘性' if connections >= 3 else
'• 挖掘独特卖点<br>• 寻找目标客户群<br>• 差异化营销'}"""
        
        node_details.append(detail)
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color='#667eea',
            line=dict(width=2, color='white')
        ),
        text=nodes,
        textposition='top center',
        textfont=dict(size=10, weight='bold'),
        hoverinfo='text',
        hovertext=node_details,
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text="<b>产品关联网络分析</b>", font=dict(size=20)),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        height=700,
        plot_bgcolor='rgba(248,249,250,0.5)',
        hovermode='closest'
    )
    
    return fig

# 促销活动柱状图
def create_optimized_promotion_chart(promo_results):
    """创建优化的促销活动有效性柱状图"""
    if len(promo_results) == 0:
        return None
        
    fig = go.Figure()
    
    colors = ['#10b981' if is_eff else '#ef4444' for is_eff in promo_results['is_effective']]
    
    hover_texts = []
    for _, row in promo_results.iterrows():
        arrow_up = '↑'
        arrow_down = '↓'
        hover_text = f"""<b>{row['product']}</b><br>
<b>4月销售额:</b> ¥{row['sales']:,.0f}<br>
<b>有效性判断:</b> {row['effectiveness_reason']}<br>
<br><b>详细分析:</b><br>
- 3月销售额: ¥{row['march_sales']:,.0f}<br>
- 环比: {arrow_up if row['mom_growth'] > 0 else arrow_down}{abs(row['mom_growth']):.1f}%<br>
- 去年4月: ¥{row['april_2024_sales']:,.0f}<br>
- 同比: {arrow_up if row['yoy_growth'] > 0 else arrow_down}{abs(row['yoy_growth']):.1f}%<br>
- 去年月均: ¥{row['avg_2024_sales']:,.0f}<br>
- 较月均: {arrow_up if row['avg_growth'] > 0 else arrow_down}{abs(row['avg_growth']):.1f}%<br>
<br><b>营销建议:</b><br>
{'继续加大促销力度，扩大市场份额' if row['is_effective'] else '调整促销策略，优化投入产出比'}"""
        hover_texts.append(hover_text)
    
    y_values = promo_results['sales'].values
    x_labels = promo_results['product'].values
    
    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"¥{val:,.0f}" for val in y_values],
        textposition='outside',
        textfont=dict(size=11, weight='bold'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        width=0.6
    ))
    
    effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
    max_sales = y_values.max() if len(y_values) > 0 else 1000
    
    fig.update_layout(
        title=dict(
            text=f"<b>全国促销活动总体有效率: {effectiveness_rate:.1f}%</b> ({promo_results['is_effective'].sum()}/{len(promo_results)})",
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title="促销产品", tickangle=-30 if len(x_labels) > 6 else 0),
        yaxis=dict(title="销售额 (¥)", range=[0, max_sales * 1.3]),
        height=550,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        bargap=0.3
    )
    
    avg_sales = y_values.mean()
    fig.add_hline(
        y=avg_sales, 
        line_dash="dash", 
        line_color="orange",
        annotation_text=f"平均: ¥{avg_sales:,.0f}",
        annotation_position="right"
    )
    
    return fig

# 新增：计算有效产品率
def calculate_effective_products_rate(sales_df, dashboard_products):
    """计算有效产品率（月均销售≥15箱）"""
    # 过滤仪表盘产品
    df = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    
    # 计算每个产品的月均销售箱数
    product_monthly = df.groupby('产品代码').agg({
        '箱数': 'sum',
        '发运月份': 'nunique'
    })
    
    product_monthly['月均箱数'] = product_monthly['箱数'] / product_monthly['发运月份']
    
    # 计算有效产品数
    effective_products = (product_monthly['月均箱数'] >= 15).sum()
    total_products = len(product_monthly)
    
    return (effective_products / total_products * 100) if total_products > 0 else 0

# 新增：有效产品详细分析
def analyze_effective_products(data, dimension='national', selected_region=None):
    """分析有效产品（月均销售≥15箱）"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    # 根据维度过滤数据
    if dimension == 'regional' and selected_region:
        df = sales_df[(sales_df['产品代码'].isin(dashboard_products)) & 
                     (sales_df['区域'] == selected_region)]
    else:
        df = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    
    # 计算每个产品的月均销售
    product_stats = []
    for product in dashboard_products:
        product_data = df[df['产品代码'] == product]
        
        if len(product_data) > 0:
            total_boxes = product_data['箱数'].sum()
            total_sales = product_data['销售额'].sum()
            months_sold = product_data['发运月份'].nunique()
            
            monthly_avg_boxes = total_boxes / months_sold if months_sold > 0 else 0
            is_effective = monthly_avg_boxes >= 15
            
            # 获取产品名称
            product_name = product_data['产品简称'].iloc[0]
            
            product_stats.append({
                'product_code': product,
                'product_name': product_name,
                'total_boxes': total_boxes,
                'total_sales': total_sales,
                'months_sold': months_sold,
                'monthly_avg_boxes': monthly_avg_boxes,
                'is_effective': is_effective,
                'effectiveness_gap': max(0, 15 - monthly_avg_boxes)
            })
    
    return pd.DataFrame(product_stats)

# 新增：创建有效产品分析图表
def create_effective_products_chart(product_df, title="有效产品分析"):
    """创建有效产品分析图表"""
    if len(product_df) == 0:
        return go.Figure()
    
    # 排序：有效产品在前，按月均箱数降序
    product_df = product_df.sort_values(['is_effective', 'monthly_avg_boxes'], 
                                        ascending=[False, False])
    
    # 显示所有产品
    display_df = product_df
    
    colors = ['#10b981' if eff else '#ef4444' for eff in display_df['is_effective']]
    
    fig = go.Figure()
    
    hover_texts = []
    for _, row in display_df.iterrows():
        status = "✅ 有效" if row['is_effective'] else "❌ 无效"
        gap_text = f"距离标准还差: {row['effectiveness_gap']:.1f}箱" if not row['is_effective'] else "超出标准: {row['monthly_avg_boxes']-15:.1f}箱"
        
        hover_text = f"""<b>{row['product_name']} ({row['product_code']})</b><br>
<b>月均销售:</b> {row['monthly_avg_boxes']:.1f}箱<br>
<b>有效性:</b> {status}<br>
<b>{gap_text}</b><br>
<br><b>详细数据:</b><br>
- 总销售箱数: {row['total_boxes']:,.0f}箱<br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 销售月数: {row['months_sold']}个月<br>
<br><b>策略建议:</b><br>
{'继续保持良好势头，可作为主推产品' if row['is_effective'] else '需要加强市场推广，提升销售表现'}"""
        hover_texts.append(hover_text)
    
    fig.add_trace(go.Bar(
        x=display_df['product_name'],
        y=display_df['monthly_avg_boxes'],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{val:.1f}" for val in display_df['monthly_avg_boxes']],
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts
    ))
    
    # 添加有效产品线
    fig.add_hline(y=15, line_dash="dash", line_color="red", 
                 annotation_text="有效产品标准: 15箱/月", 
                 annotation_position="right")
    
    # 计算统计信息
    total_products = len(product_df)
    effective_count = product_df['is_effective'].sum()
    effectiveness_rate = (effective_count / total_products * 100) if total_products > 0 else 0
    
    # 根据产品数量调整图表高度
    chart_height = max(600, 400 + len(display_df) * 15)
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br>有效产品率: {effectiveness_rate:.1f}% ({effective_count}/{total_products})",
            font=dict(size=20),
            x=0.5
        ),
        xaxis=dict(title="产品名称", tickangle=-45),
        yaxis=dict(title="月均销售 (箱)", range=[0, max(display_df['monthly_avg_boxes'].max() * 1.2, 20)]),
        height=chart_height,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        bargap=0.2
    )
    
    return fig, effectiveness_rate

# 主页面
def main():
    st.markdown("""
    <div class="main-header">
        <h1>📦 产品组合分析</h1>
        <p>基于真实销售数据的智能分析系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    data = load_data()
    if data is None:
        return
    
    # 创建标签页
    tab_names = [
        "📊 产品情况总览",
        "🎯 BCG产品矩阵", 
        "🚀 全国促销活动有效性",
        "📈 星品新品达成",
        "🔗 市场网络与覆盖分析"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 产品情况总览 - 4个卡片/行布局
    with tabs[0]:
        metrics = calculate_comprehensive_metrics(data)
        
        # 第一行：4个卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 将销售额转换为更简洁的格式
            sales_display = metrics['total_sales']
            if sales_display >= 10000:
                sales_text = f"¥{sales_display/10000:.1f}万"
            else:
                sales_text = f"¥{sales_display:.0f}"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{sales_text}</div>
                <div class="metric-label">💰 2025年总销售额</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#10b981' if metrics['jbp_status'] == 'YES' else '#ef4444'}">
                    {metrics['jbp_status']}
                </div>
                <div class="metric-label">✅ JBP符合度</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['penetration_rate']:.0f}%</div>
                <div class="metric-label">📊 新品渗透率</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['promo_effectiveness']:.0f}%</div>
                <div class="metric-label">🚀 全国促销有效性</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第二行：4个卡片
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['new_ratio']:.0f}%</div>
                <div class="metric-label">🌟 新品占比</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['star_ratio']:.0f}%</div>
                <div class="metric-label">⭐ 星品占比</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            status_color = '#10b981' if metrics['total_ratio'] >= 20 else '#ef4444'
            status_text = "✅ 达标" if metrics['total_ratio'] >= 20 else "❌ 未达标"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_ratio']:.0f}%</div>
                <div class="metric-label" style="font-size: 0.95rem;">🎯 星品&新品占比</div>
                <div style="color: {status_color}; font-size: 0.85rem; margin-top: 0.5rem;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['effective_products_rate']:.0f}%</div>
                <div class="metric-label">📦 有效产品率</div>
                <div class="metric-sublabel">月均≥15箱</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第三行：有效产品相关指标（居中显示2个）
        col_empty1, col9, col10, col_empty2 = st.columns([1, 2, 2, 1])
        
        with col9:
            st.markdown(f"""
            <div class="metric-card" style="animation-delay: 0.9s;">
                <div class="metric-value">{metrics['effective_products_count']}</div>
                <div class="metric-label">✅ 有效产品数</div>
                <div class="metric-sublabel">月均≥15箱</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col10:
            st.markdown(f"""
            <div class="metric-card" style="animation-delay: 1.0s;">
                <div class="metric-value">{metrics['avg_effective_sales']:.0f}箱</div>
                <div class="metric-label">📈 有效产品月均</div>
                <div class="metric-sublabel">平均销售量</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 2: BCG产品矩阵
    with tabs[1]:
        # 选择维度控件
        bcg_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True, key="bcg_dimension")
        
        # 获取分析数据
        if bcg_dimension == "🌏 全国维度":
            product_analysis = create_bcg_matrix(data, 'national')
            title = "BCG产品矩阵"
            selected_region = None
        else:
            regions = data['sales_df']['区域'].unique()
            selected_region = st.selectbox("🗺️ 选择区域", regions)
            product_analysis = create_bcg_matrix(data, 'regional', selected_region)
            title = f"{selected_region}区域 BCG产品矩阵"
        
        # 显示BCG矩阵图表
        if len(product_analysis) > 0:
            fig = plot_bcg_matrix(product_analysis, title=title)
            st.plotly_chart(fig, use_container_width=True)
            
            # JBP符合度分析
            total_sales = product_analysis['sales'].sum()
            cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
            star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
            dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()
            
            cow_ratio = cow_sales / total_sales * 100 if total_sales > 0 else 0
            star_question_ratio = star_question_sales / total_sales * 100 if total_sales > 0 else 0
            dog_ratio = dog_sales / total_sales * 100 if total_sales > 0 else 0
            
            region_prefix = f"{selected_region}区域 " if bcg_dimension == "🗺️ 分区域维度" else ""
            
            with st.expander(f"📊 {region_prefix}JBP符合度分析", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("现金牛产品占比", f"{cow_ratio:.1f}%", 
                             "✅ 符合" if 45 <= cow_ratio <= 50 else "❌ 不符合",
                             delta_color="normal" if 45 <= cow_ratio <= 50 else "inverse")
                    st.caption("目标: 45%-50%")
                
                with col2:
                    st.metric("明星&问号产品占比", f"{star_question_ratio:.1f}%",
                             "✅ 符合" if 40 <= star_question_ratio <= 45 else "❌ 不符合",
                             delta_color="normal" if 40 <= star_question_ratio <= 45 else "inverse")
                    st.caption("目标: 40%-45%")
                
                with col3:
                    st.metric("瘦狗产品占比", f"{dog_ratio:.1f}%",
                             "✅ 符合" if dog_ratio <= 10 else "❌ 不符合",
                             delta_color="normal" if dog_ratio <= 10 else "inverse")
                    st.caption("目标: ≤10%")
        else:
            st.warning("该区域暂无产品数据")
    
    # Tab 3: 全国促销活动有效性
    with tabs[2]:
        promo_results = analyze_promotion_effectiveness_enhanced(data)
        
        if len(promo_results) > 0:
            # 计算有效率并显示在标题中
            effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
            
            # 促销活动效果图表
            st.markdown(f"""
            <div class="promo-header">
                <h2>🚀 全国促销活动有效性分析</h2>
                <h3>总体有效率: {effectiveness_rate:.1f}% ({promo_results['is_effective'].sum()}/{len(promo_results)})</h3>
            </div>
            """, unsafe_allow_html=True)
            
            fig = create_optimized_promotion_chart(promo_results)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 促销洞察分析
            with st.expander("💡 促销活动深度洞察", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    effective_products = promo_results[promo_results['is_effective'] == True]
                    ineffective_products = promo_results[promo_results['is_effective'] == False]
                    
                    st.info(f"""
                    **🎯 有效促销产品特征**
                    - 有效产品数: {len(effective_products)}个
                    - 平均销售额: ¥{effective_products['sales'].mean():,.0f}
                    - 环比增长率: {effective_products['mom_growth'].mean():.1f}%
                    - 同比增长率: {effective_products['yoy_growth'].mean():.1f}%
                    """)
                
                with col2:
                    st.warning(f"""
                    **⚠️ 无效促销产品分析**
                    - 无效产品数: {len(ineffective_products)}个
                    - 平均销售额: ¥{ineffective_products['sales'].mean():,.0f}
                    - 环比增长率: {ineffective_products['mom_growth'].mean():.1f}%
                    - 同比增长率: {ineffective_products['yoy_growth'].mean():.1f}%
                    """)
        else:
            st.info("暂无全国促销活动数据")
    
    # Tab 4: 星品新品达成
    with tabs[3]:
        # 选择控件
        view_type = st.radio("选择分析视角", ["按区域", "按销售员", "趋势分析"], horizontal=True, key="star_new_view")
        
        sales_df = data['sales_df']
        star_products = data['star_products']
        new_products = data['new_products']
        star_new_products = list(set(star_products + new_products))
        
        if view_type == "按区域":
            # 区域分析
            region_stats = []
            for region in sales_df['区域'].unique():
                region_data = sales_df[sales_df['区域'] == region]
                total_sales = region_data['销售额'].sum()
                star_new_sales = region_data[region_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                total_customers = region_data['客户名称'].nunique()
                star_new_customers = region_data[region_data['产品代码'].isin(star_new_products)]['客户名称'].nunique()
                
                region_stats.append({
                    'region': region,
                    'ratio': ratio,
                    'achieved': ratio >= 20,
                    'total_sales': total_sales,
                    'star_new_sales': star_new_sales,
                    'customers': f"{star_new_customers}/{total_customers}",
                    'penetration': star_new_customers / total_customers * 100 if total_customers > 0 else 0
                })
            
            region_df = pd.DataFrame(region_stats)
            
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in region_df['achieved']]
            
            hover_texts = []
            for _, row in region_df.iterrows():
                hover_text = f"""<b>{row['region']}</b><br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>达成情况:</b> {'✅ 已达标' if row['achieved'] else '❌ 未达标'}<br>
<br><b>销售分析:</b><br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
- 覆盖客户: {row['customers']}<br>
- 客户渗透率: {row['penetration']:.1f}%<br>
<br><b>行动建议:</b><br>
{'继续保持，可作为其他区域标杆' if row['achieved'] else f"距离目标还差{20-row['ratio']:.1f}%，需重点提升"}"""
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Bar(
                x=region_df['region'],
                y=region_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in region_df['ratio']],
                textposition='outside',
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))
            
            fig.add_hline(y=20, line_dash="dash", line_color="red", 
                         annotation_text="目标线 20%", annotation_position="right")
            
            fig.update_layout(
                title="各区域星品&新品占比达成情况",
                xaxis_title="销售区域",
                yaxis_title="占比 (%)",
                height=500,
                showlegend=False,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif view_type == "按销售员":
            # 销售员分析
            salesperson_stats = []
            for person in sales_df['销售员'].unique():
                person_data = sales_df[sales_df['销售员'] == person]
                total_sales = person_data['销售额'].sum()
                star_new_sales = person_data[person_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                total_customers = person_data['客户名称'].nunique()
                star_new_customers = person_data[person_data['产品代码'].isin(star_new_products)]['客户名称'].nunique()
                
                salesperson_stats.append({
                    'salesperson': person,
                    'ratio': ratio,
                    'achieved': ratio >= 20,
                    'total_sales': total_sales,
                    'star_new_sales': star_new_sales,
                    'customers': f"{star_new_customers}/{total_customers}",
                    'region': person_data['区域'].mode().iloc[0] if len(person_data) > 0 else ''
                })
            
            person_df = pd.DataFrame(salesperson_stats).sort_values('ratio', ascending=False)
            
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in person_df['achieved']]
            
            hover_texts = []
            for _, row in person_df.iterrows():
                hover_text = f"""<b>{row['salesperson']}</b><br>
<b>所属区域:</b> {row['region']}<br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>达成情况:</b> {'✅ 已达标' if row['achieved'] else '❌ 未达标'}<br>
<br><b>销售分析:</b><br>
- 总销售额: ¥{row['total_sales']:,.0f}<br>
- 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
- 覆盖客户: {row['customers']}<br>
<br><b>绩效建议:</b><br>
{'优秀销售员，可分享经验' if row['achieved'] else '需要培训和支持，提升产品知识'}"""
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Bar(
                x=person_df['salesperson'],
                y=person_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in person_df['ratio']],
                textposition='outside',
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))
            
            fig.add_hline(y=20, line_dash="dash", line_color="red", 
                         annotation_text="目标线 20%", annotation_position="right")
            
            fig.update_layout(
                title=f"全部销售员星品&新品占比达成情况（共{len(person_df)}人）",
                xaxis_title="销售员",
                yaxis_title="占比 (%)",
                height=600,
                showlegend=False,
                hovermode='closest',
                xaxis={'tickangle': -45}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            achieved_count = person_df['achieved'].sum()
            st.info(f"📊 达成率统计：{achieved_count}/{len(person_df)}人达标（{achieved_count/len(person_df)*100:.1f}%）")
        
        else:  # 趋势分析
            # 趋势分析
            monthly_stats = []
            
            for month in pd.date_range(start='2024-01', end='2025-04', freq='M'):
                month_data = sales_df[
                    (sales_df['发运月份'].dt.year == month.year) & 
                    (sales_df['发运月份'].dt.month == month.month)
                ]
                
                if len(month_data) > 0:
                    total_sales = month_data['销售额'].sum()
                    star_new_sales = month_data[month_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                    ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                    
                    monthly_stats.append({
                        'month': month.strftime('%Y-%m'),
                        'ratio': ratio,
                        'total_sales': total_sales,
                        'star_new_sales': star_new_sales
                    })
            
            trend_df = pd.DataFrame(monthly_stats)
            
            fig = go.Figure()
            
            hover_texts = []
            for _, row in trend_df.iterrows():
                hover_text = f"""<b>{row['month']}</b><br>
<b>占比:</b> {row['ratio']:.1f}%<br>
<b>总销售额:</b> ¥{row['total_sales']:,.0f}<br>
<b>星品新品销售额:</b> ¥{row['star_new_sales']:,.0f}<br>
<br><b>趋势分析:</b><br>
{'保持良好势头' if row['ratio'] >= 20 else '需要加强推广'}"""
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=trend_df['month'],
                y=trend_df['ratio'],
                mode='lines+markers',
                name='星品&新品占比',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            ))
            
            fig.add_hline(y=20, line_dash="dash", line_color="red", 
                         annotation_text="目标线 20%", annotation_position="right")
            
            fig.update_layout(
                title="星品&新品占比月度趋势",
                xaxis_title="月份",
                yaxis_title="占比 (%)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: 市场网络与覆盖分析
    with tabs[4]:
        # 选择控件
        analysis_type = st.radio("选择分析类型", ["🔗 产品关联网络", "📍 区域覆盖分析", "✅ 有效产品分析"], horizontal=True, key="market_analysis_type")
        
        if analysis_type == "🔗 产品关联网络":
            # 产品关联网络
            st.subheader("产品关联网络分析")
            
            # 创建基于真实数据的2D网络图
            network_fig = create_real_product_network(data)
            st.plotly_chart(network_fig, use_container_width=True)
            
            # 关联分析洞察
            with st.expander("💡 产品关联营销策略", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("""
                    **🎯 关联分析价值**
                    - 识别经常一起购买的产品组合
                    - 发现交叉销售机会
                    - 优化产品组合策略
                    - 提升客户购买体验
                    """)
                
                with col2:
                    st.success("""
                    **📈 应用建议**
                    - 将高关联产品打包销售
                    - 在促销时同时推广关联产品
                    - 基于关联度设计货架陈列
                    - 开发新的组合套装产品
                    """)
        
        elif analysis_type == "📍 区域覆盖分析":
            # 区域覆盖分析
            # 创建更易读的区域覆盖率分析
            fig, coverage_df = create_regional_coverage_analysis(data)
            st.plotly_chart(fig, use_container_width=True)
            
            # 覆盖率分析洞察
            col1, col2 = st.columns(2)
            
            with col1:
                avg_coverage = coverage_df['coverage_rate'].mean()
                st.metric("平均覆盖率", f"{avg_coverage:.1f}%", 
                         "整体表现良好" if avg_coverage >= 70 else "需要提升")
                
                low_coverage_regions = coverage_df[coverage_df['coverage_rate'] < 80]
                if len(low_coverage_regions) > 0:
                    st.warning(f"⚠️ 有{len(low_coverage_regions)}个区域低于80%目标线")
            
            with col2:
                # 漏铺市机会分析
                total_gap = coverage_df['gap'].sum()
                if total_gap > 0:
                    potential_products = int(total_gap * len(data['dashboard_products']) / 100)
                    st.info(f"""
                    **📈 漏铺市机会**
                    - 总体覆盖缺口: {total_gap:.0f}%
                    - 潜在可增产品: 约{potential_products}个
                    - 建议优先开发覆盖率最低的区域
                    """)
                else:
                    st.success("✅ 所有区域覆盖率均达到80%以上")
        
        else:  # 有效产品分析
            st.subheader("有效产品分析（月均销售≥15箱）")
            
            # 选择维度
            eff_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True, key="eff_dimension")
            
            if eff_dimension == "🌏 全国维度":
                product_analysis = analyze_effective_products(data, 'national')
                title = "全国有效产品分析"
            else:
                regions = data['sales_df']['区域'].unique()
                selected_region = st.selectbox("选择区域", regions)
                product_analysis = analyze_effective_products(data, 'regional', selected_region)
                title = f"{selected_region}区域有效产品分析"
            
            if len(product_analysis) > 0:
                fig, effectiveness_rate = create_effective_products_chart(product_analysis, title)
                st.plotly_chart(fig, use_container_width=True)
                
                # 策略建议
                with st.expander("💡 有效产品策略建议", expanded=True):
                    effective_products = product_analysis[product_analysis['is_effective'] == True]
                    ineffective_products = product_analysis[product_analysis['is_effective'] == False]
                    
                    st.info(f"""
                    **📋 策略建议**
                    - 有效产品（{len(effective_products)}个）：继续保持良好销售势头，可作为主推产品
                    - 接近标准产品：月均销售10-15箱的产品，稍加推广即可达标
                    - 低效产品：月均销售低于10箱的产品，需要重新评估市场定位
                    - 区域差异：不同区域的有效产品可能不同，需因地制宜
                    """)
            else:
                st.warning("暂无产品数据")

if __name__ == "__main__":
    main()
