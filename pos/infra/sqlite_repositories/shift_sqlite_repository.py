from typing import Optional

from pos.core.models.repositories import ShiftRepository
from pos.core.models.shift import Shift
from pos.infra.database import Database


class ShiftSQLiteRepository(ShiftRepository):
    def __init__(self, db: Database):
        self.db = db

    def create(self, shift: Shift) -> Shift:
        self.db.execute(
            "INSERT INTO shifts (id, cashier, is_open) VALUES (?,?,?)",
            (shift.id, shift.cashier, shift.is_open),
        )
        return shift

    def read(self, shift_id: str) -> Optional[Shift]:
        row = self.db.fetchone("SELECT * FROM shifts WHERE id=?", (shift_id,))
        if row is None:
            return None

        return Shift(id=row[0], cashier=row[1], is_open=row[2])

    def close(self, shift_id: str) -> None:
        self.db.execute(
            "UPDATE shifts SET is_open = ? WHERE id = ?",
            (
                False,
                shift_id,
            ),
        )
