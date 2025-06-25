import os
from dotenv import load_dotenv
from groq import Groq
from phoenix.otel import register

# Load environment variables
load_dotenv()

def setup_phoenix_tracing():
    """Set up Phoenix tracing for Groq instrumentation using the latest Phoenix API"""
    
    # Set Phoenix API key and endpoint from environment variables
    phoenix_api_key = os.getenv("PHOENIX_API_KEY")
    phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
    
    if not phoenix_api_key or not phoenix_endpoint:
        print("❌ Phoenix Cloud configuration missing!")
        print("   Required environment variables:")
        print("   - PHOENIX_API_KEY: Your Phoenix API key")
        print("   - PHOENIX_COLLECTOR_ENDPOINT: Your Phoenix hostname")
        print("   Get these from your Phoenix Cloud Settings page")
        return None
    
    # Set Phoenix environment variables that the register function expects
    os.environ["PHOENIX_API_KEY"] = phoenix_api_key
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = phoenix_endpoint
    
    # If using Phoenix Cloud (created before June 24th, 2025), set headers
    os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={phoenix_api_key}"
    
    try:
        print(f"🔗 Connecting to Phoenix Cloud: {phoenix_endpoint}")
        
        # Configure the Phoenix tracer with auto-instrumentation
        tracer_provider = register(
            project_name=os.getenv("PHOENIX_PROJECT_NAME", "groq-arize-example"),
            auto_instrument=True,  # This will automatically instrument supported libraries
        )
        
        tracer = tracer_provider.get_tracer(__name__)
        
        print("✅ Phoenix Cloud tracing configured successfully")
        print(f"   Project: {os.getenv('PHOENIX_PROJECT_NAME', 'groq-arize-example')}")
        print(f"   Endpoint: {phoenix_endpoint}")
        
        return tracer
    
    except Exception as e:
        print(f"❌ Failed to configure Phoenix Cloud tracing: {e}")
        print("   Please check your API key and endpoint are correct")
        return None

def create_groq_client():
    """Create and return a Groq client"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is required")
        print("   Get your API key from: https://console.groq.com/")
        raise ValueError("GROQ_API_KEY environment variable is required")

    return Groq(api_key=api_key)

def chat_with_groq(client, message, model="llama-3.1-8b-instant"):
    """Send a chat message to Groq and return the response"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling Groq API: {e}")
        return None

def run_conversation_examples(client):
    """Run multiple conversation examples with tracing"""
    examples = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms", 
        "Write a haiku about artificial intelligence",
        "What are the benefits of observability in AI applications?"
    ]
    
    results = []
    print("\n🤖 Running example conversations...")
    print("=" * 50)
    
    for i, message in enumerate(examples, 1):
        print(f"\n💬 Example {i}: {message}")
        response = chat_with_groq(client, message)
        if response:
            print(f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            results.append({"question": message, "response": response})
        print("-" * 30)
    
    return results

def main():
    """Main function demonstrating Groq + Arize Phoenix integration"""
    print("🚀 Starting Groq + Arize Phoenix Cloud Example")
    
    try:
        # Set up Phoenix tracing
        tracer = setup_phoenix_tracing()
        if not tracer:
            print("❌ Cannot proceed without Phoenix tracing configuration")
            return 1
        
        # Create Groq client
        client = create_groq_client()
        print("✅ Groq client created successfully")
        
        # Run conversation examples
        results = run_conversation_examples(client)
        
        print("\n✅ All examples completed!")
        print(f"   Processed {len(results)} conversations")
        print("🔍 Check your Phoenix Cloud dashboard for observability data")
        print("   Phoenix Cloud: https://app.phoenix.arize.com")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
