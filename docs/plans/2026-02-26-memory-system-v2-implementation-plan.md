# 记忆系统架构 v2.0 - 实施计划

**日期**: 2026-02-26  
**状态**: 待执行 🔄  
**版本**: 1.0

## 项目概述

实施记忆系统架构 v2.0，将短期记忆队列从**内存队列 + 重启加载机制**简化为**SQLite嵌入式持久化队列**。

### 架构变更亮点
1. ✅ **默认队列后端**: SQLite嵌入式持久化队列（替代内存队列）
2. ✅ **简化状态管理**: 移除源数据表的`is_indexed`字段
3. ✅ **自动重启恢复**: SQLite文件自动持久化，无需手动加载
4. ✅ **部署友好**: 仅通过环境变量配置，生产代码零更改

### 技术决策
- **队列后端**: SQLite嵌入式数据库作为默认实现
- **状态标记**: 队列状态由SQLite内部管理，不再依赖源数据表`is_indexed`字段  
- **重启恢复**: SQLite文件自动恢复队列状态，移除`short_term_memory_loader.py`
- **未来扩展**: 保留Redis队列选项，用于生产环境水平扩展

## 实施范围

### 包含的功能
1. ✅ 移除源数据表的`is_indexed`字段（餐食、运动、习惯、健康记录、饮水）
2. ✅ 删除`short_term_memory_loader.py`启动加载器
3. ✅ 更新记忆索引服务，不再标记源记录
4. ✅ 更新记忆索引Pipeline，移除`_mark_*_as_indexed`方法
5. ✅ 数据库迁移脚本（删除`is_indexed`列）
6. ✅ 配置默认队列后端为SQLite
7. ✅ 测试SQLite队列的持久化和恢复功能
8. ✅ 更新相关文档

### 不包含的功能
1. ❌ 前端界面变更
2. ❌ 用户API接口变更  
3. ❌ 长期记忆存储结构变更
4. ❌ 向量索引算法变更

## 影响分析

### 受影响的模块
| 模块 | 变更类型 | 影响程度 | 备注 |
|------|----------|----------|------|
| `short_term_memory_loader.py` | 删除 | 高 | 整个文件移除 |
| `short_term_memory.py` | 修改 | 中 | 默认后端改为SQLite，移除内存队列选项 |
| `memory_index_service.py` | 修改 | 低 | 移除`_mark_source_as_indexed`函数 |
| `memory_index_pipeline.py` | 修改 | 中 | 移除`_mark_*_as_indexed`方法调用 |
| 源数据表（meals等） | 结构变更 | 高 | 删除`is_indexed`列 |
| `sqlite_queue.py` | 新增 | 高 | 已实现，需验证 |
| 部署配置 | 配置变更 | 低 | 设置`MEMORY_QUEUE_BACKEND=sqlite` |

### 数据库变更
| 表名 | 列名 | 变更类型 | 默认值 | 备注 |
|------|------|----------|--------|------|
| `meals` | `is_indexed` | 删除 | - | 不再需要状态标记 |
| `exercise_checkins` | `is_indexed` | 删除 | - | 不再需要状态标记 |
| `habits` | `is_indexed` | 删除 | - | 不再需要状态标记 |
| `health_records` | `is_indexed` | 删除 | - | 不再需要状态标记 |
| `water_intakes` | `is_indexed` | 删除 | - | 不再需要状态标记 |

## 实施阶段

### 阶段1：代码清理与重构（预计：2-3天）

#### 任务1.1：移除启动加载器
- **负责人**: 后端开发
- **预计时间**: 1天
- **依赖**: 无
- **交付物**: 
  - 删除`short_term_memory_loader.py`文件
  - 移除`main.py`中的启动加载调用

**具体任务：**
1. 删除文件：`backend/app/services/short_term_memory_loader.py`
2. 修改`backend/app/main.py`：
   - 移除`load_pending_memories_on_startup`导入
   - 移除`load_pending_memories_on_startup(db)`调用
   - 更新相关日志信息
3. 删除所有对`short_term_memory_loader`的引用
4. 运行测试确保没有导入错误

#### 任务1.2：更新记忆索引服务
- **负责人**: 后端开发
- **预计时间**: 1天
- **依赖**: 任务1.1完成
- **交付物**:
  - 更新`memory_index_service.py`
  - 移除源记录标记逻辑

