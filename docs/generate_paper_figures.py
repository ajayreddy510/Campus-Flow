from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")
BOLD_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
INK = "#17212B"
BLUE = "#315A73"
PALE = "#EAF0F3"
MID = "#C8D3DA"
WHITE = "#FFFFFF"
GREEN = "#E8F2EC"
GOLD = "#F4F0E4"


def font(size, bold=False):
    path = BOLD_PATH if bold else FONT_PATH
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def wrapped_lines(draw, text, fnt, max_width):
    result = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                line = candidate
            else:
                if line:
                    result.append(line)
                line = word
        result.append(line)
    return result


def box(draw, bounds, text, *, fill=WHITE, outline=BLUE, size=34, bold=False, radius=22, padding=22):
    left, top, right, bottom = bounds
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=4)
    fnt = font(size, bold)
    lines = wrapped_lines(draw, text, fnt, right - left - 2 * padding)
    heights = [draw.textbbox((0, 0), line, font=fnt)[3] for line in lines]
    y = (top + bottom - sum(heights) - (len(lines) - 1) * 8) / 2
    for line, height in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=fnt)[2]
        draw.text((left + (right - left - width) / 2, y), line, font=fnt, fill=INK)
        y += height + 8


def arrow(draw, start, end, color=INK, width=5, head=18):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - sign * head, y2 - head * 0.65), (x2 - sign * head, y2 + head * 0.65)]
    else:
        sign = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - head * 0.65, y2 - sign * head), (x2 + head * 0.65, y2 - sign * head)]
    draw.polygon(points, fill=color)


def heading(draw, title, subtitle, width):
    draw.text((70, 38), title, font=font(46, True), fill=INK)
    draw.text((72, 98), subtitle, font=font(26), fill=BLUE)
    draw.line((70, 145, width - 70, 145), fill=MID, width=3)


def architecture():
    image = Image.new("RGB", (2000, 1120), WHITE)
    draw = ImageDraw.Draw(image)
    heading(draw, "CampusFlow system architecture", "Browser client, modular API, domain services, and shared relational persistence", 2000)

    box(draw, (640, 180, 1360, 275), "Students  |  Placement officers  |  Administrators", fill=GOLD, size=31, bold=True)
    box(draw, (700, 360, 1300, 465), "React + TypeScript web client", fill=PALE, size=34, bold=True)
    box(draw, (700, 520, 1300, 625), "FastAPI application  |  JWT authentication  |  RBAC", fill=PALE, size=31, bold=True)
    arrow(draw, (1000, 275), (1000, 355))
    arrow(draw, (1000, 465), (1000, 520))

    box(draw, (90, 720, 650, 855), "Profiles and deterministic eligibility", fill=WHITE, size=29, bold=True)
    box(draw, (720, 720, 1280, 855), "Companies, drives, registrations, stages", fill=WHITE, size=29, bold=True)
    box(draw, (1350, 720, 1910, 855), "Analytics, notifications, audit", fill=WHITE, size=29, bold=True)
    arrow(draw, (850, 625), (380, 715))
    arrow(draw, (1000, 625), (1000, 715))
    arrow(draw, (1150, 625), (1620, 715))

    # Service modules feed a shared persistence bus to avoid misleading crossings.
    arrow(draw, (380, 855), (380, 930), color=BLUE)
    arrow(draw, (1000, 855), (1000, 930), color=BLUE)
    arrow(draw, (1620, 855), (1620, 930), color=BLUE)
    draw.line((380, 930, 1620, 930), fill=BLUE, width=5)
    arrow(draw, (1000, 930), (1000, 975), color=BLUE)
    box(draw, (700, 980, 1300, 1085), "PostgreSQL", fill=GREEN, size=34, bold=True)

    image.save(OUT / "campusflow_architecture.png", dpi=(240, 240), optimize=True)


