#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy, datetime, json, requests, os, yaml, html
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, DateTime, String, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import sessionmaker, relationship, backref

engine = create_engine(r'sqlite:///app.db', echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
Base = declarative_base()

class Karto(Base):
    __tablename__ = "karto"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    teksto = Column(String)
    chat_id = Column(Integer)
    grupnomo = Column(String, nullable=False)
    uzanto_id = Column(Integer)
    uzanto_nomo = Column(Integer, nullable=False)
    rugxa_karto = Column(Boolean)
    rugxa_duvorta_karto = Column(Boolean)
    rugxa_trivorta_karto = Column(Boolean)
    verda_karto = Column(Boolean)
    aldonita = Column(DateTime)

def aldonu_karton_al_db(
        teksto, grupnomo, uzanto_nomo, uzanto_id=0, chat_id=0, rugxa_karto=False,
        rugxa_duvorta_karto=False, rugxa_trivorta_karto=False, verda_karto=False
    ):
    session.add(Karto(
        teksto=teksto, chat_id = chat_id, rugxa_duvorta_karto = rugxa_duvorta_karto,
        grupnomo = grupnomo, uzanto_id = uzanto_id, uzanto_nomo = uzanto_nomo,
        rugxa_karto = rugxa_karto, verda_karto = verda_karto,
        rugxa_trivorta_karto = rugxa_trivorta_karto, aldonita = datetime.datetime.now()
    ))
    session.commit()

def printebligi(rugxaj, verdaj):
    return {
             "verdaj": {
                   "bildo": "../img/verdaj_kartoj.png",
                   "fontkoloro": "#008000",
                   "antauxpado": "verda",
                   "kartoj": [{"teksto":str(v.teksto)} for v in verdaj]
              },
            "rugxaj": {
                 "bildo": "../img/rugaj_kartoj.png",
                 "fontkoloro": "#ce181e",
                 "antauxpado": "rugxa",
                 "kartoj": [{"teksto":str(v.teksto)} for v in rugxaj]
            }
        }

def cxiujn_kartojn():
    return session.query(Karto).all()

def cxiujn_kartojn_por_printado_de_uzantoj(uzantoj=[]):
    verdaj = [v for v in session.query(Karto).filter((Karto.verda_karto==1)).all() if v.uzanto_nomo in uzantoj]
    rugxaj = [r for r in session.query(Karto).filter((Karto.verda_karto!=1) | (Karto.verda_karto==None)).all()  if r.uzanto_nomo in uzantoj]
    return printebligi(rugxaj, verdaj)

def cxiujn_kartojn_por_printado():
    verdaj = session.query(Karto).filter((Karto.verda_karto==1)).all()
    rugxaj = session.query(Karto).filter((Karto.verda_karto!=1) | (Karto.verda_karto==None)).all()
    return printebligi(rugxaj, verdaj)

def sercxu_kartojn_de(grupoj=[], uzantoj=[]):
    pass

def createDB():
    if os.path.isfile("app.db"):
        print("app.db already exsists, skip creation and init...")
        return
    Base.metadata.create_all(engine);
    kartoj = yaml.safe_load(open("kartoj_kontraux_esperantujo/kartoj.yaml").read())   # listo de kartoj
    for karto in kartoj["verdaj"]["kartoj"]:
        session.add(Karto(teksto=karto["teksto"], grupnomo="lakt.uk", uzanto_nomo="timsk", verda_karto=True))
    for karto in kartoj["rugxaj"]["kartoj"]:
        session.add(Karto(teksto=karto["teksto"], grupnomo="lakt.uk", uzanto_nomo="timsk", rugxa_karto=True))
    session.commit()
