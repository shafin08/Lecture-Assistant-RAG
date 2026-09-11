# ============================================================
# app/models.py
# Database table definitions
# Defines: User, Document, Conversation, Message
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    conversation = relationship(
        "Conversation",
        back_populates="owner",
        cascade="all, delete-orphan"

    )




class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    content = Column(Text)

    owner = relationship("User", back_populates="documents") 
    doc_conversation = relationship(
        "Conversation",
        back_populates="conversation_doc"

    )

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="conversation") 

    messages = relationship(
        "Messages",
        back_populates="owner_m",
        cascade="all, delete-orphan",
        order_by="Messages.created_at"
    )

    conversation_doc = relationship("Document",back_populates="doc_conversation", cascade="all, delete-orphan")



class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner_m = relationship("Conversation", back_populates="messages") 

 

