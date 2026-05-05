import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

BASE_URL = "http://localhost:5000"

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
        time.sleep(0.5)

    # ── TC-01  Page title ────────────────────────────────────────────────
    def test_01_homepage_title(self):
        """Homepage loads and has correct title"""
        self.driver.get(self.base)
        self.assertIn("Student Management System", self.driver.title)

    # ── TC-02  Homepage content ──────────────────────────────────────────
    def test_02_homepage_content(self):
        """Homepage displays hero heading and navigation links"""
        self.driver.get(self.base)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Student Management System", body)
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
        self.driver.get(f"{self.base}/register")
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "email").send_keys(self.email)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "confirm_password").send_keys(self.password)
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(0.5)
        # Redirected to login with success message
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
        self.driver.get(f"{self.base}/add_student")
        self.driver.find_element(By.ID, "name").send_keys("Ali Hassan")
        self.driver.find_element(By.ID, "roll_no").send_keys("SE-2024-01")
        self.driver.find_element(By.ID, "email").send_keys("ali@test.com")
        self.driver.find_element(By.ID, "course").send_keys("Software Engineering")
        self.driver.find_element(By.ID, "submit-student-btn").click()
        time.sleep(0.5)
        self.assertIn("dashboard", self.driver.current_url)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Ali Hassan", body)

    # ── TC-13  Search student ─────────────────────────────────────────────
    def test_13_search_student(self):
        """Search returns matching students"""
        self.login()
        self.driver.get(f"{self.base}/search?q=Ali")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Ali Hassan", body)

    # ── TC-14  Edit student ───────────────────────────────────────────────
    def test_14_edit_student(self):
        """Student record can be edited"""
        self.login()
        self.driver.get(self.base + "/dashboard")
        time.sleep(0.5)
        # Click first Edit button
        edit_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-edit")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(0.5)
            name_field = self.driver.find_element(By.ID, "name")
            name_field.clear()
            name_field.send_keys("Ali Hassan Updated")
            self.driver.find_element(By.ID, "save-edit-btn").click()
            time.sleep(0.5)
            body = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertIn("updated successfully", body.lower())
        else:
            self.skipTest("No students to edit")

    # ── TC-15  Delete student ─────────────────────────────────────────────
    def test_15_delete_student(self):
        """Student record can be deleted"""
        self.login()
        self.driver.get(f"{self.base}/dashboard")
        time.sleep(0.5)
        rows_before = self.driver.find_elements(By.CLASS_NAME, "student-row")
        if rows_before:
            delete_btn = self.driver.find_elements(By.CLASS_NAME, "btn-delete")[0]
            # Dismiss confirm dialog automatically
            self.driver.execute_script(
                "window.confirm = function(){ return true; }"
            )
            delete_btn.click()
            time.sleep(0.5)
            body = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertIn("deleted", body.lower())
        else:
            self.skipTest("No students to delete")

    # ── TC-16  Logout ─────────────────────────────────────────────────────
    def test_16_logout(self):
        """User can logout and is redirected to login"""
        self.login()
        self.driver.get(f"{self.base}/logout")
        time.sleep(0.3)
        self.assertIn("login", self.driver.current_url)

if __name__ == "__main__":
    unittest.main(verbosity=2)