# EDA_Circuit_Partitioning_KL/src/core/kl_improvements.py

"""
kl_improvements.py - KL算法改进策略：BFS初始划分
该模块实现了对经典KL算法的改进。它不接受外部的初始划分，
而是使用广度优先搜索（BFS）策略来生成一个高质量的初始划分，
旨在减少后续KL算法的迭代次数并可能获得更好的结果。
"""

import networkx as nx
import time
import random
from typing import Set, Tuple, List, Dict, Optional

# --- 从 kl_classic.py 中复用的辅助函数 ---

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

# --- 核心改进：BFS初始划分函数 ---

def _create_bfs_initial_partition(
    G: nx.Graph, 
    start_node: Optional[str] = None
) -> Tuple[Set[str], Set[str]]:
    """
    使用广度优先搜索(BFS)创建一个初始划分。
    
    参数:
        G (nx.Graph): 输入图。
        start_node (Optional[str]): BFS的起始节点。如果为None，则随机选择一个。
        
    Returns:
        Tuple[Set[str], Set[str]]: 分区A和分区B的节点集合。
    """
    if not start_node:
        start_node = random.choice(list(G.nodes()))
        
    # 执行BFS并按遍历顺序列出节点
    bfs_nodes = list(nx.bfs_tree(G, source=start_node).nodes())
    
    # 将前一半节点放入A区，后一半放入B区
    num_nodes_A = G.number_of_nodes() // 2
    partition_A = set(bfs_nodes[:num_nodes_A])
    partition_B = set(bfs_nodes[num_nodes_A:])
    
    return partition_A, partition_B

# --- 改进后的KL主函数 ---

def kernighan_lin_bfs_init(
    G: nx.Graph, 
    max_passes: int = 10,
    start_node: Optional[str] = None,
    verbose: bool = True
) -> Tuple[Set[str], Set[str], int, List[Dict], float, nx.Graph, nx.Graph]:
    """
    使用带有BFS初始划分的经典KL算法对图进行两路划分。

    参数:
        G (nx.Graph): 待划分的图。
        max_passes (int): 最大迭代轮数上限。
        start_node (Optional[str]): BFS的起始节点。
        verbose (bool): 是否打印详细的执行过程信息。

    Returns:
        (与kl_classic.py的返回接口完全一致)
    """
    start_time = time.perf_counter()

    # --- 关键改动：调用BFS函数生成初始划分，而非接收外部传入 ---
    partition_A, partition_B = _create_bfs_initial_partition(G, start_node)
    
    initial_graph = G.copy()
    for node in partition_A:
        initial_graph.nodes[node]['partition'] = 'A'
    for node in partition_B:
        initial_graph.nodes[node]['partition'] = 'B'
    
    best_partition_A = partition_A.copy()
    best_partition_B = partition_B.copy()
    best_cut_size = _calculate_cut_size(G, partition_A, partition_B)
    
    if verbose:
        print(f"--- KL算法开始 (使用BFS初始划分) ---")
        print(f"BFS生成的初始割边数: {best_cut_size}")

    history = [{'pass': 0, 'cut_size': best_cut_size, 'details': 'BFS Initial state'}]
    
    # 后续的KL核心优化流程与 kl_classic.py 完全相同
    for pass_num in range(1, max_passes + 1):
        # ... (这部分代码与 kl_classic.py 相同)
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
            unlocked_A.remove(a_swap); unlocked_B.remove(b_swap)
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

    final_graph = G.copy()
    for node in best_partition_A:
        final_graph.nodes[node]['partition'] = 'A'
    for node in best_partition_B:
        final_graph.nodes[node]['partition'] = 'B'

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    if verbose:
        print("\n--- KL算法 (BFS初始划分) 结束 ---")
        print(f"最终最小割边数: {best_cut_size}")
        print(f"总运行时间: {execution_time:.6f} 秒")

    return best_partition_A, best_partition_B, best_cut_size, history, execution_time, initial_graph, final_graph