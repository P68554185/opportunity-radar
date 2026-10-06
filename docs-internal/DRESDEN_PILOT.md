# Dresden pilot: location evidence and operating limits

## Sources and identity
Municipal construction intentions originate in dated notices on the Dresden section of
https://buergerbeteiligung.sachsen.de/portal/dresden/beteiligung/themen .
A municipal procedure is not a construction commitment. Its issuer is the planning authority,
not necessarily the investor or buyer. Notice dates are labelled accordingly.
The collector refreshes reviewed notices and places additional discovered pages in a review queue.
Source failures keep the last verified evidence; they never qualify a new unverified page.

Spatial references: https://kommisdd.dresden.de/net3/public/ogc.ashx .
- Node 489 / cls:L354: Bebauungspläne.
- Node 759 / cls:L575: VE- und VB-Pläne.
- Node 184 / cls:L134: public municipal addresses.

Attribution: Landeshauptstadt Dresden / Quelle: Geodaten Sachsen.
License: https://www.govdata.de/dl-de/by-2-0 .
The first verified collection returned 377 plan and 157 development-plan areas, plus
67,590 active address points explicitly labelled Dresden.
These are reference objects, not construction opportunities.
WFS numberMatched is unknown; completeness is not established.

## Coordinates and radius
WFS 2.0 GML requested as urn:ogc:def:crs:EPSG::4326 uses latitude/longitude axis order.
Dresden ranges, finite numbers, dimensionality and feature-collection identity are checked.
Plan keys match exactly, including amendment suffixes. A visitor, buyer or contact address is never
used as a project location. Unsupported or ambiguous references remain unlocated.

A plan bounding-box centre is a representative point, not the building site. A conservative
covering radius accounts for the full area. Customer radius eligibility requires the area's
maximum possible distance to be inside the selected company radius; unknown geography
and boundary-overlapping areas are excluded. The broader city view remains available.
Distances are approximate straight-line distances, never driving distances.

Address suggestions resolve locally from licensed reference data. The browser does not send
search strings to external geocoding services. Anonymous profiles persist locally; account
profiles, including origin and radius, persist in the existing database.
A hosted update requires the operator's ordinary Render manual deployment.

## Validation
Core tests cover GML axis errors, mismatched plan amendments, missing publication anchors,
distance sanity, unknown/buyer locations and radius-boundary areas.
Real Chromium checks use Südhöhe 9a, 01217 Dresden: all four initial municipal plan areas
appear inside 50 km and disappear from a 1 km view. Reload keeps the selected origin and radius.
SQLite and PostgreSQL profile tests cover validation and actual reloaded account persistence.
Published Pages browser checks repeat the real address/radius flow and mobile overflow assertion.

## Current limits
Only the four reviewed municipal projects are geolocated in the initial customer feed.
Most TED opportunities remain available in city/national views and are suppressed by radius mode.
More reference rows do not imply more nearby opportunities.
No independent confirmed Dresden lifecycle case or prospective lead has yet been demonstrated.
Further expansion requires additional dated construction evidence and project-site coordinates,
not guessed city-centre or buyer-address geocoding.
