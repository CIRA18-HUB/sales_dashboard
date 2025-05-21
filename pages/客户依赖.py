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
import os

# 忽略警告
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="客户分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 更现代化的设计
st.markdown("""
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #1f3867;
        --secondary-color: #4c78a8;
        --accent-color: #f0f8ff;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --gray-color: #6c757d;
    }

    /* 主标题 */
    .main-header {
        font-size: 2rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }

    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
        cursor: pointer;
        border-left: 5px solid var(--primary-color);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.15);
    }

    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .card-text {
        font-size: 0.9rem;
        color: var(--gray-color);
    }

    .card-trend {
        margin-top: 0.5rem;
        font-weight: 500;
    }

    .trend-up {
        color: var(--success-color);
    }

    .trend-down {
        color: var(--danger-color);
    }

    /* 图表容器 */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* 图表解释框 */
    .chart-explanation {
        background-color: var(--accent-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 5px solid var(--primary-color);
        font-size: 0.95rem;
    }

    /* 章节标题 */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }

    /* 提示框 */
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 5px solid var(--success-color);
    }

    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 5px solid var(--warning-color);
    }

    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 5px solid var(--danger-color);
    }

    /* 登录框样式 */
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
    }

    .login-header {
        text-align: center;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* 风险标签 */
    .risk-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }

    .risk-high {
        background-color: #F44336;
        color: white;
    }

    .risk-medium {
        background-color: #FF9800;
        color: white;
    }

    .risk-low {
        background-color: #4CAF50;
        color: white;
    }

    /* 加载动画 */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(31,56,103,.3);
        border-radius: 50%;
        border-top-color: #1f3867;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div style="font-size: 1.8rem; color: #1f3867; text-align: center; margin-bottom: 1.5rem; font-weight: 600;">客户分析仪表盘 | 登录</div>',
        unsafe_allow_html=True)

    # 创建居中的登录框
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <h2 class="login-header">请输入密码</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("密码", type="password", key="password_input")

        # 登录按钮
        login_button = st.button("登录")

        # 验证密码
        if login_button:
            if password == 'SAL!2025':
                st.session_state['authenticated'] = True
                st.success("登录成功！")
                try:
                    st.rerun()
                except AttributeError:
                    try:
                        st.experimental_rerun()
                    except:
                        st.error("请刷新页面以查看更改")
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()


# ====== 实用工具函数 ======

# 格式化货币
def format_currency(value):
    """将数值格式化为货币形式"""
    if pd.isna(value) or value is None:
        return "¥0"

    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except:
            return value

    if abs(value) >= 1_000_000:
        return f"¥{value / 1_000_000:.2f}M"
    elif abs(value) >= 1000:
        return f"¥{value / 1000:.1f}K"
    else:
        return f"¥{value:.0f}"


# 格式化数字
def format_number(value):
    """格式化数字，大数使用K/M表示"""
    if pd.isna(value) or value is None:
        return "0"

    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except:
            return value

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs(value) >= 1000:
        return f"{value / 1000:.1f}K"
    else:
        return f"{value:.0f}"


# 格式化百分比
def format_percentage(value):
    """将数值格式化为百分比形式"""
    if pd.isna(value) or value is None:
        return "0%"

    if isinstance(value, str):
        try:
            value = float(value.replace('%', '').replace(',', ''))
        except:
            return value

    return f"{value:.1f}%"


# 强制加载真实数据文件
@st.cache_data
def load_real_data_files():
    """强制加载真实数据文件，不使用模拟数据"""

    with st.spinner('正在加载数据文件...'):
        data = {}

        try:
            # 必需的文件列表
            required_files = {
                'sales_orders': '仪表盘原始数据.xlsx',
                'customer_target': '仪表盘客户月度指标维护.xlsx',
                'customer_relation': '仪表盘人与客户关系表.xlsx'
            }

            missing_files = []

            # 逐个加载文件
            for data_key, filename in required_files.items():
                file_path = filename  # 文件在项目根目录

                if os.path.exists(file_path):
                    try:
                        data[data_key] = pd.read_excel(file_path)
                        st.sidebar.success(f"✅ {filename} 加载成功")
                    except Exception as e:
                        st.error(f"❌ 读取文件 {filename} 失败: {str(e)}")
                        st.stop()
                else:
                    missing_files.append(filename)

            # 检查缺失文件
            if missing_files:
                st.error(f"❌ 以下必需文件缺失: {', '.join(missing_files)}")
                st.error("请确保所有Excel文件都放在项目根目录下")
                st.stop()

            # 验证关键数据
            if data['sales_orders'].empty:
                st.error("❌ 销售订单数据为空")
                st.stop()

            # 数据预处理
            orders = data['sales_orders']

            # 确保销售额列存在
            if '销售额' not in orders.columns and '求和项:金额（元）' in orders.columns:
                orders['销售额'] = orders['求和项:金额（元）']
                data['sales_orders'] = orders

            # 确保日期格式正确
            if '发运月份' in orders.columns:
                orders['发运月份'] = pd.to_datetime(orders['发运月份'])
                data['sales_orders'] = orders

            # 验证客户目标数据
            if not data['customer_target'].empty:
                if '月份' in data['customer_target'].columns:
                    data['customer_target']['月份'] = pd.to_datetime(data['customer_target']['月份'])

            st.sidebar.success(f"✅ 数据加载完成，订单记录数: {len(orders)}")

            return data

        except Exception as e:
            st.error(f"❌ 数据加载失败: {str(e)}")
            st.stop()


# 获取重点客户列表
def get_key_customers(data, method='top_20'):
    """获取重点客户列表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return []

        # 确定客户列
        customer_col = None
        for col in ['经销商名称', '客户简称', '客户代码']:
            if col in orders.columns:
                customer_col = col
                break

        if not customer_col or '销售额' not in orders.columns:
            return []

        # 按客户汇总销售额
        customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
        customer_sales = customer_sales.sort_values('销售额', ascending=False)

        if method == 'top_20':
            # 前20名客户
            return customer_sales.head(20)[customer_col].tolist()
        elif method == 'pareto_80':
            # 销售额占总销售额80%的客户
            total_sales = customer_sales['销售额'].sum()
            customer_sales['累计销售额'] = customer_sales['销售额'].cumsum()
            customer_sales['累计占比'] = customer_sales['累计销售额'] / total_sales
            key_customers = customer_sales[customer_sales['累计占比'] <= 0.8]
            return key_customers[customer_col].tolist()
        elif method == 'top_20_percent':
            # 前20%的客户
            top_count = max(1, int(len(customer_sales) * 0.2))
            return customer_sales.head(top_count)[customer_col].tolist()

        return customer_sales.head(20)[customer_col].tolist()

    except Exception as e:
        st.error(f"获取重点客户列表失败: {str(e)}")
        return []


# 客户筛选器
def create_customer_filters(data):
    """创建客户分析专用的筛选器"""
    filtered_data = data.copy()

    if not data or 'sales_orders' not in data or data['sales_orders'].empty:
        st.sidebar.error("❌ 无法加载客户数据")
        return filtered_data

    orders = data['sales_orders'].copy()
    customer_relation = data.get('customer_relation', pd.DataFrame())

    with st.sidebar:
        st.markdown("## 🔍 客户筛选")
        st.markdown("---")

        # 1. 区域筛选
        if '所属区域' in orders.columns:
            all_regions = sorted(['全部'] + list(orders['所属区域'].unique()))
            selected_region = st.selectbox(
                "选择区域", all_regions, index=0, key="customer_region_filter"
            )
            if selected_region != '全部':
                orders = orders[orders['所属区域'] == selected_region]

        # 2. 客户状态筛选
        if not customer_relation.empty and '状态' in customer_relation.columns:
            status_options = ['全部', '正常', '闭户']
            selected_status = st.selectbox(
                "客户状态", status_options, index=0, key="customer_status_filter"
            )
            if selected_status != '全部':
                valid_customers = customer_relation[customer_relation['状态'] == selected_status]['客户'].unique()
                orders = orders[orders['经销商名称'].isin(valid_customers)]

        # 3. 销售员筛选
        if '申请人' in orders.columns:
            all_sales = sorted(['全部'] + list(orders['申请人'].unique()))
            selected_sales = st.selectbox(
                "销售员", all_sales, index=0, key="customer_salesperson_filter"
            )
            if selected_sales != '全部':
                orders = orders[orders['申请人'] == selected_sales]

        # 4. 日期范围筛选
        if '发运月份' in orders.columns:
            try:
                # 获取当前年份数据作为默认
                current_year = datetime.now().year
                start_of_year = datetime(current_year, 1, 1)
                end_of_year = datetime(current_year, 12, 31)

                min_date = orders['发运月份'].min().date()
                max_date = orders['发运月份'].max().date()

                # 调整默认日期范围
                default_start = max(start_of_year.date(), min_date)
                default_end = min(end_of_year.date(), max_date)

                st.markdown("### 📅 日期范围")
                start_date = st.date_input(
                    "开始日期", value=default_start, min_value=min_date, max_value=max_date,
                    key="customer_start_date"
                )
                end_date = st.date_input(
                    "结束日期", value=default_end, min_value=min_date, max_value=max_date,
                    key="customer_end_date"
                )

                if end_date < start_date:
                    st.warning("结束日期不能早于开始日期")
                    end_date = start_date

                # 应用日期筛选
                start_datetime = pd.Timestamp(start_date)
                end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

                orders = orders[(orders['发运月份'] >= start_datetime) &
                                (orders['发运月份'] <= end_datetime)]

            except Exception as e:
                st.warning(f"日期筛选器错误: {e}")

        # 筛选器重置按钮
        if st.button("🔄 重置筛选条件", key="reset_customer_filters"):
            try:
                st.rerun()
            except AttributeError:
                try:
                    st.experimental_rerun()
                except:
                    st.warning("请手动刷新页面")

    # 更新筛选后的数据
    filtered_data['sales_orders'] = orders
    return filtered_data


# 计算客户关键指标
def calculate_customer_kpis(data):
    """计算客户分析的关键指标"""
    kpis = {}

    try:
        orders = data.get('sales_orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty:
            return kpis

        # 确定客户列
        customer_col = '经销商名称'  # 主要使用经销商名称

        # 1. 总客户数量
        kpis['total_customers'] = orders[customer_col].nunique()

        # 2. 客户平均销售额
        if '销售额' in orders.columns:
            total_sales = orders['销售额'].sum()
            kpis['total_sales'] = total_sales
            kpis['avg_customer_sales'] = total_sales / kpis['total_customers'] if kpis['total_customers'] > 0 else 0

            # 计算重点客户贡献
            key_customers = get_key_customers(data, 'top_20')
            if key_customers:
                key_customer_sales = orders[orders[customer_col].isin(key_customers)]['销售额'].sum()
                kpis['key_customers_contribution'] = key_customer_sales / total_sales if total_sales > 0 else 0
                kpis['key_customers_count'] = len(key_customers)

            # 计算环比增长
            if '发运月份' in orders.columns:
                # 当前月和上月
                current_month = orders['发运月份'].max().to_period('M')
                previous_month = (current_month.to_timestamp() - pd.Timedelta(days=30)).to_period('M')

                current_month_sales = orders[orders['发运月份'].dt.to_period('M') == current_month]['销售额'].sum()
                previous_month_sales = orders[orders['发运月份'].dt.to_period('M') == previous_month]['销售额'].sum()

                if previous_month_sales > 0:
                    kpis['sales_growth'] = (current_month_sales - previous_month_sales) / previous_month_sales
                else:
                    kpis['sales_growth'] = 0

                # 客户数环比
                current_month_customers = orders[orders['发运月份'].dt.to_period('M') == current_month][
                    customer_col].nunique()
                previous_month_customers = orders[orders['发运月份'].dt.to_period('M') == previous_month][
                    customer_col].nunique()

                if previous_month_customers > 0:
                    kpis['customer_count_growth'] = (
                                                                current_month_customers - previous_month_customers) / previous_month_customers
                else:
                    kpis['customer_count_growth'] = 0

        # 3. 订单频次和客单价
        orders_count = orders.groupby(customer_col).size()
        kpis['avg_order_frequency'] = orders_count.mean()

        if '销售额' in orders.columns:
            total_orders = len(orders)
            kpis['avg_order_value'] = total_sales / total_orders if total_orders > 0 else 0

        # 4. 目标达成率
        if not customer_target.empty and '月度指标' in customer_target.columns:
            try:
                # 准备月份匹配
                orders_monthly = orders.copy()
                orders_monthly['月份'] = orders_monthly['发运月份'].dt.to_period('M').dt.to_timestamp()

                # 按客户和月份汇总销售额
                sales_monthly = orders_monthly.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

                # 合并目标数据（使用客户字段匹配经销商名称）
                target_data = customer_target.copy()
                merged = pd.merge(sales_monthly, target_data,
                                  left_on=[customer_col, '月份'],
                                  right_on=['客户', '月份'], how='inner')

                if not merged.empty:
                    # 计算达成率
                    merged['达成率'] = merged['销售额'] / merged['月度指标'] * 100
                    merged = merged[merged['月度指标'] > 0]  # 排除目标为0的记录

                    if not merged.empty:
                        kpis['target_achievement'] = merged['达成率'].mean()
                        kpis['target_achievement_count'] = sum(merged['达成率'] >= 100)
                        kpis['target_total_count'] = len(merged)
                        kpis['target_achievement_rate'] = (
                            kpis['target_achievement_count'] / kpis['target_total_count'] * 100
                            if kpis['target_total_count'] > 0 else 0)

            except Exception as e:
                st.warning(f"目标达成率计算错误: {str(e)}")

        return kpis

    except Exception as e:
        st.error(f"计算客户KPI时出错: {str(e)}")
        return {}


# 创建重点客户销售排行图表
def create_key_customers_chart(data, top_n=20):
    """创建重点客户销售额排行图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return None

        customer_col = '经销商名称'

        # 按客户汇总销售额
        customer_sales = orders.groupby(customer_col)['销售额'].sum().reset_index()
        customer_sales = customer_sales.sort_values('销售额', ascending=False).head(top_n)

        # 使用客户简称显示
        if '客户简称' in orders.columns:
            customer_name_map = orders.drop_duplicates([customer_col, '客户简称']).set_index(customer_col)[
                '客户简称'].to_dict()
            customer_sales['显示名称'] = customer_sales[customer_col].map(lambda x: customer_name_map.get(x, x))
        else:
            customer_sales['显示名称'] = customer_sales[customer_col]

        # 计算累计贡献
        total_sales = customer_sales['销售额'].sum()
        customer_sales['累计销售额'] = customer_sales['销售额'].cumsum()
        customer_sales['累计占比'] = customer_sales['累计销售额'] / total_sales * 100

        # 创建图表
        fig = go.Figure()

        # 渐变颜色
        colors = px.colors.sequential.Blues_r
        color_scale = [colors[int(i / (len(customer_sales) - 1) * (len(colors) - 1))]
                       for i in range(len(customer_sales))]

        # 销售额条形图
        fig.add_trace(go.Bar(
            y=customer_sales['显示名称'],
            x=customer_sales['销售额'],
            marker_color=color_scale,
            orientation='h',
            name='销售额',
            text=customer_sales['销售额'].apply(lambda x: format_currency(x)),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>销售额: %{text}<br>累计占比: %{customdata:.1f}%<extra></extra>',
            customdata=customer_sales['累计占比']
        ))

        # 更新布局
        fig.update_layout(
            title="重点客户销售额排行TOP" + str(top_n),
            xaxis_title="销售额 (元)",
            yaxis_title="客户",
            yaxis=dict(autorange="reversed"),
            height=max(500, len(customer_sales) * 25),
            margin=dict(l=200, r=60, t=80, b=60),
            plot_bgcolor='white'
        )

        return fig

    except Exception as e:
        st.error(f"创建重点客户排行图表失败: {str(e)}")
        return None


# 创建客户目标达成分析图表
def create_target_achievement_chart(data):
    """创建客户目标达成分析图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())
        customer_target = data.get('customer_target', pd.DataFrame())

        if orders.empty or customer_target.empty:
            return None

        customer_col = '经销商名称'

        # 获取重点客户
        key_customers = get_key_customers(data, 'top_20')
        if not key_customers:
            return None

        # 筛选重点客户数据
        orders_filtered = orders[orders[customer_col].isin(key_customers)].copy()

        # 准备月份数据
        orders_filtered['月份'] = orders_filtered['发运月份'].dt.to_period('M').dt.to_timestamp()

        # 按客户和月份汇总销售额
        sales_monthly = orders_filtered.groupby([customer_col, '月份'])['销售额'].sum().reset_index()

        # 合并目标数据
        merged = pd.merge(sales_monthly, customer_target,
                          left_on=[customer_col, '月份'],
                          right_on=['客户', '月份'], how='inner')

        if merged.empty:
            return None

        # 只保留有目标的数据
        merged = merged[merged['月度指标'] > 0]

        if merged.empty:
            return None

        # 计算达成率
        merged['达成率'] = (merged['销售额'] / merged['月度指标'] * 100).fillna(0)

        # 使用客户简称
        if '客户简称' in orders.columns:
            customer_name_map = orders.drop_duplicates([customer_col, '客户简称']).set_index(customer_col)[
                '客户简称'].to_dict()
            merged['显示名称'] = merged[customer_col].map(lambda x: customer_name_map.get(x, x))
        else:
            merged['显示名称'] = merged[customer_col]

        # 创建透视表
        pivot_data = merged.pivot_table(
            values='达成率',
            index='月份',
            columns='显示名称',
            aggfunc='mean'
        ).fillna(0)

        # 限制显示的客户数量
        if pivot_data.shape[1] > 15:
            customer_avg = pivot_data.mean().sort_values(ascending=False)
            pivot_data = pivot_data[customer_avg.head(15).index]

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=[d.strftime('%Y-%m') for d in pivot_data.index],
            colorscale=[
                [0, 'rgb(165,0,38)'],  # 深红色 (0%)
                [0.25, 'rgb(244,109,67)'],  # 浅红色 (25%)
                [0.5, 'rgb(255,255,191)'],  # 黄色 (50%)
                [0.75, 'rgb(116,173,209)'],  # 浅蓝色 (75%)
                [0.9, 'rgb(49,104,142)'],  # 蓝色 (90%)
                [1, 'rgb(0,68,27)']  # 深绿色 (100%+)
            ],
            colorbar=dict(
                title="达成率 (%)",
                tickvals=[0, 25, 50, 75, 100, 150, 200],
                ticktext=["0%", "25%", "50%", "75%", "100%", "150%", "200%+"]
            ),
            hovertemplate='客户: %{x}<br>月份: %{y}<br>达成率: %{z:.1f}%<extra></extra>',
            zauto=False,
            zmin=0,
            zmax=200
        ))

        # 添加数值标注
        for i, month in enumerate(pivot_data.index):
            for j, customer in enumerate(pivot_data.columns):
                value = pivot_data.iloc[i, j]
                if not pd.isna(value) and value > 0:
                    text_color = 'white' if value < 70 or value > 130 else 'black'
                    fig.add_annotation(
                        x=customer,
                        y=month.strftime('%Y-%m'),
                        text=f"{value:.0f}%",
                        showarrow=False,
                        font=dict(size=9, color=text_color)
                    )

        fig.update_layout(
            title="重点客户月度目标达成率分析",
            xaxis_title="客户",
            yaxis_title="月份",
            xaxis=dict(tickangle=45),
            yaxis=dict(autorange="reversed"),
            height=max(500, len(pivot_data) * 40),
            margin=dict(l=80, r=80, t=80, b=120)
        )

        return fig

    except Exception as e:
        st.error(f"创建目标达成分析图表失败: {str(e)}")
        return None


