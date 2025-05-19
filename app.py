# app.py
# 主应用入口，包含登录验证和页面导航

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# 导入配置和工具
from config import PASSWORD, DATA_PATHS
from utils.data_loader import load_all_data
from utils.helpers import create_metric_card, get_current_date_info

# 导入各分析页面
from pages.overview import show_overview_page
from pages.sales_page import show_sales_page
from pages.customer_page import show_customer_page
from pages.product_page import show_product_page
from pages.inventory_page import show_inventory_page
from pages.material_page import show_material_page
from pages.new_product_page import show_new_product_page

# 配置页面
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f5;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4c78a8;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #4c78a8;
    }
    .metric-card {
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# 用户验证函数
def authenticate(password):
    return password == PASSWORD

# 会话状态管理
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = 0
    
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'region': None,
        'sales_person': None,
        'customer': None,
        'product': None,
        'date_range': None
    }

# 主应用逻辑
def main():
    # 登录页面
    if not st.session_state.authenticated:
        st.title("销售数据分析仪表盘")
        st.write("请输入密码进行访问:")
        password = st.text_input("密码", type="password")
        
        if st.button("登录"):
            if authenticate(password):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("密码错误，请重试!")
                
    # 主应用页面
    else:
        # 侧边栏
        with st.sidebar:
            st.title("销售数据分析仪表盘")
            
            # 显示当前日期和最近更新时间
            current_year, current_month, is_year_end = get_current_date_info()
            st.write(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
            st.write("上次更新: 每周一17:00更新")
            
            # 数据加载进度条
            if not st.session_state.data_loaded:
                with st.spinner("正在加载数据..."):
                    progress_bar = st.progress(0)
                    
                    # 模拟数据加载进度
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # 加载所有数据
                    try:
                        data = load_all_data(DATA_PATHS)
                        st.session_state.data = data
                        st.session_state.data_loaded = True
                        st.success("数据加载完成!")
                    except Exception as e:
                        st.error(f"数据加载失败: {str(e)}")
                        return
            
            # 筛选器
            st.subheader("数据筛选")
            
            # 区域筛选
            regions = ['全部'] + sorted(st.session_state.data['sales_data']['所属区域'].unique().tolist())
            selected_region = st.selectbox("选择区域", regions)
            if selected_region != '全部':
                st.session_state.filters['region'] = selected_region
            else:
                st.session_state.filters['region'] = None
            
            # 销售人员筛选
            sales_persons = ['全部'] + sorted(st.session_state.data['sales_data']['申请人'].unique().tolist())
            selected_sales_person = st.selectbox("选择销售人员", sales_persons)
            if selected_sales_person != '全部':
                st.session_state.filters['sales_person'] = selected_sales_person
            else:
                st.session_state.filters['sales_person'] = None
            
            # 客户筛选
            # 只显示状态为"正常"的客户
            normal_customers = st.session_state.data['customer_relations'][
                st.session_state.data['customer_relations']['状态'] == '正常'
            ]['客户'].unique().tolist()
            
            customers = ['全部'] + sorted(normal_customers)
            selected_customer = st.selectbox("选择客户", customers)
            if selected_customer != '全部':
                st.session_state.filters['customer'] = selected_customer
            else:
                st.session_state.filters['customer'] = None
            
            # 产品筛选
            # 只显示产品代码文件中的产品
            allowed_products = st.session_state.data['product_codes']
            product_names = (
                st.session_state.data['sales_data']
                [st.session_state.data['sales_data']['产品代码'].isin(allowed_products)]
                ['产品简称'].unique().tolist()
            )
            
            products = ['全部'] + sorted(product_names)
            selected_product = st.selectbox("选择产品", products)
            if selected_product != '全部':
                st.session_state.filters['product'] = selected_product
            else:
                st.session_state.filters['product'] = None
            
            # 时间范围筛选
            min_date = pd.to_datetime(st.session_state.data['sales_data']['发运月份'].min())
            max_date = pd.to_datetime(st.session_state.data['sales_data']['发运月份'].max())
            
            date_range = st.date_input(
                "选择时间范围",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date,
                format="YYYY-MM"
            )
            
            if len(date_range) == 2:
                st.session_state.filters['date_range'] = date_range
            
            # 重置筛选器按钮
            if st.button("重置筛选器"):
                st.session_state.filters = {
                    'region': None,
                    'sales_person': None,
                    'customer': None,
                    'product': None,
                    'date_range': None
                }
                st.experimental_rerun()
        
        # 主内容区
        # 使用选项卡显示不同分析页面
        tabs = st.tabs([
            "总览", "销售分析", "客户分析", 
            "产品分析", "库存分析", "物料分析", "新品分析"
        ])
        
        # 根据选择的选项卡显示对应页面
        with tabs[0]:
            show_overview_page(st.session_state.data, st.session_state.filters)
            
        with tabs[1]:
            show_sales_page(st.session_state.data, st.session_state.filters)
            
        with tabs[2]:
            show_customer_page(st.session_state.data, st.session_state.filters)
            
        with tabs[3]:
            show_product_page(st.session_state.data, st.session_state.filters)
            
        with tabs[4]:
            show_inventory_page(st.session_state.data, st.session_state.filters)
            
        with tabs[5]:
            show_material_page(st.session_state.data, st.session_state.filters)
            
        with tabs[6]:
            show_new_product_page(st.session_state.data, st.session_state.filters)

# 运行应用
if __name__ == "__main__":
    main()