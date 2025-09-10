/**
 * Audio API Mocks for Testing
 * Comprehensive mocks for Web Audio API, MediaRecorder, and getUserMedia
 */

import { vi } from 'vitest';

/**
 * Mock AudioContext implementation
 */
export class MockAudioContext implements AudioContext {
  baseLatency: number = 0.01;
  outputLatency: number = 0.02;
  sampleRate: number = 24000;
  currentTime: number = 0;
  listener: AudioListener = {} as AudioListener;
  state: AudioContextState = 'running';
  audioWorklet: AudioWorklet = new MockAudioWorklet() as any;
  destination: AudioDestinationNode = new MockAudioDestinationNode() as any;
  
  // Event handlers
  onstatechange: ((this: BaseAudioContext, ev: Event) => any) | null = null;

  // Mock implementations
  close = vi.fn().mockResolvedValue(undefined);
  suspend = vi.fn().mockResolvedValue(undefined);
  resume = vi.fn().mockResolvedValue(undefined);
  
  createAnalyser = vi.fn(() => new MockAnalyserNode() as any);
  createBiquadFilter = vi.fn(() => ({} as BiquadFilterNode));
  createBuffer = vi.fn((channels: number, length: number, sampleRate: number) => 
    new MockAudioBuffer(channels, length, sampleRate) as any
  );
  createBufferSource = vi.fn(() => new MockAudioBufferSourceNode() as any);
  createChannelMerger = vi.fn(() => ({} as ChannelMergerNode));
  createChannelSplitter = vi.fn(() => ({} as ChannelSplitterNode));
  createConstantSource = vi.fn(() => ({} as ConstantSourceNode));
  createConvolver = vi.fn(() => ({} as ConvolverNode));
  createDelay = vi.fn(() => ({} as DelayNode));
  createDynamicsCompressor = vi.fn(() => ({} as DynamicsCompressorNode));
  createGain = vi.fn(() => new MockGainNode() as any);
  createIIRFilter = vi.fn(() => ({} as IIRFilterNode));
  createMediaElementSource = vi.fn(() => ({} as MediaElementAudioSourceNode));
  createMediaStreamDestination = vi.fn(() => new MockMediaStreamAudioDestinationNode() as any);
  createMediaStreamSource = vi.fn((stream: MediaStream) => new MockMediaStreamAudioSourceNode(stream) as any);
  createMediaStreamTrackSource = vi.fn(() => ({} as MediaStreamTrackAudioSourceNode));
  createOscillator = vi.fn(() => ({} as OscillatorNode));
  createPanner = vi.fn(() => ({} as PannerNode));
  createPeriodicWave = vi.fn(() => ({} as PeriodicWave));
  createScriptProcessor = vi.fn((bufferSize?: number) => new MockScriptProcessorNode(bufferSize) as any);
  createStereoPanner = vi.fn(() => ({} as StereoPannerNode));
  createWaveShaper = vi.fn(() => ({} as WaveShaperNode));
  
  decodeAudioData = vi.fn().mockResolvedValue(new MockAudioBuffer(2, 44100, 44100));
  
  // EventTarget methods
  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn(() => true);
  
  // Additional required properties
  getOutputTimestamp(): AudioTimestamp {
    return {
      contextTime: this.currentTime,
      performanceTime: performance.now()
    };
  }
}

/**
 * Mock AudioWorklet implementation
 */
class MockAudioWorklet implements AudioWorklet {
  addModule = vi.fn().mockResolvedValue(undefined);
}

/**
 * Mock AudioBuffer implementation
 */
export class MockAudioBuffer implements AudioBuffer {
  readonly sampleRate: number;
  readonly length: number;
  readonly duration: number;
  readonly numberOfChannels: number;

  constructor(channels: number, length: number, sampleRate: number) {
    this.numberOfChannels = channels;
    this.length = length;
    this.sampleRate = sampleRate;
    this.duration = length / sampleRate;
  }

