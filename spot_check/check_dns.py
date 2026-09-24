import sys

sys.path.insert(0, "src")

from subdomain_enum.dns import resolve_domain

print("github.com:", resolve_domain("github.com"))

print("google.com:", resolve_domain("google.com"))

print("nonexistent-xyz-12345.com:", resolve_domain("nonexistent-xyz-12345.com"))

print("slow.example.com:", resolve_domain("slow.example.com", timeout=0.1))