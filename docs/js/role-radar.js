/* Six-role radar production-ready renderer; NEVER infers XP or skills from combat.
   The source gate must be explicit and must contain all six verified levels. */
'use strict';
(function(root){
 const ROLES=['Assault','Medic','Support','Recon','Driver','Pilot'];
 const NS='http://www.w3.org/2000/svg';
 function scaleFor(levels){
  const peak=Math.max(0,...ROLES.map(role=>Number(levels?.[role])||0));
  return Math.max(10,Math.ceil(peak/10)*10);
 }
 function render(svg, record){
  if(!svg||svg.namespaceURI!==NS)throw new TypeError('SVG element required');
  svg.querySelector('[data-role-profile]')?.remove();
  // Fictional role fills are allowed ONLY inside the explicitly marked
  // PlayerOne example document. Live player dossiers still require verification.
  const fictional=Boolean(record&&record.demo===true&&
    record.sourceStatus==='fictional-demo'&&
    record.source==='FICTIONAL PLAYERONE FIXTURE'&&
    svg.dataset.roleDemo==='true'&&
    document.body.dataset.fictionalDemo==='true');
  const verified=Boolean(record&&record.sourceStatus==='verified'&&
    typeof record.source==='string'&&record.source.trim().length>2);
  const ok=record&&(fictional||verified)&&
    Number.isFinite(record.maxLevel)&&record.maxLevel>0&&
    record.levels&&typeof record.levels==='object'&&
    ROLES.every(role=>Number.isFinite(record.levels[role])&&
      record.levels[role]>=0&&record.levels[role]<=record.maxLevel);
  const empty=[...svg.querySelectorAll('[data-role-empty]')];
  for(const item of empty)item.style.display=ok?'none':'';
  if(!ok){
   const scaleCaption=document.getElementById(svg.id==='demo-role-radar'?'demo-radar-scale':'progression-radar-scale');
   if(scaleCaption)scaleCaption.textContent='Display scale adjusts to the highest verified role level';
   svg.setAttribute('aria-label','Six-role progression unavailable: six verified levels have not been obtained.');
   return false;
  }
  const displayMax=scaleFor(record.levels);
  const scaleCaption=document.getElementById(svg.id==='demo-role-radar'?'demo-radar-scale':'progression-radar-scale');
  if(scaleCaption)scaleCaption.textContent='Display scale 0–'+displayMax+' · Actual levels shown in the table';
  const centerX=200,centerY=139,radius=104;
  const points=ROLES.map((name,i)=>{
    const radians=(-90+i*60)*Math.PI/180;
    const distance=radius*record.levels[name]/displayMax;
    return [+(centerX+distance*Math.cos(radians)).toFixed(2),
            +(centerY+distance*Math.sin(radians)).toFixed(2)];
  });
  const poly=document.createElementNS(NS,'polygon');
  poly.setAttribute('data-role-profile','true');
  poly.setAttribute('points',points.map(p=>p.join(',')).join(' '));
  poly.setAttribute('stroke','#86f4a4');poly.setAttribute('stroke-width','2.5');
  poly.setAttribute('fill','#86f4a4');poly.setAttribute('fill-opacity','0.20');
  const title=document.createElementNS(NS,'title');
  title.textContent=(fictional?'Fictional PlayerOne levels: ':'Verified role progression: ')+
    ROLES.map(r=>r+': '+record.levels[r]).join(', ');
  poly.append(title);svg.append(poly);
  svg.setAttribute('aria-label','Display scale 0–'+displayMax+'. '+ROLES.map(r=>r+' actual level '+record.levels[r]).join('; ')+
    (fictional?'. FICTIONAL visualization; not real linked Steam data.':
             '. Verified source: '+record.source));
  return true;
 }
 root.OneADAARRoleRadar=Object.freeze({ROLES,render,scaleFor});
})(window);
