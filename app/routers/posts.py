from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app import oath2
from .. import models, schemas, oath2
from ..database import get_db

#this prefixes all of the decorators in this file with /post
#prefix =  a prefix to the url path in the decorator
#tags = a logical grouping in the swagger documentation at <api_url>/docs
router = APIRouter(prefix="/posts", tags=['Posts'])

#posts, will return all of the posts in json
@router.get("/", response_model=List[schemas.PostWithVote]) #List creates a list of class PostResponse
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""): #here the limit is a query parameter that can be added in the url such as http://myurl.com/posts?limit=5
    
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #here we apply the limit passed in as a parameter to the query

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

#post by id, get a single post by id, if not found throw a 404 status, else return the post details
@router.get("/{id}", response_model=schemas.PostWithVote)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)): #function has access to id from path parameter and FastAPI is going to do validation to make sure that the parameter is of the correct type, otherwise will throw an error

    #query the database and filter for the record with the specified id
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    return post

#create a new post and return 201 status
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)): #get_current_user: int = Depends(oath2.get_current_user) means it depends on the user being logged in

    #using the %s parameters helps sanitize the input and prevent things like sql injection
    # cursor.execute("""Insert Into posts (title, content, published) Values (%s, %s, %s) Returning *""", (new_post.title, new_post.content, new_post.published))
    # new_post_record = cursor.fetchone() #get the record returned by the insert returning command
    # conn.commit() #force the record to be saved

    #new_post = models.Post(title=post.title, content=post.content, published=post.published) #this maps the inputs from class Post to the model Posts in the database
    #alternately, you can do it like this

    new_post = models.Post(user_id = current_user.id, **post.dict()) #this unpacks the dictionary and maps them to the fields    
    db.add(new_post) #insert new post
    db.commit() #commit it
    db.refresh(new_post) #pull new post and get info
    return new_post


#delete a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) #update the status code to a 204, in FastAPI a 204 does not allow data to be returned, such as a message
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    
    # cursor.execute("""Delete From posts Where id = %s Returning *""", (str(id),)) #not sure why but the last , needs to be there to make this code work correctly
    # post = cursor.fetchone()
    # conn.commit() #force the record to be saved

    post_query = db.query(models.Post).filter(models.Post.id == id) #run the query to get matching records

    post = post_query.first()

    #if not found, return a 404 status
    if post == None: #if there isn't a first record raise a 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with  id: {id} does not exist")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user id {current_user.id} is not allowed to delete posts created by other users")


    post_query.delete(synchronize_session=False) #if there is a record, delete it
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#update an existing post by id
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
   
    #using the %s parameters helps sanitize the input and prevent things like sql injection
    # cursor.execute("""Update posts Set title = %s, content = %s, published=%s Where id = %s Returning *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone() #get the record returned by the insert returning command
    # conn.commit() #force the record to be saved
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with  id: {id} does not exist")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user id {current_user.id} is not allowed to update posts created by other users")

    #this is the way manually map the fields
    #post_query.update({'title': 'hey this is my updated title', 'content': 'this is the updated content'}, synchronize_session=False)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()