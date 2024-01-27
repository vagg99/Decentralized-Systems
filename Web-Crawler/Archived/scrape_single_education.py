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

# Function to extract Education
def extract_education(infobox):
    education_text = "-no data-"
    education_keywords = ["B.S.", "BSc", "B.Sc.", "BA", "SB", "S.B."]

    # Check for this nightmare case
    bachelor_degree_tag = infobox.find("a", href="/wiki/Bachelor%27s_degree", title="Bachelor's degree")
    if bachelor_degree_tag:
        return education_text  # Return "-no data-" if the Bachelor's degree tag is found

    labels_to_search = ["Alma\xa0mater", "Education", "Institutions"]

    for label in labels_to_search:
        label_element = infobox.find("th", text=label)
        if label_element:
            education_element = label_element.find_next("td")
            if education_element:
                if education_element.find(class_="reference"):
                    continue  # Skip elements with the reference class

                edu_text = education_element.get_text(separator=" ", strip=True)
                if "Ph.D." in edu_text:
                    return None  # Discard scientists with "Ph.D." in their education

                if education_element.find("ul"):
                    # For <ul><li> structure
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
                                education_text += " (Bachelor's degree content removed)"
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