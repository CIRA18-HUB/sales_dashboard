# app.py - 欢迎页(负责登录和显示核心指标)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import time

# 导入统一配置
from config import (
    COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, load_data_files, create_filters, add_chart_explanation,
    create_flip_card, setup_page
)

# 设置页面
setup_page()

# 检查认证
if not check_authentication():
    st.stop()

# 显示标题与更新信息
st.markdown('<div class="main-header">销售数据分析仪表盘</div>', unsafe_allow_html=True)

# 显示更新时间提示
st.info("⏰ 数据每周一17:00更新", icon="ℹ️")

# 加载数据
with st.spinner("正在加载数据..."):
    data = load_data_files()

if not data:
    st.error("无法加载数据文件，请检查文件路径")
    st.stop()

# 添加欢迎信息
st.markdown("""
### 欢迎使用销售数据分析仪表盘

这个仪表盘提供了销售数据的全面分析，帮助您做出更好的业务决策。

点击左侧导航栏可以切换到不同的分析页面：
- **销售总览**: 销售趋势、目标达成、渠道分析
- **客户分析**: 客户分布、客户价值分析
- **产品分析**: BCG矩阵、产品组合优化
- **库存分析**: 库存周转、健康度分析
- **物料分析**: 物料消耗与费用趋势
- **新品分析**: 新品销售表现与渗透率
""")

# 显示每个页面的核心指标
st.subheader("核心业务指标")

# 提取各页面核心指标
sales_data = data['sales_orders']
current_year = datetime.now().year
ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]

# 销售总览页核心指标 - 销售总额
total_sales = ytd_sales['销售额'].sum() if 'sales_orders' in data else 0

# 客户分析页核心指标 - 客户总数
total_customers = ytd_sales['客户代码'].nunique() if 'sales_orders' in data else 0

# 产品分析页核心指标 - BCG健康度
# 简单计算一个产品健康度指数
product_codes = data.get('product_codes', [])
if product_codes:
    bcg_sales = ytd_sales[ytd_sales['产品代码'].isin(product_codes)].copy()

    # 计算每个产品的销售额和占比
    product_sales = bcg_sales.groupby(['产品代码', '产品简称'])['销售额'].sum().reset_index()
    product_sales['销售占比'] = product_sales['销售额'] / product_sales['销售额'].sum() * 100

    # 计算去年销售数据
    last_year_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year - 1]
    if not last_year_sales.empty:
        last_year_product_sales = last_year_sales.groupby(['产品代码'])['销售额'].sum().reset_index()
        last_year_product_sales.rename(columns={'销售额': '去年销售额'}, inplace=True)

        # 合并今年和去年的销售数据
        product_sales = product_sales.merge(last_year_product_sales, on='产品代码', how='left')
        product_sales['去年销售额'] = product_sales['去年销售额'].fillna(0)

        # 计算增长率
        product_sales['增长率'] = (product_sales['销售额'] - product_sales['去年销售额']) / product_sales[
            '去年销售额'] * 100
        product_sales['增长率'] = product_sales['增长率'].fillna(0)
        product_sales.loc[product_sales['去年销售额'] == 0, '增长率'] = 100
    else:
        # 无去年数据时设置默认增长率
        product_sales['增长率'] = 0

    # 分类产品
    product_sales['BCG分类'] = product_sales.apply(
        lambda row: '明星产品' if row['销售占比'] >= 1.5 and row['增长率'] >= 20
        else '现金牛产品' if row['销售占比'] >= 1.5 and row['增长率'] < 20
        else '问号产品' if row['销售占比'] < 1.5 and row['增长率'] >= 20
        else '瘦狗产品',
        axis=1
    )

    # 计算各类产品的销售占比
    bcg_summary = product_sales.groupby('BCG分类')['销售额'].sum().reset_index()
    bcg_summary['销售占比'] = bcg_summary['销售额'] / bcg_summary['销售额'].sum() * 100

    # 计算健康度指标
    cash_cow_percent = bcg_summary.loc[
        bcg_summary['BCG分类'] == '现金牛产品', '销售占比'].sum() if not bcg_summary.empty else 0
    star_question_percent = bcg_summary.loc[
        bcg_summary['BCG分类'].isin(['明星产品', '问号产品']), '销售占比'].sum() if not bcg_summary.empty else 0
    dog_percent = bcg_summary.loc[
        bcg_summary['BCG分类'] == '瘦狗产品', '销售占比'].sum() if not bcg_summary.empty else 0

    # 判断是否符合健康产品组合
    is_healthy_mix = (
            (45 <= cash_cow_percent <= 50) and
            (40 <= star_question_percent <= 45) and
            (dog_percent <= 10)
    )

    bcg_health_score = 100 - (
            abs(cash_cow_percent - 47.5) * 1.5 +  # 理想值47.5%的偏差
            abs(star_question_percent - 42.5) * 1.5 +  # 理想值42.5%的偏差
            max(0, dog_percent - 10) * 3  # 瘦狗产品超出10%的惩罚
    )

    bcg_health = max(0, min(100, bcg_health_score))
