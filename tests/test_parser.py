"""
tests/test_parser.py - 对网表解析器 netlist_parser.py 的单元测试
该文件包含了针对网表解析功能的多个测试用例，以确保其能够正确、
稳定地处理各种情况。
"""

import unittest
import os
import sys
import networkx as nx
import tempfile
import shutil

# --- 路径设置 ---
# 让测试脚本能够找到 src 目录下的模块，将项目根目录添加到 sys.path
# 当前文件路径: EDA_Circuit_Partitioning_KL/tests/test_parser.py
# 项目根目录: EDA_Circuit_Partitioning_KL/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 从 src.utils 包中导入被测试的函数
from src.utils.netlist_parser import parse_netlist_to_graph

class TestNetlistParser(unittest.TestCase):
    """测试 netlist_parser.py 中的核心功能"""

    def setUp(self):
        """在每个测试用例运行前执行"""
        # 创建一个临时目录来存放测试用的网表文件
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """在每个测试用例运行后执行"""
        # 删除临时目录及其所有内容
        shutil.rmtree(self.test_dir)

    def test_successful_parsing(self):
        """测试能否成功解析一个格式正确的标准文件"""
        file_path = os.path.join(self.test_dir, "valid_netlist.txt")
        content = (
            "# 这是一个标准的测试文件\n"
            "\n"
            "N0 N1 1\n"
            "N1 N2 2\n"
            "N0 N2 1\n"
            "N3 N4\n"  # 测试无权重的情况，应默认为1
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        graph = parse_netlist_to_graph(file_path)

        # 断言返回的是一个图对象
        self.assertIsInstance(graph, nx.Graph)
        # 验证节点和边的数量
        self.assertEqual(graph.number_of_nodes(), 5)
        self.assertEqual(graph.number_of_edges(), 4)
        # 验证边的权重
        self.assertEqual(graph.edges['N1', 'N2']['weight'], 2)
        self.assertEqual(graph.edges['N3', 'N4']['weight'], 1) # 默认权重

    def test_file_not_found(self):
        """测试当文件不存在时，函数是否返回 None"""
        file_path = os.path.join(self.test_dir, "non_existent_file.txt")
        graph = parse_netlist_to_graph(file_path)
        # 断言返回值是 None
        self.assertIsNone(graph)

    def test_malformed_file(self):
        """测试能否正确处理包含格式错误行的文件"""
        file_path = os.path.join(self.test_dir, "malformed_netlist.txt")
        content = (
            "N0 N1 1\n"
            "This is a malformed line\n"  # 格式错误的行
            "N2 N3 1\n"
            "N4\n"  # 缺少节点的行
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        graph = parse_netlist_to_graph(file_path)
        
        # 应该成功创建图，但只包含有效的边
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(graph.number_of_nodes(), 4) # N0, N1, N2, N3
        self.assertEqual(graph.number_of_edges(), 2) # (N0,N1) 和 (N2,N3)

    def test_empty_or_comment_only_file(self):
        """测试解析空文件或只包含注释的文件"""
        # 1. 测试空文件
        empty_file_path = os.path.join(self.test_dir, "empty.txt")
        open(empty_file_path, 'w').close()
        
        graph = parse_netlist_to_graph(empty_file_path)
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(graph.number_of_nodes(), 0)
        self.assertEqual(graph.number_of_edges(), 0)

        # 2. 测试只包含注释和空行的文件
        comment_file_path = os.path.join(self.test_dir, "comments.txt")
        content = (
            "# 这是一个只有注释的文件\n"
            "\n"
            "# --- End of file ---"
        )
        with open(comment_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        graph = parse_netlist_to_graph(comment_file_path)
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(graph.number_of_nodes(), 0)


# 这使得脚本可以直接从命令行运行
if __name__ == '__main__':
    # unittest.main() 会自动发现并运行这个文件中的所有测试用例
    unittest.main(verbosity=2)