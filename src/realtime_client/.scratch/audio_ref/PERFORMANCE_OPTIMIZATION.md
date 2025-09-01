# Audio System Performance Optimization Guide

## Overview

The Virtual Joe audio system is designed for high performance with binary WebSocket transmission, efficient resource management, and optimized audio processing. This guide covers best practices and optimization techniques for maximum performance.

## Core Performance Principles

### 1. Binary-First Architecture
- **Zero Base64 Encoding**: Direct ArrayBuffer transmission eliminates ~33% overhead
- **WebSocket Binary Frames**: Native binary support for minimal processing
- **Memory Efficiency**: ArrayBuffer sharing reduces garbage collection pressure

### 2. Singleton Pattern Benefits
- **Resource Pooling**: Single AudioContext, MediaStream, and WebSocket connections
- **State Consistency**: Centralized state management prevents conflicts
- **Memory Conservation**: Shared instances reduce memory footprint

### 3. Turn-Based Optimization
- **Bandwidth Conservation**: Audio suppressed during agent turns
- **Processing Efficiency**: Reduces unnecessary audio processing
- **Battery Life**: Lower CPU usage on mobile devices

## Optimization Strategies

### Audio Processing Optimization

#### 1. Optimal Chunk Configuration
```typescript
// Recommended audio chunk settings for different use cases
const audioConfigs = {
  // Low latency (real-time conversation)
  lowLatency: {
    chunkDurationMs: 50,        // 50ms chunks for quick response
    sampleRate: 16000,          // 16kHz for voice (adequate quality)
    bufferSize: 2,              // Minimal buffering
  },
  
  // Balanced (default recommended)
  balanced: {
    chunkDurationMs: 100,       // 100ms chunks (good balance)
    sampleRate: 16000,          // Standard voice quality
    bufferSize: 4,              // Moderate buffering
  },
  
  // High quality (music/high fidelity)
  highQuality: {
    chunkDurationMs: 200,       // Larger chunks for efficiency
    sampleRate: 44100,          // CD quality
    bufferSize: 8,              // More buffering for stability
  }
};

// Apply configuration based on use case
const audioService = AudioService.getInstance();
audioService.updateConfig(audioConfigs.balanced);
```

#### 2. AudioWorklet Optimization
```typescript
// Optimized AudioWorklet processor (audio-processor.js)
class OptimizedAudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    // Pre-allocate buffers to avoid runtime allocation
    this.buffer = new Float32Array(1600); // 100ms at 16kHz
    this.bufferIndex = 0;
  }
  
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || !input[0]) return true;
    
    const inputData = input[0];
    
    // Optimized audio level calculation (RMS)
    let sum = 0;
    for (let i = 0; i < inputData.length; i++) {
      const sample = inputData[i];
      this.buffer[this.bufferIndex + i] = sample;
      sum += sample * sample;
    }
    
    this.bufferIndex += inputData.length;
    
    // Send chunk when buffer is full
    if (this.bufferIndex >= this.buffer.length) {
      const audioLevel = Math.sqrt(sum / inputData.length);
      
      // Use transferable ArrayBuffer for zero-copy
      const chunkBuffer = this.buffer.slice().buffer;
      this.port.postMessage({
        type: 'audioChunk',
        audioData: chunkBuffer,
        audioLevel,
        timestamp: Date.now()
      }, [chunkBuffer]); // Transfer ownership
      
      this.bufferIndex = 0;
    }
    
    return true;
  }
}
```

### Network Optimization

