import pandas as pd

# --- HELPER FUNCTIONS ---
def is_pass(grade):
    """Returns True if grade is A+ through E (Pass)."""
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]

def is_credit(grade):
    """Returns True if grade is A+ through C (Credit)."""
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_attempted(grade):
    """Returns True if grade is A+ through G (Attempted/Taking). Excludes TH/None."""
    # We assume 'G' is the lowest valid grade that proves they 'did' the subject.
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]

def safe_int(val, default=0):
    """
    Robustly converts inputs to int. 
    Handles 'NaN', floats, strings like '1.0', and empty strings.
    """
    try:
        # Check for pandas NaN (which is a float)
        if pd.isna(val):
            return default
        # Convert float '1.0' to int 1
        return int(float(val))
    except (ValueError, TypeError):
        return default

class StudentProfile:
    def __init__(self, grades, gender, nationality, colorblind, disability, other_tech=False, other_voc=False):
        self.grades = grades
        self.gender = gender
        self.nationality = nationality
        self.colorblind = colorblind
        self.disability = disability
        self.other_tech = other_tech
        self.other_voc = other_voc
        
        # Calculate Counts
        self.credits = 0
        self.passes = 0
        
        for subj, grade in grades.items():
            if is_credit(grade):
                self.credits += 1
            if is_pass(grade):
                self.passes += 1

def check_eligibility(student, req):
    """
    Checks if a student meets the requirements.
    Returns: (bool_status, list_of_audit_logs)
    """
    audit = []
    
    # --- HELPER TO LOG CHECKS ---
    def check(label, condition, fail_msg=None):
        if condition:
            audit.append({"label": label, "passed": True, "reason": None})
            return True
        else:
            audit.append({"label": label, "passed": False, "reason": fail_msg})
            return False

    # --- 1. GATEKEEPERS (Fail Fast) ---
    if safe_int(req.get('req_malaysian')) == 1:
        if not check("Warganegara", student.nationality == 'Warganegara', "Hanya untuk Warganegara"):
            return False, audit

    if safe_int(req.get('req_male')) == 1:
        if not check("Jantina (Lelaki)", student.gender == 'Lelaki', "Lelaki Sahaja"): return False, audit
    if safe_int(req.get('req_female')) == 1:
        if not check("Jantina (Wanita)", student.gender == 'Perempuan', "Wanita Sahaja"): return False, audit

    if safe_int(req.get('no_colorblind')) == 1:
        if not check("Bebas Buta Warna", student.colorblind == 'Tidak', "Tidak boleh rabun warna"): return False, audit
    
    if safe_int(req.get('no_disability')) == 1:
        if not check("Sihat Tubuh Badan", student.disability == 'Tidak', "Syarat fizikal tidak dipenuhi"): return False, audit

    g = student.grades # Short alias

    # --- 2. TVET SPECIAL (3M) ---
    # FIX: Use safe_int to handle cases where 3m_only is loaded as float 1.0
    is_3m = safe_int(req.get('3m_only')) == 1
    
    if is_3m:
        # Check if they actually attempted BM and Math (At least Grade G)
        has_bm = is_attempted(g.get('bm'))
        has_math = is_attempted(g.get('math'))
        
        if check("Syarat 3M (BM & Math)", has_bm and has_math, "Perlu sekurang-kurangnya Gred G dalam BM dan Matematik"):
            return True, audit
        else:
            return False, audit

    # --- 3. ACADEMIC CHECKS ---
    passed_academics = True

    # -- Specific Subjects --
    if safe_int(req.get('pass_bm')) == 1:
        if not check("Lulus BM", is_pass(g.get('bm')), "Gagal Bahasa Melayu"): passed_academics = False
    if safe_int(req.get('credit_bm')) == 1:
        if not check("Kredit BM", is_credit(g.get('bm')), "Tiada Kredit Bahasa Melayu"): passed_academics = False

    if safe_int(req.get('pass_history')) == 1:
        if not check("Lulus Sejarah", is_pass(g.get('hist')), "Gagal Sejarah"): passed_academics = False

    if safe_int(req.get('pass_eng')) == 1:
        if not check("Lulus BI", is_pass(g.get('eng')), "Gagal Bahasa Inggeris"): passed_academics = False
    if safe_int(req.get('credit_english')) == 1:
        if not check("Kredit BI", is_credit(g.get('eng')), "Tiada Kredit Bahasa Inggeris"): passed_academics = False

    if safe_int(req.get('pass_math')) == 1:
        if not check("Lulus Matematik", is_pass(g.get('math')), "Gagal Matematik"): passed_academics = False
    if safe_int(req.get('credit_math')) == 1:
        if not check("Kredit Matematik", is_credit(g.get('math')), "Tiada Kredit Matematik"): passed_academics = False

    # -- Group Logic (Science/Tech) --
    pure_sci = [g.get('phy'), g.get('chem'), g.get('bio')]
    all_sci = pure_sci + [g.get('sci')]
    tech_subjs = [g.get('rc'), g.get('cs'), g.get('agro'), g.get('srt')]
    if student.other_tech: tech_subjs.append('C')

    def has_pass(grade_list): return any(is_pass(x) for x in grade_list)
    def has_credit(grade_list): return any(is_credit(x) for x in grade_list)

    if safe_int(req.get('pass_math_sci')) == 1:
        cond = is_pass(g.get('math')) or has_pass(pure_sci)
        if not check("Lulus Matemaik ATAU Sains Tulen", cond, "Perlu Lulus Math/Sains Tulen"): passed_academics = False

    if safe_int(req.get('pass_science_tech')) == 1:
        cond = has_pass(all_sci) or has_pass(tech_subjs)
        if not check("Lulus Sains ATAU Teknikal", cond, "Perlu Lulus Sains/Teknikal"): passed_academics = False

    if safe_int(req.get('credit_math_sci')) == 1:
        cond = is_credit(g.get('math')) or has_credit(pure_sci)
        if not check("Kredit Matematik ATAU Sains Tulen", cond, "Perlu Kredit Math/Sains Tulen"): passed_academics = False

    if safe_int(req.get('credit_math_sci_tech')) == 1:
        cond = is_credit(g.get('math')) or has_credit(all_sci) or has_credit(tech_subjs)
        if not check("Kredit Math/Sains/Teknikal", cond, "Perlu Kredit Math/Sains/Teknikal"): passed_academics = False

    if safe_int(req.get('pass_stv')) == 1:
        cond = has_pass(all_sci) or has_pass(tech_subjs) or student.other_voc
        if not check("Aliran Sains/Vokasional", cond, "Perlu Lulus Sains/Vokasional"): passed_academics = False

    # -- General Counters --
    min_c = safe_int(req.get('min_credits'), 0)
    if min_c > 0:
        if not check(f"Minimum {min_c} Kredit", student.credits >= min_c, f"Hanya {student.credits} Kredit (Perlu {min_c})"): passed_academics = False

    min_p = safe_int(req.get('min_pass'), 0)
    if min_p > 0:
        if not check(f"Minimum {min_p} Lulus", student.passes >= min_p, f"Hanya {student.passes} Lulus"): passed_academics = False

    return passed_academics, audit