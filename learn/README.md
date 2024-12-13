# A step by step guide to getting started with Agent C

This series of lessons is meant to introduce you the concepts and code needed to work with Agent C. As you move through the lessons I'll explain how the APIs we're calling work and how the abstractions in Agent C assist you in creating an agent.  I have made *zero* effort to ensure that the lessons are of equal length.  Each lesson is intended to introduce a concept (or part of a concept() and is as long and drawn out or short and sweet as it takes to get there.

**Note:**

> If you don't already know Python, I don't go out of my way to explain Python in any detail aside from walking you through the PyCharm setup below.  If you know pretty much any other language you'll likely be fine going through the lessons.  The code in them isn't that complex.

## Lesson plan

Currently complete lessons are in bold

1. **Simple chat completions** - Create a small app that can send a prompt and get a response.
2. **Context windows and you** - Learn about context windows, tokens and ways to deal with large files.  Create an app that can summarize multiple blog posts in parallel.
3. **Tool use in agents** - Learn how tool use works at the API level, how Agent C abstracts that and how to **use** tools with an agent. Create an app that can give you a weather forecast.
4. **Beyond one-shots** - Learn how to create an agent you can chat with and how to work with the chat event stream.
5. **Prompt composition** - Learn about the prompt composition system, why it exists and how to use it. 
6. **The Workspace tool** - Learn how to give your agent access to a file system.
7. **Working with Media** - Learn how to provide images as input to an agent and how to handled `RednderMedia` events in the stream.
8. *Chat session management* - In this lesson we'll introduce Zep from our docker stack and show how it handles a LOT of heavy lifting for us.
9. *Creating your own tools* - This lesson will go over the the creation of tools with some depth. We will create a tool that can analyze transcripts of meetings and produce various types of output from it.
10. (more lighter weight lessons might get injected here)
11. *Segmentation, vectorization*
12. *RAG*

## Folder layout

- The `learn/lessons` sub-folder contains a series of lessons that build on each other to introduce various concepts and framework features you'll need to understand to make full use of Agent C.1

- The `learn/example_code` folder contains, you guessed it, example code for the lessons. `learn/sample_data` has the data for these examples

- The `learn/lab_code` folder is set aside for  you to use as a scratchpad without needing to worry about git. 

## Initial setup

Before you can start any of the lessons there's some baseline setup stuff that needs to be done.  This is an abbreviated version of the full setup from the main README.  If you've done all that you're good to go.

### Before you begin you will need:

- A decent Python IDE like [PyCharm](https://www.jetbrains.com/pycharm/?var=1).
  - There will be PyCharm specific instructions here and there but it's not strictly required as long as you can translate what my directions are for your IDE of choice. 
- Python 3.10 or higher.
- If you are on Windows, I highly suggest installing the [Windows Terminal Preview](https://apps.microsoft.com/detail/9n8g5rfz9xk3?hl=en-us&gl=US) from the Microsoft Store

### Clone the repo and setup your Python environment

Python virtual environments are incredibly useful for managing dependencies and creating isolated environments for different projects. When working on multiple Python projects, each project may require different versions of packages or libraries. Without virtual environments, it can be challenging to manage these dependencies, leading to conflicts and compatibility issues. Virtual environments allow you to create separate, self-contained environments for each project, ensuring that the required packages and their versions are isolated from other projects. 

The easiest way to accomplish this is to launch PyCharm and select "get from VCS". Give it the repo URL (https://github.com/centricconsulting/agent_c.git) and tell it where to save the project.

- PyCharm may prompt you to trust the project, if so, you should do so.
- PyCharm should next offer to set up virtual environment for you. The defaults should be fine, as long as nothing is red.

PyCharm will set up a new Python installation in the `.venv` subfolder and install all of the dependencies for Agent C in it.  This can take a bit to complete.

#### Note

PyCharm will automatically use this virtual environment as will the built in terminal for PyCharm.  Outside of PyCharm you will need to activate your virtual environment before using it:

- On Linux/MacOS/WSL run: `source .venv/bin/activate`
- If you're on Windows run: `.venv\Scripts\activate.bat`

### Set up your env file

In PyCharm, right click on the project root folder and add a new file called `.env`.  **NOTE THE LEADING DOT** 

This file allows us to store environment variables on a per-project basis and is where we'll store our configuration we need. This file is ignored by git and can contain your API keys without worrying about accidentally committing a secret.

We only need to worry about one variable for a bit, `OPENAI_API_KEY`.  Add a line to the `.env` file that looks something like this: `OPENAI_API_KEY=YOUR_API_KEY`. If you don't yet have an Open AI key see below.

#### Get an Open AI API Key.

If you do not all ready have an Open AI API Key, that's a HARD requirement for working with this code.  Visit the signup page for the [Open AI Platform](https://platform.openai.com/signup) to sign up.  

After signing up, deposit $20 USD with them for usage credits.  **This is needed for GPT-4 and beyond access**

### Create a default run configuration

In the menu bar for PyCharm there is a drop-down menu for "run configurations".  Select the "Edit Configurations" option from it, then "Edit configuration templates" from the dialog that appears.

In the "Run/Debug configuration templates" dialog, find "Python" in the list and:

- From the `Modify options` drop-down enable "Emulate terminal in output console"
- From the `Modify options` drop-down enable "Focus run/debug tool window when started"
- Click the folder icon in `Working directory` edit box and select the root folder of the project. 
- Click the folder icon in the edit box for `Paths to "env" files` section and select your `.env` file you made above.
- Click "OK"

## You're done!

Any other setup tasks will be addressed in the lessons.