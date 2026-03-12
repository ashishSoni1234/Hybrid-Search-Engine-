import argparse
import os
import json
import time
import requests
import re
from datetime import datetime
from tqdm import tqdm

BASE_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# Curated list of ~400 AI/CS/Data Science Wikipedia topics
TOPICS = [
    "Machine_learning", "Deep_learning", "Artificial_intelligence", "Neural_network",
    "Computer_vision", "Natural_language_processing", "Python_(programming_language)",
    "Data_science", "Big_data", "Information_retrieval", "Search_engine",
    "Vector_database", "Embeddings", "Reinforcement_learning",
    "Transformer_(machine_learning)", "ChatGPT", "Generative_artificial_intelligence",
    "Convolutional_neural_network", "Recurrent_neural_network", "Decision_tree",
    "Random_forest", "Support_vector_machine", "K-means_clustering",
    "Gradient_boosting", "Artificial_neural_network", "Attention_mechanism_(machine_learning)",
    "Prompt_engineering", "Large_language_model", "Recommendation_system",
    "Graph_neural_network", "Autoencoder", "Self-supervised_learning",
    "Speech_recognition", "Image_classification", "Object_detection",
    "Generative_adversarial_network", "BERT_(language_model)", "GPT-3",
    "Word_embedding", "Backpropagation", "Stochastic_gradient_descent",
    "Overfitting", "Regularization_(mathematics)", "Logistic_regression",
    "Linear_regression", "Principal_component_analysis", "Dimensionality_reduction",
    "Feature_engineering", "Transfer_learning", "Fine-tuning_(deep_learning)",
    "Named-entity_recognition", "Sentiment_analysis", "Text_classification",
    "Question_answering", "Information_extraction", "Knowledge_graph",
    "Semantic_search", "TF-IDF", "Inverted_index", "PageRank",
    "Collaborative_filtering", "Content-based_filtering", "Matrix_factorization",
    "Bayesian_network", "Hidden_Markov_model", "Naive_Bayes_classifier",
    "Gaussian_process", "Expectation-maximization_algorithm",
    "DBSCAN", "Hierarchical_clustering", "Association_rule_learning",
    "Anomaly_detection", "Semi-supervised_learning", "Contrastive_learning",
    "Active_learning_(machine_learning)", "Federated_learning",
    "Explainable_artificial_intelligence", "Artificial_general_intelligence",
    "Turing_test", "Expert_system", "Fuzzy_logic", "Genetic_algorithm",
    "Particle_swarm_optimization", "Q-learning", "Deep_Q-network",
    "AlphaGo", "AlphaFold", "Natural_language_generation",
    "Text_mining", "Computational_linguistics", "Part-of-speech_tagging",
    "Chatbot", "Virtual_assistant", "Optical_character_recognition",
    "Autonomous_vehicle", "Robotics", "Knowledge_representation_and_reasoning",
    "Causal_inference", "Hyperparameter_optimization", "AutoML",
    "Knowledge_distillation", "Edge_computing", "MLOps",
    "Apache_Spark", "Apache_Hadoop", "Distributed_computing",
    "Cloud_computing", "Kubernetes", "Docker_(software)", "Microservices",
    "PostgreSQL", "MongoDB", "Redis", "Apache_Kafka",
    "Time_series", "A/B_testing", "Statistical_hypothesis_testing",
    "Bayesian_inference", "Data_visualization", "Multimodal_learning",
    "Vision_transformer", "CLIP_(model)", "Zero-shot_learning",
    "Few-shot_learning", "Meta-learning_(computer_science)",
    "Retrieval-augmented_generation", "Long_short-term_memory",
    "Gated_recurrent_unit", "Beam_search", "Softmax_function",
    "Dropout_(neural_networks)", "Batch_normalization",
    "Residual_neural_network", "U-Net", "YOLO_(object_detection)",
    "Faster_R-CNN", "AlexNet", "Stable_Diffusion", "Diffusion_model",
    "Variational_autoencoder", "Seq2seq", "Layer_normalization",
    "Activation_function", "Sigmoid_function",
    "Image_segmentation", "Face_recognition", "Machine_translation",
    "Text-to-speech", "Event_detection", "Relation_extraction",
    "Coreference_resolution", "Parsing", "Dialog_system",
    "SLAM_(robotics)", "Planning_(artificial_intelligence)",
    "Logic_programming", "First-order_logic",
    "Neural_architecture_search", "Model_compression",
    "Feature_store", "Data_lake", "Data_warehouse", "ETL",
    "MapReduce", "Stream_processing", "Forecasting",
    "Bootstrapping_(statistics)", "Confidence_interval",
    "Tableau", "Natural_language_inference",
    "Semantic_role_labeling", "Reading_comprehension",
    "Temporal_reasoning", "Text-to-image_generation",
    "Online_machine_learning", "Curriculum_learning",
    "In-context_learning_(natural_language_processing)",
    "Swarm_intelligence", "Ant_colony_optimization",
    "Multi-armed_bandit", "Proximal_policy_optimization",
    "Actor-critic_algorithm", "Monte_Carlo_tree_search",
    "Summarization", "Corpus_linguistics",
    "Morphology_(linguistics)", "Ontology_(information_science)",
    "Constraint_satisfaction_problem", "Description_logic",
    "Common_sense_reasoning", "Counterfactual_thinking",
    "Quantization_(signal_processing)", "Pruning_(artificial_intelligence)",
    "Data_pipeline", "GraphQL", "Database", "SQL", "NoSQL",
    "Apache_Flink", "Statistical_model",
    "Bias_in_algorithm", "AI_safety", "Fairness_(machine_learning)",
    "Singularity_(technology)", "Evolutionary_algorithm",
    "EfficientNet", "MobileNet", "SegNet", "Mask_R-CNN",
    "VGGNet", "Inception_(machine_learning)", "GPT-4",
    "MidJourney", "Llama_(language_model)", "PaLM",
    "Microsoft_Azure", "Google_Cloud_Platform", "Amazon_Web_Services",
    "GPU_computing", "Nvidia", "CUDA",
    "Floating_point", "Binary_number", "Assembly_language",
    "Compiler", "Operating_system", "Linux", "Unix",
    "Memory_management", "Cache_(computing)", "CPU",
    "Parallel_computing", "Supercomputer", "Quantum_computing",
    "Blockchain", "Cryptography", "Hash_function",
    "Computer_security", "Cybersecurity", "Encryption",
    "Digital_signature", "Public_key_infrastructure",
    "Network_topology", "Computer_network", "Internet_protocol_suite",
    "TCP/IP", "Domain_Name_System", "HTTP", "HTTPS",
    "Web_browser", "World_Wide_Web", "HTML", "CSS",
    "JavaScript", "TypeScript", "React_(software)", "Node.js",
    "Django_(web_framework)", "Flask_(web_framework)", "FastAPI",
    "REST", "WebSocket", "Microservice", "Serverless_computing",
    "Algorithm", "Data_structure", "Array_data_structure",
    "Linked_list", "Stack_(abstract_data_type)", "Queue_(abstract_data_type)",
    "Hash_table", "Binary_tree", "Graph_(discrete_mathematics)",
    "Sorting_algorithm", "Search_algorithm", "Breadth-first_search",
    "Depth-first_search", "Dijkstra's_algorithm", "Dynamic_programming",
    "Divide_and_conquer_algorithm", "Recursion_(computer_science)",
    "Big_O_notation", "NP-completeness", "P_versus_NP_problem",
    "Turing_machine", "Computability_theory", "Formal_language",
    "Automata_theory", "Regular_expression", "Context-free_grammar",
    "Compiler_design", "Parsing_(computer_language)",
    "Object-oriented_programming", "Functional_programming",
    "Concurrent_computing", "Multithreading_(computer_architecture)",
    "Software_engineering", "Agile_software_development",
    "DevOps", "Continuous_integration", "Unit_testing",
    "Software_testing", "Version_control", "Git",
    "GitHub", "Open-source_software", "License",
    "Jupyter_Notebook", "NumPy", "Pandas_(software)",
    "Matplotlib", "Scikit-learn", "TensorFlow",
    "PyTorch", "Keras", "OpenCV",
    "NLTK", "SpaCy", "Hugging_Face",
    "LangChain", "LlamaIndex", "Chroma_(database)",
    "Pinecone_(vector_database)", "Weaviate",
    "Elasticsearch", "OpenSearch", "Solr_(software)",
    "Lucene", "Whoosh_(search_library)",
    "Cosine_similarity", "Euclidean_distance",
    "Dot_product", "Matrix_(mathematics)",
    "Eigenvalues_and_eigenvectors",
    "Singular_value_decomposition",
    "Gradient_descent", "Learning_rate",
    "Loss_function", "Cross-entropy", "Mean_squared_error",
    "Precision_and_recall", "F1_score", "ROC_curve",
    "Confusion_matrix", "Accuracy_and_precision",
    "Bias-variance_tradeoff", "Ensemble_learning",
    "Bagging", "XGBoost", "LightGBM", "CatBoost",
    "Isolation_forest", "Local_outlier_factor",
    "Label_encoding", "One-hot_encoding",
    "Data_augmentation", "Synthetic_data",
    "SMOTE", "Class_imbalance",
    "Explainability", "SHAP", "LIME_(machine_learning)",
    "Adversarial_machine_learning", "Data_poisoning",
    "Robustness_(computer_science)", "Model_interpretability",
    "Ethics_of_artificial_intelligence", "AI_regulation",
    "Deepfake", "Misinformation", "Algorithmic_bias",
    "Privacy-preserving_machine_learning",
    "Differential_privacy", "Homomorphic_encryption",
    "Neuromorphic_computing", "Spiking_neural_network",
    "Optical_neural_network", "DNA_computing",
    "Cognitive_computing", "Embodied_cognition",
    "Brain-computer_interface", "Human-computer_interaction"
]


def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input raw data directory")
    parser.add_argument("--out", type=str, required=True, help="Output processed data directory")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.input, exist_ok=True)

    docs = []
    doc_id = 1

    print(f"Fetching Wikipedia summaries for {len(TOPICS)} topics (targeting ~400 docs)...")
    pbar = tqdm(TOPICS, desc="Fetching")

    for topic in pbar:
        if doc_id > 400:
            break

        try:
            url = BASE_URL + topic
            r = requests.get(url, timeout=8, headers={"User-Agent": "HybridSearchBot/1.0"})

            if r.status_code != 200:
                continue

            data = r.json()
            title = data.get("title", "")
            text = normalize_text(data.get("extract", ""))

            if len(text) < 50:
                continue

            doc = {
                "doc_id": doc_id,
                "title": title,
                "text": text,
                "source": "wikipedia",
                "created_at": datetime.utcnow().isoformat()
            }

            docs.append(doc)
            doc_id += 1
            pbar.set_postfix({"collected": len(docs)})

        except Exception as e:
            continue

        time.sleep(0.3)

    output_path = os.path.join(args.out, "docs.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Saved {len(docs)} documents to {output_path}")


if __name__ == "__main__":
    main()
