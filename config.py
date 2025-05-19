# config.py
# 配置文件，存储全局设置

# 登录密码
PASSWORD = 'SAL!2025'

# 颜色主题
COLOR_THEME = {
    'primary': '#1f77b4',  # 主题色
    'secondary': '#ff7f0e',  # 次主题色
    'success': '#2ca02c',  # 正向指标
    'warning': '#d62728',  # 警告指标
    'info': '#9467bd',  # 信息指标
    'background': '#f8f9fa',  # 背景色
}

# BCG矩阵配置
BCG_CONFIG = {
    'cash_cow_color': '#2ca02c',  # 现金牛产品颜色
    'star_color': '#1f77b4',      # 明星产品颜色
    'question_mark_color': '#ff7f0e',  # 问号产品颜色
    'dog_color': '#d62728',       # 瘦狗产品颜色
}

# 销售达成阈值（用于颜色编码）
ACHIEVEMENT_THRESHOLDS = {
    'excellent': 1.0,  # 达成率>=100%
    'good': 0.9,       # 达成率>=90%
    'warning': 0.8,    # 达成率>=80%
    'danger': 0.7      # 达成率>=70%
}

# 指标卡配置
METRIC_CARD_STYLE = """
    <style>
    .metric-card {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        text-align: center;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }
    .metric-card:hover {
        box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-title {
        font-size: 16px;
        color: #666;
    }
    .metric-change {
        font-size: 14px;
        margin-top: 5px;
    }
    .positive-change {
        color: #2ca02c;
    }
    .negative-change {
        color: #d62728;
    }
    </style>
"""

# 数据文件路径（将按照实际GitHub仓库中的路径调整）
DATA_PATHS = {
    'sales_data': 'data/仪表盘原始数据.xlsx',
    'inventory_data': 'data/仪表盘实时库存.xlsx',
    'promotion_data': 'data/仪表盘促销活动.xlsx',
    'monthly_inventory': 'data/仪表盘月终月末库存.xlsx',
    'forecast_data': 'data/仪表盘人工预测.xlsx',
    'product_codes': 'data/仪表盘产品代码.txt',
    'new_product_codes': 'data/仪表盘新品代码.txt',
    'sales_target': 'data/仪表盘销售月度指标维护.xlsx',
    'customer_relations': 'data/仪表盘人与客户关系表.xlsx',
    'tt_product_target': 'data/仪表盘TT产品月度指标.xlsx',
    'customer_target': 'data/仪表盘客户月度指标维护.xlsx'
}