else:
    bcg_health = 0

# 库存分析页核心指标 - 库存总价值
inventory_data = data.get('inventory_data', pd.DataFrame())
if not inventory_data.empty and '现有库存' in inventory_data.columns and '单价（箱）' in ytd_sales.columns:
    # 创建产品代码到单价的映射
    price_map = ytd_sales.groupby('产品代码')['单价（箱）'].mean().to_dict()

    # 合并库存数据与单价
    product_inventory = inventory_data[inventory_data['物料'].str.startswith('F', na=False)].copy()
    product_inventory['单价'] = product_inventory['物料'].map(price_map)
    product_inventory['库存价值'] = product_inventory['现有库存'] * product_inventory['单价']

    total_inventory_value = product_inventory['库存价值'].sum()
else:
    total_inventory_value = 0

# 物料分析页核心指标 - 物料费用总额
expense_orders = data.get('expense_orders', pd.DataFrame())
if not expense_orders.empty and '求和项:金额（元）' in expense_orders.columns:
    material_expense = expense_orders[expense_orders['订单类型'] == '物料']['求和项:金额（元）'].sum()
else:
    material_expense = 0

# 新品分析页核心指标 - 新品销售额
new_product_codes = data.get('new_product_codes', [])
if new_product_codes:
    new_product_sales = ytd_sales[ytd_sales['产品代码'].isin(new_product_codes)]['销售额'].sum()
else:
    new_product_sales = 0

# 创建指标卡片行
col1, col2, col3 = st.columns(3)

