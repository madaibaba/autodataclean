import pandas as pd
import numpy as np
import logging
import plotly.express as px
from jinja2 import Environment, FileSystemLoader
import os

def calculate_data_quality_metrics(df):
    """计算数据质量指标"""
    metrics = {}
    metrics['rows'] = df.shape[0]
    metrics['columns'] = df.shape[1]
    metrics['missing_values'] = df.isnull().sum().sum()
    metrics['duplicate_rows'] = df.duplicated().sum()
    return metrics

def generate_visualization_report(df, original_df, config):
    """生成可视化报告"""
    if not('generate_reports' in config and config['generate_reports']):
        return
    # 创建图表目录
    report_dir = os.path.join(config['output_path'], f"report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # 处理 MultiIndex 列名
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)) for col in df.columns]

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    # 柱状图
    if len(numeric_cols) > 0:
        fig = px.histogram(df, x=numeric_cols[0])
        fig.update_layout(title_text=f'Histogram of {numeric_cols[0]}')
        hist_path = os.path.join(report_dir, 'histogram.html')
        fig.write_html(hist_path)

    # 相关性热力图
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto")
        fig.update_layout(title_text='Correlation Heatmap')
        heatmap_path = os.path.join(report_dir, 'heatmap.html')
        fig.write_html(heatmap_path)

    # 箱线图
    if len(numeric_cols) > 0:
        fig = px.box(df, y=numeric_cols)
        fig.update_layout(title_text='Boxplot of Numeric Features')
        boxplot_path = os.path.join(report_dir, 'boxplot.html')
        fig.write_html(boxplot_path)

    # 分类变量柱状图
    if len(categorical_cols) > 0:
        fig = px.bar(df[categorical_cols[0]].value_counts())
        fig.update_layout(title_text=f'Bar Chart of {categorical_cols[0]}')
        bar_path = os.path.join(report_dir, 'bar_chart.html')
        fig.write_html(bar_path)

    # 计算数据质量指标
    pre_cleaning_metrics = calculate_data_quality_metrics(original_df) if original_df is not None else None
    post_cleaning_metrics = calculate_data_quality_metrics(df)

    # 生成 HTML 报告
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report_template.html')
    html_content = template.render(
        hist_path=hist_path.replace(config['output_path'],'.'),
        heatmap_path=heatmap_path.replace(config['output_path'],'.'),
        boxplot_path=boxplot_path.replace(config['output_path'],'.'),
        bar_path=bar_path.replace(config['output_path'],'.'),
        pre_cleaning_metrics=pre_cleaning_metrics,
        post_cleaning_metrics=post_cleaning_metrics
    )
    report_path = os.path.join(config['output_path'], 'report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logging.info(f"可视化报告已生成：{report_path}")

def generate_data_quality_comparison_report(df, original_df, config):
    """生成数据质量对比报告"""
    if not('generate_reports' in config and config['generate_reports']):
        return
    # 计算清洗前的数据质量指标
    pre_cleaning_metrics = calculate_data_quality_metrics(original_df) if original_df is not None else None

    # 计算清洗后的数据质量指标
    post_cleaning_metrics = calculate_data_quality_metrics(df)

    # 生成报告内容
    report_content = "数据质量对比报告\n"
    report_content += "=" * 30 + "\n"

    if pre_cleaning_metrics:
        report_content += "清洗前数据质量指标:\n"
        for key, value in pre_cleaning_metrics.items():
            report_content += f"{key}: {value}\n"
        report_content += "\n"

    report_content += "清洗后数据质量指标:\n"
    for key, value in post_cleaning_metrics.items():
        report_content += f"{key}: {value}\n"

    # 保存报告到文件
    report_path = os.path.join(config['output_path'], f"report")
    report_path = os.path.join(report_path, 'data_quality_comparison_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logging.info(f"数据质量对比报告已生成：{report_path}")