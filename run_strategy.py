#!/usr/bin/env python3
"""
Run startup strategist for your actual startup idea
"""

from startup_strategist import StartupStrategist
import json

def main():
    strategist = StartupStrategist()
    
    # Define your startup inputs - customize these for your actual idea
    inputs = {
        'niche': 'AI agents for ecommerce',  # Change this to your actual startup idea
        'stage': 'MVP',  # idea | discovery | MVP | PMF | scale
        'geo': 'Pakistan, South Asia',  # Your target geography
        'founder_profile': 'AI graduate with strong technical skills',  # Your skills/background
        'constraints': 'budget constraints, need to build MVP efficiently',  # Your constraints
        'goals': 'make a proper working MVP that can be launched in the market'  # Your 12-week goals
    }
    
    print('🚀 Generating strategy for your startup idea...')
    print('=' * 60)
    
    strategy = strategist.generate_strategy(inputs)
    strategist.print_strategy(strategy)
    
    # Save to file
    with open('my_startup_strategy.json', 'w', encoding='utf-8') as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)
    
    print('\n💾 Strategy saved to my_startup_strategy.json')
    print('🎉 Your startup strategy is ready!')

if __name__ == "__main__":
    main()
