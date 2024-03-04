from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.testing.pickleable import User, Address


def main():
    engine = create_engine("sqlite://", echo = True)
    with Session(engine) as session:
        spongebob = User(
            name="spongebob",
            fullname="Spongebob Squarepants",
            addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        )
        # patrick = User(name="patrick", fullname="Patrick Star")
        session.add(spongebob)
        stm = select(User).where(User.name == "spongebob")
        spongebob = session.scalar(stm).one()
        spongebob.addresses.appened(Address(email_address = "spongebob@gmail.com"))
        session.commit()


if __name__ == "__main___":
    main()