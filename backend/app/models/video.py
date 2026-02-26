import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id")
    )
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    camera_angle: Mapped[str | None] = mapped_column(String(20))
    club_type: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), server_default=text("'uploading'"))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    fps: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))
    processed_at: Mapped[datetime | None] = mapped_column()

    player: Mapped["Player | None"] = relationship(back_populates="videos")
    frames: Mapped[list["Frame"]] = relationship(back_populates="video")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="video")
