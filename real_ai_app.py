from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
import os
import httpx
import asyncio
from datetime import datetime

# QWen API 配置
QWEN_API_KEY = "sk-14e3024216784670afe00fc2b5d79861"
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen-turbo"

# 创建数据库
conn = sqlite3.connect("test_real.db")
cursor = conn.cursor()

# 创建用户表
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nickname TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 创建健康数据表
cursor.execute("""
CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight REAL,
    height REAL,
    bmi REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# 创建对话历史表
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

conn.commit()

app = FastAPI(title="体重管理 AI 助手 - 真实AI版", version="1.0.0")


# 模型
class UserCreate(BaseModel):
    email: str
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class HealthData(BaseModel):
    weight: float
    height: float


class AIChat(BaseModel):
    message: str
    user_id: Optional[int] = 1


class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None


# QWen AI 服务
async def get_ai_response(
    user_message: str, user_context: dict | None = None, max_retries: int = 3
) -> str:
    """调用 QWen API 获取 AI 响应"""

    # 构建系统提示词 - 体重管理专家角色
    system_prompt = """你是一位专业的体重管理AI助手，融合了营养师、行为教练和情感支持者三重身份。请以专业、温暖、支持性的方式回应用户。

你的核心能力：
1. 营养师：提供科学的饮食建议、热量计算、营养分析
2. 行为教练：帮助建立健康习惯、克服障碍、保持动力
3. 情感支持者：提供情感支持、压力管理、积极鼓励

请根据用户的问题提供个性化、实用、可操作的建议。保持回答简洁实用，重点突出。"""

    # 构建用户上下文
    user_context_str = ""
    if user_context:
        user_context_str = f"\n用户信息：{json.dumps(user_context, ensure_ascii=False)}"

    messages = [
        {"role": "system", "content": system_prompt + user_context_str},
        {"role": "user", "content": user_message},
    ]

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": QWEN_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800,  # 减少token数量，加快响应
    }

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # 增加超时时间到60秒
                response = await client.post(QWEN_API_URL, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 429:  # 限流
                    wait_time = 2**attempt  # 指数退避
                    print(f"API限流，等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(
                        f"QWen API 错误 (尝试 {attempt + 1}/{max_retries}): {response.status_code}"
                    )
                    if attempt == max_retries - 1:
                        return "抱歉，AI服务暂时不可用。请稍后再试。"
                    await asyncio.sleep(1)

        except httpx.TimeoutException:
            print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                return "请求超时，请检查网络连接后重试。"
            await asyncio.sleep(1)
        except Exception as e:
            print(f"调用 QWen API 异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return "网络连接异常，请检查网络后重试。"
            await asyncio.sleep(1)

    return "服务暂时不可用，请稍后再试。"


# API端点
@app.get("/")
async def root():
    return {
        "message": "体重管理 AI 助手 API (真实AI版)",
        "version": "1.0.0",
        "ai_service": "QWen Turbo",
        "status": "running",
    }


@app.get("/health")
async def health():
    # 测试 AI 服务连通性
    try:
        test_response = await get_ai_response("测试连接")
        ai_status = "connected" if len(test_response) > 0 else "disconnected"
    except:
        ai_status = "error"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_service": ai_status,
        "database": "connected",
    }


@app.post("/api/v1/auth/register")
async def register(user: UserCreate):
    try:
        cursor.execute(
            "INSERT INTO users (email, password, nickname) VALUES (?, ?, ?)",
            (user.email, user.password, user.nickname),
        )
        conn.commit()
        user_id = cursor.lastrowid

        # 创建欢迎对话
        welcome_message = f"欢迎 {user.nickname or user.email} 加入体重管理助手！我是你的AI健康伙伴，随时为你提供专业的营养建议、行为指导和情感支持。"

        cursor.execute(
            "INSERT INTO conversations (user_id, user_message, ai_response) VALUES (?, ?, ?)",
            (user_id, "注册成功", welcome_message),
        )
        conn.commit()

        return {
            "message": "注册成功",
            "user_id": user_id,
            "email": user.email,
            "welcome_message": welcome_message,
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="邮箱已存在")


@app.post("/api/v1/auth/login")
async def login(user: UserLogin):
    cursor.execute(
        "SELECT id, email, nickname FROM users WHERE email = ? AND password = ?",
        (user.email, user.password),
    )
    result = cursor.fetchone()
    if result:
        return {
            "message": "登录成功",
            "user_id": result[0],
            "email": result[1],
            "nickname": result[2],
        }
    else:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")


@app.post("/api/v1/health-data")
async def record_health_data(data: HealthData):
    # 模拟用户ID
    user_id = 1
    bmi = data.weight / ((data.height / 100) ** 2)

    cursor.execute(
        "INSERT INTO health_data (user_id, weight, height, bmi) VALUES (?, ?, ?, ?)",
        (user_id, data.weight, data.height, bmi),
    )
    conn.commit()

    # 根据BMI提供建议
    bmi_category = ""
    if bmi < 18.5:
        bmi_category = "偏瘦"
    elif bmi < 24:
        bmi_category = "正常"
    elif bmi < 28:
        bmi_category = "超重"
    else:
        bmi_category = "肥胖"

    return {
        "message": "数据记录成功",
        "weight": data.weight,
        "height": data.height,
        "bmi": round(bmi, 2),
        "bmi_category": bmi_category,
        "health_assessment": f"你的BMI为{round(bmi, 2)}，属于{bmi_category}范围。",
    }


@app.post("/api/v1/chat")
async def chat_with_ai(chat: AIChat):
    # 获取用户健康数据作为上下文
    cursor.execute(
        "SELECT weight, height, bmi FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1",
        (chat.user_id,),
    )
    health_data = cursor.fetchone()

    user_context = {}
    if health_data:
        user_context = {
            "weight": health_data[0],
            "height": health_data[1],
            "bmi": health_data[2],
        }

    # 调用真实 QWen AI
    ai_response = await get_ai_response(chat.message, user_context)

    # 保存对话历史
    cursor.execute(
        "INSERT INTO conversations (user_id, user_message, ai_response) VALUES (?, ?, ?)",
        (chat.user_id, chat.message, ai_response),
    )
    conn.commit()

    return {
        "user_message": chat.message,
        "ai_response": ai_response,
        "timestamp": datetime.now().isoformat(),
        "ai_model": QWEN_MODEL,
    }


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    cursor.execute(
        "SELECT id, email, nickname, created_at FROM users WHERE id = ?", (user_id,)
    )
    result = cursor.fetchone()
    if result:
        # 获取用户健康数据
        cursor.execute(
            "SELECT weight, height, bmi, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 5",
            (user_id,),
        )
        health_records = cursor.fetchall()

        # 获取对话历史
        cursor.execute(
            "SELECT user_message, ai_response, created_at FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,),
        )
        conversations = cursor.fetchall()

        return {
            "id": result[0],
            "email": result[1],
            "nickname": result[2],
            "created_at": result[3],
            "health_records": [
                {
                    "weight": record[0],
                    "height": record[1],
                    "bmi": record[2],
                    "recorded_at": record[3],
                }
                for record in health_records
            ],
            "recent_conversations": [
                {
                    "user_message": conv[0],
                    "ai_response": conv[1][:100] + "..."
                    if len(conv[1]) > 100
                    else conv[1],
                    "created_at": conv[2],
                }
                for conv in conversations
            ],
        }
    else:
        raise HTTPException(status_code=404, detail="用户不存在")


@app.get("/api/v1/health-summary/{user_id}")
async def get_health_summary(user_id: int):
    cursor.execute(
        "SELECT weight, height, bmi, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1",
        (user_id,),
    )
    latest = cursor.fetchone()

    if not latest:
        raise HTTPException(status_code=404, detail="未找到健康数据")

    weight, height, bmi, recorded_at = latest

    # 计算趋势
    cursor.execute(
        "SELECT weight FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 2",
        (user_id,),
    )
    weights = cursor.fetchall()

    trend = "稳定"
    if len(weights) >= 2:
        change = weights[0][0] - weights[1][0]
        if change > 0.5:
            trend = "上升"
        elif change < -0.5:
            trend = "下降"

    # BMI分类
    if bmi < 18.5:
        category = "偏瘦"
        suggestion = "建议适当增加营养摄入"
    elif bmi < 24:
        category = "正常"
        suggestion = "保持健康生活习惯"
    elif bmi < 28:
        category = "超重"
        suggestion = "建议控制饮食，增加运动"
    else:
        category = "肥胖"
        suggestion = "建议制定减重计划，咨询专业人士"

    return {
        "current_weight": weight,
        "height": height,
        "bmi": round(bmi, 2),
        "bmi_category": category,
        "recorded_at": recorded_at,
        "trend": trend,
        "health_suggestion": suggestion,
    }


@app.post("/api/v1/ai-analysis/{user_id}")
async def get_ai_analysis(user_id: int):
    """获取AI对用户数据的综合分析"""

    # 获取用户所有健康数据
    cursor.execute(
        "SELECT weight, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at",
        (user_id,),
    )
    weight_data = cursor.fetchall()

    if not weight_data:
        raise HTTPException(status_code=404, detail="未找到健康数据")

    # 构建分析请求
    weights = [w[0] for w in weight_data]
    dates = [w[1] for w in weight_data]

    analysis_request = f"""
    请分析以下用户的体重数据，并提供专业建议：
    
    用户ID: {user_id}
    体重记录: {weights} kg
    记录时间: {dates}
    
    当前体重: {weights[-1]} kg
    体重变化趋势: 从{weights[0]} kg 到 {weights[-1]} kg
    
    请提供：
    1. 体重变化分析
    2. 健康风险评估
    3. 个性化建议（饮食、运动、习惯）
    4. 鼓励和支持性话语
    """

    ai_response = await get_ai_response(analysis_request)

    return {
        "user_id": user_id,
        "weight_data": weights,
        "analysis_date": datetime.now().isoformat(),
        "ai_analysis": ai_response,
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 启动体重管理 AI 助手 (真实AI版)")
    print(f"📡 AI服务: QWen Turbo")
    print(f"🌐 服务地址: http://localhost:8000")
    print(f"📚 API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
