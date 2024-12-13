# Context windows and you.

**Important note**: This lesson is somewhat wasteful with tokens.  I'm being wasteful on purpose up front to help get you in the mindset of optimizing your token usage / costs.  You don't necessarily need to run every example to follow along. Example outputs for large token tasks has been provided. That being said, we're talking about a dollar or so max.

A context window for a large language model refers to the span of text that the model looks at when making predictions about what word or phrase should come next. It is essentially the amount of recent input text that the model can consider while generating responses or completing a task.

The context window size is determined by the model's architecture, specifically by its number of attention layers and the maximum sequence length it can handle. For instance, GPT-3 has a context window of 2048 tokens, meaning it can consider the last 2048 tokens (words or pieces of words) of input when generating its output. If the text input exceeds the context window size, the model won't take the earlier parts into consideration, which could result in losing important information relevant to the current output.

The context window sizes have been rapidly growing:

- GPT-3.5.turbo had 4k, then 16k
- GPT-4 had 8k, then 32k
- GPT-4-turbo has 128k

Increased context window sizes are a huge help but they don't tell the whole story.  There's a difference between what the model can HOLD vs what it can pay close attention to.  Just because a model has a context window large enough doesn't mean that consuming it all is the best option.  In rarely is in fact.

Tokens are a commodity, the more of them you use, the more you pay.  The larger the model context size, the larger cost per token. Prices have dropped considerably but not to the point where "can I do this with 3.5?" isn't the first thing I consider when considering a new workload.  3.5-turbo is fast and cheap and good for a lot of tasks, it's just terrible at following directions.

## Counting tokens

In order to manage your token budget you need to be able to measure it. `agent_c.utils.token_c+ounter` has as a class that can count tokens for any our our back ends using a consistent interface:

```python
token_counter = TikTokenCounter()  # Used for non-claude models
token_count = token_counter.count_tokens("In order to manage your token budget you need to be able to measure it.")

# Ouputs:  Token count: 17
```