def workflow():
    image = Image.new("RGB", (1300, 1900), WHITE)
    draw = ImageDraw.Draw(image)
    heading(draw, "Placement-drive lifecycle", "A drive advances through explicit officer-controlled states", 1300)

    stages = [
        ("1  Draft", "Officer creates company-linked drive and configures criteria."),
        ("2  Published", "Drive becomes visible to students; eligible recipients can be notified."),
        ("3  Registration open", "Student checks eligibility and submits a registration."),
        ("4  Registration closed", "Deadline passes or officer closes registration."),
        ("5  Shortlisting", "Officer reviews applicants and assigns candidates to stages."),
        ("6  Assessment and interview", "Stage schedules, instructions, and candidate outcomes are tracked."),
        ("7  Result and completion", "Results are published and the drive is completed."),
    ]
    top = 190
    box_h = 165
    gap = 65
    for index, (title, body) in enumerate(stages):
        y = top + index * (box_h + gap)
        fill = GREEN if index in (2, 6) else PALE
        box(draw, (150, y, 1150, y + box_h), f"{title}\n{body}", fill=fill, size=32, bold=False, padding=45)
        if index < len(stages) - 1:
            arrow(draw, (650, y + box_h), (650, y + box_h + gap - 10))
    image.save(OUT / "placement_lifecycle.png", dpi=(220, 220), optimize=True)


def eligibility_notifications():
    image = Image.new("RGB", (2000, 1200), WHITE)
    draw = ImageDraw.Draw(image)
    heading(draw, "Eligibility and notification processing", "Eligibility decisions are deterministic; notification delivery is asynchronous", 2000)

    draw.text((90, 185), "A. Eligibility check", font=font(32, True), fill=BLUE)
    box(draw, (80, 260, 440, 410), "Student profile\nCGPA, branch, batch, backlogs, gender", fill=GOLD, size=27)
    box(draw, (565, 260, 1040, 410), "Drive criteria\nConfigured by placement officer", fill=GOLD, size=27)
    box(draw, (300, 540, 820, 705), "EligibilityService\nEvaluate each configured rule", fill=PALE, size=31, bold=True)
    arrow(draw, (270, 410), (465, 535))
    arrow(draw, (800, 410), (650, 535))
    box(draw, (90, 850, 495, 1010), "Eligible\nRegistration may proceed", fill=GREEN, size=28)
    box(draw, (620, 850, 1060, 1010), "Not eligible\nReturn failed-rule reasons", fill=GOLD, size=28)
    arrow(draw, (485, 705), (300, 845))
    arrow(draw, (650, 705), (840, 845))

    draw.line((1110, 190, 1110, 1100), fill=MID, width=3)
    draw.text((1170, 185), "B. Notification delivery", font=font(32, True), fill=BLUE)
    box(draw, (1180, 270, 1900, 405), "Business event\nDrive published, student shortlisted, result published", fill=GOLD, size=28)
    box(draw, (1180, 510, 1900, 645), "Dispatcher\nBuild recipient payload and idempotency key", fill=PALE, size=28)
    box(draw, (1180, 750, 1500, 885), "Task queue\nRetry boundary", fill=GOLD, size=27)
    box(draw, (1580, 750, 1900, 885), "Worker\nDeduplicate and deliver", fill=PALE, size=27)
    box(draw, (1180, 1000, 1500, 1120), "In-app notification", fill=GREEN, size=25)
    box(draw, (1580, 1000, 1900, 1120), "Optional browser push", fill=GREEN, size=25)
    arrow(draw, (1540, 405), (1540, 505))
    arrow(draw, (1540, 645), (1340, 745))
    arrow(draw, (1500, 820), (1575, 820))
    arrow(draw, (1670, 885), (1470, 995))
    arrow(draw, (1740, 885), (1740, 995))

    image.save(OUT / "eligibility_notifications.png", dpi=(240, 240), optimize=True)


if __name__ == "__main__":
    architecture()
    workflow()
    eligibility_notifications()
    print(f"Generated PNG figures in {OUT}")
