from fastapi import APIRouter, HTTPException

from app.db.database import store
from app.services.imo_compliance import evaluate_imo_compliance

router = APIRouter(prefix="/compliance", tags=["compliance"])

# In production this would come from the vessel agent's pre-arrival
# submission via the port's single-window system. Sample declarations
# below demonstrate both a fully-compliant and a non-compliant vessel.
SAMPLE_DECLARATIONS = {
    "366123456": {
        "mmsi": "366123456", "fal_general_declaration": True, "fal_crew_list": True,
        "fal_passenger_list": True, "ballast_water_report": True,
        "garbage_record_book_current": True, "oil_record_book_current": True,
        "pre_arrival_notice_filed": True,
    },
    "235098765": {
        "mmsi": "235098765", "fal_general_declaration": True, "fal_crew_list": True,
        "fal_passenger_list": True, "ballast_water_report": False,
        "garbage_record_book_current": True, "oil_record_book_current": False,
        "pre_arrival_notice_filed": True,
    },
}


@router.get("/{mmsi}")
def get_compliance(mmsi: str):
    if mmsi not in store.vessels:
        raise HTTPException(status_code=404, detail="Vessel not found")

    declarations = SAMPLE_DECLARATIONS.get(mmsi, {"mmsi": mmsi})
    report = evaluate_imo_compliance(declarations)
    return {
        "mmsi": report.mmsi,
        "fully_compliant": report.fully_compliant,
        "items": [item.__dict__ for item in report.items],
    }
