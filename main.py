import requests, json, re, os, dotenv

# Loading .env values
dotenv.load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CONSOLE_URL = os.getenv('CONSOLE_URL')

# API endpoints (concatenated to CONSOLE_URL)
GET_AGENTS_URL = "/web/api/v2.1/agents"
GET_SITES_URL = "/web/api/v2.1/sites"
MOVE_SITE_URL = "/web/api/v2.1/agents/actions/move-to-site"

# Please edit this object according to your needs
SITE_PATTERN_MATCHING = {
    # Use '(?i)' at the beginning of the regex to disable case sensitiveness
    'Austria': ['(?i)^(C|S|V)AT.+'],
    'Benelux': ['(?i)^(C|S|V)(BE|NL).+'],
    'Czech Republic': ['(?i)^(C|S|V)CZ.+'],
    'France': ['(?i)^(C|S|V)FR.+'],
    'Germany': ['(?i)^(C|S|V)DE.+'],
    'Italy': ['(?i)^(C|S|V)IT.+'],
    'Nordic': [],
    'Poland': ['(?i)^(C|S|V)PL.+'],
    'Shared Services': ['(?i)^AZ.+'],
    'South Africa': ['(?i)^(C|S|V)ZA.+'],
    'Spain & Portugal': ['(?i)^(C|S|V)ES.+'],
    'United Arabic Emirates': [],
    'United Kingdom': ['(?i)^(C|S|V)(GB|UK).+'],
    'Switzerland': ['(?i)^(C|S|V)CH.+'],
    'Default site': [],
    'Camlog - Medentis': []
}

authHeaders = { 'Authorization': f'ApiToken {API_TOKEN}'}

"""
    Utilities
"""
def writeJsonToFile(text):
    with open('debugOutput.json', 'w') as f:
        f.write(json.dumps(json.loads(text), indent=2))

def moveEndpoints(toBeMovedEndpoints):
    for site, endpoints in toBeMovedEndpoints.items():
        if len(endpoints) <= 0:
            continue # Skip this site if endpoint list is empty
        postData = {
            'data': {
                'targetSiteId': siteIDs[site]
            },
            'filter': {
                'ids': [id for name, id in endpoints]
            }
        }
        postMoveAgentResponse = requests.post(CONSOLE_URL + MOVE_SITE_URL, headers=authHeaders, json=postData)
        if postMoveAgentResponse.status_code != 200:
            print(f'❌ ERROR: failed attempt to move agent. Status code is {postMoveAgentResponse.status_code}\nResponse:\n{postMoveAgentResponse.text}')
            exit()
        print(f"✅ {site} -> {len(endpoints)} agent{'s' if len(endpoints) > 1 else ''}")

def classifyEndpoint(endpoint, toBeMovedEndpoints):
    for site, patterns in SITE_PATTERN_MATCHING.items():
        if any([re.match(pattern, endpoint['computerName']) for pattern in patterns]):
            toBeMovedEndpoints[site].append((endpoint['computerName'], endpoint['id']))
            return
    print(f"❗ Endpoint {endpoint['computerName']} did not match any patterns from SITE_PATTERN_MATCHING object. No action was performed.")



def getSiteIDs():
    getSitesResponse = requests.get(CONSOLE_URL + GET_SITES_URL, headers=authHeaders, params={'availableMoveSites': True, 'limit': 1000})
    if getSitesResponse.status_code != 200:
        print(f'❌ ERROR: failed attempt to retrieve sites from the console. Status code is {getSitesResponse.status_code}\nResponse:\n{getSitesResponse.text}')
        exit()
    getSitesJsonData = json.loads(getSitesResponse.text)
    sitesIDs = {}
    for siteData in getSitesJsonData["data"]["sites"]:
        if siteData["name"] in SITE_PATTERN_MATCHING.keys():
            sitesIDs[siteData["name"]] = siteData["id"]
        else:
            print(f"❌ ERROR: Site '{siteData['name']}' has no pattern associated in SITE_PATTERN_MATCHING object. Please add the key and associate a list of patterns (regex) or an empty array to ignore it.")
            exit()
    print(f"✅ Successfully loaded sites IDs from the API")
    if len(sitesIDs.keys()) != len(SITE_PATTERN_MATCHING.keys()):
        print(f"❌ ERROR: Mismatch between SITE_PATTERN_MATCHING keys (site names) and API result.\nAPI returned site list: {sorted(sitesIDs.keys())}\nSITE_PATTERN_MATCHING expected following to be returned from API: {sorted(SITE_PATTERN_MATCHING.keys())}\n\nIs the service account admin on all mentioned sites?")
        exit()
    return sitesIDs


"""
    Beginning of the main execution
"""

# Retrieve all sites' IDs (mandatory for further API calls)
siteIDs = getSiteIDs()

# Retrieve all agents in the Default site
getAgentResponse = requests.get(CONSOLE_URL + GET_AGENTS_URL, headers=authHeaders, params={'filteredSiteIds': siteIDs["Default site"], "limit": 1000})
if getAgentResponse.status_code != 200:
    print(f'❌ ERROR: status code is {getAgentResponse.status_code}\nResponse:\n{getAgentResponse.text}')
    exit()

getAgentJsonData = json.loads(getAgentResponse.text)

toBeMovedEndpoints = {key: [] for key in siteIDs.keys()}
for endpoint in getAgentJsonData["data"]:
    classifyEndpoint(endpoint, toBeMovedEndpoints)

print(f"=========================\nAgents that will me moved\n=========================")
isWorthMove = False
for site, endpoints in toBeMovedEndpoints.items():
    if len(endpoints) > 0:
        isWorthMove = True
        print(f"{site}:" + ''.join([f'\n\t{name}' for name, id in endpoints]))

if not isWorthMove:
    print("No agent to move. If this behaviour is not expected, please edit the SITE_PATTERN_MATCHING patterns to include agents.")
    exit()

if (input("\n\nConfirm changes and move the agents in the console? (Yes/No): ").lower() == "yes"):
    print("Moving agents...")
    moveEndpoints(toBeMovedEndpoints)
else:
    print("Aborted; No endpoint was moved.")



