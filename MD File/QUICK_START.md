# Quick Start Guide - JSON/TXT to Pinecone

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Pinecone API Key
- OpenAI API Key

---

## Step 1: Install Dependencies

```bash
pip install langchain langchain-openai langchain-pinecone pinecone-client python-dotenv pandas
```

Or if you have a `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## Step 2: Set Up Environment Variables

Create a `.env` file in your project root:

```env
PINECONE_API_KEY=your-pinecone-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

**Where to get API keys:**
- **Pinecone**: https://app.pinecone.io/ (Sign up → Create API key)
- **OpenAI**: https://platform.openai.com/api-keys (Sign up → Create API key)

---

## Step 3: Verify Your Data

Make sure your `data/` folder contains:

```
data/
├── caps_catalog_v2.json    ✅ (10 products)
├── caps_catalog1.json      ✅ (10 products)
├── v3.json                 ✅ (10 products)
├── txt1.txt                ✅ (Patch options)
├── txt2.txt                ✅ (Base pricing)
└── json3.txt               ✅ (Marketing info)
```

---

## Step 4: Run the Test Script

```bash
python test_json_txt_upload.py
```

**What it does:**
1. ✅ Analyzes your JSON and TXT files
2. ✅ Shows file structure and content
3. ✅ Asks if you want to upload to Pinecone
4. ✅ Creates vector embeddings
5. ✅ Uploads to Pinecone index
6. ✅ Tests search functionality

**Expected output:**
```
============================================================
🧢 HEADWEAR CATALOG - PINECONE VECTOR STORE TEST
============================================================

📋 Step 1: Initializing Manager...
📁 Data directory: data
✅ Connected to Pinecone index: headwear-catalog
✅ JSONTXTPineconeManager initialized

📊 Step 2: Analyzing Data Files...

📋 JSON Files (3):
   📄 caps_catalog_v2.json - 10.8 KB - 10 products
   📄 caps_catalog1.json - 10.8 KB - 10 products
   📄 v3.json - 9.3 KB - 10 products

📝 TXT Files (3):
   📄 txt1.txt - 0.52 KB - 24 lines - pricing_patches
   📄 txt2.txt - 2.3 KB - 125 lines - pricing_base
   📄 json3.txt - 0.41 KB - 14 lines - product_catalog_info

💡 Do you want to create and upload vector store? (yes/no): 
```

**Type `yes` and press Enter** to proceed.

---

## Step 5: Test Searches

After upload completes, the script automatically tests 3 searches:

### Test 1: Product Search
```
🔍 Search Test 1: Product Search - 'lightweight performance cap'
```
Returns products matching the description.

### Test 2: Pricing Search
```
🔍 Search Test 2: Pricing Search - 'patch options cost'
```
Returns pricing information from TXT files.

### Test 3: General Search
```
🔍 Search Test 3: General Search - 'trucker mesh cap navy blue'
```
Returns relevant products and info.

---

## Step 6: Use in Your Code

### Basic Usage

```python
from vector_store.json_txt_pinecone import JSONTXTPineconeManager

# Initialize
manager = JSONTXTPineconeManager(
    data_dir="data",
    index_name="headwear-catalog"
)

# Search products
results = manager.search_products_only("lightweight cap", k=3)

# Search pricing
results = manager.search_pricing_only("patch cost", k=2)

# General search
results = manager.search_vectors("navy trucker cap", k=5)
```

### Advanced Usage

```python
# Load vector store (for existing index)
vector_store = manager.load_vector_store()

# Direct similarity search
docs = vector_store.similarity_search("UV protection cap", k=3)

# Search with metadata filter
docs = vector_store.similarity_search(
    "performance cap",
    k=5,
    filter={"has_stock_issues": False}
)

# Get statistics
stats = manager.get_statistics()
```

---

## 📊 Understanding Results

When you search, results look like this:

```
============================================================
📄 Result 1:
Source: caps_catalog_v2.json
Type: json
Category: headwear_product
Product ID: i7041
Base Price: $15.25

Content Preview:
Product ID: i7041
Title: Lightweight Aerated Performance Cap

Features:
- Medium profile six panel structured cap
- Modified flat visor
- 100% aerated polyester fabric
- UV protection & moisture wicking
- Adjustable snap back closure

Sizing: XS / OSFM

Pricing:
Flat Embroidery:
  24 units: $17.5
  48 units: $15.75
...
```

---

## 🔧 Customization

### Change Index Name

```python
manager = JSONTXTPineconeManager(
    data_dir="data",
    index_name="my-custom-catalog"  # Change this
)
```

### Use Different Embedding Model

