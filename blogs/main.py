from fastapi import FastAPI, status, HTTPException, Depends
from schemas import Blog, User, BlogResponse, UserResponseAll, UserLoginRequest
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from utils import hash_password, verify_password
from typing import List

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# blogs = [
#     {
#         "id": 1,
#         "title": "Getting Started with FastAPI",
#         "content": "FastAPI is a modern, fast web framework for building APIs with Python based on standard type hints.",
#         "is_published": False
#     },
#     {
#         "id": 2,
#         "title": "Understanding Python Decorators",
#         "content": "Decorators allow you to modify the behavior of a function or class without changing its source code.",
#         "is_published": True
#     },
#     {
#         "id": 3,
#         "title": "Async Programming in Python",
#         "content": "Learn how async and await work in Python to write concurrent code using asyncio.",
#         "is_published": True
#     },
#     {
#         "id": 4,
#         "title": "Introduction to Pydantic Models",
#         "content": "Pydantic uses Python type annotations to validate data and manage settings in your applications.",
#         "is_published": False
#     },
#     {
#         "id": 5,
#         "title": "Deploying FastAPI with Docker",
#         "content": "A step-by-step guide to containerizing your FastAPI application and deploying it with Docker.",
#         "is_published": True
#     }
# ]

# @app.get('/blogs')
# def get_blogs():
#     return {
#         'blogs': blogs
#     }

# @app.post('/blogs', status_code=status.HTTP_200_OK)
# def create_blog(blog: Blog):
#     blog_dict = blog.model_dump()
#     blog_dict['id'] = len(blogs) + 1
#     blogs.append(blog_dict)
#     return blog_dict

# @app.put('/blogs/{blog_id}')
# def update_blog(blog_id: int, payload: Blog):
#     for blog in blogs:
#         if blog['id'] == blog_id:
#             payload_dict = payload.model_dump()
#             blog.update(payload_dict)
#             return blog
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')

# @app.delete('/blogs/{blog_id}')
# def delete_blog(blog_id: int):
#     for index, blog in enumerate(blogs):
#         if blog['id'] == blog_id:
#             blogs.pop(index)
#             return { 'message': 'Blog deleted successfully' }
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/blogs', tags=['Blogs'], response_model=List[BlogResponse])
def get_blogs(db: Session = Depends(get_db)):
    return db.query(models.Blog).all()

@app.post('/blogs', status_code=status.HTTP_200_OK, tags=['Blogs'])
def create_blog(blog: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(**blog.model_dump())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.put('/blogs/{blog_id}', tags=['Blogs'])
def update_blog(blog_id: int, blog: Blog, db: Session = Depends(get_db)):
    blog_db = db.query(models.Blog).get(blog_id)
    if not blog_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Blog not found')
    else:
        blog_dict = blog.model_dump()
        for key, value in blog_dict.items():
            setattr(blog_db, key, value)
        db.commit()
        db.refresh(blog_db)
        return blog_db

@app.delete('/blogs/{blog_id}', tags=['Blogs'])
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog_db = db.query(models.Blog).get(blog_id)
    if not blog_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Blog not found')
    else:
        db.delete(blog_db)
        db.commit()
        return { 'message': 'Deleted blog successfully' }

@app.post('/users', status_code=status.HTTP_200_OK, tags=['Users'])
def create_user(user: User, db: Session = Depends(get_db)):
    existing_user = db.query(models.Blog).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist with this email.')
    else:
        hashed_password = hash_password(user.password)
        user_dict = user.model_dump()
        user_dict['password'] = hashed_password
        new_user = models.User(**user_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

@app.get('/users', tags=['Users'], response_model=List[UserResponseAll])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post('/users/login', tags=['Users'])
def login_user(user: UserLoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    is_password_correct = verify_password(user.password, db_user.password)

    if not is_password_correct:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password')

# ACCESS TOKEN - JWT - Expiry time