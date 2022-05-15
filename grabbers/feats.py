import requests
import json

from bs4 import BeautifulSoup
from common import progress_bar
from enum import Enum
from pathlib import Path


PB = progress_bar.draw_progress_bar
FEATS_PAGE = "https://www.d20pfsrd.com/feats"
FEAT_STRUCTURE_CATEGORIES = [
    "Benefit",
    "Benefits",
    "Benefit(s)",
    "Normal",
    "Special",
    "Prerequisite",
    "Prerequisites",
    "Prerequisite(s)"
]
_BROKEN_FEATS = "Here's a list of links that could not be reached:\n"


class FeatsTables(Enum):
    """
    Feats that would be grabbed from tables
    """
    Achievement = "https://www.d20pfsrd.com/feats/achievement-feats"
    Combat = "https://www.d20pfsrd.com/feats/combat-feats"
    Critical = "https://www.d20pfsrd.com/feats/combat-feats/critical-feats/"
    General = "https://www.d20pfsrd.com/feats/general-feats"
    Grit = "https://www.d20pfsrd.com/feats/grit-feats"
    Item_Creation = "https://www.d20pfsrd.com/feats/item-creation-feats"
    Metamagic = "https://www.d20pfsrd.com/feats/metamagic-feats"
    Monster = "https://www.d20pfsrd.com/feats/monster-feats"
    Mythic = "https://www.d20pfsrd.com/alternative-rule-systems/mythic/mythic-feats/"
    Performance = "https://www.d20pfsrd.com/feats/performance-feats"
    Racial = "https://www.d20pfsrd.com/feats/racial-feats"
    Stare = "https://www.d20pfsrd.com/feats/racial-feats"
    Story = "https://www.d20pfsrd.com/feats/story-feats"
    Style = "https://www.d20pfsrd.com/feats/style-feats"
    Teamwork = "https://www.d20pfsrd.com/feats/teamwork-feats"


class FeatsSubpages(Enum):
    """
    Feats that would be grabbed from subpages
    """
    Animal_Companion = "https://www.d20pfsrd.com/feats/animal-companion-feats/"
    Blood_Hex = "https://www.d20pfsrd.com/feats/general-feats/blood-hex"
    Conduit = "https://www.d20pfsrd.com/feats/conduit-feats"
    Damnation = "https://www.d20pfsrd.com/feats/damnation-feats"
    Item_Mastery = "https://www.d20pfsrd.com/feats/item-mastery-feats"
    Panache = "https://www.d20pfsrd.com/feats/panache-feats"


class FeatsOther(Enum):
    """
    Special case for some feats.
    These feats do nat have corresponding pages for them,
    so they should be grabbed separately.
    """
    Animal_Familiar = "AnimalFamiliar_Feats"
    Meditation = "Meditation_Feats"
    Faction = "Faction_Feats"
    Hero_Point = "Hero_Point_Feats"


class FeatType(Enum):
    """
    Basically all feat categories present in game.
    """
    Achievement = "Table"
    Animal_Companion = "Subpages"
    Animal_Familiar = "Other"
    Blood_Hex = "Subpages"
    Combat = "Table"
    Conduit = "Subpages"
    Critical = "Table"
    Damnation = "Subpages"
    Faction = "Other"
    General = "Table"
    Grit = "Table"
    Hero_Point = "Other"
    Item_Creation = "Table"
    Item_Mastery = "Subpages"
    Metamagic = "Table"
    Meditation = "Other"
    Monster = "Table"
    Mythic = "Table"
    Panache = "Subpages"
    Performance = "Table"
    Racial = "Table"
    Stare = "Table"
    Story = "Table"
    Style = "Table"
    Teamwork = "Table"


def grab_feats_subpage_links(feat_link: FeatsSubpages) -> list:
    """
    Function that returns list of links for selected feat type

    :param feat_link: One of FeatsSubpages types
    :return: list of tuples ("url_to_feat", "feat_name")
    """
    r_top = requests.get(feat_link.value)
    subpages = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(name="ul", class_="ogn-childpages")
    result = []

    for child in subpages.children:
        link = child.find("a")
        result.append((link["href"], feat_link.name))

    return result


