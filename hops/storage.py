"""
This module provides the `Storage` class for interacting with a SQLite database.
It supports logging received messages, inserting BBS entries, and reading BBS messages.

"""

import sqlite3
from datetime import datetime
from typing import Optional


class Storage:
    """
    Storage is a class that provides an interface for interacting with a SQLite database
    to store and retrieve logs, bulletin board system (BBS) messages, and general messages.
    """

    def __init__(self, db_filename):
        self.db_filename = db_filename
        self._initialize_database()

    def _initialize_database(self):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME UNIQUE NOT NULL,
                    packet_json TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bbs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME UNIQUE NOT NULL,
                    from_id TEXT NOT NULL,
                    from_short_name TEXT,
                    from_long_name TEXT,
                    message TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_bbs_timestamp
                ON bbs (timestamp)
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME UNIQUE NOT NULL,
                    from_id TEXT NOT NULL,
                    from_short_name TEXT,
                    from_long_name TEXT,
                    to_id TEXT NOT NULL,
                    channel_index INTEGER NOT NULL,
                    message TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_to_id_timestamp
                ON messages (to_id, timestamp)
            """
            )
            conn.commit()

    def log_packet(self, packet_json: str):
        """
        Log a received packet
        """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO packets
                    (timestamp, packet_json)
                VALUES
                    (?, ?)
            """,
                (now, packet_json),
            )
            conn.commit()

    def bbs_insert(
        self,
        from_id: str,
        from_short_name: Optional[str],
        from_long_name: Optional[str],
        message: str,
    ):
        """
        Log a received message
        """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bbs
                    (timestamp, from_id, from_short_name, from_long_name, message)
                VALUES
                    (?, ?, ?, ?, ?)
            """,
                (
                    now,
                    from_id,
                    from_short_name,
                    from_long_name,
                    message,
                ),
            )
            conn.commit()

    def bbs_read(self):
        """
        Log a received message
        """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    *
                FROM
                    bbs
                WHERE
                    timestamp >= datetime(?, '-28 days')
                ORDER BY timestamp DESC
                LIMIT 5
            """,
                (now,),
            )
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return result

    def messages_insert(
        self,
        from_id: str,
        from_short_name: Optional[str],
        from_long_name: Optional[str],
        to_id: str,
        message: str,
    ):
        """
        Log a received message
        """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages
                    (timestamp, from_id, from_short_name, from_long_name, to_id, message)
                VALUES
                    (?, ?, ?, ?, ?, ?)
            """,
                (now, from_id, from_short_name, from_long_name, to_id, message),
            )
            conn.commit()

    def messages_read(self, to_id: str):
        """
        Log a received message
        """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    *
                FROM
                    messages
                WHERE
                    to_id = ?
                    AND timestamp >= datetime(?, '-28 days')
                LIMIT 5
            """,
                (
                    to_id,
                    now,
                ),
            )
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