# 创建客户产品偏好强度分析
def create_customer_product_preference(data):
    """创建客户产品偏好强度分析"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return None

        customer_col = '经销商名称'

        # 获取重点客户
        key_customers = get_key_customers(data, 'top_20')
        if not key_customers:
            return None

        # 筛选重点客户数据
        filtered_orders = orders[orders[customer_col].isin(key_customers)].copy()

        # 使用客户简称
        if '客户简称' in orders.columns:
            customer_name_map = orders.drop_duplicates([customer_col, '客户简称']).set_index(customer_col)[
                '客户简称'].to_dict()
            filtered_orders['显示名称'] = filtered_orders[customer_col].map(lambda x: customer_name_map.get(x, x))
        else:
            filtered_orders['显示名称'] = filtered_orders[customer_col]

        # 使用产品简称
        product_col = '产品简称' if '产品简称' in filtered_orders.columns else '产品名称'

        # 创建客户-产品销售额透视表
        pivot_data = filtered_orders.pivot_table(
            values='销售额',
            index='显示名称',
            columns=product_col,
            aggfunc='sum'
        ).fillna(0)

        # 转换为百分比（每个客户的产品偏好强度）
        pivot_pct = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100

        # 只保留有意义的产品（至少有一个客户的偏好强度超过5%）
        significant_products = pivot_pct.columns[pivot_pct.max() >= 5]
        pivot_pct = pivot_pct[significant_products]

        if pivot_pct.empty:
            return None

        # 按客户销售额排序
        customer_total_sales = pivot_data.sum(axis=1).sort_values(ascending=False)
        pivot_pct = pivot_pct.reindex(customer_total_sales.index)

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=pivot_pct.values,
            x=pivot_pct.columns,
            y=pivot_pct.index,
            colorscale=[
                [0, 'rgb(255,255,255)'],  # 白色 (0%)
                [0.05, 'rgb(240,248,255)'],  # 极浅蓝 (5%)
                [0.1, 'rgb(200,220,255)'],  # 浅蓝 (10%)
                [0.2, 'rgb(130,170,255)'],  # 中蓝 (20%)
                [0.4, 'rgb(60,120,220)'],  # 深蓝 (40%)
                [0.6, 'rgb(0,80,180)'],  # 更深蓝 (60%)
                [1, 'rgb(0,40,120)']  # 深深蓝 (100%)
            ],
            colorbar=dict(
                title="偏好强度 (%)",
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=["0%", "20%", "40%", "60%", "80%", "100%"]
            ),
            hovertemplate='客户: %{y}<br>产品: %{x}<br>偏好强度: %{z:.1f}%<extra></extra>',
            zauto=True
        ))

        # 添加百分比标注（只显示主要偏好）
        for i, customer in enumerate(pivot_pct.index):
            for j, product in enumerate(pivot_pct.columns):
                value = pivot_pct.iloc[i, j]
                if value >= 10:  # 只显示偏好强度>=10%的值
                    text_color = 'white' if value >= 30 else 'black'
                    fig.add_annotation(
                        x=product,
                        y=customer,
                        text=f"{value:.1f}%",
                        showarrow=False,
                        font=dict(size=9, color=text_color)
                    )

        fig.update_layout(
            title="重点客户产品偏好强度分析",
            xaxis_title="产品",
            yaxis_title="客户",
            xaxis=dict(tickangle=45),
            height=max(500, len(pivot_pct) * 40),
            margin=dict(l=150, r=50, t=80, b=120)
        )

        return fig

    except Exception as e:
        st.error(f"创建客户产品偏好分析失败: {str(e)}")
        return None


# 创建客户趋势分析图
def create_customer_trend_chart(data):
    """创建客户趋势分析图"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return None

        customer_col = '经销商名称'

        # 按月份汇总数据
        orders['月份'] = orders['发运月份'].dt.to_period('M').dt.to_timestamp()
        monthly_stats = orders.groupby('月份').agg(
            客户数量=pd.NamedAgg(column=customer_col, aggfunc='nunique'),
            销售额=pd.NamedAgg(column='销售额', aggfunc='sum'),
            订单数=pd.NamedAgg(column=customer_col, aggfunc='count')
        ).reset_index()

        # 计算环比增长率
        monthly_stats['客户环比'] = monthly_stats['客户数量'].pct_change() * 100
        monthly_stats['销售额环比'] = monthly_stats['销售额'].pct_change() * 100

        # 计算移动平均
        if len(monthly_stats) >= 3:
            monthly_stats['客户数量_MA3'] = monthly_stats['客户数量'].rolling(window=3).mean()
            monthly_stats['销售额_MA3'] = monthly_stats['销售额'].rolling(window=3).mean()

        # 创建双轴图表
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 客户数量折线图
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['客户数量'],
                mode='lines+markers',
                name='客户数量',
                line=dict(color='rgba(58, 134, 255, 1)', width=3),
                marker=dict(size=8),
                hovertemplate='客户数量: %{y}<br>环比: %{text:.1f}%<extra></extra>',
                text=monthly_stats['客户环比'].fillna(0)
            ),
            secondary_y=False
        )

        # 销售额面积图
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['月份'],
                y=monthly_stats['销售额'],
                mode='lines+markers',
                name='销售额',
                line=dict(color='rgba(231, 107, 124, 1)', width=3),
                marker=dict(size=8),
                fill='tonexty',
                fillcolor='rgba(231, 107, 124, 0.2)',
                hovertemplate='销售额: %{y:,.0f}元<br>环比: %{text:.1f}%<extra></extra>',
                text=monthly_stats['销售额环比'].fillna(0)
            ),
            secondary_y=True
        )

        # 添加移动平均线
        if len(monthly_stats) >= 3:
            fig.add_trace(
                go.Scatter(
                    x=monthly_stats['月份'],
                    y=monthly_stats['客户数量_MA3'],
                    mode='lines',
                    name='客户数量(3月移动平均)',
                    line=dict(color='rgba(58, 134, 255, 0.5)', width=2, dash='dash'),
                    hovertemplate='3月移动平均: %{y:.1f}<extra></extra>'
                ),
                secondary_y=False
            )

        # 更新轴和布局
        fig.update_xaxes(title_text="月份")
        fig.update_yaxes(title_text="客户数量", secondary_y=False)
        fig.update_yaxes(title_text="销售额 (元)", tickformat=",", secondary_y=True)

        fig.update_layout(
            title="客户数量与销售额月度趋势",
            height=550,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    except Exception as e:
        st.error(f"创建客户趋势分析失败: {str(e)}")
        return None


# 创建区域客户依赖风险分析
def create_region_dependency_risk_chart(data):
    """创建区域客户依赖风险分析"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty or '所属区域' not in orders.columns:
            return None

        customer_col = '经销商名称'

        # 按区域和客户汇总销售额
        region_customer_sales = orders.groupby(['所属区域', customer_col])['销售额'].sum().reset_index()

        # 计算每个区域的总销售额
        region_total_sales = orders.groupby('所属区域')['销售额'].sum()

        # 计算每个客户在其所在区域的依赖度
        region_customer_sales['区域总销售额'] = region_customer_sales['所属区域'].map(region_total_sales)
        region_customer_sales['依赖度'] = region_customer_sales['销售额'] / region_customer_sales['区域总销售额'] * 100

        # 找出每个区域的最大客户依赖度
        max_dependency_by_region = region_customer_sales.groupby('所属区域').agg({
            '依赖度': 'max',
            customer_col: lambda x: x.iloc[
                region_customer_sales.loc[x.index, '依赖度'].idxmax() - region_customer_sales.index[0]],
            '销售额': 'max',
            '区域总销售额': 'first'
        }).reset_index()

        max_dependency_by_region.columns = ['所属区域', '最大依赖度', '最大依赖客户', '最大客户销售额', '区域总销售额']

        # 风险等级分类
        def get_risk_level(dependency):
            if dependency >= 40:
                return '高风险', '#F44336'
            elif dependency >= 20:
                return '中风险', '#FF9800'
            else:
                return '低风险', '#4CAF50'

        max_dependency_by_region[['风险等级', '风险颜色']] = max_dependency_by_region['最大依赖度'].apply(
            lambda x: pd.Series(get_risk_level(x))
        )

        # 使用客户简称
        if '客户简称' in orders.columns:
            customer_name_map = orders.drop_duplicates([customer_col, '客户简称']).set_index(customer_col)[
                '客户简称'].to_dict()
            max_dependency_by_region['客户简称'] = max_dependency_by_region['最大依赖客户'].map(
                lambda x: customer_name_map.get(x, x)
            )
        else:
            max_dependency_by_region['客户简称'] = max_dependency_by_region['最大依赖客户']

        # 创建气泡图
        fig = go.Figure()

        for idx, row in max_dependency_by_region.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['所属区域']],
                y=[row['最大依赖度']],
                mode='markers+text',
                marker=dict(
                    size=row['区域总销售额'] / max_dependency_by_region['区域总销售额'].max() * 80 + 20,
                    color=row['风险颜色'],
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=f"{row['风险等级']}<br>{row['最大依赖度']:.1f}%",
                textposition="middle center",
                textfont=dict(color='white', size=10),
                name=row['所属区域'],
                hovertemplate=f'<b>{row["所属区域"]}</b><br>' +
                              f'最大依赖客户: {row["客户简称"]}<br>' +
                              f'依赖度: {row["最大依赖度"]:.1f}%<br>' +
                              f'客户销售额: {format_currency(row["最大客户销售额"])}<br>' +
                              f'区域总销售额: {format_currency(row["区域总销售额"])}<br>' +
                              f'风险等级: {row["风险等级"]}<extra></extra>',
                showlegend=False
            ))

        # 添加风险等级参考线
        fig.add_hline(y=40, line_dash="dash", line_color="red",
                      annotation_text="高风险线 (40%)", annotation_position="bottom right")
        fig.add_hline(y=20, line_dash="dash", line_color="orange",
                      annotation_text="中风险线 (20%)", annotation_position="bottom right")

        fig.update_layout(
            title="各区域客户依赖风险分析",
            xaxis_title="区域",
            yaxis_title="最大客户依赖度 (%)",
            yaxis=dict(range=[0, max(max_dependency_by_region['最大依赖度'].max() * 1.1, 50)]),
            height=500,
            plot_bgcolor='white'
        )

        return fig

    except Exception as e:
        st.error(f"创建区域依赖风险分析失败: {str(e)}")
        return None


# 图表解释函数
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 创建可点击卡片
def create_clickable_metric_card(header, value, description, trend=None, trend_value=None):
    """创建指标卡片"""
    trend_class = ""
    trend_symbol = ""

    if trend:
        if trend == "up":
            trend_class = "trend-up"
            trend_symbol = "▲"
        elif trend == "down":
            trend_class = "trend-down"
            trend_symbol = "▼"

    trend_html = ""
    if trend and trend_value is not None:
        trend_html = f'<p class="card-trend {trend_class}">{trend_symbol} {abs(trend_value):.1f}%</p>'

    card_html = f"""
    <div class="metric-card">
        <p class="card-header">{header}</p>
        <p class="card-value">{value}</p>
        <p class="card-text">{description}</p>
        {trend_html}
    </div>
    """

    return card_html


# ====== 主程序 ======

# 加载真实数据
data = load_real_data_files()

# 应用筛选器
filtered_data = create_customer_filters(data)

# 标题
st.markdown('<div class="main-header">客户分析仪表盘</div>', unsafe_allow_html=True)

# 计算关键指标
kpis = calculate_customer_kpis(filtered_data)

# 创建标签页
tab_names = ["📊 客户概览", "🎯 目标达成分析", "📈 趋势与偏好", "⚠️ 风险分析"]
tabs = st.tabs(tab_names)

# 客户概览标签
with tabs[0]:
    # 核心指标卡片
    st.markdown('<div class="section-header">🔑 核心客户指标</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            create_clickable_metric_card(
                header="客户总数",
                value=format_number(kpis.get('total_customers', 0)),
                description="活跃交易客户数量",
                trend="up" if kpis.get('customer_count_growth', 0) > 0 else "down" if kpis.get('customer_count_growth',
                                                                                               0) < 0 else None,
                trend_value=kpis.get('customer_count_growth', 0) * 100 if kpis.get(
                    'customer_count_growth') is not None else None
            ),
            unsafe_allow_html=True
        )

    with col2:
        key_count = kpis.get('key_customers_count', 0)
        key_contribution = kpis.get('key_customers_contribution', 0) * 100
        st.markdown(
            create_clickable_metric_card(
                header="重点客户贡献",
                value=f"{key_contribution:.1f}%",
                description=f"TOP {key_count} 客户销售占比"
            ),
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            create_clickable_metric_card(
                header="目标达成率",
                value=format_percentage(kpis.get('target_achievement_rate', 0)),
                description=f"{kpis.get('target_achievement_count', 0)}/{kpis.get('target_total_count', 0)} 客户达成目标"
            ),
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            create_clickable_metric_card(
                header="客户均销售额",
                value=format_currency(kpis.get('avg_customer_sales', 0)),
                description="平均每客户贡献",
                trend="up" if kpis.get('sales_growth', 0) > 0 else "down" if kpis.get('sales_growth', 0) < 0 else None,
                trend_value=kpis.get('sales_growth', 0) * 100 if kpis.get('sales_growth') is not None else None
            ),
            unsafe_allow_html=True
        )

    # 重点客户销售排行
    st.markdown('<div class="section-header">📊 重点客户销售贡献TOP20</div>', unsafe_allow_html=True)
    key_customers_fig = create_key_customers_chart(filtered_data, 20)
    if key_customers_fig:
        st.plotly_chart(key_customers_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 此图展示销售额最高的20个重点客户及其累计销售贡献。条形图长度表示销售额，
        悬停可查看客户详情和累计占比。通过此图可快速识别核心客户群体，优化客户关系管理策略。
        """)
    else:
        st.warning("⚠️ 无法生成重点客户排行图表")

