const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Rachel Ma & Joel Li";
pres.title = "AI-Enabled Care Prioritization System";

// ── Color Palette (Healthcare: deep teal + warm accents) ─────────────────
const C = {
  dark:    "0B2545",  // deep navy
  mid:     "13547A",  // teal
  accent:  "E8443A",  // warm red (urgency)
  light:   "F0F4F8",  // ice gray
  white:   "FFFFFF",
  text:    "1B2A4A",  // dark text
  muted:   "6B7B8D",  // secondary text
  green:   "2CA02C",
  orange:  "FF7F0E",
  yellow:  "F5C518",
  critical:"D62728",
};

const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ══════════════════════════════════════════════════════════════════════════
let s1 = pres.addSlide();
s1.background = { color: C.dark };

// Subtle top line accent
s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent } });

s1.addText("AI-Enabled Care\nPrioritization System", {
  x: 0.8, y: 1.0, w: 8.4, h: 2.2,
  fontSize: 40, fontFace: "Trebuchet MS", color: C.white, bold: true,
  lineSpacingMultiple: 1.1, margin: 0,
});

s1.addText("Context-aware care gap detection for Island Health, BC", {
  x: 0.8, y: 3.2, w: 8.4, h: 0.5,
  fontSize: 18, fontFace: "Calibri", color: "8EAEC0", italic: true, margin: 0,
});

// Divider line
s1.addShape(pres.shapes.LINE, { x: 0.8, y: 4.0, w: 2.5, h: 0, line: { color: C.accent, width: 3 } });

s1.addText("Rachel Ma  &  Joel Li", {
  x: 0.8, y: 4.3, w: 5, h: 0.4,
  fontSize: 16, fontFace: "Calibri", color: "CADCFC", margin: 0,
});

s1.addText("UVic Healthcare AI Hackathon  ·  March 2026  ·  Track 2: Population Health & Health Equity", {
  x: 0.8, y: 4.75, w: 8, h: 0.35,
  fontSize: 12, fontFace: "Calibri", color: "6B8BA4", margin: 0,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 2 — The Problem
// ══════════════════════════════════════════════════════════════════════════
let s2 = pres.addSlide();
s2.background = { color: C.light };

s2.addText("The Problem", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

// Big stat callouts — two columns
// Left stat
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 1.3, w: 4.0, h: 1.6, fill: { color: C.white },
  shadow: makeShadow(),
});
s2.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 0.08, h: 1.6, fill: { color: C.accent } });
s2.addText("1 in 5", {
  x: 1.1, y: 1.35, w: 3.5, h: 0.8,
  fontSize: 44, fontFace: "Trebuchet MS", color: C.accent, bold: true, margin: 0,
});
s2.addText("BC residents lack a family doctor", {
  x: 1.1, y: 2.15, w: 3.5, h: 0.6,
  fontSize: 14, fontFace: "Calibri", color: C.text, margin: 0,
});

// Right stat
s2.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.3, w: 4.0, h: 1.6, fill: { color: C.white },
  shadow: makeShadow(),
});
s2.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 0.08, h: 1.6, fill: { color: C.orange } });
s2.addText("78", {
  x: 5.5, y: 1.35, w: 3.5, h: 0.8,
  fontSize: 44, fontFace: "Trebuchet MS", color: C.orange, bold: true, margin: 0,
});
s2.addText("BC communities with vastly different\naccess to primary care", {
  x: 5.5, y: 2.15, w: 3.5, h: 0.6,
  fontSize: 14, fontFace: "Calibri", color: C.text, margin: 0,
});

