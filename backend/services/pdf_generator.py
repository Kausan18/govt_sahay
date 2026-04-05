from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io

def generate_application_guide(scheme: dict, profile: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, h - 3*cm, scheme["name"])

    c.setFont("Helvetica", 12)
    c.drawString(2*cm, h - 4.5*cm, f"Applicant: {profile.get('name', 'N/A')}")
    c.drawString(2*cm, h - 5.2*cm, f"State: {profile.get('state', 'N/A')}")

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, h - 6.5*cm, "Required Documents:")
    c.setFont("Helvetica", 12)
    y = h - 7.2*cm
    for doc in scheme.get("required_docs", []):
        c.drawString(2.5*cm, y, f"• {doc.replace('_', ' ').title()}")
        y -= 0.7*cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, y - 0.5*cm, "How to Apply:")
    c.setFont("Helvetica", 12)
    steps = ["Visit the official government portal", "Register with your Aadhaar number",
             "Upload all required documents", "Submit and note your application ID"]
    y -= 1.2*cm
    for i, step in enumerate(steps, 1):
        c.drawString(2.5*cm, y, f"{i}. {step}")
        y -= 0.7*cm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y - 0.5*cm, f"Official Portal: {scheme.get('official_url', 'N/A')}")

    c.save()
    buffer.seek(0)
    return buffer.read()