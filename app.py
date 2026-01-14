import streamlit as st
import pandas as pd
import os
# Pastikan fail description.py berada dalam folder yang sama
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
        background-color: #71797f;
        border-left: 5px solid #0d47a1;
    }
    .kk-box {
        background-color: #525e75;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def clean_header(text):
    # Membersihkan nama lajur supaya konsisten (huruf kecil, tiada ruang kosong pelik)
    return str(text).strip().replace("\ufeff", "").lower()

# --- LOAD DATA ---
@st.cache_data
def load_data_v19():
    # Helper function to load files specifically from the 'data' folder
    def load_csv(filename):
        # This joins "data" + "filename" safely (e.g. data/courses.csv)
        file_path = os.path.join("data", filename) 
        return pd.read_csv(file_path, encoding="latin1")

    # Membaca fail CSV
    try:
        # We use the helper function now instead of pd.read_csv directly
        courses = load_csv("courses.csv")
        institutions = load_csv("institutions.csv")
        reqs = load_csv("requirements.csv")
        links = load_csv("links.csv")
    except FileNotFoundError as e:
        st.error(f"Fail tidak dijumpai: {e}. Sila pastikan fail csv berada dalam folder 'data/'.")
        st.stop()

    # Bersihkan Header (This part remains exactly the same)
    for df in [courses, institutions, reqs, links]:
        df.columns = [clean_header(c) for c in df.columns]

    # Bersihkan ID untuk matching (This part remains exactly the same)
    for df in [courses, reqs, links]:
        df['course_id'] = df['course_id'].astype(str).str.strip()
    
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    institutions['institution_id'] = institutions['institution_id'].astype(str).str.strip()

    return courses, institutions, reqs, links

courses_df, inst_df, reqs_df, links_df = load_data_v19()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Semakan TVET Malaysia")
st.sidebar.caption("Politeknik & Kolej Komuniti")

with st.sidebar.expander("👤 Maklumat Peribadi", expanded=True):
    nationality = st.radio("Warganegara", ["Warganegara", "Bukan Warganegara"], key="nat")
    gender = st.radio("Jantina", ["Lelaki", "Perempuan"], key="gen")
    
    st.write("**Status Kesihatan**")
    colorblind = st.radio("Buta Warna?", ["Tidak", "Ya"], key="cb")
    # Pautan Ujian Buta Warna (Requirement User)
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

# 1. Create the Student Profile (The "Input")
current_student = StudentProfile(
    grades={
        'bm': bm_grade, 'eng': eng_grade, 'hist': hist_grade, 
        'math': math_grade, 'addmath': addmath_grade,
        'phy': phy_grade, 'chem': chem_grade, 'bio': bio_grade,
        'sci': sci_gen, 'geo': geo_grade, 'acc': acc_grade,
        'biz': biz_grade, 'econ': econ_grade, 'psv': psv_grade,
        'lang': lang_add, 'lit': lit_grade, 'rel': islam_add, 
        'rc': rc_grade, 'cs': cs_grade, 'agro': agro_grade, 'srt': srt_grade
    },
    gender=gender,
    nationality=nationality,
    colorblind=colorblind,
    disability=disability,
    other_tech=other_tech,
    other_voc=other_voc
)

# 2. Display Credit Count (Calculated by the Engine)
st.sidebar.info(f"📊 Jumlah Kredit Dikira: {current_student.credits}")

# 3. Simple Gatekeeper Check (For fast UI feedback only)
def check_gatekeepers():
    if nationality == "Bukan Warganegara": return False, "Warganegara Malaysia Diperlukan."
    
    # Simple check for "Lulus" (Pass) just for the UI warning
    pass_grades = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
    
    if str(bm_grade).strip() not in pass_grades: return False, "Wajib Lulus Bahasa Melayu."
    if str(hist_grade).strip() not in pass_grades: return False, "Wajib Lulus Sejarah."
    return True, "OK"

# --- MAIN BUTTON ---
if st.sidebar.button("Semak Kelayakan", type="primary"):
    passed, msg = check_gatekeepers()
    if not passed:
        st.session_state['eligible_ids'] = []
        st.session_state['fail_reason'] = msg
        st.session_state['checked'] = True
    else:
        e_ids = []
        grouped = reqs_df.groupby('course_id')
        # Convert dataframe to a dictionary list for easier processing
        requirements_list = reqs_df.to_dict('records')
        
        for req in requirements_list:
            # THE BRAIN TRANSPLANT:
            # We ask the Engine: "Is this student eligible for this requirement?"
            is_eligible, reason = check_eligibility(current_student, req)
            
            if is_eligible:
                e_ids.append(req['course_id'])
        
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
        poly_ids = [i for i in e_ids if "POLY" in i]
        kk_ids = [i for i in e_ids if "POLY" not in i] 

        st.markdown("### 🎉 Tahniah! Anda Layak.")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Politeknik (Diploma)", f"{len(poly_ids)} Program")
        m2.metric("Kolej Komuniti (Sijil/Dip)", f"{len(kk_ids)} Program")
        m3.metric("Jumlah Kredit", f"{current_student.credits}")

        # --- TABS UI ---
        tab1, tab2 = st.tabs(["🏛️ POLITEKNIK", "🛠️ KOLEJ KOMUNITI"])

        # HELPER FOR TABLE DISPLAY
        def display_courses_table(ids):
            if not ids:
                st.info("Tiada program yang layak.")
                return None
            
            res = courses_df[courses_df['course_id'].isin(ids)]
            
            # Konfigurasi Lajur (Mapping)
            cols_to_show = ['course', 'department']
            rename_map = {'course': 'Nama Program', 'department': 'Jabatan/Bidang'}
            
            # Cek jika lajur baru wujud (semesters & hyperlink)
            if 'semesters' in res.columns:
                cols_to_show.append('semesters')
                rename_map['semesters'] = 'Tempoh'
            
            if 'hyperlink' in res.columns:
                cols_to_show.append('hyperlink')
                rename_map['hyperlink'] = 'Web'

            final_df = res[cols_to_show].rename(columns=rename_map)
            
            st.dataframe(
                final_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Web": st.column_config.LinkColumn(
                        "Info Lanjut",
                        display_text="Layari 🔗"
                    ),
                    "Tempoh": st.column_config.TextColumn(
                        "Tempoh",
                        help="Bilangan semester pengajian"
                    )
                }
            )
            return res

        # === TAB 1: POLITEKNIK ===
        with tab1:
            # BLURB PENGENALAN POLITEKNIK
            st.markdown("""
            <div class="info-box poly-box">
                <h4>🏛️ Apa itu Politeknik?</h4>
                <p>
                    Politeknik adalah institusi kerajaan yang menawarkan pendidikan <b>Teknikal & Vokasional (TVET)</b> bertaraf dunia. 
                    Fokus kepada latihan amali (hands-on) dalam bidang Kejuruteraan, Perdagangan, Teknologi Maklumat, dan Perkhidmatan.
                </p>
                <ul>
                    <li><b>Sesuai untuk:</b> Pelajar yang mahu kemahiran teknikal & peluang kerja cerah.</li>
                    <li><b>Peringkat:</b> Diploma & Ijazah Sarjana Muda.</li>
                    <li><b>Yuran:</b> Sangat berpatutan & disokong kerajaan.</li>
                    <li><b>Laluan:</b> Terus bekerja atau sambung Ijazah di Universiti.</li>
                </ul>
                <p>👉 <a href="https://ambilan.mypolycc.edu.my/portalbpp2/index.asp" target="_blank">Laman Web Rasmi Pengambilan</a></p>
            </div>
            """, unsafe_allow_html=True)

            poly_res = display_courses_table(poly_ids)
            
            if poly_res is not None:
                st.markdown("---")
                st.subheader("🔍 Lihat Detail Program Politeknik")
                sel_poly = st.selectbox("Pilih Program:", poly_res['course'].unique(), key="sel_poly")
                
                if sel_poly:
                    cid = poly_res[poly_res['course'] == sel_poly].iloc[0]['course_id']
                    details = get_course_details(cid, sel_poly)
                    
                    with st.container():
                        st.info(f"### {details['headline']}")
                        st.write(details['synopsis'])
                        if 'pathway' in details: st.write(f"**🎓 Laluan Sambung Belajar:** {details['pathway']}")
                        st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                        
                        rows = reqs_df[reqs_df['course_id'] == cid]
                        if rows['req_interview'].apply(is_active).any():
                            st.warning("🗣️ Temuduga Diperlukan.")
                    
                    pids = links_df[links_df['course_id'] == cid]['institution_id']
                    final_loc = inst_df[inst_df['institution_id'].isin(pids)]
                    if not final_loc.empty:
                        st.markdown("**📍 Lokasi:**")
                        st.dataframe(
                            final_loc[['institution_name', 'state', 'url']].rename(columns={'institution_name':'Institusi', 'state':'Negeri', 'url':'Web'}),
                            column_config={"Web": st.column_config.LinkColumn("Web", display_text="Layari")},
                            hide_index=True, use_container_width=True
                        )

        # === TAB 2: KOLEJ KOMUNITI ===
        with tab2:
            # BLURB PENGENALAN KOLEJ KOMUNITI
            st.markdown("""
            <div class="info-box kk-box">
                <h4>🛠️ Apa itu Kolej Komuniti?</h4>
                <p>
                    Institusi TVET "Mesra Komuniti" yang menawarkan latihan kemahiran praktikal untuk membolehkan anda terus bekerja atau berniaga.
                    Terdapat lebih 100 buah kolej di seluruh Malaysia!
                </p>
                <ul>
                    <li><b>Sesuai untuk:</b> Anda yang minat 'buat kerja' (hands-on) berbanding teori buku.</li>
                    <li><b>Syarat Masuk:</b> Mudah! Lulus SPM (BM & Sejarah) sahaja.</li>
                    <li><b>Bidang Popular:</b> Automotif, Masakan (Kulinari), Elektrik, Fesyen, Kecantikan.</li>
                    <li><b>Laluan:</b> Tamat Sijil boleh terus kerja atau sambung Diploma di Politeknik.</li>
                </ul>
                <p>👉 <a href="https://ambilan.mypolycc.edu.my/portalbpp2/index.asp" target="_blank">Laman Web Rasmi Pengambilan</a></p>
            </div>
            """, unsafe_allow_html=True)

            kk_res = display_courses_table(kk_ids)
            
            if kk_res is not None:
                st.markdown("---")
                st.subheader("🔍 Lihat Detail Program Kolej Komuniti")
                sel_kk = st.selectbox("Pilih Program:", kk_res['course'].unique(), key="sel_kk")
                
                if sel_kk:
                    cid = kk_res[kk_res['course'] == sel_kk].iloc[0]['course_id']
                    details = get_course_details(cid, sel_kk)
                    
                    with st.container():
                        st.success(f"### {details['headline']}")
                        st.write(details['synopsis'])
                        if 'pathway' in details: st.write(f"**🎓 Laluan Sambung Belajar:** {details['pathway']}")
                        st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                    
                    pids = links_df[links_df['course_id'] == cid]['institution_id']
                    final_loc = inst_df[inst_df['institution_id'].isin(pids)]
                    if not final_loc.empty:
                        st.markdown("**📍 Lokasi:**")
                        st.dataframe(
                            final_loc[['institution_name', 'state', 'url']].rename(columns={'institution_name':'Institusi', 'state':'Negeri', 'url':'Web'}),
                            column_config={"Web": st.column_config.LinkColumn("Web", display_text="Layari")},
                            hide_index=True, use_container_width=True
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
                    try: min_c = int(float(req.get('min_credits', 0)))
                    except: min_c = 0
                    if calculated_credits < min_c: reasons.append(f"Kredit tidak cukup (Perlu {min_c})")
                    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): reasons.append("Gagal Bahasa Inggeris")
                    if is_active(req.get('pass_math')) and not is_pass(math_grade): reasons.append("Gagal Matematik")
                    if is_active(req.get('req_male')) and gender == 'Perempuan': reasons.append("Syarat Jantina (Lelaki Sahaja)")
                    
                    if not reasons: st.warning("Gagal memenuhi syarat subjek khusus (Sains/Teknikal) atau mata kredit lain.")
                    else:
                        for r in reasons: st.error(r)
