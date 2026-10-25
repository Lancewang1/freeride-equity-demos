'use strict';
const data=JSON.parse(document.getElementById('model-data').textContent);
const a=data.actual.actuals, market=data.market, output=document.getElementById('operating-result');
const isConsumer=data.sector==='consumer';
const defaults=isConsumer?{mainGrowth:2,deliveryGrowth:15,materialDelta:0,fx:1.17025}:{copperPrice:0,goldPrice:0,volume:3,cost:2};
const fmt=(n,d=2)=>n.toFixed(d), pct=n=>(n*100).toFixed(1)+'%';
function calculate(){
  const v={};
  for(const id of Object.keys(defaults)){
    const el=document.getElementById(id),raw=el.value;
    v[id]=Number(raw);
    if(raw.trim()===''||!Number.isFinite(v[id])||!el.checkValidity()){
      output.textContent='请输入有效范围内的数值；缺失输入不按零处理。';output.dataset.valid='false';return;
    }
  }
  let fy,eps,benchmark,value,pe,price,unit,body;
  if(isConsumer){
    const growth=[v.mainGrowth/100,v.deliveryGrowth/100,.15,.10,.20,0];
    const revenue=a.segments.reduce((s,x,i)=>s+x.current*(1+growth[i]),0),ratio=revenue/a.revenue;
    const materialRate=a.material/a.revenue+v.materialDelta/100;
    if(revenue<=0||materialRate<0||materialRate>1){output.textContent='该收入或材料费率超出模型有效范围。';output.dataset.valid='false';return;}
    const material=revenue*materialRate,labor=a.labor*(.5*ratio+.5*1.01),other=revenue*a.other_expenses/a.revenue;
    const pbt=revenue-material-labor-other-(a.utilities+a.travel)*ratio-a.rent-a.da+a.other_income+a.associate+a.other_gains-a.finance_cost;
    const h2=pbt*(1-a.tax/a.pbt)+a.np-a.group_profit;
    fy=a.np+h2;eps=fy/a.shares_thousand;
    pe=market.consumer.consensus_pe_2026;price=market.consumer.price_HKD;benchmark=price/pe/v.fx;
    value=eps*v.fx*pe;unit='港币';
    body=`H2 收入 ${fmt(revenue/1e5)} 亿元，归母 ${fmt(h2/1e5)} 亿元；全年归母 <strong>${fmt(fy/1e5)} 亿元</strong>，EPS ${fmt(eps,3)} 人民币元。`;
  }else{
    let delta=0;
    for(const p of data.actual.mining_sales){
      const priceChange=p.scope.startsWith('矿山产铜/')?v.copperPrice/100:p.scope.startsWith('矿山产金/')?v.goldPrice/100:0;
      delta+=p.quantity*p.quantity_to_price_unit_factor*((1+v.volume/100)*(p.price*(1+priceChange)-p.cost*(1+v.cost/100))-(p.price-p.cost));
    }
    const h2=a.core_np+delta*a.np/a.pbt;fy=a.np+h2;eps=a.eps*fy/a.np;
    pe=market.nonferrous.consensus_pe_A_2026;price=market.nonferrous.price_A_CNY;benchmark=price/pe;
    value=eps*pe;unit='人民币';
    body=`H2 归母 ${fmt(h2/1e8)} 亿元；全年归母 <strong>${fmt(fy/1e8)} 亿元</strong>，近似 EPS ${fmt(eps,3)} 人民币元。`;
  }
  const gap=eps/benchmark-1,verdict=gap>=0?'达到或高于':'低于';
  output.dataset.valid='true';output.dataset.eps=eps;output.dataset.gap=gap;output.dataset.fy=fy;
  const valuation=eps>0?`固定快照 PE ${pe} 倍的条件价值：${fmt(value)} ${unit}元/股（相对快照价格 ${pct(value/price-1)}）。`:'全年盈利非正，PE 估值不适用。';
  output.innerHTML=`<p>${body}</p><p>该情景<strong>${verdict}</strong>条件盈利参照 ${pct(Math.abs(gap))}。${valuation}</p><small style="color:#d7e6eb">比较假设利润口径可比；${isConsumer?'汇率与股数须核验':'股本、内部抵销与共识 EPS 定义须核验'}。这回答经营门槛，不自动构成买卖结论。静态表保留原中性情景，当前调整仅更新此结果框。</small>`;
}
for(const id of Object.keys(defaults))document.getElementById(id).addEventListener('input',calculate);
document.getElementById('reset').addEventListener('click',()=>{for(const[id,value]of Object.entries(defaults))document.getElementById(id).value=value;calculate();});
calculate();
