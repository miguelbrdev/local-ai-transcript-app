import { FileText, Sparkles, MessageCircle } from 'lucide-react';
import styles from './TranscriptionResults.module.css';
import type { TranscriptionResultsProps } from '../types';
import { TextBox } from './TextBox';
import { Box } from './Box';
import { DialogueView } from './DialogueView';

export function TranscriptionResults({
  rawText,
  cleanedText,
  dialogue,
  useLLM,
  isCopied,
  isCleaningWithLLM,
  isProcessing,
  isOriginalExpanded,
  onCopy,
  onToggleOriginalExpanded,
}: TranscriptionResultsProps) {
  if (!isProcessing && !rawText) {
    return null;
  }

  const displayText = useLLM && cleanedText ? cleanedText : rawText;

  return (
    <div className={styles.container}>
      <Box
        header="Original Transcription"
        icon={FileText}
        collapsible={true}
        isExpanded={isOriginalExpanded}
        onToggleExpanded={onToggleOriginalExpanded}
      >
        <TextBox
          mode="display"
          variant="default"
          value={rawText || ''}
          isLoading={isProcessing && !rawText}
          maxHeight="300px"
        />
      </Box>

      {useLLM && (cleanedText || isCleaningWithLLM) && (
        <Box header="Cleaned Transcription" icon={Sparkles}>
          <TextBox
            mode="display"
            variant="default"
            value={cleanedText || ''}
            isLoading={isCleaningWithLLM}
            showCopyButton={!!cleanedText}
            isCopied={isCopied}
            onCopy={() => cleanedText && onCopy(cleanedText)}
            maxHeight="300px"
          />
        </Box>
      )}

      {!useLLM && displayText && (
        <TextBox
          mode="display"
          variant="default"
          value={displayText}
          showCopyButton={true}
          isCopied={isCopied}
          onCopy={() => onCopy(displayText)}
          maxHeight="300px"
        />
      )}

      {useLLM && (cleanedText || isCleaningWithLLM) && (
        <Box header="Dialogue" icon={MessageCircle}>
          <DialogueView dialogue={dialogue} isProcessing={isCleaningWithLLM} />
        </Box>
      )}
    </div>
  );
}
