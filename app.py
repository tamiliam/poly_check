import streamlit as st
import pandas as pd
# Ensure description.py is in the same folder and has no syntax errors
from description import get_course_details

# --- PAGE SETUP ---
st.set_page_config(page_title="Semakan TVET (Politeknik & Komuniti)", page_icon="🇲🇾", layout="wide")

# --- CUSTOM CSS FOR METRICS ---
st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #004E98;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def clean_header(text):
    return str(text).strip().replace("\ufeff", "").lower()

def is_active(value):
    s = str(value).strip().lower()
    return s in ['1', '1.0', 'true', 'yes', 'y']

def is_pass(g): return str(g).strip() in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
def is_credit(g): return str(g).strip() in ["A+", "A", "A-", "B+", "B", "C+", "C"]

# --- LOAD DATA ---
@st.cache_data
def load_data_v17():
    # Ensure these 4 files exist in your folder
    courses = pd.read_csv("courses.csv", encoding="latin1")
    institutions = pd.read_csv("institutions.csv", encoding="latin1")
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1")

    # Clean Headers
    for df in [courses, institutions, reqs, links]:
        df.columns = [clean_header(c) for c in df.columns]

    # Clean IDs to ensure matching works
    for df in [courses, reqs, links]:
        df['course_id'] = df['course_id'].astype(str).str.strip()
    
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    institutions['institution_id'] = institutions['institution_id'].astype(str).str.strip()

    return courses, institutions, reqs, links

try:
    courses_df, inst_df, reqs_df, links_df = load_data_v17()
except Exception as e:
    st.error(f"Ralat memuatkan pangkalan data: {e}")
    st.stop()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Semakan TVET Malaysia")
st.sidebar.caption("Politeknik & Kolej Komuniti")

with st.sidebar.expander("👤 Maklumat Peribadi", expanded=True):
    nationality = st.radio("Warganegara", ["Warganegara", "Bukan Warganegara"], key="nat")
    gender = st.radio("Jantina", ["Lelaki", "Perempuan"], key="gen")
    
    st.write("**Status Kesihatan**")
    colorblind = st.radio("Buta Warna?", ["Tidak", "Ya"], key="cb")
    disability = st.radio("Kecacatan Fizikal?", ["Tidak", "Ya"], key="dis")

grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G", "Tidak Ambil"]

with st.sidebar.expander("📚 Subjek Teras (SPM)", expanded=True):
    bm_grade = st.selectbox("Bahasa Melayu", grade_opts, index=5, key="bm")
    eng_grade = st.selectbox("Bahasa Inggeris", grade_opts, index=6, key="eng")
    hist_grade = st.selectbox("Sejarah", grade_opts, index=6, key="hist")
    math_grade = st.selectbox("Matematik", grade_opts, index=5, key="math")
    islam_moral = st.selectbox("P. Islam / P. Moral", grade_opts, index=5, key="rel")

with st.sidebar.expander("🧪 Aliran Sains"):
    addmath_grade = st.selectbox("Matematik Tambahan", grade_opts, index=10, key="am")
    phy_grade = st.selectbox("Fizik", grade_opts, index=10, key="phy")
    chem_grade = st.selectbox("Kimia", grade_opts, index=10, key="chem")
    bio_grade = st.selectbox("Biologi", grade_opts, index=10, key="bio")

with st.sidebar.expander("🎨 Sastera & Kemanusiaan"):
    sci_gen = st.selectbox("Sains (Umum)", grade_opts, index=10, key="sci")
    geo_grade = st.selectbox("Geografi", grade_opts, index=10, key="geo")
    acc_grade = st.selectbox("Prinsip Perakaunan", grade_opts, index=10, key="acc")
    biz_grade = st.selectbox("Perniagaan", grade_opts, index=10, key="biz")
    econ_grade = st.selectbox("Ekonomi", grade_opts, index=10, key="econ")
    psv_grade = st.selectbox("Pendidikan Seni Visual", grade_opts, index=10, key="psv")

