"""Deterministic research calculations. Values must already share currency/unit/basis."""
import math
def finite(*xs):
    if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in xs):raise ValueError('finite numeric inputs required')
def growth(current,prior):
    finite(current,prior)
    if prior<=0:raise ValueError('positive comparable base required')
    return current/prior-1
def same_store(current,prior,current_cohort,prior_cohort):
    if not current_cohort or current_cohort!=prior_cohort:raise ValueError('cohort mismatch')
    return growth(current,prior)
def gross_profit(q,p,c):
    finite(q,p,c)
    if q<0:raise ValueError('negative physical sales')
    return q*(p-c)
def profit_bridge(q0,p0,c0,q1,p1,c1):
    # Exact sequential identity; price/cost effects use current volume.
    before=gross_profit(q0,p0,c0);after=gross_profit(q1,p1,c1)
    return {'volume':(q1-q0)*(p0-c0),'price':q1*(p1-p0),'unit_cost':-q1*(c1-c0),'total':after-before}
def pe_value(net_profit,shares,pe,quote_currency_per_profit_currency=1):
    finite(net_profit,shares,pe,quote_currency_per_profit_currency)
    if shares<=0 or pe<=0 or quote_currency_per_profit_currency<=0:raise ValueError('positive denominator/multiple/FX required')
    if net_profit<=0:return None
    return net_profit/shares*pe*quote_currency_per_profit_currency
def cash_after_investment(cfo,ppe,intangibles=0,rou_cash=0,lease_principal=0,financing_interest=0):
    finite(cfo,ppe,intangibles,rou_cash,lease_principal,financing_interest)
    if min(ppe,intangibles,rou_cash,lease_principal,financing_interest)<0:raise ValueError('cash outflows use positive magnitudes')
    return cfo-ppe-intangibles-rou_cash-lease_principal-financing_interest
