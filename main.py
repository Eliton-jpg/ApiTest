from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from database import SessionLocal, engine, Base
from models import Person as PersonModel
from pydantic import BaseModel

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic
class PersonBase(BaseModel):
    nome: str
    cidade: str

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int

    class Config:
        from_attributes = True

# Métricas Prometheus
REQUEST_COUNT = Counter('fastapi_request_count', 'Total number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('fastapi_request_latency_seconds', 'Request latency', ['endpoint'])

# Middleware para contar as requisições
@app.middleware("http")
async def add_metrics_middleware(request, call_next):
    endpoint = request.url.path
    method = request.method
    with REQUEST_LATENCY.labels(endpoint).time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method, endpoint).inc()
    return response

# Criar uma nova pessoa
@app.post("/people/", response_model=Person)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    db_person = PersonModel(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# Ler todas as pessoas
@app.get("/people/", response_model=List[Person])
def read_people(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    people = db.query(PersonModel).offset(skip).limit(limit).all()
    return people

# Ler uma pessoa pelo ID
@app.get("/people/{person_id}", response_model=Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

# Atualizar uma pessoa pelo ID
@app.put("/people/{person_id}", response_model=Person)
def update_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    db_person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    for key, value in person.dict().items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person

# Deletar uma pessoa pelo ID
@app.delete("/people/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(db_person)
    db.commit()
    return {"detail": "Person deleted"}

# Endpoint de saúde
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoint para expor métricas para o Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