```python
manager = JSONTXTPineconeManager(
    data_dir="data",
    index_name="headwear-catalog",
    embedding_model="text-embedding-3-small"  # Faster, cheaper
)
```

### Filter Searches

```python
# Only products from specific file
manager.search_vectors(
    "cap",
    k=5,
    filter_dict={"source": "caps_catalog_v2.json"}
)

# Only TXT files
manager.search_vectors(
    "pricing",
    k=3,
    filter_dict={"file_type": "txt"}
)

# Only specific category
manager.search_vectors(
    "patch",
    k=3,
    filter_dict={"category": "pricing_patches"}
)
```

---

## 🐛 Troubleshooting

### Error: "PINECONE_API_KEY not found"
**Solution**: Create `.env` file with your API keys in project root.

### Error: "No JSON files found"
**Solution**: Verify `data/` folder path and that JSON files exist.

### Error: Module not found
**Solution**: Install dependencies:
```bash
pip install langchain langchain-openai langchain-pinecone pinecone-client python-dotenv pandas
```

### Slow Upload Speed
**Normal**: Embedding 30+ documents takes time (~30-60 seconds).

### Search Returns No Results
**Solution**: 
1. Verify upload completed successfully
2. Try broader search terms
3. Check if index name matches

---

## 🎯 Common Use Cases

### Use Case 1: Find Specific Product

```python
manager = JSONTXTPineconeManager(index_name="headwear-catalog")

# Search by features
results = manager.search_products_only(
    "trucker cap with mesh back and snap closure",
    k=3
)

for doc in results:
    print(f"Product: {doc.metadata['title']}")
    print(f"ID: {doc.metadata['product_id']}")
    print(f"Price: ${doc.metadata.get('base_price', 'N/A')}")
```

### Use Case 2: Get Pricing Info

```python
# Search for patch pricing
results = manager.search_pricing_only("leather patch cost", k=2)

for doc in results:
    print(doc.page_content)
```

### Use Case 3: Build RAG Chatbot

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Initialize
manager = JSONTXTPineconeManager(index_name="headwear-catalog")
vector_store = manager.load_vector_store()

# Create RAG chain
llm = ChatOpenAI(model="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3})
)

# Ask questions
response = qa_chain.run("What lightweight caps do you have with UV protection?")
print(response)
```

### Use Case 4: Batch Queries

```python
queries = [
    "navy blue trucker cap",
    "water resistant cap",
    "patch embroidery cost"
]

for query in queries:
    print(f"\nQuery: {query}")
    results = manager.search_vectors(query, k=2)
```

---

## 📚 What's Next?

### For More Details:
- 📖 **README**: See `vector_store/README.md` for full documentation
- 🔄 **Migration Guide**: See `MIGRATION_GUIDE.md` for PDF vs JSON/TXT comparison
- 💻 **Code**: Check `vector_store/json_txt_pinecone.py` for implementation details

### Integration:
1. ✅ Test with `test_json_txt_upload.py`
2. ✅ Verify searches work correctly
3. ✅ Update your RAG application (`rag.py`, `app.py`)
4. ✅ Add custom categories/metadata as needed

---

## 💡 Pro Tips

1. **First Time**: Always run `analyze_data_files()` first to verify your data
2. **Updates**: To update data, delete index and recreate (Pinecone doesn't support easy updates)
3. **Testing**: Use small `k` values (k=2-3) for faster testing
4. **Metadata**: Use metadata filters to narrow down searches
5. **Cost**: `text-embedding-3-large` is more accurate but expensive; use `text-embedding-3-small` for testing

---

## ⏱️ Time Estimates

- **Setup (Steps 1-2)**: 5 minutes
- **First Upload (Step 4)**: 30-60 seconds
- **Each Search**: < 1 second
- **Total First Run**: ~10 minutes

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] `.env` file created with API keys
- [ ] Data files verified in `data/` folder
- [ ] `test_json_txt_upload.py` runs successfully
- [ ] Search tests return relevant results
- [ ] Vector store statistics show correct count (~34 vectors)
- [ ] Ready to integrate with RAG application

---

## 🎉 You're Ready!

Once all checks pass, you have a working Pinecone vector store with:
- ✅ 30 products from JSON files
- ✅ 4 pricing/info chunks from TXT files
- ✅ Semantic search capability
- ✅ Metadata filtering
- ✅ Ready for RAG integration

**Happy coding! 🚀**

---

## 📞 Need Help?

1. Check error messages carefully
2. Review `vector_store/README.md`
3. Read code comments in `json_txt_pinecone.py`
4. Verify API keys and data files
5. Check Pinecone dashboard for index status

