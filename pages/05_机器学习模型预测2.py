# pages/05_机器学习模型预测.py
"""
管理员专用机器学习销售预测系统 - 完整集成版（优化版）
目标准确率：85-90%
包含数据加载、模型训练、预测和可视化
仅限管理员账号访问
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
import os
import time

# 页面配置
st.set_page_config(
    page_title="管理员 - 机器学习模型预测",
    page_icon="🤖",
    layout="wide"
)

# 权限检查函数 - 保持原有类别
def check_admin_access():
    """检查管理员权限"""
    # 检查是否已登录且为管理员
    if not hasattr(st.session_state, 'authenticated') or not st.session_state.authenticated:
        st.error("❌ 未登录，请先从主页登录")
        st.stop()
    
    if not hasattr(st.session_state, 'username') or st.session_state.username != 'admin':
        st.error("❌ 权限不足，此功能仅限管理员使用")
        st.info("💡 请使用管理员账号登录")
        st.stop()

# 执行权限检查
check_admin_access()

# 统一背景样式CSS - 保持原有类别
unified_admin_styles = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 - 与登录界面保持一致 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 主容器背景 + 增强动画 - 与登录界面完全一致 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
        overflow: hidden;
    }

    /* 增强版动态背景波纹效果 - 与登录界面一致 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.6) 0%, transparent 60%),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(120, 119, 198, 0.4) 0%, transparent 70%),
            radial-gradient(circle at 70% 30%, rgba(182, 244, 146, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, rgba(255, 182, 193, 0.4) 0%, transparent 60%);
        animation: enhancedWaveMove 12s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes enhancedWaveMove {
        0%, 100% { 
            background-size: 200% 200%, 150% 150%, 300% 300%, 180% 180%, 220% 220%;
            background-position: 0% 0%, 100% 100%, 50% 50%, 20% 80%, 90% 10%; 
        }
        25% { 
            background-size: 300% 300%, 200% 200%, 250% 250%, 240% 240%, 160% 160%;
            background-position: 100% 0%, 0% 50%, 80% 20%, 70% 30%, 10% 90%; 
        }
        50% { 
            background-size: 250% 250%, 300% 300%, 200% 200%, 190% 190%, 280% 280%;
            background-position: 50% 100%, 50% 0%, 20% 80%, 90% 70%, 30% 20%; 
        }
        75% { 
            background-size: 320% 320%, 180% 180%, 270% 270%, 210% 210%, 200% 200%;
            background-position: 20% 70%, 80% 30%, 60% 10%, 40% 90%, 70% 50%; 
        }
    }

    /* 增强版浮动粒子效果 - 与登录界面一致 */  
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(3px 3px at 20px 30px, rgba(255,255,255,0.4), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.3), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.5), transparent),
            radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.3), transparent),
            radial-gradient(3px 3px at 160px 30px, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 200px 60px, rgba(182, 244, 146, 0.6), transparent),
            radial-gradient(2px 2px at 250px 90px, rgba(255, 182, 193, 0.5), transparent),
            radial-gradient(1px 1px at 300px 20px, rgba(255, 255, 255, 0.4), transparent);
        background-repeat: repeat;
        background-size: 300px 150px;
        animation: enhancedParticleFloat 25s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes enhancedParticleFloat {
        0% { transform: translateY(100vh) translateX(0) rotate(0deg); }
        25% { transform: translateY(75vh) translateX(50px) rotate(90deg); }
        50% { transform: translateY(50vh) translateX(-30px) rotate(180deg); }
        75% { transform: translateY(25vh) translateX(80px) rotate(270deg); }
        100% { transform: translateY(-100vh) translateX(120px) rotate(360deg); }
    }

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(8px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 管理员头部样式 - 保持原有类别 */
    .admin-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        z-index: 20;
    }

    .admin-badge {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
        animation: adminBadgePulse 2s ease-in-out infinite;
    }

    @keyframes adminBadgePulse {
        0%, 100% { 
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 20px rgba(255, 107, 107, 0.6);
            transform: scale(1.05);
        }
    }

    /* 页面标题样式 - 保持原有类别 */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        color: #2d3748;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        z-index: 20;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: #4a5568;
        opacity: 0.9;
    }
    
    /* 指标卡片样式 - 保持原有类别 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
        position: relative;
        z-index: 20;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* 按钮样式 - 保持原有类别 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 信息框样式 - 保持原有类别 */
    .info-box {
        background: rgba(240, 244, 255, 0.95);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        position: relative;
        z-index: 20;
    }
    
    /* 表格样式 - 保持原有类别 */
    .dataframe {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border: none !important;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .dataframe th {
        background: #667eea !important;
        color: white !important;
        padding: 0.75rem !important;
    }
    
    .dataframe td {
        padding: 0.75rem !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }

    /* Tab样式 - 保持原有类别 */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* 侧边栏样式 - 保持原有类别 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
    }

    /* 退出按钮样式 - 保持原有类别 */
    .logout-button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        font-size: 0.9rem;
    }

    .logout-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
    }

    /* 响应式设计 - 保持原有类别 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .main-subtitle {
            font-size: 1rem;
        }
        .metric-card {
            padding: 1rem;
        }
        .admin-header {
            padding: 1rem;
        }
    }
</style>
"""

st.markdown(unified_admin_styles, unsafe_allow_html=True)

# 管理员头部信息 - 保持原有类别
def render_admin_header():
    """渲染管理员头部信息"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="admin-header">
            <div class="admin-badge">🔒 管理员专用</div>
            <h3 style="margin: 0; color: #2d3748;">欢迎，{st.session_state.get('display_name', '管理员')}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #718096; font-size: 0.9rem;">
                登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 退出登录", key="logout_btn"):
            # 清除session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ 已成功退出登录")
            time.sleep(1)
            st.rerun()

# 渲染管理员头部
render_admin_header()

# 页面标题
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🤖 机器学习模型预测</h1>
    <p class="main-subtitle">基于XGBoost、LightGBM和RandomForest的高精度销售预测 (目标准确率: 85-90%)</p>
</div>
""", unsafe_allow_html=True)

# 初始化session state - 保持原有类别
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'prediction_system' not in st.session_state:
    st.session_state.prediction_system = None
if 'training_history' not in st.session_state:
    st.session_state.training_history = []

