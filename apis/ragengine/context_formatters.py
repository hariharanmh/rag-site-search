def format_for_llm(page_data, include_metadata=True, max_chars=None):
    """
    Format scraped page data into a clean context string suitable for LLM processing
    and text embeddings.
    
    Args:
        page_data (dict): The scraped page data dictionary
        include_metadata (bool): Whether to include metadata in the context
        max_chars (int, optional): Maximum characters to include (None for no limit)
    
    Returns:
        str: Formatted context string
    """
    context_parts = []
    
    # Add title
    if page_data.get("title"):
        context_parts.append(f"Title: {page_data['title']}\n")
    
    # Add metadata if requested
    if include_metadata and page_data.get("metadatas"):
        meta_parts = []
        for meta in page_data["metadatas"]:
            if meta.get("name"):
                meta_parts.append(f"{meta['name']}: {meta['content']}")
            elif meta.get("property"):
                meta_parts.append(f"{meta['property']}: {meta['content']}")
        if meta_parts:
            context_parts.append("Metadata:\n" + "\n".join(meta_parts) + "\n")
    
    # Process headings and their content
    if page_data.get("headings"):
        # Sort headings by position
        sorted_headings = sorted(
            page_data["headings"].items(),
            key=lambda x: x[1].get("position", 0)
        )
        
        for heading_text, heading_data in sorted_headings:
            level = heading_data.get("level", 1)
            context_parts.append(f"\n{'#' * level} {heading_text}")
            
            # Add texts under this heading
            if heading_data.get("texts"):
                for text_item in heading_data["texts"]:
                    content = text_item["content"]
                    # Optionally include the element type
                    # context_parts.append(f"<{text_item['type']}>{content}</{text_item['type']}>")
                    context_parts.append(content)
    
    # Add orphan texts
    if page_data.get("orphan_texts"):
        context_parts.append("\nAdditional Content:")
        for text_item in page_data["orphan_texts"]:
            context_parts.append(text_item["content"])
    
    # Join all parts
    context = "\n".join(context_parts)
    
    # Truncate if max_chars is specified
    if max_chars and len(context) > max_chars:
        context = context[:max_chars].rsplit('\n', 1)[0]
        context += "\n[Content truncated]"
    
    return context

def format_for_embeddings(page_data):
    """
    Format page data into chunks suitable for text embeddings.
    Returns list of chunks with their metadata.
    """
    chunks = []
    
    # Add title as a chunk
    if page_data.get("title"):
        chunks.append({
            "text": page_data["title"],
            "type": "title",
            "metadata": {
                "source": "title"
            }
        })
    
    # Process headings and their content
    if page_data.get("headings"):
        sorted_headings = sorted(
            page_data["headings"].items(),
            key=lambda x: x[1].get("position", 0)
        )
        
        for heading_text, heading_data in sorted_headings:
            # Add heading as a chunk
            chunks.append({
                "text": heading_text,
                "type": "heading",
                "metadata": {
                    "level": heading_data.get("level", 1),
                    "position": heading_data.get("position", 0)
                }
            })
            
            # Add texts under this heading
            if heading_data.get("texts"):
                for text_item in heading_data["texts"]:
                    chunks.append({
                        "text": text_item["content"],
                        "type": text_item["type"],
                        "metadata": {
                            "heading": heading_text,
                            "heading_level": heading_data.get("level", 1)
                        }
                    })
    
    # Add orphan texts
    if page_data.get("orphan_texts"):
        for text_item in page_data["orphan_texts"]:
            chunks.append({
                "text": text_item["content"],
                "type": text_item["type"],
                "metadata": {
                    "source": "orphan_text"
                }
            })
    
    return chunks

# Example usage:
if __name__ == "__main__":
    # Sample page data
    sample_data = {
        "title": "Sample Page",
        "metadatas": [
            {"name": "description", "content": "A sample page description"},
            {"property": "og:title", "content": "Sample Page"}
        ],
        "headings": {
            "Introduction": {
                "level": 1,
                "position": 0,
                "texts": [
                    {"type": "p", "content": "This is an introduction paragraph."},
                    {"type": "span", "content": "Important note here."}
                ]
            },
            "Details": {
                "level": 2,
                "position": 1,
                "texts": [
                    {"type": "p", "content": "Detailed information goes here."}
                ]
            }
        },
        "orphan_texts": [
            {"type": "div", "content": "Footer text here"}
        ]
    }
    
    # Format for LLM
    llm_context = format_for_llm(sample_data)
    print("LLM Context:")
    print(llm_context)
    print("\n" + "="*50 + "\n")
    
    # Format for embeddings
    embedding_chunks = format_for_embeddings(sample_data)
    print("Embedding Chunks:")
    for chunk in embedding_chunks:
        print(f"\nType: {chunk['type']}")
        print(f"Text: {chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")