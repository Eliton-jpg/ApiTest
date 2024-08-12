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

## Banco de Dados
O banco de dados adotado nesse código fora feito utilizando SQLAlchemy, dividi em dois arquivos
 ### Database.py 
 Este arquivo é responsável por configurar a conexão com o banco de dados e fornecer as ferramentas necessárias para interagir com ele.
 ~~~python
 from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
 ~~~
### Models.py
Este arquivo define as classes de modelo que representam as tabelas do banco de dados. No SQLAlchemy, essas classes são mapeadas diretamente para tabelas no banco de dados.
~~~python
from sqlalchemy import Column, Integer, String
from database import Base

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cidade = Column(String, index=True)
~~~
# Continuous Integration
 Fora feito um GitHub Actions, para fazer a integração continua da imagem Docker na Arquitetura da Aplicação
 ˋˋˋ
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Check out the repository
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USER }}/docker-fastapi-app:latest
            ${{ secrets.DOCKERHUB_USER }}/docker-fastapi-app:${{ github.run_number }}

      - name: Check out GitOps repo
        uses: actions/checkout@v3
        with:
          repository: Eliton-jpg/Gitops
          token: ${{ secrets.GITOPS_REPO_ACCESS_TOKEN }}
          path: gitops-repo

      - name: Update image tag and repository in values.yaml
        run: |
          sed -i 's|repository:.*|repository: '${{ secrets.DOCKERHUB_USER }}/docker-fastapi-app'|' gitops-repo/my-api/values.yaml
          sed -i 's|tag:.*|tag: "${{ github.run_number }}"|' gitops-repo/my-api/values.yaml

      - name: Commit and push changes
        working-directory: gitops-repo
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add my-api/values.yaml
          git commit -m "Update image repository and tag to ${{ secrets.DOCKERHUB_USER }}/docker-fastapi-app:${{ github.run_number }}"
          git push origin main
 ˋˋˋ
# Continuous Deployment
## Preparação do Ambiente:
- Minikube foi utilizado como ambiente de Kubernetes local para facilitar o desenvolvimento e testes. Ele foi iniciado para criar um cluster Kubernetes em uma máquina local.
  
- Argo CD, uma ferramenta declarativa de GitOps, foi instalada no cluster Minikube. O Argo CD permite gerenciar o estado das aplicações Kubernetes a partir de repositórios Git.
  
- Um repositório privado do GitHub foi configurado para armazenar os manifests de Kubernetes (Helm Charts) necessários para o deploy da aplicação
## Configuração do Repositório e Autenticação:
- Um par de chaves SSH foi gerado e configurado para permitir que o Argo CD acessasse o repositório privado do GitHub de forma segura.
- As chaves SSH foram adicionadas ao Argo CD como um segredo no cluster Kubernetes, permitindo a autenticação automática para clonar o repositório privado.
  
## Configuração do Argo CD:
- Dentro do Argo CD, foi criada uma nova aplicação apontando para o repositório privado onde os Helm Charts estão armazenados.
- O Argo CD foi configurado para monitorar as alterações nesse repositório e sincronizar automaticamente o estado do cluster Kubernetes com os manifests presentes no repositório.
- A aplicação no Argo CD foi configurada para usar o repositório privado, especificando o caminho do Helm Chart e a branch correta.
![ArgoCd Aplication](ApiTest\imagens\imagem.png)