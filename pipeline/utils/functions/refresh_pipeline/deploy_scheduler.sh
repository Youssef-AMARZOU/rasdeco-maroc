"""
deploy_scheduler.sh -- Script de creation des 6 jobs Cloud Scheduler pour RASD-Maroc.

Usage:
  bash deploy_scheduler.sh                             # Preview
  bash deploy_scheduler.sh --apply                     # Deploy
  bash deploy_scheduler.sh --delete                    # Delete all

Chaque module a sa propre frequence :
  - economie:    hebdomadaire (lundi 06:00 UTC)
  - social:      annuelle (01/01 08:00 UTC)
  - education:   annuelle (01/09 08:00 UTC)
  - sante:       annuelle (01/04 08:00 UTC)
  - agriculture: saisonniere (01/03, 01/10) + NDVI
  - sport:       quotidienne (06:00 UTC)
"""

PROJECT="${GCP_PROJECT:-rasd-maroc}"
REGION="${GCP_REGION:-europe-west1}"
FUNCTION_URL="${FUNCTION_URL:-https://europe-west1-rasd-maroc.cloudfunctions.net/refresh}"

SCHEDULES=(
  "economie:0 6 * * 1"
  "social:0 8 1 1 *"
  "education:0 8 1 9 *"
  "sante:0 8 1 4 *"
  "agriculture-saisonnier:0 8 1 3,10 *"
  "agriculture-ndvi:0 6 */14 * *"
  "sport:0 6 * * *"
)

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=== Cloud Scheduler jobs for RASD-Maroc ==="
echo "Project: $PROJECT"
echo "Region:  $REGION"
echo ""

for entry in "${SCHEDULES[@]}"; do
  NAME="${entry%%:*}"
  SCHED="${entry##*:}"
  MODULE="${NAME%-*}"

  # Determine module name
  if [[ "$NAME" =~ ^economie ]]; then MODULE="economie"; fi
  if [[ "$NAME" =~ ^social ]]; then MODULE="social"; fi
  if [[ "$NAME" =~ ^education ]]; then MODULE="education"; fi
  if [[ "$NAME" =~ ^sante ]]; then MODULE="sante"; fi
  if [[ "$NAME" =~ ^agriculture ]]; then MODULE="agriculture"; fi
  if [[ "$NAME" =~ ^sport ]]; then MODULE="sport"; fi

  if [ "$1" = "--apply" ]; then
    echo "Creating: $NAME (module=$MODULE, cron=\"$SCHED\")"
    gcloud scheduler jobs create http "refresh-$NAME" \
      --project="$PROJECT" \
      --location="$REGION" \
      --schedule="$SCHED" \
      --uri="$FUNCTION_URL" \
      --http-method=POST \
      --headers="Content-Type=application/json" \
      --message-body="{\"module\": \"$MODULE\"}" \
      --time-zone="UTC" \
      --description="Refresh $MODULE data pipeline"
  elif [ "$1" = "--delete" ]; then
    echo "Deleting: refresh-$NAME"
    gcloud scheduler jobs delete "refresh-$NAME" \
      --project="$PROJECT" --location="$REGION" --quiet
  else
    echo "[PREVIEW] Would create: refresh-$NAME"
    echo "  Module:    $MODULE"
    echo "  Schedule:  \"$SCHED\""
    echo "  URI:       $FUNCTION_URL"
    echo "  Body:      {\"module\": \"$MODULE\"}"
  fi
  echo ""
done

if [ "$1" != "--apply" ] && [ "$1" != "--delete" ]; then
  echo "---"
  echo "Pass --apply to actually create jobs, --delete to remove them."
fi
