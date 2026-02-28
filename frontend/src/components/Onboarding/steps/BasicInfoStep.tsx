import React, { useState } from 'react';
import { Form, InputNumber, Select, Typography, Alert, Space } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

interface BasicInfoStepProps {
  data: any;
  onChange: (data: any) => void;
  onNext: () => void;
  onBack: () => void;
}

/**
 * Step 1: 基本信息
 * 收集用户的基础身体数据
 */
const BasicInfoStep: React.FC<BasicInfoStepProps> = ({ 
  data, 
  onChange, 
  onNext, 
  onBack 
}) => {
  const [form] = Form.useForm();
  const [errors, setErrors] = useState<any>({});

  // 计算 BMI 和健康范围
  const calculateBMI = (height?: number, weight?: number) => {
    if (!height || !weight) return null;
    const heightM = height / 100;
    return weight / (heightM * heightM);
  };

  const getHealthyWeightRange = (height?: number) => {
    if (!height) return null;
    const heightM = height / 100;
    // BMI 18.5-24 为健康范围
    const minWeight = 18.5 * heightM * heightM;
    const maxWeight = 24 * heightM * heightM;
    return { min: Math.round(minWeight), max: Math.round(maxWeight) };
  };

  const handleValuesChange = (changedValues: any) => {
    const newData = { ...data, ...changedValues };
    onChange(newData);
    
    // 实时更新验证
    validateField(changedValues);
  };

  const validateField = (values: any) => {
    const newErrors: any = {};
    
    if (values.age !== undefined) {
      if (values.age < 0 || values.age > 120) {
        newErrors.age = '年龄必须在 0-120 岁之间';
      }
    }
    
    if (values.height !== undefined) {
      if (values.height < 50 || values.height > 250) {
        newErrors.height = '身高必须在 50-250cm 之间';
      }
    }
    
    // P1-3: 添加所有字段验证
    if (values.body_fat_percentage !== undefined && values.body_fat_percentage !== null) {
      if (values.body_fat_percentage < 3 || values.body_fat_percentage > 70) {
        newErrors.body_fat_percentage = '体脂率必须在 3-70% 之间';
      }
    }
    
    if (values.sleep_quality !== undefined && values.sleep_quality !== null) {
      if (values.sleep_quality < 1 || values.sleep_quality > 10) {
        newErrors.sleep_quality = '睡眠质量必须在 1-10 分之间';
      }
    }
    
    if (values.waist_circumference !== undefined && values.waist_circumference !== null) {
      if (values.waist_circumference < 50 || values.waist_circumference > 150) {
        newErrors.waist_circumference = '腰围必须在 50-150cm 之间';
      }
    }
    
    if (values.height !== undefined) {
      if (values.height < 50 || values.height > 250) {
        newErrors.height = '身高必须在 50-250cm 之间';
      }
    }
    
    if (values.initial_weight !== undefined) {
      if (values.initial_weight < 20 || values.initial_weight > 300) {
        newErrors.initial_weight = '体重必须在 20-300kg 之间';
      }
    }
    
    if (values.target_weight !== undefined) {
      if (values.target_weight < 20 || values.target_weight > 300) {
        newErrors.target_weight = '目标体重必须在 20-300kg 之间';
      }
      
      // 检查目标体重是否在健康范围
      const healthyRange = getHealthyWeightRange(form.getFieldValue('height'));
      if (healthyRange) {
        if (values.target_weight < healthyRange.min || values.target_weight > healthyRange.max) {
          newErrors.target_weight_warning = `健康范围：${healthyRange.min}-${healthyRange.max}kg`;
        }
      }
    }
    
    setErrors(newErrors);
  };

  const handleNext = () => {
    form.validateFields().then(() => {
      onNext();
    }).catch(() => {
      // 验证失败
    });
  };

  const healthyRange = getHealthyWeightRange(data.height);

  return (
    <div className="py-4">
      <Title level={3} className="mb-6">基本信息</Title>
      
      <Alert
        message="温馨提示"
        description="这些数据将用于为您计算健康目标和营养建议"
        type="info"
        showIcon
        icon={<InfoCircleOutlined />}
        className="mb-6"
      />

      <Form
        form={form}
        layout="vertical"
        initialValues={data}
        onValuesChange={handleValuesChange}
      >
        <Form.Item
          label="年龄"
          name="age"
          rules={[{ required: true, message: '请输入年龄' }]}
          validateStatus={errors.age ? 'error' : ''}
          help={errors.age}
        >
          <InputNumber 
            min={0} 
            max={120} 
            className="w-full" 
            placeholder="岁"
            addonAfter="岁"
          />
        </Form.Item>

        <Form.Item
          label="性别"
          name="gender"
          rules={[{ required: true, message: '请选择性别' }]}
        >
          <Select className="w-full" placeholder="请选择">
            <Option value="male">男</Option>
            <Option value="female">女</Option>
            <Option value="other">其他</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="身高"
          name="height"
          rules={[{ required: true, message: '请输入身高' }]}
          validateStatus={errors.height ? 'error' : ''}
          help={errors.height}
        >
          <InputNumber 
            min={50} 
            max={250} 
            className="w-full" 
            placeholder="cm"
            addonAfter="cm"
          />
        </Form.Item>

        <Form.Item
          label="当前体重"
          name="initial_weight"
          rules={[{ required: true, message: '请输入当前体重' }]}
          validateStatus={errors.initial_weight ? 'error' : ''}
          help={errors.initial_weight}
        >
          <InputNumber 
            min={20} 
            max={300} 
            className="w-full" 
            placeholder="kg"
            addonAfter="kg"
          />
        </Form.Item>

        <Form.Item
          label="目标体重"
          name="target_weight"
          rules={[{ required: true, message: '请输入目标体重' }]}
          validateStatus={errors.target_weight ? 'error' : ''}
          help={
            <Space direction="vertical" style={{ width: '100%' }}>
              {errors.target_weight}
              {errors.target_weight_warning && (
                <Text type="warning" className="text-xs">
                  ⚠️ {errors.target_weight_warning}
                </Text>
              )}
            </Space>
          }
        >
          <InputNumber 
            min={20} 
            max={300} 
            className="w-full" 
            placeholder="kg"
            addonAfter="kg"
          />
        </Form.Item>

        {data.height && data.initial_weight && (
          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            <Text strong>您的 BMI: </Text>
            <Text className="text-blue-600">
              {calculateBMI(data.height, data.initial_weight)?.toFixed(1)}
            </Text>
            {healthyRange && (
              <>
                <br />
                <Text>健康体重范围：</Text>
                <Text className="text-green-600">
                  {healthyRange.min} - {healthyRange.max} kg
                </Text>
              </>
            )}
          </div>
        )}
      </Form>

      <div className="flex justify-between mt-8">
        <button onClick={onBack} className="btn-secondary">
          上一步
        </button>
        <button onClick={handleNext} className="btn-primary">
          下一步
        </button>
      </div>
    </div>
  );
};

export default BasicInfoStep;
