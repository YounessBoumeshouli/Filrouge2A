# Morocco Places Chatbot — LocationHelper Feature Brief

**For:** Amazon Q Agent (Claude Sonnet 4)
**Component:** `Frontend/src/pages/LocationHelper.jsx` → `MapSection`

---

## Overview

Add a floating chat widget inside `MapSection`. The bot answers questions about Moroccan destinations — especially Marrakech — using the existing RAG pipeline and a hardcoded knowledge base injected into the Claude system prompt.

---

## RAG — Use the Existing Pipeline

> **The RAG system already exists in the `/rag` folder. Do not rebuild it.**
> Simply run the embedding generation script to index the Morocco knowledge base, then query it from the chat function.

### Steps to generate new embeddings

```bash
# From the project root
cd rag
npm install          # if not already done
node generate-embeddings.js
```

This will read the knowledge sources, chunk them, embed them via the configured model, and write the vector index to `rag/embeddings/`. The chatbot function will then retrieve the top-k relevant chunks at query time and inject them into the Claude system prompt.

If the RAG folder uses Python instead of Node:

```bash
cd rag
pip install -r requirements.txt
python generate_embeddings.py
```

Check the `rag/README.md` for the exact command — only the run step is needed.

---

## Step 1 — Add Chat State to MapSection

Add inside `MapSection`, alongside the existing state declarations:

```js
const [chatOpen,     setChatOpen]     = useState(false);
const [chatMessages, setChatMessages] = useState([
  { role: 'assistant', content: "Marhaba! 👋 Ask me anything about Marrakech's souks, monuments, or neighbourhoods." }
]);
const [chatInput,    setChatInput]    = useState('');
const [chatLoading,  setChatLoading]  = useState(false);
const chatBottomRef = useRef(null); // for auto-scroll
```

---

## Step 2 — Hardcoded Knowledge Base Constant

Paste this outside any component, near `SOUK_PINS`. This is the fallback knowledge base and also serves as the base context injected into every system prompt alongside RAG results.

```js
const MOROCCO_KB = `
## Jemaa el-Fna (ساحة جامع الفناء)
The beating heart of Marrakech and a UNESCO-listed square active day and night.
By day: orange juice vendors, henna artists, snake charmers.
By night: open-air food stalls, storytellers, musicians.
Located at the entrance of the medina. Best time to visit: sunset (around 6–7pm).
Nearest souk: Souk Semmarine (2 min walk north).

## Koutoubia Mosque (جامع الكتبية)
The largest mosque in Marrakech, built in the 12th century under Almohad sultan Yaqub al-Mansour.
The 70m minaret served as the model for the Giralda in Seville and the Hassan Tower in Rabat.
Non-Muslims cannot enter but the surrounding rose gardens are open to all.
Located west of Jemaa el-Fna.

## Bahia Palace (قصر الباهية)
A 19th-century palace built for grand vizier Si Musa. The name means "brilliance."
Features 8 hectares of rooms, courtyards, and gardens.
Highlights: grand courtyard with orange trees, harem with zellij tilework, painted cedarwood ceilings.
Open daily. 15 min walk from Jemaa el-Fna.

## Saadian Tombs (المقابر السعدية)
Royal necropolis built under Sultan Ahmad al-Mansur in the late 16th century.
Hidden and sealed for centuries, rediscovered in 1917.
Contains 66 graves; the Hall of Twelve Columns features Italian Carrara marble and muqarnas plasterwork.
Located near the Kasbah Mosque.

## El Badi Palace (قصر البديع)
"The Incomparable" — built in 1578 to celebrate victory over Portugal.
Now a romantic ruin with sunken gardens and stork nests on towers.
Houses the original Koutoubia minbar (pulpit). Great views from the ramparts.

## Majorelle Garden (حديقة ماجوريل)
Created by French painter Jacques Majorelle in 1923, bought by Yves Saint Laurent in 1980.
Famous for its cobalt blue buildings (Majorelle Blue), exotic cactus garden, and the Berber Museum.
Located in Gueliz (Ville Nouvelle), 20 min walk or short taxi from the medina.

## Ben Youssef Madrasa (مدرسة ابن يوسف)
Islamic college founded in the 14th century, expanded by the Saadians in 1564–65.
Once the largest madrasa in North Africa, housing 900 students.
Stunning marble courtyard, zellij mosaics, carved stucco, cedarwood screens.
Located in the northern medina near the Ben Youssef Mosque.

## Tanneries (الدباغة — Chouara Tannery)
One of the oldest tanneries in the world, operating since the 11th century.
Hides are soaked in limestone and pigeon dung, then dyed in stone vats of saffron (yellow),
poppy (red), indigo (blue), and mint (green).
Best viewed from leather shop balconies. Go in the morning for the best light.
Located near Bab Debbagh in the eastern medina.

