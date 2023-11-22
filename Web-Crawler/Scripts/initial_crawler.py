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
    with open("sur_computer_scientists.txt", "w", encoding="utf-8") as file:
        inside_valid_section = False
        current_letter = ""

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "h2":
                # Check if the section is valid (A-Z)
                section_title = element.find("span", class_="mw-headline")
                if section_title and section_title.text.isalpha() and len(section_title.text) == 1:
                    inside_valid_section = True
                    current_letter = section_title.text
                    file.write(current_letter + "\n")  # Write the current letter

                else:
                    inside_valid_section = False
            elif element.name == "ul" and inside_valid_section:
                for li in element.find_all("li"):
                    # Extract the first href and title, and format the href as a full URL
                    link = li.find("a")
                    if link:
                        title = link.get("title")
                        names = title.split()
                        surname = None

                        for name in names:
                            if name.startswith(current_letter):
                                surname = name
                                break

                        if surname is None:
                            # If no name starts with the section letter, look for a name in the same line
                            for name in names:
                                if name[0] == current_letter:
                                    surname = name
                                    break

                        if surname:
                            file.write(surname + "\n")

    print("Data has been scraped and saved to sur_computer_scientists.txt.")
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)
