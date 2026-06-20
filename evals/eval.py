# ============================================================
# evals/eval.py
# Evaluates the RAG pipeline using RAGAS metrics
# Runs test questions through the pipeline and scores answers
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datasets import Dataset
from ragas import evaluate

from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from sentence_transformers import CrossEncoder
from config import RERANKER_MODEL

from langchain_openai import ChatOpenAI, OpenAIEmbeddings




from rag.pipeline import ask_llm
from rag.retriever import load_vectorstore, load_bm25, hybrid_search
from rag.reranker import run_reranker
from config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL
)


def test_questions():
    if not os.path.exists("evals/tests_questions.json"):
        print("Sample tests questions not found")
        return None
     
    with open("evals/tests_questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"Test questions loaded")
        return data


def run_rag_pipeline(questions):
    print(f"Running rag pipeline on test questions.....\n")
    vectordb = load_vectorstore()
    bm25 = load_bm25()
    reranker_model = CrossEncoder(RERANKER_MODEL)

    test_results = []

    for i, item in enumerate(questions, start=1):
        query = item["question"]
        expected_answer = item["expected_answer"] 
        character = item["ground_truth_character"]

        try:
            all_chunks = hybrid_search(query, vectordb, bm25)
            rerank_chunks = run_reranker(query, reranker_model, all_chunks)

    

            llm_call = ask_llm(query, vectordb, bm25, reranker_model, chathistory=[])

            llm_answer = llm_call["answer"]

            final_chunks = []
        
            for chunks in rerank_chunks:
                final_chunks.append(chunks.page_content)

            ground_truth = (
                    f"The answer should be about {character}. "
                    f"The expected answer contains: {expected_answer}"
                )
            
            test_results.append({
                "question": query,
                "answer": llm_answer,
                "retrieved_contexts": final_chunks,
                "ground_truth": ground_truth
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to run tests: {e}")
            test_results.append({
                "question": query,
                "answer": "Failed to provide an answer",
                "retrieved_contexts": [""],
                "ground_truth": expected_answer
            })


    return test_results

def evaluate_with_ragas(test_results):
    dataset = Dataset.from_list(test_results)
    llm_ai = ChatOpenAI(
        model=LLM_MODEL
    )
    ragas_llm = LangchainLLMWrapper(llm_ai)

    embeddings = OpenAIEmbeddings(
        model = EMBEDDING_MODEL
    )
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

    test_score = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), AnswerRelevancy(),ContextPrecision(), ContextRecall()],
        llm=ragas_llm,
        embeddings=ragas_embeddings

    )

    return test_score


def print_results(scores):
    print(scores)
    scores_dict = scores._repr_dict
    avg_score = sum(scores_dict.values())/len(scores_dict)
    scores_dict["average_score"] = avg_score
    with open("evals/test_results.json","w", encoding="utf-8") as f:
        json.dump(scores_dict, f, indent=2)
        

def run_evals():
    questions = test_questions()
    rag_pipeline = run_rag_pipeline(questions)
    ragas_results = evaluate_with_ragas(rag_pipeline)
    print_results(ragas_results)


if __name__ == "__main__":
    run_evals()



    











