/* 1ADAAR Steam 2.0 ownership proof and WARDOGS Tracker progression.
 * Isolated Cloudflare Free Worker + private D1, no Pages secrets or SteamIDs.
 * NO deployed service is implied by this source file.
 */
const STEAM='https://steamcommunity.com/openid/login';
const TRACKER='https://wardogstracker.gg/api/v1/players/';
const ACCOUNT=/^7656119[0-9]{10}$/;
const KEY=/^[a-f0-9]{64}$/;
const PKCE=/^[A-Za-z0-9_-]{43}$/;
const NO_STORE={'Cache-Control':'no-store, max-age=0','Referrer-Policy':'no-referrer',
  'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY'};
const now=()=>Math.floor(Date.now()/1000);
const text=new TextEncoder();
const random=()=>{const b=crypto.getRandomValues(new Uint8Array(32));return b64(b);};
const b64=b=>btoa(String.fromCharCode(...b)).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
const sha=async s=>new Uint8Array(await crypto.subtle.digest('SHA-256',text.encode(s)));
const hash=async s=>[...await sha(s)].map(n=>n.toString(16).padStart(2,'0')).join('');
const challenge=async s=>b64(await sha(s));
const pageKey=async id=>hash('1ADAAR:v1:'+id);

function headers(env,origin=''){
  const h=new Headers(NO_STORE);h.set('Content-Type','application/json; charset=utf-8');
  if(origin===env.PUBLIC_ORIGIN){
    h.set('Access-Control-Allow-Origin',origin);h.set('Vary','Origin');
    h.set('Access-Control-Allow-Methods','GET, POST, OPTIONS');
    h.set('Access-Control-Allow-Headers','Authorization, Content-Type');
    h.set('Access-Control-Max-Age','300');
  }
  return h;
}
const json=(data,status,env,origin='')=>
  new Response(JSON.stringify(data),{status,headers:headers(env,origin)});
