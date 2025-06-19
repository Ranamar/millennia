from bisect import insort
import graphviz
import millennia_data
from pprint import pprint as pretty_print

tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects = millennia_data.load_data()

# Wrapper class around the graphviz graph to facilitate unified formatting
# To reduce number of things that need to be touched, we're providing pass-through methods for rendering.
class UpgradeTechTreeGraph:
    def __init__(self, tree_name='upgrade_tree', spacing='4', format='svg', cluster_ages=False):
        self.spacing = spacing
        self.tree = graphviz.Digraph(name=tree_name, strict=True)
        self.format = format
        self.cluster_ages = cluster_ages
        self.build_age_trunk()
    
    def pipe(self):
        self.tree.format = self.format
        return self.tree.pipe()

    def render(self):
        self.tree.format = self.format
        return self.tree.render()

    def build_age_trunk(self):
        tree = self.tree
        tree.graph_attr.update(mclimit='2')
        trunk_name = 'cluster_agealign'
        with tree.subgraph(name=trunk_name) as age_align:
            # Space the age tags out by our spacing interval.
            age_align.edge_attr.update(style='invis', minlen=self.spacing)
            age_align.attr('graph', style='invis')
            # Create non-tech nodes, one per age, to keep the rest of the tree from drifting sideways
            for age_num in range(1, 11):
                age_node_str = 'AGE_' + str(age_num)
                age_align.node(age_node_str, 'Age ' + str(age_num))
                if age_num > 1:
                    age_align.edge('AGE_' + str(age_num - 1), age_node_str)
            age_subgraph_name = 'sub_'
            if self.cluster_ages:
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
                    cluster.attr('edge', minlen=self.spacing)
                    for child in children:
                        cluster.edge(age, child)
                        age_num = millennia_data.get_age_from_tech(child)
                        tree.edge('AGE_' + str(age_num), child, style='invis')

    def attach_spirits_and_governments_to_ages(self, spirits_and_governments):
        tree = self.tree
        for age, spirits in age_spirits.items():
            age_subgraph_name = 'sub_spirit_'
            if self.cluster_ages:
                age_subgraph_name = 'cluster_' + age_subgraph_name
            with tree.subgraph(name=age_subgraph_name + age) as cluster:
                for spirit in spirits:
                    if spirit in spirits_and_governments:
                        cluster.node(spirit)
                        tree.edge(age, spirit)
        for age, governments in age_governments.items():
            age_subgraph_name = 'sub_government_'
            # if cluster_ages:
            #     age_subgraph_name = 'cluster_' + age_subgraph_name
            with tree.subgraph(name=age_subgraph_name + age) as cluster:
                for gov in governments:
                    if gov in spirits_and_governments:
                        cluster.node(gov)
                        tree.edge(age, gov)

    #TODO: A parameter for node and/or edge formatting once we want to differentiate that between entity types.
    #      This could be attached to the containing class.
    def draw_upgrade_tech_tree(self, upgrade_lines):
        tree = self.tree
        non_age_unlocks = set()
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
                    c.node(line_list[i].entity_id, group=cluster_name)
                    # Invisible link from entity to the next age (except the last one)
                    # so that we don't get things wandering away from their age
                    if line_list[i].age < 10:
                        tree.edge(line_list[i].entity_id, 'AGE_' + str(line_list[i].age+1), style='invis')
                    # Link techs
                    for tech in line_list[i].unlocked_by:
                        c.node(tech, group=cluster_name)
                        tree.edge(tech, line_list[i].entity_id, color='blue2')
                        if tech in tech_ages:
                            for age in tech_ages[tech]:
                                tree.edge(age, tech)
                                if not age.startswith('TECHAGE'):
                                    non_age_unlocks.add(age)
                        else:
                            # Fallback in case we missed something.
                            # With barbarian and exploration cards removed, this should just be innovations.
                            tree.edge('TECHAGE'+str(line_list[i].age), tech)
        self.attach_spirits_and_governments_to_ages(non_age_unlocks)


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

# For improvements and buildings, both of which only ever have one upgrade line
def find_single_upgrade_line(dictionary, upgrade_line):
    line = []
    for entity in dictionary.values():
        if upgrade_line in entity.upgrade_lines:
            insort(line, entity, key=lambda e: e.upgrade_lines[upgrade_line])
    # This format is to match with cases where there are multiple upgrade lines.
    return {upgrade_line: line}

