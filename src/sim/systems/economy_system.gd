class_name EconomySystem
extends RefCounted

func tick(world: WorldState) -> void:
    var settlement: Dictionary = world.settlements["asha"]
    settlement["salt_stock"] = maxf(0.0, float(settlement["salt_stock"]) - float(settlement["daily_salt_use"]))
    var stock := float(settlement["salt_stock"])
    if stock <= float(settlement["reorder_point"]):
        if not world.has_active_caravan_to("asha") and not world.has_open_trade_request("asha"):
            var request := {"id": world.next_request_id(), "settlement_id": "asha", "resource": "salt", "amount": float(settlement["target_stock"]) - stock, "created_day": world.day, "status": "open"}
            world.trade_requests.append(request)
            var event := world.record_event("trade_requested", request)
            (world.faction_knowledge["asha_council"] as Array).append({"delivery_day": world.day, "scope": "faction", "target_id": "asha_council", "event_id": event["id"], "event_type": event["type"], "confidence": 1.0, "channel": "internal"})