  getChannelData = vi.fn((channel: number) => new Float32Array(this.length));
  copyFromChannel = vi.fn();
  copyToChannel = vi.fn();
}

/**
 * Mock AudioNode base class
 */
class MockAudioNode {
  context: BaseAudioContext;
  numberOfInputs: number = 1;
  numberOfOutputs: number = 1;
  channelCount: number = 2;
  channelCountMode: ChannelCountMode = 'max';
  channelInterpretation: ChannelInterpretation = 'speakers';

  constructor(context?: BaseAudioContext) {
    this.context = context || new MockAudioContext() as any;
  }

  connect = vi.fn((destination: AudioNode | AudioParam) => destination);
  disconnect = vi.fn();
  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn(() => true);
}

/**
 * Mock GainNode implementation
 */
class MockGainNode extends MockAudioNode implements GainNode {
  gain: AudioParam = {
    value: 1,
    defaultValue: 1,
    minValue: -3.4028235e38,
    maxValue: 3.4028235e38,
    automationRate: 'a-rate' as AutomationRate,
    setValueAtTime: vi.fn(),
    linearRampToValueAtTime: vi.fn(),
    exponentialRampToValueAtTime: vi.fn(),
    setTargetAtTime: vi.fn(),
    setValueCurveAtTime: vi.fn(),
    cancelScheduledValues: vi.fn(),
    cancelAndHoldAtTime: vi.fn()
  } as AudioParam;
}

/**
 * Mock AnalyserNode implementation
 */
class MockAnalyserNode extends MockAudioNode implements AnalyserNode {
  fftSize: number = 2048;
  frequencyBinCount: number = 1024;
  minDecibels: number = -100;
  maxDecibels: number = -30;
  smoothingTimeConstant: number = 0.8;

  getByteFrequencyData = vi.fn((array: Uint8Array) => {
    array.fill(128);
  });
  getFloatFrequencyData = vi.fn((array: Float32Array) => {
    array.fill(0);
  });
  getByteTimeDomainData = vi.fn((array: Uint8Array) => {
    array.fill(128);
  });
  getFloatTimeDomainData = vi.fn((array: Float32Array) => {
    array.fill(0);
  });
}

/**
 * Mock MediaStreamAudioSourceNode implementation
 */
class MockMediaStreamAudioSourceNode extends MockAudioNode implements MediaStreamAudioSourceNode {
  mediaStream: MediaStream;

  constructor(stream: MediaStream) {
    super();
    this.mediaStream = stream;
  }
}

/**
 * Mock MediaStreamAudioDestinationNode implementation
 */
class MockMediaStreamAudioDestinationNode extends MockAudioNode implements MediaStreamAudioDestinationNode {
  stream: MediaStream = new MockMediaStream() as any;
}

/**
 * Mock AudioDestinationNode implementation
 */
class MockAudioDestinationNode extends MockAudioNode implements AudioDestinationNode {
  maxChannelCount: number = 2;
}

/**
 * Mock AudioBufferSourceNode implementation
 */
class MockAudioBufferSourceNode extends MockAudioNode implements AudioBufferSourceNode {
  buffer: AudioBuffer | null = null;
  detune: AudioParam = {} as AudioParam;
  loop: boolean = false;
  loopEnd: number = 0;
  loopStart: number = 0;
  playbackRate: AudioParam = {} as AudioParam;
  
  onended: ((this: AudioScheduledSourceNode, ev: Event) => any) | null = null;
  
  start = vi.fn();
  stop = vi.fn();
}

/**
 * Mock ScriptProcessorNode implementation
 */
class MockScriptProcessorNode extends MockAudioNode implements ScriptProcessorNode {
  bufferSize: number;
  onaudioprocess: ((this: ScriptProcessorNode, ev: AudioProcessingEvent) => any) | null = null;

  constructor(bufferSize: number = 4096) {
    super();
    this.bufferSize = bufferSize;
  }

