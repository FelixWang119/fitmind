/**
 * 友好错误提示工具
 * 将技术性错误转换为用户友好的提示
 */

interface FieldError {
  field: string;
  message: string;
  suggestion?: string;
}

// 字段友好的错误提示
const fieldFriendlyMessages: Record<string, Record<string, FieldError>> = {
  age: {
    required: {
      field: 'age',
      message: '请告诉我们您的年龄',
      suggestion: '这是了解您健康状况的基础信息',
    },
    min: {
      field: 'age',
      message: '年龄最小为 0 岁',
      suggestion: '请检查输入的年龄是否正确',
    },
    max: {
      field: 'age',
      message: '年龄最大为 120 岁',
      suggestion: '请检查输入的年龄是否正确',
    },
  },
  height: {
    required: {
      field: 'height',
      message: '请告诉我们您的身高',
      suggestion: '身高用于计算健康指标',
    },
    min: {
      field: 'height',
      message: '身高最小为 50cm',
      suggestion: '请检查单位是否正确 (厘米)',
    },
    max: {
      field: 'height',
      message: '身高最大为 250cm',
      suggestion: '请检查单位是否正确 (厘米)',
    },
  },
  initial_weight: {
    required: {
      field: 'initial_weight',
      message: '请告诉我们您当前的体重',
      suggestion: '这是设定目标的基础',
    },
    min: {
      field: 'initial_weight',
      message: '体重最小为 20kg',
      suggestion: '请检查单位是否正确 (公斤)',
    },
    max: {
      field: 'initial_weight',
      message: '体重最大为 300kg',
      suggestion: '请检查单位是否正确 (公斤)',
    },
  },
  target_weight: {
    required: {
      field: 'target_weight',
      message: '请设定您的目标体重',
      suggestion: '目标会帮助您保持动力',
    },
    min: {
      field: 'target_weight',
      message: '目标体重最小为 20kg',
      suggestion: '请设定一个健康的 target',
    },
    max: {
      field: 'target_weight',
      message: '目标体重最大为 300kg',
      suggestion: '请设定一个健康的 target',
    },
    range: {
      field: 'target_weight',
      message: '目标体重可能不太合理',
      suggestion: '建议设定在健康范围内',
    },
  },
  sleep_quality: {
    min: {
      field: 'sleep_quality',
      message: '睡眠质量最低为 1 分',
      suggestion: '1 分表示睡眠质量很差',
    },
    max: {
      field: 'sleep_quality',
      message: '睡眠质量最高为 10 分',
      suggestion: '10 分表示睡眠质量非常好',
    },
  },
};

/**
 * 获取友好的错误提示
 * @param field 字段名
 * @param errorType 错误类型 (required, min, max, etc.)
 * @returns 友好的错误信息
 */
export const getFriendlyError = (field: string, errorType: string): FieldError | null => {
  const fieldErrors = fieldFriendlyMessages[field];
  
  if (!fieldErrors) {
    return {
      field,
      message: '这个输入好像不太对',
      suggestion: '请检查后重新输入',
    };
  }
  
  return fieldErrors[errorType] || {
    field,
    message: `${field} 的输入有问题`,
    suggestion: '请检查后重新输入',
  };
};

/**
 * 验证错误并返回友好的提示
 * @param values 表单值
 * @returns 错误列表
 */
export const validateWithFriendlyMessages = (values: any): FieldError[] => {
  const errors: FieldError[] = [];
  
  // 年龄验证
  if (values.age !== undefined) {
    if (values.age < 0) {
      errors.push(getFriendlyError('age', 'min')!);
    } else if (values.age > 120) {
      errors.push(getFriendlyError('age', 'max')!);
    }
  }
  
  // 身高验证
  if (values.height !== undefined) {
    if (values.height < 50) {
      errors.push(getFriendlyError('height', 'min')!);
    } else if (values.height > 250) {
      errors.push(getFriendlyError('height', 'max')!);
    }
  }
  
  // 体重验证
  if (values.initial_weight !== undefined) {
    if (values.initial_weight < 20) {
      errors.push(getFriendlyError('initial_weight', 'min')!);
    } else if (values.initial_weight > 300) {
      errors.push(getFriendlyError('initial_weight', 'max')!);
    }
  }
  
  // 目标体重验证
  if (values.target_weight !== undefined) {
    if (values.target_weight < 20) {
      errors.push(getFriendlyError('target_weight', 'min')!);
    } else if (values.target_weight > 300) {
      errors.push(getFriendlyError('target_weight', 'max')!);
    }
  }
  
  // 睡眠质量验证
  if (values.sleep_quality !== undefined) {
    if (values.sleep_quality < 1) {
      errors.push(getFriendlyError('sleep_quality', 'min')!);
    } else if (values.sleep_quality > 10) {
      errors.push(getFriendlyError('sleep_quality', 'max')!);
    }
  }
  
  return errors;
};
