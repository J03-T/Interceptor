from interceptor.net.addresses import IPv4Address, MACAddress
import netifaces
import re

_IP4_REGEX = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
_MAC_REGEX = r"[0-9a-fA-F]{2}(:|-)[0-9a-fA-F]{2}(:|-)[0-9a-fA-F]{2}(:|-)[0-9a-fA-F]{2}(:|-)[0-9a-fA-F]{2}(:|-)[0-9a-fA-F]{2}"

class Interface:
    """
    Represents a system network interface with a name, ipv4 address and mac address
    """
    def __init__(self, iface: str | IPv4Address | MACAddress):
        """
        Construct an Interface. 

        Args:
            iface (str | IPv4Address | MACAddress): The name, ipv4 address or 
            mac address of the interface. 
        """
        self._name: str | None = None
        self._ipv4_addr: IPv4Address | None = None
        self._mac_addr: IPv4Address | None = None 
        self._ipv4_netmask: IPv4Address | None = None
        self._ipv4_broadcast: IPv4Address | None = None
        if isinstance(iface, IPv4Address):
            self._ipv4_addr = iface
        elif isinstance(iface, MACAddress):
            self._mac_addr = iface
        elif re.match(_IP4_REGEX, iface):
            self._ipv4_addr = IPv4Address(iface)
        elif re.match(_MAC_REGEX, iface):
            self._mac_addr = MACAddress(iface)
        else:
            self._name = iface

        if self._name:
            try:
                if_info = netifaces.ifaddresses(self._name)
            except ValueError:
                raise Exception("No such interface exists.")
            if netifaces.AF_LINK in if_info:
                ether_info = if_info[netifaces.AF_LINK][0]
                self._mac_addr = MACAddress(ether_info['addr'])
            if netifaces.AF_INET in if_info:
                inet_info = if_info[netifaces.AF_INET][0]
                self._ipv4_addr = IPv4Address(inet_info['addr'])
                if 'broadcast' in inet_info:
                    self._ipv4_broadcast = IPv4Address(inet_info['broadcast'])
                self._ipv4_netmask = IPv4Address(inet_info['netmask'])
        elif self._ipv4_addr:
            if_names = netifaces.interfaces()
            for if_name in if_names:
                if_info = netifaces.ifaddresses(if_name)
                if netifaces.AF_INET in if_info:
                    if any(map(lambda i: i['addr'] == str(self._ipv4_addr), if_info[netifaces.AF_INET])):
                        self._name = if_name
                        if 'broadcast' in if_info[netifaces.AF_INET][0]:
                            self._ipv4_broadcast = IPv4Address(if_info[netifaces.AF_INET][0]['broadcast'])
                        self._ipv4_netmask = IPv4Address(if_info[netifaces.AF_INET][0]['netmask'])
                        if netifaces.AF_LINK in if_info:
                            mac_addr = if_info[netifaces.AF_LINK][0]['addr']
                            self._mac_addr = MACAddress(mac_addr)
            if self._name is None:
                raise Exception("No such interface exists.")
        elif self._mac_addr:
            if_names = netifaces.interfaces()
            for if_name in if_names:
                if_info = netifaces.ifaddresses(if_name)
                if netifaces.AF_LINK in if_info:
                    if any(map(lambda i: i['addr'] == str(self._mac_addr), if_info[netifaces.AF_LINK])):
                        self._name = if_name
                        if netifaces.AF_INET in if_info:
                            ipv4_addr = if_info[netifaces.AF_INET][0]['addr']
                            self._ipv4_addr = IPv4Address(ipv4_addr)
                            if 'broadcast' in if_info[netifaces.AF_INET][0]:
                                self._ipv4_broadcast = IPv4Address(if_info[netifaces.AF_INET][0]['broadcast'])
                            self._ipv4_netmask = IPv4Address(if_info[netifaces.AF_INET][0]['netmask'])
            if self._name is None:
                raise Exception("No such interface exists.")

    @property
    def mac_addr(self) -> MACAddress | None:
        """
        The MAC address of the network interface (if one exists).
        """
        return self._mac_addr
    
    @property
    def name(self) -> str:
        """
        The name of the network interface.
        """
        return self._name
            
    
    @property
    def ipv4_addr(self) -> IPv4Address | None:
        """
        The IPv4 address of interface (if it has one).
        """
        return self._ipv4_addr

    @property
    def ipv4_broadcast(self) -> IPv4Address | None:
        """
        The IPv4 broadcast address of the interface.
        """
        return self._ipv4_broadcast
    
    @property
    def ipv4_netmask(self) -> IPv4Address | None:
        """
        The IPv4 subnet mask of the interface
        """
        return self._ipv4_netmask
    
    def __str__(self) -> str:
        return self._name
    
    def __hash__(self) -> int:
        return hash((self._name, self._ipv4_addr, self._mac_addr))
    
def get_default_gateway_addr(proto = netifaces.AF_INET) -> IPv4Address:
    default_gateways = netifaces.gateways()['default']
    if proto in default_gateways:
        addr, _ = default_gateways[proto]
        return IPv4Address(addr)

def get_default_interface(proto = netifaces.AF_INET) -> Interface | None:
    default_gateways = netifaces.gateways()['default']
    if proto in default_gateways:
        _, if_name = default_gateways[proto]
        return Interface(if_name)

def get_interfaces() -> list[Interface]:
    return [Interface(i) for i in netifaces.interfaces()]