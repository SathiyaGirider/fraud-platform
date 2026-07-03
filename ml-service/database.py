from sqlalchemy import create_engine,Column,String,Float,Boolean,Integer,DateTime,Text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker
import os
import json
from datetime import datetime,UTC

DATABASE_URL =os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:password@localhost:5432/fraud_platform'
)
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class PredictionLog(Base):
    """
    Audit log table — every API call logged with full context.
    shap_json stores the FLAT, ungrouped SHAP output (top_shap_flat from
    pipeline.py) — grouping by risk category is presentation logic and
    happens only in the API response, never in this table.
    """

    __tablename__="prediction_log"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    transaction_id:Mapped[str]=mapped_column(String(50),nullable=False,index=True)
    timestamp:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(UTC),index=True)
    fraud_score: Mapped[float]=mapped_column(Float, nullable=False)
    is_fraud: Mapped[bool]=mapped_column(Boolean, nullable=False)
    risk_tier: Mapped[str]=mapped_column(String(20))
    model_version: Mapped[str]=mapped_column(String(50))

    shap_json: Mapped[str]=mapped_column(Text)   # json.dumps(top_shap_flat)
    narrative: Mapped[str]=mapped_column(Text)   # json.dumps(narrative dict)
    pipeline_latency_ms: Mapped[float]=mapped_column(Float)

def init_db():
    # Create tables if they dont exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

def log_prediction(result:dict):
    """
    Write a prediction result to the audit log.
    Expects result['top_shap_flat'] — the flat list from pipeline.py,
    not the grouped 'top_shap' used in the API response.
    """
    db=SessionLocal()
    try:
        log=PredictionLog(
            transaction_id=result['transaction_id'],
            fraud_score=result['fraud_score'],
            is_fraud=result['is_fraud'],
            risk_tier=result['risk_tier']['tier'],
            model_version=result['model_version'],
            shap_json=json.dumps(result['top_shap_flat']),
            narrative=json.dumps(result.get('narrative')),
            pipeline_latency_ms=result.get('pipeline_latency_ms'),
        )    
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

