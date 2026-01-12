import streamlit as st
import pandas as pd
from description import get_course_details

# --- PAGE SETUP ---
st.set_page_config(page_title="Semakan TVET (Politeknik & Komuniti)", page_icon="🇲🇾", layout="wide")

# --- HELPER: ROBUST STRING CLEANING ---
def clean_header(text):
    return str(text).strip().replace("\ufeff", "").lower()

def is_active(value):
    s = str(value).strip().lower()
    return s in ['1', '1.0', 'true', 'yes', 'y']

# --- GRADE LOGIC ---
PASS_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
CREDIT_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_pass(g): return str(g).strip() in PASS_GRADES
def is_credit(g): return str(g).strip() in CREDIT_GRADES

# --- LOAD DATA ---
@st.cache_data
def load_data_v16():
    courses = pd.read_csv("courses.csv", encoding="latin1")
    institutions = pd.read_csv("institutions.csv", encoding="latin1")
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1")

    # Clean Headers & Content
    courses.columns = [clean_header(c) for c in courses.columns]
    institutions.columns = [clean_header(c) for c in institutions.columns]
    reqs.columns = [clean_header(c) for c in reqs.columns]
    links.columns = [clean_header(c) for c in links.columns]

    reqs['course_id'] = reqs['course_id'].astype(str).str.strip()
    courses['course_id'] = courses['course_id'].astype(str).str.strip()
    links['course_id'] = links['course_id'].astype(str).str.strip()
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    institutions['institution_id'] = institutions['institution_id'].astype(str).str.strip()

    return courses, institutions, reqs, links

try:
    courses_df, inst_df, reqs_df, links_df = load_data_v16()
except Exception as e:
    st.error(f"Ralat pangkalan data: {e}")
    st.stop()

# --- SIDEBAR INPUTS (BM TRANSLATED) ---
st.sidebar.header("Semakan TVET Malaysia")
st.sidebar.caption("Politeknik & Kolej Komuniti")

# 1. Demographics
with st.sidebar.expander("👤 Maklumat Peribadi", expanded=True):
    nationality = st.radio("Warganegara", ["Warganegara", "Bukan Warganegara"], key="nat_input")
    gender = st.radio("Jantina", ["Lelaki", "Perempuan"], key="gen_input")
    
    st.write("**Status Kesihatan**")
    colorblind = st.radio("Buta Warna?", ["Tidak", "Ya"], key="cb_input")
    st.caption("Tidak pasti? [Uji di sini (Percuma)](https://enchroma.com/pages/color-blind-test)")
    
    disability = st.radio("Kecacatan Fizikal?", ["Tidak", "Ya"], key="dis_input")

# 2. Subjects
grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G", "Tidak Ambil"]

with st.sidebar.expander("📚 Subjek Teras (SPM)", expanded=True):
    bm_grade = st.selectbox("Bahasa Melayu", grade_opts, index=5, key="bm_input")
    eng_grade = st.selectbox("Bahasa Inggeris", grade_opts, index=6, key="bi_input")
    hist_grade = st.selectbox("Sejarah", grade_opts, index=6, key="hist_input")
    math_grade = st.selectbox("Matematik", grade_opts, index=5, key="math_input")
    islam_moral = st.selectbox("P. Islam / P. Moral", grade_opts, index=5, key="rel_input")

with st.sidebar.expander("🧪 Aliran Sains"):
    addmath_grade = st.selectbox("Matematik Tambahan", grade_opts, index=10, key="am_input")
    phy_grade = st.selectbox("Fizik", grade_opts, index=10, key="phy_input")
    chem_grade = st.selectbox("Kimia", grade_opts, index=10, key="chem_input")
    bio_grade = st.selectbox("Biologi", grade_opts, index=10, key="bio_input")

with st.sidebar.expander("🎨 Sastera & Kemanusiaan"):
    science_gen_grade = st.selectbox("Sains (Umum)", grade_opts, index=10, key="sci_input")
    geo_grade = st.selectbox("Geografi", grade_opts, index=10, key="geo_input")
    acc_grade = st.selectbox("Prinsip Perakaunan", grade_opts, index=10, key="acc_input")
    biz_grade = st.selectbox("Perniagaan", grade_opts, index=10, key="biz_input")
    econ_grade = st.selectbox("Ekonomi", grade_opts, index=10, key="econ_input")
    psv_grade = st.selectbox("Pendidikan Seni Visual", grade_opts, index=10, key="psv_input")

