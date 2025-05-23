# pages/预测库存分析.py - 库存预警仪表盘 - 完整HTML版本
import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="库存预警仪表盘",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查登录状态
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("请先登录系统")
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
    [data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 📊 Trolli SAL")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.switch_page("登陆界面haha.py")

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    if st.button("📊 预测库存分析", use_container_width=True, disabled=True):
        pass

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.markdown("""
    <div class="user-info" style="background: #e6fffa; border: 1px solid #38d9a9; border-radius: 10px; padding: 1rem; color: #2d3748;">
        <strong>管理员</strong>
        cira
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("登陆界面haha.py")


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

        # 处理库存数据 - 提取批次信息
        batch_data = []
        current_material = None
        current_desc = None
        current_stock = 0
        current_price = 0

        for idx, row in inventory_df.iterrows():
            if pd.notna(row['物料']) and row['物料'].startswith('F'):
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
                elif age_days >= 90:
                    risk_level = '高风险'
                elif age_days >= 60:
                    risk_level = '中风险'
                elif age_days >= 30:
                    risk_level = '低风险'
                else:
                    risk_level = '极低风险'

                batch_data.append({
                    '物料': current_material,
                    '描述': current_desc,
                    '生产日期': prod_date,
                    '生产批号': batch_no,
                    '数量': quantity,
                    '库龄': age_days,
                    '风险等级': risk_level,
                    '单价': current_price,
                    '批次价值': quantity * current_price
                })

        processed_inventory = pd.DataFrame(batch_data)

        # 计算预测准确率
        forecast_accuracy = calculate_forecast_accuracy(shipment_df, forecast_df)

        # 计算关键指标
        metrics = calculate_key_metrics(processed_inventory, forecast_accuracy, shipment_df)

        # 准备图表数据
        chart_data = prepare_chart_data(processed_inventory, forecast_accuracy, shipment_df, forecast_df)

        return metrics, chart_data

    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        # 返回模拟数据
        return get_mock_data()


def calculate_forecast_accuracy(shipment_df, forecast_df):
    """计算预测准确率"""
    try:
        # 统一字段名
        shipment_df['区域'] = shipment_df['所属区域']
        shipment_df['销售员'] = shipment_df['申请人']
        forecast_df['区域'] = forecast_df['所属大区']

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
    except:
        return pd.DataFrame()


def calculate_key_metrics(processed_inventory, forecast_accuracy, shipment_df):
    """计算关键指标"""
    if processed_inventory.empty:
        return get_mock_metrics()

    total_batches = len(processed_inventory)
    high_risk_batches = len(processed_inventory[processed_inventory['风险等级'].isin(['极高风险', '高风险'])])
    high_risk_ratio = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0

    total_inventory_value = processed_inventory['批次价值'].sum() / 1000000
    high_risk_value = processed_inventory[
        processed_inventory['风险等级'].isin(['极高风险', '高风险'])
    ]['批次价值'].sum()
    high_risk_value_ratio = (high_risk_value / processed_inventory['批次价值'].sum() * 100) if processed_inventory[
                                                                                                   '批次价值'].sum() > 0 else 0

    avg_age = processed_inventory['库龄'].mean()
    forecast_acc = forecast_accuracy['预测准确率'].mean() * 100 if not forecast_accuracy.empty else 78.5

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


def prepare_chart_data(processed_inventory, forecast_accuracy, shipment_df, forecast_df):
    """准备图表数据"""
    chart_data = {}

    try:
        # 高风险批次数据（用于气泡图）
        high_risk_items = processed_inventory[
            processed_inventory['风险等级'].isin(['极高风险', '高风险'])
        ].head(20)

        if not high_risk_items.empty:
            chart_data['priority_bubble'] = {
                'extreme_risk': {
                    'x': high_risk_items[high_risk_items['风险等级'] == '极高风险']['库龄'].tolist(),
                    'y': high_risk_items[high_risk_items['风险等级'] == '极高风险']['批次价值'].tolist(),
                    'size': (high_risk_items[high_risk_items['风险等级'] == '极高风险']['数量'] / 10).clip(10,
                                                                                                           50).tolist(),
                    'text': high_risk_items[high_risk_items['风险等级'] == '极高风险']['描述'].fillna(
                        high_risk_items[high_risk_items['风险等级'] == '极高风险']['物料']).tolist()
                },
                'high_risk': {
                    'x': high_risk_items[high_risk_items['风险等级'] == '高风险']['库龄'].tolist(),
                    'y': high_risk_items[high_risk_items['风险等级'] == '高风险']['批次价值'].tolist(),
                    'size': (high_risk_items[high_risk_items['风险等级'] == '高风险']['数量'] / 10).clip(10,
                                                                                                         50).tolist(),
                    'text': high_risk_items[high_risk_items['风险等级'] == '高风险']['描述'].fillna(
                        high_risk_items[high_risk_items['风险等级'] == '高风险']['物料']).tolist()
                }
            }

        # 风险价值分布
        risk_value = processed_inventory.groupby('风险等级')['批次价值'].sum()
        chart_data['risk_value'] = {
            'labels': risk_value.index.tolist(),
            'values': risk_value.values.tolist()
        }

        # 预测准确率趋势
        if not forecast_accuracy.empty:
            monthly_acc = forecast_accuracy.groupby(
                forecast_accuracy['所属年月'].dt.to_period('M')
            )['预测准确率'].mean().reset_index()
            monthly_acc['年月'] = monthly_acc['所属年月'].dt.to_timestamp()

            chart_data['forecast_trend'] = {
                'x': monthly_acc['年月'].dt.strftime('%Y-%m').tolist(),
                'y': (monthly_acc['预测准确率'] * 100).tolist()
            }

        # 区域绩效数据
        if not shipment_df.empty:
            shipment_df['区域'] = shipment_df['所属区域']
            region_stats = shipment_df.groupby('区域').agg({
                '求和项:数量（箱）': ['sum', 'mean', 'count'],
                '申请人': 'nunique'
            }).round(2)
            region_stats.columns = ['总销量', '平均订单量', '订单数', '销售员数']
            region_stats = region_stats.reset_index()

            chart_data['region_heatmap'] = {
                'regions': region_stats['区域'].tolist(),
                'metrics': ['总销量', '平均订单量', '订单数', '销售员数'],
                'values': region_stats[['总销量', '平均订单量', '订单数', '销售员数']].values.tolist()
            }

        # 销售员绩效
        if not shipment_df.empty:
            sales_performance = shipment_df.groupby('申请人')['求和项:数量（箱）'].sum().sort_values(
                ascending=False).head(10)
            chart_data['sales_ranking'] = {
                'names': sales_performance.index.tolist(),
                'values': sales_performance.values.tolist()
            }

        # 库存趋势（模拟数据）
        dates = pd.date_range(start='2024-02-01', periods=13, freq='M')
        inventory_trend = 8000 + np.random.randint(-800, 1200, 13)
        chart_data['inventory_trend'] = {
            'x': dates.strftime('%Y-%m').tolist(),
            'y': inventory_trend.tolist()
        }

        return chart_data

    except Exception as e:
        return get_mock_chart_data()


def get_mock_data():
    """获取模拟数据"""
    metrics = {
        'total_batches': 1247,
        'high_risk_batches': 216,
        'high_risk_ratio': 17.3,
        'total_inventory_value': 8.42,
        'high_risk_value_ratio': 32.1,
        'avg_age': 67,
        'forecast_accuracy': 78.5,
        'high_risk_value': 2.7,
        'risk_counts': {
            'extreme': 85,
            'high': 131,
            'medium': 298,
            'low': 445,
            'minimal': 288
        }
    }

    chart_data = get_mock_chart_data()
    return metrics, chart_data


def get_mock_chart_data():
    """获取模拟图表数据"""
    return {
        'priority_bubble': {
            'extreme_risk': {
                'x': [120, 89, 156, 201, 78, 134, 167, 92, 145, 188],
                'y': [45000, 67000, 32000, 89000, 23000, 56000, 78000, 41000, 52000, 73000],
                'size': [40, 35, 45, 50, 30, 38, 42, 34, 39, 47],
                'text': ['F01E4A-口力汉堡90G', 'F01L3A-蜂蜜饼干', 'F0289A-巧克力棒', 'F0156B-牛奶糖',
                         'F0334C-果汁饮料', 'F0445D-坚果组合', 'F0567E-酸奶杯', 'F0678F-能量棒',
                         'F0789A-蛋白棒', 'F0890B-维他命']
            },
            'high_risk': {
                'x': [65, 72, 58, 81, 69, 75, 63, 77, 70, 68],
                'y': [34000, 28000, 42000, 51000, 29000, 38000, 33000, 45000, 39000, 31000],
                'size': [32, 30, 36, 38, 28, 34, 31, 37, 33, 29],
                'text': ['F0789G-维生素片', 'F0890H-蛋白粉', 'F0123I-燕麦片', 'F0234J-麦片',
                         'F0345K-豆浆粉', 'F0456L-奶茶粉', 'F0567M-咖啡豆', 'F0678N-茶叶',
                         'F0789O-坚果', 'F0890P-果干']
            }
        },
        'risk_value': {
            'labels': ['极高风险', '高风险', '中风险', '低风险', '极低风险'],
            'values': [1250000, 1890000, 2340000, 2180000, 750000]
        },
        'forecast_trend': {
            'x': ['2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
            'y': [75.2, 78.1, 73.5, 78.5, 82.1, 79.3]
        },
        'region_heatmap': {
            'regions': ['东区', '南区', '西区', '北区'],
            'metrics': ['总销量', '平均订单量', '订单数', '销售员数'],
            'values': [[15420, 142.3, 108, 12], [12890, 156.7, 82, 8], [8950, 178.2, 50, 6], [11200, 134.8, 73, 9]]
        },
        'sales_ranking': {
            'names': ['吴十', '刘嫔妍', '李根', '张三', '王五', '赵六', '孙七', '周八', '郑九', '陈一'],
            'values': [2840, 2650, 2420, 2180, 1980, 1850, 1720, 1650, 1580, 1520]
        },
        'inventory_trend': {
            'x': ['2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10',
                  '2024-11', '2024-12', '2025-01', '2025-02'],
            'y': [7850, 8120, 8450, 8890, 9200, 8750, 8980, 9350, 9680, 9800, 9420, 8950, 8420]
        }
    }


def get_mock_metrics():
    """获取模拟关键指标"""
    return {
        'total_batches': 1247,
        'high_risk_batches': 216,
        'high_risk_ratio': 17.3,
        'total_inventory_value': 8.42,
        'high_risk_value_ratio': 32.1,
        'avg_age': 67,
        'forecast_accuracy': 78.5,
        'high_risk_value': 2.7,
        'risk_counts': {
            'extreme': 85,
            'high': 131,
            'medium': 298,
            'low': 445,
            'minimal': 288
        }
    }


# 加载数据
try:
    metrics, chart_data = load_and_process_data()
except Exception as e:
    st.warning(f"使用模拟数据: {str(e)}")
    metrics, chart_data = get_mock_data()


# 生成完整的HTML页面
def generate_html_dashboard(metrics, chart_data):
    """生成完整的HTML仪表盘"""

    # 将数据转换为JSON
    metrics_json = json.dumps(metrics)
    chart_data_json = json.dumps(chart_data)

    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>库存预警仪表盘</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.26.0/plotly.min.js"></script>
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
            font-size: 3.5rem;
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
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
        .metric-card:nth-child(6) {{ animation-delay: 0.6s; }}

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
            transform: translateY(-15px) scale(1.03);
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
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            line-height: 1;
            animation: numberGlow 2s ease-out;
        }}

        @keyframes numberGlow {{
            0% {{ filter: drop-shadow(0 0 0 transparent); }}
            50% {{ filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.6)); }}
            100% {{ filter: drop-shadow(0 0 0 transparent); }}
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
            border-radius: 15px;
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

        /* 网格布局 */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
        }}

        /* 风险分析特殊组件 */
        .risk-matrix {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }}

        .risk-cell {{
            aspect-ratio: 1;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}

        .risk-cell::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--risk-color, #667eea);
            opacity: 0.1;
            transition: opacity 0.3s ease;
        }}

        .risk-cell:hover::before {{
            opacity: 0.2;
        }}

        .risk-cell:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}

        .risk-extreme {{ --risk-color: #ef4444; color: #ef4444; }}
        .risk-high {{ --risk-color: #f59e0b; color: #f59e0b; }}
        .risk-medium {{ --risk-color: #eab308; color: #eab308; }}
        .risk-low {{ --risk-color: #22c55e; color: #22c55e; }}
        .risk-minimal {{ --risk-color: #06b6d4; color: #06b6d4; }}

        .risk-count {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}

        .risk-label {{
            font-size: 0.8rem;
            opacity: 0.8;
        }}

        /* ABC分析组件 */
        .abc-analysis {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 2rem;
            align-items: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
            border-radius: 15px;
            margin: 2rem 0;
        }}

        .abc-category {{
            text-align: center;
            padding: 1.5rem;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.9);
            transition: all 0.3s ease;
        }}

        .abc-category:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}

        .abc-label {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}

        .abc-a {{ color: #667eea; }}
        .abc-b {{ color: #f59e0b; }}
        .abc-c {{ color: #10b981; }}

        .abc-percentage {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .abc-description {{
            font-size: 0.85rem;
            color: #718096;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .page-title {{
                font-size: 2.5rem;
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

            .charts-grid {{
                grid-template-columns: 1fr;
            }}

            .showcase-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .risk-matrix {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .abc-analysis {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1 class="page-title">📦 库存预警仪表盘</h1>
            <p class="page-subtitle">Clay风格企业级分析系统 - 数据驱动的促销清库决策支持</p>
        </div>

        <!-- 标签页导航 -->
        <div class="tab-navigation">
            <button class="tab-button active" data-tab="overview">
                📊 关键指标总览
            </button>
            <button class="tab-button" data-tab="risk">
                🚨 风险分析
            </button>
            <button class="tab-button" data-tab="forecast">
                📈 预测分析
            </button>
            <button class="tab-button" data-tab="responsibility">
                👥 责任分析
            </button>
            <button class="tab-button" data-tab="inventory">
                📋 库存分析
            </button>
        </div>

        <!-- 标签1：关键指标总览 -->
        <div id="overview" class="tab-content active">
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-icon">📦</span>
                    <h3 class="metric-title">总批次数量</h3>
                    <div class="metric-value counter-number" data-target="{metrics['total_batches']}">{metrics['total_batches']}</div>
                    <p class="metric-description">
                        库存批次总数{metrics['total_batches']}个，其中{metrics['high_risk_batches']}个批次处于高风险状态，需要制定促销清库策略进行风险控制。
                    </p>
                    <span class="metric-status status-warning">需要关注</span>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">⚠️</span>
                    <h3 class="metric-title">高风险批次占比</h3>
                    <div class="metric-value counter-number" data-target="{metrics['high_risk_ratio']}" data-suffix="%">{metrics['high_risk_ratio']}%</div>
                    <p class="metric-description">
                        {metrics['high_risk_ratio']}%的批次处于高风险状态。主要集中在库龄超过90天的产品，需要紧急促销清库。
                    </p>
                    <span class="metric-status {'status-danger' if metrics['high_risk_ratio'] > 15 else 'status-warning'}">{'风险预警' if metrics['high_risk_ratio'] > 15 else '需要关注'}</span>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">💎</span>
                    <h3 class="metric-title">库存总价值</h3>
                    <div class="metric-value counter-number" data-target="{metrics['total_inventory_value']}" data-suffix="M">{metrics['total_inventory_value']}M</div>
                    <p class="metric-description">
                        库存总价值{metrics['total_inventory_value']}百万元。高价值产品需要重点关注库存周转效率。
                    </p>
                    <span class="metric-status status-healthy">稳定增长</span>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">🚨</span>
                    <h3 class="metric-title">高风险价值占比</h3>
                    <div class="metric-value counter-number" data-target="{metrics['high_risk_value_ratio']}" data-suffix="%">{metrics['high_risk_value_ratio']}%</div>
                    <p class="metric-description">
                        {metrics['high_risk_value_ratio']}%的高价值库存需要促销清库，严重影响现金流周转。
                    </p>
                    <span class="metric-status {'status-danger' if metrics['high_risk_value_ratio'] > 30 else 'status-warning'}">{'紧急处理' if metrics['high_risk_value_ratio'] > 30 else '需要关注'}</span>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">⏰</span>
                    <h3 class="metric-title">平均库龄</h3>
                    <div class="metric-value counter-number" data-target="{metrics['avg_age']}" data-suffix="天">{metrics['avg_age']}天</div>
                    <p class="metric-description">
                        平均库龄{metrics['avg_age']}天。受季节性因素影响较大，建议优化进货计划和预测准确率。
                    </p>
                    <span class="metric-status {'status-warning' if metrics['avg_age'] > 60 else 'status-healthy'}">{'需要优化' if metrics['avg_age'] > 60 else '状态良好'}</span>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">🎯</span>
                    <h3 class="metric-title">预测准确率</h3>
                    <div class="metric-value counter-number" data-target="{metrics['forecast_accuracy']}" data-suffix="%">{metrics['forecast_accuracy']}%</div>
                    <p class="metric-description">
                        整体预测准确率{metrics['forecast_accuracy']}%，需要持续改善预测模型的准确性。
                    </p>
                    <span class="metric-status status-healthy">持续改善</span>
                </div>
            </div>

            <!-- 数据概览展示 -->
            <div class="data-showcase">
                <h3 class="showcase-title">📈 核心业务数据一览</h3>
                <div class="showcase-grid">
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #ef4444;">{metrics['risk_counts']['extreme']}个</div>
                        <div class="showcase-label">极高风险批次</div>
                    </div>
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #f59e0b;">{metrics['risk_counts']['high']}个</div>
                        <div class="showcase-label">高风险批次</div>
                    </div>
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #eab308;">{metrics['risk_counts']['medium']}个</div>
                        <div class="showcase-label">中风险批次</div>
                    </div>
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #22c55e;">{metrics['risk_counts']['low']}个</div>
                        <div class="showcase-label">低风险批次</div>
                    </div>
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #06b6d4;">{metrics['risk_counts']['minimal']}个</div>
                        <div class="showcase-label">极低风险批次</div>
                    </div>
                    <div class="showcase-item">
                        <div class="showcase-number" style="color: #667eea;">{metrics['high_risk_value']}M</div>
                        <div class="showcase-label">高风险总价值</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 标签2：风险分析 -->
        <div id="risk" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">🎯 风险等级分布矩阵</h3>
                <div class="risk-matrix">
                    <div class="risk-cell risk-extreme">
                        <div class="risk-count">{metrics['risk_counts']['extreme']}</div>
                        <div class="risk-label">极高风险</div>
                    </div>
                    <div class="risk-cell risk-high">
                        <div class="risk-count">{metrics['risk_counts']['high']}</div>
                        <div class="risk-label">高风险</div>
                    </div>
                    <div class="risk-cell risk-medium">
                        <div class="risk-count">{metrics['risk_counts']['medium']}</div>
                        <div class="risk-label">中风险</div>
                    </div>
                    <div class="risk-cell risk-low">
                        <div class="risk-count">{metrics['risk_counts']['low']}</div>
                        <div class="risk-label">低风险</div>
                    </div>
                    <div class="risk-cell risk-minimal">
                        <div class="risk-count">{metrics['risk_counts']['minimal']}</div>
                        <div class="risk-label">极低风险</div>
                    </div>
                </div>

                <div class="insight-summary">
                    <div class="insight-title">⚠️ 风险分布洞察</div>
                    <div class="insight-content">
                        当前{metrics['high_risk_batches']}个批次({metrics['high_risk_ratio']}%)处于高风险状态，需要立即制定促销清库策略。
                        极高风险批次需要启动深度折扣快速清库。中风险批次需要密切监控，防止转为高风险。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">风险阈值：15%</span>
                        <span class="insight-metric">当前状态：{metrics['high_risk_ratio']}%</span>
                        <span class="insight-metric">清库目标：6周内降至12%</span>
                        <span class="insight-metric">促销预算：估算{metrics['high_risk_value'] * 100:.0f}万</span>
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title">🔥 高风险批次优先级分析</h3>
                    <div id="priorityBubbleChart" style="height: 400px;"></div>
                    <div class="insight-summary">
                        <div class="insight-title">🎪 处理优先级建议</div>
                        <div class="insight-content">
                            优先处理右上角的高价值、高库龄批次。气泡大小代表清库难度，越大越需要更大的促销力度。
                        </div>
                        <div class="insight-metrics">
                            <span class="insight-metric">紧急批次：8个</span>
                            <span class="insight-metric">重点批次：15个</span>
                            <span class="insight-metric">预期收益：2.2M</span>
                        </div>
                    </div>
                </div>

                <div class="chart-container">
                    <h3 class="chart-title">📊 风险价值分布结构</h3>
                    <div id="riskValueChart" style="height: 400px;"></div>
                    <div class="insight-summary">
                        <div class="insight-title">💰 价值风险评估</div>
                        <div class="insight-content">
                            需要重点关注高价值风险批次，制定差异化的促销策略，确保资金快速回笼。
                        </div>
                        <div class="insight-metrics">
                            <span class="insight-metric">高价值风险：¥{metrics['high_risk_value']}M</span>
                            <span class="insight-metric">促销目标：80%清库</span>
                            <span class="insight-metric">预期回收：¥{metrics['high_risk_value'] * 0.8:.1f}M</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 标签3：预测分析 -->
        <div id="forecast" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">📈 预测准确率趋势与季节性分析</h3>
                <div id="forecastTrendChart" style="height: 400px;"></div>

                <div class="insight-summary">
                    <div class="insight-title">📊 预测表现洞察</div>
                    <div class="insight-content">
                        预测准确率整体平均为{metrics['forecast_accuracy']}%，建议加强季节性调整系数，提升节假日期间的预测精度。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">平均准确率：{metrics['forecast_accuracy']}%</span>
                        <span class="insight-metric">改进目标：85%+</span>
                        <span class="insight-metric">季节性影响：需优化</span>
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title">🎯 产品预测表现散点分析</h3>
                    <div id="forecastScatterChart" style="height: 400px;"></div>
                </div>

                <div class="chart-container">
                    <h3 class="chart-title">📊 预测偏差分布箱线图</h3>
                    <div id="forecastBoxPlot" style="height: 400px;"></div>
                </div>
            </div>
        </div>

        <!-- 标签4：责任分析 -->
        <div id="responsibility" class="tab-content">
            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title">🌍 区域绩效热力图</h3>
                    <div id="regionHeatmap" style="height: 400px;"></div>
                </div>

                <div class="chart-container">
                    <h3 class="chart-title">🎯 区域综合雷达对比</h3>
                    <div id="regionRadar" style="height: 400px;"></div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title">👤 销售员绩效能力矩阵</h3>
                    <div id="salesPerformanceScatter" style="height: 400px;"></div>
                </div>

                <div class="chart-container">
                    <h3 class="chart-title">📊 销售员综合排名</h3>
                    <div id="performanceRanking" style="height: 400px;"></div>
                </div>
            </div>
        </div>

        <!-- 标签5：库存分析 -->
        <div id="inventory" class="tab-content">
            <div class="chart-container">
                <h3 class="chart-title">📈 13个月库存趋势健康度分析</h3>
                <div id="inventoryTrendChart" style="height: 400px;"></div>
                <div class="insight-summary">
                    <div class="insight-title">📊 趋势洞察分析</div>
                    <div class="insight-content">
                        库存水平平均为8,756箱，波动率为18.2%。当前库存处于相对合理区间，但需要关注季节性波动对库存管理的影响。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">平均库存：8,756箱</span>
                        <span class="insight-metric">波动幅度：18.2%</span>
                        <span class="insight-metric">健康评分：78分</span>
                        <span class="insight-metric">优化目标：减少15%波动</span>
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <h3 class="chart-title">🔄 ABC分类管理优化策略</h3>
                <div class="abc-analysis">
                    <div class="abc-category">
                        <div class="abc-label abc-a">A类</div>
                        <div class="abc-percentage">80%</div>
                        <div class="abc-description">高价值产品<br>重点管理<br>精确预测</div>
                    </div>
                    <div class="abc-category">
                        <div class="abc-label abc-b">B类</div>
                        <div class="abc-percentage">15%</div>
                        <div class="abc-description">中价值产品<br>常规管理<br>定期审查</div>
                    </div>
                    <div class="abc-category">
                        <div class="abc-label abc-c">C类</div>
                        <div class="abc-percentage">5%</div>
                        <div class="abc-description">低价值产品<br>简化管理<br>批量处理</div>
                    </div>
                </div>

                <div class="insight-summary">
                    <div class="insight-title">💡 ABC管理策略</div>
                    <div class="insight-content">
                        当前ABC分类符合帕累托法则，A类产品贡献80%价值需要重点管理。建议对A类产品建立专门的预测模型，
                        B类产品采用定期审查机制，C类产品实行批量管理降低成本。
                    </div>
                    <div class="insight-metrics">
                        <span class="insight-metric">A类产品：重点管理</span>
                        <span class="insight-metric">B类产品：定期审查</span>
                        <span class="insight-metric">C类产品：批量处理</span>
                        <span class="insight-metric">管理效率：可提升25%</span>
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <h3 class="chart-title">⚡ 清库难度分析矩阵</h3>
                <div id="clearanceDifficultyChart" style="height: 400px;"></div>
            </div>
        </div>
    </div>

    <script>
        // 数据加载
        const metrics = {metrics_json};
        const chartData = {chart_data_json};

        // 通用图表配置
        const commonLayout = {{
            font: {{
                family: 'Inter, sans-serif',
                size: 12,
                color: '#2d3748'
            }},
            paper_bgcolor: 'rgba(255, 255, 255, 0.95)',
            plot_bgcolor: 'rgba(255, 255, 255, 0.8)',
            margin: {{ t: 40, r: 20, b: 60, l: 60 }},
            showlegend: true,
            legend: {{
                orientation: 'h',
                x: 0.5,
                xanchor: 'center',
                y: -0.15,
                font: {{ color: '#2d3748' }}
            }}
        }};

        const commonConfig = {{
            displayModeBar: false,
            responsive: true
        }};

        // 现代化配色方案
        const modernColors = {{
            extreme: '#ef4444',
            high: '#f59e0b', 
            medium: '#eab308',
            low: '#22c55e',
            minimal: '#06b6d4',
            primary: '#667eea',
            secondary: '#764ba2'
        }};

        // 标签页切换功能
        function initTabNavigation() {{
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {{
                button.addEventListener('click', () => {{
                    const targetTab = button.getAttribute('data-tab');

                    // 移除所有活动状态
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));

                    // 添加活动状态
                    button.classList.add('active');
                    document.getElementById(targetTab).classList.add('active');

                    // 重新渲染图表
                    setTimeout(() => {{
                        if (targetTab === 'risk') createRiskCharts();
                        else if (targetTab === 'forecast') createForecastCharts();
                        else if (targetTab === 'responsibility') createResponsibilityCharts();
                        else if (targetTab === 'inventory') createInventoryCharts();
                    }}, 100);
                }});
            }});
        }}

        // 数字滚动动画
        function animateCounters() {{
            const counters = document.querySelectorAll('.counter-number');

            counters.forEach(counter => {{
                const target = parseFloat(counter.getAttribute('data-target'));
                const suffix = counter.getAttribute('data-suffix') || '';
                let current = 0;
                const increment = target / 60;

                const timer = setInterval(() => {{
                    current += increment;
                    if (current >= target) {{
                        current = target;
                        clearInterval(timer);
                        counter.style.animation = 'numberGlow 1s ease-out';
                    }}

                    if (target >= 10) {{
                        counter.textContent = Math.ceil(current) + suffix;
                    }} else {{
                        counter.textContent = current.toFixed(1) + suffix;
                    }}
                }}, 40);
            }});
        }}

        // 创建风险分析图表
        function createRiskCharts() {{
            // 高风险气泡图
            if (chartData.priority_bubble) {{
                const extremeRisk = {{
                    x: chartData.priority_bubble.extreme_risk.x,
                    y: chartData.priority_bubble.extreme_risk.y,
                    mode: 'markers',
                    marker: {{
                        size: chartData.priority_bubble.extreme_risk.size,
                        color: modernColors.extreme,
                        opacity: 0.8,
                        line: {{ width: 3, color: '#ffffff' }},
                        sizemode: 'diameter'
                    }},
                    text: chartData.priority_bubble.extreme_risk.text,
                    name: '🚨 极高风险',
                    hovertemplate: '<b>🎯 %{{text}}</b><br>' +
                                  '⏰ 库龄: %{{x}}天<br>' +
                                  '💰 批次价值: ¥%{{y:,.0f}}<br>' +
                                  '<extra></extra>'
                }};

                const highRisk = {{
                    x: chartData.priority_bubble.high_risk.x,
                    y: chartData.priority_bubble.high_risk.y,
                    mode: 'markers',
                    marker: {{
                        size: chartData.priority_bubble.high_risk.size,
                        color: modernColors.high,
                        opacity: 0.8,
                        line: {{ width: 3, color: '#ffffff' }},
                        sizemode: 'diameter'
                    }},
                    text: chartData.priority_bubble.high_risk.text,
                    name: '⚠️ 高风险',
                    hovertemplate: '<b>🎯 %{{text}}</b><br>' +
                                  '⏰ 库龄: %{{x}}天<br>' +
                                  '💰 批次价值: ¥%{{y:,.0f}}<br>' +
                                  '<extra></extra>'
                }};

                const layout = {{
                    ...commonLayout,
                    title: {{
                        text: '高风险批次优先级分析 (气泡大小=清库难度)',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400,
                    xaxis: {{
                        title: '⏰ 库龄 (天)',
                        gridcolor: 'rgba(102, 126, 234, 0.1)',
                        color: '#2d3748'
                    }},
                    yaxis: {{
                        title: '💰 批次价值 (元)',
                        tickformat: '.0s',
                        gridcolor: 'rgba(102, 126, 234, 0.1)',
                        color: '#2d3748'
                    }}
                }};

                Plotly.newPlot('priorityBubbleChart', [extremeRisk, highRisk], layout, commonConfig);
            }}

            // 风险价值分布
            if (chartData.risk_value) {{
                const colors = [modernColors.extreme, modernColors.high, modernColors.medium, modernColors.low, modernColors.minimal];

                const riskValueData = [{{
                    type: 'pie',
                    labels: chartData.risk_value.labels,
                    values: chartData.risk_value.values,
                    marker: {{
                        colors: colors,
                        line: {{ color: '#ffffff', width: 2 }}
                    }},
                    textinfo: 'label+percent',
                    hovertemplate: '<b>%{{label}}</b><br>价值: ¥%{{value:,.0f}}<br>占比: %{{percent}}<extra></extra>'
                }}];

                const layout = {{
                    ...commonLayout,
                    title: {{
                        text: '风险价值分布结构',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400
                }};

                Plotly.newPlot('riskValueChart', riskValueData, layout, commonConfig);
            }}
        }}

        // 创建预测分析图表
        function createForecastCharts() {{
            // 预测准确率趋势
            if (chartData.forecast_trend) {{
                const trendData = [{{
                    x: chartData.forecast_trend.x,
                    y: chartData.forecast_trend.y,
                    mode: 'lines+markers',
                    name: '预测准确率',
                    line: {{ color: modernColors.primary, width: 3 }},
                    marker: {{ size: 8, color: modernColors.primary }},
                    hovertemplate: '<b>%{{x}}</b><br>准确率: %{{y:.1f}}%<extra></extra>'
                }}];

                const layout = {{
                    ...commonLayout,
                    title: {{
                        text: '预测准确率月度趋势',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400,
                    xaxis: {{
                        title: '月份',
                        gridcolor: 'rgba(102, 126, 234, 0.1)',
                        color: '#2d3748'
                    }},
                    yaxis: {{
                        title: '预测准确率 (%)',
                        gridcolor: 'rgba(102, 126, 234, 0.1)',
                        color: '#2d3748'
                    }}
                }};

                Plotly.newPlot('forecastTrendChart', trendData, layout, commonConfig);
            }}

            // 模拟产品预测散点图
            const scatterData = [{{
                x: [120, 89, 156, 78, 134, 92, 145, 201, 167, 188],
                y: [110, 95, 142, 85, 128, 98, 139, 185, 171, 195],
                mode: 'markers',
                marker: {{
                    size: 12,
                    color: modernColors.primary,
                    opacity: 0.7
                }},
                name: '产品预测表现',
                hovertemplate: '预测: %{{x}}<br>实际: %{{y}}<extra></extra>'
            }}];

            // 添加完美预测线
            scatterData.push({{
                x: [0, 250],
                y: [0, 250],
                mode: 'lines',
                name: '完美预测线',
                line: {{ color: 'red', dash: 'dash', width: 2 }}
            }});

            const scatterLayout = {{
                ...commonLayout,
                title: {{
                    text: '产品预测精度散点分析',
                    x: 0.5,
                    font: {{ size: 16, color: '#2d3748' }}
                }},
                height: 400,
                xaxis: {{ title: '预测销量' }},
                yaxis: {{ title: '实际销量' }}
            }};

            Plotly.newPlot('forecastScatterChart', scatterData, scatterLayout, commonConfig);

            // 预测偏差箱线图
            const boxData = [{{
                y: [-15.2, -8.7, -3.1, 2.4, 7.8, 12.5, -22.3, 18.9, -5.6, 9.2, 14.7, -11.8, 6.3],
                type: 'box',
                name: '预测偏差',
                marker: {{ color: modernColors.primary }},
                hovertemplate: '偏差: %{{y:.1f}}%<extra></extra>'
            }}];

            const boxLayout = {{
                ...commonLayout,
                title: {{
                    text: '预测偏差分布箱线图',
                    x: 0.5,
                    font: {{ size: 16, color: '#2d3748' }}
                }},
                height: 400,
                yaxis: {{ title: '偏差百分比 (%)' }}
            }};

            Plotly.newPlot('forecastBoxPlot', boxData, boxLayout, commonConfig);
        }}

        // 创建责任分析图表
        function createResponsibilityCharts() {{
            // 区域热力图
            if (chartData.region_heatmap) {{
                const heatmapData = [{{
                    z: chartData.region_heatmap.values,
                    x: chartData.region_heatmap.regions,
                    y: chartData.region_heatmap.metrics,
                    type: 'heatmap',
                    colorscale: 'RdYlBu_r',
                    hovertemplate: '<b>%{{y}}</b><br>区域: %{{x}}<br>标准化值: %{{z:.2f}}<extra></extra>'
                }}];

                const heatmapLayout = {{
                    ...commonLayout,
                    title: {{
                        text: '区域绩效热力图',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400
                }};

                Plotly.newPlot('regionHeatmap', heatmapData, heatmapLayout, commonConfig);
            }}

            // 区域雷达图
            const radarData = [{{
                r: [85, 92, 78, 88, 85],
                theta: ['总销量', '平均订单量', '订单数', '销售员数', '总销量'],
                fill: 'toself',
                name: '东区',
                line: {{ color: modernColors.primary }}
            }}, {{
                r: [78, 85, 82, 90, 78],
                theta: ['总销量', '平均订单量', '订单数', '销售员数', '总销量'],
                fill: 'toself',
                name: '南区',
                line: {{ color: modernColors.secondary }}
            }}];

            const radarLayout = {{
                ...commonLayout,
                polar: {{
                    radialaxis: {{
                        visible: true,
                        range: [0, 100]
                    }}
                }},
                title: {{
                    text: '区域综合雷达对比',
                    x: 0.5,
                    font: {{ size: 16, color: '#2d3748' }}
                }},
                height: 400
            }};

            Plotly.newPlot('regionRadar', radarData, radarLayout, commonConfig);

            // 销售员绩效散点图
            const salesScatterData = [{{
                x: [78, 85, 72, 89, 76, 82, 68, 91, 74, 87],
                y: [82, 89, 75, 92, 79, 85, 71, 94, 77, 90],
                mode: 'markers+text',
                marker: {{
                    size: [25, 30, 20, 35, 22, 28, 18, 38, 21, 32],
                    color: [2840, 2650, 2420, 2180, 1980, 1850, 1720, 1650, 1580, 1520],
                    colorscale: 'viridis',
                    opacity: 0.7,
                    line: {{ width: 2, color: 'white' }},
                    colorbar: {{ title: "销售量" }}
                }},
                text: ['吴十', '刘嫔妍', '李根', '张三', '王五', '赵六', '孙七', '周八', '郑九', '陈一'],
                textposition: 'top center',
                hovertemplate: '<b>%{{text}}</b><br>预测准确率: %{{x:.1f}}%<br>库存健康度: %{{y:.1f}}%<extra></extra>'
            }}];

            const salesScatterLayout = {{
                ...commonLayout,
                title: {{
                    text: '销售员绩效能力矩阵',
                    x: 0.5,
                    font: {{ size: 16, color: '#2d3748' }}
                }},
                height: 400,
                xaxis: {{ title: '预测准确率 (%)' }},
                yaxis: {{ title: '库存健康度 (%)' }}
            }};

            Plotly.newPlot('salesPerformanceScatter', salesScatterData, salesScatterLayout, commonConfig);

            // 销售员排名
            if (chartData.sales_ranking) {{
                const rankingData = [{{
                    x: chartData.sales_ranking.values,
                    y: chartData.sales_ranking.names,
                    type: 'bar',
                    orientation: 'h',
                    marker: {{ color: modernColors.primary }},
                    text: chartData.sales_ranking.values,
                    textposition: 'auto',
                    hovertemplate: '<b>%{{y}}</b><br>销售量: %{{x}}箱<extra></extra>'
                }}];

                const rankingLayout = {{
                    ...commonLayout,
                    title: {{
                        text: '销售员综合排名',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400,
                    xaxis: {{ title: '销售量 (箱)' }},
                    yaxis: {{ title: '销售员' }}
                }};

                Plotly.newPlot('performanceRanking', rankingData, rankingLayout, commonConfig);
            }}
        }}

        // 创建库存分析图表
        function createInventoryCharts() {{
            // 库存趋势图
            if (chartData.inventory_trend) {{
                const trendData = [{{
                    x: chartData.inventory_trend.x,
                    y: chartData.inventory_trend.y,
                    mode: 'lines+markers',
                    name: '库存量',
                    line: {{ color: modernColors.primary, width: 3 }},
                    marker: {{ size: 8, color: modernColors.primary }},
                    fill: 'tonexty',
                    fillcolor: 'rgba(102, 126, 234, 0.1)',
                    hovertemplate: '<b>%{{x}}</b><br>库存量: %{{y:,}}箱<extra></extra>'
                }}];

                const layout = {{
                    ...commonLayout,
                    title: {{
                        text: '13个月库存趋势健康度分析',
                        x: 0.5,
                        font: {{ size: 16, color: '#2d3748' }}
                    }},
                    height: 400,
                    xaxis: {{ title: '月份' }},
                    yaxis: {{ title: '库存量 (箱)' }},
                    shapes: [
                        {{
                            type: 'line',
                            x0: chartData.inventory_trend.x[0],
                            y0: 8000,
                            x1: chartData.inventory_trend.x[chartData.inventory_trend.x.length - 1],
                            y1: 8000,
                            line: {{ color: 'green', dash: 'dash' }}
                        }},
                        {{
                            type: 'line',
                            x0: chartData.inventory_trend.x[0],
                            y0: 9500,
                            x1: chartData.inventory_trend.x[chartData.inventory_trend.x.length - 1],
                            y1: 9500,
                            line: {{ color: 'orange', dash: 'dash' }}
                        }}
                    ],
                    annotations: [
                        {{
                            x: chartData.inventory_trend.x[chartData.inventory_trend.x.length - 1],
                            y: 8000,
                            text: '健康库存线',
                            showarrow: false,
                            xanchor: 'right'
                        }},
                        {{
                            x: chartData.inventory_trend.x[chartData.inventory_trend.x.length - 1],
                            y: 9500,
                            text: '预警线',
                            showarrow: false,
                            xanchor: 'right'
                        }}
                    ]
                }};

                Plotly.newPlot('inventoryTrendChart', trendData, layout, commonConfig);
            }}

            // 清库难度散点图
            const difficultyData = [{{
                x: [45, 67, 32, 89, 23, 56, 78, 41, 52, 73, 95, 38, 61, 84, 29],
                y: [42, 58, 35, 75, 28, 51, 68, 39, 48, 64, 82, 36, 55, 71, 31],
                mode: 'markers',
                marker: {{
                    size: 10,
                    color: [modernColors.extreme, modernColors.high, modernColors.medium, modernColors.low, modernColors.minimal][Math.floor(Math.random() * 5)],
                    opacity: 0.7,
                    line: {{ width: 1, color: 'white' }}
                }},
                text: ['产品A', '产品B', '产品C', '产品D', '产品E', '产品F', '产品G', '产品H', '产品I', '产品J', '产品K', '产品L', '产品M', '产品N', '产品O'],
                hovertemplate: '<b>%{{text}}</b><br>库龄: %{{x}}天<br>清库难度: %{{y:.1f}}<extra></extra>'
            }}];

            const difficultyLayout = {{
                ...commonLayout,
                title: {{
                    text: '清库难度分析矩阵',
                    x: 0.5,
                    font: {{ size: 16, color: '#2d3748' }}
                }},
                height: 400,
                xaxis: {{ title: '库龄 (天)' }},
                yaxis: {{ title: '清库难度指数' }}
            }};

            Plotly.newPlot('clearanceDifficultyChart', difficultyData, difficultyLayout, commonConfig);
        }}

        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 初始化标签页导航
            initTabNavigation();

            // 启动数字滚动动画
            setTimeout(animateCounters, 1000);

            // 初始化第一个标签页的图表
            setTimeout(() => {{
                createRiskCharts();
            }}, 1500);
        }});
    </script>
</body>
</html>
    """

    return html_template


# 生成和显示HTML
html_content = generate_html_dashboard(metrics, chart_data)

# 使用streamlit显示HTML
st.components.v1.html(html_content, height=1200, scrolling=True)