#!/bin/bash

rundetached() {
  name=$1
  shift
  screen -dmS "$name" sh -c '"$@" | tee $0;read -p Done.;exec bash' "$@"
}

for file in ./testfiles/*;
do
   filename="${file##*/}"
   p=${filename%%.*}
   for sched in {1..4};
   do
     rundetached "sudoku-${filename}-S${sched}" "results/S${sched}/${filename}" python ./tests.py -s $p -S "$sched" -H "$file"
   done
   rundetached "sudoku-${filename}-S0.0.0" "results/S0.0.0/${filename}" python ./tests.py -s $p -S 0 --setformula --noskip -H "$file"
   rundetached "sudoku-${filename}-S0.0.1" "results/S0.0.1/${filename}" python ./tests.py -s $p -S 0 --setformula --skip -H "$file"
   rundetached "sudoku-${filename}-S0.1.0" "results/S0.1.0/${filename}" python ./tests.py -s $p -S 0 --nosetformula --noskip -H "$file"
   rundetached "sudoku-${filename}-S0.1.1" "results/S0.1.1/${filename}" python ./tests.py -s $p -S 0 --nosetformula --skip -H "$file"
done
