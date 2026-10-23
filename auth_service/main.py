from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from database import get_session, create_db_and_tables
from model import FormRequest, FormCreate
from pdf_service import generate_pdf


def now() -> datetime:
    return datetime.now(timezone.utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="ServiceHub Form Service", lifespan=lifespan)



@app.post("/send-form", response_model=FormRequest, status_code=201)
def create_form(
    data: FormCreate,
    session: Session = Depends(get_session)
):
    try:
        now_time = now()

        form = FormRequest(
            **data.model_dump(),
            created_at=now_time,
            updated_at=now_time
        )

        session.add(form)
        session.flush()

        # Generate PDF without sending email
        pdf_path = generate_pdf(
            form.id,
            data.name,
            data.item,
            data.options,
            data.dependent_name,
            data.dependent_age
        )

        form.pdf_path = str(pdf_path) if pdf_path else None
        form.updated_at = now()

        session.commit()
        session.refresh(form)

        return form

    except Exception:
        session.rollback()
        raise



@app.get("/forms/{form_id}/pdf")
def view_pdf(
    form_id: int,
    session: Session = Depends(get_session)
):
    form = session.get(FormRequest, form_id)

    if not form:
        raise HTTPException(404, "Form not found")

    return FileResponse(
        path=form.pdf_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=form_{form_id}.pdf"
        }
    )