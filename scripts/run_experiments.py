# scripts/run_experiments.py - 数据统计与分析实验启动器
# 功能：按照要求对三种算法进行多次实验，计算最大/平均割边减少率、运行时间和稳定性，并生成CSV报告与对比图。
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import random
import networkx as nx

# --- 设置路径，确保可以导入src目录下的模块 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# --- 导入所有需要的模块 ---
from src.utils.netlist_parser import parse_netlist_to_graph
from src.core.base_partitioning import simple_greedy_partition
from src.core.kl_classic import kernighan_lin_partition
from src.core.kl_improvements import kernighan_lin_bfs_init

# --- 实验参数配置 ---
NUM_RUNS = 20  # 每种情况运行20次

# --- 算法配置 ---
ALGORITHMS = {
    'greedy': {
        'func': simple_greedy_partition, 
        'csv_path': 'results/generate_data/baseline_performance.csv', 
        'name': 'Simple Greedy',
        'requires_initial_partition': True
    },
    'kl_random': {
        'func': kernighan_lin_partition, 
        'csv_path': 'results/generate_data/kl_classic_performance.csv', 
        'name': 'Classic KL (Random Init)',
        'requires_initial_partition': True
    },
    'kl_bfs': {
        'func': kernighan_lin_bfs_init, 
        'csv_path': 'results/generate_data/kl_improvements_performance.csv', 
        'name': 'KL with BFS Init',
        'requires_initial_partition': False
    }
}

# --- 网表规模配置 ---
NETLIST_CONFIGS = {
    'Small (10n, 20e)': {"path": "data/generated_netlists/netlist_small_10n_20e.txt"},
    'Medium (20n, 40e)': {"path": "data/generated_netlists/netlist_medium_20n_40e.txt"},
    'Large (50n, 100e)': {"path": "data/generated_netlists/netlist_large_50n_100e.txt"}
}