## Menara Gardens (حدائق المنارة)
12th-century Almohad gardens with an iconic pavilion reflected in a large rectangular pool.
The Atlas Mountains form a dramatic backdrop. Best at golden hour.
Located 3km west of the medina.

## Mellah — Jewish Quarter
Historic Jewish quarter established in the 16th century.
Overhanging balconies, narrow streets, the Lazama Synagogue, and a large Jewish cemetery.
Borders El Badi Palace to the north. Quieter and less touristy than the main medina.

## Souks of Marrakech
Organized by trade, a system unchanged since medieval times:
- Souk Semmarine: main artery — bags, shoes, pottery (entry point from Jemaa el-Fna)
- Souk Smata: babouches (leather slippers) — 80–150 MAD
- Souk Zrabi: Berber carpets and rugs — 800–5,000+ MAD
- Souk Cherratine: leather bags and belts
- Rahba Kedima: spices, herbs, medicinal plants, rosewater — the apothecary square
- Souk Haddadine: metalworkers hammering brass lanterns
- Souk des Bijoutiers: silver jewelry and Berber ornaments
- Souk El Attarine: argan oil, perfumes, and botanicals — 150–300 MAD
- Souk Chouari: wood, baskets, carpentry workshops

## Ramparts and Gates
Marrakech's 19km of ochre walls date from the 12th century (Almoravid dynasty).
Key gates: Bab Agnaou (most ornate, leads to Kasbah), Bab Doukkala (northwest),
Bab el-Khemis (north, flea market on Thursdays), Bab Debbagh (east, near tanneries).

## Practical Tips for Marrakech
- Currency: Moroccan Dirham (MAD). 1 EUR ≈ 11 MAD.
- Bargaining: expected in souks. Start at 30–40% of the asking price.
- Getting around: petit taxis (red, metered) for Gueliz; walk or calèche for the medina.
- Best seasons: March–May and September–November. Summers reach 40°C+.
- Languages: Darija (Moroccan Arabic), French, Tamazight. English widely spoken in tourist areas.
- Dress: cover shoulders and knees near mosques and conservative neighbourhoods.
`;
```

---

## Step 3 — sendChatMessage Function

Add inside `MapSection`. The RAG retrieval step is marked with a comment — replace with the actual RAG query call using whatever interface the `/rag` folder exposes (REST endpoint, imported function, etc.).

```js
const sendChatMessage = async () => {
  if (!chatInput.trim() || chatLoading) return;

  const userMsg = { role: 'user', content: chatInput.trim() };
  const newMessages = [...chatMessages, userMsg];
  setChatMessages(newMessages);
  setChatInput('');
  setChatLoading(true);

  try {
    // ── RAG: retrieve relevant chunks from the existing /rag pipeline ──
    // Replace this comment with the actual call, e.g.:
    // const ragChunks = await fetch('/api/rag/query', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ query: userMsg.content, topK: 4 })
    // }).then(r => r.json()).then(d => d.chunks.join('\n\n'));
    // For now, fall back to the hardcoded MOROCCO_KB:
    const ragChunks = MOROCCO_KB;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: `You are a knowledgeable Marrakech travel guide embedded in a souk navigation app.
Answer questions about Moroccan destinations, history, and culture using the knowledge base below.
Be concise (3–5 sentences max), warm, and practical.
If the user asks about a specific place, mention the nearest souk or landmark as a navigation hint.
If the question is outside Morocco, politely redirect to Moroccan destinations.
Never make up facts not in the knowledge base.

KNOWLEDGE BASE:
${ragChunks}`,
        messages: newMessages,
      }),
    });

    const data = await response.json();
    const reply = data.content?.[0]?.text ?? 'Sorry, I could not get a response.';
    setChatMessages(prev => [...prev, { role: 'assistant', content: reply }]);
  } catch (e) {
    setChatMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }]);
  } finally {
    setChatLoading(false);
  }
};
```

---

## Step 4 — Auto-scroll Effect

Add this `useEffect` inside `MapSection` to scroll to the latest message whenever `chatMessages` updates:

```js
useEffect(() => {
  chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [chatMessages]);
```

---

## Step 5 — Chat UI Widget

Place this JSX **inside the MapSection return**, as a sibling to the map `<div>`. Use the existing `C` design tokens to match the page style.

### Floating toggle button (always visible)

```jsx
<button
  onClick={() => setChatOpen(o => !o)}
  style={{
    position: 'fixed', bottom: 32, right: 32, zIndex: 500,
    width: 56, height: 56, borderRadius: '50%', background: C.terra,
    border: 'none', color: 'white', fontSize: '1.4rem', cursor: 'pointer',
    boxShadow: '0 4px 24px rgba(181,69,27,0.45)', transition: 'transform .2s',
  }}
  onMouseOver={e => e.currentTarget.style.transform = 'scale(1.08)'}
  onMouseOut={e  => e.currentTarget.style.transform = 'scale(1)'}>
  {chatOpen ? '✕' : '🗺️'}
</button>
```

