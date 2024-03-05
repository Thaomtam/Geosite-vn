import os
import aiohttp
import asyncio
import tldextract
import json

output_dir = "./rule-set"

async def fetch_domains_from_url(session, url):
    unique_domains = set()
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if "rules" in data:
                    for rule in data["rules"]:
                        if "domain" in rule:
                            domains = rule["domain"]
                            for domain in domains:
                                ext = tldextract.extract(domain)
                                normalized_domain = f"{ext.subdomain}.{ext.domain}.{ext.suffix}"
                                unique_domains.add(normalized_domain.lower())
    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        # Ghi lỗi vào tệp log hoặc gửi cảnh báo qua dịch vụ bên ngoài
        print(f"Error fetching data from URL: {url}, Error: {e}")
    return unique_domains

async def fetch_domains_from_urls(urls):
    unique_domains = set()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_domains_from_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            unique_domains = unique_domains.union(result)
    return list(unique_domains)

def write_json_file(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

async def main():
    os.makedirs(output_dir, exist_ok=True)

    # Đọc danh sách URL từ tệp hoặc sử dụng các URL khác
    urls = [
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/block.json",
        "https://raw.githubusercontent.com/Thaomtam/sing-box-rule-set-vn/rule-set/adway.json",
        # Add more URLs here...
    ]

    unique_domains = await fetch_domains_from_urls(urls)

    new_json_data = {"version": 1, "rules": [{"domain": unique_domains}]}

    output_json_filepath = os.path.join(output_dir, "Geosite-vn.json")
    write_json_file(new_json_data, output_json_filepath)

    # Additional steps for compilation if needed...

if __name__ == "__main__":
    asyncio.run(main())
