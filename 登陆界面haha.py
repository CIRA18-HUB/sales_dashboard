# app.py - 完整版本（包含所有JavaScript动画效果）
import streamlit as st
from datetime import datetime
import os

# 设置页面配置
st.set_page_config(
    page_title="销售数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 超强力隐藏Streamlit默认元素
hide_elements = """
<style>
    /* 隐藏所有可能的Streamlit默认元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp > header {display: none !important;}

    /* 强力隐藏侧边栏中的应用名称 */
    .stSidebar > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }

    /* 隐藏侧边栏顶部的应用标题 */
    .stSidebar .element-container:first-child {
        display: none !important;
    }

    /* 通过多种方式隐藏应用标题 */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 如果以上都无效，至少让它不可见 */
    .stSidebar > div:first-child {
        background: transparent !important;
        border: none !important;
    }

    .stSidebar .stSelectbox {
        display: none !important;
    }
</style>

<script>
// JavaScript强制隐藏
setTimeout(() => {
    // 隐藏所有可能的标题元素
    const elementsToHide = [
        'header',
        '[data-testid="stHeader"]',
        '[data-testid="stSidebarNav"]',
        '.stSidebar .stSelectbox',
        '.stSidebar > div:first-child > div:first-child'
    ];

    elementsToHide.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.opacity = '0';
                el.style.height = '0';
                el.style.overflow = 'hidden';
            }
        });
    });
}, 100);

// 持续监控和隐藏
setInterval(() => {
    const appName = document.querySelector('.stSidebar');
    if (appName) {
        const firstChild = appName.firstElementChild;
        if (firstChild && firstChild.textContent.includes('app')) {
            firstChild.style.display = 'none';
        }
    }
}, 500);
</script>
"""

st.markdown(hide_elements, unsafe_allow_html=True)

# 完整CSS样式（包含所有动画）
complete_css_with_animations = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* 主容器背景 + 动画 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景波纹效果 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 60%);
        animation: waveMove 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes waveMove {
        0%, 100% { 
            background-size: 200% 200%, 150% 150%, 300% 300%;
            background-position: 0% 0%, 100% 100%, 50% 50%; 
        }
        33% { 
            background-size: 300% 300%, 200% 200%, 250% 250%;
            background-position: 100% 0%, 0% 50%, 80% 20%; 
        }
        66% { 
            background-size: 250% 250%, 300% 300%, 200% 200%;
            background-position: 50% 100%, 50% 0%, 20% 80%; 
        }
    }

    /* 浮动粒子效果 */
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.2), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.3), transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: particleFloat 20s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes particleFloat {
        0% { transform: translateY(100vh) translateX(0); }
        100% { transform: translateY(-100vh) translateX(100px); }
    }

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(5px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 侧边栏美化 */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }

    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .stSidebar > div:first-child {
        background: transparent;
        padding-top: 1rem;
    }

    /* 侧边栏标题 */
    .stSidebar .stMarkdown h3 {
        color: #2d3748;
        font-weight: 600;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titlePulse 3s ease-in-out infinite;
    }

    @keyframes titlePulse {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.2); }
    }

    /* 侧边栏按钮 */
    .stSidebar .stButton > button {
        width: 100%;
        background: transparent;
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        color: #4a5568;
        text-align: left;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.9rem;
        position: relative;
        overflow: hidden;
    }

    .stSidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s ease;
    }

    .stSidebar .stButton > button:hover::before {
        left: 100%;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: #667eea;
        color: #667eea;
        transform: translateX(8px) scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    /* 登录容器 */
    .login-container {
        animation: slideUpBounce 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes slideUpBounce {
        0% {
            opacity: 0;
            transform: translateY(100px) scale(0.8) rotateX(30deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-10px) scale(1.05) rotateX(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    /* 输入框动画 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(229, 232, 240, 0.8);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        transform: translateY(-3px) scale(1.02);
        background: rgba(255, 255, 255, 1);
    }

    /* 按钮动画 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transition: width 0.6s, height 0.6s, top 0.6s, left 0.6s;
        transform: translate(-50%, -50%);
    }

    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
    }

    /* 消息动画 */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        animation: alertSlideIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes alertSlideIn {
        0% {
            opacity: 0;
            transform: translateY(-30px) scale(0.8);
        }
        60% {
            opacity: 1;
            transform: translateY(5px) scale(1.05);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
    }

    .stError {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }
</style>
"""

st.markdown(complete_css_with_animations, unsafe_allow_html=True)

# JavaScript组件 - 数字滚动和其他交互效果
javascript_animations = """
<script>
// 数字滚动动画函数
function animateCounters() {
    const counters = document.querySelectorAll('.counter-number');

    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target + (counter.getAttribute('data-suffix') || '');
                clearInterval(timer);
            } else {
                counter.textContent = Math.ceil(current) + (counter.getAttribute('data-suffix') || '');
            }
        }, 40);
    });
}

// 页面加载后执行动画
setTimeout(() => {
    animateCounters();
}, 1000);

// 创建浮动几何图形
function createFloatingShapes() {
    const shapesContainer = document.createElement('div');
    shapesContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 2;
    `;

    const shapes = ['▲', '■', '●', '◆', '★'];
    const colors = ['rgba(255,255,255,0.1)', 'rgba(102,126,234,0.1)', 'rgba(129,236,236,0.1)'];

    for (let i = 0; i < 15; i++) {
        const shape = document.createElement('div');
        shape.textContent = shapes[Math.floor(Math.random() * shapes.length)];
        shape.style.cssText = `
            position: absolute;
            font-size: ${Math.random() * 20 + 10}px;
            color: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: shapeFloat ${Math.random() * 10 + 8}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        shapesContainer.appendChild(shape);
    }

    document.body.appendChild(shapesContainer);
}

