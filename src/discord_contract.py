"""Discord Components V2 design-source contract — safe, no network or posting.

Official rules: https://docs.discord.com/developers/components/reference
- IS_COMPONENTS_V2 flag 32768, with content carried by Text Displays, not
  legacy message content/embeds.
- Link Button type=2 style=5 requires url and MUST NOT have custom_id.
- Media Gallery type=12 references a real attached PNG by attachment:// name.
- No unverified "top player" claims when faction player lines are incomplete.
"""
from __future__ import annotations
from collections import defaultdict
from urllib.parse import urlsplit

COMPONENTS_V2=1<<15
FACTIONS=("Lonestar","Valkyra","Manticore")
SITE_URL="https://ejronin.github.io/1ADAAR/"
TINTS={"Lonestar":0x465EFF,"Valkyra":0xEE4138,"Manticore":0x3EBA42}


def faction_leaders(match: dict) -> list[dict]:
    """Best *recorded kills in this match*, not role XP or all-time ranking.

    Requires a complete sanitized WARCON match player-line dataset.
    The implementation collector must explicitly certify completeness;
    absent/partial records yield no claimed leader.
    """
    if not (isinstance(match,dict) and match.get("verifiedCompleted") is True
            and match.get("playerLinesComplete") is True
            and isinstance(match.get("players"),list)):
        return []
    groups=defaultdict(dict)
    for player in match["players"]:
        if not isinstance(player,dict) or player.get("faction") not in FACTIONS:
            continue
        faction=player["faction"]
        key,name=player.get("key"),player.get("name")
        kills,deaths=player.get("kills"),player.get("deaths")
        if not (isinstance(key,str) and bool(key) and isinstance(name,str)
                and 0<len(name)<=100 and isinstance(kills,int) and not isinstance(kills,bool)
                and kills>=0 and isinstance(deaths,int) and not isinstance(deaths,bool)
                and deaths>=0):
            continue
        if key not in groups[faction]:
            groups[faction][key]={"name":name,"kills":0,"deaths":0}
        groups[faction][key]["kills"]+=kills
        groups[faction][key]["deaths"]+=deaths
    out=[]
    for faction in FACTIONS:
        cohort=list(groups[faction].values())
        if not cohort:
            continue
        maximum=max(row["kills"] for row in cohort)
        tied=sorted((x for x in cohort if x["kills"]==maximum),key=lambda x:x["name"].casefold())
        if len(tied)==1:
            out.append({"faction":faction,"name":tied[0]["name"],"kills":maximum,
                        "deaths":tied[0]["deaths"],"tie":False})
        else:
            out.append({"faction":faction,"name":None,"kills":maximum,
                        "tiedCount":len(tied),"tie":True})
    return out


def _plain(value: object, limit: int=75) -> str:
    s=str(value or "").replace("@","＠").replace("\r"," ").replace("\n"," ").strip()
    return s[:limit]


def build_design_recap(
    match:dict, *,
    dashboard_url: str=SITE_URL,
    attachment_filename: str="match-recap.png",
) -> dict:
    """Build a VALID Discord V2 message JSON. Artwork bytes uploaded separately."""
    if not (isinstance(match,dict) and match.get("verifiedCompleted") is True
            and isinstance(match.get("id"),int) and match["id"]>0):
        raise ValueError("No verified completed match: refusing recap")
    url=urlsplit(dashboard_url)
    if url.scheme!="https" or url.hostname!="ejronin.github.io" or not url.path.startswith("/1ADAAR/") or len(dashboard_url)>512:
        raise ValueError("Dashboard link must be approved first-party GitHub Pages HTTPS URL")
    if not (isinstance(attachment_filename,str) and attachment_filename=="match-recap.png"):
        raise ValueError("Expected one verified exported PNG attachment")
    leaders=faction_leaders(match)
    if leaders:
        summary="**TOP RECORDED KILLS BY FACTION (THIS MATCH)**\n"+ "\n".join(
            f"**{r['faction']}** — "+(
                f"{_plain(r['name'])} · {r['kills']} K / {r['deaths']} D"
                if not r["tie"] else
                f"{r['tiedCount']} players tied · {r['kills']} K")
            for r in leaders
        )
    else:
        summary="**Faction standouts:** not shown until complete, verified match player lines are available."
    return {
        "username":"1ADAAR | WARDOGS",
        "allowed_mentions":{"parse":[]},
        "flags":COMPONENTS_V2,
        "components":[
            {"type":17,"accent_color":0x56CE71,"components":[
                {"type":10,"content":"## AFTER ACTION REPORT"},
                {"type":12,"items":[{"media":{"url":"attachment://"+attachment_filename},
                          "description":"Verified WARDOGS completed-match after-action image, with final faction scores and game map"}]},
                {"type":10,"content":summary},
                {"type":10,"content":"Next map and conditions will be posted separately only if WARCON confirms them."},
                {"type":1,"components":[{"type":2,"style":5,
                  "label":"Open in 1ADAAR","url":dashboard_url}]}
            ]}
        ]
    }
