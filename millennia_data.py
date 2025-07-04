import os
import xmltodict
from pprint import pprint as pretty_print
import re

tech_ages = {}
# This might be able to be generated from the data files
age_advances = {
    'TECHAGE1':['TECHAGE2'],
    'TECHAGE2':['TECHAGE3', 'TECHAGE3_HEROES', 'TECHAGE3_CRISISBLOOD'],
    'TECHAGE3':['TECHAGE4', 'TECHAGE4_MONUMENTS', 'TECHAGE4_CRISISPLAGUE'],
    'TECHAGE4':['TECHAGE5', 'TECHAGE5_DISCOVERY', 'TECHAGE5_CRISISINTOLERANCE',
                'TECHAGE5_VICTORYCONQUEST'],
    'TECHAGE5':['TECHAGE6', 'TECHAGE6_ALCHEMY', 'TECHAGE6_CRISISHERESY'],
    'TECHAGE6':['TECHAGE7','TECHAGE7_AETHER', 'TECHAGE7_CRISISIGNORANCE',
                'TECHAGE7_ATOM', 'TECHAGE7_VICTORYHARMONY'],
    'TECHAGE6_CRISISHERESY': ['TECHAGE7_CRISISOLDONES'],
    'TECHAGE7':['TECHAGE8', 'TECHAGE8_UTOPIA', 'TECHAGE8_CRISISDYSTOPIA',
                'TECHAGE8_VICTORYGENERALS'],
    'TECHAGE8':['TECHAGE9', 'TECHAGE9_ECOLOGY', 'TECHAGE9_CRISISVISITORS', 'TECHAGE9_CRISISWASTELAND'],
    'TECHAGE9':['TECHAGE10_VICTORYARCHANGEL', 'TECHAGE10_VICTORYCOLONYSHIP',
                'TECHAGE10_VICTORYTRANSCENDENCE', 'TECHAGE10_VICTORYROGUEAI']
}
# This doesn't look like it can be generated from the data files
age_spirits = {
    'AGE_2':['MESSENGERS', 'MOUNDBUILDERS', 'OLYMPICLEGACY', 'RAIDER',
                'EARLYSEA', 'GODKINGDYNASTY','RITUALHUNTERS'],
    'AGE_4': ['CHIVALRY', 'CRUSADERS', 'EXPLORERS', 'MACHINERY', 'TRADERS',
                 'THEOLOGIANS', 'SHOGUNATE', 'SIEGEMASTERS'],
    'AGE_6': ['COLONIALISM', 'FIELDMARSHAL', 'GREATMASTERS', 'INVENTORS',
                 'MERCENARIES', 'WARRIORPRIESTS', 'SCHOLARS', 'SULTANS'],
    'AGE_8': ['BANKING', 'FLOWERCHILD', 'MEDIACONGLOMERATE', 'MODERNIZATION',
                 'POLITICALSCIENCE', 'POPCULTURE', 'SILICONVALLEY', 'SPACEAGENCY',
                 'SPECIALOPERATIONS']
}
age_governments = {
    'AGE_3': ['GOVKINGDOM', 'GOVIMPERIALDYNASTY'],
    'AGE_5': ['GOVEMPIRE', 'GOVMONARCHY', 'GOVREPUBLIC'],
    'AGE_8': ['GOVAUTOCRATIC', 'GOVCOMMUNIST', 'GOVDEMOCRATICREPUBLIC',
                 'GOVFUNDAMENTALIST'],
}
units = {}
improvements = {}
buildings = {}
projects = {}

error_cards = {}
def card_error(name, card, errors):
    if name in error_cards:
        error_cards[name].append((card, errors))
    else:
        error_cards[name] = [(card, errors)]

error_entities = []
blank_entities = []

def get_unit(name):
    if name not in units:
        units[name] = Unit(name)
    return units[name]

def get_building(name):
    if name not in buildings:
        buildings[name] = Building(name)
    return buildings[name]

def get_improvement(name):
    if name not in improvements:
        improvements[name] = Improvement(name)
    return improvements[name]

def get_project(name):
    if name not in projects:
        projects[name] = Project(name)
    return projects[name]