const fail=(code,status,env,origin='')=>json({error:code},status,env,origin);
function destination(env,params={},player=''){
  const url=new URL(env.PUBLIC_PAGE_URL);
  for(const [k,v] of Object.entries(params))url.searchParams.set(k,v);
  if(player)url.hash='player-'+player;
  return url.toString();
}
function bounce(env,params,player){
  return new Response(null,{status:303,headers:{...NO_STORE,Location:destination(env,params,player)}});
}
async function bodyOf(req){
  if(Number(req.headers.get('content-length')||0)>16384)throw Error('body_too_large');
  const s=await req.text();if(s.length>16384)throw Error('body_too_large');
  const obj=JSON.parse(s);
  if(!obj||Array.isArray(obj)||typeof obj!=='object')throw Error('invalid_body');
  return obj;
}
const q=(env,sql,...args)=>env.DB.prepare(sql).bind(...args);
async function session(req,env){
  const h=req.headers.get('Authorization')||'';
  if(!/^Bearer [A-Za-z0-9_-]{32,100}$/.test(h))return null;
  const tokenHash=await hash(h.slice(7));
  const row=await q(env,'SELECT steam_id,player_key FROM sessions WHERE token_hash=? AND expires_at>?',tokenHash,now()).first();
  return row&&ACCOUNT.test(row.steam_id)&&KEY.test(row.player_key)?row:null;
}
async function verifySteam(url,env,stateHash){
  const p=url.searchParams;
  if(p.get('openid.mode')!=='id_res')return null;
  const claimed=p.get('openid.claimed_id')||'';
  const match=/^https?:\/\/steamcommunity\.com\/openid\/id\/(7656119\d{10})$/.exec(claimed);
  if(!match||!ACCOUNT.test(match[1])||
     p.get('openid.identity')!==claimed||
     p.get('openid.op_endpoint')!==STEAM||
     p.get('openid.ns')!=='http://specs.openid.net/auth/2.0')return null;
  const signed=(p.get('openid.signed')||'').split(',');
  if(!['claimed_id','identity','return_to','response_nonce','assoc_handle'].every(x=>signed.includes(x)))return null;
  if(p.get('openid.return_to')!==env.AUTH_ORIGIN+'/auth/callback?state='+stateHash)return null;
  const posted=new URLSearchParams();
  for(const [key,val] of p)if(key.startsWith('openid.')&&key!=='openid.mode')posted.append(key,val);
  posted.set('openid.mode','check_authentication');
  const response=await fetch(STEAM,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:posted.toString(),signal:AbortSignal.timeout(9000),redirect:'error'});
  if(!response.ok)return null;
  const answer=await response.text();
  return /^is_valid:true\s*$/m.test(answer)?match[1]:null;
}
async function loginStart(req,env){
  const url=new URL(req.url),pkce=url.searchParams.get('challenge')||'',
    player=url.searchParams.get('player')||'';
  if(!PKCE.test(pkce)||!KEY.test(player))return fail('invalid_login_request',400,env);
  const state=random(),stateHash=await hash(state);
  await q(env,'INSERT INTO login_states(state_hash,pkce_challenge,player_key,expires_at) VALUES(?,?,?,?)',
    stateHash,pkce,player,now()+300).run();
  const op=new URL(STEAM);
  const callback=env.AUTH_ORIGIN+'/auth/callback?state='+state;
  for(const [k,v] of Object.entries({'openid.ns':'http://specs.openid.net/auth/2.0',
    'openid.mode':'checkid_setup','openid.claimed_id':'http://specs.openid.net/auth/2.0/identifier_select',
    'openid.identity':'http://specs.openid.net/auth/2.0/identifier_select',
    'openid.return_to':callback,'openid.realm':env.AUTH_ORIGIN+'/'}))
    op.searchParams.set(k,v);
  return new Response(null,{status:302,headers:{...NO_STORE,Location:op.toString()}});
}
async function loginCallback(req,env){
  const url=new URL(req.url),state=url.searchParams.get('state')||'';
  if(!/^[A-Za-z0-9_-]{40,60}$/.test(state))return bounce(env,{progression_error:'invalid_state'});
  const stateHash=await hash(state);
  // Atomic single-use consume before checking network signatures prevents replay.
  const record=await q(env,'DELETE FROM login_states WHERE state_hash=? AND expires_at>? RETURNING pkce_challenge,player_key',
    stateHash,now()).first();
  if(!record)return bounce(env,{progression_error:'expired_login'});
  let steamId;
  try{steamId=await verifySteam(url,env,state);}
  catch(_){return bounce(env,{progression_error:'steam_unavailable'},record.player_key);}
  if(!steamId)return bounce(env,{progression_error:'verification_failed'},record.player_key);
  if(await pageKey(steamId)!==record.player_key)
    return bounce(env,{progression_error:'wrong_player'},record.player_key);
  const code=random();
  await q(env,'INSERT INTO exchange_codes(code_hash,steam_id,player_key,pkce_challenge,expires_at) VALUES(?,?,?,?,?)',
    await hash(code),steamId,record.player_key,record.pkce_challenge,now()+90).run();
  return bounce(env,{progression_code:code},record.player_key);
}
async function exchange(req,env,origin){
  const body=await bodyOf(req),code=body.code||'',verifier=body.verifier||'';
  if(!/^[A-Za-z0-9_-]{40,60}$/.test(code)||!PKCE.test(verifier))
    return fail('invalid_code',400,env,origin);
  const row=await q(env,'DELETE FROM exchange_codes WHERE code_hash=? AND expires_at>? RETURNING steam_id,player_key,pkce_challenge',
    await hash(code),now()).first();
  if(!row||await challenge(verifier)!==row.pkce_challenge)
    return fail('code_invalid_or_expired',401,env,origin);
  const token=random(),expiresAt=now()+2700;
  await q(env,'INSERT INTO sessions(token_hash,steam_id,player_key,expires_at) VALUES(?,?,?,?)',
    await hash(token),row.steam_id,row.player_key,expiresAt).run();
  return json({token,expiresAt,playerKey:row.player_key},200,env,origin);
}
async function consentFor(env,id){
  return q(env,'SELECT progression,economy FROM consents WHERE steam_id=?',id).first();
}
async function updateConsent(req,env,who,origin){
  const data=await bodyOf(req);
  if(data.progression!==true||typeof data.economy!=='boolean')
    return fail('explicit_consent_required',400,env,origin);
  await q(env,'INSERT INTO consents(steam_id,progression,economy,updated_at) VALUES(?,?,?,?) ON CONFLICT(steam_id) DO UPDATE SET progression=excluded.progression,economy=excluded.economy,updated_at=excluded.updated_at',
    who.steam_id,1,data.economy?1:0,now()).run();
  if(!data.economy)await q(env,'DELETE FROM progression_cache WHERE steam_id=?',who.steam_id).run();
  return json({state:'connected',progression:true,economy:data.economy},200,env,origin);
}
function normalize(payload,steamId,allowEconomy){
  if(!payload||payload.player?.steamId!==steamId)return null;
  const stats=payload.player.stats;
  if(!stats||!stats.roles||!Number.isSafeInteger(stats.wardogLevel)||
     !Number.isSafeInteger(stats.careerXp)||stats.wardogLevel<0||stats.careerXp<0||
     !Number.isFinite(Date.parse(stats.syncedAt)))return null;
  const names=['Assault','Medic','Support','Recon','Driver','Pilot'],levels={},xp={};
  for(const name of names){
    const raw=stats.roles[name.toLowerCase()];
    if(!raw||!Number.isInteger(raw.level)||raw.level<0||raw.level>100||
       !Number.isSafeInteger(raw.xp)||raw.xp<0)return null;
    levels[name]=raw.level;xp[name]=raw.xp;
  }
  const economy=v=>allowEconomy&&Number.isSafeInteger(v)&&v>=0?v:null;
  return {sourceStatus:'verified',source:'WARDOGS Tracker',dataScope:'Game-wide WARDOGS progression, not Dan\'s server combat stats',
    syncedAt:stats.syncedAt,maxLevel:100,levels,xp,wardogLevel:stats.wardogLevel,
    careerXp:stats.careerXp,cash:economy(stats.cash),gold:economy(stats.gold),
    economyConsented:allowEconomy};
}
async function progression(env,who,consent,force,origin){
  if(!consent?.progression)return json({state:'consent_required'},200,env,origin);
  const saved=await q(env,'SELECT payload,synced_at FROM progression_cache WHERE steam_id=?',who.steam_id).first();
  if(saved&&now()-saved.synced_at<60){
    const record=JSON.parse(saved.payload);
    return json({state:'connected',record,cached:true},200,env,origin);
  }
  let response;
  try{response=await fetch(TRACKER+who.steam_id,{headers:{Accept:'application/json'},
    redirect:'error',signal:AbortSignal.timeout(9000)});}
  catch(_){return fail('tracker_unavailable',503,env,origin);}
  if(response.status===404){
    await q(env,'DELETE FROM progression_cache WHERE steam_id=?',who.steam_id).run();
    return json({state:'not_synced_or_private',record:null},200,env,origin);
  }
  if(response.status===429)return fail('tracker_rate_limited',429,env,origin);
  if(!response.ok)return fail('tracker_unavailable',503,env,origin);
  const payload=await response.json();
  const record=normalize(payload,who.steam_id,Boolean(consent.economy));
  if(!record)return json({state:'not_synced_or_unavailable',record:null},200,env,origin);
  await q(env,'INSERT INTO progression_cache(steam_id,payload,synced_at) VALUES(?,?,?) ON CONFLICT(steam_id) DO UPDATE SET payload=excluded.payload,synced_at=excluded.synced_at',
    who.steam_id,JSON.stringify(record),now()).run();
  return json({state:'connected',record,cached:false},200,env,origin);
}
async function disconnect(env,who,origin){
  await env.DB.batch([
    q(env,'DELETE FROM sessions WHERE steam_id=?',who.steam_id),
    q(env,'DELETE FROM consents WHERE steam_id=?',who.steam_id),
    q(env,'DELETE FROM progression_cache WHERE steam_id=?',who.steam_id)
  ]);
  return json({state:'disconnected'},200,env,origin);
}
export default {
  async fetch(req,env){
    const origin=req.headers.get('Origin')||'';
    if(!env.DB||!env.AUTH_ORIGIN||!env.PUBLIC_ORIGIN||!env.PUBLIC_PAGE_URL||
       env.AUTH_ORIGIN.includes('REPLACE'))return fail('service_not_configured',503,env,origin);
    const url=new URL(req.url),path=url.pathname;
    if(url.origin!==env.AUTH_ORIGIN)return fail('invalid_host',403,env,origin);
    if(req.method==='OPTIONS')
      return origin===env.PUBLIC_ORIGIN?
        new Response(null,{status:204,headers:headers(env,origin)}):
        fail('forbidden_origin',403,env);
    if(path==='/health'&&req.method==='GET')return json({ok:true,service:'1ADAAR progression auth'},200,env);
    if(path==='/auth/start'&&req.method==='GET')return loginStart(req,env);
    if(path==='/auth/callback'&&req.method==='GET')return loginCallback(req,env);
    if(origin!==env.PUBLIC_ORIGIN)return fail('forbidden_origin',403,env);
    try{
      if(path==='/api/exchange'&&req.method==='POST')return exchange(req,env,origin);
      const who=await session(req,env);
      if(!who)return fail('unauthenticated',401,env,origin);
      const consent=await consentFor(env,who.steam_id);
      if(path==='/api/me'&&req.method==='GET')
        return json({state:consent?.progression?'connected':'consent_required',playerKey:who.player_key,
          economy:Boolean(consent?.economy)},200,env,origin);
      if(path==='/api/consent'&&req.method==='POST')return updateConsent(req,env,who,origin);
      if(path==='/api/progression'&&req.method==='GET')return progression(env,who,consent,false,origin);
      if(path==='/api/refresh'&&req.method==='POST')return progression(env,who,consent,true,origin);
      if(path==='/api/disconnect'&&req.method==='POST')return disconnect(env,who,origin);
      return fail('not_found',404,env,origin);
    }catch(_){return fail('request_failed',400,env,origin);}
  }
};
export const internalForTests={normalize,pageKey,challenge,verifySteam};
