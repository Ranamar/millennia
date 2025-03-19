import graphviz
import millennia_data
from pprint import pprint as pretty_print

tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects = millennia_data.load_data()

#TODO: Call this from build_tech_graph() if we're not deprecating that.
def build_age_trunk(name='age_trunk', spacing='4', cluster_trunk=True):
    tree = graphviz.Digraph(name=name)
    trunk_name = 'cluster_agealign'
    if not cluster_trunk:
        trunk_name = 'trunk_ages_unaligned'
    with tree.subgraph(name=trunk_name) as age_align:
        for age, children in age_advances.items():
            # We're trying to build a main trunk box.
            # Fortunately, the non-trunk ages all have underscores in their name, so that's an easy filter.
            if '_' not in age:
                age_align.node(age)
            with tree.subgraph(name='sub_'+age) as cluster:
                cluster.attr('edge', minlen=spacing)
                for child in children:
                    cluster.edge(age, child)
    return tree

# Create a list of digraphs named "cluster_age_[age number]" to cluster each age's techs and unlocks.
#TODO: Finish using this
def build_age_clusters():
    age_clusters = []
    for i in range(10):
        cluster = graphviz.Digraph(name='cluster_age_'+str(i))
        #TODO: Put the ages in the clusters here?
        # You can't draw advancement lines for ages here because they'll be in different clusters
        # That will need to go in a later function that assembles the clusters into a graph.
        age_clusters.append(cluster)
    return age_clusters

def build_tech_graph():
    tree = graphviz.Digraph(name='tech_tree')
    tree.attr(compound='true')
    with tree.subgraph(name='cluster_agealign') as age_align:
        for age, children in age_advances.items():
            # This is super hacky, but we're just trying to do some age alignment
            if age != 'TECHAGE6_CRISISHERESY':
                age_align.node(age)
            with tree.subgraph(name='sub_'+age) as cluster:
                cluster.attr('edge', minlen='4')
                for child in children:
                    cluster.edge(age, child)
    for age, children in age_spirits.items():
        cluster_name = 'cluster_spirits_'+age
        with tree.subgraph(name=cluster_name) as cluster:
            for child in children:
                cluster.node(child)
        tree.edge(age, children[0], lhead=cluster_name)
    for age, children in age_governments.items():
        cluster_name = 'cluster_governments_'+age
        with tree.subgraph(name=cluster_name) as cluster:
            for child in children:
                cluster.node(child)
        tree.edge(age, children[0], lhead=cluster_name)
    for tech, parents in tech_ages.items():
        for parent in parents:
            tree.edge(parent, tech)
    return tree

def find_unit_upgrade_lines(search_unit):
    upgrade_lines = {}
    # It's just easier to do if we know we have at least one 
    for line in search_unit.upgrade_lines:
        upgrade_lines[line] = [search_unit]
    for name, unit in units.items():
        if name != search_unit.entity_id:
            for line in unit.upgrade_lines:
                # Insertion sort our upgrade lines
                if line in upgrade_lines:
                    line_num = unit.upgrade_lines[line]
                    line_list = upgrade_lines[line]
                    insert_point = 0
                    while insert_point < len(line_list) and line_list[insert_point].upgrade_lines[line] < line_num:
                        insert_point += 1
                    line_list.insert(insert_point, unit)
    return upgrade_lines     

def build_unit_upgrade_graph(unit):
    tree = graphviz.Digraph(name='upgrade_tree', strict=True)
    tree.subgraph(graph=build_age_trunk())
    upgrade_lines = find_unit_upgrade_lines(units[unit])
    age_blocks = []
    for i in range(11):
        age_blocks.append(set())
    for line in upgrade_lines:
        line_list = upgrade_lines[line]
        for i in range(len(line_list)):
            # Link the upgrade line to all options in the next age where any one appears
            # It would be very cool if we had them also connect past things where
            # not all age variants have an upgrade, but that's more work to identify.
            link_age = 0
            for potential_link in line_list[i:]:
                if potential_link.age > line_list[i].age:
                    if link_age == 0:
                        link_age = potential_link.age
                    elif link_age < potential_link.age:
                        break
                    # If we didn't bail out, draw the edge.
                    tree.edge(line_list[i].entity_id, potential_link.entity_id)
            # Link to techs, and group techs
            cluster_name = 'cluster_age'+str(line_list[i].age)
            with tree.subgraph(name=cluster_name) as c:
                c.node(line_list[i].entity_id)
                for tech in line_list[i].unlocked_by:
                    c.node(tech)
                    tree.edge(tech, line_list[i].entity_id)
                    if tech in tech_ages:
                        for age in tech_ages[tech]:
                            tree.edge(age, tech)
                    else:
                        tree.edge('TECHAGE'+str(line_list[i].age), tech)
    return tree
