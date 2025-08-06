#!/usr/bin/env python3
"""
Test OAuth token validation specifically for IRC chat
"""
import requests
import json

def test_token_validation():
    """Test the OAuth token against Twitch's validation endpoint"""
    print("🔍 Testing OAuth Token Validation")
    print("=" * 50)
    
    # Load config
    with open('configs/config.json') as f:
        config = json.load(f)
    
    oauth_token = config.get('oauth', '')
    client_id = config.get('client_id', '')
    
    print(f"Token: {oauth_token[:15]}...")
    print(f"Client ID: {client_id[:15]}...")
    
    # Remove 'oauth:' prefix for API call
    token_clean = oauth_token.replace('oauth:', '') if oauth_token.startswith('oauth:') else oauth_token
    
    # Test 1: Validate token with Twitch API
    print("\n📡 Testing token with Twitch validation API...")
    try:
        headers = {
            'Authorization': f'OAuth {token_clean}',
            'Client-ID': client_id
        }
        
        response = requests.get('https://id.twitch.tv/oauth2/validate', headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token is valid!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Login: {data.get('login')}")
            print(f"   Scopes: {data.get('scopes')}")
            print(f"   Client ID: {data.get('client_id')}")
            
            # Check if login matches our config
            config_nick = config.get('nick')
            if data.get('login') != config_nick:
                print(f"⚠️  WARNING: Token login '{data.get('login')}' doesn't match config nick '{config_nick}'")
            else:
                print(f"✅ Token login matches config nick")
                
        else:
            print(f"❌ Token validation failed")
            
    except Exception as e:
        print(f"❌ Error validating token: {e}")
    
    # Test 2: Check IRC-specific requirements
    print(f"\n🔧 IRC Token Analysis:")
    print(f"   Has 'oauth:' prefix: {oauth_token.startswith('oauth:')}")
    print(f"   Token length (with prefix): {len(oauth_token)}")
    print(f"   Token length (without prefix): {len(token_clean)}")
    print(f"   Expected IRC format: oauth:{'x' * 30}")
    
    # Test 3: Check if this is a Chat token vs API token
    print(f"\n💬 Testing IRC Chat compatibility...")
    if len(token_clean) == 30:
        print("✅ Token length matches IRC chat token format (30 chars)")
    else:
        print(f"⚠️  Token length is {len(token_clean)}, IRC chat tokens should be 30 chars")
        print("   This might be an API token instead of an IRC chat token")
        print("   IRC tokens are generated at: https://twitchapps.com/tmi/")
        print("   API tokens are generated at: https://dev.twitch.tv/console")

if __name__ == "__main__":
    test_token_validation()