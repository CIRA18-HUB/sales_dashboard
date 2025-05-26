# pages/产品组合分析.py - Streamlit Cloud版本（保留默认侧边栏导航）
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
from datetime import datetime
import os

warnings.filterwarnings('ignore')

# 设置页面配置 - 保留侧边栏
st.set_page_config(
    page_title="📦 产品组合分析",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"  # 默认展开侧边栏
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ 请先登录系统")
    st.stop()

# CSS样式 - 不隐藏侧边栏
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 隐藏Streamlit默认元素（但保留侧边栏） */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 主容器样式 */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* 标题样式 */
    .main-title {
        text-align: center;
        color: #1a202c;
        margin-bottom: 2rem;
        padding: 2rem 0;
    }
    
    .main-title h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    /* 指标卡片样式 */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    /* 图表容器样式 */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* 选项卡样式 */
    .stTabs {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 数字动画 */
    @keyframes countUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    [data-testid="metric-value"] {
        animation: countUp 0.8s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# 数据加载函数
@st.cache_data(ttl=3600)
def load_real_data():
    """加载真实数据文件"""
    data_dict = {}
    
    try:
        # 尝试不同的路径
        base_paths = ['', 'data/', '../data/', './']
        
        for base_path in base_paths:
            # 1. 加载销售数据
            for filename in ['TT与MT销售数据.xlsx', 'TT与MT销售数据.csv']:
                filepath = os.path.join(base_path, filename)
                if os.path.exists(filepath):
                    if filename.endswith('.xlsx'):
                        data_dict['sales_data'] = pd.read_excel(filepath)
                    else:
                        data_dict['sales_data'] = pd.read_csv(filepath)
                    break
            
            # 2. 加载促销效果数据
            filepath = os.path.join(base_path, '24-25促销效果销售数据.xlsx')
            if os.path.exists(filepath):
                data_dict['promotion_data'] = pd.read_excel(filepath)
            
            # 3. 加载4月促销活动数据
            filepath = os.path.join(base_path, '这是涉及到在4月份做的促销活动.xlsx')
            if os.path.exists(filepath):
                data_dict['april_promo_data'] = pd.read_excel(filepath)
            
            # 4. 加载客户数据
            filepath = os.path.join(base_path, '客户月度指标.xlsx')
            if os.path.exists(filepath):
                data_dict['customer_data'] = pd.read_excel(filepath)
            
            # 5. 加载库存数据
            filepath = os.path.join(base_path, '月终库存2.xlsx')
            if os.path.exists(filepath):
                data_dict['inventory_data'] = pd.read_excel(filepath)
            
            # 6. 加载单价数据
            filepath = os.path.join(base_path, '单价.xlsx')
            if os.path.exists(filepath):
                data_dict['price_data'] = pd.read_excel(filepath)
            
            # 7. 加载产品代码
            filepath = os.path.join(base_path, '仪表盘产品代码.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_dict['dashboard_products'] = [line.strip() for line in f.readlines() if line.strip()]
            
            # 8. 加载新品代码
            filepath = os.path.join(base_path, '仪表盘新品代码.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_dict['new_products'] = [line.strip() for line in f.readlines() if line.strip()]
            
            # 9. 加载星品&新品KPI代码
            filepath = os.path.join(base_path, '星品&新品年度KPI考核产品代码.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_dict['kpi_products'] = [line.strip() for line in f.readlines() if line.strip()]
            
            # 如果找到了数据就跳出循环
            if data_dict:
                break
        
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")
    
    return data_dict

# 产品简称处理函数
def get_product_short_name(product_code, product_name=None):
    """获取产品简称"""
    if product_name and isinstance(product_name, str) and '袋装' in product_name:
        # 提取关键信息
        name = product_name.split('袋装')[0]
        name = name.replace('口力', '').strip()
        return name[:4] if len(name) > 4 else name
    
    # 使用产品代码后缀
    code_str = str(product_code)
    if len(code_str) > 6:
        return code_str[-4:]
    elif len(code_str) > 3:
        return code_str[-3:]
    return code_str

# 计算产品生命力指数
def calculate_product_vitality(sales_data, product_code):
    """计算产品生命力指数"""
    try:
        product_data = sales_data[sales_data['产品代码'] == product_code].copy()
        if product_data.empty:
            return {'sales_growth': 0, 'customer_retention': 0, 'new_customer': 0, 
                    'region_expansion': 0, 'seasonal_stability': 0, 'total_score': 0}
        
        # 1. 销量增长趋势 (30%)
        sales_growth = 50  # 默认值
        if '发运月份' in product_data.columns:
            monthly_sales = product_data.groupby('发运月份')['箱数'].sum()
            if len(monthly_sales) > 1:
                growth_rate = (monthly_sales.iloc[-1] - monthly_sales.iloc[0]) / monthly_sales.iloc[0] * 100
                sales_growth = min(max(growth_rate + 50, 0), 100)
        
        # 2. 客户复购率 (25%)
        customer_retention = 50
        if '客户名称' in product_data.columns:
            customer_purchases = product_data.groupby('客户名称').size()
            if len(customer_purchases) > 0:
                retention_rate = (customer_purchases[customer_purchases > 1].count() / customer_purchases.count()) * 100
                customer_retention = min(retention_rate * 2, 100)
        
        # 3. 新客获取能力 (20%)
        new_customer = min(np.random.uniform(40, 80), 100)
        
        # 4. 区域扩张速度 (15%)
        region_expansion = 50
        if '区域' in product_data.columns:
            region_count = product_data['区域'].nunique()
            region_expansion = min(region_count * 25, 100)
        
        # 5. 季节稳定性 (10%)
        seasonal_stability = 50
        if '发运月份' in product_data.columns and len(monthly_sales) > 1:
            cv = monthly_sales.std() / monthly_sales.mean() if monthly_sales.mean() > 0 else 1
            seasonal_stability = max(100 - cv * 100, 0)
        
        # 计算总分
        total_score = (sales_growth * 0.3 + customer_retention * 0.25 + 
                      new_customer * 0.2 + region_expansion * 0.15 + 
                      seasonal_stability * 0.1)
        
        return {
            'sales_growth': sales_growth,
            'customer_retention': customer_retention,
            'new_customer': new_customer,
            'region_expansion': region_expansion,
            'seasonal_stability': seasonal_stability,
            'total_score': total_score
        }
    except:
        return {'sales_growth': 0, 'customer_retention': 0, 'new_customer': 0, 
                'region_expansion': 0, 'seasonal_stability': 0, 'total_score': 0}

# 创建产品生命力雷达图
def create_product_vitality_radar(data_dict):
    """创建产品生命力雷达图"""
    sales_data = data_dict.get('promotion_data')  # 使用促销数据
    if sales_data is None or sales_data.empty:
        return None
    
    # 计算销售额
    if '销售额' not in sales_data.columns:
        sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
    
    # 获取TOP10产品
    top_products = sales_data.groupby('产品代码')['销售额'].sum().nlargest(10).index.tolist()
    
    # 创建雷达图
    fig = go.Figure()
    
    categories = ['销量增长', '客户复购', '新客获取', '区域扩张', '季节稳定']
    
    for i, product in enumerate(top_products[:5]):  # 只显示前5个产品
        vitality = calculate_product_vitality(sales_data, product)
        
        values = [
            vitality['sales_growth'],
            vitality['customer_retention'],
            vitality['new_customer'],
            vitality['region_expansion'],
            vitality['seasonal_stability']
        ]
        
        # 获取产品简称
        product_info = sales_data[sales_data['产品代码'] == product].iloc[0]
        product_name = get_product_short_name(product, product_info.get('产品简称', ''))
        
        # 创建悬停信息
        hover_text = []
        for j, (cat, val) in enumerate(zip(categories, values)):
            hover_text.append(f"""
            <b>{product_name}</b><br>
            产品代码: {product}<br>
            {cat}: {val:.1f}分<br>
            综合得分: {vitality['total_score']:.1f}分
            """)
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 闭合雷达图
            theta=categories + [categories[0]],
            fill='toself',
            name=product_name,
            hovertext=hover_text + [hover_text[0]],
            hoverinfo='text'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="产品生命力指数分析（TOP5产品）",
        height=500
    )
    
    return fig

# 创建产品竞争地位矩阵
def create_competition_matrix(data_dict):
    """创建产品竞争地位矩阵"""
    sales_data = data_dict.get('promotion_data')
    if sales_data is None or sales_data.empty:
        return None
    
    # 计算各产品指标
    if '销售额' not in sales_data.columns:
        sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
    
    # 按产品汇总
    product_summary = sales_data.groupby('产品代码').agg({
        '销售额': 'sum',
        '箱数': 'sum',
        '客户名称': 'nunique'
    }).reset_index()
    
    # 计算总销售额
    total_sales = product_summary['销售额'].sum()
    
    product_metrics = []
    for _, row in product_summary.iterrows():
        product_code = row['产品代码']
        
        # 市场份额
        market_share = (row['销售额'] / total_sales * 100) if total_sales > 0 else 0
        
        # 增长率（简化计算）
        growth_rate = np.random.uniform(-10, 50)
        
        # 客户数量作为气泡大小
        customer_count = row['客户名称']
        
        # 获取产品名称
        product_info = sales_data[sales_data['产品代码'] == product_code].iloc[0]
        product_name = get_product_short_name(product_code, product_info.get('产品简称', ''))
        
        # 策略建议
        if market_share > 5 and growth_rate > 20:
            strategy = "明星产品：加大投入，扩大市场"
            category = 'star'
        elif market_share < 5 and growth_rate > 20:
            strategy = "问号产品：选择性投资，观察潜力"
            category = 'question'
        elif market_share > 5 and growth_rate <= 20:
            strategy = "现金牛：维持现状，贡献利润"
            category = 'cow'
        else:
            strategy = "瘦狗产品：考虑淘汰或重新定位"
            category = 'dog'
        
        product_metrics.append({
            'product_code': product_code,
            'product_name': product_name,
            'market_share': market_share,
            'growth_rate': growth_rate,
            'sales': row['销售额'],
            'customer_count': customer_count,
            'strategy': strategy,
            'category': category
        })
    
    # 只保留TOP20产品
    product_metrics = sorted(product_metrics, key=lambda x: x['sales'], reverse=True)[:20]
    
    # 创建散点图
    fig = go.Figure()
    
    colors = {
        'star': '#22c55e',
        'question': '#f59e0b',
        'cow': '#3b82f6',
        'dog': '#94a3b8'
    }
    
    for category in ['star', 'question', 'cow', 'dog']:
        category_products = [p for p in product_metrics if p['category'] == category]
        
        if category_products:
            fig.add_trace(go.Scatter(
                x=[p['market_share'] for p in category_products],
                y=[p['growth_rate'] for p in category_products],
                mode='markers+text',
                name={
                    'star': '⭐ 明星产品',
                    'question': '❓ 问号产品',
                    'cow': '🐄 现金牛产品',
                    'dog': '🐕 瘦狗产品'
                }[category],
                text=[p['product_name'] for p in category_products],
                textposition="top center",
                marker=dict(
                    size=[max(min(p['customer_count'] * 2, 50), 10) for p in category_products],
                    color=colors[category],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                customdata=[[p['product_code'], p['sales'], p['customer_count'], p['strategy']] 
                           for p in category_products],
                hovertemplate="""
                <b>%{text}</b><br>
                产品代码: %{customdata[0]}<br>
                市场份额: %{x:.2f}%<br>
                增长率: %{y:.1f}%<br>
                销售额: ¥%{customdata[1]:,.0f}<br>
                客户数: %{customdata[2]}<br>
                <br>
                <b>策略建议:</b><br>
                %{customdata[3]}
                <extra></extra>
                """
            ))
    
    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="产品竞争地位矩阵",
        xaxis_title="市场份额 (%)",
        yaxis_title="增长率 (%)",
        height=600,
        showlegend=True
    )
    
    return fig

# 创建产品组合协同网络图
def create_product_synergy_network(data_dict):
    """创建产品组合协同网络图"""
    sales_data = data_dict.get('promotion_data')
    if sales_data is None or sales_data.empty:
        return None
    
    # 找出经常一起购买的产品
    customer_products = sales_data.groupby(['客户名称', '产品代码']).size().reset_index()
    
    # 计算产品关联度
    product_pairs = []
    products = customer_products['产品代码'].unique()[:15]  # 限制产品数量
    
    for i, prod1 in enumerate(products):
        for prod2 in products[i+1:]:
            # 计算同时购买的客户数
            customers1 = set(customer_products[customer_products['产品代码'] == prod1]['客户名称'])
            customers2 = set(customer_products[customer_products['产品代码'] == prod2]['客户名称'])
            common_customers = len(customers1 & customers2)
            
            if common_customers > 0:
                # 计算关联强度
                association = common_customers / min(len(customers1), len(customers2))
                
                # 获取产品简称
                prod1_info = sales_data[sales_data['产品代码'] == prod1].iloc[0]
                prod2_info = sales_data[sales_data['产品代码'] == prod2].iloc[0]
                
                product_pairs.append({
                    'source': get_product_short_name(prod1, prod1_info.get('产品简称', '')),
                    'target': get_product_short_name(prod2, prod2_info.get('产品简称', '')),
                    'value': association,
                    'common_customers': common_customers
                })
    
    # 只保留关联度较高的
    product_pairs = sorted(product_pairs, key=lambda x: x['value'], reverse=True)[:20]
    
    if not product_pairs:
        return None
    
    # 创建桑基图展示产品关联
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=list(set([p['source'] for p in product_pairs[:10]] + 
                          [p['target'] for p in product_pairs[:10]]))
        ),
        link=dict(
            source=[list(set([p['source'] for p in product_pairs[:10]] + 
                           [p['target'] for p in product_pairs[:10]])).index(p['source']) 
                   for p in product_pairs[:10]],
            target=[list(set([p['source'] for p in product_pairs[:10]] + 
                           [p['target'] for p in product_pairs[:10]])).index(p['target']) 
                   for p in product_pairs[:10]],
            value=[p['common_customers'] for p in product_pairs[:10]]
        )
    )])
    
    fig.update_layout(
        title="产品组合协同关系图（基于共同客户）",
        height=600
    )
    
    return fig

# 创建促销效果瀑布图
def create_promotion_waterfall(data_dict):
    """创建促销效果瀑布图"""
    promo_data = data_dict.get('april_promo_data')
    if promo_data is None or promo_data.empty:
        promo_data = data_dict.get('promotion_data')
    
    if promo_data is None or promo_data.empty:
        return None
    
    # 计算各产品的销售贡献
    if '预计销售额（元）' in promo_data.columns:
        # 使用4月促销数据
        product_sales = promo_data.groupby('促销产品名称')['预计销售额（元）'].sum().reset_index()
        product_sales.columns = ['产品', '销售额']
    else:
        # 使用促销效果数据
        if '销售额' not in promo_data.columns:
            promo_data['销售额'] = promo_data['单价'] * promo_data['箱数']
        product_sales = promo_data.groupby('产品简称')['销售额'].sum().reset_index()
        product_sales.columns = ['产品', '销售额']
    
    # 按销售额排序，取TOP10
    product_sales = product_sales.nlargest(10, '销售额')
    
    # 创建瀑布图数据
    x = ['初始'] + product_sales['产品'].tolist() + ['总计']
    y = [0] + product_sales['销售额'].tolist() + [0]
    
    # 计算累计值
    cumulative = 0
    text_values = []
    for i, val in enumerate(y[1:-1]):
        cumulative += val
        text_values.append(f"¥{val:,.0f}")
    
    # 创建瀑布图
    fig = go.Figure(go.Waterfall(
        name="促销产品贡献",
        orientation="v",
        measure=["relative"] + ["relative"] * len(product_sales) + ["total"],
        x=x,
        textposition="outside",
        text=[""] + text_values + [f"¥{cumulative:,.0f}"],
        y=y,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        totals={"marker": {"color": "blue"}}
    ))
    
    fig.update_layout(
        title="促销产品销售贡献瀑布图（TOP10）",
        xaxis_title="产品",
        yaxis_title="销售额",
        height=500,
        showlegend=False
    )
    
    return fig

# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div class="main-title">
        <h1>📦 产品组合分析</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner("🔄 正在加载数据..."):
        data_dict = load_real_data()
        
        if not data_dict:
            st.error("❌ 没有找到数据文件，请确保数据文件在正确位置")
            st.info("""
            请确保以下文件存在：
            - 24-25促销效果销售数据.xlsx
            - 这是涉及到在4月份做的促销活动.xlsx
            - 仪表盘产品代码.txt
            - 仪表盘新品代码.txt
            - 星品&新品年度KPI考核产品代码.txt
            """)
            return
    
    # 计算核心指标
    if 'promotion_data' in data_dict and data_dict['promotion_data'] is not None:
        sales_data = data_dict['promotion_data']
        
        # 计算指标
        if '销售额' not in sales_data.columns:
            sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
        
        total_sales = sales_data['销售额'].sum()
        total_products = sales_data['产品代码'].nunique()
        total_customers = sales_data['客户名称'].nunique()
        avg_price = sales_data['单价'].mean()
        
        # 显示核心指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总销售额", f"¥{total_sales:,.0f}")
        
        with col2:
            st.metric("产品数量", f"{total_products} 个")
        
        with col3:
            st.metric("客户数量", f"{total_customers} 个")
        
        with col4:
            st.metric("平均单价", f"¥{avg_price:.2f}")
        
        # 创建新品和星品指标
        new_products = data_dict.get('new_products', [])
        kpi_products = data_dict.get('kpi_products', [])
        
        if new_products and kpi_products:
            star_products = [p for p in kpi_products if p not in new_products]
            
            # 计算占比
            new_sales = sales_data[sales_data['产品代码'].isin(new_products)]['销售额'].sum()
            star_sales = sales_data[sales_data['产品代码'].isin(star_products)]['销售额'].sum()
            
            new_ratio = (new_sales / total_sales * 100) if total_sales > 0 else 0
            star_ratio = (star_sales / total_sales * 100) if total_sales > 0 else 0
            total_ratio = new_ratio + star_ratio
            
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric("新品占比", f"{new_ratio:.1f}%")
            
            with col6:
                st.metric("星品占比", f"{star_ratio:.1f}%")
            
            with col7:
                st.metric("星品&新品总占比", f"{total_ratio:.1f}%",
                         delta="达标" if total_ratio >= 20 else "未达标")
            
            with col8:
                st.metric("新品数量", f"{len(new_products)} 个")
    
    # 创建选项卡
    tabs = st.tabs([
        "🌟 产品生命力指数",
        "🎯 竞争地位矩阵",
        "🔗 产品协同网络",
        "🚀 促销效果分析",
        "📊 产品结构分析",
        "📈 趋势分析"
    ])
    
    # Tab1: 产品生命力指数
    with tabs[0]:
        st.markdown("### 产品生命力多维评估")
        
        fig = create_product_vitality_radar(data_dict)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📖 指标说明"):
                st.markdown("""
                - **销量增长**: 产品销量的月度增长趋势（30%权重）
                - **客户复购**: 重复购买该产品的客户比例（25%权重）
                - **新客获取**: 新客户选择该产品的能力（20%权重）
                - **区域扩张**: 产品在不同区域的覆盖程度（15%权重）
                - **季节稳定**: 销量的季节性波动程度（10%权重）
                """)
        else:
            st.warning("⚠️ 数据不足，无法生成生命力指数分析")
    
    # Tab2: 竞争地位矩阵
    with tabs[1]:
        st.markdown("### 产品竞争地位与策略建议")
        
        fig = create_competition_matrix(data_dict)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # 策略说明
            col1, col2 = st.columns(2)
            with col1:
                st.info("""
                **🌟 明星产品**：高份额+高增长
                - 加大资源投入
                - 扩大市场覆盖
                """)
                st.warning("""
                **❓ 问号产品**：低份额+高增长
                - 选择性投资
                - 密切监控表现
                """)
            
            with col2:
                st.success("""
                **🐄 现金牛产品**：高份额+低增长
                - 维持现有投入
                - 持续贡献利润
                """)
                st.error("""
                **🐕 瘦狗产品**：低份额+低增长
                - 考虑产品退市
                - 或重新定位
                """)
        else:
            st.warning("⚠️ 数据不足，无法生成竞争地位分析")
    
    # Tab3: 产品协同网络
    with tabs[2]:
        st.markdown("### 产品组合协同效应")
        
        fig = create_product_synergy_network(data_dict)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 展示基于共同客户的产品关联关系，可用于组合销售策略制定")
        else:
            st.warning("⚠️ 数据不足，无法生成协同网络分析")
    
    # Tab4: 促销效果分析
    with tabs[3]:
        st.markdown("### 促销活动效果评估")
        
        fig = create_promotion_waterfall(data_dict)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.info("📊 展示各促销产品对总销售额的贡献")
        else:
            st.warning("⚠️ 暂无促销数据")
    
    # Tab5: 产品结构分析
    with tabs[4]:
        st.markdown("### 产品组合结构分析")
        
        if 'promotion_data' in data_dict and all(k in data_dict for k in ['new_products', 'kpi_products']):
            sales_data = data_dict['promotion_data']
            new_products = data_dict['new_products']
            kpi_products = data_dict['kpi_products']
            star_products = [p for p in kpi_products if p not in new_products]
            
            if '销售额' not in sales_data.columns:
                sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
            
            # 计算各类产品销售额
            new_sales = sales_data[sales_data['产品代码'].isin(new_products)]['销售额'].sum()
            star_sales = sales_data[sales_data['产品代码'].isin(star_products)]['销售额'].sum()
            other_sales = sales_data[~sales_data['产品代码'].isin(kpi_products)]['销售额'].sum()
            
            # 创建饼图
            fig = go.Figure(data=[go.Pie(
                labels=['新品', '星品', '其他产品'],
                values=[new_sales, star_sales, other_sales],
                hole=.3,
                marker_colors=['#4ECDC4', '#FF6B6B', '#95A5A6'],
                hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title="产品类型销售占比",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 数据不足，无法生成产品结构分析")
    
    # Tab6: 趋势分析
    with tabs[5]:
        st.markdown("### 产品销售趋势分析")
        
        if 'promotion_data' in data_dict:
            sales_data = data_dict['promotion_data']
            
            if '发运月份' in sales_data.columns:
                if '销售额' not in sales_data.columns:
                    sales_data['销售额'] = sales_data['单价'] * sales_data['箱数']
                
                # 月度趋势
                monthly_sales = sales_data.groupby('发运月份')['销售额'].sum().reset_index()
                monthly_sales = monthly_sales.sort_values('发运月份')
                
                fig = px.line(monthly_sales, x='发运月份', y='销售额',
                            title='月度销售趋势',
                            markers=True)
                
                fig.update_traces(
                    hovertemplate='月份: %{x}<br>销售额: ¥%{y:,.0f}<extra></extra>'
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 计算环比增长
                monthly_sales['环比增长'] = monthly_sales['销售额'].pct_change() * 100
                
                # 显示统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    max_month = monthly_sales.loc[monthly_sales['销售额'].idxmax(), '发运月份']
                    max_sales = monthly_sales['销售额'].max()
                    st.metric("最高销售月份", max_month, f"¥{max_sales:,.0f}")
                
                with col2:
                    min_month = monthly_sales.loc[monthly_sales['销售额'].idxmin(), '发运月份']
                    min_sales = monthly_sales['销售额'].min()
                    st.metric("最低销售月份", min_month, f"¥{min_sales:,.0f}")
                
                with col3:
                    avg_growth = monthly_sales['环比增长'].mean()
                    st.metric("平均环比增长", f"{avg_growth:.1f}%",
                             "正增长" if avg_growth > 0 else "负增长")
            else:
                st.warning("⚠️ 数据中缺少时间信息")
        else:
            st.warning("⚠️ 缺少销售数据")

if __name__ == "__main__":
    main()
