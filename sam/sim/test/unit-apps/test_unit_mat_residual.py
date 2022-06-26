import pytest
import time
import scipy.sparse
from sam.sim.src.rd_scanner import UncompressCrdRdScan, CompressedCrdRdScan
from sam.sim.src.wr_scanner import ValsWrScan
from sam.sim.src.joiner import Intersect2, Union2
from sam.sim.src.compute import Multiply2, Add2
from sam.sim.src.crd_manager import CrdDrop, CrdHold
from sam.sim.src.repeater import Repeat, RepeatSigGen
from sam.sim.src.accumulator import Reduce
from sam.sim.src.accumulator import SparseAccumulator1, SparseAccumulator2
from sam.sim.src.token import *
from sam.sim.test.test import *
from sam.sim.test.gold import *
import os
import csv

cwd = os.getcwd()
formatted_dir = os.getenv('SUITESPARSE_FORMATTED_PATH', default=os.path.join(cwd, 'mode-formats'))
other_dir = os.getenv('OTHER_FORMATTED_PATH', default=os.path.join(cwd, 'mode-formats'))


arr_dict1 = {"vi_seg": [0, 2],
             "vi_crd": [1, 2],
             "vi_vals": [1, 2],
             "vj_seg": [0, 1],
             "vj_crd": [1],
             "vj_vals": [5],
             "mi_seg": [0, 2],
             "mi_crd": [0, 2],
             "mj_seg": [0, 1, 2],
             "mj_crd": [1, 1],
             "m_vals": [3, 4],
             "gold_seg": [0, 3],
             "gold_crd": [0, 1, 2],
             "gold_vals": [-15, 1, -18]}

