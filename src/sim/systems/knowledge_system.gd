class_name KnowledgeSystem
extends RefCounted

func tick(world) -> void:
    var remaining: Array = []
    for packet in world.scheduled_knowledge:
        if int(packet["delivery_day"]) <= world.day:
            _deliver(world, packet)
        else:
            remaining.append(packet)
    world.scheduled_knowledge = remaining

func schedule_for_faction(world, event: Dictionary, faction_id: String, delay_days: int, confidence: float, channel: String) -> void:
    _schedule(world, _packet_from_event(world, event, "faction", faction_id, delay_days, confidence, channel))

func schedule_for_agent(world, event: Dictionary, agent_id: String, delay_days: int, confidence: float, channel: String) -> void:
    _schedule(world, _packet_from_event(world, event, "agent", agent_id, delay_days, confidence, channel))

func grant_faction_immediate(world, event: Dictionary, faction_id: String, confidence: float = 1.0, channel: String = "direct") -> Dictionary:
    var packet := _packet_from_event(world, event, "faction", faction_id, 0, confidence, channel)
    _deliver(world, packet)
    return packet

func grant_agent_immediate(world, event: Dictionary, agent_id: String, confidence: float = 1.0, channel: String = "direct") -> Dictionary:
    var packet := _packet_from_event(world, event, "agent", agent_id, 0, confidence, channel)
    _deliver(world, packet)
    return packet

func relay_from_agent(world, source_agent_id: String, source_packet: Dictionary, target_faction_id: String, delay_days: int, confidence_multiplier: float, channel: String) -> Dictionary:
    return _relay(world, source_packet, "agent", source_agent_id, "faction", target_faction_id, delay_days, confidence_multiplier, channel)

func relay_from_faction(world, source_faction_id: String, source_packet: Dictionary, target_faction_id: String, delay_days: int, confidence_multiplier: float, channel: String) -> Dictionary:
    return _relay(world, source_packet, "faction", source_faction_id, "faction", target_faction_id, delay_days, confidence_multiplier, channel)

func _relay(world, source_packet: Dictionary, source_scope: String, source_id: String, target_scope: String, target_id: String, delay_days: int, confidence_multiplier: float, channel: String) -> Dictionary:
    var provenance: Array = (source_packet.get("provenance", []) as Array).duplicate(true)
    provenance.append({
        "scope": source_scope,
        "id": source_id,
        "channel": channel,
        "relay_day": world.day,
    })
    var packet := {
        "delivery_day": world.day + max(delay_days, 0),
        "scope": target_scope,
        "target_id": target_id,
        "event_id": int(source_packet["event_id"]),
        "event_type": String(source_packet["event_type"]),
        "confidence": clampf(float(source_packet["confidence"]) * confidence_multiplier, 0.0, 1.0),
        "channel": channel,
        "hops": int(source_packet.get("hops", 0)) + 1,
        "provenance": provenance,
    }
    _schedule(world, packet)
    return packet

func _schedule(world, packet: Dictionary) -> void:
    world.scheduled_knowledge.append(packet.duplicate(true))

func _packet_from_event(world, event: Dictionary, scope: String, target_id: String, delay_days: int, confidence: float, channel: String) -> Dictionary:
    return {
        "delivery_day": world.day + max(delay_days, 0),
        "scope": scope,
        "target_id": target_id,
        "event_id": int(event["id"]),
        "event_type": String(event["type"]),
        "confidence": clampf(confidence, 0.0, 1.0),
        "channel": channel,
        "hops": 0,
        "provenance": [{
            "scope": "world_event",
            "id": str(event["id"]),
            "channel": channel,
            "relay_day": world.day,
        }],
    }

func _deliver(world, packet: Dictionary) -> void:
    var scope := String(packet["scope"])
    var target_id := String(packet["target_id"])
    if scope == "faction":
        if not world.faction_knowledge.has(target_id):
            world.faction_knowledge[target_id] = []
        (world.faction_knowledge[target_id] as Array).append(packet.duplicate(true))
    elif scope == "agent":
        if not world.agent_knowledge.has(target_id):
            world.agent_knowledge[target_id] = []
        (world.agent_knowledge[target_id] as Array).append(packet.duplicate(true))
    else:
        push_error("Unsupported knowledge scope: " + scope)
        return

    world.record_event("knowledge_delivered", {
        "target_scope": scope,
        "target_id": target_id,
        "source_event_id": packet["event_id"],
        "source_event_type": packet["event_type"],
        "channel": packet["channel"],
        "confidence": packet["confidence"],
        "hops": packet.get("hops", 0),
        "provenance": (packet.get("provenance", []) as Array).duplicate(true),
    })
