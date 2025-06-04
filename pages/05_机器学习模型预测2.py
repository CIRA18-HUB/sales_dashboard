# 5_机器学习模型预测.py - 基于GitHub数据的机器学习预测系统
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import io
import json
import pickle
import hashlib
from data_storage import storage

warnings.filterwarnings('ignore')

# 机器学习库
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

# ====================================================================
# 页面配置
# ====================================================================
st.set_page_config(
    page_title="🤖 机器学习模型预测",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏Streamlit默认元素
hide_elements = """
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# ====================================================================
# 样式定义
# ====================================================================
modern_ml_styles = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 头部样式 */
    .ml-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }

    .ml-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    .ml-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }

    /* 功能卡片 */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }

    /* 指标卡片 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border-left: 4px solid #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        height: 100%;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }

    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }

    /* 状态指示器 */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }

    .status-success { background-color: #4CAF50; }
    .status-warning { background-color: #FF9800; }
    .status-danger { background-color: #f44336; }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    .error-card {
        background: rgba(255, 82, 82, 0.1);
        border: 1px solid #ff5252;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .warning-card {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .success-card {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
"""

st.markdown(modern_ml_styles, unsafe_allow_html=True)

# ====================================================================
# 认证检查
# ====================================================================
def check_authentication():
    """检查用户认证状态"""
    return (
        'authenticated' in st.session_state and 
        st.session_state.authenticated and
        'username' in st.session_state and
        st.session_state.username != ""
    )

# 如果未认证，重定向到登录页面
if not check_authentication():
    st.markdown("""
    <div class="error-card">
        <h3>🔒 访问受限</h3>
        <p>您需要先登录才能访问机器学习预测系统。</p>
        <p>请返回登录页面完成身份验证。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔑 返回登录页面"):
        st.session_state.clear()
        st.rerun()
    
    st.stop()

# ====================================================================
# Session State 初始化
# ====================================================================
def initialize_ml_session_state():
    """初始化机器学习会话状态"""
    defaults = {
        'ml_model_trained': False,
        'ml_prediction_system': None,
        'ml_training_progress': 0.0,
        'ml_training_status': "等待开始",
        'ml_prediction_results': None,
        'ml_historical_analysis': None,
        'ml_accuracy_stats': None,
        'ml_feature_importance': None,
        'ml_model_comparison': None,
        'ml_data_loaded': False,
        'ml_data_validation_passed': False,
        # 训练参数
        'ml_test_ratio': 0.2,
        'ml_months_ahead': 3,
        'ml_outlier_factor': 3.0,
        'ml_min_data_points': 4,
        'ml_n_estimators': 300,
        'ml_max_depth': 5,
        'ml_learning_rate': 0.05,
        # GitHub配置
        'github_repo': 'CIRA18-HUB/sales_dashboard',
        'github_branch': 'main',
        'data_file_path': 'pages/2409-2502出货数据集.xlsx'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_ml_session_state()

# ====================================================================
# GitHub数据加载系统
# ====================================================================
class GitHubDataLoader:
    """GitHub数据加载器"""
    
    def __init__(self, repo, branch='main'):
        self.repo = repo
        self.branch = branch
        self.base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/"
    
    def load_excel_from_github(self, file_path, progress_callback=None):
        """从GitHub加载Excel文件"""
        try:
            if progress_callback:
                progress_callback(0.1, "🔗 连接GitHub仓库...")
            
            url = self.base_url + file_path
            
            if progress_callback:
                progress_callback(0.3, f"📥 下载文件: {file_path}")
            
            # 读取Excel文件
            df = pd.read_excel(url)
            
            if progress_callback:
                progress_callback(0.5, f"✅ 成功加载: {len(df)} 行数据")
            
            return df, {
                'source': 'GitHub',
                'repo': self.repo,
                'branch': self.branch,
                'file_path': file_path,
                'url': url,
                'rows': len(df),
                'columns': len(df.columns),
                'load_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            error_msg = f"从GitHub加载数据失败: {str(e)}"
            if progress_callback:
                progress_callback(0.1, f"❌ {error_msg}")
            raise Exception(error_msg)

# ====================================================================
# 机器学习预测系统类
# ====================================================================
class GitHubMLPredictionSystem:
    """基于GitHub数据的机器学习预测系统"""
    
    def __init__(self):
        self.shipment_data = None
        self.feature_data = None
        self.models = {}
        self.scalers = {}
        self.predictions = None
        self.accuracy_results = {}
        self.product_segments = {}
        self.historical_predictions = None
        self.historical_accuracy = None
        self.data_summary = {}
        self.training_time = None
        self.data_source_info = {}
        
    def load_data_from_github(self, progress_callback=None):
        """从GitHub加载数据"""
        try:
            loader = GitHubDataLoader(
                st.session_state.github_repo, 
                st.session_state.github_branch
            )
            
            # 加载数据
            self.shipment_data, self.data_source_info = loader.load_excel_from_github(
                st.session_state.data_file_path,
                progress_callback
            )
            
            if progress_callback:
                progress_callback(0.6, "🧹 数据清理中...")
            
            # 验证和清理数据
            self.shipment_data = self._validate_and_clean_data(self.shipment_data)
            
            if progress_callback:
                progress_callback(0.8, f"✅ 数据准备完成: {len(self.shipment_data)} 条记录")
            
            return True
            
        except Exception as e:
            error_msg = f"GitHub数据加载失败: {str(e)}"
            if progress_callback:
                progress_callback(0.1, f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def _validate_and_clean_data(self, raw_data):
        """验证和清理数据"""
        if len(raw_data) == 0:
            raise Exception("GitHub数据文件为空")
        
        # 列名标准化
        column_mapping = {
            '订单日期': 'order_date', '出货日期': 'order_date', '日期': 'order_date',
            '区域': 'region', '地区': 'region',
            '客户代码': 'customer_code', '客户编码': 'customer_code', '经销商代码': 'customer_code',
            '产品代码': 'product_code', '产品编码': 'product_code', '货号': 'product_code',
            '数量': 'quantity', '销量': 'quantity', '出货量': 'quantity', '箱数': 'quantity',
        }
        
        cleaned_data = raw_data.copy()
        
        # 应用列名映射
        for original_col in raw_data.columns:
            col_lower = str(original_col).lower().strip()
            for pattern, target in column_mapping.items():
                if pattern in col_lower or col_lower in pattern:
                    cleaned_data = cleaned_data.rename(columns={original_col: target})
                    break
        
        # 检查必要字段
        required_fields = ['order_date', 'product_code', 'quantity']
        missing_fields = [field for field in required_fields if field not in cleaned_data.columns]
        
        if missing_fields:
            raise Exception(f"GitHub数据缺少必要字段: {missing_fields}")
        
        # 添加默认字段
        if 'customer_code' not in cleaned_data.columns:
            cleaned_data['customer_code'] = 'DEFAULT_CUSTOMER'
        if 'region' not in cleaned_data.columns:
            cleaned_data['region'] = 'DEFAULT_REGION'
        
        # 数据类型转换
        cleaned_data['order_date'] = pd.to_datetime(cleaned_data['order_date'], errors='coerce')
        cleaned_data['quantity'] = pd.to_numeric(cleaned_data['quantity'], errors='coerce')
        
        # 清理无效数据
        cleaned_data = cleaned_data.dropna(subset=['order_date', 'product_code', 'quantity'])
        cleaned_data = cleaned_data[cleaned_data['quantity'] > 0]
        
        return cleaned_data
    
    def preprocess_data(self, progress_callback=None):
        """数据预处理"""
        if progress_callback:
            progress_callback(0.1, "🧹 数据预处理中...")
        
        # 异常值处理
        original_len = len(self.shipment_data)
        self.shipment_data = self._remove_outliers_iqr(self.shipment_data)
        
        # 产品分段
        self._segment_products()
        
        # 数据摘要
        self.data_summary = {
            'total_records': len(self.shipment_data),
            'total_products': self.shipment_data['product_code'].nunique(),
            'total_customers': self.shipment_data['customer_code'].nunique(),
            'date_range': (self.shipment_data['order_date'].min(), self.shipment_data['order_date'].max()),
            'total_quantity': self.shipment_data['quantity'].sum(),
            'avg_daily_quantity': self.shipment_data.groupby('order_date')['quantity'].sum().mean(),
            'data_source': self.data_source_info,
            'outliers_removed': original_len - len(self.shipment_data),
            'data_quality_score': self._calculate_data_quality_score()
        }
        
        if progress_callback:
            progress_callback(0.5, f"✅ 预处理完成: {len(self.shipment_data)} 行优质数据")
        
        return True
    
    def _remove_outliers_iqr(self, data, column='quantity', factor=3.0):
        """使用IQR方法移除异常值"""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
    
    def _segment_products(self):
        """产品分段"""
        product_stats = self.shipment_data.groupby('product_code')['quantity'].agg([
            'count', 'mean', 'std', 'min', 'max', 'sum'
        ]).reset_index()
        
        product_stats['cv'] = product_stats['std'] / product_stats['mean']
        product_stats['cv'] = product_stats['cv'].fillna(0)
        
        # 分段逻辑
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
        self.product_segments = dict(zip(product_stats['product_code'], product_stats['segment']))
        
        return product_stats
    
    def _calculate_data_quality_score(self):
        """计算数据质量评分"""
        score = 100
        
        # 时间跨度检查
        days_span = (self.data_summary['date_range'][1] - self.data_summary['date_range'][0]).days
        if days_span < 90:
            score -= 20
        elif days_span < 180:
            score -= 10
        
        # 产品数量检查
        if self.data_summary['total_products'] < 5:
            score -= 20
        elif self.data_summary['total_products'] < 10:
            score -= 10
        
        # 数据量检查
        if self.data_summary['total_records'] < 100:
            score -= 20
        elif self.data_summary['total_records'] < 500:
            score -= 10
        
        return max(0, score)
    
    def create_features(self, progress_callback=None):
        """创建特征"""
        if progress_callback:
            progress_callback(0.1, "🔧 特征工程中...")
        
        # 创建月度数据
        monthly_data = self.shipment_data.groupby([
            'product_code',
            self.shipment_data['order_date'].dt.to_period('M')
        ]).agg({
            'quantity': ['sum', 'count', 'mean', 'std'],
            'customer_code': 'nunique',
            'region': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]
        }).reset_index()
        
        monthly_data.columns = ['product_code', 'year_month', 'total_qty', 'order_count',
                               'avg_qty', 'std_qty', 'customer_count', 'main_region']
        monthly_data['std_qty'] = monthly_data['std_qty'].fillna(0)
        monthly_data = monthly_data.sort_values(['product_code', 'year_month'])
        
        # 创建特征
        all_features = []
        
        for product in self.product_segments.keys():
            product_data = monthly_data[monthly_data['product_code'] == product].copy()
            
            if len(product_data) < st.session_state.ml_min_data_points:
                continue
            
            # 时间序列特征创建
            for idx in range(3, len(product_data)):
                historical_data = product_data.iloc[:idx].copy()
                
                features = self._create_time_series_features(
                    product, historical_data, self.product_segments[product]
                )
                
                # 目标变量
                target_row = product_data.iloc[idx]
                features['target'] = target_row['total_qty']
                features['target_month'] = str(target_row['year_month'])
                features['segment'] = self.product_segments[product]
                
                all_features.append(features)
        
        self.feature_data = pd.DataFrame(all_features)
        
        if len(self.feature_data) == 0:
            raise Exception("无法创建特征数据，请检查GitHub数据质量和完整性")
        
        # 特征后处理
        self._post_process_features()
        
        if progress_callback:
            progress_callback(0.8, f"✅ 特征完成: {len(self.feature_data)} 时间序列样本")
        
        return True
    
    def _create_time_series_features(self, product_code, historical_data, segment):
        """创建时间序列特征"""
        features = {'product_code': product_code}
        
        if len(historical_data) < 3:
            return features
        
        qty_values = historical_data['total_qty'].values
        
        # 基础统计特征
        features.update({
            'qty_mean': np.mean(qty_values),
            'qty_median': np.median(qty_values),
            'qty_std': np.std(qty_values),
            'qty_cv': np.std(qty_values) / (np.mean(qty_values) + 1),
            
            # 滞后特征
            'qty_lag_1': qty_values[-1],
            'qty_lag_2': qty_values[-2] if len(qty_values) > 1 else 0,
            'qty_lag_3': qty_values[-3] if len(qty_values) > 2 else 0,
            
            # 移动平均
            'qty_ma_2': np.mean(qty_values[-2:]),
            'qty_ma_3': np.mean(qty_values[-3:]) if len(qty_values) >= 3 else np.mean(qty_values),
        })
        
        # 趋势特征
        if len(qty_values) > 2:
            x = np.arange(len(qty_values))
            trend_coef = np.polyfit(x, qty_values, 1)[0]
            features['trend_slope'] = trend_coef
            
            recent_growth = (qty_values[-1] - qty_values[-2]) / (qty_values[-2] + 1)
            features['recent_growth'] = recent_growth
            
            features['stability_score'] = 1 / (1 + features['qty_cv'])
        else:
            features.update({
                'trend_slope': 0,
                'recent_growth': 0,
                'stability_score': 0.5
            })
        
        # 时间特征
        last_period = historical_data.iloc[-1]['year_month']
        features.update({
            'month': last_period.month,
            'quarter': last_period.quarter,
            'is_year_end': 1 if last_period.month in [11, 12] else 0,
            'is_peak_season': 1 if last_period.month in [3, 4, 10, 11] else 0,
        })
        
        # 产品段特征
        segment_map = {
            '高销量稳定': 1, '高销量波动': 2, '中销量稳定': 3,
            '中销量波动': 4, '低销量稳定': 5, '低销量波动': 6
        }
        features['segment_encoded'] = segment_map.get(segment, 0)
        
        # 数据质量特征
        features.update({
            'data_points': len(qty_values),
            'consistency_score': len(qty_values[qty_values > 0]) / len(qty_values)
        })
        
        return features
    
    def _post_process_features(self):
        """特征后处理"""
        feature_cols = [col for col in self.feature_data.columns 
                       if col not in ['product_code', 'target', 'target_month', 'segment']]
        
        # 处理异常值
        self.feature_data[feature_cols] = self.feature_data[feature_cols].replace([np.inf, -np.inf], np.nan)
        self.feature_data[feature_cols] = self.feature_data[feature_cols].fillna(0)
        
        # 移除常数特征
        constant_features = [col for col in feature_cols if self.feature_data[col].std() == 0]
        if constant_features:
            self.feature_data = self.feature_data.drop(columns=constant_features)
    
    def train_models(self, progress_callback=None):
        """训练机器学习模型"""
        if progress_callback:
            progress_callback(0.1, "🚀 开始训练机器学习模型...")
        
        start_time = time.time()
        
        # 准备数据
        feature_cols = [col for col in self.feature_data.columns 
                       if col not in ['product_code', 'target', 'target_month', 'segment']]
        
        X = self.feature_data[feature_cols]
        y = self.feature_data['target']
        
        # 时间序列分割
        self.feature_data['target_month_dt'] = pd.to_datetime(self.feature_data['target_month'])
        sorted_indices = self.feature_data.sort_values('target_month_dt').index
        
        X = X.loc[sorted_indices]
        y = y.loc[sorted_indices]
        
        # 训练测试分割
        n_samples = len(X)
        split_point = int(n_samples * (1 - st.session_state.ml_test_ratio))
        
        X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
        y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]
        
        # 特征缩放
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['feature_scaler'] = scaler
        
        # 训练模型
        models = {}
        predictions = {}
        
        # XGBoost
        if progress_callback:
            progress_callback(0.3, "🎯 训练XGBoost模型...")
        
        xgb_model = xgb.XGBRegressor(
            n_estimators=st.session_state.ml_n_estimators,
            max_depth=st.session_state.ml_max_depth,
            learning_rate=st.session_state.ml_learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        xgb_model.fit(X_train_scaled, y_train, verbose=False)
        xgb_pred = np.maximum(xgb_model.predict(X_test_scaled), 0)
        
        models['XGBoost'] = xgb_model
        predictions['XGBoost'] = xgb_pred
        
        # LightGBM
        if progress_callback:
            progress_callback(0.5, "🎯 训练LightGBM模型...")
        
        lgb_model = lgb.LGBMRegressor(
            n_estimators=st.session_state.ml_n_estimators,
            max_depth=st.session_state.ml_max_depth,
            learning_rate=st.session_state.ml_learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        
        lgb_model.fit(X_train_scaled, y_train)
        lgb_pred = np.maximum(lgb_model.predict(X_test_scaled), 0)
        
        models['LightGBM'] = lgb_model
        predictions['LightGBM'] = lgb_pred
        
        # Random Forest
        if progress_callback:
            progress_callback(0.7, "🎯 训练Random Forest模型...")
        
        rf_model = RandomForestRegressor(
            n_estimators=int(st.session_state.ml_n_estimators * 0.7),
            max_depth=st.session_state.ml_max_depth + 5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = np.maximum(rf_model.predict(X_test_scaled), 0)
        
        models['RandomForest'] = rf_model
        predictions['RandomForest'] = rf_pred
        
        # 模型融合
        weights = self._calculate_model_weights(predictions, y_test)
        ensemble_pred = (weights['XGBoost'] * predictions['XGBoost'] + 
                        weights['LightGBM'] * predictions['LightGBM'] + 
                        weights['RandomForest'] * predictions['RandomForest'])
        
        predictions['Ensemble'] = ensemble_pred
        
        # 模型评估
        results = {}
        for model_name, pred in predictions.items():
            smape_accuracies = self.calculate_batch_robust_accuracy(y_test.values, pred)
            smape_accuracy = np.mean(smape_accuracies)
            
            mae = np.mean(np.abs(y_test - pred))
            rmse = np.sqrt(mean_squared_error(y_test, pred))
            r2 = r2_score(y_test, pred)
            
            results[model_name] = {
                'SMAPE_Accuracy': smape_accuracy,
                'MAE': mae,
                'RMSE': rmse,
                'R²': r2
            }
        
        # 选择最佳模型
        best_model_name = max(results.keys(), key=lambda x: results[x]['SMAPE_Accuracy'])
        
        self.models = {
            'best_model': models[best_model_name],
            'best_model_name': best_model_name,
            'all_models': models,
            'feature_cols': feature_cols,
            'weights': weights if best_model_name == 'Ensemble' else None
        }
        
        self.accuracy_results = results
        self.training_time = time.time() - start_time
        
        if progress_callback:
            best_accuracy = results[best_model_name]['SMAPE_Accuracy']
            progress_callback(1.0, f"✅ 训练完成! {best_model_name}: {best_accuracy:.1f}%")
        
        return True
    
    def calculate_batch_robust_accuracy(self, actual_values, predicted_values):
        """批量计算SMAPE准确率"""
        actual_values = np.array(actual_values)
        predicted_values = np.array(predicted_values)
        
        both_zero = (actual_values == 0) & (predicted_values == 0)
        
        smape = 200 * np.abs(actual_values - predicted_values) / (
            np.abs(actual_values) + np.abs(predicted_values) + 1e-8
        )
        accuracy = np.maximum(0, 100 - smape)
        accuracy[both_zero] = 100.0
        
        return accuracy
    
    def _calculate_model_weights(self, predictions, y_true):
        """计算模型融合权重"""
        scores = {}
        for name, pred in predictions.items():
            smape_accuracies = self.calculate_batch_robust_accuracy(y_true.values, pred)
            scores[name] = np.mean(smape_accuracies)
        
        total_score = sum(scores.values())
        if total_score > 0:
            weights = {name: score / total_score for name, score in scores.items()}
        else:
            weights = {name: 1/len(scores) for name in scores.keys()}
        
        return weights
    
    def predict_future(self, months_ahead=None):
        """预测未来销量"""
        if months_ahead is None:
            months_ahead = st.session_state.ml_months_ahead
        
        predictions = []
        products = self.feature_data['product_code'].unique()
        
        for product in products:
            product_features = self.feature_data[
                self.feature_data['product_code'] == product
            ].tail(1)
            
            if len(product_features) == 0:
                continue
            
            for month in range(1, months_ahead + 1):
                X = product_features[self.models['feature_cols']]
                X_scaled = self.scalers['feature_scaler'].transform(X)
                
                # 预测
                if self.models['best_model_name'] == 'Ensemble':
                    xgb_pred = self.models['all_models']['XGBoost'].predict(X_scaled)[0]
                    lgb_pred = self.models['all_models']['LightGBM'].predict(X_scaled)[0]
                    rf_pred = self.models['all_models']['RandomForest'].predict(X_scaled)[0]
                    
                    weights = self.models['weights']
                    final_pred = (weights['XGBoost'] * xgb_pred + 
                                 weights['LightGBM'] * lgb_pred + 
                                 weights['RandomForest'] * rf_pred)
                else:
                    final_pred = self.models['best_model'].predict(X_scaled)[0]
                
                final_pred = max(0, final_pred)
                
                # 置信区间
                segment = product_features['segment'].iloc[0]
                confidence_factor = self._get_confidence_factor(segment)
                lower_bound = max(0, final_pred * (1 - confidence_factor))
                upper_bound = final_pred * (1 + confidence_factor)
                
                # 目标月份
                target_month = datetime.now().replace(day=1) + timedelta(days=32*month)
                target_month_str = target_month.strftime('%Y-%m')
                
                predictions.append({
                    '产品代码': product,
                    '未来月份': month,
                    '目标月份': target_month_str,
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
        """获取置信度因子"""
        confidence_map = {
            '高销量稳定': 0.15,
            '高销量波动': 0.25,
            '中销量稳定': 0.20,
            '中销量波动': 0.30,
            '低销量稳定': 0.25,
            '低销量波动': 0.35
        }
        return confidence_map.get(segment, 0.25)

# ====================================================================
# 界面函数
# ====================================================================

def render_ml_header():
    """渲染机器学习头部"""
    user_display = st.session_state.get('display_name', st.session_state.get('username', '用户'))
    
    st.markdown(f"""
    <div class="ml-header">
        <h1 class="ml-title">🤖 机器学习模型预测</h1>
        <p class="ml-subtitle">
            基于GitHub数据的智能销量预测系统 | 欢迎 {user_display}
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;">
            <span style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px;">✅ GitHub数据源</span>
            <span style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px;">🤖 多模型融合</span>
            <span style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px;">📊 时序分析</span>
            <span style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px;">🎯 智能预测</span>
        </div>
        <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
            数据源: {st.session_state.github_repo} | 文件: {st.session_state.data_file_path}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_data_loading_tab():
    """数据加载标签页"""
    st.markdown("### 📁 GitHub数据加载")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🔗 GitHub数据源配置")
        
        # GitHub配置
        st.session_state.github_repo = st.text_input(
            "GitHub仓库", 
            value=st.session_state.github_repo,
            help="格式: 用户名/仓库名"
        )
        
        st.session_state.github_branch = st.text_input(
            "分支名称", 
            value=st.session_state.github_branch
        )
        
        st.session_state.data_file_path = st.text_input(
            "数据文件路径", 
            value=st.session_state.data_file_path,
            help="相对于仓库根目录的文件路径"
        )
        
        # 数据加载按钮
        if st.button("🔍 加载GitHub数据", type="primary", use_container_width=True):
            try:
                with st.spinner("正在从GitHub加载数据..."):
                    # 初始化系统
                    system = GitHubMLPredictionSystem()
                    
                    # 创建进度显示
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def update_progress(progress, message):
                        progress_bar.progress(progress)
                        status_text.text(message)
                    
                    # 加载和预处理数据
                    if system.load_data_from_github(update_progress):
                        system.preprocess_data(update_progress)
                        
                        # 保存到session state
                        st.session_state.ml_prediction_system = system
                        st.session_state.ml_data_loaded = True
                        st.session_state.ml_data_validation_passed = True
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        # 显示数据摘要
                        st.success("✅ GitHub数据加载成功！")
                        
                        summary = system.data_summary
                        
                        st.markdown(f"""
                        <div class="success-card">
                            <h4>📊 GitHub数据摘要</h4>
                            <p><strong>仓库:</strong> {summary['data_source']['repo']}</p>
                            <p><strong>文件:</strong> {summary['data_source']['file_path']}</p>
                            <p><strong>数据记录:</strong> {summary['total_records']:,} 条</p>
                            <p><strong>产品数量:</strong> {summary['total_products']} 个</p>
                            <p><strong>客户数量:</strong> {summary['total_customers']} 个</p>
                            <p><strong>时间跨度:</strong> {summary['date_range'][0].strftime('%Y-%m-%d')} 至 {summary['date_range'][1].strftime('%Y-%m-%d')}</p>
                            <p><strong>总销量:</strong> {summary['total_quantity']:,.0f} 箱</p>
                            <p><strong>数据质量:</strong> {summary['data_quality_score']}/100</p>
                            <p><strong>加载时间:</strong> {summary['data_source']['load_time']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 数据预览
                        st.markdown("##### 📋 GitHub数据预览")
                        st.dataframe(system.shipment_data.head(10), use_container_width=True)
                        
            except Exception as e:
                st.error(f"❌ GitHub数据加载失败: {str(e)}")
                st.markdown(f"""
                <div class="error-card">
                    <h4>💡 GitHub数据加载建议</h4>
                    <p>请检查以下设置:</p>
                    <ul>
                        <li>GitHub仓库名称是否正确</li>
                        <li>分支名称是否存在</li>
                        <li>数据文件路径是否正确</li>
                        <li>文件是否为Excel格式(.xlsx)</li>
                        <li>仓库是否为公开仓库</li>
                    </ul>
                    <p><strong>当前配置:</strong></p>
                    <p>仓库: {st.session_state.github_repo}</p>
                    <p>分支: {st.session_state.github_branch}</p>
                    <p>文件: {st.session_state.data_file_path}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📋 GitHub配置说明")
        
        requirements = f"""
        <div class="feature-card">
            <h4>✅ 当前配置</h4>
            <p><strong>仓库:</strong> {st.session_state.github_repo}</p>
            <p><strong>分支:</strong> {st.session_state.github_branch}</p>
            <p><strong>文件:</strong> {st.session_state.data_file_path}</p>
            
            <h4>🔧 配置要求</h4>
            <ul>
                <li>公开GitHub仓库</li>
                <li>Excel格式(.xlsx)文件</li>
                <li>包含销售数据列</li>
                <li>正确的文件路径</li>
            </ul>
            
            <h4>📊 数据要求</h4>
            <ul>
                <li>日期列（订单日期）</li>
                <li>产品代码列</li>
                <li>销量/数量列</li>
                <li>至少3个月数据</li>
            </ul>
        </div>
        """
        
        st.markdown(requirements, unsafe_allow_html=True)
        
        # GitHub URL预览
        if st.session_state.github_repo and st.session_state.data_file_path:
            github_url = f"https://raw.githubusercontent.com/{st.session_state.github_repo}/{st.session_state.github_branch}/{st.session_state.data_file_path}"
            
            st.markdown("#### 🔗 数据源URL")
            st.code(github_url, language="text")

def show_ml_training_tab():
    """机器学习训练标签页"""
    st.markdown("### 🚀 机器学习模型训练")
    
    if not st.session_state.ml_data_loaded:
        st.warning("⚠️ 请先加载GitHub数据")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🎯 多模型融合训练")
        
        # 训练说明
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 机器学习模型</h4>
            <ul>
                <li>🟦 <strong>XGBoost:</strong> 梯度提升树模型，处理非线性关系</li>
                <li>🟩 <strong>LightGBM:</strong> 轻量级梯度提升，快速训练</li>
                <li>🟨 <strong>Random Forest:</strong> 随机森林模型，鲁棒性强</li>
                <li>🟪 <strong>Ensemble:</strong> 多模型融合，提升预测精度</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 训练按钮
        if st.button("🚀 开始机器学习训练", type="primary", use_container_width=True):
            try:
                system = st.session_state.ml_prediction_system
                
                with st.container():
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def update_progress(progress, message):
                        progress_bar.progress(progress)
                        status_text.text(message)
                    
                    # 特征工程
                    if system.create_features(update_progress):
                        # 模型训练
                        if system.train_models(update_progress):
                            # 预测未来
                            system.predict_future()
                            
                            # 保存系统
                            st.session_state.ml_prediction_system = system
                            st.session_state.ml_model_trained = True
                            
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.success("🎉 机器学习模型训练完成！")
                            st.balloons()
                            st.rerun()
                
            except Exception as e:
                st.error(f"❌ 训练失败: {str(e)}")
    
    with col2:
        if st.session_state.ml_model_trained and st.session_state.ml_prediction_system:
            system = st.session_state.ml_prediction_system
            
            st.markdown("#### 🏆 训练结果")
            
            best_model = system.models['best_model_name']
            best_accuracy = system.accuracy_results[best_model]['SMAPE_Accuracy']
            
            # 准确率卡片
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{best_accuracy:.1f}%</div>
                <div class="metric-label">SMAPE准确率</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 训练摘要
            st.markdown(f"""
            <div class="feature-card">
                <h4>✅ 训练完成</h4>
                <p><strong>最佳模型:</strong> {best_model}</p>
                <p><strong>训练时间:</strong> {system.training_time:.1f}秒</p>
                <p><strong>特征数:</strong> {len(system.models['feature_cols'])}</p>
                <p><strong>训练样本:</strong> {len(system.feature_data)}</p>
                <p><strong>数据质量:</strong> {system.data_summary['data_quality_score']}/100</p>
                <p><strong>数据源:</strong> GitHub</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 模型对比
            st.markdown("#### 📊 模型对比")
            comparison_data = []
            for model_name, results in system.accuracy_results.items():
                comparison_data.append({
                    '模型': model_name,
                    'SMAPE准确率': f"{results['SMAPE_Accuracy']:.1f}%",
                    'MAE': f"{results['MAE']:.1f}",
                    'R²': f"{results['R²']:.3f}"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        else:
            system = st.session_state.ml_prediction_system
            summary = system.data_summary
            
            st.markdown("#### 📊 训练准备就绪")
            st.markdown(f"""
            <div class="feature-card">
                <h4>🎯 GitHub数据就绪</h4>
                <p><strong>数据源:</strong> {summary['data_source']['repo']}</p>
                <p><strong>记录数:</strong> {summary['total_records']:,}</p>
                <p><strong>产品数:</strong> {summary['total_products']}</p>
                <p><strong>质量评分:</strong> {summary['data_quality_score']}/100</p>
                <p><strong>时间跨度:</strong> {(summary['date_range'][1] - summary['date_range'][0]).days} 天</p>
                
                <h5>🔧 训练特点:</h5>
                <ul>
                    <li>多模型融合训练</li>
                    <li>时间序列特征工程</li>
                    <li>SMAPE准确率评估</li>
                    <li>自适应权重优化</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def show_ml_prediction_tab():
    """机器学习预测结果标签页"""
    st.markdown("### 🔮 智能预测结果")
    
    if not st.session_state.ml_model_trained:
        st.warning("⚠️ 请先完成机器学习模型训练")
        return
    
    system = st.session_state.ml_prediction_system
    
    # 预测结果展示
    if system.predictions is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 预测汇总图
            monthly_summary = system.predictions.groupby('未来月份').agg({
                '预测销量': 'sum',
                '下限': 'sum',
                '上限': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"第{m}个月" for m in monthly_summary['未来月份']],
                y=monthly_summary['预测销量'],
                name='预测销量',
                marker_color='#667eea'
            ))
            
            fig.add_trace(go.Scatter(
                x=[f"第{m}个月" for m in monthly_summary['未来月份']],
                y=monthly_summary['上限'],
                mode='lines',
                name='上限',
                line=dict(color='red', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=[f"第{m}个月" for m in monthly_summary['未来月份']],
                y=monthly_summary['下限'],
                mode='lines',
                name='下限',
                line=dict(color='green', dash='dash')
            ))
            
            fig.update_layout(
                title="🤖 机器学习智能预测汇总",
                xaxis_title="月份",
                yaxis_title="预测销量",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            total_pred = system.predictions['预测销量'].sum()
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_pred:,.0f}</div>
                <div class="metric-label">总预测销量(箱)</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="feature-card">
                <h4>🤖 智能预测摘要</h4>
                <p><strong>预测产品:</strong> {system.predictions['产品代码'].nunique()} 个</p>
                <p><strong>预测月数:</strong> {system.predictions['未来月份'].max()} 个月</p>
                <p><strong>最佳模型:</strong> {system.models['best_model_name']}</p>
                <p><strong>预测记录:</strong> {len(system.predictions)} 条</p>
                <p><strong>数据来源:</strong> GitHub</p>
                <p><strong>置信区间:</strong> 已计算</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 产品段预测分析
        st.markdown("#### 📊 产品段预测分析")
        
        segment_summary = system.predictions.groupby('产品段').agg({
            '预测销量': ['sum', 'mean', 'count']
        }).round(2)
        
        segment_summary.columns = ['总预测量', '平均预测量', '产品数']
        segment_summary = segment_summary.reset_index()
        
        fig_segment = px.pie(
            segment_summary, 
            values='总预测量', 
            names='产品段',
            title="📈 各产品段预测销量分布"
        )
        st.plotly_chart(fig_segment, use_container_width=True)
        
        # 详细预测表格
        st.markdown("#### 📋 详细预测记录")
        
        display_columns = ['产品代码', '未来月份', '目标月份', '预测销量', '下限', '上限', '产品段', '使用模型']
        st.dataframe(
            system.predictions[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # 导出功能
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = system.predictions.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载CSV格式",
                data=csv,
                file_name=f"ML预测结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # 创建Excel文件
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                system.predictions.to_excel(writer, sheet_name='预测结果', index=False)
                segment_summary.to_excel(writer, sheet_name='产品段汇总', index=False)
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📊 下载Excel格式",
                data=excel_data,
                file_name=f"ML预测结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            # 预测摘要JSON
            prediction_summary = {
                'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'model_used': system.models['best_model_name'],
                'total_prediction': float(total_pred),
                'products_count': int(system.predictions['产品代码'].nunique()),
                'months_ahead': int(system.predictions['未来月份'].max()),
                'data_source': system.data_source_info,
                'accuracy': system.accuracy_results[system.models['best_model_name']]
            }
            
            st.download_button(
                label="📋 下载预测摘要",
                data=json.dumps(prediction_summary, ensure_ascii=False, indent=2),
                file_name=f"ML预测摘要_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def create_ml_sidebar():
    """创建机器学习侧边栏"""
    with st.sidebar:
        st.markdown("### 🎛️ ML控制台")
        
        # 用户信息
        user_display = st.session_state.get('display_name', st.session_state.get('username', '用户'))
        st.markdown(f"👋 欢迎, {user_display}")
        
        # 系统状态
        st.markdown("#### 📊 系统状态")
        
        if st.session_state.ml_data_loaded:
            data_color = "success"
            data_text = "GitHub数据已加载"
        else:
            data_color = "warning"
            data_text = "等待加载数据"
        
        if st.session_state.ml_model_trained:
            model_color = "success"
            model_text = "ML模型已训练"
        else:
            model_color = "warning"
            model_text = "等待模型训练"
        
        st.markdown(f"""
        <div class="feature-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-indicator status-{data_color}"></span>
                <strong>{data_text}</strong>
            </div>
            <div style="display: flex; align-items: center;">
                <span class="status-indicator status-{model_color}"></span>
                <strong>{model_text}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ML训练参数
        st.markdown("#### ⚙️ ML参数")
        st.session_state.ml_test_ratio = st.slider("测试集比例", 0.1, 0.3, st.session_state.ml_test_ratio, 0.05)
        st.session_state.ml_months_ahead = st.slider("预测月数", 1, 6, st.session_state.ml_months_ahead)
        
        with st.expander("高级ML参数"):
            st.session_state.ml_outlier_factor = st.slider("异常值因子", 2.0, 5.0, st.session_state.ml_outlier_factor, 0.5)
            st.session_state.ml_min_data_points = st.slider("最小数据点", 3, 6, st.session_state.ml_min_data_points)
            st.session_state.ml_n_estimators = st.slider("树的数量", 100, 500, st.session_state.ml_n_estimators, 50)
            st.session_state.ml_max_depth = st.slider("最大深度", 3, 15, st.session_state.ml_max_depth)
            st.session_state.ml_learning_rate = st.slider("学习率", 0.01, 0.2, st.session_state.ml_learning_rate, 0.01)
        
        # 快捷操作
        st.markdown("#### ⚡ 快捷操作")
        
        if st.button("📊 返回主页", use_container_width=True):
            # 清除当前页面状态，返回主登录后页面
            for key in list(st.session_state.keys()):
                if key.startswith('ml_'):
                    del st.session_state[key]
            st.rerun()
        
        if st.button("🔄 重置ML系统", use_container_width=True):
            for key in ['ml_model_trained', 'ml_prediction_system', 'ml_data_loaded', 
                       'ml_data_validation_passed']:
                if key in st.session_state:
                    if key in ['ml_model_trained', 'ml_data_loaded', 'ml_data_validation_passed']:
                        st.session_state[key] = False
                    else:
                        st.session_state[key] = None
            st.success("✅ ML系统已重置")
            st.rerun()
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.clear()
            st.success("👋 已退出登录")
            st.rerun()

# ====================================================================
# 主程序
# ====================================================================

def main():
    """主程序"""
    render_ml_header()
    create_ml_sidebar()
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 GitHub数据",
        "🚀 ML训练", 
        "🔮 智能预测",
        "🔍 系统信息"
    ])
    
    with tab1:
        show_data_loading_tab()
    
    with tab2:
        show_ml_training_tab()
    
    with tab3:
        show_ml_prediction_tab()
    
    with tab4:
        if st.session_state.ml_model_trained:
            system = st.session_state.ml_prediction_system
            
            st.markdown("### 🔍 机器学习系统信息")
            
            # GitHub数据源信息
            st.markdown("#### 📊 GitHub数据源")
            source_info = system.data_summary['data_source']
            st.json(source_info)
            
            # ML模型信息
            st.markdown("#### 🤖 ML模型信息")
            model_info = {
                'best_model': system.models['best_model_name'],
                'feature_count': len(system.models['feature_cols']),
                'training_time': f"{system.training_time:.2f}秒",
                'data_quality_score': system.data_summary['data_quality_score'],
                'github_repo': st.session_state.github_repo,
                'data_file': st.session_state.data_file_path
            }
            st.json(model_info)
            
            # 准确率详情
            st.markdown("#### 🎯 模型准确率详情")
            st.json(system.accuracy_results)
            
            # 特征重要性（如果可用）
            if hasattr(system.models['best_model'], 'feature_importances_'):
                st.markdown("#### 📈 特征重要性")
                feature_importance = pd.DataFrame({
                    'feature': system.models['feature_cols'],
                    'importance': system.models['best_model'].feature_importances_
                }).sort_values('importance', ascending=False)
                
                fig_importance = px.bar(
                    feature_importance.head(10), 
                    x='importance', 
                    y='feature',
                    orientation='h',
                    title="Top 10 特征重要性"
                )
                st.plotly_chart(fig_importance, use_container_width=True)
            
        else:
            st.info("请先完成机器学习模型训练以查看系统信息")

if __name__ == "__main__":
    main()
