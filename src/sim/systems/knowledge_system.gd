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
    world.scheduled_knowledge.append({"delivery_day": world.day + max(delay_days, 0), "scope": "faction", "target_id": faction_id, "event_id": event["id"], "event_type": event["type"], "confidence": clampf(confidence, 0.0, 1.0), "channel": channel})

func grant_faction_immediate(world: WorldState, event: Dictionary, faction_id: String, confidence: float = 1.0, channel: String = "direct") -> void:
    _deliver(world, {"delivery_day": world.day, "scope": "faction", "target_id": faction_id, "event_id": event["id"], "event_type": event["type"], "confidence": clampf(confidence, 0.0, 1.0), "channel": channel})

func _deliver(world: WorldState, packet: Dictionary) -> void:
    if packet["scope"] == "faction":
        var faction_id := String(packet["target_id"])
        if not world.faction_knowledge.has(faction_id):
            world.faction_knowledge[faction_id] = []
        (world.faction_knowledge[faction_id] as Array).append(packet.duplicate(true))
        world.record_event("knowledge_delivered", {"target_scope": "faction", "target_id": faction_id, "source_event_id": packet["event_id"], "source_event_type": packet["event_type"], "channel": packet["channel"], "confidence": packet["confidence"]})
