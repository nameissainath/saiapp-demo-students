from fastapi import FastAPI, HTTPException

app = FastAPI(title="Cricket API", version="1.0.0")

PLAYERS = [
    {
        "id": 1,
        "name": "Virat Kohli",
        "country": "India",
        "role": "Batsman",
        "runs": 26400,
        "matches": 520,
    },
    {
        "id": 2,
        "name": "Joe Root",
        "country": "England",
        "role": "Batsman",
        "runs": 19800,
        "matches": 480,
    },
    {
        "id": 3,
        "name": "Pat Cummins",
        "country": "Australia",
        "role": "Bowler",
        "wickets": 280,
        "matches": 110,
    },
    {
        "id": 4,
        "name": "Babar Azam",
        "country": "Pakistan",
        "role": "Batsman",
        "runs": 11200,
        "matches": 310,
    },
    {
        "id": 5,
        "name": "Rashid Khan",
        "country": "Afghanistan",
        "role": "All-rounder",
        "wickets": 210,
        "runs": 1800,
        "matches": 240,
    },
]

NEWS = [
    {
        "id": 1,
        "title": "India wins the T20 series against Australia",
        "summary": "India clinched the series 3-2 with a thrilling final-over finish in Mumbai.",
        "published_at": "2026-06-24T18:30:00Z",
        "category": "Match Report",
    },
    {
        "id": 2,
        "title": "England announces squad for upcoming Test tour",
        "summary": "Young fast bowlers included as England rebuilds ahead of the Ashes.",
        "published_at": "2026-06-23T10:15:00Z",
        "category": "Team News",
    },
    {
        "id": 3,
        "title": "IPL auction highlights: record bids for all-rounders",
        "summary": "Several franchises spent heavily on versatile players during the mega auction.",
        "published_at": "2026-06-22T14:00:00Z",
        "category": "League",
    },
    {
        "id": 4,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
     {
        "id": 5,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
    {
        "id": 6,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
    {
        "id": 7,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
     {
        "id": 8,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
     {
        "id": 9,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
    {
        "id": 10,
        "title": "South Africa pace attack dominates day one",
        "summary": "Visitors reduced the hosts to 180/7 on a lively pitch in Cape Town.",
        "published_at": "2026-06-21T09:45:00Z",
        "category": "Match Report",
    },
]


@app.get("/")
def root():
    return {
        "message": "Cricket API",
        "endpoints": {
            "players": "/players",
            "news": "/news",
        },
    }


@app.get("/players")
def get_players():
    return {"count": len(PLAYERS), "players": PLAYERS}


@app.get("/players/{player_id}")
def get_player(player_id: int):
    player = next((p for p in PLAYERS if p["id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.get("/news")
def get_news():
    return {"count": len(NEWS), "news": NEWS}


@app.get("/news/{news_id}")
def get_news_item(news_id: int):
    item = next((n for n in NEWS if n["id"] == news_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    return item


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
