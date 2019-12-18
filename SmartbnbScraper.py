from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys, time, json
from datetime import datetime
from bs4 import BeautifulSoup

# Still haven't gotten to do final testing yet!
# Running from command line is being a little weird

# SMARTBNB SCRAPER for python3
# Scrapes data from smartbnb.io and saves to .json
#
# Requires:
#   selenium, beautifulsoup4
# Must have the proper selenium chrome driver installed
#   Place that .exe in the same directory as the python script
#   and you're good to go
#
# Run this script in your IDE or via command line
#   $python -m /path/to/SmartbnbScraper

"""
TODO
- run headless
- look into checkouts once their site is fixed
"""

def run():
    # Flags
    print_flag = True
    json_flag = True
    csv_flag = True
    
    # Init
    browser = webdriver.Chrome()
    url = "https://my.smartbnb.io/"
    browser.get(url)
    data = []
    json_path = "data.json"
    csv_path = "data.csv"

    # Login
    if len(sys.argv) != 3:
        print("Improper arguments given: should be <username> <password>")
        return
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        print("USERNAME: " + username)
        print("PASSWORD: " + password)
        doLogin(browser, username, password)

    # Go through the Check-ins and Check-outs pages
    data = perusePages(browser, data, print_flag)

    print("\nFinished scraping! Saving data...")

    if (json_flag):
        saveJson(data, json_path)
    if (csv_flag):
        saveCsv(data, csv_path)
    
    print("\nCompleted.")
        
def doLogin(browser, username, password):
    # Check that the page has loaded and the login fields are actually there (45 second timeout)
    WebDriverWait(browser, 45).until(EC.presence_of_element_located((By.CLASS_NAME, "mat-input-element")))

    # Locate the username and pw fields
    fields = browser.find_elements_by_class_name("mat-input-element")
    fields[0].send_keys(username)
    fields[1].send_keys(password)

    # Click the submit button
    submitButton = browser.find_element_by_class_name("login__btn-submit")
    submitButton.click()

def countPages(browser):
    # Reads the pagination button and finds the last numerical label
    # This lets us know how many pages we want to scrape
    buttonLabels = browser.find_elements_by_class_name("mat-button-toggle-label-content")
    lastPageLabel = buttonLabels[len(buttonLabels)-2] # exclude the last label, which is the > button
    lastPageNumber = int(lastPageLabel.get_attribute('innerHTML'))
    return lastPageNumber

def perusePages(browser, data, print_flag):
    try:
        # If we can't find a "checkin__container" element after 45 seconds of loading, fail
        WebDriverWait(browser, 120).until(EC.presence_of_element_located((By.CLASS_NAME, "checkin__container")))
    except:
        print("Cannot load page.")
        return
    
    # Find how many Check-ins pages there are
    numPages = countPages(browser)
    print(str(numPages) + " PAGES")
    
    # Iterate through Check-ins pages
    print("ITERATING THROUGH PAGES")
    isCheckin = True
    prev0thRow = None
    for page in range(numPages):
        data, prev0thRow = singlePage(browser, data, isCheckin, page, prev0thRow, print_flag)
    
    # Switch to Check-outs tab
    switchTabs(browser)
    
    # Find how many Check-outs pages there are
    numPages = countPages(browser)
    print(str(numPages) + " PAGES")

    # Iterate through Check-outs pages
    print("ITERATING THROUGH PAGES")
    isCheckin = False
    for page in range(numPages):
        data, prev0thRow = singlePage(browser, data, isCheckin, page, prev0thRow, print_flag)
    
    return data

def singlePage(browser, data, isCheckin, page, prev0thRow, print_flag):
    if (print_flag):
        print("\nPAGE " + str(page+1)) # Add 1 to output because 0-indexing

    # Grab our row elements
    rows = browser.find_elements_by_class_name("checkin__container")

    # Wait until the rows we've grabbed are actually new rows
    while (prev0thRow != None and prev0thRow == rows[0]):
        rows = browser.find_elements_by_class_name("checkin__container")

    # Record our current 0th row for future reference
    prev0thRow = rows[0]
    
    # Extract our data from our rows
    for row in rows:
        row_data = getDataFromRow(row.get_attribute('innerHTML'), isCheckin, print_flag)
        if (len(row_data) > 0):
            data.append(row_data)
        
    # Navigate to the next page
    nextPage(browser)
        
    return data, prev0thRow

def nextPage(browser):
    # Finds the > button and clicks it
    paginators = browser.find_elements_by_class_name("paginator__prevnext")
    if (paginators[1].get_attribute("value") == "forward"):
        paginators[1].click()

def switchTabs(browser):
    tab = browser.find_element_by_id("mat-tab-label-0-1")
    tab.click()
    print("Switched tab")
    
def getDataFromRow(row, isCheckin, print_flag):
    # Our final storage container
    row_data = {}
    
    # Parse html via the lovely Python package Beautiful Soup 4
    soup = BeautifulSoup(row, 'html.parser')

    # The names are stored in <strong> tags, and are the only <strong> tags on the page
    nametag = soup.find('strong')
    row_data["Name"] = nametag.get_text()

    # We find the rest of the data in <span> tags
    # If anything in thie program breaks, it will probably be this
    # This section is very dependent on how they structure their html, and won't
    #   work if they shift things around
    # Call print(soup.prettify()) to see the structure of the row html, which
    #   should help with rewriting this section if needed in the future
    spans = soup.find_all('span')
    row_data["Room ID"] = spans[0].get_text()
    row_data["Listing ID"] = spans[1].get_text()
    row_data["RawDates"] = spans[3].get_text()

    # Extrapolate from current data
    date_obj = datetime.strptime(row_data["RawDates"], "%b %d %Y - %H:%M")
    if notToday(date_obj):
        return {}
    row_data["Time"] = date_obj.strftime("%H:%M")
    row_data["Checkin"] = isCheckin
    row_data["Checkout"] = not isCheckin
    if (isCheckin):
        row_data["Late Checkout"] = False
        if (int(date_obj.hour) < 15):
            row_data["Early Checkin"] = True
        else:
            row_data["Early Checkin"] = False
    else:
        row_data["Early Checkin"] = False
        if (int(date_obj.hour) > 11):
            row_data["Late Checkout"] = True
        else:
            row_data["Late Checkout"] = False
    

    # Display each row we grab
    if (print_flag):
        print("{:20} | {:20} | {:12} | {}".format(row_data["Name"], row_data["Room ID"],
                                                  row_data["Listing ID"], row_data["Time"]))

    # Return json
    return row_data
        
def notToday(date_obj):
    return date_obj.date() != datetime.today().date()

def saveJson(data, json_path):
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)
    print("Wrote json.")

def saveCsv(data, csv_path):
    if (len(data) > 0):
        with open(csv_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(data[0].keys())
            for row in data:
                csv_writer.writerow(row.values())
    print("Wrote csv.")
    

if __name__ == "__main__":
    run()

