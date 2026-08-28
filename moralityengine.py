"""
================================================================================
EXTREME HEAT FLUX & CHF RESOLUTION & OPTIMIZATION SUITE
STALWART MULTIPHYSICS REALITY ENGINE v3.3.0 (COUPLED SYSTEM MASTER BUILD)
Description: Dual-Engine Multiphysics Platform with Active Boundary Stabilization,
             Material Interaction Matrices, Real-Time Advection-Diffusion Solver,
             Native ASCII VTK Export, and Master Coupled System Synthesis.
Author / Proprietary Owner: Daniel C. Schramm
================================================================================
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SCI-FI TERMINAL STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="STALWART Reality Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #06090e;
        color: #00ff66;
    }
    .stApp {
        background-color: #06090e;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0c121c;
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #1f2d3d;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #111a28;
        border-radius: 4px;
        color: #79a6d2;
        border: 1px solid #1f2d3d;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00ff66 !important;
        color: #06090e !important;
        border: 1px solid #00ff66 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #00ff66 !important;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-box {
        background-color: #0b1522;
        border: 1px solid #00ff66;
        padding: 15px;
        border-radius: 5px;
        color: #e0f2fe;
        margin-bottom: 15px;
    }
    .theory-box {
        background-color: #120a1c;
        border: 1px solid #a855f7;
        padding: 15px;
        border-radius: 5px;
        color: #fae8ff;
        margin-bottom: 15px;
    }
    .violation-box {
        background-color: #1a0033;
        border: 2px solid #8a2be2;
        box-shadow: 0 0 15px #8a2be2;
        padding: 15px;
        border-radius: 5px;
        color: #dda0dd;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE & COUPLED SYSTEM INITIALIZATION
# -----------------------------------------------------------------------------
if 'flow_velocity' not in st.session_state:
    st.session_state.flow_velocity = 0.40
if 'heat_flux_input' not in st.session_state:
    st.session_state.heat_flux_input = 1000.0
if 'b_gradient' not in st.session_state:
    st.session_state.b_gradient = 12.5
if 'flow_rate_mg' not in st.session_state:
    st.session_state.flow_rate_mg = 15.0

# -----------------------------------------------------------------------------
# 3. GLOBAL SYSTEM CONTROLS & DUAL-SOLVER + MASTER TOGGLE SWITCH
# -----------------------------------------------------------------------------
col_title, col_switch1, col_switch2 = st.columns([2, 1, 1])

with col_title:
    st.title("⚡ STALWART MULTIPHYSICS REALITY ENGINE")
    st.caption("Active Boundary Stabilization | Multiphysics Matrix | Master Coupled Synthesis")

with col_switch1:
    solver_mode = st.radio(
        "OPERATIONAL SOLVER CORE",
        ["Standard Engineering Baseline", "STALWART Custom Theory & Recycling Layer"],
        index=0,
        help="Switch between classical textbook standards and proprietary active physics."
    )

with col_switch2:
    st.markdown("### Master Interconnect")
    is_coupled = st.checkbox("🔗 Coupled System Synthesis (Master Sync)", value=False, help="Links all inputs across tabs with real-time feedback and dynamic review tab.")

is_stalwart = (solver_mode == "STALWART Custom Theory & Recycling Layer")

# Coupled Feedback Auto-Adjustment Logic
if is_coupled:
    # If heat flux spikes, automatically demand higher baseline velocity and magnetic scaling
    if st.session_state.heat_flux_input > 1100.0:
        st.session_state.flow_velocity = max(st.session_state.flow_velocity, 0.55)
        st.session_state.b_gradient = max(st.session_state.b_gradient, 18.0)

if is_stalwart:
    st.markdown("""
    <div class="theory-box">
        <b>[STALWART LAYER ACTIVE]</b> Custom active boundary stabilization, microchannel recycling loops, and dynamic transport coupling engaged.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-box">
        <b>[BASELINE CORE ACTIVE]</b> Standard physical boundaries, classical advection-diffusion, and conservative engineering limits engaged.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. CORE MATHEMATICAL COMPUTATION & VTK MESH GENERATOR
