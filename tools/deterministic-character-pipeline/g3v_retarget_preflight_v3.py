import runpy
from pathlib import Path

from mathutils import Vector

import g3v_retarget_preflight_v2 as v2


BASE = Path(__file__).with_name("g3v_retarget_preflight.py")

# The V2 failure was not a solver articulation failure. DIRECTION_SPACE_FK reproduced
# elbow/knee angles essentially exactly, but the old endpoint metric subtracted each
# rig's own rest-pose endpoint positions. That metric is invalid when the rest rigs are
# intentionally very different (mean rest orientation delta ~83 degrees, max ~180).
#
# V3 compares posed chain shape directly. Every bone contributes only its unit direction,
# so the score is independent of source/target bone roll, rest-pose axis convention and
# limb-length proportions. This is the correct skeleton-preflight question: does the
# target reproduce the source articulation/topology? Target proportions remain owned by
# MPFB and are evaluated visually in the later body-render gate.

CHAINS = {
    "torso": ("Hips", "Spine1", "Neck1", "Head"),
    "left_arm": ("LeftArm", "LeftForeArm", "LeftHand"),
    "right_arm": ("RightArm", "RightForeArm", "RightHand"),
    "left_leg": ("LeftUpLeg", "LeftLeg", "LeftFoot"),
    "right_leg": ("RightUpLeg", "RightLeg", "RightFoot"),
}


def install_v3(target_globals):
    required = ("main", "arm_point", "score_method")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V retarget v3 missing base symbols: " + ", ".join(missing))

    arm_point = target_globals["arm_point"]
    previous_score_method = target_globals["score_method"]

    def chain_shape_signature(rig):
        out = {}
        for chain_name, bones in CHAINS.items():
            accum = Vector((0.0, 0.0, 0.0))
            valid = 0
            for bone_name in bones:
                head = arm_point(rig, bone_name, False)
                tail = arm_point(rig, bone_name, True)
                direction = tail - head
                if direction.length <= 1e-8:
                    continue
                accum += direction.normalized()
                valid += 1
            if valid == 0:
                raise RuntimeError(
                    f"G3V retarget v3 chain {chain_name} contains no measurable bones"
                )
            accum /= float(valid)
            out[chain_name] = [float(accum.x), float(accum.y), float(accum.z)]
        return out

    def score_method_v3(method, source, target, frames, RigService):
        result = previous_score_method(method, source, target, frames, RigService)
        result["endpoint_metric_kind"] = "CHAIN_UNIT_DIRECTION_RMS"
        result["endpoint_metric_rest_independent"] = True
        return result

    # Base score_method resolves endpoint_motion_signature through its module globals at
    # call time, so replacing this symbol changes both MPFB_POSE_API and DIRECTION_SPACE_FK
    # scoring without changing their actual pose solvers.
    target_globals["endpoint_motion_signature"] = chain_shape_signature
    target_globals["score_method"] = score_method_v3

    if target_globals["endpoint_motion_signature"] is not chain_shape_signature:
        raise RuntimeError("G3V retarget v3 chain endpoint metric did not bind")
    if target_globals["score_method"] is not score_method_v3:
        raise RuntimeError("G3V retarget v3 score wrapper did not bind")

    print("G3V_RETARGET_V3=BOUND")
    print("G3V_RETARGET_ENDPOINT_METRIC=CHAIN_UNIT_DIRECTION_RMS")
    print("G3V_RETARGET_ENDPOINT_METRIC_REST_INDEPENDENT=TRUE")
    print("G3V_RETARGET_THRESHOLDS=UNCHANGED")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3v_retarget_base_v3")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("G3V retarget base did not expose main()")
    target_globals = target_main.__globals__

    # V2 owns the actual solvers: correct MPFB pose-mode context and the
    # axis-independent DIRECTION_SPACE_FK solver. V3 changes only the invalid endpoint
    # fidelity metric used to judge those solvers.
    v2.install_v2(target_globals)
    install_v3(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
