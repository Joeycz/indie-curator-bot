🚀 部署指南 (DeepSeek 版)

第一步：Notion 设置

创建 Database，包含列：Name, URL, Score, AI Comment, Tags, Date。

获取 NOTION_DATABASE_ID (URL 中 notion.so/ 后面的 ID)。

获取 NOTION_API_KEY (Integration Secret)，并把 Robot Connect 到该 Database。

第二步：环境配置

获取 DeepSeek API Key (platform.deepseek.com)。

在 GitHub 仓库 Settings -> Secrets -> Actions 中添加：

DEEPSEEK_API_KEY

NOTION_API_KEY

NOTION_DATABASE_ID

第三步：运行

push 到 GitHub 后，Actions 会每天自动运行。
