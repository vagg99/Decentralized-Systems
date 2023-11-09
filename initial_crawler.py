import requests
from bs4 import BeautifulSoup

# Define the URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

# Send an HTTP GET request to the URL
response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Create a text file to store the extracted information
    with open("computer_scientists.txt", "w", encoding="utf-8") as file:
        inside_valid_section = False

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "h2":
                # Check if the section is valid (A-Z)
                section_title = element.find("span", class_="mw-headline")
                if section_title and section_title.text.isalpha() and len(section_title.text) == 1:
                    inside_valid_section = True
                else:
                    inside_valid_section = False
            elif element.name == "ul" and inside_valid_section:
                for li in element.find_all("li"):
                    # Extract the first href and title, and format the href as a full URL
                    link = li.find("a")
                    if link:
                        href = link.get("href")
                        title = link.get("title")
                        full_url = f"https://en.wikipedia.org{href}"
                        file.write(f"{title} - {full_url}\n")
            elif element.name == "h2" and element.text in ["See also", "References", "External links"]:
                # Stop writing when these sections are encountered
                break

    print("Data has been scraped and saved to computer_scientists.txt.")
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)