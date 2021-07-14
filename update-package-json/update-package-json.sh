if [[ "$(uname)" == "Darwin" ]]; then
    sed -r -i '' 's/"version": ".+"/"version": "'"${INPUT_VERSION}"'"/g' package.json
else
    sed -ri 's/"version": ".+"/"version": "'"${INPUT_VERSION}"'"/g' package.json
fi
