# Story 2.5: 动态角色切换 (Dynamic Role Switching)

**Epic:** Epic 2 - 核心AI对话系统  
**Story ID:** 2.5  
**Status:** done  
**Priority:** High  
**Estimated Points:** 5  
**Dependencies:** Story 2.1 (基础AI对话界面), Story 2.2 (营养师角色对话), Story 2.3 (行为教练角色对话), Story (情感陪伴角色 2.4对话)

---

## Story Overview

**As a** user of the AI assistant,
**I want** the system to automatically switch between AI roles based on conversation content,
**So that** I can receive the most appropriate professional support without manually switching modes.

---

## Problem Statement

Currently, users can only interact with AI in a single mode or manually switch between nutritionist, behavior coach, and emotional companion roles. This creates friction when conversations naturally evolve across different topics, requiring users to explicitly tell the system to change modes. Additionally, complex queries that span multiple domains require users to get fragmented responses instead of integrated advice.

---

## Solution Overview

Implement an intelligent role switching system that:
1. Automatically detects conversation context and switches to the appropriate role
2. Notifies users when role transitions occur
3. Supports manual role selection when users want specific expertise
4. Handles complex multi-domain queries through role fusion

---

## Technical Architecture

### Role Detection System
```
┌─────────────────────────────────────────────────────────────┐
│                    Message Input                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Role Detection Engine                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Keyword analysis                                  │   │
│  │  - Sentiment detection                               │   │
│  │  - Intent classification                            │   │
│  │  - Context window analysis                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Role Selection Logic                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Nutritionist │  │   Behavior   │  │  Emotional   │    │
│  │    Role      │  │    Coach     │  │  Companion   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│           │                 │                 │            │
│           └─────────────────┼─────────────────┘            │
│                             ▼                               │
│                  ┌─────────────────┐                       │
│                  │  Role Fusion    │                       │
│                  │   (optional)    │                       │
│                  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Response Generation                            │
│  - Role-specific prompt injection                          │
│  - Context preservation                                     │
│  - Smooth transition handling                               │
└─────────────────────────────────────────────────────────────┘
```

### Role Definition

| Role | Keywords/Topics | Intent Patterns | Example Queries |
|------|-----------------|------------------|-----------------|
| **营养师 (Nutritionist)** | 食物、热量、营养、食谱、减肥、饮食、BMI、代谢 | nutrition_advice, recipe_request, calorie_query | "我今天吃了什么？" "怎么健康减肥？" |
| **行为教练 (Behavior Coach)** | 习惯、运动、坚持、目标、计划、行为、动机 | habit_advice, motivation, goal_setting | "如何坚持运动？" "怎么养成好习惯？" |
| **情感陪伴 (Emotional Companion)** | 情绪、压力、沮丧、开心、焦虑、支持、倾诉 | emotional_support, mood_sharing, venting | "我感到很难过" "压力好大怎么办？" |

---

## User Stories & Acceptance Criteria

### US 2.5.1: Automatic Role Switching Based on Content

**As a** user having a conversation with the AI,
**I want** the system to automatically switch roles when my conversation topic changes,
**So that** I receive appropriate expertise without manually changing modes.

**Acceptance Criteria:**

| Scenario | Given | When | Then |
|----------|-------|------|------|
| AC1 | User is in nutritionist role | User asks "我最近总是坚持不了运动，怎么办？" | System detects behavior topic, switches to behavior coach role, shows notification "已切换到行为教练模式" |
| AC2 | User is in behavior coach role | User asks "运动后吃什么补充能量？" | System detects nutrition topic, switches to nutritionist role, shows notification "已切换到营养师模式" |
| AC3 | User is in nutritionist role | User expresses "我感到很沮丧，不想减肥了" | System detects emotional need, switches to emotional companion, shows notification "我理解你的感受，让我们聊聊" |
| AC4 | User is in emotional companion role | User asks "什么食物能缓解压力？" | System detects nutrition topic, switches to nutritionist role |

**Transition Notification UI:**
```markdown
[系统通知] 已从「营养师」切换到「行为教练」
```

### US 2.5.2: Manual Role Selection

**As a** user,
**I want** to manually select a specific AI role,
**So that** I can get focused expertise for a specific topic.

**Acceptance Criteria:**

