import React, { useState, useEffect, useRef, useCallback } from 'react';
import useGeoLocation from '../hooks/useGeoLocation';
import { getNearbyAttractions } from '../services/api';
import monumentsData from '../data/monuments.json';
import trackingService from '../services/tracking';
import JourneyTracker from '../components/JourneyTracker';

/* ══════════════════════════════════════════════════════════════════
   FONTS + LEAFLET LOADER
   ══════════════════════════════════════════════════════════════════ */
const FontLink = () => {
  useEffect(() => {
    [
      { tag:'link', rel:'stylesheet', href:'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap' },
      { tag:'link', rel:'stylesheet', href:'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' },
      { tag:'script', src:'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js' },
    ].forEach(({ tag, ...attrs }) => {
      const el = document.createElement(tag);
      Object.assign(el, attrs);
      document.head.appendChild(el);
    });
  }, []);
  return null;
};

/* ══════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════════════ */
const C = {
  cream : '#F5F0E8',
  warm  : '#FAF7F2',
  dark  : '#1C1A17',
  mid   : '#5C5549',
  terra : '#B5451B',
  terraL: '#D4603A',
  panel : '#EDEAE3',
  border: 'rgba(28,26,23,0.09)',
  serif : "'Cormorant Garamond', Georgia, serif",
  sans  : "'Jost', sans-serif",
};

/* ══════════════════════════════════════════════════════════════════
   STATIC DATA
   ══════════════════════════════════════════════════════════════════ */
const SLIDES = [
  { label:'Spices of the Medina', sub:'Rahba Kedima · Marrakech'       },
  { label:'Leather & Babouches',  sub:'Souk Smata · Marrakech'         },
  { label:'Brass Lanterns',       sub:'Souk Haddadine · Marrakech'     },
  { label:'Argan & Botanicals',   sub:'Souk El Attarine · Marrakech'   },
  { label:'Berber Carpets',       sub:'Souk Zrabi · Marrakech'         },
  { label:'Silver Jewelry',       sub:'Souk des Bijoutiers · Marrakech'},
  { label:'Ceramics & Tagines',   sub:'Souk Semmarine · Marrakech'     },
];
const SLIDE_BG = [
  'linear-gradient(160deg,#c4a882,#8b6542,#5c3e20)',
  'linear-gradient(160deg,#b5451b,#7a2d10,#3d1608)',
  'linear-gradient(160deg,#8c7355,#5c4a30,#3d3020)',
  'linear-gradient(160deg,#6b9c6b,#4a7a4a,#2d5c2d)',
  'linear-gradient(160deg,#c8a870,#8c6830,#5c4210)',
  'linear-gradient(160deg,#7a8c9c,#4a6070,#2d4050)',
  'linear-gradient(160deg,#c4956a,#8b5e38,#5c3c1e)',
];
const SLIDE_EMOJI = ['🌶️','👟','🏮','🍶','🧺','🪬','🏺'];
const MENU_NAV  = ['Our Products','Offers','Price Detection','Souk Guide','Events','About Us','Our Story'];
const MENU_FOOT = ['Contact','FAQ','Instagram','Privacy policy'];
const CATEGORIES = ['All Categories','Spices','Leather','Textiles','Ceramics','Lanterns','Jewelry','Argan Oil'];
const SOUKS_LIST = ['All Souks','Souk Semmarine','Souk Smata','Souk Zrabi','Rahba Kedima','Souk Haddadine','Souk des Bijoutiers','Souk El Attarine'];
const BUDGETS    = ['Any Budget','Under 50 MAD','50–200 MAD','200–500 MAD','500–1,000 MAD','1,000+ MAD'];

/* ══════════════════════════════════════════════════════════════════
   MOROCCO KNOWLEDGE BASE — Hardcoded fallback + base context
   ══════════════════════════════════════════════════════════════════ */
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

const SOUK_PINS = [
  { name:'Souk Semmarine',      lat:31.6308, lng:-7.9880, spec:'Bags, shoes, pottery',        emoji:'🛍️' },
  { name:'Souk Smata',          lat:31.6315, lng:-7.9872, spec:'Babouches & leather slippers', emoji:'👟' },
  { name:'Souk Zrabi',          lat:31.6321, lng:-7.9864, spec:'Handmade carpets & rugs',      emoji:'🧺' },
  { name:'Souk Cherratine',     lat:31.6327, lng:-7.9857, spec:'Leather bags & belts',         emoji:'👜' },
  { name:'Rahba Kedima',        lat:31.6333, lng:-7.9849, spec:'Spices, herbs, rosewater',     emoji:'🌶️' },
  { name:'Souk Haddadine',      lat:31.6339, lng:-7.9841, spec:'Brass lanterns & metalwork',   emoji:'🏮' },
  { name:'Souk des Bijoutiers', lat:31.6298, lng:-7.9893, spec:'Silver & Berber jewelry',      emoji:'🪬' },
  { name:'Souk Chouari',        lat:31.6303, lng:-7.9876, spec:'Wood, baskets, games',         emoji:'🪵' },
  { name:'Souk El Attarine',    lat:31.6318, lng:-7.9887, spec:'Argan oil & perfumes',         emoji:'🍶' },
];

const PRICES = [
  { cat:'Leather', name:'Babouches',      arabic:'بلغة',        souk:'Souk Smata',       range:'80–150 MAD',     note:'Traditional pointed-toe leather. Price rises with embroidery.' },
  { cat:'Spices',  name:'Spices & Herbs', arabic:'بهارات',      souk:'Rahba Kedima',     range:'30–80 MAD/100g', note:'Cumin, saffron, ras el hanout. Always weighed fresh.' },
  { cat:'Argan',   name:'Argan Oil',      arabic:'زيت أركان',   souk:'Souk El Attarine', range:'150–300 MAD',    note:'Real oil = thick paste + strong nut aroma.' },
  { cat:'Crafts',  name:'Tagine Pot',     arabic:'طاجين',       souk:'Souk Semmarine',   range:'20–50 MAD',      note:'Decorative or functional. Clay, hand-painted.' },
  { cat:'Lanterns',name:'Moroccan Lantern',arabic:'فانوس مغربي',souk:'Souk Haddadine',   range:'100–800 MAD',    note:'Metal and glass. Stunning shadows when lit.' },
  { cat:'Textiles',name:'Berber Carpet',  arabic:'زربية بربرية',souk:'Souk Zrabi',       range:'800–5,000+ MAD', note:'Beni Ourain rugs. Shipping usually available.' },
];
const STEPS = [
  { num:'01', icon:'📷', title:'Capture',  desc:'Photograph any price tag or product in the souk with your phone.' },
  { num:'02', icon:'🔍', title:'Detect',   desc:'Computer vision locates the price region on busy market stalls.' },
  { num:'03', icon:'🧠', title:'Extract',  desc:'OCR reads prices in MAD — handwritten tags, Arabic numerals.' },
  { num:'04', icon:'✅', title:'Compare',  desc:'Instantly checked against our 2025/2026 fair price database.' },
];
const CAT_COLORS = { Leather:'#8B4513',Spices:'#e67e22',Argan:'#16a085',Crafts:'#27ae60',Lanterns:'#f39c12',Textiles:'#8e44ad' };

/* ══════════════════════════════════════════════════════════════════
   SCROLL REVEAL
   ══════════════════════════════════════════════════════════════════ */
