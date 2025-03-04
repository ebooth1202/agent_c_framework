# Agent C Framework Dockerfiles 

**All commands assume you're int the root folder of the project.**

## Dev container:

Build: `docker build -t agent_c_framework -f dockerfiles\Dockerfile.dev .`

Run: `>docker run -it -p 7860:7860 --rm --env-file .env  agent_c_framework`

When you see the message about going to http://0.0.0 open http://127.0.0.1:7860/ in your browser.

- Note: you must have set up up your `.env` file
- **Important**: If you already have a `.env` file remove quotes around strings in it before running thing.

