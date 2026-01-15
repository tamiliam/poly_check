import unittest
import sys
import os

# Add the parent directory (project root) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import StudentProfile, check_eligibility

class TestAdmissionsAudit(unittest.TestCase):

    def setUp(self):
        # Base Requirement Template (Standard TVET Req)
        self.base_req = {
            'min_credits': 3,
            'req_malaysian': 1,
            'pass_bm': 1,
            'pass_history': 1,
            # Defaults for others
            'pass_eng': 0, 'pass_math': 0,
            'no_colorblind': 0, 'no_disability': 0,
            'req_male': 0, 'req_female': 0
        }

    def verify_application(self, test_label, student, requirements, expected_result, expected_reason_keyword=None):
        """
        Custom helper to print an Audit Trail for each test.
        """
        print(f"\n🔹 TEST: {test_label}")
        print("=" * 60)
        
        # Run Engine
        is_eligible, audit_log = check_eligibility(student, requirements)

        # Print Audit Trail
        for i, check in enumerate(audit_log, 1):
            status_icon = "✅ PASS" if check['passed'] else "❌ FAIL"
            reason_str = f" >> {check['reason']}" if check['reason'] else ""
            print(f"   Step {i}: {check['label']:<30} : {status_icon}{reason_str}")
        
        print("-" * 60)
        print(f"   🏁 FINAL VERDICT: {'ELIGIBLE' if is_eligible else 'REJECTED'}")
        print("=" * 60)

        # --- ASSERTIONS ---
        if expected_result:
            self.assertTrue(is_eligible, f"[{test_label}] Expected ELIGIBLE but got REJECTED.")
        else:
            self.assertFalse(is_eligible, f"[{test_label}] Expected REJECTED but got ELIGIBLE.")
            
            if expected_reason_keyword:
                # Extract all failure reasons from the audit log
                failures = [item['reason'] for item in audit_log if not item['passed']]
                # Check if keyword is in ANY of the failure messages
                found = any(expected_reason_keyword in (f or "") for f in failures)
                
                if not found:
                    self.fail(f"[{test_label}] Expected failure reason containing '{expected_reason_keyword}', but got: {failures}")

    # --- TEST 1: The "Audit" (Finding the missing credit) ---
    def test_01_credit_calculation_completeness(self):
        print("\n🔹 TEST: Credit Calculation Completeness (Internal Unit Test)")
        all_subjects = [
            'bm', 'eng', 'hist', 'math', 'addmath', 'phy', 'chem', 'bio', 
            'sci', 'geo', 'acc', 'biz', 'econ', 'psv', 'lang', 'lit', 
            'rel', 'rc', 'cs', 'agro', 'srt'
        ]
        # Give a 'C' (Credit) for every single subject
        grades = {subj: 'C' for subj in all_subjects}
        
        student = StudentProfile(
            grades=grades, gender='Lelaki', nationality='Warganegara', 
            colorblind='Tidak', disability='Tidak'
        )
        
        # Check logic
        print(f"   Subjects Tested: {len(all_subjects)}")
        print(f"   Credits Counted: {student.credits}")
        
        self.assertEqual(student.credits, 21, f"Expected 21 credits, but counted {student.credits}. Missing subject in engine!")
        print("   ✅ PASS")

    # --- TEST 2: Credit Boundary (C vs D) ---
    def test_02_credit_boundary_c_vs_d(self):
        print("\n🔹 TEST: Credit Boundary (C vs D)")
        student = StudentProfile(
            grades={'math': 'C', 'hist': 'D', 'bm': 'C'}, # 2 Credits
            gender='Lelaki', nationality='Warganegara', 
            colorblind='Tidak', disability='Tidak'
        )
        print(f"   Math(C) + BM(C) + Hist(D) = {student.credits} Credits")
        self.assertEqual(student.credits, 2, "C should count, D should not.")
        print("   ✅ PASS")

    # --- TEST 3: High Credits but Failed Mandatory Subject ---
    def test_03_fail_bm_gatekeeper(self):
        student = StudentProfile(
            grades={'bm': 'G', 'hist': 'A', 'math': 'A', 'eng': 'A', 'sci': 'A'},
            gender='Lelaki', nationality='Warganegara', 
            colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        req['pass_bm'] = 1 
        
        self.verify_application("Fail BM Gatekeeper", student, req, False, "Gagal Bahasa Melayu")

    # --- TEST 4: Gender Constraint (Male Only) ---
    def test_04_male_only_requirement(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Perempuan', # <-- Fail
            nationality='Warganegara', colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        req['req_male'] = 1
        
        self.verify_application("Male Only Check", student, req, False, "Lelaki Sahaja")

    # --- TEST 5: Gender Constraint (Female Only) ---
    def test_05_female_only_requirement(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Lelaki', # <-- Fail
            nationality='Warganegara', colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        req['req_female'] = 1
        
        self.verify_application("Female Only Check", student, req, False, "Wanita Sahaja")

    # --- TEST 6: Colorblindness ---
    def test_06_colorblind_blocker(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Lelaki', nationality='Warganegara', 
            colorblind='Ya', # <-- Fail
            disability='Tidak'
        )
        req = self.base_req.copy()
        req['no_colorblind'] = 1
        
        # CHANGED: "Buta Warna" -> "rabun warna"
        self.verify_application("Colorblind Blocker", student, req, False, "rabun warna")

    # --- TEST 7: Disability Check ---
    def test_07_disability_blocker(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Lelaki', nationality='Warganegara', colorblind='Tidak',
            disability='Ya' # <-- Fail
        )
        req = self.base_req.copy()
        req['no_disability'] = 1
        
        # CHANGED: "Sihat" -> "Syarat fizikal"
        self.verify_application("Disability Blocker", student, req, False, "Syarat fizikal")

    # --- TEST 8: Specific Subject Credit (Math) ---
    def test_08_specific_credit_requirement(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A', 'math': 'D'}, # D is Pass, not Credit
            gender='Lelaki', nationality='Warganegara', colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        req['credit_math'] = 1
        
        self.verify_application("Specific Credit (Math)", student, req, False, "Kredit Matematik")

    # --- TEST 9: Minimum Credits Check ---
    def test_09_min_credits_fail(self):
        student = StudentProfile(
            grades={'bm':'C', 'hist':'C', 'math': 'D', 'eng': 'E'}, # 2 Credits
            gender='Lelaki', nationality='Warganegara', colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        req['min_credits'] = 3
        
        self.verify_application("Min Credits Fail", student, req, False, "Kredit")

    # --- TEST 10: The "Perfect" Student (Control Group) ---
    def test_10_perfect_student(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A', 'math':'A', 'eng':'A'},
            gender='Lelaki', nationality='Warganegara', colorblind='Tidak', disability='Tidak'
        )
        req = self.base_req.copy()
        
        self.verify_application("Perfect Student", student, req, True)

if __name__ == '__main__':
    unittest.main()