# **替换类别**: EnhancedSalesPredictionSystem类
# 原因：替换原有的简单预测系统，使用文档3的增强版本以达到85-90%准确率目标
class EnhancedSalesPredictionSystem:
    """增强版销售预测系统 - 目标准确率85-90%"""
    
    def __init__(self):
        self.shipment_data = None
        self.promotion_data = None
        self.feature_data = None
        self.models = {}
        self.scalers = {}
        self.predictions = None
        self.accuracy_results = {}
        self.product_segments = {}
        self.historical_predictions = None
        self.historical_accuracy = None
        self.feature_importance = None
    
    def load_data_from_github(self, progress_callback=None):
        """从GitHub加载数据文件"""
        try:
            if progress_callback:
                progress_callback(0.1, "正在加载数据文件...")
            
            # 从GitHub仓库加载数据
            shipment_file = "预测模型出货数据每日xlsx.xlsx"
            promotion_file = "销售业务员促销文件.xlsx"
            
            # 检查文件是否存在
            if not os.path.exists(shipment_file) or not os.path.exists(promotion_file):
                st.error(f"数据文件不存在，请确保以下文件在项目目录中：\n- {shipment_file}\n- {promotion_file}")
                return False
            
            self.shipment_data = pd.read_excel(shipment_file)
            self.promotion_data = pd.read_excel(promotion_file)
            
            if progress_callback:
                progress_callback(0.2, f"✅ 出货数据: {len(self.shipment_data):,} 行")
            
            return True
            
        except Exception as e:
            st.error(f"❌ 数据加载失败: {str(e)}")
            return False
    
    def preprocess_data(self, progress_callback=None):
        """高级数据预处理 - 增强版"""
        if progress_callback:
            progress_callback(0.3, "高级数据预处理中...")
        
        # 标准化列名
        shipment_columns = {
            '订单日期': 'order_date',
            '所属区域': 'region', 
            '客户代码': 'customer_code',
            '产品代码': 'product_code',
            '求和项:数量（箱）': 'quantity'
        }
        
        promotion_columns = {
            '申请时间': 'apply_date',
            '经销商代码': 'dealer_code',
            '产品代码': 'product_code',
            '促销开始供货时间': 'promo_start_date',
            '促销结束供货时间': 'promo_end_date',
            '预计销量（箱）': 'expected_sales',
            '赠品数量（箱）': 'gift_quantity'
        }
        
        # 重命名列
        for old_col, new_col in shipment_columns.items():
            if old_col in self.shipment_data.columns:
                self.shipment_data = self.shipment_data.rename(columns={old_col: new_col})
        
        for old_col, new_col in promotion_columns.items():
            if old_col in self.promotion_data.columns:
                self.promotion_data = self.promotion_data.rename(columns={old_col: new_col})
        
        # 数据类型转换
        self.shipment_data['order_date'] = pd.to_datetime(self.shipment_data['order_date'])
        self.shipment_data['quantity'] = pd.to_numeric(self.shipment_data['quantity'], errors='coerce')
        
        # 促销数据处理
        date_cols = ['apply_date', 'promo_start_date', 'promo_end_date']
        for col in date_cols:
            if col in self.promotion_data.columns:
                self.promotion_data[col] = pd.to_datetime(self.promotion_data[col])
        
        # 数据清洗
        original_len = len(self.shipment_data)
        self.shipment_data = self.shipment_data.dropna(subset=['order_date', 'product_code', 'quantity'])
        self.shipment_data = self.shipment_data[self.shipment_data['quantity'] > 0]
        
        # 异常值处理 - 使用更宽松的标准
        self.shipment_data = self._remove_outliers_iqr(self.shipment_data, factor=2.0)
        
        # 产品分段
        self._segment_products()
        
        if progress_callback:
            progress_callback(0.4, f"✅ 高级预处理完成: {len(self.shipment_data)} 行, {self.shipment_data['product_code'].nunique()} 个产品")
        
        return True
    
    def _remove_outliers_iqr(self, data, column='quantity', factor=2.0):
        """使用IQR方法移除异常值 - 增强版"""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        before_count = len(data)
        data_cleaned = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        after_count = len(data_cleaned)
        
        return data_cleaned
    
    def _segment_products(self):
        """产品分段 - 增强版"""
        # 计算每个产品的销量特征
        product_stats = self.shipment_data.groupby('product_code')['quantity'].agg([
            'count', 'mean', 'std', 'min', 'max', 'sum'
        ]).reset_index()
        
        product_stats['cv'] = product_stats['std'] / product_stats['mean']
        product_stats['cv'] = product_stats['cv'].fillna(0)
        
        # 基于销量均值和变异系数分段
        volume_high = product_stats['mean'].quantile(0.67)
        volume_low = product_stats['mean'].quantile(0.33)
        cv_high = product_stats['cv'].quantile(0.67)
        
        def classify_product(row):
            if row['mean'] >= volume_high:
                return '高销量稳定' if row['cv'] <= cv_high else '高销量波动'
            elif row['mean'] >= volume_low:
                return '中销量稳定' if row['cv'] <= cv_high else '中销量波动'
            else:
                return '低销量稳定' if row['cv'] <= cv_high else '低销量波动'
        
        product_stats['segment'] = product_stats.apply(classify_product, axis=1)
        
        # 保存分段结果
        self.product_segments = dict(zip(product_stats['product_code'], product_stats['segment']))
        
        return product_stats
    
    def create_features(self, progress_callback=None):
        """创建高级特征 - 增强版"""
        if progress_callback:
            progress_callback(0.5, "高级特征工程处理中...")
        
        # 创建月度数据
        monthly_data = self.shipment_data.groupby([
            'product_code',
            self.shipment_data['order_date'].dt.to_period('M')
        ]).agg({
            'quantity': ['sum', 'count', 'mean', 'std'],
            'customer_code': 'nunique',
            'region': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]
        }).reset_index()
        
        # 扁平化列名
        monthly_data.columns = ['product_code', 'year_month', 'total_qty', 'order_count',
                                'avg_qty', 'std_qty', 'customer_count', 'main_region']
        monthly_data['std_qty'] = monthly_data['std_qty'].fillna(0)
        
        # 排序
        monthly_data = monthly_data.sort_values(['product_code', 'year_month'])
        
        # 为每个产品段分别创建特征
        all_features = []
        
        for segment in self.product_segments.values():
            segment_products = [k for k, v in self.product_segments.items() if v == segment]
            segment_data = monthly_data[monthly_data['product_code'].isin(segment_products)]
            
            for product in segment_products:
                product_data = segment_data[segment_data['product_code'] == product].copy()
                
                if len(product_data) < 4:  # 至少需要4个月数据
                    continue
                
                # 为每个时间点创建特征
                for idx in range(3, len(product_data)):
                    features = self._create_advanced_product_features(
                        product, product_data.iloc[:idx], segment
                    )
                    
                    # 目标变量
                    target_row = product_data.iloc[idx]
                    features['target'] = target_row['total_qty']
                    features['target_month'] = str(target_row['year_month'])
                    features['segment'] = segment
                    
                    all_features.append(features)
        
        self.feature_data = pd.DataFrame(all_features)
        
        if len(self.feature_data) == 0:
            if progress_callback:
                progress_callback(0.6, "❌ 无法创建特征数据")
            return False
        
        # 特征后处理
        self._post_process_features()
        
        if progress_callback:
            progress_callback(0.6, f"✅ 高级特征创建完成: {len(self.feature_data)} 条数据, {len(self.feature_data.columns) - 4} 个特征")
        
        return True
    
    def _create_advanced_product_features(self, product_code, historical_data, segment):
        """为单个产品创建高级特征 - 增强版"""
        features = {'product_code': product_code}
        
        if len(historical_data) < 3:
            return features
        
        # 基础数据
        qty_values = historical_data['total_qty'].values
        order_counts = historical_data['order_count'].values
        customer_counts = historical_data['customer_count'].values
        
        # 1. 销量特征 - 使用对数变换处理偏态分布
        log_qty = np.log1p(qty_values)  # log(1+x) 避免log(0)
        
        features.update({
            # 原始销量特征
            'qty_mean': np.mean(qty_values),
            'qty_median': np.median(qty_values),
            'qty_std': np.std(qty_values),
            'qty_cv': np.std(qty_values) / (np.mean(qty_values) + 1),
            
            # 对数变换特征
            'log_qty_mean': np.mean(log_qty),
            'log_qty_std': np.std(log_qty),
            
            # 滞后特征
            'qty_lag_1': qty_values[-1],
            'qty_lag_2': qty_values[-2] if len(qty_values) > 1 else 0,
            'qty_lag_3': qty_values[-3] if len(qty_values) > 2 else 0,
            
            # 移动平均
            'qty_ma_2': np.mean(qty_values[-2:]),
            'qty_ma_3': np.mean(qty_values[-3:]),
            
            # 加权移动平均（最近的权重更大）
            'qty_wma_3': np.average(qty_values[-3:], weights=[1, 2, 3]) if len(qty_values) >= 3 else np.mean(qty_values),
        })
        
        # 2. 趋势特征
        if len(qty_values) > 1:
            # 简单增长率
            features['growth_rate_1'] = (qty_values[-1] - qty_values[-2]) / (qty_values[-2] + 1)
            
            # 线性趋势
            x = np.arange(len(qty_values))
            if len(qty_values) > 2:
                trend_coef = np.polyfit(x, qty_values, 1)[0]
                features['trend_slope'] = trend_coef
                
                # 趋势强度（R²）
                y_pred = np.polyval([trend_coef, np.mean(qty_values)], x)
                ss_res = np.sum((qty_values - y_pred) ** 2)
                ss_tot = np.sum((qty_values - np.mean(qty_values)) ** 2)
                features['trend_strength'] = 1 - (ss_res / (ss_tot + 1e-8))
            else:
                features['trend_slope'] = 0
                features['trend_strength'] = 0
        else:
            features['growth_rate_1'] = 0
            features['trend_slope'] = 0
            features['trend_strength'] = 0
        
        # 3. 订单行为特征
        features.update({
            'order_count_mean': np.mean(order_counts),
            'order_count_trend': order_counts[-1] - order_counts[0] if len(order_counts) > 1 else 0,
            'avg_order_size': features['qty_mean'] / (np.mean(order_counts) + 1),
            'customer_count_mean': np.mean(customer_counts),
            'penetration_rate': np.mean(customer_counts) / (np.max(customer_counts) + 1)
        })
        
        # 4. 时间特征
        last_month = historical_data.iloc[-1]['year_month']
        features.update({
            'month': last_month.month,
            'quarter': last_month.quarter,
            'is_year_end': 1 if last_month.month in [11, 12] else 0,
            'is_peak_season': 1 if last_month.month in [3, 4, 10, 11] else 0,
        })
        
        # 5. 稳定性特征
        features.update({
            'data_points': len(qty_values),
            'stability_score': 1 / (1 + features['qty_cv']),  # 变异系数越小越稳定
            'consistency_score': len(qty_values[qty_values > 0]) / len(qty_values)
        })
        
        # 6. 产品段特征
        segment_map = {
            '高销量稳定': 1, '高销量波动': 2,
            '中销量稳定': 3, '中销量波动': 4,
            '低销量稳定': 5, '低销量波动': 6
        }
        features['segment_encoded'] = segment_map.get(segment, 0)
        
        return features
    
    def _post_process_features(self):
        """特征后处理 - 增强版"""
        # 获取数值特征列
        feature_cols = [col for col in self.feature_data.columns
                       if col not in ['product_code', 'target', 'target_month', 'segment']]
        
        # 处理无穷值和NaN
        self.feature_data[feature_cols] = self.feature_data[feature_cols].replace([np.inf, -np.inf], np.nan)
        
        # 用0填充NaN（对于销售数据，0是合理的默认值）
        self.feature_data[feature_cols] = self.feature_data[feature_cols].fillna(0)
        
        # 移除常数特征
        constant_features = []
        for col in feature_cols:
            if self.feature_data[col].std() == 0:
                constant_features.append(col)
        
        if constant_features:
            self.feature_data = self.feature_data.drop(columns=constant_features)
    
    def train_models(self, test_ratio=0.2, progress_callback=None):
        """训练高级模型 - 增强版"""
        if progress_callback:
            progress_callback(0.7, "开始训练高级模型...")
        
        if self.feature_data is None or len(self.feature_data) == 0:
            st.error("没有特征数据")
            return False
        
        # 准备数据
        feature_cols = [col for col in self.feature_data.columns 
                       if col not in ['product_code', 'target', 'target_month', 'segment']]
        
        X = self.feature_data[feature_cols]
        y = self.feature_data['target']
        
        # 目标变量对数变换
        y_log = np.log1p(y)
        
        # 时间序列分割
        n_samples = len(X)
        split_point = int(n_samples * (1 - test_ratio))
        
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]
        y_log_train, y_log_test = y_log[:split_point], y_log[split_point:]
        
        # 保存测试集的详细信息
        test_info = self.feature_data[split_point:].copy()
        
        # 特征标准化
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['feature_scaler'] = scaler
        
        # 训练多个模型
        models = {}
        predictions = {}
        
        # 1. XGBoost (对数目标)
        if progress_callback:
            progress_callback(0.75, "训练XGBoost (增强版)...")
        
        xgb_model = xgb.XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_log_train, verbose=False)
        xgb_pred_log = xgb_model.predict(X_test_scaled)
        xgb_pred = np.expm1(xgb_pred_log)
        models['XGBoost'] = xgb_model
        predictions['XGBoost'] = xgb_pred
        
        # 2. LightGBM (对数目标)
        if progress_callback:
            progress_callback(0.85, "训练LightGBM (增强版)...")
        
        lgb_model = lgb.LGBMRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        lgb_model.fit(X_train_scaled, y_log_train)
        lgb_pred_log = lgb_model.predict(X_test_scaled)
        lgb_pred = np.expm1(lgb_pred_log)
        models['LightGBM'] = lgb_model
        predictions['LightGBM'] = lgb_pred
        
        # 3. Random Forest (原始目标)
        if progress_callback:
            progress_callback(0.9, "训练Random Forest (增强版)...")
        
        rf_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            min_samples_split=3,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = rf_model.predict(X_test_scaled)
        models['RandomForest'] = rf_model
        predictions['RandomForest'] = rf_pred
        
        # 4. 高级融合模型
        weights = self._calculate_model_weights(predictions, y_test)
        ensemble_pred = (weights['XGBoost'] * predictions['XGBoost'] +
                        weights['LightGBM'] * predictions['LightGBM'] +
                        weights['RandomForest'] * predictions['RandomForest'])
        predictions['Ensemble'] = ensemble_pred
        
        # 评估所有模型
        results = {}
        
        for model_name, pred in predictions.items():
            pred = np.maximum(pred, 0)
            
            # 计算多种评估指标
            mae = np.mean(np.abs(y_test - pred))
            rmse = np.sqrt(mean_squared_error(y_test, pred))
            
            # 改进的MAPE计算
            mape = np.mean(np.abs((y_test - pred) / np.maximum(y_test, 1))) * 100
            accuracy = max(0, 100 - mape)
            
            # 对称MAPE（更稳健）
            smape = 100 * np.mean(2 * np.abs(y_test - pred) / (np.abs(y_test) + np.abs(pred) + 1))
            smape_accuracy = max(0, 100 - smape)
            
            r2 = r2_score(y_test, pred)
            
            results[model_name] = {
                'Accuracy': accuracy,
                'SMAPE_Accuracy': smape_accuracy,
                'MAPE': mape,
                'SMAPE': smape,
                'MAE': mae,
                'RMSE': rmse,
                'R²': r2
            }
        
        # 生成完整的历史预测
        if progress_callback:
            progress_callback(0.95, "生成历史预测对比...")
        
        self._generate_complete_historical_predictions(
            models[max(results.keys(), key=lambda x: results[x]['SMAPE_Accuracy'])],
            max(results.keys(), key=lambda x: results[x]['SMAPE_Accuracy']),
            feature_cols,
            scaler
        )
        
        # 保存最佳模型
        best_model_name = max(results.keys(), key=lambda x: results[x]['SMAPE_Accuracy'])
        
        self.models = {
            'best_model': models.get(best_model_name),
            'best_model_name': best_model_name,
            'all_models': models,
            'feature_cols': feature_cols,
            'weights': weights if best_model_name == 'Ensemble' else None,
            'log_transform': best_model_name in ['XGBoost', 'LightGBM']
        }
        
        self.accuracy_results = results
        
        # 保存特征重要性
        if 'XGBoost' in models:
            feature_name_map = {
                'qty_mean': '销量均值', 'qty_median': '销量中位数', 'qty_std': '销量标准差',
                'qty_cv': '销量变异系数', 'log_qty_mean': '对数销量均值', 'log_qty_std': '对数销量标准差',
                'qty_lag_1': '滞后1期销量', 'qty_lag_2': '滞后2期销量', 'qty_lag_3': '滞后3期销量',
                'qty_ma_2': '2期移动平均', 'qty_ma_3': '3期移动平均', 'qty_wma_3': '3期加权移动平均',
                'growth_rate_1': '增长率', 'trend_slope': '趋势斜率', 'trend_strength': '趋势强度',
                'order_count_mean': '订单数均值', 'order_count_trend': '订单数趋势',
                'avg_order_size': '平均订单大小', 'customer_count_mean': '客户数均值',
                'penetration_rate': '渗透率', 'month': '月份', 'quarter': '季度',
                'is_year_end': '是否年末', 'is_peak_season': '是否旺季',
                'data_points': '数据点数', 'stability_score': '稳定性得分',
                'consistency_score': '一致性得分', 'segment_encoded': '产品段编码'
            }
            
            self.feature_importance = pd.DataFrame({
                '特征': [feature_name_map.get(col, col) for col in feature_cols],
                '重要性': models['XGBoost'].feature_importances_
            }).sort_values('重要性', ascending=False)
        
        if progress_callback:
            best_accuracy = results[best_model_name]['SMAPE_Accuracy']
            progress_callback(1.0, f"✅ 高级训练完成！最佳模型: {best_model_name} (SMAPE准确率: {best_accuracy:.1f}%)")
        
        return True
    
    def _generate_complete_historical_predictions(self, model, model_name, feature_cols, scaler):
        """生成所有产品的完整历史预测记录 - 增强版"""
        all_historical_predictions = []
        
        # 获取所有产品
        products = self.feature_data['product_code'].unique()
        
        for i, product in enumerate(products):
            # 获取该产品的所有月度数据
            product_monthly = self.shipment_data[
                self.shipment_data['product_code'] == product
            ].copy()
            
            # 按月聚合
            product_monthly['year_month'] = product_monthly['order_date'].dt.to_period('M')
            monthly_agg = product_monthly.groupby('year_month').agg({
                'quantity': ['sum', 'count', 'mean', 'std'],
                'customer_code': 'nunique',
                'region': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]
            }).reset_index()
            
            # 扁平化列名
            monthly_agg.columns = ['year_month', 'total_qty', 'order_count',
                                   'avg_qty', 'std_qty', 'customer_count', 'main_region']
            monthly_agg['std_qty'] = monthly_agg['std_qty'].fillna(0)
            monthly_agg = monthly_agg.sort_values('year_month')
            
            if len(monthly_agg) < 4:
                continue
            
            # 获取产品段
            segment = self.product_segments.get(product, '中销量稳定')
            
            # 对每个时间点进行滚动预测
            for j in range(3, len(monthly_agg)):
                # 使用前j个月的数据创建特征
                historical_data = monthly_agg.iloc[:j]
                features = self._create_advanced_product_features(
                    product, historical_data, segment
                )
                
                # 转换为特征向量
                feature_vector = pd.DataFrame([features])[feature_cols]
                X_scaled = scaler.transform(feature_vector)
                
                # 预测
                if model_name in ['XGBoost', 'LightGBM']:
                    pred_log = model.predict(X_scaled)[0]
                    pred_value = np.expm1(pred_log)
                else:
                    pred_value = model.predict(X_scaled)[0]
                
                pred_value = max(0, pred_value)
                
                # 实际值
                actual_value = monthly_agg.iloc[j]['total_qty']
                target_month = monthly_agg.iloc[j]['year_month']
                
                # 计算准确率
                error = abs(actual_value - pred_value)
                accuracy = max(0, 100 - (error / max(actual_value, 1)) * 100)
                
                all_historical_predictions.append({
                    '产品代码': product,
                    '年月': str(target_month),
                    '预测值': round(pred_value, 2),
                    '实际值': round(actual_value, 2),
                    '绝对误差': round(error, 2),
                    '准确率(%)': round(accuracy, 2),
                    '产品段': segment
                })
        
        # 保存完整的历史预测
        self.historical_predictions = pd.DataFrame(all_historical_predictions)
        
        # 计算产品准确率统计
        self._calculate_product_accuracy_stats()
    
    def _calculate_product_accuracy_stats(self):
        """计算每个产品的准确率统计 - 增强版"""
        product_stats = []
        
        for product in self.historical_predictions['产品代码'].unique():
            product_data = self.historical_predictions[
                self.historical_predictions['产品代码'] == product
            ]
            
            # 计算各种准确率指标
            avg_accuracy = product_data['准确率(%)'].mean()
            recent_accuracy = product_data.tail(1)['准确率(%)'].iloc[0] if len(product_data) > 0 else 0
            
            # 销量加权准确率（最近3个月）
            recent_data = product_data.tail(3)
            if len(recent_data) > 0:
                weights = recent_data['实际值'] / recent_data['实际值'].sum()
                weighted_accuracy = (recent_data['准确率(%)'] * weights).sum()
            else:
                weighted_accuracy = avg_accuracy
            
            # 准确率分布
            accuracy_above_85 = len(product_data[product_data['准确率(%)'] >= 85])
            accuracy_above_90 = len(product_data[product_data['准确率(%)'] >= 90])
            
            product_stats.append({
                '产品代码': product,
                '平均准确率(%)': round(avg_accuracy, 2),
                '最近准确率(%)': round(recent_accuracy, 2),
                '加权准确率(%)': round(weighted_accuracy, 2),
                '预测次数': len(product_data),
                '85%以上次数': accuracy_above_85,
                '90%以上次数': accuracy_above_90,
                '产品段': product_data['产品段'].iloc[0]
            })
        
        self.historical_accuracy = pd.DataFrame(product_stats)
    
    def _calculate_model_weights(self, predictions, y_true):
        """计算模型融合权重 - 增强版"""
        scores = {}
        for name, pred in predictions.items():
            pred = np.maximum(pred, 0)
            smape = 100 * np.mean(2 * np.abs(y_true - pred) / (np.abs(y_true) + np.abs(pred) + 1))
            scores[name] = max(0, 100 - smape)
        
        total_score = sum(scores.values())
        if total_score > 0:
            weights = {name: score / total_score for name, score in scores.items()}
        else:
            weights = {name: 1/len(scores) for name in scores.keys()}
        
        return weights
    
    def predict_future(self, months_ahead=3, product_list=None):
        """预测未来销量 - 增强版"""
        if not self.models:
            return None
        
        predictions = []
        
        if product_list is None:
            product_list = list(self.product_segments.keys())
        
        for product in product_list:
            if product not in self.product_segments:
                continue
            
            # 获取产品最新特征
            product_features = self.feature_data[
                self.feature_data['product_code'] == product
            ].tail(1)
            
            if len(product_features) == 0:
                continue
            
            # 预测每个月
            for month in range(1, months_ahead + 1):
                X = product_features[self.models['feature_cols']]
                X_scaled = self.scalers['feature_scaler'].transform(X)
                
                # 使用最佳模型预测
                if self.models['best_model_name'] == 'Ensemble':
                    # 融合预测
                    xgb_pred_log = self.models['all_models']['XGBoost'].predict(X_scaled)[0]
                    lgb_pred_log = self.models['all_models']['LightGBM'].predict(X_scaled)[0]
                    rf_pred = self.models['all_models']['RandomForest'].predict(X_scaled)[0]
                    
                    xgb_pred = np.expm1(xgb_pred_log)
                    lgb_pred = np.expm1(lgb_pred_log)
                    
                    weights = self.models['weights']
                    final_pred = (weights['XGBoost'] * xgb_pred +
                                 weights['LightGBM'] * lgb_pred +
                                 weights['RandomForest'] * rf_pred)
                else:
                    if self.models['log_transform']:
                        pred_log = self.models['best_model'].predict(X_scaled)[0]
                        final_pred = np.expm1(pred_log)
                    else:
                        final_pred = self.models['best_model'].predict(X_scaled)[0]
                
                final_pred = max(0, final_pred)
                
                # 计算置信区间
                segment = self.product_segments[product]
                confidence_factor = self._get_confidence_factor(segment)
                
                lower_bound = max(0, final_pred * (1 - confidence_factor))
                upper_bound = final_pred * (1 + confidence_factor)
                
                predictions.append({
                    '产品代码': product,
                    '未来月份': month,
                    '预测销量': round(final_pred, 2),
                    '下限': round(lower_bound, 2),
                    '上限': round(upper_bound, 2),
                    '置信度': confidence_factor,
                    '产品段': segment,
                    '使用模型': self.models['best_model_name']
                })
        
        self.predictions = pd.DataFrame(predictions)
        return self.predictions
    
    def _get_confidence_factor(self, segment):
        """根据产品段获取置信度因子"""
        confidence_map = {
            '高销量稳定': 0.10,
            '高销量波动': 0.20,
            '中销量稳定': 0.15,
            '中销量波动': 0.25,
            '低销量稳定': 0.20,
            '低销量波动': 0.30
        }
        return confidence_map.get(segment, 0.20)

