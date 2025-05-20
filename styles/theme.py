# styles/theme.py
# 统一主题样式配置

import streamlit as st

# 主题颜色配置
THEME_COLORS = {
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

# 卡片翻转样式
FLIP_CARD_CSS = """
<style>
.flip-card {
    background-color: transparent;
    width: 100%;
    height: 250px;
    perspective: 1000px;
    margin-bottom: 1rem;
}

.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.6s;
    transform-style: preserve-3d;
    cursor: pointer;
}

.flip-card.flipped .flip-card-inner {
    transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    border-radius: 0.5rem;
    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.flip-card-front {
    background-color: white;
    color: #1f3867;
}

.flip-card-back {
    background-color: #f8f9fa;
    color: #1f3867;
    transform: rotateY(180deg);
    overflow-y: auto;
}

.flip-card-back.layer-3 {
    background-color: #e3f2fd;
}

.card-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #1f3867;
}

.card-value {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #1f3867;
}

.card-subtitle {
    font-size: 0.9rem;
    color: #6c757d;
    margin-bottom: 1rem;
}

.card-indicator {
    background-color: rgba(76, 120, 168, 0.1);
    color: #4c78a8;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.8rem;
    font-weight: bold;
}

.flip-indicator {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(31, 56, 103, 0.1);
    color: #1f3867;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.7rem;
}

.insight-box {
    background-color: rgba(76, 175, 80, 0.1);
    border-left: 0.5rem solid #4CAF50;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    text-align: left;
    font-size: 0.9rem;
    line-height: 1.5;
}

.deep-analysis-box {
    background-color: rgba(33, 150, 243, 0.1);
    border-left: 0.5rem solid #2196F3;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    text-align: left;
    font-size: 0.9rem;
    line-height: 1.5;
}

.action-box {
    background-color: rgba(255, 152, 0, 0.1);
    border-left: 0.5rem solid #FF9800;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    text-align: left;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* 移动端响应式设计 */
@media (max-width: 768px) {
    .flip-card {
        height: 200px;
    }
    
    .card-value {
        font-size: 1.5rem;
    }
    
    .card-title {
        font-size: 1rem;
    }
}

/* 图表容器样式 */
.chart-container {
    width: 100%;
    height: 300px;
    margin: 1rem 0;
}

/* 加载指示器 */
.loading-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    color: #1f3867;
}

.loading-spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #1f3867;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-right: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 侧边栏样式增强 */
.glossary-term {
    background-color: rgba(76, 120, 168, 0.1);
    border-radius: 0.25rem;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #4c78a8;
}

.glossary-term-title {
    font-weight: bold;
    color: #1f3867;
    margin-bottom: 0.25rem;
}

.glossary-term-desc {
    font-size: 0.85rem;
    color: #6c757d;
    line-height: 1.4;
}
</style>
"""

def apply_theme():
    """应用统一主题样式"""
    st.markdown(FLIP_CARD_CSS, unsafe_allow_html=True)
    
    # 设置页面配置
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    
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
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 0.5rem;
    }
    
    .stMultiSelect > div > div {
        background-color: white;
        border-radius: 0.5rem;
    }
    
    .stDateInput > div > div {
        background-color: white;
        border-radius: 0.5rem;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: white;
    }
    
    /* 标题样式 */
    h1 {
        color: #1f3867;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #1f3867;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #1f3867;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f1f3f5;
        border-radius: 4px 4px 0 0;
        color: #1f3867;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f3867;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def get_color_palette():
    """获取图表颜色调色板"""
    return [
        '#1f3867',  # 主色
        '#4c78a8',  # 次色  
        '#4CAF50',  # 绿色
        '#FF9800',  # 橙色
        '#2196F3',  # 蓝色
        '#9C27B0',  # 紫色
        '#607D8B',  # 蓝灰色
        '#795548'   # 棕色
    ]