# Issue Tracker - Jira 风格 AI 友善的 Issue 追踪系统

## 产品定位

- **UI 风格**：Jira 风格，左侧项目导航、顶部筛选搜索、中央 issue 列表、右侧详情面板
- **数据架构**：File-first 设计，issue 主数据存储在 JSON + Markdown 文件中
- **数据库角色**：仅存储账号、角色权限、通知、审计日志等协作状态

## 核心功能

### Phase 1 - 核心骨架
- [x] 项目与子项目管理
- [x] Issue CRUD 操作
- [x] 状态流转 (new → triaged → assigned → in_progress → resolved → closed)
- [x] 指派与认领机制
- [x] Jira 风格列表 UI
- [x] Issue 详情 Drawer

### Phase 2 - 历史与附件
- [ ] Comments append-only 机制
- [ ] Events append-only 机制
- [ ] Activity Timeline UI
- [ ] 附件上传与管理
- [ ] Audit 日志

### Phase 3 - Email 与搜索
- [ ] Email 绑定到 Issue
- [ ] 从 Email 创建 Issue
- [ ] 全文搜索
- [ ] 高级筛选

### Phase 4 - AI 功能
- [ ] Embedding pipeline
- [ ] 语义搜索
- [ ] 相似 Issue 检测
- [ ] 自动摘要

## 技术栈

- **后端**：Python FastAPI + SQLAlchemy
- **前端**：React + TypeScript + TailwindCSS
- **数据库**：SQLite (开发) / PostgreSQL (生产)
- **文件存储**：本地文件系统 + JSON/Markdown
- **容器化**：Docker + Docker Compose

## 快速启动

```bash
# 使用 Docker 启动
docker-compose up -d

# 访问
http://localhost:3000
```

## 数据目录

- `data/issues/` - Issue 主数据和元数据
- `data/attachments/` - 附件存储
- `backend/app/data/` - SQLite 数据库

## API 端点

- `POST /api/projects` - 创建项目
- `GET /api/projects` - 获取项目列表
- `POST /api/issues` - 创建 Issue
- `GET /api/issues` - 获取 Issue 列表
- `GET /api/issues/:key` - 获取 Issue 详情
- `PUT /api/issues/:key` - 更新 Issue
- `POST /api/issues/:key/comments` - 添加评论
- `POST /api/issues/:key/attachments` - 上传附件
