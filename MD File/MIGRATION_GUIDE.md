# Migration Guide: PDF to JSON/TXT Vector Store

## Overview

This guide explains the differences between the PDF-based approach (`pdf_pinecone.py`) and the new JSON/TXT approach (`json_txt_pinecone.py`) for your Cap_RAG project.

---

## 🔄 Key Differences

### Old Approach: `pdf_pinecone.py`
- **Data Type**: PDF documents
- **Use Case**: Psychology textbooks, diagnostic manuals, research papers
- **Processing**: PyPDFLoader → Extract text from PDFs → Chunk → Embed
- **Data Structure**: Unstructured text from PDFs
- **Example**: Mental health chatbot with academic sources

### New Approach: `json_txt_pinecone.py`
- **Data Type**: JSON + TXT files
- **Use Case**: Product catalogs, pricing information, structured data
- **Processing**: JSON parser → Structured extraction → TXT reader → Chunk → Embed
- **Data Structure**: Structured JSON (products) + Semi-structured TXT (pricing)
- **Example**: Headwear catalog with product search and pricing queries

---

## 📊 Side-by-Side Comparison

| Feature | `pdf_pinecone.py` | `json_txt_pinecone.py` |
|---------|-------------------|------------------------|
| **Input Files** | `*.pdf` | `*.json`, `*.txt` |
| **Data Source** | `pdf_data/` folder | `data/` folder |
| **File Loader** | PyPDFLoader | json.load() + file.read() |
| **Document Structure** | Pages from PDFs | Products from JSON + Text chunks from TXT |
| **Metadata** | page, file_size_mb, category | product_id, base_price, has_stock_issues, category |
| **Categories** | diagnostic_manual, textbook, research_paper | headwear_product, pricing_patches, pricing_base |
| **Default Index** | `pdf-mental-health` | `headwear-catalog` |
| **Chunk Size** | 1000 chars | 1000 chars |
| **Use Case** | Academic/Medical RAG | E-commerce/Product RAG |

---

## 🎯 Your Data Structure

### Your `data/` Folder Contains:

#### JSON Files (Product Catalogs):
```
caps_catalog_v2.json  →  10 products with full details
caps_catalog1.json    →  10 products (duplicate)
v3.json               →  10 products
```

**JSON Structure:**
```json
{
  "id": "i7041",
  "title": "Lightweight Aerated Performance Cap",
  "description": {
    "features": [...],
    "sizing": "XS / OSFM"
  },
  "pricing": {
    "Flat Embroidery": {...},
    "3D Embroidery": {...}
  },
  "available_colors": [...]
}
```

#### TXT Files (Pricing & Info):
```
txt1.txt   →  Patch options and pricing
txt2.txt   →  Base pricing and decoration options
json3.txt  →  Marketing content about samples
```

---

## 🚀 How the New Module Works

### 1. **JSON Processing** (`_process_json_item`)

For each product in JSON files:

```python
# Input: JSON object
{
  "id": "i7041",
  "title": "Lightweight Aerated Performance Cap",
  "description": {
    "features": ["Medium profile...", "Modified flat visor..."],
    "sizing": "XS / OSFM"
  },
  "pricing": {
    "Flat Embroidery": {"24": 17.50, "48": 15.75, ...}
  },
  "available_colors": ["Black", "Gray", ...]
}

# Output: Document with formatted text
Product ID: i7041
Title: Lightweight Aerated Performance Cap

Features:
- Medium profile six panel structured cap
- Modified flat visor
- 100% aerated polyester fabric
...

Pricing:
Flat Embroidery:
  24 units: $17.5
  48 units: $15.75
...

Available Colors:
Black, Gray, Maroon, Navy, Red...

# Metadata:
{
  "source": "caps_catalog_v2.json",
  "file_type": "json",
  "product_id": "i7041",
  "title": "Lightweight Aerated Performance Cap",
  "category": "headwear_product",
  "base_price": 15.25,
  "has_stock_issues": True
}
```

### 2. **TXT Processing** (`load_txt_files`)

