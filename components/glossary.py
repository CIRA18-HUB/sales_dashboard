# components/glossary.py
# 名词解释侧边栏组件

import streamlit as st

# 扩展的名词解释字典
EXTENDED_GLOSSARY = {
    'BCG矩阵': {
        'definition': '波士顿咨询集团矩阵，将产品按市场占有率和市场增长率分为四类',
        'details': '明星产品（高增长率+高市场占有率）、现金牛产品（低增长率+高市场占有率）、问号产品（高增长率+低市场占有率）、瘦狗产品（低增长率+低市场占有率）',
        'application': '用于产品组合管理和资源配置决策'
    },
    '销售达成率': {
        'definition': '实际销售额与销售目标的比率',
        'details': '计算公式：达成率 = 实际销售额 ÷ 销售目标 × 100%',
        'application': '评估销售团队和个人的业绩表现'
    },
    'JBP计划': {
        'definition': '联合业务计划(Joint Business Plan)',
        'details': '与重要客户共同制定的年度业务发展计划，包括销售目标、营销策略、供应链协作等',
        'application': '深化客户合作关系，实现双赢发展'
    },
    '库存周转率': {
        'definition': '一定时期内销售量与平均库存量的比率',
        'details': '计算公式：周转率 = 销售量 ÷ 平均库存量，反映库存运营效率',
        'application': '评估存货管理效果，优化库存结构'
    },
    'MT渠道': {
        'definition': '现代渠道(Modern Trade)',
        'details': '包括大型超市、连锁店、便利店等现代零售业态',
        'application': '通常具有规模化、标准化特征，适合大批量分销'
    },
    'TT渠道': {
        'definition': '传统渠道(Traditional Trade)',
        'details': '包括小型零售店、批发商、经销商等传统零售业态',
        'application': '覆盖面广，灵活性高，适合精细化运营'
    },
    '客户细分': {
        'definition': '根据客户特征将客户群体划分为不同类别的过程',
        'details': '常见维度：新品接受度、购买金额、购买频次、产品偏好等',
        'application': '实施差异化营销策略，提升客户满意度'
    },
    '市场渗透率': {
        'definition': '产品或服务在目标市场中的覆盖程度',
        'details': '计算公式：渗透率 = 实际客户数 ÷ 目标客户数 × 100%',
        'application': '评估市场开发潜力，制定市场扩张策略'
    },
    '产品组合': {
        'definition': '企业同时生产和销售的所有产品的集合',
        'details': '包括产品的宽度（产品线数量）、长度（产品项目数量）、深度（产品变化数量）',
        'application': '优化资源配置，满足不同客户需求'
    },
    '新品接受度': {
        'definition': '目标客户对新产品的接受和购买程度',
        'details': '影响因素：产品创新性、价格定位、推广力度、客户需求匹配度',
        'application': '评估新品推广效果，调整产品策略'
    },
    '客户价值': {
        'definition': '客户为企业带来的经济价值',
        'details': '包括当前价值（现有购买金额）和潜在价值（未来购买潜力）',
        'application': '实施客户价值管理，提升客户忠诚度'
    },
    '同期比较': {
        'definition': '与去年同期数据进行对比分析',
        'details': '消除季节性因素影响，更准确反映业务增长趋势',
        'application': '制定年度预算和目标，评估长期发展趋势'
    },
    '环比增长': {
        'definition': '与上一个统计周期相比的增长情况',
        'details': '计算公式：环比增长率 = (本期数据 - 上期数据) ÷ 上期数据 × 100%',
        'application': '监控短期业务变化，及时调整经营策略'
    },
    '库存覆盖天数': {
        'definition': '现有库存按当前销售速度可以销售的天数',
        'details': '计算公式：覆盖天数 = 现有库存量 ÷ 日均销售量',
        'application': '合理安排采购计划，避免缺货或积压'
    },
    '包装类型': {
        'definition': '产品的包装形式分类',
        'details': '如袋装、盒装、瓶装、分享装、迷你包等，影响产品定位和消费场景',
        'application': '满足不同消费需求，提升产品竞争力'
    }
}

class GlossaryPanel:
    def __init__(self):
        self.glossary = EXTENDED_GLOSSARY
    
    def render_sidebar(self):
        """在侧边栏渲染名词解释"""
        with st.sidebar.expander("📚 名词解释", expanded=False):
            st.markdown("### 常用术语解释")
            
            # 搜索功能
            search_term = st.text_input("搜索术语", placeholder="输入关键词搜索...", key="glossary_search")
            
            # 按分类显示
            self._render_by_category(search_term)
    
    def render_inline(self, term):
        """内联显示单个术语解释"""
        if term in self.glossary:
            term_info = self.glossary[term]
            st.markdown(f"""
            <div class="glossary-term">
                <div class="glossary-term-title">{term}</div>
                <div class="glossary-term-desc">{term_info['definition']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"未找到术语「{term}」的解释")
    
    def _render_by_category(self, search_term=""):
        """按分类渲染术语"""
        categories = {
            '🔢 指标类': ['销售达成率', '库存周转率', '市场渗透率', '新品接受度', '客户价值', '库存覆盖天数'],
            '📋 分析方法': ['BCG矩阵', '客户细分', '产品组合', '同期比较', '环比增长'],
            '🏢 渠道类': ['MT渠道', 'TT渠道', 'JBP计划'],
            '📦 产品类': ['包装类型']
        }
        
        for category, terms in categories.items():
            filtered_terms = []
            
            if search_term:
                # 搜索功能
                for term in terms:
                    if (search_term.lower() in term.lower() or 
                        search_term.lower() in self.glossary[term]['definition'].lower()):
                        filtered_terms.append(term)
            else:
                filtered_terms = terms
            
            if filtered_terms:
                st.markdown(f"**{category}**")
                for term in filtered_terms:
                    self._render_term_detail(term)
                st.markdown("---")
    
    def _render_term_detail(self, term):
        """渲染术语详细信息"""
        if term in self.glossary:
            term_info = self.glossary[term]
            
            with st.expander(f"**{term}**", expanded=False):
                st.markdown(f"**定义：** {term_info['definition']}")
                
                if 'details' in term_info:
                    st.markdown(f"**详细说明：** {term_info['details']}")
                
                if 'application' in term_info:
                    st.markdown(f"**应用场景：** {term_info['application']}")
    
    def get_term_tooltip(self, term):
        """获取术语的提示文本"""
        if term in self.glossary:
            return self.glossary[term]['definition']
        return f"术语「{term}」暂无解释"
    
    def add_term(self, term, definition, details=None, application=None):
        """添加新术语"""
        self.glossary[term] = {
            'definition': definition,
            'details': details,
            'application': application
        }
    
    def update_term(self, term, **kwargs):
        """更新现有术语"""
        if term in self.glossary:
            self.glossary[term].update(kwargs)

# 全局实例
glossary_panel = GlossaryPanel()

# 便捷函数
def render_glossary_sidebar():
    """渲染名词解释侧边栏的便捷函数"""
    glossary_panel.render_sidebar()

def show_term_inline(term):
    """内联显示术语解释的便捷函数"""
    glossary_panel.render_inline(term)

def get_term_help(term):
    """获取术语帮助文本的便捷函数"""
    return glossary_panel.get_term_tooltip(term)