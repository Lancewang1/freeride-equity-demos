"""Reproduce V4 cycle metrics from published company facts and V3 model inputs."""
import json,math
from pathlib import Path
from depth_model import scenario
ROOT=Path(__file__).resolve().parent
def calculate():
 d=json.loads((ROOT/'depth_inputs.json').read_text('utf8'))
 h=json.loads((ROOT/'nonferrous_inputs.json').read_text('utf8'))
 r=json.loads((ROOT/'depth_results.json').read_text('utf8'))
 facts=json.loads((ROOT/'cycle_metrics.json').read_text('utf8'))
 a=d['capex_9m'];b=facts['capex_9m_prior']
 q=a-h['actuals']['capex_cash'];prior_q=b-h['actuals']['prior_capex_cash']
 result={'capex_9m_yoy':a/b-1,'capex_q3':q,'capex_q3_prior':prior_q,
  'capex_q3_yoy':q/prior_q-1,'cfo_capex_9m':d['cfo_9m']/a,'cfo_capex_q3':d['cfo_q3']/q,
  'construction_ytd':facts['construction_20260930']/facts['construction_20251231']-1,
  'gold_copper_minus10':scenario(d,r['products'],gold=-.1,copper=-.1),
  'pe_thresholds':[{'pe':pe,'required_eps':d['close']/pe,'required_fy_parent':d['close']/pe*d['shares_assumed'],'required_q4_parent':d['close']/pe*d['shares_assumed']-d['np_9m']} for pe in [8,9.5,11,13]]}
 for key,val in result.items():
  if isinstance(val,(int,float)):assert math.isclose(val,facts[key],abs_tol=.001)
  else:assert val==facts[key]
 for row in result['pe_thresholds']:
  assert math.isclose((d['np_9m']+row['required_q4_parent'])/d['shares_assumed']*row['pe'],d['close'])
 return result
if __name__=='__main__':print(json.dumps(calculate(),ensure_ascii=False,indent=2))
