# components/insights.py
# 智能洞察生成组件

import pandas as pd
import numpy as np
from datetime import datetime

class InsightGenerator:
    def __init__(self, data):
        self.data = data
    
    def generate_sales_insights(self, total_sales, growth_rate=None, target_achievement=None):
        """生成销售额洞察"""
        insights = []
        
        if total_sales > 0:
            if total_sales >= 100000000:
                insights.append("销售规模达到亿元级别，表现优异")
            elif total_sales >= 10000000:
                insights.append("销售规模达到千万级别，发展良好")
            else:
                insights.append("销售规模有待提升，需加强市场开拓")
        
        if growth_rate is not None:
            if growth_rate > 0.2:
                insights.append(f"销售增长率为{growth_rate:.1%}，增长强劲")
            elif growth_rate > 0.1:
                insights.append(f"销售增长率为{growth_rate:.1%}，保持稳健增长")
            elif growth_rate > 0:
                insights.append(f"销售增长率为{growth_rate:.1%}，增长放缓")
            else:
                insights.append(f"销售下降{abs(growth_rate):.1%}，需要重点关注")
        
        if target_achievement is not None:
            if target_achievement >= 1.0:
                insights.append(f"目标达成率{target_achievement:.1%}，超额完成任务")
            elif target_achievement >= 0.9:
                insights.append(f"目标达成率{target_achievement:.1%}，接近完成目标")
            else:
                insights.append(f"目标达成率{target_achievement:.1%}，与目标存在差距")
        
        return " • ".join(insights)
    
    def generate_customer_insights(self, customer_data):
        """生成客户分析洞察"""
        insights = []
        
        if not customer_data.empty:
            total_customers = len(customer_data)
            top5_percentage = customer_data.head(5)['销售额'].sum() / customer_data['销售额'].sum() * 100
            
            insights.append(f"共服务{total_customers}个客户")
            
            if top5_percentage > 60:
                insights.append("TOP5客户集中度过高，存在依赖风险")
            elif top5_percentage > 40:
                insights.append("客户集中度适中，结构相对合理")
            else:
                insights.append("客户分布较为均衡，风险控制良好")
            
            # 客户价值分析
            avg_value = customer_data['销售额'].mean()
            high_value_customers = len(customer_data[customer_data['销售额'] > avg_value * 2])
            
            if high_value_customers > 0:
                insights.append(f"识别出{high_value_customers}个高价值客户")
        
        return " • ".join(insights)
    
    def generate_product_insights(self, product_data):
        """生成产品分析洞察"""
        insights = []
        
        if not product_data.empty:
            total_products = len(product_data)
            top3_percentage = product_data.head(3)['销售额'].sum() / product_data['销售额'].sum() * 100
            
            insights.append(f"销售{total_products}个产品")
            
            if top3_percentage > 70:
                insights.append("产品销售过于集中，需要培育更多爆款")
            elif top3_percentage > 50:
                insights.append("主力产品贡献显著，产品结构基本合理")
            else:
                insights.append("产品销售相对均衡，多元化发展良好")
            
            # 新品表现
            new_products = ['F0110C', 'F0183F', 'F01K8A', 'F0183K', 'F0101P']
            new_product_sales = product_data[product_data['产品代码'].isin(new_products)]['销售额'].sum()
            new_product_ratio = new_product_sales / product_data['销售额'].sum() * 100
            
            if new_product_ratio > 30:
                insights.append("新品表现突出，创新能力强")
            elif new_product_ratio > 15:
                insights.append("新品发展稳健，有一定市场接受度")
            else:
                insights.append("新品占比较低，需加强推广力度")
        
        return " • ".join(insights)
    
    def generate_deep_analysis(self, metric_name, current_value, historical_data=None, benchmark=None):
        """生成深度分析"""
        analysis = []
        
        # 当前状态分析
        analysis.append(f"<b>当前状态：</b>{metric_name}为{current_value:,.0f}")
        
        # 历史趋势分析
        if historical_data is not None and len(historical_data) > 1:
            trend = self._analyze_trend(historical_data)
            analysis.append(f"<b>趋势分析：</b>{trend}")
        
        # 基准对比分析  
        if benchmark is not None:
            benchmark_analysis = self._compare_with_benchmark(current_value, benchmark)
            analysis.append(f"<b>基准对比：</b>{benchmark_analysis}")
        
        # 影响因素分析
        factors = self._identify_factors(metric_name, current_value)
        if factors:
            analysis.append(f"<b>影响因素：</b>{factors}")
        
        return "<br>".join(analysis)
    
    def generate_recommendations(self, metric_name, performance_level):
        """生成改进建议"""
        recommendations = {
            '销售额': {
                'high': '继续保持优秀表现，可考虑扩大市场份额或提升产品单价',
                'medium': '加强重点客户维护，优化产品组合，提升销售效率',
                'low': '重新评估市场策略，加强团队培训，寻找新的增长点'
            },
            '客户数量': {
                'high': '维护现有客户关系，提升客户价值，发展标杆客户',
                'medium': '平衡新客户开发与老客户维护，提升客户满意度',
                'low': '制定客户开发计划，加强市场推广，优化服务质量'
            },
            '产品销量': {
                'high': '优化热销产品供应链，考虑产能扩张，延长产品生命周期',
                'medium': '分析市场需求变化，调整产品策略，提升产品竞争力',
                'low': '重新定位产品市场，考虑产品创新或淘汰低效产品'
            }
        }
        
        return recommendations.get(metric_name, {}).get(performance_level, '建议深入分析具体情况，制定针对性改进方案')
    
    def generate_action_plan(self, metric_name, time_horizon='3个月'):
        """生成行动方案"""
        action_plans = {
            '销售额': [
                '第1月：制定详细的销售提升计划，明确目标和责任人',
                '第2月：实施重点客户营销活动，推广高价值产品',
                '第3月：评估执行效果，调整策略并制定下阶段计划'
            ],
            '客户数量': [
                '第1月：分析目标客户群体，制定获客策略',
                '第2月：实施多渠道获客活动，优化客户服务流程',
                '第3月：评估获客效果，建立客户关系管理体系'
            ],
            '产品销量': [
                '第1月：分析产品销售数据，识别增长机会',
                '第2月：优化产品营销策略，加强渠道建设',
                '第3月：监控销售表现，持续优化产品组合'
            ]
        }
        
        plans = action_plans.get(metric_name, [
            f'第1月：深入分析{metric_name}现状，识别关键问题',
            f'第2月：制定并实施针对性改进措施',
            f'第3月：评估改进效果，建立长期监控机制'
        ])
        
        return '<br>'.join([f'{i+1}. {plan}' for i, plan in enumerate(plans)])
    
    def _analyze_trend(self, data):
        """分析数据趋势"""
        if len(data) < 2:
            return "数据不足，无法分析趋势"
        
        # 计算趋势
        if isinstance(data, pd.Series):
            values = data.values
        else:
            values = np.array(data)
        
        # 使用线性回归分析趋势
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0:
            return f"呈上升趋势，平均增长率{slope/values[0]*100:.1f}%"
        elif slope < 0:
            return f"呈下降趋势，平均下降率{abs(slope)/values[0]*100:.1f}%"
        else:
            return "保持稳定，变化幅度较小"
    
    def _compare_with_benchmark(self, current_value, benchmark):
        """与基准值对比"""
        ratio = current_value / benchmark
        
        if ratio >= 1.2:
            return f"显著超过基准值{ratio:.1%}，表现优异"
        elif ratio >= 1.0:
            return f"超过基准值{ratio:.1%}，表现良好"
        elif ratio >= 0.8:
            return f"略低于基准值{ratio:.1%}，有改进空间"
        else:
            return f"明显低于基准值{ratio:.1%}，需要重点关注"
    
    def _identify_factors(self, metric_name, current_value):
        """识别影响因素"""
        factors = {
            '销售额': '市场环境、产品竞争力、销售团队能力、客户需求变化',
            '客户数量': '市场开拓能力、产品吸引力、服务质量、品牌影响力',
            '产品销量': '产品定位、价格策略、渠道覆盖、市场推广'
        }
        
        return factors.get(metric_name, '多种内外部因素综合影响')

# 便捷函数
def generate_insight(metric_name, current_value, **kwargs):
    """生成单个指标洞察的便捷函数"""
    generator = InsightGenerator(None)
    
    if metric_name == '销售额':
        return generator.generate_sales_insights(current_value, **kwargs)
    elif metric_name == '客户数量':
        return generator.generate_customer_insights(kwargs.get('customer_data', pd.DataFrame()))
    elif metric_name == '产品销量':
        return generator.generate_product_insights(kwargs.get('product_data', pd.DataFrame()))
    else:
        return f"{metric_name}当前值为{current_value:,.0f}"

def create_smart_insight(metric_name, current_value, performance_level='medium'):
    """创建智能洞察的便捷函数"""
    generator = InsightGenerator(None)
    
    insight = generate_insight(metric_name, current_value)
    deep_analysis = generator.generate_deep_analysis(metric_name, current_value)
    recommendations = generator.generate_recommendations(metric_name, performance_level)
    action_plan = generator.generate_action_plan(metric_name)
    
    return {
        'insight': insight,
        'deep_analysis': deep_analysis,
        'recommendations': recommendations,
        'action_plan': action_plan
    }