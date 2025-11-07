"""
CapAmerica Headwear Catalog Assistant - RAG Implementation
AI-powered sales assistant for headwear product catalog using Pinecone vector database

Features:
- Function-based architecture for flexibility
- User-specific conversation memory with MemorySaver
- Specialized headwear product recommendations and pricing
- Product catalog search (JSON/TXT data)
- Website content retrieval (CSV data)
- Multi-step retrieval for complex product queries
- Pricing calculations and customization guidance
"""

import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain imports
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.documents import Document

# LangGraph imports
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Pinecone imports
from pinecone import Pinecone

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables for models and stores
llm = None
embeddings = None
csv_vector_store = None
pdf_vector_store = None
conversational_graph = None
agent_executor = None
memory_saver = None

# Removed crisis detection - not needed for generic document Q&A

def initialize_models(model_name: str = "gpt-4o-mini"):
    """Initialize chat model and embeddings"""
    global llm, embeddings
    
    # Initialize chat model
    llm = init_chat_model(model_name, model_provider="openai")
    
    # Initialize embeddings model - using text-embedding-3-large
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    print("✅ Models initialized successfully")

def setup_pinecone_connections(csv_index_name: str = "cap-website-data", 
                              pdf_index_name: str = "cap-rag-index"):
    """Setup connections to Pinecone vector databases"""
    global csv_vector_store, pdf_vector_store
    
    # Get API key from environment
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    
    # Connect to CSV index (interview and synthetic data)
    try:
        csv_index = pc.Index(csv_index_name)
        csv_vector_store = PineconeVectorStore(
            embedding=embeddings,
            index=csv_index
        )
        print(f"✅ Connected to CSV vector store: {csv_index_name}")
    except Exception as e:
        print(f"⚠️ Could not connect to CSV index: {e}")
        csv_vector_store = None
    
    # Connect to PDF index (research papers and textbooks)
    try:
        pdf_index = pc.Index(pdf_index_name)
        pdf_vector_store = PineconeVectorStore(
            embedding=embeddings,
            index=pdf_index
        )
        print(f"✅ Connected to PDF vector store: {pdf_index_name}")
    except Exception as e:
        print(f"⚠️ Could not connect to PDF index: {e}")
        pdf_vector_store = None

def create_retrieval_tools():
    """Create retrieval tools for different data sources"""
    
    @tool(response_format="content_and_artifact")
    def retrieve_csv_data(query: str):
        """Retrieve website content and structured data about CapAmerica company, services, and general information."""
        if not csv_vector_store:
            return "CSV vector store not available", []
        
        try:
            retrieved_docs = csv_vector_store.similarity_search(query, k=3)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                 f"Type: {doc.metadata.get('category', 'Unknown')}\n"
                 f"Data Source: Website/CSV\n"
                 f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        except Exception as e:
            return f"Error retrieving website data: {e}", []
    
    @tool(response_format="content_and_artifact")
    def retrieve_product_catalog(query: str):
        """Retrieve headwear product catalog information including caps, pricing, features, colors, customization options, and decoration pricing."""
        if not pdf_vector_store:
            return "Product catalog not available", []
        
        try:
            retrieved_docs = pdf_vector_store.similarity_search(query, k=3)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                 f"Category: {doc.metadata.get('category', 'Unknown')}\n"
                 f"Product ID: {doc.metadata.get('product_id', 'N/A')}\n"
                 f"Data Source: Product Catalog\n"
                 f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        except Exception as e:
            return f"Error retrieving product catalog: {e}", []
    
    tools = [retrieve_csv_data, retrieve_product_catalog]
    print("✅ Retrieval tools setup complete")
    return tools

