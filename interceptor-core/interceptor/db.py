from interceptor.net.addresses import IPv4Address, MACAddress
import sqlite3

def open() -> sqlite3.Connection:
    return sqlite3.connect("interceptor.db")

def setup(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("CREATE TABLE hosts (id INTEGER NOT NULL PRIMARY KEY , ipv4 TEXT, ipv6 TEXT, mac TEXT)")
    cur.execute("CREATE TABLE services (id INTEGER NOT NULL PRIMARY KEY, host_id INT, transport_protocol TEXT, port INT)")
    cur.execute("CREATE TABLE credentials (id INTEGER NOT NULL PRIMARY KEY, service_id INT, login_name TEXT, credential TEXT)")
    conn.commit()

def clear(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("DELETE FROM hosts")
    cur.execute("DELETE FROM services")
    cur.execute("DELETE FROM credentials")

def add_host(conn: sqlite3.Connection, ipv4_addr: IPv4Address = None, ipv6_addr: str = None, mac_addr: MACAddress = None):
    cur = conn.cursor()
    if ipv4_addr is not None:
        ipv4_addr = str(ipv4_addr)
    if ipv6_addr is not None:
        ipv6_addr = str(ipv6_addr)
    if mac_addr is not None:
        mac_addr = str(mac_addr)
    cur.execute("INSERT INTO hosts (ipv4, ipv6, mac) VALUES (?, ?, ?)", (ipv4_addr, ipv6_addr, mac_addr))
    conn.commit()
    return cur.lastrowid

def add_service(conn: sqlite3.Connection, host_id: int, transport_protocol: str, port: int):
    cur = conn.cursor()
    cur.execute("INSERT INTO services (host_id, transport_protocol, port) VALUES (?, ?, ?)", (host_id, transport_protocol, port))
    conn.commit()
    return cur.lastrowid

def add_credential(conn: sqlite3.Connection, service_id: int, login_name: str, credential: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO credentials (service_id, login_name, credential) VALUES (?, ?, ?)", (service_id, login_name, credential))
    conn.commit()
    return cur.lastrowid

def set_host(conn: sqlite3.Connection, id: int, ipv4_addr: IPv4Address = None, ipv6_addr: str = None, mac_addr: MACAddress = None):
    cur = conn.cursor()
    if ipv4_addr:
        cur.execute("UPDATE hosts SET ipv4 = ? WHERE id = ?", (str(ipv4_addr), id))
    if ipv6_addr:
        cur.execute("UPDATE hosts SET ipv6 = ? WHERE id = ?", (str(ipv6_addr), id))
    if mac_addr:
        cur.execute("UPDATE hosts SET mac =? WHERE id = ?", (str(mac_addr), id))
    conn.commit()
    
class _Host:
    def __init__(self, id: int, ipv4: IPv4Address | None, ipv6: str | None, mac: MACAddress | None):
        self.id = id
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.mac = mac
    def __str__(self) -> str:
        return f"ID: {self.id}\n\tIPv4: {str(self.ipv4)}\n\tIPv6: {str(self.ipv6)}\n\tMAC: {str(self.mac)}"

def get_all_hosts(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT * FROM hosts")
    res = cur.fetchall()
    return [_Host(*r) for r in res]

def search_hosts(conn: sqlite3.Connection, ipv4_addr: IPv4Address | None = None, ipv6_addr: str | None = None, mac_addr: MACAddress | None = None):
    query = "SELECT id, ipv4, ipv6, mac FROM hosts WHERE "
    if ipv4_addr:
        query += "ipv4 = ?"
        if ipv6_addr or mac_addr:
            query += " AND "
    if ipv6_addr:
        query += "ipv6 = ?"
        if mac_addr:
            query += " AND "
    if mac_addr:
        query += "mac = ?"
    args = ()
    if ipv4_addr:
        args += (str(ipv4_addr),)
    if ipv6_addr:
        args += (str(ipv6_addr),)
    if mac_addr:
        args += (str(mac_addr),)
    cur = conn.cursor()
    cur.execute(query, args)
    res = cur.fetchone()
    return _Host(*res) if res else None

def get_host(conn: sqlite3.Connection, id: int):
    cur = conn.cursor()
    cur.execute("SELECT ipv4, ipv6, mac FROM hosts WHERE id = ?", (id,))
    res = cur.fetchone()
    if res is None:
        return None
    return _Host(id, *res)

class _Credential:
    def __init__(self, id: int, service_id: int, login_name: str, credential: str):
        self.id = id
        self.service_id = service_id
        self.login_name = login_name
        self.credential = credential
    def __str__(self) -> str:
        return f"ID: {self.id}\n\tService ID: {self.service_id}\n\tLogin Name: {self.login_name}\n\tCredential: {self.credential}"
    
def get_all_credentials(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT * FROM credentials")
    res = cur.fetchall()
    return [_Credential(*r) for r in res]

def get_credential(conn: sqlite3.Connection, id: int):
    cur = conn.cursor()
    cur.execute("SELECT service_id, login_name, credential FROM credentials WHERE id = ?", (id, ))
    res = cur.fetchone()
    if res is None:
        return None
    return _Credential(id, *res)

class _Service:
    def __init__(self, id: int, host_id: int, transport_protocol: str, port: int):
        self.id = id
        self.host_id = host_id
        self.transport_protocol = transport_protocol
        self.port = port
    def __str__(self) -> str:
        return f"ID: {self.id}\n\tHost ID: {self.host_id}\n\tTransport Protocol: {self.transport_protocol}\n\tPort: {self.port}"

def get_all_services(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT * FROM services")
    res = cur.fetchall()
    return [_Service(*r) for r in res]

def get_service(conn: sqlite3.Connection, id: int):
    cur = conn.cursor()
    cur.execute("SELECT host_id, transport_protocol, port FROM services WHERE id = ?", (id, ))
    res = cur.fetchone()
    if res is None:
        return None
    return _Service(id, *res)

def search_services(conn: sqlite3.Connection, host_id: int = None, transport_protocol: str = None, port: int = None):
    query = "SELECT id, host_id, transport_protocol, port FROM services WHERE "
    if host_id:
        query += "host_id = ?"
        if transport_protocol or port:
            query += " AND "
    if transport_protocol:
        query += "transport_protocol = ?"
        if port:
            query += " AND "
    if port:
        query += "port = ?"
    args = ()
    if host_id:
        args += (host_id,)
    if transport_protocol:
        args += (transport_protocol,)
    if port:
        args += (port,)
    cur = conn.cursor()
    cur.execute(query, args)
    res = cur.fetchone()
    return _Service(*res) if res else None