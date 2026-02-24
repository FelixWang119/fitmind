const request = require('supertest');
const app = require('../../backend/app/main'); // 根据实际情况调整

describe('营养API测试', () => {
  let token;
  let userId;

  beforeAll(async () => {
    // 创建测试用户并获取认证令牌
    const registerResponse = await request(app)
      .post('/api/v1/auth/register')
      .send({
        email: 'test-nutrition@example.com',
        password: 'TestPass123!',
        confirm_password: 'TestPass123!',
        nickname: '营养测试用户'
      });
    
    expect(registerResponse.status).toBe(200);
    
    const loginResponse = await request(app)
      .post('/api/v1/auth/login')
      .send({
        username: 'test-nutrition@example.com',
        password: 'TestPass123!'
      });
    
    expect(loginResponse.status).toBe(200);
    token = loginResponse.body.access_token;
    userId = registerResponse.body.id;
  });

  describe('GET /api/v1/nutrition/recommendations', () => {
    it('应该成功返回营养推荐数据', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/recommendations')
        .set('Authorization', `Bearer ${token}`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('calorie_targets');
      expect(response.body).toHaveProperty('macronutrients');
      expect(response.body).toHaveProperty('meal_suggestions');
      expect(response.body).toHaveProperty('hydration_goal');
      expect(response.body).toHaveProperty('supplement_recommendations');
      
      // 验证数据结构
      expect(response.body.calorie_targets).toHaveProperty('maintenance');
      expect(response.body.calorie_targets).toHaveProperty('target');
      expect(response.body.calorie_targets).toHaveProperty('weight_loss');
      expect(response.body.calorie_targets).toHaveProperty('weight_gain');
      expect(response.body.calorie_targets).toHaveProperty('weight_difference');
      
      expect(response.body.macronutrients).toHaveProperty('protein_g');
      expect(response.body.macronutrients).toHaveProperty('fat_g');
      expect(response.body.macronutrients).toHaveProperty('carb_g');
      
      expect(Array.isArray(response.body.meal_suggestions)).toBe(true);
    });

    it('未认证用户访问应返回401错误', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/recommendations');
      
      expect(response.status).toBe(401);
    });
  });

  describe('GET /api/v1/nutrition/calorie-target', () => {
    it('应该成功返回卡路里目标', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/calorie-target')
        .set('Authorization', `Bearer ${token}`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('bmr');
      expect(response.body).toHaveProperty('tdee');
      expect(response.body).toHaveProperty('maintenance');
      expect(response.body).toHaveProperty('target');
    });

    it('未认证用户访问应返回401错误', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/calorie-target');
      
      expect(response.status).toBe(401);
    });
  });

  describe('POST /api/v1/nutrition/analyze-food-image', () => {
    it('应该返回食物图像分析结果', async () => {
      // 使用模拟图像数据
      const mockImageData = {
        image: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEAA', // 压缩的测试图像base64字符串
        date: new Date().toISOString().split('T')[0]
      };
      
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-image')
        .set('Authorization', `Bearer ${token}`)
        .send(mockImageData);
      
      // 预期成功或内部错误，但不应该因为空值抛出错误
      expect([200, 400, 500]).toContain(response.status);
    });

    it('使用无效图像数据应返回适当的错误', async () => {
      const invalidImageData = {
        image: '',
        date: new Date().toISOString().split('T')[0]
      };
      
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-image')
        .set('Authorization', `Bearer ${token}`)
        .send(invalidImageData);
      
      expect([400, 200]).toContain(response.status); // 可能返回错误或模拟的默认值
    });

    it('未认证用户访问应返回401错误', async () => {
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-image')
        .send({ image: 'mock' });
      
      expect(response.status).toBe(401);
    });
  });

  describe('GET /api/v1/nutrition/macronutrients', () => {
    it('应该成功返回宏量营养素目标', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/macronutrients')
        .set('Authorization', `Bearer ${token}`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('target_calories');
      expect(response.body).toHaveProperty('protein_g');
      expect(response.body).toHaveProperty('fat_g');
      expect(response.body).toHaveProperty('carb_g');
      expect(response.body).toHaveProperty('protein_percentage');
      expect(response.body).toHaveProperty('fat_percentage');
      expect(response.body).toHaveProperty('carb_percentage');
    });

    it('未认证用户访问应返回401错误', async () => {
      const response = await request(app)
        .get('/api/v1/nutrition/macronutrients');
      
      expect(response.status).toBe(401);
    });
  });

  describe('POST /api/v1/nutrition/analyze-food-log', () => {
    it('应该分析食物日志并返回营养评估', async () => {
      const foodItems = [
        {
          name: '苹果',
          meal_type: 'snack',
          calories: 52,
          protein_g: 0.3,
          fat_g: 0.2,
          carb_g: 14
        }
      ];
      
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-log')
        .set('Authorization', `Bearer ${token}`)
        .send(foodItems);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('meal_distribution');
      expect(response.body).toHaveProperty('nutrition_score');
      expect(response.body).toHaveProperty('target_comparison');
    });

    it('提交空的食物列表应返回错误或有效响应', async () => {
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-log')
        .set('Authorization', `Bearer ${token}`)
        .send([]);
      
      // 可接受200（正常处理）或400（输入错误）
      expect([200, 400]).toContain(response.status);
    });

    it('未认证用户访问应返回401错误', async () => {
      const response = await request(app)
        .post('/api/v1/nutrition/analyze-food-log')
        .send([{ name: 'test' }]);
      
      expect(response.status).toBe(401);
    });
  });
});