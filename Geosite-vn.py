import os
import requests
import json
import logging
import subprocess

output_dir = "./rule-set"

logging.basicConfig(filename='process.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def fetch_domains_from_url(url):
    unique_domains = set()
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad status codes
        logging.info(f"Successfully fetched data from {url}")
        data = response.json()
        if "rules" in data and isinstance(data["rules"], list):
            for rule_set in data["rules"]:
                if "domain" in rule_set and isinstance(rule_set["domain"], list):
                    for domain in rule_set["domain"]:
                        if isinstance(domain, str):
                            unique_domains.add(domain)

        sorted_domains = sorted(list(unique_domains), key=str.lower)  # Sắp xếp theo thứ tự chữ cái không phân biệt chữ hoa chữ thường
        return sorted_domains
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON data from {url}: {e}")

    return []

def get_top_level_domains(domains):
    top_level_domains = set()
    for domain in domains:
        parts = domain.split('.')
        if len(parts) > 1:
            top_level_domains.add(parts[-2] + '.' + parts[-1])
        else:
            top_level_domains.add(domain)
    return sorted(top_level_domains, key=str.lower)

def main():
    os.makedirs(output_dir, exist_ok=True)

    urls = [
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/block.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/adway.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/adservers.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/adway.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/easylist.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/MVPS.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/yoyo.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/threat.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/d3host.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/abpvn.json"
    ]

    unique_domains = set()
    for url in urls:
        unique_domains.update(fetch_domains_from_url(url))

    sorted_domains = sorted(list(unique_domains), key=str.lower)
    new_json_data = {"version": 1, "rules": [{"domain": sorted_domains}]}

    output_json_filepath = os.path.join(output_dir, "Geosite-vn.json")
    with open(output_json_filepath, 'w') as f:
        json.dump(new_json_data, f, indent=4)
        logging.info(f"Geosite-vn.json created at {output_json_filepath}")

    output_srs_filepath = os.path.join(output_dir, "Geosite-vn.srs")
    result = subprocess.run(["sing-box", "rule-set", "compile", "--output", output_srs_filepath, output_json_filepath], capture_output=True, text=True)

    if result.returncode != 0:
        logging.error(f"Error compiling rule-set: {result.stderr}")
    else:
        logging.info("Rule-set compiled successfully.")

    # Create domain.json with only top-level domains
    top_level_domains = get_top_level_domains(sorted_domains)
    domain_json_filepath = os.path.join(output_dir, "domain.json")
    with open(domain_json_filepath, 'w') as f:
        json.dump(top_level_domains, f, indent=4)
        logging.info(f"domain.json created at {domain_json_filepath}")

if __name__ == "__main__":
    main()
