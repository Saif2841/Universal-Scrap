import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class DatabaseConnection:
    """
    Supabase DB layer for UUID-based schema
    Works with your existing database structure
    PURE JSON - No ORM - Safe UPSERTS
    """

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY missing in .env")

        self.db: Client = create_client(url, key)

    # =========================================================
    # LEAGUES
    # =========================================================

    def save_league(self, league: dict):
        """
        Insert or update league
        returns saved row (with id)
        """
        res = (
            self.db
            .table("leagues")
            .upsert(
                league,
                on_conflict="name,season"
            )
            .execute()
        )

        return res.data[0]

    def get_league_by_name(self, name, season=None):
        """Get league by name and optionally season"""
        query = self.db.table("leagues").select("*").eq("name", name)
        
        if season:
            query = query.eq("season", season)
        
        res = query.limit(1).execute()
        return res.data[0] if res.data else None

    def get_all_leagues(self):
        """Get all leagues"""
        res = self.db.table("leagues").select("*").execute()
        return res.data

    def delete_league_by_name(self, league_name):
        """Delete league by name"""
        self.db.table("leagues").delete().eq("name", league_name).execute()

    # =========================================================
    # TEAMS
    # =========================================================

    def save_teams(self, teams):
        """
        teams = list[dict]
        Upsert teams with logo support
        """
        if teams:
            self.db.table("teams").upsert(
                teams,
                on_conflict="league_id,name"
            ).execute()

    def get_teams_by_league_and_names(self, league_id, names):
        """Get teams by league and names, create if not exists"""
        res = (
            self.db
            .table("teams")
            .select("*")
            .eq("league_id", league_id)
            .in_("name", names)
            .execute()
        )

        existing = {t["name"]: t for t in res.data}
        result = []

        for name in names:
            if name in existing:
                result.append(existing[name])
            else:
                # Create missing team
                created = (
                    self.db
                    .table("teams")
                    .insert({
                        "league_id": league_id,
                        "name": name
                    })
                    .execute()
                )
                result.append(created.data[0])

        return result

    def get_teams_by_league(self, league_id):
        """Get all teams in a league"""
        res = (
            self.db
            .table("teams")
            .select("*")
            .eq("league_id", league_id)
            .execute()
        )

        return res.data

    def get_team_by_id(self, team_id):
        """Get team by ID"""
        res = (
            self.db
            .table("teams")
            .select("*")
            .eq("id", team_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    # =========================================================
    # STANDINGS
    # =========================================================

    def save_table_entries(self, rows):
        """Save standings/table entries"""
        if rows:
            self.db.table("standings").upsert(
                rows,
                on_conflict="league_id,team_id,season"
            ).execute()

    def get_standings_by_league(self, league_id, season):
        """Get standings for a league and season"""
        res = (
            self.db
            .table("standings")
            .select("*")
            .eq("league_id", league_id)
            .eq("season", season)
            .order("position")
            .execute()
        )
        return res.data

    # =========================================================
    # TEAM STATS
    # =========================================================

    def save_team_stats(self, rows):
        """Save team statistics"""
        if rows:
            self.db.table("team_stats").upsert(
                rows,
                on_conflict="team_id,season"
            ).execute()

    def get_team_stats(self, team_id, season):
        """Get team stats for a season"""
        res = (
            self.db
            .table("team_stats")
            .select("*")
            .eq("team_id", team_id)
            .eq("season", season)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_all_team_stats_by_league(self, league_id, season):
        """Get all team stats for a league"""
        # Need to join through teams table
        res = (
            self.db
            .table("team_stats")
            .select("*, teams!inner(league_id, name)")
            .eq("teams.league_id", league_id)
            .eq("season", season)
            .execute()
        )
        return res.data

    # =========================================================
    # MATCHES
    # =========================================================

    def save_matches(self, matches):
        """Save matches with upsert"""
        if matches:
            self.db.table("matches").upsert(
                matches,
                on_conflict="external_id"
            ).execute()

    def get_match_by_external_id(self, external_id):
        """Get match by external_id"""
        res = (
            self.db
            .table("matches")
            .select("*")
            .eq("external_id", external_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_matches_by_league(self, league_id, status=None):
        """Get matches by league, optionally filter by status"""
        query = (
            self.db
            .table("matches")
            .select("*")
            .eq("league_id", league_id)
        )
        
        if status:
            query = query.eq("status", status)
        
        res = query.order("match_date", desc=True).execute()
        return res.data

    def get_matches_by_team(self, team_id, status=None):
        """Get matches by team"""
        query = (
            self.db
            .table("matches")
            .select("*")
            .or_(f"home_team_id.eq.{team_id},away_team_id.eq.{team_id}")
        )
        
        if status:
            query = query.eq("status", status)
        
        res = query.order("match_date", desc=True).execute()
        return res.data

    def get_live_matches(self, league_id=None):
        """Get all live matches, optionally filtered by league"""
        query = self.db.table("matches").select("*").eq("status", "live")
        
        if league_id:
            query = query.eq("league_id", league_id)
        
        res = query.execute()
        return res.data

    def get_upcoming_matches(self, league_id=None, limit=10):
        """Get upcoming scheduled matches"""
        query = self.db.table("matches").select("*").eq("status", "scheduled")
        
        if league_id:
            query = query.eq("league_id", league_id)
        
        res = query.order("match_date").limit(limit).execute()
        return res.data

    # =========================================================
    # MATCH EVENTS
    # =========================================================

    def save_match_events(self, events):
        """
        Save match events (goals, cards, substitutions)
        events = list[dict]
        """
        if events:
            self.db.table("match_events").insert(events).execute()

    def get_match_events(self, match_id):
        """Get all events for a match"""
        res = (
            self.db
            .table("match_events")
            .select("*")
            .eq("match_id", match_id)
            .order("minute")
            .execute()
        )
        return res.data

    def delete_match_events(self, match_id):
        """Delete all events for a match (for re-scraping)"""
        self.db.table("match_events").delete().eq("match_id", match_id).execute()

    # =========================================================
    # UTILITY METHODS
    # =========================================================

    def bulk_delete_by_league(self, league_id):
        """Delete all data for a league (for re-scraping)"""
        print(f"Deleting all data for league_id: {league_id}")
        
        # Get all matches for this league
        matches = self.get_matches_by_league(league_id)
        match_ids = [m['id'] for m in matches]
        
        # Delete match events first
        for match_id in match_ids:
            self.delete_match_events(match_id)
        
        # Delete matches
        self.db.table("matches").delete().eq("league_id", league_id).execute()
        
        # Delete standings
        self.db.table("standings").delete().eq("league_id", league_id).execute()
        
        # Get teams for this league
        teams = self.get_teams_by_league(league_id)
        team_ids = [t['id'] for t in teams]
        
        # Delete team stats
        for team_id in team_ids:
            self.db.table("team_stats").delete().eq("team_id", team_id).execute()
        
        # Delete teams
        self.db.table("teams").delete().eq("league_id", league_id).execute()
        
        print(f"✓ Deleted all data for league_id: {league_id}")

    def get_database_stats(self):
        """Get statistics about the database"""
        stats = {}
        
        tables = ["leagues", "teams", "standings", "matches", "match_events", "team_stats"]
        
        for table in tables:
            try:
                res = self.db.table(table).select("id", count="exact").execute()
                stats[table] = res.count if res.count is not None else 0
            except:
                stats[table] = 0
        
        return stats