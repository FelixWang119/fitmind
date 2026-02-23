# Story 2.4: 情感陪伴角色对话

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为需要情感支持的用户，
我想要与AI情感陪伴对话，
以便我可以在减肥过程中获得情感支持和鼓励。

## Acceptance Criteria

1. **Given** 用户在聊天界面 **When** 用户表达情感需求（如"我感到很沮丧"） **Then** 系统识别情感支持话题 **And** 切换到情感陪伴角色模式

2. **Given** AI处于情感陪伴角色模式 **When** 用户分享情绪感受 **Then** AI提供共情回应 **And** 使用温和、支持性的语言

3. **Given** 用户表达压力或焦虑 **When** 用户描述压力来源 **Then** AI提供压力管理建议 **And** 教授放松技巧

4. **Given** 用户需要鼓励 **When** 用户表达自我怀疑 **Then** AI提供积极心理暗示 **And** 强调用户的进步和努力

## Tasks / Subtasks

- [x] Task 1 (AC: #1)
  - [x] 实现情感陪伴角色识别逻辑
  - [x] 实现角色切换到情感陪伴模式
  - [x] 前端显示角色切换提示
- [x] Task 2 (AC: #2)
  - [x] 实现共情回应生成逻辑
  - [x] 设计温和、支持性语言模板
  - [x] 集成到 AI 对话服务
- [x] Task 3 (AC: #3)
  - [x] 实现压力管理建议生成
  - [x] 添加放松技巧库
  - [x] 前端显示建议卡片
- [x] Task 4 (AC: #4)
  - [x] 实现积极心理暗示生成
  - [x] 集成用户进步数据获取
  - [x] 前端显示鼓励消息

## Dev Notes

### Project Structure Notes

- 后端: `app/services/ai_service.py` - 扩展角色类型支持情感陪伴
- 前端: `frontend/src/pages/Chat.tsx` - 添加情感陪伴角色 UI
- 角色系统: 参考现有 `story-2.2` (营养师) 和 `story-2.3` (行为教练) 的实现模式

### Technical Considerations

- 情感陪伴角色需要特殊的 prompt 模板，保持温和语调
- 需要集成用户历史数据获取（进步、成就）用于个性化鼓励
- 情绪识别可复用现有的情感分析模块

### References

- [Source: _bmad_out/planning-artifacts/epics.md#Story-2.4]
- [Source: _bmad_out/implementation-artifacts/1-2-user-login.md - 角色模式参考]

## Dev Agent Record

### Agent Model Used

OpenAI / Claude (minimax-m2.5-free)

### Debug Log References

- Backend AI service: `app/services/ai_service.py`
- Role services: `app/services/ai_role_services.py`
- Role detection: `app/services/ai_role_detection.py`
- Emotional support service: `app/services/emotional_support_service.py`
- Frontend chat: `frontend/src/pages/EmotionalSupportChat.tsx`

### Completion Notes List

1. **Task 1 (AC #1)**: 情感陪伴角色识别和切换
   - 后端: `ai_role_detection.py` 已实现 emotional_keywords 检测
   - 角色切换通过 `determine_role_by_content()` 函数自动识别
   - 前端: `EmotionalSupportChat.tsx` 专用聊天界面已存在

2. **Task 2 (AC #2)**: 共情回应
   - `EmotionalSupportRole.provide_support()` 实现共情回应
   - 支持多种情绪类型: sad, anxious, frustrated, tired, default
   - 使用温和、支持性的语言模板

3. **Task 3 (AC #3)**: 压力管理建议
   - `EmotionalSupportRole.provide_support()` 包含压力管理建议
   - `emotional_support_service.py` 提供放松技巧库 (深呼吸、正念冥想等)
   - 前端显示建议内容

4. **Task 4 (AC #4)**: 积极心理暗示
   - `EmotionalSupportRole.daily_affirmation()` 提供每日肯定语
   - `emotional_support_service.py` 的 `get_positive_affirmations()` 支持个性化肯定语
   - 强调用户进步和努力

### Test Results

- 19 AI role integration tests: ALL PASSED
- Emotional support specific tests: 3 tests PASSED
- 角色识别测试: PASSED
- 关键词检测测试: PASSED

### File List

**Backend (已存在，无新增文件):**
- `app/services/ai_service.py` - 已支持 emotional_support 角色
- `app/services/ai_role_services.py` - EmotionalSupportRole 类已实现
- `app/services/ai_role_detection.py` - emotional_keywords 关键词检测
- `app/services/emotional_support_service.py` - 完整情感支持服务

**Frontend (已存在):**
- `frontend/src/pages/EmotionalSupportChat.tsx` - 情感陪伴聊天界面

**Tests:**
- `tests/test_ai_role_integration.py` - 已包含情感支持测试 (19 tests)