// Problem bullets
s2.addText([
  { text: "Patients cycle through EDs without continuity of care", options: { bullet: true, breakLine: true } },
  { text: "Care coordinators have no systematic way to identify who needs outreach most", options: { bullet: true, breakLine: true } },
  { text: "Existing tools look at clinical data OR community data — never both together", options: { bullet: true, breakLine: true } },
  { text: "A patient with uncontrolled diabetes in a GP-shortage community is at compound risk", options: { bullet: true } },
], {
  x: 0.8, y: 3.3, w: 8.4, h: 2.0,
  fontSize: 15, fontFace: "Calibri", color: C.text,
  paraSpaceAfter: 8, bullet: { color: C.accent },
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 3 — Our Solution
// ══════════════════════════════════════════════════════════════════════════
let s3 = pres.addSlide();
s3.background = { color: C.white };

s3.addText("Our Solution", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

s3.addText("Fuse patient clinical risk with community structural barriers into one actionable priority score", {
  x: 0.8, y: 1.0, w: 8.4, h: 0.5,
  fontSize: 16, fontFace: "Calibri", color: C.muted, italic: true, margin: 0,
});

// Three-column feature cards
const features = [
  { title: "Priority Queue", desc: "Ranked patient list with\n\"Why Now?\" reasoning:\nClinical Need, Access Barrier,\nSystem Impact", color: C.critical },
  { title: "Intervention Planner", desc: "Given N outreach capacity,\nselect optimal patients,\nestimate avoided ED visits\nand cost savings", color: C.orange },
  { title: "Scenario Simulator", desc: "What-if: improve primary care\nattachment in a community,\nsee tier shifts and\nprojected impact", color: C.mid },
];

features.forEach((f, i) => {
  const x = 0.8 + i * 3.1;
  s3.addShape(pres.shapes.RECTANGLE, {
    x, y: 1.8, w: 2.8, h: 2.8, fill: { color: C.light },
    shadow: makeShadow(),
  });
  s3.addShape(pres.shapes.RECTANGLE, { x, y: 1.8, w: 2.8, h: 0.06, fill: { color: f.color } });
  s3.addText(f.title, {
    x: x + 0.2, y: 2.0, w: 2.4, h: 0.5,
    fontSize: 17, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
  });
  s3.addText(f.desc, {
    x: x + 0.2, y: 2.55, w: 2.4, h: 1.8,
    fontSize: 13, fontFace: "Calibri", color: C.text, margin: 0,
  });
});

// Bottom note
s3.addText("+ AI-generated natural-language rationale per patient (Claude 3.5 Haiku)  ·  Full 78-community BC vulnerability ranking  ·  Opioid & wait time context", {
  x: 0.8, y: 4.9, w: 8.4, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.muted, margin: 0,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 4 — How It Works (Architecture)
// ══════════════════════════════════════════════════════════════════════════
let s4 = pres.addSlide();
s4.background = { color: C.white };

s4.addText("How It Works", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

// Left pipeline: Track 1
s4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.3, w: 3.0, h: 2.0, fill: { color: "EBF5FB" },
  shadow: makeShadow(),
});
s4.addText("Track 1: Patient Data", {
  x: 0.7, y: 1.4, w: 2.6, h: 0.4,
  fontSize: 14, fontFace: "Trebuchet MS", color: C.mid, bold: true, margin: 0,
});
s4.addText([
  { text: "Encounters & ED visits", options: { bullet: true, breakLine: true } },
  { text: "Lab results (HbA1c, troponin)", options: { bullet: true, breakLine: true } },
  { text: "Medications (polypharmacy)", options: { bullet: true, breakLine: true } },
  { text: "AMA history, follow-up gaps", options: { bullet: true } },
], {
  x: 0.7, y: 1.85, w: 2.6, h: 1.3,
  fontSize: 11, fontFace: "Calibri", color: C.text, paraSpaceAfter: 3,
  bullet: { color: C.mid },
});

// Right pipeline: Track 2
s4.addShape(pres.shapes.RECTANGLE, {
  x: 6.5, y: 1.3, w: 3.0, h: 2.0, fill: { color: "FEF3E2" },
  shadow: makeShadow(),
});
s4.addText("Track 2: Community Data", {
  x: 6.7, y: 1.4, w: 2.6, h: 0.4,
  fontSize: 14, fontFace: "Trebuchet MS", color: C.orange, bold: true, margin: 0,
});
s4.addText([
  { text: "% without family doctor", options: { bullet: true, breakLine: true } },
  { text: "Poverty, opioid overdose rates", options: { bullet: true, breakLine: true } },
  { text: "CIHI elective wait times", options: { bullet: true, breakLine: true } },
  { text: "78 BC communities", options: { bullet: true } },
], {
  x: 6.7, y: 1.85, w: 2.6, h: 1.3,
  fontSize: 11, fontFace: "Calibri", color: C.text, paraSpaceAfter: 3,
  bullet: { color: C.orange },
});

// Arrows pointing down
s4.addText("↓", { x: 1.5, y: 3.35, w: 1, h: 0.4, fontSize: 24, color: C.mid, align: "center", margin: 0 });
s4.addText("↓", { x: 7.5, y: 3.35, w: 1, h: 0.4, fontSize: 24, color: C.orange, align: "center", margin: 0 });

// Score boxes
s4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.75, w: 3.0, h: 0.65, fill: { color: C.mid },
});
s4.addText("Patient Risk Score  (0–100)", {
  x: 0.5, y: 3.75, w: 3.0, h: 0.65,
  fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle", margin: 0,
});

s4.addShape(pres.shapes.RECTANGLE, {
  x: 6.5, y: 3.75, w: 3.0, h: 0.65, fill: { color: C.orange },
});
s4.addText("Community Vuln. Score  (0–100)", {
  x: 6.5, y: 3.75, w: 3.0, h: 0.65,
  fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle", margin: 0,
});

// Convergence arrows
s4.addText("→", { x: 3.5, y: 3.75, w: 0.6, h: 0.65, fontSize: 28, color: C.muted, align: "center", valign: "middle", margin: 0 });
s4.addText("←", { x: 5.9, y: 3.75, w: 0.6, h: 0.65, fontSize: 28, color: C.muted, align: "center", valign: "middle", margin: 0 });

// Combined score box (center)
s4.addShape(pres.shapes.RECTANGLE, {
  x: 3.8, y: 4.7, w: 2.4, h: 0.7, fill: { color: C.dark },
  shadow: makeShadow(),
});
s4.addText("Combined Priority Score", {
  x: 3.8, y: 4.7, w: 2.4, h: 0.4,
  fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, align: "center", margin: 0,
});
s4.addText("60% clinical  +  40% community", {
  x: 3.8, y: 5.05, w: 2.4, h: 0.3,
  fontSize: 10, fontFace: "Calibri", color: "8EAEC0", align: "center", margin: 0,
});

// Arrow down to formula
s4.addText("↓", { x: 4.5, y: 4.4, w: 1, h: 0.35, fontSize: 22, color: C.dark, align: "center", margin: 0 });

// Linkage note
s4.addText("Linkage: Patient postal code (FSA) → BC Community Health Service Area (CHSA)  —  CIHI area-based approach", {
  x: 0.5, y: 1.05, w: 9, h: 0.25,
  fontSize: 10, fontFace: "Calibri", color: C.muted, italic: true, margin: 0,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Scoring Deep Dive
// ══════════════════════════════════════════════════════════════════════════
let s5 = pres.addSlide();
s5.background = { color: C.light };

s5.addText("Scoring & Tier Assignment", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

// Left: Patient risk components
s5.addText("Patient Risk (7 components)", {
  x: 0.8, y: 1.15, w: 4, h: 0.4,
  fontSize: 16, fontFace: "Trebuchet MS", color: C.mid, bold: true, margin: 0,
});

const riskItems = [
  ["ED visit frequency (12mo)", "25 pts"],
  ["Chronic disease control", "20 pts"],
  ["Polypharmacy", "15 pts"],
  ["Left-AMA history", "15 pts"],
  ["Post-discharge follow-up gap", "10 pts"],
  ["Wait time burden (Track 2)", "10 pts"],
  ["Language barrier", "5 pts"],
];

let tableRows = riskItems.map(([name, pts]) => [
  { text: name, options: { fontSize: 12, fontFace: "Calibri", color: C.text } },
  { text: pts, options: { fontSize: 12, fontFace: "Calibri", color: C.mid, bold: true, align: "right" } },
]);

s5.addTable(tableRows, {
  x: 0.8, y: 1.6, w: 4.2, colW: [3.2, 1.0],
  rowH: 0.33,
  border: { type: "none" },
  fill: { color: C.white },
});

// Right: Tier assignment
s5.addText("Priority Tiers (percentile-based)", {
  x: 5.5, y: 1.15, w: 4, h: 0.4,
  fontSize: 16, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

const tiers = [
  { name: "CRITICAL", pct: "Top 5%", action: "Outreach within 48h", color: C.critical },
  { name: "HIGH", pct: "80th–95th", action: "Follow-up in 2 weeks", color: C.orange },
  { name: "MEDIUM", pct: "50th–80th", action: "Add to watchlist", color: C.yellow },
  { name: "LOW", pct: "Bottom 50%", action: "Standard recall", color: C.green },
];

tiers.forEach((t, i) => {
  const y = 1.7 + i * 0.85;
  s5.addShape(pres.shapes.RECTANGLE, {
    x: 5.5, y, w: 4.0, h: 0.7, fill: { color: C.white },
    shadow: makeShadow(),
  });
  s5.addShape(pres.shapes.RECTANGLE, { x: 5.5, y, w: 0.08, h: 0.7, fill: { color: t.color } });
  s5.addText(t.name, {
    x: 5.75, y, w: 1.3, h: 0.35,
    fontSize: 13, fontFace: "Trebuchet MS", color: t.color, bold: true, margin: 0,
  });
  s5.addText(t.pct, {
    x: 7.1, y, w: 1.0, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: C.muted, margin: 0,
  });
  s5.addText(t.action, {
    x: 5.75, y: y + 0.32, w: 3.5, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: C.text, margin: 0,
  });
});

// Bottom note
s5.addText("All weights and thresholds are explicit in config.py — fully auditable, no black box.", {
  x: 0.8, y: 5.0, w: 8.4, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.muted, italic: true, margin: 0,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 6 — Impact & Demo Results
// ══════════════════════════════════════════════════════════════════════════
let s6 = pres.addSlide();
s6.background = { color: C.white };

s6.addText("Impact — What the System Reveals", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

// Big metric cards
const metrics = [
  { num: "2,000", label: "Patients scored\nand ranked", color: C.mid },
  { num: "349", label: "High-priority patients\nlacking GP access", color: C.accent },
  { num: "170", label: "Preventable ED\nvisits per year", color: C.orange },
  { num: "$85K", label: "Potential annual\ncost savings", color: C.green },
];

metrics.forEach((m, i) => {
  const x = 0.5 + i * 2.4;
  s6.addShape(pres.shapes.RECTANGLE, {
    x, y: 1.3, w: 2.15, h: 1.8, fill: { color: C.light },
    shadow: makeShadow(),
  });
  s6.addShape(pres.shapes.RECTANGLE, { x, y: 1.3, w: 2.15, h: 0.06, fill: { color: m.color } });
  s6.addText(m.num, {
    x, y: 1.5, w: 2.15, h: 0.7,
    fontSize: 36, fontFace: "Trebuchet MS", color: m.color, bold: true, align: "center", margin: 0,
  });
  s6.addText(m.label, {
    x, y: 2.25, w: 2.15, h: 0.7,
    fontSize: 12, fontFace: "Calibri", color: C.text, align: "center", margin: 0,
  });
});

// Key insights
s6.addText("Key Insights from the Demo", {
  x: 0.8, y: 3.5, w: 8, h: 0.4,
  fontSize: 18, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

s6.addText([
  { text: "Intervention Planner: ", options: { bold: true } },
  { text: "Outreaching just 50 patients avoids 96 ED visits/yr ($48K savings)", options: { breakLine: true } },
  { text: "Scenario Simulator: ", options: { bold: true } },
  { text: "5pp improvement in GP attachment shifts 547 patients to lower-urgency tiers", options: { breakLine: true } },
  { text: "\"Why Now?\" module: ", options: { bold: true } },
  { text: "Each patient has structured reasoning — Clinical Need, Access Barrier, System Impact", options: {} },
], {
  x: 0.8, y: 3.95, w: 8.4, h: 1.5,
  fontSize: 14, fontFace: "Calibri", color: C.text, paraSpaceAfter: 8,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Methodology & Honesty
// ══════════════════════════════════════════════════════════════════════════
let s7 = pres.addSlide();
s7.background = { color: C.light };

s7.addText("Honest by Design", {
  x: 0.8, y: 0.4, w: 8, h: 0.6,
  fontSize: 32, fontFace: "Trebuchet MS", color: C.dark, bold: true, margin: 0,
});

s7.addText("What we built into the system to earn trust", {
  x: 0.8, y: 1.0, w: 8, h: 0.35,
  fontSize: 15, fontFace: "Calibri", color: C.muted, italic: true, margin: 0,
});

// Two columns
// Left: What we do right
s7.addText("Strengths", {
  x: 0.8, y: 1.55, w: 4, h: 0.4,
  fontSize: 18, fontFace: "Trebuchet MS", color: C.mid, bold: true, margin: 0,
});

s7.addText([
  { text: "Explicit, auditable scoring weights", options: { bullet: true, breakLine: true } },
  { text: "\"Why Now?\" explains every patient flag", options: { bullet: true, breakLine: true } },
  { text: "Framed as prioritization, not prediction", options: { bullet: true, breakLine: true } },
  { text: "CIHI area-based linkage approach", options: { bullet: true, breakLine: true } },
  { text: "Uses ALL Track 2 datasets (community,\nwait times, opioid surveillance)", options: { bullet: true } },
], {
  x: 0.8, y: 2.0, w: 4.2, h: 2.5,
  fontSize: 14, fontFace: "Calibri", color: C.text,
  paraSpaceAfter: 6, bullet: { color: C.mid },
});

// Right: What we disclose
s7.addText("Disclosed Limitations", {
  x: 5.5, y: 1.55, w: 4, h: 0.4,
  fontSize: 18, fontFace: "Trebuchet MS", color: C.accent, bold: true, margin: 0,
});

s7.addText([
  { text: "Ecological fallacy: area stats ≠ individual truth", options: { bullet: true, breakLine: true } },
  { text: "No causal validation in this dataset", options: { bullet: true, breakLine: true } },
  { text: "Synthetic patient data (Synthea)", options: { bullet: true, breakLine: true } },
  { text: "FSA→CHSA mapping is approximate", options: { bullet: true, breakLine: true } },
  { text: "30% ED reduction is modelled assumption", options: { bullet: true } },
], {
  x: 5.5, y: 2.0, w: 4.2, h: 2.5,
  fontSize: 14, fontFace: "Calibri", color: C.text,
  paraSpaceAfter: 6, bullet: { color: C.accent },
});

// Bottom callout
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 4.6, w: 8.4, h: 0.7, fill: { color: C.dark },
});
s7.addText("\"A tool that knows what it doesn't know is more trustworthy than one that hides it.\"", {
  x: 1.0, y: 4.6, w: 8.0, h: 0.7,
  fontSize: 15, fontFace: "Calibri", color: C.white, italic: true,
  align: "center", valign: "middle", margin: 0,
});


// ══════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Thank You / Links
// ══════════════════════════════════════════════════════════════════════════
let s8 = pres.addSlide();
s8.background = { color: C.dark };

s8.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent } });

s8.addText("Thank You", {
  x: 0.8, y: 1.2, w: 8.4, h: 1.0,
  fontSize: 44, fontFace: "Trebuchet MS", color: C.white, bold: true, margin: 0,
});

s8.addShape(pres.shapes.LINE, { x: 0.8, y: 2.3, w: 2, h: 0, line: { color: C.accent, width: 3 } });

s8.addText([
  { text: "Live Demo", options: { bold: true, breakLine: true, color: "8EAEC0" } },
  { text: "care-priority.streamlit.app", options: { breakLine: true, color: C.white, hyperlink: { url: "https://care-priority.streamlit.app" } } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "GitHub", options: { bold: true, breakLine: true, color: "8EAEC0" } },
  { text: "github.com/rachel-wenhui-ma/care-priority", options: { color: C.white, hyperlink: { url: "https://github.com/rachel-wenhui-ma/care-priority" } } },
], {
  x: 0.8, y: 2.6, w: 8, h: 2.0,
  fontSize: 18, fontFace: "Calibri", margin: 0, paraSpaceAfter: 4,
});

s8.addText("Rachel Ma  ·  Joel Li  |  Track 2: Population Health & Health Equity", {
  x: 0.8, y: 4.8, w: 8, h: 0.4,
  fontSize: 13, fontFace: "Calibri", color: "6B8BA4", margin: 0,
});


// ── Save ────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "D:\\MADS\\Healthcare Hackathon\\care-priority\\slides2.pptx" })
  .then(() => console.log("slides.pptx created successfully!"))
  .catch(err => console.error(err));
