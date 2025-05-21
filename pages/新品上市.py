import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
import os
import warnings

warnings.filterwarnings('ignore')

# 在设置页面配置后添加这段代码
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 使用与物料分析类似的样式
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
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown('<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">2025新品销售数据分析仪表盘 | 登录</div>', unsafe_allow_html=True)

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
            if password == 'SAL':
                st.session_state.authenticated = True
                st.success("登录成功！")
                st.rerun()  # 修改这里，使用st.rerun()代替st.experimental_rerun()
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()

# 以下是原有的标题和内容，只有在认证后才会显示
# 删除此处的重复标题，只保留后面的主标题
# st.markdown('<div class="main-header">2025新品销售数据分析仪表盘 </div>', unsafe_allow_html=True)

# 格式化数值的函数
def format_yuan(value):
    if value >= 100000000:  # 亿元级别
        return f"{value / 100000000:.2f}亿元"
    elif value >= 10000:  # 万元级别
        return f"{value / 10000:.2f}万元"
    else:
        return f"{value:.2f}元"


# ==== 工具函数区 ====
def extract_packaging(product_name):
    """从产品名称中提取包装类型"""
    try:
        # 确保输入是字符串
        if not isinstance(product_name, str):
            return "其他"

        # 检查组合类型（优先级最高）
        if re.search(r'分享装袋装', product_name):
            return '分享装袋装'
        elif re.search(r'分享装盒装', product_name):
            return '分享装盒装'

        # 按包装大小分类（从大到小）
        elif re.search(r'随手包', product_name):
            return '随手包'
        elif re.search(r'迷你包', product_name):
            return '迷你包'
        elif re.search(r'分享装', product_name):
            return '分享装'

        # 按包装形式分类
        elif re.search(r'袋装', product_name):
            return '袋装'
        elif re.search(r'盒装', product_name):
            return '盒装'
        elif re.search(r'瓶装', product_name):
            return '瓶装'

        # 处理特殊规格
        kg_match = re.search(r'(\d+(?:\.\d+)?)\s*KG', product_name, re.IGNORECASE)
        if kg_match:
            weight = float(kg_match.group(1))
            if weight >= 1.5:
                return '大包装'
            return '散装'

        g_match = re.search(r'(\d+(?:\.\d+)?)\s*G', product_name)
        if g_match:
            weight = float(g_match.group(1))
            if weight <= 50:
                return '小包装'
            elif weight <= 100:
                return '中包装'
            else:
                return '大包装'

        # 默认分类
        return '其他'
    except Exception as e:
        print(f"提取包装类型时出错: {str(e)}, 产品名称: {product_name}")
        return '其他'  # 捕获任何异常并返回默认值


# 创建产品代码到简化产品名称的映射函数
def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称"""
    try:
        # 确保输入是字符串类型
        if not isinstance(product_name, str):
            return str(product_code)  # 返回产品代码作为备选

        if '口力' in product_name:
            # 提取"口力"之后的产品类型
            name_parts = product_name.split('口力')
            if len(name_parts) > 1:
                name_part = name_parts[1]
                if '-' in name_part:
                    name_part = name_part.split('-')[0].strip()

                # 进一步简化，只保留主要部分（去掉规格和包装形式）
                for suffix in ['G分享装袋装', 'G盒装', 'G袋装', 'KG迷你包', 'KG随手包']:
                    if suffix in name_part:
                        name_part = name_part.split(suffix)[0]
                        break

                # 去掉可能的数字和单位
                simple_name = re.sub(r'\d+\w*\s*', '', name_part).strip()

                if simple_name:  # 确保简化名称不为空
                    return f"{simple_name} ({product_code})"

        # 如果无法提取或处理中出现错误，则返回产品代码
        return str(product_code)
    except Exception as e:
        # 捕获任何异常，确保函数始终返回一个字符串
        print(f"简化产品名称时出错: {e}，产品代码: {product_code}")
        return str(product_code)


# ==== 数据加载函数 ====
@st.cache_data
def load_data(file_path=None):
    """从文件加载数据或使用示例数据"""
    # 如果提供了文件路径，从文件加载
    if file_path and os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)

            # 数据预处理
            # 确保所有必要的列都存在
            required_columns = ['客户简称', '所属区域', '发运月份', '申请人', '产品代码', '产品名称',
                                '订单类型', '单价（箱）', '数量（箱）']

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
                return load_sample_data()

            # 计算销售额
            df['销售额'] = df['单价（箱）'] * df['数量（箱）']

            # 确保发运月份是日期类型
            try:
                df['发运月份'] = pd.to_datetime(df['发运月份'])
            except Exception as e:
                st.warning(f"转换日期格式时出错: {str(e)}。月份分析功能可能受影响。")

            # 确保所有的字符串列都是字符串类型
            for col in ['客户简称', '所属区域', '申请人', '产品代码', '产品名称', '订单类型']:
                df[col] = df[col].astype(str)

            # 添加简化产品名称列
            df['简化产品名称'] = df.apply(
                lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
                axis=1
            )

            # 在这里一次性提取包装类型
            df['包装类型'] = df['产品名称'].apply(extract_packaging)

            return df
        except Exception as e:
            st.error(f"文件加载失败: {str(e)}。使用示例数据进行演示。")
            return load_sample_data()
    else:
        # 没有文件路径或文件不存在，使用示例数据
        if file_path:
            st.warning(f"文件路径不存在: {file_path}。使用示例数据进行演示。")
        return load_sample_data()


# 创建示例数据（以防用户没有上传文件）
@st.cache_data
def load_sample_data():
    """创建示例数据"""
    # 产品代码
    product_codes = [
        'F3415D', 'F3421D', 'F0104J', 'F0104L', 'F3411A', 'F01E4B',
        'F01L4C', 'F01C2P', 'F01E6D', 'F3450B', 'F3415B', 'F0110C',
        'F0183F', 'F01K8A', 'F0183K', 'F0101P'
    ]

    # 产品名称，确保与产品代码数量一致
    product_names = [
        '口力酸小虫250G分享装袋装-中国', '口力可乐瓶250G分享装袋装-中国',
        '口力比萨XXL45G盒装-中国', '口力比萨68G袋装-中国', '口力午餐袋77G袋装-中国',
        '口力汉堡108G袋装-中国', '口力扭扭虫2KG迷你包-中国', '口力字节软糖2KG迷你包-中国',
        '口力西瓜1.5KG随手包-中国', '口力七彩熊1.5KG随手包-中国',
        '口力软糖新品A-中国', '口力软糖新品B-中国', '口力软糖新品C-中国', '口力软糖新品D-中国',
        '口力软糖新品E-中国', '口力软糖新品F-中国'
    ]

    # 客户简称
    customers = ['广州佳成行', '广州佳成行', '广州佳成行', '广州佳成行', '广州佳成行',
                 '广州佳成行', '河南甜丰號', '河南甜丰號', '河南甜丰號', '河南甜丰號',
                 '河南甜丰號', '广州佳成行', '河南甜丰號', '广州佳成行', '河南甜丰號',
                 '广州佳成行']

    try:
        # 创建示例数据
        data = {
            '客户简称': customers,
            '所属区域': ['东', '东', '东', '东', '东', '东', '中', '中', '中', '中', '中',
                         '南', '中', '北', '北', '西'],
            '发运月份': ['2025-03', '2025-03', '2025-03', '2025-03', '2025-03', '2025-03',
                         '2025-03', '2025-03', '2025-03', '2025-03', '2025-03', '2025-03',
                         '2025-03', '2025-03', '2025-03', '2025-03'],
            '申请人': ['梁洪泽', '梁洪泽', '梁洪泽', '梁洪泽', '梁洪泽', '梁洪泽',
                       '胡斌', '胡斌', '胡斌', '胡斌', '胡斌', '梁洪泽', '胡斌', '梁洪泽',
                       '胡斌', '梁洪泽'],
            '产品代码': product_codes,
            '产品名称': product_names,
            '订单类型': ['订单-正常产品'] * 16,
            '单价（箱）': [121.44, 121.44, 216.96, 126.72, 137.04, 137.04, 127.2, 127.2,
                         180, 180, 180, 150, 160, 170, 180, 190],
            '数量（箱）': [10, 10, 20, 50, 252, 204, 7, 2, 6, 6, 6, 30, 20, 15, 10, 5]
        }

        # 创建DataFrame
        df = pd.DataFrame(data)

        # 计算销售额
        df['销售额'] = df['单价（箱）'] * df['数量（箱）']

        # 增加销售额的变化性
        region_factors = {'东': 5.2, '南': 3.8, '中': 0.9, '北': 1.6, '西': 1.3}

        # 应用区域因子
        for region, factor in region_factors.items():
            mask = df['所属区域'] == region
            df.loc[mask, '销售额'] = df.loc[mask, '销售额'] * factor

        # 添加简化产品名称
        df['简化产品名称'] = df.apply(
            lambda row: get_simplified_product_name(row['产品代码'], row['产品名称']),
            axis=1
        )

        # 添加包装类型
        df['包装类型'] = df['产品名称'].apply(extract_packaging)

        return df
    except Exception as e:
        # 如果示例数据创建失败，创建一个最小化的DataFrame
        st.error(f"创建示例数据时出错: {str(e)}。使用简化版示例数据。")

        # 创建最简单的数据集
        simple_df = pd.DataFrame({
            '客户简称': ['示例客户A', '示例客户B', '示例客户C'],
            '所属区域': ['东', '南', '中'],
            '发运月份': ['2025-03', '2025-03', '2025-03'],
            '申请人': ['示例申请人A', '示例申请人B', '示例申请人C'],
            '产品代码': ['X001', 'X002', 'X003'],
            '产品名称': ['示例产品A', '示例产品B', '示例产品C'],
            '订单类型': ['订单-正常产品'] * 3,
            '单价（箱）': [100, 150, 200],
            '数量（箱）': [10, 15, 20],
            '销售额': [1000, 2250, 4000],
            '简化产品名称': ['产品A (X001)', '产品B (X002)', '产品C (X003)'],
            '包装类型': ['盒装', '袋装', '盒装']
        })

        return simple_df


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 定义默认文件路径
DEFAULT_FILE_PATH = "Q1xlsx.xlsx"

# 标题
st.markdown('<div class="main-header">2025新品销售数据分析仪表盘</div>', unsafe_allow_html=True)

# 侧边栏 - 上传文件区域
st.sidebar.header("📂 数据导入")
use_default_file = st.sidebar.checkbox("使用默认文件", value=True, help="使用指定的本地文件路径")
uploaded_file = st.sidebar.file_uploader("或上传Excel销售数据文件", type=["xlsx", "xls"], disabled=use_default_file)

# 加载数据
if use_default_file:
    # 使用默认文件路径
    if os.path.exists(DEFAULT_FILE_PATH):
        df = load_data(DEFAULT_FILE_PATH)
        st.sidebar.success(f"已成功加载默认文件: {DEFAULT_FILE_PATH}")
    else:
        st.sidebar.error(f"默认文件路径不存在: {DEFAULT_FILE_PATH}")
        df = load_sample_data()
        st.sidebar.info("正在使用示例数据。请上传您的数据文件获取真实分析。")
elif uploaded_file is not None:
    # 使用上传的文件
    df = load_data(uploaded_file)
else:
    # 没有文件，使用示例数据
    df = load_sample_data()
    st.sidebar.info("正在使用示例数据。请上传您的数据文件获取真实分析。")

# 定义新品产品代码
new_products = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']
new_products_df = df[df['产品代码'].isin(new_products)]

# 创建产品代码到简化名称的映射字典（用于图表显示）
product_name_mapping = {
    code: df[df['产品代码'] == code]['简化产品名称'].iloc[0] if len(df[df['产品代码'] == code]) > 0 else code
    for code in df['产品代码'].unique()
}

# 侧边栏 - 筛选器
st.sidebar.header("🔍 筛选数据")

# 区域筛选器
all_regions = sorted(df['所属区域'].astype(str).unique())
selected_regions = st.sidebar.multiselect("选择区域", all_regions, default=all_regions)

# 客户筛选器
all_customers = sorted(df['客户简称'].astype(str).unique())
selected_customers = st.sidebar.multiselect("选择客户", all_customers, default=[])

# 产品代码筛选器
all_products = sorted(df['产品代码'].astype(str).unique())
selected_products = st.sidebar.multiselect(
    "选择产品",
    options=all_products,
    format_func=lambda x: f"{x} ({product_name_mapping[x]})",
    default=[]
)

# 申请人筛选器
all_applicants = sorted(df['申请人'].astype(str).unique())
selected_applicants = st.sidebar.multiselect("选择申请人", all_applicants, default=[])

# 应用筛选条件
filtered_df = df.copy()

if selected_regions:
    filtered_df = filtered_df[filtered_df['所属区域'].isin(selected_regions)]

if selected_customers:
    filtered_df = filtered_df[filtered_df['客户简称'].isin(selected_customers)]

if selected_products:
    filtered_df = filtered_df[filtered_df['产品代码'].isin(selected_products)]

if selected_applicants:
    filtered_df = filtered_df[filtered_df['申请人'].isin(selected_applicants)]

# 根据筛选后的数据筛选新品数据
filtered_new_products_df = filtered_df[filtered_df['产品代码'].isin(new_products)]

# 创建标签页
tabs = st.tabs(["📊 销售概览", "🆕 新品分析", "👥 客户细分", "🔄 产品组合", "🌐 市场渗透率"])

with tabs[0]:  # 销售概览
    # KPI指标行
    st.subheader("🔑 关键绩效指标")
    col1, col2, col3, col4 = st.columns(4)

    # 总销售额
    total_sales = filtered_df['销售额'].sum()
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总销售额</p>
            <p class="card-value">{format_yuan(total_sales)}</p>
            <p class="card-text">全部销售收入</p>
        </div>
        """, unsafe_allow_html=True)

    # 客户数量
    total_customers = filtered_df['客户简称'].nunique()
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">客户数量</p>
            <p class="card-value">{total_customers}</p>
            <p class="card-text">服务客户总数</p>
        </div>
        """, unsafe_allow_html=True)

    # 产品数量
    total_products = filtered_df['产品代码'].nunique()
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">产品数量</p>
            <p class="card-value">{total_products}</p>
            <p class="card-text">销售产品总数</p>
        </div>
        """, unsafe_allow_html=True)

    # 平均单价
    avg_price = filtered_df['单价（箱）'].mean()
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均单价</p>
            <p class="card-value">￥{avg_price:.2f}</p>
            <p class="card-text">每箱平均价格</p>
        </div>
        """, unsafe_allow_html=True)

    # 区域销售分析
    st.markdown('<div class="sub-header">📊 区域销售分析</div>', unsafe_allow_html=True)

    # 计算区域销售数据
    region_sales = filtered_df.groupby('所属区域')['销售额'].sum().reset_index()
    region_sales = region_sales.sort_values(by='销售额', ascending=False)

    # 创建区域销售图表
    cols = st.columns(2)
    with cols[0]:
        # 区域销售柱状图
        fig_region_bar = px.bar(
            region_sales,
            x='所属区域',
            y='销售额',
            title="各区域销售总额",
            color='所属区域',
            text='销售额'
        )
        fig_region_bar.update_traces(
            texttemplate='￥%{text:,.2f}',
            textposition='outside'
        )
        fig_region_bar.update_layout(
            xaxis_title="区域",
            yaxis_title="销售总额 (元)",
            yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元")
        )
        st.plotly_chart(fig_region_bar, use_container_width=True)

    with cols[1]:
        # 区域销售占比饼图
        fig_region_pie = px.pie(
            region_sales,
            values='销售额',
            names='所属区域',
            title='各区域销售占比'
        )
        fig_region_pie.update_traces(
            textinfo='percent+label',
            hovertemplate='%{label}: %{value:,.2f}元 (%{percent})'
        )
        st.plotly_chart(fig_region_pie, use_container_width=True)

    # 添加图表解释
    add_chart_explanation("""
    <b>图表解读：</b> 左图展示各区域销售额数值对比，右图展示各区域在总销售中的占比。柱子/扇形越大表示销售额/占比越高。
    从图表可以看出，销售分布在区域间存在显著差异，可能与区域市场规模、消费习惯或销售资源配置有关。
    <b>行动建议：</b> 重点关注销售占比最大的区域，分析其成功因素；针对销售额较低的区域，考虑增加资源投入或开展针对性营销活动。
    """)

    # 产品销售分析
    st.markdown('<div class="sub-header">📦 产品销售与包装分析</div>', unsafe_allow_html=True)

    # 提取包装类型数据
    packaging_sales = filtered_df.groupby('包装类型')['销售额'].sum().reset_index()
    packaging_sales = packaging_sales.sort_values(by='销售额', ascending=False)

    cols = st.columns(2)
    with cols[0]:
        # 包装类型销售柱状图
        fig_packaging = px.bar(
            packaging_sales,
            x='包装类型',
            y='销售额',
            title="不同包装类型销售额",
            color='包装类型',
            text='销售额'
        )
        fig_packaging.update_traces(
            texttemplate='￥%{text:,.2f}',
            textposition='outside'
        )
        fig_packaging.update_layout(
            xaxis_title="包装类型",
            yaxis_title="销售额 (元)",
            yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元")
        )
        st.plotly_chart(fig_packaging, use_container_width=True)

    with cols[1]:
        # 产品价格-销量散点图
        fig_price_volume = px.scatter(
            filtered_df,
            x='单价（箱）',
            y='数量（箱）',
            color='所属区域',
            size='销售额',
            hover_name='简化产品名称',
            title="产品价格-销量关系",
            size_max=50
        )
        fig_price_volume.update_layout(
            xaxis_title="单价 (元/箱)",
            yaxis_title="销售数量 (箱)",
            xaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元")
        )
        st.plotly_chart(fig_price_volume, use_container_width=True)

    # 添加图表解释
    add_chart_explanation("""
    <b>图表解读：</b> 左图展示不同包装类型产品的销售额对比，右图展示产品价格与销量的关系，气泡大小代表销售额，颜色代表销售区域。
    分析显示特定包装类型更受欢迎，价格与销量之间存在一定的负相关关系，但因区域差异而有所不同。
    <b>行动建议：</b> 重点投资生产和推广热销包装类型产品；对价格敏感型市场适当调整价格策略；针对高价产品销量好的区域，加大高利润产品的营销力度。
    """)

    # 申请人销售业绩分析
    st.markdown('<div class="sub-header">👨‍💼 申请人销售业绩分析</div>', unsafe_allow_html=True)

    # 计算申请人业绩数据
    applicant_performance = filtered_df.groupby('申请人').agg({
        '销售额': 'sum',
        '客户简称': pd.Series.nunique,
        '产品代码': pd.Series.nunique
    }).reset_index()

    applicant_performance.columns = ['申请人', '销售额', '服务客户数', '销售产品种类数']
    applicant_performance = applicant_performance.sort_values('销售额', ascending=False)

    cols = st.columns(2)
    with cols[0]:
        # 申请人销售额排名
        fig_applicant_sales = px.bar(
            applicant_performance,
            x='申请人',
            y='销售额',
            title="申请人销售额排名",
            color_discrete_sequence=['royalblue'],  # 使用固定颜色而不是渐变
            text='销售额'
        )
        fig_applicant_sales.update_traces(
            texttemplate='￥%{text:,.2f}',
            textposition='outside'
        )
        fig_applicant_sales.update_layout(
            xaxis_title="申请人",
            yaxis_title="销售额 (元)",
            yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元"),
        )
        st.plotly_chart(fig_applicant_sales, use_container_width=True)

    with cols[1]:
        # 客户与产品覆盖情况
        fig_applicant_coverage = go.Figure()

        # 服务客户数柱状图
        fig_applicant_coverage.add_trace(go.Bar(
            x=applicant_performance['申请人'],
            y=applicant_performance['服务客户数'],
            name='服务客户数',
            marker_color='royalblue',
            text=applicant_performance['服务客户数'],
            textposition='outside'
        ))

        # 销售产品种类数柱状图
        fig_applicant_coverage.add_trace(go.Bar(
            x=applicant_performance['申请人'],
            y=applicant_performance['销售产品种类数'],
            name='销售产品种类数',
            marker_color='lightcoral',
            text=applicant_performance['销售产品种类数'],
            textposition='outside'
        ))

        fig_applicant_coverage.update_layout(
            title="客户与产品覆盖情况",
            xaxis_title="申请人",
            yaxis_title="数量",
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_applicant_coverage, use_container_width=True)

    # 添加图表解释
    add_chart_explanation("""
    <b>图表解读：</b> 左图展示各申请人的销售额排名，右图对比每位申请人覆盖的客户数量（蓝色）和销售的产品种类数（红色）。
    分析表明销售业绩优秀的申请人通常拥有更广泛的客户覆盖或更多样化的产品组合。部分申请人专注于高价值客户，尽管客户数量少但销售额高。
    <b>行动建议：</b> 向顶尖业绩申请人学习成功经验并在团队内分享；针对客户数多但销售额低的申请人，提供客户价值提升培训；鼓励产品多样化销售。
    """)

    # 原始数据表
    with st.expander("查看筛选后的原始数据"):
        st.dataframe(filtered_df)

with tabs[1]:  # 新品分析
    st.markdown('<div class="sub-header">🆕 新品销售分析</div>', unsafe_allow_html=True)

    # 新品KPI指标
    col1, col2, col3 = st.columns(3)

    # 新品销售额
    new_products_sales = filtered_new_products_df['销售额'].sum()
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">新品销售额</p>
            <p class="card-value">{format_yuan(new_products_sales)}</p>
            <p class="card-text">新品产生的销售额</p>
        </div>
        """, unsafe_allow_html=True)

    # 新品销售占比
    new_products_percentage = (new_products_sales / total_sales * 100) if total_sales > 0 else 0
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">新品销售占比</p>
            <p class="card-value">{new_products_percentage:.2f}%</p>
            <p class="card-text">新品占总销售额比例</p>
        </div>
        """, unsafe_allow_html=True)

    # 购买新品的客户数
    new_products_customers = filtered_new_products_df['客户简称'].nunique()
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">购买新品的客户数</p>
            <p class="card-value">{new_products_customers}</p>
            <p class="card-text">尝试新品的客户数量</p>
        </div>
        """, unsafe_allow_html=True)

    # 新品销售详情
    st.markdown('<div class="sub-header">新品销售表现分析</div>', unsafe_allow_html=True)

    if not filtered_new_products_df.empty:
        # 创建新品销售分析图表
        cols = st.columns(2)

        with cols[0]:
            # 各新品销售额对比
            product_sales = filtered_new_products_df.groupby(['产品代码', '简化产品名称'])['销售额'].sum().reset_index()
            product_sales = product_sales.sort_values('销售额', ascending=False)

            fig_product_sales = px.bar(
                product_sales,
                x='简化产品名称',
                y='销售额',
                title="各新品销售额对比",
                color='简化产品名称',
                text='销售额'
            )
            fig_product_sales.update_traces(
                texttemplate='￥%{text:,.2f}',
                textposition='outside'
            )
            fig_product_sales.update_layout(
                xaxis_title="新品名称",
                yaxis_title="销售额 (元)",
                yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元"),
                showlegend=False
            )
            st.plotly_chart(fig_product_sales, use_container_width=True)

        with cols[1]:
            # 各区域新品销售额
            region_product_sales = filtered_new_products_df.groupby(['所属区域', '简化产品名称'])[
                '销售额'].sum().reset_index()

            fig_region_product = px.bar(
                region_product_sales,
                x='所属区域',
                y='销售额',
                color='简化产品名称',
                title="各区域新品销售额",
                barmode='stack'
            )
            fig_region_product.update_layout(
                xaxis_title="区域",
                yaxis_title="销售额 (元)",
                yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元"),
                legend_title="新品名称"
            )
            st.plotly_chart(fig_region_product, use_container_width=True)

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 左图展示各新品销售额对比，右图展示不同区域对各新品的接受情况，堆叠柱状图显示了各区域对不同新品的销售额贡献。
        分析发现新品间存在明显的销售差异，不同区域对新品有不同的偏好。部分新品在特定区域表现突出。
        <b>行动建议：</b> 针对表现最佳的新品加大生产和营销投入；针对表现不佳的新品，分析原因并调整策略；根据区域偏好，制定差异化的新品推广策略。
        """)

        # 新品销售占比分析
        st.markdown('<div class="sub-header">新品销售占比分析</div>', unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            # 新品与非新品销售占比饼图
            fig_sales_ratio = px.pie(
                names=['新品', '非新品'],
                values=[new_products_sales, total_sales - new_products_sales],
                title="新品与非新品销售占比"
            )
            fig_sales_ratio.update_traces(
                textinfo='percent+label',
                hovertemplate='%{label}: %{value:,.2f}元 (%{percent})'
            )
            st.plotly_chart(fig_sales_ratio, use_container_width=True)

        with cols[1]:
            # 各区域新品销售占比
            region_total_sales = filtered_df.groupby('所属区域')['销售额'].sum().reset_index()
            region_new_sales = filtered_new_products_df.groupby('所属区域')['销售额'].sum().reset_index()

            region_sales_ratio = pd.merge(region_total_sales, region_new_sales, on='所属区域', how='left',
                                          suffixes=('_total', '_new'))
            region_sales_ratio['new_ratio'] = region_sales_ratio['销售额_new'].fillna(0) / region_sales_ratio[
                '销售额_total'] * 100
            region_sales_ratio = region_sales_ratio.sort_values('new_ratio', ascending=False)

            fig_region_ratio = px.bar(
                region_sales_ratio,
                x='所属区域',
                y='new_ratio',
                title="各区域新品销售占比",
                color='所属区域',
                text='new_ratio'
            )
            fig_region_ratio.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside'
            )
            fig_region_ratio.update_layout(
                xaxis_title="区域",
                yaxis_title="新品销售占比 (%)",
                showlegend=False
            )
            st.plotly_chart(fig_region_ratio, use_container_width=True)

        # 添加图表解释
        add_chart_explanation(f"""
        <b>图表解读：</b> 左图展示新品销售在总销售中的占比，右图展示各区域的新品销售占比情况。
        从数据可见新品总体占比为{new_products_percentage:.2f}%，各区域对新品的接受度不同。这种差异可能来自区域市场特性、推广力度或消费习惯。
        <b>行动建议：</b> 评估新品占比是否达到预期目标；分析新品接受度高的区域成功经验；针对新品占比低的区域，制定强化培训和营销方案。
        """)
    else:
        st.warning("当前筛选条件下没有新品数据。请调整筛选条件或确认数据中包含新品。")

    # 新品数据表
    with st.expander("查看新品销售数据"):
        if not filtered_new_products_df.empty:
            st.dataframe(filtered_new_products_df)
        else:
            st.info("当前筛选条件下没有新品数据。")

with tabs[2]:  # 客户细分
    st.markdown('<div class="sub-header">👥 客户细分分析</div>', unsafe_allow_html=True)

    if not filtered_df.empty:
        # 计算客户特征
        customer_features = filtered_df.groupby('客户简称').agg({
            '销售额': 'sum',  # 总销售额
            '产品代码': lambda x: len(set(x)),  # 购买的不同产品数量
            '数量（箱）': 'sum',  # 总购买数量
            '单价（箱）': 'mean'  # 平均单价
        }).reset_index()

        # 添加新品购买指标
        new_products_by_customer = filtered_new_products_df.groupby('客户简称')['销售额'].sum().reset_index()
        customer_features = customer_features.merge(new_products_by_customer, on='客户简称', how='left',
                                                    suffixes=('', '_新品'))
        customer_features['销售额_新品'] = customer_features['销售额_新品'].fillna(0)
        customer_features['新品占比'] = customer_features['销售额_新品'] / customer_features['销售额'] * 100

        # 简单客户分类
        customer_features['客户类型'] = pd.cut(
            customer_features['新品占比'],
            bins=[0, 10, 30, 100],
            labels=['保守型客户', '平衡型客户', '创新型客户']
        )

        # 添加客户类型解释
        st.markdown("""
        ### 客户类型分类标准
        - **保守型客户**：新品销售占比在0-10%之间，对新品接受度较低，倾向于购买成熟稳定的产品。
        - **平衡型客户**：新品销售占比在10-30%之间，对新品有一定接受度，同时保持对现有产品的购买。
        - **创新型客户**：新品销售占比在30-100%之间，积极尝试新品，是推广新产品的重要客户群体。
        """)

        # 客户分类概览
        st.markdown('<div class="sub-header">客户类型分布与特征分析</div>', unsafe_allow_html=True)

        # 计算客户类型统计数据
        customer_segments = customer_features.groupby('客户类型').agg({
            '客户简称': 'count',
            '销售额': 'mean',
            '新品占比': 'mean'
        }).reset_index()

        customer_segments.columns = ['客户类型', '客户数量', '平均销售额', '平均新品占比']

        # 创建客户类型分析图表
        cols = st.columns(2)

        with cols[0]:
            # 客户类型分布
            fig_customer_dist = px.bar(
                customer_segments,
                x='客户类型',
                y='客户数量',
                title="客户类型分布",
                color='客户类型',
                text='客户数量'
            )
            fig_customer_dist.update_traces(
                textposition='outside'
            )
            fig_customer_dist.update_layout(
                xaxis_title="客户类型",
                yaxis_title="客户数量",
                showlegend=False
            )
            st.plotly_chart(fig_customer_dist, use_container_width=True)

        with cols[1]:
            # 客户类型特征对比
            fig_customer_features = make_subplots(specs=[[{"secondary_y": True}]])

            # 平均销售额柱状图
            fig_customer_features.add_trace(
                go.Bar(
                    x=customer_segments['客户类型'],
                    y=customer_segments['平均销售额'],
                    name='平均销售额',
                    marker_color='royalblue',
                    text=[f"￥{val:,.2f}" for val in customer_segments['平均销售额']],
                    textposition='outside'
                ),
                secondary_y=False
            )

            # 平均新品占比线图
            fig_customer_features.add_trace(
                go.Scatter(
                    x=customer_segments['客户类型'],
                    y=customer_segments['平均新品占比'],
                    name='平均新品占比',
                    mode='lines+markers+text',
                    line=dict(color='red', width=2),
                    marker=dict(size=10),
                    text=[f"{val:.2f}%" for val in customer_segments['平均新品占比']],
                    textposition='top center'
                ),
                secondary_y=True
            )

            fig_customer_features.update_layout(
                title="客户类型特征对比",
                xaxis_title="客户类型",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            # 更新Y轴
            fig_customer_features.update_yaxes(
                title_text="平均销售额 (元)",
                secondary_y=False,
                tickprefix="￥",
                tickformat=",.2f"
            )
            fig_customer_features.update_yaxes(
                title_text="平均新品占比 (%)",
                secondary_y=True
            )

            st.plotly_chart(fig_customer_features, use_container_width=True)

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 左图展示三种客户类型的分布情况，右图对比各类客户的平均销售额（柱状图）和平均新品占比（折线图）。
        客户类型分布反映了市场对新品的总体接受度，不同类型客户的平均销售额差异显示了创新性与购买力的关系。
        <b>行动建议：</b> 针对保守型客户群，开发渐进式的新品尝试激励方案；对平衡型客户，强化新品与经典产品的组合推荐；重视创新型客户的尝鲜行为。
        """)

        # 客户销售额和新品占比散点图
        st.markdown('<div class="sub-header">客户销售额与新品占比关系</div>', unsafe_allow_html=True)

        fig_customer_scatter = px.scatter(
            customer_features,
            x='销售额',
            y='新品占比',
            color='客户类型',
            size='产品代码',  # 购买的产品种类数量
            hover_name='客户简称',
            title='客户销售额与新品占比关系',
            labels={
                '销售额': '销售额 (元)',
                '新品占比': '新品销售占比 (%)',
                '产品代码': '购买产品种类数',
                '客户类型': '客户类型'
            },
            color_discrete_map={
                '保守型客户': 'blue',
                '平衡型客户': 'orange',
                '创新型客户': 'red'
            }
        )

        # 添加分隔线
        fig_customer_scatter.add_shape(
            type="line",
            x0=customer_features['销售额'].min(),
            x1=customer_features['销售额'].max(),
            y0=10, y1=10,
            line=dict(color="orange", width=1, dash="dash")
        )

        fig_customer_scatter.add_shape(
            type="line",
            x0=customer_features['销售额'].min(),
            x1=customer_features['销售额'].max(),
            y0=30, y1=30,
            line=dict(color="red", width=1, dash="dash")
        )

        fig_customer_scatter.update_layout(
            xaxis=dict(
                title="销售额 (元)",
                tickprefix="￥",
                tickformat=",.0f",  # 使用,.0f格式而不是默认的格式
                ticksuffix=" 元"  # 明确指定后缀为" 元"
            ),
            yaxis=dict(
                title="新品销售占比 (%)",
                range=[0, 100]
            )
        )

        st.plotly_chart(fig_customer_scatter, use_container_width=True)

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 此散点图展示了客户销售额与新品占比之间的关系，气泡大小表示购买的产品种类数量，颜色表示客户类型。虚线区分了不同客户类型的区域。
        分析发现高销售额客户分布在不同的新品接受度区间，部分高销售额客户展现出较高的新品接受度。购买产品种类数与新品占比有一定关联性。
        <b>行动建议：</b> 识别右上方的高价值创新型客户优先推广新品；关注右下方的高价值保守型客户设计专门的渐进式新品导入方案；对中间区域的平衡型客户通过组合销售提升新品比例。
        """)

        # 新品接受度最高的客户
        st.markdown('<div class="sub-header">新品接受度最高的客户</div>', unsafe_allow_html=True)

        # 选取新品占比最高的前10名客户
        top_acceptance = customer_features.sort_values('新品占比', ascending=False).head(10)

        fig_top_acceptance = px.bar(
            top_acceptance,
            x='客户简称',
            y='新品占比',
            title='新品接受度最高的前10名客户',
            color='新品占比',
            text='新品占比',
            hover_data=['销售额', '销售额_新品']
        )
        fig_top_acceptance.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )
        fig_top_acceptance.update_layout(
            xaxis_title="客户",
            yaxis_title="新品销售占比 (%)",
            coloraxis_showscale=False
        )

        # 添加参考线
        fig_top_acceptance.add_shape(
            type="line",
            x0=-0.5,
            x1=len(top_acceptance) - 0.5,
            y0=30,
            y1=30,
            line=dict(color="red", width=1, dash="dash")
        )

        st.plotly_chart(fig_top_acceptance, use_container_width=True)

        # 添加图表解释
        add_chart_explanation("""
        <b>图表解读：</b> 此图表展示新品接受度最高的10名客户，按新品销售占比降序排列。虚线表示创新型客户的标准线(30%)。
        这些客户新品占比明显高于平均水平，是新品推广的关键客户群体。部分客户新品占比接近或超过50%，表明对新品有极强的接受意愿。
        <b>行动建议：</b> 将这些高接受度客户作为新品首发测试的目标群体；深入调研这些客户的购买动机和满意度反馈；开发专属VIP新品尝鲜计划增强忠诚度。
        """)

        # 客户表格
        with st.expander("查看客户细分数据表格"):
            display_columns = ['客户简称', '客户类型', '销售额', '销售额_新品', '新品占比', '产品代码', '数量（箱）',
                               '单价（箱）']
            display_df = customer_features[display_columns].copy()
            # 格式化数值列
            display_df['销售额'] = display_df['销售额'].apply(lambda x: f"¥{x:,.2f}")
            display_df['销售额_新品'] = display_df['销售额_新品'].apply(lambda x: f"¥{x:,.2f}")
            display_df['新品占比'] = display_df['新品占比'].apply(lambda x: f"{x:.2f}%")
            display_df['单价（箱）'] = display_df['单价（箱）'].apply(lambda x: f"¥{x:.2f}")

            # 重命名列以便更好显示
            display_df.columns = ['客户简称', '客户类型', '总销售额', '新品销售额', '新品占比',
                                  '购买产品种类数', '总购买数量(箱)', '平均单价(元/箱)']

            st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("当前筛选条件下没有客户数据。请调整筛选条件。")

with tabs[3]:  # 产品组合
    st.markdown('<div class="sub-header">🔄 产品组合分析</div>', unsafe_allow_html=True)

    if not filtered_df.empty and len(filtered_df['客户简称'].unique()) > 1 and len(
            filtered_df['产品代码'].unique()) > 1:
        # 共现矩阵分析介绍
        st.markdown("""
        ### 共现分析说明
        共现分析展示了不同产品被同一客户一起购买的频率，有助于发现产品间的关联性和互补关系。
        这一分析对于产品组合营销、交叉销售和货架陈列优化具有重要指导意义。
        """)

        # 准备数据 - 创建交易矩阵
        transaction_data = filtered_df.groupby(['客户简称', '产品代码'])['销售额'].sum().unstack().fillna(0)
        # 转换为二进制格式（是否购买）
        transaction_binary = transaction_data.applymap(lambda x: 1 if x > 0 else 0)

        # 创建产品共现矩阵
        co_occurrence = pd.DataFrame(0, index=transaction_binary.columns, columns=transaction_binary.columns)

        # 创建产品代码到简化名称的映射
        name_mapping = {
            code: filtered_df[filtered_df['产品代码'] == code]['简化产品名称'].iloc[0]
            if len(filtered_df[filtered_df['产品代码'] == code]) > 0 else code
            for code in transaction_binary.columns
        }

        # 计算共现次数
        for _, row in transaction_binary.iterrows():
            bought_products = row.index[row == 1].tolist()
            for p1 in bought_products:
                for p2 in bought_products:
                    if p1 != p2:
                        co_occurrence.loc[p1, p2] += 1

        # 筛选新品的共现情况
        valid_new_products = [p for p in new_products if p in co_occurrence.index]

        # 新品产品共现分析
        if valid_new_products:
            st.markdown('<div class="sub-header">新品产品共现分析</div>', unsafe_allow_html=True)

            # 创建整合后的共现数据
            top_co_products = []
            for np_code in valid_new_products:
                np_name = name_mapping.get(np_code, np_code)
                top_co = co_occurrence.loc[np_code].sort_values(ascending=False).head(5)
                for product_code, count in top_co.items():
                    if count > 0 and product_code not in valid_new_products:  # 只添加有共现且非新品的产品
                        top_co_products.append({
                            '新品代码': np_code,
                            '新品名称': np_name,
                            '共现产品代码': product_code,
                            '共现产品名称': name_mapping.get(product_code, product_code),
                            '共现次数': count
                        })

            # 转换为DataFrame
            co_df = pd.DataFrame(top_co_products)

            if not co_df.empty:
                # 创建共现分析图表
                fig_co_analysis = go.Figure()

                # 按新品分组并排序，展示每个新品的前3个共现产品
                for new_product in co_df['新品名称'].unique():
                    product_data = co_df[co_df['新品名称'] == new_product].sort_values('共现次数',
                                                                                       ascending=False).head(3)

                    # 为每个新品创建独立的分组条形图
                    for i, row in product_data.iterrows():
                        fig_co_analysis.add_trace(go.Bar(
                            x=[row['新品名称']],
                            y=[row['共现次数']],
                            name=row['共现产品名称'],
                            text=[row['共现产品名称']],
                            textposition='auto'
                        ))

                fig_co_analysis.update_layout(
                    title="新品与热门产品共现关系 (前3名)",
                    xaxis_title="新品名称",
                    yaxis_title="共现次数",
                    legend_title="共现产品",
                    barmode='group'
                )

                st.plotly_chart(fig_co_analysis, use_container_width=True)

                # 添加图表解释
                add_chart_explanation("""
                <b>图表解读：</b> 此图表显示每种新品与哪些产品最经常被同一客户一起购买，横轴表示新品名称，纵轴表示共同购买的次数，颜色区分不同的共现产品。
                共现次数高的产品组合通常表明这些产品之间可能有互补关系或被消费者认为适合一起购买。
                <b>行动建议：</b> 针对共现频率高的产品组合，考虑在销售系统中设置关联推荐；开发组合促销方案；调整货架陈列，将共现产品放在相近位置。
                """)

                # 热力图分析
                st.markdown('<div class="sub-header">产品共现热力图</div>', unsafe_allow_html=True)

                # 筛选主要产品以避免图表过于复杂
                important_products = set(valid_new_products)  # 确保包含所有新品

                # 添加与新品高度相关的产品
                for np_code in valid_new_products:
                    top_related = co_occurrence.loc[np_code].sort_values(ascending=False).head(3).index.tolist()
                    important_products.update(top_related)

                important_products = list(important_products)

                if len(important_products) > 2:  # 确保有足够的产品进行分析
                    # 创建简化名称映射的列表
                    important_product_names = [name_mapping.get(code, code) for code in important_products]

                    # 创建热力图数据
                    heatmap_data = co_occurrence.loc[important_products, important_products].copy()

                    # 对角线设为0（产品不与自身共现）
                    np.fill_diagonal(heatmap_data.values, 0)

                    # 创建热力图
                    fig_heatmap = px.imshow(
                        heatmap_data,
                        labels=dict(x="产品", y="产品", color="共现次数"),
                        x=important_product_names,
                        y=important_product_names,
                        color_continuous_scale="Blues",
                        title="主要产品共现热力图"
                    )

                    fig_heatmap.update_layout(
                        xaxis_tickangle=-45
                    )

                    # 添加数值注释
                    for i in range(len(important_products)):
                        for j in range(len(important_products)):
                            if heatmap_data.iloc[i, j] > 0:  # 只显示非零值
                                fig_heatmap.add_annotation(
                                    x=j,
                                    y=i,
                                    text=f"{int(heatmap_data.iloc[i, j])}",
                                    showarrow=False,
                                    font=dict(
                                        color="white" if heatmap_data.iloc[
                                                             i, j] > heatmap_data.max().max() / 2 else "black"
                                    )
                                )

                    st.plotly_chart(fig_heatmap, use_container_width=True)

                    # 添加图表解释
                    add_chart_explanation("""
                    <b>图表解读：</b> 此热力图展示了主要产品之间的共现关系，颜色越深表示两个产品一起购买的频率越高，数字显示具体共现次数。
                    通过热力图可迅速识别产品间的强关联性，深色方块代表高频共现的产品组合，这些组合在市场上受到客户的普遍欢迎。
                    <b>行动建议：</b> 对高共现值（深色区域）的产品组合设计捆绑促销方案；对中等共现值的组合进行交叉推荐增强关联性；对理论上互补但共现值低的产品组合，可通过货架邻近摆放提升协同效应。
                    """)
                else:
                    st.info("共现产品数量不足，无法生成有意义的热力图。请扩大数据范围。")
            else:
                st.warning("在当前筛选条件下，未发现新品有明显的共现关系。可能是新品购买量较少或共现样本不足。")

            # 产品购买模式分析
            st.markdown('<div class="sub-header">产品购买模式分析</div>', unsafe_allow_html=True)

            # 计算平均每单购买的产品种类数
            avg_products_per_order = transaction_binary.sum(axis=1).mean()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">平均每客户购买产品种类</p>
                    <p class="card-value">{avg_products_per_order:.2f}</p>
                    <p class="card-text">客户购买多样性指标</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # 计算含有新品的订单比例
                orders_with_new_products = transaction_binary[valid_new_products].any(
                    axis=1).sum() if valid_new_products else 0
                total_orders = len(transaction_binary)
                percentage_orders_with_new = (orders_with_new_products / total_orders * 100) if total_orders > 0 else 0

                st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">含新品的客户比例</p>
                    <p class="card-value">{percentage_orders_with_new:.2f}%</p>
                    <p class="card-text">尝试过新品的客户比例</p>
                </div>
                """, unsafe_allow_html=True)

            # 购买产品种类数分布
            products_per_order = transaction_binary.sum(axis=1).value_counts().sort_index().reset_index()
            products_per_order.columns = ['产品种类数', '客户数']

            fig_products_dist = px.bar(
                products_per_order,
                x='产品种类数',
                y='客户数',
                title='客户购买产品种类数分布',
                color='产品种类数',
                text='客户数'
            )
            fig_products_dist.update_traces(
                textposition='outside'
            )
            fig_products_dist.update_layout(
                xaxis_title="购买产品种类数",
                yaxis_title="客户数量",
                xaxis=dict(dtick=1),  # 强制X轴只显示整数
                coloraxis_showscale=False
            )

            st.plotly_chart(fig_products_dist, use_container_width=True)

            # 添加购买模式图表解释
            add_chart_explanation("""
            <b>图表解读：</b> 此图表展示客户购买产品种类数的分布情况，横轴表示购买的不同产品种类数，纵轴表示对应的客户数量。
            通过分析可以发现客户购买行为的多样性特征，了解客户是倾向于集中购买少数几种固定产品，还是喜欢尝试多种产品组合。
            <b>行动建议：</b> 针对单一产品购买客户，设计阶梯式交叉销售激励方案；对购买2-3种产品的客户，提供组合优惠增强购买意愿；对多种类购买客户，开发更具个性化的产品套餐。
            """)

            # 添加产品组合总结
            st.markdown("""
            ### 产品组合分析总结
            产品组合分析揭示了产品间的关联性和客户购买模式，为交叉销售、组合营销和产品开发提供了重要依据。
            通过新品与现有产品的共现关系，可以制定更有效的新品推广策略；通过客户购买模式分析，可以优化产品组合和个性化营销方案。
            """)

            # 产品组合表格
            with st.expander("查看产品共现矩阵数据"):
                # 转换产品代码为简化名称
                display_co_occurrence = co_occurrence.copy()
                display_co_occurrence.index = [name_mapping.get(code, code) for code in display_co_occurrence.index]
                display_co_occurrence.columns = [name_mapping.get(code, code) for code in display_co_occurrence.columns]
                st.dataframe(display_co_occurrence, use_container_width=True)
        else:
            st.warning("当前筛选条件下的数据不足以进行产品组合分析。请确保有多个客户和产品。")

