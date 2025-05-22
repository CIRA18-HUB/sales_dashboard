import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import math
import os

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="库存预警仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clay.com风格CSS样式
st.markdown("""
<style>
    /* 导入Inter字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Clay.com风格配色和动画 */
    :root {
        --clay-black: #000000;
        --clay-white: #ffffff;
        --clay-teal: #49c5b6;
        --clay-light-gray: #f8f9fa;
        --clay-gray: #6c757d;
        --clay-light-blue: #e3f2fd;
        --clay-orange: #ff5722;
        --clay-divider: #e0e0e0;
        --clay-shadow: 0 2px 8px rgba(0,0,0,0.08);
        --clay-shadow-hover: 0 8px 25px rgba(73, 197, 182, 0.15);
    }

    /* 全局字体设置 */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 隐藏Streamlit默认元素 */
    .streamlit-container {
        background-color: var(--clay-white);
    }

    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}

    /* 主标题样式 */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: var(--clay-black);
        text-align: center;
        margin: 3rem 0 4rem 0;
        letter-spacing: -0.02em;
        line-height: 1.1;
        animation: fadeInUp 0.6s ease-out;
    }

    /* 指标卡片样式 */
    .metric-card {
        background: var(--clay-white);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--clay-shadow);
        border: 1px solid var(--clay-divider);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        animation: slideUp 0.4s ease-out;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--clay-teal), var(--clay-black));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--clay-shadow-hover);
        border-color: var(--clay-teal);
    }

    .metric-card:hover::before {
        transform: scaleX(1);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--clay-black);
        margin-bottom: 0.5rem;
        line-height: 1;
    }

    .metric-label {
        font-size: 1rem;
        color: var(--clay-gray);
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .metric-time {
        font-size: 0.8rem;
        color: var(--clay-teal);
        font-weight: 600;
        font-style: italic;
    }

    /* 图表容器样式 */
    .chart-container {
        background: var(--clay-white);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--clay-shadow);
        border: 1px solid var(--clay-divider);
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-out;
        transition: all 0.3s ease;
    }

    .chart-container:hover {
        box-shadow: var(--clay-shadow-hover);
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: var(--clay-light-gray);
        border-radius: 12px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: var(--clay-gray);
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0.75rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--clay-black);
        color: var(--clay-white);
        transform: scale(1.05);
    }

    /* 动画定义 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .metric-card:active {
        animation: pulse 0.1s ease;
    }

    /* 加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid var(--clay-divider);
        border-radius: 50%;
        border-top-color: var(--clay-teal);
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .metric-card {
            padding: 1.5rem;
        }
        .metric-value {
            font-size: 2rem;
        }
    }

    /* 骨架屏样式 */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
    }

    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
</style>
""", unsafe_allow_html=True)


