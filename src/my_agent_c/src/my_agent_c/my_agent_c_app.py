import os
import argparse
import asyncio

from dotenv import load_dotenv

from my_agent_c.tools.my_tool.tool import MyTool # noqa

# Uncomment the following lines to import all the tools from the various packages
#from agent_c_tools.tools import *  # noqa
#from agent_c_demo.tools import *  # noqa
#from agent_c_voice.tools import *  # noqa

from agent_c_reference_apps.ui.gradio_ui import GradioChat


def main():
    parser = argparse.ArgumentParser(description="CLI Chat Interface")
    parser.add_argument('--session', type=str, help='Existing session ID to use', default=None)
    parser.add_argument('--model', type=str, help='The model name to use', default="gpt-4o")
    parser.add_argument('--persona', type=str,
                        help='The bare name of a markdown file in the personas folder to use. e.g. --persona toolman',
                        default='default')
    parser.add_argument('--userid', type=str, help='The userid for the session',
                        default=os.environ.get("CLI_CHAT_USER_ID", "default"))
    parser.add_argument('--voice', action='store_true',
                        help='Enable text_iter to speech via ElevenLabs.  Requires ELEVEN_LABS_API_KEY be set.')
    parser.add_argument('--oi', action='store_true', help='Enable experimental Open Interpreter support')
    parser.add_argument('--vision', action='store_true', help='Enable vision support')
    parser.add_argument('--camera', type=int, default=-1,
                        help='What camera number to use for vision support.  Defaults to -1 which checks the env var, which defaults to 0.')
    parser.add_argument('--claude', action='store_true',
                        help='Use Claude as the agent instead of GPT-4-1106-preview.  This is experimental.')
    args = parser.parse_args()
    load_dotenv(override=True)

    backend: str = 'openai'
    camera: int = args.camera
    if args.vision:

        if camera == -1:
            camera = int(os.environ.get('VIDEO_CAPTURE_DEVICE_NUM', 0))

    if args.claude:
        backend = 'claude'


    chat = GradioChat(user_id=args.userid, persona=args.persona, session_id=args.session, voice=args.voice,
                      model_name=args.model, allow_oi=args.oi, backend=backend, vision=args.vision,
                      camera_no=camera)
    asyncio.run(chat.run())

if __name__ == "__main__":
    main()