# Story 1.4: Onboarding 引导流程 UI/UX

**Epic**: 1 - 个人档案扩展与 Onboarding 优化  
**Story ID**: 1.4  
**Story Key**: `1-4-onboarding-ui-ux`  
**优先级**: P2 (进阶功能)  
**故事点数**: 13 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 新用户  
**我想要** 通过 5 步 Onboarding 引导流程设置档案  
**以便** 我能轻松完成个人信息设置  

---

## ✅ 验收标准 (BDD 格式)

### AC 1.1: 5 步引导流程完整

**Given** 用户首次注册  
**When** 进入 Onboarding 流程  
**Then** 显示 5 步引导:
- Step 0: 欢迎与价值说明 (30 秒)
- Step 1: 基本信息 (1 分钟)
- Step 2: 目标设定 (2 分钟)
- Step 3: 生活方式 (1 分钟)
- Step 4: 健康信息 (1 分钟，选填)
- Step 5: 动机与完成 (1 分钟)

### AC 1.2: 进度条实时显示

**Given** 用户进行 Onboarding  
**When** 每步完成时  
**Then** 显示:
- 进度条 (实时显示完成度)
- 步骤指示器 (Step 1/5, 2/5...)
- 鼓励文案
- 重要性提示

### AC 1.3: 支持跳过和保存

**Given** 用户中途退出  
**When** 用户离开引导流程  
**Then** 保存已填数据  
**And** 支持后续继续  

### AC 1.4: 字段验证友好

**Given** 用户输入无效数据  
**When** 提交表单  
**Then** 显示友好的错误提示  
**And** 高亮问题字段  

### AC 1.5: 完成庆祝

**Given** 用户完成所有步骤  
**When** 提交最后一步  
**Then** 显示庆祝动画  
**And** 自动跳转到主页  

---

## 🏗️ 技术需求

### 前端组件结构

**文件位置**: `frontend/src/pages/Onboarding.tsx`

**组件结构**:
```typescript
// 主组件
<OnboardingWizard>
  <ProgressBar current={step} total={5} />
  <StepIndicator steps={5} current={step} />
  
  <Step0>WelcomeStep</Step0>      // 欢迎页
  <Step1>BasicInfoStep</Step1>    // 基本信息
  <Step2>GoalSettingStep</Step2>  // 目标设定
  <Step3>LifestyleStep</Step3>    // 生活方式
  <Step4>HealthInfoStep</Step4>   // 健康信息
  <Step5>MotivationStep</Step5>   // 动机与完成
</OnboardingWizard>
```

### Step 0: 欢迎页

```typescript
interface WelcomeStepProps {
  onNext: () => void;
}

// 内容:
// - 欢迎标题
// - 价值说明 (3-4 个要点)
// - 预计时间提示
// - "开始" 按钮
```

### Step 1: 基本信息

```typescript
interface BasicInfoStepProps {
  data: UserProfile;
  onChange: (data: UserProfile) => void;
  onNext: () => void;
  onBack: () => void;
}

// 字段:
// - age (数字输入)
// - gender (选择：男/女/其他)
// - height (数字输入，单位：cm)
// - initial_weight (数字输入，单位：kg)
// - target_weight (数字输入，单位：kg)
// 验证：实时显示 AI 推荐范围
```

### Step 2: 目标设定

```typescript
interface GoalSettingStepProps {
  // 字段:
  // - health_target_type (选择：减重/增肌/维持)
  // - target_weight (从 Step 1 继承)
  // - weekly_goal (数字：每周目标减重 kg)
  // - target_date (日期选择器)
  // 验证：AI 推荐健康范围
}
```

### Step 3: 生活方式

```typescript
interface LifestyleStepProps {
  // 字段:
  // - activity_level (选择：sedentary/light/moderate/active/very_active)
  // - sleep_quality (滑动条 1-10)
  // - dietary_preferences (多选：vegetarian/vegan/low-carb/etc)
  // - exercise_habits (选择：从不/偶尔/经常)
}
```

### Step 4: 健康信息 (选填)

```typescript
interface HealthInfoStepProps {
  // 字段 (全部选填):
  // - current_weight (数字，kg)
  // - waist_circumference (数字，cm)
  // - hip_circumference (数字，cm)
  // - body_fat_percentage (数字，%)
  // - muscle_mass (数字，kg)
  // - health_conditions (JSON，多选 + 自定义)
  // - allergies (文本数组)
  // - medications (JSON，文本输入)
  // 提示：明确标注"可以不填"
}
```

### Step 5: 动机与完成

```typescript
interface MotivationStepProps {
  // 字段:
  // - motivation_type (选择：健康/外貌/运动/其他)
  // - motivation_detail (文本输入，可选)
  // 完成后:
  // - 庆祝动画
  // - "开始旅程" 按钮 → 跳转到主页
}
```

---

## 📋 架构合规要求

### API 集成

**来源**: Story 1.3 API 端点更新

