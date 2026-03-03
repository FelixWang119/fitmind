# API 一致性检查清单

**创建日期**: 2026-03-01
**触发原因**: Habits complete API 路径不一致错误

---

## 🔴 已发现的问题

### 1. Habits API - 已完成打卡

| 项目 | 前端 | 后端 | 状态 |
|------|------|------|------|
| 路径 | `/habits/{id}/completions` | `/habits/{id}/complete` | ❌ 不一致 |
| 修复 | ✅ 已改为 `/complete` | - | ✅ 已修复 |

---

## 📋 检查清单（待完成）

### Auth API
- [ ] POST /register
- [ ] POST /login
- [ ] GET /me
- [ ] PUT /me
- [ ] POST /logout
- [ ] POST /refresh
- [ ] POST /forgot-password
- [ ] POST /reset-password

### Users API
- [ ] GET /profile
- [ ] PUT /profile
- [ ] POST /profile/sync-to-memory
- [ ] GET /{user_id}

### Habits API
- [x] GET / (习惯列表)
- [x] POST / (创建习惯)
- [x] GET /daily-checklist
- [x] POST /{id}/complete (打卡)
- [ ] GET /{id}/completions (获取完成记录) ← **需要检查**
- [ ] PUT /{id}
- [ ] DELETE /{id}
- [ ] GET /{id}/streak-info
- [ ] GET /statistics
- [ ] GET /templates

### Diet API
- [ ] 待检查

### Exercise API
- [ ] 待检查

### Weight API
- [ ] 待检查

### Goals API
- [ ] 待检查

### Gamification API
- [ ] 待检查

---

## 🎯 改进措施

### 立即执行
1. 创建 API 文档（OpenAPI/Swagger）
2. 前端使用代码生成 API client
3. 添加 API 集成测试

### 流程改进
1. API 变更必须同步更新前后端
2. 代码审查必须检查 API 路径
3. 添加 API 路径自动化检查脚本

---

**状态**: 进行中
**负责人**: 开发团队
