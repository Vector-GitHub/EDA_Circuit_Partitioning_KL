# EDA_Circuit_Partitioning_KL/src/core/kl_classic.py

"""
kl_classic.py - 经典Kernighan-Lin (KL) 算法实现
该模块严格遵循B. W. Kernighan and S. Lin发表的原始论文
"An Efficient Heuristic Procedure for Partitioning Graphs",
并添加了如下功能：
1. 运行时间统计
2. 最大迭代轮次上限设置
3. (新) 输出带有分区信息的初始和最终图对象，用于可视化。
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
    """为图中所有节点计算初始D值 (E(v) - I(v))。"""
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
    verbose: bool = True
) -> Tuple[Set[str], Set[str], int, List[Dict], float, nx.Graph, nx.Graph]:
    """
    使用经典Kernighan-Lin算法对图进行两路划分。
    此实现严格遵循原始论文，包含轮次内D值更新。

    Returns:
        Tuple[...]:
            - ... (原有返回项)
            - initial_graph (nx.Graph): 带有初始分区信息的图对象。
            - final_graph (nx.Graph): 带有最终分区信息的图对象。
    """
    start_time = time.perf_counter()

    partition_A, partition_B = initial_partition[0].copy(), initial_partition[1].copy()
    
    # --- 新功能：创建带有初始分区信息的图 ---
    initial_graph = G.copy()
    for node in partition_A:
        initial_graph.nodes[node]['partition'] = 'A'
    for node in partition_B:
        initial_graph.nodes[node]['partition'] = 'B'
    
    best_partition_A = partition_A.copy()
    best_partition_B = partition_B.copy()
    best_cut_size = _calculate_cut_size(G, partition_A, partition_B)
    
    if verbose:
        print(f"--- KL算法开始 (遵从原始论文) ---")
        print(f"初始割边数: {best_cut_size}")

    history = [{'pass': 0, 'cut_size': best_cut_size, 'details': 'Initial state'}]
    
    # ... (算法核心循环部分保持不变)
    for pass_num in range(1, max_passes + 1):
        if verbose: print(f"\n--- Pass {pass_num} ---")
        D = _calculate_D_values(G, partition_A, partition_B)
        current_A, current_B = partition_A.copy(), partition_B.copy()
        unlocked_A, unlocked_B = current_A.copy(), current_B.copy()
        swap_history = []
        for _ in range(min(len(current_A), len(current_B))):
            best_gain, best_pair = -float('inf'), (None, None)
            for a in unlocked_A:
                for b in unlocked_B:
                    c_ab = G.get_edge_data(a, b, default={'weight': 0})['weight']
                    gain = D[a] + D[b] - 2 * c_ab
                    if gain > best_gain:
                        best_gain, best_pair = gain, (a, b)
            if best_pair == (None, None): break
            a_swap, b_swap = best_pair
            swap_history.append({'gain': best_gain, 'pair': (a_swap, b_swap)})
            unlocked_A.remove(a_swap)
            unlocked_B.remove(b_swap)
            for u in unlocked_A:
                c_ua = G.get_edge_data(u, a_swap, default={'weight': 0})['weight']
                c_ub = G.get_edge_data(u, b_swap, default={'weight': 0})['weight']
                D[u] += 2 * c_ua - 2 * c_ub
            for v in unlocked_B:
                c_va = G.get_edge_data(v, a_swap, default={'weight': 0})['weight']
                c_vb = G.get_edge_data(v, b_swap, default={'weight': 0})['weight']
                D[v] += 2 * c_vb - 2 * c_va
        max_cumulative_gain, best_k = 0, -1
        cumulative_gain = 0
        for i, item in enumerate(swap_history):
            cumulative_gain += item['gain']
            if cumulative_gain > max_cumulative_gain:
                max_cumulative_gain, best_k = cumulative_gain, i
        if verbose: print(f"本轮找到 {len(swap_history)} 个交换对，最大累积增益 G = {max_cumulative_gain} (在第 {best_k + 1} 次交换时达到)。")
        if max_cumulative_gain > 0:
            for i in range(best_k + 1):
                a_swapped, b_swapped = swap_history[i]['pair']
                partition_A.remove(a_swapped); partition_A.add(b_swapped)
                partition_B.remove(b_swapped); partition_B.add(a_swapped)
            current_cut_size = _calculate_cut_size(G, partition_A, partition_B)
            history.append({'pass': pass_num, 'cut_size': current_cut_size, 'details': f'Applied {best_k+1} swaps.'})
            if current_cut_size < best_cut_size:
                best_cut_size = current_cut_size
                best_partition_A, best_partition_B = partition_A.copy(), partition_B.copy()
            if verbose: print(f"Pass {pass_num} 结束。更新后割边数: {current_cut_size}")
        else:
            if verbose: print("最大累积增益 <= 0，算法收敛。")
            break

    # --- 新功能：创建带有最终分区信息的图 ---
    final_graph = G.copy()
    for node in best_partition_A:
        final_graph.nodes[node]['partition'] = 'A'
    for node in best_partition_B:
        final_graph.nodes[node]['partition'] = 'B'

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    if verbose:
        print("\n--- KL算法结束 ---")
        print(f"最终最小割边数: {best_cut_size}")
        print(f"总运行时间: {execution_time:.6f} 秒")

    return best_partition_A, best_partition_B, best_cut_size, history, execution_time, initial_graph, final_graph
