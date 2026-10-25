/* No-dependency forecast candidates for DAILY WARDOGS in-game gold prices.
   Rolling-origin validation and empirical error distributions, not stock trading advice.
*/
(function(root){
'use strict';
const DAY=86400000;
const NAMES={"naive":"No-change benchmark","ses":"Log-price exponential smoothing","damped":"Damped Holt log-trend","ar1":"AR(1) log-return regression","momentum":"Damped EWMA momentum"};
function clamp(x,a,b){return Math.max(a,Math.min(b,x));}
function quantile(values,q){
  const sorted=values.slice().sort((a,b)=>a-b);
  if(!sorted.length)return null;
  const rank=(sorted.length-1)*q,lo=Math.floor(rank),hi=Math.ceil(rank);
  return sorted[lo]+(sorted[hi]-sorted[lo])*(rank-lo);
}
function simulate(prices,name,horizon=7){
  if(!Array.isArray(prices)||prices.length<3||prices.some(p=>!Number.isFinite(p)||p<=0))return null;
  const logs=prices.map(Math.log);
  const last=logs[logs.length-1];
  let result=[];
  if(name==="naive"){
    result=Array(horizon).fill(last);
  }else if(name==="ses"){
    let level=logs[0],alpha=.38;
    for(let i=1;i<logs.length;i++)level=alpha*logs[i]+(1-alpha)*level;
    result=Array(horizon).fill(level);
  }else if(name==="damped"){
    const alpha=.40,beta=.10,phi=.86;
    let level=logs[0],slope=clamp((logs[Math.min(5,logs.length-1)]-logs[0])/Math.min(5,logs.length-1),-.18,.18);
    for(let i=1;i<logs.length;i++){
      const next=alpha*logs[i]+(1-alpha)*(level+phi*slope);
      slope=beta*(next-level)+(1-beta)*phi*slope;
      level=next;
    }
    let s=0;
    for(let h=1;h<=horizon;h++){s+=phi**h;result.push(level+s*slope);}
  }else if(name==="ar1"){
    const returns=logs.slice(1).map((x,i)=>x-logs[i]).slice(-42);
    if(returns.length<12)return null;
    const x=returns.slice(0,-1),y=returns.slice(1);
    const n=x.length,mx=x.reduce((a,b)=>a+b,0)/n,my=y.reduce((a,b)=>a+b,0)/n;
    let cov=0,variance=0;
    for(let i=0;i<n;i++){cov+=(x[i]-mx)*(y[i]-my);variance+=(x[i]-mx)**2;}
    const phi=clamp(cov/(variance+Math.max(0.0005,0.07*variance)),-.65,.65);
    const mu=clamp((my-phi*mx)*.65,-.12,.12);
    let state=returns[returns.length-1],level=last;
    for(let h=0;h<horizon;h++){state=clamp(mu+phi*state,-.30,.30);level+=state;result.push(level);}
  }else if(name==="momentum"){
    const returns=logs.slice(1).map((x,i)=>x-logs[i]);
    let ewma=returns[0];
    for(let i=1;i<returns.length;i++)ewma=.27*returns[i]+.73*ewma;
    let level=last;
    for(let h=1;h<=horizon;h++){level+=clamp(ewma,-.18,.18)*.67**h;result.push(level);}
  }else return null;
  return result.map(x=>Math.exp(clamp(x,Math.log(1),Math.log(1e9))));
}
function evaluate(rows){
  if(!Array.isArray(rows)||!rows.length)return {state:"insufficient",reason:"No recorded daily prices."};
  const ordered=rows.filter(r=>Number.isSafeInteger(r.ts)&&Number.isFinite(r.price)&&r.price>0).sort((a,b)=>a.ts-b.ts);
  if(!ordered.length)return {state:"insufficient",reason:"No valid prices."};
  let at=ordered.length-1;
  while(at>0&&ordered[at].ts-ordered[at-1].ts===DAY)at--;
  const contiguous=ordered.slice(at),prices=contiguous.map(r=>r.price),n=prices.length;
  if(n<49)return {state:"insufficient",reason:"At least 49 consecutive daily prices are needed for seven-day walk-forward validation."};
  const first=Math.max(28,n-7-21),last=n-8,count=last-first+1;
  if(count<14)return {state:"insufficient",reason:"Not enough completed validation windows."};
  const models={};
  for(const name of Object.keys(NAMES)){
    let total=0,terms=0;const errors=Array.from({length:7},()=>[]),absolutes=Array.from({length:7},()=>[]);
    for(let i=first;i<=last;i++){
      const projection=simulate(prices.slice(0,i+1),name,7);
      if(!projection)return {state:"insufficient",reason:"Not enough observations to validate the models."};
      for(let h=1;h<=7;h++){
        const actual=prices[i+h],prediction=projection[h-1];
        const residual=Math.log(actual/prediction);
        errors[h-1].push(residual);
        absolutes[h-1].push(Math.abs(prediction-actual));
        if(h===1||h===7){total+=Math.abs(residual);terms++;}
      }
    }
    models[name]={score:total/terms,errors,mae1:Math.round(absolutes[0].reduce((a,b)=>a+b,0)/count),mae7:Math.round(absolutes[6].reduce((a,b)=>a+b,0)/count)};
  }
  let selected="naive";
  for(const name of Object.keys(models)){
    if(models[name].score<models[selected].score)selected=name;
  }
  const base=models.naive.score;
  if(base===0||models[selected].score>base*.95)selected="naive";
  const outputs=simulate(prices,selected,7),latest=contiguous[n-1];
  const intervals=outputs.map((price,i)=>{
    const residuals=models[selected].errors[i];
    const l=price*Math.exp(quantile(residuals,.1)),u=price*Math.exp(quantile(residuals,.9));
    return {ts:latest.ts+(i+1)*DAY,price:Math.round(price),lower:Math.round(Math.max(1,Math.min(price,l))),upper:Math.round(Math.max(price,u))};
  });
  return {state:"ready",model:selected,modelLabel:NAMES[selected],rows:intervals,validations:count,baselineMae1:models.naive.mae1,baselineMae7:models.naive.mae7,modelMae1:models[selected].mae1,modelMae7:models[selected].mae7,improvementPct:base>0?Math.round(100*(1-models[selected].score/base)*10)/10:0,historyDays:n,asOf:latest.ts,intervalDescription:"Empirical 10th–90th percentile of walk-forward log errors; approximate and not guaranteed."};
}
const api=Object.freeze({simulate,evaluate,quantile,modelNames:NAMES});
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.GoldForecast=api;
})(typeof globalThis!=='undefined'?globalThis:this);
