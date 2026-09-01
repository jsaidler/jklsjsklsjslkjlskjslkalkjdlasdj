class_name SimulationScheduler
extends RefCounted

const SimulationLodScript = preload("res://src/sim/simulation_lod.gd")

func ensure(entity: Dictionary, world_day: int, default_lod: String = SimulationLodScript.REGIONAL) -> void:
    if not entity.has("simulation_lod"):
        entity["simulation_lod"] = default_lod
    if not entity.has("last_simulation_day"):
        entity["last_simulation_day"] = world_day
    if not entity.has("next_simulation_day"):
        entity["next_simulation_day"] = world_day

func is_due(entity: Dictionary, world_day: int) -> bool:
    ensure(entity, world_day)
    return world_day >= int(entity["next_simulation_day"])

func elapsed_days(entity: Dictionary, world_day: int) -> int:
    ensure(entity, world_day)
    return maxi(1, world_day - int(entity["last_simulation_day"]))

func mark_simulated(entity: Dictionary, world_day: int, max_interval_days: int = -1) -> void:
    ensure(entity, world_day)
    entity["last_simulation_day"] = world_day
    var lod := String(entity["simulation_lod"])
    var interval := SimulationLodScript.interval_days(lod)
    if max_interval_days > 0:
        interval = mini(interval, max_interval_days)
    entity["next_simulation_day"] = world_day + maxi(interval, 1)

func set_lod(world: WorldState, entity_type: String, entity_id: String, entity: Dictionary, lod: String, preserved_state: Dictionary = {}) -> bool:
    if not SimulationLodScript.is_valid(lod):
        return false
    ensure(entity, world.day)
    var previous := String(entity["simulation_lod"])
    if previous == lod:
        return true
    entity["simulation_lod"] = lod
    entity["next_simulation_day"] = world.day
    world.record_event("simulation_lod_changed", {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "from": previous,
        "to": lod,
        "preserved_state": preserved_state.duplicate(true),
    })
    return true
