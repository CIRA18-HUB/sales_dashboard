# 完整的修复方案 - 替换原文件中的相应部分

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_advanced_charts(metrics, sales_data, monthly_data):
    """创建高级交互式图表 - 修复版"""
    charts = {}
    
    # 1. 增强版客户健康状态雷达图
    categories = ['健康度', '目标达成', '价值贡献', '活跃度', '稳定性']
    
    values = [
        metrics['normal_rate'],
        metrics['target_achievement_rate'],
        metrics['high_value_rate'],
        (metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics['normal_customers'] > 0 else 0,
        (100 - metrics['max_dependency'])
    ]
    
    # 对应的详细说明
    descriptions = {
        '健康度': f"正常运营客户占比 {metrics['normal_rate']:.1f}%\n越高说明客户群体越稳定",
        '目标达成': f"销售目标达成率 {metrics['target_achievement_rate']:.1f}%\n反映整体销售执行力",
        '价值贡献': f"高价值客户占比 {metrics['high_value_rate']:.1f}%\n钻石+黄金客户比例",
        '活跃度': f"活跃客户占比 {((metrics['normal_customers'] - metrics['risk_customers']) / metrics['normal_customers'] * 100 if metrics['normal_customers'] > 0 else 0):.1f}%\n近期有交易的客户比例",
        '稳定性': f"风险分散度 {(100 - metrics['max_dependency']):.1f}%\n100-最大客户依赖度"
    }
    
    fig_radar = go.Figure()
    
    # 添加当前状态
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='当前状态',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        customdata=[[desc] for desc in descriptions.values()],
        hovertemplate='<b>%{theta}</b><br>%{customdata[0]}<extra></extra>',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.9)",
            font_size=12,
            font_family="Arial"
        )
    ))
    
    # 添加基准线
    fig_radar.add_trace(go.Scatterpolar(
        r=[85, 80, 70, 85, 70],
        theta=categories,
        fill='toself',
        name='目标基准',
        fillcolor='rgba(255, 99, 71, 0.1)',
        line=dict(color='#ff6347', width=2, dash='dash'),
        hovertemplate='%{theta} 目标: %{r:.1f}%<extra></extra>'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                tickfont=dict(size=12)
            ),
            angularaxis=dict(
                tickfont=dict(size=14, weight='bold')
            )
        ),
        showlegend=True,
        height=500,
        margin=dict(t=40, b=40, l=40, r=40),
        font=dict(size=14)
    )
    
    charts['health_radar'] = fig_radar
    
    # 2. 客户价值流动桑基图（安全版本）
    if not metrics['rfm_df'].empty:
        try:
            # 准备桑基图数据
            source = []
            target = []
            value = []
            labels = ['全部客户']
            colors = ['#f0f0f0']
            
            # 客户类型及其对应的颜色
            customer_types = [
                ('钻石客户', '#ff6b6b'),
                ('黄金客户', '#ffd93d'),
                ('白银客户', '#c0c0c0'),
                ('潜力客户', '#4ecdc4'),
                ('流失风险', '#a8a8a8')
            ]
            
            node_idx = 1
            for ct, color in customer_types:
                count = len(metrics['rfm_df'][metrics['rfm_df']['类型'] == ct])
                if count > 0:
                    labels.append(f"{ct}\n{count}家")
                    colors.append(color)
                    source.append(0)
                    target.append(node_idx)
                    value.append(count)
                    node_idx += 1
            
            if len(source) > 0:  # 确保有数据
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=20,
                        thickness=25,
                        line=dict(color="white", width=2),
                        label=labels,
                        color=colors
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=value,
                        color='rgba(180, 180, 180, 0.3)'
                    )
                )])
                
                fig_sankey.update_layout(
                    height=700,
                    margin=dict(t=60, b=60, l=60, r=60),
                    font=dict(size=14)
                )
                
                charts['sankey'] = fig_sankey
        except Exception as e:
            print(f"桑基图创建失败: {e}")
    
    # 3. 客户贡献度旭日图（安全版本）
    if not metrics['rfm_df'].empty:
        try:
            # 准备旭日图数据
            sunburst_data = []
            total_value = metrics['rfm_df']['M'].sum()
            
            if total_value > 0:
                sunburst_data.append({
                    'labels': '全部客户',
                    'parents': '',
                    'values': total_value
                })
                
                # 按客户类型分组
                for customer_type in ['钻石客户', '黄金客户', '白银客户', '潜力客户', '流失风险']:
                    type_customers = metrics['rfm_df'][metrics['rfm_df']['类型'] == customer_type]
                    if not type_customers.empty:
                        type_total = type_customers['M'].sum()
                        sunburst_data.append({
                            'labels': f"{customer_type}\n({len(type_customers)}家)",
                            'parents': '全部客户',
                            'values': type_total
                        })
                
                if len(sunburst_data) > 1:
                    df_sunburst = pd.DataFrame(sunburst_data)
                    
                    fig_sunburst = go.Figure(go.Sunburst(
                        labels=df_sunburst['labels'],
                        parents=df_sunburst['parents'],
                        values=df_sunburst['values'],
                        branchvalues="total"
                    ))
                    
                    fig_sunburst.update_layout(
                        height=700,
                        margin=dict(t=40, b=40, l=40, r=40)
                    )
                    
                    charts['sunburst'] = fig_sunburst
        except Exception as e:
            print(f"旭日图创建失败: {e}")
    
    # 4. 动态月度趋势面积图
    if not sales_data.empty:
        try:
            # 按月汇总销售数据
            sales_data['年月'] = sales_data['订单日期'].dt.to_period('M')
            monthly_sales = sales_data.groupby('年月')['金额'].agg(['sum', 'count']).reset_index()
            monthly_sales['年月'] = monthly_sales['年月'].astype(str)
            
            # 创建双轴图
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 销售额面积图
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_sales['年月'],
                    y=monthly_sales['sum'],
                    mode='lines+markers',
                    name='销售额',
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.2)',
                    line=dict(color='#667eea', width=3)
                ),
                secondary_y=False
            )
            
            # 订单数量线
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_sales['年月'],
                    y=monthly_sales['count'],
                    mode='lines+markers',
                    name='订单数',
                    line=dict(color='#ff6b6b', width=2)
                ),
                secondary_y=True
            )
            
            fig_trend.update_xaxes(title_text="月份")
            fig_trend.update_yaxes(title_text="销售额", secondary_y=False)
            fig_trend.update_yaxes(title_text="订单数", secondary_y=True)
            
            fig_trend.update_layout(
                height=500,
                hovermode='x unified',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            
            charts['trend'] = fig_trend
        except Exception as e:
            print(f"趋势图创建失败: {e}")
    
    # 5. 目标达成散点图（修复版本）
    if not metrics['customer_achievement_details'].empty:
        try:
            achievement_df = metrics['customer_achievement_details'].copy()
            
            # 数据清理和验证
            achievement_df = achievement_df.dropna(subset=['目标', '实际', '达成率'])
            achievement_df = achievement_df[achievement_df['目标'] > 0]
            achievement_df = achievement_df[achievement_df['实际'] >= 0]
            
            if not achievement_df.empty:
                fig_scatter = go.Figure()
                
                # 安全的颜色和大小计算
                colors = []
                sizes = []
                for rate in achievement_df['达成率']:
                    rate = max(0, min(500, rate))  # 限制范围
                    
                    if rate >= 100:
                        colors.append('#48bb78')
                        sizes.append(max(20, min(80, rate / 2)))
                    elif rate >= 80:
                        colors.append('#ffd93d')
                        sizes.append(max(15, min(60, rate / 2.5)))
                    else:
                        colors.append('#ff6b6b')
                        sizes.append(max(10, min(40, rate / 3)))
                
                # 添加散点
                fig_scatter.add_trace(go.Scatter(
                    x=achievement_df['目标'],
                    y=achievement_df['实际'],
                    mode='markers',
                    marker=dict(
                        size=sizes,
                        color=colors,
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    text=achievement_df['客户'],
                    name='客户达成情况',
                    hovertemplate='<b>%{text}</b><br>目标: ¥%{x:,.0f}<br>实际: ¥%{y:,.0f}<extra></extra>'
                ))
                
                # 安全计算最大值
                max_target = achievement_df['目标'].max()
                max_actual = achievement_df['实际'].max()
                max_val = max(max_target, max_actual, 1000000) * 1.1
                
                # 添加参考线
                if max_val > 0 and pd.notna(max_val):
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val],
                        y=[0, max_val],
                        mode='lines',
                        name='目标线(100%)',
                        line=dict(color='#e74c3c', width=3, dash='dash')
                    ))
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=[0, max_val],
                        y=[0, max_val * 0.8],
                        mode='lines',
                        name='达成线(80%)',
                        line=dict(color='#f39c12', width=2, dash='dot')
                    ))
                
                # 安全的布局更新
                fig_scatter.update_layout(
                    title="客户目标达成分析",
                    xaxis_title="目标金额",
                    yaxis_title="实际金额",
                    height=800,
                    hovermode='closest',
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                charts['target_scatter'] = fig_scatter
            else:
                # 空数据的处理
                fig_empty = go.Figure()
                fig_empty.add_annotation(
                    text="暂无有效的目标达成数据",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=20, color="gray")
                )
                fig_empty.update_layout(height=400, plot_bgcolor='white')
                charts['target_scatter'] = fig_empty
                
        except Exception as e:
            print(f"目标达成散点图创建失败: {e}")
            # 创建错误提示图
            fig_error = go.Figure()
            fig_error.add_annotation(
                text=f"图表创建出错: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig_error.update_layout(height=400, plot_bgcolor='white')
            charts['target_scatter'] = fig_error
    
    return charts

# 添加数据验证函数
def validate_metrics_data(metrics):
    """验证指标数据的有效性"""
    try:
        # 确保基本指标都是有效数值
        for key in ['normal_rate', 'target_achievement_rate', 'high_value_rate', 'max_dependency']:
            if key in metrics:
                if pd.isna(metrics[key]) or not isinstance(metrics[key], (int, float)):
                    metrics[key] = 0
                else:
                    metrics[key] = max(0, min(100, metrics[key]))  # 限制在0-100范围内
        
        # 确保客户数量都是非负整数
        for key in ['total_customers', 'normal_customers', 'risk_customers']:
            if key in metrics:
                if pd.isna(metrics[key]) or metrics[key] < 0:
                    metrics[key] = 0
                else:
                    metrics[key] = int(metrics[key])
        
        # 验证DataFrame
        if 'rfm_df' in metrics and not isinstance(metrics['rfm_df'], pd.DataFrame):
            metrics['rfm_df'] = pd.DataFrame()
            
        if 'customer_achievement_details' in metrics and not isinstance(metrics['customer_achievement_details'], pd.DataFrame):
            metrics['customer_achievement_details'] = pd.DataFrame()
        
        return metrics
    except Exception as e:
        print(f"数据验证出错: {e}")
        return metrics

# 在main函数中调用数据验证
def main():
    # ... 前面的代码保持不变 ...
    
    # 加载数据
    metrics, customer_status, sales_data, monthly_data = load_and_process_data()
    
    if metrics is None:
        st.error("❌ 数据加载失败，请检查数据文件是否存在。")
        return
    
    # 验证数据
    metrics = validate_metrics_data(metrics)
    
    # 创建高级图表
    charts = create_advanced_charts(metrics, sales_data, monthly_data)
    
    # ... 其余代码保持不变 ...