with st.sidebar.expander("🕌 Bahasa & Elektif Lain"):
    lang_add_grade = st.selectbox("B. Arab / Cina / Tamil / Punjabi", grade_opts, index=10, key="lang_input")
    lit_grade = st.selectbox("Kesusasteraan (Melayu/Inggeris/Cina/Tamil)", grade_opts, index=10, key="lit_input")
    islam_add_grade = st.selectbox("P. Al-Quran / As-Sunnah / Syariah", grade_opts, index=10, key="rel_add_input")

with st.sidebar.expander("🛠️ Elektif Teknikal & Vokasional"):
    rekacipta_grade = st.selectbox("Reka Cipta", grade_opts, index=10, key="rc_input")
    cs_grade = st.selectbox("Sains Komputer", grade_opts, index=10, key="cs_input")
    pertanian_grade = st.selectbox("Pertanian", grade_opts, index=10, key="agro_input")
    srt_grade = st.selectbox("Sains Rumah Tangga", grade_opts, index=10, key="srt_input")
    
    st.caption("Lain-lain")
    other_tech_grade = st.checkbox("Kepujian (C ke atas) subjek Teknikal Lain", key="tech_check")
    other_voc_grade = st.checkbox("Kepujian (C ke atas) subjek Vokasional Lain", key="voc_check")

# --- AUTO-CALCULATE DERIVED STATS ---
all_subjects = [
    bm_grade, eng_grade, hist_grade, math_grade, islam_moral,
    addmath_grade, phy_grade, chem_grade, bio_grade,
    science_gen_grade, geo_grade, acc_grade, biz_grade, econ_grade, psv_grade,
    lang_add_grade, lit_grade, islam_add_grade,
    rekacipta_grade, cs_grade, pertanian_grade, srt_grade
]

calculated_credits = 0
for g in all_subjects:
    if is_credit(g):
        calculated_credits += 1
if other_tech_grade: calculated_credits += 1
if other_voc_grade: calculated_credits += 1

st.sidebar.info(f"📊 Jumlah Kredit Dikira: {calculated_credits}")

# --- LOGIC ENGINE ---
def check_gatekeepers():
    if nationality == "Bukan Warganegara": return False, "Warganegara Malaysia Diperlukan."
    if not is_pass(bm_grade): return False, "Wajib Lulus Bahasa Melayu."
    if not is_pass(hist_grade): return False, "Wajib Lulus Sejarah."
    return True, "OK"

