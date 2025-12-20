from pyjwt import encode
from datetime import datetime, timedelta
from jose import jwt
from schemas import User

def generate_token(user: User):
    to_encode = {'sub': user.id, 'exp': datetime.utcnow() + timedelta(minutes=15), 'name': user.name, 'email': user.email}
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt
