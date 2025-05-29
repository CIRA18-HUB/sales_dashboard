# 登陆界面haha.py - 增强版登录界面（完整版 - 修复版）
import streamlit as st
from datetime import datetime
import time
import random
import math
from data_storage import storage

# 设置页面配置
st.set_page_config(
    page_title="Trolli SAL | 登录",
    page_icon="📊",
    layout="wide"
)

# 隐藏Streamlit默认元素
hide_elements = """
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# 【替换类别】enhanced_complete_css → fixed_enhanced_complete_css（修复版本）
fixed_enhanced_complete_css = """
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* 主容器背景 + 增强动画 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        position: relative;
        overflow: hidden;
    }

    /* 增强版动态背景波纹效果 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.6) 0%, transparent 60%),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(120, 119, 198, 0.4) 0%, transparent 70%),
            radial-gradient(circle at 70% 30%, rgba(182, 244, 146, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, rgba(255, 182, 193, 0.4) 0%, transparent 60%);
        animation: enhancedWaveMove 12s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes enhancedWaveMove {
        0%, 100% { 
            background-size: 200% 200%, 150% 150%, 300% 300%, 180% 180%, 220% 220%;
            background-position: 0% 0%, 100% 100%, 50% 50%, 20% 80%, 90% 10%; 
        }
        25% { 
            background-size: 300% 300%, 200% 200%, 250% 250%, 240% 240%, 160% 160%;
            background-position: 100% 0%, 0% 50%, 80% 20%, 70% 30%, 10% 90%; 
        }
        50% { 
            background-size: 250% 250%, 300% 300%, 200% 200%, 190% 190%, 280% 280%;
            background-position: 50% 100%, 50% 0%, 20% 80%, 90% 70%, 30% 20%; 
        }
        75% { 
            background-size: 320% 320%, 180% 180%, 270% 270%, 210% 210%, 200% 200%;
            background-position: 20% 70%, 80% 30%, 60% 10%, 40% 90%, 70% 50%; 
        }
    }

    /* 增强版浮动粒子效果 */  
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(3px 3px at 20px 30px, rgba(255,255,255,0.4), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.3), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.5), transparent),
            radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.3), transparent),
            radial-gradient(3px 3px at 160px 30px, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 200px 60px, rgba(182, 244, 146, 0.6), transparent),
            radial-gradient(2px 2px at 250px 90px, rgba(255, 182, 193, 0.5), transparent),
            radial-gradient(1px 1px at 300px 20px, rgba(255, 255, 255, 0.4), transparent);
        background-repeat: repeat;
        background-size: 300px 150px;
        animation: enhancedParticleFloat 25s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes enhancedParticleFloat {
        0% { transform: translateY(100vh) translateX(0) rotate(0deg); }
        25% { transform: translateY(75vh) translateX(50px) rotate(90deg); }
        50% { transform: translateY(50vh) translateX(-30px) rotate(180deg); }
        75% { transform: translateY(25vh) translateX(80px) rotate(270deg); }
        100% { transform: translateY(-100vh) translateX(120px) rotate(360deg); }
    }

    /* 主容器 */
    .block-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(8px);
        padding-top: 1rem;
        max-width: 100%;
    }

    /* 增强版登录容器 */
    .login-container {
        animation: enhancedSlideUpBounce 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
        z-index: 20;
    }

    @keyframes enhancedSlideUpBounce {
        0% {
            opacity: 0;
            transform: translateY(150px) scale(0.6) rotateX(45deg) rotateY(15deg);
        }
        40% {
            opacity: 0.8;
            transform: translateY(-30px) scale(1.1) rotateX(-10deg) rotateY(-8deg);
        }
        70% {
            opacity: 1;
            transform: translateY(15px) scale(0.95) rotateX(5deg) rotateY(3deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg) rotateY(0deg);
        }
    }

    /* 互动游戏元素 - 可爱飘浮图标 */
    .floating-icons {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 5;
    }

    .floating-icon {
        position: absolute;
        font-size: 1.5rem;
        animation: floatingIconMove 8s ease-in-out infinite;
        opacity: 0.7;
        cursor: pointer;
        pointer-events: auto;
        transition: all 0.3s ease;
    }

    .floating-icon:hover {
        transform: scale(1.5) rotate(360deg);
        opacity: 1;
        animation-play-state: paused;
    }

    .floating-icon:nth-child(1) { 
        top: 15%; left: 10%; 
        animation-delay: 0s;
        animation-duration: 6s;
    }
    .floating-icon:nth-child(2) { 
        top: 25%; right: 15%; 
        animation-delay: 1s;
        animation-duration: 8s;
    }
    .floating-icon:nth-child(3) { 
        top: 45%; left: 5%; 
        animation-delay: 2s;
        animation-duration: 7s;
    }
    .floating-icon:nth-child(4) { 
        top: 60%; right: 8%; 
        animation-delay: 3s;
        animation-duration: 9s;
    }
    .floating-icon:nth-child(5) { 
        top: 75%; left: 12%; 
        animation-delay: 4s;
        animation-duration: 5s;
    }
    .floating-icon:nth-child(6) { 
        top: 35%; right: 25%; 
        animation-delay: 2.5s;
        animation-duration: 6.5s;
    }

    @keyframes floatingIconMove {
        0%, 100% { 
            transform: translateY(0) translateX(0) rotate(0deg) scale(1);
        }
        25% { 
            transform: translateY(-20px) translateX(15px) rotate(90deg) scale(1.1);
        }
        50% { 
            transform: translateY(-10px) translateX(-10px) rotate(180deg) scale(0.9);
        }
        75% { 
            transform: translateY(-30px) translateX(20px) rotate(270deg) scale(1.2);
        }
    }

    /* 增强版输入框动画 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border: 3px solid rgba(229, 232, 240, 0.8);
        border-radius: 15px;
        padding: 1.2rem 1.5rem;
        font-size: 1.1rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 
            0 0 0 6px rgba(102, 126, 234, 0.15),
            0 10px 30px rgba(102, 126, 234, 0.3),
            inset 0 0 20px rgba(102, 126, 234, 0.1);
        transform: translateY(-5px) scale(1.03);
        background: rgba(255, 255, 255, 1);
        animation: inputGlow 2s ease-in-out infinite;
    }

    @keyframes inputGlow {
        0%, 100% { 
            box-shadow: 
                0 0 0 6px rgba(102, 126, 234, 0.15),
                0 10px 30px rgba(102, 126, 234, 0.3);
        }
        50% { 
            box-shadow: 
                0 0 0 8px rgba(102, 126, 234, 0.25),
                0 15px 40px rgba(102, 126, 234, 0.5);
        }
    }

    /* 超级增强版登录按钮动画 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1.2rem 2.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.4);
        transition: width 0.8s, height 0.8s, top 0.8s, left 0.8s;
        transform: translate(-50%, -50%);
    }

    .stButton > button::after {
        content: '✨';
        position: absolute;
        top: 50%;
        right: 20px;
        transform: translateY(-50%);
        opacity: 0;
        transition: all 0.3s ease;
    }

    .stButton > button:hover::after {
        opacity: 1;
        right: 15px;
        animation: sparkle 1s ease-in-out infinite;
    }

    @keyframes sparkle {
        0%, 100% { transform: translateY(-50%) scale(1) rotate(0deg); }
        50% { transform: translateY(-50%) scale(1.2) rotate(180deg); }
    }

    .stButton > button:active::before {
        width: 400px;
        height: 400px;
    }

    .stButton > button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 
            0 20px 50px rgba(102, 126, 234, 0.5),
            0 0 30px rgba(102, 126, 234, 0.3);
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4f9a 100%);
        animation: buttonPulse 1.5s ease-in-out infinite;
    }

    @keyframes buttonPulse {
        0%, 100% { 
            box-shadow: 
                0 20px 50px rgba(102, 126, 234, 0.5),
                0 0 30px rgba(102, 126, 234, 0.3);
        }
        50% { 
            box-shadow: 
                0 25px 60px rgba(102, 126, 234, 0.7),
                0 0 50px rgba(102, 126, 234, 0.5);
        }
    }

    /* 增强版消息动画 */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(15px);
        animation: enhancedAlertSlideIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
        overflow: hidden;
    }

    .stAlert::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s ease-in-out infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    @keyframes enhancedAlertSlideIn {
        0% {
            opacity: 0;
            transform: translateY(-50px) scale(0.8) rotateX(30deg);
        }
        40% {
            opacity: 0.8;
            transform: translateY(10px) scale(1.1) rotateX(-10deg);
        }
        70% {
            opacity: 1;
            transform: translateY(-5px) scale(0.95) rotateX(5deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
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

    /* 增强版主标题部分 */
    .main-title {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
        z-index: 10;
    }

    .main-title h1 {
        font-size: 3.5rem;
        color: white;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
        margin-bottom: 1rem;
        font-weight: 700;
        animation: enhancedTitleGlowPulse 4s ease-in-out infinite;
    }

    .main-title p {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 2rem;
        animation: enhancedSubtitleFloat 6s ease-in-out infinite;
    }

    @keyframes enhancedTitleGlowPulse {
        0%, 100% { 
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4), 0 0 30px rgba(255, 255, 255, 0.6);
            transform: scale(1);
        }
        25% { 
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4), 0 0 50px rgba(182, 244, 146, 0.8);
            transform: scale(1.02);
        }
        50% { 
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4), 0 0 60px rgba(255, 255, 255, 1);
            transform: scale(1.05);
        }
        75% { 
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4), 0 0 40px rgba(255, 182, 193, 0.9);
            transform: scale(1.02);
        }
    }

    @keyframes enhancedSubtitleFloat {
        0%, 100% { transform: translateY(0) scale(1); }
        33% { transform: translateY(-12px) scale(1.02); }
        66% { transform: translateY(-6px) scale(0.98); }
    }

    /* 可爱图标动画容器 */
    .cute-login-icon {
        font-size: 4rem;
        background: linear-gradient(45deg, #667eea, #764ba2, #81ecec, #fd79a8);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        animation: cuteIconColorShift 4s ease-in-out infinite, cuteIconBounce 2s ease-in-out infinite;
        display: block;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .cute-login-icon:hover {
        animation: cuteIconSpin 1s ease-in-out, cuteIconColorShift 4s ease-in-out infinite;
        transform: scale(1.2);
    }

    @keyframes cuteIconColorShift {
        0%, 100% { 
            background-position: 0% 50%;
            filter: hue-rotate(0deg);
        }
        25% { 
            background-position: 100% 50%;
            filter: hue-rotate(90deg);
        }
        50% { 
            background-position: 50% 100%;
            filter: hue-rotate(180deg);
        }
        75% { 
            background-position: 50% 0%;
            filter: hue-rotate(270deg);
        }
    }

    @keyframes cuteIconBounce {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-10px) scale(1.1); }
    }

    @keyframes cuteIconSpin {
        0% { transform: rotate(0deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1.2); }
    }

    /* 互动小游戏 - 点击效果 */
    .click-effect {
        position: absolute;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.8), transparent);
        pointer-events: none;
        animation: clickRipple 1s ease-out forwards;
    }

    @keyframes clickRipple {
        0% {
            transform: scale(0);
            opacity: 1;
        }
        100% {
            transform: scale(10);
            opacity: 0;
        }
    }

    /* 数字统计卡片样式 */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2rem;
        margin-bottom: 4rem;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        animation: cardSlideUpStagger 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    .stat-card:nth-child(1) { animation-delay: 0.1s; }
    .stat-card:nth-child(2) { animation-delay: 0.2s; }
    .stat-card:nth-child(3) { animation-delay: 0.3s; }
    .stat-card:nth-child(4) { animation-delay: 0.4s; }

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

    .stat-card:hover {
        animation: cardWiggle 0.6s ease-in-out;
        transform: scale(1.05);
    }

    @keyframes cardWiggle {
        0%, 100% { transform: rotate(0deg) scale(1.05); }
        25% { transform: rotate(2deg) scale(1.08); }
        75% { transform: rotate(-2deg) scale(1.08); }
    }

    .counter-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
        transition: all 0.3s ease;
        animation: numberSlideUp 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes numberSlideUp {
        0% {
            opacity: 0;
            transform: translateY(100%) scale(0.5) rotateX(90deg);
        }
        60% {
            opacity: 1;
            transform: translateY(-10%) scale(1.1) rotateX(-10deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    .counter-number.updating {
        animation: numberBounceUpdate 0.6s ease-out;
    }

    @keyframes numberBounceUpdate {
        0% { 
            transform: scale(1); 
            filter: brightness(1); 
        }
        30% { 
            transform: scale(1.2) translateY(-10px); 
            filter: brightness(1.4) hue-rotate(30deg); 
        }
        60% { 
            transform: scale(0.9) translateY(5px); 
            filter: brightness(1.2) hue-rotate(-15deg); 
        }
        100% { 
            transform: scale(1); 
            filter: brightness(1); 
        }
    }

    .counter-number.sparkle {
        animation: numberSparkle 0.8s ease-out;
    }

    @keyframes numberSparkle {
        0%, 100% { 
            background: linear-gradient(45deg, #667eea, #764ba2);
            text-shadow: none;
        }
        25% { 
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            text-shadow: 0 0 20px rgba(255, 107, 107, 0.8);
        }
        50% { 
            background: linear-gradient(45deg, #4ecdc4, #44e1ff);
            text-shadow: 0 0 25px rgba(78, 205, 196, 0.9);
        }
        75% { 
            background: linear-gradient(45deg, #96ceb4, #feca57);
            text-shadow: 0 0 20px rgba(150, 206, 180, 0.8);
        }
    }

    .stat-label {
        color: #4a5568;
        font-size: 0.9rem;
    }

    /* 功能模块介绍 */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 2rem;
        margin-bottom: 3rem;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: featureCardFloat 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
        overflow: hidden;
        transition: all 0.5s ease;
    }

    .feature-card:nth-child(1) { animation-delay: 0.2s; }
    .feature-card:nth-child(2) { animation-delay: 0.4s; }
    .feature-card:nth-child(3) { animation-delay: 0.6s; }
    .feature-card:nth-child(4) { animation-delay: 0.8s; }

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

    .feature-card:hover {
        animation: cardBounce 0.8s ease-in-out;
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
    }

    @keyframes cardBounce {
        0%, 100% { transform: translateY(-10px) scale(1.02); }
        25% { transform: translateY(-20px) scale(1.05); }
        50% { transform: translateY(-5px) scale(1.08); }
        75% { transform: translateY(-15px) scale(1.03); }
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #667eea, #764ba2, #81ecec);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: iconColorShift 4s ease-in-out infinite;
        display: block;
        transition: all 0.3s ease;
    }

    .feature-card:hover .feature-icon {
        animation: iconSpin 0.6s ease-in-out, iconColorShift 4s ease-in-out infinite;
    }

    @keyframes iconSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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

    .feature-title {
        font-size: 1.4rem;
        color: #2d3748;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .feature-description {
        color: #4a5568;
        line-height: 1.6;
    }

    /* 页脚 */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        margin-top: 3rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }

    .footer p {
        margin-bottom: 0.5rem;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title h1 {
            font-size: 2.5rem;
        }
        .main-title p {
            font-size: 1.1rem;
        }
        .floating-icon {
            font-size: 1.2rem;
        }
        .cute-login-icon {
            font-size: 3rem;
        }
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        .features-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        .counter-number {
            font-size: 2rem;
        }
    }

    @media (max-width: 480px) {
        .floating-icon {
            font-size: 1rem;
        }
        .cute-login-icon {
            font-size: 2.5rem;
        }
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""

st.markdown(fixed_enhanced_complete_css, unsafe_allow_html=True)

# 【保持类别】interactive_js（保持不变）
interactive_js = """
<script>
// 互动点击效果
document.addEventListener('click', function(e) {
    const effect = document.createElement('div');
    effect.className = 'click-effect';
    effect.style.left = e.clientX - 10 + 'px';
    effect.style.top = e.clientY - 10 + 'px';
    document.body.appendChild(effect);

    setTimeout(() => {
        effect.remove();
    }, 1000);
});

// 键盘彩蛋
document.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        const icons = document.querySelectorAll('.floating-icon');
        icons.forEach(icon => {
            icon.style.animationPlayState = 'paused';
            setTimeout(() => {
                icon.style.animationPlayState = 'running';
            }, 2000);
        });
    }
});

// 随机鼓励语句
const encouragements = [
    '🌟 你今天看起来很棒！',
    '💪 相信自己，你可以的！',
    '🎉 今天会是美好的一天！',
    '✨ 你的笑容很有感染力！',
    '🌈 保持积极的心态！'
];

function showRandomEncouragement() {
    const message = encouragements[Math.floor(Math.random() * encouragements.length)];
    console.log(message);
}

// 每30秒显示一次鼓励语句
setInterval(showRandomEncouragement, 30000);
</script>
"""

st.markdown(interactive_js, unsafe_allow_html=True)


# 【替换类别】会话状态初始化 → fixed_session_state_init（修复版本）
def fixed_session_state_init():
    """修复版本的会话状态初始化函数"""
    # 强制初始化所有必要的状态
    required_states = {
        'authenticated': False,
        'username': "",
        'user_role': "",
        'display_name': "",
        'login_attempts': 0,
        'page_loaded': False
    }

    for key, default_value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # 调试信息（可选，用于排查问题）
    # st.write(f"调试信息: authenticated={st.session_state.authenticated}")


# 调用修复版本的初始化函数
fixed_session_state_init()


# 【替换类别】认证状态检查 → fixed_authentication_check（修复版本）
def fixed_authentication_check():
    """修复版本的认证状态检查函数"""
    # 严格检查认证状态
    is_authenticated = (
            hasattr(st.session_state, 'authenticated') and
            st.session_state.authenticated is True and
            hasattr(st.session_state, 'username') and
            st.session_state.username != ""
    )
    return is_authenticated


# 【替换类别】动态统计数字初始化 → fixed_stats_initialization（修复版本）
def fixed_stats_initialization():
    """修复版本的动态统计数字初始化函数"""
    stats_keys = [
        'stats_initialized', 'stat1_value', 'stat2_value',
        'stat3_value', 'stat4_value', 'last_update'
    ]

    if not all(key in st.session_state for key in stats_keys):
        st.session_state.stats_initialized = False
        st.session_state.stat1_value = 1000
        st.session_state.stat2_value = 4
        st.session_state.stat3_value = 24
        st.session_state.stat4_value = 99
        st.session_state.last_update = time.time()


# 【替换类别】动态数字更新函数 → fixed_update_dynamic_stats（修复版本）
def fixed_update_dynamic_stats():
    """修复版本的动态数字更新函数"""
    current_time = time.time()
    time_elapsed = current_time - st.session_state.last_update

    # 每3秒更新一次
    if time_elapsed >= 3:
        # 数据分析 - 递增趋势
        st.session_state.stat1_value = 1000 + random.randint(0, 200) + int(math.sin(current_time * 0.1) * 100)

        # 分析模块 - 稳定变化
        st.session_state.stat2_value = 4 + random.randint(-1, 1)

        # 小时监控 - 周期性变化
        st.session_state.stat3_value = 24 + int(math.sin(current_time * 0.2) * 8)

        # 准确率 - 波动变化
        st.session_state.stat4_value = 95 + random.randint(0, 4) + int(math.sin(current_time * 0.15) * 3)

        st.session_state.last_update = current_time
        return True
    return False


# 【替换类别】登录处理函数 → fixed_login_handler（修复版本）
def fixed_login_handler(password):
    """修复版本的登录处理函数"""
    try:
        # 使用storage进行用户认证
        auth_result = storage.authenticate_user(password)

        if auth_result and auth_result.get('authenticated', False):
            # 成功登录，设置会话状态
            st.session_state.authenticated = True
            st.session_state.username = auth_result.get('username', '')
            st.session_state.user_role = auth_result.get('role', '')
            st.session_state.display_name = auth_result.get('display_name', '')
            st.session_state.login_attempts = 0

            # 显示成功消息
            st.success(f"🎉 登录成功！欢迎 {auth_result.get('display_name', '用户')}，正在进入仪表盘...")
            time.sleep(1)
            st.rerun()

        else:
            # 登录失败
            st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
            st.error("❌ 密码错误，请重试！")

    except Exception as e:
        st.error(f"❌ 登录过程中出现错误：{str(e)}")


# ================================
# 【替换类别】主要页面逻辑 → fixed_main_page_logic（修复版本）
# ================================



# 使用修复版本的认证检查
if fixed_authentication_check():
    # ================================
    # 🎯 登录成功后的欢迎页面
    # ================================

    # 初始化动态数字
    fixed_stats_initialization()

    # 更新动态数字
    is_updated = fixed_update_dynamic_stats()

    # 主标题
    st.markdown("""
    <div class="main-title">
        <h1>📊 Trolli SAL</h1>
        <p>欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
    </div>
    """, unsafe_allow_html=True)

    # 数据统计展示 - 带动态数字更新
    col1, col2, col3, col4 = st.columns(4)

    # 添加CSS类来触发动画
    update_class = "updating sparkle" if is_updated else ""

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat1_value}+</span>
            <div class="stat-label">数据分析</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat2_value}</span>
            <div class="stat-label">分析模块</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat3_value}</span>
            <div class="stat-label">小时监控</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="counter-number {update_class}">{st.session_state.stat4_value}%</span>
            <div class="stat-label">准确率</div>
        </div>
        """, unsafe_allow_html=True)

    # 功能模块介绍
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <h3 class="feature-title">产品组合分析</h3>
            <p class="feature-description">
                分析产品销售表现，包括BCG矩阵分析、产品生命周期管理，优化产品组合策略，提升整体盈利能力。
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">👥</span>
            <h3 class="feature-title">客户依赖分析</h3>
            <p class="feature-description">
                深入分析客户依赖度、风险评估、客户价值分布，识别关键客户群体，制定客户维护和风险控制策略。
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">预测库存分析</h3>
            <p class="feature-description">
                基于历史数据和趋势分析，预测未来库存需求，优化库存管理流程，降低运营成本，提高资金使用效率。
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3 class="feature-title">销售达成分析</h3>
            <p class="feature-description">
                监控销售目标达成情况，分析销售业绩趋势，识别销售瓶颈，为销售策略调整提供数据支持。
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 页脚
    st.markdown("""
    <div class="footer">
        <p>Trolli SAL | 版本 1.0.0 | 最后更新: 2025年5月</p>
        <p>数据更新截止到5月30日 | 将枯燥数据变好看</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加这行，阻止继续执行
    st.stop()

    # 自动刷新页面来实现动态效果
    if not st.session_state.stats_initialized:
        st.session_state.stats_initialized = True
        time.sleep(0.1)
        st.rerun()

    # 每3秒自动刷新页面
    time.sleep(3)
    st.rerun()

else:
    # ================================
    # 🔐 修复版登录界面
    # ================================


    # 飘浮可爱图标
    st.markdown("""
    <div class="floating-icons">
        <div class="floating-icon">🌟</div>
        <div class="floating-icon">✨</div>
        <div class="floating-icon">🎉</div>
        <div class="floating-icon">💫</div>
        <div class="floating-icon">🌈</div>
        <div class="floating-icon">🎨</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container" style="max-width: 500px; margin: 3rem auto; padding: 3.5rem 3rem; background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(25px); border-radius: 25px; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.3); text-align: center;">
            <div class="cute-login-icon">📊</div>
            <h2 style="font-size: 2rem; color: #2d3748; margin-bottom: 0.8rem; font-weight: 700;">Trolli SAL</h2>
            <p style="color: #718096; font-size: 1rem; margin-bottom: 2.5rem; line-height: 1.6;">欢迎使用Trolli SAL，本系统提供销售数据的多维度分析，帮助您洞察业务趋势、发现增长机会</p>
        </div>
        """, unsafe_allow_html=True)

        # 修复版登录表单
        with st.form("login_form"):
            st.markdown("#### 🔐 请输入访问密码")
            password = st.text_input("密码", type="password", placeholder="请输入访问密码")
            submit_button = st.form_submit_button("🚀 开始分析之旅", use_container_width=True)

        if submit_button:
            if password:
                fixed_login_handler(password)
            else:
                st.error("❌ 请输入密码！")

        # 小贴士和互动提示
        st.markdown("""
        <div style="text-align: center; margin: 2rem auto; padding: 1.5rem; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 15px; color: rgba(255, 255, 255, 0.9);">
            <p style="margin-bottom: 0.5rem;">💡 <strong>小贴士：</strong></p>
            <p style="font-size: 0.9rem; line-height: 1.5;">
                点击飘浮的图标可以暂停它们 ✨<br>
                按空格键可以让所有图标暂停一会儿 🎮<br>
                试试点击屏幕的不同地方看看会发生什么 🌟
            </p>
        </div>
        """, unsafe_allow_html=True)
