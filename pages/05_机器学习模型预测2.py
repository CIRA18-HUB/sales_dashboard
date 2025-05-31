# pages/05_机器学习模型预测.py
"""
机器学习销售预测系统 - 完整集成版
包含数据加载、模型训练、预测和可视化
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
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
import os
import time

# 页面配置
st.set_page_config(
    page_title="机器学习模型预测",
    page_icon="🤖",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 页面标题样式 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* 指标卡片样式 */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
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
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 信息框样式 */
    .info-box {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* 表格样式 */
    .dataframe {
        border: none !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #667eea !important;
        color: white !important;
        padding: 0.75rem !important;
    }
    
    .dataframe td {
        padding: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🤖 机器学习模型预测</h1>
    <p class="main-subtitle">基于XGBoost、LightGBM和RandomForest的高精度销售预测</p>
</div>
""", unsafe_allow_html=True)

# 初始化session state
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'prediction_system' not in st.session_state:
    st.session_state.prediction_system = None
if 'training_history' not in st.session_state:
    st.session_state.training_history = []

class EnhancedSalesPredictionSystem:
    """增强版销售预测系统"""
    
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
            shipment_file = "2409~25022出货数据.xlsx"
            promotion_file = "24-25促销效果销售数据.xlsx"
            
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
        """数据预处理"""
        if progress_callback:
            progress_callback(0.3, "数据预处理中...")
        
        # 标准化列名
        shipment_columns = {
            '订单日期': 'order_date',
            '所属区域': 'region', 
            '客户代码': 'customer_code',
            '产品代码': 'product_code',
            '求和项:数量（箱）': 'quantity'
        }
        
        # 重命名列
        for old_col, new_col in shipment_columns.items():
            if old_col in self.shipment_data.columns:
                self.shipment_data = self.shipment_data.rename(columns={old_col: new_col})
        
        # 数据类型转换
        self.shipment_data['order_date'] = pd.to_datetime(self.shipment_data['order_date'])
        self.shipment_data['quantity'] = pd.to_numeric(self.shipment_data['quantity'], errors='coerce')
        
        # 数据清洗
        self.shipment_data = self.shipment_data.dropna(subset=['order_date', 'product_code', 'quantity'])
        self.shipment_data = self.shipment_data[self.shipment_data['quantity'] > 0]
        
        # 异常值处理
        self.shipment_data = self._remove_outliers_iqr(self.shipment_data, factor=3.0)
        
        # 产品分段
        self._segment_products()
        
        if progress_callback:
            progress_callback(0.4, f"✅ 预处理完成: {len(self.shipment_data)} 行, {self.shipment_data['product_code'].nunique()} 个产品")
        
        return True
    
    def _remove_outliers_iqr(self, data, column='quantity', factor=3.0):
        """使用IQR方法移除异常值"""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        data_cleaned = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        
        return data_cleaned
    
    def _segment_products(self):
        """产品分段"""
        # 计算每个产品的销量特征
        product_stats = self.shipment_data.groupby('product_code')['quantity'].agg([
            'count', 'mean', 'std', 'sum'
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
        """创建特征"""
        if progress_callback:
            progress_callback(0.5, "特征工程处理中...")
        
        # 创建月度数据
        monthly_data = self.shipment_data.groupby([
            'product_code',
            self.shipment_data['order_date'].dt.to_period('M')
        ]).agg({
            'quantity': ['sum', 'count', 'mean', 'std'],
            'customer_code': 'nunique'
        }).reset_index()
        
        # 扁平化列名
        monthly_data.columns = ['product_code', 'year_month', 'total_qty', 'order_count',
                                'avg_qty', 'std_qty', 'customer_count']
        monthly_data['std_qty'] = monthly_data['std_qty'].fillna(0)
        
        # 排序
        monthly_data = monthly_data.sort_values(['product_code', 'year_month'])
        
        # 为每个产品创建特征
        all_features = []
        
        for product in self.product_segments.keys():
            product_data = monthly_data[monthly_data['product_code'] == product].copy()
            
            if len(product_data) < 4:
                continue
            
            # 为每个时间点创建特征
            for idx in range(3, len(product_data)):
                features = self._create_product_features(
                    product, product_data.iloc[:idx], self.product_segments[product]
                )
                
                # 目标变量
                target_row = product_data.iloc[idx]
                features['target'] = target_row['total_qty']
                features['target_month'] = str(target_row['year_month'])
                features['segment'] = self.product_segments[product]
                
                all_features.append(features)
        
        self.feature_data = pd.DataFrame(all_features)
        
        if progress_callback:
            progress_callback(0.6, f"✅ 特征创建完成: {len(self.feature_data)} 条数据, {len(self.feature_data.columns) - 4} 个特征")
        
        return True
    
    def _create_product_features(self, product_code, historical_data, segment):
        """为单个产品创建特征"""
        features = {'product_code': product_code}
        
        if len(historical_data) < 3:
            return features
        
        # 基础数据
        qty_values = historical_data['total_qty'].values
        order_counts = historical_data['order_count'].values
        customer_counts = historical_data['customer_count'].values
        
        # 销量特征
        features.update({
            'qty_mean': np.mean(qty_values),
            'qty_std': np.std(qty_values),
            'qty_cv': np.std(qty_values) / (np.mean(qty_values) + 1),
            
            # 滞后特征
            'qty_lag_1': qty_values[-1],
            'qty_lag_2': qty_values[-2] if len(qty_values) > 1 else 0,
            'qty_lag_3': qty_values[-3] if len(qty_values) > 2 else 0,
            
            # 移动平均
            'qty_ma_2': np.mean(qty_values[-2:]),
            'qty_ma_3': np.mean(qty_values[-3:]) if len(qty_values) >= 3 else np.mean(qty_values),
            
            # 加权移动平均
            'qty_wma_3': np.average(qty_values[-3:], weights=[1, 2, 3]) if len(qty_values) >= 3 else np.mean(qty_values),
        })
        
        # 趋势特征
        if len(qty_values) > 1:
            features['growth_rate_1'] = (qty_values[-1] - qty_values[-2]) / (qty_values[-2] + 1)
            
            if len(qty_values) > 2:
                x = np.arange(len(qty_values))
                trend_coef = np.polyfit(x, qty_values, 1)[0]
                features['trend_slope'] = trend_coef
            else:
                features['trend_slope'] = 0
        else:
            features['growth_rate_1'] = 0
            features['trend_slope'] = 0
        
        # 时间特征
        last_month = historical_data.iloc[-1]['year_month']
        features.update({
            'month': last_month.month,
            'quarter': last_month.quarter,
            'is_year_end': 1 if last_month.month in [11, 12] else 0,
            'is_peak_season': 1 if last_month.month in [3, 4, 10, 11] else 0,
        })
        
        # 产品段特征
        segment_map = {
            '高销量稳定': 1, '高销量波动': 2,
            '中销量稳定': 3, '中销量波动': 4,
            '低销量稳定': 5, '低销量波动': 6
        }
        features['segment_encoded'] = segment_map.get(segment, 0)
        
        return features
    
    def train_models(self, test_ratio=0.2, progress_callback=None):
        """训练模型"""
        if progress_callback:
            progress_callback(0.7, "开始训练模型...")
        
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
        
        # 特征标准化
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['feature_scaler'] = scaler
        
        # 训练多个模型
        models = {}
        predictions = {}
        
        # 1. XGBoost
        if progress_callback:
            progress_callback(0.75, "训练XGBoost...")
        
        xgb_model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_log_train, verbose=False)
        xgb_pred = np.expm1(xgb_model.predict(X_test_scaled))
        models['XGBoost'] = xgb_model
        predictions['XGBoost'] = xgb_pred
        
        # 2. LightGBM
        if progress_callback:
            progress_callback(0.85, "训练LightGBM...")
        
        lgb_model = lgb.LGBMRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        lgb_model.fit(X_train_scaled, y_log_train)
        lgb_pred = np.expm1(lgb_model.predict(X_test_scaled))
        models['LightGBM'] = lgb_model
        predictions['LightGBM'] = lgb_pred
        
        # 3. Random Forest
        if progress_callback:
            progress_callback(0.9, "训练Random Forest...")
        
        rf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = rf_model.predict(X_test_scaled)
        models['RandomForest'] = rf_model
        predictions['RandomForest'] = rf_pred
        
        # 4. 融合模型
        weights = self._calculate_model_weights(predictions, y_test)
        ensemble_pred = sum(weights[name] * pred for name, pred in predictions.items())
        predictions['Ensemble'] = ensemble_pred
        
        # 评估模型
        results = {}
        
        for model_name, pred in predictions.items():
            pred = np.maximum(pred, 0)
            mape = np.mean(np.abs((y_test - pred) / np.maximum(y_test, 1))) * 100
            accuracy = max(0, 100 - mape)
            
            results[model_name] = {
                'Accuracy': accuracy,
                'MAPE': mape,
                'MAE': np.mean(np.abs(y_test - pred)),
                'R²': r2_score(y_test, pred)
            }
        
        # 保存最佳模型
        best_model_name = max(results.keys(), key=lambda x: results[x]['Accuracy'])
        
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
            self.feature_importance = pd.DataFrame({
                '特征': feature_cols,
                '重要性': models['XGBoost'].feature_importances_
            }).sort_values('重要性', ascending=False)
        
        if progress_callback:
            progress_callback(1.0, f"✅ 训练完成！最佳模型: {best_model_name} (准确率: {results[best_model_name]['Accuracy']:.1f}%)")
        
        return True
    
    def _calculate_model_weights(self, predictions, y_true):
        """计算模型融合权重"""
        scores = {}
        for name, pred in predictions.items():
            pred = np.maximum(pred, 0)
            mape = np.mean(np.abs((y_true - pred) / np.maximum(y_true, 1))) * 100
            scores[name] = max(0, 100 - mape)
        
        total_score = sum(scores.values())
        weights = {name: score / total_score for name, score in scores.items()}
        
        return weights
    
    def predict_future(self, months_ahead=3, product_list=None):
        """预测未来销量"""
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
                    pred_values = []
                    for model_name, model in self.models['all_models'].items():
                        if model_name in ['XGBoost', 'LightGBM']:
                            pred = np.expm1(model.predict(X_scaled)[0])
                        else:
                            pred = model.predict(X_scaled)[0]
                        pred_values.append(self.models['weights'][model_name] * pred)
                    final_pred = sum(pred_values)
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
            '高销量稳定': 0.15,
            '高销量波动': 0.25,
            '中销量稳定': 0.20,
            '中销量波动': 0.30,
            '低销量稳定': 0.25,
            '低销量波动': 0.35
        }
        return confidence_map.get(segment, 0.25)

