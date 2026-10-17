'use strict';
/* Standalone fictional PlayerOne timeline. No live API or WARCON calls. */
(function(){
  const key='demo-playerone';
  const entries=[
    ['2026-10-15','Bakurani',29,12,'win'],
    ['2026-10-14','Ozeti',18,15,'loss'],
    ['2026-10-12','Zestafona',21,8,'win'],
    ['2026-10-11','Bakurani',11,10,'draw'],
    ['2026-10-10','Ozeti',20,7,'win'],
    ['2026-10-09','Zestafona',14,17,'loss'],
    ['2026-10-08','Bakurani',24,10,'win'],
    ['2026-10-07','Ozeti',12,14,'loss'],
    ['2026-10-06','Zestafona',27,9,'win'],
    ['2026-10-05','Bakurani',9,16,'loss']
  ];
  const matches=entries.map(([date,map,kills,deaths,result])=>({
    id:0,endedAt:date+'T19:00:00Z',map,players:[{key,kills,deaths,result}]
  }));
  let kills=449,deaths=214,matchesPlayed=38,wins=22,losses=13,draws=3;
  const career=matches.slice().reverse().map(record=>{
    const player=record.players[0];kills+=player.kills;deaths+=player.deaths;matchesPlayed++;
    wins+=Number(player.result==='win');
    losses+=Number(player.result==='loss');
    draws+=Number(player.result==='draw');
    return {date:record.endedAt.slice(0,10),kills,deaths,matches:matchesPlayed,
      wins,losses,draws,minutes:Math.floor(2220*matchesPlayed/48)};
  });
  window.OneADAARPerformance.mount(document.getElementById('performance-module'),{
    key,matches,career,demo:true
  });
})();
