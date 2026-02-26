"""Seed the database with a test academy, coach, and players."""

import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable when running from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.academy import Academy
from app.models.coach import Coach
from app.models.player import Player


async def seed() -> None:
    async with async_session() as session:
        session: AsyncSession

        # --- Academy ---
        result = await session.execute(select(Academy).where(Academy.name == "TSG Bangalore"))
        academy = result.scalar_one_or_none()
        if academy is None:
            academy = Academy(name="TSG Bangalore", city="Bangalore")
            session.add(academy)
            await session.flush()
            print(f"Created academy: {academy.name} ({academy.id})")
        else:
            print(f"Academy already exists: {academy.name} ({academy.id})")

        # --- Coach ---
        coach_email = "coach@tsg.com"
        result = await session.execute(select(Coach).where(Coach.email == coach_email))
        coach = result.scalar_one_or_none()
        if coach is None:
            coach = Coach(
                academy_id=academy.id,
                name="Coach TSG",
                email=coach_email,
                password_hash=bcrypt.hashpw(b"test1234", bcrypt.gensalt()).decode(),
                phone="+919000000001",
            )
            session.add(coach)
            await session.flush()
            print(f"Created coach: {coach.email} ({coach.id})")
        else:
            print(f"Coach already exists: {coach.email} ({coach.id})")

        # --- Players ---
        players_data = [
            {"name": "Rahul Sharma", "phone": "+919100000001", "skill_level": "beginner"},
            {"name": "Priya Patel", "phone": "+919100000002", "skill_level": "intermediate"},
            {"name": "Arjun Reddy", "phone": "+919100000003", "skill_level": "advanced"},
        ]

        for p in players_data:
            result = await session.execute(select(Player).where(Player.phone == p["phone"]))
            existing = result.scalar_one_or_none()
            if existing is None:
                player = Player(
                    academy_id=academy.id,
                    coach_id=coach.id,
                    name=p["name"],
                    phone=p["phone"],
                    skill_level=p["skill_level"],
                )
                session.add(player)
                print(f"Created player: {p['name']} ({p['phone']})")
            else:
                print(f"Player already exists: {existing.name} ({existing.phone})")

        await session.commit()

    await engine.dispose()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