def grab_feats_tables_links(feat_link: FeatsTables) -> list:
    """
    Function that returns list of links for selected feat type

    :param feat_link: One of FeatsTables types
    :return: list of tuples ("url_to_feat", "feat_name")
    """
    r_top = requests.get(feat_link.value)
    content = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(class_="article-content")

    if content.find(name="p", class_="divider"):
        content.find("table").decompose()

    tables = content.find_all("table")
    result = []

    for table in tables:
        if table.tbody:
            rows = table.tbody.find_all("tr")
            for row in rows:
                link = row.find("a")
                if link:
                    href = link["href"] if link["href"][:5] == "https" else \
                        "https://www.d20pfsrd.com/feats/" + link["href"]
                    result.append((href, feat_link.name))

    return result


def grab_feats_other_links(feat_type: FeatsOther) -> list:
    """
    Function that returns list of links for selected feat type

    :param feat_type: One of FeatsOther types
    :return: list of tuples ("url_to_feat", "feat_name")
    """
    r_top = requests.get(FEATS_PAGE)
    body = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(class_="article-content")
    category = body.find(name="span", id=feat_type.value).parent.parent
    category.h4.decompose()
    links = category.find_all("a")
    result = []

    for link in links:
        result.append((link["href"], feat_type.name))

    return result


def get_all_feats() -> None:
    global _BROKEN_FEATS
    result = []

    # with alive_bar(len(FeatsTables),
    #                title=f"Finding links pt 1",
    #                force_tty=True) as bar:
    # for type_ in PB(FeatsTables, prefix="Finding links pt 1"):
    #     result += grab_feats_tables_links(type_)
            # bar()
    result += grab_feats_tables_links(FeatsTables.General)

    # with alive_bar(len(FeatsSubpages),
    #                title=f"Finding links pt 2",
    #                force_tty=True) as bar:
    # for type_ in PB(FeatsSubpages, prefix="Finding links pt 2"):
    #     result += grab_feats_subpage_links(type_)
            # bar()

    # with alive_bar(len(FeatsOther),
    #                title=f"Finding links pt 3",
    #                force_tty=True) as bar:
    # for type_ in PB(FeatsOther, prefix="Finding links pt 2"):
    #     result += grab_feats_other_links(type_)
            # bar()

    # Path("./results/feats").mkdir(parents=True, exist_ok=True)
    # with alive_bar(len(result),
    #                title=f"Grabbing feats",
    #                force_tty=True,
    #                stats=True) as bar:
    #     for link, type_ in result:
    #         feat = feat_presentation(link, type_)
    #         bar()
    #         file_path = Path(f"./results/feats/{type_}/{feat['Name']}.json")
    #         with open(file_path, mode="x") as f:
    #             feat = json.dumps(feat)
    #             f.write(feat)

    # with alive_bar(len(result),
    #                title=f"Grabbing feats",
    #                force_tty=True,
    #                stats=True) as bar:
    for link, type_ in PB(result, prefix="Grabbing feats"):
        feat = feat_presentation(link, type_)
    print()
    print(_BROKEN_FEATS)
    _BROKEN_FEATS = "Here's a list of links that could not be reached:\n"
            # bar()
            # print(json.dumps(feat, indent=4))


