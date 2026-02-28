/**
 * 鼓励文案库
 * 用于 Onboarding 流程中的正向激励
 */

// 通用鼓励文案
export const encouragementMessages = [
  "太棒了！继续加油！💪",
  "进展顺利！你已经完成了一半！🎉",
  "做得很好！每一步都是进步！✨",
  "马上完成了！坚持就是胜利！🏆",
  "非常棒！你的健康旅程开始了！🚀",
];


// P1-6: 鼓励文案配置 (支持未来国际化)
export const encouragementConfig = {
  zh: {  // 中文
    step0: "让我们开始这段健康旅程吧！",
    step1: "好的开始是成功的一半！",
    step2: "目标明确，成功在望！",
    step3: "生活习惯决定健康质量！",
    step4: "选填项，了解更全面！",
    step5: "恭喜你完成了所有步骤！🎊",
  },
  en: {  // English (未来支持)
    step0: "Let's start your health journey!",
    step1: "A good start is half the battle!",
    step2: "Clear goals, clear success!",
    step3: "Lifestyle determines health!",
    step4: "Optional, but more info helps!",
    step5: "Congratulations! You completed all steps! 🎊",
  }
};

export const getCurrentLang = (): string => {
  // 检测浏览器语言
  if (typeof navigator !== 'undefined') {
    return navigator.language.startsWith('zh') ? 'zh' : 'en';
  }
  return 'zh';
};

// 步骤特定的鼓励文案
export const stepSpecificEncouragement = {
  0: "欢迎开启健康之旅！",
  1: "好的开始是成功的一半！",
  2: "目标明确，成功在望！",
  3: "生活习惯决定健康质量！",
  4: " optional 选填项，了解更全面！",
  5: "恭喜你完成了所有步骤！🎊",
};

// 根据步骤获取鼓励文案
export const getEncouragement = (step: number): string => {
  if (step === 0) {
    return "让我们开始这段健康旅程吧！";
  }
  
  if (step >= 1 && step <= 5) {
    return stepSpecificEncouragement[step as keyof typeof stepSpecificEncouragement];
  }
  
  // 随机选择一个通用鼓励
  const randomIndex = Math.floor(Math.random() * encouragementMessages.length);
  return encouragementMessages[randomIndex];
};

// 完成特定步骤后的鼓励
export const getCompletionEncouragement = (step: number): string => {
  const messages: Record<number, string> = {
    1: "基本信息完成！我们更了解你了！✨",
    2: "目标设定完成！成功的第一步！🎯",
    3: "生活方式完成！健康从习惯开始！💪",
    4: "健康信息完成！更全面的健康管理！❤️",
  };
  
  return messages[step] || "太棒了！继续前进！🚀";
};
