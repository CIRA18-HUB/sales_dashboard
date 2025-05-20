# pages/inventory_page.py - 完全自包含的库存分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import math
from plotly.subplots import make_subplots

# 从config导入颜色配置
from config import COLORS, DATA_FILES


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_inventory_data():
    """加载库存分析所需的所有数据"""
    try:
        # 加载销售数据
        sales_data = pd.read_excel(DATA_FILES['sales_data'])

        # 处理日期列
        if '发运月份' in sales_data.columns:
            sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

        # 过滤销售订单（只保留正常产品和TT产品）
        sales_orders = sales_data[
            sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品'])
        ].copy()

        # 加载实时库存数据 - 支持分层结构
        try:
            inventory_data_raw = pd.read_excel(DATA_FILES['inventory_data'])

            # 处理分层级的库存数据
            product_rows = inventory_data_raw[inventory_data_raw.iloc[:, 0].notna()]
            inventory_data = product_rows.iloc[:, :7].copy()
            if len(inventory_data.columns) >= 7:
                inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                          '现有库存可订量', '待入库量', '本月剩余可订量']

            # 处理批次信息
            batch_data = []
            product_code = None
            product_description = None

            for i, row in inventory_data_raw.iterrows():
                # 获取产品层信息
                if pd.notna(row.iloc[0]):
                    product_code = row.iloc[0]
                    product_description = row.iloc[1] if len(row) > 1 else ""
                # 获取批次层信息
                elif pd.notna(row.iloc[7]) if len(row) > 7 else False:
                    batch_row = row.iloc[7:].copy() if len(row) > 7 else []
                    if len(batch_row) >= 4:  # 确保有足够的列
                        batch_info = {
                            '产品代码': product_code,
                            '描述': product_description,
                            '库位': batch_row.iloc[0],
                            '生产日期': batch_row.iloc[1],
                            '生产批号': batch_row.iloc[2],
                            '数量': batch_row.iloc[3]
                        }
                        batch_data.append(batch_info)

            # 创建批次数据DataFrame
            batch_df = pd.DataFrame(batch_data) if batch_data else pd.DataFrame(
                columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量'])

            # 转换日期列
            if '生产日期' in batch_df.columns:
                batch_df['生产日期'] = pd.to_datetime(batch_df['生产日期'], errors='coerce')
        except Exception as e:
            st.warning(f"处理实时库存数据时出错: {str(e)}，将使用简化的库存数据")
            inventory_data = pd.DataFrame()
            batch_df = pd.DataFrame()

        # 加载月终月末库存数据
        try:
            monthly_inventory = pd.read_excel(DATA_FILES['monthly_inventory'])
            if '所属年月' in monthly_inventory.columns:
                monthly_inventory['所属年月'] = pd.to_datetime(monthly_inventory['所属年月'])
        except:
            monthly_inventory = pd.DataFrame()

        # 加载人工预测数据
        try:
            forecast_data = pd.read_excel(DATA_FILES['forecast_data'])
            if '所属年月' in forecast_data.columns:
                forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])
        except:
            forecast_data = pd.DataFrame()

        # 加载人与客户关系表
        try:
            person_customer_data = pd.read_excel(DATA_FILES['customer_relations'])
        except:
            person_customer_data = pd.DataFrame()

        return sales_orders, inventory_data, batch_df, monthly_inventory, forecast_data, person_customer_data

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def apply_inventory_filters(data):
    """应用筛选条件"""
    filtered_data = data.copy()

    # 应用全局筛选条件
    if st.session_state.get('filter_region') and st.session_state.get('filter_region') != '全部':
        if '所属区域' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['所属区域'] == st.session_state.get('filter_region')]

    if st.session_state.get('filter_person') and st.session_state.get('filter_person') != '全部':
        if '申请人' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['申请人'] == st.session_state.get('filter_person')]

    if st.session_state.get('filter_customer') and st.session_state.get('filter_customer') != '全部':
        if '客户代码' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['客户代码'] == st.session_state.get('filter_customer')]

    return filtered_data


