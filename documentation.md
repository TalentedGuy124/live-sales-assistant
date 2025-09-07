# Live Sales Assistant - Architecture & Design

## 1. Objective
[cite_start]To build an agentic Live Sales Assistant where multiple specialized agents work together to fetch intelligence, process meeting audio, and produce contextual, timely talking points for a salesperson. [cite: 53] [cite_start]The system is designed to be explainable, providing provenance for all suggestions. [cite: 58]

## 2. System Architecture
[cite_start]The system is composed of lightweight, single-responsibility agents (microservices)[cite: 62]. [cite_start]Agents communicate asynchronously using an event bus (Redis Streams) [cite: 64, 86] [cite_start]and update a shared state[cite: 64]. [cite_start]A dedicated UI Agent streams final results to the frontend for transparency. [cite: 65]

## 3. Agent Roles & Responsibilities
The prototype consists of the following key agents:

* [cite_start]**STT Agent (Simulated)**: Converts meeting audio into structured context by producing a transcript. [cite: 56, 68, 70]
* [cite_start]**Entity Extraction Agent**: Listens to the transcript and extracts key entities like company names. [cite: 71, 72]
* [cite_start]**Domain Intelligence Agent**: Fetches public information (like company news and size) about a detected entity. [cite: 73, 75]
* [cite_start]**Retriever Agent**: Fetches relevant information from an internal knowledge base (a vector database). [cite: 77]
* [cite_start]**Planner Agent**: Generates candidate talking points based on the collected intelligence from the Domain and Retriever agents. [cite: 79]
* [cite_start]**Ranking Agent**: Ranks the candidate talking points by relevance and confidence score. [cite: 80]
* [cite_start]**UI Agent**: Listens for the final ranked suggestions and streams them to the frontend web application for display. [cite: 83]

## 4. Provenance & Transparency
[cite_start]To ensure the system is explainable, all suggestions are tagged with their source agent, confidence score, and the evidence used to generate them. [cite: 101] [cite_start]The user interface displays this information, fulfilling the requirement to explain which agent did what with provenance. [cite: 58]


## 5. Message Flow Diagram

```mermaid
graph TD
    A[STT Agent] -- Transcript --> B((stt_stream));
    B -- Transcript --> C[Entity Agent];
    C -- Company Name --> D((entity_stream));
    D -- Company Name --> E[Domain Agent];
    D -- Company Name --> F[Retriever Agent];
    E -- Public Info --> G((intelligence_stream));
    F -- Internal Docs --> G;
    G -- Intelligence --> H[Planner Agent];
    H -- Suggestions --> I((suggestion_stream));
    I -- Suggestions --> J[Ranking Agent];
    J -- Ranked Suggestions --> K((ranked_suggestion_stream));
    K -- Ranked Suggestions --> L[UI Agent];
    L -- WebSocket --> M[/Frontend UI/];