from sqlalchemy import select

from app.db import SessionLocal
from app.models import Plan


def get_or_create_plan(
    db,
    *,
    name: str,
    description: str,
) -> Plan:
    plan = db.scalar(
        select(Plan).where(
            Plan.name == name
        )
    )

    if plan is None:
        plan = Plan(
            name=name,
            description=description,
            is_active=True,
        )

        db.add(plan)
        db.flush()

    else:
        plan.description = description
        plan.is_active = True

    return plan


def seed_production() -> None:
    with SessionLocal() as db:
        try:
            get_or_create_plan(
                db,
                name="free",
                description=(
                    "Default RateGuard "
                    "developer plan"
                ),
            )

            db.commit()

            print(
                "Production seed completed."
            )

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_production()