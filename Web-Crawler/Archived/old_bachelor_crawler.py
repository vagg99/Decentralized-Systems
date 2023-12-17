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
output_file_path = os.path.join(output_directory, "scientist_BA_info.txt")

# keywords for education
education_keywords = ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]

if response.status_code == 200:
    # HTML parser 
    soup = BeautifulSoup(response.text, "html.parser")

    # Create a text file to store the surnames, awards, and education information
    with open(output_file_path, "w", encoding="utf-8") as info_file:
        inside_valid_section = False
        current_letter = ""
        error_count = 0
        scientists_count = 0

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

                                # Handle single-letter surnames
                                if len(surname) == 2 and surname[1] == '.':
                                    for name in names:
                                        if len(name) > 1 and name.startswith(current_letter):
                                            surname = name
                                            break

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
                                education_text = "-no data-"

                                # Look for the education in infobox under different labels
                                labels_to_search = ["Alma\xa0mater", "Education", "Institutions"]

                                for label in labels_to_search:
                                    label_element = infobox.find("th", text=label)
                                    if label_element:
                                        education_element = label_element.find_next("td")
                                        if education_element:
                                            # Check if the education contains reference class
                                            if education_element.find(class_="reference"):
                                                continue  # Skip elements with the reference class
                                            
                                            if education_element.find("ul"):
                                                # For <ul><li> structure
                                                education_list = education_element.find_all("li")
                                                for edu_item in education_list:
                                                    edu_text = edu_item.get_text(separator=" ", strip=True)
                                                    if any(keyword in edu_text for keyword in education_keywords):
                                                        education_text = edu_text.split("(")[0]
                                                        education_text += " (Bachelor's degree content removed)"
                                                        break
                                                else:
                                                    education_text = education_list[0].get_text(separator=" ", strip=True).split("(")[0]
                                                break
                                            else:
                                                # For linked institutions within <td>
                                                education_links = education_element.find_all("a")
                                                for edu_link in education_links:
                                                    edu_text = edu_link.get_text(strip=True)
                                                    if any(keyword in edu_text for keyword in education_keywords):
                                                        education_text = edu_text.split("(")[0]
                                                        break
                                                else:
                                                    education_text = education_links[0].get_text(strip=True).split("(")[0]
                                                break
                                    # subcase for plain text university name
                                    if education_text == "-no data-":
                                        plain_text_education = infobox.find("td", class_="infobox-data")
                                        if plain_text_education:
                                            edu_text = plain_text_education.get_text(strip=True)
                                            if any(keyword in edu_text for keyword in education_keywords):
                                                education_text = edu_text.split("(")[0]


                                # Write the scientist's surname, awards count, and education text to the text file
                                info_file.write(f"Surname: {surname}\nAwards: {awards_count}\nEducation: {education_text}\n\n")
                                scientists_count += 1

                            else:
                                print(f"Failed to retrieve the page for {scientist_url}. Status code: {response.status_code}")

                            # sleep interval to avoid overwhelming the server
                            time.sleep(1)
                        
                        except Exception as e:
                            error_count += 1
                            print(f"{error_count}) An error occurred while processing {scientist_url}: {str(e)}")

        # Write the total number of scientists and excluded count to the file
        info_file.write(f"\nTotal Scientists Included: {scientists_count}\n")
        info_file.write(f"{error_count} scientists excluded from the final list, due to not meeting the data criteria\n")
        
    print("Information including surnames, awards, and education has been scraped and saved to scientist_BA_info.txt.")
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)
