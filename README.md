# Script purpose
This script will help SentinelOne console administrators to move endpoints, based in the endpoint name, to a target site.
Naming convention will be specified in the script with regular expressions (regex) to define the destination site.

Expected use case:
- Move all endpoints landing in the fallback (default) site their destination site based on naming convention.

# Environment setup
## Install dependancies
```bash
python -m pip install -r requirements.txt
```
## Prepare environment variables
- Copy or rename .env.example into .env
- Generate your API key in SentinelOne*
- Update the API token and console URL in the .env file

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
