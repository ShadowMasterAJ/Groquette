#!/usr/bin/env python3
"""
AI Video Call Assistant - Main Entry Point
Handles Google Meet integration with AI audio processing
"""

import sys
import argparse
from src.meeting.meet_joiner import MeetJoiner

def main():
    parser = argparse.ArgumentParser(description='AI Video Call Assistant for Google Meet')
    parser.add_argument('meeting_code', nargs='?', help='Google Meet code in format: xxx-xxxx-xxx')
    
    args = parser.parse_args()
    
    # If no meeting code provided, prompt user
    if not args.meeting_code:
        meeting_code = input("Enter Google Meet code (xxx-xxxx-xxx): ").strip()
    else:
        meeting_code = args.meeting_code
    
    # Validate meeting code format
    code_parts = meeting_code.split('-')
    if len(code_parts) != 3 or len(code_parts[0]) != 3 or len(code_parts[1]) != 4 or len(code_parts[2]) != 3:
        print("Invalid meeting code format. Expected format: xxx-xxxx-xxx")
        sys.exit(1)
    
    # Create meeting URL
    meet_url = f"https://meet.google.com/{meeting_code}"
    
    print(f"Starting AI Video Call Assistant...")
    print(f"Meeting: {meet_url}")
    
    # Initialize meeting joiner
    joiner = MeetJoiner(meet_url)
    
    try:
        # Join the meeting
        joiner.join_meeting()
        
        # TODO: Initialize audio streaming with LiveKit
        # TODO: Initialize AI processing with Groq
        
        print("AI assistant is now active in the meeting...")
        print("Press Ctrl+C to leave the meeting")
        
        # Keep the session alive
        joiner.keep_alive()
        
    except KeyboardInterrupt:
        print("\nLeaving meeting...")
        joiner.leave_meeting()
    except Exception as e:
        print(f"Error: {e}")
        joiner.leave_meeting()

if __name__ == "__main__":
    main() 