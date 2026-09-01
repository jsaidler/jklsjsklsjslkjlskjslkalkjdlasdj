class_name WorldSerializer
extends RefCounted

const SCHEMA_VERSION := 1
const GENERATOR_VERSION := "kernel_0a"

static func to_snapshot(world: WorldState) -> Dictionary:
    return {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "world": {
            "seed": world.seed,
            "day": world.day,
            "cultures": world.cultures.duplicate(true),
            "factions": world.factions.duplicate(true),
            "settlements": world.settlements.duplicate(true),
            "regions": world.regions.duplicate(true),
            "routes": world.routes.duplicate(true),
            "species": world.species.duplicate(true),
            "agents": world.agents.duplicate(true),
            "caravans": world.caravans.duplicate(true),
            "trade_requests": world.trade_requests.duplicate(true),
            "events": world.events.duplicate(true),
            "faction_knowledge": world.faction_knowledge.duplicate(true),
            "agent_knowledge": world.agent_knowledge.duplicate(true),
            "scheduled_knowledge": world.scheduled_knowledge.duplicate(true),
            "decision_log": world.decision_log.duplicate(true),
            "rng_states": world.rng_states.duplicate(true),
            "counters": world.export_counters(),
        },
    }

static func from_snapshot(snapshot: Dictionary) -> WorldState:
    if int(snapshot.get("schema_version", -1)) != SCHEMA_VERSION:
        push_error("Unsupported world save schema version: %s" % str(snapshot.get("schema_version", "missing")))
        return null
    if not snapshot.has("world") or typeof(snapshot["world"]) != TYPE_DICTIONARY:
        push_error("Invalid world save: missing world payload")
        return null

    var data: Dictionary = snapshot["world"]
    var world := WorldState.new(int(data["seed"]))
    world.day = int(data["day"])
    world.cultures = (data["cultures"] as Dictionary).duplicate(true)
    world.factions = (data["factions"] as Dictionary).duplicate(true)
    world.settlements = (data["settlements"] as Dictionary).duplicate(true)
    world.regions = (data["regions"] as Dictionary).duplicate(true)
    world.routes = (data["routes"] as Dictionary).duplicate(true)
    world.species = (data["species"] as Dictionary).duplicate(true)
    world.agents = (data["agents"] as Dictionary).duplicate(true)
    world.caravans = (data["caravans"] as Dictionary).duplicate(true)
    world.trade_requests = (data["trade_requests"] as Array).duplicate(true)
    world.events = (data["events"] as Array).duplicate(true)
    world.faction_knowledge = (data["faction_knowledge"] as Dictionary).duplicate(true)
    world.agent_knowledge = (data["agent_knowledge"] as Dictionary).duplicate(true)
    world.scheduled_knowledge = (data["scheduled_knowledge"] as Array).duplicate(true)
    world.decision_log = (data["decision_log"] as Array).duplicate(true)
    world.rng_states = (data["rng_states"] as Dictionary).duplicate(true)
    world.import_counters(data.get("counters", {}))
    return world

static func save_world(path: String, world: WorldState) -> Error:
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        return FileAccess.get_open_error()
    file.store_var(to_snapshot(world), false)
    return OK

static func load_world(path: String) -> WorldState:
    if not FileAccess.file_exists(path):
        return null
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return null
    var value = file.get_var(false)
    if typeof(value) != TYPE_DICTIONARY:
        push_error("Invalid world save payload")
        return null
    return from_snapshot(value)
