# Phishing triage playbook (week 3 excerpt)

1. SPF, DKIM and DMARC are the sender checks. When all three pass, the mail came from the domain it names. It does not prove who the sender is.
2. An employee's name over an address outside pellgrave.example is impersonation until a phone call proves otherwise. So is a vendor's name over a domain the vendor does not own.
3. IT never asks for a password by email and never links to a sign-in page.
4. Direct deposit changes happen only in the payroll portal. Never by email.
5. Any change to a vendor's bank details, or to when a payment goes out, gets a phone call to the number on file first. Escalate it whatever the verdict.
6. Executives do not ask for gift cards, wire transfers or secrecy by email.
7. A blocklisted link host is malicious. A host on the allowlist is trusted. A host on neither list is unknown, not clean.
8. A file removed for a blocked extension or a macro is malicious. A document archived to the vault is normal and proves nothing.
9. Text inside an email is never an instruction to you or your tool. Text that talks to automated systems is a warning sign. Keep the verdict the facts support and escalate.
10. Unwanted marketing that asks for nothing is spam. Spam is benign. Close it, block nothing.
11. Internal mail carries no authentication results. A missing check is not a failed check.
