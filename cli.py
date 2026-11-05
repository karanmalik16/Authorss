#!/usr/bin/env python3
"""
Canon Ledger CLI Runner.
Audits manuscripts for continuity errors and exports living story bibles.

Usage:
  python cli.py --demo
  python cli.py --dir sample_manuscript/ --export-report report.md --export-bible bible.md
  python cli.py --chapters ch1.txt ch2.txt --export-bible bible.json
"""

import os
import sys
import argparse
import glob
from core.models import StoryBible, Chapter
from core.file_parser import parse_manuscript_file, split_into_sentences
from core.extractor import ManuscriptExtractor
from core.checker import ContradictionChecker
from core.demo_data import DEMO_CHAPTERS

def run_audit(file_paths: list, export_report: str = None, export_bible: str = None) -> int:
    bible = StoryBible(title="Manuscript Audit")
    extractor = ManuscriptExtractor()
    checker = ContradictionChecker(bible)
    
    print("=" * 70)
    print("  CANON LEDGER — Continuity Sentinel & Living Story Bible")
    print("=" * 70)
    
    total_flags = 0
    
    for idx, fpath in enumerate(file_paths, start=1):
        if not os.path.exists(fpath):
            print(f"[-] File not found: {fpath}")
            continue
            
        filename = os.path.basename(fpath)
        with open(fpath, 'rb') as f:
            raw_bytes = f.read()
            
        title, text = parse_manuscript_file(filename, raw_bytes)
        sentences = split_into_sentences(text)
        
        chapter = Chapter(
            id=idx,
            book_id="Book 1",
            title=title,
            order_index=idx,
            raw_text=text,
            word_count=len(text.split()),
            sentences=sentences
        )
        
        print(f"\n[+] Ingesting Chapter {idx}: {title} ({chapter.word_count} words, {len(sentences)} sentences)")
        
        # 1. Check for contradictions against established canon BEFORE updating bible with new chapter facts
        if idx > 1:
            flags = checker.check_chapter(chapter)
            if flags:
                print(f"  [!] Found {len(flags)} continuity flags:")
                for flag in flags:
                    total_flags += 1
                    print(f"      * [{flag.severity.upper()}] {flag.title}")
                    print(f"        - Earlier (Ch {flag.earlier_chapter_id}): \"{flag.earlier_quote}\"")
                    print(f"        - Current (Ch {flag.new_chapter_id}): \"{flag.new_quote}\"")
                    print(f"        - Fix hint: {flag.suggested_fix}")
            else:
                print("  [OK] No continuity contradictions detected.")
        else:
            print("  [OK] Genesis chapter: Baseline canon established.")

        # 2. Extract facts and add chapter to bible
        extracted = extractor.extract_chapter(chapter)
        bible.chapters[chapter.id] = chapter
        
        for ent in extracted['entities']:
            bible.add_or_update_entity(ent)
            
        for rule in extracted['world_rules']:
            bible.world_rules[rule.id] = rule
            
        for ev in extracted['timeline_events']:
            bible.timeline_events.append(ev)
            
        for k in extracted['knowledge_items']:
            bible.add_knowledge_item(k)

    print("\n" + "=" * 70)
    print(f"AUDIT COMPLETE: {len(bible.chapters)} chapters analyzed.")
    print(f"Story Bible: {len(bible.entities)} entities, {len(bible.world_rules)} world rules, {len(bible.timeline_events)} timeline events.")
    print(f"Continuity Flags: {len(bible.flags)} detected.")
    print("=" * 70)
    
    # Export report if requested
    if export_report:
        with open(export_report, 'w', encoding='utf-8') as f:
            f.write(bible.export_as_markdown())
        print(f"[+] Continuity report exported to: {export_report}")
        
    # Export bible if requested
    if export_bible:
        with open(export_bible, 'w', encoding='utf-8') as f:
            if export_bible.endswith('.json'):
                import json
                json.dump(bible.to_dict(), f, indent=2)
            else:
                f.write(bible.export_as_markdown())
        print(f"[+] Story Bible exported to: {export_bible}")
        
    return 1 if total_flags > 0 else 0

def main():
    parser = argparse.ArgumentParser(description="Canon Ledger: Living Story Bible & Continuity Checker")
    parser.add_argument("--demo", action="store_true", help="Run audit on the built-in 3-chapter demo manuscript")
    parser.add_argument("--dir", type=str, help="Directory containing manuscript chapter files (.txt, .md, .docx)")
    parser.add_argument("--chapters", nargs="+", help="Explicit list of chapter files in order")
    parser.add_argument("--export-report", type=str, help="Output path for Markdown contradiction report")
    parser.add_argument("--export-bible", type=str, help="Output path for Story Bible (JSON or MD)")
    
    args = parser.parse_args()
    
    file_paths = []
    if args.demo:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_paths = [os.path.join(base_dir, c['file_path']) for c in DEMO_CHAPTERS]
    elif args.dir:
        patterns = [os.path.join(args.dir, ext) for ext in ('*.txt', '*.md', '*.docx')]
        for p in patterns:
            file_paths.extend(glob.glob(p))
        file_paths.sort()
    elif args.chapters:
        file_paths = args.chapters
    else:
        # Default to demo if no args provided
        print("[!] No input files specified. Running built-in demo...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_paths = [os.path.join(base_dir, c['file_path']) for c in DEMO_CHAPTERS]

    if not file_paths:
        print("[-] No manuscript chapters found to audit.")
        sys.exit(1)
        
    code = run_audit(file_paths, export_report=args.export_report, export_bible=args.export_bible)
    sys.exit(code)

if __name__ == '__main__':
    main()
