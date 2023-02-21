from passlib.context import CryptContext

pwd_content = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash(password:str):
    return pwd_content.hash(password)

def verify_pass(plain_password, hashed_password):
    return pwd_content.verify(plain_password, hashed_password)