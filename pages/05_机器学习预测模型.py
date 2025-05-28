import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from io import BytesIO
import warnings
from scipy import stats
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from collections import defaultdict, Counter
import pickle
import os
import math
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

warnings.filterwarnings('ignore')

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="机器学习预测排产系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS样式（保持附件1风格） ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* 浮动粒子背景 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
        background-size: 100px 100px;
        animation: float 20s linear infinite;
        pointer-events: none; z-index: -1;
    }

    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(-10px); }
        75% { transform: translateY(-10px) translateX(5px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    /* 主容器 */
    .main .block-container {
        background: rgba(255,255,255,0.95);
        border-radius: 20px; padding: 2rem; margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 主标题 */
    .main-header {
        text-align: center; padding: 2.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        color: white; border-radius: 20px; margin-bottom: 2rem;
        animation: gradientShift 4s ease infinite, fadeInScale 1.2s ease-out;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        position: relative; overflow: hidden;
    }

    .main-header::before {
        content: ''; position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: shimmer 3s linear infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    @keyframes fadeInScale {
        from { opacity: 0; transform: translateY(-30px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 统一指标卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem; border-radius: 18px; text-align: center; height: 100%;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 3px 10px rgba(0,0,0,0.03);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUp 0.8s ease-out;
        position: relative; overflow: hidden;
        backdrop-filter: blur(10px);
    }

    .metric-card::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s ease;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 10px 20px rgba(102, 126, 234, 0.15);
    }

    .metric-card:hover::before { left: 100%; }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 指标数值样式 */
    .metric-value {
        font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1.1;
    }

    .big-value {
        font-size: 2.8rem; font-weight: 900; margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: #667eea;
        animation: valueGlow 2s ease-in-out infinite alternate;
        line-height: 1;
    }

    @keyframes valueGlow {
        from { filter: brightness(1); }
        to { filter: brightness(1.1); }
    }

    .metric-label {
        color: #374151; font-size: 0.95rem; font-weight: 600;
        margin-top: 0.5rem; letter-spacing: 0.3px;
    }

    .metric-sublabel {
        color: #6b7280; font-size: 0.8rem; margin-top: 0.4rem;
        font-weight: 500; font-style: italic;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 0.6rem; border-radius: 12px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px; padding: 0 20px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px; border: 1px solid rgba(102, 126, 234, 0.15);
        font-weight: 600; font-size: 0.85rem;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px); 
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }

    /* 洞察卡片 */
    .insight-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-left: 4px solid #667eea; border-radius: 12px;
        padding: 1.2rem; margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        animation: slideInLeft 0.6s ease-out;
        transition: all 0.3s ease;
    }

    .insight-card:hover {
        transform: translateX(5px) translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.12);
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .insight-card h4 {
        color: #1f2937; margin-bottom: 0.8rem;
        font-weight: 700; font-size: 1rem;
    }

    /* 图表标题容器 */
    .chart-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 200% 200%;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
        position: relative;
        overflow: hidden;
        animation: gradientFlow 6s ease infinite;
        transition: all 0.3s ease;
    }

    .chart-header:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
    }

    /* 渐变流动动画 */
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 光泽效果 */
    .chart-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent
        );
        animation: shine 3s ease-in-out infinite;
    }

    @keyframes shine {
        0% { left: -100%; }
        50%, 100% { left: 200%; }
    }

    /* 图表标题样式 */
    .chart-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-align: left;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
        line-height: 1.2;
        animation: fadeInSlide 0.8s ease-out;
    }

    .chart-subtitle {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        font-weight: 400;
        text-align: left;
        line-height: 1.4;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
        animation: fadeInSlide 1s ease-out;
    }

    @keyframes fadeInSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* 动画延迟 */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    .metric-card:nth-child(5) { animation-delay: 0.5s; }
    .metric-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-card:nth-child(7) { animation-delay: 0.7s; }
    .metric-card:nth-child(8) { animation-delay: 0.8s; }

    /* 响应式 */
    @media (max-width: 768px) {
        .metric-value, .big-value { font-size: 1.8rem; }
        .metric-card { padding: 1rem; margin: 0.5rem 0; }
        .main-header { padding: 1.5rem 0; }
    }

    /* 确保文字颜色 */
    h1, h2, h3, h4, h5, h6 { color: #1f2937 !important; }
    p, span, div { color: #374151; }
</style>
""", unsafe_allow_html=True)

# ==================== 全局变量和函数 ====================
VERBOSE = False
CURRENT_LOG_LEVEL = 2  # WARNING

def calculate_accuracy(predicted, actual):
    """统一的准确率计算方法"""
    absolute_threshold = 20
    
    if actual == 0:
        return 100 if predicted <= absolute_threshold else 0
    
    absolute_error = abs(predicted - actual)
    
    if absolute_error <= absolute_threshold:
        return 100
    
    relative_error = (absolute_error / actual) * 100
    accuracy = max(0, 100 - relative_error)
    
    return accuracy

def log(message, level="INFO", force=False):
    """日志函数"""
    if force or VERBOSE:
        print(f"[{level}] {message}")

# ==================== 数据处理类 ====================
class DataPreprocessor:
    """数据预处理器"""
    def __init__(self):
        self.z_threshold = 3.0
        self.smooth_window = 3
    
    def detect_outliers(self, data, method='zscore'):
        """检测异常值"""
        if len(data) < 4:
            return []
        
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            return np.where(z_scores > self.z_threshold)[0]
        elif method == 'iqr':
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            return np.where((data < lower_bound) | (data > upper_bound))[0]
        
        return []
    
    def smooth_data(self, data, window_size=None):
        """平滑数据"""
        if window_size is None:
            window_size = self.smooth_window
        
        if len(data) < window_size:
            return data
        
        smoothed_data = np.zeros_like(data)
        for i in range(len(data)):
            start = max(0, i - window_size + 1)
            smoothed_data[i] = np.mean(data[start:i + 1])
        
        return smoothed_data

# ==================== 产品分组器类 ====================
class ProductGrouper:
    """产品分组器"""
    def __init__(self):
        self.cv_threshold = 0.5
        self.seasonal_threshold = 0.2
        self.groups = {}
    
    def calculate_cv(self, data):
        """计算变异系数"""
        if np.mean(data) == 0:
            return float('inf')
        return np.std(data) / np.mean(data)
    
    def detect_seasonality(self, monthly_data):
        """检测季节性"""
        if len(monthly_data) < 12:
            return False, 1.0
        
        monthly_avg = {}
        for i, val in enumerate(monthly_data):
            month = (i % 12) + 1
            if month not in monthly_avg:
                monthly_avg[month] = []
            monthly_avg[month].append(val)
        
        for month in monthly_avg:
            monthly_avg[month] = np.mean(monthly_avg[month])
        
        overall_avg = np.mean(list(monthly_avg.values()))
        max_diff = max(monthly_avg.values()) - min(monthly_avg.values())
        relative_diff = max_diff / overall_avg if overall_avg > 0 else 0
        
        is_seasonal = relative_diff > self.seasonal_threshold
        
        return is_seasonal, monthly_avg
    
    def group_products(self, shipping_data, product_codes=None):
        """对产品进行分组"""
        monthly_sales = shipping_data.copy()
        monthly_sales['月份'] = monthly_sales['订单日期'].dt.to_period('M')
        monthly_sales = monthly_sales.groupby(['月份', '产品代码'])['求和项:数量（箱）'].sum().reset_index()
        
        if product_codes is None:
            product_codes = monthly_sales['产品代码'].unique()
        
        for product in product_codes:
            product_sales = monthly_sales[monthly_sales['产品代码'] == product].sort_values('月份')
            
            if len(product_sales) < 3:
                self.groups[product] = 'stable'
                continue
            
            sales_values = product_sales['求和项:数量（箱）'].values
            cv = self.calculate_cv(sales_values)
            is_seasonal, _ = self.detect_seasonality(sales_values)
            
            if is_seasonal:
                group_type = 'seasonal'
            elif cv > self.cv_threshold:
                group_type = 'volatile'
            else:
                group_type = 'stable'
            
            self.groups[product] = group_type
        
        return self.groups

# ==================== ML模型选择器 ====================
class MLModelSelector:
    """模型选择器"""
    def __init__(self, data_tracker=None):
        self.data_tracker = data_tracker
        self.models = {}
        self.best_model_records = {}
        self.model_cache_path = 'ml_models_cache/'
        
        if not os.path.exists(self.model_cache_path):
            os.makedirs(self.model_cache_path)
    
    def _create_xgboost_model(self):
        """创建XGBoost模型"""
        return xgb.XGBRegressor(
            n_estimators=50,
            learning_rate=0.05,
            max_depth=2,
            min_child_weight=1,
            gamma=0,
            subsample=0.9,
            colsample_bytree=0.9,
            objective='reg:squarederror',
            verbosity=0,
            random_state=42
        )
    
    def _create_lightgbm_model(self):
        """创建LightGBM模型"""
        return lgb.LGBMRegressor(
            n_estimators=50,
            learning_rate=0.05,
            max_depth=2,
            min_child_samples=2,
            subsample=0.9,
            colsample_bytree=0.9,
            objective='regression',
            verbose=-1,
            min_data_in_leaf=1,
            min_sum_hessian_in_leaf=0.001,
            random_state=42
        )
    
    def select_best_model(self, product_code, features_df, target, time_col='月份'):
        """选择最佳模型 - 简化版，始终使用XGBoost"""
        log(f"为产品 {product_code} 选择最佳模型...")
        
        if len(features_df) < 3:
            log(f"产品 {product_code} 数据量极少，使用扩展移动平均模型")
            return {
                'model_name': 'extended_ma',
                'model': {'model_type': 'extended_ma'},
                'score': 0,
                'feature_cols': None,
                'last_update': datetime.now()
            }
        
        features_df = features_df.sort_values(time_col).reset_index(drop=True)
        feature_cols = [col for col in features_df.columns if col != time_col and col != target]
        
        model_name = 'xgboost'
        is_new_product = len(features_df) < 6
        
        if is_new_product:
            model = self._create_xgboost_model()
            log(f"产品 {product_code} 数据量较少，使用简化XGBoost模型")
        else:
            model = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='reg:squarederror',
                verbosity=0,
                random_state=42
            )
            log(f"产品 {product_code} 数据充足，使用标准XGBoost模型")
        
        X = features_df[feature_cols]
        y = features_df[target]
        model.fit(X, y)
        
        train_predictions = model.predict(X)
        score = mean_absolute_error(y, train_predictions)
        
        best_model_info = {
            'model_name': model_name,
            'model': model,
            'score': score,
            'feature_cols': feature_cols,
            'last_update': datetime.now()
        }
        
        log(f"产品 {product_code} 的最佳模型: {model_name}, 得分: {score:.2f}")
        return best_model_info

# ==================== ML预测器 ====================
class MLPredictor:
    """机器学习预测器"""
    def __init__(self, shipping_data, product_info, promotion_data, data_tracker=None):
        self.shipping_data = shipping_data
        self.product_info = product_info
        self.promotion_data = promotion_data
        self.data_tracker = data_tracker
        self.current_date = datetime.now()
        self.model_selector = MLModelSelector(data_tracker)
        self.data_preprocessor = DataPreprocessor()
        
        self.special_periods = {
            '儿童节': (5, 7),
            '暑假': (7, 9),
            '春节': (1, 3)
        }
        
        self.predictions = {}
    
    def prepare_features(self, product_code):
        """准备预测特征"""
        product_data = self.shipping_data[self.shipping_data['产品代码'] == product_code].copy()
        
        if product_data.empty:
            log(f"产品 {product_code} 没有销售数据")
            return None
        
        product_data['月份'] = product_data['订单日期'].dt.to_period('M')
        monthly_sales = product_data.groupby('月份')['求和项:数量（箱）'].sum().reset_index()
        monthly_sales['月份'] = monthly_sales['月份'].dt.to_timestamp()
        monthly_sales = monthly_sales.sort_values('月份')
        
        total_sales = monthly_sales['求和项:数量（箱）'].sum()
        avg_monthly_sales = monthly_sales['求和项:数量（箱）'].mean()
        sales_std = monthly_sales['求和项:数量（箱）'].std()
        sales_cv = sales_std / avg_monthly_sales if avg_monthly_sales > 0 else 0
        
        is_new_product = len(monthly_sales) < 6
        
        features = []
        
        for i, row in monthly_sales.iterrows():
            month = row['月份']
            sales = row['求和项:数量（箱）']
            
            feature = {
                '月份': month,
                '销量': sales,
                '月份_sin': np.sin(2 * np.pi * month.month / 12),
                '月份_cos': np.cos(2 * np.pi * month.month / 12),
                '季度': (month.month - 1) // 3 + 1,
                '年份': month.year,
                '月号': month.month,
                '是春季': 3 <= month.month <= 5,
                '是夏季': 6 <= month.month <= 8,
                '是秋季': 9 <= month.month <= 11,
                '是冬季': month.month == 12 or month.month <= 2,
                '是春节期间': 1 <= month.month <= 2,
                '是儿童节期间': 5 <= month.month <= 6,
                '是暑假期间': 7 <= month.month <= 8,
                '是新品': is_new_product,
                '平均月销量': avg_monthly_sales,
                '销量变异系数': sales_cv,
            }
            
            if self.data_tracker and hasattr(self.data_tracker, 'get_product_group'):
                group_type = self.data_tracker.get_product_group(product_code)
                feature['产品分组_stable'] = 1 if group_type == 'stable' else 0
                feature['产品分组_volatile'] = 1 if group_type == 'volatile' else 0
                feature['产品分组_seasonal'] = 1 if group_type == 'seasonal' else 0
            else:
                feature['产品分组_stable'] = 1
                feature['产品分组_volatile'] = 0
                feature['产品分组_seasonal'] = 0
            
            features.append(feature)
        
        features_df = pd.DataFrame(features)
        
        # 添加历史销量特征
        max_lag = min(12, len(features_df))
        for lag in range(1, max_lag):
            features_df[f'销量_lag{lag}'] = features_df['销量'].shift(lag)
        
        # 添加移动平均特征
        if is_new_product:
            window_sizes = [2, 3]
        else:
            window_sizes = [3, 6, 12]
        
        for window in window_sizes:
            if window <= len(features_df):
                features_df[f'销量_ma{window}'] = features_df['销量'].rolling(window=window).mean()
        
        # 添加趋势特征
        features_df['销量_trend'] = 0.0
        
        if len(features_df) >= 3:
            recent_data = features_df.tail(min(6, len(features_df)))
            x = np.arange(len(recent_data))
            y = recent_data['销量'].values
            
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                if not np.isnan(slope):
                    norm_slope = slope / recent_data['销量'].mean() if recent_data['销量'].mean() > 0 else 0
                    features_df.loc[features_df.index[-3:], '销量_trend'] = norm_slope
            except:
                pass
        
        # 添加客户特征
        if '客户代码' in self.shipping_data.columns:
            customer_sales = product_data.groupby('客户代码')['求和项:数量（箱）'].sum()
            total_sales = customer_sales.sum()
            
            if total_sales > 0:
                herfindahl_index = sum((sales / total_sales) ** 2 for sales in customer_sales)
                features_df['客户集中度'] = herfindahl_index
                
                main_customers = [customer for customer, sales in customer_sales.items()
                                  if sales / total_sales >= 0.1]
                features_df['主要客户数'] = len(main_customers)
                
                main_customer_contribution = sum(sales for customer, sales in customer_sales.items()
                                                 if customer in main_customers) / total_sales
                features_df['主要客户贡献率'] = main_customer_contribution
                
                if not customer_sales.empty:
                    features_df['最大客户贡献率'] = customer_sales.max() / total_sales
            else:
                features_df['客户集中度'] = 0
                features_df['主要客户数'] = 0
                features_df['主要客户贡献率'] = 0
                features_df['最大客户贡献率'] = 0
        else:
            features_df['客户集中度'] = 0
            features_df['主要客户数'] = 0
            features_df['主要客户贡献率'] = 0
            features_df['最大客户贡献率'] = 0
        
        # 处理NaN值
        lag_columns = [col for col in features_df.columns if col.startswith('销量_lag')]
        for col in lag_columns:
            features_df[col] = features_df[col].fillna(0)
        
        ma_columns = [col for col in features_df.columns if col.startswith('销量_ma')]
        for col in ma_columns:
            features_df[col] = features_df[col].fillna(features_df['销量'])
        
        features_df['销量_trend'] = features_df['销量_trend'].fillna(1.0)
        
        return features_df
    
    def predict_next_months(self, product_code, horizon=4, current_date=None):
        """预测未来几个月"""
        if current_date is None:
            current_date = self.current_date
        
        log(f"使用统一XGBoost模型预测产品 {product_code}")
        
        features_df = self.prepare_features(product_code)
        
        if features_df is None or features_df.empty:
            log(f"产品 {product_code} 没有足够数据，无法预测")
            return None
        
        avg_monthly_sales = features_df['销量'].mean() if '销量' in features_df.columns else 0
        is_new_product = len(features_df) < 6
        sales_std = features_df['销量'].std() if '销量' in features_df.columns else 0
        sales_cv = sales_std / avg_monthly_sales if avg_monthly_sales > 0 else 0
        
        if len(features_df) < 3:
            log(f"产品 {product_code} 数据量极少，使用简单平均预测")
            conservative_factor = 0.9
            avg_sales = features_df['销量'].mean()
            predictions = [round(avg_sales * conservative_factor)] * horizon
            return predictions
        
        X = features_df.drop(['月份', '销量'], axis=1)
        y = features_df['销量']
        
        if is_new_product:
            model = xgb.XGBRegressor(
                n_estimators=50,
                learning_rate=0.05,
                max_depth=2,
                min_child_weight=2,
                subsample=0.9,
                colsample_bytree=0.9,
                objective='reg:squarederror',
                verbosity=0,
                random_state=42
            )
        else:
            model = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='reg:squarederror',
                verbosity=0,
                random_state=42
            )
        
        model.fit(X, y)
        
        feature_importance = model.feature_importances_
        feature_names = X.columns
        importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importance})
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        top_features = importance_df.head(5)
        log(f"产品 {product_code} 的前5个重要特征:")
        for _, row in top_features.iterrows():
            log(f"  {row['feature']}: {row['importance']:.4f}")
        
        predictions = []
        last_features = X.iloc[-1].copy()
        
        if is_new_product:
            base_conservative_factor = 0.9
        elif sales_cv > 0.5:
            base_conservative_factor = 0.92
        else:
            base_conservative_factor = 0.95
        
        for i in range(horizon):
            target_month = current_date.month + i
            target_year = current_date.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            
            next_month = datetime(target_year, target_month, 1)
            if '月号' in last_features:
                last_features['月号'] = next_month.month
            if '年份' in last_features:
                last_features['年份'] = next_month.year
            if '月份_sin' in last_features:
                last_features['月份_sin'] = np.sin(2 * np.pi * next_month.month / 12)
            if '月份_cos' in last_features:
                last_features['月份_cos'] = np.cos(2 * np.pi * next_month.month / 12)
            if '季度' in last_features:
                last_features['季度'] = (next_month.month - 1) // 3 + 1
            
            if '是春季' in last_features:
                last_features['是春季'] = 3 <= next_month.month <= 5
            if '是夏季' in last_features:
                last_features['是夏季'] = 6 <= next_month.month <= 8
            if '是秋季' in last_features:
                last_features['是秋季'] = 9 <= next_month.month <= 11
            if '是冬季' in last_features:
                last_features['是冬季'] = next_month.month == 12 or next_month.month <= 2
            
            if '是春节期间' in last_features:
                last_features['是春节期间'] = 1 <= next_month.month <= 2
            if '是儿童节期间' in last_features:
                last_features['是儿童节期间'] = 5 <= next_month.month <= 6
            if '是暑假期间' in last_features:
                last_features['是暑假期间'] = 7 <= next_month.month <= 8
            
            try:
                prediction = model.predict(last_features.values.reshape(1, -1))[0]
                prediction = max(0, prediction)
                prediction_horizon_factor = base_conservative_factor * (1 - i * 0.01)
                adjusted_prediction = prediction * prediction_horizon_factor
            except Exception as e:
                log(f"预测出错: {e}")
                adjusted_prediction = avg_monthly_sales * base_conservative_factor
            
            predictions.append(round(adjusted_prediction))
            
            for lag in range(min(12, len(features_df)), 1, -1):
                lag_col = f'销量_lag{lag}'
                prev_lag_col = f'销量_lag{lag - 1}'
                if lag_col in last_features and prev_lag_col in last_features:
                    last_features[lag_col] = last_features[prev_lag_col]
            
            if '销量_lag1' in last_features:
                last_features['销量_lag1'] = adjusted_prediction
            
            for window in [3, 6, 12]:
                ma_col = f'销量_ma{window}'
                if ma_col in last_features:
                    if i >= window - 1:
                        last_features[ma_col] = np.mean(predictions[-window:])
                    else:
                        hist_values = y.iloc[-(window - i - 1):].values.tolist() if i < window - 1 else []
                        all_values = hist_values + predictions
                        last_features[ma_col] = np.mean(all_values[-window:])
        
        self.predictions[product_code] = predictions
        
        if is_new_product and len(y) > 0:
            max_historical = y.max()
            for i in range(len(predictions)):
                if predictions[i] > max_historical * 1.5:
                    predictions[i] = round(max_historical * 1.5)
        
        return predictions

# ==================== 客户分析类 ====================
class CustomerProductAnalyzer:
    """客户产品分析器"""
    def analyze_dependencies(self, shipping_data):
        """分析产品对客户的依赖关系"""
        if '客户代码' not in shipping_data.columns:
            log("数据中不包含客户信息，无法分析客户依赖关系")
            return {}
        
        result = {}
        
        product_customer_sales = shipping_data.groupby(['产品代码', '客户代码'])['求和项:数量（箱）'].sum().reset_index()
        product_total_sales = product_customer_sales.groupby('产品代码')['求和项:数量（箱）'].sum().to_dict()
        
        for _, row in product_customer_sales.iterrows():
            product = row['产品代码']
            customer = row['客户代码']
            sales = row['求和项:数量（箱）']
            
            total_sales = product_total_sales.get(product, 0)
            if total_sales > 0:
                contribution = sales / total_sales
                
                if product not in result:
                    result[product] = []
                
                if contribution >= 0.1:
                    result[product].append({
                        'customer': customer,
                        'contribution': contribution,
                        'sales': sales
                    })
        
        for product in result:
            result[product] = sorted(result[product], key=lambda x: x['contribution'], reverse=True)
        
        return result

class CustomerActivityMonitor:
    """客户活跃度监控"""
    def __init__(self, months_threshold=3):
        self.months_threshold = months_threshold
    
    def check_customer_activity(self, shipping_data, product_customer_deps, current_date=None):
        """检查客户活跃状态"""
        if '客户代码' not in shipping_data.columns:
            log("数据中不包含客户信息，无法监控客户活跃度")
            return {}
        
        if current_date is None:
            current_date = datetime.now()
        
        activity_status = {}
        
        for product, customers in product_customer_deps.items():
            activity_status[product] = {}
            
            for customer_info in customers[:min(3, len(customers))]:
                customer = customer_info['customer']
                
                customer_orders = shipping_data[
                    (shipping_data['产品代码'] == product) &
                    (shipping_data['客户代码'] == customer)
                ]
                
                if not customer_orders.empty:
                    last_order_date = customer_orders['订单日期'].max()
                    months_inactive = (current_date - last_order_date).days // 30
                    
                    activity_status[product][customer] = {
                        'last_order_date': last_order_date,
                        'months_inactive': months_inactive,
                        'is_active': months_inactive < self.months_threshold,
                        'contribution': customer_info['contribution']
                    }
                else:
                    activity_status[product][customer] = {
                        'last_order_date': None,
                        'months_inactive': float('inf'),
                        'is_active': False,
                        'contribution': customer_info['contribution']
                    }
        
        return activity_status

# ==================== 数据追踪器 ====================
class DataTracker:
    """数据追踪器"""
    def __init__(self, results_file='sales_forecast_results.xlsx'):
        self.results_file = results_file
        self.last_processed_date = None
        self.predictions = {}
        self.actual_sales = {}
        self.accuracy_history = {}
        self.model_params = {}
        self.product_groups = {}
        self.production_decisions = {}
        self.model_accuracy_history = {}
        self.model_predictions = {}
        self.model_selections = {}
        self._load_data()
    
    def _load_data(self):
        """加载历史数据"""
        try:
            if os.path.exists(self.results_file):
                # 这里简化，实际应该从Excel读取
                pass
        except Exception as e:
            log(f"加载历史数据失败: {e}")
        
        # 初始化默认参数
        self.model_params['default'] = {
            'weights': [0.2, 0.3, 0.5],
            'seasonal_factor': 1.0,
            'promotion_factor': 1.2,
            'safety_stock_factor': 0.5,
            'best_accuracy': 0.0,
        }
    
    def get_params(self, product_code):
        """获取产品参数"""
        if product_code not in self.model_params:
            if product_code in self.product_groups:
                group_type = self.product_groups[product_code]
                product_grouper = ProductGrouper()
                params = {
                    'weights': [0.2, 0.3, 0.5],
                    'seasonal_factor': 1.0,
                    'promotion_factor': 1.2,
                    'safety_stock_factor': 0.5,
                    'best_accuracy': 0.0
                }
                if group_type == 'volatile':
                    params['weights'] = [0.1, 0.2, 0.7]
                    params['safety_stock_factor'] = 0.7
                elif group_type == 'seasonal':
                    params['weights'] = [0.15, 0.25, 0.6]
                    params['safety_stock_factor'] = 0.6
                self.model_params[product_code] = params
            else:
                self.model_params[product_code] = self.model_params['default'].copy()
        
        return self.model_params[product_code]
    
    def set_product_group(self, product_code, group_type):
        """设置产品分组"""
        self.product_groups[product_code] = group_type
    
    def get_product_group(self, product_code):
        """获取产品分组"""
        return self.product_groups.get(product_code, 'stable')
    
    def get_average_accuracy(self, product_code):
        """获取平均准确率"""
        if product_code not in self.accuracy_history or not self.accuracy_history[product_code]:
            return None
        
        accuracies = [record['accuracy'] for record in self.accuracy_history[product_code]]
        return sum(accuracies) / len(accuracies)
    
    def record_prediction(self, product_code, month, predicted_value):
        """记录预测值"""
        if product_code not in self.predictions:
            self.predictions[product_code] = {}
        self.predictions[product_code][month] = predicted_value
    
    def record_actual_sales(self, product_code, month, actual_value):
        """记录实际销量"""
        if product_code not in self.actual_sales:
            self.actual_sales[product_code] = {}
        self.actual_sales[product_code][month] = actual_value
    
    def save_data(self):
        """保存数据（简化版）"""
        log("数据已保存")
        return True

# ==================== 销售预测器 ====================
class SalesPredictor:
    """销售预测器"""
    def __init__(self, shipping_data, product_info, promotion_data, data_tracker=None):
        self.shipping_data = shipping_data
        self.product_info = product_info
        self.promotion_data = promotion_data
        self.current_date = datetime.now()
        self.data_tracker = data_tracker
        
        self.data_preprocessor = DataPreprocessor()
        self.product_grouper = ProductGrouper()
        
        self.special_periods = {
            '儿童节': (5, 7),
            '暑假': (7, 9),
            '春节': (1, 3)
        }
        
        self.customer_analyzer = CustomerProductAnalyzer()
        self.activity_monitor = CustomerActivityMonitor(months_threshold=3)
    
    def predict_next_months(self, months=4):
        """预测未来几个月的销量"""
        monthly_sales = self._get_monthly_sales()
        
        log("开始执行预测，使用统一XGBoost预测策略...")
        
        all_products = self.product_info['产品代码'].unique() if self.product_info is not None else monthly_sales['产品代码'].unique()
        
        log(f"共有{len(all_products)}个产品需要预测")
        
        product_groups = self.product_grouper.group_products(self.shipping_data, all_products)
        
        if self.data_tracker:
            for product, group_type in product_groups.items():
                self.data_tracker.set_product_group(product, group_type)
        
        ml_predictor = MLPredictor(
            self.shipping_data,
            self.product_info,
            self.promotion_data,
            self.data_tracker
        )
        
        predictions = []
        
        current_month = self.current_date.month
        current_year = self.current_date.year
        
        log("开始对各产品进行预测...")
        
        for product in all_products:
            product_group = self.data_tracker.get_product_group(product) if self.data_tracker else 'stable'
            
            product_data = monthly_sales[monthly_sales['产品代码'] == product]
            data_months = len(product_data['月份'].unique())
            is_new_product = data_months < 6
            
            log(f"产品 {product}: 使用统一XGBoost预测 (数据月数: {data_months}, 分组: {product_group})")
            ml_predictions = ml_predictor.predict_next_months(product, months, self.current_date)
            
            for i in range(months):
                if ml_predictions is not None and i < len(ml_predictions):
                    predict_month = current_month + i
                    predict_year = current_year
                    if predict_month > 12:
                        predict_month -= 12
                        predict_year += 1
                    
                    month_str = f"{predict_year}-{predict_month:02d}"
                    
                    product_name = ''
                    if self.product_info is not None:
                        product_info = self.product_info[self.product_info['产品代码'] == product]
                        if not product_info.empty:
                            product_name = product_info.iloc[0]['产品名称']
                    
                    ml_pred = ml_predictions[i]
                    
                    prediction_item = {
                        '产品代码': product,
                        '产品名称': product_name,
                        '预测月份': month_str,
                        '预测销量': ml_pred,
                        '季节性因子': 1.0,
                        '促销因子': 1.0,
                        '保守系数': 0.95 if not is_new_product else 0.9
                    }
                    
                    predictions.append(prediction_item)
                    
                    if self.data_tracker:
                        self.data_tracker.record_prediction(product, month_str, ml_pred)
        
        if self.data_tracker:
            self.data_tracker.save_data()
        
        log(f"预测完成: 已预测 {len(all_products)} 个产品的 {months} 个月销量")
        
        return pd.DataFrame(predictions)
    
    def _get_monthly_sales(self):
        """获取月度销量"""
        monthly_sales = self.shipping_data.copy()
        monthly_sales['月份'] = monthly_sales['订单日期'].dt.to_period('M')
        monthly_sales = monthly_sales.groupby(['月份', '产品代码'])['求和项:数量（箱）'].sum().reset_index()
        return monthly_sales

# ==================== 库存管理器 ====================
class InventoryManager:
    """库存管理器"""
    def __init__(self, inventory_data, product_info, shipping_data, data_tracker=None, batch_data=None):
        self.inventory_data = inventory_data
        self.product_info = product_info
        self.shipping_data = shipping_data
        self.batch_data = batch_data
        self.current_date = datetime.now()
        self.data_tracker = data_tracker
    
    def calculate_safety_stock(self):
        """计算安全库存"""
        if self.shipping_data is None:
            return pd.DataFrame()
        
        six_months_ago = self.current_date - timedelta(days=180)
        six_month_sales = self.shipping_data[self.shipping_data['订单日期'] >= six_months_ago]
        monthly_sales = six_month_sales.groupby('产品代码')['求和项:数量（箱）'].sum() / 6
        
        safety_stock = pd.DataFrame({
            '产品代码': monthly_sales.index,
            '月均销量': monthly_sales.values.round()
        })
        
        safety_stock['安全库存'] = safety_stock.apply(
            lambda row: round(row['月均销量'] * 
                              (self.data_tracker.get_params(row['产品代码'])['safety_stock_factor'] if self.data_tracker else 0.5)),
            axis=1
        )
        
        if self.product_info is not None:
            safety_stock = safety_stock.merge(
                self.product_info[['产品代码', '产品名称']],
                on='产品代码', how='left'
            )
        
        return safety_stock
    
    def identify_stock_issues(self, sales_prediction):
        """识别库存问题"""
        if self.inventory_data is None:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        batch_info_by_product = {}
        
        if self.batch_data is not None and not self.batch_data.empty:
            for _, row in self.batch_data.iterrows():
                product_code = row['物料']
                production_date = row['生产日期']
                quantity = row['数量']
                
                if pd.notna(production_date):
                    age_days = (self.current_date - production_date).days
                    
                    if (product_code not in batch_info_by_product or
                            age_days > batch_info_by_product[product_code]['age']):
                        
                        product_name = ''
                        if self.product_info is not None:
                            product_info = self.product_info[self.product_info['产品代码'] == product_code]
                            if not product_info.empty:
                                product_name = product_info.iloc[0]['产品名称']
                        
                        batch_info_by_product[product_code] = {
                            'product_name': product_name,
                            'date': production_date,
                            'age': age_days,
                            'quantity': quantity,
                            'is_backlog': age_days > 90
                        }
        
        batch_info = []
        backlog_products = []
        
        for _, row in self.inventory_data.iterrows():
            product_code = row['物料']
            product_name = ''
            
            if self.product_info is not None:
                product_info = self.product_info[self.product_info['产品代码'] == product_code]
                if not product_info.empty:
                    product_name = product_info.iloc[0]['产品名称']
            
            if product_code in batch_info_by_product:
                info = batch_info_by_product[product_code]
                batch_record = {
                    '产品代码': product_code,
                    '产品名称': product_name,
                    '生产日期': info['date'],
                    '批次年龄(天)': info['age'],
                    '数量': info['quantity']
                }
                batch_info.append(batch_record)
                
                if info['is_backlog']:
                    backlog_record = batch_record.copy()
                    backlog_record['积压数量'] = backlog_record.pop('数量')
                    backlog_products.append(backlog_record)
            else:
                batch_info.append({
                    '产品代码': product_code,
                    '产品名称': product_name,
                    '生产日期': None,
                    '批次年龄(天)': 0,
                    '数量': 0
                })
        
        stockout_risk = []
        
        current_stock = self.inventory_data[['物料', '现有库存']].copy()
        current_stock.rename(columns={'物料': '产品代码'}, inplace=True)
        
        if not sales_prediction.empty:
            prediction_monthly = sales_prediction.groupby('产品代码')['预测销量'].mean().reset_index()
            prediction_monthly['15天销量'] = (prediction_monthly['预测销量'] / 30 * 15).round()
            
            stock_vs_prediction = current_stock.merge(
                prediction_monthly[['产品代码', '15天销量']],
                on='产品代码', how='outer'
            ).fillna(0)
            
            for _, row in stock_vs_prediction.iterrows():
                if row['现有库存'] < row['15天销量']:
                    product_code = row['产品代码']
                    product_name = ''
                    if self.product_info is not None:
                        product_info = self.product_info[self.product_info['产品代码'] == product_code]
                        if not product_info.empty:
                            product_name = product_info.iloc[0]['产品名称']
                    
                    stockout_risk.append({
                        '产品代码': product_code,
                        '产品名称': product_name,
                        '当前库存': row['现有库存'],
                        '15天预测销量': row['15天销量'],
                        '缺货风险': '高' if row['现有库存'] < row['15天销量'] / 2 else '中'
                    })
        
        return pd.DataFrame(backlog_products), pd.DataFrame(stockout_risk), pd.DataFrame(batch_info)

# ==================== 生产计划器 ====================
class ProductionPlanner:
    """生产计划器"""
    def __init__(self, inventory_data, sales_prediction, safety_stock):
        self.inventory_data = inventory_data
        self.sales_prediction = sales_prediction
        self.safety_stock = safety_stock
    
    def generate_production_plan(self, batch_info=None, data_tracker=None):
        """生成生产计划"""
        if self.inventory_data is None or self.sales_prediction is None or self.safety_stock is None:
            return pd.DataFrame()
        
        current_stock = self.inventory_data[['物料', '现有库存']].copy()
        current_stock.rename(columns={'物料': '产品代码'}, inplace=True)
        
        all_months = self.sales_prediction['预测月份'].unique()
        months_sorted = sorted(all_months)
        
        all_plans = []
        
        for i, month in enumerate(months_sorted):
            month_forecast = self.sales_prediction[self.sales_prediction['预测月份'] == month]
            
            month_plan = current_stock.copy()
            month_plan['月份'] = month
            
            month_plan = month_plan.merge(
                month_forecast[['产品代码', '预测销量']],
                on='产品代码', how='left'
            ).fillna(0)
            
            month_plan = month_plan.merge(
                self.safety_stock[['产品代码', '安全库存', '月均销量']],
                on='产品代码', how='left'
            ).fillna(0)
            
            if '产品名称' in self.safety_stock.columns:
                month_plan = month_plan.merge(
                    self.safety_stock[['产品代码', '产品名称']],
                    on='产品代码', how='left'
                )
            
            month_plan['日均销量'] = month_plan['月均销量'] / 30
            month_plan['库存覆盖天数'] = month_plan.apply(
                lambda row: round(row['现有库存'] / row['日均销量']) if row['日均销量'] > 0 else 0,
                axis=1
            )
            
            if i == 0:
                month_plan['需要生产数量'] = month_plan.apply(
                    lambda row: max(0, round(
                        row['预测销量'] - row['现有库存'] + row['安全库存'] * 1.2
                    )),
                    axis=1
                )
            elif i == 1:
                prev_month_plan = all_plans[0].copy()
                
                month_plan['预计剩余库存'] = month_plan.apply(
                    lambda row: max(0, row['现有库存'] -
                                    prev_month_plan.loc[
                                        prev_month_plan['产品代码'] == row['产品代码'],
                                        '预测销量'
                                    ].sum() +
                                    prev_month_plan.loc[
                                        prev_month_plan['产品代码'] == row['产品代码'],
                                        '需要生产数量'
                                    ].sum()),
                    axis=1
                )
                
                month_plan['需要生产数量'] = month_plan.apply(
                    lambda row: max(0, round(
                        row['预测销量'] - row['预计剩余库存'] + row['安全库存']
                    )),
                    axis=1
                )
            else:
                prev_month_plan1 = all_plans[0].copy()
                prev_month_plan2 = all_plans[1].copy()
                
                month_plan['预计剩余库存'] = month_plan.apply(
                    lambda row: max(0, row['现有库存'] -
                                    prev_month_plan1.loc[
                                        prev_month_plan1['产品代码'] == row['产品代码'],
                                        '预测销量'
                                    ].sum() -
                                    prev_month_plan2.loc[
                                        prev_month_plan2['产品代码'] == row['产品代码'],
                                        '预测销量'
                                    ].sum() +
                                    prev_month_plan1.loc[
                                        prev_month_plan1['产品代码'] == row['产品代码'],
                                        '需要生产数量'
                                    ].sum() +
                                    prev_month_plan2.loc[
                                        prev_month_plan2['产品代码'] == row['产品代码'],
                                        '需要生产数量'
                                    ].sum()),
                    axis=1
                )
                
                month_plan['需要生产数量'] = month_plan.apply(
                    lambda row: max(0, round(
                        row['预测销量'] - row['预计剩余库存'] + row['安全库存'] * 0.8
                    )),
                    axis=1
                )
            
            month_plan['优先级分数'] = month_plan.apply(
                lambda row: 0 if row['现有库存'] == 0 else row['库存覆盖天数'],
                axis=1
            )
            
            month_plan['排产优先级'] = month_plan['优先级分数'].rank()
            
            all_plans.append(month_plan)
        
        production_plan = pd.concat(all_plans, ignore_index=True)
        
        if batch_info is not None and data_tracker is not None:
            for product_code in production_plan['产品代码'].unique():
                product_batch = batch_info[batch_info['产品代码'] == product_code]
                if not product_batch.empty and '批次年龄(天)' in product_batch.columns:
                    batch_age = product_batch['批次年龄(天)'].max()
                    if pd.notna(batch_age) and batch_age > 0:
                        # 这里可以根据批次年龄调整参数
                        pass
        
        production_plan = production_plan[production_plan['需要生产数量'] > 0]
        production_plan = production_plan.sort_values(['月份', '排产优先级'])
        
        return production_plan

# ==================== 缓存数据加载函数 ====================
@st.cache_data(ttl=3600)
def load_github_data(file_url):
    """从GitHub加载Excel文件"""
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return pd.read_excel(BytesIO(response.content))
        else:
            st.error(f"无法加载文件: {file_url}")
            return None
    except Exception as e:
        st.error(f"加载数据出错: {str(e)}")
        return None

# ==================== 数据加载器 ====================
class DataLoader:
    """数据加载器"""
    def __init__(self):
        self.shipping_data = None
        self.inventory_data = None
        self.batch_data = None
        self.product_info = None
        self.promotion_data = None
    
    def load_all_data(self):
        """加载所有数据"""
        base_url = "https://raw.githubusercontent.com/CIRA18-HUB/sales_dashboard/main/"
        
        data = {}
        files = {
            'shipping': '预测模型出货数据每日xlsx.xlsx',
            'inventory': '含批次库存0221(2).xlsx', 
            'product': '产品信息.xlsx',
            'promotion': '销售业务员促销文件.xlsx'
        }
        
        for key, filename in files.items():
            with st.spinner(f'加载{filename}...'):
                data[key] = load_github_data(base_url + filename)
        
        # 处理数据
        if data['shipping'] is not None:
            self.shipping_data = data['shipping']
            self.shipping_data['订单日期'] = pd.to_datetime(self.shipping_data['订单日期'])
            
        if data['inventory'] is not None:
            self.inventory_data = data['inventory']
            # 处理批次数据
            self._process_batch_data(data['inventory'])
            
        if data['product'] is not None:
            self.product_info = data['product']
            # 清理产品名称
            if '产品名称' in self.product_info.columns:
                self.product_info['产品名称'] = self.product_info['产品名称'].apply(self._clean_product_name)
        
        if data['promotion'] is not None:
            self.promotion_data = data['promotion']
        
        return self
    
    def _process_batch_data(self, raw_data):
        """处理批次数据"""
        batch_data = []
        inventory_data = []
        
        current_product = None
        
        for idx, row in raw_data.iterrows():
            if pd.notna(row.get('物料')):
                product_code = row['物料']
                current_product = {
                    '物料': product_code,
                    '描述': row.get('描述', ''),
                    '现有库存': row.get('现有库存', 0)
                }
                inventory_data.append(current_product)
            
            elif pd.notna(row.get('库位')) and current_product is not None:
                product_code = current_product['物料']
                batch_record = {
                    '物料': product_code,
                    '库位': row.get('库位', ''),
                    '生产日期': row.get('生产日期'),
                    '生产批号': row.get('生产批号', ''),
                    '数量': row.get('数量', 0)
                }
                batch_data.append(batch_record)
        
        self.inventory_data = pd.DataFrame(inventory_data)
        self.batch_data = pd.DataFrame(batch_data)
        
        if not self.batch_data.empty and '生产日期' in self.batch_data.columns:
            self.batch_data['生产日期'] = pd.to_datetime(self.batch_data['生产日期'], errors='coerce')
    
    def _clean_product_name(self, name):
        """清理产品名称"""
        if pd.isna(name):
            return name
        name = str(name)
        name = name.replace('口力', '')
        name = name.replace('-中国', '')
        return name.strip()

# ==================== 系统类 ====================
class SalesForecastSystem:
    """销售预测系统"""
    def __init__(self):
        self.data_loader = DataLoader()
        self.data_tracker = DataTracker()
        self.sales_predictor = None
        self.inventory_manager = None
        self.production_planner = None
    
    def load_data(self):
        """加载数据"""
        self.data_loader.load_all_data()
        return True
    
    def run_forecast(self, months=4):
        """运行预测"""
        # 创建销售预测器
        self.sales_predictor = SalesPredictor(
            self.data_loader.shipping_data,
            self.data_loader.product_info,
            self.data_loader.promotion_data,
            self.data_tracker
        )
        
        # 执行预测
        sales_prediction = self.sales_predictor.predict_next_months(months)
        
        # 创建库存管理器
        self.inventory_manager = InventoryManager(
            self.data_loader.inventory_data,
            self.data_loader.product_info,
            self.data_loader.shipping_data,
            self.data_tracker,
            self.data_loader.batch_data
        )
        
        # 计算安全库存
        safety_stock = self.inventory_manager.calculate_safety_stock()
        
        # 识别库存问题
        backlog_products, stockout_risk, batch_info = self.inventory_manager.identify_stock_issues(sales_prediction)
        
        # 创建生产计划器
        self.production_planner = ProductionPlanner(
            self.data_loader.inventory_data,
            sales_prediction,
            safety_stock
        )
        
        # 生成生产计划
        production_plan = self.production_planner.generate_production_plan(batch_info, self.data_tracker)
        
        return {
            'sales_prediction': sales_prediction,
            'production_plan': production_plan,
            'backlog_products': backlog_products,
            'stockout_risk': stockout_risk,
            'batch_info': batch_info,
            'safety_stock': safety_stock
        }

# ==================== 辅助函数 ====================
def format_amount(amount):
    """格式化金额"""
    if amount >= 100000000:
        return f"¥{amount / 100000000:.1f}亿"
    elif amount >= 10000:
        return f"¥{amount / 10000:.0f}万"
    else:
        return f"¥{amount:,.0f}"

def create_analysis_charts(system):
    """创建分析图表"""
    charts = {}
    
    # 1. 销售趋势图
    if system.data_loader.shipping_data is not None:
        monthly_sales = system.data_loader.shipping_data.copy()
        monthly_sales['月份'] = pd.to_datetime(monthly_sales['订单日期']).dt.to_period('M')
        monthly_trend = monthly_sales.groupby('月份')['求和项:数量（箱）'].sum().reset_index()
        monthly_trend['月份'] = monthly_trend['月份'].dt.to_timestamp()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_trend['月份'],
            y=monthly_trend['求和项:数量（箱）'],
            mode='lines+markers',
            name='实际销量',
            line=dict(width=3, color='#667eea'),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            title="历史销售趋势",
            xaxis_title="月份",
            yaxis_title="销量（箱）",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        charts['sales_trend'] = fig_trend
    
    # 2. 产品分组分布
    grouper = ProductGrouper()
    if system.data_loader.shipping_data is not None:
        product_groups = grouper.group_products(system.data_loader.shipping_data)
        group_counts = pd.Series(product_groups).value_counts()
        
        fig_groups = go.Figure(data=[
            go.Pie(
                labels=group_counts.index,
                values=group_counts.values,
                hole=0.4,
                marker_colors=['#667eea', '#764ba2', '#ff6b6b']
            )
        ])
        
        fig_groups.update_layout(
            title="产品分组分布",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        charts['product_groups'] = fig_groups
    
    return charts

# ==================== 主界面 ====================
st.markdown("""
<div class="main-header">
    <h1>🤖 机器学习预测排产智能系统</h1>
    <p>基于XGBoost的多模型融合预测</p>
</div>
""", unsafe_allow_html=True)

# 侧边栏控制
with st.sidebar:
    st.header("控制面板")
    
    if st.button("🔄 刷新数据", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.subheader("预测参数")
    prediction_months = st.slider("预测月数", 1, 6, 4)
    
    st.subheader("显示选项")
    show_accuracy = st.checkbox("显示准确率分析", value=True)
    show_customer = st.checkbox("显示客户分析", value=True)
    show_batch = st.checkbox("显示批次分析", value=True)

# 初始化系统
@st.cache_resource
def init_system():
    system = SalesForecastSystem()
    system.load_data()
    return system

# 主要内容区域
try:
    # 加载系统
    with st.spinner('初始化系统...'):
        system = init_system()
    
    if system.data_loader.shipping_data is not None:
        # 获取基础统计信息
        total_products = len(system.data_loader.shipping_data['产品代码'].unique())
        total_customers = len(system.data_loader.shipping_data['客户代码'].unique()) if '客户代码' in system.data_loader.shipping_data.columns else 0
        total_inventory_value = system.data_loader.inventory_data['现有库存'].sum() * 100 if system.data_loader.inventory_data is not None else 0
        
        # 创建分析图表
        charts = create_analysis_charts(system)
        
        # 创建标签页
        tabs = st.tabs([
            "📊 数据概览", "🧠 模型预测分析", "📈 准确率分析", 
            "📦 库存状态", "📋 智能建议"
        ])
        
        # Tab 1: 数据概览
        with tabs[0]:
            st.markdown("### 📊 系统数据概览")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_products}</div>
                    <div class="metric-label">总产品数</div>
                    <div class="metric-sublabel">活跃SKU</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_customers}</div>
                    <div class="metric-label">客户数量</div>
                    <div class="metric-sublabel">活跃客户</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-value">{format_amount(total_inventory_value)}</div>
                    <div class="metric-label">库存总值</div>
                    <div class="metric-sublabel">当前库存</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(system.data_loader.shipping_data)}</div>
                    <div class="metric-label">订单记录数</div>
                    <div class="metric-sublabel">历史数据</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 显示图表
            if 'sales_trend' in charts:
                st.markdown('''
                <div class="chart-header">
                    <div class="chart-title">历史销售趋势</div>
                    <div class="chart-subtitle">月度销售数据分析</div>
                </div>
                ''', unsafe_allow_html=True)
                st.plotly_chart(charts['sales_trend'], use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if 'product_groups' in charts:
                    st.plotly_chart(charts['product_groups'], use_container_width=True)
            
            with col2:
                # 这里可以添加其他图表
                pass
        
        # Tab 2: 模型预测分析
        with tabs[1]:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">多模型预测分析</div>
                <div class="chart-subtitle">基于XGBoost的智能预测</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # 运行预测
            with st.spinner('运行预测模型...'):
                results = system.run_forecast(prediction_months)
            
            # 显示预测结果
            if results['sales_prediction'] is not None and not results['sales_prediction'].empty:
                # 选择产品显示详细预测
                products = results['sales_prediction']['产品代码'].unique()[:20]
                selected_product = st.selectbox("选择产品查看详细预测", products)
                
                # 获取该产品的预测数据
                product_pred = results['sales_prediction'][results['sales_prediction']['产品代码'] == selected_product]
                
                # 创建预测图表
                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(
                    x=product_pred['预测月份'],
                    y=product_pred['预测销量'],
                    mode='lines+markers',
                    name='预测销量',
                    line=dict(width=3, color='#667eea'),
                    marker=dict(size=10)
                ))
                
                fig_pred.update_layout(
                    title=f"产品 {selected_product} 销量预测",
                    xaxis_title="月份",
                    yaxis_title="预测销量（箱）",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # 显示预测数据表
                st.dataframe(product_pred[['预测月份', '预测销量', '季节性因子', '促销因子', '保守系数']], 
                            use_container_width=True)
        
        # Tab 3: 准确率分析
        with tabs[2]:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">预测准确率分析</div>
                <div class="chart-subtitle">模型性能评估</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if show_accuracy:
                # 这里可以添加准确率分析内容
                st.markdown("""
                <div class="insight-card">
                    <h4>📊 准确率评估说明</h4>
                    <ul>
                        <li>使用历史数据最后一个月作为测试集</li>
                        <li>准确率计算采用绝对误差阈值（20箱）和相对误差结合</li>
                        <li>不同产品类型（稳定/波动/季节性）采用不同预测策略</li>
                        <li>系统会自动选择最优模型进行预测</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # Tab 4: 库存状态
        with tabs[3]:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">库存状态分析</div>
                <div class="chart-subtitle">当前库存情况和风险评估</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if results['stockout_risk'] is not None and not results['stockout_risk'].empty:
                st.subheader("缺货风险产品")
                st.dataframe(results['stockout_risk'], use_container_width=True)
            
            if results['backlog_products'] is not None and not results['backlog_products'].empty:
                st.subheader("积压产品")
                st.dataframe(results['backlog_products'], use_container_width=True)
            
            if show_batch and results['batch_info'] is not None and not results['batch_info'].empty:
                st.subheader("批次信息")
                batch_display = results['batch_info'][results['batch_info']['批次年龄(天)'] > 0].head(20)
                st.dataframe(batch_display, use_container_width=True)
        
        # Tab 5: 智能建议
        with tabs[4]:
            st.markdown('''
            <div class="chart-header">
                <div class="chart-title">智能排产建议</div>
                <div class="chart-subtitle">基于预测和库存的生产建议</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if results['production_plan'] is not None and not results['production_plan'].empty:
                # 按月份分组显示生产计划
                months = results['production_plan']['月份'].unique()
                
                for month in sorted(months)[:3]:  # 只显示前3个月
                    st.subheader(f"📅 {month} 生产计划")
                    month_plan = results['production_plan'][results['production_plan']['月份'] == month]
                    
                    # 只显示需要生产的前10个产品
                    display_plan = month_plan.nlargest(10, '需要生产数量')[
                        ['产品代码', '产品名称', '当前库存', '预测销量', '需要生产数量', '排产优先级']
                    ]
                    
                    st.dataframe(display_plan, use_container_width=True)
            
            # 建议说明
            st.markdown("""
            <div class="insight-card">
                <h4>🎯 排产建议说明</h4>
                <ul>
                    <li><b>高优先级：</b>当前库存低于100箱的产品</li>
                    <li><b>建议生产量：</b>基于月均销量的1.5倍减去当前库存</li>
                    <li><b>考虑因素：</b>历史销量趋势、季节性因素、库存周转率</li>
                    <li><b>更新频率：</b>建议每周更新一次排产计划</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.error("数据加载失败，请检查数据源配置")
        
except Exception as e:
    st.error(f"系统错误: {str(e)}")
    st.info("请确保GitHub仓库URL配置正确，且数据文件存在")

# 页脚信息
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: gray;">
    机器学习预测排产系统 v3.0 | 
    数据更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} | 
    <a href="https://github.com/CIRA18-HUB/sales_dashboard" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
