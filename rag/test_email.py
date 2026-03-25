from pydantic import BaseModel, EmailStr

class Test(BaseModel):
    email: EmailStr

t = Test(email='test@example.com')
print('Email validation works:', t.email)
