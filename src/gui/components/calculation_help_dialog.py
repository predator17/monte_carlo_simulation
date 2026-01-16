"""Help dialog explaining monthly table calculations.

This module provides a dialog that displays detailed formulas
and explanations for how the monthly table values are calculated.
Uses MathJax via QWebEngineView for proper LaTeX rendering.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

# Dark theme colors
DARK_BG = "#1E1E1E"
DARK_TEXT = "#E0E0E0"
FORMULA_BG = "#252529"
FORMULA_BORDER = "#3A3A3E"


MATHJAX_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            background-color: """ + DARK_BG + """;
            color: """ + DARK_TEXT + """;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            margin: 0;
            padding: 24px 32px;
        }
        .section { margin-bottom: 32px; }
        .section-title {
            color: #6CB6EE;
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 16px;
            margin-top: 24px;
            letter-spacing: 0.3px;
        }
        .formula-box {
            background: linear-gradient(145deg, """ + FORMULA_BG + """ 0%, #2A2A2E 100%);
            border: 1px solid """ + FORMULA_BORDER + """;
            border-radius: 12px;
            padding: 20px 28px;
            margin: 14px 0;
        }
        .formula-title {
            color: #9CA3AF;
            font-size: 12px;
            margin-bottom: 12px;
            font-weight: 500;
        }
        .legend {
            color: #8B949E;
            font-size: 11px;
            margin-top: 12px;
            padding: 10px 16px;
            background: rgba(255,255,255,0.04);
            border-radius: 8px;
            line-height: 1.7;
        }
        .arrow {
            text-align: center;
            color: #6CB6EE;
            font-size: 20px;
            margin: 6px 0;
            letter-spacing: 2px;
        }
        .step {
            background: """ + FORMULA_BG + """;
            border: 1px solid """ + FORMULA_BORDER + """;
            border-left: 3px solid #6CB6EE;
            border-radius: 8px;
            padding: 14px 20px;
            margin: 10px 0;
            font-size: 14px;
        }
        .example-table {
            color: #E0E0E0;
            margin: 16px 0 0 16px;
            font-size: 13px;
        }
        .example-table td { padding: 7px 28px 7px 0; }
        .example-table td:first-child { color: #9CA3AF; }
        h4 {
            color: #6CB6EE;
            font-size: 14px;
            margin: 16px 0 12px 0;
            font-weight: 600;
        }
    </style>
</head>
<body>
""" + """
<div class="section">
    <div class="section-title">1. Overview</div>
    <div class="formula-box"><div class="formula-title">Start balance</div>$$B_{start}$$</div>
    <div class="arrow">↓</div>
    <div class="formula-box"><div class="formula-title">After withdrawal</div>$$B_{start} - W$$</div>
    <div class="arrow">↓</div>
    <div class="formula-box"><div class="formula-title">After income</div>$$B_{start} - W + I$$</div>
    <div class="arrow">↓</div>
    <div class="formula-box"><div class="formula-title">Split to stock/cash</div>$$S + C$$</div>
    <div class="arrow">↓</div>
    <div class="formula-box"><div class="formula-title">Final balance</div>$$S(1+r_s) + C(1+r_c) = B_{end}$$</div>
    <div class="legend">B = balance | W = withdrawal | I = income | S = stock | C = cash | r_s = stock return | r_c = cash return</div>
</div>

<div class="section">
    <div class="section-title">2. Monthly Inflation Rate</div>
    <div class="formula-box"><div class="formula-title">Convert annual inflation to monthly:</div>$$i_{monthly} = (1 + i_{annual})^{1/12} - 1$$</div>
    <div class="formula-box"><div class="formula-title">Example (3% annual):</div>$$i_{monthly} = (1 + 0.03)^{1/12} - 1 \\approx 0.002466 = 0.2466\\%$$</div>
    <div class="legend">Note: Uses geometric mean for accurate compounding (not simple division)</div>
</div>

<div class="section">
    <div class="section-title">3. Balance Calculation (Step-by-Step)</div>
    <div class="step">Step 1: $$B_{after\\_withdrawal} = B_{prev} - W_m$$</div>
    <div class="step">Step 2: $$B_{for\\_investment} = B_{after\\_withdrawal} + I$$</div>
    <div class="step">Step 3: $$S_m = B_{for\\_investment} \\times a_s$$, $$C_m = B_{for\\_investment} \\times a_c$$</div>
    <div class="step">Step 4: $$S_{final} = S_m(1 + r_s)$$, $$C_{final} = C_m(1 + r_c)$$</div>
    <div class="step">Step 5: $$B_{curr} = S_{final} + C_{final}$$</div>
    <div class="legend" style="font-size: 11px;">B_prev = start balance | W_m = month m withdrawal | I = income | a_s, a_c = stock/cash allocations | r_s = stock return | r_c = cash return</div>
</div>

<div class="section">
    <div class="section-title">4. Portfolio Return &amp; Cash Return</div>
    <div class="formula-box"><div class="formula-title">Cash Return (fixed monthly rate):</div>$$R_c = r_c \\times 100\\%$$</div>
    <div class="formula-box"><div class="formula-title">Portfolio Return (back-calculated):</div>$$R_s = \\left(\\dfrac{B_{curr} - C_{final}}{S_m} - 1\\right) \\times 100\\%$$</div>
    <div class="legend">Portfolio return is the ACTUAL stock return. We back-calculate it from the final balance.</div>
</div>

<div class="section">
    <div class="section-title">5. Withdrawal with Inflation</div>
    <div class="formula-box"><div class="formula-title">Withdrawal grows with inflation:</div>$$W_m = W_{base} \\times (1 + i_{monthly})^m$$</div>
    <div class="formula-box"><div class="formula-title">Example (Base = ¥10,000, 3%):</div>$$W_0 = ¥10,000$$, $$W_1 = ¥10,024.66$$, $$W_2 = ¥10,049.40$$</div>
</div>

<div class="section">
    <div class="section-title">6. Numerical Example (January 2026)</div>
    <div class="formula-box">Given: $$B_{prev} = ¥100,000$$, $$W = ¥10,000$$, $$I = ¥1,000$$, $$a_s = 0.8$$, $$a_c = 0.2$$</div>
    <div class="formula-box"><div class="formula-title">After withdrawal, income, split:</div>$$B_{after\\_withdrawal} = ¥90,000$$, $$B_{for\\_investment} = ¥91,000$$, $$S = ¥72,800$$, $$C = ¥18,000$$</div>
    <div class="formula-box"><div class="formula-title">If $$r_s = -5\\%$$, $$r_c = 0.2\\%$$:</div>$$S_{final} = ¥69,160$$, $$C_{final} = ¥18,036$$, $$B_{curr} = ¥87,196$$</div>
    <h4>Final Table Values:</h4>
    <table class="example-table">
        <tr><td>Balance:</td><td>¥87,196.0000</td></tr>
        <tr><td>Change:</td><td>-¥12,804.0000</td></tr>
        <tr><td>Portfolio Return:</td><td>-5.0000%</td></tr>
        <tr><td>Cash Return:</td><td>0.2000%</td></tr>
        <tr><td>Withdrawal:</td><td>¥10,000.0000</td></tr>
        <tr><td>Income:</td><td>¥1,000.0000</td></tr>
    </table>
</div>
""" + """
</body>
</html>"""


class CalculationHelpDialog(QDialog):
    """Dialog showing calculation formulas with MathJax rendering."""

    def __init__(self, parent: QWidget = None):
        """Initialize the help dialog.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("How Are Values Calculated?")
        self.setMinimumSize(850, 650)
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {DARK_TEXT};")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        title = QLabel("Monthly Table Calculation Formulas")
        title.setStyleSheet("font-size: 15pt; font-weight: 600; color: #6CB6EE; padding: 12px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # WebEngineView for MathJax
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(f"background-color: {DARK_BG}; border: none;")
        layout.addWidget(self.web_view)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6CB6EE;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 11px 24px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{ background-color: #5A9FE0; }}
        """)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Load HTML
        self.web_view.setHtml(MATHJAX_HTML)
