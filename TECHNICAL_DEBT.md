# 技术债务文档 (Technical Debt)

**创建日期**: 2026-02-24  
**最后更新**: 2026-02-24  
**优先级说明**: P0-紧急 | P1-高 | P2-中 | P3-低

---

## 📋 目录

1. [认证与授权](#认证与授权)
2. [前端优化](#前端优化)
3. [后端优化](#后端优化)
4. [测试覆盖](#测试覆盖)
5. [文档完善](#文档完善)

---

## 认证与授权

### AUTH-001: Token 自动刷新机制

**优先级**: P1 - 高  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

当前 JWT Token 有效期为 30 分钟，过期后用户请求会收到 401 Unauthorized 错误，导致：
- 饮食照片上传后保存失败
- 用户需要手动重新登录
- 用户体验中断

**日志证据**:
```json
{"error": "Signature has expired.", "event": "Token verification failed"}
INFO: 127.0.0.1:63344 - "PUT /api/v1/meals/14 HTTP/1.1" 401 Unauthorized
```

#### 当前行为
1. 用户登录获取 token（有效期 30 分钟）
2. 30 分钟后 token 过期
3. 用户操作触发 401 错误
4. 用户需要手动重新登录

#### 期望行为
1. 前端监测 token 有效期
2. 在 token 即将过期时（如剩余 5 分钟）自动刷新
3. 无感知续期，用户体验不中断
4. 仅在刷新失败时才要求重新登录

#### 技术方案

**方案 A: 双 Token 机制（推荐）**
```typescript
// 访问 token (30 分钟) + 刷新 token (7 天)
interface AuthTokens {
  accessToken: string;  // 短期
  refreshToken: string; // 长期
}

// 刷新逻辑
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  const response = await api.post('/auth/refresh', { refreshToken });
  // 更新 access token
}

// 定时检查
setInterval(() => {
  const expiryTime = getAccessTokenExpiry();
  const timeLeft = expiryTime - Date.now();
  if (timeLeft < 5 * 60 * 1000) { // 剩余 5 分钟
    refreshAccessToken();
  }
}, 60 * 1000); // 每分钟检查
```

**方案 B: 拦截器自动刷新**
```typescript
// Axios 拦截器
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        await refreshAccessToken();
        // 重试原请求
        return api.request(error.config);
      } catch (e) {
        // 刷新失败，跳转登录
        redirectToLogin();
      }
    }
    return Promise.reject(error);
  }
);
```

#### 影响范围

**需要修改的文件**:
- `frontend/src/api/client.ts` - 添加 token 刷新逻辑
- `frontend/src/store/authStore.ts` - 存储 refresh token
- `backend/app/api/v1/endpoints/auth.py` - 添加刷新接口

**后端需要新增**:
```python
@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """刷新访问令牌"""
    # 验证 refresh token
    # 生成新的 access token
    return {"access_token": new_token}
```

#### 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| Refresh token 泄露 | 低 | 高 | 存储到 HttpOnly cookie |
| 刷新请求被劫持 | 低 | 高 | 使用 HTTPS |
| 无限续期 | 中 | 中 | refresh token 设置最长有效期（如 7 天） |

#### 验收标准

- [ ] Token 过期前 5 分钟自动刷新
- [ ] 刷新过程用户无感知
- [ ] 刷新失败时提示用户重新登录
- [ ] Refresh token 安全存储
- [ ] 支持 token 强制失效（登出时）

#### 相关工作

- 后端 API: `/auth/refresh` (待实现)
- 前端存储: authStore (待修改)
- 安全策略: Token 有效期配置 (待优化)

---

### AUTH-002: 密码重置功能安全性增强

**优先级**: P2 - 中  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

LSP 错误显示密码重置功能存在类型不匹配问题：
```
ERROR [357:51] Argument of type "Column[str]" cannot be assigned to parameter "to_email"
ERROR [400:24] Cannot assign to attribute "used" for class "PasswordResetToken"
```

#### 技术细节

需要检查：
- 密码重置 token 的生成和验证逻辑
- Token 使用状态标记
- 邮件发送服务集成

#### 验收标准

- [ ] 修复类型错误
- [ ] Token 一次性使用
- [ ] Token 过期时间合理（如 1 小时）
- [ ] 邮件发送失败有提示

---

## 前端优化

### FE-001: TypeScript 严格模式错误清理

**优先级**: P3 - 低  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

项目中存在大量 TypeScript 严格检查错误（约 98 个），虽然不影响打包，但可能导致潜在 bug：

**主要错误类型**:
1. 未使用的变量和导入（~40 个）
2. 类型不匹配（~20 个）
3. 缺失的属性（~20 个）
4. 私有成员访问（~10 个）
5. 依赖缺失（如 `recharts`）

**影响文件**:
- `src/pages/HealthReports.tsx` - 35+ 错误
- `src/pages/DynamicAIAssistant.tsx` - 5+ 错误
- `src/pages/Gamification.tsx` - 4+ 错误
- `src/components/layout/Header.tsx` - 1 错误

#### 解决方案

1. **立即修复**: 关键类型错误
2. **逐步清理**: 每次修改一个模块
3. **配置调整**: 考虑在 `tsconfig.json` 中调整严格程度

#### 验收标准

- [ ] 关键类型错误全部修复
- [ ] 未使用变量/导入清理完毕
- [ ] 缺失依赖安装完成
- [ ] TypeScript 编译无错误

---

### FE-002: 错误提示优化

**优先级**: P2 - 中  
**发现日期**: 2026-02-24  
**状态**: ✅ 部分完成

#### 当前状态

已将全局 error 状态改为 alert 提示，避免影响界面：
```typescript
// 修复前
setError('保存失败');

// 修复后
alert('保存失败，请重试');
```

#### 待改进

**建议使用 Toast 通知代替 alert**:
```typescript
// 更好的用户体验
toast.error('保存失败，请重试', {
  duration: 3000,
  position: 'top-center'
});
```

**推荐库**: `react-toastify` 或 `sonner`

#### 验收标准

- [ ] 统一错误提示方式
- [ ] Toast 自动消失
- [ ] 支持多条错误同时显示
- [ ] 美观的 UI 设计

---

### FE-003: 日期选择器功能

**优先级**: P3 - 低  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

当前 `selectedDate` 固定为今天，`setSelectedDate` 未使用：
```typescript
const [selectedDate] = useState<string>(() => {
  // 只能选择今天
  return new Date().toISOString().split('T')[0];
});
// setSelectedDate 未使用
```

#### 期望功能

用户应该能够查看历史日期的饮食记录：
- 添加日期选择器组件
- 支持查看任意日期的记录
- 支持快速切换（昨天、今天、明天）

#### 验收标准

- [ ] 日期选择器 UI
- [ ] 切换日期时刷新数据
- [ ] 显示选中日期的餐食记录
- [ ] 未来日期不能上传餐食

---

## 后端优化

### BE-001: 数据库连接池优化

**优先级**: P2 - 中  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

当前使用 SQLite，每次请求都创建新连接。建议：
- 使用连接池
- 配置合理的连接数
- 添加连接超时机制

#### 验收标准

- [ ] 实现连接池
- [ ] 配置连接数参数
- [ ] 添加性能监控

---

### BE-002: AI 服务降级处理

**优先级**: P1 - 高  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

日志显示 Qwen API 有时会断开连接：
```json
{"response": "Server disconnected without sending a response.", 
 "event": "HTTP error from Qwen API, using fallback"}
```

当前使用模拟数据作为降级方案，但应该：
- 记录 API 失败次数
- 实现重试机制
- 提供友好的错误提示

#### 验收标准

- [ ] 实现重试机制（最多 3 次）
- [ ] 记录 API 健康状态
- [ ] 失败时提示用户"AI 服务暂时不可用"
- [ ] 仍允许用户手动输入食材

---

## 测试覆盖

### TEST-001: 端到端测试缺失

**优先级**: P1 - 高  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

缺少完整的 E2E 测试覆盖，以下场景未测试：
1. 上传照片 → AI 识别 → 保存餐食
2. Token 过期 → 刷新 → 重试请求
3. 切换日期 → 查看历史记录
4. 删除餐食 → 验证数据清除

#### 建议方案

**使用 Playwright 或 Cypress**:
```typescript
// Playwright 示例
test('upload and save meal', async ({ page }) => {
  await page.goto('/diet');
  await page.click('[data-testid="upload-photo"]');
  await page.setInputFiles('input[type="file"]', 'test-food.jpg');
  await page.click('[data-testid="confirm-save"]');
  await expect(page.locator('[data-testid="meal-list"]')).toContainText('dinner');
});
```

#### 验收标准

- [ ] 核心流程 E2E 测试覆盖
- [ ] 关键 API 接口测试
- [ ] 错误场景测试
- [ ] 测试覆盖率 > 80%

---

### TEST-002: 单元测试补充

**优先级**: P2 - 中  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

以下模块缺少单元测试：
- `food_image_analyzer.py` - AI 图像分析
- `meal_service.py` - 餐食服务逻辑
- `calorie_service.py` - 热量计算

#### 验收标准

- [ ] 服务层单元测试
- [ ] 工具函数测试
- [ ] 边界条件测试
- [ ]  mocking 外部依赖

---

## 文档完善

### DOC-001: API 文档同步

**优先级**: P2 - 中  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

API 变更未及时更新文档：
- FastAPI 自动生成 `/docs` (Swagger)
- 但缺少业务逻辑说明
- 缺少错误码说明

#### 验收标准

- [ ] 所有接口有详细描述
- [ ] 错误码文档完整
- [ ] 提供使用示例
- [ ] 定期同步更新

---

### DOC-002: 部署文档

**优先级**: P3 - 低  
**发现日期**: 2026-02-24  
**状态**: ⏳ 待处理

#### 问题描述

缺少完整的部署指南：
- 环境配置说明
- 数据库迁移步骤
- 常见问题 FAQ

#### 验收标准

- [ ] 部署步骤文档化
- [ ] 配置文件说明
- [ ] 故障排查指南
- [ ] 性能调优建议

---

## 📊 技术债务统计

| 优先级 | 数量 | 占比 |
|--------|------|------|
| P0 - 紧急 | 0 | 0% |
| P1 - 高 | 3 | 25% |
| P2 - 中 | 5 | 42% |
| P3 - 低 | 4 | 33% |
| **总计** | **12** | **100%** |

---

## 📈 趋势图

### 按类别分布

```
认证与授权：██ 2 项
前端优化：  ███ 3 项
后端优化：  ██ 2 项
测试覆盖：  ██ 2 项
文档完善：  ██ 2 项
```

---

## 🎯 下一步行动

### 本周内完成 (P1)
- [ ] AUTH-001: Token 自动刷新机制
- [ ] BE-002: AI 服务降级处理
- [ ] TEST-001: 端到端测试框架搭建

### 本月内完成 (P2)
- [ ] FE-002: 错误提示优化（Toast）
- [ ] BE-001: 数据库连接池优化
- [ ] TEST-002: 核心模块单元测试
- [ ] DOC-001: API 文档完善

### 下次迭代 (P3)
- [ ] FE-001: TypeScript 错误清理
- [ ] FE-003: 日期选择器功能
- [ ] DOC-002: 部署文档

---

## 📝 变更记录

| 日期 | 操作 | 说明 |
|------|------|------|
| 2026-02-24 | 创建文档 | 初始版本，记录 12 项技术债务 |
| 2026-02-24 | 添加 AUTH-001 | Token 自动刷新机制（高优先级） |

---

**维护者**: Development Team  
**审查周期**: 每季度审查一次  
**最后审查日期**: 2026-02-24
