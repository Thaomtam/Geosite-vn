import os
import requests
import json
import dns.resolver  # Replace 'adns' with 'dnspython'
import queue
import threading
from concurrent.futures import ThreadPoolExecutor

output_dir = "./rule-set"

resolver = dns.resolver.Resolver()  # Use 'dns.resolver.Resolver()' for DNS resolution
cache = {}  # Cache dictionary

# Replace the rest of the code according to the earlier suggestion using 'dns.resolver'


def process_domain(domain):
    if domain in cache:
        return cache[domain]

    try:
        result = resolver.submit(domain, adns.rr.A)
        ip = result.result().to_ip()  # Lấy IP 
        cache[domain] = ip  # Lưu kết quả vào cache
        return ip
    except:
        return None

def fetch_domains_from_url(url):
    unique_domains = set()
    response = requests.get(url)
    if response.ok:
        data = response.json()
        if "rules" in data and isinstance(data["rules"], list):
            for rule_set in data["rules"]:
                if "domain" in rule_set and isinstance(rule_set["domain"], list):
                    for domain in rule_set["domain"]:
                        if isinstance(domain, str):
                            unique_domains.add(domain)
    return unique_domains

def fetch_domains_from_urls(urls):
    unique_domains = set()
    with ThreadPoolExecutor(max_workers=10) as executor:
        domain_queue = queue.Queue()
        result_queue = queue.Queue()

        # Đưa các domain vào domain_queue
        for url in urls:
            domains = fetch_domains_from_url(url)
            for domain in domains:
                domain_queue.put(domain)

        # Workers lấy miền từ domain_queue, xử lý và đưa kết quả vào result_queue
        def worker():
            while True:
                domain = domain_queue.get()
                if domain is None:
                    break
                ip = process_domain(domain)
                if ip is not None:
                    result_queue.put(ip)
                domain_queue.task_done()

        # Khởi tạo và chạy các workers
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Chờ cho tất cả các workers hoàn thành
        for t in threads:
            t.join()

        # Thu thập kết quả từ result_queue
        while not result_queue.empty():
            unique_domains.add(result_queue.get())

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
