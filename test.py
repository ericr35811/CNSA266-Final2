import obd
from time import sleep

conn = obd.OBD()
print(conn.status())
sleep(10)
