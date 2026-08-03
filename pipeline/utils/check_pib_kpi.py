import re

with open('src/lib/rasd-data.ts', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('PIB_CROISSANCE')
if idx >= 0:
    start = content.rfind('{', idx-200, idx)
    end = content.find('}', idx) + 1
    if start >= 0:
        snippet = content[start:end]
        print('PIB_CROISSANCE KPI:')
        print(snippet)
        
        # Check value
        vm = re.search(r'value:\s*([\d.]+)', snippet)
        if vm:
            print(f'\nValue: {vm.group(1)}')
else:
    print('PIB_CROISSANCE not found')
