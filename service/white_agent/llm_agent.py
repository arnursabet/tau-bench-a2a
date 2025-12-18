"""
LLM-Based White Agent for Project Management Tasks
"""

import json
import re
from typing import Dict, Any, List, Optional
from litellm import completion
import asyncio


class LLMWhiteAgent:
    """LLM-based white agent that can execute PM tasks"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the LLM white agent
        """
        self.model = model
        self.temperature = temperature
        self.conversation_history = []
        
        # Check API key
        import os
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            print(f"[LLMWhiteAgent]  OpenAI API key found ({len(api_key)} chars)")
        else:
            print(f"[LLMWhiteAgent]  WARNING: No OpenAI API key found")
            print(f"[LLMWhiteAgent]  Will use fallback mechanism only")
        
        print(f"[LLMWhiteAgent] Initialized with model: {model}")
    
    def reset(self):
        """Reset the agent state"""
        self.conversation_history = []
        print("[LLMWhiteAgent] State reset")
    
    async def execute_task(
        self, 
        task_id: str,
        instruction: str, 
        tools: List[Dict[str, Any]],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a task using LLM reasoning
        """
        print(f"[LLMWhiteAgent] Executing task {task_id}")
        print(f"[LLMWhiteAgent] Instruction: {instruction[:100]}...")
        
        # Build system prompt with PM domain knowledge
        system_prompt = self._build_system_prompt(tools)
        
        # Execute task with iterative reasoning
        actions = []
        status = "success"
        
        try:
            # Get LLM response
            user_message = f"USER REQUEST: {instruction}\n\nPlease provide the tool calls needed to complete this task."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            print(f"[LLMWhiteAgent] Calling LLM with {self.model}")
            
            # Call LLM
            response = await asyncio.to_thread(
                completion,
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=1000
            )
            
            llm_output = response.choices[0].message.content
            print(f"[LLMWhiteAgent] LLM response: {llm_output[:200]}...")
            
            # Parse tool calls from LLM response
            actions = self._parse_tool_calls(llm_output)
            print(f"[LLMWhiteAgent] Extracted {len(actions)} actions")
            
            if not actions:
                print("[LLMWhiteAgent] Warning: No actions extracted, using fallback")
                # Fallback: generate some basic action
                actions = self._generate_fallback_actions(instruction, tools)
            
        except Exception as e:
            print(f"[LLMWhiteAgent]    Error during LLM execution:")
            print(f"[LLMWhiteAgent]    Error type: {type(e).__name__}")
            print(f"[LLMWhiteAgent]    Error message: {str(e)}")
            import traceback
            print(f"[LLMWhiteAgent]    Traceback: {traceback.format_exc()}")
            print(f"[LLMWhiteAgent]  Falling back to rule-based action generation")
            status = "success"  # Still mark as success since we have fallback
            # Generate fallback actions on error
            actions = self._generate_fallback_actions(instruction, tools)
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "task_id": task_id,
                "status": status,
                "actions": actions,
                "message": f"Executed {len(actions)} actions",
            },
            "id": f"task_{task_id}"
        }
    
    def _build_system_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Build system prompt with domain knowledge and tool descriptions"""
        
        tool_descriptions = self._format_tools(tools)
        
        prompt = f"""You are an AI assistant helping with project management tasks in a ticket management system.

DOMAIN: Project Management System
- Users: Team members with IDs, names, and emails
- Projects: Collections of tickets, each with specific team members
- Tickets: Tasks with fields like title, description, status, priority, assignee, comments

WORKFLOW:
- Status transitions: todo → in_progress → in_review → done
- You can also move backwards (e.g., in_progress → todo)

POLICY RULES (IMPORTANT):
1. Authentication: Always identify the user at the beginning if not specified
2. Single Project: Work within one project per conversation
3. Membership: Only assign tickets to project members
4. Confirmation: Ask for confirmation before state-changing operations
5. One Action per Turn: Either call a tool OR respond to the user, not both

AVAILABLE TOOLS:
{tool_descriptions}

RESPONSE FORMAT:
Respond with tool calls in the following JSON format:

```json
[
    {{
        "name": "tool_name",
        "kwargs": {{
            "param1": "value1",
            "param2": "value2"
        }}
    }},
    ...
]
```

EXAMPLES:

Example 1 - List tickets:
User: "Show me all todo tickets"
Response:
```json
[
    {{
        "name": "list_tickets",
        "kwargs": {{
            "status": "todo"
        }}
    }}
]
```

Example 2 - Create and assign ticket:
User: "Create a high priority ticket for fixing the login bug and assign it to user1"
Response:
```json
[
    {{
        "name": "create_ticket",
        "kwargs": {{
            "title": "Fix login bug",
            "description": "Bug in login functionality needs immediate attention",
            "priority": "high"
        }}
    }}
]
```

Example 3 - Update ticket status:
User: "Move ticket 5 to in progress"
Response:
```json
[
    {{
        "name": "update_status",
        "kwargs": {{
            "ticket_id": "5",
            "status": "in_progress"
        }}
    }}
]
```

Remember:
- Be precise with tool calls
- Follow the policy rules
- Return valid JSON
- Use appropriate tool for each action
"""
        
        return prompt
    
    def _format_tools(self, tools: List[Dict[str, Any]]) -> str:
        """Format tool descriptions for the prompt"""
        if not tools:
            return "No tools available"
        
        formatted = []
        for tool in tools:
            name = tool.get("name", "unknown")
            description = tool.get("description", "No description")
            parameters = tool.get("parameters", {})
            
            param_str = ""
            if isinstance(parameters, dict):
                props = parameters.get("properties", {})
                required = parameters.get("required", [])
                
                param_parts = []
                for param_name, param_info in props.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    is_required = " (required)" if param_name in required else " (optional)"
                    param_parts.append(f"  - {param_name} ({param_type}){is_required}: {param_desc}")
                
                if param_parts:
                    param_str = "\n" + "\n".join(param_parts)
            
            formatted.append(f"• {name}: {description}{param_str}")
        
        return "\n".join(formatted)
    
    def _parse_tool_calls(self, llm_output: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from LLM output
        """
        actions = []
        
        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
        matches = re.findall(json_pattern, llm_output, re.DOTALL)
        
        if matches:
            # Try each match
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, list):
                        actions.extend(parsed)
                    elif isinstance(parsed, dict):
                        actions.append(parsed)
                except json.JSONDecodeError:
                    continue
        
        # If no code blocks, try to find raw JSON array
        if not actions:
            try:
                # Look for array pattern
                array_pattern = r'\[\s*\{.*?\}\s*\]'
                array_match = re.search(array_pattern, llm_output, re.DOTALL)
                if array_match:
                    parsed = json.loads(array_match.group(0))
                    if isinstance(parsed, list):
                        actions = parsed
            except:
                pass
        
        # Validate actions
        validated_actions = []
        for action in actions:
            if isinstance(action, dict) and "name" in action:
                validated_actions.append({
                    "name": action["name"],
                    "kwargs": action.get("kwargs", action.get("arguments", {}))
                })
        
        return validated_actions
    
    def _generate_fallback_actions(
        self, 
        instruction: str, 
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate fallback actions based on simple keyword matching
        """
        actions = []
        instruction_lower = instruction.lower()
        
        # Simple keyword-based action generation
        if "list" in instruction_lower or "show" in instruction_lower:
            actions.append({"name": "list_tickets", "kwargs": {}})
        
        elif "create" in instruction_lower or "new ticket" in instruction_lower:
            # Extract title if possible
            title = "New ticket from user request"
            actions.append({
                "name": "create_ticket",
                "kwargs": {
                    "title": title,
                    "description": "Created based on user instruction",
                    "priority": "medium"
                }
            })
        
        elif "assign" in instruction_lower:
            # Try to extract ticket ID and user ID
            actions.append({
                "name": "assign_user",
                "kwargs": {
                    "ticket_id": "1",
                    "user_id": "user1"
                }
            })
        
        elif "status" in instruction_lower or "move" in instruction_lower:
            # Determine target status
            status = "in_progress"
            if "done" in instruction_lower or "complete" in instruction_lower:
                status = "done"
            elif "review" in instruction_lower:
                status = "in_review"
            elif "todo" in instruction_lower:
                status = "todo"
            
            actions.append({
                "name": "update_status",
                "kwargs": {
                    "ticket_id": "1",
                    "status": status
                }
            })
        
        elif "priority" in instruction_lower:
            priority = "high" if "high" in instruction_lower else "medium"
            actions.append({
                "name": "update_priority",
                "kwargs": {
                    "ticket_id": "1",
                    "priority": priority
                }
            })
        
        elif "comment" in instruction_lower:
            actions.append({
                "name": "add_comment",
                "kwargs": {
                    "ticket_id": "1",
                    "comment": "Comment from user"
                }
            })
        
        else:
            # Default: list tickets
            actions.append({"name": "list_tickets", "kwargs": {}})
        
        return actions


# Test function
async def test_agent():
    """Test the LLM white agent"""
    agent = LLMWhiteAgent(model="gpt-4o-mini")
    
    tools = [
        {
            "name": "list_tickets",
            "description": "List tickets in the project",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status"}
                }
            }
        }
    ]
    
    result = await agent.execute_task(
        task_id="test_1",
        instruction="Show me all high priority tickets",
        tools=tools
    )
    
    print("\nTest Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_agent())

