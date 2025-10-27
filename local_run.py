from draw_trees import *

# upgrade_tree = build_unit_upgrade_graph('UNIT_MBT')
# upgrade_tree = build_improvement_upgrade_graph('B_TILEIMP_FARM')
# upgrade_tree = build_building_upgrade_graph('B_UNIVERSITY')
# upgrade_tree = build_terrain_upgrade_graph('DesertImprovements')
# upgrade_tree = build_tag_upgrade_graph('Modernization')
# upgrade_tree = build_tag_upgrade_graph('Furnace')
upgrade_tree = build_town_bonus_upgrade_graph('FarmTownBonus')

upgrade_tree.format = 'svg'
upgrade_tree.render()

