import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging

def convert_data_types(df, config):
    """数据类型转换"""
    if 'dtype_conversion' not in config:
        return df

    conversions = config['dtype_conversion']
    for col, target_type in conversions.items():
        if col not in df.columns:
            logging.warning(f"列 {col} 不存在，跳过类型转换")
            continue

        try:
            if target_type == 'timestamp':
                df[col] = pd.to_datetime(df[col]).astype('int64') // 10**9
            elif target_type == 'category':
                df[col] = df[col].astype('category').cat.codes
            else:
                df[col] = df[col].astype(target_type)
            logging.info(f"列 {col} 成功转换为 {target_type}")
        except Exception as e:
            logging.error(f"列 {col} 类型转换失败：{str(e)}")
            raise
    return df

def feature_scaling(df, config):
    """特征缩放"""
    scalers = {}
    if 'feature_scaling' not in config:
        return df, scalers

    scaling_config = config['feature_scaling']
    for col, method in scaling_config.items():
        if col not in df.columns:
            logging.warning(f"列 {col} 不存在，跳过特征缩放")
            continue

        # 检查数据是否为空
        if df[col].shape[0] == 0:
            logging.warning(f"列 {col} 数据为空，跳过特征缩放")
            continue

        if method == 'standard':
            scaler = StandardScaler()
            df[col] = scaler.fit_transform(df[[col]])
            scalers[col] = scaler
        elif method == 'minmax':
            scaler = MinMaxScaler()
            df[col] = scaler.fit_transform(df[[col]])
            scalers[col] = scaler
        logging.info(f"列 {col} 特征缩放完成，方法：{method}")
    
    return df, scalers

def data_aggregation(df, config):
    """数据聚合"""
    if 'aggregation' not in config:
        return df

    agg_config = config['aggregation']
    try:
        grouped = df.groupby(agg_config['group_by'])
        df = grouped.agg(agg_config['agg_dict']).reset_index()
        logging.info(f"数据聚合完成，分组字段：{agg_config['group_by']}")
    except Exception as e:
        logging.error(f"数据聚合失败：{str(e)}")
        raise
    return df