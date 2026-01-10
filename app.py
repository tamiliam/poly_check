import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- HELPER: NUCLEAR COMPARISON ---
def is_active(value):
    # This cleans the value and checks if it looks like a "Yes"
    clean_val = str(value).strip().lower()
    return clean_val in ["1", "1.0", "true", "yes", "y"]

# --- HELPER: GRADE CHECK ---
PASS_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]
CREDIT_GRADES = ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_pass(grade): return str(grade).strip() in PASS_GRADES
def is_credit(grade): return str(grade).strip() in CREDIT_GRADES

# --- LOAD DATA ---
@st.cache_data
def load_data_forensic():
    # Load all as String to see the raw data truth
    courses = pd.read_csv("courses.csv", encoding="latin1", dtype=str)
    polys = pd.read_csv("polys.csv", encoding="latin1", dtype=str)
    reqs = pd.read_csv("requirements.csv", encoding="latin1", dtype=str)
    links = pd.read_csv("links.csv", encoding="latin1", dtype=str)

    # Clean Headers (Strip invisible spaces)
    courses.columns = courses.columns.str.strip()
    polys.columns = polys.columns.str.strip()
    reqs.columns = reqs.columns.str.strip()
    links.columns = links.columns.str.strip()

    # Clean Content (Fixing the previous bug where this wasn't saved)
    courses = courses.map(lambda x: x.strip() if isinstance(x, str) else x)
    polys = polys.map(lambda x: x.strip() if isinstance(x, str) else x)
    reqs = reqs.map(lambda x: x.strip() if isinstance(x, str) else x)
    links = links.map(lambda x: x.strip() if isinstance(x, str) else x)

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data_forensic()
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

# --- CORE LOGIC ---
def check_eligibility(req):
    # 1. Statutory
    if is_active(req.get("req_malaysian")) and nationality == "Non-Malaysian": return False
    if is_active(req.get("req_male")) and gender == "Female": return False
    if is_active(req.get("no_colorblind")) and colorblind == "Yes": return False
    if is_active(req.get("no_disability")) and disability == "Yes": return False

    # 2. Core Subjects (Pass)
    if is_active(req.get("pass_bm")) and not is_pass(bm_grade): return False
    if is_active(req.get("pass_history")) and not is_pass(sejarah_grade): return False
    if is_active(req.get("pass_eng")) and not is_pass(bi_grade): return False
    if is_active(req.get("pass_math")) and not is_pass(math_grade): return False

    # 3. Core Subjects (Credit)
    if is_active(req.get("credit_bm")) and not is_credit(bm_grade): return False
    if is_active(req.get("credit_math")) and not is_credit(math_grade): return False
    if is_active(req.get("credit_eng")) and not is_credit(bi_grade): return False

    # 4. Special Groups
    if is_active(req.get("credit_bmbi")):
        if not (is_credit(bm_grade) or is_credit(bi_grade)): return False

    has_sci_pass = is_pass(science_grade) or has_pure_science
    has_sci_credit = is_credit(science_grade) or has_pure_science
    has_stv_pass = has_sci_pass or has_tech_credit or has_voc_credit
    has_stv_credit = has_sci_credit or has_tech_credit or has_voc_credit

    if is_active(req.get("pass_stv")) and not has_stv_pass: return False
    if is_active(req.get("credit_stv")) and not has_stv_credit: return False
    if is_active(req.get("credit_sf")) and not has_sci_credit: return False
    
    if is_active(req.get("credit_sfmt")):
        if not (has_stv_credit or is_credit(math_grade)): return False

    # 5. Total Credits
    try:
        min_c = int(float(req.get("min_credits", 0)))
    except:
        min_c = 0
        
    if total_credits < min_c: return False

    return True

# --- RUN CHECK ---
eligible_ids = []
debug_trace = [] # Store data for forensic report

for _, row in reqs_df.iterrows():
    if check_eligibility(row):
        eligible_ids.append(row["course_ID"])
        # Save the raw 'req_malaysian' value for the report
        debug_trace.append({
            "Course ID": row["course_ID"],
            "Raw req_malaysian Value": row.get("req_malaysian", "MISSING")
        })

# --- RESULTS DISPLAY ---
if not eligible_ids:
    st.warning("No eligible courses found based on these results.")
else:
    # --- FORENSIC REPORT (Only shows if Non-Malaysian) ---
    if nationality == "Non-Malaysian":
        st.error(f"⚠️ FORENSIC ALERT: {len(eligible_ids)} courses bypassed the Citizenship check.")
        st.write("Below are the courses that passed, and the value they have in the 'req_malaysian' column.")
        st.write("If the value is '0', 'nan', or blank, the system allowed them (Correctly). If it is '1', the logic is broken.")
        
        # Convert list to dataframe for display
        trace_df = pd.DataFrame(debug_trace)
        st.dataframe(trace_df, use_container_width=True)
        st.stop() # Stop here so you can read the report

    # Normal Success View
    st.success(f"✅ You are eligible for {len(eligible_ids)} courses!")
    
    result_df = courses_df[courses_df["course_ID"].isin(eligible_ids)]
    
    st.dataframe(
        result_df[["course", "field", "department"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.markdown("### 📍 Course Locations")
    
    course_names = result_df["course"].unique()
    selected_course = st.selectbox("Select a course to view campuses:", course_names)
    
    if selected_course:
        rows = result_df[result_df["course"] == selected_course]
        if not rows.empty:
            sel_id = rows.iloc[0]["course_ID"]
            poly_ids = links_df[links_df["course_ID"] == sel_id]["institution_ID"]
            final_polys = polys_df[polys_df["institution_ID"].isin(poly_ids)]
            
            if not final_polys.empty:
                st.table(final_polys[["institution_name", "State", "category"]])
            else:
                st.info("No specific location data available.")
