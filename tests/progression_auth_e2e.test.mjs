/* End-to-end offline Steam signature / D1 replay / progression/consent test.
 * Uses simulated Steam and Tracker HTTP. Not a claim of live authentication. */
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {webcrypto} from 'node:crypto';
import worker,{internalForTests as core} from '../services/steam-progression/worker.mjs';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const ID='76561190000000001';
const AUTH='https://1adaar-auth.example.workers.dev';
const ORIGIN='https://ejronin.github.io';
class FakeDb {
  constructor(){this.states=new Map();this.codes=new Map();this.sessions=new Map();
    this.consents=new Map();this.cache=new Map();}
  prepare(sql){
    const me=this;
    return {bind(...a){return {
      async first(){
        if(sql.startsWith('DELETE FROM login_states')){
          const v=me.states.get(a[0]);if(v&&v.expires_at>a[1]){me.states.delete(a[0]);return v;}return null;
        }
        if(sql.startsWith('DELETE FROM exchange_codes')){
          const v=me.codes.get(a[0]);if(v&&v.expires_at>a[1]){me.codes.delete(a[0]);return v;}return null;
        }
        if(sql.startsWith('SELECT steam_id,player_key FROM sessions')){
          const v=me.sessions.get(a[0]);return v&&v.expires_at>a[1]?v:null;
        }
        if(sql.startsWith('SELECT progression,economy FROM consents'))return me.consents.get(a[0])||null;
        if(sql.startsWith('SELECT payload,synced_at FROM progression_cache'))return me.cache.get(a[0])||null;
        throw Error('Unhandled D1 first: '+sql);
      },
      async run(){
        if(sql.startsWith('INSERT INTO login_states')){
          me.states.set(a[0],{pkce_challenge:a[1],player_key:a[2],return_route:a[3],expires_at:a[4]});
        }else if(sql.startsWith('INSERT INTO exchange_codes')){
          me.codes.set(a[0],{steam_id:a[1],player_key:a[2],pkce_challenge:a[3],expires_at:a[4]});
        }else if(sql.startsWith('INSERT INTO sessions')){
          me.sessions.set(a[0],{steam_id:a[1],player_key:a[2],expires_at:a[3]});
        }else if(sql.startsWith('INSERT INTO consents')){
          me.consents.set(a[0],{progression:a[1],economy:a[2],updated_at:a[3]});
        }else if(sql.startsWith('INSERT INTO progression_cache')){
          me.cache.set(a[0],{payload:a[1],synced_at:a[2]});
        }else if(sql.startsWith('DELETE FROM sessions WHERE steam_id')){
          for(const [k,v] of me.sessions)if(v.steam_id===a[0])me.sessions.delete(k);
        }else if(sql.startsWith('DELETE FROM consents WHERE steam_id'))me.consents.delete(a[0]);
        else if(sql.startsWith('DELETE FROM progression_cache WHERE steam_id'))me.cache.delete(a[0]);
        else throw Error('Unhandled D1 run: '+sql);
        return {success:true};
      }};}};
  }
  async batch(statements){for(const s of statements)await s.run();}
}
const db=new FakeDb();
const env={DB:db,AUTH_ORIGIN:AUTH,PUBLIC_ORIGIN:ORIGIN,
  PUBLIC_PAGE_URL:ORIGIN+'/1ADAAR/players.html',
  PUBLIC_PROGRESSION_URL:ORIGIN+'/1ADAAR/progression.html'};
const tracker={player:{steamId:ID,stats:{syncedAt:'2026-10-22T18:12:00Z',
  wardogLevel:72,careerXp:234000,cash:400,gold:0,roles:{
    assault:{level:5,xp:1000},medic:{level:8,xp:4000},support:{level:3,xp:300},
    recon:{level:15,xp:14000},driver:{level:2,xp:80},pilot:{level:0,xp:0}
  }}}};
