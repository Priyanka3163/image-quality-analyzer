from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import JSON

from datetime import datetime

from database import Base


class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    quality_score = Column(
        Integer,
        nullable=False
    )

    quality_label = Column(
        String,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    statistics = Column(
        JSON,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )