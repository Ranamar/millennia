import graphviz
import millennia_data
# from pprint import pprint as pretty_print

tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects = millennia_data.load_data()

#TODO: Call this from build_tech_graph() if we're not deprecating that.
def build_age_trunk(tree, spacing='4', cluster_ages=False):
    trunk_name = 'cluster_agealign'
    with tree.subgraph(name=trunk_name) as age_align:
        # Space the age tags out by our spacing interval.
        age_align.attr('edge', minlen=spacing)
        age_align.attr('edge', style='invis')
        age_align.attr('graph', style='invis')
        # Create non-tech nodes, one per age, to keep the rest of the tree from drifting sideways
        for age_num in range(1, 11):
            age_node_str = 'AGE_' + str(age_num)
            age_align.node(age_node_str, 'Age ' + str(age_num))
            if age_num > 1:
                age_align.edge('AGE_' + str(age_num - 1), age_node_str)
        age_subgraph_name = 'sub_'
        if cluster_ages:
            age_subgraph_name = 'cluster_' + age_subgraph_name
        # Because there are no parents to age 1, We won't get an edge from 'AGE_1' to 'TECHAGE1' later.
        # If we don't put age 1 in its own subgraph here, it ends up being globbed into age 2 in weird ways if we use clusters.
        with tree.subgraph(name=age_subgraph_name + 'TECHAGE0') as cluster:
            cluster.node('TECHAGE1')
            tree.edge('AGE_1', 'TECHAGE1', style='invis')
        for age, children in age_advances.items():
            # We're trying to build a main trunk box. These are not techs, but rather springs to be used to hold stuff together.
            # Fortunately, the non-trunk ages all have underscores in their name, so that's an easy way to get a unique starting point.
            # The one fly in this ointment is age 10, which has no base age.
            with tree.subgraph(name=age_subgraph_name+age) as cluster:
                cluster.attr('edge', minlen=spacing)
                if cluster_ages:
                    cluster.attr('graph', rank='same')
                for child in children:
                    cluster.edge(age, child)
                    age_num_string = str(millennia_data.get_age_from_tech(child))
                    tree.edge('AGE_' + age_num_string, child, style='invis')

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
    # tree.subgraph(graph=build_age_trunk())
    build_age_trunk(tree)
    upgrade_lines = find_unit_upgrade_lines(units[unit])
    # age_blocks = []
    # for i in range(11):
    #     age_blocks.append(set())
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
            # This was clustered at one point in the past, but we've solved the 
            cluster_name = 'age'+str(line_list[i].age)
            with tree.subgraph(name=cluster_name) as c:
                c.node(line_list[i].entity_id)
                for tech in line_list[i].unlocked_by:
                    c.node(tech)
                    tree.edge(tech, line_list[i].entity_id)
                    if tech in tech_ages:
                        for age in tech_ages[tech]:
                            tree.edge(age, tech)
                    else:
                        # Fallback in case we missed something.
                        # With barbarian and exploration cards removed, this should just be innovations.
                        tree.edge('TECHAGE'+str(line_list[i].age), tech)
    return tree
