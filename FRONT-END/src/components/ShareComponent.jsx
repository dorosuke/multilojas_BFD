import React from 'react';
import { getShareUrl } from '../services/social';

export default function ShareComponent({ title, url }) {
  const platforms = ['facebook','twitter','whatsapp','linkedin','telegram'];
  return (
    <div className="share">
      {platforms.map(p => (
        <a key={p} href={getShareUrl(p, { title, url })} target="_blank" rel="noreferrer">{p}</a>
      ))}
    </div>
  );
}
