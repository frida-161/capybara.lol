"""Database Models."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Date,
    ForeignKey)
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import select

from app.helpers import generate_filename

Base = declarative_base()

class Capybara(Base):
    """Model for our capybara content."""
    __tablename__ = 'capybaras'

    id = Column(Integer(), primary_key=True)
    date = Column(Date(), nullable=False)
    filename = Column(String(), nullable=False)
    user_id = Column(Integer(), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='capybaras')
    cute_votes = Column(Integer())
    funny_votes = Column(Integer())


class User(UserMixin, Base):
    """Model for our users."""
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(120))
    superuser = Column(Boolean(), nullable=False)
    capybaras = relationship('Capybara', back_populates='user')

    def set_password(self, password):
        """Set the password for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the users password."""
        return check_password_hash(self.password_hash, password)