with col1:
    sales_layer = create_flip_card(
        "total_sales",
        "销售总额",
        total_sales,
        "销售总览页",
        is_currency=True
    )

    if sales_layer == 1:  # 第二层：图表分析
        st.markdown("#### 销售总览")

        # 计算月度趋势
        ytd_sales['月份'] = ytd_sales['发运月份'].dt.month
        monthly_sales = ytd_sales.groupby('月份')['销售额'].sum().reset_index()

        # 创建月度趋势图
        fig = px.line(
            monthly_sales,
            x='月份',
            y='销售额',
            title='月度销售趋势',
            markers=True,
            color_discrete_sequence=[COLORS['primary']]
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            height=300,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="月份",
            yaxis_title="销售额（元）"
        )

        st.plotly_chart(fig, use_container_width=True)

        add_chart_explanation("""
        <b>图表解读：</b> 月度销售趋势反映了业务的季节性和增长情况。分析销售高峰和低谷，可以帮助我们优化资源配置和制定有针对性的销售策略。
        <b>建议：</b> 点击左侧导航栏的 "销售总览" 页面，查看更详细的销售分析。
        """)

    elif sales_layer == 2:  # 第三层：深度分析
        st.markdown("#### 销售总额深度分析")

        # 渠道分布
        mt_sales = ytd_sales[ytd_sales['渠道'] == 'MT']['销售额'].sum()
        tt_sales = ytd_sales[ytd_sales['渠道'] == 'TT']['销售额'].sum()

        channel_data = pd.DataFrame({
            '渠道': ['MT渠道', 'TT渠道'],
            '销售额': [mt_sales, tt_sales]
        })

        # 创建渠道分布饼图
        fig = px.pie(
            channel_data,
            names='渠道',
            values='销售额',
            title='渠道销售占比',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
            hole=0.3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        add_chart_explanation("""
        <b>深度分析：</b> 销售额分析需要结合渠道、客户、产品等多维度一起看才能获得全面理解。
        <b>行动建议：</b> 前往「销售总览」页面进行更详细的分析，包括目标达成率、同比增长等关键指标。
        """)

with col2:
    customer_layer = create_flip_card(
        "total_customers",
        "客户总数",
        total_customers,
        "客户分析页",
        is_number=True
    )

    if customer_layer == 1:  # 第二层：图表分析
        st.markdown("#### 客户分析")

        # 计算区域客户分布
        region_customers = ytd_sales.groupby('所属区域')['客户代码'].nunique().reset_index()
        region_customers.columns = ['所属区域', '客户数量']
        region_customers = region_customers.sort_values('客户数量', ascending=False)

        # 创建区域客户分布图
        fig = px.bar(
            region_customers,
            x='所属区域',
            y='客户数量',
            title='区域客户分布',
            color='所属区域',
            text='客户数量'
        )

        fig.update_traces(
            textposition='outside'
        )

        fig.update_layout(
            height=300,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="区域",
            yaxis_title="客户数量",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        add_chart_explanation("""
        <b>图表解读：</b> 区域客户分布反映了不同区域的客户覆盖情况。客户数量多的区域表明市场渗透度高，但也需关注客户质量和单客价值。
        <b>建议：</b> 点击左侧导航栏的 "客户分析" 页面，查看更详细的客户价值和分布分析。
        """)

    elif customer_layer == 2:  # 第三层：深度分析
        st.markdown("#### 客户深度分析")

        # 计算客户集中度
        customer_sales = ytd_sales.groupby('客户代码')['销售额'].sum().reset_index()
        customer_sales = customer_sales.sort_values('销售额', ascending=False)

        top5_customers = customer_sales.head(5)
        top5_sales = top5_customers['销售额'].sum()
        total_sales_val = customer_sales['销售额'].sum()

        concentration_ratio = (top5_sales / total_sales_val * 100) if total_sales_val > 0 else 0

        st.metric(
            "TOP5客户集中度",
            f"{concentration_ratio:.1f}%",
            help="前5大客户的销售额占总销售额的比例"
        )

        add_chart_explanation("""
        <b>深度分析：</b> 客户集中度反映了业务对大客户的依赖程度。过高的集中度可能带来风险，但也意味着关键客户关系管理的重要性。
        <b>行动建议：</b> 前往「客户分析」页面查看完整的客户价值分析、忠诚度和增长潜力评估。
        """)

with col3:
    product_layer = create_flip_card(
        "bcg_health",
        "产品组合健康度",
        bcg_health,
        "产品分析页",
        is_percentage=True
    )

    if product_layer == 1:  # 第二层：图表分析
        st.markdown("#### 产品组合分析")

        if 'bcg_summary' in locals() and not bcg_summary.empty:
            # 创建BCG分类饼图
            fig = px.pie(
                bcg_summary,
                names='BCG分类',
                values='销售占比',
                title='BCG产品组合分析',
                color='BCG分类',
                color_discrete_map={
                    '明星产品': '#FFD700',  # 金色
                    '现金牛产品': '#4CAF50',  # 绿色
                    '问号产品': '#2196F3',  # 蓝色
                    '瘦狗产品': '#F44336'  # 红色
                },
                hole=0.3
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hoverinfo='label+percent+value'
            )

            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=60, b=20),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)

            add_chart_explanation(f"""
            <b>图表解读：</b> BCG产品组合分析反映了产品结构的健康度。理想结构为：现金牛产品45-50%，明星和问号产品40-45%，瘦狗产品≤10%。
            <b>当前状态：</b> 现金牛产品{cash_cow_percent:.1f}%，明星和问号产品{star_question_percent:.1f}%，瘦狗产品{dog_percent:.1f}%。
            <b>建议：</b> 点击左侧导航栏的 "产品分析" 页面，查看详细的BCG矩阵分析。
            """)
        else:
            st.warning("暂无足够的产品数据进行BCG分析")

    elif product_layer == 2:  # 第三层：深度分析
        st.markdown("#### 产品深度分析")

        if 'product_sales' in locals() and not product_sales.empty:
            # 获取TOP5产品
            top_products = product_sales.sort_values('销售额', ascending=False).head(5)

            # 创建TOP5产品柱状图
            fig = px.bar(
                top_products,
                x='产品简称',
                y='销售额',
                title='TOP5热销产品',
                color='BCG分类',
                color_discrete_map={
                    '明星产品': '#FFD700',  # 金色
                    '现金牛产品': '#4CAF50',  # 绿色
                    '问号产品': '#2196F3',  # 蓝色
                    '瘦狗产品': '#F44336'  # 红色
                },
                text='销售额'
            )

            fig.update_traces(
                texttemplate='%{y:,.0f}',
                textposition='outside'
            )

            fig.update_layout(
                height=300,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="产品",
                yaxis_title="销售额（元）"
            )

            st.plotly_chart(fig, use_container_width=True)

            add_chart_explanation("""
            <b>深度分析：</b> 产品组合健康度评估是一种战略性分析，需要结合增长率、市场份额和生命周期一起考量。
            <b>行动建议：</b> 前往「产品分析」页面查看完整的BCG矩阵分析、产品生命周期评估和未来产品规划建议。
            """)
        else:
            st.warning("暂无足够的产品数据进行深度分析")

