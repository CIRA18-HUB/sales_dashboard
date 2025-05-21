# 产品组合.py - 简化版产品组合分析页面
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
    page_title="产品组合分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
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

    /* BCG矩阵样式 */
    .bcg-matrix {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 0.25rem 1.2rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
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
        '<div style="font-size: 1.8rem; color: #1f3867; text-align: center; margin-bottom: 1.5rem; font-weight: 600;">产品组合分析仪表盘 | 登录</div>',
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


# 简化产品名称
def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称"""
    try:
        if not isinstance(product_name, str):
            return str(product_code)

        if '口力' in product_name:
            name_parts = product_name.split('口力')
            if len(name_parts) > 1:
                name_part = name_parts[1]
                if '-' in name_part:
                    name_part = name_part.split('-')[0].strip()

                # 去掉规格和包装形式
                for suffix in ['G分享装袋装', 'G盒装', 'G袋装', 'KG迷你包', 'KG随手包']:
                    if suffix in name_part:
                        name_part = name_part.split(suffix)[0]
                        break

                # 去掉数字和单位
                simple_name = re.sub(r'\d+\w*\s*', '', name_part).strip()

                if simple_name:
                    return f"{simple_name}"

        return str(product_code)
    except Exception as e:
        return str(product_code)


# 数据加载函数
@st.cache_data
def load_product_data():
    """加载产品分析相关数据"""
    with st.spinner('正在加载产品数据...'):
        data = {}

        try:
            # 主要销售数据文件
            main_file = '仪表盘原始数据.xlsx'

            if os.path.exists(main_file):
                try:
                    data['sales_orders'] = pd.read_excel(main_file)
                    st.sidebar.success(f"✅ {main_file} 加载成功")
                except Exception as e:
                    st.error(f"❌ 读取文件 {main_file} 失败: {str(e)}")
                    st.stop()
            else:
                st.error(f"❌ 必需文件缺失: {main_file}")
                st.stop()

            # 可选的新品代码文件
            new_products_file = '仪表盘新品代码.txt'
            try:
                if os.path.exists(new_products_file):
                    with open(new_products_file, 'r', encoding='utf-8') as f:
                        data['new_products'] = [line.strip() for line in f.readlines() if line.strip()]
                    st.sidebar.success(f"✅ {new_products_file} 加载成功")
                else:
                    # 使用默认新品代码
                    data['new_products'] = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']
                    st.sidebar.info(f"ℹ️ 使用默认新品代码")
            except Exception as e:
                data['new_products'] = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']
                st.sidebar.warning(f"⚠️ 新品代码文件读取失败，使用默认值")

            # 验证和预处理数据
            orders = data['sales_orders']

            if orders.empty:
                st.error("❌ 销售订单数据为空")
                st.stop()

            # 确保销售额列存在
            if '销售额' not in orders.columns:
                if '求和项:金额（元）' in orders.columns:
                    orders['销售额'] = orders['求和项:金额（元）']
                elif '单价（箱）' in orders.columns and '数量（箱）' in orders.columns:
                    orders['销售额'] = orders['单价（箱）'] * orders['数量（箱）']
                elif '求和项:数量（箱）' in orders.columns and '单价（箱）' in orders.columns:
                    orders['销售额'] = orders['单价（箱）'] * orders['求和项:数量（箱）']
                else:
                    st.error("❌ 无法计算销售额，缺少必要的价格或数量字段")
                    st.stop()

            # 数量列处理
            if '数量（箱）' not in orders.columns and '求和项:数量（箱）' in orders.columns:
                orders['数量（箱）'] = orders['求和项:数量（箱）']

            # 确保日期格式正确
            if '发运月份' in orders.columns:
                try:
                    orders['发运月份'] = pd.to_datetime(orders['发运月份'])
                except:
                    st.warning("⚠️ 日期格式转换失败")

            # 添加简化产品名称
            if '产品名称' in orders.columns:
                orders['简化产品名称'] = orders.apply(
                    lambda row: get_simplified_product_name(row.get('产品代码', ''), row.get('产品名称', '')),
                    axis=1
                )
            else:
                orders['简化产品名称'] = orders.get('产品代码', '')

            data['sales_orders'] = orders

            st.sidebar.success(f"✅ 数据预处理完成，订单记录数: {len(orders)}")
            return data

        except Exception as e:
            st.error(f"❌ 数据加载失败: {str(e)}")
            st.stop()


# 筛选器
def create_product_filters(data):
    """创建产品分析专用的筛选器"""
    filtered_data = data.copy()

    if not data or 'sales_orders' not in data or data['sales_orders'].empty:
        st.sidebar.error("❌ 无法加载产品数据")
        return filtered_data

    orders = data['sales_orders'].copy()

    with st.sidebar:
        st.markdown("## 🔍 产品筛选")
        st.markdown("---")

        # 1. 区域筛选
        if '所属区域' in orders.columns:
            all_regions = sorted(['全部'] + list(orders['所属区域'].unique()))
            selected_region = st.selectbox(
                "选择区域", all_regions, index=0, key="product_region_filter"
            )
            if selected_region != '全部':
                orders = orders[orders['所属区域'] == selected_region]

        # 2. 产品类型筛选
        product_type_options = ['全部产品', '仅新品', '仅非新品']
        selected_type = st.selectbox(
            "产品类型", product_type_options, index=0, key="product_type_filter"
        )

        new_products = data.get('new_products', [])
        if selected_type == '仅新品' and new_products:
            orders = orders[orders['产品代码'].isin(new_products)]
        elif selected_type == '仅非新品' and new_products:
            orders = orders[~orders['产品代码'].isin(new_products)]

        # 3. 销售员筛选
        if '申请人' in orders.columns:
            all_sales = sorted(['全部'] + list(orders['申请人'].unique()))
            selected_sales = st.selectbox(
                "销售员", all_sales, index=0, key="product_salesperson_filter"
            )
            if selected_sales != '全部':
                orders = orders[orders['申请人'] == selected_sales]

        # 4. 日期范围筛选
        if '发运月份' in orders.columns:
            try:
                current_year = datetime.now().year
                start_of_year = datetime(current_year, 1, 1)
                end_of_year = datetime(current_year, 12, 31)

                min_date = orders['发运月份'].min().date()
                max_date = orders['发运月份'].max().date()

                default_start = max(start_of_year.date(), min_date)
                default_end = min(end_of_year.date(), max_date)

                st.markdown("### 📅 日期范围")
                start_date = st.date_input(
                    "开始日期", value=default_start, min_value=min_date, max_value=max_date,
                    key="product_start_date"
                )
                end_date = st.date_input(
                    "结束日期", value=default_end, min_value=min_date, max_value=max_date,
                    key="product_end_date"
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
        if st.button("🔄 重置筛选条件", key="reset_product_filters"):
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


# 计算产品关键指标
def calculate_product_kpis(data):
    """计算产品分析的关键指标"""
    kpis = {}

    try:
        orders = data.get('sales_orders', pd.DataFrame())
        new_products = data.get('new_products', [])

        if orders.empty:
            return kpis

        # 1. 总产品数量和销售额
        kpis['total_products'] = orders['产品代码'].nunique()
        kpis['total_sales'] = orders['销售额'].sum()

        # 2. 新品分析
        if new_products:
            new_product_sales = orders[orders['产品代码'].isin(new_products)]['销售额'].sum()
            kpis['new_product_sales'] = new_product_sales
            kpis['new_product_ratio'] = (new_product_sales / kpis['total_sales'] * 100) if kpis[
                                                                                               'total_sales'] > 0 else 0
            kpis['new_product_count'] = orders[orders['产品代码'].isin(new_products)]['产品代码'].nunique()

        # 3. 产品平均销售额
        product_sales = orders.groupby('产品代码')['销售额'].sum()
        kpis['avg_product_sales'] = product_sales.mean()

        # 4. 头部产品贡献（前20%产品的贡献）
        product_sales_sorted = product_sales.sort_values(ascending=False)
        top_20_count = max(1, int(len(product_sales_sorted) * 0.2))
        top_20_sales = product_sales_sorted.head(top_20_count).sum()
        kpis['top_20_contribution'] = (top_20_sales / kpis['total_sales'] * 100) if kpis['total_sales'] > 0 else 0

        return kpis

    except Exception as e:
        st.error(f"计算产品KPI时出错: {str(e)}")
        return {}


# 创建产品销售排行图表
def create_product_ranking_chart(data, top_n=20):
    """创建产品销售额排行图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return None

        # 按产品汇总销售额
        product_sales = orders.groupby(['产品代码', '简化产品名称'])['销售额'].sum().reset_index()
        product_sales = product_sales.sort_values('销售额', ascending=False).head(top_n)

        # 创建图表
        fig = go.Figure()

        # 渐变颜色
        colors = px.colors.sequential.Blues_r
        color_scale = [colors[int(i / (len(product_sales) - 1) * (len(colors) - 1))]
                       for i in range(len(product_sales))]

        # 销售额条形图
        fig.add_trace(go.Bar(
            y=product_sales['简化产品名称'],
            x=product_sales['销售额'],
            marker_color=color_scale,
            orientation='h',
            name='销售额',
            text=product_sales['销售额'].apply(lambda x: format_currency(x)),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>销售额: %{text}<br>产品代码: %{customdata}<extra></extra>',
            customdata=product_sales['产品代码']
        ))

        # 更新布局
        fig.update_layout(
            title="产品销售额排行TOP" + str(top_n),
            xaxis_title="销售额 (元)",
            yaxis_title="产品",
            yaxis=dict(autorange="reversed"),
            height=max(500, len(product_sales) * 25),
            margin=dict(l=200, r=60, t=80, b=60),
            plot_bgcolor='white'
        )

        return fig

    except Exception as e:
        st.error(f"创建产品排行图表失败: {str(e)}")
        return None


# 创建新品分析图表
def create_new_product_analysis_chart(data):
    """创建新品分析图表"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())
        new_products = data.get('new_products', [])

        if orders.empty or not new_products:
            return None

        # 筛选新品数据
        new_product_orders = orders[orders['产品代码'].isin(new_products)]

        if new_product_orders.empty:
            return None

        # 按新品汇总
        new_product_sales = new_product_orders.groupby(['产品代码', '简化产品名称']).agg({
            '销售额': 'sum',
            '数量（箱）': 'sum'
        }).reset_index().sort_values('销售额', ascending=False)

        # 创建饼图
        fig = px.pie(
            new_product_sales,
            values='销售额',
            names='简化产品名称',
            title='新品销售额分布',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(size=12)
        )

        fig.update_layout(
            height=400,
            margin=dict(t=60, b=60, l=60, r=60),
            font=dict(size=14)
        )

        return fig

    except Exception as e:
        st.error(f"创建新品分析图表失败: {str(e)}")
        return None


# 创建简化BCG矩阵
def create_simple_bcg_matrix(data):
    """创建简化的BCG矩阵分析"""
    try:
        orders = data.get('sales_orders', pd.DataFrame())

        if orders.empty:
            return None

        # 按产品汇总销售数据
        product_analysis = orders.groupby(['产品代码', '简化产品名称']).agg({
            '销售额': 'sum',
            '数量（箱）': 'sum'
        }).reset_index()

        if product_analysis.empty:
            return None

        # 计算市场占有率（销售额占比）
        total_sales = product_analysis['销售额'].sum()
        product_analysis['市场占有率'] = product_analysis['销售额'] / total_sales * 100

        # 简化的增长率计算（使用随机数模拟，实际应用中需要真实的历史数据）
        np.random.seed(42)
        product_analysis['市场增长率'] = np.random.normal(15, 20, len(product_analysis))

        # BCG分类
        market_share_threshold = product_analysis['市场占有率'].median()
        growth_rate_threshold = product_analysis['市场增长率'].median()

        def classify_bcg(row):
            if row['市场占有率'] >= market_share_threshold and row['市场增长率'] >= growth_rate_threshold:
                return '明星产品'
            elif row['市场占有率'] >= market_share_threshold and row['市场增长率'] < growth_rate_threshold:
                return '现金牛产品'
            elif row['市场占有率'] < market_share_threshold and row['市场增长率'] >= growth_rate_threshold:
                return '问号产品'
            else:
                return '瘦狗产品'

        product_analysis['BCG分类'] = product_analysis.apply(classify_bcg, axis=1)

        # 创建散点图
        color_map = {
            '明星产品': '#FFD700',
            '现金牛产品': '#4CAF50',
            '问号产品': '#2196F3',
            '瘦狗产品': '#F44336'
        }

        fig = go.Figure()

        for category in product_analysis['BCG分类'].unique():
            category_data = product_analysis[product_analysis['BCG分类'] == category]

            fig.add_trace(go.Scatter(
                x=category_data['市场增长率'],
                y=category_data['市场占有率'],
                mode='markers+text',
                marker=dict(
                    size=category_data['销售额'] / 50000,  # 调整气泡大小
                    color=color_map.get(category, 'blue'),
                    line=dict(width=2, color='white'),
                    sizemode='diameter',
                    sizemin=8,
                    sizemax=50
                ),
                text=category_data['简化产品名称'],
                textposition="middle center",
                textfont=dict(size=10, color='black'),
                name=category,
                hovertemplate='<b>%{text}</b><br>市场增长率: %{x:.1f}%<br>市场占有率: %{y:.2f}%<br>分类: ' + category + '<extra></extra>'
            ))

        # 添加分隔线
        fig.add_vline(x=growth_rate_threshold, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_hline(y=market_share_threshold, line_dash="dash", line_color="gray", opacity=0.7)

        # 添加象限标签
        fig.add_annotation(x=growth_rate_threshold + 10, y=market_share_threshold + 1,
                           text="明星产品", showarrow=False, font=dict(size=14, color='#FFD700'))
        fig.add_annotation(x=growth_rate_threshold - 10, y=market_share_threshold + 1,
                           text="现金牛产品", showarrow=False, font=dict(size=14, color='#4CAF50'))
        fig.add_annotation(x=growth_rate_threshold + 10, y=market_share_threshold - 1,
                           text="问号产品", showarrow=False, font=dict(size=14, color='#2196F3'))
        fig.add_annotation(x=growth_rate_threshold - 10, y=market_share_threshold - 1,
                           text="瘦狗产品", showarrow=False, font=dict(size=14, color='#F44336'))

        fig.update_layout(
            title='产品组合BCG矩阵分析',
            xaxis_title='市场增长率 (%)',
            yaxis_title='市场占有率 (%)',
            height=600,
            plot_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )

        return fig

    except Exception as e:
        st.error(f"创建BCG矩阵失败: {str(e)}")
        return None


# 创建指标卡片
def create_metric_card(header, value, description):
    """创建指标卡片"""
    card_html = f"""
    <div class="metric-card">
        <p class="card-header">{header}</p>
        <p class="card-value">{value}</p>
        <p class="card-text">{description}</p>
    </div>
    """
    return card_html


# 图表解释函数
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# ====== 主程序执行部分 ======

# 加载数据
product_data = load_product_data()

# 应用筛选器
filtered_data = create_product_filters(product_data)

# 标题
st.markdown('<div class="main-header">产品组合分析仪表盘</div>', unsafe_allow_html=True)

# 计算关键指标
kpis = calculate_product_kpis(filtered_data)

# 创建标签页
tab_names = ["📊 产品概览", "🏆 产品排行", "🆕 新品分析", "🔄 BCG矩阵"]
tabs = st.tabs(tab_names)

# 产品概览标签
with tabs[0]:
    # 核心指标卡片
    st.markdown('<div class="section-header">🔑 核心产品指标</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            create_metric_card(
                header="产品总数",
                value=format_number(kpis.get('total_products', 0)),
                description="销售的产品种类数量"
            ),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            create_metric_card(
                header="总销售额",
                value=format_currency(kpis.get('total_sales', 0)),
                description="所有产品的销售总额"
            ),
            unsafe_allow_html=True
        )

    with col3:
        new_ratio = kpis.get('new_product_ratio', 0)
        st.markdown(
            create_metric_card(
                header="新品销售占比",
                value=format_percentage(new_ratio),
                description=f"新品贡献 {format_currency(kpis.get('new_product_sales', 0))}"
            ),
            unsafe_allow_html=True
        )

    with col4:
        top_20_contribution = kpis.get('top_20_contribution', 0)
        st.markdown(
            create_metric_card(
                header="头部产品贡献",
                value=format_percentage(top_20_contribution),
                description="前20%产品的销售贡献"
            ),
            unsafe_allow_html=True
        )

    # 产品销售概况统计表
    if not filtered_data['sales_orders'].empty:
        st.markdown('<div class="section-header">📈 产品销售概况</div>', unsafe_allow_html=True)

        orders = filtered_data['sales_orders']

        # 按产品汇总
        product_summary = orders.groupby(['产品代码', '简化产品名称']).agg({
            '销售额': 'sum',
            '数量（箱）': 'sum',
            '经销商名称': 'nunique'
        }).reset_index()
        product_summary.columns = ['产品代码', '产品名称', '销售额', '销售数量', '客户数']
        product_summary = product_summary.sort_values('销售额', ascending=False)

        # 显示前15个产品
        st.dataframe(product_summary.head(15), use_container_width=True)

# 产品排行标签
with tabs[1]:
    st.markdown('<div class="section-header">🏆 产品销售额排行TOP20</div>', unsafe_allow_html=True)
    ranking_fig = create_product_ranking_chart(filtered_data, 20)
    if ranking_fig:
        st.plotly_chart(ranking_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> 此图展示销售额最高的20个产品及其销售表现。条形图长度表示销售额，
        悬停可查看产品详情。通过此图可快速识别明星产品，优化产品组合策略。
        """)
    else:
        st.warning("⚠️ 无法生成产品排行图表")

