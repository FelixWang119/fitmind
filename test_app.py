from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import json
import os

# 创建数据库
conn = sqlite3.connect("test.db")
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

conn.commit()

app = FastAPI(title="体重管理 AI 助手 - 测试版", version="1.0.0")


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


# API端点
@app.get("/")
async def root():
    return {"message": "体重管理 AI 助手 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/auth/register")
async def register(user: UserCreate):
    try:
        cursor.execute(
            "INSERT INTO users (email, password, nickname) VALUES (?, ?, ?)",
            (user.email, user.password, user.nickname),
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"message": "注册成功", "user_id": user_id, "email": user.email}
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

    return {
        "message": "数据记录成功",
        "weight": data.weight,
        "height": data.height,
        "bmi": round(bmi, 2),
    }


@app.post("/api/v1/chat")
async def chat_with_ai(chat: AIChat):
    # 模拟AI响应
    responses = {
        "你好": "你好！我是你的体重管理助手，有什么可以帮助你的吗？",
        "我今天该吃什么": "根据健康饮食原则，建议你今天摄入：\n- 早餐：燕麦粥+鸡蛋\n- 午餐：鸡胸肉沙拉\n- 晚餐：蒸鱼+蔬菜\n记得多喝水哦！",
        "我的BMI正常吗": "BMI在18.5-24之间是正常范围。请记录你的身高体重，我可以帮你计算。",
        "如何减肥": "健康减肥建议：\n1. 控制热量摄入\n2. 增加运动量\n3. 保证充足睡眠\n4. 保持水分摄入\n5. 建立健康习惯",
    }

    response = responses.get(
        chat.message,
        "我理解你的问题，但需要更多信息来提供个性化建议。你可以告诉我你的身高体重吗？",
    )

    return {"user_message": chat.message, "ai_response": response, "timestamp": "now"}


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    cursor.execute(
        "SELECT id, email, nickname, created_at FROM users WHERE id = ?", (user_id,)
    )
    result = cursor.fetchone()
    if result:
        return {
            "id": result[0],
            "email": result[1],
            "nickname": result[2],
            "created_at": result[3],
        }
    else:
        raise HTTPException(status_code=404, detail="用户不存在")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
