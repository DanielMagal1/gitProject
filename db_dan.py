from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import nacl.secret
import nacl.utils
def main():

    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())
if __name__ == "__main__":
    main()