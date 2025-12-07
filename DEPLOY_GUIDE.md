🚀 部署指南 (DeepSeek + Twitter 版)

第一步：Notion 设置

创建 Database，包含列：Name, URL, Score, AI Comment, Tags, Date。

获取 NOTION_DATABASE_ID (URL 中 notion.so/ 后面的 ID)。

获取 NOTION_API_KEY (Integration Secret)，并把 Robot Connect 到该 Database。

第二步：环境配置

1. **AI**: 获取 DeepSeek API Key (platform.deepseek.com)。
2. **Twitter**: 获取 Apify API Token (console.apify.com) -> Settings -> Integrations -> API Tokens.

在 GitHub 仓库 Settings -> Secrets -> Actions 中添加：

DEEPSEEK_API_KEY
NOTION_API_KEY
NOTION_DATABASE_ID

### 3. Twitter 配置 (Chrome 扩展模式)

本项目使用 Chrome 扩展配合本地 Python 服务来抓取 Twitter Likes。

1. **安装扩展**:
   - 打开 Chrome 浏览器，进入 `chrome://extensions/`
   - 打开右上角 "Developer mode"
   - 点击 "Load unpacked"，选择项目目录下的 `extension` 文件夹。

2. **启动服务**:
   - 在终端运行: `python server.py`
   - 看到 "🚀 Server running" 即表示服务就绪。

3. **使用方法**:
   - 打开 Twitter (X) 的 Likes 页面 (https://x.com/your_handle/likes)。
   - 点击浏览器右上角的 🤖 图标。
   - 点击 "Sync Visible Likes"。
   - 扩展会自动抓取页面上可见的推文发送给本地服务进行分析和入库。

### 4. 运行 RSS 任务

push 到 GitHub 后，Actions 会每天自动运行。
程序会先抓取 RSS，然后抓取 Twitter Likes。