#### 1. WebSocket Connection Management
```typescript
class OptimizedAgentCClient {
  constructor() {
    // Connection pooling and reuse
    this.connectionPool = new Map();
    this.maxConnectionAge = 5 * 60 * 1000; // 5 minutes
  }
  
  async connect(endpoint: string): Promise<WebSocket> {
    // Reuse existing connection if available and healthy
    const existing = this.connectionPool.get(endpoint);
    if (existing && existing.readyState === WebSocket.OPEN) {
      const age = Date.now() - existing.createdAt;
      if (age < this.maxConnectionAge) {
        return existing.websocket;
      }
    }
    
    // Create new optimized connection
    const websocket = new WebSocket(endpoint);
    
    // Optimize WebSocket settings
    websocket.binaryType = 'arraybuffer'; // Efficient binary handling
    
    // Connection management
    const connection = {
      websocket,
      createdAt: Date.now(),
      messagesReceived: 0,
      messagesSent: 0
    };
    
    this.connectionPool.set(endpoint, connection);
    return websocket;
  }
  
  // Optimized binary transmission
  sendAudioChunk(audioBuffer: ArrayBuffer): void {
    if (this.websocket.readyState === WebSocket.OPEN) {
      // Direct ArrayBuffer send (zero-copy when possible)
      this.websocket.send(audioBuffer);
      
      // Update metrics
      this.metrics.bytesSent += audioBuffer.byteLength;
      this.metrics.chunksSent++;
    }
  }
}
```

#### 2. Bandwidth Monitoring and Adaptation
```typescript
class BandwidthManager {
  constructor() {
    this.stats = {
      bytesSent: 0,
      startTime: Date.now(),
      chunksSent: 0,
      errors: 0
    };
  }
  
  // Calculate current bandwidth usage
  getCurrentBandwidth(): number {
    const elapsed = (Date.now() - this.stats.startTime) / 1000;
    return (this.stats.bytesSent * 8) / elapsed; // bits per second
  }
  
  // Adaptive quality based on network performance
  adaptQuality(): AudioConfig {
    const bandwidth = this.getCurrentBandwidth();
    const errorRate = this.stats.errors / this.stats.chunksSent;
    
    if (bandwidth < 64000 || errorRate > 0.1) { // < 64kbps or high errors
      // Reduce quality for poor connections
      return {
        chunkDurationMs: 200,     // Larger chunks
        sampleRate: 16000,        // Standard rate
        compression: true         // Enable compression
      };
    } else if (bandwidth > 256000) { // > 256kbps
      // High quality for good connections  
      return {
        chunkDurationMs: 50,      // Low latency
        sampleRate: 16000,        // Voice optimized
        compression: false        // No compression overhead
      };
    }
    
    // Balanced configuration
    return {
      chunkDurationMs: 100,
      sampleRate: 16000,
      compression: false
    };
  }
}
```

### Memory Optimization

#### 1. Efficient Buffer Management
```typescript
class AudioBufferPool {
  private bufferPool: ArrayBuffer[] = [];
  private readonly POOL_SIZE = 20;
  private readonly BUFFER_SIZE = 3200; // 100ms at 16kHz
  
  constructor() {
    // Pre-allocate buffers
    for (let i = 0; i < this.POOL_SIZE; i++) {
      this.bufferPool.push(new ArrayBuffer(this.BUFFER_SIZE));
    }
  }
  
  acquire(): ArrayBuffer {
    // Reuse pooled buffer if available
    if (this.bufferPool.length > 0) {
      return this.bufferPool.pop()!;
    }
    
    // Create new buffer if pool empty
    return new ArrayBuffer(this.BUFFER_SIZE);
  }
  
  release(buffer: ArrayBuffer): void {
    // Return buffer to pool if space available
    if (this.bufferPool.length < this.POOL_SIZE) {
      this.bufferPool.push(buffer);
    }
    // Otherwise let GC handle it
  }
}

// Usage in AudioService
class AudioService {
  private bufferPool = new AudioBufferPool();
  
  private processAudioChunk(audioData: Float32Array): void {
    const buffer = this.bufferPool.acquire();
    const view = new DataView(buffer);
    
    // Convert audio data to PCM16
    for (let i = 0; i < audioData.length; i++) {
      const sample = Math.max(-1, Math.min(1, audioData[i]));
      const int16 = sample < 0 ? sample * 32768 : sample * 32767;
      view.setInt16(i * 2, int16, true);
    }
    
    // Send audio chunk
    this.emitAudioChunk({
      content: buffer,
      audioLevel: this.calculateAudioLevel(audioData),
      timestamp: Date.now()
    });
    
    // Don't release buffer here - let receiver handle it
  }
}
```

