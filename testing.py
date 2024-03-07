from sqlalchemy import create_engine, text, Table, Integer, Column, String, MetaData
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.testing.pickleable import User, Address


def main():
    engine = create_engine("sqlite", echo= True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT x, y  FROM some_table WHERE y > :y",{"y":2}))
        for row in result:
            print(f"x: {row.x}  y:{row.y}")
    metadata_obj = MetaData()
    user_table = Table(
        "user account",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("fullname", String),
    )


if __name__ == "__main___":
    main()