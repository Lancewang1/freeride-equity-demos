'use strict';
const colors=['#aa7a22','#bd643d','#75899a','#46928a','#69598b'];
function chart(id,lines,unit){
 const el=document.getElementById(id),w=850,h=280,L=68,R=20,T=25,B=40;
 const values=lines.flatMap(x=>x.rows.map(r=>r.value));let lo=Math.min(...values),hi=Math.max(...values);const pad=(hi-lo)*.1||1;lo-=pad;hi+=pad;
 const dates=lines.flatMap(x=>x.rows.map(r=>Date.parse(r.date)));const d0=Math.min(...dates),d1=Math.max(...dates);
 const x=d=>L+(Date.parse(d)-d0)/(d1-d0||1)*(w-L-R),y=v=>T+(hi-v)/(hi-lo)*(h-T-B);
 let svg=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${unit}"><text x="${L}" y="16" fill="#5f7073" font-size="13">${unit}</text>`;
 for(let i=0;i<5;i++){const v=lo+(hi-lo)*i/4;svg+=`<line x1="${L}" x2="${w-R}" y1="${y(v)}" y2="${y(v)}" stroke="#dfe5e0"/><text x="${L-8}" y="${y(v)+5}" text-anchor="end" font-size="12" fill="#5f7073">${v.toLocaleString('en-US',{maximumFractionDigits:1})}</text>`;}
 for(let i=0;i<lines.length;i++){const line=lines[i];svg+=`<path fill="none" stroke="${colors[i]}" stroke-width="2.5" d="${line.rows.map((r,j)=>`${j?'L':'M'}${x(r.date).toFixed(2)},${y(r.value).toFixed(2)}`).join(' ')}"/>`;}
 for(const [d,anchor]of [[d0,'start'],[d1,'end']])svg+=`<text x="${d===d0?L:w-R}" y="${h-10}" text-anchor="${anchor}" font-size="12" fill="#5f7073">${new Date(d).toISOString().slice(0,10)}</text>`;
 el.innerHTML=svg+'</svg><div class="legend">'+lines.map((v,i)=>`<span style="color:${colors[i]}">● ${v.name}</span>`).join('')+'</div>';
}
function runModel(d,rows,v){
 const k=v.conversion/100;let delta=0;
 for(const r of rows){if(!['gold','copper'].includes(r.metal))continue;const dp=v[r.metal]/100;delta+=r.q*(1+v.volume/100)*(r.p*(1+dp)-r.c*(1+v.cost/100))*r.f-r.gp;}
 const q4=d.core_q3+delta*k+v.other*1e8,fy=d.np_9m+q4,eps=fy/d.shares_assumed;
 return {delta,q4,fy,eps,value:eps>0?eps*v.multiple:null};
}
window.runDepthModel=runModel;
async function init(){
 const [d,r,c]=await Promise.all(['depth_inputs.json','depth_results.json','depth_chart_data.json'].map(u=>fetch(u).then(x=>{if(!x.ok)throw Error(u);return x.json();})));
 const s=c.series;
 chart('regimeChart',[['WB_Gold','黄金'],['WB_Copper','铜'],['WB_Silver','白银'],['WB_Aluminum','铝'],['WB_Crude_oil','原油']].map(([key,name])=>({name,rows:s[key].map(v=>({...v,value:v.value/s[key][0].value*100}))})),'美元月均价格指数 · 2025-01=100');
 for(const [id,key,name,unit]of [['goldChart','Au9999','Au99.99 收盘','元/克'],['rateChart','DFII10','10 年 TIPS 实际收益率','% · 水平变化用 bp'],['copperChart','CU_MAIN','SHFE 主力结算（未复权）','元/吨'],['inventoryChart','CU_WARRANT_DOMESTIC','境内铜仓单（剔除保税）','吨']])chart(id,[{name,rows:s[key]}],unit);
 chart('curveChart',[{name:'10-23 铜期货结算期限结构，横轴为交割月份',rows:[108130,107310,106700,106330,106340,106240,106150,106160,106430,106060,105990,105800].map((value,i)=>({date:new Date(Date.UTC(2026,10+i,1)).toISOString().slice(0,10),value}))}],'元/吨 · 合约 CU2611 → CU2710');
 document.getElementById('gold').value=(d.scenarios.base.gold*100).toFixed(8);document.getElementById('copper').value=(d.scenarios.base.copper*100).toFixed(8);document.getElementById('conversion').value=(d.core_q3/d.pbt_q3*100).toFixed(8);
 function update(){const v={};for(const id of ['gold','copper','volume','cost','conversion','other','multiple']){const raw=document.getElementById(id).value;v[id]=raw===''?NaN:Number(raw);}
  const out=document.getElementById('modelOutput');if(Object.values(v).some(n=>!Number.isFinite(n))||['gold','copper','volume','cost'].some(k=>v[k]<=-100)||v.conversion<0||v.conversion>100||v.multiple<=0){out.innerHTML='<span class="error">请输入有效数值：量价成本变化须大于 −100%，转化系数为 0–100%，PE 须为正。</span>';return;}
  const z=runModel(d,r.products,v),yi=n=>(n/1e8).toFixed(2);window.depthLastResult=z;
  out.textContent=`Q4 归母 ${yi(z.q4)} 亿元 · FY 归母 ${yi(z.fy)} 亿元 · EPS ${z.eps.toFixed(3)} 元。距旧共识参照对应的 Q4 门槛 ${( (z.q4-r.required_q4_parent)/1e8).toFixed(2)} 亿元。`+(z.value===null?'全年亏损：PE 估值不适用。':`假设 ${v.multiple}× PE 的情景价值 ${z.value.toFixed(2)} 元，较公告前收盘 28.79 元 ${(100*(z.value/d.close-1)).toFixed(1)}%。该差距不等于真实预期差。`);
 }
 document.querySelectorAll('input').forEach(el=>el.addEventListener('input',update));update();window.depthReady=true;
}
init().catch(e=>{document.getElementById('modelOutput').textContent='模型数据未加载，请通过站点访问或本地 HTTP 服务打开。'+e.message;});
