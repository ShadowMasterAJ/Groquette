"""Custom LLM component for voice agent using Groq's compound-beta model."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from livekit.agents.llm import ChatChunk, ChatContext, ChoiceDelta, LLM, LLMStream
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS

load_dotenv()


class CustomGroqLLM(LLM):
    """Custom Groq LLM that extracts executed_tools from compound-beta responses."""

    def __init__(
        self,
        model: str = "compound-beta",
        api_key: Optional[str] = None,
        room: Any = None,
    ) -> None:
        """Initialize the CustomGroqLLM instance."""
        super().__init__()
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.room = room

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        try:
            from groq import Groq

            self._client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "groq package is required. Install with: pip install groq"
            )

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        conn_options: Optional[Any] = None,
        fnc_ctx: Optional[Any] = None,
        tools: Optional[Any] = None,
        **kwargs: Any,
    ) -> "ChatContextManager":
        """Main chat method that returns an async context manager."""
        return ChatContextManager(self, chat_ctx, conn_options, fnc_ctx, tools, kwargs)

    def _convert_messages(self, chat_ctx: ChatContext) -> List[Dict[str, str]]:
        """Convert ChatContext items to Groq format, filtering out empty messages."""
        messages = []

        for message in chat_ctx.items:
            if not (hasattr(message, "role") and hasattr(message, "content")):
                continue

            content = self._extract_content(message.content)
            if not content.strip():
                continue

            messages.append({"role": str(message.role), "content": content})

        # Compound-beta requires the last message to be from user role
        if self.model == "compound-beta" and messages:
            if len(messages) == 1 and messages[0]["role"] == "system":
                messages.append(
                    {
                        "role": "user",
                        "content": "Briefly greet semi-formally like you are entering a weekly standup with colleagues",
                    }
                )

        return messages

    def _extract_content(self, content_obj: Any) -> str:
        """Extract text content from various content object types."""
        if isinstance(content_obj, str):
            return content_obj
        elif hasattr(content_obj, "text"):
            return str(content_obj.text)
        elif isinstance(content_obj, list):
            return "".join(
                str(part.text) if hasattr(part, "text") else str(part)
                for part in content_obj
            )
        elif content_obj is not None:
            return str(content_obj)
        return ""


class ChatContextManager:
    """Async context manager for chat operations."""

    def __init__(
        self,
        llm: CustomGroqLLM,
        chat_ctx: ChatContext,
        conn_options: Optional[Any],
        fnc_ctx: Optional[Any],
        tools: Optional[Any],
        kwargs: Dict[str, Any],
    ) -> None:
        """Initialize the ChatContextManager."""
        self.llm = llm
        self.chat_ctx = chat_ctx
        self.conn_options = conn_options
        self.fnc_ctx = fnc_ctx
        self.tools = tools
        self.kwargs = kwargs
        self.stream = None

    async def __aenter__(self) -> "CustomGroqLLMStream":
        """Enter the async context manager."""
        messages = self.llm._convert_messages(self.chat_ctx)
        request_id = "unknown_request_id"

        try:
            response = self.llm._client.chat.completions.create(
                model=self.llm.model,
                messages=messages,
                stream=False,
            )

            request_id = getattr(response, "id", request_id)
            choice = response.choices[0]
            executed_tools = getattr(choice.message, "executed_tools", None)

            if executed_tools:
                search_results = self._extract_search_results(executed_tools)
                if search_results:
                    print(f"[DEBUG] Extracted {len(search_results)} search results")

            self.stream = CustomGroqLLMStream(
                llm=self.llm,
                chat_ctx=self.chat_ctx,
                fnc_ctx=self.fnc_ctx,
                conn_options=self.conn_options,
                request_id=request_id,
                content=choice.message.content,
                executed_tools=executed_tools,
                tools=self.tools,
            )
            return self.stream

        except Exception as e:
            print(f"[ERROR] Groq API call failed: {e}")
            self.stream = CustomGroqLLMStream(
                llm=self.llm,
                chat_ctx=self.chat_ctx,
                fnc_ctx=self.fnc_ctx,
                conn_options=self.conn_options,
                request_id=request_id,
                content="I apologize, but I encountered an error processing your request. Please try again.",
                executed_tools=None,
                tools=self.tools,
            )
            return self.stream

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context manager."""
        pass

    def _extract_search_results(self, executed_tools: Any) -> List[Dict[str, Any]]:
        """Extract search results from executed tools."""
        results = []
        try:
            for tool in executed_tools:
                if (
                    hasattr(tool, "type")
                    and tool.type == "search"
                    and hasattr(tool, "search_results")
                    and tool.search_results
                    and hasattr(tool.search_results, "results")
                ):
                    for result in tool.search_results.results:
                        if all(
                            hasattr(result, attr) for attr in ["title", "url", "score"]
                        ):
                            results.append(
                                {
                                    "title": result.title,
                                    "url": result.url,
                                    "score": result.score,
                                }
                            )
        except Exception as e:
            print(f"[ERROR] Error extracting search results: {e}")

        return results


class CustomGroqLLMStream(LLMStream):
    """Custom stream implementation for our Groq LLM."""

    def __init__(
        self,
        llm: LLM,
        chat_ctx: ChatContext,
        fnc_ctx: Optional[Any],
        conn_options: Optional[Any],
        request_id: str,
        content: str,
        executed_tools: Optional[Any] = None,
        tools: Optional[Any] = None,
    ) -> None:
        """Initialize the CustomGroqLLMStream."""
        actual_conn_options = conn_options or DEFAULT_API_CONNECT_OPTIONS

        super().__init__(
            llm, chat_ctx=chat_ctx, tools=tools or [], conn_options=actual_conn_options
        )
        self.request_id = request_id
        self.content = content
        self.executed_tools = executed_tools
        self.fnc_ctx = fnc_ctx
        self._sent = False

    async def _run(self) -> None:
        """Abstract method from LLMStream."""
        pass

    async def __anext__(self) -> ChatChunk:
        """Get the next chunk in the async iteration."""
        if self._sent:
            raise StopAsyncIteration

        self._sent = True

        return ChatChunk(
            id=self.request_id,
            delta=ChoiceDelta(role="assistant", content=self.content),
        )

    def __aiter__(self) -> "CustomGroqLLMStream":
        """Return the async iterator."""
        return self


# Create the LLM component instance
llm_component = CustomGroqLLM()


if __name__ == "__main__":
    print("🧠 Custom Groq LLM Component - compound-beta with tool extraction")
    print("=" * 60)
    print("✅ Model: compound-beta")
    print("✅ Features: executed_tools extraction, search results forwarding")
    print("🔧 Custom implementation for LiveKit Agents compatibility")
