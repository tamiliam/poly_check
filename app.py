import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

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
def load_data_v12():
    courses = pd.read_csv("courses.csv", encoding="latin1")
    polys = pd.read_csv("polys.csv", encoding="latin1")
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1")

    # Clean Headers & Content
    courses.columns = [clean_header(c) for c in courses.columns]
    polys.columns = [clean_header(c) for c in polys.columns]
    reqs.columns = [clean_header(c) for c in reqs.columns]
    links.columns = [clean_header(c) for c in links.columns]

    reqs['course_id'] = reqs['course_id'].astype(str).str.strip()
    courses['course_id'] = courses['course_id'].astype(str).str.strip()
    links['course_id'] = links['course_id'].astype(str).str.strip()
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    polys['institution_id'] = polys['institution_id'].astype(str).str.strip()

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data_v12()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Student Profile")

# 1. Demographics
with st.sidebar.expander("👤 Personal Details", expanded=True):
    nationality = st.radio("Citizenship", ["Malaysian", "Non-Malaysian"], key="nat_input")
    gender = st.radio("Gender", ["Male", "Female"], key="gen_input")
    
    # COLORBLIND TEST LINK ADDED HERE
    st.write("**Medical Conditions**")
    colorblind = st.radio("Colorblind?", ["No", "Yes"], key="cb_input")
    st.caption("Not sure? [Take a quick free test here](https://enchroma.com/pages/color-blind-test) (External Link)")
    
    disability = st.radio("Physical Disability?", ["No", "Yes"], key="dis_input")

# 2. Subjects
grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G", "Not Taken"]

with st.sidebar.expander("📚 Compulsory Subjects", expanded=True):
    bm_grade = st.selectbox("Bahasa Melayu", grade_opts, index=5, key="bm_input")
    eng_grade = st.selectbox("Bahasa Inggeris", grade_opts, index=6, key="bi_input")
    hist_grade = st.selectbox("Sejarah", grade_opts, index=6, key="hist_input")
    math_grade = st.selectbox("Matematik", grade_opts, index=5, key="math_input")
    islam_moral = st.selectbox("P. Islam / P. Moral", grade_opts, index=5, key="rel_input")

with st.sidebar.expander("🧪 Science Stream"):
    addmath_grade = st.selectbox("Matematik Tambahan", grade_opts, index=10, key="am_input")
    phy_grade = st.selectbox("Fizik", grade_opts, index=10, key="phy_input")
    chem_grade = st.selectbox("Kimia", grade_opts, index=10, key="chem_input")
    bio_grade = st.selectbox("Biologi", grade_opts, index=10, key="bio_input")

with st.sidebar.expander("🎨 Arts & Humanities"):
    science_gen_grade = st.selectbox("Sains (General)", grade_opts, index=10, key="sci_input")
    geo_grade = st.selectbox("Geografi", grade_opts, index=10, key="geo_input")
    acc_grade = st.selectbox("Prinsip Perakaunan", grade_opts, index=10, key="acc_input")
    biz_grade = st.selectbox("Perniagaan", grade_opts, index=10, key="biz_input")
    econ_grade = st.selectbox("Ekonomi", grade_opts, index=10, key="econ_input")
    psv_grade = st.selectbox("Pendidikan Seni Visual", grade_opts, index=10, key="psv_input")

with st.sidebar.expander("🕌 Languages & Islamic Electives"):
    lang_add_grade = st.selectbox("B. Arab / Cina / Tamil / Punjabi", grade_opts, index=10, key="lang_input")
    lit_grade = st.selectbox("Kesusasteraan (Melayu/Inggeris/Cina/Tamil)", grade_opts, index=10, key="lit_input")
    islam_add_grade = st.selectbox("P. Al-Quran / As-Sunnah / Syariah", grade_opts, index=10, key="rel_add_input")

with st.sidebar.expander("🛠️ Technical & Vocational Electives"):
    rekacipta_grade = st.selectbox("Reka Cipta", grade_opts, index=10, key="rc_input")
    cs_grade = st.selectbox("Sains Komputer", grade_opts, index=10, key="cs_input")
    pertanian_grade = st.selectbox("Pertanian", grade_opts, index=10, key="agro_input")
    srt_grade = st.selectbox("Sains Rumah Tangga", grade_opts, index=10, key="srt_input")
    
    st.caption("Others")
    other_tech_grade = st.checkbox("Credit (C or above) in other Technical Subject", key="tech_check")
    other_voc_grade = st.checkbox("Credit (C or above) in other Vocational Subject", key="voc_check")

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

st.sidebar.info(f"📊 Calculated Total Credits: {calculated_credits}")

# --- 1. GATEKEEPER LOGIC ---
def check_gatekeepers():
    if nationality == "Non-Malaysian": return False, "Malaysian Citizenship is required."
    if not is_pass(bm_grade): return False, "A Pass in Bahasa Melayu is mandatory."
    if not is_pass(hist_grade): return False, "A Pass in Sejarah is mandatory."
    return True, "OK"

# --- 2. ROW EVALUATOR ---
def check_row_constraints(req):
    
    # Gender & Medical
    if is_active(req.get('req_male')) and gender == "Female": return False
    if is_active(req.get('no_colorblind')) and colorblind == "Yes": return False
    if is_active(req.get('no_disability')) and disability == "Yes": return False

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

    # Min Credits
    try:
        min_c = int(float(req.get('min_credits', 0)))
    except:
        min_c = 0
    
    if calculated_credits < min_c: return False

    return True

