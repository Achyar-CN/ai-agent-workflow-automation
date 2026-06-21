"""Agent 4 — Cold-email drafting.

Runs only for qualified (GO) leads. Personalizes the email to the top key person
using true facts from the profile and recent signals, and reports the hooks used."""

from __future__ import annotations

from ...llm.prompts import DRAFT_SYSTEM
from ...llm.provider import LLMError, generate_structured
from ...schemas import EmailDraft, KeyPerson
from ..state import LeadResearchState, emit


async def draft_node(state: LeadResearchState) -> dict:
    emit("draft", "start", message="Drafting personalized email…")

    profile = state["company_profile"]
    icp = state["icp"]
    people: list[KeyPerson] = state.get("key_people", [])
    recipient = people[0] if people else None

    user = (
        f"Sender: {icp.sender_name}, {icp.sender_role} at {icp.sender_company}\n"
        f"Sender value proposition: {icp.value_proposition}\n\n"
        f"Recipient: {recipient.name if recipient else 'the most relevant decision-maker'}"
        f"{f' ({recipient.title})' if recipient and recipient.title else ''}\n\n"
        f"Target company profile:\n{profile.model_dump_json(indent=2)}\n\n"
        "Write the personalized cold email."
    )

    try:
        draft = await generate_structured(DRAFT_SYSTEM, user, EmailDraft)
        if recipient and not draft.recipient:
            draft.recipient = recipient.name
    except LLMError as exc:
        draft = EmailDraft(
            recipient=recipient.name if recipient else "",
            subject=f"Quick idea for {profile.name}",
            body=f"(Draft unavailable: {exc})",
        )

    emit("draft", "done", data=draft.model_dump())
    return {"email_draft": draft}
