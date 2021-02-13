from sqlalchemy import engine, schema
from fastapi import FastAPI
import databases,sqlalchemy
import uuid
from pydantic import BaseModel,Field
from typing import List
from passlib.context import CryptContext
from var import *
import datetime
import os
import psycopg2


####### password encrypt ###
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")



########## db config
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "py_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("age", sqlalchemy.Integer),
    sqlalchemy.Column("created_at", sqlalchemy.String)
    
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)
###########################


########### Models ###############

class UserList(BaseModel):
    id: str
    username: str
    password: str
    first_name: str
    last_name: str
    age: int
    created_at: str



class UserEntry(BaseModel):
    username: str = Field(..., example="felipelipe")
    password: str = Field(..., example="@Password12345")
    first_name: str = Field(..., example="Felipe")
    last_name: str  = Field(..., example="Silva")
    age: int  = Field(..., example="22")


class UpdateUser(BaseModel):
    id : str = Field(..., example="Enter The ID params")
    first_name: str = Field(..., example="Felipe")
    last_name: str  = Field(..., example="Silva")
    age: int  = Field(..., example="22")


class DeleteUser(BaseModel):
    id : str = Field(..., example="Enter The ID params")



app = FastAPI()





###### turn on the db
@app.on_event('startup')
async def startup(): 
    await database.connect()

##### turn off the db
@app.on_event('shutdown')
async def shutdown(): 
    await database.disconnect()

###### Routes

@app.get('/api/users', response_model=List[UserList])
async def listUsers():
    """This Function Returns All User.
    Função que retorna todos os usuários
     """
    query_set = users.select()
    return await database.fetch_all(query_set)


@app.post('/api/users/register',response_model=UserList)
async def register_user(user: UserEntry): 
    """This Function Register User Datas.
    Função que registra os dados do usuário
     """
    gId = str(uuid.uuid4())
    gDate = str(datetime.datetime.now())
    query_set = users.insert().values(
        id = gId,
        created_at = gDate,
        username = user.username,
        password = pwd_context.hash(user.password),
        first_name = user.first_name,
        last_name = user.last_name,
        age = user.age,
    )
    await database.execute(query_set)
    return {
        "id":gId,
        **user.dict(),
        "created_at":gDate
        }


@app.get('/api/users/{userID}', response_model=UserList)
async def find_user_by_id(userID:str):
    """This Function Returns one User by id.
    Função que retorna um usuario pelo ID
     """
    query_set = users.select().where(users.c.id == userID)
    return await database.fetch_one(query_set)



@app.put('/api/users/update',response_model=UserList)
async def update_user(user: UpdateUser):
    """This Function Update the data user by id.
          Função que Edita ou atualiza os dados do usuario
    """
    gDate = str(datetime.datetime.now())
    query_set = users.update().where(users.c.id == user.id).values(
        first_name = user.first_name,
        last_name = user.last_name,
        age = user.age,
        created_at = gDate,
    
    )
    await database.execute(query_set)
    return await find_user_by_id(user.id)

@app.delete('/api/users/delete/{userID}')
async def delete_user(user:DeleteUser):
    query_set = users.delete().where(users.c.id == user.id)
    await database.execute(query_set)

    return {
        "Msg": "The user has been deleted",
        "Status": True
    }
