# tests/test_regression.py
import os
import unittest
import pandas as pd
from src.engine import StudentProfile, check_eligibility

class TestGoldenScenarios(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Load the source of truth ONCE
        try:
            cls.reqs = pd.read_csv(os.path.join("data", "requirements.csv"), encoding="latin1")
            # Index by course_id for easy lookup
            cls.reqs.set_index("course_id", inplace=True)
        except FileNotFoundError:
            raise unittest.SkipTest("requirements.csv not found")

    def get_req(self, course_id):
        # Helper to get a requirement row as a dict
        if course_id not in self.reqs.index:
            self.fail(f"Course ID {course_id} not found in CSV")
        return self.reqs.loc[course_id].to_dict()

    # --- SCENARIO 1: The "Perfect" Student ---
    # Should qualify for everything basically
    def test_golden_student_pass(self):
        student = StudentProfile(
            grades={
                'bm': 'A', 'hist': 'A', 'math': 'A', 'eng': 'A', 
                'sci': 'A', 'phy': 'A', 'chem': 'A' 
            },
            gender="Lelaki",
            nationality="Warganegara",
            colorblind="Tidak",
            disability="Tidak"
        )
        
        # Test against a known difficult course (e.g., POLY-DIP-001)
        rule = self.get_req("POLY-DIP-001")
        eligible, reason = check_eligibility(student, rule)
        self.assertTrue(eligible, f"Perfect student failed logic! Reason: {reason}")

    # --- SCENARIO 2: The "Colorblind" Student ---
    # Should fail courses with no_colorblind = 1
    def test_colorblind_restriction(self):
        student = StudentProfile(
            grades={'bm': 'A', 'hist': 'A', 'math': 'A'}, # Good grades
            gender="Lelaki",
            nationality="Warganegara",
            colorblind="Ya", # <--- The constraints
            disability="Tidak"
        )
        
        # POLY-DIP-001 usually requires no colorblindness
        rule = self.get_req("POLY-DIP-001")
        
        # Check if the rule actually enforces colorblindness in CSV
        if rule.get('no_colorblind') == 1:
            eligible, reason = check_eligibility(student, rule)
            self.assertFalse(eligible, "Colorblind student was accidentally passed!")
            self.assertIn("Rabun Warna", reason)

    # --- SCENARIO 3: The "Minimum Credit" Fail ---
    def test_min_credits(self):
        student = StudentProfile(
            # Only 1 credit (BM), others are passes (D/E)
            grades={'bm': 'A', 'hist': 'E', 'math': 'E', 'eng': 'E'}, 
            gender="Lelaki",
            nationality="Warganegara",
            colorblind="Tidak",
            disability="Tidak"
        )
        
        # Course requiring 3 credits
        rule = self.get_req("POLY-DIP-001") 
        eligible, reason = check_eligibility(student, rule)
        self.assertFalse(eligible, "Student with 1 credit passed a 3-credit course!")

if __name__ == '__main__':
    unittest.main()
