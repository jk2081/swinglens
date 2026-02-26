import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    video_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id"))
    swing_phase: Mapped[str] = mapped_column(String(30), nullable=False)
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    s3_key_raw: Mapped[str | None] = mapped_column(String(500))
    s3_key_overlay: Mapped[str | None] = mapped_column(String(500))
    s3_key_skeleton: Mapped[str | None] = mapped_column(String(500))
    keypoints_json: Mapped[dict | None] = mapped_column(JSONB)
    joint_angles_json: Mapped[dict | None] = mapped_column(JSONB)
    is_reference: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    video: Mapped["Video | None"] = relationship(back_populates="frames")
    comparisons: Mapped[list["Comparison"]] = relationship(
        back_populates="frame",
        foreign_keys="Comparison.frame_id",
    )
    reference_comparisons: Mapped[list["Comparison"]] = relationship(
        back_populates="reference_frame",
        foreign_keys="Comparison.reference_frame_id",
    )
