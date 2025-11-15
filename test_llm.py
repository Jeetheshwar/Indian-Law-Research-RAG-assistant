"""Test HuggingFace token and Kimi K2 model access."""
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

print("Testing HuggingFace API and Kimi K2 model access...\n")

# Get token
hf_token = os.getenv("HF_TOKEN")
model_name = os.getenv("LLM_MODEL", "moonshotai/Kimi-K2-Thinking")

print(f"1. HuggingFace Token: {'✓ Found' if hf_token else '✗ Missing'}")
if hf_token:
    print(f"   Token starts with: {hf_token[:10]}...")
print(f"2. Model: {model_name}\n")

# Test token validity
print("3. Testing token validity...")
try:
    client = InferenceClient(token=hf_token)
    print("   ✓ Token is valid\n")
except Exception as e:
    print(f"   ✗ Token validation failed: {str(e)}\n")
    exit(1)

# Test model access
print("4. Testing Kimi K2 model access...")
try:
    response = client.chat_completion(
        model=model_name,
        messages=[
            {"role": "user", "content": "Say 'Hello' in one word."}
        ],
        max_tokens=10,
        temperature=0.1
    )
    
    print("   ✓ Model is accessible")
    print(f"   Response: {response.choices[0].message.content}\n")
    print("✅ ALL TESTS PASSED!")
    print("Your HuggingFace token and Kimi K2 model are working correctly.")
    
except Exception as e:
    print(f"   ✗ Model access failed: {str(e)}\n")
    
    # Check if it's an authentication error
    if "401" in str(e) or "unauthorized" in str(e).lower():
        print("❌ AUTHENTICATION ERROR")
        print("Your HuggingFace token might be invalid or expired.")
        print("\nTo fix this:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Read' access")
        print("3. Update your .env file with the new token")
    
    # Check if it's a model access error
    elif "404" in str(e) or "not found" in str(e).lower():
        print("❌ MODEL NOT FOUND")
        print("The Kimi K2 model might not be available or accessible.")
        print("\nTo fix this:")
        print("1. Check if the model exists: https://huggingface.co/moonshotai/Kimi-K2-Thinking")
        print("2. You might need to accept the model's terms of use")
        print("3. Or try a different model like 'meta-llama/Llama-3.2-3B-Instruct'")
    
    # Check if it's a rate limit error
    elif "429" in str(e) or "rate limit" in str(e).lower():
        print("❌ RATE LIMIT EXCEEDED")
        print("You've hit the API rate limit.")
        print("\nTo fix this:")
        print("1. Wait a few minutes and try again")
        print("2. Consider upgrading to HuggingFace Pro for higher limits")
    
    else:
        print("❌ UNKNOWN ERROR")
        print(f"Error details: {str(e)}")
        print("\nTry:")
        print("1. Check your internet connection")
        print("2. Verify the model is available")
        print("3. Check HuggingFace status: https://status.huggingface.co/")

