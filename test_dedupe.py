from scripts.lib.deduplicator import Deduplicator
import json

def test_dedupe():
    deduper = Deduplicator()
    
    records = [
        # Same exact content, ArXiv vs RSS
        {
            "unique_id": "arxiv_1",
            "source_type": "arxiv",
            "raw_payload": { "title": "A Great AI Paper", "content": "This is the summary of the paper." }
        },
        {
            "unique_id": "rss_1",
            "source_type": "rss",
            "raw_payload": { "title": "A Great AI Paper", "content": "This is the summary of the paper." }
        },
        # Same title, different casing
        {
            "unique_id": "hf_1",
            "source_type": "huggingface",
            "raw_payload": { "title": "meta-llama-3-8b", "content": "A model." }
        },
        {
            "unique_id": "hf_2",
            "source_type": "huggingface",
            "raw_payload": { "title": "Meta-Llama-3-8B  ", "content": "A model." }
        }
    ]
    
    print("=== SECTION 5: Deduplication Edge Case Test ===")
    print(f"Input records: {len(records)}")
    
    deduped, removed = deduper.remove_duplicates(records)
    
    print(f"Output records: {len(deduped)}")
    print(f"Duplicates removed: {removed}")
    
    if len(deduped) != 2:
        print("FAIL: Expected exactly 2 records remaining.")
        exit(1)
        
    print("SUCCESS: Deduplicator works correctly on edge cases.")

if __name__ == "__main__":
    test_dedupe()
