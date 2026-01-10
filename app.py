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
def load_data_v7():
    courses = pd.read_csv("courses.csv", encoding="latin1")
    polys = pd.read_csv("polys.csv", encoding="latin1")
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1")

    # Clean Headers & Content
    courses.columns = [clean_header(c) for c in courses.columns]
    polys.columns = [clean_header(c) for c in polys.columns]
    reqs.columns = [clean_header(c) for c in reqs.columns]
    links.columns = [clean_header(c) for c in links.columns]

    # Clean IDs
    reqs['course_id'] = reqs['course_id'].astype(str).str.strip()
    courses['course_id'] = courses['course_id'].astype(str).str.strip()
    links['course_id'] = links['course_id'].astype(str).str.strip()
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    polys['institution_id'] = polys['institution_id'].astype(str).str.strip()

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data_v7()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Enter Your SPM Results")

nationality = st.sidebar.radio("Citizenship", ["Malaysian", "Non-Malaysian"])
gender = st.sidebar.radio("Gender", ["Male", "Female"])
colorblind = st.sidebar.radio("Are you Colorblind?", ["No", "Yes"])
disability = st.sidebar.radio("Do you have a physical disability?", ["No", "Yes"])

grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]
st.sidebar.markdown("### Core Subjects")
bm_grade = st.sidebar.selectbox("Bahasa Melayu", grade_opts, index=6)
sejarah_grade = st.sidebar.selectbox("Sejarah", grade_opts, index=7)
bi_grade = st.sidebar.selectbox("Bahasa Inggeris", grade_opts, index=6)
math_grade = st.sidebar.selectbox("Matematik", grade_opts, index=6)
science_grade = st.sidebar.selectbox("Sains (General)", grade_opts, index=6)

st.sidebar.markdown("### Additional Credits")
has_pure_science = st.sidebar.checkbox("Credit (C or better) in Bio/Physics/Chem?")
has_tech_credit = st.sidebar.checkbox("Credit (C or better) in Technical Subjects?")
has_voc_credit = st.sidebar.checkbox("Credit (C or better) in Vocational Subjects?")
total_credits = st.sidebar.slider("Total Number of Kepujian (C and above):", 0, 12, 3)

# --- 1. GATEKEEPER LOGIC (Global Mandates) ---
# These are checked BEFORE looking at any course.
def check_gatekeepers():
    if nationality == "Non-Malaysian":
        return False, "Malaysian Citizenship is required."
    if not is_pass(bm_grade):
        return False, "A Pass in Bahasa Melayu is mandatory."
    if not is_pass(sejarah_grade):
        return False, "A Pass in Sejarah is mandatory."
    return True, "OK"

# --- 2. ROW EVALUATOR (Partial Constraints) ---
def check_row_constraints(req):
    # This function checks if the student meets the constraints IN THIS SPECIFIC ROW.
    
    # Gender
    if is_active(req.get('req_male')) and gender == "Female": return False
    
    # Medical
    if is_active(req.get('no_colorblind')) and colorblind == "Yes": return False
    if is_active(req.get('no_disability')) and disability == "Yes": return False

    # English & Math (Pass)
    if is_active(req.get('pass_eng')) and not is_pass(bi_grade): return False
    if is_active(req.get('pass_math')) and not is_pass(math_grade): return False

    # Credits (Kepujian)
    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): return False
    if is_active(req.get('credit_math')) and not is_credit(math_grade): return False
    if is_active(req.get('credit_eng')) and not is_credit(bi_grade): return False
    if is_active(req.get('credit_bmbi')) and not (is_credit(bm_grade) or is_credit(bi_grade)): return False

    # Science / Tech Logic
    sci_p = is_pass(science_grade) or has_pure_science
    sci_c = is_credit(science_grade) or has_pure_science
    stv_p = sci_p or has_tech_credit or has_voc_credit
    stv_c = sci_c or has_tech_credit or has_voc_credit

    if is_active(req.get('pass_stv')) and not stv_p: return False
    if is_active(req.get('credit_stv')) and not stv_c: return False
    if is_active(req.get('credit_sf')) and not sci_c: return False
    
    if is_active(req.get('credit_sfmt')):
        if not (stv_c or is_credit(math_grade)): return False

    # Min Credits
    try:
        min_c = int(float(req.get('min_credits', 0)))
    except:
        min_c = 0
    if total_credits < min_c: return False

    return True

# --- MAIN FLOW ---
if st.sidebar.button("Check Eligibility"):
    
    # A. Run Gatekeepers First
    passed_gates, gate_msg = check_gatekeepers()
    
    if not passed_gates:
        st.session_state['eligible_ids'] = []
        st.session_state['fail_reason'] = gate_msg
        st.session_state['has_checked'] = True
    else:
        # B. Run Course Evaluator (AND Logic across rows)
        eligible_ids = []
        
        # Group by Course ID to handle split requirements
        # If a course has 2 rows, student must pass BOTH rows.
        grouped = reqs_df.groupby('course_id')
        
        for cid, group in grouped:
            # Check every row in the group
            # group.apply(...) returns a Series of True/False
            # .all() ensures every row returned True
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
