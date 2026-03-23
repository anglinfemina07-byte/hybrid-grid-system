import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Grid Stability Analyzer",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    body { background-color: #0d1117; }
    .main { background-color: #0d1117; }
    .block-container { padding: 2rem 3rem; }
    h1 { color: #00e5ff; font-family: 'Courier New'; text-align: center; font-size: 2.2rem; }
    h2, h3 { color: #00e5ff; font-family: 'Courier New'; }
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #0d1117);
        border: 1px solid #00e5ff33;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        margin: 0.5rem;
    }
    .score-value { color: #00e5ff; font-size: 2rem; font-weight: bold; }
    .score-label { color: #aaa; font-size: 0.85rem; }
    .winner-badge {
        background: linear-gradient(90deg, #00e5ff, #00ff88);
        color: #000;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .stSlider label { color: #00e5ff !important; }
    .control-box {
        background: #1a1f2e;
        border: 1px solid #00e5ff22;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────
HOURS = np.linspace(0, 24, 288)
np.random.seed(42)
BASE_NOISE = np.random.normal(0, 1, 288)

colors = {'solar': '#FFD700', 'wind': '#00BFFF', 'hybrid': '#00FF88'}
fill_colors = {
    'solar': 'rgba(255,215,0,0.15)',
    'wind': 'rgba(0,191,255,0.15)',
    'hybrid': 'rgba(0,255,136,0.15)'
}

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("<h1>⚡ Solar-Wind Hybrid Grid Stability Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa;'>Real-Time Interactive Simulation — Adjust inputs and see live results</p>", unsafe_allow_html=True)
st.markdown("---")

# ── SIDEBAR CONTROLS ───────────────────────────────────────────────────────
st.sidebar.markdown("## 🎮 Control Panel")
st.sidebar.markdown("### ☀️ Solar Settings")
solar_intensity = st.sidebar.slider("Solar Intensity (%)", 0, 100, 100, step=5,
    help="0% = Full night / heavy clouds, 100% = Clear sunny day")
cloud_disturbance = st.sidebar.slider("Cloud Disturbance (%)", 0, 50, 5, step=5,
    help="Simulates sudden cloud cover causing power dips")

st.sidebar.markdown("### 💨 Wind Settings")
wind_speed = st.sidebar.slider("Wind Speed (%)", 0, 100, 100, step=5,
    help="0% = Complete calm / no wind, 100% = Full wind")
wind_turbulence = st.sidebar.slider("Wind Turbulence (%)", 0, 50, 15, step=5,
    help="Higher = more random fluctuations in wind power")

st.sidebar.markdown("### 📈 Grid Settings")
demand_spike = st.sidebar.slider("Demand Level (%)", 50, 150, 100, step=10,
    help="100% = Normal demand, 150% = Peak load / industrial surge")

st.sidebar.markdown("### ⚡ Fault Simulation")
inject_fault = st.sidebar.checkbox("Inject Grid Fault", value=False,
    help="Simulates a sudden short circuit in the grid")
if inject_fault:
    fault_hour = st.sidebar.slider("Fault at Hour", 1, 23, 12)
    fault_severity = st.sidebar.slider("Fault Severity (%)", 10, 90, 70,
        help="How much power drops during fault")

st.sidebar.markdown("### 🌍 Quick Scenarios")
scenario = st.sidebar.selectbox("Load Preset Scenario", [
    "Custom (Use Sliders)",
    "☀️ Perfect Sunny Day",
    "🌧️ Cloudy Day (Low Solar)",
    "🌬️ Strong Wind Only",
    "😶 No Wind at All",
    "🌑 Night Time",
    "⚡ Storm + Fault",
    "🏭 Peak Industrial Demand",
    "🌪️ Worst Case Scenario"
])

# ── APPLY SCENARIOS ────────────────────────────────────────────────────────
si = solar_intensity / 100
wi = wind_speed / 100
cd = cloud_disturbance / 100
wt = wind_turbulence / 100
dm = demand_spike / 100

if scenario == "☀️ Perfect Sunny Day":
    si, wi, cd, wt, dm = 1.0, 0.5, 0.02, 0.05, 1.0
    inject_fault = False
elif scenario == "🌧️ Cloudy Day (Low Solar)":
    si, wi, cd, wt, dm = 0.2, 0.8, 0.4, 0.2, 1.0
    inject_fault = False
elif scenario == "🌬️ Strong Wind Only":
    si, wi, cd, wt, dm = 0.0, 1.0, 0.0, 0.1, 1.0
    inject_fault = False
elif scenario == "😶 No Wind at All":
    si, wi, cd, wt, dm = 1.0, 0.0, 0.1, 0.0, 1.0
    inject_fault = False
elif scenario == "🌑 Night Time":
    si, wi, cd, wt, dm = 0.0, 0.6, 0.0, 0.2, 0.8
    inject_fault = False
elif scenario == "⚡ Storm + Fault":
    si, wi, cd, wt, dm = 0.3, 0.4, 0.4, 0.45, 1.2
    inject_fault = True
    fault_hour = 12
    fault_severity = 80
elif scenario == "🏭 Peak Industrial Demand":
    si, wi, cd, wt, dm = 1.0, 1.0, 0.05, 0.1, 1.5
    inject_fault = False
elif scenario == "🌪️ Worst Case Scenario":
    si, wi, cd, wt, dm = 0.1, 0.1, 0.45, 0.45, 1.5
    inject_fault = True
    fault_hour = 12
    fault_severity = 90

# ── GENERATE POWER DATA ────────────────────────────────────────────────────
def generate_solar(hours, intensity, cloud_dist):
    solar = np.zeros_like(hours)
    for i, h in enumerate(hours):
        if 6 <= h <= 18:
            base = np.sin(np.pi * (h - 6) / 12) * 100 * intensity
            noise = BASE_NOISE[i] * cloud_dist * 20
            solar[i] = max(0, base + noise)
    return solar

def generate_wind(hours, speed, turbulence):
    wind_base = (40 + 20 * np.sin(2 * np.pi * hours / 24)) * speed
    noise = BASE_NOISE * turbulence * 30
    return np.clip(wind_base + noise, 0, 100)

def generate_hybrid(solar, wind):
    return (solar + wind) / 2

def get_demand(hours, level):
    demand = (60 + 20 * np.sin(np.pi * (hours - 6) / 12)) * level
    return np.clip(demand, 20, 150)

solar_power = generate_solar(HOURS, si, cd)
wind_power  = generate_wind(HOURS, wi, wt)
hybrid_power = generate_hybrid(solar_power, wind_power)
demand = get_demand(HOURS, dm)

# ── APPLY FAULT ────────────────────────────────────────────────────────────
def apply_fault(power, fault_hr, severity):
    p = power.copy()
    idx = np.argmin(np.abs(HOURS - fault_hr))
    drop = severity / 100
    p[idx:idx+6] *= (1 - drop)
    recovery = np.linspace(1 - drop, 1.0, 24)
    end = idx + 6
    p[end:end+24] = power[end:end+24] * recovery
    return p

if inject_fault:
    solar_fault  = apply_fault(solar_power,  fault_hour, fault_severity)
    wind_fault   = apply_fault(wind_power,   fault_hour, fault_severity * 1.2)
    hybrid_fault = apply_fault(hybrid_power, fault_hour, fault_severity * 0.6)
else:
    solar_fault  = solar_power.copy()
    wind_fault   = wind_power.copy()
    hybrid_fault = hybrid_power.copy()

# ── COMPUTE SCORES ─────────────────────────────────────────────────────────
def compute_scores(power, demand):
    freq = np.clip(50 + (power - demand) / (demand + 1e-6) * 0.5, 48, 52)
    volt = np.clip(0.95 + (power / (demand + 1e-6) - 1) * 0.1, 0.88, 1.12)
    var  = np.std(np.diff(power))
    freq_score = max(0, 100 - np.mean(np.abs(freq - 50)) * 20)
    volt_score = max(0, 100 - np.mean(np.abs(volt - 1.0)) * 100)
    var_score  = max(0, 100 - var * 2)
    return {
        'frequency': freq, 'voltage': volt,
        'freq_score': round(freq_score, 1),
        'volt_score': round(volt_score, 1),
        'var_score':  round(var_score, 1),
        'variability': round(var, 2)
    }

def compute_fault_score(fault_power, orig_power):
    idx = np.argmin(np.abs(HOURS - (fault_hour if inject_fault else 12)))
    segment = fault_power[idx:idx+30]
    orig    = orig_power[idx:idx+30]
    recovery = np.mean(segment / (orig + 1e-6)) * 100
    return round(min(100, recovery), 1)

scores = {
    'solar':  compute_scores(solar_fault,  demand),
    'wind':   compute_scores(wind_fault,   demand),
    'hybrid': compute_scores(hybrid_fault, demand)
}

for s in ['solar', 'wind', 'hybrid']:
    fault_p = {'solar': solar_fault, 'wind': wind_fault, 'hybrid': hybrid_fault}[s]
    orig_p  = {'solar': solar_power, 'wind': wind_power, 'hybrid': hybrid_power}[s]
    scores[s]['fault_score'] = compute_fault_score(fault_p, orig_p)
    scores[s]['overall'] = round(
        (scores[s]['freq_score'] + scores[s]['volt_score'] +
         scores[s]['var_score']  + scores[s]['fault_score']) / 4, 1
    )

best = max(scores, key=lambda x: scores[x]['overall'])

# ── LIVE STATUS BANNER ─────────────────────────────────────────────────────
status_parts = []
if si == 0: status_parts.append("🌑 No Solar")
elif si < 0.4: status_parts.append("🌥️ Low Solar")
else: status_parts.append("☀️ Solar Active")

if wi == 0: status_parts.append("😶 No Wind")
elif wi < 0.4: status_parts.append("🍃 Low Wind")
else: status_parts.append("💨 Wind Active")

if inject_fault: status_parts.append(f"⚠️ FAULT at Hour {fault_hour}")
if dm > 1.2: status_parts.append("🏭 High Demand")

st.info(f"**Live Scenario:** {' | '.join(status_parts)}")

# ── SCORECARD ──────────────────────────────────────────────────────────────
st.markdown("## 🏆 Real-Time Stability Scorecard")
col1, col2, col3 = st.columns(3)
icons = {'solar': '☀️', 'wind': '💨', 'hybrid': '⚡'}

for col, source in zip([col1, col2, col3], ['solar', 'wind', 'hybrid']):
    with col:
        r = scores[source]
        badge = "<span class='winner-badge'>🏆 WINNER</span>" if source == best else ""
        color = colors[source]
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size:2.5rem'>{icons[source]}</div>
            <div style='color:{color};font-size:1.2rem;font-weight:bold;text-transform:uppercase'>{source} {badge}</div>
            <div class='score-value'>{r['overall']}<span style='font-size:1rem'>%</span></div>
            <div class='score-label'>Overall Stability Score</div>
            <hr style='border-color:#ffffff22'>
            <div style='color:#ccc;font-size:0.8rem'>
                🔁 Frequency: {r['freq_score']}%<br>
                🔋 Voltage: {r['volt_score']}%<br>
                📉 Variability: {r['var_score']}%<br>
                ⚡ Fault Ride-Through: {r['fault_score']}%
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── POWER OUTPUT ───────────────────────────────────────────────────────────
st.markdown("## 📊 Live Power Output")
fig1 = go.Figure()

power_map = {
    'Solar':  (solar_fault,  '#FFD700', 'solid'),
    'Wind':   (wind_fault,   '#00BFFF', 'dot'),
    'Hybrid': (hybrid_fault, '#00FF88', 'solid'),
    'Demand': (demand,       '#FF6B6B', 'dash'),
}
for name, (data, clr, dash) in power_map.items():
    fig1.add_trace(go.Scatter(
        x=HOURS, y=data, name=name,
        line=dict(color=clr, width=2.5, dash=dash),
        fill='tozeroy' if name == 'Hybrid' else None,
        fillcolor='rgba(0,255,136,0.04)' if name == 'Hybrid' else None
    ))

if inject_fault:
    fig1.add_vline(x=fault_hour, line_dash='dash', line_color='red',
                   annotation_text='⚠️ Fault', annotation_font_color='red')

fig1.update_layout(
    plot_bgcolor='#0d1117', paper_bgcolor='#0d1117',
    font=dict(color='#ccc'), xaxis_title='Hour of Day',
    yaxis_title='Power (MW)', legend=dict(bgcolor='#1a1f2e'),
    xaxis=dict(gridcolor='#1a1f2e'), yaxis=dict(gridcolor='#1a1f2e'),
    height=400
)
st.plotly_chart(fig1, use_container_width=True)

# ── FREQUENCY & VOLTAGE ────────────────────────────────────────────────────
st.markdown("## 📡 Frequency & Voltage Stability")
col_f, col_v = st.columns(2)

with col_f:
    fig2 = go.Figure()
    fig2.add_hline(y=50, line_dash='dash', line_color='#FF6B6B', annotation_text='Nominal 50Hz')
    fig2.add_hrect(y0=49.5, y1=50.5, fillcolor='rgba(0,255,136,0.05)', line_width=0)
    for s in ['solar', 'wind', 'hybrid']:
        fig2.add_trace(go.Scatter(
            x=HOURS, y=scores[s]['frequency'],
            name=s.capitalize(), line=dict(color=colors[s], width=2)
        ))
    if inject_fault:
        fig2.add_vline(x=fault_hour, line_dash='dash', line_color='red')
    fig2.update_layout(
        title='Grid Frequency (Hz)', plot_bgcolor='#0d1117',
        paper_bgcolor='#0d1117', font=dict(color='#ccc'),
        xaxis=dict(gridcolor='#1a1f2e'), yaxis=dict(gridcolor='#1a1f2e'), height=350
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_v:
    fig3 = go.Figure()
    fig3.add_hline(y=1.0, line_dash='dash', line_color='#FF6B6B', annotation_text='Nominal 1.0 pu')
    fig3.add_hrect(y0=0.95, y1=1.05, fillcolor='rgba(0,229,255,0.05)', line_width=0)
    for s in ['solar', 'wind', 'hybrid']:
        fig3.add_trace(go.Scatter(
            x=HOURS, y=scores[s]['voltage'],
            name=s.capitalize(), line=dict(color=colors[s], width=2)
        ))
    if inject_fault:
        fig3.add_vline(x=fault_hour, line_dash='dash', line_color='red')
    fig3.update_layout(
        title='Voltage Stability (pu)', plot_bgcolor='#0d1117',
        paper_bgcolor='#0d1117', font=dict(color='#ccc'),
        xaxis=dict(gridcolor='#1a1f2e'), yaxis=dict(gridcolor='#1a1f2e'), height=350
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── VARIABILITY BAR ────────────────────────────────────────────────────────
st.markdown("## 📉 Power Variability Comparison")
fig5 = go.Figure(go.Bar(
    x=['Solar', 'Wind', 'Hybrid'],
    y=[scores[s]['variability'] for s in ['solar', 'wind', 'hybrid']],
    marker_color=[colors[s] for s in ['solar', 'wind', 'hybrid']],
    text=[str(scores[s]['variability']) for s in ['solar', 'wind', 'hybrid']],
    textposition='outside'
))
fig5.update_layout(
    plot_bgcolor='#0d1117', paper_bgcolor='#0d1117',
    font=dict(color='#ccc'), yaxis_title='Variability Index (lower = better)',
    xaxis=dict(gridcolor='#1a1f2e'), yaxis=dict(gridcolor='#1a1f2e'), height=320
)
st.plotly_chart(fig5, use_container_width=True)

# ── RADAR CHART ────────────────────────────────────────────────────────────
st.markdown("## 🕸️ Radar Performance Chart")
categories = ['Frequency', 'Voltage', 'Variability', 'Fault Ride-Through']

fig6 = go.Figure()
for s in ['solar', 'wind', 'hybrid']:
    vals = [scores[s]['freq_score'], scores[s]['volt_score'],
            scores[s]['var_score'],  scores[s]['fault_score']]
    vals += [vals[0]]
    fig6.add_trace(go.Scatterpolar(
        r=vals, theta=categories + [categories[0]],
        fill='toself', name=s.capitalize(),
        line=dict(color=colors[s]),
        fillcolor=fill_colors[s]
    ))
fig6.update_layout(
    polar=dict(
        bgcolor='#0d1117',
        radialaxis=dict(visible=True, range=[0, 100], gridcolor='#333', color='#aaa'),
        angularaxis=dict(gridcolor='#333', color='#aaa')
    ),
    paper_bgcolor='#0d1117', font=dict(color='#ccc'),
    height=420, showlegend=True
)
st.plotly_chart(fig6, use_container_width=True)

# ── AI RECOMMENDATION ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🤖 AI Recommendation Engine")

worst = min(scores, key=lambda x: scores[x]['overall'])
improvement = round(scores['hybrid']['overall'] - scores[worst]['overall'], 1)

if scores['hybrid']['overall'] >= scores['solar']['overall'] and \
   scores['hybrid']['overall'] >= scores['wind']['overall']:
    verdict = "✅ **Hybrid Plant Wins** — Best grid stability across all parameters."
    color_verdict = "success"
elif scores['solar']['overall'] > scores['wind']['overall']:
    verdict = "⚠️ **Solar Plant performs better** under current conditions — but adding wind would improve stability further."
    color_verdict = "warning"
else:
    verdict = "⚠️ **Wind Plant performs better** under current conditions — but adding solar would improve stability further."
    color_verdict = "warning"

if color_verdict == "success":
    st.success(f"""
{verdict}

- 🏆 **{best.upper()}** achieves **{scores[best]['overall']}%** overall stability
- 📈 **{improvement}% more stable** than {worst} standalone plant
- 🔁 Frequency Score: Solar {scores['solar']['freq_score']}% | Wind {scores['wind']['freq_score']}% | Hybrid {scores['hybrid']['freq_score']}%
- 🔋 Voltage Score: Solar {scores['solar']['volt_score']}% | Wind {scores['wind']['volt_score']}% | Hybrid {scores['hybrid']['volt_score']}%
- 📉 Variability: Solar {scores['solar']['variability']} | Wind {scores['wind']['variability']} | Hybrid {scores['hybrid']['variability']}
- ⚡ Fault Recovery: Solar {scores['solar']['fault_score']}% | Wind {scores['wind']['fault_score']}% | Hybrid {scores['hybrid']['fault_score']}%

> **Conclusion:** Under current input conditions, **{best.upper()}** provides the most stable and reliable grid performance.
    """)
else:
    st.warning(f"""
{verdict}

- 🏆 Best performer: **{best.upper()}** at **{scores[best]['overall']}%**
- Solar: {scores['solar']['overall']}% | Wind: {scores['wind']['overall']}% | Hybrid: {scores['hybrid']['overall']}%

> Try adjusting the sliders to see how hybrid recovers advantage under balanced conditions.
    """)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#555;font-size:0.8rem'>⚡ Grid Stability Analyzer | Real-Time Interactive Simulation | Hackathon 2026</p>", unsafe_allow_html=True)
