USER=app

cd /app/

# Use .env.example to get relevant env args and put them in .env for runtime loading
awk -F'=' '{ print $1"="ENVIRON[$1] }' /app/.env.example > /app/.env

# Setup data directory
mkdir -p $DATA_DIR
chown -R $USER:$USER $DATA_DIR

if [ "$1" == "bash" ]; then
  echo "Running in bash mode..."
  bash
elif [ "$1" == "cron" ] || [ "${FORCE_CRON}" -eq 1 ]; then
  echo "Running in cron mode..."
  set -x
  (
    echo "${CRON} sudo -u ${USER} /app/enrichrbot.py >> /proc/1/fd/1 2>/proc/1/fd/2"
  ) >> /etc/cron.d/enrichrbot
  chmod +x /etc/cron.d/enrichrbot
  crontab /etc/cron.d/enrichrbot
  cron -f
else
  echo "Running in single-shot mode..."
  set -x
  sudo -u $USER /app/enrichrbot.py $@
fi
