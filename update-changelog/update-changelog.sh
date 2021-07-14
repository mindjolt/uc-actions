FORMATTED_DATE=$(date "+%Y-%m-%d")
CHANGELOG="CHANGELOG.md"
REPOSITORY_URL="https://github.com/${GITHUB_REPOSITORY}"

SEARCH_FOR="## \[Unreleased\]"

REPLACE_WITH="## [Unreleased]\n"
REPLACE_WITH+="### Added\n\n"
REPLACE_WITH+="### Fixed\n\n"
REPLACE_WITH+="### Changed\n\n"
REPLACE_WITH+="### Deprecated\n\n"
REPLACE_WITH+="### Removed\n\n"
REPLACE_WITH+="## [${INPUT_VERSION}] - ${FORMATTED_DATE}"

LINK_TEXT="[Unreleased]: ${REPOSITORY_URL}/compare/${INPUT_VERSION}...HEAD\n"
LINK_TEXT+="[${INPUT_VERSION}]: ${REPOSITORY_URL}/tree/${INPUT_VERSION}"

if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' 's/'"${SEARCH_FOR}"'/'"${REPLACE_WITH}"'/g' ${CHANGELOG}
    sed -r -i '' 's%\[Unreleased\]: .+%'"${LINK_TEXT}"'%g' ${CHANGELOG}
else
    sed -i 's/'"${SEARCH_FOR}"'/'"${REPLACE_WITH}"'/g' ${CHANGELOG}
    sed -ri 's%\[Unreleased\]: .+%'"${LINK_TEXT}"'%g' ${CHANGELOG}
fi
