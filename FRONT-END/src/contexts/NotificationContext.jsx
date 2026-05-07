import React, { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const notify = useCallback((message, type = 'info', timeout = 5000) => {
    const id = Date.now() + Math.random();
    const toast = { id, message, type };
    setToasts(t => [toast, ...t]);
    if (timeout) setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), timeout);
    return id;
  }, []);

  const remove = useCallback(id => setToasts(t => t.filter(x => x.id !== id)), []);

  return (
    <NotificationContext.Provider value={{ toasts, notify, remove }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  return useContext(NotificationContext);
}
