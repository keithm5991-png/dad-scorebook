"""Blank printable USA Softball-style score sheet (letter portrait PDF).
Faithful to the official 2024 USA Softball sheet (p.7) with one modification:
summary = AWAY row + HOME row, each with RUNS-over-HITS slashed boxes per
inning, so both teams' line score fits on one sheet (official pairs
RUNS/HITS + ERRORS/LOB for one team).
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

W, H = letter            # 612 x 792
M = 24                   # margin
GW = W - 2 * M           # grid width
BLOCKS = 16
INN = 9
RAIL = ["AB", "R", "H", "SB", "BB", "SO", "RBI", "E"]

# column geometry
PLY_W, POS_W, RAIL_W = 96, 14, 13
INN_W = (GW - PLY_W - POS_W - RAIL_W * len(RAIL)) / INN   # ~38.9

# row geometry (top-down)
TITLE_H, META_H, HDR_H = 24, 14, 13
NAME_H, SUB_H = 24, 9
BLOCK_H = NAME_H + SUB_H
SUM_H = 18
PIT_ROW_H, PIT_ROWS = 12, 5

c = canvas.Canvas("usa-softball-scoresheet.pdf", pagesize=letter)
c.setLineWidth(0.7)

top = H - M
x0 = M
x_pos = x0 + PLY_W
x_inn = x_pos + POS_W
x_rail = x_inn + INN * INN_W
x_end = x_rail + len(RAIL) * RAIL_W

# ---------- title ----------
c.setFont("Helvetica-Bold", 19)
c.drawCentredString(W / 2, top - 16, "USA SOFTBALL SCORE SHEET")
y = top - TITLE_H

# ---------- vs / at / Date line ----------
c.setFont("Helvetica-Bold", 7)
def blank(label, lx, llen):
    c.drawString(lx, y - 10, label)
    lw = c.stringWidth(label, "Helvetica-Bold", 7)
    c.line(lx + lw + 2, y - 11, lx + lw + 2 + llen, y - 11)
blank("vs.", x_inn + 10, 150)
blank("at", x_inn + INN_W * 5, 130)
blank("Date", x_rail - 60, 80)
y -= META_H

# ---------- header row ----------
hdr_top = y
c.setFont("Helvetica-Bold", 7.5)
c.rect(x0, y - HDR_H, PLY_W, HDR_H)
c.drawString(x0 + 3, y - HDR_H + 3.5, "PLAYERS")
c.rect(x_pos, y - HDR_H, POS_W, HDR_H)
c.saveState(); c.translate(x_pos + POS_W / 2 + 2, y - HDR_H + 1.5); c.rotate(90)
c.setFont("Helvetica-Bold", 5.5); c.drawString(0, 0, "POS"); c.restoreState()
c.setFont("Helvetica-Bold", 8)
for i in range(INN):
    x = x_inn + i * INN_W
    c.rect(x, y - HDR_H, INN_W, HDR_H)
    c.drawCentredString(x + INN_W / 2, y - HDR_H + 3.5, str(i + 1))
for j, s in enumerate(RAIL):
    x = x_rail + j * RAIL_W
    c.rect(x, y - HDR_H, RAIL_W, HDR_H)
    c.saveState(); c.translate(x + RAIL_W / 2 + 2, y - HDR_H + 2); c.rotate(90)
    c.setFont("Helvetica-Bold", 5.5); c.drawString(0, 0, s); c.restoreState()
y -= HDR_H

# ---------- one inning cell ----------
def cell(x, yb, w, h):
    """Diamond with arc top, circling labels on right strip, count boxes."""
    strip = 11
    dx0, dw = x + 1, w - strip - 2          # diamond zone
    cx = dx0 + dw / 2
    cy = yb + h * 0.52
    r = min(dw / 2 - 1, h * 0.40)
    p = c.beginPath()
    p.moveTo(cx, cy - r)                    # home (bottom vertex)
    p.lineTo(cx + r, cy)                    # 1st
    p.lineTo(cx, cy + r)                    # 2nd (top vertex)
    p.lineTo(cx - r, cy)                    # 3rd
    p.close()
    c.setLineWidth(0.55)
    c.drawPath(p)
    c.arc(cx - r, cy - r, cx + r, cy + r, 0, 180)   # rounded top over diamond
    # right strip labels (circle-to-mark)
    c.setFont("Helvetica", 3.3)
    labels = ["HR", "3B", "2B", "1B", "SAC", "HP", "BB"]
    for k, lab in enumerate(labels):
        ly = yb + h - 4 - k * (h - 6) / 6.4
        c.drawRightString(x + w - 1, ly, lab)
    # ball/strike count boxes: 2 rows x 3 cols, bottom area left of strip
    bs = 3.2
    bx = x + w - strip - bs * 3 - 1.5
    by = yb + 1.5
    c.setLineWidth(0.4)
    for rr in range(2):
        for cc in range(3):
            c.rect(bx + cc * bs, by + rr * bs, bs, bs)
    c.setLineWidth(0.7)

# ---------- player blocks ----------
for b in range(BLOCKS):
    yb_top = y - b * BLOCK_H            # top of this block
    yb = yb_top - BLOCK_H               # bottom
    # name + sub rows
    c.rect(x0, yb + SUB_H, PLY_W, NAME_H)
    c.rect(x0, yb, PLY_W, SUB_H)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(x0 + 2, yb + 2.2, "Sub.")
    c.rect(x_pos, yb, POS_W, BLOCK_H)
    for i in range(INN):
        x = x_inn + i * INN_W
        c.rect(x, yb, INN_W, BLOCK_H)
        cell(x, yb, INN_W, BLOCK_H)
    for j in range(len(RAIL)):
        c.rect(x_rail + j * RAIL_W, yb, RAIL_W, BLOCK_H)
y -= BLOCKS * BLOCK_H

# ---------- summary block (THE MOD: AWAY/HOME rows, RUNS over HITS each) ----------
teams = ["AWAY", "HOME"]
lbl_w = PLY_W * 0.55                      # team label box
for k, team in enumerate(teams):
    yr = y - (k + 1) * SUM_H
    # team box
    c.rect(x0, yr, lbl_w, SUM_H)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x0 + lbl_w / 2, yr + SUM_H / 2 - 2.5, team)
    # diagonal label cell (right part of players col + POS col)
    lx, lw_ = x0 + lbl_w, (PLY_W - lbl_w) + POS_W
    c.rect(lx, yr, lw_, SUM_H)
    c.line(lx, yr, lx + lw_, yr + SUM_H)
    c.setFont("Helvetica-Bold", 4.6)
    c.drawString(lx + 2, yr + SUM_H - 5.5, "RUNS")
    c.drawRightString(lx + lw_ - 2, yr + 2, "HITS")
    # slashed inning boxes
    for i in range(INN):
        x = x_inn + i * INN_W
        c.rect(x, yr, INN_W, SUM_H)
        c.line(x, yr, x + INN_W, yr + SUM_H)
# rail footer totals (one tall box per rail col with rotated label)
for j, s in enumerate(RAIL):
    x = x_rail + j * RAIL_W
    c.rect(x, y - 2 * SUM_H, RAIL_W, 2 * SUM_H)
    c.saveState(); c.translate(x + RAIL_W / 2 + 2, y - 2 * SUM_H + 4); c.rotate(90)
    c.setFont("Helvetica-Bold", 5.5); c.drawString(0, 0, s); c.restoreState()
y -= 2 * SUM_H + 8

# ---------- pitchers table ----------
pcols = [("W", 14), ("L", 14), ("S", 14), ("PITCHERS", 132), ("IP", 26), ("AB", 26),
         ("H", 26), ("R", 26), ("ER", 26), ("BB", 26), ("SO", 26), ("HR", 26),
         ("BK", 26), ("WP", 26), ("HB", 26)]
px = x0
c.setFont("Helvetica-Bold", 6)
for name, wd in pcols:
    c.rect(px, y - PIT_ROW_H, wd, PIT_ROW_H)
    c.drawCentredString(px + wd / 2, y - PIT_ROW_H + 3.5, name)
    for rix in range(PIT_ROWS):
        c.rect(px, y - PIT_ROW_H * (rix + 2), wd, PIT_ROW_H)
    px += wd
# brand
c.setFont("Helvetica-Bold", 8)
c.drawRightString(x_end, y - PIT_ROW_H * (PIT_ROWS + 1) + 2, "www.USAsoftball.com")

c.save()
print("saved usa-softball-scoresheet.pdf")