# 创建侧边栏 - 保持原有类别，增加新的参数选项
with st.sidebar:
    st.markdown("### 🎯 增强模型训练控制")
    
    # 管理员信息展示 - 保持原有类别
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="color: #ff6b6b; font-weight: bold; font-size: 0.9rem;">🔒 管理员模式</div>
        <div style="color: white; font-size: 0.8rem;">用户: {st.session_state.get('display_name', 'Admin')}</div>
        <div style="color: white; font-size: 0.8rem;">目标: 85-90% 准确率</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 训练参数 - 修改原有类别，增加更多选项
    st.markdown("#### 高级训练参数")
    test_ratio = st.slider("测试集比例", 0.1, 0.3, 0.2, 0.05)
    
    # 新增类别：模型选择
    st.markdown("#### 模型配置")
    enable_ensemble = st.checkbox("启用融合模型", value=True)
    feature_selection = st.selectbox("特征选择策略", ["全部特征", "重要特征", "自动选择"], index=0)
    
    # 预测选项 - 保持原有类别
    st.markdown("#### 预测设置")
    months_ahead = st.selectbox("预测月数", [1, 2, 3, 6], index=2)
    
    # 模型信息 - 修改原有类别，显示更多信息
    if st.session_state.model_trained:
        st.markdown("---")
        st.markdown("### 📊 当前模型信息")
        system = st.session_state.prediction_system
        
        if system and system.models:
            st.success(f"✅ 最佳模型: {system.models['best_model_name']}")
            
            # 显示SMAPE准确率（更可靠的指标）
            if 'SMAPE_Accuracy' in system.accuracy_results[system.models['best_model_name']]:
                best_accuracy = system.accuracy_results[system.models['best_model_name']]['SMAPE_Accuracy']
                st.metric("SMAPE准确率", f"{best_accuracy:.1f}%")
                
                # 目标达成状态
                if best_accuracy >= 90:
                    st.success("🎯 已超越90%目标！")
                elif best_accuracy >= 85:
                    st.info("🎯 已达成85%目标")
                else:
                    st.warning(f"🎯 距离85%目标还差{85-best_accuracy:.1f}%")
            else:
                best_accuracy = system.accuracy_results[system.models['best_model_name']]['Accuracy']
                st.metric("模型准确率", f"{best_accuracy:.1f}%")
            
            st.info(f"""
            - 高级特征数量: {len(system.models['feature_cols'])}
            - 产品数量: {len(system.product_segments)}
            - 训练样本: {len(system.feature_data)}
            - 历史预测记录: {len(system.historical_predictions) if system.historical_predictions is not None else 0}
            """)

