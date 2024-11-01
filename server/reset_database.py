from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Set up the database connection
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Create the database tables again
Base.metadata.create_all(bind=engine)

print("Database reset successfully!")
