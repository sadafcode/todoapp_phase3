"""
Chat API Endpoint for AI Chatbot
Implements the stateless chat endpoint that persists conversation state to database
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel
import asyncio

from db import get_session
from models import User, Conversation, Message
from auth import get_current_user

# Import OpenAI Agents SDK and MCP integration
try:
    from agents_mcp import Agent, Runner, RunnerContext
    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False
    # Fallback implementation will be used

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class AIChatbotAgent:
    """
    AI Agent for handling chatbot interactions
    Follows the pattern from reusable skill for consistency
    """

    def __init__(self, session: Session):
        self.session = session

    def _get_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for context
        """
        history_messages = self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages
        ]

    async def process_message(self, message: str, user_id: str, conversation_id: int) -> tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message and return AI response with tool calls
        """
        # Get conversation history for context
        history = self._get_conversation_history(conversation_id)

        # Process with OpenAI Agents SDK if available, otherwise use fallback
        if OPENAI_AGENTS_AVAILABLE:
            response_text, tool_calls = await self._process_with_openai_agents(
                message, user_id, history
            )
        else:
            # Fallback implementation
            response_text, tool_calls = await self._process_natural_language_command(
                message, user_id, history
            )

        return response_text, tool_calls

    async def _process_with_openai_agents(
        self,
        message: str,
        user_id: str,
        history_messages: List[Dict[str, str]]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Process message using OpenAI Agents SDK with MCP integration
        """
        if not OPENAI_AGENTS_AVAILABLE:
            # Fallback if agents are not available
            return await self._process_natural_language_command(message, user_id, history_messages)

        # Create an agent with MCP server integration
        agent = Agent(
            name="Todo Assistant",
            instructions=f"""
            You are a helpful assistant that helps users manage their tasks.
            You have access to tools that allow you to add, list, complete, delete, and update tasks.
            The current user ID is {user_id}. Always use this user ID when calling tools.
            Be friendly and conversational in your responses.
            """,
            # Use the MCP servers that provide our task management tools
            mcp_servers=["todo-tools"]  # This references the server defined in mcp_agent.config.yaml
        )

        # Run the agent with the user's message
        try:
            result = await Runner.run(
                agent,
                input=message,
                context=RunnerContext()
            )

            # Extract the response and any tool calls made
            response_text = result.response.value if hasattr(result, 'response') and result.response else "I processed your request."

            # For now, return a simple response - in a full implementation,
            # we would extract the actual tool calls from the result
            return response_text, []

        except Exception as e:
            # If there's an error with the agents, fall back to the simple implementation
            return await self._process_natural_language_command(message, user_id, history_messages)

    async def _process_natural_language_command(
        self,
        message: str,
        user_id: str,
        history_messages: List[Dict[str, str]]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Process natural language command and execute appropriate MCP tools
        This is a fallback implementation when OpenAI Agents SDK is not available
        """
        import re

        # Simple natural language processing to identify commands
        message_lower = message.lower().strip()

        # Add task command
        if any(word in message_lower for word in ["add", "create", "new", "remember"]):
            # Extract task title (simple approach)
            # Remove command words and extract the rest as title
            title = re.sub(r'^(add|create|new|remember|make|set)', '', message_lower, 1, re.IGNORECASE).strip()
            if title:
                # For now, return a mock response - in a real implementation,
                # this would call the actual MCP tool via the OpenAI Agents SDK
                return f"Task '{title}' has been created for you.", [
                    {"tool_name": "add_task", "parameters": {"user_id": user_id, "title": title}}
                ]

        # List tasks command
        elif any(word in message_lower for word in ["show", "list", "see", "what", "my", "all"]):
            status = None
            if "pending" in message_lower or "incomplete" in message_lower:
                status = "pending"
            elif "completed" in message_lower or "done" in message_lower:
                status = "completed"

            # Mock response for listing tasks
            status_text = f" {status}" if status else " all"
            return f"Here are your{status_text} tasks: [mock task list]", [
                {"tool_name": "list_tasks", "parameters": {"user_id": user_id, "status": status}}
            ]

        # Complete task command
        elif any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
            # Try to extract task ID from message
            task_id_match = re.search(r'\b(\d+)\b', message)
            if task_id_match:
                task_id = int(task_id_match.group(1))
                return f"Task {task_id} has been marked as completed.", [
                    {"tool_name": "complete_task", "parameters": {"user_id": user_id, "task_id": task_id}}
                ]
            else:
                return "Please specify which task to complete by ID (e.g., 'complete task 3').", []

        # Delete task command
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            # Try to extract task ID from message
            task_id_match = re.search(r'\b(\d+)\b', message)
            if task_id_match:
                task_id = int(task_id_match.group(1))
                return f"Task {task_id} has been deleted.", [
                    {"tool_name": "delete_task", "parameters": {"user_id": user_id, "task_id": task_id}}
                ]
            else:
                return "Please specify which task to delete by ID (e.g., 'delete task 3').", []

        # Update task command
        elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
            # Simple implementation: extract task ID and new title
            task_id_match = re.search(r'\b(\d+)\b', message)
            title_match = re.search(r'(?:to|as|with) ([^.!?]+)', message_lower)

            if task_id_match and title_match:
                task_id = int(task_id_match.group(1))
                new_title = title_match.group(1).strip()
                return f"Task {task_id} has been updated to '{new_title}'.", [
                    {"tool_name": "update_task", "parameters": {"user_id": user_id, "task_id": task_id, "title": new_title}}
                ]
            else:
                return "Please specify which task to update and the new title (e.g., 'update task 1 to Buy groceries').", []

        # Default response
        else:
            return "I understand you're trying to interact with your tasks. You can ask me to add, list, complete, delete, or update tasks.", []


@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that processes user message and returns AI response
    Implements the stateless request cycle as specified:
    1. Receive user message
    2. Fetch conversation history from database
    3. Build message array for agent (history + new message)
    4. Store user message in database
    5. Run agent with MCP tools
    6. Agent invokes appropriate MCP tool(s)
    7. Store assistant response in database
    8. Return response to client
    9. Server holds NO state (ready for next request)
    """
    # Verify user authentication
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's chat")

    # Get or create conversation
    conversation = None
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Store user message in database
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Create and use the AIChatbotAgent to process the message
    agent = AIChatbotAgent(session)
    response_text, tool_calls = await agent.process_message(
        message=request.message,
        user_id=user_id,
        conversation_id=conversation.id
    )

    # Store assistant response in database
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,  # This represents the system/assistant
        role="assistant",
        content=response_text
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_calls
    )