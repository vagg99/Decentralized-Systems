import requests
from bs4 import BeautifulSoup
import time

# Read the list of scientist URLs from the file
with open("computer_scientists_hrefs.txt", "r", encoding="utf-8") as hrefs_file:
    scientist_urls = hrefs_file.read().splitlines()[:15]

# Create a text file to store the surnames and awards information
with open("scientist_awards_surnames.txt", "w", encoding="utf-8") as awards_file:
    for scientist_url in scientist_urls:
        try:
            # Send an HTTP GET request to the scientist's Wikipedia page with a timeout
            response = requests.get(scientist_url, timeout=10)

            if response.status_code == 200:
                # Parse the HTML content of the page using BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")

                # Find the scientist's name from the page
                name = soup.find("h1", class_="firstHeading").text

                # Extract the surname by splitting the name
                surname = name.split()[-1]

                # Find the "Awards" section inside the infobox biography vcard
                infobox = soup.find("table", class_="infobox biography vcard")
                awards_count = 0

                if infobox:
                    awards_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Awards")
                    if awards_label:
                        awards_section = awards_label.find_next("ul")
                        if awards_section:
                            awards_count = len(awards_section.find_all("li"))

                if awards_count == 0:
                    # If no awards were found in the infobox, check for an "Awards" section containing the word "awards"
                    awards_section = soup.find("span", {"id": lambda x: x and "awards" in x.lower()})
                    if awards_section:
                        awards_list = awards_section.find_next("ul")
                        if awards_list:
                            awards_count = len(awards_list.find_all("li"))

                # Write the scientist's surname and awards count to the text file
                awards_file.write(f"{surname} - {awards_count}\n")

            else:
                print(f"Failed to retrieve the page for {scientist_url}. Status code: {response.status_code}")

            # Add a sleep interval to avoid overwhelming the server
            time.sleep(1)

        except Exception as e:
            print(f"An error occurred while processing {scientist_url}: {str(e)}")

print("Awards information with surnames has been scraped and saved to scientist_awards_surnames.txt.")