def get_headwear_catalog_system_prompt() -> str:
    """Get the specialized system prompt for headwear catalog assistant"""
    return """You are a professional and knowledgeable sales assistant for CapAmerica, specializing in custom headwear and branded caps. Your role is to help customers find the perfect headwear products, provide accurate pricing information, and explain customization options.

**CORE PRINCIPLES:**
- Provide accurate product information based on the catalog data
- Help customers find products that match their needs (style, features, price, colors)
- Explain pricing tiers, embroidery options, and customization clearly
- Mention stock availability when relevant
- Be friendly, professional, and solution-oriented

**PRODUCT KNOWLEDGE:**
You have access to our complete headwear catalog including:
- **10+ Cap Styles**: Performance caps, trucker caps, snap backs, visors, foam truckers, 5-7 panel caps
- **Key Features**: UV protection, moisture wicking, water-resistant options, various closures (snap back, hook & loop)
- **Materials**: Polyester, poly/cotton blends, poly/spandex, mesh backs, foam
- **Colors**: 20+ color options (Black, Navy, Gray, White, Red, Maroon, Royal, and more)
- **Sizing**: OSFM (One Size Fits Most), XS, S, M, L, XL, XXL options

**PRICING STRUCTURE:**
- **Quantity Tiers**: 15, 24, 48, 96, 144, 576, 2500+ units
- **Base Pricing**: Includes standard flat embroidery (up to 10,000 stitches)
- **Price Range**: $9.00 - $27.00 per unit depending on style and quantity
- **3D Embroidery**: Additional $3-5 per unit over flat embroidery

**CUSTOMIZATION OPTIONS:**
- **Embroidery Locations**: Front panel (included), side/back ($3.00), across back seam ($3.00)
- **Patches**: Molded rubber ($6), leather ($4-5), woven ($5), embroidered ($4), sublimated ($4)
- **Special Options**: Custom labels ($0.90), American flag patch ($5), poms ($1.40-5.00)
- **Extra Stitches**: $0.80 per 1,000 stitches beyond base allowance

**RESPONSE GUIDELINES:**
1. **Product Recommendations**: Suggest products based on customer needs (features, budget, style)
2. **Pricing Clarity**: Always specify quantity tiers and embroidery type when discussing prices
3. **Feature Highlighting**: Emphasize relevant features (UV protection, moisture wicking, water-resistant, etc.)
4. **Color Options**: Mention available colors and note any out-of-stock items
5. **Comparison**: Help compare similar products when customers are deciding
6. **Customization Guidance**: Explain decoration options clearly and calculate add-on costs
7. **Stock Awareness**: Inform customers about stock status when available

**WHEN ANSWERING QUESTIONS:**
- Start with the most relevant products/information
- Use bullet points for product features and pricing tiers
- Provide product IDs (e.g., i7041, i8502) for easy reference
- Calculate total pricing when asked (base price + add-ons)
- Suggest alternatives if exact request isn't available

**CONVERSATION STYLE:**
- Friendly and professional sales assistant tone
- Use clear, jargon-free language
- Ask clarifying questions about quantity, budget, or specific needs
- Be enthusiastic about products while staying factual
- Offer to provide more details or alternatives

**DATA SOURCES:**
1. **JSON Product Catalog**: Detailed product information with pricing, features, colors, and sizing
2. **TXT Pricing Files**: Decoration options, patch pricing, and add-on costs
3. **Marketing Content**: Free samples information and quality promises

**EXAMPLE INTERACTIONS:**
- "Looking for affordable navy caps" → Suggest i8505 ($11.50-13.00) or i3057 ($12.00)
- "Need UV protection for outdoor events" → Highlight i7041, i8530, i8540 with UV features
- "What's the cost for leather patches?" → Explain genuine leather ($5) vs faux leather ($4) options
- "Bulk order pricing for 200 units" → Use 144-tier pricing as reference point

Remember: Your goal is to help customers find the right headwear products and understand all costs involved. Be consultative, accurate, and helpful. Always base recommendations on the actual catalog data."""

# Crisis detection removed - not needed for generic document Q&A

