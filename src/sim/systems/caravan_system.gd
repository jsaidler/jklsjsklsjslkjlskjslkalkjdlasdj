class_name CaravanSystem
extends RefCounted

const KnowledgeSystemScript = preload("res://src/sim/systems/knowledge_system.gd")
const SimulationLodScript = preload("res://src/sim/simulation_lod.gd")
const SimulationSchedulerScript = preload("res://src/sim/simulation_scheduler.gd")
var knowledge := KnowledgeSystemScript.new()
var scheduler := SimulationSchedulerScript.new()

func tick(world, streams, ecology, factions) -> void:
    _spawn_from_requests(world, streams)
    for caravan_id in world.caravans.keys():
        var caravan: Dictionary = world.caravans[caravan_id]
        if caravan["status"] != "travelling":
            continue
        scheduler.ensure(caravan, world.day, SimulationLodScript.REGIONAL)
        if not scheduler.is_due(caravan, world.day):
            continue

        var elapsed_days := scheduler.elapsed_days(caravan, world.day)

        _consider_predators(world, caravan, streams, ecology)
        if caravan["status"] != "travelling":
            scheduler.mark_simulated(caravan, world.day)
            continue
        _consider_bandits(world, caravan, streams, factions)
        if caravan["status"] != "travelling":
            scheduler.mark_simulated(caravan, world.day)
            continue

        caravan["days_remaining"] = int(caravan["days_remaining"]) - elapsed_days
        if int(caravan["days_remaining"]) <= 0:
            _arrive(world, caravan)
            scheduler.mark_simulated(caravan, world.day)
            continue

        scheduler.mark_simulated(caravan, world.day, int(caravan["days_remaining"]))

func set_lod(world, caravan_id: String, lod: String) -> bool:
    if not world.caravans.has(caravan_id):
        return false
    var caravan: Dictionary = world.caravans[caravan_id]
    var preserved := {
        "status": caravan["status"],
        "days_remaining": caravan["days_remaining"],
        "cargo_salt": caravan["cargo_salt"],
        "guard_strength": caravan["guard_strength"],
    }
    return scheduler.set_lod(world, "caravan", caravan_id, caravan, lod, preserved)

func _spawn_from_requests(world, streams) -> void:
    var rng := streams.get_rng("caravan_generation")
    for request in world.trade_requests:
        if request["status"] != "open":
            continue
        var wardens: Dictionary = world.factions["road_wardens"]
        var caravan_id := world.next_caravan_id()
        var cargo := minf(24.0, maxf(12.0, float(request["amount"])))
        var guard_strength := 4.6 + float(wardens["escort_bonus"]) + rng.randf_range(-0.35, 0.35)
        var caravan := {
            "id": caravan_id,
            "request_id": request["id"],
            "origin": "white_salt_quarry",
            "destination": request["settlement_id"],
            "route_id": "white_road",
            "status": "travelling",
            "days_remaining": 4,
            "cargo_salt": cargo,
            "guard_strength": guard_strength,
            "escort_quality": 0.55 + float(wardens["escort_bonus"]) * 0.04,
        }
        scheduler.ensure(caravan, world.day, SimulationLodScript.REGIONAL)
        world.caravans[caravan_id] = caravan
        request["status"] = "dispatched"
        var event := world.record_event("caravan_departed", {
            "caravan_id": caravan_id,
            "request_id": request["id"],
            "cargo_salt": cargo,
            "guard_strength": guard_strength,
            "route_id": "white_road",
            "simulation_lod": SimulationLodScript.REGIONAL,
        })
        knowledge.grant_faction_immediate(world, event, "salt_bearers", 1.0, "dispatch_record")

func _consider_predators(world, caravan: Dictionary, streams, ecology) -> void:
    var scores: Dictionary = ecology.predator_attack_utility(world, caravan)
    var action := "attack" if float(scores["total"]) >= 0.58 else "ignore"
    world.log_decision("ash_hyena_pack", "predator_caravan_response", action, scores, {"caravan_id": caravan["id"], "simulation_lod": caravan["simulation_lod"]})
    if action != "attack":
        return
    var result: Dictionary = ecology.resolve_predator_attack(world, caravan, streams)
    var event := world.record_event("predator_attack", {"caravan_id": caravan["id"], "species_id": "ash_hyena", "guard_loss": result["guard_loss"], "pressure": result["pressure"]}, ["tracks", "wounds"])
    knowledge.schedule_for_faction(world, event, "road_wardens", 1, 0.85, "caravan_report")

func _consider_bandits(world, caravan: Dictionary, streams, factions) -> void:
    var scores: Dictionary = factions.bandit_attack_scores(world, caravan)
    var action := "attack" if float(scores["total"]) >= 0.43 else "shadow"
    world.log_decision("red_knives", "bandit_caravan_response", action, scores, {"caravan_id": caravan["id"], "simulation_lod": caravan["simulation_lod"]})
    if action != "attack":
        return
    var result: Dictionary = factions.resolve_bandit_attack(world, caravan, streams)
    var event := world.record_event("bandit_attack", {
        "caravan_id": caravan["id"],
        "attacker_faction": "red_knives",
        "bandits_win": result["bandits_win"],
        "power_ratio": result["power_ratio"],
        "roll": result["roll"],
        "witness_agent_ids": ["road_scout"],
    }, ["survivor_testimony", "tracks", "spent_arrows"])

    var witness_packet := knowledge.grant_agent_immediate(world, event, "road_scout", 1.0, "direct_witness")
    knowledge.relay_from_agent(world, "road_scout", witness_packet, "road_wardens", 2, 0.95, "road_scout_report")
    knowledge.grant_faction_immediate(world, event, "red_knives", 1.0, "participants")
    if bool(result["bandits_win"]):
        world.record_event("caravan_lost", {"caravan_id": caravan["id"], "cause": "red_knives"})

func _arrive(world, caravan: Dictionary) -> void:
    caravan["status"] = "arrived"
    var settlement: Dictionary = world.settlements[caravan["destination"]]
    settlement["salt_stock"] = float(settlement["salt_stock"]) + float(caravan["cargo_salt"])
    var event := world.record_event("caravan_arrived", {"caravan_id": caravan["id"], "destination": caravan["destination"], "cargo_salt": caravan["cargo_salt"]})
    knowledge.grant_faction_immediate(world, event, "asha_council", 1.0, "arrival")
    knowledge.grant_faction_immediate(world, event, "road_wardens", 1.0, "escort_record")
