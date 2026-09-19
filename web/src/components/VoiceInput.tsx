import { Mic, MicOff } from 'lucide-react';
import { clsx } from 'clsx';
import { useVoiceInput } from '../hooks/useVoiceInput';

export default function VoiceInput({ onSend }: { onSend: (text: string) => void }) {
  const { isListening, toggle, transcript, supported } = useVoiceInput((text) => {
    onSend(text);
  });

  if (!supported) return null;

  return (
    <div className="relative">
      <button 
        type="button"
        onClick={toggle}
        className={clsx(
          "p-3 rounded-full transition-all duration-300",
          isListening ? "bg-galaxy-accent text-white animate-pulse" : "bg-galaxy-800 text-gray-400 hover:text-white"
        )}
      >
        {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
      </button>
      {isListening && transcript && (
        <div className="absolute bottom-full mb-2 right-0 bg-galaxy-800 text-sm text-gray-200 p-2 rounded-lg whitespace-nowrap overflow-hidden text-ellipsis max-w-xs border border-galaxy-700">
          {transcript}
        </div>
      )}
    </div>
  );
}
