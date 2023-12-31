from interceptor.net.interfaces import Interface, get_default_interface
from interceptor.net.addresses import IPv4Address, cidr_range, ip_range
from interceptor.net.sockets.layer3 import HostUnresolvedException
import interceptor.net.protocols.icmp as icmp
import interceptor.io as io
import interceptor.db as db
import interceptor.threads as threads

def _ping_thread_f(ip, timeout, interface):
    db_conn = db.open()
    io.write(f"Sending ECHO REQUEST to {str(ip)}")
    ping_pkt = icmp.ICMPPacket(icmp.ICMPType.ECHO_REQUEST, 0, b'1234567890')
    try:
        resp = ping_pkt.send_and_recv(ip, interface, timeout)
    except HostUnresolvedException:
        resp = None
    if resp is not None:
        io.write(f"Received ECHO REPLY from {str(ip)}")
        if db.search_hosts(db_conn, ipv4_addr=ip) is None:
            db.add_host(db_conn, ipv4_addr=ip)
    else:
        io.write(f"No reply from {str(ip)}")
    db_conn.close()

class Module:
    """Performs a pingsweep of a given subnet to discover live hosts"""
    def run(self, range: str, timeout: float = 5.0, interface: Interface = get_default_interface()):
        if "/" in range:
            ip_addresses = cidr_range(range)
        elif "-" in range:
            ip_addresses = ip_range(range)
        ping_threads = []
        for ip in ip_addresses:
            thread = threads.create_thread(_ping_thread_f, (ip, timeout, interface))
            ping_threads.append(thread)
            thread.start()
        for thread in ping_threads:
            thread.join()
        return True