#### 2. Memory Leak Prevention
```typescript
class MemoryManager {
  private intervals: Set<NodeJS.Timeout> = new Set();
  private eventListeners: Map<EventTarget, Map<string, Function>> = new Map();
  
  // Managed interval creation
  setInterval(callback: Function, ms: number): NodeJS.Timeout {
    const interval = setInterval(callback, ms);
    this.intervals.add(interval);
    return interval;
  }
  
  // Managed event listener registration
  addEventListener(target: EventTarget, event: string, handler: Function): void {
    target.addEventListener(event, handler as EventListener);
    
    if (!this.eventListeners.has(target)) {
      this.eventListeners.set(target, new Map());
    }
    this.eventListeners.get(target)!.set(event, handler);
  }
  
  // Cleanup all managed resources
  cleanup(): void {
    // Clear all intervals
    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals.clear();
    
    // Remove all event listeners
    this.eventListeners.forEach((listeners, target) => {
      listeners.forEach((handler, event) => {
        target.removeEventListener(event, handler as EventListener);
      });
    });
    this.eventListeners.clear();
  }
}

// Use in services
class AudioService {
  private memoryManager = new MemoryManager();
  
  constructor() {
    // Managed resource setup
    this.memoryManager.setInterval(() => {
      this.performMaintenanceTasks();
    }, 30000); // Every 30 seconds
  }
  
  private performMaintenanceTasks(): void {
    // Clean up old audio buffers
    this.cleanupOldBuffers();
    
    // Check memory usage
    if ((performance as any).memory) {
      const memInfo = (performance as any).memory;
      if (memInfo.usedJSHeapSize > memInfo.jsHeapSizeLimit * 0.8) {
        console.warn('High memory usage detected, triggering cleanup');
        this.forceCleanup();
      }
    }
  }
  
  destroy(): void {
    this.memoryManager.cleanup();
  }
}
```

### CPU Optimization

#### 1. Efficient Audio Processing
```typescript
// Optimized audio level calculation using SIMD-like operations
function calculateAudioLevelOptimized(samples: Float32Array): number {
  let sum = 0;
  let i = 0;
  
  // Process 4 samples at a time (manual unrolling)
  const length4 = samples.length - (samples.length % 4);
  for (i = 0; i < length4; i += 4) {
    const s1 = samples[i];
    const s2 = samples[i + 1];
    const s3 = samples[i + 2];
    const s4 = samples[i + 3];
    sum += s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4;
  }
  
  // Process remaining samples
  for (; i < samples.length; i++) {
    const s = samples[i];
    sum += s * s;
  }
  
  return Math.sqrt(sum / samples.length);
}

// Fast PCM16 conversion using typed arrays
function convertToPCM16Fast(floatData: Float32Array): ArrayBuffer {
  const buffer = new ArrayBuffer(floatData.length * 2);
  const int16View = new Int16Array(buffer);
  
  for (let i = 0; i < floatData.length; i++) {
    // Clamp and convert to int16 in one operation
    int16View[i] = Math.max(-32768, Math.min(32767, floatData[i] * 32767));
  }
  
  return buffer;
}
```