def feat_presentation(feat_link: str, feat_type: str) -> dict:
    """
    type Feat struct {
       Name          string
       Type          string
       Benefit       string
       Description   string
       Normal        string
       Special       string
       Source        string
       SourceLink    string
       Link          string
       Prerequisites []Prerequisite
    }
    """
    feat = {}

    r = requests.get(feat_link, timeout=10.0)
    if r.status_code == 404:
        page = BeautifulSoup(r.text, "html.parser").find("article")
        correct_link = page.find("a")
        if correct_link:
            correct_link = correct_link["href"]
            r = requests.get(correct_link, timeout=10.0)

    if not r:
        _log_broken_feats(feat_link)
        return feat

    page = BeautifulSoup(r.text, "html.parser").find("article")
    article = page.find(class_="article-content")

    feat["Name"] = page.h1.get_text()
    feat["Type"] = feat_type
    feat["Link"] = feat_link

    feat["Description"] = ""
    description = article.find(class_="description")
    if description:
        feat["Description"] = description.extract().get_text()

    feat["Source"] = ""
    feat["SourceLink"] = ""
    source_section = article.find(class_="section15")
    if source_section:
        source_link_tag = article.find(class_="section15").find("a")
        source_text = article.find(class_="section15").get_text()
        space = source_text.find(" ")

        source = source_link_tag.get_text() if \
            source_link_tag else source_text[:space]
        source_link = source_link_tag["href"] if source_link_tag else ""

        feat["Source"] = source
        feat["SourceLink"] = source_link

        source_section.decompose()

    tag_class = ""
    for tag in article.find_all("p"):
        if tag.b:
            tag_class = tag.b.get_text() if tag.b.get_text() in \
                                            FEAT_STRUCTURE_CATEGORIES else \
                                                "Special"
            tag_class = "Prerequisites" if \
                tag_class.startswith("Prerequisite") else tag_class
            tag_class = "Benefit" if \
                tag_class.startswith("Benefit") else tag_class

        tag["class"] = tag_class

    feat["Prerequisites"] = []
    prerequisites = article.find(class_="Prerequisites")
    if prerequisites:
        prerequisites = prerequisites.contents[2:]
        prerequisites = "".join(str(item) for item in prerequisites)
        # prerequisites = prerequisites.get_text()
        prerequisites = prerequisites[:-1] if prerequisites.endswith(".") \
            else prerequisites
        feat["Prerequisites"] = _parse_prerequisites(prerequisites)

    benefit = ""
    benefit_tags = article.find_all(class_="Benefit")
    for tag in benefit_tags:
        benefit += tag.get_text()
        benefit += " "
    feat["Benefit"] = benefit[9:] if \
        benefit.lower().startswith("benefit: ") else benefit

    normal = ""
    normal_tags = article.find_all(class_="Normal")
    for tag in normal_tags:
        normal += tag.get_text()
        normal += " "
    feat["Normal"] = normal[8:] if \
        normal.lower().startswith("normal: ") else normal

    special = ""
    special_tags = article.find_all(class_="Special")
    for tag in special_tags:
        special += tag.get_text()
        special += " "
    feat["Special"] = special[9:] if \
        special.lower().startswith("special: ") else special

    return feat


def _parse_prerequisites(prerequisites: str) -> list:
    result = []
    prereq_list = [p.strip().split(",") for p in prerequisites.split(";")]
    prereq_list = [i[j].strip() for i in prereq_list for j, k in enumerate(i)]
    skip = False
    for count, prereq in enumerate(prereq_list):
        if skip:
            skip = False
            continue
        if count < (len(prereq_list)-1) and \
                prereq_list[count+1].startswith("or"):
            skip = True
            temp = {"MultiPrerequisite": []}
            temp["MultiPrerequisite"].append(
                _get_prereq_type_value(prereq_list[count])
            )
            temp["MultiPrerequisite"].append(
                _get_prereq_type_value(prereq_list[count+1])
            )
            result.append(temp)
            continue

        result.append(_get_prereq_type_value(prereq))

    return result


def _log_broken_feats(link: str) -> None:
    global _BROKEN_FEATS
    _BROKEN_FEATS += link
    _BROKEN_FEATS += "\n"


