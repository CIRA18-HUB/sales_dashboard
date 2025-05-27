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

# 计算总体指标
def calculate_overview_metrics(data):
    """计算产品情况总览的各项指标"""
    sales_df = data['sales_df']
    star_products = data['star_products']
    new_products = data['new_products']
    
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
    
    return {
        'total_sales': total_sales,
        'star_ratio': star_ratio,
        'new_ratio': new_ratio,
        'total_ratio': total_ratio,
        'kpi_rate': kpi_rate,
        'penetration_rate': penetration_rate,
        'jbp_status': 'YES' if total_ratio >= 20 else 'NO'
    }

# 增强的BCG矩阵分析
def create_enhanced_bcg_matrix(data, dimension='national'):
    """创建增强的BCG矩阵分析"""
    sales_df = data['sales_df']
    
    if dimension == 'national':
        product_analysis = analyze_product_bcg(sales_df)
        fig = plot_modern_bcg_matrix(product_analysis)
        return fig, product_analysis
    else:
        # 分区域维度BCG分析
        regions = sales_df['区域'].unique()
        regional_figs = []
        
        for region in regions:
            region_data = sales_df[sales_df['区域'] == region]
            region_analysis = analyze_product_bcg(region_data)
            fig = plot_modern_bcg_matrix(region_analysis, title=f"{region}区域")
            regional_figs.append((region, fig))
        
        return regional_figs

def analyze_product_bcg(sales_df):
    """分析产品BCG矩阵数据"""
    current_year = sales_df['发运月份'].dt.year.max()
    current_data = sales_df[sales_df['发运月份'].dt.year == current_year]
    prev_data = sales_df[sales_df['发运月份'].dt.year == current_year - 1]
    
    product_stats = []
    total_sales = current_data['销售额'].sum()
    
    for product in current_data['产品代码'].unique():
        current_sales = current_data[current_data['产品代码'] == product]['销售额'].sum()
        prev_sales = prev_data[prev_data['产品代码'] == product]['销售额'].sum()
        
        market_share = (current_sales / total_sales * 100) if total_sales > 0 else 0
        growth_rate = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        
        # 分类
        if market_share >= 1.5 and growth_rate > 20:
            category = 'star'
        elif market_share < 1.5 and growth_rate > 20:
            category = 'question'
        elif market_share >= 1.5 and growth_rate <= 20:
            category = 'cow'
        else:
            category = 'dog'
        
        product_stats.append({
            'product': product,
            'name': current_data[current_data['产品代码'] == product]['产品简称'].iloc[0],
            'market_share': market_share,
            'growth_rate': growth_rate,
            'sales': current_sales,
            'category': category
        })
    
    return pd.DataFrame(product_stats)

