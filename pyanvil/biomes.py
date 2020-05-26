class Biome:
    ocean = 'ocean'
    plains = 'plains'
    desert = 'desert'
    mountains = 'mountains'
    forest = 'forest'
    taiga = 'taiga'
    swamp = 'swamp'
    river = 'river'
    nether = 'nether'
    the_end = 'the_end'
    frozen_ocean = 'frozen_ocean'
    frozen_river = 'frozen_river'
    snowy_tundra = 'snowy_tundra'
    snowy_mountains = 'snowy_mountains'
    mushroom_fields = 'mushroom_fields'
    mushroom_field_shore = 'mushroom_field_shore'
    beach = 'beach'
    desert_hills = 'desert_hills'
    wooded_hills = 'wooded_hills'
    taiga_hills = 'taiga_hills'
    mountain_edge = 'mountain_edge'
    jungle = 'jungle'
    jungle_hills = 'jungle_hills'
    jungle_edge = 'jungle_edge'
    deep_ocean = 'deep_ocean'
    stone_shore = 'stone_shore'
    snowy_beach = 'snowy_beach'
    birch_forest = 'birch_forest'
    birch_forest_hills = 'birch_forest_hills'
    dark_forest = 'dark_forest'
    snowy_taiga = 'snowy_taiga'
    snowy_taiga_hills = 'snowy_taiga_hills'
    giant_tree_taiga = 'giant_tree_taiga'
    giant_tree_taiga_hills = 'giant_tree_taiga_hills'
    wooded_mountains = 'wooded_mountains'
    savanna = 'savanna'
    savanna_plateau = 'savanna_plateau'
    badlands = 'badlands'
    wooded_badlands_plateau = 'wooded_badlands_plateau'
    badlands_plateau = 'badlands_plateau'
    small_end_islands = 'small_end_islands'
    end_midlands = 'end_midlands'
    end_highlands = 'end_highlands'
    end_barrens = 'end_barrens'
    warm_ocean = 'warm_ocean'
    lukewarm_ocean = 'lukewarm_ocean'
    cold_ocean = 'cold_ocean'
    deep_warm_ocean = 'deep_warm_ocean'
    deep_lukewarm_ocean = 'deep_lukewarm_ocean'
    deep_cold_ocean = 'deep_cold_ocean'
    deep_frozen_ocean = 'deep_frozen_ocean'
    the_void = 'the_void'
    sunflower_plains = 'sunflower_plains'
    desert_lakes = 'desert_lakes'
    gravelly_mountains = 'gravelly_mountains'
    flower_forest = 'flower_forest'
    taiga_mountains = 'taiga_mountains'
    swamp_hills = 'swamp_hills'
    ice_spikes = 'ice_spikes'
    modified_jungle = 'modified_jungle'
    modified_jungle_edge = 'modified_jungle_edge'
    tall_birch_forest = 'tall_birch_forest'
    tall_birch_hills = 'tall_birch_hills'
    dark_forest_hills = 'dark_forest_hills'
    snowy_taiga_mountains = 'snowy_taiga_mountains'
    giant_spruce_taiga = 'giant_spruce_taiga'
    giant_spruce_taiga_hills = 'giant_spruce_taiga_hills'
    modified_gravelly_mountains = 'modified_gravelly_mountains'
    shattered_savanna = 'shattered_savanna'
    shattered_savanna_plateau = 'shattered_savanna_plateau'
    eroded_badlands = 'eroded_badlands'
    modified_wooded_badlands_plateau = 'modified_wooded_badlands_plateau'
    modified_badlands_plateau = 'modified_badlands_plateau'

    @staticmethod
    def from_index(i):
        if i < len(Biome.biome_list):
            return Biome.biome_list[i]
        return i  # Otherwise it's a mod biome with unknown name, so just return the index.

    biome_list = [
        'ocean',
        'plains',
        'desert',
        'mountains',
        'forest',
        'taiga',
        'swamp',
        'river',
        'nether',
        'the_end',
        'frozen_ocean',
        'frozen_river',
        'snowy_tundra',
        'snowy_mountains',
        'mushroom_fields',
        'mushroom_field_shore',
        'beach',
        'desert_hills',
        'wooded_hills',
        'taiga_hills',
        'mountain_edge',
        'jungle',
        'jungle_hills',
        'jungle_edge',
        'deep_ocean',
        'stone_shore',
        'snowy_beach',
        'birch_forest',
        'birch_forest_hills',
        'dark_forest',
        'snowy_taiga',
        'snowy_taiga_hills',
        'giant_tree_taiga',
        'giant_tree_taiga_hills',
        'wooded_mountains',
        'savanna',
        'savanna_plateau',
        'badlands',
        'wooded_badlands_plateau',
        'badlands_plateau',
        'small_end_islands',
        'end_midlands',
        'end_highlands',
        'end_barrens',
        'warm_ocean',
        'lukewarm_ocean',
        'cold_ocean',
        'deep_warm_ocean',
        'deep_lukewarm_ocean',
        'deep_cold_ocean',
        'deep_frozen_ocean',
        'the_void',
        'sunflower_plains',
        'desert_lakes',
        'gravelly_mountains',
        'flower_forest',
        'taiga_mountains',
        'swamp_hills',
        'ice_spikes',
        'modified_jungle',
        'modified_jungle_edge',
        'tall_birch_forest',
        'tall_birch_hills',
        'dark_forest_hills',
        'snowy_taiga_mountains',
        'giant_spruce_taiga',
        'giant_spruce_taiga_hills',
        'modified_gravelly_mountains',
        'shattered_savanna',
        'shattered_savanna_plateau',
        'eroded_badlands',
        'modified_wooded_badlands_plateau',
        'modified_badlands_plateau',
    ]
