import configparser
import fdb
import platform
import fdb.fbcore as fbcore

def my_b2u(st, charset):
    if charset.upper() == "NONE":
        return st  
    else:
        return st.decode(charset, errors="replace")

fbcore.b2u = my_b2u

print("Python Architecture:", platform.architecture())

fdb.load_api(r"C:\Program Files (x86)\Firebird\Firebird_5_0\fbclient.dll")

config = configparser.ConfigParser()
config.read(r"C:\Athenas Sistemas\dbxconnections.ini", encoding="utf-8-sig")
cfg = config["Athenas"]
con = fdb.connect(
    dsn=cfg["database"].strip('"'),
    user=cfg["user_name"],
    password=cfg["password"],
    charset="NONE", 
    sql_dialect=int(cfg.get("sqldialect", 3))
)

cur = con.cursor()
cur.execute("SELECT * FROM USUARIOS")

colunas = [desc[0] for desc in cur.description]
dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
con.close()
for dado in dados:
    print(dado)