For each TXT file:

```python
# Input: TXT file content
patches OPTIONS

These fees are charged in addition to...

Molded Rubber Patch $6.0
FlexStyle appliques $5
...

# Output: Document(s)
# - If < 800 chars: Single document
# - If > 800 chars: Multiple chunks with overlap

# Metadata:
{
  "source": "txt1.txt",
  "file_type": "txt",
  "category": "pricing_patches",  # Auto-detected
  "file_size_kb": 0.52
}
```

### 3. **Automatic Categorization** (`_categorize_txt_content`)

The system reads TXT content and auto-categorizes:

| Content Keywords | Category |
|-----------------|----------|
| "patch", "embroidery", "decoration" + "$" | `pricing_patches` |
| "base", "stitches", "pricing" | `pricing_base` |
| "catalog", "product", "browse" | `product_catalog_info` |
| "sample", "free", "quality" | `marketing_samples` |
| Generic pricing terms | `pricing_general` |
| Default | `general_info` |

---

## 💻 Code Comparison

### Initialize Manager

#### PDF Approach:
```python
from vector_store.pdf_pinecone import PDFPineconeManager

manager = PDFPineconeManager(
    pdf_paths=["pdf_data/1.pdf", "pdf_data/2.pdf"],
    index_name="my-pdf-index"
)
```

#### JSON/TXT Approach:
```python
from vector_store.json_txt_pinecone import JSONTXTPineconeManager

manager = JSONTXTPineconeManager(
    data_dir="data",
    index_name="headwear-catalog"
)
```

### Upload Data

#### PDF Approach:
```python
# Loads PDFs → Extracts pages → Chunks → Embeds → Uploads
vector_store = manager.create_and_upload_vector_store()
```

#### JSON/TXT Approach:
```python
# Loads JSON → Formats products → Loads TXT → Chunks → Embeds → Uploads
vector_store = manager.create_and_upload_vector_store()
```

### Search

#### PDF Approach:
```python
# Search by category (diagnostic, textbook, research)
manager.search_by_category("anxiety disorders", "diagnostic_manual", k=3)
```

#### JSON/TXT Approach:
```python
# Search products only
manager.search_products_only("lightweight cap", k=3)

# Search pricing only
manager.search_pricing_only("patch costs", k=2)

# Search by category
manager.search_by_category("embroidery", "pricing_patches", k=2)
```

---

## 🔍 Search Capabilities

### What the New Module Can Do:

#### 1. Product Search
```python
manager.search_products_only("trucker mesh cap navy blue", k=3)
```
**Returns**: Products matching description, with pricing and colors

#### 2. Pricing Search
```python
manager.search_pricing_only("leather patch cost", k=2)
```
**Returns**: Pricing information from TXT files

#### 3. Feature-Based Search
```python
manager.search_vectors("water resistant UV protection snap back", k=3)
```
**Returns**: Products with those specific features

#### 4. Filtered Search
```python
# Products without stock issues
manager.search_vectors(
    "performance cap",
    k=5,
    filter_dict={"has_stock_issues": False}
)

# Only JSON data
manager.search_vectors(
    "cap",
    k=5,
    filter_dict={"file_type": "json"}
)
```

---

## 📈 Performance Comparison

### PDF Approach:
- **Input**: 3 PDF files (~2-5 MB each)
- **Processing Time**: 30-60 seconds (PDF parsing is slow)
- **Output**: ~50-200 chunks (depends on PDF length)
- **Use Case**: Dense academic content

### JSON/TXT Approach:
- **Input**: 3 JSON + 3 TXT files (~25 KB total)
- **Processing Time**: 5-10 seconds (JSON/TXT parsing is fast)
- **Output**: ~30-40 documents/chunks (30 products + 4 text chunks)
- **Use Case**: Structured product data

---

## 🎓 When to Use Which?

### Use `pdf_pinecone.py` when:
✅ You have PDF documents (books, papers, manuals)  
✅ Content is unstructured text  
✅ You need page-level references  
✅ Academic or research-focused RAG  

