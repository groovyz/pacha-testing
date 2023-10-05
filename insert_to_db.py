from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
import os

Base = declarative_base()

class References(Base):
	__tablename__ = "references"
	id: Mapped[int] = mapped_column(primary_key=True)
	folder: Mapped[str] = mapped_column(String(100))
	question: Mapped[str] = mapped_column(String(64000))
	answer: Mapped[str] = mapped_column(String(64000))
	embedding = mapped_column(Vector(1536))
	
def db_connect():
    engine = create_engine(os.environ["AzureCosmosDBString"])
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    return session

def insert_into_database(embedded_qas, path):
    session = db_connect()
    for item in embedded_qas:
        new_reference = References(folder=path, question=item["question"], answer=item["answer"], embedding=item["embedding"])
        session.add(new_reference)
        session.commit()
    session.close()
    return "INSERTED ALL ITEMS FROM Q&AS, SESSION CLOSED"





	