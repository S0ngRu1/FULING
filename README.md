# 赋灵 (Fuling) - AI 角色扮演语音聊天系统

> **想深入了解本项目的设计思路、用户分析和技术选型吗？请查阅我们的 [项目设计文档](PROJECT_DOCUMENT.md)。**

**与你最爱的角色进行一场跨越时空的语音对话。**

-----

## 🌟 项目预览



https://github.com/user-attachments/assets/8225b249-8526-476f-a0c2-1a8a4ba3e94e



## ✨ 项目理念

**“赋灵”**，取“赋予灵魂”之意。

我们相信，每一个深入人心的角色，无论是来自历史长河、经典文学还是幻想世界，都拥有其独特的“灵魂”。本项目旨在通过前沿的人工智能技术，打破现实与想象的壁垒，为您所钟爱的角色**赋予**鲜活的生命与**灵性**。

用户不再是被动的读者或观众，而是可以成为主动的对话者，与李白交流优美的唐诗，向福尔摩斯请教推理，和美杜莎女王进行一场宿命的对话，甚至和班级校草谈一场校园恋爱。我们致力于创造一个有温度、有深度、极具沉浸感的智能交互体验。

## 🚀 主要功能

  * **实时语音对话**: 集成浏览器原生语音识别（STT）和高质量的云端语音合成（TTS），实现自然、流畅的语音输入与输出。
  * **情感化语音合成**: 独创的 **LLM 驱动 TTS** 流程，系统会首先让大语言模型分析并返回当前角色的**情绪**，再根据此情绪动态调节语音合成的**语速**，最终生成真正富有情感表现力的声音。
  * **深度角色扮演**: 基于强大的 **LLM** 大语言模型，通过精细的Prompt Engineering确保每个角色都严格遵守其人设、背景和说话风格。
  * **RAG专家记忆系统**: 为特定角色（如福尔摩斯）配备基于向量数据库 (ChromaDB) 的RAG系统，使其能根据外部知识库精准回答专业问题，极大提升了回答的准确性和深度。
  * **长程记忆**: 用户在结束一段对话时，系统会自动调用LLM为本次对话生成摘要并保存。当用户再次与同一角色开启新对话时，这份“记忆摘要”会被注入到角色的认知中，实现真正的跨会话记忆。
  * **用户自定义角色**: 提供了完整的角色创建流程，用户可以上传自定义形象、设定名称、描述和专属音色，打造独一无二的AI伙伴。
  * **语音回放**: AI角色的每一条回复都支持点击回放，方便用户反复聆听。
  * **沉浸式UI**: 采用Vue.js构建的现代化前端界面，拥有全局置顶导航、多栏布局和优雅的悬浮交互动画，提供了专业、流畅的用户体验。


## 🛠️ 技术栈

| 类别       | 技术/服务                                                                              | 描述                                                           |
| :--------- |:-----------------------------------------------------------------------------------| :------------------------------------------------------------- |
| **前端** | **Vue 3** (Composition API), **Vite**, **Vue Router**, **Tailwind CSS**, **Axios** | 构建了一个响应式、组件化、样式精美的单页面应用（SPA）。          |
| **后端** | **Python**, **Flask**                                                              | 提供了轻量、稳定且高性能的API服务。                             |
| **AI - LLM** | **Doubao-Seed 1.6 Flash**                                            | 负责核心的自然语言理解、角色扮演和情绪分析。                     |
| **AI - TTS** | **七牛云 TTS**                                                                       | 提供高质量、多音色的语音合成服务，是实现情感化语音的关键。       |
| **架构** | **前后端分离**, **服务层架构 (Services Layer)**                                              | 前后端职责清晰，后端逻辑被拆分为独立的服务模块，易于维护和扩展。 |
| **错误处理** | **自定义异常**, **装饰器**                                                                 | 构建了统一、健壮的错误处理机制，提升了系统的稳定性。           |



## 📂 项目文件结构

```text
FULING/
├── app.py                  # 后端Flask应用的主入口
├── backend/
│   ├── characters/         # 存放所有角色的JSON配置文件
│   ├── chroma_db/          # ChromaDB向量数据库的存储目录
│   ├── config/             # 存放配置文件 (如TTS情感映射)
│   ├── errors/             # 自定义异常和统一错误处理
│   ├── knowledge_base/     # RAG系统的知识库源文件
│   ├── services/           # 核心业务逻辑层
│   │   ├── chat_service.py     # 处理与LLM的聊天交互
│   │   ├── database_manager.py # 数据库操作(长程记忆)
│   │   ├── rag_service.py      # RAG检索逻辑
│   │   └── tts_service.py      # TTS语音合成逻辑
│   ├── index_knowledge_base.py # (首次运行)索引知识库到向量数据库的脚本
│   └── fuling_memory.db    # SQLite数据库文件
├── frontend/
│   ├── public/             # 存放图片等静态资源
│   ├── src/
│   │   ├── components/     # 可复用的Vue组件 (如历史记录)
│   │   ├── views/          # 页级视图组件 (角色列表页、聊天页)
│   │   ├── router/         # Vue Router配置
│   │   ├── App.vue         # Vue应用的根组件
│   │   └── main.js         # Vue应用的入口
│   ├── package.json        # 前端项目依赖与脚本
│   └── vite.config.js      # Vite构建配置
└── requirements.txt        # 后端Python依赖列表
```

## ⚙️ 本地部署与运行

请确保您的电脑已安装 [Node.js](https://nodejs.org/) (LTS v20+) 和 [Python](https://www.python.org/) (v3.10+)。

#### 1\. 配置后端

```bash
# 创建并激活Python虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 进入后端目录
cd backend
# 索引知识库

# 首次运行会下载模型，需要一些时间
# 创建向量数据库，用于知识型角色的回复RAG增强
python index_knowledge_base.py

# 创建.env文件，并填入您的API密钥
# (请参考 .env.example 文件)
```

#### 2\. 配置前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

#### 3\. 启动项目

  * **启动后端服务器:**

      * 打开一个新终端，进入`FULING`目录并激活虚拟环境。
      * 运行: `python app.py`
      * 后端将运行在 `http://127.0.0.1:5123`

  * **启动前端开发服务器:**

      * 打开另一个终端，进入`frontend`目录。
      * 运行: `npm run dev`
      * 前端将运行在 `http://localhost:5173` 

在浏览器中打开前端地址即可开始使用！

## 📜 API 接口规范

#### `GET /api/characters`

- **功能**: 获取所有可用角色的列表信息。

#### `POST /api/characters`

- **功能**: 创建一个新的角色。
- **Content-Type**: `multipart/form-data`
- **表单字段**: `name`, `description`, `voiceType`, `image` (文件)。

#### `GET /api/voices`

- **功能**: 作为安全代理，从七牛云获取可用音色列表。

#### `POST /api/chat`

- **功能**: 发送用户消息，获取包含文本、语音和对话ID的完整响应。
- **请求体**: `{ "characterId", "message", "history", "conversationId" (可选) }`
- **响应体**: `{ "response", "audioData", "conversationId" }`

#### `GET /api/conversations/<character_id>`

- **功能**: 获取与特定角色的所有历史对话摘要列表。

#### `POST /api/conversations/<conversation_id>/summarize`

- **功能**: 结束当前对话，并为其生成、保存摘要。
- **请求体**: `{ "history": [...] }`

#### `DELETE /api/conversations/<conversation_id>`

- **功能**: 删除指定的历史对话记录。