def _get_prereq_type_value(prereq: str) -> dict:
    result = {}
    feat_type = ""
    feat_name = ""
    parsed_prereq = BeautifulSoup(prereq, "html.parser")
    prereq_link = parsed_prereq.a
    if prereq_link:
        # 25 is number of characters in https://www.d20pfsrd.com/
        href = prereq_link["href"][25:]
        feat_type = href[:href.find("/")]
        feat_name = prereq_link.get_text()
    prereq = parsed_prereq.get_text()


    if prereq.lower().endswith(" class feature"):
        result["ClassFeaturePrerequisite"] = prereq[:-14]
        return result

    if prereq.lower().startswith("str ") or \
            prereq.lower().startswith("strength "):
        space = prereq.find(" ")
        result["StrPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("dex ") or \
            prereq.lower().startswith("dexterity "):
        space = prereq.find(" ")
        result["DexPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("con ") or \
            prereq.lower().startswith("constitution "):
        space = prereq.find(" ")
        result["ConPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("int ") or \
            prereq.lower().startswith("intelligence "):
        space = prereq.find(" ")
        result["IntPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("wis ") or \
            prereq.lower().startswith("wisdom "):
        space = prereq.find(" ")
        result["WisPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("cha ") or \
            prereq.lower().startswith("charisma "):
        space = prereq.find(" ")
        result["ChaPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("base attack bonus ") or \
            prereq.lower().startswith("bab "):
        space = prereq.rfind(" ")
        result["BabPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("caster level"):
        space = prereq.rfind(" ")
        result["CasterLvlPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("character level "):
        start_space = prereq.find(" ")
        end_space = prereq.rfind(" ")
        result["ClassLvlPrerequisite"] = {}
        result["ClassLvlPrerequisite"]["Class"] = prereq[:start_space]
        result["ClassLvlPrerequisite"]["Level"] = prereq[end_space+1:]
        return result

    if feat_type == "classes":
        end_space = prereq.rfind(" ")
        result["ClassLvlPrerequisite"] = {}
        result["ClassLvlPrerequisite"]["Class"] = feat_name
        result["ClassLvlPrerequisite"]["Level"] = prereq[end_space + 1:]

    if prereq.startswith("Acrobatics "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["AcrobaticsPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Appraise "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["AppraisePrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Bluff "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["BluffPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Climb "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["ClimbPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Craft "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["BluffPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Diplomacy "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["DiplomacyPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("disable device "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["DisableDevicePrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Disguise "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["BluffPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("escape artist "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["EscapeArtistPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Fly "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["FlyPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("handle animal "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["HandleAnimalPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Heal "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["HealPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Intimidate "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["IntimidatePrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("arcana") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeArcanaPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("dungeoneering") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeDungeoneeringPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("engineering") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeEngineeringPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("geography") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeGeographyPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("history") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeHistoryPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("local") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeLocalPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("nature") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeNaturePrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("nobility") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeNobilityPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("planes") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgePlanesPrerequisite"] = prereq[space + 1:]
        return result

    if prereq.startswith("Knowledge ") and \
            (prereq.lower().find("religion") != -1):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["KnowledgeReligionPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Linguistics "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["LinguisticsPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Perception "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["PerceptionPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Perform "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["PerformPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Profession "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["ProfessionPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Ride "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["RidePrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("sense motive "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["SenseMotivePrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("sleight of hand "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["SleightOfHandPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Spellcraft "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["SpellcraftPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Stealth "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["StealthPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Survival "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["SurvivalPrerequisite"] = prereq[space+1:]
        return result

    if prereq.startswith("Swim "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["SwimPrerequisite"] = prereq[space+1:]
        return result

    if prereq.lower().startswith("use magic device "):
        if prereq.endswith(" ranks"):
            prereq = prereq[:-6]
        if prereq.endswith(" rank"):
            prereq = prereq[:-5]
        space = prereq.rfind(" ")
        result["UseMagicDevicePrerequisite"] = prereq[space+1:]
        return result

    if feat_type == "feats":
        result["FeatPrerequisite"] = feat_name
        return result

    if feat_type == "races" or feat_type == "bestiary":
        result["RacePrerequisite"] = prereq
        return result

    result["SpecialPrerequisite"] = prereq
    return result
