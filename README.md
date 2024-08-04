
# English Learning Article Generator

## 项目描述

本项目是一个用于生成英文阅读文章的工具，基于用户已经学习过的词汇和句子。通过调用LLaMA 3.1模型，生成与用户学习内容相匹配的文章，帮助用户提高英语阅读理解能力。项目使用 [Cuixueshe Earthworm](https://github.com/cuixueshe/earthworm) 项目的课程学习数据生成文章。

## 系统要求

- 操作系统：Linux, macOS, Windows
- Python版本：3.10及以上
- [Ollama](https://ollama.com/)：用于支持LLaMA 3.1模型的运行

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-username/english-learning-article-generator.git
cd english-learning-article-generator
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # 对于Windows用户使用 `venv\Scripts\activate`
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装Ollama和LLaMA 3.1模型

请参考以下指南进行安装：

- [Ollama安装指南](https://ollama.com/)
- [LLaMA 3.1模型安装指南](https://ollama.com/library/llama3.1)

## 运行项目

### 1. 获取课程数据

确保API接口已经正确配置，并且可以访问课程列表和详细信息。

### 2. 运行主程序

```bash
python main.py
```

根据提示选择生成文章的选项并输入相应的课程编号。

## 使用说明

- **生成单独某一课的内容**：选择选项1，输入课程编号即可生成该课的文章。
- **生成某一课及其以前的内容**：选择选项2，输入已学到的课程编号即可生成包含之前所有课程的文章。
- **生成每一课的内容并保存到对应的文件**：选择选项3，程序将自动生成每一课的内容并保存到独立的Markdown文件中。

## 示例文章

生成的课程文章将会保存在项目目录下的 `generated_articles` 文件夹中。每篇文章都会按照课程编号命名，例如 `lesson_1.md`、`lesson_2.md` 等等。

您可以在该文件夹中找到所有生成的课程文章示例，并查看生成的Markdown格式文件。

## 贡献指南

欢迎贡献！请阅读以下指南以了解如何贡献代码：

1. Fork 本仓库
2. 创建一个新的分支 (`git checkout -b feature/your-feature`)
3. 提交您的修改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建一个新的Pull Request

## 许可

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 免责声明

本项目涉及到第三方接口的调用，所有使用的数据和接口均来自于 [Cuixueshe Earthworm](https://github.com/cuixueshe/earthworm) 项目。使用本项目生成的内容仅供学习和参考，请勿用于商业用途。对于因使用本项目而导致的任何损失或问题，项目作者不承担任何责任。
