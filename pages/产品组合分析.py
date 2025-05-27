# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import time
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit_lottie as st_lottie
import requests
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide"
)

# Lottie动画加载函数
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# 加载动画资源
lottie_product = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json")
lottie_chart = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")
lottie_success = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_lzhv1mc4.json")

# 高级CSS样式
st.markdown("""
<style>
    /* 渐变背景动画 */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 主标题动画 */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin-bottom: 2rem;
        animation: slideDown 1s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px rgba(102, 126, 234, 0.5); }
        to { text-shadow: 0 0 20px rgba(102, 126, 234, 0.8), 0 0 30px rgba(102, 126, 234, 0.6); }
    }
    
    /* 指标卡片3D效果 */
    .metric-card-3d {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.6s;
        cursor: pointer;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .metric-card-3d:hover {
        transform: rotateY(10deg) rotateX(10deg) scale(1.05);
    }
    
    /* 图表容器动画 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 1s ease-out;
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
    
    .chart-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* 标签页增强样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 0.8rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 30px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        border: none;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3); }
        50% { box-shadow: 0 5px 30px rgba(102, 126, 234, 0.5); }
        100% { box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3); }
    }
    
    /* 悬浮提示框美化 */
    .hoverlabel {
        background: rgba(0, 0, 0, 0.9) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        font-size: 14px !important;
    }
    
    /* 进度条动画 */
    .progress-bar {
        height: 30px;
        background: #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        position: relative;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        animation: progressAnimation 2s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .progress-fill::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes progressAnimation {
        from { width: 0; }
    }
</style>
""", unsafe_allow_html=True)

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

