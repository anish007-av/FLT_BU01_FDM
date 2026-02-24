import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


#  PAGE CONFIG

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



#  SIDEBAR — THRESHOLD SLIDERS

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



#  STATUS HELPERS

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

#   DATAFRAMES

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



#  HELPER: line chart for engine temp & fuel 

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



#  HELPER: roll angle line chart (symmetric ± axis)

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



#  HELPER: altitude profile line chart  ← NEW

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



#  HELPER: drop rate line chart  

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
        type="category",                
        categoryorder="array",
        categoryarray=LABELS             
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



#  PAGE HEADER

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


#  SECTION 1 — ENGINE TEMPERATURE

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



#  SECTION 2 — FUEL LEVEL

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


#  SECTION 3 — ROLL ANGLE

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



#  SECTION 4 — ALTITUDE DROP  

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
st.caption("✈ Aircraft FDM System | Conditions 1, 2, 3 & 4 | analysis | FLT-BU01")




#FUEL INNOVATION -----------------------------------------------

st.markdown(
    '<div class="section-banner" style="border-color:#a78bfa;background:#a78bfa10;color:#a78bfa">'
    '🔮 SECTION 5 &nbsp;—&nbsp; INNOVATION: PREDICTIVE FUEL ESTIMATION ENGINE'
    '</div>', unsafe_allow_html=True
)

st.info(
    "**AI Prediction** &nbsp;|&nbsp; Uses current burn rate trend to forecast fuel level "
    "for remaining flight &nbsp;|&nbsp; Flags if projected fuel drops below safe threshold before landing",
    icon="🤖"
)

# Inline controls for prediction
pred_col1, pred_col2, pred_col3 = st.columns(3)
with pred_col1:
    lookback = st.slider("📊 Burn rate lookback window (samples)", 2, 10, 5,
                         help="How many past samples to use for burn rate estimate")
with pred_col2:
    fuel_reserve = st.slider("🛬 Min. reserve fuel at landing (%)", 5, 25, 10,
                              help="Minimum fuel % required at T+29m for safe landing")
with pred_col3:
    pred_confidence = st.select_slider("📐 Prediction band width",
                                        options=["Tight (±0.5%)", "Normal (±1%)", "Wide (±2%)"],
                                        value="Normal (±1%)")

band_map = {"Tight (±0.5%)": 0.5, "Normal (±1%)": 1.0, "Wide (±2%)": 2.0}
band_width = band_map[pred_confidence]

# ── Calculate burn rate from last `lookback` known samples ───
# Use full 30-pt fuel array (as if analysing post-flight or at T+29)
# In a real sim you'd only use fuel[:current_step]
burn_rates = np.array([fuel[i-1] - fuel[i] for i in range(1, DURATION)])  # per-minute burn
recent_burn = burn_rates[-lookback:]                    # last N samples
avg_burn    = float(np.mean(recent_burn))               # average burn rate
std_burn    = float(np.std(recent_burn))                # variability

# ── Project forward from last known point ────────────────────
# We "predict" from T+20m onward (mid-cruise) to show the feature meaningfully
PREDICT_FROM = 20          # minute index we start predicting from
remaining    = DURATION - PREDICT_FROM   # 10 future minutes

pred_times  = list(range(PREDICT_FROM, DURATION))
pred_labels = [f"T+{t:02d}m" for t in pred_times]

# Central prediction
pred_fuel_central = [fuel[PREDICT_FROM]]
for _ in range(1, remaining):
    pred_fuel_central.append(max(0, pred_fuel_central[-1] - avg_burn))

# Optimistic band (lower burn rate)
pred_fuel_upper = [fuel[PREDICT_FROM]]
for _ in range(1, remaining):
    pred_fuel_upper.append(max(0, pred_fuel_upper[-1] - max(0, avg_burn - band_width)))

# Pessimistic band (higher burn rate)
pred_fuel_lower = [fuel[PREDICT_FROM]]
for _ in range(1, remaining):
    pred_fuel_lower.append(max(0, pred_fuel_lower[-1] - (avg_burn + band_width)))

