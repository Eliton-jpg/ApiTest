# Fast-Api
Esse réposito é dedicado para o desenvolvimento de uma simples Api em python utlizando Fast-Api.
## Main.py
A main.py define uma API usando o FastAPI que interage com um banco de dados SQLAlchemy para gerenciar registros de pessoas. A API tem endpoints para criar, ler, atualizar e deletar pessoas no banco de dados. Além disso, inclui um endpoint /health para verificar a saúde da aplicação.
### Resumo dos Endpoints:
- POST /people/: Cria uma nova pessoa.
- GET /people/: Lista todas as pessoas, com paginação.
- GET /people/{person_id}: Lê uma pessoa específica pelo ID.
- PUT /people/{person_id}: Atualiza os dados de uma pessoa pelo ID.
- DELETE /people/{person_id}: Deleta uma pessoa pelo ID.
- GET /health: Retorna o status "ok" para indicar que o serviço está funciona

~~~python
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

@app.get("/health")
def health_check():
    return {"status": "ok"}
~~~