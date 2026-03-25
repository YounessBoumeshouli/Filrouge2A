import { Container, Typography, CircularProgress, Alert } from '@mui/material';
import ImageUpload from '../components/ImageUpload';
import PriceResult from '../components/PriceResult';
import { analyzePrice } from '../services/api';
import trackingService from '../services/tracking';

import React, { useState, useEffect, useRef } from 'react';

/* ══════════════════════════════════════════════════════════════════
   FONTS
   ══════════════════════════════════════════════════════════════════ */
const FontLink = () => {
  useEffect(() => {
    const l = document.createElement('link');
    l.rel  = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap';
    document.head.appendChild(l);
  }, []);
  return null;
};

/* ══════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════════════ */
const C = {
  cream : '#F5F0E8',
  warm  : '#FAF7F2',
  panel : '#EDEAE3',
  dark  : '#1C1A17',
  mid   : '#5C5549',
  soft  : '#9d9080',
  terra : '#B5451B',
  terraL: '#D4603A',
  border: 'rgba(28,26,23,0.09)',
  serif : "'Cormorant Garamond', Georgia, serif",
  sans  : "'Jost', sans-serif",
};

/* ══════════════════════════════════════════════════════════════════
   PRICE DATABASE - Load from actual JSON file
   ══════════════════════════════════════════════════════════════════ */
// This will be loaded from the actual marrakech_price_labels.json
const PRICE_DB_DEFAULT = [
  { product:'Moroccan Leather Babouches', category:'Leather',  emoji:'👟', fairMin:80,  fairMax:150,  currency:'MAD', souk:'Souk Smata',        tip:'Start at 90 MAD and walk away slowly — vendors often call you back.',          arabic:'بلغة'        },
  { product:'Ras el Hanout Spice Mix',    category:'Spices',   emoji:'🌶️', fairMin:30,  fairMax:80,   currency:'MAD/100g', souk:'Rahba Kedima',  tip:'Ask to smell before buying. Avoid pre-packaged "tourist blends".',             arabic:'رأس الحانوت' },
  { product:'Argan Oil (250ml)',          category:'Argan',    emoji:'🍶', fairMin:150, fairMax:300,  currency:'MAD', souk:'Souk El Attarine',   tip:'Real argan oil has a strong nutty smell and thick consistency.',               arabic:'زيت أركان'   },
  { product:'Hand-painted Tagine Pot',   category:'Ceramics', emoji:'🏺', fairMin:20,  fairMax:50,   currency:'MAD', souk:'Souk Semmarine',     tip:'Check the base — tourist tagines say "Made in China". Real ones are rough clay.',arabic:'طاجين'       },
  { product:'Brass Moroccan Lantern',    category:'Lanterns', emoji:'🏮', fairMin:100, fairMax:500,  currency:'MAD', souk:'Souk Haddadine',     tip:'Price depends on size & intricacy of the metalwork piercing.',                arabic:'فانوس مغربي' },
  { product:'Berber Wool Carpet',        category:'Textiles', emoji:'🧺', fairMin:800, fairMax:5000, currency:'MAD', souk:'Souk Zrabi',         tip:'Ask for the village of origin. Genuine Beni Ourain rugs are ivory with black.', arabic:'زربية بربرية' },
  { product:'Silver Berber Bracelet',    category:'Jewelry',  emoji:'🪬', fairMin:100, fairMax:600,  currency:'MAD', souk:'Souk des Bijoutiers', tip:'Real silver tarnishes — a bright, never-tarnished piece may be alpaca metal.',  arabic:'أساور أمازيغية'},
  { product:'Moroccan Woven Scarf',      category:'Textiles', emoji:'🧣', fairMin:50,  fairMax:120,  currency:'MAD', souk:'Souk Ahiak',         tip:'Pull a thread — silk frays, synthetic melts. Feel the weight.',               arabic:'وشاح'        },
];

const CAT_COLORS = {
  Leather:'#8B4513', Spices:'#e67e22', Argan:'#16a085',
  Ceramics:'#27ae60', Lanterns:'#f39c12', Textiles:'#8e44ad', Jewelry:'#2563eb',
};

const HISTORY_MOCK = [
  { id:1, product:'Argan Oil (250ml)', detected:'420 MAD', fair:'150–300 MAD', verdict:'overpriced', date:'Today, 11:42', emoji:'🍶' },
  { id:2, product:'Hand-painted Tagine', detected:'35 MAD',  fair:'20–50 MAD',  verdict:'fair',       date:'Today, 10:18', emoji:'🏺' },
  { id:3, product:'Brass Lantern',       detected:'280 MAD', fair:'100–500 MAD',verdict:'fair',       date:'Yesterday',    emoji:'🏮' },
];

/* ══════════════════════════════════════════════════════════════════
   HELPERS
   ══════════════════════════════════════════════════════════════════ */
const VERDICT = {
  overpriced:{ color:'#e74c3c', bg:'rgba(231,76,60,0.07)',  border:'rgba(231,76,60,0.2)',  label:'↑ Overpriced',  desc:'You\'re being charged more than fair market value.' },
  fair:      { color:'#16a34a', bg:'rgba(22,163,74,0.07)',  border:'rgba(22,163,74,0.2)',  label:'✓ Fair Price',  desc:'This price is within the fair range for Marrakech.' },
  deal:      { color:'#2563eb', bg:'rgba(37,99,235,0.07)',  border:'rgba(37,99,235,0.2)',  label:'↓ Great Deal',  desc:'You\'re getting a good price — go for it!' },
};

