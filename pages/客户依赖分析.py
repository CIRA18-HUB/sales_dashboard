# pages/客户依赖分析.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import re

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="客户依赖分析",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 (保持原有样式)
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 动态背景效果 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: backgroundMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes backgroundMove {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
    }

    /* 主容器 */
    .main .block-container {
        max-width: 1600px;
        padding: 2rem;
        position: relative;
        z-index: 10;
    }

    /* 页面标题 */
    .page-header {
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0;
        animation: fadeInDown 1s ease-out forwards;
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .page-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        animation: titleGlow 3s ease-in-out infinite;
    }

    @keyframes titleGlow {
        0%, 100% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.3); }
        50% { text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.6); }
    }

    .page-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
    }

    /* 关键指标卡片 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
        border-top: 4px solid transparent;
        border-image: linear-gradient(90deg, #667eea, #764ba2, #81ecec) 1;
    }

    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
    }

    .metric-icon {
        font-size: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        display: block;
        animation: iconBounce 2s ease-in-out infinite;
    }

    @keyframes iconBounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .metric-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1;
    }

    .metric-description {
        color: #718096;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .metric-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-healthy {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }

    .status-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }

    .status-danger {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }

    /* 图表容器 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
        border-top: 4px solid transparent;
        border-image: linear-gradient(90deg, #667eea, #764ba2, #81ecec, #74b9ff) 1;
    }

    .chart-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1.5rem;
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 洞察汇总区域 */
    .insight-summary {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border-left: 4px solid #667eea;
        position: relative;
    }

    .insight-summary::before {
        content: '💡';
        position: absolute;
        top: 1rem;
        left: 1rem;
        font-size: 1.5rem;
    }

    .insight-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0 0 0.5rem 2.5rem;
    }

    .insight-content {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-left: 2.5rem;
    }

    .insight-metrics {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }

    .insight-metric {
        background: rgba(255, 255, 255, 0.7);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #2d3748;
    }

    /* Streamlit特定样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 15px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: #4a5568;
        transition: all 0.3s ease;
        border: none;
        min-width: 180px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        color: #667eea;
        transform: translateY(-2px);
    }

    /* 隐藏plotly工具栏 */
    .modebar {
        display: none !important;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .page-title {
            font-size: 2rem;
        }

        .stTabs [data-baseweb="tab"] {
            min-width: auto;
            padding: 0.8rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """加载并处理Excel数据"""
    try:
        # 读取三个Excel文件
        customer_status = pd.read_excel('客户状态.xlsx')
        customer_sales = pd.read_excel('客户月度销售达成.xlsx')
        customer_targets = pd.read_excel('客户月度指标.xlsx')

        # 数据清洗和预处理
        customer_status.columns = ['客户名称', '状态']
        customer_sales.columns = ['订单日期', '发运月份', '经销商名称', '销售金额']
        customer_targets.columns = ['客户', '月度指标', '月份', '省份区域', '所属大区']

        # 数据类型转换
        customer_sales['销售金额'] = pd.to_numeric(customer_sales['销售金额'], errors='coerce')
        customer_targets['月度指标'] = pd.to_numeric(customer_targets['月度指标'], errors='coerce')

        # 处理日期
        customer_sales['订单日期'] = pd.to_datetime(customer_sales['订单日期'], errors='coerce')

        # 清洗无效数据
        customer_sales = customer_sales.dropna(subset=['销售金额'])
        customer_targets = customer_targets.dropna(subset=['月度指标'])

        return customer_status, customer_sales, customer_targets

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return generate_sample_data()


def generate_sample_data():
    """生成示例数据用于演示"""
    regions = ['华东', '华南', '华北', '西南', '华中', '东北']

    # 客户状态数据
    customer_status = pd.DataFrame({
        '客户名称': [f'客户{chr(65 + i)}' for i in range(175)],
        '状态': ['正常'] * 156 + ['闭户'] * 19
    })

    # 客户销售数据
    customer_sales = pd.DataFrame({
        '订单日期': pd.date_range('2024-01-01', periods=500, freq='D'),
        '发运月份': ['2025-01', '2025-02', '2025-03'] * 167,
        '经销商名称': np.random.choice([f'客户{chr(65 + i)}' for i in range(50)], 500),
        '销售金额': np.random.normal(50, 20, 500) * 10000
    })

    # 客户目标数据
    customer_targets = pd.DataFrame({
        '客户': [f'客户{chr(65 + i)}' for i in range(123)],
        '月度指标': np.random.normal(400, 150, 123) * 10000,
        '月份': ['2025-01'] * 123,
        '省份区域': np.random.choice(regions, 123),
        '所属大区': np.random.choice(['东', '南', '西', '北', '中'], 123)
    })

    return customer_status, customer_sales, customer_targets


def analyze_customer_data(customer_status, customer_sales, customer_targets):
    """全面分析客户数据并生成动态洞察"""
    analysis_results = {}

    # 1. 客户健康分析
    total_customers = len(customer_status)
    normal_customers = len(customer_status[customer_status['状态'] == '正常'])
    closed_customers = len(customer_status[customer_status['状态'] == '闭户'])
    health_rate = (normal_customers / total_customers) * 100

    # 2. 销售规模分析
    total_sales = customer_sales['销售金额'].sum() / 10000  # 转换为万元
    avg_customer_contribution = total_sales / total_customers

    # 3. 客户贡献度分析
    customer_contribution = customer_sales.groupby('经销商名称')['销售金额'].sum().sort_values(ascending=False)
    max_dependency = (customer_contribution.iloc[0] / customer_contribution.sum()) * 100
    top5_dependency = (customer_contribution.head(5).sum() / customer_contribution.sum()) * 100

    # 4. 区域分析
    # 合并区域信息
    sales_with_region = customer_sales.merge(
        customer_targets[['客户', '省份区域', '所属大区']].drop_duplicates(),
        left_on='经销商名称',
        right_on='客户',
        how='left'
    )

    regional_sales = sales_with_region.groupby('省份区域')['销售金额'].sum().sort_values(ascending=False)
    regional_customers = sales_with_region.groupby('省份区域')['经销商名称'].nunique()

    # 计算区域客户健康度
    region_health = {}
    for region in regional_sales.index:
        region_customers_list = sales_with_region[sales_with_region['省份区域'] == region]['经销商名称'].unique()
        region_status = customer_status[customer_status['客户名称'].isin(region_customers_list)]
        if len(region_status) > 0:
            region_normal = len(region_status[region_status['状态'] == '正常'])
            region_total = len(region_status)
            region_health[region] = (region_normal / region_total) * 100
        else:
            region_health[region] = 0

    # 5. 目标达成分析
    # 计算实际达成情况
    actual_sales_by_customer = customer_sales.groupby('经销商名称')['销售金额'].sum()

    # 合并目标和实际销售
    target_vs_actual = customer_targets.merge(
        actual_sales_by_customer.reset_index(),
        left_on='客户',
        right_on='经销商名称',
        how='left'
    )
    target_vs_actual['销售金额'] = target_vs_actual['销售金额'].fillna(0)
    target_vs_actual['达成率'] = (target_vs_actual['销售金额'] / target_vs_actual['月度指标']) * 100

    # 总体目标达成率
    total_target = target_vs_actual['月度指标'].sum()
    total_actual = target_vs_actual['销售金额'].sum()
    overall_achievement = (total_actual / total_target) * 100 if total_target > 0 else 0

    # 分类客户达成情况
    achievement_analysis = {
        'excellent': len(target_vs_actual[target_vs_actual['达成率'] >= 120]),  # 超额达成
        'good': len(target_vs_actual[(target_vs_actual['达成率'] >= 100) & (target_vs_actual['达成率'] < 120)]),  # 达标优秀
        'near': len(target_vs_actual[(target_vs_actual['达成率'] >= 80) & (target_vs_actual['达成率'] < 100)]),  # 接近达成
        'need_support': len(target_vs_actual[(target_vs_actual['达成率'] >= 60) & (target_vs_actual['达成率'] < 80)]),
        # 需要支持
        'critical': len(target_vs_actual[target_vs_actual['达成率'] < 60])  # 重点关注
    }

    # 6. 客户价值分析 (基于RFM模型)
    rfm_analysis = calculate_rfm_analysis(customer_sales)

    # 7. 风险等级评估
    risk_assessment = assess_business_risks(max_dependency, top5_dependency, health_rate, overall_achievement)

    # 整合分析结果
    analysis_results = {
        # 基础指标
        'total_customers': total_customers,
        'normal_customers': normal_customers,
        'closed_customers': closed_customers,
        'health_rate': health_rate,
        'total_sales': total_sales,
        'avg_contribution': avg_customer_contribution,

        # 依赖度风险
        'max_dependency': max_dependency,
        'top5_dependency': top5_dependency,
        'max_customer': customer_contribution.index[0],
        'max_customer_sales': customer_contribution.iloc[0] / 10000,

        # 区域分析
        'regional_sales': regional_sales / 10000,  # 转万元
        'regional_customers': regional_customers,
        'region_health': region_health,
        'top_region': regional_sales.index[0],
        'weakest_region': min(region_health.keys(), key=lambda x: region_health[x]),

        # 目标达成
        'overall_achievement': overall_achievement,
        'achievement_analysis': achievement_analysis,
        'target_vs_actual': target_vs_actual,

        # 客户价值
        'rfm_analysis': rfm_analysis,

        # 风险评估
        'risk_assessment': risk_assessment,

        # 客户贡献排名
        'customer_contribution': customer_contribution / 10000  # 转万元
    }

    return analysis_results


def calculate_rfm_analysis(customer_sales):
    """计算RFM客户价值分析"""
    # 计算最近购买日期作为参考点
    reference_date = customer_sales['订单日期'].max()

    # 按客户聚合RFM指标
    rfm = customer_sales.groupby('经销商名称').agg({
        '订单日期': ['max', 'count'],  # 最近购买日期和频次
        '销售金额': 'sum'  # 总金额
    }).round(2)

    # 展平列名
    rfm.columns = ['最近购买日期', '购买频次', '总金额']

    # 计算距今天数
    rfm['距今天数'] = (reference_date - rfm['最近购买日期']).dt.days

    # RFM评分 (1-5分制)
    rfm['R评分'] = pd.qcut(rfm['距今天数'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
    rfm['F评分'] = pd.qcut(rfm['购买频次'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M评分'] = pd.qcut(rfm['总金额'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

    # 转换为数值
    rfm['R评分'] = rfm['R评分'].astype(int)
    rfm['F评分'] = rfm['F评分'].astype(int)
    rfm['M评分'] = rfm['M评分'].astype(int)

    # 综合评分
    rfm['RFM综合评分'] = rfm['R评分'] + rfm['F评分'] + rfm['M评分']

    # 客户分层
    def categorize_customer(row):
        if row['RFM综合评分'] >= 13:
            return '钻石客户'
        elif row['RFM综合评分'] >= 11:
            return '黄金客户'
        elif row['RFM综合评分'] >= 8:
            return '白银客户'
        elif row['R评分'] >= 3:
            return '潜力客户'
        else:
            return '流失风险'

    rfm['客户类别'] = rfm.apply(categorize_customer, axis=1)

    # 统计各类别数量
    category_counts = rfm['客户类别'].value_counts()

    # 计算平均CLV (简化版本)
    category_clv = rfm.groupby('客户类别')['总金额'].mean() / 10000  # 转万元

    return {
        'rfm_data': rfm,
        'category_counts': category_counts,
        'category_clv': category_clv
    }


def assess_business_risks(max_dependency, top5_dependency, health_rate, achievement_rate):
    """评估业务风险等级"""
    risks = []
    risk_level = '低风险'

    # 客户依赖风险
    if max_dependency > 40:
        risks.append('单一客户依赖过高')
        risk_level = '高风险'
    elif max_dependency > 25:
        risks.append('单一客户依赖较高')
        risk_level = '中风险' if risk_level != '高风险' else risk_level

    # 客户集中度风险
    if top5_dependency > 70:
        risks.append('TOP5客户过度集中')
        risk_level = '高风险'
    elif top5_dependency > 60:
        risks.append('客户集中度偏高')
        risk_level = '中风险' if risk_level != '高风险' else risk_level

    # 客户健康风险
    if health_rate < 80:
        risks.append('客户流失率过高')
        risk_level = '高风险'
    elif health_rate < 90:
        risks.append('需关注客户健康度')
        risk_level = '中风险' if risk_level != '高风险' else risk_level

    # 目标达成风险
    if achievement_rate < 70:
        risks.append('目标达成严重不足')
        risk_level = '高风险'
    elif achievement_rate < 85:
        risks.append('目标达成需要改进')
        risk_level = '中风险' if risk_level != '高风险' else risk_level

    return {
        'risk_level': risk_level,
        'risk_factors': risks,
        'risk_score': len(risks)
    }


def generate_dynamic_insights(analysis_results):
    """根据分析结果生成动态洞察"""
    insights = {}

    # 健康度洞察
    health_rate = analysis_results['health_rate']
    if health_rate >= 95:
        health_insight = f"客户健康度极佳，{health_rate:.1f}%的正常客户比例远超行业标准。客户关系稳定，流失风险极低。"
        health_status = "优秀状态"
        health_class = "status-healthy"
    elif health_rate >= 90:
        health_insight = f"客户健康度良好，{health_rate:.1f}%的正常客户比例超过行业标准(85%)。客户关系基本稳定。"
        health_status = "健康状态"
        health_class = "status-healthy"
    elif health_rate >= 80:
        health_insight = f"客户健康度一般，{health_rate:.1f}%的正常客户比例接近行业标准。需要关注客户关系维护。"
        health_status = "需要关注"
        health_class = "status-warning"
    else:
        health_insight = f"客户健康度偏低，{health_rate:.1f}%的正常客户比例低于行业标准。存在较高的客户流失风险。"
        health_status = "风险状态"
        health_class = "status-danger"

    # 依赖度风险洞察
    max_dependency = analysis_results['max_dependency']
    max_customer = analysis_results['max_customer']
    if max_dependency >= 40:
        dependency_insight = f"存在严重的客户依赖风险，{max_customer}占总销售额的{max_dependency:.1f}%，远超30%的安全阈值。急需制定客户分散化策略。"
        dependency_status = "高风险"
        dependency_class = "status-danger"
    elif max_dependency >= 25:
        dependency_insight = f"存在一定的客户依赖风险，{max_customer}占总销售额的{max_dependency:.1f}%，超过25%的建议阈值。建议逐步降低依赖度。"
        dependency_status = "中等风险"
        dependency_class = "status-warning"
    else:
        dependency_insight = f"客户依赖度控制良好，{max_customer}占总销售额的{max_dependency:.1f}%，在安全范围内。客户结构相对均衡。"
        dependency_status = "低风险"
        dependency_class = "status-healthy"

    # 目标达成洞察
    achievement = analysis_results['overall_achievement']
    if achievement >= 100:
        achievement_insight = f"目标达成优异，整体达成率{achievement:.1f}%，超额完成预定目标。团队执行力强。"
        achievement_status = "超额完成"
        achievement_class = "status-healthy"
    elif achievement >= 85:
        achievement_insight = f"目标达成良好，整体达成率{achievement:.1f}%，基本完成预定目标。"
        achievement_status = "基本达成"
        achievement_class = "status-healthy"
    elif achievement >= 70:
        achievement_insight = f"目标达成一般，整体达成率{achievement:.1f}%，存在一定差距。需要加强执行和管理。"
        achievement_status = "需要改进"
        achievement_class = "status-warning"
    else:
        achievement_insight = f"目标达成不足，整体达成率{achievement:.1f}%，存在较大差距。需要重点关注和改进。"
        achievement_status = "严重不足"
        achievement_class = "status-danger"

    # 价值分层洞察
    rfm_counts = analysis_results['rfm_analysis']['category_counts']
    total_customers = analysis_results['total_customers']
    high_value_count = rfm_counts.get('钻石客户', 0) + rfm_counts.get('黄金客户', 0)
    high_value_rate = (high_value_count / total_customers) * 100

    if high_value_rate >= 30:
        value_insight = f"客户价值结构优秀，高价值客户占比{high_value_rate:.1f}%，超过行业标准(25%)。客户质量较高。"
        value_status = "结构优秀"
        value_class = "status-healthy"
    elif high_value_rate >= 20:
        value_insight = f"客户价值结构良好，高价值客户占比{high_value_rate:.1f}%，接近行业标准。仍有提升空间。"
        value_status = "结构良好"
        value_class = "status-healthy"
    else:
        value_insight = f"客户价值结构有待优化，高价值客户占比{high_value_rate:.1f}%，低于行业标准(25%)。需要重点培育和维护高价值客户。"
        value_status = "需要优化"
        value_class = "status-warning"

    insights = {
        'health': {
            'insight': health_insight,
            'status': health_status,
            'class': health_class,
            'rate': health_rate
        },
        'dependency': {
            'insight': dependency_insight,
            'status': dependency_status,
            'class': dependency_class,
            'rate': max_dependency
        },
        'achievement': {
            'insight': achievement_insight,
            'status': achievement_status,
            'class': achievement_class,
            'rate': achievement
        },
        'value': {
            'insight': value_insight,
            'status': value_status,
            'class': value_class,
            'rate': high_value_rate
        }
    }

    return insights


def create_dynamic_donut_chart(normal_customers, closed_customers):
    """创建动态环形图"""
    fig = go.Figure(data=[go.Pie(
        labels=['正常客户', '闭户客户'],
        values=[normal_customers, closed_customers],
        hole=0.6,
        marker_colors=['#667eea', '#ef4444'],
        textinfo='label+percent',
        textfont_size=14,
        showlegend=True
    )])

    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )

    return fig


def create_dynamic_regional_health_chart(region_health, regional_customers):
    """创建动态区域健康度图表"""
    regions = list(region_health.keys())
    health_rates = [region_health[region] for region in regions]
    customer_counts = [regional_customers.get(region, 0) for region in regions]

    # 计算闭户客户数（基于健康度推算）
    closed_counts = [int(customer_counts[i] * (100 - health_rates[i]) / 100) for i in range(len(regions))]
    normal_counts = [customer_counts[i] - closed_counts[i] for i in range(len(regions))]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='正常客户',
        x=regions,
        y=normal_counts,
        marker_color='#667eea',
        text=normal_counts,
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        name='闭户客户',
        x=regions,
        y=closed_counts,
        marker_color='#ef4444',
        text=closed_counts,
        textposition='auto'
    ))

    fig.update_layout(
        height=400,
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )

    return fig


def create_dynamic_risk_bubble_chart(analysis_results):
    """创建动态风险气泡图"""
    regional_sales = analysis_results['regional_sales']
    regional_customers = analysis_results['regional_customers']

    # 计算每个区域的最大客户依赖度（简化计算）
    regions = list(regional_sales.index)
    sales_values = list(regional_sales.values)
    customer_counts = [regional_customers.get(region, 1) for region in regions]

    # 模拟区域内客户依赖度（基于销售额分布）
    dependency_rates = []
    for i, region in enumerate(regions):
        # 假设最大客户占该区域销售额的比例与区域总体集中度相关
        region_concentration = min(80, 40 + (sales_values[i] / sum(sales_values)) * 100)
        dependency_rates.append(region_concentration)

    # 定义风险等级颜色
    colors = []
    for dep in dependency_rates:
        if dep >= 50:
            colors.append('#ef4444')  # 高风险
        elif dep >= 35:
            colors.append('#f59e0b')  # 中风险
        else:
            colors.append('#667eea')  # 低风险

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sales_values,
        y=dependency_rates,
        mode='markers',
        marker=dict(
            size=[c * 2 for c in customer_counts],  # 根据客户数量调整大小
            color=colors,
            opacity=0.7,
            line=dict(width=2, color='white'),
            sizemode='diameter',
            sizeref=2,
            sizemin=10
        ),
        text=regions,
        textposition='middle center',
        textfont=dict(color='white', size=12, family='Inter'),
        hovertemplate='<b>%{text}</b><br>' +
                      '销售额: %{x:.0f}万元<br>' +
                      '依赖度: %{y:.1f}%<br>' +
                      '客户数: %{marker.size}家<extra></extra>'
    ))

    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        xaxis=dict(
            title='区域总销售额(万元)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title='最大客户依赖度(%)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        )
    )

    return fig


