from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "slasher.db"


class StatsDatabase:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_stats (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                hunts INTEGER NOT NULL DEFAULT 0,
                survived INTEGER NOT NULL DEFAULT 0,
                killed INTEGER NOT NULL DEFAULT 0,
                current_streak INTEGER NOT NULL DEFAULT 0,
                best_streak INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS killer_stats (
                guild_id INTEGER NOT NULL,
                killer_key TEXT NOT NULL,
                encounters INTEGER NOT NULL DEFAULT 0,
                kills INTEGER NOT NULL DEFAULT 0,
                escapes INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, killer_key)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_killer_stats (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                killer_key TEXT NOT NULL,
                encounters INTEGER NOT NULL DEFAULT 0,
                kills INTEGER NOT NULL DEFAULT 0,
                escapes INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id, killer_key)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                auto_enabled INTEGER NOT NULL DEFAULT 0,
                auto_channel_id INTEGER,
                min_minutes INTEGER NOT NULL DEFAULT 45,
                max_minutes INTEGER NOT NULL DEFAULT 120,
                ai_enabled INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Upgrade older Slasher databases in place.
        columns = {
            row["name"]
            for row in self.conn.execute(
                "PRAGMA table_info(guild_settings)"
            ).fetchall()
        }

        if "ai_enabled" not in columns:
            self.conn.execute(
                """
                ALTER TABLE guild_settings
                ADD COLUMN ai_enabled INTEGER NOT NULL DEFAULT 0
                """
            )

        self.conn.commit()

    def record_hunt(
        self,
        guild_id: int,
        user_id: int,
        killer_key: str,
        killed: bool,
    ) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO player_stats (guild_id, user_id)
            VALUES (?, ?)
            """,
            (guild_id, user_id),
        )

        self.conn.execute(
            """
            UPDATE player_stats
            SET hunts = hunts + 1,
                survived = survived + ?,
                killed = killed + ?,
                current_streak = CASE
                    WHEN ? = 1 THEN 0
                    ELSE current_streak + 1
                END,
                best_streak = CASE
                    WHEN ? = 0 AND current_streak + 1 > best_streak
                    THEN current_streak + 1
                    ELSE best_streak
                END
            WHERE guild_id = ? AND user_id = ?
            """,
            (
                0 if killed else 1,
                1 if killed else 0,
                1 if killed else 0,
                1 if killed else 0,
                guild_id,
                user_id,
            ),
        )

        self.conn.execute(
            """
            INSERT OR IGNORE INTO killer_stats (guild_id, killer_key)
            VALUES (?, ?)
            """,
            (guild_id, killer_key),
        )

        self.conn.execute(
            """
            UPDATE killer_stats
            SET encounters = encounters + 1,
                kills = kills + ?,
                escapes = escapes + ?
            WHERE guild_id = ? AND killer_key = ?
            """,
            (
                1 if killed else 0,
                0 if killed else 1,
                guild_id,
                killer_key,
            ),
        )

        self.conn.execute(
            """
            INSERT OR IGNORE INTO player_killer_stats
                (guild_id, user_id, killer_key)
            VALUES (?, ?, ?)
            """,
            (guild_id, user_id, killer_key),
        )

        self.conn.execute(
            """
            UPDATE player_killer_stats
            SET encounters = encounters + 1,
                kills = kills + ?,
                escapes = escapes + ?
            WHERE guild_id = ? AND user_id = ? AND killer_key = ?
            """,
            (
                1 if killed else 0,
                0 if killed else 1,
                guild_id,
                user_id,
                killer_key,
            ),
        )

        self.conn.commit()

    def get_player_stats(
        self,
        guild_id: int,
        user_id: int,
    ) -> dict[str, Any]:
        row = self.conn.execute(
            """
            SELECT hunts, survived, killed, current_streak, best_streak
            FROM player_stats
            WHERE guild_id = ? AND user_id = ?
            """,
            (guild_id, user_id),
        ).fetchone()

        if row is None:
            return {
                "hunts": 0,
                "survived": 0,
                "killed": 0,
                "current_streak": 0,
                "best_streak": 0,
            }

        return dict(row)

    def get_player_killer_stats(
        self,
        guild_id: int,
        user_id: int,
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT killer_key, encounters, kills, escapes
            FROM player_killer_stats
            WHERE guild_id = ? AND user_id = ?
            ORDER BY encounters DESC, killer_key ASC
            """,
            (guild_id, user_id),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_leaderboard(
        self,
        guild_id: int,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT user_id, hunts, survived, killed,
                   current_streak, best_streak
            FROM player_stats
            WHERE guild_id = ?
            ORDER BY survived DESC, best_streak DESC, hunts DESC
            LIMIT ?
            """,
            (guild_id, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_killer_stats(
        self,
        guild_id: int,
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT killer_key, encounters, kills, escapes
            FROM killer_stats
            WHERE guild_id = ?
            ORDER BY encounters DESC, killer_key ASC
            """,
            (guild_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    def _ensure_guild_settings(self, guild_id: int) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO guild_settings (guild_id)
            VALUES (?)
            """,
            (guild_id,),
        )
        self.conn.commit()

    def get_guild_settings(
        self,
        guild_id: int,
    ) -> dict[str, Any]:
        self._ensure_guild_settings(guild_id)

        row = self.conn.execute(
            """
            SELECT auto_enabled,
                   auto_channel_id,
                   min_minutes,
                   max_minutes,
                   ai_enabled
            FROM guild_settings
            WHERE guild_id = ?
            """,
            (guild_id,),
        ).fetchone()

        return {
            "auto_enabled": bool(row["auto_enabled"]),
            "auto_channel_id": row["auto_channel_id"],
            "min_minutes": row["min_minutes"],
            "max_minutes": row["max_minutes"],
            "ai_enabled": bool(row["ai_enabled"]),
        }

    def set_ai_enabled(
        self,
        guild_id: int,
        enabled: bool,
    ) -> None:
        self._ensure_guild_settings(guild_id)
        self.conn.execute(
            """
            UPDATE guild_settings
            SET ai_enabled = ?
            WHERE guild_id = ?
            """,
            (1 if enabled else 0, guild_id),
        )
        self.conn.commit()

    def set_auto_enabled(
        self,
        guild_id: int,
        enabled: bool,
    ) -> None:
        self._ensure_guild_settings(guild_id)
        self.conn.execute(
            """
            UPDATE guild_settings
            SET auto_enabled = ?
            WHERE guild_id = ?
            """,
            (1 if enabled else 0, guild_id),
        )
        self.conn.commit()

    def set_auto_channel(
        self,
        guild_id: int,
        channel_id: int,
    ) -> None:
        self._ensure_guild_settings(guild_id)
        self.conn.execute(
            """
            UPDATE guild_settings
            SET auto_channel_id = ?
            WHERE guild_id = ?
            """,
            (channel_id, guild_id),
        )
        self.conn.commit()

    def set_auto_frequency(
        self,
        guild_id: int,
        min_minutes: int,
        max_minutes: int,
    ) -> None:
        self._ensure_guild_settings(guild_id)
        self.conn.execute(
            """
            UPDATE guild_settings
            SET min_minutes = ?, max_minutes = ?
            WHERE guild_id = ?
            """,
            (min_minutes, max_minutes, guild_id),
        )
        self.conn.commit()
