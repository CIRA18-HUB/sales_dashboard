# customer_page.py - 客户分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import re
from calendar import monthrange
import sys
import os

# 导入配置模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 忽略警告
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="客户分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 与预测与计划.py完全一致
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #444444;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f3867;
    }
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .card-text {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
    }
    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
    }
    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f3867;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 0.9rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border-left: 0.5rem solid #4CAF50;
    }
    .low-accuracy {
        border: 2px solid #F44336;
        box-shadow: 0 0 8px #F44336;
    }
    .logo-container {
        position: absolute;
        top: 0.5rem;
        right: 1rem;
        z-index: 1000;
    }
    .logo-img {
        height: 40px;
    }
    .pagination-btn {
        background-color: #1f3867;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
        margin: 5px;
        cursor: pointer;
    }
    .pagination-btn:hover {
        background-color: #2c4f8f;
    }
    .pagination-info {
        display: inline-block;
        padding: 5px;
        margin: 5px;
    }
    .hover-info {
        background-color: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .slider-container {
        padding: 10px 0;
    }
    .highlight-product {
        font-weight: bold;
        background-color: #ffeb3b;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .recommendation-tag {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 5px;
    }
    .recommendation-increase {
        background-color: #4CAF50;
        color: white;
    }
    .recommendation-maintain {
        background-color: #FFC107;
        color: black;
    }
    .recommendation-decrease {
        background-color: #F44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">客户分析仪表盘 | 登录</div>',
        unsafe_allow_html=True)

    # 创建居中的登录框
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
            <h2 style="text-align: center; color: #1f3867; margin-bottom: 20px;">请输入密码</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("密码", type="password", key="password_input")

        # 登录按钮
        login_button = st.button("登录")

        # 验证密码
        if login_button:
            if password == 'SAL!2025':  # 使用与app.py相同的密码
                st.session_state['authenticated'] = True
                st.success("登录成功！")
                try:
                    st.rerun()  # 使用新版本方法
                except AttributeError:
                    try:
                        st.experimental_rerun()  # 尝试使用旧版本方法
                    except:
                        st.error("请刷新页面以查看更改")
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()


# 添加Logo到右上角
def add_logo():
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://www.example.com/logo.png" class="logo-img">
        </div>
        """,
        unsafe_allow_html=True
    )


# 格式化函数
def format_currency(value):
    """格式化货币显示"""
    return f"¥{int(value):,}"


def format_percentage(value):
    """格式化百分比显示"""
    return f"{value:.1f}%"


def format_number(value):
    """格式化数量显示为逗号分隔的完整数字"""
    return f"{int(value):,}"


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 数据加载函数
@st.cache_data
def load_data():
    """加载客户分析所需的所有数据"""
    try:
        # 加载销售原始数据
        sales_data_path = "C:\\Users\\何晴雅\\Desktop\\仪表盘原始数据.xlsx"
        if os.path.exists(sales_data_path):
            sales_data = pd.read_excel(sales_data_path)
            # 确保日期列是日期类型
            if '发运月份' in sales_data.columns:
                sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

            # 提取订单数据
            orders = sales_data[sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])]

            # 添加销售额字段（如果不存在）
            if '销售额' not in orders.columns:
                if '单价（箱）' in orders.columns and '求和项:数量（箱）' in orders.columns:
                    orders['销售额'] = orders['单价（箱）'] * orders['求和项:数量（箱）']
                elif '求和项:金额（元）' in orders.columns:
                    orders['销售额'] = orders['求和项:金额（元）']
        else:
            st.error(f"找不到销售数据文件: {sales_data_path}")
            orders = pd.DataFrame()

        # 加载客户与销售员关系表
        customer_relation_path = "C:\\Users\\何晴雅\\Desktop\\仪表盘人与客户关系表.xlsx"
        if os.path.exists(customer_relation_path):
            customer_relation = pd.read_excel(customer_relation_path)
        else:
            st.error(f"找不到客户关系表文件: {customer_relation_path}")
            customer_relation = pd.DataFrame()

        # 加载客户指标数据
        customer_target_path = "C:\\Users\\何晴雅\\Desktop\\仪表盘客户月度指标维护.xlsx"
        if os.path.exists(customer_target_path):
            customer_target = pd.read_excel(customer_target_path)
            # 确保日期列是日期类型
            if '月份' in customer_target.columns:
                customer_target['月份'] = pd.to_datetime(customer_target['月份'])
        else:
            st.error(f"找不到客户指标文件: {customer_target_path}")
            customer_target = pd.DataFrame()

        # 加载促销活动数据
        promotion_path = "C:\\Users\\何晴雅\\Desktop\\仪表盘促销活动.xlsx"
        if os.path.exists(promotion_path):
            promotion = pd.read_excel(promotion_path)
            # 确保日期列是日期类型
            date_cols = ['促销开始供货时间', '促销结束供货时间']
            for col in date_cols:
                if col in promotion.columns:
                    promotion[col] = pd.to_datetime(promotion[col])
        else:
            st.warning(f"找不到促销活动文件: {promotion_path}")
            promotion = pd.DataFrame()

        # 读取产品代码列表
        product_codes_path = "C:\\Users\\何晴雅\\Desktop\\仪表盘产品代码.txt"
        if os.path.exists(product_codes_path):
            with open(product_codes_path, 'r') as f:
                product_codes = [line.strip() for line in f.readlines() if line.strip()]
        else:
            st.warning(f"找不到产品代码文件: {product_codes_path}")
            product_codes = []

        # 返回所有数据
        return {
            'orders': orders,
            'customer_relation': customer_relation,
            'customer_target': customer_target,
            'promotion': promotion,
            'product_codes': product_codes
        }
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        return {}


# 客户专用筛选器
def create_customer_filters(data):
    """创建客户分析专用的筛选器"""
    # 初始化筛选结果
    filtered_data = data.copy()

    # 确保数据加载成功
    if not data or 'orders' not in data or data['orders'].empty:
        st.sidebar.warning("无法加载客户数据，请检查数据源")
        return filtered_data

    orders = data['orders']
    customer_relation = data.get('customer_relation', pd.DataFrame())

    with st.sidebar:
        st.markdown("## 🔍 客户筛选")
        st.markdown("---")

        # 1. 区域筛选
        if '所属区域' in orders.columns:
            all_regions = sorted(['全部'] + list(orders['所属区域'].unique()))
            selected_region = st.sidebar.selectbox(
                "选择区域", all_regions, index=0, key="customer_region_filter"
            )
            if selected_region != '全部':
                orders = orders[orders['所属区域'] == selected_region]

        # 2. 客户状态筛选（基于客户关系表）
        if not customer_relation.empty and '状态' in customer_relation.columns:
            status_options = ['全部', '正常', '闭户']
            selected_status = st.sidebar.selectbox(
                "客户状态", status_options, index=0, key="customer_status_filter"
            )
            if selected_status != '全部':
                # 根据状态过滤客户关系表
                filtered_customers = customer_relation[customer_relation['状态'] == selected_status]

                # 找出客户列
                customer_col = None
                for col in ['客户', '客户简称', '经销商名称', '客户代码']:
                    if col in customer_relation.columns:
                        customer_col = col
                        break

                if customer_col:
                    # 获取符合状态的客户列表
                    valid_customers = filtered_customers[customer_col].unique()

                    # 查找订单表中对应客户列
                    order_customer_col = None
                    for col in ['客户代码', '经销商名称', '客户简称']:
                        if col in orders.columns:
                            order_customer_col = col
                            break

                    if order_customer_col:
                        # 根据状态过滤订单
                        orders = orders[orders[order_customer_col].isin(valid_customers)]

        # 3. 销售员筛选
        if '申请人' in orders.columns:
            all_sales = sorted(['全部'] + list(orders['申请人'].unique()))
            selected_sales = st.sidebar.selectbox(
                "销售员", all_sales, index=0, key="customer_salesperson_filter"
            )
            if selected_sales != '全部':
                orders = orders[orders['申请人'] == selected_sales]

        # 4. 客户类型或层级筛选 (基于销售额分层)
        if '销售额' in orders.columns:
            # 按客户汇总销售额
            if '客户代码' in orders.columns:
                customer_sales = orders.groupby('客户代码')['销售额'].sum().reset_index()
                customer_sales['层级'] = pd.qcut(
                    customer_sales['销售额'],
                    q=[0, 0.5, 0.8, 1.0],
                    labels=['小客户', '中等客户', '大客户']
                )

                # 计算每个层级的客户数量
                tier_counts = customer_sales['层级'].value_counts()

                tier_options = ['全部', '大客户', '中等客户', '小客户']
                selected_tier = st.sidebar.selectbox(
                    "客户层级", tier_options, index=0,
                    help=f"大客户: 销售额前20%的客户 ({tier_counts.get('大客户', 0)}家)\n"
                         f"中等客户: 销售额前21-50%的客户 ({tier_counts.get('中等客户', 0)}家)\n"
                         f"小客户: 销售额占比低于50%的客户 ({tier_counts.get('小客户', 0)}家)",
                    key="customer_tier_filter"
                )

                if selected_tier != '全部':
                    tier_customers = customer_sales[customer_sales['层级'] == selected_tier]['客户代码'].tolist()
                    orders = orders[orders['客户代码'].isin(tier_customers)]

        # 5. 日期范围筛选
        if '发运月份' in orders.columns:
            try:
                min_date = orders['发运月份'].min().date()
                max_date = orders['发运月份'].max().date()

                st.sidebar.markdown("### 日期范围")
                # 默认显示最近6个月
                default_start = max_date - timedelta(days=180)
                default_start = max(default_start, min_date)

                start_date = st.sidebar.date_input(
                    "开始日期", value=default_start, min_value=min_date, max_value=max_date,
                    key="customer_start_date"
                )
                end_date = st.sidebar.date_input(
                    "结束日期", value=max_date, min_value=min_date, max_value=max_date,
                    key="customer_end_date"
                )

                if end_date < start_date:
                    st.sidebar.warning("结束日期不能早于开始日期，已自动调整")
                    end_date = start_date

                # 转换为datetime格式以便比较
                start_datetime = pd.Timestamp(start_date)
                end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

                # 应用日期筛选
                orders = orders[(orders['发运月份'] >= start_datetime) &
                                (orders['发运月份'] <= end_datetime)]
            except Exception as e:
                st.sidebar.warning(f"日期筛选器初始化失败: {e}")

        # 筛选器重置按钮
        if st.sidebar.button("重置筛选条件", key="reset_customer_filters"):
            st.rerun()

    # 更新筛选后的数据
    filtered_data['orders'] = orders
    return filtered_data


# 计算客户关键指标
def calculate_customer_kpis(data):
    """计算客户分析的关键指标"""
    kpis = {}

    try:
        orders = data.get('orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty:
            return kpis

        # 找出客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return kpis

        # 1. 总客户数量
        kpis['total_customers'] = orders[customer_col].nunique()

        # 2. 客户平均销售额
        if '销售额' in orders.columns:
            total_sales = orders['销售额'].sum()
            kpis['total_sales'] = total_sales
            kpis['avg_customer_sales'] = total_sales / kpis['total_customers'] if kpis['total_customers'] > 0 else 0

        # 3. 客户订单频次
        orders_count = orders.groupby(customer_col).size().reset_index(name='订单数')
        kpis['avg_order_frequency'] = orders_count['订单数'].mean()

        # 4. 目标达成率
        if not customer_target.empty and '月度指标' in customer_target.columns:
            common_cols = set(customer_target.columns) & set(orders.columns)
            if customer_col in common_cols and '月份' in customer_target.columns and '发运月份' in orders.columns:
                # 准备订单月份
                orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()

                # 合并订单和目标
                # 为每个客户和月份创建销售汇总
                sales_monthly = orders.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

                # 合并目标数据
                merged = pd.merge(sales_monthly, customer_target, on=[customer_col, '月份'], how='inner')

                if not merged.empty:
                    # 计算达成率
                    merged['达成率'] = merged['销售额'] / merged['月度指标'] * 100
                    kpis['target_achievement'] = merged['达成率'].mean()
                    kpis['target_achievement_count'] = sum(merged['达成率'] >= 100)
                    kpis['target_total_count'] = len(merged)
                    kpis['target_achievement_rate'] = (
                        kpis['target_achievement_count'] / kpis['target_total_count'] * 100
                        if kpis['target_total_count'] > 0 else 0)

        return kpis

    except Exception as e:
        st.error(f"计算客户KPI时出错: {str(e)}")
        return {}


# 创建客户销售额排行图表
def create_top_customers_chart(data, top_n=10):
    """创建客户销售额排行图表"""
    try:
        orders = data.get('orders', pd.DataFrame())

        if orders.empty or len(orders) < 5:
            st.warning("数据不足，无法创建客户销售额排行图表")
            return None

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return None

        # 按客户汇总销售额
        if '销售额' in orders.columns:
            customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
            customer_sales = customer_sales.sort_values('销售额', ascending=False).head(top_n)

            # 如果有客户简称列，使用简称；否则使用代码
            display_col = customer_col
            if '客户简称' in orders.columns and customer_col != '客户简称':
                # 尝试获取客户简称
                customer_name_map = {}
                for _, row in orders.drop_duplicates([customer_col, '客户简称']).iterrows():
                    customer_name_map[row[customer_col]] = row['客户简称']

                if customer_name_map:
                    customer_sales['客户简称'] = customer_sales[customer_col].map(customer_name_map)
                    display_col = '客户简称'

            # 创建柱状图
            fig = go.Figure()

            # 添加销售额柱状图
            fig.add_trace(go.Bar(
                x=customer_sales[display_col],
                y=customer_sales['销售额'],
                marker_color='royalblue',
                name='销售额'
            ))

            # 添加累计占比线
            total_sales = customer_sales['销售额'].sum()
            customer_sales['累计销售额'] = customer_sales['销售额'].cumsum()
            customer_sales['累计占比'] = customer_sales['累计销售额'] / total_sales * 100

            fig.add_trace(go.Scatter(
                x=customer_sales[display_col],
                y=customer_sales['累计占比'],
                mode='lines+markers',
                name='累计占比',
                yaxis='y2',
                line=dict(color='firebrick', width=3),
                marker=dict(size=8)
            ))

            # 更新布局
            fig.update_layout(
                title="客户销售额排行Top" + str(top_n),
                xaxis=dict(
                    title="客户",
                    tickangle=45,
                    tickmode='linear'
                ),
                yaxis=dict(
                    title="销售额 (元)",
                    tickformat=",",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
                ),
                yaxis2=dict(
                    title="累计占比 (%)",
                    overlaying='y',
                    side='right',
                    range=[0, 100],
                    showgrid=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=60, r=60, t=50, b=100),
                plot_bgcolor='white',
                barmode='group'
            )

            # 添加悬停信息
            hover_data = []
            for i, row in customer_sales.iterrows():
                order_count = orders[orders[customer_col] == row[customer_col]].shape[0]
                avg_order_value = row['销售额'] / order_count if order_count > 0 else 0

                # 收集该客户的产品信息
                customer_orders = orders[orders[customer_col] == row[customer_col]]
                top_products = []
                if '产品代码' in customer_orders.columns and '产品简称' in customer_orders.columns:
                    product_sales = customer_orders.groupby(['产品代码', '产品简称'])['销售额'].sum().reset_index()
                    product_sales = product_sales.sort_values('销售额', ascending=False).head(3)
                    for _, prod in product_sales.iterrows():
                        top_products.append(f"{prod['产品简称']}: {format_currency(prod['销售额'])}")

                info = (
                    f"销售额: {format_currency(row['销售额'])}<br>"
                    f"订单数: {order_count}<br>"
                    f"平均订单金额: {format_currency(avg_order_value)}<br>"
                    f"累计占比: {row['累计占比']:.1f}%<br>"
                )

                if top_products:
                    info += "<br><b>主要产品:</b><br>" + "<br>".join(top_products)

                hover_data.append(info)

            # 添加悬停模板
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>%{customdata}<extra></extra>',
                customdata=hover_data,
                selector=dict(type='bar')
            )

            return fig

        else:
            st.warning("找不到销售额列，无法创建客户销售额排行图表")
            return None

    except Exception as e:
        st.error(f"创建客户销售额排行图表时出错: {str(e)}")
        return None


# 创建客户目标达成率图表
def create_target_achievement_chart(data):
    """创建客户目标达成率图表"""
    try:
        orders = data.get('orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty or customer_target.empty:
            st.warning("数据不足，无法创建客户目标达成率图表")
            return None

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称', '客户']:
            if col in orders.columns and col in customer_target.columns:
                customer_col = col
                break

        if not customer_col:
            st.warning("找不到客户相关列")
            return None

        # 准备月份数据
        if '发运月份' in orders.columns and '月份' in customer_target.columns:
            # 准备订单月份
            orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()

            # 确保月份格式一致
            customer_target['月份'] = pd.to_datetime(customer_target['月份'])

            # 汇总订单销售额
            if '销售额' in orders.columns:
                sales_monthly = orders.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

                # 合并目标数据
                merged = pd.merge(sales_monthly, customer_target, on=[customer_col, '月份'], how='inner')

                if not merged.empty and '月度指标' in merged.columns:
                    # 计算达成率
                    merged['达成率'] = (merged['销售额'] / merged['月度指标'] * 100).fillna(0)

                    # 标记达成状态
                    merged['达成状态'] = merged['达成率'].apply(
                        lambda x: '已达成' if x >= 100 else '未达成'
                    )

                    # 按月份和客户排序
                    merged = merged.sort_values(['月份', customer_col])

                    # 创建热力图
                    # 准备透视表数据
                    pivot_data = merged.pivot_table(
                        values='达成率',
                        index='月份',
                        columns=customer_col,
                        aggfunc='mean'
                    ).fillna(0)

                    # 限制客户数量，避免图表过于拥挤
                    max_customers = 15
                    if pivot_data.shape[1] > max_customers:
                        # 按平均达成率排序，选取最高和最低的客户
                        customer_avg = pivot_data.mean().sort_values(ascending=False)
                        top_customers = customer_avg.head(max_customers // 2).index
                        bottom_customers = customer_avg.tail(max_customers // 2).index
                        selected_customers = list(top_customers) + list(bottom_customers)
                        pivot_data = pivot_data[selected_customers]

                    # 创建热力图
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_data.values,
                        x=pivot_data.columns,
                        y=[d.strftime('%Y-%m') for d in pivot_data.index],
                        colorscale=[
                            [0, 'rgb(255,0,0)'],  # 红色 (0%)
                            [0.5, 'rgb(255,255,0)'],  # 黄色 (50%)
                            [0.8, 'rgb(144,238,144)'],  # 浅绿色 (80%)
                            [1, 'rgb(0,128,0)']  # 深绿色 (100%+)
                        ],
                        colorbar=dict(
                            title="达成率 (%)",
                            tickvals=[0, 50, 80, 100, 150, 200],
                            ticktext=["0%", "50%", "80%", "100%", "150%", "200%+"]
                        ),
                        hovertemplate='客户: %{x}<br>月份: %{y}<br>达成率: %{z:.1f}%<extra></extra>',
                        zauto=False,
                        zmin=0,
                        zmax=200,  # 限制最大值，避免极端值影响色彩显示
                    ))

                    # 更新布局
                    fig.update_layout(
                        title='客户月度指标达成率热力图',
                        xaxis=dict(
                            title="客户",
                            tickangle=45
                        ),
                        yaxis=dict(
                            title="月份",
                            autorange="reversed"  # 最新月份在上方
                        ),
                        margin=dict(l=60, r=60, t=50, b=100),
                        height=500 + (pivot_data.shape[0] * 30),  # 动态调整高度
                    )

                    return fig

        st.warning("数据不足，无法创建客户目标达成率图表")
        return None

    except Exception as e:
        st.error(f"创建客户目标达成率图表时出错: {str(e)}")
        return None


# 创建客户趋势分析图
def create_customer_trend_chart(data):
    """创建客户趋势分析图"""
    try:
        orders = data.get('orders', pd.DataFrame())

        if orders.empty:
            st.warning("数据不足，无法创建客户趋势分析图")
            return None

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '发运月份' not in orders.columns or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 按月份汇总客户数和销售额
        orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()
        monthly_stats = orders.groupby('月份').agg(
            客户数量=pd.NamedAgg(column=customer_col, aggfunc='nunique'),
            销售额=pd.NamedAgg(column='销售额', aggfunc='sum')
        ).reset_index()

        # 计算环比增长率
        monthly_stats['客户环比'] = monthly_stats['客户数量'].pct_change() * 100
        monthly_stats['销售额环比'] = monthly_stats['销售额'].pct_change() * 100

        # 创建双Y轴图表
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加客户数量线
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['客户数量'],
                mode='lines+markers',
                name='客户数量',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8)
            ),
            secondary_y=False
        )

        # 添加销售额柱状图
        fig.add_trace(
            go.Bar(
                x=monthly_stats['月份'],
                y=monthly_stats['销售额'],
                name='销售额',
                marker_color='lightcoral'
            ),
            secondary_y=True
        )

        # 添加环比增长注释
        for i, row in monthly_stats.iterrows():
            if i > 0:  # 跳过第一个月，因为没有环比数据
                # 客户环比标注
                color = 'green' if row['客户环比'] >= 0 else 'red'
                symbol = '▲' if row['客户环比'] >= 0 else '▼'
                fig.add_annotation(
                    x=row['月份'],
                    y=row['客户数量'],
                    text=f"{symbol} {abs(row['客户环比']):.1f}%",
                    showarrow=False,
                    yshift=15,
                    font=dict(color=color)
                )

                # 销售额环比标注
                color = 'green' if row['销售额环比'] >= 0 else 'red'
                symbol = '▲' if row['销售额环比'] >= 0 else '▼'
                fig.add_annotation(
                    x=row['月份'],
                    y=row['销售额'],
                    text=f"{symbol} {abs(row['销售额环比']):.1f}%",
                    showarrow=False,
                    yshift=15,
                    font=dict(color=color)
                )

        # 更新轴标题
        fig.update_xaxes(title_text="月份")
        fig.update_yaxes(title_text="客户数量", secondary_y=False)
        fig.update_yaxes(
            title_text="销售额 (元)",
            tickformat=",",
            secondary_y=True
        )

        # 更新布局
        fig.update_layout(
            title="客户数量与销售额月度趋势",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=60, t=50, b=60),
            plot_bgcolor='white',
            hovermode="x unified"
        )

        # 添加悬停模板
        fig.update_traces(
            hovertemplate='月份: %{x}<br>客户数量: %{y}<extra></extra>',
            selector=dict(name='客户数量')
        )

        fig.update_traces(
            hovertemplate='月份: %{x}<br>销售额: ¥%{y:,.2f}<extra></extra>',
            selector=dict(name='销售额')
        )

        return fig

    except Exception as e:
        st.error(f"创建客户趋势分析图表时出错: {str(e)}")
        return None


# 创建客户区域分布图
def create_customer_region_chart(data):
    """创建客户区域分布图"""
    try:
        orders = data.get('orders', pd.DataFrame())

        if orders.empty or '所属区域' not in orders.columns:
            st.warning("数据不足，无法创建客户区域分布图")
            return None

        # 确定客户列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 按区域统计客户数量和销售额
        region_stats = orders.groupby('所属区域').agg(
            客户数量=pd.NamedAgg(column=customer_col, aggfunc='nunique'),
            销售额=pd.NamedAgg(column='销售额', aggfunc='sum'),
            订单数=pd.NamedAgg(column=customer_col, aggfunc='count')
        ).reset_index()

        # 计算客户均销售额
        region_stats['客户均销售额'] = region_stats['销售额'] / region_stats['客户数量']

        # 按客户数量降序排序
        region_stats = region_stats.sort_values('客户数量', ascending=False)

        # 创建图表
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "bar"}]],
            subplot_titles=("客户区域分布", "区域客户指标对比"),
            column_widths=[0.4, 0.6]
        )

        # 添加饼图 - 客户数量分布
        fig.add_trace(
            go.Pie(
                labels=region_stats['所属区域'],
                values=region_stats['客户数量'],
                name="客户分布",
                marker_colors=px.colors.qualitative.Set3,
                textinfo='percent+label',
                hovertemplate='%{label}<br>客户数量: %{value}<br>占比: %{percent}<extra></extra>'
            ),
            row=1, col=1
        )

        # 添加柱状图 - 区域指标对比
        fig.add_trace(
            go.Bar(
                x=region_stats['所属区域'],
                y=region_stats['客户均销售额'],
                name="客户均销售额",
                marker_color='forestgreen',
                hovertemplate='区域: %{x}<br>客户均销售额: ¥%{y:,.2f}<extra></extra>'
            ),
            row=1, col=2
        )

        # 添加客户数量线
        fig.add_trace(
            go.Scatter(
                x=region_stats['所属区域'],
                y=region_stats['客户数量'],
                mode='lines+markers',
                name='客户数量',
                marker=dict(color='royalblue', size=8),
                line=dict(width=3),
                hovertemplate='区域: %{x}<br>客户数量: %{y}<extra></extra>'
            ),
            row=1, col=2
        )

        # 更新布局
        fig.update_layout(
            title="客户区域分布与区域指标",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=80, b=100),
            plot_bgcolor='white',
            height=600
        )

        # 更新Y轴标题
        fig.update_yaxes(title_text="客户均销售额 (元)", row=1, col=2)

        # 悬停数据准备
        hover_data = []
        for _, row in region_stats.iterrows():
            info = (
                f"区域: {row['所属区域']}<br>"
                f"客户数量: {row['客户数量']}<br>"
                f"销售额: {format_currency(row['销售额'])}<br>"
                f"客户均销售额: {format_currency(row['客户均销售额'])}<br>"
                f"订单数: {row['订单数']}<br>"
                f"客户均订单数: {row['订单数'] / row['客户数量']:.1f}"
            )
            hover_data.append(info)

        # 设置柱状图悬停模板
        fig.update_traces(
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_data,
            selector=dict(type='bar')
        )

        return fig

    except Exception as e:
        st.error(f"创建客户区域分布图表时出错: {str(e)}")
        return None


# 创建客户产品偏好分析图
def create_customer_product_preference(data):
    """创建客户产品偏好分析图"""
    try:
        orders = data.get('orders', pd.DataFrame())

        if orders.empty:
            st.warning("数据不足，无法创建客户产品偏好分析图")
            return None

        # 确定必要列
        customer_col = None
        for col in ['客户代码', '经销商名称', '客户简称']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '产品代码' not in orders.columns or '销售额' not in orders.columns:
            st.warning("缺少必要的数据列")
            return None

        # 获取客户销售额排名
        customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
        customer_sales = customer_sales.sort_values('销售额', ascending=False)

        # 选取销售额前5的客户
        top_customers = customer_sales.head(5)[customer_col].tolist()

        # 为每个客户找出销售额前5的产品
        filtered_orders = orders[orders[customer_col].isin(top_customers)]

        # 使用客户简称显示（如果有）
        display_col = customer_col
        if '客户简称' in orders.columns and customer_col != '客户简称':
            customer_name_map = {}
            for _, row in orders.drop_duplicates([customer_col, '客户简称']).iterrows():
                customer_name_map[row[customer_col]] = row['客户简称']

            if customer_name_map:
                filtered_orders['显示名称'] = filtered_orders[customer_col].map(customer_name_map)
                display_col = '显示名称'

        # 创建产品偏好图
        product_col = '产品简称' if '产品简称' in filtered_orders.columns else '产品代码'

        # 客户-产品销售额透视表
        pivot_data = filtered_orders.pivot_table(
            values='销售额',
            index=display_col,
            columns=product_col,
            aggfunc='sum'
        ).fillna(0)

        # 如果产品太多，只保留每个客户销售额最高的5个产品
        if pivot_data.shape[1] > 20:  # 如果产品超过20个
            top_products_per_customer = {}
            for customer in pivot_data.index:
                customer_products = pivot_data.loc[customer].nlargest(5)
                for product in customer_products.index:
                    top_products_per_customer[product] = True

            # 只保留这些产品
            pivot_data = pivot_data[top_products_per_customer.keys()]

        # 计算每个客户的总销售额
        pivot_data['总销售额'] = pivot_data.sum(axis=1)

        # 按总销售额排序
        pivot_data = pivot_data.sort_values('总销售额', ascending=False)

        # 移除总销售额列
        pivot_data = pivot_data.drop(columns=['总销售额'])

        # 转换为百分比
        for customer in pivot_data.index:
            total = pivot_data.loc[customer].sum()
            pivot_data.loc[customer] = pivot_data.loc[customer] / total * 100 if total > 0 else 0

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale=[
                [0, 'rgb(255,255,255)'],  # 白色 (0%)
                [0.01, 'rgb(240,240,240)'],  # 极浅灰 (1%)
                [0.1, 'rgb(220,220,255)'],  # 浅蓝灰 (10%)
                [0.3, 'rgb(180,180,255)'],  # 中蓝灰 (30%)
                [0.5, 'rgb(120,120,255)'],  # 蓝色 (50%)
                [0.7, 'rgb(80,80,200)'],  # 深蓝 (70%)
                [1, 'rgb(0,0,128)']  # 深蓝 (100%)
            ],
            colorbar=dict(
                title="销售占比 (%)",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0%", "25%", "50%", "75%", "100%"]
            ),
            hovertemplate='客户: %{y}<br>产品: %{x}<br>销售占比: %{z:.1f}%<extra></extra>',
        ))

        # 更新布局
        fig.update_layout(
            title='主要客户产品偏好分析（销售额占比）',
            xaxis=dict(
                title="产品",
                tickangle=45
            ),
            yaxis=dict(
                title="客户"
            ),
            margin=dict(l=60, r=60, t=50, b=120),
            height=500  # 固定高度
        )

        return fig

    except Exception as e:
        st.error(f"创建客户产品偏好分析图表时出错: {str(e)}")
        return None


# 主程序
add_logo()

# 标题
st.markdown('<div class="main-header">客户分析仪表盘</div>', unsafe_allow_html=True)

# 加载数据
data = load_data()

# 应用客户专用筛选器
filtered_data = create_customer_filters(data)

# 计算关键指标
kpis = calculate_customer_kpis(filtered_data)

# 指标卡展示
st.markdown("### 🔑 客户关键指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="card-header">客户总数</p>
        <p class="card-value">{format_number(kpis.get('total_customers', 0))}</p>
        <p class="card-text">分析期内活跃客户</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="card-header">客户均销售额</p>
        <p class="card-value">{format_currency(kpis.get('avg_customer_sales', 0))}</p>
        <p class="card-text">平均每客户贡献</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="card-header">平均订单频次</p>
        <p class="card-value">{kpis.get('avg_order_frequency', 0):.1f}</p>
        <p class="card-text">每客户平均订单数</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p class="card-header">目标达成率</p>
        <p class="card-value">{format_percentage(kpis.get('target_achievement_rate', 0))}</p>
        <p class="card-text">{kpis.get('target_achievement_count', 0)}/{kpis.get('target_total_count', 0)} 客户达成月度目标</p>
    </div>
    """, unsafe_allow_html=True)

