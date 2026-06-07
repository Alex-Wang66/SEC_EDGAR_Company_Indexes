# SEC EDGAR 公司财报索引数据处理系统

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source: SEC EDGAR](https://img.shields.io/badge/Data-SEC%20EDGAR-green)](https://www.sec.gov/cgi-bin/browse-edgar)

一个完整的数据工程解决方案，用于获取、解析和处理美国SEC EDGAR公司财报索引数据。

[功能](#功能) • [快速开始](#快速开始) • [文档](#文档) • [架构](#架构)

</div>

---

## 项目概述

本项目提供一个**生产级数据管道**，用于从[SEC官方数据库](https://www.sec.gov/Archives/edgar/full-index/)采集和处理SEC EDGAR公司财报索引数据。

**项目功能：**
- 📥 自动从SEC下载季度公司财报索引
- 🔍 解析SEC索引文件中的结构化数据（制表符分隔格式）
- 🧹 清洗、去重、处理数据
- 💾 导出多种格式（Parquet、CSV、JSON）
- 📊 生成综合统计信息和元数据

**核心特性：**
- **真实数据**：使用正式的SEC EDGAR数据
- **高可扩展性**：处理10,000+条公司记录
- **模块化设计**：下载、解析、处理逻辑清晰分离
- **可配置**：基于环境变量和配置文件
- **可续传**：支持跳过下载直接处理现有文件
- **文档完善**：代码和使用文档齐全

---

## 功能特性

### ✨ 核心功能

| 功能 | 描述 |
|------|------|
| **自动下载** | 从SEC服务器获取company.idx文件，支持速率限制 |
| **格式解析** | 处理SEC特有的可变宽度索引文件格式 |
| **数据清洗** | 删除重复项、处理缺失值、规范化空白字符 |
| **去重处理** | 按文件日期保留每家公司的最新财报 |
| **多格式导出** | 支持Parquet（高效）、CSV（通用）、JSON格式 |
| **日志监控** | 结构化日志提供管道执行的完整透视 |
| **命令行工具** | 提供命令行接口用于批处理 |

### 📈 数据处理流程

```
SEC EDGAR 官方网站
       ↓
   下载 (按季度下载company.idx文件)
       ↓
   解析 (从索引格式提取结构化数据)
       ↓
   清洗 (处理空白、空行、日期转换)
       ↓
   去重 (每家公司保留最新财报)
       ↓
   导出 (Parquet/CSV/JSON格式)
```

---

## 快速开始

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/Alex-Wang66/SEC_EDGAR_Company_Indexes.git
   cd SEC_EDGAR_Company_Indexes
   ```

2. **创建Python虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows系统: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 基本用法

#### 命令行使用

```bash
# 下载2023-2024年数据并保存为Parquet格式
python run_pipeline.py --start-year 2023 --end-year 2024

# 只处理现有文件（跳过下载），导出为CSV
python run_pipeline.py --skip-download --format csv

# 启用详细日志下载数据
python run_pipeline.py --start-year 2023 --verbose
```

#### Python代码调用

```python
from src.sec_edgar.main import SECEDGARPipeline

# 创建并运行管道
pipeline = SECEDGARPipeline()
results = pipeline.run(
    start_year=2023,
    end_year=2024,
    download=True,
    output_format="parquet"
)

print(f"输出文件: {results['output_file']}")
print(f"记录数: {results['stages']['process']['records']:,}")
```

### 输出示例

```
SEC EDGAR 数据管道已启动
============================================================

[阶段 1/3] 下载SEC EDGAR索引文件...
✓ 已下载 8 个文件

[阶段 2/3] 解析公司索引文件...
✓ 已解析 47,233 条记录

[阶段 3/3] 处理和清洗数据...
✓ 已处理 12,456 条最终记录

保存结果为 PARQUET 格式...
✓ 已保存到: data/processed/company_files_20240607_154523.parquet

============================================================
SEC EDGAR 数据管道执行完成

管道摘要:
  输出文件: data/processed/company_files_20240607_154523.parquet
  总记录数: 12,456
  独立公司数: 5,234
  表单类型: 42
```

---

## 项目架构

### 项目结构

```
SEC_EDGAR_Company_Indexes/
├── src/sec_edgar/              # 核心代码包
│   ├── __init__.py             # 包初始化
│   ├── config.py               # 配置管理
│   ├── downloader.py           # SEC EDGAR下载器 (SECDownloader类)
│   ├── parser.py               # 索引文件解析器 (SECIndexParser类)
│   ├── processor.py            # 数据处理器 (DataProcessor类)
│   └── main.py                 # 管道编排器 (SECEDGARPipeline类)
├── data/
│   ├── raw/                    # 下载的.idx文件
│   └── processed/              # 输出文件 (Parquet/CSV/JSON)
├── logs/                       # 管道日志
├── tests/                      # 单元测试
├── run_pipeline.py             # CLI入口点
├── setup.py                    # 包设置
├── requirements.txt            # 依赖清单
├── README.md                   # 本文件
├── USAGE.md                    # 详细使用指南
├── DATA_FORMAT.md              # 数据格式规范
├── CHANGELOG.md                # 版本历史
└── LICENSE                     # MIT许可证
```

### 核心组件

#### 1. **SECDownloader** (`downloader.py`)
从SEC下载季度公司索引文件
- 遵守SEC速率限制指南（请求间隔0.2秒）
- 优雅处理网络错误
- 返回下载统计信息

#### 2. **SECIndexParser** (`parser.py`)
解析SEC固定宽度索引文件格式
- 跳过头部行（前10行）
- 提取：公司名称、表单类型、CIK、日期、文件名
- 处理可变长度公司名称

#### 3. **DataProcessor** (`processor.py`)
清洗和转换原始数据
- 按最新文件日期删除重复项
- 规范化空白字符
- 将日期字符串转换为datetime对象
- 生成统计信息

#### 4. **SECEDGARPipeline** (`main.py`)
编排完整工作流
- 管理日志和错误处理
- 保存多种格式的结果
- 提供进度报告

---

## 使用指南

### 命令行选项

```
用法: run_pipeline.py [-h] [--start-year START_YEAR] 
                      [--end-year END_YEAR] [--skip-download]
                      [--format {parquet,csv,json}] [--verbose]

可选项:
  --start-year START_YEAR    起始年份 (默认: 2023)
  --end-year END_YEAR        截止年份 (默认: 当前年份)
  --skip-download            跳过下载，处理现有文件
  --format {parquet,csv,json}  输出格式 (默认: parquet)
  --verbose                  启用详细日志
```

### 配置

编辑 `src/sec_edgar/config.py` 自定义：
- SEC EDGAR基础URL
- 默认年份范围
- 请求延迟和超时
- 输出目录路径
- 日志设置

详细示例见 [USAGE.md](USAGE.md)。

---

## 数据格式

输出文件包含以下字段：

| 列名 | 类型 | 描述 |
|-----|------|------|
| Company Name | 字符串 | 向SEC报备的官方公司名称 |
| Form Type | 字符串 | SEC表单类型 (如 10-K, 10-Q, 8-K) |
| CIK | 字符串 | 中央索引键 - 公司唯一标识符 |
| Date Filed | 日期时间 | 文件提交日期 |
| Filename | 字符串 | SEC服务器上的文件路径 |

**示例记录：**
```json
{
  "Company Name": "Apple Inc.",
  "Form Type": "10-Q",
  "CIK": "0000320193",
  "Date Filed": "2024-05-03",
  "Filename": "edgar/data/320193/0000320193-24-000066.txt"
}
```

完整规范见 [DATA_FORMAT.md](DATA_FORMAT.md)。

---

## 性能特征

| 指标 | 数值 |
|-----|------|
| **下载速度** | 约2个文件/分钟 (遵守SEC速率限制) |
| **解析速度** | 约10,000条记录/秒 |
| **内存占用** | 50,000条记录约500MB |
| **文件大小** | Parquet(~15MB), CSV(~60MB) - 50,000条记录 |

---

## 开发

### 测试

```bash
# 运行测试
python -m pytest tests/

# 运行并生成覆盖率报告
python -m pytest --cov=src tests/
```

### 代码质量

```bash
# 类型检查
mypy src/

# 代码检查
flake8 src/ --max-line-length=100

# 代码格式化
black src/
```

### 构建包

```bash
# 构建分发文件
python setup.py sdist bdist_wheel

# 本地开发模式安装
pip install -e .
```

---

## API参考

详细的API文档请查看各模块的docstring：

```python
from src.sec_edgar.downloader import SECDownloader
from src.sec_edgar.parser import SECIndexParser
from src.sec_edgar.processor import DataProcessor
```

完整的API文档见 [USAGE.md](USAGE.md#api-reference)。

---

## 法律声明及数据来源

- **数据来源**: [SEC EDGAR数据库](https://www.sec.gov/cgi-bin/browse-edgar)
- **使用协议**: 本工具遵守SEC的robots.txt和速率限制指南
- **速率限制**: 默认请求间隔为0.2秒
- **用户代理**: 清晰标识为教育用途

SEC EDGAR数据库是公开且免费使用的。所有财报都是SEC的官方文件。

---

## 故障排查

### 常见问题

**问题**: 网络超时错误
- **解决**: 在config.py中增加超时时间或检查SEC服务状态

**问题**: 文件已存在
- **解决**: 输出文件带时间戳；之前的文件会被保留

**问题**: 大数据集内存错误
- **解决**: 逐年处理；使用CSV代替一次加载全部

更多解决方案见 [USAGE.md](USAGE.md#troubleshooting)。

---

## 贡献指南

欢迎贡献！请按以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

---

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 引用

如在研究或出版中使用本数据，请引用SEC EDGAR数据源：

```bibtex
@dataset{sec_edgar_2024,
  title={SEC EDGAR Company Indexes},
  author={U.S. Securities and Exchange Commission},
  year={2024},
  url={https://www.sec.gov/Archives/edgar/full-index/}
}
```

---

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md) 了解版本历史和更新。

---

## 联系方式

**作者**: Alex Wang  
**邮箱**: wangjle9@mail2.sysu.edu.cn  
**GitHub**: [@Alex-Wang66](https://github.com/Alex-Wang66)

---

<div align="center">

用 ❤️ 为金融数据爱好者打造

⭐ 如果对你有帮助，请考虑给本仓库点个Star!

</div>