class Entity:
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.data = {}
        self.upgrade_lines = {}
        self.unlocked_by = []
        self.age = 0
        self.unknown_tags = set()
    
    def add_upgrade_line(self, data):
        upgrade = data[0].split('-')
        # We don't want to accidentally lexicographically sort our numbers!
        self.upgrade_lines[upgrade[1]] = int(data[1])
    
    def add_unlock(self, tech):
        if tech.startswith('EXPLORE-') or tech.startswith('BARBARIAN-'):
            # EXPLORE- cards are events when you find villages, so it's not actually a tech.
            # BARBARIAN- cards are for generating barbarians.
            return
        if tech not in self.unlocked_by:
            self.unlocked_by.append(tech)
        if self.age == 0:
            self.calculate_age()

    def is_unlockable(self):
        return len(self.unlocked_by) > 0
    
    def parse_attribute(self, data):
        #TODO: ConstructionCost, probably other things
        if data[0] == 'FilterAge':
            self.age = int(data[1])
        elif data[0].startswith('UpgradeLine'):
            self.add_upgrade_line(data)
        else:
            return False
        return True
    
    def parse_tags(self, tags):
        for entry in tags:
            if not self.parse_tag(entry):
                self.unknown_tags.add(entry)

    def parse_tag(self, tag: str) -> bool:
        return False
    
    def calculate_age(self):
        self.age = get_age_from_tech(self.unlocked_by[0])
    
    def parse_data(self, data):
        for entry in data:
            # See if we can parse out something special,
            # then just shove it in the data dict if not.
            parsed = entry.split(',')
            if not self.parse_attribute(parsed):
                self.data[parsed[0]] = parsed[1]
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'entity ' + self.entity_id + ' - age: ' + str(self.age) + '; unlocked by: ' + str(self.unlocked_by) + '; upgrade lines: ' + str(self.upgrade_lines)

class Unit(Entity):
    def __init__(self, entity_id):
        super().__init__(entity_id)

class Improvement(Entity):
    NOTABLE_TAGS = frozenset({'Factory', 'Modernization', 'AetherImprovement', 'Furnace'})

    def __init__(self, entity_id):
        super().__init__(entity_id)
        self.consumes = {}
        self.produces = {}
        self.build_requirements = set()
        self.improvement_category = ''
        self.town_bonus = set()
        self.notable_tags = set()
        self.outpost_core = False
    
    def parse_attribute(self, data):
        #TODO: WorkableRes (produces currencies), (extra) worker slots, probably other things
        #TODO: Work vs. non-work (i.e. passive production)
        if data[0].startswith('WorkableConvertGoods'):
            conversion = data[0].split('-')
            self.consumes[conversion[1]] = conversion[2]
            self.produces[conversion[3]] = data[1]
        elif data[0].startswith('WorkableGoodsSpecial'):
            # WorkableGoodsSpecial-TileProduction-[PT_something]
            product = data[0].split('-')[2]
            self.produces[product] = data[1]
        elif data[0].startswith('WorkableGoods'):
            product = data[0][len('WorkableGoods'):]
            self.produces[product] = data[1]
        else:
            # Try common attribute parsing from the parent class
            return super().parse_attribute(data)
        return True
    
    def parse_tag(self, tag: str) -> bool:
        # There's both BuildRequirementTag for terrain types and BuildRequirementTile for goods
        # Perhaps in the future these should be split? but for now we're keeping them together.
        if tag.startswith('BuildRequirementTag'):
            parsed = tag.split('-')
            self.add_build_requirement(parsed[1])
        elif tag == 'OutpostCore':
            self.outpost_core = True
            # I'm trying not to have anything with truly no build requirements
            self.add_build_requirement('OutpostCore')
        elif tag.startswith('ImprovementCategory'):
            parsed = tag.split('-')
            self.improvement_category = parsed[1]
        elif tag.endswith('TownBonus'):
            self.town_bonus.add(tag)
            if tag not in town_bonus_types:
                town_bonus_types.add(tag)
        elif tag in Improvement.NOTABLE_TAGS:
            self.notable_tags.add(tag)
        else:
            return super().parse_tag(tag)
        return True
    
    def add_build_requirement(self, req):
        # The plus character '+' causes trouble in URLs, so we're stripping it out of build requirements that use it.
        req = req.lstrip('+')
        self.build_requirements.add(req)
        if req not in improvement_terrain_possible_requirements:
            improvement_terrain_possible_requirements.add(req)
    
    def __str__(self):
        repr = 'entity ' + self.entity_id + ' - age: ' + str(self.age) + ', unlocked by: ' + str(self.unlocked_by)
        if len(self.town_bonus) > 0:
            repr += ', town bonuses: ' + str(self.town_bonus)
        if len(self.notable_tags) > 0:
            repr += ', notable tags: ' + str(self.notable_tags)
        repr += ', upgrade lines: ' + str(self.upgrade_lines) + ', Terrain: ' + str(self.build_requirements) + ', Category: ' + str(self.improvement_category)
        return repr