def create_dynamic_achievement_heatmap(analysis_results):
    """创建动态目标达成热力图"""
    region_health = analysis_results['region_health']
    target_vs_actual = analysis_results['target_vs_actual']

    # 按区域计算达成率
    region_achievement = target_vs_actual.groupby('省份区域')['达成率'].mean()

    regions = list(region_health.keys())
    normal_achievement = [region_health.get(region, 0) for region in regions]
    total_achievement = [region_achievement.get(region, 0) for region in regions]

    heatmap_data = [normal_achievement, total_achievement]

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=regions,
        y=['正常客户健康度', '目标达成率'],
        colorscale=[
            [0, '#ef4444'],
            [0.6, '#f59e0b'],
            [1, '#10b981']
        ],
        text=[[f'{val:.1f}%' for val in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        hoveronitemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>',
        zmin=0,
        zmax=100
    ))

    fig.update_layout(
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        xaxis=dict(side='top'),
        margin=dict(t=50, b=50, l=120, r=50)
    )

    return fig


def create_dynamic_rfm_scatter(rfm_analysis):
    """创建动态RFM散点图"""
    rfm_data = rfm_analysis['rfm_data']

    # 计算综合得分用于散点图
    x_score = rfm_data['F评分'] * rfm_data['M评分'] / 5  # 频次×价值
    y_score = rfm_data['R评分'] * (rfm_data['F评分'] + rfm_data['M评分']) / 10  # 最近度×忠诚度

    colors_map = {
        '钻石客户': '#9333ea',
        '黄金客户': '#f59e0b',
        '白银客户': '#9ca3af',
        '潜力客户': '#10b981',
        '流失风险': '#ef4444'
    }

    fig = go.Figure()

    for category in rfm_data['客户类别'].unique():
        mask = rfm_data['客户类别'] == category
        fig.add_trace(go.Scatter(
            x=x_score[mask],
            y=y_score[mask],
            mode='markers',
            name=category,
            marker=dict(
                color=colors_map.get(category, '#667eea'),
                size=15,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            hovertemplate=f'<b>{category}</b><br>' +
                          'RFM得分 - 频次×价值: %{x:.1f}<br>' +
                          'RFM得分 - 最近度×忠诚度: %{y:.1f}<extra></extra>'
        ))

    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        xaxis=dict(
            title='RFM综合得分 - 频次×价值',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title='RFM综合得分 - 最近度×忠诚度',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    return fig


def create_dynamic_pareto_chart(customer_contribution):
    """创建动态帕累托图"""
    # 取前10名客户
    top_customers = customer_contribution.head(10)

    # 计算累计占比
    total_sales = customer_contribution.sum()
    cumulative_pct = (top_customers.cumsum() / total_sales * 100).round(1)

    # 处理客户名称显示
    customer_names = [name[:6] + '...' if len(name) > 8 else name for name in top_customers.index]
    sales_values = top_customers.values.round(0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加柱状图
    fig.add_trace(
        go.Bar(
            x=customer_names,
            y=sales_values,
            name='销售额(万元)',
            marker_color='#667eea',
            text=[f'{s:.0f}万' for s in sales_values],
            textposition='auto'
        ),
        secondary_y=False,
    )

    # 添加累计百分比线
    fig.add_trace(
        go.Scatter(
            x=customer_names,
            y=cumulative_pct.values,
            mode='lines+markers',
            name='累计占比(%)',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8, color='#ef4444', line=dict(width=2, color='white'))
        ),
        secondary_y=True,
    )

    # 设置坐标轴
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title_text="销售额(万元)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(title_text="累计占比(%)", secondary_y=True, range=[0, 100])

    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    return fig


def create_gauge_chart(achievement_rate):
    """创建动态仪表盘图"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=achievement_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "目标达成率 (%)", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [None, 120]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 60], 'color': "#fee2e2"},
                {'range': [60, 80], 'color': "#fef3c7"},
                {'range': [80, 100], 'color': "#d1fae5"},
                {'range': [100, 120], 'color': "#dcfce7"}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12)
    )

    return fig


# 主函数
def main():
    # 页面标题
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">👥 客户依赖分析</h1>
        <p class="page-subtitle">深入洞察客户关系，识别业务风险，优化客户组合策略</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner('正在加载和分析数据...'):
        customer_status, customer_sales, customer_targets = load_data()
        analysis_results = analyze_customer_data(customer_status, customer_sales, customer_targets)
        insights = generate_dynamic_insights(analysis_results)

    # 标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 关键指标总览",
        "❤️ 客户健康分析",
        "⚠️ 区域风险分析",
        "🎯 目标达成分析",
        "💎 客户价值分析",
        "📈 销售规模分析"
    ])

    with tab1:
        # 关键指标总览 - 使用动态数据
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            health_insight = insights['health']
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">❤️</span>
                <h3 class="metric-title">客户健康指标</h3>
                <div class="metric-value">{health_insight['rate']:.1f}%</div>
                <p class="metric-description">
                    {health_insight['insight']}
                </p>
                <span class="metric-status {health_insight['class']}">{health_insight['status']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            dependency_insight = insights['dependency']
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">⚠️</span>
                <h3 class="metric-title">区域风险指标</h3>
                <div class="metric-value">{dependency_insight['rate']:.1f}%</div>
                <p class="metric-description">
                    {dependency_insight['insight']}
                </p>
                <span class="metric-status {dependency_insight['class']}">{dependency_insight['status']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            achievement_insight = insights['achievement']
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">🎯</span>
                <h3 class="metric-title">目标达成指标</h3>
                <div class="metric-value">{achievement_insight['rate']:.1f}%</div>
                <p class="metric-description">
                    {achievement_insight['insight']}
                </p>
                <span class="metric-status {achievement_insight['class']}">{achievement_insight['status']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            value_insight = insights['value']
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">💎</span>
                <h3 class="metric-title">客户价值指标</h3>
                <div class="metric-value">{value_insight['rate']:.1f}%</div>
                <p class="metric-description">
                    {value_insight['insight']}
                </p>
                <span class="metric-status {value_insight['class']}">{value_insight['status']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            # 计算增长率（简化版本，实际应该从历史数据计算）
            growth_rate = 12.4  # 这里可以从历史数据计算得出
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">📈</span>
                <h3 class="metric-title">销售规模指标</h3>
                <div class="metric-value">+{growth_rate}%</div>
                <p class="metric-description">
                    总销售额{analysis_results['total_sales']:.0f}万元，平均客户贡献{analysis_results['avg_contribution']:.1f}万元。业务规模稳步增长。
                </p>
                <span class="metric-status status-healthy">增长态势</span>
            </div>
            """, unsafe_allow_html=True)

        # 核心数据展示
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("总客户数", f"{analysis_results['total_customers']}家", "基于实际数据")
        with col2:
            st.metric("总销售额", f"{analysis_results['total_sales']:.0f}万", "所有客户贡献")
        with col3:
            st.metric("平均客户贡献", f"{analysis_results['avg_contribution']:.1f}万", "单客户平均")
        with col4:
            st.metric("覆盖区域", f"{len(analysis_results['regional_sales'])}个", "业务覆盖范围")
        with col5:
            st.metric("最大客户", f"{analysis_results['max_customer_sales']:.0f}万",
                      f"{analysis_results['max_customer']}")
        with col6:
            st.metric("风险等级", analysis_results['risk_assessment']['risk_level'],
                      f"{analysis_results['risk_assessment']['risk_score']}个风险因子")

    with tab2:
        # 客户健康分析
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">客户状态分布</h3>', unsafe_allow_html=True)
            fig_donut = create_dynamic_donut_chart(analysis_results['normal_customers'],
                                                   analysis_results['closed_customers'])
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

            # 动态生成洞察
            health_score = int(analysis_results['health_rate'])
            if health_score >= 90:
                benchmark = "超过行业标准"
                suggestion = "继续保持优秀的客户关系管理"
            else:
                benchmark = "需要提升至行业标准(85%)"
                suggestion = "重点关注客户流失原因分析"

            st.markdown(f"""
            <div class="insight-summary">
                <div class="insight-title">📈 健康度洞察</div>
                <div class="insight-content">
                    当前客户健康度{analysis_results['health_rate']:.1f}%，{benchmark}。{suggestion}。共有{analysis_results['closed_customers']}家闭户客户需要分析流失原因。
                </div>
                <div class="insight-metrics">
                    <span class="insight-metric">健康度评分: {health_score}分</span>
                    <span class="insight-metric">正常客户: {analysis_results['normal_customers']}家</span>
                    <span class="insight-metric">闭户客户: {analysis_results['closed_customers']}家</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">区域客户健康度分布</h3>', unsafe_allow_html=True)
            fig_bar = create_dynamic_regional_health_chart(analysis_results['region_health'],
                                                           analysis_results['regional_customers'])
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

            # 动态区域洞察
            best_region = max(analysis_results['region_health'].keys(),
                              key=lambda x: analysis_results['region_health'][x])
            worst_region = min(analysis_results['region_health'].keys(),
                               key=lambda x: analysis_results['region_health'][x])
            best_rate = analysis_results['region_health'][best_region]
            worst_rate = analysis_results['region_health'][worst_region]

            st.markdown(f"""
            <div class="insight-summary">
                <div class="insight-title">🏢 区域健康度分析</div>
                <div class="insight-content">
                    {best_region}健康度最高({best_rate:.1f}%)，{worst_region}相对较低({worst_rate:.1f}%)。建议重点关注{worst_region}的客户关系维护，同时在{best_region}扩大客户规模。
                </div>
                <div class="insight-metrics">
                    <span class="insight-metric">最佳区域: {best_region}({best_rate:.1f}%)</span>
                    <span class="insight-metric">待提升: {worst_region}({worst_rate:.1f}%)</span>
                    <span class="insight-metric">区域数量: {len(analysis_results['region_health'])}个</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        # 区域风险分析
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">区域风险气泡图</h3>', unsafe_allow_html=True)
        fig_bubble = create_dynamic_risk_bubble_chart(analysis_results)
        st.plotly_chart(fig_bubble, use_container_width=True, config={'displayModeBar': False})

        # 动态风险洞察
        top_region = analysis_results['top_region']
        top_region_sales = analysis_results['regional_sales'][top_region]
        risk_assessment = analysis_results['risk_assessment']

        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">⚠️ 风险集中度分析</div>
            <div class="insight-content">
                {top_region}为最大销售区域(销售额{top_region_sales:.0f}万元)，存在{analysis_results['max_dependency']:.1f}%的客户依赖度。当前风险等级为{risk_assessment['risk_level']}，主要风险因子包括：{', '.join(risk_assessment['risk_factors'])}。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">最大依赖度: {analysis_results['max_dependency']:.1f}%</span>
                <span class="insight-metric">TOP5集中度: {analysis_results['top5_dependency']:.1f}%</span>
                <span class="insight-metric">风险等级: {risk_assessment['risk_level']}</span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        # 目标达成分析
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">区域×客户健康度目标达成热力矩阵</h3>', unsafe_allow_html=True)
        fig_heatmap = create_dynamic_achievement_heatmap(analysis_results)
        st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

        # 目标达成详情
        achievement_analysis = analysis_results['achievement_analysis']
        total_target_customers = sum(achievement_analysis.values())

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">客户达成情况分布</h3>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🏆 超额达成", f"{achievement_analysis['excellent']}家", "≥120%")
                st.metric("🎯 接近达成", f"{achievement_analysis['near']}家", "80-99%")
                st.metric("🆘 重点关注", f"{achievement_analysis['critical']}家", "<60%")
            with col_b:
                st.metric("⭐ 达标优秀", f"{achievement_analysis['good']}家", "100-119%")
                st.metric("📢 需要支持", f"{achievement_analysis['need_support']}家", "60-79%")
                st.metric("📋 设定目标客户", f"{total_target_customers}家", "有明确目标")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">整体达成率仪表盘</h3>', unsafe_allow_html=True)
            fig_gauge = create_gauge_chart(analysis_results['overall_achievement'])
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # 动态达成洞察
        excellent_rate = (achievement_analysis['excellent'] / total_target_customers) * 100
        critical_rate = (achievement_analysis['critical'] / total_target_customers) * 100

        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">🎯 目标达成深度分析</div>
            <div class="insight-content">
                整体目标达成率{analysis_results['overall_achievement']:.1f}%，其中{excellent_rate:.1f}%的客户超额完成目标，但有{critical_rate:.1f}%的客户严重不达标。建议对{achievement_analysis['critical']}家重点关注客户制定专项支持计划。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">达成率: {analysis_results['overall_achievement']:.1f}%</span>
                <span class="insight-metric">优秀客户: {achievement_analysis['excellent']}家</span>
                <span class="insight-metric">风险客户: {achievement_analysis['critical']}家</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        # 客户价值分析
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">RFM客户价值分析</h3>', unsafe_allow_html=True)
            fig_rfm = create_dynamic_rfm_scatter(analysis_results['rfm_analysis'])
            st.plotly_chart(fig_rfm, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">客户价值金字塔分布</h3>', unsafe_allow_html=True)

            category_counts = analysis_results['rfm_analysis']['category_counts']
            category_clv = analysis_results['rfm_analysis']['category_clv']

            col_a, col_b = st.columns(2)
            with col_a:
                diamond_count = category_counts.get('钻石客户', 0)
                silver_count = category_counts.get('白银客户', 0)
                risk_count = category_counts.get('流失风险', 0)
                st.metric("💎 钻石客户", f"{diamond_count}家", f"平均CLV {category_clv.get('钻石客户', 0):.0f}万")
                st.metric("🥈 白银客户", f"{silver_count}家", f"平均CLV {category_clv.get('白银客户', 0):.0f}万")
                st.metric("⚠️ 流失风险", f"{risk_count}家", "需要挽回")
            with col_b:
                gold_count = category_counts.get('黄金客户', 0)
                potential_count = category_counts.get('潜力客户', 0)
                high_value_rate = insights['value']['rate']
                st.metric("🥇 黄金客户", f"{gold_count}家", f"平均CLV {category_clv.get('黄金客户', 0):.0f}万")
                st.metric("🌟 潜力客户", f"{potential_count}家", "成长机会")
                st.metric("💰 高价值占比", f"{high_value_rate:.1f}%", "钻石+黄金客户")

            st.markdown('</div>', unsafe_allow_html=True)

        # 动态价值洞察
        diamond_clv = category_clv.get('钻石客户', 0)
        silver_clv = category_clv.get('白银客户', 0)
        clv_ratio = diamond_clv / silver_clv if silver_clv > 0 else 0

        st.markdown(f"""
        <div class="insight-summary">
            <div class="insight-title">💰 价值分层洞察</div>
            <div class="insight-content">
                钻石客户平均CLV({diamond_clv:.0f}万)是白银客户({silver_clv:.0f}万)的{clv_ratio:.1f}倍，显示出明显的价值分层。{potential_count}家潜力客户是重要的增长机会，建议制定专门的培育计划将其转化为高价值客户。
            </div>
            <div class="insight-metrics">
                <span class="insight-metric">价值倍数: {clv_ratio:.1f}倍</span>
                <span class="insight-metric">潜力客户: {potential_count}家</span>
                <span class="insight-metric">流失风险: {risk_count}家</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab6:
        # 销售规模分析
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">客户贡献帕累托分析</h3>', unsafe_allow_html=True)
            fig_pareto = create_dynamic_pareto_chart(analysis_results['customer_contribution'])
            st.plotly_chart(fig_pareto, use_container_width=True, config={'displayModeBar': False})

            # 动态帕累托洞察
            top5_contribution = analysis_results['customer_contribution'].head(5).sum()
            total_contribution = analysis_results['customer_contribution'].sum()
            top5_pct = (top5_contribution / total_contribution) * 100

            st.markdown(f"""
            <div class="insight-summary">
                <div class="insight-title">📊 帕累托效应分析</div>
                <div class="insight-content">
                    TOP5客户贡献了总销售额的{top5_pct:.1f}%，符合帕累托法则。{analysis_results['max_customer']}贡献度最高({analysis_results['max_dependency']:.1f}%)，建议适度平衡发展其他客户以降低单一客户依赖风险。
                </div>
                <div class="insight-metrics">
                    <span class="insight-metric">TOP5贡献: {top5_pct:.1f}%</span>
                    <span class="insight-metric">最大客户: {analysis_results['max_dependency']:.1f}%</span>
                    <span class="insight-metric">客户总数: {len(analysis_results['customer_contribution'])}家</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">区域市场份额分析</h3>', unsafe_allow_html=True)

            regional_sales = analysis_results['regional_sales']
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(regional_sales.index),
                values=list(regional_sales.values),
                marker_colors=['#667eea', '#f59e0b', '#10b981', '#ef4444', '#9333ea', '#9ca3af'],
                textinfo='label+percent',
                textfont_size=12,
                showlegend=True
            )])

            fig_pie.update_layout(
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

            # 动态区域洞察
            top_region_pct = (regional_sales.iloc[0] / regional_sales.sum()) * 100
            region_count = len(regional_sales)

            st.markdown(f"""
            <div class="insight-summary">
                <div class="insight-title">🏆 市场竞争力评估</div>
                <div class="insight-content">
                    {analysis_results['top_region']}保持市场领导地位，占总销售额的{top_region_pct:.1f}%。业务覆盖{region_count}个区域，市场布局相对均衡。建议在保持领先区域优势的同时，重点开发潜力区域。
                </div>
                <div class="insight-metrics">
                    <span class="insight-metric">领先区域: {analysis_results['top_region']} {top_region_pct:.1f}%</span>
                    <span class="insight-metric">覆盖区域: {region_count}个</span>
                    <span class="insight-metric">市场集中度: 适中</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()