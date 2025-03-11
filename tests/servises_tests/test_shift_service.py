import unittest

from pos.core.services.shift_service import ShiftService
from pos.infra.database import Database
from pos.infra.sqlite_repositories.shift_sqlite_repository import ShiftSQLiteRepository


class TestShiftService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.shift_repo = ShiftSQLiteRepository(self.db)
        self.shift_service = ShiftService(self.shift_repo)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS shifts")

    def test_create_shift(self) -> None:
        # Test creating a new shift
        shift = self.shift_service.create_shift(shift_id="1", cashier="Luka")
        self.assertEqual(shift.id, "1")
        self.assertEqual(shift.cashier, "Luka")
        self.assertEqual(shift.is_open, True)

    def test_get_product(self) -> None:
        # Create a shift
        self.shift_service.create_shift(shift_id="1", cashier="Luka")

        # Test getting an existing shift
        shift = self.shift_service.get_shift("1")
        self.assertIsNotNone(shift)
        self.assertEqual(shift.cashier, "Luka")
        self.assertEqual(shift.is_open, True)

        # Test getting a non-existent shift
        with self.assertRaises(ValueError):
            self.shift_service.get_shift("2")

    def test_close_shift(self) -> None:
        # Create a shift
        self.shift_service.create_shift(shift_id="1", cashier="Luka")

        # Close a shift
        self.shift_service.close_shift("1")

        shift = self.shift_service.get_shift("1")
        self.assertIsNotNone(shift)
        self.assertEqual(shift.cashier, "Luka")
        self.assertEqual(shift.is_open, False)
