"""
OBINexus Constitutional Updates - Claude Processing Methods
Three approaches for generating update notes from live feeds
"""

import anthropic
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# METHOD 1: Live Transcript Processing (Real-time Stream)
# ============================================================================

class LiveTranscriptProcessor:
    """
    Process raw YouTube transcripts into structured update notes.
    Best for: Unstructured video content, live updates, stream-of-consciousness
    
    Integration: rust-semverx (assigns versions based on content analysis)
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def process_transcript(self, transcript_path: str, video_metadata: dict) -> dict:
        """
        Analyze transcript and extract constitutional updates
        
        Args:
            transcript_path: Path to transcript file
            video_metadata: YouTube video info (URL, date, duration)
            
        Returns:
            Structured update note with NLM coordinates and SemVerX state
        """
        
        with open(transcript_path, 'r') as f:
            transcript_text = f.read()
        
        # System prompt for constitutional analysis
        system_prompt = """You are analyzing OBINexus constitutional framework updates.

Your task is to extract:
1. Key constitutional changes (housing, ring topology, business model)
2. Technical architecture updates (infrastructure, networking, security)
3. Personal development insights (neurodivergent support, life-work balance)
4. NLM-framework coordinates (X: coherence, Y: reasoning, Z: evolution)
5. SemVerX state classification (stable/experimental/legacy)

Format output as structured JSON matching OBINexus update schema."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"""Analyze this OBINexus constitutional update transcript:

Video Metadata:
{json.dumps(video_metadata, indent=2)}

Transcript:
{transcript_text}

Extract:
1. Main topics and constitutional changes
2. Technical architecture updates
3. Business model tier changes (T1/T2/T3)
4. NLM coordinates (X/Y/Z axes)
5. SemVerX state (stable/experimental/legacy)
6. Action items and next steps

Respond with ONLY valid JSON in this format:
{{
  "update_title": "string",
  "summary": "2-3 sentences",
  "topics": ["topic1", "topic2"],
  "constitutional_changes": [
    {{"area": "string", "change": "string", "impact": "low|medium|high"}}
  ],
  "technical_updates": [
    {{"component": "string", "update": "string", "breaking": true|false}}
  ],
  "business_model": {{"tier": "T1|T2|T3", "changes": ["change1"]}},
  "nlm_coordinates": {{"x_axis": 0.0-1.0, "y_axis": 0.0-1.0, "z_axis": 0.0-1.0}},
  "semverx_state": "stable|experimental|legacy",
  "action_items": ["item1", "item2"],
  "key_quotes": ["quote1", "quote2"]
}}"""
            }]
        )
        
        # Parse Claude's JSON response
        response_text = message.content[0].text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        update_data = json.loads(response_text)
        
        # Add metadata
        update_data['metadata'] = {
            'source': video_metadata,
            'processed_at': datetime.utcnow().isoformat(),
            'processor': 'method-1-live-transcript',
            'version': self._generate_version(update_data)
        }
        
        return update_data
    
    def _generate_version(self, update_data: dict) -> str:
        """Generate SemVerX version based on update content"""
        state = update_data['semverx_state']
        
        # Determine major/minor/patch based on impact
        has_breaking = any(
            u.get('breaking', False) 
            for u in update_data.get('technical_updates', [])
        )
        
        constitutional_impact = any(
            c.get('impact') == 'high' 
            for c in update_data.get('constitutional_changes', [])
        )
        
        if has_breaking or constitutional_impact:
            return f"v1.{state}.1.0"
        elif update_data.get('technical_updates'):
            return f"v1.{state}.0.1"
        else:
            return f"v1.{state}.0.0"
    
    def save_update_note(self, update_data: dict, output_dir: str):
        """Save structured update as markdown and JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from date and title
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        title_slug = update_data['update_title'].lower().replace(' ', '-')[:50]
        filename = f"{date_str}-{title_slug}"
        
        # Save JSON metadata
        with open(output_path / f"{filename}.json", 'w') as f:
            json.dump(update_data, f, indent=2)
        
        # Generate markdown update note
        markdown = self._generate_markdown(update_data)
        with open(output_path / f"{filename}.md", 'w') as f:
            f.write(markdown)
        
        return str(output_path / f"{filename}.md")
    
    def _generate_markdown(self, data: dict) -> str:
        """Convert JSON data to markdown update note"""
        md = f"""# LIVE: {data['update_title']}

**Date**: {data['metadata']['processed_at'][:10]}  
**Version**: {data['metadata']['version']}  
**Source**: {data['metadata']['source']['url']}  
**Status**: Draft

## Summary

{data['summary']}

## Key Changes

### Constitutional Framework
"""
        
        for change in data.get('constitutional_changes', []):
            md += f"- **{change['area']}**: {change['change']} (Impact: {change['impact']})\n"
        
        md += "\n### Technical Architecture\n"
        for update in data.get('technical_updates', []):
            breaking = " [BREAKING]" if update.get('breaking') else ""
            md += f"- **{update['component']}**: {update['update']}{breaking}\n"
        
        md += f"""
### Business Model
- **Tier**: {data['business_model']['tier']}
- **Changes**: {', '.join(data['business_model']['changes'])}

## NLM Coordinates

- **X-Axis (Coherence)**: {data['nlm_coordinates']['x_axis']:.2f}
- **Y-Axis (Reasoning)**: {data['nlm_coordinates']['y_axis']:.2f}
- **Z-Axis (Evolution)**: {data['nlm_coordinates']['z_axis']:.2f}

## SemVerX State

- **Current State**: {data['semverx_state']}
- **Version**: {data['metadata']['version']}

## Action Items

"""
        for item in data['action_items']:
            md += f"- [ ] {item}\n"
        
        md += "\n## Key Quotes\n\n"
        for quote in data.get('key_quotes', []):
            md += f"> {quote}\n\n"
        
        md += f"""
---

**Generated by**: Claude Method 1 (Live Transcript Processor)  
**Processed**: {data['metadata']['processed_at']}
"""
        return md