class Building(Entity):
    def __init__(self, entity_id):
        super().__init__(entity_id)

class Project(Entity):
    def __init__(self, entity_id):
        super().__init__(entity_id)

def add_tech_age(tech, age):
    if tech in tech_ages:
        tech_ages[tech].append(age)
    else:
        tech_ages[tech] = [age]

def get_age_from_tech(tech):
    # Extract an age number for a tech
    # Governments and spirits are a bit convoluted because it's not in the name.
    age_match = re.match('(INNOVATION-)?TECHAGE([0-9]+)', tech)
    if age_match:
        return int(age_match.group(2))
    elif tech.startswith('GOV'):
        for age, govs in age_governments.items():
            if tech in govs:
                return get_age_from_baseage(age)
    else:
        spirit_match = re.match('([A-Z]+)-', tech)
        if spirit_match:
            spirit = spirit_match.group(1)
            for age, spirits in age_spirits.items():
                if spirit in spirits:
                    return get_age_from_baseage(age)
        else:
            return 0
    print('Somehow reached end of age calculation with no result! ' + tech)
    return 0

def get_age_from_baseage(age):
    age_match = re.match('AGE_([0-9]+)', age)
    if age_match:
        return int(age_match.group(1))
    else:
        return 0

def load_unlocks(filename):
    print(filename)
    file = open(filename, "rb")
    data = xmltodict.parse(file, force_list=('ACardChoice','Effects','ACardEffect'))
    file.close()
    deck = data['ADeck']
    name = deck['DeckName']
##    print("Name:", name)
    for card in deck['Definition']['ACard']:
        errors = []
        unlock_tech = False
        if 'ID' in card:
##            print(card['ID'])
            if not 'Subtype' in card:
                # These seem to be administrivia like updating the draft ability
                # and therefore should probably be skipped without error.
                # The one exception is shared techs, which the ID check catches.
                continue
            if not 'Choices' in card or card['Choices'] is None:
                errors.append("No choices")
            else:
                for choice in card['Choices']['ACardChoice']:
                    if not 'Effects' in choice:
                        # There are two instances of this.
                        # They seem to be sub-abilities that happen to be in decks that do unlocks.
                        # This might be expected? So we're not reporting it right now
                        ##errors.append("Effects not present")
                        continue
                    for effect_container in choice['Effects']:
                        if not effect_container is None:
                            # This is to prevent doubled entries in the unlock list
                            unlocks = []
                            for effect in effect_container['ACardEffect']:
                                if effect['EffectType'].startswith('CE_Unlock'):
                                    # We unlocked something, so mark the card as an unlock tech.
                                    unlock_tech = True
                                    effect_unlock = effect['Payload']
                                    # Store unlock in the relevant dict
                                    # We're very fortunate that they put these tags on their entities!
                                    if effect_unlock.startswith('UNIT_'):
                                        if not effect_unlock in unlocks:
                                            get_unit(effect_unlock).add_unlock(card['ID'])
                                            unlocks.append(effect_unlock)
                                    elif effect_unlock.startswith('B_TILEIMP_'):
                                        if not effect_unlock in unlocks:
                                            get_improvement(effect_unlock).add_unlock(card['ID'])
                                            unlocks.append(effect_unlock)
                                    elif effect_unlock.startswith('B_'):
                                        if not effect_unlock in unlocks:
                                            get_building(effect_unlock).add_unlock(card['ID'])
                                            unlocks.append(effect_unlock)
                                    elif effect_unlock.startswith('PROJECT_'):
                                        if not effect_unlock in unlocks:
                                            get_project(effect_unlock).add_unlock(card['ID'])
                                            unlocks.append(effect_unlock)
                                    elif effect_unlock.startswith('DS_PROJECT_'):
                                        # Deep sea project (there's only one)
                                        if not effect_unlock in unlocks:
                                            get_project(effect_unlock).add_unlock(card['ID'])
                                            unlocks.append(effect_unlock)
                                    elif effect_unlock.startswith('CONCEPT_'):
                                        # These seem to be tutorial cards for late-game contests
                                        # Maybe track these later, but I don't think we'll care.
                                        pass
                                    elif effect_unlock.startswith('DomainSpecialization'):
                                        # I have no idea what this is, but they're kinds of things that get tutorial cards
                                        # and it doesn't seem like they'll matter for tech trees.
                                        pass
                                    else:
                                        errors.append("unidentifiable unlock: " + effect['Payload'])
            if unlock_tech:
                any_techs = True
                if card['Subtype'] == 'CST_Tech':
                    add_tech_age(card['ID'], name)
                elif card['Subtype'] == 'CST_Event':
                    #TODO maybe care sometime?
                    # This is stuff like buildings unlocked by Innovation events.
                    pass
                else:
                    errors.append("Unidentified unlock subtype")
        else:
            # No ID on card seems to mostly happen when a variant age imports a tech from the standard age
            if 'Import' in card:
                add_tech_age(card['Import'], name)
            else:
                errors.append("Missing ID")
        if len(errors) > 0:
            card_error(name, card, errors)

