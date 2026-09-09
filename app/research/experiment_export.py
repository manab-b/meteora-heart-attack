from __future__ import annotations
import json
from dataclasses import asdict

def to_json(rows, path: str) -> None:
    payload=[]
    for row in rows:
        item={"strategy":asdict(row.strategy),"train":row.train,"test":row.test,"robust":row.robust}
        payload.append(item)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(payload,f,ensure_ascii=False,indent=2,sort_keys=True)
