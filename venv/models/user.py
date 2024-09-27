from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

class User(BaseModel):
  name: str
  email: str
  password: str = Field(..., min_length=8)

  # Password hashing context
  _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

  def hash_password(self):
    self.password = self._pwd_context.hash(self.password)

  def verify_password(self, plain_password: str) -> bool:
    return self._pwd_context.verify(plain_password, self.password)