# 创建侧边栏
with st.sidebar:
    st.markdown("### 🎯 模型训练控制")
    
    # 训练选项
    st.markdown("#### 训练参数")
    test_ratio = st.slider("测试集比例", 0.1, 0.3, 0.2, 0.05)
    
    # 预测选项
    st.markdown("#### 预测设置")
    months_ahead = st.selectbox("预测月数", [1, 2, 3, 6], index=2)
    
    # 模型信息
    if st.session_state.model_trained:
        st.markdown("---")
        st.markdown("### 📊 当前模型信息")
        system = st.session_state.prediction_system
        
        if system and system.models:
            st.success(f"✅ 最佳模型: {system.models['best_model_name']}")
            
            best_accuracy = system.accuracy_results[system.models['best_model_name']]['Accuracy']
            st.metric("模型准确率", f"{best_accuracy:.1f}%")
            
            st.info(f"""
            - 特征数量: {len(system.models['feature_cols'])}
            - 产品数量: {len(system.product_segments)}
            - 训练样本: {len(system.feature_data)}
            """)

# 主界面
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 模型训练", "🔮 销量预测", "📊 模型评估", "📈 特征分析", "📑 历史记录"])

# Tab 1: 模型训练
with tab1:
    st.markdown("### 🚀 一键训练预测模型")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🔄 开始训练", type="primary", use_container_width=True):
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 初始化系统
            system = EnhancedSalesPredictionSystem()
            
            # 定义进度回调
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # 执行训练流程
            try:
                # 1. 加载数据
                if system.load_data_from_github(update_progress):
                    time.sleep(0.5)
                    
                    # 2. 数据预处理
                    if system.preprocess_data(update_progress):
                        time.sleep(0.5)
                        
                        # 3. 特征工程
                        if system.create_features(update_progress):
                            time.sleep(0.5)
                            
                            # 4. 训练模型
                            if system.train_models(test_ratio, update_progress):
                                # 保存到session state
                                st.session_state.prediction_system = system
                                st.session_state.model_trained = True
                                
                                # 记录训练历史
                                st.session_state.training_history.append({
                                    'time': datetime.now(),
                                    'accuracy': system.accuracy_results[system.models['best_model_name']]['Accuracy'],
                                    'model': system.models['best_model_name']
                                })
                                
                                st.success("🎉 模型训练完成！")
                                st.balloons()
                            else:
                                st.error("模型训练失败")
                        else:
                            st.error("特征创建失败")
                    else:
                        st.error("数据预处理失败")
                else:
                    st.error("数据加载失败")
                    
            except Exception as e:
                st.error(f"训练过程出错: {str(e)}")
                
    with col2:
        st.info("""
        **训练说明：**
        - 系统将自动从GitHub加载最新数据
        - 使用XGBoost、LightGBM和RandomForest三种模型
        - 自动选择最佳模型进行预测
        - 训练过程大约需要1-2分钟
        """)
    
    # 显示训练结果
    if st.session_state.model_trained:
        st.markdown("---")
        st.markdown("### 📊 训练结果")
        
        system = st.session_state.prediction_system
        
        # 显示各模型性能
        col1, col2, col3, col4 = st.columns(4)
        
        for idx, (model_name, metrics) in enumerate(system.accuracy_results.items()):
            with [col1, col2, col3, col4][idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['Accuracy']:.1f}%</div>
                    <div class="metric-label">{model_name}</div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">
                        MAE: {metrics['MAE']:.1f}<br>
                        R²: {metrics['R²']:.3f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 产品分段统计
        st.markdown("### 📦 产品分段统计")
        
        segment_counts = pd.Series(list(system.product_segments.values())).value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=segment_counts.index,
                values=segment_counts.values,
                hole=0.3,
                marker_colors=['#667eea', '#764ba2', '#9f7aea', '#b794f4', '#d6bcfa', '#e9d8fd']
            )
        ])
        
        fig.update_layout(
            title="产品分段分布",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: 销量预测
with tab2:
    st.markdown("### 🔮 智能销量预测")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先在'模型训练'页面训练模型")
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
                        hovermode='x unified'
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
                        file_name=f'销量预测_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv'
                    )
                else:
                    st.error("预测失败，请检查数据和模型")

