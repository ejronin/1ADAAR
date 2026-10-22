/* Six-role radar production-ready renderer; NEVER infers XP or skills from combat.
   The source gate must be explicit and must contain all six verified levels. */
'use strict';
(function(root){
 const ROLES=['Assault','Medic','Support','Recon','Driver','Pilot'];
 const NS='http://www.w3.org/2000/svg';
 function render(svg, record){
  if(!svg||svg.namespaceURI!==NS)throw new TypeError('SVG element required');
  svg.querySelector('[data-role-profile]')?.remove();
  const ok=record&&record.sourceStatus==='verified'&&
    typeof record.source==='string'&&record.source.trim().length>2&&
    Number.isFinite(record.maxLevel)&&record.maxLevel>0&&
    record.levels&&typeof record.levels==='object'&&
    ROLES.every(role=>Number.isFinite(record.levels[role])&&
      record.levels[role]>=0&&record.levels[role]<=record.maxLevel);
  const empty=[...svg.querySelectorAll('[data-role-empty]')];
  for(const item of empty)item.style.display=ok?'none':'';
  if(!ok){
   svg.setAttribute('aria-label','Six-role progression unavailable: six verified levels have not been obtained.');
   return false;
  }
  const centerX=200,centerY=139,radius=104;
  const points=ROLES.map((name,i)=>{
    const radians=(-90+i*60)*Math.PI/180;
    const distance=radius*record.levels[name]/record.maxLevel;
    return [+(centerX+distance*Math.cos(radians)).toFixed(2),
            +(centerY+distance*Math.sin(radians)).toFixed(2)];
  });
  const poly=document.createElementNS(NS,'polygon');
  poly.setAttribute('data-role-profile','true');
  poly.setAttribute('points',points.map(p=>p.join(',')).join(' '));
  poly.setAttribute('stroke','#86f4a4');poly.setAttribute('stroke-width','2.5');
  poly.setAttribute('fill','#86f4a4');poly.setAttribute('fill-opacity','0.20');
  const title=document.createElementNS(NS,'title');
  title.textContent='Verified role progression: '+ROLES.map(r=>r+': '+record.levels[r]).join(', ');
  poly.append(title);svg.append(poly);
  svg.setAttribute('aria-label',ROLES.map(r=>r+' '+record.levels[r]+' of '+record.maxLevel).join('; ')+
    '. Verified source: '+record.source);
  return true;
 }
 root.OneADAARRoleRadar=Object.freeze({ROLES,render});
})(window);