# 客户销售额排行
st.markdown('<div class="sub-header">📊 客户销售额排行</div>', unsafe_allow_html=True)
top_customers_fig = create_top_customers_chart(filtered_data)
if top_customers_fig:
    st.plotly_chart(top_customers_fig, use_container_width=True)

    # 添加图表解释
    top_customers_explanation = """
    <b>图表解读：</b> 此图展示了销售额最高的客户排名及其累计销售占比。柱状图显示每个客户的销售额，红线表示累计占比。
    悬停在客户上可查看其详细销售情况和主要产品。这有助于识别核心客户，优化客户关系管理策略。
    """
    add_chart_explanation(top_customers_explanation)
else:
    st.warning("无法生成客户销售额排行图表，请检查数据或筛选条件。")

# 客户目标达成率热力图
st.markdown('<div class="sub-header">📊 客户目标达成分析</div>', unsafe_allow_html=True)
target_achievement_fig = create_target_achievement_chart(filtered_data)
if target_achievement_fig:
    st.plotly_chart(target_achievement_fig, use_container_width=True)

    # 添加图表解释
    target_explanation = """
    <b>图表解读：</b> 此热力图展示了各客户月度销售目标的达成情况。颜色从红色(低达成率)到绿色(高达成率)，直观展示客户业绩表现。
    绿色区域表示目标达成良好的客户和月份，红色区域表示需要重点关注的客户和时期。通过分析热力图模式，可识别季节性波动和客户绩效趋势。
    """
    add_chart_explanation(target_explanation)