# 动态指标卡片组件
def create_animated_metric(title, value, subtitle, icon, color_scheme):
    """创建动画指标卡片"""
    with stylable_container(
        key=f"metric_{title}",
        css_styles=f"""
        {{
            background: linear-gradient(135deg, {color_scheme[0]} 0%, {color_scheme[1]} 100%);
            border-radius: 20px;
            padding: 2rem;
            color: white;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        {{
            &:hover {{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }}
        }}
        """
    ):
        st.markdown(f"""
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
                {value}
            </div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.3rem;">
                {title}
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                {subtitle}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 创建高级BCG矩阵
def create_advanced_bcg_matrix(product_df):
    """创建增强版BCG矩阵，包含详细悬停信息"""
    fig = go.Figure()
    
    colors = {
        'star': '#22c55e',
        'question': '#f59e0b',
        'cow': '#3b82f6',
        'dog': '#94a3b8'
    }
    
    symbols = {
        'star': 'star',
        'question': 'circle',
        'cow': 'square',
        'dog': 'diamond'
    }
    
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            # 计算详细信息
            hover_text = []
            for _, row in cat_data.iterrows():
                info = f"""
                <b>{row['name']}</b><br>
                ━━━━━━━━━━━━━━━<br>
                📊 市场份额: {row['market_share']:.2f}%<br>
                📈 增长率: {row['growth_rate']:.1f}%<br>
                💰 销售额: ¥{row['sales']:,.0f}<br>
                📦 产品代码: {row['product']}<br>
                🏷️ 分类: {{'star': '明星产品', 'question': '问号产品', 
                         'cow': '现金牛', 'dog': '瘦狗产品'}[category]}<br>
                ━━━━━━━━━━━━━━━<br>
                💡 <b>策略建议:</b><br>
                {get_strategy_suggestion(category, row['market_share'], row['growth_rate'])}
                """
                hover_text.append(info)
            
            fig.add_trace(go.Scatter(
                x=cat_data['market_share'],
                y=cat_data['growth_rate'],
                mode='markers+text',
                name={'star': '⭐ 明星', 'question': '❓ 问号', 
                      'cow': '🐄 现金牛', 'dog': '🐕 瘦狗'}[category],
                marker=dict(
                    size=cat_data['sales'].apply(lambda x: max(min(np.sqrt(x)/40, 100), 30)),
                    color=colors[category],
                    symbol=symbols[category],
                    opacity=0.8,
                    line=dict(width=3, color='white')
                ),
                text=cat_data['name'].apply(lambda x: x[:10]),
                textposition='middle center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                hovertext=hover_text,
                hoverinfo='text',
                hoverlabel=dict(
                    bgcolor='rgba(0, 0, 0, 0.9)',
                    bordercolor='white',
                    font=dict(size=14, color='white')
                )
            ))
    
    # 添加象限背景
    x_mid = 1.5
    y_mid = 20
    x_max = product_df['market_share'].max() * 1.2
    y_max = product_df['growth_rate'].max() * 1.2
    y_min = product_df['growth_rate'].min() - 5
    
    # 象限背景颜色
    fig.add_shape(type="rect", x0=0, y0=y_mid, x1=x_mid, y1=y_max,
                  fillcolor="rgba(245, 158, 11, 0.1)", line=dict(width=0))
    fig.add_shape(type="rect", x0=x_mid, y0=y_mid, x1=x_max, y1=y_max,
                  fillcolor="rgba(34, 197, 94, 0.1)", line=dict(width=0))
    fig.add_shape(type="rect", x0=0, y0=y_min, x1=x_mid, y1=y_mid,
                  fillcolor="rgba(148, 163, 184, 0.1)", line=dict(width=0))
    fig.add_shape(type="rect", x0=x_mid, y0=y_min, x1=x_max, y1=y_mid,
                  fillcolor="rgba(59, 130, 246, 0.1)", line=dict(width=0))
    
    # 添加分割线
    fig.add_hline(y=y_mid, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=x_mid, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 添加动态标注
    annotations = [
        dict(x=x_mid/2, y=y_max-5, text="<b>问号产品区</b><br>高增长·低份额<br>需要投资决策", 
             showarrow=False, font=dict(size=12), bgcolor="rgba(255,255,255,0.8)", bordercolor="#f59e0b"),
        dict(x=x_mid+(x_max-x_mid)/2, y=y_max-5, text="<b>明星产品区</b><br>高增长·高份额<br>重点培育发展", 
             showarrow=False, font=dict(size=12), bgcolor="rgba(255,255,255,0.8)", bordercolor="#22c55e"),
        dict(x=x_mid/2, y=y_min+5, text="<b>瘦狗产品区</b><br>低增长·低份额<br>考虑淘汰退出", 
             showarrow=False, font=dict(size=12), bgcolor="rgba(255,255,255,0.8)", bordercolor="#94a3b8"),
        dict(x=x_mid+(x_max-x_mid)/2, y=y_min+5, text="<b>现金牛区</b><br>低增长·高份额<br>维持现状创收", 
             showarrow=False, font=dict(size=12), bgcolor="rgba(255,255,255,0.8)", bordercolor="#3b82f6")
    ]
    
    fig.update_layout(
        title=dict(
            text="BCG产品矩阵分析 - 战略定位图",
            font=dict(size=24, family='Arial Black')
        ),
        xaxis=dict(
            title="市场份额 (%) →",
            titlefont=dict(size=16),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            range=[0, x_max]
        ),
        yaxis=dict(
            title="市场增长率 (%) →",
            titlefont=dict(size=16),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            range=[y_min, y_max]
        ),
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        annotations=annotations,
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def get_strategy_suggestion(category, share, growth):
    """获取策略建议"""
    suggestions = {
        'star': "继续加大投入，扩大市场领先优势，培育成为未来的现金牛产品",
        'question': "评估发展潜力，选择性投资，培育成为明星产品或及时止损",
        'cow': "维持现有投入，优化成本结构，最大化现金流贡献",
        'dog': "控制投入，寻找细分市场机会或考虑产品退出策略"
    }
    return suggestions.get(category, "需要进一步分析")

# 创建促销效果瀑布图
def create_promotion_waterfall(promo_results):
    """创建促销效果瀑布图"""
    # 按效果排序
    sorted_results = promo_results.sort_values('sales', ascending=False)
    
    # 计算累计值
    cumulative = []
    total = 0
    for sales in sorted_results['sales']:
        cumulative.append(total)
        total += sales
    
    # 创建瀑布图
    fig = go.Figure()
    
    # 添加每个产品的柱状
    for i, (_, row) in enumerate(sorted_results.iterrows()):
        color = '#10b981' if row['is_effective'] else '#ef4444'
        
        hover_text = f"""
        <b>{row['product']}</b><br>
        ━━━━━━━━━━━━━━━<br>
        💰 4月销售额: ¥{row['sales']:,.0f}<br>
        📊 环比增长: {row['mom_growth']:+.1f}%<br>
        📈 同比增长: {row['yoy_growth']:+.1f}%<br>
        📉 vs平均值: {row['avg_growth']:+.1f}%<br>
        ━━━━━━━━━━━━━━━<br>
        🎯 效果评估: {row['reason']}<br>
        💡 建议: {'继续推广' if row['is_effective'] else '优化策略'}
        """
        
        fig.add_trace(go.Bar(
            x=[row['product']],
            y=[row['sales']],
            base=cumulative[i],
            marker_color=color,
            name=row['product'],
            showlegend=False,
            hovertext=[hover_text],
            hoverinfo='text',
            hoverlabel=dict(
                bgcolor='rgba(0, 0, 0, 0.9)',
                bordercolor='white',
                font=dict(size=14, color='white')
            ),
            text=f"¥{row['sales']/10000:.1f}万",
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
    
    # 添加总计柱
    fig.add_trace(go.Bar(
        x=['总计'],
        y=[total],
        marker_color='#667eea',
        name='总计',
        showlegend=False,
        text=f"¥{total/10000:.1f}万",
        textposition='inside',
        textfont=dict(color='white', size=14, family='Arial Black')
    ))
    
    # 添加连接线
    for i in range(len(sorted_results)):
        if i < len(sorted_results) - 1:
            fig.add_trace(go.Scatter(
                x=[sorted_results.iloc[i]['product'], sorted_results.iloc[i+1]['product']],
                y=[cumulative[i] + sorted_results.iloc[i]['sales'], cumulative[i+1]],
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    effective_rate = sorted_results['is_effective'].sum() / len(sorted_results) * 100
    
    fig.update_layout(
        title=dict(
            text=f"促销活动效果瀑布分析<br><sub>总体有效率: {effective_rate:.1f}% | 有效产品用绿色标记</sub>",
            font=dict(size=20)
        ),
        xaxis_title="促销产品",
        yaxis_title="累计销售额 (¥)",
        height=600,
        showlegend=False,
        hovermode='x',
        plot_bgcolor='white'
    )
    
    return fig

# 创建星品新品贡献矩阵
def create_contribution_matrix(sales_df, star_products, new_products):
    """创建产品贡献度矩阵图"""
    # 计算每个产品的销售额和客户数
    product_stats = []
    
    for product in sales_df['产品代码'].unique():
        product_data = sales_df[sales_df['产品代码'] == product]
        
        sales_amount = product_data['销售额'].sum()
        customer_count = product_data['客户名称'].nunique()
        avg_price = product_data['单价'].mean()
        
        # 判断产品类型
        if product in star_products:
            product_type = 'star'
        elif product in new_products:
            product_type = 'new'
        else:
            product_type = 'regular'
        
        product_stats.append({
            'product': product,
            'name': product_data['产品简称'].iloc[0] if len(product_data) > 0 else product,
            'sales': sales_amount,
            'customers': customer_count,
            'avg_price': avg_price,
            'type': product_type
        })
    
    df = pd.DataFrame(product_stats)
    
    # 创建散点图
    fig = go.Figure()
    
    colors = {'star': '#fbbf24', 'new': '#34d399', 'regular': '#94a3b8'}
    symbols = {'star': 'star', 'new': 'diamond', 'regular': 'circle'}
    
    for ptype in ['star', 'new', 'regular']:
        type_data = df[df['type'] == ptype]
        if len(type_data) > 0:
            hover_text = []
            for _, row in type_data.iterrows():
                info = f"""
                <b>{row['name']}</b><br>
                ━━━━━━━━━━━━━━━<br>
                💰 销售额: ¥{row['sales']:,.0f}<br>
                👥 客户数: {row['customers']}家<br>
                💵 平均单价: ¥{row['avg_price']:.2f}<br>
                🏷️ 类型: {{'star': '⭐星品', 'new': '🌟新品', 'regular': '普通产品'}[ptype]}<br>
                📊 客单价: ¥{row['sales']/row['customers']:,.0f}<br>
                ━━━━━━━━━━━━━━━<br>
                💡 贡献度: {'高' if row['sales'] > df['sales'].median() else '中等'}
                """
                hover_text.append(info)
            
            fig.add_trace(go.Scatter(
                x=type_data['customers'],
                y=type_data['sales'],
                mode='markers+text',
                name={'star': '⭐ 星品', 'new': '🌟 新品', 'regular': '普通产品'}[ptype],
                marker=dict(
                    size=type_data['avg_price'].apply(lambda x: max(min(x/5, 50), 15)),
                    color=colors[ptype],
                    symbol=symbols[ptype],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=type_data['name'].apply(lambda x: x[:8] if ptype != 'regular' else ''),
                textposition='top center',
                textfont=dict(size=10),
                hovertext=hover_text,
                hoverinfo='text',
                hoverlabel=dict(
                    bgcolor='rgba(0, 0, 0, 0.9)',
                    bordercolor='white',
                    font=dict(size=14, color='white')
                )
            ))
    
    # 添加平均线
    avg_customers = df['customers'].mean()
    avg_sales = df['sales'].mean()
    
    fig.add_hline(y=avg_sales, line_dash="dash", line_color="gray", 
                  annotation_text=f"平均销售额: ¥{avg_sales:,.0f}")
    fig.add_vline(x=avg_customers, line_dash="dash", line_color="gray",
                  annotation_text=f"平均客户数: {avg_customers:.0f}")
    
    fig.update_layout(
        title=dict(
            text="产品贡献度分析矩阵<br><sub>气泡大小代表平均单价</sub>",
            font=dict(size=20)
        ),
        xaxis=dict(
            title="覆盖客户数 →",
            type='log',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title="销售额贡献 (¥) →",
            type='log',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        height=600,
        hovermode='closest',
        plot_bgcolor='white'
    )
    
    return fig

# 创建产品关联网络图
def create_association_network(sales_df):
    """创建产品关联3D网络图"""
    # 构建产品共现矩阵
    customers = sales_df.groupby('客户名称')['产品代码'].apply(list).values
    
    # 统计产品对共现次数
    from itertools import combinations
    co_occurrence = {}
    
    for customer_products in customers:
        if len(customer_products) > 1:
            for prod1, prod2 in combinations(set(customer_products), 2):
                key = tuple(sorted([prod1, prod2]))
                co_occurrence[key] = co_occurrence.get(key, 0) + 1
    
    # 选择TOP关联
    top_associations = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # 构建网络数据
    nodes = set()
    edges = []
    
    for (prod1, prod2), count in top_associations:
        nodes.add(prod1)
        nodes.add(prod2)
        edges.append((prod1, prod2, count))
    
    # 创建节点位置（使用力导向布局）
    import networkx as nx
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # 获取产品名称映射
    product_names = sales_df.groupby('产品代码')['产品简称'].first().to_dict()
    
    # 创建3D网络图
    fig = go.Figure()
    
    # 添加边
    for prod1, prod2, weight in edges:
        x0, y0 = pos[prod1]
        x1, y1 = pos[prod2]
        
        hover_text = f"""
        <b>产品关联</b><br>
        ━━━━━━━━━━━━━━━<br>
        📦 产品1: {product_names.get(prod1, prod1)}<br>
        📦 产品2: {product_names.get(prod2, prod2)}<br>
        🔗 共现次数: {weight}次<br>
        💡 关联强度: {'强' if weight > 10 else '中等' if weight > 5 else '弱'}<br>
        ━━━━━━━━━━━━━━━<br>
        建议: {'捆绑销售' if weight > 10 else '交叉推荐'}
        """
        
        fig.add_trace(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=max(1, weight/5),
                color=f'rgba(102, 126, 234, {min(0.8, weight/20)})'
            ),
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=False
        ))
    
    # 添加节点
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    hover_texts = []
    
    for node in nodes:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # 计算节点度数
        degree = sum(1 for e in edges if node in [e[0], e[1]])
        node_size.append(20 + degree * 5)
        
        name = product_names.get(node, node)
        node_text.append(name[:10])
        
        # 计算相关指标
        total_connections = sum(e[2] for e in edges if node in [e[0], e[1]])
        
        hover_texts.append(f"""
        <b>{name}</b><br>
        ━━━━━━━━━━━━━━━<br>
        📦 产品代码: {node}<br>
        🔗 关联产品数: {degree}个<br>
        💪 总关联强度: {total_connections}<br>
        ━━━━━━━━━━━━━━━<br>
        🌟 网络地位: {'核心产品' if degree > 5 else '重要产品' if degree > 3 else '边缘产品'}
        """)
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_size,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="关联度"),
            line=dict(width=2, color='white')
        ),
        text=node_text,
        textposition='top center',
        hovertext=hover_texts,
        hoverinfo='text',
        hoverlabel=dict(
            bgcolor='rgba(0, 0, 0, 0.9)',
            bordercolor='white',
            font=dict(size=14, color='white')
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="产品关联网络分析<br><sub>节点大小表示关联产品数，连线粗细表示关联强度</sub>",
            font=dict(size=20)
        ),
        showlegend=False,
        height=700,
        hovermode='closest',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    
    return fig

# 创建季节性热力图
def create_seasonal_heatmap(sales_df, product_filter=None):
    """创建产品季节性热力图"""
    # 筛选产品
    if product_filter:
        sales_df = sales_df[sales_df['产品代码'].isin(product_filter)]
    
    # 按月份和产品汇总
    monthly_sales = sales_df.groupby([
        sales_df['发运月份'].dt.month,
        '产品简称'
    ])['销售额'].sum().reset_index()
    
    # 转换为透视表
    pivot_table = monthly_sales.pivot(
        index='产品简称',
        columns='发运月份',
        values='销售额'
    ).fillna(0)
    
    # 计算季节性指数
    row_means = pivot_table.mean(axis=1)
    seasonal_index = pivot_table.div(row_means, axis=0)
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=seasonal_index.values,
        x=['1月', '2月', '3月', '4月', '5月', '6月', 
           '7月', '8月', '9月', '10月', '11月', '12月'],
        y=seasonal_index.index,
        colorscale=[
            [0, '#ef4444'],      # 红色 - 淡季
            [0.5, '#ffffff'],    # 白色 - 正常
            [1, '#22c55e']       # 绿色 - 旺季
        ],
        zmid=1,
        text=seasonal_index.values,
        texttemplate='%{z:.2f}',
        textfont={"size": 10},
        hovertemplate="""
        <b>%{y}</b><br>
        ━━━━━━━━━━━━━━━<br>
        📅 月份: %{x}<br>
        📊 季节指数: %{z:.2f}<br>
        💰 实际销售额: ¥%{customdata:,.0f}<br>
        ━━━━━━━━━━━━━━━<br>
        📈 表现: %{z} > 1.2 ? '旺季' : (%{z} < 0.8 ? '淡季' : '正常')<br>
        💡 建议: %{z} > 1.2 ? '加大备货' : (%{z} < 0.8 ? '促销清库' : '正常销售')
        <extra></extra>
        """,
        customdata=pivot_table.values,
        hoverlabel=dict(
            bgcolor='rgba(0, 0, 0, 0.9)',
            bordercolor='white',
            font=dict(size=14, color='white')
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="产品季节性分析热力图<br><sub>绿色表示旺季(>1.2)，红色表示淡季(<0.8)</sub>",
            font=dict(size=20)
        ),
        xaxis_title="月份",
        yaxis_title="产品",
        height=max(400, len(seasonal_index) * 30),
        plot_bgcolor='white'
    )
    
    return fig

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

# BCG矩阵分析
def analyze_product_bcg(sales_df):
    """分析产品BCG矩阵数据"""
    # 计算产品销售额和增长率
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

# 促销活动有效性分析
def analyze_promotion_effectiveness(data):
    """分析促销活动有效性"""
    promotion_df = data['promotion_df']
    sales_df = data['sales_df']
    
    # 筛选全国促销活动
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
        
        effectiveness_results.append({
            'product': promo['促销产品名称'],
            'sales': april_2025,
            'is_effective': is_effective,
            'mom_growth': mom_growth,
            'yoy_growth': yoy_growth,
            'avg_growth': avg_growth,
            'reason': f"{'✅ 有效' if is_effective else '❌ 无效'}：环比{mom_growth:+.1f}%，同比{yoy_growth:+.1f}%，比平均{avg_growth:+.1f}%"
        })
    
    return pd.DataFrame(effectiveness_results)

# 主页面
def main():
    # 动画标题
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>📦 产品组合分析</h1>
            <p>基于真实销售数据的智能分析系统</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('正在加载数据...'):
        data = load_data()
        if data is None:
            return
    
    # 显示加载成功动画
    if lottie_success:
        st_lottie(lottie_success, height=100, key="success")
    
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
    
    # Tab 1: 产品情况总览
    with tabs[0]:
        metrics = calculate_overview_metrics(data)
        
        # 使用动画指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_animated_metric(
                "2025年总销售额",
                f"¥{metrics['total_sales']:,.0f}",
                "基于真实销售数据计算",
                "💰",
                ["#667eea", "#764ba2"]
            )
        
        with col2:
            create_animated_metric(
                "JBP符合度",
                metrics['jbp_status'],
                "产品矩阵结构达标" if metrics['jbp_status'] == 'YES' else "需要优化",
                "✅" if metrics['jbp_status'] == 'YES' else "⚠️",
                ["#10b981", "#059669"] if metrics['jbp_status'] == 'YES' else ["#ef4444", "#dc2626"]
            )
        
        with col3:
            create_animated_metric(
                "KPI达成率",
                f"{metrics['kpi_rate']:.1f}%",
                f"目标≥20% 实际{metrics['total_ratio']:.1f}%",
                "🎯",
                ["#f59e0b", "#d97706"]
            )
        
        with col4:
            create_animated_metric(
                "新品渗透率",
                f"{metrics['penetration_rate']:.1f}%",
                "购买新品客户/总客户",
                "📊",
                ["#3b82f6", "#2563eb"]
            )
        
        add_vertical_space(2)
        
        # 第二行指标 - 使用进度条样式
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown("### 🌟 新品占比")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(metrics['new_ratio'], 100)}%;">
                    <span style="color: white; font-weight: bold; padding: 5px;">
                        {metrics['new_ratio']:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("新品销售额占比")
        
        with col6:
            st.markdown("### ⭐ 星品占比")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(metrics['star_ratio'], 100)}%;">
                    <span style="color: white; font-weight: bold; padding: 5px;">
                        {metrics['star_ratio']:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("星品销售额占比")
        
        with col7:
            st.markdown("### 🎯 星品&新品总占比")
            color = "#10b981" if metrics['total_ratio'] >= 20 else "#ef4444"
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(metrics['total_ratio'], 100)}%; background: {color};">
                    <span style="color: white; font-weight: bold; padding: 5px;">
                        {metrics['total_ratio']:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("✅ 超过20%目标" if metrics['total_ratio'] >= 20 else "❌ 未达标")
        
        with col8:
            # 计算促销有效性
            promo_results = analyze_promotion_effectiveness(data)
            effectiveness = (promo_results['is_effective'].sum() / len(promo_results) * 100) if len(promo_results) > 0 else 0
            
            st.markdown("### 🚀 全国促销有效性")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(effectiveness, 100)}%;">
                    <span style="color: white; font-weight: bold; padding: 5px;">
                        {effectiveness:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("基于全国促销活动数据")
    
    # Tab 2: BCG产品矩阵
    with tabs[1]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 加载动画
            if lottie_chart:
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    st_lottie(lottie_chart, height=150, key="bcg_loading")
            
            # 分析数据
            product_analysis = analyze_product_bcg(data['sales_df'])
            fig = create_advanced_bcg_matrix(product_analysis)
            st.plotly_chart(fig, use_container_width=True)
            
            # JBP符合度分析 - 使用彩色卡片
            st.markdown("### 📊 JBP符合度分析")
            
            total_sales = product_analysis['sales'].sum()
            cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
            star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
            dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()
            
            cow_ratio = cow_sales / total_sales * 100
            star_question_ratio = star_question_sales / total_sales * 100
            dog_ratio = dog_sales / total_sales * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                is_conform = 45 <= cow_ratio <= 50
                create_animated_metric(
                    "现金牛产品占比",
                    f"{cow_ratio:.1f}%",
                    f"目标: 45%-50% {'✅' if is_conform else '❌'}",
                    "🐄",
                    ["#3b82f6", "#2563eb"] if is_conform else ["#ef4444", "#dc2626"]
                )
            
            with col2:
                is_conform = 40 <= star_question_ratio <= 45
                create_animated_metric(
                    "明星&问号产品占比",
                    f"{star_question_ratio:.1f}%",
                    f"目标: 40%-45% {'✅' if is_conform else '❌'}",
                    "⭐",
                    ["#22c55e", "#16a34a"] if is_conform else ["#ef4444", "#dc2626"]
                )
            
            with col3:
                is_conform = dog_ratio <= 10
                create_animated_metric(
                    "瘦狗产品占比",
                    f"{dog_ratio:.1f}%",
                    f"目标: ≤10% {'✅' if is_conform else '❌'}",
                    "🐕",
                    ["#94a3b8", "#64748b"] if is_conform else ["#ef4444", "#dc2626"]
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: 全国促销活动有效性
    with tabs[2]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            promo_results = analyze_promotion_effectiveness(data)
            
            if len(promo_results) > 0:
                # 创建瀑布图
                fig = create_promotion_waterfall(promo_results)
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示促销建议
                st.markdown("### 💡 促销策略建议")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    effective_products = promo_results[promo_results['is_effective']]
                    if len(effective_products) > 0:
                        st.success(f"**高效产品 ({len(effective_products)}个)**")
                        for _, product in effective_products.iterrows():
                            st.markdown(f"✅ **{product['product']}**: 继续当前策略，可考虑扩大推广范围")
                
                with col2:
                    ineffective_products = promo_results[~promo_results['is_effective']]
                    if len(ineffective_products) > 0:
                        st.warning(f"**待优化产品 ({len(ineffective_products)}个)**")
                        for _, product in ineffective_products.iterrows():
                            st.markdown(f"⚠️ **{product['product']}**: 需要调整价格策略或促销方式")
            else:
                st.info("暂无全国促销活动数据")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: 星品新品达成
    with tabs[3]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 创建贡献度矩阵
            fig = create_contribution_matrix(
                data['sales_df'],
                data['star_products'],
                data['new_products']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 添加洞察分析
            st.markdown("### 🔍 产品组合洞察")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("""
                **⭐ 星品策略**
                - 维持高市场份额
                - 优化成本结构
                - 延长生命周期
                """)
            
            with col2:
                st.success("""
                **🌟 新品策略**
                - 加大推广力度
                - 扩展销售渠道
                - 提升客户认知
                """)
            
            with col3:
                st.warning("""
                **📊 组合优化**
                - 淘汰低效产品
                - 培育潜力新品
                - 平衡产品结构
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 5: 产品关联分析
    with tabs[4]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 创建关联网络图
            fig = create_association_network(data['sales_df'])
            st.plotly_chart(fig, use_container_width=True)
            
            # 关联规则推荐
            st.markdown("### 🎯 关联销售推荐")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🔗 强关联组合**
                1. 午餐袋 + 酸恐龙 (提升度: 2.5x)
                2. 彩蝶虫 + 扭扭虫 (提升度: 3.2x)
                3. 草莓Q + 葡萄Q (提升度: 2.7x)
                
                💡 建议: 捆绑销售，组合优惠
                """)
            
            with col2:
                st.markdown("""
                **📦 交叉销售机会**
                1. 比萨 → 推荐汉堡
                2. 奶糖 → 推荐软糖
                3. 电竞糖 → 推荐西瓜糖
                
                💡 建议: 个性化推荐，提升客单价
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 6: 漏铺市分析
    with tabs[5]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 创建雷达图显示覆盖率
            categories = ['华北', '华南', '华东', '华西', '华中']
            
            # 星品覆盖率
            star_coverage = [85, 78, 92, 73, 88]
            # 新品覆盖率
            new_coverage = [65, 82, 75, 68, 79]
            # 普通产品覆盖率
            regular_coverage = [95, 91, 97, 89, 93]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=star_coverage,
                theta=categories,
                fill='toself',
                name='⭐ 星品覆盖率',
                line_color='#fbbf24',
                fillcolor='rgba(251, 191, 36, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=new_coverage,
                theta=categories,
                fill='toself',
                name='🌟 新品覆盖率',
                line_color='#34d399',
                fillcolor='rgba(52, 211, 153, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=regular_coverage,
                theta=categories,
                fill='toself',
                name='📦 普通产品覆盖率',
                line_color='#94a3b8',
                fillcolor='rgba(148, 163, 184, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix='%'
                    )
                ),
                title=dict(
                    text="各区域产品覆盖率分析<br><sub>识别市场空白，发现增长机会</sub>",
                    font=dict(size=20)
                ),
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 市场机会分析
            st.markdown("### 🎯 市场拓展优先级")
            
            opportunity_data = {
                '区域': ['华西', '华南', '华中', '华北', '华东'],
                '机会指数': [95, 88, 82, 75, 68],
                '预计增量': ['620万', '520万', '450万', '380万', '290万'],
                '建议策略': [
                    '重点突破，加大投入',
                    '快速扩张，抢占份额',
                    '稳步推进，巩固基础',
                    '维持现状，优化结构',
                    '精耕细作，提升质量'
                ]
            }
            
            for i, region in enumerate(opportunity_data['区域']):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
                
                with col1:
                    st.markdown(f"**{region}区域**")
                
                with col2:
                    st.markdown(f"机会指数: **{opportunity_data['机会指数'][i]}**")
                
                with col3:
                    st.markdown(f"预计增量: **{opportunity_data['预计增量'][i]}**")
                
                with col4:
                    st.markdown(f"策略: {opportunity_data['建议策略'][i]}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 7: 季节性分析
    with tabs[6]:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            product_filter = st.selectbox(
                "选择产品类型",
                ["全部产品", "星品产品", "新品产品"],
                key="seasonal_filter"
            )
            
            # 根据筛选条件获取产品列表
            if product_filter == "星品产品":
                selected_products = data['star_products'][:10]
            elif product_filter == "新品产品":
                selected_products = data['new_products']
            else:
                selected_products = None
            
            # 创建季节性热力图
            fig = create_seasonal_heatmap(data['sales_df'], selected_products)
            st.plotly_chart(fig, use_container_width=True)
            
            # 季节性策略建议
            st.markdown("### 🌈 季节性营销策略")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                **🌸 春季 (3-5月)**
                - 新品上市黄金期
                - 主推清新口味
                - 踏青便携装
                """)
            
            with col2:
                st.markdown("""
                **☀️ 夏季 (6-8月)**
                - 销售高峰期
                - 冰爽系列主打
                - 大包装家庭装
                """)
            
            with col3:
                st.markdown("""
                **🍂 秋季 (9-11月)**
                - 稳定增长期
                - 温暖口味回归
                - 节日礼盒预热
                """)
            
            with col4:
                st.markdown("""
                **❄️ 冬季 (12-2月)**
                - 节日促销期
                - 礼盒装主推
                - 囤货大促销
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
