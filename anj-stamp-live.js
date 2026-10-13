(() => {
  const ANJ_JS = "https://af84fdbb-4457-4ce1-85e4-18782f98b79b.snippet.anjcdn.org/anj-seal.js";
  const INTERVAL_MS = 60000;
  const proxies = [
    (u) => "https://api.allorigins.win/raw?url=" + encodeURIComponent(u),
    (u) => "https://corsproxy.io/?" + encodeURIComponent(u)
  ];

  function decodeHex(text) {
    return text.replace(/\\x([0-9a-fA-F]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
  }

  async function fetchStamp() {
    const url = ANJ_JS + "?t=" + Date.now();
    let text = null;
    for (const make of proxies) {
      try {
        const res = await fetch(make(url), { cache: "no-store" });
        if (!res.ok) continue;
        text = await res.text();
        if (text && text.length > 50) break;
      } catch (_) {}
    }
    if (!text) throw new Error("stamp fetch failed");
    text = decodeHex(text);
    let m = text.match(/sealassets\/([a-f0-9]{32})-/);
    if (m) return m[1];
    m = text.match(/stamp=([a-f0-9]{32})/);
    if (m) return m[1];
    throw new Error("stamp not found");
  }

  function applyStamp(stamp) {
    const nodes = document.querySelectorAll("[data-anj-real-href], a[href*=\"stamp=\"], img[src*=\"sealassets/\"]");
    nodes.forEach((el) => {
      ["data-anj-real-href", "href", "src"].forEach((attr) => {
        const v = el.getAttribute(attr);
        if (!v) return;
        let n = v.replace(/stamp=[a-f0-9]{32}/, "stamp=" + stamp);
        n = n.replace(/sealassets\/[a-f0-9]{32}-vodka\.bet-/, "sealassets/" + stamp + "-vodka.bet-");
        if (n !== v) el.setAttribute(attr, n);
      });
    });
  }

  async function tick() {
    try {
      applyStamp(await fetchStamp());
    } catch (_) {}
  }

  tick();
  setInterval(tick, INTERVAL_MS);
})();
