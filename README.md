# 基于Kernighan-Lin算法的电路两路划分实现、分析与优化

## 项目概览

本项目旨在实现、优化和分析经典的Kernighan-Lin (KL)电路划分算法。项目不仅包含了对1970年原始KL算法的精确复现，还实现了一个简单的贪心算法作为基线对比，并探索了使用BFS（广度优先搜索）进行初始划分的优化策略。整个项目配备了自动化实验和可视化功能，能够直观地对比不同算法在多个维度上的性能表现。

## 主要功能

### 多种算法实现
- 经典KL算法：严格遵循1970年原始论文，包含轮次内D值更新机制
- 改进版KL算法：使用BFS（广度优先搜索）进行初始划分，减少迭代次数
- 简单贪心算法：作为baseline对照组，实现单步最优贪心策略

### 自动化实验框架
- 提供脚本可对所有算法在不同规模的网表上进行批量测试（每种算法运行20次）
- 自动统计和生成CSV格式的性能报告
- 计算最大/平均割边减少率、运行时间和结果稳定性

### 丰富的可视化
- 提供脚本可生成"原始图-初始划分-最终划分"的3x3对比图
- 划分结果以颜色和布局清晰区隔，割边高亮显示
- 支持多种布局样式（spring、bipartite等）

### 命令行控制
- 支持通过命令行参数自由切换要测试和可视化的算法
- 提供灵活的参数配置选项

### UML图表支持
- 集成PlantUML扩展，支持生成项目架构图和算法流程图
- 提供完整的UML文档，包括类图、活动图等
- 自动化的图表生成和导出功能

## 项目结构

```
EDA_Circuit_Partitioning_KL/
├── .vscode/
│   └── settings.json                 # VS Code工作区设置 (PlantUML输出路径、格式等)
├── data/
│   ├── generated_netlists/           # 存放由脚本生成的标准网表文件
│   │   ├── netlist_large_50n_100e.txt
│   │   ├── netlist_medium_20n_40e.txt
│   │   └── netlist_small_10n_20e.txt
│   └── raw/                          # 存放外部提供的或特殊设计的原始网表
├── docs/
│   ├── uml/                          # 存放UML图的源文件
│   │   ├── flow_greedy.puml          # 流程图: 贪心算法
│   │   ├── flow_kl_classic.puml      # 流程图: 经典KL算法
│   │   ├── flow_kl_improvements.puml # 流程图: 改进KL算法
│   │   └── project_architecture.puml # 项目整体架构图
│   ├── plantuml_guide.md             # PlantUML使用指南
│   ├── project_report.pdf            # 项目报告
│   └── user_guide.md                 # 详细的用户使用指南
├── results/
│   ├── generate_data/                # 存放实验生成的原始性能数据
│   │   ├── baseline_performance.csv
│   │   ├── kl_classic_performance.csv
│   │   └── kl_improvements_performance.csv
│   └── images/                       # 存放所有可视化结果图片 (含UML图)
│       ├── Classic KL Algorithm Flow.svg
│       ├── EDA Circuit Partitioning Project Architecture.svg
│       ├── experiments_results.png
│       ├── full_results_classic_kl_(random_init).png
│       ├── full_results_kl_with_bfs_init.png
│       ├── full_results_simple_greedy.png
│       ├── Improved KL Algorithm Flow.svg
│       └── Simple Greedy Algorithm Flow.svg
├── scripts/
│   ├── create_combined_view.py       # 生成3x3算法流程对比图的脚本
│   ├── generate_netlists.py          # 生成标准测试网表的脚本
│   └── run_experiments.py            # 运行完整实验并生成性能报告的脚本
├── src/
│   ├── core/                         # 核心算法实现
│   │   ├── base_partitioning.py      # 基线算法: 简单贪心
│   │   ├── kl_classic.py             # 经典KL算法 (复现论文)
│   │   ├── kl_improvements.py        # 改进KL算法 (BFS初始划分)
│   │   └── kl_original.py            # (已废弃) 最初的错误实现版本
│   └── utils/                        # 辅助工具模块
│       ├── graph_visualizer.py       # 图可视化功能
│       └── netlist_parser.py         # 网表文件解析器
├── tests/
│   ├── test_graph_visualizer.py
│   └── test_parser.py
├── .gitignore                        # Git忽略文件配置
├── README.md                         # 项目概览与快速上手指南
└── requirements.txt                  # Python依赖库列表
```

