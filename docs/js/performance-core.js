'use strict';
/* Pure performance calculations; testable without a browser or WARCON. */
(function (root) {
  const isCount = n => Number.isSafeInteger(n) && n >= 0;
  const displayRatio = (kills, deaths) => !kills && !deaths ? null : deaths === 0 ? kills : kills / deaths;
  const round = n => n === null || !Number.isFinite(n) ? null : Math.round(n * 100) / 100;
  function matchSeries(matches, key) {
    if (!Array.isArray(matches) || typeof key !== 'string') return [];
    const seen = new Set(), rows = [];
    for (const match of matches) {
      if (!match || !Array.isArray(match.players) || typeof match.endedAt !== 'string') continue;
      const ts = Date.parse(match.endedAt);
      if (!Number.isFinite(ts)) continue;
      const p = match.players.find(player => player && player.key === key);
      if (!p || !isCount(p.kills) || !isCount(p.deaths)) continue;
      // The demo fixture intentionally has ID 0 for all synthetic examples.
      const unique = Number.isSafeInteger(match.id) && match.id > 0 ? String(match.id) : null;
      if (unique !== null && seen.has(unique)) continue;
      if (unique !== null) seen.add(unique);
      rows.push({date:match.endedAt, ts, map:typeof match.map === 'string' ? match.map : 'Unknown map',
        id:unique, kills:p.kills, deaths:p.deaths,
        kd:round(displayRatio(p.kills,p.deaths)), rolling:null});
    }
    rows.sort((a,b) => a.ts - b.ts || String(a.id).localeCompare(String(b.id)));
    for (let i = 4; i < rows.length; i++) {
      const last = rows.slice(i-4,i+1);
      const kills = last.reduce((sum,r)=>sum+r.kills,0);
      const deaths = last.reduce((sum,r)=>sum+r.deaths,0);
      rows[i].rolling = round(displayRatio(kills,deaths));
    }
    return rows;
  }
  function careerSeries(points) {
    if (!Array.isArray(points)) return [];
    const byDate = new Map();
    for(const p of points) {
      if (!p || typeof p.date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(p.date) || !isCount(p.kills) ||
          !isCount(p.deaths) || !isCount(p.matches) || !isCount(p.wins)) continue;
      const ts = Date.parse(p.date + 'T12:00:00Z');
      if (!Number.isFinite(ts)) continue;
      byDate.set(p.date, {date:p.date,ts,kills:p.kills,deaths:p.deaths,matches:p.matches,wins:p.wins,
        kd:round(displayRatio(p.kills,p.deaths))});
    }
    return [...byDate.values()].sort((a,b)=>a.ts-b.ts);
  }
  function windowed(series, limit) {
    const n = limit === 10 || limit === 25 ? limit : Infinity;
    return series.slice(Math.max(0,series.length-n));
  }
  const format = n => n === null || !Number.isFinite(n) ? '—' : n.toFixed(2);
  const tickDate = stamp => {
    const date = new Date(stamp);
    return Number.isFinite(date.getTime())
      ? date.toLocaleDateString(undefined,{month:'short',day:'numeric'}) : '—';
  };
  const api = Object.freeze({matchSeries,careerSeries,windowed,format,tickDate});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.OneADAARMetrics = api;
})(typeof window === 'undefined' ? null : window);
