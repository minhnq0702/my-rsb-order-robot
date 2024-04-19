# -*- coding: utf-8 -*-
import csv
import os

from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive


ORDER_FILE_NAME = 'orders.csv'
ORDER_DATA_DIR = 'output/orders'

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    download_order_file()
    make_orders()
    # save_screenshot_of_ordered_robot()
    # embed_screenshot_to_pdf_receipt()
    # create_zip_archive_of_receipts_and_images()


def open_robot_order_website():
    """
    Opens the RobotSpareBin Industries Inc. website.
    """
    browser.configure(
        slowmo=100,
        screenshot="only-on-failure",
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_order_file():
    url = "https://robotsparebinindustries.com/orders.csv"
    http = HTTP()
    http.download(url, f"output/{ORDER_FILE_NAME}", overwrite=True)


def close_annoying_modal():
    page = browser.page()
    if page.locator("//div[@class='modal-dialog']").count() > 0:
        page.click("button:text('OK')")


def next_order():
    page = browser.page()
    page.click("button#order-another")


def make_orders():
    orders = []
    with open(f"output/{ORDER_FILE_NAME}", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            success = False

            # click on annoying modal if it appears
            close_annoying_modal()

            while not success:
                success = fill_the_form_and_submit(row)
            order_name = get_order_receipt_name()
            save_order_receipt_as_pdf(order_name)
            take_screenshot_of_ordered_robot(order_name)
            concat_pdf_and_image(order_name)
            next_order()
            orders.append(order_name)
    delete_old_image()
    archive_files(files=orders)



def fill_the_form_and_submit(order: dict):
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.click(f"input#id-body-{order['Body']}")
    page.fill("//input[@placeholder='Enter the part number for the legs']", order['Legs'])
    page.fill("input#address", order['Address'])
    page.click("button:text('Order')")

    if page.locator("div#receipt").count() > 0:
        print("Order successful!")
        return True

    elif page.locator("//div[@class='alert alert-danger']").count() > 0:
        print("Error occurred while ordering, skipping...")
        return False
    else:
        print("Unknown error occurred, skipping...")
        return False
    

def get_order_receipt_name():
    page = browser.page()
    try:
        order_receipt = page.locator("div#order-completion")
        order_id = order_receipt.locator("//p[@class='badge badge-success']").text_content()
    except:
        order_id = None
    return order_id or "_unknow"


def save_order_receipt_as_pdf(order_name: str) -> str:
    page = browser.page()
    order_receipt = page.locator("div#order-completion")
    pdf = PDF()
    order_receipt_file_name = f"{ORDER_DATA_DIR}/{order_name}.pdf"
    pdf.html_to_pdf(order_receipt.inner_html(), order_receipt_file_name)
    

def take_screenshot_of_ordered_robot(order_name: str):
    page = browser.page()
    robot_image = page.locator("div#robot-preview-image")
    robot_image.screenshot(path=f"{ORDER_DATA_DIR}/{order_name}.png", type='png')


def concat_pdf_and_image(order_name: str):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[
            # f"output/{order_name}.pdf",
            f"{ORDER_DATA_DIR}/{order_name}.png:align=center,width=50,height=100",
        ],
        target_document=f"{ORDER_DATA_DIR}/{order_name}.pdf",
        append=True,
    )


def delete_old_image():
    folder_path = ORDER_DATA_DIR
    file_extension = ".png"
    files = [file for file in os.listdir(folder_path) if file.endswith(file_extension)]
    for file in files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)


def archive_files(files=[]):
    if not files:
        return
    
    archive = Archive()
    archive.archive_folder_with_zip(
        folder=ORDER_DATA_DIR,
        archive_name="output/archive.zip",
    )


def odoo_robot_test():
    browser.configure(
        slowmo=1000,
    )
    browser.goto("https://task.mingne.dev")
    page = browser.page()
    page.fill("id=login", "minhnq.0702@gmail.com")
    page.fill("id=password", "Ynhucu0&0@")
    page.click("button:text('Log in')")
    page.click("//a[@data-menu-xmlid='contacts.menu_contacts']")
    # page.click("button:text(' Mới ')")
    page.click("div.d-none.d-xl-inline-flex.gap-1 > button")