# EDA_Circuit_Partitioning_KL/src/core/kl_original.py

"""
kl_original.py - 原始Kernighan-Lin (KL) 算法实现
该模块为预设方案KL算法的实现，并添加了如下功能：
1. 增加收敛判据 （连续patience轮无改善则终止）
2. 运行时间统计 
"""

import networkx as nx
import time
from typing import Set, Tuple, List, Dict

def _calculate_cut_size(G: nx.Graph, partition_A: Set[str], partition_B: Set[str]) -> int:
    """计算两个分区之间的割边数量（考虑权重）。"""
    cut_size = 0
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        if (u in partition_A and v in partition_B) or \
           (u in partition_B and v in partition_A):
            cut_size += weight
    return cut_size

def _calculate_D_values(G: nx.Graph, partition_A: Set[str], partition_B: Set[str]) -> Dict[str, int]:
    """为图中所有节点计算D值 (E(v) - I(v))。"""
    D_values = {}
    nodes = list(partition_A) + list(partition_B)
    
    for node in nodes:
        E_v, I_v = 0, 0
        current_partition = partition_A if node in partition_A else partition_B
        other_partition = partition_B if node in partition_A else partition_A

        for neighbor in G.neighbors(node):
            weight = G.get_edge_data(node, neighbor).get('weight', 1)
            if neighbor in other_partition:
                E_v += weight
            elif neighbor in current_partition:
                I_v += weight
        D_values[node] = E_v - I_v
    return D_values

def kernighan_lin_partition(
    G: nx.Graph, 
    initial_partition: Tuple[Set[str], Set[str]],
    max_passes: int = 10,
    patience: int = 2, # 新增参数：连续多少轮无改善则终止
    verbose: bool = True
) -> Tuple[Set[str], Set[str], int, List[Dict], float]:
    """
    使用 Kernighan-Lin 算法对图进行两路划分（包含提前终止和计时功能）。

    参数:
        G (nx.Graph): 待划分的图。
        initial_partition (Tuple[Set[str], Set[str]]): 初始分区 A 和 B。
        max_passes (int): 最大迭代轮数上限。
        patience (int): 容忍的连续无改善轮数，用于提前终止。
        verbose (bool): 是否打印详细的执行过程信息。

    Returns:
        Tuple[Set[str], Set[str], int, List[Dict], float]:
            - best_partition_A: 优化后的分区A。
            - best_partition_B: 优化后的分区B。
            - best_cut_size: 优化后的最小割边数。
            - history: 记录每轮迭代信息的列表。
            - execution_time: 算法总运行时间（秒）。
    """
    # --- 新功能：开始计时 ---
    start_time = time.perf_counter()

    partition_A, partition_B = initial_partition[0].copy(), initial_partition[1].copy()
    
    best_partition_A = partition_A.copy()
    best_partition_B = partition_B.copy()
    best_cut_size = _calculate_cut_size(G, partition_A, partition_B)
    
    if verbose:
        print(f"--- KL算法开始 ---")
        print(f"初始割边数: {best_cut_size}")

    history = [{'pass': 0, 'cut_size': best_cut_size, 'details': 'Initial state'}]
    
    # --- 新功能：用于提前终止的计数器 ---
    passes_without_improvement = 0

    for pass_num in range(1, max_passes + 1):
        if verbose:
            print(f"\n--- Pass {pass_num} ---")
        
        cut_size_before_pass = best_cut_size

        current_A, current_B = partition_A.copy(), partition_B.copy()
        unlocked_A, unlocked_B = current_A.copy(), current_B.copy()
        D = _calculate_D_values(G, current_A, current_B)
        
        swap_gains = []
        for _ in range(min(len(unlocked_A), len(unlocked_B))):
            best_gain = -float('inf')
            best_pair = (None, None)
            for a in unlocked_A:
                for b in unlocked_B:
                    c_ab = G.get_edge_data(a, b, default={'weight': 0})['weight']
                    gain = D[a] + D[b] - 2 * c_ab
                    if gain > best_gain:
                        best_gain, best_pair = gain, (a, b)
            
            if best_pair == (None, None): break
            a_to_swap, b_to_swap = best_pair
            swap_gains.append({'gain': best_gain, 'pair': (a_to_swap, b_to_swap)})
            unlocked_A.remove(a_to_swap)
            unlocked_B.remove(b_to_swap)
        
        max_cumulative_gain, best_k = 0, -1
        cumulative_gain = 0
        for i, item in enumerate(swap_gains):
            cumulative_gain += item['gain']
            if cumulative_gain > max_cumulative_gain:
                max_cumulative_gain, best_k = cumulative_gain, i

        if verbose:
            print(f"本轮找到 {len(swap_gains)} 个交换对，最大累积增益 G = {max_cumulative_gain} (在第 {best_k + 1} 次交换时达到)。")

        if max_cumulative_gain > 0:
            for i in range(best_k + 1):
                a_swapped, b_swapped = swap_gains[i]['pair']
                partition_A.remove(a_swapped); partition_A.add(b_swapped)
                partition_B.remove(b_swapped); partition_B.add(a_swapped)
            
            current_cut_size = _calculate_cut_size(G, partition_A, partition_B)
            history.append({'pass': pass_num, 'cut_size': current_cut_size, 'details': f'Applied {best_k+1} swaps.'})
            
            if current_cut_size < best_cut_size:
                best_cut_size = current_cut_size
                best_partition_A, best_partition_B = partition_A.copy(), partition_B.copy()
            if verbose:
                print(f"Pass {pass_num} 结束。更新后割边数: {current_cut_size}")
        else:
            if verbose:
                print("最大累积增益 <= 0，算法收敛。")
            break

        # --- 新功能：检查是否需要提前终止 ---
        if best_cut_size < cut_size_before_pass:
            passes_without_improvement = 0 # 有改善，重置计数器
        else:
            passes_without_improvement += 1 # 无改善，计数器+1

        if passes_without_improvement >= patience:
            if verbose:
                print(f"\n连续 {patience} 轮最优割边数未改善，提前终止算法。")
            break

    # --- 新功能：结束计时并计算总时间 ---
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    if verbose:
        print("\n--- KL算法结束 ---")
        print(f"最终最小割边数: {best_cut_size}")
        print(f"总运行时间: {execution_time:.6f} 秒")

    return best_partition_A, best_partition_B, best_cut_size, history, execution_time


