export const config = { runtime: 'edge' };

const userAgents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
];

export default async function handler(request) {
  const url = new URL(request.url);
  const targetUrl = url.searchParams.get('url');
  if (!targetUrl) return new Response('Falta ?url=', { status: 400 });

  const ua = userAgents[Math.floor(Math.random() * userAgents.length)];

  // Paso 1: Calentar sesión
  const homeResponse = await fetch("https://www.mercadolibre.com.ar/", {
    headers: { 'User-Agent': ua }
  });
  const cookies = homeResponse.headers.get('set-cookie') || '';

  // Paso 2: Petición real con headers nivel navegador
  const modifiedRequest = new Request(targetUrl, {
    headers: {
      'User-Agent': ua,
      'Cookie': cookies,
      'Referer': 'https://www.mercadolibre.com.ar/',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
      'Accept-Encoding': 'gzip, deflate, br',
      'Priority': 'u=0, i',
      'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand)";v="24", "Google Chrome";v="122"',
      'Sec-Ch-Ua-Mobile': '?0',
      'Sec-Ch-Ua-Platform': '"Windows"',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1'
    }
  });

  try {
    const response = await fetch(modifiedRequest);
    const text = await response.text();

    if (text.includes('suspicious_traffic') || text.includes('account-verification')) {
      return new Response('BLOQUEO_DETECTADO', { status: 403 });
    }

    return new Response(text, {
      status: response.status,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  } catch (e) {
    return new Response('Error: ' + e.message, { status: 500 });
  }
}
