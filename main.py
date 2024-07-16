#!/usr/bin/env python3
import requests, json, re, os, dotenv
from utils import output

# Loading .env values
dotenv.load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CONSOLE_URL = os.getenv('CONSOLE_URL')
ENV = os.getenv('ENV')
RETENTION_LOGS_DAYS = int(os.getenv('RETENTION_LOGS_DAYS'))

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
    'France': ['(?i)^(C|S|V)FR.+', '(?i)^Julie.+'],
    'Germany': ['(?i)^(C|S|V)DE.+'],
    'Italy': ['(?i)^(C|S|V)IT.+'],
    'Nordic': ['(?i)^(C|S|V)SE.+'],
    'Poland': ['(?i)^(C|S|V)PL.+'],
    'Shared Services': ['(?i)^AZ.+'],
    'South Africa': ['(?i)^(C|S|V)ZA.+'],
    'Spain & Portugal': ['(?i)^(C|S|V|EU)?ES.+'],
    'United Arabic Emirates': [],
    'United Kingdom': ['(?i)^(C|S|V)(GB|UK).+'],
    'Switzerland': ['(?i)^(C|S|V)CH.+', '(?i)^Condor.+'],
    'Default site': [],
    'Camlog - Medentis': []
}

authHeaders = { 'Authorization': f'ApiToken {API_TOKEN}'}

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
            output(f'ERROR: failed attempt to move agent. Status code is {postMoveAgentResponse.status_code}\nResponse:\n{postMoveAgentResponse.text}', doExit=True)
        output(f"{site} -> {[name for name, id in endpoints]}")

def classifyEndpoint(endpoint, toBeMovedEndpoints):
    for site, patterns in SITE_PATTERN_MATCHING.items():
        if any([re.match(pattern, endpoint['computerName']) for pattern in patterns]):
            toBeMovedEndpoints[site].append((endpoint['computerName'], endpoint['id']))
            return
    output(f"WARNING: Endpoint {endpoint['computerName']} did not match any patterns from SITE_PATTERN_MATCHING object. No action was performed.")



def getSiteIDs():
    getSitesResponse = requests.get(CONSOLE_URL + GET_SITES_URL, headers=authHeaders, params={'availableMoveSites': True, 'limit': 1000})
    if getSitesResponse.status_code != 200:
        output(f'ERROR: failed attempt to retrieve sites from the console. Status code is {getSitesResponse.status_code}\nResponse:\n{getSitesResponse.text}', doExit=True)
    getSitesJsonData = json.loads(getSitesResponse.text)
    sitesIDs = {}
    for siteData in getSitesJsonData["data"]["sites"]:
        if siteData["name"] in SITE_PATTERN_MATCHING.keys():
            sitesIDs[siteData["name"]] = siteData["id"]
        else:
            output(f"ERROR: Site '{siteData['name']}' has no pattern associated in SITE_PATTERN_MATCHING object. Please add the key and associate a list of patterns (regex) or an empty array to ignore it.", doExit=True)
    output(f"Successfully loaded sites IDs from the API")
    if len(sitesIDs.keys()) != len(SITE_PATTERN_MATCHING.keys()):
        output(f"ERROR: Mismatch between SITE_PATTERN_MATCHING keys (site names) and API result.\nAPI returned site list: {sorted(sitesIDs.keys())}\nSITE_PATTERN_MATCHING expected following to be returned from API: {sorted(SITE_PATTERN_MATCHING.keys())}\n\nIs the service account admin on all mentioned sites?", doExit=True)
    return sitesIDs


"""
    Beginning of the main execution
"""

# Retrieve all sites' IDs (mandatory for further API calls)
siteIDs = getSiteIDs()

# Retrieve all agents in the Default site
getAgentResponse = requests.get(CONSOLE_URL + GET_AGENTS_URL, headers=authHeaders, params={'filteredSiteIds': siteIDs["Default site"], "limit": 1000})
if getAgentResponse.status_code != 200:
    output(f'ERROR: status code is {getAgentResponse.status_code}\nResponse:\n{getAgentResponse.text}', doExit=True)
getAgentJsonData = json.loads(getAgentResponse.text)

# Classify endpoints per site in a new object
toBeMovedEndpoints = {key: [] for key in siteIDs.keys()}
for endpoint in getAgentJsonData["data"]:
    classifyEndpoint(endpoint, toBeMovedEndpoints)

# Summarize and display the classified endpoints
isWorthMove = False
if ENV != "prod":
    output(f"=========================\nAgents that will me moved\n=========================")
for site, endpoints in toBeMovedEndpoints.items():
    if len(endpoints) > 0:
        isWorthMove = True
        if ENV != "prod":
            output(f"{site}:" + ''.join([f'\n\t{name}' for name, id in endpoints]))

# No endpoint to be moved; abort the process
if not isWorthMove:
    output("WARNING: No agent to move. If this behaviour is not expected, please edit the SITE_PATTERN_MATCHING patterns to include agents.", doExit=True)

# If in production, move the endpoints
# If not, prompt an approval before API calls
if (ENV == "prod" or input("\n\nConfirm changes and move the agents in the console? (Yes/No): ").lower() == "yes"):
    output("INFO: Moving agents...")
    moveEndpoints(toBeMovedEndpoints)
else:
    output("INFO: Aborted. No endpoint was moved.")



