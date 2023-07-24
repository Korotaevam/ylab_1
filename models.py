from sqlalchemy.orm import relationship
from config import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    submenus = relationship("Submenu", cascade="all, delete-orphan")


class Submenu(Base):
    __tablename__ = 'submenu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id'), nullable=False)
    dishes = relationship("Dish", cascade="all, delete-orphan")


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(String(255), nullable=False)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenu.id'), nullable=False)