#### 2. Debounced UI Updates
```typescript
// Efficient UI updates for audio visualizations
function useOptimizedAudioVisualization() {
  const [audioLevel, setAudioLevel] = useState(0);
  const updateRef = useRef<NodeJS.Timeout>();
  
  const updateAudioLevel = useCallback((level: number) => {
    // Debounce UI updates to 60fps max
    if (updateRef.current) {
      clearTimeout(updateRef.current);
    }
    
    updateRef.current = setTimeout(() => {
      setAudioLevel(level);
    }, 16); // ~60fps
  }, []);
  
  return { audioLevel, updateAudioLevel };
}

// Optimized component rendering
const AudioLevelMeter = React.memo<AudioLevelMeterProps>(({ audioLevel }) => {
  // Memoize expensive calculations
  const barHeights = useMemo(() => {
    const bars = 20;
    const heights: number[] = [];
    
    for (let i = 0; i < bars; i++) {
      const threshold = i / bars;
      heights.push(audioLevel > threshold ? (audioLevel - threshold) * bars : 0);
    }
    
    return heights;
  }, [audioLevel]);
  
  return (
    <div className="audio-level-meter">
      {barHeights.map((height, i) => (
        <div
          key={i}
          className="bar"
          style={{ height: `${Math.min(100, height * 100)}%` }}
        />
      ))}
    </div>
  );
});
```

## Performance Monitoring

### 1. Real-time Performance Metrics
```typescript
class PerformanceMonitor {
  private metrics = {
    audioLatency: [] as number[],
    networkLatency: [] as number[],
    cpuUsage: [] as number[],
    memoryUsage: [] as number[],
    frameDrops: 0,
    totalFrames: 0
  };
  
  // Measure audio processing latency
  measureAudioLatency(startTime: number): void {
    const latency = performance.now() - startTime;
    this.metrics.audioLatency.push(latency);
    
    // Keep only recent measurements
    if (this.metrics.audioLatency.length > 100) {
      this.metrics.audioLatency.shift();
    }
  }
  
  // Monitor frame drops for UI performance
  measureFramePerformance(): void {
    let lastTime = performance.now();
    const targetFPS = 60;
    const targetInterval = 1000 / targetFPS;
    
    const measure = () => {
      const currentTime = performance.now();
      const interval = currentTime - lastTime;
      
      this.metrics.totalFrames++;
      
      if (interval > targetInterval * 1.5) {
        this.metrics.frameDrops++;
      }
      
      lastTime = currentTime;
      requestAnimationFrame(measure);
    };
    
    requestAnimationFrame(measure);
  }
  
  // Generate performance report
  getPerformanceReport(): PerformanceReport {
    const avgAudioLatency = this.metrics.audioLatency.reduce((a, b) => a + b, 0) / this.metrics.audioLatency.length;
    const frameDropRate = this.metrics.frameDrops / this.metrics.totalFrames;
    
    return {
      audioLatency: {
        average: avgAudioLatency,
        p95: this.percentile(this.metrics.audioLatency, 0.95),
        max: Math.max(...this.metrics.audioLatency)
      },
      framePerformance: {
        dropRate: frameDropRate,
        totalFrames: this.metrics.totalFrames,
        droppedFrames: this.metrics.frameDrops
      },
      recommendations: this.generateRecommendations(avgAudioLatency, frameDropRate)
    };
  }
  
  private generateRecommendations(latency: number, frameDropRate: number): string[] {
    const recommendations: string[] = [];
    
    if (latency > 100) {
      recommendations.push('Consider reducing audio chunk size for lower latency');
    }
    
    if (frameDropRate > 0.05) {
      recommendations.push('UI performance issues detected - reduce visualization complexity');
    }
    
    if (this.metrics.audioLatency.some(l => l > 500)) {
      recommendations.push('High audio latency spikes detected - check for blocking operations');
    }
    
    return recommendations;
  }
}
```

### 2. Performance Benchmarks
```typescript
// Benchmark different optimization strategies
class AudioBenchmark {
  async benchmarkAudioProcessing(): Promise<BenchmarkResults> {
    const testAudio = new Float32Array(1600); // 100ms at 16kHz
    for (let i = 0; i < testAudio.length; i++) {
      testAudio[i] = Math.sin(2 * Math.PI * 440 * i / 16000); // 440Hz tone
    }
    
    const results: BenchmarkResults = {};
    
    // Benchmark PCM16 conversion
    const pcmStart = performance.now();
    for (let i = 0; i < 1000; i++) {
      convertToPCM16Fast(testAudio);
    }
    results.pcmConversion = performance.now() - pcmStart;
    
    // Benchmark audio level calculation
    const levelStart = performance.now();
    for (let i = 0; i < 1000; i++) {
      calculateAudioLevelOptimized(testAudio);
    }
    results.audioLevel = performance.now() - levelStart;
    
    // Benchmark WebSocket sending
    const wsStart = performance.now();
    const buffer = convertToPCM16Fast(testAudio);
    for (let i = 0; i < 100; i++) {
      // Simulate WebSocket send without actual network
      const simulatedSend = () => buffer.slice();
      simulatedSend();
    }
    results.websocketSend = performance.now() - wsStart;
    
    return results;
  }
}
```

