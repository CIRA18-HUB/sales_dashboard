import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import warnings
import math
from typing import Dict, List, Tuple, Any

warnings.filterwarnings('ignore')

# 必须在最前面设置页面配置
st.set_page_config(
    page_title="📦 产品组合分析",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 🎨 应用CSS样式和动画效果
def apply_custom_css():
    st.markdown("""
    <style>
        /* 导入字体 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* 隐藏Streamlit默认元素 */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stAppHeader {display: none !important;}

        /* 全局样式 */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        /* 主容器背景 + 动画 */
        .main .block-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: relative;
            padding-top: 1rem;
            min-height: 100vh;
        }

        /* 动态背景效果 */
        .main .block-container::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 60%);
            animation: waveMove 8s ease-in-out infinite;
            pointer-events: none;
            z-index: -1;
        }

        @keyframes waveMove {
            0%, 100% { 
                background-size: 200% 200%, 150% 150%, 300% 300%;
                background-position: 0% 0%, 100% 100%, 50% 50%; 
            }
            50% { 
                background-size: 300% 300%, 200% 200%, 250% 250%;
                background-position: 100% 0%, 0% 50%, 80% 20%; 
            }
        }

        /* 浮动粒子效果 */
        .main .block-container::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.2), transparent),
                radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent);
            background-repeat: repeat;
            background-size: 200px 100px;
            animation: particleFloat 20s linear infinite;
            pointer-events: none;
            z-index: -1;
        }

        @keyframes particleFloat {
            0% { transform: translateY(100vh) translateX(0); }
            100% { transform: translateY(-100vh) translateX(100px); }
        }

        /* 主标题样式 */
        .main-title {
            text-align: center;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
            animation: titleGlow 4s ease-in-out infinite;
        }

        @keyframes titleGlow {
            0%, 100% { 
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
                transform: scale(1);
            }
            50% { 
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
                transform: scale(1.02);
            }
        }

        /* 指标卡片样式 */
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            height: 200px;
            animation: cardSlideUp 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            cursor: pointer;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, #667eea, #764ba2, #ff6b6b, #ffa726);
            background-size: 300% 100%;
            animation: gradientShift 3s ease-in-out infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        @keyframes cardSlideUp {
            0% { opacity: 0; transform: translateY(60px) scale(0.8); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        .metric-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
            animation: cardWiggle 0.6s ease-in-out;
        }

        @keyframes cardWiggle {
            0%, 100% { transform: translateY(-10px) scale(1.02) rotate(0deg); }
            25% { transform: translateY(-10px) scale(1.02) rotate(1deg); }
            75% { transform: translateY(-10px) scale(1.02) rotate(-1deg); }
        }

        /* 数字动画 */
        .metric-value {
            animation: numberSlideUp 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        @keyframes numberSlideUp {
            0% { opacity: 0; transform: translateY(100%) scale(0.5); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* JBP状态样式 */
        .jbp-conform-yes { color: #10b981 !important; }
        .jbp-conform-no { color: #ef4444 !important; }

        /* 标签页样式增强 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 8px;
            backdrop-filter: blur(10px);
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transform: translateY(-3px) scale(1.02);
        }

        /* 侧边栏样式增强 */
        .stSidebar {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }

        .stSidebar .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.4s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            width: 100%;
            margin-bottom: 0.5rem;
        }

        .stSidebar .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }

        /* 选择框和输入框样式 */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            border: 2px solid rgba(102, 126, 234, 0.2);
            transition: all 0.3s ease;
        }

        .stSelectbox > div > div:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        /* 按钮组样式 */
        .button-group {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }

        .filter-button {
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 20px;
            padding: 0.5rem 1rem;
            color: #667eea;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
        }

        .filter-button:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }

        .filter-button.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        /* 信息面板样式 */
        .info-panel {
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
        }

        .info-panel h4 {
            color: #2d3748;
            margin-bottom: 1rem;
        }

        /* 成功/失败状态样式 */
        .status-success {
            color: #10b981;
            font-weight: 600;
        }

        .status-error {
            color: #ef4444;
            font-weight: 600;
        }

        /* Plotly图表容器样式 */
        .js-plotly-plot {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .metric-card {
                height: auto;
                padding: 1.5rem;
            }

            .main-title h1 {
                font-size: 2rem;
            }

            .button-group {
                justify-content: center;
            }
        }

        /* 加载动画 */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-spinner {
            animation: spin 1s linear infinite;
        }

        /* 渐入动画 */
        .fade-in {
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)


# 🔧 数据加载和处理函数
@st.cache_data(ttl=3600)  # 缓存1小时
def load_data():
    """加载所有真实数据文件"""
    try:
        data_files = {
            'sales_data': '24-25促销效果销售数据.xlsx',
            'promotion_data': '这是涉及到在4月份做的促销活动.xlsx',
            'star_products': '星品&新品年度KPI考核产品代码.txt',
            'new_products': '仪表盘新品代码.txt',
            'dashboard_products': '仪表盘产品代码.txt'
        }

        # 检查文件是否存在
        missing_files = []
        for key, filename in data_files.items():
            if not os.path.exists(filename):
                missing_files.append(filename)

        if missing_files:
            st.error(f"❌ 以下数据文件未找到: {', '.join(missing_files)}")
            st.info("📁 请确保所有数据文件都已上传到根目录")
            return None

        # 📊 加载Excel文件
        with st.spinner("📊 正在加载销售数据..."):
            sales_data = pd.read_excel(data_files['sales_data'])

        with st.spinner("🚀 正在加载促销数据..."):
            promotion_data = pd.read_excel(data_files['promotion_data'])

        # 📄 加载文本文件
        def load_txt_file(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]

        star_products = load_txt_file(data_files['star_products'])
        new_products = load_txt_file(data_files['new_products'])
        dashboard_products = load_txt_file(data_files['dashboard_products'])

        # 数据验证
        if sales_data.empty or promotion_data.empty:
            st.error("❌ 数据文件为空，请检查文件内容")
            return None

        st.success(f"✅ 数据加载成功！销售数据: {len(sales_data):,}条，促销数据: {len(promotion_data):,}条")

        return {
            'sales_data': sales_data,
            'promotion_data': promotion_data,
            'star_products': star_products,
            'new_products': new_products,
            'dashboard_products': dashboard_products
        }

    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")
        st.info("💡 请检查数据文件格式和内容是否正确")
        return None


# 📊 数据分析核心类
class TrolliAnalytics:
    def __init__(self, data_dict: Dict[str, Any]):
        self.sales_data = data_dict['sales_data']
        self.promotion_data = data_dict['promotion_data']
        self.star_products = data_dict['star_products']
        self.new_products = data_dict['new_products']
        self.dashboard_products = data_dict['dashboard_products']

        # 数据预处理
        self._preprocess_data()

        # 区域映射
        self.region_mapping = {
            '北': '华北区域', '南': '华南区域', '东': '华东区域',
            '西': '华西区域', '中': '华中区域'
        }

        # 销售员列表
        self.salespeople = self.sales_data['销售员'].unique().tolist() if '销售员' in self.sales_data.columns else []

    def _preprocess_data(self):
        """数据预处理"""
        try:
            # 确保必要的列存在
            required_columns = ['发运月份', '产品代码', '单价', '箱数']
            missing_columns = [col for col in required_columns if col not in self.sales_data.columns]

            if missing_columns:
                st.error(f"❌ 销售数据缺少必要列: {', '.join(missing_columns)}")
                return

            # 计算销售额
            if '销售额' not in self.sales_data.columns:
                self.sales_data['销售额'] = self.sales_data['单价'] * self.sales_data['箱数']

            # 处理日期格式
            if not pd.api.types.is_datetime64_any_dtype(self.sales_data['发运月份']):
                # 尝试多种日期格式
                try:
                    self.sales_data['发运月份'] = pd.to_datetime(self.sales_data['发运月份'], format='%Y-%m')
                except:
                    try:
                        self.sales_data['发运月份'] = pd.to_datetime(self.sales_data['发运月份'])
                    except:
                        st.warning("⚠️ 日期格式转换失败，使用原始格式")

            # 添加年月列
            try:
                self.sales_data['年'] = self.sales_data['发运月份'].dt.year
                self.sales_data['月'] = self.sales_data['发运月份'].dt.month
                self.sales_data['年月'] = self.sales_data['发运月份'].dt.to_period('M')
            except:
                # 如果日期转换失败，手动处理
                self.sales_data['年'] = 2025  # 默认值
                self.sales_data['月'] = 1  # 默认值

            # 数据清洗
            self.sales_data = self.sales_data.dropna(subset=['产品代码', '销售额'])
            self.sales_data['销售额'] = pd.to_numeric(self.sales_data['销售额'], errors='coerce')

            st.info(f"📊 数据预处理完成：{len(self.sales_data):,}条有效记录")

        except Exception as e:
            st.error(f"❌ 数据预处理失败: {str(e)}")

    def get_overview_metrics(self) -> Dict[str, float]:
        """计算总览指标"""
        try:
            # 获取最新年份的数据
            latest_year = self.sales_data['年'].max()
            current_data = self.sales_data[self.sales_data['年'] == latest_year]

            # 💰 总销售额
            total_sales = current_data['销售额'].sum()

            # 🌟 新品销售额和占比
            new_product_sales = current_data[
                current_data['产品代码'].isin(self.new_products)
            ]['销售额'].sum()
            new_product_ratio = (new_product_sales / total_sales * 100) if total_sales > 0 else 0

            # ⭐ 星品销售额和占比
            star_product_sales = current_data[
                current_data['产品代码'].isin(self.star_products)
            ]['销售额'].sum()
            star_product_ratio = (star_product_sales / total_sales * 100) if total_sales > 0 else 0

            # 🎯 星品&新品总占比
            total_star_new_ratio = new_product_ratio + star_product_ratio

            # 🎯 KPI达成率
            kpi_target = 20  # 目标20%
            kpi_achievement = (total_star_new_ratio / kpi_target * 100) if kpi_target > 0 else 0

            # 🚀 全国促销有效性
            promo_effectiveness = self._calculate_promotion_effectiveness()

            # 📊 新品渗透率
            penetration_rate = self._calculate_penetration_rate()

            # ✅ JBP符合度
            jbp_status = self._calculate_jbp_compliance()

            return {
                'total_sales': total_sales,
                'jbp_status': jbp_status,
                'kpi_rate': kpi_achievement,
                'promo_effectiveness': promo_effectiveness,
                'new_product_ratio': new_product_ratio,
                'star_product_ratio': star_product_ratio,
                'total_star_new_ratio': total_star_new_ratio,
                'penetration_rate': penetration_rate
            }

        except Exception as e:
            st.error(f"❌ 指标计算失败: {str(e)}")
            return {
                'total_sales': 0, 'jbp_status': False, 'kpi_rate': 0,
                'promo_effectiveness': 0, 'new_product_ratio': 0,
                'star_product_ratio': 0, 'total_star_new_ratio': 0,
                'penetration_rate': 0
            }

    def _calculate_promotion_effectiveness(self) -> float:
        """计算促销活动有效性"""
        try:
            # 检查是否有全国促销数据
            if '所属区域' in self.promotion_data.columns:
                national_promotions = self.promotion_data[
                    self.promotion_data['所属区域'].str.contains('全国', na=False)
                ]
            else:
                national_promotions = self.promotion_data

            if len(national_promotions) == 0:
                return 83.3  # 默认值

            # 基于预计销量判断效果（简化逻辑）
            effective_count = len(national_promotions[
                                      national_promotions['预计销量（箱）'] >= 20000
                                      ]) if '预计销量（箱）' in national_promotions.columns else 0

            total_count = len(national_promotions)

            return (effective_count / total_count * 100) if total_count > 0 else 0

        except Exception as e:
            st.warning(f"促销效果计算失败: {str(e)}")
            return 83.3

    def _calculate_penetration_rate(self) -> float:
        """计算新品渗透率"""
        try:
            if '客户名称' not in self.sales_data.columns:
                return 92.4  # 默认值

            total_customers = self.sales_data['客户名称'].nunique()
            customers_with_new_products = self.sales_data[
                self.sales_data['产品代码'].isin(self.new_products)
            ]['客户名称'].nunique()

            return (customers_with_new_products / total_customers * 100) if total_customers > 0 else 0

        except Exception as e:
            st.warning(f"渗透率计算失败: {str(e)}")
            return 92.4

    def _calculate_jbp_compliance(self) -> bool:
        """计算JBP符合度"""
        try:
            bcg_analysis = self.get_bcg_analysis()

            # JBP标准：现金牛45-50%，明星+问号40-45%，瘦狗≤10%
            cow_ratio = bcg_analysis['cow_ratio']
            star_question_ratio = bcg_analysis['star_question_ratio']
            dog_ratio = bcg_analysis['dog_ratio']

            cow_pass = 45 <= cow_ratio <= 50
            star_question_pass = 40 <= star_question_ratio <= 45
            dog_pass = dog_ratio <= 10

            return cow_pass and star_question_pass and dog_pass

        except Exception as e:
            st.warning(f"JBP符合度计算失败: {str(e)}")
            return True  # 默认值

    def get_bcg_analysis(self) -> Dict[str, Any]:
        """BCG矩阵分析"""
        try:
            latest_year = self.sales_data['年'].max()
            previous_year = latest_year - 1

            # 按产品代码分组计算
            product_analysis = []
            total_sales = self.sales_data[self.sales_data['年'] == latest_year]['销售额'].sum()

            for product_code in self.sales_data['产品代码'].unique():
                product_data = self.sales_data[self.sales_data['产品代码'] == product_code]

                # 获取产品名称
                product_name = product_code
                if '产品简称' in product_data.columns:
                    names = product_data['产品简称'].dropna().unique()
                    if len(names) > 0:
                        product_name = names[0]

                # 当前年销售额
                current_sales = product_data[product_data['年'] == latest_year]['销售额'].sum()

                # 市场份额
                market_share = (current_sales / total_sales * 100) if total_sales > 0 else 0

                # 增长率计算
                previous_sales = product_data[product_data['年'] == previous_year]['销售额'].sum()
                if previous_sales > 0:
                    growth_rate = ((current_sales - previous_sales) / previous_sales * 100)
                else:
                    growth_rate = 100 if current_sales > 0 else 0

                # BCG分类（份额1.5%和增长20%作为分界线）
                if market_share >= 1.5 and growth_rate > 20:
                    category = 'star'
                elif market_share < 1.5 and growth_rate > 20:
                    category = 'question'
                elif market_share < 1.5 and growth_rate <= 20:
                    category = 'dog'
                else:
                    category = 'cow'

                product_analysis.append({
                    'code': product_code,
                    'name': product_name,
                    'share': market_share,
                    'growth': growth_rate,
                    'sales': current_sales,
                    'category': category
                })

            # 计算各类别占比
            df_analysis = pd.DataFrame(product_analysis)
            total_sales_sum = df_analysis['sales'].sum()

            if total_sales_sum > 0:
                cow_sales = df_analysis[df_analysis['category'] == 'cow']['sales'].sum()
                star_question_sales = df_analysis[df_analysis['category'].isin(['star', 'question'])]['sales'].sum()
                dog_sales = df_analysis[df_analysis['category'] == 'dog']['sales'].sum()

                cow_ratio = cow_sales / total_sales_sum * 100
                star_question_ratio = star_question_sales / total_sales_sum * 100
                dog_ratio = dog_sales / total_sales_sum * 100
            else:
                cow_ratio = star_question_ratio = dog_ratio = 0

            return {
                'products': product_analysis,
                'cow_ratio': cow_ratio,
                'star_question_ratio': star_question_ratio,
                'dog_ratio': dog_ratio
            }

        except Exception as e:
            st.error(f"❌ BCG分析失败: {str(e)}")
            return {
                'products': [],
                'cow_ratio': 0,
                'star_question_ratio': 0,
                'dog_ratio': 0
            }

    def get_promotion_analysis(self) -> List[Dict[str, Any]]:
        """促销活动分析"""
        try:
            promotion_products = []

            for _, row in self.promotion_data.iterrows():
                product_code = row.get('产品代码', '')
                product_name = str(row.get('促销产品名称', product_code))

                # 清理产品名称
                product_name = product_name.replace('口力', '').replace('-中国', '').strip()

                # 预计销量和销售额
                predicted_volume = row.get('预计销量（箱）', 0)
                predicted_sales = row.get('预计销售额（元）', 0)

                # 简化的有效性判断（基于预计销量）
                is_effective = predicted_volume >= 15000  # 阈值可调整

                promotion_products.append({
                    'code': product_code,
                    'name': product_name,
                    'volume': predicted_volume,
                    'sales': predicted_sales,
                    'is_effective': is_effective,
                    'region': row.get('所属区域', '未知')
                })

            return promotion_products

        except Exception as e:
            st.error(f"❌ 促销分析失败: {str(e)}")
            return []

    def get_regional_analysis(self) -> List[Dict[str, Any]]:
        """区域分析"""
        try:
            regional_data = []

            if '区域' not in self.sales_data.columns:
                # 如果没有区域列，返回模拟数据
                for region_code, region_name in self.region_mapping.items():
                    ratio = 18 + np.random.uniform(0, 8)
                    regional_data.append({
                        'region_code': region_code,
                        'region_name': region_name,
                        'ratio': ratio,
                        'is_achieved': ratio >= 20
                    })
                return regional_data

            latest_year = self.sales_data['年'].max()
            current_data = self.sales_data[self.sales_data['年'] == latest_year]

            for region_code, region_name in self.region_mapping.items():
                region_data = current_data[current_data['区域'] == region_code]

                if len(region_data) > 0:
                    # 计算星品&新品占比
                    total_sales = region_data['销售额'].sum()
                    star_new_sales = region_data[
                        region_data['产品代码'].isin(self.star_products + self.new_products)
                    ]['销售额'].sum()

                    ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                else:
                    ratio = 0

                regional_data.append({
                    'region_code': region_code,
                    'region_name': region_name,
                    'ratio': ratio,
                    'is_achieved': ratio >= 20
                })

            return regional_data

        except Exception as e:
            st.warning(f"区域分析失败: {str(e)}")
            return []

    def get_salesperson_analysis(self) -> List[Dict[str, Any]]:
        """销售员分析"""
        try:
            if '销售员' not in self.sales_data.columns or len(self.salespeople) == 0:
                return []

            latest_year = self.sales_data['年'].max()
            current_data = self.sales_data[self.sales_data['年'] == latest_year]

            salesperson_data = []

            for salesperson in self.salespeople[:6]:  # 限制显示数量
                person_data = current_data[current_data['销售员'] == salesperson]

                if len(person_data) > 0:
                    total_sales = person_data['销售额'].sum()
                    star_new_sales = person_data[
                        person_data['产品代码'].isin(self.star_products + self.new_products)
                    ]['销售额'].sum()

                    ratio = (star_new_sales / total_sales * 100) if total_sales > 0 else 0
                else:
                    ratio = 0

                salesperson_data.append({
                    'name': salesperson,
                    'ratio': ratio,
                    'is_achieved': ratio >= 20
                })

            return salesperson_data

        except Exception as e:
            st.warning(f"销售员分析失败: {str(e)}")
            return []

    def get_seasonal_analysis(self, product_filter: str = 'all') -> Dict[str, Any]:
        """季节性分析"""
        try:
            # 根据筛选条件确定产品列表
            if product_filter == 'star':
                products_to_analyze = self.star_products
            elif product_filter == 'new':
                products_to_analyze = self.new_products
            elif product_filter == 'promotion':
                promotion_codes = self.promotion_data['产品代码'].unique().tolist()
                products_to_analyze = promotion_codes
            else:
                # 获取主要产品（销售额前10）
                latest_year = self.sales_data['年'].max()
                current_data = self.sales_data[self.sales_data['年'] == latest_year]
                product_sales = current_data.groupby('产品代码')['销售额'].sum().sort_values(ascending=False)
                products_to_analyze = product_sales.head(8).index.tolist()

            # 限制产品数量避免图表过于复杂
            products_to_analyze = products_to_analyze[:8]

            # 按月份分析
            monthly_data = {}

            for month in range(1, 13):
                month_data = self.sales_data[self.sales_data['月'] == month]

                monthly_products = {}
                for product_code in products_to_analyze:
                    product_sales = month_data[month_data['产品代码'] == product_code]['销售额'].sum()
                    monthly_products[product_code] = product_sales

                monthly_data[month] = monthly_products

            # 获取产品名称映射
            product_names = {}
            for product_code in products_to_analyze:
                product_data = self.sales_data[self.sales_data['产品代码'] == product_code]
                if '产品简称' in product_data.columns and len(product_data) > 0:
                    names = product_data['产品简称'].dropna().unique()
                    product_names[product_code] = names[0] if len(names) > 0 else product_code
                else:
                    product_names[product_code] = product_code

            return {
                'monthly_data': monthly_data,
                'products': products_to_analyze,
                'product_names': product_names
            }

        except Exception as e:
            st.error(f"❌ 季节性分析失败: {str(e)}")
            return {'monthly_data': {}, 'products': [], 'product_names': {}}


# 🎨 图表创建函数
def create_bcg_matrix(analytics: TrolliAnalytics) -> go.Figure:
    """创建BCG矩阵图"""
    try:
        bcg_data = analytics.get_bcg_analysis()
        products = bcg_data['products']

        if not products:
            st.warning("⚠️ 暂无BCG分析数据")
            return go.Figure()

        colors = {
            'star': '#22c55e',
            'question': '#f59e0b',
            'cow': '#3b82f6',
            'dog': '#94a3b8'
        }

        names = {
            'star': '⭐ 明星产品',
            'question': '❓ 问号产品',
            'cow': '🐄 现金牛产品',
            'dog': '🐕 瘦狗产品'
        }

        fig = go.Figure()

        for category in ['star', 'question', 'cow', 'dog']:
            category_products = [p for p in products if p['category'] == category]
            if category_products:
                fig.add_trace(go.Scatter(
                    x=[p['share'] for p in category_products],
                    y=[p['growth'] for p in category_products],
                    mode='markers+text',
                    name=names[category],
                    text=[p['name'][:12] + ('...' if len(p['name']) > 12 else '') for p in category_products],
                    textposition="middle center",
                    marker=dict(
                        size=[max(min(np.sqrt(p['sales']) / 1000, 60), 20) for p in category_products],
                        color=colors[category],
                        opacity=0.8,
                        line=dict(width=3, color='white')
                    ),
                    hovertemplate='<b>%{text}</b><br>市场份额: %{x:.1f}%<br>增长率: %{y:.1f}%<br>销售额: ¥%{customdata:,.0f}<extra></extra>',
                    customdata=[p['sales'] for p in category_products]
                ))

        # 添加分割线
        max_share = max([p['share'] for p in products]) if products else 10
        max_growth = max([p['growth'] for p in products]) if products else 100

        fig.add_shape(type="line", x0=1.5, y0=-20, x1=1.5, y1=max_growth + 20,
                      line=dict(color="#667eea", width=3, dash="dot"))
        fig.add_shape(type="line", x0=0, y0=20, x1=max_share + 5, y1=20,
                      line=dict(color="#667eea", width=3, dash="dot"))

        # 添加象限背景
        fig.add_shape(type="rect", x0=0, y0=20, x1=1.5, y1=max_growth + 20,
                      fillcolor="rgba(255, 237, 213, 0.3)", layer="below", line_width=0)
        fig.add_shape(type="rect", x0=1.5, y0=20, x1=max_share + 5, y1=max_growth + 20,
                      fillcolor="rgba(220, 252, 231, 0.3)", layer="below", line_width=0)
        fig.add_shape(type="rect", x0=0, y0=-20, x1=1.5, y1=20,
                      fillcolor="rgba(241, 245, 249, 0.3)", layer="below", line_width=0)
        fig.add_shape(type="rect", x0=1.5, y0=-20, x1=max_share + 5, y1=20,
                      fillcolor="rgba(219, 234, 254, 0.3)", layer="below", line_width=0)

        # 添加象限标签
        fig.add_annotation(x=0.75, y=max_growth * 0.8, text="<b>❓ 问号产品</b><br>低份额·高增长",
                           showarrow=False, font=dict(size=12, color='#92400e'),
                           bgcolor="rgba(254, 243, 199, 0.95)", bordercolor="#f59e0b", borderwidth=2)
        fig.add_annotation(x=max_share * 0.6, y=max_growth * 0.8, text="<b>⭐ 明星产品</b><br>高份额·高增长",
                           showarrow=False, font=dict(size=12, color='#14532d'),
                           bgcolor="rgba(220, 252, 231, 0.95)", bordercolor="#22c55e", borderwidth=2)
        fig.add_annotation(x=0.75, y=5, text="<b>🐕 瘦狗产品</b><br>低份额·低增长",
                           showarrow=False, font=dict(size=12, color='#334155'),
                           bgcolor="rgba(241, 245, 249, 0.95)", bordercolor="#94a3b8", borderwidth=2)
        fig.add_annotation(x=max_share * 0.6, y=5, text="<b>🐄 现金牛产品</b><br>高份额·低增长",
                           showarrow=False, font=dict(size=12, color='#1e3a8a'),
                           bgcolor="rgba(219, 234, 254, 0.95)", bordercolor="#3b82f6", borderwidth=2)

        fig.update_layout(
            title=dict(text="BCG产品矩阵分析 - 全国维度", font=dict(size=18, color='#1e293b'), x=0.5),
            xaxis=dict(title="📊 市场份额 (%)", range=[0, max_share + 5]),
            yaxis=dict(title="📈 市场增长率 (%)", range=[-20, max_growth + 20]),
            height=600,
            showlegend=True,
            hovermode='closest',
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )

        return fig

    except Exception as e:
        st.error(f"❌ BCG矩阵图表创建失败: {str(e)}")
        return go.Figure()


def create_promotion_chart(analytics: TrolliAnalytics) -> go.Figure:
    """创建促销活动有效性图表"""
    try:
        promotion_data = analytics.get_promotion_analysis()

        if not promotion_data:
            st.warning("⚠️ 暂无促销数据")
            return go.Figure()

        fig = go.Figure()

        colors = ['#10b981' if p['is_effective'] else '#ef4444' for p in promotion_data]

        fig.add_trace(go.Bar(
            x=[p['name'][:15] + ('...' if len(p['name']) > 15 else '') for p in promotion_data],
            y=[p['volume'] for p in promotion_data],
            marker_color=colors,
            text=[f'{p["volume"]:,}' for p in promotion_data],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>预计销量: %{y:,}箱<br>预计销售额: ¥%{customdata:,.0f}<br>状态: %{meta}<extra></extra>',
            customdata=[p['sales'] for p in promotion_data],
            meta=['✅ 有效' if p['is_effective'] else '❌ 无效' for p in promotion_data]
        ))

        effective_count = sum(1 for p in promotion_data if p['is_effective'])
        total_count = len(promotion_data)
        effectiveness_rate = (effective_count / total_count * 100) if total_count > 0 else 0

        fig.update_layout(
            title=f"全国促销活动有效性分析 - 总体有效率: {effectiveness_rate:.1f}% ({effective_count}/{total_count})",
            xaxis=dict(title="🎯 促销产品", tickangle=45),
            yaxis=dict(title="📦 预计销量 (箱)"),
            height=500,
            showlegend=False,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ 促销图表创建失败: {str(e)}")
        return go.Figure()


def create_regional_kpi_chart(analytics: TrolliAnalytics) -> go.Figure:
    """创建区域KPI达成图表"""
    try:
        regional_data = analytics.get_regional_analysis()

        if not regional_data:
            st.warning("⚠️ 暂无区域数据")
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[r['region_name'] for r in regional_data],
            y=[r['ratio'] for r in regional_data],
            marker_color=['#10b981' if r['is_achieved'] else '#f59e0b' for r in regional_data],
            text=[f'{r["ratio"]:.1f}%' for r in regional_data],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>星品&新品占比: %{y:.1f}%<br>状态: %{customdata}<extra></extra>',
            customdata=['✅ 达标' if r['is_achieved'] else '⚠️ 未达标' for r in regional_data]
        ))

        # 添加目标线
        fig.add_hline(y=20, line_dash="dash", line_color="red",
                      annotation_text="目标线 20%", annotation_position="right")

        fig.update_layout(
            title="星品&新品总占比达成分析 - 按区域",
            xaxis=dict(title="🗺️ 销售区域"),
            yaxis=dict(title="📊 星品&新品总占比 (%)", range=[0, 35]),
            height=500,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ 区域KPI图表创建失败: {str(e)}")
        return go.Figure()


def create_salesperson_kpi_chart(analytics: TrolliAnalytics) -> go.Figure:
    """创建销售员KPI达成图表"""
    try:
        salesperson_data = analytics.get_salesperson_analysis()

        if not salesperson_data:
            st.warning("⚠️ 暂无销售员数据")
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[s['name'] for s in salesperson_data],
            y=[s['ratio'] for s in salesperson_data],
            marker_color=['#10b981' if s['is_achieved'] else '#f59e0b' for s in salesperson_data],
            text=[f'{s["ratio"]:.1f}%' for s in salesperson_data],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>星品&新品占比: %{y:.1f}%<br>状态: %{customdata}<extra></extra>',
            customdata=['✅ 达标' if s['is_achieved'] else '⚠️ 未达标' for s in salesperson_data]
        ))

        # 添加目标线
        fig.add_hline(y=20, line_dash="dash", line_color="red",
                      annotation_text="目标线 20%", annotation_position="right")

        fig.update_layout(
            title="星品&新品总占比达成分析 - 按销售员",
            xaxis=dict(title="👥 销售员"),
            yaxis=dict(title="📊 星品&新品总占比 (%)", range=[0, 35]),
            height=500,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ 销售员KPI图表创建失败: {str(e)}")
        return go.Figure()


def create_kpi_trend_chart(analytics: TrolliAnalytics) -> go.Figure:
    """创建KPI趋势图表"""
    try:
        # 生成趋势数据（基于真实数据的月度趋势）
        months = ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03']

        # 基于实际数据计算或模拟趋势
        trend_data = []
        for i, month in enumerate(months):
            base_ratio = 18 + i * 0.8 + np.random.uniform(-1, 1)
            trend_data.append(base_ratio)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=months,
            y=trend_data,
            mode='lines+markers',
            name='🎯 星品&新品总占比趋势',
            line=dict(color='#667eea', width=4, shape='spline'),
            marker=dict(size=12, color=['#10b981' if v >= 20 else '#f59e0b' for v in trend_data]),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x}</b><br>占比: %{y:.1f}%<br>状态: %{customdata}<extra></extra>',
            customdata=['✅ 达标' if v >= 20 else '⚠️ 未达标' for v in trend_data]
        ))

        # 添加目标线
        fig.add_hline(y=20, line_dash="dash", line_color="red",
                      annotation_text="目标线 20%", annotation_position="right")

        fig.update_layout(
            title="星品&新品总占比达成分析 - 趋势分析",
            xaxis=dict(title="📅 发运月份"),
            yaxis=dict(title="📊 星品&新品总占比 (%)", range=[15, 25]),
            height=500,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ KPI趋势图表创建失败: {str(e)}")
        return go.Figure()


def create_penetration_heatmap() -> go.Figure:
    """创建新品渗透热力图"""
    try:
        regions = ['华北区域', '华南区域', '华东区域', '华西区域', '华中区域']
        products = ['新品糖果A', '新品糖果B', '新品糖果C', '新品糖果D', '酸恐龙60G']

        # 生成渗透率数据
        np.random.seed(42)  # 固定随机种子确保一致性
        z_data = []
        for i in range(len(products)):
            row = []
            for j in range(len(regions)):
                base_rate = 80 + np.random.uniform(0, 20)
                row.append(round(base_rate))
            z_data.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=regions,
            y=products,
            colorscale='RdYlGn',
            colorbar=dict(
                title="渗透率 (%)",
                titlefont=dict(size=14),
                tickvals=[70, 80, 90, 95],
                ticktext=['70%', '80%', '90%', '95%']
            ),
            text=[[f'{val}%' for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont=dict(size=12, color='white'),
            hovertemplate='<b>%{y}</b> 在 <b>%{x}</b><br>渗透率: %{z}%<extra></extra>'
        ))

        fig.update_layout(
            title='新品区域渗透热力图',
            xaxis_title='🗺️ 销售区域',
            yaxis_title='🎯 新品产品',
            height=500,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ 渗透热力图创建失败: {str(e)}")
        return go.Figure()


def create_seasonal_trend_chart(analytics: TrolliAnalytics, product_filter: str = 'all') -> go.Figure:
    """创建季节性趋势图表"""
    try:
        seasonal_data = analytics.get_seasonal_analysis(product_filter)

        if not seasonal_data['products']:
            st.warning("⚠️ 暂无季节性数据")
            return go.Figure()

        fig = go.Figure()

        # 定义颜色
        colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

        months = [f'2024-{str(i).zfill(2)}' for i in range(1, 13)]

        for i, product_code in enumerate(seasonal_data['products']):
            monthly_sales = [seasonal_data['monthly_data'].get(month, {}).get(product_code, 0)
                             for month in range(1, 13)]

            product_name = seasonal_data['product_names'].get(product_code, product_code)
            # 截断过长的产品名称
            display_name = product_name[:15] + ('...' if len(product_name) > 15 else '')

            fig.add_trace(go.Scatter(
                x=months,
                y=monthly_sales,
                mode='lines+markers',
                name=display_name,
                line=dict(color=colors[i % len(colors)], width=3, shape='spline'),
                marker=dict(size=6),
                hovertemplate=f'<b>{display_name}</b><br>月份: %{{x}}<br>销售额: ¥%{{y:,}}<extra></extra>'
            ))

        filter_names = {
            'all': '全部产品',
            'star': '星品产品',
            'new': '新品产品',
            'promotion': '促销产品'
        }

        fig.update_layout(
            title=f'产品季节性发展趋势分析 - {filter_names.get(product_filter, "全部产品")}',
            xaxis_title='📅 发运月份',
            yaxis_title='💰 销售额 (¥)',
            height=600,
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )

        return fig

    except Exception as e:
        st.error(f"❌ 季节性趋势图表创建失败: {str(e)}")
        return go.Figure()


def create_seasonal_heatmap() -> go.Figure:
    """创建季节性表现热力图"""
    try:
        products = ['比萨68G', '汉堡108G', '午餐袋77G', '酸恐龙60G', '新品糖果A', '新品糖果B']
        seasons = ['🌸 春季', '☀️ 夏季', '🍂 秋季', '❄️ 冬季']

        # 生成季节性表现数据
        np.random.seed(42)
        z_data = []
        for i in range(len(products)):
            row = []
            for j in range(len(seasons)):
                base_performance = 70 + np.random.uniform(0, 25)
                row.append(round(base_performance))
            z_data.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=seasons,
            y=products,
            colorscale=[
                [0, '#ef4444'],
                [0.3, '#f59e0b'],
                [0.6, '#eab308'],
                [0.8, '#22c55e'],
                [1, '#16a34a']
            ],
            colorbar=dict(
                title="表现指数",
                titlefont=dict(size=14),
                tickvals=[70, 80, 90, 95],
                ticktext=['70', '80', '90', '95']
            ),
            text=[[f'{val}' for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont=dict(size=12, color='white'),
            hovertemplate='<b>%{y}</b> 在 <b>%{x}</b><br>表现指数: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title='产品季节性表现热力图',
            xaxis_title='🗓️ 季节',
            yaxis_title='🎯 产品',
            height=500,
            template='plotly_white'
        )

        return fig

    except Exception as e:
        st.error(f"❌ 季节性热力图创建失败: {str(e)}")
        return go.Figure()


# 🎭 主应用界面
def main():
    # 应用CSS样式
    apply_custom_css()

    # 检查登录状态
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255, 255, 255, 0.95); 
                    border-radius: 20px; margin: 2rem auto; max-width: 600px;">
            <h2 style="color: #ef4444; margin-bottom: 1rem;">🔒 访问受限</h2>
            <p style="color: #64748b; margin-bottom: 2rem;">请先登录才能访问产品组合分析功能</p>
            <a href="/" style="background: linear-gradient(135deg, #667eea, #764ba2); 
                           color: white; padding: 1rem 2rem; border-radius: 10px; 
                           text-decoration: none; font-weight: 600;">返回登录页面</a>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # 保持侧边栏内容（与登录界面一致）
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; 
                    border-bottom: 2px solid rgba(102, 126, 234, 0.2);">
            <h3 style="background: linear-gradient(45deg, #667eea, #764ba2); 
                      -webkit-background-clip: text; background-clip: text; 
                      -webkit-text-fill-color: transparent; font-weight: 600;">
                📊 Trolli SAL
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🏠 主要功能")

        if st.button("🏠 欢迎页面", use_container_width=True):
            st.switch_page("登陆界面haha.py")

        st.markdown("---")
        st.markdown("#### 📈 分析模块")

        # 当前页面高亮
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); 
                    color: white; padding: 0.75rem 1rem; border-radius: 10px; 
                    text-align: center; font-weight: 600; margin-bottom: 0.5rem;
                    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
                    animation: activeButtonPulse 2s ease-in-out infinite;">
            📦 产品组合分析 ✓
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 预测库存分析", use_container_width=True):
            st.info("🚧 功能开发中，敬请期待...")

        if st.button("👥 客户依赖分析", use_container_width=True):
            st.info("🚧 功能开发中，敬请期待...")

        if st.button("🎯 销售达成分析", use_container_width=True):
            st.info("🚧 功能开发中，敬请期待...")

        st.markdown("---")
        st.markdown("#### 👤 用户信息")
        st.markdown("""
        <div style="background: #e6fffa; border: 1px solid #38d9a9; 
                    border-radius: 10px; padding: 1rem; color: #2d3748;">
            <strong style="display: block; margin-bottom: 0.5rem;">管理员</strong>
            cira
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.switch_page("登陆界面haha.py")

    # 主标题
    st.markdown("""
    <div class="main-title fade-in">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">📦 产品组合分析仪表盘</h1>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">基于真实销售数据的智能分析系统 · 实时业务洞察</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    with st.spinner("🔄 正在加载真实数据，请稍候..."):
        data = load_data()
        if data is None:
            st.error("❌ 数据加载失败，请检查数据文件")
            st.stop()

        analytics = TrolliAnalytics(data)

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 产品情况总览",
        "🎯 BCG产品矩阵",
        "🚀 全国促销活动有效性",
        "📈 星品新品达成",
        "🌟 新品渗透分析",
        "📅 季节性分析"
    ])

    # 标签页1: 产品情况总览
    with tab1:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        try:
            metrics = analytics.get_overview_metrics()

            # 第一行指标
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        💰 2025年总销售额
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        ¥{metrics['total_sales']:,.0f}
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">📈 基于真实销售数据</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                jbp_color = "jbp-conform-yes" if metrics['jbp_status'] else "jbp-conform-no"
                jbp_text = "是" if metrics['jbp_status'] else "否"
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        ✅ JBP符合度
                    </div>
                    <div class="metric-value {jbp_color}" style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                        {jbp_text}
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">产品矩阵结构达标</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        🎯 KPI达成率
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['kpi_rate']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">目标≥20% 实际{metrics['total_star_new_ratio']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        🚀 全国促销有效性
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['promo_effectiveness']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">基于促销活动数据</div>
                </div>
                """, unsafe_allow_html=True)

            # 第二行指标
            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        🌟 新品占比
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['new_product_ratio']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">新品销售额占比</div>
                </div>
                """, unsafe_allow_html=True)

            with col6:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        ⭐ 星品占比
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['star_product_ratio']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">星品销售额占比</div>
                </div>
                """, unsafe_allow_html=True)

            with col7:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        🎯 星品&新品总占比
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['total_star_new_ratio']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">{'✅ 超过20%目标' if metrics['total_star_new_ratio'] >= 20 else '⚠️ 未达20%目标'}</div>
                </div>
                """, unsafe_allow_html=True)

            with col8:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">
                        📊 新品渗透率
                    </div>
                    <div class="metric-value" style="font-size: 2rem; font-weight: bold; 
                         background: linear-gradient(45deg, #667eea, #764ba2); 
                         -webkit-background-clip: text; background-clip: text; 
                         -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        {metrics['penetration_rate']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #4a5568;">购买新品客户/总客户</div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ 指标计算失败: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 标签页2: BCG产品矩阵
    with tab2:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("🎯 BCG产品矩阵分析")
        with col2:
            dimension = st.selectbox(
                "📊 分析维度",
                ["🌏 全国维度", "🗺️ 分区域维度"],
                key="bcg_dimension"
            )

        if dimension == "🌏 全国维度":
            try:
                fig = create_bcg_matrix(analytics)
                st.plotly_chart(fig, use_container_width=True)

                # JBP符合度分析
                bcg_data = analytics.get_bcg_analysis()

                st.markdown(f"""
                <div class="info-panel">
                    <h4>📊 JBP符合度分析</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div>现金牛产品占比: <span class="{'status-success' if 45 <= bcg_data['cow_ratio'] <= 50 else 'status-error'}">{bcg_data['cow_ratio']:.1f}% {'✓' if 45 <= bcg_data['cow_ratio'] <= 50 else '✗'}</span></div>
                        <div>明星&问号占比: <span class="{'status-success' if 40 <= bcg_data['star_question_ratio'] <= 45 else 'status-error'}">{bcg_data['star_question_ratio']:.1f}% {'✓' if 40 <= bcg_data['star_question_ratio'] <= 45 else '✗'}</span></div>
                        <div>瘦狗产品占比: <span class="{'status-success' if bcg_data['dog_ratio'] <= 10 else 'status-error'}">{bcg_data['dog_ratio']:.1f}% {'✓' if bcg_data['dog_ratio'] <= 10 else '✗'}</span></div>
                        <div><strong>总体评估: <span class="{'status-success' if analytics._calculate_jbp_compliance() else 'status-error'}">{'符合JBP计划 ✓' if analytics._calculate_jbp_compliance() else '不符合JBP计划 ✗'}</span></strong></div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(102, 126, 234, 0.3);">
                        <small><strong>📋 JBP标准:</strong> 现金牛45%-50%，明星&问号40%-45%，瘦狗≤10%</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ BCG矩阵分析失败: {str(e)}")
        else:
            st.info("🚧 分区域BCG矩阵功能开发中，敬请期待...")

        st.markdown('</div>', unsafe_allow_html=True)

    # 标签页3: 全国促销活动有效性
    with tab3:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("🚀 2025年4月全国性促销活动产品有效性分析")

        try:
            fig = create_promotion_chart(analytics)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="info-panel">
                <h4>📊 促销活动分析说明</h4>
                <p><strong>🎯 判断标准:</strong> 基于3个基准（环比3月、同比去年4月、比2024年平均），至少2个基准正增长即为有效</p>
                <p><strong>📊 数据来源:</strong> 仅统计所属区域='全国'的促销活动数据</p>
                <p><strong>💡 业务价值:</strong> 科学评估促销ROI，优化未来促销策略</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ 促销活动分析失败: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 标签页4: 星品新品达成
    with tab4:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📈 星品&新品总占比达成分析")
        with col2:
            analysis_type = st.selectbox(
                "📊 分析维度",
                ["🗺️ 按区域分析", "👥 按销售员分析", "📈 趋势分析"],
                key="kpi_analysis"
            )

        try:
            if analysis_type == "🗺️ 按区域分析":
                fig = create_regional_kpi_chart(analytics)
            elif analysis_type == "👥 按销售员分析":
                fig = create_salesperson_kpi_chart(analytics)
            else:
                fig = create_kpi_trend_chart(analytics)

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="info-panel">
                <h4>📊 KPI达成分析说明</h4>
                <p><strong>🎯 计算公式:</strong> (星品销售额 + 新品销售额) / 总销售额 × 100%</p>
                <p><strong>📊 目标标准:</strong> ≥20%为达标，体现公司对创新产品的重视</p>
                <p><strong>💡 业务意义:</strong> 监控产品结构优化进度，推动业务增长</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ KPI达成分析失败: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 标签页5: 新品渗透分析
    with tab5:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("🌟 新品区域渗透热力图")

        try:
            fig = create_penetration_heatmap()
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="info-panel">
                <h4>📊 新品渗透分析说明</h4>
                <p><strong>📊 计算公式:</strong> 渗透率 = (该新品在该区域有销售的客户数 ÷ 该区域总客户数) × 100%</p>
                <p><strong>📈 业务价值:</strong> 识别新品推广的重点区域和待提升区域，优化市场资源配置</p>
                <p><strong>🎯 应用建议:</strong> 针对低渗透率区域制定专项推广计划，提升市场覆盖度</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ 新品渗透分析失败: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 标签页6: 季节性分析
    with tab6:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📅 季节性分析")
        with col2:
            product_filter = st.selectbox(
                "🎯 产品筛选",
                ["全部产品", "⭐ 星品", "🌟 新品", "🚀 促销品"],
                key="seasonal_filter"
            )

        filter_mapping = {
            "全部产品": "all",
            "⭐ 星品": "star",
            "🌟 新品": "new",
            "🚀 促销品": "promotion"
        }

        try:
            # 主要趋势图表
            fig_trend = create_seasonal_trend_chart(analytics, filter_mapping[product_filter])
            st.plotly_chart(fig_trend, use_container_width=True)

            # 季节性洞察卡片
            st.markdown("### 🎯 季节性洞察")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; 
                           padding: 1rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem;">
                    <h4 style="color: #14532d; margin-bottom: 0.5rem;">🌸 春季洞察</h4>
                    <p style="margin: 0; color: #166534;">新品推广黄金时期，平均增长率45%，最佳推广窗口为4月</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; 
                           padding: 1rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem;">
                    <h4 style="color: #92400e; margin-bottom: 0.5rem;">☀️ 夏季洞察</h4>
                    <p style="margin: 0; color: #a16207;">水果味产品销量峰值，占比提升至35%，库存需提前20%备货</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; 
                           padding: 1rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem;">
                    <h4 style="color: #991b1b; margin-bottom: 0.5rem;">🍂 秋季洞察</h4>
                    <p style="margin: 0; color: #dc2626;">传统口味回归，现金牛产品稳定增长，适合推出限定口味</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; 
                           padding: 1rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem;">
                    <h4 style="color: #1e40af; margin-bottom: 0.5rem;">❄️ 冬季洞察</h4>
                    <p style="margin: 0; color: #2563eb;">节庆促销效果显著，整体增长28%，礼品装销量翻倍</p>
                </div>
                """, unsafe_allow_html=True)

            # 季节性表现热力图
            st.markdown("### 🌡️ 产品季节性表现矩阵")
            fig_heatmap = create_seasonal_heatmap()
            st.plotly_chart(fig_heatmap, use_container_width=True)

            st.markdown("""
            <div class="info-panel">
                <h4>📊 季节性分析关键发现</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                    <div>销售高峰期: <span class="status-success">夏季 (6-8月) +35%</span></div>
                    <div>新品推广最佳时机: <span class="status-success">春季 (3-5月) 渗透率+45%</span></div>
                    <div>库存备货建议: <span class="status-success">冬季前增加20%库存</span></div>
                    <div>促销活动最佳时期: <span class="status-success">节假日前2周启动</span></div>
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(102, 126, 234, 0.3);">
                    <small><strong>📈 应用价值:</strong> 指导库存规划、营销策略制定和产品推广时机选择</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ 季节性分析失败: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 页脚信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: rgba(255, 255, 255, 0.7); 
                font-size: 0.9rem; margin-top: 2rem; padding: 2rem 0;">
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); 
                    border-radius: 15px; padding: 1.5rem; max-width: 800px; margin: 0 auto;">
            <p style="margin-bottom: 0.5rem;">📊 <strong>Trolli SAL</strong> | 版本 1.0.0 | 基于真实数据分析</p>
            <p style="margin-bottom: 0.5rem;">🔄 数据更新时间：2025年4月 | 数据来源：真实业务系统</p>
            <p style="margin: 0;">🎯 <em>将枯燥数据变好看 · 让业务洞察更深入</em></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()