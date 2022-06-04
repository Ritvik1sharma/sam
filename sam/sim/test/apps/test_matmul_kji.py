import pytest
import time
import scipy.sparse
from sam.sim.src.rd_scanner import UncompressCrdRdScan, CompressedCrdRdScan
from sam.sim.src.wr_scanner import ValsWrScan
from sam.sim.src.joiner import Intersect2
from sam.sim.src.compute import Multiply2
from sam.sim.src.crd_manager import CrdDrop
from sam.sim.src.repeater import Repeat, RepeatSigGen
from sam.sim.src.accumulator import Reduce
from sam.sim.src.accumulator import SparseAccumulator1, SparseAccumulator2
from sam.sim.src.token import *
from sam.sim.test.test import *
import os
import csv
cwd = os.getcwd()
formatted_dir = os.getenv('SUITESPARSE_FORMATTED_PATH', default=os.path.join(cwd, 'mode-formats'))


# FIXME: Figureout formats
@pytest.mark.skipif(
    os.getenv('CI', 'false') == 'true',
    reason='CI lacks datasets',
)
def test_matmul_kji(samBench, ssname, debug_sim, fill=0):
    B_dirname = os.path.join(formatted_dir, ssname, "orig", "ss10")
    B_shape_filename = os.path.join(B_dirname, "B_shape.txt")
    B_shape = read_inputs(B_shape_filename)

    B0_seg_filename = os.path.join(B_dirname, "B0_seg.txt")
    B_seg0 = read_inputs(B0_seg_filename)
    B0_crd_filename = os.path.join(B_dirname, "B0_crd.txt")
    B_crd0 = read_inputs(B0_crd_filename)

    B1_seg_filename = os.path.join(B_dirname, "B1_seg.txt")
    B_seg1 = read_inputs(B1_seg_filename)
    B1_crd_filename = os.path.join(B_dirname, "B1_crd.txt")
    B_crd1 = read_inputs(B1_crd_filename)

    B_vals_filename = os.path.join(B_dirname, "B_vals.txt")
    B_vals = read_inputs(B_vals_filename, float)

    C_dirname = os.path.join(formatted_dir, ssname, "shift-trans", "ss01")
    C_shape_filename = os.path.join(C_dirname, "C_shape.txt")
    C_shape = read_inputs(C_shape_filename)

    C0_seg_filename = os.path.join(C_dirname, "C0_seg.txt")
    C_seg0 = read_inputs(C0_seg_filename)
    C0_crd_filename = os.path.join(C_dirname, "C0_crd.txt")
    C_crd0 = read_inputs(C0_crd_filename)

    C1_seg_filename = os.path.join(C_dirname, "C1_seg.txt")
    C_seg1 = read_inputs(C1_seg_filename)
    C1_crd_filename = os.path.join(C_dirname, "C1_crd.txt")
    C_crd1 = read_inputs(C1_crd_filename)

    C_vals_filename = os.path.join(C_dirname, "C_vals.txt")
    C_vals = read_inputs(C_vals_filename, float)

    fiberlookup_Bk_16 = CompressedCrdRdScan(crd_arr=B_crd1, seg_arr=B_seg1, debug=debug_sim)
    fiberlookup_Ck_17 = CompressedCrdRdScan(crd_arr=C_crd0, seg_arr=C_seg0, debug=debug_sim)
    intersectk_15 = Intersect2(debug=debug_sim)
    fiberlookup_Cj_14 = CompressedCrdRdScan(crd_arr=C_crd1, seg_arr=C_seg1, debug=debug_sim)
    repsiggen_j_12 = RepeatSigGen(debug=debug_sim)
    repeat_Bj_11 = Repeat(debug=debug_sim)
    fiberlookup_Bi_10 = CompressedCrdRdScan(crd_arr=B_crd0, seg_arr=B_seg0, debug=debug_sim)
    arrayvals_B_5 = Array(init_arr=B_vals, debug=debug_sim)
    repsiggen_i_8 = RepeatSigGen(debug=debug_sim)
    repeat_Ci_7 = Repeat(debug=debug_sim)
    arrayvals_C_6 = Array(init_arr=C_vals, debug=debug_sim)
    mul_4 = Multiply2(debug=debug_sim)
    spaccumulator2_3 = SparseAccumulator2(debug=debug_sim)
    spaccumulator2_3_drop_crd_in_0 = StknDrop(debug=debug_sim)
    spaccumulator2_3_drop_crd_in_1 = StknDrop(debug=debug_sim)
    spaccumulator2_3_drop_crd_in_2 = StknDrop(debug=debug_sim)
    spaccumulator2_3_drop_val = StknDrop(debug=debug_sim)
    fiberwrite_Xvals_0 = ValsWrScan(size=1 * C_shape[1] * B_shape[0], fill=fill, debug=debug_sim)
    fiberwrite_X0_1 = CompressWrScan(seg_size=C_shape[1] + 1, size=C_shape[1] * B_shape[0], fill=fill, debug=debug_sim)
    fiberwrite_X1_2 = CompressWrScan(seg_size=2, size=C_shape[1], fill=fill, debug=debug_sim)
    in_ref_B = [0, 'D']
    in_ref_C = [0, 'D']
    done = False
    time_cnt = 0

    while not done and time_cnt < TIMEOUT:
        if len(in_ref_B) > 0:
            fiberlookup_Bk_16.set_in_ref(in_ref_B.pop(0))
        fiberlookup_Bk_16.update()

        if len(in_ref_C) > 0:
            fiberlookup_Ck_17.set_in_ref(in_ref_C.pop(0))
        fiberlookup_Ck_17.update()

        intersectk_15.set_in1(fiberlookup_Bk_16.out_ref(), fiberlookup_Bk_16.out_crd())
        intersectk_15.set_in2(fiberlookup_Ck_17.out_ref(), fiberlookup_Ck_17.out_crd())
        intersectk_15.update()

        fiberlookup_Cj_14.set_in_ref(intersectk_15.out_ref2())
        fiberlookup_Cj_14.update()

        repsiggen_j_12.set_istream(fiberlookup_Cj_14.out_crd())
        repsiggen_j_12.update()

        repeat_Bj_11.set_in_ref(intersectk_15.out_ref1())
        repeat_Bj_11.set_in_repsig(repsiggen_j_12.out_repsig())
        repeat_Bj_11.update()

        fiberlookup_Bi_10.set_in_ref(repeat_Bj_11.out_ref())
        fiberlookup_Bi_10.update()

        arrayvals_B_5.set_load(fiberlookup_Bi_10.out_ref())
        arrayvals_B_5.update()

        repsiggen_i_8.set_istream(fiberlookup_Bi_10.out_crd())
        repsiggen_i_8.update()

        repeat_Ci_7.set_in_repsig(repsiggen_i_8.out_repsig())
        repeat_Ci_7.set_in_ref(fiberlookup_Cj_14.out_ref())
        repeat_Ci_7.update()

        arrayvals_C_6.set_load(repeat_Ci_7.out_ref())
        arrayvals_C_6.update()

        mul_4.set_in1(arrayvals_C_6.out_load())
        mul_4.set_in2(arrayvals_B_5.out_load())
        mul_4.update()

        spaccumulator2_3_drop_crd_in_2.set_in_stream(intersectk_15.out_crd())
        spaccumulator2_3_drop_crd_in_0.set_in_stream(fiberlookup_Bi_10.out_crd())
        spaccumulator2_3_drop_val.set_in_stream(mul_4.out_val())
        spaccumulator2_3_drop_crd_in_1.set_in_stream(fiberlookup_Cj_14.out_crd())
        spaccumulator2_3.crd_in_2(spaccumulator2_3_drop_crd_in_2.out_val())
        spaccumulator2_3.crd_in_0(spaccumulator2_3_drop_crd_in_0.out_val())
        spaccumulator2_3.set_val(spaccumulator2_3_drop_val.out_val())
        spaccumulator2_3.crd_in_1(spaccumulator2_3_drop_crd_in_1.out_val())
        spaccumulator2_3.update()

        fiberwrite_Xvals_0.set_input(spaccumulator2_3.out_val())
        fiberwrite_Xvals_0.update()

        fiberwrite_X0_1.set_input(spaccumulator2_3.out_crd_0())
        fiberwrite_X0_1.update()

        fiberwrite_X1_2.set_input(spaccumulator2_3.out_crd_1())
        fiberwrite_X1_2.update()

        done = fiberwrite_Xvals_0.out_done() and fiberwrite_X0_1.out_done() and fiberwrite_X1_2.out_done()
        time_cnt += 1

    fiberwrite_Xvals_0.autosize()
    fiberwrite_X0_1.autosize()
    fiberwrite_X1_2.autosize()

    out_crds = [fiberwrite_X0_1.get_arr(), fiberwrite_X1_2.get_arr()]
    out_segs = [fiberwrite_X0_1.get_seg_arr(), fiberwrite_X1_2.get_seg_arr()]
    out_vals = fiberwrite_Xvals_0.get_arr()
    def bench():
        time.sleep(0.01)

    extra_info = dict()
    extra_info["dataset"] = ssname
    extra_info["cycles"] = time_cnt
    extra_info["tensor_B_shape"] = B_shape
    extra_info["tensor_C_shape"] = C_shape
    sample_dict = intersectk_15.return_statistics()
    for k in sample_dict.keys():
        extra_info["intersectk_15" + "_" + k] =  sample_dict[k]

    sample_dict = spaccumulator2_3.return_statistics()
    for k in sample_dict.keys():
        extra_info["spaccumulator2_3" + "_" + k] =  sample_dict[k]

    sample_dict = fiberwrite_Xvals_0.return_statistics()
    for k in sample_dict.keys():
        extra_info["fiberwrite_Xvals_0" + "_" + k] =  sample_dict[k]

    sample_dict = fiberwrite_X0_1.return_statistics()
    for k in sample_dict.keys():
        extra_info["fiberwrite_X0_1" + "_" + k] =  sample_dict[k]

    sample_dict = fiberwrite_X1_2.return_statistics()
    for k in sample_dict.keys():
        extra_info["fiberwrite_X1_2" + "_" + k] =  sample_dict[k]

    sample_dict = repeat_Bj_11.return_statistics()
    for k in sample_dict.keys():
        extra_info["repeat_Bj_11" + "_" + k] =  sample_dict[k]

    sample_dict = repeat_Ci_7.return_statistics()
    for k in sample_dict.keys():
        extra_info["repeat_Ci_7" + "_" + k] =  sample_dict[k]

    sample_dict = arrayvals_C_6.return_statistics()
    for k in sample_dict.keys():
        extra_info["arrayvals_C_6" + "_" + k] =  sample_dict[k]

    sample_dict = arrayvals_B_5.return_statistics()
    for k in sample_dict.keys():
        extra_info["arrayvals_B_5" + "_" + k] =  sample_dict[k]

    samBench(bench, extra_info)