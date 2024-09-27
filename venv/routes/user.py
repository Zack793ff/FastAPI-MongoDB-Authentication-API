from fastapi import APIRouter, HTTPException
from models.user import User
from config.db import conn
from schemas.user import userEntity, usersEntity, serializeDict, serializeList
from bson import ObjectId

user_router = APIRouter()  # Renamed from 'user' to 'user_router' for clarity

@user_router.get('/')
async def find_all_users():
    users = list(conn.local.user.find())  # Convert the cursor to a list
    return serializeList(users)  # Use serializeList to transform users

@user_router.post('/register')
async def create_user(new_user: User):
    # Hash the user's password before saving
    new_user.hash_password()

    # Check if the user already exists
    if conn.local.user.find_one({"email": new_user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Convert the Pydantic model to a dictionary for insertion
    # inserted_user = conn.local.user.insert_one(new_user.model_dump(exclude={"password"}))
    user_data = new_user.model_dump(exclude_unset=True)   #ensure all feeds are included
    user_data['password'] = new_user.password # include the hashed password

    inserted_user = conn.local.user.insert_one(user_data)
    
    # Optionally, return the inserted user data
    return serializeDict(conn.local.user.find_one({"_id": inserted_user.inserted_id}))


@user_router.put('/{id}')
async def update_user(id: str, updated_user: User):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    updated_result = conn.local.user.find_one_and_replace(
        {"_id": ObjectId(id)},
        updated_user.model_dump(exclude={"password"})
    )

    if updated_result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return serializeDict(conn.local.user.find_one({"_id": ObjectId(id)}))


@user_router.patch('/{id}')
async def patch_user(id: str, updates: dict):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    updated_result = conn.local.user.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": updates},
        return_document=True
    )

    if updated_result is None:  # Corrected reference
        raise HTTPException(status_code=404, detail="User not found")
    
    return serializeDict(updated_result)


@user_router.delete('/{id}')
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    delete_result = conn.local.user.find_one_and_delete({"_id": ObjectId(id)})

    if delete_result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@user_router.post('/login')
async def login_user(email: str, password: str):
    # Find the user by email 
    user = conn.local.user.find_one({"email": email})

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Use the User model to verify the password
    user_model = User(name=user["name"], email=user["email"], password=user['password'])

    if not user_model.verify_password(password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Successful login, return user data without password
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]  # Corrected reference
    }
