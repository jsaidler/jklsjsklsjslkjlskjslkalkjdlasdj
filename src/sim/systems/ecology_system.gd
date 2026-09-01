class_name EcologySystem
extends RefCounted

func tick(world: WorldState, streams: SeedStreams) -> void:
    var ecology: Dictionary = world.regions["salt_road_vale"]["ecology"]
    var predator: Dictionary = world.species["ash_hyena"]
    var prey := float(ecology["prey_level"])
    var carrying := float(ecology["prey_carrying_capacity"])
    var pack_size := float(predator["pack_size"])
    prey += maxf(0.0, (carrying - prey) * 0.035)
    prey -= pack_size * 0.065
    ecology["prey_level"] = clampf(prey, 0.0, carrying)
    var food_pressure := 1.0 - float(ecology["prey_level"]) / maxf(carrying, 1.0)
    predator["hunger"] = clampf(float(predator["hunger"]) + 0.025 + food_pressure * 0.05, 0.0, 1.0)

func predator_attack_utility(world: WorldState, caravan: Dictionary) -> Dictionary:
    var predator: Dictionary = world.species["ash_hyena"]
    var route: Dictionary = world.routes[caravan["route_id"]]
    var hunger := float(predator["hunger"])
    var overlap := float(route["predator_territory_overlap"])
    var weakness := clampf((7.0 - float(caravan["guard_strength"])) / 7.0, 0.0, 1.0)
    var total := hunger * 0.52 + overlap * 0.30 + weakness * 0.18
    return {"hunger": hunger * 0.52, "territory_overlap": overlap * 0.30, "target_weakness": weakness * 0.18, "total": total}

func resolve_predator_attack(world: WorldState, caravan: Dictionary, streams: SeedStreams) -> Dictionary:
    var predator: Dictionary = world.species["ash_hyena"]
    var rng := streams.get_rng("ecology_combat")
    var pack_power := float(predator["pack_size"]) * (0.75 + float(predator["hunger"]) * 0.35)
    var guard_power := float(caravan["guard_strength"]) * 1.25
    var pressure := pack_power / maxf(pack_power + guard_power, 0.001)
    var guard_loss := 0
    if rng.randf() < pressure:
        guard_loss = 1
        caravan["guard_strength"] = maxf(0.0, float(caravan["guard_strength"]) - 1.0)
    predator["hunger"] = maxf(0.0, float(predator["hunger"]) - 0.22)
    return {"guard_loss": guard_loss, "pressure": pressure}
