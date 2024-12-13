# CLI Agent Processor - A CLI tool for processing text using AI agents.
#
# TODOs: 1. Given an input file, an output file, a prompt, and a model name
#        2. Create a GPT Chat agent from agent_c
#        3. Read in the file as a string
#        4. Call the agent one_shot method the file contents as the user input, along with the prompt
#        5. Write the output to the output file

import asyncio
import argparse
from agent_c import GPTChatAgent

async def main(input_file, output_file, prompt, model_name):
    agent = GPTChatAgent(model_name=model_name)

    with open(input_file, 'r') as file:
        input_text = file.read()

    # Use `count_tokens` on the agent object to make sure the text isn't over 50k tokens
    token_count = agent.count_tokens(input_text)
    max_tokens = 50000

    if token_count > max_tokens:
        lines = input_text.split('\n')
        chunks = []
        current_chunk = []

        for line in lines:
            current_chunk.append(line)
            if agent.count_tokens('\n'.join(current_chunk)) > max_tokens:
                current_chunk.pop()  # Remove the last line that caused the overflow
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]  # Start a new chunk with the current line

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

            output_text = ""
            # Process chunks in parallel
            tasks = [agent.one_shot(user_input=chunk, prompt=prompt) for chunk in chunks]
            results = await asyncio.gather(*tasks)
            output_text = "\n".join(results) + "\n"
        else:
            output_text = await agent.one_shot(user_input=input_text, prompt=prompt)

    with open(output_file, 'w') as file:
        file.write(output_text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('input_file', type=str, help='Input file path')
    parser.add_argument('output_file', type=str, help='Output file path')
    parser.add_argument('prompt', type=str, help='Prompt to use')
    parser.add_argument('model_name', type=str, help='Model name to use')
    args = parser.parse_args()
    asyncio.run(main(args.input_file, args.output_file, args.prompt, args.model_name))

