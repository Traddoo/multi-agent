from swarm import Swarm, Agent
from swarm.repl import run_demo_loop
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()  # This loads the variables from .env

# Initialize the OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the Swarm client with the OpenAI client
client = Swarm(client=openai_client)

def transfer_to_executor(enhanced_prompt):
    print(f"\nEnhancer Agent output:\n{enhanced_prompt}")
    return executor_agent, {"prompt": enhanced_prompt}

def transfer_to_planner(executed_response):
    print(f"\nExecutor Agent output:\n{executed_response}")
    return planner_agent, {"response": executed_response}

def transfer_to_checker(executed_response):
    print(f"\nExecutor Agent output:\n{executed_response}")
    return checker_agent, {"response": executed_response}

def transfer_to_enhancer(checked_response):
    print(f"\nChecker Agent output:\n{checked_response}")
    return enhancer_agent, {"response": checked_response}

enhancer_agent = Agent(
    name="Enhancer",
    instructions="""You are an agent that enhances user prompts. Your task is to:
    1. Reword the user's input to be more clear, specific, and thorough.
    2. Prepend the following instructions to the enhanced prompt:

    [Instructions for the next agent:
    1. Begin by enclosing all thoughts within <thinking> tags, exploring multiple angles and approaches.
    2. Break down the solution into clear steps within <step> tags.
    3. Start with a 20-step budget, requesting more for complex problems if needed.
    4. Use <count> tags after each step to show the remaining budget. Stop when reaching 0.
    5. Continuously adjust your reasoning based on intermediate results and reflections, adapting your strategy as you progress.
    6. Regularly evaluate progress using <reflection> tags. Be critical and honest about your reasoning process.
    7. Assign a quality score between 0.0 and 1.0 using <reward> tags after each reflection.
    8. Use the reward score to guide your approach:
       - 0.8+: Continue current approach
       - 0.5-0.7: Consider minor adjustments
       - Below 0.5: Seriously consider backtracking and trying a different approach
    9. If unsure or if reward score is low, backtrack and try a different approach, explaining your decision within <thinking> tags.
    10. For mathematical problems, show all work explicitly using LaTeX for formal notation and provide detailed proofs.
    11. Explore multiple solutions individually if possible, comparing approaches in reflections.
    12. Use thoughts as a scratchpad, writing out all calculations and reasoning explicitly.
    13. Synthesize the final answer within <answer> tags, providing a clear, concise summary.
    14. Conclude with a final reflection on the overall solution, discussing effectiveness, challenges, and solutions.
    15. Assign a final reward score.]

    3. Ensure these instructions are clearly separated from the enhanced user prompt.
    Do not answer the prompt yourself, only enhance it and add the instructions.""",
    functions=[transfer_to_executor],
)

clarifier_agent = Agent(
    name="Clarifier",
    instructions="You are an agent that clarifies and enhances user prompts. Reword the user's input to be more clear, specific, and thorough. Ask for additional information if needed.",
    functions=[transfer_to_executor],
)

executor_agent = Agent(
    name="Executor",
    instructions="You are an agent that executes clarified prompts. Provide a detailed, well-thought-out response to the clarified question or request.",
    functions=[transfer_to_planner],
)

checker_agent = Agent(
    name="Checker",
    instructions="You are an agent that checks responses for correctness. If correct, approve it. If not, edit and improve it. Always provide your reasoning.",
    functions=[transfer_to_enhancer],
)

planner_agent = Agent(
    name="Planner",
    instructions="You are an agent that creates action plans based on the user's request and the executor's response. Provide a step-by-step plan with resources and instructions for the user to follow up on their request.",
    functions=[],
)

if __name__ == "__main__":
    console = Console()
    console.print(Panel("Starting Multi-Agent Swarm. Type 'exit' to quit.", style="bold green"))

    while True:
        user_input = console.input("\n[bold cyan]User:[/bold cyan] ")
        if user_input.lower() == 'exit':
            break
        console.print(Panel(f"[bold cyan]User input:[/bold cyan]\n{user_input}", border_style="cyan"))

        # Enhancer Agent
        enhanced_response = client.run(enhancer_agent, messages=[{"role": "user", "content": user_input}])
        enhanced_prompt = enhanced_response.messages[-1]["content"]
        console.print(Panel(f"[bold green]Enhanced Prompt:[/bold green]\n{enhanced_prompt}", border_style="green"))

        # Executor Agent
        executed_response = client.run(executor_agent, messages=[{"role": "user", "content": enhanced_prompt}])
        executed_output = executed_response.messages[-1]["content"]
        console.print(Panel(f"[bold yellow]Executor Response:[/bold yellow]\n{executed_output}", border_style="yellow"))

        # Planner Agent
        plan_response = client.run(planner_agent, messages=[
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": executed_output},
            {"role": "user", "content": "Based on this information, create an action plan with resources and instructions."}
        ])
        action_plan = plan_response.messages[-1]["content"]
        console.print(Panel(f"[bold magenta]Action Plan:[/bold magenta]\n{action_plan}", border_style="magenta"))

        console.print("\n[bold blue]Process Complete[/bold blue]")
