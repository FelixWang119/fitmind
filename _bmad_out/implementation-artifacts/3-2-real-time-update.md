# Story 3.2: 实时更新机制

**Epic**: 3 - 热量平衡集成增强  
**Story ID**: 3.2  
**Story Key**: `3-2-real-time-update`  
**优先级**: P0 (MVP 核心)  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 热量数据实时更新  
**以便** 我能即时看到我的变化  

---

## ✅ 验收标准 (BDD 格式)

### AC 3.2.1: 饮食记录后实时更新

**Given** 用户记录饮食  
**When** 提交饮食记录  
**Then** 更新摄入热量  
**And** 立即刷新热量平衡显示  
**And** 显示更新动画效果

### AC 3.2.2: 运动打卡后实时更新

**Given** 用户打卡运动  
**When** 提交运动记录  
**Then** 更新运动消耗  
**And** 立即刷新热量平衡显示  
**And** 显示更新动画效果

### AC 3.2.3: WebSocket 实时推送

**Given** 用户打开热量页面  
**When** 建立 WebSocket 连接  
**Then** 实时接收热量数据更新  
**And** 无需手动刷新页面

### AC 3.2.4: 并发更新处理

**Given** 计算复杂  
**When** 多个用户同时操作  
**Then** 系统能处理并发更新  
**And** 保持数据一致性

---

## 🏗️ 技术需求

### WebSocket 端点

```python
# 后端 WebSocket
@router.websocket("/ws/calorie-balance")
async def calorie_balance_websocket(websocket: WebSocket):
    """实时热量平衡推送"""
    await websocket.accept()
    try:
        while True:
            # 监听热量更新事件
            data = await redis.subscribe("calorie:update:user_id")
            await websocket.send_json(data)
    except Exception:
        await websocket.close()
```

### 前端实时更新

```tsx
// 使用 SWR 或 React Query 实现实时更新
const { data } = useSWR(
  '/api/v1/calorie-balance',
  fetcher,
  { refreshInterval: 5000 } // 每5秒轮询
);
```

---

## 🔄 依赖关系

- **前置**: Story 3.1 (三栏展示) - 本 Epic 内
- **后续**: 无

---

## 🧪 测试用例

1. `test_meal_record_triggers_update` - 饮食记录触发更新
2. `test_exercise_checkin_triggers_update` - 运动打卡触发更新
3. `test_concurrent_updates` - 并发更新处理