  // Simulate audio processing
  simulateAudioProcess(inputBuffer?: AudioBuffer, outputBuffer?: AudioBuffer): void {
    if (this.onaudioprocess) {
      const event = {
        inputBuffer: inputBuffer || new MockAudioBuffer(2, this.bufferSize, 24000),
        outputBuffer: outputBuffer || new MockAudioBuffer(2, this.bufferSize, 24000),
        playbackTime: 0
      } as AudioProcessingEvent;
      this.onaudioprocess.call(this, event);
    }
  }
}

/**
 * Mock MediaStream implementation
 */
export class MockMediaStream implements MediaStream {
  id: string = `stream_${Math.random().toString(36).substr(2, 9)}`;
  active: boolean = true;
  onaddtrack: ((this: MediaStream, ev: MediaStreamTrackEvent) => any) | null = null;
  onremovetrack: ((this: MediaStream, ev: MediaStreamTrackEvent) => any) | null = null;

  private tracks: MediaStreamTrack[] = [];

  constructor(tracks?: MediaStreamTrack[]) {
    if (tracks) {
      this.tracks = [...tracks];
    } else {
      // Create a default audio track
      this.tracks = [new MockMediaStreamTrack('audio') as any];
    }
  }

  getTracks(): MediaStreamTrack[] {
    return [...this.tracks];
  }

  getAudioTracks(): MediaStreamTrack[] {
    return this.tracks.filter(track => track.kind === 'audio');
  }

  getVideoTracks(): MediaStreamTrack[] {
    return this.tracks.filter(track => track.kind === 'video');
  }

  getTrackById(id: string): MediaStreamTrack | null {
    return this.tracks.find(track => track.id === id) || null;
  }

  addTrack(track: MediaStreamTrack): void {
    this.tracks.push(track);
  }

  removeTrack(track: MediaStreamTrack): void {
    const index = this.tracks.indexOf(track);
    if (index > -1) {
      this.tracks.splice(index, 1);
    }
  }

  clone(): MediaStream {
    return new MockMediaStream(this.tracks.map(track => track.clone())) as any;
  }

  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn(() => true);
}

/**
 * Mock MediaStreamTrack implementation
 */
export class MockMediaStreamTrack implements MediaStreamTrack {
  id: string = `track_${Math.random().toString(36).substr(2, 9)}`;
  kind: string;
  label: string = '';
  enabled: boolean = true;
  muted: boolean = false;
  readyState: MediaStreamTrackState = 'live';
  contentHint: string = '';
  isolated: boolean = false;

  onended: ((this: MediaStreamTrack, ev: Event) => any) | null = null;
  onmute: ((this: MediaStreamTrack, ev: Event) => any) | null = null;
  onunmute: ((this: MediaStreamTrack, ev: Event) => any) | null = null;

  constructor(kind: 'audio' | 'video' = 'audio') {
    this.kind = kind;
  }

  stop = vi.fn(() => {
    this.readyState = 'ended';
    if (this.onended) {
      this.onended(new Event('ended'));
    }
  });

  clone(): MediaStreamTrack {
    return new MockMediaStreamTrack(this.kind as 'audio' | 'video') as any;
  }

  getCapabilities(): MediaTrackCapabilities {
    return {};
  }

  getConstraints(): MediaTrackConstraints {
    return {};
  }

  getSettings(): MediaTrackSettings {
    return {
      deviceId: 'default',
      groupId: 'default',
      aspectRatio: 1,
      facingMode: 'user',
      frameRate: 30,
      height: 480,
      width: 640
    };
  }

  applyConstraints = vi.fn().mockResolvedValue(undefined);
  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn(() => true);
}

/**
 * Mock MediaRecorder implementation
 */
export class MockMediaRecorder implements MediaRecorder {
  stream: MediaStream;
  mimeType: string = 'audio/webm';
  state: RecordingState = 'inactive';
  videoBitsPerSecond: number = 0;
  audioBitsPerSecond: number = 128000;

