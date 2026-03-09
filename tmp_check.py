import json, shutil

print("jq path:", shutil.which("jq"))
with open("data/vm-types.json") as f:
    data = json.load(f)
langs = [vm["name"] for vm in data["vms"]["language"]]
print("languages in json:", langs)
