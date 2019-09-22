USER=app

cd /app/

# Use .env.example to get relevant env args and put them in .env for runtime loading
awk -F'=' '{ print $1"="ENVIRON[$1] }' /app/.env.example > /app/.env

# Fetch data
if [ ! -z "${DATA_DOWNLOAD}" ]; then
  mkdir -p "${DATA_DIR}"
  curl "${DATA_DOWNLOAD}" | bsdtar -xvf - -C "${DATA_DIR}"
fi

# Ensure data isn't empty
if [ -d "${DATA}" ] && [ -z "$(ls ${DATA})" ]; then
  echo "Data directory is empty! Perhaps you forgot to mount ${DATA} or provide a download? exiting..."
  exit 1
fi

# Ensure our user has access to the data directory
chown -R $USER:$USER $DATA_DIR

if [ "$1" == "bash" ]; then
  echo "Running in bash mode..."
  bash
elif [ "$1" == "cron" ] || [ "${FORCE_CRON}" -eq 1 ]; then
  echo "Running in cron mode..."
  date
  set -x
  (
    echo "${CRON} (date && cd /app/ && sudo -u ${USER} /app/enrichrbot.py) >> /proc/1/fd/1 2>/proc/1/fd/2"
  ) >> /etc/cron.d/enrichrbot
  chmod 700 /etc/cron.d/enrichrbot
  crontab /etc/cron.d/enrichrbot
  cron -f
else
  echo "Running in single-shot mode..."
  set -x
  sudo -u $USER /app/enrichrbot.py $@
fi
