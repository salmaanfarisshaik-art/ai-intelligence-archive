import json
import glob
import sys

required_fields = ['unique_id', 'source_url', 'source_name', 'source_type', 'last_updated', 'category', 'raw_payload']
DOMAINS = ['skills', 'apis', 'benchmarks', 'datasets', 'ide_rules', 'mcps', 'models', 'news', 'prompts', 'tools']
files = []
for domain in DOMAINS:
    files.extend(glob.glob(f'{domain}/*/*.json'))

failed = False

print('=== SECTION 8: Data Integrity Check ===')
for f in files:
    print(f'Checking {f}')
    try:
        record = json.load(open(f, encoding='utf-8'))
        for field in required_fields:
            if field not in record:
                print(f'FAIL: {f} missing {field}')
                failed = True
            elif record[field] is None:
                print(f'FAIL: {f} {field} is null')
                failed = True
    except Exception as e:
        print(f'FAIL: {f} could not be read: {e}')
        failed = True
            
        if failed:
            break
    if failed:
        break

if not failed:
    print('All records valid.')
else:
    sys.exit(1)