def extend_upgrade_lines_from_partial(dictionary: dict[str, millennia_data.Entity], upgrade_lines: dict[str, list[millennia_data.Entity]]):
    for entity in dictionary.values():
        for line_id, line_list in upgrade_lines.items():
            if line_id in entity.upgrade_lines:
                # We're just going to do this the inefficient way, because somehow bisect breaks but insort doesn't.
                if entity not in line_list:
                    insort(line_list, entity, key=lambda e: e.upgrade_lines[line_id])

def build_building_upgrade_graph(building):
    tree = UpgradeTechTreeGraph()
    upgrade_line = None
    for line_name in buildings[building].upgrade_lines.keys():
        upgrade_line = line_name
    line = {'default': [buildings[building]]}
    if upgrade_line is not None:
        line = find_single_upgrade_line(buildings, upgrade_line)
    pretty_print(line)
    tree.draw_upgrade_tech_tree(line)
    return tree

def build_improvement_upgrade_graph(improvement):
    tree = UpgradeTechTreeGraph()
    upgrade_line = None
    for line_name in improvements[improvement].upgrade_lines.keys():
        upgrade_line = line_name
    upgrade_lines = {'default': [improvements[improvement]]}
    if upgrade_line is not None:
        upgrade_lines = find_single_upgrade_line(improvements, upgrade_line)
    pretty_print(upgrade_lines)
    tree.draw_upgrade_tech_tree(upgrade_lines)
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
                # The bisect library makes it easy!
                if line in upgrade_lines:
                    line_list = upgrade_lines[line]
                    insort(line_list, unit, key=lambda u: u.upgrade_lines[line])
    if len(upgrade_lines) == 0:
        {'default': search_unit}
    return upgrade_lines     

def build_unit_upgrade_graph(unit):
    tree = UpgradeTechTreeGraph()
    upgrade_lines = find_unit_upgrade_lines(units[unit])
    pretty_print(upgrade_lines)
    tree.draw_upgrade_tech_tree(upgrade_lines)
    return tree

def get_improvements_for_terrain(required_attribute):
    print(required_attribute)
    improvement_lines = {}
    for id, imp in improvements.items():
        if required_attribute in imp.build_requirements:
            if len(imp.upgrade_lines) == 0:
                improvement_lines[id] = [imp]
            else:
                for line in imp.upgrade_lines.keys():
                    if line not in improvement_lines:
                        improvement_lines[line] = []
                    insort(improvement_lines[line], imp, key=lambda i: i.upgrade_lines[line])
    return improvement_lines

def build_terrain_upgrade_graph(terrain_reqs):
    tree = UpgradeTechTreeGraph()
    upgrade_lines = get_improvements_for_terrain(terrain_reqs)
    pretty_print(upgrade_lines)
    tree.draw_upgrade_tech_tree(upgrade_lines)
    return tree

def get_improvements_with_tag(required_attribute: str) -> dict[str, list[millennia_data.Improvement]]:
    print(required_attribute)
    improvement_lines = {}
    for id, imp in improvements.items():
        if required_attribute in imp.notable_tags:
            if len(imp.upgrade_lines) == 0:
                improvement_lines[id] = [imp]
            else:
                for line in imp.upgrade_lines.keys():
                    if line not in improvement_lines:
                        improvement_lines[line] = []
                    insort(improvement_lines[line], imp, key=lambda i: i.upgrade_lines[line])
    return improvement_lines

def build_tag_upgrade_graph(tag):
    tree = UpgradeTechTreeGraph()
    upgrade_lines = get_improvements_with_tag(tag)
    pretty_print(upgrade_lines)
    # TODO: Find a way to make this not illegible, probably by implementing some sort of stagger for children of a tech.
    #       Unfortunately, the way we construct these lists means it will take extra checking to notice when things share a tech.
    # extend_upgrade_lines_from_partial(improvements, upgrade_lines)
    # pretty_print(upgrade_lines)
    tree.draw_upgrade_tech_tree(upgrade_lines)
    return tree

