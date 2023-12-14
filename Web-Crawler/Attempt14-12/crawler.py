import requests
from bs4 import BeautifulSoup
import time
import os

# Function to extract Surname
def extract_surname(scientist_soup, current_letter):
    # Logic to extract and return the surname
    name = scientist_soup.find("h1", class_="firstHeading").text
    names = name.split()
    surname = None

    for name in names:
        if name.startswith(current_letter):
            surname = name
            break
    
    if surname is None:
        for name in names:
            if name[0] == current_letter:
                surname = name
                break
    
    if surname is None:
        surname = names[-1]

    if len(surname) == 2 and surname[1] == '.':
        for name in names:
            if len(name) > 1 and name.startswith(current_letter):
                surname = name
                break
    
    return surname

# Function to extract Awards
def extract_awards(scientist_soup):
    infobox = scientist_soup.find("table", class_="infobox biography vcard")
    awards_count = 0

    if infobox:
        awards_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Awards")
        if awards_label:
            awards_section = awards_label.find_next("ul")
            if awards_section:
                awards_count = len(awards_section.find_all("li"))

    if awards_count == 0:
        awards_section = scientist_soup.find("span", {"id": lambda x: x and "awards" in x.lower()})
        if awards_section:
            awards_list = awards_section.find_next("ul")
            if awards_list:
                awards_count = len(awards_list.find_all("li"))

    return awards_count

# Function to extract Education
def extract_education(scientist_soup, current_letter):
    education_text = "-no data-"
    infobox = scientist_soup.find("table", class_="infobox biography vcard")

    labels_to_search = ["Alma\xa0mater", "Education", "Institutions"]

    for label in labels_to_search:
        label_element = infobox.find("th", text=label)
        if label_element:
            education_element = label_element.find_next("td")
            if education_element:
                if education_element.find(class_="reference"):
                    continue

                if education_element.find("ul"):
                    education_list = education_element.find_all("li")
                    keyword_found = False
                    phd_ignored = False
                    for edu_item in education_list:
                        edu_text = edu_item.get_text(separator=" ", strip=True)
                        if any(keyword in edu_text for keyword in ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]):
                            if not keyword_found:
                                keyword_found = True
                                continue  # Ignore the first keyword bullet
                            else:
                                education_text = edu_text.split("(")[0]
                                break
                        elif "Ph.D." in edu_text:
                            if not phd_ignored:
                                phd_ignored = True
                                continue  # Ignore Ph.D. as education
                            else:
                                education_text = edu_text.split("(")[0]
                                break
                        else:
                            education_text = edu_text.split("(")[0]
                            break  # Capture the first non-keyword university
                    break

                else:
                    education_links = education_element.find_all("a")
                    keyword_found = False
                    phd_ignored = False
                    for edu_link in education_links:
                        edu_text = edu_link.get_text(strip=True)
                        if any(keyword in edu_text for keyword in ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]):
                            if not keyword_found:
                                keyword_found = True
                                continue  # Ignore the first keyword bullet
                            else:
                                education_text = edu_text.split("(")[0]
                                break
                        elif "Ph.D." in edu_text:
                            if not phd_ignored:
                                phd_ignored = True
                                continue  # Ignore Ph.D. as education
                            else:
                                education_text = edu_text.split("(")[0]
                                break
                        else:
                            education_text = edu_text.split("(")[0]
                            break  # Capture the first non-keyword university
                    break

    return education_text


# Main code
url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

response = requests.get(url)
# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(current_directory, "..", "Text-Outputs")
output_file_path = os.path.join(output_directory, "14_12_scientist_info.txt")
education_keywords = ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    with open(output_file_path, "w", encoding="utf-8") as info_file:
        inside_valid_section = False
        current_letter = ""
        error_count = 0
        scientists_count = 0

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "h2":
                section_title = element.find("span", class_="mw-headline")
                if section_title and section_title.text.isalpha() and len(section_title.text) == 1:
                    inside_valid_section = True
                    current_letter = section_title.text
                    info_file.write("--------------------------\n> Surnames under letter: " + current_letter + "\n--------------------------\n\n" )  

                else:
                    inside_valid_section = False
            elif element.name == "ul" and inside_valid_section:
                for li in element.find_all("li"):
                    link = li.find("a")
                    if link:
                        scientist_url = f"https://en.wikipedia.org{link.get('href')}"
                        try:
                            response = requests.get(scientist_url, timeout=10)

                            if response.status_code == 200:
                                scientist_soup = BeautifulSoup(response.text, "html.parser")
                                surname = extract_surname(scientist_soup, current_letter)
                                awards_count = extract_awards(scientist_soup)
                                education_text = extract_education(scientist_soup, current_letter)

                                info_file.write(f"Surname: {surname}\nAwards: {awards_count}\nEducation: {education_text}\n\n")
                                scientists_count += 1

                            else:
                                print(f"Failed to retrieve the page for {scientist_url}. Status code: {response.status_code}")

                            time.sleep(1)
                        
                        except Exception as e:
                            error_count += 1
                            print(f"{error_count}) An error occurred while processing {scientist_url}: {str(e)}")

        info_file.write(f"\nTotal Scientists Included: {scientists_count}\n")
        info_file.write(f"{error_count} scientists excluded from the final list, due to not meeting the data criteria\n")
        
    print("Information including surnames, awards, and education has been scraped and saved to 14_12_scientist_info.txt.")
else:
    print("Failed to retrieve the web page. Status code:", response.status_code)
