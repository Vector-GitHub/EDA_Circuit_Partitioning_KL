# src/core/base_partitioning.py

"""
base_partitioning.py - 基线划分算法：单步最优贪心策略
该模块实现了一个简单的贪心划分算法，作为KL算法的对照组。
它的策略是：在每一步都寻找并执行能带来最大即时收益的单次节点对交换。
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

def simple_greedy_partition(
    G: nx.Graph, 
    initial_partition: Tuple[Set[str], Set[str]],
    max_iterations: int = 100,
    verbose: bool = True
) -> Tuple[Set[str], Set[str], int, List[Dict], float, nx.Graph, nx.Graph]:
    """
    使用单步最优贪心策略对图进行两路划分。

    参数:
        G (nx.Graph): 待划分的图。
        initial_partition (Tuple[Set[str], Set[str]]): 初始分区 A 和 B。
        max_iterations (int): 最大迭代轮数上限，作为安全终止条件。
        verbose (bool): 是否打印详细的执行过程信息。

    Returns:
        Tuple[...]: (与kl_classic.py的返回接口完全一致)
            - final_partition_A, final_partition_B: 优化后的分区。
            - final_cut_size: 优化后的最小割边数。
            - history: 记录每轮迭代信息的列表。
            - execution_time: 算法总运行时间（秒）。
            - initial_graph: 带有初始分区信息的图对象。
            - final_graph: 带有最终分区信息的图对象。
    """
    start_time = time.perf_counter()

    partition_A, partition_B = initial_partition[0].copy(), initial_partition[1].copy()
    
    initial_graph = G.copy()
    for node in partition_A:
        initial_graph.nodes[node]['partition'] = 'A'
    for node in partition_B:
        initial_graph.nodes[node]['partition'] = 'B'
    
    initial_cut_size = _calculate_cut_size(G, partition_A, partition_B)
    history = [{'iteration': 0, 'cut_size': initial_cut_size, 'details': 'Initial state'}]
    
    if verbose:
        print(f"--- 简单贪心算法开始 ---")
        print(f"初始割边数: {initial_cut_size}")

    for iter_num in range(1, max_iterations + 1):
        if verbose:
            print(f"\n--- Iteration {iter_num} ---")
        
        # 1. 计算当前分区的D值
        D = _calculate_D_values(G, partition_A, partition_B)
        
        # 2. 寻找能带来最大即时收益的单步交换
        best_gain_this_iter = 0  # 只考虑正增益
        best_pair_to_swap = None
        
        for a in partition_A:
            for b in partition_B:
                c_ab = G.get_edge_data(a, b, default={'weight': 0})['weight']
                gain = D[a] + D[b] - 2 * c_ab
                if gain > best_gain_this_iter:
                    best_gain_this_iter = gain
                    best_pair_to_swap = (a, b)
        
        # 3. 决策与执行
        if best_pair_to_swap:
            a_swap, b_swap = best_pair_to_swap
            
            # 永久执行交换
            partition_A.remove(a_swap); partition_A.add(b_swap)
            partition_B.remove(b_swap); partition_B.add(a_swap)
            
            current_cut_size = _calculate_cut_size(G, partition_A, partition_B)
            history.append({
                'iteration': iter_num, 
                'cut_size': current_cut_size, 
                'details': f"Swapped {a_swap} and {b_swap} with gain {best_gain_this_iter:.2f}"
            })
            if verbose:
                print(f"执行交换: {a_swap} <-> {b_swap} (Gain: {best_gain_this_iter:.2f})")
                print(f"Iteration {iter_num} 结束。更新后割边数: {current_cut_size}")
        else:
            # 如果找不到任何正增益的交换，则算法收敛
            if verbose:
                print("找不到任何可产生正增益的交换，算法收敛。")
            break
            
    # 在循环结束后整理最终结果
    final_cut_size = _calculate_cut_size(G, partition_A, partition_B)
    
    final_graph = G.copy()
    for node in partition_A:
        final_graph.nodes[node]['partition'] = 'A'
    for node in partition_B:
        final_graph.nodes[node]['partition'] = 'B'
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    if verbose:
        print("\n--- 简单贪心算法结束 ---")
        print(f"最终最小割边数: {final_cut_size}")
        print(f"总运行时间: {execution_time:.6f} 秒")
        
    return partition_A, partition_B, final_cut_size, history, execution_time, initial_graph, final_graph