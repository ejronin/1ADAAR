import assert from 'node:assert/strict';
import {test} from 'node:test';
import {webcrypto, createHash} from 'node:crypto';
import worker,{internalForTests as core} from '../services/steam-progression/worker.mjs';
if(!globalThis.crypto)globalThis.crypto=webcrypto;

const SID='76561190000000001';
const env={AUTH_ORIGIN:'https://1adaar-auth.example.workers.dev',
  PUBLIC_PAGE_URL:'https://ejronin.github.io/1ADAAR/players.html',
  PUBLIC_ORIGIN:'https://ejronin.github.io',
  PUBLIC_PROGRESSION_URL:'https://ejronin.github.io/1ADAAR/progression.html',DB:{}};
const fixture={player:{steamId:SID,stats:{wardogLevel:142,careerXp:1830450,cash:0,gold:4,
  syncedAt:'2026-10-22T11:00:00Z',roles:{
    assault:{level:41,xp:612000},medic:{level:22,xp:180400},
    support:{level:19,xp:140800},recon:{level:30,xp:350200},
    driver:{level:12,xp:90050},pilot:{level:18,xp:457000}
  }}}};

test('worker source modules can load without deployment or npm dependencies',async()=>{
  const r=await worker.fetch(new Request(env.AUTH_ORIGIN+'/health'),env);
  assert.equal(r.status,200);
  assert.equal((await r.json()).ok,true);
});
test('Steam player key is the exact collector public hash and not the SteamID',async()=>{
  const expected=createHash('sha256').update('1ADAAR:v1:'+SID).digest('hex');
  assert.equal(await core.pageKey(SID),expected);
  assert.doesNotMatch(expected,/7656119/);
});
test('progression fields are game-account values with verified source and no SteamID',()=>{
  const record=core.normalize(fixture,SID,true);
  assert.equal(record.sourceStatus,'verified');
  assert.match(record.dataScope,/Game-wide/);
  assert.equal(record.maxLevel,100);
  assert.equal(record.levels.Pilot,18);
  assert.equal(record.xp.Recon,350200);
  assert.equal(record.cash,0);
  assert.equal(record.gold,4);
  assert.equal(record.careerXp,1830450);
  assert.doesNotMatch(JSON.stringify(record),/76561190000000001/);
});
test('additional Tracker fields and Steam avatar remain source-gated',()=>{
  const data=structuredClone(fixture);
  data.player.stats.unlocks=9;
  data.player.leaderboardRank=872;
  data.player.leaderboardPlayers=901;
  data.player.avatarUrl='https://avatars.steamstatic.com/abc123_full.jpg';
  const got=core.normalize(data,SID,false);
  assert.equal(got.unlocks,9);
  assert.equal(got.leaderboardRank,872);
  assert.equal(got.leaderboardPlayers,901);
  assert.equal(got.avatarUrl,data.player.avatarUrl);
  assert.equal(got.cash,null);
  const malformed=structuredClone(data);
  malformed.player.avatarUrl='https://evil.example/track?steamid='+SID;
  malformed.player.leaderboardRank=902;
  malformed.player.stats.unlocks=-1;
  const rejected=core.normalize(malformed,SID,false);
  assert.equal(rejected.avatarUrl,null);
  assert.equal(rejected.leaderboardRank,null);
  assert.equal(rejected.leaderboardPlayers,null);
  assert.equal(rejected.unlocks,null);
  assert.equal(core.normalize(data,SID,false).xp.Pilot,457000);
  const zero=structuredClone(data);
  zero.player.stats.roles.pilot={level:0,xp:0};
  assert.equal(core.normalize(zero,SID,false).xp.Pilot,0);
});

test('economy permission is independent of public game progression',()=>{
  const record=core.normalize(fixture,SID,false);
  assert.equal(record.cash,null);assert.equal(record.gold,null);
  assert.equal(record.levels.Assault,41);
  const hidden=structuredClone(fixture);hidden.player.stats.cash=null;
  hidden.player.stats.gold=null;
  const privateEconomy=core.normalize(hidden,SID,true);
  assert.equal(privateEconomy.cash,null);assert.equal(privateEconomy.gold,null);
});
test('reject wrong player identity, incomplete roles, malformed level and unsynced records',()=>{
  assert.equal(core.normalize(fixture,'76561190000000002',true),null);
  const partial=structuredClone(fixture);delete partial.player.stats.roles.medic;
  assert.equal(core.normalize(partial,SID,true),null);
  const tooHigh=structuredClone(fixture);tooHigh.player.stats.roles.pilot.level=101;
  assert.equal(core.normalize(tooHigh,SID,true),null);
  const noSync=structuredClone(fixture);noSync.player.stats=null;
  assert.equal(core.normalize(noSync,SID,false),null);
  const missingDate=structuredClone(fixture);missingDate.player.stats.syncedAt='???';
  assert.equal(core.normalize(missingDate,SID,true),null);
});
test('OpenID callback strictly checks Steam endpoint, signed claims, return-to and Steam acknowledgement',async()=>{
  const state='base64url_State_No_SteamID_12345';
  const openid={
    'openid.mode':'id_res','openid.ns':'http://specs.openid.net/auth/2.0',
    'openid.claimed_id':'http://steamcommunity.com/openid/id/'+SID,
    'openid.identity':'http://steamcommunity.com/openid/id/'+SID,
    'openid.op_endpoint':'https://steamcommunity.com/openid/login',
    'openid.return_to':env.AUTH_ORIGIN+'/auth/callback?state='+state,
    'openid.signed':'claimed_id,identity,return_to,response_nonce,assoc_handle',
    'openid.response_nonce':'2026-10-22T15:00:00Z1234',
    'openid.assoc_handle':'12345',
    'openid.sig':'mock-signed-by-Steam'
  };
  const called=[];
  const old=globalThis.fetch;
  globalThis.fetch=async(url,args)=>{
    called.push({url,args});
    return new Response('ns:http://specs.openid.net/auth/2.0\nis_valid:true\n',{status:200});
  };
  try{
    const url=new URL(env.AUTH_ORIGIN+'/auth/callback');
    for(const [k,v] of Object.entries(openid))url.searchParams.set(k,v);
    assert.equal(await core.verifySteam(url,env,state),SID);
    assert.equal(called.length,1);assert.equal(called[0].url,'https://steamcommunity.com/openid/login');
    assert.match(called[0].args.body,/openid.mode=check_authentication/);
    url.searchParams.set('openid.return_to','https://malicious.example/');
    assert.equal(await core.verifySteam(url,env,state),null);
    url.searchParams.set('openid.return_to',openid['openid.return_to']);
    url.searchParams.set('openid.op_endpoint','https://malicious.example/');
    assert.equal(await core.verifySteam(url,env,state),null);
    url.searchParams.set('openid.op_endpoint',openid['openid.op_endpoint']);
    url.searchParams.set('openid.signed','identity,return_to,response_nonce,assoc_handle');
    assert.equal(await core.verifySteam(url,env,state),null);
  }finally{globalThis.fetch=old;}
});
test('deny browser calls from unapproved origins without exposing account data',async()=>{
  const r=await worker.fetch(new Request(env.AUTH_ORIGIN+'/api/me',{
    headers:{Origin:'https://thirdparty.example',Authorization:'Bearer fake'}}),env);
  assert.equal(r.status,403);
  assert.equal((await r.json()).error,'forbidden_origin');
});
