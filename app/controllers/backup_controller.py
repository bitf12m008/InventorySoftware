import os
import hashlib
import datetime
from shutil import copyfile
from app.db.database_init import DB_PATH

class BackupController:
    BACKUP_DIR = "backups"
    HASH_FILE = ".last_db_hash"

    @classmethod
    def _calculate_db_hash(cls):
        h = hashlib.sha256()
        with open(DB_PATH, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def _load_last_hash(cls):
        if not os.path.exists(cls.HASH_FILE):
            return None
        with open(cls.HASH_FILE, "r") as f:
            return f.read().strip()

    @classmethod
    def _save_last_hash(cls, db_hash):
        with open(cls.HASH_FILE, "w") as f:
            f.write(db_hash)

    @classmethod
    def backup_forced(cls):
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)

        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"inventory_{ts}.db"
        path = os.path.join(cls.BACKUP_DIR, filename)

        copyfile(DB_PATH, path)
        return path
    
    @classmethod
    def backup_if_changed(cls):
        current_hash = cls._calculate_db_hash()
        last_hash = cls._load_last_hash()

        if current_hash == last_hash:
            # No DB changes → skip backup
            return None

        # DB changed → backup
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)

        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(
            cls.BACKUP_DIR, f"inventory_{ts}.db"
        )

        copyfile(DB_PATH, backup_path)
        cls._save_last_hash(current_hash)

        return backup_path

    @classmethod
    def restore_backup(cls, backup_path):
        copyfile(backup_path, DB_PATH)

    # Placeholder for future online backup
    @classmethod
    def backup_online(cls):
        raise NotImplementedError("Online backup not configured yet")
