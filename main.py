"""
main.py – Interactive CLI entry point for the Personal AI Assistant.
"""

import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Import the compiled agent
from agent_router import agent, AgentState


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["DEEPSEEK_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the following content:")
        print("DEEPSEEK_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully.")


def print_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("🤖  PERSONAL AI ASSISTANT")
    print("=" * 60)
    print("Welcome to your AI-powered assistant with:")
    print("  • 🌐 Real-time web search (DuckDuckGo)")
    print("  • 🖥️  System diagnostics (CPU, Memory, Network)")
    print("  • 💬 General conversation and coding help")
    print("  • 🧠 DeepSeek LLM backend")
    print("\nCommands:")
    print("  • Type your question naturally")
    print("  • Try: 'search for Python 3.12 features'")
    print("  • Try: 'show me system info'")
    print("  • Try: 'ping google.com'")
    print("  • Type 'exit', 'quit', or press Ctrl+C to quit")
    print("=" * 60 + "\n")


def format_message(message: BaseMessage) -> str:
    """
    Format a message for display in the CLI.
    
    Args:
        message: A LangChain message object.
    
    Returns:
        Formatted string representation.
    """
    if isinstance(message, HumanMessage):
        return f"👤 You: {message.content}"
    elif isinstance(message, AIMessage):
        return f"🤖 AI: {message.content}"
    else:
        return f"📝 {message.content}"


def run_interactive_session():
    """
    Run the interactive CLI session.
    """
    # Initialize message history
    messages: List[BaseMessage] = []
    state: AgentState = {
        "messages": messages,
        "next_step": "chat"
    }
    
    print_welcome()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q", "bye"]:
                print("\n🤖 AI: Goodbye! Have a great day! 👋")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Add user message to state
            user_message = HumanMessage(content=user_input)
            state["messages"].append(user_message)
            
            # Run the agent
            print("\n⏳ Thinking...")
            
            try:
                result = agent.invoke(state)
                
                # Update state with the result
                state = result
                
                # Display the assistant's response
                if state.get("messages"):
                    last_message = state["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        print(f"\n🤖 AI: {last_message.content}")
                    else:
                        print(f"\n{format_message(last_message)}")
                
                # Show a separator after the response
                print("\n" + "-" * 60)
                
            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")
                print("Please try again with a different question.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("Please try again.")


def main():
    """Main entry point for the application."""
    # Load environment
    load_environment()
    
    # Run the interactive session
    try:
        run_interactive_session()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()