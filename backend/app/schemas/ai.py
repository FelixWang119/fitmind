from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    """AI请求"""

    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000)
    conversation_id: Optional[int] = None


class AIResponse(BaseModel):
    """AI 响应"""

    response: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # Role switching fields
    current_role: Optional[str] = "general"
    role_switched: Optional[bool] = False
    previous_role: Optional[str] = None
    is_fusion: Optional[bool] = False
    fusion_roles: Optional[list] = None
    notification: Optional[str] = None
    # Conversation ID
    conversation_id: Optional[int] = None

    class Config:
        from_attributes = True


class NutritionAdviceRequest(BaseModel):
    """营养建议请求"""

    user_data: Dict[str, Any]
    goal: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None


class NutritionAdviceResponse(BaseModel):
    """营养建议响应"""

    advice: str
    daily_calories: Optional[int] = None
    macronutrients: Optional[Dict[str, float]] = None
    meal_suggestions: Optional[list] = None
    warnings: Optional[list] = None

    class Config:
        from_attributes = True


class AIHealthAdviceRequest(BaseModel):
    """AI健康建议请求"""

    context: Optional[Dict[str, Any]] = None
    specific_question: Optional[str] = None


class AIHealthAdviceResponse(BaseModel):
    """AI健康建议响应"""

    advice: str
    confidence_score: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    recommendations: Optional[list] = None
    warnings: Optional[list] = None

    class Config:
        from_attributes = True
