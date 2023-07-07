from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from typing import Annotated
import models
import schemas
from utils import (
    get_password_hash,
    verify_password,
    verify_email,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM
)
from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, user_id: int) -> models.User:
    """
    Returns user by id from db.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_username(db: Session, username: str) -> models.User:
    """
    Returns user by username from db.
    """
    user = db.query(
        models.User).filter(models.User.username == username).first()
    return user


def get_users(
        db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """
    Returns all users from db.
    """
    return db.query(models.User).offset(skip).limit(limit).all()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """
    Returns current user from db using jwt token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    """
    Returns current user if he isn't disabled.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate user by password.
    Returns user.
    """
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, user: schemas.UserCreate):
    """
    Creating new user in db;
    Returns new user.
    """
    if not verify_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Can't verify email '{user.email}'"
        )
    hashed_password = get_password_hash(user.password)
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This username or email already registered"
        )


def get_posts(
    db: Session,
    user: schemas.User,
    skip: int = 0,
    limit: int = 100,
):
    """
    Returns all posts from db
    if user is authorized.
    """
    if not get_user(db, user.id):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view posts"
        )
    return db.query(models.Post).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    """
    Returns post from db by id.
    """
    return db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()


def create_user_post(db: Session, post: schemas.PostCreate, user_id: int):
    """
    Creates new post to db;
    Returns new post.
    """
    try:
        db_post = models.Post(**post.dict(), author_id=user_id)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Post with this title already exists"
        )


def update_post(
    db: Session,
    post_id: int,
    post: schemas.PostCreate,
    current_user: schemas.User
) -> models.Post:
    """
    Updates post in db.
    Returns post.
    """
    db_post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    elif db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to edit this post"
        )
    else:
        for key, value in post.dict().items():
            setattr(db_post, key, value)
        db.commit()
        db.refresh(db_post)
        return db_post


def delete_post(
    post_id: int,
    current_user: schemas.User,
    db: Session
) -> dict:
    """
    Deletes post from db.
    Returns status {'Deleted': True}.
    """
    db_post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()
    if not db_post:
        raise HTTPException(
            status_code=404,
            detail="Post id {post_id} not found"
        )
    elif db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this post"
        )
    else:
        db.delete(db_post)
        db.commit()
        return {'Deleted': True}


def update_like(
    post_id: int,
    current_user: schemas.User,
    db: Session
) -> None:
    """
    Adds like to post from current user
    if there is no like and current user isn't author;
    If there is a like from current user deletes it.
    """
    db_post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not db_post:
        raise HTTPException(
            status_code=404,
            detail=f"Post {post_id} not found"
        )
    elif db_post.author_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot like your own post"
        )
    else:
        if current_user not in db_post.user_likes:
            db_post.user_likes.append(current_user)
            db.commit()
            db.refresh(db_post)
        else:
            db_post.user_likes.remove(current_user)
            db.commit()
            db.refresh(db_post)
    return db_post