### Use `json_txt_pinecone.py` when:
✅ You have structured JSON data (products, catalogs)  
✅ You have TXT files with pricing/info  
✅ You need product-level metadata  
✅ E-commerce or catalog-focused RAG  

### Use Both when:
✅ You have mixed data sources  
✅ Create separate indexes for different data types  
✅ Query both indexes in your RAG application  

---

## 🔧 Customization Guide

### Add New JSON Fields

Modify `_process_json_item()` in `json_txt_pinecone.py`:

```python
# Add new field extraction
inventory = item.get('inventory', 'Unknown')
content_parts.append(f"\nInventory: {inventory}")

# Add to metadata
metadata['inventory_count'] = inventory
```

### Add New TXT Categories

Modify `_categorize_txt_content()`:

```python
# Add new category detection
if 'shipping' in content_lower and 'delivery' in content_lower:
    return "shipping_info"
```

### Change Chunk Size

Modify `__init__()`:

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Smaller chunks
    chunk_overlap=100,   # Less overlap
    ...
)
```

---

## 🚦 Migration Checklist

If you want to migrate from PDFs to JSON/TXT:

- [ ] Backup existing Pinecone index
- [ ] Prepare JSON/TXT data in `data/` folder
- [ ] Install required packages
- [ ] Set up `.env` with API keys
- [ ] Run `test_json_txt_upload.py` to test
- [ ] Verify search results
- [ ] Update your RAG application (`rag.py`, `app.py`) to use new module
- [ ] Delete old index if no longer needed

---

## 📝 Integration Example

### Before (PDF):
```python
from vector_store.pdf_pinecone import PDFPineconeManager

manager = PDFPineconeManager(
    pdf_paths=["pdf_data/1.pdf"],
    index_name="pdf-index"
)
vector_store = manager.load_vector_store()
results = vector_store.similarity_search("mental health", k=5)
```

### After (JSON/TXT):
```python
from vector_store.json_txt_pinecone import JSONTXTPineconeManager

manager = JSONTXTPineconeManager(
    data_dir="data",
    index_name="headwear-catalog"
)
vector_store = manager.load_vector_store()
results = vector_store.similarity_search("lightweight cap", k=5)
```

---

## 🎉 Summary

**What Changed:**
1. ✅ New module specifically for your JSON/TXT data
2. ✅ Structured product extraction from JSON
3. ✅ Smart TXT categorization
4. ✅ Rich metadata (product_id, prices, stock status)
5. ✅ Product-specific and pricing-specific searches
6. ✅ Faster processing (no PDF parsing overhead)

**What Stayed the Same:**
1. ✅ Same Pinecone backend
2. ✅ Same embedding model (text-embedding-3-large)
3. ✅ Same chunking strategy (RecursiveCharacterTextSplitter)
4. ✅ Same search interface (similarity_search)
5. ✅ Same metadata structure pattern

**Next Steps:**
1. 🚀 Run `python test_json_txt_upload.py`
2. 🔍 Test searches with your queries
3. 🔗 Integrate with your RAG app
4. 🎯 Customize categories/metadata as needed

---

## ❓ FAQ

**Q: Can I use both modules together?**  
A: Yes! Create separate indexes for PDFs and JSON/TXT, then query both in your RAG app.

**Q: What if I have new JSON files?**  
A: Add them to `data/` folder and re-run `create_and_upload_vector_store()` (or delete index first).

**Q: How do I update existing products?**  
A: Delete the index and recreate it. Pinecone doesn't support in-place updates easily.

**Q: Can I add more metadata fields?**  
A: Yes! Modify `_process_json_item()` to extract and store additional fields.

**Q: What about the old PDF data?**  
A: Keep `pdf_pinecone.py` if you want to use PDFs. It's independent from the new module.

---

## 📚 Resources

- [Pinecone Documentation](https://docs.pinecone.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- Vector Store README: `vector_store/README.md`

---

**Need Help?** Check the README or review the code comments in `json_txt_pinecone.py`! 🚀

