import { useState, useEffect, useRef } from 'react';

export function useVoiceInput(onComplete: (text: string) => void) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognition = useRef<any>(null);
  const silenceTimer = useRef<number | null>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = true;
      recognition.current.interimResults = true;

      recognition.current.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(currentTranscript);
        
        if (silenceTimer.current) clearTimeout(silenceTimer.current);
        silenceTimer.current = window.setTimeout(() => {
          stopListening(currentTranscript);
        }, 2000);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
    
    return () => {
      if (silenceTimer.current) clearTimeout(silenceTimer.current);
      if (recognition.current) recognition.current.stop();
    };
  }, []);

  const startListening = () => {
    setTranscript('');
    setIsListening(true);
    recognition.current?.start();
  };

  const stopListening = (finalText: string = transcript) => {
    setIsListening(false);
    recognition.current?.stop();
    if (finalText.trim()) {
      onComplete(finalText.trim());
    }
  };

  const toggle = () => {
    if (isListening) stopListening();
    else startListening();
  };

  return { isListening, transcript, toggle, supported: !!recognition.current };
}
