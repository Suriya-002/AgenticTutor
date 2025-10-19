# Agentic AI Tutor

Project Description
The Agentic AI Tutor is an interactive, adaptive learning application designed to provide personalized instruction on complex topics. Moving beyond the static, one-size-fits-all approach of traditional online learning, this project uses a multi-agent system to simulate a dynamic teaching ecosystem. A team of specialized AI agents—including a Content Agent, Quiz Agent, and Feedback Agent—are orchestrated by a LangGraph state machine. This system delivers a conversational learning loop where explanations are followed by quizzes and personalized feedback, allowing the tutor to adapt to each student's pace and level of understanding. The core goal is to combine the structured rigor of formal education with the interactive, on-demand nature of conversational AI, making high-quality, personalized learning accessible to everyone.

Installation and Setup
This project is built in Python and uses Gradio for the user interface. Follow these steps to set up your local development environment.

Prerequisites
Python 3.11 or later

An OpenAI API Key

Setup Instructions
Clone the Repository:

Bash

git clone 
cd AgenticTutor
Create a Virtual Environment: It is highly recommended to use a virtual environment to manage project dependencies.

Bash

# For Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependencies: Install all required Python packages from the requirements.txt file.

Bash

pip install -r requirements.txt
Set Up Environment Variables: Create a file named .env in the root of the project directory. This file will securely store your API key.

OPENAI_API_KEY="sk-YourSecretKeyGoesHere"
How to Run
The application is run as a local web server powered by Gradio.

Activate your virtual environment if it's not already active.

Bash

# For Windows
.\venv\Scripts\Activate.ps1
Run the application script:

Bash

python app.py
Access the Interface: Once the script is running, your terminal will display a local URL, typically http://127.0.0.1:7860. Open this URL in your web browser to start interacting with the AI Tutor.

Dataset Information
This project does not use a traditional, static dataset for training. Instead, it employs a Retrieval-Augmented Generation (RAG) approach, treating a collection of text documents as a dynamic knowledge base.

Source & Type: The "dataset" consists of plain text (.txt) or Markdown (.md) files containing validated educational content on various subjects (e.g., finance, science, mathematics). For this prototype, the knowledge is simulated via a hardcoded context string within the generate_explanation function in app.py.

Data Format & Access: The data is unstructured text. In a full production system (as outlined in our architecture design), these files would be stored in an AWS S3 bucket.

Preprocessing: The planned preprocessing pipeline involves:

Chunking: Documents are programmatically split into smaller, semantically coherent paragraphs or sections.

Embedding: Each chunk is converted into a numerical vector representation (an embedding) using a powerful language model (e.g., Amazon Titan via Bedrock).

Indexing: These vectors are stored and indexed in a vector database (e.g., Amazon OpenSearch) for efficient similarity searching.

Ethical Considerations: The RAG approach is used to mitigate the risk of model "hallucination" by grounding all AI-generated explanations in a trusted, human-verified source of information. This ensures the educational content is accurate and reliable. There are no direct privacy concerns as the knowledge base does not contain any personal user data.

Author
Name: Suriya

Contact: suriyasparks007@gmail.com