import sys
import ldap

class ldapUtils():
    def __init__(self, basedn, address, adminUsername, adminPass):
        self._basedn = basedn
        self._address = address
        self._adminUsername = adminUsername
        self._adminPassword = adminPass

    def authenticate(self, username, password) -> str:
        conn = ldap.initialize('ldap://' + self._address)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)    
        try:
            result = conn.simple_bind_s(username, password)
        except ldap.INVALID_CREDENTIALS:
            return "Invalid credentials"
        except ldap.SERVER_DOWN:
            return "Server down"
        except (ldap.LDAPError, e):
            if type(e.message) == dict and e.message.has_key('desc'):
                return "Other LDAP error: " + e.message['desc']
            else: 
                return "Other LDAP error: " + e
        finally:
            conn.unbind_s()    
        return "Succesfully authenticated"