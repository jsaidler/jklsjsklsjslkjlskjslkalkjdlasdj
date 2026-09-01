class_name FactionSystem
extends RefCounted

func tick(world: WorldState) -> void:
    _consume_bandit_resources(world)
    _process_new_knowledge(world, "asha_council")
    _process_new_knowledge(world, "road_wardens")

func bandit_attack_scores(world: WorldState, caravan: Dictionary) -> Dictionary:
    var bandits: Dictionary = world.factions["red_knives"]
    var need := float(bandits["salt_need"])
    var aggression := float(bandits["aggression"])
    var intel := float(bandits["route_intel"])
    var morale := float(bandits["morale"])
    var guard_deterrence := clampf(float(caravan["guard_strength"]) / 10.0, 0.0, 1.0)
    var recent_loss_fear := float(bandits["recent_loss_fear"])
    var cargo_value := clampf(float(caravan["cargo_salt"]) / 24.0, 0.0, 1.0)
    var total := need * 0.30 + aggression * 0.22 + intel * 0.12 + morale * 0.12 + cargo_value * 0.24 - guard_deterrence * 0.25 - recent_loss_fear * 0.22
    return {"salt_need": need * 0.30, "aggression": aggression * 0.22, "route_intel": intel * 0.12, "morale": morale * 0.12, "cargo_value": cargo_value * 0.24, "guard_deterrence": -guard_deterrence * 0.25, "recent_loss_fear": -recent_loss_fear * 0.22, "total": total}

func resolve_bandit_attack(world: WorldState, caravan: Dictionary, streams: SeedStreams) -> Dictionary:
    var bandits: Dictionary = world.factions["red_knives"]
    var rng := streams.get_rng("faction_combat")
    var bandit_power := float(bandits["raider_strength"]) * (0.75 + float(bandits["morale"]) * 0.5)
    var guard_power := float(caravan["guard_strength"]) * (0.90 + float(caravan["escort_quality"]) * 0.35)
    var ratio := bandit_power / maxf(bandit_power + guard_power, 0.001)
    var roll := rng.randf()
    var bandits_win := roll < ratio
    if bandits_win:
        var stolen := float(caravan["cargo_salt"])
        bandits["salt_stock"] = float(bandits["salt_stock"]) + stolen
        caravan["cargo_salt"] = 0.0
        caravan["status"] = "lost"
        bandits["morale"] = clampf(float(bandits["morale"]) + 0.08, 0.0, 1.0)
        bandits["recent_loss_fear"] = maxf(0.0, float(bandits["recent_loss_fear"]) - 0.12)
    else:
        bandits["raider_strength"] = maxf(2.0, float(bandits["raider_strength"]) - 1.0)
        bandits["morale"] = maxf(0.1, float(bandits["morale"]) - 0.10)
        bandits["recent_loss_fear"] = clampf(float(bandits["recent_loss_fear"]) + 0.24, 0.0, 1.0)
        caravan["guard_strength"] = maxf(1.0, float(caravan["guard_strength"]) - 0.75)
    return {"bandits_win": bandits_win, "power_ratio": ratio, "roll": roll}

func _consume_bandit_resources(world: WorldState) -> void:
    var bandits: Dictionary = world.factions["red_knives"]
    bandits["salt_stock"] = maxf(0.0, float(bandits["salt_stock"]) - float(bandits["daily_salt_use"]))
    var target := maxf(float(bandits["salt_target"]), 1.0)
    bandits["salt_need"] = clampf(1.0 - float(bandits["salt_stock"]) / target, 0.0, 1.0)
    bandits["recent_loss_fear"] = maxf(0.0, float(bandits["recent_loss_fear"]) - 0.01)

func _process_new_knowledge(world: WorldState, faction_id: String) -> void:
    var faction: Dictionary = world.factions[faction_id]
    var knowledge: Array = world.faction_knowledge[faction_id]
    var cursor := int(faction.get("knowledge_cursor", 0))
    while cursor < knowledge.size():
        var packet: Dictionary = knowledge[cursor]
        if packet["event_type"] == "bandit_attack" and faction_id in ["asha_council", "road_wardens"]:
            faction["known_route_danger"] = clampf(float(faction.get("known_route_danger", 0.0)) + 0.22 * float(packet["confidence"]), 0.0, 1.0)
            if faction_id == "road_wardens":
                faction["escort_bonus"] = minf(4.0, float(faction["escort_bonus"]) + 0.6)
        cursor += 1
    faction["knowledge_cursor"] = cursor
