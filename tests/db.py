import sys

sys.path.insert(0, '../code')

import db

response = db.aliasPin("test", 1)
assert response.success, "Failed to alias pin"
response = db.setPinEnabled("test", True)
assert response.success, "Failed to set pin status"
response = db.getPinEnabled("test")
assert response.success, "Failed to get pin status"
response = db.unsetPin(1)
assert response.success, "Failed to unset pin"
print("All tests passed!")