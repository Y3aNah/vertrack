import re
import requests
import yaml
from bs4 import BeautifulSoup

# Function to extract latest version from product name
def extract_version(product_name):
    version_match = re.search(r'(\d+(\.\d+)*(\.\d+)*)', product_name)
    if version_match:
        return version_match.group()
    return None

# Function to scrape the table and extract latest versions
def scrape_latest_versions(url):
    # Make a GET request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the URL.")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables on the page
    tables = soup.find_all("table")
    if not tables:
        print("No tables found on the webpage.")
        return

    # Initialize dictionary to store latest versions
    latest_versions = {}

    # Iterate over each table to find the one containing the relevant data
    for table in tables:
        # Check if the table contains the expected headers
        headers = table.find("tr")
        if headers and "product" in headers.text.lower() and "date" in headers.text.lower():
            # Extract data from table rows
            rows = table.find_all("tr")[1:]  # Skip header row
            for row in rows:
                columns = row.find_all("td")
                if len(columns) < 2:
                    print("Invalid table structure. Skipping row with missing columns.")
                    continue

                product_info = columns[0].text.strip()
                product_version = extract_version(product_info)
                if product_version:
                    product_name = product_info.split(product_version)[0].strip()
                else:
                    product_name = product_info.strip()
                    product_version = "Unknown"

                release_date = columns[1].text.strip()

                # Update latest_versions dictionary
                if product_name not in latest_versions:
                    latest_versions[product_name] = {"version": product_version, "date": release_date}
                else:
                    current_date = latest_versions[product_name]["date"]
                    if release_date > current_date:
                        latest_versions[product_name] = {"version": product_version, "date": release_date}
                    elif release_date == current_date and product_version > latest_versions[product_name]["version"]:
                        latest_versions[product_name] = {"version": product_version, "date": release_date}

            break  # Exit loop after processing the first suitable table

    return latest_versions

# Function to write Markdown table to file
def write_markdown_table(versions, filename):
    with open(filename, "w") as file:
        file.write("| Product | Version | Release Date |\n")
        file.write("| ------- | ------- | ------------ |\n")
        for product, info in versions.items():
            file.write(f"| {product} | {info['version']} | {info['date']} |\n")

# Main function
def main():
    # Load config from YAML file
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Extract URL from config
    url = config.get("url")
    if not url:
        print("URL not found in the config file.")
        return

    latest_versions = scrape_latest_versions(url)
    if latest_versions:
        write_markdown_table(latest_versions, "latest-versions.md")
        print("Latest versions saved to latest-versions.md")

if __name__ == "__main__":
    main()
