class_name KnowledgeSystem
extends RefCounted

func tick(world: WorldState) -> void:
    var remaining: Array = []
    for packet in world.scheduled_knowledge:
        if int(packet["delivery_day"]) <= world.day:
            _deliver(world, packet)
        else:
            remaining.append(packet)
    world.scheduled_knowledge = remaining

func schedule_for_faction(world: WorldState, event: Dictionary, faction_id: String, delay_days: int, confidence: float, channel: String) -> void:
    _schedule(world, event, "faction", faction_id, delay_days, confidence, channel)

func schedule_for_agent(world: WorldState, event: Dictionary, agent_id: String, delay_days: int, confidence: float, channel: String) -> void:
    _schedule(world, event, "agent", agent_id, delay_days, confidence, channel)

func grant_faction_immediate(world: WorldState, event: Dictionary, faction_id: String, confidence: float = 1.0, channel: String = "direct") -> void:
    _deliver(world, _packet(world, event, "faction", faction_id, 0, confidence, channel))

func grant_agent_immediate(world: WorldState, event: Dictionary, agent_id: String, confidence: float = 1.0, channel: String = "direct") -> void:
    _deliver(world, _packet(world, event, "agent", agent_id, 0, confidence, channel))

func _schedule(world: WorldState, event: Dictionary, scope: String, target_id: String, delay_days: int, confidence: float, channel: String) -> void:
    world.scheduled_knowledge.append(_packet(world, event, scope, target_id, delay_days, confidence, channel))

func _packet(world: WorldState, event: Dictionary, scope: String, target_id: String, delay_days: int, confidence: float, channel: String) -> Dictionary:
    return {
        "delivery_day": world.day + max(delay_days, 0),
        "scope": scope,
        "target_id": target_id,
        "event_id": event["id"],
        "event_type": event["type"],
        "confidence": clampf(confidence, 0.0, 1.0),
        "channel": channel,
    }

func _deliver(world: WorldState, packet: Dictionary) -> void:
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
    })
