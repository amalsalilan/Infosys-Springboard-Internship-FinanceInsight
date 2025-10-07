# Simple backend with authentication
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import hashlib
from datetime import datetime, timedelta
import json
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple file-based user storage
USERS_FILE = "users.json"
SECRET_KEY = "your-secret-key"
security = HTTPBearer()

# Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def create_token(username):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.post("/auth/register")
async def register(user: UserRegister):
    users = load_users()
    
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users[user.username] = {
        "email": user.email,
        "password": hash_password(user.password)
    }
    save_users(users)
    
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(user: UserLogin):
    users = load_users()
    
    if user.username not in users or not verify_password(user.password, users[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/profile")
async def profile(username: str = Depends(verify_token)):
    users = load_users()
    if username in users:
        return {"username": username, "email": users[username]["email"]}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/process/")
async def process_dummy(username: str = Depends(verify_token)):
    # Dummy response for now - you can integrate your NER processing here
    return {
        "status": "success",
        "message": f"Hello {username}! NER processing would happen here.",
        "entities": [],
        "pdf_highlights": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)