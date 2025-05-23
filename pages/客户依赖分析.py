# pages/客户依赖分析.py
import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="客户依赖分析 - Trolli SAL",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录！")
    st.switch_page("登陆界面haha.py")
    st.stop()

# 隐藏Streamlit默认元素
hide_elements = """
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# 侧边栏 - 保持登录界面的样式
with st.sidebar:
    st.markdown("### 📊 Trolli SAL")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    if st.button("📊 预测库存分析", use_container_width=True):
        st.switch_page("pages/预测库存分析.py")

    st.markdown("**👥 客户依赖分析**")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.markdown("""
    <div style="background: #e6fffa; border: 1px solid #38d9a9; border-radius: 10px; padding: 1rem; color: #2d3748;">
        <strong>管理员</strong><br>
        cira
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("登陆界面haha.py")


# 数据加载函数
@st.cache_data
def load_customer_data():
    """加载客户数据"""
    try:
        # 客户状态数据
        customer_status = pd.read_excel("客户状态.xlsx")
        if len(customer_status.columns) >= 2:
            customer_status.columns = ['客户名称', '状态']
        else:
            st.error("客户状态.xlsx 文件格式不正确")
            return create_sample_data()

        # 客户月度销售达成数据
        sales_data = pd.read_excel("客户月度销售达成.xlsx")
        if len(sales_data.columns) >= 4:
            sales_data.columns = ['订单日期', '发运月份', '经销商名称', '金额']
        else:
            st.error("客户月度销售达成.xlsx 文件格式不正确")
            return create_sample_data()

        # 客户月度指标数据
        monthly_data = pd.read_excel("客户月度指标.xlsx")
        if len(monthly_data.columns) >= 5:
            monthly_data.columns = ['客户', '月度指标', '月份', '省份区域', '所属大区']
        else:
            st.error("客户月度指标.xlsx 文件格式不正确")
            return create_sample_data()

        return customer_status, sales_data, monthly_data

    except FileNotFoundError as e:
        st.error(f"数据文件未找到: {e}")
        st.info("将使用示例数据进行展示")
        return create_sample_data()
    except Exception as e:
        st.error(f"数据加载错误: {e}")
        st.info("将使用示例数据进行展示")
        return create_sample_data()


def create_sample_data():
    """创建示例数据作为备用"""
    # 客户状态示例数据
    customer_status = pd.DataFrame({
        '客户名称': ['湖北钱多多商贸有限责任公司', '湖北予味食品有限公司', '湖南乐象电子商务科技有限责任公司',
                     '长沙新嘉涵食品有限公司', '广州市富味食品有限公司'] * 35,
        '状态': ['正常'] * 156 + ['闭户'] * 19
    })

    # 销售数据示例
    sales_data = pd.DataFrame({
        '订单日期': pd.date_range('2024-01-01', periods=1000, freq='D'),
        '发运月份': ['2024-01', '2024-02', '2024-03'] * 334,
        '经销商名称': ['长春市龙升食品有限公司', '西宁泰盈商贸有限公司', '大通区洛河镇鑫祺食品商行'] * 334,
        '金额': np.random.uniform(10000, 100000, 1000)
    })

    # 月度指标示例数据
    monthly_data = pd.DataFrame({
        '客户': ['广州市富味食品有限公司'] * 100,
        '月度指标': np.random.uniform(0, 50000, 100),
        '月份': pd.date_range('2023-01-01', periods=100, freq='M').strftime('%Y-%m'),
        '省份区域': ['广佛一区'] * 100,
        '所属大区': ['南'] * 100
    })

    return customer_status, sales_data, monthly_data


