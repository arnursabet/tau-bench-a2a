"""
Assessment Launcher starts both green and mock white agents, runs assessment, and displays results
"""

import subprocess
import time
import httpx
import asyncio
import json
import sys
from pathlib import Path

class AssessmentLauncher:
    
    def __init__(self):
        self.green_agent_process = None
        self.white_agent_process = None
        self.green_agent_url = "http://localhost:8000"
        self.white_agent_url = "http://localhost:8001"
    
    def start_agents(self):
        print("="*70)
        print(" "*20 + "AgentBeats Assessment Launcher")
        print("="*70)
        
        print("\n[Launcher] Starting green agent")
        try:
            self.green_agent_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "service.green_agent.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            time.sleep(0.5)
            if self.green_agent_process.poll() is not None:
                stderr_output = ""
                if self.green_agent_process.stderr:
                    try:
                        stderr_output = self.green_agent_process.stderr.read().decode(errors='ignore')
                    except:
                        pass
                raise Exception(f"Green agent failed to start: {stderr_output[:200]}")
            print("[Launcher] Green agent process started")
        except Exception as e:
            print(f"[Launcher] Failed to start green agent: {e}")
            raise
        
        print("[Launcher] Starting mock white agent")
        try:
            self.white_agent_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "service.mock_white_agent:app",
                    "--host", "127.0.0.1",
                    "--port", "8001"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            time.sleep(0.5)
            if self.white_agent_process.poll() is not None:
                stderr_output = ""
                if self.white_agent_process.stderr:
                    try:
                        stderr_output = self.white_agent_process.stderr.read().decode(errors='ignore')
                    except:
                        pass
                raise Exception(f"White agent failed to start: {stderr_output[:200]}")
            print("[Launcher] Mock white agent process started")
        except Exception as e:
            print(f"[Launcher] Failed to start white agent: {e}")
            self.cleanup()
            raise
        
        print("[Launcher] Waiting for agents to initialize")
        max_retries = 10
        for i in range(max_retries):
            time.sleep(1)
            if self.green_agent_process.poll() is not None:
                stderr = self.green_agent_process.stderr.read().decode() if self.green_agent_process.stderr else "Unknown"
                raise Exception(f"Green agent process died: {stderr[:200]}")
            if self.white_agent_process.poll() is not None:
                stderr = self.white_agent_process.stderr.read().decode() if self.white_agent_process.stderr else "Unknown"
                raise Exception(f"White agent process died: {stderr[:200]}")
            
            try:
                response = httpx.get(f"{self.green_agent_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"[Launcher] Agents ready after {i+1} seconds")
                    break
            except:
                if i < max_retries - 1:
                    continue
                else:
                    raise
        
        self._check_agent_health()
    
    def _check_agent_health(self):
        print("\n[Launcher] Checking agent health")
        
        for attempt in range(5):
            try:
                response = httpx.get(f"{self.green_agent_url}/health", timeout=3)
                if response.status_code == 200:
                    print("[Launcher] Green agent is healthy")
                    break
                else:
                    raise Exception(f"Green agent unhealthy: {response.status_code}")
            except Exception as e:
                if attempt < 4:
                    print(f"[Launcher] Waiting for green agent (attempt {attempt+1}/5)")
                    time.sleep(1)
                    if self.green_agent_process.poll() is not None:
                        stderr = ""
                        if self.green_agent_process.stderr:
                            try:
                                stderr = self.green_agent_process.stderr.read().decode()
                            except:
                                pass
                        raise Exception(f"Green agent process died: {stderr[:300]}")
                else:
                    print(f"[Launcher] Green agent health check failed: {e}")
                    if self.green_agent_process and self.green_agent_process.stderr:
                        try:
                            stderr = self.green_agent_process.stderr.read().decode()
                            if stderr:
                                print(f"[Launcher] Green agent stderr: {stderr[:500]}")
                        except:
                            pass
                    self.cleanup()
                    sys.exit(1)
        
        for attempt in range(5):
            try:
                response = httpx.get(f"{self.white_agent_url}/a2a/agent-card", timeout=3)
                if response.status_code == 200:
                    print("[Launcher] Mock white agent is healthy")
                    break
                else:
                    raise Exception(f"White agent unhealthy: {response.status_code}")
            except Exception as e:
                if attempt < 4:
                    print(f"[Launcher] Waiting for white agent (attempt {attempt+1}/5)")
                    time.sleep(1)
                    if self.white_agent_process.poll() is not None:
                        stderr = ""
                        if self.white_agent_process.stderr:
                            try:
                                stderr = self.white_agent_process.stderr.read().decode()
                            except:
                                pass
                        raise Exception(f"White agent process died: {stderr[:300]}")
                else:
                    print(f"[Launcher] White agent health check failed: {e}")
                    if self.white_agent_process and self.white_agent_process.stderr:
                        try:
                            stderr = self.white_agent_process.stderr.read().decode()
                            if stderr:
                                print(f"[Launcher] White agent stderr: {stderr[:500]}")
                        except:
                            pass
                    self.cleanup()
                    sys.exit(1)
    
    async def run_assessment(self):
        print("\n" + "="*70)
        print("Starting Assessment")
        print("="*70)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\n[Launcher] Registering white agent")
            register_response = await client.post(
                f"{self.green_agent_url}/a2a/register_agent",
                json={
                    "agent_url": self.white_agent_url,
                    "agent_card": None,
                }
            )
            
            if register_response.status_code != 200:
                print(f"[Launcher] Registration failed: {register_response.text}")
                return None
            
            assessment_id = register_response.json()["assessment_id"]
            print(f"[Launcher] White agent registered with ID: {assessment_id}")
            
            print("\n[Launcher] Executing assessment task")
            task_response = await client.post(
                f"{self.green_agent_url}/a2a/execute_task",
                json={
                    "jsonrpc": "2.0",
                    "method": "tasks/execute",
                    "params": {
                        "assessment_id": assessment_id,
                        "task_id": "0",
                        "instruction": "List all tickets in the project management system",
                        "tools": [],
                    },
                    "id": "launcher_task_1"
                }
            )
            
            if task_response.status_code != 200:
                print(f"[Launcher] Task execution failed: {task_response.text}")
                return None
            
            result = task_response.json()
            print("[Launcher] Task execution completed")
            
            return result
    
    def display_results(self, result):
        print("\n" + "="*70)
        print("Assessment Results")
        print("="*70)
        
        if result and "result" in result:
            evaluation = result["result"].get("evaluation", {})
            
            print(f"\n Evaluation Metrics:")
            print(f"   Reward: {evaluation.get('reward', 0.0)}")
            print(f"   Status: {evaluation.get('status', 'unknown')}")
            print(f"   Actions Match: {evaluation.get('actions_match', False)}")
            print(f"   Outputs Match: {evaluation.get('outputs_match', False)}")
            print(f"   Violations: {evaluation.get('violations', 0)}")
            
            print(f"\n Task Details:")
            print(f"   Task ID: {result['result'].get('task_id')}")
            print(f"   Assessment ID: {result['result'].get('assessment_id')}")
            print(f"   Timestamp: {result['result'].get('timestamp')}")
            print(f"   Mode: {result['result'].get('mode', 'unknown')}")
            
            print(f"\n Assessment completed successfully!")
        else:
            print("\n  No results available")
            if result:
                print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
        
        print("="*70)
    
    def cleanup(self):
        print("\n[Launcher] Cleaning up")
        
        if self.green_agent_process:
            try:
                self.green_agent_process.terminate()
                self.green_agent_process.wait(timeout=5)
                print("[Launcher] Green agent terminated")
            except Exception as e:
                print(f"[Launcher] Error terminating green agent: {e}")
                try:
                    self.green_agent_process.kill()
                except:
                    pass
        
        if self.white_agent_process:
            try:
                self.white_agent_process.terminate()
                self.white_agent_process.wait(timeout=5)
                print("[Launcher] Mock white agent terminated")
            except Exception as e:
                print(f"[Launcher] Error terminating white agent: {e}")
                try:
                    self.white_agent_process.kill()
                except:
                    pass
    
    async def run(self):
        try:
            self.start_agents()
            
            result = await self.run_assessment()
            
            self.display_results(result)
            
        except KeyboardInterrupt:
            print("\n\n[Launcher] Interrupted by user")
        except Exception as e:
            print(f"\n[Launcher] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    launcher = AssessmentLauncher()
    asyncio.run(launcher.run())


if __name__ == "__main__":
    main()