**具体任务：**
1. 修改`backend/app/services/memory_index_service.py`：
   - 删除`_mark_source_as_indexed`函数（第126-143行）
   - 移除`_mark_source_as_indexed(db, overflow_item)`调用（第95行）
   - 更新相关日志和注释
2. 验证索引功能仍正常工作
3. 运行相关单元测试

#### 任务1.3：更新记忆索引Pipeline
- **负责人**: 后端开发
- **预计时间**: 1天
- **依赖**: 任务1.2完成
- **交付物**:
  - 更新`memory_index_pipeline.py`
  - 移除所有`_mark_*_as_indexed`方法

**具体任务：**
1. 修改`backend/app/services/memory_index_pipeline.py`：
   - 删除`_mark_meal_as_indexed`方法
   - 删除`_mark_exercise_as_indexed`方法  
   - 删除`_mark_habit_as_indexed`方法
   - 删除`_mark_health_record_as_indexed`方法
   - 删除所有对这些方法的调用（第336、379、422、578-593行等）
   - 更新相关日志和注释
2. 验证Pipeline仍能正常处理数据
3. 运行相关测试

### 阶段2：数据库迁移（预计：2-3天）

#### 任务2.1：创建数据库迁移脚本
- **负责人**: 后端开发
- **预计时间**: 2天
- **依赖**: 阶段1完成
- **交付物**:
  - Alembic迁移脚本
  - 回滚脚本
  - 数据验证脚本

**具体任务：**
1. 创建迁移脚本：`backend/alembic/versions/2026_02_26_remove_is_indexed_columns.py`
2. 实现删除列操作：
   ```python
   # 前向迁移：删除is_indexed列
   op.drop_column('meals', 'is_indexed')
   op.drop_column('exercise_checkins', 'is_indexed')
   op.drop_column('habits', 'is_indexed')
   op.drop_column('health_records', 'is_indexed')
   op.drop_column('water_intakes', 'is_indexed')
   ```
3. 实现回滚操作：
   ```python
   # 回滚：重新添加is_indexed列
   op.add_column('meals', sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='false'))
   op.add_column('exercise_checkins', sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='false'))
   op.add_column('habits', sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='false'))
   op.add_column('health_records', sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='false'))
   op.add_column('water_intakes', sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='false'))
   ```
4. 创建数据验证脚本，确保删除列后系统正常运行

#### 任务2.2：更新ORM模型定义
- **负责人**: 后端开发
- **预计时间**: 1天
- **依赖**: 任务2.1完成
- **交付物**:
  - 更新所有源数据模型定义
  - 验证模型与数据库同步

**具体任务：**
1. 修改以下模型文件，删除`is_indexed`字段定义：
   - `backend/app/models/nutrition.py`（Meal模型，第48行）
   - `backend/app/models/exercise_checkin.py`（第53行）
   - `backend/app/models/habit.py`（第73行）
   - `backend/app/models/health_record.py`（第66行）
   - `backend/app/models/water_intake.py`（如果存在）
2. 更新相关导入和引用
3. 运行模型测试确保没有定义错误

### 阶段3：队列配置与优化（预计：2-3天）

#### 任务3.1：更新短期记忆服务配置
- **负责人**: 后端开发
- **预计时间**: 1天
- **依赖**: 阶段2完成
- **交付物**:
  - 更新默认队列后端为SQLite
  - 优化SQLite队列配置

**具体任务：**
1. 修改`backend/app/services/short_term_memory.py`：
   - 将默认后端从`'memory'`改为`'sqlite'`（第109行）
   - 可选：移除内存队列选项，仅保留SQLite和Redis
   - 更新文档字符串和注释
2. 配置SQLite数据库路径：
   - 默认路径：`./data/memory_queue.db`
   - 支持通过`SQLITE_QUEUE_DB_PATH`环境变量自定义
3. 验证SQLite队列正确初始化

#### 任务3.2：验证SQLite队列实现
- **负责人**: 后端开发
- **预计时间**: 2天
- **依赖**: 任务3.1完成
- **交付物**:
  - SQLite队列功能测试
  - 持久化恢复测试
  - 性能基准测试

**具体任务：**
1. 测试`sqlite_queue.py`的完整功能：
   - FIFO队列行为
   - 容量限制（100条）
   - 溢出处理
