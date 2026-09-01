class_name SeedStreams
extends RefCounted

var root_seed: int
var _streams: Dictionary = {}

func _init(seed_value: int) -> void:
    root_seed = seed_value

func get_rng(stream_name: String) -> RandomNumberGenerator:
    if not _streams.has(stream_name):
        var rng := RandomNumberGenerator.new()
        rng.seed = _derive_seed(stream_name)
        _streams[stream_name] = rng
    return _streams[stream_name]

func export_states() -> Dictionary:
    var states := {}
    for stream_name in _streams.keys():
        states[stream_name] = (_streams[stream_name] as RandomNumberGenerator).state
    return states

func import_states(states: Dictionary) -> void:
    for stream_name in states.keys():
        var rng := get_rng(String(stream_name))
        rng.state = int(states[stream_name])

func _derive_seed(stream_name: String) -> int:
    var text := "%s::%s" % [str(root_seed), stream_name]
    var hash_value: int = 2166136261
    var bytes := text.to_utf8_buffer()
    for byte_value in bytes:
        hash_value = hash_value ^ int(byte_value)
        hash_value = (hash_value * 16777619) & 0xFFFFFFFF
    return hash_value