# Tab 3: 模型评估
with tab3:
    st.markdown("### 📊 模型性能评估")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先训练模型")
    else:
        system = st.session_state.prediction_system
        
        # 模型对比
        st.markdown("#### 🏆 模型性能对比")
        
        # 创建性能对比图
        models = list(system.accuracy_results.keys())
        metrics_data = {
            'Accuracy': [system.accuracy_results[m]['Accuracy'] for m in models],
            'MAPE': [system.accuracy_results[m]['MAPE'] for m in models],
            'R²': [system.accuracy_results[m]['R²'] * 100 for m in models]
        }
        
        fig = go.Figure()
        
        # 添加准确率条形图
        fig.add_trace(go.Bar(
            name='准确率 (%)',
            x=models,
            y=metrics_data['Accuracy'],
            marker_color='#667eea',
            text=[f'{v:.1f}%' for v in metrics_data['Accuracy']],
            textposition='outside'
        ))
        
        # 添加R²条形图
        fig.add_trace(go.Bar(
            name='R² (%)',
            x=models,
            y=metrics_data['R²'],
            marker_color='#764ba2',
            text=[f'{v:.1f}%' for v in metrics_data['R²']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="模型性能指标对比",
            xaxis_title="模型",
            yaxis_title="性能指标 (%)",
            barmode='group',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细指标表
        st.markdown("#### 📋 详细性能指标")
        
        performance_df = pd.DataFrame([
            {
                '模型': model,
                '准确率 (%)': metrics['Accuracy'],
                'MAPE (%)': metrics['MAPE'],
                'MAE': metrics['MAE'],
                'R²': metrics['R²']
            }
            for model, metrics in system.accuracy_results.items()
        ])
        
        # 高亮最佳值
        def highlight_best(s):
            if s.name in ['准确率 (%)', 'R²']:
                return ['background-color: #90EE90' if v == s.max() else '' for v in s]
            elif s.name in ['MAPE (%)', 'MAE']:
                return ['background-color: #90EE90' if v == s.min() else '' for v in s]
            return [''] * len(s)
        
        st.dataframe(
            performance_df.style.apply(highlight_best).format({
                '准确率 (%)': '{:.2f}',
                'MAPE (%)': '{:.2f}',
                'MAE': '{:.2f}',
                'R²': '{:.4f}'
            }),
            use_container_width=True
        )
        
        # 模型选择建议
        best_model = system.models['best_model_name']
        best_accuracy = system.accuracy_results[best_model]['Accuracy']
        
        if best_accuracy >= 95:
            recommendation = "🌟 模型表现优秀，可以直接用于生产环境"
            color = "#00FF00"
        elif best_accuracy >= 90:
            recommendation = "✅ 模型表现良好，建议继续监控优化"
            color = "#90EE90"
        elif best_accuracy >= 85:
            recommendation = "⚠️ 模型表现一般，建议增加特征或调整参数"
            color = "#FFD700"
        else:
            recommendation = "❌ 模型表现较差，需要重新评估数据和方法"
            color = "#FF6347"
        
        st.markdown(f"""
        <div class="info-box" style="border-left-color: {color};">
            <h4>🎯 模型评估结论</h4>
            <p>当前最佳模型: <strong>{best_model}</strong></p>
            <p>准确率: <strong>{best_accuracy:.1f}%</strong></p>
            <p>{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

# Tab 4: 特征分析
with tab4:
    st.markdown("### 📈 特征重要性分析")
    
    if not st.session_state.model_trained:
        st.warning("⚠️ 请先训练模型")
    else:
        system = st.session_state.prediction_system
        
        if system.feature_importance is not None:
            # 特征重要性图
            top_features = system.feature_importance.head(15)
            
            # 特征名称映射
            feature_name_map = {
                'qty_mean': '销量均值',
                'qty_std': '销量标准差',
                'qty_cv': '销量变异系数',
                'qty_lag_1': '滞后1期销量',
                'qty_lag_2': '滞后2期销量',
                'qty_lag_3': '滞后3期销量',
                'qty_ma_2': '2期移动平均',
                'qty_ma_3': '3期移动平均',
                'qty_wma_3': '3期加权移动平均',
                'growth_rate_1': '增长率',
                'trend_slope': '趋势斜率',
                'month': '月份',
                'quarter': '季度',
                'is_year_end': '是否年末',
                'is_peak_season': '是否旺季',
                'segment_encoded': '产品段编码'
            }
            
            # 映射特征名称
            top_features['特征名称'] = top_features['特征'].map(lambda x: feature_name_map.get(x, x))
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_features['重要性'],
                y=top_features['特征名称'],
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
                title="Top 15 特征重要性",
                xaxis_title="重要性得分",
                yaxis_title="特征",
                height=600,
                margin=dict(l=150)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 特征说明
            st.markdown("#### 📖 特征说明")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **销量相关特征：**
                - **销量均值**: 历史销量的平均值
                - **滞后特征**: 前1-3期的销量值
                - **移动平均**: 近期销量的平均趋势
                - **变异系数**: 销量波动程度
                """)
            
            with col2:
                st.markdown("""
                **时间相关特征：**
                - **月份/季度**: 捕捉季节性规律
                - **年末标识**: 年底销售高峰
                - **旺季标识**: 传统销售旺季
                - **趋势斜率**: 销量变化趋势
                """)
            
            # 特征相关性分析
            st.markdown("#### 🔗 特征相关性分析")
            
            # 计算特征相关性
            feature_data = system.feature_data[system.models['feature_cols']]
            correlation_matrix = feature_data.corr()
            
            # 选择与目标变量相关性最高的特征
            target_corr = system.feature_data[system.models['feature_cols']].corrwith(
                system.feature_data['target']
            ).abs().sort_values(ascending=False).head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=target_corr.values,
                y=[feature_name_map.get(f, f) for f in target_corr.index],
                orientation='h',
                marker_color='#764ba2',
                text=[f'{v:.3f}' for v in target_corr.values],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="与目标变量相关性最高的特征",
                xaxis_title="相关系数",
                yaxis_title="特征",
                height=400,
                margin=dict(l=150)
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Tab 5: 历史记录
with tab5:
    st.markdown("### 📑 训练历史记录")
    
    if len(st.session_state.training_history) == 0:
        st.info("暂无训练记录")
    else:
        # 显示训练历史
        history_df = pd.DataFrame(st.session_state.training_history)
        history_df['time'] = pd.to_datetime(history_df['time'])
        history_df = history_df.sort_values('time', ascending=False)
        
        # 格式化显示
        history_df['训练时间'] = history_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        history_df['准确率'] = history_df['accuracy'].apply(lambda x: f"{x:.2f}%")
        history_df['模型'] = history_df['model']
        
        st.dataframe(
            history_df[['训练时间', '模型', '准确率']],
            use_container_width=True,
            hide_index=True
        )
        
        # 准确率趋势图
        if len(history_df) > 1:
            st.markdown("#### 📈 准确率趋势")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=history_df['time'],
                y=history_df['accuracy'],
                mode='lines+markers',
                name='准确率',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title="模型准确率变化趋势",
                xaxis_title="训练时间",
                yaxis_title="准确率 (%)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 清除历史记录
        if st.button("🗑️ 清除历史记录"):
            st.session_state.training_history = []
            st.rerun()

# 底部信息
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🤖 机器学习销售预测系统 v2.0 | 
    使用 XGBoost + LightGBM + RandomForest | 
    数据更新时间: {:%Y-%m-%d}
</div>
""".format(datetime.now()), unsafe_allow_html=True)