# ── Estimated Time to WARNING / CRITICAL ─────────────────────
def estimate_tte(start_fuel, burn, threshold, is_lower):
    """Minutes from PREDICT_FROM until fuel crosses threshold."""
    f = start_fuel
    for minute in range(remaining):
        if is_lower and f <= threshold:
            return PREDICT_FROM + minute
        f = max(0, f - burn)
    return None  # won't cross in remaining flight

tte_warn  = estimate_tte(fuel[PREDICT_FROM], avg_burn, fuel_warn,  True)
tte_crit  = estimate_tte(fuel[PREDICT_FROM], avg_burn, fuel_crit,  True)
tte_resrv = estimate_tte(fuel[PREDICT_FROM], avg_burn, fuel_reserve, True)

landing_fuel_central  = pred_fuel_central[-1]
landing_fuel_optimist = pred_fuel_upper[-1]
landing_fuel_pessimst = pred_fuel_lower[-1]

# Overall prediction verdict
if landing_fuel_pessimst < fuel_crit:
    verdict = "🔴 CRITICAL RISK — Even optimistic scenario may not meet reserve"
    verdict_clr = "#ff2244"
elif landing_fuel_central < fuel_warn:
    verdict = "🟡 WARNING — Central forecast below safe landing reserve"
    verdict_clr = "#ffaa00"
elif landing_fuel_pessimst < fuel_reserve:
    verdict = "🟠 CAUTION — Pessimistic scenario misses reserve target"
    verdict_clr = "#ff8c00"
else:
    verdict = "🟢 NOMINAL — Fuel sufficient for safe landing with reserve"
    verdict_clr = "#39ff14"


#  KPI ROW — PREDICTION SUMMARY

pk1, pk2, pk3, pk4, pk5, pk6 = st.columns(6)
pk1.metric("Avg Burn Rate",    f"{avg_burn:.2f}%/min",
           delta=f"±{std_burn:.2f} variability", delta_color="off")
pk2.metric("Predicted Landing Fuel", f"{landing_fuel_central:.1f}%",
           delta="CRITICAL" if landing_fuel_central < fuel_crit
           else "LOW" if landing_fuel_central < fuel_warn else "Safe",
           delta_color="inverse" if landing_fuel_central < fuel_warn else "off")
pk3.metric("Optimistic Landing",  f"{landing_fuel_optimist:.1f}%")
pk4.metric("Pessimistic Landing", f"{landing_fuel_pessimst:.1f}%",
           delta="⚠ Below reserve!" if landing_fuel_pessimst < fuel_reserve else "✅ Above reserve",
           delta_color="inverse" if landing_fuel_pessimst < fuel_reserve else "off")
pk5.metric("ETA to WARNING",
           f"T+{tte_warn:02d}m" if tte_warn else "Not reached",
           delta="Already breached" if fuel[PREDICT_FROM] <= fuel_warn else "",
           delta_color="inverse")
pk6.metric("ETA to CRITICAL",
           f"T+{tte_crit:02d}m" if tte_crit else "Not reached",
           delta="Already breached" if fuel[PREDICT_FROM] <= fuel_crit else "",
           delta_color="inverse")

# Verdict banner
st.markdown(
    f'<div style="background:#0a0010;border:2px solid {verdict_clr};border-radius:8px;'
    f'padding:12px 20px;margin:12px 0;font-family:monospace;font-size:14px;'
    f'color:{verdict_clr};font-weight:bold;letter-spacing:1px">'
    f'🤖 PREDICTION VERDICT &nbsp;|&nbsp; {verdict}'
    f'</div>', unsafe_allow_html=True)

#  PREDICTION CHART

st.markdown("#### 📈 Fuel Level — Actual vs Predicted Forecast")

fig_pred = go.Figure()

# ── Phase bands ───────────────────────────────────────────────
phase_changes = [0]
for i in range(1, DURATION):
    if PHASES[i] != PHASES[i-1]: phase_changes.append(i)
