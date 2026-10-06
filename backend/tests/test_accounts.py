import importlib
import os
from pathlib import Path
import tempfile
import unittest
from fastapi.testclient import TestClient

class AccountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        os.environ["BAURADAR_DATABASE_URL"]=os.environ.get("TEST_POSTGRES_URL","") if getattr(cls,"use_postgres",False) else ""
        os.environ["BAURADAR_DB"]=str(Path(cls.temp.name)/"users.sqlite")
        os.environ["BAURADAR_ORIGIN"]="http://testserver"
        os.environ["BAURADAR_SECURE_COOKIES"]="false"
        os.environ["BAURADAR_ENABLE_SIGNUP"]="true"
        import backend.app as module
        cls.module=importlib.reload(module)
        cls.app=cls.module.app
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def setUp(self):
        with self.module.database() as db:
            for table in ("attempts","sessions","profiles","watches","users"): db.execute("DELETE FROM "+table)
        self.client=TestClient(self.app,headers={"Origin":"http://testserver"})
    def register(self,client,email="one@example.com"):
        response=client.post("/api/register",json={"email":email,"password":"a-long-test-password"})
        self.assertEqual(response.status_code,200,response.text)
        return response
    def test_session_and_logout(self):
        response=self.register(self.client)
        self.assertIn("HttpOnly",response.headers["set-cookie"])
        self.assertEqual(self.client.get("/api/me").status_code,200)
        self.client.post("/api/logout")
        self.assertEqual(self.client.get("/api/me").status_code,401)
    def test_password_storage_and_login(self):
        self.register(self.client)
        with self.module.database() as db: stored=db.execute("SELECT password FROM users").fetchone()[0]
        self.assertNotIn("a-long-test-password",stored)
        self.client.post("/api/logout")
        self.assertEqual(self.client.post("/api/login",json={"email":"one@example.com","password":"wrong-password-123"}).status_code,401)
        self.assertEqual(self.client.post("/api/login",json={"email":"one@example.com","password":"a-long-test-password"}).status_code,200)
    def test_csrf_and_access_control(self):
        self.assertEqual(self.client.post("/api/register",headers={"Origin":"https://attacker.example"},json={"email":"x@example.com","password":"long-test-password"}).status_code,403)
        self.assertEqual(self.client.get("/api/profile").status_code,401)
        self.register(self.client)
        self.assertEqual(self.client.get("/admin").status_code,403)
    def test_profiles_are_isolated_and_persistent(self):
        self.register(self.client)
        response=self.client.put("/api/profile",json={"name":"Betrieb Eins","trades":["electrical"],"city":"Roth","locationMode":"city"})
        self.assertEqual(response.status_code,200)
        other=TestClient(self.app,headers={"Origin":"http://testserver"})
        self.register(other,"two@example.com")
        self.assertEqual(other.get("/api/profile").json()["name"],"")
        self.assertEqual(self.client.get("/api/profile").json()["name"],"Betrieb Eins")
        self.assertEqual(self.client.put("/api/profile",json={"radius_km":0}).status_code,422)
        self.assertEqual(self.client.put("/api/profile",json={"trades":["invented"]}).status_code,422)
    def test_radius_profile_validation_and_persistence(self):
        self.register(self.client)
        self.assertEqual(self.client.put("/api/profile",json={"locationMode":"radius"}).status_code,422)
        self.assertEqual(self.client.put("/api/profile",json={"locationMode":"radius","lat":51.019,"lon":13.745,"radius_km":501}).status_code,422)
        value={"locationMode":"radius","city":"Dresden","lat":51.0190174492382,"lon":13.7454971065981,"radius_km":50,
            "location_id":"DRESDEN-43184","location_label":"Südhöhe 9a · 01217 Dresden"}
        result=self.client.put("/api/profile",json=value)
        self.assertEqual(result.status_code,200,result.text)
        restarted=TestClient(importlib.reload(self.module).app,headers={"Origin":"http://testserver"})
        restarted.cookies.update(self.client.cookies)
        profile=restarted.get("/api/profile").json()
        for key,item in value.items():self.assertEqual(profile[key],item)

    def test_restart_keeps_accounts_and_sessions(self):
        self.register(self.client)
        restarted=TestClient(importlib.reload(self.module).app,headers={"Origin":"http://testserver"})
        restarted.cookies.update(self.client.cookies)
        self.assertEqual(restarted.get("/api/me").json()["email"],"one@example.com")

    def test_watches_are_isolated_and_idempotent(self):
        import json
        self.register(self.client)
        feed=json.loads((self.module.ROOT/"docs"/"data"/"bauradar_feed.json").read_text(encoding="utf-8"))
        identity=feed["opportunities"][0]["id"]
        self.assertEqual(self.client.put("/api/watches/"+identity).status_code,200)
        self.assertEqual(self.client.put("/api/watches/"+identity).status_code,200)
        self.assertEqual(self.client.get("/api/watches").json(),[identity])
        other=TestClient(self.app,headers={"Origin":"http://testserver"})
        self.register(other,"other@example.com")
        self.assertEqual(other.get("/api/watches").json(),[])

    def test_expired_session(self):
        self.register(self.client)
        with self.module.database() as db: db.execute("UPDATE sessions SET expires=0")
        self.assertEqual(self.client.get("/api/me").status_code,401)
    def test_unknown_projects_not_watched(self):
        self.register(self.client)
        self.assertEqual(self.client.put("/api/watches/nonexistent").status_code,404)

@unittest.skipUnless(os.environ.get("TEST_POSTGRES_URL"),"PostgreSQL test service unavailable")
class PostgresAccountTests(AccountTests):
    use_postgres=True

if __name__=="__main__": unittest.main()
