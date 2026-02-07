# PDF 转 Word 网页工具

基于 Vue 3 和 Flask 的 PDF 转 Word 在线转换工具。

## 功能特点

- ⚡ 快速转换：基于 pdf2docx 库，转换速度快
- 🔒 安全可靠：文件在本地处理，保护隐私
- 📝 保持格式：保留原文档的格式和布局
- 🎨 现代界面：简洁美观的用户界面
- 🤖 AI 智能助手：集成 GLM-4.7 Flash 模型，提供文档摘要、翻译和问答功能

## 技术栈

### 前端
- Vue 3 (Composition API)
- Vite
- Axios

### 后端
- Flask
- pdf2docx
- Flask-CORS
- zhipuai (GLM-4.7 Flash SDK)
- python-dotenv

## 项目结构

```
pdf-to-word-web/
├── backend/              # Python 后端
│   ├── app.py           # Flask 应用主文件
│   ├── ai_service.py    # AI 服务模块
│   ├── requirements.txt  # Python 依赖
│   ├── .env.example     # 环境变量配置模板
│   ├── uploads/         # 上传文件临时目录
│   └── downloads/      # 转换后文件目录
└── frontend/           # Vue 前端
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue
        ├── main.js
        └── style.css
```

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 1.5. 配置 AI 服务

```bash
cd backend
cp .env.example .env
```

获取 API Key 的方式：
1. 访问 https://open.bigmodel.cn/usercenter/apikeys
2. 注册/登录账号
3. 创建新的 API Key
4. 复制 API Key 到 `.env` 文件中

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

## 运行项目

### 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:5000` 运行

### 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:3000` 运行

## 使用方法

### 基础功能

**方式一：PDF 转 Word**
1. 在浏览器中打开 `http://localhost:3000`
2. 点击上传区域选择 PDF 文件
3. 点击"开始转换"按钮
4. 等待转换完成
5. 点击"下载原 Word 文件"按钮下载转换后的文件

**方式二：PDF 直接转翻译后的 Word（推荐）**
1. 在浏览器中打开 `http://localhost:3000`
2. 点击上传区域选择 PDF 文件
3. 选择目标翻译语言
4. 点击"PDF 转翻译 Word"按钮
5. 等待转换和翻译完成
6. 点击"下载翻译后的 Word 文件"

**方式三：PDF 转 Word 后再翻译**
1. 先按照"方式一"将 PDF 转换为 Word
2. 点击"翻译成[目标语言]"按钮，将 Word 文档翻译成指定语言
3. 翻译完成后，点击"下载翻译后的 Word 文件"

### AI 智能助手功能

1. 在浏览器中打开 `http://localhost:3000`
2. 选择 PDF 文件后，点击"AI 助手"按钮
3. 系统会自动提取 PDF 文本内容
4. 在 AI 面板中选择功能：
   - **文档摘要**：生成文档的智能摘要
   - **翻译**：将文档内容翻译成中文
   - **问答**：基于文档内容进行智能问答
5. 查看并复制 AI 生成的结果

**注意**：AI 功能需要先配置 API Key（见上方配置说明）

## API 接口

### POST /api/convert

上传 PDF 文件并转换为 Word

**请求：**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF 文件)

**响应：**
```json
{
  "success": true,
  "downloadUrl": "/api/download/xxx.docx",
  "filename": "xxx.docx"
}
```

### GET /api/download/<filename>

下载转换后的 Word 文件

**请求：**
- Method: GET
- Parameter: filename (文件名)

### GET /api/health

健康检查接口

**响应：**
```json
{
  "status": "ok"
}
```

### GET /api/ai/status

检查 AI 服务状态和可用功能

**响应：**
```json
{
  "enabled": true,
  "features": {
    "summary": true,
    "translate": true,
    "chat": true
  }
}
```

### POST /api/extract-text

提取 PDF 文件的文本内容

**请求：**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF 文件)

**响应：**
```json
{
  "success": true,
  "text": "PDF 文本的完整内容",
  "char_count": 12345
}
```

### POST /api/ai/summary

生成文档摘要

**请求：**
- Method: POST
- Content-Type: application/json
- Body: 
```json
{
  "text": "文档文本内容"
}
```

**响应：**
```json
{
  "success": true,
  "summary": "这是文档的智能摘要..."
}
```

### POST /api/ai/translate

翻译文档内容

**请求：**
- Method: POST
- Content-Type: application/json
- Body: 
```json
{
  "text": "文档文本内容",
  "target_lang": "中文"
}
```

**响应：**
```json
{
  "success": true,
  "translation": "翻译后的文本内容..."
}
```

### POST /api/ai/chat

基于文档内容进行问答

**请求：**
- Method: POST
- Content-Type: application/json
- Body: 
```json
{
  "question": "用户的问题",
  "context": "文档文本内容"
}
```

**响应：**
```json
{
  "success": true,
  "answer": "基于文档内容的回答..."
}
```

### POST /api/translate-word

将 Word 文档翻译成目标语言

**请求：**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - file: Word 文件
  - target_lang: 目标语言（如"中文"、"英文"等）

**响应：**
```json
{
  "success": true,
  "downloadUrl": "/api/download/xxx_translated.docx",
  "filename": "xxx_translated.docx"
}
```

### POST /api/translate-pdf

直接将 PDF 文件转换并翻译成目标语言的 Word 文档（一步到位）

**请求：**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - file: PDF 文件
  - target_lang: 目标语言（如"中文"、"英文"等）

**响应：**
```json
{
  "success": true,
  "downloadUrl": "/api/download/xxx_translated.docx",
  "filename": "xxx_translated.docx"
}
```

## 配置说明

### 后端配置

在 `backend/app.py` 中可以修改以下配置：

```python
app.config['UPLOAD_FOLDER'] = 'uploads'      # 上传文件目录
app.config['DOWNLOAD_FOLDER'] = 'downloads'   # 下载文件目录
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大文件大小 (16MB)
```

### 前端配置

在 `frontend/vite.config.js` 中可以修改以下配置：

```javascript
server: {
  port: 3000,  # 前端端口
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // 后端地址
      changeOrigin: true
    }
  }
}
```

## 注意事项

- 最大支持 16MB 的 PDF 文件
- 仅支持 PDF 格式的文件
- 转换后的文件会自动清理，建议及时下载
- 需要确保 Python 和 Node.js 环境已正确安装

## 依赖版本

- Python >= 3.8
- Node.js >= 18.0
- pdf2docx == 0.5.6
- Vue == 3.4.0
- Flask == 3.0.0

## 许可证

MIT License
