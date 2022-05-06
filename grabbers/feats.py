import requests
import json

from bs4 import BeautifulSoup
from enum import Enum


FEATS_PAGE = "https://www.d20pfsrd.com/feats"


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


def grab_feats_subpage_links(link: FeatsSubpages) -> list:
    r_top = requests.get(link.value)
    subpages = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(name="ul", class_="ogn-childpages")
    result = []

    for child in subpages.children:
        link = child.find("a")
        result.append(link["href"])

    return result


def grab_feats_tables_links(link: FeatsTables) -> list:
    r_top = requests.get(link.value)
    tables = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(class_="article-content").find_all("table")
    result = []

    for table in tables:
        rows = table.tbody.find_all("tr")
        for row in rows:
            link = row.find("a")
            result.append(link["href"])

    return result


def grab_feats_other_links(feat_type: FeatsOther) -> list:
    r_top = requests.get(FEATS_PAGE)
    body = BeautifulSoup(r_top.text, "html.parser")\
        .body.find(class_="article-content")
    category = body.find(name="span", id=feat_type.value).parent.parent
    category.h4.decompose()
    links = category.find_all("a")
    result = []

    for link in links:
        result.append(link["href"])

    return result
