"""
╔══════════════════════════════════════════════════════════════╗
║  AIRCRAFT FDM — CONDITIONS 1, 2, 3 & 4                      ║
║  • Condition 1: Engine Temp  ≥ 850°C  → WARNING             ║
║                              ≥ 950°C  → CRITICAL            ║
║  • Condition 2: Fuel Level   ≤ 30%   → WARNING              ║
║                              ≤ 20%   → CRITICAL             ║
║  • Condition 3: Roll Angle   > ±40°  → ALERT                ║
║                              > ±45°  → INSTABILITY          ║
║  • Condition 4: Altitude Drop> 500ft → WARNING              ║
║                              >1000ft → EMERGENCY            ║
║                                                              ║
║  Run:  streamlit run fdm_conditions_1_2_3_4.py               ║
║  Pip:  pip install streamlit pandas plotly numpy             ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aircraft FDM — All 4 Conditions",
    page_icon="✈",
    layout="wide",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #000d1a; }
    [data-testid="stSidebar"]          { background-color: #020c18; border-right: 1px solid #1a3045; }
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    h1, h2, h3, h4   { font-family: monospace !important; letter-spacing: 1px; }
    .section-banner {
        padding: 10px 18px;
        border-radius: 6px;
        margin: 22px 0 14px 0;
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 2px;
        border-left: 5px solid;
    }
    .kpi-box {
        background: #050f1e;
        border: 1px solid #1a3045;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        font-family: monospace;
    }
    .kpi-val   { font-size: 26px; font-weight: bold; line-height: 1.2; }
    .kpi-label { font-size: 10px; color: #5577aa; letter-spacing: 2px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  SIMULATION — ENGINE TEMP + FUEL LEVEL + ROLL ANGLE + ALTITUDE
# ─────────────────────────────────────────────────────────────
np.random.seed(42)
DURATION = 30
TIME     = np.arange(DURATION)
LABELS   = [f"T+{t:02d}m" for t in TIME]

PHASES = [
    "Takeoff"  if t < 3  else
    "Climb"    if t < 8  else
    "Cruise"   if t < 22 else
    "Descent"  if t < 27 else
    "Approach"
    for t in TIME
]

# ── Engine Temperature ────────────────────────────────────────
eng = np.zeros(DURATION); eng[0] = 620
for i in range(1, DURATION):
    p = PHASES[i]
    if   p == "Takeoff": eng[i] = eng[i-1] + np.random.uniform(15, 30)
    elif p == "Climb":   eng[i] = eng[i-1] + np.random.uniform(20, 35)
    elif p == "Cruise":
        if   i == 10: eng[i] = 862      # ← WARNING anomaly
        elif i == 14: eng[i] = 972      # ← CRITICAL anomaly
        elif i == 15: eng[i] = 935
        elif i == 16: eng[i] = 855
        else:          eng[i] = 820 + np.random.uniform(-12, 12)
    elif p == "Descent": eng[i] = eng[i-1] - np.random.uniform(10, 20)
    else:                eng[i] = eng[i-1] - np.random.uniform(15, 25)
eng = np.clip(np.round(eng).astype(int), 400, 1100)

# ── Fuel Level ────────────────────────────────────────────────
fuel = np.zeros(DURATION); fuel[0] = 98.0
for i in range(1, DURATION):
    rate = 2.6 + np.random.uniform(0.5, 1.0)
    if PHASES[i] in ("Takeoff", "Climb"):
        rate *= 1.7
    fuel[i] = fuel[i-1] - rate
fuel = np.clip(np.round(fuel, 1), 0, 100)

# ── Roll Angle ────────────────────────────────────────────────
roll = np.zeros(DURATION)
for i in range(DURATION):
    p = PHASES[i]
    if   p == "Takeoff":  roll[i] = np.random.uniform(-8, 8)
    elif p == "Climb":    roll[i] = np.random.uniform(-12, 12)
    elif p == "Cruise":
        if   i == 11: roll[i] =  42.5
        elif i == 12: roll[i] =  48.0
        elif i == 17: roll[i] = -43.0
        elif i == 18: roll[i] = -41.5
        elif i == 19: roll[i] = -52.0
        elif i == 20: roll[i] = -47.5
        else:          roll[i] = np.random.uniform(-15, 15)
    elif p == "Descent":  roll[i] = np.random.uniform(-18, 18)
    else:                 roll[i] = np.random.uniform(-10, 10)
roll = np.round(roll, 1)

# ── Altitude ──────────────────────────────────────────────────
alt = np.zeros(DURATION); alt[0] = 800
for i in range(1, DURATION):
    p = PHASES[i]
    if   p == "Takeoff": alt[i] = alt[i-1] + np.random.uniform(1800, 2500)
    elif p == "Climb":   alt[i] = alt[i-1] + np.random.uniform(2800, 3500)
    elif p == "Cruise":  alt[i] = 36000 + np.random.uniform(-150, 150)
    elif p == "Descent":
        if   i == 23: alt[i] = alt[i-1] - 620    # ← WARNING drop
        elif i == 25: alt[i] = alt[i-1] - 1350   # ← EMERGENCY drop
        elif i == 26: alt[i] = alt[i-1] - 1100   # ← EMERGENCY drop
        else:          alt[i] = alt[i-1] - np.random.uniform(700, 950)
    else:                alt[i] = alt[i-1] - np.random.uniform(1200, 1800)
alt = np.clip(np.round(alt).astype(int), 0, 42000)

# Drop per minute (index 0 has no previous → 0)
alt_drops = np.array([0] + [int(alt[i-1] - alt[i]) for i in range(1, DURATION)])


# ─────────────────────────────────────────────────────────────
#  SIDEBAR — THRESHOLD SLIDERS
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈ Aircraft FDM")
    st.markdown("**Conditions 1, 2, 3 & 4**")
    st.divider()

    st.markdown("### 🌡 Engine Temp Thresholds")
    eng_warn  = st.slider("Warning (°C)",   800, 900,  850, step=10)
    eng_crit  = st.slider("Critical (°C)",  900, 1000, 950, step=10)

    st.divider()
    st.markdown("### ⛽ Fuel Level Thresholds")
    fuel_warn = st.slider("Low Fuel Warning (%)",    20, 40, 30, step=5)
    fuel_crit = st.slider("Critical Fuel Level (%)",  5, 25, 20, step=5)

    st.divider()
    st.markdown("### 🔄 Roll Angle Thresholds")
    roll_alert  = st.slider("Alert threshold (°)",        30, 44, 40, step=1)
    roll_instab = st.slider("Instability threshold (°)",  41, 60, 45, step=1)

    st.divider()
    st.markdown("### 📉 Altitude Drop Thresholds")
    alt_warn  = st.slider("Warning drop (ft/min)",    300, 800,  500, step=50)
    alt_emerg = st.slider("Emergency drop (ft/min)",  800, 1500, 1000, step=50)

    st.divider()
    st.markdown("### 📋 Flight Info")
    st.markdown("🛫 **FLT - BU01**")
    st.markdown("⏱ **Duration:** 30 minutes")
    st.markdown("📡 **Sampling:** 1 / minute")


# ─────────────────────────────────────────────────────────────
#  STATUS HELPERS
# ─────────────────────────────────────────────────────────────
def eng_status(t):
    if   t >= eng_crit: return "CRITICAL"
    elif t >= eng_warn: return "WARNING"
    return "SAFE"

def fuel_status(f):
    if   f <= fuel_crit: return "CRITICAL"
    elif f <= fuel_warn: return "WARNING"
    return "SAFE"

def roll_status(r):
    abs_r = abs(r)
    if   abs_r > roll_instab: return "INSTABILITY"
    elif abs_r > roll_alert:  return "ALERT"
    return "SAFE"

def alt_drop_status(d):
    if   d >= alt_emerg: return "EMERGENCY"
    elif d >= alt_warn:  return "WARNING"
    return "SAFE"

SEV_BG = {
    "EMERGENCY":   "background-color:#1a0000;color:#ff0033;font-weight:bold",
    "CRITICAL":    "background-color:#2a1000;color:#ff2244;font-weight:bold",
    "WARNING":     "background-color:#1e1600;color:#ffaa00;font-weight:bold",
    "INSTABILITY": "background-color:#1a0030;color:#ff00ff;font-weight:bold",
    "ALERT":       "background-color:#1e1600;color:#ffaa00;font-weight:bold",
    "SAFE":        "background-color:#001a0a;color:#39ff14",
}


# ─────────────────────────────────────────────────────────────
#  BUILD DATAFRAMES
# ─────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "Time":           LABELS,
    "Phase":          PHASES,
    "Eng Temp (°C)":  eng,
    "Eng Status":     [eng_status(t)  for t in eng],
    "Fuel Level (%)": fuel,
    "Fuel Status":    [fuel_status(f) for f in fuel],
    "Roll Angle (°)": roll,
    "Roll Status":    [roll_status(r) for r in roll],
    "Altitude (ft)":  alt,
    "Drop (ft/min)":  alt_drops,
    "Alt Status":     [alt_drop_status(d) for d in alt_drops],
})

# Engine alerts
eng_alerts = df[df["Eng Status"] != "SAFE"][["Time","Phase","Eng Temp (°C)","Eng Status"]].copy().reset_index(drop=True)
eng_alerts.index += 1
eng_alerts["Message"] = eng_alerts.apply(lambda r:
    f"OVERHEAT — {r['Eng Temp (°C)']}°C exceeds CRITICAL limit ({eng_crit}°C). Immediate action!"
    if r["Eng Status"] == "CRITICAL"
    else f"Temp elevated — {r['Eng Temp (°C)']}°C exceeds WARNING ({eng_warn}°C). Monitor closely.",
    axis=1)

# Fuel alerts
fuel_alerts = df[df["Fuel Status"] != "SAFE"][["Time","Phase","Fuel Level (%)","Fuel Status"]].copy().reset_index(drop=True)
fuel_alerts.index += 1
fuel_alerts["Message"] = fuel_alerts.apply(lambda r:
    f"CRITICAL FUEL — {r['Fuel Level (%)']}% remaining. Divert immediately!"
    if r["Fuel Status"] == "CRITICAL"
    else f"Low fuel — {r['Fuel Level (%)']}% remaining. Refuel at next opportunity.",
    axis=1)

# Roll alerts
roll_alerts = df[df["Roll Status"] != "SAFE"][["Time","Phase","Roll Angle (°)","Roll Status"]].copy().reset_index(drop=True)
roll_alerts.index += 1
roll_alerts["Message"] = roll_alerts.apply(lambda r:
    f"⚠ INSTABILITY — Roll {r['Roll Angle (°)']}° exceeds ±{roll_instab}°. Aircraft control at risk!"
    if r["Roll Status"] == "INSTABILITY"
    else f"Roll ALERT — {r['Roll Angle (°)']}° exceeds ±{roll_alert}°. Corrective action advised.",
    axis=1)

# Altitude alerts
alt_alerts = df[df["Alt Status"] != "SAFE"][["Time","Phase","Altitude (ft)","Drop (ft/min)","Alt Status"]].copy().reset_index(drop=True)
alt_alerts.index += 1
alt_alerts["Message"] = alt_alerts.apply(lambda r:
    f"🚨 EMERGENCY — Rapid altitude loss of {r['Drop (ft/min)']} ft in 1 min! Exceeds {alt_emerg} ft threshold."
    if r["Alt Status"] == "EMERGENCY"
    else f"⚠ WARNING — Altitude dropping {r['Drop (ft/min)']} ft/min. Exceeds warning threshold ({alt_warn} ft).",
    axis=1)


# ─────────────────────────────────────────────────────────────
#  HELPER: line chart for engine temp & fuel (existing)
# ─────────────────────────────────────────────────────────────
def make_line_chart(
    y_data, y_label, y_range,
    line_color, fill_color,
    warn_val, crit_val,
    warn_is_upper,
    warn_color="#ffaa00",
    crit_color="#ff2244",
    height=360,
):
    fig = go.Figure()

    phase_changes = [0]
    for i in range(1, DURATION):
        if PHASES[i] != PHASES[i-1]:
            phase_changes.append(i)
    phase_changes.append(DURATION)

    PHASE_CLR = {
        "Takeoff":  "rgba(255,215,0,0.12)",
        "Climb":    "rgba(0,191,255,0.10)",
        "Cruise":   "rgba(57,255,20,0.10)",
        "Descent":  "rgba(255,140,0,0.10)",
        "Approach": "rgba(255,107,53,0.10)",
    }
    for j in range(len(phase_changes)-1):
        s, e = phase_changes[j], phase_changes[j+1]
        p = PHASES[s]
        fig.add_vrect(x0=LABELS[s], x1=LABELS[e-1],
                      fillcolor=PHASE_CLR[p], layer="below", line_width=0)

    if warn_is_upper:
        fig.add_hrect(y0=warn_val, y1=crit_val,   fillcolor=warn_color, opacity=0.06, line_width=0)
        fig.add_hrect(y0=crit_val, y1=y_range[1], fillcolor=crit_color, opacity=0.08, line_width=0)
    else:
        fig.add_hrect(y0=crit_val, y1=warn_val,   fillcolor=warn_color, opacity=0.06, line_width=0)
        fig.add_hrect(y0=y_range[0], y1=crit_val, fillcolor=crit_color, opacity=0.08, line_width=0)

    for i in range(DURATION - 1):
        mid = (y_data[i] + y_data[i+1]) / 2
        if warn_is_upper:
            seg_c = crit_color if mid >= crit_val else warn_color if mid >= warn_val else line_color
        else:
            seg_c = crit_color if mid <= crit_val else warn_color if mid <= warn_val else line_color
        fig.add_trace(go.Scatter(
            x=[LABELS[i], LABELS[i+1]], y=[y_data[i], y_data[i+1]],
            mode="lines", line=dict(color=seg_c, width=3),
            showlegend=False, hoverinfo="skip",
        ))

    fig.add_trace(go.Scatter(
        x=LABELS, y=y_data, mode="markers",
        marker=dict(
            color=[
                crit_color if (warn_is_upper and v >= crit_val) or (not warn_is_upper and v <= crit_val)
                else warn_color if (warn_is_upper and v >= warn_val) or (not warn_is_upper and v <= warn_val)
                else line_color
                for v in y_data
            ],
            size=6, line=dict(color="#000d1a", width=1)
        ),
        name=y_label,
        hovertemplate="<b>%{x}</b><br>" + y_label + ": %{y}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=LABELS, y=y_data, fill="tozeroy", fillcolor=fill_color,
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
    ))

    fig.add_hline(y=warn_val, line_dash="dash", line_color=warn_color, line_width=1.8,
                  annotation_text=f"⚠ WARN {'≥' if warn_is_upper else '≤'}{warn_val}",
                  annotation_font_color=warn_color, annotation_position="top right")
    fig.add_hline(y=crit_val, line_dash="dash", line_color=crit_color, line_width=1.8,
                  annotation_text=f"🔴 CRIT {'≥' if warn_is_upper else '≤'}{crit_val}",
                  annotation_font_color=crit_color, annotation_position="top right")

    alert_x, alert_y, alert_txt, alert_clr = [], [], [], []
    for i, v in enumerate(y_data):
        if warn_is_upper:
            if v >= crit_val:   alert_x.append(LABELS[i]); alert_y.append(v); alert_txt.append("🔴"); alert_clr.append(crit_color)
            elif v >= warn_val: alert_x.append(LABELS[i]); alert_y.append(v); alert_txt.append("⚠"); alert_clr.append(warn_color)
        else:
            if v <= crit_val:   alert_x.append(LABELS[i]); alert_y.append(v); alert_txt.append("🔴"); alert_clr.append(crit_color)
            elif v <= warn_val: alert_x.append(LABELS[i]); alert_y.append(v); alert_txt.append("⚠"); alert_clr.append(warn_color)
    if alert_x:
        fig.add_trace(go.Scatter(
            x=alert_x, y=alert_y, mode="markers+text",
            marker=dict(symbol="triangle-up", size=14, color=alert_clr,
                        line=dict(color="#fff", width=1)),
            text=alert_txt, textposition="top center",
            textfont=dict(size=11), showlegend=False,
            hovertemplate="<b>%{x}</b><br>🔺 Alert: %{y}<extra></extra>",
        ))

    fig.update_layout(
        plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
        font=dict(family="monospace", color="#c8d8e8"),
        xaxis=dict(
    title="Flight Time",
    gridcolor="#0d2035",
    tickfont=dict(size=10),
    tickangle=-30,
    tickmode="array",
    tickvals=LABELS,
    ticktext=LABELS
),
        yaxis=dict(title=y_label, gridcolor="#0d2035", range=y_range),
        height=height, showlegend=False,
        margin=dict(l=60, r=40, t=30, b=50),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────
#  HELPER: roll angle line chart (symmetric ± axis)
# ─────────────────────────────────────────────────────────────
def make_roll_chart(height=380):
    fig = go.Figure()

    phase_changes = [0]
    for i in range(1, DURATION):
        if PHASES[i] != PHASES[i-1]:
            phase_changes.append(i)
    phase_changes.append(DURATION)

    PHASE_CLR = {
        "Takeoff":  "rgba(255,215,0,0.12)",
        "Climb":    "rgba(0,191,255,0.10)",
        "Cruise":   "rgba(57,255,20,0.10)",
        "Descent":  "rgba(255,140,0,0.10)",
        "Approach": "rgba(255,107,53,0.10)",
    }
    for j in range(len(phase_changes)-1):
        s, e = phase_changes[j], phase_changes[j+1]
        p = PHASES[s]
        fig.add_vrect(x0=LABELS[s], x1=LABELS[e-1],
                      fillcolor=PHASE_CLR[p], layer="below", line_width=0)

    ALERT_CLR  = "#ffaa00"
    INSTAB_CLR = "#ff00ff"

    fig.add_hrect(y0= roll_alert,  y1= roll_instab, fillcolor=ALERT_CLR,  opacity=0.07, line_width=0)
    fig.add_hrect(y0= roll_instab, y1= 65,          fillcolor=INSTAB_CLR, opacity=0.09, line_width=0)
    fig.add_hrect(y0=-roll_instab, y1=-roll_alert,  fillcolor=ALERT_CLR,  opacity=0.07, line_width=0)
    fig.add_hrect(y0=-65,          y1=-roll_instab, fillcolor=INSTAB_CLR, opacity=0.09, line_width=0)

    fig.add_hline(y=0, line_color="#2a4a6a", line_width=1)

    fig.add_hline(y= roll_alert,  line_dash="dash", line_color=ALERT_CLR,  line_width=1.8,
                  annotation_text=f"⚠ ALERT +{roll_alert}°",
                  annotation_font_color=ALERT_CLR, annotation_position="top right")
    fig.add_hline(y= roll_instab, line_dash="dash", line_color=INSTAB_CLR, line_width=1.8,
                  annotation_text=f"🚨 INSTAB +{roll_instab}°",
                  annotation_font_color=INSTAB_CLR, annotation_position="top right")
    fig.add_hline(y=-roll_alert,  line_dash="dash", line_color=ALERT_CLR,  line_width=1.8,
                  annotation_text=f"⚠ ALERT -{roll_alert}°",
                  annotation_font_color=ALERT_CLR, annotation_position="bottom right")
    fig.add_hline(y=-roll_instab, line_dash="dash", line_color=INSTAB_CLR, line_width=1.8,
                  annotation_text=f"🚨 INSTAB -{roll_instab}°",
                  annotation_font_color=INSTAB_CLR, annotation_position="bottom right")

    for i in range(DURATION - 1):
        abs_mid = (abs(roll[i]) + abs(roll[i+1])) / 2
        seg_c = (INSTAB_CLR if abs_mid > roll_instab
                 else ALERT_CLR if abs_mid > roll_alert
                 else "#ff3fa4")
        fig.add_trace(go.Scatter(
            x=[LABELS[i], LABELS[i+1]], y=[roll[i], roll[i+1]],
            mode="lines", line=dict(color=seg_c, width=3),
            showlegend=False, hoverinfo="skip",
        ))

    marker_colors = []
    for v in roll:
        abs_v = abs(v)
        if   abs_v > roll_instab: marker_colors.append(INSTAB_CLR)
        elif abs_v > roll_alert:  marker_colors.append(ALERT_CLR)
        else:                     marker_colors.append("#ff3fa4")

    fig.add_trace(go.Scatter(
        x=LABELS, y=roll, mode="markers",
        marker=dict(color=marker_colors, size=7, line=dict(color="#000d1a", width=1)),
        name="Roll Angle",
        hovertemplate="<b>%{x}</b><br>Roll: %{y}°<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=LABELS, y=roll, fill="tozeroy",
        fillcolor="rgba(255,63,164,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))

    ax, ay, atxt, aclr = [], [], [], []
    for i, v in enumerate(roll):
        abs_v = abs(v)
        if abs_v > roll_instab:
            ax.append(LABELS[i]); ay.append(v)
            atxt.append("🚨"); aclr.append(INSTAB_CLR)
        elif abs_v > roll_alert:
            ax.append(LABELS[i]); ay.append(v)
            atxt.append("⚠"); aclr.append(ALERT_CLR)

    if ax:
        fig.add_trace(go.Scatter(
            x=ax, y=ay, mode="markers+text",
            marker=dict(
                symbol=["triangle-up" if v >= 0 else "triangle-down" for v in ay],
                size=14, color=aclr, line=dict(color="#fff", width=1)
            ),
            text=atxt,
            textposition=["top center" if v >= 0 else "bottom center" for v in ay],
            textfont=dict(size=12), showlegend=False,
            hovertemplate="<b>%{x}</b><br>🔺 Roll Alert: %{y}°<extra></extra>",
        ))

    fig.update_layout(
        plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
        font=dict(family="monospace", color="#c8d8e8"),
        xaxis=dict(
            title="Flight Time",
            type="category",
            categoryorder="array",
            categoryarray=LABELS,
            gridcolor="#0d2035",
            tickangle=-30,
            tickmode="array",
            tickvals=LABELS,
            ticktext=LABELS
),
        yaxis=dict(title="Roll Angle (°)", gridcolor="#0d2035",
                   range=[-65, 65], zeroline=False,
                   tickvals=[-60,-45,-40,-30,-20,-10,0,10,20,30,40,45,60],
                   ticktext=["-60°","-45°","-40°","-30°","-20°","-10°","0°",
                              "10°","20°","30°","40°","45°","60°"]),
        height=height, showlegend=False,
        margin=dict(l=70, r=40, t=30, b=50),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────
#  HELPER: altitude profile line chart  ← NEW
# ─────────────────────────────────────────────────────────────
def make_altitude_chart(height=380):
    fig = go.Figure()

    phase_changes = [0]
    for i in range(1, DURATION):
        if PHASES[i] != PHASES[i-1]:
            phase_changes.append(i)
    phase_changes.append(DURATION)

    PHASE_CLR = {
        "Takeoff":  "rgba(255,215,0,0.12)",
        "Climb":    "rgba(0,191,255,0.10)",
        "Cruise":   "rgba(57,255,20,0.10)",
        "Descent":  "rgba(255,140,0,0.10)",
        "Approach": "rgba(255,107,53,0.10)",
    }
    for j in range(len(phase_changes)-1):
        s, e = phase_changes[j], phase_changes[j+1]
        p    = PHASES[s]
        fig.add_vrect(x0=LABELS[s], x1=LABELS[e-1],
                      fillcolor=PHASE_CLR[p], layer="below", line_width=0)
        # Phase label at top
        mid = (s + e - 1) // 2
        fig.add_annotation(
            x=LABELS[mid], y=41500, text=p, showarrow=False,
            font=dict(size=9, color="#c8d8e8"), yanchor="top"
        )

    # Color-coded segments — cyan normal, amber warning drop, red emergency drop
    for i in range(DURATION - 1):
        drop_next = alt_drops[i+1]
        sc = ("#ff0033" if drop_next >= alt_emerg
              else "#ffaa00" if drop_next >= alt_warn
              else "#00d4ff")
        fig.add_trace(go.Scatter(
            x=[LABELS[i], LABELS[i+1]], y=[alt[i], alt[i+1]],
            mode="lines", line=dict(color=sc, width=3),
            showlegend=False, hoverinfo="skip",
        ))

    # Markers
    mcolors = [
        "#ff0033" if alt_drops[i] >= alt_emerg
        else "#ffaa00" if alt_drops[i] >= alt_warn
        else "#00d4ff"
        for i in range(DURATION)
    ]
    fig.add_trace(go.Scatter(
        x=LABELS, y=alt, mode="markers",
        marker=dict(color=mcolors, size=7, line=dict(color="#000d1a", width=1)),
        name="Altitude",
        hovertemplate="<b>%{x}</b><br>Altitude: %{y:,} ft<br>Drop: %{customdata} ft/min<extra></extra>",
        customdata=alt_drops,
    ))

    # Fill under curve
    fig.add_trace(go.Scatter(
        x=LABELS, y=alt, fill="tozeroy",
        fillcolor="rgba(0,212,255,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))

    # Alert markers — ▼ triangles at breach points with drop value label
    ex, ey, etxt, eclr = [], [], [], []
    for i in range(1, DURATION):
        d = alt_drops[i]
        if d >= alt_emerg:
            ex.append(LABELS[i]); ey.append(alt[i])
            etxt.append(f"🚨 -{d} ft"); eclr.append("#ff0033")
        elif d >= alt_warn:
            ex.append(LABELS[i]); ey.append(alt[i])
            etxt.append(f"⚠ -{d} ft"); eclr.append("#ffaa00")
    if ex:
        fig.add_trace(go.Scatter(
            x=ex, y=ey, mode="markers+text",
            marker=dict(symbol="triangle-down", size=14, color=eclr,
                        line=dict(color="#fff", width=1)),
            text=etxt, textposition="bottom center",
            textfont=dict(size=9), showlegend=False,
            hovertemplate="<b>%{x}</b><br>🔻 Drop alert: %{y:,} ft<extra></extra>",
        ))

    fig.update_layout(
        plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
        font=dict(family="monospace", color="#c8d8e8"),
        xaxis=dict(title="Flight Time", gridcolor="#0d2035",
                   tickfont=dict(size=10), tickangle=-30),
        yaxis=dict(title="Altitude (ft)", gridcolor="#0d2035",
                   range=[0, 43000],
                   tickformat=","),
        height=height, showlegend=False,
        margin=dict(l=80, r=40, t=30, b=50),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────
#  HELPER: drop rate line chart  ← NEW
# ─────────────────────────────────────────────────────────────
def make_drop_rate_chart(height=300):
    fig = go.Figure()

    # Color segments by severity
    for i in range(DURATION - 1):
        d_mid = (alt_drops[i] + alt_drops[i+1]) / 2

    if PHASES[i] == "Cruise":
        sc = "#00d4ff55"
    else:
        sc = ("#ff0033" if d_mid >= alt_emerg
              else "#ffaa00" if d_mid >= alt_warn
              else "#00d4ff55")
        fig.add_trace(go.Scatter(
            x=[LABELS[i], LABELS[i+1]], y=[alt_drops[i], alt_drops[i+1]],
            mode="lines", line=dict(color=sc, width=3),
            showlegend=False, hoverinfo="skip",
        ))

    # Markers
    drop_mcolors = [
        "#ff0033" if d >= alt_emerg else "#ffaa00" if d >= alt_warn else "#00d4ff"
        for d in alt_drops
    ]
    fig.add_trace(go.Scatter(
        x=LABELS, y=alt_drops, mode="markers",
        marker=dict(color=drop_mcolors, size=7, line=dict(color="#000d1a", width=1)),
        name="Drop Rate",
        hovertemplate="<b>%{x}</b><br>Drop: %{y} ft/min<extra></extra>",
    ))

    # Fill under
    fig.add_trace(go.Scatter(
        x=LABELS, y=alt_drops, fill="tozeroy",
        fillcolor="rgba(0,212,255,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))

    # Threshold lines + shaded zones
    fig.add_hrect(y0=alt_warn,  y1=alt_emerg, fillcolor="#ffaa00", opacity=0.05, line_width=0)
    fig.add_hrect(y0=alt_emerg, y1=max(alt_drops)+300, fillcolor="#ff0033", opacity=0.07, line_width=0)

    fig.add_hline(y=alt_warn,  line_dash="dash", line_color="#ffaa00", line_width=1.8,
                  annotation_text=f"⚠ WARN {alt_warn} ft/min",
                  annotation_font_color="#ffaa00", annotation_position="top right")
    fig.add_hline(y=alt_emerg, line_dash="dash", line_color="#ff0033", line_width=1.8,
                  annotation_text=f"🚨 EMERGENCY {alt_emerg} ft/min",
                  annotation_font_color="#ff0033", annotation_position="top right")

    # Alert markers on drop chart
    dx, dy, dtxt, dclr = [], [], [], []
    for i in range(DURATION):
        d = alt_drops[i]
        if d >= alt_emerg:
            dx.append(LABELS[i]); dy.append(d); dtxt.append("🚨"); dclr.append("#ff0033")
        elif d >= alt_warn:
            dx.append(LABELS[i]); dy.append(d); dtxt.append("⚠"); dclr.append("#ffaa00")
    if dx:
        fig.add_trace(go.Scatter(
            x=dx, y=dy, mode="markers+text",
            marker=dict(symbol="triangle-up", size=13, color=dclr,
                        line=dict(color="#fff", width=1)),
            text=dtxt, textposition="top center",
            textfont=dict(size=11), showlegend=False,
            hovertemplate="<b>%{x}</b><br>Drop alert: %{y} ft/min<extra></extra>",
        ))

    fig.update_layout(
    plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
    font=dict(family="monospace", color="#c8d8e8"),

    xaxis=dict(
        title="Flight Time",
        gridcolor="#0d2035",
        tickfont=dict(size=10),
        tickangle=-30,
        type="category",                 # <<< FORCE CATEGORY
        categoryorder="array",
        categoryarray=LABELS             # <<< FORCE ORDER T+00 → T+29
    ),

    yaxis=dict(
        title="Altitude Drop (ft/min)",
        gridcolor="#0d2035",
        range=[0, max(alt_drops) + 250]
    ),

    height=height,
    showlegend=False,
    margin=dict(l=80, r=40, t=30, b=50),
    hovermode="x unified",

    )
    return fig


# ═════════════════════════════════════════════════════════════
#  PAGE HEADER
# ═════════════════════════════════════════════════════════════
eng_crit_cnt    = sum(1 for t in eng       if eng_status(t)      == "CRITICAL")
eng_warn_cnt    = sum(1 for t in eng       if eng_status(t)      == "WARNING")
fuel_crit_cnt   = sum(1 for f in fuel      if fuel_status(f)     == "CRITICAL")
fuel_warn_cnt   = sum(1 for f in fuel      if fuel_status(f)     == "WARNING")
roll_instab_cnt = sum(1 for r in roll      if roll_status(r)     == "INSTABILITY")
roll_alert_cnt  = sum(1 for r in roll      if roll_status(r)     == "ALERT")
alt_emerg_cnt   = sum(1 for d in alt_drops if alt_drop_status(d) == "EMERGENCY")
alt_warn_cnt    = sum(1 for d in alt_drops if alt_drop_status(d) == "WARNING")

overall_status = (
    "🔴 CRITICAL / EMERGENCY"
    if eng_crit_cnt or fuel_crit_cnt or roll_instab_cnt or alt_emerg_cnt else
    "🟡 WARNING / ALERT"
    if eng_warn_cnt or fuel_warn_cnt or roll_alert_cnt or alt_warn_cnt else
    "🟢 NOMINAL"
)

st.markdown("# ✈ Aircraft Flight Data Monitor")
st.markdown(
    f"**FLT-BU01** &nbsp;|&nbsp; 30-min simulation &nbsp;|&nbsp; "
    f"1 sample/min &nbsp;|&nbsp; System: **{overall_status}**"
)

# KPI row — 12 cols, 3 per condition
k1,k2,k3, k4,k5,k6, k7,k8,k9, k10,k11,k12 = st.columns(12)
k1.metric("Peak Eng Temp",    f"{eng.max()}°C",
          delta=f"+{eng.max()-eng_warn}°C WARN" if eng.max()>=eng_warn else "Normal",
          delta_color="inverse")
k2.metric("Avg Eng Temp",     f"{eng.mean():.0f}°C")
k3.metric("Eng Alerts",       eng_warn_cnt+eng_crit_cnt,
          delta=f"{eng_crit_cnt} critical", delta_color="inverse")
k4.metric("Final Fuel",       f"{fuel[-1]}%",
          delta=f"-{fuel[0]-fuel[-1]:.0f}% used", delta_color="inverse")
k5.metric("Fuel Flow",        f"{(fuel[0]-fuel[-1])/DURATION:.2f}%/m")
k6.metric("Fuel Alerts",      fuel_warn_cnt+fuel_crit_cnt,
          delta=f"{fuel_crit_cnt} critical", delta_color="inverse")
k7.metric("Max Roll",         f"{max(abs(roll)):.1f}°",
          delta="INSTABILITY" if max(abs(roll))>roll_instab else "ALERT" if max(abs(roll))>roll_alert else "Normal",
          delta_color="inverse")
k8.metric("Roll Alerts",      roll_alert_cnt)
k9.metric("Roll Instability", roll_instab_cnt, delta_color="inverse")
k10.metric("Max Drop",        f"{alt_drops.max()} ft/m",
           delta="EMERGENCY" if alt_drops.max()>=alt_emerg else "WARNING" if alt_drops.max()>=alt_warn else "Normal",
           delta_color="inverse")
k11.metric("Alt Warnings",    alt_warn_cnt)
k12.metric("Alt Emergencies", alt_emerg_cnt,
           delta="🚨 Act now!" if alt_emerg_cnt>0 else "✅ Clear",
           delta_color="inverse")

st.divider()


# ═════════════════════════════════════════════════════════════
#  SECTION 1 — ENGINE TEMPERATURE
# ═════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-banner" style="border-color:#ff6b35;background:#ff6b3510;color:#ff6b35">'
    '🌡 SECTION 1 &nbsp;—&nbsp; CONDITION 1: ENGINE TEMPERATURE MONITOR'
    '</div>', unsafe_allow_html=True
)

st.markdown("#### 📈 Engine Temperature — Line Graph")
st.plotly_chart(
    make_line_chart(
        y_data=eng, y_label="Engine Temp (°C)", y_range=[400, 1050],
        line_color="#ff6b35", fill_color="rgba(255,107,53,0.08)",
        warn_val=eng_warn, crit_val=eng_crit, warn_is_upper=True,
    ),
    use_container_width=True,
)

st.markdown("#### 📋 Engine Temperature — Data Table (All 30 Samples)")
eng_df = df[["Time", "Phase", "Eng Temp (°C)", "Eng Status"]].copy()

def color_eng(val):
    if isinstance(val, (int, float)):
        if val >= eng_crit: return "color:#ff2244;font-weight:bold"
        if val >= eng_warn: return "color:#ffaa00;font-weight:bold"
        return "color:#ff6b35"
    return ""

st.dataframe(
    eng_df.style
        .applymap(lambda v: SEV_BG.get(v,""), subset=["Eng Status"])
        .applymap(color_eng, subset=["Eng Temp (°C)"])
        .hide(axis="index"),
    use_container_width=True, height=400,
)

st.markdown(f"#### ⚠ Engine Temp — Cumulative Alert Log ({len(eng_alerts)} alert(s))")
if eng_alerts.empty:
    st.success("✅ Engine temperature nominal — no anomalies detected.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 CRITICAL", eng_crit_cnt)
    c2.metric("🟡 WARNING",  eng_warn_cnt)
    c3.metric("✅ SAFE",     DURATION - eng_crit_cnt - eng_warn_cnt)
    st.dataframe(
        eng_alerts.style
            .applymap(lambda v: SEV_BG.get(v,""), subset=["Eng Status"])
            .hide(axis="index"),
        use_container_width=True,
        height=min(80 + len(eng_alerts)*38, 420),
    )

st.divider()


# ═════════════════════════════════════════════════════════════
#  SECTION 2 — FUEL LEVEL
# ═════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-banner" style="border-color:#39ff14;background:#39ff1410;color:#39ff14">'
    '⛽ SECTION 2 &nbsp;—&nbsp; CONDITION 2: FUEL LEVEL MONITOR'
    '</div>', unsafe_allow_html=True
)

st.markdown("#### 📈 Fuel Level — Line Graph")
st.plotly_chart(
    make_line_chart(
        y_data=fuel, y_label="Fuel Level (%)", y_range=[0, 100],
        line_color="#39ff14", fill_color="rgba(57,255,20,0.08)",
        warn_val=fuel_warn, crit_val=fuel_crit, warn_is_upper=False,
        warn_color="#ffaa00", crit_color="#ff2244",
    ),
    use_container_width=True,
)

st.markdown("#### 📋 Fuel Level — Data Table (All 30 Samples)")
fuel_df = df[["Time", "Phase", "Fuel Level (%)", "Fuel Status"]].copy()

def color_fuel(val):
    if isinstance(val, (int, float)):
        if val <= fuel_crit: return "color:#ff2244;font-weight:bold"
        if val <= fuel_warn: return "color:#ffaa00;font-weight:bold"
        return "color:#39ff14"
    return ""

st.dataframe(
    fuel_df.style
        .applymap(lambda v: SEV_BG.get(v,""), subset=["Fuel Status"])
        .applymap(color_fuel, subset=["Fuel Level (%)"])
        .hide(axis="index"),
    use_container_width=True, height=400,
)

st.markdown(f"#### ⚠ Fuel Level — Cumulative Alert Log ({len(fuel_alerts)} alert(s))")
if fuel_alerts.empty:
    st.success("✅ Fuel level nominal — no anomalies detected.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 CRITICAL", fuel_crit_cnt)
    c2.metric("🟡 WARNING",  fuel_warn_cnt)
    c3.metric("✅ SAFE",     DURATION - fuel_crit_cnt - fuel_warn_cnt)
    st.dataframe(
        fuel_alerts.style
            .applymap(lambda v: SEV_BG.get(v,""), subset=["Fuel Status"])
            .hide(axis="index"),
        use_container_width=True,
        height=min(80 + len(fuel_alerts)*38, 420),
    )

st.divider()


# ═════════════════════════════════════════════════════════════
#  SECTION 3 — ROLL ANGLE
# ═════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-banner" style="border-color:#ff3fa4;background:#ff3fa410;color:#ff3fa4">'
    '🔄 SECTION 3 &nbsp;—&nbsp; CONDITION 3: ROLL ANGLE & INSTABILITY MONITOR'
    '</div>', unsafe_allow_html=True
)

st.info(
    f"**Detection Rules** &nbsp;|&nbsp; "
    f"Roll > ±**{roll_alert}°** → ⚠ ALERT (corrective action needed)  &nbsp;&nbsp; "
    f"Roll > ±**{roll_instab}°** → 🚨 INSTABILITY (aircraft control at risk)",
    icon="ℹ️"
)

st.markdown("#### 📈 Roll Angle — Line Graph (± Symmetric)")
st.plotly_chart(make_roll_chart(height=400), use_container_width=True)

st.markdown("#### 📋 Roll Angle — Data Table (All 30 Samples)")
roll_df = df[["Time", "Phase", "Roll Angle (°)", "Roll Status"]].copy()

def color_roll_val(val):
    if isinstance(val, (int, float)):
        abs_v = abs(val)
        if abs_v > roll_instab: return "color:#ff00ff;font-weight:bold"
        if abs_v > roll_alert:  return "color:#ffaa00;font-weight:bold"
        return "color:#ff3fa4"
    return ""

st.dataframe(
    roll_df.style
        .applymap(lambda v: SEV_BG.get(v,""), subset=["Roll Status"])
        .applymap(color_roll_val, subset=["Roll Angle (°)"])
        .hide(axis="index"),
    use_container_width=True, height=400,
)

st.markdown(f"#### ⚠ Roll Angle — Cumulative Alert Log ({len(roll_alerts)} alert(s))")
if roll_alerts.empty:
    st.success("✅ Roll angle nominal — no instability detected.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("🚨 INSTABILITY", roll_instab_cnt, help=f"Roll exceeded ±{roll_instab}°")
    c2.metric("⚠ ALERT",       roll_alert_cnt,  help=f"Roll exceeded ±{roll_alert}°")
    c3.metric("✅ SAFE",        DURATION - roll_instab_cnt - roll_alert_cnt)
    st.dataframe(
        roll_alerts.style
            .applymap(lambda v: SEV_BG.get(v,""), subset=["Roll Status"])
            .hide(axis="index"),
        use_container_width=True,
        height=min(80 + len(roll_alerts)*38, 420),
    )

st.divider()


# ═════════════════════════════════════════════════════════════
#  SECTION 4 — ALTITUDE DROP  ← NEW
# ═════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-banner" style="border-color:#00d4ff;background:#00d4ff10;color:#00d4ff">'
    '📉 SECTION 4 &nbsp;—&nbsp; CONDITION 4: ALTITUDE DROP EMERGENCY MONITOR'
    '</div>', unsafe_allow_html=True
)

st.info(
    f"**Detection Rules** &nbsp;|&nbsp; "
    f"Drop > **{alt_warn} ft/min** → ⚠ WARNING &nbsp;&nbsp; "
    f"Drop > **{alt_emerg} ft/min** → 🚨 EMERGENCY (rapid altitude loss)",
    icon="ℹ️"
)

# ── 4A: Altitude profile ──────────────────────────────────────
st.markdown("#### 📈 Altitude Profile — Line Graph")
st.plotly_chart(make_altitude_chart(height=400), use_container_width=True)

# ── 4B: Drop rate line chart ──────────────────────────────────
st.markdown("#### 📈 Altitude Drop Rate — Per Minute Line Graph")
st.plotly_chart(make_drop_rate_chart(height=300), use_container_width=True)

# ── 4C: Data table ────────────────────────────────────────────
st.markdown("#### 📋 Altitude — Data Table (All 30 Samples)")

def color_alt_val(val):
    if isinstance(val, (int, float)): return "color:#00d4ff"
    return ""

def color_drop_val(val):
    if isinstance(val, (int, float)):
        if val >= alt_emerg: return "color:#ff0033;font-weight:bold"
        if val >= alt_warn:  return "color:#ffaa00;font-weight:bold"
        return "color:#5577aa"
    return ""

alt_df = df[["Time", "Phase", "Altitude (ft)", "Drop (ft/min)", "Alt Status"]].copy()

st.dataframe(
    alt_df.style
        .applymap(lambda v: SEV_BG.get(v,""), subset=["Alt Status"])
        .applymap(color_alt_val,  subset=["Altitude (ft)"])
        .applymap(color_drop_val, subset=["Drop (ft/min)"])
        .hide(axis="index"),
    use_container_width=True, height=420,
)

# ── 4D: Cumulative alert log ──────────────────────────────────
st.markdown(f"#### ⚠ Altitude — Cumulative Alert Log ({len(alt_alerts)} alert(s))")
if alt_alerts.empty:
    st.success("✅ Altitude nominal — no emergency drops detected.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("🚨 EMERGENCY", alt_emerg_cnt,
              delta="Immediate action!" if alt_emerg_cnt > 0 else "", delta_color="inverse")
    c2.metric("⚠ WARNING",   alt_warn_cnt)
    c3.metric("✅ SAFE",      DURATION - alt_emerg_cnt - alt_warn_cnt)
    st.dataframe(
        alt_alerts.style
            .applymap(lambda v: SEV_BG.get(v,""), subset=["Alt Status"])
            .hide(axis="index"),
        use_container_width=True,
        height=min(80 + len(alt_alerts)*38, 460),
    )

st.divider()
st.caption("✈ Aircraft FDM System | Conditions 1, 2, 3 & 4 | Simulation Mode | FLT-BU01")