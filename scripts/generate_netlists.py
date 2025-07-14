import networkx as nx
import random
import os

def generate_guaranteed_connected_graph(num_nodes, num_edges, filename, output_dir=None, seed=None):
    """
    生成一个保证连通（无独立节点）的随机图，并以自定义网表格式保存。

    策略:
    1. 创建一个随机树来连接所有节点 (n-1条边)，保证连通性。
    2. 从剩余所有可能的边中，随机选择并添加剩下的 (m - (n-1)) 条边。

    参数:
        num_nodes (int): 图中节点的数量。
        num_edges (int): 图中边的数量。
        filename (str): 输出文件的名称（不包含路径）。
        output_dir (str): 输出文件存放的目录。
        seed (int, optional): 随机数生成器的种子，用于确保可重复性。默认为 None。
    """
    if seed is not None:
        random.seed(seed)

    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, 'data', 'generated_netlists')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建目录: {output_dir}")

    # --- 核心逻辑修改 ---

    # 检查边数是否足够形成连通图
    if num_edges < num_nodes - 1 and num_nodes > 1:
        raise ValueError(f"错误: 请求的边数 {num_edges} 不足以连接 {num_nodes} 个节点。至少需要 {num_nodes - 1} 条边。")
    
    # 检查边数是否超过最大可能
    max_possible_edges = num_nodes * (num_nodes - 1) // 2
    if num_edges > max_possible_edges:
        print(f"警告: 请求的边数 {num_edges} 超过了最大可能值 {max_possible_edges}。将使用最大值。")
        num_edges = max_possible_edges

    nodes = [f"N{i}" for i in range(num_nodes)]
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # 1. 创建一个随机树来保证连通性
    all_nodes = list(nodes)
    random.shuffle(all_nodes)
    
    # 将第一个节点作为起点
    connected_nodes = {all_nodes[0]}
    unconnected_nodes = set(all_nodes[1:])
    
    edges_to_add = []
    
    # 强制连接所有节点
    while unconnected_nodes:
        # 从已连接的节点中随机选一个
        u = random.choice(list(connected_nodes))
        # 从未连接的节点中随机选一个
        v = random.choice(list(unconnected_nodes))
        
        edges_to_add.append(tuple(sorted((u,v))))
        connected_nodes.add(v)
        unconnected_nodes.remove(v)
        
    # 至此连通图构建完成
    # -------------------------------------------------------------

    # 2. 添加剩余的边
    # 创建一个已添加边的集合，方便快速查找
    current_edges = set(edges_to_add)
    
    # 创建所有可能的边对 (不包括自环)
    all_possible_edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            all_possible_edges.append(tuple(sorted((nodes[i], nodes[j]))))
    
    # 从所有可能的边中，过滤掉已经用于构建树的边
    remaining_possible_edges = [edge for edge in all_possible_edges if edge not in current_edges]
    random.shuffle(remaining_possible_edges)

    # 计算还需要添加多少条边
    edges_needed = num_edges - len(edges_to_add)
    
    if edges_needed > 0:
        # 从剩余的可用边中随机选择
        additional_edges = remaining_possible_edges[:edges_needed]
        edges_to_add.extend(additional_edges)

    # 写入文件
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {filename} - Generated Guaranteed Connected Netlist\n")
        f.write(f"# Nodes: {num_nodes}, Edges: {len(edges_to_add)}\n\n")
        # 排序以保证输出的确定性
        for u, v in sorted(edges_to_add):
            f.write(f"{u} {v} 1\n")

    # 在networkx图中添加所有边并验证
    G.add_edges_from(edges_to_add)
    print(f"成功生成保证连通的网表: {filepath} (节点: {G.number_of_nodes()}, 边: {G.number_of_edges()})")
    
    # 验证独立节点 (理论上这里应该永远为空)
    isolates = list(nx.isolates(G))
    if isolates:
        print(f"!!! 警告: 代码逻辑有误，仍然发现了独立节点: {isolates}")
    else:
        print(">>> 验证通过: 图中没有独立节点。")

    return G

# 主程序部分保持不变，只需将函数名替换
if __name__ == "__main__":
    print("--- 开始生成不同规模的、保证连通的网表文件 ---")
    
    # 小规模 (10节点, 20边)
    generate_guaranteed_connected_graph(10, 20, "netlist_small_10n_20e.txt", seed=42)
    
    # 中等规模 (20节点, 40边)
    generate_guaranteed_connected_graph(20, 40, "netlist_medium_20n_40e.txt", seed=42)
    
    # 大规模 (50节点, 100边)
    generate_guaranteed_connected_graph(50, 100, "netlist_large_50n_100e.txt", seed=42)
    
    # 一个边数刚好的例子
    generate_guaranteed_connected_graph(10, 9, "netlist_tree_10n_9e.txt", seed=42)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    final_output_dir = os.path.join(project_root, 'data', 'generated_netlists')
    print(f"\n所有网表文件生成完毕,存放在 '{final_output_dir}' 目录下。")