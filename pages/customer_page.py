# pages/customer_page.py - 完全自包含的客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# 导入统一配置
from config import (
    COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, load_data_files, create_filters, add_chart_explanation,
    create_flip_card, setup_page
)

# ==================== 页面配置 ====================
setup_page()

# 检查认证
if not check_authentication():
    st.stop()

# 页面标题
st.title("👥 客户分析")

# 加载数据
data = load_data_files()
if not data:
    st.error("无法加载数据文件，请检查文件路径")
    st.stop()

# 应用筛选器
filtered_data = create_filters(data)
if not filtered_data:
    st.error("应用筛选器失败")
    st.stop()


# ==================== 工具函数 ====================
def calculate_customer_metrics(sales_data, customer_relation=None):
    """计算客户相关指标"""
    if sales_data.empty:
        return {}

    # 基础客户统计
    if 'client_id' in sales_data.columns:
        customer_id_col = 'client_id'
    elif '客户代码' in sales_data.columns:
        customer_id_col = '客户代码'
    else:
        st.error("数据中未找到客户ID列")
        return {}

    # 筛选活跃客户
    active_customers = pd.DataFrame()
    if customer_relation is not None and not customer_relation.empty:
        active_customers = customer_relation[customer_relation['状态'] == '正常']
        active_customer_ids = active_customers['客户代码'].unique() if '客户代码' in active_customers.columns else []
        if active_customer_ids:
            sales_data = sales_data[sales_data[customer_id_col].isin(active_customer_ids)]

    # 客户总数
    total_customers = sales_data[customer_id_col].nunique()

    # 客户销售额统计
    customer_sales = sales_data.groupby(customer_id_col)['销售额'].sum().reset_index()
    customer_sales = customer_sales.sort_values('销售额', ascending=False)

    # 计算TOP5、TOP10客户销售额
    top5_sales = customer_sales.head(5)['销售额'].sum() if len(customer_sales) >= 5 else customer_sales['销售额'].sum()
    top10_sales = customer_sales.head(10)['销售额'].sum() if len(customer_sales) >= 10 else customer_sales[
        '销售额'].sum()

    # 计算总销售额
    total_sales = customer_sales['销售额'].sum()

    # 计算集中度
    top5_concentration = (top5_sales / total_sales * 100) if total_sales > 0 else 0
    top10_concentration = (top10_sales / total_sales * 100) if total_sales > 0 else 0

    # 计算平均客户价值
    avg_customer_value = total_sales / total_customers if total_customers > 0 else 0

    # 计算客户依赖度风险
    dependency_risk_score = top5_concentration  # 简单起见，直接用TOP5集中度作为依赖风险

    # 按区域统计客户
    if '所属区域' in sales_data.columns:
        region_customers = sales_data.groupby('所属区域')[customer_id_col].nunique().reset_index()
        region_customers.columns = ['所属区域', '客户数量']
        region_sales = sales_data.groupby('所属区域')['销售额'].sum().reset_index()

        region_stats = pd.merge(region_customers, region_sales, on='所属区域', how='left')
        region_stats['平均客户价值'] = region_stats['销售额'] / region_stats['客户数量']
    else:
        region_stats = pd.DataFrame()

    # 添加客户销售员关系
    customer_person = pd.DataFrame()
    if '申请人' in sales_data.columns:
        customer_person = sales_data.groupby([customer_id_col, '申请人'])['销售额'].sum().reset_index()
        customer_person = customer_person.sort_values(['客户代码', '销售额'], ascending=[True, False])

        # 找出每个客户的主要销售员
        main_person = customer_person.loc[customer_person.groupby(customer_id_col)['销售额'].idxmax()]
        customer_sales = pd.merge(customer_sales, main_person[[customer_id_col, '申请人']], on=customer_id_col,
                                  how='left')

    # 添加客户产品多样性
    if '产品代码' in sales_data.columns:
        product_diversity = sales_data.groupby(customer_id_col)['产品代码'].nunique().reset_index()
        product_diversity.columns = [customer_id_col, '购买产品种类']
        customer_sales = pd.merge(customer_sales, product_diversity, on=customer_id_col, how='left')

    # 添加客户简称或名称
    if '客户简称' in sales_data.columns:
        customer_names = sales_data.groupby(customer_id_col)['客户简称'].first().reset_index()
        customer_sales = pd.merge(customer_sales, customer_names, on=customer_id_col, how='left')
    elif '经销商名称' in sales_data.columns:
        customer_names = sales_data.groupby(customer_id_col)['经销商名称'].first().reset_index()
        customer_sales = pd.merge(customer_sales, customer_names, on=customer_id_col, how='left')

    return {
        'total_customers': total_customers,
        'top5_concentration': top5_concentration,
        'top10_concentration': top10_concentration,
        'avg_customer_value': avg_customer_value,
        'dependency_risk_score': dependency_risk_score,
        'customer_sales': customer_sales,
        'region_stats': region_stats,
        'customer_person': customer_person
    }


