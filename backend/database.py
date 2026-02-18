from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel,Session, create_engine

postgres_database_url = 'postgresql://postgres:postgres123@localhost/fastapi'
engine = create_engine(
    postgres_database_url,
    echo=True,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("database tables created")
    
def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
            
SessionDep = Annotated[Session, Depends(get_session)]