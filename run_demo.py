"""Recompute both demos from bundled inputs. Python standard library only.
Usage: python run_demo.py [--check]
"""
from pathlib import Path
import json,math,sys
D=Path(__file__).resolve().parent
def read(n):return json.loads((D/n).read_text('utf8'))
def compare(a,b,path='root'):
    if isinstance(b,dict):
        for k,v in b.items():compare(a[k],v,path+'.'+k)
    elif isinstance(b,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+str(i))
    elif isinstance(b,(int,float)) and not isinstance(b,bool):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-5),(path,a,b)
    else:assert a==b,(path,a,b)
def consumer(data):
    h=data['actuals'];results=[]
    assert sum(s['current'] for s in h['segments'])==h['revenue']
    for c in data['scenario_assumptions']:
        r=sum(s['current']*(1+g) for s,g in zip(h['segments'],c['segment_growth_vs_H1']));ratio=r/h['revenue']
        mat=r*(h['material']/h['revenue']+c['material_ratio_delta']);e=c['labor_volume_elasticity']
        lab=h['labor']*(e*ratio+(1-e)*(1+c['fixed_labor_inflation']));other=r*(h['other_expenses']/h['revenue']+c['other_expense_ratio_delta'])
        pbt=r-mat-lab-other-(h['utilities']+h['travel'])*ratio-h['rent']-h['da']+h['other_income']+h['associate']+h['other_gains']-h['finance_cost']
        tax=pbt*h['tax']/h['pbt'];np=pbt-tax+h['np']-h['group_profit'];fy=h['np']+np;eps=fy/h['shares_thousand']
        results.append(dict(name=c['name'],h2_revenue=r,h2_material=mat,h2_labor=lab,h2_other_expenses=other,h2_pbt=pbt,h2_tax=tax,h2_np=np,fy_revenue=h['revenue']+r,fy_np=fy,eps_CNY=eps,pe_assumption=c['pe'],value_CNY_per_share=eps*c['pe'],status='illustrative_conditional_scenario'))
    derived={'revenue_growth':h['revenue']/h['prior_revenue']-1,'np_growth':h['np']/h['prior_np']-1,'same_store_growth':h['same_store_sales'][0]/h['same_store_sales'][1]-1,'cfo_growth':h['cfo']/h['prior_cfo']-1,'net_margin':h['np']/h['revenue'],'prior_net_margin':h['prior_np']/h['prior_revenue'],'cash_after_ppe_intangibles_rou_lease_interest':h['cfo']-sum(h[k] for k in ['ppe','intangibles','rou_cash','lease_principal','interest_financing'])}
    return {'derived_actuals':derived,'scenarios':results}
def metals(data):
    z=data['actuals'];results=[];tax=1-z['total_profit']/z['pbt'];parent=z['np']/z['total_profit']
    for c in data['scenario_assumptions']:
        delta=sum(m['quantity']*m['quantity_to_price_unit_factor']*((1+c['sales_volume_change'])*(m['price']*(1+c['price_change'])-m['cost']*(1+c['unit_cost_change']))-(m['price']-m['cost'])) for m in data['mining_sales'])
        h2=z['core_np']+delta*(1-tax)*parent;fy=z['np']+h2;eps=z['eps']*fy/z['np']
        results.append(dict(name=c['name'],h2_selected_mining_gp_delta_CNY=delta,h2_parent_np_CNY=h2,fy_parent_np_CNY=fy,eps_CNY_approx=eps,pe_assumption=c['pe'],value_CNY_per_share_approx=eps*c['pe'],status='partial_driver_conditional_scenario'))
    derived={'revenue_growth':z['revenue']/z['prior_revenue']-1,'np_growth':z['np']/z['prior_np']-1,'core_np_growth':z['core_np']/z['prior_core_np']-1,'cfo_growth':z['cfo']/z['prior_cfo']-1,'cfo_less_capex':z['cfo']-z['capex_cash'],'copper_production_growth':z['mined_cu'][0]/z['mined_cu'][1]-1,'copper_ex_kamoa_growth':z['cu_ex_kamoa'][0]/z['cu_ex_kamoa'][1]-1,'effective_tax_rate':tax,'parent_profit_share':parent}
    bridge={'volume':(353831-330599)*(60354-21104),'price':353831*(82624-60354),'unit_cost':-353831*(24480-21104),'total':353831*(82624-24480)-330599*(60354-21104)}
    return {'derived_actuals':derived,'copper_concentrate_gp_bridge_CNY':bridge,'scenarios':results}
if __name__=='__main__':
    for sector,fn in [('consumer',consumer),('nonferrous',metals)]:
        result=fn(read(sector+'_inputs.json'))
        if '--check' in sys.argv:compare(result,read(sector+'_results.json'));print(sector+': all published calculations reproduced')
        else:(D/(sector+'_recalculated.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(sector+': recalculated JSON saved; HTML is the original reviewed snapshot')
