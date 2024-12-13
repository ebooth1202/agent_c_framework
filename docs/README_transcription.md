# Real-time Transcription and Speech Input

The `RealTimeTranscriber` class provides a high level interface of the Speechmatics speech transcription API. This is an adaptation of the code behind the Centric Real-time Transcription app for meeting transcripts.  While it can still be used for multi-speaker transcripts (by setting `diarization='speaker'` in kwargs or by setting the`STT_DIARIZATION` env variable to `speaker`), this version has been refactored to also be able to provide speech input to applications.  (I needed to work through that to help the app devs on the next phase of Ticco)

It runs in a background thread and by default operates in a mode where it must be toggled on for each interaction.  The reference app uses a hot-key to enable the input and relies on the transcriber to stop the transcription when the user stops speaking. 

## Using the transcriber

The `start_background_transcription` helper method will spin up a transcriber in the background.  It accepts kwargs, two of which are required:

- `message_queue` - A queue.Queue that the transcriber can use to send transcripts.
- `active_event` - A threading.Event that is used to enable / disable transcription.

This will create a transcriber thread you can control with a flag and receive events from using the defaults for all other params (see below)

```python
stt_active_event = threading.Event()
transcription_thread = start_background_transcription(message_queue=message_queue, active_event=stt_active_event)
```

Events come into the queue as a dict with a `type` field that is one of `final`, `partial`, or `pause`. The final and partial events have an additional `transcript` field that varies between them:

- The `transcript` field in a `partial` is a single `PartialTranscriptLine` model which has a `content` field.
- The `transcript` field in a `final` is an array of `TranscriptLine` models, which contain  `content` and `speaker` fields.  If diarization is not set to `speaker` this field will always be `UU` for unknown.

Transcription can be turned on or off with the event:

- Calling `stt_active_event.set()` will start sending audio data to Speechmatics for transcription.
- Calling `stt_active_event.clear()` will stop sending audio data to Speechmatics for transcription, IMMEDIATELY.  This can cut off a transcript before all the audio has been sent to the API. (That's why toggle mode exists)

### Additional options

- `sm_api_key` (str): The Speechmatics API key.
- `enhance_accuracy` (bool): Flag indicating whether to use enhanced accuracy transcription.
- `language` (str): The transcription language. Default is `en` see the Speechmatics docs for options.
- `device_index` (int): Audio device index. Default is `-1` (System default microphone will be used)
- `audio_chunk_size` (int):  The size of each chunk of audio sent to Speechmatics.  Default is `1024`.
- `partials` (bool): Flag indicating whether to allow partial transcripts. Default is `False`
- `sm_url` (str): Speechmatics connection url.
- `max_delay` (int): maximum delay in seconds between receiving input audio and returning final transcription results. Defaults to `3` The Speechmatics default is 10. The minimum and maximum values are 2 and 20.
- `dictionary` (str): Path to a custom dictionary. See the Speechmatics docs.
- `diarization` (str): Speaker diarization mode.
- `toggle_mode` (bool): When set to true, the transcriber will disable itself after a short pause in audio input.  Default is `True`.