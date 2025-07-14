"""
test_graph_visualizer.py - 图可视化功能的集成测试

该脚本用于测试从网表生成到图形化显示的完整流程。它将：
1. 调用 generate_netlists.py 来创建测试数据。
2. 调用 netlist_parser.py 来解析这些数据。
3. 调用 graph_visualizer.py 将所有图合并显示并保存为单个文件。
"""
import os
import sys
import matplotlib.pyplot as plt

# --- 步骤 1: 设置模块导入路径 ---
# 获取当前测试脚本的目录 (EDA_Circuit_Partitioning_KL/tests/)
test_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录 (EDA_Circuit_Partitioning_KL/)
project_root = os.path.dirname(test_dir)
# 将项目根目录添加到 sys.path，以便导入 src 和 scripts 中的模块
sys.path.insert(0, project_root)

# --- 步骤 2: 导入项目模块 ---
try:
    from scripts.generate_netlists import generate_guaranteed_connected_graph
    from src.utils.netlist_parser import parse_netlist_to_graph
    from src.utils.graph_visualizer import draw_graph_on_ax 
except ImportError as e:
    print(f"错误：无法导入必要的模块。请确保项目结构正确，且脚本是从项目根目录运行的。")
    print(f"Import Error: {e}")
    sys.exit(1)

# --- 步骤 3: 定义测试配置 ---
NETLIST_CONFIGS = [
    {
        "nodes": 10,
        "edges": 20,
        "filename": "test_netlist_small.txt",
        "title": "Test Graph - Small Scale"
    },
    {
        "nodes": 20,
        "edges": 40,
        "filename": "test_netlist_medium.txt",
        "title": "Test Graph - Medium Scale"
    },
    {
        "nodes": 50,
        "edges": 100,
        "filename": "test_netlist_large.txt",
        "title": "Test Graph - Large Scale"
    }
]

def run_visualization_test():
    """
    执行完整的生成->解析->组合可视化测试流程。
    """
    print("--- 开始执行图可视化集成测试 ---")

    input_netlists_dir = os.path.join(project_root, 'data', 'generated_netlists')

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 8))
    fig.suptitle('Integration Test for Graph Visualization', fontsize=16)

    for i, config in enumerate(NETLIST_CONFIGS):
        print(f"\n[测试 {i+1}/{len(NETLIST_CONFIGS)}]: 正在处理 {config['title']}...")
        ax = axes[i]

        print(f"  -> 步骤 1: 生成网表 '{config['filename']}'...")
        try:
            generate_guaranteed_connected_graph(
                num_nodes=config["nodes"],
                num_edges=config["edges"],
                filename=config["filename"],
                output_dir=input_netlists_dir,
                seed=42
            )
        except Exception as e:
            print(f"    生成网表时出错: {e}")
            continue

        netlist_path = os.path.join(input_netlists_dir, config['filename'])
        print(f"  -> 步骤 2: 解析图文件 '{netlist_path}'...")
        graph = parse_netlist_to_graph(netlist_path)

        if graph is None:
            print("    解析失败，跳过可视化。")
            continue

        print(f"  -> 步骤 3: 在子图上绘制可视化图...")
        draw_graph_on_ax(graph, ax, title=config["title"])

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    output_image_dir = os.path.join(project_root, 'results', 'images')
    os.makedirs(output_image_dir, exist_ok=True)
    
    output_image_path = os.path.join(output_image_dir, 'test_visualization_output.png')
    plt.savefig(output_image_path)
    print(f"\n[成功] 测试可视化结果已保存到: {output_image_path}")
    
    plt.show()

    print("\n--- 图可视化集成测试完成 ---")

if __name__ == '__main__':
    run_visualization_test()