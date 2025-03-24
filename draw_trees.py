import graphviz
import millennia_data
from pprint import pprint as pretty_print

tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects = millennia_data.load_data()

#TODO: Call this from build_tech_graph() if we're not deprecating that.
def build_age_trunk(tree_name='upgrade_tree', spacing='4', cluster_ages=False):
    tree = graphviz.Digraph(name=tree_name, strict=True)
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
                for child in children:
                    cluster.edge(age, child)
                    age_num = millennia_data.get_age_from_tech(child)
                    tree.edge('AGE_' + str(age_num), child, style='invis')
    return tree

def attach_spirits_and_governments_to_ages(tree, spirits_and_governments):
    #TODO: We probably want to do (optional) clusters for these like the age trunk.
    for age, spirits in age_spirits.items():
        age_subgraph_name = 'sub_spirit_'
        # if cluster_ages:
        #     age_subgraph_name = 'cluster_' + age_subgraph_name
        with tree.subgraph(name=age_subgraph_name + age) as cluster:
            for spirit in spirits:
                if spirit in spirits_and_governments:
                    cluster.node(spirit)
                    tree.edge(age, spirit, style='invis')
    for age, governments in age_governments.items():
        age_subgraph_name = 'sub_government_'
        # if cluster_ages:
        #     age_subgraph_name = 'cluster_' + age_subgraph_name
        with tree.subgraph(name=age_subgraph_name + age) as cluster:
            for gov in governments:
                if gov in spirits_and_governments:
                    cluster.node(gov)
                    tree.edge(age, gov, style='invis')

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

#TODO: A parameter for node and/or edge formatting once we want to differentiate that between entity types.
def draw_upgrade_tech_tree(tree, upgrade_lines):
    non_age_unlocks = []
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
                    tree.edge(line_list[i].entity_id, potential_link.entity_id, color='red2')
            # Link to techs, and group techs
            # This was clustered at one point in the past, but we've solved the 
            cluster_name = 'age'+str(line_list[i].age)
            with tree.subgraph(name=cluster_name) as c:
                c.node(line_list[i].entity_id)
                # Invisible link from entity to the next age (except the last one)
                # so that we don't get things wandering away from their age
                if line_list[i].age < 10:
                    tree.edge(line_list[i].entity_id, 'AGE_' + str(line_list[i].age+1), style='invis')
                # Link techs
                for tech in line_list[i].unlocked_by:
                    c.node(tech)
                    tree.edge(tech, line_list[i].entity_id, color='blue2')
                    if tech in tech_ages:
                        for age in tech_ages[tech]:
                            tree.edge(age, tech)
                            if not age.startswith('TECHAGE'):
                                non_age_unlocks.append(age)
                    else:
                        # Fallback in case we missed something.
                        # With barbarian and exploration cards removed, this should just be innovations.
                        tree.edge('TECHAGE'+str(line_list[i].age), tech)
    attach_spirits_and_governments_to_ages(tree, non_age_unlocks)

# For improvements and buildings, both of which only ever have one upgrade line
def find_single_upgrade_line(dictionary, upgrade_line):
    line = []
    for entity in dictionary.values():
        if upgrade_line in entity.upgrade_lines:
            line_num = entity.upgrade_lines[upgrade_line]
            insert_point = 0
            while insert_point < len(line) and line[insert_point].upgrade_lines[upgrade_line] < line_num:
                insert_point += 1
            line.insert(insert_point, entity)
    # This format is to match with other expectations
    return {upgrade_line: line}

def build_building_upgrade_graph(building):
    tree = build_age_trunk()
    upgrade_line = ""
    for line_name in buildings[building].upgrade_lines.keys():
        upgrade_line = line_name
    line = find_single_upgrade_line(buildings, upgrade_line)
    draw_upgrade_tech_tree(tree, line)
    return tree

def build_improvement_upgrade_graph(improvement):
    tree = build_age_trunk()
    upgrade_line = ""
    for line_name in improvements[improvement].upgrade_lines.keys():
        upgrade_line = line_name
    upgrade_lines = find_single_upgrade_line(improvements, upgrade_line)
    draw_upgrade_tech_tree(tree, upgrade_lines)
    return tree

def find_unit_upgrade_lines(search_unit):
    upgrade_lines = {}
    # It's just easier to do if we know we have at least one 
    for line in search_unit.upgrade_lines:
        upgrade_lines[line] = [search_unit]
    for name, unit in units.items():
        if name != search_unit.entity_id:
            for line in unit.upgrade_lines:
                # Insertion sort our upgrade lines as we find entries.
                # If we were worried about efficiency, this could use a binary search insert.
                if line in upgrade_lines:
                    line_num = unit.upgrade_lines[line]
                    line_list = upgrade_lines[line]
                    insert_point = 0
                    while insert_point < len(line_list) and line_list[insert_point].upgrade_lines[line] < line_num:
                        insert_point += 1
                    line_list.insert(insert_point, unit)
    return upgrade_lines     

def build_unit_upgrade_graph(unit):
    tree = build_age_trunk()
    upgrade_lines = find_unit_upgrade_lines(units[unit])
    draw_upgrade_tech_tree(tree, upgrade_lines)
    return tree