def setup_conversational_chain(tools):
    """Setup conversational RAG chain with user-specific memory"""
    global conversational_graph, memory_saver
    
    # Create user-specific memory saver
    memory_saver = MemorySaver()
    
    # Create graph builder
    graph_builder = StateGraph(MessagesState)
    
    # Node 1: Query processing
    def process_query(state: MessagesState):
        """Process query and generate tool calls or direct response."""
        # Normal processing with tools
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    # Node 2: Tool execution (retrieval)
    tools_node = ToolNode(tools)
    
    # Node 3: Generate response using retrieved content
    def generate_document_response(state: MessagesState):
        """Generate response using retrieved document context."""
        # Get recent tool messages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]
        
        # Format retrieved content
        if tool_messages:
            docs_content = "\n\n".join(doc.content for doc in tool_messages)
            context_prompt = f"""
**RETRIEVED CATALOG INFORMATION:**
{docs_content}

**Instructions:** Use this product catalog information to help the customer. Provide specific product recommendations with IDs, pricing for their quantity needs, and relevant features. Calculate total costs when customization is discussed. If you have product information, be specific with names, IDs, and prices. If the catalog doesn't have exactly what they need, suggest the closest alternatives.
"""
        else:
            context_prompt = "**No specific catalog data retrieved - Ask the customer for more details about what they're looking for (style, quantity, budget, features) so you can search the catalog more effectively.**"
        
        # Filter conversation messages (exclude tool calls)
        conversation_messages = []
        for message in state["messages"]:
            if message.type in ("human", "system"):
                conversation_messages.append(message)
            elif message.type == "ai":
                # Only include AI messages that don't have tool calls
                try:
                    if not hasattr(message, 'tool_calls') or not message.tool_calls:
                        conversation_messages.append(message)
                except Exception:
                    # If there's any issue checking tool_calls, include the message
                    conversation_messages.append(message)
            # Skip tool messages completely
        
        # Create the prompt with system message
        system_prompt = get_headwear_catalog_system_prompt() + "\n\n" + context_prompt
        prompt = [SystemMessage(system_prompt)] + conversation_messages
        
        # Generate response
        try:
            response = llm.invoke(prompt)
            return {"messages": [response]}
        except Exception as e:
            print(f"Error generating response: {e}")
            # Return a fallback response
            fallback_response = AIMessage(content="I'm here to support you, but I'm experiencing some technical difficulties right now. Please try rephrasing your question or contact support if the issue persists.")
            return {"messages": [fallback_response]}
    
    # Add nodes to graph
    graph_builder.add_node("process_query", process_query)
    graph_builder.add_node("tools", tools_node)
    graph_builder.add_node("generate_response", generate_document_response)
    
    # Set entry point and edges
    graph_builder.set_entry_point("process_query")
    graph_builder.add_conditional_edges(
        "process_query",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate_response")
    graph_builder.add_edge("generate_response", END)
    
    # Compile with user-specific memory
    conversational_graph = graph_builder.compile(checkpointer=memory_saver)
    
    print("✅ Conversational RAG chain with user-specific memory setup complete")

def setup_agent(tools):
    """Setup ReAct agent for complex product queries"""
    global agent_executor
    
    # Create agent with user-specific memory
    agent_executor = create_react_agent(
        llm, 
        tools, 
        checkpointer=memory_saver
    )
    print("✅ Headwear Catalog agent setup complete")

def initialize_rag_system(csv_index_name: str = "cap-website-data",
                         pdf_index_name: str = "cap-rag-index",
                         model_name: str = "gpt-4o-mini"):
    """Initialize the complete RAG system"""
    print("🚀 Initializing CapAmerica Headwear Catalog System...")
    
    # Initialize models
    initialize_models(model_name)
    
    # Setup Pinecone connections
    setup_pinecone_connections(csv_index_name, pdf_index_name)
    
    # Create retrieval tools
    tools = create_retrieval_tools()
    
    # Setup conversational chain
    setup_conversational_chain(tools)
    
    # Setup agent
    setup_agent(tools)
    
    print("✅ CapAmerica Headwear Catalog System ready to help customers!")

def get_user_config(user_id: str) -> Dict[str, Any]:
    """Get configuration for user-specific memory thread"""
    return {"configurable": {"thread_id": f"user_{user_id}"}}

def detect_data_source_from_response(response_content: str) -> str:
    """Detect which data source was used based on the response content"""
    if not response_content:
        return "none"
    
    has_csv = "Data Source: CSV" in response_content
    has_pdf = "Data Source: PDF" in response_content
    
    if has_csv and has_pdf:
        return "both"
    elif has_csv:
        return "csv"
    elif has_pdf:
        return "pdf"
    else:
        return "none"

def get_response(message: str, user_id: str, use_agent: bool = False) -> Dict[str, Any]:
    """
    Get response for API endpoint with user-specific memory
    
    Args:
        message: User's message
        user_id: Unique user identifier for conversation threading
        use_agent: Whether to use agent mode for complex queries
        
    Returns:
        Dict with response data including data source information
    """
    try:
        config = get_user_config(user_id)
        
        response_data = {
            "user_id": user_id,
            "query": message,
            "response": "",
            "mode": "agent" if use_agent else "counselor",
            "data_source": "none",
            "timestamp": time.time(),
            "status_code": 200
        }
        
        # Store all messages to analyze data sources
        all_messages = []
        
        # Choose between conversational chain or agent
        try:
            if use_agent:
                # Agent mode
                events = list(agent_executor.stream(
                    {"messages": [{"role": "user", "content": message}]},
                    stream_mode="values",
                    config=config,
                ))
                if events:
                    last_event = events[-1]
                    if "messages" in last_event and last_event["messages"]:
                        response_data["response"] = last_event["messages"][-1].content
                    all_messages = last_event.get("messages", [])
            else:
                # Counselor mode
                steps = list(conversational_graph.stream(
                    {"messages": [{"role": "user", "content": message}]},
                    stream_mode="values",
                    config=config,
                ))
                if steps:
                    last_step = steps[-1]
                    if "messages" in last_step and last_step["messages"]:
                        response_data["response"] = last_step["messages"][-1].content
                    all_messages = last_step.get("messages", [])
        except Exception as stream_error:
            print(f"Error in conversation stream: {stream_error}")
            response_data["response"] = "I'm experiencing some technical difficulties. Please try again or rephrase your question."
            response_data["data_source"] = "none"
            response_data["status_code"] = 500
            return response_data
        
        # Analyze data sources from tool messages
        data_sources_used = set()
        try:
            for msg in all_messages:
                if hasattr(msg, 'type') and msg.type == "tool":
                    if hasattr(msg, 'content') and msg.content:
                        content = str(msg.content)
                        if "Data Source: CSV" in content:
                            data_sources_used.add("csv")
                        if "Data Source: PDF" in content:
                            data_sources_used.add("pdf")
        except Exception as e:
            print(f"Warning: Error analyzing data sources: {e}")
            # Continue without data source info
        
        # Determine data source
        if len(data_sources_used) > 1:
            response_data["data_source"] = "both"
        elif "csv" in data_sources_used:
            response_data["data_source"] = "csv"
        elif "pdf" in data_sources_used:
            response_data["data_source"] = "pdf"
        else:
            response_data["data_source"] = "none"
        
        # Fallback response if no response generated
        if not response_data["response"]:
            response_data["response"] = "I'm here to help, but I'm having trouble processing your message right now. Could you please try rephrasing your question?"
            response_data["data_source"] = "none"
        
        return response_data
        
    except Exception as e:
        return {
            "user_id": user_id,
            "query": message,
            "response": f"I apologize, but I encountered an error while processing your message. Please try again. If the problem persists, please contact support.",
            "error": str(e),
            "mode": "error",
            "data_source": "none",
            "timestamp": time.time(),
            "status_code": 500
        }

def chat_interactive(message: str, user_id: str, use_agent: bool = False):
    """Interactive chat interface for console use"""
    config = get_user_config(user_id)
    
    print(f"\n👤 Customer ({user_id}): {message}")
    print("=" * 60)
    
    # Choose between conversational chain or agent
    if use_agent:
        print("🤖 Agent Mode: Detailed catalog search")
        for event in agent_executor.stream(
            {"messages": [{"role": "user", "content": message}]},
            stream_mode="values",
            config=config,
        ):
            event["messages"][-1].pretty_print()
    else:
        print("🤖 Sales Assistant Mode: Product recommendations")
        for step in conversational_graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            stream_mode="values",
            config=config,
        ):
            step["messages"][-1].pretty_print()

