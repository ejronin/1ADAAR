'use strict';
/* Standalone fictional PlayerOne timeline: never calls WARCON or other APIs.
   The 32 observation fixture is tested for exact parity. */
(function(){
  const key='demo-playerone';
  const entries=[
    ['2026-09-13','Bakurani',12,7,'win','Lonestar',2400],
    ['2026-09-14','Ozeti',19,5,'win','Valkyra',2400],
    ['2026-09-15','Zestafona',8,8,'loss','Manticore',2400],
    ['2026-09-16','Bakurani',16,4,'win','Lonestar',2400],
    ['2026-09-17','Ozeti',24,6,'win','Valkyra',2400],
    ['2026-09-18','Zestafona',11,9,'loss','Manticore',2400],
    ['2026-09-19','Bakurani',15,6,'win','Lonestar',2400],
    ['2026-09-20','Ozeti',20,7,'win','Valkyra',2400],
    ['2026-09-21','Zestafona',13,5,'loss','Manticore',2400],
    ['2026-09-22','Bakurani',17,7,'win','Lonestar',2400],
    ['2026-09-23','Ozeti',6,4,'draw','Valkyra',2400],
    ['2026-09-24','Zestafona',21,8,'win','Manticore',2400],
    ['2026-09-25','Bakurani',14,5,'loss','Lonestar',2400],
    ['2026-09-26','Ozeti',10,6,'win','Valkyra',2400],
    ['2026-09-27','Zestafona',22,7,'win','Manticore',2400],
    ['2026-09-28','Bakurani',16,5,'loss','Lonestar',2400],
    ['2026-09-29','Ozeti',18,7,'win','Valkyra',2400],
    ['2026-09-30','Zestafona',9,6,'win','Manticore',2400],
    ['2026-10-01','Bakurani',25,8,'loss','Lonestar',2400],
    ['2026-10-02','Ozeti',12,5,'win','Valkyra',2400],
    ['2026-10-03','Zestafona',17,6,'win','Manticore',2400],
    ['2026-10-04','Bakurani',20,7,'draw','Lonestar',2400],
    ['2026-10-05','Bakurani',9,16,'loss','Lonestar',1980],
    ['2026-10-06','Zestafona',27,9,'win','Manticore',2760],
    ['2026-10-07','Ozeti',12,14,'loss','Valkyra',2160],
    ['2026-10-08','Bakurani',24,10,'win','Lonestar',2460],
    ['2026-10-09','Zestafona',14,17,'loss','Manticore',2640],
    ['2026-10-10','Ozeti',20,7,'win','Valkyra',2340],
    ['2026-10-11','Bakurani',11,10,'draw','Lonestar',1740],
    ['2026-10-12','Zestafona',21,8,'win','Manticore',2280],
    ['2026-10-14','Ozeti',18,15,'loss','Valkyra',2160],
    ['2026-10-15','Bakurani',29,12,'win','Lonestar',2520]
  ];
  const matches=entries.map(([date,map,kills,deaths,result,faction,seconds])=>({
    id:0,endedAt:date+'T19:00:00Z',map,
    players:[{key,name:'PlayerOne',faction,result,kills,deaths,seconds}]
  }));
  const priorMinutes=[1803,1850,1896,1942,1988,2035,2081,2127,2173,2220];
  let kills=104,deaths=76,matchesPlayed=16,wins=8,losses=7,draws=1;
  const career=matches.slice().reverse().map((record,i)=>{
    const p=record.players[0];
    kills+=p.kills;deaths+=p.deaths;matchesPlayed++;
    wins+=Number(p.result==='win');losses+=Number(p.result==='loss');draws+=Number(p.result==='draw');
    const minutes=i<22?881+(i+1)*40:priorMinutes[i-22];
    return {date:record.endedAt.slice(0,10),kills,deaths,matches:matchesPlayed,
      wins,losses,draws,minutes};
  });
  window.OneADAARPerformance.mount(document.getElementById('performance-module'),{
    key,matches:matches.slice().reverse(),career,demo:true
  });
})();