## Platform-Specific Optimizations

### Mobile Optimization
```typescript
// Mobile-specific optimizations
class MobileAudioOptimizer {
  constructor() {
    this.isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    this.isLowPowerDevice = navigator.hardwareConcurrency <= 4;
  }
  
  getOptimalConfig(): AudioConfig {
    if (this.isMobile) {
      return {
        chunkDurationMs: 200,        // Larger chunks for battery efficiency
        sampleRate: 16000,           // Standard voice quality
        enableEchoCancellation: true, // Important for mobile speakers
        enableNoiseSuppression: true, // Mobile environments are noisy
        processingInterval: 100,     // Reduce processing frequency
      };
    }
    
    return {
      chunkDurationMs: 100,
      sampleRate: 16000,
      enableEchoCancellation: true,
      enableNoiseSuppression: true,
      processingInterval: 50,
    };
  }
  
  // Battery usage optimization
  optimizeForBattery(): void {
    if (this.isMobile) {
      // Reduce UI update frequency
      this.setUpdateInterval(200); // 5fps instead of 60fps
      
      // Use lower quality visualizations
      this.enableLowPowerMode();
      
      // Reduce audio processing complexity
      this.setSimpleAudioProcessing();
    }
  }
}
```

### Desktop Optimization
```typescript
// Desktop-specific optimizations
class DesktopAudioOptimizer {
  constructor() {
    this.cpuCores = navigator.hardwareConcurrency || 4;
    this.memorySize = (navigator as any).deviceMemory || 4; // GB
  }
  
  getOptimalConfig(): AudioConfig {
    return {
      chunkDurationMs: 50,          // Low latency for desktop
      sampleRate: 16000,            // Voice optimized
      bufferSize: this.cpuCores >= 8 ? 2 : 4, // Smaller buffers for powerful CPUs
      enableAdvancedProcessing: this.cpuCores >= 8,
      useWebWorkers: this.cpuCores >= 4,
    };
  }
  
  // Utilize multiple cores for processing
  enableParallelProcessing(): void {
    if (this.cpuCores >= 4) {
      // Offload audio processing to Web Workers
      this.initializeAudioWorkers();
      
      // Use separate threads for visualization
      this.enableVisualizationWorker();
    }
  }
}
```

## Best Practices Summary

### 1. Configuration
- Use appropriate chunk sizes (50-200ms)
- Match sample rates to use case (16kHz for voice)
- Enable turn management to save bandwidth
- Configure buffers based on device capabilities

### 2. Resource Management
- Use singleton services for shared resources
- Implement proper cleanup in useEffect hooks
- Pool ArrayBuffers to reduce allocations
- Monitor memory usage and implement cleanup

### 3. Network Optimization
- Use binary WebSocket frames exclusively
- Implement connection pooling and reuse
- Monitor bandwidth and adapt quality
- Handle connection recovery gracefully

### 4. CPU Optimization
- Use efficient audio processing algorithms
- Debounce UI updates to reasonable rates
- Leverage Web Workers for heavy processing
- Profile and optimize critical paths

### 5. Mobile Considerations
- Use larger chunks for battery efficiency
- Reduce UI update frequencies on mobile
- Enable audio processing optimizations
- Consider device capabilities in configuration

The Virtual Joe audio system achieves excellent performance through these optimizations while maintaining clean, maintainable code architecture.