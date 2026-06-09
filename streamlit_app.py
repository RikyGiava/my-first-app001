import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sprint Analytics Hub", 
    page_icon="⏱️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER AND ATHLETE PROFILE ---
st.title("⏱️ Sprint Analytics Hub")

with st.expander("👤 Athlete Profile & System Calibration", expanded=True):
    st.markdown("Enter the anthropometric and technical parameters to calibrate the IMU sensors and normalize impact forces.")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    athlete_class = col_p1.selectbox(
        "Paralympic Class", 
        ["T64 (Unilateral Transtibial)", "T62 (Bilateral Transtibial)", "T63 (Unilateral Transfemoral)", "T61 (Bilateral Transfemoral)"]
    )
    athlete_weight = col_p2.number_input("Body Weight (kg)", min_value=40.0, max_value=120.0, value=75.0, step=1.0)
    
    # PARAMETRO INSERITO: Lato della Protesi
    prosthesis_side = col_p3.selectbox(
        "Prosthesis Side (Laterality)", 
        ["Right Leg", "Left Leg", "Bilateral"]
    )

st.markdown(f"### Biomechanics Monitoring Profile: **{athlete_class}**")
st.markdown("---")

# --- MOCK DATA GENERATION (Weight & Side-dependent) ---
@st.cache_data
def generate_mock_data(weight_kg, side):
    samples = 2200
    t = np.linspace(0, 11, samples)  # 11 seconds of running
    
    sacrum_acc_z = np.sin(2 * np.pi * 2.2 * t) * 2 + np.random.normal(0, 0.2, samples)
    blade_acc_z = np.sin(2 * np.pi * 2.2 * t - 0.2) * 4 + np.random.normal(0, 0.5, samples) 
    socket_acc_y = np.sin(2 * np.pi * 2.2 * t) * 0.8 + np.random.normal(0, 0.1, samples)
    
    # GRF NORMALIZATION IN NEWTONS BASED ON ATHLETE'S WEIGHT
    bw_newtons = weight_kg * 9.81
    base_grf_multiplier = np.clip(np.sin(2 * np.pi * 2.2 * t), 0, None) ** 2 * 3.8 # Peak at ~3.8 BW
    grf_newtons = base_grf_multiplier * bw_newtons + np.random.normal(0, 50, samples) # Add noise
    
    distance_m = np.linspace(0, 100, samples) 
    
    # TRAJECTORY DRIFT BASED ON PROSTHESIS SIDE
    if side == "Right Leg":
        base_drift = np.sin(distance_m / 15) * 4  # Tends to drift right (Positive)
    elif side == "Left Leg":
        base_drift = -np.sin(distance_m / 15) * 4 # Tends to drift left (Negative)
    else:
        base_drift = np.sin(distance_m / 10) * 1  # Minor wobble for bilateral
        
    random_walk = np.cumsum(np.random.normal(0, 0.015, samples)) 
    sensor_noise = np.random.normal(0, 0.5, samples) 
    
    lateral_deviation_cm = base_drift + random_walk + sensor_noise
    lateral_deviation_cm -= lateral_deviation_cm[0] 
    
    df = pd.DataFrame({
        'Time_s': t,
        'Acc_Z_Sacrum': sacrum_acc_z,
        'Acc_Z_Blade': blade_acc_z,
        'Acc_Y_Socket': socket_acc_y,
        'Estimated_GRF_N': grf_newtons, 
        'Distance_m': distance_m,
        'Lateral_Dev_cm': lateral_deviation_cm
    })
    return df

# Generate data using the user-input weight AND side
df = generate_mock_data(athlete_weight, prosthesis_side)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚙️ Session Controls")
    time_range = st.slider("Select Time Window (s)", 0.0, 11.0, (0.0, 11.0), step=0.1)
    st.info("⚡ Sampling Rate: 200 Hz\n\n🎛️ Filter: 4th-order Butterworth (15 Hz)\n\n📷 Tracking: Optical Camera")

mask = (df['Time_s'] >= time_range[0]) & (df['Time_s'] <= time_range[1])
filtered_df = df[mask]

# --- COACH'S KPI HEADER ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="🏃‍♂️ Avg Cadence", value="4.4 Hz", delta="Optimal Resonance")
kpi2.metric(label="⏱️ Ground Contact Time", value="125 ms", delta="-5 ms vs Last Run", delta_color="inverse")
kpi3.metric(label="⚠️ Max Lateral Force", value="0.85 g", delta="+0.1 g", delta_color="inverse")
kpi4.metric(label="🔋 Drive to Fly Phase", value="1.20 s", delta="-0.08 s vs Target", delta_color="inverse")
st.markdown("---")

# --- INTERACTIVE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resonance & Sync", "⚖️ Stability & Lateral Forces", "💥 Ground Reaction Force", "🛤️ Trajectory"])

with tab1:
    fig_resonance = go.Figure()
    fig_resonance.add_trace(go.Scatter(x=filtered_df['Time_s'], y=filtered_df['Acc_Z_Sacrum'], name='Sacrum', line=dict(color='#00BFFF', width=2)))
    fig_resonance.add_trace(go.Scatter(x=filtered_df['Time_s'], y=filtered_df['Acc_Z_Blade'], name='Blade', line=dict(color='#FF1493', width=2, dash='dot')))
    fig_resonance.update_layout(xaxis_title="Time (s)", yaxis_title="Vertical Acc (g)", margin=dict(l=0, r=0, t=30, b=40))
    st.plotly_chart(fig_resonance, use_container_width=True)

