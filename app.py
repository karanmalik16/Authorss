"""
Canon Ledger - Flask Web Application & REST API
A Living Story Bible and Continuity Sentinel for authors.
"""

import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, Response, send_file
from core.models import StoryBible, Chapter, ContradictionFlag, Entity, WorldRule, TimelineEvent, KnowledgeItem
from core.file_parser import parse_manuscript_file, split_into_sentences
from core.extractor import ManuscriptExtractor
from core.checker import ContradictionChecker
from core.demo_data import DEMO_CHAPTERS, REAL_WORLD_EXAMPLES, DEMO_SCRIPT_STEPS
from core.references_data import COMPETITOR_TOOLS, MARKET_DEMAND_EVIDENCE
from core.rea_audit import verify_manuscript_integrity

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# Global active story bible
active_bible = StoryBible(title="Chronicles of the Realm")
extractor = ManuscriptExtractor()
checker = ContradictionChecker(active_bible)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bible', methods=['GET'])
def get_bible():
    data = active_bible.to_dict()
    # Add stats
    total_words = sum(c.word_count for c in active_bible.chapters.values())
    pending_flags = sum(1 for f in active_bible.flags if f.status == 'pending')
    data['stats'] = {
        'total_chapters': len(active_bible.chapters),
        'total_words': total_words,
        'total_entities': len(active_bible.entities),
        'total_rules': len(active_bible.world_rules),
        'total_timeline_events': len(active_bible.timeline_events),
        'total_flags': len(active_bible.flags),
        'pending_flags': pending_flags
    }
    return jsonify(data)

@app.route('/api/chapters/upload', methods=['POST'])
def upload_chapter():
    """
    Handles upload of .txt, .md, or .docx file, or raw text pasted in JSON/form.
    """
    title = ""
    raw_text = ""
    book_id = request.form.get('book_id', active_bible.active_book)
    
    if 'file' in request.files and request.files['file'].filename:
        uploaded_file = request.files['file']
        filename = uploaded_file.filename
        file_bytes = uploaded_file.read()
        title, raw_text = parse_manuscript_file(filename, file_bytes)
        # If user explicitly provided a title in form, use it
        custom_title = request.form.get('title', '').strip()
        if custom_title:
            title = custom_title
    elif request.is_json:
        req_json = request.get_json()
        title = req_json.get('title', '').strip()
        raw_text = req_json.get('text', '').strip()
        book_id = req_json.get('book_id', active_bible.active_book)
    else:
        title = request.form.get('title', '').strip()
        raw_text = request.form.get('text', '').strip()

    if not raw_text:
        return jsonify({'error': 'No manuscript text provided'}), 400

    next_id = max(active_bible.chapters.keys(), default=0) + 1
    if not title:
        title = f"Chapter {next_id}"

    sentences = split_into_sentences(raw_text)
    word_count = len(raw_text.split())

    chapter = Chapter(
        id=next_id,
        book_id=book_id,
        title=title,
        order_index=next_id,
        raw_text=raw_text,
        word_count=word_count,
        sentences=sentences
    )

    # 1. Contradiction Sentinel Check against established canon
    new_flags = []
    if next_id > 1:
        new_flags = checker.check_chapter(chapter)

    # 2. Extract facts and update Story Bible
    extracted = extractor.extract_chapter(chapter)
    active_bible.chapters[chapter.id] = chapter
    
    integrity = verify_manuscript_integrity(raw_text)

    for ent in extracted['entities']:
        active_bible.add_or_update_entity(ent)

    for rule in extracted['world_rules']:
        active_bible.world_rules[rule.id] = rule

    for ev in extracted['timeline_events']:
        active_bible.timeline_events.append(ev)

    for k in extracted['knowledge_items']:
        active_bible.add_knowledge_item(k)

    return jsonify({
        'success': True,
        'chapter': chapter.to_dict(),
        'integrity': integrity,
        'new_flags': [f.to_dict() for f in new_flags],
        'total_flags_count': len(active_bible.flags)
    })

@app.route('/api/chapters/<int:cid>', methods=['GET'])
def get_chapter(cid):
    chap = active_bible.chapters.get(cid)
    if not chap:
        return jsonify({'error': 'Chapter not found'}), 404
    return jsonify(chap.to_dict())

