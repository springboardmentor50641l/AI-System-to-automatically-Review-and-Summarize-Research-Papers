"""
run.py - Main launcher for the project
"""

import os
import sys
from pathlib import Path

def print_menu():
    print("\n" + "="*60)
    print("           AI RESEARCH PAPER REVIEWER")
    print("="*60)
    print("\n🎯 SELECT MILESTONE TO RUN:")
    print("1. 📚 Milestone 1: Search & Download Papers")
    print("2. 📖 Milestone 2: Extract Text from PDFs")
    print("3. 🔬 Milestone 2: Analyze Papers")
    print("4. 📝 Milestone 3: Generate Drafts (requires OpenAI)")
    print("5. 🚀 Run Complete Pipeline (1-3)")
    print("6. 📊 Check Project Status")
    print("0. ❌ Exit")
    print("="*60)

def check_status():
    print("\n📊 PROJECT STATUS CHECK")
    print("-"*40)
    
    folders = [
        ("data/papers", "PDF Downloads"),
        ("data/extracted_text", "Extracted Texts"),
        ("data/analysis", "Analysis Results"),
        ("data/drafts", "Generated Drafts")
    ]
    
    for folder, description in folders:
        path = Path(folder)
        if path.exists():
            files = list(path.glob("*"))
            count = len(files)
            print(f"✅ {description}: {count} files")
        else:
            print(f"❌ {description}: Not created yet")

def main():
    while True:
        print_menu()
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == "1":
            print("\n" + "="*60)
            print("📚 MILESTONE 1: PAPER SEARCH & DOWNLOAD")
            print("="*60)
            from src.paper_search import main as milestone1
            milestone1()
            
        elif choice == "2":
            print("\n" + "="*60)
            print("📖 MILESTONE 2: TEXT EXTRACTION")
            print("="*60)
            from src.text_extractor import main as milestone2a
            milestone2a()
            
        elif choice == "3":
            print("\n" + "="*60)
            print("🔬 MILESTONE 2: PAPER ANALYSIS")
            print("="*60)
            from src.paper_analyzer import main as milestone2b
            milestone2b()
            
        elif choice == "4":
            print("\n" + "="*60)
            print("📝 MILESTONE 3: DRAFT GENERATION")
            print("="*60)
            print("Note: Requires OpenAI API key in .env file")
            confirm = input("Continue? (y/n): ").lower()
            if confirm == 'y':
                try:
                    from src.draft_generator import main as milestone3
                    milestone3()
                except ImportError:
                    print("❌ draft_generator.py not found yet")
                    
        elif choice == "5":
            print("\n" + "="*60)
            print("🚀 RUNNING COMPLETE PIPELINE")
            print("="*60)
            # Run all milestones in sequence
            print("\nStep 1: Paper Search & Download")
            from src.paper_search import main as m1
            m1()
            
            print("\nStep 2: Text Extraction")
            from src.text_extractor import main as m2a
            m2a()
            
            print("\nStep 3: Paper Analysis")
            from src.paper_analyzer import main as m2b
            m2b()
            
        elif choice == "6":
            check_status()
            
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 0-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    main()