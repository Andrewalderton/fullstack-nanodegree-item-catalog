import sys
import os

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=False)
    img = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return book data in serializable format
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'img': self.img,
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)