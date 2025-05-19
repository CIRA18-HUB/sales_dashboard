# simplified_app.py
# 极简化的应用入口，只包含登录页面

import streamlit as st
import os

# 简单的页面配置
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide"
)

# 极简CSS - 只保留登录页面需要的样式
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .login-container { 
        margin-top: 20vh; 
        text-align: center;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    }
    .stButton>button {
        background-color: #4c78a8;
        color: white;
        font-size: 16px;
        padding: 8px 16px;
        border-radius: 4px;
        border: none;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 安全地加载密码
def get_password():
    """只读取配置文件中的密码"""
    try:
        from config import PASSWORD
        return PASSWORD
    except ImportError:
        st.error("无法加载配置文件")
        return None

# 简化的验证函数
def authenticate(password):
    """验证用户密码"""
    correct_password = get_password()
    return password == correct_password

# 主应用逻辑
if not st.session_state.authenticated:
    # 极简登录页面
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("销售数据分析仪表盘")
    st.write("请输入密码进行访问:")
    password = st.text_input("密码", type="password")
    
    if st.button("登录"):
        if authenticate(password):
            st.session_state.authenticated = True
            st.rerun()  # 使用rerun以兼容所有版本的Streamlit
        else:
            st.error("密码错误，请重试!")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # 已认证，切换到主页面
    # 导入app模块，但不执行其全局代码
    import sys
    import importlib.util
    
    spec = importlib.util.spec_from_file_location("app", "app.py")
    app = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app
    spec.loader.exec_module(app)
    
    # 运行主应用
    app.main()