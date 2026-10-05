"""BauRadar API. Same-origin sessions; SQLite requires a persistent local volume."""
from __future__ import annotations
import hashlib, hmac, json, os, re, secrets, sqlite3, time, threading
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from typing import Literal
import psycopg
from backend.database import connect

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get("BAURADAR_DB", "/tmp/bauradar/users.sqlite"))
DATABASE_URL=os.environ.get("BAURADAR_DATABASE_URL","")
ORIGIN=(os.environ.get("BAURADAR_ORIGIN") or os.environ.get("RENDER_EXTERNAL_URL") or "http://localhost:8000").rstrip("/")
SECURE=os.environ.get("BAURADAR_SECURE_COOKIES","true")=="true"
SIGNUP=os.environ.get("BAURADAR_ENABLE_SIGNUP","false")=="true"
TRADES={"electrical","hvac","plumbing","drywall","painting","flooring","roof","windows_doors",
 "facade","earthworks","structural","landscaping","fire_protection","elevator","demolition",
 "roadworks","sewer_pipe","railworks","solar_energy","scaffolding","metalwork",
 "building_automation","industrial_doors","screed","steelwork","medical_technology","elevators",
 "building_services","plastering","finishing"}
app=FastAPI(title="BauRadar",docs_url=None,redoc_url=None,openapi_url=None)

_initialized=set()
_initialization_lock=threading.Lock()
SCHEMA="""
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,created BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles(user_id TEXT PRIMARY KEY REFERENCES users(id),payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS watches(user_id TEXT NOT NULL REFERENCES users(id),project_id TEXT NOT NULL,created BIGINT NOT NULL,PRIMARY KEY(user_id,project_id));
CREATE TABLE IF NOT EXISTS attempts(client TEXT NOT NULL,created BIGINT NOT NULL);
CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON sessions(expires);
CREATE INDEX IF NOT EXISTS attempts_client_time_idx ON attempts(client,created);
"""
@contextmanager
def database():
    identity=DATABASE_URL or str(DB)
    with connect(DB,DATABASE_URL) as db:
        try:
            with _initialization_lock:
                if identity not in _initialized:
                    db.executescript(SCHEMA);db.commit();_initialized.add(identity)
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise

def password_hash(password):
    salt=secrets.token_hex(16)
    result=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),600000).hex()
    return "$".join(["pbkdf2_sha256","600000",salt,result])

DUMMY_PASSWORD_HASH=password_hash("unusable-dummy-password")

def password_matches(password,encoded):
    _,rounds,salt,expected=encoded.split("$")
    result=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),int(rounds)).hex()
    return hmac.compare_digest(result,expected)

def csrf(request):
    if request.headers.get("origin")!=ORIGIN:
        raise HTTPException(403,"Anfrage stammt nicht von BauRadar.")

