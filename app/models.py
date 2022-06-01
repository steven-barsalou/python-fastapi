from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null, text
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

#classes in python are uppercase
#each of these classes defines a table in the database

class Post(Base): #the class Post extends Base class which is a SQLAlchemy model
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('Now()'))

    user = relationship("User") #this will return the user with the post when it is queries, it will come back as a nested JSON object


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('Now()'))

class Vote(Base):
    __tablename__ = "votes"
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)