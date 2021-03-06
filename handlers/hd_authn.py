"""Handler for OpenID authentication and account management."""

import traceback
import sys
import os
import os.path
import posixpath
import time
from mod_python import apache, util, Session
from openid.store import filestore
from openid.consumer import consumer
from openid.extensions import sreg

import Context
import Logger
import Account
from handler_utils import server_error

store = None

def random_key(length):
	rng = open("/dev/urandom", "r")
	raw_key = rng.read(16)
	key = ""
	for b in raw_key:
		key += "%02x" % ord(b)
	rng.close()
	return key

def verify(req):
	try:
		Context.log_ctx.generate()
		return verify_core(req)
	except apache.SERVER_RETURN, ex:
		# Catch and re-raise apache/mod_python exceptions here
		raise
	except Exception, ex:
		return server_error(req)

def verify_core(req):
	"""This is the first phase of the OpenID login. We check the
	provided identifier, try to work out who we should ask about it,
	and redirect the user to the provider's site for their login
	process."""
	# Set up the OpenID library
	session = Session.Session(req, timeout=60)
	global store
	if store is None:
		Logger.log.debug("Creating new store")
		server_options = req.get_options()
		store_path = os.path.join(server_options['wor.root_path'], "oid_store")
		store = filestore.FileOpenIDStore(store_path)
	oid_consumer = consumer.Consumer(session, store)

	# Get the user's account details that they provided
	if getattr(req, "form", None) is None:
		req.form = util.FieldStorage(req, True)
	account = req.form.getfirst("openid_identifier")

	# Look up the OAuth provider for this account
	try:
		request = oid_consumer.begin(account)
	except consumer.DiscoveryFailure, ex:
		raise

	if request is None:
		raise Exception("No OpenID services found for " + account)

	# We request some other details from them, too, so that we can use
	# them in the account.
	sreg_request = sreg.SRegRequest(
		required = ['nickname', 'email'], optional = ['fullname', 'timezone'])
	request.addExtension(sreg_request)

	# Start the authN process
	trust_root = req.construct_url("")
	return_to = posixpath.join(trust_root, "process")
	
	if request.shouldSendRedirect():
		# Run as a redirect
		Logger.log.debug("Redirecting to: " + request.redirectURL(trust_root, return_to))
		util.redirect(req,
					  request.redirectURL(trust_root, return_to),
					  permanent = False
					  )
		# Does not return
	else:
		# Run as a POST
		form_html = request.htmlMarkup(
			trust_root,
			return_to,
			form_tag_attrs = { 'id': 'openid_message' }
			)
		Logger.log.debug("POSTing with: " + form_html)
		req.content_type = "text/html"
		req.write(form_html)
		return apache.OK

def process(req):
	try:
		Context.log_ctx.generate()
		return process_core(req)
	except apache.SERVER_RETURN, ex:
		# Catch and re-raise apache/mod_python exceptions here
		raise
	except Exception, ex:
		return server_error(req)

def process_core(req):
	Logger.log.debug("Processing request: " + str(req))
	# Set up OpenID library
	session = Session.Session(req, timeout=60)
	global store
	if store is None:
		Logger.log.debug("Creating new store")
		server_options = req.get_options()
		store_path = os.path.join(server_options['wor.root_path'], "oid_store")
		store = filestore.FileOpenIDStore(store_path)
	oid_consumer = consumer.Consumer(session, store)

	# Get request parameters
	if getattr(req, "form", None) is None:
		req.form = util.FieldStorage(req, True)

	# Convert the request parameters into an ordinary decent
	# dictionary for the oid_consumer to use
	params = {}
	for k in req.form:
		params[k] = req.form.getfirst(k).value

	Logger.log.debug("Request was " + str(params))

	url = req.construct_url("/process")
	info = oid_consumer.complete(params, url)

	display_identifier = info.getDisplayIdentifier()

	if info.status == consumer.FAILURE and display_identifier:
		# In the case of failure, if info is non-None, it is the
		# URL that we were verifying. We include it in the error
		# message to help the user figure out what happened.
		fmt = "Verification of %s failed: %s"
		# FIXME: To avoid XSS issues, quote this identifier before
		# echoing it back (and below)
		message = fmt % (display_identifier,
						 info.message)
	elif info.status == consumer.SUCCESS:
		# Success means that the transaction completed without
		# error. If info is None, it means that the user cancelled
		# the verification.
		css_class = 'alert'

		# This is a successful verification attempt. If this
		# was a real application, we would do our login,
		# comment posting, etc. here.
		fmt = "You have successfully verified %s as your identity."
		message = fmt % (display_identifier,)
		if info.endpoint.canonicalID:
			# You should authorize i-name users by their canonicalID,
			# rather than their more human-friendly identifiers.  That
			# way their account with you is not compromised if their
			# i-name registration expires and is bought by someone else.
			message += ("  This is an i-name, and its persistent ID is %s"
						% (info.endpoint.canonicalID,))

		# FIXME: We should check here whether the account exists. If
		# it doesn't, we need to create the account using SREG data,
		# and drop the user into a character-creation screen. If it
		# does exist, we should drop them into the game UI, in
		# "character-selection" mode.
		accid = Account.get_id_from_name(display_identifier)
		if accid is None:
			# Then there's no corresponding account: create one
			pass

		# We generate a random string to use as a session key, store
		# that locally for the account's session, and push it up to
		# the browser for temporary storage while it loads the game
		# interface.
		key = random_value(16)
		req.headers_out['X-WoR-Session-Key'] = key
		Account.set_session_key(accid, key)
		req.write("""<html><head><title>WoR</title><script src="/js/redirect.js" type="text/javascript"/></head><body onload="load_game(%{url}s);"></body></html>""" % ("http://game.worldofrodney.org/",))

		return apache.OK
			
	elif info.status == consumer.CANCEL:
		# cancelled
		message = 'Verification cancelled'
	elif info.status == consumer.SETUP_NEEDED:
		if info.setup_url:
			message = '<a href=%s>Setup needed</a>' % (
				quoteattr(info.setup_url),)
		else:
			# This means auth didn't succeed, but you're welcome to try
			# non-immediate mode.
			message = 'Setup needed'
	else:
		# Either we don't understand the code or there is no
		# openid_url included with the error. Give a generic
		# failure message. The library should supply debug
		# information in a log.
		message = 'Verification failed.'

	req.write(message)

	return apache.OK
