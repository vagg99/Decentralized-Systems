import requests
from bs4 import BeautifulSoup
import time
import os

# Grab the name as shown in the individual scientist's Wikipedia page
# The text shown right class="after mw-page-title-main"


# Function to fetch page title from URL
def fetch_page_title(url):
    try:
        response = requests.get(f"https://en.wikipedia.org{url}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title").get_text()
            return title.split(" - Wikipedia")[0]  # Extract title and remove site name
    except Exception as e:
        print(f"Error fetching title: {e}")
    return None

# Function to extract Surname
def extract_surname(scientist_soup, current_letter):
    name = scientist_soup.find("h1", class_="firstHeading").text
    # Remove content within parentheses
    name_without_parentheses = ' '.join([word for word in name.split() if '(' not in word and ')' not in word])
    names = name_without_parentheses.split()
    surname = None

    for name in names:
        if name.startswith(current_letter):
            surname = name
            break
    
    if surname is None:
        for name in names:
            if name[0] == current_letter:
                if len(name) == 2 and name[1] == ".":
                    continue
                else:
                    surname = name
                    break
    
    if surname is None:
        surname = names[-1]

    if len(surname) == 2 and '.' in surname:
        for name in names:
            if len(name) > 1 and name.startswith(current_letter) and '.' not in name:
                surname = name
                break
    
    # Check if the surname output starts with a letter matching current_letter
    if surname[0] != current_letter:
        for name in names:
            if name.startswith(current_letter):
                surname = name
                break

    return surname

def extract_awards(scientist_soup):
    infobox = scientist_soup.find("table", class_="infobox biography vcard")
    awards_count = 0

    if infobox:
        awards_label = infobox.find("th", {"scope": "row", "class": "infobox-label"}, text="Awards")
        if awards_label:
            awards_content = awards_label.find_next(["ul", "td"])  # Check for both <ul> and <td> elements

            if awards_content:
                if awards_content.name == "ul":
                    awards_count = len(awards_content.find_all("li"))
                elif awards_content.name == "td":
                    # Check for standalone numbers in text
                    text_content = awards_content.get_text(strip=True)
                    awards_count = len([word for word in text_content.split() if word.isdigit()])

                    # Check for <br> separated awards within <td>
                    br_count = awards_content.find_all("br")
                    awards_count += len(br_count)

                    # Check for <a> elements inside <td> excluding the ones with years
                    a_count = len(awards_content.find_all("a"))
                    awards_count += a_count - awards_count  # Subtract the count of numbers

    if awards_count == 0:
        awards_section = scientist_soup.find("span", {"id": lambda x: x and "awards" in x.lower()})
        if awards_section:
            awards_list = awards_section.find_next("ul")
            if awards_list:
                awards_count = len(awards_list.find_all("li"))

    return awards_count


