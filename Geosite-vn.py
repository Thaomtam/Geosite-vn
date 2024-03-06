import os
import requests
import json
import dns.resolver

output_dir = "./rule-set"

def fetch_domains_from_urls(urls):
    unique_domains = set()
    valid_domains = set()

    for url in urls:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            if "rules" in data:
                for rule in data["rules"]:
                    if "domain" in rule:
                        domain = rule["domain"]
                        try:
                            dns.resolver.resolve(domain, "MX")
                            valid_domains.add(domain)
                        except dns.resolver.NXDOMAIN:
                            pass

    unique_domains = valid_domains
    return list(unique_domains)


def write_json_file(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def main():
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu không tồn tại

    # Danh sách các URL chứa các tệp JSON
    urls = [
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/block.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/adway.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/MVPS.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/easylist.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/yoyo.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/black.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/anudeep.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/xiaomi.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/dan.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/spam404.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/Kninja.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/Redirect.json"
    ]

    # Thu thập tất cả các tên miền duy nhất từ các tệp JSON
    unique_domains = fetch_domains_from_urls(urls)

    # Tạo cấu trúc JSON mới với danh sách tên miền duy nhất
    new_json_data = {"version": 1, "rules": [{"domain": unique_domains}]}

    # Ghi vào tệp JSON mới trong thư mục output_dir
    output_json_filepath = os.path.join(output_dir, "Geosite-vn.json")
    write_json_file(new_json_data, output_json_filepath)

    # Sử dụng tập lệnh Python để biên dịch tệp JSON mới thành tệp .srs
    output_srs_filepath = os.path.join(output_dir, "Geosite-vn.srs")
    os.system(f"sing-box rule-set compile --output {output_srs_filepath} {output_json_filepath}")

if __name__ == "__main__":
    main()