- Behind the scenes the token counter is using the [TikToken]([GitHub - openai/tiktoken: tiktoken is a fast BPE tokeniser for use with OpenAI&#39;s models.](https://github.com/openai/tiktoken)) library for GPT or the `AntropicClient` client class, to count tokens  
- The GPT agent has a TikToken encoder as a property that can also be used to count tokens.

## Working with large files

Example 3 is somewhat contrived but it allows us to start dipping our toes into dealing with large amounts of data when the model really needs to see every line in order to complete the task.

The file `learn/sample_data/blog_posts.md` contains several blog posts exported from the Centric blog sometime last year to use in a Custom GPT example.  Each post is in Markdown format and includes a short header with information about the URL, title and author.

This code loads the file and counts the tokens in it.  The full version is saved as `learn/example_code/example_3.py`

```python
token_counter = TikTokenCounter()
file_name: str = 'learn/sample_data/blog_posts.md'
file_text: str = ""

with open(file_name, 'r', encoding='utf-8') as file:
    file_text = file.read()

token_count = token_counter.count_tokens(file_text)
print(f"Token count: {token_count}")

# Output: Token count: 23620
```

Let's say we'd like a summary of each of the blog posts contained within the file.  Right off the bat we know that this is way too big for 3.5-Turbo and even 3.5-Turbo-16k.  So we might try to tackle this by using a larger context window:

```python
file_name: str = 'learn/sample_data/blog_posts.md'

with open(file_name, 'r', encoding='utf-8') as file:
    user_message = file.read()

agent = GPTChatAgent()

model_name: str = "gpt-4-turbo-preview"
prompt: str = ("The user message contains several blog posts in Markdown format. "
               "Each post starts with a Markdown header indicating the title, author, and url."
               "Produce a summary of each of the blog post in Markdown format."
               )

result: str = await agent.one_shot(model_name=model_name, user_message=user_message, prompt=prompt)

print(result)
```

This is saved as `learn/example_code/example_4.py`

Note: This is actually an example of a naive way to solve this problem. If you were to run this, it will run for a minute  or so (56.327362 seconds for me) and spit out a bunch of summaries just like you'd expect.  But it's fairly slow to return a response since we're not streaming the results. 

I've provided output from this example saved to a Markdown file in `learn/sample_data/example_4_output.md`

### Segmentation

In later lessons we'll talk about segmentation in greater depth but we're going to touch on it now in an easier to understand way so that we can get the jargon out of the way.

You will often hear the term "segmentation strategy" being used. "Segmentation" in the context of LLMs typically refers to the process of dividing text into smaller chunks to allow an LLM to process them. For such a simple concept there is a surprising amount of nuance in the process, especially once you start talking about indexing documents into a searchable database.

A segmentation strategy has, at a minimum, a "boundary condition". The boundary condition determines when we want to create a new segment based on some condition. For example, if we're dealing with transcripts we might set a target size for each segment but ensure that we always include full lines of transcript in each segment.  For a document, we might segment based on paragraphs. I often refer to this as the "smallest unit of information" used to build the segment.

There is a LOT of bad guidance out there on this aspect of working with LLMs, so let me be clear:  ***Using characters or words as boundary conditions is a terrible idea** 

### Improving our example with segmentation

We've established that stepping up to the larger context model allowed the agent to complete the task at the expense of speed.  Let's see if we can shorten the run time with parallel processing. 

If you look at the `learn/sample_data/blog_posts.md` file you'll see that it has a layout like this:

```markdown
# Blog post title:  TITLE
# Author: AUTHOR
# URL: URL
* * *

content

# Blog post title:  TITLE 2
```

This allows us to set up a very simple segmentation strategy. Using the title header as our boundary condition ensures that each segment contains an entire blog post. 

```python
def segment_blog_posts(content):
    posts = []
    current_post = []

    for line in content.split('\n'):
        if line.startswith('# Blog post title:'):
            if current_post:
                posts.append('\n'.join(current_post))
                current_post = []
            current_post.append(line)
        else:
            current_post.append(line)

    if current_post:
        posts.append('\n'.join(current_post))

    return posts
```

Now that we can split that file into multiple posts we can take advantage of the asynchronous nature of Agent C and the built in concurrency limiter in the `ChatAgent` code and execute multiple summaries in parallel.

```python
blog_posts = segment_blog_posts(file_contents)

agent = GPTChatAgent(concurrency_limit=15)
model_name = "gpt-4-turbo-preview"
prompt = "The user message contains a blog post exported to Markdown format. Produce a summary of the blog post."

results = await agent.parallel_one_shots(blog_posts, model_name=model_name, prompt=prompt)

for index, result in enumerate(results):
    print(f"# Post {index + 1} summary:\n{result}\n\n")
```

The `ChatAgent` base class uses a Semaphore to limit the number of simultaneous calls to the completion APIs so that we don't exceed our tokens per minute rate limit with the vendors. Rate limits are determined on a per user / per model basis.  The more you've used their API the higher your rate limit becomes.  Each model also has a unique limit based on their context size.  This is much less of a problem than before, but the concurrency limit of 15 may be too high for your account.  If so, you can dial it back.  The default is 3 and was from back in the 8k context days.

Running this can lead to some surprises when you're new. "If I can do 12 in 60 seconds as one file, SURELY I can them in less than 10 seconds by splitting them up running them all at the same time?" seems perfectly reasonable.  Heck the math works out to 5 seconds, so doubling it should be safe right?  

`learn/example_code/example_5.py` has a full version of the example above.  Given the foreshadowing above, if you run this example you will not at all be surprised to find that it doesn't complete in anything NEAR 10 seconds. Even with a concurrency limit that allows all of them to be run at the same time, we still take about 30 seconds to finish.

If you open the `learn/sample_data/` folder in a file manager you'll quickly see that `example_5_output.md` is roughly 3X the size of `example_4_output.md`. Way up near the beginning I wrote: *Just because a model has a context window large enough doesn't mean that consuming it all is the best option*.  This is a prime example of that.

Because the model was generating a whole bunch of summaries before, each individual summary was quite short.  By dividing the work up into multiple tasks we allowed the model to focus on a single task and as a result the output was much richer.  Since each summary was much larger the completion calls took longer.

If we didn't want those larger summaries, we might try to control this by limiting the number of tokens in allowed in the response by adding a `max_tokens` parameter to the call but that would simply truncate the summary before the model completed it.  A better way to deal with it is with model instruction:

```python
prompt: str = ("The user message contains a blog post exported to Markdown format "
               "Produce a concise summary of the blog post using no more than a paragraph.")
```

The file `learn/example_code/example_6.py` is the same as example 5, just with clear instructions as to the expected length of output. The run time drops to about 15 seconds. And `learn/sample_data/example_6_output.md` is smaller than the output from example 5, yet still larger than example 4. 

Note: All LLMs seem to have a preconceived idea for how long a summary should be, with an upper limit. Long form content ends up losing a lot of information due to this bias and care must be taken to deal with it.  But that's a different lesson

## Wrapping up

- We've learned **a couple** strategies for dealing with large content.  
- We've leveraged segmentation and parallel processing to reduce our run time.
- We've adjusted our model instructions to control output tokens AND reduce run time again.

We should pat ourselves on the back!  From 60 seconds down to 15 is a big time savings.  Except... 

<sub> I set you up.</sub>

Example 4 was meant to serve as an example of why more context doesn't always mean better results. And it does that well I think.  Clearly both the quality and run time improved when we used less of the context at once.

But I lead you astray intentionally because it's such an easy trap to fall into when you're working with these models.  Just because you've been using a particular model to solve a problem, doesn't mean it's the best choice if you reframe the problem.

The moment we switched to segmentation and parallel processing to try and reduce the run time we should have thought *can 3.5-turbo handle this task?*

So I'll leave you with this:

- `learn/example_code/example_7.py` is example 5 using 3.5-turbo it takes 8 seconds to complete.
- `learn/example_code/example_8.py` is example 6 using 3.5-turbo it takes **THREE seconds** to complete.
