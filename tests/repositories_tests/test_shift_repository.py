import unittest

from pos.core.models.shift import Shift
from pos.infra.database import Database
from pos.infra.sqlite_repositories.shift_sqlite_repository import ShiftSQLiteRepository


class TestShiftRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.repo = ShiftSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS shifts")

    def test_create_shift(self) -> None:
        shift = Shift(id="1", cashier="Luka")
        created_shift = self.repo.create(shift)
        self.assertIsNotNone(created_shift)
        if created_shift is not None:
            self.assertEqual(created_shift.id, "1")
            self.assertEqual(created_shift.cashier, "Luka")
            self.assertEqual(created_shift.is_open, True)

    def test_read_shift(self) -> None:
        shift = Shift(id="1", cashier="Luka")
        self.repo.create(shift)
        retrieved_shift = self.repo.read(shift.id)
        self.assertIsNotNone(retrieved_shift)
        if retrieved_shift is not None:
            self.assertEqual(retrieved_shift.id, "1")
            self.assertEqual(retrieved_shift.cashier, "Luka")
            self.assertEqual(retrieved_shift.is_open, True)

    def test_close_shift(self) -> None:
        shift = Shift(id="1", cashier="Luka")
        self.repo.create(shift)
        self.repo.close(shift.id)
        retrieved_shift = self.repo.read(shift.id)
        self.assertIsNotNone(retrieved_shift)
        if retrieved_shift is not None:
            self.assertEqual(retrieved_shift.id, "1")
            self.assertEqual(retrieved_shift.cashier, "Luka")
            self.assertEqual(retrieved_shift.is_open, False)