# 第二行指标卡
col1, col2, col3 = st.columns(3)

with col1:
    inventory_layer = create_flip_card(
        "inventory_value",
        "库存总价值",
        total_inventory_value,
        "库存分析页",
        is_currency=True
    )

    if inventory_layer == 1:  # 第二层：图表分析
        st.markdown("#### 库存分析")

        if not inventory_data.empty:
            # 计算库存占比
            product_inventory_summary = product_inventory.groupby('物料')['库存价值'].sum().reset_index()
            product_inventory_summary = product_inventory_summary.sort_values('库存价值', ascending=False).head(10)

            # 创建库存占比图
            fig = px.pie(
                product_inventory_summary,
                names='物料',
                values='库存价值',
                title='TOP10产品库存价值占比',
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hoverinfo='label+percent+value'
            )

            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=60, b=20),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)

            add_chart_explanation("""
            <b>图表解读：</b> 库存分布显示了不同产品的库存价值比例。高库存值产品需特别关注周转率和过期风险。
            <b>建议：</b> 点击左侧导航栏的 "库存分析" 页面，查看更详细的库存健康度和周转分析。
            """)
        else:
            st.warning("暂无库存数据")

    elif inventory_layer == 2:  # 第三层：深度分析
        st.markdown("#### 库存深度分析")

        if not inventory_data.empty:
            # 计算库存与销售比例
            # 获取当月销售数据
            current_month = datetime.now().month
            current_year = datetime.now().year

            monthly_sales = ytd_sales[
                (ytd_sales['发运月份'].dt.month == current_month) &
                (ytd_sales['发运月份'].dt.year == current_year)
                ]

            if not monthly_sales.empty:
                monthly_sales_amount = monthly_sales['销售额'].sum()
                inventory_sales_ratio = (
                            total_inventory_value / monthly_sales_amount) if monthly_sales_amount > 0 else 0

                st.metric(
                    "库存销售比",
                    f"{inventory_sales_ratio:.1f}个月",
                    help="库存总价值相当于当月销售额的倍数，反映库存可支撑销售的时间"
                )

            add_chart_explanation("""
            <b>深度分析：</b> 库存管理需要平衡供应保障和周转效率。过高的库存会占用资金并增加跌价风险，过低则可能导致断货。
            <b>行动建议：</b> 前往「库存分析」页面查看完整的库存周转分析，了解库存结构和老化风险，并获取优化建议。
            """)
        else:
            st.warning("暂无库存数据进行深度分析")

