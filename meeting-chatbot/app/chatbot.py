from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from app.ai_handlers import ai_provider
from app.database import db
from app.models import ChatQuery, ChatResponse

logger = logging.getLogger(__name__)

class MeetingChatbot:
    def __init__(self):
        self.ai_provider = ai_provider
    
    async def _build_context(self, query: ChatQuery) -> str:
        """
        Build context from relevant documents/data based on the query
        """
        try:
            context_parts = []
            
            # If specific document ID is provided
            if query.doc_id:
                document = await db.get_document_by_id(query.doc_id)
                if document:
                    context_parts.append(self._format_document_context([document]))
            
            # If specific meeting ID is provided
            if query.meeting_id:
                meeting = await db.get_meeting_by_id(query.meeting_id)
                if meeting:
                    context_parts.append(self._format_meeting_context([meeting]))
            
            # If no specific ID, search for relevant documents
            if not query.doc_id and not query.meeting_id:
                # Search for relevant documents in general documents collection
                relevant_docs = await self._find_relevant_documents(query)
                if relevant_docs:
                    context_parts.append(self._format_document_context(relevant_docs))
                
                # Also include meeting summaries if available
                relevant_meetings = await self._find_relevant_meetings(query)
                if relevant_meetings:
                    context_parts.append(self._format_meeting_context(relevant_meetings))
            
            if not context_parts:
                return ""
            
            return "\n\n---\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return ""
    
    async def _find_relevant_documents(self, query: ChatQuery) -> List[Dict[str, Any]]:
        """
        Find relevant documents from the database based on the query
        """
        try:
            import re
            
            # Extract potential keywords from query
            keywords = re.findall(r'\b\w{3,}\b', query.question.lower())  # Words with at least 3 characters
            
            # Search documents by text
            all_docs = []
            for keyword in keywords[:5]:  # Limit to top 5 keywords
                docs = await db.search_documents_text(keyword, limit=10)
                all_docs.extend(docs)
            
            # Remove duplicates based on doc_id
            seen = set()
            unique_docs = []
            for doc in all_docs:
                doc_id = doc.get('doc_id') or str(doc.get('_id', ''))
                if doc_id not in seen:
                    seen.add(doc_id)
                    unique_docs.append(doc)
            
            # Score documents by relevance
            for doc in unique_docs:
                content = f"{doc.get('title', '')} {doc.get('content', '')} {' '.join(doc.get('tags', []))}"
                content_lower = content.lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                doc['relevance_score'] = matches / len(keywords) if keywords else 0
            
            # Sort by relevance score
            unique_docs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            # Return top documents (limit based on config)
            from app.config import settings
            return unique_docs[:settings.MAX_CONTEXT_DOCUMENTS]
            
        except Exception as e:
            logger.error(f"Error finding relevant documents: {e}")
            return []
    
    def _format_document_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format documents into a context string
        """
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context = f"""
Document {i}: {doc.get('title', 'Untitled Document')}
Category: {doc.get('category', 'General')}
Tags: {', '.join(doc.get('tags', []))}
Content: {doc.get('content', 'No content available')}
"""
            context_parts.append(context.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    async def _find_relevant_meetings(self, query: ChatQuery) -> List[Dict[str, Any]]:
        """
        Find meetings relevant to the query
        """
        try:
            # Simple keyword matching for now
            # You can enhance this with embeddings/semantic search
            import re
            
            # Extract potential keywords from query
            keywords = re.findall(r'\b\w+\b', query.question.lower())
            
            # Search in recent meetings
            recent_meetings = await db.get_recent_meetings(days=query.context_days or 30, limit=50)
            
            relevant_meetings = []
            for meeting in recent_meetings:
                # Check if keywords appear in meeting content
                content = f"{meeting.get('title', '')} {meeting.get('summary', '')} {' '.join(meeting.get('tags', []))}"
                content_lower = content.lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                
                if matches > 0:
                    meeting['relevance_score'] = matches / len(keywords) if keywords else 0
                    relevant_meetings.append(meeting)
            
            # Sort by relevance score
            relevant_meetings.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return relevant_meetings[:10]  # Return top 10 relevant meetings
            
        except Exception as e:
            logger.error(f"Error finding relevant meetings: {e}")
            return []
    
    def _format_meeting_context(self, meetings: List[Dict[str, Any]]) -> str:
        """
        Format meetings into a context string
        """
        if not meetings:
            return "No meeting data available."
        
        context_parts = []
        
        for i, meeting in enumerate(meetings, 1):
            context = f"""
            Meeting {i}: {meeting.get('title', 'Untitled')}
            Date: {meeting.get('date', 'Unknown')}
            Participants: {', '.join(meeting.get('participants', []))}
            Summary: {meeting.get('summary', 'No summary available')}
            Key Points: {', '.join(meeting.get('key_points', []))}
            Action Items: {self._format_action_items(meeting.get('action_items', []))}
            Decisions: {', '.join(meeting.get('decisions', []))}
            """
            context_parts.append(context.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    def _format_action_items(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items for context"""
        if not action_items:
            return "No action items"
        
        formatted = []
        for item in action_items:
            task = item.get('task', 'Unknown task')
            assignee = item.get('assignee', 'Unassigned')
            due_date = item.get('due_date', 'No due date')
            formatted.append(f"{task} (Assigned to: {assignee}, Due: {due_date})")
        
        return "; ".join(formatted)
    
    async def ask_question(self, query: ChatQuery) -> ChatResponse:
        """
        Main method to answer questions about meetings
        """
        try:
            # Validate AI provider
            available_providers = self.ai_provider.get_available_providers()
            if query.ai_provider not in available_providers:
                query.ai_provider = available_providers[0] if available_providers else "openai"
            
            # Build context from meetings
            context = await self._build_context(query)
            
            if not context or context.strip() == "":
                # If no context, use Gemini's general knowledge but inform user
                answer = await self.ai_provider.get_response(
                    prompt=f"{query.question}\n\nNote: I don't have specific context from your connected data, so I'm providing a general answer. Please upload documents to the database for more accurate responses based on your data.",
                    context="",
                    provider=query.ai_provider
                )
                return ChatResponse(
                    answer=answer,
                    sources=[],
                    ai_provider=query.ai_provider,
                    confidence=0.3  # Lower confidence when no context
                )
            
            # Generate answer using AI
            answer = await self.ai_provider.get_response(
                prompt=query.question,
                context=context,
                provider=query.ai_provider
            )
            
            # Calculate confidence (simplified - can be enhanced)
            confidence = self._calculate_confidence(answer, query.question)
            
            # Get source meetings
            sources = await self._get_source_meetings(query)
            
            return ChatResponse(
                answer=answer,
                sources=sources,
                ai_provider=query.ai_provider,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return ChatResponse(
                answer=f"Error processing your question: {str(e)}",
                sources=[],
                ai_provider=query.ai_provider or "openai",
                confidence=0.0
            )
    
    def _calculate_confidence(self, answer: str, question: str) -> float:
        """
        Calculate confidence score for the answer
        """
        # Simple confidence calculation
        # You can enhance this with more sophisticated methods
        
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # Check for uncertainty indicators
        uncertainty_phrases = [
            "i don't know", "i'm not sure", "no information",
            "not mentioned", "not specified", "not available"
        ]
        
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                return 0.2
        
        # Check if answer contains relevant terms from question
        question_terms = set(question_lower.split())
        answer_terms = set(answer_lower.split())
        
        overlap = len(question_terms.intersection(answer_terms))
        if question_terms:
            term_similarity = overlap / len(question_terms)
        else:
            term_similarity = 0
        
        # Base confidence
        base_confidence = 0.7
        
        # Adjust based on term similarity
        confidence = min(0.95, base_confidence + (term_similarity * 0.3))
        
        return round(confidence, 2)
    
    async def _get_source_meetings(self, query: ChatQuery) -> List[Dict[str, Any]]:
        """
        Get source documents and meetings that contributed to the answer
        """
        try:
            sources = []
            
            # Add specific document if provided
            if query.doc_id:
                document = await db.get_document_by_id(query.doc_id)
                if document:
                    sources.append(self._format_source_document(document))
            
            # Add specific meeting if provided
            if query.meeting_id:
                meeting = await db.get_meeting_by_id(query.meeting_id)
                if meeting:
                    sources.append(self._format_source_meeting(meeting))
            
            # Add relevant documents if no specific ID
            if not query.doc_id and not query.meeting_id:
                documents = await self._find_relevant_documents(query)
                sources.extend([self._format_source_document(d) for d in documents[:3]])
                
                meetings = await self._find_relevant_meetings(query)
                sources.extend([self._format_source_meeting(m) for m in meetings[:3]])
            
            return sources[:5]  # Limit to top 5 sources
        except Exception as e:
            logger.error(f"Error getting source documents: {e}")
            return []
    
    def _format_source_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Format document for source display"""
        return {
            "doc_id": document.get("doc_id"),
            "title": document.get("title"),
            "category": document.get("category"),
            "content_preview": document.get("content", "")[:200] + "..." if len(document.get("content", "")) > 200 else document.get("content", "")
        }
    
    def _format_source_meeting(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Format meeting for source display"""
        return {
            "meeting_id": meeting.get("meeting_id"),
            "title": meeting.get("title"),
            "date": meeting.get("date"),
            "summary": meeting.get("summary", "")[:200] + "..." if len(meeting.get("summary", "")) > 200 else meeting.get("summary", "")
        }

# Create chatbot instance
chatbot = MeetingChatbot()