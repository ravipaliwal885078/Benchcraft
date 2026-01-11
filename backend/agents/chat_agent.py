"""
Chat Agent - Conversational AI assistant with database access and web search
Provides intelligent answers based on database analysis and web research
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from tools.vector_db import ChromaSearchTool
import google.generativeai as genai
from config import Config
import json
from datetime import date

class ChatAgent(BaseAgent):
    """The Chat Agent - Conversational Assistant"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        self.vector_tool = ChromaSearchTool()
        
        # Configure Gemini API - Use lazy initialization to avoid startup errors
        self.gemini_api_key = Config.GEMINI_API_KEY if Config.GEMINI_API_KEY else None
        self.model = None
        self.model_client = None
        self.use_new_api = False
        self._model_initialized = False
        
        # Just store the API key - initialize model when first used
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Warning: Could not configure Gemini API: {e}")
        
        super().__init__(
            role="Resource Management Assistant",
            goal="Answer questions about resource management, employees, projects, and provide insights based on database analysis",
            backstory="You are an intelligent assistant with access to the complete resource management database. You can analyze employee data, project information, allocations, skills, and provide strategic recommendations. You also have web search capabilities for general knowledge questions."
        )
    
    def query(self, user_question: str, conversation_history: list = None, use_web_search: bool = False) -> dict:
        """
        Process user question and return intelligent response with conversation context
        
        Args:
            user_question: The user's question
            conversation_history: List of previous messages in format [{'role': 'user'|'assistant', 'content': str}, ...]
            use_web_search: Whether to use web search for general knowledge
        
        Returns:
            dict with 'answer', 'sources', and 'data' keys
        """
        session = self.db_tool.Session()
        try:
            # Analyze question to determine what data is needed (with conversation context)
            context = self._analyze_question(user_question, session, conversation_history)
            
            # If web search is requested or question seems general, use web search
            if use_web_search or self._needs_web_search(user_question):
                web_context = self._web_search(user_question)
            else:
                web_context = None
            
            # Generate response using AI with database context and conversation history
            answer = self._generate_response(user_question, context, web_context, conversation_history)
            
            return {
                'answer': answer,
                'sources': context.get('sources', []),
                'data': context.get('data', {}),
                'web_context': web_context is not None
            }
            
        finally:
            session.close()
    
    def _analyze_question(self, question: str, session, conversation_history: list = None) -> dict:
        """Analyze question and extract relevant database information with conversation context"""
        from models import (
            Employee, Allocation, Project, EmployeeStatus, ProjectStatus,
            RateCard, PriorityScoring, EmployeeDomain, Domain, EmployeeSkill,
            BenchLedger, RoleLevel, RateType
        )
        
        question_lower = question.lower()
        context = {'sources': [], 'data': {}}
        today = date.today()
        
        # Check if question is clearly not related to database (general knowledge, news, etc.)
        general_knowledge_keywords = [
            'cricket', 'score', 'news', 'weather', 'sports', 'movie', 'music',
            'what is', 'who is', 'when did', 'where is', 'how to', 'explain',
            'define', 'meaning', 'latest', 'today\'s', 'current', 'recent'
        ]
        
        # If question is clearly general knowledge and not related to our database, return empty context
        is_general_question = any(keyword in question_lower for keyword in general_knowledge_keywords)
        is_db_related = any(keyword in question_lower for keyword in [
            'employee', 'resource', 'consultant', 'project', 'client', 'allocation',
            'bench', 'skill', 'domain', 'budget', 'cost', 'revenue', 'billing',
            'utilization', 'pipeline', 'active'
        ])
        
        # If it's a general question and not DB-related, skip database analysis
        if is_general_question and not is_db_related:
            return context
        
        # Extract context from conversation history for follow-up questions
        previous_context = self._extract_context_from_history(conversation_history)
        
        # Handle follow-up questions like "list them", "show me", "what about", etc.
        if self._is_followup_question(question_lower, previous_context):
            # Use context from previous messages
            if previous_context.get('topic') == 'bench_employees':
                # User wants to list bench employees
                bench_employees = session.query(Employee).filter(
                    Employee.status == EmployeeStatus.BENCH
                ).all()
                
                context['data']['bench_count'] = len(bench_employees)
                context['data']['bench_employees'] = [
                    {
                        'name': f"{e.first_name} {e.last_name}",
                        'id': e.id,
                        'role_level': e.role_level or 'N/A',
                        'email': e.email
                    }
                    for e in bench_employees
                ]
                context['sources'].append('Employee database - Bench status')
                return context
            elif previous_context.get('topic') == 'allocated_employees':
                # User wants to list allocated employees
                allocated_employees = session.query(Employee).filter(
                    Employee.status == EmployeeStatus.ALLOCATED
                ).all()
                
                context['data']['allocated_employees'] = [
                    {
                        'name': f"{e.first_name} {e.last_name}",
                        'id': e.id,
                        'role_level': e.role_level or 'N/A'
                    }
                    for e in allocated_employees
                ]
                context['sources'].append('Employee database - Allocation status')
                return context
            elif previous_context.get('topic') == 'projects':
                # User wants to list projects
                projects = session.query(Project).filter(
                    Project.status.in_([ProjectStatus.ACTIVE, ProjectStatus.PIPELINE])
                ).all()
                
                context['data']['projects'] = [
                    {
                        'id': p.id,
                        'project_name': p.project_name,
                        'client_name': p.client_name,
                        'status': p.status.value if p.status else 'N/A'
                    }
                    for p in projects
                ]
                context['sources'].append('Project database')
                return context
        
        # Employee-related queries
        if any(keyword in question_lower for keyword in ['employee', 'resource', 'consultant', 'bench', 'allocated']):
            if 'bench' in question_lower:
                bench_count = session.query(Employee).filter(
                    Employee.status == EmployeeStatus.BENCH
                ).count()
                # Fetch all bench employees (not limited) for listing
                bench_employees = session.query(Employee).filter(
                    Employee.status == EmployeeStatus.BENCH
                ).all()
                
                context['data']['bench_count'] = bench_count
                context['data']['bench_employees'] = [
                    {
                        'name': f"{e.first_name} {e.last_name}",
                        'id': e.id,
                        'role_level': e.role_level or 'N/A',
                        'email': e.email
                    }
                    for e in bench_employees
                ]
                context['sources'].append('Employee database - Bench status')
            
            if 'allocated' in question_lower or 'utilization' in question_lower:
                allocated_count = session.query(Employee).filter(
                    Employee.status == EmployeeStatus.ALLOCATED
                ).count()
                total_count = session.query(Employee).count()
                utilization = (allocated_count / total_count * 100) if total_count > 0 else 0
                
                context['data']['allocated_count'] = allocated_count
                context['data']['total_count'] = total_count
                context['data']['utilization'] = utilization
                context['sources'].append('Employee database - Allocation status')
        
        # Project-related queries
        if any(keyword in question_lower for keyword in ['project', 'client', 'pipeline', 'active']):
            active_projects = session.query(Project).filter(
                Project.status == ProjectStatus.ACTIVE
            ).count()
            pipeline_projects = session.query(Project).filter(
                Project.status == ProjectStatus.PIPELINE
            ).count()
            
            context['data']['active_projects'] = active_projects
            context['data']['pipeline_projects'] = pipeline_projects
            context['sources'].append('Project database')
        
        # Skill-related queries
        if 'skill' in question_lower:
            skills = session.query(EmployeeSkill.skill_name).distinct().limit(20).all()
            context['data']['skills'] = [s[0] for s in skills]
            context['sources'].append('Employee skills database')
        
        # Budget/cost-related queries
        if any(keyword in question_lower for keyword in ['budget', 'cost', 'revenue', 'billing']):
            bench_cost = sum(
                e.ctc_monthly for e in session.query(Employee).filter(
                    Employee.status == EmployeeStatus.BENCH
                ).all() if e.ctc_monthly
            )
            context['data']['bench_monthly_cost'] = bench_cost
            context['sources'].append('Employee cost database')
        
        # Domain-related queries
        if 'domain' in question_lower:
            domains = session.query(Domain).all()
            context['data']['domains'] = [d.domain_name for d in domains]
            context['sources'].append('Domain database')
        
        return context
    
    def _extract_context_from_history(self, conversation_history: list = None) -> dict:
        """Extract context from conversation history to understand follow-up questions"""
        if not conversation_history or len(conversation_history) == 0:
            return {}
        
        context = {}
        
        # Look at last few messages to understand what was discussed
        for msg in reversed(conversation_history[-5:]):
            content = msg.get('content', '').lower()
            role = msg.get('role', '')
            
            # Check if previous message was about bench employees
            if 'bench' in content and ('employee' in content or 'resource' in content or 'consultant' in content):
                context['topic'] = 'bench_employees'
                # Extract count if mentioned
                import re
                count_match = re.search(r'(\d+)\s*(employees?|resources?|consultants?)', content)
                if count_match:
                    context['count'] = int(count_match.group(1))
                break
            
            # Check if previous message was about allocated employees
            if 'allocated' in content or 'utilization' in content:
                context['topic'] = 'allocated_employees'
                break
            
            # Check if previous message was about projects
            if 'project' in content or 'client' in content:
                context['topic'] = 'projects'
                break
        
        return context
    
    def _is_followup_question(self, question_lower: str, previous_context: dict) -> bool:
        """Determine if current question is a follow-up to previous conversation"""
        followup_keywords = [
            'list', 'show', 'display', 'give me', 'tell me about', 'what about',
            'them', 'they', 'these', 'those', 'it', 'its', 'their', 'details',
            'more', 'further', 'additional', 'also', 'and', 'what', 'who', 'which'
        ]
        
        # Check if question contains follow-up keywords
        has_followup_keyword = any(keyword in question_lower for keyword in followup_keywords)
        
        # Check if we have previous context
        has_context = previous_context.get('topic') is not None
        
        # It's a follow-up if it has follow-up keywords and we have context
        # OR if the question is very short (likely a follow-up)
        return (has_followup_keyword and has_context) or (len(question_lower.split()) <= 3 and has_context)
    
    def _needs_web_search(self, question: str) -> bool:
        """Determine if question needs web search"""
        web_keywords = ['what is', 'how to', 'explain', 'define', 'meaning of', 'latest', 'news', 'trend']
        return any(keyword in question.lower() for keyword in web_keywords)
    
    def _web_search(self, query: str) -> str:
        """Perform web search (placeholder - would integrate with actual web search API)"""
        # In production, integrate with Google Search API, SerpAPI, or similar
        # For now, return placeholder that indicates web search should be used
        # The AI model should handle general questions when web_context is provided
        return f"User is asking a general knowledge question that requires web search: {query}. Please provide a helpful response based on general knowledge, or indicate that real-time web search is not currently available."
    
    def _initialize_model_if_needed(self):
        """Initialize Gemini model on first use (lazy initialization to avoid startup errors)"""
        if self._model_initialized:
            return  # Already tried to initialize
        
        self._model_initialized = True
        
        if not self.gemini_api_key:
            return
        
        try:
            # Try new API first (google.genai)
            try:
                import google.genai as genai_new
                genai_new.configure(api_key=self.gemini_api_key)
                self.model_client = genai_new.Client(api_key=self.gemini_api_key)
                self.use_new_api = True
                print("Initialized Gemini using google.genai (new API)")
                return
            except (ImportError, Exception) as e:
                print(f"New API not available: {e}, trying legacy API")
            
            # Fall back to legacy API - don't create model yet, just configure
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            # Store genai module for later use
            self._genai_module = genai
            self.use_new_api = False
            print("Configured for google.generativeai (legacy API) - will create model on first use")
        except Exception as e:
            print(f"Warning: Could not configure Gemini API: {e}")
            self.model = None
            self.model_client = None
    
    def _generate_response(self, question: str, db_context: dict, web_context: str = None, conversation_history: list = None) -> str:
        """Generate AI response based on question, context, and conversation history"""
        # Initialize model on first use (lazy initialization)
        self._initialize_model_if_needed()
        
        # If no model available, use rule-based response
        if not self.model and not self.model_client:
            return self._rule_based_response(question, db_context, web_context, conversation_history)
        
        # Build conversation history context
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            # Format conversation history (limit to last 10 messages to avoid token limits)
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            history_context = "\n\nPrevious Conversation:\n"
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    history_context += f"User: {content}\n"
                elif role == 'assistant':
                    history_context += f"Assistant: {content}\n"
        
        # Build prompt with context
        prompt = f"""You are a resource management assistant. Answer the following question based on the provided database context and conversation history.

Current Question: {question}

Database Context:
{json.dumps(db_context.get('data', {}), indent=2)}

Sources: {', '.join(db_context.get('sources', []))}
{history_context}

IMPORTANT: If the user asks to "list them", "show them", "list them down", "display them", etc., and the Database Context contains a list (like 'bench_employees', 'allocated_employees', 'projects'), you MUST format your response as a clear list. For example, if bench_employees is in the context, list each employee with their name and role."""
        
        if web_context:
            prompt += f"\n\nWeb Context:\n{web_context}\n"
        
        # Determine if this is a general knowledge question
        is_general = web_context is not None or not db_context.get('data') or len(db_context.get('data', {})) == 0
        
        if is_general:
            prompt += "\n\nInstructions:\n- This appears to be a general knowledge question, not related to the resource management database\n- If web search context is provided, use it to answer\n- If web search is not available, provide a helpful response based on your general knowledge\n- Be honest if you cannot provide real-time information (like current news, sports scores, etc.)\n- Do NOT try to answer with database information if the question is clearly about general knowledge"
        else:
            prompt += "\n\nInstructions:\n- Provide a clear, concise, and helpful answer based on the database context\n- Reference previous conversation if relevant\n- If the user asks to 'list them', 'show them', 'display them', etc., and the database context contains a list (like bench_employees, allocated_employees, projects), format it as a numbered or bulleted list\n- If the data is not available, say so\n- Maintain context from previous messages when answering follow-up questions\n- When the user asks follow-up questions like 'list them down' or 'show me', understand that 'them' refers to the topic from the previous conversation"
        
        try:
            # Try using the model (either new API or legacy)
            if self.use_new_api and self.model_client:
                # Use new google.genai API
                try:
                    model = self.model_client.models.get('gemini-pro')
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as new_api_error:
                    print(f"New API generation failed: {new_api_error}")
                    return self._rule_based_response(question, db_context, web_context, conversation_history)
            elif not self.use_new_api and hasattr(self, '_genai_module'):
                # Use legacy google.generativeai API - create model on first use
                if not self.model:
                    try:
                        self.model = self._genai_module.GenerativeModel('gemini-pro')
                    except Exception as model_error:
                        print(f"Failed to create Gemini model: {model_error}")
                        return self._rule_based_response(question, db_context, web_context, conversation_history)
                
                # Use chat history if available for better context
                if conversation_history and len(conversation_history) > 0:
                    # Build chat history for Gemini (last 10 messages)
                    chat_history = []
                    for msg in conversation_history[-10:]:
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        if role == 'user':
                            chat_history.append({'role': 'user', 'parts': [content]})
                        elif role == 'assistant':
                            chat_history.append({'role': 'model', 'parts': [content]})
                    
                    # Start a chat session with history
                    try:
                        chat = self.model.start_chat(history=chat_history)
                        response = chat.send_message(prompt)
                        return response.text
                    except Exception as chat_error:
                        # If chat history fails, fall back to regular generation
                        print(f"Chat history failed, using regular generation: {chat_error}")
                        try:
                            response = self.model.generate_content(prompt)
                            return response.text
                        except Exception as gen_error:
                            print(f"Regular generation also failed: {gen_error}")
                            return self._rule_based_response(question, db_context, web_context, conversation_history)
                else:
                    try:
                        response = self.model.generate_content(prompt)
                        return response.text
                    except Exception as gen_error:
                        print(f"Generation failed: {gen_error}")
                        return self._rule_based_response(question, db_context, web_context, conversation_history)
            else:
                return self._rule_based_response(question, db_context, web_context, conversation_history)
        except Exception as e:
            print(f"Error generating AI response: {e}")
            import traceback
            print(traceback.format_exc())
            return self._rule_based_response(question, db_context, web_context, conversation_history)
    
    def _rule_based_response(self, question: str, db_context: dict, web_context: str = None, conversation_history: list = None) -> str:
        """Fallback rule-based response generator with conversation context"""
        question_lower = question.lower()
        data = db_context.get('data', {})
        
        # Check conversation history for context
        context_hints = []
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                content = msg.get('content', '').lower()
                if 'bench' in content:
                    context_hints.append('bench')
                if 'project' in content:
                    context_hints.append('project')
                if 'skill' in content:
                    context_hints.append('skill')
        
        # Use context hints if current question is vague
        if len(question_lower.split()) < 3 and context_hints:
            if 'bench' in context_hints:
                question_lower = 'bench ' + question_lower
            elif 'project' in context_hints:
                question_lower = 'project ' + question_lower
        
        if 'bench' in question_lower or (conversation_history and self._extract_context_from_history(conversation_history).get('topic') == 'bench_employees'):
            count = data.get('bench_count', 0)
            bench_employees = data.get('bench_employees', [])
            
            # Check if user wants to list employees
            if bench_employees and ('list' in question_lower or 'show' in question_lower or 'display' in question_lower or 'them' in question_lower or len(question_lower.split()) <= 3):
                # User wants to list bench employees
                employee_list = "\n".join([f"- {emp.get('name', 'Unknown')} ({emp.get('role_level', 'N/A')})" for emp in bench_employees])
                return f"Here are the employees currently on bench ({count} total):\n\n{employee_list}"
            else:
                return f"There are currently {count} employees on bench."
        
        if 'allocated' in question_lower or 'utilization' in question_lower:
            utilization = data.get('utilization', 0)
            allocated = data.get('allocated_count', 0)
            total = data.get('total_count', 0)
            return f"Current utilization rate is {round(utilization, 1)}% ({allocated} out of {total} employees are allocated)."
        
        if 'project' in question_lower:
            active = data.get('active_projects', 0)
            pipeline = data.get('pipeline_projects', 0)
            return f"There are {active} active projects and {pipeline} projects in the pipeline."
        
        if 'skill' in question_lower:
            skills = data.get('skills', [])
            if skills:
                return f"Available skills in the system include: {', '.join(skills[:10])}."
            return "Skill data is not available."
        
        if 'budget' in question_lower or 'cost' in question_lower:
            cost = data.get('bench_monthly_cost', 0)
            return f"Current monthly bench cost is approximately ${round(cost / 1000, 1)}K."
        
        # Check if this is a general knowledge question
        general_keywords = ['cricket', 'score', 'news', 'weather', 'sports', 'movie', 'music', 'today\'s', 'current']
        if any(keyword in question_lower for keyword in general_keywords):
            return "I'm a resource management assistant focused on employees, projects, and resource allocation. For real-time information like sports scores, news, or weather, I would need web search capabilities which are currently limited. I can help you with questions about your resource management database instead."
        
        return "I can help you with questions about employees, projects, skills, budgets, and resource management. Could you be more specific?"
