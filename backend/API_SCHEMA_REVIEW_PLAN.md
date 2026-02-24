# API Schema 完整性 Review 计划

## 🎯 问题背景

在饮食打卡功能中发现前后端字段名不匹配：
- 后端返回：`meal_items`
- 前端期望：`items`

这导致前端显示"暂无食材详情"，而数据实际已正确保存到数据库。

## 📊 影响范围评估

### 高风险模块（需要优先 Review）

| 模块 | Schema 文件 | Endpoints | 风险点 |
|------|------------|-----------|--------|
| **Meals** | `schemas/meal_models.py` | `/api/v1/meals/*` | ✅ 已修复 |
| **Habits** | `schemas/habit_models.py` | `/api/v1/habits/*` | ⚠️ 待检查 |
| **Health** | `schemas/health_models.py` | `/api/v1/health/*` | ⚠️ 待检查 |
| **Dashboard** | `schemas/dashboard_models.py` | `/api/v1/dashboard/*` | ⚠️ 待检查 |
| **Gamification** | `schemas/gamification_models.py` | `/api/v1/gamification/*` | ⚠️ 待检查 |
| **Users** | `schemas/user.py` | `/api/v1/users/*` | ⚠️ 待检查 |

### 检查清单

#### 1. Schema 字段命名一致性
- [ ] 所有响应模型的字段名与前端期望一致
- [ ] 避免使用 `serialization_alias` 导致字段名变化
- [ ] 使用 `alias` 时确保前端了解映射关系

#### 2. CRUD 操作完整性
- [ ] `Create` schema 包含所有必要字段
- [ ] `Update` schema 包含所有可更新字段（包括嵌套对象）
- [ ] `Update` 端点正确处理嵌套对象的创建/更新/删除
- [ ] `Delete` 端点处理级联删除

#### 3. 关系数据加载
- [ ] 使用 `joinedload` 预加载关系数据
- [ ] 响应中包含前端需要的所有关系字段
- [ ] 循环引用问题已处理

#### 4. 端到端测试覆盖
- [ ] API 测试验证完整响应结构
- [ ] 前端 Mock 数据与实际 API 一致
- [ ] 集成测试覆盖完整用户流程

## 🔍 Review 步骤

### Step 1: Schema 审查
```bash
# 列出所有 schema 文件
find backend/app/schemas -name "*.py" -type f

# 检查每个 schema 的字段定义
# 特别关注：
# - 是否有 serialization_alias
# - Update schema 是否缺少字段
# - 关系字段是否正确定义
```

### Step 2: Endpoint 审查
```bash
# 列出所有 endpoints
find backend/app/api -name "*.py" -type f

# 检查每个 update 端点：
# - 是否处理嵌套对象
# - 是否正确处理 items/children 字段
```

### Step 3: 前端 API 客户端审查
```bash
# 检查前端 API 调用
grep -r "api\." frontend/src --include="*.tsx" --include="*.ts"

# 验证字段名使用情况
```

### Step 4: 集成测试
```bash
# 运行所有 API 测试
cd backend && pytest tests/ -v

# 检查测试覆盖率
pytest --cov=app tests/
```

## 📝 推荐修复模式

### Update Schema 模式
```python
class MealUpdate(BaseModel):
    """更新餐饮"""
    meal_type: Optional[str] = None
    name: Optional[str] = None
    # ✅ 包含所有可更新字段
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    # ✅ 包含嵌套对象
    items: Optional[List[MealItemCreate]] = None
```

### Update Endpoint 模式
```python
@router.put("/{meal_id}", response_model=MealSchema)
async def update_meal(
    meal_id: int,
    meal_update: MealUpdate,
    db: Session,
    current_user: UserModel
):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    update_data = meal_update.model_dump(exclude_unset=True)
    items_data = update_data.pop('items', None)  # ✅ 分离嵌套对象
    
    # 更新基本字段
    for field, value in update_data.items():
        setattr(meal, field, value)
    
    # ✅ 处理嵌套对象
    if items_data is not None:
        # 删除旧的
        for existing_item in meal.meal_items:
            db.delete(existing_item)
        db.flush()
        
        # 创建新的
        if items_data:
            for item_data in items_data:
                meal_item = MealItem(**item_data, meal_id=meal.id)
                db.add(meal_item)
    
    db.commit()
    db.refresh(meal)
    return meal
```

### Schema 字段命名模式
```python
# ❌ 避免使用 serialization_alias
items: List[MealItem] = Field(
    default_factory=list,
    serialization_alias="meal_items",  # 会导致前端拿不到数据
)

# ✅ 直接使用数据库字段名
meal_items: List[MealItem] = Field(default_factory=list)

# 或者使用 alias（双向绑定）
items: List[MealItem] = Field(
    default_factory=list,
    alias="meal_items",  # 输入输出都使用 meal_items
)
```

## 🚀 执行计划

| 优先级 | 模块 | 预计时间 | 状态 |
|--------|------|----------|------|
| P0 | Meals | ✅ 已完成 | Done |
| P1 | Habits | 2 小时 | Pending |
| P2 | Health | 2 小时 | Pending |
| P2 | Dashboard | 1 小时 | Pending |
| P3 | Gamification | 2 小时 | Pending |
| P3 | Users | 1 小时 | Pending |

## ✅ 验证标准

1. **自动化测试**
   - 所有 API 测试通过
   - 集成测试覆盖所有 CRUD 操作
   
2. **手动验证**
   - 前端能正确显示所有数据
   - 更新操作能正确保存嵌套对象
   
3. **文档化**
   - API 文档与实现一致
   - 前端 API 客户端类型定义准确

---

**生成时间**: 2026-02-24  
**执行状态**: 待启动
