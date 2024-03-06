import os
import requests
import json
import dns.resolver
import threading
from concurrent.futures import ThreadPoolExecutor

output_dir = "./rule-set"

def fetch_domains_from_url(url, resolver):
    unique_domains = set()
    response = requests.get(url)
    if response.ok:
        data = response.json()
        if "rules" in data and isinstance(data["rules"], list):
            for rule_set in data["rules"]:
                if "domain" in rule_set and isinstance(rule_set["domain"], list):
                    for domain in rule_set["domain"]:
                        if isinstance(domain, str):
                            try:
                                # Sử dụng dns.resolver để kiểm tra tính hợp lệ của domain
                                answers = resolver.resolve(domain)
                                unique_domains.add(domain)
                            except:
                                # Bỏ qua các tên miền không hợp lệ
                                pass
    return unique_domains

def fetch_domains_from_urls(urls):
    unique_domains = set()
    resolver = dns.resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_domains_from_url, url, resolver) for url in urls]
        for future in futures:
            unique_domains.update(future.result())
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
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/xiaomi.json",
        "https://github.com/Thaomtam/sing-box-rule-set-vn/raw/rule-set/spam404.json",
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
