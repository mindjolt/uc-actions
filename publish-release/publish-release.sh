RESPONSE=$(curl -f \
    -X "POST" \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${INPUT_TOKEN}" \
    -d "{\"tag_name\":\"${INPUT_VERSION}\",\"target_commitish\":\"${INPUT_REF}\"}" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/releases")

if [[ "${RESPONSE}" != *""* ]]; then
    >&2 echo "${RESPONSE}"
    exit 1
else
    echo "${RESPONSE}"
fi
