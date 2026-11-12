"""Runs inside Indexd. Preserve existing passwords, fail on a mismatch."""
import json
import sys
sys.path.insert(0, '/var/www/indexd')
from local_settings import settings
from indexd.auth.drivers.alchemy import AuthRecord

driver = settings['auth']
for username, password in json.load(sys.stdin).items():
    with driver.session as session:
        exists = session.query(AuthRecord).filter(AuthRecord.username == username).first() is not None
    if not exists:
        driver.add(username, password)
    driver.auth(username, password)
print('Indexd service credentials verified.')
