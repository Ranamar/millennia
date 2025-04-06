from draw_trees import *

#tech_tree = build_tech_graph()
##tech_tree.format = 'svg'
##tech_tree.render()
#unflat = tech_tree.unflatten(stagger=3)
#unflat.format = 'svg'
#unflat.render()

# upgrade_tree = build_unit_upgrade_graph('UNIT_AIBOMBER')
# upgrade_tree = build_improvement_upgrade_graph('B_TILEIMP_FARM')
# upgrade_tree = build_building_upgrade_graph('B_UNIVERSITY')
upgrade_tree = build_terrain_upgrade_graph('Hills')
upgrade_tree.format = 'svg'
upgrade_tree.render()
