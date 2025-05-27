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

# 增强的CSS样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 增强的指标卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
        animation: slideUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102,126,234,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s;
        opacity: 0;
    }
    
    .metric-card:hover::before {
        animation: shimmer 0.6s ease-in-out;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* 标签页样式增强 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    /* 动画卡片延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    
    /* 修复数字重影 */
    text {
        text-rendering: optimizeLegibility;
    }
    
    /* BCG矩阵特效 */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* JBP分析卡片动画 */
    @keyframes cardFlip {
        0% { transform: rotateY(0deg); }
        50% { transform: rotateY(10deg); }
        100% { transform: rotateY(0deg); }
    }
    
    .jbp-card {
        animation: cardFlip 3s ease-in-out infinite;
        transform-style: preserve-3d;
        perspective: 1000px;
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
    
    # KPI达成率
    kpi_rate = (total_ratio / 20 * 100) if total_ratio > 0 else 0
    
    # 新品渗透率
    total_customers = sales_2025['客户名称'].nunique()
    new_customers = sales_2025[sales_2025['产品代码'].isin(new_products)]['客户名称'].nunique()
    penetration_rate = (new_customers / total_customers * 100) if total_customers > 0 else 0
    
    # BCG分析 - 计算JBP符合度
    current_year = sales_df['发运月份'].dt.year.max()
    current_data = sales_df[sales_df['发运月份'].dt.year == current_year]
    current_data = current_data[current_data['产品代码'].isin(dashboard_products)]
    
    product_analysis = analyze_product_bcg_comprehensive(current_data, dashboard_products)
    
    total_bcg_sales = product_analysis['sales'].sum()
    cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
    star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
    
    cow_ratio = cow_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0
    star_question_ratio = star_question_sales / total_bcg_sales * 100 if total_bcg_sales > 0 else 0
    
    jbp_status = 'YES' if (45 <= cow_ratio <= 50 and 40 <= star_question_ratio <= 45) else 'NO'
    
    return {
        'total_sales': total_sales,
        'star_ratio': star_ratio,
        'new_ratio': new_ratio,
        'total_ratio': total_ratio,
        'kpi_rate': kpi_rate,
        'penetration_rate': penetration_rate,
        'jbp_status': jbp_status
    }

# 增强的BCG矩阵分析 - 显示所有仪表盘产品
def create_enhanced_bcg_matrix(data, dimension='national', selected_region=None):
    """创建增强的BCG矩阵分析"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    # 确保只分析仪表盘产品
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    
    if dimension == 'national':
        product_analysis = analyze_product_bcg_comprehensive(sales_df_filtered, dashboard_products)
        fig = plot_modern_bcg_matrix_enhanced(product_analysis)
        return fig, product_analysis
    else:
        # 分区域维度BCG分析
        if selected_region:
            region_data = sales_df_filtered[sales_df_filtered['区域'] == selected_region]
            region_analysis = analyze_product_bcg_comprehensive(region_data, dashboard_products)
            fig = plot_modern_bcg_matrix_enhanced(region_analysis, title=f"{selected_region}区域")
            return fig, region_analysis
        return None, None

def analyze_product_bcg_comprehensive(sales_df, dashboard_products):
    """分析产品BCG矩阵数据，包括所有仪表盘产品"""
    current_year = sales_df['发运月份'].dt.year.max()
    current_data = sales_df[sales_df['发运月份'].dt.year == current_year]
    prev_data = sales_df[sales_df['发运月份'].dt.year == current_year - 1]
    
    product_stats = []
    total_sales = current_data['销售额'].sum()
    
    # 确保分析所有仪表盘产品
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
            product_name = product  # 如果没有名称，使用代码
        
        market_share = (current_sales / total_sales * 100) if total_sales > 0 else 0
        
        # 计算增长率
        if prev_sales > 0:
            growth_rate = ((current_sales - prev_sales) / prev_sales * 100)
        elif current_sales > 0:
            growth_rate = 100  # 新产品
        else:
            growth_rate = 0
        
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
            'growth_rate': growth_rate,
            'sales': current_sales,
            'prev_sales': prev_sales,
            'category': category,
            'category_reason': reason,
            'calculation_detail': f"当前销售额: ¥{current_sales:,.0f}\n去年销售额: ¥{prev_sales:,.0f}\n市场份额: {market_share:.2f}%\n增长率: {growth_rate:.1f}%"
        })
    
    return pd.DataFrame(product_stats)

def plot_modern_bcg_matrix_enhanced(product_df, title="BCG产品矩阵"):
    """绘制增强的BCG矩阵图，避免气泡遮挡"""
    fig = go.Figure()
    
    # 定义象限颜色
    quadrant_colors = {
        'star': 'rgba(255, 235, 153, 0.5)',
        'question': 'rgba(255, 153, 153, 0.5)',
        'cow': 'rgba(204, 235, 255, 0.5)',
        'dog': 'rgba(230, 230, 230, 0.5)'
    }
    
    # 圆点颜色
    bubble_colors = {
        'star': '#FFC107',
        'question': '#F44336',
        'cow': '#2196F3',
        'dog': '#9E9E9E'
    }
    
    # 添加象限背景
    fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=100,
                  fillcolor=quadrant_colors['question'], 
                  line=dict(width=0), layer="below")
    
    fig.add_shape(type="rect", x0=1.5, y0=20, x1=10, y1=100,
                  fillcolor=quadrant_colors['star'], 
                  line=dict(width=0), layer="below")
    
    fig.add_shape(type="rect", x0=0, y0=-50, x1=1.5, y1=20,
                  fillcolor=quadrant_colors['dog'], 
                  line=dict(width=0), layer="below")
    
    fig.add_shape(type="rect", x0=1.5, y0=-50, x1=10, y1=20,
                  fillcolor=quadrant_colors['cow'], 
                  line=dict(width=0), layer="below")
    
    # 类别名称映射
    category_names = {
        'star': '⭐ 明星产品',
        'question': '❓ 问号产品',
        'cow': '🐄 现金牛产品',
        'dog': '🐕 瘦狗产品'
    }
    
    # 绘制产品气泡，改进位置算法避免遮挡
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            # 更智能的防重叠算法
            positions = optimize_bubble_positions(cat_data)
            
            # 设置气泡大小
            sizes = cat_data['sales'].apply(lambda x: max(min(np.sqrt(x)/25, 80), 30))
            
            # 创建hover文本
            hover_texts = []
            for _, row in cat_data.iterrows():
                category_name = category_names.get(category, category)
                hover_text = f"""<b>{row['name']} ({row['product']})</b><br>
<br><b>分类：{category_name}</b><br>
<br><b>分类原因：</b><br>{row['category_reason']}<br>
<br><b>详细计算：</b><br>{row['calculation_detail']}<br>
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
                textfont=dict(size=9, color='white', weight='bold'),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts,
                showlegend=False
            ))
    
    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", 
                 opacity=0.5, line_width=2)
    
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", 
                 opacity=0.5, line_width=2)
    
    # 添加文字标注
    annotations = [
        dict(x=0.75, y=60, text="<b>❓ 问号产品</b><br>低份额·高增长", 
             showarrow=False, font=dict(size=13, color="#F44336"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#F44336", 
             borderwidth=2, borderpad=4),
        
        dict(x=5.5, y=60, text="<b>⭐ 明星产品</b><br>高份额·高增长", 
             showarrow=False, font=dict(size=13, color="#FFC107"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#FFC107", 
             borderwidth=2, borderpad=4),
        
        dict(x=0.75, y=-15, text="<b>🐕 瘦狗产品</b><br>低份额·低增长", 
             showarrow=False, font=dict(size=13, color="#9E9E9E"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#9E9E9E", 
             borderwidth=2, borderpad=4),
        
        dict(x=5.5, y=-15, text="<b>🐄 现金牛产品</b><br>高份额·低增长", 
             showarrow=False, font=dict(size=13, color="#2196F3"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#2196F3", 
             borderwidth=2, borderpad=4)
    ]
    
    for ann in annotations:
        fig.add_annotation(**ann)
    
    # 添加产品总数统计
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
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="市场份额 (%)",
        yaxis_title="市场增长率 (%)",
        height=700,
        showlegend=False,
        template="plotly_white",
        xaxis=dict(
            range=[-0.5, 10.5],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[-50, 100],
            showgrid=False,
            zeroline=False
        ),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def optimize_bubble_positions(data):
    """优化气泡位置，避免重叠"""
    x_positions = data['market_share'].values.copy()
    y_positions = data['growth_rate'].values.copy()
    
    # 使用力导向算法避免重叠
    for _ in range(50):  # 迭代优化
        for i in range(len(x_positions)):
            for j in range(i+1, len(x_positions)):
                dx = x_positions[i] - x_positions[j]
                dy = y_positions[i] - y_positions[j]
                dist = np.sqrt(dx**2 + dy**2)
                
                if dist < 0.5:  # 如果太近
                    # 斥力
                    force = (0.5 - dist) / 2
                    angle = np.arctan2(dy, dx)
                    x_positions[i] += force * np.cos(angle)
                    y_positions[i] += force * np.sin(angle)
                    x_positions[j] -= force * np.cos(angle)
                    y_positions[j] -= force * np.sin(angle)
    
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

# 增强的促销活动有效性分析（去除重复）
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
        
        # 详细的有效性原因
        reasons = []
        if mom_growth > 0:
            reasons.append(f"环比增长{mom_growth:.1f}%")
        else:
            reasons.append(f"环比下降{abs(mom_growth):.1f}%")
            
        if yoy_growth > 0:
            reasons.append(f"同比增长{yoy_growth:.1f}%")
        else:
            reasons.append(f"同比下降{abs(yoy_growth):.1f}%")
            
        if avg_growth > 0:
            reasons.append(f"比去年均值增长{avg_growth:.1f}%")
        else:
            reasons.append(f"比去年均值下降{abs(avg_growth):.1f}%")
        
        effectiveness_results.append({
            'product': promo['促销产品名称'],
            'product_code': product_code,
            'sales': april_2025,
            'is_effective': is_effective,
            'mom_growth': mom_growth,
            'yoy_growth': yoy_growth,
            'avg_growth': avg_growth,
            'positive_count': positive_count,
            'reasons': reasons,
            'effectiveness_reason': f"{'✅ 有效' if is_effective else '❌ 无效'}（{positive_count}/3项正增长）",
            'detail_reason': '；'.join(reasons),
            'march_sales': march_2025,
            'april_2024_sales': april_2024,
            'avg_2024_sales': avg_2024
        })
    
    return pd.DataFrame(effectiveness_results)

# 创建更易读的区域覆盖率分析图
def create_regional_coverage_analysis(data):
    """创建更易读的区域产品覆盖率分析"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    # 计算每个区域的产品覆盖情况
    regional_stats = []
    regions = sales_df['区域'].unique()
    
    for region in regions:
        region_data = sales_df[sales_df['区域'] == region]
        
        # 该区域销售的仪表盘产品数
        products_sold = region_data[region_data['产品代码'].isin(dashboard_products)]['产品代码'].nunique()
        total_products = len(dashboard_products)
        coverage_rate = (products_sold / total_products * 100) if total_products > 0 else 0
        
        # 该区域总销售额
        total_sales = region_data['销售额'].sum()
        dashboard_sales = region_data[region_data['产品代码'].isin(dashboard_products)]['销售额'].sum()
        
        regional_stats.append({
            'region': region,
            'coverage_rate': coverage_rate,
            'products_sold': products_sold,
            'total_products': total_products,
            'total_sales': total_sales,
            'dashboard_sales': dashboard_sales,
            'gap': max(0, 80 - coverage_rate)  # 与80%目标的差距
        })
    
    df = pd.DataFrame(regional_stats).sort_values('coverage_rate', ascending=True)
    
    # 创建水平条形图
    fig = go.Figure()
    
    # 添加实际覆盖率条形
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
    
    # 添加目标线
    fig.add_vline(x=80, line_dash="dash", line_color="red", 
                 annotation_text="目标: 80%", annotation_position="top")
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text="<b>区域产品覆盖率分析</b><br><sub>各区域仪表盘产品覆盖情况</sub>",
            font=dict(size=20)
        ),
        xaxis=dict(
            title="覆盖率 (%)",
            range=[0, 105],
            tickformat='.0f'
        ),
        yaxis=dict(title=""),
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        bargap=0.2
    )
    
    return fig, df

# 创建3D产品关联网络图
def create_3d_product_network(data):
    """基于真实销售数据创建3D产品关联网络图"""
    sales_df = data['sales_df']
    dashboard_products = data['dashboard_products']
    
    # 只分析仪表盘产品
    sales_df_filtered = sales_df[sales_df['产品代码'].isin(dashboard_products)]
    
    # 计算产品关联度（基于共同客户购买）
    product_pairs = []
    
    # 限制显示前15个产品以保证3D效果清晰
    products_to_analyze = dashboard_products[:15]
    
    for prod1, prod2 in combinations(products_to_analyze, 2):
        # 找出同时购买这两个产品的客户
        customers_prod1 = set(sales_df_filtered[sales_df_filtered['产品代码'] == prod1]['客户名称'].unique())
        customers_prod2 = set(sales_df_filtered[sales_df_filtered['产品代码'] == prod2]['客户名称'].unique())
        
        common_customers = customers_prod1.intersection(customers_prod2)
        total_customers = customers_prod1.union(customers_prod2)
        
        if len(total_customers) > 0:
            correlation = len(common_customers) / len(total_customers)
            
            if correlation > 0.3:  # 只显示关联度大于30%的
                # 获取产品名称
                name1 = sales_df_filtered[sales_df_filtered['产品代码'] == prod1]['产品简称'].iloc[0] if len(sales_df_filtered[sales_df_filtered['产品代码'] == prod1]) > 0 else prod1
                name2 = sales_df_filtered[sales_df_filtered['产品代码'] == prod2]['产品简称'].iloc[0] if len(sales_df_filtered[sales_df_filtered['产品代码'] == prod2]) > 0 else prod2
                
                product_pairs.append((name1, name2, correlation, len(common_customers)))
    
    # 构建节点列表
    nodes = set()
    for pair in product_pairs:
        nodes.add(pair[0])
        nodes.add(pair[1])
    
    nodes = list(nodes)
    
    # 创建3D节点位置
    n_nodes = len(nodes)
    pos_3d = {}
    
    # 使用球形分布
    for i, node in enumerate(nodes):
        theta = 2 * np.pi * i / n_nodes
        phi = np.pi * (i + 1) / (n_nodes + 1)
        
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        
        pos_3d[node] = (x, y, z)
    
    fig = go.Figure()
    
    # 添加3D边
    for pair in product_pairs:
        x0, y0, z0 = pos_3d[pair[0]]
        x1, y1, z1 = pos_3d[pair[1]]
        
        # 边的颜色和宽度根据关联度
        color_intensity = int(255 * pair[2])
        color = f'rgba({color_intensity}, {100}, {255-color_intensity}, {pair[2]})'
        
        # 创建曲线边
        t = np.linspace(0, 1, 20)
        # 添加一些曲率
        mid_x = (x0 + x1) / 2 + 0.2 * np.sin(pair[2] * np.pi)
        mid_y = (y0 + y1) / 2 + 0.2 * np.cos(pair[2] * np.pi)
        mid_z = (z0 + z1) / 2 + 0.2
        
        x_curve = x0 * (1-t)**2 + 2 * mid_x * t * (1-t) + x1 * t**2
        y_curve = y0 * (1-t)**2 + 2 * mid_y * t * (1-t) + y1 * t**2
        z_curve = z0 * (1-t)**2 + 2 * mid_z * t * (1-t) + z1 * t**2
        
        fig.add_trace(go.Scatter3d(
            x=x_curve, y=y_curve, z=z_curve,
            mode='lines',
            line=dict(width=pair[2]*20, color=color),
            hoverinfo='text',
            text=f"""<b>产品关联分析</b><br>
产品1: {pair[0]}<br>
产品2: {pair[1]}<br>
关联度: {pair[2]:.1%}<br>
共同客户数: {pair[3]}<br>
<br><b>营销洞察:</b><br>
• 这两个产品有{pair[2]:.0%}的客户重叠<br>
• 适合捆绑销售，预计可提升{pair[2]*30:.0f}%销量<br>
• 建议在促销时同时推广<br>
• 可设计组合套装，提高客单价""",
            showlegend=False
        ))
    
    # 添加3D节点
    node_x = [pos_3d[node][0] for node in nodes]
    node_y = [pos_3d[node][1] for node in nodes]
    node_z = [pos_3d[node][2] for node in nodes]
    
    # 计算节点重要性（基于连接数）
    node_sizes = []
    node_colors = []
    node_details = []
    
    for node in nodes:
        connections = sum(1 for pair in product_pairs if node in pair[:2])
        total_correlation = sum(pair[2] for pair in product_pairs if node in pair[:2])
        node_sizes.append(20 + connections * 5)
        node_colors.append(connections)
        
        # 获取产品销售数据
        product_data = sales_df_filtered[sales_df_filtered['产品简称'] == node]
        if len(product_data) > 0:
            total_sales = product_data['销售额'].sum()
            customer_count = product_data['客户名称'].nunique()
        else:
            total_sales = 0
            customer_count = 0
        
        detail = f"""<b>{node}</b><br>
<br><b>网络分析:</b><br>
• 关联产品数: {connections}<br>
• 平均关联度: {total_correlation/connections if connections > 0 else 0:.1%}<br>
• 总销售额: ¥{total_sales:,.0f}<br>
• 客户数: {customer_count}<br>
<br><b>产品定位:</b><br>
{'• 核心产品，适合作为引流主打' if connections >= 5 else 
'• 重要连接点，适合交叉销售' if connections >= 3 else 
'• 特色产品，可独立推广'}<br>
<br><b>策略建议:</b><br>
{'• 作为促销活动的核心产品<br>• 与多个产品组合销售<br>• 重点培养忠实客户' if connections >= 5 else
'• 选择2-3个关联产品捆绑<br>• 开发组合套装<br>• 提升客户粘性' if connections >= 3 else
'• 挖掘独特卖点<br>• 寻找目标客户群<br>• 差异化营销'}"""
        
        node_details.append(detail)
    
    fig.add_trace(go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='连接数'),
            line=dict(width=2, color='white')
        ),
        text=nodes,
        textposition='top center',
        textfont=dict(size=10, color='black', weight='bold'),
        hoverinfo='text',
        hovertext=node_details,
        showlegend=False
    ))
    
    # 更新3D布局
    fig.update_layout(
        title=dict(
            text="<b>3D产品关联网络分析</b><br><sub>基于客户购买行为的产品关联度</sub>",
            font=dict(size=20)
        ),
        scene=dict(
            xaxis=dict(showgrid=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, showticklabels=False, title=''),
            zaxis=dict(showgrid=False, showticklabels=False, title=''),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='cube'
        ),
        height=700,
        hovermode='closest'
    )
    
    return fig

# 创建优化的促销活动柱状图
def create_optimized_promotion_chart(promo_results):
    """创建优化的促销活动有效性柱状图"""
    if len(promo_results) == 0:
        return None
        
    fig = go.Figure()
    
    # 根据有效性设置颜色
    colors = []
    for is_eff in promo_results['is_effective']:
        colors.append('#10b981' if is_eff else '#ef4444')
    
    # 创建详细的hover文本
    hover_texts = []
    for _, row in promo_results.iterrows():
        arrow_up = '↑'
        arrow_down = '↓'
        hover_text = f"""<b>{row['product']}</b><br>
<b>4月销售额:</b> ¥{row['sales']:,.0f}<br>
<b>有效性判断:</b> {row['effectiveness_reason']}<br>
<br><b>详细分析:</b><br>
• 3月销售额: ¥{row['march_sales']:,.0f}<br>
• 环比: {arrow_up if row['mom_growth'] > 0 else arrow_down}{abs(row['mom_growth']):.1f}%<br>
• 去年4月: ¥{row['april_2024_sales']:,.0f}<br>
• 同比: {arrow_up if row['yoy_growth'] > 0 else arrow_down}{abs(row['yoy_growth']):.1f}%<br>
• 去年月均: ¥{row['avg_2024_sales']:,.0f}<br>
• 较月均: {arrow_up if row['avg_growth'] > 0 else arrow_down}{abs(row['avg_growth']):.1f}%<br>
<br><b>营销建议:</b><br>
{'继续加大促销力度，扩大市场份额' if row['is_effective'] else '调整促销策略，优化投入产出比'}"""
        hover_texts.append(hover_text)
    
    # 为避免文字重叠，调整数据显示
    y_values = promo_results['sales'].values
    x_labels = promo_results['product'].values
    
    # 创建柱状图
    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        text=[f"¥{val:,.0f}" for val in y_values],
        textposition='outside',
        textfont=dict(size=11, weight='bold'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        width=0.6
    ))
    
    effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
    
    # 计算合适的Y轴范围
    max_sales = y_values.max() if len(y_values) > 0 else 1000
    y_range_max = max_sales * 1.3
    
    fig.update_layout(
        title=dict(
            text=f"<b>全国促销活动总体有效率: {effectiveness_rate:.1f}%</b> ({promo_results['is_effective'].sum()}/{len(promo_results)})",
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="促销产品",
            tickangle=-30 if len(x_labels) > 6 else 0,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title="销售额 (¥)",
            range=[0, y_range_max],
            gridcolor='rgba(200,200,200,0.3)',
            zerolinecolor='rgba(200,200,200,0.5)'
        ),
        height=550,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        bargap=0.3,
        margin=dict(t=100, b=100)
    )
    
    # 添加平均线
    avg_sales = y_values.mean()
    fig.add_hline(
        y=avg_sales, 
        line_dash="dash", 
        line_color="orange",
        annotation_text=f"平均: ¥{avg_sales:,.0f}",
        annotation_position="right"
    )
    
    return fig

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
    
    # Tab 1: 产品情况总览
    with tabs[0]:
        metrics = calculate_comprehensive_metrics(data)
        
        # 第一行卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">¥{metrics['total_sales']:,.0f}</div>
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
                <div class="metric-value">{metrics['kpi_rate']:.1f}%</div>
                <div class="metric-label">🎯 KPI达成率</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['penetration_rate']:.1f}%</div>
                <div class="metric-label">📊 新品渗透率</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 第二行卡片
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['new_ratio']:.1f}%</div>
                <div class="metric-label">🌟 新品占比</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['star_ratio']:.1f}%</div>
                <div class="metric-label">⭐ 星品占比</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            status_color = '#10b981' if metrics['total_ratio'] >= 20 else '#ef4444'
            status_text = "✅ 达标" if metrics['total_ratio'] >= 20 else "❌ 未达标"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_ratio']:.1f}%</div>
                <div class="metric-label">🎯 星品&新品总占比</div>
                <div style="color: {status_color}; font-size: 0.9rem; margin-top: 0.5rem;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            promo_results = analyze_promotion_effectiveness_enhanced(data)
            effectiveness = (promo_results['is_effective'].sum() / len(promo_results) * 100) if len(promo_results) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{effectiveness:.1f}%</div>
                <div class="metric-label">🚀 全国促销有效性</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 2: BCG产品矩阵
    with tabs[1]:
        bcg_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True)
        
        if bcg_dimension == "🌏 全国维度":
            fig, product_analysis = create_enhanced_bcg_matrix(data, 'national')
            st.plotly_chart(fig, use_container_width=True)
            
            # JBP符合度分析
            total_sales = product_analysis['sales'].sum()
            cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
            star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
            dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()
            
            cow_ratio = cow_sales / total_sales * 100 if total_sales > 0 else 0
            star_question_ratio = star_question_sales / total_sales * 100 if total_sales > 0 else 0
            dog_ratio = dog_sales / total_sales * 100 if total_sales > 0 else 0
            
            with st.expander("📊 JBP符合度分析", expanded=True):
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
        
        else:  # 分区域维度
            regions = data['sales_df']['区域'].unique()
            selected_region = st.selectbox("选择区域", regions)
            
            if selected_region:
                fig, product_analysis = create_enhanced_bcg_matrix(data, 'regional', selected_region)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 该区域的JBP符合度分析
                    total_sales = product_analysis['sales'].sum()
                    cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
                    star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
                    dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()
                    
                    cow_ratio = cow_sales / total_sales * 100 if total_sales > 0 else 0
                    star_question_ratio = star_question_sales / total_sales * 100 if total_sales > 0 else 0
                    dog_ratio = dog_sales / total_sales * 100 if total_sales > 0 else 0
                    
                    with st.expander(f"📊 {selected_region}区域 JBP符合度分析", expanded=True):
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
    
    # Tab 3: 全国促销活动有效性
    with tabs[2]:
        promo_results = analyze_promotion_effectiveness_enhanced(data)
        
        if len(promo_results) > 0:
            fig = create_optimized_promotion_chart(promo_results)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无全国促销活动数据")
    
    # Tab 4: 星品新品达成
    with tabs[3]:
        view_type = st.radio("选择分析视角", ["按区域", "按销售员", "趋势分析"], horizontal=True)
        
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
• 总销售额: ¥{row['total_sales']:,.0f}<br>
• 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
• 覆盖客户: {row['customers']}<br>
• 客户渗透率: {row['penetration']:.1f}%<br>
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
• 总销售额: ¥{row['total_sales']:,.0f}<br>
• 星品新品销售额: ¥{row['star_new_sales']:,.0f}<br>
• 覆盖客户: {row['customers']}<br>
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
        analysis_type = st.radio("选择分析类型", ["🔗 3D产品关联网络", "📍 区域覆盖分析"], horizontal=True)
        
        if analysis_type == "🔗 3D产品关联网络":
            st.subheader("3D产品关联网络分析")
            
            # 创建基于真实数据的3D网络图
            network_fig = create_3d_product_network(data)
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
        
        else:  # 区域覆盖分析
            st.subheader("区域产品覆盖率分析")
            
            # 创建更易读的区域覆盖率分析
            fig, coverage_df = create_regional_coverage_analysis(data)
            st.plotly_chart(fig, use_container_width=True)
            
            # 覆盖率分析
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

if __name__ == "__main__":
    main()
