<p align="center">
  <img src="docs/assets/1ad-logo.svg" width="100" alt="1AD emblem">
</p>

# 1ADAAR
### OneAverageDan After-Action Report

**A home for the matches, players and stories behind the OneAverageDan WARDOGS Community Server.**

[Open 1ADAAR](https://ejronin.github.io/1ADAAR/) · [Find your stats](https://ejronin.github.io/1ADAAR/players.html) · [Match records on WARCON](https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches)

![Official WARDOGS game artwork](docs/assets/wardogs-official-hero.webp)

## What is 1ADAAR?

When a WARDOGS match ends, there's a lot more to remember than who won. There are the close fights, the players who had a good round, the maps that always seem to go one way, and the people who keep coming back.

I wanted a place where our community could look at those results after the match was over. That's what 1ADAAR is: **OneAverageDan After-Action Report**, a small, independent stats site built around our WARDOGS server.

It brings together the public records available through WARCON and makes them easier to explore. It also gives me a way to share completed-match recaps in Discord without sitting at a computer to run a bot.

## What you can see

### The matches we've played

The home page shows server information and a history of recorded completed matches. Each report is built from what WARCON actually saved: the map, factions, scores and other available match details.

[Browse match results](https://ejronin.github.io/1ADAAR/)

### Your own numbers

Player search is the quickest way to find a name in the available WARCON records. A player page brings together recorded career totals, wins, kills, deaths, K/D, playtime, recent matches and map or faction results where the source supports them.

The aim is to make the figures understandable, not to bury them in unexplained charts. A career total and a handful of recent matches tell different stories, so 1ADAAR keeps them separate.

[Find your stats](https://ejronin.github.io/1ADAAR/players.html)

### A look back at the week

The [weekly roundup](https://ejronin.github.io/1ADAAR/weekly.html) is the place for community highlights and saved weekly results. Reporting weeks run from Sunday noon to Sunday noon Eastern. A week with too little verified data shouldn't suddenly have a made-up champion. The numbers, awards and recap images need to come from matches the server actually recorded.

## How it works

WARCON collects the match and player information used by the site. GitHub Actions aims to check the public records about every ten minutes, prepares the data for the website and produces the recap artwork. GitHub Pages serves the finished pages. A Discord recap goes out only after WARCON has recorded a completed match with usable results.

That setup is intentional. **1ADAAR doesn't require a computer at home to stay online**, or a separate paid web server for its existing public dashboard. Most of the work happens during scheduled GitHub jobs, and the website reads the data they've already prepared.

It's also why the numbers aren't a live game feed. A refresh might run late, a public WARCON endpoint may temporarily be unavailable, and some details simply aren't recorded. The site shows the latest known observation instead of pretending every value is current.

## A note about the statistics

I would rather leave a number empty than show one that looks convincing but isn't supported.

The public leaderboard has a limited number of entries, match history only goes back as far as the records we've captured, and career snapshots start when 1ADAAR begins observing them. Activity by match start isn't the same as a player's time online. Those distinctions matter when comparing players or looking at trends.

There is a fictional player called **PlayerOne** in the design examples. It's there to test layouts and calculations, not to appear as a real community member or weekly winner.

The public site uses player lookup keys rather than showing SteamID64 values in its pages. Any later account-connected features will need to respect the player's own privacy choices.

## Where I'm taking it

The next design, **v1.1.0**, builds on the existing site rather than replacing it with a generic dashboard. The work focuses on clearer performance charts, a better map/faction view, the time-activity heatmap, the weekly podium, original 1AD artwork and more useful Discord recaps.

I'm also exploring an **optional** connection to [WARDOGS Tracker](https://wardogstracker.gg/stats) for players who choose to synchronize their own public game profiles. That could show the six role levels and XP, overall WARDOG level, career XP, and account cash or gold when the player allows it. It isn't part of the current WARCON match feed, and a player won't need it to see their normal 1ADAAR stats.

These improvements are still being implemented and reviewed. The [v1.1.0 design handoff](https://github.com/ejronin/1ADAAR/tree/design/v1.1.0-ia-handoff/design/v1.1.0) shows the planned screens; it doesn't mean everything in them has shipped.

## The project

1ADAAR is a community project for the OneAverageDan WARDOGS server, not an official BULKHEAD or WARDOGS service. The original 1AD, WARDOGS and faction artwork is used to identify the community and the game.

The site is built with Python, JavaScript, HTML, CSS and SVG, with GitHub Pages and Actions handling publication. I keep the technical details and earlier release decisions in the repository for anyone interested in how the data is collected or why certain features work the way they do.

**Project reference:** [v1.0.1 release notes](planning/V1.0.1.md) · [Weekly data rules](planning/WEEKLY_DATA_CONTRACT.md) · [Design and technical research](https://github.com/ejronin/1ADAAR/tree/design/v1.1.0-ia-handoff/design/v1.1.0/research)

---

*Built for the OneAverageDan WARDOGS community. The scoreboard is the end of a match, not the end of the story.*
