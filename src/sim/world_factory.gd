class_name WorldFactory
extends RefCounted

static func create_kernel_0a(seed_value: int) -> WorldState:
    var world := WorldState.new(seed_value)
    var streams := SeedStreams.new(seed_value)
    var rng := streams.get_rng("world_generation")
    world.cultures = {"asha_riverfolk": {"trade_value": 0.82, "hospitality": 0.68, "slavery_acceptance": 0.18, "combat_doctrine": "shielded_escort"}, "red_waste_clans": {"trade_value": 0.31, "hospitality": 0.22, "slavery_acceptance": 0.74, "combat_doctrine": "ambush_and_withdrawal"}}
    world.regions = {"salt_road_vale": {"biome": "semi_arid_vale", "ecology": {"prey_level": rng.randf_range(22.0, 34.0), "prey_carrying_capacity": 40.0}}}
    world.routes = {"white_road": {"from": "white_salt_quarry", "to": "asha", "travel_days": 4, "predator_territory_overlap": rng.randf_range(0.58, 0.82)}}
    world.settlements = {"asha": {"name": "Asha", "faction_id": "asha_council", "salt_stock": rng.randf_range(8.0, 12.0), "daily_salt_use": 0.72, "reorder_point": 7.0, "target_stock": 23.0, "population": 86}}
    world.factions = {"asha_council": {"culture_id": "asha_riverfolk", "goal": "keep_settlement_supplied", "known_route_danger": 0.0, "knowledge_cursor": 0}, "salt_bearers": {"culture_id": "asha_riverfolk", "goal": "move_salt_for_profit", "knowledge_cursor": 0}, "road_wardens": {"culture_id": "asha_riverfolk", "goal": "keep_white_road_open", "escort_bonus": 0.0, "known_route_danger": 0.0, "knowledge_cursor": 0}, "red_knives": {"culture_id": "red_waste_clans", "goal": "secure_resources_through_raiding", "salt_stock": rng.randf_range(2.0, 5.5), "salt_target": 12.0, "daily_salt_use": 0.22, "salt_need": 0.7, "aggression": rng.randf_range(0.68, 0.86), "route_intel": rng.randf_range(0.72, 0.92), "morale": rng.randf_range(0.60, 0.80), "raider_strength": rng.randf_range(5.2, 6.5), "recent_loss_fear": 0.0, "knowledge_cursor": 0}}
    world.species = {"ash_hyena": {"region_id": "salt_road_vale", "behavior": "territorial_pack_predator", "pack_size": rng.randi_range(4, 6), "hunger": rng.randf_range(0.42, 0.60)}}
    world.agents = {
        "asha_steward": {"species": "human", "culture_id": "asha_riverfolk", "faction_id": "asha_council", "role": "steward", "traits": {"caution": 0.72, "greed": 0.28, "loyalty": 0.80}},
        "warden_captain": {"species": "human", "culture_id": "asha_riverfolk", "faction_id": "road_wardens", "role": "captain", "traits": {"courage": 0.75, "caution": 0.54, "loyalty": 0.83}},
        "road_scout": {"species": "human", "culture_id": "asha_riverfolk", "faction_id": "road_wardens", "role": "caravan_scout", "traits": {"courage": 0.66, "caution": 0.74, "loyalty": 0.72}},
        "red_knife_chief": {"species": "human", "culture_id": "red_waste_clans", "faction_id": "red_knives", "role": "raider_chief", "traits": {"courage": 0.79, "greed": 0.72, "caution": 0.34}},
    }
    for faction_id in world.factions.keys():
        world.faction_knowledge[faction_id] = []
    for agent_id in world.agents.keys():
        world.agent_knowledge[agent_id] = []
    world.rng_states = streams.export_states()
    return world
