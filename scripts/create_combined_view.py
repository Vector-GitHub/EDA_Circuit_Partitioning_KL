# scripts/create_combined_view.py
# 功能：算法工作流可视化启动器。可通过命令行参数选择不同的划分算法，
# 运行后生成并展示包含“原始图->初始划分->最终划分”的3x3组合对比图。

import os
import sys
import argparse
import matplotlib.pyplot as plt
import random
import networkx as nx

# --- 设置路径，确保可以导入src目录下的模块 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# --- 导入所有需要的模块 ---
from src.utils.netlist_parser import parse_netlist_to_graph
from src.utils.graph_visualizer import visualize_partitioned_graph
# 导入三种不同的划分算法
from src.core.base_partitioning import simple_greedy_partition
from src.core.kl_classic import kernighan_lin_partition
from src.core.kl_improvements import kernighan_lin_bfs_init

def main():
    """
    主函数，负责解析命令行参数并启动相应的可视化流程。
    """
    # --- 步骤1: 设置命令行参数解析 ---
    parser = argparse.ArgumentParser(
        description="运行并可视化电路划分算法。支持多种算法策略并生成3x3对比图。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-a', '--algorithm',
        type=str,
        default='kl_random',
        choices=['greedy', 'kl_random', 'kl_bfs'],
        help="""选择要运行的划分算法:
  'greedy'    - 单步最优贪心算法
  'kl_random' - 经典KL算法 (随机初始划分)
  'kl_bfs'    - 改进版KL算法 (BFS初始划分)
"""
    )
    args = parser.parse_args()
    
    # --- 步骤2: 根据参数选择算法和配置 ---
    if args.algorithm == 'greedy':
        partition_func = simple_greedy_partition
        algo_name = "Simple Greedy"
        requires_initial_partition = True
    elif args.algorithm == 'kl_bfs':
        partition_func = kernighan_lin_bfs_init
        algo_name = "KL with BFS Init"
        requires_initial_partition = False
    else: # 默认 'kl_random'
        partition_func = kernighan_lin_partition
        algo_name = "Classic KL (Random Init)"
        requires_initial_partition = True

    print(f"--- 已选择算法: {algo_name} ---")
    
    # --- 步骤3: 运行并生成3x3可视化结果 ---
    run_and_visualize_3x3(partition_func, algo_name, requires_initial_partition)

def run_and_visualize_3x3(partition_func, algo_name, requires_initial_partition):
    """
    对所有规模的网表运行指定的划分算法，并生成3x3的组合图像。
    """
    netlist_configs = [
        {"path": "data/generated_netlists/netlist_small_10n_20e.txt", "title": "Small Scale"},
        {"path": "data/generated_netlists/netlist_medium_20n_40e.txt", "title": "Medium Scale"},
        {"path": "data/generated_netlists/netlist_large_50n_100e.txt", "title": "Large Scale"}
    ]

    # --- 关键改动：创建3行3列的子图 ---
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(24, 21))
    fig.suptitle(f'{algo_name} Full Process: Original -> Initial -> Final', fontsize=22)

    for i, config in enumerate(netlist_configs):
        netlist_path = os.path.join(project_root, config['path'])
        print(f"\n--- 处理: {config['title']} ---")

        original_graph = parse_netlist_to_graph(netlist_path)

        if original_graph:
            # --- 步骤A: 在第1列绘制原始图 ---
            ax_original = axes[i, 0]
            visualize_partitioned_graph(
                original_graph, ax=ax_original,
                title=f"{config['title']}\nOriginal Graph",
                layout_style='spring'
            )

            # --- 步骤B: 运行所选的划分算法 ---
            if requires_initial_partition:
                nodes = list(original_graph.nodes())
                random.seed(42)
                random.shuffle(nodes)
                initial_A = set(nodes[:len(nodes)//2])
                initial_B = set(nodes[len(nodes)//2:])
                _, _, final_cut_size, history, _, initial_graph, final_graph = partition_func(
                    original_graph, (initial_A, initial_B), verbose=False
                )
            else:
                _, _, final_cut_size, history, _, initial_graph, final_graph = partition_func(
                    original_graph, verbose=False
                )
            
            initial_cut_size = history[0].get('cut_size', 'N/A')
            print(f"算法执行完毕。初始割边数: {initial_cut_size}, 最终割边数: {final_cut_size}")

            # --- 步骤C: 在第2列绘制初始划分图 ---
            ax_initial = axes[i, 1]
            visualize_partitioned_graph(
                initial_graph, ax=ax_initial,
                title=f"{config['title']}\nInitial Partition (Cut: {initial_cut_size})",
                layout_style='bipartite'
            )
            
            # --- 步骤D: 在第3列绘制最终划分图 ---
            ax_final = axes[i, 2]
            visualize_partitioned_graph(
                final_graph, ax=ax_final,
                title=f"{config['title']}\nFinal Partition (Cut: {final_cut_size})",
                layout_style='bipartite'
            )
        else:
            for j in range(3):
                axes[i, j].set_title(f"{config['title']} - Failed: Netlist not found")
                axes[i, j].axis('off')

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    
    output_image_dir = os.path.join(project_root, 'results', 'images')
    os.makedirs(output_image_dir, exist_ok=True)
    
    output_filename = f'full_results_{algo_name.lower().replace(" ", "_")}.png'
    output_image_path = os.path.join(output_image_dir, output_filename)
    
    plt.savefig(output_image_path)
    print(f"\n[成功] {algo_name} 的3x3完整对比图像已保存到: {output_image_path}")
    plt.show()

if __name__ == '__main__':
    main()