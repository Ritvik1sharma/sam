#!/bin/bash
#SBATCH -N 1
#SBATCH -t 360

# Vars
if [ -z "$2" ]
then
    export SYNTHETIC_PATH="$(pwd)/synthetic/"
else
    export SYNTHETIC_PATH="$2"
fi

BENCHMARKS=(
  test_vec_elemmul_bittree
  test_vec_elemmul_bitvector
  test_vec_elemmul_compress_skip
  test_vec_elemmul_compress_split
  test_vec_elemmul_compressed
  test_vec_elemmul_uncompressed
)

cwd=$(pwd)
resultdir=results

for b in ${!BENCHMARKS[@]}; do
    bench=${BENCHMARKS[$b]}
    path=$resultdir/

    mkdir -p $resultdir/
    echo "Testing $bench..."

    pytest sam/sim/test/study-apps/$bench.py --synth -k "random-40 or 0.2-blocks or 0.2-runs" --benchmark-json="$path/$bench.json"
    python $cwd/scripts/converter.py --json_name $path/$bench.json
    python $cwd/scripts/bench_csv_aggregator.py $path $cwd/SYNTH_OUT.csv

done

BENCHMARKS=(
    test_matmul_ijk
    test_matmul_ikj
    test_matmul_jik
    test_matmul_jki
    test_matmul_kij
    test_matmul_kji
)

cwd=$(pwd)
resultdir=results_mats

for b in ${!BENCHMARKS[@]}; do
    bench=${BENCHMARKS[$b]}
    path=$resultdir/

    mkdir -p $resultdir/
    echo "Testing $bench..."

    pytest sam/sim/test/reorder-study/$bench.py --synth --check-gold --benchmark-json="$path/$bench.json"
    python $cwd/scripts/converter.py --json_name $path/$bench.json
    python $cwd/scripts/bench_csv_aggregator.py $path $cwd/SYNTH_OUT_MAT.csv

done

# echo -e "${RED}Failed tests:"
# for i in ${!errors[@]}; do
#     error=${errors[$i]} 
#     echo -e "${RED}$error,"
# done
# echo -e "${NC}"