# --- MAIN FLOW ---
if st.sidebar.button("Check Eligibility", key="check_btn"):
    
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
        st.error(f"❌ Not Eligible. Reason: {fail_reason}")
    elif not eligible_ids:
        st.warning("No eligible courses found based on your specific grades.")
        st.write(f"Total Credits Detected: {calculated_credits}")
    else:
        st.success(f"✅ You are eligible for {len(eligible_ids)} courses!")
        
        # 1. PREPARE RESULTS TABLE
        res = courses_df[courses_df['course_id'].isin(eligible_ids)].copy()
        
        # 2. INJECT INTERVIEW STATUS
        # Map ID to Interview Req
        interview_map = {}
        for cid in eligible_ids:
            # Check if ANY row for this course requires interview
            rows = reqs_df[reqs_df['course_id'] == cid]
            has_interview = rows['req_interview'].apply(is_active).any()
            interview_map[cid] = "🗣️ Yes" if has_interview else "No"
            
        res['Interview?'] = res['course_id'].map(interview_map)
        
        # 3. DISPLAY TABLE
        st.dataframe(
            res[['course', 'Interview?', 'field', 'department']], 
            hide_index=True, 
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### 📍 Course Locations")
        
        sel = st.selectbox("Select a course to view campuses:", res['course'].unique(), key="location_select")
        
        if sel:
            cid = res[res['course'] == sel].iloc[0]['course_id']
            pids = links_df[links_df['course_id'] == cid]['institution_id']
            final = polys_df[polys_df['institution_id'].isin(pids)]
            
            if not final.empty:
                st.table(final[['institution_name', 'state', 'category']])
            else:
                st.info("No specific campus location data available.")

    # FORENSIC INSPECTOR
    st.markdown("---")
    st.header("🕵️ Why wasn't I eligible?")
    st.write("Select a course below to see exactly which requirement you missed.")

    all_course_ids = set(courses_df['course_id'].unique())
    eligible_set = set(eligible_ids)
    rejected_ids = list(all_course_ids - eligible_set)
    
    if rejected_ids:
        rejected_courses = courses_df[courses_df['course_id'].isin(rejected_ids)]
        rejected_courses = rejected_courses.sort_values('course')
        course_options = dict(zip(rejected_courses['course'], rejected_courses['course_id']))
        
        inspect_name = st.selectbox("Select a rejected course:", options=course_options.keys(), key="inspect_select")
        
        if inspect_name:
            inspect_id = course_options[inspect_name]
            st.markdown(f"### 🧐 Analysis for: {inspect_name}")
            
            gate_pass, gate_msg = check_gatekeepers()
            if not gate_pass:
                st.error(f"❌ FAILED: {gate_msg}")
            else:
                st.success("✅ Global Requirements (Citizenship, BM, Sejarah) Met")

                rows = reqs_df[reqs_df['course_id'] == inspect_id]
                
                if rows.empty:
                    st.error("⚠️ Error: No requirements found for this course.")
                
                count = 1
                for index, req in rows.iterrows():
                    st.markdown(f"**Criteria Set #{count}:**")
                    reasons = []

                    if is_active(req.get('req_male')) and gender == "Female": reasons.append("Requires Male applicants.")
                    if is_active(req.get('no_colorblind')) and colorblind == "Yes": reasons.append("Cannot accept Colorblind applicants.")
                    if is_active(req.get('no_disability')) and disability == "Yes": reasons.append("Cannot accept applicants with physical disabilities.")

                    if is_active(req.get('pass_eng')) and not is_pass(eng_grade): reasons.append("Requires Pass in English.")
                    if is_active(req.get('pass_math')) and not is_pass(math_grade): reasons.append("Requires Pass in Mathematics.")
                    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): reasons.append("Requires Credit (C) in BM.")
                    if is_active(req.get('credit_math')) and not is_credit(math_grade): reasons.append("Requires Credit (C) in Mathematics.")
                    if is_active(req.get('credit_eng')) and not is_credit(eng_grade): reasons.append("Requires Credit (C) in English.")
                    
                    if is_active(req.get('credit_bmbi')):
                         if not (is_credit(bm_grade) or is_credit(eng_grade)):
                             reasons.append("Requires Credit (C) in EITHER BM or English.")

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

                    if is_active(req.get('pass_stv')) and not stv_pass: reasons.append("Requires Pass in Science/Tech/Voc.")
                    if is_active(req.get('credit_stv')) and not stv_credit: reasons.append("Requires Credit in Science/Tech/Voc.")
                    
                    if is_active(req.get('credit_sf')):
                        if not (is_credit(science_gen_grade) or is_credit(phy_grade)): 
                            reasons.append("Requires Credit (C) in General Science OR Physics.")

                    if is_active(req.get('credit_sfmt')):
                        if not (is_credit(science_gen_grade) or is_credit(phy_grade) or is_credit(addmath_grade)):
                            reasons.append("Requires Credit (C) in General Science OR Physics OR Add Math.")

                    try:
                        min_c = int(float(req.get('min_credits', 0)))
                    except:
                        min_c = 0
                    
                    if calculated_credits < min_c:
                        reasons.append(f"Requires {min_c} Total Credits. You have {calculated_credits}.")

                    if reasons:
                        for r in reasons: st.error(f"❌ {r}")
                    else:
                        st.success("✅ You meet all criteria in this set.")
                    
                    count += 1
else:
    st.info("👈 Enter your results in the sidebar and click 'Check Eligibility'")