2. 验证持久化恢复：
   - 重启服务后队列状态恢复
   - 数据一致性检查
3. 性能测试：
   - 与内存队列的对比
   - 并发访问测试
4. 编写集成测试

### 阶段4：测试与验证（预计：3-4天）

#### 任务4.1：单元测试更新
- **负责人**: 测试工程师
- **预计时间**: 2天
- **依赖**: 阶段3完成
- **交付物**:
  - 更新所有相关单元测试
  - 测试通过率100%

**具体任务：**
1. 更新`short_term_memory_loader.py`相关测试（删除或修改）
2. 更新`memory_index_service.py`测试，移除状态标记验证
3. 更新`memory_index_pipeline.py`测试，移除状态标记验证
4. 添加`sqlite_queue.py`单元测试
5. 运行完整测试套件

#### 任务4.2：集成测试
- **负责人**: 测试工程师
- **预计时间**: 2天
- **依赖**: 任务4.1完成
- **交付物**:
  - 端到端集成测试
  - 性能回归测试

**具体任务：**
1. 创建端到端测试场景：
   - 数据创建 → 短期记忆队列 → 溢出 → 长期记忆索引
   - 服务重启 → 队列恢复 → 继续处理
2. 验证完整记忆流程：
   - 餐食记录处理
   - 运动记录处理
   - 习惯记录处理
3. 性能回归测试：
   - 响应时间基准
   - 内存使用情况
   - 数据库连接数

#### 任务4.3：生产环境模拟
- **负责人**: DevOps工程师
- **预计时间**: 1天
- **依赖**: 任务4.2完成
- **交付物**:
  - 生产环境配置验证
  - 部署检查清单

**具体任务：**
1. 模拟生产环境部署：
   - 设置`MEMORY_QUEUE_BACKEND=sqlite`
   - 配置`SQLITE_QUEUE_DB_PATH`
   - 验证服务启动
2. 测试高可用场景：
   - 多个实例共享SQLite文件（需注意文件锁）
   - 备份与恢复过程
3. 创建部署检查清单

### 阶段5：部署与监控（预计：2-3天）

#### 任务5.1：部署配置更新
- **负责人**: DevOps工程师
- **预计时间**: 1天
- **依赖**: 阶段4完成
- **交付物**:
  - 更新部署配置
  - 环境变量配置

**具体任务：**
1. 更新Docker配置：
   - 设置默认环境变量
   - 确保`./data`目录可写
2. 更新Kubernetes配置：
   - ConfigMap更新
   - 持久化卷配置
3. 更新CI/CD流水线：
   - 测试环境配置
   - 生产环境配置

#### 任务5.2：监控与告警
- **负责人**: DevOps工程师
- **预计时间**: 2天
- **依赖**: 任务5.1完成
- **交付物**:
  - 监控仪表板
  - 告警规则

**具体任务：**
1. 添加SQLite队列监控：
   - 队列大小监控
   - 磁盘使用监控
   - 文件锁状态监控
2. 创建Grafana仪表板：
   - 记忆队列状态
   - 索引处理统计
3. 设置告警规则：
   - SQLite文件增长异常
   - 队列处理延迟
   - 索引失败率

## 技术实现细节

### 代码变更清单

#### 删除的文件
1. `backend/app/services/short_term_memory_loader.py` - 启动加载器

#### 修改的文件
1. `backend/app/main.py` - 移除启动加载调用
2. `backend/app/services/short_term_memory.py` - 默认后端改为SQLite
3. `backend/app/services/memory_index_service.py` - 移除`_mark_source_as_indexed`
4. `backend/app/services/memory_index_pipeline.py` - 移除`_mark_*_as_indexed`方法
5. `backend/app/models/nutrition.py` - 移除`is_indexed`字段
6. `backend/app/models/exercise_checkin.py` - 移除`is_indexed`字段
7. `backend/app/models/habit.py` - 移除`is_indexed`字段
8. `backend/app/models/health_record.py` - 移除`is_indexed`字段

#### 新增的文件
1. `backend/app/services/sqlite_queue.py` - 已实现，需验证

### 数据库迁移策略

#### 迁移时机
- **开发环境**: 立即执行，验证功能
- **测试环境**: 阶段测试后执行
- **生产环境**: 低流量时段执行