def get_conversation_summary(user_id: str) -> str:
    """Get a summary of the conversation for continuity"""
    return f"Conversation thread: user_{user_id} - Headwear catalog inquiry"

def clear_conversation(user_id: str):
    """Clear conversation memory for a user"""
    print(f"🧹 Cleared conversation memory for user: {user_id}")
    # The MemorySaver automatically handles user-specific threads

def interactive_document_chat():
    """Interactive headwear catalog chat session"""
    print("🧢 CapAmerica Headwear Catalog Assistant")
    print("=" * 50)
    print("Welcome! I'm here to help you find the perfect headwear products.")
    print("Type 'quit' to exit, 'agent' to use agent mode, 'clear' to clear conversation.")
    print("=" * 50)
    
    # Initialize the system
    try:
        initialize_rag_system()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        print("💡 Make sure your Pinecone indexes are created and API keys are set")
        return
    
    # Start conversation
    user_id = f"session_{int(time.time())}"
    use_agent = False
    
    while True:
        try:
            user_input = input(f"\n💬 You ({user_id}): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for exploring our catalog. Have a great day!")
                break
            elif user_input.lower() == 'agent':
                use_agent = not use_agent
                mode = "Agent" if use_agent else "Sales Assistant"
                print(f"\n🔄 Switched to {mode} mode")
                continue
            elif user_input.lower() == 'clear':
                clear_conversation(user_id)
                user_id = f"session_{int(time.time())}"
                continue
            elif not user_input:
                continue
            
            # Process the message
            chat_interactive(user_input, user_id, use_agent)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for exploring our catalog. Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or type 'quit' to exit.")

