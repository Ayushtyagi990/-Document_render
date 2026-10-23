from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from model import FormRequest, FormCreate
from pdf_service import generate_pdf
import os


app = FastAPI(
    title="ServiceHub Form Service"
)
forms_data = []

@app.post("/send-form", response_model=FormRequest, status_code=201)
def create_form(data: FormCreate):

    # Generate unique PDF number for every request
    form_id = len(forms_data) + 1

    pdf_path = generate_pdf(
        form_id=form_id,
        name=data.name,
        item=data.item,
        options=data.options,
        dependent_name=data.dependent_name,
        dependent_age=data.dependent_age
    )

    form_data = {
        "id": form_id,
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "item": data.item,
        "options": data.options,
        "dependent_name": data.dependent_name,
        "dependent_age": data.dependent_age,
        "pdf_path": pdf_path
    }

    forms_data.append(form_data)

    return form_data



@app.get("/pdf")
def view_all_pdf():

    folder = "generated_forms"

    if not os.path.exists(folder):
        raise HTTPException(
            status_code=404,
            detail="PDF folder not found"
        )

    pdf_files = [
        file for file in os.listdir(folder)
        if file.endswith(".pdf")
    ]

    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF files found"
        )

    return {
        "total": len(pdf_files),
        "files": pdf_files
    }
