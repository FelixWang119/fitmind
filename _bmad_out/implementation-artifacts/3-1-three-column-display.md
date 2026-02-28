# Story 3.1: 热量平衡三栏展示

**Epic**: 3 - 热量平衡集成增强  
**Story ID**: 3.1  
**Story Key**: `3-1-three-column-display`  
**优先级**: P0 (MVP 核心)  
**故事点数**: 5 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 查看热量平衡的详细对比  
**以便** 我能清楚了解我的热量盈亏状况  

---

## ✅ 验收标准 (BDD 格式)

### AC 3.1.1: 三栏热量展示

**Given** 用户访问首页或热量页面  
**When** 查看热量信息  
**Then** 显示三栏对比:
- 左栏: 今日摄入热量 (from meals)
- 中栏: 基础代谢 BMR (calculated from profile)
- 右栏: 运动消耗 (from exercise_checkins)
- 底部: 热量盈余 = 摄入 - 基础代谢 - 运动消耗

### AC 3.1.2: 热量数值显示

**Given** 用户查看热量数据  
**When** 数据已计算  
**Then** 显示:
- 数值使用大号字体突出显示
- 单位 (kcal) 明确标注
- 与目标对比显示 (如: "超出 200 kcal")

### AC 3.1.3: 热量进度条

**Given** 用户查看热量平衡  
**When** 显示热量数据  
**Then** 显示进度条:
- 显示目标热量 vs 实际摄入
- 颜色区分: 绿色(未超)/橙色(接近)/红色(超出)

### AC 3.1.4: 热量趋势图

**Given** 用户查看热量数据  
**When** 查看历史趋势  
**Then** 显示:
- 近 7 天热量趋势折线图
- 标记目标线
- 显示每日详情

---

## 🏗️ 技术需求

### 后端 API

**文件**: `backend/app/api/v1/endpoints/calorie_balance.py` (新建)

```python
@router.get("/calorie-balance")
def get_calorie_balance(
    date: str = Query(None),  # YYYY-MM-DD
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取热量平衡数据"""
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    
    # 1. 获取摄入热量
    intake = get_daily_calorie_intake(db, current_user.id, target_date)
    
    # 2. 计算基础代谢 BMR
    bmr = calculate_bmr(current_user)
    
    # 3. 获取运动消耗
    burn = get_daily_exercise_burn(db, current_user.id, target_date)
    
    # 4. 计算热量盈余
    surplus = intake - bmr - burn
    
    # 5. 计算进度百分比
    progress = min(100, (intake / bmr) * 100) if bmr > 0 else 0
    
    return {
        "date": target_date,
        "intake": intake,  # 摄入
        "bmr": bmr,  # 基础代谢
        "burn": burn,  # 运动消耗
        "surplus": surplus,  # 盈余
        "net": bmr + burn - intake,  # 净消耗
        "progress": progress,
        "target": bmr,  # 目标摄入
    }
```

### 前端组件

**文件**: `frontend/src/components/CalorieBalanceSection.tsx` (扩展)

```tsx
// 热量平衡三栏展示组件
// - Left: 摄入热量
// - Center: BMR 基础代谢
// - Right: 运动消耗
// - Bottom: 热量盈余/亏损
```

---

## 🔄 依赖关系

- **前置**: Story 2.2 (目标创建与追踪) - Epic 2 已完成 ✅
- **后续**: Story 3.2 (实时更新机制)

---

## 🧪 测试用例

1. `test_calorie_balance_calculation` - 热量计算正确性
2. `test_bmr_calculation` - BMR 计算
3. `test_surplus_display` - 盈余显示
4. `test_progress_bar_color` - 进度条颜色
