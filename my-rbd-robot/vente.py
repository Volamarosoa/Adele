from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF

@task
def robot_spare_bin_python():
    """Insert the sales data for the week and export it as a PDF"""
    browser.configure(
        slowmo=100,
    )
    open_the_intranet_website()
    log_in()
    download_excel_file()
    fill_form_with_excel_data()
    collect_results()
    export_as_pdf()

def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")

def log_in():
    """Fills in the login form and clicks the 'Log in' button"""
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log in')")

def fill_and_submit_sales_form(sales_rep):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()

    page.fill("#firstname", sales_rep["First Name"])
    page.fill("#lastname", sales_rep["Last Name"])
    page.select_option("#salestarget", str(sales_rep["Sales Target"]))
    page.fill("#salesresult", str(sales_rep["Sales"]))
    page.click("text=Submit")

def download_excel_file():
    """Downloads excel file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/SalesData.xlsx", overwrite=True)

def fill_form_with_excel_data():
    """Read data from excel and fill in the sales form"""
    excel = Files()
    excel.open_workbook("SalesData.xlsx")
    worksheet = excel.read_worksheet_as_table("data", header=True)
    excel.close_workbook()

    for row in worksheet:
        fill_and_submit_sales_form(row)

def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="D:\Stage\my-rbd-robot\output\sales_summary.png")

def export_as_pdf():
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#sales-results").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "output/sales_results.pdf")


robot_spare_bin_python()


    #  public async Task RunRobotAsync(int robotId)
    #     {
    #         String _apiKey = "20985:1b2263ae5e0a0db4c72540988f194ac5764db65bf63eff3b436219b3e2d5a59fd8a004d99a1fc6f049f7a475374db218";

    #         var requestUrl = $"https://api.robocorp.com/v1/workspaces/{_apiKey}/robots/{robotId}/runs";
    #         var content = new StringContent(JsonConvert.SerializeObject(new { }), Encoding.UTF8, "application/json");
    #         var response = await _httpClient.PostAsync(requestUrl, content);

    #         if (!response.IsSuccessStatusCode)
    #         {
    #             throw new Exception($"Failed to run robot: {response.StatusCode}");
    #         }
    #     }