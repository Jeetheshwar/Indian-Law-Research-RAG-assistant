"""Multi-agent system for legal document analysis and retrieval."""

from typing import List, Dict, Any, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from models import Citation, RetrievalResult, ConversationHistory
from retrieval import ContextualRetriever
from vector_store import LegalVectorStore
from config import get_settings
from huggingface_llm import HuggingFaceChatModel
from groq_llm import GroqChatModel
import json


class AgentState(TypedDict):
    """State shared between agents."""
    query: str
    conversation_history: List[Dict[str, str]]
    retrieved_documents: List[RetrievalResult]
    analysis: str
    citations: List[Citation]
    final_response: str
    metadata: Dict[str, Any]


class RetrievalAgent:
    """Agent responsible for retrieving relevant legal documents."""
    
    def __init__(self, retriever: ContextualRetriever):
        self.retriever = retriever
        self.settings = get_settings()
    
    def run(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents based on query and context."""
        
        query = state["query"]
        conversation = state.get("conversation_history", [])
        
        # Extract previous queries for context
        previous_queries = [msg["content"] for msg in conversation if msg["role"] == "user"]
        
        # Identify relevant document types
        doc_types = self.retriever.identify_relevant_document_types(query)
        
        # Perform retrieval with context
        results = self.retriever.retrieve_with_context(
            query=query,
            conversation_history=previous_queries,
            k=self.settings.top_k_retrieval
        )
        
        state["retrieved_documents"] = results
        state["metadata"] = {
            "num_retrieved": len(results),
            "document_types_searched": [dt.value for dt in doc_types]
        }
        
        return state


class AnalysisAgent:
    """Agent responsible for analyzing legal documents and generating insights."""
    
    def __init__(self):
        self.settings = get_settings()

        # Use Groq LLM if GROQ_API_KEY is configured
        if self.settings.groq_api_key:
            print(f"[INFO] Using Groq API with model: {self.settings.llm_model}")
            self.llm = GroqChatModel(
                model=self.settings.llm_model,
                api_key=self.settings.groq_api_key,
                temperature=self.settings.agent_temperature,
                max_tokens=4096
            )
        # Use HuggingFace LLM if HF_TOKEN is configured
        elif self.settings.hf_token:
            print(f"[INFO] Using HuggingFace Inference Client with model: {self.settings.llm_model}")
            self.llm = HuggingFaceChatModel(
                model=self.settings.llm_model,
                api_key=self.settings.hf_token,
                temperature=self.settings.agent_temperature,
                max_tokens=2000
            )
        else:
            # Use OpenAI or OpenAI-compatible API
            llm_kwargs = {
                "model": self.settings.llm_model,
                "temperature": self.settings.agent_temperature,
                "openai_api_key": self.settings.openai_api_key
            }
            if self.settings.openai_api_base:
                llm_kwargs["base_url"] = self.settings.openai_api_base

            self.llm = ChatOpenAI(**llm_kwargs)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal analyst specializing in Indian contract and consumer protection law.
Your task is to analyze the retrieved legal documents and provide accurate, well-reasoned legal analysis.

Guidelines:
1. Base your analysis strictly on the provided legal documents
2. Cite specific sections, cases, or regulations when making legal points
3. Explain legal concepts clearly for non-experts
4. Identify relevant precedents and their applicability
5. Note any conflicts or nuances in the law
6. Be precise with legal terminology

Retrieved Documents:
{documents}

User Query: {query}

Provide a comprehensive legal analysis addressing the query."""),
            ("human", "{query}")
        ])
    
    def run(self, state: AgentState) -> AgentState:
        """Analyze retrieved documents and generate insights."""
        
        results = state.get("retrieved_documents", [])
        query = state["query"]
        
        if not results:
            state["analysis"] = "No relevant legal documents found for this query."
            return state
        
        # Format documents for analysis
        docs_text = self._format_documents(results)
        
        # Generate analysis
        messages = self.prompt.format_messages(
            documents=docs_text,
            query=query
        )
        
        response = self.llm.invoke(messages)
        state["analysis"] = response.content
        
        return state
    
    def _format_documents(self, results: List[RetrievalResult]) -> str:
        """Format retrieved documents for the LLM."""
        
        formatted = []
        for idx, result in enumerate(results, 1):
            chunk = result.chunk
            doc_info = f"\n--- Document {idx} ---"
            doc_info += f"\nTitle: {chunk.document_title}"
            doc_info += f"\nType: {chunk.document_type.value}"
            if chunk.citation:
                doc_info += f"\nCitation: {chunk.citation}"
            if chunk.section_reference:
                doc_info += f"\nSection: {chunk.section_reference}"
            doc_info += f"\nRelevance Score: {result.reranked_score or result.score:.3f}"
            doc_info += f"\n\nContent:\n{chunk.content}\n"
            formatted.append(doc_info)
        
        return "\n".join(formatted)


