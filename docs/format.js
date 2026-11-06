"use strict";
(function(root){
 function dateLabel(value){
  const match=/^(\d{4}-\d{2}-\d{2})(?:$|T|[+-])/.exec(String(value||""));
  if(!match)return "Datum unbekannt";
  const day=match[1],date=new Date(day+"T00:00:00Z");
  if(Number.isNaN(date.valueOf())||date.toISOString().slice(0,10)!==day)return "Datum unbekannt";
  // Publication calendar dates are not shifted by the viewer's device timezone.
  return new Intl.DateTimeFormat("de-DE",{timeZone:"UTC"}).format(date);
 }
 const api={dateLabel};
 if(typeof module!=="undefined")module.exports=api;else root.BauRadarFormat=api;
})(typeof globalThis!=="undefined"?globalThis:this);