  ondataavailable: ((this: MediaRecorder, ev: BlobEvent) => any) | null = null;
  onerror: ((this: MediaRecorder, ev: Event) => any) | null = null;
  onpause: ((this: MediaRecorder, ev: Event) => any) | null = null;
  onresume: ((this: MediaRecorder, ev: Event) => any) | null = null;
  onstart: ((this: MediaRecorder, ev: Event) => any) | null = null;
  onstop: ((this: MediaRecorder, ev: Event) => any) | null = null;

  private chunks: Blob[] = [];
  private recordingInterval: NodeJS.Timeout | null = null;

  constructor(stream: MediaStream, options?: MediaRecorderOptions) {
    this.stream = stream;
    if (options?.mimeType) {
      this.mimeType = options.mimeType;
    }
  }

  static isTypeSupported(mimeType: string): boolean {
    return ['audio/webm', 'audio/ogg', 'audio/wav'].includes(mimeType);
  }

  start = vi.fn((timeslice?: number) => {
    this.state = 'recording';
    if (this.onstart) {
      this.onstart(new Event('start'));
    }

    // Simulate data available events
    if (timeslice) {
      this.recordingInterval = setInterval(() => {
        this.simulateDataAvailable();
      }, timeslice);
    }
  });

  stop = vi.fn(() => {
    if (this.recordingInterval) {
      clearInterval(this.recordingInterval);
      this.recordingInterval = null;
    }

    this.state = 'inactive';
    this.simulateDataAvailable();
    
    if (this.onstop) {
      this.onstop(new Event('stop'));
    }
  });

  pause = vi.fn(() => {
    this.state = 'paused';
    if (this.onpause) {
      this.onpause(new Event('pause'));
    }
  });

  resume = vi.fn(() => {
    this.state = 'recording';
    if (this.onresume) {
      this.onresume(new Event('resume'));
    }
  });

  requestData = vi.fn(() => {
    this.simulateDataAvailable();
  });

  private simulateDataAvailable(): void {
    if (this.ondataavailable) {
      const blob = new Blob([new ArrayBuffer(1024)], { type: this.mimeType });
      const event = new BlobEvent('dataavailable', { data: blob });
      this.ondataavailable(event);
      this.chunks.push(blob);
    }
  }

  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn(() => true);
}

/**
 * Mock getUserMedia implementation
 */
export function mockGetUserMedia(): {
  stream: MockMediaStream;
  restore: () => void;
} {
  const stream = new MockMediaStream();
  const originalGetUserMedia = navigator.mediaDevices?.getUserMedia;

  navigator.mediaDevices = {
    ...navigator.mediaDevices,
    getUserMedia: vi.fn().mockResolvedValue(stream)
  } as any;

  return {
    stream,
    restore: () => {
      if (originalGetUserMedia) {
        navigator.mediaDevices.getUserMedia = originalGetUserMedia;
      }
    }
  };
}

/**
 * Setup all audio mocks for testing
 */
export function setupAudioMocks(): {
  audioContext: MockAudioContext;
  mediaRecorder: typeof MockMediaRecorder;
  getUserMedia: ReturnType<typeof mockGetUserMedia>;
  cleanup: () => void;
} {
  const audioContext = new MockAudioContext();
  const getUserMedia = mockGetUserMedia();

  // Mock global AudioContext
  (global as any).AudioContext = MockAudioContext;
  (global as any).webkitAudioContext = MockAudioContext;
  
  // Mock MediaRecorder
  (global as any).MediaRecorder = MockMediaRecorder;

  // Mock BlobEvent if not available
  if (typeof BlobEvent === 'undefined') {
    (global as any).BlobEvent = class BlobEvent extends Event {
      data: Blob;
      constructor(type: string, init: { data: Blob }) {
        super(type);
        this.data = init.data;
      }
    };
  }

  return {
    audioContext,
    mediaRecorder: MockMediaRecorder,
    getUserMedia,
    cleanup: () => {
      getUserMedia.restore();
      delete (global as any).AudioContext;
      delete (global as any).webkitAudioContext;
      delete (global as any).MediaRecorder;
    }
  };
}