def run_all_experiments():
    """
    主函数，执行所有实验，并生成报告和图表。
    """
    # 确保输出目录存在
    os.makedirs(os.path.join(project_root, 'results', 'generate_data'), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'results', 'images'), exist_ok=True)

    all_results = {}

    for algo_key, algo_info in ALGORITHMS.items():
        print(f"\n{'='*20} 开始测试算法: {algo_info['name']} {'='*20}")
        
        # 准备DataFrame，使用英文作为列和索引
        scale_columns = list(NETLIST_CONFIGS.keys())
        metric_rows = [
            'Max Cut-edge Reduction Rate', 'Average Cut-edge Reduction Rate', 
            'Average Algorithm Runtime (s)', 'Result Stability (Std Dev)'
        ]
        results_df = pd.DataFrame(index=metric_rows, columns=scale_columns)

        for i, (scale_name, scale_config) in enumerate(NETLIST_CONFIGS.items()):
            print(f"\n--- 处理规模: {scale_name} ---")
            netlist_path = os.path.join(project_root, scale_config['path'])
            graph = parse_netlist_to_graph(netlist_path)

            if not graph:
                print(f"错误：找不到网表文件 {netlist_path}，跳过此规模。")
                continue

            run_final_cuts, run_times, run_reduction_rates = [], [], []

            for run_idx in range(NUM_RUNS):
                random.seed(run_idx)  # 保证每次实验的20次随机种子都一样
                
                initial_cut_size = -1
                if algo_info['requires_initial_partition']:
                    nodes = list(graph.nodes())
                    random.shuffle(nodes)
                    initial_A = set(nodes[:graph.number_of_nodes()//2])
                    initial_B = set(nodes[graph.number_of_nodes()//2:])
                    initial_cut_size = _calculate_cut_size(graph, initial_A, initial_B)
                    _, _, final_cut, _, exec_time, _, _ = algo_info['func'](graph, (initial_A, initial_B), verbose=False)
                else:
                    _, _, final_cut, history, exec_time, _, _ = algo_info['func'](graph, start_node=random.choice(list(graph.nodes())), verbose=False)
                    initial_cut_size = history[0]['cut_size']

                reduction_rate = (initial_cut_size - final_cut) / initial_cut_size if initial_cut_size > 0 else 0
                
                run_final_cuts.append(final_cut)
                run_times.append(exec_time)
                run_reduction_rates.append(reduction_rate)
                
                print(f"  Run {run_idx+1}/{NUM_RUNS}: Initial Cut = {initial_cut_size}, Final Cut = {final_cut}, Reduction Rate = {reduction_rate:.2%}")

            # 计算统计指标
            max_reduction_rate = np.max(run_reduction_rates)
            avg_reduction_rate = np.mean(run_reduction_rates)
            avg_exec_time = np.mean(run_times)
            std_dev_cut = np.std(run_final_cuts)

            # 填充DataFrame
            df_col_name = scale_columns[i]
            results_df.loc['Max Cut-edge Reduction Rate', df_col_name] = f"{max_reduction_rate:.2%}"
            results_df.loc['Average Cut-edge Reduction Rate', df_col_name] = f"{avg_reduction_rate:.2%}"
            results_df.loc['Average Algorithm Runtime (s)', df_col_name] = f"{avg_exec_time:.6f}"
            results_df.loc['Result Stability (Std Dev)', df_col_name] = f"{std_dev_cut:.4f}"

        csv_filepath = os.path.join(project_root, algo_info['csv_path'])
        results_df.to_csv(csv_filepath, encoding='utf-8-sig')
        print(f"\n[成功] {algo_info['name']} 的性能报告已保存到: {csv_filepath}")
        
        all_results[algo_info['name']] = results_df

    create_comparison_plot(all_results)

def create_comparison_plot(all_results):
    """
    根据所有算法的实验结果，生成一个4合1的对比折线图。
    """
    print("\n--- 开始生成四合一性能对比图 ---")
    
    # 准备绘图数据
    labels = list(NETLIST_CONFIGS.keys()) # X轴标签
    metrics_to_plot = {
        'Max Cut-edge Reduction Rate': 'Max Cut-edge Reduction Rate Across Scales',
        'Average Cut-edge Reduction Rate': 'Average Cut-edge Reduction Rate Across Scales',
        'Average Algorithm Runtime (s)': 'Average Algorithm Runtime (s) Across Scales',
        'Result Stability (Std Dev)': 'Result Stability (Std Dev) Across Scales'
    }
    colors = {'Simple Greedy': 'green', 'Classic KL (Random Init)': 'blue', 'KL with BFS Init': 'orange'}
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    axes = axes.flatten()
    fig.suptitle('Performance Comparison of Partitioning Algorithms', fontsize=22)
    
    for i, (metric_row_name, metric_title) in enumerate(metrics_to_plot.items()):
        ax = axes[i]
        for algo_name, results_df in all_results.items():
            # 提取数据时，要去除百分号并转换为数值
            values_str = results_df.loc[metric_row_name, :].str.replace('%', '').to_numpy(dtype=float)
            # 如果是百分比，除以100变回小数
            if '%' in results_df.loc[metric_row_name].iloc[0]:
                values = values_str / 100
            else:
                values = values_str
                
            ax.plot(labels, values, marker='o', linestyle='-', label=algo_name, color=colors[algo_name], linewidth=2.5, markersize=8)
        
        ax.set_title(metric_title, fontsize=16)
        ax.set_ylabel(metric_row_name, fontsize=12)
        ax.set_xlabel("Netlist Scale", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(fontsize=10)

        # 对百分比的Y轴进行特殊格式化
        if 'Reduction Rate' in metric_row_name:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    output_path = os.path.join(project_root, 'results', 'images', 'experiments_results.png')
    plt.savefig(output_path)
    print(f"[成功] 性能对比图已保存到: {output_path}")
    plt.show()

def _calculate_cut_size(G, p_A, p_B):
    """辅助函数，用于计算初始割边数。"""
    cut_size = 0
    for u, v in G.edges():
        if (u in p_A and v in p_B) or (u in p_B and v in p_A):
            cut_size += 1
    return cut_size

if __name__ == '__main__':
    if not all(os.path.exists(os.path.join(project_root, v['path'])) for v in NETLIST_CONFIGS.values()):
        print("\n!!! 警告: 部分或全部网表文件不存在。")
        print("请先运行 'python scripts/generate_netlists.py' 来生成测试数据。")
    else:
        run_all_experiments()