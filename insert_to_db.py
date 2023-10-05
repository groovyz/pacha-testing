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

engine = create_engine(os.environ["AzureCosmosDBString"])
References.metadata.create_all(engine)
factory = sessionmaker(bind=engine)
session = factory()



	