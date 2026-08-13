import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add project root to python path so we can import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.conflict_resolver import resolve_conflict

def create_mock_hit(score, metadata, document="mock document"):
    hit = MagicMock()
    hit.score = score
    hit.metadata = metadata
    hit.document = document
    return hit

def test_high_score_proceed():
    mock_state = {"conflict_flag": True, "agent_outputs": {}}
    
    with patch("orchestrator.conflict_resolver.QdrantClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.query.return_value = [
            create_mock_hit(0.95, {"decision": "proceed"})
        ]
        
        result_state = resolve_conflict(mock_state)
        assert result_state["final_decision"] == "proceed_based_on_precedent", \
            f"Expected proceed_based_on_precedent, got {result_state['final_decision']}"

def test_high_score_escalate():
    mock_state = {"conflict_flag": True, "agent_outputs": {}}
    
    with patch("orchestrator.conflict_resolver.QdrantClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.query.return_value = [
            create_mock_hit(0.95, {"decision": "escalate"})
        ]
        
        result_state = resolve_conflict(mock_state)
        assert result_state["final_decision"] == "escalate", \
            f"Expected escalate for escalate metadata, got {result_state['final_decision']}"

def test_high_score_missing_decision():
    mock_state = {"conflict_flag": True, "agent_outputs": {}}
    
    with patch("orchestrator.conflict_resolver.QdrantClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.query.return_value = [
            create_mock_hit(0.95, {"other": "data"})
        ]
        
        result_state = resolve_conflict(mock_state)
        assert result_state["final_decision"] == "escalate", \
            f"Expected escalate for missing decision metadata, got {result_state['final_decision']}"

def test_low_score():
    mock_state = {"conflict_flag": True, "agent_outputs": {}}
    
    with patch("orchestrator.conflict_resolver.QdrantClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.query.return_value = [
            create_mock_hit(0.70, {"decision": "proceed"})
        ]
        
        result_state = resolve_conflict(mock_state)
        assert result_state["final_decision"] == "escalate", \
            f"Expected escalate for low score, got {result_state['final_decision']}"

def run_test():
    print("Running tests for RAG-based Conflict Resolver...")
    test_high_score_proceed()
    print(" - test_high_score_proceed passed")
    test_high_score_escalate()
    print(" - test_high_score_escalate passed")
    test_high_score_missing_decision()
    print(" - test_high_score_missing_decision passed")
    test_low_score()
    print(" - test_low_score passed")
    print("All tests passed!")

if __name__ == "__main__":
    run_test()