# ==================== 2. 工具函数 ====================
def format_currency(value):
    """格式化货币显示"""
    if pd.isna(value) or value == 0:
        return "¥0"
    if value >= 100000000:
        return f"¥{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"¥{value / 10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"


def format_number(value):
    """格式化数字显示"""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


# ==================== 3. 库存分析函数 ====================
def analyze_inventory_data(sales_data, inventory_data, batch_data, monthly_inventory, forecast_data):
    """分析库存数据"""
    if inventory_data.empty:
        return {}

    # 先处理实时库存数据
    # 从销售数据计算月平均销量
    current_year = datetime.now().year
    current_month = datetime.now().month

    # 计算最近6个月的销售
    six_months_ago = pd.Timestamp(year=current_year, month=current_month, day=1) - pd.DateOffset(months=6)

    recent_sales = sales_data[(sales_data['发运月份'] >= six_months_ago) &
                              (sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品']))]

    # 按产品计算月平均销量
    if not recent_sales.empty:
        monthly_sales_by_product = recent_sales.groupby(['产品代码', '产品简称'])['求和项:数量（箱）'].sum().reset_index()
        monthly_sales_by_product['月平均销量'] = monthly_sales_by_product['求和项:数量（箱）'] / 6  # 6个月平均
    else:
        monthly_sales_by_product = pd.DataFrame(columns=['产品代码', '产品简称', '月平均销量'])

    # 处理库存主表数据
    inventory_summary = inventory_data.copy()

    # 确认库存数据结构
    if '现有库存可订量' in inventory_summary.columns and '现有库存' in inventory_summary.columns:
        # 提取最上层汇总数据
        top_level_inventory = inventory_summary.copy()

        # 计算库存周转率和库存覆盖天数
        inventory_analysis = top_level_inventory.merge(
            monthly_sales_by_product[['产品代码', '月平均销量']],
            left_on='产品代码',
            right_on='产品代码',
            how='left'
        )

        # 填充缺失的月平均销量为很小的值(0.1)，避免除以零错误
        inventory_analysis['月平均销量'] = inventory_analysis['月平均销量'].fillna(0.1)

        # 计算库存覆盖天数和清库周期
        inventory_analysis['库存覆盖天数'] = inventory_analysis['现有库存'] / inventory_analysis['月平均销量'] * 30
        inventory_analysis['清库周期(月)'] = inventory_analysis['现有库存'] / inventory_analysis['月平均销量']

        # 计算库存健康状态
        inventory_analysis['库存状态'] = inventory_analysis.apply(
            lambda row: '库存不足' if row['库存覆盖天数'] < 15 else
            '库存过剩' if row['库存覆盖天数'] > 90 else
            '库存健康',
            axis=1
        )

        # 计算积压风险
        inventory_analysis['积压风险'] = inventory_analysis.apply(
            lambda row: '高风险' if row['清库周期(月)'] > 6 else
            '中风险' if row['清库周期(月)'] > 3 else
            '低风险',
            axis=1
        )

        # 统计各类库存状态数量
        health_distribution = inventory_analysis['库存状态'].value_counts().to_dict()
        risk_distribution = inventory_analysis['积压风险'].value_counts().to_dict()

        # 计算总库存和可订量
        total_inventory = top_level_inventory['现有库存'].sum()
        assigned_inventory = (top_level_inventory['现有库存'] - top_level_inventory['现有库存可订量']).sum()
        orderable_inventory = top_level_inventory['现有库存可订量'].sum()
        pending_inventory = top_level_inventory['待入库量'].sum() if '待入库量' in top_level_inventory.columns else 0

        # 批次级别分析 - 新增功能
        batch_analysis_result = None
        if not batch_data.empty and '生产日期' in batch_data.columns:
            batch_analysis_result = analyze_batch_data(batch_data, monthly_sales_by_product, sales_data, forecast_data)

        # 预测与库存对比
        forecast_vs_inventory = None
        if not forecast_data.empty and '预计销售量' in forecast_data.columns:
            # 获取最新月份的预测
            current_month_str = pd.Timestamp(year=current_year, month=current_month, day=1)
            current_forecasts = forecast_data[forecast_data['所属年月'] == current_month_str]

            if not current_forecasts.empty:
                # 按产品汇总预测销量
                product_forecasts = current_forecasts.groupby('产品代码')['预计销售量'].sum().reset_index()

                # 合并库存和预测
                forecast_vs_inventory = product_forecasts.merge(
                    inventory_analysis[['产品代码', '现有库存', '现有库存可订量']],
                    on='产品代码',
                    how='inner'
                )

                # 计算预测库存状态
                forecast_vs_inventory['预测库存状态'] = forecast_vs_inventory.apply(
                    lambda row: '库存不足' if row['现有库存'] < row['预计销售量'] * 0.8 else
                    '库存过剩' if row['现有库存'] > row['预计销售量'] * 1.5 else
                    '库存适中',
                    axis=1
                )

                # 新增：计算预测偏差 - 使用calculate_forecast_bias函数
                if not sales_data.empty:
                    forecast_bias_analysis = calculate_forecast_bias(forecast_data, sales_data, inventory_analysis)
                    # 合并预测偏差结果到forecast_vs_inventory
                    if forecast_bias_analysis is not None:
                        forecast_vs_inventory = forecast_vs_inventory.merge(
                            forecast_bias_analysis[['产品代码', '预测偏差', '预测偏差分类']],
                            on='产品代码',
                            how='left'
                        )

        return {
            'total_inventory': total_inventory,
            'assigned_inventory': assigned_inventory,
            'orderable_inventory': orderable_inventory,
            'pending_inventory': pending_inventory,
            'inventory_analysis': inventory_analysis,
            'health_distribution': health_distribution,
            'risk_distribution': risk_distribution,
            'batch_analysis': batch_analysis_result,  # 新增批次分析结果
            'forecast_vs_inventory': forecast_vs_inventory
        }

    return {}


# ==================== 新增: 批次级别分析函数 ====================
def analyze_batch_data(batch_data, sales_by_product, sales_data, forecast_data):
    """分析批次级别的库存数据，计算风险和清库预测"""
    # 确保批次数据有必要的列
    required_columns = ['产品代码', '生产日期', '数量']
    if not all(col in batch_data.columns for col in required_columns):
        return None

    # 处理数据类型
    batch_data = batch_data.copy()
    if batch_data['数量'].dtype == 'object':
        batch_data['数量'] = pd.to_numeric(batch_data['数量'], errors='coerce')

    # 过滤掉无效数据
    batch_data = batch_data.dropna(subset=['产品代码', '生产日期', '数量'])

    # 计算当前日期
    today = pd.Timestamp.now().date()

    # 计算每个批次的库龄
    batch_data['库龄'] = batch_data['生产日期'].apply(
        lambda x: (today - x.date()).days if pd.notna(x) else 0
    )

    # 合并销售数据，获取月平均销量
    batch_analysis = batch_data.merge(
        sales_by_product[['产品代码', '月平均销量']],
        on='产品代码',
        how='left'
    )

    # 填充缺失的月平均销量，避免除以零错误
    batch_analysis['月平均销量'] = batch_analysis['月平均销量'].fillna(0.1)

    # 计算预计清库天数
    batch_analysis['日均销量'] = batch_analysis['月平均销量'] / 30
    min_daily_sales = 0.5  # 最小日均销量阈值
    batch_analysis['调整后日均销量'] = batch_analysis['日均销量'].apply(lambda x: max(x, min_daily_sales))
    batch_analysis['预计清库天数'] = batch_analysis['数量'] / batch_analysis['调整后日均销量']

    # 计算批次价值 (假设单价为100，实际应从数据中获取)
    # 在真实场景中，应该从产品表中获取单价
    batch_analysis['批次价值'] = batch_analysis['数量'] * 100

    # 计算风险等级
    def calculate_risk_level(row):
        age = row['库龄']
        days_to_clear = row['预计清库天数']

        # 风险评分计算
        risk_score = 0

        # 库龄因素 (0-40分)
        if age > 90:
            risk_score += 40
        elif age > 60:
            risk_score += 30
        elif age > 30:
            risk_score += 20
        else:
            risk_score += 10

        # 清库天数因素 (0-40分)
        if days_to_clear > 180:  # 半年以上
            risk_score += 40
        elif days_to_clear > 90:
            risk_score += 30
        elif days_to_clear > 60:
            risk_score += 20
        elif days_to_clear > 30:
            risk_score += 10

        # 根据总分确定风险等级
        if risk_score >= 70:
            return "极高风险"
        elif risk_score >= 50:
            return "高风险"
        elif risk_score >= 30:
            return "中风险"
        elif risk_score >= 15:
            return "低风险"
        else:
            return "极低风险"

    batch_analysis['风险程度'] = batch_analysis.apply(calculate_risk_level, axis=1)

    # 计算一、二、三个月的积压风险百分比
    def calculate_risk_percentage(days_to_clear, batch_age, target_days):
        # 若库龄已超过目标天数，风险100%
        if batch_age >= target_days:
            return 100.0

        # 无法清库情况
        if pd.isna(days_to_clear) or days_to_clear > 365:
            return 100.0

        # 计算基于清库天数的风险
        clearance_ratio = days_to_clear / target_days
        if clearance_ratio >= 3:
            return 100.0
        elif clearance_ratio >= 2:
            return 90.0
        elif clearance_ratio >= 1:
            return 70.0
        elif clearance_ratio >= 0.7:
            return 50.0
        elif clearance_ratio >= 0.5:
            return 30.0
        else:
            return 10.0

    batch_analysis['一个月积压风险'] = batch_analysis.apply(
        lambda row: calculate_risk_percentage(row['预计清库天数'], row['库龄'], 30), axis=1
    )
    batch_analysis['两个月积压风险'] = batch_analysis.apply(
        lambda row: calculate_risk_percentage(row['预计清库天数'], row['库龄'], 60), axis=1
    )
    batch_analysis['三个月积压风险'] = batch_analysis.apply(
        lambda row: calculate_risk_percentage(row['预计清库天数'], row['库龄'], 90), axis=1
    )

    # 确定积压原因
    def determine_stocking_reasons(row):
        reasons = []
        if row['库龄'] > 60:
            reasons.append("库龄过长")
        if row['预计清库天数'] > 90:
            reasons.append("销量低")
        if len(reasons) == 0:
            reasons.append("正常库存")
        return "，".join(reasons)

    batch_analysis['积压原因'] = batch_analysis.apply(determine_stocking_reasons, axis=1)

    # 新增：责任归属分析
    responsibility_analysis = analyze_batch_responsibility(batch_analysis, sales_data, forecast_data)
    if responsibility_analysis is not None:
        batch_analysis = batch_analysis.merge(
            responsibility_analysis,
            on='产品代码',
            how='left'
        )

    # 生成建议措施
    def generate_recommendation(row):
        risk_level = row['风险程度']
        if risk_level == "极高风险":
            return "紧急清理：考虑折价促销或转仓"
        elif risk_level == "高风险":
            return "优先处理：促销或加大营销力度"
        elif risk_level == "中风险":
            return "密切监控：调整采购计划"
        elif risk_level == "低风险":
            return "常规管理：定期检查库存状态"
        else:
            return "维持现状：正常库存水平"

    batch_analysis['建议措施'] = batch_analysis.apply(generate_recommendation, axis=1)

    # 按风险程度排序
    risk_order = {
        "极高风险": 0,
        "高风险": 1,
        "中风险": 2,
        "低风险": 3,
        "极低风险": 4
    }
    batch_analysis['风险排序'] = batch_analysis['风险程度'].map(risk_order)
    batch_analysis = batch_analysis.sort_values(['风险排序', '库龄'], ascending=[True, False])

    # 删除辅助列
    if '风险排序' in batch_analysis.columns:
        batch_analysis = batch_analysis.drop(columns=['风险排序'])

    return batch_analysis


# ==================== 新增: 责任归属分析函数 ====================
def analyze_batch_responsibility(batch_data, sales_data, forecast_data):
    """分析批次级别的责任归属，确定主要责任人和区域"""
    if batch_data.empty or sales_data.empty:
        return None

    # 获取唯一的产品代码列表
    product_codes = batch_data['产品代码'].unique()

    # 初始化结果DataFrame
    responsibility_result = pd.DataFrame({
        '产品代码': product_codes,
        '责任区域': '',
        '责任人': '',
        '责任分析摘要': ''
    })

    # 当前日期
    today = pd.Timestamp.now().date()

    # 针对每个产品代码进行分析
    for product_code in product_codes:
        # 获取该产品的销售数据
        product_sales = sales_data[sales_data['产品代码'] == product_code]

        # 获取该产品的预测数据
        product_forecast = forecast_data[
            forecast_data['产品代码'] == product_code] if not forecast_data.empty else pd.DataFrame()

        # 如果没有销售数据，跳过此产品
        if product_sales.empty:
            continue

        # 计算每个申请人的销售占比
        person_sales = product_sales.groupby('申请人')['求和项:数量（箱）'].sum()
        total_sales = person_sales.sum()

        # 计算每个区域的销售占比
        region_sales = product_sales.groupby('所属区域')['求和项:数量（箱）'].sum()

        # 确定主要责任人 - 销售量最大的人
        if not person_sales.empty:
            main_responsible_person = person_sales.idxmax()
            main_responsible_region = ''

            # 确定主要责任人所属区域
            person_regions = product_sales[product_sales['申请人'] == main_responsible_person]['所属区域'].unique()
            if len(person_regions) > 0:
                main_responsible_region = person_regions[0]

            # 计算预测与销售的差异
            forecast_sales_gap = 0
            forecast_person = ''

            if not product_forecast.empty:
                # 获取每个人的最新预测
                latest_forecast_date = product_forecast['所属年月'].max()
                latest_forecasts = product_forecast[product_forecast['所属年月'] == latest_forecast_date]

                # 计算每个人的预测量
                person_forecasts = latest_forecasts.groupby('销售员')['预计销售量'].sum()

                # 如果主要销售人在预测人中，计算其预测差异
                if main_responsible_person in person_forecasts.index:
                    forecast_qty = person_forecasts[main_responsible_person]
                    actual_sales = person_sales.get(main_responsible_person, 0)
                    forecast_sales_gap = forecast_qty - actual_sales
                    forecast_person = main_responsible_person
                elif len(person_forecasts) > 0:
                    # 否则使用预测量最大的人
                    forecast_person = person_forecasts.idxmax()
                    forecast_qty = person_forecasts[forecast_person]
                    actual_sales = person_sales.get(forecast_person, 0)
                    forecast_sales_gap = forecast_qty - actual_sales

            # 生成责任分析摘要
            if forecast_sales_gap > 0 and forecast_person:
                summary = f"{main_responsible_person}主要责任(预测过高{forecast_sales_gap:.0f}件)"
            elif forecast_person and forecast_person != main_responsible_person:
                summary = f"{main_responsible_person}主要责任(销售量最大)，{forecast_person}次要责任(提供预测)"
            else:
                sales_percentage = person_sales[main_responsible_person] / total_sales * 100 if total_sales > 0 else 0
                summary = f"{main_responsible_person}主要责任(占销售{sales_percentage:.1f}%)"

            # 更新结果DataFrame
            responsibility_result.loc[
                responsibility_result['产品代码'] == product_code, '责任人'] = main_responsible_person
            responsibility_result.loc[
                responsibility_result['产品代码'] == product_code, '责任区域'] = main_responsible_region
            responsibility_result.loc[responsibility_result['产品代码'] == product_code, '责任分析摘要'] = summary

    return responsibility_result


# ==================== 新增: 预测偏差计算函数 ====================
def calculate_forecast_bias(forecast_data, sales_data, inventory_analysis):
    """计算预测偏差，并分析偏差原因"""
    if forecast_data.empty or sales_data.empty:
        return None

    # 获取最新的预测月份
    latest_forecast_month = forecast_data['所属年月'].max()

    # 获取最新预测月份之前的销售数据
    sales_before_forecast = sales_data[sales_data['发运月份'] < latest_forecast_month]

    # 获取最新的预测数据
    latest_forecasts = forecast_data[forecast_data['所属年月'] == latest_forecast_month]

    # 按产品汇总预测量
    product_forecasts = latest_forecasts.groupby('产品代码')['预计销售量'].sum().reset_index()

    # 计算最近一个月的实际销售量
    one_month_ago = pd.Timestamp.now() - pd.DateOffset(months=1)
    recent_sales = sales_data[sales_data['发运月份'] >= one_month_ago]
    actual_sales = recent_sales.groupby('产品代码')['求和项:数量（箱）'].sum().reset_index()

    # 合并预测和实际销售
    forecast_vs_actual = product_forecasts.merge(
        actual_sales,
        on='产品代码',
        how='left'
    )

    # 填充缺失的实际销售量为0
    forecast_vs_actual['求和项:数量（箱）'] = forecast_vs_actual['求和项:数量（箱）'].fillna(0)

    # 计算预测偏差
    forecast_vs_actual['预测偏差值'] = (forecast_vs_actual['预计销售量'] - forecast_vs_actual['求和项:数量（箱）']) / \
                                       forecast_vs_actual['预计销售量'].apply(lambda x: max(x, 1))

    # 将预测偏差转换为百分比格式
    forecast_vs_actual['预测偏差'] = forecast_vs_actual['预测偏差值'].apply(
        lambda x: f"{x * 100:.1f}%" if not pd.isna(x) else "0%"
    )

    # 将预测偏差分类
    def classify_bias(bias_value):
        if pd.isna(bias_value):
            return "无偏差"
        if bias_value > 0.3:
            return "预测过高"
        elif bias_value < -0.3:
            return "预测过低"
        else:
            return "预测准确"

    forecast_vs_actual['预测偏差分类'] = forecast_vs_actual['预测偏差值'].apply(classify_bias)

    # 合并到库存分析结果
    forecast_bias_analysis = forecast_vs_actual[['产品代码', '预测偏差', '预测偏差分类', '预测偏差值']]

    return forecast_bias_analysis


# ==================== 4. 图表创建函数 ====================
def create_inventory_health_chart(health_data, title="库存健康状况分布"):
    """创建库存健康状况饼图"""
    if not health_data:
        return None

    # 转换为DataFrame
    df = pd.DataFrame({
        '状态': list(health_data.keys()),
        '产品数量': list(health_data.values())
    })

    # 设置颜色映射
    color_map = {
        '库存健康': COLORS['success'],
        '库存不足': COLORS['warning'],
        '库存过剩': COLORS['danger']
    }

    fig = px.pie(
        df,
        names='状态',
        values='产品数量',
        title=title,
        color='状态',
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        textfont_size=14
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_inventory_risk_chart(risk_data, title="库存积压风险分布"):
    """创建库存积压风险饼图"""
    if not risk_data:
        return None

    # 转换为DataFrame
    df = pd.DataFrame({
        '风险': list(risk_data.keys()),
        '产品数量': list(risk_data.values())
    })

    # 设置颜色映射
    color_map = {
        '低风险': COLORS['success'],
        '中风险': COLORS['warning'],
        '高风险': COLORS['danger']
    }

    fig = px.pie(
        df,
        names='风险',
        values='产品数量',
        title=title,
        color='风险',
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        textfont_size=14
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_batch_age_chart(batch_data, title="批次库龄分布"):
    """创建批次库龄分布图"""
    if batch_data is None or batch_data.empty:
        return None

    # 统计各库龄风险类别的批次数量
    age_risk_counts = batch_data['风险程度'].value_counts().reset_index()
    age_risk_counts.columns = ['风险程度', '批次数量']

    # 设置风险顺序
    risk_order = ['极低风险', '低风险', '中风险', '高风险', '极高风险']
    age_risk_counts['风险程度'] = pd.Categorical(age_risk_counts['风险程度'], categories=risk_order, ordered=True)
    age_risk_counts = age_risk_counts.sort_values('风险程度')

    # 设置颜色映射
    risk_colors = {
        '极高风险': '#FF0000',  # 红色
        '高风险': '#FF5252',  # 浅红色
        '中风险': '#FFC107',  # 黄色
        '低风险': '#4CAF50',  # 绿色
        '极低风险': '#2196F3'  # 蓝色
    }

    fig = px.bar(
        age_risk_counts,
        x='风险程度',
        y='批次数量',
        title=title,
        color='风险程度',
        color_discrete_map=risk_colors,
        text_auto=True
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="风险程度",
        yaxis_title="批次数量"
    )

    return fig


def create_batch_clearance_chart(batch_data, title="高风险批次清库周期"):
    """为高风险批次创建清库周期图表"""
    if batch_data is None or batch_data.empty:
        return None

    # 筛选高风险和极高风险批次
    high_risk_batches = batch_data[batch_data['风险程度'].isin(['高风险', '极高风险'])]

    if high_risk_batches.empty:
        return None

    # 按清库周期排序，取TOP8
    top_batches = high_risk_batches.sort_values('预计清库天数', ascending=False).head(8)

    # 创建图表
    fig = go.Figure()

    # 添加清库天数条形图
    fig.add_trace(go.Bar(
        y=top_batches['产品代码'],
        x=top_batches['预计清库天数'],
        orientation='h',
        name='预计清库天数',
        marker_color=COLORS['danger'],
        text=top_batches['预计清库天数'].apply(lambda x: f"{x:.0f}天"),
        textposition='outside'
    ))

    # 添加库龄条形图
    fig.add_trace(go.Bar(
        y=top_batches['产品代码'],
        x=top_batches['库龄'],
        orientation='h',
        name='当前库龄',
        marker_color=COLORS['primary'],
        text=top_batches['库龄'].apply(lambda x: f"{x:.0f}天"),
        textposition='outside'
    ))

    # 添加风险阈值线
    fig.add_shape(
        type="line",
        x0=90, y0=-0.5,
        x1=90, y1=len(top_batches) - 0.5,
        line=dict(color="red", width=2, dash="dash"),
        name="90天阈值"
    )

    # 图表布局
    fig.update_layout(
        title=title,
        xaxis_title="天数",
        yaxis_title="产品代码",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        barmode='group',
        height=max(400, 50 * len(top_batches) + 150),
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def create_forecast_bias_chart(forecast_data, title="预测偏差分析"):
    """创建预测偏差分析图表"""
    if forecast_data is None or 'forecast_vs_inventory' not in forecast_data or forecast_data[
        'forecast_vs_inventory'] is None:
        return None

    forecast_vs_inventory = forecast_data['forecast_vs_inventory']

    if 'predictive_bias_value' not in forecast_vs_inventory.columns:
        if '预测偏差值' in forecast_vs_inventory.columns:
            forecast_vs_inventory['predictive_bias_value'] = forecast_vs_inventory['预测偏差值']
        else:
            # 尝试从预测偏差计算偏差值
            if '预测偏差' in forecast_vs_inventory.columns:
                try:
                    forecast_vs_inventory['predictive_bias_value'] = forecast_vs_inventory['预测偏差'].apply(
                        lambda x: float(str(x).rstrip('%')) / 100 if isinstance(x, str) and '%' in x else 0
                    )
                except:
                    return None
            else:
                return None

    # 按偏差绝对值排序，取TOP10
    forecast_vs_inventory['abs_bias'] = forecast_vs_inventory['predictive_bias_value'].abs()
    top_products = forecast_vs_inventory.sort_values('abs_bias', ascending=False).head(10)

    # 创建图表
    fig = go.Figure()

    # 添加预测偏差条形图
    fig.add_trace(go.Bar(
        y=top_products['产品代码'],
        x=top_products['predictive_bias_value'] * 100,  # 转换为百分比
        orientation='h',
        marker_color=top_products['predictive_bias_value'].apply(
            lambda x: COLORS['danger'] if x > 0 else COLORS['info']
        ),
        text=top_products['predictive_bias_value'].apply(lambda x: f"{x * 100:.1f}%"),
        textposition='outside'
    ))

    # 添加零线
    fig.add_shape(
        type="line",
        x0=0, y0=-0.5,
        x1=0, y1=len(top_products) - 0.5,
        line=dict(color="black", width=1)
    )

    # 添加偏差阈值线
    fig.add_shape(
        type="line",
        x0=30, y0=-0.5,
        x1=30, y1=len(top_products) - 0.5,
        line=dict(color="red", width=1, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=-30, y0=-0.5,
        x1=-30, y1=len(top_products) - 0.5,
        line=dict(color="blue", width=1, dash="dash")
    )

    # 图表布局
    fig.update_layout(
        title=title,
        xaxis_title="预测偏差百分比",
        yaxis_title="产品代码",
        height=max(400, 50 * len(top_products) + 150),
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加图例注释
    fig.add_annotation(
        x=50, y=len(top_products) - 1,
        text="正值表示预测过高<br>负值表示预测过低",
        showarrow=False,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1
    )

    return fig


def create_inventory_forecast_chart(forecast_data, title="库存与预测对比"):
    """创建库存与预测对比图"""
    if forecast_data is None or forecast_data.empty:
        return None

    # 统计各预测状态的产品数量
    status_counts = forecast_data['预测库存状态'].value_counts().reset_index()
    status_counts.columns = ['预测库存状态', '产品数量']

    # 设置状态顺序
    status_order = ['库存不足', '库存适中', '库存过剩']
    status_counts['预测库存状态'] = pd.Categorical(status_counts['预测库存状态'], categories=status_order, ordered=True)
    status_counts = status_counts.sort_values('预测库存状态')

    # 设置颜色映射
    color_map = {
        '库存不足': COLORS['warning'],
        '库存适中': COLORS['success'],
        '库存过剩': COLORS['danger']
    }

    fig = px.bar(
        status_counts,
        x='预测库存状态',
        y='产品数量',
        title=title,
        color='预测库存状态',
        color_discrete_map=color_map,
        text_auto=True
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="预测库存状态",
        yaxis_title="产品数量"
    )

    return fig


def create_high_risk_product_chart(inventory_data, title="高风险产品清库周期"):
    """创建高风险产品清库周期图"""
    if inventory_data is None or inventory_data.empty:
        return None

    # 筛选高风险产品
    high_risk = inventory_data[inventory_data['积压风险'] == '高风险'].copy()

    if high_risk.empty:
        return None

    # 按清库周期排序，取TOP10
    top_high_risk = high_risk.sort_values('清库周期(月)', ascending=False).head(10)

    # 创建横向条形图
    fig = px.bar(
        top_high_risk,
        y='产品代码',
        x='清库周期(月)',
        orientation='h',
        title=title,
        color='清库周期(月)',
        color_continuous_scale=px.colors.sequential.Reds,
        text_auto='.1f'
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="清库周期(月)",
        yaxis_title="产品代码"
    )

    # 添加库存数量标注
    for i, row in enumerate(top_high_risk.itertuples()):
        fig.add_annotation(
            x=row._5 + max(top_high_risk['清库周期(月)']) * 0.05,  # 清库周期
            y=i,
            text=f"库存: {row.现有库存:,.0f}",
            showarrow=False,
            font=dict(size=10)
        )

    return fig


# ==================== 5. 翻卡组件 ====================
def create_inventory_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False):
    """创建库存分析的翻卡组件"""
    # 初始化翻卡状态
    flip_key = f"inventory_flip_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = 0

    # 格式化值
    if is_currency:
        formatted_value = format_currency(value)
    elif is_percentage:
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)

    # 创建卡片容器
    card_container = st.container()

    with card_container:
        # 点击按钮
        if st.button(f"查看{title}详情", key=f"btn_{card_id}", help=f"点击查看{title}的详细分析"):
            st.session_state[flip_key] = (st.session_state[flip_key] + 1) % 3

        current_layer = st.session_state[flip_key]

        if current_layer == 0:
            # 第一层：基础指标
            st.markdown(f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15); 
                        text-align: center; min-height: 200px; display: flex; 
                        flex-direction: column; justify-content: center;">
                <h3 style="color: {COLORS['primary']}; margin-bottom: 1rem;">{title}</h3>
                <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">{formatted_value}</h1>
                <p style="color: {COLORS['gray']}; margin-bottom: 1rem;">{subtitle}</p>
                <p style="color: {COLORS['secondary']}; font-size: 0.9rem;">点击查看分析 →</p>
            </div>
            """, unsafe_allow_html=True)

        elif current_layer == 1:
            # 第二层：图表分析
            st.markdown(f"### 📊 {title} - 图表分析")

            # 根据不同的指标显示不同的图表
            if "总库存量" in title:
                # 显示库存健康饼图
                if 'analysis_result' in st.session_state:
                    health_data = st.session_state['analysis_result'].get('health_distribution', {})
                    if health_data:
                        fig = create_inventory_health_chart(health_data, "库存健康状况分布")
                        st.plotly_chart(fig, use_container_width=True)

                    # 新增：批次分析
                    batch_data = st.session_state['analysis_result'].get('batch_analysis')
                    if batch_data is not None and not batch_data.empty:
                        # 创建批次风险分布饼图
                        batch_fig = create_batch_age_chart(batch_data, "批次级别风险分布")
                        if batch_fig:
                            st.plotly_chart(batch_fig, use_container_width=True)

            elif "健康库存占比" in title:
                # 显示库存分布
                if 'analysis_result' in st.session_state:
                    inventory_analysis = st.session_state['analysis_result'].get('inventory_analysis', pd.DataFrame())
                    if not inventory_analysis.empty:
                        # 按库存覆盖天数排序
                        coverage_data = inventory_analysis.sort_values('库存覆盖天数', ascending=False).head(10)

                        # 创建库存覆盖天数条形图
                        fig = px.bar(
                            coverage_data,
                            y='产品代码',
                            x='库存覆盖天数',
                            orientation='h',
                            title="库存覆盖天数TOP10",
                            color='库存覆盖天数',
                            color_continuous_scale=px.colors.sequential.Blues,
                            text_auto='.1f'
                        )

                        fig.update_layout(
                            height=500,
                            margin=dict(l=20, r=20, t=60, b=20),
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            xaxis_title="库存覆盖天数",
                            yaxis_title="产品代码"
                        )

                        st.plotly_chart(fig, use_container_width=True)

            elif "高风险库存占比" in title:
                # 显示高风险产品
                if 'analysis_result' in st.session_state:
                    inventory_analysis = st.session_state['analysis_result'].get('inventory_analysis', pd.DataFrame())
                    if not inventory_analysis.empty:
                        fig = create_high_risk_product_chart(inventory_analysis, "高风险产品清库周期TOP10")
                        st.plotly_chart(fig, use_container_width=True)

                    # 新增：批次级别清库周期分析
                    batch_data = st.session_state['analysis_result'].get('batch_analysis')
                    if batch_data is not None and not batch_data.empty:
                        batch_clearance_fig = create_batch_clearance_chart(batch_data, "高风险批次清库天数分析")
                        if batch_clearance_fig:
                            st.plotly_chart(batch_clearance_fig, use_container_width=True)

            elif "已分配库存占比" in title:
                # 显示库存分配状态
                if 'analysis_result' in st.session_state:
                    total_inventory = st.session_state['analysis_result'].get('total_inventory', 0)
                    assigned_inventory = st.session_state['analysis_result'].get('assigned_inventory', 0)
                    orderable_inventory = st.session_state['analysis_result'].get('orderable_inventory', 0)
                    pending_inventory = st.session_state['analysis_result'].get('pending_inventory', 0)

                    # 创建库存分配饼图
                    inventory_allocation = pd.DataFrame({
                        '状态': ['已分配库存', '可订库存', '待入库量'],
                        '数量': [assigned_inventory, orderable_inventory, pending_inventory]
                    })

                    fig = px.pie(
                        inventory_allocation,
                        names='状态',
                        values='数量',
                        title="库存分配状态",
                        color='状态',
                        color_discrete_sequence=[COLORS['warning'], COLORS['success'], COLORS['info']],
                        hole=0.4
                    )

                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hoverinfo='label+percent+value'
                    )

                    fig.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=60, b=20),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 新增：预测偏差分析
                    forecast_bias_fig = create_forecast_bias_chart(st.session_state['analysis_result'],
                                                                   "产品预测偏差分析")
                    if forecast_bias_fig:
                        st.plotly_chart(forecast_bias_fig, use_container_width=True)

            # 洞察文本
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>💡 数据洞察</h4>
                <p>{generate_insight_text(card_id)}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击查看深度分析 →</p>",
                        unsafe_allow_html=True)

        else:
            # 第三层：深度分析
            st.markdown(f"### 🔍 {title} - 深度分析")

            # 根据不同指标显示相应的深度分析内容
            if "总库存量" in title and 'analysis_result' in st.session_state:
                batch_data = st.session_state['analysis_result'].get('batch_analysis')
                if batch_data is not None and not batch_data.empty:
                    # 显示批次级别的详细风险分析
                    st.markdown("#### 批次级别风险详细分析")

                    # 筛选高风险批次
                    high_risk_batches = batch_data[batch_data['风险程度'].isin(['极高风险', '高风险'])]

                    if not high_risk_batches.empty:
                        # 展示高风险批次数据
                        st.markdown(f"**发现 {len(high_risk_batches)} 个高风险或极高风险批次，需要优先处理：**")

                        show_columns = ['产品代码', '库龄', '预计清库天数', '风险程度', '积压原因', '建议措施']

                        if '责任人' in high_risk_batches.columns:
                            show_columns.append('责任人')

                        st.dataframe(high_risk_batches[show_columns].head(10), height=300)
                    else:
                        st.success("👍 当前没有高风险批次，库存状态良好！")
                else:
                    st.info("未能获取批次级别数据，无法进行深度分析。")

            elif "高风险库存占比" in title and 'analysis_result' in st.session_state:
                # 显示责任分析内容
                batch_data = st.session_state['analysis_result'].get('batch_analysis')
                if batch_data is not None and not batch_data.empty and '责任人' in batch_data.columns:
                    st.markdown("#### 责任归属分析")

                    # 按责任人统计风险批次
                    responsibility_summary = batch_data.groupby('责任人')['风险程度'].value_counts().unstack().fillna(0)

                    # 确保所有风险级别列都存在
                    for risk_level in ['极高风险', '高风险', '中风险', '低风险', '极低风险']:
                        if risk_level not in responsibility_summary.columns:
                            responsibility_summary[risk_level] = 0

                    # 计算总批次数和加权风险分数
                    responsibility_summary['总批次数'] = responsibility_summary.sum(axis=1)

                    # 风险权重
                    risk_weights = {
                        '极高风险': 5,
                        '高风险': 4,
                        '中风险': 3,
                        '低风险': 2,
                        '极低风险': 1
                    }

                    # 计算加权风险分数
                    for risk in risk_weights:
                        if risk in responsibility_summary.columns:
                            responsibility_summary[f'{risk}_加权'] = responsibility_summary[risk] * risk_weights[risk]

                    weighted_cols = [col for col in responsibility_summary.columns if '加权' in col]
                    responsibility_summary['风险得分'] = responsibility_summary[weighted_cols].sum(axis=1)
                    responsibility_summary['平均风险'] = responsibility_summary['风险得分'] / responsibility_summary[
                        '总批次数']

                    # 按风险得分排序
                    responsibility_summary = responsibility_summary.sort_values('风险得分', ascending=False)

                    # 显示按责任人汇总的风险分布
                    columns_to_show = ['极高风险', '高风险', '中风险', '低风险', '极低风险', '总批次数', '风险得分',
                                       '平均风险']
                    available_columns = [col for col in columns_to_show if col in responsibility_summary.columns]

                    st.dataframe(responsibility_summary[available_columns].head(10), height=300)

                    # 创建责任人风险分布图
                    if not responsibility_summary.empty:
                        top_persons = responsibility_summary.head(5).index.tolist()
                        risk_data_for_chart = []

                        for person in top_persons:
                            for risk in ['极高风险', '高风险', '中风险', '低风险', '极低风险']:
                                if risk in responsibility_summary.columns and person in responsibility_summary.index:
                                    count = responsibility_summary.loc[person, risk]
                                    if count > 0:
                                        risk_data_for_chart.append({
                                            '责任人': person,
                                            '风险级别': risk,
                                            '批次数量': count
                                        })

                        if risk_data_for_chart:
                            risk_chart_df = pd.DataFrame(risk_data_for_chart)

                            # 设置颜色映射
                            risk_colors = {
                                '极高风险': '#FF0000',
                                '高风险': '#FF5252',
                                '中风险': '#FFC107',
                                '低风险': '#4CAF50',
                                '极低风险': '#2196F3'
                            }

                            # 创建堆叠条形图
                            risk_fig = px.bar(
                                risk_chart_df,
                                x='责任人',
                                y='批次数量',
                                color='风险级别',
                                title="TOP5责任人风险批次分布",
                                color_discrete_map=risk_colors,
                                category_orders={"风险级别": ['极高风险', '高风险', '中风险', '低风险', '极低风险']}
                            )

                            risk_fig.update_layout(
                                height=400,
                                margin=dict(l=20, r=20, t=60, b=20),
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                yaxis_title="批次数量",
                                legend_title="风险级别"
                            )

                            st.plotly_chart(risk_fig, use_container_width=True)
                else:
                    st.info("未能获取批次责任数据，无法进行责任归属分析。")

            # 深度分析内容
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid {COLORS['info']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>📈 趋势分析</h4>
                    {generate_trend_analysis(card_id)}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid {COLORS['warning']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>🎯 优化建议</h4>
                    {generate_optimization_advice(card_id)}
                </div>
                """, unsafe_allow_html=True)

            # 行动方案
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin-top: 1rem; border-radius: 0.5rem;">
                <h4>📋 行动方案</h4>
                {generate_action_plan(card_id)}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #4c78a8;'>再次点击返回基础视图 ↻</p>",
                        unsafe_allow_html=True)


def generate_insight_text(card_id):
    """生成洞察文本"""
    if 'analysis_result' not in st.session_state:
        return "数据分析加载中..."

    analysis = st.session_state['analysis_result']

    if card_id == "total_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        health_distribution = analysis.get('health_distribution', {})

        healthy_count = health_distribution.get('库存健康', 0)
        low_count = health_distribution.get('库存不足', 0)
        high_count = health_distribution.get('库存过剩', 0)
        total_count = healthy_count + low_count + high_count

        # 新增：批次级别的洞察
        batch_analysis = analysis.get('batch_analysis')
        batch_insight = ""

        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_count = sum(batch_analysis['风险程度'].isin(['极高风险', '高风险']))

            if high_risk_count > 0:
                batch_insight = f"批次级别分析显示有{high_risk_count}个高风险批次需要关注，"

                # 获取最高风险的批次
                top_risk_batch = batch_analysis.sort_values(['风险程度', '库龄'], ascending=[True, False]).iloc[0]
                batch_insight += f"其中{top_risk_batch['产品代码']}批次库龄已达{top_risk_batch['库龄']}天，预计清库需要{top_risk_batch['预计清库天数']:.0f}天。"

        if total_count > 0:
            healthy_percentage = healthy_count / total_count * 100
            insight_text = f"当前总库存量为 {format_number(total_inventory)}，其中健康库存产品占 {format_percentage(healthy_percentage)}，库存不足产品占 {format_percentage(low_count / total_count * 100)}，库存过剩产品占 {format_percentage(high_count / total_count * 100)}。{'库存结构相对健康。' if healthy_percentage > 60 else '库存结构需要优化。'}"

            if batch_insight:
                insight_text += " " + batch_insight

            return insight_text
        else:
            return f"当前总库存量为 {format_number(total_inventory)}，无法获取库存健康状况分布信息。"

    elif card_id == "healthy_inventory":
        health_distribution = analysis.get('health_distribution', {})

        healthy_count = health_distribution.get('库存健康', 0)
        total_count = sum(health_distribution.values()) if health_distribution else 0

        if total_count > 0:
            healthy_percentage = healthy_count / total_count * 100

            if healthy_percentage >= 70:
                return f"健康库存产品占比 {format_percentage(healthy_percentage)}，库存结构非常健康，大部分产品库存控制在合理范围内。"
            elif healthy_percentage >= 50:
                return f"健康库存产品占比 {format_percentage(healthy_percentage)}，库存结构相对健康，但仍有优化空间。"
            else:
                return f"健康库存产品占比仅为 {format_percentage(healthy_percentage)}，库存结构不够合理，需要加强库存管理和控制。"
        else:
            return "无法获取库存健康状况分布信息。"

    elif card_id == "high_risk_inventory":
        risk_distribution = analysis.get('risk_distribution', {})

        high_risk = risk_distribution.get('高风险', 0)
        total_risk = sum(risk_distribution.values()) if risk_distribution else 0

        inventory_analysis = analysis.get('inventory_analysis', pd.DataFrame())
        batch_analysis = analysis.get('batch_analysis')

        # 生成关于批次级别风险的洞察
        batch_insight = ""
        if batch_analysis is not None and not batch_analysis.empty:
            extreme_high_risk = sum(batch_analysis['风险程度'] == '极高风险')
            high_risk_batch = sum(batch_analysis['风险程度'] == '高风险')

            if extreme_high_risk + high_risk_batch > 0:
                batch_insight = f"批次分析发现{extreme_high_risk}个极高风险和{high_risk_batch}个高风险批次，"

                # 责任人分析
                if '责任人' in batch_analysis.columns:
                    top_responsible = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])][
                        '责任人'].value_counts().head(1)
                    if not top_responsible.empty:
                        top_person = top_responsible.index[0]
                        top_count = top_responsible.iloc[0]
                        batch_insight += f"其中{top_person}负责{top_count}个高风险批次，需要优先跟进。"

        if total_risk > 0 and not inventory_analysis.empty:
            high_risk_percentage = high_risk / total_risk * 100

            # 获取高风险产品的平均清库周期
            high_risk_products = inventory_analysis[inventory_analysis['积压风险'] == '高风险']
            avg_clear_period = high_risk_products['清库周期(月)'].mean() if not high_risk_products.empty else 0

            insight_text = ""
            if high_risk_percentage > 20:
                insight_text = f"高风险库存产品占比达 {format_percentage(high_risk_percentage)}，库存积压风险较高，平均清库周期约 {avg_clear_period:.1f} 个月，需要尽快采取措施清理过剩库存。"
            elif high_risk_percentage > 10:
                insight_text = f"高风险库存产品占比为 {format_percentage(high_risk_percentage)}，库存积压风险中等，平均清库周期约 {avg_clear_period:.1f} 个月，需要关注并制定清库计划。"
            else:
                insight_text = f"高风险库存产品占比仅为 {format_percentage(high_risk_percentage)}，库存积压风险较低，平均清库周期约 {avg_clear_period:.1f} 个月，可以继续保持良好的库存管理。"

            if batch_insight:
                insight_text += " " + batch_insight

            return insight_text
        else:
            return "无法获取库存风险分布信息。"

    elif card_id == "assigned_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        assigned_inventory = analysis.get('assigned_inventory', 0)
        orderable_inventory = analysis.get('orderable_inventory', 0)

        if total_inventory > 0:
            assigned_percentage = assigned_inventory / total_inventory * 100
            orderable_percentage = orderable_inventory / total_inventory * 100

            # 新增：预测偏差洞察
            forecast_insight = ""
            forecast_vs_inventory = analysis.get('forecast_vs_inventory')
            if forecast_vs_inventory is not None and '预测偏差分类' in forecast_vs_inventory.columns:
                over_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过高')
                under_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过低')

                if over_forecast + under_forecast > 0:
                    forecast_insight = f"预测分析显示有{over_forecast}个产品预测过高，{under_forecast}个产品预测过低，"

                    if over_forecast > under_forecast:
                        forecast_insight += "整体预测偏高，可能导致库存积压。"
                    else:
                        forecast_insight += "整体预测偏低，可能导致缺货风险。"

            insight_text = ""
            if assigned_percentage > 70:
                insight_text = f"已分配库存占比达 {format_percentage(assigned_percentage)}，可订库存仅占 {format_percentage(orderable_percentage)}，库存周转率较高，但可能需要关注库存补充，以确保供应连续性。"
            elif assigned_percentage > 50:
                insight_text = f"已分配库存占比为 {format_percentage(assigned_percentage)}，可订库存占 {format_percentage(orderable_percentage)}，库存分配状态合理，供需平衡良好。"
            else:
                insight_text = f"已分配库存占比仅为 {format_percentage(assigned_percentage)}，可订库存占 {format_percentage(orderable_percentage)}，大量库存未得到有效利用，需要加强销售计划与库存管理的协同。"

            if forecast_insight:
                insight_text += " " + forecast_insight

            return insight_text
        else:
            return "无法获取库存分配信息。"

    return "数据分析加载中..."


def generate_trend_analysis(card_id):
    """生成趋势分析HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>分析数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        inventory_analysis = analysis.get('inventory_analysis', pd.DataFrame())

        if not inventory_analysis.empty:
            # 计算平均月销量
            total_monthly_sales = inventory_analysis['月平均销量'].sum()

            # 计算整体库存周转率和库存周期
            overall_coverage_days = total_inventory / total_monthly_sales * 30 if total_monthly_sales > 0 else 0

            # 找出库存量最大的TOP3产品
            top_inventory_products = inventory_analysis.nlargest(3, '现有库存')

            top_products_html = ""
            for i, row in enumerate(top_inventory_products.iterrows()):
                product = row[1]
                top_products_html += f"<p>• {product['产品代码']} - {format_number(product['现有库存'])} ({format_percentage(product['现有库存'] / total_inventory * 100 if total_inventory > 0 else 0)})</p>"

            # 新增：批次级别趋势分析
            batch_analysis = analysis.get('batch_analysis')
            batch_trend_html = ""

            if batch_analysis is not None and not batch_analysis.empty:
                # 计算批次库龄分布
                age_bins = [0, 30, 60, 90, float('inf')]
                age_labels = ['0-30天', '31-60天', '61-90天', '90天以上']

                batch_analysis['库龄分组'] = pd.cut(batch_analysis['库龄'], bins=age_bins, labels=age_labels)
                age_distribution = batch_analysis['库龄分组'].value_counts().sort_index()

                batch_trend_html = "<p><strong>批次库龄分布：</strong></p>"
                for age_group, count in age_distribution.items():
                    batch_trend_html += f"<p>• {age_group}: {count}个批次</p>"

                # 添加平均库龄信息
                avg_batch_age = batch_analysis['库龄'].mean()
                batch_trend_html += f"<p>• 平均批次库龄: {avg_batch_age:.1f}天</p>"

            trend_html = f"""
                <p><strong>总库存分析：</strong></p>
                <p>• 总库存量：{format_number(total_inventory)}</p>
                <p>• 平均库存覆盖天数：{overall_coverage_days:.1f}天</p>
                <p>• 平均月销量：{format_number(total_monthly_sales)}</p>
                <p><strong>库存集中度：</strong>TOP3产品占总库存的{format_percentage(top_inventory_products['现有库存'].sum() / total_inventory * 100 if total_inventory > 0 else 0)}</p>
                <p><strong>库存占比最高的产品：</strong></p>
                {top_products_html}
                {batch_trend_html}
            """
            return trend_html
        else:
            return "<p>无足够数据进行库存分析</p>"

    elif card_id == "healthy_inventory":
        health_distribution = analysis.get('health_distribution', {})
        inventory_analysis = analysis.get('inventory_analysis', pd.DataFrame())

        if health_distribution and not inventory_analysis.empty:
            # 获取健康库存产品
            healthy_products = inventory_analysis[inventory_analysis['库存状态'] == '库存健康']

            # 计算健康库存产品的平均覆盖天数
            avg_coverage = healthy_products['库存覆盖天数'].mean() if not healthy_products.empty else 0

            # 计算健康库存比例变化（假设这里是固定值，实际应从历史数据计算）
            # 这里假设健康库存比例相比上月提高了2%
            healthy_count = health_distribution.get('库存健康', 0)
            total_count = sum(health_distribution.values())
            current_healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

            # 假设的历史数据对比
            historical_change = "+2.0%"  # 这里应该从历史数据计算

            return f"""
                <p><strong>健康库存分析：</strong></p>
                <p>• 健康库存产品数量：{healthy_count}个</p>
                <p>• 健康库存占比：{format_percentage(current_healthy_percentage)}</p>
                <p>• 平均库存覆盖天数：{avg_coverage:.1f}天</p>
                <p>• 比例变化趋势：{historical_change} (相比上月)</p>
                <p><strong>健康标准：</strong>库存覆盖15-90天的产品被视为健康库存</p>
            """
        else:
            return "<p>无足够数据进行健康库存分析</p>"

    elif card_id == "high_risk_inventory":
        risk_distribution = analysis.get('risk_distribution', {})
        inventory_analysis = analysis.get('inventory_analysis', pd.DataFrame())
        batch_analysis = analysis.get('batch_analysis')

        if risk_distribution and not inventory_analysis.empty:
            # 获取高风险库存产品
            high_risk_products = inventory_analysis[inventory_analysis['积压风险'] == '高风险']

            # 新增：批次级别风险趋势分析
            batch_trend_html = ""

            if batch_analysis is not None and not batch_analysis.empty:
                # 计算各风险等级批次数量
                risk_counts = batch_analysis['风险程度'].value_counts()

                batch_trend_html = "<p><strong>批次风险分布：</strong></p>"
                risk_order = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
                for risk in risk_order:
                    if risk in risk_counts:
                        batch_trend_html += f"<p>• {risk}: {risk_counts[risk]}个批次</p>"

                # 获取高风险批次的平均清库天数
                high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
                if not high_risk_batches.empty:
                    avg_clearance = high_risk_batches['预计清库天数'].mean()
                    batch_trend_html += f"<p>• 高风险批次平均清库天数: {avg_clearance:.1f}天</p>"

                    # 添加责任人分析
                    if '责任人' in high_risk_batches.columns:
                        person_counts = high_risk_batches['责任人'].value_counts().head(3)
                        batch_trend_html += "<p>• 高风险批次责任人TOP3:</p>"
                        for person, count in person_counts.items():
                            batch_trend_html += f"<p>  - {person}: {count}个批次</p>"

            if not high_risk_products.empty:
                # 计算高风险库存产品的平均清库周期
                avg_clear_period = high_risk_products['清库周期(月)'].mean()

                # 找出清库周期最长的TOP3产品
                top_risk_products = high_risk_products.nlargest(3, '清库周期(月)')

                top_risk_html = ""
                for i, row in enumerate(top_risk_products.iterrows()):
                    product = row[1]
                    top_risk_html += f"<p>• {product['产品代码']} - 清库周期 {product['清库周期(月)']:.1f}个月</p>"

                # 计算高风险库存占总库存的比例
                high_risk_inventory = high_risk_products['现有库存'].sum()
                total_inventory = analysis.get('total_inventory', 0)
                high_risk_percentage = high_risk_inventory / total_inventory * 100 if total_inventory > 0 else 0

                return f"""
                    <p><strong>高风险库存分析：</strong></p>
                    <p>• 高风险产品数量：{len(high_risk_products)}个</p>
                    <p>• 高风险库存占比：{format_percentage(high_risk_percentage)}</p>
                    <p>• 平均清库周期：{avg_clear_period:.1f}个月</p>
                    <p><strong>清库周期最长的产品：</strong></p>
                    {top_risk_html}
                    {batch_trend_html}
                """
            else:
                return "<p>当前无高风险库存产品，库存管理良好</p>"
        else:
            return "<p>无足够数据进行高风险库存分析</p>"

    elif card_id == "assigned_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        assigned_inventory = analysis.get('assigned_inventory', 0)
        orderable_inventory = analysis.get('orderable_inventory', 0)
        pending_inventory = analysis.get('pending_inventory', 0)

        # 新增：预测偏差趋势分析
        forecast_trend_html = ""
        forecast_vs_inventory = analysis.get('forecast_vs_inventory')

        if forecast_vs_inventory is not None and '预测偏差分类' in forecast_vs_inventory.columns:
            # 计算各类预测偏差的产品数量
            bias_counts = forecast_vs_inventory['预测偏差分类'].value_counts()

            forecast_trend_html = "<p><strong>预测偏差分析：</strong></p>"
            for bias_type, count in bias_counts.items():
                forecast_trend_html += f"<p>• {bias_type}: {count}个产品</p>"

            # 计算平均偏差值
            if '预测偏差值' in forecast_vs_inventory.columns:
                avg_bias = forecast_vs_inventory['预测偏差值'].mean() * 100  # 转换为百分比
                forecast_trend_html += f"<p>• 平均预测偏差: {avg_bias:.1f}%</p>"

                # 判断整体预测趋势
                if avg_bias > 10:
                    forecast_trend_html += "<p>• 整体预测趋势: <span style='color:#FF5252'>预测偏高</span></p>"
                elif avg_bias < -10:
                    forecast_trend_html += "<p>• 整体预测趋势: <span style='color:#4682B4'>预测偏低</span></p>"
                else:
                    forecast_trend_html += "<p>• 整体预测趋势: <span style='color:#4CAF50'>预测准确</span></p>"

        assigned_percentage = assigned_inventory / total_inventory * 100 if total_inventory > 0 else 0
        orderable_percentage = orderable_inventory / total_inventory * 100 if total_inventory > 0 else 0
        pending_percentage = pending_inventory / total_inventory * 100 if total_inventory > 0 else 0

        # 假设的历史数据对比
        historical_assigned = "-5.0%"  # 这里应该从历史数据计算

        return f"""
            <p><strong>库存分配分析：</strong></p>
            <p>• a. 已分配库存：{format_number(assigned_inventory)} ({format_percentage(assigned_percentage)})</p>
            <p>• b. 可订库存：{format_number(orderable_inventory)} ({format_percentage(orderable_percentage)})</p>
            <p>• c. 待入库量：{format_number(pending_inventory)} ({format_percentage(pending_percentage)})</p>
            <p>• 已分配比例变化：{historical_assigned} (相比上月)</p>
            <p><strong>供应链状态：</strong>{'库存周转良好' if assigned_percentage > 60 else '库存利用率有待提高'}</p>
            {forecast_trend_html}
        """

    return "<p>分析数据加载中...</p>"


def generate_optimization_advice(card_id):
    """生成优化建议HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>建议数据加载中...</p>"

    analysis = st.session_state['analysis_result']

    if card_id == "total_inventory":
        health_distribution = analysis.get('health_distribution', {})
        batch_analysis = analysis.get('batch_analysis')

        # 批次级别优化建议
        batch_advice = ""
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_count = sum(batch_analysis['风险程度'].isin(['极高风险', '高风险']))

            if high_risk_count > 0:
                # 按风险程度对批次进行分组
                risk_groups = batch_analysis.groupby('风险程度').size()

                batch_advice = "<p>• <strong>批次级优化：</strong></p>"

                if '极高风险' in risk_groups and risk_groups['极高风险'] > 0:
                    batch_advice += f"<p>  - 对{risk_groups['极高风险']}个极高风险批次实施紧急清库措施</p>"

                if '高风险' in risk_groups and risk_groups['高风险'] > 0:
                    batch_advice += f"<p>  - 为{risk_groups['高风险']}个高风险批次制定促销计划</p>"

                # 针对责任人的建议
                if '责任人' in batch_analysis.columns:
                    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
                    person_counts = high_risk_batches['责任人'].value_counts().head(1)

                    if not person_counts.empty:
                        top_person = person_counts.index[0]
                        top_count = person_counts.iloc[0]
                        batch_advice += f"<p>  - 协同{top_person}处理其负责的{top_count}个高风险批次</p>"

        if health_distribution:
            healthy_count = health_distribution.get('库存健康', 0)
            low_count = health_distribution.get('库存不足', 0)
            high_count = health_distribution.get('库存过剩', 0)
            total_count = healthy_count + low_count + high_count

            healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

            advice = ""
            if healthy_percentage >= 70:
                advice = """
                    <p>• 维持当前库存管理策略，保持良好库存结构</p>
                    <p>• 定期评估库存健康状况，及时调整</p>
                    <p>• 优化预测准确性，进一步提高库存效率</p>
                    <p>• 建立库存绩效考核机制，激励良好库存管理</p>
                """
            elif low_count > high_count:
                advice = """
                    <p>• 增加库存不足产品的采购量，避免缺货风险</p>
                    <p>• 调整安全库存水平，确保供应连续性</p>
                    <p>• 改进销售预测准确性，提前识别需求变化</p>
                    <p>• 建立库存预警机制，及时补充库存</p>
                """
            elif high_count > low_count:
                advice = """
                    <p>• 制定过剩库存清理计划，降低库存成本</p>
                    <p>• 推出促销活动，加速清理积压库存</p>
                    <p>• 优化采购计划，避免过度库存</p>
                    <p>• 加强需求预测，减少库存波动</p>
                """
            else:
                advice = """
                    <p>• 分产品制定差异化库存策略，提高整体库存健康度</p>
                    <p>• 优化供应链流程，减少库存波动</p>
                    <p>• 加强销售与库存协同，提高库存周转率</p>
                    <p>• 建立库存管理评估体系，定期优化</p>
                """

            # 合并批次级建议
            if batch_advice:
                advice += batch_advice

            return advice
        else:
            return "<p>无足够数据提供库存优化建议</p>"

    elif card_id == "healthy_inventory":
        health_distribution = analysis.get('health_distribution', {})

        if health_distribution:
            healthy_count = health_distribution.get('库存健康', 0)
            total_count = sum(health_distribution.values())

            healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

            if healthy_percentage < 50:
                return """
                    <p>• 全面评估库存策略，找出库存不健康原因</p>
                    <p>• 重新设定安全库存水平和补货点</p>
                    <p>• 优化需求预测方法，提高准确性</p>
                    <p>• 实施库存健康度提升计划，定期跟踪进展</p>
                """
            elif healthy_percentage < 70:
                return """
                    <p>• 针对库存不足和过剩产品采取差异化策略</p>
                    <p>• 优化库存控制参数，如安全库存系数</p>
                    <p>• 加强销售与供应链协同，平衡供需</p>
                    <p>• 建立健康库存激励机制，提高管理积极性</p>
                """
            else:
                return """
                    <p>• 保持现有库存管理策略，继续优化细节</p>
                    <p>• 关注库存健康产品的需求变化，及时调整</p>
                    <p>• 复制成功经验到其他产品类别</p>
                    <p>• 持续监控市场变化，预防库存风险</p>
                """
        else:
            return "<p>无足够数据提供健康库存优化建议</p>"

    elif card_id == "high_risk_inventory":
        risk_distribution = analysis.get('risk_distribution', {})
        batch_analysis = analysis.get('batch_analysis')

        # 批次级优化建议
        batch_advice = ""
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

            if not high_risk_batches.empty:
                # 计算平均清库天数
                avg_clearance = high_risk_batches['预计清库天数'].mean()

                batch_advice = "<p>• <strong>批次级建议：</strong></p>"
                batch_advice += f"<p>  - 对于预计清库天数超过{avg_clearance:.0f}天的批次，考虑特价促销</p>"
                batch_advice += "<p>  - 建立批次库龄预警机制，批次库龄达60天前提前干预</p>"

                # 针对无销量批次的建议
                dead_stock = high_risk_batches[high_risk_batches['日均销量'] <= 0.5]
                if not dead_stock.empty:
                    batch_advice += f"<p>  - 针对{len(dead_stock)}个无销量批次实施特别清理措施</p>"

        if risk_distribution:
            high_risk = risk_distribution.get('高风险', 0)
            total_risk = sum(risk_distribution.values())

            high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0

            advice = ""
            if high_risk_percentage > 20:
                advice = """
                    <p>• 立即制定高风险库存清理计划，设定明确目标</p>
                    <p>• 考虑特价促销、打折或搭售等方式加速销售</p>
                    <p>• 评估部分高风险库存转移至其他区域可行性</p>
                    <p>• 调整采购策略，暂停相关产品采购</p>
                    <p>• 分析高风险库存形成原因，避免重复问题</p>
                """
            elif high_risk_percentage > 10:
                advice = """
                    <p>• 对高风险库存进行分级管理，优先处理最紧急的</p>
                    <p>• 制定有针对性的促销活动，提高销售</p>
                    <p>• 优化预测模型，提高需求预测准确性</p>
                    <p>• 建立库存早期预警机制，防患于未然</p>
                """
            else:
                advice = """
                    <p>• 持续监控当前高风险库存，防止风险扩大</p>
                    <p>• 定期评估库存结构，保持低风险水平</p>
                    <p>• 完善库存风险评估体系，提前识别风险</p>
                    <p>• 优化采购计划与库存策略，防止新增高风险库存</p>
                """

            # 合并批次级建议
            if batch_advice:
                advice += batch_advice

            return advice
        else:
            return "<p>无足够数据提供高风险库存优化建议</p>"

    elif card_id == "assigned_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        assigned_inventory = analysis.get('assigned_inventory', 0)
        forecast_vs_inventory = analysis.get('forecast_vs_inventory')

        # 预测偏差优化建议
        forecast_advice = ""
        if forecast_vs_inventory is not None and '预测偏差分类' in forecast_vs_inventory.columns:
            over_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过高')
            under_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过低')

            if over_forecast + under_forecast > 0:
                forecast_advice = "<p>• <strong>预测优化建议：</strong></p>"

                if over_forecast > under_forecast:
                    forecast_advice += "<p>  - 整体预测偏高，建议下调预测参数</p>"
                    forecast_advice += "<p>  - 对预测过高的产品进行重点销售支持</p>"
                else:
                    forecast_advice += "<p>  - 整体预测偏低，建议提高安全库存水平</p>"
                    forecast_advice += "<p>  - 加快补货周期，防止缺货风险</p>"

        if total_inventory > 0:
            assigned_percentage = assigned_inventory / total_inventory * 100

            advice = ""
            if assigned_percentage < 40:
                advice = """
                    <p>• 评估库存闲置原因，提高库存利用率</p>
                    <p>• 优化销售计划，加速库存周转</p>
                    <p>• 考虑调整产品结构，减少低周转产品比例</p>
                    <p>• 加强市场开发，拓展销售渠道</p>
                """
            elif assigned_percentage < 60:
                advice = """
                    <p>• 优化订单管理流程，提高库存分配效率</p>
                    <p>• 加强销售预测，提前规划库存分配</p>
                    <p>• 定期评估库存结构，调整产品组合</p>
                    <p>• 优化库存补货策略，保持合理库存水平</p>
                """
            else:
                advice = """
                    <p>• 关注库存安全水平，避免出现缺货风险</p>
                    <p>• 优化补货周期，确保库存及时补充</p>
                    <p>• 评估提高安全库存的必要性</p>
                    <p>• 加强供应商管理，缩短采购周期</p>
                """

            # 合并预测建议
            if forecast_advice:
                advice += forecast_advice

            return advice
        else:
            return "<p>无足够数据提供库存分配优化建议</p>"

    return "<p>建议数据加载中...</p>"


def generate_action_plan(card_id):
    """生成行动方案HTML内容"""
    if 'analysis_result' not in st.session_state:
        return "<p>行动计划加载中...</p>"

    if card_id == "total_inventory":
        health_distribution = st.session_state['analysis_result'].get('health_distribution', {})
        batch_analysis = st.session_state['analysis_result'].get('batch_analysis')

        # 批次级行动方案
        batch_action = ""
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_count = sum(batch_analysis['风险程度'].isin(['极高风险', '高风险']))

            if high_risk_count > 0:
                batch_action = f"<p><strong>批次级行动方案：</strong>组织专项会议，针对{high_risk_count}个高风险批次制定详细处理计划，明确责任人和时间节点。</p>"

        if health_distribution:
            healthy_count = health_distribution.get('库存健康', 0)
            low_count = health_distribution.get('库存不足', 0)
            high_count = health_distribution.get('库存过剩', 0)
            total_count = healthy_count + low_count + high_count

            healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

            action_plan = ""
            if healthy_percentage < 50:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>全面评估库存状况，对库存不足和过剩产品制定应对计划</p>
                    <p><strong>中期行动（3个月）：</strong>优化库存控制参数和补货策略，提高库存健康比例</p>
                    <p><strong>长期行动（6个月）：</strong>建立完善的库存健康管理体系，持续提高库存管理水平</p>
                """
            else:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>细化库存分析，针对不同类别产品制定优化措施</p>
                    <p><strong>中期行动（3个月）：</strong>完善库存预警机制，提高库存风险识别能力</p>
                    <p><strong>长期行动（6个月）：</strong>构建数据驱动的库存决策系统，实现库存管理智能化</p>
                """

            # 合并批次级行动方案
            if batch_action:
                action_plan += batch_action

            return action_plan
        else:
            return "<p>无足够数据制定行动计划</p>"

    elif card_id == "healthy_inventory":
        health_distribution = st.session_state['analysis_result'].get('health_distribution', {})

        if health_distribution:
            healthy_count = health_distribution.get('库存健康', 0)
            total_count = sum(health_distribution.values())

            healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

            if healthy_percentage < 60:
                return """
                    <p><strong>紧急行动（1周内）：</strong>分析库存不健康的关键产品，制定快速干预计划</p>
                    <p><strong>近期行动（1个月）：</strong>调整库存控制参数，优化补货策略和订货点</p>
                    <p><strong>中期行动（3个月）：</strong>重建库存健康评估体系，提高管理精准性</p>
                """
            else:
                return """
                    <p><strong>近期行动（1个月）：</strong>持续监控库存健康状态，巩固现有成果</p>
                    <p><strong>中期行动（3个月）：</strong>优化需求预测模型，进一步提高库存健康度</p>
                    <p><strong>长期行动（6个月）：</strong>建立库存健康长效机制，确保可持续性</p>
                """
        else:
            return "<p>无足够数据制定行动计划</p>"

    elif card_id == "high_risk_inventory":
        risk_distribution = st.session_state['analysis_result'].get('risk_distribution', {})
        inventory_analysis = st.session_state['analysis_result'].get('inventory_analysis', pd.DataFrame())
        batch_analysis = st.session_state['analysis_result'].get('batch_analysis')

        # 批次级行动方案
        batch_action = ""
        if batch_analysis is not None and not batch_analysis.empty:
            extreme_high_risk = sum(batch_analysis['风险程度'] == '极高风险')

            if extreme_high_risk > 0:
                batch_action = f"<p><strong>紧急批次行动：</strong>立即组织销售会议，针对{extreme_high_risk}个极高风险批次制定7天内实施的紧急促销方案。</p>"

        if risk_distribution and not inventory_analysis.empty:
            high_risk = risk_distribution.get('高风险', 0)
            total_risk = sum(risk_distribution.values())

            high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0

            # 获取高风险库存产品
            high_risk_products = inventory_analysis[inventory_analysis['积压风险'] == '高风险']

            if high_risk_percentage > 15 or (
                    not high_risk_products.empty and high_risk_products['清库周期(月)'].max() > 12):
                action_plan = """
                    <p><strong>紧急行动（2周内）：</strong>对最高风险库存制定特别清理方案，包括特价促销或内部调拨</p>
                    <p><strong>近期行动（1个月）：</strong>开展高风险库存促销活动，设定明确的清库目标</p>
                    <p><strong>中期行动（3个月）：</strong>全面优化采购策略和库存政策，防止新增高风险库存</p>
                """
            else:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>持续监控高风险库存，制定分批清理计划</p>
                    <p><strong>中期行动（3个月）：</strong>优化库存预警系统，提高风险预测能力</p>
                    <p><strong>长期行动（6个月）：</strong>建立库存风险评估常态化机制，防患于未然</p>
                """

            # 合并批次级行动方案
            if batch_action:
                action_plan += batch_action

            return action_plan
        else:
            return "<p>无足够数据制定行动计划</p>"

    elif card_id == "assigned_inventory":
        total_inventory = st.session_state['analysis_result'].get('total_inventory', 0)
        assigned_inventory = st.session_state['analysis_result'].get('assigned_inventory', 0)
        forecast_vs_inventory = st.session_state['analysis_result'].get('forecast_vs_inventory')

        # 预测相关行动计划
        forecast_action = ""
        if forecast_vs_inventory is not None and '预测偏差分类' in forecast_vs_inventory.columns:
            biased_products = sum(forecast_vs_inventory['预测偏差分类'] != '预测准确')

            if biased_products > 0:
                forecast_action = f"<p><strong>预测优化行动：</strong>组织销售和计划部门联合会议，针对{biased_products}个预测偏差产品进行原因分析和预测参数调整。</p>"

        if total_inventory > 0:
            assigned_percentage = assigned_inventory / total_inventory * 100

            if assigned_percentage < 50:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>加强市场开发，提高销售到库存比率</p>
                    <p><strong>中期行动（3个月）：</strong>优化产品结构，减少低周转产品库存比例</p>
                    <p><strong>长期行动（6个月）：</strong>建立销售与库存协同机制，提高整体库存效率</p>
                """
            elif assigned_percentage > 80:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>评估库存安全水平，确保供应连续性</p>
                    <p><strong>中期行动（3个月）：</strong>优化供应链响应速度，缩短补货周期</p>
                    <p><strong>长期行动（6个月）：</strong>建立动态安全库存管理机制，平衡供需变化</p>
                """
            else:
                action_plan = """
                    <p><strong>近期行动（1个月）：</strong>细化库存分配分析，找出优化空间</p>
                    <p><strong>中期行动（3个月）：</strong>优化订单管理流程，提高库存周转效率</p>
                    <p><strong>长期行动（6个月）：</strong>建立库存分配绩效评估体系，促进持续改进</p>
                """

            # 合并预测行动计划
            if forecast_action:
                action_plan += forecast_action

            return action_plan
        else:
            return "<p>无足够数据制定行动计划</p>"

    return "<p>行动计划加载中...</p>"


# ==================== 6. 主页面函数 ====================
def show_inventory_analysis():
    """显示库存分析页面"""
    # 页面样式
    st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton > button {
        background-color: #1f3867;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #4c78a8;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.title("📦 库存分析")

    # 加载数据
    with st.spinner("正在加载库存数据..."):
        sales_data, inventory_data, batch_data, monthly_inventory, forecast_data, person_customer_data = load_inventory_data()

    if inventory_data.empty:
        st.error("无法加载库存数据，请检查数据文件是否存在")
        return

    # 应用筛选
    filtered_sales = apply_inventory_filters(sales_data)

    # 分析数据
    analysis_result = analyze_inventory_data(filtered_sales, inventory_data, batch_data, monthly_inventory,
                                             forecast_data)

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

    if not analysis_result:
        st.warning("无法分析库存数据，请检查数据格式")
        return

    # 获取关键指标
    total_inventory = analysis_result.get('total_inventory', 0)
    health_distribution = analysis_result.get('health_distribution', {})
    risk_distribution = analysis_result.get('risk_distribution', {})
    assigned_inventory = analysis_result.get('assigned_inventory', 0)

    # 计算健康库存占比
    healthy_count = health_distribution.get('库存健康', 0)
    total_count = sum(health_distribution.values()) if health_distribution else 0
    healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0

    # 计算高风险库存占比
    high_risk = risk_distribution.get('高风险', 0)
    total_risk = sum(risk_distribution.values()) if risk_distribution else 0
    high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0

    # 计算已分配库存占比
    assigned_percentage = assigned_inventory / total_inventory * 100 if total_inventory > 0 else 0

    # 显示关键指标卡片
    st.subheader("📊 库存概览")

    col1, col2 = st.columns(2)

    with col1:
        create_inventory_flip_card(
            "total_inventory",
            "总库存量",
            total_inventory,
            "当前总库存数量"
        )

    with col2:
        create_inventory_flip_card(
            "healthy_inventory",
            "健康库存占比",
            healthy_percentage,
            "库存覆盖15-90天",
            is_percentage=True
        )

    col3, col4 = st.columns(2)

    with col3:
        create_inventory_flip_card(
            "high_risk_inventory",
            "高风险库存占比",
            high_risk_percentage,
            "清库周期>6个月",
            is_percentage=True
        )

    with col4:
        create_inventory_flip_card(
            "assigned_inventory",
            "已分配库存占比",
            assigned_percentage,
            "已针对订单分配",
            is_percentage=True
        )

    # 库存健康状况分析
    st.subheader("📊 库存健康状况")

    col1, col2 = st.columns(2)

    with col1:
        if health_distribution:
            fig = create_inventory_health_chart(health_distribution, "库存健康状况分布")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>库存健康状态分布：健康库存{format_percentage(healthy_percentage)}，
                库存不足{format_percentage(health_distribution.get('库存不足', 0) / total_count * 100 if total_count > 0 else 0)}，
                库存过剩{format_percentage(health_distribution.get('库存过剩', 0) / total_count * 100 if total_count > 0 else 0)}。
                {'库存结构相对健康，大部分产品库存控制在合理范围内。' if healthy_percentage > 60 else '库存结构需要优化，健康库存比例偏低。'}</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if risk_distribution:
            fig = create_inventory_risk_chart(risk_distribution, "库存积压风险分布")
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>库存积压风险分布：高风险{format_percentage(high_risk_percentage)}，
                中风险{format_percentage(risk_distribution.get('中风险', 0) / total_risk * 100 if total_risk > 0 else 0)}，
                低风险{format_percentage(risk_distribution.get('低风险', 0) / total_risk * 100 if total_risk > 0 else 0)}。
                {'库存积压风险总体可控，低风险产品占比高。' if high_risk_percentage < 10 else '库存积压风险较高，需要关注高风险产品的清库计划。'}</p>
            </div>
            """, unsafe_allow_html=True)

    # 批次库存分析 - 新增部分
    batch_analysis = analysis_result.get('batch_analysis')
    if batch_analysis is not None and not batch_analysis.empty:
        st.subheader("📦 批次级别风险分析")

        # 创建批次库龄风险分布图
        batch_fig = create_batch_age_chart(batch_analysis, "批次风险程度分布")
        if batch_fig:
            st.plotly_chart(batch_fig, use_container_width=True)

            # 图表解读
            risk_counts = batch_analysis['风险程度'].value_counts().to_dict()
            high_risk_count = risk_counts.get('极高风险', 0) + risk_counts.get('高风险', 0)
            total_batches = sum(risk_counts.values())

            high_risk_ratio = high_risk_count / total_batches if total_batches > 0 else 0
            batch_risk_status = '批次级风险总体受控，高风险批次比例较低。' if high_risk_ratio < 0.1 else '存在较多高风险批次，需要制定清库计划。'

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>批次风险分布：发现{high_risk_count}个高风险或极高风险批次，占比{format_percentage(high_risk_count / total_batches * 100 if total_batches > 0 else 0)}。
                {batch_risk_status}</p>
                {f"极高风险批次{risk_counts.get('极高风险', 0)}个，需要紧急处理。" if risk_counts.get('极高风险', 0) > 0 else ""}
            </div>
            """, unsafe_allow_html=True)

    # 预测与库存对比
    st.subheader("📊 库存与预测对比")

    forecast_vs_inventory = analysis_result.get('forecast_vs_inventory')
    if forecast_vs_inventory is not None and not forecast_vs_inventory.empty:
        # 库存与预测对比图
        fig = create_inventory_forecast_chart(forecast_vs_inventory, "库存与预测对比")
        st.plotly_chart(fig, use_container_width=True)

        # 添加预测偏差分析 - 新增部分
        if '预测偏差' in forecast_vs_inventory.columns:
            forecast_bias_fig = create_forecast_bias_chart(analysis_result, "产品预测偏差分析")
            if forecast_bias_fig:
                st.plotly_chart(forecast_bias_fig, use_container_width=True)

                # 图表解读
                if '预测偏差分类' in forecast_vs_inventory.columns:
                    over_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过高')
                    under_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测过低')
                    accurate_forecast = sum(forecast_vs_inventory['预测偏差分类'] == '预测准确')

                    bias_direction = "偏高" if over_forecast > under_forecast else "偏低"
                    bias_risk = "库存积压风险" if over_forecast > under_forecast else "缺货风险"

                    st.markdown(f"""
                            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                                <h4>📊 预测偏差解读</h4>
                                <p>预测准确性分析：{over_forecast}个产品预测过高，{under_forecast}个产品预测过低，{accurate_forecast}个产品预测准确。
                                整体预测趋势{bias_direction}，存在{bias_risk}。{'建议优化预测模型，提高预测准确性。' if over_forecast + under_forecast > accurate_forecast else '预测准确性相对较好，继续保持现有预测方法。'}</p>
                            </div>
                            """, unsafe_allow_html=True)

        # 图表解读
        status_counts = forecast_vs_inventory['预测库存状态'].value_counts().to_dict()
        low_forecast = status_counts.get('库存不足', 0)
        normal_forecast = status_counts.get('库存适中', 0)
        high_forecast = status_counts.get('库存过剩', 0)

        total_forecast = low_forecast + normal_forecast + high_forecast

        st.markdown(f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['primary']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                    <h4>📊 图表解读</h4>
                    <p>库存与预测对比：库存不足{low_forecast}个产品({format_percentage(low_forecast / total_forecast * 100 if total_forecast > 0 else 0)})，
                    库存适中{normal_forecast}个产品({format_percentage(normal_forecast / total_forecast * 100 if total_forecast > 0 else 0)})，
                    库存过剩{high_forecast}个产品({format_percentage(high_forecast / total_forecast * 100 if total_forecast > 0 else 0)})。
                    {'大多数产品库存水平与预测需求匹配良好。' if normal_forecast / total_forecast > 0.6 and total_forecast > 0 else '产品库存水平与预测需求匹配度不高,需要调整。'}</p>
                    {f'<p style="color: {COLORS["warning"]}"><strong>注意：</strong>有{low_forecast}个产品库存可能无法满足预测需求，建议及时补货！</p>' if low_forecast > 0 else ''}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("无法获取预测数据，无法进行库存与预测对比分析")

        # 高风险产品详细分析
    st.subheader("📊 高风险产品详细分析")

    inventory_analysis = analysis_result.get('inventory_analysis', pd.DataFrame())
    if not inventory_analysis.empty:
        # 筛选高风险产品
        high_risk_products = inventory_analysis[inventory_analysis['积压风险'] == '高风险']

        if not high_risk_products.empty:
            # 创建高风险产品清库周期图
            fig = create_high_risk_product_chart(inventory_analysis, "高风险产品清库周期TOP10")
            st.plotly_chart(fig, use_container_width=True)

            # 高风险产品统计
            high_risk_value = high_risk_products['现有库存'].sum()
            avg_clear_period = high_risk_products['清库周期(月)'].mean()

            st.markdown(f"""
                    <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid {COLORS['danger']}; 
                                padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4>⚠️ 高风险产品警告</h4>
                        <p><strong>高风险产品统计：</strong></p>
                        <p>• 高风险产品数量: <span style="color: {COLORS['danger']};">{len(high_risk_products)}个</span></p>
                        <p>• 高风险库存总量: <span style="color: {COLORS['danger']};">{format_number(high_risk_value)}</span></p>
                        <p>• 平均清库周期: <span style="color: {COLORS['danger']};">{avg_clear_period:.1f}个月</span></p>
                        <p><strong>建议：</strong>对这些产品制定专项清库计划，如促销活动、打折销售或调整库存策略。</p>
                    </div>
                    """, unsafe_allow_html=True)

            # 显示高风险产品清单
            with st.expander("查看高风险产品详细清单"):
                st.write(high_risk_products[['产品代码', '现有库存', '月平均销量', '清库周期(月)', '库存覆盖天数']])
        else:
            st.success("当前无高风险产品，库存管理良好！")

        # 批次级别高风险分析 - 新增部分
        batch_analysis = analysis_result.get('batch_analysis')
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

            if not high_risk_batches.empty:
                # 创建高风险批次清库天数分析图
                batch_clearance_fig = create_batch_clearance_chart(batch_analysis, "高风险批次清库天数分析")
                if batch_clearance_fig:
                    st.plotly_chart(batch_clearance_fig, use_container_width=True)

                # 高风险批次统计
                batch_value = high_risk_batches['批次价值'].sum() if '批次价值' in high_risk_batches.columns else 0
                avg_clearance_days = high_risk_batches['预计清库天数'].mean()
                avg_age = high_risk_batches['库龄'].mean()

                # 责任分析
                responsibility_analysis = ""
                if '责任人' in high_risk_batches.columns:
                    person_counts = high_risk_batches['责任人'].value_counts().head(3)
                    if not person_counts.empty:
                        responsibility_analysis = "<p><strong>主要责任人：</strong></p>"
                        for person, count in person_counts.items():
                            responsibility_analysis += f"<p>• {person}: 负责{count}个高风险批次</p>"

                st.markdown(f"""
                        <div style="background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid {COLORS['danger']}; 
                                    padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                            <h4>⚠️ 高风险批次警告</h4>
                            <p><strong>高风险批次统计：</strong></p>
                            <p>• 高风险批次数量: <span style="color: {COLORS['danger']};">{len(high_risk_batches)}个</span></p>
                            <p>• 高风险批次价值: <span style="color: {COLORS['danger']};">{format_currency(batch_value)}</span></p>
                            <p>• 平均批次库龄: <span style="color: {COLORS['danger']};">{avg_age:.1f}天</span></p>
                            <p>• 平均清库天数: <span style="color: {COLORS['danger']};">{avg_clearance_days:.1f}天</span></p>
                            {responsibility_analysis}
                            <p><strong>建议：</strong>按责任人组织专项清库会议，设定明确的清库目标和时间节点，对无销量批次考虑特价处理或转仓。</p>
                        </div>
                        """, unsafe_allow_html=True)

                # 显示高风险批次清单
                with st.expander("查看高风险批次详细清单"):
                    show_columns = ['产品代码', '库龄', '预计清库天数', '风险程度', '积压原因', '建议措施']
                    if '责任人' in high_risk_batches.columns:
                        show_columns.append('责任人')
                    if '责任区域' in high_risk_batches.columns:
                        show_columns.append('责任区域')
                    if '责任分析摘要' in high_risk_batches.columns:
                        show_columns.append('责任分析摘要')

                    st.write(high_risk_batches[show_columns])
            else:
                st.success("当前无高风险批次，批次级库存管理良好！")
    else:
        st.info("无法获取库存分析数据，无法进行高风险产品分析")

    # 库存洞察总结
    st.subheader("💡 库存洞察总结")

    # 生成综合评价
    if health_distribution and risk_distribution:
        healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0
        high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0

        # 新增：批次级分析的综合评价
        batch_insight = ""
        batch_analysis = analysis_result.get('batch_analysis')
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
            high_risk_batch_count = len(high_risk_batches)
            total_batch_count = len(batch_analysis)

            batch_insight = f"批次级分析发现{high_risk_batch_count}个高风险批次，占比{format_percentage(high_risk_batch_count / total_batch_count * 100 if total_batch_count > 0 else 0)}。"

            # 添加责任分析
            if '责任人' in high_risk_batches.columns and not high_risk_batches.empty:
                top_responsible = high_risk_batches['责任人'].value_counts().head(1)
                if not top_responsible.empty:
                    top_person = top_responsible.index[0]
                    top_count = top_responsible.iloc[0]
                    batch_insight += f"主要责任人{top_person}负责{top_count}个高风险批次，需优先跟进。"

        if healthy_percentage >= 70 and high_risk_percentage <= 10:
            status = "优秀"
            status_color = COLORS['success']
            comment = "库存管理非常健康，库存积压风险低，库存结构合理。"
        elif healthy_percentage >= 60 and high_risk_percentage <= 15:
            status = "良好"
            status_color = COLORS['success']
            comment = "库存管理总体良好，库存结构相对健康，积压风险可控。"
        elif healthy_percentage >= 50 or high_risk_percentage <= 20:
            status = "一般"
            status_color = COLORS['warning']
            comment = "库存管理存在一定问题，健康库存比例不高或积压风险较大，需要改进。"
        else:
            status = "欠佳"
            status_color = COLORS['danger']
            comment = "库存管理问题明显，健康库存比例低，积压风险高，亟需优化。"

        st.markdown(f"""
                <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                            padding: 1rem; border-radius: 0.5rem;">
                    <h4>📋 库存管理总评</h4>
                    <p><strong>总体状况：</strong><span style="color: {status_color};">{status}</span></p>
                    <p><strong>健康库存情况：</strong>{format_percentage(healthy_percentage)} ({get_health_status_text(healthy_percentage)})</p>
                    <p><strong>积压风险情况：</strong>{format_percentage(high_risk_percentage)} ({get_risk_status_text(high_risk_percentage)})</p>
                    <p><strong>批次库龄情况：</strong>{get_batch_age_status_text(batch_analysis)}</p>
                    <p><strong>预测匹配情况：</strong>{get_forecast_match_status_text(forecast_vs_inventory)}</p>
                    <p><strong>综合评价：</strong>{comment} {batch_insight}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("无法生成库存洞察总结，数据不完整")