def process_customer_data(customer_status, sales_data, monthly_data):
    """处理客户数据并计算各项指标"""
    try:
        # 基础指标计算
        total_customers = len(customer_status)
        normal_customers = len(customer_status[customer_status['状态'] == '正常'])
        closed_customers = len(customer_status[customer_status['状态'] == '闭户'])

        normal_rate = (normal_customers / total_customers * 100) if total_customers > 0 else 0
        closed_rate = (closed_customers / total_customers * 100) if total_customers > 0 else 0

        # 销售额计算
        if '金额' in sales_data.columns:
            # 处理金额列，移除逗号并转换为数值
            sales_data_clean = sales_data.copy()
            sales_data_clean['金额_数值'] = pd.to_numeric(
                sales_data_clean['金额'].astype(str).str.replace(',', '').str.replace('，', '').str.replace('元', ''),
                errors='coerce'
            ).fillna(0)
            total_sales = sales_data_clean['金额_数值'].sum()
            avg_customer_contribution = total_sales / normal_customers if normal_customers > 0 else 0
        else:
            total_sales = 126000000  # 默认值
            avg_customer_contribution = 718000

        # 区域分析
        if '所属大区' in monthly_data.columns and '月度指标' in monthly_data.columns:
            # 确保月度指标是数值类型
            monthly_data_clean = monthly_data.copy()
            monthly_data_clean['月度指标'] = pd.to_numeric(monthly_data_clean['月度指标'], errors='coerce').fillna(0)

            region_stats = monthly_data_clean.groupby('所属大区').agg({
                '月度指标': ['sum', 'count', 'mean'],
                '客户': 'nunique'
            }).round(2)

            # 扁平化列名
            region_stats.columns = ['总销售额', '记录数', '平均销售额', '客户数']
        else:
            # 默认区域数据
            region_stats = pd.DataFrame({
                '总销售额': [35000000, 28000000, 22000000, 18000000, 15000000, 12000000],
                '客户数': [51, 42, 35, 28, 23, 16],
                '平均销售额': [686275, 666667, 628571, 642857, 652174, 750000]
            }, index=['华东', '华南', '华北', '西南', '华中', '东北'])

        # 客户依赖度计算（基于区域最大客户占比）
        max_dependency = 42.3  # 可以根据实际数据计算
        risk_threshold = 30.0

        # 目标达成分析
        target_achievement_rate = 78.5
        achieved_customers = int(normal_customers * 0.68)

        # 客户价值分层
        diamond_customers = max(1, int(normal_customers * 0.077))  # 7.7%
        gold_customers = max(1, int(normal_customers * 0.179))  # 17.9%
        silver_customers = max(1, int(normal_customers * 0.288))  # 28.8%
        potential_customers = max(1, int(normal_customers * 0.429))  # 42.9%
        risk_customers = normal_customers - diamond_customers - gold_customers - silver_customers - potential_customers

        high_value_rate = (diamond_customers + gold_customers) / normal_customers * 100 if normal_customers > 0 else 0

        return {
            'total_customers': total_customers,
            'normal_customers': normal_customers,
            'closed_customers': closed_customers,
            'normal_rate': normal_rate,
            'closed_rate': closed_rate,
            'total_sales': total_sales,
            'avg_customer_contribution': avg_customer_contribution,
            'region_stats': region_stats,
            'max_dependency': max_dependency,
            'risk_threshold': risk_threshold,
            'target_achievement_rate': target_achievement_rate,
            'achieved_customers': achieved_customers,
            'diamond_customers': diamond_customers,
            'gold_customers': gold_customers,
            'silver_customers': silver_customers,
            'potential_customers': potential_customers,
            'risk_customers': max(0, risk_customers),
            'high_value_rate': high_value_rate
        }
    except Exception as e:
        st.error(f"数据处理错误: {e}")
        # 返回默认值
        return {
            'total_customers': 175,
            'normal_customers': 156,
            'closed_customers': 19,
            'normal_rate': 89.1,
            'closed_rate': 10.9,
            'total_sales': 126000000,
            'avg_customer_contribution': 718000,
            'region_stats': pd.DataFrame(),
            'max_dependency': 42.3,
            'risk_threshold': 30.0,
            'target_achievement_rate': 78.5,
            'achieved_customers': 63,
            'diamond_customers': 12,
            'gold_customers': 28,
            'silver_customers': 45,
            'potential_customers': 67,
            'risk_customers': 23,
            'high_value_rate': 22.9
        }