## 快速上手（详细版本见user_guide.md)

### 环境设置

Python版本要求：Python 3

安装依赖项：
```bash
pip install -r requirements.txt
```

#### PlantUML扩展安装(生成项目报告所需的架构图以及流程图，与实验本身无关）

**方法一：Chocolatey快速安装（推荐）**

1. 安装Chocolatey包管理器：
   - 以管理员身份打开PowerShell
   - 运行：`Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`

2. 安装PlantUML：
   - 运行：`choco install plantuml`
   - 自动安装PlantUML.jar、GraphViz和Java环境

3. 配置说明：
   - 使用本地渲染器
   - 配置文件：`.vscode/settings.json`

**方法二：在线服务器（备选方案）**

1. 安装VS Code扩展：
   - 扩展已自动安装：`jebbs.plantuml` v2.18.1

2. 安装Java环境（必需）：
   - 下载并安装 [Oracle Java](https://www.oracle.com/java/technologies/downloads/) 或 [OpenJDK](https://adoptium.net/)
   - 确保Java在系统PATH中

3. 配置说明：
   - 使用在线服务器渲染
   - 配置文件：`.vscode/settings_online.json`（复制为 `settings.json`）

4. 使用UML图表：
   - 预览：打开 `.puml` 文件，按 `Alt+Shift+D`
   - 导出：`Ctrl+Shift+P` → "PlantUML: Export Current Diagram"
   - 详细指南：查看 `docs/plantuml_guide.md`

### 生成测试数据

运行网表数据生成脚本：
```bash
python scripts/generate_netlists.py
```

这将生成三个不同规模的测试网表文件：
- `netlist_small_10n_20e.txt` (10节点，20边)
- `netlist_medium_20n_40e.txt` (20节点，40边)
- `netlist_large_50n_100e.txt` (50节点，100边)

### 运行单一算法可视化

生成一个最简单的运行示例：
```bash
# 运行经典KL算法可视化
python scripts/create_combined_view.py --algorithm kl_random

# 运行改进版KL算法可视化
python scripts/create_combined_view.py --algorithm kl_bfs

# 运行贪心算法可视化
python scripts/create_combined_view.py --algorithm greedy
```

> **注意：** 由于个人电脑配置与软件兼容性不同，`matplotlib` 实时弹出的图片可能存在一定的显示问题（如窗口过大、显示不全等）。**请进行代码检查或查看最终结果时，以存储在 `results/images/` 目录下的 `png` 格式图片为准！**

### 运行完整实验

运行自动化实验脚本：
```bash
python scripts/run_experiments.py
```

这将：
- 对三种算法在三种规模的网表上各运行20次
- 生成性能对比CSV文件到 `results/generate_data/` 目录
- 创建四合一性能对比图到 `results/images/` 目录

## 算法说明

### 预设方案KL算法 (kl_original.py)
- 按照已经上交原始开题报告写的算法
- 测试时发现逻辑有严重谬误；遂放弃使用但仍保留文件

### 经典KL算法 (kl_classic.py)
- 严格遵循1970年Kernighan-Lin原始论文
- 在每轮迭代中，单轮内每次锁定后更新D值计算
- 使用高效的D值更新算法
- 包含迭代优化和收敛判断

### 改进版KL算法 (kl_improvements.py)
- 基于经典KL算法，使用BFS进行初始划分
- 通过高质量的初始划分减少后续迭代次数
- 可能获得更好的最终结果

### 简单贪心算法 (base_partitioning.py)
- 作为性能基线算法
- 在每一步都寻找并执行能带来最大即时收益的单次节点对交换
- 用于对比KL算法的优化效果

## 输出结果

### 性能数据文件
- `baseline_performance.csv`：贪心算法性能指标
- `kl_classic_performance.csv`：经典KL算法性能指标
- `kl_improvements_performance.csv`：改进版KL算法性能指标

### 可视化图像
- `full_results_simple_greedy.png`：贪心算法3x3对比图
- `full_results_classic_kl_(random_init).png`：经典KL算法3x3对比图
- `full_results_kl_with_bfs_init.png`：改进版KL算法3x3对比图
- `experiments_results.png`：四合一性能对比图

### UML图表
- `project_architecture.puml`：项目架构类图
- `kl_algorithm_flow.puml`：KL算法流程图
- 详细使用指南：`docs/plantuml_guide.md`

## 项目成员

- 苏依然 - 22362067
- 金凤琳 - 22362034
