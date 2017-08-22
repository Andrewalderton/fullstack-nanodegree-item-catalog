import sys
import os

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'



engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
