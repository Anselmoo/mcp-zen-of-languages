"""Explicit universal-dogma assignments for Ansible rule mappings."""

from __future__ import annotations


ANSIBLE_RULE_DOGMAS = {
    "ansible-001": ["ZEN-EXPLICIT-INTENT"],
    "ansible-002": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-003": ["ZEN-RIGHT-ABSTRACTION"],
    "ansible-004": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-005": ["ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"],
    "ansible-006": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-007": ["ZEN-PROPORTIONATE-COMPLEXITY"],
    "ansible-008": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-009": ["ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"],
    "ansible-010": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-011": ["ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"],
    "ansible-012": ["ZEN-EXPLICIT-INTENT"],
    "ansible-013": ["ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"],
    "ansible-014": ["ZEN-STRICT-FENCES", "ZEN-PROPORTIONATE-COMPLEXITY"],
    "ansible-015": ["ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-RETURN-EARLY"],
    "ansible-016": ["ZEN-EXPLICIT-INTENT"],
    "ansible-017": ["ZEN-RIGHT-ABSTRACTION"],
    "ansible-018": ["ZEN-RIGHT-ABSTRACTION"],
    "ansible-019": ["ZEN-UNAMBIGUOUS-NAME"],
    "ansible-020": ["ZEN-FAIL-FAST"],
}


__all__ = ["ANSIBLE_RULE_DOGMAS"]