def recalculate_sentence_numbers():
    """
    Recalculates earlier_sentence_num and new_sentence_num across all flags
    to guarantee references strictly match the current state of manuscript chapters.
    """
    for f in active_bible.flags:
        # Earlier chapter sentence number
        e_chap = active_bible.chapters.get(f.earlier_chapter_id)
        if e_chap and e_chap.sentences and f.earlier_quote:
            eq = f.earlier_quote.strip().lower()
            for s in e_chap.sentences:
                st = s['text'].strip().lower()
                if eq in st or st in eq:
                    f.earlier_sentence_num = s['sentence_num']
                    break
        # New chapter sentence number
        n_chap = active_bible.chapters.get(f.new_chapter_id)
        if n_chap and n_chap.sentences and f.new_quote:
            nq = f.new_quote.strip().lower()
            for s in n_chap.sentences:
                st = s['text'].strip().lower()
                if nq in st or st in nq:
                    f.new_sentence_num = s['sentence_num']
                    break

def rebuild_bible_flags():
    """
    Rebuilds story bible lore citations and re-evaluates all flags across all chapters.
    Guarantees that sentence numbers ('Sent #') and quotes are strictly up to date.
    Preserves all author decisions (accepted, dismissed, fixed) and notes.
    """
    global active_bible, checker
    
    # 1. Snapshot previous author decisions
    prior_decisions = {}
    for f in active_bible.flags:
        prior_decisions[f.fingerprint] = {
            'status': f.status,
            'author_note': f.author_note
        }
        prior_decisions[(f.category, f.title)] = {
            'status': f.status,
            'author_note': f.author_note
        }
        
    # 2. Reset bible structures while preserving chapters
    saved_chapters = dict(active_bible.chapters)
    active_bible.chapters = {}
    active_bible.entities = {}
    active_bible.world_rules = {}
    active_bible.timeline_events = []
    active_bible.knowledge_items = []
    active_bible.flags = []
    checker = ContradictionChecker(active_bible)
    
    # 3. Progressively check and populate chapters in canonical order
    sorted_chapters = sorted(saved_chapters.values(), key=lambda c: c.order_index)
    for chap in sorted_chapters:
        # Check contradictions against earlier chapters
        if chap.order_index > 1:
            checker.check_chapter(chap)
            
        # Extract facts and populate bible
        extracted = extractor.extract_chapter(chap)
        active_bible.chapters[chap.id] = chap
        
        for ent in extracted['entities']:
            active_bible.add_or_update_entity(ent)
            
        for rule in extracted['world_rules']:
            active_bible.world_rules[rule.id] = rule
            
        for ev in extracted['timeline_events']:
            active_bible.timeline_events.append(ev)
            
        for k in extracted['knowledge_items']:
            active_bible.add_knowledge_item(k)

    # 4. Re-apply author decisions
    for f in active_bible.flags:
        if f.fingerprint in prior_decisions:
            f.status = prior_decisions[f.fingerprint]['status']
            f.author_note = prior_decisions[f.fingerprint]['author_note']
        elif (f.category, f.title) in prior_decisions:
            f.status = prior_decisions[(f.category, f.title)]['status']
            f.author_note = prior_decisions[(f.category, f.title)]['author_note']

    # 5. Recalculate sentence numbers
    recalculate_sentence_numbers()

