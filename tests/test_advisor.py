from forgemind.advisor import advise
from forgemind.core import Node
from forgemind.knowledge import KnowledgeBase


def test_advisor_returns_explainable_ordered_recommendations():
    candidates = [
        [Node("U", "rev"), Node("U", "sort"), Node("U", "neg")],
        [Node("U", "rev")],
    ]
    result = advise(candidates, knowledge_base=KnowledgeBase())
    assert len(result) == 2
    assert result[0].experimental_value >= result[1].experimental_value
    assert result[0].as_dict()["recommendation"]
    assert result[0].score.reasons
