'''
Registry helper functions module.
'''

# Import python libs
import logging
import collections

# Import third party libs
import yaml

# Import salt libs
import salt.utils
import salt.utils.network
from salt._compat import string_types

log = logging.getLogger(__name__)

def get_instance(accounts, networks, hosts):
    return Registry(accounts, networks, hosts)

def _ipv4_to_bits(ipaddr):
    '''
    Accepts an IPv4 dotted quad and returns a string representing its binary
    counterpart
    '''
    return ''.join([bin(int(x))[2:].rjust(8, '0') for x in ipaddr.split('.')])

def _int_to_ipv4(num):
    return '.'.join([str(num >> (i << 3) & 0xFF) for i in range(0, 4)[::-1]])

def _maxhost_of_subnet(subnet):
    cidr, masklen = subnet.split('/')
    masklen = int(masklen)
    bits = _ipv4_to_bits(cidr)
    gwbits = (bits[:masklen] + ('1' * (31 - masklen)) + '0')
    return _int_to_ipv4(int(gwbits, 2))

class Registry:
    def __init__(self, accounts, hosts, networks):
        self.hosts = hosts
        self.networks = networks

    def get_host(self, host):
        return self.hosts[host] if host in self.hosts else {}
    
    def get_host_attr(self, host, attr):
        data = self.get_host(host)
        return data[attr] if attr in data else None
    
    def host_address(self, host=None):
        key = host if host != None else __grains__['id']
        return self.get_host_attr(key, 'address')
    
    def host_subnet(self, host=None):
        host = host if host != None else __grains__['id']

        addr = self.get_host_attr(host, 'address')
        if addr is None: return None

        netmask = self.get_host_attr(host, 'netmask')
        if (netmask != None): return salt.utils.netmask.calculate_subnet(addr, result)

        result = None
        masklen = 33

        for net, data in self.networks.iteritems():
            cidr = data['cidr'] if 'cidr' in data else None
            if cidr == None: continue

            if salt.utils.network.in_subnet(cidr, [ addr ]):
                newlen = int(cidr.split('/')[1])
                if newlen < masklen:
                    masklen = newlen
                    result = cidr

        return result

    def host_netmask(self, host=None):
        masklen = 33
        host = host if host != None else __grains__['id']

        result = self.get_host_attr(host, 'netmask')
        if (result != None): return result

        addr = self.get_host_attr(host, 'address')
        if addr is None: return None

        for net, data in self.networks.iteritems():
            cidr = data['cidr'] if 'cidr' in data else None
            if cidr == None: continue

            if salt.utils.network.in_subnet(cidr, [ addr ]):
                newlen = int(cidr.split('/')[1])
                if newlen < masklen:
                    masklen = newlen
                    result = salt.utils.network.cidr_to_ipv4_netmask(newlen)

        return result

    def host_gateway(self, host=None):
        host = host if host != None else __grains__['id']
        
        result = self.get_host_attr(host, 'gateway')
        if (result != None): return result

	return _maxhost_of_subnet(self.host_subnet(host))

    def host_dnslist(self, host=None):
        host = host if host != None else __grains__['id']
        masklen = 33

        result = self.get_host_attr(host, 'dns')
        if (result != None): return result

        addr = self.get_host_attr(host, 'address')
        if addr is None: return None

        for net, data in self.networks.iteritems():
            cidr = data['cidr'] if 'cidr' in data else None
            if cidr == None: continue

            if salt.utils.network.in_subnet(cidr, [ addr ]):
                newlen = int(cidr.split('/')[1])
                if newlen < masklen:
                    masklen = newlen
                    result = [ _maxhost_of_subnet(cidr) ]

        return [ self.host_gateway(host) ] if result is None else result

# vim: set ai,ts=4,expandtab
