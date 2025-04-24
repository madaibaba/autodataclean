import os
import pandas as pd
import requests
import json
import argparse

class ConfigGenerator:
    def __init__(self, api_url='http://192.168.200.54:11434/api/generate', model_name='deepseek-coder:33b'):
        self.api_url = api_url
        self.model_name = model_name

    def get_file_type(self, file_path):
        """判断文件类型，支持 'csv', 'parquet', 'json', 'jsonl'"""
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.csv':
            return 'csv'
        elif file_extension == '.parquet':
            return 'parquet'
        elif file_extension == '.json':
            return 'json'
        elif file_extension == '.jsonl':
            return 'jsonl'
        else:
            return None

    def analyze_dataset(self, file_path):
        """分析数据集，返回基本信息"""
        file_type = self.get_file_type(file_path)
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type == 'parquet':
            df = pd.read_parquet(file_path)
        elif file_type == 'json':
            df = pd.read_json(file_path)
        elif file_type == 'jsonl':
            df = pd.read_json(file_path, lines=True)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}。请使用 'csv', 'parquet', 'json' 或 'jsonl' 格式的文件。")
        
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        return {
            "columns": columns,
            "dtypes": {col: str(dtype) for col, dtype in dtypes.items()},
            "rows": df.shape[0],
            "columns_count": df.shape[1]
        }

    def generate_prompt(self, dataset_info, file_path, output_file_path):
        """根据数据集信息生成提示词"""
        file_type = self.get_file_type(file_path)
        prompt = f"""
        我有一个数据集，基本信息如下：
        列名：{dataset_info['columns']}
        数据类型：{dataset_info['dtypes']}
        行数：{dataset_info['rows']}
        列数：{dataset_info['columns_count']}

        请帮我生成一个数据清洗的 JSON 配置文件，包含以下内容：
        - 输入路径（字段名为："input_path"， 假设数据集文件名为 {file_path}）
        - 输出路径（字段名为："output_path"，设置为 {output_file_path}）
        - 输出格式（字段名为："output_format"，设置为 '{file_type}'）
        - 是否生成报告（字段名为："generate_reports"，设置为 true 或者 false）
        - 重复值处理（字段名为："duplicates"，设置为 "remove": true 或者  "remove": false）
        - 异常值处理（字段名为："outliers"，选择 'zscore' 或者 'iqr' 方法，选择合适的列）
        - 文本清洗（字段名为："text_cleaning"，选择合适的列，样例："text_cleaning": {{"columns": ["meal"]}},）
        - 缺失值处理（字段名为："missing_value"，根据数据类型选择合适的填充方法，方法'method'有：'fill', 'ffill', 'statistic'， 'method' 为 'statistic' 时，可以设置 'type' 为 'mean' 或 'median'，也可以不设置 'type'， 每个字段一个子json，样例："company": {{"method": "fill", "value": "No Company"}}）
        - 数据类型转换（字段名为："dtype_conversion"，可以为 'timestamp' 或 'category' 或 根据实际情况转换，样例："reservation_status_date": "timestamp"）
        - 特征缩放（字段名为："feature_scaling"，选择合适的列和 'standard' 或 'minmax' 方法）

        请直接返回 JSON 格式的配置，不要包含其他说明文字。
        """
        return prompt

    def generate_config(self, prompt):
        """调用 Ollama API 生成配置文件"""
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.RequestException as e:
            print(f"调用 Ollama API 时出错: {e}")
            return ""

    def save_config(self, config_str, output_file_path):
        """保存配置文件"""
        try:
            print("尝试解析的 JSON 内容：")
            print(config_str)
            config = json.loads(config_str)
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"配置文件已保存至 {output_file_path}")
            return True
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            print("无法解析生成的 JSON 配置，请检查大模型返回结果。")
            return False

    def run(self, input_file):
        file_type = self.get_file_type(input_file)
        if file_type is None:
            print("不支持的文件类型，请使用 'csv', 'parquet', 'json' 或 'jsonl' 格式的文件。")
            return

        dataset_info = self.analyze_dataset(input_file)
        output_file_path = f"auto_{os.path.basename(input_file).replace('.'+file_type, '.json')}"
        prompt = self.generate_prompt(dataset_info, input_file, f"auto_{os.path.basename(input_file).replace('.'+file_type, '')}")

        max_retries = 5
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            if retry_count > 0:
                print(f"正在进行第 {retry_count + 1} 次重试...")
            config_str = self.generate_config(prompt)
            success = self.save_config(config_str, output_file_path)
            retry_count += 1

        if not success:
            print("达到最大重试次数，仍未能成功生成配置文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='生成数据清洗的 JSON 配置文件')
    parser.add_argument('input_file', help='输入数据集文件路径')
    parser.add_argument('--api_url', default='http://192.168.200.54:11434/api/generate', help='大模型的 API URL')
    parser.add_argument('--model_name', default='deepseek-coder:33b', help='大模型的名字')

    args = parser.parse_args()

    generator = ConfigGenerator(args.api_url, args.model_name)
    generator.run(args.input_file)