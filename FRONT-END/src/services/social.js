export function getShareUrl(platform, { title, url }) {
  const encoded = encodeURIComponent(url);
  const text = encodeURIComponent(title || '');
  switch (platform) {
    case 'facebook':
      return `https://www.facebook.com/sharer/sharer.php?u=${encoded}`;
    case 'twitter':
      return `https://twitter.com/intent/tweet?text=${text}&url=${encoded}`;
    case 'whatsapp':
      return `https://api.whatsapp.com/send?text=${text}%20${encoded}`;
    case 'linkedin':
      return `https://www.linkedin.com/shareArticle?mini=true&url=${encoded}&title=${text}`;
    case 'telegram':
      return `https://t.me/share/url?url=${encoded}&text=${text}`;
    default:
      return url;
  }
}