# 新品分析标签
with tabs[2]:
    st.markdown('<div class="section-header">🆕 新品分析</div>', unsafe_allow_html=True)

    new_products = filtered_data.get('new_products', [])
    if new_products:
        # 新品概况
        orders = filtered_data['sales_orders']
        new_product_orders = orders[orders['产品代码'].isin(new_products)]

        if not new_product_orders.empty:
            col1, col2 = st.columns(2)

            with col1:
                # 新品销售分布饼图
                new_product_fig = create_new_product_analysis_chart(filtered_data)
                if new_product_fig:
                    st.plotly_chart(new_product_fig, use_container_width=True)

            with col2:
                # 新品详细数据
                new_product_detail = new_product_orders.groupby(['产品代码', '简化产品名称']).agg({
                    '销售额': 'sum',
                    '数量（箱）': 'sum',
                    '经销商名称': 'nunique'
                }).reset_index()
                new_product_detail.columns = ['产品代码', '产品名称', '销售额', '销售数量', '客户数']
                new_product_detail = new_product_detail.sort_values('销售额', ascending=False)

                st.markdown("**新品详细数据**")
                st.dataframe(new_product_detail, use_container_width=True)

            add_chart_explanation("""
            <b>图表解读：</b> 新品分析展示各新品的销售额分布和详细数据。饼图显示新品间的相对表现，
            数据表提供具体的销售额、数量和客户数信息，帮助评估新品推广效果。
            """)
        else:
            st.info("ℹ️ 当前筛选条件下没有新品销售数据")
    else:
        st.info("ℹ️ 没有新品代码数据")

# BCG矩阵标签
with tabs[3]:
    st.markdown('<div class="section-header">🔄 产品组合BCG矩阵</div>', unsafe_allow_html=True)
    bcg_fig = create_simple_bcg_matrix(filtered_data)
    if bcg_fig:
        st.plotly_chart(bcg_fig, use_container_width=True)
        add_chart_explanation("""
        <b>图表解读：</b> BCG矩阵将产品分为四类：明星产品(高增长高份额)、现金牛产品(低增长高份额)、
        问号产品(高增长低份额)、瘦狗产品(低增长低份额)。气泡大小表示销售额，帮助制定产品策略。
        <br><br>
        <b>注意：</b> 由于缺少历史数据，增长率使用模拟数据，实际应用中需要真实的时间序列数据计算。
        """)
    else:
        st.warning("⚠️ 无法生成BCG矩阵")

# 页脚信息
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; margin-top: 2rem;">'
    '产品组合分析仪表盘 | 基于真实数据分析 | 数据更新时间: 每周一17:00'
    '</div>',
    unsafe_allow_html=True
)