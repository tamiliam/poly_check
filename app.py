import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- GRADE POLICY ---
PASS_GRADES = set(["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"])
CREDIT_GRADES = set(["A+", "A", "A-", "B+", "B", "C+", "C"])

def is_pass(grade):
    return grade in PASS_GRADES

def is_credit(grade):
    return grade in CREDIT_GRADES

# --- LOAD DATA (Renamed to force fresh reload) ---
@st.cache_data
def load_data_v2():
    # 1. Load CSVs
    courses = pd.read_csv("courses.csv", encoding="latin1", dtype=str)
    polys = pd.read_csv("polys.csv", encoding="latin1", dtype=str)
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1", dtype=str)

    # 2. Clean Headers (Strip invisible spaces)
    courses.columns = courses.columns.str.strip()
    polys.columns = polys.columns.str.strip()
    reqs.columns = reqs.columns.str.strip()
    links.columns = links.columns.str.strip()

    # 3. Clean IDs
    courses["course_ID"] = courses["course_ID"].str.strip()
    polys["institution_ID"] = polys["institution_ID"].str.strip()
    links["course_ID"] = links["course_ID"].str.strip()
    links["institution_ID"] = links["institution_ID"].str.strip()
    reqs["course_ID"] = reqs["course_ID"].astype(str).str.strip()

    # 4. Force Logic Columns to Integers (0/1)
    bool_cols = [
        "req_malaysian", "req_male", "no_colorblind", "no_disability",
        "pass_bm", "pass_history", "pass_eng", "pass_math",
        "credit_bm", "credit_math", "credit_eng",
        "credit_bmbi", "pass_stv", "credit_stv",
        "credit_sf", "credit_sfmt"
    ]

    for col in bool_cols:
        if col in reqs.columns:
            reqs[col] = pd.to_numeric(reqs[col], errors='coerce').fillna(0).astype(int)

    if "min_credits" in reqs.columns:
        reqs["min_credits"] = pd.to_numeric(reqs["min_credits"], errors='coerce').fillna(0).astype(int)

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data_v2()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.stop()

# --- SIDEBAR (INPUTS) ---
st.sidebar.header("Enter Your SPM Results")

# Changing these will now trigger an IMMEDIATE Recalculation
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

# --- LOGIC ---
def check_eligibility(req):
    # 1. Statutory
    if req.get("req_malaysian", 0) == 1 and nationality == "Non-Malaysian": return False
    if req.get("req_male", 0) == 1 and gender == "Female": return False
    if req.get("no_colorblind", 0) == 1 and colorblind == "Yes": return False
    if req.get("no_disability", 0) == 1 and disability == "Yes": return False

    # 2. Core Subjects (Pass)
    if req.get("pass_bm", 0) == 1 and not is_pass(bm_grade): return False
    if req.get("pass_history", 0) == 1 and not is_pass(sejarah_grade): return False
    if req.get("pass_eng", 0) == 1 and not is_pass(bi_grade): return False
    if req.get("pass_math", 0) == 1 and not is_pass(math_grade): return False

    # 3. Core Subjects (Credit)
    if req.get("credit_bm", 0) == 1 and not is_credit(bm_grade): return False
    if req.get("credit_math", 0) == 1 and not is_credit(math_grade): return False
    if req.get("credit_eng", 0) == 1 and not is_credit(bi_grade): return False

    # 4. Special Groups
    if req.get("credit_bmbi", 0) == 1:
        if not (is_credit(bm_grade) or is_credit(bi_grade)): return False

    has_sci_pass = is_pass(science_grade) or has_pure_science
    has_sci_credit = is_credit(science_grade) or has_pure_science
    has_stv_pass = has_sci_pass or has_tech_credit or has_voc_credit
    has_stv_credit = has_sci_credit or has_tech_credit or has_voc_credit

    if req.get("pass_stv", 0) == 1 and not has_stv_pass: return False
    if req.get("credit_stv", 0) == 1 and not has_stv_credit: return False
    if req.get("credit_sf", 0) == 1 and not has_sci_credit: return False
    if req.get("credit_sfmt", 0) == 1:
        if not (has_stv_credit or is_credit(math_grade)): return False

    # 5. Total Credits
    if total_credits < req.get("min_credits", 0): return False

    return True

# --- MAIN FLOW (No Button - Runs Automatically) ---
eligible_ids = []
for _, row in reqs_df.iterrows():
    if check_eligibility(row):
        eligible_ids.append(row["course_ID"])

# --- RESULTS DISPLAY ---
if not eligible_ids:
    st.warning("No eligible courses found based on these results.")
    if nationality == "Non-Malaysian":
        st.error("❌ Rejection Reason: Citizenship (Most courses require Malaysian status).")
else:
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