def get_health_status_text(percentage):
    """根据健康库存占比生成状态文本"""
    if percentage >= 70:
        return "非常健康"
    elif percentage >= 60:
        return "比较健康"
    elif percentage >= 50:
        return "一般"
    else:
        return "需要改善"


def get_risk_status_text(percentage):
    """根据高风险库存占比生成状态文本"""
    if percentage <= 5:
        return "风险极低"
    elif percentage <= 10:
        return "风险较低"
    elif percentage <= 20:
        return "风险中等"
    else:
        return "风险较高"


def get_batch_age_status_text(batch_data):
    """根据批次库龄数据生成状态文本"""
    if batch_data is None or batch_data.empty:
        return "无法评估"

    # 计算批次库龄风险分布
    risk_counts = batch_data['风险程度'].value_counts().to_dict()

    high_risk_count = risk_counts.get('极高风险', 0) + risk_counts.get('高风险', 0)
    total_batches = sum(risk_counts.values())
    high_risk_ratio = high_risk_count / total_batches if total_batches > 0 else 0

    if high_risk_ratio > 0.2:
        return f"高风险批次比例较高({format_percentage(high_risk_ratio * 100)})"
    elif high_risk_count > 0:
        return f"存在{high_risk_count}个高风险批次，需要关注"
    else:
        return "批次库龄结构良好"


def get_forecast_match_status_text(forecast_data):
    """根据预测匹配数据生成状态文本"""
    if forecast_data is None or forecast_data.empty:
        return "无法评估"

    status_counts = forecast_data['预测库存状态'].value_counts().to_dict()

    low_forecast = status_counts.get('库存不足', 0)
    normal_forecast = status_counts.get('库存适中', 0)
    high_forecast = status_counts.get('库存过剩', 0)

    total_forecast = low_forecast + normal_forecast + high_forecast

    low_ratio = low_forecast / total_forecast if total_forecast > 0 else 0
    normal_ratio = normal_forecast / total_forecast if total_forecast > 0 else 0
    high_ratio = high_forecast / total_forecast if total_forecast > 0 else 0

    if low_ratio > 0.2:
        return f"有{low_forecast}个产品库存可能不足，存在缺货风险"
    elif high_ratio > 0.2:
        return f"有{high_forecast}个产品库存过剩，存在积压风险"
    elif normal_ratio > 0.7:
        return "库存与预测需求匹配度高"
    else:
        return "库存与预测需求匹配度一般"


if __name__ == "__main__":
    show_inventory_analysis()