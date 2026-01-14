import unittest
import os
import pandas as pd
from src.engine import StudentProfile, check_eligibility

class TestAdmissionsEngine(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create a dummy requirements row for testing basic eligibility
        cls.base_req = {
            'min_credits': 3,
            'req_malaysian': 1,
            'pass_bm': 1,
            'pass_history': 1,
            'pass_eng': 0,
            'pass_math': 0,
            'no_colorblind': 0,
            'no_disability': 0,
            'req_male': 0,
            'req_female': 0
        }

    # --- TEST 1: The "Audit" (Finding the missing credit) ---
    def test_credit_calculation_completeness(self):
        """Test that EVERY supported subject is correctly counted as a credit."""
        all_subjects = [
            'bm', 'eng', 'hist', 'math', 'addmath', 
            'phy', 'chem', 'bio', 'sci', 'geo', 
            'acc', 'biz', 'econ', 'psv', 'lang', 
            'lit', 'rel', 'rc', 'cs', 'agro', 'srt'
        ]
        
        # Give a 'C' (Credit) for every single subject
        grades = {subj: 'C' for subj in all_subjects}
        
        student = StudentProfile(
            grades=grades,
            gender='Lelaki', nationality='Warganegara', 
            colorblind='Tidak', disability='Tidak'
        )
        
        # If this fails (e.g., gets 20 instead of 21), we know one subject is missing in engine.py
        self.assertEqual(student.credits, 21, f"Expected 21 credits, but counted {student.credits}. A subject is missing in the loop!")

    # --- TEST 2: Credit Boundary (C vs D) ---
    def test_credit_boundary_c_vs_d(self):
        """Test that C counts as credit, but D does not."""
        student = StudentProfile(
            grades={'math': 'C', 'hist': 'D', 'bm': 'C'}, # Should be 2 credits
            gender='Lelaki'
        )
        self.assertEqual(student.credits, 2, "C should count, D should not.")

    # --- TEST 3: High Credits but Failed Mandatory Subject ---
    def test_fail_bm_gatekeeper(self):
        """Student has 8 As but failed BM. Should be ineligible."""
        student = StudentProfile(
            grades={'bm': 'G', 'hist': 'A', 'math': 'A', 'eng': 'A', 'sci': 'A'},
            gender='Lelaki'
        )
        req = self.base_req.copy()
        req['pass_bm'] = 1 # Requirement: Must Pass BM
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Bahasa Melayu", reason)

    # --- TEST 4: Gender Constraint (Male Only) ---
    def test_male_only_requirement(self):
        """Female student applying for Male-only course."""
        student = StudentProfile(grades={'bm':'A', 'hist':'A'}, gender='Perempuan')
        req = self.base_req.copy()
        req['req_male'] = 1
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Lelaki", reason)

    # --- TEST 5: Gender Constraint (Female Only) ---
    def test_female_only_requirement(self):
        """Male student applying for Female-only course."""
        student = StudentProfile(grades={'bm':'A', 'hist':'A'}, gender='Lelaki')
        req = self.base_req.copy()
        req['req_female'] = 1
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Perempuan", reason)

    # --- TEST 6: Colorblindness ---
    def test_colorblind_blocker(self):
        """Colorblind student applying for Engineering (no colorblind allowed)."""
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Lelaki', 
            colorblind='Ya'
        )
        req = self.base_req.copy()
        req['no_colorblind'] = 1
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Buta Warna", reason)

    # --- TEST 7: Disability Check ---
    def test_disability_blocker(self):
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A'}, 
            gender='Lelaki', 
            disability='Ya'
        )
        req = self.base_req.copy()
        req['no_disability'] = 1
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("OKU", reason)

    # --- TEST 8: Specific Subject Credit (Math) ---
    def test_specific_credit_requirement(self):
        """Course requires CREDIT in Math, student only has PASS."""
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A', 'math': 'D'}, # D is Pass, not Credit
            gender='Lelaki'
        )
        req = self.base_req.copy()
        req['credit_math'] = 1
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Matematik", reason)

    # --- TEST 9: Minimum Credits Check ---
    def test_min_credits_fail(self):
        """Student has 2 credits, course needs 3."""
        student = StudentProfile(
            grades={'bm':'C', 'hist':'C', 'math': 'D', 'eng': 'E'}, # 2 Credits
            gender='Lelaki'
        )
        req = self.base_req.copy()
        req['min_credits'] = 3
        
        eligible, reason = check_eligibility(student, req)
        self.assertFalse(eligible)
        self.assertIn("Kredit", reason)

    # --- TEST 10: The "Perfect" Student (Control Group) ---
    def test_perfect_student(self):
        """Student matches all criteria perfectly."""
        student = StudentProfile(
            grades={'bm':'A', 'hist':'A', 'math':'A', 'eng':'A'},
            gender='Lelaki',
            colorblind='Tidak',
            disability='Tidak'
        )
        req = self.base_req.copy()
        
        eligible, reason = check_eligibility(student, req)
        self.assertTrue(eligible)

if __name__ == '__main__':
    unittest.main()
