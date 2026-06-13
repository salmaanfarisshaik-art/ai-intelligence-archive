import pytest
import os
import time
from scripts.lib.leaderboard_generator import LeaderboardGenerator

def test_generation_performance():
    # Setup mock data if needed
    start_time = time.time()
    LeaderboardGenerator().generate()
    execution_time = time.time() - start_time
    
    # We expect this simple generation to take less than 2 seconds
    assert execution_time < 2.0, f"Leaderboard generation took {execution_time}s, exceeding 2s limit."