#### 数据安全
1. **备份策略**:
   ```bash
   # 迁移前备份
   pg_dump -h localhost -U postgres bmad_db > backup_pre_migration.sql
   
   # 备份SQLite队列文件
   cp ./data/memory_queue.db ./data/memory_queue.db.backup
   ```

2. **回滚准备**:
   - 保留迁移回滚脚本
   - 准备数据恢复流程
   - 验证回滚后系统功能

#### 迁移验证
```sql
-- 验证is_indexed列已删除
SELECT column_name 
FROM information_schema.columns 
WHERE table_name IN ('meals', 'exercise_checkins', 'habits', 'health_records', 'water_intakes')
  AND column_name = 'is_indexed';
-- 预期结果：0行

-- 验证系统功能
SELECT COUNT(*) FROM meals;  -- 应正常返回
```

### 配置变更

#### 环境变量
```bash
# 必需配置
MEMORY_QUEUE_BACKEND=sqlite  # 默认值，可省略

# 可选配置
SQLITE_QUEUE_DB_PATH=./data/memory_queue.db  # 默认值
SQLITE_QUEUE_MAX_SIZE=100  # 默认值
```

#### Docker Compose 配置
```yaml
services:
  backend:
    environment:
      - MEMORY_QUEUE_BACKEND=sqlite
      - SQLITE_QUEUE_DB_PATH=/app/data/memory_queue.db
    volumes:
      - ./data:/app/data  # 持久化SQLite文件
```

#### Kubernetes 配置
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  MEMORY_QUEUE_BACKEND: "sqlite"
  SQLITE_QUEUE_DB_PATH: "/data/memory_queue.db"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: memory-queue-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

### 测试策略

#### 单元测试重点
1. **SQLite队列测试**:
   ```python
   def test_sqlite_queue_persistence():
       """测试SQLite队列持久化"""
       queue = SQLiteQueue(max_size=10)
       queue.push(1, {"data": "test"})
       
       # 模拟重启：创建新实例
       queue2 = SQLiteQueue(max_size=10)
       memories = queue2.get_all(1)
       assert len(memories) == 1
       assert memories[0]["data"] == "test"
   ```

2. **服务集成测试**:
   ```python
   def test_memory_flow_with_sqlite():
       """测试完整记忆流程"""
       # 创建记录 → 进入短期记忆 → 溢出 → 长期记忆索引
       # 验证is_indexed字段不再使用
   ```

#### 集成测试场景
1. **正常流程测试**: 创建100条记录，验证第101条触发索引
2. **重启恢复测试**: 添加50条记录，重启服务，验证队列恢复
3. **并发访问测试**: 多个用户同时操作，验证线程安全
4. **磁盘空间测试**: SQLite文件增长管理

## 风险管理

### 技术风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| SQLite文件锁冲突 | 中 | 中 | 实现连接池，监控文件锁状态 |
| 磁盘空间不足 | 低 | 高 | 监控磁盘使用，设置自动清理 |
| 迁移数据丢失 | 低 | 高 | 完整备份，分阶段迁移 |
| 性能下降 | 低 | 中 | 性能基准测试，优化SQLite配置 |

### 业务风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 服务重启记忆丢失 | 低 | 高 | SQLite自动持久化，验证恢复功能 |
| 索引流程中断 | 低 | 中 | 监控索引成功率，自动重试 |
| 用户数据不一致 | 低 | 高 | 数据验证脚本，完整性检查 |

### 缓解策略
1. **分阶段部署**:
   - 开发环境 → 测试环境 → 生产环境
   - 每个阶段充分验证

2. **渐进式迁移**:
   - 先部署代码，不运行迁移
   - 验证新代码兼容旧数据库
   - 执行数据库迁移

3. **回滚准备**:
   - 保留完整备份
   - 测试回滚流程
   - 准备应急方案

## 成功标准

### 技术成功标准
- ✅ 所有测试通过率100%
- ✅ SQLite队列性能满足要求（<100ms操作）
- ✅ 重启后队列100%恢复
- ✅ 零生产代码变更（仅配置变更）
- ✅ 数据库迁移成功，无数据丢失

### 业务成功标准
- ✅ 用户无感知升级
- ✅ 记忆功能完整保留
- ✅ 系统稳定性维持或提升
- ✅ 监控告警正常运作

## 资源需求

