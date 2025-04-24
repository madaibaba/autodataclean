import pandas as pd
import logging

def load_data(config):
    """加载数据，支持 CSV、Parquet、JSON 和 JSONL 格式"""
    input_path = config['input_path']
    try:
        if input_path.lower().endswith('.csv'):
            # 使用 utf-8 编码，并指定编码错误处理方式为替换
            df = pd.read_csv(input_path, encoding='utf-8', encoding_errors='replace')
        elif input_path.lower().endswith('.parquet'):
            df = pd.read_parquet(input_path)
        elif input_path.lower().endswith('.json'):
            df = pd.read_json(input_path)
        elif input_path.lower().endswith('.jsonl'):
            df = pd.read_json(input_path, lines=True)
        else:
            raise ValueError(f"不支持的文件格式: {input_path}")
        logging.info(f"成功加载数据，形状：{df.shape}")
        return df
    except FileNotFoundError:
        logging.error("输入文件不存在")
        raise
    except Exception as e:
        logging.error(f"数据加载失败：{str(e)}")
        raise