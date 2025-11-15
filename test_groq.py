"""Test Groq API connection."""
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

print("Testing Groq API connection...\n")

# Get API key
groq_api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("LLM_MODEL", "moonshotai/kimi-k2-instruct-0905")

print(f"1. Groq API Key: {'✓ Found' if groq_api_key else '✗ Missing'}")
if groq_api_key:
    print(f"   Key starts with: {groq_api_key[:10]}...")
print(f"2. Model: {model_name}\n")

if not groq_api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")
    print("\nPlease add your Groq API key to the .env file:")
    print("GROQ_API_KEY=your_groq_api_key_here")
    exit(1)

# Test API connection
print("3. Testing Groq API connection...")
try:
    client = Groq(api_key=groq_api_key)
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": "Say 'Hello' in one word."}
        ],
        temperature=0.6,
        max_tokens=10,
        top_p=1,
        stream=False
    )
    
    print("   ✓ API connection successful")
    print(f"   Response: {response.choices[0].message.content}\n")
    print("✅ ALL TESTS PASSED!")
    print("Your Groq API is working correctly with Kimi K2 model!")
    
except Exception as e:
    print(f"   ✗ API connection failed: {str(e)}\n")
    
    # Check error type
    if "401" in str(e) or "unauthorized" in str(e).lower():
        print("❌ AUTHENTICATION ERROR")
        print("Your Groq API key might be invalid.")
        print("\nTo fix this:")
        print("1. Go to https://console.groq.com/keys")
        print("2. Create a new API key")
        print("3. Update your .env file with the new key")
    
    elif "404" in str(e) or "not found" in str(e).lower():
        print("❌ MODEL NOT FOUND")
        print("The model might not be available on Groq.")
        print("\nAvailable models on Groq:")
        print("- moonshotai/kimi-k2-instruct-0905")
        print("- llama-3.3-70b-versatile")
        print("- mixtral-8x7b-32768")
    
    elif "429" in str(e) or "rate limit" in str(e).lower():
        print("❌ RATE LIMIT EXCEEDED")
        print("You've hit the API rate limit.")
        print("\nWait a few minutes and try again.")
    
    else:
        print("❌ UNKNOWN ERROR")
        print(f"Error details: {str(e)}")

