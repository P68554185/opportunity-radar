import os,sys
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"classification"))
from rules import classify
CASES=[
("Neubau Grundschule mit Sporthalle Elektroarbeiten","school","electrical"),
("Erweiterung Feuerwehrgerätehaus Heizungs- und Lüftungsanlagen","fire_station","hvac"),
("Sanierung Kläranlage Rohrleitungsbau","water_wastewater","sewer_pipe"),
("Brückensanierung Stahlbetonarbeiten","bridge","structural"),
("Neubau von 48 Wohnungen Fenster und Türen","residential","windows_doors"),
("Photovoltaikanlage mit Batteriespeicher","energy","solar_energy"),
("Gleiserneuerung und Bahnsteigarbeiten","rail","railworks"),
("Rathaus Fassadensanierung","administration","facade"),
]
ok=0
for text,p,t in CASES:
 got,tr=classify(text)
 passed=got==p and t in tr;ok+=passed
 print("PASS" if passed else "FAIL",text,"=>",got,tr)
print(f"{ok}/{len(CASES)} passed")
if ok!=len(CASES):raise SystemExit(1)