phase_changes.append(DURATION)
PHASE_CLR_LOCAL = {
    "Takeoff":  "rgba(255,215,0,0.10)", "Climb":   "rgba(0,191,255,0.08)",
    "Cruise":   "rgba(57,255,20,0.08)", "Descent": "rgba(255,140,0,0.08)",
    "Approach": "rgba(255,107,53,0.08)",
}
for j in range(len(phase_changes)-1):
    s, e = phase_changes[j], phase_changes[j+1]
    fig_pred.add_vrect(x0=LABELS[s], x1=LABELS[e-1],
                       fillcolor=PHASE_CLR_LOCAL[PHASES[s]], layer="below", line_width=0)

# ── Threshold lines ───────────────────────────────────────────
fig_pred.add_hline(y=fuel_warn, line_dash="dash", line_color="#ffaa00", line_width=1.5,
    annotation_text=f"⚠ WARN ≤{fuel_warn}%", annotation_font_color="#ffaa00",
    annotation_position="top left")
fig_pred.add_hline(y=fuel_crit, line_dash="dash", line_color="#ff2244", line_width=1.5,
    annotation_text=f"🔴 CRIT ≤{fuel_crit}%", annotation_font_color="#ff2244",
    annotation_position="top left")
fig_pred.add_hline(y=fuel_reserve, line_dash="dot", line_color="#a78bfa", line_width=1.5,
    annotation_text=f"🛬 Reserve {fuel_reserve}%", annotation_font_color="#a78bfa",
    annotation_position="bottom left")

# ── Prediction split divider ──────────────────────────────────
fig_pred.add_vline(x=PREDICT_FROM, line_dash="dot", line_color="#a78bfa",
                   line_width=2,
                   annotation_text="◀ Actual  |  Predicted ▶",
                   annotation_font_color="#a78bfa",
                   annotation_position="top right")

# ── Actual fuel line ──────────────────────────────────────────
fig_pred.add_trace(go.Scatter(
    x=LABELS[:PREDICT_FROM+1], y=list(fuel[:PREDICT_FROM+1]),
    mode="lines+markers",
    line=dict(color="#39ff14", width=3),
    marker=dict(color="#39ff14", size=6, line=dict(color="#000d1a", width=1)),
    name="Actual Fuel",
    hovertemplate="<b>%{x}</b><br>Actual: %{y:.1f}%<extra></extra>",
))

# ── Prediction confidence band (shaded) ───────────────────────
fig_pred.add_trace(go.Scatter(
    x=pred_labels + pred_labels[::-1],
    y=pred_fuel_upper + pred_fuel_lower[::-1],
    fill="toself",
    fillcolor="rgba(167,139,250,0.15)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=True,
    name=f"Confidence Band ({pred_confidence})",
    hoverinfo="skip",
))

# ── Pessimistic line ──────────────────────────────────────────
fig_pred.add_trace(go.Scatter(
    x=pred_labels, y=pred_fuel_lower,
    mode="lines",
    line=dict(color="#ff8c00", width=1.5, dash="dot"),
    name="Pessimistic",
    hovertemplate="<b>%{x}</b><br>Pessimistic: %{y:.1f}%<extra></extra>",
))

# ── Optimistic line ───────────────────────────────────────────
fig_pred.add_trace(go.Scatter(
    x=pred_labels, y=pred_fuel_upper,
    mode="lines",
    line=dict(color="#00d4ff", width=1.5, dash="dot"),
    name="Optimistic",
    hovertemplate="<b>%{x}</b><br>Optimistic: %{y:.1f}%<extra></extra>",
))

# ── Central prediction line ───────────────────────────────────
fig_pred.add_trace(go.Scatter(
    x=pred_labels, y=pred_fuel_central,
    mode="lines+markers",
    line=dict(color="#a78bfa", width=3, dash="dash"),
    marker=dict(color="#a78bfa", size=7,
                symbol=["circle"] * (len(pred_labels)-1) + ["diamond"],
                line=dict(color="#fff", width=1)),
    name="Predicted (Central)",
    hovertemplate="<b>%{x}</b><br>Predicted: %{y:.1f}%<extra></extra>",
))

