# Working with the web tool

- The web tool provides the agent a way to fetch web content from a URL. 
- It can make use of a cache passed in, or will construct a disk cache that uses the expires header for time to live.
- Ir uses `ContentFormatter` objects to shape the output for the model.


## Content formatters
A content formatter is responsible for taking a raw response from the webserver and packaging it up for the model.
While the existing formatters are geared around HTML there's no reason your formatter couldn't return a JSON string.

- The base `ContentFormatter` class will convert HTML to Markdown. Better than HTML for tokens but we can do better.
- The `ReadableFormatter` class first runs the content through the readability algorithm to extract the main content of the page and converts THAT to Markdown
  - This is the default formatter that's used by the web tool
  - This sometimes misses the mark, which is why you can specify formatters based on the url.
  - This is a HUGE savings in tokens


Here's the `format` method from an example formatter for Centric blog posts.

```python
def format(self, content: str, url: str) -> str:
    # Create a readability Document for the content
    doc = Document(content)
    
    # Convert the summary to Markdown
    summary = markdownify(doc.summary(), heading_style='ATX', escape_asterisks=False, escape_underscores=False)

    # Search the HTML for the author name as it's not in the main content
    author_pattern = re.compile(r'author-meta__name">By (.*?)</')
    a_matches = author_pattern.findall(content)

    # Search the HTML for the post date as it's not in the main content
    date_pattern = re.compile(r'<div class="post-meta__date">(.*?)</')
    d_matches = date_pattern.findall(content)
    
    # Making sure the model can cite sources
    markdown = f"# Blog Post URL: {url}\n# Blog Post Title: {doc.title()}\n"

    # Add the author and post date if we have them
    if a_matches:
        markdown += f"# Blog Post Author: {a_matches[0]}\n"
    if d_matches:
        markdown += f"# Blog Post Date: {d_matches[0]}\n***\n"

    # aaaaaaand scene    
    return f"{markdown}{summary}"
```

The other piece of the puzzle is the `match` method, which by default uses a regular expression to determine if the formatter applies to a url.  Derived classes can set it like so:

```python
def __init__(self):
    super().__init__(re.compile(r".*centricconsulting\.com/blog"))
```
Here we're signaling that the formatter is valid for anything that begins with `*centricconsulting.com/blog`

The tool will look through the list of formatters handed to it in the constructor and use the first one that says they handle the URL.  This allows us to use a formatter that handles `*` as the last in the list.