# app.py - 极简主应用文件
import streamlit as st
import time
from config import PASSWORD

# 配置页面
st.set_page_config(
    page_title="销售仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def login_page():
    """登录页面"""
    st.markdown("<h1 style='text-align: center;'>销售仪表盘登录</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 2rem; border-radius: 0.5rem; 
                    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);'>
            <h2 style='text-align: center; margin-bottom: 2rem;'>欢迎使用</h2>
        """, unsafe_allow_html=True)

        password = st.text_input("请输入密码", type="password", key="password_input")

        if st.button("登录", use_container_width=True):
            if password == PASSWORD:
                st.session_state.logged_in = True
                st.success("登录成功！")
                time.sleep(1)
                st.rerun()
            else:
                st.error("密码错误，请重试")

        st.markdown("</div>", unsafe_allow_html=True)


def main_app():
    """主应用界面"""
    # 侧边栏导航
    with st.sidebar:
        st.image("https://img.icons8.com/color/48/000000/dashboard.png", width=50)
        st.title("销售仪表盘")

        # 页面选择
        pages = {
            "总览": "overview_page",
            "销售分析": "sales_page",
            "客户分析": "customer_page",
            "产品分析": "product_page",
            "库存分析": "inventory_page",
            "物料分析": "material_page",
            "新品分析": "new_product_page"
        }

        selected_page = st.radio("选择页面", list(pages.keys()))

        st.markdown("---")

        # 全局筛选器
        st.subheader("筛选条件")

        # 大区筛选（这里只是占位，实际数据加载在各页面内）
        st.selectbox("大区", ["全部", "华东", "华南", "华北"], key="filter_region")
        st.selectbox("人员", ["全部"], key="filter_person")
        st.selectbox("客户", ["全部"], key="filter_customer")

        st.markdown("---")
        st.markdown("<div style='text-align: center;'>版本 v2.0.0 | © 2025</div>",
                    unsafe_allow_html=True)

    # 动态导入并显示页面
    page_module = pages[selected_page]

    if page_module == "overview_page":
        from pages.overview_page import show_overview
        show_overview()
    elif page_module == "sales_page":
        from pages.sales_page import show_sales_analysis
        show_sales_analysis()
    elif page_module == "customer_page":
        from pages.customer_page import show_customer_analysis
        show_customer_analysis()
    elif page_module == "product_page":
        from pages.product_page import show_product_analysis
        show_product_analysis()
    elif page_module == "inventory_page":
        from pages.inventory_page import show_inventory_analysis
        show_inventory_analysis()
    elif page_module == "material_page":
        from pages.material_page import show_material_analysis
        show_material_analysis()
    elif page_module == "new_product_page":
        from pages.new_product_page import show_new_product_analysis
        show_new_product_analysis()


def main():
    """主函数"""
    # 初始化登录状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 检查登录状态
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()