# ============================================================================
# METHOD 2: Structured Query Processing (Interactive Q&A)
# ============================================================================

class StructuredQueryProcessor:
    """
    Process updates through structured Q&A format.
    Best for: Clarifying specific changes, targeted updates, follow-up questions
    
    Integration: NLM-atlas (service discovery for related documentation)
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []
    
    def query_update(self, query: str, context: dict = None) -> dict:
        """
        Ask specific questions about constitutional updates
        
        Args:
            query: Question about the update (e.g., "What changed in ring topology?")
            context: Previous conversation context
            
        Returns:
            Structured answer with citations to documentation
        """
        
        system_prompt = """You are the OBINexus Constitutional Framework assistant.

You answer queries about:
- Constitutional housing ring topology
- Business model tiers (T1/T2/T3)
- NLM-framework integration
- Rust-SemVerX versioning
- Infrastructure as a Service

Provide:
1. Direct answer to the query
2. References to relevant documentation
3. Impact assessment (if applicable)
4. Related concepts to explore

Be precise and cite specific documents/videos."""

        # Build conversation history
        messages = self.conversation_history + [{
            "role": "user",
            "content": f"""Query: {query}

Context:
{json.dumps(context, indent=2) if context else 'No previous context'}

Please provide:
1. Direct answer
2. Documentation references
3. Impact assessment
4. Related topics

Format as JSON:
{{
  "answer": "string",
  "references": [{{"type": "doc|video|code", "url": "string", "title": "string"}}],
  "impact": {{"area": "string", "level": "low|medium|high", "description": "string"}},
  "related_topics": ["topic1", "topic2"]
}}"""
        }]
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=messages
        )
        
        response_text = message.content[0].text.strip()
        # Clean markdown
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        result = json.loads(response_text)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return result
    
    def batch_queries(self, queries: list[str]) -> dict:
        """Process multiple related queries"""
        results = {}
        context = None
        
        for i, query in enumerate(queries):
            print(f"Processing query {i+1}/{len(queries)}: {query}")
            result = self.query_update(query, context)
            results[f"query_{i+1}"] = {
                "question": query,
                "response": result
            }
            context = result  # Use previous result as context
        
        return {
            "batch_results": results,
            "summary": self._summarize_batch(results)
        }
    
    def _summarize_batch(self, results: dict) -> str:
        """Create summary of batch query results"""
        # Use Claude to summarize
        summary_prompt = f"""Summarize these Q&A results into a cohesive update note:

{json.dumps(results, indent=2)}

Provide a 2-3 paragraph summary highlighting:
1. Main themes across queries
2. Key changes identified
3. Areas needing follow-up"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        return message.content[0].text


# ============================================================================
# METHOD 3: State Machine Processing (Declarative Updates)
# ============================================================================

