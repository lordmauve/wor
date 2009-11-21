from Database import DB

def get_id_from_name(name):
	cur = DB.cursor()
	cur.execute("SELECT account_id FROM account"
				+ " WHERE username = %{username}s",
				{ 'username': display_identifier } )
	row = cur.fetchone()
	if row is None:
		return None
	return row[0]

def set_session_key(accid, key):
	cur = DB.cursor()
	cur.execute("UPDATE account "
				+ " SET key = %{key}s, "
				+ "     last_seen = %{now}s"
				+ " WHERE account_id = %{id}s",
				{ 'key': key,
				  'id': accid,
				  'now': time.time() } )

def touch_account(accid):
	cur = DB.cursor()
	cur.execute("UPDATE account SET last_seen = %{now}s"
				+ " WHERE account_id = %{id}s",
				{ 'now': time.time(),
				  'id': accid })

def create_account(name, email, nickname=None):
	cur = DB.cursor()
	cur.execute("INSERT INTO account (username, email, nickname)"
				+ " VALUES (%{username}s, %{email}s, %{nick}s",
				{ 'username': name,
				  'email': email,
				  'nick': nickname })