async function api(path,method,body,token){
  const r=await worker.fetch(new Request(AUTH+path,{
    method,headers:{Origin:ORIGIN,...(token?{Authorization:'Bearer '+token}:{}),
      ...(body?{'Content-Type':'application/json'}:{})},
    ...(body?{body:JSON.stringify(body)}:{})
  }),env);
  return [r,await r.json()];
}
async function login(route,player=''){
  const verifier='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234'.slice(0,43);
  const challenge=await core.challenge(verifier);
  const r=await worker.fetch(new Request(AUTH+'/auth/start?challenge='+challenge+
    '&route='+route+(player?'&player='+player:'')),env);
  assert.equal(r.status,302);
  const steam=new URL(r.headers.get('Location'));
  const returnTo=steam.searchParams.get('openid.return_to');
  const callback=new URL(returnTo);
  const fields={
    'openid.mode':'id_res','openid.ns':'http://specs.openid.net/auth/2.0',
    'openid.claimed_id':'http://steamcommunity.com/openid/id/'+ID,
    'openid.identity':'http://steamcommunity.com/openid/id/'+ID,
    'openid.op_endpoint':'https://steamcommunity.com/openid/login',
    'openid.return_to':returnTo,
    'openid.signed':'claimed_id,identity,return_to,response_nonce,assoc_handle',
    'openid.response_nonce':'2026-10-22T16:33:00Z1',
    'openid.assoc_handle':'mockhandle'
  };
  for(const [k,v] of Object.entries(fields))callback.searchParams.set(k,v);
  const response=await worker.fetch(new Request(callback),env);
  assert.equal(response.status,303);
  return {url:new URL(response.headers.get('Location')),verifier,callback};
}

test('complete standalone sign-in: one-use code, consent, hidden economy, refresh, and revoke',async()=>{
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async url=>{
    if(String(url).startsWith('https://steamcommunity.com/openid/login'))
      return new Response('is_valid:true\n',{status:200});
    if(String(url).startsWith('https://wardogstracker.gg/api/v1/players/'))
      return Response.json(tracker);
    throw Error('Unexpected remote URL: '+url);
  };
  try{
    const {url,verifier,callback}=await login('standalone');
    assert.equal(url.pathname,'/1ADAAR/progression.html');
    const code=url.searchParams.get('progression_code');
    const [ex,session]=await api('/api/exchange','POST',{code,verifier});
    assert.equal(ex.status,200);assert.match(session.playerKey,/^[a-f0-9]{64}$/);
    assert.ok(session.token.length>=40);
    const [reuse]=await api('/api/exchange','POST',{code,verifier});
    assert.equal(reuse.status,401,'Code replay must fail');
    const replay=await worker.fetch(new Request(callback),env);
    assert.match(replay.headers.get('Location'),/progression_error=expired_login/);
    const [me,unlinked]=await api('/api/me','GET',null,session.token);
    assert.equal(me.status,200);assert.equal(unlinked.state,'consent_required');
    const [pre,preResult]=await api('/api/progression','GET',null,session.token);
    assert.equal(pre.status,200);assert.equal(preResult.state,'consent_required');
    const [bad]=await api('/api/consent','POST',{progression:true,economy:'yes'},session.token);
    assert.equal(bad.status,400);
    const [allow]=await api('/api/consent','POST',{progression:true,economy:false},session.token);
    assert.equal(allow.status,200);
    const [got,prog]=await api('/api/progression','GET',null,session.token);
    assert.equal(got.status,200);assert.equal(prog.record.levels.Recon,15);
    assert.equal(prog.record.cash,null,'No economy consent may expose cash');
    assert.doesNotMatch(JSON.stringify(prog),/76561190000000001/);
    const [toggle]=await api('/api/consent','POST',{progression:true,economy:true},session.token);
    assert.equal(toggle.status,200);
    const [now,visible]=await api('/api/refresh','POST',null,session.token);
    assert.equal(now.status,200);assert.equal(visible.record.gold,0);
    assert.equal(visible.record.cash,400);
    const [gone]=await api('/api/disconnect','POST',null,session.token);
    assert.equal(gone.status,200);
    const [expired]=await api('/api/me','GET',null,session.token);
    assert.equal(expired.status,401,'After revoke no session is valid');
  }finally{globalThis.fetch=oldFetch;}
});
test('dossier mismatch cannot attach one Steam account to another player',async()=>{
  const old=globalThis.fetch;
  globalThis.fetch=async()=>new Response('is_valid:true\n');
  try{
    const wrong='f'.repeat(64);
    const {url}=await login('players',wrong);
    assert.equal(url.pathname,'/1ADAAR/players.html');
    assert.equal(url.searchParams.get('progression_error'),'wrong_player');
    assert.equal(url.searchParams.has('progression_code'),false);
  }finally{globalThis.fetch=old;}
});
