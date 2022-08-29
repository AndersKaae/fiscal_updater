from sqlalchemy import create_engine, Column, Integer, String, UnicodeText, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:miro12sd@192.168.1.66:3306/ficaldata')

Base = declarative_base()

class Rebuild_DB(Base):
    __tablename__ = 'rebuild'
    date = Column(String(200), primary_key=True)

class Fiscal_Json_Data(Base):
    __tablename__ = 'fiscal_json_data'
    sagsnummer = Column(String(200), primary_key=True)
    cvr = Column(String(200))
    fiscalstart = Column(String(200))
    fiscalend = Column(String(200))
    url = Column(String(200))
    fileguid = Column(String(200))

Session = sessionmaker(bind=engine)
Session = sessionmaker()
Session.configure(bind=engine, autoflush=False)
session = Session()
Base.metadata.create_all(engine)

def Get_Rebuild_Date():
    data = session.query(Rebuild_DB).first()
    return data.date

def Save_Json_To_DB(sagsnummer, cvr, startDato, slutDato, url):
    isItUnique = session.query(Fiscal_Json_Data).filter_by(sagsnummer = sagsnummer).first()
    if isItUnique == None:
        regtxt = Fiscal_Json_Data(sagsnummer = sagsnummer, cvr = cvr, fiscalstart = startDato, fiscalend = slutDato, url = url, fileguid = None)
        session.add(regtxt)
        session.commit()
        session.close()

def Store_Progress(date_input):
    data = session.query(Rebuild_DB).first()
    if data == None:
       newdata = Rebuild_DB(date = date_input)
       session.add(newdata)
    else:
        data.date = date_input
    session.commit()
    session.close()