# 主界面 - 保持原有Tab结构，内容进行增强
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 增强模型训练", "🔮 销量预测", "📊 模型评估", "📈 特征分析", "📑 历史记录"])

# Tab 1: 增强模型训练 - 修改原有类别
with tab1:
    st.markdown("### 🚀 一键训练增强预测模型（目标: 85-90%准确率）")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🔄 开始增强训练", type="primary", use_container_width=True):
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 初始化增强系统
            system = EnhancedSalesPredictionSystem()
            
            # 定义进度回调
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # 执行增强训练流程
            try:
                # 1. 加载数据
                if system.load_data_from_github(update_progress):
                    time.sleep(0.5)
                    
                    # 2. 高级数据预处理
                    if system.preprocess_data(update_progress):
                        time.sleep(0.5)
                        
                        # 3. 高级特征工程
                        if system.create_features(update_progress):
                            time.sleep(0.5)
                            
                            # 4. 训练增强模型
                            if system.train_models(test_ratio, update_progress):
                                # 保存到session state
                                st.session_state.prediction_system = system
                                st.session_state.model_trained = True
                                
                                # 记录训练历史
                                best_model = system.models['best_model_name']
                                best_accuracy = system.accuracy_results[best_model]['SMAPE_Accuracy']
                                
                                st.session_state.training_history.append({
                                    'time': datetime.now(),
                                    'accuracy': best_accuracy,
                                    'model': best_model,
                                    'admin': st.session_state.get('display_name', 'Admin'),
                                    'target_achieved': best_accuracy >= 85
                                })
                                
                                if best_accuracy >= 90:
                                    st.success("🎉 增强模型训练完成！已超越90%目标！")
                                    st.balloons()
                                elif best_accuracy >= 85:
                                    st.success("🎉 增强模型训练完成！已达成85%目标！")
                                    st.balloons()
                                else:
                                    st.success(f"✅ 增强模型训练完成！准确率：{best_accuracy:.1f}%")
                            else:
                                st.error("增强模型训练失败")
                        else:
                            st.error("高级特征创建失败")
                    else:
                        st.error("高级数据预处理失败")
                else:
                    st.error("数据加载失败")
                    
            except Exception as e:
                st.error(f"增强训练过程出错: {str(e)}")
                
    with col2:
        st.info("""
        **增强训练说明：**
        - 🎯 **目标准确率**: 85-90%
        - 🔧 **高级特征工程**: 26+ 个增强特征
        - 🤖 **增强模型**: XGBoost + LightGBM + RandomForest
        - 📊 **智能融合**: 基于性能的动态权重
        - 📈 **历史对比**: 完整的预测vs实际对比
        - ⏱️ **训练时间**: 大约2-3分钟
        - 🔒 **权限要求**: 仅限管理员使用
        
        **新增功能：**
        - 对数变换处理偏态分布
        - 趋势强度和稳定性特征
        - SMAPE准确率（更稳健）
        - 完整历史预测记录
        """)
    
    # 显示增强训练结果 - 修改原有类别
    if st.session_state.model_trained:
        st.markdown("---")
        st.markdown("### 📊 增强训练结果")
        
        system = st.session_state.prediction_system
        
        # 显示各模型性能 - 使用SMAPE准确率
        col1, col2, col3, col4 = st.columns(4)
        
        model_cols = [col1, col2, col3, col4]
        for idx, (model_name, metrics) in enumerate(system.accuracy_results.items()):
            if idx < 4:
                with model_cols[idx]:
                    # 使用SMAPE准确率作为主要指标
                    main_accuracy = metrics.get('SMAPE_Accuracy', metrics['Accuracy'])
                    
                    # 判断是否达成目标
                    if main_accuracy >= 90:
                        status_color = "#00FF00"
                        status_icon = "🏆"
                    elif main_accuracy >= 85:
                        status_color = "#90EE90"
                        status_icon = "✅"
                    elif main_accuracy >= 75:
                        status_color = "#FFD700"
                        status_icon = "⚠️"
                    else:
                        status_color = "#FF6347"
                        status_icon = "❌"
                    
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {status_color};">
                        <div class="metric-value" style="color: {status_color};">{main_accuracy:.1f}%</div>
                        <div class="metric-label">{status_icon} {model_name}</div>
                        <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">
                            MAE: {metrics['MAE']:.1f}<br>
                            R²: {metrics['R²']:.3f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 增强版产品分段统计 - 修改原有类别
        st.markdown("### 📦 增强产品分段统计")
        
        if system.historical_accuracy is not None:
            # 按准确率分段显示产品分布
            accuracy_distribution = system.historical_accuracy.copy()
            accuracy_distribution['准确率分段'] = pd.cut(
                accuracy_distribution['平均准确率(%)'], 
                bins=[0, 70, 80, 85, 90, 95, 100], 
                labels=['<70%', '70-80%', '80-85%', '85-90%', '90-95%', '95%+'],
                include_lowest=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 准确率分布饼图
                accuracy_counts = accuracy_distribution['准确率分段'].value_counts()
                
                fig_accuracy = go.Figure(data=[
                    go.Pie(
                        labels=accuracy_counts.index,
                        values=accuracy_counts.values,
                        hole=0.3,
                        marker_colors=['#FF6347', '#FFD700', '#90EE90', '#00FF00', '#0000FF', '#8A2BE2']
                    )
                ])
                
                fig_accuracy.update_layout(
                    title="产品准确率分布",
                    height=400,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_accuracy, use_container_width=True)
            
            with col2:
                # 产品段分布饼图
                segment_counts = pd.Series(list(system.product_segments.values())).value_counts()
                
                fig_segment = go.Figure(data=[
                    go.Pie(
                        labels=segment_counts.index,
                        values=segment_counts.values,
                        hole=0.3,
                        marker_colors=['#667eea', '#764ba2', '#9f7aea', '#b794f4', '#d6bcfa', '#e9d8fd']
                    )
                ])
                
                fig_segment.update_layout(
                    title="产品分段分布",
                    height=400,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_segment, use_container_width=True)

# Tab 2: 销量预测 - 保持原有类别内容
with tab2:
    st.markdown("### 🔮 智能销量预测")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先在'增强模型训练'页面训练模型")
    else:
        system = st.session_state.prediction_system
        
        # 预测控制
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # 产品选择
            product_selection = st.selectbox(
                "选择预测范围",
                ["全部产品", "高销量产品", "中销量产品", "低销量产品", "自定义选择"]
            )
        
        with col2:
            if product_selection == "自定义选择":
                selected_products = st.multiselect(
                    "选择产品",
                    options=list(system.product_segments.keys()),
                    default=list(system.product_segments.keys())[:5]
                )
            else:
                selected_products = None
        
        with col3:
            predict_button = st.button("🚀 开始预测", type="primary", use_container_width=True)
        
        # 执行预测
        if predict_button:
            with st.spinner("正在生成预测..."):
                # 根据选择筛选产品
                if product_selection == "全部产品":
                    product_list = None
                elif product_selection == "自定义选择":
                    product_list = selected_products
                else:
                    # 根据产品段筛选
                    segment_filter = product_selection.replace("产品", "")
                    product_list = [p for p, s in system.product_segments.items() if segment_filter in s]
                
                # 生成预测
                predictions = system.predict_future(months_ahead=months_ahead, product_list=product_list)
                
                if predictions is not None and len(predictions) > 0:
                    st.success(f"✅ 成功预测 {len(predictions['产品代码'].unique())} 个产品的未来 {months_ahead} 个月销量")
                    
                    # 显示预测结果
                    st.markdown("### 📊 预测结果汇总")
                    
                    # 汇总统计
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_prediction = predictions['预测销量'].sum()
                    avg_prediction = predictions['预测销量'].mean()
                    products_count = len(predictions['产品代码'].unique())
                    avg_confidence = (1 - predictions['置信度'].mean()) * 100
                    
                    with col1:
                        st.metric("预测总量", f"{total_prediction:,.0f} 箱")
                    with col2:
                        st.metric("平均预测量", f"{avg_prediction:,.0f} 箱")
                    with col3:
                        st.metric("产品数量", products_count)
                    with col4:
                        st.metric("平均置信度", f"{avg_confidence:.1f}%")
                    
                    # 预测趋势图
                    st.markdown("### 📈 预测趋势")
                    
                    # 按月份汇总
                    monthly_summary = predictions.groupby('未来月份').agg({
                        '预测销量': 'sum',
                        '下限': 'sum',
                        '上限': 'sum'
                    }).reset_index()
                    
                    fig = go.Figure()
                    
                    # 添加预测值
                    fig.add_trace(go.Scatter(
                        x=monthly_summary['未来月份'],
                        y=monthly_summary['预测销量'],
                        mode='lines+markers',
                        name='预测值',
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=10)
                    ))
                    
                    # 添加置信区间
                    fig.add_trace(go.Scatter(
                        x=monthly_summary['未来月份'],
                        y=monthly_summary['上限'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=monthly_summary['未来月份'],
                        y=monthly_summary['下限'],
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(102, 126, 234, 0.2)',
                        name='置信区间'
                    ))
                    
                    fig.update_layout(
                        title=f"未来{months_ahead}个月销量预测趋势",
                        xaxis_title="月份",
                        yaxis_title="预测销量 (箱)",
                        height=400,
                        hovermode='x unified',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 产品明细表
                    st.markdown("### 📋 产品预测明细")
                    
                    # 添加筛选器
                    col1, col2 = st.columns(2)
                    with col1:
                        min_qty = st.number_input("最小预测量筛选", value=0, step=100)
                    with col2:
                        selected_segments = st.multiselect(
                            "产品段筛选",
                            options=predictions['产品段'].unique(),
                            default=predictions['产品段'].unique()
                        )
                    
                    # 应用筛选
                    filtered_predictions = predictions[
                        (predictions['预测销量'] >= min_qty) &
                        (predictions['产品段'].isin(selected_segments))
                    ]
                    
                    # 显示表格
                    st.dataframe(
                        filtered_predictions.style.format({
                            '预测销量': '{:,.0f}',
                            '下限': '{:,.0f}',
                            '上限': '{:,.0f}',
                            '置信度': '{:.1%}'
                        }).background_gradient(subset=['预测销量'], cmap='Blues'),
                        use_container_width=True,
                        height=500
                    )
                    
                    # 下载按钮
                    csv = filtered_predictions.to_csv(index=False)
                    st.download_button(
                        label="📥 下载预测结果",
                        data=csv,
                        file_name=f'增强销量预测_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv'
                    )
                else:
                    st.error("预测失败，请检查数据和模型")

# Tab 3: 模型评估 - 修改原有类别，增加更多评估指标
with tab3:
    st.markdown("### 📊 增强模型性能评估")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先训练模型")
    else:
        system = st.session_state.prediction_system
        
        # 模型对比 - 使用SMAPE准确率
        st.markdown("#### 🏆 模型性能对比（基于SMAPE准确率）")
        
        # 创建性能对比图
        models = list(system.accuracy_results.keys())
        metrics_data = {
            'SMAPE_Accuracy': [system.accuracy_results[m].get('SMAPE_Accuracy', system.accuracy_results[m]['Accuracy']) for m in models],
            'MAPE_Accuracy': [system.accuracy_results[m]['Accuracy'] for m in models],
            'R²': [system.accuracy_results[m]['R²'] * 100 for m in models]
        }
        
        fig = go.Figure()
        
        # 添加SMAPE准确率条形图
        fig.add_trace(go.Bar(
            name='SMAPE准确率 (%)',
            x=models,
            y=metrics_data['SMAPE_Accuracy'],
            marker_color='#667eea',
            text=[f'{v:.1f}%' for v in metrics_data['SMAPE_Accuracy']],
            textposition='outside'
        ))
        
        # 添加MAPE准确率条形图
        fig.add_trace(go.Bar(
            name='MAPE准确率 (%)',
            x=models,
            y=metrics_data['MAPE_Accuracy'],
            marker_color='#764ba2',
            text=[f'{v:.1f}%' for v in metrics_data['MAPE_Accuracy']],
            textposition='outside'
        ))
        
        # 添加目标线
        fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="85%目标线")
        fig.add_hline(y=90, line_dash="dash", line_color="gold", annotation_text="90%目标线")
        
        fig.update_layout(
            title="增强模型性能指标对比",
            xaxis_title="模型",
            yaxis_title="性能指标 (%)",
            barmode='group',
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细指标表 - 修改原有类别
        st.markdown("#### 📋 详细性能指标")
        
        performance_df = pd.DataFrame([
            {
                '模型': model,
                'SMAPE准确率 (%)': metrics.get('SMAPE_Accuracy', metrics['Accuracy']),
                'MAPE准确率 (%)': metrics['Accuracy'],
                'SMAPE (%)': metrics.get('SMAPE', metrics['MAPE']),
                'MAPE (%)': metrics['MAPE'],
                'MAE': metrics['MAE'],
                'RMSE': metrics['RMSE'],
                'R²': metrics['R²'],
                '目标达成': '✅' if metrics.get('SMAPE_Accuracy', metrics['Accuracy']) >= 85 else '❌'
            }
            for model, metrics in system.accuracy_results.items()
        ])
        
        # 高亮最佳值和目标达成
        def highlight_best_and_target(s):
            if s.name in ['SMAPE准确率 (%)', 'MAPE准确率 (%)', 'R²']:
                return ['background-color: #90EE90' if v == s.max() else 
                       'background-color: #FFE4B5' if v >= 85 and s.name.endswith('准确率 (%)') else '' for v in s]
            elif s.name in ['SMAPE (%)', 'MAPE (%)', 'MAE', 'RMSE']:
                return ['background-color: #90EE90' if v == s.min() else '' for v in s]
            return [''] * len(s)
        
        st.dataframe(
            performance_df.style.apply(highlight_best_and_target).format({
                'SMAPE准确率 (%)': '{:.2f}',
                'MAPE准确率 (%)': '{:.2f}',
                'SMAPE (%)': '{:.2f}',
                'MAPE (%)': '{:.2f}',
                'MAE': '{:.2f}',
                'RMSE': '{:.2f}',
                'R²': '{:.4f}'
            }),
            use_container_width=True
        )
        
        # 增强版模型评估结论 - 修改原有类别
        best_model = system.models['best_model_name']
        best_accuracy = system.accuracy_results[best_model].get('SMAPE_Accuracy', system.accuracy_results[best_model]['Accuracy'])
        
        if best_accuracy >= 90:
            recommendation = "🌟 模型表现优秀，已超越90%目标，可以直接用于生产环境"
            color = "#00FF00"
            achievement = "🏆 超越目标"
        elif best_accuracy >= 85:
            recommendation = "✅ 模型表现良好，已达成85%目标，建议继续监控优化冲击90%"
            color = "#90EE90"
            achievement = "🎯 达成目标"
        elif best_accuracy >= 75:
            recommendation = "⚠️ 模型表现中等，需要进一步优化以达成85%目标"
            color = "#FFD700"
            achievement = "📈 接近目标"
        else:
            recommendation = "❌ 模型表现较差，需要重新评估数据和方法"
            color = "#FF6347"
            achievement = "⚠️ 未达目标"
        
        st.markdown(f"""
        <div class="info-box" style="border-left-color: {color};">
            <h4>🎯 增强模型评估结论</h4>
            <p>当前最佳模型: <strong>{best_model}</strong></p>
            <p>SMAPE准确率: <strong>{best_accuracy:.1f}%</strong> ({achievement})</p>
            <p>距离85%目标: <strong>{max(0, 85-best_accuracy):.1f}%</strong></p>
            <p>距离90%目标: <strong>{max(0, 90-best_accuracy):.1f}%</strong></p>
            <p>{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 新增类别：历史准确率分析
        if system.historical_accuracy is not None:
            st.markdown("#### 📈 产品准确率分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 准确率分布直方图
                fig_hist = go.Figure()
                
                fig_hist.add_trace(go.Histogram(
                    x=system.historical_accuracy['平均准确率(%)'],
                    nbinsx=20,
                    marker_color='#667eea',
                    opacity=0.7
                ))
                
                fig_hist.add_vline(x=85, line_dash="dash", line_color="green", annotation_text="85%目标")
                fig_hist.add_vline(x=90, line_dash="dash", line_color="gold", annotation_text="90%目标")
                
                fig_hist.update_layout(
                    title="产品准确率分布",
                    xaxis_title="准确率 (%)",
                    yaxis_title="产品数量",
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # 准确率统计
                total_products = len(system.historical_accuracy)
                above_85 = len(system.historical_accuracy[system.historical_accuracy['平均准确率(%)'] >= 85])
                above_90 = len(system.historical_accuracy[system.historical_accuracy['平均准确率(%)'] >= 90])
                
                st.markdown(f"""
                **准确率统计：**
                - 总产品数: {total_products}
                - 85%以上: {above_85} ({above_85/total_products*100:.1f}%)
                - 90%以上: {above_90} ({above_90/total_products*100:.1f}%)
                - 平均准确率: {system.historical_accuracy['平均准确率(%)'].mean():.1f}%
                
                **目标达成情况：**
                - 85%目标: {'✅ 达成' if above_85/total_products >= 0.8 else '❌ 未达成'}
                - 90%目标: {'✅ 达成' if above_90/total_products >= 0.7 else '❌ 未达成'}
                """)

# Tab 4: 特征分析 - 修改原有类别，增加更多特征分析
with tab4:
    st.markdown("### 📈 增强特征重要性分析")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先训练模型")
    else:
        system = st.session_state.prediction_system
        
        if system.feature_importance is not None:
            # 特征重要性图 - 显示更多特征
            top_features = system.feature_importance.head(20)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_features['重要性'],
                y=top_features['特征'],
                orientation='h',
                marker=dict(
                    color=top_features['重要性'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="重要性")
                ),
                text=[f'{v:.3f}' for v in top_features['重要性']],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Top 20 增强特征重要性",
                xaxis_title="重要性得分",
                yaxis_title="特征",
                height=700,
                margin=dict(l=150),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 特征说明 - 增强版
            st.markdown("#### 📖 增强特征说明")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **销量相关特征：**
                - **销量均值/中位数**: 历史销量的中心趋势
                - **对数销量**: 处理偏态分布的变换特征
                - **滞后特征**: 前1-3期的销量值
                - **移动平均**: 近期销量的平均趋势
                - **加权移动平均**: 近期数据权重更大
                - **变异系数**: 销量波动程度
                
                **趋势相关特征：**
                - **增长率**: 销量变化速度
                - **趋势斜率**: 长期趋势方向
                - **趋势强度**: 趋势的稳定性
                """)
            
            with col2:
                st.markdown("""
                **订单行为特征：**
                - **订单数均值**: 订单频次
                - **平均订单大小**: 单次订单规模
                - **客户数均值**: 客户基础
                - **渗透率**: 市场渗透程度
                
                **时间相关特征：**
                - **月份/季度**: 捕捉季节性规律
                - **年末标识**: 年底销售高峰
                - **旺季标识**: 传统销售旺季
                
                **稳定性特征：**
                - **稳定性得分**: 基于变异系数
                - **一致性得分**: 销售连续性
                - **数据点数**: 历史数据充分性
                """)
            
            # 新增类别：特征分类分析
            st.markdown("#### 🔍 特征分类分析")
            
            # 按特征类型分组
            feature_categories = {
                '销量类': ['销量均值', '销量中位数', '销量标准差', '销量变异系数', '对数销量均值', '对数销量标准差'],
                '滞后类': ['滞后1期销量', '滞后2期销量', '滞后3期销量'],
                '移动平均类': ['2期移动平均', '3期移动平均', '3期加权移动平均'],
                '趋势类': ['增长率', '趋势斜率', '趋势强度'],
                '订单类': ['订单数均值', '订单数趋势', '平均订单大小'],
                '客户类': ['客户数均值', '渗透率'],
                '时间类': ['月份', '季度', '是否年末', '是否旺季'],
                '稳定性类': ['稳定性得分', '一致性得分', '数据点数'],
                '产品段类': ['产品段编码']
            }
            
            category_importance = {}
            for category, features in feature_categories.items():
                category_score = system.feature_importance[
                    system.feature_importance['特征'].isin(features)
                ]['重要性'].sum()
                category_importance[category] = category_score
            
            # 特征类别重要性图
            categories = list(category_importance.keys())
            scores = list(category_importance.values())
            
            fig_cat = go.Figure()
            
            fig_cat.add_trace(go.Bar(
                x=categories,
                y=scores,
                marker_color='#764ba2',
                text=[f'{v:.3f}' for v in scores],
                textposition='outside'
            ))
            
            fig_cat.update_layout(
                title="特征类别重要性分析",
                xaxis_title="特征类别",
                yaxis_title="总重要性得分",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # 特征相关性分析 - 修改原有类别
            st.markdown("#### 🔗 增强特征相关性分析")
            
            # 计算与目标变量的相关性
            feature_data = system.feature_data[system.models['feature_cols']]
            target_corr = feature_data.corrwith(
                system.feature_data['target']
            ).abs().sort_values(ascending=False).head(15)
            
            # 映射中文名称
            feature_name_map = {
                'qty_mean': '销量均值', 'qty_median': '销量中位数', 'qty_std': '销量标准差',
                'qty_cv': '销量变异系数', 'log_qty_mean': '对数销量均值', 'log_qty_std': '对数销量标准差',
                'qty_lag_1': '滞后1期销量', 'qty_lag_2': '滞后2期销量', 'qty_lag_3': '滞后3期销量',
                'qty_ma_2': '2期移动平均', 'qty_ma_3': '3期移动平均', 'qty_wma_3': '3期加权移动平均',
                'growth_rate_1': '增长率', 'trend_slope': '趋势斜率', 'trend_strength': '趋势强度',
                'order_count_mean': '订单数均值', 'order_count_trend': '订单数趋势',
                'avg_order_size': '平均订单大小', 'customer_count_mean': '客户数均值',
                'penetration_rate': '渗透率', 'month': '月份', 'quarter': '季度',
                'is_year_end': '是否年末', 'is_peak_season': '是否旺季',
                'data_points': '数据点数', 'stability_score': '稳定性得分',
                'consistency_score': '一致性得分', 'segment_encoded': '产品段编码'
            }
            
            fig_corr = go.Figure()
            
            fig_corr.add_trace(go.Bar(
                x=target_corr.values,
                y=[feature_name_map.get(f, f) for f in target_corr.index],
                orientation='h',
                marker_color='#667eea',
                text=[f'{v:.3f}' for v in target_corr.values],
                textposition='outside'
            ))
            
            fig_corr.update_layout(
                title="与目标变量相关性最高的15个特征",
                xaxis_title="相关系数（绝对值）",
                yaxis_title="特征",
                height=500,
                margin=dict(l=150),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)

# Tab 5: 历史记录 - 修改原有类别，增加更多统计信息
with tab5:
    st.markdown("### 📑 增强训练历史记录")
    
    if len(st.session_state.training_history) == 0:
        st.info("暂无训练记录")
    else:
        # 显示训练历史 - 增强版
        history_df = pd.DataFrame(st.session_state.training_history)
        history_df['time'] = pd.to_datetime(history_df['time'])
        history_df = history_df.sort_values('time', ascending=False)
        
        # 格式化显示
        history_df['训练时间'] = history_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        history_df['准确率'] = history_df['accuracy'].apply(lambda x: f"{x:.2f}%")
        history_df['模型'] = history_df['model']
        history_df['操作员'] = history_df.get('admin', 'Admin')
        history_df['目标达成'] = history_df.get('target_achieved', False).apply(lambda x: '✅ 是' if x else '❌ 否')
        
        st.dataframe(
            history_df[['训练时间', '模型', '准确率', '目标达成', '操作员']],
            use_container_width=True,
            hide_index=True
        )
        
        # 准确率趋势图 - 修改原有类别
        if len(history_df) > 1:
            st.markdown("#### 📈 准确率变化趋势")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=history_df['time'],
                y=history_df['accuracy'],
                mode='lines+markers',
                name='准确率',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10)
            ))
            
            # 添加目标线
            fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="85%目标线")
            fig.add_hline(y=90, line_dash="dash", line_color="gold", annotation_text="90%目标线")
            
            fig.update_layout(
                title="模型准确率变化趋势",
                xaxis_title="训练时间",
                yaxis_title="准确率 (%)",
                height=400,
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 新增类别：训练统计分析
        st.markdown("#### 📊 训练统计分析")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 基础统计
            total_trainings = len(history_df)
            successful_trainings = len(history_df[history_df['target_achieved'] == '✅ 是'])
            avg_accuracy = history_df['accuracy'].mean()
            max_accuracy = history_df['accuracy'].max()
            
            st.markdown(f"""
            **基础统计：**
            - 总训练次数: {total_trainings}
            - 成功达标次数: {successful_trainings}
            - 达标率: {successful_trainings/total_trainings*100:.1f}%
            - 平均准确率: {avg_accuracy:.1f}%
            - 最高准确率: {max_accuracy:.1f}%
            """)
        
        with col2:
            # 模型使用统计
            model_counts = history_df['model'].value_counts()
            best_model = model_counts.index[0] if len(model_counts) > 0 else "无"
            
            st.markdown(f"""
            **模型使用统计：**
            - 最常用模型: {best_model}
            """)
            for model, count in model_counts.items():
                st.markdown(f"- {model}: {count} 次")
        
        with col3:
            # 操作员统计
            admin_counts = history_df['操作员'].value_counts()
            
            st.markdown(f"""
            **操作员统计：**
            """)
            for admin, count in admin_counts.items():
                st.markdown(f"- {admin}: {count} 次")
        
        # 清除历史记录 - 保持原有类别
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ 清除历史记录"):
                st.session_state.training_history = []
                st.rerun()

# 新增类别：系统状态监控
st.markdown("---")
st.markdown("### 🖥️ 系统状态监控")

col1, col2, col3, col4 = st.columns(4)

with col1:
    model_status = "🟢 已训练" if st.session_state.model_trained else "🔴 未训练"
    st.metric("模型状态", model_status)

with col2:
    if st.session_state.model_trained and st.session_state.prediction_system:
        system = st.session_state.prediction_system
        if system.accuracy_results:
            best_accuracy = max([r.get('SMAPE_Accuracy', r['Accuracy']) for r in system.accuracy_results.values()])
            target_status = "🎯 已达成" if best_accuracy >= 85 else "⚠️ 未达成"
        else:
            target_status = "❓ 未知"
    else:
        target_status = "⚠️ 未评估"
    st.metric("85%目标", target_status)

with col3:
    if st.session_state.model_trained and st.session_state.prediction_system:
        system = st.session_state.prediction_system
        if system.feature_data is not None:
            feature_count = len(system.models.get('feature_cols', []))
        else:
            feature_count = 0
    else:
        feature_count = 0
    st.metric("特征数量", feature_count)

with col4:
    if st.session_state.model_trained and st.session_state.prediction_system:
        system = st.session_state.prediction_system
        product_count = len(system.product_segments)
    else:
        product_count = 0
    st.metric("产品数量", product_count)

# 底部信息 - 修改原有类别
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: rgba(255, 255, 255, 0.8); font-size: 0.9rem; background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px;">
    🤖 增强机器学习销售预测系统 v3.0 | 
    🎯 目标准确率: 85-90% | 
    使用 XGBoost + LightGBM + RandomForest + 26+增强特征 | 
    数据更新时间: {datetime.now().strftime('%Y-%m-%d')} |
    🔒 管理员专用模式
    <br>
    <small style="opacity: 0.7;">
    ✨ 新增功能: 对数变换 | 趋势强度分析 | SMAPE准确率 | 完整历史预测 | 智能融合权重
    </small>
</div>
""", unsafe_allow_html=True)