# 目标达成分析标签
with tabs[1]:
    st.markdown('<div class="section-header">🎯 重点客户目标达成分析</div>', unsafe_allow_html=True)
    target_fig = create_target_achievement_chart(filtered_data)
    if target_fig:
        st.plotly_chart(target_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 热力图展示重点客户月度销售目标达成情况。颜色从红色(低达成率)到绿色(高达成率)，
        数字标签显示具体达成百分比。可识别客户的季节性表现和稳定性，评估目标设置的合理性。
        """)
    else:
        st.info("ℹ️ 暂无客户目标达成数据或当前筛选条件下无匹配数据")

# 趋势与偏好分析标签
with tabs[2]:
    # 客户趋势分析
    st.markdown('<div class="section-header">📈 客户数量与销售趋势</div>', unsafe_allow_html=True)
    trend_fig = create_customer_trend_chart(filtered_data)
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 展示客户数量(蓝线)和销售额(红区域)的月度变化趋势。虚线为移动平均值，
        平滑短期波动。通过分析客户数与销售额的相关性，可评估客户开发策略的有效性。
        """)
    else:
        st.warning("⚠️ 无法生成客户趋势分析")

    # 客户产品偏好分析
    st.markdown('<div class="section-header">🛒 重点客户产品偏好强度</div>', unsafe_allow_html=True)
    preference_fig = create_customer_product_preference(filtered_data)
    if preference_fig:
        st.plotly_chart(preference_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 热力图展示重点客户对不同产品的偏好强度（购买占比）。颜色深浅表示偏好程度，
        数字标签显示具体占比。横向分析单个客户的产品购买结构，纵向比较不同客户的产品偏好差异。
        """)
    else:
        st.warning("⚠️ 无法生成客户产品偏好分析")

# 风险分析标签
with tabs[3]:
    st.markdown('<div class="section-header">⚠️ 区域客户依赖风险分析</div>', unsafe_allow_html=True)
    risk_fig = create_region_dependency_risk_chart(filtered_data)
    if risk_fig:
        st.plotly_chart(risk_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 气泡图展示各区域对单一客户的最大依赖度。气泡大小表示区域总销售额，
        颜色和位置表示风险等级：高风险(≥40%)、中风险(20%-40%)、低风险(<20%)。
        帮助识别区域业务集中风险，制定风险分散策略。
        """)
    else:
        st.warning("⚠️ 无法生成区域依赖风险分析")

# 页脚信息
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; margin-top: 2rem;">'
    '客户分析仪表盘 | 基于真实数据分析 | 数据更新时间: 每周一17:00'
    '</div>',
    unsafe_allow_html=True
)