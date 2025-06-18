#!/usr/bin/env python3
"""
AI Video Call Assistant - Main Entry Point
"""

from utils import parse_meeting_code, run_assistant, restart_application

def main():
    """Main entry point"""
    meeting_code = parse_meeting_code()
    
    # Run the assistant in a loop to handle restarts
    while True:
        result = run_assistant(meeting_code)
        
        if result == 'restart':
            restart_application(meeting_code)
        elif result == 'quit':
            break

if __name__ == "__main__":
    main() 