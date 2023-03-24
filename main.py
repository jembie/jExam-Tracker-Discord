import discord_bot
import page_tracker.track_site as track_site


if __name__ == "__main__":
    tracker = track_site.Page_Tracker()
    discord_bot.run_discord_bot()
    tracker.run()