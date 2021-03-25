from sqlalchemy.orm import Session

import models, schemas


def list_jars(db: Session, user_id: int):
    return db.query(models.Jar).filter(models.Jar.id == jar_id).first()

def create_jar(db: Session, Jar: schemas.JarCreate):
    db_jar = models.Jar(name=jar_name, value=0)
    
    db.add(db_jar)
    db.commit()
    db.refresh(db_jar)
    return db_jar