else:
    st.info("无法生成客户目标达成率图表，可能是因为缺少客户目标数据或当前筛选条件下没有匹配的数据。")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    # 客户趋势分析
    st.markdown('<div class="sub-header">📈 客户趋势分析</div>', unsafe_allow_html=True)
    trend_fig = create_customer_trend_chart(filtered_data)
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)

        # 添加图表解释
        trend_explanation = """
        <b>图表解读：</b> 此图展示了客户数量(蓝线)和销售额(红柱)的月度变化趋势。
        环比增长率标注在每个数据点上，绿色箭头表示增长，红色箭头表示下降。
        通过分析客户数与销售额的相关性，可评估客户开发与销售策略的有效性。
        """
        add_chart_explanation(trend_explanation)
    else:
        st.warning("无法生成客户趋势分析图表，请检查数据或筛选条件。")

with col2:
    # 客户区域分布
    st.markdown('<div class="sub-header">🗺️ 客户区域分布</div>', unsafe_allow_html=True)
    region_fig = create_customer_region_chart(filtered_data)
    if region_fig:
        st.plotly_chart(region_fig, use_container_width=True)

        # 添加图表解释
        region_explanation = """
        <b>图表解读：</b> 左侧饼图展示各区域客户数量分布，右侧图表对比各区域的客户均销售额(绿柱)和客户数量(蓝线)。
        通过区域客户密度与均值分析，可发现客户价值与区域特性的关联，指导区域市场策略调整。
        """
        add_chart_explanation(region_explanation)
    else:
        st.warning("无法生成客户区域分布图表，请检查数据或筛选条件。")

# 客户产品偏好分析
st.markdown('<div class="sub-header">🛒 客户产品偏好分析</div>', unsafe_allow_html=True)
preference_fig = create_customer_product_preference(filtered_data)
if preference_fig:
    st.plotly_chart(preference_fig, use_container_width=True)

    # 添加图表解释
    preference_explanation = """
    <b>图表解读：</b> 此热力图展示了主要客户对不同产品的偏好程度，颜色深浅表示销售额占比。
    横向查看可分析单个客户的产品购买结构，纵向查看可比较不同客户对同一产品的偏好差异。
    这有助于针对不同客户特性制定产品推荐策略，优化客户专属促销方案。
    """
    add_chart_explanation(preference_explanation)
else:
    st.warning("无法生成客户产品偏好分析图表，请检查数据或筛选条件。")