import fdb

conn = fdb.connect(
    dsn      = '127.0.0.1/3051:/firebird/data/ATHENAS.FDB',
    user     = 'SYSDBA',
    password = 'masterkey',
    fb_library_name = '/opt/firebird/lib/libfbclient.so.5.0.2'  # ou .so.2, conforme você tenha instalado
)

cur = conn.cursor()
cur.execute("SELECT * FROM USUARIOS")
colunas = [desc[0] for desc in cur.description]
dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
print(dados)
print("✔ Conectou com Firebird no container!")
conn.close()
