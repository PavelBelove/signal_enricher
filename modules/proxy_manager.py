import requests
from bs4 import BeautifulSoup
import json
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyManager:
    def __init__(self, config_path='config/proxies.json'):
        self.config_path = config_path
        self.proxies = self.load_proxies()

    def load_proxies(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return []

    def save_proxies(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.proxies, f)

    def get_proxies(self):
        url = 'https://www.sslproxies.org/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        proxies = []
        for row in soup.find('table', attrs={'class': 'table table-striped table-bordered'}).find_all('tr')[1:]:
            tds = row.find_all('td')
            try:
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                country = tds[3].text.strip()
                if country not in ['United States', 'Canada', 'Russia'] and not country.startswith('Europe'):
                    proxies.append(f'http://{ip}:{port}')
            except IndexError:
                continue
        return proxies

    def check_proxy(self, proxy):
        try:
            response = requests.get('http://ipinfo.io/json', proxies={'http': proxy, 'https': proxy}, timeout=5)
            return proxy if response.status_code == 200 else None
        except:
            return None

    def update_proxies(self):
        new_proxies = self.get_proxies()
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(self.check_proxy, proxy): proxy for proxy in new_proxies}
            working_proxies = []
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result:
                    working_proxies.append(result)

        self.proxies = working_proxies
        self.save_proxies()
        if len(self.proxies) < 20:
            print(f"Warning: Only {len(self.proxies)} working proxies found.")

    def get_proxy(self):
        if not self.proxies:
            self.update_proxies()
        return random.choice(self.proxies) if self.proxies else None

proxy_manager = ProxyManager()
