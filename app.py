import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    courses = pd.read_csv("courses.csv", encoding='latin1', dtype=str)
    polys = pd.read_csv("polys.csv", encoding='latin1', dtype=str)
    reqs = pd.read_csv("requirements.csv", encoding='latin1') 
    links = pd.read_csv("links.csv", encoding='latin1', dtype=str)
    
    # Clean Whitespace
    courses['course_ID'] = courses['course_ID'].str.strip()
    reqs['course_ID'] = reqs['course_ID'].astype(str).str.strip()
    links['course_ID'] = links['course_ID'].str.strip()
    links['institution_ID'] = links['institution_ID'].str.strip()
    polys['institution_ID'] = polys['institution_ID'].str.strip()
    
    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Enter Your SPM Results")

# Demographics
nationality = st.sidebar.radio("Citizenship", ["Malaysian", "Non-Malaysian"])
gender = st.sidebar.radio("Gender", ["Male", "Female"])
colorblind = st.sidebar.radio("Are you Colorblind?", ["No", "Yes"])
disability = st.sidebar.radio("Do you have a physical disability?", ["No", "Yes"])

# Grades
grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]
st.sidebar.markdown("### Core Subjects")
bm_grade = st.sidebar.selectbox("Bahasa Melayu", grade_opts, index=6)
sejarah_grade = st.sidebar.selectbox("Sejarah", grade_opts, index=7)
bi_grade = st.sidebar.selectbox("Bahasa Inggeris", grade_opts, index=6)
math_grade = st.sidebar.selectbox("Matematik", grade_opts, index=6)
science_grade = st.sidebar.selectbox("Sains (General)", grade_opts, index=6)

# Credits
st.sidebar.markdown("### Additional Credits")
has_pure_science = st.sidebar.checkbox("Credit (C or better) in Bio/Physics/Chem?")
has_tech_credit = st.sidebar.checkbox("Credit (C or better) in Technical Subjects?")
has_voc_credit = st.sidebar.checkbox("Credit (C or better) in Vocational Subjects?")
total_credits = st.sidebar.slider("Total Number of Kepujian (C and above):", 0, 12, 3)

# --- LOGIC ---
def is_pass(grade): return grade in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
def is_credit(grade): return grade in ["A+", "A", "A-", "B+", "B", "C+", "C"]

def check_eligibility(req):
    # 1. Statutory
    if req.get('req_malaysian', 0) == 1 and nationality == "Non-Malaysian": return False, "Citizenship"
    if req.get('req_male', 0) == 1 and gender == "Female": return False, "Male Only"
    if req.get('no_colorblind', 0) == 1 and colorblind == "Yes": return False, "Colorblindness"
    if req.get('no_disability', 0) == 1 and disability == "Yes": return False, "Physical Disability"

    # 2. Core Subjects (Pass)
    if req.get('pass_bm', 0) == 1 and not is_pass(bm_grade): return False, "Fail BM"
    if req.get('pass_history', 0) == 1 and not is_pass(sejarah_grade): return False, "Fail Sejarah"
    if req.get('pass_eng', 0) == 1 and not is_pass(bi_grade): return False, "Fail English"
    if req.get('pass_math', 0) == 1 and not is_pass(math_grade): return False, "Fail Math"
    
    # 3. Core Subjects (Credit)
    if req.get('credit_bm', 0) == 1 and not is_credit(bm_grade): return False, "No Credit BM"
    if req.get('credit_math', 0) == 1 and not is_credit(math_grade): return False, "No Credit Math"
    if req.get('credit_eng', 0) == 1 and not is_credit(bi_grade): return False, "No Credit English"
    
    # 4. Specialized Group Logic
    if req.get('credit_bmbi', 0) == 1:
        if not (is_credit(bm_grade) or is_credit(bi_grade)): return False, "No Credit in BM or English"

    has_sci_pass = is_pass(science_grade) or has_pure_science
    has_sci_credit = is_credit(science_grade) or has_pure_science
    has_stv_pass = has_sci_pass or has_tech_credit or has_voc_credit
    has_stv_credit = has_sci_credit or has_tech_credit or has_voc_credit
    
    if req.get('pass_stv', 0) == 1 and not has_stv_pass: return False, "Fail Science/Tech/Voc"
    if req.get('credit_stv', 0) == 1 and not has_stv_credit: return False, "No Credit Science/Tech/Voc"
    if req.get('credit_sf', 0) == 1 and not has_sci_credit: return False, "No Credit Science/Physics"
    if req.get('credit_sfmt', 0) == 1:
        if not (has_stv_credit or is_credit(math_grade)): return False, "No Credit Science/Math/Tech"

    # 5. Total Credits
    if total_credits < req.get('min_credits', 0): return False, f"Min {req.get('min_credits', 0)} Credits Required"

    return True, "OK"

# --- MAIN APP FLOW ---

# 1. Handle Button Click (Update State)
if st.sidebar.button("Check Eligibility"):
    eligible = []
    for _, row in reqs_df.iterrows():
        is_ok, _ = check_eligibility(row)
        if is_ok: eligible.append(row['course_ID'])
    
    # Save to memory (Session State)
    st.session_state['eligible_ids'] = eligible
    st.session_state['has_checked'] = True

# 2. Display Results (Read from State)
if st.session_state.get('has_checked', False):
    
    eligible_ids = st.session_state['eligible_ids']
    
    if not eligible_ids:
        st.warning("No eligible courses found based on these results.")
    else:
        st.success(f"You are eligible for {len(eligible_ids)} courses!")
        
        # Filter Courses
        result_df = courses_df[courses_df['course_ID'].isin(eligible_ids)]
        
        # Display Main Table
        st.dataframe(
            result_df[['course', 'field', 'department']], 
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.markdown("### 📍 Course Locations")
        
        # Dropdown for locations
        # Note: We do NOT rely on button state here. We just read the DF.
        course_names = result_df['course'].unique()
        selected_course = st.selectbox("Select a course to view campuses:", course_names)
        
        if selected_course:
            # Look up ID safely
            sel_id = result_df[result_df['course'] == selected_course].iloc[0]['course_ID']
            
            # Find Polys
            poly_ids = links_df[links_df['course_ID'] == sel_id]['institution_ID']
            final_polys = polys_df[polys_df['institution_ID'].isin(poly_ids)]
            
            if not final_polys.empty:
                st.table(final_polys[['institution_name', 'State', 'category']])
            else:
                st.info("Location data pending.")

else:
    st.info("👈 Enter your results and click Check Eligibility")
