# 基础设施快速参考指南

## 概述

本文档提供三个核心基础设施系统的快速参考：
1. **Qwen API配置系统** - 集中管理文本和视觉模型配置
2. **测试资源管理系统** - 集中管理测试图像等资源
3. **测试用户管理系统** - 避免测试中重复注册用户

## 1. Qwen API配置系统

### 导入和使用

```python
from app.core.qwen_config import qwen_config

# 获取配置实例
config = qwen_config

# 验证配置
validation = config.validate_configuration()
print(f"状态: {validation['status']}")
```

### 模型选择

```python
# 文本对话模型
chat_model = qwen_config.QWEN_CHAT_MODEL          # qwen-plus
chat_timeout = qwen_config.CHAT_TIMEOUT           # 30.0秒
chat_temp = qwen_config.CHAT_TEMPERATURE          # 0.7

# 图片识别模型
vision_model = qwen_config.QWEN_VISION_MODEL      # qwen-vl-max
vision_timeout = qwen_config.VISION_TIMEOUT       # 60.0秒
vision_temp = qwen_config.VISION_TEMPERATURE      # 0.3

# 快速响应模型
turbo_model = qwen_config.QWEN_TURBO_MODEL        # qwen-turbo
```

### 智能选择方法

```python
# 根据用途选择模型
model = qwen_config.get_model_for_purpose("chat")     # qwen-plus
model = qwen_config.get_model_for_purpose("vision")   # qwen-vl-max
model = qwen_config.get_model_for_purpose("turbo")    # qwen-turbo

# 根据模型获取超时
timeout = qwen_config.get_timeout_for_model("qwen-vl-max")    # 60.0
timeout = qwen_config.get_timeout_for_model("qwen-plus")      # 30.0

# 根据模型获取温度
temp = qwen_config.get_temperature_for_model("qwen-vl-max")   # 0.3
temp = qwen_config.get_temperature_for_model("qwen-plus")     # 0.7
```

### API调用

```python
# 获取headers
headers = qwen_config.get_headers()
# {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}

# 获取API URL
url = qwen_config.QWEN_API_URL
# https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
```

## 2. 测试资源管理系统

### 导入和使用

```python
from app.core.test_resources import TestResources
from app.core.test_resources import get_test_image_base64, list_test_images

# 使用类方法
image_path = TestResources.get_image_path("lunch")
image_base64 = TestResources.encode_image_to_base64("lunch")
images = TestResources.list_available_images()

# 使用便利函数
image_base64 = get_test_image_base64("lunch")  # 默认使用"lunch"
images = list_test_images()
```

### 可用测试图像

| 名称 | 文件 | 描述 | 大小 |
|------|------|------|------|
| lunch | lunch.jpg | Sample lunch meal image | ~158KB |
| meal3 | meal3.png | Sample meal image 3 | ~287KB |
| meal4 | meal4.jpg | Sample meal image 4 | ~?KB |
| meal5 | meal5.jpg | Sample meal image 5 | ~?KB |
| meal6 | meal6.jpg | Sample meal image 6 | ~?KB |

### 验证和报告

```python
# 验证所有测试资源
validation = TestResources.validate_test_resources()
print(f"状态: {validation['status']}")

# 生成人类可读报告
report = TestResources.generate_resource_report()
print(report)
```

## 3. 测试用户管理系统

### 导入和使用

```python
from app.core.test_users import test_user_manager
from app.core.test_users import get_test_user, get_test_token

# 使用管理器实例
user_data = test_user_manager.get_or_create_test_user(db, "nutrition")
token = test_user_manager.get_test_user_token(db, "nutrition")
user_with_token = test_user_manager.get_test_user_with_token(db, "nutrition")

# 使用便利函数
user_data = get_test_user(db, "default")  # 默认使用"default"目的
token = get_test_token(db, "default")
```

### 预定义测试用户

| 目的 | 邮箱 | 用户名 | 密码 | 描述 |
|------|------|--------|------|------|
| default | test.user@example.com | testuser | TestPassword123! | 默认测试用户 |
| nutrition | nutrition.test@example.com | nutritiontest | NutritionTest123! | 营养分析测试 |
| habit | habit.test@example.com | habittest | HabitTest123! | 习惯跟踪测试 |
| admin | admin.test@example.com | admintest | AdminTest123! | 管理员功能测试 |

### 验证和清理

```python
# 验证所有测试用户
validation = test_user_manager.validate_test_users(db)
print(f"状态: {validation['status']}")

# 列出所有测试用户状态
users = test_user_manager.list_test_users(db)
for user in users:
    print(f"{user['purpose']}: {user['email']}")

# 清理测试用户（可选）
results = test_user_manager.cleanup_test_users(db, keep_users=True)
print(f"清理结果: {results}")
```

