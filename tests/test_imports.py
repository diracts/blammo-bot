#!/usr/bin/env python3
"""
Test script to validate imports and basic functionality without requiring Twitch connection.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all imports from main.py"""
    print("Testing imports...")
    
    try:
        # Standard library imports
        import sys, os, random, time, logging, urllib3, json, requests
        import datetime, signal, re, subprocess, math, asyncio
        from urllib.parse import urlencode, urlparse, urlunparse, urljoin
        from pathlib import Path
        from difflib import SequenceMatcher as SM
        print("✓ Standard library imports successful")
        
        # Twitchbot imports
        from twitchbot import BaseBot, event_handler, Event, Command, Message, Channel, PollData, get_bot
        from twitchbot.config import get_nick, get_oauth, get_client_id
        from twitchbot.command import Command
        from twitchbot.message import Message
        print("✓ Twitchbot imports successful")
        
        # Utils imports
        from utils.dbutils import clean_qid, add_qid
        from utils.timestamps import Timestamps
        from utils.record import Record
        from utils.points import PointData
        from utils.trivia import TriviaData
        from utils.scramble import ScrambleData
        from utils.secrets import get_oauth, get_client_id, get_client_secret, get_wa_appid
        from utils import submit
        from utils import secretcommand
        from utils.randommeal import get_meal
        print("✓ Utils imports successful")
        
        # Local imports
        import check_online
        from log.loggers.custom_format import CustomFormatter
        print("✓ Local imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of utility classes"""
    print("\nTesting basic functionality...")
    
    try:
        # Test Timestamps class
        from utils.timestamps import Timestamps
        timestamps = Timestamps()
        print("✓ Timestamps class instantiated")
        
        # Test Record class  
        from utils.record import Record
        record = Record("../blammo-bot-private/record_data.csv")
        print("✓ Record class instantiated")
        
        # Test PointData class
        from utils.points import PointData
        points = PointData()
        print("✓ PointData class instantiated")
        
        # Test TriviaData class
        from utils.trivia import TriviaData
        trivia = TriviaData()
        print("✓ TriviaData class instantiated")
        
        # Test ScrambleData class
        from utils.scramble import ScrambleData
        scramble = ScrambleData()
        print("✓ ScrambleData class instantiated")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def test_config_access():
    """Test config file access"""
    print("\nTesting config access...")
    
    try:
        from utils.secrets import get_oauth, get_client_id, get_client_secret
        
        oauth = get_oauth()
        client_id = get_client_id()
        client_secret = get_client_secret()
        
        print(f"✓ Config access successful")
        print(f"  OAuth: {oauth[:10]}..." if oauth else "  OAuth: None")
        print(f"  Client ID: {client_id[:10]}..." if client_id else "  Client ID: None")
        print(f"  Client Secret: {client_secret[:10]}..." if client_secret else "  Client Secret: None")
        
        return True
        
    except Exception as e:
        print(f"✗ Config access error: {e}")
        return False

if __name__ == "__main__":
    print("BlammoBot Import and Functionality Test")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality() 
    success &= test_config_access()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Bot should work with valid OAuth tokens.")
    else:
        print("✗ Some tests failed. Check errors above.")
        
    print("\nNote: OAuth token validation requires valid Twitch credentials.")