with st.sidebar.expander("🕌 Bahasa & Elektif Lain"):
    lang_add = st.selectbox("B. Arab / Cina / Tamil / Punjabi", grade_opts, index=10, key="lang")
    lit_grade = st.selectbox("Kesusasteraan", grade_opts, index=10, key="lit")
    islam_add = st.selectbox("P. Al-Quran / As-Sunnah / Syariah", grade_opts, index=10, key="rel_add")

with st.sidebar.expander("🛠️ Elektif Teknikal"):
    rc_grade = st.selectbox("Reka Cipta", grade_opts, index=10, key="rc")
    cs_grade = st.selectbox("Sains Komputer", grade_opts, index=10, key="cs")
    agro_grade = st.selectbox("Pertanian", grade_opts, index=10, key="agro")
    srt_grade = st.selectbox("Sains Rumah Tangga", grade_opts, index=10, key="srt")
    other_tech = st.checkbox("Kepujian (C+) Subjek Teknikal Lain", key="tech_chk")
    other_voc = st.checkbox("Kepujian (C+) Subjek Vokasional Lain", key="voc_chk")

# --- CALCULATION & LOGIC ---
all_subs = [
    bm_grade, eng_grade, hist_grade, math_grade, islam_moral, 
    addmath_grade, phy_grade, chem_grade, bio_grade, 
    sci_gen, geo_grade, acc_grade, biz_grade, econ_grade, psv_grade, 
    lang_add, lit_grade, islam_add, 
    rc_grade, cs_grade, agro_grade, srt_grade
]

calculated_credits = sum(1 for g in all_subs if is_credit(g))
if other_tech: calculated_credits += 1
if other_voc: calculated_credits += 1

st.sidebar.info(f"📊 Jumlah Kredit Dikira: {calculated_credits}")

def check_gatekeepers():
    if nationality == "Bukan Warganegara": return False, "Warganegara Malaysia Diperlukan."
    if not is_pass(bm_grade): return False, "Wajib Lulus Bahasa Melayu."
    if not is_pass(hist_grade): return False, "Wajib Lulus Sejarah."
    return True, "OK"