# ── Landing target marker ─────────────────────────────────────
fig_pred.add_trace(go.Scatter(
    x=[LABELS[-1]], y=[landing_fuel_central],
    mode="markers+text",
    marker=dict(color="#a78bfa", size=16, symbol="star",
                line=dict(color="#fff", width=2)),
    text=[f"🛬 {landing_fuel_central:.1f}%"],
    textposition="top right",
    textfont=dict(color="#a78bfa", size=11, family="monospace"),
    showlegend=False,
    hovertemplate=f"<b>Predicted Landing</b><br>Fuel: {landing_fuel_central:.1f}%<extra></extra>",
))

# ── ETA markers (if warning/critical crossed) ─────────────────
for tte, label, clr in [(tte_warn, f"WARN@T+{tte_warn:02d}m", "#ffaa00"),
                         (tte_crit, f"CRIT@T+{tte_crit:02d}m", "#ff2244")]:
    if tte:
        fig_pred.add_vline(x=tte, line_color=clr, line_width=1, line_dash="dash",
                           annotation_text=label, annotation_font_color=clr,
                           annotation_position="bottom right")

fig_pred.update_layout(
    plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
    font=dict(family="monospace", color="#c8d8e8"),
    xaxis=dict(title="Flight Time", gridcolor="#0d2035",
               tickfont=dict(size=10), tickangle=-30,
               tickmode="array", tickvals=LABELS, ticktext=LABELS),
    yaxis=dict(title="Fuel Level (%)", gridcolor="#0d2035", range=[0, 105]),
    height=420, showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.01,
                xanchor="left", x=0, font=dict(size=10),
                bgcolor="rgba(5,15,30,0.8)", bordercolor="#1a3045"),
    margin=dict(l=60, r=40, t=40, b=50),
    hovermode="x unified",
)
st.plotly_chart(fig_pred, use_container_width=True)

#  BURN RATE TREND CHART

st.markdown("#### 📊 Burn Rate Trend — Per Minute Consumption")

fig_burn = go.Figure()

burn_labels = LABELS[1:]  # T+01m to T+29m
burn_colors = ["#a78bfa" if i >= DURATION-1-lookback
               else "rgba(57,255,20,0.4)" for i in range(len(burn_rates))]

# Bar chart of burn rate
fig_burn.add_trace(go.Bar(
    x=burn_labels, y=burn_rates,
    marker_color=burn_colors,
    marker_line_color="#000d1a", marker_line_width=0.8,
    name="Burn Rate (%/min)",
    hovertemplate="<b>%{x}</b><br>Burn: %{y:.2f}%/min<extra></extra>",
))

# Average line
fig_burn.add_hline(y=avg_burn, line_dash="dash", line_color="#a78bfa", line_width=2,
    annotation_text=f"📊 Avg {avg_burn:.2f}%/min (last {lookback} pts)",
    annotation_font_color="#a78bfa", annotation_position="top right")

# Lookback window shade
fig_burn.add_vrect(
    x0=LABELS[max(1, DURATION-lookback)], x1=LABELS[-1],
    fillcolor="rgba(167,139,250,0.08)", line_color="#a78bfa",
    line_width=1, line_dash="dot",
    annotation_text=f"Lookback window ({lookback} pts)",
    annotation_font_color="#a78bfa", annotation_position="top left",
)

# Phase bands
for j in range(len(phase_changes)-1):
    s, e = phase_changes[j], phase_changes[j+1]
    if s > 0:
        fig_burn.add_vrect(x0=LABELS[s], x1=LABELS[min(e, DURATION)-1],
                           fillcolor=PHASE_CLR_LOCAL[PHASES[s]], layer="below", line_width=0)

fig_burn.update_layout(
    plot_bgcolor="#050f1e", paper_bgcolor="#000d1a",
    font=dict(family="monospace", color="#c8d8e8"),
    xaxis=dict(title="Flight Time", gridcolor="#0d2035",
               tickfont=dict(size=10), tickangle=-30,
               type="category", categoryorder="array", categoryarray=burn_labels),
    yaxis=dict(title="Burn Rate (%/min)", gridcolor="#0d2035", range=[0, max(burn_rates)+1]),
    height=280, showlegend=False,
    margin=dict(l=60, r=40, t=20, b=50),
    hovermode="x unified",
)
st.plotly_chart(fig_burn, use_container_width=True)

