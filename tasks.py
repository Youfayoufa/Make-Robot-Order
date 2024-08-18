from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    """
    browser.configure(
        slowmo=100,
    )
    get_orders()
    orders = get_orders()
    open_the_order_website()
    fill_the_order_form(orders)
    archive_receipts()
    
    

def get_orders():
    """Downloads the order csv file from the provided URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    return read_csv()


def read_csv():
    """Reads the csv files"""
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])
    return orders


def open_the_order_website():
    """Opens the order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")



def close_annoying_modal():
    """Closes the annoying modal that pops up when you open the robot order website"""
    page = browser.page()
    page.click("button:text('OK')")



def check_error(order_number):
    """Ckecks if a locator exists and acts accordingly"""
    page = browser.page()

    order_selector = "#order"
    is_order_visible = True

    while is_order_visible:
        page.click("#order")
        is_order_visible = page.locator(order_selector).is_visible()    

    pdf_file = save_receipt_as_pdf(order_number)
    screenshot_file = take_robot_screenshot(order_number)
    add_screenshot_to_pdf_file(pdf_file,screenshot_file)
    page.click("#order-another")




def save_receipt_as_pdf(order_number):
    """Saves the receipt as a pdf file"""
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, "output/receipts/"+str(order_number)+"_receipt.pdf")
    pdf_file = "output/receipts/"+str(order_number)+"_receipt.pdf"
    return str(pdf_file)



def take_robot_screenshot(order_number):
    """Takes a screenshot of the ordered robot"""
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path= "output/receipts/"+str(order_number)+"_screenshot.png")
    screenshot_file = "output/receipts/"+str(order_number)+"_screenshot.png"
    return str(screenshot_file)



def add_screenshot_to_pdf_file(pdf_file, screenshot_file):
    """Adds the screenshot of the robot to the receipt"""
    pdf = PDF()
    list_of_files = [
        pdf_file+":2-10, 15",
        screenshot_file+":align=center",
    ]
    pdf.add_files_to_pdf(
        files = list_of_files,
        target_document = str(pdf_file),
        append=True
    )



def fill_the_order_form(orders):
    """Fills the order form and click on 'order' button"""
    page = browser.page()

    for row in orders:

        if page.locator("button:text('Yep')").is_visible():
            close_annoying_modal()
        else:
            page.select_option("#head", str(row["Head"]))
            page.click("#id-body-"+str(row["Body"]))
            page.get_by_placeholder("Enter the part number for the legs").fill(str(row["Legs"]))
            page.fill("#address", str(row["Address"]))
            
            order_number = row["Order number"]

            check_error(order_number)


def archive_receipts():
    """Archives all the receipts into a zip file"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip", recursive=True)

    




        




            
            

