import streamlit as st
import pandas as pd
import os
from src.description import get_course_details
from src.engine import StudentProfile, check_eligibility

# --- PAGE SETUP ---
st.set_page_config(page_title="Semakan TVET (Politeknik & Komuniti)", page_icon="🇲🇾", layout="wide")

# --- CUSTOM CSS FOR METRICS & TABS ---
st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #004E98;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .info-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .poly-box {
        background-color: #e3f2fd;
        border-left: 5px solid #0d47a1;
        color: #0d47a1;
    }
    .kk-box {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def clean_header(text):
    # Membersihkan nama lajur supaya konsisten (huruf kecil, tiada ruang kosong pelik)
    return str(text).strip().replace("\ufeff", "").lower()

# --- LOAD DATA ---
@st.cache_data
def load_data_v20():
    # Helper: Safe Loading (Fixes Risk 1)
    def load_csv(filename):
        file_path = os.path.join("data", filename) 
        try:
            return pd.read_csv(file_path, encoding="latin1")
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding="utf-8")
        except FileNotFoundError:
            st.error(f"❌ Fail hilang: {filename}. Pastikan fail wujud dalam folder 'data/'.")
            st.stop()

    # Load Files
    courses = load_csv("courses.csv")
    institutions = load_csv("institutions.csv")
    reqs = load_csv("requirements.csv")
    links = load_csv("links.csv")
    
    tvet_courses = load_csv("tvet_courses.csv")
    tvet_inst = load_csv("tvet_institutions.csv")
    tvet_reqs = load_csv("tvet_requirements.csv")

    # 1. Clean Headers
    all_dfs = [courses, institutions, reqs, links, tvet_courses, tvet_inst, tvet_reqs]
    for df in all_dfs:
        df.columns = [clean_header(c) for c in df.columns]

    # 2. SCHEMA CHECK (Fixes Risk 2)
    schema_checks = {
        "courses.csv": (courses, ['course_id', 'course']),
        "reqs.csv": (reqs, ['course_id']),
        "institutions.csv": (institutions, ['institution_id']),
        "links.csv": (links, ['course_id', 'institution_id']),
        "tvet_courses.csv": (tvet_courses, ['course_id', 'course']),
        "tvet_reqs.csv": (tvet_reqs, ['course_id', 'institution_id']),
        "tvet_inst.csv": (tvet_inst, ['institution_id'])
    }

    for filename, (df, required_cols) in schema_checks.items():
        missing = set(required_cols) - set(df.columns)
        if missing:
            st.error(f"🛑 Struktur fail '{filename}' salah. Lajur hilang: {missing}")
            st.stop()

    # 3. Clean IDs
    for df in [courses, reqs, links, tvet_courses, tvet_reqs]:
        df['course_id'] = df['course_id'].astype(str).str.strip()
        
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    institutions['institution_id'] = institutions['institution_id'].astype(str).str.strip()
    tvet_inst['institution_id'] = tvet_inst['institution_id'].astype(str).str.strip()
    tvet_reqs['institution_id'] = tvet_reqs['institution_id'].astype(str).str.strip()

    # 4. PRE-CONVERT TO DICTIONARIES (Fixes Risk 3)
    poly_dicts = reqs.to_dict('records')
    tvet_dicts = tvet_reqs.to_dict('records')

    return courses, institutions, reqs, links, tvet_courses, tvet_inst, tvet_reqs, poly_dicts, tvet_dicts

# Unpack all 9 return values
courses_df, inst_df, reqs_df, links_df, t_courses, t_inst, t_reqs, poly_req_list, tvet_req_list = load_data_v20()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Semakan TVET Malaysia")
st.sidebar.caption("Politeknik & Kolej Komuniti")

with st.sidebar.expander("👤 Maklumat Peribadi", expanded=True):
    nationality = st.radio("Warganegara", ["Warganegara", "Bukan Warganegara"], key="nat")
    gender = st.radio("Jantina", ["Lelaki", "Perempuan"], key="gen")
    
    st.write("**Status Kesihatan**")
    colorblind = st.radio("Buta Warna?", ["Tidak", "Ya"], key="cb")
    st.caption("Tidak pasti? [Uji di sini (Percuma)](https://enchroma.com/pages/color-blind-test)")
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

# 1. Create Student Profile
current_student = StudentProfile(
    grades={
        'bm': bm_grade, 'eng': eng_grade, 'hist': hist_grade, 
        'math': math_grade, 'addmath': addmath_grade,
        'phy': phy_grade, 'chem': chem_grade, 'bio': bio_grade,
        'sci': sci_gen, 'geo': geo_grade, 'acc': acc_grade,
        'biz': biz_grade, 'econ': econ_grade, 'psv': psv_grade,
        'lang': lang_add, 'lit': lit_grade, 'rel': islam_moral,
        'rel_add': islam_add, 'rc': rc_grade, 'cs': cs_grade,
        'agro': agro_grade, 'srt': srt_grade
    },
    gender=gender,
    nationality=nationality,
    colorblind=colorblind,
    disability=disability,
    other_tech=other_tech,
    other_voc=other_voc
)

