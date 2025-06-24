#!/usr/bin/env bash

# gunicorn -w 4 ninja_kitchen_sink.wsgi:application -b :4000
# uvicorn --workers 4 --port 4001 --no-access-log ninja_kitchen_sink.asgi:application

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

for i in {1..3}; do
    echo "Running test $i"

    echo "[gunicorn] Django Rest Framework"
    run_ab http://127.0.0.1:4000/drf-api/polls/questions/1/

    echo "[gunicorn] Ninja"
    run_ab http://127.0.0.1:4000/ninja-api/polls/questions/1/

    echo "[gunicorn] Ninja async"
    run_ab http://127.0.0.1:4000/ninja-api/polls-async/questions/1/

    echo "[uvicorn] Django Rest Framework"
    run_ab http://127.0.0.1:4001/drf-api/polls/questions/1/

    echo "[uvicorn] Ninja"
    run_ab http://127.0.0.1:4001/ninja-api/polls/questions/1/

    echo "[uvicorn] Ninja async"
    run_ab http://127.0.0.1:4001/ninja-api/polls-async/questions/1/

    echo
done
