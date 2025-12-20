from fastapi import APIRouter
from schemas import User
from auth import oauth2_scheme

router = APIRouter()

@router.get('/users')
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get('/users/me')
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(db, token)
    return user

@router.post('/users')
def create_user(db: Session = Depends(get_db), user: schemas.UserCreate):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put('/users/{user_id}')
def update_user(db: Session = Depends(get_db), user_id: int, user: schemas.UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = user.name
        db_user.email = user.email
        db.commit()
        return db_user
    else:
        return None

@router.delete('/users/{user_id}')
def delete_user(db: Session = Depends(get_db), user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {'message': 'User deleted'}
    else:
        return {'message': 'User not found'}