@pytest.mark.parametrize("arrs", [arr_dict1])
def test_unit_mat_residual(samBench, arrs, check_gold, debug_sim, fill=0):
    C_shape = (3, 3)

    C_seg0 = copy.deepcopy(arrs["mi_seg"])
    C_crd0 = copy.deepcopy(arrs["mi_crd"])
    C_seg1 = copy.deepcopy(arrs["mj_seg"])
    C_crd1 = copy.deepcopy(arrs["mj_crd"])
    C_vals = copy.deepcopy(arrs["m_vals"])

    b_shape = [C_shape[0]]
    b_seg0 = copy.deepcopy(arrs["vi_seg"])
    b_crd0 = copy.deepcopy(arrs["vi_crd"])
    b_vals = copy.deepcopy(arrs["vi_vals"])

    d_shape = [C_shape[1]]
    d_seg0 = copy.deepcopy(arrs["vj_seg"])
    d_crd0 = copy.deepcopy(arrs["vj_crd"])
    d_vals = copy.deepcopy(arrs["vj_vals"])

    gold_seg = copy.deepcopy(arrs["gold_seg"])
    gold_crd = copy.deepcopy(arrs["gold_crd"])
    gold_vals = copy.deepcopy(arrs["gold_vals"])

    fiberlookup_bi_17 = CompressedCrdRdScan(crd_arr=b_crd0, seg_arr=b_seg0, debug=debug_sim)
    fiberlookup_Ci_18 = CompressedCrdRdScan(crd_arr=C_crd0, seg_arr=C_seg0, debug=debug_sim)
    unioni_16 = Union2(debug=debug_sim)
    fiberlookup_Cj_11 = CompressedCrdRdScan(crd_arr=C_crd1, seg_arr=C_seg1, debug=debug_sim)
    fiberwrite_x0_1 = CompressWrScan(seg_size=2, size=b_shape[0], fill=fill, debug=debug_sim)
    repsiggen_i_14 = RepeatSigGen(debug=debug_sim)
    repeat_di_13 = Repeat(debug=debug_sim)
    fiberlookup_dj_12 = CompressedCrdRdScan(crd_arr=d_crd0, seg_arr=d_seg0, debug=debug_sim)
    intersectj_10 = Intersect2(debug=debug_sim)
    repsiggen_j_9 = RepeatSigGen(debug=debug_sim)
    arrayvals_C_6 = Array(init_arr=C_vals, debug=debug_sim)
    arrayvals_d_7 = Array(init_arr=d_vals, debug=debug_sim)
    repeat_bj_8 = Repeat(debug=debug_sim)
    mul_5 = Multiply2(debug=debug_sim)
    arrayvals_b_4 = Array(init_arr=b_vals, debug=debug_sim)
    add_3 = Add2(debug=debug_sim, neg2=True)
    reduce_2 = Reduce(debug=debug_sim)
    fiberwrite_xvals_0 = ValsWrScan(size=1 * b_shape[0], fill=fill, debug=debug_sim)
    in_ref_b = [0, 'D']
    in_ref_C = [0, 'D']
    in_ref_d = [0, 'D']
    done = False
    time_cnt = 0

    temp = []
    temp1 = []
    temp2 = []
    temp3 = []
    while not done and time_cnt < TIMEOUT:
        if len(in_ref_b) > 0:
            fiberlookup_bi_17.set_in_ref(in_ref_b.pop(0))
        fiberlookup_bi_17.update()

        if len(in_ref_C) > 0:
            fiberlookup_Ci_18.set_in_ref(in_ref_C.pop(0))
        fiberlookup_Ci_18.update()

        unioni_16.set_in1(fiberlookup_bi_17.out_ref(), fiberlookup_bi_17.out_crd())
        unioni_16.set_in2(fiberlookup_Ci_18.out_ref(), fiberlookup_Ci_18.out_crd())
        unioni_16.update()

        fiberlookup_Cj_11.set_in_ref(unioni_16.out_ref2())
        fiberlookup_Cj_11.update()

        fiberwrite_x0_1.set_input(unioni_16.out_crd())
        fiberwrite_x0_1.update()

        repsiggen_i_14.set_istream(unioni_16.out_crd())
        repsiggen_i_14.update()

        if len(in_ref_d) > 0:
            repeat_di_13.set_in_ref(in_ref_d.pop(0))
        repeat_di_13.set_in_repsig(repsiggen_i_14.out_repsig())
        repeat_di_13.update()

        fiberlookup_dj_12.set_in_ref(repeat_di_13.out_ref())
        fiberlookup_dj_12.update()

        temp.append(fiberlookup_Cj_11.out_crd())
        temp1.append(fiberlookup_dj_12.out_crd())
        temp2.append(fiberlookup_Cj_11.out_ref())
        temp3.append(fiberlookup_dj_12.out_ref())
        print(remove_emptystr(temp))
        print(remove_emptystr(temp1))
        print(remove_emptystr(temp2))
        print(remove_emptystr(temp3))
        intersectj_10.set_in1(fiberlookup_dj_12.out_ref(), fiberlookup_dj_12.out_crd())
        intersectj_10.set_in2(fiberlookup_Cj_11.out_ref(), fiberlookup_Cj_11.out_crd())
        intersectj_10.update()

        repsiggen_j_9.set_istream(intersectj_10.out_crd())
        repsiggen_j_9.update()

        arrayvals_C_6.set_load(intersectj_10.out_ref2())
        arrayvals_C_6.update()

        arrayvals_d_7.set_load(intersectj_10.out_ref1())
        arrayvals_d_7.update()

        repeat_bj_8.set_in_ref(unioni_16.out_ref1())
        repeat_bj_8.set_in_repsig(repsiggen_j_9.out_repsig())
        repeat_bj_8.update()

        arrayvals_b_4.set_load(repeat_bj_8.out_ref())
        arrayvals_b_4.update()

        mul_5.set_in1(arrayvals_C_6.out_val())
        mul_5.set_in2(arrayvals_d_7.out_val())
        mul_5.update()

        add_3.set_in1(arrayvals_b_4.out_val())
        add_3.set_in2(mul_5.out_val())
        add_3.update()

        reduce_2.set_in_val(add_3.out_val())
        reduce_2.update()

        fiberwrite_xvals_0.set_input(reduce_2.out_val())
        fiberwrite_xvals_0.update()

        done = fiberwrite_x0_1.out_done() and fiberwrite_xvals_0.out_done()
        time_cnt += 1

    fiberwrite_x0_1.autosize()
    fiberwrite_xvals_0.autosize()

    out_crds = [fiberwrite_x0_1.get_arr()]
    out_segs = [fiberwrite_x0_1.get_seg_arr()]
    out_vals = fiberwrite_xvals_0.get_arr()

    assert out_crds[0] == gold_crd
    assert out_segs[0] == gold_seg
    assert out_vals == gold_vals
