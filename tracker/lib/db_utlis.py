from typing import Tuple, List
from lib.enums import Role
from db.models import User

from sqlalchemy.orm import Session

def get_all_workers(engine) -> List[Tuple[str, int]]:
    with Session(engine) as session:
        rows = session.query(User).filter_by(role=Role.WORKER.value).all()
        possible_workers = [(row.public_id, row.id) for row in rows]
    return possible_workers