function useReveal() {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold:0.06 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, vis];
}
function Reveal({ children, delay=0, style={} }) {
  const [ref, vis] = useReveal();
  return (
    <div ref={ref} style={{ opacity:vis?1:0, transform:vis?'translateY(0)':'translateY(22px)', transition:`opacity .65s ease ${delay}s,transform .65s ease ${delay}s`, ...style }}>
      {children}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MENU PANEL
   ══════════════════════════════════════════════════════════════════ */
const MENU_NAV  = ['Our Products','Offers','Price Detection','Souk Guide','Events','About Us','Our Story'];
const MENU_FOOT = ['Contact','FAQ','Instagram','Privacy policy'];
const CATEGORIES = ['All Categories','Spices','Leather','Textiles','Ceramics','Lanterns','Jewelry','Argan Oil'];
const SOUKS_LIST = ['All Souks','Souk Semmarine','Souk Smata','Souk Zrabi','Rahba Kedima','Souk Haddadine','Souk des Bijoutiers','Souk El Attarine'];
const BUDGETS    = ['Any Budget','Under 50 MAD','50–200 MAD','200–500 MAD','500–1,000 MAD','1,000+ MAD'];

function MenuPanel({ onClose }) {
  const [entered, setEntered] = useState(false);
  const [cat, setCat]         = useState('All Categories');
  const [souk, setSouk]       = useState('All Souks');
  const [budget, setBudget]   = useState('Any Budget');
  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    return () => cancelAnimationFrame(id);
  }, []);
  const handleClose = () => { setEntered(false); setTimeout(onClose, 380); };
  const sel = { background:'none',border:'none',fontFamily:C.sans,fontSize:'0.75rem',color:'#888',outline:'none',cursor:'pointer',width:'100%',padding:0,appearance:'none',WebkitAppearance:'none' };
  return (
    <>
      <div onClick={handleClose} style={{ position:'fixed',inset:0,zIndex:290,backdropFilter:'blur(3px)',WebkitBackdropFilter:'blur(3px)',background:'rgba(0,0,0,0.12)',opacity:entered?1:0,transition:'opacity 0.38s ease' }}/>
      <div style={{ position:'fixed',top:0,left:0,bottom:0,zIndex:300,width:490,background:C.panel,display:'flex',flexDirection:'column',transform:entered?'translateX(0)':'translateX(-100%)',transition:'transform 0.38s cubic-bezier(0.4,0,0.2,1)',boxShadow:'6px 0 48px rgba(0,0,0,0.13)' }}>
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'18px 20px',flexShrink:0 }}>
          <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'1rem',letterSpacing:'-0.01em',color:C.dark }}>Souk&amp;Price</span>
          <button onClick={handleClose} style={{ width:38,height:38,background:'transparent',border:'1.5px solid rgba(28,26,23,0.22)',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',fontSize:'0.88rem',color:C.dark,transition:'background 0.2s' }}
            onMouseOver={e=>e.currentTarget.style.background='rgba(28,26,23,0.06)'}
            onMouseOut={e=>e.currentTarget.style.background='transparent'}>✕</button>
        </div>
        <nav style={{ flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'8px 32px',overflow:'hidden' }}>
          {MENU_NAV.map((item,i) => (
            <a key={item} href="#" onClick={handleClose}
              style={{ display:'block',width:'100%',textAlign:'center',fontFamily:C.serif,fontSize:'2.15rem',fontWeight:400,lineHeight:1.45,color:C.dark,textDecoration:'none',opacity:entered?1:0,transform:entered?'translateY(0)':'translateY(10px)',transition:`opacity 0.42s ease ${i*.05+.08}s,transform 0.42s ease ${i*.05+.08}s,color 0.2s` }}
              onMouseOver={e=>e.currentTarget.style.color=C.terra}
              onMouseOut={e=>e.currentTarget.style.color=C.dark}>{item}</a>
          ))}
        </nav>
        <div style={{ padding:'0 24px 14px',textAlign:'center',flexShrink:0,opacity:entered?1:0,transition:'opacity 0.5s ease 0.45s' }}>
          <p style={{ fontSize:'0.74rem',color:'#9c9890',lineHeight:2 }}>
            {MENU_FOOT.map((link,i) => (
              <span key={link}>
                <a href="#" onClick={handleClose} style={{ color:'#9c9890',textDecoration:'none' }}
                  onMouseOver={e=>e.currentTarget.style.color=C.dark}
                  onMouseOut={e=>e.currentTarget.style.color='#9c9890'}>{link}</a>
                {i < MENU_FOOT.length-1 && <span style={{ margin:'0 4px' }}>,</span>}
              </span>
            ))}
          </p>
        </div>
        <div style={{ display:'flex',alignItems:'stretch',background:'white',borderTop:`1px solid ${C.border}`,height:68,flexShrink:0 }}>
          {[['Book a stay',cat,setCat,CATEGORIES,1.4],['Check-In',souk,setSouk,SOUKS_LIST,1],['Check-Out',budget,setBudget,BUDGETS,1]].map(([label,val,setter,opts,flex])=>(
            <div key={label} style={{ flex,padding:'10px 16px',borderRight:label!=='Check-Out'?'1px solid #EBEBEB':'none',display:'flex',flexDirection:'column',justifyContent:'center' }}>
              <p style={{ fontSize:'0.71rem',fontWeight:600,color:C.dark,marginBottom:3 }}>{label}</p>
              <select value={val} onChange={e=>setter(e.target.value)} style={sel}>{opts.map(o=><option key={o}>{o}</option>)}</select>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════
   SUBSCRIBE MODAL
   ══════════════════════════════════════════════════════════════════ */
function SubscribeModal({ onClose }) {
  const [email,setEmail]=useState('');
  const [done,setDone]=useState(false);
  return (
    <div style={{ position:'fixed',top:62,right:14,zIndex:600,width:318,background:'#c3cfd8',borderRadius:10,boxShadow:'0 16px 56px rgba(0,0,0,0.22)',overflow:'hidden' }}>
      <button onClick={onClose} style={{ position:'absolute',top:13,right:13,background:'none',border:'none',fontSize:'0.95rem',cursor:'pointer',color:C.dark }}>✕</button>
      <div style={{ padding:'26px 26px 8px',fontSize:'3.6rem',lineHeight:1 }}>🦅</div>
      <div style={{ padding:'8px 26px 26px' }}>
        {done ? <p style={{ fontFamily:C.serif,fontSize:'1.1rem',fontStyle:'italic',color:C.dark }}>You're in! We'll be in touch.</p> : <>
          <p style={{ fontSize:'0.85rem',fontWeight:500,color:C.dark,marginBottom:13,lineHeight:1.5 }}>Receive 10% off on your first price detection!</p>
          <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Enter your email address"
            style={{ width:'100%',boxSizing:'border-box',background:'rgba(255,255,255,0.75)',border:'1.5px solid rgba(255,255,255,0.95)',borderRadius:5,padding:'11px 13px',fontFamily:C.sans,fontSize:'0.82rem',outline:'none',color:C.dark,marginBottom:9 }}/>
          <button onClick={()=>email&&setDone(true)} style={{ width:'100%',background:C.dark,color:'white',border:'none',borderRadius:5,padding:11,fontFamily:C.sans,fontSize:'0.74rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',marginBottom:13 }}>Subscribe</button>
          <p style={{ fontSize:'0.73rem',color:'#3a3530',lineHeight:1.65 }}><strong>We promise we'll never spam.</strong></p>
        </>}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   PRICE METER — animated bar comparing detected vs fair
   ══════════════════════════════════════════════════════════════════ */
function PriceMeter({ detected, fairMin, fairMax }) {
  const [animated, setAnimated] = useState(false);
  useEffect(() => { const t = setTimeout(() => setAnimated(true), 200); return () => clearTimeout(t); }, []);

  const scale = fairMax * 1.8;
  const detectedPct  = Math.min((detected / scale) * 100, 100);
  const fairMinPct   = (fairMin / scale) * 100;
  const fairMaxPct   = (fairMax / scale) * 100;
  const fairWidthPct = fairMaxPct - fairMinPct;

  return (
    <div style={{ marginBottom:28 }}>
      <div style={{ display:'flex',justifyContent:'space-between',alignItems:'flex-end',marginBottom:10 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.14em',textTransform:'uppercase',color:C.mid }}>Price Comparison</p>
        <p style={{ fontSize:'0.72rem',color:C.mid }}>
          <span style={{ display:'inline-block',width:10,height:10,borderRadius:2,background:'rgba(22,163,74,0.35)',border:'1.5px solid #16a34a',marginRight:5,verticalAlign:'middle' }}/>Fair zone
        </p>
      </div>
      {/* Track */}
      <div style={{ position:'relative',height:14,background:'rgba(28,26,23,0.06)',borderRadius:8,overflow:'visible' }}>
        {/* Fair zone band */}
        <div style={{ position:'absolute',top:0,bottom:0,left:`${fairMinPct}%`,width:`${fairWidthPct}%`,background:'rgba(22,163,74,0.18)',border:'1px solid rgba(22,163,74,0.35)',borderRadius:4 }}/>
        {/* Detected needle */}
        <div style={{ position:'absolute',top:-5,bottom:-5,left:`${animated?detectedPct:0}%`,width:4,background:detected > fairMax ? '#e74c3c' : detected < fairMin ? '#2563eb' : '#16a34a',borderRadius:4,transition:'left 1.2s cubic-bezier(0.34,1.56,0.64,1)',transform:'translateX(-50%)',boxShadow:`0 0 8px ${detected > fairMax ? 'rgba(231,76,60,0.5)' : 'rgba(22,163,74,0.5)'}` }}/>
      </div>
      {/* Labels */}
      <div style={{ display:'flex',justifyContent:'space-between',marginTop:8,position:'relative' }}>
        <span style={{ fontSize:'0.7rem',color:C.mid }}>0</span>
        <span style={{ position:'absolute',left:`${fairMinPct}%`,transform:'translateX(-50%)',fontSize:'0.68rem',color:'#16a34a',whiteSpace:'nowrap' }}>{fairMin}</span>
        <span style={{ position:'absolute',left:`${fairMaxPct}%`,transform:'translateX(-50%)',fontSize:'0.68rem',color:'#16a34a',whiteSpace:'nowrap' }}>{fairMax}</span>
        <span style={{ fontSize:'0.7rem',color:C.mid }}>{Math.round(scale)} MAD</span>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   RESULT PANEL
   ══════════════════════════════════════════════════════════════════ */
function ResultPanel({ result, onReset, PRICE_DB }) {
  const vd  = VERDICT[result.verdict];
  const catColor = CAT_COLORS[result.category] || C.terra;
  const savings  = result.detected > result.fairMax ? result.detected - result.fairMax : 0;

  return (
    <div style={{ display:'flex',flexDirection:'column',gap:0,animation:'fadeSlideIn 0.55s ease forwards' }}>

      {/* ── Verdict hero banner ── */}
      <div style={{ background:vd.bg,border:`1.5px solid ${vd.border}`,borderRadius:12,padding:'28px 32px',marginBottom:20,display:'flex',alignItems:'center',gap:20 }}>
        <div style={{ width:54,height:54,borderRadius:'50%',background:vd.color,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1.5rem',flexShrink:0,boxShadow:`0 4px 18px ${vd.border}` }}>
          {result.verdict==='overpriced'?'⚠️':result.verdict==='deal'?'🎉':'✅'}
        </div>
        <div>
          <p style={{ fontFamily:C.sans,fontSize:'0.65rem',fontWeight:600,letterSpacing:'0.14em',textTransform:'uppercase',color:vd.color,marginBottom:4 }}>{vd.label}</p>
          <p style={{ fontFamily:C.serif,fontSize:'1.35rem',fontWeight:300,color:C.dark,lineHeight:1.3 }}>{vd.desc}</p>
        </div>
      </div>

      {/* ── Product identity ── */}
      <div style={{ background:'white',borderRadius:12,padding:'28px 32px',marginBottom:4,border:`1px solid ${C.border}` }}>
        <div style={{ display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:20 }}>
          <div>
            <p style={{ fontSize:'0.6rem',letterSpacing:'0.15em',textTransform:'uppercase',color:catColor,marginBottom:6 }}>{result.category}</p>
            <h3 style={{ fontFamily:C.serif,fontSize:'2rem',fontWeight:400,lineHeight:1.15,color:C.dark,marginBottom:6 }}>{result.product}</h3>
            <p style={{ fontFamily:C.serif,fontSize:'1rem',color:C.mid,fontStyle:'italic',direction:'rtl',textAlign:'right' }}>{result.arabic}</p>
            {/* Detection method badge */}
            {result.detectionMethod && (
              <div style={{ marginTop:10,display:'inline-flex',alignItems:'center',gap:6,background:result.detectionMethod === 'YOLO-Ceramic' ? 'rgba(34,197,94,0.1)' : 'rgba(59,130,246,0.1)',border:`1px solid ${result.detectionMethod === 'YOLO-Ceramic' ? 'rgba(34,197,94,0.2)' : 'rgba(59,130,246,0.2)'}`,borderRadius:12,padding:'4px 10px' }}>
                <span style={{ fontSize:'0.7rem' }}>{result.detectionMethod === 'YOLO-Ceramic' ? '🏺' : result.detectionMethod === 'Price API' ? '📊' : '🎲'}</span>
                <span style={{ fontSize:'0.65rem',fontWeight:600,color:result.detectionMethod === 'YOLO-Ceramic' ? '#059669' : '#2563eb' }}>
                  {result.detectionMethod === 'YOLO-Ceramic' ? 'AI Ceramic Detection' : result.detectionMethod === 'Price API' ? 'Price Analysis' : 'Sample Data'}
                </span>
                {result.confidence && (
                  <span style={{ fontSize:'0.6rem',color:C.mid }}>({result.confidence}%)</span>
                )}
              </div>
            )}
          </div>
          <div style={{ fontSize:'3.5rem',lineHeight:1,flexShrink:0,marginLeft:20 }}>{result.emoji}</div>
        </div>

        {/* Price pair */}
        <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:3,marginBottom:24 }}>
          <div style={{ background:'#fef2f2',borderRadius:'8px 0 0 8px',padding:'22px 24px' }}>
            <p style={{ fontSize:'0.6rem',letterSpacing:'0.13em',textTransform:'uppercase',color:C.mid,marginBottom:8 }}>
              Owner's Price
            </p>
            <p style={{ fontFamily:C.serif,fontSize:'2.2rem',fontWeight:300,color:'#dc2626',lineHeight:1 }}>{result.detected} <span style={{ fontSize:'1rem' }}>MAD</span></p>
          </div>
          <div style={{ background:'#f0fdf4',borderRadius:'0 8px 8px 0',padding:'22px 24px' }}>
            <p style={{ fontSize:'0.6rem',letterSpacing:'0.13em',textTransform:'uppercase',color:C.mid,marginBottom:8 }}>Fair Price Range</p>
            <p style={{ fontFamily:C.serif,fontSize:'2.2rem',fontWeight:300,color:'#16a34a',lineHeight:1 }}>{result.fairMin}–{result.fairMax} <span style={{ fontSize:'1rem' }}>MAD</span></p>
          </div>
        </div>

        {/* Price meter */}
        <PriceMeter detected={result.detected} fairMin={result.fairMin} fairMax={result.fairMax}/>

        {savings > 0 && (
          <div style={{ background:'rgba(181,69,27,0.06)',border:'1px solid rgba(181,69,27,0.14)',borderRadius:8,padding:'14px 18px',marginBottom:16,display:'flex',alignItems:'center',gap:12 }}>
            <span style={{ fontSize:'1.2rem' }}>💡</span>
            <p style={{ fontSize:'0.84rem',color:C.dark,lineHeight:1.6 }}>
              You could save up to <strong style={{ color:C.terra }}>{savings} MAD</strong> by negotiating to the fair price.
            </p>
          </div>
        )}

        {/* Souk tag */}
        <p style={{ fontSize:'0.78rem',color:C.mid,display:'flex',alignItems:'center',gap:8 }}>
          <span style={{ display:'inline-block',width:16,height:1.5,background:C.terra,borderRadius:1 }}/>
          Best found at <strong style={{ color:C.dark,marginLeft:4 }}>{result.souk}</strong>
        </p>
        
        {/* YOLO Detections */}
        {result.yoloDetections && result.yoloDetections.length > 1 && (
          <div style={{ marginTop:20,padding:'16px 20px',background:'rgba(34,197,94,0.05)',border:'1px solid rgba(34,197,94,0.15)',borderRadius:8 }}>
            <p style={{ fontSize:'0.65rem',letterSpacing:'0.12em',textTransform:'uppercase',color:'#059669',marginBottom:10,display:'flex',alignItems:'center',gap:6 }}>
              <span>🤖</span> Other Objects Detected
            </p>
            <div style={{ display:'flex',flexWrap:'wrap',gap:8 }}>
              {result.yoloDetections.slice(1, 4).map((det, i) => {
                const getDetectionEmoji = (category) => {
                  const emojiMap = {
                    argan: '🍶', crafts: '🏺', jewelry: '💍', lanterns: '🏮',
                    leather: '👜', spices: '🌶️', textiles: '🧣',
                    jemaa_el_fnaa: '🕌', koutoubia_mosque: '🕌', bahia_palace: '🏛️'
                  };
                  return emojiMap[category.toLowerCase()] || '🛍️';
                };
                return (
                  <div key={i} style={{ display:'flex',alignItems:'center',gap:6,background:'white',border:'1px solid rgba(34,197,94,0.2)',borderRadius:16,padding:'4px 12px' }}>
                    <span style={{ fontSize:'0.8rem' }}>{getDetectionEmoji(det.class_name)}</span>
                    <span style={{ fontSize:'0.72rem',color:C.dark }}>{det.class_name.replace('_', ' ')}</span>
                    <span style={{ fontSize:'0.65rem',color:'#059669' }}>({Math.round(det.confidence * 100)}%)</span>
                  </div>
                );
              })}
              {result.yoloDetections.length > 4 && (
                <div style={{ fontSize:'0.7rem',color:C.mid,padding:'4px 8px' }}>+{result.yoloDetections.length - 4} more</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Bargaining tip ── */}
      <div style={{ background:C.dark,borderRadius:12,padding:'28px 32px',marginBottom:4 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.terraL,marginBottom:10 }}>💬  Bargaining Strategy</p>
        <p style={{ fontFamily:C.serif,fontSize:'1.25rem',fontWeight:300,color:'white',lineHeight:1.65,fontStyle:'italic' }}>"{result.tip}"</p>
      </div>

      {/* ── Similar products ── */}
      <div style={{ background:'white',borderRadius:12,padding:'28px 32px',border:`1px solid ${C.border}` }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:18 }}>Other Products in {result.category}</p>
        <div style={{ display:'flex',flexDirection:'column',gap:10 }}>
          {PRICE_DB && PRICE_DB.filter(p=>p.category===result.category && p.product!==result.product).slice(0,2).map((p,i)=>(
            <div key={i} style={{ display:'flex',alignItems:'center',gap:14,padding:'12px 0',borderBottom:`1px solid ${C.border}` }}>
              <span style={{ fontSize:'1.3rem' }}>{p.emoji}</span>
              <div style={{ flex:1 }}>
                <p style={{ fontSize:'0.85rem',fontWeight:500,color:C.dark,marginBottom:2 }}>{p.product}</p>
                <p style={{ fontSize:'0.73rem',color:C.mid }}>{p.souk}</p>
              </div>
              <span style={{ fontFamily:C.serif,fontSize:'1.1rem',color:C.dark,fontWeight:300 }}>{p.fairMin}–{p.fairMax} MAD</span>
            </div>
          ))}
          {(!PRICE_DB || PRICE_DB.filter(p=>p.category===result.category && p.product!==result.product).length===0) && (
            <p style={{ fontSize:'0.82rem',color:C.mid }}>No other products in this category.</p>
          )}
        </div>
      </div>

      {/* Detect another */}
      <button onClick={onReset}
        style={{ marginTop:16,background:'transparent',border:`1.5px solid ${C.border}`,borderRadius:8,padding:'14px',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.1em',textTransform:'uppercase',color:C.mid,cursor:'pointer',transition:'all 0.2s' }}
        onMouseOver={e=>{e.currentTarget.style.borderColor=C.terra;e.currentTarget.style.color=C.terra;}}
        onMouseOut={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.mid;}}>
        ← Detect Another Product
      </button>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   UPLOAD ZONE
   ══════════════════════════════════════════════════════════════════ */
function UploadZone({ onFileSelect, preview, fileName, onClear, ownerPrice, setOwnerPrice }) {
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = e => onFileSelect(e.target.result, file.name);
    reader.readAsDataURL(file);
  };

  return (
    <div style={{ display:'flex',flexDirection:'column',gap:14 }}>
      {/* Drop zone */}
      <div
        onDragOver={e=>{e.preventDefault();setDragging(true);}}
        onDragLeave={()=>setDragging(false)}
        onDrop={e=>{e.preventDefault();setDragging(false);handleFile(e.dataTransfer.files[0]);}}
        onClick={()=>!preview&&fileRef.current?.click()}
        style={{
          border:`2px dashed ${dragging?C.terra:'rgba(28,26,23,0.16)'}`,
          borderRadius:12,
          background:dragging?'rgba(181,69,27,0.04)':'white',
          minHeight:320,
          display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',
          cursor:preview?'default':'pointer',
          transition:'all 0.25s',
          position:'relative',
          overflow:'hidden',
        }}>
        {preview ? (
          <>
            <img src={preview} alt="uploaded" style={{ width:'100%',height:'100%',objectFit:'cover',position:'absolute',inset:0 }}/>
            {/* Overlay */}
            <div
              className="img-overlay"
              style={{ position:'absolute',inset:0,background:'rgba(28,26,23,0)',transition:'background 0.28s',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:12 }}
              onMouseOver={e=>e.currentTarget.style.background='rgba(28,26,23,0.62)'}
              onMouseOut={e=>e.currentTarget.style.background='rgba(28,26,23,0)'}>
              <button
                onClick={e=>{e.stopPropagation();fileRef.current?.click();}}
                style={{ background:'white',border:'none',borderRadius:6,padding:'10px 22px',fontFamily:C.sans,fontSize:'0.74rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',opacity:0,transition:'opacity 0.28s' }}
                className="overlay-btn">
                Change Photo
              </button>
            </div>
            {/* File badge */}
            <div style={{ position:'absolute',bottom:14,left:14,background:'rgba(28,26,23,0.72)',backdropFilter:'blur(6px)',borderRadius:6,padding:'7px 12px',display:'flex',alignItems:'center',gap:8 }}>
              <span style={{ fontSize:'0.8rem' }}>🖼️</span>
              <span style={{ fontFamily:C.sans,fontSize:'0.72rem',color:'rgba(255,255,255,0.9)',maxWidth:200,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{fileName}</span>
            </div>
          </>
        ) : (
          <div style={{ textAlign:'center',padding:'40px 30px',userSelect:'none' }}>
            {/* Upload icon */}
            <div style={{ width:88,height:88,borderRadius:'50%',background:'rgba(181,69,27,0.07)',border:`1.5px dashed rgba(181,69,27,0.25)`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'2.4rem',margin:'0 auto 24px',transition:'background 0.25s' }}>
              📷
            </div>
            <p style={{ fontFamily:C.serif,fontSize:'1.6rem',fontWeight:300,color:C.dark,marginBottom:8 }}>Drop your souk photo</p>
            <p style={{ fontSize:'0.8rem',color:C.mid,marginBottom:6 }}>Drag & drop or <span style={{ color:C.terra,fontWeight:500 }}>click to browse</span></p>
            <p style={{ fontSize:'0.7rem',color:'#b0a898' }}>JPG · PNG · WEBP · HEIC · up to 20MB</p>
          </div>
        )}
        <input ref={fileRef} type="file" accept="image/*" style={{ display:'none' }} onChange={e=>handleFile(e.target.files[0])}/>
      </div>

      {/* Owner Price Input */}
      <div style={{ marginTop: 16 }}>
        <p style={{ fontSize:'0.68rem',color:C.mid,letterSpacing:'0.1em',textTransform:'uppercase',marginBottom:8 }}>Owner's Asking Price (Optional)</p>
        <div style={{ position:'relative' }}>
          <input
            type="number"
            value={ownerPrice}
            onChange={(e) => setOwnerPrice(e.target.value)}
            placeholder="Enter price in MAD"
            style={{
              width:'100%',
              background:'white',
              border:`1.5px solid ${C.border}`,
              borderRadius:8,
              padding:'12px 16px',
              paddingRight:'50px',
              fontFamily:C.sans,
              fontSize:'0.85rem',
              outline:'none',
              color:C.dark,
              transition:'border-color 0.2s'
            }}
            onFocus={(e) => e.currentTarget.style.borderColor = C.terra}
            onBlur={(e) => e.currentTarget.style.borderColor = C.border}
          />
          <span style={{
            position:'absolute',
            right:'16px',
            top:'50%',
            transform:'translateY(-50%)',
            fontSize:'0.8rem',
            color:C.mid,
            pointerEvents:'none'
          }}>MAD</span>
        </div>
      </div>

      {/* Example photos row */}
      {!preview && (
        <div style={{ marginTop: 16 }}>
          <p style={{ fontSize:'0.68rem',color:C.mid,letterSpacing:'0.1em',textTransform:'uppercase',marginBottom:10 }}>Try with an example</p>
          <div style={{ display:'flex',gap:8 }}>
            {['🌶️ Spices','👟 Babouches','🏺 Ceramics','🏮 Lantern'].map((ex,i) => (
              <button key={i}
                onClick={()=>{
                  // Simulate selecting an example — in prod, load a real sample image
                  const item = PRICE_DB[i] || PRICE_DB_DEFAULT[i];
                  onFileSelect('__example__'+i, `example-${item.category.toLowerCase()}.jpg`);
                }}
                style={{ flex:1,background:'white',border:`1px solid ${C.border}`,borderRadius:7,padding:'10px 6px',fontFamily:C.sans,fontSize:'0.72rem',color:C.mid,cursor:'pointer',transition:'all 0.2s',whiteSpace:'nowrap' }}
                onMouseOver={e=>{e.currentTarget.style.borderColor=C.terra;e.currentTarget.style.color=C.terra;}}
                onMouseOut={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.mid;}}>
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   DETECTION STEPS — animated scanning UI
   ══════════════════════════════════════════════════════════════════ */
function ScanningState({ step }) {
  const steps = [
    { icon:'🔬', label:'Detecting objects with AI…',  done: step > 0 },
    { icon:'🏷️', label:'Reading price information…',    done: step > 1 },
    { icon:'📊', label:'Comparing with database…',   done: step > 2 },
    { icon:'✅', label:'Generating price report…',     done: step > 3 },
  ];
  return (
    <div style={{ background:'white',borderRadius:12,padding:'48px 40px',border:`1px solid ${C.border}`,display:'flex',flexDirection:'column',alignItems:'center',minHeight:420 }}>
      {/* Spinner */}
      <div style={{ position:'relative',width:80,height:80,marginBottom:32 }}>
        <div style={{ width:80,height:80,border:`3px solid rgba(181,69,27,0.1)`,borderTopColor:C.terra,borderRadius:'50%',animation:'spin 1s linear infinite' }}/>
        <div style={{ position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1.6rem' }}>🔍</div>
      </div>
      <p style={{ fontFamily:C.serif,fontSize:'1.7rem',fontWeight:300,color:C.dark,marginBottom:6 }}>Analysing your photo</p>
      <p style={{ fontSize:'0.8rem',color:C.mid,marginBottom:36 }}>This takes just a moment…</p>
      {/* Steps */}
      <div style={{ width:'100%',maxWidth:320,display:'flex',flexDirection:'column',gap:14 }}>
        {steps.map((s,i) => (
          <div key={i} style={{ display:'flex',alignItems:'center',gap:14,opacity:step>=i?1:0.3,transition:`opacity 0.4s ease ${i*0.15}s` }}>
            <div style={{ width:32,height:32,borderRadius:'50%',background:s.done?'rgba(22,163,74,0.12)':step===i?'rgba(181,69,27,0.1)':'rgba(28,26,23,0.05)',border:`1.5px solid ${s.done?'#16a34a':step===i?C.terra:'transparent'}`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'0.9rem',transition:'all 0.3s',flexShrink:0 }}>
              {s.done ? '✓' : s.icon}
            </div>
            <p style={{ fontFamily:C.sans,fontSize:'0.83rem',color:s.done?'#16a34a':step===i?C.dark:C.mid,fontWeight:step===i?500:300,transition:'color 0.3s' }}>{s.label}</p>
            {step===i && <div style={{ marginLeft:'auto',width:16,height:16,border:'2px solid rgba(181,69,27,0.25)',borderTopColor:C.terra,borderRadius:'50%',animation:'spin 0.8s linear infinite',flexShrink:0 }}/>}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   HISTORY ROW
   ══════════════════════════════════════════════════════════════════ */
function HistoryRow({ item }) {
  const vd = VERDICT[item.verdict];
  return (
    <div style={{ display:'flex',alignItems:'center',gap:16,padding:'16px 0',borderBottom:`1px solid ${C.border}` }}>
      <div style={{ width:44,height:44,borderRadius:8,background:'rgba(28,26,23,0.04)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1.3rem',flexShrink:0 }}>{item.emoji}</div>
      <div style={{ flex:1,minWidth:0 }}>
        <p style={{ fontSize:'0.86rem',fontWeight:500,color:C.dark,marginBottom:2,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{item.product}</p>
        <p style={{ fontSize:'0.72rem',color:C.mid }}>{item.date}</p>
      </div>
      <div style={{ textAlign:'right',flexShrink:0 }}>
        <p style={{ fontFamily:C.serif,fontSize:'1rem',color:C.dark,marginBottom:3 }}>{item.detected}</p>
        <span style={{ display:'inline-block',fontSize:'0.65rem',fontWeight:600,letterSpacing:'0.08em',textTransform:'uppercase',color:vd.color,background:vd.bg,border:`1px solid ${vd.border}`,borderRadius:10,padding:'2px 8px' }}>{vd.label}</span>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN PAGE
   ══════════════════════════════════════════════════════════════════ */
/* eslint-disable no-undef */
export default function PriceDetection() {
  const [showMenu,      setShowMenu]      = useState(false);
  const [showSubscribe, setShowSubscribe] = useState(false);
  const [preview,       setPreview]       = useState(null);
  const [fileName,      setFileName]      = useState('');
  const [ownerPrice,    setOwnerPrice]    = useState('');
  const [phase,         setPhase]         = useState('idle'); // idle | scanning | done
  const [scanStep,      setScanStep]      = useState(0);
  const [result,        setResult]        = useState(null);
  const [loaded,        setLoaded]        = useState(false);
  const [PRICE_DB,      setPRICE_DB]      = useState(PRICE_DB_DEFAULT);

  useEffect(() => { 
    setTimeout(() => setLoaded(true), 60); 
    // Load actual price data
    loadPriceData();
    // Track page view
    trackingService.trackPageView('Price Helper');
  }, []);
  
  // Load price data from JSON file
  const loadPriceData = async () => {
    try {
      const response = await fetch('/marrakech_price_labels.json');
      if (response.ok) {
        const data = await response.json();
        const formattedData = data.price_reference.map(item => ({
          product: item.product,
          category: item.category.charAt(0).toUpperCase() + item.category.slice(1),
          emoji: getEmojiForCategory(item.category),
          fairMin: item.price_min_mad,
          fairMax: item.price_max_mad,
          currency: 'MAD',
          souk: item.souk,
          tip: item.notes || 'Negotiate based on quality and craftsmanship.',
          arabic: item.arabic_name
        }));
        setPRICE_DB(formattedData);
        console.log('✓ Loaded real price data:', formattedData.length, 'products');
      } else {
        console.log('⚠ Could not load price data, using defaults');
      }
    } catch (error) {
      console.log('⚠ Error loading price data:', error.message);
    }
  };

  /* ── Real AI scan with API integration ── */
  const runScan = async () => {
    if (!preview || phase === 'scanning') return;
    setPhase('scanning');
    setScanStep(0);
    
    // Track user action
    trackingService.trackUserAction('price_scan_started', {
      has_owner_price: !!ownerPrice,
      owner_price: ownerPrice ? parseFloat(ownerPrice) : null
    });
    
    // Step through scan stages
    const stepTimings = [400, 900, 1500, 2100];
    stepTimings.forEach((ms, i) => {
      setTimeout(() => setScanStep(i + 1), ms);
    });
    
    try {
      // First try YOLO detection for better product identification
      let yoloResult = null;
      try {
        // Convert image to blob if it's a data URL
        let imageBlob;
        if (preview.startsWith('data:')) {
          const response = await fetch(preview);
          imageBlob = await response.blob();
        } else {
          // Handle example images
          imageBlob = new Blob(['mock'], { type: 'image/jpeg' });
        }
        
        const formData = new FormData();
        formData.append('file', imageBlob, 'image.jpg');
        
        const yoloResponse = await fetch('http://localhost:8000/detect', {
          method: 'POST',
          body: formData
        });
        
        if (yoloResponse.ok) {
          yoloResult = await yoloResponse.json();
          console.log('🤖 YOLO API Response:', yoloResult);
        } else {
          console.log('YOLO API error:', yoloResponse.status, yoloResponse.statusText);
        }
      } catch (yoloError) {
        console.log('YOLO detection not available:', yoloError.message);
      }
      
      // Try the original price analysis API
      let apiResult = null;
      try {
        const response = await analyzePrice(preview);
        apiResult = response.data;
      } catch (priceError) {
        console.log('Price API not available, using YOLO + mock data');
      }
      
      setTimeout(() => {
        let finalResult;
        
        if (yoloResult && yoloResult.success && yoloResult.detections.length > 0) {
          // Use YOLO detection results
          const detection = yoloResult.detections[0]; // Use first detection
          const productType = detection.class_name;
          const confidence = detection.confidence;
          
          console.log('🤖 YOLO Detection Results:', {
            detections: yoloResult.detections,
            selectedDetection: detection,
            productType,
            confidence
          });
          
          // Find matching product in database
          let baseProduct = PRICE_DB.find(p => 
            p.category.toLowerCase().includes(productType.toLowerCase()) ||
            p.product.toLowerCase().includes(productType.toLowerCase())
          );
          
          console.log('📊 Database Match:', {
            searchTerm: productType,
            foundProduct: baseProduct,
            availableProducts: PRICE_DB.map(p => ({ category: p.category, product: p.product }))
          });
          
          if (!baseProduct) {
            // Map YOLO class names to price database products
            const yoloToProductMap = {
              'Ceramic Vase': { product: 'Ceramic Vase', category: 'Ceramics', emoji: '🏺', fairMin: 50, fairMax: 200, souk: 'Souk Semmarine', tip: 'Check for authentic glazing and craftsmanship. Avoid mass-produced pieces.', arabic: 'مزهرية خزفية' },
              'Tagine': { product: 'Hand-painted Tagine Pot', category: 'Ceramics', emoji: '🏺', fairMin: 20, fairMax: 50, souk: 'Souk Semmarine', tip: 'Check the base — tourist tagines say "Made in China". Real ones are rough clay.', arabic: 'طاجين' },
              'Ceramic Cups': { product: 'Moroccan Tea Glasses', category: 'Ceramics', emoji: '☕', fairMin: 15, fairMax: 40, souk: 'Souk Semmarine', tip: 'Traditional tea glasses should have gold rim details. Check for chips.', arabic: 'كؤوس الشاي' },
              'Handcrafted Tamegroute Ceramic Cake Stand': { product: 'Tamegroute Ceramic Stand', category: 'Ceramics', emoji: '🍰', fairMin: 80, fairMax: 180, souk: 'Souk Semmarine', tip: 'Tamegroute ceramics have distinctive green glaze. Authentic pieces are heavier.', arabic: 'حامل كيك خزفي' },
              'White Ceramic Divided Plate with Silver Accents': { product: 'Decorative Ceramic Plate', category: 'Ceramics', emoji: '🍽️', fairMin: 60, fairMax: 150, souk: 'Souk Semmarine', tip: 'Silver accents should not tarnish easily. Check for hand-painted details.', arabic: 'طبق خزفي مزخرف' },
              'Tamegroute Ceramic Pitcher Handmade Moroccan Water': { product: 'Moroccan Water Pitcher', category: 'Ceramics', emoji: '🏺', fairMin: 40, fairMax: 100, souk: 'Souk Semmarine', tip: 'Authentic Tamegroute pottery has unique green glaze from local minerals.', arabic: 'إبريق ماء مغربي' }
            };
            
            baseProduct = yoloToProductMap[productType] || {
              product: `${productType}`,
              category: 'Ceramics',
              emoji: '🏺',
              fairMin: 30,
              fairMax: 120,
              currency: 'MAD',
              souk: 'Marrakech Souks',
              tip: `Look for authentic ${productType.toLowerCase()} - check quality and craftsmanship before buying.`,
              arabic: 'منتج مغربي'
            };
            
            console.log('🏗️ Created Product from YOLO:', baseProduct);
          }
          
          // Use owner's price if provided, otherwise generate realistic detected price
          const detected = ownerPrice && !isNaN(parseFloat(ownerPrice)) ? 
            parseFloat(ownerPrice) : 
            Math.round(baseProduct.fairMin + (baseProduct.fairMax - baseProduct.fairMin) * priceVariation);
          
          // Determine verdict based on comparison with fair price range
          const verdict = detected > baseProduct.fairMax * 1.1 ? 'overpriced' : 
                         detected < baseProduct.fairMin * 0.9 ? 'deal' : 'fair';
          
          finalResult = { 
            ...baseProduct, 
            detected, 
            verdict,
            confidence: Math.round(confidence * 100),
            detectionMethod: 'YOLO-Ceramic',
            yoloDetections: yoloResult.detections
          };
          
        } else if (apiResult && apiResult.success) {
          // Use original price API results
          const productType = apiResult.product_type;
          const confidence = apiResult.confidence;
          
          let baseProduct = PRICE_DB.find(p => p.category.toLowerCase() === productType.toLowerCase());
          if (!baseProduct) {
            baseProduct = {
              product: `${productType.charAt(0).toUpperCase() + productType.slice(1)} Product`,
              category: productType.charAt(0).toUpperCase() + productType.slice(1),
              emoji: getEmojiForCategory(productType),
              fairMin: 50,
              fairMax: 200,
              currency: 'MAD',
              souk: 'Marrakech Souks',
              tip: 'Negotiate based on quality and craftsmanship.',
              arabic: 'منتج مغربي'
            };
          }
          
          const priceVariation = confidence > 0.8 ? 1.1 : confidence > 0.6 ? 1.3 : 1.5;
          const detected = ownerPrice && !isNaN(parseFloat(ownerPrice)) ? 
            parseFloat(ownerPrice) : 
            Math.round(baseProduct.fairMin + (baseProduct.fairMax - baseProduct.fairMin) * priceVariation);
          const verdict = detected > baseProduct.fairMax * 1.1 ? 'overpriced' : 
                         detected < baseProduct.fairMin * 0.9 ? 'deal' : 'fair';
          
          finalResult = { 
            ...baseProduct, 
            detected, 
            verdict,
            confidence: Math.round(confidence * 100),
            detectionMethod: 'Price API',
            apiPredictions: apiResult.all_predictions
          };
          
        } else {
          // Fallback to mock result
          console.log('⚠️ YOLO Detection Failed - Using Fallback:', {
            yoloResult,
            yoloSuccess: yoloResult?.success,
            detectionsCount: yoloResult?.detections?.length || 0,
            apiResult
          });
          
          const isExample = preview.startsWith('__example__');
          const idx = isExample ? parseInt(preview.replace('__example__','')) : Math.floor(Math.random() * PRICE_DB.length);
          const base = PRICE_DB[idx % PRICE_DB.length] || PRICE_DB_DEFAULT[0];
          const detected = ownerPrice && !isNaN(parseFloat(ownerPrice)) ? 
            parseFloat(ownerPrice) : 
            Math.round(base.fairMin + (base.fairMax - base.fairMin) * (0.8 + Math.random() * 1.2));
          const verdict = detected > base.fairMax * 1.1 ? 'overpriced' : detected < base.fairMin * 0.9 ? 'deal' : 'fair';
          
          console.log('🎲 Fallback Result:', {
            selectedIndex: idx,
            selectedProduct: base,
            detectedPrice: detected,
            verdict
          });
          
          finalResult = { 
            ...base, 
            detected, 
            verdict,
            detectionMethod: 'Mock Data'
          };
        }
        
        setResult(finalResult);
        setPhase('done');
        
        // Track successful price scan
        if (trackingService.hasTrackingConsent()) {
          trackingService.trackPriceScan(
            finalResult.product,
            finalResult.category,
            finalResult.detected,
            ownerPrice ? parseFloat(ownerPrice) : null,
            finalResult.souk
          );
        }
      }, 2600);
      
    } catch (error) {
      console.error('Detection failed:', error);
      // Final fallback
      setTimeout(() => {
        const isExample = preview.startsWith('__example__');
        const idx = isExample ? parseInt(preview.replace('__example__','')) : Math.floor(Math.random() * PRICE_DB.length);
        const base = PRICE_DB[idx % PRICE_DB.length] || PRICE_DB_DEFAULT[0];
        const detected = ownerPrice && !isNaN(parseFloat(ownerPrice)) ? 
          parseFloat(ownerPrice) : 
          Math.round(base.fairMin + (base.fairMax - base.fairMin) * (0.8 + Math.random() * 1.2));
        const verdict = detected > base.fairMax * 1.1 ? 'overpriced' : detected < base.fairMin * 0.9 ? 'deal' : 'fair';
        setResult({ ...base, detected, verdict, detectionMethod: 'Fallback' });
        setPhase('done');
        
        // Track fallback price scan
        if (trackingService.hasTrackingConsent()) {
          trackingService.trackPriceScan(
            base.product,
            base.category,
            detected,
            ownerPrice ? parseFloat(ownerPrice) : null,
            base.souk
          );
        }
      }, 2600);
    }
  };
  
  // Helper function to get Arabic name for product
  const getArabicName = (category) => {
    const arabicMap = {
      argan: 'زيت أركان',
      crafts: 'حرف يدوية',
      jewelry: 'مجوهرات',
      lanterns: 'فوانيس',
      leather: 'جلود',
      spices: 'توابل',
      textiles: 'منسوجات',
      jemaa_el_fnaa: 'جامع الفنا',
      koutoubia_mosque: 'مسجد الكتبية',
      bahia_palace: 'قصر الباهية'
    };
    return arabicMap[category.toLowerCase()] || 'منتج مغربي';
  };
  
  // Helper function to get emoji for category
  const getEmojiForCategory = (category) => {
    const emojiMap = {
      leather: '👜',
      textiles: '🧣',
      spices: '🌶️',
      crafts: '🏺',
      jewelry: '💍',
      lanterns: '🏮',
      argan: '🍶',
      price_tags: '🏷️',
      jemaa_el_fnaa: '🕌',
      koutoubia_mosque: '🕌',
      bahia_palace: '🏛️'
    };
    return emojiMap[category.toLowerCase()] || '🛍️';
  };

  const reset = () => { setPreview(null); setFileName(''); setOwnerPrice(''); setPhase('idle'); setResult(null); setScanStep(0); };

  const sel = { background:'none',border:'none',fontFamily:C.sans,fontSize:'0.76rem',color:'#888',outline:'none',cursor:'pointer',width:'100%',padding:0,appearance:'none',WebkitAppearance:'none' };

  return (
    <div style={{ fontFamily:C.sans,background:C.cream,color:C.dark,minHeight:'100vh',overflowX:'hidden' }}>
      <FontLink/>

      {/* ══ HEADER ══ */}
      <header style={{ position:'fixed',top:0,left:0,right:0,zIndex:200 }}>
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'12px 16px',background:'rgba(245,240,232,0.97)',backdropFilter:'blur(12px)' }}>
          <div style={{ display:'flex',alignItems:'center',gap:8 }}>
            <a href="/" style={{ background:'white',borderRadius:8,padding:'9px 18px',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',textDecoration:'none' }}>
              <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'0.98rem',letterSpacing:'-0.01em',color:C.dark }}>Souk&amp;Price</span>
            </a>
            <button onClick={()=>setShowMenu(m=>!m)}
              style={{ background:'white',border:'none',borderRadius:8,width:42,height:42,cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:4.5 }}>
              {[0,1,2].map(i=><span key={i} style={{ display:'block',width:17,height:1.5,background:C.dark,borderRadius:2 }}/>)}
            </button>
          </div>
          {/* Breadcrumb */}
          <div style={{ position:'absolute',left:'50%',transform:'translateX(-50%)',display:'flex',alignItems:'center',gap:8 }}>
            <span style={{ fontSize:'0.76rem',color:C.mid }}>Price Detection</span>
            <span style={{ width:4,height:4,borderRadius:'50%',background:C.terra }}/>
            <span style={{ fontSize:'0.76rem',color:C.terra,fontWeight:500 }}>Upload & Detect</span>
          </div>
          <div style={{ display:'flex',gap:8 }}>
            {['Enquiries','Subscribe'].map(label=>(
              <button key={label} onClick={label==='Subscribe'?()=>setShowSubscribe(s=>!s):undefined}
                style={{ background:'white',color:C.dark,border:'none',borderRadius:22,padding:'9px 20px',fontFamily:C.sans,fontSize:'0.82rem',cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',transition:'box-shadow .2s' }}
                onMouseOver={e=>e.currentTarget.style.boxShadow='0 3px 14px rgba(0,0,0,0.13)'}
                onMouseOut={e=>e.currentTarget.style.boxShadow='0 1px 6px rgba(0,0,0,0.07)'}>{label}</button>
            ))}
          </div>
        </div>
        {/* Booking bar */}
        <div style={{ display:'flex',alignItems:'stretch',background:'white',borderRadius:10,margin:'0 16px 12px',boxShadow:'0 2px 14px rgba(0,0,0,0.09)',overflow:'hidden',height:58 }}>
          {[['Category','All Categories',CATEGORIES,1.3],['Souk','All Souks',SOUKS_LIST,1],['Budget','Any Budget',BUDGETS,1]].map(([label,ph,opts,flex])=>(
            <div key={label} style={{ flex,padding:'10px 20px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
              <p style={{ fontSize:'0.73rem',fontWeight:600,color:C.dark,marginBottom:2 }}>{label}</p>
              <select defaultValue={ph} style={sel}>{opts.map(o=><option key={o}>{o}</option>)}</select>
            </div>
          ))}
          <button style={{ background:C.dark,color:'white',border:'none',padding:'0 26px',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',whiteSpace:'nowrap',transition:'background .25s' }}
            onMouseOver={e=>e.currentTarget.style.background=C.terra}
            onMouseOut={e=>e.currentTarget.style.background=C.dark}>Search</button>
        </div>
      </header>

      {showMenu      && <MenuPanel onClose={()=>setShowMenu(false)}/>}
      {showSubscribe && <SubscribeModal onClose={()=>setShowSubscribe(false)}/>}

      {/* ══ PAGE HERO ══ */}
      <div style={{ paddingTop:130,paddingBottom:0,background:`linear-gradient(180deg, ${C.cream} 0%, ${C.warm} 100%)` }}>
        <div style={{ maxWidth:1200,margin:'0 auto',padding:'60px 80px 0' }}>
          <div style={{ display:'flex',alignItems:'flex-end',justifyContent:'space-between',marginBottom:56 }}>
            <div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.1s,transform 0.6s ease 0.1s' }}>
                <p style={{ fontSize:'0.63rem',letterSpacing:'0.2em',textTransform:'uppercase',color:C.terra,marginBottom:14 }}>AI-Powered · 2025/2026 Database</p>
              </div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.2s,transform 0.6s ease 0.2s' }}>
                <h1 style={{ fontFamily:C.serif,fontSize:'clamp(2.8rem,4.5vw,4.4rem)',fontWeight:300,lineHeight:1.05,color:C.dark,marginBottom:16 }}>
                  Price Detection<br/><em style={{ fontStyle:'italic',color:C.terra }}>for the Souk.</em>
                </h1>
              </div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.3s,transform 0.6s ease 0.3s' }}>
                <p style={{ fontSize:'1rem',fontWeight:300,color:C.mid,lineHeight:1.8,maxWidth:480 }}>
                  Photograph any product or price tag in the Marrakech souks. Our AI automatically detects objects and tells you whether the price is fair.
                </p>
              </div>
            </div>
            {/* Stats pills */}
            <div style={{ display:'flex',flexDirection:'column',gap:10,opacity:loaded?1:0,transition:'opacity 0.6s ease 0.4s' }}>
              {[{n:'9',l:'Souks covered'},{n:'15+',l:'Product categories'},{n:'<3s',l:'Detection time'}].map((s,i)=>(
                <div key={i} style={{ background:'white',borderRadius:22,padding:'10px 20px',display:'flex',alignItems:'center',gap:12,boxShadow:'0 2px 12px rgba(0,0,0,0.06)',border:`1px solid ${C.border}` }}>
                  <span style={{ fontFamily:C.serif,fontSize:'1.5rem',fontWeight:300,color:C.terra }}>{s.n}</span>
                  <span style={{ fontSize:'0.72rem',color:C.mid }}>{s.l}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ══ MAIN CONTENT ══ */}
      <div style={{ maxWidth:1200,margin:'0 auto',padding:'0 80px 100px' }}>
        <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:28,alignItems:'start' }}>

          {/* ── LEFT: upload + action ── */}
          <div style={{ position:'sticky',top:130 }}>
            <Reveal>
              <UploadZone
                onFileSelect={(src,name)=>{setPreview(src);setFileName(name);setPhase('idle');setResult(null);}}
                preview={preview}
                fileName={fileName}
                ownerPrice={ownerPrice}
                setOwnerPrice={setOwnerPrice}
                onClear={reset}
              />
            </Reveal>

            {/* Detect button */}
            <Reveal delay={0.15} style={{ marginTop:16 }}>
              <button onClick={runScan} disabled={!preview||phase==='scanning'}
                style={{
                  width:'100%',
                  background: preview&&phase!=='scanning' ? C.dark : '#c8c2ba',
                  color:'white',border:'none',borderRadius:8,
                  padding:'18px 24px',
                  fontFamily:C.sans,fontSize:'0.82rem',letterSpacing:'0.1em',textTransform:'uppercase',
                  cursor:preview&&phase!=='scanning'?'pointer':'not-allowed',
                  transition:'background 0.25s',
                  display:'flex',alignItems:'center',justifyContent:'center',gap:12,
                  boxShadow: preview&&phase!=='scanning'?'0 4px 20px rgba(28,26,23,0.18)':'none',
                }}
                onMouseOver={e=>preview&&phase!=='scanning'&&(e.currentTarget.style.background=C.terra)}
                onMouseOut={e=>e.currentTarget.style.background=preview&&phase!=='scanning'?C.dark:'#c8c2ba'}>
                {phase==='scanning'
                  ? <><span style={{ width:17,height:17,border:'2px solid rgba(255,255,255,0.25)',borderTopColor:'white',borderRadius:'50%',display:'inline-block',animation:'spin 0.8s linear infinite' }}/>Analysing…</>
                  : <><span style={{ fontSize:'1.1rem' }}>🔍</span> Detect Price Now</>
                }
              </button>
            </Reveal>

            {/* How it works mini */}
            {!preview && (
              <Reveal delay={0.3}>
                <div style={{ marginTop:28,background:'white',borderRadius:10,padding:'24px 26px',border:`1px solid ${C.border}` }}>
                  <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:16 }}>How it works</p>
                  {[
                    { icon:'📷', step:'1', text:'Upload a photo of a product or price tag from any souk.' },
                    { icon:'🤖', step:'2', text:'AI detects objects and identifies the product type automatically.' },
                    { icon:'📊', step:'3', text:'Compare instantly against 2025/2026 fair price data.' },
                  ].map((s,i)=>(
                    <div key={i} style={{ display:'flex',alignItems:'flex-start',gap:14,marginBottom:i<2?16:0 }}>
                      <div style={{ width:34,height:34,borderRadius:'50%',background:'rgba(181,69,27,0.07)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'1rem',flexShrink:0 }}>{s.icon}</div>
                      <div>
                        <p style={{ fontSize:'0.7rem',color:C.terra,fontWeight:600,letterSpacing:'0.1em',textTransform:'uppercase',marginBottom:2 }}>Step {s.step}</p>
                        <p style={{ fontSize:'0.82rem',color:C.mid,lineHeight:1.6 }}>{s.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Reveal>
            )}
          </div>

          {/* ── RIGHT: state panels ── */}
          <div>
            {phase === 'idle' && !result && (
              <Reveal delay={0.1}>
                {/* Empty state */}
                <div style={{ background:'white',borderRadius:12,padding:'60px 40px',border:`1px solid ${C.border}`,textAlign:'center',minHeight:420,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center' }}>
                  <div style={{ fontSize:'4rem',marginBottom:22,lineHeight:1 }}>🏷️</div>
                  <p style={{ fontFamily:C.serif,fontSize:'1.8rem',fontWeight:300,color:C.dark,marginBottom:10,lineHeight:1.2 }}>
                    Upload a photo<br/>to get started
                  </p>
                  <p style={{ fontSize:'0.84rem',color:C.mid,lineHeight:1.75,maxWidth:300 }}>
                    Your result will appear here — including the detected price, fair price range, and a negotiation strategy.
                  </p>
                  {/* decorative price tags */}
                  <div style={{ display:'flex',gap:10,marginTop:32,flexWrap:'wrap',justifyContent:'center' }}>
                    {PRICE_DB && PRICE_DB.slice(0,5).map((p,i)=>(
                      <div key={i} style={{ background:C.cream,borderRadius:20,padding:'6px 14px',display:'flex',alignItems:'center',gap:6,border:`1px solid ${C.border}` }}>
                        <span style={{ fontSize:'0.9rem' }}>{p.emoji}</span>
                        <span style={{ fontSize:'0.72rem',color:C.mid }}>{p.fairMin}–{p.fairMax} MAD</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Reveal>
            )}

            {phase === 'scanning' && <ScanningState step={scanStep}/>}

            {phase === 'done' && result && <ResultPanel result={result} onReset={reset} PRICE_DB={PRICE_DB}/>}
          </div>
        </div>

        {/* ══ SCAN HISTORY ══ */}
        <Reveal delay={0.1} style={{ marginTop:80 }}>
          <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:28 }}>
            {/* History */}
            <div style={{ background:'white',borderRadius:12,padding:'32px 32px',border:`1px solid ${C.border}` }}>
              <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:22 }}>
                <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid }}>Recent Detections</p>
                <button style={{ background:'none',border:'none',fontFamily:C.sans,fontSize:'0.72rem',color:C.terra,cursor:'pointer',letterSpacing:'0.06em' }}>View all →</button>
              </div>
              {HISTORY_MOCK.map((item,i)=><HistoryRow key={i} item={item}/>)}
              <p style={{ fontSize:'0.76rem',color:C.mid,textAlign:'center',marginTop:18,paddingTop:18,borderTop:`1px solid ${C.border}` }}>
                Your detections are saved locally on this device.
              </p>
            </div>

            {/* Tips */}
            <div style={{ background:C.dark,borderRadius:12,padding:'32px 32px' }}>
              <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.terraL,marginBottom:22 }}>Souk Negotiation Tips</p>
              {[
                { icon:'🚶',  tip:'Walk away slowly — in 80% of cases, the vendor will call you back with a lower price.' },
                { icon:'😊',  tip:'Stay friendly and light-hearted. Negotiation is a social ritual, not a battle.' },
                { icon:'💰',  tip:'Never show too much interest. The less you seem to want it, the lower the price.' },
                { icon:'🕐',  tip:'Shop in the late afternoon — vendors are more willing to negotiate before closing.' },
                { icon:'📍',  tip:'Walk away from tourist-heavy areas for better prices on identical products.' },
              ].map((t,i)=>(
                <div key={i} style={{ display:'flex',alignItems:'flex-start',gap:14,marginBottom:i<4?18:0,paddingBottom:i<4?18:0,borderBottom:i<4?'1px solid rgba(255,255,255,0.06)':'' }}>
                  <span style={{ fontSize:'1.1rem',flexShrink:0,marginTop:1 }}>{t.icon}</span>
                  <p style={{ fontSize:'0.82rem',color:'#b0a898',lineHeight:1.65 }}>{t.tip}</p>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>

      {/* ══ FOOTER ══ */}
      <footer style={{ background:C.dark,padding:'50px 80px 28px' }}>
        <div style={{ maxWidth:1200,margin:'0 auto',display:'flex',justifyContent:'space-between',alignItems:'center',borderTop:'1px solid rgba(255,255,255,0.07)',paddingTop:20 }}>
          <span style={{ fontFamily:C.serif,fontSize:'1.1rem',color:'white' }}>Souk <span style={{ color:C.terra }}>&</span> Price</span>
          <span style={{ fontSize:'0.69rem',color:'#5c5549' }}>Price data: Morocco Travel Planner 2025/2026</span>
          <span style={{ fontSize:'0.69rem',color:'#5c5549' }}>© 2025 Souk & Price</span>
        </div>
      </footer>

      <style>{`
        *{box-sizing:border-box;margin:0;padding:0;}
        html{scroll-behavior:smooth;}
        select{-webkit-appearance:none;-moz-appearance:none;appearance:none;}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes fadeSlideIn{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
        ::placeholder{color:rgba(28,26,23,0.3)!important;}
        /* Show overlay button on hover */
        .img-overlay:hover .overlay-btn{opacity:1!important;}
      `}</style>
    </div>
  );
}