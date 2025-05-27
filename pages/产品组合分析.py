# pages/产品组合分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="产品组合分析 - Trolli SAL",
    page_icon="📦",
    layout="wide"
)

# 自定义CSS样式
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
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* 指标卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* 标签页样式 */
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
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
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
def create_bcg_matrix(data, dimension='national'):
    """创建BCG矩阵分析"""
    sales_df = data['sales_df']
    
    if dimension == 'national':
        # 全国维度BCG分析
        product_analysis = analyze_product_bcg(sales_df)
        fig = plot_bcg_matrix(product_analysis)
        return fig, product_analysis
    else:
        # 区域维度BCG分析
        regions = sales_df['区域'].unique()
        regional_analysis = {}
        for region in regions:
            region_data = sales_df[sales_df['区域'] == region]
            regional_analysis[region] = analyze_product_bcg(region_data)
        return regional_analysis

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

def plot_bcg_matrix(product_df):
    """绘制BCG矩阵图"""
    fig = go.Figure()
    
    colors = {
        'star': '#22c55e',
        'question': '#f59e0b',
        'cow': '#3b82f6',
        'dog': '#94a3b8'
    }
    
    names = {
        'star': '⭐ 明星产品',
        'question': '❓ 问号产品',
        'cow': '🐄 现金牛产品',
        'dog': '🐕 瘦狗产品'
    }
    
    for category in ['star', 'question', 'cow', 'dog']:
        cat_data = product_df[product_df['category'] == category]
        if len(cat_data) > 0:
            fig.add_trace(go.Scatter(
                x=cat_data['market_share'],
                y=cat_data['growth_rate'],
                mode='markers+text',
                name=names[category],
                marker=dict(
                    size=cat_data['sales'].apply(lambda x: max(min(np.sqrt(x)/50, 80), 20)),
                    color=colors[category],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=cat_data['name'].apply(lambda x: x[:8]),
                textposition='middle center',
                hovertemplate='<b>%{text}</b><br>市场份额: %{x:.1f}%<br>增长率: %{y:.1f}%<extra></extra>'
            ))
    
    # 添加分割线
    fig.add_hline(y=20, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 添加象限标注
    fig.add_annotation(x=0.75, y=40, text="问号产品<br>低份额·高增长", showarrow=False)
    fig.add_annotation(x=3, y=40, text="明星产品<br>高份额·高增长", showarrow=False)
    fig.add_annotation(x=0.75, y=5, text="瘦狗产品<br>低份额·低增长", showarrow=False)
    fig.add_annotation(x=3, y=5, text="现金牛产品<br>高份额·低增长", showarrow=False)
    
    fig.update_layout(
        title="BCG产品矩阵分析",
        xaxis_title="市场份额 (%)",
        yaxis_title="市场增长率 (%)",
        height=600,
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

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
        
        # 指标展示
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
        
        # 第二行指标
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("🌟 新品占比", f"{metrics['new_ratio']:.1f}%", "新品销售额占比")
        
        with col6:
            st.metric("⭐ 星品占比", f"{metrics['star_ratio']:.1f}%", "星品销售额占比")
        
        with col7:
            st.metric("🎯 星品&新品总占比", f"{metrics['total_ratio']:.1f}%", 
                     "✅ 超过20%目标" if metrics['total_ratio'] >= 20 else "❌ 未达标")
        
        with col8:
            # 计算促销有效性
            promo_results = analyze_promotion_effectiveness(data)
            effectiveness = (promo_results['is_effective'].sum() / len(promo_results) * 100) if len(promo_results) > 0 else 0
            st.metric("🚀 全国促销有效性", f"{effectiveness:.1f}%", "基于全国促销活动数据")
    
    # Tab 2: BCG产品矩阵
    with tabs[1]:
        bcg_dimension = st.radio("选择分析维度", ["🌏 全国维度", "🗺️ 分区域维度"], horizontal=True)
        
        if bcg_dimension == "🌏 全国维度":
            fig, product_analysis = create_bcg_matrix(data, 'national')
            st.plotly_chart(fig, use_container_width=True)
            
            # JBP符合度分析
            total_sales = product_analysis['sales'].sum()
            cow_sales = product_analysis[product_analysis['category'] == 'cow']['sales'].sum()
            star_question_sales = product_analysis[product_analysis['category'].isin(['star', 'question'])]['sales'].sum()
            dog_sales = product_analysis[product_analysis['category'] == 'dog']['sales'].sum()
            
            cow_ratio = cow_sales / total_sales * 100
            star_question_ratio = star_question_sales / total_sales * 100
            dog_ratio = dog_sales / total_sales * 100
            
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
            regional_analysis = create_bcg_matrix(data, 'regional')
            
            # 显示区域BCG分析
            regions = list(regional_analysis.keys())
            selected_region = st.selectbox("选择区域", regions)
            
            if selected_region:
                region_data = regional_analysis[selected_region]
                fig = plot_bcg_matrix(region_data)
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: 全国促销活动有效性
    with tabs[2]:
        promo_results = analyze_promotion_effectiveness(data)
        
        if len(promo_results) > 0:
            # 创建柱状图
            fig = go.Figure()
            
            colors = ['#10b981' if eff else '#ef4444' for eff in promo_results['is_effective']]
            
            fig.add_trace(go.Bar(
                x=promo_results['product'],
                y=promo_results['sales'],
                marker_color=colors,
                text=[f"¥{sales:,.0f}" for sales in promo_results['sales']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>4月销售额: ¥%{y:,.0f}<br><extra></extra>'
            ))
            
            effectiveness_rate = promo_results['is_effective'].sum() / len(promo_results) * 100
            
            fig.update_layout(
                title=f"全国促销活动总体有效率: {effectiveness_rate:.1f}% ({promo_results['is_effective'].sum()}/{len(promo_results)})",
                xaxis_title="促销产品",
                yaxis_title="销售额 (¥)",
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示详细分析
            with st.expander("📊 详细分析", expanded=True):
                for _, row in promo_results.iterrows():
                    st.write(f"**{row['product']}**: {row['reason']}")
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
            # 计算各区域星品新品占比
            region_stats = []
            for region in sales_df['区域'].unique():
                region_data = sales_df[sales_df['区域'] == region]
                total_sales = region_data['销售额'].sum()
                star_new_sales = region_data[region_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                region_stats.append({
                    'region': region,
                    'ratio': ratio,
                    'achieved': ratio >= 20
                })
            
            region_df = pd.DataFrame(region_stats)
            
            # 创建柱状图
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in region_df['achieved']]
            
            fig.add_trace(go.Bar(
                x=region_df['region'],
                y=region_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in region_df['ratio']],
                textposition='outside'
            ))
            
            fig.add_hline(y=20, line_dash="dash", line_color="red", 
                         annotation_text="目标线 20%", annotation_position="right")
            
            fig.update_layout(
                title="各区域星品&新品占比达成情况",
                xaxis_title="销售区域",
                yaxis_title="占比 (%)",
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif view_type == "按销售员":
            # 计算各销售员星品新品占比
            salesperson_stats = []
            for person in sales_df['销售员'].unique():
                person_data = sales_df[sales_df['销售员'] == person]
                total_sales = person_data['销售额'].sum()
                star_new_sales = person_data[person_data['产品代码'].isin(star_new_products)]['销售额'].sum()
                ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                
                salesperson_stats.append({
                    'salesperson': person,
                    'ratio': ratio,
                    'achieved': ratio >= 20
                })
            
            person_df = pd.DataFrame(salesperson_stats).sort_values('ratio', ascending=False).head(10)
            
            # 创建柱状图
            fig = go.Figure()
            
            colors = ['#10b981' if ach else '#f59e0b' for ach in person_df['achieved']]
            
            fig.add_trace(go.Bar(
                x=person_df['salesperson'],
                y=person_df['ratio'],
                marker_color=colors,
                text=[f"{r:.1f}%" for r in person_df['ratio']],
                textposition='outside'
            ))
            
            fig.add_hline(y=20, line_dash="dash", line_color="red", 
                         annotation_text="目标线 20%", annotation_position="right")
            
            fig.update_layout(
                title="TOP10销售员星品&新品占比达成情况",
                xaxis_title="销售员",
                yaxis_title="占比 (%)",
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
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
                        'ratio': ratio
                    })
            
            trend_df = pd.DataFrame(monthly_stats)
            
            # 创建趋势图
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=trend_df['month'],
                y=trend_df['ratio'],
                mode='lines+markers',
                name='星品&新品占比',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
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
    
    # Tab 5: 产品关联分析
    with tabs[4]:
        st.info("🔗 产品关联分析功能开发中...")
        
        # 模拟关联分析数据展示
        col1, col2 = st.columns(2)
        
        with col1:
            # 关联规则示例
            st.subheader("🎯 TOP关联规则")
            rules_data = {
                '规则': ['午餐袋 → 酸恐龙', '彩蝶虫 → 扭扭虫', '草莓Q → 葡萄Q'],
                '支持度': [0.15, 0.12, 0.18],
                '置信度': [0.75, 0.82, 0.68],
                '提升度': [2.5, 3.2, 2.7]
            }
            st.dataframe(pd.DataFrame(rules_data))
        
        with col2:
            # 关联强度可视化
            st.subheader("📊 关联强度分布")
            fig = go.Figure(data=go.Scatter(
                x=[0.6, 0.65, 0.7, 0.75, 0.8, 0.85],
                y=[2, 4, 6, 8, 5, 3],
                mode='markers',
                marker=dict(size=15, color='#667eea')
            ))
            fig.update_layout(
                xaxis_title="置信度",
                yaxis_title="规则数量",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 6: 漏铺市分析
    with tabs[5]:
        st.info("📍 漏铺市分析功能开发中...")
        
        # 覆盖率雷达图示例
        categories = ['华北', '华南', '华东', '华西', '华中']
        values = [85, 78, 92, 73, 88]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='产品覆盖率',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title="各区域产品覆盖率",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 7: 季节性分析
    with tabs[6]:
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
            selected_products = data['sales_df']['产品代码'].unique()[:8]  # 显示前8个产品
        
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
                        'month': f'2024-{month:02d}',
                        'sales': month_sales
                    })
        
        if monthly_data:
            trend_df = pd.DataFrame(monthly_data)
            
            # 创建季节性趋势图
            fig = px.line(trend_df, x='month', y='sales', color='product',
                         title=f"产品季节性趋势分析 - {product_filter}",
                         labels={'sales': '销售额 (¥)', 'month': '月份'})
            
            fig.update_traces(mode='lines+markers')
            fig.update_layout(height=600, hovermode='x unified')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 季节性洞察
            st.subheader("🔍 季节性洞察")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("🌸 **春季表现**: 3-5月是新品推广的黄金期，建议加大市场投入")
            
            with col2:
                st.info("☀️ **夏季表现**: 6-8月为销售高峰期，需要提前备货确保供应")

if __name__ == "__main__":
    main()
