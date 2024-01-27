import requests
from bs4 import BeautifulSoup
import time
import os

url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

response = requests.get(url)

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the output directory path relative to the current script
output_directory = os.path.join(current_directory, "..", "Text-Outputs")

# Define the path for the output file
output_file_path = os.path.join(output_directory, "scientist_info.txt")

if response.status_code == 200:
    # HTML parser 
    soup = BeautifulSoup(response.text, "html.parser")

    # Create a text file to store the surnames, awards, and education information
    with open(output_file_path, "w", encoding="utf-8") as info_file:
        inside_valid_section = False
        current_letter = ""

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "h2":
                # Check if the section is valid (A-Z)
                section_title = element.find("span", class_="mw-headline")
                if section_title and section_title.text.isalpha() and len(section_title.text) == 1:
                    inside_valid_section = True
                    current_letter = section_title.text
                    # Write the current letter
                    info_file.write("--------------------------\n> Surnames under letter: " + current_letter + "\n--------------------------\n\n" )  

                else:
                    inside_valid_section = False
            elif element.name == "ul" and inside_valid_section:
                for li in element.find_all("li"):
                    # Extract the first href and title, and format the href as a full URL
                    link = li.find("a")
                    if link:
                        scientist_url = f"https://en.wikipedia.org{link.get('href')}"
                        try:
                            # HTTP GET request
                            response = requests.get(scientist_url, timeout=10)

                            if response.status_code == 200:
                                # HTML parser
                                scientist_soup = BeautifulSoup(response.text, "html.parser")

                                #########################################################
                                # SURNAME
                                #########################################################

                                # Find the scientist's name from the page
                                name = scientist_soup.find("h1", class_="firstHeading").text

                                # Extract the surname by splitting the name
                                names = name.split()
                                surname = None

                                # Match the surname with the section letter
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

                                #########################################################
                                # AWARDS
                                #########################################################

                                # Find the "Awards" section inside the infobox biography vcard
                                infobox = scientist_soup.find("table", class_="infobox biography vcard")
                                # by default, the awards count is 0
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

                                #########################################################
                                # EDUCATION
                                #########################################################
                                education_text = ""

                                # education text manifested through
                                if not education_text:
                                    # Look for the education in infobox under "Alma mater" label
                                    infobox_alma_mater_label = infobox.find("th", text="Alma\xa0mater")
                                    if infobox_alma_mater_label:
                                        education_text = infobox_alma_mater_label.find_next("td").get_text(separator=" ", strip=True)
                                    else:
                                        # If "Alma mater" is not found, look for "Institutions" in the infobox
                                        infobox_institutions_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Institutions")
                                        if infobox_institutions_label:
                                            education_text = infobox_institutions_label.find_next("td").get_text(separator=" ", strip=True)
                                        else:
                                            # If neither "Alma mater" nor "Institutions" is found, look for "Education" in the infobox
                                            infobox_education_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Education")
                                            if infobox_education_label:
                                                    education_text = infobox_education_label.find_next("td").get_text(separator=" ", strip=True)

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
