#!/usr/bin/env bash

# gunicorn -w 4 ninja_kitchen_sink.wsgi:application -b :4000

run_ab() {
    ab \
        -c 100 \
        -t 5 \
        -H "Accept: application/json" \
        "$1" \
        2>/dev/null |
        grep "Complete requests:"
    echo
}

for i in {1..5}; do
    echo "Running test $i"

    echo "Django Rest Framework"
    run_ab http://127.0.0.1:4000/drf-api/polls/questions/1/

    echo "Ninja"
    run_ab http://127.0.0.1:4000/ninja-api/polls/questions/1/

    echo
done
