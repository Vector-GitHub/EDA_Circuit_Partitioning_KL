"""
graph_visualizer.py - 图可视化工具 (增强版)
该模块提供函数，用于将电路网络的 NetworkX 图对象进行可视化。
新增功能可以根据节点的分区属性进行着色，并高亮割边。
改进：可调整节点大小和标签字号，并使用自定义布局使分区更清晰。
新功能：支持 'spring' 和 'bipartite' 两种布局样式。
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict, Tuple

def _create_bipartite_layout(graph: nx.Graph) -> Dict[str, Tuple[float, float]]:
    """
    创建一个将节点按'partition'属性分为左右两列的布局。
    """
    pos = {}
    nodes_A, nodes_B = [], []

    for node in graph.nodes():
        if graph.nodes[node].get('partition') == 'A':
            nodes_A.append(node)
        else:
            nodes_B.append(node)

    y_A = np.linspace(1, 0, len(nodes_A)) if nodes_A else []
    for i, node in enumerate(nodes_A):
        pos[node] = (-1, y_A[i])

    y_B = np.linspace(1, 0, len(nodes_B)) if nodes_B else []
    for i, node in enumerate(nodes_B):
        pos[node] = (1, y_B[i])
        
    return pos

def visualize_partitioned_graph(
    graph: nx.Graph, 
    ax: Optional[plt.Axes] = None, 
    title: str = "Partitioned Graph",
    layout_style: str = 'spring'  # <-- 新增参数，默认为'spring'
):
    """
    可视化一个已分区的 NetworkX 图，支持多种布局样式。
    """
    if not isinstance(graph, nx.Graph) or graph.number_of_nodes() == 0:
        print("错误：传入的不是一个有效的或非空的图，无法进行可视化。")
        return

    # --- 关键改动：根据 layout_style 选择布局 ---
    if layout_style == 'bipartite':
        pos = _create_bipartite_layout(graph)
    else:  # 默认为 spring 布局
        pos = nx.spring_layout(graph, seed=42)
    
    node_colors = []
    # 如果节点有分区信息，则按分区着色，否则使用默认颜色
    if 'partition' in next(iter(graph.nodes(data=True)))[1]:
        for node in graph.nodes():
            partition = graph.nodes[node].get('partition')
            node_colors.append('skyblue' if partition == 'A' else 'lightcoral')
        
        internal_edges, cut_edges = [], []
        for u, v in graph.edges():
            part_u = graph.nodes[u].get('partition')
            part_v = graph.nodes[v].get('partition')
            if part_u is not None and part_u == part_v:
                internal_edges.append((u, v))
            else:
                cut_edges.append((u, v))
    else: # 没有分区信息，所有节点同色，所有边同一样式
        node_colors = 'skyblue'
        internal_edges = list(graph.edges())
        cut_edges = []

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        show_plot = True
    else:
        show_plot = False

    node_size = 500
    font_size = 9

    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=node_size)
    
    # 绘制内部边或普通边
    nx.draw_networkx_edges(
        graph, pos, ax=ax, 
        edgelist=internal_edges, 
        edge_color='dimgray',
        width=1.2,
        style='solid'
    )
    
    # 仅在有割边时绘制
    if cut_edges:
        nx.draw_networkx_edges(
            graph, pos, ax=ax, 
            edgelist=cut_edges, 
            edge_color='red', 
            width=1.5, 
            style='dashed'
        )

    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=font_size, font_weight='bold')
    ax.set_title(title, fontsize=14)
    ax.axis('off')
    
    if show_plot:
        plt.tight_layout()
        plt.show()

# (旧函数保持不变，但现在我们通常直接使用上面的函数)
def visualize_graph(graph: nx.Graph, title: str = "Circuit Graph"):
    visualize_partitioned_graph(graph, title=title, layout_style='spring')