def check_row_constraints(req):
    # Gender & Medical
    if is_active(req.get('req_male')) and gender == "Perempuan": return False
    if is_active(req.get('no_colorblind')) and colorblind == "Ya": return False
    if is_active(req.get('no_disability')) and disability == "Ya": return False

    # English & Math (Pass)
    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): return False
    if is_active(req.get('pass_math')) and not is_pass(math_grade): return False

    # Credits (Kepujian)
    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): return False
    if is_active(req.get('credit_math')) and not is_credit(math_grade): return False
    if is_active(req.get('credit_eng')) and not is_credit(eng_grade): return False
    
    if is_active(req.get('credit_bmbi')) and not (is_credit(bm_grade) or is_credit(eng_grade)): return False

    # Groups
    has_pure_science_pass = any(is_pass(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
    has_pure_science_credit = any(is_credit(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
    has_tech_pass = any(is_pass(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade
    has_tech_credit = any(is_credit(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade
    has_voc_pass = any(is_pass(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade
    has_voc_credit = any(is_credit(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade
    sci_broad_pass = is_pass(science_gen_grade) or has_pure_science_pass
    sci_broad_credit = is_credit(science_gen_grade) or has_pure_science_credit
    stv_pass = sci_broad_pass or has_tech_pass or has_voc_pass
    stv_credit = sci_broad_credit or has_tech_credit or has_voc_credit

    if is_active(req.get('pass_stv')) and not stv_pass: return False
    if is_active(req.get('credit_stv')) and not stv_credit: return False

    if is_active(req.get('credit_sf')):
        if not (is_credit(science_gen_grade) or is_credit(phy_grade)): return False
    
    if is_active(req.get('credit_sfmt')):
        if not (is_credit(science_gen_grade) or is_credit(phy_grade) or is_credit(addmath_grade)): return False

    try:
        min_c = int(float(req.get('min_credits', 0)))
    except:
        min_c = 0
    
    if calculated_credits < min_c: return False

    return True

# --- MAIN FLOW ---
if st.sidebar.button("Semak Kelayakan", key="check_btn", type="primary"):
    
    passed_gates, gate_msg = check_gatekeepers()
    
    if not passed_gates:
        st.session_state['eligible_ids'] = []
        st.session_state['fail_reason'] = gate_msg
        st.session_state['has_checked'] = True
    else:
        eligible_ids = []
        grouped = reqs_df.groupby('course_id')
        
        for cid, group in grouped:
            if group.apply(check_row_constraints, axis=1).all():
                eligible_ids.append(cid)
        
        st.session_state['eligible_ids'] = eligible_ids
        st.session_state['fail_reason'] = None
        st.session_state['has_checked'] = True

# --- DISPLAY RESULTS ---
if st.session_state.get('has_checked', False):
    
    eligible_ids = st.session_state['eligible_ids']
    fail_reason = st.session_state.get('fail_reason')
    
    if fail_reason:
        st.error(f"❌ Tidak Layak. Sebab: {fail_reason}")
    elif not eligible_ids:
        st.warning(f"Tiada program yang layak berdasarkan keputusan ini. Jumlah Kredit: {calculated_credits}")
    else:
        st.success(f"🎉 Tahniah! Anda layak memohon **{len(eligible_ids)}** program.")
        
        # 1. LIST OF COURSES
        st.markdown("### 📜 Senarai Program Yang Layak")
        res = courses_df[courses_df['course_id'].isin(eligible_ids)]
        
        display_df = res[['course', 'department']].copy()
        display_df.columns = ["Nama Program", "Jabatan"]
        
        st.dataframe(
            display_df, 
            hide_index=True, 
            use_container_width=True
        )

        st.markdown("---")
        
        # 2. DETAILS & LOCATIONS
        st.markdown("### 🔍 Maklumat Lanjut & Lokasi")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            sel = st.selectbox("Pilih Program:", res['course'].unique(), key="location_select")
        
        if sel:
            cid = res[res['course'] == sel].iloc[0]['course_id']
            
            # A. DESCRIPTION CARD
            details = get_course_details(cid, sel)
            
            with st.container():
                st.info(f"### {details['headline']}")
                st.write(details['synopsis'])
                
                # --- CONDITIONAL DISPLAY FOR PATHWAY (New!) ---
                # Only show if 'pathway' key exists (Kolej Komuniti)
                if 'pathway' in details:
                    st.write(f"**🎓 Laluan Sambung Belajar:** {details['pathway']}")
                
                st.write(f"**💼 Prospek Kerjaya:** {', '.join(details['jobs'])}")
                
                # Interview Alert
                rows_for_course = reqs_df[reqs_df['course_id'] == cid]
                if rows_for_course['req_interview'].apply(is_active).any():
                    st.warning("🗣️ **Temuduga Diperlukan:** Anda perlu lulus temuduga atau menghantar portfolio.")

            # B. LOCATION TABLE
            st.markdown("#### 📍 Ditawarkan di:")
            pids = links_df[links_df['course_id'] == cid]['institution_id']
            final = inst_df[inst_df['institution_id'].isin(pids)]
            
            if not final.empty:
                loc_display = final[['institution_name', 'state', 'url']].copy()
                loc_display.columns = ["Nama Institusi", "Negeri", "Laman Web"]
                
                st.dataframe(
                    loc_display,
                    column_config={
                        "Laman Web": st.column_config.LinkColumn(
                            "Laman Web",
                            display_text="Layari"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Tiada data lokasi khusus.")

    # 3. FAILURE ANALYSIS
    st.markdown("---")
    st.header("🕵️ Mengapa Saya Gagal?")
    st.write("Semak program yang anda tidak layak untuk mengetahui sebabnya.")

    all_course_ids = set(courses_df['course_id'].unique())
    eligible_set = set(eligible_ids)
    rejected_ids = list(all_course_ids - eligible_set)
    
    if rejected_ids:
        rejected_courses = courses_df[courses_df['course_id'].isin(rejected_ids)]
        rejected_courses = rejected_courses.sort_values('course')
        course_options = dict(zip(rejected_courses['course'], rejected_courses['course_id']))
        
        inspect_name = st.selectbox(
            "Pilih Program Gagal", 
            options=course_options.keys(), 
            key="inspect_select", 
            label_visibility="collapsed",
            index=None,
            placeholder="Pilih program..."
        )
        
        if inspect_name:
            inspect_id = course_options[inspect_name]
            st.markdown(f"### 🧐 Analisis: {inspect_name}")
            
            gate_pass, gate_msg = check_gatekeepers()
            if not gate_pass:
                st.error(f"❌ GAGAL: {gate_msg}")
            else:
                st.success("✅ Syarat Umum (Warganegara, BM, Sejarah) Lulus")

                rows = reqs_df[reqs_df['course_id'] == inspect_id]
                
                count = 1
                for index, req in rows.iterrows():
                    st.markdown(f"**Set Kriteria #{count}:**")
                    reasons = []

                    if is_active(req.get('req_male')) and gender == "Perempuan": reasons.append("Hanya untuk Lelaki.")
                    if is_active(req.get('no_colorblind')) and colorblind == "Ya": reasons.append("Tidak boleh Buta Warna.")
                    if is_active(req.get('no_disability')) and disability == "Ya": reasons.append("Tidak sesuai untuk OKU Fizikal.")

                    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): reasons.append("Wajib Lulus Bahasa Inggeris.")
                    if is_active(req.get('pass_math')) and not is_pass(math_grade): reasons.append("Wajib Lulus Matematik.")
                    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): reasons.append("Wajib Kepujian (C) BM.")
                    if is_active(req.get('credit_math')) and not is_credit(math_grade): reasons.append("Wajib Kepujian (C) Matematik.")
                    if is_active(req.get('credit_eng')) and not is_credit(eng_grade): reasons.append("Wajib Kepujian (C) Bahasa Inggeris.")
                    
                    if is_active(req.get('credit_bmbi')):
                         if not (is_credit(bm_grade) or is_credit(eng_grade)):
                             reasons.append("Wajib Kepujian (C) sama ada BM atau BI.")

                    # Re-calc pools for local debug
                    has_pure_science_pass = any(is_pass(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
                    has_pure_science_credit = any(is_credit(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
                    has_tech_pass = any(is_pass(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade
                    has_tech_credit = any(is_credit(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade
                    has_voc_pass = any(is_pass(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade
                    has_voc_credit = any(is_credit(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade
                    sci_broad_pass = is_pass(science_gen_grade) or has_pure_science_pass
                    sci_broad_credit = is_credit(science_gen_grade) or has_pure_science_credit
                    stv_pass = sci_broad_pass or has_tech_pass or has_voc_pass
                    stv_credit = sci_broad_credit or has_tech_credit or has_voc_credit

                    if is_active(req.get('pass_stv')) and not stv_pass: reasons.append("Wajib Lulus mana-mana subjek Sains/Teknikal/Vokasional.")
                    if is_active(req.get('credit_stv')) and not stv_credit: reasons.append("Wajib Kepujian (C) mana-mana subjek Sains/Teknikal/Vokasional.")
                    
                    if is_active(req.get('credit_sf')):
                        if not (is_credit(science_gen_grade) or is_credit(phy_grade)): 
                            reasons.append("Wajib Kepujian (C) Sains Teras ATAU Fizik.")

                    if is_active(req.get('credit_sfmt')):
                        if not (is_credit(science_gen_grade) or is_credit(phy_grade) or is_credit(addmath_grade)):
                            reasons.append("Wajib Kepujian (C) Sains Teras ATAU Fizik ATAU Matematik Tambahan.")

                    try:
                        min_c = int(float(req.get('min_credits', 0)))
                    except:
                        min_c = 0
                    
                    if calculated_credits < min_c:
                        reasons.append(f"Wajib {min_c} Kredit. Anda hanya ada {calculated_credits}.")

                    if reasons:
                        for r in reasons: st.error(f"❌ {r}")
                    else:
                        st.success("✅ Anda melepasi set kriteria ini.")
                    
                    count += 1
else:
    st.info("👈 Masukkan keputusan SPM di sebelah dan tekan 'Semak Kelayakan'")