@app.route('/api/chapters/<int:cid>/fix', methods=['POST'])
def fix_chapter_text(cid):
    """
    Allows the author to edit/fix chapter text in their manuscript.
    Canon Ledger re-checks that chapter and every chapter after it.
    Before re-checking, removes old pending flags for those chapters.
    If a flag no longer appears after the edit, marks it as fixed with the note 'Resolved by edit.'
    Recalculates sentence numbers after every save.
    """
    global active_bible, checker
    chap = active_bible.chapters.get(cid)
    if not chap:
        return jsonify({'error': 'Chapter not found'}), 404
        
    data = request.get_json() or {}
    new_text = data.get('text', '').strip()
    if not new_text:
        return jsonify({'error': 'Text cannot be empty'}), 400
        
    chap.raw_text = new_text
    chap.sentences = split_into_sentences(new_text)
    chap.word_count = len(new_text.split())

    # Chapters to re-check: this chapter and every chapter after it
    cids_to_recheck = {
        c.id for c in active_bible.chapters.values() 
        if c.order_index >= chap.order_index
    }

    # 1. Capture old pending flags for those chapters before removing them
    old_pending = [
        f for f in active_bible.flags 
        if f.new_chapter_id in cids_to_recheck and f.status == 'pending'
    ]

    # Remove old pending flags for those chapters
    active_bible.flags = [
        f for f in active_bible.flags 
        if not (f.new_chapter_id in cids_to_recheck and f.status == 'pending')
    ]

    # 2. Re-extract lore from all chapters progressively and re-check target chapters
    saved_chapters = dict(active_bible.chapters)
    active_bible.entities = {}
    active_bible.world_rules = {}
    active_bible.timeline_events = []
    active_bible.knowledge_items = []
    
    checker = ContradictionChecker(active_bible)
    newly_generated_flags = []

    sorted_chapters = sorted(saved_chapters.values(), key=lambda c: c.order_index)
    for c in sorted_chapters:
        # Re-check this chapter if it is in cids_to_recheck and not chapter 1
        if c.id in cids_to_recheck and c.order_index > 1:
            gen_flags = checker.check_chapter(c)
            newly_generated_flags.extend(gen_flags)

        # Extract lore and update bible
        extracted = extractor.extract_chapter(c)
        active_bible.chapters[c.id] = c

        for ent in extracted['entities']:
            active_bible.add_or_update_entity(ent)

        for rule in extracted['world_rules']:
            active_bible.world_rules[rule.id] = rule

        for ev in extracted['timeline_events']:
            active_bible.timeline_events.append(ev)

        for k in extracted['knowledge_items']:
            active_bible.add_knowledge_item(k)

    # 3. For any flag in old_pending that no longer appears after the edit, mark it as fixed
    new_identifiers = {
        (f.category, f.title) for f in newly_generated_flags
    }
    new_fingerprints = {
        f.fingerprint for f in newly_generated_flags
    }

    for old_f in old_pending:
        issue_still_present = (
            (old_f.category, old_f.title) in new_identifiers or
            old_f.fingerprint in new_fingerprints
        )
        if not issue_still_present:
            old_f.status = 'fixed'
            old_f.author_note = 'Resolved by edit.'
            # Only append if not already in flags
            if not any(f.id == old_f.id for f in active_bible.flags):
                active_bible.flags.append(old_f)

    # 4. Recalculate sentence numbers across all flags
    recalculate_sentence_numbers()
    
    return jsonify({
        'success': True,
        'chapter': chap.to_dict(),
        'total_flags_count': len(active_bible.flags),
        'pending_flags_count': len([f for f in active_bible.flags if f.status == 'pending'])
    })
    
    return jsonify({
        'success': True,
        'chapter': chap.to_dict(),
        'total_flags_count': len(active_bible.flags),
        'pending_flags_count': len([f for f in active_bible.flags if f.status == 'pending'])
    })

@app.route('/api/chapters/<int:cid>', methods=['DELETE'])
def delete_chapter(cid):
    if cid in active_bible.chapters:
        del active_bible.chapters[cid]
        rebuild_bible_flags()
        return jsonify({'success': True})
    return jsonify({'error': 'Chapter not found'}), 404

@app.route('/api/flags/<string:fid>/status', methods=['POST'])
def update_flag_status(fid):
    """
    Accept, dismiss, fix, or reopen (pending) a continuity flag.
    Dismissals store a deterministic fingerprint so the same false alarm won't reappear.
    """
    data = request.get_json() or {}
    new_status = data.get('status')  # 'accepted', 'dismissed', 'fixed', 'pending'
    author_note = data.get('author_note', '')
    
    if new_status == 'dismissed':
        ok = active_bible.dismiss_flag(fid, author_note)
    elif new_status == 'accepted':
        ok = active_bible.accept_flag(fid, author_note)
    elif new_status == 'fixed':
        ok = active_bible.fix_flag(fid, author_note)
    elif new_status == 'pending':
        ok = False
        for f in active_bible.flags:
            if f.id == fid:
                f.status = 'pending'
                f.author_note = ''
                active_bible.dismissed_fingerprints.discard(f.fingerprint)
                ok = True
                break
    else:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400

    if not ok:
        return jsonify({'success': False, 'error': 'Flag not found'}), 404

    return jsonify({'success': True, 'flag_id': fid, 'status': new_status})

@app.route('/api/bible/entities', methods=['POST'])
def save_entity():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    category = data.get('category', 'character')
    if not name:
        return jsonify({'error': 'Entity name required'}), 400
        
    ent_id = data.get('id') or name.lower().replace(" ", "_")
    entity = active_bible.get_or_create_entity(name, category, entity_id=ent_id)
    if 'attributes' in data:
        entity.attributes = data['attributes']
    if 'notes' in data:
        entity.notes = data['notes']
        
    return jsonify({'success': True, 'entity': entity.to_dict()})