with col2:
    material_layer = create_flip_card(
        "material_expense",
        "物料费用总额",
        material_expense,
        "物料分析页",
        is_currency=True
    )

    if material_layer == 1:  # 第二层：图表分析
        st.markdown("#### 物料分析")

        if not expense_orders.empty:
            # 按促销类型分析费用
            promotion_expenses = expense_orders[expense_orders['订单类型'] != '物料'].copy()
            promotion_expenses = promotion_expenses.groupby('订单类型')['求和项:金额（元）'].sum().reset_index()
            promotion_expenses = promotion_expenses.sort_values('求和项:金额（元）', ascending=False)

            # 创建促销费用图表
            fig = px.bar(
                promotion_expenses,
                x='订单类型',
                y='求和项:金额（元）',
                title='促销费用分布',
                color='订单类型',
                text='求和项:金额（元）'
            )

            fig.update_traces(
                texttemplate='%{y:,.0f}',
                textposition='outside'
            )

            fig.update_layout(
                height=300,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="促销类型",
                yaxis_title="费用（元）",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            add_chart_explanation("""
            <b>图表解读：</b> 促销费用分布显示了不同促销类型的投入比例。分析促销投入与销售回报，优化资源配置，提高促销ROI。
            <b>建议：</b> 点击左侧导航栏的 "物料分析" 页面，查看更详细的物料与促销分析。
            """)
        else:
            st.warning("暂无物料费用数据")

    elif material_layer == 2:  # 第三层：深度分析
        st.markdown("#### 物料深度分析")

        if not expense_orders.empty:
            # 计算物料费用占销售比例
            material_sales_ratio = (material_expense / total_sales * 100) if total_sales > 0 else 0

            st.metric(
                "物料费用率",
                f"{material_sales_ratio:.2f}%",
                help="物料费用占总销售额的比例"
            )

            add_chart_explanation("""
            <b>深度分析：</b> 物料费用管理需要平衡成本控制和销售支持。合理的物料投入可以提升品牌形象和销售转化率。
            <b>行动建议：</b> 前往「物料分析」页面查看完整的物料使用效率分析，了解不同物料类型的ROI，优化物料策略。
            """)
        else:
            st.warning("暂无物料费用数据进行深度分析")

with col3:
    new_product_layer = create_flip_card(
        "new_product_sales",
        "新品销售额",
        new_product_sales,
        "新品分析页",
        is_currency=True
    )

    if new_product_layer == 1:  # 第二层：图表分析
        st.markdown("#### 新品分析")

        if new_product_codes:
            # 计算新品销售占比
            new_product_percentage = (new_product_sales / total_sales * 100) if total_sales > 0 else 0

            # 创建新品与非新品销售占比图
            fig = px.pie(
                names=['新品', '非新品'],
                values=[new_product_sales, total_sales - new_product_sales],
                title="新品与非新品销售占比",
                color_discrete_sequence=[COLORS['success'], COLORS['secondary']]
            )

            fig.update_traces(
                textinfo='percent+label',
                hovertemplate='%{label}: %{value:,.2f}元 (%{percent})'
            )

            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=60, b=20),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)

            add_chart_explanation(f"""
            <b>图表解读：</b> 新品销售占比为{new_product_percentage:.1f}%，反映了新品的市场接受度和业务创新能力。
            <b>建议：</b> 点击左侧导航栏的 "新品分析" 页面，查看更详细的新品渗透率和表现分析。
            """)
        else:
            st.warning("暂无新品数据")

    elif new_product_layer == 2:  # 第三层：深度分析
        st.markdown("#### 新品深度分析")

        if new_product_codes:
            # 计算新品客户数
            new_product_customers = ytd_sales[ytd_sales['产品代码'].isin(new_product_codes)]['客户代码'].nunique()
            new_customer_percentage = (new_product_customers / total_customers * 100) if total_customers > 0 else 0

            st.metric(
                "新品客户渗透率",
                f"{new_customer_percentage:.1f}%",
                help="购买新品的客户数占总客户数的比例"
            )

            add_chart_explanation("""
            <b>深度分析：</b> 新品是业务增长和创新的重要驱动力。新品表现反映了产品创新能力和市场接受度。
            <b>行动建议：</b> 前往「新品分析」页面查看完整的新品渗透分析，了解不同客户群体对新品的接受程度，优化新品推广策略。
            """)
        else:
            st.warning("暂无新品数据进行深度分析")

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)