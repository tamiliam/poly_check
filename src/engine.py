# engine.py
# This file contains PURE logic. No Streamlit, no UI.

def is_pass(grade):
    return str(grade).strip() in ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E"]

def is_credit(grade):
    return str(grade).strip() in ["A+", "A", "A-", "B+", "B", "C+", "C"]

def is_active(value):
    s = str(value).strip().lower()
    return s in ['1', '1.0', 'true', 'yes', 'y']

class StudentProfile:
    def __init__(self, grades: dict, gender: str, nationality: str, colorblind: str, disability: str, other_tech: bool = False, other_voc: bool = False):
        self.grades = grades
        self.gender = gender
        self.nationality = nationality
        self.colorblind = colorblind
        self.disability = disability
        self.other_tech = other_tech
        self.other_voc = other_voc
        self.credits = self._calculate_credits()

    def _calculate_credits(self):
        count = sum(1 for g in self.grades.values() if is_credit(g))
        if self.other_tech: count += 1
        if self.other_voc: count += 1
        return count

def check_eligibility(student: StudentProfile, req: dict) -> tuple[bool, str]:
    # 1. Gatekeepers
    if student.nationality == "Bukan Warganegara" and is_active(req.get('req_malaysian')):
        return False, "Warganegara Malaysia Diperlukan"
    
    # 2. Demographics
    if is_active(req.get('req_male')) and student.gender == "Perempuan":
        return False, "Lelaki Sahaja"
    if is_active(req.get('req_female')) and student.gender == "Lelaki":
        return False, "Wanita Sahaja"
    if is_active(req.get('no_colorblind')) and student.colorblind == "Ya":
        return False, "Tidak Rabun Warna"
    if is_active(req.get('no_disability')) and student.disability == "Ya":
        return False, "Sihat Tubuh Badan"

    # 3. Mandatory Passes
    if is_active(req.get('pass_bm')) and not is_pass(student.grades.get('bm')): return False, "Gagal BM"
    if is_active(req.get('pass_history')) and not is_pass(student.grades.get('hist')): return False, "Gagal Sejarah"
    if is_active(req.get('pass_eng')) and not is_pass(student.grades.get('eng')): return False, "Gagal BI"
    if is_active(req.get('pass_math')) and not is_pass(student.grades.get('math')): return False, "Gagal Matematik"

    # 4. Mandatory Credits
    if is_active(req.get('credit_bm')) and not is_credit(student.grades.get('bm')): return False, "Tiada Kredit BM"
    if is_active(req.get('credit_math')) and not is_credit(student.grades.get('math')): return False, "Tiada Kredit Matematik"
    if is_active(req.get('credit_eng')) and not is_credit(student.grades.get('eng')): return False, "Tiada Kredit BI"
    
    # 5. Complex Grouping Logic
    # Grouping definitions (Science/Tech/Vocational)
    pure_science = ['bio', 'phy', 'chem', 'addmath']
    tech_subs = ['rc', 'cs']
    voc_subs = ['agro', 'srt']
    
    has_pure_science_pass = any(is_pass(student.grades.get(s)) for s in pure_science)
    has_tech_pass = any(is_pass(student.grades.get(s)) for s in tech_subs) or student.other_tech
    has_voc_pass = any(is_pass(student.grades.get(s)) for s in voc_subs) or student.other_voc
    
    # Logic for pass_stv (Sains/Teknikal/Vokasional)
    # Note: 'sci_gen' corresponds to Science (Umum)
    stv_pass = is_pass(student.grades.get('sci')) or has_pure_science_pass or has_tech_pass or has_voc_pass
    if is_active(req.get('pass_stv')) and not stv_pass: return False, "Gagal Subjek Sains/Teknikal"

    # 6. Minimum Credits Check
    try: min_c = int(float(req.get('min_credits', 0)))
    except: min_c = 0
    if student.credits < min_c: return False, f"Kredit Tidak Cukup ({student.credits}/{min_c})"

    return True, "OK"
