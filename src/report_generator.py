from fpdf import FPDF
import os


def generate_pdf_report(ticker, risk_summary):
    os.makedirs("outputs/reports", exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt=f"RedFlagIQ Report: {ticker}", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.ln(10)

    for key, value in risk_summary.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    output_path = f"outputs/reports/{ticker}_redflag_report.pdf"
    pdf.output(output_path)

    print(f"PDF report generated: {output_path}")