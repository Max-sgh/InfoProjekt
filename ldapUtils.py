import sys
import ldap

class ldapUtils():
    def __init__(self, basedn, address, adminUsername, adminPass):
        self._basedn = basedn
        self._address = address
        self._adminUsername = adminUsername
        self._adminPassword = adminPass

    def authenticate(self, username, password):
        conn = ldap.initialize('ldap://' + self._address)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        try:
            result = conn.simple_bind_s(username, password)
        except ldap.INVALID_CREDENTIALS:
            return "Invalid credentials", False
        except ldap.SERVER_DOWN:
            return "Server down", False
        except (ldap.LDAPError, e):
            if type(e.message) == dict and e.message.has_key('desc'):
                return "Other LDAP error: " + e.message['desc'], False
            else:
                return "Other LDAP error: " + e, False
        return conn, True
    
    def getUserDetail(self, username):
        conn, success = self.authenticate(self._adminUsername, self._adminPassword)
        if not success:
            return []
        result = conn.search_s(self._basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=user)(sAMAccountName=" + username + "))")
        attributes = result[0]
        cn = attributes[0]
        nachname = attributes[1]["sn"]
        vorname = attributes[1]['givenName']
        loginName = attributes[1]["sAMAccountName"]
        anzeigeName = attributes[1]["displayName"]
        return [cn, vorname, nachname, loginName, anzeigeName]

    def checkGroup(self, username, groupname):
        conn, success = self.authenticate(self._adminUsername, self._adminPassword)
        if not success:
            return []
        result = conn.search_s(self._basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=user)(sAMAccountName=" + username + "))")
        attributes = result[0]
        for groups in attributes[1]["memberOf"]:
            dns = groups.decode("utf-8").split(",")
            
            for d in dns:
                if d == "CN=" + groupname:
                    return True
        return False
    
    def getAllGroupMembers(self, groupname):
        conn, success = self.authenticate(self._adminUsername, self._adminPassword)
        if not success:
            return []
        result = conn.search_s(self._basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=GROUP)(cn=" + groupname + "))")
        members = []
        if result:
            if len(result[0]) >= 2 and 'member' in result[0][1]:
                members_tmp = result[0][1]['member']
                for m in members_tmp:
                    result = conn.search_s(self._basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=user)(distinguishedName=" + m.decode("utf-8") + "))")
                    attributes = result[0]
                    members.append(attributes[1]["sAMAccountName"][0].decode("utf-8"))

        return members