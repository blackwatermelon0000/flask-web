import os
import unittest
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

def get_driver():
    options = Options()
    options.add_argument("--headless")           # REQUIRED for Jenkins/EC2
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver

class TestStudentApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, 10)
        cls.base   = BASE_URL
        # Unique test credentials
        cls.username = "testuser_selenium"
        cls.email    = "selenium@test.com"
        cls.password = "Test@1234"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── Helper ──────────────────────────────────────────────────────────
    def login(self):
        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "login-btn").click()
        self.wait.until(EC.presence_of_element_located((By.ID, "add-student-btn")))

    def add_student(self, name=None):
        unique = uuid.uuid4().hex[:6]
        student_name = f"{name} {unique}" if name else f"Test Student {unique}"
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
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                student_name
            )
        )
        return student_name

    # ── TC-01  Page title ────────────────────────────────────────────────
    def test_01_homepage_title(self):
        """Homepage loads and has correct title"""
        self.driver.get(self.base)
        self.assertIn("StudentMS", self.driver.title)

    # ── TC-02  Homepage content ──────────────────────────────────────────
    def test_02_homepage_content(self):
        """Homepage displays hero heading and navigation links"""
        self.driver.get(self.base)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue("student" in body.lower() or "dashboard" in body.lower())
        self.assertIsNotNone(self.driver.find_element(By.LINK_TEXT, "Login"))
        self.assertIsNotNone(self.driver.find_element(By.LINK_TEXT, "Register"))

    # ── TC-03  Register page loads ───────────────────────────────────────
    def test_03_register_page_loads(self):
        """Register page has all required form fields"""
        self.driver.get(f"{self.base}/register")
        self.assertIsNotNone(self.driver.find_element(By.ID, "username"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "email"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "password"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "confirm_password"))

    # ── TC-04  Successful registration ──────────────────────────────────
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
        self.assertIn("login", self.driver.current_url)

    # ── TC-05  Duplicate registration ───────────────────────────────────
    def test_05_duplicate_registration(self):
        """Duplicate username shows error message"""
        self.driver.get(f"{self.base}/register")
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "email").send_keys("other@test.com")
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "confirm_password").send_keys(self.password)
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(0.5)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(
            "already exists" in body.lower() or "error" in body.lower()
        )

    # ── TC-06  Password mismatch ─────────────────────────────────────────
    def test_06_password_mismatch(self):
        """Mismatched passwords show error message"""
        self.driver.get(f"{self.base}/register")
        self.driver.find_element(By.ID, "username").send_keys("newuserxyz")
        self.driver.find_element(By.ID, "email").send_keys("newxyz@test.com")
        self.driver.find_element(By.ID, "password").send_keys("Password1")
        self.driver.find_element(By.ID, "confirm_password").send_keys("WrongPass")
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(0.5)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("do not match", body.lower())

    # ── TC-07  Successful login ──────────────────────────────────────────
    def test_07_successful_login(self):
        """Registered user can login"""
        self.login()
        self.assertIn("dashboard", self.driver.current_url)

    # ── TC-08  Invalid login ─────────────────────────────────────────────
    def test_08_invalid_login(self):
        """Wrong credentials show error message"""
        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.ID, "username").send_keys("wronguser")
        self.driver.find_element(By.ID, "password").send_keys("wrongpass")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(0.5)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("invalid", body.lower())

    # ── TC-09  Dashboard access without login ────────────────────────────
    def test_09_dashboard_redirect_without_login(self):
        """Accessing dashboard without login redirects to login page"""
        # First logout
        self.driver.get(f"{self.base}/logout")
        time.sleep(0.3)
        self.driver.get(f"{self.base}/dashboard")
        self.assertIn("login", self.driver.current_url)

    # ── TC-10  Dashboard loads after login ───────────────────────────────
    def test_10_dashboard_loads_after_login(self):
        """Dashboard displays correct content after login"""
        self.login()
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("dashboard", body.lower())
        self.assertIsNotNone(self.driver.find_element(By.ID, "add-student-btn"))

    # ── TC-11  Add student page loads ────────────────────────────────────
    def test_11_add_student_page_loads(self):
        """Add student form has all required fields"""
        self.login()
        self.driver.get(f"{self.base}/add_student")
        self.assertIsNotNone(self.driver.find_element(By.ID, "name"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "roll_no"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "email"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "course"))

    # ── TC-12  Add student successfully ──────────────────────────────────
    def test_12_add_student_successfully(self):
        """New student is saved and appears on dashboard"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        self.assertIn("dashboard", self.driver.current_url)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(student_name, body)

    # ── TC-13  Search student ─────────────────────────────────────────────
    def test_13_search_student(self):
        """Search returns matching students"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        self.driver.get(f"{self.base}/search?q={student_name.split()[0]}")
        self.wait.until(EC.presence_of_element_located((By.ID, "student-table")))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), student_name))
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(student_name, body)

    # ── TC-14  Edit student ───────────────────────────────────────────────
    def test_14_edit_student(self):
        """Student record can be edited"""
        self.login()
        student_name = self.add_student(name="Abdullah")
        self.driver.get(self.base + "/dashboard")
        edit_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//tr[td[contains(., '{student_name}')]]//a[contains(@class, 'btn-edit')]")
            )
        )
        edit_button.click()
        name_field = self.driver.find_element(By.ID, "name")
        name_field.clear()
        updated_name = "Abdullah Updated"
        name_field.send_keys(updated_name)
        self.driver.find_element(By.ID, "save-edit-btn").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), updated_name))
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(updated_name, body)

    # ── TC-15  Delete student ─────────────────────────────────────────────
    def test_15_delete_student(self):
        """Student record can be deleted"""
        self.login()
        student_name = self.add_student()
        self.driver.get(f"{self.base}/dashboard")
        delete_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//tr[td[contains(., '{student_name}')]]//button[contains(@class, 'btn-delete')]")
            )
        )
        self.driver.execute_script("window.confirm = function(){ return true; }")
        delete_btn.click()
        self.wait.until_not(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), student_name))
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotIn(student_name, body)

    # ── TC-16  Logout ─────────────────────────────────────────────────────
    def test_16_logout(self):
        """User can logout and is redirected to login"""
        self.login()
        self.driver.get(f"{self.base}/logout")
        time.sleep(0.3)
        self.assertIn("login", self.driver.current_url)

if __name__ == "__main__":
    unittest.main(verbosity=2)
