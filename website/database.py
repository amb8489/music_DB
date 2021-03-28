from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

class DB_interface:
    def __init__(self, db):
        engine = db.get_engine();
        Base = automap_base()
        Base.prepare(engine, reflect=True)
        self.db = db
        self.session = Session(engine)
