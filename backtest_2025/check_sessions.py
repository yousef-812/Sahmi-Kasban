import json, glob, os
for f in sorted(glob.glob('/tmp/bt_output/sessions_*.json')):
    data = json.load(open(f))
    dates = data['dates']
    print(os.path.basename(f), 'count=', data['count'], 'min=', dates[0] if dates else None, 'max=', dates[-1] if dates else None)
