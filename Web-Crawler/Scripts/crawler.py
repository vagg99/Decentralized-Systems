import requests
from bs4 import BeautifulSoup
import time

url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Create a text file to store the surnames, awards, and education information
    with open("scientist_info.txt", "w", encoding="utf-8") as info_file:
        inside_valid_section = False
        current_letter = ""

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "h2":
                # Check if the section is valid (A-Z)
                section_title = element.find("span", class_="mw-headline")
                if section_title and section_title.text.isalpha() and len(section_title.text) == 1:
                    inside_valid_section = True
                    current_letter = section_title.text
                    info_file.write("--------------------------\n> Surnames under letter: " + current_letter + "\n--------------------------\n\n" )  # Write the current letter

                else:
                    inside_valid_section = False
            elif element.name == "ul" and inside_valid_section:
                for li in element.find_all("li"):
                    # Extract the first href and title, and format the href as a full URL
                    link = li.find("a")
                    if link:
                        scientist_url = f"https://en.wikipedia.org{link.get('href')}"
                        try:
                            # Send an HTTP GET request to the scientist's Wikipedia page with a timeout
                            response = requests.get(scientist_url, timeout=10)

                            if response.status_code == 200:
                                # Parse the HTML content of the scientist's page using BeautifulSoup
                                scientist_soup = BeautifulSoup(response.text, "html.parser")

                                # Find the scientist's name from the page
                                name = scientist_soup.find("h1", class_="firstHeading").text

                                # Extract the surname by splitting the name
                                names = name.split()
                                surname = None

                                # Extracting surname using the logic from the second snippet
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

                                # Fallback to the last name if no name starting with the section letter is found
                                if surname is None:
                                    surname = names[-1]

                                # Find the "Awards" section inside the infobox biography vcard
                                infobox = scientist_soup.find("table", class_="infobox biography vcard")
                                awards_count = 0

                                if infobox:
                                    awards_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Awards")
                                    if awards_label:
                                        awards_section = awards_label.find_next("ul")
                                        if awards_section:
                                            awards_count = len(awards_section.find_all("li"))

                                if awards_count == 0:
                                    # If no awards were found in the infobox, check for an "Awards" section containing the word "awards"
                                    awards_section = scientist_soup.find("span", {"id": lambda x: x and "awards" in x.lower()})
                                    if awards_section:
                                        awards_list = awards_section.find_next("ul")
                                        if awards_list:
                                            awards_count = len(awards_list.find_all("li"))

                                # Find the education section
                                education_section = scientist_soup.find("span", {"id": lambda x: x and "education" in x.lower()})

                                education_text = ""
                                if education_section:
                                    next_h2 = education_section.find_next("h2")
                                    for p in education_section.find_all_next("p", recursive=False):
                                        if p.find_previous(["h2", "h3"]) == next_h2:
                                            break
                                        education_text += p.get_text(separator=" ")

                                education_text = education_text.strip()

                                # If the education_section is not found, try another section
                                if not education_section:
                                    # Look for the education in infobox
                                    infobox_education_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Education")
                                    if infobox_education_label:
                                        education_text = infobox_education_label.find_next("td").get_text(separator=" ", strip=True)

                                # If still not found, check in the Biography section
                                if not education_text:
                                    biography_section = scientist_soup.find("span", {"id": lambda x: x and "biography" in x.lower()})
                                    if biography_section:
                                        education_text = biography_section.find_next("p").get_text(separator=" ", strip=True)

                                # If education is not found in the Biography, try the top section of the Wikipedia page
                                if not education_text:
                                    top_section = infobox.find_next("p")
                                    if top_section:
                                        for paragraph in top_section.find_all_next("p"):
                                            if paragraph.find_previous("h2"):
                                                break
                                            education_text += paragraph.get_text(separator=" ", strip=True)

                                education_text = education_text.strip()


                                # Write the scientist's surname, awards count, and education text to the text file
                                info_file.write(f"Surname: {surname}\nAwards: {awards_count}\nEducation: {education_text}\n\n")

                            else:
                                print(f"Failed to retrieve the page for {scientist_url}. Status code: {response.status_code}")

                            # sleep interval to avoid overwhelming the server
                            time.sleep(1)

                        except Exception as e:
                            print(f"An error occurred while processing {scientist_url}: {str(e)}")

    print("Information including surnames, awards, and education has been scraped and saved to scientist_info.txt.")
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)