# ==================== 分析数据 ====================
def analyze_customer_data(filtered_data):
    """分析客户数据"""
    sales_data = filtered_data.get('sales_orders', pd.DataFrame())
    customer_relation = filtered_data.get('customer_relation', pd.DataFrame())

    # 获取当前年份数据
    current_year = datetime.now().year
    ytd_sales = sales_data[pd.to_datetime(sales_data['发运月份']).dt.year == current_year]

    # 计算客户指标
    customer_metrics = calculate_customer_metrics(ytd_sales, customer_relation)

    # 添加新品购买客户分析
    new_product_codes = filtered_data.get('new_product_codes', [])
    if new_product_codes:
        new_product_sales = ytd_sales[ytd_sales['产品代码'].isin(new_product_codes)]
        new_product_customers = new_product_sales['客户代码'].nunique()
        customer_metrics['new_product_customers'] = new_product_customers

        # 计算新品客户渗透率
        customer_metrics['new_product_penetration'] = (
                    new_product_customers / customer_metrics['total_customers'] * 100) if customer_metrics[
                                                                                              'total_customers'] > 0 else 0

    return customer_metrics


# ==================== 图表创建函数 ====================
def create_customer_concentration_chart(customer_sales, title="客户销售额分布"):
    """创建客户销售额分布图"""
    if customer_sales.empty:
        return None

    # 只取前10名客户
    top_customers = customer_sales.head(10).copy()
    if '客户简称' in top_customers.columns:
        top_customers['客户'] = top_customers['客户简称']
    elif '经销商名称' in top_customers.columns:
        top_customers['客户'] = top_customers['经销商名称']
    else:
        top_customers['客户'] = top_customers['客户代码']

    fig = px.bar(
        top_customers,
        x='客户',
        y='销售额',
        title=title,
        color='销售额',
        color_continuous_scale=px.colors.sequential.Blues,
        text='销售额'
    )

    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="客户",
        yaxis_title="销售额（元）",
        xaxis={'categoryorder': 'total descending'}
    )

    return fig


