import os
import requests
import json

output_dir = "./rule-set"

def fetch_domains_from_url(url):
    unique_domains = set()
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises an HTTPError for bad status codes
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
        print(f"Error fetching data from {url}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data from {url}: {e}")

    return []



# Các hàm khác không cần thay đổi

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

    new_json_data = {"version": 1, "rules": [{"domain": list(unique_domains)}]}

    output_json_filepath = os.path.join(output_dir, "Geosite-vn.json")

    # Đảm bảo output_json_filepath được định nghĩa trước khi sử dụng
    with open(output_json_filepath, 'w') as f:
        json.dump(new_json_data, f, indent=4)

    output_srs_filepath = os.path.join(output_dir, "Geosite-vn.srs")
    os.system(f"sing-box rule-set compile --output {output_srs_filepath} {output_json_filepath}")

if __name__ == "__main__":
    main()
