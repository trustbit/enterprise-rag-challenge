from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class TeamInfo:

    file_name: str = ""
    team_name: str = ""

    is_local_model: bool = False
    model_name: str = ""

    # ideally we will have all fields, filled in by the team
    # but in practice, they can sometimes provide only the total cost
    total_prefill_and_answer_costs: Optional[str] = ""

    prefill_prompt_tokens: Optional[int] = None
    prefill_completion_tokens: Optional[int] = None

    answer_prompt_tokens: Optional[int] = None
    answer_completion_tokens: Optional[int] = None

    links : List[Tuple[str, str]] = None

    #link_name: Optional[str] = None # LinkedIn, Blog, Website
    #link_url: Optional[str] = None


    architecture: Optional[str] = None
    # optional
    source_code: Optional[str] = None
    # optional exploration notes
    research_notes: Optional[str] = None

    affiliation: Optional[str] = None

    learned_from_ai_research: bool = False





TEAMS  = [
    TeamInfo(
        file_name="AlBo",
        team_name="Aleksandr Bobrov",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="""
        Created a Knowledge Graph with Neo4j and Vector Index. Used Langchain
        """,
        research_notes="""
        Can probably improve by having separate table parsing. 
        
        A lot of time was spent on analysis and graph building with LLMs. 
        Tried to use LLAMA 3.1, but it was too slow. Switched to GPT-4o and batch processing.
        """,

        total_prefill_and_answer_costs="$2,46 / ?",

        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        learned_from_ai_research=False,

        affiliation="Independent Consultant",

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/bobroval/"),
        ],

        source_code = "",
    ),
    TeamInfo(
        file_name="Artem_checklist_plus",
        team_name="Artem Checklist Plus",
        model_name="Gemini Flash Exp with 4M",
        is_local_model=False,

        total_prefill_and_answer_costs="Free",
        architecture="Run all files at once against the checklist (one file and all questions). Then took the matrix and all files to run everything again.",
        research_notes="Tried more expensive models, but they didn't give much boost at this scale. Gemini Flash Exp with 4M is currently free on Open Router.",

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/artemnurm/"),
        ],

        affiliation="Independent Consultant",

        learned_from_ai_research=True,
    ),
    TeamInfo(
        file_name="Artem_multi_stage_checklist",
        team_name="Artem Multi Stage Checklist",
        model_name="Gemini Flash Exp",
        is_local_model=False,
        architecture="Converted questions to the checklist. Run each item with Gemini Flash to build the matrix - 800 runs. Reduce by running the same checklist on the matrix of all anwers. Last stage - format fixing accordint to schema.",
        total_prefill_and_answer_costs="$4",
        research_notes="Tried more expensive models, but they didn't give much boost at this scale. ",

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/artemnurm/"),
        ],

        affiliation="Independent Consultant",
        learned_from_ai_research=True,

    ),
    TeamInfo(
        file_name="anonymous_1256",
        team_name="Anonymous 1256",
        model_name="qwen72b",
        is_local_model=True,

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        architecture="ReAct + RAG, table data was converted to XML, chunking with RecursiveCharacterTextSplitter",
        research_notes="",

        affiliation="Independent Consultant",
        links=[],
        source_code="",

        learned_from_ai_research=False,
    ),
    TeamInfo(
        file_name="anonymous_1447",
        team_name="Anonymous 1447",
        model_name="GPT-4o",
        is_local_model=False,

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,


        architecture="Structured output; 2-3 query requests; standard semantic chunking for RAG",
        research_notes="",

        affiliation="",
        links=[],
        source_code="",

        learned_from_ai_research=False,
    ),



    TeamInfo(
        file_name="Ilya_Rice",
        team_name="Ilya Rice",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="Langchain RAG with GPT-4o, Text-embedding-3-large and custom chain of thought prompts. Used fitz for text parsing, simple chunking by character count.",
        research_notes="Can improve quality by parsing tables better. Used GPT-4o-2024-05-13",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        # github.com/ilyaRice/
        # https://www.linkedin.com/in/ilya-rice-a02a5a2a3/

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/ilya-rice-a02a5a2a3/"),
            ("GitHub", "https://github.com/ilyaRice/"),
        ],

        affiliation="Independent Consultant",
        learned_from_ai_research=False,
    ),


    TeamInfo(
        file_name="Neuraldeep-tech",
        team_name="Neuraldeep Tech",
        model_name="LLAMA-3.1-8B-instruct",
        is_local_model=True,
        architecture="This is an existing product using AutoRAG arpproach. All documents are parsed with a predefined code. Text is then sent to AutoTagger agent. Consistency of chunks is checked. AutoQA test is run on the QA dataset (RAGAS approach). Diagrams and reports are generated afterwards.",
        research_notes="Using own LLM fine-tune",


        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [
            ("Website", "https://www.neuraldeep.tech"),
        ],

        affiliation="AI Product Vendor",
        learned_from_ai_research=False,
        source_code=None,
    ),

    TeamInfo(
        file_name="anonymous_1652",
        team_name="Anonymous 1652",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="Used RAG approach with OpenAIEmbeddings, Chroma",
        research_notes="",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [],

        affiliation="",
        learned_from_ai_research=False,
        source_code=None,
    ),
    TeamInfo(
        file_name="aimpresario_team",
        team_name="Aimpresario Team",
        model_name="gpt-4o-mini",
        is_local_model=False,
        architecture="Multi-agent RAG system with CoT and tools. Built a knowledge graph with recursive retriever.",
        research_notes="A lot of cofee and little sleep. Used RBAAI/bge-reranker-large and models from VikParuchuri/marker. Main PDF parsing to Markdown with LlamaParse, backup parsing with VikParuchuri/marker.",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [],

        affiliation="Independent Consultant",
        learned_from_ai_research=False,
        source_code=None,
    ),
    TeamInfo(
        file_name="A_Ovsov_M_Startseva_JustAI_2",
        team_name="A.Ovsov, M.Startseva (JustAI)",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="Used GPT-4o agent RAG",
        research_notes="",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [
            ("Company", "https://just-ai.com"),

        ],

        affiliation="",
        learned_from_ai_research=False,
        source_code=None,
    ),
    TeamInfo(
        file_name="anonymous_1337",
        team_name="Anonymous 1337",
        model_name="",
        is_local_model=False,
        architecture="Used RAG with chunk vectorizer and LLM",
        research_notes="",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [],

        affiliation="",
        learned_from_ai_research=False,
        source_code=None,
    ),


    TeamInfo(
        file_name="F-team",
        team_name="Anonymous F-team",
        model_name="",
        is_local_model=False,
        architecture="RAG using using hybrid search (bm25 and local vector-based embedder) with graph-based knowledge representation. Final answer synthesis is done with LLM",
        research_notes="",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [],

        affiliation="",
        learned_from_ai_research=False,
        source_code=None,
    ),

    # reciprocal rank fusion. 0x1d.json (anonymous). gpt4o-mini
    TeamInfo(
        file_name="Ox1d",
        team_name="Anonymous Ox1d",
        model_name="gpt4o-mini",
        is_local_model=False,
        architecture="RAG with reciprocal rank fusion",
        research_notes="",

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [],

        affiliation="",
        learned_from_ai_research=False,
        source_code=None,
    ),

    # TTA_Felix.json - TimeToAct Austria, Felix Krause.
    # Multiagent GPT-4o based solution, with 3 agents

    TeamInfo(
        file_name="TTA_Felix",
        team_name="Felix Krause",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="Multiagent GPT-4o based solution, with 3 agents",
        research_notes="""
This solution is based on three specialized agents using ChatGPT 4o, each with a specific role in the decision making process. A delegation manager is responsible for delegating simple tasks to company experts. It enhances the user queries to allow for a better understanding of the context and the question. The company experts are specialized in answering questions about a specific company report. They are responsible for extracting the relevant information from the context, which contains the results of a basic vector database with chunk size 3000. Based on this they will provide an answer according to the guidelines and also a concise explanation of their decision process. The execution manager is then responsible for deciding on the final answer based on the answers and chains of thought of the company experts. While the company experts might be very strict in providing answers based on the query, the execution manager tries to capture the whole picture and might deviate from the answers of the company experts.
        """,

        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/f-krause-ai/"),
            ("Company", "https://www.trustbit.tech/en/"),
        ],

        affiliation="TimeToAct Austria",
        learned_from_ai_research=True,
        source_code="pending",
    ),

    # TTA_Maria - Maria Ronacher from TimeToAct Austria
    # Using OpenAI Assistants API with GPT-4o
    # architecture - match files via text and then upload all relevant files with a question to the API
    TeamInfo(
        file_name="TTA_Maria",
        team_name="Maria Ronacher",
        model_name="GPT-4o",
        is_local_model=False,
        architecture="ChatGPT Assistants API",
        research_notes="Find relevant files via text matching. Then upload all relevant files with a question to the Assistants API",
        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/mariaronacher/"),
            ("Company", "https://www.trustbit.tech/en/"),
        ],

        affiliation="TimeToAct Austria",
        learned_from_ai_research=True,
        source_code="pending",
    ),

    # TTA_Pedro - Pedro Ananias from TimeToAct Austria
    # using RAG with vector embeddings and local openchat/openchat-3.5-0106
    TeamInfo(
        file_name="TTA_Pedro",
        team_name="Pedro Ananias",
        model_name="OpenChat-3.5-0106",
        is_local_model=True,
        architecture="RAG with vector embeddings and local OpenChat-3.5-0106",
        research_notes="",
        total_prefill_and_answer_costs=None,
        prefill_prompt_tokens=None,
        prefill_completion_tokens=None,
        answer_prompt_tokens=None,
        answer_completion_tokens=None,

        links = [
            ("LinkedIn", "https://www.linkedin.com/in/pedroananias/"),
            ("Company", "https://www.trustbit.tech/en/"),
        ],

        affiliation="TimeToAct Austria",
        learned_from_ai_research=True,
        source_code="pending",
    ),
    TeamInfo(
        file_name="TTA_Daniel",
        team_name="Daniel Weller",
        model_name="GPT-4o",
        is_local_model=False,
        total_prefill_and_answer_costs="$5.96+$2.44",
        prefill_prompt_tokens=2302019,
        prefill_completion_tokens=20445,
        answer_prompt_tokens=975723,
        answer_completion_tokens=250,
        architecture="Used gpt-4o with structured outputs to extract all interesting data from PDFs in bulk. Full checklist run per file. Then run each question against the filled data using structured outputs according to the desired schema.",

        links=[
            ("LinkedIn", "https://www.linkedin.com/in/daniel-weller-9bb3564b/"),
            ("Company", "https://www.trustbit.tech/en/"),
        ],

        affiliation="TimeToAct Austria",

        learned_from_ai_research=True,
        source_code="pending",
    ),

]


TEAMS = [t for t in TEAMS if not isinstance(t, str)]
