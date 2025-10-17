from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    password = Column(String(255))
    risk_profile = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    recommendations = relationship("Recommendation", back_populates="user")

class RiskLevel(enum.Enum):
    baixo = "baixo"
    moderado = "moderado"
    alto = "alto"

class Cryptos(Base):
    __tablename__ = "cryptos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    symbol = Column(String(20), unique=True, index=True)
    recommendations = relationship("Recommendation", back_populates="crypto")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    crypto_id = Column(Integer, ForeignKey("cryptos.id", ondelete="CASCADE"))
    risk_level = Column(Enum(RiskLevel), nullable=True)
    recommended_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")
    crypto = relationship("Cryptos", back_populates="recommendations")