class InventoryWarningSystem:
    """库存预警分析系统 - Clay风格版本"""

    def __init__(self):
        self.inventory_data = None
        self.batch_data = None
        self.shipping_data = None
        self.forecast_data = None
        self.price_data = None
        self.monthly_inventory = None
        self.batch_analysis = None

        # 风险参数设置
        self.high_stock_days = 90
        self.medium_stock_days = 60
        self.low_stock_days = 30
        self.high_volatility_threshold = 1.0
        self.medium_volatility_threshold = 0.8
        self.high_forecast_bias_threshold = 0.3
        self.medium_forecast_bias_threshold = 0.15
        self.min_daily_sales = 0.5
        self.min_seasonal_index = 0.3

        # Clay风格颜色配置
        self.colors = {
            '极高风险': '#ff5722',
            '高风险': '#ff8a65',
            '中风险': '#ffb74d',
            '低风险': '#81c784',
            '极低风险': '#49c5b6',
            'primary': '#000000',
            'teal': '#49c5b6',
            'gray': '#6c757d',
            'white': '#ffffff'
        }

    @st.cache_data
    def load_data(_self):
        """加载所有数据文件"""
        try:
            with st.spinner('🔄 数据加载中...'):
                # 1. 加载库存数据
                inventory_raw = pd.read_excel("含批次库存0221(2).xlsx", header=0)

                # 处理产品信息
                product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
                _self.inventory_data = product_rows.iloc[:, :7].copy()
                _self.inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                                '现有库存可订量', '待入库量', '本月剩余可订量']

                # 处理批次信息
                batch_rows = inventory_raw[inventory_raw.iloc[:, 7].notna()]
                _self.batch_data = batch_rows.iloc[:, 7:].copy()
                _self.batch_data.columns = ['库位', '生产日期', '生产批号', '数量']

                # 为批次数据添加产品代码
                product_code = None
                product_description = None
                batch_with_product = []

                for i, row in inventory_raw.iterrows():
                    if pd.notna(row.iloc[0]):
                        product_code = row.iloc[0]
                        product_description = row.iloc[1]
                    elif pd.notna(row.iloc[7]):
                        batch_row = row.iloc[7:].copy()
                        batch_row_with_product = pd.Series([product_code, product_description] + batch_row.tolist())
                        batch_with_product.append(batch_row_with_product)

                _self.batch_data = pd.DataFrame(batch_with_product)
                _self.batch_data.columns = ['产品代码', '描述', '库位', '生产日期', '生产批号', '数量']
                _self.batch_data['生产日期'] = pd.to_datetime(_self.batch_data['生产日期'])

                # 2. 加载出货数据
                _self.shipping_data = pd.read_excel("2409~250224出货数据.xlsx", header=0)
                _self.shipping_data.columns = ['订单日期', '所属区域', '申请人', '产品代码', '数量']
                _self.shipping_data['订单日期'] = pd.to_datetime(_self.shipping_data['订单日期'])
                _self.shipping_data['数量'] = pd.to_numeric(_self.shipping_data['数量'], errors='coerce')
                _self.shipping_data = _self.shipping_data.dropna(subset=['数量'])

                # 3. 加载预测数据
                _self.forecast_data = pd.read_excel("2409~2502人工预测.xlsx", header=0)
                if len(_self.forecast_data.columns) == 1:
                    columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']
                    _self.forecast_data = pd.DataFrame([
                        row.split() for row in _self.forecast_data.iloc[:, 0]
                    ], columns=columns)
                    _self.forecast_data['预计销售量'] = _self.forecast_data['预计销售量'].astype(float)
                else:
                    _self.forecast_data.columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']

                _self.forecast_data['所属年月'] = pd.to_datetime(_self.forecast_data['所属年月'])
                _self.forecast_data['预计销售量'] = pd.to_numeric(_self.forecast_data['预计销售量'], errors='coerce')

                # 4. 加载单价数据
                _self.price_data = {}
                try:
                    price_df = pd.read_excel("单价.xlsx")
                    for _, row in price_df.iterrows():
                        _self.price_data[row['产品代码']] = row['单价']
                except:
                    # 使用默认单价
                    _self.price_data = {
                        'F01E4B': 137.04, 'F3411A': 137.04, 'F0104L': 126.72,
                        'F3406B': 129.36, 'F01C5D': 153.6, 'F01L3A': 182.4,
                        'F01L6A': 307.2, 'F01A3C': 175.5, 'F01H2B': 307.2,
                        'F01L4A': 182.4, 'F0104J': 216.96
                    }

                # 5. 加载月终库存数据
                try:
                    _self.monthly_inventory = pd.read_excel("月终库存2.xlsx", header=0)
                    _self.monthly_inventory['所属年月'] = pd.to_datetime(_self.monthly_inventory['所属年月'])
                except:
                    _self.monthly_inventory = None

                return True

        except Exception as e:
            st.error(f"数据加载失败: {str(e)}")
            return False

    def calculate_risk_percentage(self, days_to_clear, batch_age, target_days):
        """计算风险百分比"""
        if batch_age >= target_days:
            return 100.0
        if days_to_clear == float('inf'):
            return 100.0
        if days_to_clear >= 3 * target_days:
            return 100.0

        clearance_ratio = days_to_clear / target_days
        clearance_risk = 100 / (1 + math.exp(-4 * (clearance_ratio - 1)))
        age_risk = 100 * batch_age / target_days
        combined_risk = 0.8 * max(clearance_risk, age_risk) + 0.2 * min(clearance_risk, age_risk)

        if days_to_clear > target_days:
            combined_risk = max(combined_risk, 80)
        if days_to_clear >= 2 * target_days:
            combined_risk = max(combined_risk, 90)
        if batch_age >= 0.75 * target_days:
            combined_risk = max(combined_risk, 75)

        return min(100, round(combined_risk, 1))

    def analyze_batch_data(self):
        """分析批次数据"""
        if self.batch_data is None:
            return None

        batch_analysis = []
        today = datetime.now().date()

        # 计算每个产品的销售指标
        product_sales_metrics = {}
        for product_code in self.inventory_data['产品代码'].unique():
            product_sales = self.shipping_data[self.shipping_data['产品代码'] == product_code]

            if len(product_sales) == 0:
                product_sales_metrics[product_code] = {
                    'daily_avg_sales': 0,
                    'sales_std': 0,
                    'coefficient_of_variation': float('inf'),
                    'total_sales': 0
                }
            else:
                total_sales = product_sales['数量'].sum()
                days_range = (today - product_sales['订单日期'].min().date()).days + 1
                daily_avg_sales = total_sales / days_range if days_range > 0 else 0
                daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['数量'].sum()
                sales_std = daily_sales.std() if len(daily_sales) > 1 else 0
                coefficient_of_variation = sales_std / daily_avg_sales if daily_avg_sales > 0 else float('inf')

                product_sales_metrics[product_code] = {
                    'daily_avg_sales': daily_avg_sales,
                    'sales_std': sales_std,
                    'coefficient_of_variation': coefficient_of_variation,
                    'total_sales': total_sales
                }

        # 计算季节性指数
        seasonal_indices = {}
        for product_code in self.inventory_data['产品代码'].unique():
            product_sales = self.shipping_data[self.shipping_data['产品代码'] == product_code]
            if len(product_sales) > 0:
                product_sales['月份'] = product_sales['订单日期'].dt.month
                monthly_sales = product_sales.groupby('月份')['数量'].sum()
                if len(monthly_sales) > 1:
                    avg_monthly_sales = monthly_sales.mean()
                    current_month = today.month
                    if current_month in monthly_sales.index:
                        seasonal_index = monthly_sales[current_month] / avg_monthly_sales
                    else:
                        seasonal_index = 1.0
                else:
                    seasonal_index = 1.0
            else:
                seasonal_index = 1.0
            seasonal_index = max(seasonal_index, self.min_seasonal_index)
            seasonal_indices[product_code] = seasonal_index

        # 分析每个批次
        for _, batch in self.batch_data.iterrows():
            product_code = batch['产品代码']
            description = batch['描述']
            batch_date = batch['生产日期']
            batch_qty = batch['数量']

            batch_age = (today - batch_date.date()).days
            sales_metrics = product_sales_metrics.get(product_code, {
                'daily_avg_sales': 0,
                'sales_std': 0,
                'coefficient_of_variation': float('inf'),
                'total_sales': 0
            })

            seasonal_index = seasonal_indices.get(product_code, 1.0)
            unit_price = self.price_data.get(product_code, 50.0)
            batch_value = batch_qty * unit_price

            daily_avg_sales = sales_metrics['daily_avg_sales']
            daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, self.min_daily_sales)

            if daily_avg_sales_adjusted > 0:
                days_to_clear = batch_qty / daily_avg_sales_adjusted
                one_month_risk = self.calculate_risk_percentage(days_to_clear, batch_age, 30)
                two_month_risk = self.calculate_risk_percentage(days_to_clear, batch_age, 60)
                three_month_risk = self.calculate_risk_percentage(days_to_clear, batch_age, 90)
            else:
                days_to_clear = float('inf')
                one_month_risk = 100
                two_month_risk = 100
                three_month_risk = 100

            # 风险等级评估
            risk_score = 0
            if batch_age > 90:
                risk_score += 40
            elif batch_age > 60:
                risk_score += 30
            elif batch_age > 30:
                risk_score += 20
            else:
                risk_score += 10

            if days_to_clear == float('inf'):
                risk_score += 40
            elif days_to_clear > 180:
                risk_score += 35
            elif days_to_clear > 90:
                risk_score += 30
            elif days_to_clear > 60:
                risk_score += 20
            elif days_to_clear > 30:
                risk_score += 10

            if sales_metrics['coefficient_of_variation'] > 2.0:
                risk_score += 10
            elif sales_metrics['coefficient_of_variation'] > 1.0:
                risk_score += 5

            if risk_score >= 80:
                risk_level = "极高风险"
            elif risk_score >= 60:
                risk_level = "高风险"
            elif risk_score >= 40:
                risk_level = "中风险"
            elif risk_score >= 20:
                risk_level = "低风险"
            else:
                risk_level = "极低风险"

            # 建议措施
            if risk_level == "极高风险":
                recommendation = "紧急清理：考虑折价促销"
            elif risk_level == "高风险":
                recommendation = "优先处理：降价促销或转仓调配"
            elif risk_level == "中风险":
                recommendation = "密切监控：调整采购计划"
            elif risk_level == "低风险":
                recommendation = "常规管理：定期审查库存周转"
            else:
                recommendation = "维持现状：正常库存水平"

            batch_analysis.append({
                '物料': product_code,
                '描述': description,
                '批次日期': batch_date.date(),
                '批次库存': batch_qty,
                '库龄': batch_age,
                '批次价值': batch_value,
                '日均出货': round(daily_avg_sales, 2),
                '出货波动系数': round(sales_metrics['coefficient_of_variation'], 2),
                '预计清库天数': days_to_clear if days_to_clear != float('inf') else 999,
                '一个月积压风险': f"{round(one_month_risk, 1)}%",
                '两个月积压风险': f"{round(two_month_risk, 1)}%",
                '三个月积压风险': f"{round(three_month_risk, 1)}%",
                '季节性指数': round(seasonal_index, 2),
                '风险程度': risk_level,
                '风险得分': risk_score,
                '建议措施': recommendation
            })

        self.batch_analysis = pd.DataFrame(batch_analysis)

        # 排序
        risk_order = {"极高风险": 0, "高风险": 1, "中风险": 2, "低风险": 3, "极低风险": 4}
        self.batch_analysis['风险排序'] = self.batch_analysis['风险程度'].map(risk_order)
        self.batch_analysis = self.batch_analysis.sort_values(by=['风险排序', '库龄'], ascending=[True, False])
        self.batch_analysis = self.batch_analysis.drop(columns=['风险排序'])

        return self.batch_analysis

    def calculate_key_metrics(self):
        """计算关键指标"""
        if self.batch_analysis is None:
            return {}

        total_batches = len(self.batch_analysis)
        risk_counts = self.batch_analysis['风险程度'].value_counts()

        # 风险等级分布
        risk_distribution = {}
        for risk_level in ['极高风险', '高风险', '中风险', '低风险', '极低风险']:
            count = risk_counts.get(risk_level, 0)
            percentage = (count / total_batches * 100) if total_batches > 0 else 0
            risk_distribution[risk_level] = {'count': count, 'percentage': percentage}

        # 库存价值
        total_value = self.batch_analysis['批次价值'].sum()
        high_risk_value = self.batch_analysis[
            self.batch_analysis['风险程度'].isin(['极高风险', '高风险'])
        ]['批次价值'].sum()
        high_risk_value_pct = (high_risk_value / total_value * 100) if total_value > 0 else 0

        # 平均库龄
        avg_age = self.batch_analysis['库龄'].mean()

        # 预测准确率计算
        forecast_accuracy = self.calculate_forecast_accuracy()

        # 平均清库天数
        finite_clearance = self.batch_analysis[self.batch_analysis['预计清库天数'] != 999]['预计清库天数']
        avg_clearance = finite_clearance.mean() if len(finite_clearance) > 0 else 0

        # 整体出货波动系数
        finite_volatility = self.batch_analysis[self.batch_analysis['出货波动系数'] != float('inf')]['出货波动系数']
        avg_volatility = finite_volatility.mean() if len(finite_volatility) > 0 else 0

        return {
            'total_batches': total_batches,
            'risk_distribution': risk_distribution,
            'total_value': total_value,
            'high_risk_value': high_risk_value,
            'high_risk_value_pct': high_risk_value_pct,
            'avg_age': avg_age,
            'forecast_accuracy': forecast_accuracy,
            'avg_clearance': avg_clearance,
            'avg_volatility': avg_volatility
        }

    def calculate_forecast_accuracy(self):
        """计算预测准确率"""
        if self.forecast_data is None or self.shipping_data is None:
            return 0

        total_forecast = self.forecast_data['预计销售量'].sum()
        actual_sales = self.shipping_data['数量'].sum()

        if total_forecast > 0:
            accuracy = 1 - abs(total_forecast - actual_sales) / max(total_forecast, actual_sales)
            return max(0, min(1, accuracy)) * 100
        return 0


