import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AudioService {
  private audioContext: AudioContext | null = null;
  private audioBuffer: AudioBuffer | null = null;
  private sourceNode: AudioBufferSourceNode | null = null;
  
  isPlaying = signal(false);

  private async initAudioContext() {
    if (this.audioContext) {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }
      return;
    }
    
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    } catch (e) {
      console.error('Web Audio API is not supported in this browser');
    }
  }

  async loadAudio(url: string): Promise<void> {
    await this.initAudioContext();
    if (!this.audioContext) return;

    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
    } catch (error) {
      console.error('Error loading or decoding audio file:', error);
    }
  }

  play(loop = true) {
    if (!this.audioContext || !this.audioBuffer) {
        console.warn('Audio not loaded yet.');
        return;
    }
    
    // Ensure context is running
    this.audioContext.resume();

    if (this.sourceNode) {
        this.stop();
    }

    this.sourceNode = this.audioContext.createBufferSource();
    this.sourceNode.buffer = this.audioBuffer;
    this.sourceNode.loop = loop;
    this.sourceNode.connect(this.audioContext.destination);
    this.sourceNode.start(0);
    this.isPlaying.set(true);
  }

  stop() {
    if (this.sourceNode) {
      this.sourceNode.stop();
      this.sourceNode.disconnect();
      this.sourceNode = null;
      this.isPlaying.set(false);
    }
  }

  async togglePlay(loop = true) {
    await this.initAudioContext();
    if (this.isPlaying()) {
      this.stop();
    } else {
      if (this.audioBuffer) {
        this.play(loop);
      } else {
        console.warn('Cannot play, audio not loaded.');
      }
    }
  }
}
