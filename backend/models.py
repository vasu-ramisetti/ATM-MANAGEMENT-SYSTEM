from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class Withdraw(BaseModel):
    username: str
    account_type: str
    amount: float

class Deposit(BaseModel):
    username: str
    account_type: str
    amount: float

class BalanceCheck(BaseModel):
    username: str
    pin: str