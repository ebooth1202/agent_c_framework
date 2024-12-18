import os
import asyncio
import argparse
from dotenv import load_dotenv

# Note: we load the env file here so that it's loaded when we start loading the libs that depend on API KEYs.   I'm looking at you Eleven Labs
load_dotenv(override=True)


# Ensure all our toolsets get registered
from agent_c_tools.tools import *  # noqa
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

    model: str = args.model
    backend: str = 'openai'
    if args.claude and args.model == 'gpt-4o':
        model = 'claude-3-sonnet-20240229'

    camera: int = args.camera
    if args.vision:

        if camera == -1:
            camera = int(os.environ.get('VIDEO_CAPTURE_DEVICE_NUM', 0))

    if args.claude:
        backend = 'claude'

    if args.voice:
        from agent_c.toolsets.voice_eleven_labs import VoiceTools  # noqa

    chat = GradioChat(user_id=args.userid, persona=args.persona, session_id=args.session, voice=args.voice,
                      model_name=model, allow_oi=args.oi, backend=backend,
                      camera_no=camera)
    asyncio.run(chat.run())


if __name__ == "__main__":
    main()