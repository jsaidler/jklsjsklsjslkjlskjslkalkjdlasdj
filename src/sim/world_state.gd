class_name WorldState
extends RefCounted

var seed: int
var day: int = 0
var cultures: Dictionary = {}
var factions: Dictionary = {}
var settlements: Dictionary = {}
var regions: Dictionary = {}
var routes: Dictionary = {}
var species: Dictionary = {}
var agents: Dictionary = {}
var caravans: Dictionary = {}
var trade_requests: Array = []
var events: Array = []
var faction_knowledge: Dictionary = {}
var agent_knowledge: Dictionary = {}
var scheduled_knowledge: Array = []
var decision_log: Array = []
var rng_states: Dictionary = {}
var _next_event_id: int = 1
var _next_caravan_id: int = 1
var _next_request_id: int = 1

func _init(seed_value: int) -> void:
    seed = seed_value

func next_caravan_id() -> String:
    var value := "caravan_%04d" % _next_caravan_id
    _next_caravan_id += 1
    return value

func next_request_id() -> String:
    var value := "request_%04d" % _next_request_id
    _next_request_id += 1
    return value

func record_event(event_type: String, payload: Dictionary = {}, evidence: Array = []) -> Dictionary:
    var event := {"id": _next_event_id, "day": day, "type": event_type, "payload": payload.duplicate(true), "evidence": evidence.duplicate(true)}
    _next_event_id += 1
    events.append(event)
    return event

func log_decision(subject_id: String, decision_type: String, chosen_action: String, scores: Dictionary, context: Dictionary = {}) -> void:
    decision_log.append({"day": day, "subject_id": subject_id, "decision_type": decision_type, "chosen_action": chosen_action, "scores": scores.duplicate(true), "context": context.duplicate(true)})

func has_active_caravan_to(settlement_id: String) -> bool:
    for caravan in caravans.values():
        if caravan["destination"] == settlement_id and caravan["status"] == "travelling":
            return true
    return false

func has_open_trade_request(settlement_id: String) -> bool:
    for request in trade_requests:
        if request["settlement_id"] == settlement_id and request["status"] == "open":
            return true
    return false
