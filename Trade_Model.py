from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.automap import automap_base


Base = automap_base()

#engine = create_engine('sqlite:///database.chartinktradelog')
engine = create_engine("sqlite:///chartinktradelog.db")

#Base.prepare(autoload_with=engine)
Base.prepare(autoload_with=engine, reflect=True)


d = Base.classes
a = d
#User = Base.classes.28_03_2024
#User = Base.classes.user
