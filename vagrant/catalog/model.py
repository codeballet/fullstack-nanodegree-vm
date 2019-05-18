from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(250), nullable=False)
    user_email = Column(String(250), nullable=False)
    user_picture = Column(String(250))
        

class Category(Base):
    __tablename__ = 'category'
   
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(80), nullable=False)
 

class Item(Base):
    __tablename__ = 'item'


    item_id = Column(Integer, primary_key = True)
    item_name =Column(String(80), nullable = False)
    item_description = Column(String)
    item_price = Column(String(20))
    category_id = Column(Integer,ForeignKey('category.category_id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship(User)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name': self.item_name,
           'description': self.item_description,
           'id': self.item_id,
           'price': self.item_price,
           'user_id': self.user_id,
           'category_id': self.category_id
       }



engine = create_engine('sqlite:///antiques.db')
 

Base.metadata.create_all(engine)