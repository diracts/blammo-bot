#!/usr/bin/env python3
"""
Test IRC authentication manually to isolate the issue
"""
import socket
import ssl
import json
import time

def test_irc_auth():
    """Test IRC authentication directly"""
    print("🔍 Testing Twitch IRC Authentication Manually")
    print("=" * 60)
    
    # Load config
    with open('configs/config.json') as f:
        config = json.load(f)
    
    oauth_token = config.get('oauth', '')
    nick = config.get('nick', '')
    
    print(f"Nick: {nick}")
    print(f"Token: {oauth_token[:15]}...")
    
    try:
        # Connect to Twitch IRC
        print("\n📡 Connecting to irc.chat.twitch.tv:6697...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname='irc.chat.twitch.tv')
        sock.connect(('irc.chat.twitch.tv', 6697))
        print("✅ Connected to IRC server")
        
        # Send authentication
        print(f"\n🔐 Sending authentication...")
        print(f"PASS: {oauth_token[:15]}...")
        print(f"NICK: {nick}")
        
        sock.send(f'PASS {oauth_token}\r\n'.encode('utf-8'))
        sock.send(f'NICK {nick}\r\n'.encode('utf-8'))
        
        # Read responses
        print(f"\n📨 Server responses:")
        sock.settimeout(5.0)
        
        for i in range(10):  # Read several responses
            try:
                response = sock.recv(2048).decode('utf-8')
                print(f"Response {i+1}: {repr(response)}")
                
                if 'Welcome' in response:
                    print("✅ Authentication successful!")
                    break
                elif 'Login authentication failed' in response or 'login unsuccessful' in response:
                    print("❌ Authentication failed!")
                    break
                elif ':tmi.twitch.tv NOTICE * :Login unsuccessful' in response:
                    print("❌ Login unsuccessful!")
                    break
                    
            except socket.timeout:
                print(f"Timeout waiting for response {i+1}")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    test_irc_auth()