# 用于直接测试该模块的演示代码
if __name__ == '__main__':
    import os
    import sys
    import random

    # 确保可以从 core/ 目录导入 utils/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用相对导入需要从项目根目录运行，所以这里假设是从根目录运行
    # 如果要直接运行此文件，需要将src添加到path
    project_root = os.path.dirname(os.path.dirname(script_dir))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    # 使用相对导入
    from src.utils.netlist_parser import parse_netlist_to_graph

    print("--- 运行 kl_algorithm.py (优化版) 演示 ---")

    demo_file_path = os.path.join(project_root, 'data', 'generated_netlists', 'netlist_small_10n_20e.txt')
    
    if not os.path.exists(demo_file_path):
        print(f"错误: 演示文件未找到于 '{demo_file_path}'，请先生成。")
        G = None
    else:
        G = parse_netlist_to_graph(demo_file_path)

    if G:
        print("\n图加载成功。")
        nodes = list(G.nodes())
        random.seed(42) # 固定种子保证结果可复现
        random.shuffle(nodes)
        
        initial_A = set(nodes[:len(nodes)//2])
        initial_B = set(nodes[len(nodes)//2:])
        initial_partition = (initial_A, initial_B)
        
        # 运行KL算法
        final_A, final_B, final_cut_size, history_data, total_time = kernighan_lin_partition(
            G, 
            initial_partition, 
            patience=3, # 设置为3轮无改善就停止，以观察效果
            verbose=True
        )
        
        print("\n--- 历史记录 ---")
        for record in history_data:
            print(f"Pass {record['pass']}: Cut Size = {record['cut_size']}, Details: {record['details']}")
    else:
        print("\n图加载失败，无法运行演示。")