// 形状浮动动画CSS
const shapeAnimationCSS = `
    @keyframes shapeFloat {
        0%, 100% { 
            transform: translateY(0) rotate(0deg) scale(1);
            opacity: 0.3;
        }
        25% { 
            transform: translateY(-30px) rotate(90deg) scale(1.2);
            opacity: 0.6;
        }
        50% { 
            transform: translateY(-60px) rotate(180deg) scale(0.8);
            opacity: 1;
        }
        75% { 
            transform: translateY(-30px) rotate(270deg) scale(1.1);
            opacity: 0.6;
        }
    }
`;

// 添加形状动画CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = shapeAnimationCSS;
document.head.appendChild(styleSheet);

// 执行函数
setTimeout(() => {
    createFloatingShapes();
}, 2000);

// 添加鼠标跟随效果
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

function animateCursor() {
    cursorX += (mouseX - cursorX) * 0.1;
    cursorY += (mouseY - cursorY) * 0.1;

    // 更新背景渐变跟随鼠标
    const main = document.querySelector('.main');
    if (main) {
        const xPercent = (cursorX / window.innerWidth) * 100;
        const yPercent = (cursorY / window.innerHeight) * 100;

        main.style.background = `
            radial-gradient(circle at ${xPercent}% ${yPercent}%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            linear-gradient(135deg, #667eea 0%, #764ba2 100%)
        `;
    }

    requestAnimationFrame(animateCursor);
}

animateCursor();
</script>
"""

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 登录界面
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container" style="max-width: 450px; margin: 3rem auto; padding: 3rem 2.5rem; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.2); text-align: center;">
            <div style="font-size: 3rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; animation: titlePulse 2s infinite;">📊</div>
            <h2 style="font-size: 1.8rem; color: #2d3748; margin-bottom: 0.5rem; font-weight: 600;">销售数据分析仪表盘</h2>
            <p style="color: #718096; font-size: 0.9rem; margin-bottom: 2rem;">洞察业务趋势，发现增长机会</p>
        </div>
        """, unsafe_allow_html=True)

        # 登录表单
        with st.form("login_form"):
            st.markdown("#### 🔐 请输入访问密码")
            password = st.text_input("密码", type="password", placeholder="请输入访问密码")
            submit_button = st.form_submit_button("登 录", use_container_width=True)

        if submit_button:
            if password == 'SAL!2025':
                st.session_state.authenticated = True
                st.success("🎉 登录成功！正在进入仪表盘...")
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试！")

        # 更新提示
        st.markdown("""
        <div style="text-align: center; margin: 3rem auto; max-width: 600px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem; box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); animation: updateBadgeGlow 2s ease-in-out infinite alternate; position: relative; overflow: hidden;">
                🕐 数据每周一 17:00 自动更新
            </div>
        </div>

        <style>
        @keyframes updateBadgeGlow {
            from { box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3); }
            to { box-shadow: 0 5px 30px rgba(116, 185, 255, 0.6); }
        }
        </style>
        """, unsafe_allow_html=True)

    st.stop()

# 认证成功后的主页面
with st.sidebar:
    st.markdown("### 📊 销售数据分析仪表盘")
    st.markdown("#### 🏠 主要功能")

    if st.button("🏠 欢迎页面", use_container_width=True):
        st.session_state.current_page = "welcome"

    st.markdown("---")
    st.markdown("#### 📈 分析模块")

    if st.button("📦 产品组合分析", use_container_width=True):
        st.switch_page("pages/产品组合分析.py")

    if st.button("📊 预测库存分析", use_container_width=True):
        st.switch_page("pages/预测库存分析.py")

    if st.button("👥 客户依赖分析", use_container_width=True):
        st.switch_page("pages/客户依赖分析.py")

    if st.button("🎯 销售达成分析", use_container_width=True):
        st.switch_page("pages/销售达成分析.py")

    st.markdown("---")
    st.markdown("#### 👤 用户信息")
    st.info("**管理员**  \n系统管理员")

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# 主内容区
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem; position: relative; z-index: 10;">
    <h1 style="font-size: 3rem; color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); margin-bottom: 1rem; font-weight: 700; animation: titleGlowPulse 4s ease-in-out infinite;">
        📊 销售数据分析仪表盘
    </h1>
    <p style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 2rem; animation: subtitleFloat 6s ease-in-out infinite;">欢迎使用销售数据分析仪表盘，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