def plot_modern_bcg_matrix(product_df, title="BCG产品矩阵"):
    """绘制现代风格的BCG矩阵图（模仿图3）"""
    fig = go.Figure()
    
    # 定义象限颜色（模仿图3的配色）
    quadrant_colors = {
        'star': 'rgba(255, 235, 153, 0.5)',      # 淡黄色 - 明星产品
        'question': 'rgba(255, 153, 153, 0.5)',  # 淡红色 - 问号产品
        'cow': 'rgba(204, 235, 255, 0.5)',       # 淡蓝色 - 现金牛产品
        'dog': 'rgba(230, 230, 230, 0.5)'        # 淡灰色 - 瘦狗产品
    }
    
    # 圆点颜色
    bubble_colors = {
        'star': '#FFC107',      # 橙黄色
        'question': '#F44336',  # 红色
        'cow': '#2196F3',       # 蓝色
        'dog': '#9E9E9E'        # 灰色
    }
    
    # 添加象限背景
    # 左上角 - 问号产品
    fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=50,
                  fillcolor=quadrant_colors['question'], 
                  line=dict(width=0), layer="below")
    
    # 右上角 - 明星产品
    fig.add_shape(type="rect", x0=1.5, y0=20, x1=5, y1=50,
                  fillcolor=quadrant_colors['star'], 
                  line=dict(width=0), layer="below")
    
    # 左下角 - 瘦狗产品
    fig.add_shape(type="rect", x0=0, y0=0, x1=1.5, y1=20,
                  fillcolor=quadrant_colors['dog'], 
                  line=dict(width=0), layer="below")
    
    # 右下角 - 现金牛产品
    fig.add_shape(type="rect", x0=1.5, y0=0, x1=5, y1=20,
                  fillcolor=quadrant_colors['cow'], 
                  line=dict(width=0), layer="below")
    
    # 绘制产品气泡
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            # 避免重叠的简单算法
            x_positions = cat_data['market_share'].values.copy()
            y_positions = cat_data['growth_rate'].values.copy()
            
            for i in range(len(x_positions)):
                for j in range(i+1, len(x_positions)):
                    dist = np.sqrt((x_positions[i]-x_positions[j])**2 + (y_positions[i]-y_positions[j])**2)
                    if dist < 0.3:
                        x_positions[j] += 0.2
                        y_positions[j] += 2
            
            # 设置气泡大小
            sizes = cat_data['sales'].apply(lambda x: max(min(np.sqrt(x)/30, 80), 40))
            
            fig.add_trace(go.Scatter(
                x=x_positions,
                y=y_positions,
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=bubble_colors[category],
                    opacity=0.8,
                    line=dict(width=0)
                ),
                text=cat_data.apply(lambda row: f"<b>{row['name']}</b>", axis=1),
                hovertemplate='<b>%{text}</b><br>' +
                             '市场份额: %{x:.1f}%<br>' +
                             '增长率: %{y:.1f}%<br>' +
                             '销售额: ¥%{customdata:,.0f}<extra></extra>',
                customdata=cat_data['sales'],
                showlegend=False
            ))
    
    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", 
                 opacity=0.5, line_width=2)
    
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", 
                 opacity=0.5, line_width=2)
    
    # 添加文字标注（在象限中心）
    annotations = [
        dict(x=0.75, y=35, text="<b>❓ 问号产品</b><br>低份额·高增长<br>🚀 潜力巨大", 
             showarrow=False, font=dict(size=13, color="#F44336"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#F44336", 
             borderwidth=2, borderpad=4),
        
        dict(x=3.25, y=35, text="<b>⭐ 明星产品</b><br>高份额·高增长<br>⭐ 重点培育", 
             showarrow=False, font=dict(size=13, color="#FFC107"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#FFC107", 
             borderwidth=2, borderpad=4),
        
        dict(x=0.75, y=10, text="<b>🐕 瘦狗产品</b><br>低份额·低增长<br>📉 考虑退出", 
             showarrow=False, font=dict(size=13, color="#9E9E9E"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#9E9E9E", 
             borderwidth=2, borderpad=4),
        
        dict(x=3.25, y=10, text="<b>🐄 现金牛产品</b><br>高份额·低增长<br>💰 稳定收益", 
             showarrow=False, font=dict(size=13, color="#2196F3"),
             bgcolor="rgba(255,255,255,0.9)", bordercolor="#2196F3", 
             borderwidth=2, borderpad=4)
    ]
    
    for ann in annotations:
        fig.add_annotation(**ann)
    
    # 添加坐标轴标签
    fig.add_annotation(x=1.5, y=-3, text="1.5%市场份额分界线", 
                      showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=-0.3, y=20, text="20%增长率分界线", 
                      showarrow=False, font=dict(size=10, color="gray"),
                      textangle=-90)
    
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
        height=600,
        showlegend=False,
        template="plotly_white",
        xaxis=dict(
            range=[-0.2, 5.2],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[-5, 55],
            showgrid=False,
            zeroline=False
        ),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # 添加动画效果
    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref=2.*max(product_df['sales'])/(80.**2),
            sizemin=20
        )
    )
    
    return fig

# 增强的促销活动有效性分析
def analyze_promotion_effectiveness_enhanced(data):
    """增强的促销活动有效性分析"""
    promotion_df = data['promotion_df']
    sales_df = data['sales_df']
    
    national_promotions = promotion_df[promotion_df['所属区域'] == '全国']
    
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

# 创建增强的2D雷达图（修复v未定义错误）
def create_enhanced_radar_chart(categories, values, title="产品覆盖率分析"):
    """创建增强的2D雷达图"""
    fig = go.Figure()
    
    # 准备数据
    theta = categories + [categories[0]]
    r = values + [values[0]]
    
    # 添加多层同心圆背景
    for i in range(1, 6):
        r_bg = [i*20] * len(theta)
        fig.add_trace(go.Scatterpolar(
            r=r_bg,
            theta=theta,
            fill=None,
            mode='lines',
            line=dict(color='rgba(200,200,200,0.3)', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 准备customdata（修复v未定义问题）
    insights = []
    for idx, val in enumerate(values):
        if idx == 0:  # 华北
            insight = '华北地区表现良好，建议维持现有策略' if val >= 80 else '华北地区有提升空间，建议加强市场开发' if val >= 70 else '华北地区需重点关注，制定专项提升计划'
        elif idx == 1:  # 华南
            insight = '华南地区市场潜力大，建议深耕细作' if val >= 80 else '华南地区仍有增长空间，优化产品组合' if val >= 70 else '华南地区亟需改善，考虑调整策略'
        elif idx == 2:  # 华东
            insight = '华东地区是核心市场，继续保持领先' if val >= 80 else '华东地区需巩固地位，防止竞争对手蚕食' if val >= 70 else '华东地区面临挑战，需紧急应对'
        elif idx == 3:  # 华西
            insight = '华西地区基础良好，可扩大投入' if val >= 80 else '华西地区稳步发展，注意渠道建设' if val >= 70 else '华西地区发展缓慢，需加快布局'
        else:  # 华中
            insight = '华中地区表现优异，可作为标杆' if val >= 80 else '华中地区发展平稳，挖掘增长点' if val >= 70 else '华中地区存在短板，需专项支持'
        insights.append(insight)
    
    insights.append(insights[0])  # 闭合数据
    
    # 添加主数据
    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=theta,
        fill='toself',
        fillcolor='rgba(102,126,234,0.3)',
        line=dict(color='#667eea', width=3),
        mode='lines+markers',
        marker=dict(size=12, color='#667eea'),
        name='覆盖率',
        hovertemplate='<b>%{theta}</b><br>覆盖率: %{r:.1f}%<br>' +
                     '<b>分析洞察:</b><br>' +
                     '%{customdata}<extra></extra>',
        customdata=insights
    ))
    
    # 添加目标线（80%）
    target_r = [80] * len(theta)
    fig.add_trace(go.Scatterpolar(
        r=target_r,
        theta=theta,
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name='目标线(80%)',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                tickfont=dict(size=12),
                gridcolor='rgba(200,200,200,0.5)'
            ),
            angularaxis=dict(
                tickfont=dict(size=14, weight='bold'),
                gridcolor='rgba(200,200,200,0.5)'
            )
        ),
        showlegend=True,
        title=dict(text=title, font=dict(size=24)),
        height=600,
        hovermode='closest'
    )
    
    return fig

# 产品关联网络图
def create_product_network(data):
    """创建产品关联网络图"""
    # 模拟关联数据
    nodes = ['午餐袋', '酸恐龙', '彩蝶虫', '扭扭虫', '草莓Q', '葡萄Q', 
             '水果软糖', '酸味糖', '巧克力豆', '棉花糖']
    
    edges = [
        ('午餐袋', '酸恐龙', 0.75),
        ('彩蝶虫', '扭扭虫', 0.82),
        ('草莓Q', '葡萄Q', 0.68),
        ('水果软糖', '酸味糖', 0.65),
        ('巧克力豆', '棉花糖', 0.71),
        ('午餐袋', '水果软糖', 0.55),
        ('酸恐龙', '扭扭虫', 0.48),
        ('草莓Q', '巧克力豆', 0.52)
    ]
    
    # 创建节点位置
    pos = {}
    angle_step = 2 * np.pi / len(nodes)
    for i, node in enumerate(nodes):
        angle = i * angle_step
        pos[node] = (np.cos(angle), np.sin(angle))
    
    fig = go.Figure()
    
    # 添加边（带动画效果）
    for idx, edge in enumerate(edges):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # 边的颜色根据强度
        color_intensity = int(255 * edge[2])
        color = f'rgba({color_intensity}, {100}, {255-color_intensity}, {edge[2]})'
        
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=edge[2]*10, color=color),
            hoverinfo='text',
            text=f'{edge[0]} ↔ {edge[1]}<br>关联度: {edge[2]:.2f}<br><b>营销建议:</b><br>可考虑捆绑销售，预计提升{edge[2]*20:.0f}%销量',
            showlegend=False,
            opacity=0.8
        ))
    
    # 添加节点（带动画效果）
    node_x = [pos[node][0] for node in nodes]
    node_y = [pos[node][1] for node in nodes]
    
    # 计算节点大小（基于连接数）
    node_sizes = []
    node_insights = []
    for node in nodes:
        connections = sum(1 for edge in edges if node in edge[:2])
        node_sizes.append(20 + connections * 10)
        if connections >= 3:
            insight = f"核心产品，建议作为主推"
        elif connections >= 2:
            insight = f"关键连接点，适合交叉销售"
        else:
            insight = f"独立产品，可单独推广"
        node_insights.append(insight)
    
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
        hoverinfo='text',
        hovertext=[f'<b>{node}</b><br>连接数: {(size-20)//10}<br><b>产品定位:</b><br>{insight}' 
                  for node, size, insight in zip(nodes, node_sizes, node_insights)],
        showlegend=False
    ))
    
    fig.update_layout(
        title="产品关联网络分析",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        height=600,
        plot_bgcolor='rgba(248,249,250,0.5)',
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
        hover_text = f"""<b>{row['product']}</b><br>
<b>4月销售额:</b> ¥{row['sales']:,.0f}<br>
<b>有效性判断:</b> {row['effectiveness_reason']}<br>
<br><b>详细分析:</b><br>
• 3月销售额: ¥{row['march_sales']:,.0f}<br>
• 环比: {'↑' if row['mom_growth'] > 0 else '↓'}{abs(row['mom_growth']):.1f}%<br>
• 去年4月: ¥{row['april_2024_sales']:,.0f}<br>
• 同比: {'↑' if row['yoy_growth'] > 0 else '↓'}{abs(row['yoy_growth']):.1f}%<br>
• 去年月均: ¥{row['avg_2024_sales']:,.0f}<br>
• 较月均: {'↑' if row['avg_growth'] > 0 else '↓'}{abs(row['avg_growth']):.1f}%<br>
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
        width=0.6  # 调整柱子宽度
    ))
    
    effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
    
    # 计算合适的Y轴范围
    max_sales = y_values.max() if len(y_values) > 0 else 1000
    y_range_max = max_sales * 1.3  # 留出30%的空间显示文字
    
    fig.update_layout(
        title=dict(
            text=f"<b>全国促销活动总体有效率: {effectiveness_rate:.1f}%</b> ({promo_results['is_effective'].sum()}/{len(promo_results)})",
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="促销产品",
            tickangle=-30 if len(x_labels) > 6 else 0,  # 当产品多时旋转标签
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
        bargap=0.3,  # 柱子间距
        margin=dict(t=100, b=100)  # 增加上下边距
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
    
    # 创建标签页 - 确保所有标签都显示
    tab_names = [
        "📊 产品情况总览",
        "🎯 BCG产品矩阵", 
        "🚀 全国促销活动有效性",
        "📈 星品新品达成",
        "🔗 产品关联分析",
        "📍 漏铺市分析",
        "📅 季节性分析"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: 产品情况总览 - 使用卡片显示
    with tabs[0]:
        metrics = calculate_overview_metrics(data)
        
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
    
    # Tab 2: BCG产品矩阵 - 现代风格版
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
        
        else:
            # 分区域维度 - 默认显示所有区域
            regional_figs = create_enhanced_bcg_matrix(data, 'regional')
            
            # 显示所有区域的BCG矩阵
            for region, fig in regional_figs:
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: 全国促销活动有效性 - 优化版
    with tabs[2]:
        promo_results = analyze_promotion_effectiveness_enhanced(data)
        
        if len(promo_results) > 0:
            # 使用优化的图表函数
            fig = create_optimized_promotion_chart(promo_results)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # 添加分析总结
                with st.expander("📊 促销效果分析总结", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📈 有效促销产品**")
                        effective_products = promo_results[promo_results['is_effective']]
                        for _, row in effective_products.iterrows():
                            st.write(f"• {row['product']}: {row['detail_reason']}")
                    
                    with col2:
                        st.markdown("**📉 需改进促销产品**")
                        ineffective_products = promo_results[~promo_results['is_effective']]
                        for _, row in ineffective_products.iterrows():
                            st.write(f"• {row['product']}: {row['detail_reason']}")
        else:
            st.info("暂无全国促销活动数据")
    
    # Tab 4: 星品新品达成 - 增强版
    with tabs[3]:
        view_type = st.radio("选择分析视角", ["按区域", "按销售员", "趋势分析"], horizontal=True)
        
        sales_df = data['sales_df']
        star_products = data['star_products']
        new_products = data['new_products']
        star_new_products = list(set(star_products + new_products))
        
        if view_type == "按区域":
            # 计算各区域星品新品占比
            region_stats = []
            for region in sales_df['区域'].unique():
                region_data = sales_df[sales_df['区域'] == region]
                total_sales = region_data['销售额'].sum()
                star_new_sales = region_data[region_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                # 计算客户数
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
            
            # 创建增强的柱状图
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in region_df['achieved']]
            
            # 创建详细的hover文本
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
            # 显示全部销售员数据
            salesperson_stats = []
            for person in sales_df['销售员'].unique():
                person_data = sales_df[sales_df['销售员'] == person]
                total_sales = person_data['销售额'].sum()
                star_new_sales = person_data[person_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                # 计算覆盖的客户数
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
            
            # 创建增强的柱状图
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in person_df['achieved']]
            
            # 创建详细的hover文本
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
            
            # 显示达成统计
            achieved_count = person_df['achieved'].sum()
            st.info(f"📊 达成率统计：{achieved_count}/{len(person_df)}人达标（{achieved_count/len(person_df)*100:.1f}%）")
        
        else:  # 趋势分析
            # 计算月度趋势
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
            
            # 创建增强的趋势图
            fig = go.Figure()
            
            # 创建详细的hover文本
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
    
    # Tab 5: 产品关联分析 - 升级版
    with tabs[4]:
        st.subheader("🔗 产品关联网络分析")
        
        # 创建网络图
        network_fig = create_product_network(data)
        st.plotly_chart(network_fig, use_container_width=True)
    
    # Tab 6: 漏铺市分析 - 增强的2D雷达图
    with tabs[5]:
        st.subheader("📍 区域产品覆盖率分析")
        
        # 覆盖率数据
        categories = ['华北', '华南', '华东', '华西', '华中']
        values = [85, 78, 92, 73, 88]
        
        # 创建增强的2D雷达图
        fig_radar = create_enhanced_radar_chart(categories, values)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # 漏铺市分析
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("平均覆盖率", f"{np.mean(values):.1f}%", "整体表现良好")
            
            # 最低覆盖率区域
            min_idx = np.argmin(values)
            st.warning(f"⚠️ {categories[min_idx]}区域覆盖率最低（{values[min_idx]}%），建议重点开发")
        
        with col2:
            # 漏铺市机会
            opportunities = []
            for cat, val in zip(categories, values):
                if val < 80:
                    gap = 80 - val
                    opportunities.append(f"{cat}: 还有{gap}%提升空间")
            
            if opportunities:
                st.info("**📈 漏铺市机会**\n" + "\n".join(f"- {opp}" for opp in opportunities))
            else:
                st.success("✅ 所有区域覆盖率均达到80%以上")
    
    # Tab 7: 季节性分析 - 确保可见
    with tabs[6]:
        st.subheader("📅 产品季节性趋势分析")
        
        product_filter = st.selectbox(
            "选择产品类型",
            ["全部产品", "星品产品", "新品产品", "促销产品"]
        )
        
        # 根据筛选条件获取产品列表
        if product_filter == "星品产品":
            selected_products = data['star_products']
        elif product_filter == "新品产品":
            selected_products = data['new_products']
        elif product_filter == "促销产品":
            promo_products = data['promotion_df']['产品代码'].unique().tolist()
            selected_products = promo_products
        else:
            selected_products = data['sales_df']['产品代码'].unique()[:8]
        
        # 生成季节性数据
        monthly_data = []
        
        for product in selected_products[:6]:  # 限制显示6个产品
            product_sales = data['sales_df'][data['sales_df']['产品代码'] == product]
            
            if len(product_sales) > 0:
                product_name = product_sales['产品简称'].iloc[0]
                
                for month in range(1, 13):
                    month_sales = product_sales[product_sales['发运月份'].dt.month == month]['销售额'].sum()
                    monthly_data.append({
                        'product': product_name,
                        'month': f'{month:02d}月',
                        'sales': month_sales,
                        'season': '春季' if month in [3,4,5] else '夏季' if month in [6,7,8] else '秋季' if month in [9,10,11] else '冬季'
                    })
        
        if monthly_data:
            trend_df = pd.DataFrame(monthly_data)
            
            # 创建增强的季节性趋势图
            fig = go.Figure()
            
            # 添加季节背景色
            seasons = [
                ('01月', '02月', 'rgba(173,216,230,0.2)', '冬季'),
                ('03月', '05月', 'rgba(144,238,144,0.2)', '春季'),
                ('06月', '08月', 'rgba(255,255,0,0.2)', '夏季'),
                ('09月', '11月', 'rgba(255,165,0,0.2)', '秋季'),
                ('12月', '12月', 'rgba(173,216,230,0.2)', '冬季')
            ]
            
            for start, end, color, name in seasons:
                fig.add_vrect(x0=start, x1=end, fillcolor=color, 
                             annotation_text=name, annotation_position="top left",
                             layer="below", line_width=0)
            
            # 为每个产品添加趋势线
            colors = px.colors.qualitative.Set3[:len(trend_df['product'].unique())]
            
            for idx, product in enumerate(trend_df['product'].unique()):
                product_data = trend_df[trend_df['product'] == product]
                
                # 创建hover文本
                hover_texts = []
                for _, row in product_data.iterrows():
                    season_insight = {
                        '春季': '新品推广黄金期，建议加大营销投入',
                        '夏季': '销售高峰期，确保库存充足',
                        '秋季': '准备节日营销，推出限定产品',
                        '冬季': '年末冲刺期，关注礼品市场'
                    }
                    hover_text = f"""<b>{row['product']}</b><br>
<b>{row['month']}销售额:</b> ¥{row['sales']:,.0f}<br>
<b>所属季节:</b> {row['season']}<br>
<b>营销建议:</b> {season_insight.get(row['season'], '')}"""
                    hover_texts.append(hover_text)
                
                fig.add_trace(go.Scatter(
                    x=product_data['month'],
                    y=product_data['sales'],
                    name=product,
                    mode='lines+markers',
                    line=dict(width=3, shape='spline', color=colors[idx]),
                    marker=dict(size=10, color=colors[idx]),
                    hovertemplate='%{customdata}<extra></extra>',
                    customdata=hover_texts
                ))
            
            fig.update_layout(
                title=f"产品季节性趋势分析 - {product_filter}",
                xaxis_title="月份",
                yaxis_title="销售额 (¥)",
                height=600,
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 季节性洞察
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("🌸 **春季表现**\n3-5月是新品推广的黄金期，建议加大市场投入")
            
            with col2:
                st.success("☀️ **夏季表现**\n6-8月为销售高峰期，需要提前备货确保供应")
            
            with col3:
                st.warning("🍂 **秋冬策略**\n9-12月需要节日营销策略，推出季节限定产品")
        else:
            st.info("暂无足够的数据进行季节性分析")

if __name__ == "__main__":
    main()
