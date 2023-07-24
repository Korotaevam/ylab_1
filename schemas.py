from pydantic import BaseModel
from typing import Optional
from uuid import UUID


# Схема для модели Menu
class MenuBase(BaseModel):
    title: str
    description: Optional[str] = None
    submenus_count: Optional[int] = None
    dishes_count: Optional[int] = None


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    pass


class Menu(MenuBase):
    id: UUID

    class Config:
        from_attributes = True


# Схема для модели Submenu
class SubmenuBase(BaseModel):
    title: str
    description: Optional[str] = None
    dishes_count: Optional[int] = None


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuUpdate(SubmenuBase):
    pass


class Submenu(SubmenuBase):
    id: UUID

    class Config:
        from_attributes = True


# Схема для модели Dish
class DishBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: str
    # submenu_id: UUID


# class DishCreate(DishBase):
#     pass

class DishCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: str


class DishUpdate(DishBase):
    pass


class Dish(DishBase):
    id: UUID

    class Config:
        from_attributes = True
