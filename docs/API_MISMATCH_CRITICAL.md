# 🔴 严重：前后端 API 路径不匹配问题

**发现日期**: 2026-03-01  
**严重程度**: 🔴 严重  
**影响范围**: 67+ 个前端 API 调用，234+ 个后端端点

---

## 🚨 问题根源

### 开发流程缺陷

1. **没有 API 设计规范**
   - 前后端各自定义路径
   - 没有统一的 API 文档
   - 缺少代码审查检查项

2. **没有集成测试**
   - 前端写完后没有测试真实 API
   - 后端改完后没有通知前端
   - 依赖手动测试发现错误

3. **缺乏自动化工具**
   - 没有 OpenAPI/Swagger 规范
   - 没有代码生成
   - 没有自动化比对工具

---

## 📊 当前状态

| 类别 | 数量 | 状态 |
|------|------|------|
| 后端 API 端点 | 234+ | 已实现 |
| 前端 API 调用 | 67+ | 已实现 |
| **路径不匹配** | **大量** | ❌ **严重问题** |
| 已修复 | 1 | ✅ (habits/complete) |

---

## 🔴 发现的不匹配示例

### Auth API
- 前端：`POST /auth/register`
- 后端：`POST /register`

### Users API
- 前端：`GET /users/profile`
- 后端：`GET /profile`

### Habits API
- 前端：`GET /habits/`
- 后端：`GET /`

### Dashboard API
- 前端：`GET /dashboard/overview`
- 后端：`GET /overview`

---

## ✅ 修复计划

### Phase 1: 紧急修复 (本周)
1. 创建 API 路径映射表
2. 修复所有 Auth API
3. 修复所有 Habits API
4. 修复所有 Users API

### Phase 2: 系统规范 (下周)
1. 编写 OpenAPI 规范
2. 前端使用代码生成 API client
3. 添加 API 集成测试
4. 建立 API 变更流程

### Phase 3: 自动化 (Sprint 4)
1. CI/CD 自动检查 API 一致性
2. 自动运行集成测试
3. API 文档自动生成

---

## 📋 立即行动项

- [ ] 修复所有 Auth API 路径
- [ ] 修复所有 Habits API 路径
- [ ] 修复所有 Dashboard API 路径
- [ ] 添加 API 路径检查脚本到 CI/CD
- [ ] 创建 API 集成测试框架

---

**状态**: 🔴 进行中  
**负责人**: 开发团队  
**截止日期**: 2026-03-08
