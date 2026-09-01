class_name CaravanSystem
extends RefCounted

const KnowledgeSystemScript = preload("res://src/sim/systems/knowledge_system.gd")
var knowledge := KnowledgeSystemScript.new()

func tick(world: WorldState, streams: SeedStreams, ecology, factions) -> void:
    _spawn_from_requests(world, streams)
    for caravan_id in world.caravans.keys():
        var caravan: Dictionary = world.caravans[caravan_id]
        if caravan["status"] != "travelling":
            continue
        _consider_predators(world, caravan, streams, ecology)
        if caravan["status"] != "travelling": continue
        _consider_bandits(world, caravan, streams, factions)
        if caravan["status"] != "travelling": continue
        caravan["days_remaining"] = int(caravan["days_remaining"]) - 1
        if int(caravan["days_remaining"]) <= 0: _arrive(world, caravan)

func _spawn_from_requests(world: WorldState, streams: SeedStreams) -> void:
    var rng := streams.get_rng("caravan_generation")
    for request in world.trade_requests:
        if request["status"] != "open": continue
        var wardens: Dictionary = world.factions["road_wardens"]
        var caravan_id := world.next_caravan_id()
        var cargo := minf(24.0, maxf(12.0, float(request["amount"])))
        var guard_strength := 4.6 + float(wardens["escort_bonus"]) + rng.randf_range(-0.35, 0.35)
        world.caravans[caravan_id] = {"id": caravan_id, "request_id": request["id"], "origin": "white_salt_quarry", "destination": request["settlement_id"], "route_id": "white_road", "status": "travelling", "days_remaining": 4, "cargo_salt": cargo, "guard_strength": guard_strength, "escort_quality": 0.55 + float(wardens["escort_bonus"]) * 0.04}
        request["status"] = "dispatched"
        var event := world.record_event("caravan_departed", {"caravan_id": caravan_id, "request_id": request["id"], "cargo_salt": cargo, "guard_strength": guard_strength, "route_id": "white_road"})
        knowledge.grant_faction_immediate(world, event, "salt_bearers", 1.0, "dispatch_record")

func _consider_predators(world: WorldState, caravan: Dictionary, streams: SeedStreams, ecology) -> void:
    var scores: Dictionary = ecology.predator_attack_utility(world, caravan)
    var action := "attack" if float(scores["total"]) >= 0.58 else "ignore"
    world.log_decision("ash_hyena_pack", "predator_caravan_response", action, scores, {"caravan_id": caravan["id"]})
    if action != "attack": return
    var result: Dictionary = ecology.resolve_predator_attack(world, caravan, streams)
    var event := world.record_event("predator_attack", {"caravan_id": caravan["id"], "species_id": "ash_hyena", "guard_loss": result["guard_loss"], "pressure": result["pressure"]}, ["tracks", "wounds"])
    knowledge.schedule_for_faction(world, event, "road_wardens", 1, 0.85, "caravan_report")

func _consider_bandits(world: WorldState, caravan: Dictionary, streams: SeedStreams, factions) -> void:
    var scores: Dictionary = factions.bandit_attack_scores(world, caravan)
    var action := "attack" if float(scores["total"]) >= 0.43 else "shadow"
    world.log_decision("red_knives", "bandit_caravan_response", action, scores, {"caravan_id": caravan["id"]})
    if action != "attack": return
    var result: Dictionary = factions.resolve_bandit_attack(world, caravan, streams)
    var event := world.record_event("bandit_attack", {"caravan_id": caravan["id"], "attacker_faction": "red_knives", "bandits_win": result["bandits_win"], "power_ratio": result["power_ratio"], "roll": result["roll"]}, ["survivor_testimony", "tracks", "spent_arrows"])
    knowledge.grant_faction_immediate(world, event, "red_knives", 1.0, "participants")
    knowledge.schedule_for_faction(world, event, "road_wardens", 2, 0.95, "survivor_or_scout_report")
    knowledge.schedule_for_faction(world, event, "asha_council", 3, 0.90, "warden_message")
    if bool(result["bandits_win"]): world.record_event("caravan_lost", {"caravan_id": caravan["id"], "cause": "red_knives"})

func _arrive(world: WorldState, caravan: Dictionary) -> void:
    caravan["status"] = "arrived"
    var settlement: Dictionary = world.settlements[caravan["destination"]]
    settlement["salt_stock"] = float(settlement["salt_stock"]) + float(caravan["cargo_salt"])
    var event := world.record_event("caravan_arrived", {"caravan_id": caravan["id"], "destination": caravan["destination"], "cargo_salt": caravan["cargo_salt"]})
    knowledge.grant_faction_immediate(world, event, "asha_council", 1.0, "arrival")
    knowledge.grant_faction_immediate(world, event, "road_wardens", 1.0, "escort_record")
