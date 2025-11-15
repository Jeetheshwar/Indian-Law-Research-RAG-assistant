"""Test script to verify embeddings work correctly."""

print("Testing embeddings import and initialization...")

try:
    print("1. Importing langchain_huggingface...")
    from langchain_huggingface import HuggingFaceEmbeddings
    print("   ✓ Import successful")
    
    print("\n2. Initializing HuggingFaceEmbeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu', 'trust_remote_code': True},
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 32},
        show_progress=False
    )
    print("   ✓ Initialization successful")
    
    print("\n3. Testing embedding generation...")
    test_text = "This is a test document about Indian law."
    embedding = embeddings.embed_query(test_text)
    print(f"   ✓ Generated embedding of length: {len(embedding)}")
    
    print("\n✅ ALL TESTS PASSED!")
    print("Embeddings are working correctly.")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

