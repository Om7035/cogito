import json
import time

class AuditLogger:
    def __init__(self, filepath):
        self.filepath = filepath

    def log(self, event_type, data):
        entry = {
            "timestamp": time.time(),
            "event": event_type,
            "data": data
        }
        with open(self.filepath, "a", encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
