# config.py - 完整配置文件
# 登录密码
PASSWORD = 'SAL!2025'

# 颜色主题 - 与sales_dashboard.py保持一致
COLORS = {
    'primary': '#1f3867',  # 主色调 - 深蓝色
    'secondary': '#4c78a8',  # 次色调 - 中蓝色
    'success': '#4CAF50',  # 成功色 - 绿色
    'warning': '#FF9800',  # 警告色 - 橙色
    'danger': '#F44336',  # 危险色 - 红色
    'info': '#2196F3',  # 信息色 - 蓝色
    'light': '#f8f9fa',  # 浅色背景
    'dark': '#343a40',  # 深色文字
    'white': '#ffffff',  # 白色
    'gray': '#6c757d'  # 灰色
}

# 数据文件路径
DATA_FILES = {
    'sales_data': '仪表盘原始数据.xlsx',
    'inventory_data': '仪表盘实时库存.xlsx',
    'promotion_data': '仪表盘促销活动.xlsx',
    'monthly_inventory': '仪表盘月终月末库存.xlsx',
    'forecast_data': '仪表盘人工预测.xlsx',
    'product_codes': '仪表盘产品代码.txt',
    'new_product_codes': '仪表盘新品代码.txt',
    'sales_target': '仪表盘销售月度指标维护.xlsx',
    'customer_relations': '仪表盘人与客户关系表.xlsx',
    'tt_product_target': '仪表盘TT产品月度指标.xlsx',
    'customer_target': '仪表盘客户月度指标维护.xlsx'
}

# BCG矩阵颜色配置
BCG_COLORS = {
    'cash_cow': '#4CAF50',  # 现金牛产品
    'star': '#1f3867',  # 明星产品
    'question': '#FF9800',  # 问号产品
    'dog': '#F44336'  # 瘦狗产品
}

# 新增：业务配置参数
BUSINESS_CONFIG = {
    # 产品分类标准
    'new_product_threshold': 0.015,  # 新品销售占比阈值 1.5%
    'growth_threshold': 0.20,  # 成长率阈值 20%

    # 客户分类标准
    'top_customer_count': 5,  # TOP客户数量
    'dependency_threshold': 0.60,  # 客户依赖度风险阈值 60%

    # 库存风险阈值
    'inventory_risk_days': 90,  # 库存风险天数
    'low_stock_threshold': 30,  # 低库存警告天数

    # 销售目标相关
    'target_achievement_good': 0.95,  # 良好达成率 95%
    'target_achievement_excellent': 1.05,  # 优秀达成率 105%
}

# 格式化函数配置
FORMAT_CONFIG = {
    'currency_unit_threshold': {
        'billion': 100000000,  # 亿元
        'million': 10000,  # 万元
    },
    'decimal_places': {
        'currency': 2,  # 货币小数位
        'percentage': 1,  # 百分比小数位
        'quantity': 0,  # 数量小数位
    }
}

# 图表默认配置
CHART_CONFIG = {
    'height': {
        'small': 300,
        'medium': 400,
        'large': 500,
        'extra_large': 600
    },
    'color_sequences': {
        'primary': ['#1f3867', '#4c78a8', '#4CAF50', '#FF9800', '#2196F3'],
        'blues': ['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3'],
        'greens': ['#e8f5e8', '#c8e6c9', '#a5d6a7', '#81c784', '#66bb6a', '#4caf50'],
    },
    'font_family': 'Arial, sans-serif',
    'margins': {
        'small': dict(l=20, r=20, t=60, b=20),
        'medium': dict(l=50, r=50, t=60, b=50),
        'large': dict(l=80, r=80, t=80, b=80)
    }
}