### 人力资源
| 角色 | 数量 | 参与阶段 | 主要职责 |
|------|------|----------|----------|
| 后端开发 | 2 | 阶段1-3 | 代码重构、数据库迁移 |
| 测试工程师 | 1 | 阶段4 | 测试设计、执行 |
| DevOps工程师 | 1 | 阶段5 | 部署配置、监控 |
| 技术负责人 | 1 | 全部 | 技术决策、风险管控 |

### 技术资源
| 资源 | 规格 | 数量 | 用途 |
|------|------|------|------|
| 开发环境 | 本地开发机 | 2 | 代码开发、测试 |
| 测试环境 | 独立服务器 | 1 | 集成测试、性能测试 |
| 数据库 | PostgreSQL 15 | 1 | 主数据库 |
| 监控系统 | Prometheus+Grafana | 1 | 性能监控 |

## 时间线

### 详细时间安排
```
第1周：阶段1 - 代码清理与重构 (3天)
  ├── 第1天：移除启动加载器
  ├── 第2天：更新记忆索引服务
  └── 第3天：更新记忆索引Pipeline

第2周：阶段2 - 数据库迁移 (3天)
  ├── 第4天：创建迁移脚本
  ├── 第5天：更新ORM模型
  └── 第6天：迁移测试

第3周：阶段3 - 队列配置与优化 (3天)
  ├── 第7天：更新服务配置
  ├── 第8天：验证SQLite队列
  └── 第9天：性能优化

第4周：阶段4 - 测试与验证 (4天)
  ├── 第10天：单元测试更新
  ├── 第11天：集成测试
  ├── 第12天：生产环境模拟
  └── 第13天：测试验收

第5周：阶段5 - 部署与监控 (3天)
  ├── 第14天：部署配置更新
  ├── 第15天：监控告警设置
  └── 第16天：正式上线
```

### 里程碑
| 里程碑 | 日期 | 交付物 | 验收标准 |
|--------|------|--------|----------|
| M1: 代码清理完成 | 2026-03-01 | 删除加载器，更新索引服务 | 代码编译通过，基础测试通过 |
| M2: 数据库迁移完成 | 2026-03-04 | 迁移脚本，更新模型 | 数据库变更成功，无数据丢失 |
| M3: 队列验证完成 | 2026-03-07 | SQLite队列测试报告 | 功能完整，性能达标 |
| M4: 测试完成 | 2026-03-11 | 测试报告，验收文档 | 所有测试通过，无回归 |
| M5: 生产上线 | 2026-03-14 | 生产部署，监控就绪 | 系统稳定运行，监控正常 |

## 附录

### A. 代码审查清单
1. **代码变更审查**:
   - [ ] 所有删除操作有充分理由
   - [ ] 新增代码有适当测试
   - [ ] 修改代码不影响现有功能
   - [ ] 注释和文档已更新

2. **数据库变更审查**:
   - [ ] 迁移脚本测试通过
   - [ ] 回滚脚本验证有效
   - [ ] 数据完整性验证
   - [ ] 性能影响评估

3. **配置变更审查**:
   - [ ] 环境变量定义清晰
   - [ ] 默认值安全合理
   - [ ] 部署配置完整
   - [ ] 监控配置到位

### B. 部署检查清单
- [ ] 数据库备份完成
- [ ] 迁移脚本已验证
- [ ] 回滚计划准备
- [ ] 监控系统就绪
- [ ] 团队通知发送
- [ ] 上线时间确认
- [ ] 应急联系人确认

### C. 紧急响应流程
1. **问题识别**: 监控告警 → 用户反馈 → 日志分析
2. **问题分类**:
   - P0: 系统完全不可用（立即响应）
   - P1: 核心功能受影响（15分钟内）
   - P2: 次要功能受影响（2小时内）
   - P3: 轻微问题（24小时内）
3. **恢复措施**:
   - 服务重启
   - 配置回滚
   - 数据恢复
   - 功能降级

### D. 性能基准
| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 队列操作延迟 | <100ms | 平均响应时间 |
| 重启恢复时间 | <5秒 | 服务启动到就绪 |
| 内存使用 | <50MB增长 | 监控工具 |
| 磁盘使用 | <100MB/月 | 文件大小监控 |

---

**文档版本历史**
- v1.0 (2026-02-26): 初始版本，实施计划制定

**审批记录**
- [ ] 项目经理: 待审批
- [ ] 技术负责人: 待审批
- [ ] 产品负责人: 待审批