def user(request):
    token=request.cookies.get("bauradar_session","")
    if not token or len(token)>200: raise HTTPException(401,"Bitte anmelden.")
    with database() as db:
        row=db.execute("SELECT u.id,u.email FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?",
            (hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
    if not row: raise HTTPException(401,"Bitte erneut anmelden.")
    return dict(row)

def throttle(request):
    client=request.client.host if request.client else "unknown"
    now=int(time.time())
    with database() as db:
        db.execute("DELETE FROM attempts WHERE created<?",(now-900,))
        count=db.execute("SELECT COUNT(*) FROM attempts WHERE client=?",(client,)).fetchone()[0]
        if count>=20: raise HTTPException(429,"Zu viele Versuche. Bitte später erneut versuchen.")
        db.execute("INSERT INTO attempts VALUES(?,?)",(client,now))

def session(response,user_id):
    token=secrets.token_urlsafe(32); now=int(time.time())
    with database() as db:
        db.execute("DELETE FROM sessions WHERE expires<=?",(now,))
        db.execute("INSERT INTO sessions VALUES(?,?,?)",(hashlib.sha256(token.encode()).hexdigest(),user_id,now+604800))
    response.set_cookie("bauradar_session",token,httponly=True,secure=SECURE,samesite="strict",max_age=604800,path="/")

class Credentials(BaseModel):
    email: str=Field(min_length=3,max_length=254)
    password: str=Field(min_length=12,max_length=200)
    @model_validator(mode="after")
    def valid_email(self):
        self.email=self.email.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",self.email): raise ValueError("E-Mail-Adresse prüfen.")
        return self

class Profile(BaseModel):
    name: str=Field(default="",max_length=120)
    city: str=Field(default="",max_length=100)
    locationMode: Literal["all","city"]="all"
    trades: list[str]=Field(default_factory=list,max_length=40)
    radius_km: float=Field(default=50,gt=0,le=500)
    lat: float|None=Field(default=None,ge=-90,le=90)
    lon: float|None=Field(default=None,ge=-180,le=180)
    @model_validator(mode="after")
    def valid_profile(self):
        self.name=self.name.strip();self.city=self.city.strip()
        if self.locationMode=="city" and not self.city: raise ValueError("Ort erforderlich.")
        if set(self.trades)-TRADES: raise ValueError("Unbekanntes Gewerk.")
        if (self.lat is None)!=(self.lon is None): raise ValueError("Vollständige Koordinaten erforderlich.")
        return self

@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    return JSONResponse(status_code=422,content={"detail":"Bitte prüfen Sie die Eingaben."})

@app.middleware("http")
async def headers(request,call_next):
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
    if request.url.path.startswith(("/api","/admin")): response.headers["Cache-Control"]="no-store"
    return response

@app.get("/api/live")
def live():
    # Platform health checks must not keep a free database awake continuously.
    return {"status":"ok"}

@app.get("/api/health")
def health():
    with database() as db: db.execute("SELECT 1").fetchone()
    return {"status":"ok","signup_enabled":SIGNUP,"email_enabled":False,"billing_enabled":False}

@app.post("/api/register")
def register(credentials:Credentials,request:Request,response:Response):
    csrf(request)
    if not SIGNUP: raise HTTPException(503,"Registrierung noch nicht freigeschaltet.")
    throttle(request);uid=secrets.token_hex(16)
    with database() as db:
        try: db.execute("INSERT INTO users VALUES(?,?,?,?)",(uid,credentials.email,password_hash(credentials.password),int(time.time())))
        except (sqlite3.IntegrityError,psycopg.IntegrityError): raise HTTPException(409,"Registrierung mit dieser Adresse nicht möglich.")
    session(response,uid)
    return {"email":credentials.email}

@app.post("/api/login")
def login(credentials:Credentials,request:Request,response:Response):
    csrf(request);throttle(request)
    with database() as db: row=db.execute("SELECT * FROM users WHERE email=?",(credentials.email,)).fetchone()
    encoded=row["password"] if row else DUMMY_PASSWORD_HASH
    if not password_matches(credentials.password,encoded) or not row: raise HTTPException(401,"E-Mail oder Passwort stimmt nicht.")
    session(response,row["id"])
    return {"email":row["email"]}

@app.post("/api/logout")
def logout(request:Request,response:Response):
    csrf(request);token=request.cookies.get("bauradar_session","")
    with database() as db: db.execute("DELETE FROM sessions WHERE token_hash=?",(hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie("bauradar_session",path="/",secure=SECURE,httponly=True,samesite="strict")
    return {"ok":True}

@app.get("/api/me")
def me(request:Request): return user(request)

@app.get("/api/profile")
def get_profile(request:Request):
    uid=user(request)["id"]
    with database() as db: row=db.execute("SELECT payload FROM profiles WHERE user_id=?",(uid,)).fetchone()
    return json.loads(row["payload"]) if row else Profile().model_dump()

@app.put("/api/profile")
def put_profile(profile:Profile,request:Request):
    csrf(request);uid=user(request)["id"]
    with database() as db:
        db.execute("INSERT INTO profiles VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload",
            (uid,json.dumps(profile.model_dump(),ensure_ascii=False)))
    return profile.model_dump()

@app.get("/api/watches")
def get_watches(request:Request):
    uid=user(request)["id"]
    with database() as db: return [r["project_id"] for r in db.execute("SELECT project_id FROM watches WHERE user_id=? ORDER BY created DESC",(uid,))]

@app.put("/api/watches/{project_id}")
def watch(project_id:str,request:Request):
    csrf(request);uid=user(request)["id"]
    if len(project_id)>100: raise HTTPException(400,"Ungültiges Projekt.")
    feed=json.loads((ROOT/"docs"/"data"/"bauradar_feed.json").read_text(encoding="utf-8"))
    if not any(r["id"]==project_id for r in feed["opportunities"]): raise HTTPException(404,"Projekt nicht gefunden.")
    with database() as db: db.execute("INSERT OR IGNORE INTO watches VALUES(?,?,?)",(uid,project_id,int(time.time())))
    return {"ok":True}

@app.delete("/api/watches/{project_id}")
def unwatch(project_id:str,request:Request):
    csrf(request);uid=user(request)["id"]
    with database() as db: db.execute("DELETE FROM watches WHERE user_id=? AND project_id=?",(uid,project_id))
    return {"ok":True}

@app.get("/admin")
@app.get("/admin/{path:path}")
def admin(request:Request,path:str="index.html"):
    current=user(request)
    allowed={v.strip().lower() for v in os.environ.get("BAURADAR_ADMIN_EMAILS","").split(",") if v.strip()}
    if current["email"] not in allowed: raise HTTPException(403,"Kein Admin-Zugriff.")
    if request.url.path=="/admin": return RedirectResponse("/admin/",status_code=307)
    path=path or "index.html"
    if path.startswith("data/"):
        target=(ROOT/"docs"/path).resolve();base=(ROOT/"docs"/"data").resolve()
    else:
        target=(ROOT/"admin"/path).resolve();base=(ROOT/"admin").resolve()
    if not target.is_relative_to(base) or not target.is_file(): raise HTTPException(404)
    return FileResponse(target)

app.mount("/",StaticFiles(directory=ROOT/"docs",html=True),name="website")
