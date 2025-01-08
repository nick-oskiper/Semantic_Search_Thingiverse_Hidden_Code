# Only the main function of this web scraper is shown. Because it was part of another repository, I put the README below.
# I also left in the imports.

# This project is meant to scrape object details from the thingiverse website.
# It automatically downloads all files associated with the object to the downloaded_files folder, and extracts all necessary information to the thing_details.csv file.
# The user has an option of either inputing specific ids to be scraped (an example would be 12345,54312,14255), entering a search query and scraping all items that show up indefinetely, or inputting nothing and scraping the main webpage.
# For git purposes, files that are larger than 25 mb are skipped. There is also an option to limit number of files downloaded (automatically set to 15 but can be turned off)
# There are two classes and a main.py file. The first class has all thing_details (thing_details.py) that are needed to gather info about the thing for export to csv file.
# The second class has all scraping functions (thingiverse_scraper.py) that are performed to gather these details.
# It also included functions to clear downloads, export details, and push to git.
# The main function is simple and just asks for the user inputs (specific thing ids or search query).
# The thing_details.csv file contains the following 'thing' information in order:
# id, url, collect count, like count, first page comments (separated by ;), summary, make links, remixes links, apps
# This file (as well as the download_files folder) can be cleared to load in completely new information and start fresh.
# It can also be beautified to tabular form using the following link for free (https://www.convertcsv.com/csv-viewer-editor.htm)

# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.firefox import GeckoDriverManager
# from bs4 import BeautifulSoup
# import time
# import shutil
# import os
# import csv
# import git
# from thing_details import ThingDetails
# import requests
# from selenium.common.exceptions import TimeoutException, WebDriverException
# class ThingiverseScraper:
#     def run(self, specific_ids=None, search_query=None, max_retries=3):
#         """Run the scraper with the given specific IDs or search query."""
#         if specific_ids:  # if specific ids, sets links for all of them to navigate through
#             links = [f"https://www.thingiverse.com/thing:{id}" for id in specific_ids]
#         else:  # otherwise if there is a search, makes the search
#             if search_query:
#                 search_box_selector = "input[type='text']"  # text box selector
#                 try:
#                     search_box = WebDriverWait(self.driver, 10).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, search_box_selector))
#                     )  # locates box
#                     search_box.clear()
#                     search_box.send_keys(search_query)  # enters query from input
#                     search_box.send_keys(Keys.RETURN)  # presses enter key
#                     time.sleep(5)
#                     current_page = 1  # Initialize page number for search results
#                     base_url = f"https://www.thingiverse.com/search?q={search_query}&page="
#                 except Exception as e:  # should never happen unless text box can't be found
#                     print(f"Could not perform search: {e}")
#                     return
#             else:
#                 self.driver.get(
#                     "https://www.thingiverse.com")  # otherwise, just go to main homepage and begin scraping there
#                 current_page = 1  # Initialize page number for main homepage
#                 base_url = "https://www.thingiverse.com/?page="
#
#             links = self.extract_and_visit_links("None", "a.ItemCardHeader__itemCardHeader--cPULo", "None",
#                                                  "div.ItemCardGrid__itemCardGrid--oBQiy.ItemCardGrid__left--kxoDS")
#
#         remaining_links = links.copy()  # Make a copy of the initial links list
#         timeout_failed_links = []  # Initialize a list to keep track of links that failed due to timeouts
#
#         while remaining_links:
#             for link in remaining_links.copy():  # Iterate over a copy of the remaining links list
#                 try:
#                     scrape_result = self.scrape_thing(link)
#                     if scrape_result == "success":  # call scrape thing on each link
#                         thing_details_list = [self.thing_details]  # set all details
#                         csv_file_path = ""  # csv path (change for device)
#                         self.write_to_csv(csv_file_path, thing_details_list)  # writes to csv
#                         repo_path = "" # repo path (change for device)
#                         commit_message = 'Add thing details and downloaded files'  # commit message
#                         if not self.git_commit_and_push(repo_path, csv_file_path, commit_message):
#                             continue  # if can't commit and push, skips
#                         remaining_links.remove(link)  # Remove the processed link from the remaining links list
#                     elif scrape_result == "timeout":
#                         timeout_failed_links.append(
#                             link)  # Add the link to the timeout_failed_links list if it fails due to a timeout
#                     else:
#                         remaining_links.remove(link)  # Remove skipped links
#                 except ScrapeTimeoutException:  # exception only occurs when there is a timeout
#                     timeout_failed_links.append(
#                         link)  # Add the link to the timeout_failed_links list if a ScrapeTimeoutException is raised
#
#                 except Exception as e:  # exception occurs if the process fully failed (not even a timeout failure) shouldn't happen
#                     print(f"Error occurred while scraping {link}: {e}")
#                     self.clear()  # Clear any details of the current thing
#                     self.reinitialize_driver()  # Reinitialize the driver
#                     continue
#
#             # Retry timeout failed links before moving to the next page
#             for attempt in range(max_retries):  # tries multiple times
#                 if not timeout_failed_links:  # if no timeout occurred, break out of loop and continue with remaining code
#                     break
#
#                 print(f"Retrying timeout failed links, attempt {attempt + 1}...")
#                 retry_links = timeout_failed_links.copy()  # copies failed links
#                 timeout_failed_links = []  # empties original list
#
#                 while retry_links:
#                     for link in retry_links.copy():  # copies retry links as well
#                         try:
#                             scrape_result = self.scrape_thing(link)
#                             if scrape_result == "success":  # calls scrape_thing on these links again
#                                 thing_details_list = [self.thing_details]  # same code chunk as before
#                                 csv_file_path = r""
#                                 self.write_to_csv(csv_file_path, thing_details_list)
#                                 repo_path = r""
#                                 commit_message = 'Add thing details and downloaded files'
#                                 if not self.git_commit_and_push(repo_path, csv_file_path, commit_message):
#                                     continue
#                                 retry_links.remove(link)  # remove link after done
#                             elif scrape_result == "timeout":
#                                 timeout_failed_links.append(
#                                     link)  # Add the link back to the timeout_failed_links list if it fails again
#                             else:
#                                 retry_links.remove(link)  # Remove skipped links
#                         except ScrapeTimeoutException:
#                             timeout_failed_links.append(
#                                 link)  # Add the link back to the timeout_failed_links list if a ScrapeTimeoutException is raised again
#
#                         except Exception as e:  # same exception and code
#                             print(f"Error occurred while scraping {link}: {e}")
#                             self.clear()
#                             self.reinitialize_driver()
#                             timeout_failed_links.append(
#                                 link)  # Add the link back to the timeout_failed_links list if any other exception occurs
#                             continue
#
#             self.clear_downloaded_files(
#                 r"C:\Users\noski\PycharmProjects\Thingiverse-Scraper\downloaded_files")  # clears downloads from folder set from path
#
#             if not specific_ids:  # doesn't do this for specific user id inputs
#                 current_page += 1  # go to next page when done
#                 next_page_url = base_url + str(current_page)  # construct next page url
#                 self.driver.get(next_page_url)  # navigate to next page
#                 time.sleep(5)  # wait for it to load
#                 new_links = self.extract_and_visit_links("None", "a.ItemCardHeader__itemCardHeader--cPULo", "None",
#                                                          "div.ItemCardGrid__itemCardGrid--oBQiy.ItemCardGrid__left--kxoDS")
#                 remaining_links.extend(new_links)
#                 if not new_links:  # if no new links found, exit the code
#                     break
#
#         if timeout_failed_links:  # if there are still failed links, then code could not successfully scrape after retries
#             print(
#                 f"These links could not be scraped after {max_retries} attempts due to timeouts: {timeout_failed_links}")
#     def close(self):
#         """Close the web driver."""
#         self.driver.quit()
