import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Polytechnic Checker", page_icon="🎓")

# --- GRADE POLICY (EXTERNALISED) ---
PASS_GRADES = set(["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"])
CREDIT_GRADES = set(["A+", "A", "A-", "B+", "B", "C+", "C"])

def is_pass(grade):
    return grade in PASS_GRADES

def is_credit(grade):
    return grade in CREDIT_GRADES

# --- LOAD DATA ---
@st.cache_data
def load_data():
    courses = pd.read_csv("courses.csv", encoding="latin1", dtype=str)
    polys = pd.read_csv("polys.csv", encoding="latin1", dtype=str)
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    links = pd.read_csv("links.csv", encoding="latin1", dtype=str)

    # --- 1. CLEAN HEADERS (Crucial Step) ---
    # This fixes issues where "req_malaysian " (with space) causes logic to fail
    courses.columns = courses.columns.str.strip()
    polys.columns = polys.columns.str.strip()
    reqs.columns = reqs.columns.str.strip()
    links.columns = links.columns.str.strip()

    # --- 2. CLEAN DATA WHITESPACE ---
    courses["course_ID"] = courses["course_ID"].str.strip()
    polys["institution_ID"] = polys["institution_ID"].str.strip()
    links["course_ID"] = links["course_ID"].str.strip()
    links["institution_ID"] = links["institution_ID"].str.strip()
    reqs["course_ID"] = reqs["course_ID"].astype(str).str.strip()

    # --- 3. NORMALISE REQUIREMENTS ---
    bool_cols = [
        "req_malaysian", "req_male", "no_colorblind", "no_disability",
        "pass_bm", "pass_history", "pass_eng", "pass_math",
        "credit_bm", "credit_math", "credit_eng",
        "credit_bmbi", "pass_stv", "credit_stv",
        "credit_sf", "credit_sfmt"
    ]

    for col in bool_cols:
        # Use .get() to avoid crashing if a column is missing
        if col in reqs.columns:
            # Force conversion to number (0 or 1)
            # errors='coerce' turns text like "Yes" into NaN (0)
            reqs[col] = pd.to_numeric(reqs[col], errors='coerce').fillna(0).astype(int)

    if "min_credits" in reqs.columns:
        reqs["min_credits"] = pd.to_numeric(reqs["min_credits"], errors='coerce').fillna(0).astype(int)

    return courses, polys, reqs, links

try:
    courses_df, polys_df, reqs_df, links_df = load_data()
except Exception as e:
#    st.error(f"Error loading database: {e}")
#    st.stop()

# --- DEBUGGER (Add this right after the try/except block) ---
# This lets you see if 'req_malaysian' is actually 1 or 0
# with st.expander("🕵️ Developer Data View (Click to Inspect)"):
    st.write("First 5 rows of Requirements Table:")
    st.dataframe(reqs_df.head())


# --- SIDEBAR ---
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

# --- ELIGIBILITY LOGIC ---
def check_eligibility(req):
    # 1. Statutory
    if req["req_malaysian"] and nationality == "Non-Malaysian":
        return False, "Citizenship"
    if req["req_male"] and gender == "Female":
        return False, "Male Only"
    if req["no_colorblind"] and colorblind == "Yes":
        return False, "Colorblindness"
    if req["no_disability"] and disability == "Yes":
        return False, "Physical Disability"

    # 2. Core Subjects (Pass)
    if req["pass_bm"] and not is_pass(bm_grade):
        return False, "Fail BM"
    if req["pass_history"] and not is_pass(sejarah_grade):
        return False, "Fail Sejarah"
    if req["pass_eng"] and not is_pass(bi_grade):
        return False, "Fail English"
    if req["pass_math"] and not is_pass(math_grade):
        return False, "Fail Math"

    # 3. Core Subjects (Credit)
    if req["credit_bm"] and not is_credit(bm_grade):
        return False, "No Credit BM"
    if req["credit_math"] and not is_credit(math_grade):
        return False, "No Credit Math"
    if req["credit_eng"] and not is_credit(bi_grade):
        return False, "No Credit English"

    # 4. Specialised Group Logic
    if req["credit_bmbi"]:
        if not (is_credit(bm_grade) or is_credit(bi_grade)):
            return False, "No Credit in BM or English"

    has_sci_pass = is_pass(science_grade) or has_pure_science
    has_sci_credit = is_credit(science_grade) or has_pure_science
    has_stv_pass = has_sci_pass or has_tech_credit or has_voc_credit
    has_stv_credit = has_sci_credit or has_tech_credit or has_voc_credit

    if req["pass_stv"] and not has_stv_pass:
        return False, "Fail Science/Tech/Voc"
    if req["credit_stv"] and not has_stv_credit:
        return False, "No Credit Science/Tech/Voc"
    if req["credit_sf"] and not has_sci_credit:
        return False, "No Credit Science/Physics"
    if req["credit_sfmt"]:
        if not (has_stv_credit or is_credit(math_grade)):
            return False, "No Credit Science/Math/Tech"

    # 5. Total Credits
    if total_credits < req["min_credits"]:
        return False, f"Min {req['min_credits']} Credits Required"

    return True, "OK"

# --- MAIN FLOW ---
if st.sidebar.button("Check Eligibility"):
    eligible = []
    for _, row in reqs_df.iterrows():
        ok, _ = check_eligibility(row)
        if ok:
            eligible.append(row["course_ID"])

    st.session_state["eligible_ids"] = eligible
    st.session_state["has_checked"] = True

if st.session_state.get("has_checked", False):

    eligible_ids = st.session_state["eligible_ids"]

    if not eligible_ids:
        st.warning("No eligible courses found based on these results.")
    else:
        st.success(f"You are eligible for {len(eligible_ids)} courses!")

        result_df = courses_df[courses_df["course_ID"].isin(eligible_ids)]

        st.dataframe(
            result_df[["course", "field", "department"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("### 📍 Course Locations")

        course_names = result_df["course"].unique()
        selected_course = st.selectbox(
            "Select a course to view campuses:",
            course_names
        )

        if selected_course:
            sel_id = (
                result_df[result_df["course"] == selected_course]
                .iloc[0]["course_ID"]
            )

            poly_ids = links_df[
                links_df["course_ID"] == sel_id
            ]["institution_ID"]

            final_polys = polys_df[
                polys_df["institution_ID"].isin(poly_ids)
            ]

            if not final_polys.empty:
                st.table(
                    final_polys[["institution_name", "State", "category"]]
                )
            else:
                st.info("Location data pending.")

else:
    st.info("👈 Enter your results and click Check Eligibility")
