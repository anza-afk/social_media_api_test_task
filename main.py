from typing import Annotated
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import schemas
import models
import crud
from database import engine
from utils import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(crud.get_db),
):
    user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(crud.get_db),
):
    return crud.create_user(db=db, user=user)


@app.get("/users/me", response_model=schemas.UserOut)
async def read_users_me(
    current_user: Annotated[schemas.UserBase, Depends(
        crud.get_current_active_user)]
):
    return current_user


@app.get("/posts/", response_model=list[schemas.PostOut])
def get_posts(
    current_user: Annotated[schemas.User, Depends(
        crud.get_current_active_user)],  # <---
    skip=0,
    limit=100,
    db: Session = Depends(crud.get_db),
):
    return crud.get_posts(db, current_user, skip, limit)


@app.get('/posts/{post_id}', response_model=schemas.PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(crud.get_db)
) -> models.Post:
    return crud.get_post(db=db, post_id=post_id)


@app.post("/posts/", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    current_user: Annotated[schemas.User, Depends(
        crud.get_current_active_user)],
    db: Session = Depends(crud.get_db),
):
    return crud.create_user_post(db=db, post=post, user_id=current_user.id)


@app.put("/posts/{post_id}", response_model=schemas.Post)
def edit_post(
    post_id: int,
    post: schemas.PostCreate,
    current_user: Annotated[schemas.User, Depends(
        crud.get_current_active_user)],
    db: Session = Depends(crud.get_db)
):
    return crud.update_post(
        db=db,
        post_id=post_id,
        post=post,
        current_user=current_user
    )


@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: Annotated[schemas.User, Depends(
        crud.get_current_active_user)],
    db: Session = Depends(crud.get_db)
):
    return crud.delete_post(db=db, current_user=current_user, post_id=post_id)


@app.post("/posts/{post_id}/like", response_model=schemas.PostOut)
def like_post(
    post_id: int,
    current_user: Annotated[schemas.User, Depends(
        crud.get_current_active_user)],
    db: Session = Depends(crud.get_db)
):
    return crud.update_like(post_id, current_user, db)
