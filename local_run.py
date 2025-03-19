from draw_trees import *

#tech_tree = build_tech_graph()
##tech_tree.format = 'svg'
##tech_tree.render()
#unflat = tech_tree.unflatten(stagger=3)
#unflat.format = 'svg'
#unflat.render()

upgrade_tree = build_unit_upgrade_graph('UNIT_DRAGONGRENADIER')
upgrade_tree.format = 'svg'
upgrade_tree.render()
