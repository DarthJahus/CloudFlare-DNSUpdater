#!/usr/bin/python3

import requests
import json

__providers = ["https://icanhazip.com", "https://api.ipify.org/", "https://ident.me"]
__token = None
__data = None

try:
	with open("config.json", "r") as _config_file:
		_config = _config_file.read()
		__data = json.loads(_config)
		_config_file.close()
except:
	print("Can't open config file.")

# Get IP address

_ext_ip = None

for _provider in __providers:
	try:
		_request = requests.get(_provider)
		_ext_ip = _request.content.decode('utf8').strip()
		break
	except:
		print("ERROR: Provider %s unreachable" % _provider)

if _ext_ip:
	print("External IP: %s" % _ext_ip)
else:
	print("ERROR: Failed to get external IP.")
	exit(1)

# Set new IP for zone

if not __data:
	print("Token file not found in script folder.")
	exit(1)

# Get zones

## If subdomain, get main zone
_zone = __data["domain"]
if len(__data["domain"].split('.')) > 2:
	_zone = '.'.join(__data["domain"].split('.')[-2:])
## Get zone records
_req = requests.get(
	"https://api.cloudflare.com/client/v4/zones/%s/dns_records/?name=%s" % (__data["zone-id"], __data["domain"]),
	headers={
		"Authorization": "Bearer %s" % __data["token"],
		"Content-Type": "application/json"
	}
)
## Check request
if _req.status_code != 200:
	print("Error while contacting the API")
	if "errors" in _req.json():
		for _error in _req.json()["errors"]:
			print(_error)
	exit(1)
# Get record data
_req_json = _req.json()
_record_data = None
for _record in _req_json["result"]:
	if _record["name"].lower() == __data["domain"].lower():
		_record_data = {
			"id": _record["id"],
			"content": _record["content"]
		}
		break
if not _record_data:
	print("Something went wrong while retrieving domain record data.")
	exit(1)
# Update record
_req = requests.patch(
	"https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s" % (__data["zone-id"], _record_data["id"]),
	headers={
		"Authorization": "Bearer %s" % __data["token"],
		"Content-Type": "application/json"
	},
	data=json.dumps({
		"content": _ext_ip
	})
)
## Check request
if _req.status_code != 200:
	print("Error while contacting the API")
	if "errors" in _req.json():
		for _error in _req.json()["errors"]:
			print(_error)
	exit(1)
# Get answer
_req_json = _req.json()
if not _req_json["success"]:
	print("Error while updating domain record.")
	for _error in _req_json["errors"]:
		print(_error)
	exit(1)
if _record_data["id"] != _req_json["result"]["id"]:
	print("Something went wrong while trying to update domain record (ID mismatch).")
	exit(1)
else:
	if _req_json["result"]["content"] != _ext_ip:
		print("Domain record failed to update to new IP (IP mismatch: %s vs ext:%s)." % (_req_json["result"]["content"], _ext_ip))
		exit(1)
	else:
		print("New IP %s correctly set for record %s" % (_ext_ip, __data["domain"]))
		exit(0)
