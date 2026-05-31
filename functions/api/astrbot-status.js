export async function onRequestGet() {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Access-Control-Allow-Origin': '*',
  };

  try {
    const res = await fetch('https://db.mer3y.xyz/api/services', {
      headers: {
        'User-Agent': 'suzuran-status-check/1.0',
        'Accept': 'application/json',
      },
      cf: { cacheTtl: 0, cacheEverything: false },
    });

    if (!res.ok) {
      return new Response(JSON.stringify({
        status: 'unknown',
        error: `dashboard api http ${res.status}`,
      }), { status: 200, headers });
    }

    const data = await res.json();
    const docker = Array.isArray(data?.docker) ? data.docker : [];
    const astrbot = docker.find((item) => item?.name === 'astrbot');

    if (!astrbot) {
      return new Response(JSON.stringify({
        status: 'offline',
        error: 'astrbot container not found',
      }), { status: 200, headers });
    }

    const online = astrbot.status === 'online' || astrbot.raw_state === 'running';
    return new Response(JSON.stringify({
      status: online ? 'online' : 'offline',
      source: 'db.mer3y.xyz/api/services',
      detail: astrbot.detail ?? null,
      raw_state: astrbot.raw_state ?? null,
      raw_status: astrbot.raw_status ?? null,
      image: astrbot.image ?? null,
      checked_at: new Date().toISOString(),
    }), { status: 200, headers });
  } catch (error) {
    return new Response(JSON.stringify({
      status: 'unknown',
      error: String(error?.message || error),
    }), { status: 200, headers });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    },
  });
}
