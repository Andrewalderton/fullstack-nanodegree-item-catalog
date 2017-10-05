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
    picture = Column(String)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String)
    img = Column(String)
    category = Column(Integer, ForeignKey('categories.id'), nullable=False)
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
            'category': self.category.name,
            'img': self.img
        }


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    book = relationship(Book, single_parent=True, cascade="all, delete-orphan")

    @property
    def serialize(self):
	    # return category data in serializable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

engine = create_engine('postgres://cppuchkbswutrx:2ca2a869db9b201d744f563bb5ddf63eb5159ad9c1ef9cc11e3d2aa070fa6663@ec2-23-21-88-45.compute-1.amazonaws.com:5432/dekf8akjo5gdgk')

Base.metadata.create_all(engine)

print('db configured')
