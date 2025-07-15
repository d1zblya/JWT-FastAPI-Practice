import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped

from src.database.session import Base


class RefreshTokenModel(Base):
    __tablename__ = 'refresh_tokens'

    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True)

    token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=False
    )