class CitationAgent:
    """Agent responsible for extracting and formatting citations."""
    
    def __init__(self, retriever: ContextualRetriever):
        self.retriever = retriever
    
    def run(self, state: AgentState) -> AgentState:
        """Extract citations from retrieved documents."""
        
        results = state.get("retrieved_documents", [])
        
        # Create citations
        citations = self.retriever.create_citations(results)
        
        state["citations"] = citations
        
        return state


class ResponseAgent:
    """Agent responsible for generating final conversational response."""
    
    def __init__(self):
        self.settings = get_settings()

        # Use Groq LLM if GROQ_API_KEY is configured
        if self.settings.groq_api_key:
            print(f"[INFO] Using Groq API with model: {self.settings.llm_model}")
            self.llm = GroqChatModel(
                model=self.settings.llm_model,
                api_key=self.settings.groq_api_key,
                temperature=self.settings.temperature,
                max_tokens=4096
            )
        # Use HuggingFace LLM if HF_TOKEN is configured
        elif self.settings.hf_token:
            print(f"[INFO] Using HuggingFace Inference Client with model: {self.settings.llm_model}")
            self.llm = HuggingFaceChatModel(
                model=self.settings.llm_model,
                api_key=self.settings.hf_token,
                temperature=self.settings.temperature,
                max_tokens=2000
            )
        else:
            # Use OpenAI or OpenAI-compatible API
            llm_kwargs = {
                "model": self.settings.llm_model,
                "temperature": self.settings.temperature,
                "openai_api_key": self.settings.openai_api_key
            }
            if self.settings.openai_api_base:
                llm_kwargs["base_url"] = self.settings.openai_api_base

            self.llm = ChatOpenAI(**llm_kwargs)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful legal assistant specializing in Indian contract and consumer protection law.
Your role is to provide clear, accurate, and conversational responses to legal queries.

Guidelines:
1. Use the legal analysis provided to craft your response
2. Maintain a conversational yet professional tone
3. Explain legal concepts in accessible language
4. Reference specific laws, sections, and cases naturally in your response
5. Be honest about limitations and uncertainties
6. Encourage users to consult qualified legal professionals for specific advice

Legal Analysis:
{analysis}

Citations Available:
{citations}

User Query: {query}

Generate a helpful, conversational response that addresses the user's query."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])
    
    def run(self, state: AgentState) -> AgentState:
        """Generate final conversational response."""
        
        query = state["query"]
        analysis = state.get("analysis", "")
        citations = state.get("citations", [])
        history = state.get("conversation_history", [])
        
        # Format citations
        citations_text = self._format_citations(citations)
        
        # Convert history to messages
        history_messages = []
        for msg in history[-6:]:  # Last 3 exchanges
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))
        
        # Generate response
        messages = self.prompt.format_messages(
            analysis=analysis,
            citations=citations_text,
            query=query,
            history=history_messages
        )
        
        response = self.llm.invoke(messages)
        state["final_response"] = response.content
        
        return state
    
    def _format_citations(self, citations: List[Citation]) -> str:
        """Format citations for the prompt."""
        
        if not citations:
            return "No citations available."
        
        formatted = []
        for idx, citation in enumerate(citations, 1):
            cite_text = f"{idx}. {citation.document_title}"
            if citation.citation_text:
                cite_text += f" ({citation.citation_text})"
            if citation.section_reference:
                cite_text += f" - {citation.section_reference}"
            formatted.append(cite_text)
        
        return "\n".join(formatted)


class LegalMultiAgentSystem:
    """Orchestrates multiple agents for legal query processing."""
    
    def __init__(self, vector_store: LegalVectorStore):
        self.settings = get_settings()
        
        # Initialize retriever
        self.retriever = ContextualRetriever(vector_store)
        
        # Initialize agents
        self.retrieval_agent = RetrievalAgent(self.retriever)
        self.analysis_agent = AnalysisAgent()
        self.citation_agent = CitationAgent(self.retriever)
        self.response_agent = ResponseAgent()
        
        # Build agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve", self.retrieval_agent.run)
        workflow.add_node("analyze", self.analysis_agent.run)
        workflow.add_node("cite", self.citation_agent.run)
        workflow.add_node("respond", self.response_agent.run)
        
        # Define edges (workflow)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "analyze")
        workflow.add_edge("analyze", "cite")
        workflow.add_edge("cite", "respond")
        workflow.add_edge("respond", END)
        
        return workflow.compile()
    
    def process_query(
        self,
        query: str,
        conversation_history: Optional[ConversationHistory] = None
    ) -> Dict[str, Any]:
        """Process a user query through the multi-agent system."""
        
        # Prepare initial state
        history_msgs = []
        if conversation_history:
            for msg in conversation_history.get_recent_context():
                history_msgs.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        initial_state: AgentState = {
            "query": query,
            "conversation_history": history_msgs,
            "retrieved_documents": [],
            "analysis": "",
            "citations": [],
            "final_response": "",
            "metadata": {}
        }
        
        # Run the agent workflow
        final_state = self.graph.invoke(initial_state)
        
        return {
            "response": final_state["final_response"],
            "citations": final_state["citations"],
            "metadata": final_state["metadata"],
            "num_documents": len(final_state["retrieved_documents"])
        }