@app.route('/api/bible/entities/<string:eid>', methods=['DELETE'])
def delete_entity(eid):
    if eid in active_bible.entities:
        del active_bible.entities[eid]
        return jsonify({'success': True})
    return jsonify({'error': 'Entity not found'}), 404

@app.route('/api/bible/rules', methods=['POST'])
def save_rule():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    statement = data.get('statement', '').strip()
    domain = data.get('domain', 'magic')
    rule_id = data.get('id') or f"rule_{uuid.uuid4().hex[:6]}"
    
    if not statement:
        return jsonify({'error': 'Rule statement required'}), 400
        
    rule = WorldRule(id=rule_id, name=name or "World Rule", domain=domain, statement=statement)
    active_bible.world_rules[rule_id] = rule
    return jsonify({'success': True, 'rule': rule.to_dict()})

@app.route('/api/bible/rules/<string:rid>', methods=['DELETE'])
def delete_rule(rid):
    if rid in active_bible.world_rules:
        del active_bible.world_rules[rid]
        return jsonify({'success': True})
    return jsonify({'error': 'Rule not found'}), 404

@app.route('/api/demo/load', methods=['POST'])
def load_demo():
    """
    Clears current bible and loads the 3-chapter manuscript with 5 planted errors.
    Also injects 1 benign ambiguity for testing author dismissal.
    """
    global active_bible, checker
    active_bible = StoryBible(title="The Shadow of Aethelgard")
    checker = ContradictionChecker(active_bible)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for item in DEMO_CHAPTERS:
        fpath = os.path.join(base_dir, item['file_path'])
        with open(fpath, 'rb') as f:
            raw_bytes = f.read()
        title, text = parse_manuscript_file(os.path.basename(fpath), raw_bytes)
        sentences = split_into_sentences(text)
        
        chap = Chapter(
            id=item['id'],
            book_id="Book 1",
            title=title,
            order_index=item['id'],
            raw_text=text,
            word_count=len(text.split()),
            sentences=sentences
        )
        
        # Check contradictions against earlier chapters
        if item['id'] > 1:
            checker.check_chapter(chap)
            
        # Extract facts and populate bible
        extracted = extractor.extract_chapter(chap)
        active_bible.chapters[chap.id] = chap
        
        for ent in extracted['entities']:
            active_bible.add_or_update_entity(ent)
            
        for rule in extracted['world_rules']:
            active_bible.world_rules[rule.id] = rule
            
        for ev in extracted['timeline_events']:
            active_bible.timeline_events.append(ev)
            
        for k in extracted['knowledge_items']:
            active_bible.add_knowledge_item(k)

    # Recalculate sentence numbers across all flags
    recalculate_sentence_numbers()

    return jsonify({
        'success': True,
        'message': 'Loaded 3-chapter demo manuscript with 5 planted errors.',
        'bible': active_bible.to_dict()
    })

@app.route('/api/reset', methods=['POST'])
def reset_project():
    global active_bible, checker
    active_bible = StoryBible(title="New Manuscript Series")
    checker = ContradictionChecker(active_bible)
    return jsonify({'success': True})

@app.route('/api/export/markdown', methods=['GET'])
def export_markdown():
    md = active_bible.export_as_markdown()
    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-Disposition": "attachment;filename=story_bible.md"}
    )

@app.route('/api/export/json', methods=['GET'])
def export_json():
    data = json.dumps(active_bible.to_dict(), indent=2)
    return Response(
        data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=story_bible.json"}
    )

@app.route('/api/export/report', methods=['GET'])
def export_report():
    md = active_bible.export_as_markdown()
    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-Disposition": "attachment;filename=continuity_audit_report.md"}
    )

@app.route('/api/demo/guide', methods=['GET'])
def get_demo_guide():
    return jsonify({
        'problem_statement': "Authors lose track of eye colors, timeline dates, world rules, and who knows what across 100,000 words. Errors slip through and readers punish them in reviews.",
        'real_world_examples': REAL_WORLD_EXAMPLES,
        'steps': DEMO_SCRIPT_STEPS
    })

@app.route('/api/references', methods=['GET'])
def get_references():
    return jsonify({
        'competitors': COMPETITOR_TOOLS,
        'demand_evidence': MARKET_DEMAND_EVIDENCE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
