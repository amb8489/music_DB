from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

def db_init(db):
    engine = db.get_engine()

    Base = automap_base()
    Base.prepare(engine, reflect=True)
