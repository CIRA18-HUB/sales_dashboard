# pages/inventory_page.py - 库存分析页面
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import math
import re

# 从config导入必要的函数和配置
from config import (
    COLORS, DATA_FILES, format_currency, format_percentage, format_number,
    load_css, check_authentication, setup_page
)

# 设置页面
setup_page()

# 检查认证
if not check_authentication():
    st.stop()

# 页面标题
st.title("📦 库存分析")


# ==================== 1. 数据加载函数 ====================
@st.cache_data
def load_inventory_data():
    """加载库存分析所需的所有数据，处理嵌套结构的库存数据"""
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

        # 加载实时库存数据 - 支持嵌套结构
        try:
            inventory_data_raw = pd.read_excel(DATA_FILES['inventory'])

            # 处理嵌套结构的库存数据
            # 1. 提取产品级别数据（非空的产品代码行）
            product_rows = inventory_data_raw[inventory_data_raw.iloc[:, 0].notna()]
            inventory_data = product_rows.iloc[:, :7].copy()

            # 确保列名正确
            if len(inventory_data.columns) >= 7:
                inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                          '现有库存可订量', '待入库量', '本月剩余可订量']

            # 2. 提取批次级别数据
            batch_data = []
            current_product_code = None
            current_product_desc = None

            for i, row in inventory_data_raw.iterrows():
                # 获取产品层信息
                if pd.notna(row.iloc[0]):  # 产品行
                    current_product_code = row.iloc[0]
                    current_product_desc = row.iloc[1] if len(row) > 1 else ""

                # 获取批次层信息
                elif pd.notna(row.iloc[7]) if len(row) > 7 else False:  # 批次行
                    batch_row = row.iloc[7:].copy() if len(row) > 7 else []
                    if len(batch_row) >= 4:  # 确保有足够的列
                        batch_info = {
                            '产品代码': current_product_code,
                            '描述': current_product_desc,
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
            monthly_inventory = pd.read_excel(DATA_FILES['month_end_inventory'])
            if '所属年月' in monthly_inventory.columns:
                monthly_inventory['所属年月'] = pd.to_datetime(monthly_inventory['所属年月'])
        except Exception as e:
            st.warning(f"处理月末库存数据时出错: {str(e)}")
            monthly_inventory = pd.DataFrame()

        # 加载人工预测数据
        try:
            forecast_data = pd.read_excel(DATA_FILES['forecast'])
            if '所属年月' in forecast_data.columns:
                forecast_data['所属年月'] = pd.to_datetime(forecast_data['所属年月'])
        except Exception as e:
            st.warning(f"处理预测数据时出错: {str(e)}")
            forecast_data = pd.DataFrame()

        # 加载人与客户关系表
        try:
            person_customer_data = pd.read_excel(DATA_FILES['customer_relation'])
        except Exception as e:
            st.warning(f"处理客户关系数据时出错: {str(e)}")
            person_customer_data = pd.DataFrame()

        return {
            'sales_orders': sales_orders,
            'inventory_data': inventory_data,
            'batch_data': batch_df,
            'monthly_inventory': monthly_inventory,
            'forecast_data': forecast_data,
            'person_customer_data': person_customer_data
        }

    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return {
            'sales_orders': pd.DataFrame(),
            'inventory_data': pd.DataFrame(),
            'batch_data': pd.DataFrame(),
            'monthly_inventory': pd.DataFrame(),
            'forecast_data': pd.DataFrame(),
            'person_customer_data': pd.DataFrame()
        }


# ==================== 2. 筛选器函数 ====================
def create_inventory_filters(data):
    """创建库存页面特有的筛选器"""
    if not data or 'inventory_data' not in data or data['inventory_data'].empty:
        st.warning("库存数据不可用，无法创建筛选器")
        return data

    # 初始化库存特有的筛选器状态
    if 'inventory_filter_product_type' not in st.session_state:
        st.session_state.inventory_filter_product_type = '全部'
    if 'inventory_filter_status' not in st.session_state:
        st.session_state.inventory_filter_status = '全部'
    if 'inventory_filter_batch_age' not in st.session_state:
        st.session_state.inventory_filter_batch_age = '全部'

    # 提取库存数据
    inventory_data = data['inventory_data']
    batch_data = data.get('batch_data', pd.DataFrame())

    with st.sidebar:
        st.markdown("## 🔍 库存筛选")
        st.markdown("---")

        # 产品代码筛选
        product_codes = ['全部'] + sorted(inventory_data['产品代码'].unique().tolist())
        selected_product = st.selectbox(
            "选择产品代码",
            product_codes,
            index=0,
            key="inventory_filter_product"
        )

        # 库存状态筛选（如果已经分析过）
        if 'inventory_analysis' in data and '库存状态' in data['inventory_analysis'].columns:
            status_options = ['全部'] + sorted(data['inventory_analysis']['库存状态'].unique().tolist())
            selected_status = st.selectbox(
                "库存状态",
                status_options,
                index=0,
                key="inventory_filter_status"
            )
            st.session_state.inventory_filter_status = selected_status

        # 批次库龄筛选（如果有批次数据）
        if not batch_data.empty and '生产日期' in batch_data.columns:
            age_options = ['全部', '30天以内', '30-60天', '60-90天', '90天以上']
            selected_age = st.selectbox(
                "批次库龄",
                age_options,
                index=0,
                key="inventory_filter_batch_age"
            )
            st.session_state.inventory_filter_batch_age = selected_age

        # 重置筛选器按钮
        if st.button("重置筛选条件", key="inventory_reset_filters"):
            st.session_state.inventory_filter_product_type = '全部'
            st.session_state.inventory_filter_status = '全部'
            st.session_state.inventory_filter_batch_age = '全部'
            st.rerun()

    # 应用筛选条件
    filtered_data = apply_inventory_filters(data)

    return filtered_data


def apply_inventory_filters(data):
    """应用库存特有的筛选条件"""
    if not data or 'inventory_data' not in data or data['inventory_data'].empty:
        return data

    filtered_data = data.copy()

    # 提取数据
    inventory_data = filtered_data['inventory_data'].copy()
    batch_data = filtered_data.get('batch_data', pd.DataFrame()).copy()

    # 应用产品代码筛选
    if 'inventory_filter_product' in st.session_state and st.session_state.inventory_filter_product != '全部':
        selected_product = st.session_state.inventory_filter_product
        inventory_data = inventory_data[inventory_data['产品代码'] == selected_product]

        if not batch_data.empty:
            batch_data = batch_data[batch_data['产品代码'] == selected_product]

    # 应用库存状态筛选
    if ('inventory_filter_status' in st.session_state and
            st.session_state.inventory_filter_status != '全部' and
            'inventory_analysis' in filtered_data and
            '库存状态' in filtered_data['inventory_analysis'].columns):

        selected_status = st.session_state.inventory_filter_status
        status_products = filtered_data['inventory_analysis'][
            filtered_data['inventory_analysis']['库存状态'] == selected_status
            ]['产品代码'].tolist()

        inventory_data = inventory_data[inventory_data['产品代码'].isin(status_products)]

        if not batch_data.empty:
            batch_data = batch_data[batch_data['产品代码'].isin(status_products)]

    # 应用批次库龄筛选
    if ('inventory_filter_batch_age' in st.session_state and
            st.session_state.inventory_filter_batch_age != '全部' and
            not batch_data.empty and
            '生产日期' in batch_data.columns):

        today = pd.Timestamp.now().date()
        age_filter = st.session_state.inventory_filter_batch_age

        if '生产日期' in batch_data.columns:
            # 计算库龄
            batch_data['库龄'] = batch_data['生产日期'].apply(
                lambda x: (today - x.date()).days if pd.notna(x) else 0
            )

            # 应用库龄筛选
            if age_filter == '30天以内':
                batch_data = batch_data[batch_data['库龄'] <= 30]
            elif age_filter == '30-60天':
                batch_data = batch_data[(batch_data['库龄'] > 30) & (batch_data['库龄'] <= 60)]
            elif age_filter == '60-90天':
                batch_data = batch_data[(batch_data['库龄'] > 60) & (batch_data['库龄'] <= 90)]
            elif age_filter == '90天以上':
                batch_data = batch_data[batch_data['库龄'] > 90]

            # 更新库存数据以匹配筛选后的批次
            filtered_products = batch_data['产品代码'].unique()
            inventory_data = inventory_data[inventory_data['产品代码'].isin(filtered_products)]

    # 更新筛选后的数据
    filtered_data['inventory_data'] = inventory_data
    filtered_data['batch_data'] = batch_data

    return filtered_data


# ==================== 3. 库存分析函数 ====================
def analyze_inventory_data(data):
    """分析库存数据"""
    if not data or 'inventory_data' not in data or data['inventory_data'].empty:
        st.warning("无法获取库存数据进行分析")
        return {}

    try:
        # 提取数据
        inventory_data = data['inventory_data']
        batch_data = data.get('batch_data', pd.DataFrame())
        sales_data = data.get('sales_orders', pd.DataFrame())
        forecast_data = data.get('forecast_data', pd.DataFrame())

        # 计算当前年份
        current_year = datetime.now().year
        current_month = datetime.now().month

        # 计算最近6个月的销售数据
        six_months_ago = pd.Timestamp(year=current_year, month=current_month, day=1) - pd.DateOffset(months=6)

        if not sales_data.empty:
            recent_sales = sales_data[(sales_data['发运月份'] >= six_months_ago) &
                                      (sales_data['订单类型'].isin(['订单-正常产品', '订单-TT产品']))]

            # 按产品计算月平均销量
            monthly_sales_by_product = recent_sales.groupby(['产品代码', '产品简称'])[
                '求和项:数量（箱）'].sum().reset_index()
            monthly_sales_by_product['月平均销量'] = monthly_sales_by_product['求和项:数量（箱）'] / 6  # 6个月平均
        else:
            monthly_sales_by_product = pd.DataFrame(columns=['产品代码', '产品简称', '月平均销量'])

        # 处理库存数据
        inventory_summary = inventory_data.copy()

        # 确认库存数据结构
        if '现有库存可订量' in inventory_summary.columns and '现有库存' in inventory_summary.columns:
            # 提取最上层汇总数据
            top_level_inventory = inventory_summary.copy()

            # 计算库存周转率和库存覆盖天数
            inventory_analysis = top_level_inventory.merge(
                monthly_sales_by_product[['产品代码', '月平均销量']],
                on='产品代码',
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
            pending_inventory = top_level_inventory[
                '待入库量'].sum() if '待入库量' in top_level_inventory.columns else 0

            # 批次级别分析
            batch_analysis_result = None
            if not batch_data.empty and '生产日期' in batch_data.columns:
                batch_analysis_result = analyze_batch_data(batch_data, monthly_sales_by_product)

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

            return {
                'total_inventory': total_inventory,
                'assigned_inventory': assigned_inventory,
                'orderable_inventory': orderable_inventory,
                'pending_inventory': pending_inventory,
                'inventory_analysis': inventory_analysis,
                'health_distribution': health_distribution,
                'risk_distribution': risk_distribution,
                'batch_analysis': batch_analysis_result,
                'forecast_vs_inventory': forecast_vs_inventory
            }

    except Exception as e:
        st.error(f"库存分析出错: {str(e)}")
        return {}

    return {}


def analyze_batch_data(batch_data, sales_by_product):
    """分析批次级别的库存数据，计算风险和清库预测"""
    try:
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

    except Exception as e:
        st.warning(f"批次分析出错: {str(e)}")
        return None


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


# ==================== 5. 翻卡组件 ====================
def create_inventory_flip_card(card_id, title, value, subtitle="", is_currency=False, is_percentage=False,
                               is_number=False):
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
    elif is_number:
        formatted_value = format_number(value)
    else:
        formatted_value = str(value)

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

                        st.dataframe(high_risk_batches[show_columns].head(10), height=300)
                    else:
                        st.success("👍 当前没有高风险批次，库存状态良好！")
                else:
                    st.info("未能获取批次级别数据，无法进行深度分析。")

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

        if total_count > 0:
            healthy_percentage = healthy_count / total_count * 100
            return f"当前总库存量为 {format_number(total_inventory)}，其中健康库存产品占 {format_percentage(healthy_percentage)}，{'库存结构相对健康。' if healthy_percentage > 60 else '库存结构需要优化。'}"
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

        if total_risk > 0:
            high_risk_percentage = high_risk / total_risk * 100

            if high_risk_percentage > 20:
                return f"高风险库存产品占比达 {format_percentage(high_risk_percentage)}，库存积压风险较高，需要尽快采取措施清理过剩库存。"
            elif high_risk_percentage > 10:
                return f"高风险库存产品占比为 {format_percentage(high_risk_percentage)}，库存积压风险中等，需要关注并制定清库计划。"
            else:
                return f"高风险库存产品占比仅为 {format_percentage(high_risk_percentage)}，库存积压风险较低，可以继续保持良好的库存管理。"
        else:
            return "无法获取库存风险分布信息。"

    elif card_id == "assigned_inventory":
        total_inventory = analysis.get('total_inventory', 0)
        assigned_inventory = analysis.get('assigned_inventory', 0)
        orderable_inventory = analysis.get('orderable_inventory', 0)

        if total_inventory > 0:
            assigned_percentage = assigned_inventory / total_inventory * 100
            orderable_percentage = orderable_inventory / total_inventory * 100

            if assigned_percentage > 70:
                return f"已分配库存占比达 {format_percentage(assigned_percentage)}，可订库存仅占 {format_percentage(orderable_percentage)}，库存周转率较高，但可能需要关注库存补充。"
            elif assigned_percentage > 50:
                return f"已分配库存占比为 {format_percentage(assigned_percentage)}，可订库存占 {format_percentage(orderable_percentage)}，库存分配状态合理，供需平衡良好。"
            else:
                return f"已分配库存占比仅为 {format_percentage(assigned_percentage)}，可订库存占 {format_percentage(orderable_percentage)}，大量库存未得到有效利用，需要加强销售。"
        else:
            return "无法获取库存分配信息。"

    return "数据分析加载中..."


# ==================== 6. 主页面逻辑 ====================
def main():
    """主页面函数"""
    # 加载数据
    with st.spinner("正在加载库存数据..."):
        data = load_inventory_data()

    if data['inventory_data'].empty:
        st.error("无法加载库存数据，请检查数据文件是否存在并格式正确")
        return

    # 应用筛选
    filtered_data = create_inventory_filters(data)

    # 分析数据
    analysis_result = analyze_inventory_data(filtered_data)

    if not analysis_result:
        st.warning("无法分析库存数据，请检查数据格式")
        return

    # 将分析结果存储到session_state用于翻卡组件
    st.session_state['analysis_result'] = analysis_result

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
            "当前总库存数量",
            is_number=True
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
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
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
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>库存积压风险分布：高风险{format_percentage(high_risk_percentage)}，
                中风险{format_percentage(risk_distribution.get('中风险', 0) / total_risk * 100 if total_risk > 0 else 0)}，
                低风险{format_percentage(risk_distribution.get('低风险', 0) / total_risk * 100 if total_risk > 0 else 0)}。
                {'库存积压风险总体可控，低风险产品占比高。' if high_risk_percentage < 10 else '库存积压风险较高，需要关注高风险产品的清库计划。'}</p>
            </div>
            """, unsafe_allow_html=True)

    # 批次库存分析
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
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>批次风险分布：发现{high_risk_count}个高风险或极高风险批次，占比{format_percentage(high_risk_count / total_batches * 100 if total_batches > 0 else 0)}。
                {batch_risk_status}</p>
                {f"极高风险批次{risk_counts.get('极高风险', 0)}个，需要紧急处理。" if risk_counts.get('极高风险', 0) > 0 else ""}
            </div>
            """, unsafe_allow_html=True)

        # 高风险批次清库天数分析
        batch_clearance_fig = create_batch_clearance_chart(batch_analysis, "高风险批次清库天数分析")
        if batch_clearance_fig:
            st.plotly_chart(batch_clearance_fig, use_container_width=True)

            # 图表解读
            high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['高风险', '极高风险'])]
            avg_clearance_days = high_risk_batches['预计清库天数'].mean() if not high_risk_batches.empty else 0
            avg_age = high_risk_batches['库龄'].mean() if not high_risk_batches.empty else 0

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h4>📊 图表解读</h4>
                <p>高风险批次分析：共有{len(high_risk_batches)}个高风险或极高风险批次，平均库龄{avg_age:.1f}天，平均预计清库天数{avg_clearance_days:.1f}天。
                其中有{sum(high_risk_batches['库龄'] > 90)}个批次库龄超过90天，有{sum(high_risk_batches['预计清库天数'] > 180)}个批次预计需要超过半年才能销售完毕。
                建议优先处理库龄最长且清库天数最多的批次。</p>
            </div>
            """, unsafe_allow_html=True)

    # 预测与库存对比
    st.subheader("📊 库存与预测对比")

    forecast_vs_inventory = analysis_result.get('forecast_vs_inventory')
    if forecast_vs_inventory is not None and not forecast_vs_inventory.empty:
        # 库存与预测对比图
        fig = create_inventory_forecast_chart(forecast_vs_inventory, "库存与预测对比")
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            # 图表解读
            status_counts = forecast_vs_inventory['预测库存状态'].value_counts().to_dict()
            low_forecast = status_counts.get('库存不足', 0)
            normal_forecast = status_counts.get('库存适中', 0)
            high_forecast = status_counts.get('库存过剩', 0)

            total_forecast = low_forecast + normal_forecast + high_forecast

            st.markdown(f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid {COLORS['success']}; 
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
                st.dataframe(
                    high_risk_products[['产品代码', '描述', '现有库存', '月平均销量', '清库周期(月)', '库存覆盖天数']])
        else:
            st.success("当前筛选条件下无高风险产品，库存管理良好！")

    # 库存洞察总结
    st.subheader("💡 库存洞察总结")

    # 生成综合评价
    if health_distribution and risk_distribution:
        healthy_percentage = healthy_count / total_count * 100 if total_count > 0 else 0
        high_risk_percentage = high_risk / total_risk * 100 if total_risk > 0 else 0

        # 批次级分析的综合评价
        batch_insight = ""
        if batch_analysis is not None and not batch_analysis.empty:
            high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]
            high_risk_batch_count = len(high_risk_batches)
            total_batch_count = len(batch_analysis)

            batch_insight = f"批次级分析发现{high_risk_batch_count}个高风险批次，占比{format_percentage(high_risk_batch_count / total_batch_count * 100 if total_batch_count > 0 else 0)}。"

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

        # 获取库存健康状况文本
        def get_health_status_text(percentage):
            if percentage >= 70:
                return "非常健康"
            elif percentage >= 60:
                return "比较健康"
            elif percentage >= 50:
                return "一般"
            else:
                return "需要改善"

        # 获取风险状况文本
        def get_risk_status_text(percentage):
            if percentage <= 5:
                return "风险极低"
            elif percentage <= 10:
                return "风险较低"
            elif percentage <= 20:
                return "风险中等"
            else:
                return "风险较高"

        # 获取批次库龄状况文本
        def get_batch_status_text(batch_data):
            if batch_data is None or batch_data.empty:
                return "无法评估"

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

        # 获取预测匹配状况
        def get_forecast_status_text(forecast_data):
            if forecast_data is None or forecast_data.empty:
                return "无法评估"

            status_counts = forecast_data['预测库存状态'].value_counts().to_dict()
            low_forecast = status_counts.get('库存不足', 0)
            normal_forecast = status_counts.get('库存适中', 0)
            high_forecast = status_counts.get('库存过剩', 0)

            total_forecast = low_forecast + normal_forecast + high_forecast
            normal_ratio = normal_forecast / total_forecast if total_forecast > 0 else 0

            if normal_ratio > 0.7:
                return "库存与预测需求匹配度高"
            elif low_forecast > high_forecast:
                return f"有{low_forecast}个产品库存可能不足，存在缺货风险"
            elif high_forecast > low_forecast:
                return f"有{high_forecast}个产品库存过剩，存在积压风险"
            else:
                return "库存与预测需求匹配度一般"

        st.markdown(f"""
        <div style="background-color: rgba(31, 56, 103, 0.1); border-left: 4px solid {COLORS['primary']}; 
                    padding: 1rem; border-radius: 0.5rem;">
            <h4>📋 库存管理总评</h4>
            <p><strong>总体状况：</strong><span style="color: {status_color};">{status}</span></p>
            <p><strong>健康库存情况：</strong>{format_percentage(healthy_percentage)} ({get_health_status_text(healthy_percentage)})</p>
            <p><strong>积压风险情况：</strong>{format_percentage(high_risk_percentage)} ({get_risk_status_text(high_risk_percentage)})</p>
            <p><strong>批次库龄情况：</strong>{get_batch_status_text(batch_analysis)}</p>
            <p><strong>预测匹配情况：</strong>{get_forecast_status_text(forecast_vs_inventory)}</p>
            <p><strong>综合评价：</strong>{comment} {batch_insight}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("无法生成库存洞察总结，数据不完整")

    # 添加页脚
    st.markdown("""
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
        <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
        <p>每周一17:00更新数据</p>
    </div>
    """, unsafe_allow_html=True)


# 执行主函数
if __name__ == "__main__":
    main()