## 4. 基础设施验证

### 运行完整验证

```bash
cd /Users/felix/bmad
python validate_infrastructure.py
```

### 单独验证

```python
# 验证Qwen配置
from app.core.qwen_config import qwen_config
validation = qwen_config.validate_configuration()

# 验证测试资源
from app.core.test_resources import TestResources
validation = TestResources.validate_test_resources()

# 验证测试用户
from app.core.test_users import test_user_manager
from app.core.database import SessionLocal
db = SessionLocal()
validation = test_user_manager.validate_test_users(db)
db.close()
```

## 5. 环境配置

### .env文件配置

```bash
# Qwen API配置
QWEN_API_KEY=your_api_key_here
QWEN_CHAT_MODEL=qwen-plus
QWEN_VISION_MODEL=qwen-vl-max
QWEN_TURBO_MODEL=qwen-turbo

# 超时配置（秒）
QWEN_CHAT_TIMEOUT=30.0
QWEN_VISION_TIMEOUT=60.0

# 温度配置
QWEN_CHAT_TEMPERATURE=0.7
QWEN_VISION_TEMPERATURE=0.3
```

## 6. 常见用例

### 用例1: 编写使用Qwen API的服务

```python
from app.core.qwen_config import qwen_config
import httpx

class MyAIService:
    def __init__(self):
        self.headers = qwen_config.get_headers()
        self.url = qwen_config.QWEN_API_URL
        
    async def call_qwen_api(self, messages, purpose="chat"):
        model = qwen_config.get_model_for_purpose(purpose)
        timeout = qwen_config.get_timeout_for_model(model)
        temperature = qwen_config.get_temperature_for_model(model)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self.url, headers=self.headers, json=payload)
            return response.json()
```

### 用例2: 编写使用测试图像的测试

```python
import pytest
from app.core.test_resources import TestResources

def test_photo_analysis():
    # 获取测试图像base64
    image_base64 = TestResources.encode_image_to_base64("lunch")
    
    # 调用分析函数
    result = analyze_food_image(image_base64)
    
    # 验证结果
    assert "items" in result
    assert len(result["items"]) > 0
```

### 用例3: 编写使用测试用户的测试

```python
import pytest
from app.core.test_users import test_user_manager

def test_protected_endpoint(db):
    # 获取测试用户和令牌
    user_data = test_user_manager.get_or_create_test_user(db, "default")
    token = test_user_manager.get_test_user_token(db, "default")
    
    # 设置认证头
    headers = {"Authorization": f"Bearer {token}"}
    
    # 调用受保护端点
    response = client.get("/api/v1/protected", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
```

## 7. 故障排除

### 问题1: Qwen API密钥未设置

**症状**: `validate_configuration()`返回`"missing_api_key"`

**解决方案**:
1. 检查`.env`文件是否存在`QWEN_API_KEY`
2. 确保环境变量已加载
3. 运行`python validate_infrastructure.py`验证

### 问题2: 测试图像不存在

**症状**: `FileNotFoundError`或`validation['status']`为`"no_resources_available"`

**解决方案**:
1. 检查`/Users/felix/bmad/backend/tests/mealimg/`目录是否存在
2. 确保测试图像文件存在
3. 运行`TestResources.generate_resource_report()`查看详情

### 问题3: 测试用户创建失败

**症状**: `get_or_create_test_user()`抛出异常

**解决方案**:
1. 检查数据库连接
2. 确保测试用户邮箱唯一
3. 运行`test_user_manager.validate_test_users(db)`诊断问题

## 8. 最佳实践

1. **始终使用集中配置**: 不要硬编码模型名称或路径
2. **验证基础设施**: 在关键操作前验证配置
3. **使用预定义测试用户**: 避免在测试中创建随机用户
4. **缓存测试资源**: 重复使用base64编码的图像
5. **定期清理**: 定期运行基础设施验证和清理

## 9. 相关文件

- `/Users/felix/bmad/backend/app/core/qwen_config.py` - Qwen API配置
- `/Users/felix/bmad/backend/app/core/test_resources.py` - 测试资源管理
- `/Users/felix/bmad/backend/app/core/test_users.py` - 测试用户管理
- `/Users/felix/bmad/validate_infrastructure.py` - 基础设施验证脚本
- `/Users/felix/bmad/docs/comprehensive-analysis-backend.md` - 详细分析文档

## 10. 支持

如有问题，请参考：
1. 详细分析文档中的"集中式基础设施管理系统"章节
2. 运行`python validate_infrastructure.py`获取诊断信息
3. 检查相关源代码文件中的文档字符串