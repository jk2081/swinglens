import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id")
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    angles_avg_json: Mapped[dict | None] = mapped_column(JSONB)
    consistency_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    total_swings: Mapped[int | None] = mapped_column(Integer)
    coach_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    player: Mapped["Player | None"] = relationship(back_populates="progress_snapshots")
