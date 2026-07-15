from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Optional,List,Dict
import time
import json
from datetime import datetime,UTC
from pipeline import predict_and_explain
from database import log_prediction,init_db,SessionLocal,PredictionLog
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app:FastAPI):
    # Startup
    init_db()
    print("Database initialized")
    yield

app=FastAPI(title='Fraud Intelligence Platform',
            description='Explainable fraud detection with SHAP narratives and compliance-mapped audit logging',
            version="1.0.0",lifespan=lifespan,)

class TransactionRequest(BaseModel):
    # Required core
    TransactionID:int
    TransactionDT:int
    TransactionAmt:float=Field(...,gt=0)
    ProductCD:str
    card1:int

    # Card metadata (optional)
    card2:Optional[float]=None
    card3:Optional[float]=None
    card4:Optional[str]=None
    card5:Optional[float]=None
    card6:Optional[str]=None

    # Address
    addr1:Optional[float]=None
    addr2:Optional[float]=None
    dist1:Optional[float]=None
    dist2:Optional[float]=None

    # Email
    P_emaildomain:Optional[str]=None
    R_emaildomain:Optional[str]=None

    # Device
    DeviceType:Optional[str]=None

    # C1-C14
    C1:Optional[float]=None
    C2:Optional[float]=None
    C3:Optional[float]=None
    C4:Optional[float]=None
    C5:Optional[float]=None
    C6:Optional[float]=None
    C7:Optional[float]=None
    C8:Optional[float]=None
    C9:Optional[float]=None
    C10:Optional[float]=None
    C11:Optional[float]=None
    C12:Optional[float]=None
    C13:Optional[float]=None
    C14:Optional[float]=None

    # D1-D15
    D1:Optional[float]=None
    D2:Optional[float]=None
    D3:Optional[float]=None
    D4:Optional[float]=None
    D5:Optional[float]=None
    D6:Optional[float]=None
    D7:Optional[float]=None
    D8:Optional[float]=None
    D9:Optional[float]=None
    D10:Optional[float]=None
    D11:Optional[float]=None
    D12:Optional[float]=None
    D13:Optional[float]=None
    D14:Optional[float]=None
    D15:Optional[float]=None

    # --- M1-M9 (match flags, T/F strings — mapped downstream)
    M1: Optional[str] = None
    M2: Optional[str] = None
    M3: Optional[str] = None
    M4: Optional[str] = None
    M5: Optional[str] = None
    M6: Optional[str] = None
    M7: Optional[str] = None
    M8: Optional[str] = None
    M9: Optional[str] = None

    # --- id_ numeric (passed through raw) ---
    id_01: Optional[float] = None
    id_02: Optional[float] = None
    id_03: Optional[float] = None
    id_04: Optional[float] = None
    id_05: Optional[float] = None
    id_06: Optional[float] = None
    id_07: Optional[float] = None
    id_08: Optional[float] = None
    id_09: Optional[float] = None
    id_10: Optional[float] = None
    id_11: Optional[float] = None
    id_13: Optional[float] = None
    id_14: Optional[float] = None
    id_17: Optional[float] = None
    id_18: Optional[float] = None
    id_19: Optional[float] = None
    id_20: Optional[float] = None
    id_21: Optional[float] = None
    id_22: Optional[float] = None
    id_24: Optional[float] = None
    id_25: Optional[float] = None
    id_26: Optional[float] = None
    id_32: Optional[float] = None

    # --- id_ categorical (freq-encoded in feature_engineering.py) ---
    id_12: Optional[str] = None
    id_15: Optional[str] = None
    id_16: Optional[str] = None
    id_23: Optional[str] = None
    id_27: Optional[str] = None
    id_28: Optional[str] = None
    id_29: Optional[str] = None
    id_30: Optional[str] = None
    id_31: Optional[str] = None
    id_33: Optional[str] = None
    id_34: Optional[str] = None
    id_35: Optional[str] = None
    id_36: Optional[str] = None
    id_37: Optional[str] = None
    id_38: Optional[str] = None

    generate_narrative: bool = True

class FeatureContribution(BaseModel):
    feature: str
    shap_value: float
    abs_impact: float

class RiskGroup(BaseModel):
    category: str
    features: List[FeatureContribution]
    narrative: str
    fatf_ref: str
    uk_ref: str

class RiskTier(BaseModel):
    tier:str
    action:str
    color_code:Optional[str]=None

class NarrativeOutput(BaseModel):
    investigation_brief:str
    compliance_notice:Optional[str]
    risk_tier:str
    full_narrative:str
    narrative_source:Optional[str]=None

class PredictionResponse(BaseModel):
    transaction_id:int
    fraud_score:float
    is_fraud:bool
    risk_tier:RiskTier
    risk_themes:List[str]=[]
    top_shap:List[RiskGroup]
    narrative:Optional[NarrativeOutput]
    model_version:str
    pipeline_latency_ms:float

startup_time=datetime.now(UTC)

@app.get("/health")
def health():
    return{
        "status":"healthy",
        "model_version":"fraud_rf_ieee",
        "mlflow_run_id":"77a03c013a734d1097ae7a4131fc519b",
        "uptime_seconds":(datetime.now(UTC)-startup_time).seconds,
        "timestamp":datetime.now(UTC).isoformat()
    }



@app.post("/predict",response_model=PredictionResponse)
def predict(request:TransactionRequest):
    txn=request.model_dump()
    generate_narrative=txn.pop("generate_narrative")

    try:
        result=predict_and_explain(txn,generate_narrative=generate_narrative)
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    try:
        log_prediction(result)
    except Exception as e:
        print(f"Audit log failed: {e}")
    
    return result



@app.get("/predictions")
def get_predictions(limit:int=20):
    db=SessionLocal()
    rows=(db.query(PredictionLog).order_by(PredictionLog.timestamp.desc()).limit(limit).all())
    db.close()

    return [
        {
            "id":r.id,
            "transaction_id":r.transaction_id,
            "timestamp":r.timestamp.isoformat(),
            "is_fraud":r.is_fraud,
            "fraud_score":r.fraud_score,
            "risk_tier":r.risk_tier,
            "model_version":r.model_version,
            "top_shap":json.loads(r.shap_json)if r.shap_json else [],
            "narrative":json.loads(r.narrative) if r.narrative else None,
        }
        for r in rows
    ]
