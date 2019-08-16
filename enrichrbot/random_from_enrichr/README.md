# EnrichrBot: Random from Enrichr

This script runs an Enrichr bot which exclusivly uses the enrichr API--allows you to tweet from a randomly chosen Enrichr library genesets. Uses enrichr API to get a list of libraries (whitelist and blacklist can filter this set). Submits list to enrichr, gets screenshot of results, and finally tweets the results with the screenshot.

## Production

### Run
```bash
# Run but show what we would have tweeted (no tweet made)
docker-compose run enrichrbot --dry-run
# Run and actually tweet
docker-compose run enrichrbot
```

### Deployment
```bash
docker-compose build
docker-compose push
```

## Development

### Setup
```bash
# Setup venv
python3 -m venv venv
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

### Run
```
source venv/bin/activate
python enrichrbot.py --dry-run
```

### .env
If present, a .env will be referenced as a fallback to explicitly set environment variables--see `.env.example`.

## Cron mode
While it's better to schedule this somewhere else--if required the image can use the env `CRON` with the cron time definition (i.e. `0 0 * * *`).

## Bash mode
If you just want to use bash, use the command `bash`.