with tab2:
    fig_lateral = go.Figure()
    fig_lateral.add_trace(go.Scatter(x=filtered_df['Time_s'], y=filtered_df['Acc_Y_Socket'], name='Socket', line=dict(color='#FF4500', width=2)))
    fig_lateral.update_layout(xaxis_title="Time (s)", yaxis_title="Lateral Acc (g)", margin=dict(l=0, r=0, t=30, b=40))
    st.plotly_chart(fig_lateral, use_container_width=True)

with tab3:
    st.subheader("Impulse & Energy Return")
    st.markdown("Estimates the elastic energy stored and released during the stance phase. Normalized to Body Weight.")
    
    # 1. GRF CHART (Continuous Area) in Newtons
    fig_grf = go.Figure()
    fig_grf.add_trace(go.Scatter(x=filtered_df['Time_s'], y=filtered_df['Estimated_GRF_N'], 
                                 name='Estimated GRF (N)', line=dict(color='#00FA9A', width=3), 
                                 fill='tozeroy', fillcolor='rgba(0, 250, 154, 0.2)'))
    fig_grf.update_layout(xaxis_title="Time (s)", yaxis_title="Ground Reaction Force (N)",
                          hovermode="x unified", margin=dict(l=0, r=0, t=30, b=40))
    st.plotly_chart(fig_grf, use_container_width=True)

    # 2. STEP EXTRACTION ALGORITHM
    st.markdown("#### 📈 Step-by-Step Evolution")
    
    grf_values = filtered_df['Estimated_GRF_N'].values
    time_values = filtered_df['Time_s'].values
    dt = 1 / 200 
    
    step_nums, contact_times, impulses = [], [], []
    in_stance = False
    current_impulse = 0
    current_stance_samples = 0
    step_count = 1
    
    threshold = athlete_weight * 9.81 * 0.20 
    
    for i in range(len(grf_values)):
        if grf_values[i] > threshold: 
            in_stance = True
            current_impulse += grf_values[i] * dt
            current_stance_samples += 1
        else:
            if in_stance:
                if current_stance_samples * dt > 0.05: 
                    step_nums.append(f"Step {step_count}")
                    contact_times.append(current_stance_samples * dt * 1000) 
                    impulses.append(current_impulse)
                    step_count += 1
                in_stance = False
                current_impulse = 0
                current_stance_samples = 0

    # 3. DUAL AXIS CHART
    if len(step_nums) > 0:
        fig_steps = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_steps.add_trace(
            go.Bar(x=step_nums, y=impulses, name="Calculated Impulse (N·s)", 
                   marker_color='rgba(31, 119, 180, 0.6)', marker_line_color='rgba(31, 119, 180, 1)', 
                   marker_line_width=1.5, width=0.4), secondary_y=False)
        
        fig_steps.add_trace(
            go.Scatter(x=step_nums, y=contact_times, name="Contact Time (ms)", mode='lines+markers', 
                       line=dict(color='#FF4500', width=3), marker=dict(size=8, symbol='diamond')), secondary_y=True)

        fig_steps.update_layout(title="Stride Analysis Trend: Impulse vs Contact Time", hovermode="x unified",
                                margin=dict(l=0, r=0, t=40, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), bargap=0.5)
        
        # Taratura corretta dell'asse Y (che nel tuo codice tagliava le colonne)
        max_impulse = max(impulses)
        fig_steps.update_yaxes(title_text="Impulse (N·s)", secondary_y=False, showgrid=False, rangemode="tozero", range=[0.95* max_impulse, max_impulse * 1.05])
        
        min_ct, max_ct = min(contact_times), max(contact_times)
        fig_steps.update_yaxes(title_text="Contact Time (ms)", secondary_y=True, showgrid=False, range=[min_ct * 0.95, max_ct * 1.05])
        
        st.plotly_chart(fig_steps, use_container_width=True)
    else:
        st.warning("No steps detected in the selected time window.")

with tab4:
    st.subheader("Trajectory & Lateral Deviations (100m Sprint)")
    fig_traj = go.Figure()
    fig_traj.add_hline(y=61, line_dash="solid", line_color="white", line_width=4)
    fig_traj.add_hline(y=-61, line_dash="solid", line_color="white", line_width=4)
    fig_traj.add_hline(y=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.6)", annotation_text="Track Center", annotation_font_color="white")
    fig_traj.add_trace(go.Scatter(x=filtered_df['Distance_m'], y=filtered_df['Lateral_Dev_cm'], mode='lines', name='Athlete Path', line=dict(color='#FFFF00', width=3)))
    fig_traj.update_layout(xaxis_title="Distance Covered (m)", yaxis_title="Lateral Deviation (cm)",
                           hovermode="x unified", margin=dict(l=0, r=0, t=30, b=40), plot_bgcolor='#C84B31', 
                           yaxis=dict(range=[-75, 75], showgrid=False, zeroline=False), 
                           xaxis=dict(showgrid=False, zeroline=False))
    st.plotly_chart(fig_traj, use_container_width=True)
    
    # Il tooltip finale si aggiorna dinamicamente in base al lato scelto
    st.info(f"💡 **Coach Insight:** Athlete selected with **{prosthesis_side}** amputation. Track expected deviation towards the prosthetic side. Corrections to the socket alignment are recommended if deviations exceed ±5 cm.")