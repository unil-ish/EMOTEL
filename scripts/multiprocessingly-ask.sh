#!/bin/bash

# deps:
#   - curl
#   - jq
#
# note: 
#   testé sur linux seulement (Debian 11).

url="https://api.openai.com/v1/chat/completions"
key=$OPENAI_API_KEY

prompt_file="$1"
chunks_dir="$2"
annotations_dir="$3"

tmp_dir=$(mktemp --directory /tmp/openai.XXX)
trap 'rm -rf -- "$tmp_dir"' EXIT

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
        '{model: "gpt-3.5-turbo", temperature: 0, messages: [{role: "user", content: $content, response_format: {type: "json_object"}}]}'
}

send_request() {
    curl --silent "$url" \
        -H "Authorization: Bearer $key" \
        -H "Content-Type: application/json" \
        -d "$1"
}

ask_then_write() {
    echo "${2} en cours..."
    send_request "$(build_request $1 $2)" | \
        jq '.choices[0].message.content' -r \
        > $3/$(basename $2).json
    echo "${2} fait!"
}

remove_empty() {
    # supprimer les fichiers vides
    if test -d $annotations_dir; then
        empty=$(rg '[`\[\{]' "${annotations_dir}" --files-without-match)
        if [ "$empty" != "" ];then
            rm $empty
        fi
    else
        echo 'no annotations_dir'
    fi
}


max_num_processes=$(ulimit -u)
limiting_factor=4
num_processes=$((max_num_processes/limiting_factor))
# > this gets the max number of processes for the user
# > An arbitrary limiting factor so that there are some free processes
# > in case I want to run something else

while test 1; do
    # enlève les fichiers vides
    remove_empty
    read -p "il y a $(ls $annotations_dir | wc -l) fichiers annotés. continue?" answer

    # récupérer les fichiers qui ne sont pas annotés: soustraire les fichiers annotés aux chunks.
    a=$(comm -23 \
        <(ls $chunks_dir | sort) \
        <(ls $annotations_dir | sed 's/\.json//' | sort))
    n=$(echo -e "$a" | wc -l)
    if [ "$n" != 0 ];then

        # copier les fichiers à annoter dans le dossier temporaraire
        for x in ${a}; do
            cp ${chunks_dir}/${x} ${tmp_dir}/${x}
        done

        # multiprocessing: envoyer une requête par fichier
        for file in $tmp_dir/*; do
            ((i=i%num_processes)); ((i++==0)) && wait
            ask_then_write "$prompt_file" "$file" "$annotations_dir" &
        done
        sleep 120
    else
        echo 'tout les fichiers sont annotés!'
        exit
    fi
done
