extends SceneTree

const WorldFactoryScript = preload("res://src/sim/world_factory.gd")
const WorldSimulatorScript = preload("res://src/sim/world_simulator.gd")
const WorldInspectorScript = preload("res://src/sim/debug/world_inspector.gd")
var failures: Array[String] = []

func _initialize() -> void:
    _test_determinism()
    _test_seed_divergence()
    _test_causal_trade_and_threat_loop()
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
        if not delivery.is_empty(): _expect(int(delivery["day"]) > int(attack["day"]), "information must travel; Asha cannot know the attack instantly")
    var decision := WorldInspectorScript.last_decision(world, "red_knives", "bandit_caravan_response")
    _expect(not decision.is_empty(), "bandit behavior must leave an auditable decision record")
    if not decision.is_empty(): _expect((decision["scores"] as Dictionary).has("salt_need"), "decision explanation must expose causal factors")
    _expect(float(world.factions["road_wardens"]["escort_bonus"]) > 0.0, "road wardens must adapt after learning about attacks")

func _expect(condition: bool, message: String) -> void:
    if not condition: failures.append(message)

func _finish() -> void:
    if failures.is_empty():
        print("PASS Living World Kernel 0A")
        quit(0)
        return
    for failure in failures: push_error("FAIL: " + failure)
    quit(1)
