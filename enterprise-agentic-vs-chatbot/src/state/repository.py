from contextlib import contextmanager
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from src.state.models import Base, Workflow
from fastapi import HTTPException


class Repository:
    def __init__(self, url):
        self.engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self):
        with self.sessions() as session:
            # Serializes local writers across workers/restarts, including approval and activation.
            session.execute(text("BEGIN IMMEDIATE"))
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def visible(self, session, workflow_id, identity):
        w = session.scalar(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.tenant == identity.tenant)
        )
        if not w:
            raise HTTPException(404, "Workflow not found")
        return w