with tabs[4]:  # 市场渗透率
    st.markdown('<div class="sub-header">🌐 新品市场渗透分析</div>', unsafe_allow_html=True)

    if not filtered_df.empty:
        # 计算总体渗透率
        total_customers = filtered_df['客户简称'].nunique()
        new_product_customers = filtered_new_products_df['客户简称'].nunique()
        penetration_rate = (new_product_customers / total_customers * 100) if total_customers > 0 else 0

        # KPI指标卡
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">总客户数</p>
                <p class="card-value">{total_customers}</p>
                <p class="card-text">市场覆盖基数</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">购买新品的客户数</p>
                <p class="card-value">{new_product_customers}</p>
                <p class="card-text">新品接受客户</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">新品市场渗透率</p>
                <p class="card-value">{penetration_rate:.2f}%</p>
                <p class="card-text">新品覆盖率</p>
            </div>
            """, unsafe_allow_html=True)

        # 渗透率综合分析
        st.markdown('<div class="sub-header">区域渗透率综合分析</div>', unsafe_allow_html=True)

        if 'selected_regions' in locals() and selected_regions:
            # 按区域计算渗透率
            region_customers = filtered_df.groupby('所属区域')['客户简称'].nunique().reset_index()
            region_customers.columns = ['所属区域', '客户总数']

            new_region_customers = filtered_new_products_df.groupby('所属区域')['客户简称'].nunique().reset_index()
            new_region_customers.columns = ['所属区域', '购买新品客户数']

            region_penetration = region_customers.merge(new_region_customers, on='所属区域', how='left')
            region_penetration['购买新品客户数'] = region_penetration['购买新品客户数'].fillna(0)
            region_penetration['渗透率'] = region_penetration['购买新品客户数'] / region_penetration['客户总数'] * 100
            region_penetration['渗透率'] = region_penetration['渗透率'].round(2)

            # 计算每个区域的新品销售额
            region_new_sales = filtered_new_products_df.groupby('所属区域')['销售额'].sum().reset_index()
            region_new_sales.columns = ['所属区域', '新品销售额']

            # 合并渗透率和销售额数据
            region_analysis = region_penetration.merge(region_new_sales, on='所属区域', how='left')
            region_analysis['新品销售额'] = region_analysis['新品销售额'].fillna(0)

            # 创建渗透率柱状图
            cols = st.columns(2)
            with cols[0]:
                fig_penetration = px.bar(
                    region_penetration,
                    x='所属区域',
                    y='渗透率',
                    title="各区域新品渗透率",
                    color='所属区域',
                    text='渗透率'
                )
                fig_penetration.update_traces(
                    texttemplate='%{text:.2f}%',
                    textposition='outside'
                )
                fig_penetration.update_layout(
                    xaxis_title="区域",
                    yaxis_title="渗透率 (%)",
                    showlegend=False
                )
                st.plotly_chart(fig_penetration, use_container_width=True)

            with cols[1]:
                # 渗透率-销售额散点图
                fig_penetration_sales = px.scatter(
                    region_analysis,
                    x='渗透率',
                    y='新品销售额',
                    size='客户总数',
                    color='所属区域',
                    hover_name='所属区域',
                    title="渗透率与销售额关系",
                    labels={
                        '渗透率': '渗透率 (%)',
                        '新品销售额': '新品销售额 (元)',
                        '客户总数': '客户总数'
                    }
                )
                fig_penetration_sales.update_layout(
                    xaxis_title="渗透率 (%)",
                    yaxis_title="新品销售额 (元)",
                    yaxis=dict(tickprefix="￥", tickformat=",.2f", ticksuffix=" 元")
                )

                # 添加平均值参考线
                fig_penetration_sales.add_shape(
                    type="line",
                    x0=0,
                    x1=region_analysis['渗透率'].max() * 1.1,
                    y0=region_analysis['新品销售额'].mean(),
                    y1=region_analysis['新品销售额'].mean(),
                    line=dict(color="orange", width=1, dash="dash")
                )

                fig_penetration_sales.add_shape(
                    type="line",
                    x0=region_analysis['渗透率'].mean(),
                    x1=region_analysis['渗透率'].mean(),
                    y0=0,
                    y1=region_analysis['新品销售额'].max() * 1.1,
                    line=dict(color="orange", width=1, dash="dash")
                )

                st.plotly_chart(fig_penetration_sales, use_container_width=True)

            # 添加图表解释
            add_chart_explanation("""
            <b>图表解读：</b> 左图展示各区域的新品市场渗透率，即购买新品的客户占总客户的比例；右图是渗透率与销售额的关系分析，气泡大小代表客户数量，虚线表示平均值。
            通过四象限分析可见：右上方为明星区域，渗透率高且销售额高；左上方为潜力区域，渗透率低但销售额高；左下方为待开发区域；右下方为效率提升区域。
            <b>行动建议：</b> 明星区域应总结成功经验并推广；潜力区域需扩大客户覆盖面；待开发区域加强培训和营销；效率提升区域应提高客单价。
            """)

            # 渗透率月度趋势分析
            if '发运月份' in filtered_df.columns and not filtered_df.empty:
                st.markdown('<div class="sub-header">新品渗透率月度趋势</div>', unsafe_allow_html=True)

                try:
                    # 确保日期类型正确
                    filtered_df['发运月份'] = pd.to_datetime(filtered_df['发运月份'])
                    filtered_new_products_df['发运月份'] = pd.to_datetime(filtered_new_products_df['发运月份'])

                    # 计算月度渗透率
                    monthly_customers = filtered_df.groupby(pd.Grouper(key='发运月份', freq='M'))[
                        '客户简称'].nunique().reset_index()
                    monthly_customers.columns = ['月份', '客户总数']

                    monthly_new_customers = filtered_new_products_df.groupby(pd.Grouper(key='发运月份', freq='M'))[
                        '客户简称'].nunique().reset_index()
                    monthly_new_customers.columns = ['月份', '购买新品客户数']

                    # 计算月度销售额
                    monthly_sales = filtered_df.groupby(pd.Grouper(key='发运月份', freq='M'))[
                        '销售额'].sum().reset_index()
                    monthly_sales.columns = ['月份', '销售额总计']

                    monthly_new_sales = filtered_new_products_df.groupby(pd.Grouper(key='发运月份', freq='M'))[
                        '销售额'].sum().reset_index()
                    monthly_new_sales.columns = ['月份', '新品销售额']

                    # 合并数据
                    monthly_data = monthly_customers.merge(monthly_new_customers, on='月份', how='left')
                    monthly_data = monthly_data.merge(monthly_sales, on='月份', how='left')
                    monthly_data = monthly_data.merge(monthly_new_sales, on='月份', how='left')

                    # 填充缺失值
                    monthly_data['购买新品客户数'] = monthly_data['购买新品客户数'].fillna(0)
                    monthly_data['新品销售额'] = monthly_data['新品销售额'].fillna(0)

                    # 计算渗透率和销售占比
                    monthly_data['渗透率'] = (monthly_data['购买新品客户数'] / monthly_data['客户总数'] * 100).round(2)
                    monthly_data['销售占比'] = (monthly_data['新品销售额'] / monthly_data['销售额总计'] * 100).round(2)

                    # 创建月度趋势图
                    fig_monthly_trend = make_subplots(specs=[[{"secondary_y": True}]])

                    # 添加渗透率线
                    fig_monthly_trend.add_trace(
                        go.Scatter(
                            x=monthly_data['月份'],
                            y=monthly_data['渗透率'],
                            mode='lines+markers+text',
                            name='新品渗透率',
                            line=dict(color='blue', width=3),
                            marker=dict(size=10),
                            text=[f"{x:.1f}%" for x in monthly_data['渗透率']],
                            textposition='top center'
                        ),
                        secondary_y=False
                    )

                    # 添加销售占比线
                    fig_monthly_trend.add_trace(
                        go.Scatter(
                            x=monthly_data['月份'],
                            y=monthly_data['销售占比'],
                            mode='lines+markers+text',
                            name='新品销售占比',
                            line=dict(color='red', width=3, dash='dot'),
                            marker=dict(size=10),
                            text=[f"{x:.1f}%" for x in monthly_data['销售占比']],
                            textposition='bottom center'
                        ),
                        secondary_y=True
                    )

                    # 更新布局
                    fig_monthly_trend.update_layout(
                        title="新品渗透率与销售占比月度趋势",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    # 更新X轴
                    fig_monthly_trend.update_xaxes(
                        title_text="月份",
                        tickformat='%Y-%m'
                    )

                    # 更新Y轴
                    fig_monthly_trend.update_yaxes(
                        title_text="新品渗透率 (%)",
                        secondary_y=False
                    )

                    fig_monthly_trend.update_yaxes(
                        title_text="新品销售占比 (%)",
                        secondary_y=True
                    )

                    st.plotly_chart(fig_monthly_trend, use_container_width=True)

                    # 添加图表解释
                    add_chart_explanation("""
                    <b>图表解读：</b> 此图表展示新品渗透率（蓝色实线）和新品销售占比（红色虚线）的月度变化趋势，帮助识别新品市场表现的动态变化。
                    渗透率与销售占比的变化趋势反映了客户数量与销售额的协同性，月度波动反映了季节性因素或营销活动的影响，趋势线方向揭示了新品市场接受度的整体发展态势。
                    <b>行动建议：</b> 识别渗透率峰值月份分析成功因素；针对渗透率低谷期制定特别促销；当渗透率上升但销售占比下降时关注客单价提升；当整体呈下降趋势时考虑产品创新或营销调整。
                    """)

                except Exception as e:
                    st.warning(f"无法处理月度渗透率分析。错误：{str(e)}")

            # 添加渗透率分析总结
            st.markdown(f"""
            ### 新品渗透分析总结
            当前新品整体市场渗透率为<strong>{penetration_rate:.2f}%</strong>，即在所有{total_customers}名客户中，有{new_product_customers}名客户购买了新品。
            通过区域渗透率分析和月度趋势观察，可识别渗透表现最佳的区域和时段，为后续新品推广策略制定提供数据支持。
            """, unsafe_allow_html=True)  # 添加unsafe_allow_html=True参数
        else:
            st.warning("请在侧边栏选择至少一个区域以查看区域渗透率分析。")
    else:
        st.warning("当前筛选条件下没有数据。请调整筛选条件。")

# 添加页脚信息
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年4月</p>
    <p>使用Streamlit和Plotly构建 | 数据更新频率: 每季度</p>
</div>
""", unsafe_allow_html=True)