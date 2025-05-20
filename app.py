# app.py - 极简路由器，只负责导航和全局样式
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

# 全局样式 - 从sales_dashboard.py提取的完整样式系统
st.markdown("""
<style>
    /* 主体样式 */
    .main { 
        background-color: #f8f9fa; 
    }

    /* 标题样式 */
    .main-header {
        font-size: 2rem;
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* 卡片样式 */
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #444444;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f3867;
    }
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .card-text {
        font-size: 0.9rem;
        color: #6c757d;
    }

    /* 警告框样式 */
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
    }
    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
    }
    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
    }
    .alert-info {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 0.5rem solid #2196F3;
    }

    /* 子标题样式 */
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f3867;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* 图表解释样式 */
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 0.9rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border-left: 0.5rem solid #4CAF50;
    }

    /* 按钮样式 */
    .stButton > button {
        background-color: #1f3867;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #4c78a8;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }

    /* 导航按钮特殊样式 */
    .nav-button {
        background-color: #ffffff;
        border: 2px solid #1f3867;
        color: #1f3867;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        text-align: left;
        font-weight: bold;
        transition: all 0.3s;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .nav-button:hover {
        background-color: #1f3867;
        color: white;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }
    .nav-button.active {
        background-color: #1f3867;
        color: white;
    }

    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }

    /* 登录页面样式 */
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }

    /* 页面进度指示器 */
    .progress-indicator {
        background-color: rgba(31, 56, 103, 0.1);
        border-left: 4px solid #1f3867;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def login_page():
    """登录页面"""
    st.markdown('<div class="main-header">销售仪表盘登录</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <h2 style='text-align: center; color: #1f3867; margin-bottom: 2rem;'>欢迎使用</h2>
        </div>
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


def create_navigation():
    """创建导航菜单"""
    # 初始化当前页面状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'overview'

    # 页面配置
    pages = {
        'overview': {
            'title': '📊 总览',
            'description': '业务概览和关键指标',
            'module': 'overview_page',
            'function': 'show_overview'
        },
        'sales': {
            'title': '📈 销售分析',
            'description': '销售数据深度分析',
            'module': 'sales_page',
            'function': 'show_sales_analysis'
        },
        'customer': {
            'title': '👥 客户分析',
            'description': '客户细分和依赖度分析',
            'module': 'customer_page',
            'function': 'show_customer_analysis'
        },
        'product': {
            'title': '📦 产品分析',
            'description': 'BCG矩阵和产品组合',
            'module': 'product_page',
            'function': 'show_product_analysis'
        },
        'inventory': {
            'title': '📋 库存分析',
            'description': '库存状态和风险评估',
            'module': 'inventory_page',
            'function': 'show_inventory_analysis'
        },
        'material': {
            'title': '🔧 物料分析',
            'description': '物料效率和供应风险',
            'module': 'material_page',
            'function': 'show_material_analysis'
        },
        'new_product': {
            'title': '🆕 新品分析',
            'description': '新品表现和市场渗透',
            'module': 'new_product_page',
            'function': 'show_new_product_analysis'
        }
    }

    # 侧边栏导航
    with st.sidebar:
        # 品牌标识
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1f3867; margin-bottom: 0.5rem;">📊</h1>
            <h2 style="color: #1f3867; margin-bottom: 0;">销售仪表盘</h2>
            <p style="color: #6c757d; font-size: 0.9rem;">Sales Dashboard v2.0</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 导航按钮
        st.markdown("### 🧭 选择页面")

        for page_key, page_info in pages.items():
            # 创建按钮，显示活跃状态
            button_class = "active" if st.session_state.current_page == page_key else ""

            if st.button(
                    f"{page_info['title']}",
                    key=f"nav_{page_key}",
                    help=page_info['description'],
                    use_container_width=True
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # 系统信息
        st.markdown("""
        <div class="progress-indicator">
            <h4 style="color: #1f3867; margin-bottom: 0.5rem;">📊 系统状态</h4>
            <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">
                • 数据更新：实时<br>
                • 缓存状态：正常<br>
                • 页面加载：快速
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 版本信息
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; color: #6c757d; font-size: 0.8rem;'>
            版本 v2.0.0 | © 2025<br>
            数据驱动决策
        </div>
        """, unsafe_allow_html=True)

    return pages


def load_page(pages):
    """动态加载当前页面"""
    current_page = st.session_state.current_page

    if current_page not in pages:
        st.error(f"页面 '{current_page}' 不存在")
        return

    page_info = pages[current_page]

    try:
        # 显示页面加载进度
        with st.spinner(f"正在加载 {page_info['title']}..."):
            # 动态导入页面模块
            module_name = f"pages.{page_info['module']}"
            module = __import__(module_name, fromlist=[page_info['function']])

            # 调用页面函数
            page_function = getattr(module, page_info['function'])
            page_function()

    except ImportError as e:
        st.error(f"无法导入页面模块 '{page_info['module']}'")
        st.error(f"错误详情：{str(e)}")
        st.info("请确保在 pages/ 目录下存在对应的页面文件")

    except AttributeError as e:
        st.error(f"页面模块 '{page_info['module']}' 中未找到函数 '{page_info['function']}'")
        st.error(f"错误详情：{str(e)}")

    except Exception as e:
        st.error(f"加载页面时发生错误：{str(e)}")
        st.error("请检查页面代码是否正确")


def main_app():
    """主应用界面"""
    # 创建导航
    pages = create_navigation()

    # 主内容区域
    with st.container():
        # 加载选中的页面
        load_page(pages)


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