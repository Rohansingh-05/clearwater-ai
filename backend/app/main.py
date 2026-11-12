from pathlib import Path
import json, sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import WaterSample
from .wqi import calculate_wqi
from .ml import predict
from .train_model import MODELS, train_and_save

DB=Path(__file__).resolve().parents[1]/"water_quality.db"
app=FastAPI(title="Water Quality AI API",version="1.0.0",
            description="Traditional WQI and AI category prediction.")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
                   allow_methods=["*"],allow_headers=["*"])

def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

@app.on_event("startup")
def startup():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, sample_name TEXT,
        input_json TEXT, wqi_score REAL, wqi_category TEXT, ai_category TEXT,
        ai_confidence REAL, result_json TEXT)""")
    if not (MODELS/"metrics.json").exists(): train_and_save()

@app.get("/")
def root(): return {"message":"Water Quality AI API","docs":"/docs"}

@app.get("/api/health")
def health(): return {"status":"ok","service":"Water Quality AI API"}

@app.get("/api/model-metrics")
def model_metrics():
    if not (MODELS/"metrics.json").exists(): train_and_save()
    return json.loads((MODELS/"metrics.json").read_text())

@app.post("/api/analyze")
def analyze(sample:WaterSample):
    data=sample.model_dump(); wqi=calculate_wqi(data); ai=predict(data)
    result={"sample":data,"wqi":wqi,"ai":ai,
      "comparison":{"same_category":wqi["category"]==ai["primary"]["category"],
      "message":"Both methods returned the same category." if wqi["category"]==ai["primary"]["category"] else "The methods differ. Review measurements and consider laboratory testing."},
      "safety_notice":"This educational result is not a drinking-water safety certificate. Laboratory testing and regulatory confirmation are required."}
    now=datetime.now(timezone.utc).isoformat()
    with connect() as c:
        cur=c.execute("INSERT INTO analyses(created_at,sample_name,input_json,wqi_score,wqi_category,ai_category,ai_confidence,result_json) VALUES(?,?,?,?,?,?,?,?)",
          (now,data["sample_name"],json.dumps(data),wqi["score"],wqi["category"],ai["primary"]["category"],ai["primary"]["confidence"],"{}"))
        result["record_id"]=cur.lastrowid
        c.execute("UPDATE analyses SET result_json=? WHERE id=?",(json.dumps(result),cur.lastrowid))
    return result

@app.get("/api/history")
def history(limit:int=30):
    limit=max(1,min(limit,100))
    with connect() as c:
        rows=c.execute("SELECT id,created_at,sample_name,wqi_score,wqi_category,ai_category,ai_confidence FROM analyses ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return [dict(r) for r in rows]

@app.delete("/api/history")
def clear_history():
    with connect() as c: c.execute("DELETE FROM analyses")
    return {"message":"History cleared"}

@app.get("/api/history/{record_id}")
def history_item(record_id:int):
    with connect() as c: row=c.execute("SELECT result_json FROM analyses WHERE id=?",(record_id,)).fetchone()
    if not row: raise HTTPException(404,"Record not found")
    return json.loads(row["result_json"])
