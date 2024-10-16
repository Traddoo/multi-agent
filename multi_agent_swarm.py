from swarm import Swarm, Agent
from swarm.repl import run_demo_loop
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from exa_py import Exa
import json

load_dotenv()  # This loads the variables from .env

# Initialize the OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the Swarm client with the OpenAI client
client = Swarm(client=openai_client)

# Initialize the Exa client
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))

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

def search_internet(query, num_results=5):
    results = exa_client.search(query, num_results=num_results)
    formatted_results = []
    for result in results:
        formatted_results.append(f"Title: {result.title}\nURL: {result.url}\nSnippet: {result.snippet}\n")
    return "\n".join(formatted_results)

def transfer_to_internet_search(query):
    print(f"\nTransferring to Internet Search Agent with query:\n{query}")
    return internet_search_agent, {"query": query}

enhancer_agent = Agent(
    name="Enhancer",
    instructions="""You are an agent that enhances user prompts. Your task is to:
    1. Reword the user's input to be more clear, specific, and thorough.
    2. Determine if the query requires internet search or not.
    3. If internet search is required, call the transfer_to_internet_search function with the enhanced query.
    4. If not, return the enhanced prompt with the following instructions prepended:

    [Instructions for the next agent:
    1. Begin by enclosing all thoughts within <thinking> tags, exploring multiple angles and approaches.
    2. Break down the solution into clear steps within <step> tags.
    3. Use <count> tags after each step to show the remaining budget. Stop when reaching 0.
    4. Continuously adjust your reasoning based on intermediate results and reflections.
    5. Regularly evaluate progress using <reflection> tags.
    6. Synthesize the final answer within <answer> tags, providing a clear, concise summary.
    7. Conclude with a final reflection on the overall solution.]

    Ensure these instructions are clearly separated from the enhanced user prompt.""",
    functions=[transfer_to_executor, transfer_to_internet_search],
)

clarifier_agent = Agent(
    name="Clarifier",
    instructions="You are an agent that clarifies and enhances user prompts. Reword the user's input to be more clear, specific, and thorough. Ask for additional information if needed.",
    functions=[transfer_to_executor],
)

executor_agent = Agent(
    name="Executor",
    instructions="You are an agent that executes enhanced prompts. Provide a detailed, well-thought-out response to the enhanced question or request.",
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

internet_search_agent = Agent(
    name="Internet Search",
    instructions="You are an agent that searches the internet for relevant information. Use the search_internet function to find information, then summarize and present the findings. Always include the source URLs in your response.",
    functions=[search_internet, transfer_to_executor],
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
        if enhanced_response.messages:
            last_message = enhanced_response.messages[-1]
            function_call = last_message.get("function_call")
            if function_call and isinstance(function_call, dict) and function_call.get("name") == "transfer_to_internet_search":
                # Internet Search Agent
                search_query = function_call.get("arguments", {}).get("query", user_input)
                search_response = client.run(internet_search_agent, messages=[{"role": "user", "content": search_query}])
                search_results = search_response.messages[-1]["content"] if search_response.messages else "No search results."
                console.print(Panel(f"[bold blue]Internet Search Results:[/bold blue]\n{search_results}", border_style="blue"))
                
                # Pass search results to Executor Agent
                executed_response = client.run(executor_agent, messages=[
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": f"Based on the internet search, here are the results:\n\n{search_results}\n\nPlease provide a detailed response to the user's query using this information."}
                ])
            else:
                enhanced_prompt = last_message.get("content", user_input)
                console.print(Panel(f"[bold green]Enhanced Prompt:[/bold green]\n{enhanced_prompt}", border_style="green"))
                
                # Executor Agent
                executed_response = client.run(executor_agent, messages=[{"role": "user", "content": enhanced_prompt}])
        else:
            console.print(Panel("[bold red]Error: Enhancer Agent returned no response.[/bold red]", border_style="red"))
            continue

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
