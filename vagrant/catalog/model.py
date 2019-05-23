from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
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
    # user = relationship('User', backref=backref('categories', cascade='all, delete-orphan'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name
        }





class Item(Base):
    __tablename__ = 'item'


    item_id = Column(Integer, primary_key = True)
    item_name =Column(String(80), nullable = False)
    item_description = Column(String)
    item_price = Column(String(20))
    item_date = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey('category.category_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    category = relationship('Category', backref=backref('items', cascade='all, delete-orphan'))
    # user = relationship('User', backref=backref('items', cascade='all, delete-orphan'))


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'item_name': self.item_name,
           'item_description': self.item_description,
           'item_id': self.item_id,
           'item_price': self.item_price,
           'item_date': self.item_date,
           'user_id': self.user_id,
           'category_id': self.category_id
       }



engine = create_engine('sqlite:///antiques.db')
 

Base.metadata.create_all(engine)