st.sidebar.info(f"📊 Jumlah Kredit Dikira: {current_student.credits}")

# 2. Gatekeeper Check
def check_gatekeepers():
    if nationality == "Bukan Warganegara": 
        return False, "Maaf, permohonan hanya terbuka kepada Warganegara Malaysia."
    return True, "OK"

# --- MAIN BUTTON ---
if st.sidebar.button("Semak Kelayakan", type="primary"):
    passed, msg = check_gatekeepers()
    if not passed:
        st.session_state['eligible_ids'] = []
        st.session_state['tvet_eligible_ids'] = []
        st.session_state['fail_reason'] = msg
        st.session_state['checked'] = True
    else:
        # 1. Check Polytechnic
        poly_ids = []
        for req in poly_req_list:
            is_eligible, reason = check_eligibility(current_student, req)
            if is_eligible:
                poly_ids.append(req['course_id'])
        
        # 2. Check TVET
        tvet_ids = []
        for req in tvet_req_list:
            is_eligible, reason = check_eligibility(current_student, req)
            if is_eligible:
                tvet_ids.append(req['course_id'])
        
        st.session_state['eligible_ids'] = poly_ids
        st.session_state['tvet_eligible_ids'] = tvet_ids
        st.session_state['fail_reason'] = None
        st.session_state['checked'] = True

