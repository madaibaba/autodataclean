import pandas as pd
import logging
from .data_loader import load_data
from .data_cleaner import handle_duplicates, handle_outliers, clean_text, handle_missing_values
from .data_processor import convert_data_types, feature_scaling, data_aggregation
from .report_generator import generate_visualization_report, generate_data_quality_comparison_report
import os
from .template_generator import create_report_template
import json
import argparse
from .generate_config import ConfigGenerator  # 导入封装好的类

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessingPipeline:
    """数据清洗处理管道"""
    
    def __init__(self, config_path):
        """
        初始化处理管道
        :param config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logging.error(f"配置文件 {config_path} 未找到")
            raise
        except Exception as e:
            logging.error(f"读取配置文件 {config_path} 失败: {str(e)}")
            raise
        self.df = None
        self.scalers = {}

    def run(self):
        """执行完整处理流程"""
        try:
            self.df = load_data(self.config)
            original_df = self.df.copy()  # 保存原始数据副本
            self.df = handle_duplicates(self.df, self.config)
            self.df = handle_outliers(self.df, self.config)
            self.df = clean_text(self.df, self.config)
            self.df = handle_missing_values(self.df, self.config)
            self.df, self.scalers = feature_scaling(self.df, self.config)
            self.df = data_aggregation(self.df, self.config)
            # 保存数据
            output_dir = self.config['output_path']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_format = self.config.get('output_format', 'csv')
            if output_format == 'csv':
                output_file_path = os.path.join(output_dir, f"cleaned.csv")
                self.df.to_csv(output_file_path, index=False)
            elif output_format == 'parquet':
                output_file_path = os.path.join(output_dir, f"cleaned.parquet")
                self.df.to_parquet(output_file_path)
            elif output_format == 'json':
                output_file_path = os.path.join(output_dir, f"cleaned.json")
                self.df.to_json(output_file_path)
            elif output_format == 'jsonl':
                output_file_path = os.path.join(output_dir, f"cleaned.jsonl")
                self.df.to_json(output_file_path, orient='records', lines=True)
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")
            
            logging.info(f"处理结果已保存至 {output_file_path}")

            generate_visualization_report(self.df, original_df, self.config)
            generate_data_quality_comparison_report(self.df, original_df, self.config)
        except Exception as e:
            logging.error(f"数据处理流程异常终止：{str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='数据清洗处理管道')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dataset', help='输入数据集文件路径')
    group.add_argument('--config', help='指定 JSON 配置文件路径')
    parser.add_argument('--api_url', default='http://192.168.200.54:11434/api/generate', help='大模型的 API URL')
    parser.add_argument('--model_name', default='deepseek-coder:33b', help='大模型的名字')

    args = parser.parse_args()

    if args.dataset:
        # 生成配置文件
        generator = ConfigGenerator(api_url=args.api_url, model_name=args.model_name)
        generator.run(args.dataset)
        output_file_path = f"auto_{os.path.basename(args.dataset).replace('.csv', '.json')}"
        print(f"JSON 配置文件已生成至 {output_file_path}")

        # 开始数据清洗
        create_report_template()
        try:
            pipeline = DataProcessingPipeline(output_file_path)
            pipeline.run()
        except Exception as e:
            logging.error(f"主程序异常：{str(e)}")
        finally:
            # 确保在生成报告之后再删除模板文件
            if os.path.exists("report_template.html"):
                os.remove("report_template.html")
    elif args.config:
        # 创建报告模板文件
        create_report_template()

        try:
            pipeline = DataProcessingPipeline(args.config)
            pipeline.run()
        except Exception as e:
            logging.error(f"主程序异常：{str(e)}")
        finally:
            # 确保在生成报告之后再删除模板文件
            if os.path.exists("report_template.html"):
                os.remove("report_template.html")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()