def demo_document_scenarios():
    """Demonstrate various headwear catalog scenarios"""
    print("🧢 CapAmerica Catalog Assistant - Demo Scenarios")
    print("=" * 60)
    
    try:
        initialize_rag_system()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Demo scenarios
    scenarios = [
        {
            "title": "Product Discovery",
            "message": "I need lightweight caps with UV protection for outdoor events. What do you have?",
            "use_agent": False,
            "user_id": "demo_customer_1"
        },
        {
            "title": "Pricing Inquiry",
            "message": "What's the cost for 100 navy blue trucker caps with embroidered patches?",
            "use_agent": True,
            "user_id": "demo_customer_2"
        },
        {
            "title": "Customization Options",
            "message": "Tell me about the different patch and embroidery options you offer.",
            "use_agent": False,
            "user_id": "demo_customer_3"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print("-" * 40)
        
        chat_interactive(
            scenario['message'], 
            scenario['user_id'], 
            scenario['use_agent']
        )
        
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    # Choose demo or interactive mode
    print("🧢 CapAmerica Headwear Catalog Assistant")
    print("1. Interactive Chat")
    print("2. Demo Scenarios")
    
    choice = input("\nChoose mode (1 or 2): ").strip()
    
    if choice == "2":
        demo_document_scenarios()
    else:
        interactive_document_chat()