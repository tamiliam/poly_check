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
# "G" is a Fail. "T" (Tidak Hadir) is a Fail. "Not Taken" is not a credit.
PASS_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
CREDIT_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_pass(g): return str(g).strip() in PASS_GRADES
def is_credit(g): return str(g).strip() in CREDIT_GRADES

# --- LOAD DATA ---
@st.cache_data
def load_data_v8():
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
    courses_df, polys_df, reqs_df, links_df = load_data_v8()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Student Profile")

# 1. Demographics
with st.sidebar.expander("👤 Personal Details", expanded=True):
    nationality = st.radio("Citizenship", ["Malaysian", "Non-Malaysian"])
    gender = st.radio("Gender", ["Male", "Female"])
    colorblind = st.radio("Colorblind?", ["No", "Yes"])
    disability = st.radio("Physical Disability?", ["No", "Yes"])

# 2. Subjects
# Option "X" means Not Taken
grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G", "Not Taken"]

with st.sidebar.expander("📚 Compulsory Subjects", expanded=True):
    bm_grade = st.selectbox("Bahasa Melayu", grade_opts, index=5) # Default C
    eng_grade = st.selectbox("Bahasa Inggeris", grade_opts, index=6) # Default D
    hist_grade = st.selectbox("Sejarah", grade_opts, index=6)
    math_grade = st.selectbox("Matematik", grade_opts, index=5)
    islam_moral = st.selectbox("P. Islam / P. Moral", grade_opts, index=5)

with st.sidebar.expander("🧪 Science Stream"):
    addmath_grade = st.selectbox("Matematik Tambahan", grade_opts, index=10) # Default Not Taken
    phy_grade = st.selectbox("Fizik", grade_opts, index=10)
    chem_grade = st.selectbox("Kimia", grade_opts, index=10)
    bio_grade = st.selectbox("Biologi", grade_opts, index=10)

with st.sidebar.expander("🎨 Arts / Humanities / Voc"):
    science_gen_grade = st.selectbox("Sains (General)", grade_opts, index=5)
    geo_grade = st.selectbox("Geografi", grade_opts, index=10)
    acc_grade = st.selectbox("Prinsip Perakaunan", grade_opts, index=10)
    biz_grade = st.selectbox("Perniagaan", grade_opts, index=10)
    econ_grade = st.selectbox("Ekonomi", grade_opts, index=10)
    psv_grade = st.selectbox("Pendidikan Seni Visual", grade_opts, index=10)
    
    st.caption("Electives / Technical / Vocational")
    rekacipta_grade = st.selectbox("Reka Cipta", grade_opts, index=10)
    cs_grade = st.selectbox("Sains Komputer", grade_opts, index=10)
    pertanian_grade = st.selectbox("Pertanian", grade_opts, index=10)
    srt_grade = st.selectbox("Sains Rumah Tangga", grade_opts, index=10)
    
    # Catch-all for the "Many others"
    other_tech_grade = st.checkbox("I have a Credit (C+) in another Technical Subject")
    other_voc_grade = st.checkbox("I have a Credit (C+) in another Vocational Subject")

# --- AUTO-CALCULATE DERIVED STATS ---
# 1. Total Credits (Count all Cs and above)
all_subjects = [
    bm_grade, eng_grade, hist_grade, math_grade, islam_moral,
    addmath_grade, phy_grade, chem_grade, bio_grade,
    science_gen_grade, geo_grade, acc_grade, biz_grade, econ_grade, psv_grade,
    rekacipta_grade, cs_grade, pertanian_grade, srt_grade
]

calculated_credits = 0
for g in all_subjects:
    if is_credit(g):
        calculated_credits += 1
# Add manual checkboxes if checked (assuming they imply credit)
if other_tech_grade: calculated_credits += 1
if other_voc_grade: calculated_credits += 1

st.sidebar.info(f"📊 Calculated Total Credits: {calculated_credits}")

# 2. Logic Groupings
# Science Group (Bio/Phy/Chem/AddMath)
has_pure_science_pass = any(is_pass(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])
has_pure_science_credit = any(is_credit(g) for g in [bio_grade, phy_grade, chem_grade, addmath_grade])

# Technical Group (Reka Cipta, CS, or Other)
has_tech_pass = any(is_pass(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade
has_tech_credit = any(is_credit(g) for g in [rekacipta_grade, cs_grade]) or other_tech_grade

# Vocational Group (Pertanian, SRT, or Other)
has_voc_pass = any(is_pass(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade
has_voc_credit = any(is_credit(g) for g in [pertanian_grade, srt_grade]) or other_voc_grade

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

    # Science / Tech / Voc Logic
    # --------------------------
    # General Science Pass = Pass in General Science OR Pure Science Subject
    sci_p = is_pass(science_gen_grade) or has_pure_science_pass
    sci_c = is_credit(science_gen_grade) or has_pure_science_credit
    
    stv_p = sci_p or has_tech_pass or has_voc_pass
    stv_c = sci_c or has_tech_credit or has_voc_credit

    if is_active(req.get('pass_stv')) and not stv_p: return False
    if is_active(req.get('credit_stv')) and not stv_c: return False
    if is_active(req.get('credit_sf')) and not sci_c: return False
    
    if is_active(req.get('credit_sfmt')):
        # Science OR Fizik OR Math OR Tech
        if not (stv_c or is_credit(math_grade)): return False

    # Min Credits
    try:
        min_c = int(float(req.get('min_credits', 0)))
    except:
        min_c = 0
    
    # Use our AUTO-CALCULATED total
    if calculated_credits < min_c: return False

    return True

# --- MAIN FLOW ---
if st.sidebar.button("Check Eligibility"):
    
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
        
        res = courses_df[courses_df['course_id'].isin(eligible_ids)]
        st.dataframe(res[['course', 'field', 'department']], hide_index=True, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📍 Course Locations")
        
        sel = st.selectbox("Select a course to view campuses:", res['course'].unique())
        
        if sel:
            cid = res[res['course'] == sel].iloc[0]['course_id']
            pids = links_df[links_df['course_id'] == cid]['institution_id']
            final = polys_df[polys_df['institution_id'].isin(pids)]
            
            if not final.empty:
                st.table(final[['institution_name', 'state', 'category']])
            else:
                st.info("No specific campus location data available.")

else:
    st.info("👈 Enter your results in the sidebar and click 'Check Eligibility'")
