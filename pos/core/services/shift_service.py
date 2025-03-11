from pos.core.models.repositories import ShiftRepository
from pos.core.models.shift import Shift


class ShiftService:
    def __init__(self, shift_repo: ShiftRepository):
        self.shift_repo = shift_repo

    def create_shift(self, shift_id: str, cashier: str) -> Shift:
        shift = Shift(id=shift_id, cashier=cashier)
        return self.shift_repo.create(shift)

    def get_shift(self, shift_id: str) -> Shift:
        shift = self.shift_repo.read(shift_id)
        if not shift:
            raise ValueError("Shift not found.")
        return shift

    def close_shift(self, shift_id: str) -> None:
        shift = self.shift_repo.read(shift_id)
        if not shift or not shift.is_open:
            raise ValueError("Shift is not valid or is already closed.")
        self.shift_repo.close(shift_id)
