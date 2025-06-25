import fdb
import configparser
import platform

def get_config():
    print("Python Architecture:", platform.architecture())
    
    fdb.load_api(r"C:\Program Files (x86)\Firebird\Firebird_5_0\fbclient.dll")
    
    config = configparser.ConfigParser()
    config.read(r"C:\Athenas Sistemas\dbxconnections.ini", encoding="utf-8-sig")
    return config["Athenas"]

def get_connection():
    cfg = get_config()
    return fdb.connect(
        dsn=cfg["database"].strip('"'), 
        user=cfg["user_name"],
        password=cfg["password"],
        charset=cfg.get("servercharset", "WIN1252"),
        sql_dialect=int(cfg.get("sqldialect", 3))
    )
