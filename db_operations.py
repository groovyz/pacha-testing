from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, select, String
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
    engine = create_engine(os.environ["CosmosDbConnectionString"])
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
    print("INSERTED ALL ITEMS FROM Q&AS, SESSION CLOSED")

def get_closest_neighbors_of(embedded_qs):
    qs_and_similar = []
    session = db_connect()
    for question in embedded_qs:
        similar = session.scalars(select(References).order_by(References.embedding.cosine_distance(question["embedding"])).limit(3))
        similar_qs = []
        similar_as = []
        for reference in similar.all():
            similar_qs.append(reference.question)
            similar_as.append(reference.answer)
        qs_and_similar.append({"question": question["question"], "similiar-questions": similar_qs, "similar-answers": similar_as})
    session.close()
    print("GET CLOSEST NEIGHBORS SUCCEEDED, SESSION CLOSED")
    return qs_and_similar