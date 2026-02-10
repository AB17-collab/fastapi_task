from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, utils
from auth_database import get_db
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError

SECRET_KEY = "KOz1eTcTi93n0Z5rMTH0M63UEZ6nPztLzXKo75h922k"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Helper function that takes user data
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

app = FastAPI()

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    # Hash the password
    hashed_password = utils.hash_password(user.password)

    # Create new user instance
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'id': new_user.id, 'username': new_user.username, 'email': new_user.email, 'role': new_user.role}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"username": username, "role": role}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}! You have access to this protected route."}

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user['role'] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
        return current_user
    return role_checker


@app.get("/profile")
def profile(current_user: dict = Depends(require_role(["user", "admin"]))):
    return {"message": f"Profile of {current_user['username']} ({current_user['role']})"}

@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_role(["user"]))):
    return {"message": f"Welcome to the user dashboard, {current_user['username']}!"}

@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_role(["admin"]))):
    return {"message": f"Welcome to the admin dashboard, {current_user['username']}!"}