def check_row_constraints(req):
    # Demographics
    if is_active(req.get('req_male')) and gender == "Perempuan": return False
    if is_active(req.get('no_colorblind')) and colorblind == "Ya": return False
    if is_active(req.get('no_disability')) and disability == "Ya": return False

    # Mandatory Passes
    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): return False
    if is_active(req.get('pass_math')) and not is_pass(math_grade): return False

    # Mandatory Credits
    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): return False
    if is_active(req.get('credit_math')) and not is_credit(math_grade): return False
    if is_active(req.get('credit_eng')) and not is_credit(eng_grade): return False
    
    if is_active(req.get('credit_bmbi')) and not (is_credit(bm_grade) or is_credit(eng_grade)): return False

    # Group Logic
    has_pure_science_pass = any(is_pass(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
    has_tech_pass = any(is_pass(g) for g in [rc_grade, cs_grade]) or other_tech
    has_voc_pass = any(is_pass(g) for g in [agro_grade, srt_grade]) or other_voc
    stv_pass = is_pass(sci_gen) or has_pure_science_pass or has_tech_pass or has_voc_pass
    
    if is_active(req.get('pass_stv')) and not stv_pass: return False
    
    has_pure_science_credit = any(is_credit(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
    has_tech_credit = any(is_credit(g) for g in [rc_grade, cs_grade]) or other_tech
    has_voc_credit = any(is_credit(g) for g in [agro_grade, srt_grade]) or other_voc
    stv_credit = is_credit(sci_gen) or has_pure_science_credit or has_tech_credit or has_voc_credit
    
    if is_active(req.get('credit_stv')) and not stv_credit: return False

    if is_active(req.get('credit_sf')):
        if not (is_credit(sci_gen) or is_credit(phy_grade)): return False
    
    if is_active(req.get('credit_sfmt')):
        if not (is_credit(sci_gen) or is_credit(phy_grade) or is_credit(addmath_grade)): return False

    try: min_c = int(float(req.get('min_credits', 0)))
    except: min_c = 0
    
    if calculated_credits < min_c: return False

    return True

# --- MAIN BUTTON ---
if st.sidebar.button("Semak Kelayakan", type="primary"):
    passed, msg = check_gatekeepers()
    if not passed:
        st.session_state['eligible_ids'] = []
        st.session_state['fail_reason'] = msg
        st.session_state['checked'] = True
    else:
        e_ids = []
        # Filter: Check every requirement row for every course
        grouped = reqs_df.groupby('course_id')
        for cid, group in grouped:
            if group.apply(check_row_constraints, axis=1).all():
                e_ids.append(cid)
        
        st.session_state['eligible_ids'] = e_ids
        st.session_state['fail_reason'] = None
        st.session_state['checked'] = True

# --- RESULT DISPLAY ---
if st.session_state.get('checked'):
    e_ids = st.session_state['eligible_ids']
    fail_reason = st.session_state.get('fail_reason')

    if fail_reason:
        st.error(f"❌ Tidak Layak: {fail_reason}")
    elif not e_ids:
        st.warning(f"Tiada program layak berdasarkan keputusan ini. Kredit: {calculated_credits}")
    else:
        # Split Data into Poly vs Kolej Komuniti
        # Logic: Poly IDs start with 'POLY', KK IDs usually start with 'KK' or have 'CET'
        poly_ids = [i for i in e_ids if "POLY" in i]
        kk_ids = [i for i in e_ids if "POLY" not in i] 

        st.markdown("### 🎉 Tahniah! Anda Layak.")
        
        # Metric Dashboard
        m1, m2, m3 = st.columns(3)
        m1.metric("Politeknik (Diploma)", f"{len(poly_ids)} Program")
        m2.metric("Kolej Komuniti (Sijil/Dip)", f"{len(kk_ids)} Program")
        m3.metric("Jumlah Kredit", f"{calculated_credits}")

        # --- TABS UI ---
        tab1, tab2 = st.tabs(["🏛️ Politeknik", "🛠️ Kolej Komuniti"])

        # === TAB 1: POLITEKNIK ===
        with tab1:
            if not poly_ids:
                st.info("Tiada program Politeknik yang layak.")
            else:
                poly_res = courses_df[courses_df['course_id'].isin(poly_ids)]
                st.dataframe(
                    poly_res[['course', 'department']].rename(columns={'course':'Nama Program', 'department':'Jabatan'}), 
                    hide_index=True, 
                    use_container_width=True
                )
                
                # Selection Scoped to Poly
                st.markdown("---")
                st.subheader("🔍 Lihat Detail Program Politeknik")
                sel_poly = st.selectbox("Pilih Program:", poly_res['course'].unique(), key="sel_poly")
                
                if sel_poly:
                    cid = poly_res[poly_res['course'] == sel_poly].iloc[0]['course_id']
                    details = get_course_details(cid, sel_poly)
                    
                    with st.container():
                        st.info(f"### {details['headline']}")
                        st.write(details['synopsis'])
                        
                        # Conditional Pathway
                        if 'pathway' in details: 
                            st.write(f"**🎓 Laluan Sambung Belajar:** {details['pathway']}")
                        
                        st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                        
                        # Interview Check
                        rows = reqs_df[reqs_df['course_id'] == cid]
                        if rows['req_interview'].apply(is_active).any():
                            st.warning("🗣️ Temuduga Diperlukan.")
                    
                    # Locations
                    pids = links_df[links_df['course_id'] == cid]['institution_id']
                    final_loc = inst_df[inst_df['institution_id'].isin(pids)]
                    
                    if not final_loc.empty:
                        st.markdown("**📍 Lokasi:**")
                        st.dataframe(
                            final_loc[['institution_name', 'state', 'url']].rename(columns={'institution_name':'Institusi', 'state':'Negeri', 'url':'Web'}),
                            column_config={"Web": st.column_config.LinkColumn("Web", display_text="Layari")},
                            hide_index=True,
                            use_container_width=True
                        )

        # === TAB 2: KOLEJ KOMUNITI ===
        with tab2:
            if not kk_ids:
                st.info("Tiada program Kolej Komuniti yang layak.")
            else:
                kk_res = courses_df[courses_df['course_id'].isin(kk_ids)]
                st.dataframe(
                    kk_res[['course', 'department']].rename(columns={'course':'Nama Program', 'department':'Bidang'}), 
                    hide_index=True, 
                    use_container_width=True
                )
                
                # Selection Scoped to KK
                st.markdown("---")
                st.subheader("🔍 Lihat Detail Program Kolej Komuniti")
                sel_kk = st.selectbox("Pilih Program:", kk_res['course'].unique(), key="sel_kk")
                
                if sel_kk:
                    cid = kk_res[kk_res['course'] == sel_kk].iloc[0]['course_id']
                    details = get_course_details(cid, sel_kk)
                    
                    with st.container():
                        st.success(f"### {details['headline']}")
                        st.write(details['synopsis'])
                        
                        if 'pathway' in details: 
                            st.write(f"**🎓 Laluan Sambung Belajar:** {details['pathway']}")
                        
                        st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                    
                    # Locations
                    pids = links_df[links_df['course_id'] == cid]['institution_id']
                    final_loc = inst_df[inst_df['institution_id'].isin(pids)]
                    
                    if not final_loc.empty:
                        st.markdown("**📍 Lokasi:**")
                        st.dataframe(
                            final_loc[['institution_name', 'state', 'url']].rename(columns={'institution_name':'Institusi', 'state':'Negeri', 'url':'Web'}),
                            column_config={"Web": st.column_config.LinkColumn("Web", display_text="Layari")},
                            hide_index=True,
                            use_container_width=True
                        )

    # 4. FAILURE ANALYSIS
    st.markdown("---")
    with st.expander("🕵️ Semak Program Yang Gagal (Analisis)"):
        all_ids = set(courses_df['course_id'].unique())
        rej_ids = list(all_ids - set(e_ids))
        
        if rej_ids:
            rej_courses = courses_df[courses_df['course_id'].isin(rej_ids)].sort_values('course')
            rej_opts = dict(zip(rej_courses['course'], rej_courses['course_id']))
            
            insp_name = st.selectbox("Pilih Program Gagal:", rej_opts.keys())
            
            if insp_name:
                insp_id = rej_opts[insp_name]
                rows = reqs_df[reqs_df['course_id'] == insp_id]
                
                for idx, req in rows.iterrows():
                    st.write(f"**Kriteria Set #{idx+1}:**")
                    reasons = []
                    
                    # Quick Check Logic for Feedback
                    try: min_c = int(float(req.get('min_credits', 0)))
                    except: min_c = 0
                    
                    if calculated_credits < min_c: reasons.append(f"Kredit tidak cukup (Perlu {min_c})")
                    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): reasons.append("Gagal Bahasa Inggeris")
                    if is_active(req.get('pass_math')) and not is_pass(math_grade): reasons.append("Gagal Matematik")
                    if is_active(req.get('credit_math')) and not is_credit(math_grade): reasons.append("Tiada Kepujian Matematik")
                    if is_active(req.get('req_male')) and gender == 'Perempuan': reasons.append("Syarat Jantina (Lelaki Sahaja)")
                    
                    if not reasons:
                        st.warning("Gagal memenuhi syarat subjek khusus (Sains/Teknikal) atau mata kredit lain.")
                    else:
                        for r in reasons: st.error(r)
