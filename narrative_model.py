"""Recompute the six-step narrative's expectation and operating bridges.
All currency conversions, rounded-consensus inference and assumptions are explicit.
Run: python narrative_model.py --check
"""
from pathlib import Path
import json,math,sys,copy
from run_demo import consumer,metals,compare
D=Path(__file__).resolve().parent
def read(name):return json.loads((D/name).read_text('utf8'))
def solve():
    c=read('consumer_inputs.json');z=read('nonferrous_inputs.json');m=read('market_snapshot.json')
    cr=consumer(c)['scenarios'];zr=metals(z)['scenarios'];a=c['actuals'];b=z['actuals']
    fx=m['fx_anchor']['HKD_per_CNY'];cm=m['consumer'];zm=m['nonferrous']
    c_eps_hkd=cm['price_HKD']/cm['consensus_pe_2026'];c_eps_cny=c_eps_hkd/fx
    c_np=c_eps_cny*a['shares_thousand'];c_h2=c_np-a['np'];cn=cr[1]
    z_eps=zm['price_A_CNY']/zm['consensus_pe_A_2026'];z_np=z_eps*b['np']/b['eps'];zn=zr[1]
    factor=b['np']/b['pbt']
    copper=[x for x in z['mining_sales'] if x['scope'].startswith('矿山产铜/')]
    assert len(copper)==3
    cu_revenue=sum(x['quantity']*x['quantity_to_price_unit_factor']*x['price'] for x in copper)
    # Match by complete product category, avoiding an opaque position-dependent slice.
    assert cu_revenue>0
    cu_needed=(z_np-zn['fy_parent_np_CNY'])/(cu_revenue*1.03*factor)
    marginal=(1-a['material']/a['revenue']-.5*a['labor']/a['revenue']-a['other_expenses']/a['revenue']-(a['utilities']+a['travel'])/a['revenue'])*(1-a['tax']/a['pbt'])
    return {'consumer':{
      'implied_consensus_eps_HKD_2026':c_eps_hkd,'implied_consensus_eps_HKD_2027':cm['price_HKD']/cm['consensus_pe_2027'],
      'consensus_eps_growth_2027':cm['consensus_pe_2026']/cm['consensus_pe_2027']-1,
      'conditional_consensus_np_CNY_thousand':c_np,'required_h2_np_CNY_thousand':c_h2,
      'required_h2_growth_vs_H1':c_h2/a['np']-1,'required_h2_margin_at_neutral_revenue':c_h2/cn['h2_revenue'],
      'neutral_vs_benchmark':cn['fy_np']/c_np-1,
      'required_material_ratio_reduction_pp':(c_np-cn['fy_np'])/cn['h2_revenue']/(1-a['tax']/a['pbt'])*100,
      'required_main_sales_growth_vs_H1':.02+(c_np-cn['fy_np'])/(a['segments'][0]['current']*marginal),
      'main_sales_plus_1pct_h2_np_CNY_thousand':a['segments'][0]['current']*.01*marginal,
      'material_ratio_minus_1pp_h2_np_CNY_thousand':cn['h2_revenue']*.01*(1-a['tax']/a['pbt']),
      'neutral_break_even_PE':cm['price_HKD']/(cn['eps_CNY']*fx),
      'scenario_value_HKD_same_consensus_PE':[s['eps_CNY']*fx*cm['consensus_pe_2026'] for s in cr],
      'neutral_eps_fx_to_match_benchmark':c_eps_hkd/cn['eps_CNY'],
      'fx_sensitivity':[{'fx':f,'benchmark_np_CNY_thousand':c_eps_hkd/f*a['shares_thousand'],'neutral_gap':cn['eps_CNY']*f/c_eps_hkd-1} for f in [1.15,fx,1.20]]},
      'nonferrous':{'implied_consensus_eps_A_CNY_2026':z_eps,'implied_consensus_eps_A_CNY_2027':zm['price_A_CNY']/zm['consensus_pe_A_2027'],
      'consensus_eps_growth_A_2027':zm['consensus_pe_A_2026']/zm['consensus_pe_A_2027']-1,
      'conditional_consensus_np_CNY':z_np,'required_h2_np_CNY':z_np-b['np'],'neutral_vs_benchmark':zn['eps_CNY_approx']/z_eps-1,
      'required_copper_realized_price_change_vs_H1':cu_needed,
      'copper_plus_1pct_h2_np_CNY':cu_revenue*1.03*factor*.01,
      'scenario_value_A_CNY_same_consensus_PE':[s['eps_CNY_approx']*zm['consensus_pe_A_2026'] for s in zr],
      'neutral_break_even_PE_A':zm['price_A_CNY']/zn['eps_CNY_approx'],
      'single_broker_FY_np_CNY':b['np']+42467000000,
      'historical_copper_bridge':metals(z)['copper_concentrate_gp_bridge_CNY']}}
if __name__=='__main__':
    result=solve()
    if '--check' in sys.argv:
        compare(result,read('narrative_results.json'))
        # An independent identity: the copper-only price change must close the EPS gap.
        z=read('nonferrous_inputs.json');b=z['actuals'];target=result['nonferrous']['conditional_consensus_np_CNY']
        change=result['nonferrous']['required_copper_realized_price_change_vs_H1']
        delta=0
        for s in z['mining_sales']:
            pct=change if s['scope'].startswith('矿山产铜/') else 0
            delta+=s['quantity']*s['quantity_to_price_unit_factor']*(1.03*(s['price']*(1+pct)-s['cost']*1.02)-(s['price']-s['cost']))
        assert math.isclose(b['np']+b['core_np']+delta*b['np']/b['pbt'],target,rel_tol=1e-10)
        c=read('consumer_inputs.json');c['scenario_assumptions']=[copy.deepcopy(c['scenario_assumptions'][1])]
        c['scenario_assumptions'][0]['segment_growth_vs_H1'][0]=result['consumer']['required_main_sales_growth_vs_H1']
        actual=consumer(c)['scenarios'][0]['fy_np']
        assert math.isclose(actual,result['consumer']['conditional_consensus_np_CNY_thousand'],rel_tol=1e-10)
        print('Narrative calculations and operating break-even identities PASS')
    else:(D/'narrative_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
