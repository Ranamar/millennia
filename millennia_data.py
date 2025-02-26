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
    'TECHAGE2':['MESSENGERS', 'MOUNDBUILDERS', 'OLYMPICLEGACY', 'RAIDER',
                'EARLYSEA', 'GODKINGDYNASTY','RITUALHUNTERS'],
    'TECHAGE4': ['CHIVALRY', 'CRUSADERS', 'EXPLORERS', 'MACHINERY', 'TRADERS',
                 'THEOLOGIANS', 'SHOGUNATE', 'SIEGEMASTERS'],
    'TECHAGE6': ['COLONIALISM', 'FIELDMARSHAL', 'GREATMASTERS', 'INVENTORS',
                 'MERCENARIES', 'WARRIORPRIESTS', 'SCHOLARS', 'SULTANS'],
    'TECHAGE8': ['BANKING', 'FLOWERCHILD', 'MEDIACONGLOMERATE', 'MODERNIZATION',
                 'POLITICALSCIENCE', 'POPCULTURE', 'SILICONVALLEY', 'SPACEAGENCY',
                 'SPECIALOPERATIONS']
}
age_governments = {
    'TECHAGE3': ['GOVKINGDOM', 'GOVIMPERIALDYNASTY'],
    'TECHAGE5': ['GOVEMPIRE', 'GOVMONARCHY', 'GOVREPUBLIC'],
    'TECHAGE8': ['GOVAUTOCRATIC', 'GOVCOMMUNIST', 'GOVDEMOCRATICREPUBLIC',
                 'GOVFUNDAMENTALIST'],
}
units = {}
improvements = {}
buildings = {}
projects = {}

error_cards = {}
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
    
    def add_upgrade_line(self, data):
        upgrade = data[0].split('-')
        self.upgrade_lines[upgrade[1]] = data[1]
    
    def add_unlock(self, tech):
        self.unlocked_by.append(tech)
    
    def parse_attribute(self, data):
        #TODO: ConstructionCost, probably other things
        if data[0] == 'FilterAge':
            self.age = int(data[1])
        elif data[0].startswith('UpgradeLine'):
            self.add_upgrade_line(data)
        else:
            return False
        return True
    
    def parse_data(self, data):
        for entry in data:
            # See if we can parse out something special,
            # then just shove it in the data dict if not.
            parsed = entry.split(',')
            if not self.parse_attribute(parsed):
                self.data[parsed[0]] = parsed[1]

class Unit(Entity):
    def __init__(self, entity_id):
        super().__init__(entity_id)

class Improvement(Entity):
    def __init__(self, entity_id):
        super().__init__(entity_id)
        self.consumes = {}
        self.produces = {}
    
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
    #TODO: This doesn't work for spirits or governments as currently stored.
    age_match = re.match(age, 'TECHAGE([0-9]+)')
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
            if name in error_cards:
                error_cards[name].append((card, errors))
            else:
                error_cards[name] = [(card, errors)]

def parse_unit_data(unit, data):
    if unit in units:
        get_unit(unit).parse_data(data)
    else:
##        print('Skipped techless unit:', unit)
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

def load_data():
    print("Loading...")
    print("Unlocks")
    unlock_dir = r'C:\Users\rhalstea\projects\millennia\textassets\unlocks'
    for filename in os.listdir(unlock_dir):
        load_unlocks(os.path.join(unlock_dir, filename))
    print("Entities")
    entity_dir = r'C:\Users\rhalstea\projects\millennia\textassets\entities'
    for filename in os.listdir(entity_dir):
        load_entities(os.path.join(entity_dir, filename))
    print("done.")
    ##print("results:")
    ##print("units:")
    ##pretty_print(units)
    ##print("improvements:")
    ##pretty_print(improvements)
    ##print("buildings:")
    ##pretty_print(buildings)
    ##print("projects:")
    ##pretty_print(projects)
    ##print("ages for techs:")
    ##pretty_print(tech_ages)
    print("Errored cards:")
    pretty_print(error_cards)
    print("Errored entities:")
    pretty_print(error_entities)
    ##print("Blank entities:")
    ##pretty_print(blank_entities)
    return (tech_ages, age_advances, age_spirits, age_governments, units, improvements, buildings, projects)
