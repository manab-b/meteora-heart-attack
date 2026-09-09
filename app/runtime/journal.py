from __future__ import annotations
import json
def trade_event(event_type:str,**fields)->str:
    return json.dumps({"event":event_type,**fields},separators=(",",":"),sort_keys=True)
