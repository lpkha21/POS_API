from pos.core.models.report import Report
from pos.core.models.repositories import ReportRepository, ShiftRepository


class ReportService:
    def __init__(
        self, report_repository: ReportRepository, shift_repository: ShiftRepository
    ):
        self.report_repo = report_repository
        self.shift_repo = shift_repository

    def get_x_report(self, shift_id: str) -> Report:
        """Generate a report based on closed receipts."""
        shift = self.shift_repo.read(shift_id)
        if shift is None:
            raise ValueError("Shift not found.")
        report = self.report_repo.generate(shift_id)
        return report

    def get_z_report(self, shift_id: str) -> Report:
        """Generate a report based on closed receipts."""
        shift = self.shift_repo.read(shift_id)
        if shift is None:
            raise ValueError("Shift not found.")
        self.shift_repo.close(shift_id)
        report = self.report_repo.generate(shift_id)
        return report
