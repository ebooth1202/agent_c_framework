# Agent C

This project contains a fairly minimalist framework for interactive tool-using AI agents.  It serves as the core runtime of the Agent C accelerator from Centric Consulting.  

The underlying agent handles things like streaming responses, parallel tool use, parallel tool calls, etc and allows us to either receive events via a callback, or consume content tokens via an async generator.  Both the agent and agent tools are fully async and designed to be non-blocking. 

## Getting started

### Before you begin you will need:

- A decent Python IDE like PyCharm.
- Python 3.10 or higher.
- On Windows you will need the Microsoft visual c++ build tools.  You can get them via `winget install Microsoft.VisualStudio.2022.BuildTools`

### Clone the repo

```shell
git clone https://github.com/centricconsulting/agent_c_framework.git
```

### Setup your Python development environment

The batch file/shell script `inital_setup` can be ran to set up an isolated Python development environment and install the dependencies required to run Agent C.  If you'd rather do it yourself the steps are below, otherwise continue on.

#### Create an Python virtual environment in the project root.

```shell
python -m venv venv
```

After this there will be a `venv` sub-folder containing a clean Python installation 

While still in that same command line you will want to activate the environment.  

- On Linux/MacOS/WSL run: `source venv/bin/activate`
- If you're on Windows run: `venv\Scripts\activate.bat`

Still in that same command line run the following to pull down all the dependencies
- On Linux/MacOS/WSL run: `scripts/install_deps.sh`
- If you're on Windows run: `scripts/install_deps.bat`

Or do it by hand with:

```shell
cd src
pip install -e agent_c_core
pip install -e agent_c_tools
pip install -e agent_c_reference_apps 
```

Make sure to set the python interpreter in your IDE to the one now in `<project_root>/venv`. 

### Note:
Each time you pull latest it's recommended to install the packages again to ensure new dependencies are installed.  There is a `fetch_latest` script in the scripts folder the project that will do this for you.

## Get an Open AI API Key.

If you do not all ready have an Open AI API Key, that's a HARD requirement for working with this code.  Visit the signup page for the [Open AI Platform](https://platform.openai.com/signup) to sign up. 

- A ChatGPT Pro subscription is not sufficient.

After signing up, deposit $20 USD with them for usage credits.  **This is needed for GPT-4 and beyond access**

### Get an Eleven Labs API Key (optional but cool)

[Eleven Labs](https://elevenlabs.io/) provides the current state of the art in text to speech models. Nobody comes close to them in quality or capability, they know it and have priced their product appropriately. On top of how well their model mimics emotion and their massive voice library, they offer the ability to create new voices or clone a human voice.

The reference app implements bi-directional-streaming TTS. Model responses are streamed as tokens to the app, which streams those tokens up to Eleven Labs, which streams chunks of MP3 audio back to the app which then streams them to the `mpv` process to play them (That's 3 for the price of 2 BTW.)  Side note: This is not meant to be an example of how to do playback in production, the support exists to test the tool...

The reference toolbelt `VoiceTools` allows the model to work with the ElevenLabs API and the app itself to select the voice used for TTS output and to save the preference in their user preferences.

If you plan on using voice output, install the player MPV from https://mpv.io/installation/ 

### Set up your application environment

In the root folder of the repo there's an `example.env` that you should copy to `.env` and complete similar to how you just finished doing above.

## Run the reference agent

From the root folder of the project you can launch the reference agent with the following command:

```shell
agent_c-cli <opts>
```

or:

```shell
agent_c-web <opts>
```

#### Command line options

- `--model [model_name]` allows you to override the default model used by the agent.
- `--prompt_file [/path/to/file]` allows you to supply a file to be used as the persona portion of the system prompt for the agent.
- `--userid [user_id]` provide a user ID to be used for the user in the chat session.  Setting this will override the value from the `.env` file for `CLI_CHAT_USER_ID`
- `--voice` turns on the streaming text to speech and enables the Eleven Labs voice tool for the agent.

### In app commands (CLI only)

There are a small number of commands available within the app available by typing them alone on in the chat input and hitting enter:

- `!exit` or `!!!` - Will exit the app.
- `!keep` - will mark a session to be kept after exiting. By default, sessions are ephemeral and are deleted on app exit.
- `!!!!` - will exit the app and without deleting the session.
- `!compact` - will compact the message array being used for the chat down to the contents of the zep memory.  This is handy for clearing out tool calls and results or reducing the overall token count of the session. 

In addition the up/down arrows act as a "command history" allowing you easy access to anything you've submitted as input to the app. 

#### Workspaces

The reference app will create a `LocalStorageWorkspace` titled `project` and make it available to the agent. This means that the agent will have full read/write access to any file/folder in under the project root. A `temp` folder exists in the repo for the sole purpose of providing a standard place to drop things in that you'd like the agent to work with.

To work with files in workspaces, refer to the workspace name and the relative path within the workspace like:  "Could you load temp/data.csv from the project workspace and..."

## Personas

Several persona files exist in the folder `personas`.  They can be used with the `--prompt_file` option to convert Agent C from a generic agent into something with a purpose.  The opening lines of each should clue you in to what they're for. 



### PyPolish

The persona file `py_polish.md` contains a persona file that can clean up up your code, add type hints, doc comments etc.  It's also aware the project structure and how to read and write to the project code.

## Additional docs

- Each sub module has it's own README, which may or may not have content...
- `docs/tools.md` outlines how to create new tools for the agent as well as info on the existing tools.  And as mentioned above, the Toolman persona can help you quite a bit when building out new tools.
- `docs/prompts.md` - Details how the prompts builder works
- `docs/web_toolmd` - Explains how the Web tool and the content formatters works.

## License This project is licensed under the Business Source License 1.1. 
- **Licensor**: Centric Consulting
- **Licensed Work**: Agent C Framework
- **Change Date**: 2024-12-31
- **Additional Use Grant**: None

For details, see the [LICENSE](./LICENSE) file in this repository or visit the [BSL 1.1 website](https://mariadb.com/bsl11/).