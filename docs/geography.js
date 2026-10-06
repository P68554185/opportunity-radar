/* Pure location policy, shared by UI and regression checks. */
"use strict";
(function(root){
 const finite=x=>typeof x==="number"&&Number.isFinite(x);
 function point(p){return p&&finite(p.lat)&&finite(p.lon)&&Math.abs(p.lat)<=90&&Math.abs(p.lon)<=180}
 function distance(a,b){
  if(!point(a)||!point(b))return null;
  const rad=x=>x*Math.PI/180,dlat=rad(b.lat-a.lat),dlon=rad(b.lon-a.lon);
  const q=Math.sin(dlat/2)**2+Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(dlon/2)**2;
  return 6371*2*Math.atan2(Math.sqrt(Math.min(1,q)),Math.sqrt(Math.max(0,1-q)));
 }
 function bounds(origin,location){
  if(!location||!["plan_area","project_point"].includes(location.basis))return null;
  const d=distance(origin,location),e=location.extent_km;
  if(d===null||!finite(e)||e<0||e>100)return null;
  return {distance:d,min:Math.max(0,d-e),max:d+e};
 }
 function inRadius(profile,location){
  const b=bounds(profile,location);
  return !!b&&finite(profile.radius_km)&&profile.radius_km>0&&profile.radius_km<=500&&b.max<=profile.radius_km;
 }
 const api={point,distance,bounds,inRadius};
 if(typeof module!=="undefined")module.exports=api;else root.BauRadarGeo=api;
})(typeof globalThis!=="undefined"?globalThis:this);
