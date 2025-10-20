
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from service.green_agent.config import DB_PATH


class Storage:
    """SQLite storage for green agent runs and logs."""
    
    def __init__(self):
        self.db_path = str(DB_PATH)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    agent_strategy TEXT,
                    num_trials INTEGER,
                    pass_1 REAL,
                    pass_k TEXT,
                    metrics_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    episode_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    task_id INTEGER,
                    trial INTEGER,
                    reward REAL,
                    actions_count INTEGER,
                    created_at TEXT,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            conn.commit()
    
    def save_run(self, run_id: str, agent_strategy: str, num_trials: int, 
                 pass_1: float, pass_k: Dict[int, float], metrics: Dict[str, Any]):
        """Save a run to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO runs (run_id, created_at, agent_strategy, num_trials, 
                                 pass_1, pass_k, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                datetime.now().isoformat(),
                agent_strategy,
                num_trials,
                pass_1,
                json.dumps(pass_k),
                json.dumps(metrics),
            ))
            conn.commit()
    
    def save_episode(self, episode_id: str, run_id: str, task_id: int,
                     trial: int, reward: float, actions_count: int):
        """Save an episode to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes (episode_id, run_id, task_id, trial, 
                                     reward, actions_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id,
                run_id,
                task_id,
                trial,
                reward,
                actions_count,
                datetime.now().isoformat(),
            ))
            conn.commit()
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a run by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row:
                return dict(row)
        return None
    
    def get_episodes(self, run_id: str) -> List[Dict[str, Any]]:
        """Retrieve all episodes for a run."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM episodes WHERE run_id = ? ORDER BY created_at",
                (run_id,)
            ).fetchall()
            return [dict(row) for row in rows]


# Global storage instance
storage = Storage()
