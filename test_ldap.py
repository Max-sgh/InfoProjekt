import sys
import ldap


AD_SERVERS = ['192.168.178.54']
AD_USER_BASEDN = "DC=srv-lange,DC=de"
AD_USER_FILTER = '(&(objectClass=USER)(sAMAccountName={username}))'
AD_USER_FILTER2 = '(&(objectClass=USER)(dn={userdn}))'
AD_GROUP_FILTER = '(&(objectClass=GROUP)(cn={group_name}))'
#AD_BIND_USER = 'Administrator@srv-lange.de'
#AD_BIND_PWD = 'Rsu3sc123'



# ldap connection
def ad_auth(username, password, address=AD_SERVERS[0]):
	conn = ldap.initialize('ldap://' + address)
	conn.protocol_version = 3
	conn.set_option(ldap.OPT_REFERRALS, 0)

	result = True

	try:
		conn.simple_bind_s(username, password)
		print("Succesfully authenticated")
	except ldap.INVALID_CREDENTIALS:
		return "Invalid credentials", False
	except ldap.SERVER_DOWN:
		return "Server down", False
	except (ldap.LDAPError, e):
		if type(e.message) == dict and e.message.has_key('desc'):
			return "Other LDAP error: " + e.message['desc'], False
		else:
			return "Other LDAP error: " + e, False

	return conn, result

def get_dn_by_username(username, ad_conn, basedn=AD_USER_BASEDN):
	return_dn = ''
	ad_filter = AD_USER_FILTER.replace('{username}', username)
	results = ad_conn.search_s(basedn, ldap.SCOPE_SUBTREE, ad_filter)
	if results:
		for dn, others in results:
			return_dn = dn
	return return_dn

#
# query only enabled users with the following filter
# (!(userAccountControl:1.2.840.113556.1.4.803:=2))
#
def get_email_by_dn(dn, ad_conn):
	email = ''
	result = ad_conn.search_s(dn, ldap.SCOPE_BASE, \
		'(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))')
	if result:
		for dn, attrb in result:
			if 'mail' in attrb and attrb['mail']:
				email = attrb['mail'][0].lower()
				break
	return email


def get_group_members(group_name, ad_conn, basedn=AD_USER_BASEDN):
	members = []
	ad_filter = AD_GROUP_FILTER.replace('{group_name}', group_name)
	result = ad_conn.search_s(basedn, ldap.SCOPE_SUBTREE, ad_filter)
    
	if result:
		if len(result[0]) >= 2 and 'member' in result[0][1]:
			#print(result[0][1])
			members_tmp = result[0][1]['member']
			for m in members_tmp:
				#email = get_email_by_dn(m, ad_conn)
				print(m)
				#res = ad_conn.search_s(basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=USER)(sAMAccountName=WAG))")
				#rint(res[0][1]["memberOf"])
                #
                # Fehler: res[0][0]="None"
                # Richtig: res[0][0]=dn
                #
                # Argumente in res[0][1]
                #
				#print("\n")
				members.append(m)
	return members


if __name__ == "__main__":
  group_name = sys.argv[1]
  ad_conn, result = ad_auth("Administrator@srv-lange.de", "Rsu3sc123")
  print(ad_conn),
  get_group_members("Lehrer", ad_conn)
  #if result:
    #group_members = get_group_members("Lehrer", ad_conn)
    #for m in group_members:
      #print(m) # b'CN=Nurzum Test,CN=Users,DC=srv-lange,DC=de' \n [...]

#(member=sAMAccountName=WAG,DC=gymsgh,DC=local)
  """res = ad_conn.search_s(AD_USER_BASEDN, ldap.SCOPE_SUBTREE, \
	 "(&(objectClass=user)(sAMAccountName=WAG))")
  if res == "":
    print("No result")
  else: 
    str = str(res[0][1]["memberOf"])
    st = str.split("'")
    for s in st:
        if s == "[b":
            continue
        gruppen = s.split("=")
        for g in gruppen:
            g = g.split(",")[0]
            if g == "Lehrer":
                print("Zugang gewährt")
            if g == "Sportfest":
                print("Adminzugang")
  #print(res)"""
