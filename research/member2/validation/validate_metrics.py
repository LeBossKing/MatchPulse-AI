import json, csv, math
from pathlib import Path
base=Path(__file__).parent
events={e['id']:e for e in json.load(open(base/'3788741_events.json',encoding='utf-8'))}
with open(base/'metrics_validation.csv',encoding='utf-8',newline='') as f:
 for row in csv.DictReader(f):
  e=events[row['event_id']]; a=e['location']; b=e['pass']['end_location']
  assert abs(math.hypot(b[0]-a[0],b[1]-a[1])-float(row['computed_distance_coordinate_units']))<0.00001
  assert abs((b[0]-a[0])-float(row['forward_delta_x_coordinate_units']))<0.00001
  assert (e['pass'].get('outcome') is None)==(row['completed_by_outcome_absence']=='True')
  if row['assisted_shot_id']:
   assert row['assisted_shot_id'] in events and events[row['assisted_shot_id']]['type']['name']=='Shot'
print('All 5 event metric checks passed')
