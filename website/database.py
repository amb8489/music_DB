from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

class DB_interface:
    def __init__(self, db):
        engine = db.get_engine();
        self.Base = automap_base()
        self.Base.prepare(engine, reflect=True)
        self.db = db
        self.session = Session(engine)

    def access(self, table: str, ):
        table = getattr(self.Base.classes, table)
        
