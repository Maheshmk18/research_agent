from fastapi import APIRouter, HTTPException

from db.mongodb import get_all_reports, get_report_by_id


router = APIRouter(prefix="/history", tags=["history"])


def _serialize_report(report: dict):
    report["_id"] = str(report["_id"])
    return report


@router.get("")
def read_history():
    reports = get_all_reports()
    return [_serialize_report(report) for report in reports]


@router.get("/{report_id}")
def read_history_detail(report_id: str):
    try:
        report = get_report_by_id(report_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid report id") from exc

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return _serialize_report(report)
