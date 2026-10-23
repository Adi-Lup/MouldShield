"""Generate the editable Level 1 SVG; no packages needed for this source step."""
from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'diagrams' / 'T15_data_flow_level1.svg'
INK = '#203C73'
parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="2130" viewBox="0 0 2200 2130" role="img" aria-labelledby="dfd-title dfd-description">
<title id="dfd-title">MouldShield data flow diagram, Level 1</title>
<desc id="dfd-description">Four processes authenticate and store sensor readings, assess risk and serve warnings, verify reading integrity, and prepare reports and landlord letters. The external entities remain Device, Tenant, Landlord and Bedrock AI. Repeated Tenant boxes identify the same actor. Data stores contain readings and hashes, reports and photos, and device authentication records. This is a proposed design.</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#203C73"/></marker></defs>
<rect width="2200" height="2130" fill="white"/>
<g font-family="DejaVu Sans,Arial,sans-serif" fill="#142332">''']

def text(x, y, value, size=24, fill='#142332', weight=400, anchor='middle', background=False):
    lines = value.split('\n')
    if background:
        width = max(len(line) for line in lines) * size * .62 + 22
        height = len(lines) * size * 1.35 + 12
        parts.append(f'<rect x="{x-width/2}" y="{y-size-5}" width="{width}" height="{height}" rx="4" fill="white"/>')
    for i, line in enumerate(lines):
        parts.append(f'<text x="{x}" y="{y+i*size*1.35}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(line)}</text>')

def rect(x, y, w, h, fill='white', radius=0):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{INK}" stroke-width="3"/>')

def entity(x, y, w, h, title, subtitle=''):
    rect(x, y, w, h)
    text(x+w/2, y+h/2-5 if subtitle else y+h/2+10, title, 31, weight=700)
    if subtitle:
        text(x+w/2, y+h/2+36, subtitle, 21)

def process(x, y, number, title):
    rect(x, y, 420, 180, '#315F94', 28)
    text(x+210, y+39, number, 26, 'white', 700)
    parts.append(f'<path d="M{x+18} {y+54}H{x+402}" stroke="#BFD3EC" stroke-width="1.5"/>')
    text(x+210, y+100, title, 29, 'white', 600)

def store(x, y, w, number, title):
    rect(x, y, w, 120, '#EDF2F8')
    parts.append(f'<path d="M{x+72} {y}V{y+120}" stroke="{INK}" stroke-width="3"/>')
    text(x+36, y+70, number, 26, INK, 700)
    text(x+72+(w-72)/2, y+68, title, 23)

def arrow(points):
    values = ' '.join(f'{x},{y}' for x,y in points)
    parts.append(f'<polyline points="{values}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linejoin="round" marker-end="url(#arrow)"/>')

text(1100, 58, 'MouldShield — Data flow diagram · Level 1', 39, INK, 700)
text(1100, 102, 'Proposed core system · expansion of your supplied context diagram', 24, INK)

# Named data flows. Separate lanes keep return flows clear.
arrow([(370,230),(650,230)])
arrow([(1070,200),(1530,200)])
arrow([(1530,275),(1070,275)])
arrow([(800,320),(800,430)])
arrow([(940,430),(940,320)])
arrow([(860,550),(860,700)])
arrow([(1070,490),(1740,490),(1740,700)])
arrow([(370,750),(650,750)])
arrow([(650,830),(370,830)])
arrow([(1640,990),(1640,880)])
arrow([(1840,880),(1840,990)])
arrow([(860,880),(860,1400)])
arrow([(650,490),(500,490),(500,1320),(750,1320),(750,1400)])
arrow([(1530,800),(1310,800),(1310,1320),(1020,1320),(1020,1400)])
arrow([(370,1460),(650,1460)])
arrow([(650,1540),(370,1540)])
arrow([(1070,1450),(1530,1450)])
arrow([(1530,1540),(1070,1540)])
arrow([(780,1580),(780,1840)])
arrow([(940,1840),(940,1580)])
arrow([(1030,1580),(1030,1730),(1740,1730),(1740,1840)])

# Nodes are drawn after routes, leaving clear attachment points.
entity(70,175,300,110,'Device','StickS3 + ENV-III')
process(650,140,'1.0','Authenticate device\nand store readings')
store(1530,155,550,'D3','Device authentication records')
store(650,430,420,'D1','Readings + hash chain')
entity(70,700,300,180,'Tenant','same external entity')
process(650,700,'2.0','Assess readings and\nserve risk warnings')
process(1530,700,'3.0','Verify reading\nintegrity')
entity(1530,990,420,160,'Tenant','same external entity')
entity(70,1400,300,180,'Tenant','same external entity')
process(650,1400,'4.0','Prepare report\nand landlord letter')
entity(1530,1400,420,180,'Bedrock AI')
store(650,1840,420,'D2','Reports + photo records')
entity(1530,1840,420,120,'Landlord')

# Flow labels sit in reserved whitespace and do not overlap nodes.
for x,y,value in [
    (510,190,'Sensor data +\nauthentication'),
    (1300,176,'Device ID lookup'),
    (1300,252,'Authentication record'),
    (685,365,'New reading\n+ hash'),
    (1050,365,'Previous hash'),
    (860,620,'Temperature, humidity\nand timestamps'),
    (1410,465,'Readings + stored hashes'),
    (510,730,'Dashboard request'),
    (510,806,'Readings, risk level\nand warnings'),
    (1450,935,'Verification\nrequest'),
    (2000,935,'Integrity\nresult'),
    (860,1080,'Risk summary'),
    (500,1190,'Selected sensor\nreadings'),
    (1310,1190,'Verification result\nrequired for report'),
    (510,1408,'Report request,\nphoto + language +\nlandlord details'),
    (510,1518,'Explanation, report\nand letter'),
    (1300,1408,'Reading summary, language\nand optional damp photo'),
    (1300,1518,'Analysis + translated\nexplanation'),
    (660,1660,'Report, letter\n+ photo record'),
    (950,1660,'Saved\nreport'),
    (1460,1705,'Tenant-approved report + letter')
]:
    text(x,y,value,20,background=True)

parts.append('<path d="M70 2010H2130" stroke="#9AAFCB" stroke-width="2"/>')
text(1100,2050,'Rectangles: external entities · Rounded boxes: processes · Numbered stores: D1–D3',23,INK)
text(1100,2090,'Repeated Tenant boxes refer to one actor. Arrows carry data; this diagram does not claim live services are connected.',21)
parts.append('</g></svg>')
OUT.write_text('\n'.join(parts),encoding='utf-8')
print(OUT)
