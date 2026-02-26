import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    frame_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("frames.id"))
    reference_frame_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("frames.id")
    )
    deviation_scores_json: Mapped[dict | None] = mapped_column(JSONB)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ai_feedback_text: Mapped[str | None] = mapped_column(Text)
    coach_feedback_text: Mapped[str | None] = mapped_column(Text)
    coach_approved: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    frame: Mapped["Frame | None"] = relationship(
        back_populates="comparisons",
        foreign_keys=[frame_id],
    )
    reference_frame: Mapped["Frame | None"] = relationship(
        back_populates="reference_comparisons",
        foreign_keys=[reference_frame_id],
    )
