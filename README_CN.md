# FSTS: 基于大语言模型的多场景多智能体模拟框架

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**语言**: [English](README.md) | [中文](README_CN.md)

## 📖 简介

FSTS 是一个自动化框架，旨在使用大语言模型 (LLMs) 设计、执行和分析复杂的多智能体模拟场景。由于具有高适应性的流水线生成能力，FSTS 支持广泛的场景——从模拟古巴导弹危机和国际关系，到分析智慧城市外卖生态系统和数字政务人员的工作效率。

FSTS 能够动态构建智能体，分配复杂的行为特征和策略参数，执行多组实验，并自主评估结果以生成深刻的因果和行为分析。

## 📊 FSTS 概览

![FSTS Overview](docs/framework.png)

## 🎯 核心特性

- **自动剧本生成**：将自然语言需求转化为结构完整的的多智能体实验场景。
- **动态角色建模**：能够针对性地实例化智能体（例如，A国、B国、外卖员、市民、商户），并赋予其独特的变量、目标和行为逻辑。
- **专门的多智能体角色**：
  - **生成器智能体 (AD, ED, RA, SS)**：负责起草行动方案、解析环境变化、对响应进行建模以及推进场景模拟。
  - **观察者智能体 (AD, ED, RA, VarObserver)**：监控状态转换、评估相互关系，并追踪定制化的响应变量（如全球紧张指数）。
- **灵活的事件与观察流水线**：内置的 `pipeline.py` 将剧本生成、剧本定稿和智能体实例化无缝集成。
- **模型无关性**：支持与领先的大语言模型（如 GPT-4o, GPT-5-mini, DeepSeek-R1）及自定义模型集成。

## 📁 项目结构

```text
FSTS/
├── models/                   # 核心建模与智能体定义
│   ├── agents/               # 多智能体专门角色
│   │   ├── LLMAgent.py       # 基础 LLM 智能体包装器
│   │   ├── ExampleActor/     # 生成的参与者角色示例 (例如: CountryAAgent, DeliveryRider)
│   │   ├── Generator/        # 场景和上下文生成器智能体
│   │   │   ├── AD/           # 动作/决策 生成器
│   │   │   ├── ED/           # 环境/事件 生成器
│   │   │   ├── RA/           # 响应/反应 生成器
│   │   │   └── SS/           # 状态/序列 生成器
│   │   └── Observer/         # 模拟状态观察者
│   │       ├── AD/           # 动作/决策 观察者
│   │       ├── ED/           # 环境/变量 观察者
│   │       └── RA/           # 响应/反应 观察者
├── tools/                    # 实用工具脚本和流水线
│   ├── api_utils.py          # API 交互和 LLM 绑定
│   ├── logger.py             # 标签化日志系统
│   ├── markdown_saver.py     # 模拟结果输出渲染
│   └── pipeline.py           # 核心执行逻辑和生成流水线
├── docs/                     # 文档和资源
│   └── framework.png         # 系统架构图
├── config.py                 # 系统配置
└── main.py                   # 主执行入口点
```

## 🏗️ 系统架构

FSTS 依赖于几个结构组件之间的协同交互：

### 生成器 (Generators)
- **职责**：动态设计变量、环境条件和智能体剧本。
- **功能**：生成实验条件，建立历史准确性（例如古巴导弹危机），并注入参数化的调整。

### 观察者 (Observers)
- **职责**：追踪如“全球紧张指数”、智能体效率和里程碑转换等指标。
- **功能**：读取场景状态，评估变量变化，记录交互历史，并计算动态相似性。

### 评估与流水线 (Evaluation & Pipeline)
- **职责**：指导生成剧本的编排和评估。
- **功能**：解析需求，生成相应逻辑 (`actor_generate`, `script_generate`)，运行逐步循环，并生成 Markdown 报告。

## 🚀 快速开始

### 环境依赖

- Python 3.10+
- 访问受支持的 LLM API (OpenAI 或通过 Ollama/vLLM 本地部署的 DeepSeek-R1)
- 标准科学计算库

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd FSTS

# 安装依赖
pip install -r requirements.txt
```

### 配置

修改 `config.py` 来设置你的 LLM 端点和 API 密钥。打开 `main.py` 并调整 `MODEL_LIST` / `REQUIREMENT_LIST` 来选择你激活的模型（如 `gpt-4o`）和提示需求。

### 运行

执行主模拟流水线：

```bash
python main.py
```

## 📊 工作流

FSTS 的标准执行步骤：

1. **需求解析**：理解自然语言请求（如“分析数字政务人员的效率”或“在极端敌对的情况下模拟古巴导弹危机”）。
2. **流水线初始化**：`script_generate` 创建蓝图，`actor_generate` 实例化定制的智能体，如 `CountryAAgent`。
3. **多智能体模拟**：智能体在场景时间步中迭代，利用 `CommunicationManager` 进行交互。
4. **观察与日志记录**：观察者智能体持续监控并把特定变量记录到内存中。
5. **输出生成**：利用 `markdown_saver` 提取结果、因果事件和日志并将其文档化。

## 📝 关于
该框架提供了从微观智能体状态控制涌现行为的细粒度控制，支持涵盖数字基础设施建模、历史冲突再现和复杂社会技术系统等广泛的模拟领域。