def get_unlockable_entity_ids(dictionary):
    def unlockable_entity(dictionary_item):
        return dictionary_item[1].is_unlockable()
    return sorted(map(lambda item: item[0], filter(unlockable_entity, dictionary.items())))

improvement_terrain_possible_requirements = set()
def get_improvement_terrains() -> list[str]:
    # Terrain restrictions are OR, not AND, fortunately!
    return sorted(improvement_terrain_possible_requirements)

def get_notable_tags() -> list[str]:
    return sorted(Improvement.NOTABLE_TAGS)

town_bonus_types = set()
def get_town_bonuses() -> list[str]:
    return sorted(town_bonus_types)

def get_improvement_with_unknown_tag(tag: str) -> list[Improvement]:
    selected = []
    for improvement in improvements.values():
        if tag in improvement.unknown_tags:
            selected.append(improvement)
    return selected

def parse_unit_data(unit, data):
    if unit in units:
        get_unit(unit).parse_data(data)
    else:
##        print('Skipped techless unit:', unit)
        pass

def parse_improvement_tags(imp, tags):
    if imp in improvements:
        get_improvement(imp).parse_tags(tags)
    else:
##        print('Skipped techless improvement:', imp)
        pass

def parse_improvement_data(imp, data):
    if imp in improvements:
        get_improvement(imp).parse_data(data)
    else:
##        print('Skipped techless improvement:', imp)
        pass

def parse_building_data(building, data):
    if building in buildings:
        get_building(building).parse_data(data)
    else:
##        print('Skipped techless building:', building)
        pass

def load_entities(filename):
    print(filename)
    file = open(filename, "rb")
    data = xmltodict.parse(file, force_list=('EntityInfo','Data'))
    file.close()
    for entity in data['EntityInfoList']['EntityInfo']:
        ent_id = entity['ID']
        if ent_id.startswith('UNIT_'):
            if 'StartingData' in entity:
                parse_unit_data(ent_id, entity['StartingData']['Data'])
            elif 'Import' in entity:
                # Inherits everything from a parent - there are a couple units like this.
                blank_entities.append(entity)
            else:
                error_entities.append((entity, 'No Starting Data or Import'))
        elif ent_id.startswith('B_TILEIMP_'):
            if 'StartingData' in entity:
                parse_improvement_data(ent_id, entity['StartingData']['Data'])
            elif 'Import' in entity:
                # Inherits everything from a parent - there are a couple units like this.
                blank_entities.append(entity)
            else:
                error_entities.append((entity, 'No Starting Data or Import'))
            if 'Tags' in entity:
                parse_improvement_tags(ent_id, entity['Tags']['Tag'])
        elif ent_id.startswith('B_'):
            if 'StartingData' in entity:
                parse_building_data(ent_id, entity['StartingData']['Data'])
            elif 'Import' in entity:
                # Inherits everything from a parent - there are a couple units like this.
                blank_entities.append(entity)
            else:
                error_entities.append((entity, 'No Starting Data or Import'))
        else:
            # not sure what would be here, but we can check to ensure we haven't missed any
            pass

def load_data(unlock_dir="txt_data/unlocks", entity_dir="txt_data/entities"):
    print("Loading...")
    print("Unlocks")
    for filename in os.listdir(unlock_dir):
        load_unlocks(os.path.join(unlock_dir, filename))
    print("Entities")
    for filename in os.listdir(entity_dir):
        load_entities(os.path.join(entity_dir, filename))
    print("done.")
    #print("results:")
    #print("units:")
    #pretty_print(units)
    # print("improvements:")
    # pretty_print(improvements)
    #print("buildings:")
    #pretty_print(buildings)
    #print("projects:")
    #pretty_print(projects)
    #print("ages for techs:")
    # pretty_print(tech_ages)
    if len(error_cards) > 0:
        print("Errored cards:")
        pretty_print(error_cards)
    if len(error_entities) > 0:
        print("Errored entities:")
        pretty_print(error_entities)
    #print("Blank entities:")
    #pretty_print(blank_entities)
    return (tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects)
