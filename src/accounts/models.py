import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TelegramAccount(Base):
    __tablename__ = 'telegram_account'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    phone = Column(String(50), unique=True, nullable=False)
    code = Column(String(10), nullable=True)
    code_hash = Column(String(50), nullable=True)

    cleared = Column(Boolean, default=False, nullable=False)  # clear all chats and logout others session
    sold = Column(Boolean, default=False, nullable=False)

    session = Column(Text, nullable=False)