# Function to extract Education
def extract_education(infobox):
    education_text = "-no data-"
    education_keywords = ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]

    # Check for Bachelor's degree tag
    bachelor_degree_tag = infobox.find("a", href="/wiki/Bachelor%27s_degree", title="Bachelor's degree")
    if bachelor_degree_tag:
        return education_text  # Return "-no data-" if the string "Bachelor's degree" is found

    # Labels to search for education-related information
    labels_to_search = ["Alma\xa0mater", "Education", "Institutions"]

    for label in labels_to_search:
        label_element = infobox.find("th", text=label)
        if label_element:
            education_element = label_element.find_next("td")
            if education_element:
                # Skip elements with the reference class
                if education_element.find(class_="reference"):
                    continue

                if education_element.find("ul"):
                    # For structure
                    # <ul>
                    #   <li> </li>
                    #   ...
                    # </ul> 
                    education_list = education_element.find_all("li")
                    for edu_item in education_list:
                        edu_text = edu_item.get_text(separator=" ", strip=True)
                        if any(keyword in edu_text for keyword in education_keywords):
                            keyword_found = False
                            for edu_link in edu_item.find_all("a", href=True):
                                if any(keyword in edu_link.get_text(strip=True) for keyword in education_keywords):
                                    keyword_found = True
                                    continue  # Move to the next link

                                education_link = edu_link.get("href")
                                if "Bachelor" not in education_link:  # Ignore degree level links
                                    university_title = fetch_page_title(education_link)
                                    if university_title:
                                        education_text = university_title
                                        break
                            if not keyword_found:
                                education_text = edu_text.split("(")[0]
                            break
                    else:
                        education_text = education_list[0].get_text(separator=" ", strip=True).split("(")[0]
                    break
                else:
                    # For linked institutions within <td>
                    education_links = education_element.find_all("a", href=True)
                    for edu_link in education_links:
                        edu_text = edu_link.get_text(strip=True)
                        if any(keyword in edu_text for keyword in education_keywords):
                            if any(keyword in edu_text for keyword in education_keywords):
                                continue  # Move to the next link

                            education_link = edu_link.get("href")
                            if "Bachelor" not in education_link:  # Ignore degree level links
                                university_title = fetch_page_title(education_link)
                                if university_title:
                                    education_text = university_title
                                    break
                    else:
                        education_text = education_links[0].get_text(strip=True).split("(")[0]
                    break

    # Subcase for keywords within parentheses
    if "(" in education_element.get_text(separator=" ", strip=True):
        parenthesis_text = education_element.get_text(separator=" ", strip=True)
        for keyword in education_keywords:
            if keyword in parenthesis_text:
                associated_uni = None
                links = education_element.find_all("a", href=True)
                for link in links:
                    if link.get_text(strip=True) == keyword:
                        associated_uni = link.find_previous("a", href=True)
                        break
                if associated_uni:
                    university_title = fetch_page_title(associated_uni["href"])
                    if university_title:
                        education_text = university_title
                        break

    # Non-Bachelor's degree case
    if education_text in ["M.Sc.", "Ph.D.", "D.Phil.", "IBM"]:
        education_text = "-no data-"
        
    if "," in education_text:
        education_text = education_text.split(",")[1].strip()

    if education_text.startswith("BS, "):
        education_text = education_text.split(", ")[1]

    if "Berkeley" in education_text:
        education_text = "University of California, Berkeley"

    if "MIT" in education_text:
        education_text = "Massachusetts Institute of Technology"

    if "Harvard" in education_text:
        education_text = "Harvard University"

    return education_text

# Function to clean education text
def clean_education_text(text):
    # If the final output follows the structure "{word1}, {word2}, {number}" only keep the word2 as the final Education output.
    if "," in text:
        text = text.split(",")[1].strip()

    # If the final output follows the structure "BS, {wordX}" only keep the wordX as the final Education output.
    if text.startswith("BS, "):
        text = text.split(", ")[1]

    # If the final output contains the word "Berkeley", change it to "University of California, Berkeley"
    if "Berkeley" in text:
        text = "University of California, Berkeley"

    # If the final output contains the word "MIT", change it to "Massachusetts Institute of Technology"
    if "MIT" in text:
        text = "Massachusetts Institute of Technology"

    return text


def scrape_scientist_info(scientist_name):
    url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"
    response = requests.get(url)
    scientist_url = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup.find_all(["h2", "ul", "li"]):
            if element.name == "ul":
                for li in element.find_all("li"):
                    link = li.find("a", title=scientist_name)
                    if link:
                        scientist_url = f"https://en.wikipedia.org{link.get('href')}"
                        break
                if scientist_url:
                    break

    if scientist_url:
        try:
            response = requests.get(scientist_url, timeout=10)

            if response.status_code == 200:
                scientist_soup = BeautifulSoup(response.text, "html.parser")
                surname = extract_surname(scientist_soup, scientist_name[0])
                awards_count = extract_awards(scientist_soup)
                education_text = extract_education(scientist_soup)

                return {
                    "Surname": surname,
                    "Awards": awards_count,
                    "Education": education_text
                }

        except Exception as e:
            print(f"An error occurred while processing {scientist_url}: {str(e)}")
    else:
        print(f"Scientist '{scientist_name}' not found in the list.")

    return None

scientist_name = input("Enter the name of the scientist you want to scrape: ")
scientist_info = scrape_scientist_info(scientist_name)

if scientist_info:
    print(f"\nInformation for {scientist_name}:")
    for key, value in scientist_info.items():
        print(f"{key}: {value}")
