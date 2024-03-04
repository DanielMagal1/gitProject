from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import nacl.secret
import nacl.utils
from sqlalchemy.testing.pickleable import Address, User


def main():
    engine = create_engine("sqlite://", echo=True)
    with Session(engine) as session:
        exmpl = User(
            name = "user",
            fullname = "User U",
            addresses = [Address(email_address="user@sqlalchemy.org")]
        )
        session.add(exmpl)
        session.commit()
if __name__ == "__main__":
    main()