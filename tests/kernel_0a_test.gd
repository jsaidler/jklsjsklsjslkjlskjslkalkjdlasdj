extends SceneTree

const WorldFactoryScript = preload("res://src/sim/world_factory.gd")
const WorldSimulatorScript = preload("res://src/sim/world_simulator.gd")
const WorldSerializerScript = preload("res://src/sim/world_serializer.gd")
const WorldInspectorScript = preload("res://src/sim/debug/world_inspector.gd")
const SimulationLodScript = preload("res://src/sim/simulation_lod.gd")
var failures: Array[String] = []

func _initialize() -> void:
    _test_determinism()
    _test_seed_divergence()
    _test_causal_trade_and_threat_loop()
    _test_save_reload_roundtrip()
    _test_individual_knowledge_precedes_remote_faction_knowledge()
    _test_lod_transition_preserves_entity_state()
    _finish()

func _simulate(seed_value: int, days: int = 120) -> WorldState:
    var world := WorldFactoryScript.create_kernel_0a(seed_value)
    var sim := WorldSimulatorScript.new(world)
    sim.run_days(days)
    return world

func _test_determinism() -> void:
    var first := _simulate(190512)
    var second := _simulate(190512)
    _expect(WorldInspectorScript.signature(first) == WorldInspectorScript.signature(second), "same seed must reproduce identical world history")

func _test_seed_divergence() -> void:
    var first := _simulate(190512)
    var second := _simulate(190513)
    _expect(WorldInspectorScript.signature(first) != WorldInspectorScript.signature(second), "different seeds must produce different histories")

func _test_causal_trade_and_threat_loop() -> void:
    var world := _simulate(190512)
    _expect(WorldInspectorScript.event_count(world, "trade_requested") > 0, "salt shortage must cause trade requests")
    _expect(WorldInspectorScript.event_count(world, "caravan_departed") > 0, "trade requests must cause caravans")
    _expect(WorldInspectorScript.event_count(world, "bandit_attack") > 0, "resource need + opportunity must eventually cause a bandit attack")
    var attack := WorldInspectorScript.first_event(world, "bandit_attack")
    _expect(not attack.is_empty(), "bandit attack event must exist")
    if not attack.is_empty():
        var delivery := WorldInspectorScript.first_knowledge_delivery_for(world, "asha_council", int(attack["id"]))
        _expect(not delivery.is_empty(), "Asha must eventually learn about the attack")
        if not delivery.is_empty():
            _expect(int(delivery["day"]) > int(attack["day"]), "information must travel; Asha cannot know the attack instantly")
    var decision := WorldInspectorScript.last_decision(world, "red_knives", "bandit_caravan_response")
    _expect(not decision.is_empty(), "bandit behavior must leave an auditable decision record")
    if not decision.is_empty():
        _expect((decision["scores"] as Dictionary).has("salt_need"), "decision explanation must expose causal factors")
    _expect(float(world.factions["road_wardens"]["escort_bonus"]) > 0.0, "road wardens must adapt after learning about attacks")

func _test_save_reload_roundtrip() -> void:
    var continuous := _simulate(190512, 120)
    var split := WorldFactoryScript.create_kernel_0a(190512)
    var first_half := WorldSimulatorScript.new(split)
    first_half.run_days(60)
    var path := "user://kernel_0a_roundtrip.save"
    var save_error := WorldSerializerScript.save_world(path, split)
    _expect(save_error == OK, "world save must succeed")
    if save_error != OK:
        return
    var loaded := WorldSerializerScript.load_world(path)
    _expect(loaded != null, "saved world must reload")
    if loaded == null:
        return
    var second_half := WorldSimulatorScript.new(loaded)
    second_half.run_days(60)
    _expect(WorldInspectorScript.signature(continuous) == WorldInspectorScript.signature(loaded), "60 days + save/reload + 60 days must equal 120 continuous days")
    if FileAccess.file_exists(path):
        DirAccess.remove_absolute(ProjectSettings.globalize_path(path))

func _test_individual_knowledge_precedes_remote_faction_knowledge() -> void:
    var world := _simulate(190512, 40)
    var attack := WorldInspectorScript.first_event(world, "bandit_attack")
    _expect(not attack.is_empty(), "knowledge test requires a bandit attack")
    if attack.is_empty():
        return
    var witness := WorldInspectorScript.first_knowledge_delivery_for(world, "road_scout", int(attack["id"]))
    var asha := WorldInspectorScript.first_knowledge_delivery_for(world, "asha_council", int(attack["id"]))
    _expect(not witness.is_empty(), "direct witness must acquire knowledge")
    _expect(not asha.is_empty(), "remote faction must eventually acquire knowledge")
    if not witness.is_empty():
        _expect(int(witness["day"]) == int(attack["day"]), "direct witness knowledge should be immediate")
    if not witness.is_empty() and not asha.is_empty():
        _expect(int(witness["day"]) < int(asha["day"]), "witness must know before remote Asha council")

func _test_lod_transition_preserves_entity_state() -> void:
    var world := WorldFactoryScript.create_kernel_0a(190512)
    var sim := WorldSimulatorScript.new(world)
    var caravan_id := ""
    for _day in range(20):
        sim.step_day()
        for candidate_id in world.caravans.keys():
            var candidate: Dictionary = world.caravans[candidate_id]
            if candidate["status"] == "travelling":
                caravan_id = String(candidate_id)
                break
        if not caravan_id.is_empty():
            break
    _expect(not caravan_id.is_empty(), "LOD test requires a travelling caravan")
    if caravan_id.is_empty():
        return

    var caravan: Dictionary = world.caravans[caravan_id]
    var before := {
        "status": caravan["status"],
        "days_remaining": caravan["days_remaining"],
        "cargo_salt": caravan["cargo_salt"],
        "guard_strength": caravan["guard_strength"],
    }
    _expect(String(caravan["simulation_lod"]) == SimulationLodScript.REGIONAL, "new off-screen caravan should start at regional LOD")
    _expect(sim.set_caravan_lod(caravan_id, SimulationLodScript.DETAILED), "LOD transition must succeed")
    var after: Dictionary = world.caravans[caravan_id]
    _expect(String(after["simulation_lod"]) == SimulationLodScript.DETAILED, "caravan must enter detailed LOD")
    _expect(before["status"] == after["status"], "LOD transition must not reset status")
    _expect(before["days_remaining"] == after["days_remaining"], "LOD transition must not reset travel progress")
    _expect(before["cargo_salt"] == after["cargo_salt"], "LOD transition must not reset cargo")
    _expect(before["guard_strength"] == after["guard_strength"], "LOD transition must not heal or alter guards")
    _expect(WorldInspectorScript.event_count(world, "simulation_lod_changed") > 0, "LOD transition must be auditable")

func _expect(condition: bool, message: String) -> void:
    if not condition:
        failures.append(message)

func _finish() -> void:
    if failures.is_empty():
        print("PASS Living World Kernel 0A")
        quit(0)
        return
    for failure in failures:
        push_error("FAIL: " + failure)
    quit(1)
