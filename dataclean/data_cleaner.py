import pandas as pd
import numpy as np
import re
import logging

def handle_duplicates(df, config):
    """处理重复值"""
    if 'duplicates' in config and config['duplicates']['remove']:
        original_rows = df.shape[0]
        df = df.drop_duplicates()
        removed_rows = original_rows - df.shape[0]
        logging.info(f"已删除 {removed_rows} 条重复记录")
    return df

def handle_outliers(df, config):
    """处理异常值"""
    if 'outliers' not in config:
        return df

    outlier_config = config['outliers']
    method = outlier_config['method']
    columns = outlier_config['columns']

    for col in columns:
        if method == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            df = df[z_scores < 3]
        elif method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[~((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR)))]
        logging.info(f"列 {col} 异常值处理完成，方法：{method}")
    return df

def clean_text(df, config):
    """清洗文本数据"""
    if 'text_cleaning' not in config:
        return df

    text_columns = config['text_cleaning']['columns']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # 去除特殊字符
            df[col] = df[col].str.lower()  # 转换为小写
            logging.info(f"列 {col} 文本数据清洗完成")
    return df

def handle_missing_values(df, config):
    """缺失值处理"""
    if 'missing_value' not in config:
        return df

    strategies = config['missing_value']
    for col, strategy in strategies.items():
        if col not in df.columns:
            logging.warning(f"列 {col} 不存在，跳过缺失值处理")
            continue

        if strategy['method'] == 'fill':
            if pd.api.types.is_numeric_dtype(df[col]) and isinstance(strategy['value'], str):
                df[col] = df[col].astype(object)
            df[col] = df[col].fillna(strategy['value'])
        elif strategy['method'] == 'ffill':
            df[col] = df[col].ffill()
        elif strategy['method'] == 'statistic':
            if strategy['type'] == 'mean':
                fill_value = df[col].mean()
            elif strategy['type'] == 'median':
                fill_value = df[col].median()
            else:
                fill_value = strategy.get('value', 0)
            df[col] = df[col].fillna(fill_value)
        logging.info(f"列 {col} 缺失值处理完成，策略：{strategy}")
    return df