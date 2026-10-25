"""Zijin commodity-to-earnings demonstration. Amounts CNY unless specified.
Run: python depth_model.py. Only reads committed, non-secret input JSON.
"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def derive(h1,nine):
    q=nine['q']-h1['quantity']; f=h1['quantity_to_price_unit_factor']
    p=(nine['q']*nine['p']-h1['quantity']*h1['price'])/q
    c=(nine['q']*nine['c']-h1['quantity']*h1['cost'])/q
    baseq=h1['quantity']/2
    bridge={'volume':(q-baseq)*(h1['price']-h1['cost'])*f,
            'price':q*(p-h1['price'])*f,'cost':-q*(c-h1['cost'])*f}
    gp=q*(p-c)*f; basegp=baseq*(h1['price']-h1['cost'])*f
    assert math.isclose(sum(bridge.values()),gp-basegp,abs_tol=.01)
    return dict(name=h1['scope'],q=q,p=p,c=c,f=f,metal=nine['metal'],h1_p=h1['price'],h1_c=h1['cost'],base_q=baseq,gp=gp,base_gp=basegp,bridge=bridge)

def scenario(d,rows,gold=0,copper=0,volume=0,cost=0,conversion=None,other=0):
    """Changes relative to derived Q3 price, sales volume and cost, not spot.
    Other is an explicit *parent* profit adjustment in CNY (M&A/FX/etc.).
    """
    vals=[gold,copper,volume,cost,other]
    if not all(math.isfinite(v) for v in vals) or min(gold,copper,volume,cost)<=-1:raise ValueError('Invalid driver')
    k=d['core_q3']/d['pbt_q3'] if conversion is None else conversion
    if not math.isfinite(k) or not 0<=k<=1:raise ValueError('Invalid conversion')
    delta=0
    for r in rows:
        if r['metal'] not in ['gold','copper']:continue
        dp=gold if r['metal']=='gold' else copper
        delta+=r['q']*(1+volume)*(r['p']*(1+dp)-r['c']*(1+cost))*r['f']-r['gp']
    q4=d['core_q3']+delta*k+other
    full=d['np_9m']+q4 # Q4 nonrecurring assumed zero; 9M actual includes it.
    return {'delta_gp':delta,'conversion':k,'q4_parent':q4,'fy_parent':full,'eps':full/d['shares_assumed'],'pe_at_close':d['close']/ (full/d['shares_assumed']) if full>0 else None}

def calculate(d,h):
    rows=[derive(a,b) for a,b in zip(h['mining_sales'],d['nine_month_products'])]
    cases={name:scenario(d,rows,**v) for name,v in d['scenarios'].items()}
    eps_ref=d['consensus_price']/d['consensus_pe']
    required=eps_ref*d['shares_assumed']-d['np_9m']
    k=d['core_q3']/d['pbt_q3']
    copper_rev=sum(r['q']*r['p']*r['f'] for r in rows if r['metal']=='copper')
    base=cases['base']
    reverse=(required-base['q4_parent'])/(copper_rev*k)+d['scenarios']['base']['copper']
    check=scenario(d,rows,gold=d['scenarios']['base']['gold'],copper=reverse)
    assert math.isclose(check['q4_parent'],required,abs_tol=.001)
    gp_delta=sum(r['gp']-r['base_gp'] for r in rows)
    pbt_delta=d['pbt_q3']-h['actuals']['pbt']/2
    return {'products':rows,'cases':cases,'eps_reference':eps_ref,'required_q4_parent':required,
      'required_q4_vs_actual_q3':required/d['np_q3']-1,'reverse_copper_realized_change':reverse,
      'single_broker_miss':d['np_q3']/d['broker_q3_forecast']-1,
      'bridge':{'selected_gp_delta':gp_delta,'pbt_delta':pbt_delta,'unallocated_pbt_residual':pbt_delta-gp_delta},
      'sensitivities':{m:scenario(d,rows,**{m:.01})['q4_parent']-d['core_q3'] for m in ['gold','copper','cost']},
      'cash':{'q3_capex':d['capex_9m']-h['actuals']['capex_cash'],'nine_month_cfo_minus_capex':d['cfo_9m']-d['capex_9m'],'q3_cfo_minus_capex':d['cfo_q3']-(d['capex_9m']-h['actuals']['capex_cash'])}}

if __name__=='__main__':
    d=json.loads((ROOT/'depth_inputs.json').read_text('utf8'));h=json.loads((ROOT/'nonferrous_inputs.json').read_text('utf8'))
    out=calculate(d,h)
    (ROOT/'depth_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    print(json.dumps({k:v for k,v in out.items() if k!='products'},ensure_ascii=False,indent=2))
