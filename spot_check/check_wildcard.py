import sys
sys.path.insert(0, "src")

from subdomain_enum.wildcard import detect_wildcard

# github.com — как мы видели, возможно, есть wildcard на GitHub Pages
print("github.com:", detect_wildcard("github.com"))

# example.com — скорее всего, без wildcard
print("example.com:", detect_wildcard("example.com"))

# yandex.ru — российский домен, посмотрим
print("yandex.ru:", detect_wildcard("yandex.ru"))

# google.com — точно без wildcard
print("google.com:", detect_wildcard("google.com"))