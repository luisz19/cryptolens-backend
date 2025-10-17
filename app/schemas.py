from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum as PyEnum

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    risk_profile: str 

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    risk_profile: Optional[str] = None

    class Config:
        from_attributes = True

class CryptoBase(BaseModel):
    name: str
    symbol: str

    class Config:
        from_attributes = True

class CryptoResponse(BaseModel):
    id: int
    name: str
    symbol: str

    class Config:
        from_attributes = True

class CryptoCreate(BaseModel):
    name: str
    symbol: str

    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    user_id: int
    crypto_id: int
    risk_level: Optional["RiskLevelEnum"] = None

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    crypto_id: int
    risk_level: Optional["RiskLevelEnum"] = None

    class Config:
        from_attributes = True

class RecommendationCreate(BaseModel):
    user_id: int
    crypto_id: int
    risk_level: Optional["RiskLevelEnum"] = None

    class Config:
        from_attributes = True

class RiskLevelUpdate(BaseModel):
    risk_level: "RiskLevelEnum"

    class Config:
        from_attributes = True


class RiskLevelEnum(str, PyEnum):
    baixo = "baixo"
    moderado = "moderado"
    alto = "alto"