import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Audit Tool", page_icon="🕵️‍♀️")

st.title("🕵️‍♀️ Requirement.csv Forensic Audit")

# --- LOAD DATA ---
try:
    reqs = pd.read_csv("requirements.csv", encoding="latin1")
    courses = pd.read_csv("courses.csv", encoding="latin1")
    
    # Clean headers
    reqs.columns = [c.strip().lower() for c in reqs.columns]
    courses.columns = [c.strip().lower() for c in courses.columns]
    
    # Clean IDs
    reqs['course_id'] = reqs['course_id'].astype(str).str.strip()
    courses['course_id'] = courses['course_id'].astype(str).str.strip()
    
    st.success("Files loaded. Running logic checks...")
    
except Exception as e:
    st.error(f"Could not load files: {e}")
    st.stop()

# --- AUDIT FUNCTIONS ---
issues = []

def log_issue(cid, issue_type, details):
    issues.append({"Course ID": cid, "Issue Type": issue_type, "Details": details})

def is_active(val):
    return str(val).strip().lower() in ['1', '1.0', 'true', 'yes']

# --- RUN CHECKS ---
for index, row in reqs.iterrows():
    cid = row['course_id']
    
    # 1. ORPHAN CHECK
    # Does this ID exist in the Courses table?
    if cid not in courses['course_id'].values:
        log_issue(cid, "Orphan Record", "ID exists in Requirements but NOT in Courses.csv")

    # 2. LOGIC LADDER CHECK (Math)
    # If you require Credit, you implicitly require Pass.
    if is_active(row.get('credit_math')) and not is_active(row.get('pass_math')):
        log_issue(cid, "Logic Conflict (Math)", "Requires Credit Math (1) but Pass Math is (0).")

    # 3. LOGIC LADDER CHECK (English)
    if is_active(row.get('credit_eng')) and not is_active(row.get('pass_eng')):
        log_issue(cid, "Logic Conflict (Eng)", "Requires Credit English (1) but Pass English is (0).")

    # 4. LOGIC LADDER CHECK (BM)
    if is_active(row.get('credit_bm')) and not is_active(row.get('pass_bm')):
        log_issue(cid, "Logic Conflict (BM)", "Requires Credit BM (1) but Pass BM is (0).")

    # 5. THE "IMPOSSIBLE" CREDIT
    # min_credits is High, but specific subjects are Low
    try:
        min_c = int(float(row.get('min_credits', 0)))
    except:
        min_c = 0
    
    # Count how many specific credits are demanded
    demanded = 0
    for col in ['credit_bm', 'credit_eng', 'credit_math', 'credit_stv', 'credit_sf']:
        if is_active(row.get(col)): demanded += 1
        
    if min_c > 3 and demanded == 0:
        log_issue(cid, "Vague Requirement", f"Requires {min_c} credits, but lists NO specific subjects.")

# --- DISPLAY REPORT ---
if issues:
    st.error(f"Found {len(issues)} Potential Inconsistencies")
    df_issues = pd.DataFrame(issues)
    st.dataframe(df_issues, use_container_width=True)
    
    # Download option
    csv = df_issues.to_csv(index=False).encode('utf-8')
    st.download_button("Download Audit Report", data=csv, file_name="audit_report.csv", mime="text/csv")
else:
    st.balloons()
    st.success("🎉 Incredible! No logical inconsistencies found.")
