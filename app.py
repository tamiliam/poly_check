import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # encoding='latin1' handles Excel-generated CSVs
    # dtype=str ensures IDs are read as text, not numbers
    courses = pd.read_csv("courses.csv", encoding='latin1', dtype=str)
    polys = pd.read_csv("polys.csv", encoding='latin1', dtype=str)
    reqs = pd.read_csv("requirements.csv", encoding='latin1') # reqs needs numbers for math
    links = pd.read_csv("links.csv", encoding='latin1', dtype=str)
    
    # --- CRITICAL FIX: WHITESPACE CLEANER ---
    # This kills the "IndexError" by stripping invisible spaces from IDs
    courses['course_ID'] = courses['course_ID'].str.strip()
    reqs['course_ID'] = reqs['course_ID'].astype(str).str.strip()
    links['course_ID'] = links['course_ID'].str.strip()
    links['institution_ID'] = links['institution_ID'].str.strip()
    polys['institution_ID'] = polys['institution_ID'].str.strip()
    
    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data()
    st.success("Database Loaded Successfully! ✅")
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR: STUDENT INPUTS ---
st.sidebar.header("Enter Your SPM Results")

# 1. Demographics
nationality = st.sidebar.radio("Citizenship", ["Malaysian", "Non-Malaysian"])
gender = st.sidebar.radio("Gender", ["Male", "Female"])
colorblind = st.sidebar.radio("Are you Colorblind?", ["No", "Yes"])
disability = st.sidebar.radio("Do you have a physical disability?", ["No", "Yes"])

# 2. Core Subjects (Grades)
grade_opts = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]

st.sidebar.markdown("### Core Subjects")
bm_grade = st.sidebar.selectbox("Bahasa Melayu", grade_opts, index=6) # Default C
sejarah_grade = st.sidebar.selectbox("Sejarah", grade_opts, index=7) # Default D
bi_grade = st.sidebar.selectbox("Bahasa Inggeris", grade_opts, index=6)
math_grade = st.sidebar.selectbox("Matematik", grade_opts, index=6)
science_grade = st.sidebar.selectbox("Sains (General)", grade_opts, index=6)

# 3. Additional Credits
st.sidebar.markdown("### Additional Credits")
has_pure_science = st.sidebar.checkbox("Credit (C or better) in Bio/Physics/Chem?")
has_tech_credit = st.sidebar.checkbox("Credit (C or better) in Technical Subjects?")
has_voc_credit = st.sidebar.checkbox("Credit (C or better) in Vocational Subjects?")

# 4. Total Count
total_credits = st.sidebar.slider("Total Number of Kepujian (Grades C and above) in all subjects:", 0, 12, 3)

# --- LOGIC FUNCTIONS ---
def is_pass(grade):
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]

def is_credit(grade):
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C"]

def check_eligibility(req):
    # Use .get() to prevent crashes if column is missing
    
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
    
    # 4. Specialized Group Logic (Based on YOUR Headers)
    
    # credit_bmbi: Credit in BM OR BI
    if req.get('credit_bmbi', 0) == 1:
        if not (is_credit(bm_grade) or is_credit(bi_grade)):
            return False, "No Credit in BM or English"

    # Logic Variables for Groups
    has_sci_pass = is_pass(science_grade) or has_pure_science
    has_sci_credit = is_credit(science_grade) or has_pure_science
    
    has_stv_pass = has_sci_pass or has_tech_credit or has_voc_credit # Assuming Credit implies Pass
    has_stv_credit = has_sci_credit or has_tech_credit or has_voc_credit
    
    # pass_stv: Pass Science OR Tech OR Voc
    if req.get('pass_stv', 0) == 1 and not has_stv_pass: return False, "Fail Science/Tech/Voc"
    
    # credit_stv: Credit Science OR Tech OR Voc
    if req.get('credit_stv', 0) == 1 and not has_stv_credit: return False, "No Credit Science/Tech/Voc"

    # credit_sf: Credit Science OR Physics (Pure Science)
    if req.get('credit_sf', 0) == 1 and not has_sci_credit: return False, "No Credit Science/Physics"
    
    # credit_sfmt: Science OR Fizik OR Math OR Tech
    # Logic: credit_stv OR credit_math
    if req.get('credit_sfmt', 0) == 1:
        if not (has_stv_credit or is_credit(math_grade)):
            return False, "No Credit Science/Math/Tech"

    # 5. Total Credits
    if total_credits < req.get('min_credits', 0): return False, f"Min {req.get('min_credits', 0)} Credits Required"

    return True, "OK"

# --- MAIN APP LOGIC ---
if st.sidebar.button("Check Eligibility"):
    eligible_courses = []
    
    for index, row in reqs_df.iterrows():
        is_eligible, reason = check_eligibility(row)
        if is_eligible:
            eligible_courses.append(row['course_ID'])
            
    # Display Results
    if len(eligible_courses) == 0:
        st.warning("No eligible courses found based on these results.")
        # Debugging hint for "Non-Malaysian" issue
        if nationality == "Non-Malaysian":
            st.caption("Note: Most Polytechnic courses require Malaysian Citizenship.")
    else:
        st.success(f"You are eligible for {len(eligible_courses)} courses!")
        
        # Merge with Course Details
        result_df = courses_df[courses_df['course_ID'].isin(eligible_courses)]
        
        # Display Table
        st.dataframe(result_df[['course', 'field', 'department']], use_container_width=True)
        
        # Course Locator
        st.markdown("---")
        st.markdown("### 📍 Where can I study?")
        
        # --- SAFE SELECTION LOGIC ---
        course_names = result_df['course'].unique()
        selected_course = st.selectbox("Select a course to view locations:", course_names)
        
        if selected_course:
            # Safe lookup to prevent IndexError
            matching_rows = result_df[result_df['course'] == selected_course]
            
            if not matching_rows.empty:
                sel_id = matching_rows.iloc[0]['course_ID']
                
                # Find Polys
                poly_ids = links_df[links_df['course_ID'] == sel_id]['institution_ID']
                final_polys = polys_df[polys_df['institution_ID'].isin(poly_ids)]
                
                if not final_polys.empty:
                    st.table(final_polys[['institution_name', 'State', 'category']])
                else:
                    st.info("No specific campus location data found for this course.")
            else:
                st.error("Error: Course found in eligibility list but ID mismatch. Try refreshing.")

else:
    st.info("👈 Enter your results in the sidebar and click 'Check Eligibility'")
