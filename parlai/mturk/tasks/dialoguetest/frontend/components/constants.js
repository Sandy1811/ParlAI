export const FIELD_VALUE_PREFIX = "fv-";
export const FIELD_OPERATOR_PREFIX = "fo-";

// This includes the initial "ready" message which is required from the turkers
export const FINISHABLE_MESSAGE_COUNT = 3;

export const DEBUG_FLAGS = {
	RENDER_INVISIBLE_MESSAGES: false
};

export const PROTOCOL_CONSTANTS = {
  "front_to_back": {
    "complete_prefix": "<complete>",
    "done_prefix": "<done>",
    "query_prefix": "? ",
    "select_kb_entry_prefix": "<select_knowledge_base_entry>",
    "select_reference_kb_entry_prefix": "<select_reference_knowledge_base_entry>",
    "request_suggestions_prefix": "<request_suggestions>",
    "pick_suggestion_prefix": "<pick_suggestion>"
  },
  "back_to_front": {
    "command_setup": "setup",
    "command_review": "review",
    "command_supply_suggestions": "supply_suggestions"
  },
  "agent_ids": {
    "system_id": "MTurk System",
    "wizard_id": "Assistant",
    "user_id": "User",
    "knowledgebase_id": "Knowledge Base",
    "onboarding_wizard_id": "onboarding",
    "onboarding_user_id": "onboarding"
  }
}