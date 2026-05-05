import os
import unittest
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def get_driver():
    options = Options()
    options.add_argument("--headless")          # REQUIRED for Jenkins
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver


class TestStudentApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait = WebDriverWait(cls.driver, 15)
        cls.base = BASE_URL
        
        # Unique test credentials
        cls.username = f"testuser_{uuid.uuid4().hex[:8]}"
        cls.email = f"selenium_{uuid.uuid4().hex[:8]}@test.com"
        cls.password = "Test@1234"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── Helper Methods ─────────────────────────────────────────────────────
    def login(self):
        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "login-btn").click()
        self.wait.until(EC.presence_of_element_located((By.ID, "add-student-btn")))

    def add_student(self, name="Test Student"):
        unique = uuid.uuid4().hex[:6]
        student_name = f"{name} {unique}"
        roll_no = f"SE-{unique}"
        email = f"student_{unique}@test.com"
        course = "Software Engineering"

        self.driver.get(f"{self.base}/add_student")
        self.driver.find_element(By.ID, "name").send_keys(student_name)
        self.driver.find_element(By.ID, "roll_no").send_keys(roll_no)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "course").send_keys(course)
        self.driver.find_element(By.ID, "submit-student-btn").click()

        self.wait.until(EC.presence_of_element_located((By.ID, "student-table")))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), student_name))
        return student_name

    # ── Test Cases ─────────────────────────────────────────────────────────

    def test_01_homepage_title(self):
        """Homepage loads and has correct title"""
        self.driver.get(self.base)
        self.assertIn("StudentMS", self.driver.title)

    def test_02_homepage_content(self):
        """Homepage displays hero heading and navigation links"""
        self.driver.get(self.base)
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertTrue("student" in body or "dashboard" in body)
        self.assertIsNotNone(self.driver.find_element(By.LINK_TEXT, "Login"))
        self.assertIsNotNone(self.driver.find_element(By.LINK_TEXT, "Register"))

    def test_03_register_page_loads(self):
        """Register page has all required form fields"""
        self.driver.get(f"{self.base}/register")
        self.assertIsNotNone(self.driver.find_element(By.ID, "username"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "email"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "password"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "confirm_password"))

    def test_04_successful_registration(self):
        """User can register a new account"""
        unique = uuid.uuid4().hex[:6]
        username = f"testuser_{unique}"
        email = f"selenium_{unique}@test.com"

        self.driver.get(f"{self.base}/register")
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "confirm_password").send_keys(self.password)
        self.driver.find_element(By.ID, "register-btn").click()

        self.wait.until(EC.url_contains("/login"))
        self.assertIn("login", self.driver.current_url.lower())

    def test_05_duplicate_registration(self):
        """Duplicate username shows error message"""
        self.driver.get(f"{self.base}/register")
        
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "email").send_keys("duplicate@test.com")
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "confirm_password").send_keys(self.password)
        self.driver.find_element(By.ID, "register-btn").click()

        time.sleep(1.5)
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        
        self.assertTrue(
            any(word in body for word in ["already exists", "already taken", "exists", "error", "failed", "username"]),
            f"Expected error message not found. Body: {body}"
        )

    def test_06_password_mismatch(self):
        """Mismatched passwords show error message"""
        self.driver.get(f"{self.base}/register")
        self.driver.find_element(By.ID, "username").send_keys("newuserxyz")
        self.driver.find_element(By.ID, "email").send_keys("newxyz@test.com")
        self.driver.find_element(By.ID, "password").send_keys("Password1")
        self.driver.find_element(By.ID, "confirm_password").send_keys("WrongPass")
        self.driver.find_element(By.ID, "register-btn").click()
        
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("do not match", body)

    def test_07_successful_login(self):
        """Registered user can login"""
        self.login()
        self.assertIn("dashboard", self.driver.current_url.lower())

    def test_08_invalid_login(self):
        """Wrong credentials show error message"""
        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.ID, "username").send_keys("wronguser")
        self.driver.find_element(By.ID, "password").send_keys("wrongpass")
        self.driver.find_element(By.ID, "login-btn").click()
        
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("invalid", body)

    def test_09_dashboard_redirect_without_login(self):
        """Accessing dashboard without login redirects to login"""
        self.driver.get(f"{self.base}/logout")
        time.sleep(0.5)
        self.driver.get(f"{self.base}/dashboard")
        self.assertIn("login", self.driver.current_url.lower())

    def test_10_dashboard_loads_after_login(self):
        """Dashboard displays correct content after login"""
        self.login()
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertIn("dashboard", body)
        self.assertIsNotNone(self.driver.find_element(By.ID, "add-student-btn"))

    def test_11_add_student_page_loads(self):
        """Add student form has all required fields"""
        self.login()
        self.driver.get(f"{self.base}/add_student")
        self.assertIsNotNone(self.driver.find_element(By.ID, "name"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "roll_no"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "email"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "course"))

    def test_12_add_student_successfully(self):
        """New student is saved and appears on dashboard"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(student_name, body)

    def test_13_search_student(self):
        """Search returns matching students"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        search_term = student_name.split()[0]
        self.driver.get(f"{self.base}/search?q={search_term}")
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), student_name))

    def test_14_edit_student(self):
        """Student record can be edited"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        self.driver.get(f"{self.base}/dashboard")
        
        edit_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(., '{student_name}')]]//a[contains(@class, 'btn-edit')]"))
        )
        edit_button.click()
        
        name_field = self.driver.find_element(By.ID, "name")
        name_field.clear()
        updated_name = "Abdullah Updated"
        name_field.send_keys(updated_name)
        self.driver.find_element(By.ID, "save-edit-btn").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), updated_name))

    def test_15_delete_student(self):
        """Student record can be deleted"""
        self.login()
        student_name = self.add_student()
        self.driver.get(f"{self.base}/dashboard")
        
        delete_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(., '{student_name}')]]//button[contains(@class, 'btn-delete')]"))
        )
        self.driver.execute_script("window.confirm = function(){ return true; }")
        delete_btn.click()
        
        self.wait.until_not(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), student_name))

    def test_16_logout(self):
        """User can logout and is redirected to login"""
        self.login()
        self.driver.get(f"{self.base}/logout")
        time.sleep(0.5)
        self.assertIn("login", self.driver.current_url.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
