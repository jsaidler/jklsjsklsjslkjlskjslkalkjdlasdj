extends SceneTree

const WorldFactoryScript = preload("res://src/sim/world_factory.gd")
const WorldSimulatorScript = preload("res://src/sim/world_simulator.gd")
const WorldInspectorScript = preload("res://src/sim/debug/world_inspector.gd")

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    var seed_value := 190512
    var days := 120
    if args.size() >= 1: seed_value = int(args[0])
    if args.size() >= 2: days = int(args[1])
    var world := WorldFactoryScript.create_kernel_0a(seed_value)
    var sim := WorldSimulatorScript.new(world)
    sim.run_days(days)
    print("Living World Kernel 0A")
    print("seed=%d days=%d" % [seed_value, days])
    print("--- timeline ---")
    print(WorldInspectorScript.timeline(world))
    print("--- last bandit decision ---")
    print(WorldInspectorScript.explain_decision(WorldInspectorScript.last_decision(world, "red_knives", "bandit_caravan_response")))
    print("--- signature ---")
    print(WorldInspectorScript.signature(world))
    quit(0)
