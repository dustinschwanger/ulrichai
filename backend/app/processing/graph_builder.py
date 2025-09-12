import networkx as nx
from typing import List, Dict, Any, Set, Tuple
import logging
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

logger = logging.getLogger(__name__)

class DocumentGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.similarity_threshold = 0.3
        
    def build_document_graph(self, documents: List[Dict[str, Any]], embeddings: Dict[str, List[float]]) -> nx.DiGraph:
        """Build relationship graph between documents"""
        
        # Add documents as nodes
        for doc in documents:
            self.graph.add_node(
                doc['doc_id'],
                title=doc.get('title', 'Untitled'),
                summary=doc['summary'],
                concepts=doc['concepts'],
                type='document'
            )
        
        # Find relationships between documents
        relationships = self.find_relationships(documents, embeddings)
        
        # Add edges for relationships
        for rel in relationships:
            self.graph.add_edge(
                rel['source'],
                rel['target'],
                weight=rel['weight'],
                type=rel['relationship_type'],
                shared_concepts=rel['shared_concepts']
            )
        
        logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        return self.graph
    
    def find_relationships(self, documents: List[Dict[str, Any]], embeddings: Dict[str, List[float]]) -> List[Dict]:
        """Find relationships between documents"""
        relationships = []
        
        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents):
                if i >= j:  # Skip self and already processed pairs
                    continue
                
                # Calculate similarity
                similarity = self.calculate_similarity(
                    embeddings[doc1['doc_id']],
                    embeddings[doc2['doc_id']]
                )
                
                if similarity > self.similarity_threshold:
                    # Find shared concepts
                    shared = self.find_shared_concepts(doc1, doc2)
                    
                    # Determine relationship type
                    rel_type = self.determine_relationship_type(doc1, doc2, shared)
                    
                    relationships.append({
                        'source': doc1['doc_id'],
                        'target': doc2['doc_id'],
                        'weight': similarity,
                        'relationship_type': rel_type,
                        'shared_concepts': shared
                    })
        
        return relationships
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            sim = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(sim)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_shared_concepts(self, doc1: Dict, doc2: Dict) -> List[str]:
        """Find concepts that appear in both documents"""
        concepts1 = set(doc1.get('concepts', []))
        concepts2 = set(doc2.get('concepts', []))
        return list(concepts1.intersection(concepts2))
    
    def determine_relationship_type(self, doc1: Dict, doc2: Dict, shared_concepts: List[str]) -> str:
        """Determine the type of relationship between documents"""
        
        # Check for specific relationship patterns
        doc1_text = doc1.get('summary', '').lower()
        doc2_text = doc2.get('summary', '').lower()
        
        # Prerequisites/sequence
        if any(phrase in doc1_text for phrase in ['before', 'prerequisite', 'foundation']):
            if any(phrase in doc2_text for phrase in ['after', 'advanced', 'build on']):
                return 'prerequisite'
        
        # Implementation/theory
        if 'implementation' in doc1_text and 'theory' in doc2_text:
            return 'implements'
        if 'theory' in doc1_text and 'implementation' in doc2_text:
            return 'theoretical_basis'
        
        # Tool/process
        if 'tool' in doc1_text and 'process' in doc2_text:
            return 'tool_for_process'
        
        # Example/concept
        if 'example' in doc1_text or 'case study' in doc1_text:
            return 'example_of'
        
        # Default based on shared concepts
        if len(shared_concepts) > 5:
            return 'strongly_related'
        elif len(shared_concepts) > 2:
            return 'related'
        else:
            return 'loosely_related'
    
    def find_related_documents(self, doc_id: str, max_docs: int = 5) -> List[Tuple[str, float]]:
        """Find documents most related to a given document"""
        
        if doc_id not in self.graph:
            return []
        
        # Get all neighbors and their weights
        related = []
        
        # Direct connections
        for neighbor in self.graph.neighbors(doc_id):
            weight = self.graph[doc_id][neighbor]['weight']
            related.append((neighbor, weight))
        
        # Reverse connections (documents pointing to this one)
        for predecessor in self.graph.predecessors(doc_id):
            if predecessor != doc_id:
                weight = self.graph[predecessor][doc_id]['weight']
                related.append((predecessor, weight * 0.8))  # Slightly lower weight for reverse
        
        # Sort by weight and return top N
        related.sort(key=lambda x: x[1], reverse=True)
        return related[:max_docs]
    
    def get_learning_path(self, start_doc: str, end_doc: str) -> List[str]:
        """Find optimal learning path between two documents"""
        try:
            path = nx.shortest_path(self.graph, start_doc, end_doc, weight='weight')
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path found between {start_doc} and {end_doc}")
            return []
    
    def get_document_cluster(self, doc_id: str, depth: int = 2) -> Set[str]:
        """Get cluster of related documents within certain depth"""
        
        if doc_id not in self.graph:
            return set()
        
        cluster = {doc_id}
        current_layer = {doc_id}
        
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                # Add neighbors
                next_layer.update(self.graph.neighbors(node))
                # Add predecessors
                next_layer.update(self.graph.predecessors(node))
            
            cluster.update(next_layer)
            current_layer = next_layer - cluster
            
            if not current_layer:
                break
        
        return cluster
    
    def export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'label': node_data.get('title', node_id),
                'concepts': node_data.get('concepts', []),
                'type': node_data.get('type', 'document')
            })
        
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'weight': edge_data.get('weight', 1.0),
                'type': edge_data.get('type', 'related'),
                'shared_concepts': edge_data.get('shared_concepts', [])
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': self.graph.number_of_nodes(),
                'total_edges': self.graph.number_of_edges(),
                'density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0
            }
        }

# Create global graph builder instance
graph_builder = DocumentGraphBuilder()