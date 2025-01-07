# RAG-Based Site Search

The Site-Search application is a simple yet effective Retrieval-Augmented Generation (RAG) tool designed to crawl a website's sitemap, extract content, and provide basic search and summarization capabilities. It is lightweight and uses a Python dictionary as its database.

## Features

- **Basic RAG Functionality:** Combines retrieval and generation for simple search and summarization tasks.
- **Python Dictionary as Database:** Uses an in-memory dictionary for storing and querying content.
- **Sitemap Crawling:** Extracts content from a website's sitemap for indexing.
- **Summarization:** Provides basic summaries of indexed content.

## Technology Stack

- **Python:** Core programming language for application development.
- **FastAPI:** Framework for building the API interface.
- **Python Dictionary:** Used as a lightweight, in-memory database.

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hariharanmh/rag-site-search.git
   cd rag-site-search
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API documentation at `http://127.0.0.1:8000/api/v1/docs`.

## Usage

1. **Ingest:** Use the `/ingest` endpoint to Ingests a website's sitemap to create a knowledge base.
2. **AskQuery:** Send a request to the `/askQuery` endpoint generates a response based on the provided prompt.

## Improvements and Future Work

- Replace the Python dictionary with a proper vector database for scalable and efficient querying.
- Add support for multi-language summarization.
- Deploy on a cloud platform for scalability and high availability.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push your branch and create a pull request.


## Acknowledgments

- Gemini for advancements in LLM technology.
- FastAPI for the web framework.
- Beautiful Soup for web scraping utilities.

<!-- ## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. -->

## Contact

For any questions or feedback, please contact Hariharan at `imhariharanm@gmail.com`.

---

Thank you for using the Site-Search Application!