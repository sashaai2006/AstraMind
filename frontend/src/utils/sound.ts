const createOscillator = (
  context: AudioContext,
  type: OscillatorType,
  frequency: number,
  duration: number,
  volume: number = 0.1
) => {
  const oscillator = context.createOscillator();
  const gainNode = context.createGain();

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, context.currentTime);
  
  gainNode.gain.setValueAtTime(volume, context.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + duration);

  oscillator.connect(gainNode);
  gainNode.connect(context.destination);

  oscillator.start();
  oscillator.stop(context.currentTime + duration);
};

class SoundManager {
  private context: AudioContext | null = null;

  private getContext() {
    if (!this.context) {
      this.context = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    if (this.context.state === 'suspended') {
      this.context.resume();
    }
    return this.context;
  }

  playHover() {
    try {
      const ctx = this.getContext();
      createOscillator(ctx, 'sine', 400, 0.05, 0.02);
    } catch (e) {
      // Ignore audio context errors (e.g. before user interaction)
    }
  }

  playClick() {
    try {
      const ctx = this.getContext();
      createOscillator(ctx, 'square', 200, 0.05, 0.05);
      setTimeout(() => createOscillator(ctx, 'square', 150, 0.05, 0.03), 50);
    } catch (e) {}
  }

  playSuccess() {
    try {
      const ctx = this.getContext();
      const now = ctx.currentTime;
      
      // Ascending arpeggio
      const notes = [440, 554.37, 659.25, 880]; // A4, C#5, E5, A5
      notes.forEach((freq, i) => {
        setTimeout(() => {
          createOscillator(ctx, 'sine', freq, 0.3, 0.1);
        }, i * 80);
      });
    } catch (e) {}
  }

  playMessage() {
    try {
      const ctx = this.getContext();
      // Data stream sound
      createOscillator(ctx, 'sawtooth', 800, 0.05, 0.03);
      setTimeout(() => createOscillator(ctx, 'sawtooth', 1200, 0.05, 0.03), 40);
    } catch (e) {}
  }
}

export const soundManager = new SoundManager();

