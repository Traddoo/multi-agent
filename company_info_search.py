from swarm import Swarm, Agent
from openai import OpenAI
from exa_py import Exa
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = Swarm(client=openai_client)
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))

def search_prop_firm_info(query, num_results=5):
    results = exa_client.search_and_contents(
        query,
        type="keyword",
        num_results=num_results,
        text=True,
        start_published_date="2023-01-01",
        category="company",
        include_domains=["propfirmmatch.com"],
        summary=True
    )
    formatted_results = []
    for result in results.results:
        formatted_results.append(f"Title: {result.title}\nURL: {result.url}\nSummary: {result.summary}\n")
    return "\n".join(formatted_results)

def search_trustpilot_reviews(company_name, num_results=3):
    query = f"site:trustpilot.com {company_name} reviews"
    results = exa_client.search_and_contents(
        query,
        type="keyword",
        num_results=num_results,
        text=True,
        start_published_date="2023-01-01",
        summary=True
    )
    formatted_results = []
    for result in results.results:
        formatted_results.append(f"Title: {result.title}\nURL: {result.url}\nSummary: {result.summary}\n")
    return "\n".join(formatted_results)

prop_firm_search_agent = Agent(
    name="Prop Firm Search",
    instructions="""You are an agent that searches for proprietary trading firm information on propfirmmatch.com and TrustPilot reviews. Use the search_prop_firm_info function to find information based on the user's query, and the search_trustpilot_reviews function to find reviews. Both functions take two parameters: query/company_name (string) and num_results (integer, default 5 for prop firm info, 3 for reviews).

    If the user describes criteria for a firm:
    1. Identify the key criteria from the user's description.
    2. Formulate a search query based on these criteria.
    3. Call the search_prop_firm_info function with this query.
    4. Summarize the results, highlighting firms that match the criteria.

    If the user names a specific firm:
    1. Use the firm's name as the search query for both functions.
    2. Call the search_prop_firm_info function with the firm's name.
    3. Call the search_trustpilot_reviews function with the firm's name.
    4. Provide a detailed summary of the information found about the firm from propfirmmatch.com.
    5. Follow this with a summary of the TrustPilot reviews, including overall sentiment and key points.

    Always include relevant details such as leverage, accepted countries, and any unique features of the firms. For reviews, include the overall rating if available.""",
    functions=[search_prop_firm_info, search_trustpilot_reviews],
)

if __name__ == "__main__":
    console = Console()
    console.print(Panel("Proprietary Trading Firm Search. Type 'exit' to quit.", style="bold green"))

    while True:
        user_input = console.input("\n[bold cyan]Enter your query or firm name:[/bold cyan] ")
        if user_input.lower() == 'exit':
            break

        search_response = client.run(prop_firm_search_agent, messages=[{"role": "user", "content": user_input}])
        search_results = search_response.messages[-1]["content"] if search_response.messages else "No search results."
        
        console.print(Panel(f"[bold blue]Prop Firm Information and Reviews:[/bold blue]\n{search_results}", border_style="blue"))

    console.print("\n[bold blue]Search Complete[/bold blue]")
