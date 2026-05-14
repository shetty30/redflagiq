"""
report_generator.py
-------------------
Auto-generates a professional PDF report per company.
Uses fpdf2 library.

Output: outputs/reports/<TICKER>_RedFlagIQ_Report.pdf
"""

import os
from datetime import datetime
from fpdf import FPDF

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "reports")


NAVY      = (31, 78, 121)
MID_BLUE  = (46, 117, 182)
LT_BLUE   = (214, 228, 240)
WHITE     = (255, 255, 255)
DARK      = (30, 30, 46)
GREY      = (120, 120, 120)
PALE      = (235, 243, 251)
GREEN     = (55, 86, 35)
GREEN_BG  = (226, 239, 218)
AMBER     = (125, 102, 8)
AMBER_BG  = (255, 242, 204)
RED_C     = (192, 0, 0)
RED_BG    = (255, 224, 224)


def _risk_colors(risk: str):
    risk = risk.upper()
    if risk == "HIGH":
        return RED_C, RED_BG
    elif risk == "MEDIUM":
        return AMBER, AMBER_BG
    else:
        return GREEN, GREEN_BG


def _verdict_icon(risk: str) -> str:
    return {"HIGH": "HIGH RISK", "MEDIUM": "MEDIUM RISK", "LOW": "LOW RISK"}.get(
        risk.upper(), risk
    )


class RedFlagReport(FPDF):

    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 16, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.set_xy(10, 5)
        self.cell(0, 6, "RedFlagIQ  |  Financial Statement Red Flag Detector", align="L")
        self.set_xy(0, 5)
        self.cell(200, 6, f"Generated: {datetime.now().strftime('%d %b %Y')}", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-14)
        self.set_fill_color(*MID_BLUE)
        self.rect(0, self.get_y(), 210, 14, "F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*WHITE)
        self.set_x(10)
        self.cell(0, 14,
                  "DISCLAIMER: For educational and portfolio purposes only. "
                  "Not financial advice.  |  "
                  f"Page {self.page_no()}", align="L")

    def section_title(self, title: str):
        self.ln(4)
        self.set_fill_color(*MID_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.ln(2)

    def kv_row(self, label: str, value: str, shade: bool = False,
               value_color=None):
        bg = PALE if shade else WHITE
        self.set_fill_color(*bg)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "B", 10)
        self.cell(70, 7, f"  {label}", fill=True,
                  border="LTB")
        if value_color:
            self.set_text_color(*value_color)
        self.set_font("Helvetica", "", 10)
        self.cell(120, 7, f"  {value}", fill=True,
                  border="RTB", ln=True)
        self.set_text_color(*DARK)

    def ratio_row(self, name: str, value: str, threshold: str,
                  flagged: bool, shade: bool = False):
        bg = PALE if shade else WHITE
        icon = "FLAG" if flagged else "OK"
        icon_color = RED_C if flagged else GREEN
        icon_bg = RED_BG if flagged else GREEN_BG

        self.set_fill_color(*bg)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "B", 9)
        self.cell(55, 6, f"  {name}", fill=True, border="LTB")

        self.set_font("Helvetica", "", 9)
        self.cell(35, 6, value, fill=True, border="TB", align="C")
        self.cell(45, 6, f"Threshold: {threshold}", fill=True,
                  border="TB", align="C")

        self.set_fill_color(*icon_bg)
        self.set_text_color(*icon_color)
        self.set_font("Helvetica", "B", 9)
        self.cell(55, 6, icon, fill=True, border="RTB", align="C", ln=True)
        self.set_fill_color(*bg)
        self.set_text_color(*DARK)

    def flag_row(self, num: int, name: str, detail: str,
                 triggered: bool, shade: bool = False):
        bg = PALE if shade else WHITE
        icon_color = RED_C if triggered else GREEN
        icon_bg = RED_BG if triggered else GREEN_BG
        status = "FLAG" if triggered else "OK"

        self.set_fill_color(*bg)
        self.set_text_color(*DARK)

        y_start = self.get_y()

        self.set_font("Helvetica", "B", 9)
        self.cell(8, 12, str(num), fill=True, border="LTB", align="C")
        self.set_font("Helvetica", "", 9)
        self.multi_cell(122, 6, f" {name}\n {detail}",
                        fill=True, border="TB")
        y_end = self.get_y()

        self.set_xy(self.get_x() + 130, y_start)
        self.set_fill_color(*icon_bg)
        self.set_text_color(*icon_color)
        self.set_font("Helvetica", "B", 9)
        self.cell(50, 12, status, fill=True, border="RTB", align="C", ln=True)


