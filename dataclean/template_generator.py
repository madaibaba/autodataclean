def create_report_template():
    template_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>数据清洗可视化报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        h1, h2, h3 {
            color: #333;
            text-align: center;
        }
        .chart-container {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        iframe {
            width: 100%;
            height: 600px;
            border: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="chart-container">
        <h2>数据质量对比报告</h2>
        {% if pre_cleaning_metrics %}
        <table>
            <thead>
                <tr>
                    <th>指标</th>
                    <th>清洗前</th>
                    <th>清洗后</th>
                </tr>
            </thead>
            <tbody>
                {% for key in pre_cleaning_metrics.keys() %}
                <tr>
                    <td>{{ key }}</td>
                    <td>{{ pre_cleaning_metrics[key] }}</td>
                    <td>{{ post_cleaning_metrics[key] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <h3>清洗后数据质量指标</h3>
        <ul>
            {% for key, value in post_cleaning_metrics.items() %}
            <li>{{ key }}: {{ value }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    <h1>数据清洗可视化报告</h1>
    <div class="chart-container">
        <h2>数值特征直方图</h2>
        <iframe src="{{ hist_path }}"></iframe>
    </div>
    <div class="chart-container">
        <h2>相关性热力图</h2>
        <iframe src="{{ heatmap_path }}"></iframe>
    </div>
    <div class="chart-container">
        <h2>数值特征箱线图</h2>
        <iframe src="{{ boxplot_path }}"></iframe>
    </div>
    <div class="chart-container">
        <h2>分类变量柱状图</h2>
        <iframe src="{{ bar_path }}"></iframe>
    </div>
</body>
</html>
    """
    # 指定编码为 utf-8 写入文件
    with open('report_template.html', 'w', encoding='utf-8') as f: 
        f.write(template_content)