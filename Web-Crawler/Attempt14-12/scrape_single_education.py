import requests
from bs4 import BeautifulSoup
import os

def fetch_page_title(url):
    base_url = "https://en.wikipedia.org"
    full_url = base_url + url

    response = requests.get(full_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        page_title = soup.find(class_="mw-page-title-main")
        if page_title:
            return page_title.text
    return None


def extract_education(infobox):
    education_text = "-no data-"
    education_keywords = ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]

    labels_to_search = ["Alma\xa0mater", "Education", "Institutions"]

    for label in labels_to_search:
        label_element = infobox.find("th", text=label)
        if label_element:
            education_element = label_element.find_next("td")
            if education_element:
                if education_element.find(class_="reference"):
                    continue  # Skip elements with the reference class

                if education_element.find("ul"):
                    # For <ul><li> structure
                    education_list = education_element.find_all("li")
                    for edu_item in education_list:
                        edu_text = edu_item.get_text(separator=" ", strip=True)
                        if any(keyword in edu_text for keyword in education_keywords):
                            # Check if the education item contains only the keyword
                            if edu_text.strip() in education_keywords:
                                # Find the preceding anchor tag
                                prev_tag = edu_item.find_previous("a")
                                if prev_tag:
                                    education_text = fetch_page_title(prev_tag["href"])
                                    break
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
                            prev_tag = edu_link.find_previous("a")
                            if prev_tag:
                                education_text = fetch_page_title(prev_tag["href"])
                            else:
                                education_text = fetch_page_title(edu_link["href"])
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
                if edu_text.strip() not in education_keywords:
                    prev_tag = plain_text_education.find_previous("a")
                    if prev_tag:
                        education_text = fetch_page_title(prev_tag["href"])
                    else:
                        education_text = edu_text.split("(")[0]

    return education_text

def scrape_scientist_info(scientist_name):
    url = f"https://en.wikipedia.org/wiki/{scientist_name.replace(' ', '_')}"

    response = requests.get(url)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(current_directory, "Text-Outputs")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_file_path = os.path.join(output_directory, f"{scientist_name.replace(' ', '_')}_info.txt")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        with open(output_file_path, "w", encoding="utf-8") as info_file:
            infobox = soup.find("table", class_="infobox biography vcard")
            education_text = extract_education(infobox)

            info_file.write(f"Education: {education_text}\n\n")

        print(f"Education information for {scientist_name} has been scraped and saved to {scientist_name.replace(' ', '_')}_info.txt.")
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)

if __name__ == "__main__":
    scientist_input = input("Enter the name of the scientist exactly as shown on Wikipedia: ")
    scrape_scientist_info(scientist_input)
