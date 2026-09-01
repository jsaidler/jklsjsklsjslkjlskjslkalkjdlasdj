class_name SimulationLod
extends RefCounted

const DETAILED := "detailed"
const REGIONAL := "regional"

static func is_valid(value: String) -> bool:
    return value == DETAILED or value == REGIONAL

static func interval_days(value: String) -> int:
    match value:
        DETAILED:
            return 1
        REGIONAL:
            return 2
        _:
            return 1
