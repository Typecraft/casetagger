from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

__tablenames__ = ['case', 'case_from_counter', 'case_relation']

Base = declarative_base()


class Case(Base):
    __tablename__ = 'case'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, index=True)
    case_to = Column(String, index=True)
    case_from = Column(String, index=True)
    occurrences = Column(Integer, default=1)

    def __eq__(self, other):
        return self.type == other.type \
            and self.case_to == other.case_to \
            and self.case_from == other.case_from


class CaseFromCounter(Base):
    __tablename__ = 'case_from_counter'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, index=True)
    case_from = Column(String, index=True)
    occurrences = Column(Integer, default=1)


class CaseRelation(Base):
    __tablename__ = 'case_relation'

    case_1 = Column(Integer, primary_key=True)
    case_2 = Column(Integer, primary_key=True)

