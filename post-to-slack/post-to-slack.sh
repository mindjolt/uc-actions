FORMATTED_DATE=$(date "+%Y-%m-%d")
REPOSITORY_URL="https://github.com/${GITHUB_REPOSITORY}"

MESSAGE="\`\`\`"
MESSAGE+="${INPUT_PROJECT_NAME} ${INPUT_VERSION} was cut today!\n\n"
MESSAGE+="GitHub: ${REPOSITORY_URL}/tree/${INPUT_VERSION}\n"
MESSAGE+="Changelog: ${REPOSITORY_URL}/blob/${INPUT_VERSION}/CHANGELOG.md#${INPUT_VERSION//./}---${FORMATTED_DATE}"
MESSAGE+="\`\`\`"

RESPONSE=$(curl -f \
    -X POST \
    -H "Authorization: Bearer ${INPUT_TOKEN}" \
    -H "Content-type: application/json" \
    --data "{\"channel\":\"${INPUT_CHANNEL}\",\"text\":\"${MESSAGE}\"}" \
    "https://slack.com/api/chat.postMessage")

if [[ "${RESPONSE}" != *"bot_message"* ]]; then
    >&2 echo "${RESPONSE}"
    exit 1
else
    echo "${RESPONSE}"
fi
