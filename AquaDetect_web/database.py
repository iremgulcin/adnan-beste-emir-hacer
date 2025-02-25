from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.orm import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./videos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    processed_filename = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uploaded")
    detections = relationship("Detection", back_populates="video")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    animal_type = Column(String, index=True)
    confidence = Column(Float)
    frame_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    video = relationship("Video", back_populates="detections")

class AnimalInfo(Base):
    __tablename__ = "animal_info"

    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String, unique=True, index=True)
    common_name = Column(String)
    description = Column(String)
    threat_level = Column(String)
    habitat = Column(String)

# Remove drop_all and keep only create_all
Base.metadata.create_all(bind=engine)