### Chat panel (shown when `chatOpen === true`)

```jsx
{chatOpen && (
  <div style={{
    position: 'fixed', bottom: 104, right: 32, zIndex: 499,
    width: 340, height: 480, background: C.warm, borderRadius: 14,
    boxShadow: '0 16px 56px rgba(0,0,0,0.18)', border: `1px solid ${C.border}`,
    display: 'flex', flexDirection: 'column', overflow: 'hidden',
  }}>
    {/* Header */}
    <div style={{ padding: '16px 20px', borderBottom: `1px solid ${C.border}`, background: C.panel }}>
      <p style={{ fontFamily: C.serif, fontSize: '1.1rem', fontWeight: 400, color: C.dark }}>
        Marrakech Guide 🧭
      </p>
      <p style={{ fontSize: '0.72rem', color: C.mid, marginTop: 2 }}>Ask about any place or souk</p>
    </div>

    {/* Messages */}
    <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
      {chatMessages.map((msg, i) => (
        <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
          <div style={{
            maxWidth: '82%', padding: '10px 14px', fontSize: '0.83rem', lineHeight: 1.6,
            borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
            background: msg.role === 'user' ? C.terra : C.panel,
            color: msg.role === 'user' ? 'white' : C.dark,
          }}>
            {msg.content}
          </div>
        </div>
      ))}
      {chatLoading && (
        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
          <div style={{ background: C.panel, borderRadius: '12px 12px 12px 2px', padding: '10px 16px', fontSize: '1rem' }}>
            ···
          </div>
        </div>
      )}
      <div ref={chatBottomRef} />
    </div>

    {/* Input row */}
    <div style={{ display: 'flex', borderTop: `1px solid ${C.border}`, background: C.panel }}>
      <input
        value={chatInput}
        onChange={e => setChatInput(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && sendChatMessage()}
        placeholder="Ask about a place..."
        style={{
          flex: 1, border: 'none', background: 'transparent', padding: '14px 16px',
          fontFamily: C.sans, fontSize: '0.83rem', color: C.dark, outline: 'none',
        }}
      />
      <button
        onClick={sendChatMessage}
        disabled={chatLoading || !chatInput.trim()}
        style={{
          background: chatLoading || !chatInput.trim() ? C.border : C.dark,
          border: 'none', padding: '0 18px', color: 'white', cursor: 'pointer',
          fontFamily: C.sans, fontSize: '0.78rem', transition: 'background .2s',
        }}>
        ➤
      </button>
    </div>
  </div>
)}
```

---

## Step 6 — "Ask the Guide" Button in Map Popups

### Register the global callback

Add this `useEffect` inside `MapSection`:

```js
useEffect(() => {
  window.__askAbout = (placeName) => {
    setChatOpen(true);
    setChatInput(`Tell me about ${placeName}`);
  };
  return () => { delete window.__askAbout; };
}, []);
```

### Add the button to each souk popup

Inside the `SOUK_PINS.forEach(s => { ... })` block in the Leaflet init `useEffect`, add a second button to the popup HTML alongside the existing "Set as Destination" button:

```html
<button onclick="window.__askAbout('${s.name} — ${s.spec}')"
  style="background:transparent;color:#B5451B;border:1px solid #B5451B;border-radius:5px;
         padding:7px 0;font-family:'Jost',sans-serif;font-size:0.72rem;letter-spacing:0.08em;
         text-transform:uppercase;cursor:pointer;width:100%;margin-top:6px;transition:all 0.2s"
  onmouseover="this.style.background='rgba(181,69,27,0.07)'"
  onmouseout="this.style.background='transparent'">
  Ask the Guide
</button>
```

---

## Summary of All Changes

| What | Where | Notes |
|---|---|---|
| Run embedding script | `/rag/` folder | One-time step, see RAG section above |
| `MOROCCO_KB` constant | Top of file, near `SOUK_PINS` | Fallback + base context |
| 4 new state variables + `chatBottomRef` | Inside `MapSection` | Chat open/messages/input/loading |
| `sendChatMessage` function | Inside `MapSection` | Calls RAG then Anthropic API |
| Auto-scroll `useEffect` | Inside `MapSection` | Watches `chatMessages` |
| `window.__askAbout` `useEffect` | Inside `MapSection` | Wires popups to chat |
| Chat widget JSX | Inside `MapSection` return | Floating button + panel |
| "Ask the Guide" button | Inside each `bindPopup` HTML string | One button per souk pin |