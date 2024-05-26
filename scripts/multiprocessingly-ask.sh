#!/bin/bash

url="https://api.openai.com/v1/chat/completions"
key=$OPENAI_API_KEY

# note: testé sur linux seulement (Debian 11).

# deps:
#   - curl
#   - jq

# pour le multiprocessing, adapté le code trouvé ici:
# https://medium.com/@robert.i.sandor/getting-started-with-parallelization-in-bash-e114f4353691

build_request() {
    # deux fichiers en arguments (la consigne et le texte à analyser) concaténés dans le message.
    file_consigne="$1"
    file_text="$2"
    # nécessite que ces deux arguments soient des fichiers.
    if ! [ -f "$file_consigne" ] || ! [ -f "$file_text" ];then
        exit 1
    fi
    # construit le json
    jq -n \
        --arg content "$(cat "$file_consigne" "$file_text")" \
        '{model: "gpt-3.5-turbo", temperature: 0, messages: [{role: "user", content: $content}]}'
}

send_request() {
    curl "$url" \
        -H "Authorization: Bearer $key" \
        -H "Content-Type: application/json" \
        -d "$1"
}

ask_then_write() {
    send_request "$(build_request $1 $2)" | \
        jq '.choices[0].message.content' -r \
        > $3/$(basename $2).json
}

max_num_processes=$(ulimit -u)
limiting_factor=4
num_processes=$((max_num_processes/limiting_factor))
# > this gets the max number of processes for the user
# > An arbitrary limiting factor so that there are some free processes
# > in case I want to run something else

for file in $2/*; do
    ((i=i%num_processes)); ((i++==0)) && wait
    ask_then_write "$1" "$file" "$3" &
done