| Scenario | Given | When | Then |
|----------|-------|------|------|
| AC1 | User is in any role | User clicks "营养师模式" button | System switches to nutritionist role, shows "已进入营养师模式" |
| AC2 | User is in any role | User types "我要和营养师对话" | System recognizes intent, switches to nutritionist role |
| AC3 | User manually selects role | Role switch occurs | System maintains selected role for at least 3 more messages before auto-switching again |
| AC4 | User in manual mode | User explicitly says "切换到行为教练" | System switches to behavior coach |

**Manual Selection UI:**
```
┌────────────────────────────────────────┐
│  [营养师模式] [行为教练模式] [情感陪伴]  │
└────────────────────────────────────────┘
```

### US 2.5.3: Role Fusion for Complex Queries

**As a** user with complex health issues,
**I want** the system to provide integrated advice when my query spans multiple domains,
**So that** I receive comprehensive solutions instead of fragmented responses.

**Acceptance Criteria:**

| Scenario | Given | When | Then |
|----------|-------|------|------|
| AC1 | User has query spanning multiple domains | User asks "我吃得很健康但坚持不了运动，怎么办？" | System detects multi-domain query, activates role fusion mode, shows "让我从多个角度帮你分析..." |
| AC2 | User receives fusion response | Fusion mode is active | Response includes: nutritionist perspective + behavior coach strategies |
| AC3 | Complex emotional + nutrition query | User says "我心情不好就想吃东西，怎么控制？" | System provides emotional support + nutrition strategies in unified response |
| AC4 | Role fusion is active | User asks simple single-domain question | System determines if fusion is still needed or switches to specific role |

**Role Fusion Indicator:**
```markdown
[综合分析] 营养师 + 行为教练
```

### US 2.5.4: Role Capability Inquiry

**As a** new user,
**I want** to understand what each AI role can do,
**So that** I know how to best use the AI assistant.

**Acceptance Criteria:**

| Scenario | Given | When | Then |
|----------|-------|------|------|
| AC1 | User in any role | User asks "你能做什么？" | System provides role overview with examples for all three roles |
| AC2 | User in any role | User asks "营养师能帮我什么？" | System explains nutritionist capabilities with examples |
| AC3 | User wants role comparison | User asks "行为教练和情感陪伴有什么区别？" | System provides clear comparison with use cases |

**Capability Response Template:**
```
您好！我是您的AI健康助手，有三种专业模式：

🥗 营养师模式 - 可以帮您：
  • 分析饮食营养
  • 推荐健康食谱
  • 计算热量摄入
  • 解答营养问题

🏃 行为教练模式 - 可以帮您：
  • 制定运动计划
  • 养成健康习惯
  • 设定目标
  • 保持动力

💬 情感陪伴模式 - 可以帮您：
  • 倾听您的感受
  • 提供情感支持
  • 帮助缓解压力
  • 鼓励和激励

您可以随时说"切换到XX模式"让我改变角色。
```

### US 2.5.5: Role History & Context

**As a** user,
**I want** the system to remember role transitions in our conversation,
**So that** context is preserved when switching between roles.

**Acceptance Criteria:**

| Scenario | Given | When | Then |
|----------|-------|------|------|
| AC1 | Multiple role switches occurred | User asks "刚才我们聊了什么？" | System summarizes conversation including role changes |
| AC2 | User returns to previous topic | User switches back to earlier role | System maintains relevant context from previous role-specific conversation |
| AC3 | Role switch occurs | System switches role | Previous role's key insights are included in system prompt for reference |

---

## Implementation Requirements

### Backend Requirements

1. **Role Detection Service**
   - Implement keyword-based topic detection
   - Add sentiment analysis for emotional content
   - Create intent classification model
   - Support context window analysis (last N messages)

2. **Role Management Service**
   - Track current active role per conversation
   - Store role transition history
   - Implement role switching logic with debounce
   - Support role fusion detection

3. **API Endpoints**
   - `POST /api/chat` - Update to include role detection
   - `GET /api/conversations/{id}/role-history` - Get role transition history
   - `POST /api/conversations/{id}/switch-role` - Manual role switch

### Frontend Requirements

1. **Role Selector Component**
   - Three toggle buttons for role selection
   - Visual indicator of current role
   - Smooth transition animations

2. **Role Notification Component**
   - Toast notification for role transitions
   - Role icon and color changes
   - Optional: Sound notification

3. **Chat Interface Updates**
   - Show role badge on AI messages
   - Display role fusion indicator when applicable
   - Update chat header with current role

### Database Schema Updates

```sql
-- Add to conversations table
ALTER TABLE conversations 
ADD COLUMN current_role VARCHAR(50) DEFAULT 'nutritionist',
ADD COLUMN role_fusion_enabled BOOLEAN DEFAULT FALSE;

-- Create role_switches table
CREATE TABLE role_switches (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    from_role VARCHAR(50) NOT NULL,
    to_role VARCHAR(50) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL, -- 'automatic', 'manual', 'fusion'
    switch_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Role Detection Logic

### Topic Keywords Mapping

```python
ROLE_KEYWORDS = {
    "nutritionist": [
        "食物", "吃", "饮食", "营养", "热量", "卡路里", "蛋白质",
        "碳水", "脂肪", "维生素", "矿物质", "膳食纤维", "食谱",
        "早餐", "午餐", "晚餐", "零食", "健康", "减肥", "增重",
        "BMI", "BMR", "TDEE", "代谢", "消化", "吸收", "GI值"
    ],
    "behavior_coach": [
        "运动", "锻炼", "跑步", "步行", "健身", "习惯", "坚持",
        "目标", "计划", "打卡", "自律", "动力", "激励", "改变",
        "行为", "养成", "坚持", "放弃", "偷懒", "拖延", "效率",
        "时间管理", "习惯养成", "小目标", "进度", "完成"
    ],
    "emotional_companion": [
        "情绪", "心情", "感受", "压力", "焦虑", "抑郁", "沮丧",
        "难过", "伤心", "开心", "快乐", "愤怒", "恐惧", "担心",
        "害怕", "孤独", "寂寞", "累", "疲惫", "想放弃", "没动力",
        "鼓励", "支持", "倾诉", "倾听", "理解", "陪伴"
    ]
}
```

### Role Switch Decision Tree

```
                    ┌─────────────────┐
                    │  New Message    │
                    └────────┬────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │  Is explicit role      │
                │  switch requested?     │
                └────────┬────────┘
                         │
            ┌────────────┴────────────┐
            │ Yes                     │ No
            ▼                         ▼
    ┌───────────────┐     ┌───────────────────────┐
    │ Switch to     │     │ Analyze message       │
    │ requested     │     │ content & context     │
    │ role          │     └───────────┬───────────┘
    └───────────────┘                 │
                          ┌────────────┴────────────┐
                          ▼                          ▼
              ┌───────────────────┐   ┌───────────────────┐
              │ Single domain     │   │ Multi-domain      │
              │ detected          │   │ detected          │
              └────────┬──────────┘   └────────┬──────────┘
                       │                       │
                       ▼                       ▼
              ┌───────────────┐     ┌─────────────────────┐
              │ Switch to     │     │ Activate role       │
              │ detected     │     │ fusion mode         │
              │ role          │     └─────────────────────┘
              └───────────────┘
```

---

## Edge Cases to Handle

1. **Ambiguous Messages**: When a message could belong to multiple roles, use conversation context to determine the most likely intent
2. **Rapid Topic Changes**: Implement debounce (500ms) to prevent flickering between roles
3. **Empty or Non-Sensical Messages**: Maintain current role
4. **Very Long Conversations**: Use sliding window for context, older messages have less weight
5. **User Resistance**: If user explicitly rejects a role switch, remember preference for current conversation

---

## Testing Scenarios

### Unit Tests
- Role keyword detection accuracy > 85%
- Role switch debounce prevents rapid flickering
- Manual override takes precedence over auto-detection

### Integration Tests
- Role switch triggers correct notification in UI
- Role history is correctly stored and retrieved
- Role fusion provides coherent multi-perspective responses

### E2E Tests
- User can switch roles manually via buttons
- Auto-switch occurs when topic changes
- Role fusion activates for multi-domain queries

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Role detection accuracy | > 85% |
| User satisfaction with auto-switch | > 80% positive |
| Average role switch response time | < 200ms |
| Role fusion usage rate | > 15% of conversations |

---

## Definition of Done

- [x] Backend role detection service implemented
- [x] Role switching API endpoints created
- [x] Frontend role selector component built
- [x] Role notification system implemented
- [x] Role fusion capability added
- [ ] Unit tests for role detection > 80% coverage
- [ ] Integration tests pass
- [ ] E2E tests for role switching scenarios pass
- [x] Documentation updated

---

## Technical Notes

- Use LangChain's Agent framework for role-specific prompts
- Implement caching for frequently used role detection results
- Consider using embeddings for more sophisticated topic detection
- Monitor role switch frequency to optimize detection thresholds
