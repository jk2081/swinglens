import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    academy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academies.id")
    )
    coach_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("coaches.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    handicap: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    skill_level: Mapped[str] = mapped_column(String(20), server_default=text("'beginner'"))
    dominant_hand: Mapped[str] = mapped_column(String(10), server_default=text("'right'"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    academy: Mapped["Academy | None"] = relationship(back_populates="players")
    coach: Mapped["Coach | None"] = relationship(back_populates="players")
    videos: Mapped[list["Video"]] = relationship(back_populates="player")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="player")
    progress_snapshots: Mapped[list["ProgressSnapshot"]] = relationship(back_populates="player")