def generate_report(
    mscore_result:  dict,
    zscore_result:  dict,
    redflags_result: dict,
    info:           dict,
) -> str:
    """
    Generate a PDF report combining all three model results.

    Args:
        mscore_result:   output from beneish_mscore.calculate_mscore()
        zscore_result:   output from altman_zscore.calculate_zscore()
        redflags_result: output from ratio_analysis.run_red_flags()
        info:            company info dict

    Returns:
        Path to the generated PDF file
    """
    ticker   = info.get("ticker", "N/A")
    company  = info.get("company_name", ticker)
    sector   = info.get("sector", "N/A")
    currency = info.get("currency", "USD")

    risks = [mscore_result["risk"], zscore_result["risk"], redflags_result["severity"]]
    if "HIGH" in risks:
        overall_risk = "HIGH"
    elif risks.count("MEDIUM") >= 2:
        overall_risk = "MEDIUM"
    elif "MEDIUM" in risks:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    risk_txt_color, risk_bg_color = _risk_colors(overall_risk)

    pdf = RedFlagReport()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_fill_color(*NAVY)
    pdf.rect(10, 18, 190, 36, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(14, 20)
    pdf.cell(0, 10, company)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_xy(14, 30)
    pdf.cell(0, 8, f"{ticker}  |  {sector}  |  {currency}  |  "
                   f"Analysis Year: {mscore_result['curr_year']}")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(14, 40)
    pdf.cell(0, 8, f"Comparing: FY{mscore_result['prev_year']} vs FY{mscore_result['curr_year']}")
    pdf.ln(30)

 
    pdf.set_fill_color(*risk_bg_color)
    pdf.set_draw_color(*risk_txt_color)
    pdf.set_text_color(*risk_txt_color)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 14, f"  OVERALL RISK RATING:  {_verdict_icon(overall_risk)}",
             fill=True, border=1, ln=True, align="C")
    pdf.ln(4)

    pdf.section_title("Score Summary")
    m_risk_col, _ = _risk_colors(mscore_result["risk"])
    z_risk_col, _ = _risk_colors(zscore_result["risk"])
    f_risk_col, _ = _risk_colors(redflags_result["severity"])

    pdf.kv_row("Beneish M-Score",
               f"{mscore_result['m_score']:.4f}  -  {mscore_result['verdict']}",
               shade=False, value_color=m_risk_col)
    pdf.kv_row("Altman Z-Score",
               f"{zscore_result['z_score']:.4f}  -  {zscore_result['zone']}",
               shade=True, value_color=z_risk_col)
    pdf.kv_row("Custom Flags Triggered",
               f"{redflags_result['triggered_count']} / {redflags_result['total_flags']}  "
               f"-  Severity: {redflags_result['severity']}",
               shade=False, value_color=f_risk_col)
    pdf.ln(4)

    
    pdf.section_title("Company Information")
    pdf.kv_row("Company",        company,               shade=False)
    pdf.kv_row("Ticker",         ticker,                shade=True)
    pdf.kv_row("Sector",         sector,                shade=False)
    pdf.kv_row("Currency",       currency,              shade=True)
    pdf.kv_row("Analysis Year",  mscore_result["curr_year"], shade=False)
    if info.get("market_cap"):
        mc = info["market_cap"] / 1_000_000
        pdf.kv_row("Market Cap", f"${mc:,.0f}M",        shade=True)
    pdf.ln(4)

    
    pdf.section_title(f"Beneish M-Score Detail  |  "
                      f"FY{mscore_result['prev_year']} vs FY{mscore_result['curr_year']}")

   
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(55, 6, "  Ratio", fill=True, border=1)
    pdf.cell(35, 6, "Value", fill=True, border=1, align="C")
    pdf.cell(45, 6, "Threshold", fill=True, border=1, align="C")
    pdf.cell(55, 6, "Status", fill=True, border=1, align="C", ln=True)

    thresholds = mscore_result["thresholds"]
    flagged    = mscore_result["flagged_ratios"]

    ratio_labels = {
        "DSRI": "DSRI - Days Sales Rec. Index",
        "GMI":  "GMI  - Gross Margin Index",
        "AQI":  "AQI  - Asset Quality Index",
        "SGI":  "SGI  - Sales Growth Index",
        "DEPI": "DEPI - Depreciation Index",
        "SGAI": "SGAI - SGA Expense Index",
        "TATA": "TATA - Accruals / Total Assets",
        "LVGI": "LVGI - Leverage Index",
    }

    for i, (key, val) in enumerate(mscore_result["ratios"].items()):
        val_str = f"{val:.4f}" if val is not None and val == val else "N/A"
        self_flag = key in flagged
        self.ratio_row(
            ratio_labels.get(key, key),
            val_str,
            f"> {thresholds[key]}",
            self_flag,
            shade=(i % 2 == 1),
        ) if False else pdf.ratio_row(
            ratio_labels.get(key, key),
            val_str,
            f"> {thresholds[key]}",
            self_flag,
            shade=(i % 2 == 1),
        )

    pdf.ln(2)
    m_col, m_bg = _risk_colors(mscore_result["risk"])
    pdf.set_fill_color(*m_bg)
    pdf.set_text_color(*m_col)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8,
             f"  M-Score: {mscore_result['m_score']:.4f}   |   "
             f"{mscore_result['verdict']}",
             fill=True, ln=True, border=1)
    pdf.ln(4)

    
    pdf.section_title(f"Altman Z-Score Detail  |  FY{zscore_result['curr_year']}")

    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(55, 6, "  Factor", fill=True, border=1)
    pdf.cell(25, 6, "Raw Value", fill=True, border=1, align="C")
    pdf.cell(20, 6, "Weight", fill=True, border=1, align="C")
    pdf.cell(30, 6, "Weighted", fill=True, border=1, align="C")
    pdf.cell(60, 6, "What It Measures", fill=True, border=1, align="C", ln=True)

    factor_labels = {
        "X1": ("X1 - Working Capital/TA", "Liquidity buffer"),
        "X2": ("X2 - Retained Earnings/TA", "Cumulative profitability"),
        "X3": ("X3 - EBIT/TA", "Operating efficiency"),
        "X4": ("X4 - Market Cap/Liabilities", "Market solvency"),
        "X5": ("X5 - Revenue/TA", "Asset turnover"),
    }

    for i, (key, val) in enumerate(zscore_result["factors"].items()):
        shade = (i % 2 == 1)
        bg = PALE if shade else WHITE
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "B", 9)
        label, meaning = factor_labels.get(key, (key, ""))
        val_str = f"{val:.4f}" if val is not None and val == val else "N/A"
        w_str   = f"{zscore_result['weights'][key]:.1f}×"
        wv_str  = f"{zscore_result['weighted'][key]:.4f}"

        pdf.cell(55, 6, f"  {label}", fill=True, border="LTB")
        pdf.cell(25, 6, val_str, fill=True, border="TB", align="C")
        pdf.cell(20, 6, w_str, fill=True, border="TB", align="C")
        pdf.cell(30, 6, wv_str, fill=True, border="TB", align="C")
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(60, 6, meaning, fill=True, border="RTB", ln=True)

    pdf.ln(2)
    z_col, z_bg = _risk_colors(zscore_result["risk"])
    pdf.set_fill_color(*z_bg)
    pdf.set_text_color(*z_col)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8,
             f"  Z-Score: {zscore_result['z_score']:.4f}   |   "
             f"{zscore_result['zone']}   |   {zscore_result['meaning']}",
             fill=True, ln=True, border=1)
    pdf.ln(4)

   
    pdf.section_title(f"Custom Red Flag Analysis  |  "
                      f"FY{redflags_result['prev_year']} vs FY{redflags_result['curr_year']}")

    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(8, 8, "#", fill=True, border=1, align="C")
    pdf.cell(122, 8, "Red Flag  |  Detail", fill=True, border=1)
    pdf.cell(50, 8, "Status", fill=True, border=1, align="C", ln=True)

    for i, flag in enumerate(redflags_result["flags"]):
        pdf.flag_row(
            flag["id"],
            flag["name"],
            flag["detail"],
            flag["triggered"],
            shade=(i % 2 == 1),
        )

    pdf.ln(2)
    f_col, f_bg = _risk_colors(redflags_result["severity"])
    pdf.set_fill_color(*f_bg)
    pdf.set_text_color(*f_col)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8,
             f"  Flags Triggered: {redflags_result['triggered_count']} / "
             f"{redflags_result['total_flags']}   |   "
             f"Severity: {redflags_result['severity']}",
             fill=True, ln=True, border=1)
    pdf.ln(6)

    
    pdf.section_title("Final Risk Assessment")
    pdf.set_fill_color(*risk_bg_color)
    pdf.set_text_color(*risk_txt_color)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 16,
             f"  {company} ({ticker})  -  OVERALL: {_verdict_icon(overall_risk)}",
             fill=True, ln=True, border=1, align="C")
    pdf.ln(3)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(*PALE)
    pdf.multi_cell(0, 5,
                   f"  This report is based on FY{mscore_result['curr_year']} financial "
                   f"statements vs FY{mscore_result['prev_year']}. "
                   f"The overall risk rating combines the Beneish M-Score "
                   f"({mscore_result['risk']} risk), Altman Z-Score "
                   f"({zscore_result['risk']} risk), and custom red flag analysis "
                   f"({redflags_result['severity']} severity). "
                   f"Always validate findings with qualitative research before "
                   f"drawing investment conclusions.",
                   fill=True, border=1)

    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{ticker}_RedFlagIQ_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    out_path = os.path.join(REPORTS_DIR, filename)
    pdf.output(out_path)

    print(f"[RedFlagIQ] ✅ PDF report saved -> outputs/reports/{filename}")
    return out_path
