# Script purpose
This script will help SentinelOne console administrators to move endpoints, based in the endpoint name, to a target site.
Naming convention will be specified in the script with regular expressions (regex) to define the destination site.

Expected use case:
- Move all endpoints landing in the fallback (default) site their destination site based on naming convention.

# Environment setup
## Install dependencies
```bash
python -m pip install -r requirements.txt
```
## Generate a service account in SentinelOne for API requests
### Create a dedicated role
Best practise is to create a new role with minimal permissions.
Here are the only two required permissions to sort endpoints with this script:
- Endpoints > View
- Endpoints > Move to another site

### Create a dedicated service account
The account must be generated as a Service account and not a Console account.
Generate the account at the Account (not Site or Global) level with the dedicated role previously created.

## Prepare environment variables
- Copy or rename .env.example into .env
- Generate your API key in SentinelOne*
- Update the API token and console URL in the .env file
- Test the script locally with a the ENV variable set to "local"
- Optional: deploy this script in an automated task (like cron on an Unix system). Please use "ENV=prod" to disable the prompt and generate log files

*SentinelOne account must be a service account with admin rights on all sites you will interact with (source & destinations)

## Edit the scripts behaviour according to you needs
- Edit the SITE_PATTERN_MATCHING object as follow
```python
SITE_PATTERN_MATCHING = {
    '{site name in S1 console}': ['endpoint name regex 1', 'endpoint name regex 1'],
    '{site name in S1 console}': [] # Ignored sites (no matching naming convention)
}
# You need to provide the EXAUSTIVE list of ALL sites, otherwise the script will throw an error.
# Create the site with an empty array if you want to ignore it.
```