#  PREDICTION SUMMARY TABLE
st.markdown("#### 📋 Predicted Fuel State — Minute by Minute")

pred_df = pd.DataFrame({
    "Time":              pred_labels,
    "Phase":             [PHASES[t] for t in pred_times],
    "Central (%)":       [round(v, 1) for v in pred_fuel_central],
    "Optimistic (%)":    [round(v, 1) for v in pred_fuel_upper],
    "Pessimistic (%)":   [round(v, 1) for v in pred_fuel_lower],
    "Central Status":    [
        "CRITICAL" if v <= fuel_crit else "WARNING" if v <= fuel_warn
        else "RESERVE!" if v <= fuel_reserve else "SAFE"
        for v in pred_fuel_central
    ],
})

SEV_BG_PRED = {
    "CRITICAL":  "background-color:#2a1000;color:#ff2244;font-weight:bold",
    "WARNING":   "background-color:#1e1600;color:#ffaa00;font-weight:bold",
    "RESERVE!":  "background-color:#1a0030;color:#a78bfa;font-weight:bold",
    "SAFE":      "background-color:#001a0a;color:#39ff14",
}

def color_pred_val(val):
    if isinstance(val, (int, float)):
        if val <= fuel_crit:    return "color:#ff2244;font-weight:bold"
        if val <= fuel_warn:    return "color:#ffaa00;font-weight:bold"
        if val <= fuel_reserve: return "color:#a78bfa;font-weight:bold"
        return "color:#39ff14"
    return ""

st.dataframe(
    pred_df.style
        .applymap(lambda v: SEV_BG_PRED.get(v, ""), subset=["Central Status"])
        .applymap(color_pred_val, subset=["Central (%)", "Optimistic (%)", "Pessimistic (%)"])
        .hide(axis="index"),
    use_container_width=True,
    height=min(80 + len(pred_df)*38, 460),
)

#  RECOMMENDATION BOX

st.markdown("#### 🤖 AI Recommendation")

rec_lines = []
if landing_fuel_pessimst < fuel_crit:
    rec_lines.append("🔴 **Divert immediately** — pessimistic projection hits CRITICAL before landing.")
if landing_fuel_central < fuel_warn:
    rec_lines.append(f"🟡 **Recommend diversion** — central forecast ({landing_fuel_central:.1f}%) below WARNING threshold.")
if tte_warn and tte_warn < DURATION - 3:
    rec_lines.append(f"⚠ **Fuel WARNING expected at {LABELS[tte_warn]}** — initiate fuel management procedures.")
if tte_crit:
    rec_lines.append(f"🚨 **CRITICAL fuel at {LABELS[tte_crit]}** — declare minimum fuel, expedite landing.")
if landing_fuel_central < fuel_reserve:
    rec_lines.append(f"🛬 **Landing reserve at risk** — projected {landing_fuel_central:.1f}% below {fuel_reserve}% minimum reserve.")
if avg_burn > 3.5:
    rec_lines.append(f"📊 **High burn rate detected** — {avg_burn:.2f}%/min is above typical cruise consumption.")
if not rec_lines:
    rec_lines.append(f"✅ **Fuel management nominal** — projected landing fuel {landing_fuel_central:.1f}% is above all thresholds.")
    rec_lines.append(f"📊 **Burn rate stable** at {avg_burn:.2f}%/min. No intervention required.")

for line in rec_lines:
    clr = "#ff2244" if "🔴" in line else "#ffaa00" if ("🟡" in line or "⚠" in line) else \
          "#ff0033" if "🚨" in line else "#a78bfa" if "🛬" in line else "#39ff14"
    st.markdown(
        f'<div style="background:#050f1e;border-left:4px solid {clr};border-radius:4px;'
        f'padding:10px 16px;margin:5px 0;font-family:monospace;font-size:13px;color:{clr}">'
        f'{line}</div>', unsafe_allow_html=True)

st.divider()
st.caption("✈ Aircraft FDM System | Conditions 1–4 + Predictive Fuel Estimation | FLT-BU01")