class StateMachineProcessor:
    """
    Process updates through state machine transitions.
    Best for: System state changes, architectural decisions, version bumps
    
    Integration: rust-semverx DAG resolution + HDIS state tracking
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.current_state = self._load_current_state()
    
    def _load_current_state(self) -> dict:
        """Load current constitutional state"""
        # In production, load from state file
        return {
            "constitutional_version": "v1.stable.4.0",
            "active_rings": 6,
            "business_tier": "T1",
            "housing_status": "pilot_planning",
            "cambridge_status": "delayed",
            "legal_claims": {"thurrock": 300_000_000}
        }
    
    def process_state_change(self, change_event: dict) -> dict:
        """
        Process a state machine transition
        
        Args:
            change_event: {
                "type": "constitutional_change|technical_update|business_model",
                "trigger": "what caused this change",
                "target_state": "desired end state",
                "impact": "description"
            }
            
        Returns:
            Transition analysis with version bump recommendation
        """
        
        system_prompt = """You are the OBINexus State Machine Analyzer.

You evaluate state transitions in the constitutional framework and determine:
1. Validity of the transition (can current state → target state?)
2. SemVerX version bump required (major/minor/patch)
3. Breaking changes introduced
4. Rollback path if needed
5. Dependencies affected

Use DAG-based reasoning to ensure coherent state transitions."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"""Analyze this state transition:

Current State:
{json.dumps(self.current_state, indent=2)}

Change Event:
{json.dumps(change_event, indent=2)}

Evaluate:
1. Is transition valid?
2. What version bump is needed?
3. What breaks?
4. How to rollback?
5. What else is affected?

Respond as JSON:
{{
  "transition_valid": true|false,
  "validation_notes": "string",
  "version_bump": {{"current": "string", "next": "string", "type": "major|minor|patch"}},
  "breaking_changes": ["change1", "change2"],
  "rollback_path": "instructions",
  "affected_components": ["component1", "component2"],
  "migration_guide": "step-by-step"
}}"""
            }]
        )
        
        response_text = message.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        analysis = json.loads(response_text)
        
        # Apply state transition if valid
        if analysis['transition_valid']:
            self._apply_transition(change_event, analysis)
        
        return analysis
    
    def _apply_transition(self, event: dict, analysis: dict):
        """Apply validated state transition"""
        # Update current state
        if event['type'] == 'constitutional_change':
            self.current_state['constitutional_version'] = analysis['version_bump']['next']
        
        # Log transition
        self._log_transition(event, analysis)
    
    def _log_transition(self, event: dict, analysis: dict):
        """Log state transition to history"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "analysis": analysis,
            "previous_state": self.current_state.copy()
        }
        
        # In production, append to state log file
        print(f"State transition logged: {json.dumps(log_entry, indent=2)}")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import os
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # ========== METHOD 1: Live Transcript ==========
    print("=" * 60)
    print("METHOD 1: Live Transcript Processing")
    print("=" * 60)
    
    processor1 = LiveTranscriptProcessor(api_key)
    
    video_metadata = {
        "url": "https://www.youtube.com/watch?v=syeQGroWQ80",
        "title": "OBINexus Update on 11-10-2025 Constitution You LIVE ADN WORKTHERE",
        "date": "2025-10-11",
        "duration": "43:22"
    }
    
    # Process transcript
    update = processor1.process_transcript(
        "transcripts/youtube/2025-10-11-constitution-you-live-adn-workthere.txt",
        video_metadata
    )
    
    # Save update note
    output_file = processor1.save_update_note(
        update,
        "updates/2025/10-October/"
    )
    print(f"✓ Update saved: {output_file}")
    
    # ========== METHOD 2: Structured Query ==========
    print("\n" + "=" * 60)
    print("METHOD 2: Structured Query Processing")
    print("=" * 60)
    
    processor2 = StructuredQueryProcessor(api_key)
    
    queries = [
        "What is the Blue Share networking concept mentioned in the update?",
        "How does the ring topology housing model work?",
        "What are the T1, T2, T3 business model tiers?"
    ]
    
    batch_results = processor2.batch_queries(queries)
    print(f"✓ Processed {len(queries)} queries")
    print(f"Summary:\n{batch_results['summary']}")
    
    # ========== METHOD 3: State Machine ==========
    print("\n" + "=" * 60)
    print("METHOD 3: State Machine Processing")
    print("=" * 60)
    
    processor3 = StateMachineProcessor(api_key)
    
    state_change = {
        "type": "constitutional_change",
        "trigger": "cambridge_masters_delayed",
        "target_state": "housing_pilot_expanded",
        "impact": "Shift focus to Thurrock council housing while awaiting Cambridge admission"
    }
    
    transition_analysis = processor3.process_state_change(state_change)
    
    if transition_analysis['transition_valid']:
        print(f"✓ State transition valid")
        print(f"Version bump: {transition_analysis['version_bump']['current']} → {transition_analysis['version_bump']['next']}")
    else:
        print(f"✗ State transition invalid: {transition_analysis['validation_notes']}")
    
    print("\n" + "=" * 60)
    print("All methods completed successfully!")
    print("=" * 60)
