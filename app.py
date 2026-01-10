import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- HELPER: ROBUST STRING CLEANING ---
def clean_header(text):
    # Removes hidden characters, spaces, BOMs, forces lowercase
    return str(text).strip().replace("\ufeff", "").lower()

def is_active(value):
    # Treats 1, "1", "1.0", "Yes", "True" as True. Everything else is False.
    s = str(value).strip().lower()
    return s in ['1', '1.0', 'true', 'yes', 'y']

# --- GRADE LOGIC ---
PASS_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
CREDIT_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_pass(g): return str(g).strip() in PASS_GRADES
def is_credit(g): return str(g).strip() in CREDIT_GRADES

# --- LOAD DATA ---
@st.cache_data
def load_data_final():
    # Read CSVs
    courses = pd.read_csv("courses.csv", encoding="latin1")
    polys = pd.read_csv("polys.csv", encoding="latin1")
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1")

    # 1. Clean Headers
    courses.columns = [clean_header(c) for c in courses.columns]
    polys.columns = [clean_header(c) for c in polys.columns]
    reqs.columns = [clean_header(c) for c in reqs.columns]
    links.columns = [clean_header(c) for c in links.columns]

    # 2. Clean ID Columns (Strings)
    reqs['course_id'] = reqs['course_id'].astype(str).str.strip()
    courses['course_id'] = courses['course_id'].astype(str).str.strip()
    links['course_id'] = links['course_id'].astype(str).str.strip()
    links['institution_id'] = links['institution_id'].astype(str).str.strip()
    polys['institution_id'] = polys['institution_id'].astype(str).str.strip()

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data_final()
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

# --- ELIGIBILITY ENGINE ---
def check_eligibility(req):
    # 1. Statutory Checks
    if is_active(req.get('req_malaysian')) and nationality == "Non-Malaysian": return False
    if is_active(req.get('req_male')) and gender == "Female": return False
    if is_active(req.get('no_colorblind')) and colorblind == "Yes": return False
    if is_active(req.get('no_disability')) and disability == "Yes": return False

    # 2. Grades
    if is_active(req.get('pass_bm')) and not is_pass(bm_grade): return False
    if is_active(req.get('pass_history')) and not is_pass(sejarah_grade): return False
    if is_active(req.get('pass_eng')) and not is_pass(bi_grade): return False
    if is_active(req.get('pass_math')) and not is_pass(math_grade): return False

    if is_active(req.get('credit_bm')) and not is_credit(bm_grade): return False
    if is_active(req.get('credit_math')) and not is_credit(math_grade): return False
    if is_active(req.get('credit_eng')) and not is_credit(bi_grade): return False
    if is_active(req.get('credit_bmbi')) and not (is_credit(bm_grade) or is_credit(bi_grade)): return False

    # 3. Science / Tech Logic
    sci_p = is_pass(science_grade) or has_pure_science
    sci_c = is_credit(science_grade) or has_pure_science
    stv_p = sci_p or has_tech_credit or has_voc_credit
    stv_c = sci_c or has_tech_credit or has_voc_credit

    if is_active(req.get('pass_stv')) and not stv_p: return False
    if is_active(req.get('credit_stv')) and not stv_c: return False
    if is_active(req.get('credit_sf')) and not sci_c: return False
    
    if is_active(req.get('credit_sfmt')):
        # Science OR Fizik OR Math OR Tech
        if not (stv_c or is_credit(math_grade)): return False

    # 4. Min Credits
    try:
        min_c = int(float(req.get('min_credits', 0)))
    except:
        min_c = 0
    if total_credits < min_c: return False

    return True

# --- MAIN FLOW ---
if st.sidebar.button("Check Eligibility"):
    eligible_ids = []
    
    # Run the Engine
    for _, row in reqs_df.iterrows():
        if check_eligibility(row):
            eligible_ids.append(row['course_id'])
    
    # Save Result to Memory
    st.session_state['eligible_ids'] = eligible_ids
    st.session_state['has_checked'] = True

# --- DISPLAY RESULTS ---
if st.session_state.get('has_checked', False):
    
    eligible_ids = st.session_state['eligible_ids']
    
    if not eligible_ids:
        st.warning("No eligible courses found based on these results.")
        if nationality == "Non-Malaysian":
            st.caption("Note: Most polytechnic courses require Malaysian citizenship.")
            
    else:
        st.success(f"✅ You are eligible for {len(eligible_ids)} courses!")
        
        # 1. Main Table
        res = courses_df[courses_df['course_id'].isin(eligible_ids)]
        st.dataframe(
            res[['course', 'field', 'department']], 
            hide_index=True, 
            use_container_width=True
        )

        # 2. Location Finder
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
