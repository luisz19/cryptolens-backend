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

class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    value = Column(String(50), index=True)  # ex: 'short', 'medium', 'long'
    label = Column(String(255))             
    score = Column(Integer)                 

    question = relationship("Questions", back_populates="options")


class QuestionnaireSubmission(Base):
    __tablename__ = "questionnaire_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    total_score = Column(Integer)
    max_score = Column(Integer)
    risk_level = Column(Enum(RiskLevel))  # baixo/moderado/alto
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="questionnaires")
    answers = relationship("UserAnswer", back_populates="submission", cascade="all, delete-orphan")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("questionnaire_submissions.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    option_id = Column(Integer, ForeignKey("question_options.id", ondelete="SET NULL"), nullable=True)
    selected_value = Column(String(50))
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("QuestionnaireSubmission", back_populates="answers")
    user = relationship("User", back_populates="answers")
    question = relationship("Questions", back_populates="answers")
    option = relationship("QuestionOption")


User.answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")
User.questionnaires = relationship("QuestionnaireSubmission", back_populates="user", cascade="all, delete-orphan")

