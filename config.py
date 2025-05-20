# config.py - 极简配置文件
# 登录密码
PASSWORD = 'SAL!2025'

# 颜色主题
COLORS = {
    'primary': '#1f3867',      # 主色调 - 深蓝色
    'secondary': '#4c78a8',    # 次色调 - 中蓝色
    'success': '#4CAF50',      # 成功色 - 绿色
    'warning': '#FF9800',      # 警告色 - 橙色
    'danger': '#F44336',       # 危险色 - 红色
    'info': '#2196F3',         # 信息色 - 蓝色
    'light': '#f8f9fa',        # 浅色背景
    'dark': '#343a40',         # 深色文字
    'white': '#ffffff',        # 白色
    'gray': '#6c757d'          # 灰色
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
    'cash_cow': '#4CAF50',    # 现金牛产品
    'star': '#1f3867',        # 明星产品
    'question': '#FF9800',    # 问号产品
    'dog': '#F44336'          # 瘦狗产品
}