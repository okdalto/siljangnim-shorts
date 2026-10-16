"""Atomic JSON writes and revision conflict errors for the skill workspace."""
import json
import os
import uuid
from datetime import datetime, timezone


def now(): return datetime.now(timezone.utc).isoformat()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    os.replace(tmp,path)


class Conflict(ValueError): pass
