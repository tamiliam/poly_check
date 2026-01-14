import pandas as pd

# --- HELPER FUNCTIONS ---
def is_pass(grade):
    """Returns True if grade is A+ through E (Pass)."""
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]

def is_credit(grade):
    """Returns True if grade is A+ through C (Credit)."""
    return grade in ["A+", "A", "A-", "B+", "B", "C+", "C"]

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
    Checks if a student meets the requirements for a specific course.
    Returns: (bool, reason_if_failed)
    """
    
    # 1. 3M / SPM Saja Check (TVET Special)
    is_3m = str(req.get('3m_only', '0')).strip() == '1'

    # --- A. GATEKEEPERS (The absolute "Must Haves") ---
    
    # Nationality
    if req.get('req_malaysian') == 1 and student.nationality != 'Warganegara':
        return False, "Warganegara Sahaja"

    # Gender
    if req.get('req_male') == 1 and student.gender != 'Lelaki':
        return False, "Lelaki Sahaja"
    if req.get('req_female') == 1 and student.gender != 'Perempuan':
        return False, "Wanita Sahaja"

    # Health
    if req.get('no_colorblind') == 1 and student.colorblind == 'Ya':
        return False, "Tidak Rabun Warna"
    
    if req.get('no_disability') == 1 and student.disability == 'Ya':
        return False, "Sihat Tubuh Badan"

    # IF 3M Only, we SKIP the academic checks below
    if is_3m:
        return True, "Layak (Syarat 3M)"

    # --- B. ACADEMIC CHECKS ---

    g = student.grades # Short alias

    # --- PRIORITY 1: SPECIFIC SUBJECTS (Check these FIRST) ---
    
    # Bahasa Melayu
    if req.get('pass_bm') == 1 and not is_pass(g.get('bm')): return False, "Gagal BM"
    if req.get('credit_bm') == 1 and not is_credit(g.get('bm')): return False, "Tiada Kredit BM"

    # Sejarah
    if req.get('pass_history') == 1 and not is_pass(g.get('hist')): return False, "Gagal Sejarah"

    # English
    if req.get('pass_eng') == 1 and not is_pass(g.get('eng')): return False, "Gagal BI"
    if req.get('credit_english') == 1 and not is_credit(g.get('eng')): return False, "Tiada Kredit BI"

    # Math
    if req.get('pass_math') == 1 and not is_pass(g.get('math')): return False, "Gagal Matematik"
    if req.get('credit_math') == 1 and not is_credit(g.get('math')): return False, "Tiada Kredit Matematik"
    
    # --- PRIORITY 2: GROUP LOGIC ---

    # Define Subject Groups
    pure_sci = [g.get('phy'), g.get('chem'), g.get('bio')]
    all_sci = pure_sci + [g.get('sci')]
    tech_subjs = [g.get('rc'), g.get('cs'), g.get('agro'), g.get('srt')]
    if student.other_tech: tech_subjs.append('C') 

    # Helpers
    def has_pass(grade_list): return any(is_pass(x) for x in grade_list)
    def has_credit(grade_list): return any(is_credit(x) for x in grade_list)

    # Logic: pass_math_sci (Math OR Pure Sciences)
    if req.get('pass_math_sci') == 1:
        math_ok = is_pass(g.get('math'))
        sci_ok = has_pass(pure_sci)
        if not (math_ok or sci_ok):
            return False, "Wajib Lulus Matematik ATAU Sains Tulen"

    # Logic: pass_science_tech (GenScience OR PureSci OR Technical)
    if req.get('pass_science_tech') == 1:
        sci_ok = has_pass(all_sci)
        tech_ok = has_pass(tech_subjs)
        if not (sci_ok or tech_ok):
            return False, "Wajib Lulus Sains ATAU Teknikal"

    # Logic: credit_math_sci (Credit Math OR Pure Sciences)
    if req.get('credit_math_sci') == 1:
        math_ok = is_credit(g.get('math'))
        sci_ok = has_credit(pure_sci)
        if not (math_ok or sci_ok):
             return False, "Wajib Kredit Matematik ATAU Sains Tulen"

    # Logic: credit_math_sci_tech (Credit Math OR Pure/Gen Sci OR Technical)
    if req.get('credit_math_sci_tech') == 1:
        math_ok = is_credit(g.get('math'))
        sci_ok = has_credit(all_sci)
        tech_ok = has_credit(tech_subjs)
        if not (math_ok or sci_ok or tech_ok):
             return False, "Wajib Kredit Matematik ATAU Sains ATAU Teknikal"

    # Logic: Polytechnic Legacy Group (pass_stv)
    if req.get('pass_stv') == 1:
        if not (has_pass(all_sci) or has_pass(tech_subjs) or student.other_voc):
            return False, "Tiada Lulus Sains/Teknikal/Vokasional"

    # --- PRIORITY 3: GENERAL COUNTERS (Check these LAST) ---
    
    # Minimum Credits (Total)
    min_c = int(req.get('min_credits', 0))
    if student.credits < min_c:
        return False, f"Kurang Kredit (Perlu {min_c})"
        
    # Minimum Passes (Total)
    min_p = int(req.get('min_pass', 0))
    if student.passes < min_p:
        return False, f"Kurang Lulus (Perlu {min_p} subjek)"

    return True, "Layak"