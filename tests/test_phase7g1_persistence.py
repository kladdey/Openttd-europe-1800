import sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cycles_phase7g1_persistence import validate,ROOT
class PersistenceReceiptTests(unittest.TestCase):
 def lines(self):return json.loads((ROOT/'docs/research/phase7g1_persistence_receipts.json').read_text())['raw']['observations']
 def test_real_ended_reload_preserves_state(self):
  r=validate(self.lines());self.assertEqual(r['before']['target'],r['after']['target']);self.assertEqual(r['after']['flags'],'0');self.assertEqual(r['after']['industries'],'543')
 def test_changed_timer_or_schema_is_rejected(self):
  for old,new in [('last_change=668667','last_change=668668'),('schema=5','schema=4')]:
   lines=self.lines();index=next(i for i,s in enumerate(lines) if 'g1_snapshot|after|' in s);lines[index]=lines[index].replace(old,new)
   with self.assertRaises(ValueError):validate(lines)
 def test_no_duplicate_or_failed_observation_is_passed(self):
  for extra in ['P7 EVENT|cycle_opened|ruhr|industry=543','P7 EVENT|cycle_level|boom|level=32','P7 G1_ERROR|failed']:
   with self.assertRaises(ValueError):validate(self.lines()+[extra])
if __name__=='__main__':unittest.main()