# --- RESULT DISPLAY ---
if st.session_state.get('checked'):
    poly_ids = st.session_state.get('eligible_ids', [])
    tvet_ids = st.session_state.get('tvet_eligible_ids', [])
    fail_reason = st.session_state.get('fail_reason')

    if fail_reason:
        st.error(f"❌ Tidak Layak: {fail_reason}")
    elif not poly_ids and not tvet_ids:
        st.warning(f"Tiada program layak. Kredit: {current_student.credits}")
    else:
        # Categorize Poly IDs
        p_poly = [i for i in poly_ids if "POLY" in i]
        p_kk = [i for i in poly_ids if "POLY" not in i] 
        
        # Display Metrics
        st.markdown("### 🎉 Tahniah! Anda Layak.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Politeknik", f"{len(p_poly)}")
        m2.metric("Kolej Komuniti", f"{len(p_kk)}")
        m3.metric("ILKBS / ILJTM", f"{len(set(tvet_ids))}") 
        m4.metric("Jumlah Kredit", f"{current_student.credits}")

        # --- TABS ---
        tab1, tab2, tab3 = st.tabs(["🏛️ POLITEKNIK", "🛠️ KOLEJ KOMUNITI", "⚙️ ILKBS & ADTEC"])

        # === TAB 1: POLITEKNIK ===
        with tab1:
            st.markdown("""
            <div class="info-box poly-box">
                <h4>🏛️ Politeknik Malaysia</h4>
                <p>Institusi TVET premier yang menawarkan program Diploma & Ijazah.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not p_poly:
                st.info("Tiada program Politeknik yang layak.")
            else:
                # Filter courses for Tab 1
                res_poly = courses_df[courses_df['course_id'].isin(p_poly)]
                if res_poly.empty:
                    st.warning("Data kursus tidak dijumpai.")
                else:
                    disp_poly = res_poly[['course']].rename(columns={'course': 'Nama Program'})
                    st.dataframe(disp_poly, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("🔍 Lihat Detail Program Politeknik")
                    sel_poly = st.selectbox("Pilih Program:", res_poly['course'].unique(), key="sel_poly")
                    
                    if sel_poly:
                        cid = res_poly[res_poly['course'] == sel_poly].iloc[0]['course_id']
                        details = get_course_details(cid, sel_poly)
                        
                        with st.container():
                            st.info(f"### {details['headline']}")
                            st.write(details['synopsis'])
                            st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                            
                            # Locations for Poly
                            loc_ids = links_df[links_df['course_id'] == cid]['institution_id'].unique()
                            final_locs = inst_df[inst_df['institution_id'].isin(loc_ids)]
                            
                            if not final_locs.empty:
                                st.markdown("**📍 Lokasi Institusi:**")
                                st.dataframe(
                                    final_locs[['institution_name', 'state']].rename(columns={'institution_name':'Institusi', 'state':'Negeri'}),
                                    hide_index=True,
                                    use_container_width=True
                                )

        # === TAB 2: KOLEJ KOMUNITI ===
        with tab2:
            st.markdown("""
            <div class="info-box kk-box">
                <h4>🛠️ Kolej Komuniti</h4>
                <p>Fokus kepada kemahiran teknikal spesifik dan pembelajaran sepanjang hayat.</p>
            </div>
            """, unsafe_allow_html=True)

            if not p_kk:
                st.info("Tiada program Kolej Komuniti yang layak.")
            else:
                # Filter courses for Tab 2
                res_kk = courses_df[courses_df['course_id'].isin(p_kk)]
                if res_kk.empty:
                    st.warning("Data kursus tidak dijumpai.")
                else:
                    disp_kk = res_kk[['course']].rename(columns={'course': 'Nama Program'})
                    st.dataframe(disp_kk, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("🔍 Lihat Detail Program Kolej Komuniti")
                    sel_kk = st.selectbox("Pilih Program:", res_kk['course'].unique(), key="sel_kk")
                    
                    if sel_kk:
                        cid = res_kk[res_kk['course'] == sel_kk].iloc[0]['course_id']
                        details = get_course_details(cid, sel_kk)
                        
                        with st.container():
                            st.info(f"### {details['headline']}")
                            st.write(details['synopsis'])
                            st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                            
                            # Locations for KK
                            loc_ids = links_df[links_df['course_id'] == cid]['institution_id'].unique()
                            final_locs = inst_df[inst_df['institution_id'].isin(loc_ids)]
                            
                            if not final_locs.empty:
                                st.markdown("**📍 Lokasi Institusi:**")
                                st.dataframe(
                                    final_locs[['institution_name', 'state']].rename(columns={'institution_name':'Institusi', 'state':'Negeri'}),
                                    hide_index=True,
                                    use_container_width=True
                                )

        # === TAB 3: TVET (New) ===
        with tab3:
            st.markdown("""
            <div class="info-box" style="background-color: #e3f2fd; border-left: 5px solid #2196f3;">
                <h4>⚙️ Institut Latihan Kemahiran (ILKBS & ILJTM)</h4>
                <p>Termasuk IKBN, IKTBN, ADTEC, dan JMTI. Fokus kepada kemahiran industri berat, minyak & gas, dan automotif.</p>
                <ul>
                    <li><b>Elaun Bulanan:</b> Disediakan (RM100 - RM300 bergantung kursus).</li>
                    <li><b>Kemudahan:</b> Asrama & Makan Minum percuma (untuk kebanyakan institut).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            if not tvet_ids:
                st.info("Tiada program TVET yang layak.")
            else:
                unique_tvet_ids = list(set(tvet_ids))
                res_tvet = t_courses[t_courses['course_id'].isin(unique_tvet_ids)]
                
                if res_tvet.empty:
                    st.warning("Data kursus tidak dijumpai.")
                else:
                    disp_tvet = res_tvet[['course', 'department', 'level']].rename(columns={
                        'course': 'Nama Program', 
                        'department': 'Bidang',
                        'level': 'Tahap'
                    })
                    
                    st.dataframe(disp_tvet, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("🔍 Lihat Detail Program TVET")
                    sel_tvet = st.selectbox("Pilih Program:", res_tvet['course'].unique(), key="sel_tvet")
                    
                    if sel_tvet:
                        cid = res_tvet[res_tvet['course'] == sel_tvet].iloc[0]['course_id']
                        details = get_course_details(cid, sel_tvet) 
                        
                        with st.container():
                            st.info(f"### {details['headline']}")
                            st.write(details['synopsis'])
                            st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                            
                            loc_rows = t_reqs[t_reqs['course_id'] == cid]
                            loc_ids = loc_rows['institution_id'].unique()
                            
                            final_locs = t_inst[t_inst['institution_id'].isin(loc_ids)]
                            
                            if not final_locs.empty:
                                st.markdown("**📍 Lokasi Institusi:**")
                                st.dataframe(
                                    final_locs[['institution_name', 'state']].rename(columns={'institution_name':'Institusi', 'state':'Negeri'}),
                                    hide_index=True,
                                    use_container_width=True
                                )
                                
                                row1 = loc_rows.iloc[0]
                                m_allow = row1.get('monthly_allowance', 'Tiada')
                                hostel = "Disediakan" if str(row1.get('free_hostel')).strip() == '1' else "Tiada"
                                st.success(f"💰 **Elaun:** {m_allow} | 🏠 **Asrama:** {hostel}")

    # 4. FAILURE ANALYSIS
    st.markdown("---")
    with st.expander("🕵️ Semak Program Yang Gagal (Analisis)"):
        eligible_poly = set(st.session_state.get('eligible_ids', []))
        eligible_tvet = set(st.session_state.get('tvet_eligible_ids', []))
        
        all_eligible = eligible_poly.union(eligible_tvet)

        all_poly_courses = set(courses_df['course_id'].unique())
        all_tvet_courses = set(t_courses['course_id'].unique())
        all_courses = all_poly_courses.union(all_tvet_courses)

        rej_ids = list(all_courses - all_eligible)
        
        if rej_ids:
            rej_courses = courses_df[courses_df['course_id'].isin(rej_ids)].sort_values('course')
            rej_opts = dict(zip(rej_courses['course'], rej_courses['course_id']))
            
            insp_name = st.selectbox("Pilih Program Gagal:", list(rej_opts.keys()))
            
            if insp_name:
                insp_id = rej_opts[insp_name]
                rows = reqs_df[reqs_df['course_id'] == insp_id]
                
                for idx, req in rows.iterrows():
                    st.write(f"**Kriteria Set #{idx+1}:**")
                    req_dict = req.to_dict()
                    is_eligible, reason = check_eligibility(current_student, req_dict)
                    
                    if not is_eligible:
                        st.error(f"❌ {reason}")
                    else:
                        st.success("✅ Set kriteria ini LULUS.")
        else:
            st.success("Tahniah! Tiada program yang gagal. Anda layak untuk semua!")