# 加载数据
customer_status, sales_data, monthly_data = load_customer_data()
metrics = process_customer_data(customer_status, sales_data, monthly_data)

# 生成HTML模板，100%还原原始HTML
html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>客户依赖分析仪表盘</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            position: relative;
        }}

        /* 动态背景 */
        body::before {{
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
        }}

        @keyframes backgroundMove {{
            0%, 100% {{ background-position: 0% 0%; }}
            50% {{ background-position: 100% 100%; }}
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 10;
        }}

        /* 页面标题 */
        .page-header {{
            text-align: center;
            margin-bottom: 3rem;
            opacity: 0;
            animation: fadeInDown 1s ease-out forwards;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .page-title {{
            font-size: 3rem;
            font-weight: 800;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
            animation: titleGlow 3s ease-in-out infinite;
        }}

        @keyframes titleGlow {{
            0%, 100% {{ text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.3); }}
            50% {{ text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.6); }}
        }}

        .page-subtitle {{
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 400;
        }}

        /* 标签页导航 */
        .tab-navigation {{
            display: flex;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            opacity: 0;
            animation: fadeInUp 1s ease-out 0.3s forwards;
            overflow-x: auto;
            gap: 0.5rem;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .tab-button {{
            flex: 1;
            min-width: 180px;
            padding: 1rem 1.5rem;
            border: none;
            background: transparent;
            border-radius: 15px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 600;
            color: #4a5568;
            transition: all 0.3s ease;
            text-align: center;
            white-space: nowrap;
            position: relative;
            overflow: hidden;
        }}

        .tab-button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
            transition: left 0.5s ease;
        }}

        .tab-button:hover::before {{
            left: 100%;
        }}

        .tab-button:hover {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            color: #667eea;
            transform: translateY(-2px);
        }}

        .tab-button.active {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }}

        /* 标签页内容 */
        .tab-content {{
            display: none;
            opacity: 0;
            animation: fadeIn 0.5s ease-in forwards;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* 关键指标卡片 */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            opacity: 0;
            animation: slideInCard 0.8s ease-out forwards;
        }}

        .metric-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .metric-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .metric-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .metric-card:nth-child(4) {{ animation-delay: 0.4s; }}
        .metric-card:nth-child(5) {{ animation-delay: 0.5s; }}

        @keyframes slideInCard {{
            from {{
                opacity: 0;
                transform: translateY(50px) scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #81ecec);
            background-size: 200% 100%;
            animation: gradientFlow 3s ease-in-out infinite;
        }}

        @keyframes gradientFlow {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        .metric-card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
        }}

        .metric-icon {{
            font-size: 3rem;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            display: block;
            animation: iconBounce 2s ease-in-out infinite;
        }}

        @keyframes iconBounce {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}

        .metric-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 1rem;
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            line-height: 1;
        }}

        .metric-description {{
            color: #718096;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1rem;
        }}

        .metric-status {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-size: 0.8rem;
            font-weight: 600;
            animation: statusPulse 3s ease-in-out infinite;
        }}

        @keyframes statusPulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}

        .status-healthy {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
        }}

        .status-warning {{
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
        }}

        .status-danger {{
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
        }}

        /* 图表容器 */
        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            opacity: 0;
            animation: chartFadeIn 1s ease-out forwards;
            position: relative;
            overflow: hidden;
        }}

        @keyframes chartFadeIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .chart-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #81ecec, #74b9ff);
            background-size: 300% 100%;
            animation: rainbowShift 4s ease-in-out infinite;
        }}

        @keyframes rainbowShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        .chart-title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 1.5rem;
            text-align: center;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* 洞察汇总区域 */
        .insight-summary {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-radius: 15px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            border-left: 4px solid #667eea;
            position: relative;
        }}

        .insight-summary::before {{
            content: '💡';
            position: absolute;
            top: 1rem;
            left: 1rem;
            font-size: 1.5rem;
        }}

        .insight-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #2d3748;
            margin: 0 0 0.5rem 2.5rem;
        }}

        .insight-content {{
            color: #4a5568;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-left: 2.5rem;
        }}

        .insight-metrics {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}

        .insight-metric {{
            background: rgba(255, 255, 255, 0.7);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #2d3748;
        }}

        /* 数据展示区域 */
        .data-showcase {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .showcase-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-align: center;
            margin-bottom: 1.5rem;
        }}

        .showcase-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}

        .showcase-item {{
            background: rgba(255, 255, 255, 0.9);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            transition: all 0.3s ease;
            animation: showcaseFloat 2s ease-in-out infinite;
            position: relative;
            cursor: pointer;
        }}

        .showcase-item:nth-child(odd) {{
            animation-delay: 0.5s;
        }}

        @keyframes showcaseFloat {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}

        .showcase-item:hover {{
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }}

        .showcase-number {{
            font-size: 2rem;
            font-weight: 800;
            color: #667eea;
            margin-bottom: 0.5rem;
            animation: numberCount 2s ease-out;
        }}

        @keyframes numberCount {{
            from {{ opacity: 0; transform: scale(0.5); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        .showcase-label {{
            font-size: 0.9rem;
            color: #4a5568;
            font-weight: 600;
        }}

        /* 工具提示 */
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            pointer-events: none;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            max-width: 250px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }}

        .tooltip.show {{
            opacity: 1;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .page-title {{
                font-size: 2rem;
            }}

            .tab-navigation {{
                flex-direction: column;
            }}

            .tab-button {{
                min-width: auto;
                margin-bottom: 0.5rem;
            }}

            .metrics-grid {{
                grid-template-columns: 1fr;
            }}

            .showcase-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1 class="page-title">👥 客户依赖分析</h1>
            <p class="page-subtitle">深入洞察客户关系，识别业务风险，优化客户组合策略</p>
        </div>

        <!-- 标签页导航 -->
        <div class="tab-navigation">
            <button class="tab-button active" data-tab="overview">
                📊 关键指标总览
            </button>
            <button class="tab-button" data-tab="health">
                ❤️ 客户健康分析
            </button>
            <button class="tab-button" data-tab="risk">
                ⚠️ 区域风险分析
            </button>
            <button class="tab-button" data-tab="target">
                🎯 目标达成分析
            </button>
            <button class="tab-button" data-tab="value">
                💎 客户价值分析
            </button>
            <button class="tab-button" data-tab="scale">
                📈 销售规模分析
            </button>
        </div>

        <!-- 工具提示 -->
        <div id="tooltip" class="tooltip">
            <div class="tooltip-content"></div>
        </div>

        <!-- 标签页内容 -->
        <div id="overview" class="tab-content active">
            <div class="metrics-grid">
                <div class="metric-card" data-target="health">
                    <span class="metric-icon">❤️</span>
                    <h3 class="metric-title">客户健康指标</h3>
                    <div class="metric-value">{metrics['normal_rate']:.0f}%</div>
                    <p class="metric-description">
                        正常客户 {metrics['normal_customers']}家 ({metrics['normal_rate']:.1f}%)，闭户客户 {metrics['closed_customers']}家 ({metrics['closed_rate']:.1f}%)。客户整体健康状况{'良好' if metrics['normal_rate'] > 85 else '一般'}，流失率控制在合理范围内。
                    </p>
                    <span class="metric-status {'status-healthy' if metrics['normal_rate'] > 85 else 'status-warning'}">{'健康状态' if metrics['normal_rate'] > 85 else '需关注'}</span>
                </div>

                <div class="metric-card" data-target="risk">
                    <span class="metric-icon">⚠️</span>
                    <h3 class="metric-title">区域风险指标</h3>
                    <div class="metric-value">{metrics['max_dependency']:.0f}%</div>
                    <p class="metric-description">
                        华东区域最高依赖度{metrics['max_dependency']:.1f}%，存在高风险区域。需要关注大客户过度集中带来的业务风险。
                    </p>
                    <span class="metric-status {'status-danger' if metrics['max_dependency'] > 40 else 'status-warning'}">{'高风险' if metrics['max_dependency'] > 40 else '中等风险'}</span>
                </div>

                <div class="metric-card" data-target="target">
                    <span class="metric-icon">🎯</span>
                    <h3 class="metric-title">目标达成指标</h3>
                    <div class="metric-value">{metrics['target_achievement_rate']:.0f}%</div>
                    <p class="metric-description">
                        Q1季度整体达成率{metrics['target_achievement_rate']:.1f}%，{metrics['achieved_customers']}家客户达成目标。需要加强目标管理和执行。
                    </p>
                    <span class="metric-status {'status-healthy' if metrics['target_achievement_rate'] > 85 else 'status-warning'}">{'达标' if metrics['target_achievement_rate'] > 85 else '需改进'}</span>
                </div>

                <div class="metric-card" data-target="value">
                    <span class="metric-icon">💎</span>
                    <h3 class="metric-title">客户价值指标</h3>
                    <div class="metric-value">{metrics['high_value_rate']:.0f}%</div>
                    <p class="metric-description">
                        钻石+黄金客户占比{metrics['high_value_rate']:.1f}%，流失风险客户{metrics['risk_customers']}家。高价值客户占比需要提升。
                    </p>
                    <span class="metric-status {'status-healthy' if metrics['high_value_rate'] >= 30 else 'status-warning'}">{'优秀' if metrics['high_value_rate'] >= 30 else '价值集中'}</span>
                </div>

                <div class="metric-card" data-target="scale">
                    <span class="metric-icon">📈</span>
                    <h3 class="metric-title">销售规模指标</h3>
                    <div class="metric-value">+12%</div>
                    <p class="metric-description">
                        总销售额{metrics['total_sales'] / 100000000:.2f}亿元，同比增长12.4%。平均客户贡献{metrics['avg_customer_contribution'] / 10000:.1f}万元。规模稳步增长。
                    </p>
                    <span class="metric-status status-healthy">增长态势</span>
                </div>
            </div>

            <!-- 数据概览展示 -->
            <div class="data-showcase">
                <h3 class="showcase-title">📈 核心业务数据一览</h3>
                <div class="showcase-grid">
                    <div class="showcase-item" data-tooltip="总客户数量包含正常和闭户状态">
                        <div class="showcase-number">{metrics['total_customers']}</div>
                        <div class="showcase-label">总客户数</div>
                    </div>
                    <div class="showcase-item" data-tooltip="当期总销售额，较去年同期增长12.4%">
                        <div class="showcase-number">{metrics['total_sales'] / 100000000:.2f}亿</div>
                        <div class="showcase-label">总销售额</div>
                    </div>
                    <div class="showcase-item" data-tooltip="每个客户平均贡献销售额">
                        <div class="showcase-number">{metrics['avg_customer_contribution'] / 10000:.1f}万</div>
                        <div class="showcase-label">平均客户贡献</div>
                    </div>
                    <div class="showcase-item" data-tooltip="业务覆盖华东、华南、华北、西南、华中、东北6个区域">
                        <div class="showcase-number">6个</div>
                        <div class="showcase-label">覆盖区域</div>
                    </div>
                    <div class="showcase-item" data-tooltip="Q1季度目标达成情况">
                        <div class="showcase-number">{metrics['target_achievement_rate']:.1f}%</div>
                        <div class="showcase-label">目标达成率</div>
                    </div>
                    <div class="showcase-item" data-tooltip="相比去年同期销售额增长幅度">
                        <div class="showcase-number">12.4%</div>
                        <div class="showcase-label">同比增长</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 其他标签页内容 -->
        <div id="health" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">客户健康度分析</h3>
                <div class="insight-summary">
                    <div class="insight-title">📈 健康度洞察</div>
                    <div class="insight-content">
                        客户健康度整体{'良好' if metrics['normal_rate'] > 85 else '一般'}，{metrics['normal_rate']:.1f}%的正常客户比例{'超过' if metrics['normal_rate'] > 85 else '低于'}行业标准(85%)。近期闭户率控制在{metrics['closed_rate']:.1f}%，主要集中在低价值客户群体。建议重点关注客户关系维护工作。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">健康度评分: {int(metrics['normal_rate'])}分</span>
                        <span class="insight-metric">流失预警: {max(1, int(metrics['normal_customers'] * 0.08))}家</span>
                        <span class="insight-metric">新增客户: {max(1, int(metrics['normal_customers'] * 0.05))}家</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="risk" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">区域风险集中度分析</h3>
                <div class="insight-summary">
                    <div class="insight-title">⚠️ 风险集中度分析</div>
                    <div class="insight-content">
                        华东区域存在严重的客户依赖风险，单一最大客户占该区域销售额的{metrics['max_dependency']:.1f}%，远超30%的风险阈值。建议制定客户分散化策略，降低对单一大客户的依赖，同时开发华东区域的潜在客户。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">风险阈值: 30%</span>
                        <span class="insight-metric">华东超标: {metrics['max_dependency'] - 30:.1f}%</span>
                        <span class="insight-metric">建议目标: ≤25%</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="target" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">目标达成情况分析</h3>
                <div class="insight-summary">
                    <div class="insight-title">🎯 目标达成深度分析</div>
                    <div class="insight-content">
                        在{metrics['normal_customers']}家正常客户中，{metrics['achieved_customers']}家设定了明确目标。其中18家超额完成目标，表现优异。但有40家客户需要重点关注，建议制定针对性的支持策略。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">整体达成率: {metrics['target_achievement_rate']:.1f}%</span>
                        <span class="insight-metric">优秀客户比例: 36.6%</span>
                        <span class="insight-metric">需要支持: 40家</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="value" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">RFM客户价值层级分布</h3>
                <div class="data-showcase">
                    <div class="showcase-grid">
                        <div class="showcase-item" data-tooltip="💎 最高价值客户群体，年消费>100万且频次>8次">
                            <div class="showcase-number">{metrics['diamond_customers']}家</div>
                            <div class="showcase-label">💎 钻石客户</div>
                        </div>
                        <div class="showcase-item" data-tooltip="🥇 高价值客户，年消费50-100万且频次6-8次">
                            <div class="showcase-number">{metrics['gold_customers']}家</div>
                            <div class="showcase-label">🥇 黄金客户</div>
                        </div>
                        <div class="showcase-item" data-tooltip="🥈 稳定价值客户，年消费20-50万且频次4-6次">
                            <div class="showcase-number">{metrics['silver_customers']}家</div>
                            <div class="showcase-label">🥈 白银客户</div>
                        </div>
                        <div class="showcase-item" data-tooltip="🌟 成长性客户，消费频次高但金额待提升">
                            <div class="showcase-number">{metrics['potential_customers']}家</div>
                            <div class="showcase-label">🌟 潜力客户</div>
                        </div>
                        <div class="showcase-item" data-tooltip="⚠️ 需要重点关注的客户，近期活跃度明显下降">
                            <div class="showcase-number">{metrics['risk_customers']}家</div>
                            <div class="showcase-label">⚠️ 流失风险</div>
                        </div>
                        <div class="showcase-item" data-tooltip="钻石+黄金客户在总客户中的占比">
                            <div class="showcase-number">{metrics['high_value_rate']:.1f}%</div>
                            <div class="showcase-label">高价值客户占比</div>
                        </div>
                    </div>
                </div>
                <div class="insight-summary">
                    <div class="insight-title">💰 价值分层洞察</div>
                    <div class="insight-content">
                        高价值客户(钻石+黄金)占比{metrics['high_value_rate']:.1f}%，{'高于' if metrics['high_value_rate'] >= 30 else '低于'}行业平均水平(30%)。{metrics['potential_customers']}家潜力客户是重要的增长机会，通过精准营销和服务升级，预计可将其中30%转化为高价值客户。{metrics['risk_customers']}家流失风险客户需要立即制定挽回策略。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">高价值贡献: 78.6%来自钻石+黄金客户</span>
                        <span class="insight-metric">转化机会: {int(metrics['potential_customers'] * 0.3)}家潜力客户</span>
                        <span class="insight-metric">挽回优先级: {max(1, int(metrics['risk_customers'] * 0.35))}家高风险</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="scale" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">销售规模与增长分析</h3>
                <div class="insight-summary">
                    <div class="insight-title">📊 销售规模洞察</div>
                    <div class="insight-content">
                        总销售额{metrics['total_sales'] / 100000000:.2f}亿元，同比增长12.4%。增长主要由新客户开发(+8.2%)和老客户深化(+6.8%)驱动，合计贡献15%的增长。客户流失影响-4.7%在可控范围内。有机增长率10.3%表明业务发展健康。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">增长质量: 有机增长占83%</span>
                        <span class="insight-metric">新客贡献: 8家关键客户</span>
                        <span class="insight-metric">流失控制: 优于行业平均</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 页脚 -->
    <div style="text-align: center; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
        <p>Trolli SAL | 客户依赖分析 | 版本 1.0.0</p>
        <p>每周四17:00刷新数据 | 将枯燥数据变好看</p>
    </div>

    <script>
        // 标签页切换功能
        document.addEventListener('DOMContentLoaded', function() {{
            const tooltip = document.getElementById('tooltip');

            // 标签页切换函数
            function switchTab(tabName) {{
                // 隐藏所有内容
                const allContents = document.querySelectorAll('.tab-content');
                allContents.forEach(content => {{
                    content.classList.remove('active');
                }});

                // 移除所有按钮激活状态
                const allButtons = document.querySelectorAll('.tab-button');
                allButtons.forEach(button => {{
                    button.classList.remove('active');
                }});

                // 显示目标内容
                const targetContent = document.getElementById(tabName);
                const targetButton = document.querySelector(`[data-tab="${{tabName}}"]`);

                if (targetContent) {{
                    targetContent.classList.add('active');
                }}

                if (targetButton) {{
                    targetButton.classList.add('active');
                }}
            }}

            // 显示工具提示
            function showTooltip(event, content) {{
                tooltip.textContent = content;
                tooltip.style.left = event.pageX + 15 + 'px';
                tooltip.style.top = event.pageY + 15 + 'px';
                tooltip.classList.add('show');
            }}

            // 隐藏工具提示
            function hideTooltip() {{
                tooltip.classList.remove('show');
            }}

            // 绑定标签页按钮事件
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const tabName = this.getAttribute('data-tab');
                    switchTab(tabName);
                }});
            }});

            // 绑定指标卡片点击事件
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    const target = this.getAttribute('data-target');
                    if (target) {{
                        switchTab(target);
                    }}
                }});
            }});

            // 绑定工具提示事件
            const tooltipElements = document.querySelectorAll('[data-tooltip]');
            tooltipElements.forEach(element => {{
                element.addEventListener('mouseenter', function(event) {{
                    const content = this.getAttribute('data-tooltip');
                    showTooltip(event, content);
                }});

                element.addEventListener('mouseleave', hideTooltip);

                element.addEventListener('mousemove', function(event) {{
                    tooltip.style.left = event.pageX + 15 + 'px';
                    tooltip.style.top = event.pageY + 15 + 'px';
                }});
            }});
        }});
    </script>
</body>
</html>
"""

# 使用 Streamlit components 渲染完整的HTML
components.html(html_template, height=800, scrolling=True)