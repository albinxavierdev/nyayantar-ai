import time
import os
import hashlib
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()

## langchain dependencies
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

## setting up directories
current_dir_path = os.path.dirname(os.path.abspath(__file__)) ## extract the directory name from the absolute path of this file
data_path = os.path.join(current_dir_path, "data") ## create path for the `data` folder
persistent_directory = os.path.join(current_dir_path, "data-ingestion-local") ## create a directory to save the vector store locally
processed_files_log = os.path.join(current_dir_path, "processed_files.txt") ## track processed files

def get_file_hash(filepath):
    """Get MD5 hash of a file to detect changes"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_processed_files():
    """Load list of processed files and their hashes"""
    if os.path.exists(processed_files_log):
        processed = {}
        with open(processed_files_log, 'r') as f:
            for line in f:
                if '|' in line:
                    filename, filehash = line.strip().split('|', 1)
                    processed[filename] = filehash
        return processed
    return {}

def save_processed_files(processed_files):
    """Save list of processed files and their hashes"""
    with open(processed_files_log, 'w') as f:
        for filename, filehash in processed_files.items():
            f.write(f"{filename}|{filehash}\n")

def get_new_or_modified_files(pdfs, processed_files):
    """Get list of new or modified PDF files"""
    new_files = []
    for pdf in pdfs:
        filepath = os.path.join(data_path, pdf)
        current_hash = get_file_hash(filepath)
        
        if pdf not in processed_files or processed_files[pdf] != current_hash:
            new_files.append((pdf, current_hash))
    
    return new_files

## check if the directory already exists
if not os.path.exists(persistent_directory):
    print("[INFO] Initiating the build of Vector Database .. 📌📌", end="\n\n")

    ## check if the folder that contains the required PDFs exists
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"[ALERT] {data_path} doesn't exist. ⚠️⚠️"
        )

    ## list of all the PDFs
    pdfs = [pdf for pdf in os.listdir(data_path) if pdf.endswith(".pdf")] ## list of all file names as str that ends with `.pdf`
    
    # Load existing processed files
    processed_files = load_processed_files()
    
    # Get new or modified files
    new_files = get_new_or_modified_files(pdfs, processed_files)
    
    if not new_files:
        print("✅ All PDFs are up to date! No new files to process.")
        print(f"📁 Vector database location: {persistent_directory}")
        exit(0)
    
    print(f"🆕 Found {len(new_files)} new or modified PDF files to process:")
    for pdf, _ in new_files:
        print(f"   • {pdf}")

    doc_container = [] ## list of chunked documents
    
    ## take each item from new_files and load it using PyPDFLoader
    print(f"\n📚 Loading {len(new_files)} new/modified PDF files...")
    for pdf, filehash in tqdm(new_files, desc="Loading PDFs", unit="file"):
        loader = PyPDFLoader(file_path=os.path.join("data", pdf),
                             extract_images=False)
        docsRaw = loader.load() ## list of `Document` objects. Each such object has - 1. Page Content // 2. Metadata
        for doc in docsRaw:
            # Ensure source metadata is properly set
            if 'source' not in doc.metadata:
                doc.metadata['source'] = pdf
            doc_container.append(doc) ## append each `Document` object to the previously declared container
        
        # Update processed files list
        processed_files[pdf] = filehash

    ## split the documents into chunks
    print(f"\n✂️  Splitting {len(doc_container)} documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs_split = splitter.split_documents(documents=doc_container)

    ## display information document splitted
    print(f"\n📊 Document Chunks Information:")
    print(f"   • Total documents: {len(doc_container)}")
    print(f"   • Total chunks: {len(docs_split)}")
    print(f"   • Average chunks per document: {len(docs_split)/len(doc_container):.1f}")
    print()

    ## embedding and vector store
    print("🔍 Initializing embedding model...")
    embedF = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2", encode_kwargs = {'normalize_embeddings': False})
    
    print(f"\n🚀 Starting embedding process for {len(docs_split)} chunks...")
    start = time.time()

    ## create embeddings for the documents and then store to a vector database
    print("   ⏳ Creating embeddings and storing in vector database...")
    
    # Check if vector database already exists
    if os.path.exists(persistent_directory):
        print("   📂 Loading existing vector database...")
        vectorDB = Chroma(embedding_function=embedF, persist_directory=persistent_directory)
        print("   ➕ Adding new documents to existing database...")
        
        # Process documents in batches to avoid ChromaDB batch size limit
        batch_size = 500  # Conservative batch size for ChromaDB
        total_batches = (len(docs_split) + batch_size - 1) // batch_size
        
        for i in range(0, len(docs_split), batch_size):
            batch = docs_split[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            print(f"      📦 Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
            vectorDB.add_documents(batch)
            
    else:
        print("   🆕 Creating new vector database...")
        vectorDB = Chroma.from_documents(documents=docs_split,
                                         embedding=embedF,
                                         persist_directory=persistent_directory)
    
    end = time.time()
    elapsed_time = end - start
    
    # Save updated processed files list
    save_processed_files(processed_files)
    
    print(f"\n✅ Embedding completed successfully!")
    print(f"   • Total time: {elapsed_time:.2f} seconds")
    print(f"   • Average time per chunk: {elapsed_time/len(docs_split):.3f} seconds")
    print(f"   • New chunks processed: {len(docs_split)}")
    print(f"   • Total files processed: {len(processed_files)}")
    print(f"   • Vector database saved to: {persistent_directory}")
    print(f"   • Processed files log: {processed_files_log}")

else:
    print("📂 Vector Database already exists!")
    print("🔄 Checking for new or modified PDF files...")
    
    # Load existing processed files
    processed_files = load_processed_files()
    
    # Get all PDFs
    pdfs = [pdf for pdf in os.listdir(data_path) if pdf.endswith(".pdf")]
    
    # Get new or modified files
    new_files = get_new_or_modified_files(pdfs, processed_files)
    
    if not new_files:
        print("✅ All PDFs are up to date! No new files to process.")
        print(f"📁 Vector database location: {persistent_directory}")
        print(f"📊 Total files in database: {len(processed_files)}")
        print(f"\n📁 Current vector database location: {persistent_directory}")
        print(f"📋 Processed files log: {processed_files_log}")
    else:
        print(f"🆕 Found {len(new_files)} new or modified PDF files to process:")
        for pdf, _ in new_files:
            print(f"   • {pdf}")

        doc_container = [] ## list of chunked documents
        
        ## take each item from new_files and load it using PyPDFLoader
        print(f"\n📚 Loading {len(new_files)} new/modified PDF files...")
        for pdf, filehash in tqdm(new_files, desc="Loading PDFs", unit="file"):
            loader = PyPDFLoader(file_path=os.path.join("data", pdf),
                                 extract_images=False)
            docsRaw = loader.load() ## list of `Document` objects. Each such object has - 1. Page Content // 2. Metadata
            for doc in docsRaw:
                # Ensure source metadata is properly set
                if 'source' not in doc.metadata:
                    doc.metadata['source'] = pdf
                doc_container.append(doc) ## append each `Document` object to the previously declared container
            
            # Update processed files list
            processed_files[pdf] = filehash

        ## split the documents into chunks
        print(f"\n✂️  Splitting {len(doc_container)} documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        docs_split = splitter.split_documents(documents=doc_container)

        ## display information document splitted
        print(f"\n📊 Document Chunks Information:")
        print(f"   • Total documents: {len(doc_container)}")
        print(f"   • Total chunks: {len(docs_split)}")
        print(f"   • Average chunks per document: {len(docs_split)/len(doc_container):.1f}")
        print()

        ## embedding and vector store
        print("🔍 Initializing embedding model...")
        embedF = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2", encode_kwargs = {'normalize_embeddings': False})
        
        print(f"\n🚀 Starting embedding process for {len(docs_split)} chunks...")
        start = time.time()

        ## create embeddings for the documents and then store to a vector database
        print("   ⏳ Creating embeddings and storing in vector database...")
        
        # Load existing vector database and add new documents
        print("   📂 Loading existing vector database...")
        vectorDB = Chroma(embedding_function=embedF, persist_directory=persistent_directory)
        print("   ➕ Adding new documents to existing database...")
        
        # Process documents in batches to avoid ChromaDB batch size limit
        batch_size = 500  # Conservative batch size for ChromaDB
        total_batches = (len(docs_split) + batch_size - 1) // batch_size
        
        for i in range(0, len(docs_split), batch_size):
            batch = docs_split[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            print(f"      📦 Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
            vectorDB.add_documents(batch)
            
        end = time.time()
        elapsed_time = end - start
        
        # Save updated processed files list
        save_processed_files(processed_files)
        
        print(f"\n✅ Embedding completed successfully!")
        print(f"   • Total time: {elapsed_time:.2f} seconds")
        print(f"   • Average time per chunk: {elapsed_time/len(docs_split):.3f} seconds")
        print(f"   • New chunks processed: {len(docs_split)}")
        print(f"   • Total files processed: {len(processed_files)}")
        print(f"   • Vector database saved to: {persistent_directory}")
        print(f"   • Processed files log: {processed_files_log}")