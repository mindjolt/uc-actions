#!/bin/bash

set -eux -o pipefail

TEMP_FILE="failed-tests"

if [ "${INPUT_NAME}" == "" ]; then
    INPUT_NAME="test-results"
fi

if [ -f "${TEMP_FILE}" ]; then
    rm "${TEMP_FILE}"
fi

for FILENAME in ${INPUT_FILES}; do
    FAILED_TESTS=$({ grep "<test-case" "${FILENAME}" || test $? = 1; } \
        | { grep "result=\"Failed\"" || test $? = 1; } \
        | { grep -Eo "fullname=\"[^\"]+\"" || test $? = 1; } \
        | cut -d \" -f 2 \
        | cut -d \( -f 1 \
        | sort \
        | uniq)

    if [ ! "${FAILED_TESTS}" == "" ]; then
        if [ -f "${TEMP_FILE}" ]; then
            echo "" >> "${TEMP_FILE}"
        fi

        echo "${FILENAME}:" >> "${TEMP_FILE}"
        echo "${FAILED_TESTS}" >> "${TEMP_FILE}"
    fi
done

if [ -f "${TEMP_FILE}" ]; then
    if [ "${GITHUB_EVENT_NAME}" == "pull_request" ]; then
        GITHUB_SHA=$(jq -r '.pull_request.head.sha' < "${GITHUB_EVENT_PATH}")
    fi

    PARAMETERS="\"accept\":\"application/vnd.github.v3+json\""
    PARAMETERS+=",\"name\":\"${INPUT_NAME}\""
    PARAMETERS+=",\"head_sha\":\"${GITHUB_SHA}\""

    RESPONSE=$(curl -fS \
        -X "POST" \
        -H "Content-Type: application/json" \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -d "{${PARAMETERS}}" \
        "https://api.github.com/repos/${GITHUB_REPOSITORY}/check-runs")

    CHECK_RUN_ID=$(jq '.id' <<< "${RESPONSE}")
    TEXT=$(jq -sR . "${TEMP_FILE}")

    PARAMETERS="\"accept\":\"application/vnd.github.v3+json\""
    PARAMETERS+=",\"check_run_id\":\"${CHECK_RUN_ID}\""
    PARAMETERS+=",\"conclusion\":\"action_required\""
    PARAMETERS+=",\"output\":{\"title\":\"Failed tests\",\"summary\":\"Some unit tests have failed\",\"text\":${TEXT}}"

    curl -fS \
        -X "PATCH" \
        -H "Content-Type: application/json" \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -d "{${PARAMETERS}}" \
        "https://api.github.com/repos/${GITHUB_REPOSITORY}/check-runs/${CHECK_RUN_ID}"
fi
