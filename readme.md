# Multi-Agent Swarm

This example demonstrates a multi-agent swarm with three agents: an Enhancer, an Executor, and a Checker. The agents work together to process user queries and provide well-thought-out, verified responses.

## Setup

To run this example:

1. Ensure you have installed the Swarm framework as described in the main README.
2. Set up your `.env` file in the root directory with the necessary API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Navigate to this directory:
   ```
   cd examples/multi_agent_swarm
   ```
4. Run the example:
   ```
   python multi_agent_swarm.py
   ```

## Agents

1. **Enhancer Agent**: Enhances user prompts by adding instructions for reasoning steps and chain of thought.
2. **Executor Agent**: Executes the enhanced prompts and provides detailed, well-thought-out responses.
3. **Checker Agent**: Checks responses for correctness, approves correct ones, and edits/improves incorrect ones.

## Process Flow

1. User input is received by the Enhancer Agent.
2. Enhancer Agent enhances the prompt and transfers to the Executor Agent.
3. Executor Agent processes the enhanced prompt and transfers the response to the Checker Agent.
4. Checker Agent verifies the response. If correct, it's shown to the user. If not, it's edited and the process restarts from the Enhancer Agent.

This example uses the `run_demo_loop` helper function to create an interactive Swarm session.

