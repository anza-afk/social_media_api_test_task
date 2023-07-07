from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: bool | None = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class UserOut(User):
    posts: list[Post] = []
    post_likes: list[Post] = []


class PostOut(Post):
    user_likes: list[User]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
