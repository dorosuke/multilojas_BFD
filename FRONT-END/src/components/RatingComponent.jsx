import React from 'react';

export default function RatingComponent({ value = 0, onChange }) {
  const stars = [1,2,3,4,5];
  return (
    <div className="rating">
      {stars.map(s => (
        <button key={s} onClick={() => onChange?.(s)} className={s <= value ? 'on' : ''}>{s <= value ? '★' : '☆'}</button>
      ))}
    </div>
  );
}
