import React from 'react';
import { useNotification } from '../contexts/NotificationContext';

export default function Notification() {
  const { toasts, remove } = useNotification();

  if (!toasts.length) return null;

  return (
    <div className="toasts">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`} onClick={() => remove(t.id)}>
          {t.message}
        </div>
      ))}
    </div>
  );
}
