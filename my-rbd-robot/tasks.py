from robocorp.tasks import task
from robocorp import browser
import time

@task
def minimal_task():
    """Insert the sales data for the week and export it as a PDF"""

@task
def robot_spare_bin_python():
    """Insert the sales data for the week and export it as a PDF"""
    open_the_intranet_website()
    log_in()
    check_login_success()

def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://www.vabf.almerys.com/CZ-J/0/valerys/")

def log_in():
    """Fills in the login form and clicks the 'Log in' button"""
    page = browser.page()
    page.fill("input[name='username']", "SAT201")  
    page.fill("input[name='password']", "Almerys0") 

    selector = "input[type='submit']" 
    page.wait_for_selector(selector, timeout=10000) 
    
    # Cliquer sur le bouton OK
    page.click(selector)

def check_login_success():
    """Checks if login was successful by waiting for a specific element"""
    page = browser.page()
    
    success_selector = "ul.topMenuIcons.floatLeft"    

    try:
        page.wait_for_selector(success_selector, timeout=30000) 
        print("Connexion réussie!")
    except:
        print("La connexion a échoué ou a pris trop de temps.")  

    collect_results()  
    time.sleep(3)

def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="./connexion.png")

print("Le script a démarré correctement.")
robot_spare_bin_python()
