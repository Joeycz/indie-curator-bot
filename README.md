# Indie Curator Bot 🤖

一个基于 AI 驱动的独立开发产品选品机器人。它自动监控 RSS 信息流，使用大语言模型（LLM）分析内容，筛选出高质量的独立开发产品，并将其保存到 Notion 数据库中。

## ✨ 功能特点

- **多源监控**: 支持 RSS/Atom 订阅源（如 Hacker News, Product Hunt, Reddit, V2EX 等）。
- **AI 智能分析**: 使用 LLM (DeepSeek / Volcano Ark / Moonshot) 对内容进行深入评分和评价。
- **自动去重**: 避免重复保存相同链接。
- **Notion 集成**: 自动将高分内容保存到指定的 Notion Database，包含标签、评分和中文点评。
- **自动化部署**: 支持 GitHub Actions 定时运行。

## 🛠 前置要求

- Python 3.8+
- Notion Integration Token & Database ID
- 下列任意一个 AI 服务的 API Key:
    - DeepSeek
    - Volcano Ark (豆包)
    - Moonshot (Kimi)

## 🚀 安装指南

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/indie-curator-bot.git
   cd indie-curator-bot
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate   # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ 配置说明

### 1. 环境变量 (.env)
复制 `.env.example` (如果有) 或直接新建 `.env` 文件，填入以下配置：

```ini
# Notion 配置 (必须)
NOTION_API_KEY=secret_xxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxx

# AI 模型配置 (任选其一)

# 1. DeepSeek (默认推荐)
DEEPSEEK_API_KEY=sk-xxxx

# 2. Volcano Ark (火山引擎)
ARK_API_KEY=xxxx
ARK_MODEL_ID=ep-xxxx # 推理接入点 ID

# 3. Moonshot (Kimi)
MOONSHOT_API_KEY=sk-xxxx

# 强制指定 Provider (可选: deepseek, volc, moonshot)
# 如果不设置，代码会根据 API Key 自动判断
LLM_PROVIDER=auto
```

### 2. 全局配置 (config.json)
用于设置默认的 LLM 提供商和其他全局选项：

```json
{
  "llm_provider": "auto" 
}
```
*支持的值: `auto`, `deepseek`, `volc`, `moonshot`*

### 3. 订阅源 (feeds.json)
在 `feeds.json` 中配置你需要监控的 RSS 地址列表：

```json
[
    "https://hnrss.org/show",
    "https://www.producthunt.com/feed",
    "https://www.v2ex.com/feed/tab/creative.xml"
]
```

## 🏃‍♂️ 运行使用

### 本地运行
确保虚拟环境已激活，然后运行：
```bash
python curator.py
```

或者使用 Provider 环境变量覆盖配置：
```bash
LLM_PROVIDER=moonshot python curator.py
```

### GitHub Actions 部署
本项目包含自动化的 GitHub Actions 工作流。详情请参考 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)。

## 🤝 贡献
欢迎提交 Issue 和 Pull Request！
