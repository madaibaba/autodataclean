# 🧹 autodataclean 使用效果展示

`autodataclean` 是一个用于数据清洗的 Python 包，支持缺失值处理、数据类型转换、特征缩放、数据聚合和可视化报告生成等功能。

## 📁 目录
- [安装](#安装)
- [使用示例](#使用示例)
- [配置文件说明](#配置文件说明)
- [清洗效果展示](#清洗效果展示)
- [功能介绍](#功能介绍)
- [依赖项](#依赖项)

## 🧩 安装

你可以使用 `pip` 安装：

```bash
pip install autodataclean
```

## ⚙️ 使用示例

```python
from autodataclean import DataProcessingPipeline

config_path = 'configs/hotel_bookings.json'

pipeline = DataProcessingPipeline(config_path)
pipeline.run()
```

## 📝 配置文件说明

以下是一个典型的配置文件（`hotel_bookings.json`）：

```json
{
  "input_path": "datasets/hotel_bookings.csv",
  "output_path": "datasets/hotel_bookings/",
  "output_format": "csv",
  "duplicates": {
    "remove": true
  },
  "missing_value": {
    "children": {
      "method": "fill",
      "value": 0
    },
    "total_cost": {
      "method": "fill",
      "value": 0
    }
  },
  "text_cleaning": {
    "columns": ["comment"]
  }
}
```

## 🔍 清洗效果展示

### 🗃 原始数据示例（`hotel_bookings.csv`）

| booking_id | arrival_date | adults | children | country | total_cost | comment |
|------------|--------------|--------|----------|---------|------------|---------|
| 1          | 2021-05-01   | 2      | NaN      | PRT     | 350        | Good!   |
| 2          | 2021-05-02   | 2      | 1        | ESP     | NaN        | Great   |
| 1          | 2021-05-01   | 2      | NaN      | PRT     | 350        | Good!   |

### ✅ 清洗后数据（`cleaned.csv`）

| booking_id | arrival_date | adults | children | country | total_cost | comment |
|------------|--------------|--------|----------|---------|------------|---------|
| 1          | 2021-05-01   | 2      | 0        | PRT     | 350        | good    |
| 2          | 2021-05-02   | 2      | 1        | ESP     | 0          | great   |

### 📊 可视化报告目录结构

```
datasets/hotel_bookings/
├── cleaned.csv
└── report/
    └── report.html
```

报告内容包括：
- 缺失值分布图
- 清洗前后字段对比图
- 字段类型和分布统计图等

## 🚀 功能介绍

- **重复值处理**：移除重复记录
- **缺失值处理**：支持填充常数、均值、中位数、前向填充等方式
- **文本清洗**：移除特殊字符、统一小写
- **异常值处理**：支持 Z-score 和 IQR 方法
- **类型转换**：支持字符串转时间戳、数值等
- **特征缩放**：标准化与归一化
- **数据聚合**：按字段分组聚合
- **可视化报告生成**：自动生成 HTML 格式报告

## 📦 依赖项

`autodataclean` 依赖以下库：

- pandas
- numpy
- scikit-learn
- plotly
- jinja2
- requests

---

欢迎提出 Issue 或 Pull Request！🚀
