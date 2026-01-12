// Sound utilities for POS interactions

// Click sound as base64 (short click sound)
const CLICK_SOUND_URL = 'data:audio/wav;base64,UklGRl4FAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YToFAAB/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f3t7e3t7e3t7e3t7e3t7f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f4GBgYGBgYGBgYGBgYKCgoKDg4ODg4ODg4ODg4ODg4ODg4OCgoKCgoKCgoKCgoKBgYGBgYGBgYGBgYGBgYCAgICAgICAgICAgICAgICAgH9/f39/f39/f39/f39/f39/f39/f39/f39/f39+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fX19fX19fX19fX19fX19fX19fX19fX19fX19fXx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fH19fX19fX19fX19fX19fX19fX19fX19fX19fX5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5/f39/f39/f39/f39/f39/f39/f39/f39/gICAgICAgICAgICAgICAgICAgYGBgYGBgYGBgYGBgYGBgYGCgoKCgoKCgoKCgoKCgoKCgoKDg4ODg4ODg4ODg4ODg4ODhISEhISEhISEhISEhISEhISEhISEhISEhISEhIODg4ODg4ODg4ODg4ODg4OCgoKCgoKCgoKCgoKCgoKBgYGBgYGBgYGBgYGBgYGAgICAgICAgICAgICAgIB/f39/f39/f39/f39/fn5+fn5+fn5+fn5+fn19fX19fX19fX19fX19fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx9fX19fX19fX19fX19fX19fn5+fn5+fn5+fn5+fn5/f39/f39/f39/f39/f39/gICAgICAgICAgICAgICAgYGBgYGBgYGBgYGBgYKCgoKCgoKCgoKCgoKCg4ODg4ODg4ODg4ODg4OEhISEhISEhISEhISEhISFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWEhISEhISEhISEhISEhISEhISEhIODg4ODg4ODg4ODg4OCgoKCgoKCgoKCgoKCgYGBgYGBgYGBgYGBgYCAgICAgICAgICAgIB/f39/f39/f39/f39/fn5+fn5+fn5+fn5+fX19fX19fX19fX19fX18fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx9fX19fX19fX19fX19fX1+fn5+fn5+fn5+fn5+fn9/f39/f39/f39/f39/f4CAgICAgICAgICAgICAgYGBgYGBgYGBgYGBgYKCgoKCgoKCgoKCgoKCg4ODg4ODg4ODg4ODg4OEhISEhISEhISEhISEhIWFhYWFhYWFhYWFhYWFhYaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhYWFhYWFhYWFhYWFhYWFhYWFhYSEhISEhISEhISEhISDg4ODg4ODg4ODg4ODgoKCgoKCgoKCgoKCgoGBgYGBgYGBgYGBgYGAgICAgICAgICAgICAf39/f39/f39/f39/f35+fn5+fn5+fn5+fn19fX19fX19fX19fX19fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fX19fX19fX19fX19fX1+fn5+fn5+fn5+fn5+fn9/f39/f39/f39/f39/gICAgICAgICAgICAgICAgYGBgYGBgYGBgYGBgYKCgoKCgoKCgoKCgoKCg4ODg4ODg4ODg4ODg4Q=';

let audioContext = null;
let clickBuffer = null;

// Initialize audio context
const initAudio = async () => {
  if (audioContext) return;
  
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Decode the click sound
    const response = await fetch(CLICK_SOUND_URL);
    const arrayBuffer = await response.arrayBuffer();
    clickBuffer = await audioContext.decodeAudioData(arrayBuffer);
  } catch (error) {
    console.warn('Audio initialization failed:', error);
  }
};

/**
 * Play click sound effect
 */
export const playClick = async () => {
  try {
    // Initialize on first use (browser requires user interaction)
    if (!audioContext) {
      await initAudio();
    }
    
    if (!audioContext || !clickBuffer) {
      // Fallback: create simple beep
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05);
      
      oscillator.start(ctx.currentTime);
      oscillator.stop(ctx.currentTime + 0.05);
      
      return;
    }
    
    // Resume context if suspended
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }
    
    // Play the sound
    const source = audioContext.createBufferSource();
    const gainNode = audioContext.createGain();
    
    source.buffer = clickBuffer;
    gainNode.gain.value = 0.3;
    
    source.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    source.start(0);
  } catch (error) {
    console.warn('Sound playback failed:', error);
  }
};

/**
 * Play success sound
 */
export const playSuccess = () => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    oscillator.frequency.value = 880;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
    
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.2);
  } catch (error) {
    console.warn('Sound playback failed:', error);
  }
};

/**
 * Play error sound
 */
export const playError = () => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    oscillator.frequency.value = 200;
    oscillator.type = 'sawtooth';
    
    gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
    
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.15);
  } catch (error) {
    console.warn('Sound playback failed:', error);
  }
};

export default {
  playClick,
  playSuccess,
  playError,
};
