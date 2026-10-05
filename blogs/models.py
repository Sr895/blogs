from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    blogs = relationship('Blog', back_populates='author')

class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    is_published = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    author = relationship('User', back_populates='blogs')