"""
Database configuration and models
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./uc_dashboard.db")

# PostgreSQL URLs from Heroku/Railway use 'postgres://' but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Invoice(Base):
    """Invoice table"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, unique=True, index=True, nullable=False)
    invoice_date = Column(Date, nullable=True)
    customer = Column(String, index=True, nullable=False)
    ship_via = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False)
    line_item_count = Column(Integer, nullable=False)
    filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LineItem(Base):
    """Line items table"""
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, index=True, nullable=False)
    p_n = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    qty = Column(Float, nullable=False)
    price_unit = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


if __name__ == "__main__":
    init_db()
