import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # encoding='latin1' handles Excel-generated CSVs that contain special characters
    courses = pd.read_csv("courses.csv", encoding='latin1')
    polys = pd.read_csv("polys.csv", encoding='latin1')
    reqs = pd.read_csv("requirements.csv", encoding='latin1')
    links = pd.read_csv("links.csv", encoding='latin1')
    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data()
    st.success("Database Loaded Successfully! ✅")
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- HEADER ---
st.title("🎓 Poly-Checker MVP")
st.write("Check your eligibility for Malaysian Polytechnic Diploma programmes based on SPM results.")
st.markdown("---")

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
has_pure_science = st.sidebar.checkbox("Credit (C or better) in Bio/Physics/Chem/AddMath?")
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
    # 1. Citizenship
    if req['req_malaysian'] == 1 and nationality == "Non-Malaysian": return False, "Citizenship"
    
    # 2. Gender
    if req['req_male'] == 1 and gender == "Female": return False, "Male Only"
    
    # 3. Medical
    if req['no_colorblind'] == 1 and colorblind == "Yes": return False, "Colorblindness"
    if req['no_disability'] == 1 and disability == "Yes": return False, "Physical Disability"

    # 4. Core Subjects
    if req['pass_bm'] == 1 and not is_pass(bm_grade): return False, "Fail BM"
    if req['pass_history'] == 1 and not is_pass(sejarah_grade): return False, "Fail Sejarah"
    if req['pass_eng'] == 1 and not is_pass(bi_grade): return False, "Fail English"
    if req['pass_math'] == 1 and not is_pass(math_grade): return False, "Fail Math"
    if req['credit_math'] == 1 and not is_credit(math_grade): return False, "No Credit Math"
    if req['credit_bm'] == 1 and not is_credit(bm_grade): return False, "No Credit BM"
    if req['credit_eng'] == 1 and not is_credit(bi_grade): return False, "No Credit English"

    # 5. Science/Tech/Voc Logic (The Complex Part)
    # Check Pass in Science/Tech/Voc
    pass_sci = is_pass(science_grade) or has_pure_science
    # For MVP: Assuming 'has_tech'/'has_voc' implies a PASS as well
    pass_stv = pass_sci or has_tech_credit or has_voc_credit
    if req['pass_stv'] == 1 and not pass_stv: return False, "Fail Science/Tech/Voc"

    # Check Credit in Science/Tech/Voc
    credit_sci = is_credit(science_grade) or has_pure_science
    credit_stv = credit_sci or has_tech_credit or has_voc_credit
    if req['credit_stv'] == 1 and not credit_stv: return False, "No Credit Science/Tech/Voc"
    
    # Check Credit in Science/Fizik (Specific Engineering)
    # For MVP, we treat 'has_pure_science' as the proxy for Physics/Bio/Chem
    credit_sf = credit_sci or has_pure_science 
    if req['credit_sf'] == 1 and not credit_sf: return False, "No Credit Science/Physics"

    # 6. Total Credits
    if total_credits < req['min_credits']: return False, f"Min {req['min_credits']} Credits Required"

    return True, "OK"

# --- MAIN APP LOGIC ---
if st.sidebar.button("Check Eligibility"):
    eligible_courses = []
    
    # Run loop
    for index, row in reqs_df.iterrows():
        is_eligible, reason = check_eligibility(row)
        if is_eligible:
            eligible_courses.append(row['course_ID'])
            
    # Display Results
    if len(eligible_courses) == 0:
        st.warning("No eligible courses found based on these results. Try adjusting the grades.")
    else:
        st.success(f"You are eligible for {len(eligible_courses)} courses!")
        
        # Merge with Course Details to get names
        result_df = courses_df[courses_df['course_ID'].isin(eligible_courses)]
        
        # Show cleaner table
        st.dataframe(result_df[['course', 'field', 'department']])
        
        # Optional: Show 'Where is it offered?' for selected course
        st.markdown("### Course Locator")
        selected_course = st.selectbox("Select a course to see locations:", result_df['course'].unique())
        
        # Find ID of selected name
        selected_id = result_df[result_df['course'] == selected_course].iloc[0]['course_ID']
        
        # Find Polys
        linked_polys = links_df[links_df['course_ID'] == selected_id]['institution_ID']
        offering_polys = polys_df[polys_df['institution_ID'].isin(linked_polys)]
        
        st.write(f"**{selected_course}** is available at:")
        st.table(offering_polys[['institution_name', 'State', 'category']])

else:
    st.info("👈 Enter your results in the sidebar and click 'Check Eligibility'")