def create_metric_card(label, value, time_info, key=None):
    """创建Clay风格指标卡片"""
    card_html = f"""
    <div class="metric-card" onclick="document.getElementById('{key or label}').scrollIntoView()">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-time">{time_info}</div>
    </div>
    """
    return card_html


def apply_clay_theme(fig, height=400, show_legend=True):
    """应用Clay风格主题到图表"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=12, color='#000000'),
        margin=dict(t=80, b=40, l=40, r=40),
        height=height,
        showlegend=show_legend,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
    )
    return fig


def create_risk_distribution_chart(risk_data):
    """创建风险分布饼图"""
    labels = list(risk_data.keys())
    values = [risk_data[label]['count'] for label in labels]
    colors = ['#ff5722', '#ff8a65', '#ffb74d', '#81c784', '#49c5b6']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=3)),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=14, family='Inter'),
        hovertemplate='<b>%{label}</b><br>批次数量: %{value}<br>占比: %{percent}<extra></extra>'
    )])

    # 添加中心文字
    fig.add_annotation(
        text=f"<b>{sum(values)}</b><br>总批次",
        x=0.5, y=0.5,
        font_size=20,
        font_color='#000000',
        showarrow=False
    )

    fig.update_layout(
        title=dict(
            text="批次风险分布<br><sub>数据截止: 2025年2月</sub>",
            x=0.5,
            font=dict(size=18, color='#000000', family='Inter')
        )
    )

    fig = apply_clay_theme(fig, height=400, show_legend=False)

    return fig


def create_value_risk_chart(batch_analysis):
    """创建库存价值风险结构图"""
    risk_value = batch_analysis.groupby('风险程度')['批次价值'].sum().reset_index()
    colors = {'极高风险': '#ff5722', '高风险': '#ff8a65', '中风险': '#ffb74d',
              '低风险': '#81c784', '极低风险': '#49c5b6'}

    fig = go.Figure(data=[go.Bar(
        x=risk_value['风险程度'],
        y=risk_value['批次价值'],
        marker=dict(
            color=[colors.get(level, '#6c757d') for level in risk_value['风险程度']],
            line=dict(color='#ffffff', width=2)
        ),
        text=[f'¥{value:,.0f}' for value in risk_value['批次价值']],
        textposition='outside',
        textfont=dict(size=12, family='Inter'),
        hovertemplate='<b>%{x}</b><br>库存价值: ¥%{y:,.0f}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text="库存价值风险分布<br><sub>价值基准: 最新单价</sub>",
            x=0.5,
            font=dict(size=18, color='#000000', family='Inter')
        ),
        xaxis_title="风险等级",
        yaxis_title="库存价值 (元)"
    )

    fig = apply_clay_theme(fig, height=400)

    return fig


def create_high_risk_priority_chart(batch_analysis):
    """创建高风险批次处理优先级气泡图"""
    high_risk = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])].copy()

    if high_risk.empty:
        fig = go.Figure()
        fig.add_annotation(text="暂无高风险批次", x=0.5, y=0.5, showarrow=False)
        return fig

    # 处理无穷大的清库天数
    high_risk['清库天数_处理'] = high_risk['预计清库天数'].apply(
        lambda x: 365 if x == 999 else x
    )

    # 确保数据类型正确
    high_risk = high_risk.copy()
    high_risk['库龄'] = pd.to_numeric(high_risk['库龄'], errors='coerce')
    high_risk['批次价值'] = pd.to_numeric(high_risk['批次价值'], errors='coerce')
    high_risk['清库天数_处理'] = pd.to_numeric(high_risk['清库天数_处理'], errors='coerce')

    # 移除任何NaN值
    high_risk = high_risk.dropna(subset=['库龄', '批次价值', '清库天数_处理'])

    if high_risk.empty:
        fig = go.Figure()
        fig.add_annotation(text="暂无有效的高风险批次数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # 计算气泡大小
    size_vals = high_risk['清库天数_处理'] / 10
    size_vals = np.clip(size_vals, 8, 50)  # 限制气泡大小范围

    fig = go.Figure(data=go.Scatter(
        x=high_risk['库龄'].values,
        y=high_risk['批次价值'].values,
        mode='markers',
        marker=dict(
            size=size_vals,
            color=[{'极高风险': '#ff5722', '高风险': '#ff8a65'}.get(risk, '#6c757d')
                   for risk in high_risk['风险程度']],
            sizemode='diameter',
            line=dict(width=2, color='#FFFFFF'),
            opacity=0.8
        ),
        text=high_risk['物料'].values,
        hovertemplate='<b>%{text}</b><br>' +
                      '库龄: %{x}天<br>' +
                      '批次价值: ¥%{y:,.0f}<br>' +
                      '清库天数: %{customdata}<br>' +
                      '建议措施: %{customdata2}<extra></extra>',
        customdata=[
            '无法预计' if x == 999 else f'{x:.0f}天'
            for x in high_risk['预计清库天数']
        ],
        customdata2=high_risk['建议措施'].values
    ))

    fig.update_layout(
        title=dict(
            text="高风险批次处理优先级<br><sub>气泡大小表示清库难度 | 数据截止: 2025年2月</sub>",
            x=0.5,
            font=dict(size=18, color='#000000', family='Inter')
        ),
        xaxis_title="库龄 (天)",
        yaxis_title="批次价值 (元)"
    )

    fig = apply_clay_theme(fig, height=500)

    return fig


def create_forecast_trend_chart(system):
    """创建预测趋势+季节性图表"""
    if system.forecast_data is None or system.shipping_data is None:
        fig = go.Figure()
        fig.add_annotation(text="暂无预测数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # 按月汇总预测和实际数据
    forecast_monthly = system.forecast_data.groupby(
        system.forecast_data['所属年月'].dt.to_period('M')
    )['预计销售量'].sum().reset_index()
    forecast_monthly['所属年月'] = forecast_monthly['所属年月'].dt.to_timestamp()

    shipping_monthly = system.shipping_data.groupby(
        system.shipping_data['订单日期'].dt.to_period('M')
    )['数量'].sum().reset_index()
    shipping_monthly['订单日期'] = shipping_monthly['订单日期'].dt.to_timestamp()

    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['预测准确率趋势 + 季节性波动', '月度预测 vs 实际对比'],
        specs=[[{"secondary_y": True}], [{}]],
        vertical_spacing=0.15
    )

    # 计算准确率和季节性指数
    accuracy_data = []
    seasonal_data = []

    for _, forecast_row in forecast_monthly.iterrows():
        month = forecast_row['所属年月']
        forecast_qty = forecast_row['预计销售量']

        actual_qty = shipping_monthly[shipping_monthly['订单日期'] == month]['数量'].sum()

        if forecast_qty > 0 or actual_qty > 0:
            accuracy = 1 - abs(forecast_qty - actual_qty) / max(forecast_qty, actual_qty, 1)
            accuracy_data.append({'month': month, 'accuracy': accuracy * 100})

        # 简化的季节性指数
        month_num = month.month
        seasonal_index = 1 + 0.2 * np.sin(2 * np.pi * month_num / 12)  # 模拟季节性
        seasonal_data.append({'month': month, 'seasonal': seasonal_index * 100})

    if accuracy_data:
        accuracy_df = pd.DataFrame(accuracy_data)
        seasonal_df = pd.DataFrame(seasonal_data)

        # 第一个子图：趋势线
        fig.add_trace(
            go.Scatter(
                x=accuracy_df['month'],
                y=accuracy_df['accuracy'],
                mode='lines+markers',
                name='预测准确率',
                line=dict(color='#000000', width=3),
                marker=dict(size=8, color='#000000')
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=seasonal_df['month'],
                y=seasonal_df['seasonal'],
                mode='lines',
                name='季节性指数',
                line=dict(color='#49c5b6', width=2, dash='dash'),
                yaxis='y2'
            ),
            row=1, col=1, secondary_y=True
        )

    # 第二个子图：柱状图对比
    fig.add_trace(
        go.Bar(
            x=forecast_monthly['所属年月'],
            y=forecast_monthly['预计销售量'],
            name='预测销量',
            marker=dict(color='#ff8a65', opacity=0.8)
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            x=shipping_monthly['订单日期'],
            y=shipping_monthly['数量'],
            name='实际销量',
            marker=dict(color='#000000', opacity=0.8)
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=700,
        showlegend=True
    )

    fig = apply_clay_theme(fig, height=700)

    # 设置y轴标题
    fig.update_yaxes(title_text="准确率 (%)", row=1, col=1)
    fig.update_yaxes(title_text="季节性指数", secondary_y=True, row=1, col=1)
    fig.update_yaxes(title_text="销售量", row=2, col=1)
    fig.update_xaxes(title_text="月份", row=2, col=1)

    return fig


def create_product_forecast_matrix(system):
    """创建产品预测表现矩阵"""
    if system.forecast_data is None or system.shipping_data is None:
        fig = go.Figure()
        fig.add_annotation(text="暂无预测数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # 按产品汇总预测和实际数据
    forecast_by_product = system.forecast_data.groupby('产品代码')['预计销售量'].sum()
    actual_by_product = system.shipping_data.groupby('产品代码')['数量'].sum()

    # 合并数据
    comparison_data = []
    for product in forecast_by_product.index:
        forecast_qty = forecast_by_product.get(product, 0)
        actual_qty = actual_by_product.get(product, 0)

        if forecast_qty > 0 or actual_qty > 0:
            accuracy = 1 - abs(forecast_qty - actual_qty) / max(forecast_qty, actual_qty, 1)
            bias = (forecast_qty - actual_qty) / max(forecast_qty, actual_qty, 1)

            comparison_data.append({
                'product': product,
                'forecast': forecast_qty,
                'actual': actual_qty,
                'accuracy': accuracy * 100,
                'bias': bias * 100
            })

    if not comparison_data:
        fig = go.Figure()
        fig.add_annotation(text="暂无有效的预测对比数据", x=0.5, y=0.5, showarrow=False)
        return fig

    df = pd.DataFrame(comparison_data)

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['产品预测准确率散点图', '预测偏差分布'],
        specs=[[{}, {}]],
        horizontal_spacing=0.15
    )

    # 散点图
    fig.add_trace(
        go.Scatter(
            x=df['forecast'],
            y=df['actual'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['accuracy'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="准确率 (%)", x=0.45)
            ),
            text=df['product'],
            hovertemplate='<b>%{text}</b><br>' +
                          '预测量: %{x}<br>' +
                          '实际量: %{y}<br>' +
                          '准确率: %{marker.color:.1f}%<extra></extra>',
            name='产品'
        ),
        row=1, col=1
    )

    # 添加完美预测线
    max_val = max(df['forecast'].max(), df['actual'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(dash='dash', color='#000000'),
            name='完美预测线'
        ),
        row=1, col=1
    )

    # 箱线图
    fig.add_trace(
        go.Box(
            y=df['bias'],
            name='预测偏差',
            marker=dict(color='#49c5b6'),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=500
    )

    fig = apply_clay_theme(fig, height=500)

    fig.update_xaxes(title_text="预测销量", row=1, col=1)
    fig.update_yaxes(title_text="实际销量", row=1, col=1)
    fig.update_yaxes(title_text="偏差 (%)", row=1, col=2)

    return fig


def create_region_responsibility_chart(system):
    """创建区域责任全景图"""
    if system.shipping_data is None or system.forecast_data is None:
        fig = go.Figure()
        fig.add_annotation(text="暂无责任分析数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # 区域销售分析
    region_analysis = system.shipping_data.groupby('所属区域').agg({
        '数量': ['sum', 'count', 'std']
    }).round(2)

    region_analysis.columns = ['总销量', '订单数', '销量标准差']
    region_analysis['平均订单量'] = region_analysis['总销量'] / region_analysis['订单数']
    region_analysis['销量稳定性'] = 1 / (1 + region_analysis['销量标准差'] / region_analysis['总销量'])
    region_analysis = region_analysis.fillna(0)

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['区域销售表现热力图', '区域绩效雷达图'],
        specs=[[{"type": "heatmap"}, {"type": "scatterpolar"}]],
        horizontal_spacing=0.15
    )

    # 热力图数据准备
    metrics = ['总销量', '订单数', '平均订单量', '销量稳定性']
    normalized_data = region_analysis[metrics].copy()
    for col in metrics:
        normalized_data[col] = (normalized_data[col] - normalized_data[col].min()) / \
                               (normalized_data[col].max() - normalized_data[col].min())

    # 热力图
    fig.add_trace(
        go.Heatmap(
            z=normalized_data.values,
            x=metrics,
            y=region_analysis.index,
            colorscale='RdYlGn',
            showscale=True,
            text=[[f'{val:.2f}' for val in row] for row in region_analysis[metrics].values],
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate='<b>%{y}</b><br>' +
                          '%{x}: %{text}<br>' +
                          '标准化值: %{z:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # 雷达图（选择前5个区域）
    top_regions = region_analysis.nlargest(5, '总销量')

    for region in top_regions.index:
        fig.add_trace(
            go.Scatterpolar(
                r=normalized_data.loc[region, metrics].values,
                theta=metrics,
                fill='toself',
                name=region,
                line=dict(width=2)
            ),
            row=1, col=2
        )

    fig.update_layout(
        height=500
    )

    fig = apply_clay_theme(fig, height=500)

    return fig


def create_personnel_performance_chart(system):
    """创建人员责任分析图"""
    if system.shipping_data is None or system.forecast_data is None:
        fig = go.Figure()
        fig.add_annotation(text="暂无人员绩效数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # 销售员绩效分析
    sales_performance = []

    # 按销售员统计预测准确率
    for salesperson in system.forecast_data['销售员'].unique():
        # 预测数据
        person_forecast = system.forecast_data[
            system.forecast_data['销售员'] == salesperson
            ]['预计销售量'].sum()

        # 实际销售数据（基于申请人=销售员）
        person_actual = system.shipping_data[
            system.shipping_data['申请人'] == salesperson
            ]['数量'].sum()

        if person_forecast > 0 or person_actual > 0:
            accuracy = 1 - abs(person_forecast - person_actual) / max(person_forecast, person_actual, 1)

            # 库存健康度（简化计算）
            inventory_health = min(accuracy * 100, 100) if person_actual > 0 else 0

            sales_performance.append({
                'salesperson': salesperson,
                'forecast_accuracy': accuracy * 100,
                'inventory_health': inventory_health,
                'total_forecast': person_forecast,
                'total_actual': person_actual
            })

    if not sales_performance:
        fig = go.Figure()
        fig.add_annotation(text="暂无有效的销售员绩效数据", x=0.5, y=0.5, showarrow=False)
        return fig

    df = pd.DataFrame(sales_performance)

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['销售员绩效散点图', '绩效排名'],
        specs=[[{}, {}]],
        horizontal_spacing=0.15
    )

    # 散点图
    fig.add_trace(
        go.Scatter(
            x=df['forecast_accuracy'],
            y=df['inventory_health'],
            mode='markers+text',
            marker=dict(
                size=df['total_actual'] / df['total_actual'].max() * 30 + 10,
                color=df['forecast_accuracy'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="预测准确率 (%)", x=0.45)
            ),
            text=df['salesperson'],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>' +
                          '预测准确率: %{x:.1f}%<br>' +
                          '库存健康度: %{y:.1f}<br>' +
                          '实际销量: %{marker.size}<extra></extra>',
            name='销售员'
        ),
        row=1, col=1
    )

    # 绩效排名柱状图
    df['综合绩效'] = (df['forecast_accuracy'] + df['inventory_health']) / 2
    df_sorted = df.sort_values('综合绩效', ascending=True)

    fig.add_trace(
        go.Bar(
            x=df_sorted['综合绩效'],
            y=df_sorted['salesperson'],
            orientation='h',
            marker=dict(
                color=df_sorted['综合绩效'],
                colorscale='RdYlGn'
            ),
            text=[f'{val:.1f}' for val in df_sorted['综合绩效']],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>' +
                          '综合绩效: %{x:.1f}<extra></extra>',
            name='综合绩效'
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=500
    )

    fig = apply_clay_theme(fig, height=500)

    fig.update_xaxes(title_text="预测准确率 (%)", row=1, col=1)
    fig.update_yaxes(title_text="库存健康度", row=1, col=1)
    fig.update_xaxes(title_text="综合绩效分数", row=1, col=2)

    return fig


def create_inventory_trend_chart(system):
    """创建库存健康度全景图"""
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['月度库存趋势 (13个月)', '库存周转效率分析'],
        vertical_spacing=0.15
    )

    # 月度库存趋势
    if system.monthly_inventory is not None:
        monthly_trend = system.monthly_inventory.groupby('所属年月')['每月末库存'].sum().reset_index()

        fig.add_trace(
            go.Scatter(
                x=monthly_trend['所属年月'],
                y=monthly_trend['每月末库存'],
                mode='lines+markers',
                line=dict(color='#000000', width=3),
                marker=dict(size=8, color='#49c5b6'),
                fill='tonexty',
                fillcolor='rgba(73, 197, 182, 0.1)',
                name='月末库存',
                hovertemplate='<b>%{x}</b><br>' +
                              '月末库存: %{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

    # 库存周转分析（基于批次数据）
    if system.batch_analysis is not None:
        # 按风险等级统计库存周转
        turnover_data = system.batch_analysis.groupby('风险程度').agg({
            '批次库存': 'sum',
            '预计清库天数': 'mean'
        }).reset_index()

        # 计算周转率
        turnover_data['周转率'] = 365 / turnover_data['预计清库天数']
        turnover_data['周转率'] = turnover_data['周转率'].replace([np.inf, -np.inf], 0)

        fig.add_trace(
            go.Waterfall(
                x=turnover_data['风险程度'],
                y=turnover_data['周转率'],
                text=[f'{val:.1f}' for val in turnover_data['周转率']],
                textposition='outside',
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "#49c5b6"}},
                decreasing={"marker": {"color": "#ff5722"}},
                totals={"marker": {"color": "#000000"}},
                name='周转率',
                hovertemplate='<b>%{x}</b><br>' +
                              '周转率: %{y:.1f}<extra></extra>'
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=600
    )

    fig = apply_clay_theme(fig, height=600)

    fig.update_yaxes(title_text="库存数量", row=1, col=1)
    fig.update_yaxes(title_text="周转率", row=2, col=1)
    fig.update_xaxes(title_text="月份", row=1, col=1)
    fig.update_xaxes(title_text="风险等级", row=2, col=1)

    return fig


def create_abc_optimization_chart(system):
    """创建库存优化策略图"""
    if system.batch_analysis is None:
        fig = go.Figure()
        fig.add_annotation(text="暂无库存分析数据", x=0.5, y=0.5, showarrow=False)
        return fig

    # ABC分析
    value_sorted = system.batch_analysis.sort_values('批次价值', ascending=False).copy()
    value_sorted['累计价值'] = value_sorted['批次价值'].cumsum()
    total_value = value_sorted['批次价值'].sum()
    value_sorted['累计占比'] = value_sorted['累计价值'] / total_value

    # ABC分类
    value_sorted['ABC分类'] = 'C'
    value_sorted.loc[value_sorted['累计占比'] <= 0.8, 'ABC分类'] = 'A'
    value_sorted.loc[(value_sorted['累计占比'] > 0.8) & (value_sorted['累计占比'] <= 0.95), 'ABC分类'] = 'B'

    abc_counts = value_sorted['ABC分类'].value_counts()

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['ABC分类管理', '清库难度分析'],
        specs=[[{"type": "domain"}, {}]],
        horizontal_spacing=0.15
    )

    # ABC分析饼图
    fig.add_trace(
        go.Pie(
            labels=abc_counts.index,
            values=abc_counts.values,
            hole=0.4,
            text=abc_counts.index,
            textinfo='label+percent',
            textposition='outside',
            marker=dict(
                colors=['#000000', '#49c5b6', '#6c757d'],
                line=dict(color='#FFFFFF', width=2)
            ),
            hovertemplate='<b>%{label}类产品</b><br>' +
                          '批次数量: %{value}<br>' +
                          '占比: %{percent}<extra></extra>',
            name='ABC分类'
        ),
        row=1, col=1
    )

    # 清库难度气泡图
    fig.add_trace(
        go.Scatter(
            x=value_sorted['库龄'],
            y=value_sorted['预计清库天数'],
            mode='markers',
            marker=dict(
                size=value_sorted['批次价值'] / value_sorted['批次价值'].max() * 30 + 10,
                color=value_sorted['ABC分类'].map({'A': '#000000', 'B': '#49c5b6', 'C': '#6c757d'}),
                opacity=0.7,
                line=dict(width=2, color='#FFFFFF')
            ),
            text=value_sorted['物料'],
            hovertemplate='<b>%{text}</b><br>' +
                          '库龄: %{x}天<br>' +
                          '清库天数: %{y:.0f}天<br>' +
                          'ABC分类: %{marker.color}<extra></extra>',
            name='产品'
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=500
    )

    fig = apply_clay_theme(fig, height=500)

    fig.update_xaxes(title_text="库龄 (天)", row=1, col=2)
    fig.update_yaxes(title_text="预计清库天数", row=1, col=2)

    return fig


def main():
    """主函数"""
    # 主标题
    st.markdown('<h1 class="main-title">📊 库存预警仪表盘</h1>', unsafe_allow_html=True)

    # 初始化系统
    if 'system' not in st.session_state:
        st.session_state.system = InventoryWarningSystem()

    system = st.session_state.system

    # 加载数据
    if system.batch_analysis is None:
        if system.load_data():
            system.analyze_batch_data()
        else:
            st.error("❌ 数据加载失败，请检查文件路径")
            return

    # 计算关键指标
    metrics = system.calculate_key_metrics()

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 关键指标总览",
        "⚠️ 风险分析",
        "🎯 预测分析",
        "👥 责任分析",
        "📦 库存分析"
    ])

    with tab1:
        st.markdown("### 核心业务指标")
        st.markdown("*以下指标反映当前库存健康状况和促销清库决策依据*")

        # 创建指标卡片
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                create_metric_card(
                    "总批次数量",
                    f"{metrics['total_batches']:,}",
                    "数据截止: 2025年2月",
                    "total_batches"
                ),
                unsafe_allow_html=True
            )

            high_risk_count = metrics['risk_distribution']['极高风险']['count'] + \
                              metrics['risk_distribution']['高风险']['count']
            high_risk_pct = (high_risk_count / metrics['total_batches'] * 100) if metrics['total_batches'] > 0 else 0
            st.markdown(
                create_metric_card(
                    "高风险批次占比",
                    f"{high_risk_pct:.1f}%",
                    "促销清库重点关注",
                    "high_risk_batches"
                ),
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                create_metric_card(
                    "库存总价值",
                    f"¥{metrics['total_value']:,.0f}",
                    "基于最新单价计算",
                    "total_value"
                ),
                unsafe_allow_html=True
            )

            st.markdown(
                create_metric_card(
                    "高风险价值占比",
                    f"{metrics['high_risk_value_pct']:.1f}%",
                    "需要促销清库的价值",
                    "high_risk_value"
                ),
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                create_metric_card(
                    "平均库龄",
                    f"{metrics['avg_age']:.0f}天",
                    "计算截止: 2025年2月",
                    "avg_age"
                ),
                unsafe_allow_html=True
            )

            st.markdown(
                create_metric_card(
                    "整体预测准确率",
                    f"{metrics['forecast_accuracy']:.1f}%",
                    "2024年9月-2025年2月",
                    "forecast_accuracy"
                ),
                unsafe_allow_html=True
            )

    with tab2:
        st.markdown("### 库存风险分析")
        st.markdown("*风险评估基于库龄、销量波动、清库难度等多维度指标，为促销决策提供依据*")

        # 风险全景分析
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_risk = create_risk_distribution_chart(metrics['risk_distribution'])
            st.plotly_chart(fig_risk, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_value = create_value_risk_chart(system.batch_analysis)
            st.plotly_chart(fig_value, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 高风险批次处理优先级
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_priority = create_high_risk_priority_chart(system.batch_analysis)
        st.plotly_chart(fig_priority, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### 预测准确性分析")
        st.markdown("*评估预测系统表现和季节性影响，优化未来预测模型*")

        # 预测趋势全景
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_trend = create_forecast_trend_chart(system)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 产品预测表现矩阵
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_matrix = create_product_forecast_matrix(system)
        st.plotly_chart(fig_matrix, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("### 责任归属分析")
        st.markdown("*基于预测准确性和库存健康度的责任评估，优化团队绩效*")

        # 区域责任全景
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_region = create_region_responsibility_chart(system)
        st.plotly_chart(fig_region, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 人员责任分析
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_personnel = create_personnel_performance_chart(system)
        st.plotly_chart(fig_personnel, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab5:
        st.markdown("### 库存健康度分析")
        st.markdown("*库存趋势、周转效率和ABC优化策略*")

        # 库存健康度全景
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_health = create_inventory_trend_chart(system)
        st.plotly_chart(fig_health, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 库存优化策略
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_optimization = create_abc_optimization_chart(system)
        st.plotly_chart(fig_optimization, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()