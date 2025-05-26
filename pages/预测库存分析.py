# pages/预测库存分析.py - 优化版
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_lottie import st_lottie
import json
import requests

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="库存预警仪表盘",
    page_icon="📦",
    layout="wide"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 自定义CSS - 紫色主题
st.markdown("""
<style>
    /* 紫色主题背景渐变 - 与主页面保持一致 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
    }
    
    /* 动态背景波纹效果 */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: waveMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes waveMove {
        0%, 100% { 
            background-position: 0% 0%, 100% 100%;
            opacity: 0.8;
        }
        50% { 
            background-position: 100% 100%, 0% 0%;
            opacity: 1;
        }
    }
    
    /* 确保内容在背景之上 */
    .main .block-container {
        position: relative;
        z-index: 1;
        background: transparent !important;
    }
    
    /* 深色图表背景 */
    .js-plotly-plot .plotly {
        background-color: rgba(139, 92, 246, 0.1) !important;
    }
    
    /* 指标卡片紫色主题 */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
        background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.95));
    }
    
    /* 标签样式 */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 15px;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: transparent;
        border-radius: 10px;
        padding: 0 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        color: white;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* 文本颜色 */
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }
    
    /* 信息卡片样式 */
    .stInfo, .stWarning, .stSuccess {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: #2d3748 !important;
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* 悬浮提示框美化 */
    .hoverlabel {
        background: rgba(102, 126, 234, 0.95) !important;
        border: 1px solid #667eea !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }
    
    /* 解释框样式 */
    .interpretation-box {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# 紫色配色方案 - 与主页面保持一致
COLOR_SCHEME = {
    'gradient_purple': ['#667eea', '#764ba2'],
    'gradient_pink': ['#EC4899', '#BE185D'],
    'gradient_orange': ['#F59E0B', '#DC2626'],
    'gradient_blue': ['#3B82F6', '#1E40AF'],
    'gradient_green': ['#10B981', '#059669'],
    'risk_extreme': '#DC2626',
    'risk_high': '#F59E0B',
    'risk_medium': '#EAB308',
    'risk_low': '#10B981',
    'risk_minimal': '#3B82F6'
}

# 加载Lottie动画
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# 数据加载和处理函数
@st.cache_data
def load_and_process_data():
    """加载和处理所有数据"""
    try:
        # 读取数据文件
        shipment_df = pd.read_excel('2409~250224出货数据.xlsx')
        forecast_df = pd.read_excel('2409~2502人工预测.xlsx')
        inventory_df = pd.read_excel('含批次库存0221(2).xlsx')
        price_df = pd.read_excel('单价.xlsx')
        
        # 处理日期
        shipment_df['订单日期'] = pd.to_datetime(shipment_df['订单日期'])
        forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'], format='%Y-%m')
        
        # 创建产品代码到名称的映射
        product_name_map = {}
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and pd.notna(row['描述']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                product_name_map[row['物料']] = row['描述']
        
        # 处理库存数据 - 提取批次信息
        batch_data = []
        current_material = None
        current_desc = None
        current_stock = 0
        current_price = 0
        
        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and isinstance(row['物料'], str) and row['物料'].startswith('F'):
                current_material = row['物料']
                current_desc = row['描述']
                current_stock = row['现有库存'] if pd.notna(row['现有库存']) else 0
                # 获取单价
                price_match = price_df[price_df['产品代码'] == current_material]
                current_price = price_match['单价'].iloc[0] if len(price_match) > 0 else 100
            elif pd.notna(row['生产日期']) and current_material:
                # 这是批次信息行
                prod_date = pd.to_datetime(row['生产日期'])
                quantity = row['数量'] if pd.notna(row['数量']) else 0
                batch_no = row['生产批号'] if pd.notna(row['生产批号']) else ''
                
                # 计算库龄
                age_days = (datetime.now() - prod_date).days
                
                # 确定风险等级
                if age_days >= 120:
                    risk_level = '极高风险'
                    risk_color = COLOR_SCHEME['risk_extreme']
                    risk_advice = '立即启动7折清库'
                elif age_days >= 90:
                    risk_level = '高风险'
                    risk_color = COLOR_SCHEME['risk_high']
                    risk_advice = '建议8折促销'
                elif age_days >= 60:
                    risk_level = '中风险'
                    risk_color = COLOR_SCHEME['risk_medium']
                    risk_advice = '适度促销9折'
                elif age_days >= 30:
                    risk_level = '低风险'
                    risk_color = COLOR_SCHEME['risk_low']
                    risk_advice = '正常销售'
                else:
                    risk_level = '极低风险'
                    risk_color = COLOR_SCHEME['risk_minimal']
                    risk_advice = '新鲜库存'
                
                # 计算预期损失
                if age_days >= 120:
                    expected_loss = quantity * current_price * 0.3
                elif age_days >= 90:
                    expected_loss = quantity * current_price * 0.2
                elif age_days >= 60:
                    expected_loss = quantity * current_price * 0.1
                else:
                    expected_loss = 0
                
                batch_data.append({
                    '物料': current_material,
                    '产品名称': current_desc,  # 添加产品名称
                    '描述': current_desc,
                    '生产日期': prod_date,
                    '生产批号': batch_no,
                    '数量': quantity,
                    '库龄': age_days,
                    '风险等级': risk_level,
                    '风险颜色': risk_color,
                    '处理建议': risk_advice,
                    '单价': current_price,
                    '批次价值': quantity * current_price,
                    '预期损失': expected_loss
                })
        
        processed_inventory = pd.DataFrame(batch_data)
        
        # 将产品代码替换为产品名称
        shipment_df['产品名称'] = shipment_df['产品代码'].map(product_name_map).fillna(shipment_df['产品代码'])
        forecast_df['产品名称'] = forecast_df['产品代码'].map(product_name_map).fillna(forecast_df['产品代码'])
        
        # 计算预测准确率
        forecast_accuracy = calculate_forecast_accuracy(shipment_df, forecast_df)
        
        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory, forecast_accuracy)
        
        return processed_inventory, forecast_accuracy, shipment_df, forecast_df, metrics, product_name_map
        
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None, None, None, None, None

def calculate_forecast_accuracy(shipment_df, forecast_df):
    """计算预测准确率"""
    # 按月份和产品聚合实际销量
    shipment_monthly = shipment_df.groupby([
        shipment_df['订单日期'].dt.to_period('M'),
        '产品代码'
    ])['求和项:数量（箱）'].sum().reset_index()
    shipment_monthly['年月'] = shipment_monthly['订单日期'].dt.to_timestamp()
    
    # 合并预测和实际数据
    merged = forecast_df.merge(
        shipment_monthly,
        left_on=['所属年月', '产品代码'],
        right_on=['年月', '产品代码'],
        how='inner'
    )
    
    # 计算预测准确率
    merged['预测误差'] = abs(merged['预计销售量'] - merged['求和项:数量（箱）'])
    merged['预测准确率'] = 1 - (merged['预测误差'] / (merged['求和项:数量（箱）'] + 1))
    merged['预测准确率'] = merged['预测准确率'].clip(0, 1)
    
    return merged

def calculate_key_metrics(processed_inventory, forecast_accuracy):
    """计算关键指标"""
    if processed_inventory.empty:
        return None
    
    total_batches = len(processed_inventory)
    high_risk_batches = len(processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])])
    high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0
    
    total_inventory_value = processed_inventory['批次价值'].sum() / 1000000
    high_risk_value = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险'])
    ]['批次价值'].sum()
    high_risk_value_ratio = (high_risk_value / processed_inventory['批次价值'].sum() * 100) if processed_inventory['批次价值'].sum() > 0 else 0
    
    avg_age = processed_inventory['库龄'].mean()
    forecast_acc = forecast_accuracy['预测准确率'].mean() * 100 if not forecast_accuracy.empty else 0
    
    # 风险分布统计
    risk_counts = processed_inventory['风险等级'].value_counts().to_dict()
    
    return {
        'total_batches': int(total_batches),
        'high_risk_batches': int(high_risk_batches),
        'high_risk_ratio': round(high_risk_ratio, 1),
        'total_inventory_value': round(total_inventory_value, 2),
        'high_risk_value_ratio': round(high_risk_value_ratio, 1),
        'avg_age': round(avg_age, 0),
        'forecast_accuracy': round(forecast_acc, 1),
        'high_risk_value': round(high_risk_value / 1000000, 1),
        'risk_counts': {
            'extreme': risk_counts.get('极高风险', 0),
            'high': risk_counts.get('高风险', 0),
            'medium': risk_counts.get('中风险', 0),
            'low': risk_counts.get('低风险', 0),
            'minimal': risk_counts.get('极低风险', 0)
        }
    }

# 加载数据
processed_inventory, forecast_accuracy, shipment_df, forecast_df, metrics, product_name_map = load_and_process_data()

if metrics is None:
    st.stop()

# 紫色主题的plotly布局模板
plotly_layout_template = dict(
    plot_bgcolor='rgba(255, 255, 255, 0.05)',
    paper_bgcolor='rgba(255, 255, 255, 0.1)',
    font=dict(color='white'),
    title_font=dict(color='white', size=16),
    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', zerolinecolor='rgba(255, 255, 255, 0.2)'),
    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', zerolinecolor='rgba(255, 255, 255, 0.2)'),
    hoverlabel=dict(bgcolor='rgba(102, 126, 234, 0.9)', font_color='white', font_size=14),
    colorway=['#667eea', '#EC4899', '#F59E0B', '#10B981', '#3B82F6']
)

# 页面标题 - 使用彩色标题
colored_header(
    label="📦 库存预警仪表盘",
    description="智能库存风险监控与促销决策支持系统",
    color_name="blue-70"
)

# 加载动画
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json"
lottie_json = load_lottie_url(lottie_url)

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 关键指标总览",
    "🚨 风险分析",
    "📈 预测分析",
    "👥 责任分析",
    "📋 库存分析"
])

# 标签1：关键指标总览
with tab1:
    # 显示动画
    if lottie_json:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_json, height=200, key="inventory_animation")
    
    # 关键指标展示
    st.markdown("### 🎯 核心风险指标")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="总批次数量",
            value=f"{metrics['total_batches']:,}",
            delta=f"高风险: {metrics['high_risk_batches']}个",
            delta_color="inverse",
            help=f"库存批次总数{metrics['total_batches']}个，其中{metrics['high_risk_batches']}个批次处于高风险状态"
        )
    
    with col2:
        st.metric(
            label="高风险批次占比",
            value=f"{metrics['high_risk_ratio']}%",
            delta="需要紧急处理" if metrics['high_risk_ratio'] > 15 else "风险可控",
            delta_color="inverse" if metrics['high_risk_ratio'] > 15 else "normal",
            help=f"{metrics['high_risk_ratio']}%的批次处于高风险状态，主要集中在库龄超过90天的产品"
        )
    
    with col3:
        st.metric(
            label="库存总价值",
            value=f"¥{metrics['total_inventory_value']}M",
            delta=f"高风险: ¥{metrics['high_risk_value']}M",
            help=f"库存总价值{metrics['total_inventory_value']}百万元，高价值产品需要重点关注"
        )
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(
            label="高风险价值占比",
            value=f"{metrics['high_risk_value_ratio']}%",
            delta="严重影响现金流" if metrics['high_risk_value_ratio'] > 30 else "影响可控",
            delta_color="inverse" if metrics['high_risk_value_ratio'] > 30 else "normal",
            help=f"{metrics['high_risk_value_ratio']}%的高价值库存需要促销清库"
        )
    
    with col5:
        st.metric(
            label="平均库龄",
            value=f"{metrics['avg_age']}天",
            delta="需要优化" if metrics['avg_age'] > 60 else "状态良好",
            delta_color="inverse" if metrics['avg_age'] > 60 else "normal",
            help=f"平均库龄{metrics['avg_age']}天，受季节性因素影响较大"
        )
    
    with col6:
        st.metric(
            label="预测准确率",
            value=f"{metrics['forecast_accuracy']}%",
            delta="持续改善中",
            help=f"整体预测准确率{metrics['forecast_accuracy']}%"
        )
    
    # 应用样式
    style_metric_cards(
        background_color="rgba(255, 255, 255, 0.95)",
        border_left_color="#667eea",
        border_color="rgba(255, 255, 255, 0.3)",
        box_shadow=True
    )
    
    # 风险分布可视化
    st.markdown("### 📊 风险等级分布")
    
    # 添加图表解释
    with st.expander("📖 如何理解这个图表？"):
        st.markdown("""
        <div class='interpretation-box'>
        这个柱状图展示了库存批次按风险等级的分布情况：
        
        - **极高风险（红色）**：库龄超过120天，需要立即7折清库
        - **高风险（橙色）**：库龄90-120天，建议8折促销
        - **中风险（黄色）**：库龄60-90天，适度9折促销
        - **低风险（绿色）**：库龄30-60天，正常销售
        - **极低风险（蓝色）**：库龄30天内，新鲜库存
        
        通过这个分布，您可以快速了解库存的整体健康状况。
        </div>
        """, unsafe_allow_html=True)
    
    # 创建风险分布的可视化
    risk_data = pd.DataFrame({
        '风险等级': ['极高风险', '高风险', '中风险', '低风险', '极低风险'],
        '批次数量': [
            metrics['risk_counts']['extreme'],
            metrics['risk_counts']['high'],
            metrics['risk_counts']['medium'],
            metrics['risk_counts']['low'],
            metrics['risk_counts']['minimal']
        ],
        '颜色': [
            COLOR_SCHEME['risk_extreme'],
            COLOR_SCHEME['risk_high'],
            COLOR_SCHEME['risk_medium'],
            COLOR_SCHEME['risk_low'],
            COLOR_SCHEME['risk_minimal']
        ]
    })
    
    fig_risk_dist = px.bar(
        risk_data,
        x='风险等级',
        y='批次数量',
        color='风险等级',
        color_discrete_map={
            '极高风险': COLOR_SCHEME['risk_extreme'],
            '高风险': COLOR_SCHEME['risk_high'],
            '中风险': COLOR_SCHEME['risk_medium'],
            '低风险': COLOR_SCHEME['risk_low'],
            '极低风险': COLOR_SCHEME['risk_minimal']
        },
        text='批次数量'
    )
    
    fig_risk_dist.update_traces(
        texttemplate='%{text}个',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>批次数量: %{y}个<extra></extra>'
    )
    
    fig_risk_dist.update_layout(
        **plotly_layout_template,
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="批次数量"
    )
    
    st.plotly_chart(fig_risk_dist, use_container_width=True)

# 标签2：风险分析
with tab2:
    st.markdown("### 🎯 高风险批次优先级矩阵")
    
    # 添加图表解释
    with st.expander("📖 如何理解这个图表？"):
        st.markdown("""
        <div class='interpretation-box'>
        这是一个气泡图，帮助您识别需要优先处理的高风险批次：
        
        - **横轴（库龄）**：批次存放时间越长，风险越高
        - **纵轴（批次价值）**：价值越高的批次，潜在损失越大
        - **气泡大小**：代表批次数量，气泡越大数量越多
        - **颜色**：红色为极高风险，橙色为高风险
        
        **重点关注**：右上角的大气泡（高龄高值大批量），这些应该优先处理！
        </div>
        """, unsafe_allow_html=True)
    
    # 获取高风险批次数据
    high_risk_items = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险'])
    ].head(50)
    
    if not high_risk_items.empty:
        # 创建气泡图
        fig_bubble = go.Figure()
        
        # 添加极高风险批次
        extreme_risk = high_risk_items[high_risk_items['风险等级'] == '极高风险']
        if not extreme_risk.empty:
            fig_bubble.add_trace(go.Scatter(
                x=extreme_risk['库龄'],
                y=extreme_risk['批次价值'],
                mode='markers',
                marker=dict(
                    size=extreme_risk['数量'] / 10,
                    sizemode='diameter',
                    sizemin=10,
                    color=COLOR_SCHEME['risk_extreme'],
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=extreme_risk['产品名称'],  # 使用产品名称
                customdata=np.column_stack((
                    extreme_risk['物料'],
                    extreme_risk['产品名称'],  # 使用产品名称
                    extreme_risk['生产批号'],
                    extreme_risk['生产日期'].dt.strftime('%Y-%m-%d'),
                    extreme_risk['数量'],
                    extreme_risk['单价'],
                    extreme_risk['风险颜色'],
                    extreme_risk['风险等级'],
                    extreme_risk['处理建议'],
                    extreme_risk['预期损失']
                )),
                hovertemplate="""
                <b>产品信息</b><br>
                产品代码: %{customdata[0]}<br>
                产品名称: %{customdata[1]}<br>
                <br>
                <b>库存详情</b><br>
                批次号: %{customdata[2]}<br>
                生产日期: %{customdata[3]}<br>
                库龄: <b>%{x}天</b><br>
                <br>
                <b>价值分析</b><br>
                批次数量: %{customdata[4]:,}箱<br>
                单价: ¥%{customdata[5]:.2f}<br>
                批次价值: <b>¥%{y:,.0f}</b><br>
                <br>
                <b>风险评估</b><br>
                风险等级: <span style='color:%{customdata[6]}'><b>%{customdata[7]}</b></span><br>
                建议处理: %{customdata[8]}<br>
                预计损失: ¥%{customdata[9]:,.0f}<br>
                <extra></extra>
                """,
                name='极高风险'
            ))
        
        # 添加高风险批次
        high_risk = high_risk_items[high_risk_items['风险等级'] == '高风险']
        if not high_risk.empty:
            fig_bubble.add_trace(go.Scatter(
                x=high_risk['库龄'],
                y=high_risk['批次价值'],
                mode='markers',
                marker=dict(
                    size=high_risk['数量'] / 10,
                    sizemode='diameter',
                    sizemin=10,
                    color=COLOR_SCHEME['risk_high'],
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=high_risk['产品名称'],  # 使用产品名称
                customdata=np.column_stack((
                    high_risk['物料'],
                    high_risk['产品名称'],  # 使用产品名称
                    high_risk['生产批号'],
                    high_risk['生产日期'].dt.strftime('%Y-%m-%d'),
                    high_risk['数量'],
                    high_risk['单价'],
                    high_risk['风险颜色'],
                    high_risk['风险等级'],
                    high_risk['处理建议'],
                    high_risk['预期损失']
                )),
                hovertemplate="""
                <b>产品信息</b><br>
                产品代码: %{customdata[0]}<br>
                产品名称: %{customdata[1]}<br>
                <br>
                <b>库存详情</b><br>
                批次号: %{customdata[2]}<br>
                生产日期: %{customdata[3]}<br>
                库龄: <b>%{x}天</b><br>
                <br>
                <b>价值分析</b><br>
                批次数量: %{customdata[4]:,}箱<br>
                单价: ¥%{customdata[5]:.2f}<br>
                批次价值: <b>¥%{y:,.0f}</b><br>
                <br>
                <b>风险评估</b><br>
                风险等级: <span style='color:%{customdata[6]}'><b>%{customdata[7]}</b></span><br>
                建议处理: %{customdata[8]}<br>
                预计损失: ¥%{customdata[9]:,.0f}<br>
                <extra></extra>
                """,
                name='高风险'
            ))
        
        # 更新布局
        fig_bubble.update_layout(
            **plotly_layout_template,
            title="风险-价值四象限分析（气泡大小=批次数量）",
            xaxis_title="库龄（天）",
            yaxis_title="批次价值（元）",
            height=600,
            hovermode='closest',
            shapes=[
                # 添加象限分割线
                dict(
                    type='line',
                    x0=90, y0=0, x1=90, y1=high_risk_items['批次价值'].max(),
                    line=dict(color='rgba(255,255,255,0.2)', dash='dash')
                ),
                dict(
                    type='line',
                    x0=0, y0=high_risk_items['批次价值'].median(),
                    x1=high_risk_items['库龄'].max(), y1=high_risk_items['批次价值'].median(),
                    line=dict(color='rgba(255,255,255,0.2)', dash='dash')
                )
            ],
            annotations=[
                dict(
                    x=45, y=high_risk_items['批次价值'].max() * 0.9,
                    text="低龄高值<br>(关注)",
                    showarrow=False,
                    font=dict(size=12, color='white')
                ),
                dict(
                    x=135, y=high_risk_items['批次价值'].max() * 0.9,
                    text="高龄高值<br>(紧急)",
                    showarrow=False,
                    font=dict(size=12, color='white')
                )
            ]
        )
        
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    # 风险价值分布
    st.markdown("### 💰 风险价值结构分析")
    
    # 添加图表解释
    with st.expander("📖 如何理解这个图表？"):
        st.markdown("""
        <div class='interpretation-box'>
        这个饼图展示了不同风险等级批次的价值占比：
        
        - 帮助您了解风险批次占用的资金比例
        - 红色和橙色部分越大，说明积压的高风险库存价值越高
        - 理想情况下，蓝色和绿色（低风险）应该占主导
        
        **决策建议**：如果高风险占比超过30%，需要立即采取清库行动！
        </div>
        """, unsafe_allow_html=True)
    
    # 饼图
    risk_value = processed_inventory.groupby('风险等级')['批次价值'].sum()
    
    fig_pie = px.pie(
        values=risk_value.values,
        names=risk_value.index,
        color=risk_value.index,
        color_discrete_map={
            '极高风险': COLOR_SCHEME['risk_extreme'],
            '高风险': COLOR_SCHEME['risk_high'],
            '中风险': COLOR_SCHEME['risk_medium'],
            '低风险': COLOR_SCHEME['risk_low'],
            '极低风险': COLOR_SCHEME['risk_minimal']
        },
        hole=0.4
    )
    
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>价值: ¥%{value:,.0f}<br>占比: %{percent}<extra></extra>'
    )
    
    fig_pie.update_layout(
        **plotly_layout_template,
        title="风险价值分布",
        height=400
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

# 标签3：预测分析
with tab3:
    st.markdown("### 📈 预测准确率分析")
    
    # 添加图表解释
    with st.expander("📖 如何理解这个图表？"):
        st.markdown("""
        <div class='interpretation-box'>
        这个趋势图展示了预测准确率的月度变化：
        
        - **实线**：月度平均预测准确率
        - **阴影区域**：预测准确率的波动范围
        - 准确率越高，说明预测越精准，库存风险越低
        - 波动范围越小，说明预测质量越稳定
        
        **改进建议**：关注准确率下降的月份，分析原因并优化预测模型。
        </div>
        """, unsafe_allow_html=True)
    
    if not forecast_accuracy.empty:
        # 月度趋势分析
        monthly_acc = forecast_accuracy.groupby(
            forecast_accuracy['所属年月'].dt.to_period('M')
        )['预测准确率'].agg(['mean', 'std']).reset_index()
        monthly_acc['年月'] = monthly_acc['所属年月'].dt.to_timestamp()
        
        fig_trend = go.Figure()
        
        # 添加准确率线
        fig_trend.add_trace(go.Scatter(
            x=monthly_acc['年月'],
            y=monthly_acc['mean'] * 100,
            mode='lines+markers',
            name='预测准确率',
            line=dict(color=COLOR_SCHEME['gradient_purple'][0], width=3),
            marker=dict(size=10),
            hovertemplate='月份: %{x|%Y-%m}<br>准确率: %{y:.1f}%<extra></extra>'
        ))
        
        # 添加标准差范围
        fig_trend.add_trace(go.Scatter(
            x=monthly_acc['年月'],
            y=(monthly_acc['mean'] + monthly_acc['std']) * 100,
            mode='lines',
            name='上限',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=monthly_acc['年月'],
            y=(monthly_acc['mean'] - monthly_acc['std']) * 100,
            mode='lines',
            name='下限',
            line=dict(color='rgba(0,0,0,0)'),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.2)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_trend.update_layout(
            **plotly_layout_template,
            title="预测准确率月度趋势（含波动范围）",
            xaxis_title="月份",
            yaxis_title="预测准确率（%）",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # 预测偏差分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 产品预测难度分析")
        
        # 添加图表解释
        with st.expander("📖 如何理解这个图表？"):
            st.markdown("""
            <div class='interpretation-box'>
            这个散点图帮助识别哪些产品最难预测：
            
            - **横轴**：平均预测准确率（越右越好）
            - **纵轴**：预测波动性（越低越稳定）
            - **圆圈大小**：预测次数（越大数据越多）
            - **颜色深浅**：预测难度（越红越难）
            
            **重点产品**：左上角的红色大圆圈需要特别关注！
            </div>
            """, unsafe_allow_html=True)
        
        if not forecast_accuracy.empty:
            # 计算产品预测难度
            product_difficulty = forecast_accuracy.groupby('产品名称').agg({
                '预测准确率': ['mean', 'std', 'count']
            }).reset_index()
            product_difficulty.columns = ['产品名称', '平均准确率', '准确率标准差', '预测次数']
            product_difficulty['预测难度'] = (1 - product_difficulty['平均准确率']) * product_difficulty['准确率标准差']
            product_difficulty = product_difficulty.sort_values('预测难度', ascending=False).head(20)
            
            fig_difficulty = px.scatter(
                product_difficulty,
                x='平均准确率',
                y='准确率标准差',
                size='预测次数',
                color='预测难度',
                color_continuous_scale='Reds',
                hover_data=['产品名称'],
                labels={
                    '平均准确率': '平均预测准确率',
                    '准确率标准差': '预测波动性',
                    '预测次数': '预测次数',
                    '预测难度': '预测难度系数'
                }
            )
            
            fig_difficulty.update_layout(
                **plotly_layout_template,
                title="产品预测难度矩阵",
                height=400
            )
            
            st.plotly_chart(fig_difficulty, use_container_width=True)
    
    with col2:
        st.markdown("#### 👥 销售员预测能力评分")
        
        # 添加图表解释
        with st.expander("📖 如何理解这个图表？"):
            st.markdown("""
            <div class='interpretation-box'>
            这个条形图展示所有销售员的预测能力评分：
            
            - **评分计算**：综合考虑准确率和预测次数
            - **颜色深浅**：反映平均预测准确率
            - 评分越高，预测能力越强
            
            **培训建议**：为评分较低的销售员提供预测技能培训。
            </div>
            """, unsafe_allow_html=True)
        
        if not forecast_accuracy.empty:
            # 计算销售员预测能力（显示全部）
            sales_ability = forecast_accuracy.groupby('销售员').agg({
                '预测准确率': ['mean', 'count'],
                '预测误差': 'sum'
            }).reset_index()
            sales_ability.columns = ['销售员', '平均准确率', '预测次数', '总误差']
            sales_ability['能力评分'] = sales_ability['平均准确率'] * 100 * (1 - 1/(1 + sales_ability['预测次数']))
            sales_ability = sales_ability.sort_values('能力评分', ascending=True)  # 显示全部
            
            fig_sales = px.bar(
                sales_ability,
                y='销售员',
                x='能力评分',
                orientation='h',
                color='平均准确率',
                color_continuous_scale='Viridis',
                text='能力评分'
            )
            
            fig_sales.update_traces(
                texttemplate='%{text:.1f}分',
                textposition='outside'
            )
            
            fig_sales.update_layout(
                **plotly_layout_template,
                title="销售员预测能力排名（全部）",
                xaxis_title="预测能力评分",
                yaxis_title="",
                height=max(400, len(sales_ability) * 25)  # 根据人数调整高度
            )
            
            st.plotly_chart(fig_sales, use_container_width=True)

# 标签4：责任分析
with tab4:
    st.markdown("### 🌍 区域绩效分析")
    
    # 添加图表解释
    with st.expander("📖 如何理解雷达图？"):
        st.markdown("""
        <div class='interpretation-box'>
        雷达图展示各区域在7个维度的综合表现：
        
        - **总销量**：区域总体销售业绩
        - **平均订单量**：单笔订单规模
        - **订单数**：销售活跃度
        - **销售员数**：团队规模
        - **产品种类**：产品多样性
        - **人均销量**：销售效率
        - **订单效率**：单均产出
        
        **如何解读**：面积越大、越接近外圈的区域综合绩效越好。
        </div>
        """, unsafe_allow_html=True)
    
    if not shipment_df.empty:
        # 区域统计
        region_stats = shipment_df.groupby('所属区域').agg({
            '求和项:数量（箱）': ['sum', 'mean', 'count'],
            '申请人': 'nunique',
            '产品代码': 'nunique'
        }).round(2)
        region_stats.columns = ['总销量', '平均订单量', '订单数', '销售员数', '产品种类']
        region_stats = region_stats.reset_index()
        
        # 计算效率指标
        region_stats['人均销量'] = region_stats['总销量'] / region_stats['销售员数']
        region_stats['订单效率'] = region_stats['总销量'] / region_stats['订单数']
        
        # 创建雷达图
        categories = ['总销量', '平均订单量', '订单数', '销售员数', '产品种类', '人均销量', '订单效率']
        
        fig_radar = go.Figure()
        
        colors = ['#667eea', '#EC4899', '#F59E0B', '#10B981', '#3B82F6']
        for i, region in enumerate(region_stats['所属区域'].unique()):
            region_data = region_stats[region_stats['所属区域'] == region]
            
            # 标准化数据到0-100
            values = []
            for cat in categories:
                max_val = region_stats[cat].max()
                min_val = region_stats[cat].min()
                if max_val > min_val:
                    normalized = (region_data[cat].values[0] - min_val) / (max_val - min_val) * 100
                else:
                    normalized = 50
                values.append(normalized)
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=region,
                line_color=colors[i % len(colors)],
                opacity=0.6
            ))
        
        fig_radar.update_layout(
            **plotly_layout_template,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                bgcolor='rgba(255, 255, 255, 0.05)'
            ),
            showlegend=True,
            title="区域综合绩效雷达图",
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # 区域-产品交叉分析
        st.markdown("### 🎯 区域-产品交叉绩效热力图")
        
        # 添加图表解释
        with st.expander("📖 如何理解热力图？"):
            st.markdown("""
            <div class='interpretation-box'>
            热力图展示不同区域对各产品的销售情况：
            
            - **颜色深浅**：销量大小（越深销量越大）
            - **横轴**：TOP10畅销产品
            - **纵轴**：各销售区域
            
            **业务洞察**：
            - 深色区域：该区域的强势产品
            - 浅色区域：潜力待开发的产品
            - 横向对比：产品在各区域的受欢迎程度
            - 纵向对比：区域的产品结构特点
            
            **决策建议**：将强势区域的成功经验复制到弱势区域。
            </div>
            """, unsafe_allow_html=True)
        
        # 获取TOP10产品（使用产品名称）
        top_products = shipment_df.groupby('产品名称')['求和项:数量（箱）'].sum().nlargest(10).index
        
        # 创建交叉表
        cross_table = pd.crosstab(
            shipment_df[shipment_df['产品名称'].isin(top_products)]['所属区域'],
            shipment_df[shipment_df['产品名称'].isin(top_products)]['产品名称'],
            values=shipment_df[shipment_df['产品名称'].isin(top_products)]['求和项:数量（箱）'],
            aggfunc='sum'
        )
        
        fig_heatmap = px.imshow(
            cross_table,
            labels=dict(x="产品", y="区域", color="销量"),
            color_continuous_scale='Purples',
            aspect='auto'
        )
        
        fig_heatmap.update_traces(
            hovertemplate='区域: %{y}<br>产品: %{x}<br>销量: %{z:,.0f}箱<extra></extra>'
        )
        
        # 合并xaxis设置
        heatmap_layout = plotly_layout_template.copy()
        heatmap_layout['xaxis']['tickangle'] = -45
        
        fig_heatmap.update_layout(
            **heatmap_layout,
            title="区域-产品销量分布热力图（TOP10产品）",
            height=400
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)

# 标签5：库存分析
with tab5:
    st.markdown("### 📈 库存健康度分析")
    
    # 添加图表解释
    with st.expander("📖 如何理解这个图表？"):
        st.markdown("""
        <div class='interpretation-box'>
        这个组合图展示库存的累积趋势：
        
        - **紫色曲线**：累计库存量变化
        - **蓝色柱状**：每月新增入库量
        - **绿色虚线**：平均库存水平（健康基准线）
        
        **健康判断**：
        - 累计曲线平稳上升：库存增长可控
        - 突然陡升：可能存在滞销风险
        - 高于平均线过多：库存积压严重
        </div>
        """, unsafe_allow_html=True)
    
    # 创建库存趋势（使用实际数据）
    inventory_by_date = processed_inventory.groupby(
        processed_inventory['生产日期'].dt.to_period('M')
    )['数量'].sum().reset_index()
    inventory_by_date['生产日期'] = inventory_by_date['生产日期'].dt.to_timestamp()
    
    # 计算累计库存
    inventory_by_date = inventory_by_date.sort_values('生产日期')
    inventory_by_date['累计库存'] = inventory_by_date['数量'].cumsum()
    
    fig_inventory = go.Figure()
    
    # 添加库存趋势线
    fig_inventory.add_trace(go.Scatter(
        x=inventory_by_date['生产日期'],
        y=inventory_by_date['累计库存'],
        mode='lines+markers',
        name='累计库存',
        line=dict(color=COLOR_SCHEME['gradient_purple'][0], width=3),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)',
        hovertemplate='月份: %{x|%Y-%m}<br>累计库存: %{y:,.0f}箱<extra></extra>'
    ))
    
    # 添加月度入库量
    fig_inventory.add_trace(go.Bar(
        x=inventory_by_date['生产日期'],
        y=inventory_by_date['数量'],
        name='月度入库',
        marker_color=COLOR_SCHEME['gradient_blue'][1],
        opacity=0.6,
        yaxis='y2',
        hovertemplate='月份: %{x|%Y-%m}<br>入库量: %{y:,.0f}箱<extra></extra>'
    ))
    
    # 计算并添加健康线
    avg_inventory = inventory_by_date['累计库存'].mean()
    fig_inventory.add_hline(
        y=avg_inventory,
        line_dash="dash",
        line_color="#10B981",
        annotation_text=f"平均库存: {avg_inventory:,.0f}箱",
        annotation_font_color="white"
    )
    
    fig_inventory.update_layout(
        **plotly_layout_template,
        title="库存累计趋势与健康度分析",
        xaxis_title="月份",
        yaxis_title="累计库存（箱）",
        yaxis2=dict(
            title="月度入库（箱）",
            overlaying='y',
            side='right',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_inventory, use_container_width=True)
    
    # ABC分析和智能补货建议
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 ABC分类管理")
        
        # 添加图表解释
        with st.expander("📖 什么是ABC分类？"):
            st.markdown("""
            <div class='interpretation-box'>
            ABC分类是库存管理的经典方法：
            
            - **A类产品**：占库存价值80%，需重点管理
            - **B类产品**：占库存价值15%，常规管理
            - **C类产品**：占库存价值5%，简化管理
            
            **管理策略**：
            - A类：每日监控，保持低库存高周转
            - B类：每周检查，平衡库存和服务水平
            - C类：每月盘点，可适当增加安全库存
            </div>
            """, unsafe_allow_html=True)
        
        # 基于批次价值进行ABC分类
        total_value = processed_inventory['批次价值'].sum()
        product_value = processed_inventory.groupby('产品名称')['批次价值'].sum().sort_values(ascending=False)
        
        # ABC分类
        cumsum_pct = product_value.cumsum() / total_value
        a_products = product_value[cumsum_pct <= 0.8].index
        b_products = product_value[(cumsum_pct > 0.8) & (cumsum_pct <= 0.95)].index
        c_products = product_value[cumsum_pct > 0.95].index
        
        abc_data = pd.DataFrame({
            '类别': ['A类', 'B类', 'C类'],
            '产品数量': [len(a_products), len(b_products), len(c_products)],
            '价值占比': [80, 15, 5],
            '管理策略': ['重点管理', '常规管理', '简化管理']
        })
        
        fig_abc = px.sunburst(
            abc_data,
            path=['类别'],
            values='产品数量',
            color='价值占比',
            color_continuous_scale='Purples',
            hover_data=['管理策略']
        )
        
        fig_abc.update_layout(
            **plotly_layout_template,
            title="ABC分类分布",
            height=400
        )
        
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔄 库存周转效率")
        
        # 添加图表解释
        with st.expander("📖 如何理解周转率？"):
            st.markdown("""
            <div class='interpretation-box'>
            库存周转率反映库存的流动效率：
            
            - **周转率 = 365 / 平均库龄**
            - 周转率越高，资金利用效率越好
            - 不同风险等级的理想周转率：
              - 极低风险：>12次/年
              - 低风险：8-12次/年
              - 中风险：4-8次/年
              - 高风险：<4次/年（需改进）
            
            **圆圈大小**代表库存数量
            </div>
            """, unsafe_allow_html=True)
        
        # 计算库存周转率
        turnover_data = processed_inventory.groupby('风险等级').agg({
            '数量': 'sum',
            '库龄': 'mean'
        }).reset_index()
        
        turnover_data['周转率'] = 365 / turnover_data['库龄']
        
        fig_turnover = px.scatter(
            turnover_data,
            x='库龄',
            y='周转率',
            size='数量',
            color='风险等级',
            color_discrete_map={
                '极高风险': COLOR_SCHEME['risk_extreme'],
                '高风险': COLOR_SCHEME['risk_high'],
                '中风险': COLOR_SCHEME['risk_medium'],
                '低风险': COLOR_SCHEME['risk_low'],
                '极低风险': COLOR_SCHEME['risk_minimal']
            },
            hover_data=['数量']
        )
        
        fig_turnover.update_layout(
            **plotly_layout_template,
            title="库存周转效率分析",
            xaxis_title="平均库龄（天）",
            yaxis_title="年周转率",
            height=400
        )
        
        st.plotly_chart(fig_turnover, use_container_width=True)
    
    # 智能补货建议
    st.markdown("### 💡 智能决策建议")
    
    # 创建建议卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(
            f"""
            **🚨 紧急清库建议**
            
            - 极高风险批次：{metrics['risk_counts']['extreme']}个
            - 建议7折清库，预计回收¥{metrics['high_risk_value']*0.7:.1f}M
            - 优先处理TOP5高价值批次
            """
        )
    
    with col2:
        st.warning(
            f"""
            **📊 预测优化建议**
            
            - 当前准确率：{metrics['forecast_accuracy']}%
            - 建议加强季节性调整
            - 重点提升低准确率产品的预测
            """
        )
    
    with col3:
        st.success(
            f"""
            **🔄 补货策略建议**
            
            - A类产品：保持2周安全库存
            - B类产品：保持3周安全库存
            - C类产品：按需订货
            """
        )
