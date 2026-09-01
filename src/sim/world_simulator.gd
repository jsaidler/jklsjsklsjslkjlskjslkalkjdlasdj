class_name WorldSimulator
extends RefCounted

const KnowledgeSystemScript = preload("res://src/sim/systems/knowledge_system.gd")
const EcologySystemScript = preload("res://src/sim/systems/ecology_system.gd")
const EconomySystemScript = preload("res://src/sim/systems/economy_system.gd")
const FactionSystemScript = preload("res://src/sim/systems/faction_system.gd")
const CaravanSystemScript = preload("res://src/sim/systems/caravan_system.gd")

var world: WorldState
var streams: SeedStreams
var knowledge := KnowledgeSystemScript.new()
var ecology := EcologySystemScript.new()
var economy := EconomySystemScript.new()
var factions := FactionSystemScript.new()
var caravans := CaravanSystemScript.new()

func _init(world_state: WorldState) -> void:
    world = world_state
    streams = SeedStreams.new(world.seed)
    if not world.rng_states.is_empty():
        streams.import_states(world.rng_states)

func step_day() -> void:
    world.day += 1
    knowledge.tick(world)
    ecology.tick(world, streams)
    economy.tick(world)
    factions.tick(world)
    caravans.tick(world, streams, ecology, factions)
    world.rng_states = streams.export_states()

func run_days(days: int) -> void:
    for _i in range(max(days, 0)):
        step_day()

func set_caravan_lod(caravan_id: String, lod: String) -> bool:
    return caravans.set_lod(world, caravan_id, lod)