</div>

<style>
@keyframes titleGlowPulse {
    0%, 100% { 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.5);
        transform: scale(1);
    }
    50% { 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 255, 255, 0.9);
        transform: scale(1.02);
    }
}

@keyframes subtitleFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
</style>
""", unsafe_allow_html=True)

# 数据统计展示 - 带数字滚动效果
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.1s both;">
        <span class="counter-number" data-target="1000" data-suffix="+" style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">0+</span>
        <div style="color: #4a5568; font-size: 0.9rem;">数据分析</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.2s both;">
        <span class="counter-number" data-target="4" style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">0</span>
        <div style="color: #4a5568; font-size: 0.9rem;">分析模块</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.3s both;">
        <span class="counter-number" data-target="24" style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">0</span>
        <div style="color: #4a5568; font-size: 0.9rem;">小时监控</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: all 0.4s ease; animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.4s both;">
        <span class="counter-number" data-target="99" data-suffix="%" style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; display: block;">0%</span>
        <div style="color: #4a5568; font-size: 0.9rem;">准确率</div>
    </div>

    <style>
    @keyframes cardSlideUpStagger {
        0% {
            opacity: 0;
            transform: translateY(60px) scale(0.8) rotateX(30deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-10px) scale(1.05) rotateX(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 功能模块介绍
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin-bottom: 2rem; animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.2s both; position: relative; overflow: hidden; transition: all 0.5s ease;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconColorShift 4s ease-in-out infinite; display: block;">📦</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">产品组合分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
        </p>
    </div>

    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.6s both; position: relative; overflow: hidden; transition: all 0.5s ease;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconColorShift 4s ease-in-out infinite; display: block;">👥</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">客户依赖分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin-bottom: 2rem; animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.4s both; position: relative; overflow: hidden; transition: all 0.5s ease;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconColorShift 4s ease-in-out infinite; display: block;">📊</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">预测库存分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
        </p>
    </div>

    <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.8s both; position: relative; overflow: hidden; transition: all 0.5s ease;">
        <span style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2, #81ecec); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: iconColorShift 4s ease-in-out infinite; display: block;">🎯</span>
        <h3 style="font-size: 1.4rem; color: #2d3748; margin-bottom: 1rem; font-weight: 600;">销售达成分析</h3>
        <p style="color: #4a5568; line-height: 1.6;">
            监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
        </p>
    </div>
    """, unsafe_allow_html=True)

# 更新提示和导航指引
st.markdown("""
<div style="text-align: center; margin: 3rem auto; max-width: 600px;">
    <div style="display: inline-block; background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%); color: white; padding: 1.2rem 2.5rem; border-radius: 30px; font-weight: 600; font-size: 1.1rem; animation: badgeGlowPulse 3s ease-in-out infinite, badgeFloat 5s ease-in-out infinite; position: relative; overflow: hidden;">
        🔄 数据每周一 17:00 自动更新
    </div>
</div>

<div style="text-align: center; color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; margin-top: 2rem; animation: bounceArrow 3s ease-in-out infinite;">
    👈 请使用左侧导航栏访问各分析页面
</div>

<div style="text-align: center; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
    <p>销售数据分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年5月</p>
    <p>每周一17:00更新数据 | 为您提供专业的数据洞察服务</p>
</div>

<style>
@keyframes featureCardFloat {
    0% {
        opacity: 0;
        transform: translateY(80px) scale(0.8) rotateX(45deg);
    }
    60% {
        opacity: 1;
        transform: translateY(-15px) scale(1.05) rotateX(-10deg);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1) rotateX(0deg);
    }
}

@keyframes iconColorShift {
    0%, 100% { 
        background-position: 0% 50%;
        filter: hue-rotate(0deg);
    }
    25% { 
        background-position: 50% 50%;
        filter: hue-rotate(90deg);
    }
    50% { 
        background-position: 100% 50%;
        filter: hue-rotate(180deg);
    }
    75% { 
        background-position: 50% 50%;
        filter: hue-rotate(270deg);
    }
}

@keyframes badgeGlowPulse {
    0%, 100% { 
        box-shadow: 0 5px 15px rgba(116, 185, 255, 0.3);
    }
    50% { 
        box-shadow: 0 10px 40px rgba(116, 185, 255, 0.8);
    }
}

@keyframes badgeFloat {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    33% { transform: translateY(-8px) rotate(1deg); }
    66% { transform: translateY(-12px) rotate(-1deg); }
}

@keyframes bounceArrow {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0) translateX(0); }
    10% { transform: translateY(-8px) translateX(-5px); }
    30% { transform: translateY(-5px) translateX(-8px); }
    40% { transform: translateY(-12px) translateX(-3px); }
    60% { transform: translateY(-8px) translateX(-6px); }
}
</style>
""", unsafe_allow_html=True)

# 添加JavaScript动画
st.markdown(javascript_animations, unsafe_allow_html=True)