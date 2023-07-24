from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from config import SessionLocal
from uuid import UUID

app = FastAPI(title="Restaurant")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Определяем CRUD операции для модели Menu

@app.get("/api/v1/menus", response_model=List[schemas.Menu])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = db.query(models.Menu).offset(skip).limit(limit).all()
    return menus


@app.post("/api/v1/menus", response_model=schemas.Menu, status_code=status.HTTP_201_CREATED)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@app.get("/api/v1/menus/{menu_id}", response_model=schemas.Menu)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    submenus_count = db.query(models.Submenu).join(models.Menu).filter(models.Menu.id == menu_id).count()
    dishes_count = db.query(models.Dish).join(models.Submenu).join(models.Menu).filter(
        models.Menu.id == menu_id).count()
    return {"id": db_menu.id, "title": db_menu.title, "description": db_menu.description,
            "submenus_count": submenus_count, "dishes_count": dishes_count}


@app.patch("/api/v1/menus/{menu_id}", response_model=schemas.Menu)
def update_menu(menu_id: UUID, menu: schemas.MenuUpdate, db: Session = Depends(get_db)):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    for field, value in menu.dict(exclude_unset=True).items():
        setattr(db_menu, field, value)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@app.delete("/api/v1/menus/{menu_id}")
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    db.delete(db_menu)
    db.commit()
    return {"message": "Menu deleted successfully"}


# Определяем CRUD операции для модели Submenu
@app.get("/api/v1/menus/{menu_id}/submenus", response_model=List[schemas.Menu])
def get_submenus(menu_id: UUID, db: Session = Depends(get_db)):
    db_submenus = db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).all()
    return db_submenus


@app.post("/api/v1/menus/{menu_id}/submenus", status_code=status.HTTP_201_CREATED)
def create_submenu(menu_id: UUID, submenu: schemas.SubmenuBase, db: Session = Depends(get_db)):
    db_submenu = models.Submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.Submenu)
def read_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id,
                                                 models.Submenu.menu_id == menu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    dishes_count = db.query(models.Dish).join(models.Submenu).filter(models.Submenu.id == submenu_id).count()
    return {"id": db_submenu.id, "title": db_submenu.title, "description": db_submenu.description,
            "menu_id": db_submenu.menu_id, "dishes_count": dishes_count}


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.Submenu)
def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: schemas.SubmenuUpdate, db: Session = Depends(get_db)):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id,
                                                 models.Submenu.menu_id == menu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    for field, value in submenu.dict(exclude_unset=True).items():
        setattr(db_submenu, field, value)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id,
                                                 models.Submenu.menu_id == menu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    db.delete(db_submenu)
    db.commit()

    return {"message": "Submenu and all associated dishes deleted successfully"}


# Определяем CRUD операции для модели Dish
@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[schemas.Dish])
def read_dishes(menu_id: UUID, submenu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dishes = db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id,
                                          models.Submenu.menu_id == menu_id).offset(skip).limit(limit).all()
    return dishes


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=schemas.Dish,
          status_code=status.HTTP_201_CREATED)
def create_dish(menu_id: UUID, submenu_id: UUID, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    db_dish = models.Dish(title=dish.title, description=dish.description, price=str(dish.price), submenu_id=submenu_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)

    # Возвращаем объект модели schemas.Submenu
    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(round(float(db_dish.price), 2))), 'submenu_id': db_dish.submenu_id}


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    db_dish = db.query(models.Dish). \
        join(models.Submenu). \
        join(models.Menu). \
        filter(models.Dish.id == dish_id). \
        filter(models.Submenu.id == submenu_id). \
        filter(models.Menu.id == menu_id). \
        first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")

    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(db_dish.price)), 'submenu_id': db_dish.submenu_id}


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: schemas.DishUpdate,
                db: Session = Depends(get_db)):
    db_dish = db.query(models.Dish). \
        join(models.Submenu). \
        join(models.Menu). \
        filter(models.Dish.id == dish_id). \
        filter(models.Submenu.id == submenu_id). \
        filter(models.Menu.id == menu_id). \
        first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    for field, value in dish.dict(exclude_unset=True).items():
        setattr(db_dish, field, value)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return {"id": db_dish.id, "title": db_dish.title, "description": db_dish.description,
            "price": str(float(db_dish.price)), 'submenu_id': db_dish.submenu_id}


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    db_dish = db.query(models.Dish). \
        join(models.Submenu). \
        join(models.Menu). \
        filter(models.Dish.id == dish_id). \
        filter(models.Submenu.id == submenu_id). \
        filter(models.Menu.id == menu_id). \
        first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    db.delete(db_dish)
    db.commit()
    return {"message": "Dish deleted successfully"}
