#!/usr/bin/env python3
"""
Test the ".." vs "..." fix in submission validation
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.submit import _check_safety


async def test_dots_validation():
    """Test the dots validation fix"""
    print("🧪 Testing dots validation fix")
    print("=" * 40)
    
    test_cases = [
        # (content, should_pass, description)
        ("This has .. in it", False, "Should block '..'"),
        ("This has ... in it", True, "Should allow '...'"),
        ("This has .... in it", True, "Should allow '....'"),
        ("../etc/passwd", False, "Should block path traversal"),
        ("What is...?", True, "Should allow '...' in question"),
        ("Who... what... when...", True, "Should allow multiple '...'"),
        ("file..txt", False, "Should block '..' in filename"),
        ("This is normal text", True, "Should allow normal text"),
        ("Period. Period.", True, "Should allow single dots"),
    ]
    
    all_passed = True
    
    for content, should_pass, description in test_cases:
        try:
            result = await _check_safety(content)
            if result == should_pass:
                print(f"✅ {description}: '{content}' -> {result}")
            else:
                print(f"❌ {description}: '{content}' -> {result} (expected {should_pass})")
                all_passed = False
        except Exception as e:
            print(f"🔥 Error testing '{content}': {e}")
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 All tests passed! The dots validation bug is fixed.")
    else:
        print("💥 Some tests failed. The fix needs adjustment.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_dots_validation())
    sys.exit(0 if success else 1)