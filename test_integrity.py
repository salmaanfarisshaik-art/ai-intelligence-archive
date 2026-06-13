import json
import glob
import sys

required_fields = ['unique_id', 'source_url', 'source_name', 'source_type', 'last_updated', 'category', 'raw_payload']
files = glob.glob('data/processed/*/data.json')
failed = False

print('=== SECTION 8: Data Integrity Check ===')
for f in files:
    print(f'Checking {f}')
    data = json.load(open(f, encoding='utf-8'))
    for i, record in enumerate(data):
        for field in required_fields:
            if field not in record:
                print(f'FAIL: {f} record {i} missing {field}')
                failed = True
            elif record[field] is None:
                print(f'FAIL: {f} record {i} {field} is null')
                failed = True
            
        if failed:
            break
    if failed:
        break

if not failed:
    print('All records valid.')
else:
    sys.exit(1)
