class_name WorldInspector
extends RefCounted

static func event_count(world, event_type: String) -> int:
    var count := 0
    for event in world.events:
        if event["type"] == event_type:
            count += 1
    return count

static func first_event(world, event_type: String) -> Dictionary:
    for event in world.events:
        if event["type"] == event_type:
            return event
    return {}

static func first_knowledge_delivery_for(world, target_id: String, source_event_id: int) -> Dictionary:
    for event in world.events:
        if event["type"] != "knowledge_delivered":
            continue
        var payload: Dictionary = event["payload"]
        if payload["target_id"] == target_id and int(payload["source_event_id"]) == source_event_id:
            return event
    return {}

static func knowledge_packet_for(world, scope: String, target_id: String, source_event_id: int) -> Dictionary:
    var packets: Array = []
    if scope == "agent":
        packets = world.agent_knowledge.get(target_id, [])
    elif scope == "faction":
        packets = world.faction_knowledge.get(target_id, [])
    for packet in packets:
        if int(packet["event_id"]) == source_event_id:
            return packet
    return {}

static func last_decision(world, subject_id: String, decision_type: String) -> Dictionary:
    for index in range(world.decision_log.size() - 1, -1, -1):
        var decision: Dictionary = world.decision_log[index]
        if decision["subject_id"] == subject_id and decision["decision_type"] == decision_type:
            return decision
    return {}

static func explain_decision(decision: Dictionary) -> String:
    if decision.is_empty():
        return "No decision found."
    var score_parts: Array[String] = []
    var scores: Dictionary = decision["scores"]
    var keys := scores.keys()
    keys.sort()
    for key in keys:
        score_parts.append("%s=%0.3f" % [String(key), float(scores[key])])
    return "day=%d subject=%s decision=%s action=%s | %s" % [int(decision["day"]), String(decision["subject_id"]), String(decision["decision_type"]), String(decision["chosen_action"]), ", ".join(score_parts)]

static func signature(world) -> String:
    var parts: Array[String] = []
    parts.append("seed=%d" % world.seed)
    parts.append("day=%d" % world.day)
    parts.append("asha_salt=%0.4f" % float(world.settlements["asha"]["salt_stock"]))
    parts.append("bandit_salt=%0.4f" % float(world.factions["red_knives"]["salt_stock"]))
    parts.append("bandit_strength=%0.4f" % float(world.factions["red_knives"]["raider_strength"]))
    parts.append("warden_escort=%0.4f" % float(world.factions["road_wardens"]["escort_bonus"]))
    parts.append("hyena_hunger=%0.4f" % float(world.species["ash_hyena"]["hunger"]))
    parts.append("prey_level=%0.4f" % float(world.regions["salt_road_vale"]["ecology"]["prey_level"]))
    var sequence: Array[String] = []
    for event in world.events:
        sequence.append("%d:%s" % [int(event["day"]), String(event["type"])])
    parts.append("events=" + ";".join(sequence))
    return "\n".join(parts)

static func timeline(world, limit: int = 80) -> String:
    var lines: Array[String] = []
    var start := maxi(0, world.events.size() - limit)
    for index in range(start, world.events.size()):
        var event: Dictionary = world.events[index]
        lines.append("D%03d #%04d %-22s %s" % [int(event["day"]), int(event["id"]), String(event["type"]), str(event["payload"])])
    return "\n".join(lines)
