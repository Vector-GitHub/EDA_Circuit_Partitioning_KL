"""
netlist_parser.py - 网表解析器与图构建工具
该模块用于解析电路网表文件，并构建一个 NetworkX 图对象。
"""

import networkx as nx
from typing import Union, Optional  

def parse_netlist_to_graph(file_path: str) -> Optional[nx.Graph]:
    """
    解析一个网表文件并构建一个 NetworkX 图。

    该函数会忽略注释行和空行，并动态地从边列表构建图。

    兼容的网表格式 (由 generate_netlists.py 生成):
    ----------------------------------------------------
    # 注释行以 '#' 开头。
    # 每行代表一条边，格式为: <节点A> <节点B> [权重]
    # 权重是可选的，但解析器会处理它。节点名称为字符串。

    参数:
        file_path (str): 网表文件的完整路径。

    Returns:
        Optional[nx.Graph]: 代表电路的 NetworkX Graph 对象。
                            若文件不存在或解析失败，则返回 None。
    """
    # 将函数返回值的描述从Args部分移到Returns部分
    graph = nx.Graph()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 忽略空行和注释
                if not line or line.startswith('#'):
                    continue

                parts = line.split()

                # 期望每行至少有两个部分（节点A, 节点B）
                if len(parts) >= 2 and parts[0].startswith('N') and parts[1].startswith('N'):
                    u, v = parts[0], parts[1]
                    # 如果提供了权重信息，可以将其作为边的属性添加
                    weight = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
                    graph.add_edge(u, v, weight=weight)
                else:
                    # 只有不满足上述严格条件的行才会被认为是格式错误
                    print(f"警告：跳过格式不正确的行: '{line}'")

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
        return None
    except Exception as e:
        print(f"解析文件 '{file_path}' 时发生意外错误: {e}")
        return None

    print(f"成功解析 '{file_path}': 共找到 {graph.number_of_nodes()} 个节点和 {graph.number_of_edges()} 条边。")
    return graph