def create_concentration_gauge(concentration, title="客户集中度"):
    """创建客户集中度仪表盘"""
    # 确定颜色
    if concentration <= 50:
        color = COLORS['success']
        status = "健康"
    elif concentration <= 70:
        color = COLORS['warning']
        status = "警示"
    else:
        color = COLORS['danger']
        status = "风险"

    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=concentration,
        title={'text': f"{title}<br><span style='font-size:0.8em;color:{color}'>{status}</span>", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(50, 205, 50, 0.3)'},
                {'range': [50, 70], 'color': 'rgba(255, 144, 14, 0.3)'},
                {'range': [70, 100], 'color': 'rgba(255, 67, 54, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )

    return fig


def create_region_customers_chart(region_data, title="区域客户分布"):
    """创建区域客户分布图"""
    if region_data.empty:
        return None

    # 按客户数量排序
    region_data = region_data.sort_values('客户数量', ascending=False)

    fig = px.bar(
        region_data,
        x='所属区域',
        y='客户数量',
        title=title,
        color='所属区域',
        text='客户数量'
    )

    fig.update_traces(
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="区域",
        yaxis_title="客户数量",
        showlegend=False
    )

    return fig


def create_avg_value_bar(region_data, title="区域平均客户价值"):
    """创建区域平均客户价值图"""
    if region_data.empty:
        return None

    # 按平均客户价值排序
    region_data = region_data.sort_values('平均客户价值', ascending=False)

    fig = px.bar(
        region_data,
        x='所属区域',
        y='平均客户价值',
        title=title,
        color='所属区域',
        text='平均客户价值'
    )

    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="区域",
        yaxis_title="平均客户价值（元）",
        showlegend=False
    )

    return fig


def create_customer_scatter(customer_data, title="客户价值与产品多样性"):
    """创建客户散点图"""
    if customer_data.empty or '购买产品种类' not in customer_data.columns:
        return None

    # 添加客户标签
    if '客户简称' in customer_data.columns:
        hover_name = '客户简称'
    elif '经销商名称' in customer_data.columns:
        hover_name = '经销商名称'
    else:
        hover_name = '客户代码'

    fig = px.scatter(
        customer_data,
        x='购买产品种类',
        y='销售额',
        size='销售额',
        color='申请人' if '申请人' in customer_data.columns else None,
        hover_name=hover_name,
        title=title,
        size_max=50
    )

    fig.update_layout(
        height=450,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="购买产品种类",
        yaxis_title="销售额（元）"
    )

    # 添加客户价值分类线
    avg_value = customer_data['销售额'].mean()
    fig.add_shape(
        type="line",
        x0=0,
        x1=customer_data['购买产品种类'].max() * 1.1,
        y0=avg_value,
        y1=avg_value,
        line=dict(color="red", width=1, dash="dash")
    )

    fig.add_annotation(
        x=customer_data['购买产品种类'].max() * 0.9,
        y=avg_value * 1.1,
        text="平均客户价值",
        showarrow=False,
        font=dict(color="red")
    )

    return fig


def create_customer_segments_chart(customer_data, title="客户价值分类"):
    """创建客户价值分类图"""
    if customer_data.empty:
        return None

    # 计算价值分布
    avg_value = customer_data['销售额'].mean()
    avg_variety = customer_data['购买产品种类'].mean() if '购买产品种类' in customer_data.columns else 1

    # 客户价值分类
    if '购买产品种类' in customer_data.columns:
        customer_data['客户类型'] = customer_data.apply(
            lambda row: '高价值核心客户' if row['销售额'] > avg_value and row['购买产品种类'] > avg_variety
            else '高价值单一客户' if row['销售额'] > avg_value and row['购买产品种类'] <= avg_variety
            else '低价值多样客户' if row['销售额'] <= avg_value and row['购买产品种类'] > avg_variety
            else '低价值边缘客户',
            axis=1
        )
    else:
        customer_data['客户类型'] = customer_data.apply(
            lambda row: '高价值客户' if row['销售额'] > avg_value else '低价值客户',
            axis=1
        )

    # 统计各类型客户数量
    segments = customer_data.groupby('客户类型').size().reset_index(name='客户数量')

    # 为每个类型分配颜色
    color_map = {
        '高价值核心客户': '#4CAF50',
        '高价值单一客户': '#2196F3',
        '低价值多样客户': '#FF9800',
        '低价值边缘客户': '#F44336',
        '高价值客户': '#4CAF50',
        '低价值客户': '#F44336'
    }

    fig = px.pie(
        segments,
        names='客户类型',
        values='客户数量',
        title=title,
        color='客户类型',
        color_discrete_map=color_map
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


# ==================== 主页面 ====================
# 分析数据
customer_analysis = analyze_customer_data(filtered_data)

# 创建标签页
tabs = st.tabs(["📊 客户概览", "👑 TOP客户分析", "🌐 区域客户分析", "🔍 客户价值分析"])

with tabs[0]:  # 客户概览
    # KPI指标行
    st.subheader("🔑 关键客户指标")
    col1, col2, col3, col4 = st.columns(4)

    # 客户总数
    total_customers = customer_analysis.get('total_customers', 0)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">客户总数</p>
            <p class="card-value">{format_number(total_customers)}</p>
            <p class="card-text">活跃客户数量</p>
        </div>
        """, unsafe_allow_html=True)

    # TOP5客户集中度
    top5_concentration = customer_analysis.get('top5_concentration', 0)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">TOP5客户集中度</p>
            <p class="card-value" style="color: {'#4CAF50' if top5_concentration <= 50 else '#FF9800' if top5_concentration <= 70 else '#F44336'};">{format_percentage(top5_concentration)}</p>
            <p class="card-text">TOP5客户占比</p>
        </div>
        """, unsafe_allow_html=True)

    # 平均客户价值
    avg_customer_value = customer_analysis.get('avg_customer_value', 0)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均客户价值</p>
            <p class="card-value">{format_currency(avg_customer_value)}</p>
            <p class="card-text">客户均值</p>
        </div>
        """, unsafe_allow_html=True)

    # 客户依赖度风险
    dependency_risk = customer_analysis.get('dependency_risk_score', 0)
    with col4:
        risk_level = "低" if dependency_risk <= 50 else "中" if dependency_risk <= 70 else "高"
        risk_color = "#4CAF50" if dependency_risk <= 50 else "#FF9800" if dependency_risk <= 70 else "#F44336"

        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">客户依赖度风险</p>
            <p class="card-value" style="color: {risk_color};">{risk_level}</p>
            <p class="card-text">客户集中风险评估</p>
        </div>
        """, unsafe_allow_html=True)

    # 客户概览分析
    st.markdown('<div class="sub-header">📊 客户概览分析</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        # 客户集中度仪表盘
        fig = create_concentration_gauge(top5_concentration, "TOP5客户集中度")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        concentration_status = "健康" if top5_concentration <= 50 else "警示" if top5_concentration <= 70 else "风险"

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> TOP5客户集中度为{format_percentage(top5_concentration)}，处于<span style="color: {'#4CAF50' if top5_concentration <= 50 else '#FF9800' if top5_concentration <= 70 else '#F44336'};">{concentration_status}</span>状态。
            {'客户分布较为均衡，业务风险较低。' if top5_concentration <= 50 else '客户较为集中，存在一定依赖风险。' if top5_concentration <= 70 else '客户高度集中，存在严重依赖风险，需要积极开发新客户。'}
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        # TOP10客户集中度
        top10_concentration = customer_analysis.get('top10_concentration', 0)
        fig = create_concentration_gauge(top10_concentration, "TOP10客户集中度")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        concentration_status = "健康" if top10_concentration <= 60 else "警示" if top10_concentration <= 80 else "风险"

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> TOP10客户集中度为{format_percentage(top10_concentration)}，处于<span style="color: {'#4CAF50' if top10_concentration <= 60 else '#FF9800' if top10_concentration <= 80 else '#F44336'};">{concentration_status}</span>状态。
            {'客户基础广泛，业务发展稳健。' if top10_concentration <= 60 else '客户基础略显集中，需关注客户开发。' if top10_concentration <= 80 else '客户严重集中，客户基础薄弱，急需拓展新客户。'}
        </div>
        """, unsafe_allow_html=True)

    # 客户价值分类
    st.markdown('<div class="sub-header">📊 客户价值分类</div>', unsafe_allow_html=True)

    # 客户价值散点图和分类图
    customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

    cols = st.columns(2)
    with cols[0]:
        fig = create_customer_scatter(customer_sales, "客户价值分布")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        st.markdown("""
        <div class="chart-explanation">
            <b>图表解读：</b> 散点图显示了客户销售额与产品多样性的关系。图中右上方的客户是高价值核心客户，不仅销售额高，而且产品采购多样；右下方的客户是高价值单一客户，销售额高但集中在少数产品；左上方的客户是低价值多样客户，虽采购多样但总额不高；左下方的客户是低价值边缘客户，销售额低且产品单一。
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        fig = create_customer_segments_chart(customer_sales, "客户价值分类占比")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        st.markdown("""
        <div class="chart-explanation">
            <b>图表解读：</b> 此图展示了不同价值类型客户的分布占比。高价值核心客户具有战略意义，需重点维护；高价值单一客户有扩展潜力，可增加品类渗透；低价值多样客户适合深耕，提升单品渗透率；低价值边缘客户则需评估投入产出比，进行分级管理。
        </div>
        """, unsafe_allow_html=True)

    # 客户管理建议
    st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

    if top5_concentration > 70:
        st.markdown("""
        <h4>⚠️ 客户集中度过高警告</h4>
        <p>当前TOP5客户集中度过高，业务过度依赖少数大客户，存在较高经营风险。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>制定客户多元化战略，积极开发新客户</li>
            <li>建立客户风险评估机制，为大客户制定应急预案</li>
            <li>深化与现有客户的合作，但避免过度依赖</li>
            <li>加强销售团队建设，提高获客能力</li>
        </ul>
        """, unsafe_allow_html=True)
    elif top5_concentration > 50:
        st.markdown("""
        <h4>🔔 客户结构优化提示</h4>
        <p>客户集中度处于警戒线附近，需关注客户结构优化。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>积极开发中型客户，培育成长性客户</li>
            <li>深化大客户合作同时，扩大客户基础</li>
            <li>优化客户管理体系，建立分级管理机制</li>
            <li>定期评估客户结构健康度，调整资源配置</li>
        </ul>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <h4>✅ 客户结构健康</h4>
        <p>当前客户集中度处于健康水平，客户结构相对均衡。</p>
        <p><strong>建议行动：</strong></p>
        <ul>
            <li>维持现有客户开发策略，保持客户结构健康</li>
            <li>关注大客户需求变化，加强服务质量</li>
            <li>挖掘中小客户增长潜力，培育战略客户</li>
            <li>建立客户成长激励机制，提高客户黏性</li>
        </ul>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:  # TOP客户分析
    st.subheader("👑 TOP客户分析")

    # TOP客户销售额分析
    customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

    if not customer_sales.empty:
        # TOP10客户销售额柱状图
        fig = create_customer_concentration_chart(customer_sales, "TOP10客户销售额")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        top1_customer_name = customer_sales.iloc[0][
            '客户简称'] if '客户简称' in customer_sales.columns and not customer_sales.empty else "TOP1客户"
        top1_sales = customer_sales.iloc[0]['销售额'] if not customer_sales.empty else 0
        top1_percentage = (top1_sales / customer_sales['销售额'].sum() * 100) if not customer_sales.empty and \
                                                                                 customer_sales[
                                                                                     '销售额'].sum() > 0 else 0

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> {top1_customer_name}是最大客户，销售额{format_currency(top1_sales)}，占总销售额的{format_percentage(top1_percentage)}。
            TOP10客户总体占比{format_percentage(customer_analysis.get('top10_concentration', 0))}，{'客户分布较为均衡。' if customer_analysis.get('top10_concentration', 0) <= 60 else '客户较为集中。'}
        </div>
        """, unsafe_allow_html=True)

        # TOP客户详细分析
        st.markdown('<div class="sub-header">🔍 TOP5客户详细分析</div>', unsafe_allow_html=True)

        # 获取TOP5客户
        top5_customers = customer_sales.head(5)

        # 创建TOP5客户卡片
        for i, row in top5_customers.iterrows():
            customer_name = row['客户简称'] if '客户简称' in row else row['经销商名称'] if '经销商名称' in row else row[
                '客户代码']
            customer_sales = row['销售额']
            customer_percentage = (customer_sales / customer_analysis.get('customer_sales', pd.DataFrame())[
                '销售额'].sum() * 100) if not customer_analysis.get('customer_sales', pd.DataFrame()).empty and \
                                          customer_analysis.get('customer_sales', pd.DataFrame())[
                                              '销售额'].sum() > 0 else 0
            customer_products = row['购买产品种类'] if '购买产品种类' in row else "未知"
            customer_sales_person = row['申请人'] if '申请人' in row else "未知"

            st.markdown(f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); margin-bottom: 1rem;">
                <h3 style="color: {COLORS['primary']};">{i + 1}. {customer_name}</h3>
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px; margin-right: 1rem;">
                        <p><strong>销售额：</strong> {format_currency(customer_sales)}</p>
                        <p><strong>占比：</strong> {format_percentage(customer_percentage)}</p>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <p><strong>购买产品种类：</strong> {customer_products}</p>
                        <p><strong>主要销售员：</strong> {customer_sales_person}</p>
                    </div>
                </div>
                <hr>
                <h4>客户价值分析</h4>
                <p><strong>价值类型：</strong> {'高价值核心客户' if customer_sales > customer_analysis.get('avg_customer_value', 0) and customer_products > 5 else '高价值单一客户' if customer_sales > customer_analysis.get('avg_customer_value', 0) else '低价值多样客户' if customer_products > 5 else '低价值边缘客户'}</p>
                <p><strong>发展建议：</strong> {'维护核心关系，深化战略合作' if customer_sales > customer_analysis.get('avg_customer_value', 0) and customer_products > 5 else '扩大产品覆盖，增加品类渗透' if customer_sales > customer_analysis.get('avg_customer_value', 0) else '提高单品渗透率，增加客单价' if customer_products > 5 else '评估维护成本，考虑客户升级'}</p>
            </div>
            """, unsafe_allow_html=True)

        # TOP客户管理策略
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)
        st.markdown("""
        <h4>👑 TOP客户管理策略</h4>
        <p>TOP客户是业务的核心支柱，需要精细化管理和差异化策略。</p>
        <p><strong>策略建议：</strong></p>
        <ul>
            <li><strong>战略协同：</strong> 与TOP客户建立战略合作关系，深入了解其业务需求和发展方向</li>
            <li><strong>专属服务：</strong> 为TOP客户提供专属客户经理和服务团队，提升服务质量</li>
            <li><strong>产品定制：</strong> 根据TOP客户需求提供定制化产品和解决方案</li>
            <li><strong>深度合作：</strong> 探索营销协同、供应链优化等多维度合作机会</li>
            <li><strong>风险管控：</strong> 建立客户关系健康度评估机制，及时识别并应对风险</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无客户销售数据")

with tabs[2]:  # 区域客户分析
    st.subheader("🌐 区域客户分析")

    # 区域客户分布
    region_stats = customer_analysis.get('region_stats', pd.DataFrame())

    if not region_stats.empty:
        # 区域客户数量和平均客户价值
        cols = st.columns(2)
        with cols[0]:
            fig = create_region_customers_chart(region_stats, "区域客户分布")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            most_region = region_stats.loc[
                region_stats['客户数量'].idxmax(), '所属区域'] if not region_stats.empty else "未知"
            most_customers = region_stats.loc[
                region_stats['客户数量'].idxmax(), '客户数量'] if not region_stats.empty else 0

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> {most_region}区域客户数量最多，有{most_customers}个客户，市场覆盖最广。
                {'客户分布较为均衡，市场覆盖全面。' if region_stats['客户数量'].std() / region_stats['客户数量'].mean() < 0.3 else '客户分布不均，区域发展不平衡，需关注薄弱区域。'}
            </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            fig = create_avg_value_bar(region_stats, "区域平均客户价值")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            highest_value_region = region_stats.loc[
                region_stats['平均客户价值'].idxmax(), '所属区域'] if not region_stats.empty else "未知"
            highest_avg_value = region_stats.loc[
                region_stats['平均客户价值'].idxmax(), '平均客户价值'] if not region_stats.empty else 0

            lowest_value_region = region_stats.loc[
                region_stats['平均客户价值'].idxmin(), '所属区域'] if not region_stats.empty else "未知"
            value_gap = highest_avg_value / region_stats.loc[
                region_stats['平均客户价值'].idxmin(), '平均客户价值'] if not region_stats.empty and region_stats.loc[
                region_stats['平均客户价值'].idxmin(), '平均客户价值'] > 0 else 0

            st.markdown(f"""
            <div class="chart-explanation">
                <b>图表解读：</b> {highest_value_region}区域平均客户价值最高，为{format_currency(highest_avg_value)}。
                {highest_value_region}与{lowest_value_region}区域的平均客户价值差距{value_gap:.1f}倍，{'区域客户价值差异显著' if value_gap > 2 else '区域客户价值较为均衡'}。
            </div>
            """, unsafe_allow_html=True)

        # 区域客户价值矩阵
        st.markdown('<div class="sub-header">📊 区域客户价值矩阵</div>', unsafe_allow_html=True)

        # 创建区域客户价值矩阵
        region_matrix = region_stats.copy()
        region_matrix['客户密度'] = region_matrix['客户数量'] / region_matrix['客户数量'].sum() * 100

        # 计算全局平均值
        avg_density = region_matrix['客户密度'].mean()
        avg_value = region_matrix['平均客户价值'].mean()

        # 添加区域类型
        region_matrix['区域类型'] = region_matrix.apply(
            lambda row: '核心区域' if row['客户密度'] > avg_density and row['平均客户价值'] > avg_value
            else '价值区域' if row['客户密度'] <= avg_density and row['平均客户价值'] > avg_value
            else '数量区域' if row['客户密度'] > avg_density and row['平均客户价值'] <= avg_value
            else '发展区域',
            axis=1
        )

        # 创建区域客户价值散点图
        fig = px.scatter(
            region_matrix,
            x='客户密度',
            y='平均客户价值',
            size='销售额',
            color='区域类型',
            hover_name='所属区域',
            text='所属区域',
            title="区域客户价值矩阵",
            size_max=50,
            color_discrete_map={
                '核心区域': '#4CAF50',
                '价值区域': '#2196F3',
                '数量区域': '#FF9800',
                '发展区域': '#F44336'
            }
        )

        # 添加四象限分隔线
        fig.add_shape(
            type="line",
            x0=avg_density,
            x1=avg_density,
            y0=0,
            y1=region_matrix['平均客户价值'].max() * 1.1,
            line=dict(color="gray", width=1, dash="dash")
        )

        fig.add_shape(
            type="line",
            x0=0,
            x1=region_matrix['客户密度'].max() * 1.1,
            y0=avg_value,
            y1=avg_value,
            line=dict(color="gray", width=1, dash="dash")
        )

        # 添加象限标签
        annotations = [
            dict(
                x=avg_density * 1.5,
                y=avg_value * 1.5,
                text="核心区域",
                showarrow=False,
                font=dict(size=12, color='#4CAF50')
            ),
            dict(
                x=avg_density * 0.5,
                y=avg_value * 1.5,
                text="价值区域",
                showarrow=False,
                font=dict(size=12, color='#2196F3')
            ),
            dict(
                x=avg_density * 1.5,
                y=avg_value * 0.5,
                text="数量区域",
                showarrow=False,
                font=dict(size=12, color='#FF9800')
            ),
            dict(
                x=avg_density * 0.5,
                y=avg_value * 0.5,
                text="发展区域",
                showarrow=False,
                font=dict(size=12, color='#F44336')
            )
        ]

        fig.update_layout(
            annotations=annotations,
            height=500,
            margin=dict(l=50, r=50, t=60, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="客户密度 (%)",
            yaxis_title="平均客户价值 (元)"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        st.markdown("""
        <div class="chart-explanation">
            <b>图表解读：</b> 区域客户价值矩阵将区域按客户密度和平均客户价值分为四类：
            <ul>
                <li><b>核心区域</b> - 客户数量多且价值高，是业务核心区域，需维护优势</li>
                <li><b>价值区域</b> - 客户数量少但价值高，适合精耕细作，提升客户覆盖</li>
                <li><b>数量区域</b> - 客户数量多但价值低，需提升客户价值，加强产品渗透</li>
                <li><b>发展区域</b> - 客户数量少且价值低，需评估发展潜力，针对性培育</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 区域客户策略建议
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

        # 获取各类型区域
        core_regions = region_matrix[region_matrix['区域类型'] == '核心区域']['所属区域'].tolist()
        value_regions = region_matrix[region_matrix['区域类型'] == '价值区域']['所属区域'].tolist()
        quantity_regions = region_matrix[region_matrix['区域类型'] == '数量区域']['所属区域'].tolist()
        develop_regions = region_matrix[region_matrix['区域类型'] == '发展区域']['所属区域'].tolist()

        st.markdown(f"""
        <h4>🗺️ 区域客户发展策略</h4>
        <p>不同类型区域需要差异化的客户发展策略。</p>
        <p><strong>区域细分策略：</strong></p>
        <ul>
            <li><strong>核心区域</strong> ({', '.join(core_regions) if core_regions else '无'})：
                <ul>
                    <li>维护核心客户关系，提高客户忠诚度</li>
                    <li>扩大产品覆盖面，提升单客销售额</li>
                    <li>建立区域标杆客户，辐射带动其他客户</li>
                </ul>
            </li>
            <li><strong>价值区域</strong> ({', '.join(value_regions) if value_regions else '无'})：
                <ul>
                    <li>扩大客户覆盖，获取更多高价值客户</li>
                    <li>深化现有客户合作，提高渗透率</li>
                    <li>寻找区域扩张的关键突破点</li>
                </ul>
            </li>
            <li><strong>数量区域</strong> ({', '.join(quantity_regions) if quantity_regions else '无'})：
                <ul>
                    <li>提升客户价值，增加高价值产品渗透</li>
                    <li>客户分级管理，重点提升高潜客户</li>
                    <li>优化客户结构，减少低效客户</li>
                </ul>
            </li>
            <li><strong>发展区域</strong> ({', '.join(develop_regions) if develop_regions else '无'})：
                <ul>
                    <li>评估区域发展潜力，制定针对性拓展计划</li>
                    <li>聚焦关键客户和渠道，建立区域据点</li>
                    <li>适度资源投入，控制发展风险</li>
                </ul>
            </li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无区域客户分析数据")

with tabs[3]:  # 客户价值分析
    st.subheader("🔍 客户价值分析")

    # 客户价值分析
    customer_sales = customer_analysis.get('customer_sales', pd.DataFrame())

    if not customer_sales.empty and '购买产品种类' in customer_sales.columns:
        # 创建客户价值分布散点图
        fig = create_customer_scatter(customer_sales, "客户价值与产品多样性分布")
        st.plotly_chart(fig, use_container_width=True)

        # 图表解读
        avg_value = customer_sales['销售额'].mean()
        avg_variety = customer_sales['购买产品种类'].mean()

        st.markdown(f"""
        <div class="chart-explanation">
            <b>图表解读：</b> 此图展示了客户销售额与产品多样性的关系。平均客户价值为{format_currency(avg_value)}，平均购买产品种类为{avg_variety:.1f}种。
            客户主要分为四类：右上方的高价值核心客户，右下方的高价值单一客户，左上方的低价值多样客户，左下方的低价值边缘客户。不同类型的客户需要不同的经营策略。
        </div>
        """, unsafe_allow_html=True)

        # 客户价值分析详情
        st.markdown('<div class="sub-header">📊 客户价值分类详情</div>', unsafe_allow_html=True)

        # 计算客户类型
        if '客户类型' not in customer_sales.columns:
            customer_sales['客户类型'] = customer_sales.apply(
                lambda row: '高价值核心客户' if row['销售额'] > avg_value and row['购买产品种类'] > avg_variety
                else '高价值单一客户' if row['销售额'] > avg_value and row['购买产品种类'] <= avg_variety
                else '低价值多样客户' if row['销售额'] <= avg_value and row['购买产品种类'] > avg_variety
                else '低价值边缘客户',
                axis=1
            )

        # 统计各类客户指标
        segment_stats = customer_sales.groupby('客户类型').agg({
            '客户代码': 'count',
            '销售额': 'sum',
            '购买产品种类': 'mean'
        }).reset_index()

        segment_stats.columns = ['客户类型', '客户数量', '销售额', '平均购买产品种类']
        segment_stats['占比'] = segment_stats['客户数量'] / segment_stats['客户数量'].sum() * 100
        segment_stats['销售额占比'] = segment_stats['销售额'] / segment_stats['销售额'].sum() * 100

        # 客户类型卡片
        col1, col2 = st.columns(2)

        with col1:
            # 高价值核心客户
            core_stats = segment_stats[segment_stats['客户类型'] == '高价值核心客户']
            if not core_stats.empty:
                core_count = core_stats.iloc[0]['客户数量']
                core_sales = core_stats.iloc[0]['销售额']
                core_percentage = core_stats.iloc[0]['占比']
                core_sales_percentage = core_stats.iloc[0]['销售额占比']
                core_products = core_stats.iloc[0]['平均购买产品种类']

                st.markdown(f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; 
                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #4CAF50;">💎 高价值核心客户</h4>
                    <p><b>客户数量：</b> {format_number(core_count)} ({format_percentage(core_percentage)})</p>
                    <p><b>销售贡献：</b> {format_currency(core_sales)} ({format_percentage(core_sales_percentage)})</p>
                    <p><b>平均购买产品种类：</b> {core_products:.1f}</p>
                    <hr>
                    <h5>策略建议</h5>
                    <ul>
                        <li>建立战略合作关系，成为客户首选供应商</li>
                        <li>提供定制化产品和服务，满足特殊需求</li>
                        <li>分配专属客户经理，提供VIP服务</li>
                        <li>定期高层拜访，加强战略协同</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 低价值多样客户
            diverse_stats = segment_stats[segment_stats['客户类型'] == '低价值多样客户']
            if not diverse_stats.empty:
                diverse_count = diverse_stats.iloc[0]['客户数量']
                diverse_sales = diverse_stats.iloc[0]['销售额']
                diverse_percentage = diverse_stats.iloc[0]['占比']
                diverse_sales_percentage = diverse_stats.iloc[0]['销售额占比']
                diverse_products = diverse_stats.iloc[0]['平均购买产品种类']

                st.markdown(f"""
                <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; 
                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #FF9800;">🌱 低价值多样客户</h4>
                    <p><b>客户数量：</b> {format_number(diverse_count)} ({format_percentage(diverse_percentage)})</p>
                    <p><b>销售贡献：</b> {format_currency(diverse_sales)} ({format_percentage(diverse_sales_percentage)})</p>
                    <p><b>平均购买产品种类：</b> {diverse_products:.1f}</p>
                    <hr>
                    <h5>策略建议</h5>
                    <ul>
                        <li>提高单品渗透率，增加客户采购量</li>
                        <li>挖掘客户需求，提供整体解决方案</li>
                        <li>设计数量激励，提高复购频率</li>
                        <li>分析购买行为，找出提升价值点</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # 高价值单一客户
            single_stats = segment_stats[segment_stats['客户类型'] == '高价值单一客户']
            if not single_stats.empty:
                single_count = single_stats.iloc[0]['客户数量']
                single_sales = single_stats.iloc[0]['销售额']
                single_percentage = single_stats.iloc[0]['占比']
                single_sales_percentage = single_stats.iloc[0]['销售额占比']
                single_products = single_stats.iloc[0]['平均购买产品种类']

                st.markdown(f"""
                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; 
                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #2196F3;">💰 高价值单一客户</h4>
                    <p><b>客户数量：</b> {format_number(single_count)} ({format_percentage(single_percentage)})</p>
                    <p><b>销售贡献：</b> {format_currency(single_sales)} ({format_percentage(single_sales_percentage)})</p>
                    <p><b>平均购买产品种类：</b> {single_products:.1f}</p>
                    <hr>
                    <h5>策略建议</h5>
                    <ul>
                        <li>增加品类渗透，扩大产品覆盖</li>
                        <li>交叉销售相关产品，增加客户价值</li>
                        <li>开展产品体验活动，促进新品尝试</li>
                        <li>深入了解客户需求，匹配更多产品</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 低价值边缘客户
            marginal_stats = segment_stats[segment_stats['客户类型'] == '低价值边缘客户']
            if not marginal_stats.empty:
                marginal_count = marginal_stats.iloc[0]['客户数量']
                marginal_sales = marginal_stats.iloc[0]['销售额']
                marginal_percentage = marginal_stats.iloc[0]['占比']
                marginal_sales_percentage = marginal_stats.iloc[0]['销售额占比']
                marginal_products = marginal_stats.iloc[0]['平均购买产品种类']

                st.markdown(f"""
                <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; 
                            padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #F44336;">⚠️ 低价值边缘客户</h4>
                    <p><b>客户数量：</b> {format_number(marginal_count)} ({format_percentage(marginal_percentage)})</p>
                    <p><b>销售贡献：</b> {format_currency(marginal_sales)} ({format_percentage(marginal_sales_percentage)})</p>
                    <p><b>平均购买产品种类：</b> {marginal_products:.1f}</p>
                    <hr>
                    <h5>策略建议</h5>
                    <ul>
                        <li>评估客户潜力，进行分类管理</li>
                        <li>针对高潜力客户制定发展计划</li>
                        <li>优化服务成本，提高客户效率</li>
                        <li>考虑逐步淘汰长期低价值客户</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # 客户价值总结
        st.markdown('<div class="alert-box alert-success">', unsafe_allow_html=True)

        # 计算高价值客户占比
        high_value_customers = customer_sales[customer_sales['销售额'] > avg_value]
        high_value_count = len(high_value_customers)
        high_value_percentage = (high_value_count / len(customer_sales) * 100) if len(customer_sales) > 0 else 0
        high_value_sales = high_value_customers['销售额'].sum()
        high_value_sales_percentage = (high_value_sales / customer_sales['销售额'].sum() * 100) if customer_sales[
                                                                                                       '销售额'].sum() > 0 else 0

        st.markdown(f"""
        <h4>📊 客户价值构成分析</h4>
        <p>高价值客户（{format_number(high_value_count)}个，占比{format_percentage(high_value_percentage)}）贡献了{format_percentage(high_value_sales_percentage)}的销售额。</p>
        <p><strong>客户策略建议：</strong></p>
        <ul>
            <li><strong>差异化服务策略：</strong> 根据客户价值分级，提供差异化服务</li>
            <li><strong>高价值客户维护：</strong> 重点资源配置给高价值客户，提高忠诚度</li>
            <li><strong>产品渗透提升：</strong> 针对单一产品客户，增加品类渗透</li>
            <li><strong>客户价值提升：</strong> 对低价值客户进行筛选，重点培育高潜力客户</li>
            <li><strong>建立价值评估体系：</strong> 定期评估客户价值和潜力，动态调整客户策略</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 客户价值矩阵表格
        with st.expander("查看客户价值分类详细数据"):
            # 按客户类型筛选客户
            core_customers = customer_sales[customer_sales['客户类型'] == '高价值核心客户'].sort_values('销售额',
                                                                                                        ascending=False)
            single_customers = customer_sales[customer_sales['客户类型'] == '高价值单一客户'].sort_values('销售额',
                                                                                                          ascending=False)
            diverse_customers = customer_sales[customer_sales['客户类型'] == '低价值多样客户'].sort_values('销售额',
                                                                                                           ascending=False)
            marginal_customers = customer_sales[customer_sales['客户类型'] == '低价值边缘客户'].sort_values('销售额',
                                                                                                            ascending=False)

            # 创建标签页
            customer_tabs = st.tabs(["高价值核心客户", "高价值单一客户", "低价值多样客户", "低价值边缘客户"])

            with customer_tabs[0]:
                if not core_customers.empty:
                    # 显示列
                    display_cols = ['客户代码', '客户简称', '销售额', '购买产品种类',
                                    '申请人'] if '申请人' in core_customers.columns else ['客户代码', '客户简称',
                                                                                          '销售额', '购买产品种类']
                    st.dataframe(core_customers[display_cols], use_container_width=True)
                else:
                    st.info("暂无高价值核心客户")

            with customer_tabs[1]:
                if not single_customers.empty:
                    # 显示列
                    display_cols = ['客户代码', '客户简称', '销售额', '购买产品种类',
                                    '申请人'] if '申请人' in single_customers.columns else ['客户代码', '客户简称',
                                                                                            '销售额', '购买产品种类']
                    st.dataframe(single_customers[display_cols], use_container_width=True)
                else:
                    st.info("暂无高价值单一客户")

            with customer_tabs[2]:
                if not diverse_customers.empty:
                    # 显示列
                    display_cols = ['客户代码', '客户简称', '销售额', '购买产品种类',
                                    '申请人'] if '申请人' in diverse_customers.columns else ['客户代码', '客户简称',
                                                                                             '销售额', '购买产品种类']
                    st.dataframe(diverse_customers[display_cols], use_container_width=True)
                else:
                    st.info("暂无低价值多样客户")

            with customer_tabs[3]:
                if not marginal_customers.empty:
                    # 显示列
                    display_cols = ['客户代码', '客户简称', '销售额', '购买产品种类',
                                    '申请人'] if '申请人' in marginal_customers.columns else ['客户代码', '客户简称',
                                                                                              '销售额', '购买产品种类']
                    st.dataframe(marginal_customers[display_cols], use_container_width=True)
                else:
                    st.info("暂无低价值边缘客户")
    else:
        st.info("暂无客户价值分析数据或产品多样性数据")

# 客户洞察总结
st.subheader("💡 客户洞察总结")

# 生成洞察内容
total_customers = customer_analysis.get('total_customers', 0)
top5_concentration = customer_analysis.get('top5_concentration', 0)
avg_customer_value = customer_analysis.get('avg_customer_value', 0)

# 综合评估
if top5_concentration > 70:
    customer_structure = "存在较高客户集中风险"
    structure_color = COLORS['danger']
    structure_advice = "急需开发新客户，降低对大客户的依赖"
elif top5_concentration > 50:
    customer_structure = "客户集中度中等"
    structure_color = COLORS['warning']
    structure_advice = "需要关注客户结构优化，加强中小客户开发"
else:
    customer_structure = "客户结构健康"
    structure_color = COLORS['success']
    structure_advice = "保持现有客户开发策略，继续维护客户结构健康"

st.markdown(f"""
<div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
            padding: 1rem; border-radius: 0.5rem;">
    <h4>📋 客户分析总结</h4>
    <p><strong>客户基础：</strong>当前共有{format_number(total_customers)}个活跃客户，平均客户价值{format_currency(avg_customer_value)}。</p>
    <p><strong>客户结构：</strong><span style="color: {structure_color};">{customer_structure}</span>，TOP5客户集中度{format_percentage(top5_concentration)}。</p>
    <p><strong>区域分布：</strong>{'区域客户分布不均衡，需关注薄弱区域发展' if customer_analysis.get('region_stats', pd.DataFrame()).empty or customer_analysis.get('region_stats', pd.DataFrame())['客户数量'].std() / customer_analysis.get('region_stats', pd.DataFrame())['客户数量'].mean() > 0.3 else '区域客户分布相对均衡，市场覆盖全面'}。</p>
    <p><strong>客户价值：</strong>{'客户价值分布差异大，需分级管理' if customer_analysis.get('customer_sales', pd.DataFrame()).empty or customer_analysis.get('customer_sales', pd.DataFrame())['销售额'].std() / customer_analysis.get('customer_sales', pd.DataFrame())['销售额'].mean() > 1 else '客户价值分布相对均衡，整体质量良好'}。</p>
    <p><strong>发展建议：</strong>{structure_advice}；完善客户分级管理体系；针对不同价值客户制定差异化策略；加强客户关系管理，提高客户忠诚度。</p>
</div>
""", unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据</p>
</div>
""", unsafe_allow_html=True)