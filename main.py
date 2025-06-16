#!/usr/bin/env python3
"""
AI Video Call Assistant - Main Entry Point
Handles Google Meet integration with AI audio processing
"""

import sys
import argparse
import threading
import time
from src.meeting.meet_joiner import MeetJoiner

def get_user_input():
    """Get user input in a non-blocking way"""
    try:
        return input().strip().lower()
    except EOFError:
        return None

def run_assistant(meeting_code):
    """Run the assistant for a given meeting code"""
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
        print("Commands:")
        print("  Press 'r' + Enter to restart the application")
        print("  Press Ctrl+C to leave the meeting")
        
        # Keep the session alive with command handling
        while True:
            try:
                user_input = get_user_input()
                
                if user_input == 'r':
                    print("Restarting application...")
                    joiner.leave_meeting()
                    return 'restart'  # Signal to restart
                    
                elif user_input == 'q' or user_input == 'quit':
                    print("Exiting...")
                    joiner.leave_meeting()
                    return 'quit'  # Signal to quit
                    
                else:
                    if user_input:  # Only show message for non-empty input
                        print("Unknown command. Press 'r' to restart or Ctrl+C to exit.")
                        
            except EOFError:
                # Handle Ctrl+D
                joiner.leave_meeting()
                return 'quit'
                
    except KeyboardInterrupt:
        print("\nLeaving meeting...")
        joiner.leave_meeting()
        return 'quit'
    except Exception as e:
        print(f"Error: {e}")
        joiner.leave_meeting()
        return 'quit'

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
    
    # Run the assistant in a loop to handle restarts
    while True:
        result = run_assistant(meeting_code)
        
        if result == 'restart':
            print("Restarting main application...\n")
            # Reload the module to pick up any code changes
            import importlib
            import src.meeting.meet_joiner
            importlib.reload(src.meeting.meet_joiner)
            from src.meeting.meet_joiner import MeetJoiner
            continue
        elif result == 'quit':
            break

if __name__ == "__main__":
    main() 