function useReveal() {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold:0.08 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, vis];
}
function Reveal({ children, delay=0, style={} }) {
  const [ref, vis] = useReveal();
  return (
    <div ref={ref} style={{ opacity:vis?1:0, transform:vis?'translateY(0)':'translateY(26px)', transition:`opacity .7s ease ${delay}s,transform .7s ease ${delay}s`, ...style }}>
      {children}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   SUBSCRIBE MODAL
   ══════════════════════════════════════════════════════════════════ */
function SubscribeModal({ onClose }) {
  const [email, setEmail] = useState('');
  const [done,  setDone]  = useState(false);
  return (
    <div style={{ position:'fixed',top:62,right:14,zIndex:600,width:318,background:'#c3cfd8',borderRadius:10,boxShadow:'0 16px 56px rgba(0,0,0,0.22)',overflow:'hidden' }}>
      <button onClick={onClose} style={{ position:'absolute',top:13,right:13,background:'none',border:'none',fontSize:'0.95rem',cursor:'pointer',color:C.dark }}>✕</button>
      <div style={{ padding:'26px 26px 8px',fontSize:'3.6rem',lineHeight:1 }}>🦅</div>
      <div style={{ padding:'8px 26px 26px' }}>
        {done
          ? <p style={{ fontFamily:C.serif,fontSize:'1.1rem',fontStyle:'italic',color:C.dark }}>You're in! We'll be in touch.</p>
          : <>
              <p style={{ fontSize:'0.85rem',fontWeight:500,color:C.dark,marginBottom:13,lineHeight:1.5 }}>Receive 10% off on your first price detection!</p>
              <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Enter your email address"
                style={{ width:'100%',boxSizing:'border-box',background:'rgba(255,255,255,0.75)',border:'1.5px solid rgba(255,255,255,0.95)',borderRadius:5,padding:'11px 13px',fontFamily:C.sans,fontSize:'0.82rem',outline:'none',color:C.dark,marginBottom:9 }} />
              <button onClick={()=>email&&setDone(true)} style={{ width:'100%',background:C.dark,color:'white',border:'none',borderRadius:5,padding:11,fontFamily:C.sans,fontSize:'0.74rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',marginBottom:13 }}>Subscribe</button>
              <p style={{ fontSize:'0.73rem',color:'#3a3530',lineHeight:1.65 }}><strong>We promise we'll never spam.</strong> You'll only hear from us when we have something worth sharing.</p>
            </>
        }
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MENU PANEL — exact Mason & Fifth
   ══════════════════════════════════════════════════════════════════ */
function MenuPanel({ onClose, category, setCategory, souk, setSouk, budget, setBudget }) {
  const [entered, setEntered] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    return () => cancelAnimationFrame(id);
  }, []);
  const handleClose = () => { setEntered(false); setTimeout(onClose, 380); };
  const sel = { background:'none',border:'none',fontFamily:C.sans,fontSize:'0.75rem',color:'#888',outline:'none',cursor:'pointer',width:'100%',padding:0,appearance:'none',WebkitAppearance:'none' };
  return (
    <>
      {/* Blurred backdrop */}
      <div onClick={handleClose} style={{ position:'fixed',inset:0,zIndex:290,backdropFilter:'blur(3px)',WebkitBackdropFilter:'blur(3px)',background:'rgba(0,0,0,0.12)',opacity:entered?1:0,transition:'opacity 0.38s ease' }} />

      {/* Panel */}
      <div style={{ position:'fixed',top:0,left:0,bottom:0,zIndex:300,width:490,background:C.panel,display:'flex',flexDirection:'column',transform:entered?'translateX(0)':'translateX(-100%)',transition:'transform 0.38s cubic-bezier(0.4,0,0.2,1)',boxShadow:'6px 0 48px rgba(0,0,0,0.13)' }}>

        {/* Top: Logo + ✕ */}
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'18px 20px',flexShrink:0 }}>
          <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'1rem',letterSpacing:'-0.01em',color:C.dark }}>Souk&amp;Price</span>
          <button onClick={handleClose}
            style={{ width:38,height:38,background:'transparent',border:'1.5px solid rgba(28,26,23,0.22)',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',fontSize:'0.88rem',color:C.dark,transition:'background 0.2s' }}
            onMouseOver={e=>e.currentTarget.style.background='rgba(28,26,23,0.06)'}
            onMouseOut={e=>e.currentTarget.style.background='transparent'}>✕</button>
        </div>

        {/* Nav links: vertically centred, large serif */}
        <nav style={{ flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'8px 32px',overflow:'hidden' }}>
          {MENU_NAV.map((item,i) => (
            <a key={item} href="#" onClick={handleClose}
              style={{ display:'block',width:'100%',textAlign:'center',fontFamily:C.serif,fontSize:'2.15rem',fontWeight:400,lineHeight:1.45,color:C.dark,textDecoration:'none',opacity:entered?1:0,transform:entered?'translateY(0)':'translateY(10px)',transition:`opacity 0.42s ease ${i*.05+.08}s,transform 0.42s ease ${i*.05+.08}s,color 0.2s` }}
              onMouseOver={e=>e.currentTarget.style.color=C.terra}
              onMouseOut={e=>e.currentTarget.style.color=C.dark}>{item}</a>
          ))}
        </nav>

        {/* Footer links */}
        <div style={{ padding:'0 24px 14px',textAlign:'center',flexShrink:0,opacity:entered?1:0,transition:'opacity 0.5s ease 0.45s' }}>
          <p style={{ fontSize:'0.74rem',color:'#9c9890',lineHeight:2 }}>
            {MENU_FOOT.map((link,i) => (
              <span key={link}>
                <a href="#" onClick={handleClose} style={{ color:'#9c9890',textDecoration:'none',transition:'color 0.2s' }}
                  onMouseOver={e=>e.currentTarget.style.color=C.dark}
                  onMouseOut={e=>e.currentTarget.style.color='#9c9890'}>{link}</a>
                {i < MENU_FOOT.length-1 && <span style={{ margin:'0 4px' }}>,</span>}
              </span>
            ))}
          </p>
        </div>

        {/* Booking bar pinned at bottom */}
        <div style={{ display:'flex',alignItems:'stretch',background:'white',borderTop:`1px solid ${C.border}`,height:68,flexShrink:0 }}>
          <div style={{ flex:1.4,padding:'10px 18px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
            <p style={{ fontSize:'0.71rem',fontWeight:600,color:C.dark,marginBottom:3 }}>Book a stay</p>
            <select value={category} onChange={e=>setCategory(e.target.value)} style={sel}>{CATEGORIES.map(c=><option key={c}>{c}</option>)}</select>
          </div>
          <div style={{ flex:1,padding:'10px 16px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
            <p style={{ fontSize:'0.71rem',fontWeight:600,color:C.dark,marginBottom:3 }}>Check-In</p>
            <select value={souk} onChange={e=>setSouk(e.target.value)} style={sel}>{SOUKS_LIST.map(s=><option key={s}>{s}</option>)}</select>
          </div>
          <div style={{ flex:1,padding:'10px 16px',display:'flex',flexDirection:'column',justifyContent:'center' }}>
            <p style={{ fontSize:'0.71rem',fontWeight:600,color:C.dark,marginBottom:3 }}>Check-Out</p>
            <select value={budget} onChange={e=>setBudget(e.target.value)} style={sel}>{BUDGETS.map(b=><option key={b}>{b}</option>)}</select>
          </div>
        </div>
      </div>
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════
   ② INTERACTIVE MAP SECTION — Leaflet
   ══════════════════════════════════════════════════════════════════ */
function MapSection() {
  const mapRef      = useRef(null);
  const lMap        = useRef(null);         // Leaflet map instance
  const userMarkerR = useRef(null);
  const destMarkerR      = useRef(null);
  const routePolylineR   = useRef(null);   // ref → no stale closure
  const waypointMarkersR = useRef([]);     // ref → no stale closure
  const chatBottomRef = useRef(null);      // for auto-scroll

  const [mapReady,      setMapReady]      = useState(false);
  const [userPos,       setUserPos]       = useState(null);
  const [destination,   setDestination]   = useState(null);
  const [activeSouk,    setActiveSouk]    = useState(null);
  const [locating,      setLocating]      = useState(false);
  const [locError,      setLocError]      = useState(null);
  const [searchQuery,   setSearchQuery]   = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [nearbyPlaces,  setNearbyPlaces]  = useState([]);
  const [routeMode,     setRouteMode]     = useState(null);
  const [waypointMonuments, setWaypointMonuments] = useState([]);
  const [selectedWaypoint, setSelectedWaypoint] = useState(null);
  const [selectedWaypoints, setSelectedWaypoints] = useState([]);
  const [showJourneyTracker, setShowJourneyTracker] = useState(false);
  const [journeyActive, setJourneyActive] = useState(false);
  const [journeyData, setJourneyData] = useState(null);

  // ── Chat state ──
  const [chatOpen,     setChatOpen]     = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: "Marhaba! 👋 Ask me anything about Marrakech's souks, monuments, or neighbourhoods." }
  ]);
  const [chatInput,    setChatInput]    = useState('');
  const [chatLoading,  setChatLoading]  = useState(false);

  /* ── sendChatMessage function ── */
  const sendChatMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userMsg = { role: 'user', content: chatInput.trim() };
    const newMessages = [...chatMessages, userMsg];
    setChatMessages(newMessages);
    setChatInput('');
    setChatLoading(true);

    try {
      // Call local Ollama API
      const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3:latest', // Using your installed model
          prompt: `You are a knowledgeable Marrakech travel guide. Answer questions about Moroccan destinations using the knowledge base below. Be concise (2-4 sentences), warm, and practical. Always mention the nearest souk or landmark when relevant.

KNOWLEDGE BASE:
${MOROCCO_KB}

Question: ${userMsg.content}

Answer:`,
          stream: false,
          options: {
            temperature: 0.7,
            top_p: 0.9,
            max_tokens: 300
          }
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        let reply = data.response || 'Sorry, I could not get a response.';
        
        // Clean up the response
        reply = reply.trim();
        if (reply.startsWith('Answer:')) {
          reply = reply.substring(7).trim();
        }
        
        setChatMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, the local AI model is not available. Please make sure Ollama is running with: ollama serve' }]);
      }
    } catch (e) {
      console.error('Ollama API error:', e);
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please make sure Ollama is running on localhost:11434. Start with: ollama serve' }]);
    } finally {
      setChatLoading(false);
    }
  };



  /* ── Auto-scroll effect ── */
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  /* ── "Ask the Guide" callback ── */
  useEffect(() => {
    window.__askAbout = (placeName) => {
      setChatOpen(true);
      setChatInput(`Tell me about ${placeName}`);
    };
    return () => { delete window.__askAbout; };
  }, []);

  /* ── Auto-send message about destination ── */
  const askAboutDestination = (destinationName) => {
    setChatOpen(true);
    
    // Track user asking about destination
    trackingService.trackUserAction('ask_about_destination', {
      destination: destinationName
    });
    
    // Create the question
    const question = `Tell me about ${destinationName} - what should I know as a visitor?`;
    
    // Add user message immediately
    const userMsg = { role: 'user', content: question };
    setChatMessages(prev => [...prev, userMsg]);
    
    // Set loading state and send to chatbot
    setChatLoading(true);
    
    // Process the message
    setTimeout(async () => {
      try {
        // Call local Ollama API
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llama3:latest', // Using your installed model
            prompt: `You are a knowledgeable Marrakech travel guide. Provide detailed information about this destination using the knowledge base below. Include practical details like opening hours, entrance fees, and nearby landmarks.

KNOWLEDGE BASE:
${MOROCCO_KB}

Destination: ${destinationName}

Provide a comprehensive guide:`,
            stream: false,
            options: {
              temperature: 0.7,
              top_p: 0.9,
              max_tokens: 400
            }
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          let reply = data.response || 'Sorry, I could not find information about that destination.';
          
          // Clean up the response
          reply = reply.trim();
          if (reply.startsWith('Provide a comprehensive guide:')) {
            reply = reply.substring(30).trim();
          }
          
          setChatMessages(prev => [...prev, { role: 'assistant', content: reply }]);
        } else {
          setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, the local AI model is not available. Please make sure Ollama is running with: ollama serve' }]);
        }
      } catch (e) {
        console.error('Ollama API error:', e);
        setChatMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please make sure Ollama is running on localhost:11434. Start with: ollama serve' }]);
      } finally {
        setChatLoading(false);
      }
    }, 300);
  };

  /* ── Get user location ── */
  const locateMe = () => {
    setLocating(true); setLocError(null);
    navigator.geolocation.getCurrentPosition(
      p  => { setUserPos({ lat:p.coords.latitude, lng:p.coords.longitude }); setLocating(false); },
      () => { setLocError('Location access denied. Please enable it in your browser.'); setLocating(false); },
      { enableHighAccuracy:true, timeout:12000 }
    );
  };

  /* ── Auto-request location on mount ── */
  useEffect(() => {
    locateMe();
    // Track page view
    trackingService.trackPageView('Location Helper');
  }, []);

  /* ── Init Leaflet ── */
  useEffect(() => {
    const tryInit = () => {
      if (!window.L || lMap.current || !mapRef.current) return false;
      const L = window.L;

      const map = L.map(mapRef.current, { center:[31.6295,-7.9811], zoom:15, zoomControl:false });
      L.control.zoom({ position:'bottomright' }).addTo(map);

      // CartoDB Voyager — warm, readable, English labels
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution:'© OpenStreetMap contributors © CARTO', maxZoom:19,
      }).addTo(map);

      lMap.current = map;
      setMapReady(true);

      // Souk pin markers
      SOUK_PINS.forEach(s => {
        const icon = L.divIcon({
          className:'',
          html:`<div style="width:38px;height:38px;background:#B5451B;border:3px solid white;border-radius:50% 50% 50% 4px;transform:rotate(-45deg);box-shadow:0 3px 14px rgba(181,69,27,0.38);display:flex;align-items:center;justify-content:center;cursor:pointer">
                  <span style="transform:rotate(45deg);font-size:14px;line-height:1">${s.emoji}</span>
                </div>`,
          iconSize:[38,38], iconAnchor:[19,38],
        });
        L.marker([s.lat,s.lng],{icon}).addTo(map)
          .bindPopup(`
            <div style="font-family:'Jost',sans-serif;padding:2px 0;min-width:170px">
              <p style="font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;color:#B5451B;margin-bottom:5px">Souk</p>
              <p style="font-size:1rem;font-weight:600;color:#1C1A17;margin-bottom:4px">${s.name}</p>
              <p style="font-size:0.76rem;color:#5C5549;margin-bottom:12px">${s.spec}</p>
              <button onclick="window.__setSoukDest(${s.lat},${s.lng},'${s.name}')"
                style="background:#1C1A17;color:white;border:none;border-radius:5px;padding:9px 0;font-family:'Jost',sans-serif;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;width:100%;transition:background 0.2s;margin-bottom:6px"
                onmouseover="this.style.background='#B5451B'" onmouseout="this.style.background='#1C1A17'">
                Set as Destination
              </button>
              <button onclick="window.__askAbout('${s.name} — ${s.spec}')"
                style="background:transparent;color:#B5451B;border:1px solid #B5451B;border-radius:5px;padding:7px 0;font-family:'Jost',sans-serif;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;width:100%;margin-top:6px;transition:all 0.2s"
                onmouseover="this.style.background='rgba(181,69,27,0.07)'" onmouseout="this.style.background='transparent'">
                Ask the Guide
              </button>
            </div>`, { maxWidth:220, closeButton:false });
      });

      // Click anywhere → custom destination
      map.on('click', e => {
        window.__setSoukDest(e.latlng.lat, e.latlng.lng, `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`);
      });

      return true;
    };

    if (!tryInit()) {
      const iv = setInterval(() => { if (tryInit()) clearInterval(iv); }, 250);
      return () => clearInterval(iv);
    }
  }, []);

  /* ── Global popup callback ── */
  useEffect(() => {
    window.__setSoukDest = (lat, lng, name) => {
      selectDestination(lat, lng, name);
      lMap.current?.closePopup();
    };
    return () => { 
      delete window.__setSoukDest;
    };
  }, []);

  /* ── Update route and markers when waypoints change ── */
  useEffect(() => {
    if (routeMode === 'scenic' && waypointMonuments.length > 0) {
      updateRouteWithWaypoints(selectedWaypoints);
      updateWaypointMarkers(selectedWaypoints);
    }
  }, [selectedWaypoints, routeMode, waypointMonuments.length]);

  const selectWaypoint = useCallback((waypointIndex) => {
    if (!userPos || !destination || !waypointMonuments[waypointIndex]) return;
    
    const waypoint = waypointMonuments[waypointIndex];
    const isAlreadySelected = selectedWaypoints.some(w => w.name === waypoint.name);
    
    // Track waypoint selection
    trackingService.trackUserAction('waypoint_selected', {
      waypoint_name: waypoint.name,
      action: isAlreadySelected ? 'removed' : 'added'
    });
    
    let newSelectedWaypoints;
    if (isAlreadySelected) {
      newSelectedWaypoints = selectedWaypoints.filter(w => w.name !== waypoint.name);
    } else {
      newSelectedWaypoints = [...selectedWaypoints, waypoint];
      
      // Track location scan for waypoint
      if (trackingService.hasTrackingConsent()) {
        trackingService.trackLocationScan(waypoint.name, waypoint.lat, waypoint.lng, true);
      }
    }
    
    setSelectedWaypoints(newSelectedWaypoints);
    lMap.current?.closePopup();
  }, [userPos, destination, waypointMonuments, selectedWaypoints]);

  /* ── Waypoint selection callback ── */
  useEffect(() => {
    console.log('Setting up waypoint callback, selectedWaypoints:', selectedWaypoints);
    window.__selectWaypoint = (waypointIndex) => {
      console.log('Callback called with index:', waypointIndex);
      selectWaypoint(waypointIndex);
    };
    return () => {
      delete window.__selectWaypoint;
    };
  }, [selectWaypoint]);

  const selectDestination = (lat, lng, name) => {
    setDestination({ lat, lng, name });
    setActiveSouk(name);
    
    // Track destination selection
    trackingService.trackUserAction('destination_selected', {
      destination_name: name,
      latitude: lat,
      longitude: lng
    });
    
    if (trackingService.hasTrackingConsent()) {
      trackingService.trackLocationScan(name, lat, lng, false);
    }
    
    setRouteMode(null);
    setWaypointMonuments([]);
    setSelectedWaypoint(null);
    setSelectedWaypoints([]);
    clearWaypointMarkers();
    if (routePolylineR.current) {
      routePolylineR.current.remove();
      routePolylineR.current = null;
    }
    drawRoute(lat, lng);
  };

  const clearWaypointMarkers = () => {
    waypointMarkersR.current.forEach(marker => marker.remove());
    waypointMarkersR.current = [];
  };

  const drawRoute = async (destLat, destLng) => {
    if (!mapReady || !userPos || !window.L) return;
    const L = window.L;
    if (routePolylineR.current) routePolylineR.current.remove();

    const pts = await fetchOSRMRoute([userPos, { lat: destLat, lng: destLng }]);
    const coords = pts ?? [[userPos.lat, userPos.lng], [destLat, destLng]];
    const polyline = L.polyline(coords, { color: C.terra, weight: 4, opacity: 0.85 }).addTo(lMap.current);
    routePolylineR.current = polyline;
    lMap.current.fitBounds(polyline.getBounds(), { padding: [60, 60] });
  };

  /* ── User location marker ── */
  useEffect(() => {
    if (!mapReady || !userPos || !window.L) return;
    const L = window.L;
    userMarkerR.current?.remove();
    userMarkerR.current = L.marker([userPos.lat, userPos.lng], {
      icon: L.divIcon({
        className:'',
        html:`<div style="width:20px;height:20px;background:#2563eb;border:3px solid white;border-radius:50%;box-shadow:0 0 0 8px rgba(37,99,235,0.18)"></div>`,
        iconSize:[20,20], iconAnchor:[10,10],
      }),
    }).addTo(lMap.current).bindPopup('<p style="font-family:\'Jost\',sans-serif;font-weight:600;font-size:0.85rem">📍 You are here</p>');
    lMap.current.flyTo([userPos.lat, userPos.lng], 16, { duration:1.5 });
  }, [userPos, mapReady]);

  /* ── Destination marker + route ── */
  useEffect(() => {
    if (!mapReady || !destination || !window.L) return;
    const L = window.L;
    destMarkerR.current?.remove();

    destMarkerR.current = L.marker([destination.lat, destination.lng], {
      icon: L.divIcon({
        className:'',
        html:`<div style="width:44px;height:44px;background:white;border:3px solid #1C1A17;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 4px 18px rgba(0,0,0,0.18)">🏁</div>`,
        iconSize:[44,44], iconAnchor:[22,22],
      }),
    }).addTo(lMap.current)
      .bindPopup(`<p style="font-family:'Jost',sans-serif;font-weight:600;font-size:0.85rem">🏁 ${destination.name}</p>`)
      .openPopup();

    if (!userPos) {
      lMap.current.flyTo([destination.lat, destination.lng], 17, { duration:1.2 });
    }
  }, [destination, mapReady]);

  // Straight-line distance estimate
  const distKm = userPos && destination
    ? Math.sqrt(
        Math.pow((destination.lat-userPos.lat)*111, 2) +
        Math.pow((destination.lng-userPos.lng)*111*Math.cos(userPos.lat*Math.PI/180), 2)
      ).toFixed(2)
    : null;

  const clearDest = () => {
    setDestination(null); setActiveSouk(null);
    setRouteMode(null); setWaypointMonuments([]);
    setSelectedWaypoint(null); setSelectedWaypoints([]);
    clearWaypointMarkers();
    destMarkerR.current?.remove(); destMarkerR.current = null;
    if (routePolylineR.current) {
      routePolylineR.current.remove();
      routePolylineR.current = null;
    }
  };

  const handleFastRoute = async () => {
    if (!userPos || !destination) return;
    setRouteMode('fast');
    setWaypointMonuments([]);
    if (routePolylineR.current) routePolylineR.current.remove();

    const L = window.L;
    const pts = await fetchOSRMRoute([userPos, destination]);
    const coords = pts ?? [[userPos.lat, userPos.lng], [destination.lat, destination.lng]];
    const polyline = L.polyline(coords, { color: C.terra, weight: 4, opacity: 0.85 }).addTo(lMap.current);
    routePolylineR.current = polyline;
    lMap.current.fitBounds(polyline.getBounds(), { padding: [60, 60] });
  };

  const handleScenicRoute = () => {
    if (!userPos || !destination || !window.L) return;
    
    setRouteMode('scenic');
    setSelectedWaypoint(null);
    setSelectedWaypoints([]);
    
    // Find monuments within 2km of the midpoint
    const midLat = (userPos.lat + destination.lat) / 2;
    const midLng = (userPos.lng + destination.lng) / 2;
    
    let nearbyMonuments = monumentsData
      .map(m => ({ ...m, distance: getDistance(midLat, midLng, m.lat, m.lon) }))
      .filter(m => m.distance <= 2)
      .sort((a, b) => a.distance - b.distance)
      .slice(0, 3);
    
    // Fallback: if no monuments within 2km, get closest 3 monuments
    if (nearbyMonuments.length === 0) {
      nearbyMonuments = monumentsData
        .map(m => ({ ...m, distance: getDistance(midLat, midLng, m.lat, m.lon) }))
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 3);
    }
    
    setWaypointMonuments(nearbyMonuments);
    
    // Clear existing route and waypoint markers
    if (routePolylineR.current) {
      routePolylineR.current.remove();
      routePolylineR.current = null;
    }
    clearWaypointMarkers();
    
    const L = window.L;
    const newWaypointMarkers = [];
    
    // Add clickable waypoint markers
    nearbyMonuments.forEach((monument, index) => {
      const marker = L.marker([monument.lat, monument.lon], {
        icon: L.divIcon({
          className: '',
          html: `<div style="width:36px;height:36px;background:#D4603A;border:3px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 3px 12px rgba(0,0,0,0.25);cursor:pointer;transition:transform 0.2s;font-weight:600;color:white" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">${index + 1}</div>`,
          iconSize: [36, 36],
          iconAnchor: [18, 18]
        })
      }).addTo(lMap.current);
      
      marker.bindPopup(`<div style="font-family:'Jost',sans-serif;padding:8px 0;min-width:180px">
        <p style="font-size:0.9rem;font-weight:600;color:#1C1A17;margin-bottom:6px">${monument.name}</p>
        <p style="font-size:0.75rem;color:#5C5549;margin-bottom:8px">${monument.category}</p>
        <p style="font-size:0.75rem;color:#B5451B;margin-bottom:12px">${monument.distance.toFixed(1)} km from route</p>
        <button onclick="window.__selectWaypoint && window.__selectWaypoint(${index})"
          style="background:#B5451B;color:white;border:none;border-radius:5px;padding:8px 16px;font-family:'Jost',sans-serif;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;width:100%;transition:background 0.2s"
          onmouseover="this.style.background='#D4603A'" onmouseout="this.style.background='#B5451B'">
          Add to Route
        </button>
      </div>`, { maxWidth: 220, closeButton: false });
      
      newWaypointMarkers.push(marker);
    });
    
    waypointMarkersR.current = newWaypointMarkers;
    
    // Show real road preview while user picks waypoints
    fetchOSRMRoute([userPos, destination]).then(pts => {
      if (routePolylineR.current) routePolylineR.current.remove();
      const coords = pts ?? [[userPos.lat, userPos.lng], [destination.lat, destination.lng]];
      const polyline = L.polyline(coords, { color: '#aaa', weight: 3, opacity: 0.55 }).addTo(lMap.current);
      routePolylineR.current = polyline;
    });
    
    // Fit bounds to include all waypoints
    const allPoints = [
      [userPos.lat, userPos.lng], 
      [destination.lat, destination.lng], 
      ...nearbyMonuments.map(m => [m.lat, m.lon])
    ];
    lMap.current.fitBounds(allPoints, { padding: [50, 50] });
  };


  const updateRouteWithWaypoints = async (waypoints) => {
    if (!userPos || !destination) return;
    if (routePolylineR.current) routePolylineR.current.remove();

    const L = window.L;

    // Build ordered stop list: user → ...waypoints → destination
    const stops = [userPos, ...waypoints.map(w => ({ lat: w.lat, lng: w.lon ?? w.lng })), destination];
    const pts = await fetchOSRMRoute(stops);
    const coords = pts ?? stops.map(p => [p.lat, p.lng ?? p.lon]);
    const color = waypoints.length > 0 ? C.terraL : '#aaa';
    const polyline = L.polyline(coords, { color, weight: 4, opacity: waypoints.length > 0 ? 0.9 : 0.55 }).addTo(lMap.current);
    routePolylineR.current = polyline;
    lMap.current.fitBounds(polyline.getBounds(), { padding: [50, 50] });
  };

  const updateWaypointMarkers = (selectedWaypoints) => {
    const L = window.L;
    
    waypointMarkersR.current.forEach((marker, index) => {
      const monument = waypointMonuments[index];
      const isSelected = selectedWaypoints.some(w => w.name === monument.name);
      const selectionOrder = selectedWaypoints.findIndex(w => w.name === monument.name) + 1;
      
      const iconHtml = isSelected 
        ? `<div style="width:36px;height:36px;background:#16a34a;border:3px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 3px 12px rgba(0,0,0,0.25);cursor:pointer;transition:all 0.2s;font-weight:600;color:white" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">${selectionOrder}</div>`
        : `<div style="width:36px;height:36px;background:#D4603A;border:3px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 3px 12px rgba(0,0,0,0.25);cursor:pointer;transition:transform 0.2s;font-weight:600;color:white" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">${index + 1}</div>`;
      
      marker.setIcon(L.divIcon({
        className: '',
        html: iconHtml,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      }));
      
      // Update popup content
      const buttonText = isSelected ? 'Remove from Route' : 'Add to Route';
      const buttonColor = isSelected ? '#dc2626' : '#B5451B';
      const buttonHoverColor = isSelected ? '#ef4444' : '#D4603A';
      
      marker.setPopupContent(`<div style="font-family:'Jost',sans-serif;padding:8px 0;min-width:180px">
        <p style="font-size:0.9rem;font-weight:600;color:#1C1A17;margin-bottom:6px">${monument.name}</p>
        <p style="font-size:0.75rem;color:#5C5549;margin-bottom:8px">${monument.category}</p>
        <p style="font-size:0.75rem;color:#B5451B;margin-bottom:12px">${monument.distance.toFixed(1)} km from route</p>
        ${isSelected ? `<p style="font-size:0.7rem;color:#16a34a;margin-bottom:8px;font-weight:600">✓ Stop ${selectionOrder} in route</p>` : ''}
        <button onclick="window.__selectWaypoint && window.__selectWaypoint(${index})"
          style="background:${buttonColor};color:white;border:none;border-radius:5px;padding:8px 16px;font-family:'Jost',sans-serif;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;width:100%;transition:background 0.2s"
          onmouseover="this.style.background='${buttonHoverColor}'" onmouseout="this.style.background='${buttonColor}'">
          ${buttonText}
        </button>
      </div>`);
    });
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    const results = monumentsData.filter(m => 
      m.name.toLowerCase().includes(query.toLowerCase()) || 
      m.city.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 5);
    setSearchResults(results);
  };

  const selectMonument = (monument) => {
    selectDestination(monument.lat, monument.lon, monument.name);
    setSearchQuery('');
    setSearchResults([]);
    findNearbyPlaces(monument.lat, monument.lon);
  };

  const getDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  /* ── OSRM real-road routing ── */
  const fetchOSRMRoute = async (waypoints) => {
    // waypoints: array of {lat, lng} or {lat, lon}
    const coords = waypoints
      .map(p => `${p.lng ?? p.lon},${p.lat}`)
      .join(';');
    const url = `https://router.project-osrm.org/route/v1/foot/${coords}?overview=full&geometries=geojson`;
    try {
      const res = await fetch(url);
      const data = await res.json();
      if (data.code !== 'Ok' || !data.routes[0]) return null;
      // GeoJSON coords are [lng, lat] — flip to [lat, lng] for Leaflet
      return data.routes[0].geometry.coordinates.map(([lng, lat]) => [lat, lng]);
    } catch (e) {
      console.error('OSRM error', e);
      return null;
    }
  };



  const findNearbyPlaces = (lat, lon) => {
    const nearby = monumentsData
      .map(m => ({ ...m, distance: getDistance(lat, lon, m.lat, m.lon) }))
      .filter(m => m.distance > 0 && m.distance <= 1000)
      .sort((a, b) => a.distance - b.distance)
      .slice(0, 10);
    setNearbyPlaces(nearby);
  };

  return (
    <section id="map" style={{ background:C.dark }}>
      {/* Section header */}
    

      {/* Map + sidebar */}
      <div style={{ display:'grid',gridTemplateColumns:'340px 1fr',minHeight:640 }}>

        {/* ── Sidebar ── */}
        <div style={{ background:'#232018',padding:'28px 24px',display:'flex',flexDirection:'column',gap:22,overflowY:'auto' }}>

          {/* Search */}
          <div>
            <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'#7a7060',marginBottom:10 }}>Search Monument</p>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search monuments..."
              style={{ width:'100%',background:'rgba(255,255,255,0.08)',border:'1px solid rgba(255,255,255,0.14)',borderRadius:7,padding:'12px 14px',fontFamily:C.sans,fontSize:'0.83rem',color:'white',outline:'none',marginBottom:8 }}
            />
            {searchResults.length > 0 && (
              <div style={{ background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',borderRadius:7,maxHeight:200,overflowY:'auto' }}>
                {searchResults.map((m, i) => (
                  <div
                    key={i}
                    onClick={() => selectMonument(m)}
                    style={{ padding:'10px 12px',cursor:'pointer',borderBottom:i<searchResults.length-1?'1px solid rgba(255,255,255,0.07)':'none',transition:'background 0.2s' }}
                    onMouseOver={e=>e.currentTarget.style.background='rgba(255,255,255,0.08)'}
                    onMouseOut={e=>e.currentTarget.style.background='transparent'}>
                    <p style={{ fontSize:'0.8rem',color:'white',marginBottom:2 }}>{m.name}</p>
                    <p style={{ fontSize:'0.7rem',color:'#7a7060' }}>{m.city}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Locate Me */}
          <div>
            <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'#7a7060',marginBottom:10 }}>Your Location</p>
            <button onClick={locateMe} disabled={locating}
              style={{ width:'100%',background:locating?'#3a3530':C.terra,color:'white',border:'none',borderRadius:7,padding:'14px 0',fontFamily:C.sans,fontSize:'0.78rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:locating?'not-allowed':'pointer',transition:'background 0.25s',display:'flex',alignItems:'center',justifyContent:'center',gap:10 }}
              onMouseOver={e=>!locating&&(e.currentTarget.style.background=C.terraL)}
              onMouseOut={e=>e.currentTarget.style.background=locating?'#3a3530':C.terra}>
              {locating
                ? <><span style={{ width:15,height:15,border:'2px solid rgba(255,255,255,0.3)',borderTopColor:'white',borderRadius:'50%',display:'inline-block',animation:'spin 0.8s linear infinite' }}/>Locating…</>
                : '📍  Use My Location'}
            </button>
            {locError && <p style={{ fontSize:'0.74rem',color:'#ef4444',marginTop:8,lineHeight:1.5 }}>{locError}</p>}
            {userPos   && <p style={{ fontSize:'0.74rem',color:'#22c55e',marginTop:8,display:'flex',alignItems:'center',gap:6 }}><span>✓</span>Location found</p>}
          </div>

          {/* Souk list */}
          <div style={{ flex:1 }}>
            <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'#7a7060',marginBottom:10 }}>Choose Destination</p>
            <div style={{ display:'flex',flexDirection:'column',gap:3 }}>
              {SOUK_PINS.map(s => {
                const active = activeSouk === s.name;
                return (
                  <button key={s.name}
                    onClick={() => selectDestination(s.lat, s.lng, s.name)}
                    style={{ background:active?C.terra:'rgba(255,255,255,0.04)',border:active?'none':'1px solid rgba(255,255,255,0.07)',borderRadius:7,padding:'12px 14px',cursor:'pointer',display:'flex',alignItems:'center',gap:12,textAlign:'left',transition:'all 0.2s',width:'100%' }}
                    onMouseOver={e=>!active&&(e.currentTarget.style.background='rgba(255,255,255,0.09)')}
                    onMouseOut={e=>!active&&(e.currentTarget.style.background='rgba(255,255,255,0.04)')}>
                    <span style={{ fontSize:'1.15rem',flexShrink:0 }}>{s.emoji}</span>
                    <div style={{ flex:1,minWidth:0 }}>
                      <p style={{ fontFamily:C.sans,fontSize:'0.83rem',fontWeight:500,color:active?'white':'#e0d8cc',marginBottom:2,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{s.name}</p>
                      <p style={{ fontSize:'0.69rem',color:active?'rgba(255,255,255,0.72)':'#7a7060',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{s.spec}</p>
                    </div>
                    {active && <span style={{ color:'rgba(255,255,255,0.8)',fontSize:'0.75rem',flexShrink:0 }}>✓</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Route card */}
          {destination && (
            <div style={{ background:'rgba(181,69,27,0.12)',border:'1px solid rgba(181,69,27,0.24)',borderRadius:9,padding:'20px 18px' }}>
              <p style={{ fontSize:'0.62rem',letterSpacing:'0.12em',textTransform:'uppercase',color:C.terra,marginBottom:10 }}>Active Route</p>
              <p style={{ fontFamily:C.serif,fontSize:'1.15rem',fontWeight:400,color:'white',marginBottom:6 }}>{destination.name}</p>
              {distKm && routeMode === 'fast' && (
                <p style={{ fontSize:'0.8rem',color:'#9d9080',marginBottom:14 }}>
                  ≈ <strong style={{ color:'white' }}>{distKm} km</strong> straight line · <strong style={{ color:'white' }}>{Math.round(distKm / 4 * 60)} min</strong> walking
                </p>
              )}
              {distKm && !routeMode && (
                <p style={{ fontSize:'0.8rem',color:'#9d9080',marginBottom:14 }}>
                  ≈ <strong style={{ color:'white' }}>{distKm} km</strong> as the crow flies
                </p>
              )}
              
              {/* Know More button */}
              <button 
                onClick={() => askAboutDestination(destination.name)}
                style={{ 
                  width:'100%',
                  background:C.terraL,
                  color:'white',
                  border:'none',
                  borderRadius:6,
                  padding:'10px 0',
                  fontFamily:C.sans,
                  fontSize:'0.74rem',
                  letterSpacing:'0.08em',
                  textTransform:'uppercase',
                  cursor:'pointer',
                  transition:'background 0.2s',
                  marginBottom:10,
                  display:'flex',
                  alignItems:'center',
                  justifyContent:'center',
                  gap:8
                }}
                onMouseOver={e=>e.currentTarget.style.background='#E67E22'}
                onMouseOut={e=>e.currentTarget.style.background=C.terraL}>
                🧭 Know More
              </button>
              
              {/* Start Journey button */}
              <button 
                onClick={() => setShowJourneyTracker(true)}
                style={{ 
                  width:'100%',
                  background:'#16a34a',
                  color:'white',
                  border:'none',
                  borderRadius:6,
                  padding:'12px 0',
                  fontFamily:C.sans,
                  fontSize:'0.76rem',
                  letterSpacing:'0.08em',
                  textTransform:'uppercase',
                  cursor:'pointer',
                  transition:'background 0.2s',
                  marginBottom:10,
                  display:'flex',
                  alignItems:'center',
                  justifyContent:'center',
                  gap:8,
                  fontWeight:600
                }}
                onMouseOver={e=>e.currentTarget.style.background='#22c55e'}
                onMouseOut={e=>e.currentTarget.style.background='#16a34a'}>
                🚀 Start Journey
              </button>
              
              <button onClick={clearDest}
                style={{ width:'100%',background:'none',border:'1px solid rgba(255,255,255,0.14)',borderRadius:5,padding:'8px 0',fontFamily:C.sans,fontSize:'0.71rem',color:'#9d9080',cursor:'pointer',transition:'all 0.2s' }}
                onMouseOver={e=>{e.currentTarget.style.borderColor='rgba(255,255,255,0.35)';e.currentTarget.style.color='white';}}
                onMouseOut={e=>{e.currentTarget.style.borderColor='rgba(255,255,255,0.14)';e.currentTarget.style.color='#9d9080';}}>
                Clear destination
              </button>
            </div>
          )}

          {/* Route Options Card */}
          {destination && !routeMode && userPos && (
            <div style={{ background:'rgba(255,255,255,0.08)',border:'1px solid rgba(255,255,255,0.14)',borderRadius:9,padding:'20px 18px' }}>
              <p style={{ fontFamily:C.serif,fontSize:'1.2rem',fontWeight:400,color:'white',marginBottom:16 }}>How do you want to get there?</p>
              <div style={{ display:'flex',flexDirection:'column',gap:10 }}>
                <button onClick={handleFastRoute}
                  style={{ width:'100%',background:C.terra,color:'white',border:'none',borderRadius:6,padding:'12px 16px',fontFamily:C.sans,fontSize:'0.8rem',fontWeight:500,cursor:'pointer',transition:'background 0.2s',textAlign:'left' }}
                  onMouseOver={e=>e.currentTarget.style.background=C.terraL}
                  onMouseOut={e=>e.currentTarget.style.background=C.terra}>
                  🏃 Take me there fast
                </button>
                <button onClick={handleScenicRoute}
                  style={{ width:'100%',background:C.panel,color:C.dark,border:'none',borderRadius:6,padding:'12px 16px',fontFamily:C.sans,fontSize:'0.8rem',fontWeight:500,cursor:'pointer',transition:'background 0.2s',textAlign:'left' }}
                  onMouseOver={e=>e.currentTarget.style.background='white'}
                  onMouseOut={e=>e.currentTarget.style.background=C.panel}>
                  🎭 Show me what's around
                </button>
              </div>
            </div>
          )}

          {/* Waypoint Monuments */}
          {routeMode === 'scenic' && waypointMonuments.length > 0 && (
            <div>
              <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'#7a7060',marginBottom:10 }}>Available Waypoints</p>
              <p style={{ fontSize:'0.75rem',color:'#9d9080',marginBottom:12,lineHeight:1.5 }}>Click numbered markers on map or cards below to build your route</p>
              <div style={{ display:'flex',flexDirection:'column',gap:3,maxHeight:200,overflowY:'auto' }}>
                {waypointMonuments.map((monument, i) => {
                  const isSelected = selectedWaypoints.some(w => w.name === monument.name);
                  const selectionOrder = selectedWaypoints.findIndex(w => w.name === monument.name) + 1;
                  return (
                    <div key={i}
                      onClick={() => selectWaypoint(i)}
                      style={{ 
                        background: isSelected ? 'rgba(34,197,94,0.12)' : 'rgba(212,96,58,0.12)',
                        border: isSelected ? '1px solid rgba(34,197,94,0.24)' : '1px solid rgba(212,96,58,0.24)',
                        borderRadius:7,
                        padding:'12px 14px',
                        display:'flex',
                        alignItems:'center',
                        justifyContent:'space-between',
                        cursor:'pointer',
                        transition:'all 0.2s'
                      }}
                      onMouseOver={e=>!isSelected&&(e.currentTarget.style.background='rgba(212,96,58,0.18)')}
                      onMouseOut={e=>!isSelected&&(e.currentTarget.style.background='rgba(212,96,58,0.12)')}>
                      <div style={{ display:'flex',alignItems:'center',gap:12,flex:1,minWidth:0 }}>
                        <div style={{ 
                          width:24,
                          height:24,
                          borderRadius:'50%',
                          background: isSelected ? '#16a34a' : C.terraL,
                          color:'white',
                          display:'flex',
                          alignItems:'center',
                          justifyContent:'center',
                          fontSize:'0.75rem',
                          fontWeight:600,
                          flexShrink:0
                        }}>
                          {isSelected ? selectionOrder : i + 1}
                        </div>
                        <div style={{ flex:1,minWidth:0 }}>
                          <p style={{ fontFamily:C.sans,fontSize:'0.83rem',fontWeight:500,color:'white',marginBottom:2,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{monument.name}</p>
                          <p style={{ fontSize:'0.69rem',color:'#9d9080',marginBottom:2 }}>{monument.category}</p>
                          <p style={{ fontSize:'0.69rem',color: isSelected ? '#22c55e' : C.terraL }}>{monument.distance.toFixed(1)} km from route</p>
                        </div>
                      </div>
                      <div style={{ fontSize:'0.7rem',color: isSelected ? '#22c55e' : '#9d9080',fontWeight:500 }}>
                        {isSelected ? `Stop ${selectionOrder}` : 'Click to add'}
                      </div>
                    </div>
                  );
                })}
              </div>
              {selectedWaypoints.length > 0 && (
                <div style={{ marginTop:12,padding:'12px',background:'rgba(34,197,94,0.08)',border:'1px solid rgba(34,197,94,0.2)',borderRadius:7 }}>
                  <p style={{ fontSize:'0.75rem',color:'#22c55e',fontWeight:500,marginBottom:4 }}>✓ Route with {selectedWaypoints.length} stop{selectedWaypoints.length > 1 ? 's' : ''}</p>
                  <p style={{ fontSize:'0.7rem',color:'#9d9080',lineHeight:1.4 }}>
                    Your location → {selectedWaypoints.map(w => w.name.split(' ')[0]).join(' → ')} → {destination.name}
                  </p>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedWaypoints([]);
                      updateRouteWithWaypoints([]);
                      updateWaypointMarkers([]);
                    }}
                    style={{ marginTop:8,background:'rgba(220,38,38,0.1)',border:'1px solid rgba(220,38,38,0.2)',borderRadius:4,padding:'6px 12px',fontSize:'0.7rem',color:'#dc2626',cursor:'pointer',transition:'all 0.2s' }}
                    onMouseOver={e=>e.currentTarget.style.background='rgba(220,38,38,0.15)'}
                    onMouseOut={e=>e.currentTarget.style.background='rgba(220,38,38,0.1)'}>
                    Clear all waypoints
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Nearby Places */}
          {nearbyPlaces.length > 0 && (
            <div>
              <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'#7a7060',marginBottom:10 }}>Nearby Places (100km)</p>
              <div style={{ display:'flex',flexDirection:'column',gap:3,maxHeight:250,overflowY:'auto' }}>
                {nearbyPlaces.map((place, i) => (
                  <div key={i} style={{ background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',borderRadius:7,padding:'10px 12px',transition:'all 0.2s' }}>
                    <div style={{ display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8 }}>
                      <div style={{ flex:1 }}>
                        <p style={{ fontFamily:C.sans,fontSize:'0.8rem',color:'#e0d8cc',marginBottom:2 }}>{place.name}</p>
                        <p style={{ fontSize:'0.69rem',color:'#7a7060' }}>{place.distance.toFixed(1)} km • {place.city}</p>
                      </div>
                    </div>
                    <div style={{ display:'flex',gap:6 }}>
                      <button 
                        onClick={() => selectDestination(place.lat, place.lon, place.name)}
                        style={{ flex:1,background:'rgba(255,255,255,0.08)',border:'1px solid rgba(255,255,255,0.14)',borderRadius:5,padding:'6px 8px',fontSize:'0.7rem',color:'#e0d8cc',cursor:'pointer',transition:'all 0.2s' }}
                        onMouseOver={e=>e.currentTarget.style.background='rgba(255,255,255,0.15)'}
                        onMouseOut={e=>e.currentTarget.style.background='rgba(255,255,255,0.08)'}>
                        Set Route
                      </button>
                      <button 
                        onClick={() => askAboutDestination(place.name)}
                        style={{ background:C.terraL,border:'none',borderRadius:5,padding:'6px 12px',fontSize:'0.7rem',color:'white',cursor:'pointer',transition:'background 0.2s',whiteSpace:'nowrap' }}
                        onMouseOver={e=>e.currentTarget.style.background='#E67E22'}
                        onMouseOut={e=>e.currentTarget.style.background=C.terraL}>
                        🧭 Ask
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Map canvas ── */}
        <div style={{ position:'relative' }}>
          <div ref={mapRef} style={{ width:'100%',height:'100%',minHeight:640 }} />

          {/* Floating hint */}
          {mapReady && !destination && (
            <div style={{ position:'absolute',bottom:22,left:'50%',transform:'translateX(-50%)',zIndex:500,background:'rgba(28,26,23,0.82)',backdropFilter:'blur(8px)',borderRadius:26,padding:'10px 22px',pointerEvents:'none',whiteSpace:'nowrap' }}>
              <p style={{ fontFamily:C.sans,fontSize:'0.74rem',color:'rgba(255,255,255,0.82)',letterSpacing:'0.05em' }}>
                🗺️  Click a pin or anywhere on the map to set your destination
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ── Chat Widget ── */}
      {/* Floating toggle button (always visible) */}
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

      {/* Chat panel (shown when chatOpen === true) */}
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
      
      {/* Floating Journey Indicator - shows when journey is active but modal is closed */}
      {journeyActive && !showJourneyTracker && journeyData && (
        <div style={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          zIndex: 400,
          background: '#16a34a',
          color: 'white',
          borderRadius: 12,
          padding: '12px 16px',
          boxShadow: '0 4px 20px rgba(22, 163, 74, 0.3)',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          minWidth: 200
        }}
        onClick={() => setShowJourneyTracker(true)}
        onMouseOver={e => {
          e.currentTarget.style.transform = 'scale(1.05)';
          e.currentTarget.style.boxShadow = '0 6px 25px rgba(22, 163, 74, 0.4)';
        }}
        onMouseOut={e => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 20px rgba(22, 163, 74, 0.3)';
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <div style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#22c55e',
              animation: 'pulse 2s infinite'
            }} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Journey Active</span>
          </div>
          <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>
            Duration: {journeyData.duration || '0s'}
          </div>
          <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>
            Locations: {journeyData.visitedCount || 0}
          </div>
          <div style={{ fontSize: '0.7rem', opacity: 0.7, marginTop: 4 }}>
            Click to open tracker
          </div>
        </div>
      )}
      
      {/* Journey Tracker Modal */}
      {showJourneyTracker && (
        <div style={{
          position: 'fixed',
          inset: 0,
          zIndex: 600,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}>
          <div style={{
            background: 'white',
            borderRadius: 16,
            width: '100%',
            maxWidth: '900px',
            maxHeight: '90vh',
            overflow: 'hidden',
            boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
            position: 'relative'
          }}>
            {/* Close button */}
            <button
              onClick={() => setShowJourneyTracker(false)}
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                zIndex: 10,
                background: 'rgba(0,0,0,0.1)',
                border: 'none',
                borderRadius: '50%',
                width: 40,
                height: 40,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                fontSize: '18px',
                color: '#666',
                transition: 'background 0.2s'
              }}
              onMouseOver={e => e.currentTarget.style.background = 'rgba(0,0,0,0.2)'}
              onMouseOut={e => e.currentTarget.style.background = 'rgba(0,0,0,0.1)'}
            >
              ✕
            </button>
            
            {/* Journey Tracker Content */}
            <div style={{ height: '90vh', overflow: 'auto' }}>
              <JourneyTracker 
                destination={destination}
                userPosition={userPos}
                onClose={() => setShowJourneyTracker(false)}
                existingJourneyData={journeyData}
                onJourneyStart={(data) => {
                  setJourneyActive(true);
                  setJourneyData(data);
                }}
                onJourneyEnd={() => {
                  setJourneyActive(false);
                  setJourneyData(null);
                }}
                onJourneyUpdate={(data) => {
                  setJourneyData(data);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

/* ══════════════════════════════════════════════════════════════════
   PRICE / STEP CARDS
   ══════════════════════════════════════════════════════════════════ */
function PriceCard({ p, delay }) {
  const [hov,setHov]=useState(false);
  return (
    <Reveal delay={delay}>
      <div onMouseEnter={()=>setHov(true)} onMouseLeave={()=>setHov(false)}
        style={{ background:hov?'#fff':C.warm,padding:'32px 28px',borderRight:`1px solid ${C.border}`,transition:'background .3s',height:'100%' }}>
        <p style={{ fontSize:'0.6rem',letterSpacing:'0.15em',textTransform:'uppercase',color:CAT_COLORS[p.cat]||C.terra,marginBottom:8 }}>{p.cat}</p>
        <h3 style={{ fontFamily:C.serif,fontSize:'1.4rem',fontWeight:400,marginBottom:4,lineHeight:1.2 }}>{p.name}</h3>
        <span style={{ display:'block',direction:'rtl',color:C.mid,fontSize:'0.82rem',fontStyle:'italic',fontFamily:C.serif,marginBottom:14 }}>{p.arabic}</span>
        <p style={{ fontSize:'0.71rem',color:C.mid,marginBottom:16,display:'flex',alignItems:'center',gap:8 }}>
          <span style={{ display:'inline-block',width:12,height:1,background:C.terra }}/>{p.souk}
        </p>
        <span style={{ fontFamily:C.serif,fontSize:'2rem',fontWeight:300 }}>{p.range}</span>
        <p style={{ marginTop:16,paddingTop:16,borderTop:`1px solid ${C.border}`,fontSize:'0.77rem',color:C.mid,lineHeight:1.65 }}>{p.note}</p>
      </div>
    </Reveal>
  );
}
function StepCard({ s, delay }) {
  const [hov,setHov]=useState(false);
  return (
    <Reveal delay={delay}>
      <div onMouseEnter={()=>setHov(true)} onMouseLeave={()=>setHov(false)}
        style={{ background:hov?'#26231f':C.dark,padding:'44px 32px',borderRight:'1px solid rgba(255,255,255,0.06)',transition:'background .3s',height:'100%' }}>
        <div style={{ fontFamily:C.serif,fontSize:'3rem',fontWeight:300,color:'rgba(181,69,27,0.2)',marginBottom:22 }}>{s.num}</div>
        <div style={{ width:44,height:44,background:'rgba(181,69,27,0.14)',borderRadius:'50%',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1.2rem',marginBottom:20 }}>{s.icon}</div>
        <h4 style={{ fontFamily:C.serif,fontSize:'1.3rem',fontWeight:400,color:'white',marginBottom:10 }}>{s.title}</h4>
        <p style={{ fontSize:'0.83rem',color:'#9d9080',lineHeight:1.75,fontWeight:300 }}>{s.desc}</p>
      </div>
    </Reveal>
  );
}
function Newsletter() {
  const [email,setEmail]=useState('');
  const [done,setDone]=useState(false);
  return (
    <div style={{ background:C.terra,padding:'90px 80px',textAlign:'center' }}>
      <Reveal><h2 style={{ fontFamily:C.serif,fontSize:'clamp(2.2rem,4vw,3.8rem)',fontWeight:300,color:'white',lineHeight:1.1,marginBottom:14 }}>Shop Marrakech with <em style={{ fontStyle:'italic' }}>confidence.</em></h2></Reveal>
      <Reveal delay={0.1}><p style={{ color:'rgba(255,255,255,0.75)',fontSize:'0.93rem',fontWeight:300,marginBottom:44 }}>Get price alerts and souk guides delivered to your inbox.</p></Reveal>
      <Reveal delay={0.2}>
        {done?<p style={{ color:'white',fontFamily:C.serif,fontSize:'1.4rem',fontStyle:'italic' }}>✓ You're in!</p>:(
          <div style={{ display:'flex',maxWidth:460,margin:'0 auto' }}>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Your email address"
              style={{ flex:1,background:'rgba(255,255,255,0.15)',border:'1px solid rgba(255,255,255,0.3)',borderRight:'none',padding:'15px 20px',color:'white',fontFamily:C.sans,fontSize:'0.88rem',outline:'none',borderRadius:'2px 0 0 2px' }}/>
            <button onClick={()=>email&&setDone(true)} style={{ background:'white',color:C.terra,border:'none',padding:'15px 26px',fontFamily:C.sans,fontSize:'0.72rem',letterSpacing:'0.1em',textTransform:'uppercase',cursor:'pointer',fontWeight:500,borderRadius:'0 2px 2px 0' }}>Subscribe</button>
          </div>
        )}
      </Reveal>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN
   ══════════════════════════════════════════════════════════════════ */
export default function SoukPrice() {
  const [showSubscribe,setShowSubscribe]=useState(false);
  const [showMenu,setShowMenu]=useState(false);
  const [slide,setSlide]=useState(0);
  const [category,setCategory]=useState('All Categories');
  const [souk,setSouk]=useState('All Souks');
  const [budget,setBudget]=useState('Any Budget');
  const [heroLoaded,setHeroLoaded]=useState(false);

  const { location, error: geoError, loading: geoLoading, getLocation } = useGeoLocation();
  const [attractions,setAttractions]=useState([]);

  useEffect(()=>{
    const t=setTimeout(()=>setHeroLoaded(true),80);
    const iv=setInterval(()=>setSlide(s=>(s+1)%SLIDES.length),5000);
    // Track page view
    trackingService.trackPageView('Location Helper Main');
    return()=>{ clearTimeout(t); clearInterval(iv); };
  },[]);

  useEffect(()=>{
    if(location){
      getNearbyAttractions(location.latitude,location.longitude)
        .then(({data})=>setAttractions(data))
        .catch(err=>console.error('Failed to fetch nearby attractions:',err));
    }
  },[location]);

  const ha=(d=0)=>({ opacity:heroLoaded?1:0, transform:heroLoaded?'translateY(0)':'translateY(18px)', transition:`opacity .7s ease ${d}s,transform .7s ease ${d}s` });
  const sel={ background:'none',border:'none',fontFamily:C.sans,fontSize:'0.76rem',color:'#888',outline:'none',cursor:'pointer',width:'100%',padding:0,appearance:'none',WebkitAppearance:'none' };

  return (
    <div style={{ fontFamily:C.sans,background:C.cream,color:C.dark,overflowX:'hidden' }}>
      <FontLink/>

      {/* ══ HEADER ══ */}
      <header style={{ position:'fixed',top:0,left:0,right:0,zIndex:200 }}>
        {/* Top row */}
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'12px 16px',background:'rgba(245,240,232,0.97)',backdropFilter:'blur(12px)' }}>
          <div style={{ display:'flex',alignItems:'center',gap:8 }}>
            <div style={{ background:'white',borderRadius:8,padding:'9px 18px',boxShadow:'0 1px 6px rgba(0,0,0,0.07)' }}>
              <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'0.98rem',letterSpacing:'-0.01em',color:C.dark }}>Souk&amp;Price</span>
            </div>
            <button onClick={()=>setShowMenu(m=>!m)}
              style={{ background:'white',border:'none',borderRadius:8,width:42,height:42,cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:4.5 }}>
              {[0,1,2].map(i=><span key={i} style={{ display:'block',width:17,height:1.5,background:C.dark,borderRadius:2 }}/>)}
            </button>
          </div>
          <div style={{ display:'flex',gap:8 }}>
            {['Enquiries','Subscribe'].map(label=>(
              <button key={label} onClick={label==='Subscribe'?()=>setShowSubscribe(s=>!s):undefined}
                style={{ background:'white',color:C.dark,border:'none',borderRadius:22,padding:'9px 20px',fontFamily:C.sans,fontSize:'0.82rem',fontWeight:400,cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',transition:'box-shadow .2s' }}
                onMouseOver={e=>e.currentTarget.style.boxShadow='0 3px 14px rgba(0,0,0,0.13)'}
                onMouseOut={e=>e.currentTarget.style.boxShadow='0 1px 6px rgba(0,0,0,0.07)'}>
                {label}
              </button>
            ))}
          </div>
        </div>
        {/* Booking bar */}
        {!showMenu&&(
          <div style={{ display:'flex',alignItems:'stretch',background:'white',borderRadius:10,margin:'0 16px 12px',boxShadow:'0 2px 14px rgba(0,0,0,0.09)',overflow:'hidden',height:58 }}>
            {[['Book a stay',category,setCategory,CATEGORIES,1.3],['Check-In',souk,setSouk,SOUKS_LIST,1],['Check-Out',budget,setBudget,BUDGETS,1]].map(([label,val,setter,opts,flex])=>(
              <div key={label} style={{ flex,padding:'10px 20px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
                <p style={{ fontSize:'0.73rem',fontWeight:600,color:C.dark,marginBottom:2 }}>{label}</p>
                <select value={val} onChange={e=>setter(e.target.value)} style={sel}>{opts.map(o=><option key={o}>{o}</option>)}</select>
              </div>
            ))}
            <button style={{ background:C.dark,color:'white',border:'none',padding:'0 26px',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',whiteSpace:'nowrap',transition:'background .25s' }}
              onMouseOver={e=>e.currentTarget.style.background=C.terra}
              onMouseOut={e=>e.currentTarget.style.background=C.dark}>Search</button>
          </div>
        )}
      </header>

      {showMenu&&<MenuPanel onClose={()=>setShowMenu(false)} category={category} setCategory={setCategory} souk={souk} setSouk={setSouk} budget={budget} setBudget={setBudget}/>}
      {showSubscribe&&<SubscribeModal onClose={()=>setShowSubscribe(false)}/>}

      

      {/* ── NEW: Interactive Map ── */}
      <MapSection/>

      <Newsletter/>

      {/* Footer */}
      <footer style={{ background:C.dark,padding:'60px 80px 30px' }}>
        <div style={{ display:'grid',gridTemplateColumns:'2fr 1fr 1fr 1fr',gap:56,marginBottom:52 }}>
          <div>
            <p style={{ fontFamily:C.serif,fontSize:'1.35rem',color:'white',marginBottom:14 }}>Souk <span style={{ color:C.terra }}>&</span> Price</p>
            <p style={{ fontSize:'0.81rem',color:'#7a7060',lineHeight:1.7,maxWidth:260 }}>AI-powered price detection for Marrakech souk products. Know what's fair.</p>
          </div>
          {[
            {t:'Products',l:['Spices','Leather','Textiles','Ceramics','Lanterns','Jewelry']},
            {t:'Souks',l:['Souk Semmarine','Rahba Kedima','Souk Zrabi','Souk Haddadine','Souk Smata']},
            {t:'Project',l:['About','Dataset','API','Price Guide','Contact']},
          ].map(col=>(
            <div key={col.t}>
              <h5 style={{ fontSize:'0.62rem',letterSpacing:'0.2em',textTransform:'uppercase',color:'#5c5549',marginBottom:16 }}>{col.t}</h5>
              <ul style={{ listStyle:'none' }}>{col.l.map(l=><li key={l} style={{ marginBottom:8 }}><a href="#" style={{ color:'#9d9080',textDecoration:'none',fontSize:'0.82rem' }}>{l}</a></li>)}</ul>
            </div>
          ))}
        </div>
        <div style={{ borderTop:'1px solid rgba(255,255,255,0.07)',paddingTop:20,display:'flex',justifyContent:'space-between',fontSize:'0.69rem',color:'#5c5549' }}>
          <span>© 2025 Souk & Price</span>
          <span>Price data: Morocco Travel Planner 2025/2026</span>
        </div>
      </footer>

      <style>{`
        *{box-sizing:border-box;margin:0;padding:0;}
        html{scroll-behavior:smooth;}
        select{-webkit-appearance:none;-moz-appearance:none;appearance:none;}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{box-shadow:0 0 0 5px rgba(181,69,27,0.22);}50%{box-shadow:0 0 0 11px rgba(181,69,27,0.07);}}
        ::placeholder{color:rgba(255,255,255,0.42)!important;}
        /* Leaflet popup styling */
        .leaflet-popup-content-wrapper{
          border-radius:10px!important;
          box-shadow:0 8px 40px rgba(0,0,0,0.16)!important;
          border:1px solid rgba(28,26,23,0.08)!important;
          padding:0!important;
        }
        .leaflet-popup-content{margin:20px 22px!important;}
        .leaflet-popup-tip-container{display:none!important;}
        .leaflet-container{font-family:'Jost',sans-serif!important;}
        .leaflet-control-zoom a{
          font-family:C.sans!important;
          border-radius:6px!important;
        }
      `}</style>
    </div>
  );
}