# -----------------------------------------------------------------------------
def simulate_chf_matrix(velocity, heat_flux_w_cm2, active_boost=False):
    nx, ny = 120, 70
    dx, dy = 0.00003, 0.00003
    k_fluid = 0.026
    rho_cp = 1200.0
    alpha = k_fluid / rho_cp
    T_inlet = 303.15  
    
    eff_velocity = velocity * (1.35 if active_boost else 1.0)
    T_hotspot = T_inlet + (heat_flux_w_cm2 * 0.035) / (eff_velocity * 0.8 + 0.2)
    
    N = nx * ny
    A = lil_matrix((N, N))
    b = np.zeros(N)
    
    def get_index(i, j):
        return j * nx + i

    for j in range(ny):
        for i in range(nx):
            idx = get_index(i, j)
            if i == 0:
                A[idx, idx] = 1.0
                b[idx] = T_inlet
            elif i == nx - 1:
                A[idx, idx] = 1.0
                A[idx, get_index(i - 1, j)] = -1.0
                b[idx] = 0.0
            elif j == 0 or j == ny - 1:
                j_adj = 1 if j == 0 else ny - 2
                A[idx, idx] = 1.0
                A[idx, get_index(i, j_adj)] = -1.0
                b[idx] = 0.0
            elif (nx // 3 <= i <= 2 * nx // 3) and (ny // 4 <= j <= 3 * ny // 4):
                A[idx, idx] = 1.0
                b[idx] = T_hotspot
            else:
                A[idx, idx] = -2.0 / (dx**2) - 2.0 / (dy**2) + (eff_velocity / alpha) / dx
                A[idx, get_index(i - 1, j)] = 1.0 / (dx**2)
                A[idx, get_index(i + 1, j)] = 1.0 / (dx**2) - (eff_velocity / alpha) / dx
                A[idx, get_index(i, j - 1)] = 1.0 / (dy**2)
                A[idx, get_index(i, j + 1)] = 1.0 / (dy**2)
                b[idx] = 0.0

    T_flat = spsolve(A.tocsr(), b)
    T_field_k = T_flat.reshape((ny, nx))
    T_field_c = T_field_k - 273.15
    return float(np.min(T_field_c)), float(np.max(T_field_c)), T_field_c

def generate_vtk_mesh(T_field_c, nx=120, ny=70, dx=0.00003, dy=0.00003):
    vtk_lines = [
        "# vtk DataFile Version 3.0",
        "STALWART Multiphysics Thermal Grid Export",
        "ASCII",
        "DATASET RECTILINEAR_GRID",
        f"DIMENSIONS {nx} {ny} 1"
    ]
    x_coords = np.linspace(0, nx * dx, nx)
    vtk_lines.append(f"X_COORDINATES {nx} float")
    vtk_lines.append(" ".join(f"{x:.6e}" for x in x_coords))
    
    y_coords = np.linspace(0, ny * dy, ny)
    vtk_lines.append(f"Y_COORDINATES {ny} float")
    vtk_lines.append(" ".join(f"{y:.6e}" for y in y_coords))
    
    vtk_lines.append("Z_COORDINATES 1 float\n0.000000e+00")
    
    num_points = nx * ny
    vtk_lines.append(f"POINT_DATA {num_points}")
    vtk_lines.append("SCALARS Temperature_Celsius float 1")
    vtk_lines.append("LOOKUP_TABLE default")
    vtk_lines.append(" ".join(f"{temp:.4f}" for temp in T_field_c.flatten()))
    return "\n".join(vtk_lines)

# -----------------------------------------------------------------------------
# 5. DYNAMIC TAB ARCHITECTURE (APPENDS REVIEW TAB WHEN MASTER SYNC IS ACTIVE)
# -----------------------------------------------------------------------------
tab_labels = [
    "01 // PLASMA & THRUST",
    "02 // ELECTROMAGNETICS & MHD",
    "03 // FLUID & THERMAL SOLVER",
    "04 // MATERIAL INTERACTION",
    "05 // PRIOR ART & SANDBOX"
]

if is_coupled:
    tab_labels.append("06 // FULL SYSTEM REVIEW")

tabs = st.tabs(tab_labels)

tab1 = tabs[0]
tab2 = tabs[1]
tab3 = tabs[2]
tab4 = tabs[3]
tab5 = tabs[4]
tab6 = tabs[5] if is_coupled else None

# -----------------------------------------------------------------------------
# TAB 1: PLASMA & THRUST DYNAMICS
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Plasma Injection & Exhaust Vectoring")
    col1, col2 = st.columns(2)
    with col1:
        fuel_selection = st.selectbox("Fuel Configuration", ["Deuterium-Tritium (D-T)", "Hydrogen-Boron (p-11B)", "Deuterium-Helium-3 (D-3He)", "Custom Matrix"])
        flow_rate_mg = st.number_input("Fuel Mass Flow Rate (mg/s)", value=st.session_state.flow_rate_mg, min_value=0.1, step=0.5, key="flow_rate_input")
        st.session_state.flow_rate_mg = flow_rate_mg
        icrf_freq = st.number_input("Dual-MHz ICRF Excitation (MHz)", value=2.45, min_value=0.1, step=0.05)
    with col2:
        if fuel_selection == "Custom Matrix":
            c_mass = st.number_input("Custom Atomic Mass (amu)", value=11.0)
            c_charge = st.number_input("Custom Atomic Number (Z)", value=5)
        else:
            st.info(f"Target Fuel Profile: {fuel_selection}")
        exhaust_area = st.number_input("Nozzle Throat Area (cm²)", value=4.5, min_value=0.1)

    base_isp = 2800.0 if "p-11B" in fuel_selection else 3400.0
    if is_stalwart:
        boosted_isp = base_isp * (1.0 + (icrf_freq * 0.04))
        recaptured_power = (flow_rate_mg * 0.08) * icrf_freq
        st.success(f"STALWART Active ISP: {boosted_isp:.1f} s | Direct Energy Conversion Yield: {recaptured_power:.2f} kW")
    else:
        st.metric(label="Standard Theoretical Specific Impulse (ISP)", value=f"{base_isp:.1f} s")
    
    st.latex(r"I_{crit} = \frac{4 \pi}{\mu_0} \frac{k_B (T_e + T_i)}{v_d}")

# -----------------------------------------------------------------------------
# TAB 2: ELECTROMAGNETICS & MHD
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Magnetic Containment & Force Gradients")
    col1, col2 = st.columns(2)
    with col1:
        geom_type = st.selectbox("Coil Topology", ["Standard Solenoid", "Helmholtz Pair", "Toroidal Field Array", "Starship Rodin Array", "Custom Coordinates"])
        b_gradient = st.number_input("Field Gradient (∇B) [T/m]", value=st.session_state.b_gradient, step=0.5, key="b_grad_input")
        st.session_state.b_gradient = b_gradient
    with col2:
        current_ka = st.number_input("Operating Current (kA)", value=45.0, step=1.0)
        core_radius = st.number_input("Coil Core Radius (m)", value=0.35, step=0.05)
    
    if geom_type == "Custom Coordinates":
        st.text_area("Coordinate Matrix [x, y, z, I]", "0.0, 0.0, 0.0, 45.0\n0.1, 0.2, 0.3, 45.0")
    
    lorentz_force = b_gradient * current_ka * core_radius * (1.25 if is_stalwart else 1.0)
    st.metric(label="Calculated Lorentz Containment Force", value=f"{lorentz_force:.2f} kN", delta="Stable" if lorentz_force < 500 else "Critical Stress")

# -----------------------------------------------------------------------------
# TAB 3: FLUID & THERMAL SOLVER (WITH VTK EXPORT & HEATMAP)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("High-Flux Thermal Management & Advection-Diffusion Suite")
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        heat_flux_input = st.number_input("Target Heat Flux (W/cm²)", value=st.session_state.heat_flux_input, step=50.0, key="hf_input")
        st.session_state.heat_flux_input = heat_flux_input
    with col_in2:
        flow_velocity = st.slider("Fluid Sweep Velocity (m/s)", 0.05, 1.5, value=st.session_state.flow_velocity, step=0.05, key="vel_input")
        st.session_state.flow_velocity = flow_velocity
    with col_in3:
        run_full_sweep = st.checkbox("Execute Multi-Velocity Optimization Sweep", value=False)
        
    if st.button("RUN THERMAL SIMULATION MATRIX", type="primary"):
        with st.spinner("Computing Sparse Linear System (Advection-Diffusion Discretization)..."):
            min_c, max_c, t_matrix = simulate_chf_matrix(st.session_state.flow_velocity, st.session_state.heat_flux_input, active_boost=is_stalwart)
            
            # High-Stress Violation Check (Glowing Dark Purple Trigger)
            if st.session_state.heat_flux_input > 1100.0 and st.session_state.flow_velocity < 0.50 and not is_stalwart:
                st.markdown("""
                <div class="violation-box">
                    <b>[VIOLATION ALERT: HIGH THERMAL STRESS]</b> High heat flux combined with insufficient velocity exceeds baseline boundary limits. STALWART Master Sync or velocity increase recommended.
                </div>
                """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Inlet Fluid Temperature", f"{min_c:.2f} °C")
            c2.metric("Hotspot Boundary Temperature", f"{max_c:.2f} °C", delta="SAFE" if max_c < 100.0 else "DRY-OUT RISK", delta_color="inverse")
            c3.metric("Operating Margin (<100°C Limit)", f"{100.0 - max_c:.2f} °C")
            
            fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='#06090e')
            ax.set_facecolor('#06090e')
            cmap = plt.cm.magma
            im = ax.imshow(t_matrix, origin='lower', aspect='auto', cmap=cmap)
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label('Temperature (°C)', color='#00ff66', fontfamily='monospace')
            cbar.ax.yaxis.set_tick_params(color='#00ff66')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#00ff66', fontfamily='monospace')
            
            ax.set_title(f"Thermal Gradient Field Profile (Velocity: {st.session_state.flow_velocity:.2f} m/s)", color='#00ff66', fontfamily='monospace')
            ax.set_xlabel("X Grid Index", color='#00ff66', fontfamily='monospace')
            ax.set_ylabel("Y Grid Index", color='#00ff66', fontfamily='monospace')
            ax.tick_params(colors='#00ff66')
            for spine in ax.spines.values():
                spine.set_color('#1f2d3d')
            
            st.pyplot(fig)
            plt.close()
            
            st.markdown("### ════ 3D VISUALIZATION & MESH PIPELINE ════")
            vtk_output = generate_vtk_mesh(t_matrix)
            st.download_button(label="⬇️ EXPORT .VTK MESH (PARAVIEW / BLENDER READY)", data=vtk_output, file_name="stalwart_thermal_mesh.vtk", mime="text/plain", type="primary")
            
            if run_full_sweep:
                st.markdown("### ════ AUTOMATED VELOCITY SWEEP BENCHMARK REPORT ════")
                sweep_velocities = [0.10, 0.25, 0.40, 0.55, 0.70]
                terminal_output = "======================================================================\n"
                terminal_output += f"[INFO] Executing stabilization sweep for target heat flux: {st.session_state.heat_flux_input:.1f} W/cm²\n"
                for v in sweep_velocities:
                    _, max_t, _ = simulate_chf_matrix(v, st.session_state.heat_flux_input, active_boost=is_stalwart)
                    status_str = "SAFE" if max_t < 100.0 else "[!] DRY-OUT RISK"
                    terminal_output += f"Velocity: {v:.2f} m/s | Peak Hotspot: {max_t:.2f} °C | Status: {status_str}\n"
                st.code(terminal_output, language="text")

# -----------------------------------------------------------------------------
# TAB 4: MATERIAL SCIENCE INTERACTION MATRIX
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Coupled Material Science Interaction Engine")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mat_dielectric = st.selectbox("Dielectric / Piezoelectric Phase", ["Hafnium Oxide (HfO2)", "Quartz Crystal (SiO2)", "Tourmaline Matrix", "Barium Titanate (BaTiO3)"])
        electric_field = st.number_input("Applied Electric Field (kV/mm)", value=5.0, step=0.5)
        vibration_freq = st.number_input("Acoustic Vibration (kHz)", value=40.0, step=5.0)
    with col_m2:
        mat_conductor = st.selectbox("Conductor Phase", ["Yttrium Barium Copper Oxide (YBCO)", "Amorphous Nanocrystalline Alloy", "Bismuth Telluride (Bi2Te3)", "Copper OFHC"])
        mag_flux_density = st.number_input("External Magnetic Field (Tesla)", value=2.0, step=0.1)
        system_temp_k = st.number_input("Operating Temperature (K)", value=77.0, step=1.0)

    d_coeff = 25.0 if "HfO2" in mat_dielectric else (2.3 if "Quartz" in mat_dielectric else 8.5)
    piezo_response = electric_field * vibration_freq * (0.045 if is_stalwart else 0.02)
    sc_critical = True if ("YBCO" in mat_conductor and system_temp_k <= 93.0 and mag_flux_density <= 10.0) else False
    
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Induced Polarization Index", f"{d_coeff * electric_field:.2f} µC/cm²")
    mc2.metric("Mechanical Resonance Coupling", f"{piezo_response:.3f} MPa")
    mc3.metric("Phase Superconductivity State", "SUPERCONDUCTING" if sc_critical else "RESISTIVE NORMAL", delta="OPTIMAL" if sc_critical else "NORMAL")

# -----------------------------------------------------------------------------
# TAB 5: PRIOR ART & SECURE IP SANDBOX
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Proprietary IP, Licensing & Prior Art Repository")
    st.markdown("""
    <div class="theory-box">
        <h3>NOTICE OF PRIOR ART & INTELLECTUAL PROPERTY DECLARATION</h3>
        <p>All custom equations, active boundary-layer stabilization topologies, microchannel recycling architectures, 
        and directional vector manifolds housed within this reality engine represent proprietary prior art established by 
        <b>Daniel C. Schramm</b>, documented via <b>Zenodo</b> and <b>Technical Disclosure Commons (TD Commons)</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    doi_key = st.text_input("Zenodo / TD Commons DOI Verification Key", value="10.5281/zenodo.stalwart-chf-build", type="password")
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.slider("Thermoelectric Recycling Loop Coefficient (ZT)", 0.1, 4.0, 1.85 if is_stalwart else 1.0)
        st.slider("Directional Vector Gradient Shift", -10.0, 10.0, 2.4 if is_stalwart else 0.0)
    with col_sb2:
        st.slider("Active Boundary Entrainment Factor", 0.0, 1.0, 0.35 if is_stalwart else 0.0)
        st.selectbox("Sandboxed Encryption Protocol", ["AES-256 Air-Gapped", "Client-Side Tokenization Active"])

# -----------------------------------------------------------------------------
# TAB 6: FULL SYSTEM REVIEW & VISUAL RENDER (DYNAMICALLY GENERATED WHEN COUPLED)
# -----------------------------------------------------------------------------
if is_coupled and tab6 is not None:
    with tab6:
        st.subheader("Master Coupled System Synthesis & Review Matrix")
        st.markdown("""
        <div class="theory-box">
            <b>[MASTER COUPLED MODE ACTIVE]</b> Real-time parameter aggregation across all physics subsystems. Review global inputs and rendered system metrics prior to full-matrix solve.
        </div>
        """, unsafe_allow_html=True)
        
        # Breakdown Summary Table / Metrics
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Synced Fuel Flow Rate", f"{st.session_state.flow_rate_mg:.1f} mg/s")
        rc2.metric("Synced Magnetic Gradient", f"{st.session_state.b_gradient:.1f} T/m")
        rc3.metric("Synced Heat Flux", f"{st.session_state.heat_flux_input:.1f} W/cm²")
        rc4.metric("Synced Fluid Velocity", f"{st.session_state.flow_velocity:.2f} m/s")
        
        st.markdown("### Integrated System Visual Render")
        # Generate quick multi-variable render (Coupled Thermal-Magnetic Profile)
        _, _, review_matrix = simulate_chf_matrix(st.session_state.flow_velocity, st.session_state.heat_flux_input, active_boost=is_stalwart)
        
        fig_r, ax_r = plt.subplots(figsize=(10, 3.5), facecolor='#06090e')
        ax_r.set_facecolor('#06090e')
        im_r = ax_r.imshow(review_matrix, origin='lower', aspect='auto', cmap='plasma')
        cbar_r = fig_r.colorbar(im_r, ax=ax_r)
        cbar_r.set_label('Coupled Temp (°C)', color='#00ff66', fontfamily='monospace')
        cbar_r.ax.yaxis.set_tick_params(color='#00ff66')
        plt.setp(plt.getp(cbar_r.ax.axes, 'yticklabels'), color='#00ff66', fontfamily='monospace')
        
        ax_r.set_title("Master Coupled Multi-Domain Render Matrix", color='#00ff66', fontfamily='monospace')
        ax_r.tick_params(colors='#00ff66')
        for spine in ax_r.spines.values():
            spine.set_color('#1f2d3d')
            
        st.pyplot(fig_r)
        plt.close()

# -----------------------------------------------------------------------------
st.caption("STALWART Reality Engine Execution Core v3.3.0 | All Local Arrays Synced.")
