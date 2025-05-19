# utils/data_loader.py
# 数据加载和处理模块

import pandas as pd
import numpy as np
import os

# 加载所有数据源
def load_all_data(data_paths):
    """
    加载所有数据源并返回字典形式的数据集
    
    参数:
        data_paths (dict): 包含所有数据文件路径的字典
        
    返回:
        dict: 包含所有加载数据的字典
    """
    data = {}
    
    # 加载销售数据
    try:
        data['sales_data'] = pd.read_excel(data_paths['sales_data'])
        # 将发运月份转换为日期格式
        data['sales_data']['发运月份'] = pd.to_datetime(data['sales_data']['发运月份'])
    except Exception as e:
        print(f"加载销售数据失败: {str(e)}")
        data['sales_data'] = pd.DataFrame()
    
    # 加载库存数据
    try:
        data['inventory_data'] = pd.read_excel(data_paths['inventory_data'])
    except Exception as e:
        print(f"加载库存数据失败: {str(e)}")
        data['inventory_data'] = pd.DataFrame()
    
    # 加载促销活动数据
    try:
        data['promotion_data'] = pd.read_excel(data_paths['promotion_data'])
        # 将日期列转换为日期格式
        date_columns = ['申请时间', '促销开始供货时间', '促销结束供货时间']
        for col in date_columns:
            if col in data['promotion_data'].columns:
                data['promotion_data'][col] = pd.to_datetime(data['promotion_data'][col])
    except Exception as e:
        print(f"加载促销活动数据失败: {str(e)}")
        data['promotion_data'] = pd.DataFrame()
    
    # 加载月终月末库存数据
    try:
        data['monthly_inventory'] = pd.read_excel(data_paths['monthly_inventory'])
        # 将所属年月转换为日期格式
        data['monthly_inventory']['所属年月'] = pd.to_datetime(data['monthly_inventory']['所属年月'])
    except Exception as e:
        print(f"加载月终月末库存数据失败: {str(e)}")
        data['monthly_inventory'] = pd.DataFrame()
    
    # 加载人工预测数据
    try:
        data['forecast_data'] = pd.read_excel(data_paths['forecast_data'])
        # 将所属年月转换为日期格式
        data['forecast_data']['所属年月'] = pd.to_datetime(data['forecast_data']['所属年月'])
    except Exception as e:
        print(f"加载人工预测数据失败: {str(e)}")
        data['forecast_data'] = pd.DataFrame()
    
    # 加载产品代码
    try:
        with open(data_paths['product_codes'], 'r') as f:
            data['product_codes'] = [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"加载产品代码失败: {str(e)}")
        data['product_codes'] = []
    
    # 加载新品代码
    try:
        with open(data_paths['new_product_codes'], 'r') as f:
            data['new_product_codes'] = [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"加载新品代码失败: {str(e)}")
        data['new_product_codes'] = []
    
    # 加载销售目标数据
    try:
        data['sales_target'] = pd.read_excel(data_paths['sales_target'])
        # 将指标年月转换为日期格式
        data['sales_target']['指标年月'] = pd.to_datetime(data['sales_target']['指标年月'])
    except Exception as e:
        print(f"加载销售目标数据失败: {str(e)}")
        data['sales_target'] = pd.DataFrame()
    
    # 加载客户关系数据
    try:
        data['customer_relations'] = pd.read_excel(data_paths['customer_relations'])
    except Exception as e:
        print(f"加载客户关系数据失败: {str(e)}")
        data['customer_relations'] = pd.DataFrame()
    
    # 加载TT产品目标数据
    try:
        data['tt_product_target'] = pd.read_excel(data_paths['tt_product_target'])
        # 将指标年月转换为日期格式
        data['tt_product_target']['指标年月'] = pd.to_datetime(data['tt_product_target']['指标年月'])
    except Exception as e:
        print(f"加载TT产品目标数据失败: {str(e)}")
        data['tt_product_target'] = pd.DataFrame()
    
    # 加载客户目标数据
    try:
        data['customer_target'] = pd.read_excel(data_paths['customer_target'])
        # 将月份转换为日期格式
        data['customer_target']['月份'] = pd.to_datetime(data['customer_target']['月份'])
    except Exception as e:
        print(f"加载客户目标数据失败: {str(e)}")
        data['customer_target'] = pd.DataFrame()
    
    # 预处理销售数据 - 分离MT和TT渠道
    if not data['sales_data'].empty:
        # 判断订单类型创建渠道字段
        data['sales_data']['渠道'] = data['sales_data']['订单类型'].apply(
            lambda x: 'TT' if x == '订单-TT产品' else ('MT' if x == '订单-正常产品' else '其他')
        )
        
        # 过滤销售订单（只包括正常产品和TT产品）
        data['sales_orders'] = data['sales_data'][
            data['sales_data']['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()
        
        # 过滤费用订单（促销相关订单）
        data['expense_orders'] = data['sales_data'][
            data['sales_data']['订单类型'].isin([
                '陈列激励明细-F1', '促销补差支持-F1', 
                '促销搭赠支持-F1', '门店运维激励费用-F3', 
                '全国旧日期库存处理-F3'
            ])
        ].copy()
    
    return data

# 应用筛选条件到数据集
def apply_filters(data, filters):
    """
    根据筛选条件过滤数据
    
    参数:
        data (DataFrame): 原始数据框
        filters (dict): 筛选条件字典
        
    返回:
        DataFrame: 筛选后的数据框
    """
    filtered_data = data.copy()
    
    # 应用区域筛选
    if filters.get('region') is not None:
        filtered_data = filtered_data[filtered_data['所属区域'] == filters['region']]
    
    # 应用销售人员筛选
    if filters.get('sales_person') is not None:
        filtered_data = filtered_data[filtered_data['申请人'] == filters['sales_person']]
    
    # 应用客户筛选
    if filters.get('customer') is not None:
        # 先尝试匹配客户代码
        customer_match = filtered_data['客户代码'] == filters['customer']
        # 再尝试匹配客户简称或经销商名称
        if customer_match.sum() == 0:
            customer_match = (
                (filtered_data['客户简称'] == filters['customer']) | 
                (filtered_data['经销商名称'] == filters['customer'])
            )
        filtered_data = filtered_data[customer_match]
    
    # 应用产品筛选
    if filters.get('product') is not None:
        # 先尝试匹配产品代码
        product_match = filtered_data['产品代码'] == filters['product']
        # 再尝试匹配产品简称或产品名称
        if product_match.sum() == 0:
            product_match = (
                (filtered_data['产品简称'] == filters['product']) | 
                (filtered_data['产品名称'] == filters['product'])
            )
        filtered_data = filtered_data[product_match]
    
    # 应用日期范围筛选
    if filters.get('date_range') is not None and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        filtered_data = filtered_data[
            (filtered_data['发运月份'] >= pd.Timestamp(start_date)) & 
            (filtered_data['发运月份'] <= pd.Timestamp(end_date))
        ]
    
    return filtered_data

# 计算产品BCG象限
def categorize_products(sales_data, product_codes):
    """
    根据销售占比和增长率将产品分类为现金牛、明星、问号和瘦狗
    
    参数:
        sales_data (DataFrame): 销售数据
        product_codes (list): 允许的产品代码列表
        
    返回:
        DataFrame: 包含产品分类的数据框
    """
    # 过滤只包含指定产品代码的销售数据
    filtered_sales = sales_data[sales_data['产品代码'].isin(product_codes)].copy()
    
    # 计算每个产品的销售总额
    product_total_sales = filtered_sales.groupby('产品代码')['求和项:金额（元）'].sum().reset_index()
    
    # 计算总销售额
    total_sales = product_total_sales['求和项:金额（元）'].sum()
    
    # 计算每个产品的销售占比
    product_total_sales['销售占比'] = product_total_sales['求和项:金额（元）'] / total_sales
    
    # 计算每个产品的增长率（这里简化为相对于平均值的增长）
    # 在实际应用中，应该比较不同时间段的销售额计算增长率
    # 这里做一个简化的模拟
    # 如果有上一年同期数据，可以用实际增长率替换这个模拟
    
    # 为每个产品随机生成一个-30%到70%之间的增长率（仅供演示）
    np.random.seed(42)  # 设置随机种子以获得可重复的结果
    product_total_sales['增长率'] = np.random.uniform(-0.3, 0.7, len(product_total_sales))
    
    # 根据销售占比和增长率对产品进行分类
    def categorize(row):
        if row['销售占比'] >= 0.015:  # 销售占比>=1.5%
            if row['增长率'] >= 0.2:  # 增长率>=20%
                return '明星产品'
            else:
                return '现金牛产品'
        else:  # 销售占比<1.5%
            if row['增长率'] >= 0.2:  # 增长率>=20%
                return '问号产品'
            else:
                return '瘦狗产品'
    
    product_total_sales['产品类型'] = product_total_sales.apply(categorize, axis=1)
    
    return product_total_sales

# 计算销售达成率
def calculate_sales_achievement(sales_data, target_data, period):
    """
    计算销售达成率
    
    参数:
        sales_data (DataFrame): 销售数据
        target_data (DataFrame): 目标数据
        period (str): 时间周期，可以是'monthly'、'quarterly'或'yearly'
        
    返回:
        DataFrame: 包含销售达成率的数据框
    """
    # 确保销售数据和目标数据都有所需的列
    if not {'发运月份', '求和项:金额（元）'}.issubset(sales_data.columns) or \
       not {'指标年月', '月度指标'}.issubset(target_data.columns):
        return pd.DataFrame()
    
    # 按月份和销售人员分组计算销售额
    sales_by_month = sales_data.groupby([
        pd.Grouper(key='发运月份', freq='M'), '申请人'
    ])['求和项:金额（元）'].sum().reset_index()
    
    # 将月份格式调整为与目标数据相同
    sales_by_month['月份'] = sales_by_month['发运月份'].dt.to_period('M').dt.to_timestamp()
    
    # 将目标数据的月份格式调整
    target_data['月份'] = target_data['指标年月'].dt.to_period('M').dt.to_timestamp()
    
    # 合并销售数据和目标数据
    achievement_data = pd.merge(
        sales_by_month,
        target_data[['月份', '申请人', '月度指标']],
        on=['月份', '申请人'],
        how='left'
    )
    
    # 计算达成率
    achievement_data['达成率'] = achievement_data['求和项:金额（元）'] / achievement_data['月度指标']
    
    # 根据时间周期聚合数据
    if period == 'quarterly':
        achievement_data['季度'] = achievement_data['月份'].dt.to_period('Q').dt.to_timestamp()
        achievement_data = achievement_data.groupby(['季度', '申请人']).agg({
            '求和项:金额（元）': 'sum',
            '月度指标': 'sum',
            '达成率': 'mean'
        }).reset_index()
    elif period == 'yearly':
        achievement_data['年份'] = achievement_data['月份'].dt.to_period('Y').dt.to_timestamp()
        achievement_data = achievement_data.groupby(['年份', '申请人']).agg({
            '求和项:金额（元）': 'sum',
            '月度指标': 'sum',
            '达成率': 'mean'
        }).reset_index()
    
    return achievement_data

# 物料使用效率分析
def analyze_material_efficiency(sales_data, inventory_data):
    """
    分析物料使用效率
    
    参数:
        sales_data (DataFrame): 销售数据
        inventory_data (DataFrame): 库存数据
        
    返回:
        DataFrame: 包含物料使用效率分析的数据框
    """
    # 确保数据包含所需列
    if not {'产品代码', '求和项:数量（箱）', '发运月份'}.issubset(sales_data.columns) or \
       not {'物料', '现有库存'}.issubset(inventory_data.columns):
        return pd.DataFrame()
    
    # 按产品代码和月份分组计算销售量
    monthly_sales = sales_data.groupby([
        '产品代码', pd.Grouper(key='发运月份', freq='M')
    ])['求和项:数量（箱）'].sum().reset_index()
    
    # 计算每个产品的月平均销售量
    avg_monthly_sales = monthly_sales.groupby('产品代码')['求和项:数量（箱）'].mean().reset_index()
    avg_monthly_sales.rename(columns={'求和项:数量（箱）': '月平均销量'}, inplace=True)
    
    # 物料与产品代码对应（假设产品代码与物料代码相同或有映射关系）
    # 在实际应用中，可能需要一个映射表来将产品代码映射到物料代码
    inventory_summary = inventory_data.groupby('物料').agg({
        '现有库存': 'sum',
        '已分配量': 'sum',
        '现有库存可订量': 'sum',
        '待入库量': 'sum'
    }).reset_index()
    
    # 将物料当作产品代码（假设它们相同或有映射关系）
    inventory_summary.rename(columns={'物料': '产品代码'}, inplace=True)
    
    # 合并销售和库存数据
    efficiency_data = pd.merge(
        inventory_summary,
        avg_monthly_sales,
        on='产品代码',
        how='left'
    )
    
    # 处理缺失值（没有销售记录的产品）
    efficiency_data['月平均销量'].fillna(0, inplace=True)
    
    # 计算库存周转率（月平均销量/现有库存）
    # 避免除以零
    efficiency_data['库存周转率'] = np.where(
        efficiency_data['现有库存'] > 0,
        efficiency_data['月平均销量'] / efficiency_data['现有库存'],
        0
    )
    
    # 计算库存覆盖天数（现有库存/(月平均销量/30)）
    # 避免除以零
    efficiency_data['库存覆盖天数'] = np.where(
        efficiency_data['月平均销量'] > 0,
        efficiency_data['现有库存'] / (efficiency_data['月平均销量'] / 30),
        float('inf')  # 如果没有销售，则覆盖天数为无穷大
    )
    
    # 添加产品代码到库存效率数据
    product_names = sales_data[['产品代码', '产品名称', '产品简称']].drop_duplicates()
    efficiency_data = pd.merge(
        efficiency_data,
        product_names,
        on='产品代码',
        how='left'
    )
    
    return efficiency_data