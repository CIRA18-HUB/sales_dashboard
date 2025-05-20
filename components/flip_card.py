# components/flip_card.py
# 三层翻转卡片组件

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from styles.theme import THEME_COLORS, apply_theme

class FlipCard:
    def __init__(self, card_id, title, value, subtitle="", unit="", is_percentage=False, is_currency=False):
        self.card_id = card_id
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.unit = unit
        self.is_percentage = is_percentage
        self.is_currency = is_currency
        self.layer_1_content = None
        self.layer_2_content = None
        self.layer_3_content = None
        
    def set_layer_2(self, chart_func=None, insight_text=""):
        """设置第二层内容：图表 + 洞察"""
        self.layer_2_content = {
            'chart_func': chart_func,
            'insight': insight_text
        }
        return self
    
    def set_layer_3(self, deep_analysis="", recommendations="", action_plan=""):
        """设置第三层内容：深度分析 + 建议 + 行动方案"""
        self.layer_3_content = {
            'analysis': deep_analysis,
            'recommendations': recommendations,
            'action_plan': action_plan
        }
        return self
    
    def format_value(self):
        """格式化显示值"""
        if self.is_currency:
            if self.value >= 100000000:
                return f"¥{self.value/100000000:.2f}亿"
            elif self.value >= 10000:
                return f"¥{self.value/10000:.2f}万"
            else:
                return f"¥{self.value:,.2f}"
        elif self.is_percentage:
            return f"{self.value:.1f}%"
        else:
            return f"{self.value:,.0f}{self.unit}"
    
    def render(self):
        """渲染卡片"""
        # 初始化会话状态
        if f"flip_state_{self.card_id}" not in st.session_state:
            st.session_state[f"flip_state_{self.card_id}"] = 0
        
        # 创建卡片容器
        card_container = st.container()
        
        with card_container:
            # 卡片点击处理
            if st.button(f"点击查看详情", key=f"flip_btn_{self.card_id}", 
                        help=f"点击查看{self.title}的详细分析"):
                st.session_state[f"flip_state_{self.card_id}"] = (
                    st.session_state[f"flip_state_{self.card_id}"] + 1
                ) % 3
            
            current_layer = st.session_state[f"flip_state_{self.card_id}"]
            
            # 渲染不同层级的内容
            if current_layer == 0:
                self._render_layer_1()
            elif current_layer == 1:
                self._render_layer_2()
            else:
                self._render_layer_3()
    
    def _render_layer_1(self):
        """渲染第一层：基础指标"""
        st.markdown(f"""
        <div class="flip-card">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    <div class="card-title">{self.title}</div>
                    <div class="card-value">{self.format_value()}</div>
                    <div class="card-subtitle">{self.subtitle}</div>
                    <div class="flip-indicator">点击查看分析 →</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_layer_2(self):
        """渲染第二层：图表 + 洞察"""
        if self.layer_2_content:
            # 显示图表
            if self.layer_2_content['chart_func']:
                fig = self.layer_2_content['chart_func']()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # 显示洞察
            if self.layer_2_content['insight']:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>📊 数据洞察</h4>
                    {self.layer_2_content['insight']}
                </div>
                """, unsafe_allow_html=True)
            
            # 继续查看提示
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <div class="flip-indicator">再次点击查看深度分析 →</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无第二层分析内容")
    
    def _render_layer_3(self):
        """渲染第三层：深度分析"""
        if self.layer_3_content:
            # 深度分析
            if self.layer_3_content['analysis']:
                st.markdown(f"""
                <div class="deep-analysis-box">
                    <h4>🔍 深度分析</h4>
                    {self.layer_3_content['analysis']}
                </div>
                """, unsafe_allow_html=True)
            
            # 改进建议
            if self.layer_3_content['recommendations']:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>💡 改进建议</h4>
                    {self.layer_3_content['recommendations']}
                </div>
                """, unsafe_allow_html=True)
            
            # 行动方案
            if self.layer_3_content['action_plan']:
                st.markdown(f"""
                <div class="action-box">
                    <h4>🎯 行动方案</h4>
                    {self.layer_3_content['action_plan']}
                </div>
                """, unsafe_allow_html=True)
            
            # 返回提示
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <div class="flip-indicator">再次点击返回基础视图 ↻</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无第三层分析内容")

# 工具函数
def create_flip_card(card_id, title, value, subtitle="", unit="", is_percentage=False, is_currency=False):
    """创建翻转卡片的便捷函数"""
    return FlipCard(card_id, title, value, subtitle, unit, is_percentage, is_currency)

def render_flip_card_row(cards):
    """渲染一行翻转卡片"""
    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            card.render()