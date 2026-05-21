import { MessageSquare, User } from 'lucide-react';
import styles from './DialogueView.module.css';
import type { DialogueEntry } from '../types';

interface DialogueViewProps {
  dialogue: DialogueEntry[] | null;
  isProcessing: boolean;
}

export function DialogueView({ dialogue, isProcessing }: DialogueViewProps) {
  if (isProcessing) {
    return (
      <div className={styles.empty}>
        <p>Analizando la conversación...</p>
      </div>
    );
  }

  if (!dialogue || dialogue.length === 0) {
    return (
      <div className={styles.empty}>
        <p>
          No se pudo separar el diálogo. El modelo de IA no identificó turnos de
          conversación.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {dialogue.map((entry, index) => (
        <div key={index} className={`${styles.bubble} ${styles[entry.role]}`}>
          <div className={styles.bubbleHeader}>
            {entry.role === 'interviewer' ? (
              <MessageSquare className={styles.icon} />
            ) : (
              <User className={styles.icon} />
            )}
            <span className={styles.roleLabel}>
              {entry.role === 'interviewer' ? 'Entrevistador' : 'Candidato'}
            </span>
          </div>
          <p className={styles.bubbleText}>{entry.text}</p>
        </div>
      ))}
    </div>
  );
}
