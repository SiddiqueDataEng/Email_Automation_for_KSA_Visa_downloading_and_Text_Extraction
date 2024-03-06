"""Test specific pattern matching"""
import re

# Sample text from actual PDF (PyPDF2 extraction)
text = """
رقم التأشيرة 6103254019 Visa No.
صالحة اعتبارا من 06/10/2023 Valid From
صالحة لغاية 04/01/2024 Valid Until
مدة الإقامة Days90يوم Duration of Stay
مكان الإصدارا لممثلية السعودية في كراتشي Saudi Mission In KarachiPlace of issue
نوع التأشيرة Work ‐  عمل Visa Type
الاسم MUHAMMAD IDREES MUHAMMAD ISHAQ Name
الجنسية Pakistan ‐  باكستان Nationality
رقم الجواز AL1422123 Passport No.
رقم المستند 1303496464 Ref. No.
التاريخ 06/10/2023 Ref. Date
المهنة Builder بناء ‐  Occupation
اسم صاحب العملش ركة نسما وشركاهم للمقاولات المحدود Employer name
الرسوم‐ Visa Fees
1<PAKISHAQ<<MUHAMMAD<IDREES<MUHAMMAD<<<<<<<<
AL14221236PAK0101198951084<<<<<<<<<<<<<<<<09

Visa No. 6103254019
Application No. E812193787
"""

print("="*80)
print("PATTERN TESTING")
print("="*80)

# Test Nationality
print("\n1. Testing Nationality patterns:")
patterns = [
    r'([A-Z][a-z]+)\s+‐\s+[\u0600-\u06FF]+\s+Nationality',
    r'Nationality\s+([A-Za-z]+)\s+‐',
    r'([A-Z][a-z]+)\s+‐\s+[\u0600-\u06FF]+\s+Passport',
]
for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"  Pattern {i}: MATCH = '{match.group(1)}'")
    else:
        print(f"  Pattern {i}: NO MATCH")

# Test Occupation
print("\n2. Testing Occupation patterns:")
patterns = [
    r'([A-Z][A-Za-z\s]+?)\s+[\u0600-\u06FF]+\s+‐\s+Occupation',
    r'Occupation\s+([A-Za-z\s]+?)\s+[\u0600-\u06FF]',
    r'([A-Z][a-z]+)\s+[\u0600-\u06FF]+\s+‐\s+Occupation',
]
for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"  Pattern {i}: MATCH = '{match.group(1)}'")
    else:
        print(f"  Pattern {i}: NO MATCH")

# Test Employer
print("\n3. Testing Employer patterns:")
patterns = [
    r'([\u0600-\u06FF\s]+)\s+Employer\s*name',
    r'Employer\s*name\s+([A-Za-z\s]+)',
    r'[\u0600-\u06FF]+\s+([A-Za-z\s]+)\s+Employer',
]
for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        result = match.group(1)[:50]  # Truncate for display
        print(f"  Pattern {i}: MATCH = '{result}'")
    else:
        print(f"  Pattern {i}: NO MATCH")

# Test Application No
print("\n4. Testing Application No patterns:")
patterns = [
    r'Application\s*No\.?\s+([A-Z]\d{9,10})',
    r'([A-Z]\d{9,10})\s+Application',
    r'\b([A-Z]\d{9,10})\b',
]
for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"  Pattern {i}: MATCH = '{match.group(1)}'")
    else:
        print(f"  Pattern {i}: NO MATCH")

print("\n" + "="*80)
