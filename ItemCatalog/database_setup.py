import sys
import random
import string
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# get Base class
Base = declarative_base()
                     
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(250), nullable = False, index = True)
    
class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id"))
    def_by_user = relationship(User)
    name = Column(String(80), nullable = False)

class LearningItem(Base):
    __tablename__ = "to_learn"
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer, ForeignKey("category.id"))
    in_category = relationship(Category)
    name = Column(String(80), nullable = False)
    description = Column(String())
    done = Column(Boolean, default = False)

class Resource(Base):
    __tablename__ = "resource"
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    url = Column(String(250))
    item_id = Column(Integer, ForeignKey("to_learn.id"))
    for_item = relationship(LearningItem)
    
# point to database that will be used
# creates new file that can be used similarly to a db
engine = create_engine("sqlite:///tolearn.db")
# create classes as db tables
Base.metadata.create_all(engine)
