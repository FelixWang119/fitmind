# Story 1.5: 防反感设计

**Epic**: 1 - 个人档案扩展与 Onboarding 优化  
**Story ID**: 1.5  
**Story Key**: `1-5-anti-annoyance-design`  
**优先级**: P2 (进阶功能)  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 在档案设置中体验友好的引导  
**以便** 我不会感到被强迫或厌烦  

---

## ✅ 验收标准 (BDD 格式)

### AC 1.1: 进度条和鼓励文案

**Given** 用户进行 Onboarding  
**When** 每步完成时  
**Then** 显示:
- 进度条 (实时显示完成度)
- 鼓励文案 ("太棒了！"、"继续加油！")
- 已完成步骤的视觉反馈

### AC 1.2: 跳过功能明显

**Given** 用户在选填步骤 (Step 4 健康信息)  
**When** 用户想要跳过  
**Then** "跳过"按钮明显可见  
**And** 明确告知"可以不填"

### AC 1.3: 重要性提示友好

**Given** 用户看到必填字段  
**When** 用户犹豫是否填写  
**Then** 显示重要性提示  
**And** 语气温和而非强迫

### AC 1.4: 错误提示友好

**Given** 用户输入无效数据  
**When** 提交表单  
**Then** 显示友好的错误提示  
**And** 提供修正建议

### AC 1.5: 支持中途保存退出

**Given** 用户中途想要离开  
**When** 用户关闭页面或点击退出  
**Then** 自动保存已填数据  
**And** 提示"下次可以继续"

---

## 🏗️ 技术需求

### 鼓励文案库

```typescript
const encouragementMessages = [
  "太棒了！继续加油！💪",
  "进展顺利！你已经完成了一半！🎉",
  "做得很好！每一步都是进步！✨",
  "马上完成了！坚持就是胜利！🏆",
  "非常棒！你的健康旅程开始了！🚀",
];

const stepSpecificEncouragement = {
  1: "好的开始是成功的一半！",
  2: "目标明确，成功在望！",
  3: "生活习惯决定健康质量！",
  4: " optional 选填项，了解更全面！",
  5: "恭喜你完成了所有步骤！🎊",
};
```

### 友好错误提示

```typescript
// 不友好的错误提示
❌ "Invalid input"
❌ "Validation failed"

// 友好的错误提示
✅ "这个数值好像不太对哦，请检查后重新输入"
✅ "体重应该在 20-300kg 之间，您输入的是多少呢？"
✅ "别担心，我们帮您检查了一下：年龄必须在 0-120 岁之间"
```

### 自动保存机制

```typescript
// 使用 localStorage 自动保存
useEffect(() => {
  const saved = localStorage.getItem('onboarding_data');
  if (saved) {
    setFormData(JSON.parse(saved));
  }
}, []);

useEffect(() => {
  localStorage.setItem('onboarding_data', JSON.stringify(formData));
}, [formData]);

// 页面关闭前提醒
useEffect(() => {
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (currentStep > 0 && currentStep < 5) {
      e.preventDefault();
      e.returnValue = '您的进度已自动保存，下次可以继续';
    }
  };
  window.addEventListener('beforeunload', handleBeforeUnload);
  return () => window.removeEventListener('beforeunload', handleBeforeUnload);
}, [currentStep]);
```

---

## 📋 架构合规要求

### UI/UX 设计原则

**来源**: Story 1.4 Onboarding 设计

1. **友好**: 鼓励性文案，避免强迫感
2. **透明**: 明确标注必填/选填
3. **宽容**: 允许跳过和保存退出
4. **渐进**: 逐步引导，避免信息过载

### 本地存储

**来源**: [project-context.md#前端技术栈](file:///Users/felix/bmad/_bmad_out/project-context-weight-ai.md#技术架构)

- 使用 `localStorage` 保存临时数据
- 数据格式：JSON
- 清理策略：完成后 7 天自动清理

---

## 🧪 测试要求

### 组件测试

**文件位置**: `frontend/src/pages/__tests__/Onboarding.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import Onboarding from '../Onboarding';

describe('Anti-Annoyance Features', () => {
  test('shows encouragement message after completing step', () => {
    render(<Onboarding />);
    fireEvent.click(screen.getByText(/开始/i));
    
    // Should show encouragement
    expect(screen.getByText(/太棒了/i)).toBeInTheDocument();
  });

  test('skip button is visible on optional step', () => {
    render(<Onboarding />);
    // Navigate to Step 4 (optional)
    // ... navigate through steps
    
    // Should see skip button
    expect(screen.getByText(/跳过/i)).toBeInTheDocument();
  });

  test('shows friendly error message', () => {
    render(<Onboarding />);
    fireEvent.click(screen.getByText(/开始/i));
    
    // Enter invalid age
    fireEvent.change(screen.getByLabelText(/年龄/i), {
      target: { value: '150' }
    });
    
    // Should show friendly error
    expect(screen.getByText(/年龄必须在/i)).toBeInTheDocument();
  });

  test('auto-saves progress', () => {
    render(<Onboarding />);
    fireEvent.click(screen.getByText(/开始/i));
    
    // Fill in data
    fireEvent.change(screen.getByLabelText(/年龄/i), {
      target: { value: '30' }
    });
    
    // Check localStorage
    const saved = localStorage.getItem('onboarding_data');
    expect(saved).toContain('30');
  });
});
```

---

## 📁 文件结构要求

### 需要修改/创建的文件

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `frontend/src/components/Onboarding/Onboarding.tsx` | 修改 | 添加防反感功能 |
| `frontend/src/components/Onboarding/utils/encouragement.ts` | 创建 | 鼓励文案库 |
| `frontend/src/components/Onboarding/utils/autoSave.ts` | 创建 | 自动保存工具 |
| `frontend/src/components/Onboarding/utils/friendlyErrors.ts` | 创建 | 友好错误提示 |
| `frontend/src/pages/__tests__/Onboarding.test.tsx` | 修改 | 添加防反感测试 |

---

## 📊 Story 完成状态

**状态**: ready-for-dev  
**创建日期**: 2026-02-27  
**最后更新**: 2026-02-27  
**创建者**: BMad Scrum Master Agent  

**完成标准**:
- [ ] 鼓励文案系统
- [ ] 跳过功能明显
- [ ] 友好错误提示
- [ ] 自动保存机制
- [ ] beforeunload 提醒
- [ ] 组件测试通过

---

## 💡 Dev Agent 实现指南

### 实现步骤建议

1. **Step 1**: 创建工具函数
   - encouragement.ts (鼓励文案)
   - friendlyErrors.ts (友好错误)
   - autoSave.ts (自动保存)

2. **Step 2**: 集成到 Onboarding 组件
   - 添加鼓励文案显示
   - 添加自动保存
   - 优化错误提示

3. **Step 3**: 测试
   - 单元测试
   - 手动测试用户体验

4. **Step 4**: 优化
   - 调整文案语气
   - 优化保存频率

---

**Story 文件已就绪，可以开始开发！** 🚀
