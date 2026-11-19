"use strict";
const assert=require("node:assert/strict"),{dateLabel}=require("../docs/format.js");
for(const zone of ["UTC","Europe/Berlin","America/Los_Angeles","Pacific/Kiritimati"]){
 process.env.TZ=zone;
 assert.equal(dateLabel("2026-09-25+02:00"),"25.9.2026");
 assert.equal(dateLabel("2026-08-11+02:00"),"11.8.2026");
 assert.equal(dateLabel("2023-07-27"),"27.7.2023");
 assert.equal(dateLabel("2024-02-29"),"29.2.2024");
 assert.equal(dateLabel("2026-10-06T12:00:00+02:00"),"6.10.2026");
 for(const bad of ["2026-02-29","2026-02-30","2026-13-01","garbage",null,undefined])assert.equal(dateLabel(bad),"Datum unbekannt");
}
console.log("Publication dates: real TED timezone forms, leap dates and four device timezones verified.");
