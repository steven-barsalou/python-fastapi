from fastapi import Depends, APIRouter, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import oath2
from .. import models, schemas, oath2
from ..database import get_db

router = APIRouter(prefix="/vote", tags=['Vote']) #the tags helps delineate the sections in the swagger documentation

#posts, will return all of the posts in json
@router.post("/", status_code=status.HTTP_201_CREATED) #List creates a list of class PostResponse
def post_vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)): 
    

    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    found_post = post_query.first()
    if not found_post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post {vote.post_id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    found_vote = vote_query.first()

    if (vote.direction == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote does not exist")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="post deleted")
