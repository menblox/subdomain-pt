import sys
import time

sys.path.insert(0, "src")

from subdomain_enum.bruteforce import bruteforce, load_wordlist

words = load_wordlist("wordlists/subdomains-5000.txt")

start = time.time()
results = bruteforce("github.com", words, timeout=2.0, max_workers=30)
elapsed = time.time() - start

found = 0
for name, ips in results:
    if ips:
        print(f"{name}\t{', '.join(ips)}")
        found += 1

print(f"Найдено: {found} из {len(words)}")
print(f"Время: {elapsed:.2f} сек")