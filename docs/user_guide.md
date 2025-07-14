# EDA电路划分KL算法项目 - 详细用户指南

## 目录
1. [环境配置](#环境配置)
2. [数据准备](#数据准备)
3. [算法运行](#算法运行)
4. [结果分析](#结果分析)
5. [故障排除](#故障排除)

---

## 环境配置

### 系统要求
- Python版本：Python 3+
- 内存要求：至少 4GB RAM
- 存储空间：至少 500MB

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/Vector-GitHub/EDA_Circuit_Partitioning_KL.git
cd EDA_Circuit_Partitioning_KL

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python -c "import networkx, matplotlib, numpy, pandas; print('安装成功！')"
```

### 依赖库说明
- networkx (>=3.0)：图论库
- matplotlib (>=3.5)：数据可视化
- numpy (>=1.20)：数值计算
- pandas (>=1.3)：数据处理

---

## 数据准备

### 网表文件格式

```
# 注释行以 '#' 开头
# 每行代表一条边：<节点A> <节点B> [权重]
N0 N1 1
N1 N2 1
N2 N3 1
```

节点命名规则：`N{数字}`（如N0, N1, N2...）

### 生成测试数据

```bash
python scripts/generate_netlists.py
```

生成的文件（`data/generated_netlists/`）：

| 文件名 | 节点数 | 边数 | 用途 |
|--------|--------|------|------|
| `netlist_small_10n_20e.txt` | 10 | 20 | 小规模测试 |
| `netlist_medium_20n_40e.txt` | 20 | 40 | 中等规模测试 |
| `netlist_large_50n_100e.txt` | 50 | 100 | 大规模测试 |

生成特点：
- 保证连通性：所有节点相互可达
- 随机性：固定种子确保可重复性
- 无自环和重边

### 自定义网表创建

```python
import networkx as nx

# 创建图
G = nx.Graph()
G.add_edges_from([('N0', 'N1'), ('N1', 'N2'), ('N2', 'N3')])

# 保存为网表格式
with open('my_netlist.txt', 'w') as f:
    for u, v in G.edges():
        f.write(f"{u} {v} 1\n")
```

---

## 算法运行

### 单一算法可视化

#### 1. 经典KL算法
```bash
python scripts/create_combined_view.py --algorithm kl_random
```

#### 2. 改进版KL算法
```bash
python scripts/create_combined_view.py --algorithm kl_bfs
```

#### 3. 简单贪心算法
```bash
python scripts/create_combined_view.py --algorithm greedy
```


输出：
- 生成3x3对比图：原始图 → 初始划分 → 最终划分
- 三种规模：小、中、大规模网表
- 保存到 `results/images/` 目录

### 完整实验运行

```bash
python scripts/run_experiments.py
```

实验配置：
- 每种算法运行20次
- 三种网表规模
- 固定随机种子确保可重复性

输出文件：

性能数据CSV文件（`results/generate_data/`）：
- `baseline_performance.csv`：贪心算法性能
- `kl_classic_performance.csv`：经典KL算法性能
- `kl_improvements_performance.csv`：改进版KL算法性能

可视化结果（`results/images/`）：
- `experiments_results.png`：四合一性能对比图

> **注意：** 由于个人电脑配置与软件兼容性不同，`matplotlib` 实时弹出的图片可能存在一定的显示问题（如窗口过大、显示不全等）。**请进行代码检查或查看最终结果时，以存储在 `results/images/` 目录下的 `png` 格式图片为准！**

> **补充说明：** `create_combined_view.py` 生成的3x3布局对比图中，中间列（Initial Partition）和最右列（Final Partition）的视图为了实现有序且清晰的分区观感，采用了特殊的 `bipartite` 布局，使节点在分区内纵向对齐。这种布局可能导致分区内部的边在视觉上发生重合，因此看起来边的数量似乎减少了。**这不是一个错误**，设计的重点在于清晰地展示跨越分区的**割边（Cut Edges）**。如果需要验证原始网表的完整结构，**请参考最左列的"Original Graph"视图**，该视图使用 `spring` 布局，完整地展示了所有节点和边。

### 步骤 4: 运行完整实验与分析

如果您想一次性运行所有算法（贪心、经典KL、改进KL）并生成性能对比报告和图表，请执行以下命令：

```bash
python scripts/run_experiments.py
```

---

## 结果分析

### 可视化结果解读

#### 3x3对比图说明
```
[原始图] [初始划分] [最终划分]
[原始图] [初始划分] [最终划分]  ← 中等规模
[原始图] [初始划分] [最终划分]  ← 大规模
```

颜色编码：
- 蓝色节点：分区A
- 红色节点：分区B
- 灰色实线：内部边（同一分区内）
- 红色虚线：割边（跨分区）

### 性能指标说明

| 指标 | 说明 | 单位 |
|------|------|------|
| 最大割边减少率 | 20次运行中的最佳结果 | 百分比 |
| 平均割边减少率 | 20次运行的平均值 | 百分比 |
| 平均算法运行时间 | 20次运行的平均时间 | 秒 |
| 结果稳定性 | 最终割边数的标准差 | 无单位 |

### CSV文件格式示例

```csv
,Small (10n, 20e),Medium (20n, 40e),Large (50n, 100e)
Max Cut-edge Reduction Rate,25.00%,30.50%,28.75%
Average Cut-edge Reduction Rate,22.15%,27.80%,25.90%
Average Algorithm Runtime (s),0.001234,0.005678,0.023456
Result Stability (Std Dev),0.1234,0.2345,0.3456
```

### 性能对比分析

割边减少率：越高越好，表示算法优化效果
运行时间：越小越好，表示算法效率
结果稳定性：标准差越小越稳定

---

## 故障排除

### 常见问题及解决方案

#### 1. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 方法1：使用requirements.txt安装（推荐）
pip install -r requirements.txt

# 方法2：指定版本安装（如果方法1失败）
pip install networkx==3.3 matplotlib==3.9.0 numpy==1.26.4 pandas==1.5.3

# 方法3：逐个安装（如果仍有问题）
pip install networkx>=3.0,<4.0
pip install matplotlib>=3.5,<4.0
pip install numpy>=1.20,<2.0
pip install pandas>=1.3,<2.0

# 方法4：使用conda安装（如果使用Anaconda环境）
conda install networkx matplotlib numpy pandas
```

#### 2. 网表文件不存在
```bash
# 先生成测试数据
python scripts/generate_netlists.py
```

#### 3. 可视化显示问题
```python
# 设置matplotlib后端
import matplotlib
matplotlib.use('Agg')  # 无界面模式
```

#### 4. 算法收敛问题
```python
# 检查网表连通性
import networkx as nx
from src.utils.netlist_parser import parse_netlist_to_graph
G = parse_netlist_to_graph('data/generated_netlists/netlist_small_10n_20e.txt')
print('连通性:', nx.is_connected(G))
```

### 调试技巧

#### 1. 启用详细输出
```python
from src.core.kl_classic import kernighan_lin_partition
result = kernighan_lin_partition(graph, initial_partition, verbose=True)
```

#### 2. 检查中间结果
```python
partition_A, partition_B, cut_size, history, time, _, _ = result
for record in history:
    print(f"Iteration {record['iteration']}: Cut size = {record['cut_size']}")
```

#### 3. 验证图结构
```python
print(f"节点数: {G.number_of_nodes()}")
print(f"边数: {G.number_of_edges()}")
print(f"连通性: {nx.is_connected(G)}")
print(f"独立节点: {list(nx.isolates(G))}")
```

---

## 高级用法

### 自定义算法参数

#### 修改最大迭代次数
```python
from src.core.kl_classic import kernighan_lin_partition
result = kernighan_lin_partition(graph, initial_partition, max_passes=20)
```

#### 自定义初始划分
```python
nodes = list(graph.nodes())
initial_A = set(nodes[:len(nodes)//2])
initial_B = set(nodes[len(nodes)//2:])
initial_partition = (initial_A, initial_B)
```

#### 批量实验配置
```python
# 修改 run_experiments.py 中的参数
NUM_RUNS = 50  # 增加运行次数
```

### 扩展功能开发

#### 添加新的初始划分策略
```python
def _create_dfs_initial_partition(G, start_node=None):
    """使用深度优先搜索创建初始划分"""
    # 实现DFS逻辑
    pass
```

#### 实现多路划分
```python
def kernighan_lin_k_way_partition(G, k=4):
    """K路划分算法"""
    # 实现K路划分逻辑
    pass
```

#### 添加新的性能指标
```python
def calculate_balance_ratio(partition_A, partition_B):
    """计算分区平衡度"""
    return min(len(partition_A), len(partition_B)) / max(len(partition_A), len(partition_B))
```

---

## 联系与支持

### 项目维护者
- 苏依然 - 22362067 - suyr7@mail2.sysu.edu.cn
- 金凤琳 - 22362034 - jinflin@mail2.sysu.edu.cn

### 获取帮助
1. 查看本文档的故障排除部分
2. 检查项目README.md文件
3. 查看源代码中的注释和文档字符串
4. 联系项目维护者

---

*最后更新：2025年6月23*