```typescript
// API 调用
PUT /api/v1/users/profile
Body: UserProfile (17 字段)

// 响应
{
  "id": 1,
  "email": "user@example.com",
  "age": 30,
  "current_weight": 70000,  // 克
  // ... 所有字段
}
```

### 单位转换

**来源**: [project-context.md#CRITICAL-重量单位约定](file:///Users/felix/bmad/_bmad_out/project-context-weight-ai.md#关键注意事项)

```typescript
// 前端输入：kg
const weightKg = 70;

// API 传输：g
const weightG = weightKg * 1000;  // 70000

// 后端响应：g → 前端展示：kg
const displayWeight = response.current_weight / 1000;  // 70
```

### UI 组件库

**来源**: [project-context.md#前端技术栈](file:///Users/felix/bmad/_bmad_out/project-context-weight-ai.md#技术架构)

- **UI 库**: Ant Design ^6.3.1
- **样式**: TailwindCSS ^3.3.0
- **表单验证**: Ant Design Form validation
- **动画**: Ant Design + CSS animations

---

## 🎨 UI/UX 设计要求

### 整体风格

- **友好**: 鼓励性文案，避免强迫感
- **简洁**: 每步聚焦 2-4 个字段
- **进度可视化**: 清晰的进度条和步骤指示
- **响应式**: 支持手机/平板/桌面

### 防反感设计

**来源**: Story 1.5 需求

- ✅ 明确标注选填字段
- ✅ 提供"跳过"按钮
- ✅ 鼓励文案而非警告
- ✅ 进度条实时显示
- ✅ 支持中途保存退出

### 错误处理

```typescript
// 好的错误提示
❌ "Invalid input"
✅ "体重应该在 20-300kg 之间，请检查您的输入"

// 高亮问题字段
<Form.Item
  name="target_weight"
  rules={[{ required: true, message: '请设置目标体重' }]}
  validateStatus="error"
  help="目标体重应该在健康范围内 (50-150kg)"
>
```

### 庆祝动画

```typescript
// 完成时的动画
- Confetti 效果 (可选库：react-confetti)
- 成功图标 + 动画
- 鼓励文案："太棒了！让我们开始健康旅程吧！"
```

---

## 🧪 测试要求

### 前端组件测试

**文件位置**: `frontend/src/pages/__tests__/Onboarding.test.tsx`

**测试覆盖率**: > 60%

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import Onboarding from '../Onboarding';

describe('Onboarding Component', () => {
  test('renders welcome step initially', () => {
    render(<Onboarding />);
    expect(screen.getByText(/欢迎/i)).toBeInTheDocument();
  });

  test('progress bar updates correctly', async () => {
    render(<Onboarding />);
    // Step 0
    fireEvent.click(screen.getByText(/开始/i));
    // Should be on Step 1
    expect(screen.getByText(/基本信息/i)).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(<Onboarding />);
    fireEvent.click(screen.getByText(/开始/i));
    
    // Try to submit empty form
    fireEvent.click(screen.getByText(/下一步/i));
    
    // Should show validation error
    expect(screen.getByText(/必填/i)).toBeInTheDocument();
  });

  test('saves data between steps', async () => {
    render(<Onboarding />);
    fireEvent.click(screen.getByText(/开始/i));
    
    // Fill in age
    fireEvent.change(screen.getByLabelText(/年龄/i), {
      target: { value: '30' }
    });
    
    fireEvent.click(screen.getByText(/下一步/i));
    fireEvent.click(screen.getByText(/上一步/i));
    
    // Age should still be filled
    expect(screen.getByLabelText(/年龄/i)).toHaveValue('30');
  });

  test('skips optional fields', async () => {
    render(<Onboarding />);
    // Navigate to Step 4 (health info)
    // ... skip through steps
    fireEvent.click(screen.getByText(/跳过/i));
    
    // Should proceed to next step
    expect(screen.getByText(/动机/i)).toBeInTheDocument();
  });

  test('completes onboarding successfully', async () => {
    render(<Onboarding />);
    // Fill all required steps
    // ... fill data
    fireEvent.click(screen.getByText(/完成/i));
    
    // Should show celebration
    expect(screen.getByText(/太棒了/i)).toBeInTheDocument();
  });
});
```

---

## 📁 文件结构要求

### 需要创建/修改的文件

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `frontend/src/pages/Onboarding.tsx` | 创建 | Onboarding 主组件 |
| `frontend/src/components/Onboarding/ProgressBar.tsx` | 创建 | 进度条组件 |
| `frontend/src/components/Onboarding/StepIndicator.tsx` | 创建 | 步骤指示器 |
| `frontend/src/components/Onboarding/steps/WelcomeStep.tsx` | 创建 | 欢迎页 |
| `frontend/src/components/Onboarding/steps/BasicInfoStep.tsx` | 创建 | 基本信息 |
| `frontend/src/components/Onboarding/steps/GoalSettingStep.tsx` | 创建 | 目标设定 |
| `frontend/src/components/Onboarding/steps/LifestyleStep.tsx` | 创建 | 生活方式 |
| `frontend/src/components/Onboarding/steps/HealthInfoStep.tsx` | 创建 | 健康信息 |
| `frontend/src/components/Onboarding/steps/MotivationStep.tsx` | 创建 | 动机与完成 |
| `frontend/src/pages/__tests__/Onboarding.test.tsx` | 创建 | 组件测试 |

### 项目结构对齐

**来源**: [project-context.md#项目结构](file:///Users/felix/bmad/_bmad_out/project-context-weight-ai.md#项目结构)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Onboarding.tsx           # 创建：主组件
│   │   └── __tests__/
│   │       └── Onboarding.test.tsx  # 创建：测试
│   └── components/
│       └── Onboarding/
│           ├── ProgressBar.tsx      # 创建
│           ├── StepIndicator.tsx    # 创建
│           └── steps/
│               ├── WelcomeStep.tsx          # 创建
│               ├── BasicInfoStep.tsx        # 创建
│               ├── GoalSettingStep.tsx      # 创建
│               ├── LifestyleStep.tsx        # 创建
│               ├── HealthInfoStep.tsx       # 创建
│               └── MotivationStep.tsx       # 创建
```

---

## 📚 项目上下文参考

### 现有 User Schema

**来源**: Story 1.2 Schema 更新

```typescript
interface UserProfile {
  // 原有字段
  age?: number;
  gender?: string;
  height?: number;         // cm
  initial_weight?: number; // g
  target_weight?: number;  // g
  activity_level?: string;
  dietary_preferences?: string[];
  
  // 新增字段
  current_weight?: number;        // g
  waist_circumference?: number;   // cm
  hip_circumference?: number;     // cm
  body_fat_percentage?: number;   // %
  muscle_mass?: number;           // g
  bone_density?: number;          // g/cm²
  metabolism_rate?: number;       // kcal/day
  health_conditions?: Record<string, any>;
  medications?: Record<string, any>;
  allergies?: string[];
  sleep_quality?: number;         // 1-10
}
```

### API 客户端

**来源**: [frontend/src/api/client.ts](file:///Users/felix/bmad/frontend/src/api/client.ts)

```typescript
import api from '@/api/client';

// 更新档案
await api.put('/users/profile', profileData);

// 获取档案
const { data } = await api.get('/users/profile');
```

---

## 🎯 依赖关系

### 前置依赖

- ✅ Story 1.1: 数据库模型扩展 (已完成)
- ✅ Story 1.2: Schema 更新 (已完成)
- ✅ Story 1.3: API 端点更新 (已完成)

### 后续依赖

- → Story 1.5: 防反感设计 (本 Story 的部分功能)

---

## 📊 Story 完成状态

**状态**: ready-for-dev  
**创建日期**: 2026-02-27  
**最后更新**: 2026-02-27  
**创建者**: BMad Scrum Master Agent  

**完成标准**:
- [ ] 5 步引导流程完整实现
- [ ] 进度条和步骤指示器
- [ ] 支持跳过和保存
- [ ] 字段验证友好
- [ ] 完成庆祝动画
- [ ] 组件测试覆盖率 > 60%
- [ ] 响应式设计

---

## 💡 Dev Agent 实现指南

### 实现步骤建议

1. **Step 1**: 创建基础组件
   ```bash
   mkdir -p frontend/src/components/Onboarding/steps
   ```

2. **Step 2**: 实现主组件框架
   - OnboardingWizard 状态管理
   - 进度条组件
   - 步骤切换逻辑

3. **Step 3**: 实现各个 Step 组件
   - 从 WelcomeStep 开始
   - 依次实现 BasicInfo, GoalSetting, etc.

4. **Step 4**: API 集成
   - 保存数据到后端
   - 处理错误

5. **Step 5**: 测试
   ```bash
   cd frontend
   npm test -- Onboarding
   ```

6. **Step 6**: 优化和动画

### 常见陷阱提醒

⚠️ **避免以下错误**:
1. 忘记单位转换 (kg ↔ g) → 数据错误
2. 验证规则与后端不一致 → 提交失败
3. 未保存中间状态 → 数据丢失
4. 强制必填选填字段 → 用户反感
5. 忽略响应式设计 → 移动端体验差

---

## 🔍 验证清单

在标记为完成前，请确认:

- [ ] 5 个步骤都完整实现
- [ ] 进度条正确显示
- [ ] 跳过功能正常工作
- [ ] 数据保存正常
- [ ] 验证规则与后端一致
- [ ] 错误提示友好
- [ ] 庆祝动画流畅
- [ ] 响应式布局
- [ ] 组件测试通过
- [ ] 代码通过审查

---

**Story 文件已就绪，可以开始开发！** 🚀

**下一步**: 运行 `dev-story 1-4-onboarding-ui-ux` 开始实现
