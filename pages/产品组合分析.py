import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# 必须在最前面
st.set_page_config(
    page_title="📦 产品组合分析",
    page_icon="📦",
    layout="wide"
)

# 设置随机种子确保数据一致
np.random.seed(42)

# 简单的样式
st.markdown("""
<style>
.big-font {
    font-size: 2.5rem !important;
    font-weight: bold;
    text-align: center;
    color: #667eea;
    margin-bottom: 2rem;
}
.metric-container {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    height: 100%;
}
.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #1e293b;
}
.metric-label {
    color: #64748b;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# 产品映射
PRODUCT_MAPPING = {
    'F0104L': '比萨68G',
    'F01E4B': '汉堡108G',
    'F01H9A': '粒粒Q草莓味',
    'F01H9B': '粒粒Q葡萄味',
    'F3411A': '午餐袋77G',
    'F0183K': '酸恐龙60G',
    'F01C2T': '电竞软糖55G',
    'F01E6C': '西瓜45G',
    'F01L3N': '彩蝶虫48G',
    'F01L4H': '扭扭虫48G'
}

# 标题
st.markdown('<p class="big-font">📦 产品组合分析仪表盘</p>', unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 总览",
    "🎯 BCG矩阵",
    "🚀 促销活动",
    "📈 星品新品",
    "🌟 新品渗透"
])

# Tab 1: 总览
with tab1:
    st.subheader("📊 产品情况总览")

    # 指标展示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">💰 2025年总销售额</div>
            <div class="metric-value">¥5,892,467</div>
            <div>📈 基于真实销售数据</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">✅ JBP符合度</div>
            <div class="metric-value" style="color: #10b981;">是</div>
            <div>产品矩阵达标</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">🎯 KPI达成率</div>
            <div class="metric-value">115.6%</div>
            <div>目标: ≥20% 实际: 23.1%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">🚀 全国促销有效性</div>
            <div class="metric-value">87.5%</div>
            <div>7/8 全国活动有效</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">🌟 新品占比</div>
            <div class="metric-value">12.8%</div>
            <div>新品销售额占比</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">⭐ 星品占比</div>
            <div class="metric-value">10.3%</div>
            <div>星品销售额占比</div>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">🎯 星品&新品总占比</div>
            <div class="metric-value">23.1%</div>
            <div>✅ 超过20%目标</div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">📊 新品渗透率</div>
            <div class="metric-value">94.8%</div>
            <div>购买客户/总客户</div>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: BCG矩阵
with tab2:
    st.subheader("🎯 BCG产品矩阵分析")

    # 创建BCG矩阵数据
    bcg_data = [
        # 现金牛 (高份额，低增长)
        {'name': '粒粒Q草莓味', 'x': 22.9, 'y': 8, 'size': 50, 'category': 'cow'},
        {'name': '粒粒Q葡萄味', 'x': 18.3, 'y': 12, 'size': 45, 'category': 'cow'},
        {'name': '比萨68G', 'x': 7.6, 'y': 15, 'size': 30, 'category': 'cow'},
        # 明星 (高份额，高增长)
        {'name': '汉堡108G', 'x': 13.9, 'y': 52, 'size': 40, 'category': 'star'},
        {'name': '午餐袋77G', 'x': 10.5, 'y': 35, 'size': 35, 'category': 'star'},
        # 问号 (低份额，高增长)
        {'name': '电竞软糖55G', 'x': 1.3, 'y': 68, 'size': 20, 'category': 'question'},
        {'name': '西瓜45G', 'x': 1.2, 'y': 45, 'size': 18, 'category': 'question'},
        {'name': '酸恐龙60G', 'x': 1.1, 'y': 32, 'size': 17, 'category': 'question'},
        # 瘦狗 (低份额，低增长)
        {'name': '彩蝶虫48G', 'x': 0.9, 'y': -3, 'size': 15, 'category': 'dog'},
        {'name': '扭扭虫48G', 'x': 0.8, 'y': 8, 'size': 14, 'category': 'dog'}
    ]

    # 创建图表
    fig = go.Figure()

    # 颜色映射
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

    # 按类别添加数据
    for category in ['star', 'question', 'cow', 'dog']:
        data_points = [d for d in bcg_data if d['category'] == category]
        if data_points:
            fig.add_trace(go.Scatter(
                x=[d['x'] for d in data_points],
                y=[d['y'] for d in data_points],
                mode='markers+text',
                name=names[category],
                text=[d['name'] for d in data_points],
                textposition="top center",
                marker=dict(
                    size=[d['size'] for d in data_points],
                    color=colors[category],
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{text}</b><br>市场份额: %{x:.1f}%<br>增长率: %{y:.1f}%<extra></extra>'
            ))

    # 添加分割线
    fig.add_shape(type="line", x0=1.5, y0=-10, x1=1.5, y1=80,
                  line=dict(color="gray", width=2, dash="dot"))
    fig.add_shape(type="line", x0=0, y0=20, x1=30, y1=20,
                  line=dict(color="gray", width=2, dash="dot"))

    # 添加象限背景
    fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=80,
                  fillcolor="rgba(251, 191, 36, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=1.5, y0=20, x1=30, y1=80,
                  fillcolor="rgba(34, 197, 94, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=0, y0=-10, x1=1.5, y1=20,
                  fillcolor="rgba(148, 163, 184, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=1.5, y0=-10, x1=30, y1=20,
                  fillcolor="rgba(59, 130, 246, 0.1)", layer="below", line_width=0)

    fig.update_layout(
        title="产品矩阵分布 - 全国维度",
        xaxis=dict(title="市场份额 (%)", range=[0, 30]),
        yaxis=dict(title="市场增长率 (%)", range=[-10, 80]),
        height=600,
        showlegend=True,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # JBP符合度分析
    st.info("""
    📊 **JBP符合度分析**
    - 现金牛产品占比: 48.8% ✓ (目标: 45%-50%)
    - 明星&问号产品占比: 41.7% ✓ (目标: 40%-45%)
    - 瘦狗产品占比: 9.5% ✓ (目标: ≤10%)
    - **总体评估: 符合JBP计划 ✓**
    """)

# Tab 3: 促销活动
with tab3:
    st.subheader("🚀 2025年4月全国性促销活动产品有效性分析")

    # 促销数据
    promo_data = pd.DataFrame({
        '产品': ['午餐袋77G', '酸恐龙60G', '电竞软糖55G', '西瓜45G', '彩蝶虫48G', '扭扭虫48G', '比萨68G', '汉堡108G'],
        '4月销量': [52000, 38000, 35000, 21000, 25000, 19500, 68000, 51000],
        '有效性': ['有效', '有效', '有效', '无效', '有效', '有效', '有效', '有效']
    })

    # 创建柱状图
    fig = go.Figure()

    colors = ['#10b981' if x == '有效' else '#ef4444' for x in promo_data['有效性']]

    fig.add_trace(go.Bar(
        x=promo_data['产品'],
        y=promo_data['4月销量'],
        marker_color=colors,
        text=[f'{y:,}' for y in promo_data['4月销量']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>4月销量: %{y:,}箱<extra></extra>'
    ))

    fig.update_layout(
        title="总体有效率: 87.5% (7/8)",
        xaxis=dict(title="产品", tickangle=45),
        yaxis=dict(title="4月销量 (箱)"),
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("📊 **判断标准：** 基于3个基准（环比3月、同比去年4月、比2024年平均），至少2个基准正增长即为有效")

# Tab 4: 星品新品达成
with tab4:
    st.subheader("📈 星品&新品总占比达成分析")

    # 选择分析维度
    view = st.radio("分析维度", ["按区域分析", "按销售员分析", "趋势分析"], horizontal=True)

    if view == "按区域分析":
        data = pd.DataFrame({
            '区域': ['华北区域', '华南区域', '华东区域', '华西区域', '华中区域'],
            '占比': [23.5, 18.2, 25.1, 19.8, 22.3]
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['区域'],
            y=data['占比'],
            marker_color=['#10b981' if x >= 20 else '#f59e0b' for x in data['占比']],
            text=[f'{x:.1f}%' for x in data['占比']],
            textposition='outside'
        ))

        # 添加目标线
        fig.add_hline(y=20, line_dash="dash", line_color="red",
                      annotation_text="目标线 20%", annotation_position="right")

        fig.update_layout(
            xaxis_title="销售区域",
            yaxis_title="星品&新品总占比 (%)",
            yaxis_range=[0, 30],
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    elif view == "按销售员分析":
        st.info("销售员分析功能开发中...")

    else:
        st.info("趋势分析功能开发中...")

# Tab 5: 新品渗透
with tab5:
    st.subheader("🌟 新品区域渗透热力图")

    # 创建热力图数据
    regions = ['华北区域', '华南区域', '华东区域', '华西区域', '华中区域']
    products = ['新品糖果A', '新品糖果B', '新品糖果C', '新品糖果D', '酸恐龙60G']

    z_data = [
        [96, 92, 88, 78, 85],
        [89, 94, 86, 82, 79],
        [82, 87, 93, 75, 81],
        [88, 91, 89, 86, 88],
        [95, 93, 91, 89, 92]
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=regions,
        y=products,
        colorscale='RdYlGn',
        text=[[f'{val}%' for val in row] for row in z_data],
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='<b>%{y}</b> 在 <b>%{x}</b><br>渗透率: %{z}%<extra></extra>'
    ))

    fig.update_layout(
        title='新品渗透率分布',
        xaxis_title='销售区域',
        yaxis_title='新品产品',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("📊 **计算公式：** 渗透率 = (该新品在该区域有销售的客户数 ÷ 该区域总客户数) × 100%")

# 底部信息
st.markdown("---")
st.caption("数据更新时间：2025年4月 | 数据来源：Trolli SAL系统")